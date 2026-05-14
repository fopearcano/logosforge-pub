"""AI router smoke tests using the dry-run provider."""
from __future__ import annotations

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Author, Manuscript
from app.models.enums import WorkflowStatus


def _seed_manuscript(session: Session) -> str:
    a = Author(full_name="Iris Aldoria")
    session.add(a)
    session.commit()
    session.refresh(a)
    m = Manuscript(
        title="The Salt Atlases",
        synopsis="Twelve essays on inland seas.",
        author_id=a.id,
        status=WorkflowStatus.PUBLISHED,
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    return m.id


def test_providers_endpoint_reports_dry_run_default(
    anon_client: TestClient,
) -> None:
    body = anon_client.get("/api/ai/providers").json()
    assert body["active"]["provider"] == "dry_run"
    assert body["active"]["is_live"] is False
    assert "openai" in body["known"]
    assert "lm_studio" in body["known"]
    assert "openrouter" in body["known"]


def test_summarize_endpoint_returns_typed_result(
    client: TestClient, session: Session
) -> None:
    mid = _seed_manuscript(session)
    r = client.post(f"/api/ai/manuscripts/{mid}/summarize")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["feature"] == "summarize"
    assert body["provider"] == "dry_run"
    assert "summary" in body["result"]
    assert "themes" in body["result"]
    assert body["insight_id"]


def test_each_feature_endpoint_persists_an_insight(
    client: TestClient, session: Session
) -> None:
    mid = _seed_manuscript(session)
    endpoints = [
        ("summarize", "summarize"),
        ("style-analysis", "style_analysis"),
        ("editorial-suggestions", "editorial_suggestions"),
        ("semantic-tags", "semantic_tags"),
        ("consistency-check", "consistency_check"),
    ]
    insight_ids = set()
    for path_suffix, feature_value in endpoints:
        r = client.post(f"/api/ai/manuscripts/{mid}/{path_suffix}")
        assert r.status_code == 200, (path_suffix, r.text)
        body = r.json()
        assert body["feature"] == feature_value
        insight_ids.add(body["insight_id"])

    listed = client.get(f"/api/ai/manuscripts/{mid}/insights").json()
    assert len(listed) == 5
    assert {i["id"] for i in listed} == insight_ids


def test_insights_endpoint_filters_by_feature(
    client: TestClient, session: Session
) -> None:
    mid = _seed_manuscript(session)
    client.post(f"/api/ai/manuscripts/{mid}/summarize")
    client.post(f"/api/ai/manuscripts/{mid}/semantic-tags")

    summarize_only = client.get(
        f"/api/ai/manuscripts/{mid}/insights?feature=summarize"
    ).json()
    assert len(summarize_only) == 1
    assert summarize_only[0]["feature"] == "summarize"
    assert summarize_only[0]["payload"]  # parsed back into a dict


def test_feature_endpoints_require_auth(
    anon_client: TestClient, session: Session
) -> None:
    mid = _seed_manuscript(session)
    r = anon_client.post(f"/api/ai/manuscripts/{mid}/summarize")
    assert r.status_code == 401


def test_feature_endpoints_404_when_manuscript_missing(
    client: TestClient,
) -> None:
    r = client.post("/api/ai/manuscripts/no-such/summarize")
    assert r.status_code == 404


def test_insight_can_be_deleted(client: TestClient, session: Session) -> None:
    mid = _seed_manuscript(session)
    body = client.post(f"/api/ai/manuscripts/{mid}/summarize").json()
    iid = body["insight_id"]
    r = client.delete(f"/api/ai/insights/{iid}")
    assert r.status_code == 204
    after = client.get(f"/api/ai/manuscripts/{mid}/insights").json()
    assert after == []


def test_insights_404_when_manuscript_missing(
    anon_client: TestClient,
) -> None:
    r = anon_client.get("/api/ai/manuscripts/no-such/insights")
    assert r.status_code == 404
