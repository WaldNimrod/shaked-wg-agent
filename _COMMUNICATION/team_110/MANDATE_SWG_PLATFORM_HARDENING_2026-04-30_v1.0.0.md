---
id: MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0
type: ORCHESTRATION_MANDATE
from: team_100 (shaked-wg-agent spoke — orchestrator-of-record for this mandate set)
to: team_110 (Domain Architect — orchestrator-executor for the M1–M5 pipeline)
routed_by: team_00 (Owner — Nimrod)
date: 2026-04-30
status: OPEN
priority: P1_URGENT
expects_response: true
sla_hours: 72
spoke_profile: L0
project_window_constraint: 2026-06-08 (Shaked active search window)
related_program: S005-P002 (PROPOSED — "Cross-profile platform hardening — Shaked field-evidence driven")
canonical_pattern_reference:
  doc: /Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/_COMMUNICATION/team_100/REPORT_TO_AOS_TEAM_100_SUB_AGENT_PIPELINE_PATTERN_2026-04-29_v1.0.0.md
  status: AWAITING_HUB_CANONIZATION (TikTrack team_100 → AOS hub team_100)
  reason_to_use_pre_canonization: "Hub canonization pending; TikTrack S005-P006-WP001/WP002 already proved the pattern in production. Owner explicitly authorized use here."
field_evidence:
  - "_COMMUNICATION/team_100/SHAKED_FIELD_EVIDENCE_2026-04-30.md (this session — fresh scan run-20260429-213722-f1bd surfaced 5 critical platform gaps while serving Shaked live)"
---

# MANDATE — Shaked-WG Platform Hardening (M1–M5)

## §0 — TL;DR

Owner needs **2 parallel tracks** (per session 2026-04-30):
1. **Live-search track** (handled by team_100 in current session — DONE: 5 outreach picks delivered to Shaked).
2. **System-improvement track** (THIS MANDATE): execute **M1–M5** end-to-end as an orchestrated sub-agent pipeline, deliver to L-GATE_VALIDATE_INTERNAL passing, then **PAUSE** for cross-vendor external validation per Iron Rule #1.

Five field-evidence items must be addressed before next live-search round to make Shaked's outreach effective:

| ID | Title | Type | Blocker? |
|---|---|---|---|
| **M1** | Profile schema — `age`, `occupation_status`, `studies_*`, `move_in_optimal` | feature + scoring | gates ranking quality |
| **M2** | Full-description extraction in flatfox + wgzimmer scrapers | data-pipeline | **blocks M1, M5** |
| **M3** | wgzimmer scraper recovery (returns 0; main WG source dead) | bug-fix | halves inventory |
| **M4** | Outreach lifecycle tracking (`contacted`, `replied`, `viewed`, `rejected`) | feature | blocks 2nd-round dedup |
| **M5** | Negative-signal autofilter (`women_only`, `Wochenaufenthalter`, `Zwischenmiete<6mo`) | scoring + filter | depends on M2 |

**Authority model:** team_110 acts as **orchestrator** (not implementer). team_110 dispatches **sonnet sub-agents** for builds and **haiku sub-agents** for internal validation per the canonical pipeline pattern. team_110 keeps its own context lean by reading only orchestrator-level state.

---

## §1 — Authority and engine matrix

Per canonical TikTrack pattern §1, applied here:

| Tier | Role | Engine | Owner |
|---|---|---|---|
| **Orchestrator** | Dispatches, tracks, commits, files closure | claude-opus / claude-sonnet | **team_110** (this mandate) |
| **Builder sub-agents** | Author LOD200/400, write code, write tests | claude-sonnet-4-6 | dispatched by team_110 |
| **Internal validator sub-agents** | L-GATE_*_INTERNAL R1+ (preliminary, fast filter) | claude-haiku-4-5 | dispatched by team_110 |
| **External validator** | L-GATE_VALIDATE_EXTERNAL R1 (canonical, cross-vendor) | non-Anthropic (Cursor/GPT-5.x/Codex) | routed back to **team_00** for human dispatch |

**Iron Rule #1 satisfaction:** sonnet (builder) ≠ haiku (internal validator). Cross-vendor external validator remains the canonical authority for L-GATE_VALIDATE closure.

---

## §2 — WP decomposition and dependency graph

Each M-item is a Work Package with its own LOD200 → LOD400 → BUILD → 3 gates. team_110 must register each WP in `_aos/roadmap.yaml` (pre-flight, see §6).

```
                        ┌──────────────────────────┐
                        │  M2 (full-description)   │  ← MUST be first; blocks M1, M5
                        │  WP-ID: SWG-PLAT-M2      │
                        └──────────┬───────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
┌──────────────┐          ┌──────────────────┐       ┌──────────────────┐
│ M1 (profile  │          │ M3 (wgzimmer fix)│       │  PARALLEL OK:    │
│ + age)       │          │ INDEPENDENT —    │       │  M3 may run      │
│ WP: SWG-     │          │ may parallelize  │       │  alongside M2/M1 │
│ PLAT-M1      │          │ WP: SWG-PLAT-M3  │       └──────────────────┘
└──────┬───────┘          └──────────────────┘
       │
       ▼
┌──────────────┐
│ M4 (outreach │  depends on M1 schema (status enum extension)
│ lifecycle)   │
│ WP: SWG-     │
│ PLAT-M4      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ M5 (negative │  depends on M2 (full text) + M1 (profile shape)
│ filters)     │
│ WP: SWG-     │
│ PLAT-M5      │
└──────────────┘
```

**Parallelization plan:**
- **Wave 1 (parallel):** M2 + M3 sub-agents dispatched simultaneously (independent code areas).
- **Wave 2 (after M2 PASS):** M1 sub-agent.
- **Wave 3 (after M1 PASS):** M4 + M5 sub-agents in parallel.

This gives team_110 **3 sequential dispatch waves** instead of 5 — minimizing orchestrator context burn.

---

## §3 — Per-WP scope (executable detail)

### M1 — Profile schema: age + studies + move_in_optimal

**Files in scope:**
- `data/profiles/default.json`, `data/profiles/dror.json`, `data/profiles/pardes-hanna.json` (migration)
- `shaked_wg_agent/config.py` (Pydantic profile model)
- `shaked_wg_agent/scorer.py` (weights + bonuses)
- `tests/test_config.py`, `tests/test_scorer.py` (extend)

**New profile fields:**
- `age: int | null` (16–99 when set; null = legacy/disabled)
- `occupation_status: Literal["student","working","mixed"] | null`
- `studies_field: str | null`
- `studies_institution: str | null`
- `studies_start: str | null` (YYYY-MM)
- `move_in_optimal: str | null` (YYYY-MM-DD; preferred date inside `move_in_from..move_in_until`)

**Default profile migration values:**
```json
{
  "age": 18,
  "occupation_status": "student",
  "studies_field": "chemistry (planned)",
  "studies_institution": "Universität Basel",
  "studies_start": "2026-09",
  "move_in_optimal": "2026-06-01"
}
```
`dror.json` and `pardes-hanna.json`: leave new fields `null` (not applicable).

**Scorer additions (weights configurable in `config.py`, not hardcoded):**
- +30 if `profile.age ∈ [listing.roommate_age_min, listing.roommate_age_max]`
- +20 if `profile.occupation_status == "student"` AND `listing.is_student_oriented`
- +30 if `listing.available_from == profile.move_in_optimal` (NEW — addresses owner field-evidence: "אופטימאלי 1.6.26")
- HARD EXCLUDE (score = -1, omit from digest) when:
  - `listing.gender_restriction != "none"` and not matching profile
  - `profile.age < listing.roommate_age_min` OR `profile.age > listing.roommate_age_max`
  - `listing.tenant_type_restriction == "wochenaufenthalter_only"` and profile is permanent

**Acceptance criteria (numbered, testable):**
1. `pytest tests/test_config.py::test_profile_age_field` PASS for new field load + validation.
2. `pytest tests/test_scorer.py::test_age_match_bonus` PASS.
3. `pytest tests/test_scorer.py::test_move_in_optimal_bonus` PASS.
4. `pytest tests/test_scorer.py::test_hard_exclude_age_range` PASS.
5. Loading `default.json` produces a Profile object with `age=18`, `occupation_status="student"`.
6. Loading `dror.json` produces a Profile object with `age=null` and scorer skips age-based logic without error.
7. Re-running `python -m shaked_wg_agent run --profile default` against current `data/listings.json` produces a top-5 ranking that demonstrably differs from pre-M1 ranking (capture before/after in WP closure).
8. ruff clean. mypy/pyright (if configured) clean.

### M2 — Full-description extraction (UNBLOCKER)

**Problem:** `data/listings.json` summary field is truncated at ~200 chars. All age/student/vegan/restriction signals live in the body text. Without M2, M1 and M5 extractors fail at recall.

**Files in scope:**
- `shaked_wg_agent/scrapers/flatfox.py` (REST/HTML — extend body extraction)
- `shaked_wg_agent/scrapers/wgzimmer_pw.py` (Playwright — extend body extraction; **NOTE:** also a candidate for M3 fix)
- `shaked_wg_agent/scrapers/base.py` (`ScrapedListing` dataclass — add `full_description: str` field)
- `data/listings.json` (data migration — `full_description` field defaults to existing `summary` for legacy rows)
- `tests/test_scrapers/*` (new — fixture-driven tests)

**Acceptance criteria:**
1. Scraped listing dataclass exposes `full_description: str` (≥500 chars when source provides it; falls back to summary if not).
2. New flatfox listings stored with `full_description` length > existing `summary` length on at least 80% of fixture set.
3. Migration: legacy listings get `full_description = summary` (no data loss).
4. ≥10 fixture HTMLs in `tests/fixtures/scrapers/` (real anonymized snapshots).
5. ruff + pytest clean.

### M3 — wgzimmer scraper recovery

**Problem:** `wgzimmer_pw.py` returns 0 listings on the last 2 runs (run-20260429-213722-f1bd, prior run). Field evidence: 0/50 results from this source. wgzimmer.ch is described in `data/sources.json` as "Hauptquelle".

**Files in scope:**
- `shaked_wg_agent/scrapers/wgzimmer_pw.py`
- `shaked_wg_agent/scrapers/wgzimmer.py` (legacy non-PW — assess deprecation)
- `tests/test_scrapers/test_wgzimmer.py` (new or extend)

**Acceptance criteria:**
1. Manual canonical URL probe documented in WP closure: HTTP status, page structure (DOM diff vs. expected).
2. If selector drift: update selectors with regression-resistant strategy (data-test-id where available, multiple fallbacks).
3. If anti-bot escalation: document the failure mode and propose a non-evasive workaround (e.g., reduced cadence, login/account, or escalate to team_50 for source-strategy review).
4. Live test against wgzimmer.ch Basel canton URL returns ≥1 listing OR a documented "source-side outage" verdict.
5. ruff + pytest clean.

### M4 — Outreach lifecycle tracking

**Problem:** Listings stay `status="neu"` forever. No tracking of contacted / replied / viewed / rejected. Next-round dedup is impossible.

**Files in scope:**
- `shaked_wg_agent/repositories/listings_repo.py` (or equivalent — add status mutation API)
- `shaked_wg_agent/__main__.py` (add CLI subcommands: `mark-contacted`, `mark-replied`, `mark-rejected`, `mark-viewed`)
- `data/listings.json` schema: extend `status` enum + add `contacted_at`, `reply_received_at`, `rejection_reason`, `outreach_notes`
- `shaked_wg_agent/publisher/html_report.py` (badge/column for status)
- `tests/test_outreach_lifecycle.py` (new)

**Acceptance criteria:**
1. CLI: `python -m shaked_wg_agent mark-contacted <listing_id> --note "sent via flatfox 13:42"` updates status atomically.
2. CLI: `python -m shaked_wg_agent mark-replied <listing_id> --positive` records reply.
3. Re-running scan does NOT reset a contacted listing to `neu`.
4. HTML report renders distinct visual treatment for each status.
5. Top-5 generation excludes listings already in `rejected` / `replied_negative` states.
6. ruff + pytest clean.

### M5 — Negative-signal autofilter

**Problem:** orchestrator (team_100) currently performs negative-signal filtering **manually** every live-search round. Not scalable.

**Files in scope:**
- `shaked_wg_agent/extractors/negative_signals.py` (new)
- `shaked_wg_agent/scorer.py` (integrate)
- `tests/test_negative_signals.py` (new — ≥15 cases drawn from real entries)

**Patterns to extract (DE / EN / IT / FR):**
- Gender: `women only`, `nur frauen`, `frauen-WG`, `female only`, `male only`, `nur männer`
- Tenant type: `Wochenaufenthalter`, `Geschäftsleute`, `business only`
- Duration: `Zwischenmiete < 6 Monate`, `nur befristet`, `temporary stay`
- Religion preference: `Christian preferably` (advisory, not exclude — score penalty)

**Acceptance criteria:**
1. Recall ≥90% on hand-labeled set of 20 real listings from current `data/listings.json` (use the 105 we have).
2. Precision ≥95% on same set (low false-positive priority — better to miss-flag than mis-exclude).
3. Integration with M1 scorer: hard-exclude when restriction conflicts with profile.
4. ruff + pytest clean.

---

## §4 — Pipeline phases and gate checkpoints (per WP)

For **each** of M1–M5, team_110 follows the canonical pipeline:

```
Phase 1: PRE-FLIGHT          (orchestrator, deterministic checklist — see §6)
Phase 2: LOD200 architecture (sonnet sub-agent)
Phase 3: LOD400 exec spec    (sonnet sub-agent — split if >32K tokens, see §7)
Phase 4: L-GATE_SPEC R1      (haiku sub-agent — internal preliminary)
Phase 5: BUILD               (sonnet sub-agent — split A/B if needed)
Phase 6: L-GATE_BUILD R1     (haiku sub-agent — internal preliminary)
Phase 7: L-GATE_VALIDATE R1  (haiku sub-agent — internal preliminary, holistic)
Phase 8: PAUSE → team_00     (route to external validator — Iron Rule #1 canonical closure)
```

After Phase 7 INTERNAL passes for ALL of M1–M5, team_110 **stops**, files a single bundle handoff to team_00, and Owner routes to external validator (Cursor / GPT-5 / Codex) for L-GATE_VALIDATE_EXTERNAL R1.

**Verdict files** land in `_COMMUNICATION/team_190/` per existing convention. Internal verdicts use suffix `_R1_INTERNAL`; external verdicts use `_R1_EXTERNAL`.

---

## §5 — Sub-agent dispatch — standard prompt template

team_110 uses this template per dispatch (paraphrase, do not deviate from structure):

```
You are a {sonnet|haiku} sub-agent dispatched by team_110 (orchestrator) on the
shaked-wg-agent AOS spoke. Profile L0. Mandate:
MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0.

Your scope is exactly Phase {N} ({phase_name}) for WP {SWG-PLAT-MX}.
Read first:
  - This mandate (above)
  - _aos/governance/team_110.md
  - {prior phase artifact if any}
  - {scope-specific source files listed in §3}

Hard constraints:
  - Do NOT touch _aos/. (Iron Rule #11)
  - Do NOT modify other WPs' files.
  - Do NOT commit (orchestrator commits — see §8 R-8).
  - Do NOT make policy decisions. If ambiguous → file
    _COMMUNICATION/team_110/CLARIFICATION_<WP>_<topic>.md and STOP.
  - ruff + pytest must pass before you return.

Deliverables:
  {phase-specific list}

Return format:
  - File paths created/modified
  - Test results summary
  - Any deviations from the mandate, with justification
  - DONE / PARTIAL / BLOCKED disposition
```

**Validator (haiku) prompt extension** — each gate has a deterministic VC checklist. Validator MUST execute each check (file exists? grep matches? command returns 0?), not just "stamp PASS". This addresses canonical-pattern §4 C-1 (rigor inconsistency).

---

## §6 — Pre-flight checklist (before EVERY sub-agent dispatch)

Adapted from canonical pattern §5 R-2. team_110 runs this deterministically:

1. WP registered in `_aos/roadmap.yaml` with `status`, `lod_status`, `current_lean_gate`, `spec_ref` ✓
   (For M1–M5: register under `S005-P002` program — propose to team_00 via brief artifact if program doesn't exist; do NOT edit `_aos/roadmap.yaml` directly — file a registration request to team_100 via `_COMMUNICATION/team_110/ROADMAP_REGISTRATION_REQUEST_S005-P002_v1.0.0.md` and proceed only after confirmation.)
2. DB connectivity probe: `cat /Users/nimrod/Documents/agents-os/_aos/db_connectivity_status.json` ✓
   - If `status: online` → API-only mutations (Iron Rule #7).
   - If `status: offline` → STOP and report to team_00 per ADR034 R8.
3. `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL ✓
4. Required env vars present (don't print values) ✓
5. Sibling-WP dependencies satisfied per §2 dependency graph ✓
6. No uncommitted changes in scope-overlapping files (check with `git status`) ✓

If ANY check fails: do NOT dispatch. File a BLOCKED artifact and route to team_00.

---

## §7 — Token-budget split protocol

If a sonnet sub-agent for LOD400 or BUILD is at risk of >32K tokens output:
- Pre-emptive split signal: if LOD300 or sibling spec >1500 lines → split.
- Sub-agent self-detection: instruct in dispatch prompt to emit `<<SPLIT_REQUIRED reason="approaching budget">>` and stop, rather than silently truncate.
- Split convention: **Part A = backend/data**, **Part B = frontend/UI/tests**.
- For these WPs: most should fit in single sonnet pass. M2 BUILD may split (scrapers + tests). Monitor.

---

## §8 — Bookkeeping (orchestrator-only)

Per canonical pattern §5 R-8, sub-agents author files but do NOT commit. team_110 commits per WP with messages:

- `spec(SWG-PLAT-Mx): LOD200 architecture` (after Phase 2 returns)
- `spec(SWG-PLAT-Mx): LOD400 executable spec` (after Phase 3 returns)
- `validate(SWG-PLAT-Mx): L-GATE_SPEC R1 internal PASS|BLOCKED` (after Phase 4 returns)
- `feat(SWG-PLAT-Mx): build` (after Phase 5 returns)
- `validate(SWG-PLAT-Mx): L-GATE_BUILD R1 internal PASS|BLOCKED` (after Phase 6)
- `validate(SWG-PLAT-Mx): L-GATE_VALIDATE R1 internal PASS|BLOCKED` (after Phase 7)

team_110 also maintains:
- `_COMMUNICATION/team_110/SWG-PLAT-Mx/PIPELINE_LOG_v1.0.0.md` — running log of every dispatch, return, verdict.
- `_COMMUNICATION/team_110/SWG-PLAT-PIPELINE_DASHBOARD_v1.0.0.md` — single-page status across all 5 WPs.

---

## §9 — Definition of Done (this mandate, end-to-end)

team_110 returns DONE to team_00 only when ALL of these hold:

- [ ] All 5 WPs (SWG-PLAT-M1..M5) registered in `_aos/roadmap.yaml`
- [ ] All 5 WPs have LOD200 + LOD400 specs filed
- [ ] All 5 WPs have BUILD complete with code merged to main (single-writer rule respected)
- [ ] All 5 WPs have L-GATE_SPEC_R1_INTERNAL = PASS
- [ ] All 5 WPs have L-GATE_BUILD_R1_INTERNAL = PASS
- [ ] All 5 WPs have L-GATE_VALIDATE_R1_INTERNAL = PASS
- [ ] `pytest` 100% pass on full test suite
- [ ] `ruff check .` clean
- [ ] `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL
- [ ] Single bundle handoff filed at `_COMMUNICATION/team_110/HANDOFF_SWG_PLAT_BUNDLE_TO_TEAM_00_v1.0.0.md` containing:
  - Per-WP summary (files changed, test counts, verdict refs)
  - Activation prompts ready to paste for external Cursor/GPT-5/Codex sessions (one per WP)
  - Before/after demonstration: re-rank top-5 for `default` profile, show how field evidence (Shaked age=18, student) changes the ordering
  - Open questions / advisories for external validator

team_110 does NOT proceed beyond Phase 7 to external validation. That is team_00's call.

---

## §10 — Out of scope (do NOT do these)

- Editing `_aos/governance/`, `_aos/lean-kit/`, `_aos/project_identity.yaml` (Iron Rules #11, #12).
- Editing `_aos/roadmap.yaml` directly — must request via team_100 (this spoke's team_100 = current orchestrator-of-record).
- **NOTE — `_aos/work_packages/` IS in scope** for team_110 writes under this mandate per AOS_DIRECTORY_CANON Part 5 (team_110 row: `W (mandated)`). Earlier draft said otherwise — corrected per MSG-HUB-20260429-003-RESPONSE.
- Source coverage expansion (ronorp / students.ch / Uni Basel housing board) — explicitly deferred per team_100 assessment.
- Multi-channel notifications — already in S002 platform, not needed for L0 spoke.
- `vegan_signal` extractor improvement — implicitly covered by M2 (full description) + M5 patterns; no separate WP.
- Touching `dror` or `pardes-hanna` profile logic beyond null-default migration in M1.

---

## §11 — Required deliverables (artifacts team_110 produces)

1. **Roadmap registration request** — `_COMMUNICATION/team_110/ROADMAP_REGISTRATION_REQUEST_S005-P002_v1.0.0.md` (FIRST — pre-flight gate)
2. **5 LOD200 specs** — `_aos/work_packages/SWG-PLAT-Mx/LOD200_spec.md` (one per WP). Path is **canonical (Option A)** per AOS_DIRECTORY_CANON Part 5 + LOD_STANDARD §Lean.2 (ruling MSG-HUB-20260429-003-RESPONSE, 2026-04-30: team_110 has W-mandated authority on `_aos/work_packages/`). The local CLAUDE.md `_aos/`-write restriction is a defect being corrected via hub propagation; team_110 may proceed under this mandate without waiting for the propagation to land.
3. **5 LOD400 specs** — same path convention: `_aos/work_packages/SWG-PLAT-Mx/LOD400_spec.md`.
4. **15 verdict files** — 3 internal gates × 5 WPs (`_COMMUNICATION/team_190/VERDICT_SWG-PLAT-Mx_<gate>_R1_INTERNAL_v1.0.0.md`)
5. **5 PIPELINE_LOG files** — one per WP
6. **1 PIPELINE_DASHBOARD** — cross-WP status
7. **1 BUNDLE_HANDOFF** — final
8. **Code changes** — production code under `shaked_wg_agent/`, tests under `tests/`, data migrations applied to `data/`

---

## §12 — Open questions team_110 may face (pre-answered where possible)

| Q | Answer |
|---|---|
| L0 spoke — is full LOD200/300/400 chain required, or can we skip LOD300? | **L0 → LOD200 + LOD400 sufficient** (skip LOD300). External L-GATE_VALIDATE_EXTERNAL still required for cross-engine canonical closure. |
| Where do LOD specs live on L0 spoke? | `_aos/work_packages/<WP_ID>/LOD{200,400}_spec.md` — canonical per AOS_DIRECTORY_CANON Part 5 (team_110 W-mandated). Ruling MSG-HUB-20260429-003-RESPONSE, 2026-04-30. |
| What's `S005-P002`? It doesn't exist in roadmap. | **PROPOSED — file ROADMAP_REGISTRATION_REQUEST first.** team_100 will create the program before team_110 dispatches. |
| Can sonnet sub-agents work in worktrees to parallelize? | **Yes — recommended** for Wave-1 (M2 + M3 in parallel) and Wave-3 (M4 + M5 in parallel). See canonical pattern §5 R-9. |
| Is haiku internal verdict canonical? | **No — preliminary only.** Canonical authority remains external cross-vendor. |
| What if a sub-agent emits SPLIT_REQUIRED? | Re-dispatch as Part A + Part B per §7. Don't attempt to merge — keep parts atomic. |

---

## §13 — Authority chain

- **team_00 (Owner — Nimrod)** — supreme decision authority; routes external L-GATE_VALIDATE_EXTERNAL.
- **team_100 (this spoke, current session)** — orchestrator-of-record for THIS mandate; receives RESPONSE_* from team_110.
- **team_110 (Domain Architect)** — executes the M1–M5 pipeline as orchestrator + sub-agent dispatcher.
- **team_190 (Validator)** — receives external verdicts, files final closure when team_00 returns external pass.

team_110 escalates back to team_100 (via `_COMMUNICATION/team_110/CLARIFICATION_*.md`) on:
- Policy decisions (e.g., gender-restriction filtering semantics)
- Architectural ambiguity in any LOD200
- Cross-WP scope conflicts
- DB-online violations (Iron Rule #7) it cannot resolve

team_110 does NOT escalate for:
- Token-budget splits (handle per §7)
- Test failures (fix and re-dispatch)
- Lint failures (fix in same dispatch)

---

## §14 — Activation prompt for team_110 (paste into team_110 Cursor session)

```
You are team_110 (Domain Architect — orchestrator) on the AOS spoke
shaked-wg-agent. Profile L0. Working directory:
/Users/nimrod/Documents/shaked-wg-agent.

Mandate: MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0
Path: _COMMUNICATION/team_110/MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0.md

Read the full mandate first. Your role is ORCHESTRATOR — you do NOT
implement code yourself. You dispatch sonnet sub-agents for builds
and haiku sub-agents for internal validation, per the canonical
sub-agent pipeline pattern (TikTrack 2026-04-29, awaiting hub canon).

Execution order:
  1. Run pre-flight checklist (§6) — STOP if any check fails.
  2. File ROADMAP_REGISTRATION_REQUEST_S005-P002 to team_100, wait for confirmation.
  3. Dispatch Wave 1 (M2 + M3 in parallel — independent worktrees).
  4. After Wave 1 Phase 7 PASS for both: Wave 2 (M1).
  5. After Wave 2 Phase 7 PASS: Wave 3 (M4 + M5 in parallel).
  6. File BUNDLE_HANDOFF to team_00.

Hard constraints:
  - Do NOT edit _aos/ directly (Iron Rule #11/#12).
  - Do NOT commit from sub-agents (you commit per §8).
  - Do NOT proceed past Phase 7 (internal validation) — pause for team_00 external routing.
  - ALL structured mutations through repository patterns (Iron Rule #7 if DB online).
  - Sub-agent prompts MUST follow §5 template.
  - Pre-flight before EVERY dispatch — no exceptions.

When DONE per §9, file:
_COMMUNICATION/team_110/HANDOFF_SWG_PLAT_BUNDLE_TO_TEAM_00_v1.0.0.md

Report progress incrementally to PIPELINE_DASHBOARD so team_100 and
team_00 can monitor without inspecting your full context.
```

---

## §15 — Routing and acknowledgement

**Routed by:** team_100 (this spoke session, 2026-04-30) on behalf of team_00 (Owner).
**Expected response:** team_110 acknowledges receipt within 24h via:
`_COMMUNICATION/team_110/ACK_MANDATE_SWG_PLATFORM_HARDENING_v1.0.0.md`
containing:
- Pre-flight checklist results
- Wave-1 dispatch plan (sub-agent prompts as deliverables)
- Estimated wall-clock to BUNDLE_HANDOFF (per canonical-pattern empirical: ~30–60min/WP × 5 = 2.5–5h orchestrator time)

**END OF MANDATE v1.0.0**
