---
id: ADR037_CODE_STANDARDS_CITATION_AND_MAINTENANCE
title: "ADR-037 — CODE_STANDARDS Qualified Citations and Long-Term Maintenance"
version: "1.0.0"
status: APPROVED
author: Team 100 (Chief System Architect)
approved_by:
  - team_00
  - team_100
approval_date: "2026-04-18"
adr_ref: ADR-037
---

# ADR-037 — CODE_STANDARDS Qualified Citations and Maintenance

## 1. Purpose

`_aos/context/CODE_STANDARDS.md` is **per project**. The same **CS-N** label can mean different things in **agents-os (hub)** vs **TikTrack Phoenix** vs other spokes. Unqualified `[CS-N]` references in LOD400 acceptance criteria cause **cross-repo drift** and invalid QA traceability.

This directive locks **citation format** and **maintenance triggers** for all AOS-managed projects.

## 2. Decisions

### 2.1 Qualified citations (binding)

In every **LOD400** (and LOD300 where ACs reference code standards):

- **Forbidden:** Bare `[CS-N]` or `[CS-2]` with no repository / path.
- **Required:** Each reference includes **project or repo label** + **path** + **CS-N**, for example:
  - `[agents-os _aos/context/CODE_STANDARDS.md CS-2]`
  - `[TikTrack-Phoenix_AOSProject _aos/context/CODE_STANDARDS.md CS-4]`

Normative copy also lives in `agents-os` at `_aos/context/CODE_STANDARDS.md` § “How to cite (cross-repo)”.

### 2.2 Maintenance triggers (binding)

When implementation changes **public contract** visible to agents or operators, update documentation **in the same change set** (PR / commit series) where feasible:

| Change type | Update |
|-------------|--------|
| HTTP API route contract | `core/` docstrings or route `summary`/`description`; `documentation/.../AGENTS_OS_V3_API_REFERENCE.md` if listed there |
| Default port / URL | `AGENTS_OS_V3_NETWORK_PORTS_AND_UI_ENTRY_*.md`, `port-registry.yaml` (Team 60), `_aos/context/CODE_STANDARDS.md` CS-6 if rule text changes |
| CLI / script flags | `core/README.md` or script header; CS-5 |
| New CS row | Team 100 proposes → Team 00 approves → bump `CODE_STANDARDS.md` version footer |

Structured roadmap/WP state when DB is online: **API-only** mutations per ADR034 / Iron Rule #7.

### 2.3 Roles

| Role | Responsibility |
|------|----------------|
| Team 100 | Proposes `CODE_STANDARDS` amendments; aligns hub + lean-kit template |
| Team 70 | Drafts long-form docs and communication artifacts; does not override product code without mandate |
| Builders | Implement ACs using **qualified** CS references only |
| Team 190 | L-GATE_SPEC / L-GATE_VALIDATE — verifies citation discipline and PAC-DOC alignment |

## 3. Compliance

| Artifact | Requirement |
|----------|---------------|
| `lean-kit/.../DOMAIN_CODE_STANDARDS_TEMPLATE.md` | “How to Use” references this ADR |
| Hub `_aos/context/PROJECT_CONTEXT.md` | Points to `_aos/context/CODE_STANDARDS.md` and this ADR |
| Spoke `PROJECT_CONTEXT.md` | Same citation rule when `CODE_STANDARDS` is used in WPs |

## 4. Amendment

New version file (not in-place edit of LOCKED text after promotion): `ADR037_*_v1.1.0.md` with Team 00 approval for material changes.

---

**log_entry | ADR037 | APPROVED | 2026-04-18 | CODE_STANDARDS qualified citations + maintenance**
