"""Load and validate project configuration from data/agent.json, cities, profiles, sources."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"

_ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,29}$")

_VALID_RENTAL = frozenset({"temporary", "short", "permanent"})
_VALID_SMOKING = frozenset({"non_smoking", "smoking_ok", ""})
_VALID_DIET = frozenset({"vegan", "vegetarian", ""})
_VALID_ROOMMATE_AGE = frozenset({"young", "mixed", "any", ""})
_VALID_CHANNEL_TYPES = frozenset({"email", "telegram", "discord", "ntfy", "webhook"})


@dataclass
class LanguagePolicy:
    primary_listing_language: str = "de"
    translation_required: bool = False
    preserve_source_text: bool = True


@dataclass
class BoundingBox:
    west: float
    east: float
    south: float
    north: float


@dataclass
class CityDefinition:
    city_id: str
    city_name: str
    bounding_box: BoundingBox
    available_sources: list[str]
    country: str = "CH"
    currency: str = "CHF"
    zip_filter: list[str] = field(default_factory=list)
    # If non-empty, listings must match at least one settlement substring (district/title/location).
    settlement_allowlist: list[str] = field(default_factory=list)


@dataclass
class AgentMeta:
    default_profile_id: str
    manual_triggers_only: bool = True
    project_window_days: int = 60
    project_start: str = ""
    project_end: str = ""


@dataclass
class ChannelConfig:
    type: str
    enabled: bool
    label: str | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in _VALID_CHANNEL_TYPES:
            raise ValueError(
                "ChannelConfig type must be one of: email, telegram, discord, ntfy, webhook"
            )


@dataclass
class NotificationConfig:
    digest_max_listings: int = 5
    min_score_threshold: int = 0
    channels: list[ChannelConfig] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.channels) > 5:
            raise ValueError("NotificationConfig allows at most 5 channels")
        if not (1 <= self.digest_max_listings <= 25):
            raise ValueError("digest_max_listings must be between 1 and 25 inclusive")
        if not (0 <= self.min_score_threshold <= 100):
            raise ValueError("min_score_threshold must be between 0 and 100 inclusive")


@dataclass
class SearchProfile:
    profile_id: str
    profile_name: str
    city_id: str
    move_in_from: str
    budget_min: int
    budget_max: int
    preferred_roommate_age: str
    rental_duration: str
    diet: str = ""
    smoking_policy: str = ""
    transit_lines: list[str] = field(default_factory=list)
    custom_tags: list[str] = field(default_factory=list)
    language_policy: LanguagePolicy = field(default_factory=LanguagePolicy)
    retention_days: int = 30
    enabled_sources: list[str] = field(default_factory=list)
    notifications: NotificationConfig | None = None
    # Hebrew client-facing title for published HTML when country is IL (optional).
    report_title_he: str | None = None


@dataclass
class CitySourceParams:
    search_url: str
    connection_method: str = ""
    enabled: bool = True


@dataclass
class SourceDefinition:
    source_id: str
    label: str
    base_url: str
    scraper_class: str
    city_params: dict[str, CitySourceParams]
    connector_class: str | None = None
    requires_playwright: bool = False
    notes: str = ""


@dataclass
class ResolvedSource:
    source_id: str
    label: str
    base_url: str
    search_url: str
    scraper_class: str
    requires_playwright: bool
    priority: int
    notes: str
    connector_class: str | None = None


@dataclass
class ProjectConfig:
    agent: AgentMeta
    profile: SearchProfile
    city: CityDefinition
    sources: list[ResolvedSource] = field(default_factory=list)

    @property
    def active_sources(self) -> list[ResolvedSource]:
        return sorted(self.sources, key=lambda s: s.priority)


def _validate_profile_id(profile_id: str) -> None:
    if not _ID_RE.match(profile_id):
        raise ValueError(
            f"Invalid profile_id '{profile_id}': must match ^[a-z][a-z0-9-]{{0,29}}$"
        )


def _validate_city_id(city_id: str) -> None:
    if not _ID_RE.match(city_id):
        raise ValueError(f"Invalid city_id '{city_id}': must match ^[a-z][a-z0-9-]{{0,29}}$")


def _parse_channel(raw: dict[str, Any]) -> ChannelConfig:
    rest = {
        k: v
        for k, v in raw.items()
        if k not in ("type", "enabled", "label")
    }
    return ChannelConfig(
        type=raw["type"],
        enabled=raw["enabled"],
        label=raw.get("label"),
        params=rest,
    )


def _notification_from_dict(raw: dict[str, Any] | None) -> NotificationConfig | None:
    if raw is None:
        return None
    chans: list[ChannelConfig] = []
    for c in raw.get("channels") or []:
        chans.append(_parse_channel(c))
    return NotificationConfig(
        digest_max_listings=raw.get("digest_max_listings", 5),
        min_score_threshold=raw.get("min_score_threshold", 0),
        channels=chans,
    )


def _load_agent_meta() -> AgentMeta:
    path = DATA_DIR / "agent.json"
    if not path.exists():
        raise FileNotFoundError(f"Agent config not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    dpid = raw.get("default_profile_id")
    if not dpid:
        raise ValueError("agent.json missing required field 'default_profile_id'")
    return AgentMeta(
        default_profile_id=str(dpid),
        manual_triggers_only=raw.get("manual_triggers_only", True),
        project_window_days=raw.get("project_window_days", 60),
        project_start=raw.get("project_start", ""),
        project_end=raw.get("project_end", ""),
    )


def _load_city(city_id: str) -> CityDefinition:
    _validate_city_id(city_id)
    path = DATA_DIR / "cities" / f"{city_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"City definition not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    bb = raw["bounding_box"]
    filters = raw.get("filters") or {}
    settlements = list(filters.get("settlements") or [])

    currency = raw.get("currency", "CHF")
    country = raw.get("country")
    if country is None or country == "":
        # Infer IL when Shekel is set but country omitted (older city JSON on edge servers).
        country = "IL" if str(currency).upper() == "ILS" else "CH"

    return CityDefinition(
        city_id=raw["city_id"],
        city_name=raw["city_name"],
        bounding_box=BoundingBox(
            west=float(bb["west"]),
            east=float(bb["east"]),
            south=float(bb["south"]),
            north=float(bb["north"]),
        ),
        available_sources=list(raw["available_sources"]),
        country=str(country),
        currency=currency,
        zip_filter=list(raw.get("zip_filter", [])),
        settlement_allowlist=settlements,
    )


def _validate_search_profile_fields(p: SearchProfile) -> None:
    if len(p.custom_tags) > 3:
        raise ValueError(
            f"SearchProfile custom_tags limited to 3 entries, got {len(p.custom_tags)}"
        )
    if p.rental_duration not in _VALID_RENTAL:
        raise ValueError("rental_duration must be one of: temporary, short, permanent")
    if p.smoking_policy not in _VALID_SMOKING:
        raise ValueError("smoking_policy must be one of: non_smoking, smoking_ok, (empty string)")
    if p.diet not in _VALID_DIET:
        raise ValueError("diet must be one of: vegan, vegetarian, (empty string)")
    if p.preferred_roommate_age not in _VALID_ROOMMATE_AGE:
        raise ValueError(
            "preferred_roommate_age must be one of: young, mixed, any, (empty string)"
        )


def _load_profile(profile_id: str) -> SearchProfile:
    _validate_profile_id(profile_id)
    path = DATA_DIR / "profiles" / f"{profile_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))

    lp_raw = raw.get("language_policy") or {}
    language_policy = LanguagePolicy(
        primary_listing_language=lp_raw.get("primary_listing_language", "de"),
        translation_required=lp_raw.get("translation_required", False),
        preserve_source_text=lp_raw.get("preserve_source_text", True),
    )

    tags = list(raw.get("custom_tags") or [])
    if len(tags) > 3:
        raise ValueError(f"SearchProfile custom_tags limited to 3 entries, got {len(tags)}")

    notif_raw = raw.get("notifications")
    notifications: NotificationConfig | None = (
        None if notif_raw is None else _notification_from_dict(notif_raw)
    )

    budget_min_val = raw.get("budget_min")
    if budget_min_val is None:
        budget_min_val = raw.get("budget_min_chf")
    budget_max_val = raw.get("budget_max")
    if budget_max_val is None:
        budget_max_val = raw.get("budget_max_chf")
    if budget_min_val is None or budget_max_val is None:
        raise KeyError(
            f"Profile '{profile_id}' missing budget_min/budget_max (or legacy budget_min_chf/budget_max_chf)"
        )

    profile = SearchProfile(
        profile_id=raw["profile_id"],
        profile_name=raw["profile_name"],
        report_title_he=raw.get("report_title_he"),
        city_id=raw["city_id"],
        move_in_from=raw["move_in_from"],
        budget_min=int(budget_min_val),
        budget_max=int(budget_max_val),
        preferred_roommate_age=raw["preferred_roommate_age"],
        rental_duration=raw["rental_duration"],
        diet=raw.get("diet", ""),
        smoking_policy=raw.get("smoking_policy", ""),
        transit_lines=list(raw.get("transit_lines") or []),
        custom_tags=tags,
        language_policy=language_policy,
        retention_days=raw.get("retention_days", 30),
        enabled_sources=list(raw.get("enabled_sources") or []),
        notifications=notifications,
    )
    _validate_search_profile_fields(profile)
    return profile


def _load_sources() -> list[SourceDefinition]:
    path = DATA_DIR / "sources.json"
    if not path.exists():
        raise FileNotFoundError(f"Sources registry not found: {path}")
    raw_list = json.loads(path.read_text(encoding="utf-8"))
    out: list[SourceDefinition] = []
    for raw in raw_list:
        cparams: dict[str, CitySourceParams] = {}
        for cid, cp in (raw.get("city_params") or {}).items():
            cparams[cid] = CitySourceParams(
                search_url=cp.get("search_url", ""),
                connection_method=cp.get("connection_method", ""),
                enabled=cp.get("enabled", True),
            )
        out.append(
            SourceDefinition(
                source_id=raw["source_id"],
                label=raw["label"],
                base_url=raw["base_url"],
                scraper_class=raw["scraper_class"],
                city_params=cparams,
                connector_class=raw.get("connector_class"),
                requires_playwright=raw.get("requires_playwright", False),
                notes=raw.get("notes", ""),
            )
        )
    return out


def load_config(profile_id: str | None = None) -> ProjectConfig:
    """Load full project config: agent meta → profile → city → resolved sources."""
    agent_meta = _load_agent_meta()
    pid = profile_id if profile_id is not None else agent_meta.default_profile_id
    profile = _load_profile(pid)
    city = _load_city(profile.city_id)
    source_defs = _load_sources()
    registry = {sd.source_id: sd for sd in source_defs}

    if profile.enabled_sources:
        enabled_ids = set(profile.enabled_sources)
    else:
        enabled_ids = set(city.available_sources)
    candidate_ids = enabled_ids & set(city.available_sources)

    resolved_sources: list[ResolvedSource] = []
    for priority, source_id in enumerate(city.available_sources):
        if source_id not in candidate_ids:
            continue
        sd = registry.get(source_id)
        if sd is None:
            logger.warning(
                "Source '%s' in city/profile but not in sources.json — skipped", source_id
            )
            continue
        csp = sd.city_params.get(city.city_id)
        if csp is None:
            logger.warning(
                "Source '%s' has no params for city '%s' — skipped",
                source_id,
                city.city_id,
            )
            continue
        if not csp.enabled:
            continue
        resolved_sources.append(
            ResolvedSource(
                source_id=sd.source_id,
                label=sd.label,
                base_url=sd.base_url,
                search_url=csp.search_url,
                scraper_class=sd.scraper_class,
                requires_playwright=sd.requires_playwright,
                priority=priority,
                notes=sd.notes,
                connector_class=sd.connector_class,
            )
        )

    if not resolved_sources:
        raise ValueError(
            f"No active sources after resolving profile '{pid}' with city '{city.city_id}'"
        )

    return ProjectConfig(
        agent=agent_meta,
        profile=profile,
        city=city,
        sources=resolved_sources,
    )
