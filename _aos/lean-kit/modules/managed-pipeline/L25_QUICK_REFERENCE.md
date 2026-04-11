# L2.5 Quick Reference — Managed Agent Pipeline
# Version: 1.1.0 | Status: CANONICAL | Canonicalized: 2026-04-11 | Updated: 2026-04-11

---

## Profile Selection — L0 / L2 / L2.5

→ Full guide: `lean-kit/PROFILE_SELECTION_GUIDE.md`

| | L0 | L2 | L2.5 |
|--|----|----|------|
| LOD300 | Optional | Optional | **Always required** |
| Research rounds | None | None | **R1/R2/R3 mandatory** |
| Human gates | 0 | 0 | **2 (Team 00 only)** |
| Cross-model validation (within loop) | Optional | Optional | **Mandatory every LOD step** |
| External one-shot checkpoints | None | None | **EXT-CP1 always; EXT-CP2 conditional** |
| Engine | No | Yes | Yes (extends L2) |
| Complexity | Low | Low–Medium | **Medium–High** |

**Use L2.5 when:** ≥2 teams + integration contracts, state machine ≥5 states, MEDIUM/HIGH risk, new data model or API surface.
**Use L2 when:** bounded single-team, well-understood pattern, Track A viable.
**Use L0 when:** governance structure only, no engine needed.

Profile is declared in LOD100 by Team 00. **Immutable once set.**

---

## What is L2.5?

A managed, research-deepened, human-gated agent pipeline for complex WPs.
Sits between L2 (manual agent activation) and L3 (future autonomous CLI).

**Use when:** ≥2 teams, new state machine, MEDIUM/HIGH implementation risk, integration contracts.
**Don't use when:** single team, well-understood pattern, Track A viable.

---

## How to activate as Orchestrator

**Step 1 — Session start (read in order):**
```
1. core/operator_dna.yaml              ← decision context
2. core/definition.yaml                ← team assignments, Iron Rules
3. lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md  ← your constitution
4. {project}/_aos/work_packages/{WP-ID}/LOD100_{WP-ID}.md             ← the WP
```

**Step 2 — Paste this activation block to Claude Code:**
```
You are the L2.5 Pipeline Orchestrator (Team 100).
Read: lean-kit/modules/managed-pipeline/runbooks/ORCHESTRATOR_RUNBOOK.md
Then validate LOD100 at: {path/to/LOD100}.md
Profile: L2.5. WP-ID: {WP-ID}. Project: {project-id}.
Start Phase 1.
```

---

## Pipeline at a glance

```
EXT-CP1 → One-shot external LOD100 validation (team_190/Codex) [always, pre-pipeline]
PH1     → LOD100 validated (entry check)
PH2A    → R1 research + LOD200 + constitutional validation  [auto]
PH2B    → R2 research + LOD300 + Mockup + constitutional validation  [auto]
PH3     ← HUMAN GATE — Team 00 approves LOD300 + Mockup
PH4A    → R3 research + LOD400 + 8-check + constitutional validation  [auto]
EXT-CP2 → One-shot external LOD400 validation (team_190/Codex) [HIGH: mandatory, MEDIUM: advisory, LOW: skip]
PH4B    → Work Plan + mandates  [auto]
PH4C    → Implementation (teams per mandate)  [auto]
PH4D    → QA (cross-model from builders)  [auto]
PH4E    → Technical validation (cross-model from QA)  [auto]
PH5     ← HUMAN GATE — Team 00 UX approval
PH6     → LOD500 + AS_MADE_LOCK + closure  [auto]
```

**Total gates:** 11 sub-phases, 2 human gates, 2 external one-shot checkpoints.
**Human gate format:** Orchestrator presents summary + artifacts table + 3 exit options (APPROVED / REVISIONS / REJECTED).
**One-shot pattern:** team_190 fires once per checkpoint, pipeline ingests report and continues internally. Re-routing PROHIBITED without Team 00 authorization.

---

## Research rounds (mandatory)

| Round | Before | What you research |
|-------|--------|-------------------|
| R1 | LOD200 | Existing patterns, risk surface, unknowns, operator alignment |
| R2 | LOD300 | State space, integration constraints, edge cases, AC pre-verification |
| R3 | LOD400 | Exact values, library behavior, resolve all OADs, build test skeleton |

Research findings append to the LOD doc as `## Research Findings — R{N}`.
Time ratio: R1:LOD200 = 1:1, R2:LOD300 = 1:1, R3:LOD400 = 1:2.

---

## FCP classification (quick decision)

```
Bug/gap found →
  Can fix with ≤2 file / ≤20 line change, no DDL, no API change?  → FCP-1 (PWA fix)
  Bounded single section, single team?                             → FCP-2 (targeted fix)
  Multi-team or architectural impact?                              → FCP-3 (restart phase)
  Spec itself is wrong (LOD300/400 defect)?                        → FCP-4 (STOP, escalate)
```

**Circuit breaker:** FCP-3 ≥ 3 cycles OR any FCP-4 → stop, present full diff to Team 00.

---

## Cross-engine validation model

### Within-loop: Cross-model (Anthropic — known limitation)

| Phase | Builder | Validator | Notes |
|-------|---------|-----------|-------|
| LOD200/300/400 production | claude-sonnet-4-6 | claude-opus | Cross-model, same vendor |
| QA (PH4D) | cross-model from builders | — | Different Claude model required |
| Tech validation (PH4E) | cross-model from QA | — | Different Claude model required |
| Constitutional validation | always claude-opus | — | |

**Known limitation:** Both builder and validator are Anthropic Claude models. This is cross-model, not cross-vendor. Acknowledged and accepted per L2.5 Profile v1.1 (Team 00, 2026-04-11).

### One-shot external checkpoints (cross-vendor: team_190 / OpenAI Codex)

| Checkpoint | Phase | Trigger | Validator |
|------------|-------|---------|-----------|
| EXT-CP1 | LOD100 pre-pipeline entry | ALWAYS (mandatory) | team_190 (Codex) |
| EXT-CP2 | LOD400 pre-implementation | HIGH risk: MANDATORY / MEDIUM: advisory / LOW: skip | team_190 (Codex) |

**One-shot pattern:** team_190 produces ONE report per checkpoint. Pipeline ingests report as context and continues internally. No iterative external loop. Re-routing based on team_190 verdict is PROHIBITED without explicit Team 00 authorization.

**Report paths:**
- EXT-CP1: `_COMMUNICATION/team_190/EXT_CP1_REPORT_{WP-ID}.md`
- EXT-CP2: `_COMMUNICATION/team_190/EXT_CP2_REPORT_{WP-ID}.md`

---

## LOD100 required fields (L2.5 specific)

```yaml
profile: L2.5                      # mandatory
wp_id: {PROJECT}-P{N}-WP-{N}      # canonical format
project_id: {project-id}
operator_dna_version: "0.1.0"      # must match core/operator_dna.yaml
# + standard fields: problem statement, actors, outcomes, scope, open questions
```

---

## LOD levels at a glance

| LOD | Level | Key requirement |
|-----|-------|-----------------|
| LOD100 | Intent | Problem, actors, scope, open questions |
| LOD200 | Concept | Components, flow, ACs (measurable), risk |
| LOD300 | System Behavior | State machine (complete), data model, API surface, integration contracts |
| LOD400 | Execution-Ready | Zero TBD, exact values, buildable by any agent without questions |
| LOD500 | As-Built | Fidelity record, deviation log, AS_MADE_LOCK |

---

## Gate history format (roadmap.yaml)

```yaml
gate_history:
  - gate: L25-PH1
    result: PASS            # PASS | FAIL | REVISION
    date: "YYYY-MM-DD"
    notes: "brief note — include FCP level if applicable"
```

---

## Files to know

| File | What it does |
|------|-------------|
| `runbooks/ORCHESTRATOR_RUNBOOK.md` | Full step-by-step execution guide (read first) |
| `activation/ACTIVATION_ORCHESTRATOR.md` | Orchestrator identity + session start |
| `activation/ACTIVATION_SPEC_AGENT.md` | Spec agent (LOD200 + LOD400) |
| `activation/ACTIVATION_ARCH_AGENT_L25.md` | Arch agent (LOD300) |
| `activation/ACTIVATION_CONST_VALIDATOR.md` | Constitutional validator |
| `activation/ACTIVATION_MOCKUP_AGENT.md` | Mockup agent |
| `activation/ACTIVATION_GATEWAY_AGENT_L25.md` | Gateway (work plan + mandates) |
| `activation/ACTIVATION_QA_AGENT_L25.md` | QA agent |
| `activation/ACTIVATION_TECH_VALIDATOR_L25.md` | Technical validator |
| `activation/ACTIVATION_DOC_AGENT_L25.md` | LOD500 + closure |
| `artifacts/LOD_RESEARCH_PROTOCOL.md` | R1/R2/R3 protocol detail |
| `artifacts/FCP_CLASSIFICATION_GUIDE.md` | FCP decision tree |
| `artifacts/PHASE_GATE_TEMPLATE.md` | Human gate presentation format |
| `profiles/L2.5.yaml` | Profile definition (modules, gates, criteria) |

---

## LOD300 must contain (minimum)

- [ ] Complete state machine (Mermaid stateDiagram-v2)
- [ ] Business rules (numbered, unambiguous, no single interpretation)
- [ ] Data model (entities, fields, types, constraints)
- [ ] API surface (method, path, request, response, error codes)
- [ ] Sequence diagrams (primary flows + error flows)
- [ ] Integration contracts (if multi-system)
- [ ] LOD300 ACs (system behavior level — not user story)
- [ ] Open architectural decisions (explicit, not hidden)

**Tip:** Missing any of these → constitutional validation will return FCP-2 or FCP-3.

---

## LOD400 cannot contain

- TBD, TODO, placeholder
- "similar to...", implicit references
- Open questions (all must be resolved in LOD300 first)
- Implicit project-convention assumptions

**Tip:** If a builder would have to ask one question → it's not LOD400.

---

## Canary run data (2026-04-11)

First complete L2.5 run: `SBXF-P001-WP-L25-001` (L2.5 Run Viewer).
- 11 sub-phases completed
- FCP-1×3, FCP-2×1, FCP-3×0, FCP-4×0
- 2 human gates — both APPROVED first pass
- AS_MADE_LOCK applied

Process validated. Module 12 status: CANONICAL.

---

*Read ORCHESTRATOR_RUNBOOK.md for full step-by-step execution.*
*This file: concise activation reference for future agents.*
