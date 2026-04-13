# Mandate — S005-P004-WP003 | Team 20 (Builder) | L2.5 Phase 4C

**Issued by:** Team 110 (shaked_arch / Claude Code)
**Authority:** Team 00 (Nimrod)
**Date:** 2026-04-12
**Execution order:** 3 of 3 (AFTER WP001 + WP002)

---

## Context

- **Work Package:** S005-P004-WP003 — Keyword and Label Locale Generalization
- **LOD400 spec:** `specs/LOD400_S005-P004-WP003.md` (v1.1.0)
- **Your scope:** Create new `locale.py` module with frozen Locale dataclass (CH + IL), integrate locale-aware vegan scoring, add `country` to ScrapedListing, make Accept-Language locale-driven, localize CLI status labels, and localize email notifier text. Email strings stored as module-level dict, NOT as Locale fields.
- **Prerequisites:** WP001 complete (field renames in place). WP002 complete (scraper registry in place, scraper constructor via FQN).

## Inputs (read before implementing)

| # | File | Purpose |
|---|------|---------|
| 1 | `specs/LOD400_S005-P004-WP003.md` | **Primary spec — follow exactly** |
| 2 | `shaked_wg_agent/scorer.py` | Vegan scoring (§2.2) — already has WP001 renames |
| 3 | `shaked_wg_agent/scrapers/base.py` | ScrapedListing + BaseScraper (§2.3, §2.4) — already has WP001 renames |
| 4 | `shaked_wg_agent/__main__.py` | CLI status labels (§2.5) — already has WP001 renames |
| 5 | `shaked_wg_agent/notifier/email_notifier.py` | Email text (§2.6) — already has WP001 renames |

## Deliverables

| # | File | Change |
|---|------|--------|
| 1 | `shaked_wg_agent/locale.py` | **NEW** — Locale dataclass, LOCALE_CH, LOCALE_IL, get_locale, EMAIL_STRINGS, get_email_strings |
| 2 | `shaked_wg_agent/scorer.py` | Remove hardcoded vegan keywords, use get_locale(country) |
| 3 | `shaked_wg_agent/scrapers/base.py` | Add `country` field to ScrapedListing; locale-aware Accept-Language in BaseScraper |
| 4 | `shaked_wg_agent/__main__.py` | Status labels from locale |
| 5 | `shaked_wg_agent/notifier/email_notifier.py` | German text from get_email_strings |

## Acceptance Criteria (your scope — all 29)

| AC | Description | Verification |
|----|-------------|--------------|
| AC-01 | `Locale` is frozen dataclass with exactly 10 fields (see §3.1) | Unit test |
| AC-02 | `get_locale("CH").accept_language == "de-CH,de;q=0.9,en;q=0.8"` | Unit test |
| AC-03 | `get_locale("IL").accept_language == "he-IL,he;q=0.9,en;q=0.8"` | Unit test |
| AC-04 | `get_locale("XX")` returns Swiss German locale (fallback) | Unit test |
| AC-05 | `get_locale("CH").vegan_strong` = frozenset with 6 German keywords | Unit test |
| AC-06 | `get_locale("IL").vegan_strong` = frozenset with 4 Hebrew keywords | Unit test |
| AC-07 | `get_locale("CH").direction == "ltr"` and `get_locale("IL").direction == "rtl"` | Unit test |
| AC-08 | `get_locale("CH").html_lang == "de"` and `get_locale("IL").html_lang == "he"` | Unit test |
| AC-09 | `get_locale("CH").status_labels["neu"] == "neu"` and `get_locale("IL").status_labels["neu"] == "חדש"` | Unit test |
| AC-10 | `get_locale("CH").currency_symbol == "CHF"` and `get_locale("IL").currency_symbol == "₪"` | Unit test |
| AC-11 | `grep -n "_VEGAN_STRONG\|_VEGAN_PARTIAL\|_VEGAN_WEAK" shaked_wg_agent/scorer.py` = zero hits | grep check |
| AC-12 | `_vegan_score("vegan", "CH")` returns 35 | Unit test |
| AC-13 | `_vegan_score("טבעוני", "IL")` returns 35 | Unit test |
| AC-14 | `_vegan_score("pflanzlich", "CH")` returns 22 | Unit test |
| AC-15 | `_vegan_score("צמחוני", "IL")` returns 22 | Unit test |
| AC-16 | `_vegan_score("", "CH")` returns 0 | Unit test |
| AC-17 | `_vegan_score("kein signal", "CH")` returns 0 | Unit test |
| AC-18 | `_vegan_score("לא צוין", "IL")` returns 0 | Unit test |
| AC-19 | `ScrapedListing` has `country: str = "CH"` | Unit test |
| AC-20 | `ScrapedListing(..., country="IL").to_dict()` contains `"country": "IL"` | Unit test |
| AC-21 | `grep -n "de-CH" shaked_wg_agent/scrapers/base.py` = zero hits | grep check |
| AC-22 | BaseScraper with `city.country == "IL"` → headers contain `"he-IL"` | Unit test |
| AC-23 | CLI displays `locale.status_labels[status]` for badge text | Code review |
| AC-24 | With `country="CH"`, status `"neu"` displays as `"neu"` | Integration test |
| AC-25 | With `country="IL"`, status `"neu"` displays as `"חדש"` | Integration test |
| AC-26 | `grep -n '"neue Angebote\|Preis nicht angegeben\|Generiert von"' shaked_wg_agent/notifier/email_notifier.py` = zero hits | grep check |
| AC-27 | `get_email_strings("CH")["new_offers"] == "neue Angebote"` | Unit test |
| AC-28 | `get_email_strings("IL")["new_offers"] == "הצעות חדשות"` | Unit test |
| AC-29 | `Locale` dataclass has exactly 10 fields (email strings are NOT Locale fields) | Unit test |

## DO NOT

- Implement RTL rendering in HTML templates (WP004 scope)
- Localize HTML report strings (~50+ strings — WP004 scope)
- Add scraper parsing keywords (source-specific, not locale-specific)
- Add locales beyond CH and IL
- Modify CityDefinition, SearchProfile, or ListingResponse (WP001 scope, already done)
- Modify `runner.py` or `sources.json` (WP002 scope, already done)
- Add email strings as Locale dataclass fields (must be separate EMAIL_STRINGS dict)
- Make design decisions not covered by the LOD400 spec
- Modify files outside your listed deliverables

---

*Mandate issued by Team 110 (shaked_arch / Claude Code) on authority of Team 00 | shaked-wg-agent | S005-P004-WP003 | 2026-04-12*
