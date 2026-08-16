"""Tests for the FastAPI layer.

The important one is test_survives_the_threadpool. FastAPI runs `def` endpoints
in an anyio worker threadpool, and a shared sqlite3 connection raises
ProgrammingError across threads. That bug does not show up in a single request,
so it needs an explicit test.
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from novasystem.persona import api as api_module  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv(api_module.DB_ENV_VAR, str(tmp_path / "api.db"))
    with TestClient(api_module.create_app()) as c:
        yield c


def payload(**kw):
    base = dict(
        subject="storage-engine",
        choice="sqlite",
        rationale="embedded, no server to run, fits a single-user CLI workload",
        persona_id="dce",
    )
    base.update(kw)
    return base


# ---------------------------------------------------------------- lifecycle

def test_personas_are_bootstrapped_on_startup(client):
    r = client.get("/personas")
    assert r.status_code == 200
    ids = {p["persona_id"] for p in r.json()}
    assert {"dce", "cae"} <= ids


def test_persona_history_endpoint(client):
    r = client.get("/personas/dce/history")
    assert r.status_code == 200
    assert r.json()[0]["version"] == 1


def test_unknown_persona_404s(client):
    assert client.get("/personas/nope").status_code == 404


# ---------------------------------------------------------------- decisions

def test_first_decision_is_recorded(client):
    r = client.post("/decisions", json=payload())
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["recorded"] is True
    assert body["assessment"]["status"] == "novel"
    assert body["row_hash"]


def test_contradiction_is_rejected_with_409_and_explains_itself(client):
    client.post("/decisions", json=payload(choice="sqlite"))
    r = client.post("/decisions", json=payload(choice="postgres"))
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert detail["recorded"] is False
    assert detail["assessment"]["status"] == "contradicts"
    assert detail["assessment"]["must_supersede"]
    # and nothing was written
    assert len(client.get("/decisions").json()) == 1


def test_supersede_with_citation_is_accepted(client):
    first = client.post("/decisions", json=payload(choice="sqlite")).json()
    fid = first["decision_id"]
    r = client.post("/decisions", json=payload(
        choice="postgres", supersedes=fid, evidence_refs=[fid],
        rationale="outgrew the single-writer model once workers went above one",
    ))
    assert r.status_code == 201, r.text
    assert r.json()["assessment"]["status"] == "consistent"
    assert len(client.get("/decisions").json()) == 2


def test_force_records_and_still_reports_blocked(client):
    client.post("/decisions", json=payload(choice="sqlite"))
    r = client.post("/decisions?force=true", json=payload(choice="postgres"))
    assert r.status_code == 201
    assert r.json()["assessment"]["blocked"] is True


def test_invalid_payload_is_422(client):
    assert client.post("/decisions", json=payload(confidence_at_decision=5)
                       ).status_code == 422
    assert client.post("/decisions", json=payload(subject="")).status_code == 422


def test_bad_reversibility_is_400_not_500(client):
    r = client.post("/decisions", json=payload(reversibility="whenever"))
    assert r.status_code == 400


def test_supersede_unknown_id_is_400_not_500(client):
    r = client.post("/decisions", json=payload(supersedes="dec-nope"))
    assert r.status_code == 400


def test_get_and_list_decisions(client):
    did = client.post("/decisions", json=payload()).json()["decision_id"]
    assert client.get(f"/decisions/{did}").json()["choice"] == "sqlite"
    assert client.get("/decisions/dec-missing").status_code == 404
    assert len(client.get("/decisions", params={"persona_id": "dce"}).json()) == 1
    assert client.get("/decisions", params={"persona_id": "cae"}).json() == []


def test_precedent_query_does_not_write(client):
    client.post("/decisions", json=payload(choice="sqlite"))
    r = client.get("/subjects/storage-engine/precedent",
                   params={"choice": "postgres"})
    assert r.status_code == 200
    assert r.json()["status"] == "contradicts"
    assert len(client.get("/decisions").json()) == 1, "a query must not record"


# ---------------------------------------------------------------- integrity

def test_integrity_endpoint_reports_intact(client):
    client.post("/decisions", json=payload())
    r = client.get("/integrity").json()
    assert r["intact"] is True
    assert r["decisions"] == 1


# --------------------------------------------------------------- threadpool

def test_survives_the_threadpool(client):
    """The regression guard for the shared-connection bug.

    A single ledger held on app.state raises:
        ProgrammingError: SQLite objects created in a thread can only be used
        in that same thread.
    Sequential requests happen to reuse a thread often enough to hide it, so
    this drives concurrent requests to force the threadpool to spread.
    """
    # Genuinely unrelated subjects. Using "subject-0", "subject-1", ... would
    # collide in the relatedness check, since the numeric suffixes are dropped as
    # too short and every subject reduces to the same token.
    topics = [
        "cache eviction policy", "retry backoff strategy", "log retention window",
        "image thumbnail sizing", "session cookie lifetime", "queue worker count",
        "backup schedule cadence", "search index refresh", "rate limit ceiling",
        "timezone normalisation", "email bounce handling", "avatar upload limit",
        "webhook signing scheme", "pagination page size", "audit trail depth",
        "feature flag rollout", "password hash cost", "cdn purge trigger",
        "metric scrape interval", "error budget threshold", "locale fallback order",
        "invoice numbering rule", "export file format", "onboarding step order",
    ]

    def post(i: int):
        return client.post("/decisions", json=payload(
            subject=topics[i], choice=f"option-{i}",
            rationale=(
                "each request uses an unrelated subject, so nothing here "
                "contradicts and the only thing under test is the threadpool"
            ),
        )).status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(post, range(24)))

    assert all(c == 201 for c in codes), f"threadpool failures: {codes}"
    assert len(client.get("/decisions").json()) == 24
    assert client.get("/integrity").json()["intact"] is True
