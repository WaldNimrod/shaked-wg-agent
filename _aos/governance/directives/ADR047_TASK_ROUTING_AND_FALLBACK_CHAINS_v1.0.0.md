---
id: ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS
title: "ADR-047 — Task Class Catalog + Default Routing + Fallback Chains"
version: "1.0.0"
status: LOCKED
author: Team 100 (Chief Architect)
approved_by:
  - team_00
  - team_100
approval_date: "2026-04-27"
companion: ADR046_ENGINE_AND_EXECUTION_TIERING_v1.0.0
adr_ref: ADR-047
based_on:
  - "_COMMUNICATION/team_80/MERGED_M2_CURSOR_canonical_2026-04-25_v1.0.0.md"
  - "_COMMUNICATION/team_80/MERGED_M3_COWORK_canonical_2026-04-25_v1.0.0.md"
  - "_COMMUNICATION/team_80/INCOMING_claude_chat_M3_RECOMMENDATION_M2_TC8_REVISION_2026-04-25_v1.0.0.md"
---

# ADR-047 — Task Class Catalog + Default Routing + Fallback Chains

ADR047 covers: task class catalog, default routing matrix (per Q/C/S dominant axis), per-team override decision tree, deterministic fallback chains with `exhausted_signal` enum, re-evaluation triggers. Engine matrix + per-team access rules live in ADR046 (companion).

---

## 1. Status & Context

**Status:** LOCKED v1.0.0 (promoted 2026-04-27 with team_00 approval)
**Companion:** ADR046 (engine matrix + per-team access)

**Why split from ADR046:** different change cadences. Engine matrix changes rarely (new engine = REGISTER_ENGINE form). Routing rules change quarterly per re-review trigger. Cowork ops change with Anthropic releases. Separating concerns matches AOS modular pattern (ADR034 R-addenda; engines.yaml + cost_caps.yaml + cowork_session_parameters.yaml all separate).

---

## 2. Decisions

### 2.1 Task Class Catalog (TC-1 through TC-12 + TC-12 sub-classes)

Working set v0.1 — per Claude Chat M-2 REVISED §2 + M-3 §2 sub-class refinement. team_100 confirms completeness/granularity.

| ID | Task Class | Typical AOS context | Stakes | Context size | Dominant axis |
|---|---|---|---|---|---|
| **TC-1** | Tab autocomplete during typing | Any builder team in IDE | LOW | tiny | SPEED |
| **TC-2** | Single-file mechanical refactor | Builder during build phase | LOW | small | COST + SPEED |
| **TC-3** | Multi-file mechanical refactor (≤5 files) | Builder at L-GATE_BUILD | LOW-MED | medium | COST |
| **TC-4** | Multi-file logical refactor (>5 files OR semantic change) | Builder under MANAGED track | MED | large | QUALITY + COST |
| **TC-5** | LOD400 authoring (templated, build-ready spec) | team_170 / spec engine | MED | medium | COST |
| **TC-6** | LOD200/LOD300 architecture | team_100 / team_110 | HIGH | large | QUALITY |
| **TC-7** | First-pass code review | team_50 / team_90 | LOW-MED | medium | SPEED + COST |
| **TC-8** | Final-pass / constitutional validation | team_190 (cross-vendor required) | HIGH | large | QUALITY |
| **TC-9** | Repeated test runs / iteration loops | Builder during BUILD | LOW | small per run | COST + SPEED |
| **TC-10** | Headless CI / batch validation | DevOps / pipeline engine | MED | varies | COST + reliability |
| **TC-11** | Live web research | team_80 (Research) | MED | medium | reliability + freshness |
| **TC-12** | Strategic synthesis / Cowork bundle | team_200 (Cowork) | HIGH | very large | QUALITY × context |
| **TC-12.1** | LOD300 authoring (sub-class of TC-12) | team_100 / team_110 | HIGH | very large | QUALITY × context |
| **TC-12.2** | Multi-doc strategic synthesis (governance review, ADR drafting) | team_100 | HIGH | very large | QUALITY × context |
| **TC-12.3** | Design pass with mockup review | team_35 / team_100 | MED-HIGH | very large | QUALITY × speed (chat loop) |
| **TC-12.4** | Long-running autonomous (>90 min uninterrupted) | Builder | varies | varies | COST × independence (NOT Cowork — exceeds cap) |

### 2.2 Default Routing Matrix (per dominant axis)

| TC | Default engine | Default mode | Rationale |
|---|---|---|---|
| TC-1 | `cursor` | composer-tab | Best-in-class IDE; effectively free in plan |
| TC-2 | `cursor` | manual mode | Surgical edits; lowest credit/value ratio |
| TC-3 | `cursor` | composer agent on cheap model | Flat-rate tier absorbs volume |
| TC-4 | `claude-code` | sonnet, terminal-managed | Long-context reasoning critical |
| TC-5 | `cursor` | composer agent (cheap model) | Templated, low-context |
| TC-6 | `claude-code` | sonnet, terminal-managed | Strategic depth; Cursor weak here |
| TC-7 | `cursor` (composer ask) **OR** `claude-haiku-4-5` | depends on team | Both viable; per-team default |
| TC-8 | **per-team** — see §2.4 below | depends on builder vendor + per-team access | IR#1 binding |
| TC-9 | `cursor` | composer agent (cheap model) | High-frequency, low stakes |
| TC-10 | `claude-code` **OR** `claude-haiku-4-5` | terminal-managed | Cursor CLI MCP CI gap → AVOID Cursor |
| TC-11 | `perplexity` (MCP); `gemini` fallback | MCP via `perplexity_ask` | Web-grounded; team_80 default |
| TC-12.1 | `claude-desktop` | Cowork bundle (team_200) | RAG + Memory + chat-native UX |
| TC-12.2 | `claude-desktop` | Cowork bundle | Multi-doc synthesis |
| TC-12.3 | `claude-desktop` | Cowork bundle | Chat-native design loop |
| TC-12.4 | `claude-code` | terminal-managed (NOT Cowork — exceeds 90-min cap) | Open-ended session length |

### 2.3 Override Decision Tree (per AOS v3 UI override mechanism)

```
DEFAULT (engines.yaml routing)
  ↓
PER-PROJECT OVERRIDE (project-level config; e.g., TikTrack vs agros-insite)
  ↓
PER-TEAM OVERRIDE (team-level config; e.g., team_80 vs team_50)
  ↓
PER-WP OVERRIDE (rare; case-by-case via team_lead approval)
  ↓
RUNTIME ENGINE (effective for this WP execution)
```

**Override is operational** — NOT governance. Project leads override based on actual workflow (subscription tier, peak hours, quality floor failures). ADR047 governs the *default* and *override schema*, not specific override choices.

### 2.4 Fallback Chains per Task Class (with `exhausted_signal` enum)

`exhausted_signal` enum:

| Signal | Meaning | Action |
|---|---|---|
| `out_of_credits` | primary engine credit pool depleted for billing cycle | advance chain |
| `rate_limited` | primary engine throttling (transient) | retry primary after cooldown OR advance |
| `timeout` | primary engine non-responsive past SLA | advance |
| `quality_floor_failure` | validator verdict: primary output failed minimum quality bar | advance |
| `anthropic_budget_depleted` ⭐NEW (M-3) | Anthropic shared pool HARD BLOCK; no soft throttle, no model downgrade | advance — special handling |
| `peak_hour_scarcity` ⭐NEW (M-3) | within 8am-2pm ET weekday window | advisory — defer non-urgent |
| `memory_pollution_risk` ⭐NEW (M-3) | governance signal | route to fresh-project |

#### Fallback chains per TC

| TC | Primary | F1 | F2 | F3 | F4 | F5 |
|---|---|---|---|---|---|---|
| TC-1 | `cursor` (tab) | `claude-code` (inline) | manual / no-completion | — | — | — |
| TC-2 | `cursor` (manual) | `claude-code` | `claude-haiku-4-5` | manual | — | — |
| TC-3 | `cursor` (agent cheap) | `claude-code` | `claude-haiku-4-5` | manual | — | — |
| TC-4 | `claude-code` | `codex` | `cursor` (Composer w/ caution) | manual + escalate | — | — |
| TC-5 | `cursor` (cheap) | `claude-haiku-4-5` | `claude-code` | manual | — | — |
| TC-6 | `claude-code` | `codex` | `claude-desktop` (Cowork) | manual + escalate | — | — |
| TC-7 | `cursor` OR `haiku` | `claude-code` | `codex` | manual review | — | — |
| **TC-8 — see §2.5 per-team** | per-team divergent | per-team | per-team | per-team | — | — |
| TC-9 | `cursor` (cheap) | `claude-haiku-4-5` | `claude-code` | manual | — | — |
| TC-10 | `claude-code` | `claude-haiku-4-5` | `codex` | manual / fail-CI | — | — |
| TC-11 | `perplexity` (MCP) | `gemini` | `claude-code` (with web tool) | manual research | — | — |
| TC-12.1 | `claude-desktop` (Cowork) | `claude-code` (terminal) | `claude-desktop` fresh-project (Memory reset) | `claude-code` (access_method=api, bypass subscription) | `codex` (access_method=mcp_wrapper_around_api, vendor-distinct per RULING-2) | manual escalation |
| TC-12.2 | same as TC-12.1 | | | | | |
| TC-12.3 | same as TC-12.1 | | | | | |
| TC-12.4 | `claude-code` | `codex` parallel | `claude-haiku-4-5` | manual escalate | — | — |

### 2.5 TC-8 Per-Team Fallback Chain (cross-mandate revision, R2-2 reconciled)

Per `INCOMING_claude_chat_M3_RECOMMENDATION_M2_TC8_REVISION_*` (accepted in principle), and reconciled against ADR046 §2.3 `accessible_to_teams` matrix (R2-2 / F2 fix). Chain entries below honor `accessible_to_teams` exactly — no chain step grants broader access than the engines.yaml contract permits.

**Access reminder (per ADR046 §2.3 + engines.yaml):**

| Engine | team_80 | team_50 | team_90 | team_190 | team_10 | team_100 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `cursor` | ❌ | ✅ | ✅ | ❌ (constitutional → premium only) | ✅ | ✅ via Bash |
| `gemini` | ✅ MCP only | ❌ | ❌ | ❌ | ❌ | ✅ |
| `codex` | ✅ via MCP wrapper | ✅ | ✅ | ✅ | ✅ | ✅ |
| `claude-haiku-4-5` | ✅ MCP only | ✅ | ✅ | ✅ | ✅ | ✅ |

**Builder = claude-vendor (Anthropic):**

| Team | Primary | F1 | F2 | F3 |
|---|---|---|---|---|
| **team_80 (MCP-only)** | `codex` (access_method=mcp_wrapper_around_api, RULING-2) | `gemini` (access_method=mcp, vendor-distinct — team_80 has gemini-MCP access) | manual escalation to team_00 | — |
| **team_50 / team_90** | `codex` (direct API or wrapper) | `cursor` (Bash + cursor-cli, vendor-distinct — team_50/90 have cursor access) | `claude-haiku-4-5` is INVALID (same-vendor as claude-builder = IR#1) — effectively skipped | manual escalation |
| **team_190 (Constitutional)** | `codex` (direct API or wrapper) | `claude-haiku-4-5` is INVALID (same-vendor as claude-builder = IR#1) — effectively skipped (cursor + gemini NOT accessible to team_190 per ADR046 §2.3) | manual escalation | — |
| **team_10 / team_100** | `codex` | `cursor` (vendor-distinct; both teams have access) | `claude-haiku-4-5` is INVALID (same-vendor as claude-builder = IR#1) — effectively skipped | manual escalation |

> **Note on team_190 chain shallowness:** team_190 is the Senior Constitutional Validator and per ADR046 §2.3 has access only to `claude-*`, `codex`, and `claude-haiku-4-5`. When the builder is also Anthropic, only `codex` remains as a vendor-distinct option. The chain depth reflects operational reality #1 (OpenAI daily blocks) — F1 manual escalation when codex is exhausted is the honest depiction, not a gap.

**Builder = openai-vendor (Codex):**

| Team | Primary | F1 | F2 | F3 |
|---|---|---|---|---|
| **team_80** | `claude-code` is INVALID for team_80 (no API access; not MCP-reachable) — start from `claude-haiku-4-5` | `claude-haiku-4-5` (access_method=mcp; vendor-distinct from openai-builder) | `gemini` (access_method=mcp, vendor-distinct) | manual escalation |
| **team_50 / team_90 / team_190 / team_10 / team_100** | `claude-code` (vendor-distinct from openai-builder) | `claude-haiku-4-5` (vendor-distinct) | manual escalation | — |

**Builder = cursor-vendor (rare):**

| Team | Primary | F1 | F2 |
|---|---|---|---|
| **team_50 / team_90 / team_190 / team_10 / team_100** | `claude-code` (vendor-distinct) | `codex` (vendor-distinct; all listed teams have codex access) | manual escalation |
| **team_80** | `claude-haiku-4-5` (access_method=mcp; vendor-distinct) | `codex` (access_method=mcp_wrapper_around_api) | manual escalation |

**Critical:** EngineAdapter MUST validate vendor-distinctness at runtime per ADR046 §2.5 (model provenance check) AND validate `accessible_to_teams` membership for each chain step before selecting it. Static config validation at engines.yaml load time is insufficient — chain selection happens dynamically based on (a) builder vendor of the artifact, and (b) requesting team's access matrix. A chain step that names an engine the team cannot access MUST be skipped at runtime, not silently bypassed at config load.

### 2.6 Anthropic Budget Depletion Special Handling (CRITICAL — from M-3)

When `anthropic_budget_depleted` triggers in any chain, the advance is **NOT vendor-preserving** by default — it's vendor-changing because:

1. All Anthropic engines (claude-code, claude-desktop, claude-haiku) share the same shared pool
2. HARD BLOCK on consumer subscription means F1-F2-F3 within Anthropic vendor are ALL blocked simultaneously
3. Recovery requires either: (a) wait for reset, (b) API direct billing (bypass subscription), (c) vendor-change to OpenAI/Gemini

**Required EngineAdapter logic:**

```
on anthropic_budget_depleted:
  IF current TC has F4 = api_direct_billing:
    advance to F4 (same vendor, different billing)
  ELIF current TC has F4 = vendor-distinct (e.g., codex with access_method=mcp_wrapper_around_api):
    check operational reality:
      IF openai_service_blocked (daily reality):
        advance to F5 (manual escalation)
      ELSE:
        advance to F4
  ELSE:
    advance to manual escalation
```

This handling is documented separately because the failure mode is structurally different from `out_of_credits` of a single engine.

### 2.7 Re-Evaluation Triggers

Per Decision: routing matrix is **re-evaluable** quarterly + on specific triggers. NOT runtime drift detection (per team_00 simplification directive).

| Trigger | Action | Owner |
|---|---|---|
| Quarterly cycle (every 90 days; next 2026-07-25) | Full re-review of routing matrix | team_80 (research) + team_100 (review) |
| Cursor / Anthropic / OpenAI ships major release | Targeted re-review of affected entries | team_80 |
| New engine added via REGISTER_ENGINE | Add to matrix + re-eval fallback chains where new engine fits | team_100 |
| Practitioner consensus shift (>3 posts in 30 days reporting axis change) | Targeted re-review | team_80 |
| Credit-exhaustion event ≥3× same project in a month | Local override review at project level + global default review if pattern widespread | team_lead → team_100 |

**Each routing rule entry must carry `last_reviewed_at`** for audit. NO runtime change-awareness automation (per team_00 directive).

---

## 3. Consequences

### 3.1 Positive

- 16 task classes (TC-1..12 + TC-12.1-4) cover known AOS work shapes
- Default routing is explicit + reasoning-attributed
- Per-team override + per-team fallback chains acknowledge AOS reality
- `anthropic_budget_depleted` first-class signal handles HARD BLOCK semantics
- IR#1 enforcement preserved across full fallback chain depth

### 3.2 Negative / Costs

- 16 task classes is more than initial 12; complexity for routing logic
- Per-team fallback chains × 4-5 teams × 16 TCs = ~64-80 chain configurations
- TC-8 per-team divergence is real complexity but unavoidable given operational reality #1

### 3.3 Risks

| Risk | Mitigation |
|---|---|
| Fallback chain validation: how do we test in production? | OPEN-O-7 → propose chain-validation test harness as separate WP |
| F4 OpenAI conditional on service uptime | Real failure mode acknowledged; F5 manual escalation is the de-facto floor |
| TC catalog evolves over time | Quarterly re-review absorbs additions |
| `anthropic_budget_depleted` cascade across all TCs simultaneously | Documented special handling §2.6 |

---

## 4. Cross-References

| Topic | Artifact |
|---|---|
| Engine matrix + tier defs + per-team access | `governance/directives/ADR046_ENGINE_AND_EXECUTION_TIERING_v1.0.0.md` |
| Cowork operational config | `_aos/config/cowork_session_parameters.yaml` |
| Research evidence M-2 | `_COMMUNICATION/team_80/MERGED_M2_CURSOR_canonical_*` |
| Research evidence M-3 | `_COMMUNICATION/team_80/MERGED_M3_COWORK_canonical_*` |
| Cross-mandate TC-8 revision rationale | `_COMMUNICATION/team_80/INCOMING_claude_chat_M3_RECOMMENDATION_M2_TC8_REVISION_*` |
| OPEN items | `_COMMUNICATION/team_80/OPEN_ITEMS_TRIAGE_2026-04-25_v1.0.0.md` |

---

*Promoted 2026-04-27 with team_00 approval. Authored by team_100; canonical placement by team_110.*
