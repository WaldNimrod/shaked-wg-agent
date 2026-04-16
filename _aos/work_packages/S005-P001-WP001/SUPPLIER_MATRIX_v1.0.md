# [L-GATE_B] — Team 10 | Supplier matrix (Israel listing data) | v1.0.0

## Context bundle

- Work Package: S005-P001-WP001
- Parent plan: [`ISRAEL_SOURCES_RESEARCH_PLAN_v1.0.md`](ISRAEL_SOURCES_RESEARCH_PLAN_v1.0.md)
- Date: 2026-04-12
- **Note:** Pricing and limits change — verify on primary sites before purchase.

---

## 1. Purpose

Document **commercial and semi-commercial** paths to obtain **web data** or **infrastructure** relevant to Israeli rental aggregation, with **limitations** and **indicative cost model**. This does **not** constitute a recommendation to bypass any website ToS.

---

## 2. Supplier table (seed — fill `as_of` when validating)

| Supplier | Product / SKU | Pricing model (indicative) | Limitations | Yad2-specific? | Risk | as_of |
|----------|---------------|----------------------------|-------------|----------------|------|-------|
| Apify | Marketplace actors (e.g. search “yad2”) | Pay per compute unit / monthly | Actor quality varies; author may abandon | Often marketed | MED — vendor + target ToS | 2026-04-12 |
| Bright Data | Datasets / Web Scraper IDE | Enterprise quote; self-serve tiers | Contract defines permitted use | Marketing mentions IL real estate | MED–HIGH | 2026-04-12 |
| Oxylabs | Residential proxies | GB-based subscription | Cost; ethical use policy | No — infra only | MED | 2026-04-12 |
| Smartproxy | Residential/datacenter | Monthly plans | Same | No | MED | 2026-04-12 |
| Zyte | Smart proxy + API | Request-based | Automated compliance tooling | Generic | MED | 2026-04-12 |
| ScraperAPI | Managed API | Monthly tiers + free trial | Single vendor SPOF | Generic | MED | 2026-04-12 |
| Nimble | Nimbleway browser API | Quote / tiers | TBD | TBD | TBD | 2026-04-12 |

---

## 3. Yad2 “referral-only” legal checklist (engineering handoff to counsel)

**Goal:** Show users **enough** to decide whether to open Yad2, without committing **unsanctioned bulk scrape**.

| Question | Owner | Status |
|----------|-------|--------|
| Is displaying a **title** scraped from Yad2 HTML permitted, or only user-typed text? | Counsel | Open |
| Is **price** extracted from HTML a separate database right issue? | Counsel | Open |
| Does **deep linking** to `yad2.co.il/item/...` avoid database claims if we store no substantial content? | Counsel | Open |
| Can we use **official** broker / publisher APIs instead? | BD / Team 00 | Open |
| Should referral cards be **user-curated only** (zero automation)? | Product | Open |

**Product pattern (hypothesis):** separate **“External — Yad2”** section in UI; CTA opens browser; in-app text explains that **המידע המלא באתר המקור בלבד**.

---

## 4. Next updates

- Replace `TBD` cells with URLs to price pages and notes from sales calls.
- Add Israeli-local vendors if identified (Hebrew support, ILS billing).

---

*End — SUPPLIER_MATRIX_v1.0.0*
