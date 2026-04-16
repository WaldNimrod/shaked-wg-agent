# MANDATE — S005-P005-WP001: wgzimmer.ch reCAPTCHA v3 Bypass

**Assigned to:** Team 20 (Builder)
**Authority:** Team 00

## YOUR TASK

Modify `shaked_wg_agent/scrapers/wgzimmer_pw.py` to replace Playwright with Patchright (drop-in fork removing automation markers) and switch from ephemeral browser contexts to a persistent browser profile. This restores wgzimmer.ch search results by improving the reCAPTCHA v3 score. No parsing or filtering logic is changed.

## INPUT FILES

- **Read:** `specs/LOD400_S005-P005-WP001.md` — full spec with code changes, error handling contract, test requirements
- **Modify:** `src/shaked_wg_agent/scrapers/wgzimmer_pw.py` — the scraper to update
- **Reference:** `src/shaked_wg_agent/scrapers/base.py` — BaseScraper interface and ScrapedListing dataclass

## OUTPUT FILES

- **Modify:** `output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py`

## TECHNICAL CONTEXT

**Patchright** is a drop-in Playwright fork with identical API (`sync_playwright`, `chromium.launch`, etc.) but with automation detection markers removed. The only import change is `from patchright.sync_api import sync_playwright`.

**Persistent browser context** uses `chromium.launch_persistent_context(user_data_dir=...)` instead of `chromium.launch()` + `browser.new_context()`. This retains Google cookies across sessions for reCAPTCHA v3 trust.

**Key changes per LOD400:**
1. Replace `from playwright.sync_api` with `from patchright.sync_api` (with ImportError guard)
2. Switch to `launch_persistent_context` with configurable profile dir via `SHAKED_BROWSER_PROFILE_DIR` env var
3. Add randomized human-like delays (`random.randint(1500, 3000)` and `random.randint(500, 1500)`)
4. Wrap entire `fetch_listings()` in `try/except Exception` with deterministic `return []` + ERROR log
5. Preserve ALL existing parsing methods unchanged: `_parse_api_item`, `_dom_fallback`, `_detect_vegan`, `_allowed_zips`, `_wg_path_segment`

**Installation in Cowork:**
```bash
pip install patchright && patchright install chromium
```

## DO NOT

- Modify any parsing or filtering methods (`_parse_api_item`, `_dom_fallback`, `_detect_vegan`, `_allowed_zips`, `_wg_path_segment`)
- Modify the `_on_response` callback function body
- Change the reCAPTCHA block detection condition
- Touch any other scraper file (flatfox, homeless)
- Modify `base.py` or any data files
- Add new scrapers or new data sources

## ACCEPTANCE CRITERIA

15 ACs (AC-01 through AC-15) — see LOD400 spec for full details.

## DEPENDENCIES

None — this WP is independent.
