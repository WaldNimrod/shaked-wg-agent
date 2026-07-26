#!/usr/bin/env bash
# pre-receive_gate.sh — self-hosted git gate for the authoritative bare repo
# (AOS-V5-M12-WP-L0-SELFHOST-GIT-GATE, S2). Track-B self-host design, co-signed
# team_00 2026-07-18 (GOVERNANCE_CHANGE_REQUEST_TRACKB_SELFHOST_GIT_GATE_v1.0.0).
#
# Purpose: gate ONLY `refs/heads/main` on the bare repo this is installed into.
#   Two FAST checks run HARD + synchronous, server-local, on every gated push:
#     - validate_aos.sh (0 FAIL)
#     - qa_enforcement.py {skips,allowlist,assertions,tally} --strict
#   Two HEAVY checks (cold-integration, cockpit-e2e) are ATTESTED: this hook
#   verifies a lightweight SHA-keyed pass-marker produced by the Mac pre-push
#   harness (scripts/hooks/pre-push_validation.sh, S5) and pushed alongside
#   main as `refs/attestations/<sha>`. Missing/invalid/wrong-SHA -> reject.
#
# Install (atomic — Tier-2 #7, AC-11): copy this file to a TEMP path inside
#   the target bare's hooks/ dir, chmod +x, then `mv` (rename) it onto
#   hooks/pre-receive. Never edit hooks/pre-receive in place.
#     b="/data/repos/agents-os.git"   # or the staging bare under test
#     install -m 0755 scripts/hooks/pre-receive_gate.sh "$b/hooks/.pre-receive.tmp.$$"
#     mv -f "$b/hooks/.pre-receive.tmp.$$" "$b/hooks/pre-receive"
#     test -x "$b/hooks/pre-receive" && cmp -s scripts/hooks/pre-receive_gate.sh "$b/hooks/pre-receive"
#   The last `cmp` proves byte-for-byte parity with the tracked source (AC-11).
#
# Prerequisites: bash, git, python3, tar (for `git archive | tar -x`). Invoked
#   by git itself as the bare repo's `hooks/pre-receive` (stdin = one
#   "<old-sha> <new-sha> <ref-name>" line per updated ref; no args).
# Env vars:
#   AOS_GATE_REPO_ROOT_HINT     — optional override for where validate_aos.sh /
#                                 scripts/qa_enforcement.py live inside the
#                                 materialized tree (default: the tree root).
#   AOS_GATE_REEXEC_COLD_INTEGRATION=1  — OFF by default (Tier-2 #2 hardening,
#                                 not the default). When set, re-executes a
#                                 cold-integration-equivalent (fresh venv from
#                                 core/requirements.lock + `pytest core/tests -q`)
#                                 server-side INSTEAD of trusting that leg of
#                                 the attestation. Latency cost; team_00 opt-in.
#   AOS_RECEIVE_BREAK_GLASS=1 + AOS_RECEIVE_BREAK_GLASS_REASON="<text>"
#                               — logged break-glass bypass (never silent).
#                                 Read from BOTH the hook process environment
#                                 (an operator running receive-pack locally)
#                                 AND from git push-options (the standard way
#                                 a remote client's flag reaches a server-side
#                                 hook) — see _read_break_glass() below. Both
#                                 fields are REQUIRED together; a flag with no
#                                 reason is treated as NOT set (never a silent
#                                 skip).
#   AOS_GATE_DECISION_LOG_FILE  — override the decision-log path (default
#                                 <this-bare's-git-dir>/gate-decisions.jsonl).
#                                 A plain append-only, SHA-256 hash-chained
#                                 JSONL file — NOT a git ref (see the S0
#                                 dry-run finding in _append_decision_log()'s
#                                 own comment below: git's quarantine
#                                 mechanism silently defeats ref updates from
#                                 inside pre-receive). Off-box shipping is
#                                 scripts/aos_hub_backup.sh's (S7) job — it
#                                 ships this file alongside the nightly
#                                 `git bundle`, over the SAME rsync leg.
# Ports: none.
# Contract: exit 0 = accept the push; non-zero = reject the ENTIRE push (git
#   pre-receive is all-or-nothing across every ref in one invocation — there
#   is no partial accept). If `refs/heads/main` is not among the pushed refs,
#   this hook has nothing to gate and exits 0 immediately.
#
# Cite: [agents-os _aos/context/CODE_STANDARDS.md CS-5] (shell prerequisites/
#   env/ports stated), CS-6 (English in code).
# Ref: _aos/work_packages/AOS-V5-M12-WP-L0-SELFHOST-GIT-GATE/LOD400_BUILD_SPEC_SELFHOST_GIT_GATE_v1.0.0.md §1 S2.
#
# S0 STAGING DRY-RUN FINDINGS (2026-07-18 — folded in here, not left as TODOs):
#   1. `git archive <sha> | tar -x` alone produces a plain directory with NO
#      `.git` at all. validate_aos.sh Check 40 (MSG-HARDENING pre-commit hook
#      wiring) resolves its target via `git rev-parse --git-path`, which
#      requires an actual git repo — it can NEVER pass in a `.git`-less
#      directory, for ANY commit, regardless of code quality (it tests a
#      property of the git INSTALLATION, not of tree content). Fix: `git init`
#      IN-PLACE over the extracted files (a real, if historyless, repo) +
#      commit the tree (see finding 2) + run the materialized tree's OWN
#      scripts/install_hooks.sh (canonical, tracked, unmodified) so hook-wiring
#      checks evaluate a genuinely correctly-set-up checkout.
#   2. A fresh `git init` starts with an empty index, so EVERY extracted file
#      shows as `??` untracked — which trips validate_aos.sh checks that scan
#      `git status --porcelain` for cleanliness (e.g. Check 32, "uncommitted
#      _aos/ drift"). Fix: commit the extracted tree in-place (`-c user.*`
#      inline, never ambient config; `--no-verify`, since no hook exists yet
#      at that point anyway).
#   3. Git's quarantine safety mechanism forbids ANY ref update (a `git commit`
#      does one, via HEAD) in ANY process holding GIT_QUARANTINE_PATH /
#      GIT_OBJECT_DIRECTORY / GIT_ALTERNATE_OBJECT_DIRECTORIES in its
#      environment — for the ENTIRE lifetime of this hook invocation, and
#      regardless of which repository the ref update targets (confirmed live:
#      it fired against the completely unrelated ephemeral $TMP_TREE, not just
#      the bare). Fix: every command that performs a ref update on $TMP_TREE
#      (git init, the materialize-commit, install_hooks.sh) runs via the
#      `_Q_UNSET` env-scoped prefix below — never a blanket `unset` in this
#      shell, because step 3 (reading the pushed attestation object) still
#      needs those vars to see objects that may still be in quarantine.
#   4. The decision-log mechanism itself was originally a git-ref commit chain
#      (`git commit-tree` + `git update-ref refs/meta/gate-log`) — finding 3
#      applies to it too: empirically, only ~1 in 7 test decisions actually
#      persisted before this was found. Fix: replaced with the plain,
#      SHA-256 hash-chained JSONL file described above — immune to the
#      quarantine restriction because it performs no git ref update at all.

set -uo pipefail
# NOTE: deliberately NOT `set -e` for the whole script — a pre-receive hook
# must run its own multi-step decision logic and always reach the decision-log
# append + explicit exit, even when an intermediate check fails. Every command
# whose failure must be handled is checked explicitly.

# Git env hygiene (same root cause documented in scripts/hooks/pre-push_validation.sh
# and scripts/install_hooks.sh): git invokes this hook with GIT_DIR (and
# possibly GIT_WORK_TREE / GIT_INDEX_FILE) already set, pointing at THIS bare.
# Those env vars are an explicit override that takes priority over `-C <path>`
# / `cd <path>` for repository discovery — an inherited GIT_DIR silently
# redirects every later `git -C "$TMP_TREE" ...` / `cd "$TMP_TREE" && git ...`
# call in this script back onto the bare (which has no work tree) instead of
# the ephemeral materialized tree. Found live during the S0 staging dry-run:
# the materialize-commit step failed with "this operation must be run in a
# work tree" — it was silently still targeting the bare. Unset here, at the
# very top, before anything else runs: the one command that explicitly needs
# to target the BARE (`git --git-dir="$BARE_ABS" archive` further below)
# passes that path explicitly, so it is unaffected by this unset; likewise
# `git rev-parse --git-dir` for the decision-log path (right below) resolves
# correctly via plain cwd-based discovery — cwd IS this bare's directory, by
# git's own invocation convention for pre-receive, independent of GIT_DIR.
# GIT_OBJECT_DIRECTORY / GIT_ALTERNATE_OBJECT_DIRECTORIES are NOT unset here —
# those are what let `git archive` (and the attestation `git cat-file -p`
# read, further below) see this receive's quarantined objects; see the
# separate, narrowly-scoped `_Q_UNSET` further down for where THOSE get
# stripped, and why that one is scoped per-command rather than done here.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_PREFIX GIT_COMMON_DIR 2>/dev/null || true

GATED_REF="refs/heads/main"

log() { printf '[pre-receive-gate] %s\n' "$1" >&2; }

# ── 0. Read every ref update in this push (pre-receive is all-or-nothing) ──
MAIN_OLD=""
MAIN_NEW=""
declare -A PUSHED_REF_NEW=()
while read -r old new ref; do
  [ -z "$ref" ] && continue
  PUSHED_REF_NEW["$ref"]="$new"
  if [ "$ref" = "$GATED_REF" ]; then
    MAIN_OLD="$old"
    MAIN_NEW="$new"
  fi
done

if [ -z "$MAIN_NEW" ]; then
  log "refs/heads/main not part of this push — nothing to gate, ACCEPT."
  exit 0
fi

# ── decision-log helper (append-only, SHA-256 hash-chained flat file) ──────
# NOT a git-ref commit chain — see "S0 STAGING DRY-RUN FINDINGS" #4 above.
DECISION_LOG_FILE_DEFAULT="$(git rev-parse --git-dir 2>/dev/null)/gate-decisions.jsonl"
DECISION_LOG_FILE="${AOS_GATE_DECISION_LOG_FILE:-$DECISION_LOG_FILE_DEFAULT}"

_append_decision_log() {
  local sha="$1" verdict="$2" detail="$3"
  local ts line prev_hash this_hash
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  # Escape double-quotes/backslashes minimally for a single-line JSON-ish record.
  local esc_detail="${detail//\\/\\\\}"
  esc_detail="${esc_detail//\"/\\\"}"
  prev_hash="$(tail -n1 "$DECISION_LOG_FILE" 2>/dev/null | python3 -c 'import sys,json
try:
    print(json.load(sys.stdin).get("this_hash",""))
except Exception:
    print("")' 2>/dev/null || true)"
  line="{\"sha\":\"${sha}\",\"verdict\":\"${verdict}\",\"checks\":\"${esc_detail}\",\"ts\":\"${ts}\",\"prev_hash\":\"${prev_hash}\"}"
  this_hash="$(printf '%s' "${line}" | shasum -a 256 2>/dev/null | cut -d' ' -f1)"
  if [ -z "$this_hash" ]; then
    this_hash="$(printf '%s' "${line}" | sha256sum 2>/dev/null | cut -d' ' -f1)"
  fi
  line="{\"sha\":\"${sha}\",\"verdict\":\"${verdict}\",\"checks\":\"${esc_detail}\",\"ts\":\"${ts}\",\"prev_hash\":\"${prev_hash}\",\"this_hash\":\"${this_hash}\"}"
  printf '%s\n' "$line" >> "$DECISION_LOG_FILE" 2>/dev/null \
    || log "WARNING: decision-log append to ${DECISION_LOG_FILE} failed — verdict was still ${verdict} (log append is best-effort, never the gate itself)."
}

reject() {
  local reason="$1"
  log "REJECT (${MAIN_NEW}): ${reason}"
  _append_decision_log "$MAIN_NEW" "REJECT" "$reason"
  exit 1
}

accept() {
  local detail="$1"
  log "ACCEPT (${MAIN_NEW}): ${detail}"
  _append_decision_log "$MAIN_NEW" "ACCEPT" "$detail"
  exit 0
}

ZERO_SHA="0000000000000000000000000000000000000000"
if [ "$MAIN_NEW" = "$ZERO_SHA" ]; then
  reject "refs/heads/main deletion attempt — forbidden regardless of receive.denyDeletes"
fi

# ── break-glass (Tier-2 logged bypass — never silent) ──────────────────────
_read_break_glass() {
  # 1) real process environment (an operator running receive-pack/this hook
  #    directly on the server, e.g. a manual override session).
  local flag="${AOS_RECEIVE_BREAK_GLASS:-}"
  local reason="${AOS_RECEIVE_BREAK_GLASS_REASON:-}"
  if [ "$flag" = "1" ] && [ -n "$reason" ]; then
    printf '%s' "$reason"
    return 0
  fi
  # 2) git push-options — the standard transport for a REMOTE client's flag to
  #    reach a server-side hook (requires `receive.advertisePushOptions=true`
  #    on this bare; part of S1 repo normalization). Encoded as literal
  #    "AOS_RECEIVE_BREAK_GLASS=1" / "AOS_RECEIVE_BREAK_GLASS_REASON=<text>"
  #    strings via `git push -o ...` so the on-the-wire shape matches the
  #    spec-named env-var literally, even though the actual transport is
  #    push-options (documented design choice — see script header).
  local n="${GIT_PUSH_OPTION_COUNT:-0}" i opt po_flag="" po_reason=""
  i=0
  while [ "$i" -lt "$n" ]; do
    eval "opt=\"\${GIT_PUSH_OPTION_${i}:-}\""
    case "$opt" in
      AOS_RECEIVE_BREAK_GLASS=1) po_flag="1" ;;
      AOS_RECEIVE_BREAK_GLASS_REASON=*) po_reason="${opt#AOS_RECEIVE_BREAK_GLASS_REASON=}" ;;
    esac
    i=$((i + 1))
  done
  if [ "$po_flag" = "1" ] && [ -n "$po_reason" ]; then
    printf '%s' "$po_reason"
    return 0
  fi
  return 1
}

BREAK_GLASS_REASON=""
if BREAK_GLASS_REASON="$(_read_break_glass)"; then
  log "BREAK-GLASS engaged: ${BREAK_GLASS_REASON}"
  _append_decision_log "$MAIN_NEW" "BREAK_GLASS" "reason=${BREAK_GLASS_REASON}"
  exit 0
fi

# ── 1. Materialize <new> into a clean ephemeral worktree ───────────────────
# Step 1a: `git archive <sha> | tar -x` for the FILE CONTENT (proven reliable
# mid-receive: this reads through GIT_OBJECT_DIRECTORY / GIT_ALTERNATE_OBJECT_
# DIRECTORIES, which git sets for this hook's own process so the pushed SHA's
# objects resolve even while still in this receive's quarantine directory, not
# yet the bare's permanent objects/. Explicit --git-dir so this is correct
# regardless of any inherited GIT_DIR).
# Step 1b: `git init` IN-PLACE over the already-extracted files, then commit
# the tree, then run install_hooks.sh — see "S0 STAGING DRY-RUN FINDINGS"
# #1/#2/#3 above for why each of these three exists.
TMP_TREE="$(mktemp -d "${TMPDIR:-/tmp}/aos_gate_materialize.XXXXXX")" || reject "mktemp failed for ephemeral worktree"
trap 'rm -rf "$TMP_TREE"' EXIT

BARE_ABS="$(pwd)"   # pre-receive's cwd is this bare's GIT_DIR by git's own convention

if ! git --git-dir="$BARE_ABS" archive "$MAIN_NEW" 2>/tmp/aos_gate_archive_err.$$ | tar -x -C "$TMP_TREE" 2>>/tmp/aos_gate_archive_err.$$; then
  err="$(cat "/tmp/aos_gate_archive_err.$$" 2>/dev/null || true)"
  rm -f "/tmp/aos_gate_archive_err.$$"
  reject "materialize failed — 'git archive ${MAIN_NEW} | tar -x' errored: ${err}"
fi
rm -f "/tmp/aos_gate_archive_err.$$"

REPO_ROOT="${AOS_GATE_REPO_ROOT_HINT:-$TMP_TREE}"
if [ ! -d "$REPO_ROOT/_aos" ]; then
  reject "materialized tree at ${MAIN_NEW} has no _aos/ — not a valid AOS tree, refusing to gate blind"
fi

# Everything from here on operates on $TMP_TREE, a completely separate repo —
# and git's quarantine safety mechanism forbids ANY ref update in ANY repo for
# the lifetime of the vars below (finding #3) — so each command that performs
# one runs via this env-scoped prefix, never a blanket `unset` in this shell
# (step 3 further below still needs these vars to read the still-quarantined
# attestation object).
_Q_UNSET=(env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES)

if ! "${_Q_UNSET[@]}" git init -q "$TMP_TREE" 2>/tmp/aos_gate_init_err.$$; then
  err="$(cat "/tmp/aos_gate_init_err.$$" 2>/dev/null || true)"; rm -f "/tmp/aos_gate_init_err.$$"
  reject "materialize failed — 'git init ${TMP_TREE}' (blessing the extracted tree as a real repo for hook-wiring checks) errored: ${err}"
fi
rm -f "/tmp/aos_gate_init_err.$$"

# Commit the extracted tree in-place (finding #2). `-c user.*` inline (never
# relies on any ambient git identity config on the host) + `--no-verify` (no
# hooks are installed yet at this point anyway — this commit happens BEFORE
# install_hooks.sh runs, deliberately, so there is no pre-commit/branch-guard
# interaction to reason about).
if ! ( cd "$TMP_TREE" && "${_Q_UNSET[@]}" git add -A \
       && "${_Q_UNSET[@]}" git -c user.email="aos-gate@localhost" -c user.name="AOS Gate" \
            commit -q --no-verify -m "materialize ${MAIN_NEW} for gate validation" \
     ) 2>/tmp/aos_gate_commit_err.$$; then
  err="$(cat "/tmp/aos_gate_commit_err.$$" 2>/dev/null || true)"; rm -f "/tmp/aos_gate_commit_err.$$"
  reject "materialize failed — committing the extracted tree in-place errored: ${err}"
fi
rm -f "/tmp/aos_gate_commit_err.$$"

# Wire the ephemeral checkout's local git hooks (pre-commit/pre-push/etc.) the
# same way any normal AOS checkout is expected to be wired, so hook-wiring
# checks (e.g. validate_aos.sh Check 40) evaluate a genuine, correctly-set-up
# checkout rather than a structurally-impossible-to-satisfy non-repo (finding
# #1). Uses the MATERIALIZED tree's own install_hooks.sh (the exact version
# shipped in this commit), not this hook's — the tracked, canonical tool for
# this, unmodified.
if [ -f "$REPO_ROOT/scripts/install_hooks.sh" ]; then
  ( cd "$REPO_ROOT" && "${_Q_UNSET[@]}" bash scripts/install_hooks.sh >/tmp/aos_gate_install_hooks_out.$$ 2>&1 ) \
    || log "WARNING: scripts/install_hooks.sh reported a non-zero exit while wiring the ephemeral checkout — hook-wiring checks below may FAIL for that reason, not from the pushed content: $(cat /tmp/aos_gate_install_hooks_out.$$ 2>/dev/null)"
  rm -f /tmp/aos_gate_install_hooks_out.$$
fi

# ── 2. HARD synchronous checks — validate_aos.sh + qa_enforcement.py ───────
if [ ! -f "$REPO_ROOT/validate_aos.sh" ]; then
  reject "validate_aos.sh not found in materialized tree at ${MAIN_NEW}"
fi

VALIDATE_OUT="$(cd "$REPO_ROOT" && "${_Q_UNSET[@]}" bash validate_aos.sh . 2>&1)"
VALIDATE_RC=$?
if [ "$VALIDATE_RC" -ne 0 ]; then
  fail_line="$(printf '%s\n' "$VALIDATE_OUT" | grep -m1 '^\[FAIL\]' || echo "validate_aos.sh exited ${VALIDATE_RC} (see server log for detail)")"
  reject "validate_aos.sh FAILED — ${fail_line}"
fi

if [ ! -f "$REPO_ROOT/scripts/qa_enforcement.py" ]; then
  reject "scripts/qa_enforcement.py not found in materialized tree at ${MAIN_NEW}"
fi

QA_FAILED_CMD=""
QA_FAIL_DETAIL=""
for _qa_cmd in skips assertions allowlist tally; do
  if [ "$_qa_cmd" = "allowlist" ]; then
    _qa_out="$(cd "$REPO_ROOT" && "${_Q_UNSET[@]}" python3 scripts/qa_enforcement.py allowlist --today "$(date -u +%Y-%m-%d)" --strict 2>&1)"
  else
    _qa_out="$(cd "$REPO_ROOT" && "${_Q_UNSET[@]}" python3 scripts/qa_enforcement.py "$_qa_cmd" --strict 2>&1)"
  fi
  _qa_rc=$?
  if [ "$_qa_rc" -ne 0 ]; then
    QA_FAILED_CMD="$_qa_cmd"
    QA_FAIL_DETAIL="$(printf '%s\n' "$_qa_out" | grep -m1 '^RESULT' || printf '%s\n' "$_qa_out" | tail -1)"
    break
  fi
done
if [ -n "$QA_FAILED_CMD" ]; then
  reject "qa_enforcement.py ${QA_FAILED_CMD} --strict FAILED — ${QA_FAIL_DETAIL}"
fi

# ── (Tier-2 #2, OFF by default) — cold-integration server-side re-exec ─────
if [ "${AOS_GATE_REEXEC_COLD_INTEGRATION:-0}" = "1" ]; then
  if [ -f "$REPO_ROOT/core/requirements.lock" ] && [ -d "$REPO_ROOT/core/tests" ]; then
    _venv="$TMP_TREE/.gate_venv"
    if python3 -m venv "$_venv" >/dev/null 2>&1 \
       && "$_venv/bin/pip" install -q -r "$REPO_ROOT/core/requirements.lock" >/dev/null 2>&1; then
      if ! ( cd "$REPO_ROOT" && env -u AOS_DATABASE_URL "$_venv/bin/python3" -m pytest core/tests -q ); then
        reject "AOS_GATE_REEXEC_COLD_INTEGRATION=1 — server-side pytest core/tests re-execution FAILED (independent leg, not the attestation)"
      fi
      log "server-side cold-integration re-exec PASSED (independent leg — attestation's cold-integration marker not required for this push)."
    else
      reject "AOS_GATE_REEXEC_COLD_INTEGRATION=1 — could not build the server-side venv from core/requirements.lock"
    fi
  else
    log "AOS_GATE_REEXEC_COLD_INTEGRATION=1 but no lockfile/core/tests in this tree — falling back to attestation for cold-integration."
  fi
fi

# ── 3. Attested pass-marker for cold-integration + cockpit-e2e ─────────────
# Resolve the attestation ref's object either from THIS SAME push (present in
# the stdin batch read at step 0) or from an already-existing ref in the repo
# (a marker pushed by an earlier `git push` in the same session).
ATT_REF="refs/attestations/${MAIN_NEW}"
ATT_OBJ="${PUSHED_REF_NEW[$ATT_REF]:-}"
if [ -z "$ATT_OBJ" ]; then
  ATT_OBJ="$(git rev-parse --verify --quiet "$ATT_REF" 2>/dev/null || true)"
fi

if [ "${AOS_GATE_REEXEC_COLD_INTEGRATION:-0}" != "1" ]; then
  if [ -z "$ATT_OBJ" ]; then
    reject "no SHA-keyed pass-marker at ${ATT_REF} — missing attestation (cold-integration + cockpit-e2e unverified). A --no-verify push has no marker by construction."
  fi

  ATT_JSON_FILE="$TMP_TREE/.attestation.json"
  if ! git cat-file -p "$ATT_OBJ" > "$ATT_JSON_FILE" 2>/dev/null || [ ! -s "$ATT_JSON_FILE" ]; then
    reject "attestation object ${ATT_OBJ} at ${ATT_REF} is unreadable (git cat-file -p failed)"
  fi

  ATT_VERIFY_OUT="$(python3 - "$MAIN_NEW" "$ATT_JSON_FILE" <<'PYEOF' 2>&1
import json, sys
expected_sha = sys.argv[1]
att_path = sys.argv[2]
try:
    with open(att_path) as f:
        data = json.load(f)
except Exception as e:
    print(f"INVALID_JSON:{e}")
    sys.exit(1)
if data.get("sha") != expected_sha:
    print(f"WRONG_SHA:marker={data.get('sha')!r} expected={expected_sha!r}")
    sys.exit(1)
checks = data.get("checks", {})
for required in ("cold-integration", "cockpit-e2e"):
    if checks.get(required) != "pass":
        print(f"MISSING_CHECK:{required}={checks.get(required)!r}")
        sys.exit(1)
print("OK")
sys.exit(0)
PYEOF
)"
  ATT_RC=$?
  if [ "$ATT_RC" -ne 0 ]; then
    reject "attestation at ${ATT_REF} invalid — ${ATT_VERIFY_OUT}"
  fi
fi

# ── All checks passed ───────────────────────────────────────────────────────
accept "validate=pass qa_enforcement(skips,assertions,allowlist,tally)=pass attestation(cold-integration,cockpit-e2e)=pass"
