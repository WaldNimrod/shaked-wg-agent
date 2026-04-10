# Role: Builder Agent

**type:** builder_agent
**level:** All

## What this role does
Implements the approved LOD400 specification, runs same-engine QA at L-GATE_B, and produces the LOD500 as-built draft for independent validation at L-GATE_V.

## Responsibilities
- Implement all in-scope LOD400 components and ACs
- Record fidelity in LOD500 §2 before validator review
- Raise spec ambiguities to Architecture Agent (spec correction) instead of silent drift
- Execute unit/integration tests per LOD400 §7

## What this role does NOT do (hard boundaries)
- **Does not** declare L-GATE_V PASS on its own work (cross-engine rule)
- **Does not** change scope without LOD400 version bump or documented deviation
- **Does not** select itself as validator

## Required skills (minimum viable)
| Skill | Why required |
|-------|--------------|
| [language/framework] | Deliver working implementation |
| lod400_execution | Map ACs to code and tests |
| lod500_authoring | Accurate as-built documentation |

## Engine requirements
- **Preferred engine type:** LLM
- **Must differ from:** **Validator agent engine (IRON RULE)** — same engine for builder and validator blocks L-GATE_V
- **In L0:** declared in `team_assignments.yaml` under `role_type: builder_agent`

## team_assignments.yaml entry format (L0)
```yaml
teams:
  - id: [TEAM_ID]
    role_type: builder_agent
    engine: [cursor-composer|openai-codex|gemini|claude-code]
    skills:
      - lod400_execution
      - lod500_authoring
```

## Example slot (fill with your project IDs)
| Slot | Engine | Notes |
|------|--------|-------|
| [TEAM_ID] | [engine-name] | Builder — must differ from validator engine |
