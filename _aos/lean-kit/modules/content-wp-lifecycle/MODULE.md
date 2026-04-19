---
module: 13
id: content-wp-lifecycle
title: Content WP Lifecycle (CONTENT_SUBSTRATE)
version: 1.0.0
status: ACTIVE
category: WORKFLOW
required_by_profiles: [L0]
depends_on: [document-lifecycle, project-governance]
lifecycle_archetype: CONTENT_SUBSTRATE
---

# Module 13 — Content WP Lifecycle (CONTENT_SUBSTRATE)

## Purpose

Defines the canonical Work Package lifecycle for projects whose primary deliverable
is a knowledge artifact — a structured corpus of information consumed by agents,
humans, or hybrid workflows.

Applies when `lifecycle_archetype: CONTENT_SUBSTRATE` is declared in `roadmap.yaml`.

**Core principle:** Every unit of information entering the corpus — regardless of source —
goes through the same LOD funnel. No stage skipping.

## Contents

| File | Description |
|------|-------------|
| `LIFECYCLE_CONTENT_WP.md` | Canonical lifecycle definition — authoritative spec |
| `templates/LOD100_CONTENT_SOURCE.md` | LOD100 template: raw source intake |
| `templates/LOD200_CONTENT_PLACEMENT.md` | LOD200 template: placement + go/no-go |
| `templates/LOD300_CONTENT_STRUCTURE.md` | LOD300 template: structure design |
| `templates/LOD400_CONTENT_SPEC.md` | LOD400 template: exact paragraphs, zero TBD |
| `templates/DECISION_PACKAGE.md` | Mandatory decision package (min 3 options) |

## Information Source Types

| Source | Trigger |
|--------|---------|
| Message / Idea | Ad-hoc note from domain owner |
| Research session | Team 80 domain investigation |
| File / document | Provided by domain owner |
| Scheduled scan | Automated sweep (Gmail, Drive, etc.) |

## LOD Funnel (mandatory — no skipping)

```
LOD100 → LOD200 → LOD300 → LOD400 → L-GATE_BUILD → L-GATE_VALIDATE
```

| LOD | Question | Gate |
|-----|----------|------|
| LOD100 | What is it? Is it relevant at all? | L-GATE_ELIGIBILITY |
| LOD200 | Where does it belong? Go/no-go. | L-GATE_SPEC (initial) |
| LOD300 | What is the structure? Format? Sources? | L-GATE_SPEC (confirm) |
| LOD400 | Exact file, location, copy-paste wording. Zero TBD. | L-GATE_SPEC (final) |
| Build | Update files exactly per LOD400. LOD500 draft. | L-GATE_BUILD |
| Validate | Team 190 cross-engine. AC-CS-01..06. | L-GATE_VALIDATE |

## Dependencies

- Module 04 (document-lifecycle): LOD100–LOD400 standard definitions
- Module 01 (project-governance): roadmap.yaml schema, gate spine

## Profile Inclusion

| Profile | Status |
|---------|--------|
| L0 | CORE (CONTENT_SUBSTRATE projects) |
| L2 | OPTIONAL |
| L3 | OPTIONAL |

## Proven in

- nimrod-book (WaldNimrod/nimrod-book) — canonical first implementation, 2026-04-15
