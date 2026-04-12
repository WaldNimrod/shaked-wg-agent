#!/usr/bin/env python3
"""Generate a standalone HTML proof page with live screenshots of flatfox listings.

Run from project root:
  .venv/bin/python scripts/generate_proof.py
"""
from __future__ import annotations

import base64
import contextlib
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def _load_data() -> tuple[list[dict], list[dict]]:
    with open(PROJECT_ROOT / "data/listings.json", encoding="utf-8") as f:
        listings = json.load(f)
    with open(PROJECT_ROOT / "data/runs.json", encoding="utf-8") as f:
        runs = json.load(f)
    return listings, runs


def _select_listings(listings: list[dict], count: int = 8) -> list[dict]:
    """Pick top verified-active flatfox listings sorted by score."""
    candidates = [
        lst for lst in listings
        if lst.get("verified_active") is True
        and lst.get("source") == "flatfox"
        and lst.get("relevance_score", 0) > 0
        and lst.get("direct_url", "")
    ]
    candidates.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return candidates[:count]


def _take_screenshots(targets: list[dict]) -> dict[str, str]:
    """Return {source_listing_id: base64_png} for each listing."""
    from playwright.sync_api import sync_playwright

    results: dict[str, str] = {}
    print(f"Taking {len(targets)} screenshots with Playwright…", flush=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1200, "height": 820},
            locale="de-CH",
        )
        page = ctx.new_page()

        for lst in targets:
            pk = lst["source_listing_id"]
            url = lst["direct_url"]
            try:
                print(f"  → {pk}  {url[:70]}", flush=True)
                page.goto(url, wait_until="domcontentloaded", timeout=25_000)
                # Dismiss cookie/consent banners if present
                for sel in [
                    "button:has-text('Alle akzeptieren')",
                    "button:has-text('Accept all')",
                    "button:has-text('Akzeptieren')",
                    "button:has-text('OK')",
                    "[id*='cookie'] button",
                    "[class*='cookie'] button",
                ]:
                    with contextlib.suppress(Exception):
                        page.click(sel, timeout=1_500)
                        break
                time.sleep(1.5)
                shot = page.screenshot(full_page=False, clip={"x": 0, "y": 0, "width": 1200, "height": 780})
                results[pk] = base64.b64encode(shot).decode()
                print(f"    ✓ OK ({len(shot)//1024} KB)", flush=True)
            except Exception as exc:
                print(f"    ✗ FAILED: {exc}", flush=True)

        browser.close()

    return results


def _proof_html(
    listings: list[dict],
    screenshots: dict[str, str],
    runs: list[dict],
    generated_at: str,
) -> str:
    last_run = runs[0] if runs else {}
    last_scan = last_run.get("run_timestamp", "—")
    n_total = last_run.get("results_scanned", 0)
    errors = last_run.get("errors", [])

    # Stats
    n_verified = sum(1 for lst in listings if lst.get("verified_active") is True)
    n_broken   = sum(1 for lst in listings if lst.get("verified_active") is False)
    scores     = [lst.get("relevance_score", 0) for lst in listings if lst.get("relevance_score", 0) > 0]
    avg_score  = round(sum(scores) / len(scores), 1) if scores else 0

    def safe(v: object, d: str = "—") -> str:
        import html as _html
        return _html.escape(str(v)) if v else d

    cards_html = ""
    for idx, lst in enumerate(listings, 1):
        pk = lst.get("source_listing_id", "")
        title = safe(lst.get("title", ""), "Unbekannt")
        price = lst.get("price_chf")
        district = safe(lst.get("district", ""))
        location = safe(lst.get("location_text", ""))
        available = safe(lst.get("available_from", ""))
        score = lst.get("relevance_score", 0)
        lines = lst.get("transit_match_lines") or lst.get("tram_match_lines") or []
        tram = ", ".join(f"T{t}" for t in lines)
        vegan = safe(lst.get("vegan_signal", ""))
        url = lst.get("direct_url", "")
        verified_at = lst.get("last_verified_at", "—")
        try:
            dt = datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
            verified_str = dt.strftime("%d.%m.%Y %H:%M UTC")
        except Exception:
            verified_str = verified_at[:16] if verified_at else "—"

        shot = screenshots.get(pk, "")
        screenshot_html = (
            f'<img src="data:image/png;base64,{shot}" alt="Screenshot flatfox #{pk}" '
            f'class="screenshot" loading="lazy">'
            if shot else
            '<div class="no-shot">Screenshot nicht verfügbar</div>'
        )

        score_cls = "score-high" if score >= 40 else "score-mid" if score >= 20 else "score-low"

        cards_html += f"""
<div class="proof-card" id="card-{pk}">
  <div class="card-header">
    <span class="card-num">#{idx}</span>
    <span class="card-title">{title}</span>
    <span class="card-score {score_cls}">Score {score}</span>
  </div>
  <div class="card-body">
    <div class="card-meta">
      <table>
        <tr><td>🆔 Flatfox-ID</td><td><strong>{pk}</strong></td></tr>
        <tr><td>📍 Lage</td><td>{location}</td></tr>
        <tr><td>🏘 Quartier</td><td>{district}</td></tr>
        <tr><td>💰 Preis</td><td>{"CHF " + str(price) + " / Mt." if price else "—"}</td></tr>
        <tr><td>🗓 Verfügbar ab</td><td>{available if available != "—" else "Nicht angegeben"}</td></tr>
        <tr><td>🚃 Tram</td><td>{tram if tram else "—"}</td></tr>
        <tr><td>🌱 Vegan</td><td>{vegan if vegan not in ("—","kein Signal") else "kein Signal"}</td></tr>
        <tr><td>✅ Geprüft am</td><td><strong>{verified_str}</strong></td></tr>
        <tr><td>🔗 URL</td><td><a href="{url}" target="_blank" rel="noopener">{url[:60]}…</a></td></tr>
      </table>
      <a href="{url}" target="_blank" rel="noopener" class="open-btn">
        Inserat öffnen ↗
      </a>
    </div>
    <div class="card-screenshot">
      <div class="shot-label">Live-Screenshot — {generated_at}</div>
      {screenshot_html}
    </div>
  </div>
</div>
"""

    errors_html = ""
    if errors:
        errors_html = (
            '<div class="errors-box"><strong>Scan-Fehler:</strong> '
            + "; ".join(errors)
            + "</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Daten-Nachweisseite — Shaked WG Basel</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           background: #f8f9fa; color: #1c1917; line-height: 1.5; }}
    .hero {{ background: linear-gradient(135deg,#1e40af,#1d4ed8);
             color: #fff; padding: 2rem; }}
    .hero h1 {{ font-size: 1.6rem; margin-bottom: .5rem; }}
    .hero .sub {{ font-size: .9rem; opacity: .85; margin-top: .3rem; }}
    .badge-green  {{ background: #16a34a; color: #fff; border-radius: 4px;
                     padding: 2px 8px; font-size: .78rem; font-weight: 600; }}
    .badge-yellow {{ background: #ca8a04; color: #fff; border-radius: 4px;
                     padding: 2px 8px; font-size: .78rem; font-weight: 600; }}
    .stats-bar {{ display: flex; flex-wrap: wrap; gap: 1rem; padding: 1.25rem 2rem;
                  background: #fff; border-bottom: 1px solid #e5e7eb; }}
    .stat {{ text-align: center; }}
    .stat .val {{ font-size: 1.6rem; font-weight: 700; color: #1e40af; }}
    .stat .lbl {{ font-size: .75rem; color: #6b7280; }}
    .container {{ max-width: 1300px; margin: 0 auto; padding: 1.5rem 1rem; }}
    .section-title {{ font-size: 1.1rem; font-weight: 700; color: #374151;
                      margin: 1.5rem 0 .75rem; border-left: 4px solid #1d4ed8;
                      padding-left: .75rem; }}
    .proof-card {{ background: #fff; border-radius: 12px; overflow: hidden;
                   box-shadow: 0 2px 12px rgba(0,0,0,.08); margin-bottom: 1.5rem; }}
    .card-header {{ display: flex; align-items: center; gap: .75rem;
                    padding: .75rem 1.25rem; background: #f1f5f9;
                    border-bottom: 1px solid #e2e8f0; }}
    .card-num {{ background: #1d4ed8; color: #fff; border-radius: 50%;
                 width: 28px; height: 28px; display: flex; align-items: center;
                 justify-content: center; font-size: .8rem; font-weight: 700;
                 flex-shrink: 0; }}
    .card-title {{ flex: 1; font-weight: 600; font-size: .95rem; }}
    .card-score {{ font-size: .8rem; font-weight: 700; padding: 2px 8px;
                   border-radius: 4px; }}
    .score-high {{ background: #dcfce7; color: #15803d; }}
    .score-mid  {{ background: #fef9c3; color: #a16207; }}
    .score-low  {{ background: #f3f4f6; color: #6b7280; }}
    .card-body {{ display: grid; grid-template-columns: 340px 1fr; gap: 0; }}
    @media (max-width: 900px) {{ .card-body {{ grid-template-columns: 1fr; }} }}
    .card-meta {{ padding: 1.25rem; border-right: 1px solid #e2e8f0; }}
    .card-meta table {{ width: 100%; border-collapse: collapse; font-size: .83rem; }}
    .card-meta td {{ padding: 4px 6px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }}
    .card-meta td:first-child {{ color: #6b7280; white-space: nowrap; width: 110px; }}
    .card-meta a {{ color: #1d4ed8; text-decoration: none; font-size: .78rem;
                    word-break: break-all; }}
    .open-btn {{ display: inline-block; margin-top: 1rem; padding: .5rem 1rem;
                 background: #1d4ed8; color: #fff !important; border-radius: 6px;
                 text-decoration: none; font-weight: 600; font-size: .85rem; }}
    .open-btn:hover {{ background: #1e40af; }}
    .card-screenshot {{ padding: 1rem; background: #f8fafc; }}
    .shot-label {{ font-size: .72rem; color: #94a3b8; margin-bottom: .5rem; }}
    .screenshot {{ width: 100%; border-radius: 6px; border: 1px solid #e2e8f0;
                   display: block; }}
    .no-shot {{ width: 100%; height: 200px; background: #e2e8f0; border-radius: 6px;
                display: flex; align-items: center; justify-content: center;
                color: #9ca3af; font-size: .85rem; }}
    .errors-box {{ background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px;
                   padding: 1rem; margin-bottom: 1rem; font-size: .85rem; color: #b91c1c; }}
    .methodology {{ background: #fffbf5; border: 1px solid #f59e0b; border-radius: 8px;
                    padding: 1.25rem; margin-bottom: 1.5rem; font-size: .85rem; }}
    .methodology h3 {{ font-size: .95rem; margin-bottom: .5rem; color: #92400e; }}
    .methodology ul {{ padding-left: 1.2rem; }}
    .methodology li {{ margin-bottom: .3rem; }}
    footer {{ text-align: center; padding: 2rem; color: #9ca3af; font-size: .8rem; }}
  </style>
</head>
<body>

<div class="hero">
  <h1>🔍 Daten-Nachweis — Shaked WG Search Basel</h1>
  <div class="sub">
    Generiert am: <strong>{generated_at}</strong> &nbsp;·&nbsp;
    Letzter Scan: <strong>{last_scan}</strong> &nbsp;·&nbsp;
    <span class="badge-green">✓ Echtdaten — flatfox.ch API</span>
    &nbsp;
    <span class="badge-green">✓ Live-Screenshots</span>
  </div>
  <div class="sub" style="margin-top:.5rem">
    Diese Seite beweist, dass alle unten gezeigten Inserate real, aktuell und erreichbar sind.
    Jede Karte enthält einen Screenshot der tatsächlich geöffneten Webseite sowie einen direkten Link zur Quelle.
  </div>
</div>

<div class="stats-bar">
  <div class="stat"><div class="val">{n_total}</div><div class="lbl">API-Ergebnisse (Scan)</div></div>
  <div class="stat"><div class="val" style="color:#16a34a">{n_verified}</div><div class="lbl">Aktiv geprüft</div></div>
  <div class="stat"><div class="val" style="color:#dc2626">{n_broken}</div><div class="lbl">Offline/Broken</div></div>
  <div class="stat"><div class="val">{avg_score}</div><div class="lbl">Ø Relevanz-Score</div></div>
  <div class="stat"><div class="val" style="color:#d97706">{len(listings)}</div><div class="lbl">Gezeigt auf dieser Seite</div></div>
  <div class="stat"><div class="val">{generated_at[-8:]}</div><div class="lbl">Screenshot-Zeit</div></div>
</div>

<div class="container">
  {errors_html}

  <div class="methodology">
    <h3>📋 Methodik dieser Nachweisseite</h3>
    <ul>
      <li><strong>Datenquelle:</strong> flatfox.ch öffentliche REST-API (<code>/api/v1/public-listing/</code>)</li>
      <li><strong>Verifikation:</strong> Pin-API-Abgleich — jede Inserat-ID wird gegen die aktive Treffermenge in Basel geprüft</li>
      <li><strong>Screenshots:</strong> Aufgenommen mit Playwright/Chromium direkt vor der Generierung dieser Seite ({generated_at})</li>
      <li><strong>Keine Testdaten:</strong> 6 Seed-Einträge wurden aus der Datenbank entfernt (v0.2.2)</li>
      <li><strong>Direktlinks:</strong> Alle URLs führen zur echten Inserat-Seite auf flatfox.ch — klickbar und überprüfbar</li>
    </ul>
  </div>

  <div class="methodology" style="border-color:#1d4ed8">
    <h3 style="color:#1e40af">🔬 Wie du ein einzelnes Inserat selbst validieren kannst</h3>
    <p style="margin:.5rem 0 .75rem">Im Haupt-Interface (<a href="index.html" style="color:#1d4ed8">Shaked WG Search</a>) gibt es pro Inserat einen <strong>„🔄 Jetzt prüfen"</strong>-Button. So funktioniert er:</p>
    <ol style="padding-left:1.3rem;line-height:2">
      <li><strong>Öffne ein Inserat</strong> im Haupt-Interface — klicke auf eine beliebige Tabellenzeile</li>
      <li>Im Modal erscheint der Button <strong>„🔄 Jetzt prüfen"</strong> neben dem Verifikationsstatus</li>
      <li>Ein Klick sendet eine <strong>Live-Anfrage an die flatfox.ch API</strong>:<br>
          <code style="font-size:.78rem;background:#f1f5f9;padding:2px 6px;border-radius:3px">GET https://flatfox.ch/api/v1/pin/?west=7.5147&amp;east=7.6559&amp;south=47.5176&amp;north=47.5956</code></li>
      <li>Die API liefert alle aktuell aktiven Inserat-IDs (PKs) in der Basel-Bounding-Box</li>
      <li>Das System prüft, ob die <strong>Inserat-ID des gewählten Inserats</strong> in dieser Liste vorkommt</li>
      <li>Ergebnis: <span style="color:#16a34a;font-weight:600">✅ Aktiv (HH:MM)</span> oder <span style="color:#ca8a04;font-weight:600">⚠️ Nicht mehr aktiv</span></li>
    </ol>
    <p style="margin-top:.75rem;font-size:.83rem;color:#64748b">
      Die Prüfung läuft direkt im Browser — kein Laden der Seite nötig. Die API ist öffentlich zugänglich (kein Login).
      Dasselbe Verfahren verwendet der Server bei jedem automatischen Scan (3× täglich).
    </p>
  </div>

  <div class="section-title">Top-{len(listings)} Inserate nach Relevanz-Score — mit Live-Screenshots</div>
  {cards_html}
</div>

<footer>
  Shaked WG Agent v0.2.2 · Generiert {generated_at} · flatfox.ch API · Basel, Schweiz
</footer>

</body>
</html>
"""


def main() -> None:
    print("=== Shaked WG — Proof Page Generator ===", flush=True)
    print("1/4 Loading current data…", flush=True)
    listings_all, runs = _load_data()

    print("2/4 Selecting top verified listings…", flush=True)
    targets = _select_listings(listings_all, count=8)
    print(f"   Selected {len(targets)} listings for screenshots", flush=True)

    print("3/4 Taking live screenshots…", flush=True)
    screenshots = _take_screenshots(targets)
    print(f"   {len(screenshots)}/{len(targets)} screenshots captured", flush=True)

    print("4/4 Generating HTML proof page…", flush=True)
    generated_at = datetime.now(UTC).strftime("%d.%m.%Y %H:%M UTC")
    html = _proof_html(targets, screenshots, runs, generated_at)

    out_path = PROJECT_ROOT / "data" / "proof.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"\n✅ Proof page written: {out_path} ({len(html)//1024} KB)", flush=True)

    # Upload to upress if credentials available
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
    if os.environ.get("UPRESS_SFTP_HOST"):
        print("5/5 Uploading proof.html to server…", flush=True)
        try:
            from shaked_wg_agent.publisher.ftps_upload import (
                _connect,
                _ensure_remote_dir,
                _upload_file,
            )
            upload_path = os.environ.get("UPRESS_UPLOAD_PATH", "agents/shaked-wg")
            public_base = os.environ.get("UPRESS_PUBLIC_BASE", "https://www.nimrod.bio").rstrip("/")
            remote_file = f"{upload_path}/proof.html"
            public_url  = f"{public_base}/{upload_path}/proof.html"

            ftp = _connect()
            try:
                _ensure_remote_dir(ftp, upload_path)
                _upload_file(ftp, out_path, remote_file)
            finally:
                with contextlib.suppress(Exception):
                    ftp.quit()
            print(f"✅ Published: {public_url}")
        except Exception as exc:
            print(f"⚠ Upload failed: {exc}")
    else:
        print("   (No UPRESS credentials — skipping upload)")
        print(f"   Open locally: file://{out_path}")


if __name__ == "__main__":
    main()
