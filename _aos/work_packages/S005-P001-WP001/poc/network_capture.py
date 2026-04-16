#!/usr/bin/env python3
"""Log XHR/fetch-like responses from one Playwright navigation (polite, single page)."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

POC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(POC_DIR))

from common import DEFAULT_SEARCH_URL_MOBILE, POLITE_DELAY_SEC, USER_AGENTS  # noqa: E402

# Patterns that suggest API/data endpoints (for documentation only)
INTERESTING = re.compile(
    r"(/api/|graphql|\.json|feed|search|items|listings|nadlan|realestate)",
    re.I,
)


def main() -> int:
    time.sleep(POLITE_DELAY_SEC)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    captured: list[dict[str, str | int]] = []

    def on_response(response) -> None:
        try:
            u = response.url
            if not INTERESTING.search(u):
                return
            ct = (response.headers.get("content-type") or "")[:80]
            captured.append(
                {
                    "url": u[:500],
                    "status": response.status,
                    "content_type": ct,
                    "host": urlparse(u).netloc,
                }
            )
        except Exception:
            pass

    url = os.environ.get("YAD2_TEST_URL", DEFAULT_SEARCH_URL_MOBILE)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENTS["iphone_safari"])
        page.on("response", on_response)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        browser.close()

    out = {"search_url": url, "responses": captured[:80]}
    path = POC_DIR / "network_capture.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False)[:12000])
    print(f"\nWrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
