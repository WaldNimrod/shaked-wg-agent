# LOD200 — Concept | S001-P001-WP001

**Work package:** S001-P001-WP001  
**Project:** Example Task Tracker (L0)  
**Track:** A  
**Status (example narrative):** Superseded by LOD400/LOD500 for this WP.

---

## 1. Problem statement

Users need a minimal command-line task list to capture items, mark them done, and list open tasks without a database or network dependency for the MVP.

## 2. Goals

- Add and list tasks from a single JSON file store on disk.
- Mark tasks complete with a stable identifier.
- Operate via a small CLI (`task` subcommands).

## 3. Non-goals (out of scope for this WP)

- Web UI, sync, or multi-user collaboration.
- Due dates and reminders (deferred to S001-P001-WP002).

## 4. Components (conceptual)

| Component | Responsibility |
|-----------|----------------|
| CLI entry | Parse arguments, dispatch subcommands |
| Task store | Load/save JSON file; assign IDs |
| Task model | id, title, done flag |

## 5. Risks and assumptions

- Assumption: Python 3.11+ available locally.
- Risk: File corruption — MVP uses atomic write (documented in LOD400).

## 6. Lean gates completed (example)

- L-GATE_E, L-GATE_S — concept and spec path approved before build (see `roadmap.yaml`).
