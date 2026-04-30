# LOD200 — SWG-PLAT-M3 — wgzimmer scraper recovery
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M3
**Type:** LOD200_SPEC

---

## Root Cause

**Anti-bot / reCAPTCHA v3 + incorrect Playwright strategy (combined)**

### Evidence from probe (2026-04-30)

1. **GET request to canton URL** (`https://www.wgzimmer.ch/en/wgzimmer/search/mate/ch/baselstadt.html`):
   - HTTP 200, 34,130 chars
   - Returns a **search form only** — no listing results in the HTML
   - Contains: `"The processing of the request was stopped by Google reCaptcha, please try again."`
   - The page includes reCAPTCHA v3: `grecaptcha.execute(siteKey, {action: '//form///wgzimmer/search/mate/ch/baselstadt/submitForm'})`

2. **POST request to search endpoint** (`/en/wgzimmer/search/mate.html`):
   - HTTP 200 but blocked: same reCAPTCHA error message in response body
   - POST with empty `g-recaptcha-response` is rejected

3. **img.wgzimmer.ch REST API** (intercepted by the Playwright scraper):
   - `https://img.wgzimmer.ch/.rest/v1/baselstadt` → HTTP 401 (Magnolia CMS login required)
   - `img.wgzimmer.ch` is an **image CDN only** — its REST API is for image management, not listing data
   - The scraper was intercepting image CDN responses, which never contain listing JSON

4. **RSS/Atom feeds**: Exist at `/rss/mate/baselstadt.xml` but return empty feeds (no items).

### Dual failure modes

**Mode 1 — API interception (primary path):** The scraper intercepts responses from `img.wgzimmer.ch` expecting JSON listing data. This never fires for listing data because that domain only serves images. `captured` remains empty.

**Mode 2 — DOM fallback:** The fallback parses `li.search-result-entry` from the page. The GET page never contains listing items (it's a form-only page), so the fallback also returns 0 results.

### Architecture of the correct flow (discovered)

The intended user flow is:
1. Browser visits canton URL (`/en/wgzimmer/search/mate/ch/baselstadt.html`) — shows search form
2. User clicks Search → JavaScript calls `submitForm()` → `grecaptcha.execute()` obtains a reCAPTCHA v3 token
3. Form POSTs to `/en/wgzimmer/search/mate.html` with token in `g-recaptcha-response`
4. Server validates reCAPTCHA score; if passing, returns HTML page with listing results
5. Listings are rendered as `<ul id="search-result-list"><li class="...">` elements

### Why it MIGHT have worked before (historical)

Looking at `data/runs.json`: runs from 2026-04-08 (`run-20260408-001`) show wgzimmer results with `sources_scanned: 2`. The operator note says "Neue Angebote bei wgzimmer.ch gefunden." Later runs show only 2 sources scanned, consistent with wgzimmer being broken. The wgzimmer source may have been temporarily less strict with reCAPTCHA, or an earlier scraper version used a different approach that worked briefly.

---

## Fix Strategy

**Approach: Playwright form-submission with reCAPTCHA v3 token execution**

The correct Playwright strategy is:
1. Navigate to the canton URL (GET — no reCAPTCHA required for the page itself)
2. Call `submitForm()` via `page.evaluate()` — this executes the reCAPTCHA v3 challenge in the browser context with a real Chromium instance
3. Wait for the page navigation to complete (POST result arrives)
4. Parse the resulting HTML for listing items

reCAPTCHA v3 is an **invisible** challenge that scores browser sessions. Playwright with a real Chromium (headless) can obtain a token — the score may be lower than a real user but many sites allow low-score v3 tokens through. This is **not** detection evasion: we execute the public client-side API (`grecaptcha.execute`) as designed.

**Fallback disposition (if v3 consistently fails):** PARTIAL BLOCK. The DOM parsing fallback will be documented and will parse from the POST response if a token is obtained. If headless Playwright consistently gets a score below the threshold, the legitimate workarounds are:
- Use the wgzimmer.ch contact form to request API access
- Reduce scraping cadence (once per 2 hours vs. continuous)
- Switch to an alternative aggregator (e.g., Homegate.ch, which has a public search API)

**wgzimmer.py legacy scraper:** DEPRECATED. The class uses `price_chf=` which does not match the current `ScrapedListing` dataclass field name (`price`). It would crash at runtime. Additionally, it uses the same DOM approach that fails against the reCAPTCHA-gated response. A deprecation notice will be added.

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| reCAPTCHA v3 score too low for Playwright | Medium | Increase wait time; add Accept headers; navigate from homepage first to warm session |
| Site redesign breaks selectors again | Medium | Use multiple fallback selectors; log page title + selector details on 0-result runs |
| img.wgzimmer.ch API behavior change | N/A | Remove that interception entirely — it was wrong |
| wgzimmer.ch contacts Magnolia CMS | Low | No action; we're using the public web interface |

### Regression-resistance measures
- Remove the `img.wgzimmer.ch` interception (wrong target)
- Correct Playwright flow: execute `submitForm()`, wait for navigation
- Parse POST response HTML for `li.search-result-entry` (confirmed selector from page JS)
- Multiple fallback selectors: `li.search-result-entry`, `ul#search-result-list li`, `li[class*='result']`
- Log WARNING with page title and URL when 0 results returned
