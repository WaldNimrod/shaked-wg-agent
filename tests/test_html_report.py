"""Tests for static HTML report (IL Hebrew + RTL + Bootstrap RTL)."""
from __future__ import annotations

from shaked_wg_agent.publisher.html_report import generate_report


def test_il_report_uses_bootstrap_rtl_hebrew_title() -> None:
    html = generate_report(
        listings=[],
        runs=[],
        profile_name="English Internal",
        project_end="2026-12-31",
        currency="ILS",
        country="IL",
        city_name="Test",
        report_title_he="כותרת ללקוח בעברית",
    )
    assert 'lang="he"' in html
    assert 'dir="rtl"' in html
    assert "bootstrap.rtl.min.css" in html
    assert "/dist/css/bootstrap.min.css" not in html
    assert "כותרת ללקוח בעברית" in html
    assert "Inserat" not in html
    assert "Verifiziert" not in html


def test_ch_report_uses_ltr_bootstrap() -> None:
    html = generate_report(
        listings=[],
        runs=[],
        profile_name="Shaked Basel",
        project_end="2026-06-08",
        currency="CHF",
        country="CH",
    )
    assert 'lang="de"' in html
    assert 'dir="ltr"' in html
    assert "bootstrap.min.css" in html
    assert "bootstrap.rtl.min.css" not in html


def test_il_report_hebrew_when_country_missing_but_ils_and_title_he() -> None:
    """Server/legacy city JSON may omit country; ILS + report_title_he still selects Hebrew UI."""
    html = generate_report(
        listings=[],
        runs=[],
        profile_name="Dror Internal",
        project_end="2026-12-31",
        currency="ILS",
        country="",
        report_title_he="דרור — כותרת",
    )
    assert 'lang="he"' in html
    assert "bootstrap.rtl.min.css" in html


def test_dror_profile_forces_hebrew_ui_even_if_country_mismatch() -> None:
    """Published dror path must stay Hebrew even if city JSON is wrong."""
    html = generate_report(
        listings=[],
        runs=[],
        profile_name="Dror Internal EN",
        project_end="2026-12-31",
        currency="CHF",
        country="CH",
        report_title_he="דרור — כותרת",
        profile_id="dror",
    )
    assert 'lang="he"' in html
    assert "bootstrap.rtl.min.css" in html
    assert "Build" not in html


def test_il_price_cell_wraps_ltr() -> None:
    html = generate_report(
        listings=[
            {
                "listing_id": "x1",
                "profile_id": "dror",
                "relevance_score": 50,
                "price": 5000,
                "currency": "ILS",
                "district": "בנימינה",
                "title": "בדיקה",
                "vegan_signal": "",
                "status": "neu",
                "url_status": "direct",
                "verified_active": True,
                "source": "homeless",
            }
        ],
        runs=[],
        profile_name="P",
        project_end="2026-12-31",
        currency="ILS",
        country="IL",
        report_title_he="דרור",
    )
    assert '<span dir="ltr">₪5000</span>' in html
