---
id: UPRESS_FTPS_PROTOCOL
version: v1.0.0
date: 2026-05-22
status: ACTIVE
canonical_owner: team_100 (hub governance)
applies_to: Any AOS project deploying to uPress hosting (nimrod.bio)
origin: GCR_UPRESS_FTPS_PROTOCOL_2026-05-10_v1.0.0 (team_10, SmallFarmsAgents WP004)
---

# uPress FTPS — Canonical Connection Protocol

**Host:** `ftp.s887.upress.link` · **Port:** 21 (explicit FTPS / STARTTLS — NOT implicit)
**Credentials:** `UPRESS_SFTP_HOST`, `UPRESS_SFTP_PORT`, `UPRESS_SFTP_USER`, `UPRESS_SFTP_PASS` from project `.env`

---

## Working Python pattern

```python
import ftplib, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE  # uPress data channel cert is self-signed

ftp = ftplib.FTP_TLS(context=ctx)
ftp.connect('ftp.s887.upress.link', 21, timeout=15)
ftp.login(user, password)
ftp.prot_c()       # MANDATORY — prot_p causes 425 on data channel
ftp.set_pasv(True)
# ftp.cwd(...), ftp.storbinary(...), ftp.nlst(...) all work now
```

---

## IP allowlist (MANDATORY before every connect)

uPress blocks FTP by source IP. Before connecting:
1. `curl -s ifconfig.me` — get current agent IP
2. Open uPress control panel → FTP accounts → IP allowlist → add IP
3. Nimrod must confirm allowlist update before agent retries

**The agent IP is NOT static.** Check before each session.

---

## What does NOT work

| Attempt | Result |
|---------|--------|
| Implicit FTPS (port 990) | TCP timeout |
| `prot_p()` on data channel | `425 Unable to build data connection` |
| `curl --ssl-reqd ftps://...` | SSL cert error then `425` |
| Connecting without IP allowlist | TCP timeout |
| SSH/SFTP port 22 | Blocked by uPress |

---

## WP option registration timing

When a mu-plugin calls `register_setting()` on `init`, the option is only
addressable via `POST /wp/v2/settings` **after the mu-plugin is installed**.
Always install mu-plugin via FTPS first, then call `--set-mou-url` or equivalent.

---

## ezcache purge (after any file deploy)

```python
requests.delete(
    'https://www.nimrod.bio/wp-json/ezcache/v1/cache',
    auth=(WP_APP_USER, WP_APP_PASS)
)
```

---

*Runbook | AOS Module 12 | hub governance*
*Propagated to all spokes via lean-kit rsync (aos_sync_all.sh Step 2)*
