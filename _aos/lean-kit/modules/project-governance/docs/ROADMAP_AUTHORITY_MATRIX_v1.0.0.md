---
doc_id: ROADMAP_AUTHORITY_MATRIX
version: 1.0.0
status: ACTIVE
authority: team_00 (approval) + team_100 (author)
date: 2026-04-20
trigger: HUB_UPDATE_AOS100_ROADMAP_API_GAP_2026-04-20_v1.md (TikTrack spoke team_100)
---

# Roadmap Authority Matrix v1.0.0

Canonical reference for who may perform which roadmap mutation action.
Read in conjunction with `ADR034_ADDENDUM_R2_ROADMAP_SSOT_CLARIFICATION_v1.0.0.md`.

---

## Authority Table

| Action | team_00 | team_100 (hub repo) | team_100 (spoke repo) | team_191 | team_110 | all other teams |
|--------|:-------:|:-------------------:|:---------------------:|:--------:|:--------:|:---------------:|
| **Add new WP** (bootstrap, today) | ✅ approve | ✅ execute | ❌ → ROADMAP_INSERTION_REQUEST | ❌ | ❌ | ❌ |
| **Add new WP** (via `/AOS_roadmap-add`, post AOS-V325) | ✅ | ✅ | ✅ own domain | ❌ | ❌ | ❌ |
| **Patch WP metadata** (label, notes, spec_ref) | ✅ | ✅ | ✅ own domain | ❌ | ❌ | ❌ |
| **Patch operational state** (status, lod_status, gate) | ✅ | ✅ | ❌ → file ROADMAP_INSERTION_REQUEST | ❌ | ❌ | ❌ |
| **Defer WP** | ✅ approve | ✅ execute | ✅ execute + notify team_00 | ❌ | ❌ | ❌ |
| **Cancel WP** | ✅ approve | ✅ execute | ✅ execute + notify team_00 | ❌ | ❌ | ❌ |
| **Bootstrap / propagate** (_aos/ sync) | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **File ROADMAP_INSERTION_REQUEST** | n/a | n/a | ✅ | ✅ | ✅ | ✅ any team |

---

## Definitions

**team_100 (hub repo)** — Team 100 executing within the agents-os hub repository. Same team ID as spoke team_100; the distinction is the active working directory and file access scope, not a separate authority class.

**team_100 (spoke repo)** — Team 100 executing within a spoke project repository (e.g., TikTrack, AOS-Sandbox). Cannot directly edit hub files — must route via ROADMAP_INSERTION_REQUEST or (post-AOS-V325) `/AOS_roadmap-add` command calling hub API.

**own domain** — The spoke's own WPs (e.g., TikTrack spoke team_100 may create WPs in the tiktrack domain, not in agents-os or other domains).

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

When filing a request, include:

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

- `_aos/roadmap.yaml` is hub-only. Spoke sessions must NOT push edits to it.
- `_aos/governance/` snapshots are READ-ONLY in spokes — propagated by hub only.
- Any WP touching multiple domains requires hub team_100 execution regardless.

---

## References

- `governance/directives/ADR034_ADDENDUM_R2_ROADMAP_SSOT_CLARIFICATION_v1.0.0.md`
- `governance/directives/ADR040_AOS_DOMAIN_AUTHORITY_LOCKDOWN_v1.0.0.md` (Iron Rule #12)
- `governance/directives/ADR041_COMMAND_ARCHITECTURE_UNIFICATION_v1.0.0.md` (Iron Rule #13)
- `_aos/work_packages/AOS-V325-WP-ROADMAP-API/LOD200_AOS-V325-WP-ROADMAP-API.md`
