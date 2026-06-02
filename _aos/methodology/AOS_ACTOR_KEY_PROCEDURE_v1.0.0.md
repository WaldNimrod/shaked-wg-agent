# AOS Actor Key Procedure v1.0.0

**Authority:** team_00 (Principal) + team_100 (Chief System Architect)
**Governance:** ADR040 (Authority Lockdown) + ADR034 (DB SSoT)
**Version:** 1.0.0 | **Date:** 2026-05-11
**WP:** AOS-V4.1-WP-ACTOR-KEY-PROCEDURE
**Propagated to spokes via:** /AOS_gov-sync (supersedes the deprecated /AOS_gov-update)

---

## Purpose

This document describes the end-to-end procedure for issuing, rotating, and revoking actor keys
for AOS hub API access. Any spoke team_100 can follow this document cold to onboard a new session
or rotate a compromised key.

## Background

The AOS hub API at `http://100.125.98.56:8090` (waldhomeserver, Tailscale) requires all mutation
calls to carry two headers:

| Header | Value |
|--------|-------|
| `X-Actor-Team-Id` | Your team ID (e.g., `team_100`) |
| `X-Actor-Api-Key` | The secret key assigned to your team |

The server validates the pair using timing-safe compare against `AOS_V3_ACTOR_KEYS` (a JSON map
stored in `core/.env` on waldhomeserver). If either header is absent or incorrect, the server
returns HTTP 401 or 403. This is defined in `core/modules/management/authority.py` (SEC-001).

**IMPORTANT:** The correct client-side env var is `AOS_ACTOR_API_KEY` — not the shorter form
without the `_API` suffix. See §4 for the correct configuration.

---

## §1 Who Can Issue Keys

Per ADR040 (Iron Rule #12), only three teams may issue actor keys:

| Team | Role |
|------|------|
| team_00 | Principal (Nimrod) |
| team_99 | Waldhomeserver operations |
| team_100 | Chief System Architect |

All other teams must request a key from one of the above. Requests go to team_99 inbox:
`_COMMUNICATION/team_99/` with subject `ACTOR_KEY_REQUEST_<your_team_id>`.

---

## §2 Requesting a Key (spoke team_100 or team_110)

1. File a message artifact at `_COMMUNICATION/team_99/MSG_ACTOR_KEY_REQUEST_<team_id>_v1.0.0.md`
   with fields: team_id, spoke project name, justification, AOS_API_BASE target.
2. team_99 runs `scripts/issue_actor_key.sh` on waldhomeserver to write the key silently.
3. team_99 runs `scripts/retrieve_actor_key.sh` on waldhomeserver secure terminal to read the
   key exactly once for delivery. Key is delivered only via waldhomeserver secure terminal
   (never chat, never commit, never email).
4. Receiving team sets:
   ```bash
   export AOS_ACTOR_TEAM_ID=<your_team_id>
   export AOS_ACTOR_API_KEY=<key delivered by team_99>
   export AOS_API_BASE=http://100.125.98.56:8090
   ```
5. Verify with the smoke test in §5.

---

## §3 Server-Side Issuance (team_99 only)

On waldhomeserver at `/data/projects/agents-os/`:

```bash
# Set issuer identity
export AOS_ACTOR_TEAM_ID=team_99

# Step 1: Issue key (writes silently — no key printed to stdout)
bash scripts/issue_actor_key.sh team_100

# Step 2: Retrieve key for one-time secure delivery
AOS_ACTOR_TEAM_ID=team_99 bash scripts/retrieve_actor_key.sh team_100
# Output: the key value printed once to this secure terminal
# Copy the key value and deliver it to the receiving session.
# Close this terminal immediately after copying.
```

The issuance script:
- Validates the issuer is in `{team_00, team_99, team_100}` (ADR040)
- Generates a cryptographically secure key via `openssl rand -base64 32`
- Writes the key to `core/.env` `AOS_V3_ACTOR_KEYS` JSON map using python3 (never `echo <key>`)
- Restarts `aos-api` systemd unit to load the new key
- Prints delivery instructions (NOT the key) to stdout

The retrieval script (`retrieve_actor_key.sh`) is the single point where the key appears — only
on the waldhomeserver secure SSH terminal. Only team_00 and team_99 may run it.

---

## §4 Spoke-Side Configuration

After receiving the key from team_99:

### Shell session (one-time or per-session):
```bash
export AOS_ACTOR_TEAM_ID=team_100        # or your team id
export AOS_ACTOR_API_KEY=<received key>  # ← correct var: AOS_ACTOR_API_KEY
export AOS_API_BASE=http://100.125.98.56:8090
```

### For Mac sessions (persistent, add to `~/.zshrc` or spoke `core/.env`):
```bash
# In spoke project core/.env (NOT committed to git):
AOS_ACTOR_TEAM_ID=team_100
AOS_ACTOR_API_KEY=<received key>
AOS_API_BASE=http://100.125.98.56:8090
```

**Note:** The server reads `AOS_V3_ACTOR_KEYS` (a JSON map stored in hub `core/.env`).
The client reads `AOS_ACTOR_API_KEY` (a single secret string for its team).
These are different variables — do not confuse them.

---

## §5 Verification Smoke Test

After setting the three env vars:

```bash
# Health check (no auth required — confirms connectivity):
curl -s "${AOS_API_BASE}/api/health" | python3 -m json.tool

# Authenticated mutation check (requires valid X-Actor-Api-Key):
curl -s \
  -H "X-Actor-Team-Id: ${AOS_ACTOR_TEAM_ID}" \
  -H "X-Actor-Api-Key: ${AOS_ACTOR_API_KEY}" \
  "${AOS_API_BASE}/api/health"
# Expected: HTTP 200 with {"status":"ok"} or similar

# Using msg_preflight.sh (if lean-kit messaging module is loaded):
source lean-kit/modules/team-messaging/scripts/msg_preflight.sh
msg_curl GET /api/health
# Expected: HTTP 200
```

**Error codes:**
| HTTP Code | `detail.code` | Meaning |
|-----------|---------------|---------|
| 400 | `MISSING_ACTOR_HEADER` | `X-Actor-Team-Id` header not sent |
| 401 | `ACTOR_KEY_NOT_CONFIGURED` | team_id not in server key map |
| 401 | `INVALID_ACTOR_KEY` | Key sent does not match server map |
| 403 | `ACTOR_VERIFICATION_DISABLED` | Server has no `AOS_V3_ACTOR_KEYS` AND no trust flag |

---

## §6 Key Rotation Procedure

Use rotation when a key is suspected compromised or as scheduled hygiene (recommended: every 90
days).

**IMPORTANT (OI-2 architectural constraint):** The `aos-api` server reads `AOS_V3_ACTOR_KEYS`
once at startup. There is no live dual-key mode without modifying `authority.py`. Rotation uses a
PRE-WRITE overlap window: the old key remains valid until the server restarts. Coordinate key
delivery BEFORE starting the rotation script.

```bash
# On waldhomeserver — team_99 (or team_00 / team_100):
export AOS_ACTOR_TEAM_ID=team_99

# Default 5-min overlap; extend if delivery coordination takes longer:
bash scripts/rotate_actor_key.sh team_100 --overlap-seconds 600

# In a SEPARATE terminal (during the overlap window), retrieve and deliver new key:
AOS_ACTOR_TEAM_ID=team_99 bash scripts/retrieve_actor_key.sh team_100
# Copy the key value and deliver it to the receiving session before the overlap expires.
```

Rotation sequence:
1. New key is generated (not yet written to env file)
2. Script prints rotation instructions and overlap window countdown
3. In a separate terminal: team_99 runs `retrieve_actor_key.sh` to get the new key
4. team_99 delivers new key to receiving team via secure terminal channel
5. Overlap window runs (default 300s) — old key still valid during this window
6. New key is written to `core/.env` and `aos-api` restarts
7. Old key is now invalid. Receiving team must have new key configured.

**Checklist:**
- [ ] Receiving team has new `AOS_ACTOR_API_KEY` set before overlap window expires
- [ ] Verify with smoke test (§5) after restart
- [ ] Old key confirmed invalid (HTTP 401 with old key)

---

## §7 Key Revocation Procedure

```bash
# On waldhomeserver — team_99:
export AOS_ACTOR_TEAM_ID=team_99
bash scripts/revoke_actor_key.sh team_100
```

The script removes the team's entry from `AOS_V3_ACTOR_KEYS` and restarts `aos-api`. The old
key becomes invalid within 60 seconds of script completion (the time for systemd restart + warm
start).

Revocation is idempotent — running it when a key is already absent exits 0 cleanly.

---

## §8 Security Constraints

| Constraint | Mechanism |
|-----------|-----------|
| Key never echoed during issuance | `issue_actor_key.sh` uses python3 file-write; key in shell variable only; no stdout key |
| Secure one-time retrieval only | `retrieve_actor_key.sh` is the only key-output path; restricted to team_00 / team_99; SSH terminal only |
| Key never in git history | `core/.env` is in `.gitignore`; scripts do not commit |
| Key never in chat logs | Delivery is waldhomeserver secure terminal only |
| Key never in process listing | python3 receives key via env var (not `sys.argv`) |
| `set +x` in all scripts | Prevents bash xtrace from leaking key in CI/debug logs |
| Timing-safe compare | Server uses `secrets.compare_digest` — not vulnerable to timing attack |
| Fail-closed default | Server returns 403 if `AOS_V3_ACTOR_KEYS` is unset (no silent accept) |

---

## §9 Approved Team Set for Issuance

Per ADR040 §3 — only these teams may run issuance scripts:

```
{team_00, team_99, team_100}
```

Only `{team_00, team_99}` may run `retrieve_actor_key.sh`.

To expand either set: file a Governance Change Request (GCR) per
`lean-kit/modules/project-governance/config_templates/GOVERNANCE_CHANGE_REQUEST.md.template`.
GCR requires team_00 approval (IR#12).

---

## §10 References

- `governance/directives/ADR040_GOVERNANCE_AUTHORITY_LOCKDOWN.md` — approved issuance teams
- `governance/directives/ADR034_DATA_AUTHORITY_DB_SSOT_ALL_PROFILES.md` — API header contract
- `core/modules/management/authority.py` — server-side key validation (SEC-001)
- `core/.env.example` lines 32-51 — `AOS_V3_ACTOR_KEYS` format + `AOS_ACTOR_API_KEY` client var
- `lean-kit/modules/team-messaging/scripts/msg_preflight.sh` line 163 — client key injection
- `_aos/work_packages/AOS-V4.1-WP-ACTOR-KEY-PROCEDURE/LOD400_spec.md` — implementation spec
