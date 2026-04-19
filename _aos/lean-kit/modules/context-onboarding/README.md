# Module 12 — Multi-Engine Context Onboarding

Generates engine-specific context files from canonical AOS templates.

## Usage

### Generate a context file
```bash
bash scripts/generate_context.sh <project_root> <engine> [--output <path>]
```
Engines: `claude-code`, `cursor`, `openai`

### Validate consistency across engines
```bash
bash scripts/validate_context_consistency.sh <project_root>
```
Exit 0 = consistent, Exit 1 = drift detected.

## Template Variables

All variables are resolved from `_aos/` files in the project:

| Variable | Source |
|----------|--------|
| `{{PROJECT_ID}}` | `_aos/project_identity.yaml` → `project_id` |
| `{{DISPLAY_NAME}}` | `_aos/project_identity.yaml` → `display_name` |
| `{{PROFILE}}` | `_aos/metadata.yaml` → `profile` |
| `{{TEAM_MODEL}}` | `_aos/team_assignments.yaml` (formatted list) |
| `{{IRON_RULES}}` | `_aos/team_assignments.yaml` or `_aos/governance/` |
| `{{MANDATORY_READS}}` | `_aos/context/PROJECT_CONTEXT.md` |
| `{{FORBIDDEN_PATTERNS}}` | `_aos/project_identity.yaml` → `boundaries.forbidden_patterns` |
| `{{ALLOWED_WRITE_ROOTS}}` | `_aos/project_identity.yaml` → `boundaries.allowed_write_roots` |
