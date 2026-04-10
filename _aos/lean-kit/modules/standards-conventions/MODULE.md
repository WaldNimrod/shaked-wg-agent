---
module: 11
id: standards-conventions
title: Standards & Conventions
version: 3.1.1
status: ACTIVE
category: STANDARDS
required_by_profiles: []
depends_on: []
---

# Module 11 — Standards & Conventions

## Purpose
Coding standards and conventions. Each standard is independently optional per project.
The category is open for future standards (accessibility, security, testing, etc.).

## Contents
| Standard | ID | Activation Condition |
|----------|-----|---------------------|
| RTL & Bidirectional UI | 11.1 (rtl-bidi) | `rtl: true` in project profile |
| Multi-Project Docker Workstation | 11.2 (multi-project-docker) | Docker services present in project |
| (future) | 11.x | Per-standard conditions |

## Sub-standards
- `rtl-bidi/RTL_BIDI_STANDARD_v1.0.0.md` — RTL/BiDi UI conventions
- `MULTI_PROJECT_DOCKER_WORKSTATION_v1.0.0.md` — Port registry and conflict resolution for shared workstations
