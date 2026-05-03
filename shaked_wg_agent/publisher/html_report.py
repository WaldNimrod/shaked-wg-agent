"""Generate a static HTML report with full-screen listing modals.

IL (country=IL) reports follow AOS Module 11 RTL/BiDi: bootstrap.rtl.min.css, lang=he,
dir=rtl, LTR islands for prices (dir=ltr), <bdi> for dynamic listing snippets.
"""
from __future__ import annotations

import html as _html
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from shaked_wg_agent import __version__

# Status keys are stable across JS and HTML (German labels in storage — internal keys only).
_STATUS_BADGE_DE = {
    "favorit": ("success", "⭐ favorit"),
    "interessant": ("warning", "interessant"),
    "kontaktiert": ("primary", "kontaktiert"),
    "neu": ("secondary", "neu"),
    "abgesagt": ("danger", "abgesagt"),
    # M4: outreach lifecycle statuses
    "contacted": ("primary", "📤 Contacted"),
    "replied": ("success", "💬 Replied"),
    "replied_negative": ("danger", "❌ Declined"),
    "viewed": ("warning", "👀 Viewed"),
    "rejected": ("secondary", "🚫 Removed"),
}
_STATUS_BADGE_HE = {
    "favorit": ("success", "⭐ מועדף"),
    "interessant": ("warning", "מעניין"),
    "kontaktiert": ("primary", "נוצר קשר"),
    "neu": ("secondary", "חדש"),
    "abgesagt": ("danger", "בוטל"),
    # M4: outreach lifecycle statuses
    "contacted": ("primary", "📤 פנייה נשלחה"),
    "replied": ("success", "💬 ענה"),
    "replied_negative": ("danger", "❌ סירב"),
    "viewed": ("warning", "👀 נצפה"),
    "rejected": ("secondary", "🚫 הוסר"),
}

# M4: statuses that place a listing in the "Closed" section
_CLOSED_STATUSES: frozenset[str] = frozenset({"rejected", "replied_negative"})

# Hebrew display names for listing source keys (UI chrome only).
_SOURCE_LABEL_HE = {
    "homeless": "הומלס",
    "flatfox": "פלטפוקס",
    "wg-gesucht": "ווי־גה־זוכט",
    "wgzimmer": "ווי־גצימר",
}


def _source_label(source_id: str, il: bool) -> str:
    if not il:
        return source_id
    return _SOURCE_LABEL_HE.get(source_id, source_id)


def _format_tram_lines(lines: list[Any], il: bool) -> str:
    """Format transit line numbers; IL UI uses Hebrew labels, no \"T\" prefix."""
    if not lines:
        return ""
    parts = [str(x) for x in lines]
    nums = ", ".join(parts)
    if il:
        return f'<span class="text-nowrap">קווים <span dir="ltr">{nums}</span></span>'
    return ", ".join(f"T{t}" for t in parts)


@dataclass(frozen=True)
class ReportUiContext:
    """UI bundle for one report locale (DE/CH vs IL Hebrew RTL)."""

    il: bool


def _badges_map(il: bool) -> dict[str, tuple[str, str]]:
    return _STATUS_BADGE_HE if il else _STATUS_BADGE_DE


def _classify_tier_key(lst: dict) -> str:
    url_status = lst.get("url_status", "")
    verified = lst.get("verified_active")
    if url_status == "broken_needs_recovery" or verified is False:
        return "broken"
    if url_status == "direct":
        source = lst.get("source", "")
        if source in ("flatfox", "wg-gesucht"):
            return "login"
        return "direct"
    if url_status == "search_only":
        return "search"
    return "search"


def _tier_tuple(lst: dict, il: bool) -> tuple[str, str, str, str]:
    """Return (icon, label, badge_class, tooltip)."""
    key = _classify_tier_key(lst)
    if il:
        mapping = {
            "broken": (
                "⚠️",
                "לא פעיל",
                "danger",
                "כתובת לא אומתה — נסה חיפוש לפי מילות מפתח",
            ),
            "login": (
                "🔐",
                "נדרשת התחברות",
                "warning",
                "קישור ישיר — ייתכן שתידרש הרשמה לאתר ליצירת קשר",
            ),
            "direct": (
                "🔗",
                "קישור ישיר",
                "success",
                "דף המודעה זמין ישירות",
            ),
            "search": (
                "🔍",
                "דרוש חיפוש",
                "secondary",
                "אין קישור ישיר — איתור לפי כותרת או מילות מפתח",
            ),
        }
    else:
        mapping = {
            "broken": (
                "⚠️",
                "Offline?",
                "danger",
                "URL möglicherweise offline — Recovery-Suche verwenden",
            ),
            "login": (
                "🔐",
                "Login nötig",
                "warning",
                "Direktlink vorhanden — kostenloser Account für Kontakt nötig",
            ),
            "direct": (
                "🔗",
                "Direktlink",
                "success",
                "Direktlink — vollständige Seite direkt erreichbar",
            ),
            "search": (
                "🔍",
                "Suche nötig",
                "secondary",
                "Kein Direktlink — über Suchbegriff auffindbar",
            ),
        }
    return mapping[key]


def _badge(status: str, il: bool) -> str:
    cls, label = _badges_map(il).get(status, ("secondary", status))
    return f'<span class="badge bg-{cls} text-nowrap" data-status-badge>{label}</span>'


def _listing_price(lst: dict) -> Any:
    price = lst.get("price")
    if price is None:
        price = lst.get("price_chf")
    return price


def _price_html(price: Any, currency: str, il: bool) -> str:
    """Wrap monetary tokens in dir=ltr per AOS RTL §4.3 (₪ before digits for ILS)."""
    if price is None or price == "":
        return "—"
    p = _html.escape(str(price))
    cur = str(currency or "")
    if il and cur == "ILS":
        return f'<span dir="ltr">₪{p}</span>'
    return f'<span dir="ltr">{_html.escape(cur)} {p}</span>'


def _price_badge_modal(price: Any, currency: str, il: bool) -> str:
    if not price:
        return ""
    p = _html.escape(str(price))
    if il and str(currency) == "ILS":
        return f"<span dir=\"ltr\">💰 ₪{p}/חודש</span>"
    return f"<span dir=\"ltr\">💰 {_html.escape(str(currency))} {p}/Mt.</span>"


def _vegan_cell(lst: dict, il: bool) -> str:
    """Render the vegan column. Highlights priority listings with a 🌱 badge."""
    signal = lst.get("vegan_signal", "")
    priority = bool(lst.get("vegan_priority"))
    if not signal or signal in ("kein Signal", "unbekannt", "אין אות", "לא ידוע"):
        if priority:
            label = "🌱 מטבח טבעוני" if il else "🌱 vegan"
            return f'<span class="badge bg-success text-white">{label}</span>'
        if signal in ("kein Signal", "אין אות"):
            return "—"
        return "לא ידוע" if il else "?"
    badge = "🌱 " if priority else ""
    return (
        f'<span class="text-success fw-semibold">{badge}{_html.escape(signal[:24])}</span>'
    )


def _safe(val: Any, default: str = "—") -> str:
    return _html.escape(str(val)) if val else default


def _bdi(val: str) -> str:
    return f"<bdi>{val}</bdi>"


def _modal(lst: dict, ctx: ReportUiContext) -> str:
    """Build modal; full Hebrew copy when ctx.il."""
    il = ctx.il
    lid = lst.get("listing_id", "")
    title_raw = _safe(lst.get("title", ""), "Unbekannt" if not il else "ללא כותרת")
    title = _bdi(title_raw) if il else title_raw
    price = _listing_price(lst)
    currency = lst.get("currency", "CHF")
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
    _lines = lst.get("transit_match_lines") or lst.get("tram_match_lines") or []
    tram = _format_tram_lines(list(_lines), il)
    direct_url = lst.get("direct_url", "")
    source_search_url = lst.get("source_search_url", "")
    recovery_query = lst.get("recovery_query", "") or lst.get("title", "")
    rq_js = recovery_query.replace("'", "\\'").replace('"', "&quot;")

    source_raw = str(lst.get("source", "") or "")

    tier_icon, tier_label, tier_cls, tier_tip = _tier_tuple(lst, il)
    tier_tip_esc = _html.escape(tier_tip)

    verified_at = lst.get("last_verified_at", "")
    verified_active = lst.get("verified_active")
    if verified_active is True and verified_at:
        try:
            dt = datetime.fromisoformat(verified_at)
            age_h = round((datetime.now(dt.tzinfo) - dt).total_seconds() / 3600)
            if il:
                age_str = f"לפני {age_h} שעות" if age_h > 0 else "עכשיו"
            else:
                age_str = f"vor {age_h}h" if age_h > 0 else "gerade eben"
        except Exception:
            age_str = verified_at[:10]
        verify_line = (
            f'<span class="text-success small">✓ {age_str} — נבדק פעיל</span>'
            if il
            else f'<span class="text-success small">✓ Geprüft aktiv ({age_str})</span>'
        )
    elif verified_active is False:
        verify_line = (
            '<span class="text-danger small">⚠️ הכתובת אולי לא פעילה — יש לבדוק במקור</span>'
            if il
            else '<span class="text-danger small">⚠️ URL möglicherweise offline — bitte Quelle prüfen</span>'
        )
    else:
        verify_line = (
            '<span class="text-muted small">טרם נבדק</span>'
            if il
            else '<span class="text-muted small">Noch nicht geprüft</span>'
        )

    is_broken = (verified_active is False) or (lst.get("url_status") == "broken_needs_recovery")
    contact_href = direct_url or source_search_url

    copy_title = "העתקת מילות חיפוש" if il else "Suchbegriff in Zwischenablage kopieren"
    copy_lbl = "📋 העתק מילות חיפוש" if il else "📋 Suchbegriff kopieren"
    copy_btn = (
        f'<button class="btn btn-sm btn-outline-secondary copy-btn" '
        f'onclick="copySearch(\'{rq_js}\', this)" '
        f'title="{_html.escape(copy_title)}">{copy_lbl}</button>'
    )
    recovery_search_url = f"https://www.google.com/search?q={_html.escape(recovery_query[:80])}"

    pk = lst.get("source_listing_id", "")
    livecheck_btn = ""
    if source_raw == "flatfox" and not is_broken:
        lc_title = (
            "בדיקה מול אתר המקור האם המודעה עדיין פעילה"
            if il
            else "Flatfox-API abfragen — prüft ob das Inserat noch aktiv ist"
        )
        lc_lbl = "🔄 בדוק עכשיו" if il else "🔄 Jetzt prüfen"
        livecheck_btn = (
            f'<button id="lc-{lid}" class="btn btn-sm btn-outline-info ms-2" '
            f'onclick="liveCheck(\'{pk}\', \'lc-{lid}\')" '
            f'title="{_html.escape(lc_title)}">{lc_lbl}</button>'
        )

    if is_broken:
        if il:
            contact_block = f"""
              <div class="alert alert-warning mb-2 py-2 px-3">
                <strong>⚠️ המודעה אולי לא פעילה</strong><br>
                <small class="text-muted">לא נמצא קישור תקף או שהדף הוסר. אין אפשרות קשר ישירה מכאן.</small>
              </div>
              <div class="d-flex flex-wrap gap-2 mt-2">
                <a href="{_html.escape(recovery_search_url)}" target="_blank" rel="noopener"
                   class="btn btn-sm btn-outline-secondary">🔍 חיפוש שחזור</a>
                {copy_btn}
              </div>"""
        else:
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
        if il:
            src_name = _html.escape(_source_label(source_raw, True))
            contact_block = f"""
              <ol class="small mb-3 ps-3" style="line-height:1.9" dir="rtl">
                <li>לחץ על <strong>«קישור לאתר המקור ↗»</strong> — ייפתח האתר ({src_name})</li>
                <li>התחבר או הירשם לפי הנדרש באתר</li>
                <li>מצא את המודעה ושלח פנייה למפרסם</li>
                <li>פרט בקצרה: מצב, תאריך כניסה רצוי</li>
              </ol>
              <div class="d-flex flex-wrap gap-2 mb-2">
                <a href="{contact_href_esc}" target="_blank" rel="noopener"
                   class="btn btn-sm btn-primary">קישור לאתר המקור ↗</a>
                {copy_btn}
              </div>
              <div class="d-flex align-items-center gap-2 small">
                {verify_line}
                {livecheck_btn}
              </div>"""
        else:
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

    status_options = "".join(
        f'<option value="{k}">{v[1]}</option>'
        for k, v in _badges_map(il).items()
    )

    price_badge = _price_badge_modal(price, currency, il)

    if il:
        hdr_contact = "📞 איך יוצרים קשר"
        hdr_status = "✏️ סטטוס אישי"
        pin_ph = "הקלד קוד אישור"
        pin_btn = "פתח"
        pin_err = "הקוד שגוי"
        save_btn = "שמור"
        saved_msg = "✓ נשמר"
        status_note = "שינויי סטטוס נשמרים מקומית בדפדפן זה בלבד."
        lbl_loc = "📍 מיקום"
        lbl_room = "👥 שותפים"
        lbl_vegan = "🌱 טבעונות"
        lbl_src = "🏠 מקור"
        lbl_note = "📝 הערה"
        lbl_avail = "🗓 זמין מ-"
        lbl_score = "📊 ציון"
        close_aria = "סגור"
        modal_body_l = "col-12 col-md-7"
        modal_body_r = "col-12 col-md-5"
    else:
        hdr_contact = "📞 So kontaktierst du:"
        hdr_status = "✏️ Eigener Status"
        pin_ph = "PIN eingeben"
        pin_btn = "Entsperren"
        pin_err = "Falscher PIN"
        save_btn = "Speichern"
        saved_msg = "✓ Gespeichert"
        status_note = "Statusänderungen werden lokal gespeichert (nur dieser Browser)."
        lbl_loc = "📍 Lage:"
        lbl_room = "👥 Mitbewohner:"
        lbl_vegan = "🌱 Vegan-Signal:"
        lbl_src = "🏠 Quelle:"
        lbl_note = "📝 Notiz:"
        lbl_avail = "🗓 ab "
        lbl_score = "📊 Score: "
        close_aria = "Close"
        modal_body_l = "col-12 col-md-7"
        modal_body_r = "col-12 col-md-5"

    pin_attrs = 'dir="auto" autocomplete="off"' if il else 'autocomplete="off"'

    loc_line = ""
    if location and location != "—":
        loc_line = f"<p class='mb-2'><strong>{lbl_loc}</strong> {_bdi(location) if il else location}</p>"
    room_line = ""
    if roommate and roommate != "—":
        room_line = f"<p class='mb-2'><strong>{lbl_room}</strong> {_bdi(roommate) if il else roommate}</p>"
    vegan_line = ""
    if vegan and vegan != "—":
        vegan_line = f"<p class='mb-2'><strong>{lbl_vegan}</strong> {_bdi(vegan) if il else vegan}</p>"
    src_line = (
        f"<p class='mb-2'><strong>{lbl_src}</strong> {_html.escape(_source_label(source_raw, il))}</p>"
        if source
        else ""
    )

    summary_line = ""
    if summary and summary != "—":
        summary_line = f"<p class='mb-2 text-muted fst-italic'>{_bdi(summary) if il else summary}</p>"
    note_line = ""
    if note and note != "—":
        note_line = f"<p class='mb-2'><strong>{lbl_note}</strong> {_bdi(note) if il else note}</p>"

    if tram:
        tram_disp = (
            f'<span class="text-nowrap">🚃 {tram}</span>'
            if il
            else f'<span dir="ltr">🚃 {tram}</span>'
        )
    else:
        tram_disp = ""
    avail_disp = ""
    if available and available != "—":
        avail_disp = f"<span>{lbl_avail}{available}</span>" if il else f"<span>🗓 ab {available}</span>"

    score_lbl = (
        f'<span>{lbl_score} <strong dir="ltr">{score}</strong></span>'
        if il
        else f"<span>📊 Score: <strong>{score}</strong></span>"
    )

    return f"""
<div class="modal fade" id="modal-{lid}" tabindex="-1" aria-labelledby="modal-label-{lid}" aria-hidden="true" data-listing-id="{lid}">
  <div class="modal-dialog modal-fullscreen-md-down modal-xl modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header" style="background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff">
        <div class="w-100">
          <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
            <span class="badge bg-{tier_cls} text-white" title="{tier_tip_esc}">{tier_icon} {tier_label}</span>
            {_badge(status, il)}
            <span class="fw-bold fs-5">{title}</span>
          </div>
          <div class="d-flex gap-3 flex-wrap small opacity-90">
            <span>📍 {_bdi(district) if il and district != "—" else district}</span>
            {price_badge}
            {avail_disp}
            {tram_disp}
            {score_lbl}
          </div>
        </div>
        <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="modal" aria-label="{close_aria}"></button>
      </div>
      <div class="modal-body">
        <div class="row g-3">
          <div class="{modal_body_l}">
            {loc_line}
            {room_line}
            {vegan_line}
            {src_line}
            <hr class="my-2">
            {summary_line}
            {note_line}
            {"<p class='mb-0'>" + tags_html + "</p>" if tags else ""}
          </div>
          <div class="{modal_body_r}">
            <div class="card border-0 bg-light rounded-3 p-3 mb-3">
              <h6 class="fw-semibold mb-2">{hdr_contact}</h6>
              {contact_block}
            </div>
            <div class="card border-0 bg-light rounded-3 p-3">
              <h6 class="fw-semibold mb-2">{hdr_status}</h6>
              <div class="pin-section mb-2">
                <div class="input-group input-group-sm" style="max-width:220px">
                  <input type="password" class="form-control pin-input" placeholder="{_html.escape(pin_ph)}"
                         id="pin-{lid}" {pin_attrs}>
                  <button class="btn btn-outline-secondary" type="button"
                          onclick="checkPin('{lid}')">{_html.escape(pin_btn)}</button>
                </div>
                <div id="pin-err-{lid}" class="text-danger small mt-1" style="display:none">{_html.escape(pin_err)}</div>
              </div>
              <div id="status-editor-{lid}" style="display:none">
                <div class="d-flex align-items-center gap-2 flex-wrap">
                  <select class="form-select form-select-sm" id="status-sel-{lid}" style="width:auto">
                    {status_options}
                  </select>
                  <button class="btn btn-sm btn-primary" onclick="saveStatus('{lid}')">{_html.escape(save_btn)}</button>
                  <span id="status-saved-{lid}" class="text-success small" style="display:none">{saved_msg}</span>
                </div>
              </div>
              <p class="text-muted" style="font-size:.72rem;margin-top:.5rem;margin-bottom:0">
                {status_note}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>"""


def _table_row(lst: dict, il: bool) -> str:
    """Build a single <tr> that opens the modal on click."""
    lid = lst.get("listing_id", "")
    price = _listing_price(lst)
    currency = lst.get("currency", "CHF")
    _lines = lst.get("transit_match_lines") or lst.get("tram_match_lines") or []
    tram = _format_tram_lines(list(_lines), il)
    tier_icon, tier_label, tier_cls, tier_tip = _tier_tuple(lst, il)
    tier_tip_esc = _html.escape(tier_tip)
    status = lst.get("status", "neu")
    score = lst.get("relevance_score", 0)
    district = lst.get("district", "")

    price_cell = _price_html(price, currency, il)
    if lst.get("over_budget_vegan_exception"):
        tip = "מעל התקציב — נשמרה כי המטבח טבעוני/צמחוני" if il else "Über Budget — Vegan-Ausnahme"
        price_cell = (
            f'<span class="text-warning" title="{_html.escape(tip)}">'
            f'⚠️ {price_cell}</span>'
        )
    title_snippet = _bdi(_safe(lst.get("title", ""))[:65]) if il else _safe(lst.get("title", ""))[:65]
    vegan_priority_attr = "1" if lst.get("vegan_priority") else "0"

    return (
        f'<tr data-bs-toggle="modal" data-bs-target="#modal-{lid}" style="cursor:pointer"'
        f' data-status="{_html.escape(status)}"'
        f' data-price="{price or 0}"'
        f' data-tier="{tier_icon}"'
        f' data-vegan="{vegan_priority_attr}"'
        f' data-score="{score}"'
        f' data-district="{_html.escape(district)}">'
        f'<td onclick="event.stopPropagation()">'
        f'<button id="fav-{lid}" class="btn p-0 border-0 fav-btn" '
        f'onclick="toggleFav(\'{lid}\')" style="font-size:1.1rem;background:none;line-height:1">☆</button>'
        f'</td>'
        f'<td>{_score_bar(score)}</td>'
        f'<td>{_badge(status, il)}</td>'
        f'<td class="text-nowrap">{price_cell}</td>'
        f'<td>{_bdi(_safe(district)) if il else _safe(district)}</td>'
        f'<td class="text-nowrap">{tram}</td>'
        f'<td>{_vegan_cell(lst, il)}</td>'
        f'<td>'
        f'<span class="badge bg-{tier_cls} text-white me-1" title="{tier_tip_esc}" style="font-size:.7rem">{tier_icon}</span>'
        f'{title_snippet}'
        f'</td>'
        f'</tr>\n'
    )


def _score_bar(score: int) -> str:
    cls = "success" if score >= 85 else "warning" if score >= 65 else "secondary"
    return (
        f'<div class="d-flex align-items-center gap-1">'
        f'<div class="progress flex-grow-1" style="height:6px">'
        f'<div class="progress-bar bg-{cls}" style="width:{score}%"></div></div>'
        f'<small class="fw-semibold" dir="ltr">{score}</small></div>'
    )


_JS_DE = """
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
  const row=document.querySelector('tr[data-bs-target="#modal-'+lid+'"]');
  if(row){
    row.dataset.status=st;
    const badge=row.querySelector('td:nth-child(3) [data-status-badge]');
    if(badge){badge.className='badge bg-'+info[0]+' text-nowrap';badge.setAttribute('data-status-badge','');badge.textContent=info[1];}
    if(st==='favorit')row.classList.add('table-warning');else row.classList.remove('table-warning');
  }
  const modal=document.getElementById('modal-'+lid);
  if(modal){
    const hbadge=modal.querySelector('.modal-header [data-status-badge]');
    if(hbadge){hbadge.className='badge bg-'+info[0]+' text-nowrap';hbadge.textContent=info[1];}
  }
  filterTable();
}

function applyStoredStatuses(){
  const statuses=loadStatuses();
  Object.entries(statuses).forEach(function([lid,st]){_applyStatus(lid,st);});
}

// ── Filtering ───────────────────────────────────────────────
const FILTERS={status:'alle',price:'alle',tier:'alle',vegan:'alle'};

function filterTable(){
  const rows=document.querySelectorAll('#listings-tbody tr');
  let visible=0;
  rows.forEach(function(row){
    const st=row.dataset.status||'neu';
    const pr=parseInt(row.dataset.price||'0');
    const ti=row.dataset.tier||'';
    const vg=row.dataset.vegan||'0';
    let show=true;
    if(FILTERS.status!=='alle'&&st!==FILTERS.status)show=false;
    if(FILTERS.price!=='alle'){
      const maxP=parseInt(FILTERS.price);
      if(pr<=0||pr>maxP)show=false;
    }
    if(FILTERS.tier!=='alle'&&ti!==FILTERS.tier)show=false;
    if(FILTERS.vegan==='only'&&vg!=='1')show=false;
    row.style.display=show?'':'none';
    if(show)visible++;
  });
  const cnt=document.getElementById('row-count-verified');
  if(cnt)cnt.textContent='Zeige '+visible+' von '+rows.length+' verifizierten Inseraten';
}

function setFilter(key,val){FILTERS[key]=val;filterTable();}
function clearFilters(){
  FILTERS.status='alle';FILTERS.price='alle';FILTERS.tier='alle';FILTERS.vegan='alle';
  document.querySelectorAll('.filter-sel').forEach(function(s){s.value='alle';});
  filterTable();
}

// ── Sorting ─────────────────────────────────────────────────
let sortCol='score', sortDir=-1;

function sortTable(col, tbodyId){
  tbodyId = tbodyId || 'listings-tbody';
  if(sortCol===col)sortDir=-sortDir;
  else{sortCol=col;sortDir=(col==='district'||col==='status')?1:-1;}
  const tbody=document.getElementById(tbodyId);
  if(!tbody)return;
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

_JS_HE = """
<script>
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

const _FLATFOX_PIN = 'https://flatfox.ch/api/v1/pin/?west=7.5147&east=7.6559&south=47.5176&north=47.5956&max_count=500';
function liveCheck(pk,btnId){
  const btn=document.getElementById(btnId);
  if(!btn)return;
  btn.innerHTML='⏳ בודק...';btn.disabled=true;
  fetch(_FLATFOX_PIN)
    .then(function(r){return r.json();})
    .then(function(data){
      const items=Array.isArray(data)?data:(data.results||[]);
      const active=items.some(function(item){return String(item.pk)===String(pk);});
      const now=new Date().toLocaleTimeString('he-IL',{hour:'2-digit',minute:'2-digit'});
      btn.innerHTML=active?'✅ פעיל ('+now+')':'⚠️ כבר לא פעיל';
      btn.className=active?'btn btn-sm btn-success ms-2':'btn btn-sm btn-warning ms-2';
      btn.disabled=false;
    })
    .catch(function(){
      btn.innerHTML='⚠️ הבדיקה נכשלה';
      btn.disabled=false;
    });
}

function copySearch(text,btn){
  navigator.clipboard.writeText(text).then(function(){
    const orig=btn.innerHTML;btn.innerHTML='✅ הועתק!';btn.disabled=true;
    setTimeout(function(){btn.innerHTML=orig;btn.disabled=false;},2000);
  });
}

const STATUS_KEY = 'shaked-wg-status';
const CORRECT_PIN = '418141';
const STATUS_MAP = {
  favorit:     ['success','⭐ מועדף'],
  interessant: ['warning','מעניין'],
  kontaktiert: ['primary','נוצר קשר'],
  neu:         ['secondary','חדש'],
  abgesagt:    ['danger','בוטל']
};

function loadStatuses(){try{return JSON.parse(localStorage.getItem(STATUS_KEY)||'{}');}catch{return{};}}

function checkPin(lid){
  const input=document.getElementById('pin-'+lid);
  const err=document.getElementById('pin-err-'+lid);
  if(input.value===CORRECT_PIN){
    document.getElementById('status-editor-'+lid).style.display='';
    input.parentElement.parentElement.style.display='none';
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
  const row=document.querySelector('tr[data-bs-target="#modal-'+lid+'"]');
  if(row){
    row.dataset.status=st;
    const badge=row.querySelector('td:nth-child(3) [data-status-badge]');
    if(badge){badge.className='badge bg-'+info[0]+' text-nowrap';badge.setAttribute('data-status-badge','');badge.textContent=info[1];}
    if(st==='favorit')row.classList.add('table-warning');else row.classList.remove('table-warning');
  }
  const modal=document.getElementById('modal-'+lid);
  if(modal){
    const hbadge=modal.querySelector('.modal-header [data-status-badge]');
    if(hbadge){hbadge.className='badge bg-'+info[0]+' text-nowrap';hbadge.textContent=info[1];}
  }
  filterTable();
}

function applyStoredStatuses(){
  const statuses=loadStatuses();
  Object.entries(statuses).forEach(function([lid,st]){_applyStatus(lid,st);});
}

const FILTERS={status:'alle',price:'alle',tier:'alle',vegan:'alle'};

function filterTable(){
  const rows=document.querySelectorAll('#listings-tbody tr');
  let visible=0;
  rows.forEach(function(row){
    const st=row.dataset.status||'neu';
    const pr=parseInt(row.dataset.price||'0');
    const ti=row.dataset.tier||'';
    const vg=row.dataset.vegan||'0';
    let show=true;
    if(FILTERS.status!=='alle'&&st!==FILTERS.status)show=false;
    if(FILTERS.price!=='alle'){
      const maxP=parseInt(FILTERS.price);
      if(pr<=0||pr>maxP)show=false;
    }
    if(FILTERS.tier!=='alle'&&ti!==FILTERS.tier)show=false;
    if(FILTERS.vegan==='only'&&vg!=='1')show=false;
    row.style.display=show?'':'none';
    if(show)visible++;
  });
  const cnt=document.getElementById('row-count-verified');
  if(cnt)cnt.textContent='מציג '+visible+' מתוך '+rows.length+' פרטים מאומתים';
}

function setFilter(key,val){FILTERS[key]=val;filterTable();}
function clearFilters(){
  FILTERS.status='alle';FILTERS.price='alle';FILTERS.tier='alle';FILTERS.vegan='alle';
  document.querySelectorAll('.filter-sel').forEach(function(s){s.value='alle';});
  filterTable();
}

let sortCol='score', sortDir=-1;

function sortTable(col, tbodyId){
  tbodyId = tbodyId || 'listings-tbody';
  if(sortCol===col)sortDir=-sortDir;
  else{sortCol=col;sortDir=(col==='district'||col==='status')?1:-1;}
  const tbody=document.getElementById(tbodyId);
  if(!tbody)return;
  const rows=Array.from(tbody.querySelectorAll('tr'));
  rows.sort(function(a,b){
    if(col==='score'){return sortDir*(parseInt(a.dataset.score||'0')-parseInt(b.dataset.score||'0'));}
    if(col==='price'){
      const av=parseInt(a.dataset.price)||9999,bv=parseInt(b.dataset.price)||9999;
      return sortDir*(av-bv);
    }
    if(col==='district'){return sortDir*(a.dataset.district||'').localeCompare(b.dataset.district||'','he');}
    if(col==='status'){return sortDir*(a.dataset.status||'').localeCompare(b.dataset.status||'','he');}
    return 0;
  });
  rows.forEach(function(r){tbody.appendChild(r);});
  document.querySelectorAll('th[data-sortcol]').forEach(function(th){
    const ind=th.querySelector('.sort-ind');
    if(ind)ind.textContent=th.dataset.sortcol===col?(sortDir===1?' ↑':' ↓'):' ↕';
  });
}

document.addEventListener('DOMContentLoaded',function(){
  loadFavs().forEach(function(id){applyFav(id,true);});
  applyStoredStatuses();
  filterTable();
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


def _js_for_report(il: bool) -> str:
    return _JS_HE if il else _JS_DE


def generate_report(
    listings: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    profile_name: str = "Shaked Basel WG Search",
    project_end: str = "2026-06-08",
    currency: str = "CHF",
    *,
    country: str = "CH",
    city_name: str = "",
    report_title_he: str | None = None,
    profile_id: str = "",
) -> str:
    """Return full HTML string for the listings report page."""
    country_norm = (country or "").strip().upper()
    profile_id_norm = (profile_id or "").strip().lower()
    # ILS + optional Hebrew report title: belt-and-suspenders if country string is wrong on server data.
    # profile_id dror: always Hebrew UI for published /shaked-wg/dror/ reports.
    he = (
        country_norm == "IL"
        or (
            str(currency).upper() == "ILS"
            and bool((report_title_he or "").strip())
        )
        or profile_id_norm == "dror"
    )
    raw_display = (report_title_he or profile_name).strip() if he else profile_name
    esc_display = _html.escape(raw_display)

    ctx = ReportUiContext(il=he)

    sorted_listings = sorted(listings, key=lambda x: x.get("relevance_score", 0), reverse=True)
    # M4: separate closed (rejected/declined) listings before visibility filter
    closed_listings = [lst for lst in sorted_listings if lst.get("status") in _CLOSED_STATUSES]
    open_listings = [lst for lst in sorted_listings if lst.get("status") not in _CLOSED_STATUSES]
    visible_listings = [lst for lst in open_listings if lst.get("relevance_score", 0) > 0]
    hidden_count = len(open_listings) - len(visible_listings)
    verified_listings = [
        lst
        for lst in visible_listings
        if lst.get("verified_active") is True and lst.get("url_status") == "direct"
    ]
    unverified_listings = [lst for lst in visible_listings if lst not in verified_listings]
    last_run = runs[0] if runs else None
    last_scan = last_run["run_timestamp"] if last_run else "—"
    n_new = last_run.get("new_results", 0) if last_run else 0

    build_date = date.today().isoformat()

    try:
        days_left = (date.fromisoformat(project_end) - date.today()).days
    except ValueError:
        days_left = "?"
    days_color = (
        "danger"
        if isinstance(days_left, int) and days_left < 10
        else "warning"
        if isinstance(days_left, int) and days_left < 21
        else "success"
    )

    n_direct = sum(1 for lst in visible_listings if _tier_tuple(lst, he)[0] == "🔗")
    n_login = sum(1 for lst in visible_listings if _tier_tuple(lst, he)[0] == "🔐")
    n_search = sum(1 for lst in visible_listings if _tier_tuple(lst, he)[0] == "🔍")
    n_broken = sum(1 for lst in visible_listings if _tier_tuple(lst, he)[0] == "⚠️")
    n_verified = sum(1 for lst in listings if lst.get("verified_active") is True)
    n_total_real = len(listings)
    n_vegan_priority = sum(1 for lst in visible_listings if lst.get("vegan_priority"))
    n_overbudget_exception = sum(
        1 for lst in visible_listings if lst.get("over_budget_vegan_exception")
    )

    rows_verified = "".join(_table_row(lst, he) for lst in verified_listings)
    rows_unverified = "".join(_table_row(lst, he) for lst in unverified_listings)
    # M4: closed listings get dimmed rows and their own modals
    rows_closed = "".join(_table_row(lst, he) for lst in closed_listings)
    modals = "".join(_modal(lst, ctx) for lst in visible_listings)
    modals += "".join(_modal(lst, ctx) for lst in closed_listings)

    cur_esc = _html.escape(str(currency))
    esc_city = _html.escape(city_name) if city_name else ""

    bootstrap_css = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css"
        if he
        else "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    )

    if he:
        html_lang, html_dir = "he", "rtl"
        doc_title = esc_display
        hero_h1 = f"🏠 {esc_display}"
        version_bar_1 = (
            f"גרסה {__version__} · נבנה {build_date} · "
            f"סריקה אחרונה: <strong>{last_scan}</strong> · "
            f"{n_new} חדשים מאז הריצה הקודמת"
        )
        hero_quality_inner = (
            "איכות נתונים: <strong>מודעות אמיתיות מ-homeless.co.il</strong> · "
            "חיפוש לפי אזור (מועצה אזורית השרון, inumber1=41) · "
            "<strong>ציון 0 למודעות שלא מזוהות עם יישוב מהרשימה בפרופיל</strong>"
            + (f" — {esc_city}" if esc_city else "")
            + f" · {n_verified} מתוך {n_total_real} נבדקו לפעילות כשהיה אפשר · "
            "יש לאמת מול המודעה המקורית לפני כל החלטה."
        )
        stat_lbl_budget = "מודעות בטווח (אזור + תקציב)"
        stat_lbl_high = "ציון מקסימלי"
        stat_lbl_days = "ימים ליעד הפרויקט"
        tier_intro = "נגישות:"
        tier_d = "קישור ישיר"
        tier_l = "התחברות (חינם)"
        tier_s = "דרוש חיפוש"
        tier_b = "לא פעיל"
        tier_hint = "שורה = פרטים · ☆ = מועדף"
        btn_clear = "✕ ניקוי מסננים"
        verified_title = "✅ מודעות מאומתות"
        verified_sub = (
            f"{len(verified_listings)} מודעות — קישור נבדק, בטווח תקציב ובאזור היישובים"
        )
        unverified_title = "⚠️ מודעות לא מאומתות"
        unverified_sub = f"{len(unverified_listings)} מודעות — אימות חלקי או ללא קישור ישיר"
        unverified_alert = (
            "<strong>שים לב:</strong> המודעות בטווח התקציב והאזור אך לא אומתו במלואן "
            "(בדיקת HTTP ממתינה או אין קישור ישיר). יש לבדוק במקור לפני יצירת קשר."
        )
        # M4: closed section labels
        closed_title = "🗄️ סגורות / נדחו"
        closed_sub = f"{len(closed_listings)} מודעות — נדחו או שהמשא ומתן הסתיים"
        closed_alert = (
            "<strong>ארכיון:</strong> מודעות אלו סומנו כ«נדחו» או «סירב» ואינן פעילות לחיפוש. "
            "הן מוצגות כאן לצורכי תיעוד בלבד."
        )
        hidden_msg = (
            f"+ {hidden_count} מודעות מוסתרות (מחוץ לתקציב או מחוץ לרשימת היישובים / ציון 0)"
        )
        footer_line = f"עודכן מהסריקה האחרונה · {raw_display} · גרסה {__version__}"
        th_score, th_status, th_price = "ציון", "סטטוס", "מחיר"
        th_district, th_tram, th_vegan, th_title = "אזור", "תחבורה", "טבעוני", "מודעה"
        status_opts = '<option value="alle">סטטוס: הכל</option>' + "".join(
            f'<option value="{k}">{v[1]}</option>'
            for k, v in _STATUS_BADGE_HE.items()
        )
        price_opts = f"""      <option value="alle">מחיר: הכל</option>
      <option value="600">≤ 600 {cur_esc}</option>
      <option value="800">≤ 800 {cur_esc}</option>
      <option value="1000">≤ 1000 {cur_esc}</option>"""
        tier_opts = f"""      <option value="alle">שכבת גישה: הכל</option>
      <option value="🔗">🔗 {tier_d}</option>
      <option value="🔐">🔐 {tier_l}</option>
      <option value="🔍">🔍 {tier_s}</option>
      <option value="⚠️">⚠️ {tier_b}</option>"""
        vegan_opts = """      <option value="alle">מטבח: הכל</option>
      <option value="only">🌱 רק טבעוני/צמחוני</option>"""
        vegan_stat_label = "מטבח טבעוני/צמחוני"
    else:
        html_lang, html_dir = "de", "ltr"
        doc_title = esc_display
        hero_h1 = f"🏠 {esc_display}"
        version_bar_1 = (
            f"v{__version__} &nbsp;·&nbsp; Build {build_date}"
            f" &nbsp;·&nbsp; Letzte Suche: <strong>{last_scan}</strong>"
            f" &nbsp;·&nbsp; {n_new} neu seit letztem Lauf"
        )
        hero_quality_inner = (
            f'Datenqualität: <strong>Echtdaten (flatfox API)</strong>'
            f" &nbsp;·&nbsp; {n_verified} von {n_total_real} aktiv geprüft"
            f" &nbsp;·&nbsp; Keine Testdaten"
            f' &nbsp;·&nbsp; <a href="proof.html" target="_blank" rel="noopener"'
            f' style="color:#fff;text-decoration:underline;font-weight:600">🔍 Datennachweise</a>'
        )
        stat_lbl_budget = "Inserate im Budget"
        stat_lbl_high = "Höchster Score"
        stat_lbl_days = "Tage verbleibend"
        tier_intro = "Erreichbarkeit:"
        tier_d, tier_l, tier_s, tier_b = "Direktlink", "Login (kostenlos)", "Suche nötig", "Offline?"
        tier_hint = "Klick auf Zeile → Details &nbsp;|&nbsp; ☆ = Favorit"
        btn_clear = "✕ Filter löschen"
        verified_title = "✅ Verifizierte Inserate"
        verified_sub = (
            f"{len(verified_listings)} Inserate — aktiv geprüft, Direktlink, im Budget"
        )
        unverified_title = "⚠️ Nicht verifizierte Inserate"
        unverified_sub = f"{len(unverified_listings)} Inserate — Daten nicht 100% bestätigt"
        unverified_alert = (
            "<strong>Hinweis:</strong> Diese Inserate sind im Budget, konnten jedoch nicht "
            "vollständig verifiziert werden (z.B. Verifikation ausstehend, URL-Status unklar "
            "oder <code>verified_active</code> nicht gesetzt). "
            "Direkt auf der Quellseite prüfen, bevor du Kontakt aufnimmst."
        )
        # M4: closed section labels
        closed_title = "🗄️ Geschlossene Inserate"
        closed_sub = f"{len(closed_listings)} Inserate — abgelehnt oder Kontakt abgebrochen"
        closed_alert = (
            "<strong>Archiv:</strong> Diese Inserate wurden als «abgelehnt» oder «abgesagt» "
            "markiert und erscheinen nicht im aktiven Ranking. "
            "Sie werden zur Nachverfolgung hier angezeigt."
        )
        hidden_msg = (
            f"+ {hidden_count} weitere Inserate ausgeblendet (Außerhalb Budget / Score 0)"
        )
        footer_line = (
            f"3× täglich aktualisiert (07:00 / 13:00 / 19:00) · {profile_name} · v{__version__}"
        )
        th_score, th_status, th_price = "Score", "Status", "Preis"
        th_district, th_tram, th_vegan, th_title = "Quartier", "Tram", "Vegan", "Inserat"
        status_opts = '<option value="alle">Status: alle</option>' + "".join(
            f'<option value="{k}">{v[1]}</option>'
            for k, v in _STATUS_BADGE_DE.items()
        )
        price_opts = f"""      <option value="alle">Preis: alle</option>
      <option value="600">≤ 600 {cur_esc}</option>
      <option value="800">≤ 800 {cur_esc}</option>
      <option value="1000">≤ 1000 {cur_esc}</option>"""
        tier_opts = f"""      <option value="alle">Tier: alle</option>
      <option value="🔗">🔗 {tier_d}</option>
      <option value="🔐">🔐 {tier_l}</option>
      <option value="🔍">🔍 {tier_s}</option>
      <option value="⚠️">⚠️ {tier_b}</option>"""
        vegan_opts = """      <option value="alle">Küche: alle</option>
      <option value="only">🌱 nur vegan/vegetarisch</option>"""
        vegan_stat_label = "Vegan/vegetarische Küche"

    # Custom CSS: logical properties for RTL-friendly layout (AOS §2)
    extra_body = ""
    if he:
        extra_body = """
    [dir="rtl"] .filter-bar { text-align: start; }
    [dir="rtl"] .hero .version-bar { text-align: start; }
"""

    return f"""<!DOCTYPE html>
<html lang="{html_lang}" dir="{html_dir}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{doc_title}</title>
  <link rel="stylesheet" href="{bootstrap_css}">
  <style>
    body {{ background:#fffbf5; color:#1c1917; }}
    .hero {{ background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);
             color:#fff; padding-block:1.75rem; padding-inline:2rem; border-radius:.875rem; }}
    .hero .version-bar {{ font-size:.78rem; opacity:.85; margin-block-start:.5rem;
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
                   padding-block:.75rem; padding-inline:1rem; margin-block-end:.75rem; }}
{extra_body}
  </style>
</head>
<body>
<div class="container py-4">

  <!-- Hero -->
  <div class="hero mb-4">
    <h1 class="h3 mb-1">{hero_h1}</h1>
    <div class="version-bar">
      {version_bar_1}
    </div>
    <div class="version-bar mt-1">
      {hero_quality_inner}
    </div>
  </div>

  <!-- Stats row -->
  <div class="row g-3 mb-4">
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold" style="color:#d97706">{len(visible_listings)}</div>
        <div class="text-muted small">{stat_lbl_budget}</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-success" dir="ltr">
          {visible_listings[0].get('relevance_score', 0) if visible_listings else '—'}
        </div>
        <div class="text-muted small">{stat_lbl_high}</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-{days_color}" dir="ltr">{days_left}</div>
        <div class="text-muted small">{stat_lbl_days}</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-success" dir="ltr">
          {n_vegan_priority}
        </div>
        <div class="text-muted small">🌱 {vegan_stat_label}</div>
        {f'<div class="text-warning" style="font-size:.7rem">+{n_overbudget_exception} מעל תקציב — חריגה טבעונית</div>' if he and n_overbudget_exception else (f'<div class="text-warning" style="font-size:.7rem">+{n_overbudget_exception} über Budget (Vegan-Ausnahme)</div>' if n_overbudget_exception else '')}
      </div>
    </div>
  </div>

  <!-- Tier legend -->
  <div class="d-flex flex-wrap gap-3 mb-3 small align-items-center">
    <span class="fw-semibold text-muted">{tier_intro}</span>
    <span><span class="badge bg-success">🔗 {n_direct}</span> {tier_d}</span>
    <span><span class="badge bg-warning text-dark">🔐 {n_login}</span> {tier_l}</span>
    <span><span class="badge bg-secondary">🔍 {n_search}</span> {tier_s}</span>
    {"<span><span class='badge bg-danger'>⚠️ " + str(n_broken) + "</span> " + tier_b + "</span>" if n_broken else ""}
    <span class="ms-auto text-muted">{tier_hint}</span>
  </div>

  <!-- Filter bar -->
  <div class="filter-bar d-flex flex-wrap gap-2 align-items-center">
    <select class="form-select form-select-sm filter-sel" style="width:auto"
            onchange="setFilter('status', this.value)">
      {status_opts}
    </select>
    <select class="form-select form-select-sm filter-sel" style="width:auto"
            onchange="setFilter('price', this.value)">
{price_opts}
    </select>
    <select class="form-select form-select-sm filter-sel" style="width:auto"
            onchange="setFilter('tier', this.value)">
{tier_opts}
    </select>
    <select class="form-select form-select-sm filter-sel" style="width:auto"
            onchange="setFilter('vegan', this.value)">
{vegan_opts}
    </select>
    <button class="btn btn-sm btn-outline-secondary" onclick="clearFilters()">{btn_clear}</button>
  </div>

  <!-- Verified listings table -->
  <div class="d-flex align-items-center gap-2 mb-2 mt-3">
    <span class="badge bg-success fs-6 px-3 py-2">{verified_title}</span>
    <span class="text-muted small">{verified_sub}</span>
  </div>
  <div class="card stat-card mb-2">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th style="width:32px"></th>
            <th data-sortcol="score" style="width:120px" onclick="sortTable('score','listings-tbody')">{th_score}<span class="sort-ind"> ↓</span></th>
            <th data-sortcol="status" onclick="sortTable('status','listings-tbody')">{th_status}<span class="sort-ind"> ↕</span></th>
            <th data-sortcol="price" onclick="sortTable('price','listings-tbody')">{th_price}<span class="sort-ind"> ↕</span></th>
            <th data-sortcol="district" onclick="sortTable('district','listings-tbody')">{th_district}<span class="sort-ind"> ↕</span></th>
            <th>{th_tram}</th>
            <th>{th_vegan}</th>
            <th>{th_title}</th>
          </tr>
        </thead>
        <tbody id="listings-tbody">
{rows_verified}
        </tbody>
      </table>
    </div>
  </div>
  <p id="row-count-verified" class="text-muted small mb-3"></p>

  {f'''
  <div class="d-flex align-items-center gap-2 mb-2 mt-4">
    <span class="badge bg-warning text-dark fs-6 px-3 py-2">{unverified_title}</span>
    <span class="text-muted small">{unverified_sub}</span>
  </div>
  <div class="alert alert-warning border-warning mb-2 py-2 px-3 small">
    {unverified_alert}
  </div>
  <div class="card stat-card mb-2" style="border:2px solid #f59e0b">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead style="background:#fef9c3">
          <tr>
            <th style="width:32px"></th>
            <th>{th_score}</th>
            <th>{th_status}</th>
            <th>{th_price}</th>
            <th>{th_district}</th>
            <th>{th_tram}</th>
            <th>{th_vegan}</th>
            <th>{th_title}</th>
          </tr>
        </thead>
        <tbody id="listings-tbody-unverified">
{rows_unverified}
        </tbody>
      </table>
    </div>
  </div>
  ''' if unverified_listings else ''}

  {f'<p class="text-muted small mt-2 text-center">{hidden_msg}</p>' if hidden_count else ''}

  {f'''
  <div class="d-flex align-items-center gap-2 mb-2 mt-4" style="opacity:0.7">
    <span class="badge bg-secondary fs-6 px-3 py-2">{closed_title}</span>
    <span class="text-muted small">{closed_sub}</span>
  </div>
  <div class="alert alert-secondary border-secondary mb-2 py-2 px-3 small" style="opacity:0.7">
    {closed_alert}
  </div>
  <div class="card stat-card mb-2" style="opacity:0.55">
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-secondary">
          <tr>
            <th style="width:32px"></th>
            <th>{th_score}</th>
            <th>{th_status}</th>
            <th>{th_price}</th>
            <th>{th_district}</th>
            <th>{th_tram}</th>
            <th>{th_vegan}</th>
            <th>{th_title}</th>
          </tr>
        </thead>
        <tbody id="listings-tbody-closed">
{rows_closed}
        </tbody>
      </table>
    </div>
  </div>
  ''' if closed_listings else ''}

  <p class="text-muted small mt-2 text-center">
    {_html.escape(footer_line)}
  </p>
</div>

{modals}

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
{_js_for_report(he)}
</body>
</html>"""
