#!/usr/bin/env python3
"""
Extract structured listing samples from Yad2 search page (Playwright).
Uses mobile-style context when YAD2_MOBILE=1 (recommended when desktop hits ShieldSquare).
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

POC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(POC_DIR))

from common import POLITE_DELAY_SEC, USER_AGENTS  # noqa: E402

SAMPLES_DIR = POC_DIR.parent / "samples"


def _pick_feed_items(obj: object, out: list[dict], depth: int = 0) -> None:
    if depth > 12 or len(out) >= 25:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in ("feed", "items", "listings", "data", "commercial", "private") and isinstance(
                v, list
            ):
                for it in v:
                    if isinstance(it, dict) and len(it) > 3:
                        out.append(it)
            _pick_feed_items(v, out, depth + 1)
    elif isinstance(obj, list):
        for it in obj:
            _pick_feed_items(it, out, depth + 1)


def main() -> int:
    time.sleep(POLITE_DELAY_SEC)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        print(json.dumps({"error": str(e)}))
        return 1

    mobile = os.environ.get("YAD2_MOBILE", "1") == "1"
    url = os.environ.get(
        "YAD2_TEST_URL",
        "https://www.yad2.co.il/realestate/rent?mobile=1&topArea=2&area=3&property=1&rooms=1-5.5&price=1-10000",
    )
    if "mobile=" not in url and mobile:
        sep = "&" if "?" in url else "?"
        url = url + sep + "mobile=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        if mobile:
            context = browser.new_context(
                user_agent=USER_AGENTS["iphone_safari"],
                viewport={"width": 390, "height": 844},
                locale="he-IL",
                is_mobile=True,
                has_touch=True,
            )
        else:
            context = browser.new_context(
                user_agent=USER_AGENTS["chrome_desktop"],
                locale="he-IL",
            )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        time.sleep(5)
        html = page.content()
        title = page.title()

        # Try __NEXT_DATA__ (Next.js)
        next_data = None
        el = page.query_selector("script#__NEXT_DATA__")
        if el:
            raw = el.inner_text()
            try:
                next_data = json.loads(raw)
            except json.JSONDecodeError:
                next_data = {"_error": "parse failed", "raw_len": len(raw)}

        # Fallback: find large JSON in script tags
        if not next_data:
            for script in page.query_selector_all("script"):
                txt = script.inner_text()
                if len(txt) < 500 or "token" in txt[:200].lower():
                    continue
                if "feed" in txt.lower() or "listing" in txt.lower() or "nadlan" in txt.lower():
                    try:
                        next_data = json.loads(txt)
                        break
                    except json.JSONDecodeError:
                        m = re.search(r"\{[\s\S]{1000,200000}\}", txt)
                        if m:
                            try:
                                next_data = json.loads(m.group(0))
                                break
                            except json.JSONDecodeError:
                                pass

        browser.close()

    items: list[dict] = []
    if isinstance(next_data, dict):
        _pick_feed_items(next_data, items)

    # De-dup by id-like keys
    seen: set[str] = set()
    unique: list[dict] = []
    for it in items:
        key = str(
            it.get("id") or it.get("token") or it.get("orderId") or it.get("adNumber") or it.get("_id") or ""
        )
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        unique.append(it)
        if len(unique) >= 10:
            break

    meta = {
        "source_url": url,
        "page_title": title,
        "html_bytes": len(html.encode("utf-8")),
        "next_data_found": next_data is not None,
        "items_extracted": len(unique),
        "notes": "items from embedded JSON heuristics; verify fields against live UI",
    }

    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    (SAMPLES_DIR / "extraction_meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    for i, it in enumerate(unique[:10]):
        (SAMPLES_DIR / f"listing_sample_{i+1:02d}.json").write_text(
            json.dumps(it, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )

    # Live extraction attempt bundle (does not overwrite curated synthetic batch_listings_redacted.json)
    (SAMPLES_DIR / "batch_listings_live_attempt.json").write_text(
        json.dumps(
            {
                "meta": meta,
                "listings": unique[:10],
            },
            indent=2,
            ensure_ascii=False,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"Wrote up to {len(unique)} samples under {SAMPLES_DIR}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
