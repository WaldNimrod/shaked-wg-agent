"""FastAPI application factory."""
from __future__ import annotations

import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest

from shaked_wg_agent.api.auth import verify_api_key
from shaked_wg_agent.api.routes import create_auth_router, create_public_router
from shaked_wg_agent.api.schemas import ErrorDetail, ErrorResponse

logger = logging.getLogger("shaked_wg_agent.api.middleware")


@asynccontextmanager
async def lifespan(app: FastAPI):
    key = os.environ.get("API_KEY")
    if not key or not str(key).strip():
        logger.warning("API_KEY is not set — protected routes will return 500 until configured.")
    elif len(str(key)) < 32:
        logger.warning("API_KEY is shorter than 32 characters — consider a longer key.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Shaked WG Agent API",
        version="0.3.0",
        lifespan=lifespan,
    )

    origins_raw = os.environ.get("API_CORS_ORIGINS", "")
    if origins_raw.strip():
        origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.middleware("http")
    async def add_request_id(request: StarletteRequest, call_next):
        request.state.request_id = f"req-{uuid.uuid4().hex[:8]}"
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        body = ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred.",
                detail=str(exc) if os.environ.get("API_DEBUG") else None,
            )
        )
        return JSONResponse(
            status_code=500,
            content=body.model_dump(),
            headers={"X-Request-ID": request_id},
        )

    app.include_router(create_public_router())
    app.include_router(
        create_auth_router(),
        dependencies=[Depends(verify_api_key)],
    )

    return app
