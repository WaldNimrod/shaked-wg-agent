# Content WP Lifecycle — Canonical Definition
## Module 13 | version: 1.0.0 | status: CANONICAL
## Applies to: lifecycle_archetype: CONTENT_SUBSTRATE

---

## 0. Core Principle

Every unit of information entering the corpus — regardless of source —
goes through the same LOD funnel in this exact order:

```
LOD100 → LOD200 → LOD300 → LOD400 → L-GATE_BUILD → L-GATE_VALIDATE
```

**Skipping any LOD stage is a process violation.**

The weight of the WP is in specification (LOD100–LOD400).
Implementation (file update) is the trivial step.

---

## 1. Information Source Types

Four source types trigger a new WP. All converge into the same funnel.

| Type | Description | Initial artifact |
|------|-------------|-----------------|
| **Message / Idea** | Ad-hoc note from domain owner | `feedback/` draft |
| **Research session** | Team investigation in a domain | `feedback/` report |
| **File / document** | Provided by domain owner | `sources/inbox/` |
| **Scheduled scan** | Automated sweep (future) | `sources/inbox/` |

---

## 2. LOD Funnel — Mandatory

### LOD100 — What is it? Is it relevant?

**Principle:** Raw description of the information as received.
Open questions are allowed. Goal: taste check — does this belong in the corpus?

Gates to: **L-GATE_ELIGIBILITY**

Checklist:
- [ ] What is this information? (describe without analyzing)
- [ ] Why is it potentially relevant to the corpus?
- [ ] Preliminary go / no-go — is it worth continuing?

Open questions are permitted at this stage.
Template: `templates/LOD100_CONTENT_SOURCE.md`

---

### LOD200 — Where does it belong?

**Principle:** Last cheap checkpoint — real go / no-go.
Map to an existing chapter / section / principle, or define a new one.
No final wording yet. Decide: where does it live and how does it connect?

Gates to: **L-GATE_SPEC** (initial)

Checklist:
- [ ] Target file / chapter identified (exact name)
- [ ] Relationship to existing content: expands / corrects / opens new section?
- [ ] Local and system-wide impacts documented
- [ ] Explicit go / no-go decision recorded
- [ ] If decision or dilemma → apply Decision Package (§4)

Do not continue if the placement is unclear. Stop here, not at LOD400.
Template: `templates/LOD200_CONTENT_PLACEMENT.md`

---

### LOD300 — What is the structure?

**Principle:** Not "where" anymore — "how much and in what format."
Map content structure before final wording. Prevents rewriting at LOD400.
**Never jump from LOD200 directly to LOD400.**

Gates to: **L-GATE_SPEC** (confirmation)

Checklist:
- [ ] Content structure: headings, sections, tables — correct format for this corpus?
- [ ] Scope boundary: what stays outside this unit (explicit)
- [ ] Every factual claim → source identified (extraction over invention)
- [ ] Language check: corpus content language vs. communication language

Template: `templates/LOD300_CONTENT_STRUCTURE.md`

---

### LOD400 — Exact paragraphs and location

**Principle:** Zero TBD. Zero interpretation.
This is the "product" the WP was opened for.
If any TBD remains → return to LOD300.
**Domain owner (Team 00) must approve before L-GATE_BUILD.**

Gates to: **L-GATE_SPEC** (final) → **L-GATE_BUILD**

Checklist:
- [ ] Exact target filename
- [ ] Exact location in file: after which heading / line / section
- [ ] Final wording — copy-paste ready
- [ ] Team 00 approval recorded
- [ ] Zero TBD — no ambiguity

Template: `templates/LOD400_CONTENT_SPEC.md`

---

## 3. Gate Spine

| Gate | Question | Evidence |
|------|----------|----------|
| **L-GATE_ELIGIBILITY** | Is the source ready to process? | LOD100 complete · source exists · no blocker |
| **L-GATE_SPEC** | LOD400 zero-TBD? Approved? | All LOD stages done · Team 00 approved · location + wording final |
| **L-GATE_BUILD** | Corpus files updated as specified? | Exactly per LOD400 · LOD500 draft ready |
| **L-GATE_VALIDATE** | Output meets fidelity standards? | Team 190 cross-engine · AC-CS-01..06 · AS_MADE_LOCK |

### L-GATE_BUILD — Implementation

- Update corpus files exactly per LOD400 — no improvisation
- LOD500 draft: what was updated vs. what was specified
- Every claim = verified source or `UNVERIFIED` tag
- Version bump: patch / minor / major per corpus versioning rules

### L-GATE_VALIDATE — Closure

- Validator engine ≠ builder engine (Iron Rule — unconditional)
- AC-CS-01: all LOD400 sections present in output
- AC-CS-02: no unverified claims
- AC-CS-03: semantic versioning applied correctly
- AC-CS-04: manifest / index updated and internally consistent
- AC-CS-05: cross-engine review complete
- AC-CS-06: deviations from LOD400 documented with justification
- Canonical version pointer updated **only after** PASS verdict
- WP archived

---

## 4. Decision Package (mandatory when decisions arise)

When a WP discussion includes a decision or dilemma, **always** produce this structure.
Not optional.

```markdown
## Decision — [topic]

### Context

### System location
(where does this sit in the corpus / workflow?)

### Options (minimum 3)
- Option A:
- Option B:
- Option C:

### Pros / cons (relevant parameters per option)

### Costs — time + resources

### Impacts — local + system-wide

### Ranked recommendation + reasoning
1. [best option] — why it wins
2. ...
3. ...
```

**Binary framing preferred** — when possible, frame as A vs B for faster, higher-quality decisions.
**Dual-path inspection** — always examine the path not chosen. Document it.

Template: `templates/DECISION_PACKAGE.md`

---

## 5. stage_mapping Values for roadmap.yaml

```yaml
stage_mapping: "LOD100"           # eligibility + taste check
stage_mapping: "LOD200"           # go/no-go + placement
stage_mapping: "LOD300"           # structure design
stage_mapping: "LOD400"           # exact paragraphs — spec complete
stage_mapping: "LOD400 + Build"   # spec + file update in one WP (simple sources)
stage_mapping: "LOD100–LOD400"    # full funnel in one WP (small/clear sources)
```

---

## 6. Compatibility

- Gate spine (L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE): **UNCHANGED**
- Iron Rules: **ALL APPLY** — cross-engine validation at L-GATE_VALIDATE unconditional
- LOD standard (LOD100–LOD500): **UNCHANGED** — content is domain-adapted, standard is not
- Backwards compatible: LOD300 is made explicit (was implicit in document-lifecycle module)

## Evidence

- PLA_CONTENT_SUBSTRATE.md (`methodology/lifecycle-archetypes/`) — gate mapping, AC-CS-01..06
- nimrod-book `core/15_LIFECYCLE_WP.md` — first domain implementation
- nimrod-book `CLAUDE.md` — session startup integration

## Terminology Gloss — CONTENT_SUBSTRATE (temporary, per AOS-V329 scope)

Generic AOS lean-kit vocabulary originally designed for SOFTWARE projects.
For CONTENT_SUBSTRATE domains, read these aliases:

| Generic term | Read as | Meaning |
|--------------|---------|---------|
| implementation | **corpus file update** | Writing / updating markdown + JSON per LOD400 spec |
| build | **corpus assembly** | Assembling verified corpus from approved LOD400 units |
| integration | **cross-source merge** | Merging content across GPT / Claude / critic engine outputs |
| CI / automated tests | **corpus QA** | AC-CS-01..06 validation by a different engine than the builder |
| deploy | **publish snapshot** | Versioned Markdown + JSON + Context Pack bundle |
| bug fix | **corpus correction** | Fixing factual / consistency defects in approved corpus |

**Status:** Temporary short-term fix. AOS-V329-WP-CONTENT-ARCHETYPE-POLISH
scope includes producing a full lexicon and **removing this gloss** as a prelude.

**Rule:** When a lean-kit template or artifact uses the generic term, agents in
CONTENT_SUBSTRATE domains substitute the CONTENT_SUBSTRATE meaning.
