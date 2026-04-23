#!/bin/bash
# propagate_governance.sh — Governance propagation with conflict detection & verification
# =======================================================================================
# Iron Rule #11: Governance flows source → snapshot.
# Source: AOS Project core/governance/ → all spoke _aos/governance/ targets.
#
# Usage:
#   propagate_governance.sh --all                     # propagate to all registered targets
#   propagate_governance.sh --all --diff              # show diffs before propagating
#   propagate_governance.sh --all --dry-run           # detect conflicts only, don't copy
#   propagate_governance.sh --all --report FILE.md    # generate markdown report
#   propagate_governance.sh <aos_path> <spoke_path>   # legacy single-target mode
#
# Exit codes:
#   0 = success (all targets propagated and verified)
#   1 = fatal error
#   2 = conflicts detected (in --dry-run mode)
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
    echo "   Non-AOS teams must file GOVERNANCE_CHANGE_REQUEST — see methodology/AOS_GOVERNANCE_UPDATE_PROCEDURE_v1.1.0.md" >&2
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

# Registered spoke targets (self-snapshot + spoke projects)
TARGETS=(
  "$AOS_ROOT/_aos/governance"
  "/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject/_aos/governance"
  "/Users/nimrod/Documents/AOS-Sandbox-Lean/_aos/governance"
  "/Users/nimrod/Documents/AOS-Sandbox-Full/_aos/governance"
  "/Users/nimrod/Documents/Eyal Amit/EyalAmit.co.il-2026/_aos/governance"
  "/Users/nimrod/Documents/SmallFarmsAgents/_aos/governance"
  "/Users/nimrod/Documents/shaked-wg-agent/_aos/governance"
  "/Users/nimrod/Documents/israel Microgreens/IsraelMicrogreens-BlenderV2-Project/_aos/governance"
  "/Users/nimrod/Documents/HobbitHome/_aos/governance"
  "/Users/nimrod/Documents/nimrod-book/_aos/governance"
)

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
REPORT_FILE=""
LEGACY_AOS=""
LEGACY_SPOKE=""

CONFLICTS_FOUND=0
FILES_PROPAGATED=0
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
    --report)    REPORT_FILE="${2:?--report requires a file path}"; shift 2 ;;
    --help|-h)
      echo "Usage: propagate_governance.sh [--all] [--diff] [--dry-run] [--report FILE]"
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

# Legacy mode: override SOURCE and TARGETS from positional args
if [ "$MODE" = "legacy" ]; then
  if [ -z "$LEGACY_AOS" ] || [ -z "$LEGACY_SPOKE" ]; then
    echo "Usage: propagate_governance.sh <aos_project_path> <spoke_project_path>"
    echo "   or: propagate_governance.sh --all [--diff] [--dry-run] [--report FILE]"
    exit 1
  fi
  SOURCE="$LEGACY_AOS/core/governance"
  TARGETS=("$LEGACY_SPOKE/_aos/governance")
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

# ─── Phase 1: Conflict Detection ────────────────────────────────────────────────

detect_conflicts() {
  local target="$1"
  local name
  name=$(target_name "$target")
  local conflicts=0

  for src_file in "$SOURCE"/team_*.md; do
    local basename
    basename=$(basename "$src_file")
    local tgt_file="$target/$basename"

    if [ ! -f "$tgt_file" ]; then
      continue  # new file, no conflict possible
    fi

    local src_hash tgt_hash
    src_hash=$(md5_hash "$src_file")
    tgt_hash=$(md5_hash "$tgt_file")

    if [ "$src_hash" != "$tgt_hash" ]; then
      CONFLICTS_FOUND=$((CONFLICTS_FOUND + 1))
      conflicts=$((conflicts + 1))
      log "  CONFLICT: $basename in $name (source=$src_hash target=$tgt_hash)"
      report "| $name | $basename | $src_hash | $tgt_hash | CONFLICT |"

      if [ "$SHOW_DIFF" = true ]; then
        echo "--- diff: $name/$basename ---"
        diff -u "$tgt_file" "$src_file" || true
        echo "--- end diff ---"
        echo ""
      fi
    fi
  done

  return $conflicts
}

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

  FILES_PROPAGATED=$((FILES_PROPAGATED + count))
  log "  Copied $count files → $name"
  report "| $name | $count files | OK |"
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

  VERIFICATION_ERRORS=$((VERIFICATION_ERRORS + errors))
  if [ $errors -eq 0 ]; then
    log "  Verified: $name — all files MATCH"
    report "| $name | ALL MATCH | $(ls "$SOURCE"/team_*.md | wc -l | tr -d ' ') files |"
  fi

  return $errors
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
log "Source files: $SRC_COUNT"
log ""

report "# Governance Propagation Report"
report ""
report "**Date:** $(timestamp)"
report "**Source:** \`$SOURCE\` ($SRC_COUNT files)"
report "**Mode:** $MODE | Dry-run: $DRY_RUN"
report ""

# ── Phase 1: Conflict Detection ──
log "--- Phase 1: Conflict Detection ---"
report "## Phase 1: Conflict Detection"
report ""
report "| Target | File | Source Hash | Target Hash | Status |"
report "|--------|------|-------------|-------------|--------|"

for target in "${TARGETS[@]}"; do
  name=$(target_name "$target")
  if [ ! -d "$target" ]; then
    warn "Target not found: $target — SKIP"
    report "| $name | — | — | — | SKIP (dir not found) |"
    TARGETS_SKIPPED=$((TARGETS_SKIPPED + 1))
    continue
  fi
  detect_conflicts "$target" || true
done

report ""
log ""
log "Conflicts found: $CONFLICTS_FOUND"
log ""

if [ $CONFLICTS_FOUND -gt 0 ] && [ "$DRY_RUN" = true ]; then
  log "Dry-run mode — stopping. Resolve conflicts before propagating."
  report "## Result: CONFLICTS DETECTED ($CONFLICTS_FOUND)"
  report ""
  report "Resolve conflicts before propagating. Use \`--diff\` to see details."

  # Write report if requested
  if [ -n "$REPORT_FILE" ]; then
    printf '%s\n' "${REPORT_LINES[@]}" > "$REPORT_FILE"
    log "Report written to: $REPORT_FILE"
  fi

  exit 2
fi

# ── Phase 2+3: Propagation ──
if [ "$DRY_RUN" = true ]; then
  log "Dry-run mode — no conflicts, nothing to propagate."
  report "## Result: DRY-RUN CLEAN (0 conflicts)"
else
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

  # ── Phase 5: Validation ──
  log "--- Phase 5: Validation ---"
  report ""
  report "## Phase 5: Validation (validate_aos.sh)"
  report ""
  report "| Target | Result |"
  report "|--------|--------|"

  VAL_FAILURES=0
  for target in "${TARGETS[@]}"; do
    if [ ! -d "$target" ]; then
      continue
    fi
    validate_target "$target" || VAL_FAILURES=$((VAL_FAILURES + 1))
  done

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
fi

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
report "- Conflicts detected: $CONFLICTS_FOUND"
report "- Targets propagated: $TARGETS_OK"
report "- Targets skipped: $TARGETS_SKIPPED"
report "- Verification errors: $VERIFICATION_ERRORS"
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

# Exit code
if [ "${VAL_CMD_FAIL:-0}" -gt 0 ]; then
  exit 1
elif [ $VERIFICATION_ERRORS -gt 0 ]; then
  exit 1
elif [ $CONFLICTS_FOUND -gt 0 ] && [ "$DRY_RUN" = true ]; then
  exit 2
else
  exit 0
fi
