#!/usr/bin/env bash
# AOS pre-push validation hook (delegated) — AOS-V4.5-WP-CI-LOCAL-MINIMAL (S1)
#
# Purpose: the AUTHORITATIVE local pre-merge gate. Per ADR051 (Local-first, Minimal-cloud,
#   Zero-pay) this replaces reliance on GitHub-hosted CI: validation runs here, on the dev's
#   machine, before any push reaches GitHub.
#
# Prerequisites: bash, git, python3; invoked from within an AOS repo (hub or spoke).
# Env vars:
#   AOS_SKIP_TESTS=1         → run validate_aos.sh only; skip the repo test suite.
#   AOS_PREPUSH_TESTS=advisory → repo-test failures only WARN (non-blocking). Default is now
#                              STRICT: repo-test failures BLOCK the push. Flipped 2026-06-16 once
#                              the v5 suite reached green + deterministic (471/0); was advisory
#                              under D-S1-002 only while pre-existing test debt could wedge pushes.
# Ports: none — this script opens no listeners (CS-5: prerequisites/env/ports stated).
# Contract: exit 0 = allow push; non-zero = block push.
# Bypass: `git push --no-verify` skips the hook natively (single disciplined operator).
#
# Ref: _aos/work_packages/AOS-V4.5-WP-CI-LOCAL-MINIMAL/LOD400_BUILD_SPEC_v1.0.0.md §B/S1
#      [agents-os _aos/context/CODE_STANDARDS.md CS-5] (shell), CS-6 (English in code).

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

# Git env hygiene: when invoked as a git hook, git exports GIT_DIR / GIT_WORK_TREE /
# GIT_INDEX_FILE pointing at THIS repo. Child processes (validate_aos.sh, the pytest suite)
# inherit them, so their git subcommands operate on this repo instead of their own fixtures —
# e.g. tests doing `git init` / `git worktree add` in a tmp dir leaked 'init' commits and
# stray worktrees onto the working branch. Unset so children resolve git from their own cwd.
# (AOS-V4.5 — root cause of pre-push branch pollution.)
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_OBJECT_DIRECTORY 2>/dev/null || true

log() { printf '[pre-push] %s\n' "$1" >&2; }

# ── 1. Governance validation — locate validate_aos.sh ─────────────────────────
#    Preference: hub root wrapper → spoke snapshot (_aos/lean-kit) → hub lean-kit source.
VALIDATE=""
for cand in \
  "$REPO_ROOT/validate_aos.sh" \
  "$REPO_ROOT/_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh" \
  "$REPO_ROOT/lean-kit/modules/validation-quality/scripts/validate_aos.sh"; do
  if [ -f "$cand" ]; then VALIDATE="$cand"; break; fi
done

if [ -n "$VALIDATE" ]; then
  log "validate_aos.sh → $VALIDATE"
  if ! bash "$VALIDATE" "$REPO_ROOT"; then
    log "validate_aos.sh FAILED — push blocked. (bypass: git push --no-verify)"
    exit 1
  fi
else
  # DV-4.2 fail-loud (ADR056 / Model-B). An AOS repo (has _aos/) with no resolvable
  # validate_aos.sh means the Model-B governance cache is not hydrated — typical in a fresh
  # git worktree, where _aos/lean-kit/ is git-ignored and therefore not checked out. Silently
  # skipping the governance gate here is a false-green hole: the push lands with NO governance
  # validation at all (independent of --no-verify). Block loud and point at the fix. A genuine
  # non-AOS repo (no _aos/ at all) still skips harmlessly.
  if [ -d "$REPO_ROOT/_aos" ]; then
    log "validate_aos.sh not found but _aos/ present — Model-B governance cache not hydrated"
    log "  (fresh worktree?). Governance gate CANNOT run — push BLOCKED (DV-4.2 fail-loud)."
    log "  Fix: hydrate the cache → bash scripts/aos_governance_bootstrap.sh  (then re-push)."
    log "  Deliberate bypass (single disciplined operator): git push --no-verify."
    exit 1
  else
    log "validate_aos.sh not found + no _aos/ — genuine non-AOS repo, skipping governance validation."
  fi
fi

# ── 2. Repo test entrypoint (graceful — skip when absent) ─────────────────────
if [ "${AOS_SKIP_TESTS:-0}" = "1" ]; then
  log "AOS_SKIP_TESTS=1 — skipping repo test suite."
  exit 0
fi

# Detect + run the repo test entrypoint. Returns the test command's exit code
# (0 when no entrypoint or tooling absent — graceful).
_run_repo_tests() {
  if [ -f "$REPO_ROOT/Makefile" ] && grep -qE '^test:' "$REPO_ROOT/Makefile"; then
    log "tests: make test"; make -C "$REPO_ROOT" test; return $?
  elif [ -f "$REPO_ROOT/pytest.ini" ] || \
       { [ -f "$REPO_ROOT/pyproject.toml" ] && grep -q 'pytest' "$REPO_ROOT/pyproject.toml" 2>/dev/null; }; then
    if command -v pytest >/dev/null 2>&1; then log "tests: pytest -q"; pytest -q; return $?; fi
    log "pytest config present but pytest not installed — skipping."; return 0
  elif [ -f "$REPO_ROOT/package.json" ] && grep -q '"test"' "$REPO_ROOT/package.json"; then
    if command -v npm >/dev/null 2>&1; then log "tests: npm test"; ( cd "$REPO_ROOT" && npm test ); return $?; fi
    log "package.json test script present but npm not installed — skipping."; return 0
  fi
  log "no repo test entrypoint detected — validate-only."; return 0
}

if _run_repo_tests; then
  log "OK — push allowed."
else
  trc=$?
  if [ "${AOS_PREPUSH_TESTS:-strict}" = "strict" ]; then
    log "repo tests FAILED (rc=$trc) and AOS_PREPUSH_TESTS=strict — push blocked."
    exit 1
  fi
  log "WARNING: repo tests FAILED (rc=$trc) — ADVISORY mode, push ALLOWED."
  log "  (validate_aos.sh governance gate already passed; set AOS_PREPUSH_TESTS=strict to block on tests.)"
fi
exit 0
