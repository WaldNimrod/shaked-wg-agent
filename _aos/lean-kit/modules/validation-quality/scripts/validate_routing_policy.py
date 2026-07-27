#!/usr/bin/env python3
"""validate_routing_policy.py — AOS v5 routing-policy anti-drift lint (M7-P1-WP1; validate_aos.sh Check 60).

The Check-53 clone for CANON_WP_ROUTING_POLICY (LOD300 §8 / AC-3 / AC-9). Enforces, BLOCKING:
  The CHECKED key-set of `core/config/routing_policy.yaml` (the hub-file SSoT) and the seed of the
  `routing_policy` projection (migration 027) agree EXACTLY — bidirectional: no key in the file
  missing from the projection, none in the projection missing from the file. This is the
  "edited the file, forgot to re-seed" (and vice-versa) guard.

CHECKED key-set (LOD300 §8 — flat, enumerable; rule BODIES are value-compared, not key-enumerated):
  params.*  ·  weights.*  ·  outputs.<output>.rules[].id (track_rules normalised to .rules.)  ·
  outputs.<output>.floors.*  ·  outputs.<output>.decisive_tier.*  ·  modes.*

Emits FAIL: lines to stdout. Exits 0 always — validate_aos.sh Check 60 decides blocking from the
FAIL: count (mirrors validate_canon_enums.py / the Check 35 helper pattern). Static file-vs-seed
comparison — needs no live DB.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except Exception:  # noqa: BLE001 — PyYAML absent → vacuous PASS (validate_aos already gates on PyYAML)
    yaml = None

REPO_ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[4]
POLICY = REPO_ROOT / "core/config/routing_policy.yaml"
MIG027 = REPO_ROOT / "core/db/migrations/027_routing_policy_projection.sql"

# A seed row is ('checked.key','group') — first capture is the checked key (mirrors validate_canon_enums _SEED_RE).
_SEED_RE = re.compile(r"\('([^']+)','([^']+)'\)")


def checked_keys_from_policy(policy: dict) -> set[str]:
    """The flat CHECKED key-set per LOD300 §8. `track_rules` is normalised to `.rules.` so process,
    who_builds and environment share one rule-list shape."""
    keys: set[str] = set()
    for k in (policy.get("params") or {}):
        keys.add(f"params.{k}")
    for k in (policy.get("weights") or {}):
        keys.add(f"weights.{k}")
    for oname, obody in (policy.get("outputs") or {}).items():
        if not isinstance(obody, dict):
            continue
        for r in (obody.get("rules") or obody.get("track_rules") or []):
            if isinstance(r, dict) and "id" in r:
                keys.add(f"outputs.{oname}.rules.{r['id']}")
        for fk in (obody.get("floors") or {}):
            keys.add(f"outputs.{oname}.floors.{fk}")
        for tk in (obody.get("decisive_tier") or {}):
            keys.add(f"outputs.{oname}.decisive_tier.{tk}")
    for k in (policy.get("modes") or {}):
        keys.add(f"modes.{k}")
    return keys


def seed_keys(seed_text: str) -> set[str]:
    """The checked keys the migration 027 projection seeds (first column of each VALUES row)."""
    return {m.group(1) for m in _SEED_RE.finditer(seed_text)}


def lint(policy_text: str, seed_text: str) -> list[str]:
    """Return FAIL strings (pure — used by tests with synthetic inputs)."""
    fails: list[str] = []
    if yaml is None:
        return fails
    try:
        policy = yaml.safe_load(policy_text) or {}
    except Exception as e:  # noqa: BLE001
        return [f"FAIL: routing_policy.yaml does not parse — {str(e).splitlines()[0]}"]
    file_keys = checked_keys_from_policy(policy)
    proj_keys = seed_keys(seed_text)
    for k in sorted(file_keys - proj_keys):
        fails.append(f"FAIL: routing-policy key '{k}' in routing_policy.yaml but NOT seeded (migration 027) — re-seed")
    for k in sorted(proj_keys - file_keys):
        fails.append(f"FAIL: routing-policy key '{k}' seeded (migration 027) but NOT in routing_policy.yaml — prune/restore")
    return fails


def main() -> int:
    if not POLICY.is_file() or not MIG027.is_file():
        print(f"FAIL: routing-policy source missing (policy={POLICY.is_file()}, mig027={MIG027.is_file()})")
        return 0
    fails = lint(POLICY.read_text(encoding="utf-8"), MIG027.read_text(encoding="utf-8"))
    for ln in fails:
        print(ln)
    if not fails:
        n = len(seed_keys(MIG027.read_text(encoding="utf-8")))
        print(f"OK: {n} routing-policy checked keys agree file<->projection (bidirectional set-equality).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
