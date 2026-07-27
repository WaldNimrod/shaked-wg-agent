#!/usr/bin/env python3
"""validate_canon_enums.py — AOS v5 Enum-SSoT lint (M2-W7; validate_aos.sh Check 53).

Enforces L20 (single-source enums, anti-drift / P9), all BLOCKING:
  (A) Per enum kind, the migration 018 `enums` seed (the DB realisation the cockpit reads) and
      CANON_COCKPIT_ENUMS (the human SSoT) agree EXACTLY — bidirectional: no seeded value missing
      from the canon, and no canon enum-table value missing from the seed. This is "single source,
      zero duplicate definitions".
  (B) The legacy GATE_0–8 -> named-gate bridge is FULLY documented in the canon (every GATE_0..GATE_8
      present), so numeric gate references resolve via ONE table (controlled deprecation, P11).
  (C) A NEW bare numeric `GATE_n` in the canonical v5 LOD-standard (methodology/lod-standard/
      LOD_STANDARD_v5.md) is a FAIL — v5 uses named-gates only (CA14 §7); numbers are legacy
      read-only. Scoped to the v5 standard (not the to-be-archived legacy versions); vacuous-PASS
      until W4 creates that file.

Emits FAIL: lines to stdout. Exits 0 always — validate_aos.sh Check 53 decides blocking from the
FAIL: count (mirrors the Check 35 helper pattern).
"""
import re
import sys
from pathlib import Path

REPO_ROOT = (
    Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[4]
)
CANON = REPO_ROOT / "_aos/v5_characterization/synthesis/CANON_COCKPIT_ENUMS_v1.0.0.md"
MIG018 = REPO_ROOT / "core/db/migrations/018_canon_tables.sql"
LOD_STANDARD_V5 = REPO_ROOT / "methodology/lod-standard/LOD_STANDARD_v5.md"

# enum kinds the canon governs (CANON_COCKPIT_ENUMS §§1-5); `color` (hex) + roster/faq are excluded
_ENUM_KINDS = ("wp_status", "session_status", "gate", "track", "domain_status", "session_type")
# canon section id -> enum kind (§2b bridge, §6 colors, §7 impl are intentionally NOT enum-value sections)
_SECTION_KIND = {
    "1": "wp_status", "2": "gate", "3": "session_status",
    "4": "session_type", "4b": "domain_status", "5": "track",
}
_BRIDGE_GATES = {f"GATE_{i}" for i in range(0, 9)}  # full legacy set GATE_0..GATE_8
_TOKEN_RE = re.compile(r"`([A-Z][A-Z0-9_]*(?:-[0-9]+)?)`")          # backtick enum token (HG-1, GATE_0…)
_SEED_RE = re.compile(r"\('(\w+)','([^']+)'")                       # migration 018 seed row ('kind','VALUE',…
_HEADER_RE = re.compile(r"\n#{2,3}\s+(\d+b?)\.\s")                  # ## N. / ### Nb. section headers
_NUMERIC_GATE_RE = re.compile(r"\bGATE_\d+\b")  # GATE_0..GATE_99 (not just single digit)


def seed_by_kind(text: str) -> dict:
    out: dict[str, set] = {}
    for kind, value in _SEED_RE.findall(text):
        if kind in _ENUM_KINDS:  # skips roster (role,label,…), faq, and color hex rows
            out.setdefault(kind, set()).add(value)
    return out


def _sections(text: str) -> dict:
    """Split the canon doc into {section-id: body} on ## N. / ### Nb. headers. Each body runs to the
    NEXT header, so the §2 gate body excludes the nested ### 2b bridge sub-section."""
    parts = _HEADER_RE.split("\n" + text)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def canon_by_kind(text: str) -> dict:
    """Per-kind enum values from the canon doc. Values live in table rows (| `VALUE` | …); the track
    section (§5) lists them inline, so it is read whole."""
    sections = _sections(text)
    out = {k: set() for k in _ENUM_KINDS}
    for secid, kind in _SECTION_KIND.items():
        for line in sections.get(secid, "").splitlines():
            if line.lstrip().startswith("|") or kind == "track":
                out[kind] |= set(_TOKEN_RE.findall(line))
    return out


def lint(canon_text: str, seed_text: str, lod_standard: Path | None) -> list:
    """Return the list of FAIL/WARN strings (pure — used by tests with synthetic inputs)."""
    fails: list[str] = []
    seed = seed_by_kind(seed_text)
    canon = canon_by_kind(canon_text)

    # (A) bidirectional per-kind agreement
    for kind in _ENUM_KINDS:
        s, c = seed.get(kind, set()), canon.get(kind, set())
        for v in sorted(s - c):
            fails.append(f"FAIL: {kind}='{v}' seeded (migration 018) but not documented in CANON_COCKPIT_ENUMS")
        for v in sorted(c - s):
            fails.append(f"FAIL: {kind}='{v}' documented in CANON_COCKPIT_ENUMS but not seeded (migration 018)")

    # (B) full legacy bridge present — checked in the §2b bridge section specifically, so a stray
    #     GATE_n mention elsewhere cannot mask a deleted bridge row.
    bridge_tokens = set(_TOKEN_RE.findall(_sections(canon_text).get("2b", "")))
    missing = sorted(_BRIDGE_GATES - bridge_tokens)
    if missing:
        fails.append("FAIL: GATE_0–8 bridge incomplete in CANON_COCKPIT_ENUMS §2b — missing " + ", ".join(missing))

    # (C) new bare numeric GATE_n in the v5 LOD-standard
    if lod_standard is not None and lod_standard.is_file():
        for i, line in enumerate(lod_standard.read_text(encoding="utf-8").splitlines(), 1):
            for m in _NUMERIC_GATE_RE.finditer(line):
                fails.append(
                    f"FAIL: {lod_standard.name}:{i} uses legacy numeric {m.group(0)} — "
                    f"v5 uses named-gates only (CANON_COCKPIT_ENUMS §2)"
                )
    return fails


def main() -> int:
    if not CANON.is_file() or not MIG018.is_file():
        print(f"FAIL: enum-SSoT source missing (canon={CANON.is_file()}, mig018={MIG018.is_file()})")
        return 0
    fails = lint(CANON.read_text(encoding="utf-8"), MIG018.read_text(encoding="utf-8"), LOD_STANDARD_V5)
    for ln in fails:
        print(ln)
    if not fails:
        total = sum(len(v) for v in seed_by_kind(MIG018.read_text(encoding="utf-8")).values())
        print(f"OK: {total} enum values agree seed<->canon across {len(_ENUM_KINDS)} kinds; GATE_0–8 bridge locked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
