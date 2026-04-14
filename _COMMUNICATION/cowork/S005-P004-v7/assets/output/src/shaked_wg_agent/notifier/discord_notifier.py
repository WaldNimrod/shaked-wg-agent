"""Discord webhook notifier."""
from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shaked_wg_agent.notifier.base import BaseNotifier

log = logging.getLogger("shaked_wg_agent.notifier")


class DiscordNotifier(BaseNotifier):
    def format_message(self, digest_payload: dict[str, Any]) -> dict[str, Any]:
        p = digest_payload.get("profile_name", "")
        c = digest_payload.get("city_name", "")
        total = digest_payload.get("total_new", 0)
        listings = digest_payload.get("listings", [])
        shown = listings[:10]
        extra = len(listings) - 10 if len(listings) > 10 else 0
        content = f"**{p}** — **{c}** — {total} neue Angebote"
        if extra > 0:
            content += f" (zeige 10 von {total})"
        embeds = []
        for lst in shown:
            score = int(lst.get("relevance_score", 0) or 0)
            color = 0x2E7D32 if score >= 70 else 0xE65100 if score >= 40 else 0xC62828
            price = lst.get("price")
            if price is None:
                price = lst.get("price_chf")
            currency = lst.get("currency", "CHF")
            price_s = "k.A." if price is None else f"{currency} {price}"
            fields = [
                {"name": "Preis", "value": price_s, "inline": True},
                {"name": "Quartier", "value": str(lst.get("district", "")), "inline": True},
                {"name": "Score", "value": str(score), "inline": True},
            ]
            vegan = lst.get("vegan_signal") or ""
            if vegan:
                fields.append({"name": "Vegan", "value": vegan[:200], "inline": False})
            tlines = lst.get("transit_match_lines") or []
            if tlines:
                fields.append(
                    {
                        "name": "Tram/Bus",
                        "value": ", ".join(tlines),
                        "inline": False,
                    }
                )
            embeds.append(
                {
                    "title": lst.get("title", "")[:256],
                    "url": lst.get("direct_url") or None,
                    "color": color,
                    "fields": fields,
                }
            )
        return {"content": content, "embeds": embeds}

    def send(self, digest_payload: dict[str, Any]) -> bool:
        webhook = self.config.get("webhook_url", "")
        if not webhook.startswith("https://discord.com/api/webhooks/"):
            log.warning("DiscordNotifier: invalid webhook_url")
            return False
        try:
            payload = self.format_message(digest_payload)
            body = json.dumps(payload).encode("utf-8")
            req = Request(
                webhook,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=10) as resp:
                code = resp.status
                return code in (200, 204)
        except (OSError, HTTPError, URLError) as e:
            self.last_error = str(e)
            self.last_error_transient = getattr(e, "code", None) in (429, 500, 502, 503, 504)
            log.warning("DiscordNotifier: %s", e)
            return False
        except Exception as e:
            self.last_error = str(e)
            self.last_error_transient = False
            log.warning("DiscordNotifier: %s", e)
            return False
