"""
tests/memory/test_journal.py: NovaSystem's queryable memory.

The contract under test: mirroring is off by default, never raises, never loses
an entry, and the Ledger's hash chain is unaffected by anything the journal does.
"""

import json
import sys
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from novasystem.memory import journal  # noqa: E402


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    """Every test gets its own spool and starts with mirroring off."""
    monkeypatch.setattr(journal, "SPOOL", tmp_path / "spool.jsonl")
    monkeypatch.setattr(journal, "_forced", None)
    monkeypatch.delenv("NOVA_JOURNAL", raising=False)
    monkeypatch.delenv("NOVA_JOURNAL_FEED_KINDS", raising=False)
    yield
    journal._forced = None


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(journal, "_is_online", lambda recheck=False: False)
    journal.enable()


# SimpleAgentOS owns this collection (see its pb_migrations). It is a scratch
# twin of `agent_journal` with deletes allowed, so live tests can write real
# records and take them back out again. Writing them into `agent_journal`
# instead pollutes the shared memory both projects read from.
TEST_COLLECTION = "agent_journal_test"


def _scratch_records():
    """Rows currently in the scratch collection, or None if it isn't there."""
    try:
        req = urllib.request.Request(
            "%s/api/collections/%s/records?perPage=500" % (journal.BASE, TEST_COLLECTION)
        )
        with urllib.request.urlopen(req, timeout=journal.TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8")).get("items", [])
    except Exception:
        return None


def _purge_scratch():
    while True:
        rows = _scratch_records()
        if not rows:
            return
        for row in rows:
            req = urllib.request.Request(
                "%s/api/collections/%s/records/%s" % (journal.BASE, TEST_COLLECTION, row["id"]),
                method="DELETE",
            )
            try:
                urllib.request.urlopen(req, timeout=journal.TIMEOUT)
            except Exception:
                return  # server went away mid-teardown; not worth failing over


@pytest.fixture
def live(monkeypatch):
    if not journal._is_online(recheck=True):
        pytest.skip("PocketBase not running (pb_journal.py serve in SimpleAgentOS)")
    if _scratch_records() is None:
        pytest.skip(
            "%s missing. Restart PocketBase to apply SimpleAgentOS pb_migrations"
            % TEST_COLLECTION
        )
    monkeypatch.setattr(journal, "COLLECTION", TEST_COLLECTION)
    journal.enable()
    yield True
    _purge_scratch()


# ── Opt-in ────────────────────────────────────────────────────────────

def test_disabled_by_default():
    assert journal.enabled() is False
    assert journal.remember("should not be written") is None


def test_env_var_enables(monkeypatch):
    monkeypatch.setenv("NOVA_JOURNAL", "1")
    assert journal.enabled() is True


@pytest.mark.parametrize("value", ["0", "", "false", "no"])
def test_falsey_env_values_stay_off(monkeypatch, value):
    monkeypatch.setenv("NOVA_JOURNAL", value)
    assert journal.enabled() is False


def test_enable_disable_override_env(monkeypatch):
    monkeypatch.setenv("NOVA_JOURNAL", "0")
    journal.enable()
    assert journal.enabled() is True
    journal.disable()
    assert journal.enabled() is False


def test_force_writes_even_when_disabled(offline, monkeypatch):
    journal.disable()
    entry = journal.remember("explicit CLI write", force=True)
    assert entry is not None
    assert entry["_stored"] == "spool"


# ── Durability ────────────────────────────────────────────────────────

def test_spools_when_pocketbase_is_down(offline):
    entry = journal.remember("offline note", kind="finding", tags=["a", "b"])
    assert entry["_stored"] == "spool"
    lines = journal.SPOOL.read_text().strip().splitlines()
    assert json.loads(lines[0])["body"] == "offline note"
    assert json.loads(lines[0])["project"] == "NovaSystem"


def test_remember_never_raises(monkeypatch):
    journal.enable()

    def explode(*a, **k):
        raise RuntimeError("network on fire")

    monkeypatch.setattr(journal, "_is_online", explode)
    entry = journal.remember("must still land")  # must not raise
    assert entry["_stored"] == "spool"


def test_recall_reads_the_spool(offline):
    journal.remember("needle in nova memory", kind="finding", tags=["alpha"])
    journal.remember("unrelated", kind="note")
    assert len(journal.recall("needle")) == 1
    assert len(journal.recall(kind="finding")) == 1
    assert len(journal.recall(tags=["alpha"])) == 1
    assert len(journal.recall(tags=["nope"])) == 0


def test_recall_filters_by_project(offline):
    journal.remember("mine")
    assert len(journal.recall(project="NovaSystem")) == 1
    assert len(journal.recall(project="SomethingElse")) == 0
    assert len(journal.recall(project=None)) == 1  # cross-project view


def test_sync_keeps_entries_when_offline(offline):
    journal.remember("keep me")
    result = journal.sync()
    assert result["synced"] == 0 and result["remaining"] == 1


# ── Spool caps ────────────────────────────────────────────────────────

def test_spool_trim_drops_oldest_over_entry_cap(offline, monkeypatch):
    monkeypatch.setattr(journal, "SPOOL_MAX_ENTRIES", 3)
    monkeypatch.setattr(journal, "SPOOL_MAX_AGE_DAYS", 0)
    for i in range(6):
        journal.remember("entry %d" % i, occurred_at="2026-07-2%dT00:00:00+00:00" % i)

    assert journal._spool_trim() == 3
    assert [e["body"] for e in journal._spool_read()] == ["entry 3", "entry 4", "entry 5"]
    assert journal.spool_dropped() == 3


def test_spool_trim_drops_entries_past_the_age_cap(offline, monkeypatch):
    monkeypatch.setattr(journal, "SPOOL_MAX_AGE_DAYS", 7)
    monkeypatch.setattr(journal, "SPOOL_MAX_ENTRIES", 0)
    old = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    journal.remember("ancient", occurred_at=old)
    journal.remember("recent", occurred_at=datetime.now(timezone.utc).isoformat())

    assert journal._spool_trim() == 1
    assert [e["body"] for e in journal._spool_read()] == ["recent"]


def test_spool_trim_is_a_noop_under_the_caps(offline):
    journal.remember("well within limits")
    assert journal._spool_trim() == 0
    assert journal.spool_dropped() == 0


def test_oversize_spool_trims_on_append(offline, monkeypatch):
    """The cap has to fire on the write path, not only when someone asks."""
    monkeypatch.setattr(journal, "SPOOL_MAX_BYTES", 200)
    monkeypatch.setattr(journal, "SPOOL_MAX_ENTRIES", 2)
    monkeypatch.setattr(journal, "SPOOL_MAX_AGE_DAYS", 0)
    for i in range(10):
        journal.remember("entry %d" % i)  # must not raise

    assert len(journal._spool_read()) <= 2
    assert journal.spool_dropped() > 0


def test_dropped_tally_follows_a_redirected_spool(offline, tmp_path):
    assert journal._dropped_path().parent == tmp_path
    assert not (Path.home() / ".novasystem" / "journal_spool.dropped").exists()


def test_torn_spool_line_is_skipped(offline):
    journal.remember("good")
    with journal.SPOOL.open("a", encoding="utf-8") as fh:
        fh.write("{not json\n")
    assert len(journal.recall()) == 1


def test_pb_datetime_format():
    assert journal._pb_datetime("2026-07-26T23:11:31.123456+00:00") == \
        "2026-07-26 23:11:31.123Z"


def test_resolve_since_relative():
    assert journal._resolve_since("7d").endswith("+00:00")
    assert journal._resolve_since("2026-01-01") == "2026-01-01"
    assert journal._resolve_since("") == ""


# ── Feed mirror filtering ─────────────────────────────────────────────

def test_feed_mirror_skips_noisy_kinds(offline):
    journal.mirror_feed_event("Read", "some/file.py")
    journal.mirror_feed_event("Bash", "ls")
    assert journal.recall() == []


def test_feed_mirror_keeps_meaningful_kinds(offline):
    journal.mirror_feed_event("Edit", "novasystem/cli.py", sid="ab12")
    rows = journal.recall()
    assert len(rows) == 1
    assert rows[0]["kind"] == "event"
    assert rows[0]["session_id"] == "ab12"
    assert "coworking" in rows[0]["tags"]


def test_feed_kinds_wildcard(offline, monkeypatch):
    monkeypatch.setenv("NOVA_JOURNAL_FEED_KINDS", "*")
    journal.mirror_feed_event("Read", "x.py")
    assert len(journal.recall()) == 1


def test_feed_kinds_custom_list(offline, monkeypatch):
    monkeypatch.setenv("NOVA_JOURNAL_FEED_KINDS", "Bash")
    journal.mirror_feed_event("Bash", "pytest")
    journal.mirror_feed_event("Edit", "x.py")
    rows = journal.recall()
    assert len(rows) == 1 and "Bash" in rows[0]["tags"]


def test_feed_mirror_is_silent_when_disabled(offline):
    # `offline` pins reads to this test's own spool. Otherwise recall() would
    # answer from the live PocketBase and see every other test's entries.
    journal.disable()
    journal.mirror_feed_event("Edit", "x.py")  # must not raise
    assert journal.recall() == []


# ── Ledger integration ────────────────────────────────────────────────

def test_ledger_record_still_works_with_journal_off(tmp_path):
    from novasystem.persona.ledger import Decision, Ledger

    with Ledger(tmp_path / "ledger.db") as ledger:
        digest = ledger.record(Decision(
            subject="storage", choice="sqlite", rationale="single file",
            persona_id="p1",
        ))
        assert digest
        ok, err = ledger.verify_chain()
        assert ok, err


def test_ledger_mirror_writes_a_decision(tmp_path, offline):
    from novasystem.persona.ledger import Decision, Ledger

    with Ledger(tmp_path / "ledger.db") as ledger:
        ledger.record(Decision(
            subject="storage engine", choice="sqlite",
            rationale="one file, no server", persona_id="architect",
            reversibility="committal", confidence_at_decision=0.8,
        ))

    rows = journal.recall(kind="decision")
    assert len(rows) == 1
    assert rows[0]["title"] == "storage engine"
    assert "sqlite" in rows[0]["body"]
    assert rows[0]["metadata"]["row_hash"]
    assert rows[0]["actor"] == "architect"


def test_a_broken_journal_cannot_break_the_ledger(tmp_path, monkeypatch):
    """The whole point of the try/except around the mirror."""
    from novasystem.persona.ledger import Decision, Ledger

    journal.enable()
    monkeypatch.setattr(journal, "mirror_decision",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))

    with Ledger(tmp_path / "ledger.db") as ledger:
        digest = ledger.record(Decision(
            subject="s", choice="c", rationale="r", persona_id="p",
        ))
        assert digest
        ok, _ = ledger.verify_chain()
        assert ok


# ── Live PocketBase ───────────────────────────────────────────────────

def test_live_roundtrip(live):
    marker = "novatest-%s" % uuid.uuid4().hex[:12]
    entry = journal.remember("nova live check %s" % marker, kind="event",
                             tags=["pytest", marker])
    assert entry["_stored"] == "pocketbase"

    rows = journal.recall(marker)
    assert len(rows) == 1
    assert rows[0]["project"] == "NovaSystem"
    assert rows[0]["_source"] == "pocketbase"


def test_live_cross_project_view(live):
    """project=None is how NovaSystem sees what other projects wrote."""
    marker = "novatest-%s" % uuid.uuid4().hex[:12]
    journal.remember("cross project %s" % marker, kind="note")
    assert len(journal.recall(marker, project=None)) == 1
    assert len(journal.recall(marker, project="SimpleAgentOS")) == 0
