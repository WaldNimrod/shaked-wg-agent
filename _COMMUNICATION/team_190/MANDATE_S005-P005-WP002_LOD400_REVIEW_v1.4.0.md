---
id: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.4.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: LOD400_REVIEW_MANDATE
wp: S005-P005-WP002
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
correction_cycle: 4
supersedes: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.3.0
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# LOD400 Review Mandate (Round 5) — S005-P005-WP002: Facebook Manual Listing Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | LOD400 Spec Review — Round 5 |
| Work Package | S005-P005-WP002 |
| Track | A |
| Correction Cycle | 4 |

## 2. Prior Gate History

| Gate | Result | Notes |
|------|--------|-------|
| LOD400 v1.0.0 | BLOCK | F-001..004 |
| LOD400 v1.1.0 | BLOCK | F-005..007 |
| LOD400 v1.2.0 | BLOCK | F-008 (rooms not in ScrapedListing) |
| LOD400 v1.3.0 | PASS_WITH_FINDINGS | F-009 (MINOR: warning path + callsite) |

## 3. Finding Addressed in v1.4.0

| Finding | Severity | Resolution |
|---------|----------|------------|
| F-LOD400-009 | MINOR | (a) Split single `check_llm_config()` warning into two distinct paths: provider-missing check first, then key-missing check — matching matrix rows "No provider" and "No API key" exactly. (b) Callsite now passes `post_id=post_id` to `parse_rental_post()`, matching the function signature. |

## 4. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP002/LOD400_S005-P005-WP002.md` | **Primary (v1.4.0)** |
| `_aos/work_packages/S005-P005-WP002/LOD200_S005-P005-WP002.md` | Parent (v1.3.0) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper + ScrapedListing |

## 5. Output

**Verdict:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP002_LOD400_REVIEW_v1.4.0.md`
