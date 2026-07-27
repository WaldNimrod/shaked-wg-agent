---
module: 1
id: project-governance
title: Project Governance Structure
version: 3.1.1
status: ACTIVE
category: CORE
required_by_profiles: [L0, L2, L3]
depends_on: []
---

# Module 01 — Project Governance Structure

## Purpose
Defines the `_aos/` directory layout, YAML schemas for roadmap.yaml and team_assignments.yaml,
ideas.json schema, project README template, and the example project.

## Contents
| File | Description |
|------|-------------|
| DOMAIN_DOC_ARCHIVE_SWEEP_PROCEDURE_v1.0.0.md | Uniform per-domain code-doc + full-archival + v4-quarantine sweep (weak-engine-safe; anti-v4-drift). Returns a standardized report → team_120 central review. |
| V4_LEGACY_QUARANTINE_CONVENTION_v1.0.0.md | Machine-readable `aos_lifecycle: V4_LEGACY_QUARANTINE` marker + domain quarantine index (companion to the sweep procedure). |
| config_templates/roadmap.yaml.template | WP state registry schema v1.1 |
| config_templates/ideas.json.template | Idea pipeline schema (pre-GATE_0 incubator) |
| config_templates/team_assignments.yaml.template | Team registry with role types |
| config_templates/README.md.template | _aos/ README template |
| examples/example-project/ | Full Track A example with 2 WPs and LOD chain |
| examples/EXAMPLE_ONLY.md | Marker: this is not a real project |
| scripts/migrate_sfa_roadmap.py | SFA migration spec (Phase 4) |

## Dependencies
None (root module).

## Profile Inclusion
| Profile | Status |
|---------|--------|
| L0 | CORE |
| L2 | CORE |
| L3 | CORE |
