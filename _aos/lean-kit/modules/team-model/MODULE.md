---
module: 3
id: team-model
title: Team & Role Model
version: 3.1.1
status: ACTIVE
category: CORE
required_by_profiles: [L0, L2, L3]
depends_on: [project-governance]
---

# Module 03 — Team & Role Model

## Purpose
Role type definitions (6 roles), two-layer naming model, slug regex, cross-engine Iron Rule.

## Contents
| File | Description |
|------|-------------|
| roles/ROLE_SYSTEM_DESIGNER.md | Human orchestrator |
| roles/ROLE_ARCHITECTURE_AGENT.md | Spec author (LOD200/LOD400) |
| roles/ROLE_BUILDER_AGENT.md | Implementation agent |
| roles/ROLE_VALIDATOR_AGENT.md | Cross-engine QA |
| roles/ROLE_DOCUMENTATION_AGENT.md | Technical writing (optional) |
| roles/ROLE_GATEWAY_AGENT.md | Gate coordination (optional) |

## Dependencies
- Requires: Module 01 (roles reference team_assignments.yaml schema)

## Profile Inclusion
| Profile | Status |
|---------|--------|
| L0 | CORE |
| L2 | CORE |
| L3 | CORE |
