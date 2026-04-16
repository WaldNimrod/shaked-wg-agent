---
description: "Unified verdict template — ONE format for all teams (50, 90, 190). Replaces legacy per-team formats."
version: "1.0.0"
wp: AOS-V314-WP-CANONICAL-GATES
---

# Unified Verdict Template

Used by `/AOS_qa` and `/AOS_validate` to generate canonical verdict artifacts.

---

## YAML Frontmatter (required — all fields)

```yaml
---
id: VERDICT_{WP_ID}_{GATE}_v{VERSION}
from: Team {ID} ({ROLE_DESCRIPTION})
to: Team 00
type: {QA_VERDICT | TECH_VALIDATION | CONSTITUTIONAL_VERDICT | ADVISORY_VERDICT}
work_package: {WP_ID}
gate: {GATE_TYPE}
date: {YYYY-MM-DD}
engine: {ENGINE — resolved dynamically from team_assignments.yaml}
enforcement: {regular | strict}
verdict: {PASS | PASS_WITH_FINDINGS | FAIL | CLEAR | CONCERNS | BLOCKED}
criteria_total: {N}
criteria_pass: {N}
criteria_fail: {N}
findings_blocker: {N}
findings_major: {N}
findings_minor: {N}
resubmission_round: {N}        # only for resubmission verdicts
supersedes: {prior verdict id}  # only for resubmission verdicts
---
```

---

## Body Structure (7 sections — all required)

### Section 1: Verdict Summary

```markdown
## 1. Verdict Summary

**{VERDICT}** — {one-line summary of result}

Enforcement: {regular/strict}
Revalidation: {fresh / targeted / delta / N/A}
```

### Section 2: Parameters

```markdown
## 2. Parameters

| Parameter | Value |
|-----------|-------|
| Mandate | {mandate file path} |
| Context mode | {full / minimal} |
| Team | {team_id} |
| Engine | {engine name — from team_assignments.yaml} |
| Gate | {gate type} |
| Track | {A/B/L2/L2.5} |
| Profile | {L0/L2/L2.5} |
| Enforcement | {regular/strict} |
| Revalidation | {fresh / targeted / delta} |
| Builder engine | {builder engine — for cross-engine check} |
| Cross-engine | {OK / VIOLATION} |
```

### Section 3: Criteria Table

```markdown
## 3. Criteria Table

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| VC-1 / AC-1 | {criterion name} | PASS / FAIL | {file:line reference or command output} |
| VC-2 / AC-2 | {criterion name} | PASS / FAIL | {evidence} |
| ... | ... | ... | ... |

Summary: {N} PASS / {N} FAIL of {N} total
```

### Section 4: Findings

```markdown
## 4. Findings

### Blockers (must fix)
1. **{finding title}** — Severity: BLOCKER
   - Evidence: {file}:{line} — {description}
   - Required fix: {what must change}

### Major (significant but may be non-blocking)
1. **{finding title}** — Severity: MAJOR
   - Evidence: {file}:{line} — {description}

### Minor (observations)
1. **{finding title}** — Severity: MINOR
   - Evidence: {file}:{line} — {description}

### Advisory (informational only)
{Observations that do not affect the verdict}
```

### Section 5: validate_aos.sh

```markdown
## 5. validate_aos.sh

{Full script output if run}

Exit criterion: {SATISFIED / NOT MET / N/A — not required for this gate}
Result: {N} PASS / {N} SKIP / {N} FAIL
```

### Section 6: Disposition

```markdown
## 6. Finding Disposition

| # | Finding | Severity | User Decision | Rationale |
|---|---------|----------|---------------|-----------|
| 1 | {title} | BLOCKER | Block | {reason} |
| 2 | {title} | MAJOR | Accept non-blocking | {reason} |
| 3 | {title} | MINOR | Skip | {reason — QA only} |

Enforcement: {regular — skip/accept available / strict — all findings block}
```

### Section 7: Next Step

```markdown
## 7. Next Step

{One of:}
- WP advances to {next gate}. Use `/AOS_gate-mandate {WP_ID} {NEXT_GATE}` to create mandate.
- {N} blockers must be fixed. Use `/AOS_gate-mandate {WP_ID} {GATE}` to generate resubmission.
- Route verdict to Team 00 for disposition.
- WP ready for closure — update roadmap.yaml → status: COMPLETE.
```

---

## Verdict File Naming Convention

```
_COMMUNICATION/team_{ID}/VERDICT_{WP_ID}_{GATE}_v{VERSION}.md
```

Examples:
- `VERDICT_AOS-V314-WP-CANONICAL-GATES_L-GATE_VALIDATE_v1.0.0.md`
- `VERDICT_AOS-V314-WP-CANONICAL-GATES_L-GATE_BUILD_v1.0.0.md`

---

*AOS-V314-WP-CANONICAL-GATES | Unified Verdict Template v1.0.0 | 2026-04-12*
