# [L-GATE_B] — Team 10 | Israel ecosystem research plan | v1.0.0

## Context bundle

- Work Package: S005-P001-WP001 (follow-on research; does not replace [`S002-RND-WP001`](../S002-RND-WP001/LOD200_S002-RND-WP001.md))
- Operating mode: Mode B (Solo Builder)
- Date: 2026-04-12
- Prerequisite read: [`FINDINGS_REPORT_v1.0.md`](FINDINGS_REPORT_v1.0.md)
- Baseline mapping (do not duplicate): [`../S002-RND-WP001/LOD200_S002-RND-WP001.md`](../S002-RND-WP001/LOD200_S002-RND-WP001.md)

---

## 1. Goals

1. **Expand** the catalog of **third-party and alternative** acquisition paths for Israeli rental listings — **without duplicating** the baseline platform list in S002-RND-WP001; instead **start from that list** and add **net-new** rows (vendors, APIs, communities, data products).
2. **Map commercial suppliers** (data marketplaces, proxy/scraper-as-a-service, Israeli products) with **limitations and cost model** (public list price or “contact sales”) and **contractual risk** notes.
3. **Evaluate a “Yad2-safe” product direction:** surface **minimal metadata** (e.g. title/snippet/area/price if obtainable lawfully) plus **deep link** and **in-product guidance** so the user completes discovery **on the source site** in compliance with policy — **subject to legal review** (database rights, ToS, hotlinking).

---

## 2. Non-duplication rule

- **Canonical first-pass mapping:** `S002-RND-WP001` LOD200 §3.1.1–§10 (11 platforms + parameters).
- Phase 2 adds **new rows only** in [`EXTENDED_SOURCE_CATALOG_v1.0.yaml`](EXTENDED_SOURCE_CATALOG_v1.0.yaml) (seed structure below) with `extends_baseline: true` where applicable.
- If a platform was already in RND, **do not copy** full parameter tables here — **reference** RND and add only **delta** (e.g. new vendor wrapping that platform).

---

## 3. Workstreams

### 3.1 Extended source catalog (large initial list, filter later)

**Output:** `EXTENDED_SOURCE_CATALOG_v1.0.yaml` in this directory (machine-readable; grows over time).

**Categories to add (examples — not exhaustive):**

| Category | Examples of what to list |
|----------|----------------------------|
| Commercial data / scraper marketplaces | Apify actors, Bright Data datasets, Oxylabs, Zyte, etc. |
| Israeli-specific bots / Telegram / WhatsApp | Public invite links, bot names (no scraping commitment) |
| Niche sites | Local forums, `reva.co.il`-class, student bboards not in RND |
| RSS / feeds / official partner programs | If any platform exposes sanctioned feeds |
| “Aggregator” apps | Any app that legally aggregates — partnership target |

**Per row (minimum fields):** `id`, `name`, `url`, `category`, `relation_to_baseline` (new | extends_yad2 | …), `data_mode` (api | partner | manual | unknown), `legal_notes`, `quality_tier` (TBD), `last_reviewed`.

**Process:** Brainstorm **max breadth** first; **scoring/filtering** in a later pass (separate rubric).

### 3.2 Supplier mapping (section 2 of mandate)

**Output:** Section in this file + table in [`SUPPLIER_MATRIX_v1.0.md`](SUPPLIER_MATRIX_v1.0.md).

**Per supplier:**

| Column | Content |
|--------|---------|
| Supplier | Name |
| Product | Dataset / actor / API |
| Pricing model | per-1k, monthly seat, enterprise quote |
| **Limitations** | GEO, rate, ToS, residential IP only, no Yad2 guarantee, etc. |
| **Yad2 relevance** | Explicit support vs. generic scraper |
| Risk | LOW / MED / HIGH (contractual + operational) |
| Evidence | URL to pricing page (date fetched) |

**Note:** Prices change — record **as-of date**; prefer primary sources.

### 3.3 “Referral-only Yad2” direction (מידע מינימלי + הפניה)

**Product concept (research, not implementation here):**

- **Card** in UI: short **title**, optional **neighborhood/city**, **price** *only if* from a source we are confident we may display (legal sign-off).
- **Primary CTA:** “Open on Yad2” → `direct_url`.
- **Copy:** short Hebrew explanation — המודעה המלאה והעדכנית באתר המקור בלבד; אין שכפול מסחרי של מאגר יד2.

**Technical options to evaluate (with counsel):**

1. **User-pasted URLs** / bookmarks — no scrape.
2. **Official sitemap / permitted indexing** — what reuse is allowed for titles/snippets (if any).
3. **Licensed feed** from Yad2 or reseller — only if contract explicitly permits product use.
4. **No automated bulk extraction** from Yad2 HTML — aligns with Team 00 stance.

**Deliverable:** subsection in [`SUPPLIER_MATRIX_v1.0.md`](SUPPLIER_MATRIX_v1.0.md) or standalone `YAD2_REFERRAL_UX_LEGAL_CHECKLIST_v1.0.md` after first legal pass.

---

## 4. Success criteria (Phase 2 research)

- [ ] **SC-A:** Extended catalog contains **≥ 30 net-new rows** (beyond the 11 baseline platforms, counting vendors/communities/channels separately) OR documented reason for smaller set.
- [ ] **SC-B:** Supplier matrix covers **≥ 5** distinct commercial suppliers or pricing models.
- [ ] **SC-C:** Referral-only Yad2 path documented with **open legal questions** list (not answered by engineering).
- [ ] **SC-D:** No duplicated parameter tables from S002-RND-WP001 — **references + deltas** only.

---

## 5. Timeline & owners (proposal)

| Milestone | Suggested owner | Notes |
|-----------|-----------------|-------|
| Catalog seed + supplier matrix draft | Team 10 / Builder | Desk research + primary URLs |
| Legal review of referral model | Team 00 + external counsel | Out of scope for builder to “approve” |
| Architect alignment | Team 110 | WP boundaries, connector vs. referral |

---

## 6. Files created by this plan

| File | Role |
|------|------|
| [`EXTENDED_SOURCE_CATALOG_v1.0.yaml`](EXTENDED_SOURCE_CATALOG_v1.0.yaml) | Living catalog (YAML) |
| [`SUPPLIER_MATRIX_v1.0.md`](SUPPLIER_MATRIX_v1.0.md) | Supplier pricing/limitations |
| `YAD2_REFERRAL_UX_LEGAL_CHECKLIST_v1.0.md` | Optional after first review |

---

*End — ISRAEL_SOURCES_RESEARCH_PLAN_v1.0.0*
