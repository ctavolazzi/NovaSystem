"""FastAPI application layer over the persona and decision ledger.

A note on the shape, because the obvious implementation is broken.

The tempting version holds one ledger on ``app.state`` and shares it. That fails
the moment it runs, and it fails in a way that only appears under load:

    ProgrammingError: SQLite objects created in a thread can only be used in
    that same thread. The object was created in thread id 4657804800 and this
    is thread id 123145584140288.

FastAPI runs ``def`` endpoints in an anyio worker threadpool, so consecutive
requests land on different threads. A shared sqlite3 connection is not usable
across them. Passing ``check_same_thread=False`` silences the exception and
replaces it with unsynchronised concurrent access to one connection, which is
worse: the failure stops being loud.

So every request opens its own connection and closes it. SQLite connection setup
is cheap, and cross-process durability is already handled by ``busy_timeout``,
measured at 320/320 writes surviving 8 concurrent processes where a zero timeout
lost 297. Under ``uvicorn --workers N`` those are real processes, so that
measurement is the operating regime, not a synthetic one.

Endpoints are ``def`` rather than ``async def`` on purpose. SQLite calls block,
and a blocking call inside ``async def`` stalls the event loop for every other
request. Declaring them sync hands them to the threadpool, which is correct for
blocking I/O.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator, Optional

try:
    from fastapi import Depends, FastAPI, HTTPException, status
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "the API layer needs fastapi and pydantic: pip install 'fastapi' 'uvicorn'"
    ) from exc

from .ledger import Decision, Ledger, LedgerError
from .persona import BUILTIN_PERSONAS, Persona, PersonaError, PersonaStore
from .precedent import Assessment, PrecedentCheck

DB_ENV_VAR = "NOVA_LEDGER_DB"
DEFAULT_DB = Path.home() / ".novasystem" / "persona.db"


def database_path() -> Path:
    return Path(os.environ.get(DB_ENV_VAR, str(DEFAULT_DB)))


# ------------------------------------------------------------------ schemas

class DecisionIn(BaseModel):
    subject: str = Field(min_length=1)
    choice: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    persona_id: str = Field(min_length=1)
    confidence_at_decision: float = Field(default=0.5, ge=0.0, le=1.0)
    alternatives: list[str] = Field(default_factory=list)
    reversibility: str = "committal"
    evidence_refs: list[str] = Field(default_factory=list)
    supersedes: Optional[str] = None
    session_id: Optional[str] = None
    project: Optional[str] = None

    def to_decision(self) -> Decision:
        return Decision(
            subject=self.subject,
            choice=self.choice,
            rationale=self.rationale,
            persona_id=self.persona_id,
            confidence_at_decision=self.confidence_at_decision,
            alternatives=tuple(self.alternatives),
            reversibility=self.reversibility,
            evidence_refs=tuple(self.evidence_refs),
            supersedes=self.supersedes,
            session_id=self.session_id,
            project=self.project,
        )


class ViolationOut(BaseModel):
    commitment: str
    detail: str


class AssessmentOut(BaseModel):
    status: str
    subject: str
    blocked: bool
    notes: list[str]
    violations: list[ViolationOut]
    must_supersede: list[str]
    prior_active: list[str]
    related: list[str]

    @classmethod
    def of(cls, a: Assessment) -> "AssessmentOut":
        return cls(
            status=a.status.value,
            subject=a.subject,
            blocked=a.blocked,
            notes=list(a.notes),
            violations=[ViolationOut(commitment=v.commitment, detail=v.detail)
                        for v in a.violations],
            must_supersede=list(a.must_supersede),
            prior_active=[r["id"] for r in a.prior_active],
            related=[r["id"] for r in a.related],
        )


class DecisionOut(BaseModel):
    id: str
    persona_id: str
    subject: str
    choice: str
    rationale: str
    confidence_at_decision: float
    reversibility: str
    supersedes: Optional[str]
    outcome: Optional[str]
    regret_score: Optional[float]
    created_timestamp: float
    row_hash: str

    @classmethod
    def of(cls, row) -> "DecisionOut":
        return cls(**{k: row[k] for k in cls.model_fields})


class RecordResult(BaseModel):
    recorded: bool
    row_hash: Optional[str]
    decision_id: str
    assessment: AssessmentOut


class PersonaOut(BaseModel):
    persona_id: str
    name: str
    role: str
    charter: str
    commitments: list[str]
    defers_to: dict[str, str]
    voice: Optional[str]
    mirrors: Optional[str]
    version: int

    @classmethod
    def of(cls, p: Persona) -> "PersonaOut":
        return cls(
            persona_id=p.persona_id, name=p.name, role=p.role, charter=p.charter,
            commitments=list(p.commitments), defers_to=dict(p.defers_to),
            voice=p.voice, mirrors=p.mirrors, version=p.version,
        )


class IntegrityOut(BaseModel):
    intact: bool
    reason: Optional[str]
    decisions: int


# --------------------------------------------------------------- dependencies

def get_ledger() -> Iterator[Ledger]:
    """One connection per request, owned by that request alone.

    cross_thread=True is required, not optional: FastAPI creates the dependency
    on one threadpool thread and may run the finally-block teardown on another.
    The connection is never shared between requests, so it is used sequentially
    and the sqlite3 same-thread check is over-strict here. See open_connection.
    """
    led = Ledger(database_path(), cross_thread=True)
    try:
        yield led
    finally:
        led.close()


def get_store() -> Iterator[PersonaStore]:
    store = PersonaStore(database_path(), cross_thread=True)
    try:
        yield store
    finally:
        store.close()


# ---------------------------------------------------------------------- app

def create_app() -> FastAPI:
    app = FastAPI(
        title="NovaSystem Persona Ledger",
        version="0.1.0",
        description=(
            "Durable identity and decision history for Nova agents. Decisions are "
            "append-only and hash-chained; proposals are checked against precedent "
            "before they are written."
        ),
    )

    @app.on_event("startup")
    def _bootstrap() -> None:
        store = PersonaStore(database_path())
        try:
            store.bootstrap()
        finally:
            store.close()

    # ------------------------------------------------------------ decisions

    @app.post("/decisions", response_model=RecordResult,
              status_code=status.HTTP_201_CREATED)
    def propose_decision(
        payload: DecisionIn,
        force: bool = False,
        led: Ledger = Depends(get_ledger),
        store: PersonaStore = Depends(get_store),
    ):
        """Evaluate a proposal against precedent, then record it if clear.

        Returns 409 when the proposal contradicts an active decision or violates
        the persona's commitments. The assessment is in the response body either
        way, so a rejection explains itself.
        """
        try:
            decision = payload.to_decision()
            persona = store.get(payload.persona_id) or BUILTIN_PERSONAS.get(
                payload.persona_id
            )
            row_hash, assessment = PrecedentCheck(led).record_if_clear(
                decision, persona, force=force
            )
        except (ValueError, LedgerError) as exc:
            # Domain validation the Pydantic schema cannot express: the
            # reversibility enum and the supersedes foreign key.
            raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

        result = RecordResult(
            recorded=row_hash is not None,
            row_hash=row_hash,
            decision_id=decision.id,
            assessment=AssessmentOut.of(assessment),
        )
        if row_hash is None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, detail=result.model_dump()
            )
        return result

    @app.get("/decisions", response_model=list[DecisionOut])
    def list_decisions(persona_id: Optional[str] = None,
                       led: Ledger = Depends(get_ledger)):
        rows = led.by_persona(persona_id) if persona_id else led.all()
        return [DecisionOut.of(r) for r in rows]

    @app.get("/decisions/{decision_id}", response_model=DecisionOut)
    def get_decision(decision_id: str, led: Ledger = Depends(get_ledger)):
        row = led.get(decision_id)
        if row is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such decision")
        return DecisionOut.of(row)

    @app.get("/subjects/{subject}/precedent", response_model=AssessmentOut)
    def subject_precedent(subject: str, choice: str = "",
                          persona_id: str = "dce",
                          led: Ledger = Depends(get_ledger),
                          store: PersonaStore = Depends(get_store)):
        """Ask what the record already says, without proposing anything."""
        probe = Decision(
            subject=subject, choice=choice or "<query>",
            rationale="read-only precedent query, no decision is being made here",
            persona_id=persona_id,
        )
        persona = store.get(persona_id) or BUILTIN_PERSONAS.get(persona_id)
        return AssessmentOut.of(PrecedentCheck(led).evaluate(probe, persona))

    # ------------------------------------------------------------- personas

    @app.get("/personas", response_model=list[PersonaOut])
    def list_personas(store: PersonaStore = Depends(get_store)):
        return [PersonaOut.of(p) for p in store.list_personas()]

    @app.get("/personas/{persona_id}", response_model=PersonaOut)
    def get_persona(persona_id: str, version: Optional[int] = None,
                    store: PersonaStore = Depends(get_store)):
        p = store.get(persona_id, version)
        if p is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such persona")
        return PersonaOut.of(p)

    @app.get("/personas/{persona_id}/history", response_model=list[PersonaOut])
    def persona_history(persona_id: str,
                        store: PersonaStore = Depends(get_store)):
        hist = store.history(persona_id)
        if not hist:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such persona")
        return [PersonaOut.of(p) for p in hist]

    @app.post("/personas", response_model=PersonaOut,
              status_code=status.HTTP_201_CREATED)
    def register_persona(payload: PersonaOut,
                         store: PersonaStore = Depends(get_store)):
        try:
            p = Persona(
                persona_id=payload.persona_id, name=payload.name,
                role=payload.role, charter=payload.charter,
                commitments=tuple(payload.commitments),
                defers_to=dict(payload.defers_to), voice=payload.voice,
                mirrors=payload.mirrors,
            )
        except PersonaError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                str(exc)) from exc
        return PersonaOut.of(store.register(p))

    # ------------------------------------------------------------ integrity

    @app.get("/integrity", response_model=IntegrityOut)
    def integrity(led: Ledger = Depends(get_ledger)):
        """Recompute the hash chain. Cheap to poll, and the only honest health check."""
        ok, reason = led.verify_chain()
        return IntegrityOut(intact=ok, reason=reason, decisions=led.count())

    return app


app = create_app()
