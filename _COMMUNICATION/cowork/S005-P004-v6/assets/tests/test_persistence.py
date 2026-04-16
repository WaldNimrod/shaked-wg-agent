"""Unit tests for the JSON persistence layer."""
from __future__ import annotations

from pathlib import Path

import pytest

import shaked_wg_agent.persistence as persistence_module


@pytest.fixture(autouse=True)
def tmp_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Redirect all persistence operations to a temp directory."""
    (tmp_path / "listings.json").write_text("[]", encoding="utf-8")
    (tmp_path / "runs.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(persistence_module, "LISTINGS_PATH", tmp_path / "listings.json")
    monkeypatch.setattr(persistence_module, "RUNS_PATH", tmp_path / "runs.json")
    return tmp_path


# ---------------------------------------------------------------------------
# Listings persistence
# ---------------------------------------------------------------------------

def test_load_listings_empty() -> None:
    assert persistence_module.load_listings() == []


def test_upsert_listing_new() -> None:
    listing = {
        "listing_id": "test-001",
        "source": "wgzimmer",
        "title": "Test Zimmer",
        "price_chf": 700,
        "status": "neu",
    }
    action, saved = persistence_module.upsert_listing(listing)
    assert action == "new"
    assert saved["listing_id"] == "test-001"
    assert "first_seen_at" in saved
    assert "last_seen_at" in saved


def test_upsert_listing_duplicate_unchanged() -> None:
    listing = {"listing_id": "test-002", "title": "Same", "price_chf": 600}
    persistence_module.upsert_listing(listing)
    action, _ = persistence_module.upsert_listing(listing.copy())
    assert action == "unchanged"


def test_upsert_listing_updated() -> None:
    listing = {"listing_id": "test-003", "title": "Old Title", "price_chf": 600}
    persistence_module.upsert_listing(listing)
    updated = {"listing_id": "test-003", "title": "New Title", "price_chf": 650}
    action, saved = persistence_module.upsert_listing(updated)
    assert action == "updated"
    assert saved["title"] == "New Title"
    assert saved["price_chf"] == 650


def test_upsert_listing_generates_id_if_missing() -> None:
    listing = {"title": "No ID listing", "price_chf": 500}
    action, saved = persistence_module.upsert_listing(listing)
    assert action == "new"
    assert saved["listing_id"]  # ID was generated


def test_load_listings_returns_all() -> None:
    for i in range(3):
        persistence_module.upsert_listing({"listing_id": f"l-{i}", "title": f"Listing {i}"})
    assert len(persistence_module.load_listings()) == 3


def test_save_and_reload_listings() -> None:
    listings = [{"listing_id": "x", "title": "X", "price_chf": 800}]
    persistence_module.save_listings(listings)
    reloaded = persistence_module.load_listings()
    assert reloaded[0]["listing_id"] == "x"


# ---------------------------------------------------------------------------
# Stale listing removal
# ---------------------------------------------------------------------------

def test_mark_stale_removes_old_listings(tmp_path: Path) -> None:
    old_listing = {
        "listing_id": "old-001",
        "title": "Old",
        "last_seen_at": "2020-01-01T00:00:00",
    }
    new_listing = {
        "listing_id": "new-001",
        "title": "New",
        "last_seen_at": "2026-04-09T09:00:00",
    }
    persistence_module.save_listings([old_listing, new_listing])
    removed = persistence_module.mark_stale_listings({"new-001"}, retention_days=30)
    assert removed == 1
    remaining = persistence_module.load_listings()
    assert len(remaining) == 1
    assert remaining[0]["listing_id"] == "new-001"


def test_mark_stale_keeps_active_listings() -> None:
    listing = {
        "listing_id": "active-001",
        "title": "Active",
        "last_seen_at": "2020-01-01T00:00:00",  # old but in active_ids
    }
    persistence_module.save_listings([listing])
    removed = persistence_module.mark_stale_listings({"active-001"}, retention_days=30)
    assert removed == 0


# ---------------------------------------------------------------------------
# Run records
# ---------------------------------------------------------------------------

def test_load_runs_empty() -> None:
    assert persistence_module.load_runs() == []


def test_append_run_and_reload() -> None:
    run = {"run_id": "run-001", "run_timestamp": "2026-04-09T09:00:00", "new_results": 4}
    persistence_module.append_run(run)
    runs = persistence_module.load_runs()
    assert len(runs) == 1
    assert runs[0]["run_id"] == "run-001"


def test_append_run_newest_first() -> None:
    persistence_module.append_run({"run_id": "run-001"})
    persistence_module.append_run({"run_id": "run-002"})
    runs = persistence_module.load_runs()
    assert runs[0]["run_id"] == "run-002"
    assert runs[1]["run_id"] == "run-001"


def test_last_run_returns_most_recent() -> None:
    persistence_module.append_run({"run_id": "run-001"})
    persistence_module.append_run({"run_id": "run-002"})
    assert persistence_module.last_run()["run_id"] == "run-002"


def test_last_run_none_when_empty() -> None:
    assert persistence_module.last_run() is None
