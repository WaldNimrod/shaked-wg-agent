---
id: ADR031_D04_APPROVAL
title: "ADR-031 Stage C — D-04 Formal Approval: Dual-Key Cross-Engine Governance Model"
version: "1.0.0"
status: APPROVED
author: Team 100 (Chief System Architect)
approved_by:
  - team_00
  - team_100
approval_date: "2026-04-13"
supersedes: null
adr_ref: ADR-031
stage: C
wp_ref: AOS-V315-WP-CROSS-ENGINE-PARITY
prerequisite: ADR031_MODEL_B_FILE_STRUCTURE
---

# ADR-031 Stage C — D-04 Formal Approval

## 1. Purpose

This directive formally ratifies the dual-key governance model for cross-engine configuration management. It is the Stage C completion artifact for ADR-031, marking the final resolution of all ADR-031 open items.

## 2. What is Being Approved

1. The **Model B file structure** (`governance/directives/ADR031_MODEL_B_FILE_STRUCTURE.md`) as the canonical layout for all engine-specific governance configuration files.
2. The **cross-engine equivalence model**: Claude Code slash commands → Cursor `.cursorrules` instruction blocks → Codex `SYSTEM_PROMPT.template` sections.
3. The **version synchronization procedure** (manual checklist in Model B directive §5) for maintaining parity when commands are updated.
4. The **Tier 1 / Tier 2 command classification**: 5 gate operations are cross-engine mandatory; 6 infrastructure commands are Claude Code-only.

## 3. Approval Chain

```
Drafted by:   Team 100 (Chief System Architect) — 2026-04-13
Reviewed by:  Team 00 (System Designer, Principal) — 2026-04-13
Approved by:  Team 00 + Team 100 (dual-key) — 2026-04-13
```

## 4. Governance Authority

- All engine configuration files listed in Model B §2 are governed by this directive.
- Changes to engine config **structure** (new sections, renamed sections, new files) require a new version of the Model B directive with dual-key re-approval.
- The version sync checklist in Model B §5 MUST be maintained whenever any Claude Code command is updated. Sync is verified at each L-GATE_BUILD.
- Team 00 retains sole write authority over `governance/directives/`.

## 5. ADR-031 Stage Completion Status

| Stage | Description | Status | Artifact |
|-------|------------|--------|----------|
| A | Parser/UI fixes | COMPLETE | Various code fixes (2026-03-14) |
| B | Model B file structure | COMPLETE | `governance/directives/ADR031_MODEL_B_FILE_STRUCTURE.md` |
| C | D-04 formal approval | COMPLETE | This file |

## 6. Binding Constraints

- This directive is **immutable** after dual-key approval.
- ADR-031 is now **fully resolved** — no remaining open items.
- Future cross-engine governance changes operate under the Model B framework established by this directive, not as ADR-031 extensions.

---

*ADR-031 Stage C | D-04 Formal Approval | v1.0.0 | 2026-04-13*
*Approved by: Team 00 (System Designer) + Team 100 (Chief System Architect)*
