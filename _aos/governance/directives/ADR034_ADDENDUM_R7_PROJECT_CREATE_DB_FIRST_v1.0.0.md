# ADR034 Addendum R7 — Project Create: DB-First + Deploy-Only Snapshots

**Type:** Addendum (extends; does not replace)
**Parent:** [`ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`](ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md) (LOCKED)
**Status:** LOCKED
**Date:** 2026-04-17
**Authority:** Team 00 (principal) + Team 100 (chief architect)
**Work Package:** AOS-V320-WP-MODULE-INTEGRITY (L-GATE_SPEC remediation — Team 190 VC-6)

---

## Purpose

Team 190 L-GATE_SPEC (`VERDICT_AOS-V320-WP-MODULE-INTEGRITY_L-GATE_SPEC_v1.0.0.md`) identified a **spec-level** conflict: a “YAML-first then seed DB” flow for `POST /api/projects` would cause **direct `_aos/projects.yaml` mutation outside `deploy_cascade()`** while the database is online, contradicting ADR034 **R2** and **R3**.

This addendum makes the ruling **enforcement-explicit** for the **project registration / provisioning** surface only.

---

## R7 — Project create when DB is online

When `AOS_V3_DATABASE_URL` is set and the database is reachable:

1. **Authoritative writes** for new project metadata (`projects` table and default `project_module_config` rows) occur **only** via the API implementation path (INSERT / upsert in PostgreSQL), in line with ADR034 **R1**–**R2**.

2. **`_aos/projects.yaml` is not edited by hand nor by `atomic_write_yaml()` for structured project fields** in that code path. The file is updated **only** as a **deployed snapshot** produced by **`deploy_cascade()`** (ADR034 **R3**), after the DB transaction that registers the project succeeds.

3. **Ordering (normative):** provision spoke on disk (existing behavior) → **commit project row + PMC defaults in DB** → **`deploy_cascade(conn, …)`** with `triggered_by` documenting `POST /api/projects` (or equivalent). The snapshot step must include the new row via `_write_projects_yaml` inside `deploy_cascade`, not a separate ad-hoc YAML writer.

4. **Failure:** If DB insert or `deploy_cascade` fails after disk provisioning, the API must **not** leave a hub-only YAML row without a matching DB row when DB was required; return **5xx** and document operator cleanup (rollback / manual reconcile) in the WP implementation.

---

## Offline / no DB (explicit exception)

When `AOS_V3_DATABASE_URL` is **not** set or the hub is in an **offline / isolated branch** context per ADR034 **R5**, file-centric registration may remain. That path does **not** invoke R7; it is outside DB-as-SSoT enforcement. On merge-back to a DB-backed mainline, reconciliation remains **R5** (DB first, then deploy).

> **Operator note:** The `db_conn is None` code branch in `create_project()` is an **internal / programmatic** fallback (e.g., direct SDK use with no DB connection passed). It is **not reachable via `POST /api/projects`** when the hub DB URL is set — that API endpoint requires the DB and returns **503** when it is unavailable. "Offline create via API" is therefore not a supported user-facing flow; offline registration is for bootstrap tooling only.

---

## Traceability

| Artifact | Role |
|----------|------|
| LOD400 | `_aos/work_packages/AOS-V320-WP-MODULE-INTEGRITY/LOD400_AOS-V320-WP-MODULE-INTEGRITY.md` (v1.0.1+) |
| Verdict | `_COMMUNICATION/team_190/VERDICT_AOS-V320-WP-MODULE-INTEGRITY_L-GATE_SPEC_v1.0.0.md` |

---

**log_entry | ADR034 R7 Addendum | LOCKED | 2026-04-17 | Project create DB-first; deploy-only projects.yaml when DB online**
