"""Run orchestrator — drives a full scan cycle and updates data files."""
from __future__ import annotations

import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from shaked_wg_agent.config import ProjectConfig, Source, load_config
from shaked_wg_agent.persistence import append_run, load_listings, load_runs, mark_stale_listings, upsert_listing
from shaked_wg_agent.scorer import score_listing
from shaked_wg_agent.scrapers.base import BaseScraper


def _build_scraper(source: Source) -> BaseScraper:
    """Instantiate the correct scraper for a given source."""
    from shaked_wg_agent.scrapers.flatfox import FlatfoxScraper
    from shaked_wg_agent.scrapers.wg_gesucht import WgGesuchtScraper
    from shaked_wg_agent.scrapers.wgzimmer import WgzimmerScraper

    mapping = {
        "wgzimmer": WgzimmerScraper,
        "wg-gesucht": WgGesuchtScraper,
        "flatfox": FlatfoxScraper,
    }
    cls = mapping.get(source.id)
    if cls is None:
        raise ValueError(f"No scraper registered for source id '{source.id}'")
    return cls(source_id=source.id, search_url=source.search_url)


def _publish(cfg: ProjectConfig) -> str | None:
    """Generate HTML report and upload to upress. Returns public URL or None."""
    import os

    # Only publish if credentials are present
    if not os.environ.get("UPRESS_SFTP_HOST"):
        return None

    try:
        from shaked_wg_agent.publisher.ftps_upload import MissingCredentialsError, upload_report
        from shaked_wg_agent.publisher.html_report import generate_report

        listings = load_listings()
        runs = load_runs()
        html = generate_report(
            listings=listings,
            runs=runs,
            profile_name=cfg.agent.profile_name,
            project_end=cfg.agent.project_end,
        )
        tmp = Path(tempfile.mkdtemp()) / "index.html"
        tmp.write_text(html, encoding="utf-8")
        public_url = upload_report(tmp)
        return public_url
    except MissingCredentialsError:
        return None
    except Exception as exc:
        return f"ERROR: {exc}"


def run_scan(cfg: ProjectConfig | None = None) -> dict[str, Any]:
    """Execute a full scan across all enabled sources.

    Returns a run record dict (also persisted to data/runs.json).
    """
    if cfg is None:
        cfg = load_config()

    run_id = f"run-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4]}"
    started_at = datetime.now(UTC)

    sources_scanned = 0
    results_scanned = 0
    new_results = 0
    updated_results = 0
    active_ids: set[str] = set()
    errors: list[str] = []

    for source in cfg.active_sources:
        scraper: BaseScraper | None = None
        try:
            scraper = _build_scraper(source)
            scraped = scraper.fetch_listings()
            sources_scanned += 1
            results_scanned += len(scraped)

            for scraped_listing in scraped:
                listing_dict = scraped_listing.to_dict()
                listing_dict["relevance_score"] = score_listing(listing_dict, cfg.agent)
                action, saved = upsert_listing(listing_dict)
                active_ids.add(saved["listing_id"])
                if action == "new":
                    new_results += 1
                elif action == "updated":
                    updated_results += 1
        except Exception as exc:
            errors.append(f"{source.id}: {exc}")
        finally:
            if scraper is not None:
                scraper.close()

    stale_removed = mark_stale_listings(active_ids, cfg.agent.retention_days)
    duration = round((datetime.now(UTC) - started_at).total_seconds())

    # Publish HTML report to upress (if credentials available)
    report_url = _publish(cfg)

    run_record: dict[str, Any] = {
        "run_id": run_id,
        "run_timestamp": started_at.isoformat(timespec="seconds"),
        "triggered_by": "manual",
        "sources_scanned": sources_scanned,
        "results_scanned": results_scanned,
        "new_results": new_results,
        "updated_results": updated_results,
        "stale_removed": stale_removed,
        "duration_seconds": duration,
        "errors": errors,
        "report_url": report_url,
        "operator_notes": "",
    }

    append_run(run_record)
    return run_record
