#!/bin/bash
# propagate_governance.sh — Governance propagation with conflict detection & verification
# =======================================================================================
# Iron Rule #11: Governance flows source → snapshot.
# Source: AOS Project core/governance/ (team_*.md) and governance/directives/ (ADR*.md)
#         → all spoke _aos/governance/ and _aos/governance/directives/ targets.
# Team 60: joint operations / infrastructure authorship for ADR→spoke snapshot path
#         (parallels port-registry and validate_aos spoke parity).
#
# Usage:
#   propagate_governance.sh --all                     # propagate to all registered targets
#   propagate_governance.sh --all --diff              # show diffs before propagating
#   propagate_governance.sh --all --dry-run           # show the change PLAN (update/add/remove), don't copy
#   propagate_governance.sh --all --report FILE.md    # generate markdown report
#   propagate_governance.sh <aos_path> <spoke_path>   # legacy single-target mode
#
# R4 (AOS-V5-WP-GOV-SNAPSHOT-HARDENING):
#   - TARGETS are DERIVED from _aos/projects.yaml (ADR049 SSoT) — no hardcoded array.
#   - --dry-run reports "will update N / add M / remove K" (one-directional
#     source→snapshot is an OVERWRITE, not a merge conflict) and exits 0.
#   - live mode prunes dissolved-team team_*.md left on a spoke (reconcile, not upsert).
#
# Exit codes:
#   0 = success (targets propagated + verified, or dry-run plan reported)
#   1 = fatal error / verification / push failure
#
# See: methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md
# If a WP shipped new/modified .claude/commands/AOS_*.md: also run
#   lean-kit/modules/project-governance/docs/WP_COMMAND_SHIPPING_CHECKLIST_v1.0.0.md

set -uo pipefail

# ─── ADR040 / Iron Rule #12 — Authority Gate ────────────────────────────────────
# Only team_00 (Principal) and team_100 (Chief Architect) may run this script.
# Requires AOS_ACTOR_TEAM_ID env var. Bypass (not recommended, dev-only):
# AOS_SKIP_AUTHORITY_CHECK=1.
ACTOR="${AOS_ACTOR_TEAM_ID:-}"
if [[ "${AOS_SKIP_AUTHORITY_CHECK:-0}" != "1" ]]; then
  if [[ -z "$ACTOR" ]]; then
    echo "⛔ FATAL (ADR040 / Iron Rule #12): AOS_ACTOR_TEAM_ID env var not set." >&2
    echo "   Authorized teams: team_00, team_100." >&2
    echo "   Example: AOS_ACTOR_TEAM_ID=team_100 $0 --all" >&2
    echo "   Non-AOS teams must file GOVERNANCE_CHANGE_REQUEST — see methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.0.0.md" >&2
    exit 10
  fi
  case "$ACTOR" in
    team_00|team_100) ;;
    *)
      echo "⛔ FATAL (ADR040 / Iron Rule #12): team '$ACTOR' is not authorized to propagate governance." >&2
      echo "   Authorized teams: team_00, team_100." >&2
      echo "   To request a governance change: file GOVERNANCE_CHANGE_REQUEST artifact in _COMMUNICATION/team_XX/ and route to team_100." >&2
      echo "   Template: lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template" >&2
      exit 10
      ;;
  esac
fi

# ─── Configuration ──────────────────────────────────────────────────────────────

# AOS hub project root (auto-detect from script location)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SOURCE="$AOS_ROOT/core/governance"

# Hub identity verifier (RC2 defense — prevent silent-match when misconfigured)
if [[ ! -f "$AOS_ROOT/_aos/project_identity.yaml" ]]; then
  echo "⛔ FATAL: Not an AOS hub: $AOS_ROOT missing _aos/project_identity.yaml" >&2
  echo "   propagate_governance.sh must be invoked from within the hub." >&2
  exit 11
fi

echo "✓ Authority: $ACTOR (authorized per ADR040 / Iron Rule #12)"
echo "✓ Hub identity verified: $AOS_ROOT"

# Registered spoke targets — DERIVED from _aos/projects.yaml (ADR049 Registry SSoT).
# R4(c): the hardcoded path array is GONE (it drifted to stale paths during the v5
# cutover). TARGETS is populated AFTER argument parsing (so legacy mode + MODE are
# known) by _load_governance_targets_from_yaml — see "Derive TARGETS" block below.
PROJECTS_YAML="$AOS_ROOT/_aos/projects.yaml"
TARGETS=()

# Emit "<local_path>/_aos/governance" for every enabled non-hub spoke in the registry.
_load_governance_targets_from_yaml() {
  local projects_yaml="$1"
  python3 - "$projects_yaml" <<'PYEOF'
import sys, yaml
with open(sys.argv[1]) as f:
    doc = yaml.safe_load(f) or {}
for p in doc.get('projects', []) or []:
    if not p.get('enabled', True):
        continue
    if p.get('type') == 'aos_project':   # hub itself — added separately (self-snapshot)
        continue
    lp = p.get('local_path') or ''
    if not lp:
        continue
    print(f"{lp.rstrip('/')}/_aos/governance")
PYEOF
}

# Validation script path
VALIDATE_SCRIPT="$AOS_ROOT/lean-kit/modules/validation-quality/scripts/validate_aos.sh"
# Also check _aos copy
VALIDATE_SCRIPT_AOS="$AOS_ROOT/_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh"

# ─── Platform Detection ─────────────────────────────────────────────────────────

md5_hash() {
  if command -v md5 >/dev/null 2>&1; then
    md5 -q "$1"
  elif command -v md5sum >/dev/null 2>&1; then
    md5sum "$1" | awk '{print $1}'
  else
    echo "ERROR: no md5 command found" >&2
    exit 1
  fi
}

# ─── State ───────────────────────────────────────────────────────────────────────

MODE="legacy"          # legacy | all
DRY_RUN=false
SHOW_DIFF=false
# NO_PUSH: commit propagated snapshots locally but never `git push`.
# Default ON for the single-dev/one-machine model (git = backup/deploy, not dev-sync;
# ADR052). Honors env override AOS_SYNC_NO_PUSH=0 to re-enable push, or --push flag.
NO_PUSH="${AOS_SYNC_NO_PUSH:-1}"
# GIT_NET_TIMEOUT: hard cap (seconds) on every network git op so a credential prompt
# or stalled remote can NEVER hang propagation again (root cause of the 3× hang).
GIT_NET_TIMEOUT="${AOS_GIT_NET_TIMEOUT:-30}"
REPORT_FILE=""
LEGACY_AOS=""
LEGACY_SPOKE=""

# R4(a): one-directional source→snapshot propagation is an OVERWRITE, not a merge
# conflict. The dry-run plan counts UPDATE (target differs), ADD (target missing),
# REMOVE (dissolved-team file on spoke). CHANGES_PLANNED is informational and does
# NOT abort the dry-run (rc 0). CONFLICTS_FOUND is retained for backward-compat but
# only ever increments on a *true* anomaly (none in normal overwrite flow).
CONFLICTS_FOUND=0
CHANGES_UPDATE=0
CHANGES_ADD=0
CHANGES_REMOVE=0
FILES_PROPAGATED=0
FILES_REMOVED=0
TARGETS_OK=0
TARGETS_SKIPPED=0
TARGETS_FAILED=0
VERIFICATION_ERRORS=0

REPORT_LINES=()

# ─── Argument Parsing ────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)       MODE="all"; shift ;;
    --dry-run)   DRY_RUN=true; shift ;;
    --diff)      SHOW_DIFF=true; shift ;;
    --no-push)   NO_PUSH=1; shift ;;
    --push)      NO_PUSH=0; shift ;;
    --report)    REPORT_FILE="${2:?--report requires a file path}"; shift 2 ;;
    --help|-h)
      echo "Usage: propagate_governance.sh [--all] [--diff] [--dry-run] [--no-push|--push] [--report FILE]"
      echo "       propagate_governance.sh <aos_project_path> <spoke_project_path>"
      exit 0
      ;;
    *)
      if [ -z "$LEGACY_AOS" ]; then
        LEGACY_AOS="$1"
      elif [ -z "$LEGACY_SPOKE" ]; then
        LEGACY_SPOKE="$1"
      else
        echo "ERROR: unexpected argument: $1" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

# ─── ADR052 Addendum / Iron Rule #17 — Orchestrator Worktree Enforcement ────────
# Standalone invocations (not orchestrated by aos_sync_all.sh, which already checked
# and exported AOS_WORKTREE_VERIFIED=1) must not run from the shared primary checkout.
# --dry-run never mutates, so it is exempt. See scripts/lib/aos_worktree_guard.sh.
if [ "$DRY_RUN" = false ]; then
  _WT_GUARD="$AOS_ROOT/scripts/lib/aos_worktree_guard.sh"
  [ -f "$_WT_GUARD" ] && . "$_WT_GUARD"
  if declare -f aos_require_isolated_worktree >/dev/null 2>&1; then
    aos_require_isolated_worktree "propagate_governance.sh" || exit $?
  fi
fi

# Legacy mode: override SOURCE and TARGETS from positional args
if [ "$MODE" = "legacy" ]; then
  if [ -z "$LEGACY_AOS" ] || [ -z "$LEGACY_SPOKE" ]; then
    echo "Usage: propagate_governance.sh <aos_project_path> <spoke_project_path>"
    echo "   or: propagate_governance.sh --all [--diff] [--dry-run] [--report FILE]"
    exit 1
  fi
  SOURCE="$LEGACY_AOS/core/governance"
  TARGETS=("$LEGACY_SPOKE/_aos/governance")
else
  # ── Derive TARGETS from the registry (ADR049 SSoT) — R4(c) ──
  # Hub self-snapshot first, then every enabled non-hub spoke from projects.yaml.
  TARGETS=("$AOS_ROOT/_aos/governance")
  if [ -f "$PROJECTS_YAML" ]; then
    _tgt_tmp=$(mktemp 2>/dev/null) || _tgt_tmp="/tmp/aos_gov_targets_$$"
    _load_governance_targets_from_yaml "$PROJECTS_YAML" > "$_tgt_tmp" 2>/dev/null || true
    while IFS= read -r _tline; do
      [ -n "$_tline" ] && TARGETS+=("$_tline")
    done < "$_tgt_tmp"
    rm -f "$_tgt_tmp" 2>/dev/null || true
  else
    echo "WARN: registry $PROJECTS_YAML not found — propagating to hub self-snapshot only" >&2
  fi
fi

# ADR directive snapshot source (hub: governance/directives/ADR*.md)
if [ "$MODE" = "legacy" ]; then
  DIRECTIVE_SOURCE="${LEGACY_AOS}/governance/directives"
else
  DIRECTIVE_SOURCE="${AOS_ROOT}/governance/directives"
fi

# Methodology snapshot source (hub: methodology/*.md → _aos/methodology/ in spokes)
if [ "$MODE" = "legacy" ]; then
  METHODOLOGY_SOURCE="${LEGACY_AOS}/methodology"
else
  METHODOLOGY_SOURCE="${AOS_ROOT}/methodology"
fi

# ─── Helpers ─────────────────────────────────────────────────────────────────────

log() { echo "$@"; }
warn() { echo "WARN: $@" >&2; }
fail() { echo "FAIL: $@" >&2; }
report() { REPORT_LINES+=("$1"); }

timestamp() { date "+%Y-%m-%d %H:%M:%S"; }

target_name() {
  local t="$1"
  # Extract project name from path
  echo "$t" | sed 's|.*/Documents/||; s|/_aos/governance||; s|/.*||'
}

# ─── Phase 1: Change Plan (R4(a) — overwrite, not conflict) ──────────────────────
# One-directional source→snapshot propagation: a target that differs from source is
# "to be UPDATED" (overwritten), a missing target is "to be ADDED", and a spoke
# team_*.md with no matching source file is a dissolved team "to be REMOVED". None
# of these is a merge conflict requiring human resolution. The dry-run reports the
# plan and exits 0.
plan_changes() {
  local target="$1"
  local name
  name=$(target_name "$target")

  # team_*.md — UPDATE / ADD
  for src_file in "$SOURCE"/team_*.md; do
    [ -f "$src_file" ] || continue
    local basename tgt_file
    basename=$(basename "$src_file")
    tgt_file="$target/$basename"
    if [ ! -f "$tgt_file" ]; then
      CHANGES_ADD=$((CHANGES_ADD + 1))
      log "  ADD:    $basename → $name"
      report "| $name | $basename | ADD |"
    else
      local src_hash tgt_hash
      src_hash=$(md5_hash "$src_file"); tgt_hash=$(md5_hash "$tgt_file")
      if [ "$src_hash" != "$tgt_hash" ]; then
        CHANGES_UPDATE=$((CHANGES_UPDATE + 1))
        log "  UPDATE: $basename in $name (overwrite — source wins, IR#11)"
        report "| $name | $basename | UPDATE |"
        if [ "$SHOW_DIFF" = true ]; then
          echo "--- diff: $name/$basename ---"; diff -u "$tgt_file" "$src_file" || true; echo "--- end diff ---"; echo ""
        fi
      fi
    fi
  done

  # team_*.md — REMOVE (R4(b)): a dissolved-team file present on the spoke but with
  # no matching source team_*.md is pruned.
  if [ -d "$target" ]; then
    for tgt_file in "$target"/team_*.md; do
      [ -f "$tgt_file" ] || continue
      local tbase
      tbase=$(basename "$tgt_file")
      if [ ! -f "$SOURCE/$tbase" ]; then
        CHANGES_REMOVE=$((CHANGES_REMOVE + 1))
        log "  REMOVE: $tbase in $name (dissolved team — not in hub roster)"
        report "| $name | $tbase | REMOVE (dissolved) |"
      fi
    done
  fi

  # ADR directives — UPDATE / ADD
  if [ -d "$DIRECTIVE_SOURCE" ]; then
    for src_file in "$DIRECTIVE_SOURCE"/ADR*.md; do
      [ -f "$src_file" ] || continue
      local adr_base tgt_d
      adr_base=$(basename "$src_file")
      tgt_d="$target/directives/$adr_base"
      if [ ! -f "$tgt_d" ]; then
        CHANGES_ADD=$((CHANGES_ADD + 1))
        log "  ADD:    directives/$adr_base → $name"
        report "| $name | directives/$adr_base | ADD |"
      else
        local src_hash_d tgt_hash_d
        src_hash_d=$(md5_hash "$src_file"); tgt_hash_d=$(md5_hash "$tgt_d")
        if [ "$src_hash_d" != "$tgt_hash_d" ]; then
          CHANGES_UPDATE=$((CHANGES_UPDATE + 1))
          log "  UPDATE: directives/$adr_base in $name (overwrite — source wins, IR#11)"
          report "| $name | directives/$adr_base | UPDATE |"
          if [ "$SHOW_DIFF" = true ]; then
            echo "--- diff: $name/directives/$adr_base ---"; diff -u "$tgt_d" "$src_file" || true; echo "--- end diff ---"; echo ""
          fi
        fi
      fi
    done
  fi

  # Methodology snapshot — UPDATE / ADD
  if [ -d "$METHODOLOGY_SOURCE" ]; then
    local meth_tgt
    meth_tgt="$(dirname "$target")/methodology"
    for src_file in "$METHODOLOGY_SOURCE"/*.md; do
      [ -f "$src_file" ] || continue
      local meth_base meth_tgt_file
      meth_base=$(basename "$src_file")
      meth_tgt_file="$meth_tgt/$meth_base"
      if [ ! -f "$meth_tgt_file" ]; then
        CHANGES_ADD=$((CHANGES_ADD + 1))
        log "  ADD:    methodology/$meth_base → $name"
        report "| $name | methodology/$meth_base | ADD |"
      else
        local src_hash_m tgt_hash_m
        src_hash_m=$(md5_hash "$src_file"); tgt_hash_m=$(md5_hash "$meth_tgt_file")
        if [ "$src_hash_m" != "$tgt_hash_m" ]; then
          CHANGES_UPDATE=$((CHANGES_UPDATE + 1))
          log "  UPDATE: methodology/$meth_base in $name (overwrite — source wins, IR#11)"
          report "| $name | methodology/$meth_base | UPDATE |"
          if [ "$SHOW_DIFF" = true ]; then
            echo "--- diff: $name/methodology/$meth_base ---"; diff -u "$meth_tgt_file" "$src_file" || true; echo "--- end diff ---"; echo ""
          fi
        fi
      fi
    done
  fi

  return 0
}

# Backward-compatible alias (call sites may still reference detect_conflicts).
detect_conflicts() { plan_changes "$@"; }

# ─── Phase 3: Propagation ───────────────────────────────────────────────────────

propagate_target() {
  local target="$1"
  local name
  name=$(target_name "$target")
  local count=0

  mkdir -p "$target"

  for src_file in "$SOURCE"/team_*.md; do
    local basename
    basename=$(basename "$src_file")
    cp "$src_file" "$target/$basename"
    count=$((count + 1))
  done

  # R4(b) DELETE pass: prune dissolved-team team_*.md left on the spoke (a file with
  # no matching source team_*.md). Reconcile, not just upsert — keeps Check 13 honest.
  local removed=0
  for tgt_file in "$target"/team_*.md; do
    [ -f "$tgt_file" ] || continue
    local tbase
    tbase=$(basename "$tgt_file")
    if [ ! -f "$SOURCE/$tbase" ]; then
      rm -f "$tgt_file"
      removed=$((removed + 1))
      log "  Pruned dissolved team file → $name: $tbase"
      report "| $name | $tbase | REMOVED (dissolved) |"
    fi
  done
  FILES_REMOVED=$((FILES_REMOVED + removed))

  local adr_copied=0
  if [ -d "$DIRECTIVE_SOURCE" ]; then
    mkdir -p "$target/directives"
    for src_file in "$DIRECTIVE_SOURCE"/ADR*.md; do
      [ -f "$src_file" ] || continue
      cp "$src_file" "$target/directives/"
      adr_copied=$((adr_copied + 1))
    done
  fi
  if [ "$adr_copied" -gt 0 ]; then
    count=$((count + adr_copied))
  fi

  # Methodology snapshot propagation (methodology/*.md → _aos/methodology/)
  local meth_copied=0
  if [ -d "$METHODOLOGY_SOURCE" ]; then
    local meth_tgt
    meth_tgt="$(dirname "$target")/methodology"
    mkdir -p "$meth_tgt"
    for src_file in "$METHODOLOGY_SOURCE"/*.md; do
      [ -f "$src_file" ] || continue
      cp "$src_file" "$meth_tgt/"
      meth_copied=$((meth_copied + 1))
    done
  fi
  if [ "$meth_copied" -gt 0 ]; then
    count=$((count + meth_copied))
  fi

  FILES_PROPAGATED=$((FILES_PROPAGATED + count))
  local team_n=$((count - adr_copied - meth_copied))
  log "  Copied → $name: $team_n team_*.md + $adr_copied ADR + $meth_copied methodology (total $count); pruned $removed dissolved"
  report "| $name | $count files (team + directives + methodology), $removed removed | OK |"
}

# ─── Phase 4: Verification ──────────────────────────────────────────────────────

verify_target() {
  local target="$1"
  local name
  name=$(target_name "$target")
  local errors=0

  for src_file in "$SOURCE"/team_*.md; do
    local basename
    basename=$(basename "$src_file")
    local tgt_file="$target/$basename"

    if [ ! -f "$tgt_file" ]; then
      fail "  MISSING: $name/$basename"
      errors=$((errors + 1))
      report "| $name | $basename | MISSING |"
      continue
    fi

    local src_hash tgt_hash
    src_hash=$(md5_hash "$src_file")
    tgt_hash=$(md5_hash "$tgt_file")

    if [ "$src_hash" != "$tgt_hash" ]; then
      fail "  MISMATCH: $name/$basename"
      errors=$((errors + 1))
      report "| $name | $basename | MISMATCH |"
    fi
  done

  if [ -d "$DIRECTIVE_SOURCE" ]; then
    for src_file in "$DIRECTIVE_SOURCE"/ADR*.md; do
      [ -f "$src_file" ] || continue
      local adr_base
      adr_base=$(basename "$src_file")
      local tgt_adr="$target/directives/$adr_base"
      if [ ! -f "$tgt_adr" ]; then
        fail "  MISSING: $name/directives/$adr_base"
        errors=$((errors + 1))
        report "| $name | directives/$adr_base | MISSING |"
        continue
      fi
      local s_ha t_ha
      s_ha=$(md5_hash "$src_file")
      t_ha=$(md5_hash "$tgt_adr")
      if [ "$s_ha" != "$t_ha" ]; then
        fail "  MISMATCH: $name/directives/$adr_base"
        errors=$((errors + 1))
        report "| $name | directives/$adr_base | MISMATCH |"
      fi
    done
  fi

  # Methodology snapshot verification (methodology/*.md → _aos/methodology/)
  if [ -d "$METHODOLOGY_SOURCE" ]; then
    local meth_tgt
    meth_tgt="$(dirname "$target")/methodology"
    for src_file in "$METHODOLOGY_SOURCE"/*.md; do
      [ -f "$src_file" ] || continue
      local meth_base meth_tgt_file
      meth_base=$(basename "$src_file")
      meth_tgt_file="$meth_tgt/$meth_base"
      if [ ! -f "$meth_tgt_file" ]; then
        fail "  MISSING: $name/methodology/$meth_base"
        errors=$((errors + 1))
        report "| $name | methodology/$meth_base | MISSING |"
        continue
      fi
      local s_hm t_hm
      s_hm=$(md5_hash "$src_file")
      t_hm=$(md5_hash "$meth_tgt_file")
      if [ "$s_hm" != "$t_hm" ]; then
        fail "  MISMATCH: $name/methodology/$meth_base"
        errors=$((errors + 1))
        report "| $name | methodology/$meth_base | MISMATCH |"
      fi
    done
  fi

  VERIFICATION_ERRORS=$((VERIFICATION_ERRORS + errors))
  if [ $errors -eq 0 ]; then
    local tc ac mc f
    tc=$(ls "$SOURCE"/team_*.md 2>/dev/null | wc -l | tr -d ' ')
    ac=0
    if [ -d "$DIRECTIVE_SOURCE" ]; then
      for f in "$DIRECTIVE_SOURCE"/ADR*.md; do
        [ -f "$f" ] || continue
        ac=$((ac + 1))
      done
    fi
    mc=0
    if [ -d "$METHODOLOGY_SOURCE" ]; then
      for f in "$METHODOLOGY_SOURCE"/*.md; do
        [ -f "$f" ] || continue
        mc=$((mc + 1))
      done
    fi
    log "  Verified: $name — all files MATCH (team: $tc, ADR: $ac, methodology: $mc)"
    report "| $name | ALL MATCH | team $tc + ADR $ac + methodology $mc |"
  fi

  return $errors
}

# ─── Phase 4b: Git commit + push per spoke ──────────────────────────────────────

git_commit_push_target() {
  local target="$1"
  local name
  name=$(target_name "$target")

  # Derive git root: target = /path/project/_aos/governance → root = /path/project
  local git_root
  git_root=$(dirname "$(dirname "$target")")

  if [ ! -d "$git_root/.git" ]; then
    warn "  Git commit+push: $name — no .git at $git_root, SKIP"
    report "| $name | SKIP (no .git) |"
    return 0
  fi

  # Model B (ADR054): _aos/governance + _aos/methodology are a GIT-IGNORED LOCAL CACHE,
  # refreshed in-place by the copy phase — NEVER committed or pushed into the spoke.
  # Committing/pushing governance onto the spoke's working branch was the root coupling
  # behind every gov-sync collision (nimrod-bio CI block, EyalAmit branch drag, dirty-tree).
  # Audit is carried by the tracked _aos/AOS_GOVERNANCE_VERSION.yaml stamp + the spoke's own
  # tracked-set commit (aos_sync_all.sh Step 3b). This guard short-circuits the legacy
  # commit+push path. Override only for a Model-A in-history domain via AOS_GOV_INHISTORY=1
  # (no such domain exists today — R2/R4 decided Model B fleet-wide).
  if [ "${AOS_GOV_INHISTORY:-0}" != "1" ]; then
    log "  Git commit+push: $name — SKIP (Model B: governance is a git-ignored cache; stamp carries audit)"
    report "| $name | SKIP (Model B cache — not committed) |"
    return 0
  fi

  # Compute git-relative paths for propagated directories
  local gov_rel="_aos/governance"
  local meth_rel="_aos/methodology"

  # Count changed files in the propagated dirs
  local changed
  changed=$(cd "$git_root" && git status --porcelain "$gov_rel" "$meth_rel" 2>/dev/null | grep -c . || true)

  if [ "${changed:-0}" -eq 0 ]; then
    log "  Git commit+push: $name — nothing to commit"
    report "| $name | already up to date |"
    return 0
  fi

  # Stage propagated paths only
  (cd "$git_root" && git add "$gov_rel" "$meth_rel") 2>/dev/null

  # Commit
  local commit_msg="governance(sync): propagate hub governance snapshot — $(date '+%Y-%m-%d')"
  local commit_out commit_rc
  commit_out=$(cd "$git_root" && git commit -m "$commit_msg" 2>&1)
  commit_rc=$?

  if [ $commit_rc -ne 0 ]; then
    fail "  Git commit failed in $name: $commit_out"
    report "| $name | COMMIT FAILED |"
    return 1
  fi

  # NO_PUSH mode: commit locally, never push (single-dev/one-machine default, ADR052).
  # Push is a deliberate backup/deploy action, decoupled from propagation.
  if [ "${NO_PUSH:-1}" = "1" ]; then
    log "  Git commit: $name — committed locally (no-push mode; push deferred)"
    report "| $name | committed (local, no-push) |"
    return 0
  fi

  # Check if any remote exists before attempting push
  local has_remote
  has_remote=$(cd "$git_root" && git remote 2>/dev/null | head -1)
  if [ -z "$has_remote" ]; then
    log "  Git commit+push: $name — committed (no remote configured, push skipped)"
    report "| $name | committed (no remote) |"
    return 0
  fi

  # All network git ops are wrapped in `timeout` + GIT_TERMINAL_PROMPT=0 so a stalled
  # remote or credential prompt can never hang propagation (root cause of the 3× hang).
  local T="$GIT_NET_TIMEOUT"
  local push_out push_rc
  push_out=$(cd "$git_root" && GIT_TERMINAL_PROMPT=0 timeout "$T" git push origin HEAD 2>&1)
  push_rc=$?

  if [ $push_rc -eq 124 ]; then
    fail "  Git push TIMED OUT (${T}s) in $name — push deferred, snapshot is committed locally"
    report "| $name | committed (push timeout — deferred) |"
    return 0  # not fatal: the snapshot is safely committed; push can be retried manually
  fi

  if [ $push_rc -ne 0 ]; then
    # Retry: fetch + rebase onto remote branch, then push — each time-bounded.
    warn "  Git push rejected in $name — retrying with fetch+rebase (≤${T}s each)"
    local current_branch
    current_branch=$(cd "$git_root" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
    (cd "$git_root" && GIT_TERMINAL_PROMPT=0 timeout "$T" git fetch origin \
        && GIT_TERMINAL_PROMPT=0 timeout "$T" git rebase "origin/$current_branch") >/dev/null 2>&1 || true
    push_out=$(cd "$git_root" && GIT_TERMINAL_PROMPT=0 timeout "$T" git push origin HEAD 2>&1)
    push_rc=$?
  fi

  if [ $push_rc -eq 124 ]; then
    fail "  Git push TIMED OUT (${T}s, retry) in $name — push deferred, committed locally"
    report "| $name | committed (push timeout — deferred) |"
    return 0
  fi

  if [ $push_rc -ne 0 ]; then
    fail "  Git push failed in $name: $push_out"
    report "| $name | PUSH FAILED |"
    return 1
  fi

  log "  Git commit+push: $name — DONE"
  report "| $name | committed + pushed |"
  return 0
}

# ─── Phase 5: Validation ────────────────────────────────────────────────────────

validate_target() {
  local target="$1"
  local name
  name=$(target_name "$target")

  # Derive project root from target (strip /_aos/governance)
  local project_root
  project_root=$(echo "$target" | sed 's|/_aos/governance$||')

  # Find validate_aos.sh — prefer the project's own copy, then hub copy
  local val_script=""
  if [ -f "$project_root/_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh" ]; then
    val_script="$project_root/_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh"
  elif [ -f "$VALIDATE_SCRIPT" ]; then
    val_script="$VALIDATE_SCRIPT"
  elif [ -f "$VALIDATE_SCRIPT_AOS" ]; then
    val_script="$VALIDATE_SCRIPT_AOS"
  fi

  if [ -z "$val_script" ]; then
    warn "  validate_aos.sh not found for $name — SKIP"
    report "| $name | SKIP (no validator) |"
    return 0
  fi

  if bash "$val_script" "$project_root" >/dev/null 2>&1; then
    log "  Validation: $name — PASS"
    report "| $name | PASS |"
    return 0
  else
    fail "  Validation: $name — FAIL"
    report "| $name | FAIL |"
    return 1
  fi
}

# ─── Main ────────────────────────────────────────────────────────────────────────

log "=== Governance Propagation $(timestamp) ==="
log "Source: $SOURCE"
log "Mode: $MODE | Dry-run: $DRY_RUN | Diff: $SHOW_DIFF"
log ""

# Verify source exists
if [ ! -d "$SOURCE" ]; then
  fail "Source directory not found: $SOURCE"
  exit 1
fi

SRC_COUNT=$(ls "$SOURCE"/team_*.md 2>/dev/null | wc -l | tr -d ' ')
ADR_SRC_COUNT=0
if [ -d "$DIRECTIVE_SOURCE" ]; then
  for f in "$DIRECTIVE_SOURCE"/ADR*.md; do
    [ -f "$f" ] || continue
    ADR_SRC_COUNT=$((ADR_SRC_COUNT + 1))
  done
else
  warn "ADR directive source not found: $DIRECTIVE_SOURCE — ADR propagation will be skipped"
fi
METH_SRC_COUNT=0
if [ -d "$METHODOLOGY_SOURCE" ]; then
  for f in "$METHODOLOGY_SOURCE"/*.md; do
    [ -f "$f" ] || continue
    METH_SRC_COUNT=$((METH_SRC_COUNT + 1))
  done
else
  warn "Methodology source not found: $METHODOLOGY_SOURCE — methodology propagation will be skipped"
fi
log "Source: $SRC_COUNT team_*.md from $SOURCE"
log "ADR directives: $ADR_SRC_COUNT file(s) from $DIRECTIVE_SOURCE"
log "Methodology docs: $METH_SRC_COUNT file(s) from $METHODOLOGY_SOURCE"
log ""

report "# Governance Propagation Report"
report ""
report "**Date:** $(timestamp)"
report "**Team contracts:** \`$SOURCE\` ($SRC_COUNT files)"
report "**ADR directives:** \`$DIRECTIVE_SOURCE\` ($ADR_SRC_COUNT files)"
report "**Methodology docs:** \`$METHODOLOGY_SOURCE\` ($METH_SRC_COUNT files)"
report "**Mode:** $MODE | Dry-run: $DRY_RUN"
report ""

# ── Phase 1: Change Plan (R4(a) — overwrite, not conflict) ──
log "--- Phase 1: Change Plan (source→snapshot overwrite, IR#11) ---"
report "## Phase 1: Change Plan"
report ""
report "| Target | File | Action |"
report "|--------|------|--------|"

for target in "${TARGETS[@]}"; do
  name=$(target_name "$target")
  if [ ! -d "$target" ]; then
    warn "Target not found: $target — SKIP"
    report "| $name | — | SKIP (dir not found) |"
    TARGETS_SKIPPED=$((TARGETS_SKIPPED + 1))
    continue
  fi
  plan_changes "$target" || true
done

report ""
log ""
log "Change plan: will UPDATE $CHANGES_UPDATE, ADD $CHANGES_ADD, REMOVE $CHANGES_REMOVE file(s) across $(( ${#TARGETS[@]} - TARGETS_SKIPPED )) target(s)."
log ""

# ── Dry-run: always emit propagation manifest (regardless of conflicts) ──
if [ "$DRY_RUN" = true ]; then
  log "--- Dry-run propagation manifest ---"
  log ""
  log "  Team contracts ($SRC_COUNT):"
  for f in "$SOURCE"/team_*.md; do
    [ -f "$f" ] || continue
    log "    → $(basename "$f")"
  done
  log ""
  log "  ADR directives ($ADR_SRC_COUNT):"
  if [ -d "$DIRECTIVE_SOURCE" ]; then
    for f in "$DIRECTIVE_SOURCE"/ADR*.md; do
      [ -f "$f" ] || continue
      log "    → directives/$(basename "$f")"
    done
  fi
  log ""
  log "  Methodology docs ($METH_SRC_COUNT):"
  if [ -d "$METHODOLOGY_SOURCE" ]; then
    for f in "$METHODOLOGY_SOURCE"/*.md; do
      [ -f "$f" ] || continue
      log "    → methodology/$(basename "$f")"
    done
  fi
  log ""
  report "### Propagation manifest"
  report ""
  report "**Team contracts ($SRC_COUNT):**"
  for f in "$SOURCE"/team_*.md; do
    [ -f "$f" ] || continue
    report "- \`$(basename "$f")\`"
  done
  report ""
  report "**ADR directives ($ADR_SRC_COUNT):**"
  if [ -d "$DIRECTIVE_SOURCE" ]; then
    for f in "$DIRECTIVE_SOURCE"/ADR*.md; do
      [ -f "$f" ] || continue
      report "- \`directives/$(basename "$f")\`"
    done
  fi
  report ""
  report "**Methodology docs ($METH_SRC_COUNT):**"
  if [ -d "$METHODOLOGY_SOURCE" ]; then
    for f in "$METHODOLOGY_SOURCE"/*.md; do
      [ -f "$f" ] || continue
      report "- \`methodology/$(basename "$f")\`"
    done
  fi
fi

# ── Dry-run completes here (R4(a)): a differing target is an intended OVERWRITE,
#    not a merge conflict needing resolution. Report the plan + exit 0.
if [ "$DRY_RUN" = true ]; then
  _planned=$((CHANGES_UPDATE + CHANGES_ADD + CHANGES_REMOVE))
  if [ "$_planned" -gt 0 ]; then
    log "Dry-run: $_planned change(s) planned — will update $CHANGES_UPDATE / add $CHANGES_ADD / remove $CHANGES_REMOVE on next live run."
    report ""
    report "## Result: DRY-RUN PLAN — update $CHANGES_UPDATE / add $CHANGES_ADD / remove $CHANGES_REMOVE"
    report ""
    report "These are one-directional source→snapshot OVERWRITES (IR#11), not merge conflicts. Run without --dry-run to apply."
  else
    log "Dry-run: snapshots already match source — nothing to update/add/remove."
    report ""
    report "## Result: DRY-RUN IN-SYNC (0 changes)"
  fi
  if [ -n "$REPORT_FILE" ]; then
    printf '%s\n' "${REPORT_LINES[@]}" > "$REPORT_FILE"
    log "Report written to: $REPORT_FILE"
  fi
  exit 0
fi

# ── Phase 2+3: Propagation (live — dry-run already returned above) ──
{
  log "--- Phase 3: Propagation ---"
  report "## Phase 3: Propagation"
  report ""
  report "| Target | Files | Status |"
  report "|--------|-------|--------|"

  for target in "${TARGETS[@]}"; do
    if [ ! -d "$(dirname "$target")" ]; then
      TARGETS_SKIPPED=$((TARGETS_SKIPPED + 1))
      continue
    fi
    propagate_target "$target"
    TARGETS_OK=$((TARGETS_OK + 1))
  done

  report ""
  log ""
  log "Propagated $FILES_PROPAGATED files to $TARGETS_OK targets ($TARGETS_SKIPPED skipped)"
  log ""

  # ── Phase 4: Verification ──
  log "--- Phase 4: Verification ---"
  report "## Phase 4: Verification"
  report ""
  report "| Target | Status | Files |"
  report "|--------|--------|-------|"

  for target in "${TARGETS[@]}"; do
    if [ ! -d "$target" ]; then
      continue
    fi
    verify_target "$target" || true
  done

  report ""
  log ""

  if [ $VERIFICATION_ERRORS -gt 0 ]; then
    fail "VERIFICATION FAILED: $VERIFICATION_ERRORS mismatches"
    report "## Verification: FAILED ($VERIFICATION_ERRORS errors)"
  else
    log "Verification: ALL TARGETS MATCH"
    report "## Verification: ALL MATCH"
  fi

  log ""

  # ── Phase 4b: Git commit + push ──
  GIT_PUSH_FAILURES=0
  log "--- Phase 4b: Git commit + push ---"
  report ""
  report "## Phase 4b: Git commit + push"
  report ""
  report "| Target | Status |"
  report "|--------|--------|"

  for target in "${TARGETS[@]}"; do
    if [ ! -d "$target" ]; then
      continue
    fi
    git_commit_push_target "$target" || GIT_PUSH_FAILURES=$((GIT_PUSH_FAILURES + 1))
  done

  report ""
  log ""

  if [ $GIT_PUSH_FAILURES -gt 0 ]; then
    fail "GIT PUSH: $GIT_PUSH_FAILURES target(s) failed"
    report "## Git Push: $GIT_PUSH_FAILURES FAILURE(S)"
  else
    log "Git commit+push: ALL TARGETS DONE"
    report "## Git Push: ALL DONE"
  fi

  log ""

  # ── Phase 5: Validation ──
  # AOS_PROPAGATE_ORCHESTRATED=1 (set by aos_sync_all.sh Step 1): spoke self-validation
  # here would run each spoke's own cached validate_aos.sh BEFORE aos_sync_all.sh Step 2
  # has rsynced that spoke's _aos/lean-kit/ tree — checking freshly-propagated
  # governance/methodology against a stale lean-kit cache, which transiently FAILs on
  # every full sync (same applies to the hub's own _aos/lean-kit, refreshed only in
  # Step 4b). aos_sync_all.sh's own Step 4/5 re-validates authoritatively after all
  # propagation phases complete, so this pass is redundant there. Skipping it also lets
  # Phase 5b (hub command-manifest check, gated on VAL_FAILURES==0) run instead of being
  # silently skipped on every orchestrated sync. Standalone/legacy invocations of this
  # script are unaffected — the env var is unset and Phase 5 runs as before.
  log "--- Phase 5: Validation ---"
  report ""
  report "## Phase 5: Validation (validate_aos.sh)"
  report ""
  report "| Target | Result |"
  report "|--------|--------|"

  VAL_FAILURES=0
  if [ "${AOS_PROPAGATE_ORCHESTRATED:-0}" = "1" ]; then
    log "Phase 5: SKIPPED — orchestrated by aos_sync_all.sh (authoritative validation runs in its Step 4/5, after lean-kit sync)"
    report "| (all targets) | SKIP (deferred to aos_sync_all.sh Step 4/5) |"
  else
    for target in "${TARGETS[@]}"; do
      if [ ! -d "$target" ]; then
        continue
      fi
      validate_target "$target" || VAL_FAILURES=$((VAL_FAILURES + 1))
    done
  fi

  report ""
  log ""

  if [ $VAL_FAILURES -gt 0 ]; then
    fail "VALIDATION: $VAL_FAILURES target(s) failed"
    report "## Validation: $VAL_FAILURES FAILURE(S)"
  else
    log "Validation: ALL TARGETS PASS"
    report "## Validation: ALL PASS"
  fi

  # ── Phase 5b: Hub-only — AOS slash commands vs manifest (Team 00 / WP plan 2026-04-15) ──
  VAL_CMD_FAIL=0
  report ""
  report "## Phase 5b: validate_aos_commands.sh (hub only)"
  report ""
  report "| Scope | Result |"
  report "|-------|--------|"
  if [ $VAL_FAILURES -gt 0 ]; then
    log "Skipping Phase 5b — validate_aos.sh reported failures"
    report "| hub | SKIP (Phase 5 failed) |"
  else
    log "--- Phase 5b: AOS command manifest validation (hub) ---"
    CMD_VAL_SCRIPT="$AOS_ROOT/lean-kit/modules/validation-quality/validate_aos_commands.sh"
    if [ ! -f "$CMD_VAL_SCRIPT" ]; then
      CMD_VAL_SCRIPT="$AOS_ROOT/_aos/lean-kit/modules/validation-quality/validate_aos_commands.sh"
    fi
    ID_FILE="$AOS_ROOT/_aos/project_identity.yaml"
    if [ ! -f "$CMD_VAL_SCRIPT" ] || [ ! -f "$ID_FILE" ]; then
      warn "Phase 5b: script or project_identity missing — SKIP"
      report "| hub | SKIP (missing script or project_identity) |"
    else
      is_hub=$(python3 -c "import yaml; d=yaml.safe_load(open('$ID_FILE')); print('yes' if d.get('is_hub') else 'no')" 2>/dev/null || echo no)
      if [ "$is_hub" != "yes" ]; then
        log "Phase 5b: not hub project — SKIP"
        report "| project | SKIP (not hub) |"
      elif bash "$CMD_VAL_SCRIPT" "$AOS_ROOT" >/tmp/aos_cmd_val_$$.log 2>&1; then
        log "Phase 5b: validate_aos_commands.sh — PASS (hub)"
        report "| agents-os (hub) | PASS |"
        rm -f /tmp/aos_cmd_val_$$.log
      else
        fail "Phase 5b: validate_aos_commands.sh — FAIL on hub"
        report "| agents-os (hub) | FAIL |"
        cat /tmp/aos_cmd_val_$$.log >&2 || true
        rm -f /tmp/aos_cmd_val_$$.log
        VAL_CMD_FAIL=1
      fi
    fi
  fi
}

VAL_CMD_FAIL=${VAL_CMD_FAIL:-0}

# ── Phase 6: Project Identity Check (warning only) ──
log "--- Phase 6: project_identity.yaml check ---"
report ""
report "## Phase 6: Project Identity Check"
report ""
report "| Target | project_identity.yaml | Note |"
report "|--------|----------------------|------|"

for target in "${TARGETS[@]}"; do
  if [ ! -d "$target" ]; then
    continue
  fi
  # target = /path/to/project/_aos/governance — project root is two levels up
  project_root=$(dirname "$(dirname "$target")")
  id_file="$project_root/_aos/project_identity.yaml"
  if [ ! -f "$id_file" ]; then
    log "  WARN: $project_root — _aos/project_identity.yaml MISSING (validate_aos.sh Check 12 will FAIL)"
    report "| $project_root | ❌ MISSING | Create manually — not propagated by this script |"
  else
    report "| $project_root | ✅ Present | — |"
  fi
done

log ""

# ── Phase 7: Summary ──
report ""
report "## Summary"
report ""
report "- Source files: $SRC_COUNT"
report "- Files propagated: $FILES_PROPAGATED"
report "- Dissolved-team files removed: $FILES_REMOVED"
report "- Targets propagated: $TARGETS_OK"
report "- Targets skipped: $TARGETS_SKIPPED"
report "- Verification errors: $VERIFICATION_ERRORS"
report "- Git push failures: ${GIT_PUSH_FAILURES:-0}"
report ""
report "---"
report "*Generated by propagate_governance.sh | $(timestamp)*"

# Write report if requested
if [ -n "$REPORT_FILE" ]; then
  mkdir -p "$(dirname "$REPORT_FILE")"
  printf '%s\n' "${REPORT_LINES[@]}" > "$REPORT_FILE"
  log ""
  log "Report written to: $REPORT_FILE"
fi

log ""
log "=== Done ==="

# Exit code (R4(a): dry-run already exited 0 above; a differing snapshot is an
# intended overwrite, never an rc=2 "conflict". Real failures still gate.)
if [ "${VAL_CMD_FAIL:-0}" -gt 0 ]; then
  exit 1
elif [ $VERIFICATION_ERRORS -gt 0 ]; then
  exit 1
elif [ "${GIT_PUSH_FAILURES:-0}" -gt 0 ]; then
  exit 1
else
  exit 0
fi
