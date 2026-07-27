---
id: SPEC_CONVENTIONS_KERNEL
title: "M10 P3 Cockpit — SPEC Conventions Kernel (anti-drift authoring contract)"
milestone_ref: AOS-V5-M10
phase: P3 (Cockpit capstone)
author: team_100 (Chief System Architect · parallel cockpit-authoring session)
date: 2026-07-01
version: v1.0.0
status: FROZEN — every CK LOD200/LOD300/LOD400 MUST cite this kernel verbatim
supersedes: null
scope: internal authoring contract (not itself a gated LOD deliverable; enforced transitively via each CK's L-GATE_SPEC)
---

# SPEC Conventions Kernel — M10 Cockpit (CK-0 … CK-9)

> **Purpose.** Ten interdependent LOD400 specs authored by concurrent sessions WILL drift on
> enum values, colours, endpoint paths, SSE event names, Hebrew copy, thresholds, and component
> props unless they all bind to ONE frozen reference. **This kernel is that reference.** Every CK
> package (CK-0 … CK-9) MUST cite the block below for every enum, colour, endpoint, SSE event,
> threshold, typography rule, N×4 state label, and the M1 create-contract. **Inventing a value not
> in this kernel is a spec defect (BLOCKER at L-GATE_SPEC).** Copy shared Hebrew copy and the N×4
> column headers character-for-character.

---

## §0 — team_00 rulings binding this authoring run (2026-07-01)

1. **Validation = single-engine Cursor (`composer-2.5`) only.** team_00 (Principal) ruled the
   handoff's *dual* (Cursor + ChatGPT) L-GATE_SPEC validation down to **one** cross-engine validator:
   **Cursor / `composer-2.5`**. This still satisfies **IR#1 Tier-2** (Cursor ≠ Claude → different
   vendor/model_family → decisive cross-engine per ADR053). It is a **recorded Principal override of
   the dual mandate**, NOT a silent downgrade. Every CK `metadata.yaml` records
   `validation_tiering.L-GATE_SPEC.cross_engine: true` with `engines: [composer-2.5]` and a
   `team_00_override` note. ChatGPT/`gpt-5.2-codex` is NOT run this milestone.
2. **Parallel authoring.** The surface/modal fan-out (CK-2…CK-8 ∥ CK-9-LOD400) is authored by
   **concurrent worktree-isolated sessions**, each binding to this frozen kernel + the frozen CK-9
   data contract. The foundation (this kernel + CK-0 + CK-1 + CK-9 contract) is authored first because
   the dependency graph requires it.
3. **SPEC authoring only.** No cockpit application code is built in this run. Specs GROUND against the
   already-built backend (read `core/`, never edit it). BUILD is team_110's sequenced P3 job.
4. **Validation loop-termination policy (point-fix for BUG-M10-VAL-LOOP-001).** The L-GATE_SPEC
   validation runs **exactly ONE** Cursor (`composer-2.5`) pass per CK. **Fix only `[BLOCKER]` findings**,
   then re-run **at most once** (hard cap: **2 Cursor invocations per CK**). **Accept at `CONDITIONAL_GO`** —
   `[MAJOR]`/`[MINOR]` findings that remain become a **documented punch list for team_110 at BUILD**, NOT
   chased at SPEC. **Never loop the validator toward a literal `VERDICT: PASS`.** Rationale: `composer` is a
   pedantic adversary that surfaces a fresh narrow prop/path/copy refinement each round while drift-critical
   fidelity (enums/colours/endpoints) passes every round — chasing a pristine PASS is non-terminating and
   token-wasteful. The **decisive** cross-engine gate is L-GATE_VALIDATE at BUILD (ADR053); SPEC is a
   quality gate. Validation is **orchestrator-controlled** (authoring agents author + self-review only; they
   do NOT run the validator). Incident + root-cause tracking: roadmap `BUG-M10-VAL-LOOP-001`.

---

## §1 — ENUM BLOCK (source: `_aos/v5_characterization/synthesis/CANON_COCKPIT_ENUMS_v1.0.0.md`, locked)

**Rule:** specs CITE these values; they never redefine, translate differently, or invent an enum.
A status/session/gate/track token not on these lists = automatic BLOCKER. All enum tokens render in
**JetBrains Mono** (machine voice). Cockpit reads these from live `GET /api/enums` (`canon_service.list_enums`).

### 1.1 WP status (lifecycle) — 7 values
| enum | Hebrew label | colour role | meaning |
|---|---|---|---|
| `DRAFT` | טיוטה | idle (gray) | created, not started |
| `ACTIVE` | פעיל | run (blue) | in work (at some gate) |
| `IN_VALIDATION` | בולידציה | run (blue) | at VALIDATE gate (validator engine running) |
| `AWAITING_YOU` | ממתין לך | await (purple) | requires team_00 decision (approval/closure) |
| `BLOCKED` | חסום | block (red) | stuck / anomaly |
| `CLOSED` | נסגר | ok (green) | LOD500_LOCKED (done) |
| `ARCHIVED` | אורכב | archived (`#c2c6cf`) | moved to archive |

### 1.2 Gates — the progress pipe
`LOD_CHECK` (טעימות+השלכות) · `SPEC` (אפיון) · `BUILD` (בנייה) · `VALIDATE` (ולידציה) ·
`CLOSE` (סגירה) · `DELIVER` (מסירה — CONTENT track only) · modifier `HG-1`/`HG-2` (שערי-אדם — MANAGED only).
**Gate paths per track (GatePipe segments):**
- `STANDARD`: LOD_CHECK → SPEC → BUILD → VALIDATE → CLOSE
- `EXPRESS`: LOD_CHECK → BUILD → (VALIDATE) → CLOSE
- `MANAGED`: LOD_CHECK → SPEC → HG-1 → BUILD → VALIDATE → HG-2 → CLOSE
- `RESEARCH`: LOD_CHECK → (report) → CLOSE
- `CONTENT`: LOD_CHECK → SPEC → BUILD → DELIVER → CLOSE
- **Legacy `GATE_0`–`GATE_8` are deprecated, read-only bridge only** (CANON §2b). NEVER emit a numeric gate; named gates are the sole canon.

### 1.3 Session status — 5 values
| enum | Hebrew | colour | meaning |
|---|---|---|---|
| `RUNNING` | רץ | run (blue) | active now |
| `WAITING` | ממתין | wait (orange) | async — **declared** wait (reason set); STUCK timer paused |
| `STUCK` | תקוע | wait (orange-warn ⚠) | heartbeat silence > `T_stuck` WITHOUT declaration → anomaly (C2) |
| `IDLE` | סרק | idle (gray) | registered, not active |
| `CLOSED` | נסגר | idle-light (`#c2c6cf`) | finished |

> **A1 anti-alert-fatigue (locked):** `WAITING(declared)` ≠ `STUCK(inferred)`. The heartbeat/`T_stuck`
> timer runs ONLY in RUNNING-without-declaration. `WAITING` is legitimate, not an anomaly.

### 1.4 Session type (role → default engine; override always allowed per-task) — 10 values
`ARCHITECT` (team_100·Claude Code) · `ORCHESTRATOR` (team_110·Claude Code) ·
`SUBAGENT` (team_10/20/30·flexible) · `VALIDATION` (team_90/190·Codex/Cursor cross-engine) ·
`QA` (team_50·external+browser-QA) · `RESEARCH` (team_80·web/local/NotebookLM) ·
`OPS` (team_99·waldhomeserver) · `COWORK` (team_200·Claude Desktop) ·
`DESIGN` (team_35·Claude Design) · `AMBASSADOR` (team-dedicated·governance-only).

### 1.5 Domain/spoke status (`domain_status`) — 4 values
`ACTIVE` (פעיל·blue) · `DORMANT` (רדום·orange — auto when `last_activity` > `dormancy_days`) ·
`CLOSED` (סגור·gray) · `ARCHIVED` (אורכב·gray-light).

### 1.6 Track (ADR044) — 7 values
`EXPRESS` · `STANDARD` · `MANAGED` · `RESEARCH` · `OPS` · `CONTENT` · `HOTFIX`.

### 1.7 LOD100 verdict fields (routed to team_00 via `AWAITING_YOU`)
`taste_verdict` (טעם) · `consequences_verdict` (השלכות). WP-state fields, not enum values.

---

## §2 — COLOUR LEGEND BLOCK (source: `design-system/tokens/colors.css`, LOCKED by CANON §6)

**The five status colours are immutable. Status is carried by DOTS, never icons. Brand petrol
`#0c8f9c` NEVER implies status.** AWAITING_YOU purple is decoupled from brand accent so the
"needs a human" signal never drifts.

| token | hex | role |
|---|---|---|
| `--legend-ok` | `#16a34a` | green · ok / closed |
| `--legend-run` | `#2563eb` | blue · running |
| `--legend-wait` | `#d97706` | orange · waiting / anomaly |
| `--legend-block` | `#dc2626` | red · blocked / needs-you-urgent |
| `--legend-idle` | `#9ca3af` | gray · idle / draft |
| `--await` | `#6b4fc4` | purple · AWAITING_YOU (stable, decoupled) |
| `--accent` (petrol) | `#0c8f9c` | brand/chrome/primary-action ONLY — **never status** |

Soft fills: `--legend-ok-soft #e9f7ee` · `--legend-run-soft #e7eefe` · `--legend-wait-soft #fdf0e7`
· `--legend-block-soft #fdeaea` · `--legend-idle-soft #eef0f3` · `--await-soft #f1edfb`
· `--accent-soft #dff2f4`. Archived status colour = `#c2c6cf`.

**Status → role mapping (verbatim from colors.css):** DRAFT→idle · ACTIVE→run · IN_VALIDATION→run ·
AWAITING_YOU→await(purple) · BLOCKED→block · CLOSED→ok · ARCHIVED→`#c2c6cf`.

---

## §3 — REST ENDPOINT BLOCK (source: `core/modules/management/api.py` + `dashboard_routes.py`, live on `:8092`)

**Contract:** cockpit reads REST + SSE; writes the SAME REST endpoints with **server-side P9 (id-mint)
+ version-guard (If-Match)**; **cockpit NEVER hits the DB directly.** All paths are prefixed `/api`.
A surface LOD400 that needs data MUST name the exact route below; anything not present here is a
**backend delta** flagged for team_110 (not silently assumed to exist).

### 3.1 Reads
| route | serves surface |
|---|---|
| `GET /api/work-packages` (+`?project_id=`) · `GET /api/work-packages/{wp_id}` | CK-2 Map, CK-3 WP |
| `GET /api/work-packages/{wp_id}/routing-explain` | CK-3 (read-only routing explainer) |
| `GET /api/runs` (status/domain/gate filters) · `GET /api/runs/{run_id}` · `.../state` · `.../history` | CK-2, CK-3 |
| `GET /api/runs/{run_id}/context` (token budget + approx_tokens) | CK-3 cost panel |
| `GET /api/teams` · `GET /api/teams/{team_id}` · `GET /api/teams/{team_id}/context` | CK-7 Settings |
| `GET /api/ideas` (funnel; degrade-mirrors on DB-down) | CK-5 Funnel |
| `GET /api/enums` · `GET /api/roster` · `GET /api/faq` | CK-6 Help, CK-7 Settings, all (enum read) |
| `GET /api/policies` | CK-7 Settings, CK-9 (D3 thresholds) |
| `GET /api/routing-policy` · `GET /api/routing-rules` | CK-7 Settings |
| `GET /api/templates` · `GET /api/templates/{id}` | CK-8 M2 mandate preview |
| `GET /api/feedback/stats` | CK-2 needs-you feed (D1 input signal) |
| `GET /api/governance/status` | CK-7 Settings health |
| `GET /api/system/health` + `db_connectivity_status.json` + `wan_dual_stack_status.json` | CK-7 health panel (D2 trivial wrap of 3 probes) |
| messaging reads under `/api/messaging/*` (+ `/api/messaging/v2/inbox`) | CK-4 Mail (all-box monitor, domain log) |

### 3.2 Writes (server-side P9 + version-guard; cockpit signs as team_00 device-key — see D7/§9)
| route | method | surface | guard |
|---|---|---|---|
| `/api/work-packages` | POST | CK-8 M1 create | P9 id-mint (`INVALID_WP_ID_FORMAT` 400), track enum, description required |
| `/api/runs/{run_id}/advance`·`/fail`·`/approve`·`/pause`·`/resume`·`/override`·`/reject-entry` | POST | CK-3 gate actions | SM-B `advance_gate`; IR#1 at decisive gate (403 `IR1SameEngine`); If-Match 412 |
| `/api/runs` | POST | CK-8 M2 dispatch → run | binding team+domain (P9/CA18) |
| `/api/work-packages/{wp_id}/start`·`/cancel` | POST | CK-3 | — |
| `/api/ideas` | POST · `PUT /api/ideas/{id}` | CK-5 Funnel | — |
| `/api/ideas/{id}/promote` | POST | CK-5 → CK-8 M1 | promote idea → WP |
| `/api/messaging/v2/send` (+ `/api/messaging/*`) | POST | CK-4 Mail send | binding sender team+domain |
| `/api/enums/{kind}/{value}`·`/api/roster/{role}`·`/api/policies/{id}`·`/api/routing-rules[/{id}]` | PUT/POST/DELETE | CK-7 Settings CRUD | **team_00 only** |
| `/api/teams/{team_id}/engine`·`/environment` | PUT | CK-7 team→engine pills | **team_00 only** |

**Error codes — the REAL surfaced `code` STRINGS (grounded verbatim in `sm_b.py` / `authority.py`;
these are the `code=...` values the API returns, NOT the Python class names) that every write-spec must
surface verbatim (rev: corrected from class-name form during CK-9 grounding, 2026-07-01):**
`INVALID_WP_ID_FORMAT` (400) · `ILLEGAL_TRANSITION` (409) · `IR1_SAME_ENGINE` (403) ·
`IF_MATCH_FAILED` (412, version-guard) · `WP_NOT_FOUND` (404) · `BLOCKED_EXIT_NOT_HUMAN` (403) ·
`SMB_ERROR` (400, base) · `MISSING_ACTOR_HEADER` (400) · `INVALID_ACTOR_KEY` (401) ·
`ACTOR_VERIFICATION_DISABLED` (403) · `TEAM_ID_MISMATCH` (403).

---

## §4 — SSE EVENT BLOCK (source: `GET /api/events/stream`, `api.py` + `modules/audit/sse.py`)

Cockpit subscribes `GET /api/events/stream` (optional query scoping: `run_id`, `domain_id`,
`awaiting_msg`, `team`). **Exactly these 9 event types are emitted** by live `core/modules/audit/sse.py`
(rev: corrected from 6 → 9 during CK-9 grounding, 2026-07-01 — the extra 3 are pre-existing add-only
emissions, NOT invented). A spec may not invent a NEW event beyond these 9; new live data needs an
add-only emission flagged as a backend delta (D5).

| event | consumed by |
|---|---|
| `pipeline_event` | CK-2 gate-pipe advance, CK-3 gate-history |
| `run_state_changed` | CK-2 WP cards status dots, CK-3, live-sessions rail |
| `heartbeat` | CK-2/CK-3 session status (SM-C RUNNING/STUCK inference) |
| `feedback_ingested` | CK-2 needs-you rail (D1 anomaly input) |
| `msg_received` (team-scoped, CC-01) | CK-4 Mail |
| `msg_response_received` | CK-4 Mail |
| `session_state_changed` | CK-2/CK-3 live-sessions rail (SM-C status transitions) |
| `verdict_received` | CK-3 gate-history, CK-2 needs-you (gate verdict PASS/FAIL) |
| `wp_status_changed` | CK-2 map WP-card liveness (non-verdict SM-B transitions the other events miss) |

**Poll-fallback rule:** every SSE-driven view MUST degrade to a REST poll if the stream drops
(SM-D DEGRADED). Poll interval = `cache_ttl_seconds` (§5). This is acceptable (D5).

---

## §5 — D3 THRESHOLD BLOCK (seeded defaults — CK-9 formalises; tunable via `GET/PUT /api/policies`, team_00)

**"Seed D3 first" mandate.** Every surface that renders STUCK / dormant / needs-you / WIP status cites
these EXACT seeded values. They live in the `policies` table; the cockpit reads them, never hardcodes.

| policy id | seeded default | governs |
|---|---|---|
| `T_stuck` | **900 s (15 min)** | session heartbeat silence WITHOUT declaration → `STUCK` (SM-C) |
| `awaiting_you_age_warn` | **24 h** | AWAITING_YOU item ranks "aging/urgent" in needs-you feed (always present; ranking only) |
| `wip_cap` | **3** (soft) | active-WP soft cap; cockpit **warns, never blocks** on exceed (C2) |
| `dormancy_days` | **14 d** | `domain_status` auto → `DORMANT` when `last_activity` older |
| `cache_ttl_seconds` | **30 s** (status reads) · **300 s** (param lists: domains/teams/subjects) | poll-fallback interval + dropdown cache |

**Enum-value alignment assert (D3):** `work_packages.status` ∈ §1.1 · `active_sessions.status` ∈ §1.3 ·
`ideas.status` ∈ its funnel enum · `domain_status` ∈ §1.5. A DB value outside the canon enum = silent
status-render breakage → CK-9 specs an alignment assert-test (spec-level; the test itself is team_110 BUILD).

---

## §6 — TYPOGRAPHY / RTL / LIGHT-ONLY BLOCK (source: `tokens/typography.css`)

- **Fonts:** `--font-ui` = **Heebo** (all UI prose, Hebrew+Latin). `--font-mono` = **JetBrains Mono** =
  the "machine voice" — use for **WP ids, enum tokens, mandate ids, gate timings, token/cost figures**.
- **Type scale (verbatim):** display 21 · title 15 · body 14 · sm 13 · xs 12.5 · 2xs 11.5 · micro 11 ·
  nano 10.5 (px). Never below 12.5px for prose. Weights 400/500/600/700/800. Leading 1.2/1.35/1.55.
- **RTL:** logical properties throughout (`margin-inline-*`, `inset-inline-*`, `text-align: start`);
  NO hardcoded left/right. `dir="rtl"` is the default; Latin/mono runs read LTR inline.
- **Light-only.** No dark mode. Canvas `--bg #f1f6f7`, panels `--panel #ffffff`.
- **D8 font self-host (CK-0):** Heebo + JetBrains Mono ship as local `woff2` + `@font-face`
  (replacing the Google-Fonts CDN `@import` in `tokens/fonts.css`) for offline resilience + privacy.
  Both are SIL-OFL — licence-clean. **No visual change.**

---

## §7 — N×4 STATE MATRIX SKELETON (verbatim Hebrew labels — the biggest drift preventer)

Every surface with UI defines, at LOD400, a matrix of **every surface region (N)** × the **4 states**.
Use these exact column headers and shared copy patterns character-for-character:

| state | header (verbatim) | shared copy pattern |
|---|---|---|
| empty | **ריק** (empty) | surface-specific "אין …" line + CTA (e.g. "אין חבילות בפרויקט", "אין חריגות", "אין רעיונות פתוחים") |
| loading | **טעינה** (loading) | skeleton shimmer (1.4 s sweep), 3–5 skeleton rows/cards; mono caption "מתחבר…" |
| error | **שגיאה** (error) | inline banner + "נסה שוב" CTA; preserve last cached state if present (e.g. "טעינת המפה נכשלה") |
| offline / degrade | **לא-מקוון (degrade+reconcile)** | **DegradeBanner** visible; read-only from git; writes → local changelog; reconcile on reconnect |

**DegradeBanner copy (verbatim, CANONICAL — rev 2026-07-01, resolves CK-0/CK-1 K-copy gap):**
degraded = red ⚠ "DB לא-זמין · עובד ב-git · reconcile ממתין"; reconciling = orange ↻ (spin)
**"מיישב {count} שינויים…"** (canonical wording — NOT "מסנכרן"; matches the CK-0 `DegradeBanner` component
and the ack root "ייושב"). Remote-normal (Tailscale+server up) = **no banner** (anti alert-fatigue).
Offline write acknowledgement string: "נשמר מקומית · ייושב עם החזרת החיבור".

---

## §8 — M1 CREATE-CONTRACT + P9 PREVIEW BLOCK (freezes CK-5 ∥ CK-8 binding)

**M1 "+ חבילה חדשה" create modal fields** (CK-8 owns the modal; CK-5 Funnel "promote" reuses THIS contract):
- `milestone` (select) · `project` (select/new) · **`slug`/מהות (required, mono)** · `track` (select from §1.6) ·
  **`description`/תיאור (required)** · live **id preview** (mono) built server-side as **`{M}-{P}-WP-{slug}`** (P9).
- **P9 enforcement surfaced inline:** id format (`INVALID_WP_ID_FORMAT` 400) · track enum mandatory ·
  description mandatory ("תיאור חובה"). Submit → `POST /api/work-packages`.

**M2 dispatch-session modal fields** (CK-8): role/task (select §1.4) · **engine** (auto-suggested + override;
rule **בונה≠מאמת** / builder≠validator) · **domain** (binding-required, P9/CA18) · token budget ·
mandate preview (from `GET /api/templates`, CA7) · mode (auto/manual, L38). Submit → `POST /api/runs`.

**D6 CLI-fallback (defer/document only):** when create/dispatch can't reach the API, the modal shows the
verbatim string **"git-mode · ייושב"** and documents the bridge contract (fields + changelog format) — no
engine is built this milestone.

---

## §9 — metadata.yaml CONVENTIONS (every CK identical shape; differences only in scope)

```yaml
wp_id: AOS-V5-M10-CK-<n>-<slug>
milestone_ref: AOS-V5-M10
parent_wp: AOS-V5-M10-P3-COCKPIT
track: STANDARD                 # all CK are STANDARD-style ladders (CK-1/CK-9 add LOD300)
effort: NORMAL                  # LOW | NORMAL | HI (validate_aos.sh Check 44 — REQUIRED)
lod_target: LOD400
lod_status: DRAFT
status: DRAFT
author: team_100
date: "2026-07-01"
version: v1.0.0
supersedes: null
builder_team: team_110          # sequenced P3 build
validator_teams:
  governance: team_90           # governance facet of L-gates
  functional: team_50           # functional facet at BUILD + dual VALIDATE
consuming_team: team_110
cross_engine_required: true
validation_tiering:             # ADR053 — team_00 override: single-engine Cursor (§0.1)
  L-GATE_SPEC:
    tier: 2
    cross_engine: true
    engines: [composer-2.5]     # Cursor only (team_00 ruling 2026-07-01); NOT gpt-5.2-codex
    team_00_override: "dual (Cursor+ChatGPT) → single Cursor; still IR#1 Tier-2 (non-Claude)"
  L-GATE_VALIDATE:
    tier: 2
    cross_engine: true
    dual: true                  # team_90 governance ∥ team_50 functional at BUILD-time (team_110's job)
gate_path: [LOD_CHECK, SPEC, BUILD, VALIDATE, CLOSE]
cost_cap:
  tokens_est: <per-CK>
  human_time_ceiling_hours: <per-CK>
  overrun_policy: "escalate to team_00 (do not silently continue)"
depends_on: [<CK deps>]
blocks: [<CK deps>]
```

**CS citation format (ADR037):** qualified only — ``[agents-os _aos/context/CODE_STANDARDS.md CS-N]``.
Never bare `[CS-N]`. Relevant: CS-2 (FastAPI handlers), CS-4 (core/ui/*.js), CS-5 (shell), CS-6 (lang/drift).

---

## §10 — Authoring order + CK↔delta map (bind here)

`CK-0 → CK-1 ∥ CK-9(contract 200/300) → [foundation review] → CK-2…CK-8 ∥ CK-9(LOD400) → consistency critic → close`

| CK | slug | surface | ladder | backend delta | depends_on |
|---|---|---|---|---|---|
| CK-0 | design-system-foundation | tokens + 15 components | 200→400 | D8 | — |
| CK-1 | canonical-shell-nav | shell + SM-A + degrade banner | 200→300→400 | — | CK-0 |
| CK-2 | map-surface | Map S1 (WP cards, gate-pipe, needs-you + live-sessions rails) | 200→400 | D2 | CK-1, CK-9 |
| CK-3 | wp-workspace | WP S2 (belongs-to banner, gate-history, cost panel) | 200→400 | D2 | CK-1, CK-9 |
| CK-4 | mail-surface | Mail S3 (domain↔domain, all-box monitor, send UI) | 200→400 | D2 (largest) | CK-1, CK-9 |
| CK-5 | funnel-surface | Funnel S4 (idea rows → promote-to-WP) | 200→400 | D2 | CK-1, CK-8, CK-9 |
| CK-6 | help-surface | Help S5 (visual cheat-sheet from CANON_QUICK_HELP_FAQ) | 200→400 | D2 | CK-1, CK-9 |
| CK-7 | settings-surface | Settings S6 (health, team→engine pills, params, modules) | 200→400 | D2 | CK-1, CK-9 |
| CK-8 | modals | M1 +WP create (P9 preview) · M2 dispatch | 200→400 | D6 (contract only) | CK-0, CK-1, CK-9 |
| CK-9 | data-state-layer | SM-B/C/D + engines | 200→300→400 | D1 (phased) · D4 (LWW) · D5 · D7 | CK-0 |

> **CK-8 → CK-9 dependency note.** CK-9 is CK-8's **build-time error-code / write-route contract dependency**:
> CK-8's M1 (WP create) and M2 (dispatch) write modals submit `POST /api/work-packages` · `POST /api/runs`
> and MUST surface CK-9's verbatim write error-code strings (CK-9 §2.4 — e.g. `INVALID_WP_ID_FORMAT` 400,
> `DESCRIPTION_REQUIRED` / "תיאור חובה") + the CK-9 §3.2 write-path sequence (`If-Match` version-guard, D7
> device-key headers). Hence CK-8 `depends_on` includes CK-9 (matches CK-8 `metadata.yaml`).

**Backend delta dispositions (rev B locked):** D1 BUILD-phased (phase-1 = AWAITING_YOU + session-STUCK +
gate-VALIDATE-FAIL only; tier-2 signals → next MS) · D4 LWW-default + manual/blanket/per-domain override
(finer per-domain → next MS) · D6 defer/document · D7 team_00 device-held key (MUST in P3) · D8 font
self-host · D9 route-trim DEFER (separate OPS WP). **Do NOT scope:** D1 tier-2 signals, D4 finer rules,
D6 build, D9, O25 broader auth-model.

### 15 components (CK-0 authors; every surface composes from these — do not invent new primitives)
`Button` · `Field` · `Input` · `Select` · `SelectPill` · `StatusDot` · `StatusBadge` · `TrackTag` ·
`LodBadge` · `GatePipe` · `WpCard` · `SessionRow` · `NeedCard` · `Modal` · `DegradeBanner`.
(Prop contracts: `_aos/v5_characterization/cockpit_design_system_v1.0/design-system/COMPONENT_SOURCE_REFERENCE.md`.)

---

## §11 — Locked principle (carry into every CK)
**"The cockpit REFLECTS the process — it does not manage it."** It reads state, renders it legibly
(via the locked legend/enums), and enables action; humans + sessions manage. Idiot-proof minimalism:
*"remove any element whose meaning survives its removal."* Every UI surface designs all 4 states, not
just the happy path.

---

## §12 — SHELL / SURFACE RECONCILIATION (ratified 2026-07-01 — resolves CK-1 K-1/K-3; binds CK-2 + team_110)

The runnable M8 `cockpit/index.html` shipped a **4-tab** shell (map/funnel/help/settings) with a
**needs/sessions/verdicts** right rail. The **M10 canon (this kernel) SUPERSEDES that** — team_110 must
build the M10 shell, not preserve the M8 one. Ratified canon:

1. **Segmented tabs (5):** `🗺️map · 🌳tree · ✉️mail · 💡funnel · ❓help`. `⚙️settings` is a **chrome gear,
   NOT a segmented tab**. `+חבילה חדשה` is a CTA. `WP_WORKSPACE` is **not a tab** — it is entered by
   opening a WP from the map/tree.
2. **Surface ↔ CK mapping:** `map`+`tree` are two views **owned by CK-2 (Map surface)** (map = WP cards;
   tree = hierarchical spine); `mail`→CK-4; `funnel`→CK-5; `help`→CK-6; `settings`(gear)→CK-7;
   `WP_WORKSPACE`→CK-3; the two modals→CK-8; data/state→CK-9.
3. **Right rail = the tree, always** ("you are here" path highlight), per CK-1. The M8 rail's
   **needs-you / live-sessions / verdicts feeds RE-HOME into the CK-2 Map surface content** (not the
   right rail). CK-2 owns rendering those feeds (they consume CK-9 D1 + `session_state_changed` +
   `verdict_received`).
4. **Left panel:** resizable detail/actions, clamp **280–560px, default 360px** (CK-1 concrete choice;
   grounded on `--aside-w` 312). buttons inline-end.

---

## §13 — BACKEND CATALOGUE COMPLETION (grounded during fan-out, 2026-07-01 — supersedes §3 generic entries)

The fan-out specs grounded against the REAL backend and surfaced routes/codes/enums the §3 catalogue
listed generically or omitted. These are the authoritative bindings (all verified present in `core/`):

**Additional REAL REST routes (exist; add to the §3 catalogue):**
- Mail (`dashboard_routes.py`): `GET /api/messaging/v2/inbox` (`?team=` single; `?scope=all` all-box monitor,
  **team_00/team_100 only** → `FORBIDDEN_SCOPE`) · `GET /api/messaging/log?project_id` (x-ndjson domain log) ·
  `GET /api/messaging/v2/verdicts` · `POST /api/messaging/v2/send` (server binds `origin_team=actor`) ·
  `POST /api/messaging/v2/{read|ack|archive}` (recipient-only → `NOT_RECIPIENT`).
- History: **`GET /api/history?run_id=`** (top-level — NOT nested `/runs/{id}/history`; corrects §3.1).
- Settings: `GET /api/server/wan-status` · `GET /api/governance/status` · `GET /api/modules` ·
  `GET /api/modules/status` · `POST /api/modules/{id}/activate|deactivate` (**L-GATE_BUILD delegated
  authority**, not team_00-only — mixed authority model).
- Ideas: `PUT /api/ideas/{id}` is the groom/triage write (partial via `exclude_unset`) — the CA1 `PATCH`
  reference is superseded.

**Additional REAL error `code` strings (exist; append to §3 list):**
`INSUFFICIENT_AUTHORITY` (403 — EVERY team_00-gated write) · `ACTOR_KEY_NOT_CONFIGURED` (401) ·
`DESCRIPTION_REQUIRED` (422 — the M1 "תיאור חובה" real code) · `READ_ONLY_WP` · `ACTOR_MISMATCH` ·
`FORBIDDEN_SCOPE` · `NOT_RECIPIENT` · `VALIDATION_ERROR` (e.g. `{field: lod_target}`) ·
ideas: `IDEA_TITLE_REQUIRED` · `INVALID_ACTION` · `INVALID_IDEA_TYPE` · `IDEA_NOT_FOUND` ·
`INVALID_STATE` · `DB_UNAVAILABLE` (503).

**Enums the surfaces bind (CK-5 owns/registers in CANON; D3 assert is generic `list_enums('idea_status')`):**
- idea/funnel status: `NEW · EVALUATING · APPROVED · DEFERRED · REJECTED` (backend also stamps `promoted`
  on promote). priority: `CRITICAL · HIGH · MEDIUM · LOW` (visual tiers: CRITICAL+HIGH→דחוף · MEDIUM→בינוני
  · LOW→נמוך; CRITICAL-distinct-chip = BUILD punch-list). idea_type: `BUG · FEATURE · IMPROVEMENT ·
  TECH_DEBT · RESEARCH`.

**Status-dot ↔ badge convention (resolves CK-2 K-2-2; CK-3 binds identically):** `AWAITING_YOU` renders
`StatusDot dot='wait'` (orange) + `StatusBadge status='awaiting_you'` (purple). The "needs a human" purple
is carried by the **badge + the NeedCard feed**, NOT by a dedicated purple dot (the 5-role dot legend has
no purple). Do not add a purple dot without updating CK-2 §4.2 + CK-3.

**M1/M2 create-contract clarifications (refine §8):**
- **M1 id is server-VALIDATED, not server-MINTED** (today): `POST /api/work-packages` accepts a
  client-supplied `work_package_id` and validates format (`is_v5_canon`/`V5_CANON_RE`); there is no
  running-`WP{n}` mint. Preview is regex-identical either way; offline shows `WP?` for the number.
  `WorkPackageCreateBody` also **requires `lod_target`** (modal defaults e.g. `LOD200`).
- **M2 `POST /api/runs` `CreateRunBody` accepts ONLY** `work_package_id · domain_id · process_variant`
  today. The richer M2 fields (`role/task · engine(+override) · token_budget · mode`) are a **PENDING
  backend delta** — specified-but-unbuildable until team_110 extends `CreateRunBody` (or adds a mandate
  dispatch endpoint). IR#1 (`IR1_SAME_ENGINE` 403) fires at `/runs/{id}/advance` (decisive), not at create.

**→ Consolidated team_110 backend-delta punch list lives in the COMPLETION_REPORT (not built this MS).**

---

*— team_100 · 2026-07-01 · frozen anti-drift kernel for AOS-V5-M10 P3 cockpit LOD400 authoring
(rev in-place: §0.4 loop-policy · §3 real error-codes · §4 nine SSE events · §7 canonical reconcile copy ·
§12 shell/surface reconciliation · §13 backend catalogue completion from fan-out grounding)*
