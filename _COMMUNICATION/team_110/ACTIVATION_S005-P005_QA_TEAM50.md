# S005-P005 QA Activation — Team 50

You are Team 50 (QA Validator) for the shaked-wg-agent project.
Validate the Team 200 build output for S005-P005 (Data Source Expansion) — 3 work packages, 87 acceptance criteria.

## Setup

```bash
cd _COMMUNICATION/cowork/S005-P005-v1/assets
export SOURCE_ROOT="."
```

---

## PHASE 1: Structural Verification

Verify all output files exist:

```bash
echo "=== File Manifest Check ==="
files=(
  "output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py"
  "output/src/shaked_wg_agent/parsers/__init__.py"
  "output/src/shaked_wg_agent/parsers/llm_listing_parser.py"
  "output/src/shaked_wg_agent/scrapers/facebook_manual.py"
  "output/src/shaked_wg_agent/scrapers/facebook_email.py"
  "output/data/sources.json"
  "output/data/cities/pardes-hanna-region.json"
  "output/data/profiles/pardes-hanna.json"
  "output/data/facebook/pardes-hanna-posts.json"
  "output/data/facebook/processed_email_ids.json"
  "output/tests/fixtures/hebrew_posts.json"
  "output/tests/fixtures/fb_email_single.eml"
  "output/tests/fixtures/fb_email_digest.eml"
  "output/tests/fixtures/fb_email_popular.eml"
  "output/tests/test_facebook_manual.py"
  "output/tests/test_llm_parser.py"
  "output/tests/test_facebook_manual_dedup.py"
  "output/tests/test_facebook_manual_validation.py"
  "output/tests/test_llm_parser_modes.py"
  "output/tests/test_facebook_email.py"
)
pass=0; fail=0
for f in "${files[@]}"; do
  if [ -f "$f" ]; then ((pass++)); else echo "MISSING: $f"; ((fail++)); fi
done
echo "Files: $pass present, $fail missing"
```

---

## PHASE 2: WP001 — reCAPTCHA v3 Bypass (15 ACs)

Read the spec first:
```
Read specs/LOD400_S005-P005-WP001.md
Read output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py
Read src/shaked_wg_agent/scrapers/wgzimmer_pw.py  (original for diff)
```

Run AC checks:
```bash
# AC-01: Patchright import
grep -q "from patchright.sync_api import sync_playwright" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py && echo "AC-01 PASS" || echo "AC-01 FAIL"

# AC-02: No playwright import
grep -c "from playwright.sync_api" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py | grep -q "^0$" && echo "AC-02 PASS" || echo "AC-02 FAIL"

# AC-03: ImportError guard
grep -q "_HAS_PATCHRIGHT" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py && echo "AC-03 PASS" || echo "AC-03 FAIL"

# AC-04: launch_persistent_context
grep -q "launch_persistent_context" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py && echo "AC-04 PASS" || echo "AC-04 FAIL"

# AC-05: No browser.new_context
grep -c "browser.new_context\|pw.chromium.launch(" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py | grep -q "^0$" && echo "AC-05 PASS" || echo "AC-05 FAIL"

# AC-06: SHAKED_BROWSER_PROFILE_DIR env var
grep -q "SHAKED_BROWSER_PROFILE_DIR" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py && echo "AC-06 PASS" || echo "AC-06 FAIL"

# AC-07: Default profile path
grep -q "~/.shaked-wg/browser-profile/wgzimmer" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py && echo "AC-07 PASS" || echo "AC-07 FAIL"

# AC-08: makedirs with exist_ok
grep -q "os.makedirs.*exist_ok=True" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py && echo "AC-08 PASS" || echo "AC-08 FAIL"

# AC-09: Human-like delays (>=2 random.randint calls)
count=$(grep -c "wait_for_timeout(random.randint(" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py)
[ "$count" -ge 2 ] && echo "AC-09 PASS (count=$count)" || echo "AC-09 FAIL (count=$count)"

# AC-10: No fixed extreme timeouts
grep -cP "wait_for_timeout\(\d+\)" output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py | head -1
echo "AC-10: manually verify no fixed values <500ms or >5000ms"
```

Verify parsing methods unchanged (AST):
```bash
python3 -c "
import ast
with open('output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'Wgzimmer' in node.name:
        methods = sorted([n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))])
        print(f'Methods found: {methods}')
        required = ['_allowed_zips','_detect_vegan','_dom_fallback','_parse_api_item','_wg_path_segment','fetch_listings']
        for m in required:
            assert m in methods, f'Missing method: {m}'
        print('AC-13/14/15 structure PASS')
        break
"
```

Verify error handling:
```bash
python3 -c "
import ast
with open('output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'fetch_listings':
        # Check for try/except at top level of method
        for child in node.body:
            if isinstance(child, ast.Try):
                for handler in child.handlers:
                    if handler.type and hasattr(handler.type, 'id') and handler.type.id == 'Exception':
                        print('fetch_listings has top-level try/except Exception — PASS')
                        break
        break
"
```

---

## PHASE 3: WP002 — Facebook Manual Parser (38 ACs)

Read the spec:
```
Read specs/LOD400_S005-P005-WP002.md
Read output/src/shaked_wg_agent/parsers/llm_listing_parser.py
Read output/src/shaked_wg_agent/scrapers/facebook_manual.py
```

Run AC checks:
```bash
# AC-01: Parser module imports
PYTHONPATH="output/src:src" python3 -c "
from shaked_wg_agent.parsers.llm_listing_parser import parse_rental_post, check_llm_config
assert callable(parse_rental_post)
assert callable(check_llm_config)
print('AC-01 PASS')
"

# AC-02: check_llm_config behavior
PYTHONPATH="output/src:src" python3 -c "
import os
os.environ.pop('SHAKED_LLM_PROVIDER', None)
os.environ.pop('ANTHROPIC_API_KEY', None)
# Need to reimport after env change — but module-level vars cached
# Just verify function signature
from shaked_wg_agent.parsers.llm_listing_parser import check_llm_config
print(f'AC-02: check_llm_config is callable, returns {type(check_llm_config()).__name__}')
"

# AC-08/09: ManualFacebookScraper
PYTHONPATH="output/src:src" python3 -c "
from shaked_wg_agent.scrapers.facebook_manual import ManualFacebookScraper
from shaked_wg_agent.scrapers.base import BaseScraper
assert issubclass(ManualFacebookScraper, BaseScraper)
print('AC-08/09 PASS')
"

# AC-22..26: Source registration
python3 -c "
import json
s = json.load(open('output/data/sources.json'))
fb = [x for x in s if x['source_id'] == 'facebook-manual']
assert len(fb) == 1, 'AC-22 FAIL'
assert '.' in fb[0]['scraper_class'], 'AC-22 FAIL (not FQN)'
print('AC-22 PASS')

c = json.load(open('output/data/cities/pardes-hanna-region.json'))
assert 'facebook-manual' in c['available_sources'], 'AC-23 FAIL'
print('AC-23 PASS')

p = json.load(open('output/data/profiles/pardes-hanna.json'))
assert 'facebook-manual' in p['enabled_sources'], 'AC-24 FAIL'
print('AC-24 PASS')

t = json.load(open('output/data/facebook/pardes-hanna-posts.json'))
assert t == [], 'AC-25 FAIL'
print('AC-25 PASS')
"

# AC-29..31: Fixtures
python3 -c "
import json
posts = json.load(open('output/tests/fixtures/hebrew_posts.json'))
assert len(posts) >= 13, f'AC-29 FAIL: {len(posts)}'
print(f'AC-29 PASS: {len(posts)} posts')
assert all('post_id' in p and 'text' in p for p in posts), 'AC-30 FAIL'
print('AC-30 PASS')
# Count rental vs non-rental (heuristic)
non_rental_kw = ['מחפש', 'מישהו', 'למכירה']
rentals = sum(1 for p in posts if not any(k in p['text'] for k in non_rental_kw))
non_rentals = len(posts) - rentals
assert rentals >= 10 and non_rentals >= 3, f'AC-31 FAIL: {rentals} rental, {non_rentals} non-rental'
print(f'AC-31 PASS: {rentals} rental, {non_rentals} non-rental')
"

# AC-14: PII check — verify phone regex exists
grep -q "PHONE_PATTERN" output/src/shaked_wg_agent/scrapers/facebook_manual.py && echo "AC-14 regex PASS" || echo "AC-14 FAIL"
grep -q "phone removed" output/src/shaked_wg_agent/scrapers/facebook_manual.py && echo "AC-14 strip PASS" || echo "AC-14 FAIL"

# AC-15: author_name never in output
grep -q "author_name" output/src/shaked_wg_agent/scrapers/facebook_manual.py
echo "AC-15: verify _to_scraped_listing never uses author_name (manual check)"

# Dedup checks
grep -q "_is_duplicate" output/src/shaked_wg_agent/scrapers/facebook_manual.py && echo "AC-35/36 dedup method PASS" || echo "FAIL"
grep -q "sha256" output/src/shaked_wg_agent/scrapers/facebook_manual.py && echo "AC-34 text-hash PASS" || echo "FAIL"
```

---

## PHASE 4: WP003 — Facebook Email Parser (34 ACs)

Read the spec:
```
Read specs/LOD400_S005-P005-WP003.md
Read output/src/shaked_wg_agent/scrapers/facebook_email.py
```

Run AC checks:
```bash
# AC-01/02: EmailFacebookScraper
PYTHONPATH="output/src:src" python3 -c "
from shaked_wg_agent.scrapers.facebook_email import EmailFacebookScraper
from shaked_wg_agent.scrapers.base import BaseScraper
assert issubclass(EmailFacebookScraper, BaseScraper)
print('AC-01/02 PASS')
"

# AC-07/08: No credential literals
python3 -c "
with open('output/src/shaked_wg_agent/scrapers/facebook_email.py') as f:
    content = f.read()
# Check no hardcoded passwords
import re
# Should only have env var reads
lines = [l for l in content.split('\n') if 'password' in l.lower() or 'PASS' in l]
for l in lines:
    print(f'  Credential ref: {l.strip()}')
print('AC-07/08: verify no literal credentials above')
"

# AC-27..31: Source registration (preserves WP002)
python3 -c "
import json
s = json.load(open('output/data/sources.json'))
ids = [x['source_id'] for x in s]
assert 'facebook-email' in ids, 'AC-27 FAIL'
assert 'facebook-manual' in ids, 'WP002 entry lost!'
print('AC-27 PASS')

c = json.load(open('output/data/cities/pardes-hanna-region.json'))
assert 'facebook-email' in c['available_sources'], 'AC-28 FAIL'
assert 'facebook-manual' in c['available_sources'], 'WP002 entry lost!'
print('AC-28 PASS')

p = json.load(open('output/data/profiles/pardes-hanna.json'))
assert 'facebook-email' in p['enabled_sources'], 'AC-29 FAIL'
assert 'facebook-manual' in p['enabled_sources'], 'WP002 entry lost!'
print('AC-29 PASS')

e = json.load(open('output/data/facebook/processed_email_ids.json'))
print(f'AC-30 PASS: processed_email_ids.json = {e}')
"

# AC-32..34: .eml fixtures
python3 -c "
import email
for f in ['fb_email_single.eml', 'fb_email_digest.eml', 'fb_email_popular.eml']:
    with open(f'output/tests/fixtures/{f}', 'rb') as fh:
        msg = email.message_from_bytes(fh.read())
    assert msg.get('From'), f'{f}: no From'
    assert msg.get('Subject'), f'{f}: no Subject'
    assert msg.get('Message-ID'), f'{f}: no Message-ID'
    print(f'AC-32 {f}: PASS')
print('AC-33 PASS: all parseable')
"

# AC-34: Parse extraction test
PYTHONPATH="output/src:src" python3 -c "
import email
from shaked_wg_agent.scrapers.facebook_email import EmailFacebookScraper
from unittest.mock import MagicMock

city = MagicMock()
city.currency = 'ILS'
city.country = 'IL'
scraper = EmailFacebookScraper('facebook-email', 'test', city)

# Single post
with open('output/tests/fixtures/fb_email_single.eml', 'rb') as f:
    msg = email.message_from_bytes(f.read())
html = ''
if msg.is_multipart():
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            html = part.get_payload(decode=True).decode('utf-8', errors='replace')
else:
    html = msg.get_payload(decode=True).decode('utf-8', errors='replace')
snippets = scraper._parse_email_html(html, msg.get('Subject', ''))
assert len(snippets) >= 1, f'Single: expected >=1, got {len(snippets)}'
print(f'AC-34 single: {len(snippets)} snippet(s) PASS')

# Digest
with open('output/tests/fixtures/fb_email_digest.eml', 'rb') as f:
    msg = email.message_from_bytes(f.read())
html = msg.get_payload(decode=True).decode('utf-8', errors='replace')
snippets = scraper._parse_email_html(html, msg.get('Subject', ''))
assert len(snippets) >= 2, f'Digest: expected >=2, got {len(snippets)}'
print(f'AC-34 digest: {len(snippets)} snippet(s) PASS')
"
```

---

## PHASE 5: Test Suite

Run the complete test suite:
```bash
PYTHONPATH="output/src:src" python3 -m pytest output/tests/ -v --tb=short
```

Expected: **62 tests, 0 failures**.

---

## PHASE 6: Final Cross-WP Integration

```bash
PYTHONPATH="output/src:src" python3 -c "
# Full integration check
from shaked_wg_agent.parsers.llm_listing_parser import parse_rental_post, check_llm_config
from shaked_wg_agent.scrapers.facebook_manual import ManualFacebookScraper
from shaked_wg_agent.scrapers.facebook_email import EmailFacebookScraper
from shaked_wg_agent.scrapers.base import BaseScraper
import json

# Class hierarchy
assert issubclass(ManualFacebookScraper, BaseScraper)
assert issubclass(EmailFacebookScraper, BaseScraper)

# Data integrity
s = json.load(open('output/data/sources.json'))
ids = sorted([x['source_id'] for x in s])
assert 'facebook-email' in ids and 'facebook-manual' in ids

c = json.load(open('output/data/cities/pardes-hanna-region.json'))
assert 'facebook-manual' in c['available_sources']
assert 'facebook-email' in c['available_sources']

p = json.load(open('output/data/profiles/pardes-hanna.json'))
assert 'facebook-manual' in p['enabled_sources']
assert 'facebook-email' in p['enabled_sources']

# WP001 patchright
with open('output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py') as f:
    wg = f.read()
assert 'from patchright.sync_api' in wg
assert 'from playwright.sync_api' not in wg
assert 'launch_persistent_context' in wg

print('=== FINAL INTEGRATION: ALL PASS ===')
print(f'Sources registered: {ids}')
print('WP001: Patchright + persistent context OK')
print('WP002: ManualFacebookScraper + parsers OK')
print('WP003: EmailFacebookScraper + data preserved OK')
"
```

---

## VERDICT FORMAT

Produce your verdict as:

```markdown
# VERDICT — S005-P005 QA Validation

**Verdict:** PASS / PASS_WITH_FINDINGS / BLOCK
**Date:** YYYY-MM-DD
**Validator:** Team 50
**Engine:** [your engine name]

## Summary
[1-3 sentences]

## AC Checklist

### WP001 (15 ACs)
- AC-01: PASS/FAIL — [evidence]
...

### WP002 (38 ACs)
- AC-01: PASS/FAIL — [evidence]
...

### WP003 (34 ACs)
- AC-01: PASS/FAIL — [evidence]
...

## Test Results
[pytest output summary]

## Findings
[F-QA-NNN severity descriptions if any]

## Cross-WP Integration
[Data integrity check results]
```

Write the verdict to: `_COMMUNICATION/team_50/VERDICT_S005-P005_QA.md`
