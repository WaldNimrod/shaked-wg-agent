"""One-click curated HTML builder — v1.9 structure.

Reads data/listings.json, re-scores with the canonical scorer, and emits a
static HTML5 page that reproduces the major sections of
data/shaked_curated_2026-05-01.html:

  1. Header (title, stats strip, profile summary)
  2. Score-matrix table (all top-N listings × 7 score components)
  3. Filter bar (static, no JS framework required)
  4. Listing cards (top-N, data-driven)
  5. Footer

Cooking-culture badge (🌱) is rendered when listing.is_vegetarian_friendly is True.
Uses only the Python standard library — no Jinja2 required.
"""
from __future__ import annotations

import html as _html
from datetime import date
from pathlib import Path
from typing import Any

from shaked_wg_agent.config import CityDefinition, SearchProfile, load_config
from shaked_wg_agent.persistence import load_listings
from shaked_wg_agent.publisher.scoring_v18 import score_top_n

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CSS = """\
<style>
  body { font-family: -apple-system, "Segoe UI", "Helvetica Neue", "Arial Hebrew", sans-serif;
         -webkit-font-smoothing: antialiased; background: #fafaf9; color: #1c1917; }
  .score-ring { background: conic-gradient(var(--c) calc(var(--p)*1%), #e5e7eb 0);
                border-radius: 50%; }
  .heatmap-1 { background: #fee2e2; color: #991b1b; }
  .heatmap-2 { background: #fed7aa; color: #9a3412; }
  .heatmap-3 { background: #fef3c7; color: #92400e; }
  .heatmap-4 { background: #d9f99d; color: #3f6212; }
  .heatmap-5 { background: #a7f3d0; color: #065f46; }
  .heatmap-max { background: #6ee7b7; color: #064e3b; }
  .matrix table { font-variant-numeric: tabular-nums; border-collapse: collapse; }
  .matrix td, .matrix th { padding: 6px 10px; border: 1px solid #e2e8f0; }
  .matrix td.scorecell { text-align: center; font-weight: 600; }
  .matrix td.total { background: #f1f5f9; font-weight: 700; text-align: center; }
  .scroll-x { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .card { background: #fff; border-radius: 12px;
          box-shadow: 0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
          margin-bottom: 16px; overflow: hidden; }
  .card-header { padding: 16px 20px 12px; border-bottom: 1px solid #f1f5f9; }
  .card-body { padding: 16px 20px; }
  .badge { display: inline-flex; align-items: center; padding: 2px 8px;
           border-radius: 9999px; font-size: 11px; font-weight: 600; }
  .badge-green { background: #d1fae5; color: #065f46; }
  .badge-blue { background: #dbeafe; color: #1e40af; }
  .badge-purple { background: #ede9fe; color: #5b21b6; }
  .badge-amber { background: #fef3c7; color: #92400e; }
  .badge-cooking { background: #bbf7d0; color: #14532d;
                   border: 2px solid rgba(34,197,94,.4); font-weight: 700; }
  .score-bar { display: flex; align-items: center; gap: 6px; }
  .score-bar .bar { flex: 1; height: 6px; background: #e5e7eb; border-radius: 3px; }
  .score-bar .fill { height: 100%; border-radius: 3px; }
  .filter-bar { background: rgba(250,250,247,.94); border-bottom: 1px solid #e2e8f0;
                padding: 12px 24px; display: flex; flex-wrap: wrap; gap: 8px;
                align-items: center; position: sticky; top: 0; z-index: 40;
                backdrop-filter: blur(8px); }
  header { background: linear-gradient(to left, #1d4ed8, #1e3a8a); color: #fff;
           padding: 32px 24px; }
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
                margin-top: 20px; }
  @media (max-width: 640px) {
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
  }
  .stat-box { background: rgba(255,255,255,.1); border-radius: 8px; padding: 10px 12px; }
  .cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
                gap: 20px; padding: 24px; max-width: 1280px; margin: 0 auto; }
  @media (max-width: 480px) { .cards-grid { grid-template-columns: 1fr; padding: 12px; } }
  .section { max-width: 1280px; margin: 0 auto; padding: 24px; }
  .cta-btn { display: inline-flex; align-items: center; padding: 10px 20px;
             background: #2563eb; color: #fff; border-radius: 8px; text-decoration: none;
             font-weight: 600; font-size: 14px; }
  .cta-btn:hover { background: #1d4ed8; }
  footer { text-align: center; padding: 32px 16px; color: #94a3b8; font-size: 13px; }
</style>
"""


def _esc(val: Any) -> str:
    return _html.escape(str(val)) if val else ""


def _heatmap_cls(val: int, max_val: int) -> str:
    """Return heatmap CSS class based on fraction of max."""
    if max_val <= 0:
        return ""
    pct = val / max_val
    if pct >= 1.0:
        return "heatmap-max"
    if pct >= 0.8:
        return "heatmap-5"
    if pct >= 0.6:
        return "heatmap-4"
    if pct >= 0.4:
        return "heatmap-3"
    if pct >= 0.2:
        return "heatmap-2"
    return "heatmap-1"


def _score_bar_html(score: int) -> str:
    cls = "#059669" if score >= 65 else "#2563eb" if score >= 50 else "#b45309"
    return (
        f'<div class="score-bar">'
        f'<div class="bar"><div class="fill" style="width:{score}%;background:{cls}"></div></div>'
        f'<strong style="min-width:28px;text-align:right">{score}</strong>'
        f"</div>"
    )


def _price(lst: dict[str, Any]) -> int | None:
    p = lst.get("price")
    if p is None:
        p = lst.get("price_chf")
    return p


def _transit_lines(lst: dict[str, Any]) -> list[str]:
    raw = lst.get("transit_match_lines") or lst.get("tram_match_lines") or []
    return list(raw)


# ---------------------------------------------------------------------------
# Score breakdown helpers (map scorer fields to matrix columns)
# ---------------------------------------------------------------------------

def _breakdown(lst: dict[str, Any]) -> dict[str, int]:
    """Extract per-component scores from a scored listing.

    The canonical scorer stores the aggregate in relevance_score only.
    We reconstruct component breakdowns from listing fields so the matrix
    remains informative without duplicating scorer logic.
    """
    from shaked_wg_agent.scorer import (  # noqa: PLC0415
        _available_score,
        _freshness_score,
        _roommate_score,
        _transit_score,
        _url_score,
        _vegan_score,
    )

    lines = _transit_lines(lst)
    # We can't access the profile here; use stored transit_match_lines.
    # For the matrix we show the raw sub-scores as stored in the listing.
    # Use profile transit lines stored on the listing if available, else []
    preferred = lst.get("_profile_transit_lines") or []

    vegan = min(35, _vegan_score(lst.get("vegan_signal", ""), lst.get("country", "CH"))
                + (2 if lst.get("is_vegetarian_friendly") else 0))
    transit = _transit_score(lines, preferred)
    roommate = min(15, _roommate_score(lst.get("roommate_signal", ""), "young")
                   + (1 if lst.get("is_quiet_friendly") else 0))
    freshness = _freshness_score(lst.get("posted_date"), lst.get("first_seen_at"))
    available = _available_score(lst.get("available_from"), "2026-06-01")
    url = _url_score(lst.get("url_status", ""))
    total = lst.get("relevance_score", 0)

    return {
        "vegan": vegan,
        "transit": transit,
        "roommates": roommate,
        "freshness": freshness,
        "available": available,
        "url": url,
        "total": total,
    }


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_header(listings: list[dict[str, Any]], top: int, built: str) -> str:
    total = len(listings)
    prices = [p for lst in listings if (p := _price(lst)) is not None]
    price_range = f"{min(prices)}–{max(prices)}" if prices else "—"
    veg_count = sum(1 for lst in listings if lst.get("is_vegetarian_friendly"))

    return f"""
<header>
  <div style="max-width:1280px;margin:0 auto">
    <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:8px">
      <h1 style="font-size:clamp(1.4rem,3vw,2rem);font-weight:700;margin:0">
        {top} דירות לשקד · באזל
      </h1>
      <span style="color:#bfdbfe;font-size:13px">v1.9 · {built}</span>
    </div>
    <p style="color:#bfdbfe;font-size:15px;max-width:700px;margin:0">
      WG ארוך-טווח · כניסה 01.06.2026 · תקציב <strong>≤ 1000 CHF</strong> ·
      אזרח שוויצרי בן 18, סטודנט עתידי כימיה Uni Basel · ILS Basel ·
      אנגלית מועדפת · <strong>טבעוני</strong>
    </p>
    <div style="margin-top:12px;background:rgba(6,95,70,.4);border:1px solid rgba(52,211,153,.4);
                border-radius:8px;padding:10px 14px;font-size:13px;color:#a7f3d0">
      <strong>🌱 מטבח צמחוני / טבעוני</strong> = יתרון משמעותי. מסומן בבירור על כרטיסים כשנמצא.
    </div>
    <div class="stats-grid">
      <div class="stat-box">
        <div style="font-size:10px;color:#bfdbfe">מאומתות חיות</div>
        <div style="font-size:24px;font-weight:700">{total}/{top}</div>
      </div>
      <div class="stat-box">
        <div style="font-size:10px;color:#bfdbfe">טווח מחיר</div>
        <div style="font-size:24px;font-weight:700">{price_range}</div>
      </div>
      <div class="stat-box">
        <div style="font-size:10px;color:#bfdbfe">בנוי</div>
        <div style="font-size:24px;font-weight:700">{built}</div>
      </div>
      <div class="stat-box">
        <div style="font-size:10px;color:#bfdbfe">🌱 צמחוני</div>
        <div style="font-size:24px;font-weight:700">{veg_count}</div>
      </div>
    </div>
  </div>
</header>"""


def _render_matrix(listings: list[dict[str, Any]]) -> str:
    """Render the score-comparison matrix table."""
    rows = []
    for lst in listings:
        bd = _breakdown(lst)
        title = _esc(lst.get("title", "")[:50])
        url = _esc(lst.get("direct_url") or lst.get("source_search_url") or "#")
        loc = _esc(lst.get("district") or lst.get("location_text") or "")

        def _cell(breakdown: dict[str, int], key: str, mx: int) -> str:
            v = breakdown[key]
            cls = _heatmap_cls(v, mx)
            return f'<td class="scorecell {cls}">{v}</td>'

        rows.append(
            f'<tr>'
            f'<td style="text-align:right;white-space:nowrap;font-size:11px">'
            f'<a href="{url}" target="_blank" style="font-weight:600;color:#1e40af">{title}</a>'
            f'<div style="color:#64748b;font-size:10px">{loc}</div></td>'
            + _cell(bd, "vegan", 35)
            + _cell(bd, "transit", 25)
            + _cell(bd, "roommates", 15)
            + _cell(bd, "freshness", 15)
            + _cell(bd, "available", 10)
            + _cell(bd, "url", 10)
            + f'<td class="total scorecell">{bd["total"]}</td>'
            + "</tr>"
        )

    rows_html = "\n".join(rows)
    return f"""
<section class="section">
  <h2 style="font-size:1.4rem;font-weight:700;margin-bottom:8px">
    📊 טבלת השוואת ציונים — רכיבי הניקוד
  </h2>
  <p style="font-size:13px;color:#64748b;margin-bottom:12px">
    כל ציון = סכום רכיבי הניקוד. תאי הטבלה צבועים לפי אחוז המקסימום שכל רכיב השיג.
  </p>
  <div class="matrix scroll-x">
    <table style="min-width:760px;width:100%;font-size:12px">
      <thead style="background:#f8fafc">
        <tr>
          <th style="text-align:right;min-width:180px;padding:8px 10px">דירה</th>
          <th style="text-align:center;padding:8px 6px">🌱<br>טבעוני<br><span style="color:#94a3b8;font-size:10px">/35</span></th>
          <th style="text-align:center;padding:8px 6px">🚊<br>טרם<br><span style="color:#94a3b8;font-size:10px">/25</span></th>
          <th style="text-align:center;padding:8px 6px">👥<br>שותפים<br><span style="color:#94a3b8;font-size:10px">/15</span></th>
          <th style="text-align:center;padding:8px 6px">🕐<br>רעננות<br><span style="color:#94a3b8;font-size:10px">/15</span></th>
          <th style="text-align:center;padding:8px 6px">📅<br>תאריך<br><span style="color:#94a3b8;font-size:10px">/10</span></th>
          <th style="text-align:center;padding:8px 6px">🔗<br>קישור<br><span style="color:#94a3b8;font-size:10px">/10</span></th>
          <th style="text-align:center;padding:8px 6px;background:#f1f5f9">סה״כ<br><span style="color:#94a3b8;font-size:10px">/100</span></th>
        </tr>
      </thead>
      <tbody id="score-matrix-tbody">
{rows_html}
      </tbody>
    </table>
  </div>
</section>"""


def _render_filter_bar() -> str:
    return """
<div class="filter-bar" dir="rtl">
  <span style="font-weight:600;font-size:13px;color:#374151">סינון:</span>
  <div style="display:flex;align-items:center;gap:4px;background:#fff;border-radius:9999px;border:1px solid #d1d5db;padding:2px 4px">
    <span style="font-size:11px;color:#6b7280;padding:0 8px">תאריך</span>
    <button onclick="void(0)" style="padding:3px 12px;border-radius:9999px;border:none;background:#2563eb;color:#fff;font-size:11px;cursor:pointer">הכל</button>
    <button onclick="void(0)" style="padding:3px 12px;border-radius:9999px;border:none;background:none;color:#374151;font-size:11px;cursor:pointer">01.06 ודאי</button>
  </div>
  <div style="display:flex;align-items:center;gap:4px;background:#fff;border-radius:9999px;border:1px solid #d1d5db;padding:2px 4px">
    <span style="font-size:11px;color:#6b7280;padding:0 8px">תקציב</span>
    <button onclick="void(0)" style="padding:3px 12px;border-radius:9999px;border:none;background:#2563eb;color:#fff;font-size:11px;cursor:pointer">הכל</button>
    <button onclick="void(0)" style="padding:3px 12px;border-radius:9999px;border:none;background:none;color:#374151;font-size:11px;cursor:pointer">≤800</button>
    <button onclick="void(0)" style="padding:3px 12px;border-radius:9999px;border:none;background:none;color:#374151;font-size:11px;cursor:pointer">≤1000</button>
  </div>
  <span style="font-size:12px;color:#6b7280;margin-right:auto">מציג <strong id="visible-count">—</strong> דירות</span>
</div>"""


def _render_card(lst: dict[str, Any], rank: int) -> str:
    """Render a single listing card."""
    title = _esc(lst.get("title") or "")
    district = _esc(lst.get("district") or lst.get("location_text") or "")
    price = _price(lst)
    price_str = f"{price} CHF" if price else "—"
    score = lst.get("relevance_score", 0)
    url = _esc(lst.get("direct_url") or lst.get("source_search_url") or "#")
    avail = _esc(lst.get("available_from") or "")
    summary = _esc((lst.get("summary") or "")[:200])
    lines = _transit_lines(lst)
    lines_str = ", ".join(str(x) for x in lines) if lines else "—"
    vegan_signal = lst.get("vegan_signal") or ""
    is_veg = lst.get("is_vegetarian_friendly", False)

    # Score ring color
    ring_color = "#059669" if score >= 65 else "#2563eb" if score >= 50 else "#b45309"
    text_cls = "color:#059669" if score >= 65 else "color:#1d4ed8" if score >= 50 else "color:#b45309"

    # Badges
    badges = []
    if is_veg:
        badges.append('<span class="badge badge-cooking">🌱 Cooking-Culture</span>')
    if lines:
        badges.append('<span class="badge badge-green">🚊 טרם</span>')
    if lst.get("is_student_oriented"):
        badges.append('<span class="badge badge-purple">🎓 Studenten</span>')
    if vegan_signal and "vegan" in vegan_signal.lower():
        badges.append('<span class="badge badge-green">🌿 טבעוני</span>')

    badges_html = " ".join(badges)

    vegan_row = ""
    if vegan_signal:
        vegan_row = f'<div style="font-size:12px;color:#059669;margin-top:4px">🌱 {_esc(vegan_signal[:60])}</div>'

    summary_row = ""
    if summary:
        summary_row = f'<p style="font-size:13px;color:#64748b;margin:8px 0 0;line-height:1.5">{summary}…</p>'

    return f"""
<article class="card" data-score="{score}" data-price="{price or 0}" data-listing-card>
  <div class="card-header">
    <div style="display:flex;align-items:flex-start;gap:16px">
      <!-- Score ring -->
      <div class="score-ring" style="--p:{score};--c:{ring_color};width:56px;height:56px;
           flex-shrink:0;display:flex;align-items:center;justify-content:center">
        <div style="width:44px;height:44px;background:#fff;border-radius:50%;
                    display:flex;align-items:center;justify-content:center">
          <span style="font-weight:700;font-size:18px;{text_cls}">{score}</span>
        </div>
      </div>
      <div style="flex:1;min-width:0">
        <div style="display:flex;align-items:baseline;gap:8px;margin-bottom:4px">
          <span style="font-size:11px;font-weight:600;color:#94a3b8">#{rank}</span>
          <h2 style="font-weight:700;font-size:17px;color:#0f172a;margin:0;
                     white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{title}</h2>
        </div>
        <div style="font-size:13px;color:#475569">{district}</div>
        <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:6px">{badges_html}</div>
      </div>
    </div>
  </div>
  <div class="card-body">
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:12px">
      <div>
        <div style="font-size:11px;color:#94a3b8">מחיר/חודש</div>
        <div style="font-weight:700;font-size:16px">{price_str}</div>
      </div>
      <div>
        <div style="font-size:11px;color:#94a3b8">תאריך כניסה</div>
        <div style="font-weight:700;font-size:15px">{avail or "—"}</div>
      </div>
      <div>
        <div style="font-size:11px;color:#94a3b8">קווי טרם</div>
        <div style="font-weight:700;font-size:15px">{lines_str}</div>
      </div>
    </div>
    {vegan_row}
    {summary_row}
    <div style="margin-top:16px;border-top:1px solid #f1f5f9;padding-top:12px;
                display:flex;justify-content:space-between;align-items:center">
      {_score_bar_html(score)}
      <a href="{url}" target="_blank" rel="noopener" class="cta-btn" style="margin-right:12px">
        פתח מודעה ↗
      </a>
    </div>
  </div>
</article>"""


def _render_listings_section(listings: list[dict[str, Any]]) -> str:
    cards = "".join(_render_card(lst, i + 1) for i, lst in enumerate(listings))
    return f"""
<section style="max-width:1280px;margin:0 auto;padding:24px" id="listings-section">
  <h2 style="font-size:1.5rem;font-weight:700;margin-bottom:20px">
    🏠 {len(listings)} הדירות המובילות
  </h2>
  <div class="cards-grid">
{cards}
  </div>
</section>"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_html(
    listings: list[dict[str, Any]],
    profile: SearchProfile,
    city: CityDefinition | None = None,
    top: int = 10,
) -> str:
    """Score, select top-N, and render the curated HTML page.

    Parameters
    ----------
    listings:
        All listings (unsorted; will be scored in-place).
    profile:
        The search profile used for scoring.
    city:
        Optional city definition (used for settlement allowlist).
    top:
        Number of top-scoring listings to include.

    Returns
    -------
    str
        A complete HTML5 document string.
    """
    # Stamp the profile transit lines on each listing so _breakdown() can
    # re-derive the transit sub-score without importing the profile again.
    for lst in listings:
        lst["_profile_transit_lines"] = profile.transit_lines

    top_listings = score_top_n(listings, profile, city, top=top)
    built = date.today().isoformat()

    header = _render_header(top_listings, top, built)
    matrix = _render_matrix(top_listings)
    filter_bar = _render_filter_bar()
    listing_section = _render_listings_section(top_listings)

    total_listings = len(top_listings)

    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>שקד · {top} דירות באזל · WG ארוך-טווח · v1.9 · {built}</title>
<meta name="description" content="{top} דירות מאומתות בבאזל עבור שקד — פרופיל v1.9.">
{_CSS}
</head>
<body>

{header}

{matrix}

{filter_bar}

{listing_section}

<footer>
  <p>נבנה אוטומטית · {built} · {total_listings} דירות מובילות · v1.9</p>
</footer>

<script>
// Update visible count
document.addEventListener('DOMContentLoaded', function() {{
  var cards = document.querySelectorAll('[data-listing-card]');
  var el = document.getElementById('visible-count');
  if (el) el.textContent = cards.length;
}});
</script>
</body>
</html>"""


def rebuild_html(
    profile_id: str | None = None,
    top: int = 10,
    out: str | Path = "shaked_curated.html",
    extra_listings_path: str | Path | None = None,
) -> Path:
    """High-level entry point: load config + listings, build, write file.

    Parameters
    ----------
    profile_id:
        Profile to load (None → uses agent default).
    top:
        Number of top listings to include.
    out:
        Output path for the HTML file.
    extra_listings_path:
        Optional path to a JSON file with additional listings to merge
        (e.g. data/manual_finds_2026-05-05.json). Deduplicates by
        source+source_listing_id; extra entries win on conflict.

    Returns
    -------
    Path
        Resolved path of the written file.
    """
    import json

    cfg = load_config(profile_id)
    listings = load_listings()

    if extra_listings_path is not None:
        extra_path = Path(extra_listings_path)
        extra_raw: list[dict[str, Any]] = json.loads(extra_path.read_text(encoding="utf-8"))
        # Build a dedup index from the base listings
        seen: dict[tuple[str, str], int] = {}
        for idx, lst in enumerate(listings):
            key = (lst.get("source", ""), lst.get("source_listing_id", ""))
            seen[key] = idx
        # Merge extra listings — update in place if key exists, else append
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
