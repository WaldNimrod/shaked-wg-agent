#!/bin/bash
# validate_aos.sh — Universal _aos/ Validation (15 Checks)
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

load_active_modules

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
# Check 3: Version Consistency (module 09 — version-identity)
# ================================================================
check_3() {
    _require_active_modules 3 09 || return 0
    python3 -c "
import yaml, sys, re, os
meta_path = '$AOS_DIR/metadata.yaml'
lkv_path = '$AOS_DIR/lean-kit/LEAN_KIT_VERSION.md'
if not os.path.isfile(meta_path):
    print(f'NOT_FOUND: {meta_path}', file=sys.stderr)
    sys.exit(1)
if not os.path.isfile(lkv_path):
    print(f'NOT_FOUND: {lkv_path}', file=sys.stderr)
    sys.exit(1)
with open(meta_path) as f:
    meta = yaml.safe_load(f)
lkv_meta = str(meta.get('lean_kit_version', '')).split('+')[0].strip()
with open(lkv_path) as f:
    content = f.read()
# Try markdown bold format first, then plain
match = re.search(r'\*\*version:\*\*\s*(\S+)', content)
if not match:
    match = re.search(r'version:\s*(\S+)', content)
if not match:
    print('PARSE_ERROR: cannot extract version from LEAN_KIT_VERSION.md', file=sys.stderr)
    sys.exit(1)
lkv_file = match.group(1).split('+')[0].strip()
if lkv_meta != lkv_file:
    print(f'MISMATCH: metadata.yaml={lkv_meta} vs LEAN_KIT_VERSION.md={lkv_file}', file=sys.stderr)
    sys.exit(1)
" && log_pass 3 "Version consistency confirmed" || log_fail 3 "Version mismatch"
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
# Check 10: Dashboard observability snapshot (module 05)
# ================================================================
check_10() {
    _require_active_modules 10 05 || return 0
    local p="$AOS_DIR/lean-kit/modules/dashboard-observability/MODULE.md"
    if [ ! -f "$p" ]; then
        log_fail 10 "dashboard-observability module missing from _aos/lean-kit snapshot"
        return
    fi
    log_pass 10 "dashboard-observability present in lean-kit snapshot"
}

# ================================================================
# Check 11: Governance directory completeness (module 01)
# ================================================================
check_11() {
    _require_active_modules 11 01 || return 0
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
    python3 -c "
import yaml, sys, os, glob

aos_dir = '$AOS_DIR'
def_path = os.path.join(aos_dir, 'definition.yaml')
gov_dir  = os.path.join(aos_dir, 'governance')

with open(def_path) as f:
    d = yaml.safe_load(f) or {}

defn_teams = set(k for k in d.keys() if k.startswith('team_'))
gov_files  = set(os.path.splitext(os.path.basename(f))[0]
                 for f in glob.glob(os.path.join(gov_dir, 'team_*.md')))

missing = sorted(defn_teams - gov_files)
if missing:
    for t in missing:
        print('MISSING_GOV: ' + t + ' in definition.yaml has no governance/team file', file=sys.stderr)
    sys.exit(1)
" && log_pass 13 "All definition.yaml teams have governance files" \
  || log_fail 13 "definition.yaml teams without governance files (ghost teams) — see MISSING_GOV lines above"
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

    # 12c: Scan tracked source files for forbidden patterns
    local violations=0
    local violation_details=""
    while IFS= read -r pattern; do
        [ -z "$pattern" ] && continue
        # Search in common source dirs, skip _aos/ itself and .git/
        local matches
        matches=$(grep -rl --include="*.py" --include="*.js" --include="*.ts" --include="*.md" \
            --exclude-dir=".git" --exclude-dir="_aos" --exclude-dir="node_modules" \
            --exclude-dir=".claude" --exclude-dir="_COMMUNICATION" --exclude-dir="_communication" \
            --exclude-dir="_archive" \
            --exclude="CHANGELOG.md" --exclude="*.template" \
            "$pattern" "$PROJECT_ROOT" 2>/dev/null | head -5)
        if [ -n "$matches" ]; then
            ((violations++)) || true
            local first_match
            first_match=$(echo "$matches" | head -1)
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

additional_dirs = settings.get('additionalDirectories', [])
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
# Execute All Checks
# ================================================================
echo "validate_aos.sh — running up to 15 checks on $AOS_DIR (active_modules mode: $ACTIVE_MODULES_MODE)"
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
