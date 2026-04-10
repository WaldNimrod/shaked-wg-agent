# LOD400 — Executable specification | S001-P001-WP001

**Work package:** S001-P001-WP001  
**Project:** Example Task Tracker (L0)

---

## 1. Scope

Deliver a Python CLI `taskctl` with subcommands `add`, `list`, `done` backed by `tasks.json` in the current working directory.

## 2. Acceptance criteria

| ID | Criterion | Test approach |
|----|-----------|-----------------|
| AC-01 | Running `taskctl add "Buy milk"` creates `tasks.json` if missing and appends a task with unique `id`, `title`, `done: false` | Execute CLI; parse JSON; assert one task |
| AC-02 | `taskctl list` prints only tasks where `done` is false, one per line with id and title | Seed file; capture stdout |
| AC-03 | `taskctl done <id>` sets matching task `done` to true; unknown id exits non-zero with stderr message | Seed file; run command; inspect JSON |
| AC-04 | Concurrent-safe save: write to temp file then `os.replace` into `tasks.json` | Unit test or scripted two rapid adds without corruption |
| AC-05 | `taskctl --help` documents all subcommands | Capture help text; assert keywords |

## 3. Interfaces

- **CLI:** `taskctl add <title>`, `taskctl list`, `taskctl done <id>`
- **Storage:** JSON array of objects `{ "id": string, "title": string, "done": boolean }`

## 4. Sign-off (example)

| Role | Team ID | Date | Result |
|------|---------|------|--------|
| Architecture agent | team_tasktracker_arch | 2026-03-19 | APPROVED |
