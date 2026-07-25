"""
NovaSystem: Automated Repository Installation System

A system for automatically reading software repository documentation,
extracting installation instructions, and executing them in a secure sandbox.

Submodules are resolved lazily (PEP 562). ``import novasystem`` previously pulled
in ``docker``, ``git``, and the database layer at import time, so the package could
not be imported at all on a machine without Docker installed, and no subpackage
could be tested in isolation. The public API is unchanged: ``from novasystem import
Nova`` still works, it just no longer costs a Docker dependency to reach it.
"""

from typing import TYPE_CHECKING

# Version number should match the one in pyproject.toml
__version__ = "0.1.1"

# Public name -> submodule that defines it.
_EXPORTS = {
    "RepositoryHandler": ".repository",
    "DocumentationParser": ".parser",
    "Command": ".parser",
    "CommandType": ".parser",
    "CommandSource": ".parser",
    "DockerExecutor": ".docker",
    "CommandResult": ".docker",
    "DatabaseManager": ".database",
    "Nova": ".nova",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str):
    """Resolve a public name to its submodule on first access."""
    module_path = _EXPORTS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    module = import_module(module_path, __name__)
    value = getattr(module, name)
    globals()[name] = value  # cache, so later lookups skip __getattr__
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


if TYPE_CHECKING:  # keep static analysis and IDE completion working
    from .database import DatabaseManager
    from .docker import CommandResult, DockerExecutor
    from .nova import Nova
    from .parser import Command, CommandSource, CommandType, DocumentationParser
    from .repository import RepositoryHandler
