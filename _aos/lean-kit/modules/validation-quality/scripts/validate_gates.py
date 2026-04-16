#!/usr/bin/env python3
"""validate_gates.py — AOS Gate History Validator (V318)
Checks: V-GATE-1 (LOD progression), V-GATE-2 (report_path exists)
Exit: 0 = 0 FAIL, 1 = any FAIL
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[4]

LOD_STATUS_ENUM = {
    "DRAFT", "LOD100_APPROVED", "LOD200_APPROVED", "LOD300_APPROVED",
    "LOD400_APPROVED", "LOD500_LOCKED", "SUPERSEDED", "ARCHIVED"
}

# Valid forward progressions (each state → allowed next states)
VALID_TRANSITIONS = {
    "DRAFT":            {"LOD100_APPROVED", "ARCHIVED"},
    "LOD100_APPROVED":  {"LOD200_APPROVED", "LOD300_APPROVED", "ARCHIVED"},
    "LOD200_APPROVED":  {"LOD400_APPROVED", "ARCHIVED"},
    "LOD300_APPROVED":  {"LOD400_APPROVED", "ARCHIVED"},
    "LOD400_APPROVED":  {"LOD500_LOCKED", "ARCHIVED"},
    "LOD500_LOCKED":    {"SUPERSEDED", "ARCHIVED"},
    "SUPERSEDED":       {"ARCHIVED"},
    "ARCHIVED":         set(),
}

PASS_COUNT = FAIL_COUNT = SKIP_COUNT = 0

def log_pass(check, msg):
    global PASS_COUNT
    print(f"[PASS] {check}: {msg}")
    PASS_COUNT += 1

def log_fail(check, msg):
    global FAIL_COUNT
    print(f"[FAIL] {check}: {msg}")
    FAIL_COUNT += 1

def log_skip(check, msg):
    global SKIP_COUNT
    print(f"[SKIP] {check}: {msg}")
    SKIP_COUNT += 1

def check_progression(wp_id, lod_status, gate_history):
    """V-GATE-1: Validate lod_status enum and progression evidence (BR-16, BR-17).

    BR-16: lod_status must be a valid enum value.
    BR-17: lod_status LOD500_LOCKED requires evidence of L-GATE_SPEC PASS
           in gate_history (proving LOD400_APPROVED was reached). A WP
           with LOD500_LOCKED and empty gate_history has no evidence of
           required intermediate approvals and FAILS this check.
    BR-19: DRAFT with empty gate_history is SKIP (nothing to validate).
    """
    if lod_status not in LOD_STATUS_ENUM:
        log_fail("V-GATE-1", f"{wp_id} — invalid lod_status: '{lod_status}' (not in allowed enum)")
        return

    if lod_status == "DRAFT" and not gate_history:
        log_skip("V-GATE-1", f"{wp_id} — DRAFT with empty gate_history, skip (BR-19)")
        return

    # BR-17: LOD500_LOCKED requires L-GATE_SPEC PASS evidence in gate_history
    if "LOD500" in lod_status:
        if not gate_history:
            log_fail("V-GATE-1",
                     f"{wp_id} — lod_status '{lod_status}' but gate_history is empty "
                     f"(no L-GATE_SPEC PASS evidence for LOD400_APPROVED — BR-17)")
            return
        has_spec_pass = any(
            str(e.get("gate", "")) == "L-GATE_SPEC" and str(e.get("result", "")).upper() == "PASS"
            for e in gate_history
        )
        if not has_spec_pass:
            log_fail("V-GATE-1",
                     f"{wp_id} — lod_status '{lod_status}' but no L-GATE_SPEC PASS entry "
                     f"in gate_history (required as LOD400_APPROVED evidence — BR-17)")
        else:
            log_pass("V-GATE-1",
                     f"{wp_id} — '{lod_status}' with L-GATE_SPEC PASS evidence confirmed (BR-17)")
    else:
        log_pass("V-GATE-1", f"{wp_id} — lod_status '{lod_status}' is a valid enum value (BR-16)")

def check_report_paths(wp_id, gate_history):
    """V-GATE-2: Every PASS gate_history entry must have an existing report_path (BR-18).

    BR-18: The 'report_path' field is authoritative. No alternative field name
    (e.g., 'verdict_ref') is accepted as a substitute.
    """
    if not gate_history:
        log_skip("V-GATE-2", f"{wp_id} — gate_history empty, skip")
        return

    has_pass_entries = False
    for i, entry in enumerate(gate_history):
        result = str(entry.get("result", "")).upper()
        if result != "PASS":
            continue
        has_pass_entries = True
        # BR-18: strictly require 'report_path' — no fallback to 'verdict_ref'
        report_path = entry.get("report_path")
        if not report_path:
            log_fail("V-GATE-2",
                     f"{wp_id} — gate_history[{i}] ({entry.get('gate','?')}) PASS entry "
                     f"missing 'report_path' field (BR-18; 'verdict_ref' is not accepted)")
            continue
        full_path = REPO_ROOT / report_path
        if not full_path.exists():
            log_fail("V-GATE-2",
                     f"{wp_id} — gate_history[{i}] ({entry.get('gate','?')}) report_path "
                     f"not found on filesystem: {report_path}")
        else:
            log_pass("V-GATE-2",
                     f"{wp_id} — gate_history[{i}] ({entry.get('gate','?')}) report_path exists: {report_path}")

    if not has_pass_entries:
        log_skip("V-GATE-2", f"{wp_id} — no PASS entries in gate_history, skip")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AOS Gate History Validator")
    parser.add_argument("--wp", default=None,
                        help="Validate only this WP ID")
    parser.add_argument("--roadmap", default=None,
                        help="Path to roadmap.yaml (default: _aos/roadmap.yaml)")
    args = parser.parse_args()

    roadmap_path = Path(args.roadmap) if args.roadmap else REPO_ROOT / "_aos" / "roadmap.yaml"
    if not roadmap_path.exists():
        print(f"FATAL: roadmap.yaml not found at {roadmap_path}")
        sys.exit(1)

    with open(roadmap_path) as f:
        roadmap = yaml.safe_load(f) or {}

    wps = roadmap.get("work_packages", [])
    if not wps:
        print("FATAL: No work_packages found in roadmap.yaml")
        sys.exit(1)

    if args.wp:
        wps = [w for w in wps if w.get("id") == args.wp]
        if not wps:
            print(f"FATAL: WP '{args.wp}' not found in roadmap.yaml")
            sys.exit(1)

    print(f"validate_gates.py — reading {roadmap_path.name} ({len(wps)} WPs)")
    print()

    for wp in wps:
        wp_id = wp.get("id", "UNKNOWN")
        lod_status = str(wp.get("lod_status", "DRAFT"))
        gate_history = wp.get("gate_history") or []
        check_progression(wp_id, lod_status, gate_history)
        check_report_paths(wp_id, gate_history)

    print(f"{'─' * 50}")
    print(f"RESULT: {PASS_COUNT} PASS · {FAIL_COUNT} FAIL · {SKIP_COUNT} SKIP (over {len(wps)} WPs)")
    sys.exit(1 if FAIL_COUNT > 0 else 0)

if __name__ == "__main__":
    main()
