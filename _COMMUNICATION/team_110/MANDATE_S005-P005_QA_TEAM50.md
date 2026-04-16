# MANDATE — S005-P005 QA Validation: Data Source Expansion

**Assigned to:** Team 50 (QA Validator)
**Authority:** Team 00
**Package:** S005-P005-v1 (3 WPs, 87 ACs)
**Build output:** `_COMMUNICATION/cowork/S005-P005-v1/assets/output/`

---

## YOUR TASK

Validate the Team 200 build output for S005-P005 (Data Source Expansion) against the LOD400 specs. This package contains 3 work packages:

| WP | Title | ACs | Spec |
|----|-------|-----|------|
| WP001 | wgzimmer.ch reCAPTCHA v3 Bypass | 15 | LOD400_S005-P005-WP001.md |
| WP002 | Facebook Manual Listing Parser | 38 | LOD400_S005-P005-WP002.md |
| WP003 | Facebook Email Notification Parser | 34 | LOD400_S005-P005-WP003.md |

Team 110 has already completed an architectural review and fixed all discovered issues (test path bug, missing post_id in WP003 callsite, missing IMAP-specific error catch). 62/62 unit tests pass.

Your role: **independent cross-engine validation** — verify every AC, run all tests, check data integrity, and produce a formal verdict.

---

## INPUT FILES

### Specs (read-only)
- `assets/specs/LOD400_S005-P005-WP001.md` — 15 ACs
- `assets/specs/LOD400_S005-P005-WP002.md` — 38 ACs
- `assets/specs/LOD400_S005-P005-WP003.md` — 34 ACs

### Build Output (under review)
- `assets/output/src/shaked_wg_agent/scrapers/wgzimmer_pw.py` — WP001
- `assets/output/src/shaked_wg_agent/parsers/__init__.py` — WP002
- `assets/output/src/shaked_wg_agent/parsers/llm_listing_parser.py` — WP002
- `assets/output/src/shaked_wg_agent/scrapers/facebook_manual.py` — WP002
- `assets/output/src/shaked_wg_agent/scrapers/facebook_email.py` — WP003
- `assets/output/data/sources.json` — WP002 + WP003
- `assets/output/data/cities/pardes-hanna-region.json` — WP002 + WP003
- `assets/output/data/profiles/pardes-hanna.json` — WP002 + WP003
- `assets/output/data/facebook/pardes-hanna-posts.json` — WP002
- `assets/output/data/facebook/processed_email_ids.json` — WP003
- `assets/output/tests/fixtures/hebrew_posts.json` — WP002
- `assets/output/tests/fixtures/fb_email_single.eml` — WP003
- `assets/output/tests/fixtures/fb_email_digest.eml` — WP003
- `assets/output/tests/fixtures/fb_email_popular.eml` — WP003
- `assets/output/tests/test_facebook_manual.py` — WP002
- `assets/output/tests/test_llm_parser.py` — WP002
- `assets/output/tests/test_facebook_manual_dedup.py` — WP002
- `assets/output/tests/test_facebook_manual_validation.py` — WP002
- `assets/output/tests/test_llm_parser_modes.py` — WP002
- `assets/output/tests/test_facebook_email.py` — WP003

### Reference (original, read-only)
- `assets/src/shaked_wg_agent/scrapers/base.py` — BaseScraper + ScrapedListing

---

## VALIDATION PROTOCOL

### Phase 1: Structural Checks
1. Verify all 25 output files exist
2. Verify file structure matches spec file manifest
3. Verify no files outside spec scope were modified

### Phase 2: WP001 ACs (15 total)
- AC-01/02: Patchright import replaces Playwright import
- AC-03: ImportError guard returns [] and logs warning
- AC-04/05: `launch_persistent_context` replaces `browser.new_context`
- AC-06/07/08: `SHAKED_BROWSER_PROFILE_DIR` env var with default path and makedirs
- AC-09/10: Randomized human-like delays (2+ calls, no fixed values <500ms/>5000ms)
- AC-13/14/15: All parsing methods unchanged (AST comparison of method bodies)

### Phase 3: WP002 ACs (38 total)
- AC-01..07: LLM parser module (imports, config check, parse function, failure modes)
- AC-08..21: ManualFacebookScraper (subclass, pipeline, validation, PII strip, error handling)
- AC-22..26: Source registration (sources.json, city, profile, template file)
- AC-29..31: Test fixtures (>=13 posts, schema compliance, rental/non-rental split)
- AC-33..38: Deduplication (text-hash, cross-source fuzzy, same-source-ID)

### Phase 4: WP003 ACs (34 total)
- AC-01..04: EmailFacebookScraper (subclass, never raises, LLM guard)
- AC-05..10: IMAP handling (env vars only, no literals, error handling)
- AC-11..13: File mode (.eml reading, missing dir, corrupt file handling)
- AC-14..18: Email HTML parsing (single, digest, group name, URL cleaning)
- AC-19..22: Dedup pipeline (message-ID, URL, text-hash, persistence)
- AC-23..26: Output mapping (ILS/IL, source name, PII strip, no author)
- AC-27..31: Source registration (preserves WP002 entries)
- AC-32..34: Fixtures (3 .eml files, parseable, extraction test)

### Phase 5: Cross-WP Integration
- Data files contain BOTH facebook-manual AND facebook-email entries
- WP003 imports from WP002's parser module successfully
- Full pytest suite passes (62 tests, 0 failures expected)

### Phase 6: Security & Compliance
- No hardcoded credentials in any file
- No author_name/PII leaking to output
- phone regex strips Israeli phone numbers from summaries
- IMAP credentials only from env vars

---

## OUTPUT

Produce a verdict document with:
1. **Summary**: PASS / PASS_WITH_FINDINGS / BLOCK
2. **Per-WP AC checklist**: each AC marked PASS/FAIL with evidence
3. **Test results**: pytest output (62 tests expected)
4. **Findings**: any deviations, with severity (CRITICAL/MAJOR/MINOR/INFO)
5. **Cross-WP integration**: data integrity verification

---

## DO NOT

- Modify any output files
- Execute LLM API calls (tests use mocks)
- Run integration tests requiring live IMAP
- Accept Team 110's QA review as substitute — you are the independent validator
- Skip any AC — all 87 must be verified

---

## IRON RULE

The validator engine MUST differ from the builder engine. Team 200 built with Cowork (Cursor Composer). You validate with a different engine. This is non-negotiable.
