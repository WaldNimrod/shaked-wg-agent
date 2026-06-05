"""WordPress REST API media upload — replaces old media before uploading new version.

Usage:
    from shaked_wg_agent.publisher.wp_upload import upload_html
    media_id, url = upload_html(Path("data/shaked_curated_2026-05-06.html"))
    media_id, url = upload_html(Path("data/shaked_aug.html"), canonical_filename="shaked-aug.html")

The canonical remote filename stays fixed so the URL never gets a numeric suffix (-1, -2 …).
The previous media_id is stored in ``data/.wp_media_id_<slug>`` and deleted before each upload.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

_CANONICAL_FILENAME = "shaked-top10.html"
_CANONICAL_FILENAME_AUG = "shaked-aug.html"


def _token() -> str:
    user = os.environ["UPRESS_WP_APP_USER"]
    pw = os.environ["UPRESS_WP_APP_PASS"]
    return base64.b64encode(f"{user}:{pw}".encode()).decode()


def _rest_base() -> str:
    return os.environ.get("UPRESS_WP_REST_BASE", "https://www.nimrod.bio/wp-json")


def _media_id_file(canonical_filename: str) -> Path:
    """Derive a local media-ID tracking file from the canonical filename."""
    slug = canonical_filename.replace(".", "_").replace("-", "_")
    return Path(f"data/.wp_media_id_{slug}")


def upload_html(html_path: Path, canonical_filename: str = _CANONICAL_FILENAME) -> tuple[int, str]:
    """Delete previous media entry (if any) then upload html_path under canonical_filename.

    Returns (media_id, public_url).
    """
    headers_auth = {"Authorization": f"Basic {_token()}"}
    base = _rest_base()
    id_file = _media_id_file(canonical_filename)

    # Migrate legacy data/.wp_media_id → new per-file naming for the default page
    legacy = Path("data/.wp_media_id")
    if canonical_filename == _CANONICAL_FILENAME and legacy.exists() and not id_file.exists():
        id_file.write_text(legacy.read_text())

    # Delete previous version so the URL stays clean (no -1 / -2 suffix)
    if id_file.exists():
        old_id = id_file.read_text().strip()
        if old_id:
            requests.delete(
                f"{base}/wp/v2/media/{old_id}?force=1",
                headers=headers_auth,
                timeout=15,
            )

    # Upload new version
    resp = requests.post(
        f"{base}/wp/v2/media",
        headers={
            **headers_auth,
            "Content-Disposition": f'attachment; filename="{canonical_filename}"',
            "Content-Type": "text/html",
        },
        data=html_path.read_bytes(),
        timeout=30,
    )
    resp.raise_for_status()
    j = resp.json()
    media_id: int = j["id"]
    url: str = j["source_url"]

    id_file.write_text(str(media_id))
    return media_id, url
