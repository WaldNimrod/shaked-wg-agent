# Phase Gate Presentation Template
# Use this template when presenting Human Gates (Phase 3 or Phase 5) to Nimrod

---

## PHASE 3 GATE TEMPLATE

```markdown
## L2.5 Phase 3 Human Gate — {WP-ID}
**Date:** {YYYY-MM-DD}
**Pipeline session:** {session reference}

---

### What has been produced:
- LOD300 (System Behavior): `_aos/work_packages/{WP-ID}/LOD300_{WP-ID}.md`
- Mockup (State Diagram + Screens): `_aos/work_packages/{WP-ID}/MOCKUP_{WP-ID}.md`
- Constitutional validation: PASS

### What will be built (LOD300 summary):
{3-5 bullets extracted from LOD300 scope section}

### Key system states:
{Copy state machine summary from LOD300}

### Architectural decisions made:
{List from LOD300 open decisions — now resolved}

### Architect concerns (if any):
{If arch agent flagged any concerns, surface them here. Otherwise: "None."}

### Open questions resolved since LOD100:
{What was unknown in LOD100 and is now resolved}

---

### YOUR DECISION:

**Option 1: APPROVED**
→ Phase 4 begins immediately (LOD400 → Implementation → QA → Validation)

**Option 2: REVISIONS**
→ Specify what to change. I will route to the right phase.
→ Examples: "Section X in LOD300 is wrong" / "Mockup screen Y doesn't match intent"

**Option 3: REJECTED**
→ Full concept rewrite. Phase 2 restarts.
→ Please describe what is fundamentally wrong.
```

---

## PHASE 5 GATE TEMPLATE

```markdown
## L2.5 Phase 5 Human Gate — {WP-ID}
**Date:** {YYYY-MM-DD}
**FCP cycles to date:** FCP-1: {N} | FCP-2: {N} | FCP-3: {N}

---

### What was implemented:
{Brief summary of what was built, 2-4 bullets}

### How to review:
{Exact steps: command to run, URL to open, sequence of actions}

### QA result: PASS
Evidence: `_COMMUNICATION/team_50/QA_VERDICT_{WP-ID}.md`

### Technical validation: PASS
Evidence: `_COMMUNICATION/team_90/TECH_VALIDATION_{WP-ID}.md`

### Acceptance criteria status:
| AC-ID | Criterion | Test performed | Result |
|-------|-----------|----------------|--------|
| AC-01 | {text}    | {evidence}     | PASS   |
| ...   | ...       | ...            | ...    |

---

### YOUR DECISION:

**Option 1: APPROVED**
→ Phase 6 begins (Documentation + Closure). WP will be closed.

**Option 2: MINOR FIXES**
→ Describe exactly what to fix.
→ I will classify as FCP-1 (trivial, simple fix agent) or FCP-2 (targeted team fix).
→ No full restart required. Re-present after fix.

**Option 3: REJECTED**
→ Describe what is wrong.
→ I will classify as FCP-3 (implementation failure) or FCP-4 (spec failure).
→ FCP-4 requires mandatory Nimrod acknowledgment before restart.
```
