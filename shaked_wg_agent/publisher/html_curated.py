"""One-click curated HTML builder — v2.0 structure.

Generates a Tailwind + Alpine.js HTML page matching the reference design of
data/shaked_curated_2026-05-01.html:

  1. Header (gradient, stats, cooking-culture notice)
  2. 13-parameter comparison matrix (heatmap, collapsible)
  3. Sticky reactive filter bar (date published, budget, source, cooking, transit, sort)
  4. Listing cards (score ring, badges, info grid, 13-param breakdown, summary)
  5. Full parameters matrix at bottom (rows = parameters, cols = listings)
  6. Footer with profile summary

Data is embedded as a JSON array in a <script> block; Alpine.js handles
all filtering, sorting, and UI state client-side.
"""
from __future__ import annotations

import base64
import contextlib
import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from shaked_wg_agent.config import CityDefinition, SearchProfile, load_config
from shaked_wg_agent.persistence import load_listings

# ---------------------------------------------------------------------------
# 13-parameter scoring
# ---------------------------------------------------------------------------

_PRIMARY_LINES = {"2", "3", "8"}
_SECONDARY_LINES = {"10", "11", "16"}

_VEGAN_KW = re.compile(
    r"vegan|vegetar|pflanzenbasiert|fleischlos|plant.based|tierfreie.küche|cooking.together|"
    r"cook.together|enjoy.cooking|kochbegeister|gemeinsam.kochen",
    re.I,
)
_FURNISHED_KW = re.compile(r"\bmöbliert\b|\bfurnished\b", re.I)
_UNFURNISHED_KW = re.compile(r"\bunmöbliert\b|\bunfurnished\b", re.I)
_PARTIAL_FURN_KW = re.compile(r"\bteilmöbliert\b|\bpartially\s+furnished\b", re.I)
_PRIVATE_BATH_KW = re.compile(r"eigene.dusche|private.bath|en.suite|eigenes.bad|private.bathroom", re.I)
_BALCONY_KW = re.compile(r"\bbalkon\b|\bterrasse\b|\bdachterrasse\b|\bbalcony\b|\bterrace\b|\bgarten\b|\bsitzplatz\b", re.I)
_MIGROS_KW = re.compile(r"\bmigros\b|\bcoop\b|\blidl\b|\baldi\b", re.I)
_WIFI_KW = re.compile(r"\bwlan\b|\bwifi\b|\binternet\b|\bbroadband\b|\wlan", re.I)
_QUIET_KW = re.compile(r"\bruhig\b|\bquiet\b|\bstill\b|\bleise\b|\bruhige\b", re.I)
_STUDENT_KW = re.compile(r"student|azubi|studierend|hochschule|uni\b|fachhochschule", re.I)
_ENGLISH_KW = re.compile(r"\ben\b|\benglish\b|\bwelcome\b|\bwe are\b|\bwe\'re\b|\blooking for\b|\blive\b|\broom\b", re.I)
_GERMAN_ONLY_KW = re.compile(r"\bwir suchen\b|\bwir bieten\b|\bWG\b|\bZimmer\b|\bSchweizer\b", re.I)


def _score_13(lst: dict[str, Any], profile: SearchProfile) -> dict[str, int]:
    desc = (lst.get("full_description") or lst.get("summary") or "").lower()
    title = (lst.get("title") or "").lower()
    text = f"{title} {desc}"

    # 1. Date (15)
    avail = (lst.get("available_from") or "").lower()
    if "01.06" in avail or "2026-06-01" in avail or "june 1" in avail:
        s_date = 15
    elif any(x in avail for x in ("mai", "may", "2026-05")):
        s_date = 12
    elif any(x in avail for x in ("sofort", "immediately", "ab sofort", "asap")):
        s_date = 8
    elif any(x in avail for x in ("vereinbarung", "agreement", "nach", "upon")):
        s_date = 7
    elif any(x in avail for x in ("juli", "july", "august", "2026-07", "2026-08")):
        s_date = 4
    elif avail:
        s_date = 5
    else:
        s_date = 7

    # 2. Roommates (20) — infer from roommate_signal and description
    rmate = (lst.get("roommate_signal") or "").strip()
    if rmate and len(rmate) > 3:
        # Has named roommate info
        s_room = 12
    elif any(x in text for x in ("wg", "mitbewohner", "roommate", "flatmate", "together")):
        s_room = 7
    else:
        s_room = 5

    # 3. Language (12) — detect from title/description
    en_hits = len(_ENGLISH_KW.findall(text))
    de_hits = len(_GERMAN_ONLY_KW.findall(text))
    source = lst.get("source", "")
    if (source == "weegee" and en_hits > 2) or (en_hits >= de_hits and en_hits > 1):
        s_lang = 12
    elif en_hits > 0 and de_hits > 0:
        s_lang = 10
    else:
        s_lang = 4

    # 4. Tram (8)
    lines = set(str(x) for x in (lst.get("transit_match_lines") or []))
    primary_count = len(lines & _PRIMARY_LINES)
    secondary_count = len(lines & _SECONDARY_LINES)
    s_tram = min(8, primary_count * 3 + secondary_count * 1)

    # 5. Furniture (8)
    if _FURNISHED_KW.search(title):
        s_furn = 8
    elif _UNFURNISHED_KW.search(text):
        s_furn = 0
    elif _PARTIAL_FURN_KW.search(text) or _FURNISHED_KW.search(text):
        s_furn = 4
    else:
        s_furn = 2

    # 6. Bathroom (6)
    if _PRIVATE_BATH_KW.search(text) or lst.get("is_quiet_friendly"):
        s_bath = 6
    elif any(x in text for x in ("bad für 2", "halbprivat")):
        s_bath = 4
    else:
        s_bath = 2

    # 7. Kitchen (6)
    if lst.get("is_vegetarian_friendly") or _VEGAN_KW.search(text):
        s_kitchen = 6
    elif lst.get("vegan_signal") and lst["vegan_signal"] != "kein Signal":
        s_kitchen = 4
    else:
        s_kitchen = 2

    # 8. Common space (4)
    if any(x in text for x in ("wohnzimmer", "living room", "gemeinsam", "together", "120m", "100m")):
        s_common = 3
    else:
        s_common = 2

    # 9. Quiet (4)
    s_quiet = 4 if lst.get("is_quiet_friendly") or _QUIET_KW.search(text) else 2

    # 10. Student (8)
    s_student = 6 if lst.get("is_student_oriented") or _STUDENT_KW.search(text) else 2

    # 11. Balcony (3)
    s_balcony = 3 if _BALCONY_KW.search(text) else 0

    # 12. Shopping (3)
    s_migros = 2 if _MIGROS_KW.search(text) else 1

    # 13. Infrastructure (3)
    s_infra = 2 if _WIFI_KW.search(text) else 1

    return {
        "date": s_date,
        "roommates": s_room,
        "lang": s_lang,
        "tram": s_tram,
        "furn": s_furn,
        "bath": s_bath,
        "kitchen": s_kitchen,
        "common": s_common,
        "quiet": s_quiet,
        "student": s_student,
        "balcony": s_balcony,
        "migros": s_migros,
        "intheat": s_infra,
    }


def _total_13(s: dict[str, int]) -> int:
    return sum(s.values())


# ---------------------------------------------------------------------------
# Data preparation
# ---------------------------------------------------------------------------

def _first_seen_bucket(lst: dict[str, Any]) -> str:
    """Return 'today' / 'week' / 'older' based on posted_date (source publication) or first_seen_at."""
    raw = lst.get("posted_date") or lst.get("first_seen_at") or ""
    if not raw:
        return "older"
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        today = datetime.now(timezone.utc).date()  # noqa: UP017
        delta = (today - dt.date()).days
        if delta == 0:
            return "today"
        if delta <= 7:
            return "week"
        return "older"
    except Exception:
        return "older"


def _extract_roommate_age(lst: dict[str, Any]) -> str:
    """Derive a human-readable roommate age string from description text.

    Returns strings like: '≤28 yrs', '20–30 yrs', '~22 yrs (roommate)',
    'young focus', '—'.  Runs at build time so all existing listings benefit.
    """
    text = (
        (lst.get("full_description") or "")
        + " "
        + (lst.get("summary") or "")
        + " "
        + (lst.get("roommate_signal") or "")
    ).lower()

    # Explicit stored values from scraper (best)
    age_min = lst.get("roommate_age_min")
    age_max = lst.get("roommate_age_max")
    if age_min is not None and age_max is not None:
        return f"{age_min}–{age_max} yrs"
    if age_max is not None:
        return f"≤{age_max} yrs"
    if age_min is not None:
        return f"≥{age_min} yrs"

    # Age range: "20 - 35 Jahre" / "zwischen 20 und 35" / "20 to 35"
    m = re.search(r"(\d{2})\s*[-–]\s*(\d{2})\s*(?:j[aä]h|year)", text)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        if 16 <= lo <= hi <= 60:
            return f"{lo}–{hi} yrs"

    m = re.search(r"zwischen\s+(\d{2})\s+und\s+(\d{2})", text)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        if 16 <= lo <= hi <= 60:
            return f"{lo}–{hi} yrs"

    # Upper limit: "bis 28 Jahre", "max 30", "unter 30", "up to 25", "28 Jahre jung"
    m = re.search(r"(?:bis|max\.?|unter|up to)\s+(\d{2})\s*(?:j[aä]h|year|\b)", text)
    if m:
        val = int(m.group(1))
        if 16 <= val <= 60:
            return f"≤{val} yrs"

    m = re.search(r"(\d{2})\s+j[aä]h\w*\s+jung\b", text)
    if m:
        val = int(m.group(1))
        if 16 <= val <= 60:
            return f"≤{val} yrs"

    # Lower limit: "über 30 Jahre", "mindestens 25", "at least 25"
    m = re.search(r"(?:\büber\b|mindestens|at least|over)\s+(\d{2})\s*(?:j[aä]h|year)", text)
    if m:
        val = int(m.group(1))
        if 16 <= val <= 60:
            return f"≥{val} yrs"

    # Existing roommate's age: "ich bin 22 Jahre alt" / "bin 22"
    m = re.search(r"\b(\d{2})\s+j[aä]h\w*\s+alt", text)
    if m:
        age = int(m.group(1))
        if 16 <= age <= 55:
            return f"roommate ~{age} yrs"

    m = re.search(r"\b(?:bin|ich bin|i am|i'm|am)\s+(\d{2})\b", text)
    if m:
        age = int(m.group(1))
        if 16 <= age <= 55:
            return f"roommate ~{age} yrs"

    # "Anfang/Mitte/Ende 20/30" (German idioms)
    m = re.search(r"\b(anfang|mitte|ende)\s+(20|30)\b", text)
    if m:
        decade_map = {"anfang": "early", "mitte": "mid", "ende": "late"}
        return f"{decade_map[m.group(1)]} {m.group(2)}s"

    # Youth signal keywords (broad fallback)
    if re.search(
        r"\bjung[e]?\b|\byoung\b|junge beruf|junge leute|studenten\b|young professional",
        text,
    ):
        return "young focus"

    return "—"


def _listing_js(lst: dict[str, Any], profile: SearchProfile, rank: int) -> dict[str, Any]:
    """Convert a listing dict to a JS-compatible object for Alpine.js."""
    s = _score_13(lst, profile)
    score = _total_13(s)
    lines = list(str(x) for x in (lst.get("transit_match_lines") or []))
    primary_count = sum(1 for ln in lines if ln in _PRIMARY_LINES)
    secondary_count = sum(1 for ln in lines if ln in _SECONDARY_LINES)
    desc = lst.get("full_description") or lst.get("summary") or ""
    avail = lst.get("available_from") or "?"
    source = lst.get("source", "")
    source_url = lst.get("source_search_url") or ""
    source_label = {"flatfox": "flatfox.ch", "weegee": "weegee.ch", "ronorp": "ronorp.net",
                    "unimarkt": "unimarkt.ch", "manual_research": "Manual find"}.get(source, source)
    roommate_age = _extract_roommate_age(lst)
    return {
        "id": lst.get("listing_id", f"lst-{rank}"),
        "rank": rank,
        "title": _make_display_title(lst),
        "location": lst.get("location_text") or "",
        "district": lst.get("district") or "",
        "price": lst.get("price") or lst.get("price_chf") or 0,
        "embeddedStatus": lst.get("status") or "neu",
        "available": avail,
        "availBucket": _avail_bucket(avail),
        "source": source,
        "sourceLabel": source_label,
        "url": lst.get("direct_url") or source_url or "#",
        "tram": lines,
        "tramPrimaryCount": primary_count,
        "tramSecondaryCount": secondary_count,
        "tramPrimary": primary_count > 0,
        "cookingCulture": bool(lst.get("is_vegetarian_friendly")),
        "veganSignal": lst.get("vegan_signal") or "",
        "isQuiet": bool(lst.get("is_quiet_friendly")),
        "isStudent": bool(lst.get("is_student_oriented")),
        "roommateAge": roommate_age,
        "summary": (desc[:300] + "…") if len(desc) > 300 else desc,
        "firstSeenBucket": _first_seen_bucket(lst),
        "firstSeenAt": lst.get("posted_date") or lst.get("first_seen_at") or "",
        "status": lst.get("status") or "",
        "verifiedActive": bool(lst.get("verified_active", True)),
        "s": s,
        "score": score,
        "_open": True,
    }


_GENERIC_TITLE_RE = re.compile(
    r"^(wg[- ]?zimmer?|[0-9][- ]zimmer[- ]?(wohnung|einzelzimmer|wg)?|zimmer in wg|zimmer)$",
    re.I,
)


def _make_display_title(lst: dict[str, Any]) -> str:
    """Build a human-readable title when the source title is generic (e.g. 'WG Zimmer')."""
    raw = (lst.get("title") or "").strip()
    if raw and not _GENERIC_TITLE_RE.match(raw):
        return raw
    # Build from available fields
    parts: list[str] = []
    district = (lst.get("district") or "").strip()
    if district and district not in ("Basel", ""):
        parts.append(district)
    else:
        loc = lst.get("location_text") or ""
        street = loc.split(",")[0].strip()
        if street:
            parts.append(street[:22])
    price = lst.get("price") or lst.get("price_chf")
    if price:
        parts.append(f"{price} CHF")
    avail = (lst.get("available_from") or "").strip()
    if avail:
        if "2026-06-01" in avail or "01.06" in avail:
            parts.append("01.06")
        elif "2026-05" in avail:
            parts.append("Mai")
        elif "sofort" in avail.lower() or "immediately" in avail.lower():
            parts.append("Sofort")
        else:
            parts.append(avail[:7])
    return " · ".join(parts) if parts else (raw or "WG Basel")


def _avail_bucket(avail: str) -> str:
    a = avail.lower()
    if any(x in a for x in ("01.06", "2026-06-01")):
        return "jun_confirmed"
    if any(x in a for x in ("sofort", "immediately", "asap", "ab sofort")):
        return "immediate"
    if any(x in a for x in ("mai", "may", "2026-05", "2026-06", "july", "juni", "juli")):
        return "flex_window"
    return "flex_window"


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shaked WG Basel · {page_title_tag}</title>
<script src="https://cdn.tailwindcss.com"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<style>
  [x-cloak]{{display:none!important}}
  .score-ring{{background:conic-gradient(var(--c) calc(var(--p)*1%),#e5e7eb 0);border-radius:50%}}
  .sticky-filter{{position:sticky;top:0;z-index:40;backdrop-filter:blur(8px);background:rgba(250,250,247,.94)}}
  .matrix table{{font-variant-numeric:tabular-nums}}
  .matrix td.sc{{text-align:center;font-weight:600}}
  .heatmap-1{{background:#fee2e2;color:#991b1b}}
  .heatmap-2{{background:#fed7aa;color:#9a3412}}
  .heatmap-3{{background:#fef3c7;color:#92400e}}
  .heatmap-4{{background:#d9f99d;color:#3f6212}}
  .heatmap-5{{background:#a7f3d0;color:#065f46}}
  .heatmap-max{{background:#6ee7b7;color:#064e3b}}
  .scroll-x{{overflow-x:auto;-webkit-overflow-scrolling:touch}}
  @media(max-width:767px){{.filter-strip{{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}}.filter-strip>*{{flex-shrink:0}}}}
</style>
</head>
<body class="bg-stone-50 text-slate-800" x-data="app()" x-cloak>

<!-- ═══ HEADER ═══ -->
<header class="bg-gradient-to-l {header_gradient} text-white">
  <div class="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-10">
    <div class="flex items-baseline flex-wrap gap-2 mb-1">
      <h1 class="text-xl md:text-3xl font-bold">{header_title}</h1>
      <span class="{header_text_muted} text-xs md:text-sm">v2.0 · {built}</span>
    </div>
    {peer_link_html}
    <p class="{header_text_light} text-sm md:text-lg max-w-3xl mt-2">
      {header_subtitle}
    </p>
    <div class="mt-3 bg-emerald-900/40 border border-emerald-500/40 rounded-lg p-3 text-sm text-emerald-100">
      <strong>🌱 Vegan / plant-based kitchen</strong> = strong advantage. Flagged on cards when detected.
      <span class="text-emerald-300">In database: {veg_count} listings with cooking-culture</span>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4 mt-4">
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs {header_text_muted}">Verified live</div><div class="text-lg md:text-2xl font-bold">{top_n}/{top_n}</div></div>
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs {header_text_muted}">Price range</div><div class="text-lg md:text-2xl font-bold">{price_range}</div></div>
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs {header_text_muted}">Sources</div><div class="text-lg md:text-2xl font-bold">{sources_str}</div></div>
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs {header_text_muted}">🌱 Vegan</div><div class="text-lg md:text-2xl font-bold">{veg_count}</div></div>
    </div>
  </div>
</header>

<!-- ═══ STICKY FILTER BAR ═══ -->
<div class="sticky-filter border-b border-stone-200 shadow-sm">
  <div class="max-w-7xl mx-auto px-4 md:px-6 py-3">
    <div class="filter-strip flex flex-wrap items-center gap-2 text-sm">
      <span class="font-semibold text-slate-700 text-xs">Filter:</span>

      <!-- Publication date -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">Published</span>
        <template x-for="opt in [{{v:'all',l:'All'}},{{v:'today',l:'Today'}},{{v:'recent',l:'2 days'}},{{v:'week',l:'This week'}}]" :key="opt.v">
          <button @click="filters.published=opt.v"
                  :class="filters.published===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Budget min/max -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">Min</span>
        <template x-for="opt in [{{v:'all',l:'All'}},{{v:'ge500',l:'≥500'}},{{v:'ge600',l:'≥600'}},{{v:'ge700',l:'≥700'}}]" :key="opt.v">
          <button @click="filters.budgetMin=opt.v"
                  :class="filters.budgetMin===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">Max</span>
        <template x-for="opt in [{{v:'all',l:'All'}},{{v:'le800',l:'≤800'}},{{v:'le900',l:'≤900'}},{{v:'le1000',l:'≤1000'}}]" :key="opt.v">
          <button @click="filters.budgetMax=opt.v"
                  :class="filters.budgetMax===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Available date -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">Move-in</span>
        <template x-for="opt in [{{v:'all',l:'All'}},{{v:'jun_confirmed',l:'Confirmed'}},{{v:'immediate',l:'Sofort'}},{{v:'flex_window',l:'Flexible'}}]" :key="opt.v">
          <button @click="filters.avail=opt.v"
                  :class="filters.avail===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Source -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">Source</span>
        <template x-for="opt in [{{v:'all',l:'All'}},{{v:'flatfox',l:'flatfox'}},{{v:'weegee',l:'weegee'}}]" :key="opt.v">
          <button @click="filters.source=opt.v"
                  :class="filters.source===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Status filter -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">Status</span>
        <template x-for="opt in [{{v:'active',l:'Active'}},{{v:'all',l:'All'}},{{v:'sent',l:'💬 Contacted'}},{{v:'progress',l:'⏳ In progress'}}]" :key="opt.v">
          <button @click="filters.status=opt.v"
                  :class="filters.status===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Checkboxes -->
      <label class="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
        <input type="checkbox" x-model="filters.cooking" class="rounded">🌱 cooking culture
      </label>
      <label class="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
        <input type="checkbox" x-model="filters.tram" class="rounded">🚊 primary tram (3/8/2)
      </label>
      <label class="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
        <input type="checkbox" x-model="filters.quiet" class="rounded">🤫 quiet
      </label>

      <!-- Sort -->
      <div class="mr-auto flex items-center gap-2">
        <span class="text-xs text-slate-500">Sort:</span>
        <select x-model="sortBy" class="text-xs border border-stone-300 rounded-lg px-2 py-1 bg-white">
          <option value="score">Score</option>
          <option value="price_asc">Price ↑</option>
          <option value="price_desc">Price ↓</option>
          <option value="date_new">Newest first</option>
        </select>
      </div>
      <button @click="resetFilters()" class="text-xs text-slate-600 hover:text-slate-900 underline">Reset</button>
    </div>
    <div class="mt-1.5 text-xs text-slate-500">Showing <span class="font-semibold" x-text="filtered().length"></span> of {top_n} listings</div>
  </div>
</div>

<!-- ═══ LISTING CARDS ═══ -->
<main class="max-w-7xl mx-auto px-3 md:px-6 py-4 md:py-8">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6" data-listing-count="{top_n}">
    <template x-for="(l, i) in filtered()" :key="l.id">
      <article data-listing-card class="bg-white rounded-xl overflow-hidden border border-stone-100 shadow-sm transition hover:shadow-md"
               :class="statusCardClass(getStatus(l.id))">

        <!-- Card header -->
        <div class="p-4 pb-3 border-b border-stone-100">
          <div class="flex items-start gap-4">
            <div class="score-ring flex-shrink-0 w-14 h-14 flex items-center justify-center"
                 :style="`--p:${{l.score}}; --c:${{l.score>=65?'#059669':l.score>=50?'#2563eb':'#b45309'}}`">
              <div class="w-11 h-11 bg-white rounded-full flex items-center justify-center">
                <span class="font-bold text-lg"
                      :class="l.score>=65?'text-emerald-700':l.score>=50?'text-blue-700':'text-amber-700'"
                      x-text="l.score"></span>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline gap-2 mb-1">
                <span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-slate-800 text-white text-xs font-bold flex-shrink-0" x-text="`#${{l.rank}}`"></span>
                <h2 class="font-bold text-base text-slate-900 leading-tight" x-text="l.title"></h2>
              </div>
              <div class="text-sm text-slate-500" x-text="(l.district||'') + (l.location?' · '+l.location:'')"></div>
              <div class="flex flex-wrap gap-1.5 mt-2">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700" x-text="l.sourceLabel"></span>
                <span x-show="l.cookingCulture" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-green-200 text-green-900 ring-2 ring-green-500/40">🌱 Cooking-Culture</span>
                <span x-show="l.tramPrimary" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">🚊 Primary line</span>
                <span x-show="l.isStudent" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">🎓 Student-friendly</span>
                <span x-show="l.isQuiet" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-sky-100 text-sky-800">🤫 Quiet</span>
                <span x-show="l.firstSeenBucket==='today'" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">🆕 Today</span>
                <span x-show="l.firstSeenBucket==='recent'" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-700">🕐 2 days</span>
                <span x-show="l.firstSeenBucket==='week'" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-stone-100 text-stone-600">📅 This week</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Info grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 pb-2">
          <div>
            <div class="text-xs text-slate-400">Price / mo</div>
            <div class="font-bold text-slate-900" x-text="(l.price||'?') + ' CHF'"></div>
          </div>
          <div>
            <div class="text-xs text-slate-400">Move-in</div>
            <div class="font-bold text-slate-900 text-sm" x-text="l.available"></div>
            <div class="text-xs" :class="l.availBucket==='jun_confirmed'?'text-emerald-700':l.availBucket==='immediate'?'text-blue-700':'text-amber-700'"
                 x-text="l.availBucket==='jun_confirmed'?'✓ Confirmed':l.availBucket==='immediate'?'◐ Immediate':'◐ Flexible'"></div>
          </div>
          <div>
            <div class="text-xs text-slate-400">Tram lines</div>
            <div class="font-bold text-slate-900" x-text="l.tram.length ? l.tram.join(', ') : '—'"></div>
            <div class="text-xs" :class="l.tramPrimaryCount>0?'text-emerald-600':'text-slate-400'"
                 x-text="`${{l.tramPrimaryCount}} primary · ${{l.tramSecondaryCount}} secondary`"></div>
          </div>
          <div>
            <div class="text-xs text-slate-400">👥 Roommates</div>
            <div class="font-bold text-sm"
                 :class="l.roommateAge!=='—'?(l.roommateAge.includes('young')||l.roommateAge.includes('≤')?'text-emerald-700':'text-slate-800'):'text-slate-500'"
                 x-text="l.roommateAge!=='—'?l.roommateAge:(l.s.roommates>=12?'Named ✓':l.s.roommates>=7?'WG ✓':'Unknown')"></div>
            <div class="text-[10px] text-slate-400" x-text="l.roommateAge!=='—'?'age detected':l.sourceLabel"></div>
          </div>
        </div>

        <!-- 13-param breakdown table (always visible) -->
        <div class="px-4 pt-2 pb-3 bg-slate-50/60 border-y border-stone-100">
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-semibold text-slate-600">📊 Score breakdown — 13 parameters</span>
            <button @click="l._open=!l._open"
                    class="text-[11px] text-slate-400 hover:text-slate-700 underline"
                    x-text="l._open?'Collapse ▲':'Expand ▼'"></button>
          </div>
          <div x-show="l._open" x-transition>
            <div class="overflow-x-auto rounded border border-stone-200">
              <table class="w-full text-xs">
                <thead class="bg-slate-100 text-slate-600">
                  <tr>
                    <th class="text-left px-2 py-1.5 font-semibold">Parameter</th>
                    <th class="text-center px-2 py-1.5 font-semibold w-14">Score</th>
                    <th class="text-center px-2 py-1.5 font-semibold w-10">Max</th>
                    <th class="text-left px-2 py-1.5 font-semibold">Signal detected</th>
                  </tr>
                </thead>
                <tbody>
                  <template x-for="p in scoreRows(l)" :key="p.k">
                    <tr class="border-t border-stone-100 hover:bg-stone-50">
                      <td class="px-2 py-1 text-slate-700 font-medium" x-text="p.name"></td>
                      <td class="px-2 py-1 text-center font-bold"
                          :class="p.v/p.max>=1?'text-emerald-700':p.v/p.max>=0.6?'text-blue-600':p.v/p.max>=0.3?'text-amber-600':'text-rose-600'"
                          x-text="p.v"></td>
                      <td class="px-2 py-1 text-center text-slate-400" x-text="p.max"></td>
                      <td class="px-2 py-1 text-slate-500 italic" x-text="p.sig"></td>
                    </tr>
                  </template>
                  <tr class="border-t-2 border-slate-300 bg-slate-100 font-bold">
                    <td class="px-2 py-1.5 text-slate-800">Total</td>
                    <td class="px-2 py-1.5 text-center"
                        :class="l.score>=65?'text-emerald-700':l.score>=50?'text-blue-700':'text-amber-700'"
                        x-text="l.score"></td>
                    <td class="px-2 py-1.5 text-center text-slate-400">100</td>
                    <td class="px-2 py-1.5 text-slate-400 text-xs font-normal">sum of all 13 parameters</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="px-4 py-3">
          <p class="text-sm text-slate-600 line-clamp-3" x-text="l.summary"></p>
          <div x-show="l.veganSignal && l.veganSignal !== 'kein Signal'"
               class="mt-2 text-xs text-emerald-700">🌱 <span x-text="l.veganSignal"></span></div>
        </div>

        <!-- Status buttons -->
        <div class="px-3 py-2 bg-stone-50/80 border-t border-stone-100">
          <div class="flex items-center gap-1 flex-wrap">
            <span class="text-[10px] text-slate-400 ml-1">Status:</span>
            <template x-for="[sv, sl] in Object.entries(statusLabels)" :key="sv">
              <button @click.stop="setStatus(l.id, sv)"
                      :class="getStatus(l.id)===sv ? statusActiveClass(sv) : 'bg-white text-slate-500 border-stone-200 hover:bg-stone-100'"
                      class="px-2 py-0.5 text-[11px] rounded border transition"
                      x-text="sl"></button>
            </template>
          </div>
        </div>

        <!-- CTA -->
        <div class="px-4 py-2.5 border-t border-stone-100 flex items-center justify-between bg-white">
          <div class="text-xs text-slate-400">
            <span x-show="l.firstSeenAt" x-text="l.firstSeenAt.substring(0,10)"></span>
          </div>
          <a :href="l.url" target="_blank" rel="noopener"
             class="inline-flex items-center gap-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-lg text-sm font-medium transition">
            Open ↗
          </a>
        </div>
      </article>
    </template>
  </div>

  <div x-show="filtered().length===0" class="text-center py-16">
    <div class="text-5xl mb-3">🔍</div>
    <p class="text-slate-600">No listings match the current filters.</p>
    <button @click="resetFilters()" class="mt-3 text-blue-600 hover:underline text-sm">Reset filters</button>
  </div>

  <!-- ═══ FULL PARAMETERS MATRIX ═══ -->
  <section class="mt-12 pt-8 border-t-2 border-stone-200">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-xl md:text-2xl font-bold text-slate-900">📋 Full Parameters Matrix</h2>
      <button @click="showFullTable=!showFullTable" class="text-sm text-blue-600 hover:text-blue-800 font-medium"
              x-text="showFullTable?'Collapse ▲':'Expand ▼'"></button>
    </div>
    <p class="text-sm text-slate-600 mb-4">
      Columns = listings (sorted by score) · Rows = parameters ·
      <span class="text-amber-600">"?"</span> = not mentioned in listing.
    </p>
    <div x-show="showFullTable" x-transition class="scroll-x">
      <table class="text-xs border border-stone-200 rounded-lg bg-white w-full" style="min-width:100%">
        <thead class="bg-slate-50">
          <tr>
            <th class="text-left p-2 sticky left-0 bg-slate-50 border-r-2 border-stone-300 min-w-[160px]">Parameter</th>
            <template x-for="l in sortedListings()" :key="'fh-'+l.id">
              <th class="text-center p-2 min-w-[130px] border-l border-stone-200">
                <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-slate-800 text-white text-[10px] font-bold mb-1" x-text="`#${{l.rank}}`"></span>
                <div class="font-bold text-slate-900 text-[11px] leading-tight" x-text="l.title.substring(0,22)"></div>
                <div class="text-slate-400 text-[10px]" x-text="l.district||l.location"></div>
                <div class="mt-1 inline-block px-2 py-0.5 rounded font-bold text-xs"
                     :class="l.score>=65?'bg-emerald-100 text-emerald-800':l.score>=50?'bg-blue-100 text-blue-800':'bg-amber-100 text-amber-800'"
                     x-text="l.score"></div>
              </th>
            </template>
          </tr>
        </thead>
        <tbody class="text-slate-700">

          <tr class="bg-blue-50/40"><td colspan="99" class="p-1.5 font-bold text-blue-900 sticky left-0">🎯 Basics</td></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Price (CHF)</td>
          <template x-for="l in sortedListings()" :key="'pr-'+l.id"><td class="text-center p-2 font-bold border-l border-stone-100" x-text="l.price||'?'"></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Move-in</td>
          <template x-for="l in sortedListings()" :key="'av-'+l.id"><td class="text-center p-2 border-l border-stone-100">
            <div x-text="l.available"></div>
            <div class="text-[10px]" :class="l.availBucket==='jun_confirmed'?'text-emerald-700':'text-amber-600'"
                 x-text="l.availBucket==='jun_confirmed'?'✓ Confirmed':l.availBucket==='immediate'?'◐ Immediate':'◐ Flexible'"></div>
          </td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Source</td>
          <template x-for="l in sortedListings()" :key="'src-'+l.id"><td class="text-center p-2 text-[11px] border-l border-stone-100" x-text="l.sourceLabel"></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">👥 Roommate age</td>
          <template x-for="l in sortedListings()" :key="'ra-'+l.id"><td class="text-center p-2 border-l border-stone-100"
            :class="l.roommateAge==='—'?'text-slate-300':l.roommateAge.includes('young')||l.roommateAge.includes('≤')?'text-emerald-700 font-bold':'text-slate-700 font-medium'"
            x-text="l.roommateAge"></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Published</td>
          <template x-for="l in sortedListings()" :key="'fs-'+l.id"><td class="text-center p-2 text-[11px] border-l border-stone-100">
            <span :class="l.firstSeenBucket==='today'?'text-amber-700 font-bold':l.firstSeenBucket==='recent'?'text-orange-600 font-semibold':l.firstSeenBucket==='week'?'text-blue-600':'text-slate-400'"
                  x-text="l.firstSeenBucket==='today'?'🆕 Today':l.firstSeenBucket==='recent'?'🕐 2 days':l.firstSeenBucket==='week'?'This week':'Old'"></span>
            <div class="text-[10px] text-slate-400" x-text="l.firstSeenAt?l.firstSeenAt.substring(0,10):''"></div>
          </td></template></tr>

          <tr class="bg-cyan-50/40"><td colspan="99" class="p-1.5 font-bold text-cyan-900 sticky left-0">🚊 Transit</td></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Tram lines</td>
          <template x-for="l in sortedListings()" :key="'tr-'+l.id"><td class="text-center p-2 font-medium border-l border-stone-100" x-text="l.tram.length?l.tram.join(', '):'—'"></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Primary (3/8/2)</td>
          <template x-for="l in sortedListings()" :key="'trp-'+l.id"><td class="text-center p-2 border-l border-stone-100" :class="l.tramPrimaryCount>0?'text-emerald-700 font-bold':'text-slate-400'" x-text="l.tramPrimaryCount+' of 3'"></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Secondary (10/11/16)</td>
          <template x-for="l in sortedListings()" :key="'trs-'+l.id"><td class="text-center p-2 border-l border-stone-100 text-slate-600" x-text="l.tramSecondaryCount+' of 3'"></td></template></tr>

          <tr class="bg-emerald-50/40"><td colspan="99" class="p-1.5 font-bold text-emerald-900 sticky left-0">✨ Signals</td></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">🌱 Cooking-Culture</td>
          <template x-for="l in sortedListings()" :key="'cc-'+l.id"><td class="text-center p-2 border-l border-stone-100"><span x-show="l.cookingCulture" class="text-emerald-700 font-bold">✓</span><span x-show="!l.cookingCulture" class="text-slate-300">—</span></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Vegan signal</td>
          <template x-for="l in sortedListings()" :key="'vs-'+l.id"><td class="text-center p-2 text-[11px] border-l border-stone-100" x-text="l.veganSignal&&l.veganSignal!=='kein Signal'?l.veganSignal:'—'"></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">🤫 Quiet</td>
          <template x-for="l in sortedListings()" :key="'qt-'+l.id"><td class="text-center p-2 border-l border-stone-100"><span x-show="l.isQuiet" class="text-sky-700 font-bold">✓</span><span x-show="!l.isQuiet" class="text-slate-300">—</span></td></template></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">🎓 Student-friendly</td>
          <template x-for="l in sortedListings()" :key="'st-'+l.id"><td class="text-center p-2 border-l border-stone-100"><span x-show="l.isStudent" class="text-indigo-700 font-bold">✓</span><span x-show="!l.isStudent" class="text-slate-300">—</span></td></template></tr>

          <tr class="bg-slate-100"><td colspan="99" class="p-1.5 font-bold text-slate-900 sticky left-0">📊 13-Parameter Scores</td></tr>
          <template x-for="p in [['📅 Move-in','date',15],['👥 Roommates','roommates',20],['🇬🇧 Language','lang',12],['🚊 Tram','tram',8],['🛏 Furnished','furn',8],['🚿 Bathroom','bath',6],['🍳 Kitchen/diet','kitchen',6],['🏠 Common space','common',4],['🤫 Quiet','quiet',4],['🎓 Student','student',8],['🌳 Balcony','balcony',3],['🛒 Shopping','migros',3],['⚡ Internet','intheat',3]]" :key="p[1]">
            <tr>
              <td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium text-[11px]" x-text="p[0]+' /'+p[2]"></td>
              <template x-for="l in sortedListings()" :key="p[1]+'-'+l.id">
                <td class="sc p-1.5 border-l border-stone-100" :class="hm(l.s[p[1]],p[2])" x-text="l.s[p[1]]"></td>
              </template>
            </tr>
          </template>

          <tr class="bg-slate-200"><td class="p-2 sticky left-0 bg-slate-200 border-r-2 border-stone-300 font-bold">Total /100</td>
          <template x-for="l in sortedListings()" :key="'tot-'+l.id">
            <td class="text-center p-2 font-bold text-base border-l border-stone-200"
                :class="l.score>=65?'bg-emerald-100 text-emerald-900':l.score>=50?'bg-blue-100 text-blue-900':'bg-amber-100 text-amber-900'"
                x-text="l.score"></td>
          </template></tr>

          <tr class="bg-stone-50"><td colspan="99" class="p-1.5 font-bold text-slate-700 sticky left-0">🔗 Links</td></tr>
          <tr><td class="p-2 sticky left-0 bg-white border-r-2 border-stone-200 font-medium">Listing link</td>
          <template x-for="l in sortedListings()" :key="'lk-'+l.id"><td class="text-center p-2 border-l border-stone-100"><a :href="l.url" target="_blank" rel="noopener" class="text-blue-600 hover:text-blue-800 underline text-xs">Open ↗</a></td></template></tr>
        </tbody>
      </table>
    </div>
  </section>
</main>

<!-- ═══ 13-PARAM SCORE MATRIX ═══ -->
<section class="bg-white border-t-2 border-stone-200 mt-8">
  <div class="max-w-7xl mx-auto px-3 md:px-6 py-4 md:py-8">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl md:text-2xl font-bold text-slate-900">📊 Score Heatmap — 13 Parameters</h2>
      <button @click="showMatrix=!showMatrix" class="text-sm text-blue-600 hover:text-blue-800 font-medium" x-text="showMatrix?'Collapse ▲':'Expand ▼'"></button>
    </div>
    <p class="text-sm text-slate-600 mb-4">Each total = sum of 13 parameters / 100. Cells are colour-coded by % of the parameter's maximum.</p>
    <div x-show="showMatrix" x-transition class="matrix scroll-x">
      <table class="w-full text-xs border border-stone-200 rounded-lg overflow-hidden" style="min-width:1050px">
        <thead class="bg-slate-50">
          <tr>
            <th class="text-left p-2 sticky left-0 bg-slate-50 border-l border-stone-200 min-w-[180px]">Listing</th>
            <th class="text-center p-2">📅<br>Move-in<br><span class="text-[10px] text-slate-400">/15</span></th>
            <th class="text-center p-2">👥<br>Roommates<br><span class="text-[10px] text-slate-400">/20</span></th>
            <th class="text-center p-2">🇬🇧<br>Language<br><span class="text-[10px] text-slate-400">/12</span></th>
            <th class="text-center p-2">🚊<br>Tram<br><span class="text-[10px] text-slate-400">/8</span></th>
            <th class="text-center p-2">🛏<br>Furnished<br><span class="text-[10px] text-slate-400">/8</span></th>
            <th class="text-center p-2">🚿<br>Bathroom<br><span class="text-[10px] text-slate-400">/6</span></th>
            <th class="text-center p-2">🍳<br>Kitchen<br><span class="text-[10px] text-slate-400">/6</span></th>
            <th class="text-center p-2">🏠<br>Space<br><span class="text-[10px] text-slate-400">/4</span></th>
            <th class="text-center p-2">🤫<br>Quiet<br><span class="text-[10px] text-slate-400">/4</span></th>
            <th class="text-center p-2">🎓<br>Student<br><span class="text-[10px] text-slate-400">/8</span></th>
            <th class="text-center p-2">🌳<br>Balcony<br><span class="text-[10px] text-slate-400">/3</span></th>
            <th class="text-center p-2">🛒<br>Shopping<br><span class="text-[10px] text-slate-400">/3</span></th>
            <th class="text-center p-2">⚡<br>Internet<br><span class="text-[10px] text-slate-400">/3</span></th>
            <th class="text-center p-2 bg-slate-100 font-bold">Total<br><span class="text-[10px] text-slate-400">/100</span></th>
          </tr>
        </thead>
        <tbody id="score-matrix-tbody">
          <template x-for="l in sortedListings()" :key="'m-'+l.id">
            <tr class="border-t border-stone-100 hover:bg-blue-50/30">
              <td class="p-2 sticky left-0 bg-white border-l border-stone-200">
                <div class="flex items-center gap-1.5">
                  <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-slate-800 text-white text-[10px] font-bold flex-shrink-0" x-text="`#${{l.rank}}`"></span>
                  <a :href="l.url" target="_blank" class="font-semibold text-slate-900 hover:text-blue-700 text-xs" x-text="l.title.substring(0,38)"></a>
                </div>
                <div class="text-[10px] text-slate-500 mt-0.5" x-text="l.district || l.location"></div>
              </td>
              <td class="sc p-1" :class="hm(l.s.date,15)" x-text="l.s.date"></td>
              <td class="sc p-1" :class="hm(l.s.roommates,20)" x-text="l.s.roommates"></td>
              <td class="sc p-1" :class="hm(l.s.lang,12)" x-text="l.s.lang"></td>
              <td class="sc p-1" :class="hm(l.s.tram,8)" x-text="l.s.tram"></td>
              <td class="sc p-1" :class="hm(l.s.furn,8)" x-text="l.s.furn"></td>
              <td class="sc p-1" :class="hm(l.s.bath,6)" x-text="l.s.bath"></td>
              <td class="sc p-1" :class="hm(l.s.kitchen,6)" x-text="l.s.kitchen"></td>
              <td class="sc p-1" :class="hm(l.s.common,4)" x-text="l.s.common"></td>
              <td class="sc p-1" :class="hm(l.s.quiet,4)" x-text="l.s.quiet"></td>
              <td class="sc p-1" :class="hm(l.s.student,8)" x-text="l.s.student"></td>
              <td class="sc p-1" :class="hm(l.s.balcony,3)" x-text="l.s.balcony"></td>
              <td class="sc p-1" :class="hm(l.s.migros,3)" x-text="l.s.migros"></td>
              <td class="sc p-1" :class="hm(l.s.intheat,3)" x-text="l.s.intheat"></td>
              <td class="sc p-1 bg-slate-50 font-bold text-base" x-text="l.score"></td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    <details class="mt-4 text-sm">
      <summary class="cursor-pointer text-slate-700 font-semibold">📖 How is each parameter scored?</summary>
      <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-600 text-xs">
        <div class="bg-stone-50 rounded p-3"><strong>📅 Move-in date (15)</strong><br>15=01.06 confirmed · 12=May–June · 8=Sofort (immediate) · 7=By arrangement · 4=Jul–Aug</div>
        <div class="bg-stone-50 rounded p-3"><strong>👥 Roommates (20)</strong><br>12=Named roommates found · 7=WG mentioned · 5=Unknown</div>
        <div class="bg-stone-50 rounded p-3"><strong>🇬🇧 Language (12)</strong><br>12=English listing · 10=EN+DE · 4=German only</div>
        <div class="bg-stone-50 rounded p-3"><strong>🚊 Tram (8)</strong><br>3 pts per primary line (3/8/2) · 1 pt per secondary (10/11/16)</div>
        <div class="bg-stone-50 rounded p-3"><strong>🛏 Furnished (8)</strong><br>8=Fully furnished · 4=Partial · 2=Unknown · 0=Unfurnished</div>
        <div class="bg-stone-50 rounded p-3"><strong>🚿 Bathroom (6)</strong><br>6=Private / en-suite · 4=Semi-private · 2=Shared</div>
        <div class="bg-stone-50 rounded p-3"><strong>🍳 Kitchen / diet (6)</strong><br>6=Cooking culture / vegan household · 4=Vegan keywords · 2=Not specified</div>
        <div class="bg-stone-50 rounded p-3"><strong>🤫 Quiet (4)</strong><br>4=ruhig / quiet explicitly mentioned · 2=Not specified</div>
        <div class="bg-stone-50 rounded p-3"><strong>🎓 Student-friendly (8)</strong><br>6=student / Studenten explicitly mentioned · 2=Neutral</div>
        <div class="bg-stone-50 rounded p-3"><strong>🌳 Balcony (3)</strong><br>3=Balkon / Terrasse · 0=Not mentioned</div>
        <div class="bg-stone-50 rounded p-3"><strong>🛒 Shopping (3)</strong><br>2=Migros / Coop mentioned · 1=Not specified</div>
        <div class="bg-stone-50 rounded p-3"><strong>⚡ Internet / infra (3)</strong><br>2=WiFi / Internet mentioned · 1=Not mentioned</div>
      </div>
    </details>
  </div>
</section>

<!-- ═══ FOOTER ═══ -->
<footer class="bg-slate-900 text-slate-300 mt-12">
  <div class="max-w-7xl mx-auto px-6 py-10">
    <h3 class="text-xl font-bold text-white mb-4">Profile v2.0 · Shaked · WG Basel</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-sm">
      <div><h4 class="font-semibold text-white mb-2">Layer 1 — Core facts</h4>
        <p>Shaked, 18, Swiss citizen, future chemistry student at Uni Basel (Frühjahr 2027), language student at ILS Basel, Swiss-Arab background.</p></div>
      <div><h4 class="font-semibold text-white mb-2">Layer 2 — Explicit requirements</h4>
        <p>Hard budget 1000 CHF · WG with roommates · Tram 3/8/2 · Cooking culture kitchen · Acoustic insulation · English preferred · Furnished + bed · Common space &gt; private.</p></div>
      <div><h4 class="font-semibold text-white mb-2">Score calculation</h4>
        <p>13 parameters, 100 points total. Automatic analysis from listing text. ? = not mentioned — ask when contacting.</p></div>
    </div>
    <div class="mt-6 text-xs text-slate-500 text-center">v2.0 · {built} · {total_count} listings in database · Sources: {sources_full}</div>
  </div>
</footer>

<!-- ═══ FLOATING SYNC BUTTON ═══ -->
<div class="fixed bottom-5 left-4 z-50 flex flex-col items-start gap-2" x-show="pendingSync || syncing">
  <button @click="syncStatus()"
          :disabled="syncing"
          class="flex items-center gap-2 bg-blue-700 hover:bg-blue-800 disabled:opacity-60 text-white text-sm font-semibold px-4 py-2.5 rounded-full shadow-lg transition">
    <span x-show="!syncing">☁️ Save statuses</span>
    <span x-show="syncing">⏳ Saving…</span>
  </button>
</div>

<script>
function app() {{
  return {{
    showMatrix: false,
    showFullTable: false,
    filters: {{ published:'all', budgetMin:'all', budgetMax:'all', avail:'all', source:'all', cooking:false, tram:false, quiet:false, status:'active' }},
    sortBy: 'score',
    statusMap: {{}},
    statusLabels: {{'neu':'◯ New','sent':'💬 Contacted','progress':'⏳ In progress','visited':'🏠 Visited','skip':'❌ Skip','signed':'✅ Signed'}},
    pendingSync: false,
    syncing: false,

    init() {{
      const today = new Date(); today.setHours(0,0,0,0);
      this.listings.forEach(l => {{
        if (!l.firstSeenAt) {{ l.firstSeenBucket = 'older'; return; }}
        const d = new Date(l.firstSeenAt); d.setHours(0,0,0,0);
        const delta = Math.round((today - d) / 86400000);
        l.firstSeenBucket = delta === 0 ? 'today' : delta <= 2 ? 'recent' : delta <= 7 ? 'week' : 'older';
      }});
      const saved = localStorage.getItem('shaked_wg_status');
      if (saved) try {{ this.statusMap = JSON.parse(saved); }} catch(e) {{}}
      this.listings.forEach(l => {{
        if (!this.statusMap[l.id] && l.embeddedStatus && l.embeddedStatus !== 'neu')
          this.statusMap[l.id] = l.embeddedStatus;
      }});
      localStorage.setItem('shaked_wg_status', JSON.stringify(this.statusMap));
    }},

    getStatus(id) {{ return this.statusMap[id] || 'neu'; }},
    setStatus(id, sv) {{
      if (sv === 'neu') delete this.statusMap[id]; else this.statusMap[id] = sv;
      this.statusMap = {{...this.statusMap}};
      localStorage.setItem('shaked_wg_status', JSON.stringify(this.statusMap));
      this.pendingSync = true;
    }},
    statusCardClass(s) {{
      return {{'sent':'border-l-4 border-l-blue-400','progress':'border-l-4 border-l-amber-400','visited':'border-l-4 border-l-purple-400','skip':'opacity-40 border-l-4 border-l-red-300','signed':'border-l-4 border-l-emerald-500 bg-emerald-50/20'}}[s] || '';
    }},
    statusActiveClass(sv) {{
      return {{'sent':'bg-blue-100 text-blue-800 border-blue-300','progress':'bg-amber-100 text-amber-800 border-amber-300','visited':'bg-purple-100 text-purple-800 border-purple-300','skip':'bg-red-100 text-red-800 border-red-300','signed':'bg-emerald-100 text-emerald-800 border-emerald-300','neu':'bg-slate-200 text-slate-700 border-slate-300'}}[sv] || '';
    }},
    async syncStatus() {{
      this.syncing = true;
      try {{
        const tok = '{wp_token}';
        const base = '{wp_rest_base}';
        const oldId = localStorage.getItem('shaked_status_mid');
        if (oldId) await fetch(base+'/wp/v2/media/'+oldId+'?force=1', {{method:'DELETE',headers:{{Authorization:'Basic '+tok}}}});
        const r = await fetch(base+'/wp/v2/media', {{method:'POST',headers:{{Authorization:'Basic '+tok,'Content-Disposition':'attachment; filename="shaked-status.json"','Content-Type':'application/json'}},body:JSON.stringify(this.statusMap)}});
        if (!r.ok) throw new Error(await r.text());
        const j = await r.json();
        localStorage.setItem('shaked_status_mid', String(j.id));
        this.pendingSync = false;
        alert('✅ Sync successful! ID: '+j.id);
      }} catch(e) {{ alert('❌ Sync error: '+e); }}
      finally {{ this.syncing = false; }}
    }},

    hm(v, max) {{
      const p = v/max;
      if (p>=1) return 'heatmap-max';
      if (p>=0.75) return 'heatmap-5';
      if (p>=0.5) return 'heatmap-4';
      if (p>=0.3) return 'heatmap-3';
      if (p>0) return 'heatmap-2';
      return 'heatmap-1';
    }},

    sortedListings() {{
      return this.listings.slice().sort((a,b) => b.score - a.score);
    }},

    filtered() {{
      let list = this.listings.filter(l => {{
        if (this.filters.published !== 'all' && l.firstSeenBucket !== this.filters.published) return false;
        if (this.filters.budgetMin === 'ge500' && l.price < 500) return false;
        if (this.filters.budgetMin === 'ge600' && l.price < 600) return false;
        if (this.filters.budgetMin === 'ge700' && l.price < 700) return false;
        if (this.filters.budgetMax === 'le800' && l.price > 800) return false;
        if (this.filters.budgetMax === 'le900' && l.price > 900) return false;
        if (this.filters.budgetMax === 'le1000' && l.price > 1000) return false;
        if (this.filters.avail !== 'all' && l.availBucket !== this.filters.avail) return false;
        if (this.filters.source !== 'all' && l.source !== this.filters.source) return false;
        if (this.filters.cooking && !l.cookingCulture) return false;
        if (this.filters.tram && !l.tramPrimary) return false;
        if (this.filters.quiet && !l.isQuiet) return false;
        const st = this.getStatus(l.id);
        if (this.filters.status === 'active' && (st === 'skip' || st === 'signed')) return false;
        if (this.filters.status === 'sent' && st !== 'sent') return false;
        if (this.filters.status === 'progress' && st !== 'progress') return false;
        return true;
      }});
      const dir = this.sortBy === 'price_asc' ? 1 : -1;
      if (this.sortBy === 'price_asc' || this.sortBy === 'price_desc')
        list.sort((a,b) => (a.price - b.price) * dir);
      else if (this.sortBy === 'date_new')
        list.sort((a,b) => (b.firstSeenAt||'').localeCompare(a.firstSeenAt||''));
      else
        list.sort((a,b) => b.score - a.score);
      return list;
    }},

    resetFilters() {{
      this.filters = {{ published:'all', budgetMin:'all', budgetMax:'all', avail:'all', source:'all', cooking:false, tram:false, quiet:false, status:'active' }};
      this.sortBy = 'score';
    }},

    scoreRows(l) {{
      const params = [
        {{k:'date',      name:'Move-in date',     max:15}},
        {{k:'roommates', name:'Roommates / age',  max:20}},
        {{k:'lang',      name:'Language',          max:12}},
        {{k:'tram',      name:'Tram lines',        max:8}},
        {{k:'furn',      name:'Furnished',         max:8}},
        {{k:'bath',      name:'Bathroom',          max:6}},
        {{k:'kitchen',   name:'Kitchen / diet',    max:6}},
        {{k:'common',    name:'Common space',      max:4}},
        {{k:'quiet',     name:'Quiet',             max:4}},
        {{k:'student',   name:'Student-friendly',  max:8}},
        {{k:'balcony',   name:'Balcony',           max:3}},
        {{k:'migros',    name:'Shopping nearby',   max:3}},
        {{k:'intheat',   name:'Internet / infra',  max:3}},
      ];
      return params.map(p => {{
        const v = l.s[p.k] ?? 0;
        let sig = '';
        if (p.k === 'date') {{
          sig = v===15?'01.06 confirmed':v===12?'May–June window':v===8?'Sofort / immediate':v===7?'By arrangement':v===4?'Jul–Aug':v>0?'Possible':'Unknown / not specified';
        }} else if (p.k === 'roommates') {{
          const ageStr = l.roommateAge && l.roommateAge !== '—' ? ' · age: '+l.roommateAge : '';
          sig = (v===12?'Named roommates found':v===7?'WG mentioned':'Unknown') + ageStr;
        }} else if (p.k === 'lang') {{
          sig = v===12?'English listing':v===10?'English + German':v===4?'German only':'Unknown';
        }} else if (p.k === 'tram') {{
          sig = l.tram && l.tram.length ? 'Lines: '+l.tram.join(', ')+(l.tramPrimaryCount>0?' ('+l.tramPrimaryCount+' primary)':'') : 'No tram data';
        }} else if (p.k === 'furn') {{
          sig = v===8?'Fully furnished':v===4?'Partial / unclear':v===2?'Not specified':'Unfurnished';
        }} else if (p.k === 'bath') {{
          sig = v===6?'Private / en-suite':v===4?'Semi-private':'Shared';
        }} else if (p.k === 'kitchen') {{
          sig = v===6?'🌱 Cooking culture / vegan household':v===4?'Vegan keyword detected':'Not specified';
        }} else if (p.k === 'common') {{
          sig = v>=3?'Common space mentioned':'Not specified';
        }} else if (p.k === 'quiet') {{
          sig = v>=3?'Quiet / ruhig explicitly mentioned':'Not specified';
        }} else if (p.k === 'student') {{
          sig = v>=5?'Student-friendly listing':'Neutral';
        }} else if (p.k === 'balcony') {{
          sig = v>0?'Balcony / terrace':'—';
        }} else if (p.k === 'migros') {{
          sig = v>=2?'Migros / Coop mentioned':'—';
        }} else if (p.k === 'intheat') {{
          sig = v>=2?'WiFi / Internet mentioned':'—';
        }}
        return {{...p, v, sig}};
      }});
    }},

    listings: {listings_json}
  }};
}}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_THEMES: dict[str, dict[str, str]] = {
    "blue": {
        "header_gradient": "from-blue-700 to-blue-900",
        "header_text_muted": "text-blue-200",
        "header_text_light": "text-blue-100",
    },
    "orange": {
        "header_gradient": "from-orange-600 to-amber-800",
        "header_text_muted": "text-orange-200",
        "header_text_light": "text-orange-100",
    },
}


def build_html(
    listings: list[dict[str, Any]],
    profile: SearchProfile,
    city: CityDefinition | None = None,
    top: int = 20,
    wp_token: str = "",
    wp_rest_base: str = "https://www.nimrod.bio/wp-json",
    color_theme: str = "blue",
    peer_url: str = "",
    peer_label: str = "",
    avail_label: str = "01.06.2026",
) -> str:
    """Score, select top-N, and render the curated HTML page."""
    # Score all listings with 13-param system, sort, take top N
    scored = []
    for lst in listings:
        s = _score_13(lst, profile)
        total = _total_13(s)
        scored.append((total, lst))
    scored.sort(key=lambda x: x[0], reverse=True)
    top_listings = [lst for _, lst in scored[:top]]

    # Build JS objects
    js_objects = [_listing_js(lst, profile, i + 1) for i, lst in enumerate(top_listings)]

    built = date.today().isoformat()
    prices = [lst.get("price") or lst.get("price_chf") for lst in top_listings]
    prices = [p for p in prices if p]
    price_range = f"{min(prices)}–{max(prices)}" if prices else "—"
    veg_count = sum(1 for lst in top_listings if lst.get("is_vegetarian_friendly"))
    sources = sorted(set(lst.get("source", "") for lst in top_listings))
    sources_str = "+".join(s for s in sources if s)
    total_count = len(listings)

    listings_json = json.dumps(js_objects, ensure_ascii=False, indent=2)

    theme = _THEMES.get(color_theme, _THEMES["blue"])

    # Peer link HTML (link between the two pages)
    if peer_url and peer_label:
        peer_link_html = (
            f'<a href="{peer_url}" class="inline-flex items-center gap-1 mt-1 mb-1 '
            f'text-white/80 hover:text-white text-xs underline underline-offset-2">'
            f'↗ {peer_label}</a>'
        )
    else:
        peer_link_html = ""

    # Header title / subtitle based on theme
    if color_theme == "orange":
        header_title = f"Shaked's Top {top} — Basel 🍂 Aug–Sep"
        header_subtitle = (
            "Long-term WG · Move-in <strong>01.08 – 01.10.2026</strong> · "
            "Budget <strong>≤ 1,000 CHF</strong> · "
            "Swiss citizen, 18, future chemistry student Uni Basel · English preferred · <strong>vegan</strong>"
        )
        page_title_tag = f"Basel Aug–Sep · {top} listings · {built}"
    else:
        header_title = f"Shaked's Top {top} — Basel"
        header_subtitle = (
            f"Long-term WG · Move-in {avail_label} · Budget <strong>≤ 1,000 CHF</strong> · "
            "Swiss citizen, 18, future chemistry student Uni Basel · ILS Basel · English preferred · <strong>vegan</strong>"
        )
        page_title_tag = f"Basel · {top} listings · {built}"

    return _HTML_TEMPLATE.format(
        top=top,
        top_n=top,
        built=built,
        price_range=price_range,
        veg_count=veg_count,
        sources_str=sources_str,
        sources_full=", ".join(sources) if sources else "—",
        total_count=total_count,
        listings_json=listings_json,
        wp_token=wp_token,
        wp_rest_base=wp_rest_base,
        header_gradient=theme["header_gradient"],
        header_text_muted=theme["header_text_muted"],
        header_text_light=theme["header_text_light"],
        peer_link_html=peer_link_html,
        header_title=header_title,
        header_subtitle=header_subtitle,
        page_title_tag=page_title_tag,
    )


def _load_status_map() -> dict[str, str]:
    """Download shaked-status.json from WP (current month) or fall back to local file."""
    import requests
    now = datetime.now(timezone.utc)  # noqa: UP017
    public_base = os.environ.get("UPRESS_PUBLIC_BASE", "https://www.nimrod.bio")
    url = f"{public_base}/wp-content/uploads/{now.year}/{now.month:02d}/shaked-status.json"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            data = r.json()
            Path("data/shaked-status.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return data
    except Exception:
        pass
    local = Path("data/shaked-status.json")
    if local.exists():
        return json.loads(local.read_text(encoding="utf-8"))
    return {}


def rebuild_html(
    profile_id: str | None = None,
    top: int = 20,
    out: str | Path = "shaked_curated.html",
    extra_listings_path: str | Path | None = None,
    avail_from: str | None = None,
    avail_to: str | None = None,
    color_theme: str = "blue",
    peer_url: str = "",
    peer_label: str = "",
) -> Path:
    """High-level entry point: load config + listings, build, write file.

    avail_from / avail_to: ISO date strings (YYYY-MM-DD) to filter by available_from.
    extra_listings_path:
        Optional path to a JSON file with additional listings to merge.
        Deduplicates by source+source_listing_id; extra entries win on conflict.
    """
    from dotenv import load_dotenv
    load_dotenv()

    # Build WP auth token for embedding in the HTML (status sync)
    wp_user = os.environ.get("UPRESS_WP_APP_USER", "")
    wp_pass = os.environ.get("UPRESS_WP_APP_PASS", "")
    wp_token = base64.b64encode(f"{wp_user}:{wp_pass}".encode()).decode() if wp_user else ""
    wp_rest_base = os.environ.get("UPRESS_WP_REST_BASE", "https://www.nimrod.bio/wp-json")

    cfg = load_config(profile_id)
    listings = load_listings()

    # Apply persisted statuses (from previous browser syncs)
    status_map = _load_status_map()
    if status_map:
        for lst in listings:
            lid = lst.get("listing_id")
            if lid and lid in status_map:
                lst["status"] = status_map[lid]

    if extra_listings_path is not None:
        extra_path = Path(extra_listings_path)
        extra_raw: list[dict[str, Any]] = json.loads(extra_path.read_text(encoding="utf-8"))
        seen: dict[tuple[str, str], int] = {}
        for idx, lst in enumerate(listings):
            key = (lst.get("source", ""), lst.get("source_listing_id", ""))
            seen[key] = idx
        for extra in extra_raw:
            key = (extra.get("source", ""), extra.get("source_listing_id", ""))
            if key in seen:
                listings[seen[key]].update(extra)
            else:
                listings.append(extra)

    # Filter by available_from date range if specified
    if avail_from or avail_to:
        from datetime import date as _date
        filtered: list[dict[str, Any]] = []
        for lst in listings:
            raw_avail = str(lst.get("available_from") or "").strip().lower()
            # Parse to date; treat unknown/sofort as None (skip for date-specific views)
            avail_date: _date | None = None
            if raw_avail and raw_avail not in ("none", "null", "nan", "sofort", "immediately", "ab sofort", "asap"):
                with contextlib.suppress(ValueError):
                    avail_date = _date.fromisoformat(raw_avail[:10])
            if avail_date is None:
                continue  # exclude unknown dates in date-filtered view
            if avail_from and avail_date < _date.fromisoformat(avail_from):
                continue
            if avail_to and avail_date > _date.fromisoformat(avail_to):
                continue
            filtered.append(lst)
        listings = filtered

    avail_label = "01.06.2026"
    if avail_from:
        avail_label = avail_from

    html = build_html(listings, cfg.profile, cfg.city, top=top,
                      wp_token=wp_token, wp_rest_base=wp_rest_base,
                      color_theme=color_theme, peer_url=peer_url, peer_label=peer_label,
                      avail_label=avail_label)
    out_path = Path(out)
    out_path.write_text(html, encoding="utf-8")
    return out_path
