#!/usr/bin/env python3
"""validate_qa_request_enums.py — AOS QA Request Enum Lint (AOS-V324-WP-QA-ENUM-LINT)
Validates controlled-vocabulary fields in QA_REQUEST.md artifacts.
Exits 0 always (advisory); emits WARN: lines to stdout on violations.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML not installed. Run: pip3 install pyyaml")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
D2_PATH = SCRIPT_DIR.parent / "docs" / "QA_ENUM_LINT_STANDARD_v1.0.0.md"
REPO_ROOT = Path(__file__).resolve().parents[4]

VALIDATED_FIELDS = ["verdict", "confidence", "blocked_reason_code"]

_YAML_BLOCK_RE = re.compile(
    r"##\s+Canonical Enum Values\s*\n+```yaml\s*\n(.*?)```",
    re.DOTALL,
)


def load_enums(d2_path: Path) -> dict:
    text = d2_path.read_text(encoding="utf-8")
    m = _YAML_BLOCK_RE.search(text)
    if not m:
        print(f"FATAL: Could not parse enum block from {d2_path}")
        sys.exit(1)
    return yaml.safe_load(m.group(1)) or {}


def parse_frontmatter(filepath: Path) -> dict | None:
    try:
        content = filepath.read_text(encoding="utf-8")
    except OSError:
        return None
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None


def validate_file(filepath: Path, root: Path, enums: dict) -> int:
    """Returns number of warnings emitted."""
    fm = parse_frontmatter(filepath)
    if fm is None:
        return 0
    try:
        rel = filepath.relative_to(root)
    except ValueError:
        rel = filepath
    warns = 0
    for field in VALIDATED_FIELDS:
        if field not in fm:
            continue
        value = fm[field]
        if value is None:
            continue
        allowed = enums.get(field, [])
        if str(value) not in allowed:
            choices = ", ".join(allowed)
            print(f"WARN: {rel} — {field}: got '{value}', expected one of: {choices}")
            warns += 1
    return warns


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO_ROOT
    enums = load_enums(D2_PATH)

    comm_dir = root / "_COMMUNICATION"
    if not comm_dir.exists():
        print(f"# validate_qa_request_enums: _COMMUNICATION/ not found under {root} — nothing to scan")
        sys.exit(0)

    files = sorted(comm_dir.rglob("QA_REQUEST.md"))
    total_warns = 0
    for f in files:
        total_warns += validate_file(f, root, enums)

    scanned = len(files)
    print(f"{'─' * 50}")
    print(f"QA enum lint: {scanned} QA_REQUEST.md file(s) scanned — {total_warns} violation(s)")
    sys.exit(0)


if __name__ == "__main__":
    main()
