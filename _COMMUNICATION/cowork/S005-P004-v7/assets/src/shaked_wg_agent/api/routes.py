"""FastAPI route handlers."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from shaked_wg_agent.api.deps import resolve_profile_id
from shaked_wg_agent.api.schemas import (
    ErrorDetail,
    ErrorResponse,
    ListingResponse,
    ListingsQuery,
    PaginatedMeta,
    PaginatedResponse,
    ResponseEnvelope,
    ResponseMeta,
    RunResponse,
    RunsQuery,
    SearchRequest,
)
from shaked_wg_agent.config import load_config
from shaked_wg_agent.persistence import load_listings, load_runs
from shaked_wg_agent.runner import run_scan


def create_public_router() -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, Any]:
        import os

        from shaked_wg_agent import __version__

        key = os.environ.get("API_KEY")
        return {
            "status": "ok",
            "version": __version__,
            "auth_configured": bool(key and str(key).strip()),
        }

    return router


def create_auth_router() -> APIRouter:
    router = APIRouter()

    @router.post("/search")
    async def search(body: SearchRequest, request: Request) -> dict[str, Any]:
        profile_id = resolve_profile_id(body.profile_id, body.city_id)
        cfg = load_config(profile_id)
        run_record = run_scan(cfg=cfg, triggered_by="api")
        return ResponseEnvelope(
            data=RunResponse(**run_record),
            meta=ResponseMeta(
                timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
                request_id=request.state.request_id,
            ),
        ).model_dump()

    @router.get("/listings")
    async def list_listings(
        request: Request,
        profile_id: str | None = Query(None),
        city_id: str | None = Query(None),
        min_score: int = Query(0, ge=0, le=100),
        status: str | None = Query(None),
        source: str | None = Query(None),
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ) -> dict[str, Any]:
        params = ListingsQuery(
            profile_id=profile_id,
            city_id=city_id,
            min_score=min_score,
            status=status,
            source=source,
            limit=limit,
            offset=offset,
        )
        resolved = resolve_profile_id(params.profile_id, params.city_id)
        if resolved is None and params.city_id is None:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error=ErrorDetail(
                        code="BAD_REQUEST",
                        message="Either profile_id or city_id is required.",
                    )
                ).model_dump(),
            )

        all_listings = load_listings()
        effective_city_id = params.city_id
        if resolved and not effective_city_id:
            try:
                cfg = load_config(resolved)
                effective_city_id = cfg.city.city_id
            except (FileNotFoundError, ValueError):
                pass

        filtered = all_listings
        if effective_city_id:
            filtered = [row for row in filtered if row.get("city_id") == effective_city_id]
        if resolved:
            filtered = [row for row in filtered if row.get("profile_id") == resolved]
        if params.min_score > 0:
            filtered = [
                row for row in filtered if row.get("relevance_score", 0) >= params.min_score
            ]
        if params.status:
            filtered = [row for row in filtered if row.get("status") == params.status]
        if params.source:
            filtered = [row for row in filtered if row.get("source") == params.source]

        filtered.sort(key=lambda row: row.get("relevance_score", 0), reverse=True)
        total_count = len(filtered)
        page = filtered[params.offset : params.offset + params.limit]
        items = [ListingResponse(**row) for row in page]
        return PaginatedResponse(
            data=items,
            meta=PaginatedMeta(
                timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
                request_id=request.state.request_id,
                total_count=total_count,
                offset=params.offset,
                limit=params.limit,
            ),
        ).model_dump()

    @router.get("/listings/{listing_id}")
    async def get_listing(listing_id: str, request: Request) -> dict[str, Any]:
        all_listings = load_listings()
        match = next(
            (row for row in all_listings if row.get("listing_id") == listing_id),
            None,
        )
        if match is None:
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    error=ErrorDetail(
                        code="NOT_FOUND",
                        message=f"Listing '{listing_id}' not found.",
                    )
                ).model_dump(),
            )
        return ResponseEnvelope(
            data=ListingResponse(**match),
            meta=ResponseMeta(
                timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
                request_id=request.state.request_id,
            ),
        ).model_dump()

    @router.get("/runs")
    async def list_runs(
        request: Request,
        profile_id: str | None = Query(None),
        city_id: str | None = Query(None),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ) -> dict[str, Any]:
        params = RunsQuery(profile_id=profile_id, city_id=city_id, limit=limit, offset=offset)
        all_runs = load_runs()
        filtered = all_runs
        if params.city_id:
            filtered = [r for r in filtered if r.get("city_id") == params.city_id]
        if params.profile_id:
            filtered = [r for r in filtered if r.get("profile_id") == params.profile_id]
        total_count = len(filtered)
        page = filtered[params.offset : params.offset + params.limit]
        items = [RunResponse(**r) for r in page]
        return PaginatedResponse(
            data=items,
            meta=PaginatedMeta(
                timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
                request_id=request.state.request_id,
                total_count=total_count,
                offset=params.offset,
                limit=params.limit,
            ),
        ).model_dump()

    @router.get("/runs/{run_id}")
    async def get_run(run_id: str, request: Request) -> dict[str, Any]:
        all_runs = load_runs()
        match = next((r for r in all_runs if r.get("run_id") == run_id), None)
        if match is None:
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    error=ErrorDetail(
                        code="NOT_FOUND",
                        message=f"Run '{run_id}' not found.",
                    )
                ).model_dump(),
            )
        return ResponseEnvelope(
            data=RunResponse(**match),
            meta=ResponseMeta(
                timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
                request_id=request.state.request_id,
            ),
        ).model_dump()

    return router
