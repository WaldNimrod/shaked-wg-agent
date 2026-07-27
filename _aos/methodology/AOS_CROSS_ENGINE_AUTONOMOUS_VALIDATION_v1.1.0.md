# AOS Cross-Engine Autonomous Validation (v5)

- **Version:** v1.1.0
- **Date:** 2026-06-27 (v1.0.0) · amended 2026-07-15 (v1.1.0)
- **Owner:** team_100 (Chief System Architect) + team_00 (Principal)
- **Status:** CANON — binding for every gated build/validate handoff in all spokes
- **Origin:** ALERT_team_110 (2026-06-27) — the autonomous path (`cursor-agent`) works but was undocumented;
  the documented path was still v4-style human-paste. Closes that gap system-wide.
- **v1.1.0 amendment (2026-07-15, team_100 + team_00):** adds **§4.1 validator tiering** + **§4.1.1 cost + risk
  escalation matrix** + **§9 calibration-weak validator addendum** — the operational canon for engines that are
  strong nets but poor judges (Grok 4.5 the first case), and for matching engine strength to check subtlety
  independent of cost tier. Folds in `REGISTER_ENGINE_xai-via-cursor` (team_00-approved), the S010 field trial
  (`§M.12`), the BE-S1/WP001-WP002 field insights, and two external studies. Filename renamed `_v1.0.0`→`_v1.1.0`
  (team_120, same amendment). Propagation rides the next `aos_sync_all.sh` (Ambassador team_120).

---

## 1. The rule

> When Iron Rule #1 requires a **cross-engine validator** (validator engine ≠ builder engine at the decisive
> gate), the builder session **drives the validator engine's headless CLI directly**. It does **NOT** generate
> a human-paste activation block and ask the Principal to carry it to another app. v5 sessions have the tools;
> they use them.

Human-paste (open a second app, paste the prompt) is the **v4 fallback** — retained only for engines that have
no headless CLI, never as the default.

### 1.1 Prompt-display policy (binding — team_00 directive 2026-06-27)

| Situation | Behaviour |
|---|---|
| **Default — any CLI-capable validator** (cursor / cursor-composer-2 / codex) | **ALWAYS run the CLI.** Do not display a human-paste prompt. |
| **Operator asks or configures it** (`/AOS_dispatch --paste` / `--no-exec`, or "show me the prompt") | Run is suppressed; display the human-paste activation block on request. |
| **Validator engine has no headless CLI** (e.g. `engine: variable`) | Auto-fallback to the human-paste block (the run is impossible). |
| **team_80 (Research) — ANY invocation** | **ALWAYS ALSO display the human-paste prompt**, in addition to attempting the run. team_80 (`engine: variable`, pre-approval-gated per `team_80.md`) is the one team that is never driven purely headless: the operator always sees the prompt. This is an explicit rule, not an emergent side-effect of `engine: variable`. |

So: **CLI by default for everyone; a prompt only when you ask for it — except team_80, which always shows you the prompt too.**

## 2. Why (the defect this fixes)

The v4 canon trained every session to offload cross-engine validation onto the human: `/AOS_dispatch` Phase 2
emits *"copy the block → open a new Claude Desktop → paste"* (`AOS_dispatch.md:57-62`), and the spoke `CLAUDE.md`
states only the *rule* (builder ≠ validator), never the *tool*. So a compliant session lands on human-paste —
which defeats v5's unified tooling and stalls every gate behind the operator. The autonomous mechanism
(`cursor-agent`) existed and worked but appeared in **zero** methodology/script/command files.

## 3. The mechanism — headless invocation per engine

`cursor-agent` (`~/.local/bin/cursor-agent`) runs the Cursor agent headless; `codex` runs the OpenAI Codex CLI.
Both take a workspace + a mandate string and write report artifacts without a human in the loop.

| Roster engine (`core/definition.yaml`) | Headless CLI invocation | Default model |
|---|---|---|
| `cursor`, `cursor-composer-2` | `cursor-agent -p --force --trust --model composer-2.5 --workspace <path> "<mandate>"` | `composer-2.5` (= the `cursor-composer-2` engine) |
| `codex` | `codex exec --cd <path> --model gpt-5.1-codex "<mandate>"` *(or `cursor-agent --model gpt-5.1-codex …` — codex models are in `cursor-agent --list-models`)* | `gpt-5.1-codex` |
| `claude*` | **invalid as a validator against a Claude builder** (IR#1) — pick a `cursor`/`codex` validator instead | — |

**Flags:** `-p/--print` = headless print mode (shell + write tools, no interactive UI); `--force --trust` =
run without per-action approval prompts; `--workspace` = the repo/worktree to inspect. The validator is
**report-only** — it re-runs suites, reviews against spec, and writes a verdict artifact; it does **not** edit
app code.

## 4. Validator team → engine map (v5 roster)

| Validator team | Engine | Headless CLI | Typical gate |
|---|---|---|---|
| **team_90** (Default / Senior Constitutional Validator) | `cursor-composer-2` | `cursor-agent … --model composer-2.5` | L-GATE_BUILD, L-GATE_VALIDATE (governance facet), L-GATE_SPEC/ELIGIBILITY |
| **team_50** (QA & Functional Acceptance) | `cursor` | `cursor-agent … --model composer-2.5` | L-GATE_VALIDATE (functional facet) |
| **team_70 / codex senior** | `codex` | `codex exec …` | cross-engine senior review when the builder is Cursor |

Cross-engine pairing: **builder=Claude → validator=Cursor (team_90/50) or Codex**; **builder=Cursor →
validator=Codex or Claude**. Never validate with the same engine that built, at the decisive gate (ADR053).

### 4.1 Validator TIERING (v1.1.0 — BINDING)

Not all validators are interchangeable. A validator is either a **first-pass net** (cheap, high-recall,
poorly-calibrated → produces a *candidate list*) or a **decisive judge** (frontier, better-calibrated → produces
a *trusted verdict*). Assign by tier, not just by team:

| Tier | Engines (vendor) | Produces | Rule |
|---|---|---|---|
| **First-pass / intermediate** (TC-7) | `cursor-grok-4.5-high` (xai) · `cursor-composer-2` / Composer 2.5 (cursor) | an **unranked candidate list** | cheap + fast (flat `cursor_max_400` pool) → run *many* passes; **NEVER a decisive verdict alone**; every finding is a candidate to ground, not a fact |
| **Decisive / constitutional** (TC-8) | `gpt-5.x` / `codex` (openai) · Claude Opus (only when builder ≠ Claude) | the **trusted verdict** | mandatory as the verdict engine at every decisive gate (G1 spec-approval, G4 cert, L-GATE_BUILD/VALIDATE final) |

**Decisive-gate multi-vendor rule (BINDING):** at a decisive gate the verdict MUST come from a **decisive-tier**
engine. Any first-pass engine used runs **alongside** it — **diff the two, and independently ground every
finding** (a `file:line` check or a repro) before acting. **No decisive gate rests on one engine, and never on a
first-pass engine's verdict.** Grok/Composer widen coverage; the decisive engine (or your own grounding) judges.

**Vendor diversity:** for a Claude-built artifact the CLI-ready distinct-vendor validators today are
`{openai/GPT, cursor/Composer, xai/Grok}` — three vendors. `gemini` (google, registered, premium) is the
recommended **4th vendor** to break any OpenAI/xAI blind-spot overlap. **Correction (team_120 scoping,
2026-07-15): the "pending a headless path (not in `cursor-agent`)" note above is now stale** — verified live
on this machine that `cursor-agent --list-models` already lists `gemini-3.1-pro`/`gemini-3-flash`/`gemini-3.5-flash`,
and a real headless `--print --output-format json` call against Gemini succeeded. The engine is already
registered in `engines.yaml` at `access_method: mcp` (interactive-only); wiring a `cli_via_bash` method
(mirroring `xai-via-cursor`) is the remaining gap, not a from-scratch registration. **Caveat:** Gemini has a
long, recurring history of tool-call reliability issues specifically within Cursor across model generations,
persisting into the Gemini 3 era (multiple independent forum reports) — a different failure mode from Grok's
calibration problem, but a real one; treat as first-pass/net-widening only until proven otherwise, same posture
as Grok. Full scoping + proposed `engines.yaml` amendment: see team_100's inbox. More independent vendors at a
decisive gate = fewer correlated misses.

### 4.1.1 Cost + risk escalation matrix (v1.1.0 — BINDING)

Engine cost is a significant lever — but **cheap-by-default only works paired with risk-based escalation**.
Cost tier and decisiveness tier (§4.1 above) answer *who can render the verdict*; this matrix answers
*what should even run the check*, matched to how subtle the change actually is.

**Default: cheap, flat-pool first-pass.** First-pass/intermediate validation defaults to the flat
`cursor_max_400` pool — **Composer 2.5 or Cursor `auto`** (free at the margin) — **not** GPT-5.5 (premium,
metered). GPT-5.x/Opus are reserved for **decisive**-tier gates (§4.1), not spent on routine first-pass checks.

**But subtlety escalates the engine, even at first-pass.** Hard evidence (WP001 build-validate, 2026-07-15):
a bash `restore` trap was installed **after** the `mv` of `api/.env` — meaning an `INT`/`TERM` signal landing in
that window would strand `.env` in an inconsistent state. **GPT-5.5 caught this signal-safety bug; a full,
fully-green test suite (1413 pytest + 650 vitest) and a truncated Grok pass both missed it.** The lesson:
correctness checks (green tests, a fast net-pass) do not substitute for an engine capable of reasoning about
*why* code is subtle — some diffs need a stronger engine even when nothing else about the gate is decisive yet.

| Validation-process type | Default profile (`engine` / `mode` / `model-tier`) | Notes |
|---|---|---|
| Small, mechanical diff (formatting, copy, codegen, single-file boilerplate) | `auto` or `cursor-composer-2` / plan / cheap | Flat pool; no escalation needed |
| **Subtle-logic diff** (signal/concurrency safety, security, numeric/valuation correctness, migrations) | `gpt-5.x` / plan / premium — **even at first-pass** | Green tests are not sufficient evidence for this class; escalate the *engine*, not just the gate |
| Large spec deep-validation (a full package review, many files) | **Paired**: `cursor-grok-4.5-*` (net, wide+cheap) + `gpt-5.x` (judge) — diff findings, ground every one | Matches §4.1/§9: Grok widens the candidate list, GPT/your own grounding decides what's real |
| Decisive gate (G1 spec-approval, G4 cert, L-GATE_BUILD/VALIDATE final) | `gpt-5.x`/`codex` **+ a 2nd distinct vendor** | Per §4.1's decisive multi-vendor rule — never one engine alone |

**Reconfirmed (2026-07-15, same day):** on a *small* 6-file diff, Grok truncated its final JSON `.result` to
progress-narration only (~12k tokens of work, no report emitted) — the same failure shape as §9, now observed on
a routine-sized task, not just a large one. **Never rely on Grok alone for a captured/final verdict, regardless
of diff size** — reinforces "net, not judge" (§9) as a size-independent rule, not just a large-package caveat.

**Adoption note:** BE-S1/WP002 onward defaults to Composer/`auto` for first-pass, escalating per this matrix.

## 5. The wrapper (thin orchestrator — Iron Rule #13)

`scripts/run_cross_engine_validation.sh <validator_team> <workspace> <mandate_path>` does all of the above in
one call: resolves the validator's engine from `core/definition.yaml`, maps engine→CLI/model, invokes it
headless, tees the run log to `<workspace>/_COMMUNICATION/<team>/`, locates the verdict artifact the validator
wrote, and prints the verdict flag (PASS / PASS_WITH_FINDINGS / FAIL / BLOCKED).

```bash
# example — Claude builder needs the L-GATE_BUILD cross-engine validation by team_90 (Cursor):
scripts/run_cross_engine_validation.sh team_90 \
  /Users/nimrod/Documents/AOS_V5/<domain> \
  _COMMUNICATION/team_90/MANDATE_<WP>_L-GATE_BUILD.md
# add --dry-run to print the resolved command without invoking the engine.
```

The mandate file is the prompt body (context bundle + what to validate + where to write the verdict). The
wrapper enforces the IR#1 guard: a `claude*` validator engine is rejected (the common builder here is Claude).

## 6. `/AOS_dispatch --exec` (autonomous mode)

`/AOS_dispatch` gains an **`--exec`** flag: when the target engine has a headless CLI, it runs the wrapper
instead of emitting the human-paste block — the gate is validated end-to-end with no operator step. Without
`--exec`, or for an engine with no CLI, it falls back to the v4 paste block (now explicitly labelled
*"fallback — only when the target engine has no headless CLI"*). Default for cross-engine gates going forward:
**`--exec`**.

## 7. Spoke guidance (CLAUDE.md + GATE_REGISTRY)

Every spoke `CLAUDE.md` "Cross-engine" note and the `GATE_REGISTRY` get one line:

> **Cross-engine validation is autonomous.** Drive the validator engine via
> `scripts/run_cross_engine_validation.sh` (canon: `methodology/AOS_CROSS_ENGINE_AUTONOMOUS_VALIDATION_v1.1.0.md`).
> Never hand a validation prompt to the human — that is the v4 fallback, used only when the target engine has
> no headless CLI.

The in-repo v4 `ACTIVATION_PROMPT_*` examples are **deprecated** — relabel "fallback only" or archive.

## 8. Propagation

Hub-authored. The Ambassador (team_120) propagates this canon + the wrapper script to every spoke on the next
`scripts/aos_sync_all.sh --all`, then broadcasts a context-refresh so active sessions re-read it. Backward
compatible: adds an autonomous path; the human-paste fallback still works for CLI-less engines.

## 9. Calibration-weak validators — the Grok 4.5 addendum (v1.1.0, BINDING)

Some engines are **excellent, cheap, distinct-vendor NETS but poor JUDGES** — high recall, low precision. Grok
4.5 (`xai-via-cursor`, TC-7-only per `REGISTER_ENGINE_xai-via-cursor`) is the first registered case. This
addendum is the operational canon for using such an engine as a validator. Sourced from team_120's research
(two external studies) + team_100's S010 field trial (`§M.12`) — which converged on the same rules independently.

**One-line model:** *use it to widen what you look at, never to decide.* Pair it with a well-calibrated engine;
let Grok cast a wide net cheaply; let the OTHER engine (or your own grounding) judge what is real.

**What it is good at:** high recall + genuine unique findings (in the S010 trial it surfaced 2 real issues GPT-5.5
missed); a true third vendor (xAI ≠ Anthropic ≠ OpenAI — real IR#1 independence); sound at the *verdict* level
(converged GO with GPT-5.5 even while individual findings were noisy); fast, token-efficient, flat-cost (run many
passes cheaply).

**Where it is weak — calibration:** an external study found **10 confident findings, only 2 real (~80%
false-positive)**, stating the false ones with the same confidence as the true; benchmark hallucination rose
**25%→54%** vs the prior Grok; miscalibrated in BOTH directions (the S010 trial caught it *refuting a finding
grounding then proved real*); it invents plausible-but-nonexistent details (fabricated tool-call IDs). Its
findings are an **unranked candidate list, not a trusted verdict.**

| ✅ USE a calibration-weak validator for | ❌ do NOT use it for |
|---|---|
| First-pass / intermediate / in-process validation (TC-7) | The **sole or decisive** gate (TC-8, constitutional/final) — never |
| A cheap, high-volume net-casting pass (free + fast) | Trusting **any individual finding** without independent grounding |
| A **distinct-vendor** third perspective, paired with another engine | High-stakes single-pass "is this safe to ship?" with no per-item grounding |
| One **vote** among engines at the verdict level | Ranking/prioritizing findings by *its own* confidence |

**Operational rules (BINDING):**
1. **Always run it AND another engine, then diff the findings** (doubly-confirmed: field trial + external research).
2. **Ground every finding** — a `file:line` check or a repro — before acting. Candidates to verify, not verdicts.
3. **Trust its verdict as one vote, not its per-finding confidence.**
4. **Keep decisive Tier-2 gates on GPT-5.x / Opus** until real AOS-side calibration data accrues (§4.1).

**Implementation gotchas (Grok via `cursor-agent`):**
- **`--output-format text` silently drops Grok's output** (exits 0, empty stdout) → **use `--output-format json`
  and read `.result`.** Grok also truncates long reports in json (`.result` = progress narration only) — keep the
  report scoped and demand it explicitly.
- Invoke: `cursor-agent --model cursor-grok-4.5-high --mode plan --force --print --output-format json "<prompt>"`.
- **Explicitly demand the final report** in the prompt ("your FINAL assistant message MUST BE the complete
  report as plain text — do not end on a tool call"); Grok in plan mode mishandles structured tool calls.
- The mandate-frontmatter `--` crash is fixed by **PR #39**. Cursor caps its context window at **256K** (relevant
  for very large spec packages). Auth uses the operator's existing Cursor login (may be absent in headless/cron).

### 9.1 Coverage-audit + adversarial FP-guard (Harvest A7 — Train-1)

When a validation package claims ADDRESSED / PARTIAL / COMPLETE across many findings, do **not** accept the
builder's own completeness narrative. Run a cheap first-pass engine to build a **coverage matrix**, then an
independent grounding pass, then a **skeptic / adversarial refute** that tries to break ADDRESSED and PARTIAL
claims (false gaps and rubber-stamp “fixed” both count as defects). Adapt the TikTrack 10-cluster
verify→refute pattern; do not clone ladder-specific matrices wholesale. Disposition SSoT:
`file:///Users/nimrod/Documents/AOS_V5/agents-os/_COMMUNICATION/team_100/HARVEST_DISPOSITION_A1_A10_TRAIN1_2026-07-26_v1.0.0.md`
(asset **A7**).

---
*team_100 (hub) + team_00 | AOS_CROSS_ENGINE_AUTONOMOUS_VALIDATION v1.1.0 | 2026-06-27 (v1.0.0) · amended 2026-07-15 · A7 cite 2026-07-26 | closes ALERT_team_110 · folds in REGISTER_ENGINE_xai-via-cursor*
