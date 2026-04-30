---
id: OS_PATCH_MANAGEMENT_v1.0.0
type: RUNBOOK
author: Team 00 (Principal) — ratified by Team 60 + Team 100 on 2026-04-30 (dual canonical co-sign per ADR040)
date: 2026-04-30
status: ACTIVE
applies_to: waldhomeserver (Ubuntu 24.04 LTS)
strategic_anchor: "Routine OS hygiene — keep waldhomeserver patched without manual sweeps"
references:
  - lean-kit/modules/12-home-server-infrastructure/server-registry/waldhomeserver.yaml
  - core/governance/team_99.md
operating_team: team_99
---

# Runbook — OS Patch Management (waldhomeserver)

## Purpose

Keep waldhomeserver continuously patched (security + regular updates) with
minimal manual intervention. Document the canonical configuration so any
team_99 session can verify, maintain, and recover the auto-update setup.

The server uses Ubuntu's `unattended-upgrades` daemon to apply patches
automatically every morning, and reboots itself at 04:00 if a kernel
update requires it. team_99's routine duty is to **verify the auto-update
mechanism is healthy** — not to apply patches by hand.

---

## Current configuration (canonical state)

This is the configuration that MUST exist on waldhomeserver. If any field
diverges, treat it as drift and restore — do not silently accept the
current state.

| Setting | Value | File |
|---|---|---|
| `unattended-upgrades` service | enabled, active | systemd |
| Daily fetch timer | `apt-daily.timer` | systemd |
| Daily upgrade timer | `apt-daily-upgrade.timer` | systemd |
| `Update-Package-Lists` | `"1"` (daily) | `/etc/apt/apt.conf.d/20auto-upgrades` |
| `Unattended-Upgrade` | `"1"` (daily) | `/etc/apt/apt.conf.d/20auto-upgrades` |
| Allowed origins | `${distro_id}:${distro_codename}` (main) | `/etc/apt/apt.conf.d/50unattended-upgrades` |
| Allowed origins | `${distro_id}:${distro_codename}-security` | (same) |
| Allowed origins | `${distro_id}:${distro_codename}-updates` | (same) |
| Allowed origins | `${distro_id}ESMApps:${distro_codename}-apps-security` | (same) |
| Allowed origins | `${distro_id}ESM:${distro_codename}-infra-security` | (same) |
| `Automatic-Reboot` | `"true"` | (same) |
| `Automatic-Reboot-Time` | `"04:00"` | (same) |
| Disabled origins (intentional) | `-proposed`, `-backports` | (same) |
| Third-party repos NOT auto-upgraded | Docker (`docker.com`) | by design |

**Why these choices:**
- `noble-updates` is enabled (not just security): home server, low risk, prefer being current.
- `-proposed` / `-backports` are disabled: they ship experimental / non-vetted packages and are unsafe for unattended use.
- Docker is excluded from auto-upgrades: container restarts during a Docker upgrade can disrupt running services. Docker is patched manually during planned maintenance.
- Reboot is forced at 04:00 if a kernel/`linux-base` update is pending. Without this, kernel patches install but never activate.

---

## Routine verification (run weekly or when prompted)

team_99 should run this check at least once a week (or whenever a session
starts and ops health is uncertain):

```bash
ssh nimrodw@10.100.102.2 '
echo "=== service ==="
systemctl is-enabled unattended-upgrades
systemctl is-active unattended-upgrades

echo
echo "=== timers ==="
systemctl list-timers apt-daily.timer apt-daily-upgrade.timer --no-pager

echo
echo "=== auto-upgrades config ==="
cat /etc/apt/apt.conf.d/20auto-upgrades

echo
echo "=== allowed origins (active only) ==="
sed -n "/Allowed-Origins/,/};/p" /etc/apt/apt.conf.d/50unattended-upgrades | grep -v "^//"

echo
echo "=== reboot policy ==="
grep -E "^Unattended-Upgrade::Automatic-Reboot" /etc/apt/apt.conf.d/50unattended-upgrades

echo
echo "=== reboot pending? ==="
[ -f /var/run/reboot-required ] && (echo YES; cat /var/run/reboot-required.pkgs) || echo no

echo
echo "=== upgradable packages ==="
apt list --upgradable 2>/dev/null | tail -n +2

echo
echo "=== last unattended-upgrades run ==="
sudo tail -3 /var/log/unattended-upgrades/unattended-upgrades.log 2>/dev/null || echo "no log entries"
'
```

**Expected output (healthy):**
- service: `enabled` + `active`
- timers: both listed with a future `NEXT` time
- `20auto-upgrades`: both periodic flags = `"1"`
- allowed origins: 5 active lines (main, security, updates, ESMApps-security, ESM-infra-security)
- reboot policy: `Automatic-Reboot "true"` and `Automatic-Reboot-Time "04:00"`
- reboot pending: `no` (or `YES` if a recent kernel update is waiting for 04:00)
- upgradable packages: should be empty most of the time, OR limited to Docker repo packages

**Drift signals (act on):**
- Service inactive/disabled → re-enable per §Recovery
- Origins missing `-updates` → re-apply per §Recovery
- Reboot policy reverted to false → re-apply per §Recovery
- Upgradable list growing past Docker → unattended-upgrades is failing; check log and act

---

## Manual maintenance (planned windows)

### A. Apply Docker stack updates

Docker is excluded from auto-upgrades. When the upgradable list shows
Docker packages, schedule a maintenance window and run:

```bash
ssh nimrodw@10.100.102.2 '
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get -y \
  -o Dpkg::Options::="--force-confdef" \
  -o Dpkg::Options::="--force-confold" \
  install --only-upgrade \
    docker-ce docker-ce-cli docker-ce-rootless-extras \
    containerd.io docker-compose-plugin docker-model-plugin
'
```

After upgrade: `/server --status` and verify all containers came back up.

### B. Force an immediate full upgrade (emergency / vulnerability advisory)

```bash
ssh nimrodw@10.100.102.2 '
sudo apt-get update -qq && \
sudo DEBIAN_FRONTEND=noninteractive apt-get -y \
  -o Dpkg::Options::="--force-confdef" \
  -o Dpkg::Options::="--force-confold" full-upgrade && \
sudo apt-get -y autoremove
'
```

If `/var/run/reboot-required` is present afterwards, either wait for
04:00 auto-reboot or reboot immediately with Team 00 approval (Iron
Rule #2 — destructive op).

### C. Enable Ubuntu Pro (free for personal use, ≤5 machines)

This unlocks the ESM Apps update channel (currently 1 deferred package).
Requires a Pro token from https://ubuntu.com/pro:

```bash
ssh nimrodw@10.100.102.2 'sudo pro attach <TOKEN>'
```

After attaching, `unattended-upgrades` will pick up ESM packages
automatically because the ESM origins are already in the allowed list.

---

## Recovery — restore canonical configuration

If the verification check shows drift, restore as follows.

**Re-enable service:**
```bash
ssh nimrodw@10.100.102.2 '
sudo apt-get install -y unattended-upgrades
sudo systemctl enable --now unattended-upgrades
'
```

**Restore `20auto-upgrades`:**
```bash
ssh nimrodw@10.100.102.2 '
sudo tee /etc/apt/apt.conf.d/20auto-upgrades > /dev/null <<EOF
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
'
```

**Restore allowed origins (`-updates` enabled) + auto-reboot at 04:00:**
```bash
ssh nimrodw@10.100.102.2 '
sudo cp /etc/apt/apt.conf.d/50unattended-upgrades \
        /etc/apt/apt.conf.d/50unattended-upgrades.bak.$(date +%Y%m%d-%H%M%S)
sudo sed -i "s|^//\(.*-updates\";\)|\1|" /etc/apt/apt.conf.d/50unattended-upgrades
sudo sed -i "s|^//Unattended-Upgrade::Automatic-Reboot \"false\";|Unattended-Upgrade::Automatic-Reboot \"true\";|" /etc/apt/apt.conf.d/50unattended-upgrades
sudo sed -i "s|^//Unattended-Upgrade::Automatic-Reboot-Time \"02:00\";|Unattended-Upgrade::Automatic-Reboot-Time \"04:00\";|" /etc/apt/apt.conf.d/50unattended-upgrades
'
```

**Verify with the routine check above.**

---

## Rollback — an upgrade broke something

If a package upgrade broke a service:

1. Identify the offending package from `/var/log/dpkg.log`:
   ```bash
   ssh nimrodw@10.100.102.2 'grep -E " upgrade " /var/log/dpkg.log | tail -20'
   ```
2. Pin a specific version:
   ```bash
   ssh nimrodw@10.100.102.2 'apt-cache madison <package>'
   ssh nimrodw@10.100.102.2 'sudo apt install <package>=<old-version>'
   ssh nimrodw@10.100.102.2 'sudo apt-mark hold <package>'
   ```
3. Document the hold in `_COMMUNICATION/team_99/` so it is not silently
   forgotten — held packages stop receiving security updates.
4. Open an issue/note for Team 100 if the upgrade exposed a deeper
   architectural concern.

**Kernel rollback** — if a kernel update breaks boot, GRUB still has
the previous kernel as a menu option. From console: select the older
kernel at boot. Then `apt remove linux-image-<bad-version>` and
`apt-mark hold` it.

---

## Auditing & logging

- **Daily log:** `/var/log/unattended-upgrades/unattended-upgrades.log`
- **Reboot log:** `/var/log/unattended-upgrades/unattended-upgrades.log` (mentions reboot)
- **`apt` history:** `/var/log/apt/history.log` and `/var/log/dpkg.log`

Per Iron Rule #4 (team_99 contract), any **manual** patch operation
(maintenance windows, emergency patch, package hold/rollback) MUST be
logged as an artifact in `_COMMUNICATION/team_99/` named:

`OPS_LOG_OS_PATCH_<YYYYMMDD>_v1.0.0.md`

Routine `unattended-upgrades` runs are logged on the server itself —
they do not need a `_COMMUNICATION/` artifact unless something failed.

---

## Reference — when this was set up

| Date | Action | Session |
|---|---|---|
| 2026-04-30 | Initial bring-current (14 packages + kernel 6.8.0-110→111). Configured `noble-updates` origin and 04:00 auto-reboot. | Team 00 / Mac CLI |

Backup of pre-change `50unattended-upgrades`:
`/etc/apt/apt.conf.d/50unattended-upgrades.bak.20260430` (on server)

---

*Module 12 runbook | OS Patch Management | v1.0.0 | 2026-04-30*
