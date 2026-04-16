#!/usr/bin/env python3
"""
Conservative rate probe: sequential GETs with fixed delay; STOP at first CF challenge.
Do not use for aggressive load testing.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

POC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(POC_DIR))

from common import DEFAULT_SEARCH_URL, USER_AGENTS, looks_like_bot_wall  # noqa: E402

DELAY = float(os.environ.get("RATE_PROBE_DELAY_SEC", "4"))
MAX_REQ = int(os.environ.get("RATE_PROBE_MAX", "15"))


def main() -> int:
    url = os.environ.get("YAD2_TEST_URL", DEFAULT_SEARCH_URL)
    ua = USER_AGENTS["chrome_desktop"]
    events: list[dict[str, object]] = []
    for i in range(MAX_REQ):
        time.sleep(DELAY)
        t0 = time.monotonic()
        try:
            r = requests.get(
                url,
                headers={"User-Agent": ua, "Accept-Language": "he-IL"},
                timeout=25,
            )
            body = r.text or ""
            wall = looks_like_bot_wall(body, "")
            dt = time.monotonic() - t0
            events.append(
                {
                    "n": i + 1,
                    "status": r.status_code,
                    "bot_wall": wall,
                    "elapsed_sec": round(dt, 3),
                    "bytes": len(body.encode("utf-8")),
                }
            )
            if wall or r.status_code in (403, 429, 503):
                events.append({"stopped": True, "reason": "challenge_or_error_status"})
                break
        except requests.RequestException as e:
            events.append({"n": i + 1, "error": str(e)})
            break

    out = {"url": url, "delay_sec": DELAY, "max_planned": MAX_REQ, "events": events}
    path = POC_DIR / "rate_limit_trace.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
