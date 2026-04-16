---
id: MANDATE_S005-P005-WP003_L-GATE_S_v1.0.0
from: Team 110 (Architecture Agent)
to: Team 190 (Senior Constitutional Validator)
date: 2026-04-15
type: GATE_MANDATE
gate: L-GATE_S
wp: S005-P005-WP003
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
engine_constraint: "validator engine (openai) != builder engine (cursor-composer)"
---

# L-GATE_S Mandate — S005-P005-WP003: Facebook Email Notification Parser

## 1. Header

| Field | Value |
|-------|-------|
| Gate | L-GATE_S (Spec Authorization) |
| Work Package | S005-P005-WP003 |
| Label | Facebook email notification parser — passive acquisition |
| Track | A (new scraper following BaseScraper pattern) |
| Profile | L0 |
| Priority | MEDIUM |
| Risk | MEDIUM (email parsing + external dependency on FB notification format) |
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
| VC-02 | Problem statement clarity | Why email-based acquisition complements WP002 manual input; coverage gap identified |
| VC-03 | Scope boundaries | Clear separation from WP002; dependency on WP002's LLM parser documented |
| VC-04 | Success criteria measurability | All SC-01 through SC-11 can be verified with tests or inspection |
| VC-05 | Track A justification | New scraper subclass following BaseScraper pattern — confirm Track A fit |
| VC-06 | Dependency declaration | Hard dependency on S005-P005-WP002 explicitly stated and justified |
| VC-07 | IMAP integration design | Secure authentication, credential management (env vars), connection handling, retry logic |
| VC-08 | Email parsing robustness | Multiple FB notification formats handled (single post, digest, popular posts) |
| VC-09 | Privacy safeguards | Same PII policy as WP002; email credentials in env vars only |
| VC-10 | Deduplication strategy | Cross-source dedup (email vs manual vs other sources) — approach defined |
| VC-11 | Graceful degradation | No IMAP config → returns []; no LLM API → returns []; file-mode fallback |
| VC-12 | Risk assessment | Facebook format changes, truncated snippets, coverage limitations — identified |
| VC-13 | No Iron Rule violations | Cross-engine, independence, governance compliance |

## 5. Files to Review

| File | Purpose |
|------|---------|
| `_aos/work_packages/S005-P005-WP003/LOD200_S005-P005-WP003.md` | **Primary artifact** — LOD200 spec under review |
| `_aos/work_packages/S005-P005-WP002/LOD200_S005-P005-WP002.md` | Dependency — WP002 spec (LLM parser reused) |
| `_aos/roadmap.yaml` | WP registration and dependency chain (search for S005-P005-WP003) |
| `shaked_wg_agent/scrapers/base.py` | BaseScraper interface (pattern to follow) |
| `data/sources.json` | Source registry (will be modified) |

## 6. Output

**Verdict file:** `_COMMUNICATION/team_190/VERDICT_S005-P005-WP003_L-GATE_S_v1.0.0.md`

**Verdict options:**
- `PASS` — spec approved, proceed to LOD400
- `PASS_WITH_FINDINGS` — spec approved with minor findings to address in LOD400
- `BLOCK` — spec has material deficiencies; must be revised before LOD400

**Constraints:**
- Cross-engine: validator (openai) != builder (cursor-composer)
- Independence: form conclusions from primary artifacts ONLY
- Evidence: cite specific spec sections for each finding
