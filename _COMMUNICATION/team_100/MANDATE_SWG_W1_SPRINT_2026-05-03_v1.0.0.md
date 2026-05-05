---
id: MANDATE_SWG_W1_SPRINT_2026-05-03_v1.0.0
type: SPRINT_MANDATE
sprint_id: SWG-W1-SPRINT
from: team_00 (Owner — Nimrod) via team_100 (current orchestrator-of-record, this session)
to: team_100 (NEW — fresh orchestrator session, runs the W1 sprint)
date: 2026-05-03
status: OPEN
priority: P0_CRITICAL
expects_response: true
sla_hours: 120 (5 working days, ends 2026-05-08 23:59 Europe/Zurich)
spoke_profile: L0
project_window_constraint: 2026-05-31 (Shaked must vacate current housing; this sprint enables outreach phase)
authority_basis:
  - "Owner (team_00) directive 2026-05-03: 4-week deadline, 5-day dev sprint, manual-trigger only"
  - "ADR034 R9 — spoke-native sprint, file-based SSOT"
  - "Iron Rule #1 — cross-engine validation (sonnet builders ≠ haiku validators ≠ opus orchestrator)"
  - "TikTrack canonical sub-agent pipeline pattern (REPORT_TO_AOS_TEAM_100_SUB_AGENT_PIPELINE_PATTERN_2026-04-29_v1.0.0)"
related_artifacts:
  - data/profiles/default_PROFILE_POLICY.md (profile v1.8 SSOT, Layer-2 client refinements)
  - data/shaked_curated_2026-05-01.html (current published page v1.9)
  - _COMMUNICATION/team_110/MANDATE_SWG_PLATFORM_HARDENING_2026-04-30_v1.0.0.md (M1-M5 baseline)
  - _COMMUNICATION/team_100/MSG-HUB-20260429-003-RESPONSE.md (Option A LOD path canon)
engine_matrix:
  orchestrator: claude-opus-4 (or sonnet-class) — team_100 NEW session
  builders: claude-sonnet-4-6 (parallelizable per WP)
  internal_validators: claude-haiku-4-5 (per gate)
  external_validator: out-of-scope for L0 sprint (Owner waives external L-GATE_VALIDATE for this 5-day window)
---

# SPRINT MANDATE — SWG-W1 (5-Day Dev Sprint Before Shaked Outreach Phase)

## §1 — Goal & Strategic Context

### 1.1 The deadline that matters
Shaked must vacate current housing on **2026-05-30**. He needs a signed lease on a Basel WG room before then.

### 1.2 The dev window
Owner (team_00) directive 2026-05-03 specified: **5 days for development (Mon 2026-05-04 → Fri 2026-05-08)**. After Friday, all energy shifts to outreach + visits + decisions (3-week window).

### 1.3 Why this sprint exists
v1.9 of the curated page shipped 2026-05-03 with 10 listings sourced from flatfox.ch alone, with manual scoring & curation. To maximize Shaked's signing probability, this sprint expands the funnel and accelerates each manual update cycle:
- **Funnel ×3**: Add Weegee.ch (89 Basel WG-rooms) and RonOrp Basel (vegan/quiet keyword-rich) to existing flatfox source
- **Signal coverage**: Full-description extraction unblocks vegan/cooking-culture/quiet detection (current state: 0 vegan signals in budget-fit listings — RonOrp is the documented fix)
- **Tooling**: One-click HTML rebuild — current manual cycle ~90 minutes, target ≤15 minutes

### 1.4 Out of scope (explicitly waived by Owner 2026-05-03)
- Dynamic UI / SPA rebuild
- Long-term schema redesign (M9 dynamic profile UI)
- Unimarkt scraper (Playwright complexity > 5-day window — defer)
- Tutti, MeinWGZimmer, RealAdvisor, Comparis (defer)
- Cron / auto-scheduling — manual triggers only
- External cross-vendor L-GATE_VALIDATE — waived for this sprint due to time pressure

---

## §2 — Authority & Engine Matrix

### 2.1 Roles
| Role | Engine | Responsibility |
|---|---|---|
| **Orchestrator** (this mandate's recipient) | opus-class (or sonnet) | Dispatches sub-agents, tracks progress, commits, files daily PIPELINE_LOG |
| **Builder sub-agent** | sonnet | Writes code/specs per WP, runs tests, returns disposition |
| **Internal validator sub-agent** | haiku | L-GATE_*_R1 internal — fast preliminary checks |
| **Final approver** | opus-class | Reviews bundle handoff before declaring sprint DONE |
| **External canonical validator** | n/a for this sprint | Owner waived to fit 5-day window |

### 2.2 Iron Rule #1 satisfaction
- sonnet ≠ haiku → cross-engine independence within Anthropic ✓
- For full canonical compliance, a future cycle should add cross-vendor validation (Cursor/GPT-5/Codex) — Owner accepts the gap for this sprint

### 2.3 Authority chain
- **Owner (team_00 — Nimrod)** — supreme authority, accepts/rejects bundle on 2026-05-08
- **Current team_100 session (this mandate's author)** — handover-of-record; ceases dispatching after this mandate is filed
- **NEW team_100 session (mandate's recipient)** — owns the 5-day sprint orchestration end-to-end
- **team_110 (Domain Architect)** — NOT involved in this sprint; this is a tactical sprint, not LOD400-architect-authored. Builder sub-agents go directly from team_100.

---

## §3 — Work Package Decomposition (5 WPs)

### Dependency graph
```
W1.1 (Weegee scraper)                           [INDEPENDENT]
       │
W1.2 (Full-description extraction)              [INDEPENDENT — parallelizable with W1.1]
       │
       ▼
W1.3 (RonOrp scraper + signal extractor)        [DEPENDS ON W1.2 for full text]
       │
W1.4 (One-click HTML rebuild tool)              [DEPENDS ON W1.1, W1.2, W1.3 schemas]
       │
W1.5 (Integration test + first re-run)          [FINAL — depends on all]
```

### Wave dispatch plan
- **Wave 1 (Day 1, parallel)**: W1.1 + W1.2
- **Wave 2 (Day 2-3)**: W1.3 (after W1.2 PASS)
- **Wave 3 (Day 4)**: W1.4 (after W1.1+W1.2+W1.3 PASS)
- **Wave 4 (Day 5)**: W1.5 integration

If sonnet sub-agents complete waves faster, orchestrator may compress to 3-day effective timeline.

---

## §4 — Per-WP Specifications

### W1.1 — Weegee Basel Scraper

**Files in scope:**
- `shaked_wg_agent/scrapers/weegee.py` (NEW)
- `shaked_wg_agent/scrapers/__init__.py` (register)
- `data/sources.json` (add weegee entry, enabled for basel)
- `tests/test_scrapers/test_weegee.py` (NEW)
- `tests/fixtures/scrapers/weegee_basel_search.html` (NEW — anonymized snapshot)

**Source URL pattern:** `https://weegee.ch/de/search/city-basel?page={N}&filter=price_{MIN}_{MAX}`

**Acceptance criteria (testable):**
1. `pytest tests/test_scrapers/test_weegee.py::test_parse_basel_search` PASS — extracts ≥10 listings from fixture
2. `pytest tests/test_scrapers/test_weegee.py::test_listing_fields` PASS — each listing has: listing_id, source_listing_id, title, price (CHF), available_from, location_text, room_size_m2, direct_url, summary
3. `python -m shaked_wg_agent run --profile default` includes weegee source and returns ≥20 Basel listings (live test)
4. Listing schema matches existing flatfox connector output (compatible with `data/listings.json`)
5. Polite-delay: 5-10s between requests (respects robots.txt)
6. ruff + pytest clean

**Test plan:**
- Unit: parse fixture HTML, assert field extraction
- Integration: live fetch + persist to test DB
- Edge: empty results page, network timeout, malformed HTML

**Estimated effort:** 6h sonnet build + 1h haiku validation

### W1.2 — Full-Description Extraction (was M2 in earlier mandate)

**Problem:** Current `summary` field truncated at ~200 chars. Critical signals (vegan, "wir kochen gerne", "ruhige WG", "ohne Bürgschaft") live in body text 5+ sentences in.

**Files in scope:**
- `shaked_wg_agent/scrapers/base.py` — add `full_description: str` field to `ScrapedListing`
- `shaked_wg_agent/scrapers/flatfox.py` — extract full body, not truncated
- `shaked_wg_agent/scrapers/wgzimmer_pw.py` — extract full body (note: wgzimmer broken on selectors, fix beyond this WP, but extraction logic must be ready)
- `data/listings.json` migration — backfill `full_description` from `summary` for existing rows; new scrapes get full text
- `tests/test_scrapers/test_full_description.py` (NEW)

**Acceptance criteria:**
1. `ScrapedListing` exposes `full_description: str`, length ≥500 chars when source provides it
2. Migration adds field to existing 105 listings without breaking schema (`pytest tests/test_listings_schema_migration.py` PASS)
3. New scrapes populate `full_description` (avg length on flatfox ≥800 chars)
4. Existing tests still pass (no regressions)
5. ruff clean

**Estimated effort:** 5h sonnet + 1h haiku

### W1.3 — RonOrp Basel Scraper + Signal Extractors

**Files in scope:**
- `shaked_wg_agent/scrapers/ronorp.py` (NEW)
- `shaked_wg_agent/extractors/__init__.py` (NEW package)
- `shaked_wg_agent/extractors/diet_signals.py` (NEW — vegan/vegetarian/cooking-culture)
- `shaked_wg_agent/extractors/quiet_signals.py` (NEW — ruhig/quiet/calm/insulation)
- `shaked_wg_agent/extractors/social_signals.py` (NEW — community vibe, named-roommates, age extraction)
- `shaked_wg_agent/scorer.py` — integrate new extractor outputs into scoring (kitchen +cooking-culture bonus, quiet signal, etc.)
- `data/sources.json` (add ronorp entry)
- `tests/test_scrapers/test_ronorp.py` (NEW)
- `tests/test_extractors/test_diet_signals.py` (NEW — ≥15 cases)
- `tests/test_extractors/test_quiet_signals.py` (NEW — ≥10 cases)

**Source URL pattern:** `https://www.ronorp.net/basel/markt/immobilien-basel/wg-zimmer-basel`

**Acceptance criteria:**
1. RonOrp scraper extracts ≥10 Basel WG listings from live page (manual verification)
2. Diet extractor: regex pack matches `vegan|vegetar|pflanzenbasiert|fleischlos|plant.based|veggi|bio.küche` with case-insensitive German+English
3. Diet extractor recall ≥90% on 15 hand-labeled examples (8 positive, 7 negative)
4. Quiet extractor: matches `ruhig|quiet|calm|leise|schallisolier|sound.insul|peaceful`
5. Polite-delay 5-10s, respects RonOrp robots
6. Scorer integration: when `diet_signals.is_vegetarian_friendly == True`, kitchen score reaches max (6/6)
7. Re-run on existing 105 flatfox listings produces ≥3 cooking-culture detections (vs current 2)
8. ruff + pytest clean

**Test plan:**
- Unit: regex packs against fixture descriptions
- Integration: scrape RonOrp live, assert ≥10 listings
- Migration: re-run extractors on existing flatfox `full_description` field, validate count of detections increases vs v1.9 manual scoring

**Estimated effort:** 7h sonnet + 1.5h haiku (regex review especially important)

### W1.4 — One-Click HTML Rebuild Tool

**Files in scope:**
- `shaked_wg_agent/publisher/html_curated.py` (NEW)
- `shaked_wg_agent/publisher/templates/curated.html.j2` (NEW — Jinja2 template extracted from current static HTML)
- `shaked_wg_agent/publisher/scoring_v18.py` (NEW — Python implementation of the 13-param scorer used in v1.9 HTML)
- `shaked_wg_agent/__main__.py` — add subcommand `rebuild-html`
- `tests/test_publisher/test_html_curated.py` (NEW)

**CLI contract:**
```bash
python -m shaked_wg_agent rebuild-html --profile default --top 10 --out data/shaked_curated_$(date +%Y-%m-%d).html
```

**Acceptance criteria:**
1. Command produces valid HTML (W3C HTML5 validator clean)
2. Output structurally identical to v1.9 hand-crafted HTML (header, top matrix, filter bar, 10 cards, bottom 42-row matrix, footer)
3. Mobile-first CSS preserved (auto-collapse matrices on mobile)
4. Score computation deterministic given same input listings + transit cache
5. Cooking-culture badge renders when `diet_signals.is_vegetarian_friendly == True`
6. Runtime ≤30 seconds end-to-end
7. ruff + pytest clean
8. **Output bytewise comparable to current v1.9 HTML** for the 10 listings v1.9 used (acceptance regression test — confirms the tool reproduces what we ship today)

**Estimated effort:** 5h sonnet + 1h haiku

### W1.5 — Integration Test + First Production Re-Run

**Files in scope:**
- `_COMMUNICATION/team_100/SPRINT_RUN_2026-05-08_v1.0.0.md` (NEW — sprint completion report)
- `data/shaked_curated_2026-05-08.html` (NEW — first auto-rebuilt HTML)

**Acceptance criteria:**
1. End-to-end run: `python -m shaked_wg_agent run --profile default` returns listings from flatfox + weegee + ronorp (≥80 total, ≥150 with both new sources together)
2. Re-run produces `data/listings.json` with `full_description` populated on ≥80% of listings
3. Diet/quiet/social extractors populate respective fields; manual review of 20 random listings confirms accuracy
4. `python -m shaked_wg_agent rebuild-html --profile default` produces clean HTML in ≤30s
5. Manual verification: top-10 from rebuilt HTML includes ≥3 candidates from new sources
6. WP-level haiku validation gates all PASS (W1.1, W1.2, W1.3, W1.4)
7. Owner reviews bundle and accepts on 2026-05-08

**Estimated effort:** 6h orchestrator + 2h haiku integration validation

---

## §5 — Orchestration Plan (5-Day Sprint)

### Day 1 (Monday 2026-05-04) — Parallel Wave 1
- Pre-flight: read this mandate, run `validate_aos.sh`, confirm DB status
- Dispatch **W1.1 (Weegee scraper)** to sonnet sub-agent — independent worktree
- Dispatch **W1.2 (Full-description extraction)** to sonnet sub-agent — separate worktree
- End-of-day: both sub-agents return DONE/PARTIAL/BLOCKED
- Haiku validation on each (W1.1 L-GATE_BUILD_R1 + W1.2 L-GATE_BUILD_R1)
- Orchestrator commits + updates PIPELINE_LOG

### Day 2 (Tuesday 2026-05-05) — Wave 2 + Quality
- If W1.1 + W1.2 both PASS: dispatch **W1.3 (RonOrp + extractors)** to sonnet
- If W1.1 or W1.2 BLOCKED: orchestrator triages, dispatches a fix-up sonnet sub-agent
- Mid-day: haiku spec review of W1.3 regex pack (validators often catch over-broad patterns here)

### Day 3 (Wednesday 2026-05-06) — W1.3 Completion + Wave 3 prep
- W1.3 build returns; haiku validation on extractors with hand-labeled corpus
- If issues: rapid sonnet fix-up
- Begin **W1.4 (HTML rebuild)** dispatch — it depends on stable schemas from W1.1-W1.3

### Day 4 (Thursday 2026-05-07) — Wave 3 + Pre-Integration
- W1.4 builder returns
- Haiku validation: byte-compare rebuild output to v1.9 hand-crafted HTML
- Orchestrator runs end-to-end smoke test: scrape → score → rebuild

### Day 5 (Friday 2026-05-08) — Wave 4 Integration + Handoff
- **Live production run**: `python -m shaked_wg_agent run --profile default` against real flatfox + Weegee + RonOrp
- Rebuild HTML, deploy to nimrod.bio (WP REST upload)
- File completion bundle:
  - `_COMMUNICATION/team_100/SPRINT_RUN_2026-05-08_v1.0.0.md` (run report)
  - `_COMMUNICATION/team_100/HANDOFF_SWG_W1_TO_TEAM_00_2026-05-08_v1.0.0.md` (delivery)
  - PIPELINE_DASHBOARD updated final state
- Owner (team_00) reviews on 2026-05-08 → accepts / requests fixes

### Buffer policy
- If Day N WP slips, orchestrator may parallelize remaining work using two sonnet sub-agents on Day N+1 to recover
- If by Day 4 EOD ≥1 of W1.1/W1.2/W1.3 still BLOCKED, orchestrator MUST file blocker artifact to team_00 — do NOT silently extend deadline

---

## §6 — Pre-Flight Checklist (Run Before EVERY Dispatch)

Adapted from canonical TikTrack pattern §5 R-2:

1. ✅ This mandate read in full + W1 spec for the WP being dispatched
2. ✅ DB connectivity probe: `cat /Users/nimrod/Documents/agents-os/_aos/db_connectivity_status.json`
   - If `status: online` → API-only mutations (Iron Rule #7)
   - If `status: offline` → STOP and file BLOCKED to team_00 per ADR034 R8
3. ✅ `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL
4. ✅ Required env vars present (`UPRESS_WP_APP_USER=nimrodadmin`, password set, etc.)
5. ✅ Sibling-WP dependencies satisfied per §3 graph
6. ✅ No uncommitted changes in scope-overlapping files (`git status`)
7. ✅ Worktree allocated for parallel waves (orchestrator uses worktrees, sub-agents work in isolation)

If ANY check fails: do NOT dispatch. File BLOCKED artifact and route to team_00.

---

## §7 — Sub-Agent Dispatch Template (Mandatory Format)

```
You are a {sonnet|haiku} sub-agent dispatched by team_100 (W1 sprint orchestrator)
on the shaked-wg-agent AOS spoke. Profile L0. Sprint: SWG-W1-SPRINT.

Your scope is exactly {Phase} for WP {W1.X}.
Read first:
  - This mandate: _COMMUNICATION/team_100/MANDATE_SWG_W1_SPRINT_2026-05-03_v1.0.0.md
  - Your WP spec: §4.{X} of the mandate
  - Existing scaffolding: shaked_wg_agent/scrapers/flatfox.py (reference pattern for connectors)

Hard constraints:
  - DO NOT touch _aos/ except _aos/work_packages/SWG-W1-{X}/ (per AOS_DIRECTORY_CANON Part 5)
  - DO NOT modify other WPs' files
  - DO NOT commit (orchestrator commits after your DONE)
  - DO NOT make policy decisions — file CLARIFICATION artifact and STOP if ambiguous
  - ruff + pytest must pass before you return
  - Polite delay 5-10s between live HTTP requests (respects target sites)

Deliverables:
  - {WP-specific files from §4}
  - Test results summary
  - DONE / PARTIAL / BLOCKED disposition
  - Any deviations from spec, with justification

Return concisely. Total response ≤ 600 lines.
```

**Validator (haiku) prompt extension:**
- Each gate has deterministic VC checklist (file exists? grep matches? test passes?)
- Validator MUST execute each check, not just stamp PASS
- Must produce verdict file at `_COMMUNICATION/team_190/VERDICT_SWG-W1-{X}_{gate}_R1_INTERNAL_v1.0.0.md`
- If any check fails: route_recommendation back to original sonnet builder

---

## §8 — Bookkeeping (Orchestrator Only)

Sub-agents author files but **DO NOT commit**. Orchestrator commits per WP:

| Phase | Commit message |
|---|---|
| Build complete | `feat(SWG-W1-X): {WP title} build` |
| Haiku PASS | `validate(SWG-W1-X): L-GATE_BUILD_R1_INTERNAL PASS` |
| Haiku BLOCKED | `validate(SWG-W1-X): L-GATE_BUILD_R1_INTERNAL BLOCKED — {reason}` |
| Sprint final | `sprint(SWG-W1): completion bundle` |

Orchestrator also maintains:
- `_COMMUNICATION/team_100/SWG-W1-PIPELINE_LOG.md` — running log of every dispatch + return
- `_COMMUNICATION/team_100/SWG-W1-DASHBOARD.md` — single-page status of all 5 WPs

---

## §9 — Definition of Done (Sprint-Level)

- [ ] All 5 WPs (W1.1–W1.5) pass internal haiku validation
- [ ] `pytest` 100% pass on full test suite (no regressions)
- [ ] `ruff check .` clean
- [ ] `bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .` returns 0 FAIL
- [ ] Live production run (Day 5) successfully scrapes flatfox + weegee + ronorp
- [ ] HTML rebuild tool produces valid output bytewise-similar to v1.9 for shared listings
- [ ] Diet/quiet/social extractors detect ≥3 cooking-culture signals across live corpus (vs 2 in v1.9 manual)
- [ ] Bundle handoff artifact filed at `_COMMUNICATION/team_100/HANDOFF_SWG_W1_TO_TEAM_00_2026-05-08_v1.0.0.md`
- [ ] PIPELINE_DASHBOARD final state captured

If any criterion misses by EOD Friday 2026-05-08: orchestrator files BLOCKED-FINAL artifact, owner decides whether to ship partial or extend dev window into weekend.

---

## §10 — Open Questions (Pre-Answered Where Possible)

| Q | A |
|---|---|
| LOD specs required for these WPs? | NO — this is a tactical sprint. WP specs are §4 of this mandate (LOD400-equivalent), not separate LOD200/300/400 docs. |
| External cross-vendor validation? | NO — Owner waived for this 5-day window. Note in handoff bundle so future sprints can backfill if needed. |
| What if Day 5 reveals scraper-side breakage on Weegee/RonOrp? | Orchestrator decides: ship partial bundle if 3/5 WPs PASS, file BLOCKED on the rest. Owner accepts/rejects. |
| Token budget for sonnet+haiku? | Owner approved $30-50/sprint. Orchestrator reports actual usage in completion bundle. |
| Where do new listing fields land in `data/listings.json`? | Schema additions: `full_description: str`, `is_vegetarian_friendly: bool`, `quiet_signals: list[str]`, `social_signals: dict`. Backwards-compatible (extras silently ignored by current loader). |

---

## §11 — Authority Chain Recap

- **team_00 (Owner — Nimrod)** — supreme authority, accepts/rejects bundle
- **team_100 (this mandate's recipient — NEW session)** — owns sprint orchestration end-to-end
- **team_110 (Domain Architect)** — NOT involved in this tactical sprint
- **team_190 (Validator)** — passive recipient of haiku verdict files; no active role unless escalation

team_100 NEW session escalates to team_00 (Owner) on:
- Policy decisions (e.g., scraper unable to comply with robots.txt — escalate)
- Architectural ambiguity not resolvable from §4
- Any WP slipping past Day 4 EOD with no recovery path

---

*END OF MANDATE v1.0.0 — 2026-05-03*
