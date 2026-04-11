# L2.5 Sandbox Setup & Experiment Runbook
# Version: 0.1.0
# Target: AOS-Sandbox-Full (/Users/nimrod/Documents/AOS-Sandbox-Full)

---

## OVERVIEW

This runbook covers three phases:
1. **Environment Setup** — Prepare AOS-Sandbox-Full for L2.5
2. **Experiment Run** — First L2.5 WP in sandbox (controlled test)
3. **Test Flight** — First L2.5 WP in a live project (TikTrack or agents-os)

---

## PHASE A: ENVIRONMENT SETUP

### A1 — Register Module 12 in Sandbox

In AOS-Sandbox-Full, verify that lean-kit is current.
The sandbox gets a physical copy of the lean-kit. Update it:

```bash
# From agents-os repo root:
cd /Users/nimrod/Documents/agents-os

# Check sandbox lean-kit module list
ls /Users/nimrod/Documents/AOS-Sandbox-Full/_aos/lean-kit/modules/

# If managed-pipeline module is missing, copy it:
cp -r lean-kit/modules/managed-pipeline \
      /Users/nimrod/Documents/AOS-Sandbox-Full/_aos/lean-kit/modules/
```

Verify: `managed-pipeline/MODULE.md` exists in sandbox lean-kit.

### A2 — Propagate Operator DNA to Sandbox

```bash
# Copy operator_dna.yaml to sandbox
cp core/operator_dna.yaml \
   /Users/nimrod/Documents/AOS-Sandbox-Full/_aos/operator_dna.yaml
```

Verify: file exists and version matches agents-os core/operator_dna.yaml.

### A3 — Add L2.5 Profile Support to Sandbox roadmap.yaml

Open `/Users/nimrod/Documents/AOS-Sandbox-Full/_aos/roadmap.yaml`.

Verify the project metadata shows `profile: L2` or update to support L2.5 WPs.
Add the first L2.5 WP placeholder:

```yaml
work_packages:
  # ... existing WPs ...
  
  - id: SBXF-P001-WP-L25-001
    label: "L2.5 Experiment — [WP title TBD from LOD100]"
    status: PLANNED
    track: B
    profile: L2.5
    current_lean_gate: L25-PH1
    lod_status: LOD100
    created_at: "2026-04-10"
    milestone_ref: sandbox-experiment
    gate_history: []
    notes: "First L2.5 pipeline experiment"
```

### A4 — Create WP Directory Structure

```bash
mkdir -p /Users/nimrod/Documents/AOS-Sandbox-Full/_aos/work_packages/SBXF-P001-WP-L25-001
```

### A5 — Verify Cross-Engine Setup

Confirm that the sandbox has at minimum TWO different engines available:
- Orchestrator: Claude Code (this session)
- Constitutional Validator: must use a different engine

For the experiment, acceptable configuration:
```
Producer agents:   claude-sonnet-4-6 (Claude Code, via Agent tool)
Validator agents:  claude-opus-4-6   (Claude Code Agent tool, different model = acceptable for experiment)
```

Note: In production, OpenAI (Team 190) would be the constitutional validator.
For sandbox experiment, using different Claude model tier is acceptable to validate the process.
Flag this as a known deviation in the experiment gate_history.

---

## PHASE B: EXPERIMENT RUN (Sandbox)

### B1 — Choose the Experiment WP

Select a WP that is:
- Small in scope (2-3 implementation files max)
- Well-understood domain (no new research needed)
- Has a clear, testable outcome
- Does NOT touch production systems

Recommended first experiment: A small feature addition to AOS-Sandbox-Full's dashboard.
Example: "Add a WP count summary card to the sandbox dashboard"

### B2 — Produce the LOD100

Use the template: `lean-kit/modules/managed-pipeline/artifacts/LOD100_L25_FORM.md`

Fill in:
```yaml
wp_id: SBXF-P001-WP-L25-001
project_id: aos-sandbox-full
profile: L2.5
created: 2026-04-10
owner: team_00
operator_dna_version: "0.1.0"
```

Complete all sections: problem statement, actors, desired outcome, scope, open questions.

### B3 — Activate the Orchestrator

Present the completed LOD100 to Claude Code (Team 100) with this activation:

```
[COPY-PASTE THIS TEXT TO START A PIPELINE RUN]
─────────────────────────────────────────────────────
L2.5 PIPELINE ACTIVATION

Read and follow exactly:
lean-kit/modules/managed-pipeline/activation/ACTIVATION_ORCHESTRATOR.md
lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md

Session start protocol:
1. Read core/operator_dna.yaml
2. Read core/definition.yaml
3. Validate the LOD100 below (Phase 1)
4. If PASS: begin Phase 2A automatically

LOD100 for validation:
[PASTE LOD100 CONTENT HERE]
─────────────────────────────────────────────────────
```

### B4 — Monitor the Run

The Orchestrator will:
- Report progress at each phase transition
- Stop and present at Phase 3 (LOD300 + Mockup) — your first decision point
- Stop and present at Phase 5 (UX final) — your second decision point

Between those stops: the pipeline runs autonomously.

### B5 — Experiment Evaluation Criteria

After the sandbox run, evaluate:

| Criterion | Target | Actual |
|-----------|--------|--------|
| Human gate 1 (Phase 3) — LOD300 quality | Reviewable in < 15 min | ? |
| Human gate 2 (Phase 5) — Implementation quality | Pass on first review | ? |
| FCP cycles | 0-1 total | ? |
| Artifacts produced | All phases filed correctly | ? |
| Cross-engine rule | Maintained throughout | ? |
| Circuit breaker | Not triggered | ? |

If ≥ 4/6 criteria met → proceed to Test Flight.
If < 4/6 → diagnose issues, adjust runbook, re-run sandbox.

---

## PHASE C: TEST FLIGHT (Live Project)

### Prerequisites
- Sandbox experiment: ≥ 4/6 criteria met
- A real WP that is ready for L2.5 execution
- Nimrod explicit approval to proceed to live project

### Recommended Test Flight Target

**Option 1: agents-os** — a governance or dashboard WP
**Option 2: TikTrack** — a feature WP with clear scope

Choose based on:
- Which project has a WP at LOD100 stage right now
- Which has the most to gain from managed execution
- Which has lower risk if the pipeline has issues

### Test Flight Execution

Same flow as sandbox, but:
- Real codebase (not sandbox)
- Higher quality bar for LOD300 and LOD400
- Constitutional Validator should be a different LLM provider if possible
- Nimrod reviews Phase 3 and Phase 5 with full attention (not a rubber stamp)

### Test Flight Success Criteria

| Criterion | Target |
|-----------|--------|
| Nimrod total touchpoints | ≤ 3 (LOD100 + Phase 3 + Phase 5) |
| LOD300 passes Phase 3 on first presentation | YES |
| Implementation passes Phase 5 on first review | YES |
| No Iron Rule violations | YES |
| AS_MADE_LOCK achieved | YES |

If all 5 met → L2.5 is operational. Formalize as standard module.
If 3-4 met → Iterate on runbook, re-test on next WP.
If < 3 met → Return to sandbox, diagnose architecture issue.

---

## KNOWN DEVIATIONS (Sandbox Only)

These are acceptable deviations from production L2.5 for the sandbox experiment:

1. **Constitutional Validator engine**: Using claude-opus-4-6 instead of OpenAI. Flag in gate_history.
2. **Implementation teams**: Using Claude Code Agent tool for all implementation (single engine). Acceptable for experiment.
3. **Browser QA**: Use preview tools instead of MCP browser tools. Flag in QA verdict.

These deviations MUST be resolved before Test Flight on a live project.

---

## ROLLBACK PLAN

If the sandbox experiment produces artifacts in an inconsistent state:
- All L2.5 artifacts are in `_aos/work_packages/SBXF-P001-WP-L25-001/`
- Archive them: `mv _aos/work_packages/SBXF-P001-WP-L25-001 _COMMUNICATION/99-ARCHIVE/`
- Reset roadmap.yaml WP entry to `status: PLANNED`
- No code changes in sandbox (experiment WPs are small — revert is trivial)

---

## QUICK REFERENCE: FILE LOCATIONS

| Artifact | Path |
|----------|------|
| Orchestrator Runbook | `lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md` |
| LOD100 Form | `lean-kit/modules/managed-pipeline/artifacts/LOD100_L25_FORM.md` |
| FCP Guide | `lean-kit/modules/managed-pipeline/artifacts/FCP_CLASSIFICATION_GUIDE.md` |
| Gate Template | `lean-kit/modules/managed-pipeline/artifacts/PHASE_GATE_TEMPLATE.md` |
| Operator DNA | `core/operator_dna.yaml` |
| Orchestrator Activation | `lean-kit/modules/managed-pipeline/activation/ACTIVATION_ORCHESTRATOR.md` |
| All activations | `lean-kit/modules/managed-pipeline/activation/` |
| WP artifacts (runtime) | `_aos/work_packages/{WP-ID}/` |
| Team communications | `_COMMUNICATION/team_XX/` |
