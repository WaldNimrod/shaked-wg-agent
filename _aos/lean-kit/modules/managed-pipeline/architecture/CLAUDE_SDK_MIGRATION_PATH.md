# Claude Agent SDK — Production Architecture
# Status: Research & Design (not yet implemented)
# Target: L2.5 production execution model

---

## WHY THIS EXISTS

The L2.5 experiment uses Claude Code as a manual orchestrator reading a runbook.
This is the fastest path to validation. The production target is the Claude Agent SDK
managed loop — the original motivation for L2.5.

The Claude Agent SDK provides:
- **Managed agentic loop**: SDK handles tool execution, context, retries automatically
- **Registered tools**: each agent capability is a typed, schema-validated tool
- **Human gate tool**: a special tool that PAUSES the loop and waits for human input
- **Subagent spawning**: orchestrator spawns specialized agents with defined tool sets
- **Persistent state**: pipeline state survives across sessions

---

## CURRENT vs. TARGET ARCHITECTURE

### Current (Experiment)
```
Claude Code (human session)
  reads ORCHESTRATOR_RUNBOOK.md
  manually spawns Agent tool calls
  waits at human gates in conversation
  tracks state in roadmap.yaml manually
```

### Target (Claude Agent SDK)
```python
from anthropic import Anthropic

client = Anthropic()

# L2.5 Orchestrator — managed agent
def run_l25_pipeline(lod100_path: str):
    messages = [{"role": "user", "content": f"Run L2.5 pipeline for: {lod100_path}"}]
    
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            system=load_file("activation/ACTIVATION_ORCHESTRATOR.md"),
            tools=ORCHESTRATOR_TOOLS,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            break  # Pipeline complete
            
        # SDK manages tool execution loop
        for tool_use in response.content:
            if tool_use.type == "tool_use":
                result = execute_tool(tool_use.name, tool_use.input)
                
                if tool_use.name == "present_human_gate":
                    # PAUSE the loop — wait for Team 00 input
                    human_response = wait_for_human_input(result)
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": human_response})
                    break
                else:
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append(make_tool_result(tool_use.id, result))
```

---

## TOOL SCHEMA DESIGN

Each activation prompt in `activation/` becomes an agent with this tool set:

### Orchestrator Tools
```json
[
  {
    "name": "read_artifact",
    "description": "Read a file from the AOS filesystem",
    "input_schema": {
      "type": "object",
      "properties": {
        "path": {"type": "string", "description": "Relative path from project root"}
      },
      "required": ["path"]
    }
  },
  {
    "name": "write_artifact",
    "description": "Write content to a canonical artifact path",
    "input_schema": {
      "type": "object",
      "properties": {
        "path": {"type": "string"},
        "content": {"type": "string"}
      },
      "required": ["path", "content"]
    }
  },
  {
    "name": "spawn_subagent",
    "description": "Spawn a specialized agent for a pipeline phase",
    "input_schema": {
      "type": "object",
      "properties": {
        "agent_role": {
          "type": "string",
          "enum": ["spec_agent", "arch_agent", "const_validator", "mockup_agent",
                   "gateway_agent", "qa_agent", "tech_validator", "doc_agent"]
        },
        "context": {"type": "string", "description": "Context to pass to the agent"},
        "engine": {"type": "string", "description": "Model to use for this agent"}
      },
      "required": ["agent_role", "context"]
    }
  },
  {
    "name": "update_pipeline_state",
    "description": "Update WP gate_history and status in roadmap.yaml",
    "input_schema": {
      "type": "object",
      "properties": {
        "wp_id": {"type": "string"},
        "phase": {"type": "string"},
        "result": {"type": "string", "enum": ["PASS", "FAIL", "IN_PROGRESS"]},
        "notes": {"type": "string"}
      },
      "required": ["wp_id", "phase", "result"]
    }
  },
  {
    "name": "present_human_gate",
    "description": "PAUSES the pipeline. Presents Human Gate to Team 00 and waits for decision.",
    "input_schema": {
      "type": "object",
      "properties": {
        "gate_type": {"type": "string", "enum": ["phase_3", "phase_5"]},
        "wp_id": {"type": "string"},
        "summary": {"type": "string"},
        "artifact_paths": {"type": "array", "items": {"type": "string"}},
        "decision_options": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["gate_type", "wp_id", "summary"]
    }
  },
  {
    "name": "classify_fcp",
    "description": "Classify a finding using FCP-1 through FCP-4 protocol",
    "input_schema": {
      "type": "object",
      "properties": {
        "finding": {"type": "string"},
        "scope": {"type": "string"},
        "phase": {"type": "string"}
      },
      "required": ["finding", "scope"]
    }
  }
]
```

---

## MIGRATION PATH

### Step 1: Validate runbook with Claude Code (current experiment)
- Run 1-2 WPs through the manual Claude Code orchestrator
- Document FCP patterns, missing tools, edge cases
- Refine runbook and activation prompts

### Step 2: Extract tool implementations
- Each tool in the schema above becomes a Python function
- `read_artifact` → filesystem read
- `write_artifact` → filesystem write + git staging
- `spawn_subagent` → Claude API call with agent-specific system prompt
- `update_pipeline_state` → YAML edit in roadmap.yaml
- `present_human_gate` → notification (terminal, Slack, or AOS Dashboard)

### Step 3: Wire managed loop
- Port ORCHESTRATOR_RUNBOOK.md logic to orchestrator system prompt
- Test each tool function independently
- Wire into managed agentic loop

### Step 4: Integrate with AOS Dashboard
- L2.5 pipeline state visible in Dashboard
- Human gate notification appears in Dashboard as "action required"
- Team 00 approves/rejects in Dashboard UI

### Step 5: Cowork / Home Server evaluation (open research)
- Evaluate: can longer-running phases (4C implementation) run on home server?
- Evaluate: does Cowork environment provide tools that reduce Phase 4 setup overhead?
- Decision affects: where the SDK loop runs and how it accesses the codebase

---

## OPEN RESEARCH ITEMS

### R-OPS-1: Home Server / Terminal Execution
**Question:** For Phase 4C (implementation, potentially long-running), should the SDK loop
run on the home server rather than in a Claude Code session?
- **Advantage:** Persistent, resumable, not session-dependent
- **Consideration:** Needs file access to project directories
- **Action:** Evaluate server setup in AOS-Sandbox-Full context

### R-OPS-2: Cowork Environment
**Question:** Does the Cowork environment provide tools that improve L2.5 execution?
- Built-in tools that map to the tool schema above?
- Persistent session that survives between phases?
- Multi-agent coordination primitives?
- **Action:** Run `/setup-cowork` skill, evaluate available tools, map to L2.5 needs

### R-OPS-3: Human Gate Notification Channel
**Question:** How does Team 00 receive Phase 3 / Phase 5 gate notifications?
Options:
- A: AOS Dashboard (current — requires server running)
- B: Slack / messaging (requires integration)
- C: Email (simple, no dependency)
- D: Terminal poll (simplest for experiment)
- **Decision:** Deferred to SDK implementation phase

---

*This document is updated as research items are resolved.*
*Migration to SDK does not change the activation prompts — they are SDK-ready by design.*
