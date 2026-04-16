# [L-GATE_B] — Team 10 | S005-P001-WP001

## Context bundle

- Work Package: S005-P001-WP001
- Operating mode: Mode B (Solo Builder)
- Write to: `_COMMUNICATION/team_10/S005-P001-WP001/` (handoff pointer) and canonical artifacts under `_aos/work_packages/S005-P001-WP001/`
- POC date: 2026-04-12
- Environment: local developer workstation (not `waldhomeserver`)

---

## 1. Executive summary

Yad2.co.il rental search is protected by **ShieldSquare** (bot management that redirects through `validate.perfdrive.com`) and **hCaptcha** assets, not only classic Cloudflare HTML. **Plain HTTP clients (`requests`) consistently receive a small “ShieldSquare Captcha” HTML shell** (~16 KB) with HTTP 200, not usable listing data.

**Headless Playwright** sometimes received full search HTML (Hebrew title, ~1.7 MB) in an early run, but **subsequent runs from the same environment returned the same captcha shell as `requests`**. A **mobile User-Agent + `mobile=1` query** path briefly returned an alternate Hebrew title and larger HTML in one run; later runs again hit the captcha wall. This **non-determinism** is the critical finding: feasibility depends on **session reputation, fingerprint, and bot-score**, not only request rate.

**Verdict (mandatory):** **`PARTIALLY_FEASIBLE`** — browser automation can reach real pages, but reliability is **not production-grade** without additional controls (persistent browser profile, human-in-the-loop for captchas, residential IP / rate discipline, or an official data channel).

**Recommended next step:** Proceed to **S005-P001-WP002** only with an architecture that assumes **fragile ingestion** (isolated `connectors/yad2/`, normalizer gateway, circuit breakers) and parallel **business/legal** track to validate **official/partner data access**; do **not** treat HTML scraping as a stable long-term sole source.

---

## 2. Scraping method testing

### 2.1 Methods exercised (POC scripts in `poc/`)

| Method | Result (aggregate) | Challenge / wall | Data received |
|--------|----------------------|------------------|---------------|
| `requests.get` (multiple User-Agents) | **Blocked for data** | ShieldSquare captcha page (HTTP 200) | ~16 KB captcha HTML only |
| Playwright Chromium headless (default) | **Intermittent** | Often ShieldSquare captcha title; occasionally full SERP | Full HTML when wall absent; captcha HTML when present |
| Playwright + `playwright-stealth` (`Stealth().apply_stealth_sync`) | **No improvement** in failed runs | Same captcha shell as other blocked cases | ~19 KB captcha HTML |
| Playwright + iPhone UA + `mobile=1` | **Intermittent success** in one matrix run | Less often blocked than desktop in that snapshot | ~1.1 MB HTML when successful |
| Selenium + `undetected-chromedriver` | **Failed in this environment** | `SessionNotCreatedException` (Chrome/driver session) | None |
| Cookie replay (`requests` + `Cookie` header) | **Not executed** | N/A | Skipped — no cookie material supplied (see `poc/cookies.txt` pattern, gitignored) |

**Interpretation:** User-Agent rotation on raw HTTP is insufficient. Stealth plugins did not outperform default Playwright when the wall engaged. Mobile profile is a useful **experiments knob** but not a guaranteed bypass.

### 2.2 Detection stack observed

- **ShieldSquare** — redirect/validation host `validate.perfdrive.com` appeared in network capture.
- **hCaptcha** — `newassets.hcaptcha.com` Hebrew i18n JSON loaded when the challenge UI initialized.
- **“Cloudflare” column in matrix** — POC scripts label both Cloudflare-like HTML and ShieldSquare/captcha walls under a single “challenge” boolean for brevity; the economically relevant statement is **automated wall**, not a single vendor name.

### 2.3 Non-determinism log (same scripts, same URLs)

- First `method_matrix.py` execution: Playwright default returned a long Hebrew search title and ~1.75 MB body (apparent real SERP).
- Later executions minutes apart: Playwright default matched the ShieldSquare captcha page, consistent with `requests`.

**Implication:** Rate limits per minute are **not** the sole gating variable; **fingerprint / session / IP reputation** dominate.

---

## 3. API endpoint and machine-readable surface

### 3.1 `robots.txt` (fetched 2026-04-12)

- Declares sitemap indexes including `https://www.yad2.co.il/sitemaps/sitemap-index.xml` and regional real-estate sitemaps.
- **Explicit `Disallow: /api/`** — programmatic use of private JSON APIs (if discovered) is **contrary to robots policy** and typically ToS-sensitive even when technically reachable.
- Many parameterized filter URLs are disallowed for indexing (e.g. `price=`, `floor=`), which affects SEO-style crawling patterns, not necessarily browser sessions.

### 3.2 Network observation (single navigation, `poc/network_capture.py`)

Representative excerpt committed as [`samples/network_observation_excerpt.json`](samples/network_observation_excerpt.json). Full raw log is gitignored under `poc/network_capture.json`.

**Candidate “API” patterns:** No stable public JSON feed was captured in the successful-precondition runs; when the wall activated, traffic centered on **validation and captcha** endpoints rather than listing payloads.

### 3.3 Community / desk research (secondary)

Public GitHub projects and marketplace scrapers (e.g. Apify actors naming “Yad2”) exist, which implies **others solve this with browser automation or managed proxies** — also implying **ongoing breakage** when anti-bot rules change. No durable, officially documented open API for third-party rental aggregation was identified in this POC window (verify with Yad2 commercial/broker offerings before product reliance).

---

## 4. Rate limits and blocking

### 4.1 Empirical HTTP probe (`poc/rate_limit_probe.py`)

Configuration: **4 s** between sequential `requests`, desktop UA, default rent search URL.

- **First request:** HTTP 200, **bot wall detected** on body (`ShieldSquare`/captcha HTML, ~16 KB) — probe **stopped immediately** by design once a wall is detected.
- **Earlier probe version** (bug: wall not detected) showed **15/15** HTTP 200 responses of identical small byte count — demonstrating that **“200 OK” does not mean “listings available.”**

### 4.2 What could *not* be safely measured here

- **Requests/min before hard IP block** — not stress-tested (polite-POC constraint; risk of impact to egress IP).
- **Block duration** — not observed to completion; captcha path requires interactive solve not performed in automation.
- **Residential vs datacenter IP comparison** — not A/B tested (no residential proxy attached to this POC).
- **Cookie clearing vs IP rotation** — not systematically tested.

**Qualitative expectation from industry patterns:** datacenter / cloud IPs trigger challenges faster; residential IPs may improve odds but **do not constitute permission** and can still be rate-limited or challenged.

---

## 5. Data schema mapping (to `ScrapedListing`)

Source dataclass: [`shaked_wg_agent/scrapers/base.py`](../../../shaked_wg_agent/scrapers/base.py) — `ScrapedListing`.

### 5.1 Field mapping (Yad2 → `ScrapedListing`)

| Yad2-style field (illustrative) | `ScrapedListing` field | Notes |
|---------------------------------|-------------------------|-------|
| Listing token / ad id | `source_listing_id` | Stable primary key candidate |
| Search URL used | `source_search_url` | Required for traceability |
| Headline / property type + rooms + city | `title` | Often Hebrew; build concise title in normalizer |
| Monthly rent (ILS) | `price_chf` | **Mismatch** — today’s model uses CHF ints; Israel needs **NIS** or a currency-neutral field (S005-P001-WP002) |
| Entry date / “מיידי” | `available_from` | Parse Hebrew date phrases |
| City, street, neighborhood | `location_text`, `district` | May need splitting heuristics |
| Description | `summary` | Preserve UTF-8; watch RTL markers |
| Canonical item URL | `direct_url` | Prefer HTTPS `www` link |
| Broker / roommate hints | `roommate_signal`, `vegan_signal` | Optional; often empty for standard rentals |
| Photos / lat-long | *none* | Extend via sidecar JSON or future schema |

### 5.2 Hebrew and encoding

- Expect **UTF-8** responses; store Python `str` as-is.
- UI rendering must respect RTL; avoid stripping Hebrew punctuation.

### 5.3 Samples

Because live JSON extraction was blocked in most automated runs, **six synthetic examples** with explicit provenance are in [`samples/`](samples/) (`listing_synthetic_01.json` … `06`, plus [`provenance.json`](samples/provenance.json)). [`samples/extraction_meta.json`](samples/extraction_meta.json) records a **failed** `extract_samples.py` run (captcha title, zero items).

---

## 6. Legal / ToS assessment (non-legal advice)

**Disclaimer:** This is a technical-product risk note, **not** legal counsel. Engage qualified Israeli counsel before large-scale or commercial scraping.

### 6.1 Terms of Service

An automated fetch of the public terms page timed out from this environment; **do not rely on this POC for verbatim ToS text.** Classified marketplaces typically restrict **automated access**, **bulk extraction**, and **commercial reuse** of listings. Treat systematic scraping as **high contractual risk** until counsel reviews the then-current Hebrew ToS and privacy policy.

### 6.2 Israeli law (orientation only)

- **Computer Law (Penal Law provisions on computers — commonly referenced as “Computer Law 5755-1995” in Israeli discourse)** addresses **unauthorized access** and interference with computer systems. Whether **public HTTP GET of listings** falls within prohibited “access” is **fact-specific** (volume, circumvention of technical barriers, credential use, impact on systems).
- **Privacy Protection Law** may apply when processing **personal data** (e.g. phone numbers, names). Minimize storage; prefer aggregated/archival policies aligned with project privacy posture.

### 6.3 Enforcement / practical risk

- **Technical:** Anti-bot stack is active; sustained automation may trigger blocking without any court action.
- **Civil/commercial:** Large platforms may pursue **ToS-based** remedies against commercial scrapers; **this POC did not perform legal docket research.**

**Risk classification for unsanctioned scraping at scale:** **HIGH** (contract + potential IP/legal exposure + technical instability). For a **small personal research agent** with polite frequency and local execution, residual risk differs — still **not zero**.

### 6.4 Official / partnership APIs

No **public, documented open API** for third-party rental aggregation was confirmed here. Investigate **Yad2 business / publisher / broker** programs if commercial continuity matters.

---

## 7. Maintenance burden (estimate)

**Community signal:** Scrapers for heavily protected sites commonly require **weekly to monthly** adjustments after front-end or bot-defense updates.

**For Yad2 specifically (this POC + ShieldSquare/hCaptcha observations):**

- **Estimated engineering:** **4–8 hours/month** for a single maintainer under active defense changes, assuming Playwright-based ingestion with tests and no major legal escalation workstream.
- **Spike risk:** Anti-bot vendor rule changes can cause **multi-day outages** until a new evasion or official channel is arranged.

---

## 8. Feasibility verdict (mandatory)

### **`PARTIALLY_FEASIBLE`**

**Rationale:** A **browser-based** approach can still deliver HTML/embedded state **when** the bot score permits, but **plain HTTP is unsuitable**, behavior is **volatile**, and **legal/ToS risk remains material** for anything beyond tightly scoped personal use.

### Recommended actions by outcome (this verdict)

1. **Engineering (S005-P001-WP002):** Design `connectors/yad2/` as an **isolated, replaceable** module with a **normalizer** to `ScrapedListing` (currency + NIS handling), health checks, and explicit failure modes when captcha is detected.
2. **Operations:** Prefer **low frequency**, **single interactive browser profile** for development; avoid cloud datacenter IPs for production polling without understanding block risk.
3. **Product/legal:** Parallel track to **contact Yad2** (business development) about licensed feeds or partner programs before scaling.
4. **Alternative sources:** Keep **Homeless.co.il** and other S005 research targets as diversification per milestone strategy.

---

## 9. POC artifact index

| Path | Purpose |
|------|---------|
| [`poc/method_matrix.py`](poc/method_matrix.py) | Method comparison runner |
| [`poc/network_capture.py`](poc/network_capture.py) | One-shot response URL logging |
| [`poc/rate_limit_probe.py`](poc/rate_limit_probe.py) | Sequential polite HTTP probe |
| [`poc/selenium_uc_test.py`](poc/selenium_uc_test.py) | Optional undetected-chromedriver smoke test |
| [`poc/extract_samples.py`](poc/extract_samples.py) | Attempt embedded JSON extraction (writes `batch_listings_live_attempt.json` when run — gitignored) |
| [`poc/requirements-poc.txt`](poc/requirements-poc.txt) | Extra Python deps for POC |
| [`samples/`](samples/) | Synthetic listings + network excerpt + extraction meta |

---

*End of report — Team 10 | 2026-04-12*
