---
module: 11
id: standards-conventions
title: Standards & Conventions
version: 3.1.7
status: ACTIVE
category: STANDARDS
required_by_profiles: [L0, L2, L2.5]
depends_on: []
---

# Module 11 — Standards & Conventions

## Purpose
Coding standards, conventions, and domain/platform separation policy. Each standard is independently optional per project.
The category is open for future standards (accessibility, security, testing, etc.).

## Contents
| Standard | ID | Activation Condition |
|----------|-----|---------------------|
| RTL & Bidirectional UI | 11.1 (rtl-bidi) | `rtl: true` in project profile |
| Multi-Project Docker Workstation | 11.2 (multi-project-docker) | Docker services present in project |
| Domain SSOT documentation patterns (templates) | 11.3 (domain-doc-patterns) | Optional — per spoke when closing research/build drift |
| Domain/Platform Separation | 11.4 (domain-platform-separation) | Required for all L0/L2/L2.5 projects |

## Sub-standards
- `rtl-bidi/RTL_BIDI_STANDARD_v1.0.0.md` — RTL/BiDi UI conventions
- `MULTI_PROJECT_DOCKER_WORKSTATION_v1.0.0.md` — Port registry and conflict resolution for shared workstations
- `DOMAIN_PLATFORM_SEPARATION_STANDARD_v1.0.0.md` — Binding platform/domain boundary rules (DOM-PLAT-1/2/3)

## Optional templates (11.3 — domain scope only)

Generic **documentation patterns** for spokes — **not** gate verdict templates (those stay in `validation-quality/templates/`).

| Template | Purpose |
|----------|---------|
| `templates/DOMAIN_SSOT_MATURITY_CHECKLIST_TEMPLATE_v1.0.0.md` | KPI-style maturity checklist for domain SSOT |
| `templates/AC_TO_STANDARD_ID_MAPPING_TEMPLATE_v1.0.0.md` | LOD400 AC ↔ standard crosswalk |
| `templates/CONVENTION_EXCEPTION_MAP_TEMPLATE_v1.0.0.md` | Documented deviations from a convention |

Copy into the domain repo; do not treat as hub canon text.

## Standard 11.4 templates

| Template | Purpose |
|----------|---------|
| `templates/DOMAIN_RULES_TEMPLATE.md` | Generic `## [DOMAIN] Domain Rules` template for new domain onboarding GCRs |
