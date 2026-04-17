# ACTIVATION PROMPT — Team 50 QA (S005 Dror Launch)

You are Team 50. Execute an independent fresh QA run for Dror profile launch in this repository.

## Scope

- Validate functional acceptance of temporary second-user launch in S005.
- Do not perform code implementation or architecture review.
- Do not reuse prior Team 110 conclusions as evidence.

## Inputs

1. `_COMMUNICATION/team_110/MANDATE_S005_DROR_QA_TEAM50_v1.0.0.md`
2. `_COMMUNICATION/team_110/MANDATE_S005_DROR_PROFILE_LAUNCH_v1.0.0.md`
3. `data/profiles/dror.json`
4. `data/cities/dror-carmel-region.json`
5. `data/sources.json`
6. `shaked_wg_agent/persistence.py`
7. `shaked_wg_agent/runner.py`
8. `_COMMUNICATION/team_110/STATS_S005_DROR_BASELINE_v1.0.0.md`

## Mandatory execution sequence

1. Run AC testability check on all ACs from the mandate.
2. Run:
  - `pytest tests/ -v`
  - `ruff check shaked_wg_agent/ tests/`
  - `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .`
3. Execute profile-level checks:
  - `python3 -m shaked_wg_agent status --profile dror`
  - `python3 -m shaked_wg_agent status --profile default`
4. Validate profile-isolation behavior (AC-05/06/07) with deterministic evidence.
5. Validate unique URL path behavior for Dror run context.

## Evidence standard

- Every AC must include command/action + observed output + verdict.
- Use automation-first evidence where possible.
- If blocked, return BLOCKED or CONDITIONAL-PASS with explicit blocker.

## Expected output

Create:
`_COMMUNICATION/team_50/S005-DROR-LAUNCH/QA_REPORT_S005-DROR-LAUNCH_v1.0.0.md`

Verdict format must follow Team 50 contract in `_aos/governance/team_50.md`.