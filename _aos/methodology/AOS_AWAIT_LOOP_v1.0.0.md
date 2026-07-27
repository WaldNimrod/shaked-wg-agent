---
id: AOS_AWAIT_LOOP
title: AOS Await-Loop — the named env-native "wait for the next event" process (cost-policy: bias-cheap)
version: 1.0.0
status: CANON
authority: [team_00, team_100]
wp: M9-P1-WP6 (PROJECT v5-completion / WP2)
date: 2026-06-24
supersedes: ad-hoc per-session polling (e.g. the b4wz0ofgx-style hand-rolled canary poll)
---

# AOS Await-Loop

**Problem it names.** Across v5 the orchestrator must *wait for the next event* — a verdict, a handback,
a mandate answer — without a Claude session burning tokens by interval-polling. The mechanisms to do this
cheaply all SHIP already, but they were unnamed and assembled ad-hoc per session (the canary's
hand-rolled poll, D6). This canon gives the assembly **one name** + **one cost-policy** so every
orchestrator/session awaits the same cheap way.

## 1. The components (all already shipped — this canon UNIFIES, it does not rebuild)

| Layer | Component | Role | Cost |
|---|---|---|---|
| **Push** | SSE stream `GET /api/events/stream` (+ `notify_*` emitters) | the live map / cockpit / a bounded session is PUSHED on a verdict/handoff/status change | ~0 (server push) |
| **Event-gate** | `scripts/aos_server_dispatcher.py` (M7-P2-WP1) | a NON-LLM `COUNT(deliverable & pending)` on a modest interval wakes a bounded session **only when count>0** (debounced, single-flighted, cooled-down). Two instances: server ssh-wake + Mac team_100 notify-wake. | ~0 model tokens (pure HTTP→SQL) |
| **Board** | `GET /api/orchestration/open-turns` · `/outstanding` · `/open-loops` (CC-04) | "what is waiting on whom" — one read the orchestrator runs each beat instead of N inbox checks | one cheap read |
| **Liveness** | `POST /api/sessions/heartbeat` + TTL | a session is live/stale without anyone watching it | one cheap write |
| **Local hop** | `ccd_session_mgmt` (native Claude-Code session↔session) | a queued user-turn with one-tap confirm for LOCAL live handoff | local-only, no bus |

## 2. The cost-policy (bias-cheap) — the ORDER of preference

When you need to "await", pick the **cheapest mechanism that suffices**, in this order:

1. **SSE push** — if a UI/bounded session is open, let it be pushed. Never poll what SSE already pushes.
2. **Event-gated dispatcher wake** — for an unattended recipient (server / Mac team_100 inbox), let the
   dispatcher's NON-LLM count wake a bounded session. The wake payload is the literal `/AOS_mail check`
   and nothing else.
3. **One board read** (`open-turns`/`open-loops`) on a *modest* interval — when an attended orchestrator
   beats the loop, read the board ONCE per beat, not N inbox checks.
4. **Long-interval poll** — only as a last resort, and only of the cheap board endpoints (never of a
   model session). Bias toward longer intervals; the prompt-cache TTL (~5 min) is the natural breakpoint.

**Forbidden (D6):** an interval-poll *of a Claude session* (re-invoking a model just to ask "is it done
yet?"). That is what this loop exists to obviate — the canary's hand-rolled `b4wz0ofgx`-style poll is the
anti-pattern. If you find yourself re-prompting a model to check status, you are using the wrong layer.

## 3. The named process

**`scripts/aos_await_loop.sh`** is the one env-native entry point. It runs the cheap board read
(`open-turns` + `open-loops`) at a bias-cheap cadence and prints what is waiting + any SLA-breached open
loop — so an orchestrator (or a human) consults ONE process to know "what now", instead of hand-rolling a
poll. It NEVER wakes/advances/merges (that authority is the dispatcher's `wake` + the orchestrator's
explicit gate calls). Degrade-safe: DB-down → a degraded marker, never a crash.

```
scripts/aos_await_loop.sh [interval_seconds=300] [sla_seconds=86400]
```

## 4. Acceptance (D1–D5)

- **D1** the await-loop has ONE name + ONE entry point (`aos_await_loop.sh`), not per-session ad-hoc poll.
- **D2** the cost-policy order (§2) is canon; SSE/dispatcher preferred over poll; no model-session poll.
- **D3** the board read is a single cheap call per beat (`open-turns`/`open-loops`), degrade-safe.
- **D4** the dispatcher (event-gated, NON-LLM count) is the canonical unattended waker — unchanged, named.
- **D5** D6 (hand-rolled canary poll) is obviated: the named loop + dispatcher replace it.

## 5. Notes
- This is **NOT spine** — it is the parallel "how we wait cheaply" canon. The shipped mechanisms are
  unchanged; v1.0.0 only *names + sequences* them and adds the thin `aos_await_loop.sh` entry point.
- Locality: HUB canon; propagated to spokes read-only like all `_aos/` governance.
- Related: [[project_v5_m7_state]] (the dispatcher origin), CC-04 (open-loops SLA), COMM-03/CC-02
  (the two dispatcher instances).
