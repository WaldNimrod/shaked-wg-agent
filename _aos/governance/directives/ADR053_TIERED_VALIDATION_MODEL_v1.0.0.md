---
id: ADR053_TIERED_VALIDATION_MODEL
title: "ADR-053 — Tiered Validation Model (depth always full; independence tier varies by gate × track)"
version: "1.0.0"
status: LOCKED            # Tier-2 cross-engine BUILD + VALIDATE both PASS (cursor-composer-2, 2026-06-04); team_00 closure
author: Team 100 (Chief System Architect)
approved_by:
  - team_00
  - team_100
approval_date: "2026-06-04"
companion:
  - ADR046_ENGINE_AND_EXECUTION_TIERING_v1.0.0
  - ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS_v1.0.0
adr_ref: ADR-053
wp: AOS-V4.5-WP-SESSION-W6-TIERED-VALIDATION
program: AOS-SESSION-MODEL (6/6 — closes the program)
refines: "Iron Rule #1 (cross-engine validation)"
based_on:
  - _COMMUNICATION/team_100/PROGRAM_CHARTER_AOS_SESSION_MODEL_v1.0.0.md (§W6)
  - feedback_cross_engine_validation_canon (memory, 2026-05-23)
---

# ADR-053 — Tiered Validation Model

> **One line:** *Validation **depth** is FULL at every gate. Validation **independence tier** varies by gate × track — intermediate gates (ELIGIBILITY / SPEC / BUILD) require at-minimum **Tier-1 functional** independence (sub-agent); the **decisive** gate(s) per track require **Tier-2 canonical cross-engine** (Iron Rule #1).*

---

## 1. Status & Context

**Status:** LOCKED v1.0.0 — W6-escalated Tier-2 cross-engine BUILD + VALIDATE both PASS (validator `cursor-composer-2`, Cursor; vendor-distinct from the claude-code builder; Iron Rule #1 Tier-2), 8/8 AC each, 0 blockers, 2026-06-04.
**Companions:** ADR046 (engine matrix + IR#1 enforcement mechanics), ADR047 (task-class routing).

The AOS-SESSION-MODEL program (W1–W5) ran a tiered validation pattern *in practice* — intermediate gates were attested by in-session sub-agents while the decisive gate went cross-engine — but never canonized it. This left a standing contradiction: the cross-engine memory (`feedback_cross_engine_validation_canon`, 2026-05-23) says *"sub-agent attestation is functional only, NOT canonical Iron Rule #1,"* yet intermediate gates were being passed on sub-agent attestation. W6 resolves this by **naming the two things that were conflated** and refining Iron Rule #1 to match — **without weakening the cross-engine guarantee at the gate where it matters.**

---

## 2. Decision — the two-axis model

Validation has **two orthogonal axes**. Conflating them caused the contradiction; separating them dissolves it.

### Axis 1 — Validation DEPTH (always full)
*Was the check thorough?* Every acceptance criterion examined; tests **actually executed** (not assumed); the criteria table filled with evidence; an adversarial stance taken. **Depth is FULL at every gate, regardless of who runs it.** "Full validation at every gate" is a statement about **depth**.

### Axis 2 — Validation INDEPENDENCE TIER (varies by gate × track)
*How structurally independent is the validator from the builder?*

| Tier | Name | Definition | Records |
|------|------|-----------|---------|
| **0** | self | same agent, same context | — (disallowed for any gate) |
| **1** | functional independence | **MUST** fresh context + adversarial stance; **SHOULD** different model; **same engine** OK | `canonical_cross_engine: false` |
| **2** | canonical cross-engine | **MUST** different engine / **vendor + model_family** (ADR046 §2.5) | `canonical_cross_engine: true` |

What the matrix (§4) tiers is **independence**, not depth. An intermediate gate is *full-depth at Tier-1*; the decisive gate is *full-depth at Tier-2*.

### Reconciliation with the cross-engine memory
The memory (*"do not claim Iron Rule #1 satisfied when validators are sub-agents"*) is **upheld, not overturned**: an intermediate gate records `canonical_cross_engine: false` **by design, and that is sufficient for that gate**; the decisive gate **must** record `canonical_cross_engine: true`. Iron Rule #1 (cross-engine) **binds at the decisive gate**.

---

## 3. Tier definitions (normative)

- **Tier 0 (self).** A builder validating its own work in its own context. **Disallowed for any gate.**
- **Tier 1 (functional independence).** A separate agent instance with **fresh context (MUST)** and an **adversarial prompt (MUST — "find the criterion that fails")**; a **different model is SHOULD** (e.g. Opus builds, Sonnet/Haiku validates); **same engine is acceptable**. Catches builder blind spots, context-poisoning, and self-trust. **Blind to engine-substrate failure modes** (shared harness, prompt rendering, tool surface). Records `tier: 1`, `canonical_cross_engine: false`.
- **Tier 2 (canonical cross-engine — Iron Rule #1).** A validator on a **different engine / vendor family** (Cursor / Codex / other-IDE), distinctness tested by **ADR046 §2.5** (`vendor` + `model_family`). Catches substrate-level systematic failure — a genuinely independent harness. Records `tier: 2`, `canonical_cross_engine: true`, and a distinct `engine:`.

---

## 4. The track × gate → independence-tier matrix

Gates per track are defined by **ADR044**. "Decisive gate" = the last / highest-stakes **validation** gate that locks the WP.

| Track | Gates (ADR044) | **Tier 2 (cross-engine)** | **Tier 1 (sub-agent OK)** |
|-------|----------------|---------------------------|----------------------------|
| **EXPRESS** | BUILD | — *(functional + real execution; `canonical_cross_engine:false` documented — §6)* | BUILD |
| **STANDARD** | SPEC, BUILD, VALIDATE (, COMPLETE_QA) | **VALIDATE** | SPEC, BUILD |
| **MANAGED** | ELIG, SPEC, BUILD, VALIDATE (, COMPLETE) +2 human | **VALIDATE** *(+ escalation clause §5)* | ELIG, SPEC, BUILD |
| **RESEARCH** | none (team_00 reads) | — *(team_00 human read IS the check)* | — |
| **OPS** | BUILD | — *(functional + runbook/real-execution; escalate → Tier 2 if prod / ports / security — §6)* | BUILD |
| **CONTENT** | SPEC, DELIVER | **DELIVER** *(team_00 acceptance)* | SPEC |
| **HOTFIX** *(modifier)* | underlying track | underlying decisive gate — **may defer post-merge with MANDATORY retro Tier-2 inside the 4h worktree window** | underlying |

### 4.1 Closure/completeness gates are NOT validation gates
`L-GATE_COMPLETE_QA` (STANDARD) and `L-GATE_COMPLETE` (MANAGED) sit *after* `L-GATE_V`. They are **completeness/closure checkpoints** (unresolved-items / milestone closure per ADR044), **not** independent validation gates — they carry **no independence tier**. The **decisive validation gate** for STANDARD/MANAGED remains **L-GATE_V**. Check 49 ignores COMPLETE/COMPLETE_QA entries.

### 4.2 Anti-abuse clause (binding)
The §6 floor (EXPRESS/OPS decisive gate may be Tier-1) applies **only** to WPs the **ADR044 decision tree independently classifies** EXPRESS or OPS. **Invoking floor reasoning to downgrade a STANDARD / MANAGED / CONTENT WP's decisive gate to same-engine is a methodology violation and an Iron Rule #1 violation.** Track is set by ADR044's mechanical decision tree (enforced at SPEC — `validate_aos.sh` Checks 42/44), never by a desire to avoid cross-engine friction. Check 49's FAIL-promotion (§8) is the enforcement backstop.

---

## 5. Escalation clause (D1)

A **MANAGED or STANDARD** WP **adds Tier-2 at earlier gates** (BUILD and/or SPEC, beyond the default decisive gate) when **any** of: introduces/changes a state machine; security-sensitive; modifies governance/constitution; blast radius spans hub + spokes. The WP declares the escalation in `metadata.yaml`:

```yaml
escalation:
  triggered: true
  reason: "<why>"
  extra_tier2_gates: [L-GATE_BUILD]   # in addition to the default decisive gate
```

**Worked example — W6 itself:** constitutional WP (refines Iron Rule #1; blast radius = hub + all spokes) → escalation fires → **Tier-2 cross-engine at BOTH L-GATE_BUILD and L-GATE_VALIDATE.** The meta-rule is held to its own strictest bar.

---

## 6. EXPRESS / OPS floor (D3)

For **EXPRESS** and **OPS**, whose sole gate is L-GATE_BUILD, **functional-only (Tier-1) is a legitimate terminal state** — there is **no absolute cross-engine floor**. Conditions:
- `canonical_cross_engine: false` **MUST be documented explicitly** in `metadata.yaml` — never defaulted, never silent.
- Real execution / runbook proof is still required (depth is full).
- **OPS escalates to Tier-2** if it touches production, the port registry, or security.

This is the **ratified exception** to the program charter's "L-GATE_VALIDATE = cross-engine, always" language (charter §W6 line 81 predates the W6 thinking/discussion turn). **ADR053 is operative** where the two differ.

---

## 7. Metadata convention (`validation_tiering`)

Canonical block for `metadata.yaml`; read by `validate_aos.sh` Check 49:

```yaml
validation_tiering:
  matrix_ref: governance/directives/ADR053_TIERED_VALIDATION_MODEL_v1.0.0.md
  gates:
    L-GATE_<NAME>: {tier: 1|2, canonical_cross_engine: false|true, engine: <engine_id or TBD>}
escalation:            # only when §5 fires
  triggered: true
  reason: "<why>"
  extra_tier2_gates: [L-GATE_BUILD, ...]
```

**Legacy tolerance:** WPs without a `validation_tiering` block are **skipped** by Check 49 (not failed) — locked W1–W5 and in-flight WPs are never retro-invalidated.

---

## 8. Enforcement — `validate_aos.sh` Check 49

A new check verifies that each non-archived WP on a **Tier-2 track** (STANDARD/MANAGED/CONTENT/HOTFIX) whose decisive gate declares `canonical_cross_engine: true` carries a decisive-gate `engine:` distinct from the builder.

- **v1 = advisory (D4):** emits `[WARN]` lines but always returns PASS/SKIP — **never FAIL**. Legacy-tolerant (absent block ⇒ skip). Mirrors the Check 48 advisory idiom.
- **Promotion to FAIL (D4):** after **one milestone with zero false positives**, the WARN branches flip to `log_fail`. Promotion is a one-line change recorded here when it happens.
- **v1 simplification (called out for the Tier-2 reviewer):** vendor/model_family resolution is approximated by string-distinctness on the `engine:` field + a TBD-presence check; full ADR046 §2.5 resolution is the FAIL-promotion prerequisite.

---

## 9. Relationship to ADR044 / 046 / 047 / 032 (no conflict — ADR053 generalizes)

- **ADR044** sets the **gates per track**; ADR053 §4 sets **which gate needs which tier**. Additive note in the ADR044 track table.
- **ADR046 §2.5** defines *how* engine-distinctness is tested (`vendor` + `model_family`); ADR053 §3 Tier-2 **reuses it verbatim** and supplies the *which-gate-per-track* layer 046 left implicit.
- **ADR047 §2.1** already tiers at task-class level — **TC-7** "first-pass review" maps to **Tier-1**, **TC-8** "final/constitutional, cross-vendor required" maps to **Tier-2**. ADR053 **lifts** this from task-class to **gate × track doctrine** and names the tiers. No ADR047 decision changes.
- **ADR032** routing display: **Tier-2 (decisive) gates MUST present the canonical fenced routing block to a different engine**; intermediate Tier-1 gates may be sub-agent-attested inline.

---

## 10. Consequences

**Positive:** efficiency (no full cross-IDE round-trip on every intermediate check) + preserved rigor (decisive gate stays genuinely independent); the historic sub-agent/IR#1 contradiction is resolved; the model is explicit and machine-checkable.
**Negative / risks:** the §6 floor could be misused to dodge cross-engine friction (mitigated by §4.2 anti-abuse + ADR044 mechanical track tree + explicit `canonical_cross_engine:false` + Check 49 FAIL-promotion). The v1 check is advisory and uses string-distinctness (deliberate; FAIL-promotion tightens it).

---

## 11. Cross-References

| Topic | Artifact |
|---|---|
| Engine matrix + IR#1 enforcement mechanics | `governance/directives/ADR046_ENGINE_AND_EXECUTION_TIERING_v1.0.0.md` §2.5 |
| Task-class routing (TC-7 / TC-8) | `governance/directives/ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS_v1.0.0.md` §2.1 |
| Track model + gates per track | `governance/directives/ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` |
| Routing display conventions | `governance/directives/ADR032_ROUTING_DISPLAY_CONVENTIONS.md` |
| Iron Rule #1 (refined) | `CLAUDE.md` Iron Rules block #1; `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` constitutional rule #1 |
| Program charter | `_COMMUNICATION/team_100/PROGRAM_CHARTER_AOS_SESSION_MODEL_v1.0.0.md` §W6 |
| Cross-engine memory (reconciled) | `feedback_cross_engine_validation_canon` |

---

*Authored by team_100 under W6 (AOS-V4.5-WP-SESSION-W6-TIERED-VALIDATION). PROPOSED pending Tier-2 cross-engine BUILD + VALIDATE per the W6 escalation clause.*
