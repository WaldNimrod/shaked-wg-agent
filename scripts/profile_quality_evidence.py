#!/usr/bin/env python3
"""Print settlement/budget/score breakdown for a profile (stdout, markdown-friendly).

Run from repo root after a scan, e.g.:
  python3 scripts/profile_quality_evidence.py --profile dror
"""
from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from shaked_wg_agent.config import load_config  # noqa: E402
from shaked_wg_agent.persistence import load_listings, load_runs  # noqa: E402
from shaked_wg_agent.scorer import _settlement_allowed, score_listing  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", required=True, help="profile_id")
    args = ap.parse_args()
    cfg = load_config(args.profile)
    pid = cfg.profile.profile_id
    allow = cfg.city.settlement_allowlist
    rows = [r for r in load_listings() if r.get("profile_id") == pid]
    runs = [r for r in load_runs() if r.get("profile_id") == pid]
    last_run = runs[0] if runs else None

    geo_ok = sum(1 for r in rows if not allow or _settlement_allowed(r, allow))
    geo_fail = len(rows) - geo_ok

    score_gt0 = 0
    samples_in: list[tuple[str, int, str]] = []
    samples_out: list[tuple[str, str]] = []
    for r in rows:
        s = score_listing(r, cfg.profile, cfg.city)
        if s > 0:
            score_gt0 += 1
            if len(samples_in) < 5:
                lid = str(r.get("listing_id", ""))
                samples_in.append((lid, s, str(r.get("district", ""))[:80]))
        else:
            if len(samples_out) < 5 and allow:
                samples_out.append(
                    (
                        str(r.get("listing_id", "")),
                        (str(r.get("district", "")) + " / " + str(r.get("title", "")))[:120],
                    )
                )

    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    print("# Profile data quality snapshot")
    print()
    print(f"- **Generated:** {now}")
    print(f"- **profile_id:** `{pid}`")
    print(f"- **city_id:** `{cfg.city.city_id}`")
    print(f"- **country:** `{cfg.city.country}`")
    print(f"- **settlement_allowlist entries:** {len(allow)}")
    print(f"- **listings in data store (this profile):** {len(rows)}")
    print(f"- **rows matching settlement substring gate:** {geo_ok}")
    print(f"- **rows not matching settlement gate:** {geo_fail}")
    print(f"- **rows with relevance_score > 0 (after budget + geo):** {score_gt0}")
    if last_run:
        print(f"- **last run id:** `{last_run.get('run_id')}`")
        print(f"- **last run timestamp:** `{last_run.get('run_timestamp')}`")
        print(f"- **last report_url:** `{last_run.get('report_url')}`")
    print()
    print("## Sample in-region / positive-score rows (up to 5)")
    print()
    for lid, sc, dist in samples_in:
        print(f"- `{lid}` score={sc} district={dist!r}")
    if not samples_in:
        print("(none)")
    print()
    print("## Sample rows failing geo gate (up to 5, when allowlist non-empty)")
    print()
    for lid, hint in samples_out:
        print(f"- `{lid}` {hint!r}")
    if not samples_out:
        print("(none or allowlist empty)")
    print()
    print("## Notes")
    print()
    print(
        "- Settlement matching is **substring** over district + location_text + title + summary."
    )
    print("- Score 0 also results from over-budget listings (independent of geo).")
    print("- Re-run a full scan after deploy so stored `relevance_score` matches this logic.")


if __name__ == "__main__":
    main()
