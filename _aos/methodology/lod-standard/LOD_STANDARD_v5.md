---
lod_document_type: STANDARD
id: LOD_STANDARD_v5
version: v5.1.0
status: RELEASED
supersedes:
  - methodology/lod-standard/TEAM_100_LOD_STANDARD_v0.2.md
  - methodology/lod-standard/TEAM_100_LOD_STANDARD_v0.3.md
  - methodology/lod-standard/TEAM_100_LOD_STANDARD_DELTA_v0.1_to_v0.2.md
  - methodology/lod-standard/TEAM_100_LOD_STANDARD_DELTA_v0.2_to_v0.3.md
  - methodology/gate-model/LOD_STANDARD_v1.0.0.md
authoring_team: team_100
authority: Team 00 (Principal)
enum_ssot: _aos/v5_characterization/synthesis/CANON_COCKPIT_ENUMS_v1.0.0.md
spec_ref: _aos/v5_characterization/characterization/CA14_CHARACTERIZATION_CANON_v2.0.0.md
milestone_ref: AOS-V5-M2
date: 2026-06-16
released: 2026-07-03 — team_100 executed RC→release promotion (v5.0.0/RELEASE_CANDIDATE → v5.1.0/RELEASED) per §12.2; team_00 sign-off DECISION_AOS-V5-M10-APPLY-SIGNOFFS 2026-07-02 (AOS-V5-M10 closure)
---

# LOD Standard for Software & Agentic Systems — v5

> **Single canonical house.** This document is the one live LOD Standard for AOS v5. All prior versions
> (`TEAM_100_LOD_STANDARD_v0.2/v0.3` + deltas, and the stray `gate-model/LOD_STANDARD_v1.0.0`) are archived
> read-only under `_archive/lod-standard-pre-v5/` (see §14). Gate, track, LOD, and status **names** are not
> defined here — they are referenced from the single enum source of truth,
> [`CANON_COCKPIT_ENUMS`](../../_aos/v5_characterization/synthesis/CANON_COCKPIT_ENUMS_v1.0.0.md) (W7 / L20).
> v5 uses **named gates only** (`LOD_CHECK · SPEC · BUILD · VALIDATE · CLOSE · DELIVER`); legacy numeric gate
> identifiers are deprecated and read-only (§7).

---

## §0 — Purpose & scope

**LOD (Level of Development / Level of Detail)** comes from architecture and construction, where it defines
the precision to which a building element is modeled at a given stage. This standard adapts it to software
and agentic systems.

> **LOD in software/LLM systems = the degree to which a feature, flow, system, or task is defined strongly
> enough to support aligned execution with minimal ambiguity.**

This standard serves:
- product and software teams of any size;
- multi-agent / LLM builder pipelines;
- specification-heavy environments with handoffs between producers and executors;
- any system where the cost of specification ambiguity exceeds the cost of specification effort.

It is **cross-project and cross-environment**. It specifies *what a definition must contain at each stage* and
*which gate evaluates it* — it does **not** describe autonomy, auto-advance, or a particular runtime. Deployment
differences (how a gate is enforced) are isolated in §3; they never change the specification requirement itself.

---

## §1 — Why this standard exists (cognitive origin)

LOD is not a tool adopted onto the work; it is the **natural cognition of the work made explicit**. Two
questions sit at the very front of anything worth building, before any solution thought:

1. **Taste — "is this worth wanting at all?"** (מטעים) — value before everything else.
2. **Consequences — "what does this move, and what breaks?"** (השלכות) — *a bug in the design is a bug in the
   debug* ("באג בדיזיין זה זיין בדיבג"). Get the framing wrong and every downstream cost compounds.

These two checks are the foundation of LOD100 (§5.1). The rest of the ladder is the same instinct extended:
spend specification effort exactly where ambiguity would otherwise become expensive, and no earlier or later
than necessary. LOD200 is the **last cheap checkpoint** — the real go/no-go before tokens and money are burned.

The standard exists because, without an explicit ladder, definition either arrives too late (build starts on a
guess) or masquerades as more certain than it is (a concept dressed up as a spec). Both failures are expensive;
both are preventable by naming the level and the gate.

---

## §2 — Core principle

### §2.1 — The level ladder

Each level answers a different question:

| Level | Question | Essence |
|-------|----------|---------|
| **LOD100** | What problem are we solving and why — and is it worth wanting? | Intent + **taste & consequences** verdicts (§5.1) |
| **LOD200** | What kind of solution, and at what cost ceiling? | Concept · **the cheap point** + `cost_cap` (§5.2) |
| **LOD300** | How should the system behave — and is it feasible? | System behavior + **feasibility gate** *(track-aware — §5.3)* |
| **LOD400** | What exactly must be built, shown, enforced, and verified? | Zero-ambiguity buildable spec + **N×4 / functional-DoD** (§5.4) |
| **LOD500** | What was actually implemented, verified, and is true now? | As-built · cold-integration + regression passed (§5.5) |

**The critical distinction between LOD400 and LOD500:** LOD400 is *prescriptive* (what must be); LOD500 is
*descriptive* (what is). A LOD500 that exactly matches its LOD400 is the ideal outcome; deviations must be
documented.

### §2.2 — Three pillars at every gate

Every gate decision answers up to three independent questions. Conflating them is how weak work passes:

| Pillar | Question | Who answers |
|--------|----------|-------------|
| **Judgment** | *Should we?* — taste, consequences, go/no-go, deploy | **team_00** (human) — value without a formula |
| **Compliance** | *Does it follow the rules?* — LOD level, IR#1, canon, spec-match | Validator (agent; cross-engine at the decisive gate) |
| **Correctness / Quality** 🎯 | *Does it actually work?* — build runs, tests assert real behavior, browser-QA, cold-integration, regression | Builder + harness; verified externally |

Correctness is the **core** pillar — the one most easily faked by ceremony. The definition of "working" is
team_00's: *accurate user experience · accurate interface · accurate data · all layers behave across all
scenarios* — not "tests passed," but **the product is good end-to-end**.

### §2.3 — Every gate validates reality, not ceremony

A gate exists to check a fact about the world, not to produce a document. Each gate names the reality it
verifies (the full table is in §6): a feasibility gate proves an uncertain component actually works before the
spec locks; a build gate proves cold-integration (fresh-clone + merge + regression), not a green checkmark.
**Regression caught early is a gate success, not a failure** — surfacing "wrong concept" at LOD200 or "wrong
behavior" at LOD300 is exactly what the ladder is for.

### §2.4 — Maker ≠ checker

No team is the sole validator of its own output. The decisive gate of any work package is performed by a
**different engine** than the one that built it (Iron Rule #1, tiered per ADR053 — see §10). This is structural,
not a matter of discipline.

---

## §3 — Deployment Profiles

AOS v5 recognises two deployment profiles. Profile selection is a project-level infrastructure decision — it does not change the methodology, the LOD levels, or the gate requirements.

| Profile | Name | Infrastructure | Enforcement Mechanism |
|---------|------|---------------|----------------------|
| **L0** | Lean / Manual | None — no persistent services required | Human orchestrator routes work; documents are the authoritative state record |
| **L2** | Cockpit + DB | Cockpit dashboard + PostgreSQL | Pipeline / cockpit enforces gates; state is tracked in the database |

### L-tier is an installation capability — not an autonomy ladder

"L-tier" describes **how much infrastructure is installed**, nothing more. It is not a progression from "manual" to "autonomous". There is no implication that L2 projects are more advanced, more mature, or operating at a higher standard than L0 projects. A team running L0 is not on a path to L2 — it may simply not require persistent infrastructure.

### L1 and L3 are out of scope for v5

Profiles L1 and L3 are deferred and recorded in the governance ledger. They are **not part of this standard**. No tooling, gate logic, or methodology text in v5 references them as active deployment targets.

### No auto-advance — gates are enforced

There is no `CANONICAL_AUTO` mode and no auto-advance behaviour in v5. Every gate — `LOD_CHECK`, `SPEC`, `BUILD`, `VALIDATE`, `CLOSE`, `DELIVER`, `HG-1`, `HG-2` — is a deliberate checkpoint. Gates do not self-advance regardless of profile. L2 enforcement via the cockpit means the system *blocks* advancement until the gate is cleared; it does not *substitute* for clearing it.

### Identical quality requirements across profiles

LOD levels and their quality requirements are **identical in L0 and L2**. The only thing that differs is the mechanism by which compliance is verified and enforced.

> **Iron Rule — Profile Parity:** A weak spec in L0 is exactly as invalid as a weak spec in L2. Reducing enforcement does not reduce the specification requirement.

---

## §4 — Process Tracks

Every WP declares exactly one **track** at creation time; the cockpit derives the correct LOD ladder and gate sequence automatically — no human selection of gates is required.

| Track | Hebrew | Trigger | LOD Path | Gates |
|---|---|---|---|---|
| **EXPRESS** | מהיר | ≤2 files, doc/config, LOW risk | `100-lite → 400` | `LOD_CHECK` · `BUILD` |
| **STANDARD** | תקני | Code WP, clear scope, single domain | `100 → 200 → (300) → 400 → 500` | `LOD_CHECK` · `SPEC` · `BUILD` · `VALIDATE` · `CLOSE` |
| **MANAGED** | מנוהל | HIGH risk, multi-team, new state machine | `100 → 200 → 300 → 400 → 500` | `LOD_CHECK` · `SPEC` · `HG-1`@200 · `BUILD` · `VALIDATE` · `HG-2`@500 · `CLOSE` |
| **RESEARCH** | מחקר | No code; findings/report output | `100 → report` | `LOD_CHECK` (team_00 reads) |
| **OPS** | תפעול | Infra/server/port/deploy | `400 / runbook` | `BUILD` · deploy-verify |
| **CONTENT** | תוכן | Book/video/design/non-code artifact | `100 → 200 → artifact` | `LOD_CHECK` · `SPEC` · `DELIVER` |
| **HOTFIX** *(modifier)* | דחוף | Production blocker — attaches to any base track | Base-track path; worktree ≤4h | Base-track gates (unchanged) |

> **[v5 Change — Single Continuous Sequence]**
> v5 frames all work as **one continuous backlog** with a per-track LOD ladder. The old v0.3 parallel "Track A / Track B" split is retired. There is no longer a separate "complex" track — scope and risk are expressed by choosing the appropriate track from the six above.

> **[`track` is a required enum]**
> `track` MUST be declared at WP creation. `validate_aos` Check 44 enforces presence; valid values come exclusively from `CANON_COCKPIT_ENUMS §5`. The cockpit derives the LOD path and gate sequence from the declared track — manual gate selection is not permitted.

> **[LOD300 is now track-aware]**
> LOD300 (feasibility / architecture spike) is present in **STANDARD** (when preliminary feasibility work is needed) and mandatory in **MANAGED**. It is skipped in EXPRESS and OPS. It is no longer associated with a "complex track only" designation — the track declaration determines its presence automatically.

> **[L2.5 is retired]**
> The L2.5 managed-pipeline profile is **retired as of v4.0.0** (ADR044 §4). Its governance intent — human gates for high-risk, multi-team work — is fully absorbed by the **MANAGED** track, which adds `HG-1` (human gate after LOD200) and `HG-2` (human gate at LOD500 / `CLOSE`) to the standard gate sequence.

> **[HOTFIX is a modifier, not a base track]**
> HOTFIX (דחוף) attaches to whichever base track the WP would otherwise follow — it does not replace that track's gates. The modifier adds a worktree-isolated ≤4h turnaround constraint and surfaces the WP as a production blocker in the cockpit. All base-track gates remain binding.

---

## §5 — LOD Levels — full definitions

### §5.1 — LOD100 — Intent (taste + consequences)

LOD100 captures the raw intent of a work package — *why* it exists and *whether it should* — before any solution thought is permitted.

#### The two mandatory gates

LOD100 carries two mandatory judgment fields. Neither is optional; neither can be delegated to an agent. Both route to **team_00** via the `AWAITING_YOU` status. The `LOD_CHECK` gate does not pass until both fields are filled **and** a recorded human decision is present.

| Field | Question | Hebrew gloss | Required output |
|---|---|---|---|
| **`taste_verdict`** | Is this worth wanting at all? | מטעים | Verdict (go / no-go / conditional) + reasoning — value before everything |
| **`consequences_verdict`** | What does this move? What breaks? | השלכות | Verdict + initial impact map — at minimum: what systems, flows, and teams are touched |

The maxim behind `consequences_verdict`: *a bug in the design is a bug in the debug* — "באג בדיזיין זה זיין בדיבג." Getting the framing wrong compounds every downstream cost; surfacing it here is cheap.

Both verdict fields are registered in `CANON_COCKPIT_ENUMS` (the enum SSoT).

#### Enforcement (P9 — structural block)

The `LOD_CHECK` gate blocks structurally in both deployment profiles:

- **L2 (Cockpit):** C3 does not render the "Advance to LOD200" action until `taste_verdict` and `consequences_verdict` are present in the WP state.
- **L0 (Manual / degrade):** the gate is recorded in the `gate_log.md`-style file; `validate_aos` flags the absence of either field as a gate violation, and the human orchestrator may not route the WP forward until both are filled.

Profile parity applies — reduced infrastructure does not reduce the gate requirement (§3).

#### Content requirements

**Must include:**
- **Problem statement** — 1–3 sentences; the real problem, not the solution
- **Target user or affected system** — who or what is changed
- **Desired outcome** — the state of the world if this succeeds
- **Rationale** — why now, why this, why worth the cost
- **Explicit out-of-scope** — what this WP will not address
- **Open questions / blocking assumptions** — surfaced, never omitted; unresolved is acceptable here
- **`taste_verdict`** — (go / no-go / conditional) + reasoning
- **`consequences_verdict`** — verdict + initial impact map

**Must not contain:**
- Solution design of any kind
- Technical decisions
- Acceptance criteria

**Typical length:** Half a page. Concise is correct — LOD100 is not a spec.

**Who produces:** Principal (team_00) or Architect (team_100).
**Gate:** `LOD_CHECK` — team_00 judgment; both verdict fields required.

> **Memory-origin note.** These two gates are not bureaucracy added onto the work — they are the externalization of the architect's natural cognition. A person who cares about quality asks "is this worth it?" and "what does this touch?" before writing a line. LOD100 makes that instinct a structural requirement, shared across every engine and every session that touches a work package.

### §5.2 — LOD200 — Concept (the cheap point + cost_cap)

LOD200 is **the last cheap go/no-go** — the boundary where a "no" costs a conversation, not a sprint.

After LOD200, build cost climbs steeply; every subsequent LOD level burns tokens, developer attention, and calendar. The `SPEC` gate exists precisely here: it is where the system decides whether the concept is sound enough to authorize real expenditure.

> **`cost_cap` — mandatory output of LOD200**
>
> Every LOD200 artifact MUST declare **`cost_cap`**: an estimated ceiling on build cost (tokens + human time) for the work package. This field ties the token-economics principle (P8 / L9) to delivery economics (L19 / P10). The `SPEC` gate will not pass a LOD200 that omits or leaves `cost_cap` as a placeholder.
>
> If actual build cost later **exceeds** `cost_cap`, the WP does not silently continue — it escalates to **team_00** (the judgment pillar) for an explicit go / continue / scope-cut decision.

LOD200 must also include **functional acceptance criteria** — a clear statement of "what counts as working" for the happy path. This is not deferred to LOD400. If the team cannot articulate functional acceptance at concept stage, the concept is not ready.

**Must include:**
- **Problem statement** — confirmed or refined from LOD100
- **Solution concept** — what *kind* of system this is (not how it is built)
- **Major components** — each named with its purpose in one line
- **Primary flow** — the happy-path sequence; actors, triggers, termination
- **Actors / users / systems** — who or what interacts with the solution
- **Open decisions** — explicit list; nothing papered over
- **Dependencies and constraints** — external systems, platform limits, schedule
- **Initial success criteria** — observable outcomes that signal the WP is done
- **Risk classification** — one of `Low` / `Medium` / `High` / `Critical`; drives track and gate intensity
- **`track`** — declared per §4 (EXPRESS / STANDARD / MANAGED / RESEARCH / OPS / CONTENT); binding from this point forward
- **`cost_cap`** — build-cost ceiling (see callout above); required for `SPEC` gate passage
- **Functional acceptance criteria** — what "working" means for the primary use case

**Must not contain:**
- Full field-level specification or data schemas (LOD400)
- Implementation details — algorithms, library choices, deployment topology
- Edge-case handling or error taxonomy (LOD400)
- UI/UX wireframes or copy (LOD400 or CONTENT-track deliverables)

**Who produces:** Architect (team_100 or a domain architect with hub mandate).
**Gate:** `SPEC` — compliance check (all required fields present, `cost_cap` filled, `track` declared) followed by go/no-go judgment; a failing `SPEC` gate returns the artifact to the architect with an explicit gap list before any build work begins.

### §5.3 — LOD300 — System Behavior *(track-aware)* + feasibility gate

**Question answered:** How should the system behave — and is every uncertain part of it actually feasible?

LOD300 is **not** "complex track only." It is **track-aware**: present in STANDARD (when feasibility work is
needed) and MANAGED; skipped in EXPRESS. It carries the system-behavior layer **and** the feasibility gate (L55).

**Must include:**
- Complete state machine (all states, transitions, triggers);
- All business rules governing flow;
- Integration contracts between components;
- Full acceptance criteria at feature level;
- API surface definition (endpoints, payloads, error responses);
- Data model (entity definitions, relationships, constraints);
- Sequence diagrams or equivalent for complex flows.

**Feasibility gate (L55) — a precondition within `SPEC`, before the LOD400 (`BUILD`) lock.** This is **not** a
seventh named gate: it is the design-review guard checked inside the `SPEC` envelope. Before LOD400 can lock,
**every uncertain component** (a tool/capability/integration dependency, or an unvalidated assumption) must pass
a **feasibility check** — a canary, probe, or spike — and the findings must sharpen the spec:

> `LOD400-lock ⟺ (∀ uncertain component: feasibility passed ∧ spec updated) ∧ (zero unresolved blocker)`

- **Regression rule:** a material blocker regresses the WP to LOD300 (wrong behavior) or LOD200 (wrong
  concept). **Regression is gate success, not failure** — it is cheap, early detection.
- **Track-aware depth:** EXPRESS uses light feasibility; STANDARD/MANAGED use the full gate.
- **Two planes (do not lose the second):** every feasibility check operates on (a) the specific spec's
  precision **and** (b) learning fed back to the methodology (an instance of P11).
- **DB field:** `feasibility_check` (verdict + evidence) is the condition for advancing LOD300 work to `BUILD`
  (the LOD400 lock) on STANDARD/MANAGED, enforced structurally in the cockpit (P9) as a guard within `SPEC` —
  not a separate named gate.

**Typical length:** 4–10 pages depending on complexity. **Who produces:** Architecture role, consuming team
co-reviews. **Gate relevance:** enforced as a precondition of the `SPEC` gate (the LOD300 design-review step)
before a `BUILD` advance, on tracks that include LOD300.

### §5.4 — LOD400 — Execution-Ready

**Question answered:** What exactly must be built, shown, enforced, and verified?

**Precision standard (MANDATORY):** A LOD400 spec must be detailed enough that **any junior developer — or a
freshly-initialized agent with zero project context — can implement it successfully without filling in gaps,
guessing, or making assumptions.** If the spec requires the builder to infer anything not explicitly stated, it
is not LOD400. This is the defining quality bar for this level.

**Must include:**
- Zero ambiguity on product decisions — a builder agent must not need to invent anything;
- Every UI state and **the N×4 state matrix** (see below) for any work package with an interface;
- Every permission rule and enforcement point;
- Complete acceptance criteria (numbered, testable, unambiguous);
- All copy / labels / messages (exact text, not "something about X");
- API contracts (exact endpoints, payloads, status codes);
- DB schema changes (column names, types, constraints, migrations);
- Error handling (every error state, user-visible message, system behavior);
- Performance / scale constraints if relevant;
- Explicit non-goals (what will NOT be built).

**Must not contain:** open questions, "TBD", aspirational descriptions ("should feel smooth"), or implicit
assumptions about project conventions.

**N×4 / QA chain (Q-D3).** *Spec defines N×4 → build implements N×4 → QA verifies N×4.* **N** = every surface
of the WP; **4** = the states `empty / loading / error / offline`. A work package **with an interface** must
define its N×4 matrix at LOD400, and the `BUILD`/QA gate must verify all of it. EXPRESS-with-UI uses a minimum
coverage (`error` + `offline`). **CONTENT / doc work packages** have no UI matrix — they use an **alternative
functional DoD** ("what counts as working" for that artifact) in its place.

**Four QA-deepening axes** (woven into the correctness pillar; verified at `BUILD`/`VALIDATE`):

| Axis | Requirement |
|------|-------------|
| **Q-D1 anti-false-pass** | Every test asserts on real behavior; a **silent skip is a FAIL** |
| **Q-D2 cold-integration** | A **hard gate**, not advisory: fresh-clone + merge-queue + regression + post-merge smoke |
| **Q-D3 N×4 coverage** | The test matrix is **derived from the WP's N×4 definition** |
| **Q-D4 determinism** | Playwright (or equivalent) is the **verdict**; an LLM may author/explore but is never the sole judge; visual diff is deterministic (threshold tunable in `policies`) |

**Two non-interchangeable test tiers:** **internal** (every builder self-verifies during build — mandatory,
cannot be skipped) and **external** (independent functional acceptance by a cross-engine QA role at the gate —
does not replace the internal tier).

**Typical length:** 5–20 pages. **Who produces:** Architecture role. **Who approves:** the consuming team
(builder) confirms it is executable as written. **Gate relevance:** required before `BUILD`. Immutable after
approval; correction cycles bump the version.

### §5.5 — LOD500 — As-Built Record

**Question answered:** What was actually implemented, verified, and is true now?

**Must include:**
- `spec_ref`: exact reference to the LOD400 version it documents — **required for build-time (NORMAL-mode) LOD500s**. Every shipped code change authored under the build-time ladder MUST be traceable to a locked LOD500 whose `spec_ref` names the exact LOD400 version it implements (§12).
- **Backfill provenance (BACKFILL mode, §5.6):** when the code shipped before any LOD400 existed, `spec_ref` is set to the literal string `no prior LOD400 — backfilled` and a one-line provenance note records how the as-built was reconstructed (which code paths + tests were read to verify it). A backfilled LOD500 is the canonical traceability record for pre-existing code; the absent LOD400 is a stated fact, not a gap to be papered over with a retro plan.
- Execution fidelity: `FULL_MATCH | DEVIATIONS_DOCUMENTED | PARTIAL`;
- Deviations from LOD400 (if any): what changed, why, who approved;
- Verified acceptance criteria (which passed, which were modified, evidence);
- **Cold-integration + regression result** (Q-D2) — the as-built is not locked until these pass;
- Known limitations or deferred items;
- Validation evidence: who validated, which engine, what was tested.

**Must not contain:** content written from memory (must come from actual verification) or self-certification by
the implementing team.

**Who produces:** documentation/architecture role after build. **Who approves:** an independent validator on a
**different engine** from the builder (Iron Rule #1 — §10). **Gate relevance:** required at `VALIDATE` → `CLOSE`.
**Immutable** after lock (§12); the project DOC is the running sum of locked LOD500 records, updated on every
`CLOSE`.

### §5.6 — Two authoring modes — build-time ladder vs backfill

The LOD ladder (§5.1–§5.5) can be authored in **two modes**. Both produce the same canonical artifacts;
they differ only in *when* the ladder is written relative to when the code ships. Naming the mode is
mandatory on any program that is not authoring the ladder live during build.

| Mode | When | What is authored | What is NOT authored |
|---|---|---|---|
| **NORMAL (build-time ladder)** | The ladder is written **as the code is built**, ahead of or alongside implementation. | The full per-track LOD ladder for the WP (§4): e.g. STANDARD `100 → 200 → (300) → 400 → 500`. Each level gates its build step. | — (nothing is skipped; the ladder is the plan). |
| **BACKFILL (documentation-completion)** | The code **already shipped** before its LOD ladder existed (or the ladder is incomplete). A **documentation-completion program** records what is true now. | **LOD500 (as-built) only**, verified against the running code and its tests. Prior plans, if any exist, are **cited** inside the LOD500 (`spec_ref`, `deviations`, `execution_fidelity`). | **No retro LOD300/400** is recreated. Reconstructing a plan the build never followed would be fiction, not an as-built record. |

**A LOD500-only documentation-completion program is canonically valid.** Authoring LOD500 without a
matching LOD300/400 is **not** a skipped-LOD violation *when the WP is declared BACKFILL* — it is the
correct and only honest artifact for already-shipped code. BACKFILL is the canonical home for
doc-completion work **on tracks that actually produce a LOD500** (e.g. STANDARD or OPS) — bringing
legacy subsystems under LOD discipline after the fact. (The `RESEARCH` track produces a report, not a
LOD500, so it is not a BACKFILL case.)

**Rules for BACKFILL mode:**

- **Verify, do not remember (command-citation ground-truth discipline — enforceable).** Every claim in a
  backfilled LOD500 comes from reading the code and running its tests — never from memory or from a plan
  document (§5.5 "Must not contain"). This is **enforceable, not aspirational**: every *factual or
  quantitative* claim in a backfilled LOD500 (a file/line/match count, a test-pass tally, a "N modules",
  an API-shape assertion) MUST carry (a) the **exact verification command** that produced it and (b) that
  command's **live output** quoted inline. A bare number or assertion with no command+output is a defect.
  At `VALIDATE`, the independent cross-engine reviewer **re-runs** each cited command against the working
  tree and confirms the quoted output matches ground truth; a claim whose re-run does not reproduce = a
  FAIL of the as-built record.
- **No retro plan.** LOD300 and LOD400 are **not** authored retroactively. If a prior LOD400 exists, the
  LOD500 `spec_ref` points at it; if none exists, the LOD500 carries the provenance note defined in
  §5.5 / §12 (`no prior LOD400 — backfilled`).
- **Same immutability + cross-engine gate.** A backfilled LOD500 is immutable after lock (§12) and is
  validated at `VALIDATE` by an independent validator on a **different engine** (Iron Rule #1 — §10),
  exactly as a build-time LOD500 is. Backfill relaxes *which levels are authored*, never *who checks*.
- **Declare the mode.** A documentation-completion program declares BACKFILL mode in its WP metadata /
  program charter so the validator does not read the absent LOD300/400 as a gate failure.

> **Why this is not a loophole.** BACKFILL does not lower the bar — it forbids the *worse* alternative
> (inventing a retro plan). The as-built record still passes cold-integration + regression (Q-D2, §5.4)
> and an independent cross-engine check. The only thing waived is the pretence that a plan preceded code
> that in fact shipped without one.

---

## §6 — Gate Model

v5 uses **named gates only**, referenced from `CANON_COCKPIT_ENUMS §2` (the single source — this standard does
not redefine them):

| Gate | Reality it verifies | LOD |
|------|---------------------|-----|
| **LOD_CHECK** | Taste + consequences verdicts present; team_00 judgment recorded | 100 |
| **SPEC** | Concept compliant; `cost_cap` set; go/no-go judgment. On LOD300 tracks, the design-review + `feasibility_check` (L55) are preconditions before a `BUILD` advance | 200 / 300 |
| **BUILD** | Build runs; tests assert real behavior; **cold-integration** + browser-QA pass | 400 |
| **VALIDATE** | Cross-engine validator readiness (IR#1); as-built matches spec | 500 |
| **CLOSE** | DOC obligation met; product-works verification; team_00 closure | 500 |
| **DELIVER** | (CONTENT) artifact delivered + fidelity + human judgment | artifact |
| **HG-1 / HG-2** *(modifier)* | (MANAGED) human gates at LOD200 / LOD500 | 200 / 500 |

The **per-track gate path** (which gates apply to which track) is the §4 per-track table. Lean L0 may merge
**consecutive, compatible** named gates into a single review step — an `L-GATE_*` label denotes an L0 *merge of
named gates* (e.g. `SPEC`+`BUILD`), **not** a separate gate token — but the maker≠checker independence of the
decisive gate is never merged away.

**Legacy aliases.** Older lean docs used `L-GATE_<NAME>` step names and TikTrack used numeric gate identifiers;
both map to the named gates above. They are aliases, not canonical tokens: the canonical set is §6, the numeric
mapping is read-only and lives only in the enum SSoT — see §7.

---

## §7 — Legacy gate bridge (numeric → named)

The named gates of §6 are the **only** canon. Legacy numeric gate identifiers (`GATE_n`, the TikTrack-era
sequence) are **deprecated** and **read-only**: artifacts that still reference them remain readable through a
**single mapping table maintained solely in
[`CANON_COCKPIT_ENUMS §2b`](../../_aos/v5_characterization/synthesis/CANON_COCKPIT_ENUMS_v1.0.0.md)** (controlled
deprecation, P11 — locked by W7).

This standard never uses numeric gate identifiers — only names. A **new** numeric gate reference appearing in
this v5 standard is a validation **FAIL** (`validate_aos.sh` Check 53 · `validate_canon_enums.py`). The single
source for every gate/track/status/LOD name is the enum SSoT; nothing is redefined here.

> **Honest scope.** "Deprecated and read-only" describes the **authoring interface**: no new artifact, doc, or
> spec may introduce a numeric gate, and this standard never does. The numeric identifiers do, however, still
> persist as the **internal DB phase/gate engine** during the v4→v5 transition (migration-tracked — e.g.
> migration 025 still operates on numeric phase rows). The named gates are the canonical interface over that
> engine; the numeric core is being retired progressively, not already gone. This is stated plainly so the
> bridge is not mistaken for "numbers are already deleted everywhere."

---

## §8 — Portable contract layer

The AOS v5 LOD Standard is enforceable across every environment — full cockpit, headless CI, or offline degrade — because the six elements below define a single portable contract. This section **cites** each element to its v5 home; it does not redefine it. Adding definitions here would duplicate locked sources and violate P11 (anti-drift).

| Contract element | Its v5 home |
|---|---|
| **Frontmatter schema** | The WP-metadata schema (ledger entry L15) — `description`, `params`, `track`, and `effort` among the mandatory fields (`track` + `effort` enforced by `validate_aos` Check 44); data-model constraint CA2 governs structure. Frontmatter is emitted via the template canon (CA7 / §13), not hand-modeled. |
| **Declaration authority** | Who may declare each LOD level: the team roster (ledger entry L23) combined with §11 of this standard. LOD100 is declared and approved by `team_00` at the `LOD_CHECK` gate; no other team may self-declare that level. |
| **Versioning / immutability** | `LOD500` records are immutable once locked (ledger entry L44). The project DOC is the running sum of all locked `LOD500` records; it is updated automatically on every `CLOSE` gate event. See §12 for the append-only maintenance rule. |
| **Gate artifacts & legacy bridge** | The controlled back-compat bridge defined in §7: legacy artifacts remain readable; new work uses named gates (`LOD_CHECK` / `SPEC` / `BUILD` / `VALIDATE` / `CLOSE` / `DELIVER` / `HG-1` / `HG-2`). The bridge is **not** abolished — P11 requires that existing artifact chains stay interpretable across the v4→v5 transition. |
| **WP-ID schema** | The canonical work-package identifier — `M{n}-P{n}-WP{n}-slug` for hub-native WPs, `SNNN-PNNN-WPNNN` for spoke-native WPs — is defined in ledger entry L15 and enforced at parse time by `core/wp_id.py`. An ID that does not match a recognized pattern is rejected before any LOD gate is opened. (The legacy hub-native `AOS-V*-WP-*` form is file-only and intentionally **not** accepted by `core/wp_id.py` — see ADR034 R10.) |
| **L0 / degrade fallback** | The two-mode enforcement rule defined in §9. Every structural enforcement clause in this standard applies in both modes; the cockpit is not a prerequisite. |

Every element above is derived from a locked source with zero local duplication (anti-drift, P11); the gate, track, and status names it cites are verified against the single enum source by `validate_aos` Check 53.

---

## §9 — L0 fallback / degrade

The LOD Standard operates in two modes. Structural enforcement (P9) is identical in both; the cockpit and DB provide automation, not the authority.

| Mode | Substrate | Gate logging | DB reconciliation |
|---|---|---|---|
| **Mode 1 — Full** | Cockpit + DB + `validate` CLI | Gates recorded to DB; `VALIDATE` output surfaces in dashboard | Immediate; canonical state is always in the DB |
| **Mode 2 — L0 / degrade** | `git` only (always available) | Gates logged locally to a `gate_log.md`-style file in the WP directory | Reconciled to the DB on reconnect per ADR034 R8; `git` history is the interim audit trail |

> **L0 fallback is always preserved.**
> Every P9 enforcement clause in this standard — gate sequencing, artifact requirements, declaration authority, immutability — applies in **both** modes. A `SPEC` gate that would fail in the cockpit fails equally in degrade mode. A weak or missing `description` field is invalid whether or not the DB is reachable. Degrade mode changes the logging substrate; it does not relax the standard.

---

## §10 — Cross-Engine Validation (Iron Rule #1)

**Unconditional. Applies across all profiles.** No team may be the sole validator of its own output. The
**decisive gate** of any work package (per its track — `VALIDATE`/`CLOSE` for STANDARD/MANAGED, `DELIVER` for
CONTENT, `BUILD` for EXPRESS/OPS) must be performed by a team using a **different engine** than the one that
built the implementation.

This is **tiered** per ADR053:
- **Decisive gate** → cross-engine (different vendor/model family — Tier-2; e.g. a non-Claude engine validates
  Claude-built work);
- **Intermediate gates** (`LOD_CHECK` / `SPEC` / `BUILD`) → at minimum Tier-1 functional independence (a
  fresh-context adversarial sub-agent; a different model SHOULD be used).

| Profile | How enforced |
|---------|--------------|
| **L2** (cockpit + DB) | Pipeline/cockpit enforces: `assigned_validator` engine must differ from `assigned_builder`; tracked in DB; submission rejected if same engine |
| **L0** (Lean) | Declared in role assignments (`assigned_validator` ≠ `assigned_builder`); the human orchestrator routes validation to the assigned validator and never validates content itself |

**Engine diversity principle:** "different engine" means a different model family / provider — different
training data, different failure modes, different blind spots. Same family, different size is not sufficient for
the decisive gate.

### §10.1 — Robust-harness contract (how the cross-engine gate is actually run)

Iron Rule #1 (above) says *who* validates (a different engine). This sub-section binds *how* the
validation harness behaves so a decisive gate cannot silently pass on a broken or empty run. All four
clauses are mandatory at any cross-engine gate.

- **(a) Non-empty-stdout requirement.** A validator invocation that returns **empty stdout is a FAILURE,
  never a PASS.** An empty/whitespace-only result means the engine did not actually produce a verdict
  (an empty-choke, a timeout, a dropped worker) — it is treated as `NO_VERDICT`, not as tacit approval.
  The gate stays CLOSED until a non-empty, parseable verdict is captured.
- **(b) Rerun-guard.** Cross-engine invocations are driven through the canonical harness
  `scripts/run_cross_engine_validator.sh`, whose **rerun-guard** re-invokes the validator (a bounded
  number of times) on an empty/malformed result rather than accepting it — so a single flaky empty-choke
  does not become a false PASS or a false FAIL. The guard's retry budget is finite (see clause (d)).
- **(c) Embedded-evidence fallback — a DOCUMENTED, ATTESTED degrade path (never a silent PASS).** If, after
  the rerun-guard's budget is exhausted, the external engine still cannot be invoked (worker saturation,
  outage, auth failure), validation may fall back to an **embedded adversarial analysis** performed
  in-context — **only** under all of: (i) the engine-invocation failure is **logged** (which engine, what
  error, how many attempts); (ii) the embedded analysis is genuinely **adversarial** and every factual
  claim it makes is backed by a **cited live git-grep / command + its output** (command-citation
  ground-truth discipline, §5.6); (iii) the fallback and its evidence are **attested** in the LOD500 /
  verdict as a degrade path, not presented as a clean cross-engine run. A fallback that skips the log, the
  cited evidence, or the attestation is a **silent PASS** and is forbidden.
- **(d) Anti-loop termination.** Validator invocations are **bounded** — the harness does not loop
  indefinitely chasing a literal `VERDICT: PASS` string. The terminal rule: **fix the reported BLOCKERs,
  accept a `CONDITIONAL_GO`** (proceed with the recorded conditions), and **never re-run merely to convert
  a legitimate `CONDITIONAL_GO`/`GO_WITH_CONDITIONS` into a bare `PASS`.** Once BLOCKERs are cleared and a
  GO (conditional or not) is on record, the gate is decided; further invocations are a loop and are
  disallowed. (Generalized from the M10 cockpit `_CK_KERNEL` §0.4 anti-loop rule.)

> **Why this belongs in the standard.** Iron Rule #1 guarantees engine *diversity*; without the harness
> contract, that diversity can be defeated in practice by an empty run read as PASS, an un-attested
> in-context "validation", or an infinite re-run loop. §10.1 closes those three failure modes so the
> decisive gate is robust, not merely nominally cross-engine.

---

## §11 — Declaration Authority Matrix

Role types are universal (not project-specific team numbers).

| LOD level | Who produces | Who approves | Cross-engine required |
|-----------|--------------|--------------|----------------------|
| LOD100 | Principal or Architect | **Principal (team_00)** — taste + consequences | No |
| LOD200 | Architect | Architecture role | No |
| LOD300 | Architect | Architecture + consuming team | No |
| LOD400 | Architect | **Consuming team (builder confirms executable)** | No |
| LOD500 | Tech-writer / Architect post-build | **Independent validator (different engine)** | **Yes — Iron Rule #1** |

> **RESEARCH track.** The `100 → report` path (§4) has no code gate, so it is not a row above. But a high-stakes
> or foundational ("מהלך יסודי") research/characterization output still warrants **cross-engine adversarial
> review** before team_00 relies on it — as this very standard was validated (per-section cross-engine plus a
> whole-document adversarial deep-review). "No code gate" is not "no independent check."

---

## §12 — Versioning Policy

- All LOD documents are **immutable after approval**.
- Naming: `{document_name}_v{major}.{minor}.{patch}.md`.
- Bump triggers: major = scope change; minor = content addition; patch = clarification/error fix.
- Lifecycle: `DRAFT → APPROVED → SUPERSEDED → ARCHIVED`.
- A correction cycle always produces a new version; the old version is retained as reference.
- A LOD500 `spec_ref` must point to an exact LOD400 version **for build-time (NORMAL-mode) LOD500s**; for BACKFILL-mode LOD500s (code shipped before any LOD400 existed) it instead carries the `no prior LOD400 — backfilled` provenance note (§5.6, §12.1).
- The project DOC is the running sum of locked LOD500 records (L44), updated on every `CLOSE`.

### §12.1 — spec_ref → LOD500 traceability (fleet rule)

**Every shipped code change is traceable to exactly one LOD500 as-built record.** This is the fleet-wide
traceability invariant that closes the loop between what was specified (LOD400) and what is true now
(LOD500):

- **Build-time (NORMAL mode):** the LOD500 `spec_ref` names the exact LOD400 version the code implements
  (§5.5). No shipped module authored under the build-time ladder is complete until its LOD500 is locked.
- **Backfill (BACKFILL mode, §5.6):** for code that shipped before any LOD400 existed, the LOD500
  carries the explicit provenance note `no prior LOD400 — backfilled` (§5.5) instead of a LOD400 pointer.
  This is a first-class, valid traceability record — **not** an exemption from having a LOD500.

**Where the rule is checked:**

- **DOC-close-gate (`validate_aos.sh` Check 59):** verifies `_aos/context/DOC_CANON.md` is present and
  well-formed and, at the `CLOSE` gate / in cold-integration CI (`AOS_DOC_CLOSE_GATE=1`), that the
  closing WP's LOD500 is reflected in DOC_CANON. This is the structural enforcement point that a closing
  WP produced its as-built record.
- **Cross-engine validator at `VALIDATE`:** confirms the LOD500 `spec_ref` (or the backfill provenance
  note) is present and accurate against the code — a self-certified or `spec_ref`-less LOD500 fails
  (§5.5 "Must not contain"; §10 Iron Rule #1).
- **Related citation-hygiene guard — NOT a traceability check (`validate_aos.sh` Check 26, advisory):**
  Check 26 lints CS-citation *format* only (a qualified `[repo path CS-N]` vs a bare tag), keeping the
  LOD400↔LOD500 references legible across repos ([agents-os _aos/context/CODE_STANDARDS.md CS-6],
  ADR037). It does **not** verify `spec_ref`/provenance presence — traceability itself is enforced
  solely by the two points above (Check 59 at `CLOSE` + the cross-engine validator at `VALIDATE`).

### §12.2 — RELEASE_CANDIDATE → release promotion (this standard)

This standard shipped as a release candidate (`status: RELEASE_CANDIDATE`) and was **promoted to
`status: RELEASED`, `version: v5.1.0` on 2026-07-03** (team_100, AOS-V5-M10 closure — see the promotion
`log_entry` at the foot of this file). The promotion is a **single, gated, terminal act** recorded here
for provenance; its **criteria — ALL required, in order — were:**

1. **W-a landed.** The dual-mode (§5.6), spec_ref/provenance (§5.5, §12.1), and this promotion
   sub-section (§12.2) are present in this file and `validate_aos.sh` reports **no NEW FAIL
   attributable to this WP** (Check 53 enum-SSoT PASS; Check 26 advisory clean).
2. **W-c sweep complete.** Every residual reference to a superseded LOD standard (`LOD_STANDARD_v0.*`,
   `LOD_STANDARD_v1.0.0`, `TEAM_100_LOD_STANDARD_*`) across the hub's live (non-`_archive`) tree has
   been repointed to this standard or retired — the residual-reference sweep tracked by the M10
   doc-completion program (W-c). Census 2026-07-02: **54 files / 121 match-lines** (advisory snapshot —
   it will drift with repo churn); **the gate is the CLASS assignment of each file (W-c §2.2), not the
   raw count.** No live pointer to a superseded version remains.
3. **team_00 methodology sign-off** for the promotion is recorded (constitutional — Iron Rules
   #11/#12/#14; ADR040).

**Operator (who performs the terminal act).** The RC→release flip is performed by **team_100** (Chief
Architect) as the terminal act **after** the W-c residual-reference sweep completes and criterion #3's
team_00 methodology sign-off is on record. (team_00 methodology sign-off is already the constitutional
precondition to APPLY W-a itself; the same sign-off authority gates this later flip — the flip is not a
new WP, it is the last step of this promotion sub-section.) team_100 owns the frontmatter edit.

> **Correction (2026-07-03 — team_100, under team_00 approval: DECISION_AOS-V5-M10-APPLY-SIGNOFFS
> 2026-07-02 + AOS-V5-M10 closure; constitutional per Iron Rules #11/#12/#14).** An earlier draft of this
> sub-section required a "released" status-token pre-registered in the enum SSoT `CANON_COCKPIT_ENUMS`,
> warning that `validate_aos.sh` **Check 53 "would FAIL"** otherwise. **That was incorrect as wired.**
> This document's frontmatter `status:` is **document metadata**, not a cockpit runtime enum. Check 53
> (`validate_canon_enums.py`) governs only the cockpit enum kinds `wp_status`, `session_status`, `gate`,
> `track`, `domain_status`, `session_type`, and never scans this document's frontmatter — which is exactly
> why `status: RELEASE_CANDIDATE` validated cleanly while un-enumerated. **No enum-SSoT registration is a
> precondition of this flip.** The promotion is a pure frontmatter metadata edit (`status`, `version`,
> promotion `log_entry`), as the corrected Mechanics below state.

**Mechanics (the act, performed by team_100 once all three criteria above hold):**

- Edit **only** the frontmatter of this file:
  - `status: RELEASE_CANDIDATE` → `status: RELEASED`. A document-metadata edit — **no** enum-SSoT
    registration is required (the LOD-document `status:` is not a Check-53-governed cockpit enum; see the
    Correction note above).
  - `version:` is bumped to the team_00-decided released string. **Resolved 2026-07-03: `v5.0.0` →
    `v5.1.0`** (team_00 decision at M10 closure — a semantic minor bump on the v5 line, not the `v1.0.0`
    the original `next_version_trigger` pointed at; see the version-string note below).
  - the frontmatter `next_version_trigger:` line is replaced by a `released:` record so it no longer
    points at an already-executed promotion.
- Append a `log_entry` line at the foot of this document recording the promotion (team, version,
  date), mirroring the existing `log_entry | team_100 | ...RELEASE_CANDIDATE | 2026-06-16` line.
- The body of the standard is **not** otherwise edited by the promotion act — promotion changes status,
  not content.

> **Version-string note (RESOLVED at promotion, 2026-07-03).** The RC frontmatter read `version: v5.0.0`
> while the original `next_version_trigger` read "promote to v1.0.0" — two numbering lineages (the "v5"
> standard-generation label vs. a per-document semantic `v{major}.{minor}.{patch}`). **team_00 resolved
> this at M10 closure: the released string is `v5.1.0`** (a semantic minor bump on the v5 line). Recorded
> in the promotion `log_entry` below. *(Namespace note: a git repo tag `v5.1.0` exists as the repo
> baseline — a distinct namespace from this document's `version:` field; nothing cross-checks the two.)*

---

## §13 — Anti-patterns → enforcement matrix

v0.3 listed anti-patterns as a discipline checklist — things a careful person should not do. v5 inverts that:
wherever an anti-pattern *can* be made structurally impossible, it is. **Structure is enforced in the creation
path, not in session discipline** (P9 / L16). The matrix marks honestly what is **live** today versus what has
the **slot/model in place with enforcement landing in the cockpit build (M1)** — claiming fake liveness would
itself be the anti-pattern this section exists to kill.

| Anti-pattern (was: discipline) | Structural constraint (P9) | Where enforced |
|---|---|---|
| **Undeclared / wrong track** | `track` is a **required enum** at WP creation | **Live** — `validate_aos` **Check 44** validates the `track` (one of the six base tracks) and `effort` WP-metadata fields against a canonical list; HOTFIX is recorded as a modifier flag, not a `track` value. *(Check 44 currently holds its own track list; a follow-up makes it read `CANON_COCKPIT_ENUMS §5` directly so seed↔check drift is asserted.)* |
| **Unmarked LOD level** | `lod_target` is a **typed slot**; an empty LOD ceiling is non-advanceable | **Slot live; block wiring in the cockpit** — the dedicated column **exists** (migration 022, applied in S2); application code currently serves it via the `lod_status` interim alias (`core/modules/management/wp_service.py`), and the gate-block-on-empty precondition lands with the cockpit gate logic (M1) |
| **Invalid / hand-modeled frontmatter** | Frontmatter is **emitted from data via the template canon**, not hand-typed | **Live (template-driven)** — template canon **CA7/CA17**; programmatic emission, e.g. `core/modules/management/mandates.py` builds frontmatter from structured fields; LOD templates under `lean-kit/modules/document-lifecycle/templates/`. Full **DB-sourced** WP-frontmatter is the cockpit C3 create-flow target |
| **Skipped gate** | Gate-advance is a **guarded transition** — preconditions checked, illegal edges rejected | **Live** — `core/modules/state/machine.py` (`execute_transition` / `advance_run`, `INVALID_STATE` guards); `core/modules/management/sm_b.py` `advance_gate` rejects illegal edges (HTTP 409) |

**Anti-patterns now prevented by other structural mechanisms in this standard:**

| Anti-pattern | Prevented by |
|---|---|
| Spec-less build | Gate sequencing — `BUILD` cannot open before `SPEC` (§6) |
| Same-engine validation | Cross-engine Iron Rule #1 — `assigned_validator` ≠ `assigned_builder` (§10) |
| Self-certified / orphan LOD500 | §5.5 — independent validator on a different engine; produced from verification, not memory |
| LOD100 without taste / consequences | `LOD_CHECK` blocks without both verdict fields (§5.1) |
| LOD200 without a cost ceiling | `SPEC` requires a filled `cost_cap` (§5.2) |
| Profile-based spec reduction | Profile parity — a weak spec is equally invalid in L0 and L2 (§3) |

**What still requires judgment, not a lint.** A few anti-patterns cannot be caught structurally because they
are about *content quality*, not form — e.g. a "fake LOD400" that is long and detailed but still hides an open
product question. These are caught by the **correctness pillar** at the gate (§2.2): the reviewing engine and
the build-runs / cold-integration evidence expose the gap. The same is true of the feasibility check's **second
plane** (§5.3) — feeding what was learned back into the methodology (P11): it has no lint and is, by design, a
judgment obligation, not a structural one. The standard's stance is to convert to structure wherever possible
and to name explicitly the residue that genuinely needs human and cross-engine judgment.

---

## §14 — Provenance & freeze

This document supersedes and replaces, as a single canonical house:

| Archived (read-only) → `_archive/lod-standard-pre-v5/` | Was |
|--------------------------------------------------------|-----|
| `TEAM_100_LOD_STANDARD_v0.2.md` | LOD standard (prior release) |
| `TEAM_100_LOD_STANDARD_v0.3.md` | LOD standard (release candidate) |
| `TEAM_100_LOD_STANDARD_DELTA_v0.1_to_v0.2.md` | changeset |
| `TEAM_100_LOD_STANDARD_DELTA_v0.2_to_v0.3.md` | changeset |
| `gate-model/LOD_STANDARD_v1.0.0.md` | duplicate LOD standard |

The **gate-model version sprawl** (D2) is archived as a single house under `_archive/gate-model-pre-v5/`
(M2-P1-WP9): the four `04_GATE_MODEL_PROTOCOL*` versions, the `GATE_LIFECYCLE_*` family, the
`GATE_0_GATE_1_..._LOCK`, and the stale `gate-model/` PHOENIX-SSM/WSM + TEAM_TAXONOMY copies — all superseded
by **§6/§7** (gate model) here. The single live gate model is §6/§7; legacy numeric gates are read-only (§7).

Archive manifests (original path, archived path, sha256, superseded_by, date):
`_archive/lod-standard-pre-v5/ARCHIVE_MANIFEST.json` and `_archive/gate-model-pre-v5/ARCHIVE_MANIFEST.json`.

> **Spoke boundary (IR#11):** this change is in the hub (`methodology/`); spokes receive it as a read-only
> snapshot via `propagate_governance.sh` — never edited by hand downstream.

**log_entry | team_100 | LOD_STANDARD_v5.0.0_RELEASE_CANDIDATE | 2026-06-16**

**log_entry | team_100 | LOD_STANDARD_v5.1.0_RELEASED | 2026-07-03** — RC→release promotion executed per §12.2, all three criteria met (W-a landed · W-c residual-ref sweep complete · team_00 methodology sign-off `DECISION_AOS-V5-M10-APPLY-SIGNOFFS` 2026-07-02). §12.2's enum-SSoT token precondition corrected under team_00 approval: the LOD-document `status:` is document metadata, not a Check-53-governed cockpit enum (Option 1, AOS-V5-M10 closure).
