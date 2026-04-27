---
document_type: ADR
id: ADR_SELF_REFERENTIAL_BOUNDARY
author: team_100
date: "2026-04-12"
status: ACCEPTED
source_idea: IDEA-001
work_package: AOS-V313-WP-MATURITY
---

# ADR: Self-Referential Architecture Boundary

## Context

AOS governs itself through its own process. This creates a unique architectural challenge: the same system that defines governance for spoke projects must also govern its own development. Two primary SSoT files track different concerns:

- **`core/definition.yaml`** — WHO/HOW: team definitions, gate model, phase configuration, engine assignments
- **`_aos/roadmap.yaml`** — WHAT/WHEN: work package tracking, milestone state, gate history, schedule

## Decision

### Boundary Rule

Neither file contains information belonging to the other's domain:

| Concern | SSoT File | Examples |
|---------|-----------|----------|
| Team identity, roles, engines | `definition.yaml` | team_100 is claude-code, team_190 is openai-codex |
| Gate model, phase sequence | `definition.yaml` | L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE |
| WP status, schedule, progress | `roadmap.yaml` | AOS-V313-WP-MATURITY is IN_PROGRESS |
| Milestone planning | `roadmap.yaml` | V3.1.3 contains 1 WP |

### When AOS modifies its own L2 engine

When AOS development changes the engine itself (e.g., adding a new API endpoint, modifying the gate model):

1. The **work** is tracked in `roadmap.yaml` as a WP like any other project
2. The **structural changes** to teams/gates/phases go in `definition.yaml`
3. The overlap is the WP that describes the structural change — the WP tracks when/status, definition.yaml holds the resulting structure

### Enforcement

This boundary is enforced by **manual discipline**, not automated checks. `validate_aos.sh` does not check this boundary because:

1. The semantic distinction (WHO/HOW vs WHAT/WHEN) cannot be reliably verified by pattern matching
2. The overlap cases (WPs that modify the engine) require human judgment
3. The primary risk (duplication) is low given the small number of maintainers

## Consequences

- Teams must understand which file to modify for which concern
- Code reviews should flag any commit that modifies both files unless the change is a WP that legitimately affects engine structure
- Future L3 automation may formalize this boundary with schema validation

## References

- IDEA-001: Governance boundary analysis
- `methodology/AOS_CONCEPT_AND_PRINCIPLES.md`: AOS self-referential nature
- `CLAUDE.md` §SSoT Map: directory-level SSoT assignments
