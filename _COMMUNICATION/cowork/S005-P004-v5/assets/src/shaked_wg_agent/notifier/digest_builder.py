"""Build digest payload for notification channels."""
from __future__ import annotations

from typing import Any


def build_digest_payload(
    profile: dict[str, Any],
    city: dict[str, Any],
    run_record: dict[str, Any],
    new_listings: list[dict[str, Any]],
) -> dict[str, Any]:
    """Filter, sort, truncate new listings into a DigestPayload dict."""
    if not new_listings:
        raise ValueError("new_listings must not be empty")

    notif = profile.get("notifications") or {}
    min_score = int(notif.get("min_score_threshold", 0))
    max_n = int(notif.get("digest_max_listings", 5))

    total_new = len(new_listings)
    filtered = [
        row for row in new_listings if int(row.get("relevance_score", 0) or 0) >= min_score
    ]
    filtered.sort(key=lambda row: int(row.get("relevance_score", 0) or 0), reverse=True)
    top = filtered[:max_n]

    listings_summaries = [
        {
            "title": row.get("title", ""),
            "price_chf": row.get("price_chf"),
            "district": row.get("district", ""),
            "relevance_score": int(row.get("relevance_score", 0) or 0),
            "direct_url": row.get("direct_url", ""),
            "vegan_signal": row.get("vegan_signal") or "",
            "transit_match_lines": row.get("transit_match_lines")
            or row.get("tram_match_lines")
            or [],
        }
        for row in top
    ]

    scan_ts = run_record.get("run_timestamp") or run_record.get("timestamp") or ""

    return {
        "profile_name": profile.get("profile_name", ""),
        "city_id": city.get("city_id", ""),
        "city_name": city.get("city_name", ""),
        "run_id": run_record.get("run_id", ""),
        "scan_timestamp": scan_ts,
        "total_new": total_new,
        "listings": listings_summaries,
    }
