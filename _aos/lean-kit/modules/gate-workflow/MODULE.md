---
module: 2
id: gate-workflow
title: Gate & Workflow
version: 3.1.1
status: ACTIVE
category: WORKFLOW
required_by_profiles: [L2, L3]
depends_on: [project-governance]
---

# Module 02 — Gate & Workflow

## Purpose
L-GATE definitions (E/C/S/B/V), Track A (4-gate) and Track B (5-gate) sequences,
handoff procedure, rollback policy. Optional for simple projects.

## Contents
| File | Description |
|------|-------------|
| gates/L-GATE_E_ELIGIBILITY.md | Entry eligibility gate |
| gates/L-GATE_C_CONCEPT.md | Concept review (Track B only) |
| gates/L-GATE_S_SPEC_AND_AUTH.md | Spec + authorization gate |
| gates/L-GATE_B_BUILD_AND_QA.md | Build + QA gate |
| gates/L-GATE_V_VALIDATE_AND_LOCK.md | Validate + lock (cross-engine) |

## Dependencies
- Requires: Module 01 (gates reference roadmap.yaml schema)

## Profile Inclusion
| Profile | Status |
|---------|--------|
| L0 | OPTIONAL (recommended for structured projects) |
| L2 | REQUIRED |
| L3 | REQUIRED |
