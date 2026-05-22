# ADR034 Addendum R10 — Hub-Native WP: File-Based SSoT

**Type:** Addendum (extends; does not replace)
**Parent:** [`ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`](ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md) (LOCKED)
**Status:** LOCKED
**Date:** 2026-05-23
**Authority:** Team 00 (principal) + Team 100 (chief architect)
**Trigger:** `_COMMUNICATION/team_100/FINDING_HUB_NATIVE_WP_DB_SYNC_NOT_APPLICABLE_2026-05-22_v1.0.0.md`

---

## Problem Statement

ADR034 R2 forbids direct mutations to canonical fields in structured WP data for all profiles,
requiring API-only updates when the database is online. However, for **hub-native WPs**
(`AOS-V*-WP-*` ID format, stored in hub `_aos/roadmap.yaml` and `_aos/work_packages/*/`),
the DB schema makes R2 mechanically inapplicable:

1. **No DB row exists** for hub-native WPs — the hub PostgreSQL `work_packages` table schema
   (`WP_ID_STANDARD §10`) accepts ONLY `SNNN-PNNN-WPNNN` and `NB-Vn-WP-*` formats.
   `POST /api/work-packages` with an `AOS-V*-WP-*` ID returns:
   ```
   HTTP 400
   {"code": "INVALID_WP_ID_FORMAT",
    "message": "WP ID must match SNNN-PNNN-WPNNN or NB-Vn-WP-* (CONTENT_SUBSTRATE, WP_ID_STANDARD §10)"}
   ```
2. **No hub API endpoint exists** for hub-native WP mutations — the schema constraint is at the
   database validation layer, not an API routing gap.

This gap was discovered empirically during AOS-V4.2 program closure (2026-05-22) when
team_100 attempted to sync three closed hub-native WPs to the DB after waldhomeserver restart.
All three POST calls returned HTTP 400. The finding was classified MEDIUM severity and triggered
this addendum (parallel to ADR034 R9 for L2 spoke WPs).

---

## R10 — Hub-Native WP: File-Based SSoT

### Ruling

For **hub-native WPs** (`AOS-V*-WP-*` ID format):

1. **File artifacts are the SSoT.** No DB row exists and no API endpoint accepts these IDs.
   The authoritative record for a hub-native WP is the union of:
   - `_aos/work_packages/AOS-V*-WP-*/metadata.yaml` (canonical metadata + state)
   - `_aos/roadmap.yaml` (registry + status snapshot)
   - `_archive/AOS-V*-WP-*/ARCHIVE_MANIFEST.md` (closure record)
   - `_COMMUNICATION/team_190/VERDICT_*_L-GATE_*.md` (gate verdicts)
   - Git commit history (audit trail)

2. **File-canonical closure is constitutionally valid** and completes Iron Rule #7 for this WP
   class. The git commit record is the audit trail equivalent of a DB transaction log.

3. **`PENDING_DB_SYNC.yaml` entries referencing `AOS-V*-WP-*` IDs are NOT APPLICABLE and MUST
   NOT be created.** The DB schema will always reject them. `sync_offline_to_db.sh` skips
   hub-native WP mutations with a logged `[SKIP]` message (ADR034 R10 guard).

4. **ADR034 R2 / Iron Rule #7 is not violated** for this WP class — the original ruling was
   authored with the assumption that all tracked WPs have corresponding DB rows. Hub-native WPs
   were not considered. This addendum closes that gap, consistent with the same reasoning used
   in ADR034 R9 for L2 spoke WPs.

### Scope — What This Ruling Covers

| WP ID format | Location | Ruling |
|---|---|---|
| `AOS-V*-WP-*` (e.g., `AOS-V4.3-WP-ADR034-R10-HUB-NATIVE-SSOT`) | Hub `_aos/work_packages/` + `_aos/roadmap.yaml` | **R10 — file-based SSoT; git commit = audit record** |
| `SNNN-PNNN-WPNNN` (e.g., `S005-P003-WP002`) | L2 spoke `_aos/roadmap.yaml` | ADR034 R9 — file-based SSoT; spoke team_100 direct edit |
| `NB-Vn-WP-*` (CONTENT_SUBSTRATE, e.g., `NB-V3-WP-A`) | Hub DB + `_aos/roadmap.yaml` | ADR034 R2 / Iron Rule #7 — DB via API (schema accepts this format) |

**R10 applies ONLY to hub-native WPs (`AOS-V*-WP-*` format).** L2 spoke WPs remain under R9;
`NB-Vn-WP-*` WPs remain under ADR034 R2 / Iron Rule #7. This addendum creates no exception
for those categories.

### Writer authority (R10)

Hub `_aos/roadmap.yaml` and `_aos/work_packages/*/metadata.yaml` for hub-native WPs follow the
existing single-writer rule (Iron Rule #4):

- **team_100 (hub repo):** primary writer for operational state transitions (WP lifecycle)
- **team_200 (Cowork):** may write for cowork-bundle WPs under active mandate
- **team_00 (Principal):** may write from any session
- All other teams: NO direct write authority — route via team_100 or team_200 in the hub

### Audit trail

Each hub-native WP state transition MUST be captured in a git commit with a message that
identifies the WP ID and the state change (e.g., `roadmap(AOS-V4.3-WP-ADR034-R10-HUB-NATIVE-SSOT): advance to LOD500_LOCKED`). This satisfies the audit requirement in lieu of a DB transaction log.

---

## Why Not ADR034 R2

ADR034 R2 was authored with the assumption that all WPs tracked in structured files have
corresponding DB rows. This is true for spoke-native L2 WPs registered via the API (post
AOS-V325-WP-ROADMAP-API) and for `NB-Vn-WP-*` CONTENT_SUBSTRATE WPs. Hub-native
`AOS-V*-WP-*` WPs were not considered — the WP_ID_STANDARD §10 schema constraint implicitly
excludes them from the DB entirely.

This addendum does not weaken ADR034 R2 for the cases it was designed to govern. It closes
a gap where the rule was written with an unexamined assumption about DB row existence, parallel
to the same reasoning in ADR034 R9.

---

## Future State

If a future WP (e.g., AOS-V325-WP-ROADMAP-API follow-on) extends `WP_ID_STANDARD §10` to
accept `AOS-V*-WP-*` IDs and creates DB rows for hub governance WPs, R10 would be superseded
for newly-created hub WPs. Existing pre-R10 hub WPs would require an explicit migration procedure.
Until that WP exists and is LOD500_LOCKED, R10 governs all hub-native WPs.

---

## Traceability

| Artifact | Role |
|---|---|
| Triggering finding | `_COMMUNICATION/team_100/FINDING_HUB_NATIVE_WP_DB_SYNC_NOT_APPLICABLE_2026-05-22_v1.0.0.md` |
| team_190 verdict reference | `_COMMUNICATION/team_190/VERDICT_AOS-V4.2-CLOSURE-SWEEP_v1.0.0.md` — F-CS-001 (MEDIUM) |
| DB schema constraint | `WP_ID_STANDARD §10` (hub PostgreSQL schema) |
| Parallel precedent | `governance/directives/ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md` |
| Parent ADR | `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` |
| sync_offline_to_db.sh guard | `scripts/sync_offline_to_db.sh` (R10 guard pattern: `^AOS-V.*-WP-`) |

---

**log_entry | ADR034 R10 Addendum | LOCKED | 2026-05-23 | Hub-native AOS-V*-WP-* WPs are file-canonical SSoT; no DB row; git commit = audit record; PENDING_DB_SYNC.yaml entries for these IDs are NOT APPLICABLE**
