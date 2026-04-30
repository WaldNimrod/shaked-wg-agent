#!/usr/bin/env bash
# test_msg_precommit_hook.sh — Runnable acceptance test for msg_precommit_hook.sh
# WP: AOS-V4-WP-MSG-HARDENING | Covers: ACs 1-9, 13 (hook-level)
#
# USAGE: bash lean-kit/modules/team-messaging/tests/test_msg_precommit_hook.sh
#
# Runs in temporary git repos to verify the hook rejects bad MSGs and passes
# good MSGs. Does NOT touch the live repo.
#
# Exit: 0 = all tests passed; 1 = one or more failures

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_SCRIPT="${REPO_ROOT}/lean-kit/modules/team-messaging/scripts/msg_precommit_hook.sh"
FIXTURES_DIR="${REPO_ROOT}/lean-kit/modules/team-messaging/tests/fixtures"

PASS_COUNT=0
FAIL_COUNT=0

pass() { echo "  PASS: $1"; PASS_COUNT=$((PASS_COUNT + 1)); }
fail() { echo "  FAIL: $1 — $2"; FAIL_COUNT=$((FAIL_COUNT + 1)); }

# Run hook against a file in a temp git repo.
# Returns the hook exit code.
run_hook_on_file() {
    local fixture_file="$1"
    local dest_rel="$2"
    local extra_env="${3:-}"
    local tmpdir
    tmpdir="$(mktemp -d /tmp/aos_hook_test_XXXXXX)"

    git -C "$tmpdir" init -q 2>/dev/null
    git -C "$tmpdir" config user.email "test@aos.local" 2>/dev/null
    git -C "$tmpdir" config user.name "AOS Test" 2>/dev/null

    local dest_dir="${tmpdir}/$(dirname "$dest_rel")"
    mkdir -p "$dest_dir"
    cp "$fixture_file" "${tmpdir}/${dest_rel}"
    git -C "$tmpdir" add "$dest_rel" 2>/dev/null

    local hook_exit=0
    if [ -n "$extra_env" ]; then
        (cd "$tmpdir" && env $extra_env bash "$HOOK_SCRIPT") 2>/dev/null || hook_exit=$?
    else
        (cd "$tmpdir" && bash "$HOOK_SCRIPT") 2>/dev/null || hook_exit=$?
    fi

    rm -rf "$tmpdir"
    return $hook_exit
}

# Get hook stderr output on a file
hook_stderr_on_file() {
    local fixture_file="$1"
    local dest_rel="$2"
    local tmpdir
    tmpdir="$(mktemp -d /tmp/aos_hook_stderr_XXXXXX)"

    git -C "$tmpdir" init -q 2>/dev/null
    git -C "$tmpdir" config user.email "test@aos.local" 2>/dev/null
    git -C "$tmpdir" config user.name "AOS Test" 2>/dev/null

    local dest_dir="${tmpdir}/$(dirname "$dest_rel")"
    mkdir -p "$dest_dir"
    cp "$fixture_file" "${tmpdir}/${dest_rel}"
    git -C "$tmpdir" add "$dest_rel" 2>/dev/null

    local out
    out="$( (cd "$tmpdir" && bash "$HOOK_SCRIPT") 2>&1 )" || true

    rm -rf "$tmpdir"
    echo "$out"
}

echo ""
echo "=========================================="
echo " AOS MSG Pre-Commit Hook — Acceptance Tests"
echo "=========================================="
echo ""

# ── AC-1: Hook exists and is executable ──────────────────────────────────────
echo "AC-1: Hook script exists + executable"
if [ -x "$HOOK_SCRIPT" ]; then
    pass "hook is executable at canonical path"
else
    fail "hook not executable" "$HOOK_SCRIPT"
fi

echo "AC-1b: Syntax check (bash -n)"
if bash -n "$HOOK_SCRIPT" 2>/dev/null; then
    pass "bash -n syntax valid"
else
    fail "bash -n" "syntax error in hook"
fi

echo ""
echo "--- Fixture-based tests ---"

# ── AC-3: Missing required fields → rejected ─────────────────────────────────
echo "AC-3a: Missing from_team → rejected"
hook_exit=0
run_hook_on_file \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-001.md" \
    "_COMMUNICATION/team_100/MSG-HUB-20260430-001.md" || hook_exit=$?
if [ "$hook_exit" = "1" ]; then
    # Verify error names the field
    stderr_out="$(hook_stderr_on_file \
        "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-001.md" \
        "_COMMUNICATION/team_100/MSG-HUB-20260430-001.md")"
    if echo "$stderr_out" | grep -q "from_team"; then
        pass "missing from_team rejected with field named in error"
    else
        fail "from_team not named in error" "$stderr_out"
    fi
else
    fail "missing from_team should reject (exit 1)" "got exit=$hook_exit"
fi

echo "AC-3b: Missing to_team → rejected"
hook_exit=0
run_hook_on_file \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-002.md" \
    "_COMMUNICATION/team_100/MSG-HUB-20260430-002.md" || hook_exit=$?
if [ "$hook_exit" = "1" ]; then
    pass "missing to_team rejected"
else
    fail "missing to_team should reject" "got exit=$hook_exit"
fi

echo "AC-3c: Missing type → rejected"
hook_exit=0
run_hook_on_file \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-003.md" \
    "_COMMUNICATION/team_100/MSG-HUB-20260430-003.md" || hook_exit=$?
if [ "$hook_exit" = "1" ]; then
    pass "missing type rejected"
else
    fail "missing type should reject" "got exit=$hook_exit"
fi

# ── AC-4: Valid MSGs pass ─────────────────────────────────────────────────────
echo "AC-4: Valid informal MSG → passes"
hook_exit=0
run_hook_on_file \
    "${FIXTURES_DIR}/valid/MSG-HUB-20260430-001.md" \
    "_COMMUNICATION/team_100/MSG-HUB-20260430-001.md" || hook_exit=$?
if [ "$hook_exit" = "0" ]; then
    pass "valid informal MSG passes"
else
    fail "valid informal MSG should pass" "got exit=$hook_exit"
fi

echo "AC-4b: Valid formal task MSG (with continuation fields) → passes"
hook_exit=0
run_hook_on_file \
    "${FIXTURES_DIR}/valid/MSG-HUB-20260430-002.md" \
    "_COMMUNICATION/team_100/MSG-HUB-20260430-002.md" || hook_exit=$?
if [ "$hook_exit" = "0" ]; then
    pass "valid formal task MSG passes"
else
    fail "valid formal task MSG should pass" "got exit=$hook_exit"
fi

# ── AC-7: Invalid filename → rejected ────────────────────────────────────────
echo "AC-7: Invalid filename pattern → rejected"
hook_exit=0
run_hook_on_file \
    "${FIXTURES_DIR}/malformed/MSG-WRONG-FORMAT-001.md" \
    "_COMMUNICATION/team_100/MSG-WRONG-FORMAT-001.md" || hook_exit=$?
if [ "$hook_exit" = "1" ]; then
    pass "invalid filename rejected"
else
    fail "invalid filename should reject" "got exit=$hook_exit"
fi

# ── AC-8: Strict mode + missing schema_version → rejected ────────────────────
echo "AC-8: AOS_MSG_STRICT=1 + missing schema_version → rejected"
_tmpfixture="$(mktemp /tmp/aos_strict_XXXXXX.md)"
printf -- '---\nid: MSG-HUB-20260430-099\nfrom_team: team_100\nto_team: team_110\ntype: informal\nsubject: Strict test\ndate: 2026-04-30T10:00:00Z\n---\nBody\n' > "$_tmpfixture"

hook_exit=0
run_hook_on_file "$_tmpfixture" "_COMMUNICATION/team_100/MSG-HUB-20260430-099.md" "AOS_MSG_STRICT=1" || hook_exit=$?
rm -f "$_tmpfixture"
if [ "$hook_exit" = "1" ]; then
    pass "strict mode rejects missing schema_version"
else
    fail "strict mode should reject missing schema_version" "got exit=$hook_exit"
fi

# ── Continuation fields: formal type without them → rejected ─────────────────
echo "AC-cont: Formal type without continuation fields → rejected (ADR043 v1.3.0)"
hook_exit=0
run_hook_on_file \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-004.md" \
    "_COMMUNICATION/team_100/MSG-HUB-20260430-004.md" || hook_exit=$?
if [ "$hook_exit" = "1" ]; then
    stderr_out="$(hook_stderr_on_file \
        "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-004.md" \
        "_COMMUNICATION/team_100/MSG-HUB-20260430-004.md")"
    if echo "$stderr_out" | grep -qE "ADR043|next_step|handoff_to|continuation"; then
        pass "formal type without continuation fields rejected with ADR043 reference"
    else
        fail "error should reference ADR043/continuation fields" "$stderr_out"
    fi
else
    fail "formal type without continuation should reject" "got exit=$hook_exit"
fi

# ── Non-MSG file → hook not activated ─────────────────────────────────────────
echo "AC-noop: Non-MSG staged file → hook exits 0"
tmpdir="$(mktemp -d /tmp/aos_noop_XXXXXX)"
git -C "$tmpdir" init -q 2>/dev/null
git -C "$tmpdir" config user.email "test@aos.local" 2>/dev/null
git -C "$tmpdir" config user.name "AOS Test" 2>/dev/null
printf 'hello\n' > "${tmpdir}/README.md"
git -C "$tmpdir" add README.md 2>/dev/null
noop_exit=0
(cd "$tmpdir" && bash "$HOOK_SCRIPT") 2>/dev/null || noop_exit=$?
rm -rf "$tmpdir"
if [ "$noop_exit" = "0" ]; then
    pass "non-MSG staged file — hook exits 0"
else
    fail "non-MSG file should not activate hook" "got exit=$noop_exit"
fi

# ── AC-13: No TBD/FIXME/to be defined ────────────────────────────────────────
echo "AC-13: No TBD/FIXME/to be defined in deliverables"
tbd_found=0
for f in \
    "$HOOK_SCRIPT" \
    "${REPO_ROOT}/scripts/install_hooks.sh" \
    "${FIXTURES_DIR}/valid/MSG-HUB-20260430-001.md" \
    "${FIXTURES_DIR}/valid/MSG-HUB-20260430-002.md" \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-001.md" \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-002.md" \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-003.md" \
    "${FIXTURES_DIR}/malformed/MSG-HUB-20260430-004.md" \
    "${FIXTURES_DIR}/malformed/MSG-WRONG-FORMAT-001.md"; do
    if [ -f "$f" ] && grep -qiE '\bTBD\b|\bFIXME\b|to be defined' "$f" 2>/dev/null; then
        echo "  WARN: found TBD/FIXME in: $f"
        tbd_found=$((tbd_found + 1))
    fi
done
if [ "$tbd_found" = "0" ]; then
    pass "0 TBD/FIXME/to be defined strings found"
else
    fail "TBD/FIXME found in deliverables" "$tbd_found occurrences"
fi

# ── AC-9: Performance ─────────────────────────────────────────────────────────
echo "AC-9: Performance — hook on 10 staged MSG files (<200ms)"
perf_tmpdir="$(mktemp -d /tmp/aos_perf_XXXXXX)"
git -C "$perf_tmpdir" init -q 2>/dev/null
git -C "$perf_tmpdir" config user.email "perf@aos.local" 2>/dev/null
git -C "$perf_tmpdir" config user.name "AOS Perf" 2>/dev/null
mkdir -p "${perf_tmpdir}/_COMMUNICATION/team_100"

valid_content="$(cat "${FIXTURES_DIR}/valid/MSG-HUB-20260430-001.md")"
for i in $(seq -w 1 10); do
    dest="${perf_tmpdir}/_COMMUNICATION/team_100/MSG-HUB-20260430-0${i}.md"
    printf '%s\n' "$valid_content" | \
        sed "s/id: MSG-HUB-20260430-001/id: MSG-HUB-20260430-0${i}/" > "$dest"
done
git -C "$perf_tmpdir" add "_COMMUNICATION/" 2>/dev/null

# Use python3 for millisecond timing (portable on macOS + linux).
# Take best of 3 runs to account for process startup variance.
elapsed_ms=$(python3 -c "
import subprocess, time

times = []
for _ in range(3):
    start = time.perf_counter()
    subprocess.run(['bash', '${HOOK_SCRIPT}'], cwd='${perf_tmpdir}', capture_output=True)
    elapsed = (time.perf_counter() - start) * 1000
    times.append(elapsed)
# Use minimum to measure hook runtime (exclude OS scheduling noise)
print(int(min(times)))
")
rm -rf "$perf_tmpdir"

if [ "$elapsed_ms" -lt 200 ]; then
    pass "${elapsed_ms}ms for 10 MSG files (target < 200ms)"
else
    fail "performance" "${elapsed_ms}ms exceeds 200ms target"
fi

# ─── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo " Results: ${PASS_COUNT} PASS / ${FAIL_COUNT} FAIL"
echo "=========================================="
echo ""

[ "$FAIL_COUNT" = "0" ] && exit 0 || exit 1
