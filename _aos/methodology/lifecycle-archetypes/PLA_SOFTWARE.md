---
pla_id: SOFTWARE
version: "1.0.0"
status: ACTIVE
authority: Team 00
authored_by: Team 100
date: 2026-04-15
proven_in: TikTrack (L2), AOS itself (L0), AOS sandboxes (L0)
supersedes: null
gate_spine: L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE
---

# Project Lifecycle Archetype: SOFTWARE
# Web applications, APIs, CLI tools, automation, and running software

---

## 1. What This Archetype Covers

Use SOFTWARE when the primary deliverable is running software — a program that executes, serves requests, processes data, or automates a workflow. The product is code and its infrastructure. Verification is functional: does it behave correctly?

**This is the default archetype.** If `lifecycle_archetype` is absent from a project's metadata, it defaults to SOFTWARE. No field change is needed for existing projects.

**Canonical examples:** TikTrack (L2), agents-os self-governance (L0), AOS-Sandbox-Lean (L0)

**Signs this archetype applies:**
- Primary deliverable is executable code (web app, API, script, agent infrastructure)
- Testing is functional (unit tests, integration tests, acceptance criteria against running behavior)
- Deployment produces a running service or installed tool
- Review artifacts include code diffs, test results, and CI output

**Signs it does NOT apply:**
- The project produces a knowledge corpus or document bundle → `CONTENT_SUBSTRATE`
- The project produces 3D models or visual assets → `3D_CREATIVE`
- The project produces an AI agent for a real-world domain → `DOMAIN_AGENT`

---

## 2. Stage Sequence

| Stage | Name | What happens |
|-------|------|--------------|
| Spec | Specification | Define the problem, actors, scope, acceptance criteria. LOD100 → LOD200 → LOD400. |
| Design | System Design | Architecture, data model, API contracts, state machine, mockups (if LOD300 required). |
| Build | Implementation | Write and commit code. Implement per LOD400 spec. |
| Test | Validation | Run tests, validate against ACs, QA review. |
| Deploy | Deployment | Release to target environment. LOD500 fidelity record. |

### Stage flow notes:
- Spec and Design often collapse into a single WP (both happen before L-GATE_SPEC)
- Build may span multiple WPs (one per team or per feature cohort)
- Test and Deploy may be combined in small projects (one L-GATE_BUILD + L-GATE_VALIDATE cycle)
- For L2.5: Design stage expands into R1/R2/R3 research + LOD300 mandatory (Track B)

---

## 3. Gate Mapping

| Gate | Gate question (universal) | Stages that fall here | Domain-specific evidence |
|------|--------------------------|----------------------|--------------------------|
| **L-GATE_ELIGIBILITY** | Is this WP eligible to enter the pipeline? | Spec (LOD100 complete) | WP scope declared; no Iron Rule violations; profile confirmed |
| **L-GATE_SPEC** | Is the spec complete enough to authorize work? | Spec + Design | LOD400 spec exists; ACs are testable; no TBD values; architecture reviewed |
| **L-GATE_BUILD** | Has the implementation been completed? | Build + Test | Code committed; tests pass; validate_aos.sh clean; no spec deviations |
| **L-GATE_VALIDATE** | Does the output meet quality and fidelity standards? | Deploy | LOD500 fidelity record; cross-engine constitutional review; no open defects |

### LOD artifact guidance:

| LOD Level | SOFTWARE content |
|-----------|-----------------|
| LOD100 | Problem statement, actors, scope, open questions |
| LOD200 | Components, data flow, rough AC list, risk assessment |
| LOD300 | State machine, data model, API surface, integration contracts, mockups (Track B / L2.5) |
| LOD400 | Zero TBD — exact values, file paths, function signatures, env vars, AC with testable criteria |
| LOD500 | As-built fidelity: what was actually implemented, deviation log, test result evidence |

---

## 4. Deliverable Types Per Stage

| Stage | Deliverable type | File pattern |
|-------|-----------------|-------------|
| Spec | LOD documents | `_aos/work_packages/{WP-ID}/LOD{N}_{WP-ID}.md` |
| Design | Architecture docs, data model | `_aos/work_packages/{WP-ID}/LOD300_{WP-ID}.md` |
| Build | Committed code | Git commits; `_COMMUNICATION/team_{ID}/` build artifacts |
| Test | Test results, QA report | `_COMMUNICATION/team_50/QA_{WP-ID}_{DATE}.md` |
| Deploy | LOD500 + deployment record | `_COMMUNICATION/team_{ID}/LOD500_{WP-ID}_{DATE}.md` |

---

## 5. Team Roles Per Stage

| Stage | Primary role | Validator |
|-------|-------------|-----------|
| Spec | Team 110 (architect) | Team 190 at L-GATE_SPEC |
| Design | Team 110 + Team 170 | Team 190 |
| Build | Team 10/20/30/60 (builders) | Team 50 (QA) |
| Test | Team 50 | Team 90 at L-GATE_BUILD |
| Deploy | Team 60 (DevOps) | Team 190 at L-GATE_VALIDATE |

---

## 6. Validation Criteria Per Stage

**Spec → Design:** LOD200 exists. Problem statement is unambiguous. No open scope questions remain.

**Design → Build:** LOD400 exists. Zero TBD values. All ACs are testable. Architecture has been reviewed.

**Build → Test:** All code is committed. No lint/build failures. Test suite exists for new functionality.

**Test → Deploy:** All ACs pass. QA PASS verdict issued. No open defects in scope.

**Deploy → COMPLETE:** LOD500 fidelity record exists. Deployment verified in target env. Cross-engine constitutional review passed (L-GATE_VALIDATE).

---

## 7. `stage_mapping` Field — Canonical Values

```yaml
stage_mapping: "Spec"
stage_mapping: "Design"
stage_mapping: "Build"
stage_mapping: "Test"
stage_mapping: "Deploy"
# Compound:
stage_mapping: "Spec + Design"
stage_mapping: "Build + Test"
```

---

## 8. L-GATE_VALIDATE Validation AC Extensions

Standard LOD500 fidelity criteria apply. No SOFTWARE-specific extensions beyond:
- AC-SW-01: validate_aos.sh passes with zero failures
- AC-SW-02: All ACs from LOD400 have corresponding test evidence in LOD500
- AC-SW-03: No boundary violations detected (forbidden_patterns from project_identity.yaml)

---

## 9. Compatibility Notes

- **Default:** This archetype requires no field changes to existing projects. Absence of `lifecycle_archetype` = SOFTWARE.
- **Gate spine:** This archetype's gate mapping is 1:1 with the standard gate model — it IS the standard.
- **Profile:** Works with L0, L2, and L2.5. L2.5 always uses Track B (Design stage = mandatory LOD300).
- **Iron Rules:** All apply without exception.
