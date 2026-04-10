# VERSION FILE POLICY
# Canonical — mandatory for all projects using lean-kit

## Rule 1 — Directory names are stable identifiers. They do NOT encode version.

```
Correct:  aos_engine/    lean-kit/    _aos/
Wrong:    agents_os_v3/  lean_kit_v2/ _aos_v1/
```

**Transition clause (Rule 4):** Existing legacy names are grandfathered. See Rule 4.

## Rule 2 — Version information lives in files inside the directory.

```
_aos/metadata.yaml              ← consolidated provenance (canonical)
lean-kit/LEAN_KIT_VERSION.md    ← lean-kit source version
```

No version file at directory level that duplicates metadata.yaml content.
`metadata.yaml` is the single provenance SSOT for `_aos/`.

## Rule 3 — Version files use format "version+short-sha"

```
Examples:  "3.1.0+abc1234"    "0.1.0+ecf247c"
Format:    "[semver]+[7-char git SHA]"
```

The `lean_kit_version` field in metadata.yaml always uses this format.
The SHA traces back to the agents-os commit from which the lean-kit snapshot was taken.

## Rule 4 — Transition clause (active until S004)

Existing legacy directory names (e.g., `agents_os_v3/` in TikTrack) are grandfathered.
No non-compliance claim applies until S004 migration completes.

New directories created from this policy onward MUST comply with Rule 1.
Example: AOS-Sandbox-Full uses `aos_engine/` (correct), not `agents_os_v3/` (legacy).

## Rule 5 — metadata.yaml is the canonical provenance file for _aos/

### Required fields (ALL profiles):

```yaml
lean_kit_version: "3.1.0+abc1234"      # adopted lean-kit version + source SHA
lean_kit_source_sha: "abc1234def5678"   # full SHA of agents-os commit at snapshot time
lean_kit_source_date: "2026-04-05"      # date of snapshot
profile: L0                             # L0 | L2 | L3
```

### Additional fields (L2 projects only):

```yaml
aos_engine_version: "v0.1.0+ecf247c"   # engine snapshot version (from SNAPSHOT_VERSION)
```

**No standalone `AOS_ENGINE_VERSION` file.** All provenance is in metadata.yaml (RFI-005).

## Rule 6 — Profile composition (v3.1.1)

Profiles define MINIMUM required modules. See `lean-kit/profiles/` for canonical definitions.

| Profile | CORE modules | Required additions | Optional |
|---------|-------------|-------------------|----------|
| **L0** | 01, 03, 04 | — | 02, 05-09, 11 |
| **L2** | 01, 03, 04 | 02, 05, 06, 07, 08 | 09, 11 |
| **L3** | 01, 03, 04 | 02, 05, 06, 07, 08, 09, 10 | 11 |

Module 11 (Standards & Conventions) is always optional — activated per-standard per-project.
