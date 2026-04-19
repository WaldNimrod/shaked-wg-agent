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
L-GATE definitions (L-GATE_ELIGIBILITY / L-GATE_CONCEPT / L-GATE_SPEC / L-GATE_BUILD / L-GATE_VALIDATE), Track A (4-gate) and Track B (5-gate) sequences,
handoff procedure, rollback policy. Optional for simple projects.

## Contents
| File | Description |
|------|-------------|
| gates/L-GATE_ELIGIBILITY.md | Entry eligibility gate |
| gates/L-GATE_CONCEPT.md | Concept review (Track B only) |
| gates/L-GATE_SPEC.md | Spec + authorization gate |
| gates/L-GATE_BUILD.md | Build + QA gate |
| gates/L-GATE_VALIDATE.md | Validate + lock (cross-engine) |
| POST_GATE_ARCHIVE_PROCEDURE.md | Post-gate archive runbook (Iron Rule #15) |

## Dependencies
- Requires: Module 01 (gates reference roadmap.yaml schema)

## Profile Inclusion
| Profile | Status |
|---------|--------|
| L0 | OPTIONAL (recommended for structured projects) |
| L2 | REQUIRED |
| L3 | REQUIRED |
