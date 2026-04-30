"""Atomic lifecycle mutation helpers for outreach tracking (M4)."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from shaked_wg_agent.persistence import load_listings, save_listings

# Statuses that indicate active outreach — must never be reset by scanner
OUTREACH_STATUSES: frozenset[str] = frozenset(
    {"contacted", "replied", "replied_negative", "viewed", "rejected"}
)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _find_listing(listings: list[dict[str, Any]], listing_id: str) -> int | None:
    """Return index of listing matching listing_id, or None if not found."""
    for i, lst in enumerate(listings):
        if lst.get("listing_id") == listing_id:
            return i
    return None


def mark_contacted(listing_id: str, note: str | None = None) -> dict[str, Any]:
    """Set status='contacted', contacted_at=now. Returns updated listing.

    Raises KeyError if listing_id is not found.
    """
    listings = load_listings()
    idx = _find_listing(listings, listing_id)
    if idx is None:
        raise KeyError(listing_id)
    listings[idx]["status"] = "contacted"
    listings[idx]["contacted_at"] = _now_iso()
    if note:
        listings[idx]["outreach_notes"] = note
    save_listings(listings)
    return listings[idx]


def mark_replied(listing_id: str, positive: bool = True) -> dict[str, Any]:
    """Set status='replied' or 'replied_negative', reply_received_at=now.

    Raises KeyError if listing_id is not found.
    """
    listings = load_listings()
    idx = _find_listing(listings, listing_id)
    if idx is None:
        raise KeyError(listing_id)
    listings[idx]["status"] = "replied" if positive else "replied_negative"
    listings[idx]["reply_received_at"] = _now_iso()
    save_listings(listings)
    return listings[idx]


def mark_viewed(listing_id: str, note: str | None = None) -> dict[str, Any]:
    """Set status='viewed'. Optionally record a note.

    Raises KeyError if listing_id is not found.
    """
    listings = load_listings()
    idx = _find_listing(listings, listing_id)
    if idx is None:
        raise KeyError(listing_id)
    listings[idx]["status"] = "viewed"
    if note:
        listings[idx]["outreach_notes"] = note
    save_listings(listings)
    return listings[idx]


def mark_rejected(listing_id: str, reason: str | None = None) -> dict[str, Any]:
    """Set status='rejected'. Optionally record rejection_reason.

    Raises KeyError if listing_id is not found.
    """
    listings = load_listings()
    idx = _find_listing(listings, listing_id)
    if idx is None:
        raise KeyError(listing_id)
    listings[idx]["status"] = "rejected"
    if reason:
        listings[idx]["rejection_reason"] = reason
    save_listings(listings)
    return listings[idx]
