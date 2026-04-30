"""Tests for M4 outreach lifecycle tracking."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from shaked_wg_agent.config import LanguagePolicy, SearchProfile
from shaked_wg_agent.outreach import mark_contacted, mark_rejected, mark_replied
from shaked_wg_agent.scorer import score_all

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_listing(listing_id: str, status: str = "neu", score: int = 50) -> dict[str, Any]:
    return {
        "listing_id": listing_id,
        "source": "test",
        "status": status,
        "relevance_score": score,
        "price": 700,
        "vegan_signal": "vegan",
        "transit_match_lines": ["2"],
        "roommate_signal": "",
        "url_status": "direct",
    }


@pytest.fixture()
def tmp_listings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect LISTINGS_PATH to a temp file and return the path."""
    import shaked_wg_agent.outreach as outreach_mod
    import shaked_wg_agent.persistence as persistence_mod

    listings_file = tmp_path / "listings.json"
    listings_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(persistence_mod, "LISTINGS_PATH", listings_file)
    monkeypatch.setattr(outreach_mod, "load_listings", persistence_mod.load_listings)
    monkeypatch.setattr(outreach_mod, "save_listings", persistence_mod.save_listings)

    return listings_file


@pytest.fixture()
def base_profile() -> SearchProfile:
    return SearchProfile(
        profile_id="test",
        profile_name="Test",
        city_id="basel",
        move_in_from="2026-06-01",
        budget_min=200,
        budget_max=1000,
        preferred_roommate_age="young",
        rental_duration="permanent",
        diet="",
        smoking_policy="",
        transit_lines=["2", "3"],
        custom_tags=[],
        language_policy=LanguagePolicy(),
        retention_days=30,
        enabled_sources=[],
        notifications=None,
    )


# ---------------------------------------------------------------------------
# 1. mark_contacted updates status
# ---------------------------------------------------------------------------


def test_mark_contacted_updates_status(tmp_listings: Path) -> None:
    import shaked_wg_agent.persistence as persistence_mod

    lst = _make_listing("lst-001")
    persistence_mod.save_listings([lst])

    updated = mark_contacted("lst-001", note="sent via flatfox")

    assert updated["status"] == "contacted"
    assert updated.get("contacted_at") is not None
    assert updated.get("outreach_notes") == "sent via flatfox"

    # Verify persisted
    all_listings = persistence_mod.load_listings()
    saved = next(x for x in all_listings if x["listing_id"] == "lst-001")
    assert saved["status"] == "contacted"


# ---------------------------------------------------------------------------
# 2. mark_replied positive
# ---------------------------------------------------------------------------


def test_mark_replied_positive_updates_status(tmp_listings: Path) -> None:
    import shaked_wg_agent.persistence as persistence_mod

    lst = _make_listing("lst-002")
    persistence_mod.save_listings([lst])

    updated = mark_replied("lst-002", positive=True)

    assert updated["status"] == "replied"
    assert updated.get("reply_received_at") is not None


# ---------------------------------------------------------------------------
# 3. mark_replied negative
# ---------------------------------------------------------------------------


def test_mark_replied_negative_updates_status(tmp_listings: Path) -> None:
    import shaked_wg_agent.persistence as persistence_mod

    lst = _make_listing("lst-003")
    persistence_mod.save_listings([lst])

    updated = mark_replied("lst-003", positive=False)

    assert updated["status"] == "replied_negative"
    assert updated.get("reply_received_at") is not None


# ---------------------------------------------------------------------------
# 4. mark_rejected updates status
# ---------------------------------------------------------------------------


def test_mark_rejected_updates_status(tmp_listings: Path) -> None:
    import shaked_wg_agent.persistence as persistence_mod

    lst = _make_listing("lst-004")
    persistence_mod.save_listings([lst])

    updated = mark_rejected("lst-004", reason="too far from city centre")

    assert updated["status"] == "rejected"
    assert updated.get("rejection_reason") == "too far from city centre"


# ---------------------------------------------------------------------------
# 5. scan preserves contacted status (upsert_listing keeps status)
# ---------------------------------------------------------------------------


def test_scan_preserves_contacted_status(tmp_listings: Path) -> None:
    import shaked_wg_agent.persistence as persistence_mod

    lst = _make_listing("lst-005", status="contacted")
    persistence_mod.save_listings([lst])

    # Simulate scanner upserting same listing with status="neu"
    incoming = _make_listing("lst-005", status="neu")
    persistence_mod.upsert_listing(incoming)

    all_listings = persistence_mod.load_listings()
    saved = next(x for x in all_listings if x["listing_id"] == "lst-005")
    assert saved["status"] == "contacted", "upsert_listing must preserve existing status"


# ---------------------------------------------------------------------------
# 6. scan does not resurrect rejected status
# ---------------------------------------------------------------------------


def test_scan_does_not_resurrect_rejected(tmp_listings: Path) -> None:
    import shaked_wg_agent.persistence as persistence_mod

    lst = _make_listing("lst-006", status="rejected")
    persistence_mod.save_listings([lst])

    incoming = _make_listing("lst-006", status="neu")
    persistence_mod.upsert_listing(incoming)

    all_listings = persistence_mod.load_listings()
    saved = next(x for x in all_listings if x["listing_id"] == "lst-006")
    assert saved["status"] == "rejected", "upsert_listing must preserve rejected status"


# ---------------------------------------------------------------------------
# 7. score_all excludes rejected and replied_negative from top results
# ---------------------------------------------------------------------------


def test_top5_excludes_rejected(base_profile: SearchProfile) -> None:
    # Create one high-score active listing and two closed ones with even higher stored scores
    listings = [
        _make_listing("active-1", status="neu", score=80),
        _make_listing("rejected-1", status="rejected", score=99),
        _make_listing("declined-1", status="replied_negative", score=95),
    ]

    ranked = score_all(listings, base_profile)

    # Active listing should appear first
    active_ids = [
        x["listing_id"]
        for x in ranked
        if x.get("status") not in ("rejected", "replied_negative")
    ]

    assert "active-1" in active_ids
    # Closed listings must not appear before active listings in the ranked slice
    first_closed_pos = next(
        (i for i, x in enumerate(ranked) if x["listing_id"] in ("rejected-1", "declined-1")),
        len(ranked),
    )
    first_active_pos = next(
        (i for i, x in enumerate(ranked) if x["listing_id"] == "active-1"),
        len(ranked),
    )
    assert first_active_pos < first_closed_pos, (
        "Active listing should rank before closed listings"
    )


# ---------------------------------------------------------------------------
# 8. mark_contacted with non-existent listing_id → KeyError
# ---------------------------------------------------------------------------


def test_mark_contacted_not_found_exits_1(tmp_listings: Path) -> None:
    import shaked_wg_agent.persistence as persistence_mod

    persistence_mod.save_listings([])

    with pytest.raises(KeyError):
        mark_contacted("does-not-exist")
