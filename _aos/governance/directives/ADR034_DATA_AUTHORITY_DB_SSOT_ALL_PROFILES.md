# ADR034 — Data Authority: DB-as-SSoT for All Profiles (V320)

**Type:** Architecture Decision Record
**Status:** LOCKED
**Date:** 2026-04-16
**Authority:** Team 00 (principal) + Team 100 (chief architect)
**Work Package:** V320 DB Full Migration
**Supersedes:** AOS_CONCEPT_AND_PRINCIPLES.md Iron Rule #7 (prose only — this ADR makes it enforcement-grade)

---

## Decision

All mutations to structured AOS data — for **every project profile (L0, L2, L2.5, L3)** — MUST flow through the API when the database is online. The database (`work_packages`, `projects`, `teams` tables) is the Single Source of Truth. Files (`roadmap.yaml`, `definition.yaml`, `projects.yaml`) are **read-only deployed snapshots** produced by `deploy_cascade()`.

---

## Context

The `ENGINE-SSOT` WP (AOS-V312-WP-ENGINE-SSOT, LOD500_LOCKED, 2026-04-14) implemented DB-as-SSoT for L2 projects. It explicitly deferred L0 canonicalization to IDEA-040, leaving L0 projects in a file-centric mode:

- L0 roadmap advances called `advance_stage.sh` (shell script writing to YAML)
- L0 API routes read/wrote YAML directly
- `deploy_cascade()` only pushed to hub `_aos/roadmap.yaml`
- No `projects` table existed in the DB
- `lifecycle_archetype` was file-only (in `_aos/projects.yaml`)

This created drift, required manual status file updates, and allowed unauthorized bypasses of the data flow by direct file edits.

---

## Ruling

### R1 — Universal DB Authority

When `AOS_V3_DATABASE_URL` is set and the database is reachable, the following data is authoritative in the DB only:

| Data type | DB table | File (snapshot) |
|-----------|----------|-----------------|
| Work package status, gate, lod_status | `work_packages` | `roadmap.yaml` (deployed snapshot) |
| Team engine, environment | `teams` | `definition.yaml` (deployed snapshot) |
| Project metadata, profile, archetype | `projects` | `_aos/projects.yaml` (deployed snapshot) |

### R2 — API-Only Mutation Path

All agents and teams MUST use the FastAPI endpoints to mutate structured data. The following direct file mutations are FORBIDDEN:

- Editing `roadmap.yaml` WP canonical fields (status, lod_status, current_lean_gate, track, profile, spec_ref, priority) outside of `deploy_cascade()`
- Editing `definition.yaml` team fields (engine, environment) outside of `deploy_cascade()`
- Editing `_aos/projects.yaml` project fields (profile, lifecycle_archetype, active_milestone) outside of `deploy_cascade()`

Exception: `gate_history[]` and prose `notes` fields remain file-authored (humans write history; `deploy_cascade` does NOT overwrite them).

### R3 — Deploy Cascade is the Write Path to Files

`deploy_cascade()` is the ONLY authorized function for writing the above structured fields to filesystem YAML. It is called automatically after every API mutation and produces idempotent, deterministic snapshots.

### R4 — L0 Profile is No Longer File-Centric

The `L0` profile no longer means "file is SSoT." L0 projects that have their WPs registered in the DB (via `seed.py` V320 extension) follow the same DB-as-SSoT model as L2. The profile designation (`L0`, `L2`, `L2.5`, `L3`) governs operational capability (automation level), NOT data authority.

### R5 — Offline Exception (Isolated Branch Only)

Offline file edits are permitted ONLY on a feature/bundle branch where the developer explicitly cannot reach the DB. On merge-back to main, the data MUST be reconciled via API or a `seed.py` re-run that writes to DB first, followed by `deploy_cascade()`.

### R6 — Enforcement

`validate_aos.sh` Check 19 verifies that all team contracts include the API-only mutations clause. Future `merge_validator.sh` extension (V320-WP5) will detect structured field changes in YAML committed without a corresponding `deploy_log` entry.

---

**Living methodology alignment:** `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` (Data Authority Model, Iron Rule #7) — keep in sync with this ADR.

## Rationale

1. **Drift elimination:** Manual file updates create drift within minutes of agent activity. DB-as-SSoT + structured API calls eliminate this entirely.
2. **Deterministic governance:** Agents in all environments (Cursor, Claude Code, Claude Desktop, Codex) interact with the same API. No environment-specific file-path knowledge required.
3. **Sandbox agent UX:** Sandbox agents can call `POST /api/l0/{project_id}/roadmap/advance` and get structured feedback instead of writing YAML and hoping.
4. **Cross-project consistency:** `deploy_cascade()` now pushes WP state to ALL registered projects simultaneously. One deploy propagates everywhere.
5. **Audit trail:** `deploy_log` table records every deploy with actor, trigger, timestamp, and file hashes.

---

## Implementation (V320 Work Packages)

| WP | Deliverable | Status |
|----|-------------|--------|
| WP-6 | `core/governance/team_200.md`, environment deploy trigger fix, cowork procedures restored | DONE 2026-04-16 |
| WP-1 | Migration 007 (projects table + lifecycle_archetype), seed.py extension, ProjectUpdateBody | DONE 2026-04-16 |
| WP-2 | L0 advance via DB, PUT /l0/{project_id}/work-packages/{wp_id}, environment cascade | DONE 2026-04-16 |
| WP-3 | deploy_cascade multi-project push, _write_projects_yaml helper | DONE 2026-04-16 |
| WP-4 | Iron Rule #7 extended text, all team contracts updated, Check 19 in validate_aos.sh | DONE 2026-04-16 |
| WP-5 | L0 DB route integration tests, deploy cascade multi-project test, sandbox exercise | DONE 2026-04-16 |

---

**log_entry | ADR034 | LOCKED | 2026-04-16 | Data Authority DB-as-SSoT for All Profiles — V320 DB Full Migration**
