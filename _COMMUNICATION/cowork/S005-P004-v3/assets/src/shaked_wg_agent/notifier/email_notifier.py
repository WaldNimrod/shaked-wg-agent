"""SMTP email digest notifier."""
from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from shaked_wg_agent.notifier.base import BaseNotifier

log = logging.getLogger("shaked_wg_agent.notifier")


class EmailNotifier(BaseNotifier):
    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__(config)
        self._available = bool(
            os.environ.get("SMTP_HOST")
            and os.environ.get("SMTP_USER")
            and os.environ.get("SMTP_PASS")
            and os.environ.get("SMTP_FROM")
        )
        if not self._available:
            log.warning("EmailNotifier: missing SMTP env vars — channel disabled")

    def format_message(self, digest_payload: dict[str, Any]) -> str:
        profile = digest_payload.get("profile_name", "")
        city = digest_payload.get("city_name", "")
        total = digest_payload.get("total_new", 0)
        ts = digest_payload.get("scan_timestamp", "")[:16].replace("T", " ")
        lines = [
            f"<html><body><h2>{profile} — {city}</h2>",
            f"<p>{total} neue Angebote gefunden am {ts}</p><ul>",
        ]
        for lst in digest_payload.get("listings", []):
            title = lst.get("title", "")
            url = lst.get("direct_url", "#")
            price = lst.get("price_chf")
            price_s = f"CHF {price}/Mt." if price is not None else "Preis nicht angegeben"
            dist = lst.get("district", "")
            score = int(lst.get("relevance_score", 0) or 0)
            color = "#2e7d32" if score >= 70 else "#e65100" if score >= 40 else "#c62828"
            vegan = lst.get("vegan_signal") or ""
            trans = ", ".join(lst.get("transit_match_lines") or [])
            lines.append(
                f'<li style="margin:8px 0"><a href="{url}">{title}</a> — {price_s} — {dist} — '
                f'<span style="color:{color}">Score {score}</span>'
                f"{' — ' + vegan if vegan else ''}{' — T' + trans.replace(',', ', T') if trans else ''}</li>"
            )
        lines.append("</ul><p><small>Generiert von Shaked WG Agent</small></p></body></html>")
        return "".join(lines)

    def send(self, digest_payload: dict[str, Any]) -> bool:
        if not self._available:
            return False
        recipients = self.config.get("recipients") or []
        if not recipients:
            log.warning("EmailNotifier: no recipients")
            return False
        try:
            html = self.format_message(digest_payload)
            host = os.environ["SMTP_HOST"]
            port = int(os.environ.get("SMTP_PORT", "587"))
            user = os.environ["SMTP_USER"]
            password = os.environ["SMTP_PASS"]
            from_addr = os.environ["SMTP_FROM"]
            subj = (
                f"[Shaked WG] {digest_payload.get('profile_name', '')}: "
                f"{digest_payload.get('total_new', 0)} neue Angebote"
            )
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subj
            msg["From"] = from_addr
            msg["To"] = ", ".join(recipients)
            msg.attach(MIMEText(html, "html", "utf-8"))

            with smtplib.SMTP(host, port, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(user, password)
                smtp.sendmail(from_addr, recipients, msg.as_string())
            return True
        except OSError as e:
            self.last_error = str(e)
            self.last_error_transient = True
            log.warning("EmailNotifier send failed: %s", e)
            return False
        except smtplib.SMTPAuthenticationError as e:
            self.last_error = str(e)
            self.last_error_transient = False
            log.warning("EmailNotifier auth failed: %s", e)
            return False
        except Exception as e:
            self.last_error = str(e)
            self.last_error_transient = False
            log.warning("EmailNotifier send failed: %s", e)
            return False
