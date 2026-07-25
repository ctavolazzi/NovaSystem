"""Agent personas: durable identity for Nova agents.

Today a Nova agent's identity is a class attribute::

    class DCEAgent(BaseAgent):
        ROLE_DESCRIPTION = "You are the Discussion Continuity Expert..."

That is a job description, not a persona. It has no continuity, no record, and no
capacity to be wrong in a way it can later notice. Two DCE instances in the same
process are indistinguishable, and neither knows what any earlier DCE decided.

A persona here has four parts:

``charter``
    What this agent is for, in one sentence. The thing it is accountable to.
``commitments``
    Rules the agent holds itself to, checkable after the fact. These are the
    basis of self-evaluation: a commitment nothing can violate is decoration.
``defers_to``
    Which other personas outrank it on which subjects. Prevents the CAE and the
    DCE from silently fighting over the same call.
``id``
    Stable across sessions, so the decision ledger can attribute a three-month-old
    decision to the same identity making one now.

Personas are versioned and append-only, same as decisions. Revising a persona
writes a new row; the old one stays readable, so a decision made in March can
still be read against the charter that was in force in March. Judging an old
decision by a charter written afterwards is how you manufacture false regret.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from .ledger import DEFAULT_BUSY_TIMEOUT_S, open_connection

SCHEMA = """
CREATE TABLE IF NOT EXISTS personas (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id  TEXT    NOT NULL,
    version     INTEGER NOT NULL,
    name        TEXT    NOT NULL,
    role        TEXT    NOT NULL,
    charter     TEXT    NOT NULL,
    commitments TEXT    NOT NULL DEFAULT '[]',
    defers_to   TEXT    NOT NULL DEFAULT '{}',
    voice       TEXT,
    mirrors     TEXT,
    created_at  REAL    NOT NULL,
    UNIQUE (persona_id, version)
);

CREATE INDEX IF NOT EXISTS idx_personas_id ON personas(persona_id);

CREATE TRIGGER IF NOT EXISTS personas_no_update
BEFORE UPDATE ON personas
BEGIN
    SELECT RAISE(ABORT, 'personas are versioned and append-only: revise() instead');
END;

CREATE TRIGGER IF NOT EXISTS personas_no_delete
BEFORE DELETE ON personas
BEGIN
    SELECT RAISE(ABORT, 'personas are versioned and append-only: rows are kept');
END;
"""


class PersonaError(RuntimeError):
    """Raised for invalid persona definitions or unknown lookups."""


@dataclass(frozen=True)
class Persona:
    """A durable agent identity."""

    persona_id: str
    name: str
    role: str
    charter: str
    commitments: Sequence[str] = field(default_factory=tuple)
    defers_to: Mapping[str, str] = field(default_factory=dict)
    voice: Optional[str] = None
    mirrors: Optional[str] = None
    version: int = 1

    def __post_init__(self) -> None:
        for attr in ("persona_id", "name", "role", "charter"):
            if not str(getattr(self, attr)).strip():
                raise PersonaError(f"{attr} must not be empty")
        if not self.commitments:
            raise PersonaError(
                f"persona {self.persona_id!r} declares no commitments; a persona "
                "with nothing it can violate cannot be self-evaluated"
            )

    def mirror(
        self,
        persona_id: str,
        name: str,
        role: str,
        charter: str,
        commitments: Sequence[str] = (),
        **kwargs: Any,
    ) -> "Persona":
        """Derive a sibling persona that keeps this one's structural contract.

        Mirroring copies the *shape*, not the content: the new persona inherits
        this persona's commitments as a floor and adds its own on top, and records
        what it was mirrored from. Roles stay distinct because an agent team of
        identical personas is one agent with extra latency.
        """
        inherited = tuple(self.commitments)
        added = tuple(c for c in commitments if c not in inherited)
        return Persona(
            persona_id=persona_id,
            name=name,
            role=role,
            charter=charter,
            commitments=inherited + added,
            defers_to=dict(kwargs.pop("defers_to", {})),
            voice=kwargs.pop("voice", self.voice),
            mirrors=self.persona_id,
            version=1,
            **kwargs,
        )

    def system_prompt(self) -> str:
        """Render the persona as an instruction block."""
        lines = [f"You are {self.name} ({self.role}).", "", f"Charter: {self.charter}"]
        if self.commitments:
            lines += ["", "You hold yourself to these commitments:"]
            lines += [f"  {i}. {c}" for i, c in enumerate(self.commitments, 1)]
        if self.defers_to:
            lines += ["", "Deference:"]
            lines += [f"  On {sub}, defer to {who}." for sub, who in
                      sorted(self.defers_to.items())]
        if self.voice:
            lines += ["", f"Voice: {self.voice}"]
        return "\n".join(lines)


# --------------------------------------------------------------- reference set

DCE = Persona(
    persona_id="dce",
    name="DCE",
    role="Discussion Continuity Expert",
    charter=(
        "Hold the thread of a problem from first statement to shipped decision, "
        "so that work already done is never silently redone or silently dropped."
    ),
    commitments=(
        "Check precedent before deciding. If this subject was decided before, say "
        "so and either follow it or supersede it explicitly.",
        "Never restate a prior decision as though it were new.",
        "Carry unresolved threads forward by name; a thread that stops being "
        "mentioned is a thread that was dropped, not one that was closed.",
        "State what would change your mind at the time you decide, not after.",
    ),
    defers_to={"risk assessment": "cae", "domain specifics": "domain-expert"},
    voice="Plain, sequential, oriented to what happens next.",
)

CAE = DCE.mirror(
    persona_id="cae",
    name="CAE",
    role="Critical Analysis Expert",
    charter=(
        "Find the reason a proposed decision fails before it is committed, and "
        "test the reason rather than asserting it."
    ),
    commitments=(
        "Produce a concrete failure scenario, not a general concern.",
        "Verify a claim against the artifact before repeating it.",
        "Say plainly when a proposal survives scrutiny; a critic who never "
        "approves is noise.",
    ),
    defers_to={"sequencing": "dce"},
    voice="Direct, specific, evidence first.",
)


def domain_expert(domain: str) -> Persona:
    """Mirror the DCE contract into a domain specialist."""
    slug = domain.lower().replace(" ", "-")
    return DCE.mirror(
        persona_id=f"domain-{slug}",
        name=f"Domain Expert ({domain})",
        role=f"Domain Expert in {domain}",
        charter=(
            f"Supply what is actually true about {domain}, including where the "
            f"established practice does not apply to this case."
        ),
        commitments=(
            f"Distinguish {domain} practice from {domain} folklore, and say which "
            "one is being offered.",
            "Name the conditions under which the recommendation stops holding.",
        ),
        defers_to={"sequencing": "dce", "risk assessment": "cae"},
    )


BUILTIN_PERSONAS = {p.persona_id: p for p in (DCE, CAE)}


# ---------------------------------------------------------------------- store

class PersonaStore:
    """Versioned, append-only persona storage, sharing the ledger database."""

    def __init__(self, path: Path | str,
                 busy_timeout: float = DEFAULT_BUSY_TIMEOUT_S,
                 cross_thread: bool = False) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._con = open_connection(
            self.path, busy_timeout, cross_thread=cross_thread
        )
        self._con.executescript(SCHEMA)
        self._con.commit()

    def __enter__(self) -> "PersonaStore":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        self._con.close()

    def register(self, persona: Persona) -> Persona:
        """Store a persona at its next version. Idempotent for identical content."""
        current = self.get(persona.persona_id)
        if current is not None and self._same_content(current, persona):
            return current
        version = (current.version + 1) if current else 1
        stored = Persona(
            persona_id=persona.persona_id,
            name=persona.name,
            role=persona.role,
            charter=persona.charter,
            commitments=tuple(persona.commitments),
            defers_to=dict(persona.defers_to),
            voice=persona.voice,
            mirrors=persona.mirrors,
            version=version,
        )
        with self._con:
            self._con.execute(
                """INSERT INTO personas (persona_id, version, name, role, charter,
                                         commitments, defers_to, voice, mirrors,
                                         created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    stored.persona_id, stored.version, stored.name, stored.role,
                    stored.charter, json.dumps(list(stored.commitments)),
                    json.dumps(dict(stored.defers_to)), stored.voice,
                    stored.mirrors, time.time(),
                ),
            )
        return stored

    def revise(self, persona_id: str, **changes: Any) -> Persona:
        """Write a new version. The previous version stays readable."""
        current = self.get(persona_id)
        if current is None:
            raise PersonaError(f"unknown persona {persona_id!r}")
        merged = Persona(
            persona_id=current.persona_id,
            name=changes.get("name", current.name),
            role=changes.get("role", current.role),
            charter=changes.get("charter", current.charter),
            commitments=tuple(changes.get("commitments", current.commitments)),
            defers_to=dict(changes.get("defers_to", current.defers_to)),
            voice=changes.get("voice", current.voice),
            mirrors=current.mirrors,
        )
        return self.register(merged)

    def get(self, persona_id: str, version: Optional[int] = None) -> Optional[Persona]:
        if version is None:
            row = self._con.execute(
                "SELECT * FROM personas WHERE persona_id = ? "
                "ORDER BY version DESC LIMIT 1", (persona_id,)
            ).fetchone()
        else:
            row = self._con.execute(
                "SELECT * FROM personas WHERE persona_id = ? AND version = ?",
                (persona_id, version),
            ).fetchone()
        return self._row_to_persona(row) if row else None

    def history(self, persona_id: str) -> list[Persona]:
        rows = self._con.execute(
            "SELECT * FROM personas WHERE persona_id = ? ORDER BY version",
            (persona_id,),
        ).fetchall()
        return [self._row_to_persona(r) for r in rows]

    def list_personas(self) -> list[Persona]:
        rows = self._con.execute(
            "SELECT p.* FROM personas p JOIN ("
            "  SELECT persona_id, MAX(version) v FROM personas GROUP BY persona_id"
            ") m ON p.persona_id = m.persona_id AND p.version = m.v "
            "ORDER BY p.persona_id"
        ).fetchall()
        return [self._row_to_persona(r) for r in rows]

    def bootstrap(self) -> list[Persona]:
        """Register the built-in DCE and CAE. Safe to call repeatedly."""
        return [self.register(p) for p in BUILTIN_PERSONAS.values()]

    @staticmethod
    def _same_content(a: Persona, b: Persona) -> bool:
        return (
            a.name == b.name and a.role == b.role and a.charter == b.charter
            and tuple(a.commitments) == tuple(b.commitments)
            and dict(a.defers_to) == dict(b.defers_to)
            and a.voice == b.voice
        )

    @staticmethod
    def _row_to_persona(row: Any) -> Persona:
        return Persona(
            persona_id=row["persona_id"],
            name=row["name"],
            role=row["role"],
            charter=row["charter"],
            commitments=tuple(json.loads(row["commitments"])),
            defers_to=json.loads(row["defers_to"]),
            voice=row["voice"],
            mirrors=row["mirrors"],
            version=row["version"],
        )
