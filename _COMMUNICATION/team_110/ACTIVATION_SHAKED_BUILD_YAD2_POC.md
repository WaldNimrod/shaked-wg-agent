# Builder Activation — Yad2 POC (S005-P001-WP001)

**from:** Team 110 (Domain Architect)
**to:** shaked_build (Team 20 — Backend Implementation)
**gate:** L-GATE_B entry
**work_package:** S005-P001-WP001
**date:** 2026-04-12
**priority:** URGENT — gates all downstream S005 Israel expansion work

---

## 1. Identity

You are **shaked_build** (Team 20 — Backend Implementation). Your engine is Cursor Composer.
Your scope is **S005-P001-WP001 ONLY** — Yad2 scraping feasibility POC.

## 2. Gate Status

| Gate | Status |
|------|--------|
| L-GATE_E | PASS — Team 00 decisions document authorizes (DECISIONS_ISRAEL_STRATEGY_v1.0.0.md) |
| L-GATE_S | PASS — LOD200 spec approved |
| **L-GATE_B** | **YOU ARE HERE** |

## 3. Mandate

Produce a **feasibility report + POC code** for scraping Yad2.co.il. This is NOT production code — it is a research deliverable that determines whether the Israel expansion can proceed.

**Your output gates every other S005 work package.** Be thorough.

## 4. Tasks

### 4.1 Scraping Method Testing

Test each method and document results in a structured table:

| Method | Status | Cloudflare Challenge | Data Received | Notes |
|--------|--------|---------------------|---------------|-------|

Methods to test:
1. **Plain requests** — `requests.get` with various User-Agent headers
2. **Playwright headless** — default Chromium configuration
3. **Playwright stealth** — with `playwright-extra` stealth plugin or `stealth.min.js`
4. **Selenium undetected** — `undetected-chromedriver`
5. **Mobile web** — mobile User-Agent against m.yad2.co.il
6. **Cookie replay** — curl with cookies from a manual browser session

### 4.2 API Endpoint Research

- Intercept network traffic from Yad2 web/mobile to identify REST/GraphQL endpoints
- Search community resources: GitHub repos, Stack Overflow, Israeli tech forums
- Check: `yad2.co.il/robots.txt`, `yad2.co.il/sitemap.xml`, RSS feeds
- Test any discovered API endpoints with parameters (city, category, price range)
- Document endpoint stability (how often do they change?)

### 4.3 Rate Limit Documentation

**Critical deliverable.** Must include:
- Requests per minute before first challenge appears
- Requests per minute before hard block
- Block duration (minutes? hours? permanent?)
- Recovery behavior (does rotating IP help? clearing cookies?)
- IP-based vs fingerprint-based detection
- Residential proxy effectiveness (test if possible)
- Time-of-day patterns (different limits at different times?)

### 4.4 Data Schema Mapping

For any successfully fetched listings, document field-by-field:
- Hebrew text encoding and handling
- Price format: NIS monthly, with/without utilities
- Location: city ID, neighborhood, street, coordinates
- Listing type: apartment, room, shared, sublet
- Contact info: phone, email, in-app messaging
- Photos: URLs, CDN patterns
- Map each field to `ScrapedListing` dataclass (note gaps)

### 4.5 Legal and ToS Research

- Read and summarize Yad2 Terms of Service (relevant sections)
- Israeli Computer Law 5755-1995 — what applies to scraping?
- Known enforcement: has Yad2 sued or sent C&D to scrapers?
- Official API/partnership program: does it exist? How to apply?
- Provide risk classification: LOW / MEDIUM / HIGH / UNACCEPTABLE

### 4.6 Maintenance Burden

- Community reports on Yad2 scraper breakage frequency
- Estimated hours/month to maintain a working connector
- Comparison: is this sustainable for a small project?

## 5. Deliverables

All placed in `_aos/work_packages/S005-P001-WP001/`:

| Deliverable | Filename |
|-------------|----------|
| Feasibility report | `YAD2_FEASIBILITY_REPORT.md` |
| Sample listings data | `samples/` directory with JSON files |
| POC scripts | `poc/` directory with test scripts |
| Rate limit log | included in feasibility report §3 |

## 6. Feasibility Verdict

Your report MUST end with a clear verdict:

- **FEASIBLE** — reliable scraping method found, sustainable maintenance, acceptable legal risk
- **PARTIALLY_FEASIBLE** — works but with significant limitations (rate limits, maintenance burden, legal gray area)
- **BLOCKED** — no viable scraping method; recommend API/partnership route or cancel

Include a recommended next step for each verdict.

## 7. Constraints

- Do NOT commit POC code to the main codebase
- Do NOT use production server resources for testing
- Do NOT create Yad2 accounts with real personal data
- Be polite to Yad2's servers — use reasonable delays between requests
- If you discover a working API endpoint, do NOT abuse it

## 8. Deadline

**ASAP** — This POC is the critical path for the entire Israel expansion. Every day of delay blocks architecture, geographic definition, and product decisions.

---

*Team 110 — Domain Architect | 2026-04-12*
