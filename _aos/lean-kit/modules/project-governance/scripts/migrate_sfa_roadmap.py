#!/usr/bin/env python3
"""
migrate_sfa_roadmap.py — SFA Roadmap Migration Specification
=============================================================
STATUS: SPECIFICATION ONLY — not executable until WP-6

This document specifies the deterministic migration steps that WP-6
(SmallFarmsAgents migration) must perform on SFA's roadmap.yaml and
team_assignments.yaml when moving governance from agents-os/projects/sfa/
to SmallFarmsAgents/_aos/.

Reference: WP-0C (Schema v1.1 Freeze), BLOCKER-2 (gate_history normalization)

MIGRATION TASKS:
================

1. FIELD RENAMES (roadmap.yaml):
   - team_lead      → assigned_builder
   - validator      → assigned_validator

2. GATE_HISTORY NORMALIZATION (BLOCKER-2):
   Current (broken — pipe-delimited, parses as single string):
     gate_history:
       - gate: L-GATE_E | result: PASS | date: "2026-04-04"

   Target (structured YAML):
     gate_history:
       - gate: L-GATE_E
         result: PASS
         date: "2026-04-04"
         notes: ""

3. ADD MISSING FIELDS:
   - project.active_milestone: (from existing active_milestone field — already present in SFA)
   - project.notes: (preserve existing or add empty)
   - WP.milestone_ref: (map from existing milestone_ref field — already present in SFA)

4. SPEC_REF REWRITE:
   Current: spec_ref: "projects/sfa/SFA_P001_WP001_LOD200_SPEC.md"
   Target:  spec_ref: "_aos/work_packages/SFA-P001-WP001/LOD200_spec.md"

5. TEAM_ASSIGNMENTS.YAML MIGRATION:
   Current field names → Target field names:
     lean_role: SPEC_AUTHOR       → role_type: architecture_agent
     lean_role: ORCHESTRATOR      → role_type: gateway_agent
     lean_role: IMPLEMENTATION_TEAM → role_type: builder_agent
     lean_role: CONSTITUTIONAL_VALIDATOR → role_type: validator_agent
     lean_role: ARCH_APPROVER     → role_type: system_designer

   Current team IDs → Target slugs:
     sfa_team_100 → sfa_arch
     sfa_team_10  → sfa_gate
     sfa_team_20  → sfa_build
     sfa_team_50  → sfa_val
     nimrod        → sfa_sd

6. ACTIVE MILESTONE MAPPING (per Team 00 clarification):
   SFA Milestone → roadmap.yaml WP
     M10.1 (COMPLETE) → DO NOT migrate (historical)
     M10.2 (ACTIVE)   → SFA-M10-WP002, status: IN_PROGRESS, current_lean_gate: L-GATE_B
     M10.3 (ACTIVE)   → SFA-M10-WP003, status: IN_PROGRESS, current_lean_gate: L-GATE_B
     M10.4 (ACTIVE)   → SFA-M10-WP004, status: IN_PROGRESS, current_lean_gate: L-GATE_B
     M10.5 (PLANNED)  → SFA-M10-WP005, status: PLANNED, current_lean_gate: L-GATE_E

7. SLUG FORMAT VALIDATION:
   All migrated team IDs must match: ^[a-z][a-z0-9]*_[a-z]+$
   Run validate_aos.sh after migration to confirm.

8. POST-MIGRATION LINT:
   - Zero remaining 'team_lead' or 'validator' keys in output roadmap.yaml
   - Zero remaining 'lean_role' keys in output team_assignments.yaml
   - Zero pipe-delimited gate_history entries
   - All spec_ref paths resolve to existing files within SmallFarmsAgents repo
"""
