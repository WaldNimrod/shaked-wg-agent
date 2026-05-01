---
id: WAN_DUAL_STACK_HARDENING_CANON_v1.0.0
title: WAN Dual-Stack Hardening Canon
status: CANON
date: 2026-05-02
authority: ADR048 + IR#15 (AOS-V4-MS001 / W11)
audience: spoke team_99 sessions (per-spoke); spoke team_100 sessions (mandate context)
scope: methodology + diagnostic commands + mitigation matrix + per-distro recipes (informational); NOT execution
authored_by: team_110 (Domain Architect; claude-sonnet-4-6 sub-agent of feat/v4 driver)
empirical_evidence:
  - TikTrack/_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md (PRIMARY)
  - TikTrack/_COMMUNICATION/team_80/RESEARCH_BEZEQ_BE_FIBER_AI_WIFI7_ADMIN_2026-05-01_v1.0.0.md
related:
  - ADR048 (architectural decision)
  - IR#15 (mandatory rule)
  - core/governance/team_99.md "WAN Dual-Stack Verification" section (operational clause)
  - validate_aos.sh Check 45 [SKIP:WARN] (automated awareness; Phase E)
  - lean-kit/modules/12-home-server-infrastructure/scripts/wan_dual_stack_probe.sh (Phase D)
---

# WAN Dual-Stack Hardening Canon

---

## §1 Purpose + scope

This document is the canonical SSoT for choosing a per-scenario mitigation when an AOS spoke runs on an IPv6-only WAN. It realises the mitigation matrix referenced in ADR048 §3.2 and IR#15, and is the normative reference for all spoke-facing guidance on this topic. No spoke team is authorised to invent a mitigation approach without first consulting the six-scenario matrix in §7.

**Audience.** Spoke `team_99` sessions: read this document before any deploy or network-change event on a Linux server. Spoke `team_100` sessions: consult the matrix when authoring mandates or reviewing DEPLOY_LOGs.

**Trigger.** This canon was authored following the 2026-05-01 TikTrack pilot-launch outage on Bezeq "be fiber" FTTH — a multi-hour service disruption caused by IPv6-only WAN with no ISP-side NAT64 and no pre-existing AOS guidance for Linux servers in this environment (per DEPLOY_LOG §6 and ADR048 §2.2).

**Out of scope.** Actual command execution on any server; per-spoke configuration files (these are spoke-owned artefacts); ISP customer-service interaction; cloudflared service unit management on live systems. This canon describes methodology. Execution belongs exclusively to each spoke's `team_99` session.

---

## §2 When to consult this canon

Consult this canon in any of the following situations:

1. **Initial deploy** of any spoke service that initiates outbound connections from a Linux server (cloudflared, sync jobs, third-party API calls, package manager operations, SSH to remote hosts, etc.).
2. **After any home-network change** — ISP swap, router replacement, fiber migration, line upgrade, or any reconfiguration that may alter the WAN connectivity profile.
3. **When `validate_aos.sh` Check 45 emits `[SKIP:WARN]`** — this is an advisory signal that the spoke's `_aos/server_dual_stack_status.json` is missing, stale (>30 days), or records `ipv4_outbound=false` with no permanent mitigation in place.
4. **When a deploy "GREEN" declaration is being prepared** and `_aos/server_dual_stack_status.json` is either absent or has `checked_at` older than 30 days. A deployment is not GREEN until dual-stack outbound has been explicitly verified.
5. **When authoring or reviewing a DEPLOY_LOG** and the Layer A / Layer B / Cleanup checklist split (per `core/governance/team_99.md` WAN dual-stack clause) is not yet complete.

The probe script (`wan_dual_stack_probe.sh`, Phase D) automates steps 1–4 above into a single 30-second run.

---

## §3 Detection — three commands

Run all three commands from the **server itself** (not from a LAN client). macOS and iOS devices are not affected by IPv6-only WAN because Apple implements a built-in CLAT (Customer-side Translator, RFC 6877) transparently. Linux servers have no equivalent. Results from a Mac are not representative of the server's connectivity.

### Command 1 — IPv4 outbound reachability

```bash
curl -4 -sS --max-time 5 https://1.1.1.1 -o /dev/null -w "IPv4: %{http_code}\n"
```

**Why this command.** Forces `curl` to use an IPv4 transport (`-4`) against a known-reachable IPv4-anycast address (Cloudflare 1.1.1.1). A 200-class response confirms the server can reach IPv4 destinations. A timeout or `000` confirms IPv4 outbound is broken.

**Edge cases:**
- `HTTP 000` or `curl: (28) Connection timed out` — IPv4 outbound blocked. Proceed to NAT64 probe.
- `HTTP 301` — redirecting to HTTPS; counts as reachable (confirmed observed in TikTrack case post-mitigation, per DEPLOY_LOG §4).
- `curl: (6) Could not resolve host` — DNS failure; not a definitive IPv4 test. Retry against a raw IP: `curl -4 -sS --max-time 5 http://1.1.1.1 -o /dev/null -w "IPv4: %{http_code}\n"`.
- `ping 1.1.1.1` is **not** a reliable substitute: NAT64 rate-limits ICMP, so only 1/3 packets may arrive even when TCP is fully functional (per DEPLOY_LOG §4 — "ping 1.1.1.1: 1/3 received, NAT64 ICMP rate limiting — expected").

### Command 2 — IPv6 outbound reachability

```bash
curl -6 -sS --max-time 5 https://www.cloudflare.com -o /dev/null -w "IPv6: %{http_code}\n"
```

**Why this command.** Forces IPv6 transport against a host that has a well-known AAAA record. Confirms that IPv6 outbound is functional. On Bezeq be-fiber and similar IPv6-only ISPs, this returns `HTTP 200` even when IPv4 outbound is completely broken (per DEPLOY_LOG §4 — "curl -6 cloudflare: HTTP 200").

**Edge cases:**
- `HTTP 000` or connection timeout — IPv6 outbound also broken; unusual but possible if server has no IPv6 default route. Check `ip -6 route show default`.
- Both IPv4 and IPv6 return 200 — dual-stack OK; no further action. Record in `_aos/server_dual_stack_status.json` and mark as compliant.
- IPv6 returns 200, IPv4 times out — IPv6-only WAN confirmed. Proceed to Command 3.

### Command 3 — NAT64 presence probe

```bash
dig +short AAAA ipv4only.arpa @<ISP-DNS-server>
```

Replace `<ISP-DNS-server>` with the ISP's IPv6 DNS resolver address (visible in `resolvectl status` or `cat /etc/resolv.conf`). For Bezeq be-fiber, the resolver is `2a06:c701:ffff::1`.

**Why this command.** `ipv4only.arpa` is a reserved domain that responds with only A records (192.0.0.170 and 192.0.0.171) in the absence of DNS64. When an ISP provides a DNS64 service, its resolver synthesises AAAA records from the A records, embedding the IPv4 address inside the ISP's NAT64 prefix (e.g., `64:ff9b::c000:aab`). An empty response confirms the ISP has no DNS64 and therefore no NAT64 gateway.

**Bezeq be-fiber evidence (per DEPLOY_LOG §6):**

```
$ dig +short AAAA ipv4only.arpa @2a06:c701:ffff::1
(empty — no AAAA synthesis)

$ resolvectl query ipv4only.arpa
192.0.0.170 (A record only, no AAAA)
```

Result: Bezeq be-fiber provides IPv6-only WAN with SLAAC but NO DNS64 and NO NAT64 gateway.

**Edge cases:**
- Returns an AAAA record (e.g., `64:ff9b::c000:aab`) — ISP has NAT64. The embedded IPv4 address (`192.0.0.170` = `c000:aab` in hex) confirms the synthesis. Apply matrix Scenario B.
- Empty response — ISP has no NAT64 (Bezeq case). Apply matrix Scenario C or D.
- Returns an NXDOMAIN or SERVFAIL — DNS resolver unreachable or misconfigured. Verify IPv6 DNS connectivity first.

### Decision tree — combining the three results

| IPv4 (cmd 1) | IPv6 (cmd 2) | NAT64 (cmd 3) | Situation | Go to |
|---|---|---|---|---|
| 200 | 200 | any | Dual-stack OK | No action; record status as compliant |
| timeout/000 | 200 | AAAA returned | IPv6-only; ISP has NAT64 | Scenario B |
| timeout/000 | 200 | empty | IPv6-only; no ISP NAT64 (Bezeq case) | Scenario C or D |
| timeout/000 | 200 | — (cloudflared only) | IPv6-only; only cloudflared as outbound | Scenario A |
| 200 | timeout/000 | n/a | IPv4-only WAN | Not affected by IR#15; mark compliant |
| timeout/000 | timeout/000 | n/a | No WAN outbound | Infrastructure emergency; out of scope for this canon |

---

## §4 Tayga routing-loop anti-pattern

**This section is CRITICAL.** Incorrect Tayga configuration causes a silent routing loop that produces 100% packet loss, kernel CPU spikes, and no useful error messages. This is not a theoretical risk — it was directly observed during TikTrack's T3 session (per DEPLOY_LOG §5).

### The mechanism

Tayga is a Linux userspace NAT64 daemon. It creates a virtual network device (`nat64` tun) and translates IPv4 packets destined to its configured NAT64 prefix back to IPv4. When configured with the **default documentation prefix `2001:db8::/32`** (RFC 3849), the following loop occurs on Bezeq be-fiber:

1. Application sends IPv4 packet to e.g. `1.1.1.1`.
2. IPv4 default route points to the `nat64` Tayga device.
3. Tayga translates `1.1.1.1` → `64:ff9b::101:101` (using the RFC 6052 well-known NAT64 prefix `64:ff9b::/96`).
4. The IPv6 route for `64:ff9b::/96` ALSO points back to the `nat64` device (because Tayga installs it that way by default).
5. Packet loops: IPv4 → nat64 → IPv6 → nat64 → IPv6 → ... → drop.

Even if the route is corrected to egress via the physical interface (`enp6s0`), Bezeq's WAN network does **not globally route** `64:ff9b::/96`. The prefix is RFC 6052 well-known but not universally routed — Bezeq does not forward it to a NAT64 gateway (per DEPLOY_LOG §5 — "Bezeq's network does not route 64:ff9b::/96").

**Observed symptoms (DEPLOY_LOG §5):** "All IPv4 outbound failed with 'no route to host'. Tayga running with nat64 tun device."

### Required pre-flight before starting tayga.service

Inspect the server's current IPv6 routing table BEFORE starting `tayga.service`:

```bash
ip -6 route show
```

The chosen Tayga NAT64 prefix MUST NOT appear anywhere in this output. If it does, the prefix overlaps with an existing route and will cause a loop.

### Recommended prefix

`2a00:1098:2b:0:0:1::/96` — this is a globally routable prefix operated by nat64.net, verified working from Bezeq lines on 2026-05-01 (per DEPLOY_LOG §3 — "plat-prefix=2a00:1098:2b:0:0:1::/96 works from Bezeq"). However, nat64.net is a third-party operator; see §5 for risks.

**Prefixes known NOT to work on Bezeq:**
- `64:ff9b::/96` — RFC 6052 well-known; not globally routed by Bezeq; causes the loop described above.
- `2a00:1098:2c::/96` — tested 2026-05-01; does not function from Bezeq lines (per DEPLOY_LOG §8).
- `2001:db8::/32` — RFC 3849 documentation prefix; never use in production configuration.

**Always verify against `ip -6 route show` first,** regardless of which prefix you choose, before starting `tayga.service`.

### Loop-detection diagnostic

If Tayga is already running and packet loss is occurring, run:

```bash
mtr -6 1.1.1.1
```

Inspect the hop list. If the **same hop appears more than once** in the trace, a routing loop is active. Stop `tayga.service` immediately:

```bash
sudo systemctl stop tayga
```

Then verify the `nat64` interface and associated routes have been removed:

```bash
ip link show nat64      # should be absent
ip -6 route show        # should have no Tayga prefix entries
```

### Stance on Tayga

Tayga is **ADVANCED-tier** mitigation. It requires non-overlapping prefix selection, pre-flight route inspection, loop-detection verification, and ongoing awareness of Bezeq's routing behaviour. For deployments where the team is not already comfortable with NAT64 infrastructure, prefer **Scenario D** (`clatd` + `nat64.net` DNS64) as a temporary bridge while working toward **Scenario F** (ISP Dual-Stack provisioning). Scenario D is simpler to install, simpler to diagnose, and carries lower risk of a silent routing loop — at the cost of a third-party DNS dependency (see §5).

---

## §5 DNS64 emergency patch — NOT canon (Appendix B)

**This section describes an emergency-only technique. It is NOT part of the permanent mitigation matrix.** Classify any deploy that uses this technique as `mitigation_scenario: "D"` or `"E"` in `_aos/server_dual_stack_status.json`.

### Mechanism

Edit `/etc/resolv.conf` to point to a DNS64-capable resolver:

```
# Option 1 — Cloudflare DNS64
nameserver 2606:4700:4700::64

# Option 2 — nat64.net (open-source/volunteer-operated)
nameserver 2a00:1098:2b::1
nameserver 2a00:1098:2c::1
```

When the system resolver uses a DNS64 server, hostname lookups for IPv4-only destinations return synthesised AAAA records. The system routes those AAAA addresses via `clatd`'s CLAT device, which translates them back to IPv4 at the NAT64 gateway. Result: applications that use DNS for name resolution can reach IPv4 destinations over the synthesised path.

### Why this is emergency-only

**(i) Third-party dependency.** `nat64.net` is volunteer-operated. It may disappear, rate-limit, or degrade without notice. Cloudflare's DNS64 (`2606:4700:4700::64`) is more reliable but still an external dependency not under AOS control.

**(ii) Hardcoded IPv4 addresses still fail.** DNS64 only helps when the application performs a DNS lookup and the resolver synthesises an AAAA record. Applications that use hardcoded IPv4 literals (e.g., `curl http://1.1.1.1`, SDK configs, health-check endpoints with raw IPs) bypass DNS entirely — DNS64 does not help them. A full `clatd`-based CLAT (Scenarios B/C) translates all IPv4 traffic at the network layer regardless of whether DNS is involved.

**(iii) Added DNS latency.** Every AAAA lookup that requires synthesis adds a round-trip to the nat64.net or Cloudflare DNS64 server. Typical overhead: 30–60 ms per lookup, depending on network conditions.

**(iv) DNS metadata leakage.** All hostname lookups that require IPv4 synthesis travel to the nat64.net (or Cloudflare) operator's infrastructure. For spokes handling sensitive domain names, this is an observable data leak.

### Mandatory cleanup checklist

When a permanent mitigation (Scenarios B, C, or F) is in place, the DNS64 emergency patch MUST be removed. Steps:

1. Remove the DNS64 nameserver line from `/etc/resolv.conf`.
2. Remove any persistent DNS64 configuration from `/etc/systemd/resolved.conf.d/` (e.g., the `dns64-nat64net.conf` file removed in TikTrack's Layer B cleanup — per DEPLOY_LOG §2).
3. Remove any netplan DNS override files that point to nat64.net resolvers (e.g., `/etc/netplan/60-dns64-nat64net.yaml`, also removed in TikTrack's cleanup — per DEPLOY_LOG §2).
4. Restore ISP-default DNS resolvers (for Bezeq be-fiber: `2a06:c701:ffff::1`, `2a06:c701:ffff::2` via RA).
5. Verify cleanup:

```bash
cat /etc/resolv.conf | grep nat64
# Expected: no output (zero matches)

resolvectl status | grep DNS
# Expected: only ISP-assigned resolvers
```

6. Update `_aos/server_dual_stack_status.json` with the new `mitigation_scenario` value and a fresh `checked_at` timestamp.
7. Record cleanup completion in the spoke's DEPLOY_LOG.

---

## §6 Per-distro `clatd` install recipes (informational)

`clatd` is the canonical client-side implementation of 464XLAT (RFC 6877). It creates a CLAT network device that translates IPv4 traffic to IPv6 at the network layer, allowing applications to use IPv4 addresses transparently on an IPv6-only WAN. The following recipes are informational; exact package names and paths are subject to upstream change.

### Ubuntu 22.04+ / Debian 12

Install from package repositories when available:

```bash
sudo apt update && sudo apt install clatd
```

If not in repos (Ubuntu 24.04 does not package `clatd` as of 2026-05 — per DEPLOY_LOG §3), build from source:

```bash
sudo apt install -y git perl libnet-dns-perl libnet-ip-perl tayga iproute2
git clone https://github.com/toreanderson/clatd
cd clatd
sudo make install
```

Verify installation:

```bash
clatd --version
```

Configure `/etc/clatd.conf`:

```
plat-prefix=2a00:1098:2b:0:0:1::/96
clat-dev=clat
v4-defaultroute-replace=yes
```

The `v4-defaultroute-replace=yes` setting is required when `netplan` or another network manager has left a stale IPv4 default route entry. Without it, `clatd` detects "already has IPv4 connectivity" and exits without creating the CLAT device (per DEPLOY_LOG §3 — "clatd v4-conncheck" gotcha, "use v4-defaultroute-replace=yes").

Enable and start:

```bash
sudo systemctl enable clatd
sudo systemctl start clatd
```

Verify interface state (expected output mirrors TikTrack — per DEPLOY_LOG §3):

```bash
ip addr show clat
# Expected: inet 192.0.0.1/32 scope global clat

ip route show default
# Expected: default dev clat scope link metric 2048 mtu 1260
```

Check for errors:

```bash
journalctl -u clatd --no-pager | tail -20
```

The systemd unit is auto-installed during `make install`. If it is not present, create `/etc/systemd/system/clatd.service` manually and run `systemctl daemon-reload`.

### RHEL 9+ / Rocky Linux / AlmaLinux

`clatd` has no package in default RHEL 9 repositories as of 2026-05. Build from source:

```bash
sudo dnf install -y git perl perl-Net-DNS perl-Net-IP tayga iproute
git clone https://github.com/toreanderson/clatd
cd clatd
sudo make install
```

Requires `iproute2` >= 5.x, which is the default on RHEL 9. Verify:

```bash
ip --version   # should show 5.x or higher
```

Same `/etc/clatd.conf` configuration and systemd unit setup as above.

### Older distros (Ubuntu 20.04, Debian 11)

Build from source using the same procedure as Ubuntu 22.04. Before starting, verify that the kernel supports NAT64 translation:

```bash
modinfo nf_nat   # should succeed
```

On very old kernels (< 4.x), `clatd` may require `tayga` as its NAT64 backend rather than kernel CLAT. Check `clatd`'s own dependency notes at https://github.com/toreanderson/clatd.

**Important — clatd bootstrap problem (per DEPLOY_LOG §8).** If the DNS64 emergency patch (§5) has already been removed before `clatd` is installed, the server cannot reach `github.com` (an IPv4-only host) to download the `clatd` source. Workaround: temporarily re-enable the DNS64 nameserver in `/etc/resolv.conf` for the duration of the `git clone` and `make install` operations, then remove it again and verify cleanup per §5.

### All distros — post-install verification checklist

After `systemctl start clatd`, confirm all of the following before declaring the mitigation active:

```bash
# 1. Interface is UP
ip addr show clat
# Expected: state UP, inet 192.0.0.1/32

# 2. IPv4 default route via CLAT device
ip route show default
# Expected: default dev clat

# 3. IPv4 TCP reachability
curl -4 -sS --max-time 5 https://1.1.1.1 -o /dev/null -w "IPv4: %{http_code}\n"
# Expected: HTTP 301 or 200

# 4. General hostname resolution + download
curl -sS --max-time 10 https://github.com -o /dev/null -w "github: %{http_code}\n"
# Expected: HTTP 200 (per DEPLOY_LOG §4 — "curl github.com: HTTP 200")

# 5. No errors in clatd journal
journalctl -u clatd --no-pager | grep -i error
# Expected: no output
```

---

## §7 Six-scenario mitigation matrix (A–F)

This is the canonical decision table for all AOS spokes operating on an IPv6-only WAN. After running the three detection commands in §3, map the results to a scenario and follow the Action column. Do not attempt a mitigation that is not in this table without first filing a domain-override approval request per IR#14.

| Scenario | When (precondition) | Action (per spoke team_99) | Permanence | Notes |
|---|---|---|---|---|
| **A — cloudflared-only** | Spoke runs only `cloudflared` as outbound-initiating service; no other services need IPv4 outbound | Edit `/etc/cloudflared/config.yml`: set `protocol: quic` AND `edge-ip-version: "6"` — **both flags are required**. Restart `cloudflared`. Verify 4/4 IPv6 QUIC edge connections in `journalctl -u cloudflared`. | PERMANENT | Neither flag alone is sufficient. `protocol: http2` with `edge-ip-version: "6"` fails to establish edge connections on IPv6-only WAN. `edge-ip-version: "6"` alone without `protocol: quic` is also insufficient (per DEPLOY_LOG §1 — both flags required, empirical proof). cloudflared >= 2024.x supports both flags; upgrade older cloudflared first. |
| **B — general IPv4 + ISP HAS NAT64** | Spoke needs general outbound IPv4 connectivity; NAT64 probe (cmd 3) returns AAAA synthesis records | Install `clatd` per §6 recipes. Do NOT set `plat-prefix` in `clatd.conf` — `clatd` auto-detects the upstream NAT64 prefix via `dig AAAA ipv4only.arpa`. Verify with `curl -4 1.1.1.1`. Update `_aos/server_dual_stack_status.json`. | PERMANENT | Simplest mitigation when applicable. `isp_nat64_present: true` in status JSON. |
| **C — general IPv4 + ISP has NO NAT64 (Bezeq case)** | Spoke needs general outbound IPv4 connectivity; NAT64 probe (cmd 3) returns empty; team is comfortable with advanced NAT64 configuration | Install `clatd` + `tayga` as local NAT64 gateway. Read §4 (Tayga anti-pattern) in full before proceeding. Run `ip -6 route show` pre-flight. Set `plat-prefix` to a verified non-overlapping, globally routable prefix (e.g., `2a00:1098:2b:0:0:1::/96`). Verify with `mtr -6 1.1.1.1` — no repeated hops. Confirm with `curl -4 1.1.1.1`. | PERMANENT (advanced) | Requires non-overlapping prefix selection and loop-check before promotion. `isp_nat64_present: false` in status JSON. PREFER SCENARIO D unless team is already comfortable with Tayga NAT64 configuration. |
| **D — general IPv4 + simpler than C** | Same precondition as Scenario C (IPv6-only, no ISP NAT64); team prefers simpler setup or needs faster resolution | Install `clatd` per §6 recipes. Set `plat-prefix=2a00:1098:2b:0:0:1::/96` in `/etc/clatd.conf` (nat64.net globally-routable prefix, verified working from Bezeq per DEPLOY_LOG §3). Add DNS64 nameserver to `/etc/resolv.conf` (e.g., `nameserver 2a00:1098:2b::1`). Verify with `curl -4 1.1.1.1`. Classify as TEMPORARY in DEPLOY_LOG. Execute cleanup checklist (§5) once Scenario C or F is in place. | TEMPORARY — third-party dependency | `2a00:1098:2c::/96` does NOT work from Bezeq (per DEPLOY_LOG §8). `nat64.net` is volunteer-operated; four risks documented in §5 (dependency, hardcoded IPs, latency, metadata). MUST replace with C or F for production hardening. Cleanup checklist (§5) is mandatory. |
| **E — emergency restore in <5 min** | Production outage; need IPv4 NOW; no time for full Scenario C/D install | Edit `/etc/resolv.conf` to add `nameserver 2606:4700:4700::64` (Cloudflare DNS64) or `nameserver 2a00:1098:2b::1` (nat64.net). Verify name resolution works: `curl -sS --max-time 10 https://github.com -o /dev/null -w "%{http_code}\n"`. Document as Appendix B patch in DEPLOY_LOG. | TEMPORARY — NOT canon (Appendix B only) | DNS64 resolv.conf patch only. Hardcoded IPv4 IPs still fail. Use for <30 min to unblock installation of Scenario D or C. Must be replaced ASAP. See §5 for full risks and mandatory cleanup checklist. `mitigation_scenario: "E"` in status JSON → Check 45 will emit `[SKIP:WARN]` at next validation. |
| **F — permanent line-level fix** | Spoke can tolerate a wait of days to weeks for ISP action; or is upgrading from a temporary mitigation | Contact ISP; request Dual-Stack provisioning or a static IPv4 add-on. Document the request date, ISP reference number, and expected timeline in the spoke's DEPLOY_LOG. Keep the active Scenario D or C running in parallel until ISP confirms Dual-Stack is active. Remove CLAT infrastructure after confirming `curl -4 1.1.1.1` returns 200 without any mitigation in place. | PERMANENT (cleanest) | Best long-term outcome. For Bezeq be-fiber in Israel, Dual-Stack add-on availability and cost: verify directly with Bezeq (199) — plans vary. Lead time: typically days to weeks. Document the full request-and-wait timeline in DEPLOY_LOG for spoke audit trail. |

---

## §8 Status file contract — `_aos/server_dual_stack_status.json`

Every spoke MUST maintain a `_aos/server_dual_stack_status.json` file on the spoke server. This file is the machine-readable evidence that dual-stack verification has been performed. `validate_aos.sh` Check 45 reads this file in advisory `[SKIP:WARN]` mode.

### Schema

```json
{
  "server": "<hostname>",
  "ipv4_outbound": true,
  "ipv6_outbound": true,
  "isp_nat64_present": false,
  "clat_enabled": true,
  "mitigation_scenario": "D",
  "checked_at": "2026-05-01T12:34:56Z",
  "deploy_log_ref": "_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md"
}
```

**Field definitions:**

| Field | Type | Values | Description |
|---|---|---|---|
| `server` | string | hostname | The server hostname (e.g., `waldhomeserver`) |
| `ipv4_outbound` | boolean | `true` / `false` | Result of `curl -4` check (cmd 1) |
| `ipv6_outbound` | boolean | `true` / `false` | Result of `curl -6` check (cmd 2) |
| `isp_nat64_present` | boolean or null | `true` / `false` / `null` | Result of NAT64 probe (cmd 3). `null` = not yet probed |
| `clat_enabled` | boolean | `true` / `false` | Whether `clatd` is running and its CLAT device is UP |
| `mitigation_scenario` | string | `"A"`, `"B"`, `"C"`, `"D"`, `"E"`, `"F"`, `"none"`, `"expired_temporary"` | Active mitigation from §7 matrix. `"expired_temporary"` = was D or E, cleanup checklist not yet executed |
| `checked_at` | string | ISO-8601 UTC timestamp | When the probe was last run |
| `deploy_log_ref` | string | relative path | Path to the DEPLOY_LOG artifact that documents this verification |

### Refresh triggers

Update `_aos/server_dual_stack_status.json` after every WAN verification event:
- Initial deploy (always)
- After any home-network change (ISP swap, router replacement, fiber migration)
- After applying or removing any mitigation (scenario change)
- When `validate_aos.sh` Check 45 emits `[SKIP:WARN]` and the cause is a stale timestamp

### Read by

`validate_aos.sh` Check 45 (Phase E) reads this file and emits `[SKIP:WARN]` when:
- File is absent (`SKIP:WARN` — no status on record)
- `checked_at` is older than 30 days (`SKIP:WARN` — stale; re-run probe)
- `ipv4_outbound=false AND mitigation_scenario IN {"none", "expired_temporary", "E"}` (`SKIP:WARN` — IPv4 outbound broken with no durable mitigation)

Check 45 does NOT FAIL the build. Spokes on dual-stack ISPs (where `ipv4_outbound=true`) see Check 45 SKIP cleanly with no impact on the 0-FAIL baseline.

### Written by

`wan_dual_stack_probe.sh` (Phase D) — a ~50-line bash script run by the spoke's `team_99` session. The hub does not run the probe on spoke servers; it distributes the script and schema as artefacts for local execution.

### Storage location

Spoke's `_aos/` directory only. This is a spoke-side operational file. It is NOT stored in the hub (`agents-os`) `_aos/` directory. The hub's `_aos/` contains hub governance artefacts; spoke server status does not belong there.

---

## §9 Empirical evidence — DEPLOY_LOG citations

All technical claims in this canon are grounded in TikTrack's 2026-05-01 DEPLOY_LOG — a 40-minute hands-on T3 troubleshooting session by team_99 (Home Server DevOps) that validated every mitigation described in §7. This section documents the specific findings and their §3.x location in the DEPLOY_LOG for traceability.

**Primary reference:** `TikTrack/_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md`

| Finding | DEPLOY_LOG section | Canon location |
|---|---|---|
| `protocol: quic` + `edge-ip-version: "6"` both required in cloudflared config; `protocol: http2` fails on IPv6-only WAN; 4/4 IPv6 QUIC connections confirmed with journalctl evidence (edge IPs: `2606:4700:a8::3`, `2606:4700:a0::1`, `2606:4700:a0::2`, `2606:4700:a8::4`) | §1 (Layer A) | §7 Scenario A; §3 Decision tree |
| DNS64 temporary patches removed: `/etc/systemd/resolved.conf.d/dns64-nat64net.conf`, `/etc/netplan/60-dns64-nat64net.yaml`, Tayga stopped, nat64 tun removed, iptables SNAT cleaned, `64:ff9b::/96` stale route removed | §2 (Layer B Section A cleanup) | §5 cleanup checklist |
| `clatd` installed from GitHub source (v2.1.0); `plat-prefix=2a00:1098:2b:0:0:1::/96`; `v4-defaultroute-replace=yes` required; CLAT device `clat` UP with `inet 192.0.0.1/32`; IPv4 default route `default dev clat metric 2048 mtu 1260` | §3 (clatd install) | §6 install recipes; §7 Scenarios B/C/D |
| Full dual-stack verification: `curl -4 1.1.1.1 → HTTP 301`; `curl github.com → HTTP 200`; `curl -6 cloudflare → HTTP 200`; `tt.nimrod.bio/health → HTTP 200 {"status":"ok"}`; `ssh git@github.com → authenticated`. `ping 1.1.1.1: 1/3 received (NAT64 ICMP rate limiting)` — ICMP not reliable as IPv4 test | §4 (verification) | §3 Commands 1–2; §3 edge cases (`ping` unreliability) |
| Tayga configured with `64:ff9b::/96` → routing loop because Bezeq does not route this prefix; IPv4→IPv6 translation looped back to nat64 device; 100% packet loss | §5 (Tayga routing loop) | §4 (Tayga anti-pattern — entire section) |
| `dig +short AAAA ipv4only.arpa @2a06:c701:ffff::1` returned empty; `resolvectl query ipv4only.arpa` returned A record only (`192.0.0.170`). Confirmed: Bezeq be-fiber has no DNS64 and no NAT64 gateway | §6 (Bezeq NAT64 probe) | §3 Command 3; §7 Scenario C/D precondition |
| `2a00:1098:2b:0:0:1::/96` works from Bezeq; `2a00:1098:2c::/96` does NOT; Ubuntu 24.04 does not package `clatd`; DNS64 must be temporarily re-enabled to bootstrap `clatd` from GitHub if removed too early; `v4-defaultroute-replace=yes` prevents early exit when stale IPv4 route exists | §8 (recommendations) | §6 per-distro recipes; §7 Scenario D notes; §4 prefix guidance |

---

## §10 References

| Artifact | Path / Identifier | Role |
|---|---|---|
| **ADR048** | `governance/directives/ADR048_IPV6_ONLY_WAN_COMPATIBILITY_v1.0.0.md` | Architectural decision record — governance anchor for this canon |
| **IR#15** | `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` §Iron Rules (Phase F deliverable) | Mandatory rule: IPv6-only WAN verification required on initial deploy + after network changes |
| **team_99.md** | `core/governance/team_99.md` — "WAN Dual-Stack Verification" section | Operational clause: verification required before GREEN declaration; Layer A / Layer B / Cleanup split |
| **validate_aos.sh Check 45** | `_aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh` (Phase E) | Automated advisory check (`[SKIP:WARN]`): reads `_aos/server_dual_stack_status.json` |
| **wan_dual_stack_probe.sh** | `lean-kit/modules/12-home-server-infrastructure/scripts/wan_dual_stack_probe.sh` (Phase D) | Detection probe script: populates `_aos/server_dual_stack_status.json` on spoke |
| **TikTrack DEPLOY_LOG** | `TikTrack/_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md` | PRIMARY empirical reference — T3 session validating all mitigations on Bezeq be-fiber |
| **TikTrack RESEARCH** | `TikTrack/_COMMUNICATION/team_80/RESEARCH_BEZEQ_BE_FIBER_AI_WIFI7_ADMIN_2026-05-01_v1.0.0.md` | Research backing — Bezeq be-fiber ISP architecture, IPv6-only WAN deployment model |
| **RFC 3849** | https://www.rfc-editor.org/rfc/rfc3849 | Documents `2001:db8::/32` as reserved documentation prefix — explains why Tayga's default prefix must never be used in production |
| **RFC 6052** | https://www.rfc-editor.org/rfc/rfc6052 | Well-known NAT64 prefix `64:ff9b::/96` — explains why this prefix requires global ISP routing support that Bezeq does not provide |
| **RFC 6877** | https://www.rfc-editor.org/rfc/rfc6877 | 464XLAT specification — the standard that `clatd` implements on the client (CLAT) side |

---

**Version:** v1.0.0
**Status:** CANON
**Authority:** ADR048 + IR#15 (AOS-V4-MS001 / W11)
**Authored by:** team_110 (Domain Architect; claude-sonnet-4-6)
**Date:** 2026-05-02
