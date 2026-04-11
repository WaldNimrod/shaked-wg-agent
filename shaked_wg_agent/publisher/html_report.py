"""Generate a static HTML report with full-screen listing modals."""
from __future__ import annotations

import html as _html
from datetime import date, datetime
from typing import Any

from shaked_wg_agent import __version__

_STATUS_BADGE = {
    "favorit":     ("success",   "⭐ favorit"),
    "interessant": ("warning",   "interessant"),
    "kontaktiert": ("primary",   "kontaktiert"),
    "neu":         ("secondary", "neu"),
    "abgesagt":    ("danger",    "abgesagt"),
}

# Listing access tier icons and labels
_TIER_DIRECT = ("🔗", "Direktlink", "success", "Direktlink — vollständige Seite direkt erreichbar")
_TIER_LOGIN  = ("🔐", "Login nötig", "warning", "Direktlink vorhanden — kostenloser Account für Kontakt nötig")
_TIER_SEARCH = ("🔍", "Suche nötig", "secondary", "Kein Direktlink — über Suchbegriff auffindbar")
_TIER_BROKEN = ("⚠️", "Offline?", "danger", "URL möglicherweise offline — Recovery-Suche verwenden")


def _tier(lst: dict) -> tuple:
    """Return (icon, label, badge_class, tooltip) for a listing's access tier."""
    url_status = lst.get("url_status", "")
    verified = lst.get("verified_active")
    if url_status == "broken_needs_recovery" or verified is False:
        return _TIER_BROKEN
    if url_status == "direct":
        # flatfox: direct URL but contact requires free platform login
        source = lst.get("source", "")
        if source in ("flatfox", "wg-gesucht"):
            return _TIER_LOGIN
        return _TIER_DIRECT
    if url_status == "search_only":
        return _TIER_SEARCH
    return _TIER_SEARCH


def _badge(status: str) -> str:
    cls, label = _STATUS_BADGE.get(status, ("secondary", status))
    return f'<span class="badge bg-{cls} text-nowrap">{label}</span>'


def _score_bar(score: int) -> str:
    cls = "success" if score >= 85 else "warning" if score >= 65 else "secondary"
    return (
        f'<div class="d-flex align-items-center gap-1">'
        f'<div class="progress flex-grow-1" style="height:6px">'
        f'<div class="progress-bar bg-{cls}" style="width:{score}%"></div></div>'
        f'<small class="fw-semibold">{score}</small></div>'
    )


def _vegan_cell(signal: str) -> str:
    if not signal or signal in ("kein Signal", "unbekannt"):
        return "—" if signal == "kein Signal" else "?"
    return f'<span class="text-success fw-semibold">{_html.escape(signal[:24])}</span>'


def _safe(val: Any, default: str = "—") -> str:
    return _html.escape(str(val)) if val else default


def _modal(lst: dict) -> str:
    """Build a full-screen Bootstrap modal for a listing."""
    lid = lst.get("listing_id", "")
    title = _safe(lst.get("title", ""), "Unbekannt")
    price = lst.get("price_chf")
    district = _safe(lst.get("district", ""))
    location = _safe(lst.get("location_text", ""))
    roommate = _safe(lst.get("roommate_signal", ""))
    vegan = _safe(lst.get("vegan_signal", ""))
    summary = _safe(lst.get("summary", ""))
    note = _safe(lst.get("note", ""))
    available = _safe(lst.get("available_from", ""))
    source = _safe(lst.get("source", ""))
    status = lst.get("status", "neu")
    score = lst.get("relevance_score", 0)
    tags = lst.get("tags", [])
    tram = ", ".join(f"T{t}" for t in lst.get("tram_match_lines", []))
    direct_url = lst.get("direct_url", "")
    source_search_url = lst.get("source_search_url", "")
    recovery_query = lst.get("recovery_query", "") or lst.get("title", "")
    rq_js = recovery_query.replace("'", "\\'").replace('"', '&quot;')

    # Tier
    tier_icon, tier_label, tier_cls, tier_tip = _tier(lst)

    # Verification line
    verified_at = lst.get("last_verified_at", "")
    verified_active = lst.get("verified_active")
    if verified_active is True and verified_at:
        try:
            dt = datetime.fromisoformat(verified_at)
            age_h = round((datetime.now(dt.tzinfo) - dt).total_seconds() / 3600)
            age_str = f"vor {age_h}h" if age_h > 0 else "gerade eben"
        except Exception:
            age_str = verified_at[:10]
        verify_line = f'<span class="text-success small">✓ Geprüft aktiv ({age_str})</span>'
    elif verified_active is False:
        verify_line = '<span class="text-danger small">⚠️ URL möglicherweise offline — bitte Quelle prüfen</span>'
    else:
        verify_line = '<span class="text-muted small">Noch nicht geprüft</span>'

    # Contact section
    contact_href = direct_url or source_search_url
    contact_btn = (
        f'<a href="{_html.escape(contact_href)}" target="_blank" rel="noopener" '
        f'class="btn btn-sm btn-outline-primary">'
        f'Kontakt über {source} ↗</a>'
        if contact_href else ""
    )
    copy_btn = (
        f'<button class="btn btn-sm btn-outline-secondary copy-btn ms-2" '
        f'onclick="copySearch(\'{rq_js}\', this)" '
        f'title="Suchbegriff in Zwischenablage kopieren">📋 Suchbegriff kopieren</button>'
    )
    source_link = (
        f'<a href="{_html.escape(direct_url)}" target="_blank" rel="noopener" '
        f'class="btn btn-sm btn-link text-muted">🔗 Original öffnen</a>'
        if direct_url else ""
    )

    tags_html = " ".join(
        f'<span class="badge bg-light text-dark border me-1">{_html.escape(t)}</span>'
        for t in tags
    )

    return f"""
<div class="modal fade" id="modal-{lid}" tabindex="-1" aria-labelledby="modal-label-{lid}" aria-hidden="true">
  <div class="modal-dialog modal-fullscreen-md-down modal-xl modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header" style="background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff">
        <div class="w-100">
          <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
            <span class="badge bg-{tier_cls} text-white" title="{tier_tip}">{tier_icon} {tier_label}</span>
            {_badge(status)}
            <span class="fw-bold fs-5">{title}</span>
          </div>
          <div class="d-flex gap-3 flex-wrap small opacity-90">
            <span>📍 {district}</span>
            {"<span>💰 CHF " + str(price) + "/Mt.</span>" if price else ""}
            {"<span>🗓 ab " + available + "</span>" if available and available != "—" else ""}
            {"<span>🚃 " + tram + "</span>" if tram else ""}
            <span>📊 Score: <strong>{score}</strong></span>
          </div>
        </div>
        <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <div class="row g-3">
          <div class="col-12 col-md-7">
            {"<p class='mb-2'><strong>📍 Lage:</strong> " + location + "</p>" if location and location != "—" else ""}
            {"<p class='mb-2'><strong>👥 Mitbewohner:</strong> " + roommate + "</p>" if roommate and roommate != "—" else ""}
            {"<p class='mb-2'><strong>🌱 Vegan-Signal:</strong> " + vegan + "</p>" if vegan and vegan != "—" else ""}
            {"<p class='mb-2'><strong>🏠 Quelle:</strong> " + source + "</p>" if source else ""}
            <hr class="my-2">
            {"<p class='mb-2 text-muted fst-italic'>" + summary + "</p>" if summary and summary != "—" else ""}
            {"<p class='mb-2'><strong>📝 Notiz:</strong> " + note + "</p>" if note and note != "—" else ""}
            {"<p class='mb-0'>" + tags_html + "</p>" if tags else ""}
          </div>
          <div class="col-12 col-md-5">
            <div class="card border-0 bg-light rounded-3 p-3">
              <h6 class="fw-semibold mb-3">📞 Kontakt aufnehmen</h6>
              <p class="small text-muted mb-3">
                Direktlink zur Plattform — kostenloser Account für Kontaktanfrage nötig.
              </p>
              <div class="d-flex flex-wrap gap-2">
                {contact_btn}
                {copy_btn}
              </div>
              <div class="mt-3 small">
                {verify_line}
              </div>
              {("<div class='mt-2'>" + source_link + "</div>") if source_link else ""}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>"""


def _table_row(lst: dict) -> str:
    """Build a single <tr> that opens the modal on click."""
    lid = lst.get("listing_id", "")
    price = lst.get("price_chf")
    tram = ", ".join(f"T{t}" for t in lst.get("tram_match_lines", []))
    tier_icon, tier_label, tier_cls, tier_tip = _tier(lst)

    return (
        f'<tr data-bs-toggle="modal" data-bs-target="#modal-{lid}" style="cursor:pointer">'
        f'<td onclick="event.stopPropagation()">'
        f'<button id="fav-{lid}" class="btn p-0 border-0 fav-btn" '
        f'onclick="toggleFav(\'{lid}\')" style="font-size:1.1rem;background:none;line-height:1">☆</button>'
        f'</td>'
        f'<td>{_score_bar(lst.get("relevance_score", 0))}</td>'
        f'<td>{_badge(lst.get("status", "neu"))}</td>'
        f'<td class="text-nowrap">{"CHF " + str(price) if price else "—"}</td>'
        f'<td>{_safe(lst.get("district", ""))}</td>'
        f'<td class="text-nowrap">{tram}</td>'
        f'<td>{_vegan_cell(lst.get("vegan_signal", ""))}</td>'
        f'<td>'
        f'<span class="badge bg-{tier_cls} text-white me-1" title="{tier_tip}" style="font-size:.7rem">{tier_icon}</span>'
        f'{_safe(lst.get("title", ""))[:65]}'
        f'</td>'
        f'</tr>\n'
    )


_JS = """
<script>
// ── Favorites ──────────────────────────────────────────────
const FAV_KEY = 'shaked-wg-favs';
function loadFavs(){try{return JSON.parse(localStorage.getItem(FAV_KEY)||'[]');}catch{return[];}}
function applyFav(id,active){
  const btn=document.getElementById('fav-'+id);
  const row=document.querySelector('tr[data-bs-target="#modal-'+id+'"]');
  if(btn)btn.innerHTML=active?'⭐':'☆';
  if(row){if(active)row.classList.add('table-warning');else row.classList.remove('table-warning');}
}
function toggleFav(id){
  let favs=loadFavs();const idx=favs.indexOf(id);
  if(idx>=0)favs.splice(idx,1);else favs.push(id);
  localStorage.setItem(FAV_KEY,JSON.stringify(favs));
  applyFav(id,favs.includes(id));
}
document.addEventListener('DOMContentLoaded',function(){loadFavs().forEach(id=>applyFav(id,true));});

// ── Copy search term ────────────────────────────────────────
function copySearch(text,btn){
  navigator.clipboard.writeText(text).then(function(){
    const orig=btn.innerHTML;btn.innerHTML='✅ Kopiert!';btn.disabled=true;
    setTimeout(function(){btn.innerHTML=orig;btn.disabled=false;},2000);
  });
}
</script>
"""


def generate_report(
    listings: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    profile_name: str = "Shaked Basel WG Search",
    project_end: str = "2026-06-08",
) -> str:
    """Return full HTML string for the listings report page."""
    sorted_listings = sorted(listings, key=lambda x: x.get("relevance_score", 0), reverse=True)
    last_run = runs[0] if runs else None
    last_scan = last_run["run_timestamp"] if last_run else "—"
    n_new = last_run.get("new_results", 0) if last_run else 0

    build_date = date.today().isoformat()

    try:
        days_left = (date.fromisoformat(project_end) - date.today()).days
    except ValueError:
        days_left = "?"
    days_color = (
        "danger"  if isinstance(days_left, int) and days_left < 10 else
        "warning" if isinstance(days_left, int) and days_left < 21 else "success"
    )

    # Count by tier
    n_direct = sum(1 for l in listings if _tier(l)[0] == "🔗")
    n_login  = sum(1 for l in listings if _tier(l)[0] == "🔐")
    n_search = sum(1 for l in listings if _tier(l)[0] == "🔍")
    n_broken = sum(1 for l in listings if _tier(l)[0] == "⚠️")

    rows    = "".join(_table_row(lst) for lst in sorted_listings)
    modals  = "".join(_modal(lst)     for lst in sorted_listings)

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shaked's WG Search — Basel</title>
  <link rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <style>
    body {{ background:#fffbf5; color:#1c1917; }}
    .hero {{ background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);
             color:#fff; padding:1.75rem 2rem; border-radius:.875rem; }}
    .hero .version-bar {{ font-size:.78rem; opacity:.85; margin-top:.5rem;
                          letter-spacing:.01em; }}
    .stat-card {{ border:none; border-radius:.75rem;
                  box-shadow:0 2px 8px rgba(0,0,0,.07); background:#fff; }}
    table {{ font-size:.875rem; }}
    td {{ vertical-align:middle; }}
    tr[data-bs-toggle]:hover td {{ background:rgba(245,158,11,.06); }}
    .modal-header {{ border-bottom:none; }}
    .fav-btn:focus {{ outline:none; box-shadow:none; }}
  </style>
</head>
<body>
<div class="container py-4">

  <!-- Hero -->
  <div class="hero mb-4">
    <h1 class="h3 mb-1">🏠 Shaked's WG Search — Basel</h1>
    <div class="version-bar">
      v{__version__} &nbsp;·&nbsp; Build {build_date}
      &nbsp;·&nbsp; Letzte Suche: <strong>{last_scan}</strong>
      &nbsp;·&nbsp; {n_new} neu seit letztem Lauf
    </div>
  </div>

  <!-- Stats row -->
  <div class="row g-3 mb-4">
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold" style="color:#d97706">{len(listings)}</div>
        <div class="text-muted small">Inserate total</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-success">
          {sorted_listings[0].get('relevance_score', 0) if sorted_listings else '—'}
        </div>
        <div class="text-muted small">Höchster Score</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-{days_color}">{days_left}</div>
        <div class="text-muted small">Tage verbleibend</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-success">
          {sum(1 for l in listings if 'vegan' in l.get('vegan_signal','').lower())}
        </div>
        <div class="text-muted small">Vegan-freundlich</div>
      </div>
    </div>
  </div>

  <!-- Tier legend -->
  <div class="d-flex flex-wrap gap-3 mb-3 small align-items-center">
    <span class="fw-semibold text-muted">Erreichbarkeit:</span>
    <span><span class="badge bg-success">🔗 {n_direct}</span> Direktlink</span>
    <span><span class="badge bg-warning text-dark">🔐 {n_login}</span> Login (kostenlos)</span>
    <span><span class="badge bg-secondary">🔍 {n_search}</span> Suche nötig</span>
    {"<span><span class='badge bg-danger'>⚠️ " + str(n_broken) + "</span> Offline?</span>" if n_broken else ""}
    <span class="ms-auto text-muted">Klick auf Zeile → Details &nbsp;|&nbsp; ☆ = Favorit</span>
  </div>

  <!-- Listings table -->
  <div class="card stat-card">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th style="width:32px"></th>
            <th style="width:120px">Score</th>
            <th>Status</th>
            <th>Preis</th>
            <th>Quartier</th>
            <th>Tram</th>
            <th>Vegan</th>
            <th>Inserat</th>
          </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
  </div>

  <p class="text-muted small mt-3 text-center">
    3× täglich aktualisiert (07:00 / 13:00 / 19:00) · {profile_name} · v{__version__}
  </p>
</div>

<!-- Listing modals -->
{modals}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
{_JS}
</body>
</html>"""
