# MODULE_INDEX — Path Migration Reference (v3.1.0 → v3.1.1)

This file maps v3.1.0 flat paths to v3.1.1 modular paths.
Projects upgrading from v3.1.0 should update any hardcoded references.

## Path Mapping

| v3.1.0 path | v3.1.1 path | Module |
|---|---|---|
| `config_templates/roadmap.yaml.template` | `modules/project-governance/config_templates/roadmap.yaml.template` | 01 |
| `config_templates/team_assignments.yaml.template` | `modules/project-governance/config_templates/team_assignments.yaml.template` | 01 |
| `config_templates/README.md.template` | `modules/project-governance/config_templates/README.md.template` | 01 |
| `config_templates/context/ACTIVATION_ARCH.md.template` | `modules/agent-activation/context/ACTIVATION_ARCH.md.template` | 06 |
| `config_templates/context/ACTIVATION_BUILDER.md.template` | `modules/agent-activation/context/ACTIVATION_BUILDER.md.template` | 06 |
| `config_templates/context/ACTIVATION_VALIDATOR.md.template` | `modules/agent-activation/context/ACTIVATION_VALIDATOR.md.template` | 06 |
| `gates/*` | `modules/gate-workflow/gates/*` | 02 |
| `team_roles/*` | `modules/team-model/roles/*` | 03 |
| `templates/*` | `modules/document-lifecycle/templates/*` | 04 |
| `scripts/validate_aos.sh` | `modules/validation-quality/scripts/validate_aos.sh` | 08 |
| `scripts/migrate_sfa_roadmap.py` | `modules/project-governance/scripts/migrate_sfa_roadmap.py` | 01 |
| `examples/*` | `modules/project-governance/examples/*` | 01 |
| `rtl-bidi-standards/*` | `modules/standards-conventions/rtl-bidi/*` | 11 |

## Notes

- No backward-compatibility shim exists. All project snapshots must be updated to v3.1.1.
- Existing v3.1.0 snapshots (physical copies in projects) continue working at their adopted version.
- `VERSION_POLICY.md` and `LEAN_KIT_VERSION.md` remain at lean-kit root.
