# WP Command Shipping Checklist — v1.0.0

**When to use:** Any WP that ships a new `.claude/commands/AOS_*.md` file OR modifies an existing one.  
**Authority:** team_100 executes at WP closure (after L-GATE_VALIDATE PASS, before archive).  
**Why this exists:** `propagate_governance.sh` propagates `core/governance/team_*.md` only — not command files. Teams that operate cross-domain (team_98/99/200) need an explicit update cycle when the command surface changes.

---

## Checklist

### Step 1 — Update `core/governance/team_99.md` (SSoT)

For each new or changed command, add/update the entry under **Available CLI skills**:

```
- `/AOS_<name>` — one-line description (V<NNN>+)
```

Include `--watch` flags or sub-commands if applicable.

### Step 2 — Update `_COMMUNICATION/team_99/__ONBOARDING_TEAM_99.md`

- Bump `version:` (e.g. v1.0.0 → v1.1.0)
- Update `date:` to today
- Add `changelog:` line describing what changed
- Add/update row in **Available Skills** table
- Update **Active Milestone** if relevant

### Step 3 — `git push origin main` (mandatory before MSG to team_99)

The server pulls from GitHub — without push, `git pull` on the server gets nothing.

```bash
git push origin main
```

### Step 4 — Run `propagate_governance.sh --all`

```bash
AOS_ACTOR_TEAM_ID=team_100 bash lean-kit/modules/project-governance/scripts/propagate_governance.sh --all
```

This propagates the updated `team_99.md` governance contract to all 10 spoke `_aos/governance/` directories.

### Step 5 — Commit everything

```bash
git add core/governance/team_99.md \
        _COMMUNICATION/team_99/__ONBOARDING_TEAM_99.md \
        _aos/governance/
git commit -m "chore(team_99): ship command surface update for V<NNN>"
```

### Step 6 — Send MSG to team_99

Always send — team_99 reads inbox on timer (and ad-hoc). MSG triggers `git pull` on the server.

```
/AOS_SendMail → team_99 | type: status | expects_response: false
Subject: "עדכון פקודות — V<NNN>"
Body:   "פקודות חדשות: /AOS_<name> [תיאור קצר].
         הרץ: cd /data/projects/agents-os && git pull
         הסימלינקים יתעדכנו אוטומטית."
```

---

## Scope of propagation (what goes where)

| Artifact | Propagated by | Where it lands |
|----------|--------------|----------------|
| `core/governance/team_*.md` | `propagate_governance.sh` | `_aos/governance/` in all 10 spokes |
| `.claude/commands/AOS_*.md` | **NOT propagated** — hub-only | Accessible only via Claude Code in agents-os repo, or via `~/.claude/commands/` symlinks on Mac |
| `_COMMUNICATION/team_99/__ONBOARDING_TEAM_99.md` | Manual (this checklist) | hub only — team_99 reads at session start |
| Activation prompt (GET /api/prompts/generate) | API (live generation) | Injected into every new agent session |

**Note on command files:** `.claude/commands/AOS_*.md` are hub-repo-local. They are NOT copied to spokes. Teams using Claude Code on Mac (`team_200`, `team_100`) access them directly. Teams using Codex/sandboxed engines (`team_190`, `team_99` in some configs) get command descriptions via governance contract + activation prompt — not the file itself.

---

### Step 7 — Server sync (one-time setup / after new commands added)

SSH into waldhomeserver and run:
```bash
cd ~/agents-os && git pull   # pull latest command files
# One-time setup if symlinks missing:
mkdir -p ~/.claude/commands
for f in ~/.claude/../agents-os/.claude/commands/AOS_*.md; do
  ln -sf "$(realpath $f)" ~/.claude/commands/$(basename "$f")
done
```

Verify: `ls ~/.claude/commands/AOS_* | wc -l` — should match local Mac count.

This step is **mandatory** whenever a new `AOS_*.md` command is added — otherwise `/AOS_*` commands are "Unknown skill" on the server.

---

## Trigger

This checklist is mandatory when `validate_aos.sh` Check 30/31 would find a new or modified `AOS_*.md` file. The AOS_archive skill should reference this checklist in its WP closure flow.

*v1.0.0 — 2026-04-23 — team_100*
