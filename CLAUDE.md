# CLAUDE.md — shaked-wg-agent

**Repo:** WaldNimrod/shaked-wg-agent  
**Profile:** L0 (Lean/Manual)  
**Owner:** Nimrod (Team 00)  
**Purpose:** Manual-trigger WG search agent for Basel — scan, score, and track apartment listings for Shaked moving to Basel in June 2026.

---

## Mandatory Session Startup

1. Read `_aos/roadmap.yaml` — confirm active WP and current gate
2. Read `_aos/context/PROJECT_CONTEXT.md` — project background
3. Read `_aos/context/ACTIVATION_ARCH.md` — if acting as architecture agent
4. Confirm with System Designer (Nimrod / Team 00) before beginning work on gated items

---

## Team Model

| ID | Name | Engine | Role |
|----|------|--------|------|
| shaked_sd | Nimrod | human | system_designer (Team 00) |
| shaked_arch | Claude Code | claude-code | architecture_agent |
| shaked_build | Cursor | cursor-composer | builder_agent |
| shaked_val | OpenAI | openai | validator_agent (cross-engine) |

**Iron Rule #1:** Builder engine (cursor-composer) ≠ Validator engine (openai)

---

## Key Paths

| Path | Purpose |
|------|---------|
| `_aos/` | AOS governance artifacts |
| `_aos/lean-kit/` | Lean kit methodology snapshot (physical copy) |
| `_aos/roadmap.yaml` | Work package registry (SSOT) |
| `_COMMUNICATION/` | Inter-team artifacts |
| `shaked_wg_agent/` | Application source code |
| `data/` | JSON data store (config, sources, runs, listings) |
| `tests/` | Unit tests (pytest) |

---

## CLI Usage

```bash
python -m shaked_wg_agent run      # trigger full scan
python -m shaked_wg_agent status   # show project summary
python -m shaked_wg_agent list     # show all listings table
```

---

## Validation

```bash
# Unit tests
pytest tests/ -v

# Linting
ruff check shaked_wg_agent/ tests/

# AOS structural validation
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

---

## Gate Model (Track A)

```
L-GATE_E → L-GATE_S → L-GATE_B → L-GATE_V → COMPLETE
```

S001 application WP (S001-P001-WP001) and canonization WP (S001-P002-WP001) are **COMPLETE** (L-GATE_V recorded 2026-04-11). Next planned work is **S002** (see `_aos/roadmap.yaml`).

---

## Iron Rules

1. Builder engine ≠ validator engine (cross-engine mandatory)
2. `_aos/lean-kit/` is a physical copy — never a symlink
3. All `spec_ref` paths are repo-internal
4. Single writer on `roadmap.yaml` at any time
5. L-GATE_V is always `shaked_val` — immutable, constitutional

---

## AOS Hub Reference

Clone the AOS hub from GitHub (WaldNimrod organization; repository name is `agents` hyphen `os`). This spoke is registered in the hub file `_aos/projects.yaml` under `id: shaked-wg-agent`.
