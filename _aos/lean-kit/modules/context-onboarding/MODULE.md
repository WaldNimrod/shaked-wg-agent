---
id: context-onboarding
name: "Multi-Engine Context Onboarding"
version: "1.0.1"
profile_min: L0
description: "Generates engine-specific context files (CLAUDE.md, .cursorrules, system prompt) from canonical templates."
dependencies: []
scripts:
  generate: scripts/generate_context.sh
  validate: scripts/validate_context_consistency.sh
---

# Module 12 — Multi-Engine Context Onboarding

## Purpose
Generates engine-specific context files (CLAUDE.md, .cursorrules, system prompt) from canonical templates. Ensures all engines receive consistent project context, iron rules, and boundary constraints. **Mandatory reads are capped** (see templates); agents must read `_aos/context/PROJECT_CONTEXT.md` first per Directory Canon Part 1a.

## Contents
| File | Description |
|------|-------------|
| templates/CLAUDE_MD.template | Claude Code context template |
| templates/CURSORRULES.template | Cursor context template |
| templates/SYSTEM_PROMPT.template | OpenAI/generic system prompt template |
| scripts/generate_context.sh | Renders template for a given engine |
| scripts/validate_context_consistency.sh | Checks that all context files share the same iron rules and boundaries |

## Scripts
- `generate`: `scripts/generate_context.sh`
- `validate`: `scripts/validate_context_consistency.sh`
