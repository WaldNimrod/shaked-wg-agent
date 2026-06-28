---
summary: "Run a full cross-domain health audit across all registered AOS domains."
category: project
---

## API Base Resolution

API base resolves via three tiers (ADR043 §15.4 + §16): (1) `AOS_API_BASE` env var — highest priority; (2) `AOS_V3_PUBLIC_API_BASE` from `core/.env` — waldhomeserver canonical (`http://100.125.98.56:8090`); (3) `http://127.0.0.1:8090` — localhost fallback (correct on waldhomeserver; returns HTTP 410 on Mac unless legacy stub is running). Set `AOS_ACTOR_API_KEY` for server auth when `AOS_V3_ACTOR_KEYS` is enforced. Reference: ADR043 §15.4 (key retrieval) + §16 (auth matrix per team).

Run a full cross-domain health audit across all registered AOS domains.

API endpoint: `GET {HUB_API_BASE}/api/health/domains`  
(`HUB_API_BASE` defaults to `http://127.0.0.1:8090`; override via `AOS_API_BASE` env)

Checks per domain: governance_sync, lean_kit_version_match, validate_aos_last_run, required_aos_files.

## Phase 0 — Parse arguments

No arguments required. Runs against all domains in `_aos/projects.yaml`.

## Phase 1 — Call API

```
GET {HUB_API_BASE}/api/health/domains
```

**If API unreachable:** STOP. Instruct user: `bash scripts/start_aos_api_local.sh`

## Phase 2 — Display results

Format response as a comparison table:

```
## Domain Health Audit — [DATE]

| Check | {domain_1} | {domain_2} | ... |
|---|---|---|---|
| validate_aos.sh | ✅ {N} PASS | ... |
| required_aos_files | ✅ | ... |
| governance_sync | ✅ | ⚠ N behind | ... |
| lean_kit_version | ✅ | ⚠ v mismatch | ... |
```

Severity legend: 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | ✅ PASS

## Phase 3 — Remediation list

For each domain where `remediations` is non-empty, present numbered list ordered by severity.

## Phase 4 — Write report + summary

Write report to `_COMMUNICATION/team_100/DOMAIN_HEALTH_REPORT_{DATE}.md`.

Present one-line summary: "{N}/{total} domains healthy — {M} gaps found"

## Error Handling

- API 4xx → parse detail, present to user
- API 5xx → display status; instruct user to check server logs
- Domain path not found → recorded as CRITICAL gap in API response; display as-is
