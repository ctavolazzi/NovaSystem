"""Precedent recall and self-evaluation, decided by code.

An agent asked to "check your work against precedent" will, if precedent is a
prompt instruction, reliably report that it checked. This module makes the check
mechanical so the answer does not depend on the agent's account of itself.

Everything here is deterministic. No model call, no embedding, no scoring that
cannot be reproduced from the ledger rows. That is the point: self-evaluation
that routes through the same faculty being evaluated is not evaluation.

Four questions get answered:

1. **Has this been decided before?** Exact subject match against active decisions.
2. **Does this contradict what is on record?** Same subject, different choice,
   without an explicit supersede. This is the common failure and it is silent.
3. **Is this repeating a decision that went badly?** Same choice as a prior
   decision that carries a high regret score.
4. **Did the agent honor its own commitments?** Persona commitments that are
   checkable are checked here rather than trusted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Sequence

from .ledger import Decision, Ledger
from .persona import Persona

REGRET_THRESHOLD = 0.6
STOPWORDS = frozenset(
    "a an the of for to in on and or is are be with we our this that it as by".split()
)


class Status(str, Enum):
    NOVEL = "novel"
    CONSISTENT = "consistent"
    REDUNDANT = "redundant"
    CONTRADICTS = "contradicts"
    REPEATS_REGRET = "repeats_regret"


@dataclass(frozen=True)
class Violation:
    commitment: str
    detail: str


@dataclass(frozen=True)
class Assessment:
    """Result of checking a proposed decision against the record."""

    status: Status
    subject: str
    prior_active: tuple[Any, ...] = ()
    related: tuple[Any, ...] = ()
    violations: tuple[Violation, ...] = ()
    must_supersede: tuple[str, ...] = ()
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def blocked(self) -> bool:
        """True when the proposal should not be recorded as-is."""
        return self.status is Status.CONTRADICTS or bool(self.violations)

    def describe(self) -> str:
        lines = [f"[{self.status.value}] {self.subject}"]
        lines += [f"  note: {n}" for n in self.notes]
        for v in self.violations:
            lines.append(f"  VIOLATION: {v.commitment}\n             {v.detail}")
        if self.must_supersede:
            lines.append(
                "  must supersede: " + ", ".join(self.must_supersede)
            )
        return "\n".join(lines)


def _tokens(text: str) -> set[str]:
    return {
        t for t in re.findall(r"[a-z0-9]+", text.lower())
        if t not in STOPWORDS and len(t) > 2
    }


def _overlap(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


class PrecedentCheck:
    """Evaluates a proposed decision against everything already on record."""

    def __init__(self, ledger: Ledger, relatedness: float = 0.34) -> None:
        self.ledger = ledger
        self.relatedness = relatedness

    # -------------------------------------------------------------- recall

    def prior_on_subject(self, subject: str) -> list[Any]:
        """Active decisions on exactly this subject, newest first."""
        return self.ledger.by_subject(subject, include_superseded=False)

    def related(self, subject: str, limit: int = 5) -> list[Any]:
        """Decisions on different but overlapping subjects.

        Token-overlap rather than embeddings, deliberately: it is reproducible,
        needs no model, and its failure mode is being too literal rather than
        confidently wrong.
        """
        seen: dict[str, tuple[float, Any]] = {}
        for row in self.ledger.all():
            if row["subject"] == subject:
                continue
            score = _overlap(subject, row["subject"])
            if score >= self.relatedness:
                prev = seen.get(row["subject"])
                if prev is None or score > prev[0]:
                    seen[row["subject"]] = (score, row)
        ranked = sorted(seen.values(), key=lambda t: -t[0])
        return [row for _, row in ranked[:limit]]

    # ---------------------------------------------------------- evaluation

    def evaluate(
        self, proposal: Decision, persona: Optional[Persona] = None
    ) -> Assessment:
        """Check a proposal against the record before it is written."""
        prior = self.prior_on_subject(proposal.subject)
        related = self.related(proposal.subject)
        notes: list[str] = []
        must_supersede: list[str] = []

        # Exclude any prior row this proposal already supersedes.
        unaddressed = [r for r in prior if r["id"] != proposal.supersedes]

        if not prior:
            status = Status.NOVEL
            notes.append("no prior decision on this subject")
        else:
            same_choice = [r for r in unaddressed
                           if r["choice"].strip().lower()
                           == proposal.choice.strip().lower()]
            differing = [r for r in unaddressed
                         if r["choice"].strip().lower()
                         != proposal.choice.strip().lower()]

            if proposal.supersedes and not unaddressed:
                status = Status.CONSISTENT
                notes.append(
                    f"explicitly supersedes {proposal.supersedes}; "
                    "revision is on the record"
                )
            elif differing:
                status = Status.CONTRADICTS
                must_supersede = [r["id"] for r in differing]
                notes.append(
                    f"{len(differing)} active decision(s) on this subject chose "
                    f"differently: "
                    + ", ".join(f"{r['id']}={r['choice']!r}" for r in differing[:3])
                )
                notes.append(
                    "record this as a supersede, or change the choice; a second "
                    "active decision on one subject means neither is the answer"
                )
            elif same_choice:
                status = Status.REDUNDANT
                notes.append(
                    f"already decided identically in {same_choice[0]['id']}; "
                    "restating it as new hides that the work was done"
                )
            else:
                status = Status.CONSISTENT

        # Did we previously choose this and regret it?
        regretted = [
            r for r in self.ledger.by_subject(proposal.subject,
                                              include_superseded=True)
            if r["choice"].strip().lower() == proposal.choice.strip().lower()
            and r["regret_score"] is not None
            and r["regret_score"] >= REGRET_THRESHOLD
        ]
        if regretted:
            status = Status.REPEATS_REGRET
            notes.append(
                f"this choice was made before in {regretted[0]['id']} and scored "
                f"regret {regretted[0]['regret_score']:.2f}; outcome was: "
                f"{regretted[0]['outcome'] or 'unrecorded'}"
            )

        violations = self._check_commitments(
            proposal, persona, prior=prior, related=related
        )

        return Assessment(
            status=status,
            subject=proposal.subject,
            prior_active=tuple(prior),
            related=tuple(related),
            violations=tuple(violations),
            must_supersede=tuple(must_supersede),
            notes=tuple(notes),
        )

    # -------------------------------------------------------- commitments

    def _check_commitments(
        self,
        proposal: Decision,
        persona: Optional[Persona],
        prior: Sequence[Any],
        related: Sequence[Any],
    ) -> list[Violation]:
        """Check the persona commitments that can be checked mechanically.

        Only commitments with an operational meaning are enforced. A commitment
        like "be thoughtful" is unenforceable and is left alone rather than
        pretended about.
        """
        if persona is None:
            return []
        violations: list[Violation] = []
        cited = {str(ref) for ref in proposal.evidence_refs}

        for commitment in persona.commitments:
            low = commitment.lower()

            if "precedent" in low and prior:
                # Only an exact-subject prior decision is strong enough to be a
                # violation. Merely related subjects are surfaced as context by
                # Assessment.related; treating them as binding would block every
                # novel decision that happens to share vocabulary with an old
                # one, which makes the check noise and gets it switched off.
                available = {r["id"] for r in prior}
                if not (cited & available):
                    violations.append(
                        Violation(
                            commitment,
                            f"{len(available)} prior decision(s) exist on this exact "
                            f"subject and none is cited in evidence_refs. "
                            f"Available: {', '.join(sorted(available))[:120]}",
                        )
                    )

            if "restate a prior decision" in low and prior:
                if any(
                    r["choice"].strip().lower() == proposal.choice.strip().lower()
                    and r["id"] != proposal.supersedes
                    for r in prior
                ):
                    violations.append(
                        Violation(
                            commitment,
                            "the proposed choice is identical to an active prior "
                            "decision and is not marked as superseding it",
                        )
                    )

            if "would change your mind" in low:
                if not proposal.rationale or len(proposal.rationale.split()) < 8:
                    violations.append(
                        Violation(
                            commitment,
                            "rationale is too short to contain a falsifier "
                            f"({len(proposal.rationale.split())} words)",
                        )
                    )

            if "failure scenario" in low:
                if not any(
                    w in proposal.rationale.lower()
                    for w in ("fails", "fail", "breaks", "when ", "if ")
                ):
                    violations.append(
                        Violation(
                            commitment,
                            "rationale states a concern without a concrete "
                            "failure scenario",
                        )
                    )

        return violations

    # ------------------------------------------------------------ recording

    def record_if_clear(
        self,
        proposal: Decision,
        persona: Optional[Persona] = None,
        force: bool = False,
    ) -> tuple[Optional[str], Assessment]:
        """Evaluate, then record only if the assessment is clear.

        Returns ``(row_hash_or_None, assessment)``. ``force=True`` records anyway,
        which is sometimes correct, but the assessment is returned either way so
        the override is visible rather than implicit.
        """
        assessment = self.evaluate(proposal, persona)
        if assessment.blocked and not force:
            return None, assessment
        return self.ledger.record(proposal), assessment
