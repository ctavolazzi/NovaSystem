"""`novasystem coworking` subcommands.

Kept in the coworking package rather than the top-level CLI so the whole layer
stays self-contained: nothing here imports Docker, git, or the repository
installer, and the parser can be attached to any argparse tree.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .config import Config, describe, load_config


def add_parser(subparsers) -> argparse.ArgumentParser:
    """Attach the `coworking` command group to an existing subparser set."""
    parser = subparsers.add_parser(
        "coworking",
        help="Shared work log for AI collaborators",
        description=(
            "A shared, human-readable workspace for working alongside an AI "
            "agent. One markdown file per day, with the agent's activity at "
            "the top where you can watch it happen."
        ),
    )
    parser.add_argument("--root", help="workspace root (overrides config and "
                                       "$NOVA_COWORKING_DIR)")
    parser.add_argument("--date", help="YYYY-MM-DD (default: today)")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="machine-readable output")

    sub = parser.add_subparsers(dest="coworking_command",
                                help="Coworking command")

    sub.add_parser("init", help="Create today's work log from the template")
    sub.add_parser("config", help="Show resolved paths and section schema")
    sub.add_parser("status", help="Show per-section fill state")
    sub.add_parser("render", help="Rebuild the Live Feed section now")
    sub.add_parser("show", help="Print the Live Feed markdown without writing")

    p_read = sub.add_parser("read", help="Print one section")
    p_read.add_argument("section")

    p_write = sub.add_parser("write", help="Write one section")
    p_write.add_argument("section")
    p_write.add_argument("content", nargs="?",
                         help="content, or omit to read stdin")
    p_write.add_argument("--append", action="store_true",
                         help="append instead of replacing")
    p_write.add_argument("--actor", default="agent")

    p_focus = sub.add_parser("focus", help="Set the 'Now:' headline")
    p_focus.add_argument("text")

    p_note = sub.add_parser("note", help="Add one manual entry to the feed")
    p_note.add_argument("text")

    p_log = sub.add_parser("log", help="Append a session log entry")
    p_log.add_argument("focus")
    p_log.add_argument("--change", action="append", default=[],
                       help="repeatable")
    p_log.add_argument("--next", dest="next_steps", default="")
    p_log.add_argument("--file", action="append", default=[], dest="files",
                       help="repeatable")

    p_audit = sub.add_parser("audit", help="Scan for loose ends")
    p_audit.add_argument("--since", metavar="HH:MM",
                         help="only count files modified at or after this "
                              "time today, so another session's dirty tree is "
                              "not reported as yours")
    p_audit.add_argument("--repo", action="append", default=[],
                         help="repository to inspect (repeatable, default cwd)")

    p_migrate = sub.add_parser("migrate",
                               help="Bring logs onto the current layout")
    p_migrate.add_argument("--all", action="store_true",
                           help="every log in the workspace")
    p_migrate.add_argument("--write", action="store_true",
                           help="apply changes (default is a dry run)")

    p_install = sub.add_parser("install-hook",
                               help="Install the Live Feed agent hook")
    p_install.add_argument("--dry-run", action="store_true")
    p_install.add_argument("--matcher",
                           help="tool-name regex the hook fires on")

    p_uninstall = sub.add_parser("uninstall-hook",
                                 help="Remove the Live Feed agent hook")
    p_uninstall.add_argument("--dry-run", action="store_true")

    sub.add_parser("doctor", help="Check the hook install and workspace")

    return parser


def _config(args) -> Config:
    return load_config(root=Path(args.root).expanduser() if args.root else None)


def _emit(args, payload, text: Optional[str] = None) -> int:
    if getattr(args, "as_json", False):
        print(json.dumps(payload, indent=2, default=str))
    elif text is not None:
        print(text)
    else:
        print(json.dumps(payload, indent=2, default=str))
    return 0


def handle(args) -> int:
    """Dispatch a parsed `coworking` invocation."""
    command = getattr(args, "coworking_command", None)
    if not command:
        print("usage: novasystem coworking <command>  "
              "(try: novasystem coworking --help)")
        return 0

    config = _config(args)
    date = getattr(args, "date", None)

    # Imported per-command so a broken optional dependency only breaks the
    # command that needs it.
    if command == "config":
        return _emit(args, {"root": str(config.root),
                            "log_dir": str(config.log_dir),
                            "feed_dir": str(config.feed_dir),
                            "source": config.source,
                            "sections": [s.name for s in config.sections]},
                     describe(config))

    if command == "init":
        from .document import Document
        doc = Document(date, config)
        existed = doc.exists()
        path = doc.create()
        return _emit(args, {"status": "exists" if existed else "created",
                            "path": str(path)},
                     f"{'exists' if existed else 'created'}: {path}")

    if command == "status":
        from .document import Document
        doc = Document(date, config)
        if not doc.exists():
            print(f"no work log at {doc.path}. Run: novasystem coworking init")
            return 1
        state = doc.status()
        icons = {"filled": "●", "template": "◐", "empty": "○", "absent": "·"}
        text = "\n".join(f"  {icons.get(v, '?')} {k:<14} {v}"
                         for k, v in state.items())
        return _emit(args, state, text)

    if command in ("render", "show"):
        from .live_feed import LiveFeed
        feed = LiveFeed(date, config)
        if command == "show":
            return _emit(args, {"markdown": feed.render_markdown()},
                         feed.render_markdown())
        result = feed.render()
        return _emit(args, result,
                     f"live feed: {result.get('status')}"
                     + (f" ({result['reason']})" if result.get("reason") else ""))

    if command == "read":
        from .document import Document
        return _emit(args, {"section": args.section,
                            "content": Document(date, config).read_section(args.section)},
                     Document(date, config).read_section(args.section))

    if command == "write":
        from .document import Document
        content = args.content if args.content is not None else sys.stdin.read()
        result = Document(date, config).write_section(
            args.section, content, actor=args.actor,
            mode="append" if args.append else "replace")
        return _emit(args, result, f"{result['status']}: {args.section}")

    if command == "focus":
        from .live_feed import LiveFeed
        feed = LiveFeed(date, config)
        feed.set_focus(args.text)
        feed.render()
        return _emit(args, {"status": "set", "focus": args.text},
                     f"focus: {args.text}")

    if command == "note":
        from .live_feed import LiveFeed
        feed = LiveFeed(date, config)
        feed.append("note", args.text)
        feed.render()
        return _emit(args, {"status": "added", "note": args.text},
                     f"noted: {args.text}")

    if command == "log":
        from .document import Document
        result = Document(date, config).append_session_log(
            focus=args.focus, changes=args.change,
            next_steps=args.next_steps, files=args.files)
        return _emit(args, result, f"session log: {result['status']}")

    if command == "audit":
        from .audit import format_report, run_audit
        try:
            results = run_audit(config=config, since=args.since,
                                repos=[Path(r) for r in args.repo] or None)
        except ValueError as e:
            print(str(e))
            return 2
        _emit(args, results, format_report(results))
        return 1 if any(r["status"] == "fail" for r in results) else 0

    if command == "migrate":
        from . import migrate as migrate_mod
        if args.all:
            results = migrate_mod.migrate_all(write=args.write, config=config)
        else:
            results = [migrate_mod.migrate_document(date, write=args.write,
                                                    config=config)]
        lines = []
        for r in results:
            mark = {"unchanged": "○", "skipped": "·", "refused": "✗"}.get(
                r["status"], "●")
            lines.append(f"  {mark} {Path(r['path']).stem}: {r['status']}"
                         + (f" ({r['reason']})" if r.get("reason") else ""))
            if r.get("added"):
                lines.append(f"      added: {', '.join(r['added'])}")
        if not args.write and any(str(r["status"]).startswith("would-")
                                  for r in results):
            lines.append("\nDry run. Re-run with --write to apply.")
        _emit(args, results, "\n".join(lines))
        return 1 if any(r["status"] == "refused" for r in results) else 0

    if command in ("install-hook", "uninstall-hook"):
        from . import install as installer
        if command == "install-hook":
            kwargs = {"dry_run": args.dry_run}
            if args.matcher:
                kwargs["matcher"] = args.matcher
            result = installer.install(**kwargs)
        else:
            result = installer.uninstall(dry_run=args.dry_run)
        text = f"{result['status']}\n" + "\n".join(
            f"  {c}" for c in result.get("changes", []))
        if result.get("backup"):
            text += f"\n  backup: {result['backup']}"
        return _emit(args, result, text)

    if command == "doctor":
        from . import install as installer
        state = installer.status()
        state["workspace"] = str(config.root)
        state["workspace_exists"] = config.root.exists()
        marks = {True: "ok", False: "MISSING"}
        text = "\n".join([
            f"  workspace      {state['workspace']} "
            f"({marks[state['workspace_exists']]})",
            f"  hook script    {state['hook_path']} "
            f"({marks[state['hook_installed']]})",
            f"  executable     {marks[state['hook_executable']]}",
            f"  wired events   {', '.join(state['wired_events']) or 'none'}",
            f"  jq available   {marks[state['jq_available']]}",
        ])
        if state.get("error"):
            text += f"\n  error          {state['error']}"
        _emit(args, state, text)
        ready = (state["hook_installed"] and state["hook_executable"]
                 and state["wired_events"] and state["jq_available"])
        return 0 if ready else 1

    print(f"unknown coworking command: {command}")
    return 2
