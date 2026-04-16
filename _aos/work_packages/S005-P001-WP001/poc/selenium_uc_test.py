#!/usr/bin/env python3
"""Optional: undetected-chromedriver smoke test (requires requirements-poc.txt)."""
from __future__ import annotations

import contextlib
import json
import sys
import time
from pathlib import Path

POC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(POC_DIR))

from common import DEFAULT_SEARCH_URL, POLITE_DELAY_SEC, looks_like_cloudflare  # noqa: E402


def main() -> int:
    time.sleep(POLITE_DELAY_SEC)
    try:
        import undetected_chromedriver as uc
    except ImportError:
        print(
            json.dumps(
                {
                    "method": "selenium_undetected_chromedriver",
                    "ok": False,
                    "notes": "undetected-chromedriver not installed",
                }
            )
        )
        return 0

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--lang=he-IL")
    driver = None
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        driver.set_page_load_timeout(45)
        driver.get(DEFAULT_SEARCH_URL)
        time.sleep(3)
        html = driver.page_source
        cf = looks_like_cloudflare(html)
        out = {
            "method": "selenium_undetected_chromedriver",
            "ok": not cf and len(html) > 1000,
            "cloudflare_challenge": cf,
            "bytes_received": len(html.encode("utf-8")),
            "title": driver.title[:200] if driver.title else "",
            "notes": "headless uc",
        }
    except Exception as e:
        out = {
            "method": "selenium_undetected_chromedriver",
            "ok": False,
            "notes": repr(e),
        }
    finally:
        if driver is not None:
            with contextlib.suppress(Exception):
                driver.quit()

    print(json.dumps(out, ensure_ascii=False, indent=2))
    (POC_DIR / "selenium_uc_last.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
