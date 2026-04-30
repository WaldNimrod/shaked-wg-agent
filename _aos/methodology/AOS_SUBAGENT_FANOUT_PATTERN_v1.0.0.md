# AOS Sub-Agent Fan-Out Pattern

**Document:** `methodology/AOS_SUBAGENT_FANOUT_PATTERN_v1.0.0.md`
**Version:** v1.0.0
**Status:** ACTIVE
**Author:** team_100 (Chief System Architect) — via AOS-V4-WP-CONTINUATION-AND-FANOUT
**Date:** 2026-04-30
**Supersedes:** (none — new document)
**Cross-reference:** ADR043 v1.3.0 §13; `_COMMUNICATION/team_00/V4_GAP_MATRIX_v1.1.0_AMENDMENT.md` §3

---

## Preface

This document canonicalizes the **sub-agent fan-out pattern** validated empirically in the TikTrack spoke during S005-P006-WP002 on 2026-04-29. That WP went from LOD200 to LOD500_LOCKED in a single day — a speed only possible because the orchestrator recognized a token-budget ceiling mid-spec and split the remaining work into independently coherent parallel sub-agent sessions.

This pattern is **meta-recursive**: the very WP that canonicalizes it (AOS-V4-WP-CONTINUATION-AND-FANOUT, W8) was itself produced by sub-agent fan-out during the AOS v4.0.0 planning session on 2026-04-30, when team_100's orchestrator spawned multiple Sonnet sub-agents to define all 10 v4 milestone WPs in parallel.

---

## 1. When to Fan Out

Fan-out is a **tool for specific conditions**, not a default workflow mode. Misapplied fan-out introduces synthesis overhead; over-splitting wastes coordination cost.

### 1.1 Primary trigger: token-budget ceiling

Fan out when the current agent session is approaching its token context limit and the remaining work is coherent enough to split into independently completable units.

**Indicators of token-budget ceiling:**
- Orchestrator explicitly signals "splitting to fit token budget" (as in MSG-HUB-20260429-002: "LOD300 PASS. Splitting LOD400 to fit token budget.")
- Current spec/document drafting is past 60% of estimated context window and ≥2 major sections remain
- Response quality begins to degrade (shorter answers, missed details, inconsistent cross-references)

### 1.2 Secondary trigger: true parallelism

Fan out when two sub-tasks are **genuinely independent** — i.e., Part B does not need Part A's output to proceed. Do NOT fan out if there is a data dependency; sequential execution is correct in that case.

**Genuine independence examples (fan out):**
- ADR document drafting and methodology document drafting (Part A and Part B of this WP's LOD400 pass)
- Two spoke domain propagation runs targeting different repos
- Parallel LOD200 spec drafting for multiple WPs (as in AOS v4.0.0 Phase B, where 10 WPs were spec'd in parallel)

**Hidden dependency examples (do NOT fan out — run sequentially):**
- Schema definition (Part A) → template update (Part B) when Part B imports Part A's field names
- DB migration (Part A) → API endpoint update (Part B) using the new schema
- Gate mandate issuance (Part A) → gate verdict (Part B) — verdict depends on mandate

### 1.3 Tertiary trigger: deadline pressure with parallelizable work

When SLA is tight and the work graph allows parallel execution, fan out even below the token-ceiling threshold. The TT precedent ran Part A and Part B concurrently and completed in ~7 minutes wall-clock (12:09Z to 12:16Z per MSG-HUB-20260429-005 and MSG-HUB-20260429-006) versus an estimated ~40-minute sequential run.

### 1.4 Do NOT fan out for

- Work that is small enough for a single context window (no benefit; added overhead)
- Work with complex cross-cutting state (fan-out produces partial artifacts that cannot be safely merged)
- Gate verdicts (IR#1: the builder decides, the validator validates; splitting the validator's work would break the vendor-distinct guarantee)

---

## 2. How to Split

### 2.1 Part naming convention

Parts are named alphabetically: **Part A, Part B, Part C** (maximum 3 parts per fan-out — beyond 3 indicates the WP itself should be split into separate WPs).

| Part | Naming | Purpose |
|------|--------|---------|
| Part A | First independent unit | Always the foundation; if Parts are sequential-ish, Part A has the fewest dependencies |
| Part B | Second independent unit | Can run concurrently with Part A after the split decision |
| Part C | Third independent unit (rare) | Only if Part A and Part B alone cannot complete the work and a third genuinely independent axis exists |

### 2.2 Split announcement

The orchestrator MUST announce the split via a formal MSG to the builder team **before** spawning sub-agents. This MSG is the audit record of the split decision.

**Required MSG content:**
```
Subject: [info] LOD{N} split (Part A + B) — {WP_ID}
Body: {Gate name} PASS. Splitting {next gate} to fit token budget.
      Part A: {one-sentence description of Part A scope}
      Part B: {one-sentence description of Part B scope}
```

Reference: MSG-HUB-20260429-002 ("LOD300 PASS. Splitting LOD400 to fit token budget.") is the canonical minimal example.

### 2.3 Each Part must be independently coherent

Before spawning sub-agents, verify:
- Part A, delivered in isolation, produces a complete, usable artifact (not a stub requiring Part B)
- Part B, delivered in isolation, produces a complete, usable artifact (not a stub requiring Part A)
- A human reading either Part alone can understand what was done without reading the other

### 2.4 Split checklist

Before announcing the split:
- [ ] Identify the independence boundary (what does Part A NOT need from Part B, and vice versa?)
- [ ] Name cross-references explicitly: "Part A will reference these fields by name; Part B must use exactly those field names"
- [ ] Assign each Part a responsible team or sub-agent invocation
- [ ] Set a synthesis checkpoint: when will the orchestrator combine outputs?

---

## 3. Sub-Agent Invocation Pattern

### 3.1 Invocation structure

Each Part is a separate, independently launched agent session. The orchestrator is responsible for:
1. Preparing a self-contained activation prompt for each Part (the sub-agent has NO memory of the orchestrator's context)
2. Launching both (or all) Parts — concurrently where possible
3. Collecting completion artifacts (PHASE_REPORT or COMPLETION MSG) from each Part
4. Synthesizing outputs before advancing to the next gate

### 3.2 Sub-agent activation prompt requirements

Each sub-agent activation prompt MUST include:
- The WP_ID and Part identifier ("Part A" or "Part B")
- The specific scope for this Part (files to create, files to modify, ACs to satisfy)
- Paths to required reading (spec, prior artifacts, schema files)
- The completion artifact target path
- The continuation block requirement (per ADR043 v1.3.0 §13): `next_step`, `handoff_to`, `handoff_context_pointer` in the completion artifact frontmatter

**Activation prompt template:**

```
You are {team_id} — {role description}.
WP: {WP_ID} — Part {A|B}
Scope: {one paragraph describing exactly what this Part covers}

Required reading:
1. {path/to/spec.md} — primary spec
2. {path/to/prior_artifact.md}

Your deliverables (Part {A|B} only):
- CREATE: {list of files}
- MODIFY: {list of files}

File completion artifact to: {_COMMUNICATION/team_XX/COMPLETION_{WP_ID}_Part{A|B}_v1.0.0.md}
Include next_step / handoff_to / handoff_context_pointer per ADR043 v1.3.0 §13.

Do NOT commit or push. Branch: {branch_name}.
```

### 3.3 Parallel vs sequential sub-agent execution

- **Parallel:** spawn both Parts concurrently (e.g., two separate Claude Code sessions running simultaneously in different terminal windows or worktrees). This is the maximum-speed configuration.
- **Sequential-parallel:** spawn Part A first, and while Part A runs, prepare Part B's activation prompt and spawn Part B before Part A finishes (pipeline overlap). Use when Part B preparation requires ~5 minutes but there is no data dependency.
- **Sequential:** spawn Part B only after Part A's completion artifact is filed. Use when Part B's scope depends on Part A's exact output (field names, file paths, etc.).

### 3.4 Completion artifact protocol

Each sub-agent Part MUST file a completion artifact at the designated path. Minimum required content:

```yaml
---
id: COMPLETION_{WP_ID}_Part{A|B}_v1.0.0
from: team_{NN}
to: team_{orchestrator}
date: {ISO-8601}
wp_id: {WP_ID}
part: "{A|B}"
status: BUILD_COMPLETE
next_step: "Orchestrator: verify Part {A|B} ACs, then synthesize with Part {other}."
handoff_to: team_{orchestrator}
handoff_context_pointer: {path/to/primary_deliverable.md}
---
```

---

## 4. IR#1 Maintenance in Fan-Out Chains

**Iron Rule #1:** builder engine vendor MUST be distinct from validator engine vendor. Fan-out does not relax this rule — it applies to the fan-out chain as a whole.

### 4.1 IR#1 in parallel Parts

When Part A and Part B are both build sub-tasks, they may use the same engine (both builder — same vendor). IR#1 is satisfied because the validator (separate gate) uses a different vendor.

```
Part A (claude-code, Anthropic) ─┐
                                  ├─→ synthesis ─→ L-GATE_BUILD (codex, OpenAI) → IR#1 PASS
Part B (claude-code, Anthropic) ─┘
```

This is the correct pattern used in TT S005-P006-WP002 and in this WP (AOS-V4-WP-CONTINUATION-AND-FANOUT).

### 4.2 IR#1 in cross-engine fan-out (OUT OF SCOPE — v4.0 note)

Cross-engine fan-out (Part A on Anthropic, Part B on OpenAI) is explicitly **out of scope for v4.0.0** (see LOD200 spec §2 OUT-OF-SCOPE). It introduces complex synthesis challenges and vendor-distinct guarantee ambiguity. Deferred to v4.1.

### 4.3 Validator is never a Part

The validation gate (L-GATE_BUILD, L-GATE_VALIDATE) is **never** split into Parts. The entire built artifact set is presented to a single validator session of the opposing-vendor engine. Splitting the validator's view would break IR#1's guarantee that the whole WP has been reviewed by a vendor-distinct engine.

### 4.4 Recording IR#1 compliance in metadata

`metadata.yaml` for any WP using fan-out MUST record:

```yaml
builder_engine: claude-code      # Anthropic vendor
validator_engine: codex          # OpenAI vendor — vendor-distinct: IR#1 enforced
fan_out_parts: [A, B]            # or [A] if no fan-out occurred
```

---

## 5. Synthesis

Synthesis is the orchestrator's responsibility: combining Part A and Part B outputs into a coherent whole, verifying cross-references, and advancing to the next gate.

### 5.1 Synthesis checklist

Before filing the synthesis report and advancing to the next gate:

- [ ] Both Part completion artifacts are present and `status: BUILD_COMPLETE`
- [ ] All files created/modified in each Part exist at their claimed paths
- [ ] Cross-references between Part A and Part B outputs are consistent (field names match, file paths match, version numbers match)
- [ ] No unresolved placeholder markers in any deliverable
- [ ] Continuation blocks (`next_step`, `handoff_to`, `handoff_context_pointer`) are present in all formal artifacts per ADR043 v1.3.0 §13
- [ ] The combined deliverable set satisfies all ACs in the WP LOD200 spec
- [ ] `validate_aos.sh` produces 0 FAIL on the combined work tree

### 5.2 Cross-reference verification

For each Part B artifact that references a Part A artifact (e.g., "methodology doc cites ADR043 v1.3.0 as its governance reference"), the orchestrator MUST:
1. Identify the reference (grep for the cited artifact name/path)
2. Confirm the cited artifact exists at the expected path
3. Confirm the cited content (section, field name, version number) matches what Part A actually produced

### 5.3 Synthesis failure handling

If Part A and Part B outputs conflict (e.g., incompatible field names, contradictory scope statements), the orchestrator MUST:
1. Stop synthesis
2. File a conflict report to `_COMMUNICATION/team_00/` describing the conflict
3. Re-spawn the conflicting Part with an updated activation prompt that constrains the conflict

Advancing to the next gate with unresolved synthesis conflicts is FORBIDDEN.

---

## 6. Worked Example — TT S005-P006-WP002 (2026-04-29)

This section documents the empirical precedent that validated the fan-out pattern. Data is observed (MSG timestamps), not instrumented.

### 6.1 Context

WP: S005-P006-WP002 (TikTrack spoke, Sprint 005, Program 006). Type: API integration work package. SLA: 1 sprint. Orchestrator: team_100 (claude-code Sonnet). Builder: team_30 (domain builder). Validator: team_190 (codex, OpenAI — IR#1).

### 6.2 Timeline

| Event | MSG / Artifact | Timestamp | Delta |
|-------|---------------|-----------|-------|
| LOD300 complete; split announced | MSG-HUB-20260429-002 | 2026-04-29T11:54:27Z | — |
| Part A spawn | (implicit — activation prompt issued) | ~11:55Z | +1 min |
| Part A BUILD COMPLETE | MSG-HUB-20260429-005 | 2026-04-29T12:09:59Z | +15 min |
| Part B BUILD COMPLETE | MSG-HUB-20260429-006 | 2026-04-29T12:16:07Z | +6 min (parallel with Part A tail) |
| Synthesis + L-GATE_BUILD validation | (team_190 codex) | ~12:30–13:00Z | ~44 min total build+validate |
| LOD500_LOCKED | (same day) | 2026-04-29 | < 24h from LOD200 |

**Total observed wall-clock (LOD200 → LOD500_LOCKED):** same day (under 24h). Parts A and B ran in a pipeline-overlap pattern: Part B spawn overlapped with Part A tail, producing only 6 minutes between Part A COMPLETE and Part B COMPLETE.

### 6.3 What the split looked like

MSG-HUB-20260429-002 (from team_100 to team_110, 11:54Z):

> "LOD300 PASS. Splitting LOD400 to fit token budget."

Part A scope: [API integration endpoints — the foundation layer of the WP deliverables]
Part B scope: [Test suite + documentation — the verification layer of the WP deliverables]

Both Parts were independently coherent. Part B's test suite targeted the endpoints Part A created, but the file paths and interface contracts were already specified in the LOD400 spec, so Part B could proceed concurrently without waiting for Part A's actual code.

### 6.4 Lessons applied to this pattern

1. **Announce before splitting** — MSG-HUB-20260429-002 was the audit record. Any team could see the split decision without reading code.
2. **Independence through spec, not code** — Part B ran before Part A finished because the spec defined interfaces precisely enough that Part B didn't need Part A's actual output.
3. **6-minute Part B completion** — Part B was smaller than Part A. Asymmetric Parts are normal and acceptable. The orchestrator does not need to equalize Part sizes.
4. **IR#1 preserved** — team_30 (Anthropic vendor, claude-code equivalent) built both Parts; team_190 (OpenAI vendor, codex) validated the combined result. IR#1 PASS.

### 6.5 Self-referential note

This methodology doc (Part of AOS-V4-WP-CONTINUATION-AND-FANOUT) was itself produced by a sub-agent fan-out chain. The AOS v4.0.0 Phase B WP definition session on 2026-04-30 spawned 10 parallel Sonnet sub-agents to define all 10 milestone WPs concurrently. The result: 10 LOD200 specs produced in a single orchestration session, validated by team_100, and recorded in `_COMMUNICATION/team_00/V4_GAP_MATRIX_v1.1.0_AMENDMENT.md`. The fan-out pattern ate its own dogfood before it was formally documented.

---

*Methodology version: v1.0.0 | Filed: 2026-04-30 | Author: team_100 via AOS-V4-WP-CONTINUATION-AND-FANOUT*
*Governed by: ADR043 v1.3.0 (continuation prompt standard) | Enforced by: team_190 at L-GATE_VALIDATE*
