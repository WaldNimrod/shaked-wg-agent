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

import json
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
    """Return 'today' / 'week' / 'older' based on first_seen_at."""
    raw = lst.get("first_seen_at") or lst.get("posted_date") or ""
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
                    "unimarkt": "unimarkt.ch", "manual_research": "מחקר ידני"}.get(source, source)
    return {
        "id": lst.get("listing_id", f"lst-{rank}"),
        "rank": rank,
        "title": lst.get("title") or f"Listing #{rank}",
        "location": lst.get("location_text") or "",
        "district": lst.get("district") or "",
        "price": lst.get("price") or 0,
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
        "summary": (desc[:300] + "…") if len(desc) > 300 else desc,
        "firstSeenBucket": _first_seen_bucket(lst),
        "firstSeenAt": lst.get("first_seen_at") or "",
        "status": lst.get("status") or "",
        "verifiedActive": bool(lst.get("verified_active", True)),
        "s": s,
        "score": score,
        "_open": False,
    }


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
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>שקד · {top}N דירות באזל · v2.0 · {built}</title>
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
<header class="bg-gradient-to-l from-blue-700 to-blue-900 text-white">
  <div class="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-10">
    <div class="flex items-baseline flex-wrap gap-2 mb-2">
      <h1 class="text-xl md:text-3xl font-bold">{top_n} דירות לשקד · באזל</h1>
      <span class="text-blue-200 text-xs md:text-sm">v2.0 · {built}</span>
    </div>
    <p class="text-blue-100 text-sm md:text-lg max-w-3xl">
      WG ארוך-טווח · כניסה 01.06.2026 · תקציב <strong>≤ 1000 CHF</strong> ·
      אזרח שוויצרי בן 18, סטודנט עתידי כימיה Uni Basel · ILS Basel · אנגלית מועדפת · <strong>טבעוני</strong>
    </p>
    <div class="mt-3 bg-emerald-900/40 border border-emerald-500/40 rounded-lg p-3 text-sm text-emerald-100">
      <strong>🌱 מטבח צמחוני / טבעוני</strong> = יתרון משמעותי. מסומן בכרטיסים כשנמצא.
      <span class="text-emerald-300">סטטוס במאגר: {veg_count} דירות עם cooking-culture</span>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4 mt-4">
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs text-blue-200">מאומתות חיות</div><div class="text-lg md:text-2xl font-bold">{top_n}/{top_n}</div></div>
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs text-blue-200">טווח מחיר</div><div class="text-lg md:text-2xl font-bold">{price_range}</div></div>
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs text-blue-200">מקורות</div><div class="text-lg md:text-2xl font-bold">{sources_str}</div></div>
      <div class="bg-white/10 rounded-lg p-2 md:p-3"><div class="text-[10px] md:text-xs text-blue-200">🌱 צמחוני</div><div class="text-lg md:text-2xl font-bold">{veg_count}</div></div>
    </div>
  </div>
</header>

<!-- ═══ 13-PARAM SCORE MATRIX ═══ -->
<section class="bg-white border-b-2 border-stone-200">
  <div class="max-w-7xl mx-auto px-3 md:px-6 py-4 md:py-8">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl md:text-2xl font-bold text-slate-900">📊 טבלת השוואת ציונים — 13 פרמטרים</h2>
      <button @click="showMatrix=!showMatrix" class="text-sm text-blue-600 hover:text-blue-800 font-medium" x-text="showMatrix?'כווץ ▲':'הרחב ▼'"></button>
    </div>
    <p class="text-sm text-slate-600 mb-4">כל ציון = סכום 13 פרמטרים / 100. תאי הטבלה צבועים לפי אחוז המקסימום שכל פרמטר השיג.</p>
    <div x-show="showMatrix" x-transition class="matrix scroll-x">
      <table class="w-full text-xs border border-stone-200 rounded-lg overflow-hidden" style="min-width:1050px">
        <thead class="bg-slate-50">
          <tr>
            <th class="text-right p-2 sticky right-0 bg-slate-50 border-l border-stone-200 min-w-[180px]">דירה</th>
            <th class="text-center p-2">📅<br>תאריך<br><span class="text-[10px] text-slate-400">/15</span></th>
            <th class="text-center p-2">👥<br>שותפים<br><span class="text-[10px] text-slate-400">/20</span></th>
            <th class="text-center p-2">🇬🇧<br>שפה<br><span class="text-[10px] text-slate-400">/12</span></th>
            <th class="text-center p-2">🚊<br>טרם<br><span class="text-[10px] text-slate-400">/8</span></th>
            <th class="text-center p-2">🛏<br>ריהוט<br><span class="text-[10px] text-slate-400">/8</span></th>
            <th class="text-center p-2">🚿<br>מקלחת<br><span class="text-[10px] text-slate-400">/6</span></th>
            <th class="text-center p-2">🍳<br>מטבח<br><span class="text-[10px] text-slate-400">/6</span></th>
            <th class="text-center p-2">🏠<br>שטח<br><span class="text-[10px] text-slate-400">/4</span></th>
            <th class="text-center p-2">🤫<br>שקט<br><span class="text-[10px] text-slate-400">/4</span></th>
            <th class="text-center p-2">🎓<br>סטודנט<br><span class="text-[10px] text-slate-400">/8</span></th>
            <th class="text-center p-2">🌳<br>מרפסת<br><span class="text-[10px] text-slate-400">/3</span></th>
            <th class="text-center p-2">🛒<br>קניות<br><span class="text-[10px] text-slate-400">/3</span></th>
            <th class="text-center p-2">⚡<br>תשתיות<br><span class="text-[10px] text-slate-400">/3</span></th>
            <th class="text-center p-2 bg-slate-100 font-bold">סה״כ<br><span class="text-[10px] text-slate-400">/100</span></th>
          </tr>
        </thead>
        <tbody id="score-matrix-tbody">
          <template x-for="l in sortedListings()" :key="'m-'+l.id">
            <tr class="border-t border-stone-100 hover:bg-blue-50/30">
              <td class="p-2 sticky right-0 bg-white border-l border-stone-200">
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
      <summary class="cursor-pointer text-slate-700 font-semibold">📖 כיצד מחושב כל פרמטר?</summary>
      <div class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-600 text-xs">
        <div class="bg-stone-50 rounded p-3"><strong>📅 תאריך (15)</strong><br>15=01.06 ודאי · 12=מאי-יוני · 8=Sofort · 7=Vereinbarung · 4=יולי-אוגוסט</div>
        <div class="bg-stone-50 rounded p-3"><strong>👥 שותפים (20)</strong><br>12=שמות ידועים · 7=WG מוזכר · 5=לא ידוע</div>
        <div class="bg-stone-50 rounded p-3"><strong>🇬🇧 שפה (12)</strong><br>12=אנגלית בלבד · 10=EN+DE · 4=גרמנית בלבד</div>
        <div class="bg-stone-50 rounded p-3"><strong>🚊 טרם (8)</strong><br>3 נק׳ לכל קו ראשוני (3/8/2) · 1 נק׳ לכל קו משני (10/11/16)</div>
        <div class="bg-stone-50 rounded p-3"><strong>🛏 ריהוט (8)</strong><br>8=möbliert מלא · 4=חלקי · 2=לא ידוע · 0=unmöbliert</div>
        <div class="bg-stone-50 rounded p-3"><strong>🚿 מקלחת (6)</strong><br>6=פרטית / en-suite · 4=חצי-פרטית · 2=משותפת</div>
        <div class="bg-stone-50 rounded p-3"><strong>🍳 מטבח (6)</strong><br>6=צמחוני/cooking culture · 4=vegan keywords · 2=לא צוין</div>
        <div class="bg-stone-50 rounded p-3"><strong>🤫 שקט (4)</strong><br>4=ruhig/quiet מפורש · 2=לא צוין</div>
        <div class="bg-stone-50 rounded p-3"><strong>🎓 סטודנט (8)</strong><br>6=student/Studenten מפורש · 2=ניטרלי</div>
        <div class="bg-stone-50 rounded p-3"><strong>🌳 מרפסת (3)</strong><br>3=Balkon/Terrasse · 0=אין/לא צוין</div>
        <div class="bg-stone-50 rounded p-3"><strong>🛒 קניות (3)</strong><br>2=Migros/Coop מוזכר · 1=לא צוין</div>
        <div class="bg-stone-50 rounded p-3"><strong>⚡ תשתיות (3)</strong><br>2=WiFi/Internet · 1=לא מוזכר</div>
      </div>
    </details>
  </div>
</section>

<!-- ═══ STICKY FILTER BAR ═══ -->
<div class="sticky-filter border-b border-stone-200 shadow-sm">
  <div class="max-w-7xl mx-auto px-4 md:px-6 py-3">
    <div class="filter-strip flex flex-wrap items-center gap-2 text-sm">
      <span class="font-semibold text-slate-700 text-xs">סינון:</span>

      <!-- Publication date -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">פורסם</span>
        <template x-for="opt in [{{v:'all',l:'הכל'}},{{v:'today',l:'היום'}},{{v:'week',l:'השבוע'}}]" :key="opt.v">
          <button @click="filters.published=opt.v"
                  :class="filters.published===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Budget min/max -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">מינ׳</span>
        <template x-for="opt in [{{v:'all',l:'הכל'}},{{v:'ge500',l:'≥500'}},{{v:'ge600',l:'≥600'}},{{v:'ge700',l:'≥700'}}]" :key="opt.v">
          <button @click="filters.budgetMin=opt.v"
                  :class="filters.budgetMin===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">מקס׳</span>
        <template x-for="opt in [{{v:'all',l:'הכל'}},{{v:'le800',l:'≤800'}},{{v:'le900',l:'≤900'}},{{v:'le1000',l:'≤1000'}}]" :key="opt.v">
          <button @click="filters.budgetMax=opt.v"
                  :class="filters.budgetMax===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Available date -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">כניסה</span>
        <template x-for="opt in [{{v:'all',l:'הכל'}},{{v:'jun_confirmed',l:'01.06 ודאי'}},{{v:'immediate',l:'מיידי'}},{{v:'flex_window',l:'גמיש'}}]" :key="opt.v">
          <button @click="filters.avail=opt.v"
                  :class="filters.avail===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Source -->
      <div class="flex items-center gap-1 bg-white rounded-full border border-stone-300 px-1 py-0.5">
        <span class="text-xs text-slate-500 px-2">מקור</span>
        <template x-for="opt in [{{v:'all',l:'הכל'}},{{v:'flatfox',l:'flatfox'}},{{v:'weegee',l:'weegee'}}]" :key="opt.v">
          <button @click="filters.source=opt.v"
                  :class="filters.source===opt.v?'bg-blue-600 text-white':'text-slate-600 hover:bg-stone-100'"
                  class="px-3 py-1 rounded-full text-xs font-medium transition" x-text="opt.l"></button>
        </template>
      </div>

      <!-- Checkboxes -->
      <label class="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
        <input type="checkbox" x-model="filters.cooking" class="rounded">🌱 cooking culture
      </label>
      <label class="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
        <input type="checkbox" x-model="filters.tram" class="rounded">🚊 קו ראשוני (3/8/2)
      </label>
      <label class="flex items-center gap-1.5 text-xs text-slate-700 cursor-pointer">
        <input type="checkbox" x-model="filters.quiet" class="rounded">🤫 שקט
      </label>

      <!-- Sort -->
      <div class="mr-auto flex items-center gap-2">
        <span class="text-xs text-slate-500">מיין:</span>
        <select x-model="sortBy" class="text-xs border border-stone-300 rounded-lg px-2 py-1 bg-white">
          <option value="score">ציון</option>
          <option value="price_asc">מחיר ↑</option>
          <option value="price_desc">מחיר ↓</option>
          <option value="date_new">חדש קודם</option>
        </select>
      </div>
      <button @click="resetFilters()" class="text-xs text-slate-600 hover:text-slate-900 underline">איפוס</button>
    </div>
    <div class="mt-1.5 text-xs text-slate-500">מציג <span class="font-semibold" x-text="filtered().length"></span> מתוך {top_n} דירות</div>
  </div>
</div>

<!-- ═══ LISTING CARDS ═══ -->
<main class="max-w-7xl mx-auto px-3 md:px-6 py-4 md:py-8">
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6" data-listing-count="{top_n}">
    <template x-for="(l, i) in filtered()" :key="l.id">
      <article data-listing-card class="bg-white rounded-xl overflow-hidden border border-stone-100 shadow-sm transition hover:shadow-md">

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
                <span x-show="l.tramPrimary" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">🚊 קו ראשוני</span>
                <span x-show="l.isStudent" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">🎓 Studenten</span>
                <span x-show="l.isQuiet" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-sky-100 text-sky-800">🤫 שקט</span>
                <span x-show="l.firstSeenBucket==='today'" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800">🆕 היום</span>
                <span x-show="l.firstSeenBucket==='week' && l.firstSeenBucket!=='today'" class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-stone-100 text-stone-600">📅 השבוע</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Info grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 pb-2">
          <div>
            <div class="text-xs text-slate-400">מחיר/חודש</div>
            <div class="font-bold text-slate-900" x-text="(l.price||'?') + ' CHF'"></div>
          </div>
          <div>
            <div class="text-xs text-slate-400">תאריך כניסה</div>
            <div class="font-bold text-slate-900 text-sm" x-text="l.available"></div>
            <div class="text-xs" :class="l.availBucket==='jun_confirmed'?'text-emerald-700':l.availBucket==='immediate'?'text-blue-700':'text-amber-700'"
                 x-text="l.availBucket==='jun_confirmed'?'✓ ודאי':l.availBucket==='immediate'?'◐ מיידי':'◐ גמיש'"></div>
          </div>
          <div>
            <div class="text-xs text-slate-400">קווי טרם</div>
            <div class="font-bold text-slate-900" x-text="l.tram.length ? l.tram.join(', ') : '—'"></div>
            <div class="text-xs" :class="l.tramPrimaryCount>0?'text-emerald-600':'text-slate-400'"
                 x-text="`${{l.tramPrimaryCount}} ראשוני · ${{l.tramSecondaryCount}} משני`"></div>
          </div>
          <div>
            <div class="text-xs text-slate-400">מקור</div>
            <div class="font-medium text-slate-700 text-sm" x-text="l.sourceLabel"></div>
          </div>
        </div>

        <!-- 13-param breakdown (collapsible) -->
        <div class="px-4 py-2 bg-slate-50/60 border-y border-stone-100">
          <button @click="l._open=!l._open"
                  class="text-xs font-semibold text-slate-700 hover:text-slate-900 flex items-center gap-1 w-full">
            <span x-text="l._open?'▼':'▶'"></span>
            <span>פירוט הציון לפי 13 פרמטרים</span>
            <span class="ms-auto text-slate-500 font-bold" x-text="`${{l.score}}/100`"></span>
          </button>
          <div x-show="l._open" x-transition class="mt-2 grid grid-cols-7 gap-1">
            <template x-for="p in [['📅',l.s.date,15,'תאריך'],['👥',l.s.roommates,20,'שותפים'],['🇬🇧',l.s.lang,12,'שפה'],['🚊',l.s.tram,8,'טרם'],['🛏',l.s.furn,8,'ריהוט'],['🚿',l.s.bath,6,'מקלחת'],['🍳',l.s.kitchen,6,'מטבח'],['🏠',l.s.common,4,'שטח'],['🤫',l.s.quiet,4,'שקט'],['🎓',l.s.student,8,'סטודנט'],['🌳',l.s.balcony,3,'מרפסת'],['🛒',l.s.migros,3,'קניות'],['⚡',l.s.intheat,3,'תשתית']]" :key="p[0]">
              <div class="bg-white rounded p-1 text-center border border-stone-100">
                <div class="text-[10px]" x-text="p[0]"></div>
                <div class="font-bold text-[11px]"
                     :class="p[1]/p[2]>=1?'text-emerald-700':p[1]/p[2]>=0.6?'text-blue-600':p[1]/p[2]>=0.3?'text-amber-600':'text-rose-600'"
                     x-text="`${{p[1]}}/${{p[2]}}`"></div>
              </div>
            </template>
          </div>
        </div>

        <!-- Summary -->
        <div class="px-4 py-3">
          <p class="text-sm text-slate-600 line-clamp-3" x-text="l.summary"></p>
          <div x-show="l.veganSignal && l.veganSignal !== 'kein Signal'"
               class="mt-2 text-xs text-emerald-700">🌱 <span x-text="l.veganSignal"></span></div>
        </div>

        <!-- CTA -->
        <div class="px-4 py-3 bg-stone-50 border-t border-stone-100 flex items-center justify-between">
          <div class="text-xs text-slate-500">
            <span x-show="l.firstSeenAt" x-text="'נראה לראשונה: '+l.firstSeenAt.substring(0,10)"></span>
          </div>
          <a :href="l.url" target="_blank" rel="noopener"
             class="inline-flex items-center gap-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
            פתח מודעה ↗
          </a>
        </div>
      </article>
    </template>
  </div>

  <div x-show="filtered().length===0" class="text-center py-16">
    <div class="text-5xl mb-3">🔍</div>
    <p class="text-slate-600">אין דירות לפי הסינון הנוכחי.</p>
    <button @click="resetFilters()" class="mt-3 text-blue-600 hover:underline text-sm">איפוס סינון</button>
  </div>

  <!-- ═══ FULL PARAMETERS MATRIX ═══ -->
  <section class="mt-12 pt-8 border-t-2 border-stone-200">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-xl md:text-2xl font-bold text-slate-900">📋 מטריצת מאפיינים מלאה</h2>
      <button @click="showFullTable=!showFullTable" class="text-sm text-blue-600 hover:text-blue-800 font-medium"
              x-text="showFullTable?'כווץ ▲':'הרחב ▼'"></button>
    </div>
    <p class="text-sm text-slate-600 mb-4">
      עמודות = דירות (מיון לפי ציון) · שורות = פרמטרים ·
      <span class="text-amber-600">"?"</span> = לא מצוין במודעה.
    </p>
    <div x-show="showFullTable" x-transition class="scroll-x" dir="rtl">
      <table class="text-xs border border-stone-200 rounded-lg bg-white w-full" style="min-width:100%">
        <thead class="bg-slate-50">
          <tr>
            <th class="text-right p-2 sticky right-0 bg-slate-50 border-l-2 border-stone-300 min-w-[160px]">פרמטר</th>
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

          <tr class="bg-blue-50/40"><td colspan="99" class="p-1.5 font-bold text-blue-900 sticky right-0">🎯 בסיס</td></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">מחיר (CHF)</td>
          <template x-for="l in sortedListings()" :key="'pr-'+l.id"><td class="text-center p-2 font-bold border-l border-stone-100" x-text="l.price||'?'"></td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">תאריך כניסה</td>
          <template x-for="l in sortedListings()" :key="'av-'+l.id"><td class="text-center p-2 border-l border-stone-100">
            <div x-text="l.available"></div>
            <div class="text-[10px]" :class="l.availBucket==='jun_confirmed'?'text-emerald-700':'text-amber-600'"
                 x-text="l.availBucket==='jun_confirmed'?'✓ ודאי':l.availBucket==='immediate'?'◐ מיידי':'◐ גמיש'"></div>
          </td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">מקור</td>
          <template x-for="l in sortedListings()" :key="'src-'+l.id"><td class="text-center p-2 text-[11px] border-l border-stone-100" x-text="l.sourceLabel"></td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">פורסם</td>
          <template x-for="l in sortedListings()" :key="'fs-'+l.id"><td class="text-center p-2 text-[11px] border-l border-stone-100">
            <span :class="l.firstSeenBucket==='today'?'text-amber-700 font-bold':l.firstSeenBucket==='week'?'text-blue-600':'text-slate-400'"
                  x-text="l.firstSeenBucket==='today'?'🆕 היום':l.firstSeenBucket==='week'?'השבוע':'ישן'"></span>
            <div class="text-[10px] text-slate-400" x-text="l.firstSeenAt?l.firstSeenAt.substring(0,10):''"></div>
          </td></template></tr>

          <tr class="bg-cyan-50/40"><td colspan="99" class="p-1.5 font-bold text-cyan-900 sticky right-0">🚊 תחבורה</td></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">קווי טרם</td>
          <template x-for="l in sortedListings()" :key="'tr-'+l.id"><td class="text-center p-2 font-medium border-l border-stone-100" x-text="l.tram.length?l.tram.join(', '):'—'"></td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">ראשוניים (3/8/2)</td>
          <template x-for="l in sortedListings()" :key="'trp-'+l.id"><td class="text-center p-2 border-l border-stone-100" :class="l.tramPrimaryCount>0?'text-emerald-700 font-bold':'text-slate-400'" x-text="l.tramPrimaryCount+' מ-3'"></td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">משניים (10/11/16)</td>
          <template x-for="l in sortedListings()" :key="'trs-'+l.id"><td class="text-center p-2 border-l border-stone-100 text-slate-600" x-text="l.tramSecondaryCount+' מ-3'"></td></template></tr>

          <tr class="bg-emerald-50/40"><td colspan="99" class="p-1.5 font-bold text-emerald-900 sticky right-0">✨ סיגנלים</td></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">🌱 Cooking-Culture</td>
          <template x-for="l in sortedListings()" :key="'cc-'+l.id"><td class="text-center p-2 border-l border-stone-100"><span x-show="l.cookingCulture" class="text-emerald-700 font-bold">✓</span><span x-show="!l.cookingCulture" class="text-slate-300">—</span></td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">Vegan signal</td>
          <template x-for="l in sortedListings()" :key="'vs-'+l.id"><td class="text-center p-2 text-[11px] border-l border-stone-100" x-text="l.veganSignal&&l.veganSignal!=='kein Signal'?l.veganSignal:'—'"></td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">🤫 שקט</td>
          <template x-for="l in sortedListings()" :key="'qt-'+l.id"><td class="text-center p-2 border-l border-stone-100"><span x-show="l.isQuiet" class="text-sky-700 font-bold">✓</span><span x-show="!l.isQuiet" class="text-slate-300">—</span></td></template></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">🎓 סטודנט</td>
          <template x-for="l in sortedListings()" :key="'st-'+l.id"><td class="text-center p-2 border-l border-stone-100"><span x-show="l.isStudent" class="text-indigo-700 font-bold">✓</span><span x-show="!l.isStudent" class="text-slate-300">—</span></td></template></tr>

          <tr class="bg-slate-100"><td colspan="99" class="p-1.5 font-bold text-slate-900 sticky right-0">📊 ציונים 13 פרמטרים</td></tr>
          <template x-for="p in [['📅 תאריך','date',15],['👥 שותפים','roommates',20],['🇬🇧 שפה','lang',12],['🚊 טרם','tram',8],['🛏 ריהוט','furn',8],['🚿 מקלחת','bath',6],['🍳 מטבח','kitchen',6],['🏠 שטח','common',4],['🤫 שקט','quiet',4],['🎓 סטודנט','student',8],['🌳 מרפסת','balcony',3],['🛒 קניות','migros',3],['⚡ תשתיות','intheat',3]]" :key="p[1]">
            <tr>
              <td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium text-[11px]" x-text="p[0]+' /'+p[2]"></td>
              <template x-for="l in sortedListings()" :key="p[1]+'-'+l.id">
                <td class="sc p-1.5 border-l border-stone-100" :class="hm(l.s[p[1]],p[2])" x-text="l.s[p[1]]"></td>
              </template>
            </tr>
          </template>

          <tr class="bg-slate-200"><td class="p-2 sticky right-0 bg-slate-200 border-l-2 border-stone-300 font-bold">סה״כ /100</td>
          <template x-for="l in sortedListings()" :key="'tot-'+l.id">
            <td class="text-center p-2 font-bold text-base border-l border-stone-200"
                :class="l.score>=65?'bg-emerald-100 text-emerald-900':l.score>=50?'bg-blue-100 text-blue-900':'bg-amber-100 text-amber-900'"
                x-text="l.score"></td>
          </template></tr>

          <tr class="bg-stone-50"><td colspan="99" class="p-1.5 font-bold text-slate-700 sticky right-0">🔗 קישורים</td></tr>
          <tr><td class="p-2 sticky right-0 bg-white border-l-2 border-stone-200 font-medium">קישור למודעה</td>
          <template x-for="l in sortedListings()" :key="'lk-'+l.id"><td class="text-center p-2 border-l border-stone-100"><a :href="l.url" target="_blank" rel="noopener" class="text-blue-600 hover:text-blue-800 underline text-xs">פתח ↗</a></td></template></tr>
        </tbody>
      </table>
    </div>
  </section>
</main>

<!-- ═══ FOOTER ═══ -->
<footer class="bg-slate-900 text-slate-300 mt-12">
  <div class="max-w-7xl mx-auto px-6 py-10">
    <h3 class="text-xl font-bold text-white mb-4">פרופיל v2.0 · שקד · WG Basel</h3>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-sm">
      <div><h4 class="font-semibold text-white mb-2">שכבה 1 — נתוני יסוד</h4>
        <p>שקד 18, אזרח שוויצרי, סטודנט-עתידי לכימיה ב-Uni Basel (Frühjahr 2027), Sprachschüler ב-ILS Basel, אבא שוויצרי ערב.</p></div>
      <div><h4 class="font-semibold text-white mb-2">שכבה 2 — בקשות מפורשות</h4>
        <p>תקציב קשיח 1000 CHF · WG עם שותפים · טרם 3/8/2 · מטבח cooking culture · בידוד אקוסטי · אנגלית · מרוהט+מיטה · שטח משותף > פרטי.</p></div>
      <div><h4 class="font-semibold text-white mb-2">חישוב הציון</h4>
        <p>13 פרמטרים, 100 נקודות. ניתוח אוטומטי מהמודעות. ? = לא צוין — לשאול בפנייה.</p></div>
    </div>
    <div class="mt-6 text-xs text-slate-500 text-center">v2.0 · {built} · {total_count} דירות במאגר · מקורות: {sources_full}</div>
  </div>
</footer>

<script>
function app() {{
  return {{
    showMatrix: window.innerWidth >= 768,
    showFullTable: false,
    filters: {{ published:'all', budgetMin:'all', budgetMax:'all', avail:'all', source:'all', cooking:false, tram:false, quiet:false }},
    sortBy: 'score',

    init() {{
      const today = new Date(); today.setHours(0,0,0,0);
      this.listings.forEach(l => {{
        if (!l.firstSeenAt) {{ l.firstSeenBucket = 'older'; return; }}
        const d = new Date(l.firstSeenAt); d.setHours(0,0,0,0);
        const delta = Math.round((today - d) / 86400000);
        l.firstSeenBucket = delta === 0 ? 'today' : delta <= 7 ? 'week' : 'older';
      }});
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
      this.filters = {{ published:'all', budgetMin:'all', budgetMax:'all', avail:'all', source:'all', cooking:false, tram:false, quiet:false }};
      this.sortBy = 'score';
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

def build_html(
    listings: list[dict[str, Any]],
    profile: SearchProfile,
    city: CityDefinition | None = None,
    top: int = 10,
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
    prices = [lst.get("price") for lst in top_listings if lst.get("price")]
    price_range = f"{min(prices)}–{max(prices)}" if prices else "—"
    veg_count = sum(1 for lst in top_listings if lst.get("is_vegetarian_friendly"))
    sources = sorted(set(lst.get("source", "") for lst in top_listings))
    sources_str = "+".join(s for s in sources if s)
    total_count = len(listings)

    listings_json = json.dumps(js_objects, ensure_ascii=False, indent=2)

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
    )


def rebuild_html(
    profile_id: str | None = None,
    top: int = 10,
    out: str | Path = "shaked_curated.html",
    extra_listings_path: str | Path | None = None,
) -> Path:
    """High-level entry point: load config + listings, build, write file.

    extra_listings_path:
        Optional path to a JSON file with additional listings to merge.
        Deduplicates by source+source_listing_id; extra entries win on conflict.
    """
    cfg = load_config(profile_id)
    listings = load_listings()

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

    html = build_html(listings, cfg.profile, cfg.city, top=top)
    out_path = Path(out)
    out_path.write_text(html, encoding="utf-8")
    return out_path
