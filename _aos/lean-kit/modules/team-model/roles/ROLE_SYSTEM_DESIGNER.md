# Role: System Designer (human orchestrator)

**type:** system_designer
**level:** L0-capable

## What this role does
Owns routing, prioritization, and escalation for the project in the L0 (Lean) profile. Ensures the correct agents are engaged at each L-GATE and that cross-engine validation is scheduled and honored.

## Responsibilities
- Assign work packages and track status in `roadmap.yaml`
- Verify builder and validator engines differ before L-GATE_E advance (Iron Rule)
- Escalate blockers to the appropriate role; remove organizational friction
- Declare track (TRACK_A / TRACK_B) when acting as decision authority for intake

## What this role does NOT do (hard boundaries)
- **Does not** approve specification content in place of the Architecture Agent
- **Does not** substitute for cross-engine validation at L-GATE_V (human sign-off does not replace validator engine)
- **Does not** perform code review as the sole quality gate

## Required skills (minimum viable)
| Skill | Why required |
|-------|--------------|
| domain_knowledge | Prioritize and scope work correctly |
| decision_authority | Unblock the pipeline when agents disagree |
| route_and_escalate | Operate `roadmap.yaml` / `team_assignments.yaml` accurately |

## Engine requirements
- **Preferred engine type:** human
- **Must differ from:** N/A (human is distinct from LLM builders/validators)
- **In L0:** declared in `team_assignments.yaml` under key: `system_designer`

## team_assignments.yaml entry format (L0)
```yaml
teams:
  - id: [TEAM_ID]
    role_type: system_designer
    engine: human
    skills:
      - domain_knowledge
      - decision_authority
      - route_and_escalate
```

## Example slot (fill with your project IDs)
| Slot | Engine | Notes |
|------|--------|-------|
| [TEAM_ID] | human | Orchestrator only — never content approver or validator substitute |
