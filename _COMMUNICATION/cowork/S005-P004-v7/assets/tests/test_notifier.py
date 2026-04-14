"""Tests for notification digest builder and orchestrator."""
from __future__ import annotations

from shaked_wg_agent.notifier.digest_builder import build_digest_payload
from shaked_wg_agent.notifier.orchestrator import notify_digest


def test_build_digest_payload_filters_and_sorts() -> None:
    profile = {
        "profile_name": "P",
        "notifications": {"min_score_threshold": 50, "digest_max_listings": 2},
    }
    city = {"city_id": "basel", "city_name": "Basel"}
    run = {"run_id": "r1", "run_timestamp": "2026-04-12T10:00:00+00:00"}
    new = [
        {"title": "a", "relevance_score": 40, "direct_url": "http://x", "district": "d"},
        {"title": "b", "relevance_score": 80, "direct_url": "http://y", "district": "d"},
        {"title": "c", "relevance_score": 90, "direct_url": "http://z", "district": "d"},
    ]
    p = build_digest_payload(profile, city, run, new)
    assert p["total_new"] == 3
    assert len(p["listings"]) == 2
    assert p["listings"][0]["title"] == "c"


def test_notify_digest_no_notifications() -> None:
    assert notify_digest({"notifications": None}, {}, {}, [{"x": 1}]) is None


def test_notify_digest_empty_channels() -> None:
    assert notify_digest({"notifications": {"channels": []}}, {}, {}, [{"x": 1}]) is None
