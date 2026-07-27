# Project Lifecycle Archetypes (PLA)
## AOS Methodology — Flexible Lifecycle Layer
## Version: 1.0.0 | Date: 2026-04-15 | Authority: Team 00

---

## What is a Project Lifecycle Archetype?

A **Project Lifecycle Archetype (PLA)** is a named stage-sequence template that describes the domain-specific shape of work for a given project type.

A PLA is NOT a profile level. It is NOT a gate. It is the answer to a different question:

| Question | Answer |
|----------|--------|
| How are gates enforced? | **Profile** (L0 / L2 / L2.5) |
| What governance checkpoint is this? | **Gate** (L-GATE_ELIGIBILITY / S / B / V) |
| **What kind of work is happening?** | **Lifecycle Archetype** |

---

## The Core Principle: Stages and Gates Are Orthogonal

**Gates** are universal, immutable governance checkpoints. They answer: "Has this unit of work cleared quality and accountability requirements?" They apply identically to every project type — a Blender model, a knowledge corpus, and a web application all pass through L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE.

**Stages** are domain-specific work phases. They answer: "What kind of domain activity is currently happening?" A 3D project's stages (Concept → Model → Iterate → Render → Export) are completely different from a software project's stages (Design → Build → Test → Deploy).

A PLA maps its domain stages onto the universal gate spine. Multiple stages can fall within one gate envelope; a single stage can span multiple WPs. The gate is the governance anchor; the stage is the work context.

This was first proven by the **nimrod-book** project, which defined a Stage 0–6 CONTENT_SUBSTRATE lifecycle that maps cleanly onto the L0 gate model without changing any constitutional rule.

---

## The Four Archetypes

| PLA ID | Project type | Stage count | Active example |
|--------|-------------|-------------|----------------|
| `SOFTWARE` | Web apps, APIs, CLI tools, automation | 5 | TikTrack, AOS itself |
| `CONTENT_SUBSTRATE` | Knowledge bases, context substrates, document corpora | 7 (Stage 0–6) | nimrod-book ✅ proven |
| `3D_CREATIVE` | Blender models, spatial design, visual assets | 8 (Stage 0–7) | Israel Microgreens |
| `DOMAIN_AGENT` | AI agent systems for a specific real-world domain | 7 (Stage 0–6) | SmallFarmsAgents |

---

## How to Select an Archetype

```
What is the primary deliverable of this project?

  Running software (web app, API, CLI, automation script)?
    → lifecycle_archetype: SOFTWARE
    → See: PLA_SOFTWARE.md

  A knowledge corpus, context base, document bundle, or prompt library?
    → lifecycle_archetype: CONTENT_SUBSTRATE
    → See: PLA_CONTENT_SUBSTRATE.md

  3D models, rendered scenes, visual assets, or spatial design?
    → lifecycle_archetype: 3D_CREATIVE
    → See: PLA_3D_CREATIVE.md

  An AI agent system for a specific real-world domain?
    → lifecycle_archetype: DOMAIN_AGENT
    → See: PLA_DOMAIN_AGENT.md
```

---

## How to Use an Archetype

**1. Select archetype** using the decision tree above.

**2. Record in `projects.yaml`** (hub):
```yaml
lifecycle_archetype: CONTENT_SUBSTRATE  # or SOFTWARE / 3D_CREATIVE / DOMAIN_AGENT
```

**3. Record in `roadmap.yaml`** (project-level `project:` block):
```yaml
project:
  lifecycle_archetype: CONTENT_SUBSTRATE
```

**4. Tag each WP** with `stage_mapping:` using canonical values from the PLA document (§7):
```yaml
  - id: "NB-V1-WP-B1"
    stage_mapping: "Stage 0 (Source intake) + Stage 1 (Mining)"
```

**5. Read the PLA document** for gate mapping guidance, LOD artifact expectations, team roles, and validation criteria for each stage.

---

## What PLAs Do NOT Change

- Gate spine (L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE) — **UNCHANGED**
- Iron Rules — **UNCHANGED**
- LOD standard (LOD100–LOD500) — **UNCHANGED**
- Profile levels (L0 / L2 / L2.5) — **UNCHANGED**
- Team 190 authority at L-GATE_VALIDATE — **UNCHANGED**

PLAs add domain-specific guidance on what gates look at, not whether gates exist.

---

## `stage_mapping` Field

The `stage_mapping` field in `roadmap.yaml` WP entries formally records which stage(s) a WP corresponds to. It was used informally in nimrod-book; this PLA system makes it formally defined.

- **Required** (by convention) for non-SOFTWARE archetypes
- **Informational** in L0 — not machine-validated currently
- **Values** are drawn from §7 of the applicable PLA document
- **Compound** mappings permitted: `"Stage 0 (Source intake) + Stage 1 (Mining)"`

---

## Adding a New Archetype

When a project type genuinely doesn't fit any existing archetype:

1. Write `PLA_{NEW_TYPE}.md` following the same template structure as existing PLAs
2. Get Team 00 approval
3. Add entry to the table in this README
4. Add `lifecycle_archetype: {NEW_TYPE}` to the project in `projects.yaml`
5. Register as a lean-kit version bump (patch)

Do NOT create a new archetype for minor variations within an existing type. Variations are handled via `stage_mapping` compound values and WP notes.

---

## References

- `PROFILE_SELECTION_GUIDE.md` — two-step decision (archetype first, then profile)
- `lean-kit/modules/project-governance/config_templates/roadmap.yaml.template` — `stage_mapping` field definition
- `agents-os/_aos/projects.yaml` — `lifecycle_archetype` field on registered projects
