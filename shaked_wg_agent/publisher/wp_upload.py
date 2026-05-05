"""WordPress REST API media upload — replaces old media before uploading new version.

Usage:
    from shaked_wg_agent.publisher.wp_upload import upload_html
    media_id, url = upload_html(Path("data/shaked_curated_2026-05-06.html"))

The canonical remote filename is always ``shaked-top10.html``.
The previous media_id is stored in ``data/.wp_media_id`` and deleted before each upload
so the URL never gets a numeric suffix (e.g. -1, -2 …).
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

_CANONICAL_FILENAME = "shaked-top10.html"
_MEDIA_ID_FILE = Path("data/.wp_media_id")


def _token() -> str:
    user = os.environ["UPRESS_WP_APP_USER"]
    pw = os.environ["UPRESS_WP_APP_PASS"]
    return base64.b64encode(f"{user}:{pw}".encode()).decode()


def _rest_base() -> str:
    return os.environ.get("UPRESS_WP_REST_BASE", "https://www.nimrod.bio/wp-json")


def upload_html(html_path: Path) -> tuple[int, str]:
    """Delete previous media entry (if any) then upload html_path as shaked-top10.html.

    Returns (media_id, public_url).
    """
    headers_auth = {"Authorization": f"Basic {_token()}"}
    base = _rest_base()

    # Delete previous version
    if _MEDIA_ID_FILE.exists():
        old_id = _MEDIA_ID_FILE.read_text().strip()
        if old_id:
            requests.delete(f"{base}/wp/v2/media/{old_id}?force=1",
                            headers=headers_auth, timeout=15)

    # Upload new version
    resp = requests.post(
        f"{base}/wp/v2/media",
        headers={
            **headers_auth,
            "Content-Disposition": f'attachment; filename="{_CANONICAL_FILENAME}"',
            "Content-Type": "text/html",
        },
        data=html_path.read_bytes(),
        timeout=30,
    )
    resp.raise_for_status()
    j = resp.json()
    media_id: int = j["id"]
    url: str = j["source_url"]

    _MEDIA_ID_FILE.write_text(str(media_id))
    return media_id, url
