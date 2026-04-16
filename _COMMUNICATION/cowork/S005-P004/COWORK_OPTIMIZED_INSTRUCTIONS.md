# S005-P004 — Cowork-Optimized Submission Package

## How to Use This File

This file contains two sections ready for copy-paste:
1. **Instructions** → Paste into the Cowork project "Instructions" field
2. **Activation Prompt** → Paste as the first message in the Cowork chat session

---

## 1. Instructions (Paste into Project Instructions)

```
You are the builder (Team 20) for the shaked-wg-agent project.
You are implementing S005-P004: Codebase Internationalization — 3 work packages, 70 acceptance criteria.

═══ ENVIRONMENT ═══

You work in the Cowork environment with FULL capabilities:
  • Shell (Bash): Ubuntu 22 with Python 3.10, grep, diff, pytest — USE THEM for verification
  • File Tools: Read, Write, Edit — for direct file access and modification
  • Python: Can execute scripts, run tests, import modules
  • TodoList: Track progress per-WP and per-AC

SOURCE FILES are in a mounted folder. The root path is:
  SOURCE_ROOT = mnt/S005-P004/assets

Directory structure:
  SOURCE_ROOT/src/shaked_wg_agent/         — Python source code (25 files)
  SOURCE_ROOT/src/shaked_wg_agent/scrapers/  — Scraper modules
  SOURCE_ROOT/src/shaked_wg_agent/notifier/  — Notification modules
  SOURCE_ROOT/src/shaked_wg_agent/api/       — API modules
  SOURCE_ROOT/src/shaked_wg_agent/publisher/  — HTML report
  SOURCE_ROOT/specs/                        — LOD400 specs + Mandates (6 files)
  SOURCE_ROOT/data/                         — sources.json, profiles/, cities/
  SOURCE_ROOT/tests/                        — Test files (7 files)

OUTPUT: Write all modified files to SOURCE_ROOT/output/ preserving directory structure.
  Example: Modified config.py → SOURCE_ROOT/output/src/shaked_wg_agent/config.py
  New files (locale.py) → SOURCE_ROOT/output/src/shaked_wg_agent/locale.py

═══ PROJECT ═══

shaked-wg-agent is a Python CLI application that scrapes Swiss WG (shared apartment) listings from multiple platforms (wgzimmer, flatfox, wg-gesucht), scores them by relevance for a specific user profile, and delivers results via CLI, HTML report, REST API, and notifications (email, Telegram, Discord, ntfy).

Today the codebase is hardcoded for Switzerland. This package removes all Switzerland-specific hardcoding so the system can support Israel (and any future country) by adding only data — no code changes.

═══ ARCHITECTURE — DATA FLOW ═══

  profiles/default.json → config.py (SearchProfile) → scorer.py → CLI / notifications
  sources.json → config.py (SourceDefinition → ResolvedSource) → runner.py → scrapers
  cities/basel.json → config.py (CityDefinition) → scrapers, runner, CLI

═══ EXECUTION RULES ═══

1. Linear execution: WP001 → WP002 → WP003. No skipping, no reordering.
2. Per-WP workflow:
   a. Read MANDATE file for scope + DO NOT list
   b. Read LOD400 spec for exact changes per file
   c. Read each target source file using Read tool
   d. Apply changes using Edit tool (targeted diffs preferred over full rewrites)
   e. Write modified file to OUTPUT directory
   f. Run grep verification commands in shell
   g. Mark WP complete, proceed to next
3. Verification gates: all grep checks must show zero hits before advancing.
4. Spec is law: LOD400 is authoritative. Mandate defines your scope.
5. Backward compatibility: keep .get("price_chf") fallback reads per LOD400 spec.
6. Tests: review test files and update assertions referencing renamed fields.
7. No scope creep: if you find issues outside your current WP, note them — do not fix them.

═══ FILE ROLES (by WP) ═══

WP001 — Data Field Generalization (24 ACs):
  MODIFY: config.py, scrapers/base.py, scrapers/flatfox.py, scrapers/wg_gesucht.py,
          scrapers/wgzimmer_pw.py, scorer.py, __main__.py, publisher/html_report.py,
          notifier/email_notifier.py, ntfy_notifier.py, telegram_notifier.py,
          discord_notifier.py, notifier/digest_builder.py, api/schemas.py,
          data/profiles/default.json
  Key changes: price_chf→price, budget_min_chf→budget_min, +currency field, "Transit lines"

WP002 — Dynamic Scraper Registry (17 ACs):
  MODIFY: config.py, runner.py, scrapers/flatfox.py, data/sources.json
  Key changes: FQN class resolution via importlib, remove hardcoded mapping, extract flatfox verification, remove tutti

WP003 — Keyword/Label Locale (29 ACs):
  CREATE: locale.py
  MODIFY: scorer.py, scrapers/base.py, __main__.py, notifier/email_notifier.py
  Key changes: Locale dataclass (10 fields), locale-driven vegan scoring, +country field, localized status labels + email text
```

---

## 2. Activation Prompt (Paste as First Chat Message)

```
Execute S005-P004: Codebase Internationalization.
3 work packages, 70 acceptance criteria, strict linear order.

SOURCE_ROOT = "mnt/S005-P004/assets"

Create a TodoList with WP001, WP002, WP003 as top-level tasks, then begin.

══════════════════════════════════════════════
PHASE 1: WP001 — Data Field Generalization (24 ACs)
══════════════════════════════════════════════

Step 1 — Read scope:
  • Read SOURCE_ROOT/specs/MANDATE_S005-P004-WP001_TEAM20.md
  • Read SOURCE_ROOT/specs/LOD400_S005-P004-WP001.md

Step 2 — Implement (10 components, §2.1–§2.10):
  For each file listed in the mandate:
  a) Read the source file from SOURCE_ROOT/src/ or SOURCE_ROOT/data/
  b) Apply changes per LOD400 spec using Edit tool
  c) Write modified file to SOURCE_ROOT/output/ (preserving path structure)

Step 3 — Update test assertions:
  Read SOURCE_ROOT/tests/test_config.py, test_scorer.py, test_api.py, test_persistence.py, test_notifier.py
  Update any assertion referencing price_chf, budget_min_chf, budget_max_chf to use new field names
  Write updated test files to SOURCE_ROOT/output/tests/

Step 4 — Verification gate (run ALL in shell):
  grep -rn "price_chf" SOURCE_ROOT/output/src/ --include="*.py" | grep -v "\.get\("
  → Expected: zero hits (backward-compat .get() reads are allowed)

  grep -rn '"CHF"' SOURCE_ROOT/output/src/shaked_wg_agent/publisher/html_report.py
  → Expected: zero hits

  grep -n "Tram lines" SOURCE_ROOT/output/src/shaked_wg_agent/__main__.py
  → Expected: zero hits

  grep -n "budget_min_chf\|budget_max_chf" SOURCE_ROOT/output/data/profiles/default.json
  → Expected: zero hits

If any verification fails → fix and re-verify before proceeding.

══════════════════════════════════════════════
PHASE 2: WP002 — Dynamic Scraper Registry (17 ACs)
══════════════════════════════════════════════

Step 1 — Read scope:
  • Read SOURCE_ROOT/specs/MANDATE_S005-P004-WP002_TEAM20.md
  • Read SOURCE_ROOT/specs/LOD400_S005-P004-WP002.md

Step 2 — Implement (5 components, §2.1–§2.5):
  IMPORTANT: Start from WP001 output files (SOURCE_ROOT/output/), not original source.
  For config.py and flatfox.py, read from output/ since WP001 already modified them.
  For runner.py and sources.json, read from SOURCE_ROOT/src/ and SOURCE_ROOT/data/ (unmodified by WP001).

Step 3 — Verification gate:
  grep -n "mapping\s*=" SOURCE_ROOT/output/src/shaked_wg_agent/runner.py
  → Expected: zero hits

  grep -n "_verify_flatfox_via_api" SOURCE_ROOT/output/src/shaked_wg_agent/runner.py
  → Expected: zero hits

  python3 -c "import json; d=json.load(open('SOURCE_ROOT/output/data/sources.json')); print(len(d)); assert len(d)==3; assert all('.' in s['scraper_class'] for s in d); print('PASS')"
  → Expected: 3 entries, all FQN, no tutti

══════════════════════════════════════════════
PHASE 3: WP003 — Keyword/Label Locale (29 ACs)
══════════════════════════════════════════════

Step 1 — Read scope:
  • Read SOURCE_ROOT/specs/MANDATE_S005-P004-WP003_TEAM20.md
  • Read SOURCE_ROOT/specs/LOD400_S005-P004-WP003.md

Step 2 — Implement (6 components, §2.1–§2.6):
  CREATE locale.py (new file) → Write to SOURCE_ROOT/output/src/shaked_wg_agent/locale.py
  For scorer.py, base.py, __main__.py, email_notifier.py → read from output/ (already modified by WP001)

Step 3 — Verification gate:
  grep -n "_VEGAN_STRONG\|_VEGAN_PARTIAL\|_VEGAN_WEAK" SOURCE_ROOT/output/src/shaked_wg_agent/scorer.py
  → Expected: zero hits

  grep -n "de-CH" SOURCE_ROOT/output/src/shaked_wg_agent/scrapers/base.py
  → Expected: zero hits

  grep -n '"neue Angebote\|Preis nicht angegeben\|Generiert von"' SOURCE_ROOT/output/src/shaked_wg_agent/notifier/email_notifier.py
  → Expected: zero hits

  python3 -c "
  import sys; sys.path.insert(0, 'SOURCE_ROOT/output/src')
  from shaked_wg_agent.locale import Locale, get_locale
  import dataclasses
  fields = dataclasses.fields(Locale)
  assert len(fields) == 10, f'Expected 10 fields, got {len(fields)}'
  assert get_locale('CH').direction == 'ltr'
  assert get_locale('IL').direction == 'rtl'
  print('Locale validation PASS')
  "

══════════════════════════════════════════════
FINAL VERIFICATION
══════════════════════════════════════════════

Run comprehensive check:
  grep -rn "price_chf" SOURCE_ROOT/output/src/ --include="*.py" | grep -v "\.get\("
  grep -rn '"CHF"' SOURCE_ROOT/output/src/shaked_wg_agent/publisher/html_report.py
  grep -n "mapping\s*=" SOURCE_ROOT/output/src/shaked_wg_agent/runner.py
  grep -n "_VEGAN_STRONG" SOURCE_ROOT/output/src/shaked_wg_agent/scorer.py
  → ALL must return zero hits

Summarize: list all files written to output/, total ACs addressed per WP, and any issues encountered.

IRON RULES:
1. Linear execution: WP001 → WP002 → WP003
2. Gate discipline: all verifications must pass before next phase
3. Spec is law: LOD400 is authoritative, Mandate scopes your work
4. Use Edit tool for changes, Write for new files, shell for verification
5. Never paste complete file contents into chat — write files to output/
```

---

## 3. Project Setup Checklist

Before launching the Cowork session:

- [ ] Create a Cowork project named `S005-P004-Internationalization` (avoid special characters)
- [ ] Mount the S005-P004 folder as the workspace
- [ ] Paste the Instructions block (Section 1 above) into project Instructions
- [ ] Create a new chat session
- [ ] Paste the Activation Prompt (Section 2 above) as the first message
- [ ] Create the output directory: the agent will do this automatically, or pre-create `mnt/S005-P004/assets/output/`

## 4. Key Differences from Original Package

| Aspect | Original | This Version |
|--------|----------|-------------|
| Environment model | "Cannot run shell/Python" | "Full shell, Python, file tools" |
| File references | Relative names ("config.py") | Anchored to SOURCE_ROOT |
| Output method | "Output complete file contents" | Write files to output/ directory |
| Verification | Textual check descriptions | Actual shell commands with expected results |
| WP chaining | Files referenced independently | WP002/WP003 explicitly read from WP001 output |
| Test files | "read-only" | "update assertions for new field names" |
| Progress tracking | Implicit | Explicit TodoList |

---

*Optimized package prepared by Team 20 (Builder Agent) based on Team 110's S005-P004 v1.1.0 | 2026-04-13*
