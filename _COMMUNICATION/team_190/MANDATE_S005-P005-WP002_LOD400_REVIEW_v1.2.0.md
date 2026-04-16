---
id: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.2.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: LOD400_REVIEW_MANDATE
wp: S005-P005-WP002
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
correction_cycle: 2
supersedes: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.1.0
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# LOD400 Review Mandate (Round 3) — S005-P005-WP002: Facebook Manual Listing Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | LOD400 Spec Review — Round 3 (re-validation after Round 2 BLOCK) |
| Work Package | S005-P005-WP002 |
| Label | Facebook manual listing parser — LLM-based Hebrew extraction |
| Track | A |
| Priority | HIGH |
| Correction Cycle | 2 |

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_S Round 1 | BLOCK | 2026-04-15 | team_190 | F-001..F-005 |
| L-GATE_S Round 2 | PASS | 2026-04-15 | team_190 | All findings closed |
| LOD400 Review v1.0.0 | BLOCK | 2026-04-15 | team_190 | F-LOD400-001..004 |
| LOD400 Review v1.1.0 | BLOCK | 2026-04-15 | team_190 | F-LOD400-005..007; F-001/003 partially closed |

## 3. Findings Addressed in v1.2.0

| Finding | Severity | Resolution |
|---------|----------|------------|
| F-LOD400-005 | BLOCKING | Added explicit `rooms` matching to `_is_duplicate()` pseudocode: `float(listing_rooms) == float(ex_rooms)`, both must be non-null. Now matches AC-35 "city + price(±10%) + rooms" exactly. |
| F-LOD400-006 | MAJOR | Amended LOD200 v1.2.0 normative schema: `group_url` and `raw_url` constraints changed from "Valid URL format if present" to "Informational; no runtime validation". LOD400 "stored as-is" now aligns with parent contract. |
| F-LOD400-007 | MINOR | Normalized mode naming: UT-36..41 now reference matrix row names exactly ("API timeout", "Rate limit (429)", "Malformed response", "API error (500)", "All posts fail"). Removed "refusal" and "server error" labels. Unified `parse_rental_post()` signature across §2.1 definition, §2.1 implementation, and §4 API table to include `post_id: str = ""`. |

## 4. Additional Consistency Fixes

- `parse_rental_post()` signature unified: `(text: str, group_name: str = "", post_id: str = "")` across §2.1 initial definition (item 1), §2.1 implementation (item 6), and §4.1 API table
- LOD400 `parent_lod200` reference updated to v1.2.0

## 5. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP002/LOD400_S005-P005-WP002.md` | **Primary artifact (v1.2.0)** |
| `_aos/work_packages/S005-P005-WP002/LOD200_S005-P005-WP002.md` | Parent LOD200 spec (v1.2.0 — URL constraint amendment) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper interface + ScrapedListing |
| `data/sources.json` | Source registry |
| `data/cities/pardes-hanna-region.json` | City config |

## 6. Output

**Verdict file:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP002_LOD400_REVIEW_v1.2.0.md`
