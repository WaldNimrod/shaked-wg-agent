#!/bin/bash
# archive_gate_artifacts.sh — Archive gate artifacts for a completed WP
# V316 Deliverable D1

set -uo pipefail

# 1. usage() — print usage to stderr, exit 1
usage() {
  cat >&2 <<EOF
usage: archive_gate_artifacts.sh <comm_dir> <wp_id> [--dry-run]

Arguments:
  comm_dir    Communication directory (must exist)
  wp_id       Work package ID (non-empty string)
  --dry-run   Optional: preview changes without modifying files
EOF
  exit 1
}

# 2. parse_args() — parse COMM_DIR, WP_ID, --dry-run flag
parse_args() {
  if [[ $# -lt 2 ]]; then
    usage
  fi

  COMM_DIR="$1"
  WP_ID="$2"
  DRY_RUN=0

  # Check if COMM_DIR is a directory
  if [[ ! -d "$COMM_DIR" ]]; then
    echo "Error: comm_dir '$COMM_DIR' does not exist or is not a directory" >&2
    exit 1
  fi

  # Check if WP_ID is non-empty
  if [[ -z "$WP_ID" ]]; then
    echo "Error: wp_id must be non-empty" >&2
    exit 1
  fi

  # Check for --dry-run flag
  if [[ $# -eq 3 && "$3" == "--dry-run" ]]; then
    DRY_RUN=1
  elif [[ $# -gt 3 ]]; then
    usage
  fi
}

# 3. find_wp_artifacts(team_dir, wp_id) — find files matching WP ID (non-recursive, top-level only)
find_wp_artifacts() {
  local team_dir="$1"
  local wp_id="$2"
  local artifacts=()

  # Match patterns: MANDATE_*WP_ID*, VERDICT_*WP_ID*, ROUTING_*WP_ID*, QA_VERDICT_*WP_ID*, RESUBMISSION_*WP_ID*, HANDOFF_*WP_ID*
  # Do NOT descend into _archive/ subdirs
  if [[ ! -d "$team_dir" ]]; then
    echo "${artifacts[@]}"
    return
  fi

  while IFS= read -r -d '' file; do
    artifacts+=("$file")
  done < <(find "$team_dir" -maxdepth 1 -type f \( \
    -name "MANDATE_*${wp_id}*" \
    -o -name "VERDICT_*${wp_id}*" \
    -o -name "ROUTING_*${wp_id}*" \
    -o -name "QA_VERDICT_*${wp_id}*" \
    -o -name "RESUBMISSION_*${wp_id}*" \
    -o -name "HANDOFF_*${wp_id}*" \
  \) -print0)

  printf '%s\n' "${artifacts[@]}"
}

# 4. ensure_archive_dir(team_dir, wp_id) — create _archive/ and _archive/WP_ID/ dirs
ensure_archive_dir() {
  local team_dir="$1"
  local wp_id="$2"
  local archive_dir="${team_dir}/_archive"
  local wp_archive_dir="${archive_dir}/${wp_id}"

  if [[ $DRY_RUN -eq 1 ]]; then
    if [[ ! -d "$archive_dir" ]]; then
      echo "[MKDIR] ${archive_dir}"
    fi
    if [[ ! -d "$wp_archive_dir" ]]; then
      echo "[MKDIR] ${wp_archive_dir}"
    fi
  else
    mkdir -p "$wp_archive_dir"
  fi
}

# 5. move_artifacts(team_dir, wp_id) — move artifacts, track MOVE_COUNT
move_artifacts() {
  local team_dir="$1"
  local wp_id="$2"
  local wp_archive_dir="${team_dir}/_archive/${wp_id}"
  local move_count=0

  local artifacts=()
  while IFS= read -r line; do
    [[ -n "$line" ]] && artifacts+=("$line")
  done < <(find_wp_artifacts "$team_dir" "$wp_id")

  for artifact in "${artifacts[@]}"; do
    local basename
    basename=$(basename "$artifact")
    local dest="${wp_archive_dir}/${basename}"

    # If dest exists → [SKIP]
    if [[ -e "$dest" ]]; then
      echo "[SKIP] ${basename} → _archive/${wp_id}/"
      continue
    fi

    # If dry-run → [DRY-RUN]
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "[DRY-RUN] ${basename} → _archive/${wp_id}/"
      ((move_count++))
      continue
    fi

    # Else mv and print [MOVE]
    mv "$artifact" "$dest"
    echo "[MOVE] ${basename} → _archive/${wp_id}/"
    ((move_count++))
  done

  MOVE_COUNT=$move_count
}

# 6. enforce_cap(team_dir) — maintain ≤20 subdirs in _archive/, move oldest to _archive/_deep/
enforce_cap() {
  local team_dir="$1"
  local archive_dir="${team_dir}/_archive"
  local deep_dir="${archive_dir}/_deep"
  local cap_count=0

  if [[ ! -d "$archive_dir" ]]; then
    CAP_COUNT=$cap_count
    return
  fi

  # Count subdirs in _archive/ (excluding _deep/)
  local subdirs
  subdirs=$(find "$archive_dir" -maxdepth 1 -type d ! -name "_archive" ! -name "_deep" | wc -l)

  # If >20, move oldest to _archive/_deep/
  while [[ $subdirs -gt 20 ]]; do
    # Get oldest subdir (sorted by mod time newest-first, so last is oldest)
    local oldest
    oldest=$(ls -1dt "$archive_dir"/*/ 2>/dev/null | tail -1 | sed 's:/$::')

    if [[ -z "$oldest" || ! -d "$oldest" ]]; then
      break
    fi

    # Create _deep/ if needed
    if [[ $DRY_RUN -eq 1 ]]; then
      if [[ ! -d "$deep_dir" ]]; then
        echo "[MKDIR] ${deep_dir}"
      fi
      echo "[DRY-RUN] mv $(basename "$oldest") → _archive/_deep/"
    else
      mkdir -p "$deep_dir"
      mv "$oldest" "$deep_dir/" || break
      echo "[MOVE] $(basename "$oldest") → _archive/_deep/"
    fi

    ((cap_count++))
    ((subdirs--))
  done

  CAP_COUNT=$cap_count
}

# 7. main() — iterate team_*/ dirs, call find/ensure/move/enforce, print summary
main() {
  parse_args "$@"

  echo "Archiving artifacts for: ${WP_ID}"

  local total_moves=0
  local total_caps=0

  # Iterate through team_*/ directories
  for team_dir in "$COMM_DIR"/team_*/; do
    if [[ ! -d "$team_dir" ]]; then
      continue
    fi

    find_wp_artifacts "$team_dir" "$WP_ID" > /dev/null
    ensure_archive_dir "$team_dir" "$WP_ID"
    move_artifacts "$team_dir" "$WP_ID"
    enforce_cap "$team_dir"

    total_moves=$((total_moves + MOVE_COUNT))
    total_caps=$((total_caps + CAP_COUNT))
  done

  echo "─────────────────────────────────────"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "ARCHIVE (dry-run): ${total_moves} files moved, ${total_caps} entries capped to _deep/"
  else
    echo "ARCHIVE: ${total_moves} files moved, ${total_caps} entries capped to _deep/"
  fi

  exit 0
}

main "$@"
