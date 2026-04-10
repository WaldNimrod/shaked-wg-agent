# Migration Guide: v3.1.0 → v3.1.1

## What Changed

v3.1.1 reorganizes the flat lean-kit structure into 11 modules under `modules/`.
No `_aos/` schema changes. Same roadmap.yaml, same team_assignments.yaml, same metadata.yaml.

### Structural Changes

- All content files moved from flat directories into `modules/[module-name]/`
- 11 MODULE.md descriptors added (one per module)
- `profiles/` directory added (L0.yaml, L2.yaml, L3.yaml)
- `MODULE_INDEX.md` at root maps old paths → new paths
- `scripts/` directory removed (validate_aos.sh moved to modules/validation-quality/)
- `rtl-bidi-standards/` moved to `modules/standards-conventions/rtl-bidi/`

### Key Path Changes

| What | v3.1.0 path | v3.1.1 path |
|------|------------|------------|
| validate_aos.sh | `scripts/validate_aos.sh` | `modules/validation-quality/scripts/validate_aos.sh` |
| Gate definitions | `gates/` | `modules/gate-workflow/gates/` |
| LOD templates | `templates/` | `modules/document-lifecycle/templates/` |
| Role definitions | `team_roles/` | `modules/team-model/roles/` |
| ACTIVATION templates | `config_templates/context/` | `modules/agent-activation/context/` |
| Project templates | `config_templates/` | `modules/project-governance/config_templates/` |

See `MODULE_INDEX.md` for the complete mapping.

## How to Update Your Project

### Step 1: Replace _aos/lean-kit/

```bash
rm -rf _aos/lean-kit
cp -R /path/to/agents-os/lean-kit _aos/lean-kit
```

### Step 2: Update metadata.yaml

```yaml
lean_kit_version: "3.1.1+[SHA]"
lean_kit_source_sha: "[full SHA]"
lean_kit_source_date: "[date]"
```

### Step 3: Update validate_aos.sh references

In `_aos/context/ACTIVATION_BUILDER.md` and `_aos/README.md`, update:

```
OLD: bash _aos/lean-kit/scripts/validate_aos.sh .
NEW: bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

### Step 4: Verify

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Must return exit 0 (9/9 PASS).

## What Does NOT Change

- `_aos/` directory structure (same files: roadmap.yaml, team_assignments.yaml, metadata.yaml, etc.)
- validate_aos.sh checks (same 9 checks, same logic)
- roadmap.yaml schema (v1.1, unchanged)
- team_assignments.yaml schema (unchanged)
- metadata.yaml fields (unchanged)
- Iron Rules (unchanged)
