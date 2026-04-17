"""JSON-backed persistence layer for listings and run records."""
from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"
LISTINGS_PATH = DATA_DIR / "listings.json"
RUNS_PATH = DATA_DIR / "runs.json"


# ---------------------------------------------------------------------------
# Listings
# ---------------------------------------------------------------------------

def load_listings() -> list[dict[str, Any]]:
    """Return all listings from data/listings.json."""
    if not LISTINGS_PATH.exists():
        return []
    return json.loads(LISTINGS_PATH.read_text(encoding="utf-8"))


def save_listings(listings: list[dict[str, Any]]) -> None:
    """Persist listings to data/listings.json (atomic overwrite)."""
    LISTINGS_PATH.write_text(
        json.dumps(listings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_listing(listing: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Insert or update a listing by listing_id.

    Returns (action, listing) where action is 'new', 'updated', or 'unchanged'.
    """
    listings = load_listings()
    now = datetime.now(UTC).isoformat(timespec="seconds")
    listing_id = listing.get("listing_id") or str(uuid.uuid4())
    listing["listing_id"] = listing_id

    for i, existing in enumerate(listings):
        if existing["listing_id"] == listing_id:
            changed = any(existing.get(k) != listing.get(k) for k in listing if k != "last_seen_at")
            listing["first_seen_at"] = existing.get("first_seen_at", now)
            listing["last_seen_at"] = now
            # Preserve user-editable fields — scraper must not reset manual edits
            for user_field in ("status", "note", "tags"):
                if user_field in existing:
                    listing[user_field] = existing[user_field]
            listings[i] = listing
            save_listings(listings)
            return ("updated" if changed else "unchanged"), listing

    listing.setdefault("first_seen_at", now)
    listing["last_seen_at"] = now
    listings.append(listing)
    save_listings(listings)
    return "new", listing


def mark_stale_listings(
    active_ids: set[str], retention_days: int, profile_id: str | None = None
) -> int:
    """Mark listings not seen in active_ids as stale if past retention window.

    Returns count of listings removed.
    """
    listings = load_listings()
    now = datetime.now(UTC)
    kept: list[dict[str, Any]] = []
    removed = 0

    for lst in listings:
        if profile_id is not None and lst.get("profile_id") != profile_id:
            kept.append(lst)
            continue
        if lst["listing_id"] in active_ids:
            kept.append(lst)
            continue
        last_seen_str = lst.get("last_seen_at", "")
        try:
            last_seen = datetime.fromisoformat(last_seen_str.replace("Z", "+00:00"))
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=UTC)
        except (ValueError, AttributeError):
            kept.append(lst)
            continue
        age_days = (now - last_seen).days
        if age_days > retention_days:
            removed += 1
        else:
            kept.append(lst)

    if removed:
        save_listings(kept)
    return removed


# ---------------------------------------------------------------------------
# Runs
# ---------------------------------------------------------------------------

def load_runs() -> list[dict[str, Any]]:
    """Return all run records from data/runs.json."""
    if not RUNS_PATH.exists():
        return []
    return json.loads(RUNS_PATH.read_text(encoding="utf-8"))


def save_runs(runs: list[dict[str, Any]]) -> None:
    """Persist runs to data/runs.json."""
    RUNS_PATH.write_text(
        json.dumps(runs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_run(run: dict[str, Any]) -> None:
    """Prepend a new run record (newest first)."""
    runs = load_runs()
    runs.insert(0, run)
    save_runs(runs)


def last_run() -> dict[str, Any] | None:
    """Return the most recent run record, or None."""
    runs = load_runs()
    return runs[0] if runs else None
