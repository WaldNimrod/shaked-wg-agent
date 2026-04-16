#!/usr/bin/env python3
"""validate_lod.py — AOS LOD Document Validator (V318)
Checks: V-LOD-1..7
Exit: 0 = 0 FAIL, 1 = any FAIL
"""
import sys, os, re, glob
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[4]  # lean-kit is 4 levels up from scripts/
WP_GLOB = str(REPO_ROOT / "_aos" / "work_packages" / "*")

LOD_STATUS_ENUM = {
    "DRAFT", "LOD100_APPROVED", "LOD200_APPROVED", "LOD300_APPROVED",
    "LOD400_APPROVED", "LOD500_LOCKED", "SUPERSEDED", "ARCHIVED"
}
REQUIRED_FRONTMATTER = [
    "lod_target", "lod_status", "track", "authoring_team",
    "consuming_team", "date", "version", "work_package_id", "milestone_ref"
]
LOD200_HEADERS = [
    "Problem Statement", "Solution Concept", "Major Components",
    "Primary Flow", "Governance Impact Map", "Open Decisions",
    "Initial Success Criteria", "Dependencies and Constraints",
    "Out of Scope", "Risk Assessment", "Track Declaration"
]
LOD300_HEADERS = [
    "Scope", "System Behavior Overview", "Script Interface Contracts",
    "State Machines", "Business Rules", "Resolved Open Decisions",
    "Gate Integration", "Test Suite Design", "Interface Contracts",
    "Acceptance Criteria", "Deferred"
]
LOD400_HEADERS = [
    "Scope", "Technical Architecture", "Script Specifications",
    "Fixture Specifications", "Test Script Specifications",
    "Interface Contracts", "Governance Document Update Manifest",
    "Deployment Instructions", "Rollback Procedure", "Acceptance Criteria"
]

VERSION_RE = re.compile(r'^v\d+\.\d+\.\d+$')
AC_VALID_RE = re.compile(r'\bAC-\d{3}\b')
AC_INVALID_RE = re.compile(r'\bAC-\d{1,2}(?!\d)\b')
PLACEHOLDER_RE = re.compile(r'\b(TBD|TODO|\[placeholder\]|to be determined)\b', re.IGNORECASE)
FENCED_CODE_RE = re.compile(r'```.*?```', re.DOTALL)

def strip_code_blocks(text):
    """Remove fenced code block content before prose scanning.
    BR-04/BR-05: AC format and placeholder checks apply to prose only,
    not to code examples or fixture specimens inside ``` blocks.
    """
    return FENCED_CODE_RE.sub('', text)

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

def parse_frontmatter(filepath):
    """Return (dict, body_text) or (None, full_text) if no frontmatter."""
    content = Path(filepath).read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        return None, content
    return fm, parts[2]

def detect_lod_level(fm, override=None):
    if override:
        return override
    val = str(fm.get("lod_target", fm.get("lod_status", ""))).upper()
    for level in ["LOD500", "LOD400", "LOD300", "LOD200", "LOD100"]:
        if level in val:
            return level
    return "UNKNOWN"

def find_lod_files(wp_dir):
    """Find all LOD*.md files in a WP directory."""
    return sorted(Path(wp_dir).glob("LOD*.md"))

def validate_file(filepath, lod_override=None):
    fm, body = parse_frontmatter(filepath)
    fname = Path(filepath).name

    if fm is None:
        log_fail("V-LOD-1", f"{fname} — no YAML frontmatter found")
        log_skip("V-LOD-2", f"{fname} — skipped (frontmatter parse failed)")
        log_skip("V-LOD-3", f"{fname} — skipped (frontmatter parse failed)")
        log_skip("V-LOD-4", f"{fname} — skipped (frontmatter parse failed)")
        log_skip("V-LOD-5", f"{fname} — skipped (frontmatter parse failed)")
        log_skip("V-LOD-6", f"{fname} — skipped (frontmatter parse failed)")
        log_skip("V-LOD-7", f"{fname} — skipped (frontmatter parse failed)")
        return

    natural_lod = detect_lod_level(fm)
    lod = detect_lod_level(fm, lod_override)

    # V-LOD-1: Frontmatter completeness
    missing = [f for f in REQUIRED_FRONTMATTER if f not in fm]
    if missing:
        log_fail("V-LOD-1", f"{fname} — missing fields: {', '.join(missing)}")
    else:
        log_pass("V-LOD-1", f"{fname} — frontmatter complete ({len(REQUIRED_FRONTMATTER)}/{len(REQUIRED_FRONTMATTER)} fields)")

    # V-LOD-2: Required section headers
    if lod == "LOD400":
        required_headers = LOD400_HEADERS
    elif lod == "LOD300":
        required_headers = LOD300_HEADERS
    elif lod == "LOD200":
        required_headers = LOD200_HEADERS
    else:
        required_headers = []

    if required_headers:
        if lod_override and lod != natural_lod:
            log_skip("V-LOD-2", f"{fname} — header check skipped (--lod override {lod} != document level {natural_lod})")
        else:
            missing_hdrs = [h for h in required_headers if not re.search(rf'#{{1,3}}\s+.*{re.escape(h)}', body, re.IGNORECASE)]
            if missing_hdrs:
                log_fail("V-LOD-2", f"{fname} — missing headers: {', '.join(missing_hdrs)}")
            else:
                log_pass("V-LOD-2", f"{fname} — all {len(required_headers)} required headers present")
    else:
        log_skip("V-LOD-2", f"{fname} — no header requirements for level {lod}")

    # V-LOD-3: AC numbering format (LOD400 only)
    # BR-04: fenced code blocks excluded — prose only
    if lod == "LOD400":
        prose = strip_code_blocks(body)
        bad_acs = AC_INVALID_RE.findall(prose)
        if bad_acs:
            log_fail("V-LOD-3", f"{fname} — invalid AC format in prose: {bad_acs[:5]} (use AC-001 not AC-1)")
        else:
            ac_count = len(AC_VALID_RE.findall(prose))
            log_pass("V-LOD-3", f"{fname} — AC numbering format valid in prose ({ac_count} ACs found)")
    else:
        log_skip("V-LOD-3", f"{fname} — AC check only applies to LOD400")

    # V-LOD-4: Placeholder text (LOD400 only — LOD300 may have TBD in §10 Deferred)
    # BR-05: fenced code blocks excluded — prose only
    if lod == "LOD400":
        prose = strip_code_blocks(body)
        matches = PLACEHOLDER_RE.findall(prose)
        if matches:
            lines_with = []
            for i, line in enumerate(prose.splitlines(), 1):
                if PLACEHOLDER_RE.search(line):
                    lines_with.append(i)
            log_fail("V-LOD-4", f"{fname} — placeholder text found in prose: {len(matches)} instances on lines {lines_with[:5]}")
        else:
            log_pass("V-LOD-4", f"{fname} — no placeholder text found in prose")
    else:
        log_skip("V-LOD-4", f"{fname} — placeholder check only applies to LOD400")

    # V-LOD-5: lod_status enum
    lod_status_val = str(fm.get("lod_status", ""))
    if lod_status_val in LOD_STATUS_ENUM:
        log_pass("V-LOD-5", f"{fname} — lod_status enum valid ({lod_status_val})")
    else:
        log_fail("V-LOD-5", f"{fname} — lod_status invalid: '{lod_status_val}' (allowed: {sorted(LOD_STATUS_ENUM)})")

    # V-LOD-6: version format
    version_val = str(fm.get("version", ""))
    if VERSION_RE.match(version_val):
        log_pass("V-LOD-6", f"{fname} — version format valid ({version_val})")
    else:
        log_fail("V-LOD-6", f"{fname} — version format invalid: '{version_val}' (expected v{{N}}.{{N}}.{{N}})")

    # V-LOD-7: spec_ref exists (LOD500 only)
    if lod == "LOD500":
        spec_ref = fm.get("spec_ref")
        if not spec_ref:
            log_fail("V-LOD-7", f"{fname} — LOD500 document missing spec_ref field")
        else:
            ref_path = REPO_ROOT / spec_ref
            if ref_path.exists():
                log_pass("V-LOD-7", f"{fname} — spec_ref exists ({spec_ref})")
            else:
                log_fail("V-LOD-7", f"{fname} — spec_ref not found: {spec_ref}")
    else:
        log_skip("V-LOD-7", f"{fname} — spec_ref check only applies to LOD500")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AOS LOD Document Validator")
    parser.add_argument("wp_path", nargs="?", default=None,
                        help="WP directory to validate (default: active WP)")
    parser.add_argument("--all", action="store_true",
                        help="Validate all WP directories under _aos/work_packages/")
    parser.add_argument("--lod", default=None,
                        help="Override LOD level detection (100/200/300/400/500)")
    args = parser.parse_args()

    if args.all:
        wp_dirs = [d for d in Path(REPO_ROOT / "_aos" / "work_packages").iterdir() if d.is_dir()]
        if not wp_dirs:
            print("FATAL: No WP directories found under _aos/work_packages/")
            sys.exit(1)
        print(f"validate_lod.py — scanning {len(wp_dirs)} WP directories\n")
    elif args.wp_path:
        wp_dirs = [Path(args.wp_path)]
    else:
        # Default: find active WP from .active_wp or first IN_PROGRESS in roadmap
        active_wp_file = REPO_ROOT / "_aos" / ".active_wp"
        if active_wp_file.exists():
            wp_id = active_wp_file.read_text().strip()
            wp_dirs = [REPO_ROOT / "_aos" / "work_packages" / wp_id]
        else:
            print("FATAL: No WP path given and no _aos/.active_wp file found")
            print("Usage: ./validate_lod.sh <wp-dir> OR ./validate_lod.sh --all")
            sys.exit(1)

    lod_override = f"LOD{args.lod}" if args.lod else None

    for wp_dir in wp_dirs:
        lod_files = find_lod_files(wp_dir)
        if not lod_files:
            print(f"[SKIP] {wp_dir.name} — no LOD*.md files found")
            continue
        print(f"validate_lod.py — {wp_dir.name}")
        for f in lod_files:
            validate_file(f, lod_override)
        print()

    print(f"{'─' * 50}")
    print(f"RESULT: {PASS_COUNT} PASS · {FAIL_COUNT} FAIL · {SKIP_COUNT} SKIP")
    sys.exit(1 if FAIL_COUNT > 0 else 0)

if __name__ == "__main__":
    main()
