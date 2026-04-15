# Team 190 Re-Validation Routing — S002 LOD400 v1.1.1 (Targeted)
# Drafted by: Team 110 (shaked_arch / Claude Code)
# Authority: Team 00 (Nimrod)
# To: Team 190 (shaked_val / OpenAI)
# Date: 2026-04-12
# Gate: L-GATE_S (Spec + Authorization — Targeted Re-Validation)

---

## Context

Your v1.1.0 re-validation returned FAIL (targeted) with 2 remaining BLOCKING items in WP003 and WP004. Team 110 has patched both. Only WP003 (v1.1.1) and WP004 (v1.1.1) changed; the other three WPs remain at v1.1.0.

---

## Changes (v1.1.0 → v1.1.1)

### BLOCKING fix 1: WP003 — profile_id not applied end-to-end in POST /search

**Finding:** `resolve_profile_id()` was called but the result was discarded — `load_config()` was called with no args, and `run_scan(cfg=cfg)` used the default profile regardless of request input.

**Fix applied in S002-P002-WP001 LOD400 v1.1.1:**
- §2.4.2 `POST /search`: Changed `cfg = load_config()` → `cfg = load_config(profile_id)`. Added implementation note explaining the full resolution chain.
- §2.4.3 `GET /listings`: Added profile-aware filtering. When `profile_id` is provided without `city_id`, the profile's `city_id` is resolved via `load_config(profile_id)`. Added `profile_id` filter against listing's `profile_id` field.
- Updated implementation notes to document profile-driven behavior.

### BLOCKING fix 2: WP004 — LOD300↔LOD400 auth contract drift

**Finding:** LOD300 §5 defined `auth_middleware(request, call_next)` (ASGI middleware-stack signature), but LOD400 uses `auth_middleware(request)` (FastAPI dependency). Contract drift between LOD levels.

**Fix applied:**
- **LOD300 v2.1.0** (S002-P002-WP002): Updated §5 interface contract from `auth_middleware(request, call_next)` to `auth_middleware(request)` with description reflecting router dependency pattern.
- **LOD400 v1.1.1** (S002-P002-WP002): Added "LOD300→LOD400 Refinement Note" section before §2.1, explicitly documenting the alignment between LOD levels. Renamed file from `middleware.py` to `auth.py` and function from `auth_middleware` to `verify_api_key` to eliminate middleware/dependency terminology confusion.

---

## Re-Validation Scope

Only 2 files changed. Read:

| # | WP ID | File | Version | Key sections |
|---|-------|------|---------|-------------|
| 1 | S002-P002-WP001 | `_aos/work_packages/S002-P002-WP001/LOD400_S002-P002-WP001.md` | v1.1.1 | §2.4.2 (POST /search), §2.4.3 (GET /listings) |
| 2 | S002-P002-WP002 | `_aos/work_packages/S002-P002-WP002/LOD400_S002-P002-WP002.md` | v1.1.1 | Refinement Note, §2.1 |

Also verify parent LOD300 alignment:
| 3 | S002-P002-WP002 | `_aos/work_packages/S002-P002-WP002/LOD300_S002-P002-WP002.md` | v2.1.0 | §5 (interface contract) |

---

## Validation Checklist (targeted)

1. **Cross-check #15 (API profile_id):** Verify `POST /search` now passes resolved `profile_id` to `load_config()` and that `GET /listings` filters by `profile_id` when provided.
2. **Cross-check #18 (LOD300→LOD400 traceability):** Verify WP004 LOD400 `verify_api_key(request)` dependency signature now matches LOD300 v2.1.0 §5 `auth_middleware(request)` contract.
3. **Per-doc check #3 (technical spec):** Verify both WPs are now executable without builder design decisions.

---

## Output

Write to:
```
_archive/S002-P001-WP001/S002_LOD400_REVALIDATION_RESULT_v1.1.1.md
```

Reference prior findings and state RESOLVED or STILL OPEN.

---

## Pre-conditions

AOS governance: **12 PASS / 0 FAIL** (verified 2026-04-12 after v1.1.1 edits).

---

*Re-validation routing drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S002 LOD400 v1.1.1 | 2026-04-12*
