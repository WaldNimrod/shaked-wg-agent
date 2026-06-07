#!/usr/bin/env bash
# aos_governance_bootstrap.sh — idempotent Tier-A governance cache hydrator (Model B / ADR054).
#
# Under Model B, _aos/{governance,methodology,lean-kit} are a GIT-IGNORED local cache.
# A fresh clone / cold CI has no governance until first sync — this script is step 0 of
# any AOS op: it hydrates the cache from the hub and writes the tracked version stamp.
#
# Prereqs: git, rsync (local hub) OR git-archive support (remote hub URL). Ports: none.
# Env: AOS_HUB_ROOT (path or url, optional override), AOS_HUB_REF (default main, URL path),
#      ACTOR (recorded in stamp).
#
# Usage: aos_governance_bootstrap.sh [--repo <path>] [--hub <path|url>] [--force]
set -uo pipefail

TIER_A=(governance methodology lean-kit)
REPO="."; HUB=""; FORCE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --repo)  REPO="$2"; shift 2;;
    --hub)   HUB="$2";  shift 2;;
    --force) FORCE=1;   shift;;
    -h|--help) echo "usage: aos_governance_bootstrap.sh [--repo <path>] [--hub <path|url>] [--force]"; exit 0;;
    *) echo "[aos-bootstrap] unknown arg: $1" >&2; exit 2;;
  esac
done

REPO="$(cd "$REPO" 2>/dev/null && pwd)" || { echo "[aos-bootstrap] FATAL: bad --repo path" >&2; exit 2; }
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/aos_gov_stamp.sh
. "$SCRIPT_DIR/lib/aos_gov_stamp.sh"

is_url() { printf '%s' "$1" | grep -qE '://|@[^/]+:'; }

# ── Hub-source resolution (NORMATIVE order — _aos/projects.yaml is HUB-ONLY, absent on spokes) ──
resolve_hub() {
  [ -n "$HUB" ]                 && { echo "$HUB"; return 0; }            # 1. --hub flag
  [ -n "${AOS_HUB_ROOT:-}" ]    && { echo "$AOS_HUB_ROOT"; return 0; }   # 2. AOS_HUB_ROOT env
  # 3. remote/CI git-archive is selected when the resolved hub is a URL (see hydrate()).
  [ -f "$REPO/_aos/projects.yaml" ] && { echo "$REPO"; return 0; }       # 4. on the hub ONLY
  return 1
}

HUB_SRC="$(resolve_hub)" || {
  echo "[aos-bootstrap] FATAL: cannot resolve hub source. Provide one of:" >&2
  echo "    --hub <path|url>   |   AOS_HUB_ROOT=<path|url>   |   run on the hub (has _aos/projects.yaml)" >&2
  exit 3
}

all_dirs_present() { for d in "${TIER_A[@]}"; do [ -d "$REPO/_aos/$d" ] || return 1; done; return 0; }

# ── Idempotency: skip when cache present and stamp matches hub HEAD (local hub only) ──
if [ "$FORCE" -eq 0 ] && [ -f "$REPO/_aos/AOS_GOVERNANCE_VERSION.yaml" ] && all_dirs_present; then
  if ! is_url "$HUB_SRC" && git -C "$HUB_SRC" rev-parse HEAD >/dev/null 2>&1; then
    hub_head="$(git -C "$HUB_SRC" rev-parse HEAD)"
    cur="$(awk '/^hub_sha:/{print $2; exit}' "$REPO/_aos/AOS_GOVERNANCE_VERSION.yaml")"
    if [ "$cur" = "$hub_head" ]; then
      echo "[aos-bootstrap] up-to-date (hub_sha=${cur:0:12}); no-op"
      exit 0
    fi
  fi
fi

# ── Hydrate Tier-A into the (git-ignored) cache ──
hydrate() {
  local hub="$1" d
  for d in "${TIER_A[@]}"; do
    if is_url "$hub"; then
      local ref="${AOS_HUB_REF:-main}"
      git archive --remote="$hub" "$ref" "_aos/$d" 2>/dev/null | tar -x -C "$REPO" || return 1
    elif [ -d "$hub/_aos/$d" ] && [ -n "$(ls -A "$hub/_aos/$d" 2>/dev/null)" ]; then
      # Normal case (spoke / worktree): hub's rendered snapshot is present → copy it.
      mkdir -p "$REPO/_aos/$d"
      rsync -a --delete "$hub/_aos/$d/" "$REPO/_aos/$d/" || return 1
    elif [ "$d" = "lean-kit" ] && [ -d "$hub/lean-kit" ]; then
      # Hub self-hydrate: _aos/lean-kit is a clean 1:1 mirror of the source lean-kit/.
      mkdir -p "$REPO/_aos/$d"
      rsync -a --delete --exclude=.git --exclude=.DS_Store --exclude=__pycache__ "$hub/lean-kit/" "$REPO/_aos/$d/" || return 1
    else
      # _aos/governance and _aos/methodology are COMPOSITE renders (core/governance team contracts +
      # governance/directives/ ADRs; curated methodology) — they cannot be self-hydrated by a single
      # rsync on a cold HUB. Warn + continue (non-fatal). validate_aos.sh tolerates the absent cache
      # (cold-checkout) and advises bootstrap; the proper render is scripts/aos_sync_all.sh.
      echo "[aos-bootstrap] WARN: _aos/$d unavailable at $hub and not self-renderable — run scripts/aos_sync_all.sh (hub render) or pass --hub <hydrated source> (spoke)." >&2
      HYDRATE_INCOMPLETE=1
    fi
  done
}

HYDRATE_INCOMPLETE=0
hydrate "$HUB_SRC" || { echo "[aos-bootstrap] FATAL: hydrate failed from $HUB_SRC" >&2; exit 4; }
write_gov_stamp "$REPO" "$HUB_SRC" "${ACTOR:-bootstrap}"
if [ "${HYDRATE_INCOMPLETE:-0}" -eq 1 ]; then
  echo "[aos-bootstrap] PARTIAL: hydrated what was available from ${HUB_SRC} → ${REPO}/_aos/ (+ stamp). Composite caches (governance/methodology) need scripts/aos_sync_all.sh or a hydrated --hub."
  exit 0
fi
echo "[aos-bootstrap] hydrated Tier-A governance cache from ${HUB_SRC} → ${REPO}/_aos/ (+ stamp)"
exit 0
