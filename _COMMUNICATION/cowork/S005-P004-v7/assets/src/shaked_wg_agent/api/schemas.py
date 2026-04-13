"""Pydantic request/response models for the REST API."""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SearchRequest(BaseModel):
    """POST /search body."""

    profile_id: str | None = Field(
        default=None,
        description="Search profile to scan (preferred parameter).",
    )
    city_id: str | None = Field(
        default=None,
        description="DEPRECATED. Alias for profile_id — resolved to the first "
        "profile targeting this city.",
        json_schema_extra={"deprecated": True},
    )


class ListingsQuery(BaseModel):
    """GET /listings query parameters."""

    profile_id: str | None = None
    city_id: str | None = None
    min_score: int = Field(default=0, ge=0, le=100)
    status: str | None = None
    source: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class RunsQuery(BaseModel):
    """GET /runs query parameters."""

    profile_id: str | None = None
    city_id: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ResponseMeta(BaseModel):
    timestamp: str
    request_id: str


class PaginatedMeta(ResponseMeta):
    total_count: int
    offset: int
    limit: int


class ResponseEnvelope(BaseModel, Generic[T]):
    data: T
    meta: ResponseMeta


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginatedMeta


class ListingResponse(BaseModel):
    """Single listing — fields from listings.json schema."""

    listing_id: str
    source: str
    title: str = ""
    price_chf: int | None = None
    available_from: str | None = None
    location_text: str = ""
    district: str = ""
    transit_match_lines: list[str] = Field(default_factory=list)
    roommate_signal: str = ""
    vegan_signal: str = ""
    summary: str = ""
    direct_url: str = ""
    url_status: str = ""
    relevance_score: int = 0
    status: str = "neu"
    note: str = ""
    tags: list[str] = Field(default_factory=list)
    first_seen_at: str = ""
    last_seen_at: str = ""
    verified_active: bool = False
    last_verified_at: str | None = None
    source_listing_id: str | None = None
    city_id: str | None = None
    profile_id: str | None = None

    model_config = {"extra": "ignore"}


class RunResponse(BaseModel):
    """Single run record."""

    run_id: str
    run_timestamp: str
    triggered_by: str = "manual"
    sources_scanned: int = 0
    results_scanned: int = 0
    new_results: int = 0
    updated_results: int = 0
    stale_removed: int = 0
    duration_seconds: int = 0
    errors: list[str] = Field(default_factory=list)
    report_url: str | None = None
    operator_notes: str = ""
    city_id: str | None = None
    profile_id: str | None = None
    notification_sent: dict[str, Any] | None = None

    model_config = {"extra": "ignore"}


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
