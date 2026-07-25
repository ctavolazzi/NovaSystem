"""Append-only, hash-chained decision ledger.

This is the memory a Nova agent decides against. Every decision an agent makes is
written here once and never rewritten. Corrections are new rows that supersede old
ones, so the record of having been wrong survives alongside the correction.

Three properties, each of which came out of a measurement rather than a preference:

1. ``busy_timeout`` is set explicitly on every connection.
   Measured with 8 concurrent processes writing 40 rows each:

       rollback journal, timeout=0 ->  43/320 committed, 277 lost
       WAL,              timeout=0 ->  23/320 committed, 297 lost
       WAL,              timeout=5 -> 320/320 committed,   0 lost

   WAL alone made concurrent loss worse. ``busy_timeout`` is the variable that
   decides whether writes survive; WAL is a throughput win layered on top.

2. Append-only is enforced in the database, not just in the API.
   SQL triggers raise on UPDATE and DELETE. A caller holding a raw connection
   cannot quietly rewrite history, and neither can a future maintainer who adds a
   convenience method without reading this docstring.

3. Rows are hash-chained.
   Each row commits to its predecessor, so removing or editing a row at the file
   level is detectable by :func:`Ledger.verify_chain` rather than silent.

The column vocabulary deliberately mirrors Empirica's ``decisions`` table
(choice / alternatives / rationale / confidence_at_decision / reversibility /
outcome / regret_score) so the two stores can be reconciled instead of diverging.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterator, Optional, Sequence

# Measured floor. See module docstring; do not lower this to chase latency.
DEFAULT_BUSY_TIMEOUT_S = 5.0

GENESIS_HASH = "0" * 64

REVERSIBILITY = ("exploratory", "committal", "forced")

SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
    seq                    INTEGER PRIMARY KEY AUTOINCREMENT,
    id                     TEXT    NOT NULL UNIQUE,
    persona_id             TEXT    NOT NULL,
    session_id             TEXT,
    project                TEXT,
    subject                TEXT    NOT NULL,
    choice                 TEXT    NOT NULL,
    alternatives           TEXT    NOT NULL DEFAULT '[]',
    rationale              TEXT    NOT NULL,
    confidence_at_decision REAL    NOT NULL
        CHECK (confidence_at_decision BETWEEN 0.0 AND 1.0),
    reversibility          TEXT    NOT NULL DEFAULT 'committal'
        CHECK (reversibility IN ('exploratory', 'committal', 'forced')),
    evidence_refs          TEXT    NOT NULL DEFAULT '[]',
    supersedes             TEXT,
    outcome                TEXT,
    regret_score           REAL CHECK (regret_score IS NULL
                                       OR regret_score BETWEEN 0.0 AND 1.0),
    created_timestamp      REAL    NOT NULL,
    prev_hash              TEXT    NOT NULL,
    row_hash               TEXT    NOT NULL UNIQUE,
    FOREIGN KEY (supersedes) REFERENCES decisions(id)
);

CREATE INDEX IF NOT EXISTS idx_decisions_persona  ON decisions(persona_id);
CREATE INDEX IF NOT EXISTS idx_decisions_subject  ON decisions(subject);
CREATE INDEX IF NOT EXISTS idx_decisions_project  ON decisions(project);
CREATE INDEX IF NOT EXISTS idx_decisions_supersedes ON decisions(supersedes);

-- Append-only, enforced by the engine rather than by convention.
CREATE TRIGGER IF NOT EXISTS decisions_no_update
BEFORE UPDATE ON decisions
BEGIN
    SELECT RAISE(ABORT, 'decision ledger is append-only: supersede instead of updating');
END;

CREATE TRIGGER IF NOT EXISTS decisions_no_delete
BEFORE DELETE ON decisions
BEGIN
    SELECT RAISE(ABORT, 'decision ledger is append-only: rows are never deleted');
END;
"""


def open_connection(
    path: Path | str,
    busy_timeout: float = DEFAULT_BUSY_TIMEOUT_S,
    wal: bool = True,
    cross_thread: bool = False,
) -> sqlite3.Connection:
    """Open a SQLite connection with the settings that survive concurrency.

    Shared by every store in this package so the measured configuration is
    applied in one place rather than remembered in several. A non-positive
    ``busy_timeout`` is refused outright; see the module docstring for the
    measurement showing why it silently loses writes.

    ``cross_thread`` passes ``check_same_thread=False`` and must only be set when
    the caller can guarantee the connection is used **sequentially**, never
    concurrently. There is exactly one such case in this package: a web request
    that owns its own connection. FastAPI creates a dependency in one threadpool
    thread and may run its teardown in another, so the connection legitimately
    crosses threads without ever being shared:

        ProgrammingError: SQLite objects created in a thread can only be used in
        that same thread.

    sqlite3's check is conservative. It forbids all cross-thread use, while the
    property actually required is the absence of *concurrent* use. Setting this
    on a connection that two requests can reach at once trades a loud error for
    silent corruption, so it is opt-in and documented rather than defaulted.
    """
    if busy_timeout <= 0:
        raise ValueError(
            "busy_timeout must be > 0; a zero timeout drops concurrent writes "
            "(measured: 297 of 320 lost under WAL)"
        )
    con = sqlite3.connect(
        str(path), timeout=busy_timeout, check_same_thread=not cross_thread
    )
    con.row_factory = sqlite3.Row
    # timeout= covers the Python driver; busy_timeout covers the engine.
    con.execute(f"PRAGMA busy_timeout = {int(busy_timeout * 1000)}")
    if wal:
        con.execute("PRAGMA journal_mode = WAL")
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA synchronous = FULL")
    return con


class LedgerError(RuntimeError):
    """Base class for ledger failures."""


class ChainBroken(LedgerError):
    """The hash chain does not verify. Some row was edited or removed."""


@dataclass(frozen=True)
class Decision:
    """One decision, as recorded. Immutable by construction."""

    subject: str
    choice: str
    rationale: str
    persona_id: str
    confidence_at_decision: float = 0.5
    alternatives: Sequence[str] = field(default_factory=tuple)
    reversibility: str = "committal"
    evidence_refs: Sequence[str] = field(default_factory=tuple)
    session_id: Optional[str] = None
    project: Optional[str] = None
    supersedes: Optional[str] = None
    id: str = field(default_factory=lambda: f"dec-{uuid.uuid4().hex[:12]}")

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_at_decision <= 1.0:
            raise ValueError(
                f"confidence_at_decision must be in [0,1], got "
                f"{self.confidence_at_decision}"
            )
        if self.reversibility not in REVERSIBILITY:
            raise ValueError(
                f"reversibility must be one of {REVERSIBILITY}, "
                f"got {self.reversibility!r}"
            )
        for name in ("subject", "choice", "rationale", "persona_id"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"{name} must not be empty")


def _canonical_payload(d: Decision, created_timestamp: float) -> str:
    """Stable serialization used for hashing. Key order is fixed by sort_keys."""
    return json.dumps(
        {
            "id": d.id,
            "persona_id": d.persona_id,
            "session_id": d.session_id,
            "project": d.project,
            "subject": d.subject,
            "choice": d.choice,
            "alternatives": list(d.alternatives),
            "rationale": d.rationale,
            "confidence_at_decision": d.confidence_at_decision,
            "reversibility": d.reversibility,
            "evidence_refs": list(d.evidence_refs),
            "supersedes": d.supersedes,
            "created_timestamp": created_timestamp,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def row_digest(prev_hash: str, payload: str) -> str:
    return hashlib.sha256(f"{prev_hash}{payload}".encode("utf-8")).hexdigest()


class Ledger:
    """Append-only decision store backed by SQLite.

    Usage::

        with Ledger(path) as ledger:
            ledger.record(Decision(...))
    """

    def __init__(
        self,
        path: Path | str,
        busy_timeout: float = DEFAULT_BUSY_TIMEOUT_S,
        wal: bool = True,
        cross_thread: bool = False,
    ) -> None:
        if busy_timeout <= 0:
            # Guard the exact misconfiguration that loses writes silently.
            raise ValueError(
                "busy_timeout must be > 0; a zero timeout drops concurrent writes "
                "(measured: 297 of 320 lost under WAL)"
            )
        self.path = Path(path)
        self.busy_timeout = busy_timeout
        self._wal = wal
        self._cross_thread = cross_thread
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._con = self._connect()
        self._con.executescript(SCHEMA)
        self._con.commit()

    def _connect(self) -> sqlite3.Connection:
        return open_connection(
            self.path, self.busy_timeout, self._wal, self._cross_thread
        )

    def __enter__(self) -> "Ledger":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        self._con.close()

    # ---------------------------------------------------------------- writes

    def record(self, decision: Decision) -> str:
        """Append one decision. Returns its row hash.

        The read of the chain head and the insert happen inside one IMMEDIATE
        transaction, so two processes cannot both build on the same predecessor.
        """
        ts = time.time()
        payload = _canonical_payload(decision, ts)

        with self._con:  # commits on success, rolls back on exception
            self._con.execute("BEGIN IMMEDIATE")
            head = self._con.execute(
                "SELECT row_hash FROM decisions ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            prev = head["row_hash"] if head else GENESIS_HASH

            if decision.supersedes is not None:
                exists = self._con.execute(
                    "SELECT 1 FROM decisions WHERE id = ?", (decision.supersedes,)
                ).fetchone()
                if not exists:
                    raise LedgerError(
                        f"supersedes references unknown decision "
                        f"{decision.supersedes!r}"
                    )

            digest = row_digest(prev, payload)
            self._con.execute(
                """
                INSERT INTO decisions (
                    id, persona_id, session_id, project, subject, choice,
                    alternatives, rationale, confidence_at_decision, reversibility,
                    evidence_refs, supersedes, created_timestamp, prev_hash, row_hash
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    decision.id,
                    decision.persona_id,
                    decision.session_id,
                    decision.project,
                    decision.subject,
                    decision.choice,
                    json.dumps(list(decision.alternatives)),
                    decision.rationale,
                    decision.confidence_at_decision,
                    decision.reversibility,
                    json.dumps(list(decision.evidence_refs)),
                    decision.supersedes,
                    ts,
                    prev,
                    digest,
                ),
            )
        return digest

    def supersede(
        self,
        old_id: str,
        new_choice: str,
        rationale: str,
        persona_id: str,
        **kwargs: Any,
    ) -> str:
        """Correct an earlier decision by appending, never by editing.

        The superseded row stays exactly as it was written. That is the point:
        an agent that cannot see it was wrong cannot calibrate.
        """
        old = self.get(old_id)
        if old is None:
            raise LedgerError(f"cannot supersede unknown decision {old_id!r}")
        return self.record(
            Decision(
                subject=old["subject"],
                choice=new_choice,
                rationale=rationale,
                persona_id=persona_id,
                supersedes=old_id,
                project=old["project"],
                **kwargs,
            )
        )

    # ----------------------------------------------------------------- reads

    def get(self, decision_id: str) -> Optional[sqlite3.Row]:
        return self._con.execute(
            "SELECT * FROM decisions WHERE id = ?", (decision_id,)
        ).fetchone()

    def all(self) -> list[sqlite3.Row]:
        return self._con.execute("SELECT * FROM decisions ORDER BY seq").fetchall()

    def count(self) -> int:
        return self._con.execute("SELECT COUNT(*) AS n FROM decisions").fetchone()["n"]

    def by_subject(self, subject: str, include_superseded: bool = False) -> list[sqlite3.Row]:
        """Decisions on a subject, newest first.

        By default the rows that something else supersedes are filtered out, so a
        caller asking "what do we currently think" gets the current answer.
        """
        rows = self._con.execute(
            "SELECT * FROM decisions WHERE subject = ? ORDER BY seq DESC", (subject,)
        ).fetchall()
        if include_superseded:
            return rows
        superseded = {
            r["supersedes"]
            for r in self._con.execute(
                "SELECT supersedes FROM decisions WHERE supersedes IS NOT NULL"
            ).fetchall()
        }
        return [r for r in rows if r["id"] not in superseded]

    def by_persona(self, persona_id: str) -> list[sqlite3.Row]:
        return self._con.execute(
            "SELECT * FROM decisions WHERE persona_id = ? ORDER BY seq DESC",
            (persona_id,),
        ).fetchall()

    def chain(self) -> Iterator[sqlite3.Row]:
        yield from self._con.execute("SELECT * FROM decisions ORDER BY seq")

    # ------------------------------------------------------------ integrity

    def verify_chain(self) -> tuple[bool, Optional[str]]:
        """Walk the chain and recompute every digest.

        Returns ``(True, None)`` when intact, otherwise ``(False, reason)``.
        Detects edited rows, removed rows, and reordering.
        """
        prev = GENESIS_HASH
        for row in self.chain():
            payload = _canonical_payload(
                Decision(
                    id=row["id"],
                    persona_id=row["persona_id"],
                    session_id=row["session_id"],
                    project=row["project"],
                    subject=row["subject"],
                    choice=row["choice"],
                    alternatives=tuple(json.loads(row["alternatives"])),
                    rationale=row["rationale"],
                    confidence_at_decision=row["confidence_at_decision"],
                    reversibility=row["reversibility"],
                    evidence_refs=tuple(json.loads(row["evidence_refs"])),
                    supersedes=row["supersedes"],
                ),
                row["created_timestamp"],
            )
            expected = row_digest(prev, payload)
            if row["prev_hash"] != prev:
                return False, (
                    f"row {row['seq']} ({row['id']}) expected prev_hash {prev[:12]}, "
                    f"found {row['prev_hash'][:12]}"
                )
            if expected != row["row_hash"]:
                return False, (
                    f"row {row['seq']} ({row['id']}) content does not match its "
                    f"hash: recomputed {expected[:12]}, stored {row['row_hash'][:12]}"
                )
            prev = row["row_hash"]
        return True, None

    def require_intact(self) -> None:
        ok, reason = self.verify_chain()
        if not ok:
            raise ChainBroken(reason or "chain verification failed")
