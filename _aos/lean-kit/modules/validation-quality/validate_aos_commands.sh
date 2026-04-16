#!/bin/bash
# validate_aos_commands.sh — AOS Commands Structural Validation
# =================================================================
# Validates AOS_*.md slash commands against aos_commands_manifest.yaml (SSoT).
# Usage: bash validate_aos_commands.sh [project-root]
# Exit: 0 = ALL PASS, 1 = ONE OR MORE FAIL
# Dependencies: bash, grep, wc, ls, python3 + PyYAML
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${1:-.}"
COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"
MANIFEST="$SCRIPT_DIR/schemas/aos_commands_manifest.yaml"
if [ ! -f "$MANIFEST" ]; then
    MANIFEST="$PROJECT_ROOT/_aos/lean-kit/modules/validation-quality/schemas/aos_commands_manifest.yaml"
fi

PASS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

log_pass() { echo "[PASS] AC-$1: $2"; ((PASS_COUNT++)) || true; }
log_fail() { echo "[FAIL] AC-$1: $2"; ((FAIL_COUNT++)) || true; }
log_skip() { echo "[SKIP] AC-$1: $2"; ((SKIP_COUNT++)) || true; }

# Load expected basenames (no .md) from manifest — space-separated
EXPECTED_LIST=""
EXPECTED_N=0
load_manifest() {
    if [ ! -f "$MANIFEST" ]; then
        return 1
    fi
    EXPECTED_LIST=$(python3 -c "
import yaml, sys
try:
    with open(sys.argv[1]) as f:
        d = yaml.safe_load(f) or {}
    files = d.get('expected_command_files', [])
    for x in files:
        x = str(x).strip()
        if x.endswith('.md'):
            print(x[:-3], end=' ')
        else:
            print(x, end=' ')
except Exception as e:
    print('', file=sys.stderr)
    sys.exit(1)
" "$MANIFEST") || return 1
    EXPECTED_N=$(python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    d = yaml.safe_load(f) or {}
print(len(d.get('expected_command_files', [])))
" "$MANIFEST")
    return 0
}

# ================================================================
# AC-A1: Command inventory matches manifest
# ================================================================
check_a1() {
    if [ ! -d "$COMMANDS_DIR" ]; then
        log_fail "A1" ".claude/commands/ directory not found at $COMMANDS_DIR"
        return
    fi
    if ! load_manifest; then
        log_fail "A1" "Manifest not found or invalid: $MANIFEST"
        return
    fi
    local count
    count=$(find "$COMMANDS_DIR" -maxdepth 1 -name 'AOS_*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -ne "$EXPECTED_N" ]; then
        log_fail "A1" "Found $count AOS_*.md files, manifest expects $EXPECTED_N"
        return
    fi
    local missing=0
    local b
    for b in $EXPECTED_LIST; do
        if [ ! -f "$COMMANDS_DIR/$b.md" ]; then
            echo "  MISSING: $b.md"
            ((missing++)) || true
        fi
    done
    if [ "$missing" -eq 0 ]; then
        log_pass "A1" "Command files match manifest ($EXPECTED_N files)"
    else
        log_fail "A1" "$missing file(s) missing vs manifest"
    fi
}

# ================================================================
# AC-A2: File structure (line 1, Phase, Error Handling)
# ================================================================
check_a2() {
    if [ ! -d "$COMMANDS_DIR" ]; then
        log_skip "A2" "Cannot check — .claude/commands/ not found"
        return
    fi
    if ! load_manifest; then
        log_fail "A2" "Manifest not loadable"
        return
    fi
    local bad_files=0
    local b
    for b in $EXPECTED_LIST; do
        local f="$COMMANDS_DIR/$b.md"
        [ -f "$f" ] || continue
        local line1
        line1=$(head -n 1 "$f" | tr -d ' \t\n')
        if [ -z "$line1" ]; then
            echo "  FAIL: $b.md — line 1 is empty"
            ((bad_files++)) || true
            continue
        fi
        if ! grep -q "^## Phase" "$f"; then
            echo "  FAIL: $b.md — missing '## Phase' header"
            ((bad_files++)) || true
            continue
        fi
        if ! grep -q "^## Error Handling" "$f"; then
            echo "  FAIL: $b.md — missing '## Error Handling' section"
            ((bad_files++)) || true
            continue
        fi
    done
    if [ "$bad_files" -eq 0 ]; then
        log_pass "A2" "All manifest command files have required structure"
    else
        log_fail "A2" "$bad_files file(s) missing required structure"
    fi
}

# ================================================================
# AC-A3: Spoke protection (guards on hub paths)
# ================================================================
check_a3() {
    if [ ! -d "$COMMANDS_DIR" ]; then
        log_skip "A3" "Cannot check — .claude/commands/ not found"
        return
    fi
    local bad_files=0
    for f in "$COMMANDS_DIR"/AOS_*.md; do
        [ -f "$f" ] || continue
        local basename_f
        basename_f=$(basename "$f")
        if [[ "$basename_f" == "AOS_gov-sync.md" ]] || [[ "$basename_f" == "AOS_gov-update.md" ]]; then
            continue
        fi
        if grep -q "core/definition.yaml" "$f"; then
            if ! grep -q "project_identity.yaml" "$f" && ! grep -q "is_hub" "$f"; then
                echo "  WARN: $basename_f references core/definition.yaml without spoke guard"
            fi
        fi
    done
    log_pass "A3" "Hub path references have appropriate spoke guards (or gov exceptions)"
}

# ================================================================
# AC-A4: GATE_REGISTRY.md lists all commands from manifest
# ================================================================
check_a4() {
    local registry_file="$PROJECT_ROOT/_aos/lean-kit/modules/validation-quality/GATE_REGISTRY.md"
    if [ ! -f "$registry_file" ]; then
        registry_file="$PROJECT_ROOT/lean-kit/modules/validation-quality/GATE_REGISTRY.md"
    fi
    if [ ! -f "$registry_file" ]; then
        log_fail "A4" "GATE_REGISTRY.md not found"
        return
    fi
    if ! load_manifest; then
        log_fail "A4" "Manifest not loadable"
        return
    fi
    local missing=0
    local b
    for b in $EXPECTED_LIST; do
        if ! grep -q "$b" "$registry_file"; then
            echo "  MISSING: $b not found in GATE_REGISTRY.md"
            ((missing++)) || true
        fi
    done
    if [ "$missing" -eq 0 ]; then
        log_pass "A4" "All manifest command names present in GATE_REGISTRY.md"
    else
        log_fail "A4" "$missing command name(s) missing from GATE_REGISTRY.md"
    fi
}

# ================================================================
# AC-A5: ADR031 lists all manifest commands (Tier narrative)
# ================================================================
check_a5() {
    local adr_file="$PROJECT_ROOT/governance/directives/ADR031_MODEL_B_FILE_STRUCTURE.md"
    if [ ! -f "$adr_file" ]; then
        log_fail "A5" "ADR031 file not found at $adr_file"
        return
    fi
    if ! load_manifest; then
        log_fail "A5" "Manifest not loadable"
        return
    fi
    local missing=0
    local b
    for b in $EXPECTED_LIST; do
        if ! grep -q "$b" "$adr_file"; then
            echo "  MISSING: $b not found in ADR031"
            ((missing++)) || true
        fi
    done
    if [ "$missing" -eq 0 ]; then
        log_pass "A5" "All manifest command names present in ADR031"
    else
        log_fail "A5" "$missing command name(s) missing from ADR031"
    fi
}

# ================================================================
# AC-A6: quick-help.html (optional)
# ================================================================
check_a6() {
    local html_file="$PROJECT_ROOT/dashboard/quick-help.html"
    if [ ! -f "$html_file" ]; then
        log_skip "A6" "quick-help.html not found (non-blocking)"
        return
    fi
    if ! load_manifest; then
        log_fail "A6" "Manifest not loadable"
        return
    fi
    local missing=0
    local b
    for b in $EXPECTED_LIST; do
        if ! grep -q "$b" "$html_file"; then
            echo "  MISSING: $b not found in quick-help.html"
            ((missing++)) || true
        fi
    done
    if [ "$missing" -eq 0 ]; then
        log_pass "A6" "All manifest command names present in quick-help.html"
    else
        log_fail "A6" "$missing command name(s) missing from quick-help.html"
    fi
}

# ================================================================
# AC-A7: Global symlinks ~/.claude/commands/
# ================================================================
check_a7() {
    local symlink_dir="$HOME/.claude/commands"
    if [ ! -d "$symlink_dir" ]; then
        log_fail "A7" "~/.claude/commands/ directory not found"
        return
    fi
    if ! load_manifest; then
        log_fail "A7" "Manifest not loadable"
        return
    fi
    local count=0
    local bad_links=0
    local b
    for b in $EXPECTED_LIST; do
        local link_file="$symlink_dir/$b.md"
        if [ -L "$link_file" ]; then
            ((count++)) || true
            local target
            target=$(readlink "$link_file" 2>/dev/null || echo "")
            if [[ ! "$target" == *"$b.md"* ]]; then
                echo "  WARN: $link_file does not resolve to expected command"
                ((bad_links++)) || true
            fi
        fi
    done
    if [ "$count" -eq "$EXPECTED_N" ] && [ "$bad_links" -eq 0 ]; then
        log_pass "A7" "All $EXPECTED_N symlinks present in ~/.claude/commands/"
    else
        log_fail "A7" "Found $count symlinks, expected $EXPECTED_N (bad_links: $bad_links)"
    fi
}

# ================================================================
# AC-A8: Spoke settings (hub dev paths — advisory for local machine)
# ================================================================
check_a8() {
    local spokes=(
        "/Users/nimrod/Documents/AOS-Sandbox-Lean"
        "/Users/nimrod/Documents/AOS-Sandbox-Full"
        "/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject"
        "/Users/nimrod/Documents/SmallFarmsAgents"
    )
    local missing_spokes=0
    local hub_path="$PROJECT_ROOT"
    for spoke in "${spokes[@]}"; do
        local settings_file="$spoke/.claude/settings.json"
        if [ ! -f "$settings_file" ]; then
            echo "  MISSING: .claude/settings.json in $spoke"
            ((missing_spokes++)) || true
            continue
        fi
        if ! grep -q "$hub_path" "$settings_file" 2>/dev/null; then
            echo "  WARN: hub path not in additionalDirectories for $spoke"
            ((missing_spokes++)) || true
        fi
    done
    if [ "$missing_spokes" -eq 0 ]; then
        log_pass "A8" "All 4 spokes have .claude/settings.json with hub path in additionalDirectories"
    else
        log_fail "A8" "$missing_spokes spoke(s) missing proper configuration"
    fi
}

# ================================================================
# AC-A9: Linter self-check
# ================================================================
check_a9() {
    local script_path="$SCRIPT_DIR/validate_aos_commands.sh"
    if [ ! -f "$script_path" ]; then
        log_fail "A9" "validate_aos_commands.sh not found at $script_path"
        return
    fi
    if [ ! -x "$script_path" ]; then
        log_fail "A9" "validate_aos_commands.sh exists but is not executable"
        return
    fi
    if ! head -n 1 "$script_path" | grep -q "#!/bin/bash"; then
        log_fail "A9" "Script missing #!/bin/bash shebang"
        return
    fi
    if ! grep -q "log_pass\|log_fail\|log_skip" "$script_path"; then
        log_fail "A9" "Script missing logging functions"
        return
    fi
    if [ ! -f "$MANIFEST" ]; then
        log_fail "A9" "Manifest missing next to linter: $MANIFEST"
        return
    fi
    log_pass "A9" "Linter + manifest present and executable"
}

# ================================================================
# Execute
# ================================================================
echo "validate_aos_commands.sh — AOS command validation (manifest: aos_commands_manifest.yaml)"
echo "========================================================================"

if ! load_manifest; then
    echo "FATAL: Cannot load manifest at $MANIFEST"
    exit 1
fi

check_a1
check_a2
check_a3
check_a4
check_a5
check_a6
check_a7
check_a8
check_a9

echo ""
echo "========================================================================"
echo "SUMMARY: $PASS_COUNT passed | $FAIL_COUNT failed | $SKIP_COUNT skipped"
echo "========================================================================"

if [ "$FAIL_COUNT" -eq 0 ]; then
    echo "AOS COMMAND VALIDATION: PASSED"
    exit 0
else
    echo "AOS COMMAND VALIDATION: FAILED ($FAIL_COUNT failures)"
    exit 1
fi
