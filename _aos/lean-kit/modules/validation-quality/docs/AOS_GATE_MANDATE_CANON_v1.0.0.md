---
id: AOS_GATE_MANDATE_CANON
version: v1.4.1
status: LOCKED
date: '2026-04-17'
amended: '2026-04-19'
amendment_note: >-
  v1.0.1 — Mandatory numbered WP options; default WP row first in Table A;
  explicit default-gate line before Table B.
  v1.0.2 — Phase 3.5: verify remediation before resubmission mandate / re-validation request.
  v1.0.3 — Phase -1: Session Context Check added before Phase 0. Phase 0.5/Phase 1 gated behind explicit user WP confirmation.
  v1.1.0 — Phase -1 expanded to three-signal model (Signal A: within-WP next gate; Signal B: WP-complete next WP; Signal C: resubmit to same validator). Phase 0 DB-first data access. Manual override branch made explicit.
  v1.2.0 — Phase -1: Signal D added (spec-authored trigger). DEFAULT_WP computation: extended active-status set (IN_PROGRESS|IN_VALIDATION|READY_FOR_SPEC_REVIEW|READY_FOR_BUILD). Phase 1: enhancement WP L-GATE_ELIGIBILITY auto-waiver. Phase 4: context level default applied from hint (no mandatory stop). Phase 0.5: dependency activation-condition cross-check warning.
  v1.3.0 — Signal B split into B.0 (Team 191 archive mandate — mandatory before next WP) + B-next (next WP routing). "WP closure" definition added. LOD500_LOCKED defined as requiring Team 191 archive completion, not just Team 190 verdict.
  v1.4.0 — Phase 5: mandatory §8 Post-Mandate Routing block added to every mandate (PASS/FAIL/BLOCK deterministic next-step table with exact /AOS_gate-mandate invocation). Gate alias terminology locked: full canonical gate names only in all human-facing text; single-letter alias forms (defined in pre_gate_ordering.yaml) are machine-script-only and must not appear in documentation.
  v1.4.1 — Phase 4: session-continuity override added. When the resubmission target is the same team that issued the prior rejection and that session is still active (same window, in-chat routing, no cold-start), apply [1] MINIMAL regardless of round number.
authority: Team 00 (principal) + Team 100 (chief architect)
scope: >-
  Binding for all AOS methodology deployments: agents-os hub, spoke projects (all domains),
  profiles L0/L2/L2.5/L3, Cursor, Claude Code, Codex, and CLI agents. Propagate with physical
  lean-kit copies — no symlinked SSoT.
path_repo_root_lean_kit: lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md
path_aos_lean_kit_mirror: _aos/lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md
claude_command_stub: .claude/commands/AOS_gate-mandate.md
---

# Canonical — `/AOS_gate-mandate` (all environments)

**Single source of truth.** Edit **this file** for policy; then update the Claude stub (pointer only), `.cursorrules`, and `SYSTEM_PROMPT.template` one-liners if paths change. Spoke repos consume the same document under `_aos/lean-kit/...` when lean-kit is physically copied.

> **Reference WP:** AOS-V314-WP-CANONICAL-GATES  
> **Purpose:** Standardize mandate creation for all gate types across all tracks.  
> **Design Principle:** Dynamic team-engine mapping — NEVER hardcode engines. Read from `team_assignments.yaml` / `definition.yaml` (hub: `core/definition.yaml`) at invocation time.

---

## Invocation (arguments optional)

| Form | Behavior |
|------|----------|
| `/AOS_gate-mandate` | Use **Computed defaults** (below). **Do not** ask the user to guess WP/gate. |
| `/AOS_gate-mandate <wp-id>` | Fix WP; default **gate** = that WP’s `current_lean_gate` from `_aos/roadmap.yaml`. |
| `/AOS_gate-mandate <wp-id> <gate-type>` | Fully explicit override. |

**`<gate-type>` tokens:** `L-GATE_ELIGIBILITY`, `L-GATE_CONCEPT`, `L-GATE_SPEC`, `L-GATE_BUILD`, `L-GATE_VALIDATE`, `EXT-CP1`, `EXT-CP2`, `GATE_0` … `GATE_5` (see `lean-kit/modules/validation-quality/GATE_REGISTRY.md` for track-specific validity).

---

## Defaults & option menus (mandatory — Cursor, Claude Code, Codex, CLI)

**Rule:** The agent **never** proceeds to Phase 0 (resolve context) without first emitting **Table A**, **Table B**, and the **numbered WP options** (below). The user must **see** explicit choices; defaults must be **labeled**, not implied.

**Presentation (v1.0.1 — binding):**

1. **Numbered options — always:** Immediately after Table A, emit a **numbered list** of every `IN_PROGRESS` WP. **Option 1** MUST be the computed default (`DEFAULT_WP`), tagged **`← DEFAULT`**, and MUST appear **before** options 2…N. Options 2…N are the remaining `IN_PROGRESS` WPs in **descending `updated_at`**, then document-order tie-break (same rules as default computation, excluding the default row).
2. **Table A row order:** The **first** data row after the header MUST be the default WP (`id == DEFAULT_WP`); renumber the `#` column starting at 1 for that row. Remaining rows follow the same order as the numbered options list (excluding the duplicate of row 1).
3. **Default gate visibility:** Immediately before Table B, print one line:  
   `Default gate for this selection: <SELECTED_GATE> ← DEFAULT`  
   If the user overrode the gate, use `← SELECTED` instead of `← DEFAULT`.  
4. **Table B ordering:** Keep the gate chain in **GATE_REGISTRY** prerequisite order for the track (do not reorder gates in a way that breaks the pipeline). The “default first” rule applies to **WP** options and to the **default-gate line** above — not to reordering `L-GATE_*` rows inside the chain table.

### Computed defaults (`DEFAULT_WP`, `DEFAULT_GATE`)

1. Read `_aos/roadmap.yaml` (including top-level `project:`).
2. Let `M = project.active_milestone` when present (e.g. `V320`).
3. Collect all `work_packages[]` entries with `status` in: `IN_PROGRESS | IN_VALIDATION | READY_FOR_SPEC_REVIEW | READY_FOR_BUILD`.
4. If `M` is set, let `C` = those entries with `milestone_ref == M`. If `C` is non-empty, use `C`; otherwise use the full `IN_PROGRESS` set from step 3.
5. Sort candidates by `updated_at` descending (ISO-8601 string). If `updated_at` is missing, use `created_at` or empty string.
6. **Tie-break:** equal `updated_at` → choose the entry that appears **later** in the `work_packages` list (document order = most recently listed active WP wins).
7. **`DEFAULT_WP`** = chosen `id`. **`DEFAULT_GATE`** = that entry’s **`current_lean_gate`** (the live gate position for that package).

**Phase -1 override:** If Phase -1 set `SELECTED_WP`, skip DEFAULT_WP computation and Table A/B display. Proceed directly to reading the WP entry for `SELECTED_WP` in Phase 0. Only compute DEFAULT_WP from BACKLOG when Phase -1 yielded nothing.

**Resolved WP / gate for this run:** If the user passed zero, one, or two arguments, set `SELECTED_WP` and `SELECTED_GATE` accordingly (defaults when args omitted: `SELECTED_WP = DEFAULT_WP`, `SELECTED_GATE = DEFAULT_GATE`). If one arg only: `SELECTED_WP = <wp-id>`, `SELECTED_GATE = current_lean_gate` of that WP from roadmap.

### Table A — Active work packages (show every time)

Emit a markdown table:

| # | id | label | milestone_ref | current_lean_gate | updated_at | status |

Include **all** `IN_PROGRESS` WPs from `_aos/roadmap.yaml`. **Row #1 (first data row)** MUST be `DEFAULT_WP`. Mark that row with **`← DEFAULT (computed)`** in the `id` column or a Notes column.

Then emit **Numbered WP options** (mandatory):

```markdown
**WP options (choose by number or id):**
1. ← DEFAULT — `DEFAULT_WP` — <label> — gate: <current_lean_gate>
2. `<next id>` — <label> — …
…
```

### Table B — Valid gates for the selected track (show every time)

Print the **Default gate for this selection** line (§Presentation item 3) **before** the table.

For **`SELECTED_WP`** (after resolving defaults/overrides), read `track` from that WP’s roadmap entry and print the **ordered** valid gate chain from `lean-kit/modules/validation-quality/GATE_REGISTRY.md` (Track A / B / L2 / L2.5). In the table, mark **`← DEFAULT`** next to **`DEFAULT_GATE`** when it equals the computed default **and** applies to the **same** WP as in Table A; if the user overrode WP/gate, mark **`← SELECTED`** on the chosen gate.

### Confirmation line (one sentence)

Print exactly one line, e.g.:  
`Using SELECTED_WP=<id> SELECTED_GATE=<gate> (defaults applied: yes/no). Override by re-invoking with arguments or naming another WP/gate in chat.`

**Non-interactive / automation:** If the environment cannot pause for input, proceed with `SELECTED_WP` / `SELECTED_GATE` after emitting Table A + B — do **not** omit the tables.

**Interactive pause (mandatory):** In interactive environments, STOP after emitting Table A, Table B, and the confirmation line. Do NOT proceed to Phase 0.5 or Phase 1 until the user explicitly confirms or overrides the WP/gate selection. Pre-flight and prerequisite validation run on the **confirmed** WP only, not on the computed default.

---

## Phase -1 — Session Context Check (three-signal model)

**Trigger:** Always executed when invoked with 0 or 1 argument. Skip when both `<wp-id>` AND `<gate-type>` are supplied explicitly.

**Purpose:** The session already knows the active WP and the last action. Use that context as the primary signal — not a roadmap scan.

**Step 1 — Classify the session event:**

Scan session context for the most recent gate event. Classify as one of three signals:

| Signal | Trigger condition | Default next action |
|--------|------------------|---------------------|
| **A — Within-WP gate advance** | Gate G = PASS / PASS_WITH_FINDINGS for WP-X, and G is NOT the final gate in WP-X's track | Mandate for next gate (G+1) of same WP-X |
| **B — WP-complete advance** | FINAL gate PASS for WP-X (all gates in track complete per GATE_REGISTRY) | Mandate for first gate of next WP in roadmap, OR handoff |
| **C — Resubmit after rejection** | Gate G = FAIL / BLOCK for WP-X in session, OR session contains fix actions following a prior FAIL verdict | Resubmission mandate for same gate G of WP-X to same validator |
| **D — Spec Authored** | Session wrote LOD300 or LOD400 artifact AND advanced `roadmap.yaml` `current_lean_gate` to `L-GATE_SPEC` (or updated `lod_status` to LOD400) for WP-X in this session | Mandate for L-GATE_SPEC of WP-X |
| *(none)* | No gate event found in session | Fall through to Manual Override (Phase 0 with DB-first) |

---

### Signal A — Within-WP Gate Advance

**Extract:** `SESSION_WP` (WP with PASS), `SESSION_GATE` (gate that passed).  
**Compute:** `NEXT_GATE` = next gate in GATE_REGISTRY track chain for SESSION_WP's track.  
**Resolve:** `NEXT_TEAM` = gate_authority for NEXT_GATE from SSoT (`core/definition.yaml` or `_aos/team_assignments.yaml`).

**Confirmation prompt:**
```
────────────────────────────────────────────────────────────────
{SESSION_GATE} PASS: {SESSION_WP} — {WP_LABEL}

Next gate in {TRACK} chain:
→ {NEXT_GATE} — validator: {NEXT_TEAM}

Generate mandate for {NEXT_GATE}?
[Y] Generate mandate   [N] Choose different WP/gate
────────────────────────────────────────────────────────────────
```

→ **[Y]:** Set `SELECTED_WP = SESSION_WP`, `SELECTED_GATE = NEXT_GATE`. Proceed to Phase 0. Skip Table A/B — already confirmed.  
→ **[N]:** Fall to Manual Override.

---

### Signal B — WP-Complete Advance

**Extract:** `SESSION_WP` (WP with final gate PASS).

---

#### Signal B.0 — Archive Mandate (mandatory pre-step)

**WP closure definition:** A WP is only fully closed when BOTH conditions are met:
1. Team 190 issued L-GATE_VALIDATE PASS → status=COMPLETE in DB + roadmap
2. Team 191 completed archival → `lod_status=LOD500_LOCKED` in roadmap + ARCHIVE_MANIFEST.md written

Signal B.0 must run before Signal B-next. Skipping it is non-canonical and must be explicitly recorded.

**Confirmation prompt:**
```
────────────────────────────────────────────────────────────────
{SESSION_WP} — L-GATE_VALIDATE PASS. Gates complete.

⚠️  WP CLOSURE REQUIRES ARCHIVE MANDATE (per L-GATE_VALIDATE.md §Post-Gate)
    Team 191 — Git, Archive & File Governance
    Scope: artifact archival to _archive/{WP_ID}/, ARCHIVE_MANIFEST.md,
           roadmap lod_status → LOD500_LOCKED, validate_aos Check 15

[Y] Generate Team 191 archive mandate (canonical — recommended)
[S] Skip — advance to next WP now (non-canonical; recorded in frontmatter)
[N] Choose different WP
────────────────────────────────────────────────────────────────
```

→ **[Y]:** Generate MANDATE to Team 191 using file:
  `_COMMUNICATION/team_191/MANDATE_{WP_ID}_ARCHIVE_CLOSURE_v1.0.0.md`
  Content per `lean-kit/modules/gate-workflow/POST_GATE_ARCHIVE_PROCEDURE.md`.
  After mandate is written, proceed to Signal B-next.
→ **[S]:** Record `archive_skip: true` in routing frontmatter. Proceed to Signal B-next.
→ **[N]:** Fall to Manual Override.

---

#### Signal B-next — Next WP Routing

**Compute:** `NEXT_WP` = next WP in roadmap with same `milestone_ref`, `status: BACKLOG|PLANNED`, ordered by phase sequence. `FIRST_GATE` = first gate in NEXT_WP's track per GATE_REGISTRY. `FIRST_TEAM` = gate_authority for FIRST_GATE from SSoT.

**Confirmation prompt:**
```
────────────────────────────────────────────────────────────────
{SESSION_WP} — archive mandate issued (or skipped).

Next WP in pipeline:
→ {NEXT_WP_ID} — {NEXT_WP_LABEL}
   First gate: {FIRST_GATE} | Team: {FIRST_TEAM}

Generate mandate for {NEXT_WP_ID} / {FIRST_GATE}?
[Y] Generate mandate   [H] Generate handoff instead   [N] Choose different WP
────────────────────────────────────────────────────────────────
```

→ **[Y]:** Set `SELECTED_WP = NEXT_WP_ID`, `SELECTED_GATE = FIRST_GATE`. Proceed to Phase 0. Skip Table A/B.  
→ **[H]:** Invoke `/AOS_handoff` logic — generate session handoff artifact to next team. Do not proceed with mandate flow.  
→ **[N]** or no NEXT_WP found: Fall to Manual Override.

---

### Signal C — Resubmit After Rejection

**Extract:** `SESSION_WP` (WP with FAIL/BLOCK), `SESSION_GATE` (gate that failed), `VALIDATOR_TEAM` (team that issued the FAIL — read from prior verdict `from:` field).

**Confirmation prompt:**
```
────────────────────────────────────────────────────────────────
{SESSION_GATE} FAIL/BLOCK: {SESSION_WP} — from {VALIDATOR_TEAM}.

Fixes applied in this session? Generate re-check mandate?
[Y] Generate resubmission mandate to {VALIDATOR_TEAM}
[N] Choose different WP/gate
────────────────────────────────────────────────────────────────
```

→ **[Y]:** Set `SELECTED_WP = SESSION_WP`, `SELECTED_GATE = SESSION_GATE`. Proceed to Phase 0. Skip Table A/B. Phase 3 will detect RESUBMISSION automatically (prior FAIL verdict exists) → Phase 3.5 remediation verification runs.  
→ **[N]:** Fall to Manual Override.

---

### Signal D — Spec Authored

**Extract:** `SESSION_WP` (WP whose `roadmap.yaml` entry was advanced to L-GATE_SPEC / LOD400 in this session).  
**Compute:** `SELECTED_GATE = L-GATE_SPEC`. `NEXT_TEAM` = gate authority for L-GATE_SPEC from SSoT.

**Detection rule (apply in order):**
1. Was a LOD300 or LOD400 file written in this session for a specific WP-X?
2. Was `roadmap.yaml` updated for the same WP-X — either `current_lean_gate` set to `L-GATE_SPEC` or `lod_status` updated to `LOD400`?
3. If both: Signal D fires for WP-X. If ambiguous (multiple WPs touched): use the last WP updated in roadmap.yaml.

**Confirmation prompt:**
```
────────────────────────────────────────────────────────────────
Spec authored: {SESSION_WP} — {WP_LABEL}
LOD: {LOD_STATUS} | Gate advanced to: L-GATE_SPEC

Next gate:
→ L-GATE_SPEC — validator: {NEXT_TEAM}

Generate mandate for L-GATE_SPEC?
[Y] Generate mandate   [N] Choose different WP/gate
────────────────────────────────────────────────────────────────
```

→ **[Y]:** Set `SELECTED_WP = SESSION_WP`, `SELECTED_GATE = L-GATE_SPEC`. Proceed to Phase 0. Skip Table A/B — already confirmed.  
→ **[N]:** Fall to Manual Override.

---

### Manual Override (no signal OR user declined)

1. **DB-first WP list:** Read `_aos/db_connectivity_status.json` → field `status`.
   - `status == "online"` → `GET /api/work-packages?project_id={id}&status=IN_PROGRESS,IN_VALIDATION,READY_FOR_SPEC_REVIEW,READY_FOR_BUILD` — use API result as WP list. On HTTP error, fall back to roadmap.yaml.
   - `status != "online"` → read `_aos/roadmap.yaml`, compute DEFAULT_WP per §Computed defaults.
2. Present Table A (IN_PROGRESS WPs), Table B (valid gates), numbered options per §Defaults & option menus.
3. **Interactive pause (mandatory):** STOP — wait for user to confirm WP/gate selection before Phase 0.5 or Phase 1.
4. After confirmation: proceed to Phase 0 with confirmed SELECTED_WP / SELECTED_GATE.

**Ask before analyzing:** In all signals AND in manual override, Phase 0.5 (Pre-flight) and Phase 1 (Prerequisites) run ONLY after the user confirms the WP. Never pre-run analysis on an unconfirmed selection.

---

## Phase 0 — Resolve WP Context

**DB-first (when entering from Manual Override):** If Phase -1 yielded no signal (manual override path), check DB before reading files:
1. Read `_aos/db_connectivity_status.json` → field `status` (already done in Phase -1 Manual Override).
2. `status == "online"` → `GET /api/work-packages/{SELECTED_WP}` for the confirmed WP entry — use API response for field extraction below. Fall back to roadmap.yaml on HTTP error.
3. `status != "online"` → read `_aos/roadmap.yaml` for the WP entry (existing flow).

**When SELECTED_WP was pre-set by Phase -1 Signal A/B/C:** Read WP entry directly from `_aos/roadmap.yaml` (or API if online) — no DEFAULT_WP computation needed.

Read `_aos/project_identity.yaml`:
- If `is_hub: true` → Hub mode: read team data from `core/definition.yaml`
- If `is_hub: false` or file missing → Spoke mode: read team data from `_aos/team_assignments.yaml`

Read `_aos/roadmap.yaml` and locate the WP entry by **`SELECTED_WP`** (from **Defaults & option menus** — never a blind guess). Extract:
- `track` (A/B), `profile` (L0/L2/L2.5), `milestone_ref`
- `current_lean_gate` — where the WP is now
- `gate_history` — all prior gates and their results
- `lod_status` — current LOD level
- `assigned_builder`, `assigned_validator`
- `spec_ref` — path to LOD spec file

If the WP ID is not found in roadmap.yaml, suggest closest matches and STOP.

---

## Phase 0.5 — Pre-flight Trivial Fix

Before generating anything, run automatic checks and fix trivial issues that would cause validation failures:

**Auto-fix (apply silently, report in summary):**
- `date` field in any existing mandate/routing file for this WP is stale → update to today
- Version string in spec_ref file doesn't match roadmap.yaml `lod_status` → note discrepancy (do NOT auto-fix spec content)
- LOD artifact exists but path in roadmap.yaml `spec_ref` has a typo (off-by-one in path segment) → note, ask user to confirm correct path

**Check and WARN (do not auto-fix — present as findings before proceeding):**
- `spec_ref` file does not exist at the declared path → WARN: "spec_ref not found — mandate will reference a missing file"
- LOD artifacts exist but are marked `draft` in their frontmatter → WARN: "draft LOD — may not satisfy LOD gate requirement"
- Gate prereqs: preceding gate has no `result: PASS` in gate_history → WARN (handled fully in Phase 1)
- **Dependency activation-condition cross-check (v1.2.0):** If the WP entry has `depends_on:` referencing another WP, or a prior routing artifact for this WP contains an `activation_condition:` that names another WP's gate (e.g. `"D38 L-GATE_VALIDATE PASS confirmed"`): locate the latest `VERDICT_*{dep_wp}*.md` in `_COMMUNICATION/team_{validator}/`. If that verdict carries `result: FAIL` or `result: BLOCK` → WARN: "Dependency {dep_wp} has FAIL/BLOCK verdict on file — verify activation condition before routing." Non-blocking; proceed with mandate generation.

**Report pre-flight result:**
```
PRE-FLIGHT: {N} auto-fixed | {M} warnings | {K} blockers
Auto-fixed:  {list or "none"}
Warnings:    {list or "none"}
Blockers:    {list or "none — proceed" / "STOP — resolve before mandate"}
```

If any blocker is found, STOP and present the blocker with fix guidance.

---

## Phase 1 — Validate Prerequisites

Check that **`SELECTED_GATE`** is valid for this WP's track:

| Track | Valid gates (in order) |
|-------|----------------------|
| L0 Track A | L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE |
| L0 Track B | L-GATE_ELIGIBILITY → L-GATE_CONCEPT → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE |
| L2 | GATE_0 → GATE_1 → GATE_2 → GATE_3 → GATE_4 → GATE_5 |
| L2.5 | EXT-CP1 → PH1..PH6 (with EXT-CP2 between PH4A and PH4B) |

**Enhancement WP L-GATE_ELIGIBILITY auto-waiver (check before prerequisite enforcement):**

If `SELECTED_GATE == L-GATE_SPEC` and the following conditions are ALL met, auto-waive the L-GATE_ELIGIBILITY prerequisite:
1. WP entry in roadmap.yaml has a `parent_wp:` field, AND
2. Parent WP's `gate_history` includes `L-GATE_ELIGIBILITY: PASS` OR parent WP `status` is `COMPLETE`, AND
3. WP entry has `type: ENHANCEMENT` or `ENHANCEMENT` appears in the WP label or id

On auto-waiver:
- Add to mandate frontmatter: `eligibility_waived: true` + `eligibility_waiver_reason: "Enhancement to COMPLETE parent WP — auto-waived per CANON v1.2.0 §Phase 1"`
- Emit pre-flight note: `WAIVER: L-GATE_ELIGIBILITY prerequisite waived for enhancement WP {WP_ID} (parent: {PARENT_WP_ID})`
- No user interaction required — proceed with prerequisites check for remaining gates

**Prerequisite checks:**
1. The preceding gate must have `result: PASS` (or `PASS_WITH_FINDINGS` or `CLEAR`)
2. LOD level must match gate requirements **per track** (see GATE_REGISTRY.md):
   - L-GATE_ELIGIBILITY: LOD100 minimum (all tracks)
   - L-GATE_CONCEPT: LOD200 minimum (Track B only — not present in Track A)
   - L-GATE_SPEC: **Track A: LOD200 + LOD400** | **Track B: LOD300 + LOD400**
   - L-GATE_BUILD: LOD400 + implementation complete (all tracks)
   - L-GATE_VALIDATE: LOD400 + L-GATE_BUILD PASS (all tracks)

If prerequisites are not met, STOP and present:
1. The specific missing item (e.g., "LOD400 not found — spec_ref path is {path}")
2. The concrete unblocking action (e.g., "Generate LOD400 spec for this WP first, then re-invoke")
3. The immediately actionable alternative within 2 lines (e.g., "Or choose a different WP that IS eligible: [list eligible WPs from roadmap]")

Do not generate a mandate for an ineligible gate.

---

## Phase 2 — Determine Target Team

Resolve the target team from gate authority rules:

| Gate | Default authority | Team resolution |
|------|------------------|----------------|
| L-GATE_ELIGIBILITY | Constitutional validator | Read `gate_authority.L-GATE_ELIGIBILITY` from SSoT |
| L-GATE_CONCEPT | Architecture team | team_100 or team_110 |
| L-GATE_SPEC | Constitutional validator | Read `gate_authority.L-GATE_SPEC` from SSoT |
| L-GATE_BUILD | QA + Dev validator | team_50 (QA) primary. Present option: also create team_90 (tech validation) mandate |
| L-GATE_VALIDATE | Constitutional validator | Read `gate_authority.L-GATE_VALIDATE` from SSoT |
| EXT-CP1, EXT-CP2 | Constitutional validator | team_190 |

Read the resolved team's `engine` and `environment` from SSoT (dynamic — do NOT hardcode).

---

### Cross-Engine Pre-Check (V318 insertion)

Before writing the mandate artifact:

1. Read `assigned_builder` from the WP entry in `_aos/roadmap.yaml`
2. Read `assigned_validator` from the WP entry in `_aos/roadmap.yaml`  
3. Resolve vendor using this mapping:
   - `claude-*` or `anthropic-*` or `agentos_build` → **Anthropic**
   - `codex*`, `gpt-*`, `openai-*`, `agentos_val` → **OpenAI**
   - `cursor-*` → **Cursor**
   - `human` → **Human**
4. If builder_vendor == validator_vendor:
   - Emit the WARN block below
   - Await user input: CONFIRM or ABORT
   - If ABORT: stop — do NOT write mandate artifact
   - If CONFIRM: proceed with `cross_engine_override: true` in frontmatter

**WARN block to emit:**
```
⚠️  CROSS-ENGINE CONSTRAINT VIOLATION
────────────────────────────────────────────────
Builder:   {assigned_builder}   → vendor: {builder_vendor}
Validator: {assigned_validator} → vendor: {validator_vendor}
Iron Rule 1: builder engine must differ from validator engine
────────────────────────────────────────────────
Type CONFIRM to override (recorded in mandate frontmatter), or ABORT to cancel:
```

5. Add to mandate frontmatter:
   - If no violation: `cross_engine_verified: true`
   - If override: `cross_engine_verified: false` + `cross_engine_override: true`

---

## Phase 3 — Detect Round + Override

**Count prior mandates for this WP + gate:**
- Search `_COMMUNICATION/team_{TO_ID}/` for files matching `*MANDATE*{WP_ID}*` and `*MANDATE*{WP_ID}*{GATE}*`
- Also search `_COMMUNICATION/team_{TO_ID}/` for `*VERDICT*{WP_ID}*` with BLOCK or FAIL results
- Count distinct mandate rounds → `prior_rounds = N`
- Current submission = `round = N + 1`

**Classify mode:**
- `round == 1` and no prior BLOCK verdict → **FRESH** (first submission)
- `round > 1` and prior BLOCK/FAIL verdict exists → **RESUBMISSION** (post-fix round)

**Signal C fast-path:** When SELECTED_WP and SELECTED_GATE were pre-set by Phase -1 Signal C (user confirmed resubmit intent), prior FAIL/BLOCK verdict already exists — this phase will classify as RESUBMISSION automatically. Proceed directly to Phase 3.5.

**For RESUBMISSION mode:**
- Read the most recent BLOCK/FAIL verdict to extract blocker findings
- **Before** writing a new mandate or routing prompt: execute **Phase 3.5 — Remediation verification** (below). Do **not** issue a re-validation request if remediation is incomplete.
- After Phase 3.5 passes: bump version: prior `v1.0.0` → `v1.1.0`; `v1.1.0` → `v1.2.0`, etc.
- Add `supersedes:` field pointing to the prior mandate
- Add `resubmission_round: {N}`
- In mandate §6 (Resolved findings), map each prior blocker to fix evidence

**Agent default selection + user override:**

Display detected state and offer override before proceeding:

```
=== ROUND DETECTION ==========================================
Mode:      {FRESH | RESUBMISSION}
Round:     #{N}  (based on {N-1} prior mandates found)
Prior:     {last verdict file — result — date}
Version:   v{X.Y.Z}

  [Y] Confirm — proceed with Round #{N}
  [R] Override round number — enter manually
  [F] Force FRESH — ignore prior mandates
=============================================================
```

Wait for user input. If `[Y]` or Enter → proceed with detected values.

---

## Phase 3.5 — Remediation verification (mandatory before resubmission / re-validation)

**When:** Mode is **RESUBMISSION**, or any prior **VERDICT** for this WP + gate exists with **FAIL**, **BLOCK**, or **PASS_WITH_FINDINGS** that requires remediation before the next validator pass.

**Rule:** A **mandate** (or prior gate) that required fixes does **not** authorize automatic re-validation. The agent MUST prove fixes are **adequately done** before emitting a **resubmission mandate** or **re-validation / validation request** (routing to Team 190, 90, 50, etc.).

**Steps (all required):**

1. **Load prior verdict(s):** Read the latest `VERDICT_*{WP}_{GATE}*.md` for this gate; extract every **BLOCKER**, **MAJOR**, and any **MINOR** the verdict marks as required before re-validation.
2. **Build a remediation matrix** (emit as a markdown table):

   | Finding ref | Severity | Required action (from verdict) | Status | Evidence |
   |-------------|----------|----------------------------------|--------|----------|
   | … | … | … | **FIXED** / **WAIVED** / **OPEN** | path, commit, command output, or waiver id |

3. **Verify in repo:** For each finding, confirm with primary artifacts (file on disk, `git` tracked state, test log, `validate_aos.sh` output — as applicable). **Do not** rely only on builder claims in chat.
4. **STOP condition:** If **any** row is **OPEN** (or WAIVED without documented Team 00 / authority where the verdict required it): **STOP** — print the matrix, list gaps, and **do not** write resubmission mandate or routing. User must complete fixes or obtain waiver first.
5. **Proceed condition:** If every row is **FIXED** or **WAIVED** with valid evidence: print  
   `REMEDIATION VERIFIED — resubmission mandate / re-validation request permitted.`  
   Then continue to Phase 4+ and generate **RESUBMISSION** mandate + routing with §6 Resolved findings populated from this matrix.

**Non-interactive:** Still perform steps 1–3 and emit the matrix; if OPEN → STOP with matrix; if all clear → proceed.

---

## Phase 4 — Context Level Selection

**Default application rule (v1.2.0):** Apply the hint as the automatic default. No interactive stop required. Display the selection screen as informational (shows which level was chosen and why). Proceed with the computed default unless the user has already specified a level in the current turn via `--context N` argument or an inline instruction such as "use level 1".

Display selection screen (informational — default applied, override still available):

```
=== ROUTING CONTEXT LEVEL ====================================
Target:     team_{TO_ID} — {name}
Engine:     {engine} | Environment: {environment}
Round:      #{N}

  [1] MINIMAL — action + delta only
       For: same session, team already loaded and mid-work
       Includes: resolved findings, mandate path, verdict path
       Lines: ~10

  [2] GOVERNANCE — role + iron rules reminder
       For: team returning from different WP or brief break
       Includes: role description, 3 iron rules, context, mandate
       Lines: ~25

  [3] FULL — complete session activation
       For: fresh session, new Codex/Cursor window, cold start
       Includes: all identity layers, mandatory reads, first action
       Lines: ~50

Default applied: Round #1 → [3], Round #2 → [2], Round #3+ → [1]  ← APPLIED AUTOMATICALLY
Override: re-invoke with --context 1/2/3, or reply with your level choice before the mandate is generated.
=============================================================
```

**Session-continuity override (v1.4.1):** When the resubmission target is the SAME team that issued the prior rejection AND that session is still active (same Cursor / Claude Code window, routing was delivered in-chat, no cold-start required), apply **[1] MINIMAL** regardless of round number.

Rationale: the session already holds WP context, all findings, and gate state. Re-sending GOVERNANCE or FULL context wastes tokens and dilutes validator focus on the delta.

Detection: mandate generator (team_100) checks Signal C routing — if the validator was reached in-chat without a new environment activation block, default to [1] MINIMAL. When session status is unknown, fall back to the round-number default above.

Proceed immediately with the computed default level. No wait for user input unless the user has already provided an override in this turn.

---

## Phase 5 — Generate Mandate Artifact

Write the mandate file to `_COMMUNICATION/team_{TO_ID}/` using the **unified mandate template** at:
`lean-kit/modules/validation-quality/templates/MANDATE_TEMPLATE.md`

**File naming:**
- Fresh: `_COMMUNICATION/team_{TO_ID}/MANDATE_{WP_ID}_{GATE}_v{VERSION}.md`
- Resubmission: `_COMMUNICATION/team_{TO_ID}/MANDATE_{WP_ID}_{GATE}_RESUBMISSION_R{N}_v{VERSION}.md`

### YAML Frontmatter (all fields required):
```yaml
---
id: MANDATE_{WP_ID}_{GATE}_v{VERSION}
from: Team {FROM_ID} ({FROM_ROLE})
to: Team {TO_ID} ({TO_ROLE})
date: {YYYY-MM-DD}
type: {GATE_MANDATE | QA_MANDATE | RESUBMISSION}
gate: {GATE_TYPE}
wp: {WP_ID}
project: {PROJECT_ID}
status: ACTIVE
verdict: PENDING
engine_constraint: "{cross-engine rule description}"
resubmission_round: {N}        # only for resubmissions
supersedes: {prior mandate id}  # only for resubmissions
---
```

### Body Structure (8 sections — all required):

1. **Header** — gate type, WP label, track/profile/risk
2. **Prior Gate History** — table with Gate/Result/Date/Validator/Notes columns
3. **Scope** — what this gate validates (derived from gate type per GATE_REGISTRY.md)
4. **Validation Criteria** — VC/AC table with criterion name + what to check
5. **Files to Review** — spec documents, implementation files, prior artifacts
6. **Resolved Findings** (resubmission only) — findings from prior BLOCK with fix applied + verification path
7. **Output** — verdict path using unified naming (`VERDICT_{WP_ID}_{GATE}_v{VERSION}.md`), constraints (cross-engine, independence, evidence, enforcement mode)
8. **Post-Mandate Routing** ← **mandatory, always last** — deterministic next-step table (see below)

### §8 Post-Mandate Routing (mandatory in every mandate)

This section removes all ambiguity about what to do after the mandate is executed.
The executing team reads this section **after writing the verdict** to know exactly what to invoke next.

**Template (insert at end of every generated mandate):**

```markdown
## Post-Mandate Routing

When verdict is written to `{VERDICT_PATH}`, invoke the following based on outcome:

| Outcome | Next Invocation | Signal |
|---------|----------------|--------|
| **PASS** | `/AOS_gate-mandate {WP_ID} {NEXT_GATE}` | A — within-WP gate advance to {NEXT_GATE} / {NEXT_TEAM} |
| **PASS** (final gate only) | `/AOS_gate-mandate {WP_ID}` | B.0 — WP complete → Team 191 archive mandate first |
| **PASS_WITH_FINDINGS** | Same as PASS above — surface notes to Team 00 first | |
| **FAIL** | Return verdict to Team 00. Builder applies fixes. Then: `/AOS_gate-mandate {WP_ID} {THIS_GATE}` | C — resubmission to same validator |
| **BLOCK** | Return verdict to `{ASSIGNED_BUILDER_TEAM}` (architect responsible for this WP). Builder resolves blockers. Escalate to Team 00 only if blockers require a principal decision. | — |

**This gate:** `{THIS_GATE}` | **This WP:** `{WP_ID}`
**Next gate (if PASS):** `{NEXT_GATE}` → validator: `{NEXT_TEAM}` (engine: `{NEXT_ENGINE}`)
**Final gate in track?** {YES → Signal B.0 applies | NO → Signal A applies}
```

**Populate at generation time:**
- `{THIS_GATE}` = SELECTED_GATE
- `{WP_ID}` = SELECTED_WP
- `{NEXT_GATE}` = next gate in GATE_REGISTRY track chain after SELECTED_GATE
- `{NEXT_TEAM}` = gate_authority for NEXT_GATE from SSoT
- `{NEXT_ENGINE}` = engine for NEXT_TEAM from SSoT
- **Final gate check:** Is SELECTED_GATE the last gate in the track? → YES = Signal B.0 row applies; NO = Signal A row applies
- If SELECTED_GATE is the final gate: replace Signal A row with Signal B.0 row; omit Signal A row entirely to avoid confusion

---

## Phase 6 — Generate Routing Prompt

Write the routing file to `_COMMUNICATION/team_100/ROUTING_TEAM_{TO}_{WP_ID}_{GATE}{_R{N} if resubmission}.md`

The file must contain a YAML frontmatter + a single fenced code block — **copy-paste ready**.

Generate routing prompt content based on selected context level:

---

### Level 1 — MINIMAL (action + delta only)

```markdown
---
id: ROUTING_TEAM_{TO}_{WP_ID}_{GATE}_R{N}
from: Team 100
to: Team 00 (for routing to Team {TO_ID})
date: {TODAY}
type: ROUTING_PROMPT
context_level: 1
round: {N}
---

# Routing: Team {TO_ID} | {GATE} | {WP_ID} | Round #{N}

Copy-paste into {ENGINE} environment:

```
Team {TO_ID} — Round #{N} {GATE} for {WP_ID}.

Prior round result: {PRIOR_RESULT} (Round #{N-1}, {PRIOR_DATE})

Resolved since Round #{N-1}:
{for each resolved blocker: - {BLOCKER_ID}: {one-line description of fix}}

Mandate: {MANDATE_PATH}
Verdict (write here): _COMMUNICATION/team_{TO_ID}/VERDICT_{WP_ID}_{GATE}_v{VERSION}.md

Execute the mandate. All VC criteria must be re-tested — do not inherit prior round's PASS results
without verification.
```
```

---

### Level 2 — GOVERNANCE (role + iron rules reminder)

```markdown
---
id: ROUTING_TEAM_{TO}_{WP_ID}_{GATE}{_R{N} if round>1}
from: Team 100
to: Team 00 (for routing to Team {TO_ID})
date: {TODAY}
type: ROUTING_PROMPT
context_level: 2
round: {N}
---

# Routing: Team {TO_ID} | {GATE} | {WP_ID}{if round>1:  | Round #{N}}

Copy-paste into {ENGINE} environment:

```
You are Team {TO_ID} — {ROLE_DESCRIPTION first sentence}.
Engine: {ENGINE}. Environment: {ENVIRONMENT}.

Iron Rules:
1. {iron_rules[0]}
2. {iron_rules[1]}
3. {iron_rules[2] or "Independence: form conclusions from primary artifacts ONLY"}

Context:
- Project: {PROJECT_ID} (profile: {PROFILE})
- WP: {WP_ID} — {WP_LABEL}
- Gate: {GATE_TYPE}{if round>1:  — Resubmission Round #{N}}
{if round>1:
- Prior result: {PRIOR_RESULT} — {PRIOR_DATE}
- Resolved: {count} blocker(s) fixed since last round
}

Mandate (read this): {MANDATE_PATH}
Verdict (write here): _COMMUNICATION/team_{TO_ID}/VERDICT_{WP_ID}_{GATE}_v{VERSION}.md

Execute independently. Do not read other teams' conclusions before forming your verdict.
```
```

---

### Level 3 — FULL (complete session activation)

```markdown
---
id: ROUTING_TEAM_{TO}_{WP_ID}_{GATE}{_R{N} if round>1}
from: Team 100
to: Team 00 (for routing to Team {TO_ID})
date: {TODAY}
type: ROUTING_PROMPT
context_level: 3
round: {N}
---

# Routing: Team {TO_ID} | {GATE} | {WP_ID}{if round>1:  | Round #{N}}

Copy-paste into a **fresh {ENGINE} session**:

```
You are Team {TO_ID} — {NAME} — for the {DOMAIN} domain.
Engine: {ENGINE}. Environment: {ENVIRONMENT}.

MANDATORY STARTUP — read in this exact order:
{if __ONBOARDING_TEAM_{TO_ID}.md exists:}
1. _COMMUNICATION/team_{TO_ID}/__ONBOARDING_TEAM_{TO_ID}.md — team onboarding (always first)
{end if}
{N}. _aos/governance/team_{TO_ID}.md — governance contract
{N+1}. _aos/roadmap.yaml — WP state SSoT
{N+2}. {MANDATE_PATH} — your gate mandate (read last, after identity is established)

## Identity & Authority
- Team: team_{TO_ID} — {NAME}
- Role: {ROLE_DESCRIPTION — first 2 sentences}
- Engine: {ENGINE} | Environment: {ENVIRONMENT}
- Gate authority: {gate_authority relevant fields}
- Write authority: {writes_to[]}

## Iron Rules
{for each iron_rule in iron_rules[]:}
- {iron_rule}

## Context
- Project: {PROJECT_ID} (profile: {PROFILE})
- WP: {WP_ID} — {WP_LABEL}
- Gate: {GATE_TYPE}
{if round>1:
- This is Round #{N} (Resubmission)
- Prior result: {PRIOR_RESULT} — {PRIOR_DATE}
- Prior blockers: {count} — see §6 of mandate for resolved findings
}
{if round==1:
- Track: {A | B | L2.5} | LOD: {LOD_STATUS}
- Prior gates: {gate_history summary — one line per gate}
}

## Your Task
Execute the {GATE_TYPE} mandate. Validate all criteria independently.
Do NOT read other teams' conclusions before forming your verdict.
Cross-engine rule: builder engine ≠ validator engine (builder: {BUILDER_ENGINE}; you: {TO_ENGINE}).

FIRST ACTION: Read _aos/governance/team_{TO_ID}.md, then _aos/roadmap.yaml, then the mandate at {MANDATE_PATH}.

Verdict (write here): _COMMUNICATION/team_{TO_ID}/VERDICT_{WP_ID}_{GATE}_v{VERSION}.md
```
```

---

## Phase 7 — Summary

Display final summary — all info in one view:

```
=== MANDATE COMPLETE ==========================================
WP:           {WP_ID} — {WP_LABEL}
Gate:         {GATE_TYPE} | Track: {A/B} | Profile: {L0/L2/L2.5}
Target:       team_{TO_ID} — {NAME}
Engine:       {ENGINE} | Environment: {ENVIRONMENT}
Submission:   Round #{N} — {FRESH | RESUBMISSION}
Context:      Level {1|2|3} — {MINIMAL | GOVERNANCE | FULL}
Output type:  {MANDATE_FRESH | MANDATE_RESUBMISSION | HANDOFF}
Signal:       {A — within-WP gate advance | B — WP complete | C — resubmit | none — manual}

Pre-flight:   {N} auto-fixed | {M} warnings
Mandate:      {MANDATE_PATH}
Routing:      {ROUTING_PATH}

NEXT STEP:    Route to Team {TO_ID} via {ENGINE} environment.
==============================================================

ROUTING PROMPT DISPLAY RULE (mandatory — always apply one of these two):

  Prompt ≤ 30 lines  →  Display inline as a fenced code block below.
                        Label: "── Copy this block ──────────────────────"
                        User copies the entire block as one unit.

  Prompt > 30 lines  →  Display the file path ONLY — do NOT paste inline.
                        Label: "── Open this file ───────────────────────"
                        Show:  {ROUTING_PATH}
                        Instruction: "Open in editor — copy the fenced block inside."
                        In Claude Code terminal: cmd+click the path to open.
                        In Cursor/IDE: the path renders as a clickable link.

Apply now:
{if prompt_line_count ≤ 30:}
── Copy this block ──────────────────────────────────────────
{routing prompt fenced block}
─────────────────────────────────────────────────────────────

{else:}
── Open this file ───────────────────────────────────────────
{ROUTING_PATH}
─────────────────────────────────────────────────────────────
Copy the fenced block inside the file.
{end if}
```

---

## Error Handling

| Error | Action |
|-------|--------|
| WP not found in roadmap.yaml | Suggest closest ID matches, STOP |
| Prerequisites not met | Show missing prerequisites, STOP |
| Pre-flight blocker found | Show blocker + fix guidance, STOP |
| Prior verdict path not found | Proceed as fresh mandate, warn |
| Target team not in SSoT | WARN — ask user to specify team manually |
| Gate type not valid for track | Show valid gates for this track, STOP |
| spec_ref file not found | WARN in pre-flight, include note in mandate |
| Level 3 selected but __ONBOARDING not found | Skip onboarding line, continue with governance contract |
