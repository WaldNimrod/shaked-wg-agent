# ADR041 — Command Architecture Unification (Iron Rule #13)

**Status:** LOCKED
**Version:** v1.0.0
**Date:** 2026-04-19
**Owner:** Team 00 (Principal)
**Executor:** Team 100 (Chief Architect)
**WP reference:** AOS-V323-WP-COMMANDS-UNIFICATION

---

## Context

AOS hub has 15 slash commands totaling 2,663 lines (2026-04-19 snapshot). Several commands (gov-sync 284, gov-update 294, qa 316, validate 390, project-init 267, decide 255) embed large reference tables + re-implement context assembly that Python modules in `core/modules/management/` already perform. This created three problems:

1. **Token cost** — every invocation loads the full command text into the agent's context (hundreds of tokens per command).
2. **Drift risk** — canonical tables (e.g., CANONICAL OPTIONS LOOKUP, FIRST ACTION MATRIX) duplicated in markdown files diverge from their Python counterparts over time.
3. **Cross-engine inconsistency** — Claude Code, Cursor, Codex all read commands differently; without a unified API, each engine re-implements logic.

A prior WP (AOS-V322 Prompt Quality Upgrade + ADR040 follow-up 2026-04-19) demonstrated the correct pattern: `/AOS_handoff` was refactored from 607 → 116 lines by delegating 80% of its logic to `GET /api/prompts/generate?mode=handoff` + centralizing options/first-action tables in `core/modules/management/team_options.py`. All engines now call the same endpoint. Single source of truth.

This ADR generalizes that pattern as a system-wide rule.

## Decision

### Iron Rule #13 (NEW)

> **Every AOS slash command whose logic is deterministic given inputs MUST be a thin orchestrator over an API endpoint in `core/modules/management/`. The command file carries: (1) argument parsing, (2) interactive user preview where applicable, (3) API invocation, (4) file write + display. The API carries all deterministic logic, data assembly, and SSoT tables. Command files MUST be ≤150 lines and MUST declare `summary:` + `category:` YAML frontmatter.**

### Scope

**In scope (Iron Rule #13 applies):**
- All commands with `category: gate|session|governance|project|infrastructure`
- All commands whose output is deterministic given inputs

**Out of scope (Iron Rule #13 does NOT apply):**
- `category: decision` — commands requiring human judgment (e.g., `/AOS_decide`); orchestrator may still delegate Phase 1 context loading but Phase 2+ creative/judgment work stays
- Thin wrappers around underlying skills (mail/send/server AOS_ wrappers) — inherently thin already
- `/AOS_help` itself — generator command reading other commands' frontmatter (meta-command)

### Canonical SSoT modules (one per concern)

| Module | Purpose | Consumer commands |
|--------|---------|-------------------|
| `core/modules/management/team_options.py` | CANONICAL_OPTIONS + FIRST_ACTION tables | `/AOS_handoff`, empty-task prompt |
| `core/modules/management/verdict_helpers.py` (V323) | Team context loading + mandate artifact resolution + information barrier | `/AOS_qa`, `/AOS_validate` |
| `core/modules/management/mandates.py` (V323) | Mandate signal detection + template rendering | `/AOS_gate-mandate` |
| `core/modules/management/project_create.py` (V323) | Project tree creation + template substitution | `/AOS_project-init` |
| `core/modules/management/archive.py` (V323) | WP artifact archival + manifest writing | `/AOS_archive` |
| `core/modules/management/health.py` (V323) | Cross-domain health checks | `/AOS_domain-health` |

### Three-layer enforcement

**Layer A — Structural (validate_aos.sh):**
- Check 30: any `.claude/commands/AOS_*.md` with `category: gate|session|governance` exceeding 150 lines → FAIL
- Check 31: every `.claude/commands/AOS_*.md` MUST have YAML frontmatter with `summary:` + `category:` → FAIL if missing

**Layer B — Canonical template (future commands):**
- `methodology/AOS_COMMAND_ARCHITECTURE_v1.0.0.md` defines the command template
- New commands MUST follow the template or be rejected at PR/review time

**Layer C — Cross-engine uniformity:**
- `CLAUDE.md` + `.cursorrules` + spoke templates document the command-API mapping
- Every engine calls the same API endpoint for the same operation

### Exception procedure

A command may exceed 150 lines or lack the standard frontmatter only with:
1. Explicit Team 00 written approval
2. ADR amendment documenting the exception + rationale

### Full 7-phase CANON port (DR-2 full) — deferred

This ADR authorizes **minimal viable** port of `lean-kit/modules/validation-quality/docs/AOS_GATE_MANDATE_CANON_v1.0.0.md` (826 lines of prose) into deterministic Python. Scope of V323's D7:
- CANON Phase 0 (signal detection: A/B/C/M)
- CANON Phase 5-6 (template rendering from `MANDATE_TEMPLATE.md`)

Full 7-phase port (Phases 1-4 + 7 — context gathering, option menus, routing logic, ARTIFACT_INDEX integration) deferred to a future V324 WP.

## Consequences

**Immediate:**
- 14 commands (all except `/AOS_help`, `/AOS_handoff` which are already compliant) refactored to ≤150 lines + thin-orchestrator pattern
- 7 new API endpoints live in `core/modules/management/dashboard_routes.py`
- 5 new SSoT Python modules
- 2 new validate_aos.sh checks enforce the invariant

**Short-term:**
- Token cost per agent session drops by ~500-1,000 tokens (less command text loaded)
- Drift risk eliminated for covered commands (single source enforced by Check 30/31)
- Cross-engine parity — Cursor/Codex/Desktop call same APIs as Claude Code

**Long-term:**
- New commands follow canonical template → zero new drift
- SSoT modules are testable (pytest coverage per module)
- API surface becomes the integration point for dashboard UI, CI/CD, and external tools

## Relates to / supersedes

- **Relates to:** ADR032 (Routing Display Conventions v1.2.0), ADR034 (DB SSoT), ADR038 (Governance File Source-Mirror), ADR040 (Authority Lockdown Iron Rule #12)
- **Supersedes:** nothing directly; this ADR adds a new Iron Rule + canonical architecture
- **Bumps:** `methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md` → v1.2.0

## References

- `methodology/AOS_COMMAND_ARCHITECTURE_v1.0.0.md` (canonical pattern + command template)
- `_aos/work_packages/AOS-V323-WP-COMMANDS-UNIFICATION/LOD400_spec.md`
- `_COMMUNICATION/team_00/APPROVAL_AOS-V323-WP-COMMANDS-UNIFICATION_2026-04-19.md`
- Precedent: `/AOS_handoff` refactor (2026-04-19) + `core/modules/management/team_options.py`

---

**LOCKED 2026-04-19 — Iron Rule #13 is immutable. Amendments require a superseding ADR.**
