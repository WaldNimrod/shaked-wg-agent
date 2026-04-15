# S002 LOD400 Targeted Re-Validation Result (L-GATE_S, v1.1.1)
**Validator:** Team 190 (shaked_val / OpenAI)  
**Date:** 2026-04-12  
**Gate:** L-GATE_S (Spec + Authorization — Targeted Re-Validation)  
**Overall Verdict:** PASS WITH FINDINGS

## Scope

Targeted re-validation covered only the patched documents:
1. `S002-P002-WP001` LOD400 `v1.1.1` (`§2.4.2`, `§2.4.3`)  
2. `S002-P002-WP002` LOD400 `v1.1.1` (Refinement Note, `§2.1`)  
3. `S002-P002-WP002` LOD300 `v2.1.0` (`§5` interface contract)

Prior baseline used for comparison: `_archive/S002-P001-WP001/S002_LOD400_VALIDATION_RESULT.md` (v1.1.0 re-validation result).

## Targeted Checklist Results

| Check | Result | Evidence |
|------|--------|----------|
| Cross-check #15 (API `profile_id`) | **RESOLVED** | WP003 `§2.4.2` now passes resolved `profile_id` into `load_config(profile_id)` and executes scan with that profile-aware config. WP003 `§2.4.3` now applies profile-aware listing filtering and resolves city via `load_config(profile_id)` when needed. |
| Cross-check #18 (LOD300→LOD400 traceability, auth contract) | **RESOLVED** | WP004 LOD300 `v2.1.0` `§5` now defines dependency signature `auth_middleware(request)`. WP004 LOD400 `v1.1.1` uses the same dependency model and explicitly documents the refinement alignment. |
| Per-doc check #3 (technical spec executable, no design decision gaps) | **PASS WITH FINDINGS** | Both patched WPs are executable. Minor terminology/name ambiguity remains in WP004 (see findings), but no blocking design branch remains. |

## Prior Blocking Findings Status

| Prior Blocking Finding (v1.1.0) | Status | Notes |
|---|---|---|
| WP003: resolved `profile_id` computed but not applied end-to-end | **RESOLVED** | Fixed in WP003 `v1.1.1` route flow and notes. |
| WP004: LOD300↔LOD400 auth signature drift (`request, call_next` vs `request`) | **RESOLVED** | Parent LOD300 contract updated to dependency signature; LOD400 aligned. |

## Non-Blocking Findings

1. **MINOR (WP004 naming consistency):** LOD400 introduces `verify_api_key` naming preference, but acceptance criteria and snippets still center on `auth_middleware`; this is implementable but should be normalized to one canonical symbol name to reduce reviewer/build noise.
2. **MINOR (WP004 file path wording):** LOD400 says auth lives in `api/auth.py`, while LOD300 contract table still references `api/middleware.py`; function contract is aligned, but path naming should be synchronized.
3. **MINOR (terminology hygiene):** Some LOD300 narrative/diagrams still use “middleware pipeline” phrasing. The refinement note already clarifies dependency injection; consider a doc-only cleanup in next patch for lexical consistency.

## Recommendation

**PASS L-GATE_S (targeted).**  
The two previously blocking items are closed. Builder authorization may proceed, with the minor editorial harmonization items handled opportunistically (non-gating).

---

*Targeted re-validation executed by Team 190 (shaked_val / OpenAI) | shaked-wg-agent | S002 LOD400 v1.1.1 | 2026-04-12*
