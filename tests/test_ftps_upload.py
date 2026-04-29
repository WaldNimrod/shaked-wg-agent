"""FTPS upload path resolution (per-profile public URLs on uPress)."""
from __future__ import annotations

import pytest

from shaked_wg_agent.publisher.ftps_upload import resolve_upload_path


def test_resolve_upload_path_explicit_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UPRESS_UPLOAD_PATH", "custom/path/here")
    assert resolve_upload_path("dror") == "custom/path/here"


def test_resolve_upload_path_dror_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UPRESS_UPLOAD_PATH", raising=False)
    assert resolve_upload_path("dror") == "wp-content/uploads/shaked-wg/dror"


def test_resolve_upload_path_default_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UPRESS_UPLOAD_PATH", raising=False)
    assert resolve_upload_path("default") == "wp-content/uploads/shaked-wg"
