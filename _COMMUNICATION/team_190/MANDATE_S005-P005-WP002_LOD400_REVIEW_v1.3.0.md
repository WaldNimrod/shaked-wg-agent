---
id: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.3.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: LOD400_REVIEW_MANDATE
wp: S005-P005-WP002
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
correction_cycle: 3
supersedes: MANDATE_S005-P005-WP002_LOD400_REVIEW_v1.2.0
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# LOD400 Review Mandate (Round 4) — S005-P005-WP002: Facebook Manual Listing Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | LOD400 Spec Review — Round 4 |
| Work Package | S005-P005-WP002 |
| Label | Facebook manual listing parser — LLM-based Hebrew extraction |
| Track | A |
| Priority | HIGH |
| Correction Cycle | 3 |

## 2. Prior Gate History

| Gate | Result | Date | Notes |
|------|--------|------|-------|
| L-GATE_S Round 1 | BLOCK | 2026-04-15 | F-001..F-005 |
| L-GATE_S Round 2 | PASS | 2026-04-15 | All closed |
| LOD400 v1.0.0 | BLOCK | 2026-04-15 | F-LOD400-001..004 |
| LOD400 v1.1.0 | BLOCK | 2026-04-15 | F-LOD400-005..007 |
| LOD400 v1.2.0 | BLOCK | 2026-04-15 | F-LOD400-008 (rooms not in ScrapedListing) |

## 3. Single Finding Addressed in v1.3.0

| Finding | Severity | Resolution |
|---------|----------|------------|
| F-LOD400-008 | BLOCKING | `ScrapedListing` has no `rooms` field — the dedup pseudocode referenced a non-existent attribute. **Resolution:** Removed rooms from dedup criteria entirely. Cross-source dedup now uses `location_text + price(±10%)` — the two dimensions actually available on ScrapedListing. LOD200 v1.3.0 amended to match (dedup criteria updated from "city+neighborhood+price+rooms" to "location_text+price(±10%)"). Code, ACs, docstrings, and tests all aligned to the two-dimension match. |

## 4. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP002/LOD400_S005-P005-WP002.md` | **Primary artifact (v1.3.0)** |
| `_aos/work_packages/S005-P005-WP002/LOD200_S005-P005-WP002.md` | Parent LOD200 spec (v1.3.0 — dedup criteria amendment) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper + ScrapedListing (verify `rooms` absent) |
| `data/sources.json` | Source registry |

## 5. Output

**Verdict file:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP002_LOD400_REVIEW_v1.3.0.md`
