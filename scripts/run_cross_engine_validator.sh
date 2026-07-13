#!/usr/bin/env bash
# run_cross_engine_validator.sh — WP4δ (M9-P1-WP2): the orchestrator's reliable cross-engine validator
# runner. Wraps `cursor-agent` (the AOS engine-adapter send() is still a stub, so the orchestrator runs
# the validator itself — memory: feedback_v5_run_cursor_agent) with an EMPTY-OUTPUT / FAILURE detect +
# rerun guard. cursor-agent intermittently returns an empty response, which would otherwise read as a
# no-finding PASS; a timeout or CLI error must likewise NEVER read as a valid verdict. So success is
# strictly: exit code 0 AND non-empty STDOUT (stderr is kept separate and never counted as a response).
#
# Usage:
#   scripts/run_cross_engine_validator.sh <prompt-file> [model] [workspace] [out-file]
#   echo "<prompt>" | scripts/run_cross_engine_validator.sh - [model] [workspace] [out-file]
# Defaults: model=gpt-5.2-codex, workspace=$PWD, out-file=stdout only.
# Exit: 0 = a real (exit-0, non-empty-stdout) response; 3 = still failed after the rerun (loud); 2 = usage.
set -uo pipefail

PROMPT_SRC="${1:-}"
MODEL="${2:-gpt-5.2-codex}"
WORKSPACE="${3:-$PWD}"
OUT_FILE="${4:-}"
RERUNS="${AOS_VALIDATOR_RERUNS:-1}"   # extra attempts after the first failed result

if [ -z "$PROMPT_SRC" ]; then
  echo "USAGE: $0 <prompt-file|-> [model] [workspace] [out-file]" >&2
  exit 2
fi
if [ "$PROMPT_SRC" = "-" ]; then PROMPT="$(cat)"; else PROMPT="$(cat "$PROMPT_SRC")"; fi
if [ -z "${PROMPT//[[:space:]]/}" ]; then echo "empty prompt" >&2; exit 2; fi

if ! command -v cursor-agent >/dev/null 2>&1; then
  echo "cursor-agent not on PATH — cannot run the cross-engine validator" >&2
  exit 2
fi

tmp_out="$(mktemp)"; tmp_err="$(mktemp)"
trap 'rm -f "$tmp_out" "$tmp_err"' EXIT

# One attempt: stdout → $tmp_out, stderr → $tmp_err (kept SEPARATE); returns the real exit code so a
# timeout (124) or CLI error is never mistaken for a response.
_run_attempt() {
  # --trust -f: trust the workspace dir (else cursor-agent prompts "Pass --trust …" and emits NOTHING on
  # an untrusted dir — e.g. a fresh worktree); harmless under --mode plan (read-only). The rerun-guard
  # below treats that prompt-and-exit as a loud failure, never a silent PASS.
  # The `--` before "$PROMPT" is required: any prompt file beginning with `---` (this repo's own
  # _COMMUNICATION/ frontmatter convention) is otherwise misparsed by cursor-agent's CLI as an unknown
  # option instead of a positional argument, failing loud with an empty response every time.
  ( cd "$WORKSPACE" && timeout "${AOS_VALIDATOR_TIMEOUT:-300}" \
      cursor-agent --print --trust -f --model "$MODEL" --mode plan --output-format text -- "$PROMPT" ) \
      >"$tmp_out" 2>"$tmp_err"
}

attempt=0
out=""
while :; do
  _run_attempt; rc=$?
  out="$(cat "$tmp_out")"
  # Success requires BOTH a clean exit AND non-empty stdout. stderr alone is never a valid response.
  if [ "$rc" -eq 0 ] && [ -n "${out//[[:space:]]/}" ]; then break; fi
  empty="$([ -z "${out//[[:space:]]/}" ] && echo yes || echo no)"
  reason="exit=$rc$([ "$rc" -eq 124 ] && echo ' (timeout)') stdout_empty=$empty"
  if [ "$attempt" -ge "$RERUNS" ]; then
    echo "[run_cross_engine_validator] FAILED LOUD after $((attempt + 1)) attempt(s) — $reason (NOT a silent PASS)" >&2
    echo "--- last stderr (tail) ---" >&2; tail -n 5 "$tmp_err" >&2
    exit 3
  fi
  attempt=$((attempt + 1))
  echo "[run_cross_engine_validator] retry ${attempt}/${RERUNS} — $reason" >&2
  sleep "${AOS_VALIDATOR_RERUN_SLEEP:-3}"
done

if [ -n "$OUT_FILE" ]; then printf '%s\n' "$out" > "$OUT_FILE"; fi
printf '%s\n' "$out"
exit 0
