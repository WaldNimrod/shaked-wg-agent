# LOD Research Deepening Protocol
# Version: 0.1.0
# Applies to: All LOD production phases in L2.5 pipeline

---

## PRINCIPLE

Each LOD transition is not merely "write a more detailed document."
It is a **research operation** that progressively eliminates unknowns,
validates assumptions, and deepens the understanding of the problem.

The managed pipeline has a structural advantage: it can systematically
run research phases before production phases — extracting maximum signal
at each stage before committing to spec decisions.

**Result:** LOD400 produced through 3 research rounds is qualitatively
different from LOD400 produced by jumping straight from LOD100.
It has fewer surprises, lower FCP rate, and higher first-pass quality at Phase 5.

---

## RESEARCH ROUNDS BY LOD LEVEL

### Round R1: Concept Research (before LOD200 production)

**Objective:** Understand the problem landscape before committing to any solution concept.

**Research tasks:**
```
1. EXISTING PATTERNS
   - Search codebase for similar features or flows
   - Identify reusable components, APIs, or data structures
   - Flag: what already exists that this WP extends vs. replaces?

2. RISK SURFACE
   - What are the top 3 ways this could fail or be misunderstood?
   - What assumptions in the LOD100 are unverified?
   - What external dependencies could constrain the solution?

3. UNKNOWNS MAPPING
   - What questions must be answered in LOD300 that cannot be deferred?
   - What would break LOD400 if left unresolved?
   - Produce: Open Questions list (10+ candidates → top 5 critical)

4. COMPARABLE PRECEDENT
   - Are there previous WPs in this project with similar scope?
   - What decisions were made there? What worked? What caused FCP cycles?
   - Read: gate_history of similar WPs in roadmap.yaml

5. OPERATOR ALIGNMENT CHECK
   - Does the LOD100 problem statement align with operator_dna.yaml priorities?
   - Is there a tension between LOD100 scope and current project priorities?
   - Flag if scope appears misaligned before investing in LOD200.
```

**Output:** Research memo appended to LOD200 draft as `## Research Findings — R1`  
**Time budget:** Spend as much time on research as on LOD200 production itself.

---

### Round R2: System Research (before LOD300 production)

**Objective:** Understand the full system behavior space before committing to state machine.

**Research tasks:**
```
1. STATE SPACE EXPLORATION
   - What are ALL the states this system can be in? (not just happy path)
   - What are the error states? Race conditions? Timeout states?
   - What states exist in adjacent systems that this WP touches?
   - Map: every transition that exists vs. every transition that SHOULD exist

2. INTEGRATION CONSTRAINTS
   - What APIs does this system call or expose?
   - What are the actual constraints of those APIs? (rate limits, schemas, auth)
   - Read the actual source code of integration points — not assumptions
   - What data migrations does this require?

3. EDGE CASE INVENTORY
   - What happens when: input is empty, input is maximum size, user has no permission,
     network fails mid-operation, concurrent operations happen, data is corrupted?
   - Each edge case becomes a defined state in the state machine.

4. PRECEDENT REVIEW
   - How have similar state machines been handled in this codebase?
   - Read 2-3 existing state machines in the project
   - Extract: what patterns to follow, what anti-patterns to avoid

5. ACCEPTANCE CRITERIA PRE-VERIFICATION
   - For each LOD200 acceptance criterion: can it actually be tested?
   - What test infrastructure exists that supports this?
   - Flag untestable ACs before they reach LOD400.

6. OPEN DECISIONS RESOLUTION
   - Take the Open Decisions from R1
   - For each: attempt to resolve from code reading or established convention
   - If unresolvable → remain open in LOD300, surface at Phase 3 gate
```

**Output:** Research memo appended to LOD300 draft as `## Research Findings — R2`  
**Key rule:** No LOD300 section is written without reading the relevant source code first.

---

### Round R3: Execution Research (before LOD400 production)

**Objective:** Resolve ALL remaining ambiguity before execution-ready spec is locked.

**Research tasks:**
```
1. EXACT VALUES HUNT
   - Collect every value that LOD400 must specify:
     * UI: exact labels, exact copy, exact button text (from design system)
     * API: exact field names, exact types, exact validation patterns
     * DB: exact column names, exact constraints, exact default values
     * Errors: exact error codes, exact error messages (from existing patterns)
   - Read: existing similar files/endpoints for naming patterns

2. LIBRARY / FRAMEWORK BEHAVIOR
   - For each technical decision: what does the actual library do?
   - Read documentation OR existing usage in codebase
   - Flag: any library behavior that conflicts with LOD300 design?

3. PERFORMANCE BASELINE
   - What is the current performance of the system this WP affects?
   - What are the performance constraints in LOD300?
   - Are those constraints actually achievable given current infrastructure?

4. TESTING INFRASTRUCTURE AUDIT
   - What test utilities exist for each acceptance criterion?
   - Write test skeletons (just structure, no implementation) for top 5 ACs
   - This forces LOD400 precision — if you can't write the test skeleton, the AC is too vague

5. FINAL OPEN DECISIONS
   - Take any remaining Open Decisions from R2
   - Each MUST be resolved before LOD400 is locked
   - If still unresolvable → escalate to Orchestrator for Nimrod decision (rare)
   - Producing LOD400 with open decisions is a LOD400 defect (FCP-4 risk)

6. DEVIATION ANTICIPATION
   - What parts of LOD300 are most likely to cause implementation difficulty?
   - Where might the builder legitimately need to deviate from spec?
   - Pre-approve any acceptable deviation ranges in LOD400 itself
```

**Output:** Research memo appended to LOD400 draft as `## Research Findings — R3`  
**Iron rule:** LOD400 is not written until R3 is complete. Research precedes production.

---

## RESEARCH OUTPUT FORMAT

Append to every LOD document:

```markdown
## Research Findings — R{N}
*Produced by: {agent role} | Date: {YYYY-MM-DD}*

### What was researched:
- {item}: {finding}
- {item}: {finding}

### Open questions resolved:
- {question} → {resolution + source}

### Risks identified:
- {risk}: {mitigation approach}

### Remaining open decisions (unresolved):
- {decision}: {what is needed to resolve it} [→ surfaces at Phase {N} gate]

### Precedent patterns used:
- {pattern}: {where found in codebase} [path:line]
```

---

## RESEARCH TIME ALLOCATION

| LOD Level | Research (R-round) | Production | Ratio |
|-----------|-------------------|------------|-------|
| LOD200 | R1: ~30 min | LOD200: ~30 min | 1:1 |
| LOD300 | R2: ~60 min | LOD300: ~60 min | 1:1 |
| LOD400 | R3: ~45 min | LOD400: ~90 min | 1:2 |

Research takes as long as production — this is intentional.
The goal is not speed. The goal is first-pass Phase 5 quality.

---

## COMPOUND EFFECT ACROSS PHASES

```
LOD100 (human + chat)
    ↓ R1: concept research
LOD200 (concept, validated)
    ↓ R2: system research (deepens LOD200 findings)
LOD300 (system behavior, validated)
    ↓ R3: execution research (deepens LOD300 findings)
LOD400 (execution-ready, zero ambiguity)
```

Each research round builds on the previous. By LOD400:
- R1 findings have been validated or overridden by R2
- R2 findings have been resolved or overridden by R3
- All open decisions from LOD100 are closed
- Every acceptance criterion is testable (proven in R3 test skeletons)
- No surprises remain for the implementation teams

This is the compounding advantage of L2.5 over manual spec writing:
a managed agent can spend research time systematically in a way a human rarely does.
