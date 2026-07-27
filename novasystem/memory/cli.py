"""
novasystem.memory.cli: `novasystem journal ...`

Same self-contained shape as the coworking parser: the whole feature lives in
its own package and the root CLI just mounts it.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from . import journal


def add_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "journal",
        help="Queryable memory: write things down and ask them back",
        description=(
            "NovaSystem's memory, backed by PocketBase. Mirroring from the Live "
            "Feed and the persona Ledger is opt-in (NOVA_JOURNAL=1); `log` and "
            "`query` work either way."
        ),
    )
    sub = parser.add_subparsers(dest="journal_command")

    sub.add_parser("status", help="Where memory lives and whether it's reachable")
    sub.add_parser("sync", help="Push entries written while PocketBase was down")

    p_log = sub.add_parser("log", help="Write one entry")
    p_log.add_argument("body", help="What to remember")
    p_log.add_argument("--kind", default="note",
                       help="note|finding|decision|question|event|error|reflection")
    p_log.add_argument("--title", default="")
    p_log.add_argument("--tags", default="", help="Comma-separated")
    p_log.add_argument("--session-id", default="")
    p_log.add_argument("--path-ref", default="")
    p_log.add_argument("--importance", type=float, default=0.5)

    p_query = sub.add_parser("query", help="Search memory")
    p_query.add_argument("text", nargs="?", default="")
    p_query.add_argument("--kind", default="")
    p_query.add_argument("--tags", default="")
    p_query.add_argument("--since", default="", help="ISO timestamp, or 7d / 24h")
    p_query.add_argument("-n", "--limit", type=int, default=25)
    p_query.add_argument("--all-projects", action="store_true",
                         help="Include entries from other projects sharing the collection")
    p_query.add_argument("--json", action="store_true", dest="as_json")

    p_recent = sub.add_parser("recent", help="Most recent entries")
    p_recent.add_argument("-n", "--limit", type=int, default=20)
    p_recent.add_argument("--kind", default="")
    p_recent.add_argument("--all-projects", action="store_true")
    p_recent.add_argument("--json", action="store_true", dest="as_json")

    return parser


def _print_rows(rows: List[Dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False, default=str))
        return
    if not rows:
        print("(nothing matched)")
        return
    for row in rows:
        ts = str(row.get("occurred_at") or "")[:19].replace("T", " ")
        kind = (row.get("kind") or "?")[:10].ljust(10)
        proj = (row.get("project") or "")[:14].ljust(14)
        title = (row.get("title") or row.get("body") or "").replace("\n", " ")
        line = "%s  %s  %s  %s" % (ts, kind, proj, title)
        if len(line) > 118:
            line = line[:117] + "…"
        if row.get("_source") == "spool":
            line += "  (unsynced)"
        print(line)
    print("\n%d entr%s" % (len(rows), "y" if len(rows) == 1 else "ies"))


def handle(args: Any) -> int:
    cmd = getattr(args, "journal_command", None)

    if cmd in (None, "status"):
        info = journal.status()
        print(json.dumps(info, indent=2, default=str))
        return 0 if info["online"] else 1

    if cmd == "sync":
        result = journal.sync()
        print(json.dumps(result, indent=2))
        return 0 if result.get("remaining", 0) == 0 else 1

    if cmd == "log":
        # force=True: an explicit CLI write should land whether or not the
        # background mirroring flag happens to be on.
        entry = journal.remember(
            args.body, kind=args.kind, force=True, title=args.title,
            tags=args.tags, session_id=args.session_id, path_ref=args.path_ref,
            importance=args.importance, source="cli",
        )
        if entry is None:
            print("could not build entry")
            return 1
        where = entry["_stored"]
        note = "" if where == "pocketbase" else "  (PocketBase offline, will sync)"
        print("logged %s → %s%s" % (entry["entry_id"], where, note))
        return 0

    if cmd in ("query", "recent"):
        project = None if getattr(args, "all_projects", False) else journal.PROJECT
        rows = journal.recall(
            getattr(args, "text", "") or "",
            kind=args.kind,
            tags=getattr(args, "tags", ""),
            since=getattr(args, "since", ""),
            limit=args.limit,
            project=project,
        )
        _print_rows(rows, getattr(args, "as_json", False))
        return 0

    print("unknown journal command: %s" % cmd)
    return 2
