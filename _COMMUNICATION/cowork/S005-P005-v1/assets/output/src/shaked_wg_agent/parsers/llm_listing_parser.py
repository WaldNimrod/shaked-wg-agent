"""LLM-based rental listing parser — extracts structured fields from Hebrew text.

Supports Claude (Anthropic) and OpenAI providers.
Provider is selected via SHAKED_LLM_PROVIDER env var ("claude" or "openai").
API keys via ANTHROPIC_API_KEY / OPENAI_API_KEY env vars.

Never raises — returns None on any failure.
"""
from __future__ import annotations

import json
import logging
import os
import time

logger = logging.getLogger(__name__)

_LLM_PROVIDER = os.environ.get("SHAKED_LLM_PROVIDER", "")
_ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
_OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

_SYSTEM_PROMPT = """You are a Hebrew rental listing parser. Extract structured data from Hebrew rental posts.

Return a JSON object with these fields:
- is_rental_offer: bool (true if this is a rental offer, false if it's a request, question, or off-topic)
- price_ils: int or null (monthly rent in ILS/shekels)
- rooms: float or null (number of rooms, e.g. 3.5)
- city: str (city name in Hebrew or transliterated)
- neighborhood: str (neighborhood/area name)
- street: str (street name if mentioned)
- available_from: str or null (ISO 8601 date if mentioned, e.g. "2026-06-01")
- property_type: str (one of: apartment, room, unit, villa, studio)
- floor: int or null
- area_sqm: int or null (area in square meters)
- key_features: list of str (e.g. parking, elevator, balcony, pets, furnished, air conditioning)
- contact_method: str (one of: phone, whatsapp, dm, comments)

If the post is NOT a rental offer (e.g., it's a request, question, or off-topic), set is_rental_offer to false and leave other fields null/empty.

Return ONLY valid JSON, no markdown formatting."""


def _format_user_prompt(text: str, group_name: str) -> str:
    """Format the user prompt for LLM extraction."""
    parts = [f"Parse this rental post from Facebook group"]
    if group_name:
        parts[0] += f' "{group_name}"'
    parts.append(f":\n\n{text}")
    return "".join(parts)


def check_llm_config() -> bool:
    """Return True if LLM provider and API key are configured."""
    if _LLM_PROVIDER == "claude" and _ANTHROPIC_KEY:
        return True
    if _LLM_PROVIDER == "openai" and _OPENAI_KEY:
        return True
    return False


def _call_claude(text: str, group_name: str) -> dict | None:
    """Call Claude API for extraction."""
    import anthropic

    client = anthropic.Anthropic(api_key=_ANTHROPIC_KEY)
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _format_user_prompt(text, group_name)}],
    )
    return _parse_response(response.content[0].text)


def _call_openai(text: str, group_name: str) -> dict | None:
    """Call OpenAI API for extraction."""
    import openai

    client = openai.OpenAI(api_key=_OPENAI_KEY)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _format_user_prompt(text, group_name)},
        ],
        response_format={"type": "json_object"},
    )
    return _parse_response(response.choices[0].message.content)


def _parse_response(raw: str) -> dict | None:
    """Parse LLM JSON response. Return dict or None on failure."""
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, TypeError):
        logger.warning("LLM returned malformed JSON: %.200s", raw)
        return None


def parse_rental_post(text: str, group_name: str = "", post_id: str = "") -> dict | None:
    """Parse a Hebrew rental post into structured fields using an LLM.

    Args:
        text: The raw Hebrew post text.
        group_name: Facebook group name (for LLM context).
        post_id: Post identifier (for error logging context).

    Returns a dict with extraction results, or None if parsing fails.
    NEVER raises an exception.
    """
    # MODE 1: No provider configured (run-level)
    if not _LLM_PROVIDER:
        return None

    # MODE 2: No API key configured (run-level)
    if _LLM_PROVIDER == "claude" and not _ANTHROPIC_KEY:
        return None
    if _LLM_PROVIDER == "openai" and not _OPENAI_KEY:
        return None

    call_fn = _call_claude if _LLM_PROVIDER == "claude" else _call_openai

    try:
        return call_fn(text, group_name)

    except Exception as e:
        err_str = str(e).lower()

        # MODE 4: API rate limit (429) — post-level, retry once
        if "rate_limit" in err_str or "429" in err_str or "rate limit" in err_str:
            logger.warning("LLM rate-limited for post %s, retrying in 2s", post_id)
            time.sleep(2)
            try:
                return call_fn(text, group_name)
            except Exception:
                logger.warning("LLM rate-limited after retry, skipping post %s", post_id)
                return None

        # MODE 3: API timeout — post-level, skip
        if "timeout" in err_str or "timed out" in err_str:
            logger.warning("LLM timeout for post %s, skipping", post_id)
            return None

        # MODE 6: API error (500, network) — post-level, skip
        logger.error("LLM API error for post %s: %s", post_id, e)
        return None
