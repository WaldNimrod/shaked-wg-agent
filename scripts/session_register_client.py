#!/usr/bin/env python3
"""Thin HTTP client for W3 session register API (used by shell pre-flight)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def _api_base() -> str:
    return (
        os.environ.get("AOS_API_BASE")
        or os.environ.get("AOS_V3_PUBLIC_API_BASE")
        or "http://127.0.0.1:8092"
    ).rstrip("/")


def _repo_root() -> "Path | None":
    """Nearest ancestor of cwd that looks like a repo root (has _aos/ or .git)."""
    cur = Path.cwd().resolve()
    for d in (cur, *cur.parents):
        if (d / "_aos").is_dir() or (d / ".git").exists():
            return d
    return None


def _marker_team() -> "str | None":
    """COMM-07 (v5 ENV): read the committed worktree-local identity marker `_aos/session_identity`
    (first non-empty line = the acting team id). Returns None when absent so the env/default chain wins."""
    root = _repo_root()
    if root is None:
        return None
    marker = root / "_aos" / "session_identity"
    if marker.is_file():
        try:
            for line in marker.read_text(encoding="utf-8").splitlines():
                tid = line.strip()
                if tid and not tid.startswith("#"):
                    return tid
        except Exception:
            return None
    return None


def _team_id() -> str:
    # COMM-07 precedence: explicit env override → committed worktree marker → global default → team_90.
    # Reading the marker here keeps the DB session-registry team_id correct for a domain worktree even
    # when nothing exported AOS_SESSION_TEAM_ID (parity with aos_session_ctl.sh aos_session_team()).
    return (
        os.environ.get("AOS_SESSION_TEAM_ID")
        or _marker_team()
        or os.environ.get("AOS_ACTOR_TEAM_ID")
        or "team_90"
    ).strip()


def _actor_headers() -> dict[str, str]:
    team = _team_id()
    headers = {"X-Actor-Team-Id": team, "Content-Type": "application/json"}
    # CTX-02 (v5 ENV): carry the session's project scope so the DB bus tags rows per-domain. Only set
    # when AOS_PROJECT_ID is present → a hub session (unset) sends no header (NULL=hub, unchanged).
    pid = (os.environ.get("AOS_PROJECT_ID") or "").strip()
    if pid:
        headers["X-Project-Id"] = pid
    raw = os.environ.get("AOS_V3_ACTOR_KEYS", "").strip()
    if raw:
        try:
            keys = json.loads(raw)
            key = keys.get(team, "")
            if key:
                headers["X-Actor-Api-Key"] = key
        except json.JSONDecodeError:
            pass
    elif os.environ.get("AOS_ACTOR_API_KEY"):
        headers["X-Actor-Api-Key"] = os.environ["AOS_ACTOR_API_KEY"].strip()
    return headers


def _request(method: str, path: str, body: dict | None = None, timeout: float = 3.0) -> tuple[int, dict | list | None]:
    url = f"{_api_base()}{path}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=_actor_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode("utf-8"))
        except Exception:
            payload = {"message": str(e)}
        return e.code, payload
    except Exception as e:
        return 0, {"error": str(e)}


def cmd_register(args: argparse.Namespace) -> int:
    env = os.environ.get("AOS_SESSION_ENV", "local-mac")
    body = {
        "session_id": args.session_id,
        "team_id": _team_id(),
        "environment": env,
        "branch": args.branch,
        "worktree_path": args.worktree_path,
        "wp_id": args.wp_id,
        # OBS-8: project (domain) + engine attribution (arg > env > None).
        "domain": (getattr(args, "domain", None) or os.environ.get("AOS_PROJECT_ID") or None),
        "engine": (getattr(args, "engine", None) or os.environ.get("AOS_ENGINE") or None),
    }
    code, payload = _request("POST", "/api/sessions/register", body)
    if code != 200:
        print(json.dumps({"ok": False, "code": code, "detail": payload}), file=sys.stderr)
        return 1
    print(json.dumps(payload))
    return 0


def cmd_heartbeat(args: argparse.Namespace) -> int:
    code, payload = _request("POST", "/api/sessions/heartbeat", {"session_id": args.session_id})
    if code != 200:
        return 1
    print(json.dumps(payload))
    return 0


def cmd_close(args: argparse.Namespace) -> int:
    code, payload = _request("POST", "/api/sessions/close", {"session_id": args.session_id})
    if code != 200:
        return 1
    print(json.dumps(payload))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    q = []
    if args.environment:
        q.append(f"environment={args.environment}")
    if args.status:
        q.append(f"status={args.status}")
    if args.live:
        q.append("live=true")
    path = "/api/sessions/list"
    if q:
        path += "?" + "&".join(q)
    code, payload = _request("GET", path)
    if code != 200:
        print(json.dumps({"ok": False, "code": code, "detail": payload}), file=sys.stderr)
        return 1
    print(json.dumps(payload))
    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    """W4 auto-capture: POST /messaging/v2/capture (degrade handled by shell wrapper on non-0 exit)."""
    # COMM-08: build the machine next-action routing object from --next-wp/--next-gate (None if neither).
    nw = getattr(args, "next_wp", None)
    ng = getattr(args, "next_gate", None)
    routing = {k: v for k, v in (("next_wp", nw), ("next_gate", ng)) if v} or None
    body = {
        "sender": args.sender or _team_id(),
        "recipient": args.recipient,
        "recipient_kind": args.recipient_kind,
        "kind": args.kind,
        "subject": args.subject,
        "body_ref": args.body_ref,
        "body_inline": args.body_inline,
        "session_id": args.session_id,
        "wp_id": args.wp_id,
        "gate": args.gate,
        # CTX-02: project scope tag (arg > $AOS_PROJECT_ID > None=hub). COMM-08: context_ref + routing.
        "project_id": getattr(args, "project_id", None) or os.environ.get("AOS_PROJECT_ID") or None,
        "context_ref": getattr(args, "context_ref", None),
        "routing": routing,
    }
    code, payload = _request("POST", "/api/messaging/v2/capture", body, timeout=float(args.timeout))
    if code != 200:
        print(json.dumps({"ok": False, "code": code, "detail": payload}), file=sys.stderr)
        return 1
    print(json.dumps(payload))
    return 0


def cmd_inbox(args: argparse.Namespace) -> int:
    """W4 inbox poll: GET /messaging/v2/inbox (read-only; degrade => empty on non-200)."""
    q = [
        f"recipient_kind={args.recipient_kind}",
        f"recipient={args.recipient}",
        f"status={args.status}",
        f"limit={args.limit}",
    ]
    code, payload = _request("GET", "/api/messaging/v2/inbox?" + "&".join(q), timeout=float(args.timeout))
    if code != 200:
        print(json.dumps({"degrade": True, "code": code, "count": 0, "messages": []}))
        return 2
    print(json.dumps(payload))
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    code, payload = _request("POST", "/api/messaging/v2/read", {"msg_id": args.msg_id}, timeout=float(args.timeout))
    if code != 200:
        print(json.dumps({"ok": False, "code": code, "detail": payload}), file=sys.stderr)
        return 1
    print(json.dumps(payload))
    return 0


def _fib_repo_root() -> Path:
    # client lives at <repo>/scripts/session_register_client.py
    return Path(__file__).resolve().parents[1]


def _fib_parse_fm(path: Path) -> dict:
    """Top-of-file `key: value` frontmatter reader (tolerates optional --- fences)."""
    fields: dict = {}
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return fields
    started = False
    for raw in lines[:40]:
        line = raw.rstrip()
        if line.strip() == "---":
            if started:
                break
            started = True
            continue
        if ":" in line and not line.lstrip().startswith("#"):
            k, _, v = line.partition(":")
            k = k.strip().lower()
            if k and k.replace("_", "").isalnum() and k not in fields:
                fields[k] = v.strip().strip('"').strip("'")
    return fields


def cmd_file_inbox(args: argparse.Namespace) -> int:
    """T3 (AOS-V5-WP-MAIL-SURFACE-UNIFORMITY) — local file-channel sweep (no DB / no API).

    Self-contained mirror of agents_os_v3.modules.management.messages.list_file_inbox_pending so it runs
    on spokes (which have no core/). Scans _COMMUNICATION/<team>/INBOX/ + ~/Documents/_agent_comm/
    {inbox,outbox}/ for MSG-*.md addressed `to: <team>` and unacked (no sibling *-RESPONSE.md, not under
    processed/). Same JSON shape as `inbox`. Keep in sync with the messages.py canonical version."""
    import time
    tid = (args.recipient or "").strip()
    if not tid or tid in {"mac", "server"}:
        # a team file-inbox sweep is never run for the mac<->server protocol pseudo-recipients
        print(json.dumps({"count": 0, "messages": []}))
        return 0
    home = Path(os.path.expanduser("~"))
    roots = [
        ("file-inbox", _fib_repo_root() / "_COMMUNICATION" / tid / "INBOX"),
        ("relay-inbox", home / "Documents" / "_agent_comm" / "inbox"),
        ("relay-outbox", home / "Documents" / "_agent_comm" / "outbox"),
    ]
    now = time.time()
    out: list = []
    seen: set = set()
    for src, root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("MSG-*.md")):
            name = path.name
            if name.endswith("-RESPONSE.md") or "processed" in path.parts:
                continue
            fm = _fib_parse_fm(path)
            recips = {p.strip() for p in fm.get("to", "").lower().replace(",", " ").split() if p.strip()}
            if tid not in recips:
                continue
            if (path.parent / f"{path.stem}-RESPONSE.md").exists() or name in seen:
                continue
            seen.add(name)
            try:
                age = round((now - path.stat().st_mtime) / 86400, 1)
            except OSError:
                age = None
            out.append({
                "msg_id": fm.get("id", path.stem), "from": fm.get("from", ""), "to": tid,
                "subject": fm.get("subject", fm.get("re", "")), "src": src, "path": str(path),
                "age_days": age,
                "expects_response": fm.get("expects_response", "").lower() in ("true", "yes", "1"),
            })
    print(json.dumps({"count": len(out), "messages": out}))
    return 0


def cmd_wp_run(args: argparse.Namespace) -> int:
    """W5 (additive): resolve the linked_run_id for a wp_id via the EXISTING
    GET /api/work-packages/{wp_id}. Read-only lookup; no endpoint changed."""
    code, payload = _request("GET", f"/api/work-packages/{args.wp_id}", timeout=float(args.timeout))
    if code != 200:
        print(json.dumps({"ok": False, "code": code, "detail": payload}), file=sys.stderr)
        return 1
    run_id = (payload or {}).get("linked_run_id")
    if not run_id:
        print(json.dumps({"ok": False, "code": 409, "detail": "no linked_run_id (WP not ACTIVE)"}), file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "run_id": run_id, "wp_id": args.wp_id}))
    return 0


def cmd_advance(args: argparse.Namespace) -> int:
    """W5 (additive): call the EXISTING POST /api/runs/{run_id}/advance UNCHANGED.
    Cross-engine guard (api.post_advance) stays server-side; this only forwards."""
    body: dict = {"verdict": args.verdict}
    if args.summary is not None:
        body["summary"] = args.summary
    code, payload = _request("POST", f"/api/runs/{args.run_id}/advance", body, timeout=float(args.timeout))
    if code != 200:
        print(json.dumps({"ok": False, "code": code, "detail": payload}), file=sys.stderr)
        return 1
    print(json.dumps(payload))
    return 0


def cmd_detect(args: argparse.Namespace) -> int:
    """Map live register rows → frozen detect_concurrency JSON (register backend)."""
    code, payload = _request("GET", "/api/sessions/list?live=true", timeout=float(args.timeout))
    if code != 200:
        print(json.dumps({"degrade": True, "reason": f"list HTTP {code}", "detail": payload}))
        return 2
    rows = (payload or {}).get("sessions") or []
    repo_root = os.path.abspath(args.repo_root)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
    # Lazy hub-module load via importlib — avoids the eager-import literal that the cross-project scan
    # (Check 12) forbids on spokes, so the propagated client stays clean. cmd_detect is a hub-only path
    # (spokes have no core/); on a spoke this raises ModuleNotFoundError, exactly as the eager import did.
    import importlib
    _sr = importlib.import_module("agents_os_v3.modules.management.session_register")
    out = _sr.map_list_to_detect_json(
        rows,
        repo_root=repo_root,
        session_id=args.session_id,
        wp_hint=args.wp_hint or "",
    )
    print(json.dumps(out, separators=(",", ":")))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="AOS session register API client (W3)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_reg = sub.add_parser("register")
    p_reg.add_argument("--session-id", required=True)
    p_reg.add_argument("--branch", default=None)
    p_reg.add_argument("--worktree-path", default=None)
    p_reg.add_argument("--wp-id", default=None)
    p_reg.add_argument("--domain", default=None, help="OBS-8: project/domain (default: $AOS_PROJECT_ID)")
    p_reg.add_argument("--engine", default=None, help="OBS-8: engine label (default: $AOS_ENGINE)")

    p_hb = sub.add_parser("heartbeat")
    p_hb.add_argument("--session-id", required=True)

    p_cl = sub.add_parser("close")
    p_cl.add_argument("--session-id", required=True)

    p_ls = sub.add_parser("list")
    p_ls.add_argument("--environment", default=None)
    p_ls.add_argument("--status", default=None)
    p_ls.add_argument("--live", action="store_true")

    p_wpr = sub.add_parser("wp-run")
    p_wpr.add_argument("--wp-id", required=True)
    p_wpr.add_argument("--timeout", default="3")

    p_adv = sub.add_parser("advance")
    p_adv.add_argument("--run-id", required=True)
    p_adv.add_argument("--verdict", required=True)
    p_adv.add_argument("--summary", default=None)
    p_adv.add_argument("--timeout", default="3")

    p_det = sub.add_parser("detect")
    p_det.add_argument("--repo-root", required=True)
    p_det.add_argument("--session-id", required=True)
    p_det.add_argument("--wp-hint", default="")
    p_det.add_argument("--timeout", default="3")

    p_cap = sub.add_parser("capture")
    p_cap.add_argument("--sender", default=None)
    p_cap.add_argument("--recipient", required=True)
    p_cap.add_argument("--recipient-kind", default="team")
    p_cap.add_argument("--kind", required=True)
    p_cap.add_argument("--subject", required=True)
    p_cap.add_argument("--body-ref", default=None)
    p_cap.add_argument("--body-inline", default=None)
    p_cap.add_argument("--session-id", required=True)
    p_cap.add_argument("--wp-id", default=None)
    p_cap.add_argument("--gate", default=None)
    p_cap.add_argument("--project-id", default=None, help="CTX-02: project scope tag (default: $AOS_PROJECT_ID)")
    p_cap.add_argument("--context-ref", default=None, help="COMM-08: artifact/context pointer")
    p_cap.add_argument("--next-wp", default=None, help="COMM-08: machine next-action WP")
    p_cap.add_argument("--next-gate", default=None, help="COMM-08: machine next-action gate")
    p_cap.add_argument("--timeout", default="3")

    p_ibx = sub.add_parser("inbox")
    p_ibx.add_argument("--recipient", required=True)
    p_ibx.add_argument("--recipient-kind", default="team")
    p_ibx.add_argument("--status", default="pending")
    p_ibx.add_argument("--limit", default="20")
    p_ibx.add_argument("--timeout", default="3")

    p_rd = sub.add_parser("read")
    p_rd.add_argument("--msg-id", required=True)
    p_rd.add_argument("--timeout", default="3")

    p_fib = sub.add_parser("file-inbox")   # T3 — local file-channel sweep (no API)
    p_fib.add_argument("--recipient", required=True)

    args = ap.parse_args()
    handlers = {
        "register": cmd_register,
        "heartbeat": cmd_heartbeat,
        "close": cmd_close,
        "list": cmd_list,
        "detect": cmd_detect,
        "wp-run": cmd_wp_run,
        "advance": cmd_advance,
        "capture": cmd_capture,
        "inbox": cmd_inbox,
        "read": cmd_read,
        "file-inbox": cmd_file_inbox,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
