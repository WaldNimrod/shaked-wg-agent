---
id: ADR_AOS_V3_001_CORE_ARCHITECTURE
title: 'ADR-001: Agents_OS v3 Core Architecture'
status: Proposed
date: 2026-03-19
author: Team 101 (Gemini Code Assist)
reviewers: Team 00, Team 100
---

# ADR-001: Agents_OS v3 Core Architecture

## 1. Status

**Proposed**

## 2. Context

The `agents_os` v2 system suffered a critical failure after an attempted upgrade. The deep architectural review (`TEAM_100_V2_DEEP_ARCHITECTURAL_REVIEW_v1.0.0.md`) revealed fundamental design flaws. The core issue was a disconnect between the conceptual model (a multi-agent system) and the reality (a series of sequential, stateless LLM API calls).

This led to numerous critical issues, including:
- **Lack of Resilience (C-01):** Network failures caused total pipeline collapse due to missing retry logic.
- **State Integrity Failure (C-08, C-14, C-15):** Stale context was used because the state observer wasn't integrated, and concurrent runs would corrupt state.
- **Unvalidated LLM Outputs (C-11):** The system relied on simple keyword searches (`"PASS"`) in free-text LLM responses, leading to unpredictable behavior.
- **Implicit Human Dependencies:** Steps requiring human intervention (e.g., using Cursor) were not formally managed by the pipeline, creating silent failure points.

A complete architectural refactor is required to build a reliable and scalable system. This ADR proposes the foundational architecture for `agents_os` v3.

## 3. Decision

We will design and build `agents_os` v3 based on the **"Stateful Prompt Orchestrator"** model. This model is an explicit acknowledgment of the system's true function: to route prompts to different engines based on a persistent state, validate their outputs, and manage human intervention points.

### 3.1 Core Principles

1.  **Honest Abstraction:** The system is a **Prompt Router** and **State Machine**. We will not use the "multi-agent" metaphor internally, as it creates flawed architectural assumptions. "Teams" are personas for prompts, not autonomous agents.
2.  **State is Sacred:** The pipeline's state is its only memory. It must be unique per run, consistently updated, and validated.
3.  **Validation is Not Optional:** All external inputs, especially LLM responses, **must** be validated against a strict schema before being used.
4.  **Humans are Part of the System:** Human approval and intervention points are formal gate types, not implicit, out-of-band actions.

### 3.2 Proposed Core Components

```
┌─────────────────────────┐
│   Pipeline Runner (CLI) │
└───────────┬─────────────┘
            │ 1. Start(wp_id)
┌───────────▼─────────────┐
│  Pipeline Orchestrator  │
│ (async, stateful)       │
├─────────────────────────┤
│ - pipe_run_id: UUID     │──┐ 2. Generate STATE_SNAPSHOT.json
│ - state: PipelineState  │  │
└───────────┬─────────────┘  │
            │ 3. Execute Gate(N)
┌───────────▼─────────────┐  │  ┌───────────────────┐
│        Gate Logic       │  │  │    State Reader   │
├─────────────────────────┤  └─>│ (Runs once at start)│
│  - Prompt Builder       │     └───────────────────┘
│  - Engine Caller        │
│  - Response Validator   │
└───────────┬─────────────┘
            │ 4. Call(engine, prompt)
┌───────────▼─────────────┐
│      Engine Layer       │
│ (with mandatory retry)  │
├─────────────────────────┤
│ - OpenAI                │
│ - Gemini                │
│ - Cursor (File Writer)  │
└───────────┬─────────────┘
            │ 5. LLM Response
┌───────────▼─────────────┐
│  Response Validator     │
│ (Pydantic/JSON Schema)  │
└───────────┬─────────────┘
            │ 6. Validated Data
┌───────────▼─────────────┐
│  Pipeline Orchestrator  │
├─────────────────────────┤
│ 7. Update State         │
│ 8. Advance to Gate(N+1) │
└─────────────────────────┘
```

1.  **Pipeline Orchestrator (`pipeline.py`):**
    *   The main async loop.
    *   On start, it will **always** invoke the `StateReader`.
    *   It will manage a `PipelineState` object, identified by a unique `pipe_run_id` (fixes C-14).
    *   It will execute gates sequentially based on the defined workflow.

2.  **State Reader (`state_reader.py`):**
    *   Integrated into the pipeline startup. It is no longer a manual step (fixes C-15).
    *   Its sole purpose is to generate the `STATE_SNAPSHOT.json` which provides context about the repository state.

3.  **Engine Layer (`engines/`):**
    *   All engine calls will be wrapped in a `call_with_retry` decorator by default. This is not optional (fixes C-01).
    *   The `CursorEngine` will be explicitly defined as a "Human-in-the-Loop" engine, which pauses the pipeline until a human action is registered.

4.  **Response Validator (New Component):**
    *   A new, mandatory step after every LLM call.
    *   Each gate that calls an LLM must define a Pydantic model or JSON schema for the expected response.
    *   The validator will parse the LLM's raw text output and attempt to instantiate the model.
    *   If validation fails, the `call_with_retry` logic is triggered, asking the LLM to fix its output. This replaces fragile keyword searching (fixes C-11).

5.  **Git Protocol:**
    *   The pipeline will have an explicit, simple Git interaction model.
    *   For example, before a QA gate (like `GATE_4`), the orchestrator will run `git status --porcelain`. If the output is not empty, the gate will fail with a clear "Uncommitted changes" error, instructing the user to commit their work. This makes the process explicit and reliable (addresses C-02).

## 4. Consequences

### Positive

*   **Reliability:** The system will be resilient to transient network errors and invalid LLM outputs.
*   **Predictability:** The "Stateful Prompt Orchestrator" model is explicit and easier to reason about than a vague "multi-agent" system.
*   **Debuggability:** Failures will be specific (e.g., "Response validation failed: `status` field missing") rather than cryptic. Unique `pipe_run_id` allows for clear logging and artifact tracking per run.
*   **Maintainability:** Adding new capabilities (a new "program") will have a clear pattern: create a new prompt, a new response validation schema, and add the gate to the workflow.

### Negative

*   **Increased Upfront Boilerplate:** Developers adding new LLM-based gates will need to define a Pydantic model for the response. This is a positive trade-off for reliability.
*   **Loss of "Magic":** The architecture is less aspirational than a true autonomous agent system. However, it is an honest reflection of what is currently feasible and reliable.

## 5. Next Steps

*   Review and approve this ADR.
*   Upon approval, begin drafting the detailed component specifications (Pydantic models for state, interfaces for engines, etc.).
*   Simultaneously, begin work on the visual mockups for the dashboard, which will be designed to reflect this new, more transparent architecture.

---
**log_entry | TEAM_101 | ADR_AOS_V3_001 | PROPOSED | Core architecture for a reliable, stateful prompt orchestrator. | 2026-03-19**