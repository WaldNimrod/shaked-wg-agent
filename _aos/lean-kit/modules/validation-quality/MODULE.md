---
module: 8
id: validation-quality
title: Validation & Quality
version: 3.1.6
status: ACTIVE
category: TOOLING
required_by_profiles: [L0, L2, L3]
depends_on: [project-governance]
---

# Module 08 — Validation & Quality

## Purpose

Universal hub validation via `validate_aos.sh`, L-GATE_BUILD exit criterion (PASS / 0 FAIL on applicable checks), and companion scripts (`validate_lod`, verdicts, gates). On **agents-os hub** with all `active_modules` enabled, the script runs **19 checks** (as of Lean Kit 3.1.6 / V320).

## Hub check suite (agents-os, full modules)

| Checks | Topic |
|--------|--------|
| 1–15 | YAML, cross-engine, specs, metadata, teams, profile, lean-kit snapshot, governance completeness, boundaries, etc. |
| 16 | AOS slash-command manifest (`validate_aos_commands.sh`) |
| 17 | `PROJECT_CONTEXT.md` Part 1a headings (hub) |
| 18 | `_aos/` write authority — non-governance teams must not grant `_aos/` in `writes_to` |
| 19 | Every `team_*.md` under `_aos/governance/` includes the **API-only / Iron Rule #7** structured-data clause |

Spoke projects may run a **subset** of checks depending on `active_modules` in `_aos/metadata.yaml` and profile.

## Contents

| File | Description |
|------|-------------|
| `scripts/validate_aos.sh` | Universal validation script (module-scoped when `active_modules` set) |
| `scripts/validate_lod.sh` | LOD document validator; L-GATE_SPEC pre-condition |
| `scripts/validate_lod.py` | Python core for validate_lod.sh |
| `scripts/validate_verdicts.sh` | Verdict file structure validator; L-GATE_BUILD |
| `scripts/validate_verdicts.py` | Python core |
| `scripts/validate_gates.sh` | Gate history integrity; L-GATE_VALIDATE |
| `scripts/validate_gates.py` | Python core |
| `GATE_REGISTRY.md` | Gate prerequisites and command cross-reference |

## Data authority (V320+)

Structured WP/team/project mutations when the DB is online are **not** validated by editing YAML by hand — see `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` (hub repo) and `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` Iron Rule #7. Check 19 enforces that team contracts **say** this; runtime API compliance is operational.

## Related

- `methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md` — Phase 5 uses hub **19** checks post-propagation.
- `lean-kit/modules/project-governance/GETTING_STARTED.md` — bootstrap validation expectations.
