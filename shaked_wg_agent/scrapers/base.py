"""Abstract base class for all WG platform scrapers."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import requests
from bs4 import BeautifulSoup

from shaked_wg_agent.config import CityDefinition

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "de-CH,de;q=0.9,en;q=0.8",
}

_REQUEST_TIMEOUT = 20  # seconds
_POLITE_DELAY = 2.5    # seconds between requests


@dataclass
class ScrapedListing:
    """Raw listing data as extracted from a source page."""

    source: str
    source_listing_id: str
    source_search_url: str
    title: str
    price_chf: int | None
    available_from: str | None
    location_text: str
    district: str
    transit_match_lines: list[str] = field(default_factory=list)
    roommate_signal: str = ""
    vegan_signal: str = ""
    summary: str = ""
    direct_url: str = ""
    url_status: str = "direct"
    recovery_query: str = ""
    posted_date: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to listing dict compatible with listings.json schema."""
        return {
            "listing_id": f"{self.source}-{self.source_listing_id}",
            "source": self.source,
            "direct_url": self.direct_url,
            "url_status": self.url_status,
            "source_listing_id": self.source_listing_id,
            "source_search_url": self.source_search_url,
            "title": self.title,
            "title_fragment": " ".join(self.title.split()[:6]),
            "price_chf": self.price_chf,
            "available_from": self.available_from,
            "location_text": self.location_text,
            "district": self.district,
            "transit_match_lines": self.transit_match_lines,
            "roommate_signal": self.roommate_signal,
            "vegan_signal": self.vegan_signal,
            "summary": self.summary,
            "recovery_query": self.recovery_query,
            "posted_date": self.posted_date,
            "status": "neu",
            "note": "",
            "relevance_score": 0,
            "tags": [],
        }


class BaseScraper(ABC):
    """Base class for all WG listing scrapers.

    Subclasses must implement:
      - `fetch_listings(search_url)` → list[ScrapedListing]

    The base class provides HTTP helpers with polite delays and retry logic.
    """

    def __init__(self, source_id: str, search_url: str, city: CityDefinition) -> None:
        self.source_id = source_id
        self.search_url = search_url
        self.city = city
        self._session = requests.Session()
        self._session.headers.update(_DEFAULT_HEADERS)

    def _get(self, url: str, retries: int = 2) -> requests.Response:
        """HTTP GET with retry and polite delay."""
        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            if attempt > 0:
                time.sleep(_POLITE_DELAY * attempt)
            try:
                resp = self._session.get(url, timeout=_REQUEST_TIMEOUT)
                resp.raise_for_status()
                time.sleep(_POLITE_DELAY)
                return resp
            except requests.RequestException as exc:
                last_exc = exc
        raise requests.RequestException(
            f"Failed to fetch {url} after {retries + 1} attempts"
        ) from last_exc

    def _soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    def fetch_listings(self) -> list[ScrapedListing]:
        """Fetch and parse listings from the configured search URL.

        Returns a list of ScrapedListing objects.
        On network failure, should return [] rather than raising.
        """

    def close(self) -> None:
        self._session.close()
