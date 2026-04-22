# Module — Design Studio

**Module:** design-studio
**Version:** 1.0.0
**Added:** 2026-04-22
**Owner:** Team 35 (Design Studio / claude-design) — templates; Team 100 — module governance
**Profile:** L2 / L2.5 (Track B with design-studio loop)

## Purpose

Templates and guides for invoking **Team 35** (Claude Design sandbox) within the Track B design-studio loop. Covers how to brief Team 35, what artifacts to expect, how to iterate, and how to write a canonical Design Brief.

## When to use

Use this module whenever a WP includes a Track B design-studio loop — i.e., whenever LOD200 must be followed by wireframes before LOD300 can be authored. Mandatory read for Team 100 before issuing any mandate to Team 35.

## Entry point

Start with [`HANDOFF_GUIDE_v1.0.0.md`](HANDOFF_GUIDE_v1.0.0.md) — full guide for briefing Team 35, iteration protocol, and handoff structure.

## Key files

| File | Purpose |
|------|---------|
| `HANDOFF_GUIDE_v1.0.0.md` | Full guide — who Team 35 is, how to brief, what you get back, how to iterate |
| `templates/BRIEF.template.md` | Copy-paste Design Brief template (fill before every mandate) |
| `templates/HANDOFF.template.md` | Handoff Package index template (Team 35 fills; Team 100 reads) |
| `templates/REVISION_REQUEST.template.md` | Revision Request template (Team 100 files after receiving handoff) |
| `templates/CLARIFICATION_REQUEST.template.md` | Clarification Request template (Team 35 files when brief is under-specified) |
| `checklists/before-you-brief.md` | Brief completeness checklist — answer all items before sending mandate |
| `checklists/anti-patterns.md` | Common brief failures that will produce a CLARIFICATION_REQUEST |

## Quick start

1. Read `checklists/before-you-brief.md` — answer every item
2. Copy `templates/BRIEF.template.md` into `_COMMUNICATION/team_100/[WP-ID]/BRIEF_{WP_ID}_{SCOPE}_{DATE}_v1.0.0.md`
3. Fill in all sections
4. Issue mandate to Team 35 referencing the brief
5. When Team 35 delivers `HANDOFF_*.md`, review against `checklists/before-you-brief.md` checklist items
6. Respond with APPROVED / APPROVED_WITH_REVISIONS / REJECTED (use `templates/REVISION_REQUEST.template.md` if revisions needed)

## Governance

Module governs the interface between Team 100 and Team 35. Team 35's canonical governance contract: `core/governance/team_35.md` (hub SSoT) → propagated to all spokes via `_aos/governance/team_35.md`.
