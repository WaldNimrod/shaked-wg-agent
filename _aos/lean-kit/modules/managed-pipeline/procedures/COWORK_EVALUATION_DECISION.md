---
decision_id: R-OPS-2
date: 2026-04-12
status: DECIDED
decided_by: team_110
approved_by: team_00 (pending)
---

# R-OPS-2: Cowork Environment Evaluation — Decision Record

## Research Question (from CLAUDE_SDK_MIGRATION_PATH.md)

> Does the Cowork environment provide tools that improve L2.5 execution?
> - Built-in tools that map to the tool schema?
> - Persistent session that survives between phases?
> - Multi-agent coordination primitives?

## Investigation Summary

Three execution environments were evaluated for S005-P004 Phase 4C (3 WPs, linear execution with inter-WP validation):

### 1. Claude Cowork Desktop (`/setup-cowork`)

- **What it is:** Claude Desktop feature with isolated VM, plugin marketplace, connectors to external services (email, calendar, docs).
- **Execution model:** Single agent, UI-driven, no programmatic hooks.
- **Findings:**
  - `/setup-cowork` is a guided onboarding skill — installs plugins, connects services.
  - Cowork is designed for **business workflows** (reports, emails, data processing), NOT code development.
  - No `pytest` integration, no git hooks, no file-level validation.
  - No `TaskCompleted` or `PostToolUse` hooks for automated quality gates.
- **Verdict:** NOT SUITABLE for code implementation work packages.

### 2. Claude Code Agent Teams (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)

- **What it is:** Experimental feature. Multiple Claude Code sessions (Lead + Teammates) with shared task list, inter-agent messaging, dependency tracking.
- **Execution model:** Parallel sessions, each with own context window.
- **Findings:**
  - Designed for **parallel** work (competing hypotheses, independent modules).
  - S005-P004 WPs have **serial dependencies** (WP001 field renames must complete before WP002/WP003).
  - Token cost scales linearly with team size.
  - Experimental — session resumption does not restore teammates.
  - File collision risk if two teammates edit same file.
- **Verdict:** SUBOPTIMAL. Parallelism adds complexity without benefit for serial WPs. Experimental status is a risk.

### 3. Claude Code Single Session + Serial Mandates

- **What it is:** One Claude Code session executes WP mandates in linear order with validation between each.
- **Execution model:** Sequential — WP1 → validate → WP2 → validate → WP3 → final validation.
- **Findings:**
  - Full control over execution order and validation gates.
  - `pytest` and grep verification run between WPs.
  - No file collision risk (single writer).
  - Hooks available for automated checks.
  - Stable (production feature, not experimental).
  - Token-efficient (one session).
- **Verdict:** RECOMMENDED.

## Decision

**Use Claude Code single session with serial mandate execution.**

### Rationale

1. **Serial dependencies demand serial execution.** WP001 renames `price_chf` → `price` across 14+ files. WP002 and WP003 consume these renamed fields. Parallel execution would cause merge conflicts and inconsistent state.

2. **Validation gates require control flow.** The mandate specifies: implement WP → run tests → verify ACs → proceed only if pass. This is a sequential control flow, not a parallel fan-out.

3. **Stability over novelty.** Agent Teams is experimental. This is a first execution of the cowork mandate pattern — adding an experimental execution environment doubles the risk surface.

4. **Field experience note (Team 00 directive):** Three LOD400 specs executed as a single linear mandate with per-WP validation + final comprehensive validation. This pattern prevents cascading failures where WP2 builds on broken WP1 output.

## Execution Pattern

```
MANDATE ACTIVATION (single Claude Code session)
│
├─ Phase 1: WP001 (Data Field Generalization)
│  ├─ Execute mandate
│  ├─ Run pytest
│  ├─ Verify ACs (grep checks, field assertions)
│  └─ GATE: all tests pass? → continue / → HALT
│
├─ Phase 2: WP002 (Dynamic Scraper Registry)
│  ├─ Execute mandate
│  ├─ Run pytest
│  ├─ Verify ACs (FQN resolution, grep checks)
│  └─ GATE: all tests pass? → continue / → HALT
│
├─ Phase 3: WP003 (Keyword/Label Locale)
│  ├─ Execute mandate
│  ├─ Run pytest
│  ├─ Verify ACs (locale assertions, keyword checks)
│  └─ GATE: all tests pass? → continue / → HALT
│
└─ Phase 4: Final Comprehensive Validation
   ├─ Full pytest suite (all tests, all WPs together)
   ├─ Cross-WP grep verification (zero legacy fields)
   ├─ Cross-WP integration check (renamed fields used consistently)
   ├─ Linter clean (ruff check)
   └─ GATE: all pass? → COMPLETE / → HALT + report
```

## Future Considerations

- **When to re-evaluate Agent Teams:** When WPs are genuinely independent (no shared files, no field rename cascades) and can benefit from parallel execution.
- **When to re-evaluate Cowork Desktop:** When L2.5 needs non-code automation (report generation, stakeholder communication, CI/CD orchestration).
- **R-OPS-2 status:** CLOSED for S005-P004. Re-open for S006+ if parallel WP patterns emerge.
