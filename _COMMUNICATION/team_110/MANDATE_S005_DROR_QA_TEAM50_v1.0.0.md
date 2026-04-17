# MANDATE — Team 50 QA for Dror Profile Launch (S005)

**Assigned to:** Team 50 (QA & Functional Acceptance)  
**Requestor:** Team 110  
**Authority:** Team 00  
**Date:** 2026-04-17

---

## Context Bundle
- Work package context: S005 operational launch bridge for second Israeli user profile (`dror`)
- LOD/spec context references:
  - `_aos/roadmap.yaml` (S005 ACTIVE, S003 multi-user deferred)
  - `_COMMUNICATION/team_110/MANDATE_S005_DROR_PROFILE_LAUNCH_v1.0.0.md`
- Validation target: functional behavior only (Team 50 scope)

---

## QA Goal

Verify that the Dror profile launch works as a safe temporary shared-instance deployment:
1) Dror profile and region load correctly,  
2) run outputs are scoped to `profile_id=dror`,  
3) unique production URL path is generated,  
4) existing default profile behavior is not broken.

---

## Acceptance Criteria (Test Contract)

| AC-ID | Behavior to verify | Test steps | Expected result |
|---|---|---|---|
| AC-01 | Dror profile exists and is loadable | `python3 -m shaked_wg_agent status --profile dror` | Command succeeds and shows profile `Dror Ground-House Long-Term` |
| AC-02 | Dror profile resolves to new city definition | same command as AC-01 | city id resolves to `dror-carmel-region`; no config errors |
| AC-03 | Source mapping includes homeless for Dror city | inspect loaded config via runtime or debug log | resolved active source list contains `homeless` |
| AC-04 | Unique URL path generation for Dror is supported | run with `UPRESS_UPLOAD_PATH=wp-content/uploads/shaked-wg/dror` and `--profile dror` | `run_record.report_url` equals `.../shaked-wg/dror/index.html` when upload credentials are present |
| AC-05 | Report content isolation by profile_id | use fixture data with at least two profiles and call publish path | generated report for Dror contains Dror listings only |
| AC-06 | Stale cleanup isolation by profile_id | execute stale cleanup through run for dror with non-dror rows present | non-dror rows are not removed by dror run |
| AC-07 | Verification isolation by profile_id | include non-dror listings and run dror scan flow | non-dror rows are not re-verified/modified by dror path |
| AC-08 | Backward compatibility for existing flow | `python3 -m shaked_wg_agent status --profile default` | default profile remains operational |
| AC-09 | New region coverage is documented in config | inspect `data/cities/dror-carmel-region.json` | includes requested settlement list and regional notes |
| AC-10 | Baseline stats artifact exists for handoff | inspect `_COMMUNICATION/team_110/STATS_S005_DROR_BASELINE_v1.0.0.md` | contains baseline metrics + post-run KPI template |

---

## Test Environment
- Runtime: local repository checkout
- CLI: `python3 -m shaked_wg_agent ...`
- Test suite: `pytest tests/ -v`
- Lint/structure:
  - `ruff check shaked_wg_agent/ tests/`
  - `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`

---

## Pass Threshold
- PASS only if all ACs pass.
- CONDITIONAL-PASS allowed only for environment blockers (for example missing FTPS credentials) with explicit evidence and impact note.

---

## Output Artifact Required from Team 50

Write verdict to:
`_COMMUNICATION/team_50/S005-DROR-LAUNCH/QA_REPORT_S005-DROR-LAUNCH_v1.0.0.md`

Required sections:
1. Verdict
2. AC table (Expected / Observed / Verdict)
3. Blocking findings (if any)
4. Open findings (if CONDITIONAL-PASS)
5. Environment + evidence log

