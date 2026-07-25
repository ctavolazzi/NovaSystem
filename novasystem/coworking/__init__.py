"""Coworking layer: a shared, human-readable workspace for AI collaborators.

The problem this solves is not capability, it is *visibility*. An agent that
works for twenty minutes produces a wall of tool calls you cannot watch and a
summary you have to trust. The coworking layer replaces both with one plain
markdown document that the agent writes into as it works and a human can read,
scroll, and screen-record in real time.

Four pieces:

``document``
    A markdown file with named sections and a safe write API. Sections are
    addressed by name, writes are atomic and lock-guarded, and the layout
    puts the agent's work at the TOP of the document, where it is visible
    without scrolling.

``live_feed``
    A section rebuilt from an activity log on every agent tool call. Recording
    is done by a shell hook so it costs milliseconds; rendering runs detached.
    The result is a document that updates while you watch it.

``migrate``
    Layouts change. This moves whole sections of documents already on disk to
    match the current schema, verifying every section body is byte-identical
    before it writes.

``audit``
    Scans for what a session left behind: schema drift, hooks that are not
    installed, work done but never logged, uncommitted trees.

Nothing here assumes a particular note-taking app. The default workspace lives
under ``~/.novasystem/coworking``; point it at an Obsidian vault, a git repo,
or any directory via ``NOVA_COWORKING_DIR``. See ``config.Config``.

Submodules resolve lazily, matching the parent package: importing
``novasystem.coworking`` must not require ruamel or portalocker to be present
until something actually reads or writes a document.
"""

from typing import TYPE_CHECKING

__all__ = [
    "Config",
    "Document",
    "LiveFeed",
    "SECTION_SCHEMA",
    "load_config",
    "migrate_all",
    "migrate_document",
    "run_audit",
]

# Public name -> submodule that defines it.
#
# Deliberately NOT named `migrate` or `audit`: those are submodule names, and a
# lazy attribute of the same name shadows the module, so
# `from novasystem.coworking import migrate` would hand back a function instead
# of the module. Leaving the bare names unexported lets the import system fall
# through to normal submodule resolution.
_EXPORTS = {
    "Config": ".config",
    "load_config": ".config",
    "SECTION_SCHEMA": ".config",
    "Document": ".document",
    "LiveFeed": ".live_feed",
    "migrate_document": ".migrate",
    "migrate_all": ".migrate",
    "run_audit": ".audit",
}


def __getattr__(name: str):
    """Resolve a public name to its submodule on first access."""
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module
    module = import_module(module_path, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_EXPORTS))


if TYPE_CHECKING:  # pragma: no cover - import-time typing only
    from .audit import run_audit
    from .config import SECTION_SCHEMA, Config, load_config
    from .document import Document
    from .live_feed import LiveFeed
    from .migrate import migrate_all, migrate_document
