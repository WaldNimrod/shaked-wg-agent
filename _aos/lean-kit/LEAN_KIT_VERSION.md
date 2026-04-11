# Lean Kit Version

**version:** 3.1.3
**date:** 2026-04-11
**status:** RELEASED — L2.5 Managed Pipeline Canonicalized

## Contents status

| Component | Status | Details |
|-----------|--------|---------|
| templates/ | POPULATED | 5 LOD templates (LOD100, LOD200, LOD300, LOD400, LOD500) |
| team_roles/ | POPULATED | 5 role definitions (system_designer, architecture_agent, builder_agent, validator_agent, documentation_agent) |
| gates/ | POPULATED | 5 L-GATE definitions (L-GATE_E, L-GATE_C, L-GATE_S, L-GATE_B, L-GATE_V) |
| config_templates/ | POPULATED | roadmap.yaml.template, team_assignments.yaml.template |
| examples/ | POPULATED | example-project/ with full Track A L-GATE sequence (2 WPs, LOD chain) |

## Version history

| Version | Date | Change |
|---------|------|--------|
| 0.1.0-scaffold | 2026-04-02 | Initial repository scaffold (directories created) |
| 0.1.0 | 2026-04-05 | All components populated (Team 170 WP002). Scaffold label removed. Status corrected from EMPTY. |
| 3.1.0 | 2026-04-05 | AOS v3.1.0 RELEASED. Hub-and-Spoke governance deployed across 4 projects. Schema v1.1, validate_aos.sh (9 checks), 6 role types, VERSION_POLICY. |
| 3.1.1 | 2026-04-05 | Modular restructure: 11 modules (4 categories), profile system (L0/L2/L3), MODULE_INDEX.md. Gate model now OPTIONAL. Standards category (Module 11) with RTL/BiDi. Full migration, no shims. |
| 3.1.2 | 2026-04-08 | Dashboard v2: 9 HTML pages, 10 JS modules, CSS design system. FastAPI backend (21+ endpoints). SEC-001 fail-closed actor model. PERF-002 batch resolver. Full pipeline state UI (7 states). Config CRUD. ValidationCycleUI shared component. Project type (AOS Project/Spoke). Onboarding template with MCP section. |
| 3.1.3 | 2026-04-11 | L2.5 Managed Agent Pipeline canonicalized. Module 12 status: EXPERIMENTAL → CANONICAL. Profile L2.5.yaml added. L25_QUICK_REFERENCE.md added. Canary WP SBXF-P001-WP-L25-001 completed successfully (11 phases, AS_MADE_LOCK applied). |

## Snapshot model

Projects that adopt the Lean Kit clone at a specific version tag.
This file records which version is in use.
No auto-sync. Updates via Team 100 propagation notice.

Reference: `methodology/ARCHITECT_DIRECTIVE_METHODOLOGY_DEPLOYMENT_SPLIT_v1.0.0.md` §3
