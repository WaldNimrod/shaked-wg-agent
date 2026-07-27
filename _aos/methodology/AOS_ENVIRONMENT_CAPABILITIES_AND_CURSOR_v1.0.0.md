---
id: AOS_ENVIRONMENT_CAPABILITIES_AND_CURSOR_v1.0.0
type: METHODOLOGY (environment capabilities catalog — domain-facing)
status: ADOPTED (team_100 2026-07-26; pending team_00 dual-key countersign — content binding for hub; fleet propagation on Train-1)
adoption_note: >
  team_100 adopted 2026-07-26 under the AOS Release Train Uniform Deploy program charter
  (file:///Users/nimrod/Documents/AOS_V5/agents-os/_COMMUNICATION/team_100/PROGRAM_CHARTER_AOS_RELEASE_TRAIN_UNIFORM_DEPLOY_2026-07-26_v1.0.0.md).
  Content is binding for hub operations immediately; fleet-wide read-path wiring (§3b–3d) and
  `_aos/methodology/` snapshot propagation land on Train-1 (v5.2.1). team_00 dual-key countersign
  pending — see ADOPTION artifact in _COMMUNICATION/team_100/.
audience: EVERY AOS team in EVERY environment (hub + all spoke domains)
authored_by: team_120 (Ambassador)
date: 2026-07-25
adopted_on: 2026-07-26
authority_to_adopt: team_100 (Chief Architect) + team_00 (Principal) — dual-key, same as core/config/engines.yaml
supersedes: nothing (new catalog — consolidation PLUS one NEW ruling)
consolidates:
  - core/config/engines.yaml            # engine roster + ENGINE-SELECTION CANON (SSoT for engine facts)
  - governance/directives/ADR046_ENGINE_AND_EXECUTION_TIERING_v1.0.0.md (+ v1.1.0 AMENDMENT)
  - governance/directives/ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS_v1.0.0.md
  - governance/directives/ADR053_TIERED_VALIDATION_MODEL_v1.0.0.md
  - governance/directives/ADR057_VERDICT_ATTESTATION_CHECKABILITY_v1.0.0.md
  - methodology/AOS_CROSS_ENGINE_AUTONOMOUS_VALIDATION_v1.1.0.md
  - methodology/AOS_OPERATING_ENVIRONMENT_v1.0.0.md (§3 environment taxonomy)
  - _COMMUNICATION/team_120/RULING_team_120_CURSOR_CLOUD_ENV_CANON_2026-07-05_v1.0.0.md
  - _COMMUNICATION/team_100/RESEARCH_SUMMARY_team_120_TO_team_100_CURSOR_GATEWAY_2026-07-23_v1.0.0.md (Addenda 4–5)
admits_new_ruling:
  - _COMMUNICATION/team_100/DECISION_CLOUD_DEFAULT_LANE_CLOSED_NICHE_2026-07-26_v1.0.0.md  # LOCAL default; CLOUD = niche
note: >
  This catalog consolidates already-ratified canon AND admits one NEW ruling:
  cloud = niche / local = default
  (DECISION_CLOUD_DEFAULT_LANE_CLOSED_NICHE_2026-07-26). It is not consolidation-only.
  Where a fact is still gated (not yet code-complete) it is marked in the Status Ledger (§9).
  engines.yaml remains the SSoT for engine facts; on any conflict, the cited source wins over
  this summary.
---

# AOS Environment Capabilities & Working with Cursor

**Read this before you pick an engine, launch a build, or run a validation.** AOS v5 is
multi-domain, multi-engine infrastructure. This catalog tells a domain team **what the
environment can do and how to use it** — with Cursor as the headline, because that is where the
most capability and the most live drift both sit. It is written for *every* team in *every*
environment; where your domain has a **LOCKED per-domain override** (see §7), that override wins
for your domain.

---

## 1. Purpose & audience

- **Who:** every AOS team — hub and spoke, every engine, every environment.
- **Why this exists:** engine/venue/budget facts were previously scattered across `engines.yaml`,
  several ADRs, the cross-engine methodology doc, the cursor-cloud RULING, and ad-hoc
  `_COMMUNICATION/` probes. Domains kept **re-discovering Cursor Cloud empirically** instead of
  reading a catalog. This is the catalog.
- **Standing:** **ADOPTED** (team_100, 2026-07-26) as a **base layer for all environments**,
  propagated with governance (Model B / ADR054 — the `methodology/ → _aos/methodology/` snapshot).
  Content is binding for hub; fleet propagation on Train-1 (`v5.2.1`). team_00 dual-key countersign
  pending — until countersigned, spokes may treat hub copy as authoritative preview; cite with
  adoption status from frontmatter.

---

## 2. Engine roster & roles

**SSoT: `core/config/engines.yaml`** (dual-key team_00 + team_100). Model IDs evolve — the live
list is always `cursor-agent --list-models`. Roles below are the *stable* part.

| Engine id | Vendor | Role in AOS | Cost bank (`budget_pool`) |
|---|---|---|---|
| **Claude Code** (`claude-*`) | anthropic | Orchestration, spec, heavy reasoning, **decisive validator** for Cursor/other-vendor builds | Anthropic (direct) |
| **`cursor`** (Composer 2.5) | cursor | Cheap default **builder** + first-pass validation grunt; the "included quota" workhorse | `cursor_flat` (parent `cursor_max_400`) |
| **`xai-via-cursor`** (Grok 4.5) | xai | **DUAL:** (a) first-class **flat-cost executor/builder**; (b) **first-pass validator ONLY** (Tier-1, never decisive-alone) | `cursor_flat` (parent `cursor_max_400`) |
| **`openai-via-cursor`** (gpt-5.x) | openai | **Decisive-tier (Tier-2) validator** — vendor-distinct, valid IR#1 gate for Claude- *and* Cursor-built artifacts | `cursor_api_metered` (parent `cursor_max_400`) |
| **`gemini`** (`cursor_ide_routed`) | google | **First-pass validator ONLY** (4th validator vendor; never sole/decisive) | `cursor_api_metered` (parent `cursor_max_400`) |
| **`codex`** (direct OpenAI CLI) | openai | Decisive validator via the *direct* API — but **daily rate-limited**; prefer `openai-via-cursor` on the Cursor path | OpenAI (direct) |

**Two-bank model (live pools in `core/config/cost_caps.yaml`):** `cursor_flat` = LOCAL first-party
(grok/composer/auto); `cursor_api_metered` = CLOUD / scarce API-bank slice. Both are named pools under
parent `cursor_max_400`. Venue (local vs cloud), not the model label alone, selects the bank.

**Reliability caveats you must respect** (from `engines.yaml` notes, verbatim intent):
- **Grok "cries wolf"** — ~80% false-positive on confident code-review findings; hallucination
  rose 25→54% vs prior Grok. **Never a decisive-gate solo verdict.** Excellent as a *builder*
  (the caveat does not apply to building — microgreens/Blender field-proven).
- **Gemini** — recurring Cursor-specific tool-call reliability history. **First-pass only, paired
  with a decisive-tier engine, findings independently grounded.**
- **The decisive tier stays GPT-5.x-via-cursor / Opus.** First-pass validator *net* today =
  Composer + Grok + Gemini (three flat-pool vendors).

---

## 3. Cross-engine validation (Iron Rule #1 / ADR053)

**The one rule you cannot skip:** the **decisive validator's engine must differ from the
engine(s) that actually BUILT the work package.** It is evaluated **per WP** against the real
builder engine(s) — not a fixed team↔engine pairing (`engines.yaml` ENGINE-SELECTION CANON §2).

- A WP **built by a Claude session** validates fine on **any Cursor engine** (Grok/GPT/Gemini/Composer).
- A WP **built on Cursor** must validate on a **non-Cursor** engine (e.g. Claude, or codex direct).

**Tiers (ADR053, LOCKED):**
- **Tier-0** self-validation (builder validates own work) — **disallowed** at a decisive gate.
- **Tier-1** functional independence — fresh context + adversarial prompt; same-engine *may* be
  acceptable at intermediate gates; different model SHOULD.
- **Tier-2** canonical cross-engine — **different vendor + model_family** at the **decisive gate**
  (STANDARD/MANAGED → L-GATE_VALIDATE; CONTENT → L-GATE_DELIVER).

**How to invoke it (headless):**
- **Sole Cursor path (D1–D2 landed):** `cursor_gateway` / `cursor_gateway_cli` — always
  `--output-format json`; `route_with_policy` wraps `routing_policy.resolve()`.
- `scripts/run_cross_engine_validator.sh` — the wrapper (migrated to json via gateway).
- `/AOS_dispatch --exec` — the command surface.
- **Residuals (see §9):** D3 Cloud MCP facades gated (spend before 2026-08-10 forbidden); D4 full
  anti-drift / field-name dedup still open. Prefer gateway over any direct `cursor-agent` call.

**Verdict recording (ADR057 V-1):** a verdict's `engine:` field takes the **registered engine id**
(`openai-via-cursor`); the model string goes in a **separate `model:` field** (`gpt-5.2-codex`).
Putting the model string in `engine:` is the defect that let a *fabricated* engine name pass
undetected. Never self-sign a dual-key artifact.

---

## 4. Working with Cursor — the two venues (venue = the cost axis)

Cursor is a **multi-engine gateway** (one CLI, `cursor-agent`) with **two venues**. The venue —
**not the model** — decides which budget bank you spend.

### 4a. Local `cursor-agent` (CLI) — the base-bank / default lane *where available*
- Runs at-machine (Mac / a server that has the binary installed and is logged in).
- Bills the **Cursor first-party bucket** (Composer/Grok/`auto` = large included quota, flat cost,
  ~surplus). **This is the default build/validation lane where the binary exists.**
- Auth: `cursor-agent login` (browser OAuth, persistent) is enough for at-machine runs with
  `--trust <worktree>`. **Unattended/scheduled** runs need `CURSOR_API_KEY` / `--api-key`.
- **Always `--output-format json`** and read `.result`. `text` silently drops output.
- Model ids: `cursor-agent --list-models` is the live source. Grok ids today:
  `cursor-grok-4.5-high|-medium|-low` — **`grok-4` is NOT a valid id.**

### 4b. Cursor Cloud (Background Agents, REST) — the API-bank / gated lane
- Programmatic control plane (verified live, 2026-07-23):
  - **Create:** `POST https://api.cursor.com/v0/agents`
    `{prompt:{text}, source:{repository, ref}, target:{autoCreatePr, branchName}, model?}`
  - **Poll:** `GET https://api.cursor.com/v1/agents/{id}/runs/{runId}` → `.result` = full transcript.
  - `/v0` for create, `/v1` for GET/list/status. Create-API model slugs ≠ the `/v1/models` catalog
    (map them).
- Bills the **metered API bank** ($400 pool) — **even when the model is Grok** (venue, not model,
  picks the bank). This bank is **scarce and gated**.
- Integrates via **GitHub PRs** on a `cursor/*` branch; runs under the team_200-style model
  (`OUT_OF_GATE_ISOLATED` + `ISOLATED_BRANCH` + self-QA + **team_90 validation before merge** —
  cursor-cloud RULING 2026-07-05).
- **The `cursor-agent` binary is ABSENT inside the Cloud VM** — in the cloud, the *agent itself*
  performs the LLM steps; you do not shell out to `cursor-agent` there.

### 4c. HARD RULE — never Claude via Cursor
Claude models *are* offered through Cursor (`claude-opus-4-8`, `claude-sonnet-5`, `claude-fable-5`),
so this is a real, enforceable guardrail (team_00 directive): **route any Claude work to the direct
Anthropic engine, never through Cursor** — via Cursor it bills the scarce API bank for no benefit.

---

## 5. Budget policy (current cycle)

- **Frugality until the Aug-10 reset** (team_00). Capped on-demand, **infra-setup only**; **no
  discretionary cloud usage**.
- **Local first-party (Composer/Grok/`auto` via `cursor-agent`) = the DEFAULT lane** (base-bank
  surplus, ~flat cost) — **NEW ruling** (not consolidation-only): see
  `file:///Users/nimrod/Documents/AOS_V5/agents-os/_COMMUNICATION/team_100/DECISION_CLOUD_DEFAULT_LANE_CLOSED_NICHE_2026-07-26_v1.0.0.md`.
- **Cloud = gated / scarce niche**, integrates via GitHub PRs. **Domain/spoke cloud dev work is
  team_00-routed** and, per the current cycle, not authorized as discretionary until after Aug-10.
- **Never Claude via Cursor** (§4c) — it burns the scarce bank.
- **Token accounting (partial, live):** `cursor_gateway.record_cursor_run` + `budget_pool` events
  via `token_economy` — LOCAL runs tag `cursor_flat`. Full two-bank metering / D4 anti-drift is
  still incomplete; operator policy remains required for cloud spend gates.

---

## 6. Other environment capabilities (full-environment, concise)

- **DB-as-SSoT + API** (ADR034 / Iron Rule #7): structured state (WPs, teams, sessions, messaging)
  lives in PostgreSQL behind the **v5 API at `:8092`** (waldhomeserver, Tailscale
  `http://100.125.98.56:8092`). When the DB is online, hub-native structured mutations go via the
  API — snapshots are deploy targets, not hand-edit targets. (Spoke-native `SNNN-PNNN-WPNNN` WPs
  are the file-SSoT exception, ADR034 R9.)
- **Messaging bus + `/AOS_mail`** (DB v2): inter-team mail is DB-backed; `/AOS_mail check` reads +
  flips pending→read. Startup inbox-check surfaces pending mail without operator memory (W4).
- **`/AOS_handoff`** — thin client over the hub prompt-generate API; all engines call the same
  endpoint (Cursor/Codex/Claude Desktop via direct HTTP).
- **Browser-QA / preview** — dev/staging verification via the in-app browser tools (never a manual
  "please check" hand-off).
- **`cursor-cloud` environment** (ADR052 §3 taxonomy; RULING 2026-07-05): a per-domain isolated
  cloud environment; **operator = team_60** (per-domain DevOps; session-overridable
  `engine: cursor-cloud-agent`). *(team_61 was eliminated in roster v1.6.5 — do not cite it.)*
  Each domain fills its own `CURSOR_CLOUD_ENVIRONMENT_TEMPLATE` + `.cursor/environment.json`.
- **MCP profile** — `mcp_profile` in `_aos/metadata.yaml` selects which MCP template lands in
  `.cursor/mcp.json`.

---

## 7. Per-domain overrides (LOCKED decisions win for that domain)

The environment is a **base layer**; a domain may carry a **LOCKED runtime override** that differs
from the fleet default (IR#14 — base + approved override). **The override is authoritative for that
domain.** Know yours before you act.

- **Where they live:** a domain's standing runtime rulings live in its `_COMMUNICATION/team_100/`
  (or `team_110/`) as `DECISION_*` artifacts marked `status: LOCKED`.
- **Worked example — Family-Newsletter (FNL):** `DECISION_team_00_NO_LLM_API_KEY_CLOUD_NATIVE_
  RUNTIME_2026-07-23` (LOCKED) sets, for FNL specifically: **no LLM API key, ever**; all LLM via
  **Cursor Cloud agent-native** models; `cursor-agent` binary absent in the VM; **cost = flat
  subscription**; **BUILD = `cursor-grok-4.5-high`, VALIDATE = Claude**; **Cursor Cloud cannot be
  triggered from a Claude session** (no `CURSOR_API_KEY`) — **Nimrod routes builds**; runtime split
  (Cloud generates → waldhomeserver publishes). For FNL, that ruling overrides the "local
  first-party = default lane" posture in §4a/§5.

> **Discoverability caveat (being fixed):** LOCKED per-domain decisions currently land in
> `_COMMUNICATION/team_100|110/`, which the mandatory session-startup sequence does **not** list.
> Until that read-path is wired (train item, §9), **actively check your domain's
> `_COMMUNICATION/team_100/` for `DECISION_*` (LOCKED) artifacts at session start** — do not rely
> on the guaranteed-read files alone, which may be stale.

---

## 8. Quick-start decision aid

1. **What am I doing?** Build → cheap flat lane (Composer or Grok, local `cursor-agent`, or your
   domain's locked builder). Decisive validate → **different vendor** from the builder (Claude for
   Cursor builds; GPT-5.x-via-cursor / codex for Claude builds). First-pass validate → Grok/Gemini
   (paired, never sole).
2. **Which venue?** Local `cursor-agent` (base bank, default) unless your domain is cloud-native or
   the task genuinely needs cloud fan-out (gated, API bank, PR-integrated).
3. **Cost check.** Local first-party = ~flat/surplus. Cloud = scarce API bank (frugal until Aug-10).
   Never Claude-via-Cursor.
4. **Cross-engine gate.** Confirm the decisive validator vendor ≠ the real builder vendor. Record
   `engine:` = registered id, `model:` = the model string.
5. **Headless hygiene.** `--output-format json` always. Model ids from `cursor-agent --list-models`.

---

## 9. Status ledger — canonical vs in-flight

**CANONICAL (safe to rely on):**
- Iron Rule #1 cross-engine at the decisive gate; ADR053 Tier-0/1/2 model — **LOCKED**.
- Engine registry `core/config/engines.yaml` (dual-key) + registered engines: `openai-via-cursor`
  gpt-5.x (AMENDMENT + team_00 co-sign 2026-07-17), `xai-via-cursor` Grok, `gemini` (cursor_ide_routed).
- Grok dual role (executor + first-pass-only validator); Gemini/Grok never decisive-solo.
- **Venue = cost axis; never Claude via Cursor; budget frugality until Aug-10** (team_00 directives).
- **NEW ruling (2026-07-26):** LOCAL first-party = default lane; CLOUD = niche — see
  `file:///Users/nimrod/Documents/AOS_V5/agents-os/_COMMUNICATION/team_100/DECISION_CLOUD_DEFAULT_LANE_CLOSED_NICHE_2026-07-26_v1.0.0.md`
  (admitted in this catalog; dual-key binds catalog + ruling).
- `cursor-cloud` environment + **team_60** operator model (RULING 2026-07-05).
- **This document** — **ADOPTED** (team_100 2026-07-26; team_00 dual-key countersign pending).
- **Cursor Gateway D1–D2 landed:** sole decisive shell path via `cursor_gateway_cli`;
  `route_with_policy` wraps `resolve()`; `wb_bulk` → Grok; two-bank pools `cursor_flat` /
  `cursor_api_metered` (parent `cursor_max_400`) exist; partial token accounting via
  `record_cursor_run` + `budget_pool`.

**IN-FLIGHT / GATED (do NOT state as fully Done):**
- **`AOS-V5-WP-CURSOR-GATEWAY` residuals:** D3 Cloud MCP facades **gated** (no cloud probe spend
  before 2026-08-10); D4 full anti-drift / `cost_pool`↔`budget_pool` field dedup still open.
- **Read-path wiring** of this catalog into the guaranteed session-startup sequence + spoke
  `.cursorrules` / `CLAUDE.md` templates — Train-1 fleet item (`AOS-V5-WP-ENV-CAPABILITIES`).
- **A5 NEXT-STEP skill** — READY_TO_BUILD (blocks Option-B Done, not mid-stage FREEZE-LIFT).

**SUPERSEDED — do not cite:** any "Cloud by default" framing (closed by
`DECISION_CLOUD_DEFAULT_LANE_CLOSED_NICHE_2026-07-26`); team_61 as cursor-cloud operator
(eliminated — team_60 only); `grok-4` as a model id (invalid — use `cursor-grok-4.5-*`);
`--output-format text`; "gateway not built" / "no code-level Cursor token accounting" (partially
landed — see CANONICAL above).

---

*Authored by team_120 (Ambassador), 2026-07-25 — consolidation + admitted NEW ruling (cloud=niche).
ADOPTED team_100 2026-07-26; team_00 dual-key countersign pending. On any conflict, the cited
source (esp. `core/config/engines.yaml`) wins over this summary.*
