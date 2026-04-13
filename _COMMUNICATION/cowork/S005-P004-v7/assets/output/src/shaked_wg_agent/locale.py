"""Locale registry: keyword sets, labels, and language metadata per country.

`Locale` is a frozen dataclass with exactly 10 fields — scoring and display
concerns only. Email text strings are stored separately in `EMAIL_STRINGS`
(a module-level dict) to keep the `Locale` contract stable while allowing
per-country email text to evolve independently.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Locale:
    accept_language: str
    vegan_strong: frozenset[str]
    vegan_partial: frozenset[str]
    vegan_weak: frozenset[str]
    vegan_no_signal: frozenset[str]
    status_labels: dict[str, str]
    transit_label: str
    currency_symbol: str
    direction: str
    html_lang: str


LOCALE_CH = Locale(
    accept_language="de-CH,de;q=0.9,en;q=0.8",
    vegan_strong=frozenset(
        {"vegan", "vegane", "veganer", "veganes", "tierfreie küche", "tierfreie wg"}
    ),
    vegan_partial=frozenset(
        {"pflanzlich", "pflanzliche", "vegan-freundlich", "vegetarisch"}
    ),
    vegan_weak=frozenset({"kein fleisch", "kein fisch", "plant-based"}),
    vegan_no_signal=frozenset({"kein signal", "unbekannt"}),
    status_labels={
        "favorit": "⭐ favorit",
        "interessant": "interessant",
        "kontaktiert": "kontaktiert",
        "neu": "neu",
        "abgesagt": "abgesagt",
    },
    transit_label="Transit lines",
    currency_symbol="CHF",
    direction="ltr",
    html_lang="de",
)


LOCALE_IL = Locale(
    accept_language="he-IL,he;q=0.9,en;q=0.8",
    vegan_strong=frozenset({"טבעוני", "טבעונית", "טבעוניים", "מטבח טבעוני"}),
    vegan_partial=frozenset({"צמחוני", "צמחונית", "ללא בשר", "plant-based"}),
    vegan_weak=frozenset({"ידידותי לטבעונים", "אפשרות טבעונית"}),
    vegan_no_signal=frozenset({"לא צוין", "לא ידוע"}),
    status_labels={
        "favorit": "⭐ מועדף",
        "interessant": "מעניין",
        "kontaktiert": "נוצר קשר",
        "neu": "חדש",
        "abgesagt": "בוטל",
    },
    transit_label="Transit lines",
    currency_symbol="₪",
    direction="rtl",
    html_lang="he",
)


LOCALES: dict[str, Locale] = {"CH": LOCALE_CH, "IL": LOCALE_IL}
_DEFAULT_LOCALE = LOCALE_CH


def get_locale(country: str = "CH") -> Locale:
    """Return locale for country code. Falls back to Swiss German."""
    return LOCALES.get(country, _DEFAULT_LOCALE)


EMAIL_STRINGS: dict[str, dict[str, str]] = {
    "CH": {
        "new_offers": "neue Angebote",
        "price_not_specified": "Preis nicht angegeben",
        "generated_by": "Generiert von Shaked WG Agent",
    },
    "IL": {
        "new_offers": "הצעות חדשות",
        "price_not_specified": "מחיר לא צוין",
        "generated_by": "נוצר על ידי Shaked WG Agent",
    },
}


def get_email_strings(country: str = "CH") -> dict[str, str]:
    """Return email text strings for country code. Falls back to Swiss German."""
    return EMAIL_STRINGS.get(country, EMAIL_STRINGS["CH"])
