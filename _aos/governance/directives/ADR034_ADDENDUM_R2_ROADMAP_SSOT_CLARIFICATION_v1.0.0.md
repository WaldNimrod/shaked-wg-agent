---
directive_id: ADR034_ADDENDUM_R2
title: "ADR034 Addendum — WP Bootstrap Exception and API-Only Gap Documentation"
version: 1.1.0
parent_adr: ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md
status: LOCKED
authority: team_00 (approval) + team_100 (author)
date: 2026-04-20
trigger: HUB_UPDATE_AOS100_ROADMAP_API_GAP_2026-04-20_v1.md (TikTrack spoke team_100)
change_log:
  - v1.0.0: Initial draft — Plane A/B framing (FAILED Team 190 VC-7)
  - v1.1.0: Rewritten — removed Plane A/B framing; aligned with ADR034 R2; framed as approved interim exception
---

# ADR034 Addendum R2 — WP Bootstrap Exception and API-Only Gap

## 1. Problem Statement

ADR034 R2 states "API-only mutation path" and lists direct `roadmap.yaml` edits of
canonical fields (`status, lod_status, current_lean_gate, track, profile, spec_ref,
priority`) as FORBIDDEN outside of `deploy_cascade()`.

In practice, creating a new WP entry in `_aos/roadmap.yaml` is necessary before any
API endpoint exists to do it. The current `POST /api/work-packages` (`dashboard_routes.py:876`)
has three gaps preventing its use for AOS-canonical WPs:

1. It rejects `AOS-V*` style IDs (portfolio.py:892 — only accepts `SNNN-PNNN-WPNNN`)
2. It writes DB only — not `_aos/roadmap.yaml`
3. Server requires `AOS_V3_TRUST_CLIENT_ACTOR=1` not set in default start script

WP **AOS-V325-WP-ROADMAP-API** is registered to close all three gaps.

---

## 2. ADR034 R2 — What It Covers (Unchanged)

ADR034 R2 remains fully in force. The following roadmap.yaml edits are **FORBIDDEN**:

- Changing `status`, `lod_status`, `current_lean_gate` of an existing WP directly in file
- Changing `track`, `profile`, `spec_ref`, `priority` of an existing WP directly in file
- Any change that bypasses `deploy_cascade()` for an existing, DB-registered WP record

**Exception (from ADR034 R2 itself):** `gate_history[]` and prose `notes` fields remain
file-authored — `deploy_cascade()` does not overwrite them.

**Offline exception (ADR034 R5):** Direct file edits permitted only on a feature branch
when DB is unreachable. See `governance/directives/ADR034_ADDENDUM_R8_OFFLINE_CHANGELOG_PROTOCOL_v1.0.0.md`
for the offline protocol (PENDING_DB_SYNC.yaml workflow). Note: "R8" refers to the
addendum designator in that file, not a clause in the parent ADR034.

---

## 3. Approved Interim Exception — New WP Bootstrap

**Scope:** This exception applies ONLY to **creating a new WP entry** (bootstrapping a
record that does not yet exist in the DB). It does NOT apply to mutating an existing WP's
canonical fields — ADR034 R2 applies fully to those.

**Authorization:** team_00 approves this as a controlled exception pending delivery
of AOS-V325-WP-ROADMAP-API.

**Permitted bootstrap procedure (hub session only, team_100 or team_00):**

```
1. Append new entry to _aos/roadmap.yaml with initial fields:
   id, label, status: PLANNED, track, profile, risk, lod_status, current_lean_gate,
   assigned_builder, assigned_validator, spec_ref, notes, gate_history: []
2. Call portfolio.create_work_package() directly with a DB-compatible ID (SNNN-PNNN-WPNNN)
   to register a stub in the DB. Record this as db_wp_id in roadmap.yaml.
3. Note: sync_l0_roadmap_to_db matches by roadmap.yaml `id:` value against DB `id` column.
   Since db_wp_id ≠ id (SNNN format ≠ AOS-V* format), the stub DB row is NOT reconciled
   by the startup sync — it is a standalone stub only. This is an acknowledged limitation
   of the interim procedure; AOS-V325 will resolve it (see §5).
4. Run validate_aos.sh → 0 FAIL before committing.
```

**Spoke team_100:** May NOT perform steps 1–3 directly (requires hub repo access).
Must file `ROADMAP_INSERTION_REQUEST` → routed to hub team_100.

---

## 4. sync_l0_roadmap_to_db — Accurate Behavior

`core/modules/management/l0_project_io.py:155–244` behavior:
- Reads `_aos/roadmap.yaml` entries
- For each entry, looks up a DB row where `work_packages.id = wp['id']` (the canonical `id:` field from roadmap.yaml)
- If found: updates `status`, `current_lean_gate`, `lod_status` in DB from file values
- If not found: **skips** (does NOT create new DB rows from file)
- `db_wp_id` is NOT consumed by the engine — it is metadata only in roadmap.yaml

**Implication for R1 WP design:** The new `POST /api/roadmap/wps` endpoint MUST store
the canonical AOS-V* ID (e.g., `AOS-V325-WP-ROADMAP-API`) as the DB `work_packages.id`.
This requires extending `portfolio._validate_work_package_id_format()` to accept the
`AOS-V[0-9]+-WP-[A-Z0-9-]+` pattern. See LOD200 spec critical notes for full builder guidance.

---

## 5. Post-R1 State (AOS-V325-WP-ROADMAP-API)

Once AOS-V325-WP-ROADMAP-API is complete:
- `POST /api/roadmap/wps` atomically appends to `_aos/roadmap.yaml` AND inserts to DB
  using the canonical AOS-V* ID as the `work_packages.id`
- `sync_l0_roadmap_to_db` will then reconcile operational fields correctly
- `/AOS_roadmap-add` enables spoke sessions to create WPs via hub API without direct
  file access — resolving the cross-repo boundary without violating hub file isolation
- This interim exception is retired; WP creation becomes fully ADR034 R2 compliant

---

## References

- `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` (parent)
- `governance/directives/ADR034_ADDENDUM_R8_OFFLINE_CHANGELOG_PROTOCOL_v1.0.0.md` (offline protocol)
- `governance/directives/ADR041_COMMAND_ARCHITECTURE_UNIFICATION_v1.0.0.md` (Iron Rule #13)
- `lean-kit/modules/project-governance/docs/ROADMAP_AUTHORITY_MATRIX_v1.0.0.md` (authority table — propagated to all spokes)
- `_aos/work_packages/AOS-V325-WP-ROADMAP-API/LOD200_AOS-V325-WP-ROADMAP-API.md` (R1 WP)
- `HUB_UPDATE_AOS100_ROADMAP_API_GAP_2026-04-20_v1.md` (TikTrack spoke — triggering report)
