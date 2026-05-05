"""Scraper modules for WG listing platforms."""
from shaked_wg_agent.scrapers.base import BaseScraper, ScrapedListing
from shaked_wg_agent.scrapers.weegee import WeegeeScraper

__all__ = ["BaseScraper", "ScrapedListing", "WeegeeScraper"]
