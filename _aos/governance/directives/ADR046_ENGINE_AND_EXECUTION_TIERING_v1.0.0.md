---
id: ADR046_ENGINE_AND_EXECUTION_TIERING
title: "ADR-046 — Engine Matrix + Tier Definitions + Per-Team Access"
version: "1.0.0"
status: LOCKED
author: Team 100 (Chief Architect)
approved_by:
  - team_00
  - team_100
approval_date: "2026-04-27"
supersedes: "Plan v2.0 §5.1 placeholder"
companion: ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS_v1.0.0
adr_ref: ADR-046
based_on:
  - "_COMMUNICATION/team_80/MERGED_M2_CURSOR_canonical_2026-04-25_v1.0.0.md"
  - "_COMMUNICATION/team_80/MERGED_M3_COWORK_canonical_2026-04-25_v1.0.0.md"
  - "_COMMUNICATION/team_80/DIRECTIVE_TEAM_80_MCP_DEFAULT_2026-04-25_v1.0.0.md"
  - "_COMMUNICATION/team_80/STRATEGIC_INPUT_T80_QUALITY_VS_COST_FALLBACK_2026-04-25_v1.0.0.md"
---

# ADR-046 — Engine Matrix + Tier Definitions + Per-Team Access

ADR046 covers: engine identity (matrix entries), tier classification, per-team access rules, IR#1 enforcement at the engine level, and access-method governance. Routing rules + task class catalog + fallback chains live in ADR047. Cowork operational config lives in `_aos/config/cowork_session_parameters.yaml`.

---

## 1. Status & Context

**Status:** LOCKED v1.0.0 (promoted 2026-04-27 with team_00 approval)
**Supersedes:** Plan v2.0 §5.1 placeholder
**Companion:** ADR047 (routing + fallback chains)

**Context:** AOS v4.0.0 charter requires a configurable, extensible engine matrix where every WP can declare its engine + execution mode + tier, with per-team override and cost-cap awareness. This ADR locks the matrix entries and access governance.

---

## 2. Decisions

### 2.1 Engine Matrix v2 (canonical)

| Engine ID | Name | Vendor | Surface | Tier | Q/C/S profile | Default modes | Notes |
|---|---|---|---|---|---|---|---|
| `claude-haiku-4-5` ⭐ | Claude Haiku 4.5 | Anthropic | API / claude-code | cheap | Q=MED / C=HIGH / S=HIGH | batch validation, summary, triage | universal cheap fallback; `claude-haiku-4-5 (haiku)` |
| `cursor` | Cursor (Composer) | Cursor | IDE + cursor-cli | cheap-grunt+automation | Q=MED / C=HIGH (flat-rate) / S=HIGH (in-IDE) | composer Manual / Agent / Ask / Custom; cursor-cli `/debug` `--force`; Background Agents | NOT for research; CLI MCP CI gap; Cursor 3 = up to 8 worktrees; **NOT MCP server** |
| `claude-code` | Claude Code (Sonnet) | Anthropic | terminal / IDE | premium | Q=HIGH / C=MED / S=MED | terminal-managed, inline | strategic build + long-context; subscription billing |
| `codex` | Codex (GPT-5) | OpenAI | API / cli / app | premium | Q=HIGH / C=MED / S=MED | second-opinion QA, parallel sprints | **operational reality**: blocked daily (rate-limited); MUST plan around |
| `gemini` | Gemini | Google | API / chat | premium | Q=HIGH (long-context) / C=MED / S=MED | research synthesis, long-doc analysis | MCP availability: client-only as of Apr 2026 |
| `perplexity` ⭐ | Perplexity (Sonar Pro) | Perplexity | MCP server (official) | research-live | Q=MED-HIGH (web-grounded) / C=HIGH / S=HIGH | live web research; `perplexity_ask` (NOT `_research`) | **first official engine MCP-native**; M-4 install complete |
| `notebooklm` ⭐ | NotebookLM | Google | manual web | research-synth | Q=HIGH (long synthesis) / C=HIGH (free in plan) / S=LOW | source-grounded multi-doc synthesis | manual web only — no MCP / API |
| `claude-desktop` | Claude Desktop (Cowork) | Anthropic | Desktop app | premium-chat | Q=HIGH / C=MED / S=MED | Cowork bundles only (team_200) | 90-min wall-clock cap; HARD BLOCK on quota; Memory governance per IR-11 |
| `claude-design` | Claude Design Sandbox | Anthropic | sandbox | sandbox-only | Q=HIGH / C=MED / S=MED | team_35 design artifacts | HTML / wireframes / prototypes |
| `claude-sonnet-4-6 (mobile)` | Claude Mobile | Anthropic | Phone Joker / Dispatch | premium-mobile | Q=HIGH / C=MED / S=MED | team_98 mobile dispatch | ISOLATED_BRANCH; post-hoc validation by team_190 |

**Extensibility:** New engines registered via `REGISTER_ENGINE_<engine>_v1.0.0.md` form (per Plan §5.1) → team_100 review → team_00 approval → matrix update.

### 2.2 Tier Classifications

| Tier | Definition | Members |
|---|---|---|
| **cheap** | Low cost per output unit; for batch / triage / cheap-fallback | claude-haiku-4-5 |
| **cheap-grunt+automation** | Cheap-tier + automation surface (CLI / Background Agents); IDE-bound work | cursor |
| **premium** | High-quality reasoning; subscription or per-request paid | claude-code, codex, gemini |
| **premium-chat** | Premium quality + chat-native UX; bounded by subscription | claude-desktop |
| **premium-mobile** | Premium quality + mobile dispatch surface | claude-sonnet-4-6 (mobile) |
| **research-live** | Web-grounded current-state research; MCP-native | perplexity |
| **research-synth** | Source-grounded long-context synthesis; manual surface | notebooklm |
| **sandbox-only** | Isolated sandbox; not for production | claude-design |

### 2.3 Per-Team Access Rules (`accessible_to_teams`)

| Engine | team_80 (Research) | team_50 (QA) | team_90 (Validate) | team_190 (Constitutional) | team_200 (Cowork) | team_35 (Design) | team_98 (Mobile) | team_10 (Cursor-native) | team_100 (Architect) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| claude-haiku-4-5 | ✅ MCP only | ✅ | ✅ | ✅ | — | — | — | ✅ | ✅ |
| cursor | ❌ (not MCP-reachable) | ✅ | ✅ | ❌ (constitutional → premium) | — | ✅ | — | ✅ | ✅ via Bash |
| claude-code | ❌ (no API) | ✅ | ✅ | ✅ | — | — | — | ✅ | ✅ default |
| codex | ✅ via OpenAI MCP wrapper | ✅ | ✅ | ✅ | — | — | — | ✅ | ✅ |
| gemini | ✅ MCP only | — | — | — | — | — | — | — | ✅ |
| perplexity | ✅ MCP (default) | — | — | — | — | — | — | — | ✅ MCP |
| notebooklm | ✅ manual hybrid | — | — | — | — | — | — | — | manual |
| claude-desktop | ❌ (Cowork=team_200 only) | — | — | — | ✅ EXCLUSIVE | — | — | — | — |
| claude-design | — | — | — | — | — | ✅ EXCLUSIVE | — | — | — |
| claude-sonnet-4-6 (mobile) | — | — | — | — | — | — | ✅ EXCLUSIVE | — | — |

### 2.4 Access Methods (`access_method` enum)

| Value | Definition | Authorized for |
|---|---|---|
| `mcp` | Direct MCP server invocation | universal — preferred when MCP available |
| `mcp_wrapper_around_api` | MCP server that wraps an underlying API | universal — wrapper interpretation per RULING-2 |
| `manual_hybrid` | User-operated browser + paste-back | when MCP unavailable; team_80 fallback |
| `api` | Direct API SDK invocation | NOT for team_80 (cost containment); other teams as needed |
| `cli_via_bash` | Shell invocation via Bash tool | not MCP-shaped; reserved for Cursor/Codex shell wrappers |
| `subscription_chat` | Browser/desktop subscription session | claude-desktop (Cowork); claude.ai web |
| `mobile_dispatch` | Mobile app via team_98 dispatch | claude-sonnet-4-6 (mobile) only |

**Schema for engines.yaml entry:**

```yaml
- id: <engine_id>
  name: <product_name>
  vendor: <vendor>
  surface: <api | cli | desktop | mobile | mcp_server | manual_web>
  tier: <tier_classification>
  axis_profile:
    quality: LOW | MED | HIGH
    cost: LOW | MED | HIGH
    speed: LOW | MED | HIGH
  access_methods:
    - <access_method_enum>
    # primary first
  default_method: <access_method_enum>
  accessible_to_teams:
    team_80: <true | false | conditional_with_method>
    team_50: <true | false>
    # ...all relevant teams
  default_for_task_classes: [TC-N, ...]   # see ADR047
  fallback_chain_membership: [TC-N (position), ...]   # see ADR047
  exhausted_signals_observable:
    - out_of_credits
    - rate_limited
    - timeout
    - quality_floor_failure
    - anthropic_budget_depleted   # per ADR047
    - peak_hour_scarcity          # advisory
    - memory_pollution_risk       # governance, claude-desktop only
  cost_pool: <provider>           # for credit accounting
  empirical_burn_anchor: <url>    # [empirical-pending] tier evidence if applicable
  last_reviewed_at: 2026-04-25
```

### 2.5 IR#1 Enforcement at Engine Level (model provenance)

> **see_also ADR053:** This §2.5 vendor/model_family distinctness check is the **Tier-2** test; ADR053 §4 specifies **which gates per track** require it (decisive gates), vs gates that may run Tier-1 functional (sub-agent) independence.

> **Iron Rule #1:** builder engine ≠ validator engine. Per Decision M-2 C24:

The check must compare **vendor + model_family**, not just `engine_id`. Both Cursor and Claude Code may use Sonnet underneath — same vendor + same model = IR#1 violation if used as builder/validator pair.

**Required engine.yaml field:**

```yaml
underlying_models:
  - name: <model_name>          # e.g. claude-sonnet-4-5
    vendor: <vendor>             # e.g. anthropic
    model_family: <family>       # e.g. claude-sonnet
```

EngineAdapter enforces vendor-distinctness on `vendor` field at runtime; advisory on `model_family` for stricter cases (e.g., final constitutional gate per CUR-ADR-8).

### 2.6 Team_80 Engine Access Rules (per DIRECTIVE_TEAM_80_MCP_DEFAULT)

**Rule 1 (refined):** Method recommended per case (MCP / manual hybrid / mixed / API-with-reason); team_00 approves before execution.

**Rule 2 (refined):** API access discouraged by default — limited credit pools across providers must be reserved for production work. Override permitted with reasoning + team_00 approval. All API-mode invocations log to `team_80_api_usage` ledger.

**Rule 3:** Pre-approval template at every research start (see DIRECTIVE §3).

---

## 3. Consequences

### 3.1 Positive

- Engine matrix is canonical, comparable, and extensible
- Per-team access rules eliminate routing confusion (team_80 ≠ team_10 chains)
- `access_method` enum makes MCP/API/manual distinction observable
- IR#1 enforcement uses vendor+model_family, robust to model-fanout (Cursor/Claude Code on same Sonnet)
- engines.yaml is a single SSoT readable by EngineAdapter (S006 M6.2)

### 3.2 Negative / Costs

- engines.yaml grows substantially (~10 entries × ~20 fields each)
- Per-team access rules require care at engine registration (REGISTER_ENGINE form must include team-access table)
- Underlying-models tracking adds governance overhead — but necessary for IR#1

### 3.3 Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Engine race shifts (new model / pricing) | Quarterly re-review per ADR047 §3.4; REGISTER_ENGINE form for new entrants |
| API access creep for team_80 (override abuse) | `team_80_api_usage` audit ledger; team_00 must approve each override |
| `cursor` access for team_80 escalation | Documented unavailable; manual escalation to team_00 is the canonical path |
| MCP wrapper grey-zone interpretation | RULING-2: MCP wrapper = MCP-compatible; documented with reason + audit |

---

## 4. Cross-References

| Topic | Artifact |
|---|---|
| Task class catalog + routing rules | `governance/directives/ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS_v1.0.0.md` |
| Cowork operational config | `_aos/config/cowork_session_parameters.yaml` |
| Cost caps configuration | `core/config/cost_caps.yaml` (per Plan §5.4) |
| REGISTER_ENGINE template | `lean-kit/modules/project-governance/templates/REGISTER_ENGINE.md.template` |
| team_80 governance | `core/governance/team_80.md` (Rules 1-3) |
| team_200 governance | `core/governance/team_200.md` v2.0.0 (IR-11..14) |
| Research evidence | `_COMMUNICATION/team_80/MERGED_M2_CURSOR_canonical_*` + `MERGED_M3_COWORK_canonical_*` |
| Cross-mandate naming correction | `INCOMING_claude_chat_M2_RECOMMENDATION_NAMING_*` (composer not composer-2) — accepted in principle |

---

*Promoted 2026-04-27 with team_00 approval. Authored by team_100; canonical placement by team_110.*

---

**see_amendment:** `governance/directives/ADR046_ENGINE_AND_EXECUTION_TIERING_v1.1.0_AMENDMENT.md`
*Amendment v1.1.0 (2026-04-30) — additive only; extends `access_method` enum with 4 new Cursor entry point values: `sdk`, `cursor_ide_routed`, `cursor_ide_cloud`, `cursor_ide_bg`. This v1.0.0 document content is unchanged.*
