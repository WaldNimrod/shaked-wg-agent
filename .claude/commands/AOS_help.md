---
summary: "Display a concise reference of all AOS slash commands — one line per command (auto-generated from frontmatter)."
category: meta
---

# /AOS_help

Auto-generated reference for all `.claude/commands/AOS_*.md` commands. Reads each command's YAML frontmatter (`summary:` + `category:`) and emits a grouped list.

## Phase

```bash
python3 - <<'PY'
import re
from pathlib import Path

cmd_dir = Path(__file__).resolve().parent if "__file__" in dir() else Path("/Users/nimrod/Documents/agents-os/.claude/commands")
# Fallback if __file__ unavailable (most interactive runs)
if not (cmd_dir / "AOS_help.md").exists():
    cmd_dir = Path("/Users/nimrod/Documents/agents-os/.claude/commands")

by_cat: dict[str, list[tuple[str, str]]] = {}
for p in sorted(cmd_dir.glob("AOS_*.md")):
    text = p.read_text()
    if not text.startswith("---\n"):
        continue
    end = text.find("\n---\n", 4)
    if end == -1:
        continue
    fm = text[4:end]
    m_sum = re.search(r'^summary:\s*"?([^"\n]+)"?', fm, re.MULTILINE)
    m_cat = re.search(r'^category:\s*(\S+)', fm, re.MULTILINE)
    if not m_sum or not m_cat:
        continue
    summary = m_sum.group(1).strip().strip('"').strip("'")
    category = m_cat.group(1).strip()
    by_cat.setdefault(category, []).append((p.stem, summary))

order = ["gate", "session", "governance", "project", "infrastructure", "decision", "meta"]
labels = {
    "gate":           "Gate operations",
    "session":        "Session orchestration",
    "governance":     "Governance (AOS-team-only per ADR040)",
    "project":        "Project operations",
    "infrastructure": "Infrastructure wrappers",
    "decision":       "Decision support",
    "meta":           "Meta-commands",
}
print("═══════════════════════════════════════════════════════════════")
print("  AOS SLASH COMMANDS REFERENCE")
print("  Iron Rule #13 / ADR041 — thin-orchestrator pattern")
print("═══════════════════════════════════════════════════════════════\n")
for cat in order:
    items = by_cat.get(cat, [])
    if not items:
        continue
    print(f"▸ {labels[cat]}\n")
    for name, summary in sorted(items):
        print(f"  /{name:<22} {summary}")
    print()
print("── Docs ──────────────────────────────────────────────────────")
print("  methodology/AOS_COMMAND_ARCHITECTURE_v1.0.0.md — canonical pattern")
print("  governance/directives/ADR041_COMMAND_ARCHITECTURE_UNIFICATION_v1.0.0.md")
PY
```

## Error Handling

- If no command files found: report "No AOS commands found in expected directory."
- If a command file has no valid frontmatter: silently skip it (validator reports stale files separately).

## Notes

- Reference generated from each command's YAML frontmatter — single source of truth.
- To add a new command: create `.claude/commands/AOS_{name}.md` with `summary:` + `category:` frontmatter per ADR041. Next `/AOS_help` run picks it up automatically.
- Future: `GET {HUB_API_BASE}/api/commands` returns the same data as JSON for dashboard consumers.

Reference: `governance/directives/ADR041_COMMAND_ARCHITECTURE_UNIFICATION_v1.0.0.md`, `methodology/AOS_COMMAND_ARCHITECTURE_v1.0.0.md`.
