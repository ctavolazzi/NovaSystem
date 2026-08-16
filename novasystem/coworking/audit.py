"""Scan for loose ends a working session left behind.

Answers one question: what did this session change that it did not finish?

Not a linter and not a test runner. It checks the seams that only show up after
the fact, which is exactly the class of thing an agent is bad at noticing about
its own work: a schema and a document that drifted apart, a hook installed but
not executable, a feed running ahead of the section that displays it, work done
but never written down, code changed but never committed.

Each check is independent and reports ok / warn / fail. A check that raises is
itself a finding rather than a crash, because an audit that dies on its third
check has told you less than one that reports the failure and continues.

``--since`` matters more than it looks. Several agents commonly share one
workspace and one repo. Without a cutoff the report credits this session with
another session's dirty tree, and a real finding gets lost in the noise.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .config import Config, load_config
from .document import Document
from .live_feed import LiveFeed

OK, WARN, FAIL = "ok", "warn", "fail"

# How far the session log may trail the last recorded action before it counts
# as unlogged work. Running the audit is itself recorded activity, so without
# tolerance this check could never pass, and a check that always warns gets
# ignored.
LOG_LAG_TOLERANCE_MIN = 15

# Runtime droppings, not authored work. Flagging these buries real findings.
REF_NOISE = re.compile(
    r'(\.db(-shm|-wal)?$|\.sqlite\d*$|\.log$|\.jsonl$|\.pyc$'
    r'|(^|/)\.[^/]+/|__pycache__/)'
)


class Auditor:
    """Runs the checks. Instantiate, call ``run()``."""

    def __init__(self, config: Optional[Config] = None,
                 since: Optional[datetime] = None,
                 repos: Optional[Sequence[Path]] = None):
        self.config = config or load_config()
        self.since = since
        self.repos = [Path(r) for r in repos] if repos else [Path.cwd()]
        self.doc = Document(config=self.config)
        self.feed = LiveFeed(config=self.config)

    # ── Runner ─────────────────────────────────────────────────────────

    def checks(self) -> List[Tuple[str, Callable]]:
        return [
            ("Workspace is configured and writable", self._check_workspace),
            ("Today's log matches the section schema", self._check_layout),
            ("Other logs are on the current layout", self._check_other_logs),
            ("Today's log renders correctly", self._check_structure),
            ("Every schema section is present", self._check_sections_present),
            ("Live Feed hook is installed and runnable", self._check_hook),
            ("Live Feed is current and error-free", self._check_feed),
            ("Session log reflects the work done", self._check_session_log),
            ("Changed files are referenced in the log", self._check_refs),
            ("Session work is committed", self._check_uncommitted),
        ]

    def run(self) -> List[Dict]:
        results = []
        for title, fn in self.checks():
            try:
                status, details = fn()
            except Exception as e:          # a broken check is a finding
                status, details = FAIL, [f"check raised {type(e).__name__}: {e}"]
            results.append({"check": title, "status": status,
                            "details": list(details)})
        return results

    # ── Helpers ────────────────────────────────────────────────────────

    def _touched_since(self, path: Path) -> bool:
        if self.since is None:
            return True
        try:
            return datetime.fromtimestamp(Path(path).stat().st_mtime) >= self.since
        except OSError:
            return True

    @staticmethod
    def _sh(args: Sequence[str], cwd: Optional[str] = None):
        try:
            out = subprocess.run(list(args), cwd=cwd, capture_output=True,
                                 text=True, timeout=30)
            return out.returncode, out.stdout.strip(), out.stderr.strip()
        except (OSError, subprocess.TimeoutExpired) as e:
            return 1, "", str(e)

    @staticmethod
    def _entry_path(top: str, entry: str) -> Tuple[Path, str]:
        name = entry[3:].strip().strip('"').split(" -> ")[-1]
        return Path(top) / name, name

    def _changed_repos(self) -> List[Tuple[str, List[str]]]:
        seen, found = set(), []
        for start in self.repos:
            rc, top, _ = self._sh(["git", "rev-parse", "--show-toplevel"],
                                  cwd=str(start))
            if rc != 0 or not top or top in seen:
                continue
            seen.add(top)
            rc, out, _ = self._sh(["git", "status", "--porcelain"], cwd=top)
            if rc != 0:
                continue
            lines = [l for l in out.splitlines() if l.strip()]
            lines = [l for l in lines
                     if self._touched_since(self._entry_path(top, l)[0])]
            found.append((top, lines))
        return found

    @staticmethod
    def _minutes_between(earlier: str, later: str) -> int:
        try:
            a = datetime.strptime(earlier[:5], "%H:%M")
            b = datetime.strptime(later[:5], "%H:%M")
        except (ValueError, TypeError):
            return 0
        return max(0, int((b - a).total_seconds() // 60))

    # ── Checks ─────────────────────────────────────────────────────────

    def _check_workspace(self):
        problems = []
        root = self.config.root
        if not root.exists():
            return WARN, [f"workspace root does not exist yet: {root}",
                          "run: novasystem coworking init"]
        if not os.access(root, os.W_OK):
            problems.append(f"workspace root is not writable: {root}")
        if not self.config.log_dir.is_dir():
            problems.append(f"log directory missing: {self.config.log_dir}")
        if problems:
            return FAIL, problems
        return OK, [f"{root} (resolved by {self.config.source})"]

    def _check_layout(self):
        from . import migrate as migrate_mod
        if not self.doc.exists():
            return WARN, [f"no work log for today at {self.doc.path}",
                          "run: novasystem coworking init"]
        result = migrate_mod.migrate_document(write=False, config=self.config)
        status = result.get("status")
        if status == "unchanged":
            return OK, [f"{result.get('sections')} sections, in schema order"]
        if status == "refused":
            return FAIL, ["migration refuses to run: "
                          + str(result.get("reason"))]
        if status == "skipped":
            return WARN, [str(result.get("reason"))]
        return WARN, ["log is not on the current layout. Run: "
                      "novasystem coworking migrate --write"]

    def _check_other_logs(self):
        from . import migrate as migrate_mod
        results = migrate_mod.migrate_all(write=False, config=self.config)
        today = self.doc.date
        stale, refused = [], []
        for r in results:
            date = Path(r.get("path", "")).stem
            if date == today:
                continue
            if r.get("status") == "refused":
                refused.append(date)
            elif str(r.get("status", "")).startswith("would-"):
                stale.append(date)
        if refused:
            return FAIL, [f"{len(refused)} log(s) the migration refuses to "
                          f"touch: {', '.join(refused[:5])}"]
        if stale:
            return WARN, [f"{len(stale)} of {len(results)} logs still on an "
                          f"older layout",
                          "align them with: novasystem coworking migrate --all --write",
                          "most recent: " + ", ".join(stale[-5:])]
        return OK, [f"all {len(results)} logs on the current layout"]

    def _check_structure(self):
        if not self.doc.exists():
            return WARN, ["no work log for today"]
        text = self.doc.read()
        lines = text.splitlines()
        problems = []

        swallowed = [(i + 1, lines[i]) for i in range(1, len(lines))
                     if lines[i].startswith("## ")
                     and lines[i - 1].lstrip().startswith(">")]
        if swallowed:
            problems.append(
                f"{len(swallowed)} heading(s) absorbed into a callout: "
                + ", ".join(f"L{n} {h}" for n, h in swallowed[:4]))

        nested = [i for i, (a, b) in enumerate(zip(lines, lines[1:]), 2)
                  if b.startswith("**[") and a.lstrip().startswith(">")]
        if nested:
            problems.append(f"{len(nested)} log entry nesting violation(s) at "
                            f"line(s) {nested[:4]}")

        doubled = text.count("---\n\n---")
        if doubled:
            problems.append(f"{doubled} doubled separator rule(s)")

        headers = re.findall(r'^## .+$', text, re.MULTILINE)
        dupes = sorted({h for h in headers if headers.count(h) > 1})
        if dupes:
            problems.append("duplicate section header(s): " + ", ".join(dupes))

        return (FAIL, problems) if problems else (OK, ["structure clean"])

    def _check_sections_present(self):
        if not self.doc.exists():
            return WARN, ["no work log for today"]
        status = self.doc.status()
        absent = [name for name, state in status.items() if state == "absent"]
        if absent:
            return WARN, ["sections in the schema but not the log: "
                          + ", ".join(absent),
                          "add them with: novasystem coworking migrate --write"]
        return OK, [f"all {len(status)} schema sections present"]

    def _check_hook(self):
        from .install import hook_target_path, settings_path
        problems = []
        hook = hook_target_path()
        if not hook.is_file():
            return WARN, [f"hook not installed at {hook}",
                          "install it with: novasystem coworking install-hook"]
        if not os.access(hook, os.X_OK):
            problems.append(f"hook is not executable: chmod +x {hook}")
        if not shutil.which("jq"):
            problems.append("jq is not on PATH, so the record path silently "
                            "no-ops without it")
        rc, _, err = self._sh(["bash", "-n", str(hook)])
        if rc != 0:
            problems.append(f"hook has a syntax error: {err}")

        settings = settings_path()
        if not settings.is_file():
            problems.append(f"agent settings file not found: {settings}")
        else:
            try:
                cfg = json.loads(settings.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                return FAIL, [f"{settings} is not valid JSON: {e}"]
            hooks_blob = json.dumps(cfg.get("hooks", {}))
            if hook.name not in hooks_blob:
                problems.append(f"{hook.name} is not wired into {settings}")
            elif not cfg.get("hooks", {}).get("Stop"):
                problems.append("no Stop hook configured, so the final render "
                                "of each turn can be lost")

        return (WARN, problems) if problems else (OK, ["installed, wired, jq present"])

    def _check_feed(self):
        problems = []
        events = self.feed.read_events()
        if not events:
            return WARN, ["no activity recorded today, so the hook may not be "
                          "firing"]

        last_event = str(events[-1].get("ts", ""))
        rendered = self.doc.read_section("live_feed") if self.doc.exists() else ""
        match = re.search(r'updated (\d{2}:\d{2})', rendered)
        if not match:
            problems.append("Live Feed section has no rendered timestamp")
        elif last_event[:5] > match.group(1):
            problems.append(
                f"section is behind the feed (rendered {match.group(1)}, last "
                f"event {last_event}). Run: novasystem coworking render")

        if self.feed.lock_path.is_dir():
            problems.append(f"stale render lock: {self.feed.lock_path}")

        counts: Dict[str, int] = {}
        for e in events:
            key = e.get("sid") or "untagged"
            counts[key] = counts.get(key, 0) + 1
        summary = [f"{len(events)} events from {len(counts)} session(s): "
                   + ", ".join(f"{k}={v}" for k, v in counts.items())]
        return (WARN, problems + summary) if problems else (OK, summary)

    def _check_session_log(self):
        if not self.doc.exists():
            return WARN, ["no work log for today"]
        body = self.doc.read_section("session_log")
        stamps = re.findall(r'\[!note\]-\s*(\d{2}:\d{2})', body)
        events = self.feed.read_events()
        last_activity = str(events[-1].get("ts", ""))[:5] if events else ""

        if not stamps:
            return WARN, ["session log has no entries today",
                          "close the session with append_session_log()"]
        lag = self._minutes_between(max(stamps), last_activity)
        if lag > LOG_LAG_TOLERANCE_MIN:
            return WARN, [f"last entry is {max(stamps)} but activity continued "
                          f"to {last_activity} ({lag} min), so the work since "
                          f"then is unlogged"]
        return OK, [f"{len(stamps)} entries, latest {max(stamps)}"]

    def _check_refs(self):
        if not self.doc.exists():
            return WARN, ["no work log for today"]
        text = self.doc.read()
        unreferenced = []
        for top, lines in self._changed_repos():
            for entry in lines:
                _, name = self._entry_path(top, entry)
                if REF_NOISE.search(name):
                    continue
                base = Path(name).name
                if base and base not in text:
                    unreferenced.append(f"{Path(top).name}/{name}")
        if unreferenced:
            return WARN, ["changed files the log never mentions:"] + \
                         [f"    {u}" for u in unreferenced[:12]]
        return OK, ["all changed files referenced"]

    def _check_uncommitted(self):
        repos = self._changed_repos()
        if not repos:
            return WARN, ["no git repository found for the audited paths"]
        dirty = [(top, lines) for top, lines in repos if lines]
        scope = f" since {self.since.strftime('%H:%M')}" if self.since else ""
        if not dirty:
            return OK, [f"working trees clean{scope}"]
        details = []
        if self.since:
            details.append(f"(only files modified{scope} are counted)")
        for top, lines in dirty:
            details.append(f"{Path(top).name}: {len(lines)} uncommitted change(s)")
            details += [f"    {l}" for l in lines[:10]]
            if len(lines) > 10:
                details.append(f"    … {len(lines) - 10} more")
        return WARN, details


# ── Public API ─────────────────────────────────────────────────────────

def run_audit(config: Optional[Config] = None,
              since: Optional[str] = None,
              repos: Optional[Sequence[Path]] = None) -> List[Dict]:
    """Run every check. ``since`` is ``HH:MM`` local time, today."""
    cutoff = None
    if since:
        try:
            hh, mm = (int(x) for x in str(since).split(":"))
            cutoff = datetime.now().replace(hour=hh, minute=mm, second=0,
                                            microsecond=0)
        except ValueError:
            raise ValueError(f"bad --since value {since!r}, expected HH:MM")
    return Auditor(config=config, since=cutoff, repos=repos).run()


def format_report(results: Sequence[Dict]) -> str:
    """Render results the way the CLI prints them."""
    icons = {OK: "  ok  ", WARN: " WARN ", FAIL: " FAIL "}
    out = [f"Coworking audit · {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    for r in results:
        out.append(f"[{icons[r['status']]}] {r['check']}")
        out += [f"           {d}" for d in r["details"]]
    counts = {s: sum(1 for r in results if r["status"] == s)
              for s in (OK, WARN, FAIL)}
    out += ["", f"{counts[OK]} ok · {counts[WARN]} warn · {counts[FAIL]} fail"]
    return "\n".join(out)
