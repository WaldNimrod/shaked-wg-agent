---
id: ADR042_ADDENDUM_TEAM191_DISSOLUTION
title: ADR042 WP Closure Protocol — Addendum: Team 191 dissolved; closure executor reassigned (D-191auth split)
status: LOCKED
version: v1.1.0
date: 2026-07-10
authors: [team_120]
cosigned: [team_00, team_100]   # GCR-2 co-signed 2026-07-08 (DECISION_team_100_M11_CLEANDESK_RULINGS_AND_RATIFICATIONS_2026-07-08 §D)
scope: AOS-hub
supersedes: ADR042 v1.0.0 — the "Team 191" executor references in §"Mandatory Closure Sequence" Step 1 and §"Ordering constraint" ONLY (the rest of ADR042 v1.0.0 stands unchanged)
---

# ADR042 — Addendum v1.1.0: Team 191 dissolution → closure executor reassignment

## Why this addendum

`ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md` (LOCKED, 2026-04-19) names **Team 191** as the archival executor in its
Step 1 ("issue **Team 191** archival mandate … do NOT proceed until **Team 191** confirms ARCHIVE_MANIFEST.md
written") and in its Ordering constraint ("the archive manifest is written by **Team 191**"). **team_00 dissolved
Team 191 on 2026-07-05.** ADR042 v1.0.0 is an immutable decision record, so its named-executor references are
**superseded** here rather than edited in place (no history rewrite).

## The reassignment (ratified by GCR-2, co-signed 2026-07-08)

Team 191's post-gate-archive duty is split (**D-191auth**), matching the already-updated
`POST_GATE_ARCHIVE_PROCEDURE.md` (v1.3.0):

| Facet | New owner |
|-------|-----------|
| **Custodian** of the procedure + `_aos/` archive authority | **team_120** (Ambassador) — inherits team_191's `_aos/` write authority (D-191auth) |
| **Execution** of the archive move | the **closing orchestrator** (team_100 hub-native; team_110 under ADR045) via `/AOS_archive` (API-mediated `archive.py` `execute_archive()`, which performs the Step-6b physical-presence verify) |
| **git** commit/push of the archive | **team_60** — or any team under an explicit team_00 mandate |

## Superseding text (replaces the Team 191 references in ADR042 v1.0.0)

**Step 1 (amended).** *Immediately on L-GATE_VALIDATE PASS receipt* → the **closing orchestrator** runs the post-gate
archive via `/AOS_archive` (`archive.py`) per `POST_GATE_ARCHIVE_PROCEDURE.md` v1.3.0; do NOT proceed to Step 2 until
`ARCHIVE_MANIFEST.md` is written **and** every intended destination is verified physically present under
`_archive/<WP-ID>/` (`verified_count == intended_count`). **team_120** is custodian of the procedure; **team_60**
commits the archive. The Iron Rule #15 archive obligation is unchanged — only the named executor changes.

**Ordering constraint (amended).** Steps 1 → 2 → 3 remain ordered. Step 1 (archive) must complete before Step 2 (DB
lock) because the archive manifest — now written by the **closing orchestrator via `archive.py`** (not Team 191) —
confirms the artifact set is stable and physically moved.

## What is NOT changed

- ADR042 v1.0.0's three-step closure sequence, LOD500_LOCKED terminal state, exemptions, and Check-15 enforcement all
  stand unchanged.
- **No history rewrite:** ADR042 v1.0.0 itself, ADR039/ADR045, KNOWN_BUGS, and every `_COMMUNICATION/` artifact naming
  Team 191 remain as-is — accurate audit trail for their date.

## References

- `governance/directives/ADR042_WP_CLOSURE_PROTOCOL_v1.0.0.md` — the superseded base
- `lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md` v1.3.0 — the updated runbook (D-191auth executor; Step-6b verify-and-move)
- `_COMMUNICATION/team_120/GCR_team_120_DEPLOY-CANON-AND-TEAM191-DISSOLUTION_2026-07-05_v1.0.0.md` — GCR-2 (source)
- `governance/directives/ARCHITECT_DIRECTIVE_TEAM_ROSTER_LOCK_v4.1.0.md` — the roster-tier supersession record (companion to this addendum)
- `_COMMUNICATION/team_100/DECISION_team_100_M11_CLEANDESK_RULINGS_AND_RATIFICATIONS_2026-07-08_v1.0.0.md` §D — co-sign

---
*team_120 (author) · team_00 + team_100 co-signed 2026-07-08 · ADR042 Addendum v1.1.0 · 2026-07-10 · Team 191 dissolution*
