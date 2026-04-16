#!/usr/bin/env python3
"""
Yad2 POC — scraping method matrix (S005-P001-WP001).
Not production code. Run from repo root: python _aos/work_packages/S005-P001-WP001/poc/method_matrix.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests

POC_DIR = Path(__file__).resolve().parent
if str(POC_DIR) not in sys.path:
    sys.path.insert(0, str(POC_DIR))

from common import (  # noqa: E402
    DEFAULT_SEARCH_URL,
    POLITE_DELAY_SEC,
    USER_AGENTS,
    looks_like_bot_wall,
    looks_like_cloudflare,
)


def _result(
    method: str,
    ok: bool,
    status: int | None,
    title_hint: str,
    cf_challenge: bool,
    bytes_received: int,
    notes: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "method": method,
        "ok": ok,
        "http_status": status,
        "page_title_or_hint": title_hint,
        "cloudflare_challenge": cf_challenge,
        "bytes_received": bytes_received,
        "notes": notes,
    }
    if extra:
        row["extra"] = extra
    return row


def test_requests_variants(url: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name, ua in USER_AGENTS.items():
        time.sleep(POLITE_DELAY_SEC)
        try:
            r = requests.get(
                url,
                headers={"User-Agent": ua, "Accept-Language": "he-IL,he;q=0.9,en;q=0.8"},
                timeout=25,
            )
            text = r.text or ""
            title = "n/a"
            if "<title>" in text.lower():
                start = text.lower().find("<title>")
                end = text.lower().find("</title>", start)
                if end > start:
                    title = text[start + 7 : end].strip()[:120]
            wall = looks_like_bot_wall(text, title)
            cf = looks_like_cloudflare(text)
            rows.append(
                _result(
                    f"requests.get UA={name}",
                    r.status_code == 200 and not wall,
                    r.status_code,
                    title,
                    cf or wall,
                    len(text.encode("utf-8")),
                    "bot_wall_or_captcha" if wall else "HTML body",
                )
            )
        except requests.RequestException as e:
            rows.append(
                _result(
                    f"requests.get UA={name}",
                    False,
                    None,
                    "",
                    False,
                    0,
                    str(e),
                )
            )
    return rows


def test_playwright_default(url: str) -> dict[str, Any]:
    time.sleep(POLITE_DELAY_SEC)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        return _result("playwright_headless_default", False, None, "", False, 0, f"import error: {e}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                locale="he-IL",
                user_agent=USER_AGENTS["chrome_desktop"],
            )
            page = context.new_page()
            resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            status = resp.status if resp else None
            time.sleep(2)
            content = page.content()
            title = page.title()
            wall = looks_like_bot_wall(content, title)
            cf = looks_like_cloudflare(content)
            browser.close()
            return _result(
                "playwright_headless_default",
                status == 200 and not wall,
                status,
                title[:200] if title else "",
                cf or wall,
                len(content.encode("utf-8")),
                "domcontentloaded",
            )
    except Exception as e:
        return _result("playwright_headless_default", False, None, "", False, 0, repr(e))


def test_playwright_stealth(url: str) -> dict[str, Any]:
    time.sleep(POLITE_DELAY_SEC)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        return _result("playwright_stealth", False, None, "", False, 0, f"playwright: {e}")

    try:
        from playwright_stealth import Stealth
    except ImportError:
        return _result(
            "playwright_stealth",
            False,
            None,
            "",
            False,
            0,
            "playwright_stealth package not installed (pip install -r requirements-poc.txt)",
        )

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                locale="he-IL",
                user_agent=USER_AGENTS["chrome_desktop"],
            )
            page = context.new_page()
            Stealth().apply_stealth_sync(page)
            resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            status = resp.status if resp else None
            time.sleep(2)
            content = page.content()
            title = page.title()
            wall = looks_like_bot_wall(content, title)
            cf = looks_like_cloudflare(content)
            browser.close()
            return _result(
                "playwright_stealth",
                status == 200 and not wall,
                status,
                title[:200] if title else "",
                cf or wall,
                len(content.encode("utf-8")),
                "playwright-stealth applied",
            )
    except Exception as e:
        return _result("playwright_stealth", False, None, "", False, 0, repr(e))


def test_playwright_mobile() -> dict[str, Any]:
    """Mobile User-Agent on www (m. subdomain not consistently resolvable in DNS tests)."""
    url = "https://www.yad2.co.il/realestate/rent?mobile=1"
    time.sleep(POLITE_DELAY_SEC)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        return _result("playwright_mobile_m_yad2", False, None, "", False, 0, str(e))

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=USER_AGENTS["iphone_safari"],
                viewport={"width": 390, "height": 844},
                locale="he-IL",
                is_mobile=True,
                has_touch=True,
            )
            page = context.new_page()
            resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            status = resp.status if resp else None
            time.sleep(2)
            content = page.content()
            title = page.title()
            wall = looks_like_bot_wall(content, title)
            cf = looks_like_cloudflare(content)
            browser.close()
            return _result(
                "playwright_mobile_ua_www",
                status == 200 and not wall,
                status,
                title[:200] if title else "",
                cf or wall,
                len(content.encode("utf-8")),
                f"url={url}",
            )
    except Exception as e:
        return _result("playwright_mobile_ua_www", False, None, "", False, 0, repr(e))


def test_cookie_replay(url: str) -> dict[str, Any]:
    """Optional: set COOKIE_HEADER env or cookies.txt Netscape format (first line # or tab)."""
    time.sleep(POLITE_DELAY_SEC)
    cookie_header = os.environ.get("YAD2_COOKIE_HEADER", "").strip()
    cookie_file = POC_DIR / "cookies.txt"
    if not cookie_header and cookie_file.is_file():
        raw = cookie_file.read_text(encoding="utf-8", errors="replace").strip()
        if raw and not raw.startswith("#"):
            # single line cookie string
            cookie_header = raw

    if not cookie_header:
        return _result(
            "cookie_replay_requests",
            False,
            None,
            "",
            False,
            0,
            "skipped — set YAD2_COOKIE_HEADER or create poc/cookies.txt (gitignored)",
        )

    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENTS["chrome_desktop"],
                "Cookie": cookie_header,
                "Accept-Language": "he-IL,he;q=0.9",
            },
            timeout=25,
        )
        text = r.text or ""
        wall = looks_like_bot_wall(text, "")
        cf = looks_like_cloudflare(text)
        return _result(
            "cookie_replay_requests",
            r.status_code == 200 and not wall,
            r.status_code,
            "see body",
            cf or wall,
            len(text.encode("utf-8")),
            f"Cookie header length={len(cookie_header)}",
        )
    except requests.RequestException as e:
        return _result("cookie_replay_requests", False, None, "", False, 0, str(e))


def main() -> int:
    url = os.environ.get("YAD2_TEST_URL", DEFAULT_SEARCH_URL)
    out: dict[str, Any] = {
        "test_url": url,
        "polite_delay_sec": POLITE_DELAY_SEC,
        "results": [],
    }

    out["results"].extend(test_requests_variants(url))
    out["results"].append(test_playwright_default(url))
    out["results"].append(test_playwright_stealth(url))
    out["results"].append(test_playwright_mobile())
    out["results"].append(test_cookie_replay(url))

    out_path = POC_DIR / "last_run_results.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
