---
doc_id: ROADMAP_AUTHORITY_MATRIX
version: 1.2.0
status: ACTIVE
supersedes: ROADMAP_AUTHORITY_MATRIX_v1.1.0.md
authority: team_00 (approval) + team_100 (author)
date: 2026-04-30
trigger: AOS-V4-WP-ENGINE-MATRIX (W2) — Track, Effort, Sprint columns (C9)
change_log:
  - v1.0.0: Initial matrix (2026-04-20) — L2 spoke team_100 required ROADMAP_INSERTION_REQUEST for all operational state changes
  - v1.1.0: L2 spoke WP exception per ADR034 R9 — spoke team_100 may directly edit spoke roadmap.yaml for SNNN-PNNN-WPNNN WPs
  - v1.2.0: Three new informational columns added — Track (6-track model per ADR044 §1), Effort (LOW/NORMAL/HI per ADR044 §3), Sprint (cap integer per ADR044 §5). Enables WP-level routing decisions at a glance.
---

# Roadmap Authority Matrix v1.2.0

Canonical reference for who may perform which roadmap mutation action.
Read in conjunction with `ADR034_ADDENDUM_R2_ROADMAP_SSOT_CLARIFICATION_v1.0.0.md`,
`ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md`, and
`ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` (Track + Effort + Sprint definitions).

---

## Authority Table (v1.2.0)

| Action | Track | Effort | Sprint Cap | team_00 | team_100 (hub repo) | team_100 (spoke repo) | team_191 | team_110 | all other teams |
|--------|-------|--------|:----------:|:-------:|:-------------------:|:---------------------:|:--------:|:--------:|:---------------:|
| **Add new WP** (bootstrap, today) | any | any | any | ✅ approve | ✅ execute | ❌ → ROADMAP_INSERTION_REQUEST | ❌ | ❌ | ❌ |
| **Add new WP** (via `/AOS_roadmap-add`, post AOS-V325) | any | any | any | ✅ | ✅ | ✅ own domain | ❌ | ❌ | ❌ |
| **Patch WP metadata** (label, notes, spec_ref, track, effort, sprint_cap) | any | any | any | ✅ | ✅ | ✅ own domain | ❌ | ❌ | ❌ |
| **Patch operational state — hub WP** (AOS-V* / L0) | any | any | any | ✅ | ✅ via API | ❌ | ❌ | ❌ | ❌ |
| **Patch operational state — L2 spoke WP** (SNNN-PNNN-WPNNN) | any | any | any | ✅ | ✅ in spoke session | ✅ direct edit in spoke repo (ADR034 R9) | ❌ | ❌ | ❌ |
| **Defer WP** | any | any | any | ✅ approve | ✅ execute | ✅ execute + notify team_00 | ❌ | ❌ | ❌ |
| **Cancel WP** | any | any | any | ✅ approve | ✅ execute | ✅ execute + notify team_00 | ❌ | ❌ | ❌ |
| **Bootstrap / propagate** (_aos/ sync) | any | any | any | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **File ROADMAP_INSERTION_REQUEST** | any | any | any | n/a | n/a | ✅ | ✅ | ✅ | ✅ any team |
| **Change Track assignment** (post-SPEC) | any → any | — | — | ✅ approve | ✅ execute | ✅ own domain | ❌ | ❌ | ❌ |
| **Change Effort level** (post-SPEC) | — | any → any | — | ✅ approve if HI | ✅ execute | ✅ own domain + notify team_00 if escalating to HI | ❌ | ❌ | ❌ |
| **Sprint cap override** (beyond ADR044 §5.2 max) | any | any | >3 | ✅ required | ✅ execute after team_00 approval | ❌ | ❌ | ❌ | ❌ |

---

## Track Column — Reference (ADR044 §1)

The `Track` column reflects the six-track classification from ADR044 §1.1. It is an **informational metadata field** on authority rows — it does not change the authority rules, only provides routing context.

| Track | Trigger / Nature | LOD path | Default builder engine |
|-------|-----------------|----------|------------------------|
| **EXPRESS** | ≤2 files; doc/config tweak; ADR text amendment | LOD400 only | claude-code or any-open |
| **STANDARD** | Product/governance WPs; clear scope; single domain | LOD200 → LOD400 → LOD500 | claude-code or codex |
| **MANAGED** | HIGH risk; multi-team; new state machine; cross-domain | LOD200 → LOD300 → LOD400 → LOD500 | cowork + claude-code |
| **RESEARCH** | Investigation; taxonomy; no code deliverable | LOD100 → research report | gemini or any |
| **OPS** | Infra; server; port-registry; deploy | LOD400 inline OR runbook | claude-code + team_99 |
| **CONTENT** | Non-code: book/presentation/design/video | LOD100 → LOD200 → shipped artifact | claude-desktop / gemini |

**Note:** L-tier (L0/L2/L3) is NOT a track. Per ADR044 §4 — L-tier = AOS install capability tier only. `track:` is a required field in every v4.0.0 WP `metadata.yaml`.

---

## Effort Column — Reference (ADR044 §3)

The `Effort` column reflects effort levels from ADR044 §3.1. It is an **informational metadata field**.

| Effort | Description | Sprint cap | Per-day $ cap | Per-WP total $ cap |
|--------|-------------|:----------:|:-------------:|:------------------:|
| **LOW** | Trivial; no design; auto-validate | 1 | $1 | $10 |
| **NORMAL** | Standard work; AC-based verification | 1–3 | $5 | $30 |
| **HI** | Complex; full design; multi-builder possible | up to 1 Stage | $20 | $100 |

Cost caps are enforced via `core/config/cost_caps.yaml` (W2 deliverable, C7).
Runtime enforcement is deferred to W6 (AOS-V4-WP-AUTO-ACTIVATION-DRYRUN).

---

## Sprint Column — Reference (ADR044 §5)

The `Sprint Cap` column reflects the sprint discipline from ADR044 §5.2. It is an **informational metadata field** showing the maximum sprint count for the WP.

| Sprint cap | Meaning | Escalation trigger |
|:----------:|---------|-------------------|
| 1 | EXPRESS track or LOW effort | Immediate restructure if exceeded |
| 1–3 | STANDARD track or NORMAL effort | team_100 scope review at sprint 3 start |
| Stage | MANAGED track or HI effort | team_00 check-in at each sprint boundary |

**Sprint definition (ADR044 §5.1):** ≤3 days / 1 engine / 1 writer / 1 deliverable.
**Sprint ID format:** `S[N].M[m].S[s]` — e.g., `S006.M1.S1`.

---

## Definitions

**team_100 (hub repo)** — Team 100 executing within the agents-os hub repository. Same team ID as spoke team_100; the distinction is the active working directory and file access scope, not a separate authority class.

**team_100 (spoke repo)** — Team 100 executing within a spoke project repository (e.g., TikTrack, AOS-Sandbox). Cannot directly edit hub files. For L2 spoke WPs (SNNN-PNNN-WPNNN format, no hub DB row), may directly edit the spoke `_aos/roadmap.yaml` per ADR034 R9.

**own domain** — The spoke's own WPs (e.g., TikTrack spoke team_100 may create/patch WPs in the tiktrack domain, not in agents-os or other domains).

**Track** — v4.0.0 WP classifier per ADR044 §1. Describes the nature and shape of work. Required field in metadata.yaml for all WPs created on or after 2026-04-30. See ADR044 §2 (decision tree) for binding Track assignment rules.

**Effort** — Resource intensity classifier per ADR044 §3. Orthogonal to Track. Governs cost caps, sprint count, validator depth, and documentation requirements.

**Sprint Cap** — Maximum number of sprints permitted for a WP per ADR044 §5.2. For NORMAL effort: ≤3 sprints (≤9 days). Sprint cap override requires team_00 approval.

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
| Track required? | ✅ (v4.0.0 forward) | ✅ (v4.0.0 forward) |
| Effort required? | ✅ (v4.0.0 forward) | ✅ (v4.0.0 forward) |

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
track: EXPRESS | STANDARD | MANAGED | RESEARCH | OPS | CONTENT   # v4.0.0 required
effort: LOW | NORMAL | HI                                          # v4.0.0 required
sprint_cap: <integer 1-3 or "Stage">                               # v4.0.0 required
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
- **Track assignment authority:** team_100 for hub WPs; domain lead architect for spoke WPs; team_00 is final arbiter (ADR044 §8.1).
- **Sprint cap override** (>3 sprints): always requires explicit team_00 approval — not a team_100 autonomous decision.

---

## References

- `governance/directives/ADR034_ADDENDUM_R2_ROADMAP_SSOT_CLARIFICATION_v1.0.0.md`
- `governance/directives/ADR034_ADDENDUM_R9_L2_SPOKE_ROADMAP_FILE_SSOT_v1.0.0.md`
- `governance/directives/ADR040_AOS_DOMAIN_AUTHORITY_LOCKDOWN_v1.0.0.md` (Iron Rule #12)
- `governance/directives/ADR041_COMMAND_ARCHITECTURE_UNIFICATION_v1.0.0.md` (Iron Rule #13)
- `governance/directives/ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` (Track + Effort + Sprint)
- `_aos/work_packages/AOS-V325-WP-ROADMAP-API/LOD200_AOS-V325-WP-ROADMAP-API.md`
- `core/config/cost_caps.yaml` (effort-level cost caps — C7, W2)

---

*Authored by team_110 (builder; WP W2 AOS-V4-WP-ENGINE-MATRIX; engine: claude-sonnet-4-6) — 2026-04-30*
*Approved by: team_00 (pending) + team_100 (authority)*
