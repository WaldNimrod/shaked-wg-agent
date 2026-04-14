"""Orchestrate multi-channel digest notifications."""
from __future__ import annotations

import logging
import time
from typing import Any

from shaked_wg_agent.notifier.digest_builder import build_digest_payload
from shaked_wg_agent.notifier.discord_notifier import DiscordNotifier
from shaked_wg_agent.notifier.email_notifier import EmailNotifier
from shaked_wg_agent.notifier.ntfy_notifier import NtfyNotifier
from shaked_wg_agent.notifier.telegram_notifier import TelegramNotifier
from shaked_wg_agent.notifier.webhook_notifier import WebhookNotifier

log = logging.getLogger("shaked_wg_agent.notifier")

_REGISTRY: dict[str, type] = {
    "email": EmailNotifier,
    "telegram": TelegramNotifier,
    "discord": DiscordNotifier,
    "ntfy": NtfyNotifier,
    "webhook": WebhookNotifier,
}


def _flatten_channel(ch: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in ch.items() if k != "params"}
    out.update(ch.get("params") or {})
    return out


def _send_once(
    notifier: Any,
    payload: dict[str, Any],
) -> bool:
    ok = notifier.send(payload)
    return bool(ok)


def _send_with_retry(notifier: Any, payload: dict[str, Any]) -> bool:
    if _send_once(notifier, payload):
        return True
    transient = getattr(notifier, "last_error_transient", False)
    if not transient:
        return False
    time.sleep(5)
    return _send_once(notifier, payload)


def notify_digest(
    profile: dict[str, Any],
    city: dict[str, Any],
    run_record: dict[str, Any],
    new_listings: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Send digest to all enabled channels. Never raises."""
    try:
        notif = profile.get("notifications")
        if notif is None:
            return None
        channels_raw = notif.get("channels") or []
        if not channels_raw:
            return None

        enabled = [c for c in channels_raw if c.get("enabled")]
        if not enabled:
            return None

        if len(enabled) > 5:
            log.error("More than 5 notification channels — truncating to 5")
            enabled = enabled[:5]

        if not new_listings:
            return None

        payload = build_digest_payload(profile, city, run_record, new_listings)
        results: list[dict[str, Any]] = []
        total_sent = 0
        total_failed = 0

        for ch in enabled:
            flat = _flatten_channel(ch)
            ctype = flat.get("type", "")
            label = flat.get("label")
            cls = _REGISTRY.get(ctype)
            if cls is None:
                log.warning("Unknown notification channel type: %s", ctype)
                results.append(
                    {
                        "type": ctype,
                        "label": label,
                        "success": False,
                        "error": "unknown channel type",
                    }
                )
                total_failed += 1
                continue
            notifier = cls(flat)
            ok = _send_with_retry(notifier, payload)
            err = None if ok else (getattr(notifier, "last_error", None) or "send failed")
            results.append(
                {
                    "type": ctype,
                    "label": label,
                    "success": ok,
                    "error": err,
                }
            )
            if ok:
                total_sent += 1
            else:
                total_failed += 1

        return {
            "channels": results,
            "total_sent": total_sent,
            "total_failed": total_failed,
        }
    except Exception:
        log.exception("notify_digest failed")
        return {"channels": [], "total_sent": 0, "total_failed": 0}
