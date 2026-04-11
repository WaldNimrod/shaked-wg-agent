---
module: 12
id: managed-pipeline
title: L2.5 Managed Agent Pipeline
version: 1.0.0
status: CANONICAL
canonicalized: "2026-04-11"
canonicalized_by: team_00
canary_wp: "SBXF-P001-WP-L25-001"
canary_result: "SUCCESSFUL — 6 phases, 4 FCP cycles (0 FCP-3/4), 2 human gates APPROVED first pass"
category: WORKFLOW
required_by_profiles: [L2.5]
depends_on: [project-governance, gate-workflow, team-model, document-lifecycle, agent-activation]
---

# Module 12 — Managed Agent Pipeline (L2.5)

## Purpose
This module defines the L2.5 execution profile: a managed, personally-calibrated,
multi-project pipeline that runs the full WP lifecycle with minimal human intervention.

L2.5 sits between L2 (structured pipeline, manual agent activation) and L3 (future
autonomous CLI). The current execution model uses Claude Code (Team 100) as orchestrator
with the Agent tool for subagent spawning. The production target is the Claude Agent SDK
managed loop — see `architecture/CLAUDE_SDK_MIGRATION_PATH.md`.

## Human Gates (exactly 2 per WP)
1. **Phase 3 Gate** — LOD300 + Mockup approval (before implementation begins)
2. **Phase 5 Gate** — UX final authority (Gate 4 canonical exit)

## Module Contents

### activation/
Role-specific activation prompts for each L2.5 agent.
In SDK model: these become agent system prompts with registered tool schemas.
- `ACTIVATION_ORCHESTRATOR.md` — L2.5 pipeline orchestrator (Team 100 in L2.5 mode)
- `ACTIVATION_SPEC_AGENT.md` — LOD production agent (LOD200, LOD400) + R1/R3 research
- `ACTIVATION_ARCH_AGENT_L25.md` — Domain architect (LOD300) + R2 research
- `ACTIVATION_CONST_VALIDATOR.md` — Constitutional validator (cross-model within loop; cross-vendor via EXT-CP)
- `ACTIVATION_MOCKUP_AGENT.md` — State diagram + screens (asks format preference first)
- `ACTIVATION_GATEWAY_AGENT_L25.md` — Work plan + mandate generator + PWA fixes
- `ACTIVATION_QA_AGENT_L25.md` — E2E QA agent (cross-model from builders)
- `ACTIVATION_TECH_VALIDATOR_L25.md` — Technical correctness + architectural alignment
- `ACTIVATION_DOC_AGENT_L25.md` — LOD500 + AS_MADE_LOCK producer

### artifacts/
Templates and protocols for L2.5-specific artifacts:
- `LOD100_L25_FORM.md` — Canonical LOD100 entry ticket (L2.5 specific fields)
- `LOD_RESEARCH_PROTOCOL.md` — R1/R2/R3 research deepening framework (read by all spec/arch agents)
- `FCP_CLASSIFICATION_GUIDE.md` — FCP-1 through FCP-4 decision tree + circuit breaker
- `PHASE_GATE_TEMPLATE.md` — Human gate presentation format (Phase 3 + Phase 5)

### runbooks/
Operational guides for running and setting up L2.5:
- `ORCHESTRATOR_RUNBOOK.md` — Complete step-by-step execution guide (read first)
- `SANDBOX_SETUP.md` — Environment setup → sandbox experiment → live test flight

### architecture/ (research items — to be populated)
- `CLAUDE_SDK_MIGRATION_PATH.md` — Target production architecture (Claude Agent SDK)

## Iron Rules (L2.5 specific)
1. LOD300 is ALWAYS required (L2.5 = always Track B). No exceptions.
2. Research rounds (R1/R2/R3) are mandatory before each LOD production step.
3. Mockup agent asks format preference before producing (Option C or HTML).
4. Cross-engine validation MUST be enforced at every LOD production step.
5. Human gates are NOT delegatable — Team 00 (System Designer) only.
6. FCP classification MUST precede any Phase 5 rejection routing.
7. Circuit breaker: FCP-3 ≥ 3 cycles OR FCP-4 ≥ 1 cycle → Team 00 escalation.
8. Operator DNA (`core/operator_dna.yaml`) is read at session start before any agent spawns.
9. Parallelization: Phase 2 specs may parallelize; Phase 4 implementation is serialized.

## Profile Declaration
A WP is L2.5 when:
- LOD100 field `profile: L2.5` is set by Team 00 at creation
- Profile is immutable once declared
- Complexity escalation mid-WP requires a new LOD100

## Execution Architecture

### Current (Experiment): Claude Code as Orchestrator
- Orchestrator: Claude Code (Team 100) reads ORCHESTRATOR_RUNBOOK.md
- Subagents: spawned via Agent tool, receive activation prompts as context
- State: tracked in project roadmap.yaml gate_history
- Human gates: Orchestrator pauses and presents in conversation

### Target (Production): Claude Agent SDK Managed Loop
- Orchestrator: Python managed agent with registered tools
- Tools: `read_artifact`, `write_artifact`, `spawn_subagent`, `update_pipeline_state`, `present_human_gate`
- Human gate tool pauses the managed loop, triggers notification to Team 00
- See: `architecture/CLAUDE_SDK_MIGRATION_PATH.md`

### Research Items (open)
- Cowork environment: evaluate built-in tools for pipeline execution
- Terminal / home server: evaluate for long-running phase execution (phases 4C-4D)
- Both to be evaluated before production SDK migration

## Relation to L3
L2.5 with the two human gates automated = L3:
- Phase 3 human gate → automated LOD300 quality check
- Phase 5 human gate → automated acceptance criteria coverage verification
L2.5 is the training ground: every WP produces quality data toward L3 trust thresholds.

## Relation to L2
L2 handles simple WPs (possibly Track A, fewer phases, lighter governance).
L2.5 handles complex WPs (always Track B, research rounds, full 6-phase pipeline).
Profile is declared at LOD100 creation by Team 00. Not automatic — deliberate.
