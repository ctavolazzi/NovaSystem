"""Install the Live Feed hook into an agent harness.

Currently targets Claude Code, which reads ``~/.claude/settings.json`` and
fires ``PostToolUse`` after every tool call and ``Stop`` at the end of a turn.
Other harnesses can be added here; nothing else in the package knows about a
specific agent runtime.

Editing a user's settings file is the riskiest thing this package does, so:

- the existing file is backed up before any write
- unrelated keys, hooks, and formatting are preserved
- installing twice is a no-op rather than a duplicate entry
- ``--dry-run`` shows the resulting JSON without touching anything
- a settings file that is not valid JSON aborts the install rather than being
  overwritten with something clean

Uninstall removes only the entries this installer added.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

HOOK_FILENAME = "live-feed.sh"

# Tools worth recording. Read-heavy tools are included on purpose: a long
# research stretch should look like activity, not like a stall. The renderer
# collapses consecutive runs so they take one row, not twenty.
DEFAULT_MATCHER = ("Bash|Edit|Write|MultiEdit|NotebookEdit|Read|Grep|Glob|"
                   "Task|TodoWrite|WebFetch|WebSearch")


def agent_home() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR",
                               Path.home() / ".claude")).expanduser()


def settings_path() -> Path:
    return agent_home() / "settings.json"


def hook_source_path() -> Path:
    return Path(__file__).resolve().parent / "hooks" / HOOK_FILENAME


def hook_target_path() -> Path:
    return agent_home() / "hooks" / HOOK_FILENAME


def _hook_entries(target: Path, matcher: str) -> Dict[str, Dict]:
    """The two entries this installer owns, keyed by hook event."""
    command = f'bash "{target}"'
    return {
        "PostToolUse": {
            "matcher": matcher,
            "hooks": [{
                "type": "command",
                "command": f"{command} record",
                "timeout": 10,
            }],
        },
        "Stop": {
            "hooks": [{
                "type": "command",
                "command": f"{command} flush",
                "timeout": 30,
            }],
        },
    }


def _owns(entry: Dict) -> bool:
    """True if an existing settings entry was installed by us."""
    for hook in entry.get("hooks", []) or []:
        if HOOK_FILENAME in str(hook.get("command", "")):
            return True
    return False


def _load_settings(path: Path) -> Dict:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"{path} is not valid JSON ({e}). Refusing to overwrite it. "
            f"Fix the file by hand, then run this again."
        ) from None
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _backup(path: Path) -> Optional[Path]:
    if not path.is_file():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.name}.{stamp}.bak")
    shutil.copy2(path, backup)
    return backup


def install(matcher: str = DEFAULT_MATCHER, dry_run: bool = False) -> Dict:
    """Copy the hook script into place and wire it into agent settings."""
    source, target = hook_source_path(), hook_target_path()
    if not source.is_file():
        raise FileNotFoundError(f"bundled hook missing: {source}")

    settings_file = settings_path()
    settings = _load_settings(settings_file)
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"{settings_file}: 'hooks' must be an object")

    entries = _hook_entries(target, matcher)
    changed: List[str] = []

    for event, entry in entries.items():
        bucket = hooks.setdefault(event, [])
        if not isinstance(bucket, list):
            raise ValueError(f"{settings_file}: hooks.{event} must be a list")
        existing = next((i for i, e in enumerate(bucket)
                         if isinstance(e, dict) and _owns(e)), None)
        if existing is None:
            bucket.append(entry)
            changed.append(f"added hooks.{event}")
        elif bucket[existing] != entry:
            bucket[existing] = entry
            changed.append(f"updated hooks.{event}")

    rendered = json.dumps(settings, indent=2) + "\n"

    if dry_run:
        return {"status": "dry-run", "settings": settings_file,
                "hook": target, "changes": changed, "preview": rendered}

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)

    backup = None
    if changed:
        backup = _backup(settings_file)
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings_file.write_text(rendered, encoding="utf-8")

    return {
        "status": "installed",
        "hook": str(target),
        "settings": str(settings_file),
        "backup": str(backup) if backup else None,
        "changes": changed or ["settings already current"],
    }


def uninstall(dry_run: bool = False) -> Dict:
    """Remove only the entries this installer added, and the hook script."""
    settings_file = settings_path()
    settings = _load_settings(settings_file)
    hooks = settings.get("hooks", {}) or {}
    removed: List[str] = []

    for event in ("PostToolUse", "Stop"):
        bucket = hooks.get(event)
        if not isinstance(bucket, list):
            continue
        kept = [e for e in bucket
                if not (isinstance(e, dict) and _owns(e))]
        if len(kept) != len(bucket):
            removed.append(f"removed hooks.{event}")
            if kept:
                hooks[event] = kept
            else:
                hooks.pop(event, None)

    if not hooks:
        settings.pop("hooks", None)

    target = hook_target_path()
    if dry_run:
        return {"status": "dry-run", "changes": removed,
                "would_delete": str(target) if target.is_file() else None}

    backup = None
    if removed:
        backup = _backup(settings_file)
        settings_file.write_text(json.dumps(settings, indent=2) + "\n",
                                 encoding="utf-8")
    if target.is_file():
        target.unlink()
        removed.append(f"deleted {target}")

    return {"status": "uninstalled",
            "backup": str(backup) if backup else None,
            "changes": removed or ["nothing was installed"]}


def status() -> Dict:
    """Report what is installed, for `novasystem coworking doctor`."""
    target = hook_target_path()
    settings_file = settings_path()
    wired: List[str] = []
    error = None
    try:
        hooks = _load_settings(settings_file).get("hooks", {}) or {}
        for event, bucket in hooks.items():
            if isinstance(bucket, list) and any(
                    isinstance(e, dict) and _owns(e) for e in bucket):
                wired.append(event)
    except ValueError as e:
        error = str(e)

    return {
        "hook_installed": target.is_file(),
        "hook_path": str(target),
        "hook_executable": target.is_file() and os.access(target, os.X_OK),
        "settings_path": str(settings_file),
        "wired_events": sorted(wired),
        "jq_available": shutil.which("jq") is not None,
        "error": error,
    }
