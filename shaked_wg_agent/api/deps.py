"""Shared helpers for API routes."""
from __future__ import annotations

import json

from shaked_wg_agent.config import DATA_DIR


def resolve_profile_id(profile_id: str | None, city_id: str | None) -> str | None:
    """Resolve effective profile_id (profile wins over deprecated city_id)."""
    if profile_id is not None:
        return profile_id
    if city_id is None:
        return None
    profiles_dir = DATA_DIR / "profiles"
    if not profiles_dir.is_dir():
        return None
    for path in sorted(profiles_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("city_id") == city_id:
            return str(raw["profile_id"])
    return None
