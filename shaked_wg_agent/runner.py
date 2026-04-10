"""Run orchestrator — drives a full scan cycle and updates data files."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from shaked_wg_agent.config import ProjectConfig, Source, load_config
from shaked_wg_agent.persistence import append_run, mark_stale_listings, upsert_listing
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
        "operator_notes": "",
    }

    append_run(run_record)
    return run_record
