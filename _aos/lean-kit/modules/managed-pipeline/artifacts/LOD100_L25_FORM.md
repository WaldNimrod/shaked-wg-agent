# LOD100 — L2.5 Entry Ticket
# Fill this form and present to the Orchestrator (Claude Code) to start an L2.5 pipeline run.

---

## METADATA
```yaml
wp_id:          # Format: {PROJECT-PREFIX}-P{NNN}-WP{NNN}  e.g., SBXF-P001-WP003
project_id:     # Must match _aos/projects.yaml  e.g., aos-sandbox-full
profile:        L2.5   # DO NOT CHANGE — this declares L2.5 execution
created:        # YYYY-MM-DD
owner:          team_00
operator_dna_version:  # Copy from core/operator_dna.yaml → version field
```

---

## PROBLEM STATEMENT
*What problem are we solving? Why now? Why this matters.*

[3-5 sentences minimum. Be specific. Include the pain point, not just the solution.]

---

## TARGET USERS / ACTORS
*Who is involved in this system?*

- Actor 1: [name + role]
- Actor 2: [name + role]
- (System actor): [if applicable]

---

## DESIRED OUTCOME
*What does success look like? Must be measurable.*

When this WP is complete:
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Measurable outcome 3]

---

## SCOPE BOUNDARIES
*What is explicitly OUT OF SCOPE for this WP.*

OUT:
- [Item 1]
- [Item 2]

---

## OPEN QUESTIONS
*Known unknowns. Do not hide them. The architect will resolve these in LOD300.*

1. [Question 1]
2. [Question 2]
(Leave blank if truly none — the architect will surface them)

---

## CONTEXT & BACKGROUND
*Anything the managed agent needs to know to understand this WP correctly.*

[Optional: links to prior WPs, relevant existing code, decisions already made]

---

## NOTES FOR ORCHESTRATOR
*Special instructions for this run (optional).*

- Priority: [NORMAL / HIGH]
- Deadline context: [if any]
- Related WPs: [if any dependencies]
