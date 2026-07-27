---
pla_id: CONTENT_SUBSTRATE
version: "1.0.0"
status: ACTIVE
authority: Team 00
authored_by: Team 100
date: 2026-04-15
proven_in: nimrod-book (active — NB-V1 milestone, 2026-04-15)
supersedes: null
gate_spine: L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE
---

# Project Lifecycle Archetype: CONTENT_SUBSTRATE
# Knowledge bases, context substrates, document corpora, and prompt libraries

---

## 1. What This Archetype Covers

Use CONTENT_SUBSTRATE when the primary deliverable is a knowledge artifact — a structured corpus of information designed for consumption by agents, humans, or hybrid workflows. The product is not running software; it is a body of content that has been sourced, verified, synthesized, and systematized.

**Canonical example:** nimrod-book — a living context substrate used as base-context injection for all AOS-managed projects.

**Signs this archetype applies:**
- The output is a document bundle, knowledge base, prompt library, or structured corpus
- Work involves intake of existing sources (files, interviews, databases, memory artifacts)
- There is a meaningful difference between "raw material" and "refined knowledge artifact"
- Verification is about epistemic quality (accuracy, completeness, consistency) — not functional correctness
- Multiple passes through the same material are expected (mining → gap-fill → merge)
- The corpus evolves continuously and requires version history

**Signs it does NOT apply:**
- The project produces executable software → `SOFTWARE`
- The project produces 3D models or visual assets → `3D_CREATIVE`
- The project produces an autonomous AI agent for a domain → `DOMAIN_AGENT`

---

## 2. Stage Sequence (Stages 0–6)

| Stage | Name | What happens | Domain-specific meaning |
|-------|------|--------------|-------------------------|
| **Stage 0** | Source Intake | Identify, locate, and stage all input sources | Files, interviews, exports, memory artifacts placed in intake buffer |
| **Stage 1** | Mining | Read each source; extract all signals; classify and tag | Raw extraction — no synthesis yet. Each source → extraction notes file |
| **Stage 2** | Deep Profile | Structured interrogation of subject via direct questions or deep analysis | Gap-targeted questions answered in-session; each answer opens a new chapter |
| **Stage 3** | Gap Fill | Address known gaps using targeted Q&A or secondary sources | 13_GAPS_AND_QUESTIONS.md pattern; each gap → one meaningful new section |
| **Stage 4** | Cross-Model Merge | Run same content through multiple LLM engines for depth, synthesis, critique | Different engines for depth, long-form, critique — results unified |
| **Stage 5** | Systemize | Integrate all draft material into unified, versioned corpus | Bundle all WPs; update manifest/index; produce context packs; bump version |
| **Stage 6** | Continuous Update | Recurring maintenance cycle — drift check + source sweep + version ratification | Quarterly or event-triggered; preserves corpus accuracy over time |

### Stage flow notes:
- Stages 0–1 often run concurrently per source (intake one source → mine it → intake next)
- Stage 2 and Stage 3 are often interleaved within a single WP
- Stage 4 requires multi-engine access; may be deferred or skipped for minor updates
- Stage 6 is recurring and ongoing; it restarts the cycle at Stage 0 for new sources
- Multiple stages may map to a single WP — this is normal and expected

---

## 3. Gate Mapping

The universal gate spine is unchanged. Each stage maps into a gate envelope.

| Gate | Gate question (universal) | Stages that fall here | Domain-specific evidence at this gate |
|------|--------------------------|----------------------|---------------------------------------|
| **L-GATE_ELIGIBILITY** | Is this WP eligible to enter the pipeline? | Stage 0 — sources identified | Source list documented; extraction scope defined; no unresolved input blockers |
| **L-GATE_SPEC** | Is the spec complete enough to authorize work? | Stage 0–1 (intake plan) or Stage 2 (question list) | LOD200 defines which corpus sections will be produced; source list confirmed; question list scoped |
| **L-GATE_BUILD** | Has the domain construction been completed? | Stage 1–5 (mining → systemize) | Extraction notes exist for each source; draft files produced; cross-model merge results available; corpus integration complete |
| **L-GATE_VALIDATE** | Does the output meet quality and fidelity standards? | Stage 5–6 (systemize → continuous update setup) | Cross-engine fidelity review; no unresolved gaps in scope; corpus consistent; LOD500 verdict issued |

### LOD artifact guidance (domain-adapted):

| LOD Level | Standard question | CONTENT_SUBSTRATE adaptation |
|-----------|-------------------|------------------------------|
| LOD100 | What problem? | What knowledge is missing or unsystematized? What will this corpus enable? |
| LOD200 | What kind of solution? | Which stages are active in this WP? Which sources or questions are in scope? Which corpus sections will exist after? |
| LOD400 | What exactly must be built? | Which sources are extracted and how? Which questions are asked? Which chapters/sections result? Exact version bump defined. |
| LOD500 | What was actually produced? | Which extractions were completed? Which chapters were written? Cross-engine fidelity verdict (FULL_MATCH / DEVIATIONS). |

---

## 4. Deliverable Types Per Stage

| Stage | Deliverable type | File pattern example |
|-------|-----------------|----------------------|
| Stage 0 | Source log, staged files | `SOURCES_LOG.md`, inbox files in `sources/inbox/` |
| Stage 1 | Extraction notes | `appendix/{NN}_{TOPIC}_EXTRACTION_NOTES.md` |
| Stage 2 | Deep profile draft | `feedback/DRAFT_{WP}_{TOPIC}_v1.0.0.md` |
| Stage 3 | Gap fill draft | `feedback/DRAFT_WP_{ID}_Q{N}_{TOPIC}_v1.0.0.md` |
| Stage 4 | Merged synthesis notes | Multi-engine outputs; unified draft in `feedback/` |
| Stage 5 | Versioned corpus bundle | `{corpus}_v{X.Y.Z}/` directory + `manifest.json` + `CURRENT.json` |
| Stage 6 | Maintenance record | `feedback/STAGE6_MAINTENANCE_{YYYYMM}.md` |

---

## 5. Team Roles Per Stage

| Stage | Primary role | Validator | Notes |
|-------|-------------|-----------|-------|
| Stage 0 | Team 00 (locates sources) or Team 100 | Team 100 | Source availability is often a human judgment |
| Stage 1 | Team 100 (LLM reads and extracts) | Team 190 | Cross-engine: extractor ≠ validator (Iron Rule) |
| Stage 2 | Team 00 (human answers questions) + Team 100 (mines) | Team 190 | Human is the source; LLM is the miner |
| Stage 3 | Team 00 (answers) + Team 100 (mines immediately after) | Team 190 | Same pattern as Stage 2 |
| Stage 4 | Team 100 (depth/structure) + Team 110 (long-form synthesis) + Team 190 (critique) | All three | Multi-engine is the mechanism; each has a distinct role |
| Stage 5 | Team 100 (integration) | Team 190 (fidelity check) | Cross-engine validation mandatory at LOD500 |
| Stage 6 | Team 100 (sweep) + Team 00 (ratification) | Team 190 (drift check) | Quarterly or event-triggered |

---

## 6. Validation Criteria Per Stage

**Stage 0 → Stage 1:** Every planned source is staged in intake buffer. No source listed as "TBD location."

**Stage 1 → Stage 2/3:** Every staged source has an extraction notes file. Sources classified as INSTRUMENT (not SOURCE) are documented with justification and the correct classification.

**Stage 2/3 → Stage 4/5:** Every gap listed in scope has a corresponding draft section. No open questions from the gap list remain unanswered and undeferred.

**Stage 4 → Stage 5:** All engine outputs are available. Conflicts between engine interpretations are resolved and documented. No synthesis is presented without tracing it back to a source.

**Stage 5 → Stage 6 (or COMPLETE):** Version bundle is consistent. Manifest/index is updated. Drift checklist passes. No chapter references a fact from an unverified source. Cross-engine validator confirms fidelity.

**Stage 6 → next cycle Stage 0:** Maintenance record authored. New source candidates logged. Team 00 ratification of corpus `CURRENT.json` complete. No corpus content modified without audit trail.

---

## 7. `stage_mapping` Field — Canonical Values

When using this archetype, the `stage_mapping` field in `roadmap.yaml` WP entries uses the following canonical values:

```yaml
stage_mapping: "Stage 0 (Source intake)"
stage_mapping: "Stage 1 (Mining)"
stage_mapping: "Stage 2 (Deep profile)"
stage_mapping: "Stage 3 (Gap filling)"
stage_mapping: "Stage 4 (Cross-model merge)"
stage_mapping: "Stage 5 (Systemization)"
stage_mapping: "Stage 6 (Continuous update)"

# Compound — multiple stages in one WP:
stage_mapping: "Stage 0 (Source intake) + Stage 1 (Mining)"
stage_mapping: "Stage 2 (Deep profile) + Stage 3 (Gap filling)"
stage_mapping: "Stage 4 (Cross-model merge) + Stage 5 (Systemization — full)"
```

Compound mappings (multiple stages in one WP) are explicitly permitted. The stage_mapping is informational; gate authority remains with the universal gate model.

---

## 8. L-GATE_VALIDATE Validation AC Extensions

At L-GATE_VALIDATE, Team 190 uses standard LOD500 fidelity criteria **plus** these domain-specific acceptance criteria:

- **AC-CS-01:** Every corpus chapter cited in LOD400 scope exists in the output bundle
- **AC-CS-02:** No chapter makes a factual claim traceable only to an unverified source (must have primary source or explicit UNVERIFIED tag)
- **AC-CS-03:** Version bump follows semantic versioning rules for this corpus (patch = wording; minor = new section/file; major = structural schema change)
- **AC-CS-04:** Manifest or index file is updated and internally consistent (no broken references)
- **AC-CS-05:** Cross-engine review was performed by a different engine than the primary builder (Iron Rule — cross-engine validation always)
- **AC-CS-06:** Known deviations from LOD400 scope are documented with justification in LOD500

---

## 9. Compatibility Notes

- **Gate spine:** Unchanged. L-GATE_ELIGIBILITY → L-GATE_SPEC → L-GATE_BUILD → L-GATE_VALIDATE applies in full.
- **Profile:** L0 (lean/manual). No engine infrastructure required. Discipline-driven.
- **LOD standard:** Unchanged. LOD100–LOD500 apply. The domain adaptation is in the LOD guidance column above — not in the standard itself.
- **Iron Rules:** All apply. Cross-engine validation at L-GATE_VALIDATE is unconditional.
- **`stage_mapping` values in nimrod-book `_aos/roadmap.yaml`** already conform to §7 above. No migration required. The existing nimrod-book WPs are the proven reference implementation.
- **Stage 6 WPs:** Registered as recurring lean WPs in `roadmap.yaml` with their own L-GATE_ELIGIBILITY → L-GATE_VALIDATE cycle. They are not exempt from governance.
- **Backwards compatibility:** zero breaking changes to any existing AOS artifact.

---

## 10. Domain Interaction Protocols (Iron Rule #14)

CONTENT_SUBSTRATE archetypes frequently require a domain-specific interaction
protocol above the archetype defaults — **how** the author and engine collaborate,
the division of labor, question strategy, communication style, answer-quality
rules, and cross-engine role assignments. This is different from stage
definitions: it governs the conversational texture of each session.

Per **Iron Rule #14** (Environment base / Domain override with approval) —
`methodology/AOS_CONCEPT_AND_PRINCIPLES.md` — a domain MAY define such a
protocol in its own spoke artifacts (e.g. `core/01_BOOK_INTERACTION_PROTOCOL.md`)
subject to:

1. **team_00 approval** — Principal signs off on the protocol content
2. **team_100 conflict check** — confirms no clash with hub governance, Iron Rules, or archetype defaults
3. **Domain-only storage** — protocol lives in spoke, NOT in hub; agents read it at session startup via an explicit reference in `CLAUDE.md` / `AGENTS.md` / `.cursorrules`
4. **Single-file maintenance** — protocol concentrated in ONE domain file for easy updates (principle adopted from nimrod-book 2026-04-21)

### Canonical reference (proven in nimrod-book)

- Spoke protocol file: `core/01_BOOK_INTERACTION_PROTOCOL.md`
- Invocation: mandatory read at session startup via CLAUDE.md §Mandatory session startup
- Scope: user-vs-engine labor split per stage, communication style, engine expectations, question strategy, answer-quality rule, cross-engine role assignments, online-vs-IDE policy

### Glossary alignment (short-term)

For CONTENT_SUBSTRATE domains, the following vocabulary disambiguation applies
(pending full glossary consolidation under AOS-V329):

| Term (generic) | In CONTENT_SUBSTRATE | Meaning |
|----------------|----------------------|---------|
| "implementation" | "corpus file update" | Writing / updating markdown + JSON per LOD400 spec |
| "build" | "corpus assembly" | Assembling verified corpus from approved LOD400 units |
| "integration" | "cross-source merge" | Merging content across GPT / Claude / critic engine outputs |
| "CI" | "corpus QA" | AC-CS-01..06 validation by a different engine than builder |
| "deploy" | "publish snapshot" | Versioned Markdown + JSON + Context Pack bundle |

This glossary is **temporary** (Option 2 fix per hub decision 2026-04-21) until
AOS-V329-WP-CONTENT-ARCHETYPE-POLISH delivers the full lexicon. The V329 WP
scope includes **removal of this temporary section** as a prelude.
