"""Generic HTTPS JSON webhook notifier."""
from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shaked_wg_agent.notifier.base import BaseNotifier

log = logging.getLogger("shaked_wg_agent.notifier")


class WebhookNotifier(BaseNotifier):
    def format_message(self, digest_payload: dict[str, Any]) -> dict[str, Any]:
        return dict(digest_payload)

    def send(self, digest_payload: dict[str, Any]) -> bool:
        target = self.config.get("url") or ""
        if not target.startswith("https://"):
            log.warning("WebhookNotifier: invalid url")
            return False
        try:
            payload = self.format_message(digest_payload)
            body = json.dumps(payload).encode("utf-8")
            hdrs = {"Content-Type": "application/json"}
            hdrs.update(self.config.get("headers") or {})
            req = Request(target, data=body, headers=hdrs, method="POST")
            with urlopen(req, timeout=10) as resp:
                return 200 <= resp.status < 300
        except (OSError, HTTPError, URLError) as e:
            code = getattr(e, "code", None)
            self.last_error = str(e)
            self.last_error_transient = code in (429, 500, 502, 503, 504)
            log.warning("WebhookNotifier: %s", e)
            return False
        except Exception as e:
            self.last_error = str(e)
            self.last_error_transient = False
            log.warning("WebhookNotifier: %s", e)
            return False
