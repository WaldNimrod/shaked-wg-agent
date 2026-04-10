# LOD400 — Executable specification | S001-P001-WP002 (example, in build)

**Work package:** S001-P001-WP002  
**Project:** Example Task Tracker (L0)  
**Narrative state:** Spec approved at L-GATE_S; builder working toward L-GATE_B.

---

## 1. Scope

Extend the CLI with optional due dates (`--due YYYY-MM-DD`) on `add`, `list --due` filter, and a `remind` subcommand that prints tasks due within N days.

## 2. Acceptance criteria (draft for example)

| ID | Criterion |
|----|-----------|
| AC-WP2-01 | `taskctl add "Title" --due 2026-04-01` stores `due` on the task object |
| AC-WP2-02 | `taskctl list --due-soon 7` lists open tasks with due date within the window |
| AC-WP2-03 | Tasks without `due` are included in default `list` and excluded from `--due-soon` unless documented otherwise |

## 3. Sign-off (example)

| Role | Team ID | Date | Result |
|------|---------|------|--------|
| Architecture agent | team_tasktracker_arch | 2026-03-20 | APPROVED |
