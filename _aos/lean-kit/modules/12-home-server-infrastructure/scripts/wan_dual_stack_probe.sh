#!/bin/bash
# wan_dual_stack_probe.sh — Spoke-side WAN dual-stack health probe
# =================================================================
# Authority: ADR048 + IR#15 + lean-kit/.../WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md §8
# Audience:  per-spoke team_99 (run on the spoke's own server, NOT on the hub).
# Refresh:   _aos/server_dual_stack_status.json — read by validate_aos.sh Check 45.
#
# What this probe does:
#   1. Tests IPv4 + IPv6 outbound reachability (curl).
#   2. Probes for ISP-side NAT64 (dig AAAA ipv4only.arpa).
#   3. Detects whether clatd is running on the host.
#   4. Infers the canonical matrix scenario (A–F or "none") per CANON §7.
#   5. Writes/updates _aos/server_dual_stack_status.json with timestamp.
#
# What this probe does NOT do:
#   - Apply any mitigation (no clatd install, no resolv.conf edit, no systemd touch).
#   - Run on the hub (`agents-os` itself uses macOS CLAT; this probe targets Linux spokes).
#   - Decide between scenarios C vs D vs F (operator choice; this probe surfaces the situation).
#
# Cross-platform: bash 3.2+ (macOS default), curl, dig (bind9-host or dig from bind-utils),
# python3 (already required by validate_aos.sh).

set -u

PROBE_VERSION="v1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------- args ----------
SPOKE_ROOT="${1:-.}"
ISP_DNS="${ISP_DNS:-}"  # optional override; empty = use system resolver
VERBOSE="${VERBOSE:-0}"

# Resolve absolute path for the spoke root.
if [ -d "$SPOKE_ROOT" ]; then
    SPOKE_ROOT="$(cd "$SPOKE_ROOT" && pwd)"
else
    echo "ERROR: spoke root '$SPOKE_ROOT' is not a directory" >&2
    exit 2
fi

STATUS_FILE="$SPOKE_ROOT/_aos/server_dual_stack_status.json"
STATUS_DIR="$(dirname "$STATUS_FILE")"

if [ ! -d "$STATUS_DIR" ]; then
    echo "ERROR: $STATUS_DIR does not exist — is this an AOS spoke root?" >&2
    exit 2
fi

# ---------- helpers ----------
log() { [ "$VERBOSE" -eq 1 ] && echo "  [probe] $*" >&2 || true; }

probe_ipv4() {
    # Returns 0 if curl -4 to a known IPv4-reachable destination succeeds within 5s.
    local code
    code=$(curl -4 -sS --max-time 5 https://1.1.1.1 -o /dev/null -w "%{http_code}" 2>/dev/null || echo "000")
    [ "$code" = "200" ] && return 0 || return 1
}

probe_ipv6() {
    # Returns 0 if curl -6 to a known IPv6-reachable destination succeeds within 5s.
    local code
    code=$(curl -6 -sS --max-time 5 https://www.cloudflare.com -o /dev/null -w "%{http_code}" 2>/dev/null || echo "000")
    [ "$code" = "200" ] && return 0 || return 1
}

probe_nat64() {
    # Returns 0 if ISP/upstream resolver synthesizes AAAA for ipv4only.arpa
    # (RFC 7050 NAT64 detection). Empty result = no NAT64.
    local out
    if [ -n "$ISP_DNS" ]; then
        out=$(dig +short +time=3 +tries=1 AAAA ipv4only.arpa @"$ISP_DNS" 2>/dev/null || true)
    else
        out=$(dig +short +time=3 +tries=1 AAAA ipv4only.arpa 2>/dev/null || true)
    fi
    [ -n "$out" ] && return 0 || return 1
}

probe_clat() {
    # Returns 0 if clatd or 464xlat-style daemon is running.
    if command -v systemctl >/dev/null 2>&1; then
        systemctl is-active --quiet clatd 2>/dev/null && return 0
    fi
    pgrep -f clatd >/dev/null 2>&1 && return 0
    return 1
}

infer_scenario() {
    # Args: ipv4_ok ipv6_ok nat64_present clat_enabled
    # Returns matrix scenario: A|B|C|D|E|F|none
    # See WAN_DUAL_STACK_HARDENING_CANON §7 for the canonical decision tree.
    local v4="$1" v6="$2" n64="$3" clat="$4"

    if [ "$v4" = "true" ] && [ "$v6" = "true" ]; then
        # Dual-stack OK already; no scenario needed.
        echo "none"
        return
    fi

    if [ "$v4" = "true" ] && [ "$v6" = "false" ]; then
        # IPv4-only WAN — IR#15 does not require mitigation here.
        echo "none"
        return
    fi

    if [ "$v6" = "true" ] && [ "$v4" = "false" ]; then
        # IPv6-only WAN — IR#15 enforcement zone.
        if [ "$clat" = "true" ]; then
            # CLAT is running. Infer B (NAT64 present) vs C/D (NAT64 absent + tayga or DNS64).
            if [ "$n64" = "true" ]; then
                echo "B"
            else
                # NAT64 absent but clat working → likely C (clatd + local tayga)
                # or D (clatd + nat64.net DNS64). This probe can't distinguish; report C.
                echo "C"
            fi
            return
        fi
        # No CLAT → no mitigation in place yet.
        echo "none"
        return
    fi

    # Both v4 and v6 failed — broken network or upstream outage.
    echo "none"
}

# ---------- run probes ----------
log "spoke root: $SPOKE_ROOT"
log "ISP DNS:    ${ISP_DNS:-system default}"

if probe_ipv4; then IPV4_OK="true"; else IPV4_OK="false"; fi
log "ipv4_outbound: $IPV4_OK"

if probe_ipv6; then IPV6_OK="true"; else IPV6_OK="false"; fi
log "ipv6_outbound: $IPV6_OK"

if probe_nat64; then NAT64="true"; else NAT64="false"; fi
log "isp_nat64_present: $NAT64"

if probe_clat; then CLAT="true"; else CLAT="false"; fi
log "clat_enabled: $CLAT"

SCENARIO=$(infer_scenario "$IPV4_OK" "$IPV6_OK" "$NAT64" "$CLAT")
log "inferred mitigation_scenario: $SCENARIO"

# ---------- write status JSON ----------
HOSTNAME_VAL="$(hostname 2>/dev/null || echo unknown)"
CHECKED_AT="$(python3 -c 'import datetime; print(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"))' 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Use python3 to emit valid JSON (avoids quoting headaches in bash heredocs).
python3 - "$HOSTNAME_VAL" "$IPV4_OK" "$IPV6_OK" "$NAT64" "$CLAT" "$SCENARIO" "$CHECKED_AT" "$STATUS_FILE" "$PROBE_VERSION" <<'PYEOF'
import json, sys
hostname, v4, v6, n64, clat, scenario, ts, out_path, probe_version = sys.argv[1:10]
def b(x): return x == "true"
data = {
    "server": hostname,
    "ipv4_outbound": b(v4),
    "ipv6_outbound": b(v6),
    "isp_nat64_present": b(n64) if n64 in ("true","false") else None,
    "clat_enabled": b(clat),
    "mitigation_scenario": scenario,
    "checked_at": ts,
    "deploy_log_ref": "_COMMUNICATION/team_99/DEPLOY_LOG_*  # populate per spoke",
    "probe_version": probe_version,
}
with open(out_path, "w") as f:
    json.dump(data, f, indent=2, sort_keys=True)
    f.write("\n")
print(out_path)
PYEOF

# ---------- summary line ----------
echo ""
echo "[probe] WAN dual-stack status written: $STATUS_FILE"
echo "[probe]   ipv4_outbound=$IPV4_OK  ipv6_outbound=$IPV6_OK  nat64=$NAT64  clat=$CLAT  scenario=$SCENARIO"
case "$SCENARIO" in
    none)
        if [ "$IPV4_OK" = "false" ] && [ "$IPV6_OK" = "true" ]; then
            echo "[probe] ADVISORY: IPv6-only WAN with no mitigation in place. Consult lean-kit/.../WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md §7 (matrix B/C/D/F)." >&2
        fi
        ;;
    A|B|C|D|E|F)
        echo "[probe] Matrix scenario $SCENARIO active. Refer to lean-kit/.../WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md §7 row $SCENARIO."
        ;;
esac
