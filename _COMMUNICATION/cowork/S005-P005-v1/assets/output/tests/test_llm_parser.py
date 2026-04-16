"""Unit tests for llm_listing_parser module (UT-17 through UT-22)."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "output" / "src"))
sys.path.insert(0, str(_ROOT / "src"))

from shaked_wg_agent.parsers.llm_listing_parser import (
    _parse_response,
    check_llm_config,
    parse_rental_post,
)


# UT-17: check_llm_config() returns False with no env vars
@patch.dict(os.environ, {}, clear=True)
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "")
@patch("shaked_wg_agent.parsers.llm_listing_parser._ANTHROPIC_KEY", "")
@patch("shaked_wg_agent.parsers.llm_listing_parser._OPENAI_KEY", "")
def test_check_config_no_env():
    assert check_llm_config() is False


# UT-18: check_llm_config() returns True with claude config
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "claude")
@patch("shaked_wg_agent.parsers.llm_listing_parser._ANTHROPIC_KEY", "sk-ant-test-key")
def test_check_config_claude():
    assert check_llm_config() is True


# UT-19: check_llm_config() returns True with openai config
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "openai")
@patch("shaked_wg_agent.parsers.llm_listing_parser._OPENAI_KEY", "sk-test-key")
def test_check_config_openai():
    assert check_llm_config() is True


# UT-20: parse_rental_post() returns None when no config
@patch("shaked_wg_agent.parsers.llm_listing_parser._LLM_PROVIDER", "")
def test_parse_no_config_returns_none():
    result = parse_rental_post("some text", "group", "post1")
    assert result is None


# UT-21: _parse_response() with valid JSON returns dict
def test_parse_response_valid_json():
    result = _parse_response('{"is_rental_offer": true, "price_ils": 3500}')
    assert isinstance(result, dict)
    assert result["is_rental_offer"] is True
    assert result["price_ils"] == 3500


# UT-22: _parse_response() with invalid JSON returns None
def test_parse_response_invalid_json():
    result = _parse_response("not json at all {{{")
    assert result is None


def test_parse_response_non_dict():
    result = _parse_response("[1, 2, 3]")
    assert result is None
