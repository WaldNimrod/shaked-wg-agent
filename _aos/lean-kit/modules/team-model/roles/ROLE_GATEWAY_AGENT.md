# Role: Gateway Agent

**type:** gateway_agent
**level:** All (optional — not all projects require this role)

## What this role does
Coordinates gate transitions, generates build mandates for builder agents, and manages WP routing within the project. Project-local equivalent of Teams 10/11 gateway function in the legacy numbered model.

## Responsibilities
- Generate build mandates at L-GATE_S → L-GATE_B transition
- Coordinate gate documentation and artifact routing between roles
- Manage WP assignment handoffs between architecture_agent and builder_agent
- Track gate status in roadmap.yaml during active build phases

## What this role does NOT do (hard boundaries)
- **Does not** implement features or write code (builder_agent scope)
- **Does not** perform independent validation (validator_agent scope)
- **Does not** author LOD200/LOD400 specs (architecture_agent scope)
- **Does not** approve gate results (system_designer scope)

## Required skills (minimum viable)
| Skill | Why required |
|-------|--------------|
| gate_coordination | Manage L-GATE transitions and timing correctly |
| mandate_generation | Produce unambiguous build instructions from LOD400 |

## Engine requirements
- **Preferred engine type:** LLM
- **EXEMPT from cross-engine Iron Rule** — gateway_agent does not build or validate; the cross-engine rule applies to the builder/validator pair only.
- **In L0:** declared in `team_assignments.yaml` under `role_type: gateway_agent`

## team_assignments.yaml entry format (L0)
```yaml
teams:
  - id: [project-prefix]_gate
    role_type: gateway_agent
    engine: [cursor-composer|openai-codex|gemini|claude-code]
    skills:
      - gate_coordination
      - mandate_generation
```

## Example slot (fill with your project IDs)
| Slot | Engine | Notes |
|------|--------|-------|
| [project-prefix]_gate | [engine-name] | Gateway — exempt from cross-engine rule |
