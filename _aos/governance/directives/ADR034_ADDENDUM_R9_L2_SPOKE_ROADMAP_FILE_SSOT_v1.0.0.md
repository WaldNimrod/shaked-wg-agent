# ADR034 Addendum R9 — L2 Spoke Roadmap: File-Based SSoT

**Type:** Addendum (extends; does not replace)
**Parent:** [`ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`](ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md) (LOCKED)
**Status:** LOCKED
**Date:** 2026-04-25
**Authority:** Team 00 (principal) + Team 100 (chief architect)
**Trigger:** `HUB_UPDATE_L2_ROADMAP_SSOT_DRIFT_v1.0.0.md` (TikTrack spoke team_100, commit df7bdc6)

---

## Problem Statement

ADR034 R2 forbids direct mutations to canonical fields in `roadmap.yaml` for all profiles,
requiring API-only updates when the database is online. However, for **L2 spoke WPs**
(SNNN-PNNN-WPNNN ID format, stored in a spoke `_aos/roadmap.yaml`), two facts make R2
mechanically inapplicable:

1. **No hub DB row exists** for L2 spoke WPs — the hub database only tracks hub-native WPs
   (`AOS-V*` format, L0 profile). Querying `/api/work-packages/{SNNN-PNNN-WPNNN}` returns
   `{"code": "NOT_FOUND"}`.
2. **No hub API endpoint exists** for L2 spoke roadmap mutations — `/api/l0/{project}/roadmap/advance`
   rejects L2 projects with `{"code": "INVALID_STATE", "details": {"profile": "L2"}}`.

The "hub only — SSOT edits" convention therefore has zero enforcement mechanism for L2 spoke WPs.
Requiring a hub session to mutate L2 spoke state adds >24h latency (recurring drift pattern,
documented in triggering report) without providing any governance value.

---

## R9 — L2 Spoke Roadmap: File-Based SSoT

### Ruling

For **L2 spoke WPs** (SNNN-PNNN-WPNNN ID format, stored in a spoke `_aos/roadmap.yaml`):

1. The spoke `_aos/roadmap.yaml` is the **file-based SSoT** for those WPs. No hub DB row
   exists and no API endpoint exists to enforce R2's API-only constraint.

2. **Spoke team_100 MAY directly edit** the spoke `_aos/roadmap.yaml` for L2 WP operational
   state fields (`status`, `lod_status`, `current_lean_gate`, and `gate_history[]`). A **git
   commit in the spoke repo is the audit record** — equivalent to what a DB transaction would
   provide in an L0 context.

3. A hub session is **NOT required** for L2 spoke roadmap state mutations. MSG-HUB artifacts
   for this purpose are deprecated once this addendum is propagated to all spokes.

4. **`gate_history[]` and `notes` fields** remain file-authored in all cases (unchanged from
   ADR034 R2 original exception).

### Scope — What This Ruling Covers

| WP ID format | Profile | Roadmap location | Ruling |
|---|---|---|---|
| `AOS-V*` (e.g., AOS-V320-WP-...) | L0 | Hub `_aos/roadmap.yaml` | ADR034 R2 / Iron Rule #7 applies — API only |
| `SNNN-PNNN-WPNNN` (e.g., S005-P003-WP002) | L2 spoke | Spoke `_aos/roadmap.yaml` | **R9 — file-based SSoT; spoke team_100 direct edit** |

**R9 applies ONLY to L2 spoke WPs.** Hub-native WPs (AOS-V* format, L0) remain fully
subject to ADR034 R2 and Iron Rule #7. This addendum creates no exception for those.

### Writer authority (R9)

Spoke `_aos/roadmap.yaml` for L2 WPs follows the existing single-writer rule (Iron Rule #4):

- **team_100 (spoke repo):** primary writer for operational state transitions
- **team_00 (Principal):** may write from any session
- All other teams: NO direct write authority — route via team_100 in the spoke

### Audit trail

Each L2 roadmap mutation MUST be captured in a git commit with a message that identifies
the WP ID and the state change (e.g., `roadmap(S005-P003-WP002): advance to L-GATE_COMPLETE_QA`).
This satisfies the audit requirement in lieu of a DB transaction log.

---

## Why Not ADR034 R2

ADR034 R2 was authored with the assumption that all WPs tracked in `roadmap.yaml` files have
corresponding DB rows. This is true for hub-native L0 WPs. L2 spoke WPs were not considered
in the original ruling — the "all profiles" language in ADR034 R2 refers to L0/L2/L2.5/L3
operational modes (automation level), not to the question of whether a DB row exists for the
WP being mutated.

This addendum does not weaken ADR034 R2 for the cases it was designed to govern. It closes
a gap where the rule was written with an unexamined assumption.

---

## Future State (AOS-V325-WP-ROADMAP-API)

Once AOS-V325-WP-ROADMAP-API lands, the `/AOS_roadmap-add` command will allow spoke sessions
to register WPs via hub API, creating both DB rows and `roadmap.yaml` entries atomically.
At that point, newly-created spoke WPs will have hub DB rows and will fall back under
ADR034 R2 / Iron Rule #7. Existing pre-V325 spoke WPs (no DB row) remain under R9 unless
explicitly migrated via the reconciliation tooling from AOS-V325.

---

## Traceability

| Artifact | Role |
|---|---|
| Triggering report | `TikTrack-Phoenix_AOSProject/_COMMUNICATION/team_100/HUB_UPDATE_L2_ROADMAP_SSOT_DRIFT_v1.0.0.md` |
| Authority matrix | `lean-kit/modules/project-governance/docs/ROADMAP_AUTHORITY_MATRIX_v1.1.0.md` |
| Parent ADR | `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` |
| ADR034 R2 | `governance/directives/ADR034_ADDENDUM_R2_ROADMAP_SSOT_CLARIFICATION_v1.0.0.md` |
| Future resolution | `_aos/work_packages/AOS-V325-WP-ROADMAP-API/LOD200_AOS-V325-WP-ROADMAP-API.md` |

---

**log_entry | ADR034 R9 Addendum | LOCKED | 2026-04-25 | L2 spoke roadmap.yaml = file-based SSoT; spoke team_100 direct edit; git commit = audit record**
