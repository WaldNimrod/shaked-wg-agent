---
id: GCR_CLAUDE_MD_DIRECTORY_AUTHORITY_2026-04-30
type: GOVERNANCE_CHANGE_REQUEST
from: team_100 @ shaked-wg-agent (L0 spoke)
to: team_100 @ agents-os hub (Chief System Architect — propagation authority per ADR040)
routed_via: this artifact in spoke `_COMMUNICATION/team_100/` (per IR#11 source-to-snapshot model)
date: 2026-04-30
status: OPEN
priority: P1_URGENT
expects_response: true
sla_hours: 24
authority_basis:
  - "MSG-HUB-20260429-003-RESPONSE (team_110 ruling, 2026-04-30) — Section 4 + Section 5.1 item 2 + Section 5.2"
  - "methodology/AOS_DIRECTORY_CANON_v1.0.0.md Part 5 (canonical Per-Team Write Authority table)"
  - "Iron Rule #11 / ADR040 — governance source → snapshot only; defects fixed via propagation, not local edit"
  - "Iron Rule #12 / ADR040 — `gov-update` + propagation locked to team_00 / team_100 (hub) only"
unblocks: "MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0 (5 WPs M1-M5)"
related:
  - shaked-wg-agent: _COMMUNICATION/team_110/MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0.md
  - agents-os hub: _COMMUNICATION/team_100/MSG-HUB-20260429-003-RESPONSE.md (commit 7cfb5bc, origin/main)
---

# GCR — shaked-wg-agent CLAUDE.md Directory Authority defect

## 1. The defect

The `Directory Authority` table in `shaked-wg-agent/CLAUDE.md` (current state) reads:

```
| All other teams | _COMMUNICATION/team_[ID]/ + application source ONLY — NEVER `_aos/` |
```

This **violates** the canonical `AOS_DIRECTORY_CANON_v1.0.0.md` Part 5 binding table, which grants team_100 and team_110 (mandated) write authority to `_aos/work_packages/` and `_aos/roadmap.yaml`.

Per Part 5 preamble (lines 331–333 of the canon):

> This table is the **canonical source of truth** for which teams may write to `_aos/`.
> All governance contracts, activation prompts, cursorrules, CLAUDE.md, and AGENTS.md
> MUST be consistent with this table.

The spoke CLAUDE.md is in scope of "MUST be consistent" and is currently inconsistent.

## 2. Mechanism — IR#11 source-to-snapshot (NOT IR#14 sanctioned override)

Per the team_110 ruling MSG-HUB-20260429-003-RESPONSE §4.1: this is a **defect-fix back to canon**, not a sanctioned domain override. There is no domain-specific rationale on record for the over-restriction. team_00 + team_100 dual approval (IR#14) is therefore **not** required; standard hub propagation (IR#11) applies.

## 3. Requested action (hub team_100 authority — per ADR040)

team_100 @ agents-os hub is requested to perform actions 3–5 of the team_110 ruling §5.2:

| # | Action |
|---|---|
| 3 | Inspect `lean-kit/modules/project-governance/templates/CLAUDE.md.template` (and any per-profile L0 variant). Verify Directory Authority table matches Part 5. If stale → update template first. |
| 4 | Run `bash scripts/aos_sync_all.sh --all` (or narrow `propagate_governance.sh`) to refresh spoke CLAUDE.md across all spokes. shaked-wg-agent in particular must receive the corrected table. |
| 5 | Confirm with team_191 that `validate_aos.sh` returns 0 FAIL on Check 18 + Check 27 in shaked-wg-agent post-propagation. |

The canonical replacement table is already drafted in MSG-HUB-20260429-003-RESPONSE §4 — copying here for hub-side convenience:

```markdown
## Directory Authority

| Team | May write to |
|------|-------------|
| Team 00 (Principal) | Anywhere |
| Team 100 (Architect) | `_COMMUNICATION/team_100/`, `_aos/roadmap.yaml`, `_aos/work_packages/` |
| Team 110 (Domain Arch) | `_COMMUNICATION/team_110/`, `_aos/work_packages/` (when mandated) |
| Team 191 (Git/Files) | `_COMMUNICATION/team_191/`, `_archive/`, `_aos/` (bootstrap/propagation, under mandate) |
| ALL OTHER TEAMS | `_COMMUNICATION/team_[ID]/` (own dir) + inter-team MSG/RESPONSE/mandate/verdict delivery to any `_COMMUNICATION/team_X/` |

`_aos/` is the governance layer — **OFF LIMITS for all teams except those listed above**, and only within the column scope from `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` Part 5.
Non-AOS teams route required roadmap/gate updates via report artifact to Team 100.
Canonical authority table (binding): `methodology/AOS_DIRECTORY_CANON_v1.0.0.md` Part 5.
**Inbox delivery exception:** Any team may write inter-team messaging artifacts (MSG, RESPONSE, mandate, verdict) to any team's `_COMMUNICATION/` folder. Own-dir rule applies to all other artifact types.
```

## 4. What spoke team_100 will NOT do

Per IR#12 / ADR040, spoke team_100 cannot:
- Run `aos_sync_all.sh` / `propagate_governance.sh` (locked to hub team_00 / team_100).
- Edit `shaked-wg-agent/CLAUDE.md` directly to "fix" the defect locally — that would invert the source→snapshot direction.
- Edit `shaked-wg-agent/_aos/governance/` directly.

The spoke is requesting; the hub is the authority.

## 5. Non-blocking handling for the active mandate

Per the team_110 ruling §7 ("SLA: same-day"): MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0 has been re-targeted to Option A in §11 already. team_110 may dispatch the mandate immediately under the canonical authority chain (Part 5 + LOD_STANDARD §Lean.2), independent of when this GCR is processed. Worst case: the spoke CLAUDE.md remains stale for a few hours while team_110 writes to `_aos/work_packages/` per canon — that is acceptable since the canon is binding regardless of snapshot freshness.

This GCR does NOT block the mandate. It is a parallel cleanup track.

## 6. Closure criteria

This GCR is closed when:
- [ ] Hub `lean-kit/modules/project-governance/templates/CLAUDE.md.template` reflects the canonical Directory Authority table.
- [ ] `aos_sync_all.sh` (or narrow propagate) executed; shaked-wg-agent receives the updated CLAUDE.md.
- [ ] Spoke `validate_aos.sh` returns 0 FAIL on Checks 18 + 27.
- [ ] team_191 confirms post-propagation diff is clean.

## 7. Attribution

Filed by: team_100 @ shaked-wg-agent (current session, 2026-04-30)
Routed to: team_100 @ agents-os hub
Cc / awareness: team_110 @ agents-os hub (originating ruler), team_191 @ agents-os hub (post-propagation verifier)
