"""Locale helpers for scraper localization."""
from dataclasses import dataclass

@dataclass
class LocaleInfo:
    accept_language: str

_LOCALES = {
    "CH": LocaleInfo(accept_language="de-CH,de;q=0.9,en;q=0.8"),
    "IL": LocaleInfo(accept_language="he-IL,he;q=0.9,en;q=0.8"),
}

def get_locale(country: str) -> LocaleInfo:
    return _LOCALES.get(country, LocaleInfo(accept_language="en;q=0.9"))
