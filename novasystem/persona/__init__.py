"""Persona and precedent layer for Nova agents.

Gives DCE, CAE, and domain experts a durable identity, an append-only decision
history, precedent recall that is checked by code rather than self-reported, and
a preservation interlock that treats "do not destroy work" as a separate
guarantee from "do not corrupt work".

The API layer is resolved lazily so this package stays usable without FastAPI
installed, for the same reason the parent package stopped importing eagerly.
"""

from .guardrail import (
    Authorization,
    Impact,
    Preservation,
    PreservationRefused,
    TreeImpact,
    Verdict,
    assess_tree_deletion,
)
from .ledger import ChainBroken, Decision, Ledger, LedgerError, open_connection
from .persona import (
    BUILTIN_PERSONAS,
    CAE,
    DCE,
    Persona,
    PersonaError,
    PersonaStore,
    domain_expert,
)
from .precedent import Assessment, PrecedentCheck, Status, Violation

__all__ = [
    "Assessment",
    "Authorization",
    "BUILTIN_PERSONAS",
    "CAE",
    "ChainBroken",
    "DCE",
    "Decision",
    "Impact",
    "Ledger",
    "LedgerError",
    "Persona",
    "PersonaError",
    "PersonaStore",
    "PrecedentCheck",
    "Preservation",
    "PreservationRefused",
    "Status",
    "TreeImpact",
    "Verdict",
    "Violation",
    "assess_tree_deletion",
    "domain_expert",
    "open_connection",
    "app",
    "create_app",
]


def __getattr__(name: str):
    """Resolve the FastAPI app lazily so fastapi stays an optional dependency."""
    if name in ("app", "create_app"):
        from . import api

        return getattr(api, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
