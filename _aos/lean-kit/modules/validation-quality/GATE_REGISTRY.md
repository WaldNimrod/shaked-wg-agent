---
id: GATE_REGISTRY
version: "1.1.0"
wp: AOS-V314-WP-CANONICAL-GATES
description: "Canonical reference for all gate types across all AOS tracks. Used by /AOS_gate-mandate, /AOS_qa, /AOS_validate, and /AOS_gate-status skills."
---

# AOS Gate Registry

Machine-readable reference for the canonical gate skills. Maps every gate type to its track, validator authority, LOD requirements, and skill routing.

---

## Track Definitions

### L0 Track A — Simple WPs
**Criteria:** Single system, no new state machine, no new data model, LOW/MEDIUM risk.

| Order | Gate | LOD Required | Validator Authority | Skill | Verdict Options |
|-------|------|-------------|-------------------|-------|----------------|
| 1 | L-GATE_ELIGIBILITY | LOD100 | Constitutional (team_190) | `/AOS_validate` | PASS / FAIL |
| 2 | L-GATE_SPEC | LOD200 + LOD400 | Constitutional (team_190) | `/AOS_validate` | PASS / PASS_WITH_FINDINGS / FAIL |
| 3 | L-GATE_BUILD | LOD400 + impl | QA (team_50) + Tech (team_90) | `/AOS_qa` + `/AOS_validate` | PASS / FAIL |
| 4 | L-GATE_VALIDATE | LOD400 + L-GATE_BUILD PASS | Constitutional (team_190) | `/AOS_validate` | PASS / PASS_WITH_FINDINGS / FAIL |

### L0 Track B — Complex WPs
**Criteria:** Multiple systems, new state machines, HIGH risk, multi-team.

| Order | Gate | LOD Required | Validator Authority | Skill | Verdict Options |
|-------|------|-------------|-------------------|-------|----------------|
| 1 | L-GATE_ELIGIBILITY | LOD100 | Constitutional (team_190) | `/AOS_validate` | PASS / FAIL |
| 2 | L-GATE_CONCEPT | LOD200 | Architecture team | `/AOS_validate` | PASS / FAIL |
| 3 | L-GATE_SPEC | LOD300 + LOD400 | Constitutional (team_190) | `/AOS_validate` | PASS / PASS_WITH_FINDINGS / FAIL |
| 4 | L-GATE_BUILD | LOD400 + impl | QA (team_50) + Tech (team_90) | `/AOS_qa` + `/AOS_validate` | PASS / FAIL |
| 5 | L-GATE_VALIDATE | LOD400 + L-GATE_BUILD PASS | Constitutional (team_190) | `/AOS_validate` | PASS / PASS_WITH_FINDINGS / FAIL |

### L2 — AOS v3 Dashboard
**Criteria:** Full pipeline with DB-backed state management.

| Order | Gate | LOD Required | Validator Authority | Skill | Verdict Options |
|-------|------|-------------|-------------------|-------|----------------|
| 1 | GATE_0 | LOD100 | Constitutional (team_190) | `/AOS_validate` | PASS / FAIL |
| 2 | GATE_1 | LOD200 | Architecture + Constitutional | `/AOS_validate` | PASS / FAIL |
| 3 | GATE_2 | LOD400 | Team 100 + consuming team | `/AOS_validate` | PASS / FAIL |
| 4 | GATE_3 | — (build) | Team 10 (builder) | — | — |
| 5 | GATE_4 | LOD400 + evidence | Tier 1: QA, Tier 2: Tech, Tier 3: Human | `/AOS_qa` → `/AOS_validate` → Human | PASS / FAIL |
| 6 | GATE_5 | LOD500 | Constitutional (team_190) | `/AOS_validate` | PASS / PASS_WITH_FINDINGS / FAIL |

### L2.5 — Managed Agent Pipeline
**Criteria:** Complex WPs with automated agent orchestration.

| Order | Checkpoint | Type | Validator | Skill | Verdict Options |
|-------|-----------|------|-----------|-------|----------------|
| 1 | EXT-CP1 | Advisory (always) | Constitutional (team_190) | `/AOS_validate` | CLEAR / CONCERNS / BLOCKED |
| 2 | L25-PH1 | Automated | Orchestrator | — | — |
| 3 | L25-PH2A | Automated + within-loop | Spec agent + CV | — | PASS / FCP-1..4 |
| 4 | L25-PH2B | Automated + within-loop | Arch agent + CV | — | PASS / FCP-1..4 |
| 5 | L25-PH3 | Human gate | Team 00 | — | APPROVED / REVISIONS / REJECTED |
| 6 | L25-PH4A | Automated + within-loop | Spec agent + AV + CV | — | PASS / FCP-1..4 |
| 7 | EXT-CP2 | Advisory (risk-conditioned) | Constitutional (team_190) | `/AOS_validate` | CLEAR / CONCERNS / BLOCKED |
| 8 | L25-PH4B | Automated | Gateway agent | — | — |
| 9 | L25-PH4C | Automated | Implementation teams | — | — |
| 10 | L25-PH4D | Automated | QA agent (team_50) | `/AOS_qa` | PASS / FAIL |
| 11 | L25-PH4E | Automated | Tech validator (team_90) | `/AOS_validate` | PASS / CONDITIONAL_PASS / FAIL |
| 12 | L25-PH5 | Human gate | Team 00 | — | APPROVED / MINOR FIXES / REJECTED |
| 13 | L25-PH6 | Automated | Doc agent + closure | — | AS_MADE_LOCK |

**Note:** Within-loop checkpoints (PH2A, PH2B, PH4A) use pipeline-managed subagents, not human-invoked skills. Skills handle external gates (EXT-CP1, EXT-CP2) and post-build gates (PH4D, PH4E).

---

## Skill Routing Rules

### `/AOS_qa` is used when:
- Gate requires **functional acceptance** (AC verification, test execution, browser evidence)
- Target team is QA authority (team_50 or equivalent)
- Gates: L-GATE_BUILD (QA portion), GATE_4 Tier 1, L25-PH4D

### `/AOS_validate` is used when:
- Gate requires **constitutional, technical, or advisory validation**
- Target team is validator authority (team_90, team_190, or equivalent)
- Gates: L-GATE_ELIGIBILITY, L-GATE_CONCEPT, L-GATE_SPEC, L-GATE_VALIDATE, L-GATE_BUILD (tech portion), EXT-CP1, EXT-CP2, GATE_0, GATE_1, GATE_2, GATE_5, GATE_4 Tier 2, L25-PH4E

### L-GATE_BUILD splits into two skills:
1. `/AOS_qa` — Team 50 runs Part A (CLI) + Part B (browser) + validate_aos.sh
2. `/AOS_validate` — Team 90 runs 3-layer technical validation

Both must PASS before L-GATE_BUILD is considered PASS.

---

## Enforcement Modes

| Mode | `/AOS_qa` behavior | `/AOS_validate` behavior |
|------|---------------|---------------------|
| `regular` (default) | SKIP allowed for non-blocking findings | PASS_WITH_FINDINGS allowed for MINOR findings |
| `strict` | All findings are blocking, no SKIP | 100% PASS required, no PASS_WITH_FINDINGS |

### EXT-CP enforcement mapping:
| Mode | CONCERNS verdict → | BLOCKED verdict → |
|------|-------------------|-------------------|
| `regular` | Proceed, surface to Team 00 | Stop, require Team 00 authorization |
| `strict` | Treated as BLOCKED | Stop, require Team 00 authorization |

---

## Cross-Engine Constraints

| Gate | Constraint | Check |
|------|-----------|-------|
| L-GATE_BUILD (QA) | QA engine != builder engine | Read both from team_assignments.yaml |
| L-GATE_VALIDATE | Validator engine != builder engine (different vendor) | Team 190 must be different LLM vendor |
| L-GATE_BUILD (Tech) | Tech validator != builder engine | Read from team_assignments.yaml |
| EXT-CP1/CP2 | Cross-vendor mandatory | Team 190 is OpenAI (if builders are Anthropic) |
| GATE_4 Tier 1 | QA != builder | Same-domain cross-engine |
| GATE_5 | Cross-vendor mandatory | LOD500 requires cross-engine sign-off |

**Dynamic resolution:** All engine assignments read from `core/definition.yaml` or `_aos/team_assignments.yaml` at invocation time. Never hardcoded in skills.

---

## Cross-Engine Command Routing

Maps each Tier 1 gate operation command to its equivalent in each engine environment.

| Command | Claude Code | Cursor Composer | Codex |
|---------|-----------|----------------|-------|
| Gate Mandate | `/AOS_gate-mandate` | `.cursorrules` §AOS Gate Operations — Gate Mandate | `SYSTEM_PROMPT.template` §Gate Operations > Gate Mandate Generation |
| QA Functional Acceptance | `/AOS_qa` | `.cursorrules` §AOS Gate Operations — QA Functional Acceptance | `SYSTEM_PROMPT.template` §Gate Operations > QA Functional Acceptance |
| Constitutional Validation | `/AOS_validate` | `.cursorrules` §AOS Gate Operations — Constitutional Validation | `SYSTEM_PROMPT.template` §Gate Operations > Constitutional Validation |
| Gate Status | `/AOS_gate-status` | `.cursorrules` §AOS Gate Operations — Gate Status Check | `SYSTEM_PROMPT.template` §Gate Operations > Gate Status |
| Governance Update | `/AOS_gov-update` | `.cursorrules` §AOS Gate Operations — Governance Update | `SYSTEM_PROMPT.template` §Gate Operations > Governance Update |

**Tier 2 commands** (archive, gov-sync, server, mail, send, project-init, domain-health, handoff, decide, help) are Claude Code only unless otherwise noted in ADR031. See `governance/directives/ADR031_MODEL_B_FILE_STRUCTURE.md` §6 for rationale.

**Machine-readable inventory (SSoT):** `lean-kit/modules/validation-quality/schemas/aos_commands_manifest.yaml` — enforced by `validate_aos_commands.sh`.

**Complete AOS command name index (Tier 1 + Tier 2, ADR031):** `/AOS_archive`, `/AOS_decide`, `/AOS_domain-health`, `/AOS_gate-mandate`, `/AOS_gate-status`, `/AOS_gov-sync`, `/AOS_gov-update`, `/AOS_handoff`, `/AOS_help`, `/AOS_mail`, `/AOS_project-init`, `/AOS_qa`, `/AOS_send`, `/AOS_server`, `/AOS_validate`.

**Engine resolution:** All commands resolve team-engine mapping dynamically from `core/definition.yaml` (hub) or `_aos/team_assignments.yaml` (spoke). Never hardcoded.

---

## Pipeline Hardening Integration

V316 scripts integrate with gate operations at defined trigger points. All scripts are engine-agnostic POSIX shell and live in `lean-kit/modules/validation-quality/scripts/`.

| Script | Trigger Point | Mode | Consumed By |
|--------|--------------|------|-------------|
| `validate_preactivation.sh` | Before mandate generation | Blocking (exit 1 aborts) | `/AOS_gate-mandate` Phase 1 |
| `prompt_staleness_check.sh` | Before prompt delivery | Advisory (exit 1 warns) | `/AOS_gate-mandate` Phase 2 |
| `archive_gate_artifacts.sh` | After gate PASS + advance | Automated (post-advance) | `/AOS_gate-mandate` post-advance |
| `validate_aos.sh` Check 15 | Post-build validation | Reporting | `validate_aos.sh` framework |

**Ordering schema:** `lean-kit/modules/validation-quality/schemas/pre_gate_ordering.yaml` encodes the Prerequisite Chain (below) as machine-readable YAML. The schema is the SSoT consumer, not the SSoT definer — the Prerequisite Chain section below remains the authoritative source.

**Gate alias resolution:** Scripts accept both canonical (`L-GATE_ELIGIBILITY`) and alias (`L-GATE_E`) forms. Aliases are defined in `pre_gate_ordering.yaml` and resolved at script entry. All internal logic and output uses canonical forms.

---

## Prerequisite Chain

```
L0 Track A:  L-GATE_ELIGIBILITY ──→ L-GATE_SPEC ──→ L-GATE_BUILD ──→ L-GATE_VALIDATE
L0 Track B:  L-GATE_ELIGIBILITY ──→ L-GATE_CONCEPT ──→ L-GATE_SPEC ──→ L-GATE_BUILD ──→ L-GATE_VALIDATE
L2:          GATE_0 ──→ GATE_1 ──→ GATE_2 ──→ GATE_3 ──→ GATE_4 ──→ GATE_5
L2.5:        EXT-CP1 ──→ PH1 ──→ PH2A ──→ PH2B ──→ PH3 ──→ PH4A ──→ EXT-CP2 ──→ PH4B ──→ PH4C ──→ PH4D ──→ PH4E ──→ PH5 ──→ PH6
```

Each gate requires the preceding gate to have `result: PASS` (or PASS_WITH_FINDINGS, CLEAR, APPROVED) before it can be activated.

### Data authority & L-GATE_BUILD (V320+)

When the dashboard engine and database are online, structured WP/team/project state is **not** advanced by hand-editing `roadmap.yaml` or other YAML — mutations go through the **API** and **`deploy_cascade`**, with files as deployed snapshots. This applies to all profiles when the DB is available; see `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` and `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` (Iron Rule #7). Hub `validate_aos.sh` **Check 19** verifies that every `team_*.md` under `_aos/governance/` includes the API-only clause (contract text, not runtime API proof).

---

*AOS-V314-WP-CANONICAL-GATES + AOS-V315-WP-CROSS-ENGINE-PARITY | Gate Registry v1.1.0 | 2026-04-13*

---

## V318 — New Checks

| Check ID | Script | Gate | Category | Description |
|----------|--------|------|----------|-------------|
| V-LOD-1 | validate_lod.sh | L-GATE_SPEC | CAT-1.8 | Frontmatter field completeness per LOD level |
| V-LOD-2 | validate_lod.sh | L-GATE_SPEC | CAT-1.11 | Required section headers per LOD level |
| V-LOD-3 | validate_lod.sh | L-GATE_SPEC | CAT-2.4 | AC numbering format in LOD400 |
| V-LOD-4 | validate_lod.sh | L-GATE_SPEC | CAT-2.5 | Placeholder text detection in LOD400 |
| V-LOD-5 | validate_lod.sh | L-GATE_SPEC | CAT-2.6 | lod_status enum compliance |
| V-LOD-6 | validate_lod.sh | L-GATE_SPEC | CAT-2.7 | version field format |
| V-LOD-7 | validate_lod.sh | L-GATE_SPEC | CAT-1.8 | spec_ref resolution in LOD500 |
| V-VERDICT | validate_verdicts.sh | L-GATE_BUILD | CAT-1.9 | Verdict YAML field completeness |
| V-GATE-1 | validate_gates.sh | L-GATE_VALIDATE | CAT-3.5 | LOD status progression validity |
| V-GATE-2 | validate_gates.sh | L-GATE_VALIDATE | CAT-3.6 | Gate history report_path existence |
| V-XENGINE | /AOS_gate-mandate | Mandate gen | CAT-3.7 | Cross-engine vendor constraint |
