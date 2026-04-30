# LOD400 — SWG-PLAT-M4 — Outreach lifecycle tracking
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M4
**Type:** LOD400_SPEC

---

## 1. New module: `shaked_wg_agent/outreach.py`

```python
"""Atomic lifecycle mutation helpers for outreach tracking (M4)."""
from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shaked_wg_agent.persistence import LISTINGS_PATH, load_listings, save_listings

# Statuses that indicate active outreach — never reset by scanner
OUTREACH_STATUSES: frozenset[str] = frozenset(
    {"contacted", "replied", "replied_negative", "viewed", "rejected"}
)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _find_listing(listings: list[dict[str, Any]], listing_id: str) -> int | None:
    """Return index of listing matching listing_id, or None."""
    for i, lst in enumerate(listings):
        if lst.get("listing_id") == listing_id:
            return i
    return None


def mark_contacted(listing_id: str, note: str | None = None) -> dict[str, Any]:
    """Set status='contacted', contacted_at=now. Returns updated listing."""
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
    """Set status='replied' or 'replied_negative', reply_received_at=now."""
    listings = load_listings()
    idx = _find_listing(listings, listing_id)
    if idx is None:
        raise KeyError(listing_id)
    listings[idx]["status"] = "replied" if positive else "replied_negative"
    listings[idx]["reply_received_at"] = _now_iso()
    save_listings(listings)
    return listings[idx]


def mark_viewed(listing_id: str, note: str | None = None) -> dict[str, Any]:
    """Set status='viewed'. Optionally record a note."""
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
    """Set status='rejected'. Optionally record rejection_reason."""
    listings = load_listings()
    idx = _find_listing(listings, listing_id)
    if idx is None:
        raise KeyError(listing_id)
    listings[idx]["status"] = "rejected"
    if reason:
        listings[idx]["rejection_reason"] = reason
    save_listings(listings)
    return listings[idx]
```

## 2. `shaked_wg_agent/__main__.py` additions

Four new subcommands appended to `main()`:

```python
# mark-contacted
p_mc = sub.add_parser("mark-contacted", help="mark listing as contacted")
p_mc.add_argument("listing_id", type=str)
p_mc.add_argument("--note", type=str, default=None)
p_mc.set_defaults(func=cmd_mark_contacted)

# mark-replied
p_mr = sub.add_parser("mark-replied", help="mark listing as replied")
p_mr.add_argument("listing_id", type=str)
grp = p_mr.add_mutually_exclusive_group()
grp.add_argument("--positive", dest="positive", action="store_true", default=True)
grp.add_argument("--negative", dest="positive", action="store_false")
p_mr.set_defaults(func=cmd_mark_replied)

# mark-viewed
p_mv = sub.add_parser("mark-viewed", help="mark listing as viewed in person")
p_mv.add_argument("listing_id", type=str)
p_mv.add_argument("--note", type=str, default=None)
p_mv.set_defaults(func=cmd_mark_viewed)

# mark-rejected
p_mrej = sub.add_parser("mark-rejected", help="remove listing from consideration")
p_mrej.add_argument("listing_id", type=str)
p_mrej.add_argument("--reason", type=str, default=None)
p_mrej.set_defaults(func=cmd_mark_rejected)
```

Each handler follows this pattern:

```python
def cmd_mark_contacted(args: argparse.Namespace) -> None:
    from shaked_wg_agent.outreach import mark_contacted
    try:
        mark_contacted(args.listing_id, note=args.note)
        console.print(f"Updated listing {args.listing_id}: status → contacted")
    except KeyError:
        console.print(f"[red]Listing not found: {args.listing_id}[/red]")
        raise SystemExit(1)
```

## 3. `shaked_wg_agent/scorer.py` — `score_all` filter

```python
_CLOSED_STATUSES: frozenset[str] = frozenset({"rejected", "replied_negative"})

def score_all(
    listings: list[dict[str, Any]],
    profile: SearchProfile,
    city: CityDefinition | None = None,
) -> list[dict[str, Any]]:
    """Re-score all listings in-place and return sorted (highest first).

    Listings with status 'rejected' or 'replied_negative' are excluded from
    the returned ranked list (they are not scored but remain in the input list).
    """
    active = [lst for lst in listings if lst.get("status") not in _CLOSED_STATUSES]
    closed = [lst for lst in listings if lst.get("status") in _CLOSED_STATUSES]
    for lst in active:
        lst["relevance_score"] = score_listing(lst, profile, city)
    ranked = sorted(active, key=lambda x: x.get("relevance_score", 0), reverse=True)
    return ranked + closed
```

## 4. `shaked_wg_agent/publisher/html_report.py` — status badge changes

Add to `_STATUS_BADGE_DE`:
```python
"contacted":       ("primary", "📤 Contacted"),
"replied":         ("success", "💬 Replied"),
"replied_negative": ("danger", "❌ Declined"),
"viewed":          ("warning", "👀 Viewed"),
"rejected":        ("secondary", "🚫 Removed"),
```

Add matching entries to `_STATUS_BADGE_HE`.

In `generate_report`: separate `visible_listings` into active vs closed:

```python
_CLOSED_STATUSES = frozenset({"rejected", "replied_negative"})

active_listings = [lst for lst in visible_listings if lst.get("status") not in _CLOSED_STATUSES]
closed_listings = [lst for lst in visible_listings if lst.get("status") in _CLOSED_STATUSES]
```

Render `closed_listings` in a separate "Closed" section with `opacity: 0.55`.

## 5. `tests/test_outreach_lifecycle.py`

Eight tests:

1. `test_mark_contacted_updates_status` — invoke `mark-contacted` CLI, assert status == "contacted"
2. `test_mark_replied_positive_updates_status` — invoke `mark-replied` (default positive), assert "replied"
3. `test_mark_replied_negative_updates_status` — invoke `mark-replied --negative`, assert "replied_negative"
4. `test_mark_rejected_updates_status` — invoke `mark-rejected`, assert "rejected"
5. `test_scan_preserves_contacted_status` — `upsert_listing` on existing listing keeps status "contacted"
6. `test_scan_does_not_resurrect_rejected` — same for "rejected"
7. `test_top5_excludes_rejected` — `score_all` result does not include rejected/replied_negative in top slots when eligible active listings exist
8. `test_mark_contacted_not_found_exits_1` — non-existent listing_id → `SystemExit(1)`
