# WP DB — Canonical `track` and `lod_status` (hub API)

**Status:** CANONICAL (operational KB)  
**Date:** 2026-04-17  
**Related WP (closure reference):** `AOS-V320-WP-NB-HIERARCHY-REMEDIATION`

## Why this exists

Migration **010** relaxes the `work_packages.track` CHECK so domain codes (e.g. `NB`) are valid. The **authorized** create path for L2 is `POST /api/work-packages` → `create_work_package` in `core/modules/management/portfolio.py`.

## Rules (do not regress)

1. **`track`** from the request body must be written to the column **`work_packages.track`**, not to `stage_id` or any legacy alias.
2. **`lod_status`** must be written to **`work_packages.lod_status`** (same function).
3. **`stage_id` / `program_id`** on create may remain **NULL** unless a product-specific flow explicitly sets program linkage.
4. **L2 project detail** (`dashboard_service.build_project_detail`) must read **`w.lod_status`** and **`w.track`** — not `program_id AS lod_status` / `stage_id AS track`.

## Verification (BUILD_TECH / QA)

- After create, `SELECT track, lod_status FROM work_packages WHERE id = …` matches the API body for those fields.
- `validate_aos.sh` hub run: expect **20 PASS** on baseline checks; checks **21–23** may **SKIP** on hub depending on `active_modules` / advisory wiring.

## `validation_tiering` metadata convention (ADR053 §7)

Separate from the DB columns above, `metadata.yaml` carries a **file-side** `validation_tiering` block declaring the independence tier per gate (read by `validate_aos.sh` Check 49 — advisory):

```yaml
validation_tiering:
  matrix_ref: governance/directives/ADR053_TIERED_VALIDATION_MODEL_v1.0.0.md
  gates:
    L-GATE_<NAME>: {tier: 1|2, canonical_cross_engine: false|true, engine: <engine_id or TBD>}
escalation:            # only when ADR053 §5 fires
  triggered: true
  reason: "<why>"
  extra_tier2_gates: [L-GATE_BUILD, ...]
```

- **Tier 1** = functional (fresh-context adversarial sub-agent; `canonical_cross_engine: false`).
- **Tier 2** = cross-engine (distinct vendor/model_family per ADR046 §2.5; `canonical_cross_engine: true`).
- Decisive gate is Tier-2 for STANDARD/MANAGED/CONTENT/HOTFIX; EXPRESS/OPS may terminate Tier-1 (ADR053 §6).
- **Legacy-tolerant:** WPs without this block are skipped by Check 49 (never failed).

## References

- `governance/directives/ADR053_TIERED_VALIDATION_MODEL_v1.0.0.md` (tiered validation canon)
- `core/db/migrations/010_work_packages_parent_and_track.sql`
- `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`
- `lean-kit/modules/project-governance/WP_ID_STANDARD.md` §10–§11
