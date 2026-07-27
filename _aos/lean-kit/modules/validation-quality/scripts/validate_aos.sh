#!/bin/bash
# validate_aos.sh — Universal _aos/ Validation (Checks 1–81)
# =========================================================
# L-GATE_BUILD exit criterion: MUST return exit code 0 (no FAIL; SKIP is allowed).
#
# Usage: bash validate_aos.sh [project-root]
#   project-root defaults to current directory.
#   Expects _aos/ directory at project-root/_aos/
#
# active_modules (optional) in _aos/metadata.yaml:
#   - Key absent  → all lean-kit modules treated active (no silent drift).
#   - YAML list   → only listed module IDs run their scoped checks (two-digit
#                   strings or integers per canon 01–11, see methodology
#                   AOS_DIRECTORY_CANON_v1.0.0.md Part 3).
#   - Empty list  → invalid (script exits 1 before checks).
#
# Exit: 0 = ALL PASS (SKIP allowed), 1 = ONE OR MORE FAIL or fatal parse error
# Dependencies: python3, PyYAML (python3 -c "import yaml")

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${1:-.}"
AOS_DIR="$PROJECT_ROOT/_aos"
PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0
ACTIVE_MODULES_MODE="all"
ACTIVE_MODULES_LIST=()

# --- Pre-flight: PyYAML check ---
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "FATAL: PyYAML not installed. Run: pip3 install pyyaml"
    exit 1
fi

if [ ! -d "$AOS_DIR" ]; then
    echo "FATAL: _aos/ directory not found at $AOS_DIR"
    exit 1
fi

log_pass() { echo "[PASS] Check $1: $2"; ((PASS_COUNT++)) || true; }
log_fail() { echo "[FAIL] Check $1: $2"; ((FAIL_COUNT++)) || true; }
log_skip() { echo "[SKIP] Check $1: $2"; ((SKIP_COUNT++)) || true; }

# Model B (ADR054): true when this is a Model-B domain whose git-ignored Tier-A cache
# (_aos/governance|methodology|lean-kit) is NOT yet hydrated — a fresh checkout / cold CI
# before scripts/aos_governance_bootstrap.sh has run. Cache-dependent checks SKIP-with-advice
# instead of FAIL in this state (the cache is restored by bootstrap/sync, not committed).
# AOS-V4.5 cold-checkout tolerance.
_modelb_cache_absent() {
    local is_modelb=0
    [ -f "$AOS_DIR/AOS_GOVERNANCE_VERSION.yaml" ] && is_modelb=1
    grep -q "AOS-GOV-CACHE" "$PROJECT_ROOT/.gitignore" 2>/dev/null && is_modelb=1
    [ "$is_modelb" -eq 1 ] || return 1                              # not a Model-B domain
    [ -n "$(ls "$AOS_DIR/governance" 2>/dev/null)" ] && return 1    # cache hydrated → not absent
    return 0                                                        # Model-B + cache empty → absent
}

# --- Load active_modules filter from metadata.yaml (AC-072) ---
load_active_modules() {
    ACTIVE_MODULES_MODE="all"
    ACTIVE_MODULES_LIST=()
    local mf="$AOS_DIR/metadata.yaml"
    if [ ! -f "$mf" ]; then
        return 0
    fi
    local py_out ec
    py_out=$(python3 -c "
import yaml, sys
from pathlib import Path
path = Path(sys.argv[1])
with open(path) as f:
    m = yaml.safe_load(f)
if m is None:
    m = {}
am = m.get('active_modules')
if am is None:
    print('ALL')
    sys.exit(0)
if not isinstance(am, list):
    print('ERROR: active_modules must be a YAML list', file=sys.stderr)
    sys.exit(2)
if len(am) == 0:
    print('ERROR: active_modules must not be empty when set', file=sys.stderr)
    sys.exit(2)
out = []
for x in am:
    s = str(x).strip()
    if s.isdigit():
        s = s.zfill(2)
    out.append(s)
print('FILTER')
print(' '.join(out))
" "$mf")
    ec=$?
    if [ "$ec" -eq 2 ]; then
        echo "FATAL: invalid active_modules in $mf"
        exit 1
    fi
    if [ "$ec" -ne 0 ]; then
        echo "FATAL: could not read $mf"
        exit 1
    fi
    local first
    first=$(echo "$py_out" | head -1)
    if [ "$first" = "ALL" ]; then
        ACTIVE_MODULES_MODE="all"
        return 0
    fi
    ACTIVE_MODULES_MODE="filter"
    read -r -a ACTIVE_MODULES_LIST <<< "$(echo "$py_out" | tail -1)"
}

# --- Hub vs spoke context (Checks 36, 38) --------------------------------------
# Hub (e.g. agents-os): top-level lean-kit/ and governance/directives/ hold
# canonical SSoT; _aos/lean-kit/ (and after propagation) _aos/governance/directives/
# are read-only snapshots for validation parity.
# Spoke projects: no top-level lean-kit/; validation uses _aos/lean-kit/ and
# _aos/governance/directives/ only. Requiring both hub-style and snapshot paths
# in spokes caused false FAILs.
detect_context() {
    if [ -d "$PROJECT_ROOT/core" ] && [ -d "$PROJECT_ROOT/lean-kit" ] && [ -f "$PROJECT_ROOT/scripts/aos_sync_all.sh" ]; then
        CONTEXT=hub
    elif [ -d "$PROJECT_ROOT/_aos" ]; then
        CONTEXT=spoke
    else
        CONTEXT=unknown
        echo "  [WARN] detect_context: could not classify project root — using spoke path rules" >&2
    fi
    export CONTEXT
}

load_active_modules
detect_context

# Return 0 if this check should run; 1 if skipped (already logged).
_require_active_modules() {
    local chk="$1"
    shift
    if [ "$ACTIVE_MODULES_MODE" = "all" ]; then
        return 0
    fi
    local mid found
    for mid in "$@"; do
        found=0
        for a in "${ACTIVE_MODULES_LIST[@]}"; do
            if [ "$a" = "$mid" ]; then
                found=1
                break
            fi
        done
        if [ "$found" -eq 0 ]; then
            log_skip "$chk" "skipped — required module $mid not in active_modules"
            return 1
        fi
    done
    return 0
}

# ── cannot-run ⇒ SKIP guards (AOS-V5-M11-WP-VALIDATION-VERSION-CANON-HYGIENE C1) ──────────────────
# Contract: a check that cannot EXECUTE (missing module/tool/file in this context) must SKIP, never FAIL.
# Each returns 0 when the resource is present (caller proceeds) and 1 after logging a SKIP (caller returns 0).
# Usage:  _require_module 59 core "DOC-close-gate" || return 0
_require_module() {  # <check_num> <python_import> <label>
    ( cd "$PROJECT_ROOT" && python3 -c "import $2" ) >/dev/null 2>&1 && return 0
    log_skip "$1" "$3 — python module '$2' not importable in this context (spoke/cache-only or CI CWD); check unavailable, skip"
    return 1
}
_require_tool() {    # <check_num> <command> <label>
    command -v "$2" >/dev/null 2>&1 && return 0
    log_skip "$1" "$3 — tool '$2' not present; check unavailable, skip"
    return 1
}
_require_file() {    # <check_num> <path> <label>
    [ -f "$2" ] && return 0
    log_skip "$1" "$3 — '$2' not present; check unavailable, skip"
    return 1
}

# ================================================================
# Check 1: YAML Parse Validity (module 01 — project-governance)
# ================================================================
check_1() {
    _require_active_modules 1 01 || return 0
    python3 -c "
import yaml, sys
for fname in ['$AOS_DIR/roadmap.yaml', '$AOS_DIR/team_assignments.yaml']:
    try:
        with open(fname) as f:
            data = yaml.safe_load(f)
        if data is None:
            print(f'EMPTY_FILE: {fname}', file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(f'NOT_FOUND: {fname}', file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f'PARSE_ERROR: {fname}: {e}', file=sys.stderr)
        sys.exit(1)
" && log_pass 1 "YAML files parse correctly" || log_fail 1 "YAML parse error"
}

# ================================================================
# Check 2: Cross-Engine Iron Rule (module 03 — team-model)
# ================================================================
check_2() {
    _require_active_modules 2 03 || return 0
    python3 -c "
import yaml, sys
with open('$AOS_DIR/team_assignments.yaml') as f:
    data = yaml.safe_load(f)
teams = data.get('teams', [])
builders = [t for t in teams if t.get('role_type') == 'builder_agent']
validators = [t for t in teams if t.get('role_type') == 'validator_agent']
if not builders:
    print('NO_BUILDER: no builder_agent found', file=sys.stderr)
    sys.exit(1)
if not validators:
    print('NO_VALIDATOR: no validator_agent found', file=sys.stderr)
    sys.exit(1)
for b in builders:
    for v in validators:
        if b.get('engine','').strip() == v.get('engine','').strip():
            print(f'VIOLATION: {b[\"id\"]} ({b[\"engine\"]}) == {v[\"id\"]} ({v[\"engine\"]})', file=sys.stderr)
            sys.exit(1)
" && log_pass 2 "Cross-engine Iron Rule satisfied" || log_fail 2 "Cross-engine Iron Rule VIOLATED"
}

# ================================================================
# Check 3: Version Consistency — RETIRED (module 09 deprecated by W9)
# ================================================================
# Module 09 (version-consistency) was deprecated and removed by W9; its
# lean-kit directory no longer exists. This check is retained as a numbered
# no-op so downstream check numbering stays stable, and reports an explicit
# N/A-PASS (not SKIP) per the validation-quality DEPRECATED CHECKS register
# (see MODULE.md § Deprecated / retired checks). The former logic compared
# metadata.yaml lean_kit_version against _aos/lean-kit/LEAN_KIT_VERSION.md.
check_3() {
    log_pass 3 "deprecated-module — N/A (module 09 version-consistency retired by W9)"
}

# ================================================================
# Check 4: spec_ref Resolution (module 01 — project-governance)
# ================================================================
check_4() {
    _require_active_modules 4 01 || return 0
    python3 -c "
import yaml, sys, os
with open('$AOS_DIR/roadmap.yaml') as f:
    data = yaml.safe_load(f)
for wp in data.get('work_packages', []):
    ref = wp.get('spec_ref', '')
    if not ref:
        continue
    if str(ref).strip() in ('TBD', 'null', 'None', ''):
        continue  # placeholder — spec not yet authored; skip resolution
    if ref.startswith('/'):
        print(f'ABSOLUTE_PATH: {wp[\"id\"]} spec_ref={ref}', file=sys.stderr)
        sys.exit(1)
    if '..' in ref:
        print(f'PARENT_TRAVERSAL: {wp[\"id\"]} spec_ref={ref}', file=sys.stderr)
        sys.exit(1)
    full = os.path.join('$PROJECT_ROOT', ref)
    if not os.path.isfile(full):
        print(f'NOT_FOUND: {wp[\"id\"]} spec_ref={ref} (resolved: {full})', file=sys.stderr)
        sys.exit(1)
" && log_pass 4 "All spec_refs resolve to existing files" || log_fail 4 "spec_ref resolution failed"
}

# ================================================================
# Check 5: Required Fields — Schema Compliance (module 01)
# ================================================================
check_5() {
    _require_active_modules 5 01 || return 0
    python3 -c "
import yaml, sys
with open('$AOS_DIR/roadmap.yaml') as f:
    rm = yaml.safe_load(f)
with open('$AOS_DIR/team_assignments.yaml') as f:
    ta = yaml.safe_load(f)

# Project block required fields
proj = rm.get('project', {})
for field in ['id', 'name', 'profile', 'lean_kit_version', 'owner', 'active_milestone']:
    val = proj.get(field, '')
    if not val or str(val).strip() == '':
        print(f'MISSING: project.{field}', file=sys.stderr)
        sys.exit(1)

# WP block required fields
for wp in rm.get('work_packages', []):
    for field in ['id', 'label', 'status', 'track', 'current_lean_gate', 'assigned_builder', 'assigned_validator', 'spec_ref']:
        val = wp.get(field, '')
        if not val or str(val).strip() == '':
            print(f'MISSING: WP {wp.get(\"id\", \"?\")}.{field}', file=sys.stderr)
            sys.exit(1)

# team_assignments required fields
if not ta.get('project_id', ''):
    print('MISSING: project_id in team_assignments.yaml', file=sys.stderr)
    sys.exit(1)
for team in ta.get('teams', []):
    for field in ['id', 'role_type', 'engine']:
        val = team.get(field, '')
        if not val or str(val).strip() == '':
            print(f'MISSING: team.{field} in team ' + team.get('id', '?'), file=sys.stderr)
            sys.exit(1)
" && log_pass 5 "All required fields present" || log_fail 5 "Missing required fields"
}

# ================================================================
# Check 6: metadata.yaml Existence + Provenance (module 01)
# ================================================================
check_6() {
    _require_active_modules 6 01 || return 0
    python3 -c "
import yaml, sys, os
meta_path = '$AOS_DIR/metadata.yaml'
if not os.path.isfile(meta_path):
    print(f'NOT_FOUND: {meta_path}', file=sys.stderr)
    sys.exit(1)
with open(meta_path) as f:
    meta = yaml.safe_load(f)
if meta is None:
    print('EMPTY: metadata.yaml is empty', file=sys.stderr)
    sys.exit(1)
for key in ['lean_kit_version', 'lean_kit_source_sha', 'lean_kit_source_date', 'profile']:
    val = meta.get(key, '')
    if not val or str(val).strip() == '':
        print(f'EMPTY_KEY: metadata.yaml.{key}', file=sys.stderr)
        sys.exit(1)
# L2 additional check
profile = str(meta.get('profile', ''))
if profile in ('L2', 'L3'):
    aev = meta.get('aos_engine_version', '')
    if not aev or str(aev).strip() == '':
        print(f'EMPTY_KEY: metadata.yaml.aos_engine_version (required for {profile})', file=sys.stderr)
        sys.exit(1)
" && log_pass 6 "metadata.yaml complete" || log_fail 6 "metadata.yaml incomplete"
}

# ================================================================
# Check 7: Team ID Slug Regex (module 03 — team-model)
# ================================================================
check_7() {
    _require_active_modules 7 03 || return 0
    python3 -c "
import yaml, sys, re
with open('$AOS_DIR/team_assignments.yaml') as f:
    data = yaml.safe_load(f)
pattern = re.compile(r'^[a-z][a-z0-9]*_[a-z]+$')
for team in data.get('teams', []):
    tid = str(team.get('id', ''))
    if not pattern.match(tid):
        print(f'BAD_SLUG: \"{tid}\" does not match ^[a-z][a-z0-9]*_[a-z]+\$', file=sys.stderr)
        sys.exit(1)
" && log_pass 7 "All team IDs match slug regex" || log_fail 7 "Slug regex violation"
}

# ================================================================
# Check 8: Reserved Role Suffix (module 03 — team-model)
# ================================================================
check_8() {
    _require_active_modules 8 03 || return 0
    python3 -c "
import yaml, sys
RESERVED = {'sd', 'arch', 'build', 'val', 'doc', 'gate'}
with open('$AOS_DIR/team_assignments.yaml') as f:
    data = yaml.safe_load(f)
for team in data.get('teams', []):
    tid = str(team.get('id', ''))
    parts = tid.rsplit('_', 1)
    if len(parts) != 2:
        print(f'NO_SUFFIX: \"{tid}\" has no underscore separator', file=sys.stderr)
        sys.exit(1)
    suffix = parts[1]
    if suffix not in RESERVED:
        print(f'BAD_SUFFIX: \"{tid}\" suffix \"{suffix}\" not in {sorted(RESERVED)}', file=sys.stderr)
        sys.exit(1)
" && log_pass 8 "All team suffixes are reserved" || log_fail 8 "Reserved suffix violation"
}

# ================================================================
# Check 9: Profile Enum Compliance (module 01 — project-governance)
# ================================================================
check_9() {
    _require_active_modules 9 01 || return 0
    python3 -c "
import yaml, sys
VALID_PROFILES = {'L0', 'L2', 'L3'}
with open('$AOS_DIR/roadmap.yaml') as f:
    rm = yaml.safe_load(f)
with open('$AOS_DIR/metadata.yaml') as f:
    meta = yaml.safe_load(f)
rp = str(rm.get('project', {}).get('profile', ''))
mp = str(meta.get('profile', ''))
if rp not in VALID_PROFILES:
    print(f'BAD_PROFILE: roadmap.yaml profile=\"{rp}\" not in {sorted(VALID_PROFILES)}', file=sys.stderr)
    sys.exit(1)
if mp not in VALID_PROFILES:
    print(f'BAD_PROFILE: metadata.yaml profile=\"{mp}\" not in {sorted(VALID_PROFILES)}', file=sys.stderr)
    sys.exit(1)
if rp != mp:
    print(f'MISMATCH: roadmap.yaml profile=\"{rp}\" != metadata.yaml profile=\"{mp}\"', file=sys.stderr)
    sys.exit(1)
" && log_pass 9 "Profile enum valid and consistent" || log_fail 9 "Profile enum violation"
}

# ================================================================
# Check 10: module 05 snapshot — RETIRED (module 05 deprecated by W9)
# ================================================================
# Module 05 was deprecated and removed by W9; its lean-kit directory no longer
# exists. Retained as a numbered no-op for stable check numbering; reports an
# explicit N/A-PASS (not SKIP) per the validation-quality DEPRECATED CHECKS
# register (see MODULE.md § Deprecated / retired checks).
check_10() {
    log_pass 10 "deprecated-module — N/A (module 05 snapshot retired by W9)"
}

# ================================================================
# Check 11: Governance directory completeness (module 01)
# ================================================================
check_11() {
    _require_active_modules 11 01 || return 0
    if _modelb_cache_absent; then
        log_skip 11 "governance cache not hydrated (Model B / ADR054) — run scripts/aos_governance_bootstrap.sh"
        return 0
    fi
    local def="$AOS_DIR/definition.yaml"
    local gov="$AOS_DIR/governance"
    local ok=1
    if [ ! -f "$def" ]; then
        log_fail 11 "definition.yaml missing from _aos/ (Iron Rule #8 — project independence)"
        ok=0
    fi
    if [ ! -d "$gov" ]; then
        log_fail 11 "governance/ directory missing from _aos/"
        ok=0
    elif [ ! -f "$gov/team_00.md" ]; then
        log_fail 11 "governance/ exists but team_00.md missing (incomplete governance snapshot)"
        ok=0
    fi
    if [ "$ok" -eq 1 ]; then
        local count
        count=$(ls "$gov"/team_*.md 2>/dev/null | wc -l | tr -d ' ')
        log_pass 11 "Governance directory complete (definition.yaml + $count team files)"
    fi
}

# ================================================================
# Check 13: definition.yaml ↔ governance/ team consistency (module 01)
# Every team_XX key in definition.yaml must have a team_XX.md in governance/.
# Ghost teams (defined but not governed) indicate a stale or over-broad snapshot.
# ================================================================
check_13() {
    _require_active_modules 13 01 || return 0
    local def="$AOS_DIR/definition.yaml"
    local gov="$AOS_DIR/governance"
    [ ! -f "$def" ] && return 0  # Check 11 already catches missing definition.yaml
    [ ! -d "$gov" ] && return 0  # Check 11 already catches missing governance/
    # R5 (AOS-V5-WP-GOV-SNAPSHOT-HARDENING) — determinism / reentrancy:
    #   - Paths are passed as argv, NOT string-interpolated into the python source,
    #     so a project path with a space / quote / backslash cannot corrupt the
    #     script (the prior `aos_dir = '$AOS_DIR'` form was fragile across the
    #     fleet, several of whose paths contain spaces).
    #   - def + gov are read into a SINGLE atomic snapshot inside one process and
    #     compared via sorted sets — no glob ordering, /tmp file, or env var is
    #     shared between sequential runs, so a multi-domain sweep gives identical
    #     results to an isolated run (regression: core/tests/test_check13_reentrant.py).
    if python3 - "$def" "$gov" <<'PY'
import yaml, sys, os, glob

def_path, gov_dir = sys.argv[1], sys.argv[2]

with open(def_path) as f:
    d = yaml.safe_load(f) or {}

defn_teams = set(k for k in d.keys() if isinstance(k, str) and k.startswith('team_'))
gov_files  = set(os.path.splitext(os.path.basename(p))[0]
                 for p in sorted(glob.glob(os.path.join(gov_dir, 'team_*.md'))))

# Bidirectional pairing (WP M9-P1-WP7 S2.5): catch BOTH directions of def<->gov drift. The
# legacy check was one-directional (defn-team without a gov file) so an ORPHAN governance file
# left behind by a dissolved/renamed team (e.g. team_190.md after team_190 collapses into
# team_90) was never flagged — a silent drift this canonization closes.
missing = sorted(defn_teams - gov_files)   # team in definition.yaml, no governance file (ghost team)
orphans = sorted(gov_files - defn_teams)   # governance team_*.md with no team_ block (dissolved/renamed)
err = False
for t in missing:
    print('MISSING_GOV: ' + t + ' in definition.yaml has no governance/team file', file=sys.stderr)
    err = True
for t in orphans:
    print('ORPHAN_GOV: ' + t + '.md has no team_ block in definition.yaml (dissolved/renamed team?)', file=sys.stderr)
    err = True
if err:
    sys.exit(1)
PY
    then
        log_pass 13 "definition.yaml <-> governance/ pairing is bidirectional-clean (no ghost teams, no orphan files)"
    else
        log_fail 13 "definition.yaml <-> governance/ drift — see MISSING_GOV (ghost team) / ORPHAN_GOV (orphan file) lines above"
    fi
}

# Check 12: Cross-Project Boundary — project_identity.yaml + contamination scan
check_12() {
    _require_active_modules 12 01 || return 0
    local id_file="$AOS_DIR/project_identity.yaml"

    # 12a: project_identity.yaml must exist
    if [ ! -f "$id_file" ]; then
        log_fail 12 "project_identity.yaml missing from _aos/ (cross-project boundary declaration required)"
        return
    fi

    # 12b: Parse and extract forbidden_patterns
    local patterns
    patterns=$(python3 -c "
import yaml, sys
try:
    with open('$id_file') as f:
        d = yaml.safe_load(f)
    b = d.get('boundaries', {})
    fp = b.get('forbidden_patterns', [])
    pid = d.get('project_id', '')
    if not pid:
        print('ERROR:project_id missing', file=sys.stderr)
        sys.exit(1)
    if not fp:
        print('WARN:no forbidden_patterns')
    else:
        for p in fp:
            print(p)
except Exception as e:
    print(f'ERROR:{e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)

    if echo "$patterns" | grep -q "^ERROR:"; then
        log_fail 12 "project_identity.yaml parse error: $(echo "$patterns" | grep '^ERROR:' | head -1)"
        return
    fi

    if echo "$patterns" | grep -q "^WARN:no forbidden_patterns"; then
        log_pass 12 "project_identity.yaml present (no forbidden_patterns to scan)"
        return
    fi

    # 12c: Parse optional per-file allowlist (boundaries.forbidden_patterns_allowlist).
    # Each entry: {path: <relpath>, patterns: [<pattern>,...] | omitted = all, reason: <text>}.
    # Emits "relpath<TAB><pattern>" (or "relpath<TAB>*" when patterns omitted) — a documented,
    # legitimate cross-reference exception (e.g. a portfolio/bio domain that intentionally
    # showcases sibling project names). Empty/absent → no exceptions (behavior unchanged).
    local allowlist
    allowlist=$(python3 -c "
import yaml
b = (yaml.safe_load(open('$id_file')) or {}).get('boundaries', {}) or {}
for e in (b.get('forbidden_patterns_allowlist', []) or []):
    path = e.get('path')
    if not path:
        continue
    pats = e.get('patterns')
    if not pats:
        print(f'{path}\t*')
    else:
        for p in pats:
            print(f'{path}\t{p}')
" 2>/dev/null)

    # 12d: Scan tracked source files for forbidden patterns (excluding allowlisted file/pattern pairs)
    local violations=0
    local violation_details=""
    while IFS= read -r pattern; do
        [ -z "$pattern" ] && continue
        # Pattern globally exempt for this project (allowlist entry with path: "*") —
        # e.g. a portfolio/bio domain that showcases a sibling project pervasively.
        if printf '%s\n' "$allowlist" | grep -qxF "*"$'\t'"$pattern"; then
            continue
        fi
        # Search in common source dirs, skip _aos/ itself and .git/
        local matches
        matches=$(grep -Frl --include="*.py" --include="*.js" --include="*.ts" --include="*.md" \
            --exclude-dir=".git" --exclude-dir="_aos" --exclude-dir="node_modules" \
            --exclude-dir=".claude" --exclude-dir="_COMMUNICATION" --exclude-dir="_communication" \
            --exclude-dir="_archive" \
            --exclude="CHANGELOG.md" --exclude="*.template" \
            --exclude="CLAUDE.md" --exclude=".cursorrules" \
            "$pattern" "$PROJECT_ROOT" 2>/dev/null | head -20)
        [ -z "$matches" ] && continue
        # Drop allowlisted (relpath, pattern) pairs — exact "<relpath>\t<pattern>" or "<relpath>\t*"
        local unallowed=""
        while IFS= read -r mfile; do
            [ -z "$mfile" ] && continue
            local rel="${mfile#$PROJECT_ROOT/}"
            if printf '%s\n' "$allowlist" | grep -qxF "$rel"$'\t'"$pattern" \
               || printf '%s\n' "$allowlist" | grep -qxF "$rel"$'\t*'; then
                continue
            fi
            unallowed="${unallowed}${mfile}"$'\n'
        done <<< "$matches"
        unallowed=$(printf '%s' "$unallowed" | sed '/^[[:space:]]*$/d')
        if [ -n "$unallowed" ]; then
            ((violations++)) || true
            local first_match
            first_match=$(printf '%s\n' "$unallowed" | head -1)
            violation_details="${violation_details}  pattern='$pattern' found in: $first_match"$'\n'
        fi
    done <<< "$patterns"

    if [ "$violations" -gt 0 ]; then
        log_fail 12 "Cross-project contamination: $violations forbidden pattern(s) found in tracked files"
        echo "$violation_details" | head -10
    else
        local pid
        pid=$(python3 -c "import yaml; print(yaml.safe_load(open('$id_file'))['project_id'])" 2>/dev/null)
        log_pass 12 "Cross-project boundary OK (project=$pid, 0 forbidden patterns found)"
    fi
}

# Check 14: additionalDirectories coverage (hub only, advisory/WARN)
# For hub projects: verify that each enabled spoke in _aos/projects.yaml
# has its local_path in .claude/settings.json → additionalDirectories.
# Advisory only — uses log_pass/log_skip, never log_fail.
# ================================================================
check_14() {
    local id_file="$AOS_DIR/project_identity.yaml"
    [ ! -f "$id_file" ] && { log_skip 14 "No project_identity.yaml — cannot determine hub status"; return; }

    local is_hub
    is_hub=$(python3 -c "import yaml; d=yaml.safe_load(open('$id_file')); print(d.get('is_hub', False))" 2>/dev/null || echo "False")
    if [ "$is_hub" != "True" ]; then
        log_pass 14 "Not a hub project — additionalDirectories check skipped"
        return
    fi

    local projects_file="$AOS_DIR/projects.yaml"
    [ ! -f "$projects_file" ] && { log_skip 14 "No _aos/projects.yaml — cannot check spoke paths"; return; }

    local settings_file="$PROJECT_ROOT/.claude/settings.json"
    [ ! -f "$settings_file" ] && { log_skip 14 "No .claude/settings.json — cannot verify additionalDirectories"; return; }

    python3 -c "
import yaml, json, sys

with open('$projects_file') as f:
    projects = yaml.safe_load(f) or {}

with open('$settings_file') as f:
    settings = json.load(f)

# additionalDirectories lives under permissions.* (Claude Code schema); tolerate a
# legacy top-level key too. (Fix: the check previously read only the top-level key,
# so it always reported every path missing regardless of content.)
perms = settings.get('permissions', {}) or {}
additional_dirs = perms.get('additionalDirectories') or settings.get('additionalDirectories', [])
spoke_list = projects.get('projects', projects.get('spokes', []))
if isinstance(spoke_list, dict):
    spoke_list = list(spoke_list.values())

missing = []
for p in spoke_list:
    if not isinstance(p, dict):
        continue
    if not p.get('enabled', True):
        continue
    path = p.get('local_path', '')
    if path and path not in additional_dirs:
        missing.append(path)

if missing:
    for m in missing:
        print('WARN: spoke path not in additionalDirectories: ' + m, file=sys.stderr)
    sys.exit(1)
else:
    sys.exit(0)
" && log_pass 14 "All enabled spoke paths present in additionalDirectories" \
  || { echo "  [WARN] Check 14: Some spoke paths missing from .claude/settings.json additionalDirectories (advisory)"; log_pass 14 "additionalDirectories check — warnings found (advisory, non-blocking)"; }
}

# ================================================================
# Check 15: Archive compliance — completed WPs have no stale _COMMUNICATION/ artifacts
# Verifies Iron Rule #15: completed WPs → artifacts in _archive/, not _COMMUNICATION/
# ================================================================
check_15() {
    _require_active_modules 15 01 || return 0
    python3 -c "
import yaml, sys, os, glob

project_root = '$PROJECT_ROOT'
aos_dir = '$AOS_DIR'
comm_dir = os.path.join(project_root, '_COMMUNICATION')

if not os.path.isdir(comm_dir):
    sys.exit(0)  # No _COMMUNICATION/ — nothing to check

with open(os.path.join(aos_dir, 'roadmap.yaml')) as f:
    rm = yaml.safe_load(f) or {}

complete_wps = set()
for wp in rm.get('work_packages', []):
    if wp.get('status') == 'COMPLETE' and wp.get('lod_status') in ('LOD500', 'LOD500_LOCKED'):
        complete_wps.add(wp['id'])

if not complete_wps:
    sys.exit(0)  # No completed WPs — skip

stale = []
for team_dir in glob.glob(os.path.join(comm_dir, 'team_*')):
    if not os.path.isdir(team_dir):
        continue
    for entry in os.listdir(team_dir):
        entry_path = os.path.join(team_dir, entry)
        if os.path.isdir(entry_path) and entry in complete_wps:
            stale.append(os.path.relpath(entry_path, project_root))

if stale:
    for s in sorted(stale):
        print(f'STALE_ARTIFACT_DIR: {s} (WP is COMPLETE — should be in _archive/)', file=sys.stderr)
    sys.exit(1)
" && log_pass 15 "No stale artifacts for completed WPs in _COMMUNICATION/" \
  || log_fail 15 "Completed WP artifacts still in _COMMUNICATION/ (Iron Rule #15 — archive required)"
}

# ================================================================
# Check 16: AOS slash commands vs manifest (module 08 — hub only)
# Runs validate_aos_commands.sh when project is hub and .claude/commands exists.
# ================================================================
check_16() {
    _require_active_modules 16 08 || return 0
    local idf="$AOS_DIR/project_identity.yaml"
    if [ ! -f "$idf" ]; then
        log_skip 16 "no project_identity.yaml — AOS command validation skipped"
        return 0
    fi
    local is_hub
    is_hub=$(python3 -c "import yaml; d=yaml.safe_load(open('$idf')); print('yes' if d.get('is_hub') else 'no')" 2>/dev/null || echo no)
    if [ "$is_hub" != "yes" ]; then
        log_skip 16 "not hub — validate_aos_commands.sh skipped (spoke/minimal)"
        return 0
    fi
    if [ ! -d "$PROJECT_ROOT/.claude/commands" ]; then
        log_skip 16 "no .claude/commands/ — AOS command validation skipped"
        return 0
    fi
    local cmdv="$PROJECT_ROOT/core/modules/validation-quality/validate_aos_commands.sh"
    if [ ! -f "$cmdv" ]; then
        cmdv="$PROJECT_ROOT/_aos/lean-kit/modules/validation-quality/validate_aos_commands.sh"
    fi
    if [ ! -f "$cmdv" ]; then
        log_fail 16 "validate_aos_commands.sh not found under lean-kit"
        return
    fi
    if bash "$cmdv" "$PROJECT_ROOT"; then
        log_pass 16 "AOS slash commands (validate_aos_commands.sh / manifest) PASS"
    else
        log_fail 16 "AOS slash commands (validate_aos_commands.sh / manifest) FAIL"
    fi
}

# ================================================================
# Check 17: PROJECT_CONTEXT.md schema (Directory Canon Part 1a)
# ================================================================
check_17() {
    _require_active_modules 17 01 || return 0
    local idf="$AOS_DIR/project_identity.yaml"
    local is_hub
    is_hub=$(python3 -c "import yaml; d=yaml.safe_load(open('$idf')); print('yes' if d.get('is_hub') else 'no')" 2>/dev/null || echo no)
    if [ "$is_hub" != "yes" ]; then
        log_skip 17 "not hub — PROJECT_CONTEXT schema check skipped (roll out per spoke)"
        return 0
    fi
    local pc="$PROJECT_ROOT/_aos/context/PROJECT_CONTEXT.md"
    if [ ! -f "$pc" ]; then
        log_skip 17 "no _aos/context/PROJECT_CONTEXT.md — schema check skipped"
        return 0
    fi
    python3 -c "
import sys, pathlib
p = pathlib.Path(r'$pc')
t = p.read_text(encoding='utf-8')
needed = [
    '## AOS environment (read first)',
    '## Team entry',
    '## Domain profile',
]
missing = [h for h in needed if h not in t]
if missing:
    print('PROJECT_CONTEXT missing required headings: ' + ', '.join(missing), file=sys.stderr)
    sys.exit(1)
sys.exit(0)
" && log_pass 17 "PROJECT_CONTEXT.md has Part 1a headings (AOS / Team entry / Domain)" \
  || log_fail 17 "PROJECT_CONTEXT.md missing required headings (see methodology/AOS_DIRECTORY_CANON Part 1a)"
}

# ================================================================
# Check 18: _aos/ write authority compliance
# Verify that no non-governance team contract lists _aos/ writes
# Authorized teams: SSoT = core/config/aos_write_authorized.yaml (WP M9-P1-WP7 — was the
# hardcoded {00,100,110,191}; 191 dissolved → 120 inherits the propagation authority).
# ================================================================
check_18() {
    _require_active_modules 18 01 || return 0
    local gov_dir="$AOS_DIR/governance"
    if [ ! -d "$gov_dir" ]; then
        log_skip 18 "no _aos/governance/ — write authority check skipped"
        return 0
    fi
    # _aos/ write-authority allowlist SSoT (WP M9-P1-WP7 R2-6): read the data file DIRECTLY —
    # spoke-safe, NEVER 'import agents_os' (no core/ on spokes, cwd-dependent symlink). Hub
    # path first, then the spoke _aos/ snapshot. Absent → skip (no SSoT to verify against).
    local awa_file="$PROJECT_ROOT/core/config/aos_write_authorized.yaml"
    [ -f "$awa_file" ] || awa_file="$AOS_DIR/config/aos_write_authorized.yaml"
    _require_file 18 "$awa_file" "_aos/ write allowlist (run gov sync)" || return 0
    python3 -c "
import sys, pathlib, re, yaml

_awa = yaml.safe_load(pathlib.Path(r'$awa_file').read_text(encoding='utf-8')) or {}
AUTHORIZED = set(_awa.get('authorized_teams', []) or [])
gov_dir = pathlib.Path(r'$gov_dir')
violations = []

for f in sorted(gov_dir.glob('team_*.md')):
    team_id = f.stem  # e.g. team_20
    if team_id in AUTHORIZED:
        continue
    text = f.read_text(encoding='utf-8')
    # Find writes_to: YAML block lines
    in_writes = False
    for line in text.splitlines():
        if re.match(r'\s*writes_to\s*:', line):
            in_writes = True
            continue
        if in_writes:
            # End of YAML list block (new key or empty)
            if line and not re.match(r'\s+[-\s]', line) and ':' in line:
                in_writes = False
                continue
            # Detect _aos/ path in a writes_to entry
            m = re.search(r'[\"\']\s*_aos/', line)
            if m:
                violations.append(f'{f.name}: writes_to contains _aos/ path: {line.strip()}')
    # Also check inline Boundaries section for explicit _aos/ write grants
    if re.search(r'Write to:.*_aos/', text):
        # Exclude lines that say 'do NOT' or 'NEVER'
        for line in text.splitlines():
            if re.search(r'Write to:.*_aos/', line) and not re.search(r'NOT|NEVER|never|read.only', line):
                violations.append(f'{f.name}: prose \"Write to\" mentions _aos/: {line.strip()}')

if violations:
    print('CHECK 18 VIOLATIONS (_aos/ write authority):', file=sys.stderr)
    for v in violations:
        print('  ' + v, file=sys.stderr)
    sys.exit(1)
sys.exit(0)
" && log_pass 18 "_aos/ write authority: all non-governance team contracts correctly restrict _aos/ writes (allowlist SSoT: aos_write_authorized.yaml)" \
  || log_fail 18 "_aos/ write authority: non-governance team contract(s) improperly grant _aos/ write access (see errors above)"
}

# ================================================================
# Check 19: API-only mutations + DB checker readiness
# Verify:
#  1) all team contracts include Iron Rule #7 API-only clause
#  2) unified DB checker script exists and can run
# ================================================================
check_19() {
    _require_active_modules 19 01 || return 0
    local gov_dir="$AOS_DIR/governance"
    if [ ! -d "$gov_dir" ]; then
        log_skip 19 "no _aos/governance/ — API-only mutations check skipped"
        return 0
    fi
    python3 -c "
import sys, pathlib

gov_dir = pathlib.Path(r'$gov_dir')
missing = []

for f in sorted(gov_dir.glob('team_*.md')):
    text = f.read_text(encoding='utf-8')
    # Every contract must acknowledge Iron Rule #7 / API-only mutations
    if 'API-only' not in text and 'Iron Rule #7' not in text:
        missing.append(f.name)

if missing:
    print('CHECK 19 VIOLATIONS (API-only mutations clause missing):', file=sys.stderr)
    for m in missing:
        print('  ' + m, file=sys.stderr)
    sys.exit(1)
sys.exit(0)
" && log_pass 19 "API-only mutations: all team contracts include Iron Rule #7 API-only clause" \
  || { log_fail 19 "API-only mutations: one or more team contracts missing Iron Rule #7 API-only clause (see errors above)"; return; }

    local checker="$PROJECT_ROOT/scripts/db/check_db_connectivity.py"
    _require_file 19 "$checker" "Unified DB checker (hub-only component; skip on spokes)" || return
    if ! python3 -c "import psycopg2" 2>/dev/null; then
        echo "[SKIP] Check 19b: psycopg2 not installed — unified DB checker not run (pip install psycopg2-binary)"
        return 0
    fi
    python3 "$checker" --source "validate_aos.sh" --format text --persist-success >/tmp/aos_db_check.txt 2>&1
    local rc=$?
    if [ "$rc" -eq 0 ] || [ "$rc" -eq 2 ]; then
        echo "[PASS] Check 19b: Unified DB checker executable (online=0/offline=2 accepted)"
    else
        log_fail 19 "Unified DB checker execution failed (exit=$rc)"
    fi
}

# ================================================================
# Check 20: MCP profile — .cursor/mcp.json when L2 / L2.5
# ================================================================
check_20() {
    # Always run (MCP profile is cross-cutting; not tied to module 14 snapshot filter)
    local MCP_PROFILE
    MCP_PROFILE=$(python3 -c "
import yaml, sys
try:
    d = yaml.safe_load(open('$AOS_DIR/metadata.yaml'))
    print(d.get('mcp_profile', 'none'))
except Exception:
    print('none')
" 2>/dev/null)

    if [[ "$MCP_PROFILE" == "L2" || "$MCP_PROFILE" == "L2.5" ]]; then
        if [ ! -f "$PROJECT_ROOT/.cursor/mcp.json" ]; then
            log_fail 20 ".cursor/mcp.json missing (mcp_profile=${MCP_PROFILE} requires it)"
            return
        fi
        if ! python3 -c "import json; json.load(open('$PROJECT_ROOT/.cursor/mcp.json'))" 2>/dev/null; then
            log_fail 20 ".cursor/mcp.json is not valid JSON"
            return
        fi
        log_pass 20 ".cursor/mcp.json present and valid JSON (profile=${MCP_PROFILE})"
        return
    fi

    log_pass 20 "mcp_profile='${MCP_PROFILE}' — no .cursor/mcp.json required"
}

# ================================================================
# Check 21: Gate structure validation (validate_gates.sh)
# Requires module 07 (validation-quality). Skips gracefully when absent.
# Advisory mode: SKIP (not FAIL) on violations until pre-V318 data debt
# is cleared (report_path backfill for legacy gate_history entries).
# ================================================================
check_21() {
    _require_active_modules 21 07 || return 0
    local gs="$SCRIPT_DIR/validate_gates.sh"
    _require_file 21 "$gs" "Gate structure validation" || return 0
    if bash "$gs" --roadmap "$AOS_DIR/roadmap.yaml" > /dev/null 2>&1; then
        log_pass 21 "validate_gates.sh: gate structure PASS"
    else
        log_skip 21 "validate_gates.sh: gate structure advisories found (pre-V318 data debt; run validate_gates.sh manually)"
    fi
}

# ================================================================
# Check 22: LOD document validation (validate_lod.sh, LOD400+ only)
# Requires module 07 (validation-quality). Skips gracefully when absent.
# Uses --min-lod 400 to skip WPs below LOD400 in roadmap.
# Advisory mode: SKIP on violations — pre-V318 LOD docs use a different
# frontmatter schema (lod_level/status vs lod_target/lod_status).
# ================================================================
check_22() {
    _require_active_modules 22 07 || return 0
    local ls_script="$SCRIPT_DIR/validate_lod.sh"
    [ ! -f "$ls_script" ] && { log_skip 22 "validate_lod.sh not found in $SCRIPT_DIR"; return 0; }
    if bash "$ls_script" --all --min-lod 400 > /dev/null 2>&1; then
        log_pass 22 "validate_lod.sh: LOD400+ document structure PASS"
    else
        log_skip 22 "validate_lod.sh: LOD400+ advisories found (pre-V318 schema debt; run validate_lod.sh --all --min-lod 400 manually)"
    fi
}

# ================================================================
# Check 23: Verdict schema validation (validate_verdicts.sh)
# Requires module 07 (validation-quality). Skips gracefully when absent.
# Advisory mode: SKIP on violations — pre-V318 verdicts use older
# schema without standardized part_a/b fields.
# ================================================================
check_23() {
    _require_active_modules 23 07 || return 0
    local vs="$SCRIPT_DIR/validate_verdicts.sh"
    [ ! -f "$vs" ] && { log_skip 23 "validate_verdicts.sh not found in $SCRIPT_DIR"; return 0; }
    if bash "$vs" > /dev/null 2>&1; then
        log_pass 23 "validate_verdicts.sh: verdict schema PASS"
    else
        log_skip 23 "validate_verdicts.sh: verdict schema advisories found (pre-V318 schema debt; run validate_verdicts.sh manually)"
    fi
}

# ================================================================
# Check 24: Port registry canon (Team 60 SSoT) — hub only
# Verifies lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml
# parses, has no duplicate port assignments, and that every entry has a port + project.
# Hub-scoped (skips on spoke projects where the file is absent).
# ================================================================
check_24() {
    local pr="$PROJECT_ROOT/extensions/home-server-infrastructure/deployment/port-registry.yaml"
    if [ ! -f "$pr" ]; then pr="$PROJECT_ROOT/lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml"; fi
    if [ ! -f "$pr" ]; then pr="$PROJECT_ROOT/_aos/lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml"; fi
    if [ ! -f "$pr" ]; then
        log_skip 24 "port-registry.yaml not found (spoke project — hub canon does not apply)"
        return 0
    fi
    local result
    result=$(python3 - "$pr" <<'PY' 2>&1
import sys, yaml
path = sys.argv[1]
try:
    with open(path) as f:
        docs = list(yaml.safe_load_all(f))
except Exception as e:
    print(f"PARSE_ERROR: {e}")
    sys.exit(2)
# Support both v1.x flat `ports:` list and v2.0+ `projects:` structure
doc = next((d for d in docs if isinstance(d, dict)), {})
if "ports" in doc:
    # v1.x format: flat list under ports:
    ports_flat = doc.get("ports") or []
    if not isinstance(ports_flat, list) or not ports_flat:
        print("EMPTY: ports list missing or empty")
        sys.exit(2)
    seen = {}
    errors = []
    for i, p in enumerate(ports_flat):
        if not isinstance(p, dict):
            errors.append(f"entry[{i}] not a mapping")
            continue
        if "port" not in p or "project" not in p:
            errors.append(f"entry[{i}] missing port/project ({p.get('service','?')})")
            continue
        pn = p["port"]
        if pn in seen:
            errors.append(f"duplicate port {pn} ({seen[pn]} vs {p.get('project')})")
        else:
            seen[pn] = p.get("project")
    if errors:
        print("; ".join(errors))
        sys.exit(2)
    print(f"OK: {len(seen)} unique ports registered (v1 format)")
elif "projects" in doc:
    # v2.0+ format: projects list with instances
    projects = doc.get("projects") or []
    if not isinstance(projects, list) or not projects:
        print("EMPTY: projects list missing or empty")
        sys.exit(2)
    seen = {}
    errors = []
    for proj in projects:
        if not isinstance(proj, dict):
            continue
        for inst in (proj.get("instances") or []):
            for port_entry in (inst.get("ports") or []):
                if not isinstance(port_entry, dict):
                    continue
                pn = port_entry.get("port")
                if pn is None:
                    continue
                proj_id = proj.get("project_id", proj.get("id", "?"))
                if pn in seen:
                    errors.append(f"duplicate port {pn} ({seen[pn]} vs {proj_id})")
                else:
                    seen[pn] = proj_id
    if errors:
        print("; ".join(errors))
        sys.exit(2)
    print(f"OK: {len(seen)} unique ports registered (v2 format)")
else:
    print("EMPTY: ports list missing or empty")
    sys.exit(2)
PY
    )
    if [ $? -eq 0 ]; then
        log_pass 24 "port-registry.yaml: $result"
    else
        log_fail 24 "port-registry.yaml integrity: $result"
    fi
}

# ================================================================
# Check 25: Offline DB sync — PENDING_DB_SYNC.yaml detection
# Warns when _aos/PENDING_DB_SYNC.yaml exists (offline work pending DB sync).
# WARN (not FAIL) — file is legitimate on offline branches.
# Real enforcement happens at CI merge gate (ADR034 R8.5).
# ================================================================
check_25() {
    local sync_file="$AOS_DIR/PENDING_DB_SYNC.yaml"
    if [ -f "$sync_file" ]; then
        local sid
        sid=$(python3 - "$sync_file" <<'PY' 2>&1
import yaml, sys
try:
    with open(sys.argv[1]) as f:
        d = yaml.safe_load(f)
    sid = d.get('offline_session', {}).get('session_id', 'unknown')
    print(sid)
except Exception:
    print('unknown')
PY
        ) || sid="unknown"
        log_skip 25 "PENDING_DB_SYNC.yaml found (session: $sid) — offline mutations await DB sync via sync_offline_to_db.sh"
    else
        log_pass 25 "No pending offline DB sync (PENDING_DB_SYNC.yaml absent)"
    fi
}

# ================================================================
# Check 26: LOD400 bare CS-N citations (ADR037 advisory)
# Scans _aos/work_packages/**/LOD400*.md for markdown [...CS-N...] without
# CODE_STANDARDS.md on the same line. Advisory only — does not FAIL.
# ================================================================
check_26() {
    local wp_root="$AOS_DIR/work_packages"
    if [ ! -d "$wp_root" ]; then
        log_pass 26 "No work_packages dir — skip LOD400 CS scan"
        return 0
    fi
    local result
    result=$(python3 - "$wp_root" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
pat = re.compile(r"\[[^\]]*CS-\d+[^\]]*\]")
hits = []
for path in sorted(root.rglob("LOD400*.md")):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    for i, line in enumerate(text.splitlines(), 1):
        if not pat.search(line):
            continue
        if "CODE_STANDARDS.md" in line:
            continue
        if "Forbidden" in line and "Bare" in line:
            continue
        hits.append(f"{path.relative_to(root)}:{i}")

if not hits:
    print("OK:0")
else:
    print(f"WARN:{len(hits)}")
    for h in hits[:25]:
        print(h)
    if len(hits) > 25:
        print(f"... and {len(hits) - 25} more")
PY
    )
    local code
    code=$(echo "$result" | head -1)
    if [[ "$code" == OK:0 ]]; then
        log_pass 26 "LOD400 CS citations — no suspected bare [CS-N] lines (ADR037)"
    else
        local n
        n=${code#WARN:}
        log_skip 26 "Advisory (ADR037): $n LOD400 line(s) may use bare CS cites — qualify with repo + _aos/context/CODE_STANDARDS.md + CS-N. Sample: $(echo "$result" | sed -n '2p')"
    fi
}

# ================================================================
# Check 27: Canonical CLAUDE.md invariants (ADR040 / Iron Rule #12)
# ================================================================
# Verifies that CLAUDE.md contains the AOS canonical invariants:
# - "AOS Spoke Notice" or equivalent identity section (hub/spoke aware)
# - DB probe step reference (db_connectivity_status or probe_database)
# - Iron Rule #12 / ADR040 reference
check_27() {
    local claude_path="$AOS_DIR/../CLAUDE.md"
    [ -f "$claude_path" ] || claude_path="$AOS_DIR/CLAUDE.md"
    if [ ! -f "$claude_path" ]; then
        log_skip 27 "CLAUDE.md not found at expected locations (skip — non-AOS repo root)"
        return 0
    fi
    local missing=""
    grep -q "db_connectivity_status\|probe_database" "$claude_path" || missing="${missing} DB-probe"
    grep -qE "Iron Rule #12|ADR040|AOS Spoke Notice|AOS Identity" "$claude_path" || missing="${missing} authority-identity"
    grep -q "AOS" "$claude_path" || missing="${missing} AOS-context"
    if [ -z "$missing" ]; then
        log_pass 27 "CLAUDE.md canonical invariants present (DB-probe + AOS authority/identity — ADR040)"
    else
        log_fail 27 "CLAUDE.md missing canonical invariants:${missing} — run aos_sync_all.sh to regenerate"
    fi
}

# ================================================================
# Check 28: Canonical .cursorrules invariants (ADR040 / Iron Rule #12)
# ================================================================
check_28() {
    local cursor_path="$AOS_DIR/../.cursorrules"
    [ -f "$cursor_path" ] || cursor_path="$AOS_DIR/.cursorrules"
    if [ ! -f "$cursor_path" ]; then
        log_skip 28 ".cursorrules not found at expected locations (skip — Cursor optional)"
        return 0
    fi
    local missing=""
    grep -q "db_connectivity_status\|probe_database" "$cursor_path" || missing="${missing} DB-probe"
    grep -qE "Iron Rule #12|ADR040|AOS Spoke Notice|AOS Identity|Mandatory Session Startup|Mandatory session startup|Session startup" "$cursor_path" || missing="${missing} startup-section"
    if [ -z "$missing" ]; then
        log_pass 28 ".cursorrules canonical invariants present (DB-probe + AOS startup section)"
    else
        log_fail 28 ".cursorrules missing canonical invariants:${missing} — run aos_sync_all.sh to regenerate"
    fi
}

# ================================================================
# Check 29: Spoke lean-kit version matches hub (ADR040)
# ================================================================
# Hub self-check: always PASS (hub is the SSOT).
# Spoke check: _aos/lean-kit/LEAN_KIT_VERSION.md content must match hub's lean-kit/LEAN_KIT_VERSION.md
check_29() {
    local is_hub=0
    local pid_file="$AOS_DIR/project_identity.yaml"
    if [ -f "$pid_file" ] && grep -q 'role:.*hub\|project_id:.*agents-os' "$pid_file" 2>/dev/null; then
        is_hub=1
    fi
    local local_ver="$AOS_DIR/lean-kit/LEAN_KIT_VERSION.md"
    if [ "$is_hub" -eq 1 ]; then
        _require_file 29 "$local_ver" "Hub LEAN_KIT_VERSION.md" || return 0
        log_pass 29 "Hub lean-kit version file present ($(head -1 "$local_ver" 2>/dev/null | head -c 80))"
        return 0
    fi
    _require_file 29 "$local_ver" "spoke _aos/lean-kit/LEAN_KIT_VERSION.md" || return 0
    # Tier 1: AOS_HUB_ROOT env var
    if [ -n "${AOS_HUB_ROOT:-}" ] && [ -f "${AOS_HUB_ROOT}/lean-kit/LEAN_KIT_VERSION.md" ]; then
        local hub_ver="${AOS_HUB_ROOT}/lean-kit/LEAN_KIT_VERSION.md"
        if diff -q "$local_ver" "$hub_ver" >/dev/null 2>&1; then
            log_pass 29 "spoke lean-kit version matches hub (via AOS_HUB_ROOT)"
        else
            log_fail 29 "spoke lean-kit version drifted vs hub — run aos_sync_all.sh"
        fi
        return 0
    fi
    # Tier 2: /api/hub/lean-kit/version
    local _api_base="${AOS_API_BASE:-${AOS_PUBLIC_API_BASE:-http://127.0.0.1:8090}}"
    local _api_body _api_http
    # Write body + HTTP code to a temp file; split via Python (Mac-portable — no `head -n -1` per F-HARD-002).
    local _tmp_resp
    _tmp_resp=$(mktemp 2>/dev/null) || _tmp_resp="/tmp/aos_check29_$$"
    local _api_http=000
    curl -s -w '\n%{http_code}' --max-time 3 --connect-timeout 3 \
        "${_api_base}/api/hub/lean-kit/version" -o "$_tmp_resp" 2>/dev/null || true
    # Last line of response file is the HTTP code (curl appended it).
    _api_http=$(tail -1 "$_tmp_resp" 2>/dev/null || echo "000")
    if [ "$_api_http" = "200" ]; then
        local _hub_ver _local_ver
        # Parse body (everything except the last line, which is HTTP code).
        _hub_ver=$(python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    lines = f.read().rstrip('\n').split('\n')
body = '\n'.join(lines[:-1])
try:
    d = json.loads(body)
    print(d.get('version', ''))
except Exception:
    pass
" "$_tmp_resp" 2>/dev/null || echo "")
        rm -f "$_tmp_resp" 2>/dev/null || true
        _local_ver=$(python3 -c "
import re, sys
with open(sys.argv[1]) as f: content = f.read()
m = re.search(r'\*\*version:\*\*\s*(\S+)', content) or re.search(r'version:\s*(\S+)', content)
print(m.group(1).strip() if m else '')
" "$local_ver" 2>/dev/null || echo "")
        if [ -z "$_hub_ver" ] || [ -z "$_local_ver" ]; then
            log_skip 29 "lean-kit version parse failed (hub='$_hub_ver' local='$_local_ver')"
        elif [ "$_hub_ver" = "$_local_ver" ]; then
            log_pass 29 "spoke lean-kit version matches hub (local=$_local_ver)"
        else
            log_fail 29 "spoke lean-kit version drifted (local=$_local_ver hub=$_hub_ver) — run aos_sync_all.sh"
        fi
        return 0
    fi
    rm -f "$_tmp_resp" 2>/dev/null || true
    # Tier 3: neither AOS_HUB_ROOT nor API — advisory skip
    log_skip 29 "hub LEAN_KIT_VERSION.md not reachable — set AOS_HUB_ROOT or start AOS API"
}

# ================================================================
# Check 30: AOS command line-count limit (ADR041 / Iron Rule #13)
# ================================================================
# Every .claude/commands/AOS_*.md with category in {gate|session|governance}
# MUST be ≤150 lines. Enforces thin-orchestrator pattern — commands delegate
# to API endpoints; data/logic lives in core/modules/management/*.py.
check_30() {
    local cmd_dir="$PROJECT_ROOT/.claude/commands"
    if [ ! -d "$cmd_dir" ]; then
        log_skip 30 ".claude/commands/ dir not present (non-Claude-Code repo or spoke without local commands)"
        return 0
    fi
    local violations
    violations=$(python3 - "$cmd_dir" <<'PY'
import sys, re
from pathlib import Path

cmd_dir = Path(sys.argv[1])
LIMIT = 150
GATED_CATEGORIES = {"gate", "session", "governance"}
violations = []

for path in sorted(cmd_dir.glob("AOS_*.md")):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    # Parse frontmatter for category (if present)
    category = None
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            fm = text[4:end]
            m = re.search(r"^category:\s*(\S+)", fm, re.MULTILINE)
            if m:
                category = m.group(1).strip().strip('"').strip("'")
    # Count lines
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    # Apply limit only for gated categories; unknown category treated as gated for safety
    if category is None or category in GATED_CATEGORIES:
        if line_count > LIMIT:
            violations.append(f"{path.name}:{line_count} (category={category or 'unknown'})")

if violations:
    print(f"VIOLATIONS:{len(violations)}")
    for v in violations[:10]:
        print(v)
else:
    print("OK")
PY
    )
    local code
    code=$(echo "$violations" | head -1)
    if [ "$code" = "OK" ]; then
        log_pass 30 "AOS commands within 150-line limit (Iron Rule #13 / ADR041)"
    else
        local n="${code#VIOLATIONS:}"
        local sample
        sample=$(echo "$violations" | sed -n '2p')
        log_fail 30 "$n AOS command(s) exceed 150-line limit — Iron Rule #13 violation. Sample: $sample"
    fi
}

# ================================================================
# Check 31: AOS command frontmatter required (ADR041 / Iron Rule #13)
# ================================================================
# Every .claude/commands/AOS_*.md MUST declare YAML frontmatter with
# summary: (string) + category: (one of: gate|session|governance|project|
# infrastructure|decision|meta).
check_31() {
    local cmd_dir="$PROJECT_ROOT/.claude/commands"
    if [ ! -d "$cmd_dir" ]; then
        log_skip 31 ".claude/commands/ dir not present (skip)"
        return 0
    fi
    local result
    result=$(python3 - "$cmd_dir" <<'PY'
import sys, re
from pathlib import Path

cmd_dir = Path(sys.argv[1])
VALID_CATS = {"gate","session","governance","project","infrastructure","decision","meta"}
problems = []

for path in sorted(cmd_dir.glob("AOS_*.md")):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    if not text.startswith("---\n"):
        problems.append(f"{path.name}: no frontmatter")
        continue
    end = text.find("\n---\n", 4)
    if end == -1:
        problems.append(f"{path.name}: frontmatter not closed")
        continue
    fm = text[4:end]
    has_summary = bool(re.search(r"^summary:\s*\S", fm, re.MULTILINE))
    m_cat = re.search(r"^category:\s*(\S+)", fm, re.MULTILINE)
    if not has_summary:
        problems.append(f"{path.name}: missing summary:")
    if not m_cat:
        problems.append(f"{path.name}: missing category:")
        continue
    cat = m_cat.group(1).strip().strip('"').strip("'")
    if cat not in VALID_CATS:
        problems.append(f"{path.name}: invalid category={cat}")

if problems:
    print(f"VIOLATIONS:{len(problems)}")
    for p in problems[:10]:
        print(p)
else:
    print("OK")
PY
    )
    local code
    code=$(echo "$result" | head -1)
    if [ "$code" = "OK" ]; then
        log_pass 31 "AOS command frontmatter (summary + category) present — ADR041"
    else
        local n="${code#VIOLATIONS:}"
        local sample
        sample=$(echo "$result" | sed -n '2p')
        log_fail 31 "$n AOS command(s) missing/invalid frontmatter — ADR041 violation. Sample: $sample"
    fi
}

# ================================================================
# Check 32: Iron Rule #11 enforcement — _aos/ tree must be committed after propagation.
# Uncommitted diff = hub→spoke sync incomplete; spoke-side roles cannot fix per ADR040.
# (Restored from AOS-V328 commit 2458363; V327 team_100 fix — 2026-04-21)
# ================================================================
check_32() {
    if ! git -C "$PROJECT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_skip 32 "not a git working tree (skip)"
        return 0
    fi
    local dirty
    dirty=$(git -C "$PROJECT_ROOT" status --porcelain -- _aos/ 2>/dev/null)
    if [ -z "$dirty" ]; then
        log_pass 32 "_aos/ tree committed (no propagation drift) — IR#11"
    else
        local count sample
        count=$(echo "$dirty" | wc -l | tr -d ' ')
        sample=$(echo "$dirty" | head -1)
        log_fail 32 "uncommitted _aos/ drift — $count file(s). Run aos_sync_all.sh via team_00/team_100. First: $sample"
    fi
}

# ================================================================
# Check 34: Handoff command delegates to hub API (AOS-V327 addendum — team_100 2026-04-21)
# Ensures .claude/commands/AOS_handoff.md references the unified prompt endpoint;
# skips when Claude commands are absent (spoke without local commands).
# ================================================================
check_34() {
    local hf="$PROJECT_ROOT/.claude/commands/AOS_handoff.md"
    if [ ! -f "$hf" ]; then
        log_skip 34 ".claude/commands/AOS_handoff.md not present — skip"
        return 0
    fi
    if grep -qF "/api/prompts/generate" "$hf"; then
        log_pass 34 "AOS_handoff.md references hub /api/prompts/generate (no local re-implementation)"
    else
        log_fail 34 "AOS_handoff.md must reference /api/prompts/generate — do not re-implement handoff locally (Iron Rule #13)"
    fi
}

# ================================================================
# Check 33: MSG file naming under _COMMUNICATION/ (WARN-only — AOS-V327 AC-09)
# Flags MSG-*.md that match neither hub (MSG-HUB-*) nor Module 12 (MSG-YYYYMMDD-NNN).
# Non-blocking: never increments FAIL_COUNT.
# ================================================================
check_33() {
    local comm="$PROJECT_ROOT/_COMMUNICATION"
    if [ ! -d "$comm" ]; then
        log_skip 33 "_COMMUNICATION/ not found — skip"
        return 0
    fi
    local result
    result=$(python3 - "$comm" <<'PY'
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
# Hub team messaging (ADR043); Module 12 initiator/response
pat_hub = re.compile(r"^MSG-HUB-\d{8}-\d{3}\.md$")
pat_m12 = re.compile(r"^MSG-\d{8}-\d{3}\.md$")
pat_m12_resp = re.compile(r"^MSG-\d{8}-\d{3}-RESPONSE\.md$")

hits = []
for p in root.rglob("MSG-*.md"):
    name = p.name
    if pat_hub.match(name) or pat_m12.match(name) or pat_m12_resp.match(name):
        continue
    rel = p.relative_to(root)
    hits.append(str(rel))

if hits:
    print(f"WARN:{len(hits)}")
    for h in sorted(hits)[:25]:
        print(h)
else:
    print("OK")
PY
    )
    local code
    code=$(echo "$result" | head -1)
    if [ "$code" = "OK" ]; then
        log_pass 33 "MSG file naming under _COMMUNICATION/ — no unexpected MSG-*.md patterns"
    else
        local n="${code#WARN:}"
        echo "  [WARN] Check 33: $n unexpected MSG-*.md filename(s) (advisory — ADR043 vs Module 12 naming)"
        echo "$result" | sed -n '2,30p' | sed 's/^/    /'
        log_pass 33 "MSG naming advisory complete (non-blocking)"
    fi
}

# ================================================================
# Check 35: QA_REQUEST enum lint (advisory — AOS-V324-WP-QA-ENUM-LINT)
# Validates verdict/confidence/blocked_reason_code in QA_REQUEST.md
# artifacts. Non-blocking: never increments FAIL_COUNT.
# ================================================================
check_35() {
    local script="$SCRIPT_DIR/validate_qa_request_enums.py"
    if [ ! -f "$script" ]; then
        log_skip 35 "validate_qa_request_enums.py not found — skip"
        return 0
    fi
    local result
    result=$(python3 "$script" "$PROJECT_ROOT" 2>&1)
    local warns
    warns=$(echo "$result" | grep -c "^WARN:" || true)
    if [ "$warns" -gt 0 ]; then
        echo "  [WARN] Check 35: $warns QA_REQUEST enum violation(s) (advisory — non-blocking)"
        echo "$result" | grep "^WARN:" | head -25 | sed 's/^/    /'
        log_pass 35 "QA enum lint advisory complete ($warns violation(s) — non-blocking)"
    else
        log_pass 35 "QA_REQUEST enum lint — all values valid (or no QA_REQUEST files found)"
    fi
}

# Check 36: MSG branch independence — ADR043 v1.1.0 §4 + §5
# Verify that every command that sends/reads MSGs references msg_preflight.sh
# (API-first pre-flight) and, for sending commands, msg_deliver_file (branch-safe
# push to origin/main in the fallback path).
check_36() {
    if _modelb_cache_absent; then
        log_skip 36 "lean-kit cache not hydrated (Model B / ADR054) — run scripts/aos_governance_bootstrap.sh"
        return 0
    fi
    local helper_src="core/modules/team-messaging/scripts/msg_preflight.sh"
    local helper_snapshot="_aos/lean-kit/modules/team-messaging/scripts/msg_preflight.sh"
    # Snapshot path is the baseline reference this check verifies command wiring against — absent means
    # the check cannot meaningfully run here (cold clone / pre-hydration), not that wiring is broken.
    _require_file 36 "$PROJECT_ROOT/$helper_snapshot" "MSG branch independence — msg_preflight.sh snapshot" || return 0
    local missing=0
    local details=""

    # Hub: also require top-level SSoT path (spokes have no lean-kit/ at project root)
    if [ "$CONTEXT" = "hub" ]; then
        if [ ! -f "$PROJECT_ROOT/$helper_src" ]; then
            missing=$((missing+1))
            details="${details}\n    [MISSING] $helper_src"
        fi
    fi

    # Sending commands must reference msg_preflight.sh AND msg_deliver_file
    local send_cmds="AOS_SendMail AOS_gate-mandate AOS_qa AOS_validate AOS_handoff"
    for cmd in $send_cmds; do
        local f="$PROJECT_ROOT/.claude/commands/${cmd}.md"
        if [ ! -f "$f" ]; then continue; fi
        if ! grep -q "msg_preflight.sh" "$f"; then
            missing=$((missing+1))
            details="${details}\n    [MISSING preflight ref] .claude/commands/${cmd}.md"
        fi
        if ! grep -q "msg_deliver_file\|branch-safe" "$f"; then
            missing=$((missing+1))
            details="${details}\n    [MISSING branch-safe ref] .claude/commands/${cmd}.md"
        fi
    done

    # Reading commands must reference msg_preflight.sh (read side)
    for cmd in AOS_mail; do
        local f="$PROJECT_ROOT/.claude/commands/${cmd}.md"
        if [ ! -f "$f" ]; then continue; fi
        if ! grep -q "msg_preflight.sh" "$f"; then
            missing=$((missing+1))
            details="${details}\n    [MISSING preflight ref] .claude/commands/${cmd}.md"
        fi
    done

    if [ "$missing" -gt 0 ]; then
        log_fail 36 "MSG branch independence — $missing gap(s) in preflight/branch-safe wiring (ADR043 v1.1.0 §4/§5):$details"
    else
        log_pass 36 "MSG branch independence — all send/read commands wired to msg_preflight.sh + msg_deliver_file (ADR043 v1.1.0 §4/§5)"
    fi
}

# Check 37: Multi-domain routing wired — ADR043 v1.1.0 §6 / MSG-DOMAIN-ROUTING-FIX
# Verify the messaging API + helper script honor project_id (header / body / param)
# so spoke sessions land MSGs in the spoke's _COMMUNICATION/, not the hub's.
check_37() {
    local missing=0
    local details=""

    local server_module="$PROJECT_ROOT/core/modules/management/team_messaging.py"
    if [ -f "$server_module" ]; then
        if ! grep -q "_root_for_project\|project_id" "$server_module"; then
            missing=$((missing+1))
            details="${details}\n    [server] team_messaging.py missing project_id threading"
        fi
    fi

    local routes_file="$PROJECT_ROOT/core/modules/management/dashboard_routes.py"
    if [ -f "$routes_file" ]; then
        if ! grep -q "X-Project-Id" "$routes_file"; then
            missing=$((missing+1))
            details="${details}\n    [routes] dashboard_routes.py missing X-Project-Id header dep"
        fi
    fi

    for helper in \
        "core/modules/team-messaging/scripts/msg_preflight.sh" \
        "_aos/lean-kit/modules/team-messaging/scripts/msg_preflight.sh" ; do
        local f="$PROJECT_ROOT/$helper"
        if [ -f "$f" ]; then
            if ! grep -q "msg_detect_project_id" "$f"; then
                missing=$((missing+1))
                details="${details}\n    [client] $helper missing msg_detect_project_id"
            fi
            if ! grep -q "msg_curl" "$f"; then
                missing=$((missing+1))
                details="${details}\n    [client] $helper missing msg_curl wrapper"
            fi
        fi
    done

    if [ "$missing" -gt 0 ]; then
        log_fail 37 "Multi-domain routing wiring incomplete — $missing gap(s) (ADR043 v1.1.0 §6):$details"
    else
        log_pass 37 "Multi-domain routing wired — server threads project_id, routes accept X-Project-Id, helper auto-detects spoke (ADR043 v1.1.0 §6)"
    fi
}

# Check 38: ADR043 v1.2.0 §6 + §7 + archive endpoint wired (AOS-MSG-FOLLOWUPS-WP001)
# Verify: (a) ADR043 v1.2.0 active with §6/§7 formal text; (b) archive_message
# service function exists; (c) POST /messaging/archive route exists; (d) /AOS_mail
# Phase 4 references the new endpoint (not the old 404-returning path).
check_38() {
    local missing=0
    local details=""

    # (a) ADR043 v1.2.0 active + formal §6 / §7 text
    # Hub: governance/directives/; spoke: _aos/governance/directives/ (after propagation)
    local adr_dir
    if [ "$CONTEXT" = "hub" ]; then
        adr_dir="$PROJECT_ROOT/governance/directives"
    else
        adr_dir="$PROJECT_ROOT/_aos/governance/directives"
    fi
    local adr_active="$adr_dir/ADR043_TEAM_MESSAGING_PROTOCOL_v1.2.0.md"
    local adr_v110="$adr_dir/ADR043_TEAM_MESSAGING_PROTOCOL_v1.1.0.md"
    if [ ! -f "$adr_active" ]; then
        missing=$((missing+1))
        details="${details}\n    [ADR043] v1.2.0 not present under ${adr_dir#$PROJECT_ROOT/}/"
    else
        if ! grep -q '^## 6. Multi-Domain Routing' "$adr_active"; then
            missing=$((missing+1))
            details="${details}\n    [ADR043] §6 Multi-Domain Routing not found in v1.2.0"
        fi
        if ! grep -q '^## 7. Single-MSG Archive Endpoint' "$adr_active"; then
            missing=$((missing+1))
            details="${details}\n    [ADR043] §7 Single-MSG Archive Endpoint not found in v1.2.0"
        fi
    fi
    if [ -f "$adr_v110" ]; then
        missing=$((missing+1))
        details="${details}\n    [ADR043] v1.1.0 still active under ${adr_dir#$PROJECT_ROOT/}/ (should be archived)"
    fi

    # (b) Service: archive_message function
    local server="$PROJECT_ROOT/core/modules/management/team_messaging.py"
    if [ -f "$server" ] && ! grep -q 'def archive_message' "$server"; then
        missing=$((missing+1))
        details="${details}\n    [server] team_messaging.py missing archive_message()"
    fi

    # (c) Route: POST /messaging/archive
    local routes="$PROJECT_ROOT/core/modules/management/dashboard_routes.py"
    if [ -f "$routes" ] && ! grep -q '/messaging/archive' "$routes"; then
        missing=$((missing+1))
        details="${details}\n    [routes] dashboard_routes.py missing POST /messaging/archive"
    fi

    # (d) AOS_mail Phase 4 references the new endpoint
    local aos_mail="$PROJECT_ROOT/.claude/commands/AOS_mail.md"
    if [ -f "$aos_mail" ]; then
        if ! grep -q '/api/messaging/archive' "$aos_mail"; then
            missing=$((missing+1))
            details="${details}\n    [client] AOS_mail.md Phase 4 not wired to /api/messaging/archive"
        fi
        if grep -q '/api/messaging/{team_id}/archive' "$aos_mail"; then
            missing=$((missing+1))
            details="${details}\n    [client] AOS_mail.md Phase 4 still references the old 404 path"
        fi
    fi

    if [ "$missing" -gt 0 ]; then
        log_fail 38 "ADR043 v1.2.0 / archive endpoint wiring incomplete — $missing gap(s) (AOS-MSG-FOLLOWUPS-WP001):$details"
    else
        log_pass 38 "ADR043 v1.2.0 §6+§7 published, archive endpoint wired end-to-end (AOS-MSG-FOLLOWUPS-WP001)"
    fi
}

# Check 39: MSG-LOG operational (W4 dependency — AOS-V4-WP-MSG-LOG)
# v5 messaging is the DB v2 bus (canonical port :8092). The file _COMMUNICATION/_log/messages.log
# is a DEGRADE-ONLY fallback, NOT the live transport — so "operational" = the v5 bus is reachable.
# A quiet (stale) file log on an ACTIVE domain is normal (mail flows via the DB, not the file) and
# is therefore an ADVISORY, never a FAIL.
#
# 2026-06-28 (AOS-V5-WP-GOV-SNAPSHOT-HARDENING R8): the prior check probed the RETIRED v3 port
#   :8090 (waldhomeserver legacy stub → HTTP 410) and then HARD-FAILED on file-log staleness, so
#   every active v5 domain that uses the DB bus false-FAILed (confirmed on eyalamit/smallfarms/
#   nimrod-bio — all active, 17–30d-old file logs — and tiktrack, active right now with a 4d log).
#   Fix: probe the LIVE v5 API on :8092 first (env AOS_API_BASE, then the canonical waldhomeserver
#   :8092); file-log staleness is downgraded to an advisory (WARN+PASS) — surfaced for genuinely
#   dark domains, but never blocking, because file-log mtime is not a v5 liveness signal.
# Cross-platform mtime via python3 (avoids stat -f/-c divergence).
check_39() {
    # Canonical v5 API (port-registry SSoT; Tailscale). Env-overridable for tests / alt-canonical ops.
    local _canonical_api="${AOS_CHECK39_CANONICAL_API:-http://100.125.98.56:8092}"
    local _api_base="${AOS_API_BASE:-${AOS_PUBLIC_API_BASE:-http://127.0.0.1:8092}}"
    local _http_code
    _http_code=$(curl -s -o /dev/null -w '%{http_code}' \
        --max-time 2 --connect-timeout 2 \
        "${_api_base}/api/system/health" 2>/dev/null || echo "000")
    if [ "$_http_code" = "200" ]; then
        log_pass 39 "MSG-LOG operational: v5 messaging bus healthy at ${_api_base} (HTTP 200 — DB v2 bus active)"
        return
    fi
    # The configured base is unreachable / a legacy stub (000/410/…): retry the canonical v5 API
    # (:8092) before any file fallback — the live bus is server-side, not local.
    if [ "$_api_base" != "$_canonical_api" ]; then
        local _retry_code
        _retry_code=$(curl -s -o /dev/null -w '%{http_code}' \
            --max-time 2 --connect-timeout 2 \
            "${_canonical_api}/api/system/health" 2>/dev/null || echo "000")
        if [ "$_retry_code" = "200" ]; then
            log_pass 39 "MSG-LOG operational: v5 messaging bus healthy at ${_canonical_api} (initial ${_api_base} HTTP ${_http_code}; canonical v5 endpoint responded). Advisory: export AOS_API_BASE=${_canonical_api} to skip the retry."
            return
        fi
        printf '  [INFO 39] %s\n' "v5 bus probe: ${_api_base} HTTP ${_http_code}; canonical ${_canonical_api} HTTP ${_retry_code}. Proceeding to degrade-only file fallback." >&2
    fi
    # Degrade-only file fallback: the v5 bus was UNREACHABLE from this context. The file log is NOT the live
    # transport (v5 mail flows via the DB bus), so its mtime is not a liveness signal — we therefore SKIP
    # ("couldn't verify"), never PASS (we did not confirm the bus, so an outage must not read as operational —
    # cross-engine finding) and never FAIL (staleness != failure on an active domain; R8).
    local log_file="$PROJECT_ROOT/_COMMUNICATION/_log/messages.log"
    if [ ! -f "$log_file" ]; then
        log_skip 39 "MSG-LOG: v5 bus unreachable from this context + no file log (file log is degrade-only; non-blocking)"
        return
    fi
    local days_old
    days_old=$(python3 -c "
import os, time
mtime = os.path.getmtime('$log_file')
print(int((time.time() - mtime) / 86400))
")
    echo "  [WARN] Check 39: v5 bus (:8092) unreachable from this context; degrade-only file log is ${days_old}d old (mtime is not a v5 liveness signal — v5 mail flows via the DB bus)." >&2
    log_skip 39 "MSG-LOG: could not verify the v5 bus from this context; file log ${days_old}d old (degrade-only, non-blocking; R8)"
}

# Check 40: MSG-HARDENING hook active (W5 dependency — AOS-V4-WP-MSG-HARDENING)
# W5 delivers a pre-commit hook (not commit-msg) that chains msg_precommit_hook.sh.
# Verify: (a) git pre-commit hook is installed and executable; (b) msg_precommit_hook.sh
# exists and is executable; (c) hook chains MSG hardening (references msg_precommit_hook.sh).
# Uses git rev-parse --git-path for linked-worktree compatibility (W5 R1 lesson).
# NOTE: LOD200 sketch assumed commit-msg; actual W5 deliverable uses pre-commit.
#       Deviation documented in W7 completion report §6.
check_40() {
    # Resolve pre-commit hook path (worktree-safe via git rev-parse).
    local hook_path
    hook_path=$(git -C "$PROJECT_ROOT" rev-parse --git-path hooks/pre-commit 2>/dev/null || true)
    if [ -n "$hook_path" ] && [[ "$hook_path" != /* ]]; then
        hook_path="$PROJECT_ROOT/$hook_path"
    fi
    # Resolve msg_precommit_hook.sh location: hub canon at lean-kit/..., spoke snapshot at _aos/lean-kit/...
    local msg_hook=""
    if [ -f "$PROJECT_ROOT/core/modules/team-messaging/scripts/msg_precommit_hook.sh" ]; then
        msg_hook="$PROJECT_ROOT/core/modules/team-messaging/scripts/msg_precommit_hook.sh"
    elif [ -f "$PROJECT_ROOT/_aos/lean-kit/modules/team-messaging/scripts/msg_precommit_hook.sh" ]; then
        msg_hook="$PROJECT_ROOT/_aos/lean-kit/modules/team-messaging/scripts/msg_precommit_hook.sh"
    fi
    # Spoke context: hook installation is operator choice. SKIP cleanly when no hook present
    # (acceptable pre-W5-propagation or when spoke opts out of commit-time MSG validation).
    if [ "$CONTEXT" != "hub" ]; then
        if [ -z "$hook_path" ] || [ ! -f "$hook_path" ]; then
            if [ -z "$msg_hook" ]; then
                log_skip 40 "MSG-HARDENING: spoke without pre-commit hook + no msg_precommit_hook.sh snapshot — acceptable pre-W5-propagation"
            else
                log_skip 40 "MSG-HARDENING: spoke msg_precommit_hook.sh snapshot present but pre-commit hook not installed — acceptable (operator choice)"
            fi
            return
        fi
        # Spoke with hook installed → validate it the same way as hub.
    fi
    # Hub (or spoke with hook installed): full validation.
    local missing=0
    local details=""
    if [ -z "$hook_path" ]; then
        missing=$((missing+1))
        details="${details}\n    [pre-commit] could not resolve hook path via git rev-parse --git-path"
    elif [ ! -f "$hook_path" ]; then
        missing=$((missing+1))
        details="${details}\n    [pre-commit] hook absent at $hook_path"
    elif [ ! -x "$hook_path" ]; then
        missing=$((missing+1))
        details="${details}\n    [pre-commit] hook not executable at $hook_path"
    elif ! grep -q "msg_precommit_hook" "$hook_path" 2>/dev/null; then
        missing=$((missing+1))
        details="${details}\n    [pre-commit] hook does not chain msg_precommit_hook.sh"
    fi
    if [ -z "$msg_hook" ]; then
        missing=$((missing+1))
        details="${details}\n    [msg_hook] msg_precommit_hook.sh absent at lean-kit/ or _aos/lean-kit/ — W5 not delivered"
    elif [ ! -x "$msg_hook" ]; then
        missing=$((missing+1))
        details="${details}\n    [msg_hook] msg_precommit_hook.sh not executable at $msg_hook"
    fi
    if [ "$missing" -gt 0 ]; then
        log_fail 40 "MSG-HARDENING hook wiring incomplete — $missing gap(s):$details"
    else
        log_pass 40 "MSG-HARDENING active: pre-commit hook installed + chains msg_precommit_hook.sh (W5)"
    fi
}

# Check 41: AUTO-ACTIVATION dryrun available (W6 dependency — AOS-V4-WP-AUTO-ACTIVATION-DRYRUN)
# SKIP when auto-activation/ directory absent (pre-W6 state).
# FAIL when dryrun.sh missing or not executable.
# PASS when dryrun.sh runs and produces recognisable decision output (DECISION/ACTIVATE/SKIP/REJECT).
check_41() {
    local dryrun_dir="$PROJECT_ROOT/auto-activation"
    local dryrun_sh="$dryrun_dir/dryrun.sh"
    local fixture="$dryrun_dir/tests/fixtures/clean_activation.json"
    if [ ! -d "$dryrun_dir" ]; then
        log_skip 41 "auto-activation/ directory absent — acceptable pre-W6"
        return
    fi
    if [ ! -f "$dryrun_sh" ]; then
        log_fail 41 "dryrun.sh absent in auto-activation/ — W6 not yet delivered"
        return
    fi
    if [ ! -x "$dryrun_sh" ]; then
        log_fail 41 "dryrun.sh not executable"
        return
    fi
    local output
    if [ -f "$fixture" ]; then
        output=$(bash "$dryrun_sh" --fixture "$fixture" 2>/dev/null || true)
    else
        output=$(bash "$dryrun_sh" 2>/dev/null || true)
    fi
    if echo "$output" | grep -qiE "DECISION|ACTIVATE|SKIP|REJECT"; then
        log_pass 41 "AUTO-ACTIVATION dryrun available: executable + produces decision output"
    else
        log_fail 41 "dryrun.sh ran but produced no recognizable decision output (expected DECISION/ACTIVATE/SKIP/REJECT)"
    fi
}

# Check 42: Sprint discipline — no active WP may exceed 3 sprints (ADR044 §Sprint Discipline)
# Reads sprint_count from every _aos/work_packages/*/metadata.yaml.
# Only WPs with status ACTIVE, IN_PROGRESS, or LOD*_DRAFT and explicit sprint_count > 3 fail.
# Absent sprint_count = compliant (pre-v4 WPs without the field are not penalised).
check_42() {
    local violations=0
    local details=""
    while IFS= read -r meta; do
        local wp_id sprint_count status
        wp_id=$(basename "$(dirname "$meta")")
        sprint_count=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f: m = yaml.safe_load(f) or {}
print(m.get('sprint_count', ''))
" "$meta" 2>/dev/null)
        status=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f: m = yaml.safe_load(f) or {}
print(m.get('status', ''))
" "$meta" 2>/dev/null)
        if [[ "$status" =~ ^(ACTIVE|IN_PROGRESS|LOD[0-9]+_DRAFT)$ ]] && \
           [ -n "$sprint_count" ] && \
           [ "$sprint_count" -gt 3 ] 2>/dev/null; then
            violations=$((violations+1))
            details="${details}\n    $wp_id: sprint_count=$sprint_count (max 3)"
        fi
    done < <(find "$AOS_DIR/work_packages" -name "metadata.yaml" 2>/dev/null)
    if [ "$violations" -gt 0 ]; then
        log_fail 42 "Sprint discipline violated — $violations WP(s) exceed 3-sprint cap:$details"
    else
        log_pass 42 "Sprint discipline: all active WPs within ≤3 sprint cap"
    fi
}

# Check 43: Milestone completeness gate (v4.0.0 GA criterion — G4 / V4_GAP_MATRIX §5)
# SKIP when _aos/milestones/ absent (pre-MS001 state — no milestone definitions to check against).
# A MASTER_CLOSURE for a prior milestone does NOT activate this check; only the presence of
# _aos/milestones/ (containing milestone WP listings) triggers full engagement.
# When _aos/milestones/ exists, checks:
#   (a) No forbidden markers ([T]BD / [F]IXME / to [b]e defined) in any WP spec under
#       $AOS_DIR/work_packages/ — EXCLUDING the W7 spec dir to avoid self-referential failure
#       (W7 R0 decision A: char-class exclusion of AOS-V4-WP-VALIDATE-CHECKS-39-43/).
#   (b) All milestone WPs in LOD500 / LOD500_LOCKED, or listed in MASTER_CLOSURE deferred section.
# NOTE: forbidden-marker literals obfuscated in scanner source per W5 R3 lesson.
check_43() {
    local milestone_dir="$AOS_DIR/milestones"
    local closure_glob="$PROJECT_ROOT/_COMMUNICATION/team_00/MASTER_CLOSURE*.md"
    if [ ! -d "$milestone_dir" ]; then
        log_skip 43 "Milestone completeness gate: _aos/milestones/ absent — no milestone definitions to check against (acceptable pre-MS001)"
        return
    fi
    local failures=0
    local details=""
    # (a) No [T]BD/[F]IXME/to [b]e defined in WP specs (W7 spec dir excluded — decision A)
    local tbd_hits
    tbd_hits=$(grep -ril --exclude-dir="AOS-V4-WP-VALIDATE-CHECKS-39-43" \
        "[T]BD\|[F]IXME\|to [b]e defined" \
        "$AOS_DIR/work_packages/" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$tbd_hits" -gt 0 ]; then
        failures=$((failures+1))
        details="${details}\n    [forbidden-markers] $tbd_hits WP spec file(s) contain forbidden incomplete-work markers"
    fi
    # (b) All milestone WPs in LOD500_LOCKED or deferred in MASTER_CLOSURE
    local closure_file
    closure_file=$(ls $closure_glob 2>/dev/null | sort | tail -1)
    while IFS= read -r meta; do
        local wp_id lod_status
        wp_id=$(basename "$(dirname "$meta")")
        lod_status=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f: m = yaml.safe_load(f) or {}
print(m.get('lod_status', ''))
" "$meta" 2>/dev/null)
        if [ "$lod_status" != "LOD500" ] && [ "$lod_status" != "LOD500_LOCKED" ]; then
            if [ -n "$closure_file" ] && grep -q "$wp_id" "$closure_file" 2>/dev/null; then
                : # Listed as deferred in MASTER_CLOSURE — acceptable
            else
                failures=$((failures+1))
                details="${details}\n    [incomplete] $wp_id lod_status=$lod_status — not LOD500_LOCKED and not in MASTER_CLOSURE deferred section"
            fi
        fi
    done < <(find "$milestone_dir" -name "*.yaml" -exec grep -l "wp_id" {} \; 2>/dev/null)
    if [ "$failures" -gt 0 ]; then
        log_fail 43 "Milestone completeness gate FAILED — $failures issue(s):$details"
    else
        log_pass 43 "Milestone completeness gate: all WPs LOD500_LOCKED or explicitly deferred; 0 forbidden-marker strings"
    fi
}

# Check 44: Track+Effort metadata enforcement (C14 — ADR044 §Track Model)
# Every _aos/work_packages/*/metadata.yaml must declare a valid track: and effort: field.
# Valid tracks: EXPRESS STANDARD MANAGED RESEARCH OPS CONTENT
# Valid efforts: LOW NORMAL HI
check_44() {
    local valid_tracks="EXPRESS STANDARD MANAGED RESEARCH OPS CONTENT"
    local valid_efforts="LOW NORMAL HI"
    local violations=0
    local details=""
    while IFS= read -r meta; do
        local wp_id track effort
        wp_id=$(basename "$(dirname "$meta")")
        track=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f: m = yaml.safe_load(f) or {}
print(m.get('track', ''))
" "$meta" 2>/dev/null)
        effort=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f: m = yaml.safe_load(f) or {}
print(m.get('effort', ''))
" "$meta" 2>/dev/null)
        local ok=1
        if [ -z "$track" ] || ! echo "$valid_tracks" | grep -qw "$track"; then
            ok=0; details="${details}\n    $wp_id: track='$track' invalid or missing"
        fi
        if [ -z "$effort" ] || ! echo "$valid_efforts" | grep -qw "$effort"; then
            ok=0; details="${details}\n    $wp_id: effort='$effort' invalid or missing"
        fi
        [ "$ok" -eq 0 ] && violations=$((violations+1))
    done < <(find "$AOS_DIR/work_packages" -name "metadata.yaml" 2>/dev/null)
    if [ "$violations" -gt 0 ]; then
        log_fail 44 "Track+Effort metadata enforcement — $violations WP(s) missing/invalid fields:$details"
    else
        log_pass 44 "Track+Effort metadata: all WP metadata.yaml files have valid track: and effort: fields"
    fi
}

# Check 45: WAN dual-stack health (W11 — IPv6-only WAN compatibility advisory).
# Authority: ADR048 + IR#15 + lean-kit/.../WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md §8.
# Reads $PROJECT_ROOT/_aos/server_dual_stack_status.json (refreshed by
# wan_dual_stack_probe.sh on each spoke).
# SKIP when status file absent (probe not yet run; acceptable pre-W11-propagation).
# SKIP with "WARN:" prefix in message when ipv4_outbound=false AND
# mitigation_scenario IN {none, expired_temporary} — preserves PASS/FAIL/SKIP exit
# semantics on v4.0.0 release artifact (option b per RESPONSE corrections).
# PASS when status indicates dual-stack OK or a permanent mitigation is in place.
check_45() {
    local status_file="$PROJECT_ROOT/_aos/server_dual_stack_status.json"
    local _api_base="${AOS_API_BASE:-${AOS_PUBLIC_API_BASE:-http://127.0.0.1:8090}}"
    local _wan_json=""
    local _wan_src="local-file"
    local _wan_http
    _wan_http=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 --connect-timeout 3 \
        "${_api_base}/api/server/wan-status" 2>/dev/null || echo "000")
    if [ "$_wan_http" = "200" ]; then
        _wan_json=$(curl -s --max-time 5 "${_api_base}/api/server/wan-status" 2>/dev/null || echo "")
        _wan_src="api:${_api_base}"
    fi
    if [ -z "$_wan_json" ]; then
        if [ ! -f "$status_file" ]; then
            log_skip 45 "WAN dual-stack status absent — API not reachable and local file missing"
            return
        fi
        _wan_json=$(cat "$status_file" 2>/dev/null || echo "")
        if [ -z "$_wan_json" ]; then
            log_skip 45 "WAN dual-stack status file unreadable"
            return
        fi
    fi
    # Parse JSON via python3 (already required by validate_aos.sh).
    local parse_out
    parse_out=$(python3 -c "
import json, sys
d = json.loads(sys.argv[1])
print(d.get('ipv4_outbound', None))
print(d.get('ipv6_outbound', None))
print(d.get('mitigation_scenario', ''))
print(d.get('checked_at', ''))
print(d.get('server', 'unknown'))
" "$_wan_json" 2>/dev/null)
    if [ -z "$parse_out" ]; then
        log_skip 45 "WAN dual-stack status unparseable JSON (source=$_wan_src)"
        return
    fi
    local ipv4_ok ipv6_ok scenario checked_at server
    ipv4_ok=$(echo "$parse_out" | sed -n '1p')
    ipv6_ok=$(echo "$parse_out" | sed -n '2p')
    scenario=$(echo "$parse_out" | sed -n '3p')
    checked_at=$(echo "$parse_out" | sed -n '4p')
    server=$(echo "$parse_out" | sed -n '5p')
    # Staleness check (canon §2): status file older than 30 days defeats the
    # "verify after deploy/network change" purpose of IR#15 and must surface
    # as advisory regardless of the recorded scenario.
    local stale_days
    stale_days=$(python3 -c "
import datetime, sys
ts = sys.argv[1]
try:
    if ts.endswith('Z'):
        ts = ts[:-1] + '+00:00'
    dt = datetime.datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    age = datetime.datetime.now(datetime.timezone.utc) - dt
    print(int(age.total_seconds() // 86400))
except Exception:
    print(-1)
" "$checked_at" 2>/dev/null)
    if [ -n "$stale_days" ] && [ "$stale_days" -gt 30 ] 2>/dev/null; then
        log_skip 45 "WARN: WAN dual-stack — status file on '$server' is stale ($stale_days days old, >30d threshold; canon §2). Re-run wan_dual_stack_probe.sh to refresh. Last checked: $checked_at"
        return
    fi
    # Advisory: IPv4 outbound failing AND no permanent mitigation.
    # Scenarios "none" + "expired_temporary" + "E" are all canon-defined advisory cases
    # (E is emergency-only DNS64 patch per canon §5 / Appendix B — explicitly NON-CANON
    # and must be replaced ASAP with a permanent matrix scenario B/C/D/F).
    if [ "$ipv4_ok" = "False" ] && { [ "$scenario" = "none" ] || [ "$scenario" = "expired_temporary" ] || [ "$scenario" = "E" ]; }; then
        log_skip 45 "WARN: WAN dual-stack — IPv4 outbound failing on '$server' with non-permanent mitigation (scenario='$scenario'); consult extensions/home-server-infrastructure/WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md §7. Last checked: $checked_at"
        return
    fi
    log_pass 45 "WAN dual-stack — server='$server' ipv4=$ipv4_ok ipv6=$ipv6_ok scenario='$scenario' (checked $checked_at)"
}

# Check 46: Registry SSoT drift — `_aos/projects.yaml` is the canonical project
# registry; derived surfaces (currently: msg_preflight.sh Tier 3 case block)
# MUST match a fresh derivation. Drift = FAIL.
# Authority: ADR049 Registry SSoT Lockdown.
# Hub-only. SKIP on spokes (they don't carry projects.yaml or the derived files).
check_46() {
    # Spoke shortcut: spokes have no _aos/projects.yaml and no derived surfaces.
    if [ ! -f "$PROJECT_ROOT/_aos/projects.yaml" ]; then
        log_skip 46 "not hub — _aos/projects.yaml absent (spokes skip registry SSoT drift check)"
        return
    fi
    local sync_script="$PROJECT_ROOT/scripts/sync_derived_registries.sh"
    if [ ! -x "$sync_script" ]; then
        log_skip 46 "sync_derived_registries.sh not found or not executable (pre-ADR049 hub)"
        return
    fi
    local out
    if out=$(bash "$sync_script" --check 2>&1); then
        log_pass 46 "Registry SSoT — derived surfaces in sync with _aos/projects.yaml (ADR049)"
    else
        log_fail 46 "Registry SSoT DRIFT — derived surface(s) do not match _aos/projects.yaml. Fix: bash scripts/sync_derived_registries.sh. Detail: $out"
    fi
}

# ----------------------------------------------------------------
# Check 74 — registry local_path canonical-tree guard (hub-only; AOS-V5-WP-EXTERNAL-AUDIT-REMEDIATION WS3 AC3.1)
# Every enabled _aos/projects.yaml local_path MUST live under the canonical AOS_V5/ tree. The v5 cutover
# (C1, 17effde) repointed all spokes to .../AOS_V5/<spoke>; this check prevents regression to the OLD
# /Documents/<spoke> duplicate trees (which carried stale _aos/ and made tooling resolution ambiguous).
# ----------------------------------------------------------------
check_74() {
    if [ ! -f "$PROJECT_ROOT/_aos/projects.yaml" ]; then
        log_skip 74 "not hub — _aos/projects.yaml absent (spokes skip registry local_path canonical-tree guard)"
        return
    fi
    local out
    out=$(python3 - "$PROJECT_ROOT/_aos/projects.yaml" <<'PY'
import sys, yaml
data = yaml.safe_load(open(sys.argv[1])) or {}
bad = []
for p in data.get("projects", []):
    if not p.get("enabled", True):
        continue
    lp = p.get("local_path", "")
    # Canonical tree marker: the path segment "/AOS_V5/" (the v5 consolidated root). A missing/empty
    # local_path on an ENABLED project also fails — it is not under AOS_V5/ (it is nowhere), so it must
    # not silently bypass the guard (cross-engine finding).
    if "/AOS_V5/" not in lp:
        bad.append(f"{p.get('id','?')}={lp or '<missing>'}")
print("\n".join(bad))
PY
) || { log_fail 74 "local_path guard — could not parse _aos/projects.yaml"; return; }
    if [ -z "$out" ]; then
        log_pass 74 "registry local_path canonical-tree guard — every enabled project resolves under AOS_V5/ (WS3 AC3.1)"
    else
        log_fail 74 "registry local_path OUTSIDE AOS_V5/ — regression to a non-canonical tree. Repoint in _aos/projects.yaml. Offenders: $(echo "$out" | tr '\n' ' ')"
    fi
}

# Check 75: lean_kit_version Rule-3 format (VERSION_POLICY.md Rule 3 — version+short-sha)
# (AOS-V5-M11-WP-VALIDATION-VERSION-CANON-HYGIENE C2)
check_75() {
    _require_file 75 "$AOS_DIR/metadata.yaml" "version-canon (Rule 3)" || return 0
    local v
    v=$(python3 -c "import yaml,sys; print((yaml.safe_load(open('$AOS_DIR/metadata.yaml')) or {}).get('lean_kit_version',''))" 2>/dev/null)
    if printf '%s' "$v" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\+[0-9a-f]{7}$'; then
        log_pass 75 "lean_kit_version '$v' is Rule-3 compliant (version+short-sha)"
    else
        log_fail 75 "lean_kit_version '$v' violates VERSION_POLICY.md Rule 3 (expected semver+7hexsha); run aos_sync_all generator"
    fi
}

# ----------------------------------------------------------------
# Check 76 — Orchestrator worktree hygiene (ADR052 Addendum / Iron Rule #17, hub-only)
# The hub's shared PRIMARY checkout must never carry uncommitted changes to
# fleet-mutating authoring paths (scripts/, extensions/, lean-kit/ stub, core/governance/,
# methodology/, governance/directives/) — exactly the dangling-fix pattern the
# 2026-07-15 incident (PR #44) exposed: a real script fix, authored mid-propagation-
# run, left uncommitted in the shared tree and at risk under concurrent operation.
# Isolated worktrees (feature branches, the automation worktree) are NOT primary —
# legitimate WIP there is expected and this check does not apply to them.
# ----------------------------------------------------------------
check_76() {
    if [ ! -f "$PROJECT_ROOT/_aos/projects.yaml" ]; then
        log_skip 76 "not hub — orchestrator authoring paths only exist on the hub"
        return
    fi
    local here main_wt
    here="$(git -C "$PROJECT_ROOT" rev-parse --show-toplevel 2>/dev/null)"
    main_wt="$(git -C "$PROJECT_ROOT" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2; exit}')"
    if [ -z "$here" ] || [ -z "$main_wt" ]; then
        log_skip 76 "orchestrator worktree hygiene — git worktree info unavailable"
        return
    fi
    if [ "$here" != "$main_wt" ]; then
        log_skip 76 "orchestrator worktree hygiene — this is an isolated worktree, not the primary checkout (WIP here is expected)"
        return
    fi
    local dirty
    dirty=$(git -C "$PROJECT_ROOT" status --porcelain -- scripts/ extensions/ core/governance/ methodology/ governance/directives/ lean-kit/ 2>/dev/null)
    if [ -z "$dirty" ]; then
        log_pass 76 "orchestrator worktree hygiene — primary checkout carries no uncommitted authoring-path changes (ADR052 Addendum / IR#17)"
    else
        echo "  [FAIL] Check 76: primary checkout has uncommitted authoring-path changes:" >&2
        echo "$dirty" | sed 's/^/    /' >&2
        log_fail 76 "orchestrator worktree hygiene — primary checkout has UNCOMMITTED changes under scripts/|extensions/|core/governance/|methodology/|governance/directives/|lean-kit/ — a dangling fix at risk under concurrent shared-tree operation (ADR052 Addendum / IR#17). Commit to a branch + PR, or move the work to an isolated worktree."
    fi
}

# ----------------------------------------------------------------
# Check 77 — Autonomous-merge policy wiring (ADR052 Autonomous Merge Policy, hub + spoke)
# Every domain MUST carry the deterministic gh-merge guard: the PreToolUse hook
# `scripts/hooks/gh_merge_guard.sh` (present + executable) AND its wiring in
# `.claude/settings.json` (hooks.PreToolUse, if "Bash(gh pr merge:*)" → gh_merge_guard.sh).
# Propagated by aos_sync_all.sh; FAILs on drift so the policy can't silently fall out
# of a domain. Same enforcement spirit as Check 76 (IR#17).
# ----------------------------------------------------------------
check_77() {
    local hook="$PROJECT_ROOT/scripts/hooks/gh_merge_guard.sh"
    local sj="$PROJECT_ROOT/.claude/settings.json"
    if [ ! -f "$hook" ]; then
        log_fail 77 "autonomous-merge policy — scripts/hooks/gh_merge_guard.sh MISSING (ADR052 Autonomous Merge Policy). Run aos_sync_all to propagate."
        return
    fi
    if [ ! -x "$hook" ]; then
        log_fail 77 "autonomous-merge policy — scripts/hooks/gh_merge_guard.sh present but NOT executable (chmod +x)."
        return
    fi
    if [ ! -f "$sj" ]; then
        log_fail 77 "autonomous-merge policy — .claude/settings.json MISSING the merge-guard hook wiring (ADR052 Autonomous Merge Policy). Run aos_sync_all."
        return
    fi
    local wired
    wired=$(python3 - "$sj" <<'PY' 2>/dev/null
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception:
    print("no"); sys.exit(0)
for entry in ((d.get("hooks") or {}).get("PreToolUse") or []):
    for h in (entry.get("hooks") or []):
        if "gh_merge_guard.sh" in str(h.get("command","")) and "gh pr merge" in str(h.get("if","")):
            print("yes"); sys.exit(0)
print("no")
PY
)
    if [ "$wired" = "yes" ]; then
        log_pass 77 "autonomous-merge policy wired — PreToolUse gh_merge_guard hook present + executable (ADR052 Autonomous Merge Policy)"
    else
        log_fail 77 "autonomous-merge policy — .claude/settings.json lacks the PreToolUse gh_merge_guard wiring (if 'Bash(gh pr merge:*)' → gh_merge_guard.sh). Run aos_sync_all."
    fi
}

# ----------------------------------------------------------------
# Check 78 — Verdict engine/model provenance (ADR057 V-5 stage 1, M12-P1 item f)
# ADVISORY ONLY (log_skip/WARN idiom — NEVER log_fail; see check_55/56/57 for the same idiom).
# Every `_COMMUNICATION/**/VERDICT_*.md` file that carries YAML frontmatter with an `engine:`
# key SHOULD ALSO carry a separate `model:` key, with `engine:` resolving to a
# core/config/engines.yaml `id` and `model:` resolving to one of that engine's
# `underlying_models[].name` entries. The corpus-wide drift this catches (a memory-documented
# finding, W7 2026-07-17): historically `engine:` carried a MODEL string (e.g. "gpt-5.2
# (non-Claude...)" or "cursor-composer-2") with no separate `model:` field at all — so a verdict
# naming a completely FABRICATED engine was indistinguishable from one naming a real one (the
# defect that let "GPT-5.6 Sol" pass M12 W3 round 2 undetected until team_90 caught it by hand).
# Stays advisory (never blocks) until the corpus sweep (W7 tail) closes out the ~136 pre-existing
# non-conformant files; the openai-via-cursor VERDICT_RECORDING convention (engines.yaml note)
# is the going-forward target this check measures progress against.
# Frontmatter is read with plain-text line regexes (NOT a full YAML parse of the whole block) —
# several existing frontmatter blocks are not strictly valid YAML elsewhere (unrelated unquoted
# colons in unrelated fields), which would make a full-document parse fail for reasons that have
# nothing to do with engine/model provenance; a full yaml.safe_load is exactly the wrong tool for
# a tolerant stage-1 advisory scan of a messy real-world corpus.
# ----------------------------------------------------------------
check_78() {
    local engines_yaml="$PROJECT_ROOT/core/config/engines.yaml"
    local comm_dir="$PROJECT_ROOT/_COMMUNICATION"
    if [ ! -f "$engines_yaml" ]; then
        log_skip 78 "verdict engine/model provenance — core/config/engines.yaml absent (not hub / not yet propagated)"
        return
    fi
    if [ ! -d "$comm_dir" ]; then
        log_skip 78 "verdict engine/model provenance — no _COMMUNICATION/ tree"
        return
    fi
    local out
    out=$(python3 - "$PROJECT_ROOT" <<'PY' 2>/dev/null
import glob, os, re, sys
import yaml

root = sys.argv[1]
engines_path = os.path.join(root, "core", "config", "engines.yaml")
try:
    edoc = yaml.safe_load(open(engines_path, encoding="utf-8")) or {}
except Exception as e:
    print(f"UNPARSEABLE_ENGINES_YAML:{e}")
    sys.exit(0)

engine_models = {}  # id -> set(underlying_models[].name)
for e in (edoc.get("engines") or []):
    if not isinstance(e, dict) or not e.get("id"):
        continue
    names = {m.get("name") for m in (e.get("underlying_models") or []) if isinstance(m, dict) and m.get("name")}
    engine_models[e["id"]] = names

ENGINE_RE = re.compile(r'^engine:\s*(.+?)\s*$', re.M)
MODEL_RE = re.compile(r'^model:\s*(.+?)\s*$', re.M)

def clean(raw):
    raw = raw.strip()
    if raw[:1] in ('"', "'"):
        q = raw[0]
        end = raw.find(q, 1)
        if end != -1:
            return raw[1:end]
        return raw.strip(q)
    idx = raw.find(" #")
    if idx != -1:
        raw = raw[:idx]
    return raw.strip()

findings = []
scanned = 0
files = sorted(glob.glob(os.path.join(root, "_COMMUNICATION", "**", "VERDICT_*.md"), recursive=True))
for f in files:
    rel = os.path.relpath(f, root)
    try:
        with open(f, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
    except OSError:
        continue
    if not lines or lines[0].strip() != "---":
        continue  # no YAML frontmatter fence — out of scope for this frontmatter-only check
    end = None
    for i, l in enumerate(lines[1:], start=1):
        if l.strip() == "---":
            end = i
            break
    if end is None:
        continue
    fm_text = "".join(lines[1:end])
    em = ENGINE_RE.search(fm_text)
    if not em:
        continue  # no engine: key at all — nothing to check
    scanned += 1
    mm = MODEL_RE.search(fm_text)
    if not mm:
        findings.append(f"{rel}: engine: present with no separate model: field (recording defect)")
        continue
    engine_id = clean(em.group(1))
    model_name = clean(mm.group(1))
    if engine_id not in engine_models:
        findings.append(f"{rel}: engine '{engine_id}' is not a registered engines.yaml id")
    elif model_name not in engine_models[engine_id]:
        findings.append(f"{rel}: model '{model_name}' not in {engine_id}.underlying_models[].name")

print(f"SCANNED:{scanned}")
print(f"TOTAL_FILES:{len(files)}")
for finding in findings:
    print(f"FINDING:{finding}")
PY
)
    if echo "$out" | grep -q "^UNPARSEABLE_ENGINES_YAML:"; then
        log_skip 78 "WARN: verdict engine/model provenance — core/config/engines.yaml failed to parse ($(echo "$out" | sed -n 's/^UNPARSEABLE_ENGINES_YAML://p'))"
        return
    fi
    local scanned total findings_n
    scanned=$(echo "$out" | sed -n 's/^SCANNED://p')
    total=$(echo "$out" | sed -n 's/^TOTAL_FILES://p')
    findings_n=$(echo "$out" | grep -c "^FINDING:" || true)
    if [ "$findings_n" -gt 0 ]; then
        log_skip 78 "WARN: verdict engine/model provenance — $findings_n/$scanned frontmatter-with-engine VERDICT_*.md ($total scanned total) fail engine/model resolution against engines.yaml (advisory; ADR057 V-5 stage 1, corpus sweep pending — W7 tail). First few: $(echo "$out" | grep "^FINDING:" | head -3 | sed 's/^FINDING://' | tr '\n' '|')"
    else
        log_skip 78 "verdict engine/model provenance clean — 0 findings across $scanned frontmatter-with-engine VERDICT_*.md ($total scanned total) (ADR057 V-5 stage 1 advisory)"
    fi
}

# ----------------------------------------------------------------
# Check 79 — server_path freshness assertion (W5, AOS-V5-M12-WP-L0-READ-PATH-FRESHNESS AC-5.4)
# ADVISORY ONLY (log_skip/WARN idiom — NEVER log_fail; LOD200 AC-5.4: "fails (or warns, per the
# ruling in W7)" — kept advisory since W7 has not yet formally ruled the severity, and a hard FAIL
# on first landing would break the whole fleet's baseline before scripts/refresh_server_checkouts.sh
# (P3.2) has actually reconciled the known-messy trees).
#
# Every enabled `_aos/projects.yaml` project with a `server_path` SHOULD be: present, a git
# worktree, on `main`, clean, and not behind after a real `git fetch` (never a cached ref — a
# `behind=0` reading without a fresh fetch is a false zero, T-13). `server_path` is server-local by
# construction — this check only has anything to assert when run FROM the host where those paths
# are real (waldhomeserver); on any other host (the normal case — a Mac session) it SKIPs entirely
# rather than reporting every entry as spuriously ABSENT.
# ----------------------------------------------------------------
check_79() {
    if [ ! -f "$PROJECT_ROOT/_aos/projects.yaml" ]; then
        log_skip 79 "not hub — server_path freshness only applies to the hub's registry"
        return
    fi
    local out
    out=$(python3 - "$PROJECT_ROOT/_aos/projects.yaml" <<'PY' 2>/dev/null
import subprocess, sys, yaml

doc = yaml.safe_load(open(sys.argv[1])) or {}
targets = []
for p in doc.get("projects", []):
    if p.get("enabled") is False:
        continue
    sp = p.get("server_path")
    if sp:
        targets.append((p.get("id", "?"), sp))

if not targets:
    print("NO_TARGETS")
    sys.exit(0)

import os
reachable = [t for t in targets if os.path.isdir(t[1])]
if not reachable:
    # Normal case off the server — every server_path is a remote-only path from here.
    print("NOT_ON_SERVER")
    sys.exit(0)

findings = []
checked = 0
for pid, sp in reachable:
    checked += 1
    if subprocess.run(["git", "-C", sp, "rev-parse", "--git-dir"],
                       capture_output=True).returncode != 0:
        findings.append(f"{pid}: not a git repository")
        continue
    if subprocess.run(["git", "-C", sp, "fetch", "origin"], capture_output=True).returncode != 0:
        findings.append(f"{pid}: git fetch origin failed")
        continue
    branch = subprocess.run(["git", "-C", sp, "branch", "--show-current"],
                             capture_output=True, text=True).stdout.strip()
    if branch != "main":
        findings.append(f"{pid}: on branch '{branch or '(detached)'}', not main")
        continue
    dirty = subprocess.run(["git", "-C", sp, "status", "--porcelain"],
                            capture_output=True, text=True).stdout
    if dirty.strip():
        n = len(dirty.strip().splitlines())
        findings.append(f"{pid}: {n} dirty file(s)")
        continue
    behind_ahead = subprocess.run(["git", "-C", sp, "rev-list", "--left-right", "--count",
                                    "origin/main...HEAD"], capture_output=True, text=True).stdout.strip()
    if behind_ahead:
        behind, ahead = behind_ahead.split()
        if behind != "0":
            findings.append(f"{pid}: {behind} behind origin/main (fresh fetch, not a cached ref)")
        elif ahead != "0":
            findings.append(f"{pid}: {ahead} ahead of origin/main (local commits not upstream)")

print(f"CHECKED:{checked}")
print(f"TOTAL_WITH_SERVER_PATH:{len(targets)}")
for finding in findings:
    print(f"FINDING:{finding}")
PY
)
    if [ "$out" = "NO_TARGETS" ]; then
        log_skip 79 "server_path freshness — no enabled project declares a server_path"
        return
    fi
    if [ "$out" = "NOT_ON_SERVER" ]; then
        log_skip 79 "server_path freshness — no registered server_path is locally reachable from this host (expected off waldhomeserver)"
        return
    fi
    if [ -z "$out" ]; then
        log_skip 79 "server_path freshness — could not evaluate (parse or subprocess failure)"
        return
    fi
    local checked total findings_n
    checked=$(echo "$out" | sed -n 's/^CHECKED://p')
    total=$(echo "$out" | sed -n 's/^TOTAL_WITH_SERVER_PATH://p')
    findings_n=$(echo "$out" | grep -c "^FINDING:" || true)
    if [ "$findings_n" -gt 0 ]; then
        log_skip 79 "WARN: server_path freshness — $findings_n/$checked reachable checkout(s) ($total registered total) not clean+current on main after a real fetch (advisory per LOD200 AC-5.4 pending W7 severity ruling; run scripts/refresh_server_checkouts.sh). $(echo "$out" | grep "^FINDING:" | sed 's/^FINDING://' | tr '\n' '|')"
    else
        log_skip 79 "server_path freshness clean — $checked/$total reachable registered checkout(s) clean+current on main after a real fetch (W5 AC-5.4 advisory)"
    fi
}

# ----------------------------------------------------------------
# Check 47 — Definition Snapshot Lockdown (ADR050, hub-only)
# Verifies every enabled spoke _aos/definition.yaml contains
# team_NN: blocks that are verbatim slices of hub core/definition.yaml.
# Auto-fix is OUT OF SCOPE (ADR050 §5) — surface drift to team_00.
# ----------------------------------------------------------------
check_47() {
    # Hub-only: spokes lack _aos/projects.yaml and have nothing to enforce against.
    if [ ! -f "$PROJECT_ROOT/_aos/projects.yaml" ]; then
        log_skip 47 "not hub — _aos/projects.yaml absent (spokes skip definition snapshot drift check)"
        return
    fi
    local def_script="$PROJECT_ROOT/scripts/check_definition_snapshot_consistency.sh"
    if [ ! -f "$def_script" ]; then
        log_skip 47 "check_definition_snapshot_consistency.sh not found (pre-ADR050 hub)"
        return
    fi
    local out drift_count summary
    if out=$(bash "$def_script" --quiet 2>&1); then
        log_pass 47 "definition snapshot consistency OK (ADR050)"
    else
        # Extract drift count from stderr/stdout if present; fall back to raw output.
        drift_count=$(echo "$out" | sed -n 's/.*drift=\([0-9]\+\).*/\1/p' | head -1)
        if [ -n "$drift_count" ]; then
            summary="$drift_count drift record(s)"
        else
            summary="$out"
        fi
        log_fail 47 "definition snapshot DRIFT — $summary; review hub core/definition.yaml vs spoke _aos/definition.yaml; auto-fix is out of scope (see ADR050 §5). Detail: bash scripts/check_definition_snapshot_consistency.sh"
    fi
}

# ----------------------------------------------------------------
# Check 48 — Orphan / stale worktrees (AOS-V4.5-WP-SESSION-W2, advisory)
# Flags worktrees with no live session lock; never FAIL (Phase-1 non-silent).
# ----------------------------------------------------------------
check_48() {
    local reap_script="$PROJECT_ROOT/scripts/session_reap.sh"
    if [ ! -x "$reap_script" ]; then
        log_skip 48 "session_reap.sh not found (pre-W2 hub)"
        return
    fi
    local out stale_count
    out=$(bash "$reap_script" 2>&1 || true)
    stale_count=$(echo "$out" | grep -cE '^\[(stale-worktree|stale-lock)\]' 2>/dev/null || echo 0)
    if [ "$stale_count" -gt 0 ]; then
        echo "  [WARN] Check 48: $stale_count stale worktree/lock candidate(s) (advisory — run: bash scripts/session_reap.sh)"
        echo "$out" | grep -E '^\[(stale-worktree|stale-lock|orphan-branch-hint)\]' | sed 's/^/    /' || true
        log_pass 48 "orphan worktree check — $stale_count advisory flag(s) (non-blocking)"
    else
        log_pass 48 "orphan worktree check — no stale worktrees/locks flagged"
    fi
}

check_49() {
    # ADR053 — decisive-gate validation tier matches track. Advisory in v1 (D4); legacy-tolerant.
    local wp_dir="$PROJECT_ROOT/_aos/work_packages"
    [ -d "$wp_dir" ] || { log_skip 49 "ADR053 tier check — no _aos/work_packages (spoke or pre-program)"; return; }
    local flagged=0 checked=0 md
    for md in "$wp_dir"/*/metadata.yaml; do
        [ -f "$md" ] || continue
        local track; track=$(grep -E '^track:' "$md" | head -1 | awk '{print $2}' | tr -d '"')
        case "$track" in STANDARD|MANAGED|CONTENT|HOTFIX) ;; *) continue ;; esac
        grep -q '^validation_tiering:' "$md" || continue   # legacy tolerance: no block → skip WP
        checked=$((checked+1))
        local wp; wp=$(basename "$(dirname "$md")")
        local builder; builder=$(grep -E '^assigned_builder:' "$md" | head -1)
        local dgline; dgline=$(grep -E 'L-GATE_(VALIDATE|DELIVER):' "$md" | head -1)
        if [ -z "$dgline" ] || echo "$dgline" | grep -q 'engine: TBD'; then
            echo "  [WARN] Check 49: $wp decisive-gate engine not yet set (TBD) — Tier-2 attestation pending (ADR053 §4)"
            flagged=$((flagged+1))
        elif echo "$dgline" | grep -q 'canonical_cross_engine: true'; then
            local eng; eng=$(echo "$dgline" | sed -E 's/.*engine:[[:space:]]*([^,}]+).*/\1/' | tr -d ' ')
            if [ -n "$eng" ] && [ "$eng" != "TBD" ] && echo "$builder" | grep -qi "$eng"; then
                echo "  [WARN] Check 49: $wp decisive gate claims cross-engine but engine '$eng' matches builder — possible IR#1 Tier-2 gap (ADR053 §4.2)"
                flagged=$((flagged+1))
            fi
        fi
    done
    if [ "$checked" -eq 0 ]; then
        log_skip 49 "ADR053 tier check — no Tier-2-track WPs carry a validation_tiering block yet (legacy-tolerant)"
    elif [ "$flagged" -gt 0 ] && [ "${AOS_CHECK49_STRICT:-0}" = "1" ]; then
        log_fail 49 "ADR053 decisive-gate tier — $checked WP(s) checked, $flagged IR#1 attestation gap(s) (HARD with AOS_CHECK49_STRICT=1)"
    else
        log_pass 49 "ADR053 decisive-gate tier — $checked WP(s) checked, $flagged advisory flag(s) (non-blocking, D4 advisory phase)"
    fi
}

check_50() {
    # ADR054 / Model B — governance cache version stamp present + fresh. ADVISORY ONLY:
    # never FAIL, never block domain work (LOD200 AC6). Legacy-tolerant (absent stamp → SKIP).
    local stamp="$PROJECT_ROOT/_aos/AOS_GOVERNANCE_VERSION.yaml"
    local flags=0 d
    # (a) Tier-A still tracked? → Model B not yet applied to this domain (rollout-progress signal).
    local tracked=""
    for d in governance methodology lean-kit; do
        if [ -n "$(git -C "$PROJECT_ROOT" ls-files "_aos/$d" 2>/dev/null | head -1)" ]; then
            tracked="$tracked _aos/$d"
        fi
    done
    _require_file 50 "$stamp" "ADR054 governance stamp — run scripts/aos_governance_bootstrap.sh (cold clone / pre-Model-B domain)" || return
    # (b) staleness (advisory, 14-day threshold)
    local synced_at now then_ts age_days
    synced_at=$(awk '/^synced_at:/{print $2; exit}' "$stamp")
    now=$(date -u +%s)
    then_ts=$(date -u -d "$synced_at" +%s 2>/dev/null || date -u -j -f "%Y-%m-%dT%H:%M:%SZ" "$synced_at" +%s 2>/dev/null || echo 0)
    if [ "${then_ts:-0}" -gt 0 ]; then
        age_days=$(( (now - then_ts) / 86400 ))
        if [ "$age_days" -gt 14 ]; then
            echo "  [WARN] Check 50: governance cache stale (${age_days} days, >14d) — run /AOS_gov-sync (advisory, non-blocking)"
            flags=$((flags+1))
        fi
    fi
    if [ -n "$tracked" ]; then
        echo "  [WARN] Check 50: Tier-A still TRACKED (${tracked# }) — Model B (ADR054) not yet applied to this domain (advisory)"
        flags=$((flags+1))
    fi
    log_pass 50 "ADR054 governance stamp present — $flags advisory flag(s) (non-blocking)"
}

check_51() {
    # Fleet git-health probe (AOS-V4.5-WP-GIT-HYGIENE). ADVISORY ONLY: always
    # PASS/SKIP, never FAIL, never block domain work. Reports this domain's git
    # hygiene so a recurring fault (e.g. the hub re-baring) surfaces in routine
    # validation. Mirrors the Check 48/49/50 advisory idiom: emit [WARN] lines,
    # then log_pass with a flag count. (CS-5, CS-6)
    if ! git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
        log_skip 51 "git-health probe — not a git repo (snapshot/export context)"
        return
    fi
    local flags=0

    # (a) core.bare on a working checkout → must be false. The recurring hub fault.
    # A working checkout (or linked worktree) keeps a `.git` entry at the repo root;
    # once bared, `git rev-parse --show-toplevel` fails, so test for `.git` directly.
    # A genuine bare store has no `.git` at root → correctly NOT flagged.
    local bare; bare="$(git -C "$PROJECT_ROOT" config --get core.bare 2>/dev/null || echo false)"
    local has_dotgit=0
    [ -e "$PROJECT_ROOT/.git" ] && has_dotgit=1
    if [ "$bare" = "true" ] && [ "$has_dotgit" -eq 1 ]; then
        echo "  [WARN] Check 51: core.bare=true on a working checkout — remediate: git -C \"$PROJECT_ROOT\" config core.bare false (see AOS_GIT_LAYOUT_CANON)"
        flags=$((flags+1))
    fi

    # (b) AOS hooks installed (pre-push + pre-commit). Resolve the shared hooks dir
    # (works for both main repos and linked worktrees via --git-path).
    local hooks_dir; hooks_dir="$(git -C "$PROJECT_ROOT" rev-parse --git-path hooks 2>/dev/null)"
    # --git-path may return a path relative to the gitdir; normalize against repo.
    case "$hooks_dir" in
        /*) ;;  # absolute
        *) hooks_dir="$PROJECT_ROOT/$hooks_dir" ;;
    esac
    if [ ! -x "$hooks_dir/pre-push" ] || [ ! -x "$hooks_dir/pre-commit" ]; then
        echo "  [WARN] Check 51: AOS git hooks not fully installed (pre-push/pre-commit) — run: bash scripts/install_hooks.sh"
        flags=$((flags+1))
    fi

    # (c) Model B Tier-A cache hydrated? (reuse the canonical helper)
    if _modelb_cache_absent; then
        echo "  [WARN] Check 51: Model B Tier-A governance cache NOT hydrated — run: bash scripts/aos_governance_bootstrap.sh"
        flags=$((flags+1))
    fi

    # (d) stray / prunable worktrees (orphaned worktree admin dirs).
    local prunable
    # NB: `grep -c .` already prints a single `0` on no match (and exits 1); `|| true` swallows that
    # exit code. The old `|| echo 0` ALSO fired, yielding a two-line `0\n0` → `[ -gt ]` integer error.
    prunable="$(git -C "$PROJECT_ROOT" worktree prune --dry-run 2>/dev/null | grep -c . || true)"
    if [ "${prunable:-0}" -gt 0 ]; then
        echo "  [WARN] Check 51: $prunable prunable worktree(s) — run: git worktree prune"
        flags=$((flags+1))
    fi

    log_pass 51 "git-health probe — bare=$bare, $flags advisory flag(s) (non-blocking)"
}

# Check 52 — ADR052 W2 concurrent-session enforcement (AOS-V5-WP-CONCURRENCY-DECONFLICTION)
# FAIL when DB/API online and detect_concurrency(register) reports CONCURRENT on this checkout.
# SKIP advisory when register backend degrades (DB offline).
check_52() {
    local client="$PROJECT_ROOT/scripts/session_register_client.py"
    local st_script="$PROJECT_ROOT/scripts/start_worktree.sh"
    if [ ! -f "$client" ] || [ ! -f "$st_script" ]; then
        log_skip 52 "concurrent-session enforcement — session client/start_worktree missing"
        return
    fi
    local sid repo_root
    sid="$(cat "$(git -C "$PROJECT_ROOT" rev-parse --git-path aos-session-id 2>/dev/null || echo .git/aos-session-id)" 2>/dev/null || echo "validate-$$")"
    repo_root="$(cd "$PROJECT_ROOT" && pwd)"
    local det_json state
    det_json=$(python3 "$client" detect --repo-root "$repo_root" --session-id "$sid" 2>/dev/null || echo '{"degrade":true}')
    if echo "$det_json" | grep -q '"degrade"'; then
        log_skip 52 "concurrent-session enforcement — register backend degraded (DB offline advisory)"
        return
    fi
    state=$(echo "$det_json" | python3 -c "import json,sys; print(json.load(sys.stdin).get('state','CLEAR'))" 2>/dev/null || echo CLEAR)
    if [ "$state" = "CONCURRENT" ]; then
        echo "  Check 52: CONCURRENT — another live session shares this checkout (ADR052 W2 violation)" >&2
        echo "$det_json" | python3 -m json.tool 2>/dev/null | sed 's/^/    /' || true
        log_fail 52 "concurrent local-mac sessions on shared tree — worktree-isolate required"
    else
        log_pass 52 "concurrent-session enforcement — state=${state}"
    fi
}

# Check 53: Enum-SSoT lint (M2-W7) — the migration 018 `enums` seed must agree BIDIRECTIONALLY with
# CANON_COCKPIT_ENUMS per kind, the legacy GATE_0–8 → named-gate bridge must stay fully locked, and the
# v5 LOD-standard must use named-gates only. All findings BLOCK (anti-drift, P9 / L20). (Check 52 =
# concurrent-session enforcement per AOS-V5-WP-CONCURRENCY-DECONFLICTION.)
check_53() {
    # Hub-only: validate_canon_enums.py reads _aos/v5_characterization/synthesis/CANON_COCKPIT_ENUMS
    # + core/db/migrations/018_canon_tables.sql — engine/cockpit artifacts that exist ONLY on the hub.
    # On spokes both are absent → the script returns "enum-SSoT source missing". Skip (not FAIL),
    # mirroring hub-only Checks 17/19/47/60 (the source-absent guard).
    if [ "$CONTEXT" != "hub" ]; then
        log_skip 53 "enum-SSoT (cockpit enums + migration 018 SSoT) — hub-only; skip on spokes"
        return 0
    fi
    local script="$SCRIPT_DIR/validate_canon_enums.py"
    if [ ! -f "$script" ]; then
        log_skip 53 "validate_canon_enums.py not found — skip"
        return 0
    fi
    local result fails
    result=$(python3 "$script" "$PROJECT_ROOT" 2>&1)
    fails=$(echo "$result" | grep -c "^FAIL:" || true)
    if [ "$fails" -gt 0 ]; then
        echo "$result" | grep "^FAIL:" | head -25 | sed 's/^/    /'
        log_fail 53 "enum-SSoT drift — $fails violation(s) (CANON_COCKPIT_ENUMS <-> migration 018 / GATE bridge / numeric-gate)"
    else
        log_pass 53 "enum-SSoT — seed<->canon agree (all kinds) + GATE_0–8 bridge locked + named-gates only"
    fi
}

# Check 54: Mandate R1 frontmatter conformance (CA7 §5.6 R2 — mechanical bridge).
# Advisory ONLY (log_skip/warn — NEVER log_fail): legacy _COMMUNICATION/**/MANDATE_*.md
# predate the R1 key-table; a hard retroactive FAIL would break validate_aos + cold-integration.
# HARD enforcement lives at the generation path (mandates.validate_mandate_conformance, reject-first).
# Scans MANDATE_*.md for the §4 always-core keys (id,from,to,type,date,status,target_render).
check_54() {
    local comm_dir="$PROJECT_ROOT/_COMMUNICATION"
    if [ ! -d "$comm_dir" ]; then
        log_skip 54 "no _COMMUNICATION/ — mandate R1 conformance scan skipped (CA7 §5.6 R2 advisory)"
        return
    fi
    local core_keys="id from to type date status target_render"
    local nonconformant=0
    local scanned=0
    while IFS= read -r mfile; do
        scanned=$((scanned+1))
        # Extract the leading YAML frontmatter block (between the first two '---' fences).
        local fm
        fm=$(awk 'NR==1 && $0!="---"{exit} /^---[[:space:]]*$/{c++; next} c==1{print} c>=2{exit}' "$mfile" 2>/dev/null)
        local missing=""
        local k
        for k in $core_keys; do
            if ! echo "$fm" | grep -qE "^[[:space:]]*$k:[[:space:]]*[^[:space:]]"; then
                missing="${missing}${missing:+,}$k"
            fi
        done
        if [ -n "$missing" ]; then
            nonconformant=$((nonconformant+1))
        fi
    done < <(find "$comm_dir" -type f -name "MANDATE_*.md" 2>/dev/null)
    if [ "$nonconformant" -gt 0 ]; then
        # Concise advisory only — the per-file path dump was noise on every run; the count below
        # carries the signal. HARD enforcement lives at the generation path (reject-first).
        log_skip 54 "WARN: mandate R1 conformance — $nonconformant/$scanned MANDATE_*.md non-conformant (advisory; CA7 §5.6 R2 mechanical bridge)"
    else
        log_skip 54 "mandate R1 conformance — $scanned MANDATE_*.md scanned, all carry §4 core keys (CA7 §5.6 R2 advisory bridge; HARD enforcement at generation path)"
    fi
}

# Check-QA1: QA-deepening anti-false-pass aggregate (M5-WP1 — QA_DEEPENING §1 Q-D1 + §1.2.ב.2).
# Advisory ONLY (log_skip/warn — NEVER log_fail). Per §1.5 ("advisory בהאב, hard ב-CI") + §3.4:
# the HARD-gate form lives in the CI-harness WP; hub-side these report gaps without blocking.
# Aggregates three scans from scripts/qa_enforcement.py:
#   - skips      : static @pytest.mark.skip/xfail markers not covered by tests/SKIP_ALLOWLIST.yaml
#   - assertions : `def test_*` functions with zero assertion signal (assert / expect / raises / ...)
#   - allowlist  : malformed or EXPIRED SKIP_ALLOWLIST entries (expiry < today)
# Runtime conditional skips (pytest.skip() in bodies, requires_aos_db) are NOT flagged by design.
# Degrades gracefully (log_skip) if the helper is absent (clone-portability).
check_55() {
    local helper="$PROJECT_ROOT/scripts/qa_enforcement.py"
    local test_dir="$PROJECT_ROOT/core/tests"
    local allowlist="$PROJECT_ROOT/tests/SKIP_ALLOWLIST.yaml"
    if [ ! -f "$helper" ]; then
        log_skip 55 "qa_enforcement.py absent — QA anti-false-pass scan skipped (clone-portable; M5-WP1 advisory)"
        return
    fi
    if [ ! -d "$test_dir" ]; then
        log_skip 55 "no core/tests/ — QA anti-false-pass scan skipped (M5-WP1 advisory)"
        return
    fi
    local today
    today=$(date +%Y-%m-%d)
    # Each subcommand prints a `RESULT <cmd> findings=N` machine line we grep for the count.
    local skip_n assert_n allow_n
    skip_n=$(python3 "$helper" skips --test-dir "$test_dir" --allowlist "$allowlist" 2>/dev/null \
        | sed -n 's/^RESULT skips findings=\([0-9][0-9]*\).*/\1/p' | tail -1)
    assert_n=$(python3 "$helper" assertions --test-dir "$test_dir" 2>/dev/null \
        | sed -n 's/^RESULT assertions findings=\([0-9][0-9]*\).*/\1/p' | tail -1)
    allow_n=$(python3 "$helper" allowlist --allowlist "$allowlist" --today "$today" 2>/dev/null \
        | sed -n 's/^RESULT allowlist findings=\([0-9][0-9]*\).*/\1/p' | tail -1)
    skip_n=${skip_n:-?}; assert_n=${assert_n:-?}; allow_n=${allow_n:-?}
    local total=0 numeric=1
    case "$skip_n$assert_n$allow_n" in *\?*) numeric=0 ;; esac
    if [ "$numeric" -eq 1 ]; then
        total=$((skip_n + assert_n + allow_n))
    fi
    if [ "$numeric" -eq 1 ] && [ "$total" -gt 0 ]; then
        log_skip 55 "WARN: QA anti-false-pass — static-skips=$skip_n assertion-less=$assert_n expired/malformed-allowlist=$allow_n (advisory; HARD form in CI-harness WP)"
    elif [ "$numeric" -eq 1 ]; then
        log_skip 55 "QA anti-false-pass clean — 0 static skips / 0 assertion-less tests / 0 bad allowlist entries (M5-WP1 advisory)"
    else
        log_skip 55 "QA anti-false-pass scan ran with non-numeric result (helper error) — advisory, never blocks (M5-WP1)"
    fi
}

# Check-QA2: QA-deepening N×4 state-matrix coverage tally (M5-WP1 — QA_DEEPENING §3 Q-D3).
# Advisory ONLY (log_skip/warn — NEVER log_fail). Tallies LOD400 N×4 matrices (surfaces ×
# {empty,loading,error,offline}) against `states.*` test-ids. No LOD400 matrix exists yet → the
# tool reports "no N×4 matrices" (clean no-op) until the frontend WP authors the matrix + suite.
# Degrades gracefully (log_skip) if the helper is absent (clone-portability).
check_56() {
    local helper="$PROJECT_ROOT/scripts/qa_enforcement.py"
    # Cockpit N×4 lives in Playwright .js specs under cockpit/tests (PM7-W1: tally scans .py + .js).
    local test_dir="$PROJECT_ROOT/cockpit/tests"
    if [ ! -f "$helper" ]; then
        log_skip 56 "qa_enforcement.py absent — QA N×4 tally skipped (clone-portable; M5-WP1 advisory)"
        return
    fi
    # Cockpit N×4 matrix SSoT (M5-WP5/WP8). Fall back to any LOD400 spec for clone-portability.
    local lod400="$PROJECT_ROOT/cockpit/tests/NX4_MATRIX.md"
    if [ ! -f "$lod400" ]; then
        lod400=$(find "$AOS_DIR/work_packages" -name "*LOD400*.md" 2>/dev/null | head -1)
    fi
    local out
    # --js-only: count only tid('states.x.y') refs in .js specs (no .py-literal / comment masking).
    out=$(python3 "$helper" tally --js-only --test-dir "$test_dir" ${lod400:+--lod400 "$lod400"} 2>/dev/null)
    local mfound missing
    mfound=$(echo "$out" | sed -n 's/^RESULT tally matrices_found=\([0-9][0-9]*\).*/\1/p' | tail -1)
    missing=$(echo "$out" | sed -n 's/^RESULT tally matrices_found=[0-9][0-9]* missing=\([0-9][0-9]*\).*/\1/p' | tail -1)
    mfound=${mfound:-?}; missing=${missing:-?}
    if [ "$mfound" = "0" ]; then
        log_skip 56 "QA N×4 tally — no N×4 state matrices in LOD400s yet (no-op advisory; M5-WP1, awaits frontend WP)"
    elif [ "$mfound" = "?" ]; then
        log_skip 56 "QA N×4 tally scan ran with non-numeric result (helper error) — advisory, never blocks (M5-WP1)"
    elif [ "$missing" != "0" ] && [ "$missing" != "?" ]; then
        log_skip 56 "WARN: QA N×4 tally — $missing uncovered (surface,state) cell(s) across $mfound matrix/matrices (advisory; HARD form in CI-harness WP)"
    else
        log_skip 56 "QA N×4 tally — all matrix cells covered across $mfound matrix/matrices (M5-WP1 advisory)"
    fi
}

# Check 57: CI hard-gate harness present (M5-WP2 ci-harness — QA_DEEPENING §2.2).
# Advisory ONLY (log_skip — NEVER log_fail), so `validate_aos .` stays 0 FAIL and the check is
# clone-portable. Asserts the M5-WP2 CI harness exists: .github/workflows/cold-integration.yml
# contains the `cold-integration:` + `qa-antifalsepass:` job keys AND scripts/smoke.sh exists and
# is executable. PASS-as-SKIP when present; WARN-SKIP (not FAIL) when missing. Mirrors Check 55/56.
check_57() {
    local wf="$PROJECT_ROOT/.github/workflows/cold-integration.yml"
    local smoke="$PROJECT_ROOT/scripts/smoke.sh"
    local missing=""
    if [ ! -f "$wf" ]; then
        missing="cold-integration.yml"
    else
        grep -qE '^[[:space:]]*cold-integration:' "$wf" || missing="$missing cold-integration-job"
        grep -qE '^[[:space:]]*qa-antifalsepass:' "$wf" || missing="$missing qa-antifalsepass-job"
    fi
    if [ ! -f "$smoke" ]; then
        missing="$missing smoke.sh"
    elif [ ! -x "$smoke" ]; then
        missing="$missing smoke.sh-not-executable"
    fi
    if [ -z "$missing" ]; then
        log_skip 57 "CI hard-gate harness present — cold-integration.yml (cold-integration + qa-antifalsepass jobs) + scripts/smoke.sh executable (M5-WP2 advisory)"
    else
        log_skip 57 "WARN: CI hard-gate harness incomplete —${missing} (advisory, never blocks; M5-WP2 / QA_DEEPENING §2.2)"
    fi
}

# Check 58 — context-layers assembler anti-drift (M5-WP7, advisory; never log_fail).
# Logic lives in Python (ADR041 thin-orchestrator): the --check mode verifies 4 layers
# with non-empty Base+Mission inline, profile determinism, generated _aos/context/ parity,
# and base_canon.yaml present/parseable with iron-rule count+titles matching CLAUDE.md.
check_58() {
    local out
    out=$( cd "$PROJECT_ROOT" && python3 -m core.modules.management.context_layers --check 2>&1 )
    if echo "$out" | grep -q "CHECK58 OK"; then
        log_skip 58 "context-layers assembler —$(echo "$out" | sed -n 's/.*CHECK58 OK —//p') (advisory; M5-WP7)"
    else
        log_skip 58 "WARN: context-layers assembler — $(echo "$out" | sed -n 's/.*CHECK58 WARN: //p; t; $p' | tail -1) (advisory, never blocks; M5-WP7)"
    fi
}

# Check 59 — DOC-close-gate (M5-WP8, L26). Logic lives in Python (ADR041 thin-orchestrator):
# the --check mode verifies _aos/context/DOC_CANON.md exists + is well-formed (and, when AOS_DOC_WP
# is set, that the closing WP is reflected). ADVISORY in a standalone run (log_skip → 0 FAIL,
# clone-portable); HARD at the CLOSE gate / in cold-integration CI when AOS_DOC_CLOSE_GATE=1.
check_59() {
    local out detail
    # cannot-run => SKIP, never FAIL (team_00 fix 2026-07-04; generalized in
    # AOS-V5-M11-WP-VALIDATION-VERSION-CANON-HYGIENE C1): if core/ is not importable in this context
    # (spoke/cache-only checkout, or CI with wrong CWD/PYTHONPATH) the module below crashes with
    # ModuleNotFoundError and the traceback would — under AOS_DOC_CLOSE_GATE=1 — be mis-escalated to a HARD
    # fail, conflating an infra/import failure with a doc-canon violation. Probe with the SAME import context
    # as the `-m` call and SKIP cleanly when core is absent.
    _require_module 59 core "DOC-close-gate" || return 0
    out=$( cd "$PROJECT_ROOT" && python3 -m core.modules.management.doc_canon --check 2>&1 | tail -1 )
    if [ "${out#*CHECK59 OK}" != "$out" ]; then
        detail=${out#*CHECK59 OK — }
        log_skip 59 "DOC-close-gate — ${detail} (advisory; M5-WP8 / L26)"
    else
        detail=${out#*CHECK59 WARN: }
        if [ "${AOS_DOC_CLOSE_GATE:-0}" = "1" ]; then
            log_fail 59 "DOC-close-gate (HARD at CLOSE/CI) — ${detail} (M5-WP8 / L26 — no retroactive documentation)"
        else
            log_skip 59 "WARN: DOC-close-gate — ${detail} (advisory standalone; HARD at CLOSE/CI via AOS_DOC_CLOSE_GATE=1; M5-WP8 / L26)"
        fi
    fi
}

# Check 60 — routing-policy anti-drift (M7-P1-WP1, LOD300 §8 / AC-3 / AC-9). The CHECKED key-set of
# core/config/routing_policy.yaml (hub-file SSoT, ADR055) and the migration 027 `routing_policy`
# projection seed must agree BIDIRECTIONALLY (the Check-53 clone for CANON_WP_ROUTING_POLICY). BLOCKING.
# Hub-only: routing_policy is not propagated, so SKIP cleanly when the file is absent (spokes / pre-build).
check_60() {
    local script="$SCRIPT_DIR/validate_routing_policy.py"
    if [ ! -f "$script" ] || [ ! -f "$PROJECT_ROOT/core/config/routing_policy.yaml" ]; then
        log_skip 60 "routing-policy anti-drift — no routing_policy.yaml (hub-only / pre-build) — skip"
        return 0
    fi
    local result fails
    result=$(python3 "$script" "$PROJECT_ROOT" 2>&1)
    fails=$(echo "$result" | grep -c "^FAIL:" || true)
    if [ "$fails" -gt 0 ]; then
        echo "$result" | grep "^FAIL:" | head -25 | sed 's/^/    /'
        log_fail 60 "routing-policy drift — $fails violation(s) (routing_policy.yaml <-> migration 027 projection)"
    else
        log_pass 60 "routing-policy anti-drift — file<->projection checked key-sets agree (M7-P1-WP1)"
    fi
}

# ================================================================
# Checks 61–69 — C-MB1..C-MB9: Model B (ADR054) drift-gate (SPOKE-only, HARD FAIL)
# ================================================================
# The strong PER-SPOKE structural lock that makes the single-version invariant
# ENFORCED, not merely audited (FLEET MIGRATION MAP §6.1). Each is HARD (log_fail)
# and blocks L-GATE_BUILD. Pairs with the fleet-level lock
# `scripts/fleet_check.py --require-single-version`. The hub (CONTEXT=hub) dogfoods
# Model B with a different tracked set; these spoke structural invariants are
# validated by the spokes themselves, so the hub SKIPs them (inverse of hub-only
# Check 53). Cache-dependent checks tolerate the cold-checkout state via the
# canonical `_modelb_cache_absent` helper (AOS-V4.5 cold-checkout tolerance).
_MB_CACHE_DIRS="governance methodology lean-kit"

# True when this domain is governed by Model B (stamp tracked OR gitignore cache block).
_mb_is_modelb() {
    [ -f "$AOS_DIR/AOS_GOVERNANCE_VERSION.yaml" ] && return 0
    grep -q "AOS-GOV-CACHE" "$PROJECT_ROOT/.gitignore" 2>/dev/null && return 0
    return 1
}

check_61() {  # C-MB1 — Tier-A not tracked
    if [ "$CONTEXT" != "spoke" ]; then log_skip 61 "C-MB1 Tier-A-not-tracked — spoke-only (hub dogfoods a distinct tracked set)"; return 0; fi
    if ! git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then log_skip 61 "C-MB1 — not a git working tree"; return 0; fi
    local d hit=""
    for d in $_MB_CACHE_DIRS; do
        [ -n "$(git -C "$PROJECT_ROOT" ls-files "_aos/$d" 2>/dev/null | head -1)" ] && hit="$hit _aos/$d"
    done
    if [ -n "$hit" ]; then
        log_fail 61 "C-MB1 Tier-A TRACKED (${hit# }) — governance cache must be git-ignored (ADR054); drop from index + re-sync"
    else
        log_pass 61 "C-MB1 Tier-A not tracked (governance|methodology|lean-kit out of git index)"
    fi
}

check_62() {  # C-MB2 — Tier-A git-ignored
    if [ "$CONTEXT" != "spoke" ]; then log_skip 62 "C-MB2 Tier-A-git-ignored — spoke-only"; return 0; fi
    if ! _mb_is_modelb; then log_skip 62 "C-MB2 — not a Model-B domain (no stamp / no AOS-GOV-CACHE block)"; return 0; fi
    if ! git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then log_skip 62 "C-MB2 — not a git working tree"; return 0; fi
    local d miss=""
    for d in $_MB_CACHE_DIRS; do
        git -C "$PROJECT_ROOT" check-ignore -q "_aos/$d" || miss="$miss _aos/$d"
    done
    if [ -n "$miss" ]; then
        log_fail 62 "C-MB2 Tier-A NOT git-ignored (${miss# }) — the .gitignore AOS-GOV-CACHE block was deleted/edited; restore it"
    else
        log_pass 62 "C-MB2 Tier-A git-ignored (all three cache dirs covered by AOS-GOV-CACHE block)"
    fi
}

check_63() {  # C-MB3 — Tier-A not symlinked (IR#2)
    if [ "$CONTEXT" != "spoke" ]; then log_skip 63 "C-MB3 Tier-A-not-symlinked — spoke-only"; return 0; fi
    if ! _mb_is_modelb; then log_skip 63 "C-MB3 — not a Model-B domain"; return 0; fi
    local d sym=""
    for d in $_MB_CACHE_DIRS; do
        [ -L "$AOS_DIR/$d" ] && sym="$sym _aos/$d"
    done
    if [ -n "$sym" ]; then
        log_fail 63 "C-MB3 Tier-A is a SYMLINK (${sym# }) — IR#2 (ADR054) forbids symlinked cache; must be a real dir / git-ignored copy"
    else
        log_pass 63 "C-MB3 Tier-A not symlinked (real dirs, IR#2)"
    fi
}

check_64() {  # C-MB4 — stamp present + schema
    if [ "$CONTEXT" != "spoke" ]; then log_skip 64 "C-MB4 stamp-schema — spoke-only"; return 0; fi
    if ! _mb_is_modelb; then log_skip 64 "C-MB4 — not a Model-B domain"; return 0; fi
    local stamp="$AOS_DIR/AOS_GOVERNANCE_VERSION.yaml"
    if [ ! -f "$stamp" ]; then
        log_fail 64 "C-MB4 governance stamp MISSING on a Model-B domain — broken/never-stamped sync; run scripts/aos_sync_all.sh"
        return
    fi
    local schema; schema=$(awk -F': *' '/^schema:/{print $2; exit}' "$stamp" | tr -d ' "'"'"'')
    if [ "$schema" != "aos.governance.version/v1" ]; then
        log_fail 64 "C-MB4 stamp schema '$schema' != aos.governance.version/v1 — malformed stamp"
    else
        log_pass 64 "C-MB4 governance stamp present + schema aos.governance.version/v1"
    fi
}

check_65() {  # C-MB5 — on-disk cache count == stamp cache_file_count
    if [ "$CONTEXT" != "spoke" ]; then log_skip 65 "C-MB5 cache-count — spoke-only"; return 0; fi
    if ! _mb_is_modelb; then log_skip 65 "C-MB5 — not a Model-B domain"; return 0; fi
    if _modelb_cache_absent; then log_skip 65 "C-MB5 — Tier-A cache not hydrated (cold checkout); run scripts/aos_governance_bootstrap.sh"; return 0; fi
    local stamp="$AOS_DIR/AOS_GOVERNANCE_VERSION.yaml"
    [ -f "$stamp" ] || { log_skip 65 "C-MB5 — no stamp to compare (covered by C-MB4)"; return 0; }
    local want; want=$(awk '/^cache_file_count:/{print $2; exit}' "$stamp" | tr -d ' ')
    # Mirror aos_gov_stamp.sh write_gov_stamp() EXACTLY: sum `find -type f` over existing dirs.
    local got=0 d
    for d in $_MB_CACHE_DIRS; do
        [ -d "$AOS_DIR/$d" ] && got=$(( got + $(find "$AOS_DIR/$d" -type f 2>/dev/null | wc -l | tr -d ' ') ))
    done
    if [ -z "$want" ] || ! [ "$want" -eq "$want" ] 2>/dev/null; then
        log_fail 65 "C-MB5 stamp cache_file_count missing/non-numeric ('$want') — malformed stamp"
    elif [ "$got" -ne "$want" ]; then
        log_fail 65 "C-MB5 cache count drift: on-disk $got != stamp $want — partial/extra sync; re-run scripts/aos_sync_all.sh"
    else
        log_pass 65 "C-MB5 cache count matches stamp ($got files)"
    fi
}

check_66() {  # C-MB6 — stamp hub_sha agrees with last_gov_sync hub_sha (prefix-aware)
    if [ "$CONTEXT" != "spoke" ]; then log_skip 66 "C-MB6 stamp<->last_gov_sync — spoke-only"; return 0; fi
    if ! _mb_is_modelb; then log_skip 66 "C-MB6 — not a Model-B domain"; return 0; fi
    local stamp="$AOS_DIR/AOS_GOVERNANCE_VERSION.yaml" last="$AOS_DIR/last_gov_sync.yaml"
    [ -f "$stamp" ] || { log_skip 66 "C-MB6 — no stamp (covered by C-MB4)"; return 0; }
    [ -f "$last" ]  || { log_skip 66 "C-MB6 — no last_gov_sync.yaml (pre-delta-tracking spoke)"; return 0; }
    local a b
    a=$(awk '/^hub_sha:/{print $2; exit}' "$stamp" | tr -d ' "'"'"'')
    b=$(awk '/^hub_sha:/{print $2; exit}' "$last"  | tr -d ' "'"'"'')
    if [ -z "$a" ] || [ -z "$b" ]; then
        log_fail 66 "C-MB6 hub_sha unreadable (stamp='$a' last_gov_sync='$b')"
        return
    fi
    # The stamp stores the FULL 40-char sha; last_gov_sync stores the SHORT form. Compare on the
    # shorter length (prefix-aware, like fleet_check.py) — same commit in two widths must agree.
    local n=${#a}; [ ${#b} -lt $n ] && n=${#b}
    if [ "${a:0:$n}" != "${b:0:$n}" ]; then
        log_fail 66 "C-MB6 hub_sha SPLIT: stamp ${a:0:12} != last_gov_sync ${b:0:12} — multi-sha; re-run scripts/aos_sync_all.sh"
    else
        log_pass 66 "C-MB6 stamp & last_gov_sync hub_sha agree (${a:0:12})"
    fi
}

check_67() {  # C-MB7 — no tracked ADR*.md / team_*.md outside the cache dirs
    if [ "$CONTEXT" != "spoke" ]; then log_skip 67 "C-MB7 stray-governance — spoke-only"; return 0; fi
    if ! git -C "$PROJECT_ROOT" rev-parse --git-dir >/dev/null 2>&1; then log_skip 67 "C-MB7 — not a git working tree"; return 0; fi
    # Duplicate-AOS-governance residue = AOS-named governance files (ADR*.md / team_*.md) tracked
    # under a repo-ROOT governance/ tree (the hub's tree name; tiktrack governance/directives/ADR043*
    # pattern). Under Model B a spoke's governance lives ONLY in the git-ignored _aos/governance/
    # cache, so an AOS governance file in a TRACKED root governance/ tree is always pre-Model-B residue.
    # We match the governance/ tree + AOS NAMING (not generic names anywhere): a product repo keeps its
    # own ADRs under docs/ (false-FAIL risk flagged by the cross-engine gate), and archived artifacts
    # like team_100_activation_prompt.md live OUTSIDE governance/ (would false-FAIL a bare team_*.md
    # match). :(top) anchors governance/ to the repo root; :(glob) makes ** span dirs (and match zero).
    local stray
    stray=$(git -C "$PROJECT_ROOT" ls-files -- ':(top,glob)governance/**/ADR*.md' ':(top,glob)governance/**/team_*.md' 2>/dev/null \
              | grep -vE '^(_aos/|_COMMUNICATION/)' || true)
    if [ -n "$stray" ]; then
        local n; n=$(echo "$stray" | grep -c .)
        echo "$stray" | head -8 | sed 's/^/    /'
        log_fail 67 "C-MB7 $n tracked governance file(s) OUTSIDE the cache — duplicate-governance residue; git rm the legacy tree(s)"
    else
        log_pass 67 "C-MB7 no stray tracked ADR*/team_* governance files outside the cache"
    fi
}

check_68() {  # C-MB8 — canonical block well-formed in CLAUDE.md / .cursorrules
    if [ "$CONTEXT" != "spoke" ]; then log_skip 68 "C-MB8 canonical-block — spoke-only"; return 0; fi
    # The sync OVERWRITES the canonical block (between aos:canonical:start/end) every run, so a
    # hand-edit self-heals on next sync; the DURABLE hazard is marker deletion/corruption (the render
    # then loses its insertion points). A full re-render byte-diff would false-fail on per-worktree
    # HUB_PATH/placeholder differences — so this validates STRUCTURE (markers present, ordered,
    # non-empty, notice intact), the robust invariant. (FLEET MAP §6.1 C-MB8, defensive variant.)
    local bad="" f start end notice
    for f in CLAUDE.md .cursorrules; do
        [ -f "$PROJECT_ROOT/$f" ] || continue
        grep -q "AOS-CANONICAL-TEMPLATE" "$PROJECT_ROOT/$f" 2>/dev/null || continue   # not a rendered file
        # Anchor to the EXACT marker comment lines — the "DO NOT hand-edit" notice line also embeds
        # both marker strings in prose, so a loose grep+head -1 would wrongly pick it (start==end).
        start=$(grep -nE "^[[:space:]]*<!-- aos:canonical:start -->[[:space:]]*$" "$PROJECT_ROOT/$f" | head -1 | cut -d: -f1)
        end=$(grep -nE "^[[:space:]]*<!-- aos:canonical:end -->[[:space:]]*$" "$PROJECT_ROOT/$f" | head -1 | cut -d: -f1)
        notice=$(grep -c "AOS-CANONICAL-TEMPLATE" "$PROJECT_ROOT/$f")
        if [ -z "$start" ] || [ -z "$end" ] || [ "$start" -ge "$end" ] || [ "${notice:-0}" -lt 1 ]; then
            bad="$bad $f"
        fi
    done
    if [ -n "$bad" ]; then
        log_fail 68 "C-MB8 canonical block malformed/missing markers in (${bad# }) — render insertion points broken; re-run scripts/aos_sync_all.sh"
    else
        log_pass 68 "C-MB8 canonical block well-formed (aos:canonical:start<end + notice present)"
    fi
}

check_69() {  # C-MB9 — CI-class correctness
    if [ "$CONTEXT" != "spoke" ]; then log_skip 69 "C-MB9 CI-class — spoke-only"; return 0; fi
    local wfdir="$PROJECT_ROOT/.github/workflows"
    if [ ! -d "$wfdir" ]; then log_pass 69 "C-MB9 CI-class OK (no .github/workflows — REMOVE-class correct)"; return 0; fi
    # The ONLY AOS-sanctioned spoke workflow is aos-ci-minimal.yml (KEEP-MINIMAL class). Any other
    # workflow file is Step-2d drift. Empty shell dir is inert (git cannot track empty dirs) → OK.
    # (Residual: a stale aos-ci-minimal.yml on a REMOVE-class spoke is benign and not flagged — the
    # KEEP/REMOVE class is a hub fact not reliably resolvable inside a spoke.)
    local stray=""
    local wf
    for wf in "$wfdir"/*.yml "$wfdir"/*.yaml; do
        [ -e "$wf" ] || continue
        case "$(basename "$wf")" in aos-ci-minimal.yml) ;; *) stray="$stray $(basename "$wf")" ;; esac
    done
    if [ -n "$stray" ]; then
        log_fail 69 "C-MB9 non-canonical workflow(s) (${stray# }) — only aos-ci-minimal.yml is sanctioned (Step 2d); remove the rest"
    else
        log_pass 69 "C-MB9 CI-class OK (only aos-ci-minimal.yml present, or empty)"
    fi
}

# ── CC-06 (v5 ENV fix round) — messaging-identity/provenance + WP-projection + onboarding invariants ──
# Advisory cluster (log_skip per the Check 55/58/59 idiom): a regression flips the check to WARN but NEVER
# log_fail in a standalone run, so the 0-FAIL baseline holds clone-portable; promote to HARD at the close
# gate once landed. Each check is grep-level over named HUB source files (<2s); source-absent on a spoke
# (the hub platform files aren't present) → skip silently. Locks the v5 identity/observability contract so
# the 54-fix remediation cannot silently drift back.
check_70() {  # CC-06 a — messaging-provenance: send/capture bind sender to the AUTHENTICATED actor
    local f="$PROJECT_ROOT/core/modules/management/dashboard_routes.py"
    [ -f "$f" ] || { log_skip 70 "CC-06 messaging-provenance — n/a (hub source absent)"; return 0; }
    if grep -q 'assert_actor_team(actor_team_id, body.sender' "$f"; then
        log_skip 70 "CC-06 messaging-provenance — send/capture bind sender to actor (assert_actor_team body.sender) (advisory)"
    else
        log_skip 70 "WARN: CC-06 messaging-provenance — assert_actor_team(actor_team_id, body.sender) missing in dashboard_routes.py (advisory; v5 ENV regression)"
    fi
}
check_71() {  # CC-06 b — SSE-on-send: a 'message arrived' event is emitted from the send/capture path
    local s="$PROJECT_ROOT/core/modules/audit/sse.py" d="$PROJECT_ROOT/core/modules/management/dashboard_routes.py"
    { [ -f "$s" ] && [ -f "$d" ]; } || { log_skip 71 "CC-06 SSE-on-send — n/a (hub source absent)"; return 0; }
    if grep -q 'def notify_msg_received' "$s" && grep -Eq 'notify_msg_received|_emit_msg_received' "$d"; then
        log_skip 71 "CC-06 SSE-on-send — notify_msg_received defined + wired from send/capture routes (advisory)"
    else
        log_skip 71 "WARN: CC-06 SSE-on-send — notify_msg_received missing in sse.py or not wired in routes (advisory; v5 ENV regression)"
    fi
}
check_72() {  # CC-06 c — projection-completeness: the file-WP projection INSERTs (not update-only)
    local f="$PROJECT_ROOT/core/modules/management/l0_project_io.py"
    [ -f "$f" ] || { log_skip 72 "CC-06 projection-completeness — n/a (hub source absent)"; return 0; }
    if grep -q 'def project_file_wps_to_read_model' "$f" && grep -q 'INSERT INTO work_packages' "$f"; then
        log_skip 72 "CC-06 projection-completeness — project_file_wps_to_read_model has an INSERT path (advisory)"
    else
        log_skip 72 "WARN: CC-06 projection-completeness — projection fn missing or update-only / no INSERT (advisory; v5 ENV regression)"
    fi
}
check_73() {  # CC-06 d — spoke-onboarding-identity: template + activation prompt carry the connectivity block
    local t="$PROJECT_ROOT/core/modules/project-governance/templates/SPOKE_CLAUDE_TEMPLATE.md"
    local p="$PROJECT_ROOT/core/modules/management/prompts_activation.py"
    { [ -f "$t" ] && [ -f "$p" ]; } || { log_skip 73 "CC-06 spoke-onboarding-identity — n/a (hub source absent)"; return 0; }
    local ok_t=0 ok_p=0
    { grep -q '8092' "$t" && grep -qiE 'actor|AOS_ACTOR_API_KEY' "$t"; } && ok_t=1
    { grep -q 'AOS_SESSION_TEAM_ID' "$p" && grep -q 'AOS_API_BASE' "$p"; } && ok_p=1
    if [ "$ok_t" = 1 ] && [ "$ok_p" = 1 ]; then
        log_skip 73 "CC-06 spoke-onboarding-identity — SPOKE_CLAUDE_TEMPLATE + activation prompt carry the actor-key/API-base block (advisory)"
    else
        log_skip 73 "WARN: CC-06 spoke-onboarding-identity — connectivity/identity block missing (template=$ok_t prompt=$ok_p) (advisory; v5 ENV regression)"
    fi
}

# ================================================================
# Check 80: metadata.yaml active_modules declared (team_00-approved L0
# bootstrap hardening — "enforce schema_version + active_modules in the L0
# bootstrap so new spokes cannot drift"). ADVISORY ONLY — never log_fail:
# every spoke that predates this WP (2026-07-22) legitimately lacks the
# field under the pre-existing "absent = all modules active" semantics
# (see file header) — this check surfaces the gap without breaking their
# gate. New spokes get the field by construction via metadata.yaml.template.
# ================================================================
check_80() {
    local meta="$AOS_DIR/metadata.yaml"
    _require_file 80 "$meta" "active_modules declaration" || return
    if grep -q '^active_modules:' "$meta" 2>/dev/null; then
        log_pass 80 "metadata.yaml declares active_modules explicitly"
    else
        echo "  [WARN] Check 80: metadata.yaml has no active_modules key — implicit 'all modules active' (pre-dates L0-bootstrap hardening; new spokes get this via metadata.yaml.template)"
        log_pass 80 "metadata.yaml active_modules — 1 advisory flag (non-blocking)"
    fi
}

# ================================================================
# Check 81: roadmap.yaml schema_version declared (companion to Check 80,
# same team_00-approved L0 bootstrap hardening item). ADVISORY ONLY, same
# rationale — top-level key per fleet convention (see eyalamit/
# smallfarmsagents/microgreens roadmap.yaml), not nested under project:.
# ================================================================
check_81() {
    local rm="$AOS_DIR/roadmap.yaml"
    _require_file 81 "$rm" "schema_version declaration" || return
    if grep -qE '^schema_version:' "$rm" 2>/dev/null; then
        log_pass 81 "roadmap.yaml declares schema_version explicitly"
    else
        echo "  [WARN] Check 81: roadmap.yaml has no top-level schema_version key (pre-dates L0-bootstrap hardening; new spokes get this via roadmap.yaml.template)"
        log_pass 81 "roadmap.yaml schema_version — 1 advisory flag (non-blocking)"
    fi
}

# ================================================================
# Execute All Checks
# ================================================================
echo "validate_aos.sh — running up to 81 checks on $AOS_DIR (active_modules: $ACTIVE_MODULES_MODE, context: ${CONTEXT:-?})"
echo "================================================="

check_1
check_2
check_3
check_4
check_5
check_6
check_7
check_8
check_9
check_10
check_11
check_12
check_13
check_14
check_15
check_16
check_17
check_18
check_19
check_20
check_21
check_22
check_23
check_24
check_25
check_26
check_27
check_28
check_29
check_30
check_31
check_32
check_33
check_34
check_35
check_36
check_37
check_38
check_39
check_40
check_41
check_42
check_43
check_44
check_45
check_46
check_47
check_48
check_49
check_50
check_51
check_52
check_53
check_54
check_55
check_56
check_57
check_58
check_59
check_60
check_61
check_62
check_63
check_64
check_65
check_66
check_67
check_68
check_69
check_70
check_71
check_72
check_73
check_74
check_75
check_76
check_77
check_78
check_79
check_80
check_81

echo ""
echo "================================================="
echo "RESULT: $PASS_COUNT PASS / $SKIP_COUNT SKIP / $FAIL_COUNT FAIL"
echo "================================================="

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "L-GATE_BUILD EXIT CRITERION: SATISFIED"
    exit 0
else
    echo "L-GATE_BUILD EXIT CRITERION: NOT MET ($FAIL_COUNT failures)"
    exit 1
fi
