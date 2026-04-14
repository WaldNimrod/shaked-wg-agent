# MANDATE — S005-IL-WP002: Homeless.co.il Scraper

**Assigned to:** Team 20 (Builder)
**Authority:** Team 00

## YOUR TASK

Create `shaked_wg_agent/scrapers/homeless.py` — a scraper for homeless.co.il Israeli rental classifieds. Follow the wgzimmer_pw.py Playwright pattern: subclass BaseScraper, implement fetch_listings() using Playwright to bypass Cloudflare, parse HTML with BeautifulSoup, return ScrapedListing with currency/country from city.

## INPUT FILES

- **Read:** `specs/LOD400_S005-IL-WP002.md` — full spec with HTML structure, URL patterns, field mappings, Cloudflare bypass strategy
- **Reference:** `src/shaked_wg_agent/scrapers/base.py` — BaseScraper interface and ScrapedListing dataclass
- **Reference:** `src/shaked_wg_agent/scrapers/flatfox.py` — reference for field mapping and parse pattern
- **Reference:** `src/shaked_wg_agent/scrapers/wgzimmer_pw.py` — **Playwright pattern to follow** (browser launch, stealth, page lifecycle)

## OUTPUT FILES

- **Create:** `output/src/shaked_wg_agent/scrapers/homeless.py`

## TECHNICAL CONTEXT

**CRITICAL: Cloudflare blocks plain HTTP requests.** All pages return 403 with `requests.get()`. You MUST use Playwright.

Homeless.co.il is a server-rendered HTML site (ASP.NET). Listings are in an HTML table with rows `id="ad_NNNNNN"`. Columns: property_type, city, neighborhood, street, rooms, floor, price ("N,NNN ₪"), entry_date, update_date. The board page contains all listing data — no need to visit detail pages.

**Playwright strategy (from wgzimmer_pw.py):**
1. `from playwright.sync_api import sync_playwright` (inline import, try/except ImportError → return [])
2. Launch `chromium.launch(headless=True)`
3. Remove webdriver detection: `page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")`
4. Navigate with `wait_until="domcontentloaded"` + explicit wait (~8 seconds) for Cloudflare
5. Get HTML via `page.content()`, parse with `self._soup(html)`

**Key URL patterns:**
- Rent board: `https://www.homeless.co.il/rent/`
- Pagination: `/rent/2`, `/rent/3`
- Area filter: `/rent/inumber1=AREA_ID`
- Listing detail: `/rent/viewad,ADID.aspx`

**Area ID discovery:** You must determine the correct `inumber1` value for the Pardes Hanna / Hadera area. Use Playwright to load the rent page and inspect the area dropdown/links, or search for חדרה/פרדס חנה.

**Playwright installation in Cowork:** If `playwright` is not pre-installed, run:
```bash
pip install playwright && playwright install chromium
```

## DO NOT

- Modify any existing Python source files
- Use plain `requests.get()` for page fetching (Cloudflare will block it)
- Add top-level imports of playwright (must be inline try/except)
- Modify the ScrapedListing dataclass
- Create test files

## DEPENDENCIES

- WP001 must be complete (city definition for bounding box reference)
