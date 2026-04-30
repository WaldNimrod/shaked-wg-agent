# REPORT — SWG-PLAT Bundle — L-GATE_VALIDATE R1 EXTERNAL
**Date:** 2026-04-30
**From:** team_190
**To:** team_110, team_00
**Re:** Constitutional validation result — M1–M5 bundle

## Overall Bundle Verdict: PASS_WITH_FINDINGS

## Per-WP Summary
| WP | Verdict | Blocking Findings | Notes |
|----|---------|-------------------|-------|
| SWG-PLAT-M1 | PASS_WITH_FINDINGS | None | Stale TODO in `_age_hard_exclude` docstring only. |
| SWG-PLAT-M2 | PASS_WITH_FINDINGS | None | LOD400 AC2 prose vs test thresholds — documentation alignment. |
| SWG-PLAT-M3 | PASS_WITH_FINDINGS | None | Mock-only proof per spec; live reCAPTCHA not re-run here. |
| SWG-PLAT-M4 | PASS | None | — |
| SWG-PLAT-M5 | PASS | None | — |

## Findings Requiring team_110 Action
1. Reconcile [SWG-PLAT-M2/LOD400_spec.md](_aos/work_packages/SWG-PLAT-M2/LOD400_spec.md) AC2 row (≥80% / vs summary) with the actual contract in [tests/test_scrapers/test_full_description.py](tests/test_scrapers/test_full_description.py) (≥50 chars + conditional longer-than-summary), or adjust tests if the table is authoritative — **non-blocking documentation**.
2. Remove or rewrite stale `TODO M5: gender_restriction` comment in [shaked_wg_agent/scorer.py](shaked_wg_agent/scorer.py) `_age_hard_exclude` — hygiene only.

## Findings Requiring team_00 Decision
1. **Validator engine:** This L-GATE_VALIDATE R1 EXTERNAL run was executed by **GPT-5.2 in Cursor Agent mode**, not the spoke’s registered cross-engine validator (**OpenAI / `shaked_val`** per [AGENTS.md](AGENTS.md)). Code, tests, and `validate_aos.sh` all passed; constitutional **engine independence** for this gate should be explicitly **waived or ratified** by team_00, or the verdict re-issued from the designated engine.

## Automated Checks
- pytest: **198 passed, 0 failed** (`python3 -m pytest tests/ -q`)
- ruff: **All checks passed!** (`python3 -m ruff check shaked_wg_agent/`)
- validate_aos.sh: **30 PASS / 9 SKIP / 0 FAIL** (`bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`)

## Open Questions (from HANDOFF §5)
| # | Question | Classification | Recommendation |
|---|----------|----------------|----------------|
| 1 | wgzimmer anti-bot / reCAPTCHA v3 in production | Acknowledged operational risk | Track under S005-P005-WP001 if headless scores fail threshold; not a code gate failure for M3. |
| 2 | `full_description` live ≥500 chars post-deploy | Acknowledged verification gap | Optional one live scan after deploy; fixtures + migration already verified. |
| 3 | `women_only` vs future male profile / no `profile.gender` | Out-of-scope product debt | Document in backlog; M5 spec explicitly keeps women-only WGs for current profile. |
| 4 | Read-only Docker volume / outreach writes | Deployment risk for future SaaS | Document ops constraint; L0 local path acceptable. |

## Governance Note
`roadmap.yaml` `spec_ref` for SWG-PLAT-M1..M5 still points at `LOD200_spec.md` while LOD400 files are the implementation SSOT for this program — consider hub sync to dual `spec_ref` or LOD400 path when team_100 updates registry (team_190 did not edit `_aos/`).

## Next Step
**team_110:** Read this REPORT and per-WP verdicts under `_COMMUNICATION/team_190/SWG-PLAT-M*/`; if team_00 waives engine deviation, proceed with roadmap `gate_history` + closure artifacts for **PASS_WITH_FINDINGS**; else coordinate re-validation on OpenAI and replace verdict commit.
