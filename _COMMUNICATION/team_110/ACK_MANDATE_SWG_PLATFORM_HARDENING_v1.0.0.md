---
id: ACK_MANDATE_SWG_PLATFORM_HARDENING_v1.0.0
type: MANDATE_ACK
from: team_110 (Domain Architect — orchestrator)
to: team_100 (this spoke) / team_00 (Owner)
in_reply_to: MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0
date: 2026-04-30
status: ACKNOWLEDGED — BLOCKED pending items 1 and 6
priority: P1_URGENT
---

# ACK — MANDATE_SWG_PLATFORM_HARDENING — team_110

## §1 — Readback confirmation

All 6 Phase 0 files read in full:

| File | Status |
|---|---|
| MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0.md | READ |
| MSG-HUB-20260429-003-RESPONSE.md (LOD path ruling) | READ |
| REPORT_SUB_AGENT_PIPELINE_PATTERN_2026-04-29_v1.0.0.md (TikTrack canon) | READ |
| _aos/governance/team_110.md | READ |
| CLAUDE.md (spoke identity + iron rules) | READ |
| _aos/roadmap.yaml | READ |

Understood and confirmed:
- **Orchestrator-only role**: team_110 dispatches; sub-agents author; team_110 commits.
- **3 waves**: Wave 1 (M2+M3 parallel) → Wave 2 (M1) → Wave 3 (M4+M5 parallel).
- **Option A path canon**: `_aos/work_packages/SWG-PLAT-Mx/LOD{200,400}_spec.md`.
- **No sub-agent commits**: all commits owned by team_110 per §8 conventions.
- **Stop at Phase 7**: do NOT proceed to external validation; file BUNDLE_HANDOFF and pause for team_00.
- **CLAUDE.md _aos/ restriction is a known defect**: superseded by MSG-HUB-20260429-003-RESPONSE. team_110 proceeds under mandate authority without waiting for hub propagation.

---

## §2 — Pre-flight checklist (§6) — results

| # | Check | Result | Action required |
|---|---|---|---|
| 1 | S005-P002 registered in `_aos/roadmap.yaml` | **FAIL** | ROADMAP_REGISTRATION_REQUEST filed simultaneously (see §4). Dispatch BLOCKED until team_100 confirms. |
| 2 | DB connectivity probe (`db_connectivity_status.json`) | **PASS — ONLINE** | Iron Rule #7 active. All structured mutations via API. Direct `_aos/roadmap.yaml` edits forbidden — registration routed to team_100. |
| 3 | `validate_aos.sh .` | **PASS** | 30 PASS / 9 SKIP / 0 FAIL. L-GATE_BUILD EXIT CRITERION SATISFIED. |
| 4 | Required env vars present | **PENDING** | Will verify at dispatch time (suppressed from this artifact per IR policy). Expected: `ANTHROPIC_API_KEY`, FTP credentials. |
| 5 | Wave-1 sibling dependencies satisfied | **PASS** | M2 and M3 are fully independent code areas. Wave-1 can run in parallel. |
| 6 | No uncommitted changes in scope-overlapping files | **CONCERN — ACTION REQUIRED** | See §3 below. |

**Overall pre-flight result: BLOCKED on items 1 and 6. Wave-1 dispatch will not proceed until both are resolved.**

---

## §3 — Uncommitted changes triage (pre-flight item 6)

`git diff --stat HEAD` reveals **4,598 lines of changes across 13 files** in scope-overlapping paths:

| File | Lines changed | Overlap with |
|---|---|---|
| `data/listings.json` | +3,579 | M2 (data migration), M5 (input data) |
| `shaked_wg_agent/publisher/html_report.py` | +964 | M4 (outreach lifecycle UI) |
| `tests/test_config.py` | +72 | M1 (profile tests) |
| `shaked_wg_agent/config.py` | +19 | M1 (profile schema) |
| `shaked_wg_agent/scorer.py` | +48 | M1, M5 (scoring logic) |
| `tests/test_scorer.py` | +34 | M1 (scoring tests) |
| `data/runs.json` | +51 | Runtime data |
| `shaked_wg_agent/publisher/ftps_upload.py` | +27 | M4 (publisher) |
| `shaked_wg_agent/runner.py` | +8 | M2, M3 (runner) |
| `data/profiles/dror.json` | +1 | M1 (profile migration) |
| `data/sources.json` | +2 | M3 (sources) |
| `.env.example` | +22 | Env baseline |
| `scripts/run_dror_launch.sh` | +2 | Scripts |

**Assessment:** These are substantive changes from the prior live-search session (run-20260429-213722-f1bd). They appear to be partial implementations or live-session tooling — NOT to be discarded. Sub-agents dispatched against these files will create merge conflicts if these remain as working-tree modifications.

**Required resolution (team_00 decision):**

> **Option A (recommended):** Commit these as a `chore: pre-mandate baseline — live session work` commit on main before dispatch. Sub-agents will then see a clean baseline to build upon.
> **Option B:** Stash (`git stash`) before dispatch, pop after all M1–M5 WP builds complete. Risky — stash conflicts likely given overlap.
> **Option C:** Discard (NOT recommended — 4,598 lines of likely-valid live-session work would be lost).

**team_110 will not dispatch until team_100 / team_00 confirms which option to take and it is executed.**

---

## §4 — Roadmap registration request filed

Simultaneously with this ACK, team_110 has filed:

`_COMMUNICATION/team_110/ROADMAP_REGISTRATION_REQUEST_S005-P002_v1.0.0.md`

Requesting team_100 to register program `S005-P002` and WPs `SWG-PLAT-M1` through `SWG-PLAT-M5` in `_aos/roadmap.yaml` via the API (Iron Rule #7).

**team_110 will not dispatch any sub-agent until team_100 confirms registration is complete.**

---

## §5 — Wave-1 dispatch plan (ready to execute once blockers cleared)

**Target dispatch:** Wave 1 (M2 + M3 in parallel worktrees)

### M2 — Full-description extraction (sonnet sub-agent)
- Worktree: `worktrees/swg-plat-m2`
- Phases: LOD200 (architecture) → LOD400 (exec spec) → L-GATE_SPEC R1 (haiku) → BUILD → L-GATE_BUILD R1 (haiku) → L-GATE_VALIDATE R1 (haiku)
- Spec output: `_aos/work_packages/SWG-PLAT-M2/LOD200_spec.md`, `LOD400_spec.md`
- Key files: `shaked_wg_agent/scrapers/base.py`, `scrapers/flatfox.py`, `scrapers/wgzimmer_pw.py`, `data/listings.json` (migration), `tests/fixtures/scrapers/`

### M3 — wgzimmer scraper recovery (sonnet sub-agent)
- Worktree: `worktrees/swg-plat-m3`
- Phases: same 6-phase pipeline
- Spec output: `_aos/work_packages/SWG-PLAT-M3/LOD200_spec.md`, `LOD400_spec.md`
- Key files: `shaked_wg_agent/scrapers/wgzimmer_pw.py`, `scrapers/wgzimmer.py`, `tests/test_scrapers/test_wgzimmer.py`

Both will use the §5 sub-agent prompt template with deterministic haiku VC checklist (addresses C-1 rigor inconsistency from canonical pattern §4).

---

## §6 — Estimated timeline

| Phase | ETA (orchestrator wall-clock) |
|---|---|
| Blockers resolved + Wave 1 dispatch | T+0 (pending team_100 + team_00 action) |
| Wave 1 (M2+M3) Phases 2–7 complete | T + ~60–90 min |
| Wave 2 (M1) Phases 2–7 complete | T + ~90–120 min |
| Wave 3 (M4+M5) Phases 2–7 complete | T + ~120–180 min |
| BUNDLE_HANDOFF filed | T + ~3–5h total |

Per canonical-pattern empirical data (TikTrack P006): ~30–60 min/WP × 5 WPs = 2.5–5h orchestrator time.

---

## §7 — PIPELINE_DASHBOARD initialized

`_COMMUNICATION/team_110/SWG-PLAT-PIPELINE_DASHBOARD_v1.0.0.md` created and will be updated after every sub-agent return / verdict / commit.

---

## §8 — team_110 identity header

**team_110 (Domain Architect — orchestrator-mode)**
Spoke: shaked-wg-agent (L0)
Date: 2026-04-30
Mandate: MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0

---

*ACK filed per §15. Dispatch blocked pending: (1) ROADMAP_REGISTRATION_REQUEST confirmation from team_100; (2) uncommitted changes resolution from team_00. team_110 ready to proceed immediately upon clearance.*
