---
description: "Unified mandate template — ONE format for all gate types and all teams. Replaces per-gate ad-hoc formats."
version: "1.2.0"
wp: AOS-V314-WP-CANONICAL-GATES
changelog: "1.2.0 (M4-WP1): frontmatter = UNION of CA7 §5.6 R1 key-table + AOS_GATE_MANDATE_CANON Phase 5; body now 8 sections (added §8 Post-Mandate Routing — mandatory, always last). Matches mandates.render_mandate_metadata/body."
---

# Unified Mandate Template

Used by `/AOS_gate-mandate` to generate canonical mandate artifacts.

---

## YAML Frontmatter (required — all fields)

Union of the CA7 §5.6 R1 key-table (the conformance floor) and the AOS_GATE_MANDATE_CANON
Phase 5 extras (`project`, `engine_constraint`, `verdict`). `type` is the **CA7 R1 enum**
(`ACTIVATION | HANDOFF | VALIDATION_REQUEST | TASK_REQUEST | QUESTION`) — the D6 discriminator
maps a decisive validation mandate → `VALIDATION_REQUEST`, else `TASK_REQUEST`; the gate sub-type
(`GATE_MANDATE | QA_MANDATE | RESUBMISSION`) is preserved on the distinct `mandate_type:` line.
Extended R1 keys (`domain, wp, gate, role, engine, scope, template_ref`) must be present; value
may be `n/a`.

```yaml
---
id: MANDATE_{WP_ID}_{GATE}_v{VERSION}
type: {ACTIVATION | HANDOFF | VALIDATION_REQUEST | TASK_REQUEST | QUESTION}   # CA7 R1 enum (D6 discriminator)
mandate_type: {GATE_MANDATE | QA_MANDATE | RESUBMISSION}                      # gate sub-type (preserved)
from: Team {FROM_ID} ({FROM_ROLE})
to: Team {TO_ID} ({TO_ROLE})
date: {YYYY-MM-DD}
status: ACTIVE
target_render: {file | new-session | continuation | human}
domain: {DOMAIN}
project: {PROJECT_ID}
wp: {WP_ID}
gate: {GATE_TYPE}
role: {TO_ROLE}
engine: {ENGINE or n/a}
engine_constraint: "{cross-engine rule description}"
scope: {SCOPE or n/a}
template_ref: MANDATE_TEMPLATE.md
verdict: PENDING
signal: {A | B | C} ({signal description})
resubmission_round: {N}        # only for resubmissions
supersedes: {prior mandate id}  # only for resubmissions
---
```

---

## Body Structure (8 sections — all required)

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

**QA_MANDATE addendum (mandate_type: QA_MANDATE / L-GATE_BUILD):** the emitted §3 additionally carries the QA
agent role split — **author** (Playwright-MCP writes/fixes tests) · **execute** (runs suites + collects
artifacts) · **explore** (exploratory pass → new deterministic test, not a direct verdict change) — and the
rule that the verdict MUST carry `run_evidence`. Per `TEAM_50_E2E_STANDARD v2.0.0` §4 (emitted by
`mandates.render_mandate_body`, M5-WP4).

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

<!-- §VC-3-EXTERNAL: use the following 3-part VC-3 when issuing L-GATE_VALIDATE_EXTERNAL mandates
     (supersedes literal-hash baseline check) -->

**VC-3 (External): WP build code context preserved.**
(a) **Ancestry preservation:** `git merge-base --is-ancestor <mandate_baseline> HEAD` returns true.
(b) **Working-tree preservation:** `git status --short` shows the LOD400 §3 builder-introduced artifacts uncommitted.
(c) **Build-code disjointness:** `git log --name-only <mandate_baseline>..HEAD -- <LOD400_§3_pathspecs>` returns empty output. Communication artifacts under `_COMMUNICATION/team_*/<WP>/` are EXCLUDED from this check.

If (a) + (b) pass but (c) shows intervening non-WP commits: treat as PASS_WITH_FINDINGS (log the commits as LOW finding). Only FAIL if (a) is false or (b) shows the builder's own artifacts uncommitted.

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

### Section 8: Post-Mandate Routing (mandatory — always last)

Deterministic next-step table so the executing team knows exactly what to invoke after writing
the verdict. Populate `{NEXT_GATE}` / `{NEXT_TEAM}` / `{NEXT_ENGINE}` from GATE_REGISTRY; when the
selected gate is the **final** gate in the track, Signal B.0 applies (WP complete → Team 191
archive), otherwise Signal A.

```markdown
## 8. Post-Mandate Routing

When verdict is written to `{VERDICT_PATH}`, invoke the following based on outcome:

| Outcome | Next Invocation | Signal |
|---------|----------------|--------|
| **PASS** | `/AOS_gate-mandate {WP_ID} {NEXT_GATE}` | A — within-WP gate advance to {NEXT_GATE} / {NEXT_TEAM} |
| **PASS** (final gate only) | `/AOS_gate-mandate {WP_ID}` | B.0 — WP complete → Team 191 archive mandate first |
| **PASS_WITH_FINDINGS** | Same as PASS above — surface notes to Team 00 first | |
| **FAIL** | Return verdict to Team 00. Builder applies fixes. Then: `/AOS_gate-mandate {WP_ID} {THIS_GATE}` | C — resubmission to same validator |
| **BLOCK** | Return verdict to the assigned builder team. Builder resolves blockers. Escalate to Team 00 only if blockers require a principal decision. | — |

**This gate:** `{THIS_GATE}` | **This WP:** `{WP_ID}`
**Next gate (if PASS):** `{NEXT_GATE}` → validator: `{NEXT_TEAM}` (engine: `{NEXT_ENGINE}`)
**Final gate in track?** {YES → Signal B.0 applies | NO → Signal A applies}
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

*AOS-V314-WP-CANONICAL-GATES | Unified Mandate Template v1.2.0 | 2026-04-12 (8-section + R1 union: M4-WP1)*
