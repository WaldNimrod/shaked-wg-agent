"""Shared constants for Yad2 POC scripts — polite defaults."""
from __future__ import annotations

# Seconds between HTTP attempts (POC politeness)
POLITE_DELAY_SEC = 3.0

# Public rental search URL (Hebrew site; category=nadlan rent)
DEFAULT_SEARCH_URL = (
    "https://www.yad2.co.il/realestate/rent?"
    "topArea=2&area=3&property=1&rooms=1-5.5&price=1-10000"
)

# Mobile flag often serves a lighter path (POC observation — bot wall behavior varies).
DEFAULT_SEARCH_URL_MOBILE = DEFAULT_SEARCH_URL + "&mobile=1"

USER_AGENTS = {
    "chrome_desktop": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "curl_like": "curl/8.7.1",
    "python_requests": "python-requests/2.31.0",
    "iphone_safari": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
    ),
}


def looks_like_cloudflare(html: str) -> bool:
    h = html.lower()
    return (
        "cloudflare" in h
        or "cf-browser-verification" in h
        or "checking your browser" in h
        or "just a moment" in h
        or "attention required" in h
    )


def looks_like_bot_wall(html: str, title: str = "") -> bool:
    """True if page is a challenge/captcha wall rather than real content."""
    h = (html + "\n" + title).lower()
    return looks_like_cloudflare(html) or (
        "shieldsquare" in h
        or "captcha" in title.lower()
        or "human verification" in h
        or "בדיקת אבטחה" in html  # Hebrew security check pages
    )


def snippet(html: str, max_len: int = 400) -> str:
    s = " ".join(html.split())
    return s[:max_len] + ("…" if len(s) > max_len else "")
