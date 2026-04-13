"""Telegram Bot API notifier."""
from __future__ import annotations

import json
import logging
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shaked_wg_agent.notifier.base import BaseNotifier

log = logging.getLogger("shaked_wg_agent.notifier")


class TelegramNotifier(BaseNotifier):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self._available = bool(self._token)
        if not self._available:
            log.warning("TelegramNotifier: TELEGRAM_BOT_TOKEN missing — channel disabled")

    def format_message(self, digest_payload: dict[str, Any]) -> str:
        p = digest_payload.get("profile_name", "")
        c = digest_payload.get("city_name", "")
        total = digest_payload.get("total_new", 0)
        ts = digest_payload.get("scan_timestamp", "")[:16].replace("T", " ")
        lines = [
            f"*{p}* — *{c}*",
            "",
            f"{total} neue Angebote | {ts}",
            "",
        ]
        for lst in digest_payload.get("listings", []):
            title = lst.get("title", "")
            price = lst.get("price_chf")
            price_s = "k.A." if price is None else f"CHF {price}"
            dist = lst.get("district", "")
            sc = int(lst.get("relevance_score", 0) or 0)
            url = lst.get("direct_url", "")
            lines.append(f"*{title}* — {price_s} — {dist} — Score {sc}")
            lines.append(f"{url}")
            lines.append("")
        text = "\n".join(lines) + "\n_Shaked WG Agent_"
        if len(text) > 4096:
            n = len(digest_payload.get("listings", []))
            extra = f"\n... und {max(0, n - 1)} weitere Angebote" if n else ""
            text = text[: 4096 - len(extra) - 1] + extra + "\n_Shaked WG Agent_"
            if len(text) > 4096:
                text = text[:4090] + "…"
        return text

    def send(self, digest_payload: dict[str, Any]) -> bool:
        if not self._available:
            return False
        chat_id = self.config.get("chat_id")
        if not chat_id:
            return False
        try:
            text = self.format_message(digest_payload)
            url = f"https://api.telegram.org/bot{self._token}/sendMessage"
            body = json.dumps(
                {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                }
            ).encode("utf-8")
            req = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
            with urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except (OSError, HTTPError, URLError) as e:
            self.last_error = str(e)
            self.last_error_transient = True
            log.warning("TelegramNotifier: %s", e)
            return False
        except Exception as e:
            self.last_error = str(e)
            self.last_error_transient = False
            log.warning("TelegramNotifier: %s", e)
            return False
