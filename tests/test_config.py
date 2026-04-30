"""Tests for S002 three-entity configuration model."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from shaked_wg_agent import config as config_module
from shaked_wg_agent.config import (
    BoundingBox,
    ChannelConfig,
    CityDefinition,
    CitySourceParams,
    NotificationConfig,
    _load_agent_meta,
    _load_city,
    _load_profile,
    _load_sources,
    load_config,
)


@pytest.fixture()
def cfg_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(config_module, "DATA_DIR", tmp_path)
    (tmp_path / "cities").mkdir()
    (tmp_path / "profiles").mkdir()
    return tmp_path


def _write_agent(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "default_profile_id": "default",
                "manual_triggers_only": True,
                "project_window_days": 60,
                "project_start": "2026-04-09",
                "project_end": "2026-06-08",
            }
        ),
        encoding="utf-8",
    )


def _write_city_basel(path: Path) -> None:
    (path / "cities" / "basel.json").write_text(
        json.dumps(
            {
                "city_id": "basel",
                "city_name": "Basel",
                "country": "CH",
                "bounding_box": {
                    "west": 7.5147,
                    "east": 7.6559,
                    "south": 47.5176,
                    "north": 47.5956,
                },
                "zip_filter": ["4001"],
                "available_sources": ["flatfox"],
            }
        ),
        encoding="utf-8",
    )


def _write_profile_default(path: Path, **overrides: object) -> None:
    base = {
        "profile_id": "default",
        "profile_name": "Test",
        "city_id": "basel",
        "move_in_from": "2026-06-01",
        "budget_min": 200,
        "budget_max": 1000,
        "preferred_roommate_age": "young",
        "rental_duration": "permanent",
        "diet": "vegan",
        "smoking_policy": "non_smoking",
        "transit_lines": ["2", "3"],
        "custom_tags": [],
        "language_policy": {
            "primary_listing_language": "de",
            "translation_required": False,
            "preserve_source_text": True,
        },
        "retention_days": 30,
        "enabled_sources": [],
        "notifications": None,
    }
    base.update(overrides)
    (path / "profiles" / "default.json").write_text(json.dumps(base), encoding="utf-8")


def _write_sources_minimal(path: Path) -> None:
    sources = [
        {
            "source_id": "flatfox",
            "label": "flatfox.ch",
            "base_url": "https://flatfox.ch",
            "scraper_class": "FlatfoxScraper",
            "requires_playwright": False,
            "notes": "",
            "city_params": {
                "basel": {
                    "search_url": "https://flatfox.ch/de/search/?x=1",
                    "connection_method": "bbox",
                    "enabled": True,
                }
            },
        }
    ]
    (path / "sources.json").write_text(json.dumps(sources), encoding="utf-8")


def test_bounding_box() -> None:
    bb = BoundingBox(west=7.5147, east=7.6559, south=47.5176, north=47.5956)
    assert bb.west == 7.5147


def test_city_definition_defaults() -> None:
    c = CityDefinition(
        city_id="basel",
        city_name="Basel",
        bounding_box=BoundingBox(0, 1, 2, 3),
        available_sources=["a"],
    )
    assert c.country == "CH"
    assert c.zip_filter == []


def test_notification_config_validation() -> None:
    six = [
        ChannelConfig(type="email", enabled=True, params={"recipients": [f"{i}@e.com"]})
        for i in range(6)
    ]
    with pytest.raises(ValueError):
        NotificationConfig(digest_max_listings=5, min_score_threshold=0, channels=six)
    with pytest.raises(ValueError):
        NotificationConfig(digest_max_listings=0, min_score_threshold=0, channels=[])
    with pytest.raises(ValueError):
        NotificationConfig(digest_max_listings=5, min_score_threshold=101, channels=[])


def test_channel_config_invalid_type() -> None:
    with pytest.raises(ValueError):
        ChannelConfig(type="sms", enabled=True, params={})


def test_load_agent_meta_ok(cfg_root: Path) -> None:
    _write_agent(cfg_root / "agent.json")
    m = _load_agent_meta()
    assert m.default_profile_id == "default"


def test_load_agent_meta_missing(cfg_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _load_agent_meta()


def test_load_city_regex(cfg_root: Path) -> None:
    with pytest.raises(ValueError):
        _load_city("INVALID")


def test_load_profile_report_title_he(cfg_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config_module, "DATA_DIR", cfg_root)
    (cfg_root / "profiles").mkdir(parents=True, exist_ok=True)
    (cfg_root / "profiles" / "t-report-he.json").write_text(
        json.dumps(
            {
                "profile_id": "t-report-he",
                "profile_name": "Internal",
                "report_title_he": "כותרת עברית",
                "city_id": "basel",
                "move_in_from": "2026-06-01",
                "budget_min": 200,
                "budget_max": 1000,
                "preferred_roommate_age": "young",
                "rental_duration": "permanent",
                "diet": "vegan",
                "smoking_policy": "non_smoking",
                "transit_lines": [],
                "custom_tags": [],
                "language_policy": {},
                "retention_days": 30,
                "enabled_sources": ["flatfox"],
            }
        ),
        encoding="utf-8",
    )
    p = _load_profile("t-report-he")
    assert p.report_title_he == "כותרת עברית"


def test_load_city_infers_il_when_country_missing_and_currency_ils(
    cfg_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Older deployments may lack country on city JSON; ILS implies IL for report locale."""
    monkeypatch.setattr(config_module, "DATA_DIR", cfg_root)
    (cfg_root / "cities").mkdir(parents=True, exist_ok=True)
    (cfg_root / "cities" / "infer-il.json").write_text(
        json.dumps(
            {
                "city_id": "infer-il",
                "city_name": "Test",
                "bounding_box": {"west": 1, "east": 2, "south": 3, "north": 4},
                "available_sources": ["homeless"],
                "currency": "ILS",
            }
        ),
        encoding="utf-8",
    )
    c = _load_city("infer-il")
    assert c.country == "IL"
    assert c.currency == "ILS"


def test_load_city_settlement_allowlist(cfg_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config_module, "DATA_DIR", cfg_root)
    (cfg_root / "cities").mkdir(parents=True, exist_ok=True)
    (cfg_root / "cities" / "dror-test.json").write_text(
        json.dumps(
            {
                "city_id": "dror-test",
                "city_name": "Dror Test",
                "bounding_box": {"west": 1, "east": 2, "south": 3, "north": 4},
                "available_sources": ["homeless"],
                "filters": {"settlements": ["בנימינה", "חיפה"]},
            }
        ),
        encoding="utf-8",
    )
    city = _load_city("dror-test")
    assert city.settlement_allowlist == ["בנימינה", "חיפה"]


def test_load_profile_custom_tags_limit(cfg_root: Path) -> None:
    _write_profile_default(cfg_root, custom_tags=["a", "b", "c", "d"])
    with pytest.raises(ValueError):
        _load_profile("default")


def test_load_sources_parses_city_params(cfg_root: Path) -> None:
    _write_sources_minimal(cfg_root)
    srcs = _load_sources()
    assert isinstance(srcs[0].city_params["basel"], CitySourceParams)


def test_load_config_default(cfg_root: Path) -> None:
    _write_agent(cfg_root / "agent.json")
    _write_city_basel(cfg_root)
    _write_profile_default(cfg_root)
    _write_sources_minimal(cfg_root)
    pc = load_config("default")
    assert pc.profile.profile_id == "default"
    assert pc.city.city_id == "basel"
    assert len(pc.sources) >= 1


def test_load_config_none_uses_agent_default(cfg_root: Path) -> None:
    _write_agent(cfg_root / "agent.json")
    _write_city_basel(cfg_root)
    _write_profile_default(cfg_root)
    _write_sources_minimal(cfg_root)
    pc = load_config(None)
    assert pc.profile.profile_id == "default"


def test_load_config_missing_profile(cfg_root: Path) -> None:
    _write_agent(cfg_root / "agent.json")
    _write_city_basel(cfg_root)
    _write_sources_minimal(cfg_root)
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent")


def test_source_resolution_enabled_sources_filter(cfg_root: Path) -> None:
    _write_agent(cfg_root / "agent.json")
    _write_city_basel(cfg_root)
    _write_profile_default(cfg_root, enabled_sources=["flatfox"])
    _write_sources_minimal(cfg_root)
    pc = load_config("default")
    assert [s.source_id for s in pc.sources] == ["flatfox"]


def test_zero_sources_raises(cfg_root: Path) -> None:
    _write_agent(cfg_root / "agent.json")
    (cfg_root / "cities" / "basel.json").write_text(
        json.dumps(
            {
                "city_id": "basel",
                "city_name": "Basel",
                "bounding_box": {"west": 1, "east": 2, "south": 3, "north": 4},
                "available_sources": ["only-missing"],
            }
        ),
        encoding="utf-8",
    )
    _write_profile_default(cfg_root, enabled_sources=["only-missing"])
    (cfg_root / "sources.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="No active sources"):
        load_config("default")


def test_resolved_priority_order(cfg_root: Path) -> None:
    _write_agent(cfg_root / "agent.json")
    (cfg_root / "cities" / "basel.json").write_text(
        json.dumps(
            {
                "city_id": "basel",
                "city_name": "Basel",
                "bounding_box": {"west": 1, "east": 2, "south": 3, "north": 4},
                "available_sources": ["b", "a"],
            }
        ),
        encoding="utf-8",
    )
    _write_profile_default(cfg_root, enabled_sources=[])
    (cfg_root / "sources.json").write_text(
        json.dumps(
            [
                {
                    "source_id": "a",
                    "label": "A",
                    "base_url": "https://a",
                    "scraper_class": "X",
                    "city_params": {
                        "basel": {"search_url": "https://a/s", "enabled": True},
                    },
                },
                {
                    "source_id": "b",
                    "label": "B",
                    "base_url": "https://b",
                    "scraper_class": "X",
                    "city_params": {
                        "basel": {"search_url": "https://b/s", "enabled": True},
                    },
                },
            ]
        ),
        encoding="utf-8",
    )
    pc = load_config("default")
    ids = [s.source_id for s in pc.active_sources]
    assert ids == ["b", "a"]
    assert pc.sources[0].priority == 0
    assert pc.sources[1].priority == 1


def test_validation_rental_duration(cfg_root: Path) -> None:
    _write_profile_default(cfg_root, rental_duration="invalid")
    with pytest.raises(ValueError, match="rental_duration"):
        _load_profile("default")


def test_import_old_names_raise() -> None:
    with pytest.raises(ImportError):
        exec("from shaked_wg_agent.config import AgentConfig", {})
    with pytest.raises(ImportError):
        exec("from shaked_wg_agent.config import Source", {})


# ---------------------------------------------------------------------------
# M1: age / studies / move_in_optimal profile fields
# ---------------------------------------------------------------------------


def test_profile_age_field() -> None:
    """default.json must have age == 18 (Shaked's age)."""
    p = _load_profile("default")
    assert p.age == 18


def test_profile_age_null() -> None:
    """dror.json must have age == None (not applicable)."""
    p = _load_profile("dror")
    assert p.age is None


def test_profile_studies_fields() -> None:
    """default.json must have student occupation and correct institution."""
    p = _load_profile("default")
    assert p.occupation_status == "student"
    assert p.studies_institution == "Universität Basel"


def test_profile_move_in_optimal() -> None:
    """default.json must have move_in_optimal == '2026-06-01'."""
    p = _load_profile("default")
    assert p.move_in_optimal == "2026-06-01"
