---
pla_id: 3D_CREATIVE
version: "1.0.0"
status: ACTIVE
authority: Team 00
authored_by: Team 100
date: 2026-04-15
proven_in: Israel Microgreens — BlenderV2 (planned — S002+)
supersedes: null
gate_spine: L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE
---

# Project Lifecycle Archetype: 3D_CREATIVE
# Spatial modeling, visual design, render pipelines, and export systems

---

## 1. What This Archetype Covers

Use 3D_CREATIVE when the primary deliverable is a spatial artifact: a 3D model, rendered scene, visual design system, or export pipeline for physical or digital fabrication. The product is not running software — it is a visual and spatial system. Verification is about spatial correctness, visual fidelity, and export integrity — not functional test coverage.

**Canonical example:** Israel Microgreens — BlenderV2: 3D system modeling for vertical hydroponics farm design, including structural components, growth modules, and spatial layout.

**Signs this archetype applies:**
- Primary creation tool is a 3D/CAD application (Blender, SketchUp, FreeCAD, Rhino)
- Deliverables include model files (.blend, .skp, .step), renders (.png, .exr), and exports (.fbx, .obj, .stl, .glb)
- Work involves iteration cycles driven by visual review, not code tests
- Validation is partly human (visual inspection, spatial judgment) and partly structural (mesh integrity, export fidelity)
- Physical fabrication or real-world implementation is the eventual downstream use

**Signs it does NOT apply:**
- The project is software that processes or displays 3D content → `SOFTWARE`
- The project is documentation or a knowledge corpus about 3D design → `CONTENT_SUBSTRATE`
- The project is an AI agent for a creative domain → `DOMAIN_AGENT`

---

## 2. Stage Sequence (Stages 0–7)

| Stage | Name | What happens | Domain-specific meaning |
|-------|------|--------------|-------------------------|
| **Stage 0** | Concept | Define the object, system, or scene. Reference images, dimensions, physical constraints. | Cannot model without a spatial concept. What exists in the real world? What must be designed? |
| **Stage 1** | Asset Spec | Specify materials, scale system, parametric rules, naming conventions, property drivers | Equivalent to LOD400 in software — zero ambiguity before Blender is opened |
| **Stage 2** | 3D Modeling | Build the model — geometry, structure, basic materials | First pass: focus on form and structure. Not final materials yet. |
| **Stage 3** | Iteration | Refine geometry based on review. Apply modifiers, parametric drivers, final materials. | Review cycles are visual; judgment is spatial and aesthetic. Multiple rounds expected. |
| **Stage 4** | Render Validation | Render test frames. Validate visual fidelity, lighting rig, material accuracy. | This is the human-judgment gate. Visual approval required before proceeding. |
| **Stage 5** | Export | Export to target format(s). Validate export integrity (mesh clean, scale correct, no missing refs). | Downstream tools (simulation, fabrication, game engine, web viewer) may have specific requirements. |
| **Stage 6** | Documentation | Document the model: part list, property system, naming guide, export conventions, usage instructions. | Future modelers or AI agents must be able to work with this model without the original creator. |
| **Stage 7** | Archive | Lock the .blend version. Archive renders. Commit to repo with version tag. AS_MADE record. | Version locking is as important for 3D assets as for code. |

### Stage flow notes:
- Stages 0–1 must be complete before any modeling begins (no concept = no model)
- Stage 3 (Iteration) is the natural home of most creative work — expect multiple WPs here
- Stage 4 (Render Validation) requires Team 00 or designated human visual sign-off — this is non-delegatable
- Stages 5–7 can be done as one WP for simple assets; complex systems may need separate WPs per stage
- For physical fabrication projects: an additional stage between 5 and 6 (Fabrication Test) should be added as a compound: `"Stage 5 (Export) + Fabrication Test"`

---

## 3. Gate Mapping

| Gate | Gate question (universal) | Stages that fall here | Domain-specific evidence at this gate |
|------|--------------------------|----------------------|---------------------------------------|
| **L-GATE_ELIGIBILITY** | Is this WP eligible to enter the pipeline? | Stage 0 — concept defined | Reference images or physical measurements staged; target dimensions declared; scope (what objects/scenes) documented |
| **L-GATE_SPEC** | Is the spec complete enough to authorize work? | Stage 1 — asset spec | Material list; scale system locked; naming conventions defined; parametric rules documented; LOD200 = what will be modeled |
| **L-GATE_BUILD** | Has the domain construction been completed? | Stage 2–5 (Model → Export) | .blend file committed; render samples produced; export files clean and verified |
| **L-GATE_VALIDATE** | Does the output meet quality and fidelity standards? | Stage 6–7 (Docs + Archive) | Documentation complete; LOD500 fidelity record; cross-engine review of export integrity and documentation accuracy |

### LOD artifact guidance (domain-adapted):

| LOD Level | 3D_CREATIVE adaptation |
|-----------|------------------------|
| LOD100 | What spatial problem or design need is being addressed? What is the real-world context? |
| LOD200 | What objects/scenes will be modeled? What is the target export format and downstream use? What scale system? |
| LOD400 | Exact object list with dimensions; material assignments; property driver definitions; export format and settings; render resolution and lighting rig; naming conventions |
| LOD500 | Which objects were modeled as specified? Geometry deviation log. Export test results. Visual validation record. |

---

## 4. Deliverable Types Per Stage

| Stage | Deliverable type | File pattern |
|-------|-----------------|-------------|
| Stage 0 | Reference package | `concept/REFERENCES/`, `concept/CONCEPT_SPEC.md` |
| Stage 1 | Asset spec | `_aos/work_packages/{WP-ID}/ASSET_SPEC.md`, `MATERIAL_PALETTE.md` |
| Stage 2 | Model file (WIP) | `{project}_v{N}_wip.blend` (committed, labeled WIP) |
| Stage 3 | Iteration file | `{project}_iter{N}.blend`, `ITERATION_NOTES_{N}.md` |
| Stage 4 | Render samples | `renders/test_{N}/`, `RENDER_QA_{DATE}.md` |
| Stage 5 | Export package | `exports/{format}/`, `EXPORT_VALIDATION_{DATE}.md` |
| Stage 6 | Documentation | `MODEL_GUIDE.md`, `PROPERTY_SYSTEM.md`, `PART_LIST.md` |
| Stage 7 | Locked archive | `{project}_v{X.Y.Z}_FINAL.blend`, `renders/final/`, `AS_MADE_{WP-ID}.md` |

---

## 5. Team Roles Per Stage

| Stage | Primary role | Validator | Notes |
|-------|-------------|-----------|-------|
| Stage 0–1 | Team 100 (Claude Code — spec) + Team 00 (spatial judgment) | Team 00 (human review) | Concept requires human spatial judgment |
| Stage 2–3 | Domain specialist (Blender operator — human or Blender-integrated agent) | Team 100 (structural review) | Builder = human or tool; LLM reviews geometry logic |
| Stage 4 | Domain specialist (render) | **Team 00 (visual approval — REQUIRED)** | Visual validation requires human judgment; non-delegatable |
| Stage 5 | Domain specialist (export) | Team 190 (export file integrity check) | Cross-engine: export validator ≠ modeler |
| Stage 6–7 | Team 100 (documentation) + Team 00 (sign-off) | Team 190 (LOD500 constitutional review) | Standard cross-engine validation |

### Cross-engine rule note for 3D_CREATIVE:
"Different engine" in the Iron Rule applies to **LLM governance agents** — the agent reviewing documentation and exports must use a different LLM engine than the agent that authored the spec. The Blender operator (human or tool-integrated agent executing Blender commands) is not counted as an "engine" for Iron Rule purposes — it is the build tool, analogous to a compiler.

---

## 6. Validation Criteria Per Stage

**Stage 0 → Stage 1:** Reference images or physical dimension sources identified. Target use case declared (visualization / fabrication / export pipeline). Real-world constraints documented (physical dimensions, material constraints, downstream tool requirements).

**Stage 1 → Stage 2:** Material palette defined. Scale and unit system locked. Property-driven parameters listed with driver logic defined. Naming convention applied. LOD400 spec zero-TBD.

**Stage 2 → Stage 3:** All objects in the specified object list exist in the scene. No placeholder geometry. Naming convention applied to all objects. Basic material assignments in place.

**Stage 3 → Stage 4:** Modifiers are either applied or intentionally kept live (documented). Material assignments complete. No orphan data blocks. No missing textures.

**Stage 4 → Stage 5:** Render samples match visual spec or reference images. Team 00 visual approval on record. Lighting rig is stable. No render artifacts in specified key views.

**Stage 5 → Stage 6:** Export files are clean: correct scale, no missing references, target format validated in downstream tool (if specified). Export test documented.

**Stage 6 → Stage 7:** Documentation covers all objects in the part list, all parametric drivers, all export conventions. Part list is complete. Documentation is usable by someone who was not involved in modeling.

**Stage 7 → COMPLETE:** Version-tagged .blend archive committed. Renders archived with version tag. AS_MADE record complete. LOD500 fidelity record signed off by Team 190.

---

## 7. `stage_mapping` Field — Canonical Values

```yaml
stage_mapping: "Stage 0 (Concept)"
stage_mapping: "Stage 1 (Asset Spec)"
stage_mapping: "Stage 2 (3D Modeling)"
stage_mapping: "Stage 3 (Iteration)"
stage_mapping: "Stage 4 (Render Validation)"
stage_mapping: "Stage 5 (Export)"
stage_mapping: "Stage 6 (Documentation)"
stage_mapping: "Stage 7 (Archive)"

# Compound:
stage_mapping: "Stage 0 (Concept) + Stage 1 (Asset Spec)"
stage_mapping: "Stage 2 (3D Modeling) + Stage 3 (Iteration)"
stage_mapping: "Stage 6 (Documentation) + Stage 7 (Archive)"
```

---

## 8. L-GATE_VALIDATE Validation AC Extensions

At L-GATE_VALIDATE, Team 190 uses standard LOD500 fidelity criteria **plus**:

- **AC-3D-01:** All objects in the LOD400 object list are present in the committed .blend file
- **AC-3D-02:** Export files pass format-specific integrity check (clean geometry, no missing meshes, correct scale)
- **AC-3D-03:** Team 00 visual approval of render samples is on record (render QA document exists with Team 00 sign-off)
- **AC-3D-04:** Documentation covers all parametric drivers and property systems defined in LOD400
- **AC-3D-05:** .blend file is committed with version tag; renders archived with version tag
- **AC-3D-06:** Cross-engine review of documentation and export integrity was performed by a different LLM engine than the spec author

---

## 9. Compatibility Notes

- **Gate spine:** Unchanged.
- **Profile:** L0 (Israel Microgreens). No engine infrastructure required.
- **Blender as build tool:** Blender (or SketchUp, CAD tools) is the build tool — analogous to an IDE or compiler. It does not replace LLM governance agents in the gate process; it generates the artifacts that agents review.
- **Human visual gate:** Stage 4 (Render Validation) requires human judgment that cannot be delegated to an LLM. In L0, this is handled as Team 00 sign-off in the gate_history notes. In future L2+ profiles for creative projects, this would be formalized as an explicit human gate.
- **LOD standard:** Domain-adapted guidance above does not replace the LOD standard. LOD100–500 levels apply; content is domain-appropriate.
- **Iron Rules:** All apply. Cross-engine validation at L-GATE_VALIDATE is unconditional (applies to LLM agents in governance layer; not to the Blender operator).
- **Israel Microgreens AOS canonization (S001):** Complete as of 2026-04-12. S002+ WPs should declare `stage_mapping` from §7 and `lifecycle_archetype: 3D_CREATIVE` in roadmap.yaml.
