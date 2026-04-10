# Role: Architecture Agent

**type:** architecture_agent
**level:** All (L0 / L2 / L3 methodology)

## What this role does
Authors and maintains LOD100–LOD400 documentation, performs architectural review at defined gates, and issues mandates or spec corrections so builders have an unambiguous LOD400 before L-GATE_S.

## Responsibilities
- Produce LOD200 (and LOD300 on TRACK_B) and LOD400 to template quality
- Ensure acceptance criteria are testable and traceable
- Participate in L-GATE_S approval and L-GATE_V architectural perspective when required
- Issue spec updates when scope or ACs change

## What this role does NOT do (hard boundaries)
- **Does not** implement production features (except documented architect-only exceptions)
- **Does not** approve its own work as the independent L-GATE_V validator
- **Does not** bypass LOD sequencing (no LOD400 without approved LOD200 / LOD300 as required)

## Required skills (minimum viable)
| Skill | Why required |
|-------|--------------|
| lod_spec_authoring | Produce normative specs at correct LOD |
| iron_rule_knowledge | Enforce track, gates, and cross-engine rules |
| mandate_issuance | Clear handoffs to builder and validator |

## Engine requirements
- **Preferred engine type:** LLM or human (project choice)
- **Must differ from:** Validator engine for the same work package at L-GATE_V when validator reviews implementation (validator ≠ builder; architect does not replace validator)
- **In L0:** declared in `team_assignments.yaml` under key matching `role_type: architecture_agent`

## team_assignments.yaml entry format (L0)
```yaml
teams:
  - id: [TEAM_ID]
    role_type: architecture_agent
    engine: [claude-code|gemini|openai-codex|human]
    skills:
      - lod_spec_authoring
      - iron_rule_knowledge
      - mandate_issuance
```

## Example slot (fill with your project IDs)
| Slot | Engine | Notes |
|------|--------|-------|
| [TEAM_ID] | [engine-name] | Spec author; LOD200/LOD400 |
