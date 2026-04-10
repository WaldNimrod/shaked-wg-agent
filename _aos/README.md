# _aos/ — AOS Governance Directory

**Project:** shaked-wg-agent  
**Profile:** L0 (Lean/Manual)  
**Owner:** Team 00 (Nimrod)  
**Lean Kit:** 3.1.2+3e4164e

---

## Single-Writer Rule

Only **one agent** holds write authority over `roadmap.yaml` at a time.  
Authority transfers at gate boundaries per `team_assignments.yaml`.

| Gate | Write Authority Holder |
|------|------------------------|
| Pre L-GATE_S | `shaked_arch` (claude-code) |
| L-GATE_B → L-GATE_V | `shaked_build` (cursor-composer) |
| L-GATE_V | `shaked_val` (openai) — read-only for all others |
| Post L-GATE_V | `shaked_sd` (human) |

---

## File Inventory

| File | Purpose | Authority |
|------|---------|-----------|
| `metadata.yaml` | Profile & lean-kit version provenance | Team 00 |
| `definition.yaml` | Team definitions snapshot (physical copy from hub) | Team 00 (via Team 110) |
| `roadmap.yaml` | Work package registry (SSOT) | Single-writer per gate |
| `team_assignments.yaml` | Team-to-role mapping + cross-engine validator | Team 00 |
| `README.md` | This file | Team 00 |
| `MILESTONE_MAP.md` | Milestone definitions | Team 00 |
| `context/` | Agent activation prompts | Team 110 |
| `governance/` | Per-team governance contracts | Team 00 |
| `work_packages/` | LOD spec chain per WP | Architect/Builder |
| `lean-kit/` | Methodology snapshot (PHYSICAL COPY, never symlink) | Team 00 |

---

## Validation

```bash
bash _aos/lean-kit/modules/validation-quality/scripts/validate_aos.sh .
```

Exit 0 = all checks pass. Required before L-GATE_B.

---

## Iron Rules (Immutable)

1. Builder engine ≠ validator engine
2. `lean-kit/` is a physical copy — never a symlink
3. All `spec_ref` paths are repo-internal
4. Single writer on `roadmap.yaml` at any time
5. L-GATE_V is always `shaked_val` (cross-engine, constitutional, immutable)
