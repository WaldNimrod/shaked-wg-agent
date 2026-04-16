---
description: "Unified mandate template — ONE format for all gate types and all teams. Replaces per-gate ad-hoc formats."
version: "1.0.0"
wp: AOS-V314-WP-CANONICAL-GATES
---

# Unified Mandate Template

Used by `/AOS_gate-mandate` to generate canonical mandate artifacts.

---

## YAML Frontmatter (required — all fields)

```yaml
---
id: MANDATE_{WP_ID}_{GATE}_v{VERSION}
from: Team {FROM_ID} ({FROM_ROLE})
to: Team {TO_ID} ({TO_ROLE})
date: {YYYY-MM-DD}
type: {GATE_MANDATE | QA_MANDATE | RESUBMISSION}
gate: {GATE_TYPE}
wp: {WP_ID}
project: {PROJECT_ID}
status: ACTIVE
verdict: PENDING
engine_constraint: "{cross-engine rule description}"
resubmission_round: {N}        # only for resubmissions
supersedes: {prior mandate id}  # only for resubmissions
---
```

---

## Body Structure (7 sections — all required)

### Section 1: Header

```markdown
# {GATE_TYPE} Mandate — {WP_ID}

**{WP LABEL}**
**Track:** {A/B/L2/L2.5} | **Profile:** {L0/L2/L2.5} | **Risk:** {LOW/MEDIUM/HIGH}
```

### Section 2: Gate History

```markdown
## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| L-GATE_ELIGIBILITY | PASS | 2026-04-12 | team_190 | {notes} |
| L-GATE_SPEC | PASS | 2026-04-12 | team_190 | {notes} |
| ... | ... | ... | ... | ... |
```

### Section 3: Scope

```markdown
## 3. Scope

{What this gate validates — derived from gate type:}

- L-GATE_ELIGIBILITY: Eligibility — problem coherence, scope, risk classification
- L-GATE_SPEC: Spec authorization — completeness, MoSCoW, AC coverage, manifest
- L-GATE_BUILD (QA): Functional acceptance — AC verification, test execution, browser evidence
- L-GATE_BUILD (Tech): Technical validation — spec fidelity, architecture, Iron Rules
- L-GATE_VALIDATE: Constitutional — full governance compliance + implementation fidelity
- EXT-CP1/CP2: Advisory — pre-pipeline/pre-implementation review
```

### Section 4: Validation Criteria

```markdown
## 4. Validation Criteria

| # | Criterion | What to Check |
|---|-----------|---------------|
| VC-1 / AC-1 | {name} | {specific check description} |
| VC-2 / AC-2 | {name} | {specific check description} |
| ... | ... | ... |

Total: {N} criteria
```

### Section 5: Files to Review

```markdown
## 5. Files to Review

### Spec Documents
- LOD300: {path}
- LOD400: {path}

### Implementation Files
{List of all files in scope — from LOD400 §6 manifest}

### Prior Artifacts
- QA Verdict: {path or N/A}
- Prior Validation: {path or N/A}
```

### Section 6: Resolved Findings (resubmission only)

```markdown
## 6. Resolved Findings from Round {N-1}

| # | Finding | Severity | Fix Applied | Verification |
|---|---------|----------|-------------|-------------|
| 1 | {finding from prior BLOCK} | BLOCKER | {description of fix} | {verification command} |
| 2 | {finding} | BLOCKER | {fix} | {command} |
```

### Section 7: Output Format

```markdown
## 7. Output

Write verdict to: `_COMMUNICATION/team_{TO_ID}/VERDICT_{WP_ID}_{GATE}_v{VERSION}.md`

Use the unified verdict template (7 sections):
1. Verdict Summary
2. Parameters
3. Criteria Table
4. Findings
5. validate_aos.sh
6. Disposition
7. Next Step

### Constraints
- Cross-engine: builder={BUILDER_ENGINE}, validator={VALIDATOR_ENGINE} — must differ
- Independence: do NOT read other teams' conclusions before your own verdict
- Evidence: every FAIL must cite file:line
- Enforcement mode will be communicated at invocation time
```

---

## Mandate File Naming Convention

```
_COMMUNICATION/team_{TO_ID}/MANDATE_{WP_ID}_{GATE}_v{VERSION}.md
```

For resubmissions:
```
_COMMUNICATION/team_{TO_ID}/MANDATE_{WP_ID}_{GATE}_RESUBMISSION_v{VERSION}.md
```

---

*AOS-V314-WP-CANONICAL-GATES | Unified Mandate Template v1.0.0 | 2026-04-12*
