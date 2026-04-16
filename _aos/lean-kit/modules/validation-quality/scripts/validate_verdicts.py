#!/usr/bin/env python3
"""validate_verdicts.py — AOS Verdict File Validator (V318)
Check: V-VERDICT
Exit: 0 = 0 FAIL, 1 = any FAIL
"""
import sys, os, re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[4]

REQUIRED_FIELDS = {
    "team_50":  ["id","from","to","type","work_package","gate","date",
                  "part_a_verdict","part_b_verdict","overall_verdict"],
    "team_90":  ["id","from","to","type","work_package","gate","date",
                  "verdict","findings_blocker"],
    "team_190": ["id","from","to","type","work_package","gate","date",
                  "verdict","criteria_total","criteria_pass","criteria_fail"],
}

PASS_COUNT = FAIL_COUNT = SKIP_COUNT = 0

def log_pass(msg):
    global PASS_COUNT
    print(f"[PASS] V-VERDICT: {msg}")
    PASS_COUNT += 1

def log_fail(msg):
    global FAIL_COUNT
    print(f"[FAIL] V-VERDICT: {msg}")
    FAIL_COUNT += 1

def log_skip(msg):
    global SKIP_COUNT
    print(f"[SKIP] V-VERDICT: {msg}")
    SKIP_COUNT += 1

def parse_frontmatter(filepath):
    content = Path(filepath).read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None

def validate_verdict_file(filepath, team_id):
    fname = Path(filepath).name
    fm = parse_frontmatter(filepath)
    if fm is None:
        log_fail(f"{team_id}/{fname} — no YAML frontmatter (cannot validate)")
        return
    required = REQUIRED_FIELDS[team_id]
    missing = [f for f in required if f not in fm]
    if missing:
        log_fail(f"{team_id}/{fname} — missing fields: {', '.join(missing)}")
    else:
        log_pass(f"{team_id}/{fname} — {len(required)}/{len(required)} fields present")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AOS Verdict File Validator")
    parser.add_argument("--team", default=None,
                        help="Restrict to one team (team_50, team_90, team_190)")
    parser.add_argument("--wp", default=None,
                        help="Filter to verdicts with matching work_package field")
    args = parser.parse_args()

    comm_dir = REPO_ROOT / "_COMMUNICATION"
    teams = [args.team] if args.team else ["team_50", "team_90", "team_190"]
    wp_filter = args.wp

    total_files = 0
    for team_id in teams:
        team_dir = comm_dir / team_id
        if not team_dir.exists():
            log_skip(f"{team_id}/ — directory not found")
            continue
        verdict_files = sorted(team_dir.rglob("*VERDICT*.md"))
        if not verdict_files:
            log_skip(f"{team_id}/ — no VERDICT files found")
            continue
        for vf in verdict_files:
            if wp_filter:
                fm = parse_frontmatter(vf)
                if fm is None or str(fm.get("work_package","")) != wp_filter:
                    continue
            if team_id not in REQUIRED_FIELDS:
                log_skip(f"{team_id}/{vf.name} — no field spec for this team")
                continue
            validate_verdict_file(vf, team_id)
            total_files += 1

    print(f"{'─' * 50}")
    print(f"RESULT: {PASS_COUNT} PASS · {FAIL_COUNT} FAIL · {SKIP_COUNT} SKIP ({total_files} files scanned)")
    sys.exit(1 if FAIL_COUNT > 0 else 0)

if __name__ == "__main__":
    main()
