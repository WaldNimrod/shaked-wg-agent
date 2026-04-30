---
id: ADR046_ENGINE_AND_EXECUTION_TIERING_AMENDMENT
title: "ADR-046 v1.1.0 Amendment — access_method + surface Enum Extensions for Cursor Entry Points"
version: "1.1.0"
amendment_to: ADR046_ENGINE_AND_EXECUTION_TIERING_v1.0.0.md
status: ACTIVE
author: team_110 (builder; WP W2 AOS-V4-WP-ENGINE-MATRIX; engine: claude-sonnet-4-6)
approved_by:
  - team_100 (Chief Architect)
  - team_00 (Principal)
approval_date: "2026-04-30"
type: ADDENDUM                        # v1.0.0 content preserved; this is additive only
scope: access_method enum extension + surface enum extension (both additive)
adr_ref: ADR-046 §2.4
wp: AOS-V4-WP-ENGINE-MATRIX (W2)
see_also:
  - governance/directives/ADR046_ENGINE_AND_EXECUTION_TIERING_v1.0.0.md
  - core/config/engines.yaml v1.0 (new engine entries consuming these enum values)
  - governance/directives/ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS_v1.0.0.md
---

# ADR-046 Amendment v1.1.0 — access_method + surface Enum Extensions

**Amendment type:** Addendum — v1.0.0 content is fully preserved and not altered.
This document extends two enums in ADR046 to support new Cursor entry points
registered in `core/config/engines.yaml` v1.0:
- §2.4 `access_method` enum — 4 new values (sdk, cursor_ide_routed, cursor_ide_cloud, cursor_ide_bg)
- The engine `surface` enum — 2 new values (`cloud`, `ide`) covering Cursor's async-cloud and IDE-background execution surfaces

---

## 1. Context

ADR046 v1.0.0 §2.4 defined the `access_method` enum with 7 values:
`mcp`, `mcp_wrapper_around_api`, `manual_hybrid`, `api`, `cli_via_bash`, `subscription_chat`, `mobile_dispatch`.

The v4.0.0 engine matrix (W2 AOS-V4-WP-ENGINE-MATRIX) introduces four Cursor-specific engine entry points that require distinct `access_method` values:
- `cursor-ide` — human-driven Cursor IDE manual hybrid (distinct from generic `manual_hybrid`)
- `cursor-cloud-agent` — async sandboxed Cloud Agents (no IDE attachment)
- `cursor-background-agent` — IDE Background Agents (IDE-attached background execution)
- `cursor-sdk` — Cursor SDK direct API call (token-consumption billing; separate pool)

Generic `manual_hybrid` and `api` values are insufficient to distinguish these execution modes.
This amendment adds four new enum values to cover them precisely.

---

## 2. Amendment — New access_method Enum Values

The following four values are **added** to the `access_method` enum defined in ADR046 §2.4:

| Value (new) | Definition | Authorized for | Billing pool |
|---|---|---|---|
| `sdk` | Cursor SDK (`@cursor/sdk`) direct API call; programmatic, token-consumption billing; NOT the IDE | cursor-sdk engine; conditional (enabled: false default) | cursor_sdk_overflow (separate pool) |
| `cursor_ide_routed` | Cursor IDE manual hybrid; human-operated IDE session; subscription-pool billing | cursor-ide engine; teams with Cursor IDE access | cursor_max_400 |
| `cursor_ide_cloud` | Cursor Cloud Agents; async sandboxed execution; no IDE attachment required; subscription-pool billing | cursor-cloud-agent engine; teams with Cursor Pro/Ultra subscription | cursor_max_400 |
| `cursor_ide_bg` | Cursor Background Agents; IDE background execution; non-blocking for foreground work; subscription-pool billing | cursor-background-agent engine; teams with Cursor IDE access | cursor_max_400 |

---

## 3. Complete Updated Enum (ADR046 §2.4 — as amended)

The complete `access_method` enum after this amendment (v1.1.0) is:

| Value | Definition | Status |
|---|---|---|
| `mcp` | Direct MCP server invocation | v1.0.0 — unchanged |
| `mcp_wrapper_around_api` | MCP server wrapping an underlying API | v1.0.0 — unchanged |
| `manual_hybrid` | User-operated browser + paste-back | v1.0.0 — unchanged |
| `api` | Direct API SDK invocation | v1.0.0 — unchanged |
| `cli_via_bash` | Shell invocation via Bash tool | v1.0.0 — unchanged |
| `subscription_chat` | Browser/desktop subscription session | v1.0.0 — unchanged |
| `mobile_dispatch` | Mobile app via team_98 dispatch | v1.0.0 — unchanged |
| `sdk` | Cursor SDK direct API call; token-consumption billing | **v1.1.0 NEW** |
| `cursor_ide_routed` | Cursor IDE manual hybrid; subscription-pool billing | **v1.1.0 NEW** |
| `cursor_ide_cloud` | Cursor Cloud Agents; async sandboxed; subscription-pool billing | **v1.1.0 NEW** |
| `cursor_ide_bg` | Cursor Background Agents; IDE background; subscription-pool billing | **v1.1.0 NEW** |

---

## 4. IR#1 Implications

No change to IR#1 enforcement logic. The new access_method values are execution-surface distinctions,
not vendor-identity distinctions. IR#1 vendor-distinctness continues to be checked via
`underlying_models[].vendor` + `underlying_models[].model_family` (ADR046 §2.5 — unchanged).

For all four new Cursor entry points: `underlying_models[].vendor = cursor`. This means:
- Cursor engines CANNOT serve as IR#1 validators for other cursor-built artifacts.
- Cursor engines CAN serve as builders when the validator uses a different vendor (openai, anthropic, google).

---

## 5. Engines Consuming These Values (engines.yaml v1.0)

| engine_id | access_method value used | default_method |
|---|---|---|
| `cursor-ide` | `cursor_ide_routed` | `cursor_ide_routed` |
| `cursor-cloud-agent` | `cursor_ide_cloud` | `cursor_ide_cloud` |
| `cursor-background-agent` | `cursor_ide_bg` | `cursor_ide_bg` |
| `cursor-sdk` | `sdk` | `sdk` |

All four entries are in `core/config/engines.yaml` v1.0, filed 2026-04-30.

---

## 6. Schema Change — Applicability

This amendment applies to:
- `core/config/engines.yaml` — new engine entries use the new enum values
- `lean-kit/modules/project-governance/templates/REGISTER_ENGINE.md.template` — template §3 includes the full updated enum table
- Any future REGISTER_ENGINE form for Cursor-surface engines must use these values

W3 (AOS-V4-WP-ENGINE-ADAPTER) will consume the full updated enum when building the EngineAdapter ABC.
No runtime code exists yet; no conflict possible before W3 ships.

---

## 7. Surface Enum Extension (additive — addresses W2 r1 external finding)

ADR046 v1.0.0 defined the engine `surface` enum (§ schema example) as:
`<api | cli | desktop | mobile | mcp_server | manual_web>` — 6 values.

The Cursor cloud/background entry points introduced in `engines.yaml` v1.0 require two new surface values:

| Value (new) | Definition | Engines using it | Status |
|---|---|---|---|
| `cloud` | Async sandboxed execution; no IDE attachment; runs in vendor-managed cloud sandbox | `cursor-cloud-agent` | **v1.1.0 NEW** |
| `ide` | Engine runs in IDE process / IDE background while a human works elsewhere on the same desktop | `cursor-background-agent` | **v1.1.0 NEW** |

Complete updated `surface` enum after this amendment (v1.1.0):

`<api | cli | desktop | mobile | mcp_server | manual_web | cloud | ide>` — 8 values.

**Why both** (vs collapsing to existing values): `cloud` is distinct from `api` because the workload runs in a vendor sandbox with its own filesystem and tools, not just an HTTP request/response. `ide` is distinct from `desktop` because it runs *inside* an IDE process (Cursor Background Agents), not as a standalone desktop app.

## 8. What Is NOT Changed

Per the amendment constraint (ADR046 §8.2 equivalent):
- No existing `access_method` value (`mcp`, `mcp_wrapper_around_api`, `manual_hybrid`, `api`, `cli_via_bash`, `subscription_chat`, `mobile_dispatch`) is modified, deprecated, or renamed.
- No existing `surface` value (`api`, `cli`, `desktop`, `mobile`, `mcp_server`, `manual_web`) is modified, deprecated, or renamed.
- No tier classification (§2.2) is changed.
- No per-team access rule (§2.3) is changed (new engine entries establish their own per-team rules).
- No routing rule (ADR047) is changed by this amendment; new fallback chain entries are added only to the engines.yaml entries themselves.
- ADR046 v1.0.0 `status: LOCKED` content is fully preserved.

---

## 9. Revision History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.1.0 | 2026-04-30 | team_110 (builder, WP W2 AOS-V4-WP-ENGINE-MATRIX, engine: claude-sonnet-4-6) | Addendum — 4 new access_method enum values for Cursor engine entry points (sdk, cursor_ide_routed, cursor_ide_cloud, cursor_ide_bg) |

---

*Amendment to ADR046 v1.0.0 (LOCKED 2026-04-27). Amendment is additive only — v1.0.0 content unchanged.*
*Filed by team_110 per W2 LOD200 spec §5 (CREATE: ADR046 v1.1.0 amendment) — 2026-04-30*
