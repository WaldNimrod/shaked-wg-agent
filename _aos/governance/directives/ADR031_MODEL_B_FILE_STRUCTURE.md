---
id: ADR031_MODEL_B_FILE_STRUCTURE
title: "ADR-031 Stage B — Model B Canonical File Structure for Cross-Engine Governance"
version: "1.1.0"
status: APPROVED
author: Team 100 (Chief System Architect)
approved_by:
  - team_00
  - team_100
approval_date: "2026-04-13"
supersedes: null
adr_ref: ADR-031
stage: B
wp_ref: AOS-V315-WP-CROSS-ENGINE-PARITY
---

# ADR-031 Stage B — Model B Canonical File Structure

## 1. Purpose

This directive defines the canonical file locations, naming conventions, and equivalence mapping for all engine-specific governance configuration files across the AOS ecosystem. It is the structural foundation for cross-engine governance parity: every engine environment that participates in gate operations MUST have its governance instructions located and named according to this directive.

## 2. Canonical Engine Config Locations

| Engine | Config File | Location | Format |
|--------|-----------|----------|--------|
| Claude Code | Slash commands | `.claude/commands/AOS_*.md` | One file per command, markdown instruction |
| Cursor Composer | Context rules | `.cursorrules` (project root) | Single file, structured sections |
| OpenAI Codex | System prompt template | `lean-kit/modules/context-onboarding/templates/SYSTEM_PROMPT.template` | Template with `{{VARIABLE}}` substitution |

## 3. Naming Conventions

- **Claude Code commands:** `AOS_{command_name}.md` (e.g., `AOS_gate-mandate.md`, `AOS_validate.md`)
- **Cursor sections:** `## AOS Gate Operations — {Command Name}` heading within `.cursorrules` (e.g., `## AOS Gate Operations — Gate Mandate`)
- **Codex template sections:** `## Gate Operations` heading within `SYSTEM_PROMPT.template`, with `### {Operation Name}` subsections (e.g., `### Gate Mandate Generation`)

## 4. Cross-Engine Equivalence Matrix

| Command | Claude Code | Cursor Composer | Codex |
|---------|-----------|----------------|-------|
| Gate Mandate | `/AOS_gate-mandate` (.claude/commands/AOS_gate-mandate.md) | .cursorrules §AOS Gate Operations — Gate Mandate | SYSTEM_PROMPT.template §Gate Operations > Gate Mandate Generation |
| QA Functional Acceptance | `/AOS_qa` (.claude/commands/AOS_qa.md) | .cursorrules §AOS Gate Operations — QA Functional Acceptance | SYSTEM_PROMPT.template §Gate Operations > QA Functional Acceptance |
| Constitutional Validation | `/AOS_validate` (.claude/commands/AOS_validate.md) | .cursorrules §AOS Gate Operations — Constitutional Validation | SYSTEM_PROMPT.template §Gate Operations > Constitutional Validation |
| Gate Status | `/AOS_gate-status` (.claude/commands/AOS_gate-status.md) | .cursorrules §AOS Gate Operations — Gate Status Check | SYSTEM_PROMPT.template §Gate Operations > Gate Status |
| Governance Update | `/AOS_gov-update` (.claude/commands/AOS_gov-update.md) | .cursorrules §AOS Gate Operations — Governance Update | SYSTEM_PROMPT.template §Gate Operations > Governance Update |
| Session handoff | `/AOS_handoff` (`.claude/commands/AOS_handoff.md`) | `.cursorrules` §Output Display Convention — **handoff exception**; `governance/directives/ADR032_ROUTING_DISPLAY_CONVENTIONS.md` §3.3 | `SYSTEM_PROMPT.template` §Gate Operations → **Session Handoff** |

**Note:** Session handoff uses **behavioral parity** (activation block must appear in chat; file is durable record), not a named `## AOS Gate Operations — …` mirror block. Tier 1 row-style equivalence does not apply; ADR032 §3.3 is binding.

## 5. Version Synchronization Checklist

**Machine-readable SSoT:** `lean-kit/modules/validation-quality/schemas/aos_commands_manifest.yaml` lists every `AOS_*.md` file. `validate_aos_commands.sh` (invoked from `validate_aos.sh` Check 16 on hub, and from `propagate_governance.sh` Phase 5b) MUST PASS after any change to the command set or manifest.

When any Claude Code command is updated, the corresponding Cursor and Codex equivalents MUST be updated in the same commit (Tier 1). This checklist tracks sync status.

| Command | Claude (.claude/commands/) | Cursor (.cursorrules) | Codex (SYSTEM_PROMPT.template) | Last Sync Date | Sync Status |
|---------|--------------------------|----------------------|-------------------------------|---------------|-------------|
| gate-mandate | 1.0.4 | 1.0.4 | 1.0.4 | 2026-04-18 | IN_SYNC |
| qa | 1.0.0 | 1.0.0 | 1.0.0 | 2026-04-15 | IN_SYNC |
| validate | 1.0.0 | 1.0.0 | 1.0.0 | 2026-04-15 | IN_SYNC |
| gate-status | 1.0.0 | 1.0.0 | 1.0.0 | 2026-04-15 | IN_SYNC |
| gov-update | 1.0.0 | 1.0.0 | 1.0.0 | 2026-04-15 | IN_SYNC |

## 6. Tier 2 Exclusions

The following commands are Claude Code infrastructure or hub-only operations and do NOT require cross-engine equivalents:

| Command | Reason for Claude-only |
|---------|----------------------|
| `/AOS_archive` | Post-gate artifact relocation to `_archive/` — filesystem and `ARCHIVE_MANIFEST.md`; IDE-specific tooling. |
| `/AOS_gov-sync` | Narrow scope of `/AOS_gov-update` — team contracts only. Cursor/Codex teams don't propagate governance. |
| `/AOS_server` | Wraps anthropic-skills `/server` — Claude Code infrastructure feature. |
| `/AOS_mail` | Canonical team inbox check — reads `_COMMUNICATION/team_XX/inbox/`, executes instructions, returns feedback. All engines. |
| `/AOS_dispatch` | One-shot inter-team task with `expects_response: true` — `POST /api/messaging/send`, display activation (ADR032), show `/AOS_mail --watch` (AOS-V328). |
| `/AOS_SendMail` | Canonical team message send — any team, any domain, all engines. Replaced `/AOS_send`. |
| `/AOS_send` | **DEPRECATED (2026-04-21, AOS-V327)** — stub only, redirects to `/AOS_SendMail`. |
| `/AOS_project-init` | Multi-phase wizard requiring Write tool, file creation, script execution. Cursor/Codex don't create projects. |
| `/AOS_domain-health` | Cross-domain audit requiring access to all spoke repos. Hub operation only. |
| `/AOS_decide` | Decision Brief generator — Tier 2 classification; cross-engine upgrade path open if needed. |
| `/AOS_help` | Static command reference — Claude Code native display. Cursor/Codex environments use `.cursorrules` §AOS Gate Operations as their reference. |
| `/AOS_session` | Session worktree isolation (ADR052 W2) — delegates to `scripts/start_worktree.sh` + pre-flight/reaper; hub local-mac OPS only until W3 register. |

## 7. Amendment Rules

- This directive is **immutable** after dual-key approval, except as below.
- Addition of a new engine environment requires a **v2.0.0** of this directive with full dual-key re-approval.
- The Version Synchronization Checklist (§5) is the **ONLY** section permitted for routine in-place edits (checklist maintenance: updating sync dates, version numbers, and status).
- **Minor amendments (v1.x.0):** When a **later approved directive** (e.g. ADR032) changes cross-engine obligations for a command, §4 and §6 MAY be updated in the same commit as that directive so Tier classification and equivalence tables stay consistent. Bump `version` in frontmatter and record the amendment in the footer.

---

*ADR-031 Stage B | Model B File Structure | v1.1.0 | 2026-04-17*
*Approved by: Team 00 (System Designer) + Team 100 (Chief System Architect)*
*Amendment 2026-04-15: §5 manifest SSoT + §6 `/AOS_archive` Tier 2 row (Team 00 approved implementation WP).*
*Amendment 2026-04-17: §5 checklist — gate-mandate sync bump to 1.0.2 (CANON doc + stub; ADR036).*
*Amendment 2026-04-17: v1.1.0 — §4 Session handoff behavioral parity row (ADR032 §3.3); `/AOS_handoff` removed from §6 Tier 2; §7 minor-amendment path for cross-directive consistency.*
*Amendment 2026-04-18: §5 checklist — gate-mandate sync bump to 1.0.3 (CANON v1.0.1 numbered WP options + default row first).*
*Amendment 2026-04-18: §5 checklist — gate-mandate sync bump to 1.0.4 (CANON v1.0.2 Phase 3.5 remediation verification before resubmission).*
