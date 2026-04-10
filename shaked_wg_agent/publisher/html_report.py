"""Generate a static HTML report from listings and run data."""
from __future__ import annotations

from datetime import date
from typing import Any

_STATUS_BADGE = {
    "favorit":     ("success",   "⭐ favorit"),
    "interessant": ("info",      "interessant"),
    "kontaktiert": ("primary",   "kontaktiert"),
    "neu":         ("secondary", "neu"),
    "abgesagt":    ("danger",    "abgesagt"),
}

_VEGAN_ICON = {
    "kein Signal": "—",
    "unbekannt":   "?",
}


def _badge(status: str) -> str:
    cls, label = _STATUS_BADGE.get(status, ("secondary", status))
    return f'<span class="badge bg-{cls}">{label}</span>'


def _vegan_cell(signal: str) -> str:
    if not signal or signal in _VEGAN_ICON:
        return _VEGAN_ICON.get(signal or "", "—")
    return f'<span class="text-success fw-semibold">{signal[:24]}</span>'


def _score_bar(score: int) -> str:
    cls = "success" if score >= 85 else "warning" if score >= 65 else "secondary"
    return (
        f'<div class="d-flex align-items-center gap-1">'
        f'<div class="progress flex-grow-1" style="height:8px">'
        f'<div class="progress-bar bg-{cls}" style="width:{score}%"></div></div>'
        f'<small class="text-muted">{score}</small></div>'
    )


def generate_report(
    listings: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    profile_name: str = "Shaked Basel WG Search",
    project_end: str = "2026-06-08",
) -> str:
    """Return full HTML string for the listings report page."""
    sorted_listings = sorted(listings, key=lambda x: x.get("relevance_score", 0), reverse=True)
    last_run = runs[0] if runs else None
    last_updated = last_run["run_timestamp"] if last_run else "—"
    n_new = last_run.get("new_results", 0) if last_run else 0

    try:
        days_left = (date.fromisoformat(project_end) - date.today()).days
    except ValueError:
        days_left = "?"
    days_color = "danger" if isinstance(days_left, int) and days_left < 10 else \
                 "warning" if isinstance(days_left, int) and days_left < 21 else "success"

    rows = ""
    for lst in sorted_listings:
        title = lst.get("title", "")[:70]
        url = lst.get("direct_url", "")
        title_cell = f'<a href="{url}" target="_blank">{title}</a>' if url else title
        tram = ", ".join(f"T{t}" for t in lst.get("tram_match_lines", []))
        rows += (
            f"<tr>"
            f"<td>{_score_bar(lst.get('relevance_score', 0))}</td>"
            f"<td>{_badge(lst.get('status', 'neu'))}</td>"
            f"<td class='text-nowrap'>CHF {lst.get('price_chf', '?')}</td>"
            f"<td>{lst.get('district', '')}</td>"
            f"<td class='text-nowrap'>{tram}</td>"
            f"<td>{_vegan_cell(lst.get('vegan_signal', ''))}</td>"
            f"<td>{title_cell}</td>"
            f"</tr>\n"
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
    body {{ background: #f8f9fa; }}
    .hero {{ background: linear-gradient(135deg,#0d6efd 0%,#6610f2 100%);
             color:#fff; padding:2rem; border-radius:.75rem; }}
    .stat-card {{ border:none; border-radius:.75rem; box-shadow:0 2px 8px rgba(0,0,0,.08); }}
    table {{ font-size:.875rem; }}
    td {{ vertical-align:middle; }}
  </style>
</head>
<body>
<div class="container py-4">

  <!-- Hero -->
  <div class="hero mb-4">
    <h1 class="h3 mb-1">🏠 Shaked's WG Search — Basel</h1>
    <p class="mb-0 opacity-75">
      Updated: <strong>{last_updated}</strong>
      &nbsp;·&nbsp; {n_new} new since last run
    </p>
  </div>

  <!-- Stats row -->
  <div class="row g-3 mb-4">
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-primary">{len(listings)}</div>
        <div class="text-muted small">Total listings</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-success">
          {sorted_listings[0].get('relevance_score', 0) if sorted_listings else '—'}
        </div>
        <div class="text-muted small">Top score</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-{days_color}">{days_left}</div>
        <div class="text-muted small">Days left</div>
      </div>
    </div>
    <div class="col-6 col-md-3">
      <div class="card stat-card text-center p-3">
        <div class="fs-2 fw-bold text-warning">
          {sum(1 for l in listings if 'vegan' in l.get('vegan_signal','').lower())}
        </div>
        <div class="text-muted small">Vegan-friendly</div>
      </div>
    </div>
  </div>

  <!-- Listings table -->
  <div class="card stat-card">
    <div class="card-header bg-white fw-semibold">
      Listings — sorted by relevance
    </div>
    <div class="table-responsive">
      <table class="table table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th style="width:130px">Score</th>
            <th>Status</th>
            <th>Price</th>
            <th>District</th>
            <th>Tram</th>
            <th>Vegan</th>
            <th>Title</th>
          </tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
  </div>

  <p class="text-muted small mt-3 text-center">
    Auto-updated 3× daily (07:00 / 13:00 / 19:00) · {profile_name}
  </p>
</div>
</body>
</html>"""
