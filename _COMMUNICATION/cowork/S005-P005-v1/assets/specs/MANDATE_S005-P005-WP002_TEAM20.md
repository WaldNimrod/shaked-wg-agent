# MANDATE — S005-P005-WP002: Facebook Manual Listing Parser

**Assigned to:** Team 20 (Builder)
**Authority:** Team 00

## YOUR TASK

Create a ManualFacebookScraper that reads raw Facebook group posts from a local JSON file, sends each post to an LLM (Claude/OpenAI) for structured Hebrew extraction, filters non-rental posts, strips PII, deduplicates against existing listings, and outputs ScrapedListing entries. This includes creating the LLM parser module, the scraper class, data registration, test fixtures, and test files.

## INPUT FILES

- **Read:** `specs/LOD400_S005-P005-WP002.md` — full spec (38 ACs) with code contracts, error handling, dedup algorithm, test matrix
- **Reference:** `src/shaked_wg_agent/scrapers/base.py` — BaseScraper interface and ScrapedListing dataclass
- **Reference:** `src/shaked_wg_agent/scrapers/homeless.py` — Israeli scraper pattern (currency=ILS, country=IL)
- **Reference:** `src/shaked_wg_agent/scrapers/flatfox.py` — Swiss scraper pattern
- **Read:** `data/sources.json` — current source registry (will append)
- **Read:** `data/cities/pardes-hanna-region.json` — city config (will modify available_sources)
- **Read:** `data/profiles/pardes-hanna.json` — profile config (will modify enabled_sources)

## OUTPUT FILES

- **Create:** `output/src/shaked_wg_agent/parsers/__init__.py`
- **Create:** `output/src/shaked_wg_agent/parsers/llm_listing_parser.py`
- **Create:** `output/src/shaked_wg_agent/scrapers/facebook_manual.py`
- **Create:** `output/data/facebook/pardes-hanna-posts.json` (empty template `[]`)
- **Create:** `output/tests/fixtures/hebrew_posts.json` (>=13 entries)
- **Create:** `output/tests/test_facebook_manual.py`
- **Create:** `output/tests/test_llm_parser.py`
- **Create:** `output/tests/test_facebook_manual_dedup.py`
- **Create:** `output/tests/test_facebook_manual_validation.py`
- **Create:** `output/tests/test_llm_parser_modes.py`
- **Modify:** `output/data/sources.json` (add facebook-manual entry, keep all existing)
- **Modify:** `output/data/cities/pardes-hanna-region.json` (add facebook-manual to available_sources)
- **Modify:** `output/data/profiles/pardes-hanna.json` (add facebook-manual to enabled_sources)

## TECHNICAL CONTEXT

**LLM Parser Module** (`parsers/llm_listing_parser.py`):
- `parse_rental_post(text, group_name, post_id)` — sends Hebrew text to Claude/OpenAI, returns structured dict or None
- `check_llm_config()` — returns True if provider + API key are configured
- Provider via `SHAKED_LLM_PROVIDER` env var ("claude" or "openai")
- API keys via `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` env vars
- 7-mode failure matrix: no provider, no key, timeout, rate-limit (retry 1x), malformed, API error 500, all-fail
- Never raises — returns None on any failure

**ManualFacebookScraper** (`scrapers/facebook_manual.py`):
- Subclasses BaseScraper, constructor `(source_id, search_url, city)`
- `fetch_listings()` reads JSON from `search_url` (file path), validates per-post schema, calls LLM parser, deduplicates, returns `list[ScrapedListing]`
- PII stripping: phone regex removal, author_name never in output
- Within-batch dedup: post_id + text-hash
- Cross-source dedup against `data/listings.json`: location_text + price(+-10%)

**Input JSON schema** (8 fields): `post_id` (required), `group_name`, `group_url`, `text` (required, >=10 chars), `author_name`, `posted_at`, `has_images`, `raw_url`

**Installation in Cowork:**
```bash
pip install anthropic openai
```

## DO NOT

- Create the email parser (that is WP003)
- Modify `wgzimmer_pw.py` (that is WP001)
- Modify `base.py` or any existing scraper
- Automate Facebook scraping (this is manual input only)
- Hardcode API keys anywhere
- Store author_name in any output field

## ACCEPTANCE CRITERIA

38 ACs (AC-01 through AC-38) — see LOD400 spec for full details.

## DEPENDENCIES

None — this WP is independent from WP001.
