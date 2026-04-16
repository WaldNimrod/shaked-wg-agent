#!/bin/bash
# idea_groom.sh -- Grooming report for ideas.json
# Part of AOS lean-kit validation-quality module
#
# USAGE: idea_groom.sh <ideas_json> [--format json|text]
#
# EXIT CODES:
#   0  No issues found
#   1  Issues found (report generated)
#   2  Invalid arguments or missing file
#
# DEPENDENCIES: jq (>= 1.6)
set -euo pipefail
shopt -u histexpand 2>/dev/null || true

# --- Dependency check ---
if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required but not found. Install via: brew install jq" >&2
  exit 2
fi

# --- Helper functions ---

find_duplicates() {
  jq -r '.[] | select(.status == "open") |
    { id: .id, title: .title,
      norm: (.title | ascii_downcase | gsub("[^a-z0-9]"; "")) }' "$1" |
  jq -s 'group_by(.norm) | map(select(length > 1)) |
    .[] | . as $group |
    { type: "duplicate",
      ids: [.[] | .id],
      titles: [.[] | .title] }'
}

find_stale() {
  local cutoff
  cutoff=$(date -u -d '30 days ago' '+%Y-%m-%dT%H:%M:%S' 2>/dev/null || \
           date -u -v-30d '+%Y-%m-%dT%H:%M:%S')
  jq --arg cutoff "$cutoff" -r '.[] |
    select(.status == "open" and .created_at < $cutoff) |
    { type: "stale", id: .id, title: .title, created_at: .created_at }' "$1"
}

find_missing_fields() {
  jq -r '.[] |
    select(.status == "open") | . as $idea |
    (
      (if ($idea.title == null or $idea.title == "") then ["title"] else [] end) +
      (if (($idea.description == null or $idea.description == "") and
           ($idea.notes == null or $idea.notes == "")) then ["description"] else [] end) +
      (if ($idea.urgency == null or $idea.urgency == "") then ["urgency"] else [] end)
    ) as $missing |
    if ($missing | length > 0) then
      { type: "missing_fields", id: $idea.id, title: ($idea.title // "(no title)"),
        missing: $missing }
    else
      empty
    end' "$1"
}

find_closed_no_delivery() {
  jq -r '.[] |
    select(.status == "closed" and .closed_result == "fulfilled" and
           (.delivery_ref == null or .delivery_ref == "")) |
    { type: "closed_no_delivery", id: .id, title: .title,
      closed_result: .closed_result }' "$1"
}

format_text_output() {
  local ideas_file="$1"
  local duplicates="$2"
  local stale="$3"
  local missing="$4"
  local closed_no_delivery="$5"

  local total_ideas
  total_ideas=$(jq '. | length' "$ideas_file")

  local dup_count stale_count missing_count closed_count
  dup_count=$(echo "$duplicates" | jq -s 'length')
  stale_count=$(echo "$stale" | jq -s 'length')
  missing_count=$(echo "$missing" | jq -s 'length')
  closed_count=$(echo "$closed_no_delivery" | jq -s 'length')

  echo "Grooming report for: $ideas_file ($total_ideas ideas)"
  echo "-------------------------------------"

  if [ "$dup_count" -gt 0 ]; then
    echo "DUPLICATES (normalized exact match):"
    echo "$duplicates" | jq -r '.[] | "\(.ids | join(", ")) = \(.titles | join(", "))"' | sed 's/^/  /'
    echo ""
  fi

  if [ "$stale_count" -gt 0 ]; then
    echo "STALE (open > 30 days, no activity):"
    echo "$stale" | jq -r '.[] | "\(.id) \"\(.title)\" -- opened \(.created_at) (30+ days ago)"' | sed 's/^/  /'
    echo ""
  fi

  if [ "$missing_count" -gt 0 ]; then
    echo "MISSING FIELDS:"
    echo "$missing" | jq -r '.[] | "\(.id) -- missing: \(.missing | join(", "))"' | sed 's/^/  /'
    echo ""
  fi

  if [ "$closed_count" -gt 0 ]; then
    echo "CLOSED WITHOUT delivery_ref:"
    echo "$closed_no_delivery" | jq -r '.[] | "\(.id) -- closed_result: \(.closed_result), delivery_ref: null"' | sed 's/^/  /'
    echo ""
  fi

  echo "-------------------------------------"
  echo "SUMMARY: $dup_count duplicate, $stale_count stale, $missing_count missing fields, $closed_count missing delivery_ref"
}

format_json_output() {
  local ideas_file="$1"
  local duplicates="$2"
  local stale="$3"
  local missing="$4"
  local closed_no_delivery="$5"

  local total_ideas
  total_ideas=$(jq '. | length' "$ideas_file")

  local dup_count stale_count missing_count closed_count
  dup_count=$(echo "$duplicates" | jq -s 'length')
  stale_count=$(echo "$stale" | jq -s 'length')
  missing_count=$(echo "$missing" | jq -s 'length')
  closed_count=$(echo "$closed_no_delivery" | jq -s 'length')

  local has_issues="false"
  if [ "$((dup_count + stale_count + missing_count + closed_count))" -gt 0 ]; then
    has_issues="true"
  fi

  # Emit JSON output
  printf '{"file":"%s","total_ideas":%d,"issues":{"duplicates":%s,"stale":%s,"missing_fields":%s,"closed_no_delivery":%s},"summary":{"duplicates":%d,"stale":%d,"missing_fields":%d,"closed_no_delivery":%d},"has_issues":true}\n' \
    "$ideas_file" "$total_ideas" "$duplicates" "$stale" "$missing" "$closed_no_delivery" \
    "$dup_count" "$stale_count" "$missing_count" "$closed_count"
}

run_checks() {
  local ideas_file="$1"
  local format="$2"

  # _to_array: convert jq -r stream (newline-separated JSON objects) to a JSON array.
  # Empty input → []. Works on bash 3.2+ (no mapfile needed).
  _to_array() { [[ -z "$1" ]] && echo '[]' || printf '%s\n' "$1" | jq -sc '.'; }

  local duplicates stale missing closed_no_delivery
  duplicates=$(_to_array "$(find_duplicates "$ideas_file" 2>/dev/null)")
  stale=$(_to_array "$(find_stale "$ideas_file" 2>/dev/null)")
  missing=$(_to_array "$(find_missing_fields "$ideas_file" 2>/dev/null)")
  closed_no_delivery=$(_to_array "$(find_closed_no_delivery "$ideas_file" 2>/dev/null)")

  local dup_count stale_count missing_count closed_count
  dup_count=$(echo "$duplicates" | jq 'length')
  stale_count=$(echo "$stale" | jq 'length')
  missing_count=$(echo "$missing" | jq 'length')
  closed_count=$(echo "$closed_no_delivery" | jq 'length')

  local total_issues=$((dup_count + stale_count + missing_count + closed_count))

  if [ "$format" = "json" ]; then
    format_json_output "$ideas_file" "$duplicates" "$stale" "$missing" "$closed_no_delivery"
  else
    format_text_output "$ideas_file" "$duplicates" "$stale" "$missing" "$closed_no_delivery"
  fi

  if [ "$total_issues" -gt 0 ]; then
    exit 1
  else
    exit 0
  fi
}

usage() {
  cat >&2 <<EOF
Usage: idea_groom.sh <ideas_json> [--format json|text]

  <ideas_json>   Path to ideas.json file
  --format       Output format: json or text (default: text)

Exit codes:
  0  No issues found
  1  Issues found (report generated)
  2  Invalid arguments or missing file
EOF
}

main() {
  if [ $# -lt 1 ]; then usage; exit 2; fi

  local ideas_file="$1"
  local format="text"

  shift
  while [ $# -gt 0 ]; do
    case "$1" in
      --format)
        if [ $# -lt 2 ]; then
          echo "Error: --format requires an argument" >&2
          exit 2
        fi
        format="$2"
        shift 2
        ;;
      *)
        echo "Unknown option: $1" >&2
        exit 2
        ;;
    esac
  done

  if [ ! -f "$ideas_file" ]; then
    echo "Error: File not found: $ideas_file" >&2
    exit 2
  fi

  run_checks "$ideas_file" "$format"
}

main "$@"
