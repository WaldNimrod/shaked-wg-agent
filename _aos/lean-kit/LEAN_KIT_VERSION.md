# Lean Kit Version

**version:** 3.1.7
**date:** 2026-04-16
**status:** RELEASED — Module 11.4 (Domain/Platform Separation, required L0/L2/L2.5) + Module 14 (Code Quality Infrastructure, optional)

## Contents status

| Component | Status | Details |
|-----------|--------|---------|
| templates/ | POPULATED | 5 LOD templates (LOD100, LOD200, LOD300, LOD400, LOD500) |
| team_roles/ | POPULATED | 5 role definitions (system_designer, architecture_agent, builder_agent, validator_agent, documentation_agent) |
| gates/ | POPULATED | 5 L-GATE definitions (L-GATE_ELIGIBILITY, L-GATE_CONCEPT, L-GATE_SPEC, L-GATE_BUILD, L-GATE_VALIDATE) |
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
| 3.1.4 | 2026-04-15 | Project Lifecycle Archetypes (PLA) governance layer introduced. Four archetypes: SOFTWARE (default), CONTENT_SUBSTRATE, 3D_CREATIVE, DOMAIN_AGENT. New: methodology/lifecycle-archetypes/ (5 files). PROFILE_SELECTION_GUIDE.md v1.1.0 (two-step decision). roadmap.yaml.template: stage_mapping + lifecycle_archetype fields added. Backwards-compatible: absent field = SOFTWARE. |
| 3.1.5 | 2026-04-15 | Module 13 (content-wp-lifecycle) canonicalized. Defines the WP execution model for CONTENT_SUBSTRATE projects: LOD100→LOD200→LOD300→LOD400→Build→Validate, 4 source types, Decision Package template (mandatory), 5 LOD templates. Proven in nimrod-book. No skipping stages. |
| 3.1.6 | 2026-04-16 | V320 DB Full Migration governance lock: Check 19 added to validate_aos.sh (API-only mutations Iron Rule #7 enforcement). All 17 team contracts updated with API-only clause. Iron Rule #7 extended in AOS_CONCEPT_AND_PRINCIPLES.md to cover all profiles including L0. |
| 3.1.7 | 2026-04-16 | Module 11.4 (Domain/Platform Separation): binding DOM-PLAT-1/2/3 rules; Module 11 required_by_profiles → [L0, L2, L2.5]; DOMAIN_RULES_TEMPLATE added. Module 14 (code-quality-infrastructure, optional): PRE_COMMIT_PATTERN, CI_QUALITY_GATES_PATTERN, DOMAIN_CODE_STANDARDS_TEMPLATE. Reference impl: TikTrack Phoenix. |

## Snapshot model

Projects that adopt the Lean Kit clone at a specific version tag.
This file records which version is in use.
No auto-sync. Updates via Team 100 propagation notice.

Reference: `methodology/ARCHITECT_DIRECTIVE_METHODOLOGY_DEPLOYMENT_SPLIT_v1.0.0.md` §3
