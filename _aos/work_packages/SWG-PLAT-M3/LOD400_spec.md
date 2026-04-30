# LOD400 — SWG-PLAT-M3 — wgzimmer scraper recovery
**Date:** 2026-04-30
**Author:** sonnet_sub_agent (dispatched by team_110)
**WP:** SWG-PLAT-M3
**Type:** LOD400_SPEC

---

## Changes Required

### 1. `shaked_wg_agent/scrapers/wgzimmer_pw.py`

#### Old (broken) approach
- `_API_URL_FRAGMENT = "img.wgzimmer.ch"` — intercepts responses from image CDN
- `_on_response` handler collects JSON from `img.wgzimmer.ch` — but that API returns HTTP 401 (Magnolia CMS image management, not listings)
- DOM fallback uses `li.search-result-entry` — this CSS class does not exist in the page CSS or HTML

#### New (correct) approach
- Remove the API interception entirely
- Add correct Playwright flow:
  1. Navigate to canton URL (shows search form)
  2. Execute `submitForm()` via `page.evaluate("submitForm()")` — this triggers reCAPTCHA v3 and submits the POST form
  3. Wait for navigation to complete (`page.wait_for_load_state("networkidle")` or `domcontentloaded` + explicit wait)
  4. Check for reCAPTCHA block in resulting page
  5. Parse resulting HTML with `_dom_parse_results(page)`
- Correct DOM selectors (confirmed from CSS analysis):
  - Primary: `#content ul.list li.search-mate-entry`
  - Fallback 1: `#content ul.list li` (excludes header)
  - Fallback 2: `li[class*='search-mate-entry']`
  - Fallback 3: `li[class*='search-mate']`
- Content extraction from listing item:
  - URL: `a[href]` (the `<a>` wrapping the entire item)
  - Title/description: `.state` text (or `.state h3` if present)
  - Price: `.cost` text
  - Available-from date: `.from-date` or `.searchMateFormFromDate` text
  - Location/city: `.state .wgCity` or inferred from canton

#### Probe Evidence
```
HTTP GET https://www.wgzimmer.ch/en/wgzimmer/search/mate/ch/baselstadt.html
  → 200, 34130 chars, Content-Type: text/html;charset=UTF-8
  → Contains: "The processing of the request was stopped by Google reCaptcha"
  → Contains: <form id="searchMateForm" action="/en/wgzimmer/search/mate.html" method="post">
  → Contains: grecaptcha.execute(siteKey, {action: '...submitForm'})

HTTP POST https://www.wgzimmer.ch/en/wgzimmer/search/mate.html (empty reCAPTCHA token)
  → 200, but body contains: "The processing of the request was stopped by Google reCaptcha"
  → No listing items in response

img.wgzimmer.ch/.rest/v1/baselstadt
  → 401, Magnolia CMS login required (image management CMS, not listings)

CSS analysis: #content ul.list li.search-mate-entry { height:90px; ... }
  Confirmed: listings use class "search-mate-entry" not "search-result-entry"
```

#### reCAPTCHA disposition
Playwright's Chromium can execute `grecaptcha.execute()` as the browser has access to the DOM and the reCAPTCHA script is already loaded. reCAPTCHA v3 is invisible and does not present a puzzle — it issues a token based on a behavioral score. Headless browsers typically receive a score of ~0.1 (vs. ~0.9 for real users). Sites configure a threshold; wgzimmer has historically allowed headless access. If the score is below threshold, the POST response will contain the block message.

**Detection strategy in code:** After `submitForm()` and navigation, check if page content contains `"reCaptcha"` or `"stopped by"`. If blocked → log WARNING with details → return `[]`. Do NOT retry aggressively; do NOT spoof user signals.

---

### 2. `shaked_wg_agent/scrapers/wgzimmer.py`

Add deprecation notice at top. The class has a runtime bug: uses `price_chf=price` which does not match the `ScrapedListing` dataclass field `price`. This class is non-functional as-is and should not be invoked.

---

### 3. `tests/test_scrapers/test_wgzimmer.py` (new file)

#### Test strategy: mock-only, no live network

**Fixture:** `tests/fixtures/scrapers/wgzimmer_search_page.html`
A minimal realistic HTML page matching the confirmed structure:
```html
<html>
  <body>
    <div id="content">
      <ul class="list">
        <li class="search-mate-entry">
          <a href="/en/wgzimmer/mate/ch/baselstadt/2026-04-01-123456.html">
            <div class="state"><h3>Helles Zimmer Gundeli</h3></div>
            <div class="cost">800 CHF</div>
            <div class="from-date">01.04.2026</div>
          </a>
        </li>
      </ul>
    </div>
  </body>
</html>
```

**Test cases:**
1. `test_parse_listing_page` — Given HTML fixture, `_dom_parse_results` returns ≥1 listing with correct title/price/URL
2. `test_zero_results_logs_warning` — Given an empty results page, returns `[]` and emits a `WARNING` log
3. `test_fetch_listings_returns_empty_on_recaptcha_block` — Mock `page.content()` to return reCAPTCHA block page → returns `[]`
4. `test_fetch_listings_invokes_submit_form` — Mock Playwright page, verify `page.evaluate("submitForm()")` is called
5. `test_dom_fallback_selectors` — Test fallback selector chain when primary selector finds nothing

All tests use `unittest.mock.patch` on `playwright.sync_api.sync_playwright`. No live network calls.
