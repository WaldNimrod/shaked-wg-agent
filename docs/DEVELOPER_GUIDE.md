# Shaked WG Agent — Developer Guide

**Version:** 0.3.0 (S002 Platform Foundation)
**Last updated:** 2026-04-12
**Maintained by:** Team 110 (shaked_arch / Claude Code)

This is the canonical developer reference for the Shaked WG Basel agent. It covers architecture, data model, API, configuration, notifications, CLI, deployment, and the S003 transition path.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Data Model — Three-Entity Design](#3-data-model--three-entity-design)
4. [Configuration & Resolution](#4-configuration--resolution)
5. [CLI](#5-cli)
6. [Scrapers](#6-scrapers)
7. [Scoring Engine](#7-scoring-engine)
8. [REST API](#8-rest-api)
9. [Authentication](#9-authentication)
10. [Notification System](#10-notification-system)
11. [Persistence](#11-persistence)
12. [Testing](#12-testing)
13. [Environment Variables](#13-environment-variables)
14. [Deployment](#14-deployment)
15. [Directory Structure](#15-directory-structure)
16. [S003 Transition Path](#16-s003-transition-path)

---

## 1. Project Overview

Shaked WG Agent is an automated WG (shared apartment) search agent for Swiss cities. It scrapes listings from multiple platforms (flatfox, wgzimmer, wg-gesucht), scores them against a user's search profile, and delivers notifications via email, Telegram, Discord, ntfy, or webhook.

**S002 scope (current):** Single-user, multi-city, file-based storage, REST API, API key auth, multi-channel notifications.

**S003 scope (next):** Multi-user, JWT auth with RBAC, PostgreSQL storage. See [§16](#16-s003-transition-path).

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Points                          │
│   CLI (__main__.py)     REST API (api/app.py)           │
└────────┬────────────────────────┬────────────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────────────────────┐
│              Configuration Layer (config.py)             │
│  load_config(profile_id) → ProjectConfig                │
│  AgentMeta + SearchProfile + CityDefinition + Sources   │
└────────┬────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              Runner (runner.py)                          │
│  run_scan(profile_id, triggered_by) → RunRecord         │
│  Orchestrates: scrape → score → persist → notify        │
└──┬──────────┬──────────┬──────────┬─────────────────────┘
   │          │          │          │
   ▼          ▼          ▼          ▼
Scrapers   Scorer    Persistence  Notifier
(flatfox,  (scorer   (listings    (email, telegram,
 wgzimmer,  .py)      .json,       discord, ntfy,
 wg-gesucht)          runs.json)   webhook)
```

**Key design decisions:**
- **Profile-driven:** Everything resolves from `profile_id`. The profile determines the city, which determines available sources.
- **Source resolution:** `profile.enabled_sources ∩ city.available_sources → sources.json lookup → ResolvedSource[]`
- **File-based storage:** JSON files in `data/`. No database in S002.
- **Dependency injection for auth:** FastAPI router-level `Depends()`, not ASGI middleware.

---

## 3. Data Model — Three-Entity Design

S002 separates configuration into three independent entities. This separation is critical for the S003 multi-user transition.

### 3.1 CityDefinition (geography only)

**File:** `data/cities/{city_id}.json`

| Field | Type | Description |
|-------|------|-------------|
| `city_id` | string | Unique ID: `"basel"`, `"zurich"`, `"bern"` |
| `city_name` | string | Display name |
| `country` | string | Country code (`"CH"`) |
| `bounding_box` | BoundingBox | `{west, east, south, north}` — geographic search area |
| `zip_filter` | list[string] | Valid postal codes for this city |
| `available_sources` | list[string] | Source IDs that support this city |

**Example:** `data/cities/basel.json`
```json
{
  "city_id": "basel",
  "city_name": "Basel",
  "country": "CH",
  "bounding_box": {"west": 7.5147, "east": 7.6559, "south": 47.5176, "north": 47.5956},
  "zip_filter": ["4001", "4002", "4003", "4004", "4005", "..."],
  "available_sources": ["wgzimmer", "flatfox", "tutti"]
}
```

### 3.2 SearchProfile (user preferences)

**File:** `data/profiles/{profile_id}.json`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `profile_id` | string | — | Unique ID (regex: `^[a-z][a-z0-9-]{0,29}$`) |
| `profile_name` | string | — | Human-readable label |
| `city_id` | string | — | Reference to CityDefinition |
| `move_in_from` | string | — | Earliest move-in date (ISO) |
| `budget_min_chf` | int | — | Minimum rent |
| `budget_max_chf` | int | — | Maximum rent |
| `preferred_roommate_age` | string | — | `"young"`, `"mixed"`, `"any"`, or `""` |
| `rental_duration` | string | — | `"temporary"`, `"short"`, `"permanent"` |
| `diet` | string | `""` | `"vegan"`, `"vegetarian"`, or `""` |
| `smoking_policy` | string | `""` | `"non_smoking"`, `"smoking_ok"`, or `""` |
| `transit_lines` | list[string] | `[]` | Preferred tram/bus lines |
| `custom_tags` | list[string] | `[]` | Max 3 user-defined tags |
| `language_policy` | LanguagePolicy | — | `{primary_listing_language, translation_required, preserve_source_text}` |
| `retention_days` | int | `30` | Days before stale listings are purged |
| `enabled_sources` | list[string] | `[]` | Subset of `city.available_sources` |
| `notifications` | NotificationConfig | `null` | Notification preferences (see §10) |

### 3.3 SourceDefinition (global platform registry)

**File:** `data/sources.json` (array)

| Field | Type | Description |
|-------|------|-------------|
| `source_id` | string | `"flatfox"`, `"wgzimmer"`, `"wg-gesucht"`, `"tutti"` |
| `label` | string | Display label |
| `base_url` | string | Platform base URL |
| `scraper_class` | string | Informational metadata — NOT used for runtime dispatch |
| `requires_playwright` | bool | Whether this scraper needs Playwright |
| `notes` | string | Operational notes |
| `city_params` | dict[city_id → CitySourceParams] | Per-city connection config |

**CitySourceParams:**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `search_url` | string | — | Full search URL for this city |
| `connection_method` | string | `""` | `"bbox"`, `"canton"`, `"city_id_param"` |
| `enabled` | bool | `true` | Whether this source is active for this city |

### 3.4 AgentMeta

**File:** `data/agent.json`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `default_profile_id` | string | — | Profile to use when none specified |
| `manual_triggers_only` | bool | `true` | Whether scans require explicit trigger |
| `project_window_days` | int | `60` | Active search window |
| `project_start` | string | `""` | Window start date (ISO) |
| `project_end` | string | `""` | Window end date (ISO) |

### 3.5 Resolution Chain

```
profile_id (or default from agent.json)
    → load data/profiles/{profile_id}.json → SearchProfile
    → profile.city_id → load data/cities/{city_id}.json → CityDefinition
    → profile.enabled_sources ∩ city.available_sources
    → lookup each in data/sources.json → city_params[city_id]
    → ResolvedSource[] (sorted by priority)
    → ProjectConfig { agent, profile, city, sources }
```

---

## 4. Configuration & Resolution

### load_config()

```python
def load_config(profile_id: str | None = None) -> ProjectConfig
```

- If `profile_id` is `None`, reads `data/agent.json` → `default_profile_id`
- Loads profile, city, resolves sources
- Returns `ProjectConfig` with `active_sources` property (sorted by priority)
- Validates: budget range, enabled_sources ⊆ available_sources, ID format, notification config ranges

### Validation Rules

| Rule | Error |
|------|-------|
| `budget_min_chf < budget_max_chf` | `ValueError` |
| `enabled_sources ⊆ city.available_sources` | `ValueError` |
| `profile_id` matches `^[a-z][a-z0-9-]{0,29}$` | `ValueError` |
| `custom_tags` max 3 entries | `ValueError` |
| `digest_max_listings` 1–25 | `ValueError` |
| `min_score_threshold` 0–100 | `ValueError` |
| Max 5 notification channels | `ValueError` |
| `ChannelConfig.type` in `{email, telegram, discord, ntfy, webhook}` | `ValueError` |
| Profile/city file not found | `FileNotFoundError` |

---

## 5. CLI

```bash
# Run a scan
python -m shaked_wg_agent run [--profile PROFILE_ID] [--city CITY_ID]

# Show status
python -m shaked_wg_agent status [--profile PROFILE_ID]

# List all listings
python -m shaked_wg_agent list
```

| Flag | Description |
|------|-------------|
| `--profile` | Profile ID to use (default: from `agent.json`) |
| `--city` | **Deprecated alias** for `--profile`. Hidden from help. Resolves by scanning `data/profiles/*.json` for matching `city_id` |

### Commands

- **`run`** — Execute full scan: scrape → score → persist → verify → report → notify
- **`status`** — Show profile summary, listing count, top pick, last run, deadline
- **`list`** — Table of all listings sorted by relevance score (uses `rich` for colored output)

---

## 6. Scrapers

All scrapers inherit from `BaseScraper` and implement `fetch_listings() → list[ScrapedListing]`.

### BaseScraper Interface

```python
class BaseScraper(ABC):
    def __init__(self, source_id: str, search_url: str, city: CityDefinition)
    def fetch_listings(self) -> list[ScrapedListing]   # abstract
    def close(self) -> None
```

Includes `_get(url, retries=2)` with polite 2.5s delay between retries.

### ScrapedListing Dataclass

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Source ID |
| `source_listing_id` | string | Platform-specific listing ID |
| `source_search_url` | string | URL used to find this listing |
| `title` | string | Listing title |
| `price_chf` | int \| None | Monthly rent in CHF |
| `available_from` | string \| None | Move-in date (ISO) |
| `location_text` | string | Raw location string |
| `district` | string | Extracted district/neighborhood |
| `transit_match_lines` | list[string] | Detected tram/bus lines |
| `roommate_signal` | string | Roommate age/type indicators |
| `vegan_signal` | string | Vegan/vegetarian keywords found |
| `summary` | string | Size, rooms, features |
| `direct_url` | string | Direct link to listing |
| `url_status` | string | `"direct"`, `"search_only"`, `"broken_needs_recovery"` |
| `posted_date` | string \| None | Original posting date |

### Flatfox (REST API, no Playwright)

1. PIN API: `GET /api/v1/pin/?west=...&east=...&south=...&north=...&max_count=500` → PKs in bounding box
2. Batch listings: `GET /api/v1/public-listing/?pk=X&pk=Y` (50 per batch)
3. Filters: zip in `city.zip_filter`, `offer_type=RENT`, `category ∈ {SHARED, APARTMENT}`
4. Apartments: `price ≤ 1200 CHF, rooms ≤ 2.0`
5. Tram detection: regex on description, fallback to ZIP→tram lookup table

### WGZimmer (Playwright, intercepts REST API)

1. Launches headless Chromium
2. Registers response listener for `img.wgzimmer.ch/.../rest/v1/*`
3. Navigates to search URL, waits up to 15s for API data
4. If reCAPTCHA blocks: returns `[]` (no crash, no retry)
5. Fallback: DOM parsing if API capture fails
6. Direct URL: `https://www.wgzimmer.ch/wgzimmer/mate/ch/{canton_segment}/{date}-{id}.html`

### WG-Gesucht (HTML scraper, currently disabled)

- Pure `BeautifulSoup` HTML parsing
- Currently disabled (`enabled: false` in sources.json) — requires login/CAPTCHA for Swiss cities
- Parses: `div.wgg_card`, `div.offer_list_item`, `article[class*='listing']`

---

## 7. Scoring Engine

```python
def score_listing(listing: dict, profile: SearchProfile) -> int
```

Returns 0–100 (capped). Budget is a hard gate — over-budget listings score 0.

| Dimension | Max Points | Logic |
|-----------|-----------|-------|
| **Vegan signal** | 35 | `"vegan"/"vegane"` → 35, `"pflanzlich"/"vegetarisch"` → 22, `"kein fleisch"/"plant-based"` → 12, other → 5 |
| **Transit lines** | 25 | Intersection of `listing.transit_match_lines` with `profile.transit_lines`. Formula: `min(25, 12 + (matches-1) * 8)` |
| **Roommate age** | 15 | `preferred_age="young"` + keywords (`"student"`, ages 20-27) → 15; no signal → 0; `"mixed"/"any"` → 8 |
| **Freshness** | 15 | Linear decay over 14 days: `ceil(15 * max(0, 1 - age_days/14))`. Unknown → 7 |
| **Available from** | 10 | `≤ 2026-08-31` → 10, `≤ 2026-10-31` → 5, later → 0, unknown → 5 |
| **URL quality** | 10 | `"direct"` → 10, `"search_only"` → 4, `"broken_needs_recovery"` → 2 |
| **Budget** | gate | Outside `[budget_min, budget_max]` → **score = 0** (hard reject) |

**Legacy compatibility:** `tram_match_lines` key (from S001) is still scored — mapped to `transit_match_lines` internally.

---

## 8. REST API

**Start:** `uvicorn shaked_wg_agent.api.app:create_app --factory --port 8000`

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/health` | No | Health check + `auth_configured` flag |
| `GET` | `/docs` | No | Swagger UI |
| `GET` | `/openapi.json` | No | OpenAPI schema |
| `POST` | `/search` | Yes | Trigger scan, return run record |
| `GET` | `/listings` | Yes | Query listings (paginated, filterable) |
| `GET` | `/listings/{listing_id}` | Yes | Single listing |
| `GET` | `/runs` | Yes | Query run history (paginated) |
| `GET` | `/runs/{run_id}` | Yes | Single run record |

### POST /search

**Request:**
```json
{
  "profile_id": "default",
  "city_id": null
}
```
`profile_id` is preferred. `city_id` is a deprecated alias — resolves by scanning `data/profiles/*.json` for matching `city_id`.

**Response:** `ResponseEnvelope<RunResponse>` with `meta.timestamp` and `meta.request_id`.

### GET /listings

**Query parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `profile_id` | string | — | Filter by profile |
| `city_id` | string | — | Filter by city (deprecated, resolves to profile) |
| `min_score` | int | `0` | Minimum relevance score (0–100) |
| `status` | string | — | Filter by status |
| `source` | string | — | Filter by source |
| `limit` | int | `50` | Page size (1–200) |
| `offset` | int | `0` | Pagination offset |

**Response:** `PaginatedResponse<ListingResponse>` sorted by `relevance_score` DESC.

### Response Envelopes

```json
// Single item
{"data": {...}, "meta": {"timestamp": "...", "request_id": "..."}}

// Paginated
{"data": [...], "meta": {"timestamp": "...", "request_id": "...", "total_count": 59, "offset": 0, "limit": 50}}

// Error
{"error": {"code": "NOT_FOUND", "message": "...", "detail": null}}
```

### Middleware

- **CORS:** Configured via `API_CORS_ORIGINS` env var (comma-separated origins). Disabled if unset.
- **Request ID:** `X-Request-ID` header added to all responses (8-char hex).
- **Error handling:** All exceptions wrapped in `ErrorResponse` envelope. Stack traces included only if `API_DEBUG` is set.

---

## 9. Authentication

**File:** `shaked_wg_agent/api/auth.py`

**Mechanism:** Static API key via `X-API-Key` HTTP header. FastAPI router-level `Depends()` injection — NOT ASGI middleware.

```python
async def verify_api_key(request: Request, x_api_key: str | None = Security(api_key_header)) -> None
```

### Behavior

| Scenario | Response |
|----------|----------|
| Valid key | Request proceeds |
| Missing `X-API-Key` header | 401 `{"error": {"code": "UNAUTHORIZED", "message": "Missing or invalid API key", "detail": null}}` |
| Invalid key | 401 (identical body — no information leakage) |
| `API_KEY` env var not set | 500 `{"error": {"code": "INTERNAL_ERROR", "message": "Server misconfiguration", "detail": null}}` |

### Key Properties

- **Constant-time comparison:** Uses `hmac.compare_digest()` — never `==`
- **Per-request read:** `API_KEY` read from `os.environ` on every request (not cached)
- **No key in logs:** API key value never appears in log output, error messages, or responses
- **Byte-identical 401:** Missing key and invalid key produce identical responses
- **Startup warning:** Logs WARNING if `API_KEY` is unset or shorter than 32 chars
- **`/health` flag:** Response includes `"auth_configured": true/false`

### Router Structure

```python
auth_router = APIRouter(dependencies=[Depends(verify_api_key)])  # /search, /listings, /runs
public_router = APIRouter()  # /health — no auth
# /docs and /openapi.json served by FastAPI on main app — no auth
```

---

## 10. Notification System

**Package:** `shaked_wg_agent/notifier/`

### Configuration (per profile)

```json
{
  "notifications": {
    "digest_max_listings": 5,
    "min_score_threshold": 40,
    "channels": [
      {"type": "email", "enabled": true, "label": "Primary", "params": {"recipients": ["user@example.com"]}},
      {"type": "telegram", "enabled": true, "label": "Mobile", "params": {"chat_id": "123456"}}
    ]
  }
}
```

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `digest_max_listings` | int | 1–25 | Max listings per digest |
| `min_score_threshold` | int | 0–100 | Only include listings scoring above this |
| `channels` | list[ChannelConfig] | max 5 | Notification channels |

### Orchestrator

```python
def notify_digest(profile: dict, city: dict, run_record: dict, new_listings: list[dict]) -> dict | None
```

1. Filters `new_listings` by `min_score_threshold`, sorts by score DESC, caps at `digest_max_listings`
2. Builds digest payload via `build_digest_payload()`
3. Iterates enabled channels, instantiates notifier, calls `send()`
4. On transient error: one retry after 5s sleep
5. Returns `NotificationResult` or `None` (if no channels enabled or no listings pass threshold)
6. **Never aborts the run** — notification failures are logged, not raised

### Channels

| Channel | Config Params | Required Env Vars | Format |
|---------|--------------|-------------------|--------|
| **Email** | `recipients: list[str]` | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM` | HTML with colored score highlights |
| **Telegram** | `chat_id: str` | `TELEGRAM_BOT_TOKEN` | Markdown (max 4096 chars) |
| **Discord** | `webhook_url: str` | — | Embeds with color coding (green ≥70, orange ≥40, red <40) |
| **Ntfy** | `topic: str`, `server_url: str` (default `https://ntfy.sh`) | — | Push with priority (4 if top score ≥80) |
| **Webhook** | `url: str` (must be HTTPS), `headers: dict` (optional) | — | JSON payload (raw digest) |

### BaseNotifier Interface

```python
class BaseNotifier(ABC):
    def __init__(self, config: dict[str, Any]) -> None
    def send(self, digest_payload: dict) -> bool      # abstract
    def format_message(self, digest_payload: dict) -> Any  # abstract
    last_error: str | None
    last_error_transient: bool
```

### Digest Payload Schema

```json
{
  "profile_name": "Shaked Basel WG Search",
  "city_id": "basel",
  "city_name": "Basel",
  "run_id": "run-20260412-143022-a1b2",
  "scan_timestamp": "2026-04-12T14:30:22",
  "total_new": 3,
  "listings": [
    {
      "title": "Helles WG-Zimmer am Rhein",
      "price_chf": 750,
      "district": "Kleinbasel",
      "relevance_score": 82,
      "direct_url": "https://flatfox.ch/de/wohnung/...",
      "vegan_signal": "vegan",
      "transit_match_lines": ["8", "3"]
    }
  ]
}
```

### Runner Integration

In `runner.py`, after scan and persist:
```python
if new_results > 0 and profile.notifications:
    result = notify_digest(profile_dict, city_dict, run_record, new_listing_rows)
    run_record["notification_sent"] = result
```

---

## 11. Persistence

**File:** `shaked_wg_agent/persistence.py`

All data stored as JSON files in `data/`.

### Listings (`data/listings.json`)

- Array of listing dicts
- `listing_id` = `{source}-{source_listing_id}` (unique key)
- **Upsert logic:** If listing_id exists → update fields, preserve `first_seen_at`, update `last_seen_at`. If new → insert with `first_seen_at = now`.
- **Stale removal:** Listings not seen for `retention_days` are removed from the JSON file (no intermediate status — they are dropped directly)
- **Verification:** After scan, HEAD request to each listing URL (flatfox uses PIN API). Updates `verified_active`, `last_verified_at`, `url_status`.

### Runs (`data/runs.json`)

- Array of run record dicts (newest first)
- Each record includes: `run_id`, `run_timestamp`, `triggered_by`, `city_id`, `profile_id`, sources/results/errors counts, `notification_sent`

---

## 12. Testing

**81 tests, all passing.**

```bash
python3 -m pytest tests/ -v --tb=short    # Run all tests
ruff check shaked_wg_agent/ tests/         # Lint
```

| File | Coverage |
|------|----------|
| `test_config.py` | Config loading, validation, ID regex, error cases |
| `test_scorer.py` | All scoring dimensions, edge cases, budget gate, legacy tram key |
| `test_api.py` | All endpoints, auth, pagination, error responses, CORS |
| `test_notifier.py` | Digest building, channel mocking, orchestrator, error handling |
| `test_persistence.py` | Upsert, stale marking, JSON I/O |
| `test_integration.py` | End-to-end scan → notify → report |

---

## 13. Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `API_KEY` | API key for protected endpoints (≥32 chars recommended) |

### Optional — API

| Variable | Description |
|----------|-------------|
| `API_CORS_ORIGINS` | Comma-separated allowed CORS origins |
| `API_DEBUG` | If set, include stack traces in 500 responses |

### Optional — Email Notifications

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | — | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USER` | — | SMTP login |
| `SMTP_PASS` | — | SMTP password |
| `SMTP_FROM` | — | Sender address |

### Optional — Telegram Notifications

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |

### Optional — Publishing

| Variable | Description |
|----------|-------------|
| `UPRESS_SFTP_HOST` | SFTP hostname for HTML report upload |
| `UPRESS_SFTP_PORT` | SFTP port |
| `UPRESS_SFTP_USER` | SFTP username |
| `UPRESS_SFTP_PASS` | SFTP password |
| `UPRESS_PUBLIC_BASE` | Base URL for published reports |
| `UPRESS_UPLOAD_PATH` | Remote path (e.g., `"agents/shaked-wg"`) |
| `UPRESS_WP_REST_BASE` | WordPress REST API base URL |
| `UPRESS_WP_APP_USER` | WordPress app user |
| `UPRESS_WP_APP_PASS` | WordPress app password |

---

## 14. Deployment

### Quick Start

```bash
# Install
pip install -e ".[dev]"

# Create .env
cat > .env <<'EOF'
API_KEY=your-secret-key-at-least-32-characters-long
EOF

# Run API
uvicorn shaked_wg_agent.api.app:create_app --factory --port 8000

# Run scan via CLI
python -m shaked_wg_agent run --profile default

# Run scan via API
curl -X POST http://localhost:8000/search \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "default"}'
```

### Prerequisites

- Python ≥ 3.11
- Playwright (for wgzimmer scraper): `playwright install chromium`
- Dependencies: `pip install -e .`

### Governance Check

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
# Expected: 12 PASS / 0 SKIP / 0 FAIL
```

---

## 15. Directory Structure

```
shaked-wg-agent/
├── shaked_wg_agent/              # Main package
│   ├── __init__.py               # version = "0.3.0"
│   ├── __main__.py               # CLI entry point
│   ├── config.py                 # Dataclasses + load_config()
│   ├── runner.py                 # Scan orchestrator
│   ├── scorer.py                 # Relevance scoring (0-100)
│   ├── persistence.py            # JSON file CRUD
│   ├── api/                      # REST API (FastAPI)
│   │   ├── app.py                # create_app() factory
│   │   ├── routes.py             # Endpoint handlers
│   │   ├── schemas.py            # Pydantic models
│   │   ├── auth.py               # verify_api_key + APIKeyHeader
│   │   └── deps.py               # resolve_profile_id helper
│   ├── scrapers/                 # Platform scrapers
│   │   ├── base.py               # BaseScraper ABC + ScrapedListing
│   │   ├── flatfox.py            # REST API (no Playwright)
│   │   ├── wg_gesucht.py         # HTML (disabled)
│   │   └── wgzimmer_pw.py        # Playwright + REST intercept
│   ├── notifier/                 # Multi-channel notifications
│   │   ├── base.py               # BaseNotifier ABC
│   │   ├── orchestrator.py       # notify_digest()
│   │   ├── digest_builder.py     # build_digest_payload()
│   │   ├── email_notifier.py     # SMTP
│   │   ├── telegram_notifier.py  # Telegram Bot API
│   │   ├── discord_notifier.py   # Discord webhook
│   │   ├── ntfy_notifier.py      # ntfy.sh push
│   │   └── webhook_notifier.py   # Generic HTTPS JSON
│   └── publisher/                # Report generation
│       ├── html_report.py        # Bootstrap HTML generator
│       └── ftps_upload.py        # SFTP upload
├── data/                         # Runtime data (JSON files)
│   ├── agent.json                # AgentMeta
│   ├── sources.json              # Global source registry
│   ├── cities/                   # CityDefinition files
│   │   ├── basel.json
│   │   ├── zurich.json
│   │   └── bern.json
│   ├── profiles/                 # SearchProfile files
│   │   └── default.json
│   ├── listings.json             # Scraped listings
│   └── runs.json                 # Run history
├── tests/                        # Test suite (81 tests)
├── scripts/                      # Utility scripts
├── docs/                         # Documentation
├── _aos/                         # AOS governance
│   ├── work_packages/            # LOD300/400/500 specs
│   ├── lean-kit/                 # Governance framework (read-only)
│   ├── roadmap.yaml              # Milestone tracking
│   └── governance/               # Team contracts
├── _COMMUNICATION/               # Inter-team artifacts
│   ├── team_00/                  # System Designer (read-only for agents)
│   ├── team_110/                 # Architecture agent outputs
│   └── team_190/                 # Validator outputs
└── pyproject.toml                # Project metadata + dependencies
```

---

## 16. S003 Transition Path

S003 replaces the single-user model with multi-user SaaS capabilities. The three-entity data model was designed to make this transition minimal.

| S002 (current) | S003 (planned) |
|----------------|----------------|
| Single static `API_KEY` | Per-user JWT tokens from auth service |
| One implicit user, one profile | Multiple users, multiple profiles per user |
| `SearchProfile` has no owner | `SearchProfile` gains `owner_user_id` field |
| `data/profiles/*.json` file storage | PostgreSQL `profiles` table |
| `data/listings.json` flat file | PostgreSQL `listings` table |
| `verify_api_key(request)` dependency | JWT validation dependency (same interface) |
| 401 only (unauthenticated) | 401 + 403 (unauthorized — role-based) |
| No RBAC | admin / agent / viewer roles |
| `hmac.compare_digest()` | JWT signature verification |
| No `request.state.user_id` | `request.state.user_id` set by auth dependency |

### What does NOT change in S003

- **CityDefinition schema** — geography is global, not per-user
- **SourceDefinition schema** — platform registry is global
- **SearchProfile fields** — only adds `owner_user_id`, all existing fields preserved
- **API endpoint signatures** — `/search`, `/listings`, `/runs` keep same request/response shapes
- **Auth dependency interface** — `verify_api_key(request)` becomes `verify_jwt(request)`, same `Depends()` pattern
- **Notification channel interfaces** — `BaseNotifier.send()` contract unchanged
- **Scoring algorithm** — dimensions and weights stay the same

---

*Canonical developer documentation for shaked-wg-agent S002 Platform Foundation. Maintained by Team 110 (shaked_arch / Claude Code).*
