# AOS Fix-Cycle Discipline — Methodology Canon
**Version:** v1.0.0 | **Status:** ACTIVE
**Approved by:** team_00 (Principal) 2026-05-05 | **Authored by:** team_100 (hub)
**Evidence source:** GCR_AOS_HUB_METHODOLOGY_INTEGRATION_FRAGILITY_v1.0.0.md (team_110, 2026-05-05)
**Path:** methodology/AOS_FIX_CYCLE_DISCIPLINE_v1.0.0.md

---

## 1. Purpose & Scope

A **fix cycle** is any remediation sprint triggered after a confirmed production or integration failure — where the primary deliverable is a targeted correction rather than new feature delivery.

This canon applies when:
- A WP re-enters build after gate failure or production incident
- Three or more sequential fix attempts are made on the same integration surface
- An incident postmortem identifies a systemic (not one-off) root cause

This canon supplements the standard WP LOD lifecycle for remediation phases. It does NOT replace LOD gates — it adds minimal discipline within them.

---

## 2. Preconditions — Before Writing Any Code

Before the first line of a fix cycle changes, the following must exist **in writing** (WP note, sprint issue, or spec delta):

1. **Reproduction artifact** — exact command + logs that reproduce the failure
2. **Minimal failing case** — reduced reproduction with minimal surface area
3. **Impacted surfaces listed** — which modules, files, and system boundaries are in scope

If these three do not exist, the **first task** of the fix cycle is to produce them. Producing them counts as an iteration. No code is written until all three are present.

---

## 3. Minimal Change Rule

Each fix cycle iteration MUST:

- Address **one logical hypothesis** — one root cause candidate per iteration
- Include an **explicit rollback path** documented before merge
- Document the **assumption being tested** in the commit message or WP note

If a fix requires touching more than two independent subsystems, it is no longer a fix cycle — it is a new sprint requiring LOD200 delta review.

---

## 4. Integration Checklist — Five Fragility Patterns

Before merging **any** fix cycle change, verify the following. Each unchecked item blocks merge.

### F1 — Cross-system transactions

Cross-system write = any change that updates two or more durable systems (PostgreSQL, filesystem, outbound HTTP/API, message queues) without a shared two-phase commit.

- [ ] All durable systems modified in this change are identified
- [ ] A single writer boundary is defined per logical operation
- [ ] Failure compensation / rollback is documented where more than one system is written

**Discipline:** Define single-writer scope; use outbox/idempotent retries where async delivery is needed; document failure modes before merging.

### F2 — SQL parser / dynamic SQL surface

- [ ] No new dynamic SQL string composition without parameterization
- [ ] ORM version or dialect change? → treated as parser-surface change with expanded tests
- [ ] "SQL surface touched?" gate: any change to DB query paths requires diff review

**Discipline:** Prefer parameterized, reviewable queries; treat ORM migrations as contract changes requiring diff against the parser/exec path.

### F3 — Lazy-init and lifecycle contracts

- [ ] No new module-level singletons that reach the DB before bootstrap completes
- [ ] Startup order dependencies documented in the WP note or spec delta
- [ ] Cold-start test added or existing test covers the changed init path

**Discipline:** Centralize factories and explicit bootstrap phases; forbid hidden singletons that assume ambient environment before app wiring completes.

### F4 — Async / greenlet boundaries (FastAPI + SQLAlchemy async stack)

- [ ] Session-per-request boundary maintained — no shared mutable session across coroutines
- [ ] No `await` across a lock tied to synchronous ORM internals
- [ ] Concurrency model stated explicitly in the commit when touching the DB layer

**Discipline:** Session-per-request (or per unit-of-work) with explicit lifecycle; document any bridge across sync/async boundaries before shipping.

### F5 — `try/except` scope versus transaction scope

- [ ] No catch-all handler wrapping a commit without explicit written justification
- [ ] Exception handler is narrow (I/O boundary) — does not cover the full unit-of-work
- [ ] Rollback policy is applied before any error suppression

**Discipline:** Keep `try/except` at I/O boundaries; transaction context managers own success/failure; re-raise or convert to typed errors after rollback policy is applied.

---

## 5. Engine & Gate Hygiene

### Builder discipline

Each fix iteration ships with a **written assumption log** (startup order, concurrency model, rollback path) — minimum one sentence per assumption, in the commit message or WP note. The reviewer must be able to understand the hypothesis from the commit message alone.

### Validator independence (Iron Rule #1 enforcement at fix gates)

Validators at integration-sensitive gates MUST use **fresh or explicitly bounded context**:

- A long-running session that observed multiple build iterations is NOT an independent validator for the final gate.
- If a validator session has been active for more than one fix iteration on the same WP, the gate assessment MUST note this explicitly.
- Team 100 may require a fresh validation session for L-GATE_BUILD at their discretion if conformity risk is assessed.
- **Bounded context** = validator reads only the spec artifact and the final diff — not the iterative session history.

This reinforces Iron Rule #1 (builder engine ≠ validator engine) for remediation scenarios where the same validator session may have drifted toward the builder's narrative.

---

## 6. Closure Criteria

A fix cycle is CLOSED when all of the following are satisfied:

1. Reproduction command from §2 now returns no failure
2. Integration checklist (§4) is checked and the completed checklist is committed to the WP artifact
3. A test or monitor exists that will catch regression — or an explicit note explains why one is not feasible
4. The fix is merged and deployed; if server-side, the executing team confirms via REPORT artifact
5. LOD note updated: `"fix cycle N — closed YYYY-MM-DD"`

---

## Annex A — Five-Pattern Reference Table

| Pattern ID | Short name | Checklist item |
|-----------|-----------|----------------|
| A.1 (team_110 GCR) | Cross-system transactions | F1 |
| A.2 (team_110 GCR) | SQL parser / dynamic SQL | F2 |
| A.3 (team_110 GCR) | Lazy-init lifecycle | F3 |
| A.4 (team_110 GCR) | Async / greenlet | F4 |
| A.5 (team_110 GCR) | try/except vs transaction | F5 |

---

## Annex B — Application to Hub Context

This canon was motivated by five fix cycles on WP002-class integration work (TikTrack spoke, 2026-05). The patterns are universal across AOS-managed codebases using FastAPI + SQLAlchemy + async. Any spoke or hub WP that enters a fix phase of ≥3 iterations SHOULD apply this canon.

Cross-repo session discipline (spoke sessions do not write hub `methodology/` directly) is what makes a hub methodology canon necessary: lessons surface in `_COMMUNICATION/` artifacts, but without a canon they recur in the next WP.

---

*Canon approved: team_00 (Principal) + team_100 (Chief Architect) | 2026-05-05*
*Evidence: GCR_AOS_HUB_METHODOLOGY_INTEGRATION_FRAGILITY_v1.0.0.md (team_110 | 2026-05-05)*
*Next review: when a new fragility pattern appears in ≥2 independent spokes*
