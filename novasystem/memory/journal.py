"""
novasystem.memory.journal: write NovaSystem's work into a queryable memory.

NovaSystem already records what it does: the coworking Live Feed is an event
stream, the persona Ledger is a hash-chained decision log. Both are excellent at
*keeping* things and bad at being *asked* things. This module mirrors them into
a PocketBase collection (``agent_journal``) that answers questions.

The integration is deliberately loose:

* **No import coupling.** SimpleAgentOS owns the PocketBase instance and the
  ``agent_journal`` schema. NovaSystem never imports it. This module speaks
  plain HTTP to the same collection. Either project runs fine without the other.
* **Opt-in.** Nothing mirrors unless ``NOVA_JOURNAL=1`` is set (or
  ``enable()`` is called). Off by default, so no existing behavior changes.
* **Never fatal.** Every entry point swallows its own errors. A memory layer
  that can break a decision record is worse than no memory layer.
* **Stdlib only, Python 3.8+.** Same constraints as the rest of the package.

Usage
-----
    export NOVA_JOURNAL=1
    novasystem journal status
    novasystem journal log "picked SQLite over Postgres for the ledger" \\
        --kind decision --tags ledger,storage
    novasystem journal query "ledger" --since 7d

    from novasystem.memory import journal
    journal.remember("shipped the coworking layer", kind="event")
    for row in journal.recall("ledger", kind="decision"):
        print(row["occurred_at"], row["title"])

Pointing at a different PocketBase: set ``NOVA_JOURNAL_BASE``
(default ``http://127.0.0.1:8090``).
"""

from __future__ import annotations

import hashlib
import json
import os
import socket
import threading
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

__all__ = [
    "enabled", "enable", "disable", "remember", "recall", "recent",
    "status", "spool_path", "sync",
]

# ── Config ────────────────────────────────────────────────────────────

BASE = os.environ.get("NOVA_JOURNAL_BASE", "http://127.0.0.1:8090").rstrip("/")
COLLECTION = os.environ.get("NOVA_JOURNAL_COLLECTION", "agent_journal")
PROJECT = os.environ.get("NOVA_JOURNAL_PROJECT", "NovaSystem")
TIMEOUT = float(os.environ.get("NOVA_JOURNAL_TIMEOUT", "1.5"))

# Where entries wait when PocketBase is down. Under the coworking workspace if
# one is configured, else alongside the package's own state.
SPOOL = Path(os.environ.get(
    "NOVA_JOURNAL_SPOOL",
    Path.home() / ".novasystem" / "journal_spool.jsonl",
))

# The spool is an outbox, not an archive. Left uncapped it grows for as long as
# PocketBase is down, which is the one situation where nobody is watching it.
# Oldest entries go first, and the count of what was dropped is kept so the gap
# is visible in `novasystem journal status` instead of being silent.
SPOOL_MAX_BYTES = int(os.environ.get("NOVA_JOURNAL_SPOOL_MAX_BYTES", 8 * 1024 * 1024))
SPOOL_MAX_ENTRIES = int(os.environ.get("NOVA_JOURNAL_SPOOL_MAX_ENTRIES", "5000"))
SPOOL_MAX_AGE_DAYS = float(os.environ.get("NOVA_JOURNAL_SPOOL_MAX_AGE_DAYS", "30"))

# Live Feed rows are high-volume tool calls. Mirroring every Read into a memory
# you later search would bury the things worth recalling, so only these kinds
# cross over by default. Override with NOVA_JOURNAL_FEED_KINDS=* for everything.
_DEFAULT_FEED_KINDS = {"Write", "Edit", "NotebookEdit", "note", "focus"}

_lock = threading.Lock()
_forced: Optional[bool] = None
_online: Optional[bool] = None


def enabled() -> bool:
    """Is mirroring on? Env var by default, overridable in-process."""
    if _forced is not None:
        return _forced
    return os.environ.get("NOVA_JOURNAL", "0").lower() not in ("0", "", "false", "no")


def enable() -> None:
    global _forced
    _forced = True


def disable() -> None:
    global _forced
    _forced = False


def spool_path() -> Path:
    return SPOOL


# ── Wire format ───────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pb_datetime(iso: str) -> str:
    """PocketBase wants 'YYYY-MM-DD HH:MM:SS.mmmZ', not RFC3339 with an offset."""
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return iso
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S.") + "%03dZ" % (dt.microsecond // 1000)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _norm_tags(tags: Any) -> List[str]:
    if not tags:
        return []
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    return [str(t).strip() for t in tags if str(t).strip()]


def _quote(value: str) -> str:
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _build(body: str, kind: str, title: str = "", tags: Any = None,
           actor: str = "", source: str = "", session_id: str = "",
           path_ref: str = "", importance: float = 0.5,
           metadata: Optional[Dict] = None,
           occurred_at: Optional[str] = None) -> Dict:
    occurred_at = occurred_at or _now_iso()
    body = body or ""
    if not title:
        first = body.strip().splitlines()[0] if body.strip() else ""
        title = (first[:120] + "…") if len(first) > 120 else first
    return {
        "entry_id": _hash("%s|%s|%s" % (occurred_at, body, uuid.uuid4())),
        "content_hash": _hash("%s|%s" % (kind, body)),
        "occurred_at": occurred_at,
        "kind": kind,
        "actor": actor or os.environ.get("NOVA_JOURNAL_ACTOR", "novasystem"),
        "source": source or "novasystem",
        "project": PROJECT,
        "session_id": session_id,
        "title": title,
        "body": body,
        "tags": _norm_tags(tags),
        "path_ref": path_ref,
        "importance": float(importance),
        "metadata": metadata or {},
    }


def _to_record(entry: Dict) -> Dict:
    rec = dict(entry)
    rec["occurred_at"] = _pb_datetime(entry.get("occurred_at", ""))
    rec["tags"] = _norm_tags(entry.get("tags"))
    rec["metadata"] = entry.get("metadata") or {}
    return rec


# ── HTTP ──────────────────────────────────────────────────────────────

def _is_online(recheck: bool = False) -> bool:
    global _online
    if _online is not None and not recheck:
        return _online
    try:
        req = urllib.request.Request(BASE + "/api/health")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            _online = resp.status == 200
    except Exception:
        _online = False
    return _online


def _post(path: str, payload: Dict) -> Optional[Dict]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _get(path: str) -> Optional[Dict]:
    req = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ── Spool ─────────────────────────────────────────────────────────────

def _spool_append(entry: Dict) -> None:
    oversize = False
    try:
        with _lock:
            SPOOL.parent.mkdir(parents=True, exist_ok=True)
            with SPOOL.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            oversize = SPOOL.stat().st_size > SPOOL_MAX_BYTES
    except OSError:
        return  # out of disk / read-only home: still not worth an exception
    # A stat() per append is cheap; re-reading the whole spool per append is not.
    if oversize:
        _spool_trim()


def _dropped_path() -> Path:
    """Derived from SPOOL at call time so it follows a redirected spool."""
    return SPOOL.with_suffix(".dropped")


def spool_dropped() -> int:
    """How many entries the cap discarded. Loss should be countable."""
    try:
        return int(_dropped_path().read_text().strip() or 0)
    except (OSError, ValueError):
        return 0


def _record_dropped(n: int) -> None:
    if n <= 0:
        return
    try:
        _dropped_path().write_text(str(spool_dropped() + n))
    except OSError:
        pass  # a full disk is exactly when this fires; do not make it fatal


def _spool_trim() -> int:
    """Bring the spool back under its caps. Returns how many were dropped."""
    entries = _spool_read()
    if not entries:
        return 0

    kept = entries
    if SPOOL_MAX_AGE_DAYS > 0:
        cutoff = (datetime.now(timezone.utc)
                  - timedelta(days=SPOOL_MAX_AGE_DAYS)).isoformat()
        kept = [e for e in kept if str(e.get("occurred_at") or "") >= cutoff]
    if SPOOL_MAX_ENTRIES > 0 and len(kept) > SPOOL_MAX_ENTRIES:
        kept = kept[-SPOOL_MAX_ENTRIES:]

    dropped = len(entries) - len(kept)
    if dropped:
        _spool_rewrite(kept)
        _record_dropped(dropped)
    return dropped


def _spool_read() -> List[Dict]:
    if not SPOOL.is_file():
        return []
    out = []
    try:
        with SPOOL.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        return []
    return out


def _spool_rewrite(entries: List[Dict]) -> None:
    try:
        with _lock:
            SPOOL.parent.mkdir(parents=True, exist_ok=True)
            tmp = SPOOL.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as fh:
                for entry in entries:
                    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
            tmp.replace(SPOOL)
    except OSError:
        pass


def sync() -> Dict:
    """Push spooled entries to PocketBase. Returns what happened."""
    pending = _spool_read()
    if not pending:
        return {"pending": 0, "synced": 0, "remaining": 0, "online": _is_online(True)}
    if not _is_online(recheck=True):
        return {"pending": len(pending), "synced": 0,
                "remaining": len(pending), "online": False}

    remaining, synced = [], 0
    for entry in pending:
        try:
            _post("/api/collections/%s/records" % COLLECTION, _to_record(entry))
            synced += 1
        except urllib.error.HTTPError as exc:
            # A unique-index collision means it's already remembered.
            if exc.code == 400:
                synced += 1
            else:
                remaining.append(entry)
        except Exception:
            remaining.append(entry)
    _spool_rewrite(remaining)
    return {"pending": len(pending), "synced": synced,
            "remaining": len(remaining), "online": True}


# ── Write ─────────────────────────────────────────────────────────────

def remember(body: str, kind: str = "note", force: bool = False, **kwargs) -> Optional[Dict]:
    """Write one thing into NovaSystem's memory.

    Returns the entry (with ``_stored`` set to "pocketbase" or "spool"), or None
    if journaling is off. Never raises. `force=True` bypasses the enable check
    for explicit CLI/API calls, which should work whether or not mirroring is on.
    """
    if not (force or enabled()):
        return None
    try:
        entry = _build(body, kind, **kwargs)
    except Exception:
        return None
    try:
        if _is_online():
            try:
                _post("/api/collections/%s/records" % COLLECTION, _to_record(entry))
                entry["_stored"] = "pocketbase"
                return entry
            except urllib.error.HTTPError as exc:
                if exc.code == 400 and b"entry_id" in exc.read():
                    entry["_stored"] = "pocketbase"
                    return entry
            except (urllib.error.URLError, socket.timeout, OSError):
                global _online
                _online = False
    except Exception:
        pass
    _spool_append(entry)
    entry["_stored"] = "spool"
    return entry


# ── Read ──────────────────────────────────────────────────────────────

def _matches(row: Dict, text: str, kind: str, tags: Sequence[str],
             since: str, until: str) -> bool:
    if kind and row.get("kind") != kind:
        return False
    occurred = str(row.get("occurred_at") or "")
    if since and occurred < since:
        return False
    if until and occurred > until:
        return False
    if tags:
        have = set(t.lower() for t in _norm_tags(row.get("tags")))
        if not have.issuperset(set(t.lower() for t in tags)):
            return False
    if text:
        hay = ("%s %s" % (row.get("title") or "", row.get("body") or "")).lower()
        if text.lower() not in hay:
            return False
    return True


def recall(text: str = "", kind: str = "", tags: Any = None, since: str = "",
           until: str = "", limit: int = 50, project: Optional[str] = PROJECT,
           include_spool: bool = True) -> List[Dict]:
    """Ask the memory a question.

    ``project=None`` searches across every project sharing the collection.
    That's how NovaSystem sees what SimpleAgentOS learned, and vice versa.
    """
    tags = _norm_tags(tags)
    since_pb = _pb_datetime(_resolve_since(since)) if since else ""
    until_pb = _pb_datetime(until) if until else ""

    rows: List[Dict] = []
    if _is_online():
        clauses = []
        if kind:
            clauses.append("kind=%s" % _quote(kind))
        if project:
            clauses.append("project=%s" % _quote(project))
        if since_pb:
            clauses.append("occurred_at>=%s" % _quote(since_pb))
        if until_pb:
            clauses.append("occurred_at<=%s" % _quote(until_pb))
        if text:
            clauses.append("(title~%s || body~%s)" % (_quote(text), _quote(text)))
        for tag in tags:
            clauses.append("tags~%s" % _quote(tag))
        params = ["perPage=%d" % max(1, min(limit, 500)),
                  "sort=" + urllib.parse.quote("-occurred_at")]
        if clauses:
            params.append("filter=" + urllib.parse.quote(" && ".join(clauses)))
        try:
            out = _get("/api/collections/%s/records?%s" % (COLLECTION, "&".join(params)))
            rows = out.get("items", []) if out else []
            for row in rows:
                row["_source"] = "pocketbase"
        except Exception:
            rows = []

    if include_spool:
        seen = set(r.get("entry_id") for r in rows)
        for entry in _spool_read():
            if entry.get("entry_id") in seen:
                continue
            if project and entry.get("project") != project:
                continue
            if _matches(entry, text, kind, tags, since_pb or since, until_pb or until):
                entry = dict(entry)
                entry["_source"] = "spool"
                rows.append(entry)

    rows.sort(key=lambda r: str(r.get("occurred_at") or ""), reverse=True)
    return rows[:limit]


def recent(limit: int = 20, **kwargs) -> List[Dict]:
    return recall(limit=limit, **kwargs)


def _resolve_since(value: str) -> str:
    """Accept '7d' / '24h' / an ISO timestamp."""
    if not value:
        return ""
    val = value.strip()
    if val[-1:] in ("d", "h") and val[:-1].isdigit():
        delta = timedelta(days=int(val[:-1])) if val[-1] == "d" else timedelta(hours=int(val[:-1]))
        return (datetime.now(timezone.utc) - delta).isoformat()
    return val


def status() -> Dict:
    """Where the memory lives and whether it's reachable."""
    online = _is_online(recheck=True)
    info = {
        "enabled": enabled(),
        "online": online,
        "base": BASE,
        "collection": COLLECTION,
        "project": PROJECT,
        "spool": str(SPOOL),
        "spool_pending": len(_spool_read()),
        "spool_dropped": spool_dropped(),
        "spool_caps": {"max_bytes": SPOOL_MAX_BYTES,
                       "max_entries": SPOOL_MAX_ENTRIES,
                       "max_age_days": SPOOL_MAX_AGE_DAYS},
        "entries": 0,
        "by_kind": {},
    }
    if online:
        rows = recall(limit=500)
        info["entries"] = len(rows)
        by_kind: Dict[str, int] = {}
        for row in rows:
            key = row.get("kind") or "?"
            by_kind[key] = by_kind.get(key, 0) + 1
        info["by_kind"] = by_kind
    else:
        info["hint"] = (
            "Start the PocketBase that owns this collection, e.g. "
            "`python3 pb_journal.py serve` in SimpleAgentOS."
        )
    return info


# ── Mirrors (called from LiveFeed / Ledger; all best-effort) ──────────

def _feed_kinds() -> Optional[set]:
    raw = os.environ.get("NOVA_JOURNAL_FEED_KINDS", "")
    if raw.strip() == "*":
        return None  # mirror everything
    if raw.strip():
        return set(k.strip() for k in raw.split(",") if k.strip())
    return set(_DEFAULT_FEED_KINDS)


def mirror_feed_event(kind: str, detail: str = "", sid: str = "") -> None:
    """Mirror one Live Feed row. Filtered: see NOVA_JOURNAL_FEED_KINDS."""
    if not enabled():
        return
    try:
        allowed = _feed_kinds()
        if allowed is not None and kind not in allowed:
            return
        remember(
            "%s %s" % (kind, detail) if detail else str(kind),
            kind="event",
            source="coworking.live_feed",
            tags=["coworking", kind],
            path_ref=detail if detail else "",
            session_id=sid,
            importance=0.4,
            metadata={"feed_kind": kind},
        )
    except Exception:
        pass


def mirror_decision(decision: Any, row_hash: str = "") -> None:
    """Mirror one persona-Ledger decision. The ledger stays the source of truth.

    Carries the row hash so a journal entry can always be traced back to the
    chain it came from.
    """
    if not enabled():
        return
    try:
        body = "%s\n\nChoice: %s\nRationale: %s" % (
            getattr(decision, "subject", ""),
            getattr(decision, "choice", ""),
            getattr(decision, "rationale", ""),
        )
        remember(
            body,
            kind="decision",
            title=str(getattr(decision, "subject", ""))[:120],
            source="persona.ledger",
            actor=str(getattr(decision, "persona_id", "") or "novasystem"),
            session_id=str(getattr(decision, "session_id", "") or ""),
            tags=["ledger", "decision",
                  str(getattr(decision, "reversibility", "") or "")],
            importance=float(getattr(decision, "confidence_at_decision", 0.5) or 0.5),
            metadata={
                "decision_id": getattr(decision, "id", ""),
                "row_hash": row_hash,
                "reversibility": getattr(decision, "reversibility", ""),
                "alternatives": list(getattr(decision, "alternatives", []) or []),
                "evidence_refs": list(getattr(decision, "evidence_refs", []) or []),
                "supersedes": getattr(decision, "supersedes", None),
            },
        )
    except Exception:
        pass
