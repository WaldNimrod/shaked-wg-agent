---
id: ADR055
title: Tunable Platform Canon Locality (hub-file SSoT + DB read-projection + anti-drift, hub-only)
status: ACCEPTED
date: 2026-06-17
deciders: [team_00 (Principal), team_100 (Chief Architect)]
authority: IR#12 (governance-authority lockdown — team_00 + team_100)
authored_on_branch: feat/v5-m7-adaptive-routing (M7 isolated worktree)
effective: on merge to the v5 spine / main (becomes live governance then; see §Effectivity)
relates_to: [ADR034 (data authority DB-SSoT), ADR054 (governance distribution Model B), ADR046/047 (engine matrix)]
source: M7-P1-WP3 config-locality study (LOD100 report)
version: 1.0.0
---

# ADR055 — Tunable Platform Canon Locality

## Status
ACCEPTED (team_00 + team_100, 2026-06-17). Authored on the M7 isolated branch; effective on merge (§Effectivity).

## Context
AOS already has two clear data-authority rules but a **gap between them**:
- **ADR034 / IR#7** — *operational, per-instance structured state* (WP/team/project status) is **DB-SSoT**, mutated via API.
- **ADR054 (Model B) / IR#10/#11** — *governance/methodology/lean-kit content spokes must execute locally* is a
  **propagated snapshot** (git-ignored cache + version stamp), flowing source→snapshot one-directionally.

Between them sits a third, unnamed category: **tunable platform canon** — configuration-as-data that (a) is platform-wide
(not domain-specific), (b) a live surface (the cockpit) must DISPLAY and a resolver must QUERY, (c) is agent-edited /
tuned-in-field, and (d) needs anti-drift enforcement. Today this category is handled **inconsistently**:
`core/config/engines.yaml` + `cost_caps.yaml` are pure hub files (no DB, no drift-check, not propagated), while
`CANON_COCKPIT_ENUMS` is dual-realized (doc + DB seed) guarded by a **bidirectional BLOCKING drift check (Check 53)**.
The M7 `CANON_WP_ROUTING_POLICY` needs a home, and the divergence must be resolved. (M7-P1-WP3 study.)

## Decision
**Tunable platform canon** (the engine matrix, cost caps, the WP routing policy, and config-as-data like them) is:
1. **Hub-file-canonical** — the authoring SSoT is a YAML file under **`core/config/`** (e.g. `engines.yaml`,
   `cost_caps.yaml`, `routing_policy.yaml`), carrying a **dual-key authority header (team_00 + team_100)**.
2. **DB read-projection when a live surface needs it** — if the cockpit must display it and/or a resolver must query it,
   a **DB read-projection** is generated (seeded like the enums table) and exposed via a thin canon-style read endpoint
   (mirroring `canon_service.list_enums` → `/enums`). The cockpit READS the projection; it never hardcodes and never
   authors.
3. **Bound by a bidirectional anti-drift check** — a `validate_aos.sh` check asserts **bidirectional set-equality**
   between the file and its projection (the **Check 53 pattern**), BLOCKING on drift. The file's checked key namespace
   MUST be **flat/enumerable**; free-form value bodies (e.g. rule `when:` expressions) are value-compared, not enumerated.
4. **Hub-only — NOT propagated to spokes.** Spokes receive only the *outcome* (their WP's assigned engine/process/
   validation/environment) via the hub API; they never hold the canon file. (This is the `engines.yaml` precedent and
   keeps IR#10/#11 trivially satisfied — no reverse flow is even possible.)
5. **Authority split:** *tuning values within the locked schema* = an ordinary agent/config edit (the whole point of
   "config-as-data, tunable in-field"); *schema/structure changes* = dual-key (team_00 + team_100).

**Boundary with the two existing rules:** operational per-instance state stays **DB-SSoT (ADR034/IR#7)**; content spokes
must execute locally stays a **propagated Model-B snapshot (ADR054)**; tunable platform canon is this **third category**
(hub-file SSoT + optional DB read-projection + anti-drift, hub-only).

## Consequences
- `engines.yaml` and `cost_caps.yaml` become **retroactively conformant** (they were already hub-file, dual-key,
  hub-only; they simply lacked the named category and, where a live surface reads them, the projection + drift check).
- `core/config/routing_policy.yaml` (M7) gets a **named home** with a defined read-path + anti-drift contract.
- A new `validate_routing_policy.py` check (Check-53 clone) is added at build for `routing_policy.yaml`.
- **Offline survivability:** because the file is the SSoT, the hub resolver can read it from disk when the DB is down
  (the projection is only for the cockpit read API) — strictly better than DB-SSoT for routing availability.
- Per-domain overrides (rare) are NOT forks of the file; they ride the generic `policies` table (scope=DOMAIN, priority)
  **after IR#14 sign-off**. `project_type` absorbs most domain variation, so base-only ships first.

## Alternatives considered (M7-P1-WP3 §3)
- **(A) DB table as SSoT** — degrades agent-edit/tune-in-field (mutate prod to experiment, no git diff-review) and
  weakens the anti-drift check into self-consistency (no second pole). Rejected for tunable canon.
- **(B-propagated) hub file propagated via Model-B snapshot** — unnecessary: routing canon is hub-evaluated; pushing it
  to 9 spokes creates stale copies for zero benefit. Rejected (collapses to hub-only).
- **Chosen: hub file SSoT + DB read-projection + bidirectional anti-drift, hub-only.**

## Effectivity
Authored on the M7 isolated branch (`feat/v5-m7-adaptive-routing`). It becomes **live governance on merge** to the v5
spine / main. If the spine needs the locality decision sooner (e.g. for M3 cockpit/config work), it may be cherry-picked
— a team_00 routing decision.

## References
M7-P1-WP3 config-locality study; M7-P1-WP1 routing-model LOD300 (§5/§8/§9); ADR034 (+R9/R10); ADR054 (Model B);
ADR046/047 (engine matrix); CANON_COCKPIT_ENUMS + Check 53 (`validate_canon_enums.py`); IR#7/#10/#11/#12/#14.
