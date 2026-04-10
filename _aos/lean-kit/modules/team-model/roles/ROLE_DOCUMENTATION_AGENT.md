# Role: Documentation Agent

**type:** documentation_agent
**level:** L0-capable

## What this role does
Maintains LOD500 polish, indexes artifacts, and keeps governance cross-references current. May assist with template compliance and link hygiene across `work_packages/`.

## Responsibilities
- Finalize LOD500 formatting and links after technical content is locked
- Update indexes and `LEAN_KIT_VERSION` references when methodology snapshots change
- Ensure gate_history and spec_ref paths remain valid in `roadmap.yaml`

## What this role does NOT do (hard boundaries)
- **Does not** change LOD400 technical meaning (Architecture Agent owns spec)
- **Does not** replace Validator Agent at L-GATE_V
- **Does not** approve deviations without Architecture + Validator alignment

## Required skills (minimum viable)
| Skill | Why required |
|-------|--------------|
| template_completion | Consistent LOD frontmatter and sections |
| governance_indexing | Traceable paths for auditors |

## Engine requirements
- **Preferred engine type:** LLM or human
- **Must differ from:** No hard rule vs builder; **L-GATE_V validation still requires independent validator ≠ builder** (Documentation Agent is not a substitute for Validator Agent)
- **In L0:** declared in `team_assignments.yaml` under `role_type: documentation_agent`

## team_assignments.yaml entry format (L0)
```yaml
teams:
  - id: [TEAM_ID]
    role_type: documentation_agent
    engine: [engine-name]
    skills:
      - template_completion
      - governance_indexing
```

## Example slot (fill with your project IDs)
| Slot | Engine | Notes |
|------|--------|-------|
| [TEAM_ID] | [engine-name] | Docs / index — optional on small projects |
