"""Load and validate project configuration from data/config.json and data/sources.json."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


@dataclass
class LanguagePolicy:
    primary_listing_language: str = "de"
    translation_required: bool = False
    preserve_source_text: bool = True


@dataclass
class AgentConfig:
    profile_name: str
    target_city: str
    move_in_from: str
    budget_min_chf: int
    budget_max_chf: int
    preferred_roommate_age: str
    diet: str
    tram_lines: list[str]
    language_policy: LanguagePolicy
    retention_days: int
    project_window_days: int
    project_start: str
    project_end: str
    manual_triggers_only: bool


@dataclass
class Source:
    id: str
    label: str
    base_url: str
    search_url: str
    enabled: bool
    priority: int
    notes: str = ""


@dataclass
class ProjectConfig:
    agent: AgentConfig
    sources: list[Source] = field(default_factory=list)

    @property
    def active_sources(self) -> list[Source]:
        """Return enabled sources sorted by priority."""
        return sorted([s for s in self.sources if s.enabled], key=lambda s: s.priority)


def load_config() -> ProjectConfig:
    """Load and return the full project configuration."""
    config_path = DATA_DIR / "config.json"
    sources_path = DATA_DIR / "sources.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    if not sources_path.exists():
        raise FileNotFoundError(f"Sources file not found: {sources_path}")

    raw_config = json.loads(config_path.read_text(encoding="utf-8"))
    raw_sources = json.loads(sources_path.read_text(encoding="utf-8"))

    lp_raw = raw_config.get("language_policy", {})
    language_policy = LanguagePolicy(
        primary_listing_language=lp_raw.get("primary_listing_language", "de"),
        translation_required=lp_raw.get("translation_required", False),
        preserve_source_text=lp_raw.get("preserve_source_text", True),
    )

    agent_config = AgentConfig(
        profile_name=raw_config["profile_name"],
        target_city=raw_config["target_city"],
        move_in_from=raw_config["move_in_from"],
        budget_min_chf=raw_config["budget_min_chf"],
        budget_max_chf=raw_config["budget_max_chf"],
        preferred_roommate_age=raw_config["preferred_roommate_age"],
        diet=raw_config["diet"],
        tram_lines=raw_config.get("tram_lines", []),
        language_policy=language_policy,
        retention_days=raw_config.get("retention_days", 30),
        project_window_days=raw_config.get("project_window_days", 60),
        project_start=raw_config.get("project_start", ""),
        project_end=raw_config.get("project_end", ""),
        manual_triggers_only=raw_config.get("manual_triggers_only", True),
    )

    sources = [
        Source(
            id=s["id"],
            label=s["label"],
            base_url=s["base_url"],
            search_url=s["search_url"],
            enabled=s.get("enabled", False),
            priority=s.get("priority", 99),
            notes=s.get("notes", ""),
        )
        for s in raw_sources
    ]

    return ProjectConfig(agent=agent_config, sources=sources)
