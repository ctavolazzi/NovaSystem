"""Real-time activity feed: the section that makes a work log watchable.

A session log written at the end of a session is a summary you have to trust.
The Live Feed is the other thing: a section rebuilt on every tool call, so the
document changes while you look at it. Put it on a second monitor, work, and
you can see what the agent is doing without reading a transcript.

Split in two halves, deliberately, for speed:

**Record.** A shell hook appends one JSON line per tool call. Pure shell plus
``jq``, no Python startup, so it costs milliseconds and never delays the tool
call that triggered it. Importing this module costs roughly half a second;
paying that on every ``Read`` would be felt.

**Render.** This module reads the log, formats it, and rebuilds the whole
section with a replace. Full rebuild rather than append means double fires,
races, and hand edits all converge on the same correct content, and there is no
callout-nesting hazard.

Feed file: ``<feed_dir>/YYYY-MM/YYYY-MM-DD.jsonl``. One object per line::

    {"ts": "09:52:03", "kind": "Edit", "sid": "a3f9", "detail": "<raw input>"}

The hook captures raw values only. Every formatting decision lives here, so
changing how a row looks never means touching shell.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from . import atomic
from .config import Config, load_config
from .document import Document

# Rows shown in the document. Beyond this the window stops being glanceable,
# which is the entire feature.
MAX_ROWS = 14
DETAIL_CHARS = 68

# Tools whose runs are pure reconnaissance. They still appear, but consecutive
# runs collapse into one counted row: twelve consecutive reads are one act of
# research, not twelve events worth of screen space.
QUIET_KINDS = frozenset({"Read", "Grep", "Glob", "NotebookRead", "TodoWrite",
                         "List", "Search"})

ICONS = {
    "Bash": "▶", "Shell": "▶", "Run": "▶",
    "Edit": "✎", "MultiEdit": "✎", "NotebookEdit": "✎", "Update": "✎",
    "Write": "✚", "Create": "✚",
    "Read": "·", "Grep": "·", "Glob": "·", "Search": "·", "List": "·",
    "TodoWrite": "☑",
    "Task": "⚙", "Agent": "⚙",
    "WebFetch": "⇣", "WebSearch": "⌕",
    "note": "◆",
}

# Keys a hook payload might carry the interesting value under, best first.
DETAIL_KEYS = ("command", "file_path", "notebook_path", "pattern",
               "description", "query", "url", "prompt", "path")


class LiveFeed:
    """The activity feed for one day."""

    def __init__(self, date: Optional[str] = None,
                 config: Optional[Config] = None):
        self.config = config or load_config()
        self.date = date or datetime.now().strftime(self.config.date_format)

    # ── Paths ──────────────────────────────────────────────────────────

    @property
    def path(self) -> Path:
        return self.config.feed_path(self.date)

    @property
    def state_path(self) -> Path:
        return self.config.state_path(self.date)

    @property
    def lock_path(self) -> Path:
        return self.path.parent / ".render.lock"

    # ── Recording ──────────────────────────────────────────────────────

    def append(self, kind: str, detail: str = "", sid: str = "") -> None:
        """Append one event.

        Never raises. A dropped feed row is a cosmetic loss; an exception here
        would propagate into whatever tool call triggered it, which is not a
        trade an observability layer gets to make.
        """
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            row = {
                "ts": datetime.now().strftime("%H:%M:%S"),
                "kind": kind,
                "sid": sid,
                "detail": detail,
            }
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def record_payload(self, payload: Dict) -> Optional[Dict]:
        """Extract and append one event from an agent hook payload.

        Tolerant of shape: harnesses disagree about whether the tool name is
        ``tool_name`` or ``tool``, and about where the arguments live.
        """
        if not isinstance(payload, dict):
            return None
        kind = payload.get("tool_name") or payload.get("tool") or "?"
        sid = str(payload.get("session_id") or payload.get("session") or "")[:4]
        args = payload.get("tool_input") or payload.get("input") or {}
        detail = ""
        if isinstance(args, dict):
            for key in DETAIL_KEYS:
                if args.get(key):
                    detail = str(args[key])
                    break
        self.append(str(kind), detail, sid=sid)
        return {"kind": kind, "detail": detail, "sid": sid}

    def read_events(self) -> List[Dict]:
        """Read the feed. Malformed lines are skipped, never fatal."""
        if not self.path.is_file():
            return []
        events = []
        for line in self.path.read_text(encoding="utf-8",
                                        errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("kind"):
                events.append(row)
        return events

    # ── Focus headline ─────────────────────────────────────────────────

    def set_focus(self, text: str) -> None:
        """Set the ``Now:`` headline shown at the top of the feed.

        Tool calls say what happened; they do not say what it was for. This is
        where the agent states intent, and it is the line a viewer actually
        reads.
        """
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps({
                "focus": _oneline(text),
                "set_at": datetime.now().strftime("%H:%M"),
            }, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass

    def get_focus(self) -> Dict:
        if not self.state_path.is_file():
            return {}
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    # ── Rendering ──────────────────────────────────────────────────────

    def render_markdown(self) -> str:
        """Build the Live Feed section body."""
        events = self.read_events()
        focus = self.get_focus()
        now = datetime.now().strftime("%H:%M")

        if not events and not focus:
            return ("> [!abstract]+ Live Feed\n"
                    "> Idle. Rebuilt on every agent tool call.\n")

        rows = collapse(events)
        shown = rows[::-1][:MAX_ROWS]            # newest first
        hidden = len(rows) - len(shown)

        plural = "action" if len(events) == 1 else "actions"
        all_sessions = {e.get("sid") for e in events if e.get("sid")}
        tabs = f" · {len(all_sessions)} sessions" if len(all_sessions) > 1 else ""
        lines = [f"> [!abstract]+ Live Feed · {len(events)} {plural}{tabs} "
                 f"· updated {now}"]

        if focus.get("focus"):
            since = focus.get("set_at", "")
            lines.append(f"> **Now:** {focus['focus']}"
                         + (f" *(since {since})*" if since else ""))
            lines.append(">")

        # Tag rows by session only when more than one is in the window: several
        # agent sessions share one feed, but the common single-session view
        # should stay clean.
        tag_rows = len({r["sid"] for r in shown if r.get("sid")}) > 1

        for row in shown:
            icon = ICONS.get(row["kind"], "•")
            detail = format_detail(row["kind"], row["detail"])
            count = f" ×{row['count']}" if row["count"] > 1 else ""
            body = f" `{detail}`" if detail else ""
            tag = f" ⟨{row['sid']}⟩" if tag_rows and row.get("sid") else ""
            lines.append(f"> `{row['ts']}`{tag} {icon} "
                         f"**{row['kind']}{count}**{body}")

        if hidden > 0:
            older = "row" if hidden == 1 else "rows"
            lines.append(">")
            lines.append(f"> *{hidden} earlier {older} trimmed. "
                         f"Full history in the feed log.*")

        return "\n".join(lines) + "\n"

    def render(self, dry_run: bool = False) -> Dict:
        """Rebuild the Live Feed section of today's document."""
        doc = Document(self.date, self.config)
        if not doc.exists():
            return {"status": "skipped", "reason": "no work log for this date"}

        markdown = self.render_markdown()
        if dry_run:
            return {"status": "dry-run", "markdown": markdown}

        if not self._ensure_section(doc):
            return {"status": "skipped",
                    "reason": "could not place the Live Feed section"}

        doc.write_section("live_feed", markdown, actor="hook", mode="replace")
        return {"status": "written", "events": len(self.read_events())}

    def _ensure_section(self, doc: Document) -> bool:
        """Guarantee the section exists, in the right place.

        ``write_section`` self-heals a missing header by appending at the END
        of the document, which is the one position that defeats this section's
        entire purpose. So place it explicitly, at the top of the work block.
        """
        header = self.config.section("live_feed").header
        text = doc.read()
        if re.search(rf'^{re.escape(header)}\s*$', text, re.MULTILINE):
            return True

        from .config import HEADER_END_MARKER
        block = (f"{header}\n\n> [!abstract]+ Live Feed\n"
                 f"> Starting up.\n\n---\n\n")

        if HEADER_END_MARKER in text:
            new_text = text.replace(HEADER_END_MARKER,
                                    f"{HEADER_END_MARKER}\n\n---\n\n{block}", 1)
        else:
            anchors = [s.header for s in self.config.sections
                       if s.name != "live_feed"]
            for anchor in anchors:
                if re.search(rf'^{re.escape(anchor)}\s*$', text, re.MULTILINE):
                    new_text = re.sub(rf'^{re.escape(anchor)}$',
                                      f"{block}{anchor}", text, count=1,
                                      flags=re.MULTILINE)
                    break
            else:
                return False

        atomic.write(doc.path, new_text, root=self.config.lock_root())
        return True

    def clear_stale_lock(self, max_age_s: float = 60.0) -> bool:
        """Remove a render lock left behind by a process that died.

        Without this, one crash stops the feed for the rest of the day and the
        document silently goes stale while looking fine.
        """
        lock = self.lock_path
        if not lock.is_dir():
            return False
        try:
            import time
            if time.time() - lock.stat().st_mtime > max_age_s:
                lock.rmdir()
                return True
        except OSError:
            pass
        return False


# ── Formatting helpers ─────────────────────────────────────────────────

def _oneline(value) -> str:
    return " ".join(str(value).split())


def shorten_path(raw: str) -> str:
    """Last two path components: enough to identify a file without burning the
    row on a home-directory prefix."""
    parts = [p for p in Path(raw).parts if p not in ("/", "")]
    if len(parts) > 1:
        return "/".join(parts[-2:])
    return parts[-1] if parts else raw


def format_detail(kind: str, detail: str) -> str:
    """Turn a raw tool input into one scannable row fragment."""
    detail = _oneline(detail)
    if not detail:
        return ""

    if kind in ("Edit", "Write", "MultiEdit", "NotebookEdit", "Read", "Create"):
        detail = shorten_path(detail)
    elif kind in ("Bash", "Shell", "Run"):
        # A leading `cd <path> &&` is preamble, not the action.
        detail = re.sub(r'^cd\s+\S+\s*&&\s*', '', detail)

    if len(detail) > DETAIL_CHARS:
        detail = detail[:DETAIL_CHARS - 1].rstrip() + "…"

    # Rows are wrapped in backticks; an inner backtick would close the span.
    return detail.replace("`", "'")


def collapse(events: List[Dict]) -> List[Dict]:
    """Collapse consecutive runs of the same quiet tool into one counted row.

    Loud tools (Bash, Edit, Write) never collapse: those are the ones worth
    watching individually. Runs from different sessions never merge either,
    because two agents reading in parallel is not one act of research.
    """
    rows: List[Dict] = []
    for event in events:
        kind = event.get("kind", "?")
        sid = event.get("sid", "")
        prev = rows[-1] if rows else None
        if (prev and kind in QUIET_KINDS
                and prev["kind"] == kind and prev["sid"] == sid):
            prev["count"] += 1
            prev["ts"] = event.get("ts", prev["ts"])
            prev["detail"] = event.get("detail", "")
        else:
            rows.append({
                "ts": event.get("ts", ""),
                "kind": kind,
                "sid": sid,
                "detail": event.get("detail", ""),
                "count": 1,
            })
    return rows
