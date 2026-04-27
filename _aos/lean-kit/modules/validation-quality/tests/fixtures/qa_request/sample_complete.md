---
id: QA_REQUEST_SAMPLE_COMPLETE
from: team_50 (QA)
to: team_90 (Validator)
type: QA_REQUEST
work_package: AOS-SAMPLE-WP001
gate: L-GATE_BUILD
date: 2026-04-24
verdict: PASS
confidence: HIGH
blocked_reason_code: prerequisite_missing
---

# QA Request — Sample Complete (fixture)

This fixture contains only **valid** enum values. The lint script must emit
no `WARN:` lines when scanning this file.

## Summary

All controlled-vocabulary fields use canonical values from
`QA_ENUM_LINT_STANDARD_v1.0.0.md`.
