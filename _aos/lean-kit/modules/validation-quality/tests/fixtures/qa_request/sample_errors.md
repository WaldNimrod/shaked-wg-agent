---
id: QA_REQUEST_SAMPLE_ERRORS
from: team_50 (QA)
to: team_90 (Validator)
type: QA_REQUEST
work_package: AOS-SAMPLE-WP002
gate: L-GATE_BUILD
date: 2026-04-24
verdict: APPROVED
confidence: MEDIUM
blocked_reason_code: unknown_error
---

# QA Request — Sample Errors (fixture)

This fixture contains **invalid** enum values to exercise lint warnings:

- `verdict: APPROVED` — not a canonical value (should be PASS/FAIL/BLOCKED/PASS_WITH_FINDINGS)
- `confidence: MEDIUM` — valid (control: confirms only invalid fields are flagged)
- `blocked_reason_code: unknown_error` — not a canonical value
