"""Run orchestrator — drives a full scan cycle and updates data files."""
from __future__ import annotations

import importlib
import tempfile
import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests as _requests

from shaked_wg_agent.config import CityDefinition, ProjectConfig, ResolvedSource, load_config
from shaked_wg_agent.persistence import (
    append_run,
    load_listings,
    load_runs,
    mark_stale_listings,
    save_listings,
    upsert_listing,
)
from shaked_wg_agent.scorer import score_listing
from shaked_wg_agent.scrapers.base import BaseScraper

_VERIFY_TIMEOUT = 6  # seconds per URL check


def _verify_listings(listings: list[dict], city: CityDefinition) -> list[dict]:
    """Verify stored listings are still live.

    Strategy by source:
    - flatfox: re-check via pin API (Cloudflare blocks HEAD from server IPs)
    - others: HEAD request per URL (definitive 404 → broken, 200 → active, else → unchanged)
    """
    # flatfox: API-based presence check (reliable, CF-bypass)
    from shaked_wg_agent.scrapers.flatfox import verify_listings as _verify_flatfox

    flatfox_listings = [row for row in listings if row.get("source") == "flatfox"]
    _verify_flatfox(flatfox_listings, city)

    now = datetime.now(UTC).isoformat(timespec="seconds")
    for lst in listings:
        if lst.get("source") == "flatfox":
            continue  # already handled above
        url = lst.get("direct_url", "")
        if not url:
            lst["verified_active"] = False
            continue
        try:
            resp = _requests.head(
                url,
                timeout=_VERIFY_TIMEOUT,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            final_url = resp.url
            if resp.status_code == 404:
                lst["verified_active"] = False
                lst["url_status"] = "broken_needs_recovery"
            elif resp.status_code == 200:
                is_active = (
                    "/search" not in final_url
                    and "/home" not in final_url
                    and final_url.rstrip("/") not in ("https://www.wgzimmer.ch",)
                )
                lst["verified_active"] = is_active
                if is_active:
                    lst["last_verified_at"] = now
                    if lst.get("url_status") == "broken_needs_recovery":
                        lst["url_status"] = "direct"
                else:
                    lst["url_status"] = "broken_needs_recovery"
            # 403, 5xx, 3xx → leave unchanged
        except Exception:
            pass  # network error → preserve existing state
    return listings


def _resolve_class(fqn: str) -> type:
    """Resolve fully-qualified class name to class.

    Raises ValueError if FQN lacks a '.', ImportError if module can't be
    imported, AttributeError if class is missing, or TypeError if the class
    does not subclass BaseScraper.
    """
    if "." not in fqn:
        raise ValueError(
            f"Invalid FQN '{fqn}': must contain module path and class name separated by '.'"
        )
    module_path, class_name = fqn.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ImportError(
            f"Cannot import module '{module_path}' for scraper class '{fqn}'"
        ) from exc
    if not hasattr(module, class_name):
        raise AttributeError(f"Module '{module_path}' has no class '{class_name}'")
    cls = getattr(module, class_name)
    if not (isinstance(cls, type) and issubclass(cls, BaseScraper)):
        raise TypeError(f"Class '{class_name}' is not a subclass of BaseScraper")
    return cls


def _build_scraper(source: ResolvedSource, city: CityDefinition) -> BaseScraper:
    """Instantiate the correct scraper for a given source via FQN resolution."""
    fqn = source.connector_class or source.scraper_class
    cls = _resolve_class(fqn)
    return cls(source_id=source.source_id, search_url=source.search_url, city=city)


def _publish(cfg: ProjectConfig) -> str | None:
    """Generate HTML report and upload to upress. Returns public URL or None."""
    import os

    # Only publish if credentials are present
    if not os.environ.get("UPRESS_SFTP_HOST"):
        return None

    try:
        from shaked_wg_agent.publisher.ftps_upload import MissingCredentialsError, upload_report
        from shaked_wg_agent.publisher.html_report import generate_report

        pid = cfg.profile.profile_id
        listings = [row for row in load_listings() if row.get("profile_id") == pid]
        runs = [row for row in load_runs() if row.get("profile_id") == pid]
        html = generate_report(
            listings=listings,
            runs=runs,
            profile_name=cfg.profile.profile_name,
            project_end=cfg.agent.project_end,
            currency=cfg.city.currency,
            country=cfg.city.country,
            city_name=cfg.city.city_name,
            report_title_he=cfg.profile.report_title_he,
            profile_id=cfg.profile.profile_id,
        )
        tmp = Path(tempfile.mkdtemp()) / "index.html"
        tmp.write_text(html, encoding="utf-8")
        public_url = upload_report(tmp, profile_id=cfg.profile.profile_id)
        return public_url
    except MissingCredentialsError:
        return None
    except Exception as exc:
        return f"ERROR: {exc}"


def run_scan(
    profile_id: str | None = None,
    cfg: ProjectConfig | None = None,
    triggered_by: str = "manual",
) -> dict[str, Any]:
    """Execute a full scan across all enabled sources.

    Returns a run record dict (also persisted to data/runs.json).
    """
    if cfg is None:
        cfg = load_config(profile_id)

    run_id = f"run-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
    started_at = datetime.now(UTC)

    sources_scanned = 0
    results_scanned = 0
    new_results = 0
    updated_results = 0
    active_ids: set[str] = set()
    errors: list[str] = []
    new_rows: list[dict[str, Any]] = []

    for source in cfg.active_sources:
        scraper: BaseScraper | None = None
        try:
            scraper = _build_scraper(source, cfg.city)
            scraped = scraper.fetch_listings()
            sources_scanned += 1
            results_scanned += len(scraped)

            for scraped_listing in scraped:
                listing_dict = scraped_listing.to_dict()
                listing_dict["city_id"] = cfg.city.city_id
                listing_dict["profile_id"] = cfg.profile.profile_id
                listing_dict["relevance_score"] = score_listing(listing_dict, cfg.profile, cfg.city)
                action, saved = upsert_listing(listing_dict)
                active_ids.add(saved["listing_id"])
                if action == "new":
                    new_results += 1
                    new_rows.append(saved)
                elif action == "updated":
                    updated_results += 1
        except Exception as exc:
            errors.append(f"{source.source_id}: {exc}")
        finally:
            if scraper is not None:
                scraper.close()

    stale_removed = mark_stale_listings(
        active_ids,
        cfg.profile.retention_days,
        profile_id=cfg.profile.profile_id,
    )

    # Verify only the active profile's listings to avoid cross-profile coupling.
    all_listings = load_listings()
    pid = cfg.profile.profile_id
    profile_rows = [row for row in all_listings if row.get("profile_id") == pid]
    if profile_rows:
        verified_rows = _verify_listings(profile_rows, cfg.city)
        verified_by_id = {row["listing_id"]: row for row in verified_rows}
        merged: list[dict[str, Any]] = []
        for row in all_listings:
            row_id = row.get("listing_id")
            if row_id in verified_by_id:
                merged.append(verified_by_id[row_id])
            else:
                merged.append(row)
        save_listings(merged)

    duration = round((datetime.now(UTC) - started_at).total_seconds())

    # Publish HTML report to upress (if credentials available)
    report_url = _publish(cfg)

    run_record: dict[str, Any] = {
        "run_id": run_id,
        "run_timestamp": started_at.isoformat(timespec="seconds"),
        "triggered_by": triggered_by,
        "city_id": cfg.city.city_id,
        "profile_id": cfg.profile.profile_id,
        "sources_scanned": sources_scanned,
        "results_scanned": results_scanned,
        "new_results": new_results,
        "updated_results": updated_results,
        "stale_removed": stale_removed,
        "duration_seconds": duration,
        "errors": errors,
        "report_url": report_url,
        "operator_notes": "",
        "notification_sent": None,
    }

    if new_results > 0 and cfg.profile.notifications is not None:
        from shaked_wg_agent.notifier import notify_digest

        run_record["notification_sent"] = notify_digest(
            asdict(cfg.profile),
            asdict(cfg.city),
            run_record,
            new_rows,
        )

    append_run(run_record)
    return run_record
