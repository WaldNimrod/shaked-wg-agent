"""Tests for FastAPI REST layer."""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from shaked_wg_agent.api import create_app


@pytest.fixture()
def api_key(monkeypatch: pytest.MonkeyPatch) -> str:
    key = "k" * 32
    monkeypatch.setenv("API_KEY", key)
    return key


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, api_key: str) -> TestClient:
    return TestClient(create_app())


def test_health_no_auth(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.3.0"
    assert "auth_configured" in data
    assert r.headers.get("X-Request-ID", "").startswith("req-")


def test_listings_500_when_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("API_KEY", raising=False)
    c = TestClient(create_app())
    r = c.get("/listings?city_id=basel")
    assert r.status_code == 500


def test_listings_200_with_key(client: TestClient, api_key: str) -> None:
    r = client.get(
        "/listings?city_id=basel",
        headers={"X-API-Key": api_key},
    )
    assert r.status_code == 200
    body = r.json()
    assert "data" in body and "meta" in body


def test_search_mock_run(client: TestClient, api_key: str) -> None:
    fake_run = {
        "run_id": "run-test",
        "run_timestamp": "2026-04-12T12:00:00+00:00",
        "triggered_by": "api",
        "city_id": "basel",
        "profile_id": "default",
        "sources_scanned": 0,
        "results_scanned": 0,
        "new_results": 0,
        "updated_results": 0,
        "stale_removed": 0,
        "duration_seconds": 0,
        "errors": [],
        "report_url": None,
        "operator_notes": "",
        "notification_sent": None,
    }
    with patch("shaked_wg_agent.api.routes.run_scan", return_value=fake_run):
        r = client.post(
            "/search",
            json={"profile_id": "default"},
            headers={"X-API-Key": api_key},
        )
    assert r.status_code == 200
    assert r.json()["data"]["triggered_by"] == "api"


def test_unauthorized_body_matches(client: TestClient, api_key: str) -> None:
    r = client.get(
        "/listings?city_id=basel",
        headers={"X-API-Key": "wrong" * 8},
    )
    assert r.status_code == 401
    assert r.json() == {
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Missing or invalid API key",
            "detail": None,
        }
    }
