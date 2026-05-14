"""Request-id middleware behaviour."""
from __future__ import annotations

import re

from fastapi.testclient import TestClient

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def test_request_id_header_minted_when_absent(anon_client: TestClient) -> None:
    r = anon_client.get("/api/health")
    rid = r.headers.get("X-Request-ID")
    assert rid is not None
    assert UUID_RE.match(rid)


def test_request_id_passthrough_when_supplied(anon_client: TestClient) -> None:
    r = anon_client.get(
        "/api/health", headers={"X-Request-ID": "external-correlation-1"}
    )
    assert r.headers["X-Request-ID"] == "external-correlation-1"


def test_request_id_present_on_404(anon_client: TestClient) -> None:
    r = anon_client.get("/api/manuscripts/no-such-id")
    assert r.status_code == 404
    assert "X-Request-ID" in r.headers


def test_request_id_present_on_422(anon_client: TestClient) -> None:
    r = anon_client.get("/api/authors?limit=0")
    assert r.status_code == 422
    assert "X-Request-ID" in r.headers
