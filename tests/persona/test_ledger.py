"""Tests for the append-only decision ledger.

These are adversarial: each one tries to do the thing the ledger claims to prevent.
A test that only confirms the happy path would not have caught af0dde2.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from novasystem.persona.ledger import (  # noqa: E402
    ChainBroken,
    Decision,
    Ledger,
    LedgerError,
)


@pytest.fixture()
def ledger(tmp_path):
    with Ledger(tmp_path / "ledger.db") as led:
        yield led


def mk(subject="db-choice", choice="sqlite", persona="dce", **kw):
    return Decision(
        subject=subject,
        choice=choice,
        rationale="because it is embedded and needs no server",
        persona_id=persona,
        **kw,
    )


# --------------------------------------------------------------- basic shape

def test_record_and_read_back(ledger):
    ledger.record(mk())
    assert ledger.count() == 1
    row = ledger.all()[0]
    assert row["choice"] == "sqlite"
    assert row["persona_id"] == "dce"
    assert row["reversibility"] == "committal"


def test_rejects_empty_required_fields():
    for bad in ("subject", "choice", "rationale", "persona_id"):
        with pytest.raises(ValueError, match=bad):
            Decision(**{**dict(subject="s", choice="c", rationale="r",
                               persona_id="p"), bad: "  "})


def test_rejects_out_of_range_confidence():
    with pytest.raises(ValueError, match="confidence"):
        Decision(subject="s", choice="c", rationale="r", persona_id="p",
                 confidence_at_decision=1.5)


def test_rejects_unknown_reversibility():
    with pytest.raises(ValueError, match="reversibility"):
        Decision(subject="s", choice="c", rationale="r", persona_id="p",
                 reversibility="maybe")


# ------------------------------------------------- append-only, at DB level

def test_update_is_blocked_by_trigger(ledger):
    """The API has no update method. This checks a raw connection cannot either."""
    ledger.record(mk())
    con = sqlite3.connect(str(ledger.path))
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        con.execute("UPDATE decisions SET choice = 'postgres'")
        con.commit()
    con.close()


def test_delete_is_blocked_by_trigger(ledger):
    ledger.record(mk())
    con = sqlite3.connect(str(ledger.path))
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        con.execute("DELETE FROM decisions")
        con.commit()
    con.close()
    assert ledger.count() == 1


def test_drop_table_would_be_the_real_attack(ledger, tmp_path):
    """Honesty check: triggers stop UPDATE/DELETE, not DROP.

    Documented rather than hidden. Protecting the file itself is the guardrail
    layer's job, not the ledger's.
    """
    ledger.record(mk())
    con = sqlite3.connect(str(ledger.path))
    con.execute("DROP TABLE decisions")
    con.commit()
    remaining = con.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE name='decisions'"
    ).fetchone()[0]
    con.close()
    assert remaining == 0, "DROP succeeded: ledger triggers do not cover DDL"


# ------------------------------------------------------------- supersession

def test_supersede_appends_and_preserves_the_original(ledger):
    first = mk(choice="sqlite")
    ledger.record(first)
    ledger.supersede(first.id, "postgres", "outgrew single-writer", "dce")

    assert ledger.count() == 2, "supersede must append, not replace"
    original = ledger.get(first.id)
    assert original["choice"] == "sqlite", "the record of being wrong must survive"

    current = ledger.by_subject("db-choice")
    assert len(current) == 1
    assert current[0]["choice"] == "postgres"

    full = ledger.by_subject("db-choice", include_superseded=True)
    assert len(full) == 2


def test_supersede_unknown_id_raises(ledger):
    with pytest.raises(LedgerError, match="unknown decision"):
        ledger.supersede("dec-nope", "x", "y", "dce")


def test_supersedes_fk_is_validated_on_record(ledger):
    with pytest.raises(LedgerError, match="unknown decision"):
        ledger.record(mk(supersedes="dec-doesnotexist"))


# ------------------------------------------------------------- hash chaining

def test_chain_verifies_when_intact(ledger):
    for i in range(5):
        ledger.record(mk(subject=f"s{i}"))
    ok, reason = ledger.verify_chain()
    assert ok, reason


def test_chain_detects_tampering(ledger, tmp_path):
    """Edit a row behind the ledger's back and confirm verification catches it."""
    for i in range(3):
        ledger.record(mk(subject=f"s{i}"))
    assert ledger.verify_chain()[0]

    # Bypass the triggers the only way that works: drop them, edit, restore.
    con = sqlite3.connect(str(ledger.path))
    con.execute("DROP TRIGGER decisions_no_update")
    con.execute("UPDATE decisions SET choice = 'tampered' WHERE seq = 2")
    con.commit()
    con.close()

    ok, reason = ledger.verify_chain()
    assert not ok
    assert "does not match its hash" in reason
    with pytest.raises(ChainBroken):
        ledger.require_intact()


def test_chain_detects_row_removal(ledger):
    for i in range(3):
        ledger.record(mk(subject=f"s{i}"))
    con = sqlite3.connect(str(ledger.path))
    con.execute("DROP TRIGGER decisions_no_delete")
    con.execute("DELETE FROM decisions WHERE seq = 2")
    con.commit()
    con.close()

    ok, reason = ledger.verify_chain()
    assert not ok
    assert "expected prev_hash" in reason


# ------------------------------------------------------------- concurrency

def _writer(args):
    db, who, rows = args
    led = Ledger(db)
    n = 0
    for i in range(rows):
        led.record(mk(subject=f"p{who}", choice=f"c{i}", persona=f"agent-{who}"))
        n += 1
    led.close()
    return n


def test_concurrent_processes_lose_no_writes(tmp_path):
    """The regression guard for F-10. Processes, not threads."""
    db = tmp_path / "concurrent.db"
    Ledger(db).close()  # create schema first

    writers, rows = 6, 15
    ctx = mp.get_context("spawn")
    with ctx.Pool(writers) as pool:
        counts = pool.map(_writer, [(str(db), w, rows) for w in range(writers)])

    assert sum(counts) == writers * rows
    with Ledger(db) as led:
        assert led.count() == writers * rows, "concurrent writes were lost"
        ok, reason = led.verify_chain()
        assert ok, f"chain broken under concurrency: {reason}"


def test_zero_busy_timeout_is_refused(tmp_path):
    """The misconfiguration that silently loses writes must not be constructible."""
    with pytest.raises(ValueError, match="busy_timeout"):
        Ledger(tmp_path / "x.db", busy_timeout=0)


def test_busy_timeout_is_actually_applied(tmp_path):
    led = Ledger(tmp_path / "x.db", busy_timeout=3.0)
    got = led._con.execute("PRAGMA busy_timeout").fetchone()[0]
    led.close()
    assert got == 3000


def test_wal_is_enabled_by_default(tmp_path):
    led = Ledger(tmp_path / "x.db")
    mode = led._con.execute("PRAGMA journal_mode").fetchone()[0]
    led.close()
    assert mode == "wal"


# ------------------------------------------------------------------ queries

def test_by_persona_scopes_correctly(ledger):
    ledger.record(mk(persona="dce"))
    ledger.record(mk(persona="cae", subject="other"))
    ledger.record(mk(persona="dce", subject="third"))
    assert len(ledger.by_persona("dce")) == 2
    assert len(ledger.by_persona("cae")) == 1


def test_alternatives_and_evidence_round_trip(ledger):
    d = mk(alternatives=("postgres", "duckdb"), evidence_refs=("F-10", "probe.py"))
    ledger.record(d)
    row = ledger.get(d.id)
    assert json.loads(row["alternatives"]) == ["postgres", "duckdb"]
    assert json.loads(row["evidence_refs"]) == ["F-10", "probe.py"]
