# MANDATE — S005-P005-WP003: Facebook Email Notification Parser

**Assigned to:** Team 20 (Builder)
**Authority:** Team 00

## YOUR TASK

Create an EmailFacebookScraper that reads Facebook group notification emails via IMAP, extracts listing posts, reuses the WP002 LLM parser for structured Hebrew extraction, deduplicates (4-layer pipeline), and outputs ScrapedListing entries. This provides passive coverage of Facebook groups without manual copy-paste.

## INPUT FILES

- **Read:** `specs/LOD400_S005-P005-WP003.md` — full spec (34 ACs) with IMAP contract, email parsing, dedup pipeline, test requirements
- **Reference (FROM output/):** `output/src/shaked_wg_agent/parsers/llm_listing_parser.py` — reuse `parse_rental_post()` and `check_llm_config()` (created by WP002)
- **Reference (FROM output/):** `output/src/shaked_wg_agent/scrapers/facebook_manual.py` — scraper pattern (created by WP002)
- **Reference:** `src/shaked_wg_agent/scrapers/base.py` — BaseScraper interface
- **Read (FROM output/):** `output/data/sources.json` — WP002 already modified this; append facebook-email
- **Read (FROM output/):** `output/data/cities/pardes-hanna-region.json` — WP002 already modified; add facebook-email
- **Read (FROM output/):** `output/data/profiles/pardes-hanna.json` — WP002 already modified; add facebook-email

## CRITICAL: OUTPUT CHAINING

WP003 depends on WP002 output. Read data files and parser module FROM `$SOURCE_ROOT/output/` (not from `$SOURCE_ROOT/`). WP002 has already:
- Created `parsers/llm_listing_parser.py` in output/src/
- Added `facebook-manual` to sources.json, city JSON, and profile JSON in output/data/

Your modifications to sources.json, city JSON, and profile JSON must PRESERVE WP002's additions AND append your entries.

## OUTPUT FILES

- **Create:** `output/src/shaked_wg_agent/scrapers/facebook_email.py`
- **Create:** `output/data/facebook/processed_email_ids.json` (empty `{}`)
- **Create:** `output/tests/fixtures/fb_email_single.eml`
- **Create:** `output/tests/fixtures/fb_email_digest.eml`
- **Create:** `output/tests/fixtures/fb_email_popular.eml`
- **Create:** `output/tests/test_facebook_email.py`
- **Modify:** `output/data/sources.json` (add facebook-email, keep ALL existing including facebook-manual)
- **Modify:** `output/data/cities/pardes-hanna-region.json` (add facebook-email to available_sources)
- **Modify:** `output/data/profiles/pardes-hanna.json` (add facebook-email to enabled_sources)

## TECHNICAL CONTEXT

**EmailFacebookScraper** (`scrapers/facebook_email.py`):
- Subclasses BaseScraper, constructor `(source_id, search_url, city)`
- `search_url` format: `imap://host:port/INBOX` (informational — IMAP config via env vars)
- IMAP credentials: `SHAKED_FB_IMAP_HOST`, `SHAKED_FB_IMAP_USER`, `SHAKED_FB_IMAP_PASS` env vars ONLY
- Never hardcode credentials. Never store them in files.
- `fetch_listings()`: connect IMAP, search for Facebook notification emails, parse posts, LLM extract, dedup, return `list[ScrapedListing]`

**4-layer dedup pipeline** (ordered):
1. Message-ID dedup (against `processed_email_ids.json`)
2. URL exact match
3. Text content hash
4. Fuzzy cross-source match (location_text + price +-10%)

**Email types to handle:**
- Single-post notification: `<user> posted in <group>`
- Digest notification: multiple posts in one email
- Popular post notification: `<post> is popular in <group>`

**Installation in Cowork:**
```bash
pip install imapclient
```

## DO NOT

- Modify the WP002 parser module (`llm_listing_parser.py`)
- Modify `wgzimmer_pw.py` or any existing scraper
- Hardcode IMAP credentials anywhere (env vars ONLY)
- Modify `base.py`
- Automate Facebook login or browser-based scraping

## ACCEPTANCE CRITERIA

34 ACs (AC-01 through AC-34) — see LOD400 spec for full details.

## DEPENDENCIES

- **WP002 must be complete before WP003.** WP003 reuses `parse_rental_post()` and `check_llm_config()` from the parser module created by WP002.
- WP003 reads data files from `output/` (WP002's modified versions).
