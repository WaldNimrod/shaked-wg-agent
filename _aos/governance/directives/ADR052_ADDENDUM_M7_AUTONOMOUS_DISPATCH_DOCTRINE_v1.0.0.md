---
id: ADR052_ADDENDUM_M7_AUTONOMOUS_DISPATCH_DOCTRINE
extends: ADR052_AOS_OPERATING_ENVIRONMENT_AND_SESSION_MODEL_v1.0.0.md (Decision #5 — Phase-1/2 promotion model)
status: ACCEPTED (2026-06-19) — co-signed team_00 (Nimrod) + team_100 (IR#12 governance-authority lockdown)
authority: team_00 (Principal) + team_100 (Chief Architect)  # IR#12 — BOTH required to APPLY
authoring_team: team_100
wp: M7-P2-WP2-autonomous-dispatch-doctrine
date: 2026-06-19
---

# ADR052 — Addendum (M7): Autonomous Dispatch Doctrine

> **Status: PROPOSED / DRAFT.** This addendum extends ADR052 **Decision #5** (the Phase-1/2 promotion model).
> It is on the `build/v5-m7-production` branch as the M7-P2-WP2 deliverable and **changes nothing** until
> team_00 + team_100 co-sign (IR#12). The mechanism it governs (M7-P2-WP1) is already built and structurally
> incapable of gate-advance/merge (M7-P2-WP1 AC-18, grep-proven).

## Doctrine (one line)
**"Autonomous to the gate, human at the gate."**

## A. Principle
Server-resident sessions MAY execute autonomously up to a decisive gate. **Gate-advancement, destructive
operations, main-merge, and cross-engine (Tier-2) validation REMAIN human-initiated.** A woken session MUST NOT
self-perform a decisive validation (including via a same-engine sub-agent) — it STOPs and captures (§D). The
human-in-the-loop belongs at gates/approvals, not in routine transport ("stop the copy-paste" removes the human
from transport, not from decisions).

| Capability | Disposition | Basis |
|---|---|---|
| Execute OPS/build work, self-clear `L-GATE_BUILD` | **PERMITTED** (autonomous-execution) | `definition.yaml:712` (team_99 `L-GATE_BUILD: delegated`) |
| Event-gated wake of a non-live server session | **MODERNIZE** (M7-P2-WP1) | was the only gap — nothing woke the session |
| **Gate advancement** (VALIDATE/DELIVER) | **KEEP HUMAN** | `definition.yaml:713` (`L-GATE_VALIDATE: awareness_only`) |
| **Destructive ops** (restart/delete/redeploy) | **KEEP HUMAN** | `definition.yaml:722` |
| **Merge to main** | **KEEP HUMAN** | `definition.yaml:726` |
| **Cross-engine (Tier-2) validation** | **KEEP HUMAN** | IR#1 decisive gate |

## B. Wake
Server sessions are woken **EVENT-GATED** — only on a proven, approved, server-domain bus item — by a bounded
server-local dispatcher (`aos-server-dispatcher`) whose **sole authority is wake**; its fire payload is
**`/AOS_mail check` only**. **No interval-poll wakes a model session** (the IDLE-WAIT COUNT is NON-LLM, zero
model tokens — correct hygiene regardless of billing regime). The dispatcher reads `headless_billing_mode`
(default `subscription`; the 2026-06-15 headless→API split is PAUSED) and contains **no gate-advance or merge
call**. Billing floor (HARD): **packages-only, NEVER pay-per-use API**; the woken session is **bounded
per-work-item** (not one eternal `--continue`) — drains the deliverable(s), executes to a decisive gate,
captures, and ends.

## C. Phase model
**Phase-1 (this milestone): visible-first** — every wake, STOP, and queued verdict is surfaced to team_00
(inbox + cockpit). No automatic gate-advance, ever. **Phase-2 (future, not now):** promotion of any *specific*
mechanism to a more-automatic posture is an **explicit, per-mechanism team_00 decision recorded as an ADR
amendment — never an emergent default.** The dispatcher must not contain a code path that could auto-advance a
gate even if mis-configured (enforced: M7-P2-WP1 AC-18).

### C.1 Phase-2 promotion criteria (team_00, 2026-06-19 — OQ-B resolved; define-now)
Promoting a *specific* mechanism to auto-advance a *named* gate is justified ONLY when **ALL** hold (absent any
one → stays Phase-1). Defining the bar here does **not** enable Phase-2 — each promotion still needs its own
per-mechanism team_00 ADR amendment.
1. **Track record:** the mechanism ran Phase-1 (visible-first) over **≥20 real gate-events with ZERO incidents**
   — no wrong advance, no missed STOP, no human override needed (evidence = the cockpit/inbox audit trail).
2. **Gate class:** the target is a **non-decisive, low-risk** gate (e.g. `L-GATE_BUILD` on EXPRESS/OPS where the
   builder self-clears) — **NEVER** a decisive cross-engine gate (`L-GATE_VALIDATE`/`DELIVER`, IR#1), destructive
   op, or main-merge.
3. **Bounded scope:** the promotion names the **exact (gate, track, risk-tier ≤ 2)** it covers — never blanket.
4. **Reversible kill-switch:** a single config flag instantly reverts to Phase-1 (human-at-gate), and every
   auto-advance writes an audit row + is visible in the cockpit.
5. **Explicit ADR:** recorded as a per-mechanism ADR052 amendment — never emergent, never a default.

## D. Guardrail
On reaching a KEEP-HUMAN action a session **STOPS**, captures a `verdict`/`handoff` to team_00's inbox
(`messages.capture`) with the gate + WP + a verdict summary + a recommended next action, and **ends** (does not
block, does not retry the gate). The human later advances via `/AOS_gate-status → POST /api/runs/{id}/advance`
(unchanged human path). The dispatcher and the woken session are **structurally incapable** of
gate-advance/merge.

## Application checklist (on team_00 + team_100 co-sign — IR#12)
1. Fold A–D into `ADR052_..._v1.0.0.md` Decision #5 (or as a numbered addendum reference).
2. Governance-text reconciliations already on this branch (M7-P2-WP2 §7): `core/governance/team_99.md`
   (legacy filesystem-inbox path annotated SUPERSEDED) + `.claude/commands/AOS_mail.md` ("No *unbounded
   interval* watcher; the M7 dispatcher is event-gated"). These become canonical on the Stage-1 merge.
