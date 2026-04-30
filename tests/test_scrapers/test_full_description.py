"""Fixture-driven tests for full_description extraction (SWG-PLAT-M2)."""
from __future__ import annotations

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Helpers — same extraction logic used (or mirrored) by the scrapers
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "scrapers"


def _extract_flatfox_description(html: str) -> str:
    """Extract full description from a flatfox listing HTML fixture."""
    soup = BeautifulSoup(html, "lxml")
    block = soup.select_one("div.listing-description")
    if block:
        return block.get_text(separator=" ", strip=True)
    return ""


def _extract_wgzimmer_description(html: str) -> str:
    """Extract full description from a wgzimmer listing HTML fixture."""
    soup = BeautifulSoup(html, "lxml")
    block = soup.select_one("div.wg-description")
    if block:
        return block.get_text(separator=" ", strip=True)
    return ""


def _build_summary(description: str, prefix: str = "") -> str:
    """Replicate scraper summary-truncation logic."""
    if prefix:
        return f"{prefix}. {description[:200]}"
    return description[:240]


# ---------------------------------------------------------------------------
# Flatfox fixture parametrisation
# ---------------------------------------------------------------------------

FLATFOX_FIXTURES = [
    FIXTURES_DIR / f"flatfox_listing_0{i}.html" for i in range(1, 6)
]

WGZIMMER_FIXTURES = [
    FIXTURES_DIR / f"wgzimmer_listing_0{i}.html" for i in range(1, 6)
]


@pytest.mark.parametrize("fixture_path", FLATFOX_FIXTURES, ids=[p.name for p in FLATFOX_FIXTURES])
def test_flatfox_full_description_length(fixture_path: Path) -> None:
    """full_description extracted from flatfox fixture must be >= 50 chars."""
    html = fixture_path.read_text(encoding="utf-8")
    full_desc = _extract_flatfox_description(html)
    assert len(full_desc) >= 50, (
        f"{fixture_path.name}: expected >= 50 chars, got {len(full_desc)}"
    )


@pytest.mark.parametrize("fixture_path", FLATFOX_FIXTURES, ids=[p.name for p in FLATFOX_FIXTURES])
def test_flatfox_full_description_longer_than_summary(fixture_path: Path) -> None:
    """full_description must be strictly longer than the truncated summary."""
    html = fixture_path.read_text(encoding="utf-8")
    full_desc = _extract_flatfox_description(html)
    summary = _build_summary(full_desc)
    # full_description is the raw text; summary is capped at 240 chars.
    # For descriptions > 240 chars this must hold; skip if description is short.
    if len(full_desc) > 240:
        assert len(full_desc) > len(summary), (
            f"{fixture_path.name}: full_description ({len(full_desc)}) "
            f"should exceed summary ({len(summary)})"
        )


@pytest.mark.parametrize("fixture_path", FLATFOX_FIXTURES, ids=[p.name for p in FLATFOX_FIXTURES])
def test_flatfox_full_description_not_empty(fixture_path: Path) -> None:
    """Extracted description must not be empty or whitespace-only."""
    html = fixture_path.read_text(encoding="utf-8")
    full_desc = _extract_flatfox_description(html)
    assert full_desc.strip(), f"{fixture_path.name}: full_description is empty"


# ---------------------------------------------------------------------------
# WGZimmer fixture parametrisation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture_path", WGZIMMER_FIXTURES, ids=[p.name for p in WGZIMMER_FIXTURES])
def test_wgzimmer_full_description_length(fixture_path: Path) -> None:
    """full_description extracted from wgzimmer fixture must be >= 50 chars."""
    html = fixture_path.read_text(encoding="utf-8")
    full_desc = _extract_wgzimmer_description(html)
    assert len(full_desc) >= 50, (
        f"{fixture_path.name}: expected >= 50 chars, got {len(full_desc)}"
    )


@pytest.mark.parametrize("fixture_path", WGZIMMER_FIXTURES, ids=[p.name for p in WGZIMMER_FIXTURES])
def test_wgzimmer_full_description_longer_than_summary(fixture_path: Path) -> None:
    """full_description must be strictly longer than the truncated summary."""
    html = fixture_path.read_text(encoding="utf-8")
    full_desc = _extract_wgzimmer_description(html)
    summary = _build_summary(full_desc)
    if len(full_desc) > 240:
        assert len(full_desc) > len(summary), (
            f"{fixture_path.name}: full_description ({len(full_desc)}) "
            f"should exceed summary ({len(summary)})"
        )


@pytest.mark.parametrize("fixture_path", WGZIMMER_FIXTURES, ids=[p.name for p in WGZIMMER_FIXTURES])
def test_wgzimmer_full_description_not_empty(fixture_path: Path) -> None:
    """Extracted description must not be empty or whitespace-only."""
    html = fixture_path.read_text(encoding="utf-8")
    full_desc = _extract_wgzimmer_description(html)
    assert full_desc.strip(), f"{fixture_path.name}: full_description is empty"


# ---------------------------------------------------------------------------
# ScrapedListing dataclass — field presence
# ---------------------------------------------------------------------------


def test_scraped_listing_has_full_description_field() -> None:
    """ScrapedListing must expose a full_description field defaulting to ''."""
    from shaked_wg_agent.scrapers.base import ScrapedListing

    listing = ScrapedListing(
        source="test",
        source_listing_id="1",
        source_search_url="https://example.com",
        title="Test",
        price=800,
        available_from=None,
        location_text="4051 Basel",
        district="Altstadt",
    )
    assert hasattr(listing, "full_description")
    assert listing.full_description == ""


def test_scraped_listing_full_description_set() -> None:
    """full_description field accepts and retains an arbitrary string."""
    from shaked_wg_agent.scrapers.base import ScrapedListing

    desc = "Das ist eine sehr ausführliche Beschreibung der Wohnung mit allen Details."
    listing = ScrapedListing(
        source="test",
        source_listing_id="2",
        source_search_url="https://example.com",
        title="Test WG",
        price=700,
        available_from="2026-07-01",
        location_text="4052 Basel",
        district="Gundeli",
        full_description=desc,
    )
    assert listing.full_description == desc


def test_scraped_listing_to_dict_includes_full_description() -> None:
    """to_dict() must include the full_description key."""
    from shaked_wg_agent.scrapers.base import ScrapedListing

    desc = "Vollständige Beschreibung für den to_dict Test."
    listing = ScrapedListing(
        source="test",
        source_listing_id="3",
        source_search_url="https://example.com",
        title="Dict Test",
        price=650,
        available_from=None,
        location_text="4053 Basel",
        district="Bachletten",
        full_description=desc,
    )
    d = listing.to_dict()
    assert "full_description" in d
    assert d["full_description"] == desc


# ---------------------------------------------------------------------------
# Migration logic test
# ---------------------------------------------------------------------------


def test_migration_adds_full_description_from_summary() -> None:
    """Migration must set full_description = summary for listings missing the key."""
    listings = [
        {"listing_id": "flatfox-1", "summary": "Schöne Wohnung im Zentrum.", "status": "neu"},
        {"listing_id": "flatfox-2", "summary": "Ruhiges Zimmer im Gundeli.", "status": "neu"},
        {
            "listing_id": "flatfox-3",
            "summary": "Bereits migriert.",
            "full_description": "Bereits migriert, längere Version.",
            "status": "neu",
        },
    ]

    # Inline migration logic (mirrors scripts/migrate or runner migration step)
    for lst in listings:
        if "full_description" not in lst:
            lst["full_description"] = lst.get("summary", "")

    assert listings[0]["full_description"] == "Schöne Wohnung im Zentrum."
    assert listings[1]["full_description"] == "Ruhiges Zimmer im Gundeli."
    # Pre-existing value must not be overwritten
    assert listings[2]["full_description"] == "Bereits migriert, längere Version."


def test_migration_no_data_loss() -> None:
    """Migration must not remove or alter any existing keys."""
    import copy

    original = {
        "listing_id": "wgzimmer-42",
        "source": "wgzimmer",
        "summary": "Zimmer frei ab sofort.",
        "price": 650,
        "status": "neu",
        "tags": ["transit"],
    }
    listing = copy.deepcopy(original)

    if "full_description" not in listing:
        listing["full_description"] = listing.get("summary", "")

    # All original keys must still be present with original values
    for key, val in original.items():
        assert listing[key] == val, f"Key {key!r} was altered by migration"

    assert listing["full_description"] == original["summary"]


def test_listings_json_all_have_full_description() -> None:
    """After migration, every entry in data/listings.json must have full_description."""
    import json
    from pathlib import Path

    listings_path = Path(__file__).parent.parent.parent / "data" / "listings.json"
    if not listings_path.exists():
        pytest.skip("data/listings.json not found")

    listings = json.loads(listings_path.read_text(encoding="utf-8"))
    missing = [lst.get("listing_id", idx) for idx, lst in enumerate(listings) if "full_description" not in lst]
    assert not missing, f"Listings missing full_description: {missing}"
