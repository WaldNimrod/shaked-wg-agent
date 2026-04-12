# Team 00 Decisions — Israel Market Expansion Strategy
## Date: 2026-04-12
## Authority: Team 00 (Nimrod)
## Status: FINAL

---

## Context

Israel market research (S002-RND-WP001) is complete. 11 Israeli rental platforms mapped, 7+ competitors analyzed. Research findings:
- Yad2 dominant (aggressive Cloudflare anti-bot)
- Facebook Groups highest WG velocity (scraping legally/technically problematic)
- Homeless.co.il closest to WG-Gesucht (easiest entry point)
- Multiple cheap/free competitors: Jeremy (29.99 ILS/week), TheFinder (free Telegram), Realta (free+AI)
- NO Israeli service offers scoring/matching — all are alert-only

Team 00 has reviewed the findings and made the following strategic decisions for the Israel expansion.

---

## Decision 1 — LOW_BUSINESS_POTENTIAL

**Finding:** Many parallel options at very low prices exist in the Israeli market. The business potential is small.

**Ruling: PROCEED WITH AWARENESS**

**Implications:**
- Accept small-market risk. Do not over-invest in infrastructure.
- Differentiation through scoring/matching is our only defensible advantage.
- Keep operational costs minimal — no dedicated servers for Israel initially.
- Revisit business case after first region launch with real usage data.

**Routing:** Captured as S005 milestone-level risk. No dedicated WP.

---

## Decision 2 — EXPAND_BEYOND_ROOMMATES

**Finding:** The roommate/WG niche is good but Israel is a small country with competition. Limiting to roommates only would reduce volume to unsustainable levels.

**Ruling: ALL RENTAL TYPES IN SCOPE**

**Implications:**
- Search scope expands from WG/shared apartments to ALL rental listings (apartments, rooms, sublets).
- Roommate scoring/matching retained as unique competitive advantage (no IL service does this).
- `ScrapedListing` and scoring model must handle both full apartments and shared rooms.
- Roommate-specific fields (roommate_signal, vegan_signal) remain — they add value when present, ignored when absent.

**Routing:** Scope definition for all S005 WPs.

---

## Decision 3 — GEOGRAPHY_PARDES_HANNA_REGION

**Finding:** Research recommended Tel Aviv as first city (highest volume). Team 00 overrides this.

**Ruling: START FROM LOCAL COMMUNITY — PARDES HANNA REGION**

**Coverage definition:**
- **Center:** Pardes Hanna-Karkur
- **South boundary:** North of Netanya (Netanya EXCLUDED)
- **North boundary:** South of Haifa (Haifa EXCLUDED)
- **East boundary:** West of Afula (Afula EXCLUDED)
- **Included:** All settlements/towns in the defined area (Zikhron Ya'akov, Binyamina, Caesarea, Or Akiva, Hadera, etc.)

**Strategic rationale:**
- Counter-intuitive entry — lower competition, personal knowledge of the area
- Local community validation before scaling to major cities
- Simpler initial scope (fewer listings, faster iteration)

**Implications:**
- City definition will be a regional bounding box, not a single city
- Settlement-based geography (Israel does not use zip codes the same way as Switzerland)
- Lower listing volume expected — acceptable given Decision 1

**Routing:** S005-P002-WP001

---

## Decision 4a — YAD2_ARCHITECTURAL_SEPARATION

**Finding:** Yad2 is the dominant Israeli rental platform. It is behind Cloudflare with aggressive anti-bot measures. It will require constant maintenance and updates.

**Ruling: SEPARATE INDEPENDENT MODULE WITH NORMALIZER GATEWAY**

**Implications:**
- Yad2 connector will NOT be a standard `BaseScraper` subclass
- Dedicated subpackage: `shaked_wg_agent/connectors/yad2/` (or similar)
- Normalizer gateway converts Yad2-specific data to `ScrapedListing` at the integration boundary
- The connector is expected to be dynamic — frequent updates as Yad2 changes its defenses
- Track B required — needs LOD300 design for the normalizer API contract

**Routing:** S005-P001-WP002 (BLOCKED by S005-P001-WP001 POC results)

---

## Decision 4b — YAD2_POC_IMMEDIATE

**Finding:** Yad2 feasibility is the single biggest unknown. All architecture decisions depend on knowing what's technically possible.

**Ruling: IMMEDIATE POC — TEAM 20 ACTIVATION**

**Priority: URGENT — gates all downstream product decisions**

**POC scope:**
1. Test multiple scraping methods (requests, Playwright, Selenium, stealth plugins)
2. Research official and unofficial rate limits and restrictions
3. Deep research on anti-bot measures (Cloudflare challenge types, fingerprinting, IP blocking)
4. Document what triggers blocking and how to prevent it
5. Attempt to fetch 5-10 sample listings with field mapping
6. Research undocumented API endpoints (mobile app traffic, RSS feeds)
7. Legal/ToS assessment

**Routing:** S005-P001-WP001 — assigned to shaked_build (Team 20), immediate activation

---

## Decision 5 — FACEBOOK_AGENT_EVALUATION

**Finding:** Facebook Groups are a major source for Israeli rental listings (especially roommate/WG posts). Scraping is technically difficult and legally risky.

**Ruling: EVALUATE BROWSER AGENT OPTION INCLUDING COSTS**

**Evaluation scope:**
- Feasibility of headless browser agent for FB group monitoring
- Cost analysis: compute (Playwright server), proxy costs, anti-detection tools
- Legal/ToS risk assessment
- Alternative approaches: manual curation, Meta API (if available), community partnerships
- Go/no-go recommendation with cost projection

**Routing:** S005-P003-WP001

---

## Decision-to-WP Routing Summary

| Decision | WP(s) | Priority |
|----------|--------|----------|
| D1: Low business potential | S005 milestone risk | — |
| D2: All rental types | S005 scope | — |
| D3: Pardes Hanna region | S005-P002-WP001 | Normal |
| D4a: Yad2 architecture | S005-P001-WP002 | Normal (blocked) |
| D4b: Yad2 POC | S005-P001-WP001 | **URGENT** |
| D5: Facebook agent | S005-P003-WP001 | Normal |

---

*Team 00 — Nimrod | 2026-04-12*
