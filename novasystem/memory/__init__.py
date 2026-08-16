"""
novasystem.memory: queryable memory for NovaSystem.

The coworking Live Feed keeps events and the persona Ledger keeps decisions.
Both are good at recording and bad at answering. This subpackage mirrors them
into a PocketBase collection you can query.

Off unless ``NOVA_JOURNAL=1``. See ``novasystem.memory.journal``.
"""

from .journal import (  # noqa: F401
    disable,
    enable,
    enabled,
    recall,
    recent,
    remember,
    status,
    sync,
)

__all__ = ["remember", "recall", "recent", "status", "sync",
           "enabled", "enable", "disable"]
