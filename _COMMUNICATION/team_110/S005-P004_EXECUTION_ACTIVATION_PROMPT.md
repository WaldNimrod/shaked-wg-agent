# S005-P004 Execution Activation — Linear Mandate with Validation Gates

**Drafted by:** Team 110 (shaked_arch / Claude Code)
**Authority:** Team 00 (Nimrod)
**Date:** 2026-04-12
**Decision ref:** R-OPS-2 (COWORK_EVALUATION_DECISION.md)
**Execution model:** Single Claude Code session, serial mandate execution

---

## Activation Prompt for Builder (Team 20 / Cursor Composer)

You are **Team 20** (shaked_build), the builder for the **shaked-wg-agent** project. Your engine is Cursor Composer.

**Task:** Implement 3 work packages for S005-P004 (Codebase Internationalization) in **strict linear order** with per-WP validation gates and a final comprehensive validation. You MUST NOT proceed to the next WP until the current WP passes all validation checks.

---

## Execution Discipline (Field Experience — Team 00 Directive)

**CRITICAL — LINEAR EXECUTION WITH VALIDATION GATES:**

This is a serial pipeline. WP001 renames fields consumed by WP002 and WP003. WP002 changes scraper instantiation consumed by WP003. Parallel execution would cause merge conflicts, inconsistent state, and cascading failures where WP2 builds on broken WP1 output.

**The rule:** Implement WP → run ALL validation checks → PASS = proceed / FAIL = fix before proceeding. Never skip a gate. Never start the next WP before the current one passes.

---

## Phase 1: WP001 — Data Field Generalization

### Read your mandate
```
_COMMUNICATION/team_20/MANDATE_S005-P004-WP001_TEAM20.md
```

### Read the LOD400 spec (primary — follow exactly)
```
_aos/work_packages/S005-P004-WP001/LOD400_S005-P004-WP001.md
```

### Implement
Execute all 10 components (§2.1–§2.10) per the LOD400 spec. 24 acceptance criteria.

### VALIDATION GATE 1 — must ALL pass before proceeding

```bash
# 1. All tests pass
pytest tests/ -v

# 2. No legacy field definitions/assignments
grep -ri "price_chf" shaked_wg_agent/ --include="*.py" | grep -v "\.get(" | grep -v "# "
# Expected: zero hits (backward-compat .get() reads are allowed)

grep -ri "budget_min_chf\|budget_max_chf" shaked_wg_agent/ --include="*.py" | grep -v "\.get(" | grep -v "# "
# Expected: zero hits

# 3. No hardcoded CHF in consumer rendering code
grep -i '"CHF"' shaked_wg_agent/publisher/html_report.py
# Expected: zero hits

grep -i '"CHF"' shaked_wg_agent/__main__.py
# Expected: zero hits in display strings (dataclass defaults allowed)

# 4. Data file updated
grep "budget_min_chf\|budget_max_chf" data/profiles/default.json
# Expected: zero hits

# 5. Transit label
grep -i "tram lines" shaked_wg_agent/__main__.py
# Expected: zero hits
```

**GATE 1 RESULT:** ALL pass → proceed to Phase 2. ANY fail → fix and re-validate. Do NOT proceed.

---

## Phase 2: WP002 — Dynamic Scraper Registry

### Read your mandate
```
_COMMUNICATION/team_20/MANDATE_S005-P004-WP002_TEAM20.md
```

### Read the LOD400 spec (primary — follow exactly)
```
_aos/work_packages/S005-P004-WP002/LOD400_S005-P004-WP002.md
```

### Implement
Execute all 5 components (§2.1–§2.5) per the LOD400 spec. 17 acceptance criteria.

### VALIDATION GATE 2 — must ALL pass before proceeding

```bash
# 1. All tests pass
pytest tests/ -v

# 2. No hardcoded mapping
grep -n "mapping\s*=" shaked_wg_agent/runner.py
# Expected: zero hits

# 3. Flatfox verification extracted
grep -n "_verify_flatfox_via_api" shaked_wg_agent/runner.py
# Expected: zero hits

# 4. FQN in sources.json (all entries have dots in scraper_class)
python3 -c "
import json
with open('data/sources.json') as f:
    sources = json.load(f)
for s in sources:
    sc = s.get('scraper_class', '')
    assert '.' in sc, f'Not FQN: {sc}'
    print(f'OK: {sc}')
# Also verify tutti is gone
assert not any(s.get('source_id') == 'tutti' for s in sources), 'tutti still present'
print('tutti removed: OK')
"

# 5. Verify each FQN resolves
python3 -c "
import json, importlib
with open('data/sources.json') as f:
    sources = json.load(f)
for s in sources:
    fqn = s['scraper_class']
    mod_path, _, cls_name = fqn.rpartition('.')
    mod = importlib.import_module(mod_path)
    cls = getattr(mod, cls_name)
    print(f'Resolved: {fqn} -> {cls}')
print('All FQNs resolve: OK')
"
```

**GATE 2 RESULT:** ALL pass → proceed to Phase 3. ANY fail → fix and re-validate. Do NOT proceed.

---

## Phase 3: WP003 — Keyword and Label Locale Generalization

### Read your mandate
```
_COMMUNICATION/team_20/MANDATE_S005-P004-WP003_TEAM20.md
```

### Read the LOD400 spec (primary — follow exactly)
```
_aos/work_packages/S005-P004-WP003/LOD400_S005-P004-WP003.md
```

### Implement
Execute all 6 components (§2.1–§2.6) per the LOD400 spec. 29 acceptance criteria.

### VALIDATION GATE 3 — must ALL pass before proceeding

```bash
# 1. All tests pass
pytest tests/ -v

# 2. No hardcoded vegan keywords in scorer
grep -n "_VEGAN_STRONG\|_VEGAN_PARTIAL\|_VEGAN_WEAK" shaked_wg_agent/scorer.py
# Expected: zero hits

# 3. No hardcoded Accept-Language
grep -n "de-CH" shaked_wg_agent/scrapers/base.py
# Expected: zero hits

# 4. No hardcoded German email strings
grep -n '"neue Angebote\|Preis nicht angegeben\|Generiert von"' shaked_wg_agent/notifier/email_notifier.py
# Expected: zero hits

# 5. Locale module integrity
python3 -c "
from shaked_wg_agent.locale import Locale, get_locale, get_email_strings
import dataclasses
# Exactly 10 fields
assert len(dataclasses.fields(Locale)) == 10, f'Expected 10 fields, got {len(dataclasses.fields(Locale))}'
print('Locale fields: 10 OK')
# CH locale
ch = get_locale('CH')
assert ch.direction == 'ltr'
assert ch.html_lang == 'de'
assert 'vegan' in ch.vegan_strong
print('CH locale: OK')
# IL locale
il = get_locale('IL')
assert il.direction == 'rtl'
assert il.html_lang == 'he'
assert 'טבעוני' in il.vegan_strong
assert il.currency_symbol == '₪'
print('IL locale: OK')
# Fallback
assert get_locale('XX') == get_locale('CH')
print('Fallback: OK')
# Email strings separate
es_ch = get_email_strings('CH')
assert es_ch['new_offers'] == 'neue Angebote'
es_il = get_email_strings('IL')
assert es_il['new_offers'] == 'הצעות חדשות'
print('Email strings: OK')
"
```

**GATE 3 RESULT:** ALL pass → proceed to Final Validation. ANY fail → fix and re-validate. Do NOT proceed.

---

## Phase 4: Final Comprehensive Validation

**This gate validates ALL 3 WPs together.** It catches cross-WP regressions that per-WP gates cannot detect.

```bash
# 1. FULL test suite — all tests, all WPs
pytest tests/ -v --tb=long

# 2. Cross-WP: zero legacy fields anywhere
grep -ri "price_chf" shaked_wg_agent/ --include="*.py" | grep -v "\.get(" | grep -v "# "
# Expected: zero hits

grep -ri "budget_min_chf\|budget_max_chf" shaked_wg_agent/ --include="*.py" | grep -v "\.get(" | grep -v "# "
# Expected: zero hits

# 3. Cross-WP: renamed fields used consistently
python3 -c "
from shaked_wg_agent.scrapers.base import ScrapedListing
import dataclasses
fields = {f.name for f in dataclasses.fields(ScrapedListing)}
assert 'price' in fields, 'Missing price field'
assert 'currency' in fields, 'Missing currency field'
assert 'country' in fields, 'Missing country field'
assert 'price_chf' not in fields, 'Legacy price_chf still present'
print(f'ScrapedListing fields: {sorted(fields)}')
print('Cross-WP field consistency: OK')
"

# 4. Cross-WP: scraper registry works with locale
python3 -c "
import json, importlib
from shaked_wg_agent.scrapers.base import BaseScraper
with open('data/sources.json') as f:
    sources = json.load(f)
for s in sources:
    fqn = s['scraper_class']
    mod_path, _, cls_name = fqn.rpartition('.')
    mod = importlib.import_module(mod_path)
    cls = getattr(mod, cls_name)
    assert issubclass(cls, BaseScraper), f'{cls} not a BaseScraper subclass'
    print(f'{fqn}: OK (BaseScraper subclass)')
print('Registry + BaseScraper: OK')
"

# 5. Cross-WP: locale integration with scorer
python3 -c "
from shaked_wg_agent.locale import get_locale
ch = get_locale('CH')
il = get_locale('IL')
# Verify vegan keywords are frozensets (immutable)
assert isinstance(ch.vegan_strong, frozenset)
assert isinstance(il.vegan_strong, frozenset)
# Verify scoring dimensions exist
assert len(ch.vegan_strong) == 6
assert len(il.vegan_strong) == 4
print('Locale-scorer integration: OK')
"

# 6. Linter clean
ruff check shaked_wg_agent/
# Expected: no errors (or only pre-existing ones)

# 7. Data files consistent
python3 -c "
import json
# sources.json: no tutti, all FQN
with open('data/sources.json') as f:
    sources = json.load(f)
assert not any(s.get('source_id') == 'tutti' for s in sources)
for s in sources:
    assert '.' in s['scraper_class']
print(f'sources.json: {len(sources)} entries, all FQN, no tutti')
# profiles/default.json: new field names
with open('data/profiles/default.json') as f:
    profile = json.load(f)
assert 'budget_min' in profile, 'Missing budget_min'
assert 'budget_max' in profile, 'Missing budget_max'
assert 'budget_min_chf' not in profile, 'Legacy budget_min_chf still present'
print(f'default.json: budget_min={profile[\"budget_min\"]}, budget_max={profile[\"budget_max\"]}')
"
```

**FINAL GATE RESULT:**
- ALL pass → **COMPLETE.** Implementation is done. File completion report.
- ANY fail → Fix the specific failure. Re-run the FULL final validation (not just the failed check).

---

## Completion

When final validation passes, create:
```
_COMMUNICATION/team_20/COMPLETE_S005-P004.md
```

With:
- List of all files modified/created
- All 3 WP gate results (PASS)
- Final comprehensive validation result (PASS)
- Any notes or deviations from spec (should be none)

---

## Iron Rules (binding on this execution)

1. **Linear execution.** WP001 → WP002 → WP003. No parallel, no reordering.
2. **Gate discipline.** Every gate must pass before proceeding. No skipping, no "I'll fix it later."
3. **Spec is law.** The LOD400 is the authoritative spec. The mandate scopes your work. Do not add features, refactor beyond scope, or make design decisions not in the spec.
4. **File discipline.** Only modify files listed in your mandate deliverables. Do not touch files outside scope.
5. **Test discipline.** `pytest tests/ -v` must exit 0 at every gate. Broken tests = HALT.
6. **No scope creep.** If you encounter something that seems wrong but is outside your WP scope, note it in the completion report — do not fix it.

---

*Activation prompt drafted by Team 110 (shaked_arch / Claude Code) on authority of Team 00 (Nimrod) | shaked-wg-agent | S005-P004 Phase 4C | 2026-04-12*
