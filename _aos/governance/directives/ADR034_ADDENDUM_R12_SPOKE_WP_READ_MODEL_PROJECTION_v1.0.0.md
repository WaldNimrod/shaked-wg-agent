# ADR034 Addendum R12 — Spoke / Hub-Native WP: Read-Model Projection

**Type:** Addendum (extends; does not replace)
**Parent:** [`ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md`](ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md) (LOCKED)
**Status:** LOCKED
**Date:** 2026-06-20
**Authority:** Team 00 (Principal) + Team 100 (Chief Architect)
**Trigger:** `_COMMUNICATION/team_100/CAMPAIGN_AGROS_V5_VALIDATION_CANON_v1.0.0.md` §7.2 — "cockpit ≠ domain reality" (the hub DB/cockpit is blind to spoke-native file-SSoT WPs)

---

## Problem Statement

ADR034 R9 (L2 spoke WPs) and R10 (hub-native `AOS-V*-WP-*` WPs) both establish that
certain WP classes are **file-SSoT** — authoritative state lives in `_aos/roadmap.yaml`
and `metadata.yaml`, with git commits as the audit record, and **no DB row exists**. That
ruling is correct and is preserved verbatim below.

The unintended consequence, surfaced during the v5 agros validation campaign (2026-06-20),
is that the hub cockpit (`:8092`) is a **DB reader**: it shows only WPs that have a row in
`work_packages`. Spoke-native (R9) and hub-native (R10) file-SSoT WPs therefore do **not
appear** in any unified cockpit view. The agros campaign's MESSAGES reached the DB inbox
(visible), but its six S002 WPs — being spoke-native file-SSoT with no DB row — were
invisible. The hub was not a unified WP view; the cockpit monitoring channel was crippled
for spoke domains.

This is the gap R12 closes: **observability without compromising write-authority.** The
file remains the write-SSoT; the DB gains a read-only mirror for monitoring.

---

## R12 — Spoke / Hub-Native WP: Read-Model Projection

### Ruling

1. **Write-SSoT is unchanged.** Spoke `_aos/roadmap.yaml` REMAINS the write-SSoT for L2
   spoke WPs (ADR034 R9, preserved verbatim — see "R9 Preserved" below). Hub-native
   `AOS-V*-WP-*` WPs REMAIN file-canonical (ADR034 R10, preserved). R12 creates **no new
   write path** and grants **no new mutation authority**.

2. **The hub MAY maintain a one-directional, READ-ONLY DB projection** of file-SSoT WPs
   into the `work_packages` table, for **OBSERVABILITY ONLY**. Projected rows are:
   - tagged `wp_source` ∈ {`spoke_file`, `file`} (vs `db` for authoritative API-created rows);
   - flagged `read_only = true`;
   - **never authoritative** for WP state — the file remains the source of truth;
   - **never a mutation target.** `POST` / `PATCH` against a projected row returns
     **HTTP 409** with code `READ_ONLY_WP` (alias `SPOKE_WP_FILE_SSOT`).

3. **Authoritative rows are never overwritten.** The projection MUST NOT touch or downgrade
   a row whose `wp_source = 'db'`. Where a file-SSoT WP and an authoritative DB WP could
   collide on `id`, the authoritative `db` row wins and the projection is a no-op for that id.

4. **Projected rows are excluded from all mutation endpoints** and from any logic that treats
   the DB as the write-SSoT. They participate in read/list/coverage endpoints only.

4a. **`l0_roadmap_source` — the provenance contract.** *(REGISTERED 2026-07-17, M12 W7 ·
   `AOS-V5-M12-WP-L0-CANON-RECONCILIATION`. Dual-authority — ✅ team_00 co-signed 2026-07-17 (Nimrod, in session — second key on the M12 W7 canon batch). **REGISTERED and
   BINDING.**)*

   `GET /api/l0/{project_id}/roadmap` stamps every payload with `l0_roadmap_source`, describing **the
   provenance of the WP list it just returned**. It has been emitted since R12 shipped and was
   **registered nowhere** — which is how it acquired a third value with nobody noticing.

   | Value | Means | Emitted when |
   |---|---|---|
   | **`file`** | Every returned WP came from the spoke roadmap file. The normal case, and the R12-correct one for a pure file-SSoT project. | no authoritative (`wp_source='db'`) row exists for the project (`l0_project_io.py:131`) |
   | **`mixed`** | Per-ID merge: most entries are the file's; ≥1 authoritative `db` row overrode its same-id file entry (R12 §3). **The tiktrack shape** — it carries both classes. | ≥1 authoritative row overrode **and** ≥1 file entry survived (`:201`) |
   | **`database`** | **Every** file entry was overridden by an authoritative same-id row (or the file was empty). | ≥1 override and **no** file entry survived (`:201`) |

   **Binding reading — this field is a DIAGNOSTIC, never an authority claim.** `database` does **not**
   mean "the DB is the SSoT for this project"; it means "every id in the file happened to have an
   authoritative counterpart." R12 §1-§4 are unchanged by any value of it. **Serving a projected row
   and stamping `database` is precisely the defect W3 repaired** — the pre-fix code set `database`
   unconditionally with no `wp_source` filter, making a read-only mirror look like authority. A
   consumer that branches on `database` to decide **where to write** has misread this contract: the
   write path is fixed by R9/R10 and the T-1 ruling, never by this field.

   **`mixed` is the third value**, added by W3 (2026-07-16) as part of the R12 §3 per-ID merge. Before
   it, a single `db` row collapsed the entire list to `database` and silently dropped every file-SSoT
   WP — on tiktrack, **176 of them**. Verified 2026-07-17: `l0_roadmap_source` has **zero executable
   consumers** (the route is a bare pass-through with no `response_model`; the cockpit never calls the
   endpoint), **so adding `mixed` broke nothing** — this closes team_120's C2, whose blast-radius
   concern is empty in code. That is luck, not design: an unregistered enum with no schema is one
   consumer away from a real break. Hence this registration.

   **Enforcement:** the route SHOULD declare a `response_model` pinning this enum → **W4** (fail-loud
   lane). Until then the enum is documentary and `l0_project_io.py:131,201` are its only sanctioned
   producers. ⚠ **A second, STALE producer exists:** the `agents-os-automation` worktree runs pre-W3
   `l0_project_io.py`, which sets `database` **unconditionally** with a bare `except: pass` — a live
   second emitter of the exact defect W3 fixed. Disposition → **W6**.

5. **Vocabulary remap at the projection boundary.** Spoke files frequently carry non-canon
   field values (e.g. status `COMPLETE`, `PLANNED`; non-canon `track`). The projection remaps
   these to canon at the **projection boundary only**, per
   `lean-kit/modules/validation-quality/docs/WP_FIELD_SCHEMA_v1.0.0.yaml`
   (`COMPLETE`/`COMPLETED`/`DONE`→`CLOSED`; `PLANNED`/`TODO`/`NEW`/`BACKLOG`→`DRAFT`;
   `IN_PROGRESS`/`WIP`→`ACTIVE`; `REVIEW`/`VALIDATING`→`IN_VALIDATION`; non-canon `track`→
   `UNCLASSIFIED`; non-canon `lod`→`null`). **Spoke files are left untouched — R9 is
   preserved.** The remap exists so projected rows satisfy the DB CHECK constraints
   (`chk_wp_status`, track canon, `description` NOT NULL) without editing the spoke source.

### Scope — What This Ruling Covers

| WP ID format | Write-SSoT (unchanged) | `wp_source` on projection | Authoritative? |
|---|---|---|---|
| `SNNN-PNNN-WPNNN` (L2 spoke) | Spoke `_aos/roadmap.yaml` (R9) | `spoke_file` | **No** — read-only mirror |
| `AOS-V*-WP-*` (hub-native) | Hub `_aos/work_packages/` + `_aos/roadmap.yaml` (R10) | `file` | **No** — read-only mirror |
| `M{n}-P{n}-WP{n}-slug` (v5 file-SSoT, no DB row) | `metadata.yaml` + git (R9/R10) | `file` | **No** — read-only mirror |
| API-created WPs (DB row exists) | `work_packages` via API (R2 / IR#7) | `db` | **Yes** — authoritative; projection never overwrites |

R12 applies ONLY to the **projection mechanism**. It does not alter which WPs are file-SSoT
(R9/R10 decide that) and does not alter the authoritative status of `db` rows.

---

## Relationship to AOS-V325-WP-ROADMAP-API (complementary, NOT superseding)

R12 is **COMPLEMENTARY** to **AOS-V325-WP-ROADMAP-API** (the file+DB atomic-create **WRITE**
path, COMPLETE 2026-05-25). It does **NOT** supersede V325.

- **V325** governs the **write** path: when a spoke session registers a *new* WP via the hub
  API, both the DB row and the `roadmap.yaml` entry are created **atomically**. Those WPs
  have authoritative `db` rows and fall under ADR034 R2 / Iron Rule #7.
- **R12** governs the **residual class V325 does not cover:** **pre-V325 / file-only WPs that
  have no DB row** — exactly the class that caused the agros cockpit blindness. V325 creates
  rows going forward; it does not retroactively give the existing pre-V325 / file-SSoT WPs a
  DB presence. R12 projects those into a read-only mirror so they become visible without ever
  being given an authoritative DB row or a write path.

The two are layered: **V325 = forward write path (authoritative rows); R12 = read-only
observability mirror for the file-SSoT residual.** Neither weakens the other.

---

## R9 Preserved — No Hub Session Required to Write

ADR034 R9's no-hub-session-required write path is preserved **verbatim**: a spoke team_100
(or team_00) MAY directly edit the spoke `_aos/roadmap.yaml` for L2 WP operational state
(`status`, `lod_status`, `current_lean_gate`, `gate_history[]`), with the spoke git commit as
the audit record. **No hub session is required for spoke roadmap state mutations.** R12's
projection is a downstream, read-only consequence of those file edits — it observes them; it
never gates, blocks, or requires them.

---

## Mechanism

Implementation note (for traceability — does not alter the ruling):

- **Projection function:** `l0_project_io.project_file_wps_to_read_model` — reads file-SSoT
  WP entries (spoke `_aos/roadmap.yaml` + hub-native `metadata.yaml`/`roadmap.yaml`), remaps
  vocabularies per `WP_FIELD_SCHEMA_v1.0.0.yaml`, and upserts read-only rows with an
  **`ON CONFLICT … WHERE wp_source <> 'db'`** guard so authoritative `db` rows are never
  overwritten.
- **Trigger paths:**
  - scheduled — a scheduler interval (WPDM-07) re-runs the projection so the mirror stays fresh;
  - manual — `POST /api/admin/project-wp-sync` forces an immediate projection pass.
- **Read paths:**
  - `GET /api/work-packages` (unified list — returns `db` + `spoke_file` + `file` rows, each
    carrying `wp_source` / `read_only`);
  - `GET /api/system/coverage-audit` (reports projection coverage vs. file-SSoT WP inventory).
- **Mutation guard:** `POST` / `PATCH` on any row with `read_only = true` → HTTP 409
  `READ_ONLY_WP` / `SPOKE_WP_FILE_SSOT`.

---

## Why Not Just Make Spoke WPs DB-Authoritative

Making file-SSoT WPs authoritative DB rows would re-open every problem R9 and R10 were
authored to close: it would require a hub session and an API round-trip for every spoke state
change (>24h drift latency, the original R9 trigger), and it would break R10's file-canonical
closure for `AOS-V*-WP-*` WPs that the DB schema rejects by design. R12 keeps the cheap,
correct file-SSoT write path intact and adds a **read-only** mirror purely for visibility.
The mirror can be stale or rebuilt at will without any risk to authoritative state.

---

## Traceability

| Artifact | Role |
|---|---|
| Triggering finding | `_COMMUNICATION/team_100/CAMPAIGN_AGROS_V5_VALIDATION_CANON_v1.0.0.md` §7.2 (cockpit ≠ domain reality) |
| Field schema (canon + remap) | `lean-kit/modules/validation-quality/docs/WP_FIELD_SCHEMA_v1.0.0.yaml` |
| Field schema (prose companion) | `lean-kit/modules/validation-quality/docs/WP_DB_CANONICAL_TRACK_LOD_v1.0.0.md` |
| Write-path precedent (R9) | `governance/directives/ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md` |
| Write-path precedent (R10) | `governance/directives/ADR034_ADDENDUM_R10_HUB_NATIVE_WP_FILE_SSOT_v1.0.0.md` |
| Complementary write path | `_aos/work_packages/AOS-V325-WP-ROADMAP-API/` (file+DB atomic-create, COMPLETE 2026-05-25) |
| Track canon | `governance/directives/ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` |
| Parent ADR | `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` |

---

**log_entry | ADR034 R12 Addendum | LOCKED | 2026-06-20 | Hub MAY maintain a one-directional READ-ONLY DB projection of file-SSoT WPs (wp_source spoke_file|file, read_only=true) for observability only; never authoritative, never a mutation target (409 READ_ONLY_WP); R9 write-SSoT + R10 file-canonical preserved verbatim; complementary to V325 (covers the pre-V325 file-only residual)**
