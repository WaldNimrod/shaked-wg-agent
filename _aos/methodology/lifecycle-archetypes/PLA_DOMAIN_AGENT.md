---
pla_id: DOMAIN_AGENT
version: "1.0.0"
status: ACTIVE
authority: Team 00
authored_by: Team 100
date: 2026-04-15
proven_in: SmallFarmsAgents (AOS canonization complete S001; domain work at S002+)
supersedes: null
gate_spine: L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE
---

# Project Lifecycle Archetype: DOMAIN_AGENT
# AI agent systems built for a specific real-world domain

---

## 1. What This Archetype Covers

Use DOMAIN_AGENT when the primary deliverable is an AI agent (or multi-agent system) designed to operate within a specific real-world domain — not general-purpose software or infrastructure. The agent has domain knowledge embedded in its design, interacts with domain-specific data sources, and is validated against domain-specific outcomes.

**Canonical example:** SmallFarmsAgents / OrganicMarketAgent — a community AI agent for Israel's organic farming market, providing price indexing and market intelligence.

**Signs this archetype applies:**
- The deliverable is an agent or agent pipeline designed for a specific domain (farming, health, legal, finance, etc.)
- Success is measured by domain outcomes (price accuracy, user adoption, domain-expert validation) not just functional tests
- The agent requires domain research before meaningful technical spec is possible
- Domain experts or real users are part of the validation process

**Signs it does NOT apply:**
- The project is general-purpose software without a domain-specific agent → `SOFTWARE`
- The project is AOS infrastructure or agent framework tooling → `SOFTWARE`
- The project is a knowledge corpus about a domain → `CONTENT_SUBSTRATE`

---

## 2. Stage Sequence (Stages 0–6)

| Stage | Name | What happens | Domain-specific meaning |
|-------|------|--------------|-------------------------|
| **Stage 0** | Domain Research | Map the domain: actors, data sources, market structure, terminology, existing tools | Cannot spec an agent without understanding the domain it operates in |
| **Stage 1** | Agent Spec | Define agent capabilities, data contracts, persona, boundaries, failure modes | LOD200 + LOD400 spec; domain expert review required |
| **Stage 2** | Agent Build | Implement the agent — prompts, tools, integrations, pipelines | Code + configuration + prompt library |
| **Stage 3** | Integration Test | Connect agent to real domain data sources; test end-to-end | Not unit tests — domain data fidelity tests |
| **Stage 4** | Domain Validation | Domain experts or representative users evaluate agent outputs | Functional tests ≠ domain validation; human judgment required |
| **Stage 5** | Deploy | Release agent to production environment or target users | Access control, monitoring, escalation paths configured |
| **Stage 6** | Monitor | Ongoing monitoring; domain drift detection; periodic revalidation | Agents can drift from domain reality; requires active governance |

### Stage flow notes:
- Stage 0 (Domain Research) is mandatory — no shortcut. Rushing to Stage 1 without domain understanding is the primary failure mode for agent projects.
- Stages 2–3 may iterate multiple times before Stage 4 (each iteration = one WP with its own gate cycle)
- Stage 4 requires at least one domain-expert or real-user review session; this is a human gate (informally) even in L0
- Stage 6 produces recurring WPs (monthly or quarterly) for the active lifetime of the agent

---

## 3. Gate Mapping

| Gate | Gate question (universal) | Stages that fall here | Domain-specific evidence at this gate |
|------|--------------------------|----------------------|---------------------------------------|
| **L-GATE_ELIGIBILITY** | Is this WP eligible to enter the pipeline? | Stage 0 — domain is identified; scope declared | Domain identified; key questions listed; research plan exists |
| **L-GATE_SPEC** | Is the spec complete enough to authorize work? | Stage 0 + Stage 1 | LOD400 agent spec: capabilities defined; data contracts explicit; failure modes documented; domain expert has reviewed scope |
| **L-GATE_BUILD** | Has the agent been built and integration-tested? | Stage 2 + Stage 3 | Agent code committed; integration tests pass with real domain data; no spec deviations; domain data fidelity verified |
| **L-GATE_VALIDATE** | Does the output meet quality and fidelity standards? | Stage 4 + Stage 5 | Domain validation session conducted; LOD500 fidelity record; cross-engine constitutional review; deployment verified |

### LOD artifact guidance (domain-adapted):

| LOD Level | DOMAIN_AGENT adaptation |
|-----------|------------------------|
| LOD100 | What real-world problem does this agent solve? Who are the domain actors and beneficiaries? |
| LOD200 | What are the agent's capabilities and boundaries? What data sources does it access? What does it never do? |
| LOD400 | Exact prompt templates; tool definitions; API contracts; data schema; escalation logic; failure mode handling; AC with domain-testable criteria |
| LOD500 | As-built agent: what capabilities were implemented vs. spec; integration test evidence; domain validation session record |

---

## 4. Deliverable Types Per Stage

| Stage | Deliverable type | File pattern |
|-------|-----------------|-------------|
| Stage 0 | Domain research report | `_COMMUNICATION/team_{ID}/DOMAIN_RESEARCH_{DOMAIN}_{DATE}.md` |
| Stage 1 | Agent spec | `_aos/work_packages/{WP-ID}/LOD400_agent_spec.md` |
| Stage 2 | Agent implementation | Git commits; prompt library; tool definitions |
| Stage 3 | Integration test report | `_COMMUNICATION/team_50/INTEGRATION_TEST_{WP-ID}_{DATE}.md` |
| Stage 4 | Domain validation record | `_COMMUNICATION/team_{ID}/DOMAIN_VALIDATION_{DATE}.md` |
| Stage 5 | Deployment record | `_COMMUNICATION/team_60/DEPLOY_{AGENT}_{DATE}.md` |
| Stage 6 | Monitoring report | `_COMMUNICATION/team_{ID}/MONITOR_{AGENT}_{YYYYMM}.md` |

---

## 5. Team Roles Per Stage

| Stage | Primary role | Validator | Notes |
|-------|-------------|-----------|-------|
| Stage 0 | Team 100 (research) + Team 00 (domain judgment) | Team 190 | Domain understanding requires human validation |
| Stage 1 | Team 110 (architect) | Team 190 at L-GATE_SPEC | Domain expert review is required before LOD400 is locked |
| Stage 2 | Builders (Team 10/20/30 as applicable) | Team 50 (QA) | Standard builder/QA split |
| Stage 3 | Builders + Team 50 | Team 90 at L-GATE_BUILD | Integration tests use real domain data |
| Stage 4 | Domain expert (external) + Team 00 (judgment) | Team 190 at L-GATE_VALIDATE | Human judgment is the validation mechanism |
| Stage 5 | Team 60 (DevOps) | Team 190 | Standard deployment governance |
| Stage 6 | Team 100 (monitoring) + Team 00 (revalidation decision) | Team 190 (periodic drift check) | Recurring — creates new WPs each cycle |

---

## 6. Validation Criteria Per Stage

**Stage 0 → Stage 1:** Domain map is complete (actors, data sources, existing tools). Key terminology documented. At least one real data source identified and accessible.

**Stage 1 → Stage 2:** LOD400 agent spec is zero-TBD. Agent capabilities are bounded (explicit "never does" list). Data contracts are explicit. At least one domain expert has reviewed and approved the scope.

**Stage 2 → Stage 3:** All specified capabilities are implemented. No unimplemented ACs. Code committed and passes baseline tests.

**Stage 3 → Stage 4:** Integration tests with real domain data pass. No critical failures in domain data handling. Edge cases documented.

**Stage 4 → Stage 5:** Domain validation session conducted (at least one session with domain expert or real user). Results documented. Any required adjustments implemented. Team 00 explicit approval required before deploy.

**Stage 5 → Stage 6 (or first monitor cycle):** Agent is live. Access control configured. Monitoring is active. Escalation paths defined. LOD500 fidelity record complete.

**Stage 6 → next cycle:** Domain drift assessment complete. Agent performance vs. domain reality documented. Any required updates scoped as new WPs.

---

## 7. `stage_mapping` Field — Canonical Values

```yaml
stage_mapping: "Stage 0 (Domain Research)"
stage_mapping: "Stage 1 (Agent Spec)"
stage_mapping: "Stage 2 (Agent Build)"
stage_mapping: "Stage 3 (Integration Test)"
stage_mapping: "Stage 4 (Domain Validation)"
stage_mapping: "Stage 5 (Deploy)"
stage_mapping: "Stage 6 (Monitor)"

# Compound:
stage_mapping: "Stage 0 (Domain Research) + Stage 1 (Agent Spec)"
stage_mapping: "Stage 2 (Agent Build) + Stage 3 (Integration Test)"
```

---

## 8. L-GATE_VALIDATE Validation AC Extensions

At L-GATE_VALIDATE, Team 190 uses standard LOD500 fidelity criteria **plus**:

- **AC-DA-01:** Domain validation session record exists and is signed off by Team 00
- **AC-DA-02:** Agent capability inventory in LOD500 matches LOD400 spec (or deviations are documented)
- **AC-DA-03:** "Never does" constraints from LOD400 are verified — agent does not exceed its defined scope
- **AC-DA-04:** At least one real domain data source was used in integration testing (no mock-only validation)
- **AC-DA-05:** Escalation paths are defined and tested (agent knows when to escalate to human)
- **AC-DA-06:** Cross-engine review was performed by a different engine than the primary builder

---

## 9. Compatibility Notes

- **Gate spine:** Unchanged.
- **Profile:** L0 (SmallFarmsAgents). Can use L2 if engine infrastructure is added.
- **Human judgment:** Stage 4 (Domain Validation) implicitly requires human judgment even in L0. This is NOT a formal human gate like L2.5's Phase 3/5 — it's a domain-quality gate handled through Team 00 sign-off at L-GATE_VALIDATE.
- **LOD standard:** Domain-adapted LOD guidance above does not replace the LOD standard. It describes what the standard's questions mean for this domain type.
- **SmallFarmsAgents WPs** pre-dating this archetype (M1–M10, S001 canonization WPs): classified retroactively. S002+ WPs should use `stage_mapping` from §7.
- **Iron Rules:** All apply. Cross-engine validation at L-GATE_VALIDATE is unconditional.
