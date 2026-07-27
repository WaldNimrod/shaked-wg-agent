---
id: ADR048_IPV6_ONLY_WAN_COMPATIBILITY_v1.0.0
adr_number: 048
title: IPv6-only WAN Compatibility Canon
status: ACCEPTED
date: 2026-05-02
decided_by: "team_00 (Principal); proposed by team_100 (AOS hub) on 2026-05-01; codified by team_110 (Domain Architect) under W11 / AOS-V4-MS001"
related_iron_rule: "IR#15 — IPv6-only WAN compatibility (added in this WP, methodology/AOS_CONCEPT_AND_PRINCIPLES.md)"
related_wps:
  - AOS-V4-WP-IPV6-WAN-HARDENING  # this WP — codifies the canon
related_artifacts:
  - lean-kit/modules/12-home-server-infrastructure/WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md  # Phase C — mitigation matrix
  - lean-kit/modules/12-home-server-infrastructure/scripts/wan_dual_stack_probe.sh  # Phase D
  - validate_aos.sh Check 45 [SKIP:WARN]  # Phase E
empirical_evidence:
  - TikTrack/_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md  # T3 troubleshooting — Bezeq be fiber confirmed NO ISP-side NAT64
  - TikTrack/_COMMUNICATION/team_80/RESEARCH_BEZEQ_BE_FIBER_AI_WIFI7_ADMIN_2026-05-01_v1.0.0.md  # ISP research
  - TikTrack/_COMMUNICATION/team_60/VERDICT_IPV6_WAN_HARDENING_TRIAD_haiku_v1.0.0.md  # cross-engine Haiku verdict on v1.0.0 triad
supersedes: none
superseded_by: none
---

# ADR048 — IPv6-only WAN Compatibility Canon

---

## §1 Status

**ACCEPTED** — 2026-05-02, by team_00 (Principal).

In scope for v4.0.0 GA per team_00 OVERRIDE 2026-05-02: the production environment is IPv6-only and will remain so. W11 (`AOS-V4-WP-IPV6-WAN-HARDENING`) is the 11th and final WP of milestone AOS-V4-MS001; v4.0.0 GA tag is blocked until W11 LOD500_LOCKED.

This ADR was proposed by team_100 (AOS hub) on 2026-05-01, based on a cross-domain GCR from TikTrack spoke (team_100, opus engine), and codified by team_110 (Domain Architect, claude-sonnet-4-6) under Phase A of W11. Validation: codex engine (IR#1 vendor-distinct external), per V4_ORCHESTRATOR_PROTOCOL.

---

## §2 Context

### §2.1 The systemic problem

AOS spokes deployed in environments where the ISP provides IPv6-only WAN experience a class of outbound connection failures that is not covered by any prior AOS canonical guidance. In these environments, a Linux server behind an IPv6-only WAN has no native path to IPv4 destinations — APIs, DNS resolvers, package repositories, external services — unless a compatibility layer is explicitly configured.

macOS and iOS devices are not affected: Apple's networking stack includes a built-in CLAT (Customer-side Translator, RFC 6877) that handles IPv4→IPv6 address translation transparently. Linux servers have no equivalent out-of-the-box behavior. A Linux server behind an IPv6-only WAN sees IPv4 outbound fail silently unless CLAT (`clatd`) or an equivalent mitigation is installed and correctly configured.

The AOS hub's own runtime on Team 00's Mac is unaffected for the same reason. But spoke Linux home servers — the standard deployment target for AOS projects — are exposed.

### §2.2 The trigger incident

On 2026-05-01, TikTrack's pilot-launch outage lasted multiple hours. The root cause: the production server had IPv6-only WAN (Bezeq "be fiber" FTTH rollout in Israel) and no WAN dual-stack mitigation. Outbound connections from the server — including cloudflared tunnel establishment — failed, taking the service offline.

Primary evidence: `TikTrack/_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md` (the hands-on T3 troubleshooting session; referred to as "DEPLOY_LOG" throughout this ADR).

### §2.3 The empirical correction — Bezeq has no ISP-side NAT64

This finding materially revises the v1.0.0 GCR assumption that `clatd` alone would suffice. CLAT (RFC 6877) requires a NAT64 gateway upstream to function: CLAT translates the client's IPv4 address to an IPv6 address using the ISP's NAT64 prefix, which the ISP's NAT64 gateway then translates back to IPv4 at the WAN edge.

Per DEPLOY_LOG §6:

```
$ dig +short AAAA ipv4only.arpa @2a06:c701:ffff::1
(empty — no AAAA synthesis)

$ resolvectl query ipv4only.arpa
192.0.0.170 (A record only, no AAAA)
```

Bezeq be-fiber provides IPv6-only WAN with SLAAC but NO DNS64 and NO NAT64 gateway. Without ISP-side NAT64, `clatd` alone silently fails: it discovers no NAT64 prefix and exits or creates a broken tunnel.

This means the mitigation strategy depends on whether the ISP provides NAT64 — a variable that must be detected at deploy time and rechecked after any network change.

### §2.4 Cross-spoke contagion risk

Bezeq be-fiber is an active rollout. As the ISP continues fiber-to-the-home deployment across Israel, any AOS spoke whose home server is on a Bezeq line is at risk. Current spoke inventory (non-exhaustive):

- TikTrack — confirmed impacted (2026-05-01); mitigation deployed
- SmallFarms, IsraelMicrogreens, HobbitHome, AgrosInsite, EyalAmit — exposure depends on ISP and server presence; not yet surveyed
- AOS hub — currently mitigated by macOS CLAT (Team 00's Mac); not directly at risk but propagates canon to all spokes

IPv6-only WAN rollouts are not unique to Israel. The same pattern appears in other ISPs deploying IPv6-only FTTH infrastructure globally. This canon applies to any AOS spoke on any IPv6-only WAN, not only Bezeq lines.

### §2.5 Pre-existing AOS posture

Before this ADR:

- No canonical guidance on dual-stack WAN verification existed in any AOS hub artifact.
- No `validate_aos.sh` check existed for this condition.
- No mitigation matrix existed.
- The cloudflared-specific fix (`protocol: quic` + `edge-ip-version: "6"`) was not documented in any hub artifact — it was discovered empirically during the TikTrack T3 session (DEPLOY_LOG §1).
- AOS-deployed spokes could fail silently at the network layer with no observable governance signal.

---

## §3 Decision

### §3.1 IPv6-only WAN as a first-class deployment target

AOS canonically supports IPv6-only WANs as a first-class deployment target. Spoke deployments on IPv6-only ISPs are not edge cases. Any AOS spoke running outbound-initiating services from a Linux server MUST verify dual-stack outbound connectivity at initial deploy and after any home-network change.

This requirement is formalized as **Iron Rule #15** (added in Phase F of W11 to `methodology/AOS_CONCEPT_AND_PRINCIPLES.md`, mirrored in `CLAUDE.md`).

### §3.2 Mitigation matrix as canonical SSoT

The canonical SSoT for choosing a per-scenario mitigation is `lean-kit/modules/12-home-server-infrastructure/WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md` §10 (authored in Phase C). This document contains the 6-scenario matrix (A–F), per-distro installation recipes, the Tayga anti-pattern, and the DNS64 emergency appendix.

No spoke team is authorized to invent its own mitigation approach without first consulting this matrix. Spoke-specific extensions require the standard domain-override approval process (IR#14).

### §3.3 Six-scenario mitigation matrix (A–F)

The matrix keys on two variables: (a) what service needs IPv4 outbound? and (b) does the ISP provide NAT64?

Detection commands (must run before choosing a mitigation path):

```bash
# IPv4 outbound check
curl -4 -sS --max-time 5 https://1.1.1.1 -o /dev/null -w "IPv4: %{http_code}\n"
# IPv6 outbound check
curl -6 -sS --max-time 5 https://www.cloudflare.com -o /dev/null -w "IPv6: %{http_code}\n"
# NAT64 presence probe (run against ISP DNS resolver)
dig +short AAAA ipv4only.arpa @<ISP-DNS-server>
# If the above returns an AAAA synthesis (e.g. 64:ff9b::c000:aab), ISP has NAT64.
# If empty, no NAT64 (Bezeq case — per DEPLOY_LOG §6).
```

**Scenario A — cloudflared-only tunnel (no other IPv4 outbound needed):**
Both `protocol: quic` AND `edge-ip-version: "6"` MUST be set in `/etc/cloudflared/config.yml`. Either flag alone is insufficient (per DEPLOY_LOG §1: `protocol: http2` on an IPv6-only WAN fails to establish edge connections; `--edge-ip-version 6` without `protocol: quic` is also insufficient — both flags are required to get the 4/4 IPv6 QUIC connections shown in the deploy log). This is the simplest and most reliable path when cloudflared is the only outbound-initiating service.

**Scenario B — general IPv4 outbound + ISP HAS NAT64:**
Install `clatd`. It auto-detects the ISP's NAT64 prefix via `dig AAAA ipv4only.arpa` and sets up a CLAT device. After service start, verify with `curl -4 1.1.1.1`.

**Scenario C — general IPv4 outbound + ISP has NO NAT64 (Bezeq case):**
Install `clatd` + local `tayga`. This creates a self-contained NAT64 stack. Requires careful prefix selection (see §4 — Tayga anti-pattern). This is the ADVANCED path; prefer Scenario D for initial deployments.

**Scenario D — general IPv4 outbound + ISP has NO NAT64, simpler setup:**
Install `clatd` + configure DNS64 via a third-party relay (e.g., `nat64.net`). Use `plat-prefix` pointing to the third-party relay's prefix (e.g., `2a00:1098:2b:0:0:1::/96` — per DEPLOY_LOG §3, this prefix was verified working from Bezeq lines on 2026-05-01; `2a00:1098:2c::/96` was tested and does NOT work). Classify as **TEMPORARY**: third-party dependency; must be replaced with Scenario C (local tayga) or Scenario F (ISP dual-stack) for production hardening.

**Scenario E — emergency restore in under 5 minutes:**
Edit `/etc/resolv.conf` to point to a DNS64 server from `nat64.net`. This is NOT canon. It is an emergency-only appendix (Appendix B in Phase C canon). Use only to restore connectivity to allow Scenario C or D to be properly installed.

**Scenario F — permanent line-level fix:**
Contact the ISP and request Dual-Stack provisioning or a static IPv4 add-on. This is the cleanest long-term solution but has a lead time measured in days or weeks. Use as a planned upgrade path, not an incident response.

### §3.4 `clatd` alone is not sufficient on NAT64-absent ISPs

This is the core empirical correction this ADR encodes. Any AOS documentation, mandate, or operator action that says "install `clatd`" without specifying the NAT64 situation is incomplete and potentially harmful (silent failure mode). Canon and all spoke-facing guidance MUST distinguish the two cases.

### §3.5 `validate_aos.sh` Check 45 — automated awareness

Phase E adds Check 45 to `validate_aos.sh` as an advisory `[SKIP:WARN]` check. The `[SKIP:WARN]` prefix tag is used because the AOS `validate_aos.sh` framework supports only PASS/FAIL/SKIP exit-code states; a real WARN primitive would require its own ADR and is out of scope for W11. The `[SKIP:WARN]` pattern preserves exit-code semantics on the v4.0.0 release artifact.

Check 45 reads `_aos/server_dual_stack_status.json` (schema: `{server, ipv4_outbound, ipv6_outbound, isp_nat64_present, clat_enabled, mitigation_scenario, checked_at}`). It emits `[SKIP:WARN]` when `ipv4_outbound=false AND mitigation_scenario IN {none, expired_temporary}`. It does NOT FAIL the build. Spokes not on IPv6-only WANs see Check 45 SKIP cleanly with no impact.

The JSON artifact is populated by `wan_dual_stack_probe.sh` (Phase D) — a ~50-line bash script run by each spoke's `team_99` session. The hub does not execute the probe on spoke servers; it distributes the script and the schema.

### §3.6 Scope boundary

This ADR and the W11 WP govern methodology, documentation, scripts (as artifacts), and canonical guidance only. Server-side execution — installing `clatd`, editing live systemd units, running the probe in production, contacting the ISP — belongs exclusively to each spoke's `team_99` session. The proving ground for all technical claims in this canon is TikTrack `team_99`'s 2026-05-01 deployment session (DEPLOY_LOG). Hub canon is retro-aligned to what was empirically validated there.

---

## §4 Consequences

### §4.1 Positive

**Cross-spoke resilience:** Any spoke on an IPv6-only WAN that has not run the probe will emit a `[SKIP:WARN]` from `validate_aos.sh` Check 45 rather than failing silently. Operators are made aware before a pilot-launch-style outage.

**Operator clarity:** The 6-scenario matrix (A–F) gives operators a deterministic decision tree keyed on detectable conditions (`dig AAAA ipv4only.arpa`). There is no guessing or trying mitigations sequentially.

**Empirical alignment:** Every technical claim in this canon traces to the DEPLOY_LOG (2026-05-01) — a 40-minute hands-on T3 session with verified outcomes. Canon reflects what was actually proven to work in production, not theoretical networking assumptions.

**Future-proof:** The matrix accommodates any ISP × NAT64-presence × mitigation combination. When a new ISP deploys IPv6-only service (with or without NAT64), the detection commands and matrix apply without modification.

**cloudflared specificity:** Scenario A explicitly encodes the dual-flag requirement (`protocol: quic` + `edge-ip-version: "6"`) that was discovered empirically. Without canon, every future spoke deploying cloudflared on an IPv6-only WAN would rediscover this non-obvious combination.

### §4.2 Negative / mitigated

**Tayga routing-loop anti-pattern:** When Tayga is configured with the default well-known NAT64 prefix (`64:ff9b::/96`), an ISP that does not route that prefix (Bezeq does not — per DEPLOY_LOG §5) causes all translated IPv4 traffic to loop: IPv4 → NAT64 device → `64:ff9b::target` → back to NAT64 device → loop. Symptom: 100% packet loss, kernel CPU spike. Per DEPLOY_LOG §5, this occurred on the TikTrack server during the T3 session.

The Phase C canon MUST mandate:
- Non-overlapping prefix selection: verify that the chosen Tayga prefix is globally routable AND not already in the server's routing table (`ip -6 route show` inspection before `tayga.service` start).
- Loop-detection diagnostic: `mtr -6 1.1.1.1` should not show the same hop twice. If it does, the NAT64 route is looping.
- `2a00:1098:2b:0:0:1::/96` is the empirically-verified working prefix from Bezeq lines (DEPLOY_LOG §3). `2a00:1098:2c::/96` was tested and does not work. `64:ff9b::/96` (RFC 6052 well-known prefix) is not globally routable from Bezeq and must not be used.

Mitigation: canon §3 (Phase C) enforces these precautions; Scenario C is labeled ADVANCED with an explicit pointer to the anti-pattern section.

**DNS64 via `nat64.net` is a third-party dependency.** `nat64.net` is volunteer-operated. For production deployments it carries four risks documented in the Phase C canon Appendix B: (i) third-party dependency — service may disappear or degrade without notice; (ii) hardcoded IPv4 addresses in application config still fail even with DNS64 active (no DNS lookup, no synthesis); (iii) added DNS latency for every AAAA lookup; (iv) DNS metadata leakage — all hostname lookups travel to nat64.net operators. Scenario D (DNS64 via third-party) is classified TEMPORARY in canon; the cleanup checklist is mandatory before the deploy is declared "GREEN".

**Per-distro `clatd` install variance:** Ubuntu 24.04 does not package `clatd`; install from GitHub source (per DEPLOY_LOG §8). Ubuntu 22.04+, Debian 12, and RHEL 9+ have different package paths. Phase C canon provides per-distro recipes. The `clatd` bootstrap problem (DEPLOY_LOG §8) is a documented gotcha: if DNS64 is removed before `clatd` is installed, the server cannot reach GitHub (IPv4-only host) to download the source. Temporarily re-enabling DNS64 for bootstrap is the documented workaround.

**`clatd` early-exit on dead IPv4 default route:** If netplan has a stale IPv4 default route entry, `clatd` detects "already has IPv4 connectivity" and exits without creating the CLAT device. Fix: `v4-defaultroute-replace=yes` in `/etc/clatd.conf` (per DEPLOY_LOG §3).

**Cloudflared version dependency:** Older cloudflared versions may not support `--edge-ip-version 6`. Canon mandates upgrade-first before applying Scenario A.

**Operational cost per spoke:** The probe must run on initial deploy AND after any home-network change. Mitigated: `wan_dual_stack_probe.sh` is ~50 lines of bash; detection is fast (5-second `curl` timeouts per check); total probe runtime is under 30 seconds.

### §4.3 Neutral / observational

- This ADR introduces no DB schema change. W11 artifacts are file-only during the feat/v4 milestone (consistent with all W1–W10 WPs — per metadata.yaml `db_record_present: false`).
- Backwards compatibility: spokes not on IPv6-only WANs see Check 45 SKIP cleanly (no impact on existing 0-FAIL baseline).
- `core/definition.yaml` is read-only for this WP. Per-team operating rules stay scoped there and are not affected by the global Iron Rules list.
- The DEPLOY_LOG records that `ping 1.1.1.1` only yielded 1/3 packets (NAT64 ICMP rate limiting — expected). ICMP delivery is not a reliable test for IPv4 outbound; `curl -4` is the canonical check.

---

## §5 Implementation map

The following table shows which artifact realizes each aspect of this decision. Phase A (this ADR) is the governance anchor; all subsequent phases reference it.

| Phase | Artifact | Realizes |
|-------|----------|----------|
| A | `governance/directives/ADR048_IPV6_ONLY_WAN_COMPATIBILITY_v1.0.0.md` (this file) | Architectural decision record — governance anchor |
| B | `core/governance/team_99.md` — WAN dual-stack clause amendment | team_99 contract: verification required before any deploy is declared GREEN |
| C | `lean-kit/modules/12-home-server-infrastructure/WAN_DUAL_STACK_HARDENING_CANON_v1.0.0.md` | §10 mitigation matrix SSoT; Tayga anti-pattern §3; DNS64 Appendix B |
| D | `lean-kit/modules/12-home-server-infrastructure/scripts/wan_dual_stack_probe.sh` | Detection probe; populates `_aos/server_dual_stack_status.json` |
| E | `validate_aos.sh` Check 45 (`[SKIP:WARN]`) | Automated awareness check; reads spoke's dual-stack status JSON |
| F | `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` IR#15 + `CLAUDE.md` mirror | Mandatory rule; canonical location for numbered global Iron Rules |
| G | `scripts/aos_sync_all.sh` propagation run | Delivers canon artifacts to all 9 spokes via Iron Rule #11 governance flow |
| H | Status MSG broadcast to all spokes' team_99 sessions | Spoke operator awareness; includes §10 matrix as quick reference |

The hub does not own Phases G and H execution timing — those are gated on LOD500_LOCKED for this WP (team_190 validate verdict required before propagation).

---

## §6 Empirical evidence chain

All technical claims in this canon trace to the following evidence chain. Any future revision to the mitigation guidance MUST verify against this chain or file a new empirical reference before amending canon.

### §6.1 DEPLOY_LOG — primary reference

`TikTrack/_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md`

Authored by: team_99 (TikTrack Home Server DevOps). 40-minute hands-on T3 session. Key findings:

- **§1 (Layer A):** `protocol: quic` + `edge-ip-version: "6"` are both required in `/etc/cloudflared/config.yml`. With both flags, 4/4 edge connections established over IPv6 QUIC to Cloudflare edge IPs (`2606:4700:a8::3`, `2606:4700:a0::1`, `2606:4700:a0::2`, `2606:4700:a8::4`). Public URL `https://tt.nimrod.bio/api/v1/health` returned HTTP 200.
- **§3 (clatd install):** `plat-prefix=2a00:1098:2b:0:0:1::/96` works from Bezeq lines. Install from GitHub source (v2.1.0); Ubuntu 24.04 does not package it. `v4-defaultroute-replace=yes` required to prevent early exit.
- **§4 (verification):** `curl -4 1.1.1.1 → HTTP 301`; `curl github.com → HTTP 200`; `curl -6 cloudflare → HTTP 200`; `ssh git@github.com → authenticated`. Full dual-stack verified.
- **§5 (Tayga routing loop):** Default Tayga prefix `64:ff9b::/96` causes routing loop because Bezeq does not route this prefix; IPv4→IPv6 translations looped back to the nat64 device. 100% packet loss. Fixed by replacing Tayga with `clatd` + DNS64 via `nat64.net`.
- **§6 (Bezeq NAT64 probe):** `dig +short AAAA ipv4only.arpa @2a06:c701:ffff::1` returned empty. `resolvectl query ipv4only.arpa` returned A record only. Confirmed: Bezeq be-fiber has no DNS64 and no NAT64 gateway.
- **§8 (recommendations):** `2a00:1098:2b:0:0:1::/96` works; `2a00:1098:2c::/96` does not. Ubuntu 24.04 bootstrap problem documented. `v4-defaultroute-replace=yes` required.

### §6.2 RESEARCH — supporting evidence

`TikTrack/_COMMUNICATION/team_80/RESEARCH_BEZEQ_BE_FIBER_AI_WIFI7_ADMIN_2026-05-01_v1.0.0.md`

Research-grade evidence on Bezeq be-fiber network architecture, AI WiFi7 router admin access, and IPv6-only WAN behavior. Provides broader context on ISP deployment model; corroborates DEPLOY_LOG §6 findings at the infrastructure level.

### §6.3 Cross-engine verdict — governance validation

`TikTrack/_COMMUNICATION/team_60/VERDICT_IPV6_WAN_HARDENING_TRIAD_haiku_v1.0.0.md`

Haiku (claude-haiku) constitutional review of the v1.0.0 GCR triad (RESEARCH + mandate + GCR). Verdict: **10/10 PASS** ("ship as-is"), three minor informational observations only. Validates the governance proposal shape (open a WP, amend Iron Rules, add lean-kit canon, add validate check, propagate via `aos_sync_all.sh`). Technical content of the v1.1.0 updates (NAT64-absent empirical findings) post-dates this verdict; a fresh validation at LOD200 is required per LOD100 brief §8.

---

## §7 Numbering rationale

### §7.1 ADR048 (not ADR047)

The source GCR (`GCR_CROSS_DOMAIN_IPV6_ONLY_WAN_HARDENING_v1.0.0.md` §3.5 and §11 row A) proposed "ADR047 — IPv6-only WAN compatibility canon". **ADR047 is already taken**: `ADR047_TASK_ROUTING_AND_FALLBACK_CHAINS_v1.0.0.md` is present in `governance/directives/`. This correction was identified during hub triage (TRIAGE §4, item 1) and confirmed by directory inspection. ADR045 is a numbering gap; team_00 directed defaulting to the next free slot rather than filling the gap. Therefore: **ADR048**.

### §7.2 IR#15 (not IR#16)

The source GCR §3.1 proposed "Iron Rule #16". CLAUDE.md enumerates Iron Rules #1 through #14 (most recent: IR#14 — Environment base / Domain override with approval). The next available slot is **#15**, not #16. Canonical location: `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` (not `core/definition.yaml` — the `iron_rules:` blocks in `definition.yaml` are per-team operating rules, not the numbered global list). This correction was identified during hub triage (TRIAGE §4, items 2–3). Therefore: **IR#15**.

### §7.3 Check 45 (not Check 33)

The source GCR proposed "Check 33". Check 33 is already taken (`MSG naming advisory complete` check, added in a prior WP). W7 (`AOS-V4-WP-VALIDATE-CHECKS-39-43`) added Checks 39–44. The next free slot is **Check 45**. This correction was identified during hub triage (TRIAGE §4, item 2, and confirmed in LOD100 brief §3.3). Therefore: **Check 45**.

---

## §8 Out of scope

### §8.1 Deferred — spoke server execution

The following actions belong exclusively to each spoke's `team_99` session and are NOT performed by hub team_110 under this WP:

- Editing live cloudflared systemd units on any server
- Installing `clatd`, `tayga`, or any network package on any server
- Running the probe script (`wan_dual_stack_probe.sh`) in production
- Refreshing `_aos/server_dual_stack_status.json` on spoke servers
- Contacting the ISP (Bezeq or other) for dual-stack provisioning
- Diagnosing live network failures on any spoke server

The proving ground for canonical mitigations is TikTrack `team_99`. Other spokes adopt the canon post-broadcast (Phase H) at their own pace.

### §8.2 Explicitly excluded

- Replacing Bezeq's router with third-party XGS-PON equipment. Classified HIGH-risk in team_80 RESEARCH (admin UI access risk, warranty void, BGP implications). Not addressed here.
- DNS-level forking of IPv4/IPv6 at the router level. Requires firmware-level capability not present in Bezeq's provisioned router.

### §8.3 Potential future scope (not this ADR)

- IPv4-only fallback for hub-side outbound — not currently a problem; hub's macOS environment uses Apple CLAT transparently.
- NAT64 relay self-hosting at the hub level for shared use across spokes — would require a new ADR (ADR049+) and Team 00 approval.
- Spoke-level `_aos/server_dual_stack_status.json` schema extension (e.g., per-interface reporting) — deferred to a spoke GCR if needed.

---

## §9 References

| Artifact | Path | Notes |
|----------|------|-------|
| LOD100 Brief | `_COMMUNICATION/team_100/LOD100_BRIEF_AOS_VX_WP_IPV6_WAN_HARDENING_v1.0.0.md` | Primary spec — §3.5 ADR048 framing, §4 phase plan |
| Triage | `_COMMUNICATION/team_100/TRIAGE_GCR_CROSS_DOMAIN_IPV6_ONLY_WAN_HARDENING_2026-05-01_v1.0.0.md` | Step 4 numbering corrections (ADR047→ADR048, IR#16→IR#15, Check 33→Check 45) |
| Source GCR | `TikTrack/_COMMUNICATION/team_100/GCR_CROSS_DOMAIN_IPV6_ONLY_WAN_HARDENING_v1.0.0.md` (body v1.1.0) | §9–§12 contain the T3 empirical updates |
| DEPLOY_LOG (primary) | `TikTrack/_COMMUNICATION/team_99/DEPLOY_LOG_CLOUDFLARED_IPV6_FIX_2026-05-01_v1.0.0.md` | T3 hands-on session — Bezeq NAT64 absence confirmed, all mitigations validated |
| ISP RESEARCH | `TikTrack/_COMMUNICATION/team_80/RESEARCH_BEZEQ_BE_FIBER_AI_WIFI7_ADMIN_2026-05-01_v1.0.0.md` | Bezeq be-fiber architecture; corroborates DEPLOY_LOG §6 |
| Cross-engine VERDICT | `TikTrack/_COMMUNICATION/team_60/VERDICT_IPV6_WAN_HARDENING_TRIAD_haiku_v1.0.0.md` | Haiku 10/10 PASS on v1.0.0 triad; fresh verdict required at LOD200 per LOD100 §8 |
| team_110 Mandate | `_COMMUNICATION/team_110/MANDATE_HANDOFF_IPV6_WAN_HARDENING_v1.0.0.md` | Phase plan, scope boundary, cross-engine discipline |
| W11 Metadata | `_aos/work_packages/AOS-V4-WP-IPV6-WAN-HARDENING/metadata.yaml` | validator_engine: codex (IR#1); consolidation_note (branch history) |
| V4 Orchestrator Protocol | `_COMMUNICATION/team_100/V4_ORCHESTRATOR_PROTOCOL_v1.0.0.md` | IR#1 vendor-distinct external pattern for W11 |
| ADR044 | `governance/directives/ADR044_AOS_v4_0_0_CHARTER_AND_TRACK_MODEL_v1.0.0.md` | v4.0.0 charter; STANDARD track definition applicable to W11 |
| ADR034 | `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` | DB-as-SSoT pattern; W11 uses file-only mode (consistent with all v4 WPs) |

---

**END OF ADR048 v1.0.0**
