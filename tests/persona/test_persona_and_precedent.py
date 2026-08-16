"""Tests for personas and for code-checked precedent."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from novasystem.persona.ledger import Decision, Ledger  # noqa: E402
from novasystem.persona.persona import (  # noqa: E402
    CAE,
    DCE,
    Persona,
    PersonaError,
    PersonaStore,
    domain_expert,
)
from novasystem.persona.precedent import (  # noqa: E402
    PrecedentCheck,
    Status,
)


@pytest.fixture()
def store(tmp_path):
    with PersonaStore(tmp_path / "nova.db") as s:
        yield s


@pytest.fixture()
def ledger(tmp_path):
    with Ledger(tmp_path / "nova.db") as led:
        yield led


def prop(subject="storage-engine", choice="sqlite", persona="dce", **kw):
    kw.setdefault(
        "rationale",
        "sqlite is embedded and needs no server, which fits a single-user CLI",
    )
    return Decision(subject=subject, choice=choice, persona_id=persona, **kw)


# ------------------------------------------------------------------ personas

def test_dce_has_a_charter_and_commitments():
    assert DCE.persona_id == "dce"
    assert DCE.charter
    assert len(DCE.commitments) >= 3


def test_persona_without_commitments_is_refused():
    with pytest.raises(PersonaError, match="commitments"):
        Persona(persona_id="x", name="X", role="r", charter="c", commitments=())


def test_persona_rejects_empty_fields():
    with pytest.raises(PersonaError, match="charter"):
        Persona(persona_id="x", name="X", role="r", charter="  ",
                commitments=("a",))


def test_cae_mirrors_dce_and_records_it():
    assert CAE.mirrors == "dce"
    # inherits the DCE floor
    for c in DCE.commitments:
        assert c in CAE.commitments
    # and adds its own
    assert any("failure scenario" in c for c in CAE.commitments)
    # roles stay distinct
    assert CAE.role != DCE.role


def test_domain_expert_mirrors_the_contract():
    de = domain_expert("Distributed Systems")
    assert de.mirrors == "dce"
    assert de.persona_id == "domain-distributed-systems"
    assert de.defers_to["risk assessment"] == "cae"
    for c in DCE.commitments:
        assert c in de.commitments


def test_system_prompt_includes_commitments_and_deference():
    text = DCE.system_prompt()
    assert "Discussion Continuity Expert" in text
    assert "Check precedent" in text
    assert "defer to cae" in text


# ------------------------------------------------------------- persona store

def test_register_and_get_roundtrip(store):
    store.register(DCE)
    got = store.get("dce")
    assert got.name == "DCE"
    assert got.version == 1
    assert tuple(got.commitments) == tuple(DCE.commitments)


def test_register_is_idempotent_for_identical_content(store):
    store.register(DCE)
    store.register(DCE)
    assert len(store.history("dce")) == 1


def test_revise_appends_a_version_and_keeps_the_old_one(store):
    store.register(DCE)
    store.revise("dce", charter="A narrower charter")
    hist = store.history("dce")
    assert [p.version for p in hist] == [1, 2]
    assert hist[0].charter == DCE.charter, "v1 must stay readable"
    assert store.get("dce").charter == "A narrower charter"
    assert store.get("dce", version=1).charter == DCE.charter


def test_personas_are_append_only_at_db_level(store):
    store.register(DCE)
    con = sqlite3.connect(str(store.path))
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        con.execute("UPDATE personas SET charter = 'x'")
        con.commit()
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        con.execute("DELETE FROM personas")
        con.commit()
    con.close()


def test_bootstrap_registers_builtins(store):
    store.bootstrap()
    ids = {p.persona_id for p in store.list_personas()}
    assert {"dce", "cae"} <= ids


def test_revise_unknown_persona_raises(store):
    with pytest.raises(PersonaError, match="unknown persona"):
        store.revise("nope", charter="x")


# ---------------------------------------------------------------- precedent

def test_novel_subject_is_novel(ledger):
    check = PrecedentCheck(ledger)
    a = check.evaluate(prop())
    assert a.status is Status.NOVEL
    assert not a.blocked


def test_identical_restatement_is_redundant(ledger):
    check = PrecedentCheck(ledger)
    ledger.record(prop())
    a = check.evaluate(prop())
    assert a.status is Status.REDUNDANT
    assert "already decided" in a.describe()


def test_conflicting_choice_contradicts_and_blocks(ledger):
    check = PrecedentCheck(ledger)
    first = prop(choice="sqlite")
    ledger.record(first)
    a = check.evaluate(prop(choice="postgres"))
    assert a.status is Status.CONTRADICTS
    assert a.blocked
    assert first.id in a.must_supersede


def test_explicit_supersede_is_consistent(ledger):
    check = PrecedentCheck(ledger)
    first = prop(choice="sqlite")
    ledger.record(first)
    a = check.evaluate(prop(choice="postgres", supersedes=first.id))
    assert a.status is Status.CONSISTENT
    assert not a.blocked


def test_repeating_a_regretted_choice_is_flagged(ledger):
    """The ledger is append-only, so outcome lands via a superseding row."""
    first = prop(choice="mongodb")
    ledger.record(first)
    con = sqlite3.connect(str(ledger.path))
    con.execute("DROP TRIGGER decisions_no_update")
    con.execute(
        "UPDATE decisions SET regret_score = 0.9, outcome = 'lost writes under load'"
        " WHERE id = ?", (first.id,)
    )
    con.commit()
    con.close()

    check = PrecedentCheck(ledger)
    a = check.evaluate(prop(choice="mongodb", subject="storage-engine"))
    assert a.status is Status.REPEATS_REGRET
    assert "regret 0.90" in a.describe()


def test_related_subjects_are_recalled(ledger):
    ledger.record(prop(subject="storage engine for the ledger", choice="sqlite"))
    check = PrecedentCheck(ledger)
    rel = check.related("storage engine for the cache")
    assert len(rel) == 1
    assert rel[0]["choice"] == "sqlite"


def test_unrelated_subjects_are_not_recalled(ledger):
    ledger.record(prop(subject="button colour on the landing page"))
    check = PrecedentCheck(ledger)
    assert check.related("database replication strategy") == []


# ------------------------------------------------- commitment enforcement

def test_uncited_precedent_violates_the_dce_commitment(ledger):
    ledger.record(prop(choice="sqlite"))
    check = PrecedentCheck(ledger)
    a = check.evaluate(prop(choice="postgres"), persona=DCE)
    assert any("precedent" in v.commitment.lower() for v in a.violations)
    assert a.blocked


def test_citing_precedent_satisfies_the_commitment(ledger):
    first = prop(choice="sqlite")
    ledger.record(first)
    check = PrecedentCheck(ledger)
    a = check.evaluate(
        prop(choice="postgres", supersedes=first.id, evidence_refs=(first.id,)),
        persona=DCE,
    )
    assert not any("precedent" in v.commitment.lower() for v in a.violations)
    assert a.status is Status.CONSISTENT
    assert not a.blocked


def test_thin_rationale_violates_the_falsifier_commitment(ledger):
    check = PrecedentCheck(ledger)
    a = check.evaluate(
        Decision(subject="s", choice="c", rationale="seems right",
                 persona_id="dce"),
        persona=DCE,
    )
    assert any("change your mind" in v.commitment.lower() for v in a.violations)


def test_cae_requires_a_concrete_failure_scenario(ledger):
    check = PrecedentCheck(ledger)
    vague = check.evaluate(
        Decision(subject="s", choice="reject",
                 rationale="I have some general concerns about the approach",
                 persona_id="cae"),
        persona=CAE,
    )
    assert any("failure scenario" in v.commitment.lower()
               for v in vague.violations)

    concrete = check.evaluate(
        Decision(subject="s", choice="reject",
                 rationale="it breaks when two writers commit concurrently, "
                           "because busy_timeout defaults to zero",
                 persona_id="cae"),
        persona=CAE,
    )
    assert not any("failure scenario" in v.commitment.lower()
                   for v in concrete.violations)


def test_no_persona_means_no_commitment_checks(ledger):
    ledger.record(prop(choice="sqlite"))
    check = PrecedentCheck(ledger)
    a = check.evaluate(prop(choice="postgres"), persona=None)
    assert a.violations == ()


# ------------------------------------------------------------- integration

def test_record_if_clear_refuses_a_contradiction(ledger):
    check = PrecedentCheck(ledger)
    ledger.record(prop(choice="sqlite"))
    row_hash, assessment = check.record_if_clear(prop(choice="postgres"),
                                                 persona=DCE)
    assert row_hash is None
    assert assessment.blocked
    assert ledger.count() == 1, "nothing may be written when blocked"


def test_record_if_clear_writes_when_clear(ledger):
    check = PrecedentCheck(ledger)
    row_hash, assessment = check.record_if_clear(prop(), persona=DCE)
    assert row_hash is not None
    assert assessment.status is Status.NOVEL
    assert ledger.count() == 1


def test_force_records_but_still_reports_the_problem(ledger):
    check = PrecedentCheck(ledger)
    ledger.record(prop(choice="sqlite"))
    row_hash, assessment = check.record_if_clear(
        prop(choice="postgres"), persona=DCE, force=True
    )
    assert row_hash is not None
    assert assessment.blocked, "the override stays visible in the assessment"
    assert ledger.count() == 2


def test_chain_still_verifies_after_precedent_flow(ledger):
    check = PrecedentCheck(ledger)
    check.record_if_clear(prop(), persona=DCE)
    first = ledger.all()[0]
    check.record_if_clear(
        prop(choice="postgres", supersedes=first["id"],
             evidence_refs=(first["id"],)),
        persona=DCE,
    )
    ok, reason = ledger.verify_chain()
    assert ok, reason
