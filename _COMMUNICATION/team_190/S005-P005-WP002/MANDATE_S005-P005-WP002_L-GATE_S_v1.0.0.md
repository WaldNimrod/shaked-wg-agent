---
id: MANDATE_S005-P005-WP002_L-GATE_S_v1.0.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: GATE_MANDATE
gate: L-GATE_S
wp: S005-P005-WP002
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# L-GATE_S Mandate — S005-P005-WP002: Facebook Manual Listing Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | L-GATE_S (Spec Authorization) |
| Work Package | S005-P005-WP002 |
| Label | Facebook manual listing parser — LLM-based Hebrew extraction |
| Track | A (new scraper following BaseScraper pattern) |
| Profile | L0 |
| Priority | HIGH |
| Risk | MEDIUM (new component: LLM integration + Hebrew NLP) |
| Milestone | S005 — Israel Market Expansion |

## 2. Prior Gate History

| Gate | Result | Date | Validator | Notes |
|------|--------|------|-----------|-------|
| (none) | — | — | — | First gate for this WP |

## 3. Scope — What This Gate Validates

Per L-GATE_S criteria for Team 190:

1. **Spec exists at minimum LOD200 level** — clear domain, scope, deliverables
2. **All acceptance criteria are measurable and unambiguous**
3. **No Iron Rule violations**
4. **Domain and process variant (Track A) correctly identified**
5. **Spec is sufficient for an implementation team to begin without clarification**

## 4. Validation Criteria

| VC | Criterion | What to Check |
|----|-----------|---------------|
| VC-01 | LOD200 completeness | All required sections present with adequate detail |
| VC-02 | Problem statement clarity | Facebook market significance established, why manual approach chosen (legal, ToS, privacy), why LLM parsing is the right tool |
| VC-03 | Scope boundaries | Clear separation: manual acquisition (in scope) vs automated scraping (out of scope); WP002 vs WP003 boundary clean |
| VC-04 | Success criteria measurability | All SC-01 through SC-09 can be verified with tests or inspection |
| VC-05 | Track A justification | New scraper subclass following BaseScraper pattern — confirm this fits Track A criteria |
| VC-06 | Input format specification | JSON input schema is well-defined with required/optional fields |
| VC-07 | LLM integration design | Provider selection, API key management, cost model, graceful fallback — all addressed |
| VC-08 | Privacy safeguards | PII stripping (phone numbers, names) explicitly designed in, not afterthought |
| VC-09 | Risk assessment completeness | LLM availability in Cowork sandbox, Hebrew accuracy, adoption risk — identified with mitigations |
| VC-10 | Strategic alignment | Maps to D5 (Facebook agent evaluation) Phase 1 recommendation |
| VC-11 | Affected components accuracy | New files + modifications listed; no hidden changes to existing code |
| VC-12 | No Iron Rule violations | Cross-engine rule, independence, governance compliance |

## 5. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP002/LOD200_S005-P005-WP002.md` | **Primary artifact** — LOD200 spec under review |
| `_aos/roadmap.yaml` | WP registration (search for S005-P005-WP002) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper interface (pattern to follow) |
| `shaked_wg_agent/scrapers/homeless.py` | Recent scraper example (reference for pattern compliance) |
| `data/sources.json` | Source registry (will be modified) |
| `data/profiles/pardes-hanna.json` | Profile (will be modified) |

## 6. Output

**Verdict file:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP002_L-GATE_S_v1.0.0.md`

**Verdict options:**
- `PASS` — spec approved, proceed to LOD400
- `PASS_WITH_FINDINGS` — spec approved with minor findings to address in LOD400
- `BLOCK` — spec has material deficiencies; must be revised before LOD400

**Constraints:**
- Cross-engine: validator (openai) != builder (cursor-composer)
- Independence: form conclusions from primary artifacts ONLY
- Evidence: cite specific spec sections for each finding
