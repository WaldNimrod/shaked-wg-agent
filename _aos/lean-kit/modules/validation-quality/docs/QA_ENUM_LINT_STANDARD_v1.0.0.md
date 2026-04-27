---
id: QA_ENUM_LINT_STANDARD_v1.0.0
title: QA Request Enum Lint Standard
version: 1.0.0
status: ACTIVE
domain: agents-os (lean-kit / validation-quality)
authority: AOS_GATE_MANDATE_CANON_v1.7.0+, team_50.md v2.0.5
date: 2026-04-24
wp: AOS-V324-WP-QA-ENUM-LINT
---

# QA Request Enum Lint Standard — v1.0.0

This document is the **canonical SSoT** for controlled-vocabulary fields in
`QA_REQUEST.md` artifacts. The lint script `validate_qa_request_enums.py`
reads enum values directly from this file — do not edit values here without
also updating the script's behaviour.

---

## Canonical Enum Values

```yaml
verdict: [PASS, FAIL, BLOCKED, PASS_WITH_FINDINGS]
confidence: [HIGH, MEDIUM, LOW]
blocked_reason_code: [prerequisite_missing, environment_unavailable, ac_untestable, tooling_gap]
```

---

## Field Notes

| Field | Required | Notes |
|-------|----------|-------|
| `verdict` | Yes (when present) | Overall gate result. `PASS_WITH_FINDINGS` = pass with non-blocking notes. |
| `confidence` | Yes (when present) | Validator confidence in the result. |
| `blocked_reason_code` | Conditional | Required only when `verdict: BLOCKED`. Must use one of the canonical codes above. |
| `gate` | — | **Explicitly out of scope** for this standard. Gate values vary by WP type and track; deferred to a future WP. |

Fields are validated **only when present** in the frontmatter. A missing field
does not trigger a lint warning. A null/empty value for a present field is
flagged if the empty string is not a member of the enum.

---

## Authority

- **blocked_reason_code** enum: `lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md` §BLOCKED handling
- **verdict** and **confidence** enums: `core/governance/team_50.md` v2.0.5 §QA_REQUEST schema
- Supersedes: no prior version (initial release)

---

## Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-04-24 | team_20 | Initial release (AOS-V324-WP-QA-ENUM-LINT) |
