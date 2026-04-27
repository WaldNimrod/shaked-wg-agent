---
doc_id: ROADMAP_AUTHORITY_MATRIX
version: 1.1.0
status: ACTIVE
supersedes: ROADMAP_AUTHORITY_MATRIX_v1.0.0.md
authority: team_00 (approval) + team_100 (author)
date: 2026-04-25
trigger: ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md
change_log:
  - v1.0.0: Initial matrix (2026-04-20) — L2 spoke team_100 required ROADMAP_INSERTION_REQUEST for all operational state changes
  - v1.1.0: L2 spoke WP exception per ADR034 R9 — spoke team_100 may directly edit spoke roadmap.yaml for SNNN-PNNN-WPNNN WPs; hub session no longer required
---

# Roadmap Authority Matrix v1.1.0

Canonical reference for who may perform which roadmap mutation action.
Read in conjunction with `ADR034_ADDENDUM_R2_ROADMAP_SSOT_CLARIFICATION_v1.0.0.md` and
`ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md`.

---

## Authority Table

| Action | team_00 | team_100 (hub repo) | team_100 (spoke repo) | team_191 | team_110 | all other teams |
|--------|:-------:|:-------------------:|:---------------------:|:--------:|:--------:|:---------------:|
| **Add new WP** (bootstrap, today) | ✅ approve | ✅ execute | ❌ → ROADMAP_INSERTION_REQUEST | ❌ | ❌ | ❌ |
| **Add new WP** (via `/AOS_roadmap-add`, post AOS-V325) | ✅ | ✅ | ✅ own domain | ❌ | ❌ | ❌ |
| **Patch WP metadata** (label, notes, spec_ref) | ✅ | ✅ | ✅ own domain | ❌ | ❌ | ❌ |
| **Patch operational state — hub WP** (AOS-V* / L0) | ✅ | ✅ via API | ❌ | ❌ | ❌ | ❌ |
| **Patch operational state — L2 spoke WP** (SNNN-PNNN-WPNNN) | ✅ | ✅ in spoke session | ✅ direct edit in spoke repo (ADR034 R9) | ❌ | ❌ | ❌ |
| **Defer WP** | ✅ approve | ✅ execute | ✅ execute + notify team_00 | ❌ | ❌ | ❌ |
| **Cancel WP** | ✅ approve | ✅ execute | ✅ execute + notify team_00 | ❌ | ❌ | ❌ |
| **Bootstrap / propagate** (_aos/ sync) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **File ROADMAP_INSERTION_REQUEST** | n/a | n/a | ✅ | ✅ | ✅ | ✅ any team |

---

## Definitions

**team_100 (hub repo)** — Team 100 executing within the agents-os hub repository. Same team ID as spoke team_100; the distinction is the active working directory and file access scope, not a separate authority class.

**team_100 (spoke repo)** — Team 100 executing within a spoke project repository (e.g., TikTrack, AOS-Sandbox). Cannot directly edit hub files. For L2 spoke WPs (SNNN-PNNN-WPNNN format, no hub DB row), may directly edit the spoke `_aos/roadmap.yaml` per ADR034 R9.

**own domain** — The spoke's own WPs (e.g., TikTrack spoke team_100 may create/patch WPs in the tiktrack domain, not in agents-os or other domains).

---

## Key Distinction — Hub WPs vs L2 Spoke WPs

| Property | Hub WP (AOS-V* / L0) | L2 Spoke WP (SNNN-PNNN-WPNNN) |
|---|---|---|
| ID format | `AOS-V[NNN]-WP-[NAME]` | `SNNN-PNNN-WPNNN` |
| Hub DB row | ✅ exists | ❌ does not exist |
| Hub API endpoint | ✅ `/api/l0/{project}/roadmap/advance` | ❌ rejected with INVALID_STATE |
| `roadmap.yaml` location | Hub `_aos/roadmap.yaml` | Spoke `_aos/roadmap.yaml` |
| SSoT mechanism | DB (via API) | File (git commit = audit record) |
| Who may mutate operational state | Hub team_100 via API | Spoke team_100 via direct file edit |
| Governing rule | ADR034 R2 / Iron Rule #7 | ADR034 R9 |

---

## Workflow — L2 Spoke WP Operational State Update (ADR034 R9)

```
1. Spoke team_100 identifies WP state to advance (e.g., L-GATE_V PASS → L-GATE_COMPLETE_QA)
2. Directly edits spoke _aos/roadmap.yaml:
   - Update: status, lod_status, current_lean_gate
   - Append to gate_history[] with date + verdict reference
3. Commit with message: "roadmap(SNNN-PNNN-WPNNN): advance to {new_gate} — {brief reason}"
4. No hub session required; no MSG-HUB artifact required
```

**Note:** Single-writer rule (Iron Rule #4) still applies. Only one agent holds write authority
over the spoke roadmap.yaml at a time.

---

## Workflow — Spoke team_100 Adding a New WP (interim, until AOS-V325)

```
1. Spoke team_100 drafts LOD200 spec in _aos/work_packages/<WP_ID>/
2. Files ROADMAP_INSERTION_REQUEST in _COMMUNICATION/team_100/
3. Team 00 routes to hub session
4. Hub team_100 executes:
   a. portfolio.create_work_package() → DB (ID format: SNNN-PNNN-WPNNN)
   b. Appends entry to _aos/roadmap.yaml (canonical AOS-V* ID + db_wp_id link)
5. aos_sync_all.sh propagates to spokes
```

**After AOS-V325-WP-ROADMAP-API lands:**
```
1. Spoke team_100 invokes /AOS_roadmap-add <params> from spoke session
2. Command calls POST /api/roadmap/wps on hub
3. Hub API atomically writes roadmap.yaml + DB
4. Response confirms canonical ID assigned
```

---

## ROADMAP_INSERTION_REQUEST Template

When filing a request (required for NEW WP bootstrap only — NOT for L2 spoke state updates):

```yaml
from: team_100 @ <spoke-domain>
request: ROADMAP_INSERTION_REQUEST
date: YYYY-MM-DD
wp_id_proposed: AOS-V<NNN>-WP-<NAME>     # canonical ID request
label: <one-line description>
track: A | B | C
profile: L0 | L2
risk: LOW | MEDIUM | HIGH
lod_status: LOD100 | LOD200
spec_ref: <path to LOD200 spec file>
depends_on: []                            # other WP IDs if any
notes: <rationale>
```

---

## Boundaries

- Hub `_aos/roadmap.yaml` (L0/AOS-V* WPs) is hub-only. Spoke sessions must NOT push edits to it.
- Spoke `_aos/roadmap.yaml` (L2/SNNN-PNNN-WPNNN WPs) is spoke team_100 writable per ADR034 R9.
- `_aos/governance/` snapshots are READ-ONLY in spokes — propagated by hub only.
- Any WP touching multiple domains requires hub team_100 execution regardless.

---

## References

- `governance/directives/ADR034_ADDENDUM_R2_ROADMAP_SSOT_CLARIFICATION_v1.0.0.md`
- `governance/directives/ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md`
- `governance/directives/ADR040_AOS_DOMAIN_AUTHORITY_LOCKDOWN_v1.0.0.md` (Iron Rule #12)
- `governance/directives/ADR041_COMMAND_ARCHITECTURE_UNIFICATION_v1.0.0.md` (Iron Rule #13)
- `_aos/work_packages/AOS-V325-WP-ROADMAP-API/LOD200_AOS-V325-WP-ROADMAP-API.md`
