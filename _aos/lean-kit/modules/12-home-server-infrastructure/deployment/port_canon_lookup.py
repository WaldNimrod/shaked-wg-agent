#!/usr/bin/env python3
"""
port_canon_lookup.py — Canonical port resolver for deploy-specs.

Usage:
    python3 port_canon_lookup.py <project_id> <env> <host_id> <service>

Example:
    python3 port_canon_lookup.py TikTrack-Phoenix_AOSProject staging waldhomeserver api
    → 8182

Resolves (project, env, host, service) → port by reading the canonical
port-registry.yaml. Searches in order:
  1. $PORT_REGISTRY_YAML (env var)
  2. <repo>/lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml  (hub)
  3. <repo>/_aos/lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml  (spoke)

Exit codes:
  0   success (port printed to stdout)
  1   usage error
  2   canon not found
  3   (project, env, host, service) tuple not registered
  4   canon schema / parse error

This helper is THE canonical entry point for deploy scripts. Hardcoded
ports in deploy-specs are a validate_aos.sh violation per Iron Rule #9
(port canon) and port-registry v2.0.0 §R6.

Ratified: 2026-04-20 — RATIFICATION_PORT_CANON_v2.0.0_2026-04-20.md
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _usage() -> None:
    print(__doc__, file=sys.stderr)
    sys.exit(1)


def _find_registry() -> Path:
    env = os.environ.get("PORT_REGISTRY_YAML")
    if env:
        p = Path(env)
        if p.is_file():
            return p
        print(f"ERROR: PORT_REGISTRY_YAML={env} not found", file=sys.stderr)
        sys.exit(2)
    cwd = Path.cwd()
    rel = Path("lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml")
    candidates = [
        cwd / rel,
        cwd / "_aos" / rel,
    ]
    # Walk up to 5 parents looking for either candidate
    for up in [cwd, *cwd.parents][:6]:
        for tail in (rel, Path("_aos") / rel):
            cand = up / tail
            if cand.is_file():
                return cand
    print("ERROR: port-registry.yaml not found (set PORT_REGISTRY_YAML or run from a repo root)", file=sys.stderr)
    sys.exit(2)


def lookup(project_id: str, env: str, host_id: str, service: str, registry_path: Path | None = None) -> int:
    try:
        import yaml  # type: ignore
    except ImportError:
        print("ERROR: PyYAML required (pip3 install pyyaml)", file=sys.stderr)
        sys.exit(4)

    registry_path = registry_path or _find_registry()
    try:
        with registry_path.open() as f:
            docs = list(yaml.safe_load_all(f))
    except Exception as e:
        print(f"ERROR: parse failure {registry_path}: {e}", file=sys.stderr)
        sys.exit(4)

    reg = next((d for d in docs if isinstance(d, dict) and "projects" in d), None)
    if reg is None:
        print(f"ERROR: no projects[] in {registry_path}", file=sys.stderr)
        sys.exit(4)

    version = str(reg.get("registry_version", "1.0.0"))
    if not version.startswith("2."):
        print(f"ERROR: canon version {version} < 2.0.0 — lookup requires v2.0.0+", file=sys.stderr)
        sys.exit(4)

    # Validate host exists in hosts[]
    hosts = {h.get("id") for h in reg.get("hosts", []) or [] if isinstance(h, dict)}
    if host_id not in hosts:
        print(f"ERROR: host {host_id!r} not in hosts[] (known: {sorted(hosts)})", file=sys.stderr)
        sys.exit(3)

    project = next((p for p in reg.get("projects", []) or [] if isinstance(p, dict) and p.get("id") == project_id), None)
    if project is None:
        known = [p.get("id") for p in reg.get("projects", []) or [] if isinstance(p, dict)]
        print(f"ERROR: project {project_id!r} not registered (known: {known})", file=sys.stderr)
        sys.exit(3)

    for inst in project.get("instances", []) or []:
        if not isinstance(inst, dict):
            continue
        if inst.get("env") == env and inst.get("host") == host_id:
            if service not in inst:
                base = project.get("base_triplet", {}) or {}
                print(f"ERROR: service {service!r} not in instance (available: {sorted(set(inst) - {'env','host','status','runtime_note','reconciliation_decision','reconciliation_deadline','target_release'})}, base_triplet keys: {sorted(base)})", file=sys.stderr)
                sys.exit(3)
            return int(inst[service])

    envs_hosts = [(i.get("env"), i.get("host")) for i in project.get("instances", []) or [] if isinstance(i, dict)]
    print(f"ERROR: no instance for project={project_id}, env={env}, host={host_id} (have: {envs_hosts})", file=sys.stderr)
    sys.exit(3)


def main(argv: list[str]) -> None:
    if len(argv) != 5:
        _usage()
    _, project_id, env, host_id, service = argv
    port = lookup(project_id, env, host_id, service)
    print(port)


if __name__ == "__main__":
    main(sys.argv)
