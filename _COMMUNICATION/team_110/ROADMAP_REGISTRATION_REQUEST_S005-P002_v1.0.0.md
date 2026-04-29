---
id: ROADMAP_REGISTRATION_REQUEST_S005-P002_v1.0.0
type: ROADMAP_REGISTRATION_REQUEST
from: team_110 (Domain Architect — orchestrator)
to: team_100 (this spoke — roadmap custodian)
date: 2026-04-30
status: OPEN — awaiting team_100 action
priority: P1_URGENT
mandate_ref: MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0
pre_flight_gate: true
dispatch_blocked_until: confirmed
---

# ROADMAP REGISTRATION REQUEST — S005-P002 + SWG-PLAT-M1..M5

## §1 — Request

team_110 requests that **team_100** register the following in `_aos/roadmap.yaml` via the API (Iron Rule #7 — DB online):

1. **New program** `S005-P002` under milestone `S005`
2. **Five work packages** `SWG-PLAT-M1` through `SWG-PLAT-M5` under `S005-P002`

**Authority basis:** team_110 may not edit `_aos/roadmap.yaml` directly (Iron Rule #7 — DB online; and roadmap.yaml write authority belongs to team_100 + team_00 per AOS_DIRECTORY_CANON Part 5). This request is the canonical pre-flight gate per mandate §6 check #1.

**Dispatch dependency:** team_110 will NOT dispatch any sub-agent until team_100 confirms registration is complete and responds to this request. This is a hard pre-flight gate.

---

## §2 — Program definition

```yaml
# Under milestone S005, add new program S005-P002:
programs:
  - id: S005-P002
    label: "Cross-profile platform hardening — Shaked field-evidence driven"
    milestone_ref: S005
    status: ACTIVE
    created_at: '2026-04-30'
    owner: team_110
    mandate_ref: MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0
    notes: >
      5 field-evidence gaps surfaced during live search session run-20260429-213722-f1bd.
      Orchestrated by team_110 (sub-agent pipeline pattern, TikTrack canonical).
      Project window: 2026-06-08.
```

---

## §3 — Work package stubs (proposed)

All 5 WPs follow the same structure. team_100 should adapt as needed for roadmap schema compliance.

### SWG-PLAT-M1 — Profile schema: age + studies + move_in_optimal

```yaml
- id: SWG-PLAT-M1
  label: "Profile schema — age, occupation_status, studies_*, move_in_optimal"
  milestone_ref: S005
  program_ref: S005-P002
  status: PLANNED
  track: A
  profile: L0
  current_lean_gate: L-GATE_S
  lod_status: LOD200
  assigned_builder: sonnet_sub_agent
  assigned_validator: haiku_sub_agent
  created_at: '2026-04-30'
  spec_ref: _aos/work_packages/SWG-PLAT-M1/LOD200_spec.md
  depends_on:
    - SWG-PLAT-M2
  notes: >
    Add age, occupation_status, studies_field, studies_institution, studies_start,
    move_in_optimal to profile schema. Scorer bonuses for age match, student status,
    move_in_optimal exact match. Hard excludes for age range / gender violations.
    Blocked by M2 (needs full_description field for accurate signals).
```

### SWG-PLAT-M2 — Full-description extraction (UNBLOCKER)

```yaml
- id: SWG-PLAT-M2
  label: "Full-description extraction — flatfox + wgzimmer scrapers"
  milestone_ref: S005
  program_ref: S005-P002
  status: PLANNED
  track: A
  profile: L0
  current_lean_gate: L-GATE_S
  lod_status: LOD200
  assigned_builder: sonnet_sub_agent
  assigned_validator: haiku_sub_agent
  created_at: '2026-04-30'
  spec_ref: _aos/work_packages/SWG-PLAT-M2/LOD200_spec.md
  notes: >
    Add full_description: str (≥500 chars) to ScrapedListing. Extend flatfox REST/HTML
    and wgzimmer Playwright extractors. Migrate legacy listings (full_description = summary).
    ≥10 fixture HTMLs in tests/fixtures/scrapers/. UNBLOCKER for M1 and M5.
```

### SWG-PLAT-M3 — wgzimmer scraper recovery

```yaml
- id: SWG-PLAT-M3
  label: "wgzimmer scraper recovery — returns 0 listings (Hauptquelle dead)"
  milestone_ref: S005
  program_ref: S005-P002
  status: PLANNED
  track: A
  profile: L0
  current_lean_gate: L-GATE_S
  lod_status: LOD200
  assigned_builder: sonnet_sub_agent
  assigned_validator: haiku_sub_agent
  created_at: '2026-04-30'
  spec_ref: _aos/work_packages/SWG-PLAT-M3/LOD200_spec.md
  notes: >
    wgzimmer_pw.py returned 0 listings on run-20260429-213722-f1bd and prior run.
    Diagnose selector drift vs anti-bot escalation. Restore ≥1 live listing or
    document source-side outage. Independent of M2 — Wave 1 parallel candidate.
```

### SWG-PLAT-M4 — Outreach lifecycle tracking

```yaml
- id: SWG-PLAT-M4
  label: "Outreach lifecycle tracking — contacted/replied/viewed/rejected"
  milestone_ref: S005
  program_ref: S005-P002
  status: PLANNED
  track: A
  profile: L0
  current_lean_gate: L-GATE_S
  lod_status: LOD200
  assigned_builder: sonnet_sub_agent
  assigned_validator: haiku_sub_agent
  created_at: '2026-04-30'
  spec_ref: _aos/work_packages/SWG-PLAT-M4/LOD200_spec.md
  depends_on:
    - SWG-PLAT-M1
  notes: >
    Extend status enum: contacted, replied, viewed, rejected, replied_negative.
    CLI subcommands: mark-contacted, mark-replied, mark-rejected, mark-viewed.
    Scan does not reset contacted listings to neu. HTML report visual treatment per status.
    Top-5 excludes rejected/replied_negative.
```

### SWG-PLAT-M5 — Negative-signal autofilter

```yaml
- id: SWG-PLAT-M5
  label: "Negative-signal autofilter — women_only, Wochenaufenthalter, Zwischenmiete"
  milestone_ref: S005
  program_ref: S005-P002
  status: PLANNED
  track: A
  profile: L0
  current_lean_gate: L-GATE_S
  lod_status: LOD200
  assigned_builder: sonnet_sub_agent
  assigned_validator: haiku_sub_agent
  created_at: '2026-04-30'
  spec_ref: _aos/work_packages/SWG-PLAT-M5/LOD200_spec.md
  depends_on:
    - SWG-PLAT-M2
    - SWG-PLAT-M1
  notes: >
    New extractor: shaked_wg_agent/extractors/negative_signals.py.
    Patterns: gender-only WG (DE/EN/IT/FR), Wochenaufenthalter, Zwischenmiete <6mo.
    Recall ≥90%, precision ≥95% on 20 hand-labeled listings.
    Hard-exclude when restriction conflicts with profile (uses M1 profile shape + M2 full_description).
```

---

## §4 — API mutation context (Iron Rule #7)

DB status at time of request: **ONLINE** (`checked_at: 2026-04-29T23:34:07`, `status: online`).

team_100 must execute the registration via the AOS v3 API (not direct YAML edit):

```
POST /api/programs/  → create S005-P002
POST /api/work_packages/  → create SWG-PLAT-M{1..5} (5 calls)
```

Or if the roadmap API supports bulk registration:
```
POST /api/programs/S005-P002/work_packages/bulk
```

After API registration, team_100 should verify `_aos/roadmap.yaml` reflects the new WPs (API auto-updates the file per ADR034).

---

## §5 — Expected confirmation response

team_100 responds with:
`_COMMUNICATION/team_100/RESPONSE_ROADMAP_REGISTRATION_S005-P002_v1.0.0.md`

Contents required:
- Confirmation of S005-P002 program creation (with assigned ID)
- Confirmation of all 5 WP IDs registered
- Any ID changes from proposed stubs (team_100 may adjust IDs for schema compliance)
- `validate_aos.sh` result post-registration (expect 0 FAIL)

**team_110 will begin Wave-1 dispatch within 15 minutes of receiving this confirmation** (assuming git status concern is also resolved by then — see ACK §3).

---

## §6 — team_110 identity header

**team_110 (Domain Architect — orchestrator-mode)**
Spoke: shaked-wg-agent (L0)
Date: 2026-04-30
Mandate: MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0

---

*Pre-flight gate artifact. team_110 BLOCKED on dispatch until team_100 responds with confirmation.*
