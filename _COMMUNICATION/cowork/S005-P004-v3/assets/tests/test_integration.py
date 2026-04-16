"""Integration tests for S002 config + runner."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import shaked_wg_agent.persistence as persistence_module
from shaked_wg_agent.config import DATA_DIR, load_config
from shaked_wg_agent.runner import run_scan


def test_load_config_real_data_basel_bbox() -> None:
    cfg = load_config("default")
    assert cfg.city.bounding_box.west == 7.5147
    assert cfg.profile.profile_id == "default"


@patch("shaked_wg_agent.runner._build_scraper")
def test_run_scan_adds_city_profile_ids(mock_build: MagicMock, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from shaked_wg_agent import config as config_module

    monkeypatch.setattr(config_module, "DATA_DIR", DATA_DIR)
    listings_path = tmp_path / "listings.json"
    runs_path = tmp_path / "runs.json"
    listings_path.write_text("[]", encoding="utf-8")
    runs_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(persistence_module, "LISTINGS_PATH", listings_path)
    monkeypatch.setattr(persistence_module, "RUNS_PATH", runs_path)

    scraper = MagicMock()
    scraper.fetch_listings.return_value = []
    mock_build.return_value = scraper

    rec = run_scan(profile_id="default")
    assert rec.get("city_id") == "basel"
    assert rec.get("profile_id") == "default"
    assert rec.get("triggered_by") == "manual"
