"""ntfy.sh push notifier."""
from __future__ import annotations

import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shaked_wg_agent.notifier.base import BaseNotifier

log = logging.getLogger("shaked_wg_agent.notifier")


class NtfyNotifier(BaseNotifier):
    def format_message(self, digest_payload: dict[str, Any]) -> str:
        chunks = []
        for lst in digest_payload.get("listings", []):
            title = lst.get("title", "")
            price = lst.get("price")
            if price is None:
                price = lst.get("price_chf")
            currency = lst.get("currency", "CHF")
            ps = "k.A." if price is None else f"{currency} {price}"
            dist = lst.get("district", "")
            sc = int(lst.get("relevance_score", 0) or 0)
            url = lst.get("direct_url", "")
            chunks.append(f"{title} — {ps} ({dist}) — Score: {sc}/100\n{url}")
        return "\n\n".join(chunks)

    def send(self, digest_payload: dict[str, Any]) -> bool:
        topic = self.config.get("topic") or ""
        if not topic:
            return False
        server = (self.config.get("server_url") or "https://ntfy.sh").rstrip("/")
        url = f"{server}/{topic}"
        total = digest_payload.get("total_new", 0)
        listings = digest_payload.get("listings") or []
        max_score = max(
            (int(x.get("relevance_score", 0) or 0) for x in listings),
            default=0,
        )
        priority = "4" if max_score >= 80 else "3"
        click = listings[0].get("direct_url", "") if listings else ""
        body = self.format_message(digest_payload).encode("utf-8")
        try:
            req = Request(url, data=body, method="POST")
            req.add_header("Title", f"[Shaked WG] {total} neue Angebote")
            req.add_header("Priority", priority)
            req.add_header("Tags", "house")
            req.add_header("Click", click)
            with urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except (OSError, HTTPError, URLError) as e:
            self.last_error = str(e)
            self.last_error_transient = True
            log.warning("NtfyNotifier: %s", e)
            return False
        except Exception as e:
            self.last_error = str(e)
            self.last_error_transient = False
            log.warning("NtfyNotifier: %s", e)
            return False
