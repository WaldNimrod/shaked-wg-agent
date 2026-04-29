# Evidence — Dror profile data quality (production readiness)

**Date:** 2026-04-17  
**Purpose:** Document automated checks and a reproducible snapshot for a client-facing production handoff.

## 1. What was implemented (engineering)

| Area | Change |
|------|--------|
| **Geographic gate** | `CityDefinition.settlement_allowlist` is loaded from `filters.settlements` in city JSON. `score_listing(..., city=...)` returns **0** when no allowlisted settlement substring appears in district + location_text + title + summary (after budget gate). |
| **Source crawl** | `dror-carmel-region` homeless URL set to `https://www.homeless.co.il/rent/inumber1=41` (same regional board as Pardes Hanna profile) to reduce country-wide noise. |
| **Published HTML** | For `country=IL`, the static report uses Hebrew/RTL chrome, homeless-specific data-quality copy, and client-side table strings in Hebrew (modals remain largely German/English — verify on source site). |
| **Evidence script** | `scripts/profile_quality_evidence.py --profile <id>` prints counts and samples (no extra env vars when run from repo root). |

## 2. Automated tests (local)

Commands (from repository root):

```bash
pytest tests/ -q
ruff check shaked_wg_agent/ tests/ scripts/profile_quality_evidence.py
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

**Result at capture:** 85 tests passed; ruff clean; AOS validation 17 PASS / 2 SKIP.

## 3. Snapshot against current `data/listings.json` (Dror)

Generated with:

```bash
python3 scripts/profile_quality_evidence.py --profile dror
```

**Interpretation:** At the time of this capture, **all** stored Dror rows failed the settlement substring gate (0 matches). That is consistent with a **previous** crawl using the broad `/rent/` feed pulling listings across Israel (e.g. Ramat Gan, Rishon, Holon). After deploying the narrowed URL and settlement scoring, run a **full Dror scan** and re-publish so stored scores and the public HTML reflect the new logic.

**Sample rows failing geo gate (illustrative):** listings referenced רמת גן, ראשון לציון, חולון, חיפה, etc. — none of these are on the Dror allowlist in `data/cities/dror-carmel-region.json` (by design). חיפה appears in ad text but **חיפה** is not in the configured settlement list; if Carmel/Haifa listings should count, the allowlist must be updated explicitly.

## 4. Residual risks (client communication)

- **Substring matching** can miss typos or rare spellings; it can theoretically misfire if a short token overlaps another phrase (mitigated by using concrete settlement names).
- **Scraper fields** must carry location text into `district` / `location_text` / `title` / `summary` for the gate to see them.
- **Modal UI** for IL reports is not fully localized; the critical fix was misleading Basel/flatfox hero copy, which is corrected for IL.

## 5. Recommended go-live checklist

1. Deploy this revision to the runner host and run `python -m shaked_wg_agent run` (or your launch script) for profile `dror`.
2. Re-run `python3 scripts/profile_quality_evidence.py --profile dror` and confirm non-zero “rows matching settlement gate” if the regional crawl returns in-area ads.
3. Open the published `report_url` and confirm Hebrew hero + data-quality banner.
