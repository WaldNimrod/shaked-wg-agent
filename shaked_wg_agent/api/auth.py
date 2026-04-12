"""API key authentication dependency for protected routes."""
from __future__ import annotations

import hmac
import logging
import os

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

logger = logging.getLogger("shaked_wg_agent.api.middleware")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

_UNAUTHORIZED_BODY = {
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Missing or invalid API key",
        "detail": None,
    }
}


async def verify_api_key(request: Request, x_api_key: str | None = Security(api_key_header)) -> None:
    """Validate X-API-Key header; raises HTTPException with exact JSON body on failure."""
    expected = os.environ.get("API_KEY")
    if not expected:
        logger.error("Auth error: API_KEY env var not configured")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Server misconfiguration",
                    "detail": None,
                }
            },
        )

    provided = x_api_key or ""
    if not provided:
        logger.debug("Auth failed: missing key")
        raise HTTPException(status_code=401, detail=_UNAUTHORIZED_BODY)

    if not hmac.compare_digest(provided, expected):
        logger.debug("Auth failed: invalid key")
        raise HTTPException(status_code=401, detail=_UNAUTHORIZED_BODY)


def unauthorized_exception_handler() -> dict:
    """Return literal detail dict for 401 (same for missing and invalid key)."""
    return _UNAUTHORIZED_BODY
