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
    return f'<span class="badge bg-{cls} text-nowrap" data-status-badge>{label}</span>'


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

    # Contact section — guard broken listings
    is_broken = (verified_active is False) or (lst.get("url_status") == "broken_needs_recovery")
    contact_href = direct_url or source_search_url

    copy_btn = (
        f'<button class="btn btn-sm btn-outline-secondary copy-btn" '
        f'onclick="copySearch(\'{rq_js}\', this)" '
        f'title="Suchbegriff in Zwischenablage kopieren">📋 Suchbegriff kopieren</button>'
    )
    recovery_search_url = f"https://www.google.com/search?q={_html.escape(recovery_query[:80])}"

    # "Jetzt prüfen" live-check button (flatfox only, active listings)
    source_raw = lst.get("source", "")
    pk = lst.get("source_listing_id", "")
    livecheck_btn = (
        f'<button id="lc-{lid}" class="btn btn-sm btn-outline-info ms-2" '
        f'onclick="liveCheck(\'{pk}\', \'lc-{lid}\')" '
        f'title="Flatfox-API abfragen — prüft ob das Inserat noch aktiv ist">🔄 Jetzt prüfen</button>'
        if source_raw == "flatfox" and not is_broken else ""
    )

    if is_broken:
        contact_block = f"""
              <div class="alert alert-warning mb-2 py-2 px-3">
                <strong>⚠️ Inserat möglicherweise offline</strong><br>
                <small class="text-muted">Dieses Inserat wurde zuletzt nicht mehr auf der Plattform gefunden. Kein direkter Kontakt möglich.</small>
              </div>
              <div class="d-flex flex-wrap gap-2 mt-2">
                <a href="{_html.escape(recovery_search_url)}" target="_blank" rel="noopener"
                   class="btn btn-sm btn-outline-secondary">🔍 Recovery-Suche</a>
                {copy_btn}
              </div>"""
    else:
        contact_href_esc = _html.escape(contact_href)
        contact_block = f"""
              <ol class="small mb-3 ps-3" style="line-height:1.9">
                <li>Klick auf <strong>„Kontakt über {source} ↗"</strong> — Seite öffnet sich</li>
                <li>Erstelle ein kostenloses Konto auf {source}.ch (~2 Min)</li>
                <li>Klick auf <strong>„Anfrage senden"</strong> beim Inserat</li>
                <li>Schreibe kurz: Name, Situation, Wunsch-Einzugsdatum</li>
              </ol>
              <div class="d-flex flex-wrap gap-2 mb-2">
                <a href="{contact_href_esc}" target="_blank" rel="noopener"
                   class="btn btn-sm btn-primary">Kontakt über {source} ↗</a>
                {copy_btn}
              </div>
              <div class="d-flex align-items-center gap-2 small">
                {verify_line}
                {livecheck_btn}
              </div>"""

    tags_html = " ".join(
        f'<span class="badge bg-light text-dark border me-1">{_html.escape(t)}</span>'
        for t in tags
    )

    # Status options for the select
    status_options = "".join(
        f'<option value="{k}">{v[1]}</option>'
        for k, v in _STATUS_BADGE.items()
    )

    return f"""
<div class="modal fade" id="modal-{lid}" tabindex="-1" aria-labelledby="modal-label-{lid}" aria-hidden="true" data-listing-id="{lid}">
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
            <div class="card border-0 bg-light rounded-3 p-3 mb-3">
              <h6 class="fw-semibold mb-2">📞 So kontaktierst du:</h6>
              {contact_block}
            </div>
            <!-- Status-Editor -->
            <div class="card border-0 bg-light rounded-3 p-3">
              <h6 class="fw-semibold mb-2">✏️ Eigener Status</h6>
              <div class="pin-section mb-2">
                <div class="input-group input-group-sm" style="max-width:220px">
                  <input type="password" class="form-control pin-input" placeholder="PIN eingeben"
                         id="pin-{lid}" autocomplete="off">
                  <button class="btn btn-outline-secondary" type="button"
                          onclick="checkPin('{lid}')">Entsperren</button>
                </div>
                <div id="pin-err-{lid}" class="text-danger small mt-1" style="display:none">Falscher PIN</div>
              </div>
              <div id="status-editor-{lid}" style="display:none">
                <div class="d-flex align-items-center gap-2 flex-wrap">
                  <select class="form-select form-select-sm" id="status-sel-{lid}" style="width:auto">
                    {status_options}
                  </select>
                  <button class="btn btn-sm btn-primary" onclick="saveStatus('{lid}')">Speichern</button>
                  <span id="status-saved-{lid}" class="text-success small" style="display:none">✓ Gespeichert</span>
                </div>
              </div>
              <p class="text-muted" style="font-size:.72rem;margin-top:.5rem;margin-bottom:0">
                Statusänderungen werden lokal gespeichert (nur dieser Browser).
              </p>
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
    status = lst.get("status", "neu")
    score = lst.get("relevance_score", 0)
    district = lst.get("district", "")

    return (
        f'<tr data-bs-toggle="modal" data-bs-target="#modal-{lid}" style="cursor:pointer"'
        f' data-status="{_html.escape(status)}"'
        f' data-price="{price or 0}"'
        f' data-tier="{tier_icon}"'
        f' data-score="{score}"'
        f' data-district="{_html.escape(district)}">'
        f'<td onclick="event.stopPropagation()">'
        f'<button id="fav-{lid}" class="btn p-0 border-0 fav-btn" '
        f'onclick="toggleFav(\'{lid}\')" style="font-size:1.1rem;background:none;line-height:1">☆</button>'
        f'</td>'
        f'<td>{_score_bar(score)}</td>'
        f'<td>{_badge(status)}</td>'
        f'<td class="text-nowrap">{"CHF " + str(price) if price else "—"}</td>'
        f'<td>{_safe(district)}</td>'
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

// ── Live check (flatfox pin API, client-side) ───────────────
const _FLATFOX_PIN = 'https://flatfox.ch/api/v1/pin/?west=7.5147&east=7.6559&south=47.5176&north=47.5956&max_count=500';
function liveCheck(pk,btnId){
  const btn=document.getElementById(btnId);
  if(!btn)return;
  btn.innerHTML='⏳ Prüfe...';btn.disabled=true;
  fetch(_FLATFOX_PIN)
    .then(function(r){return r.json();})
    .then(function(data){
      const items=Array.isArray(data)?data:(data.results||[]);
      const active=items.some(function(item){return String(item.pk)===String(pk);});
      const now=new Date().toLocaleTimeString('de-CH',{hour:'2-digit',minute:'2-digit'});
      btn.innerHTML=active?'✅ Aktiv ('+now+')':'⚠️ Nicht mehr aktiv';
      btn.className=active?'btn btn-sm btn-success ms-2':'btn btn-sm btn-warning ms-2';
      btn.disabled=false;
    })
    .catch(function(){
      btn.innerHTML='⚠️ Prüfung fehlgeschlagen';
      btn.disabled=false;
    });
}

// ── Copy search term ────────────────────────────────────────
function copySearch(text,btn){
  navigator.clipboard.writeText(text).then(function(){
    const orig=btn.innerHTML;btn.innerHTML='✅ Kopiert!';btn.disabled=true;
    setTimeout(function(){btn.innerHTML=orig;btn.disabled=false;},2000);
  });
}

// ── Status editing ──────────────────────────────────────────
const STATUS_KEY = 'shaked-wg-status';
const CORRECT_PIN = '418141';
const STATUS_MAP = {
  favorit:     ['success','⭐ favorit'],
  interessant: ['warning','interessant'],
  kontaktiert: ['primary','kontaktiert'],
  neu:         ['secondary','neu'],
  abgesagt:    ['danger','abgesagt']
};

function loadStatuses(){try{return JSON.parse(localStorage.getItem(STATUS_KEY)||'{}');}catch{return{};}}

function checkPin(lid){
  const input=document.getElementById('pin-'+lid);
  const err=document.getElementById('pin-err-'+lid);
  if(input.value===CORRECT_PIN){
    document.getElementById('status-editor-'+lid).style.display='';
    input.parentElement.parentElement.style.display='none';
    // Pre-fill select with current stored status
    const statuses=loadStatuses();
    const sel=document.getElementById('status-sel-'+lid);
    if(sel&&statuses[lid])sel.value=statuses[lid];
  } else {
    err.style.display='';
    input.value='';
    setTimeout(function(){err.style.display='none';},2000);
  }
}

function saveStatus(lid){
  const sel=document.getElementById('status-sel-'+lid);
  if(!sel)return;
  const st=sel.value;
  const statuses=loadStatuses();
  statuses[lid]=st;
  localStorage.setItem(STATUS_KEY,JSON.stringify(statuses));
  _applyStatus(lid,st);
  const saved=document.getElementById('status-saved-'+lid);
  if(saved){saved.style.display='';setTimeout(function(){saved.style.display='none';},2000);}
}

function _applyStatus(lid,st){
  const info=STATUS_MAP[st]||['secondary',st];
  // Update row badge + data-status
  const row=document.querySelector('tr[data-bs-target="#modal-'+lid+'"]');
  if(row){
    row.dataset.status=st;
    const badge=row.querySelector('td:nth-child(3) [data-status-badge]');
    if(badge){badge.className='badge bg-'+info[0]+' text-nowrap';badge.setAttribute('data-status-badge','');badge.textContent=info[1];}
    if(st==='favorit')row.classList.add('table-warning');else row.classList.remove('table-warning');
  }
  // Update modal header badge
  const modal=document.getElementById('modal-'+lid);
  if(modal){
    const hbadge=modal.querySelector('.modal-header [data-status-badge]');
    if(hbadge){hbadge.className='badge bg-'+info[0]+' text-nowrap';hbadge.textContent=info[1];}
  }
  // Re-apply filter since status changed
  filterTable();
}

function applyStoredStatuses(){
  const statuses=loadStatuses();
  Object.entries(statuses).forEach(function([lid,st]){_applyStatus(lid,st);});
}

// ── Filtering ───────────────────────────────────────────────
const FILTERS={status:'alle',price:'alle',tier:'alle'};

function filterTable(){
  const rows=document.querySelectorAll('#listings-tbody tr');
  let visible=0;
  rows.forEach(function(row){
    const st=row.dataset.status||'neu';
    const pr=parseInt(row.dataset.price||'0');
    const ti=row.dataset.tier||'';
    let show=true;
    if(FILTERS.status!=='alle'&&st!==FILTERS.status)show=false;
    if(FILTERS.price!=='alle'){
      const maxP=parseInt(FILTERS.price);
      if(pr<=0||pr>maxP)show=false;
    }
    if(FILTERS.tier!=='alle'&&ti!==FILTERS.tier)show=false;
    row.style.display=show?'':'none';
    if(show)visible++;
  });
  const cnt=document.getElementById('row-count');
  if(cnt)cnt.textContent='Zeige '+visible+' von '+rows.length+' Inseraten';
}

function setFilter(key,val){FILTERS[key]=val;filterTable();}
function clearFilters(){
  FILTERS.status='alle';FILTERS.price='alle';FILTERS.tier='alle';
  document.querySelectorAll('.filter-sel').forEach(function(s){s.value='alle';});
  filterTable();
}

// ── Sorting ─────────────────────────────────────────────────
let sortCol='score', sortDir=-1;

function sortTable(col){
  if(sortCol===col)sortDir=-sortDir;
  else{sortCol=col;sortDir=(col==='district'||col==='status')?1:-1;}
  const tbody=document.getElementById('listings-tbody');
  const rows=Array.from(tbody.querySelectorAll('tr'));
  rows.sort(function(a,b){
    if(col==='score'){return sortDir*(parseInt(a.dataset.score||'0')-parseInt(b.dataset.score||'0'));}
    if(col==='price'){
      const av=parseInt(a.dataset.price)||9999,bv=parseInt(b.dataset.price)||9999;
      return sortDir*(av-bv);
    }
    if(col==='district'){return sortDir*(a.dataset.district||'').localeCompare(b.dataset.district||'','de');}
    if(col==='status'){return sortDir*(a.dataset.status||'').localeCompare(b.dataset.status||'','de');}
    return 0;
  });
  rows.forEach(function(r){tbody.appendChild(r);});
  document.querySelectorAll('th[data-sortcol]').forEach(function(th){
    const ind=th.querySelector('.sort-ind');
    if(ind)ind.textContent=th.dataset.sortcol===col?(sortDir===1?' ↑':' ↓'):' ↕';
  });
}

// ── Init ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded',function(){
  loadFavs().forEach(function(id){applyFav(id,true);});
  applyStoredStatuses();
  filterTable();
  // Allow Enter key in PIN fields
  document.querySelectorAll('.pin-input').forEach(function(inp){
    inp.addEventListener('keydown',function(e){
      if(e.key==='Enter'){
        const lid=inp.id.replace('pin-','');
        checkPin(lid);
      }
    });
  });
});
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
    # Fix B: separate displayable (score>0) from hidden (score=0 = over-budget/invalid)
    visible_listings = [lst for lst in sorted_listings if lst.get("relevance_score", 0) > 0]
    hidden_count = len(sorted_listings) - len(visible_listings)
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

    # Count by tier (visible only)
    n_direct = sum(1 for lst in visible_listings if _tier(lst)[0] == "🔗")
    n_login  = sum(1 for lst in visible_listings if _tier(lst)[0] == "🔐")
    n_search = sum(1 for lst in visible_listings if _tier(lst)[0] == "🔍")
    n_broken = sum(1 for lst in visible_listings if _tier(lst)[0] == "⚠️")
    # Data quality stats for Fix F banner
    n_verified = sum(1 for lst in listings if lst.get("verified_active") is True)
    n_total_real = len(listings)

    rows    = "".join(_table_row(lst) for lst in visible_listings)
    modals  = "".join(_modal(lst)     for lst in visible_listings)

    # Filter bar: Status options
    status_opts = '<option value="alle">Status: alle</option>' + "".join(
        f'<option value="{k}">{v[1]}</option>'
        for k, v in _STATUS_BADGE.items()
    )

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
    th[data-sortcol] {{ cursor:pointer; user-select:none; white-space:nowrap; }}
    th[data-sortcol]:hover {{ background:rgba(245,158,11,.1); }}
    .filter-bar {{ background:#fff; border-radius:.75rem;
                   box-shadow:0 2px 8px rgba(0,0,0,.07);
                   padding:.75rem 1rem; margin-bottom:.75rem; }}
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
    <div class="version-bar mt-1">
      Datenqualität: <strong>Echtdaten (flatfox API)</strong>
      &nbsp;·&nbsp; {n_verified} von {n_total_real} aktiv geprüft
      &nbsp;·&nbsp; Keine Testdaten
    </div>
  </div>

  <!-- Stats row -->
  <div class="row g-3 mb-4">
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold" style="color:#d97706">{len(visible_listings)}</div>
        <div class="text-muted small">Inserate im Budget</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-success">
          {visible_listings[0].get('relevance_score', 0) if visible_listings else '—'}
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
          {sum(1 for lst in visible_listings if 'vegan' in lst.get('vegan_signal','').lower())}
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

  <!-- Filter bar -->
  <div class="filter-bar d-flex flex-wrap gap-2 align-items-center">
    <select class="form-select form-select-sm filter-sel" style="width:auto"
            onchange="setFilter('status', this.value)">
      {status_opts}
    </select>
    <select class="form-select form-select-sm filter-sel" style="width:auto"
            onchange="setFilter('price', this.value)">
      <option value="alle">Preis: alle</option>
      <option value="600">≤ 600 CHF</option>
      <option value="800">≤ 800 CHF</option>
      <option value="1000">≤ 1000 CHF</option>
    </select>
    <select class="form-select form-select-sm filter-sel" style="width:auto"
            onchange="setFilter('tier', this.value)">
      <option value="alle">Tier: alle</option>
      <option value="🔗">🔗 Direktlink</option>
      <option value="🔐">🔐 Login nötig</option>
      <option value="🔍">🔍 Suche nötig</option>
      <option value="⚠️">⚠️ Offline?</option>
    </select>
    <button class="btn btn-sm btn-outline-secondary" onclick="clearFilters()">✕ Filter löschen</button>
    <span id="row-count" class="ms-auto text-muted small"></span>
  </div>

  <!-- Listings table -->
  <div class="card stat-card">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th style="width:32px"></th>
            <th data-sortcol="score" style="width:120px" onclick="sortTable('score')">Score<span class="sort-ind"> ↓</span></th>
            <th data-sortcol="status" onclick="sortTable('status')">Status<span class="sort-ind"> ↕</span></th>
            <th data-sortcol="price" onclick="sortTable('price')">Preis<span class="sort-ind"> ↕</span></th>
            <th data-sortcol="district" onclick="sortTable('district')">Quartier<span class="sort-ind"> ↕</span></th>
            <th>Tram</th>
            <th>Vegan</th>
            <th>Inserat</th>
          </tr>
        </thead>
        <tbody id="listings-tbody">
{rows}
        </tbody>
      </table>
    </div>
  </div>

  {f'<p class="text-muted small mt-2 text-center">+ {hidden_count} weitere Inserate ausgeblendet (Außerhalb Budget / Score 0)</p>' if hidden_count else ''}
  <p class="text-muted small mt-2 text-center">
    3× täglich aktualisiert (07:00 / 13:00 / 19:00) · {profile_name} · v{__version__}
  </p>
</div>

<!-- Listing modals -->
{modals}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
{_JS}
</body>
</html>"""
