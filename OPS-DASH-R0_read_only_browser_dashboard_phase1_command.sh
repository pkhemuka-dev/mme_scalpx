#!/usr/bin/env bash
set -Eeuo pipefail

# OPS-DASH-R0: read-only browser dashboard MVP.
# Evidence-derived for current MME-ScalpX repo structure.
# Safety: no Redis writes, no service start/stop, no broker calls, no orders, no paper/live controls.

cd /home/Lenovo/scalpx/projects/mme_scalpx

BATCH="OPS-DASH-R0_READ_ONLY_BROWSER_DASHBOARD_MVP_NO_REDIS_WRITE_NO_START_NO_ORDER_NO_PAPER"
PURPOSE="create_local_browser_dashboard_compile_ast_smoke_no_runtime_start"
TS="$(date +%Y%m%d_%H%M%S)"
TAG="${BATCH}_${PURPOSE}_${TS}"

mkdir -p app/mme_scalpx/ops_dashboard run/proofs run/audits docs/milestones docs/runbooks run/handoffs run/patches run/_code_backups

PROOF="run/proofs/${TAG}.json"
AUDIT="run/audits/${TAG}_audit.json"
REPORT="run/audits/${TAG}_report.md"
MILESTONE="docs/milestones/${TAG}.md"
RUNBOOK="docs/runbooks/${TAG}_runbook.md"
HANDOFF="run/handoffs/${TAG}_handoff.md"
PATCH_DIFF="run/patches/${TAG}_patch.diff"

export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_CONTROLLED_PAPER_SCOPE_ACK || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_ALLOW_BROKER_ORDERS || true
unset SCALPX_PAPER_ARMED || true
unset SCALPX_ENABLE_PAPER || true
unset SCALPX_ENABLE_LIVE || true
unset MME_ALLOW_BROKER_ORDERS || true
unset MME_ENABLE_PAPER || true
unset MME_ENABLE_LIVE || true

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then PY="python3"; fi

r_xlen() { redis-cli XLEN "$1" 2>/dev/null || echo REDIS_UNAVAILABLE; }
r_type() { redis-cli TYPE "$1" 2>/dev/null || echo REDIS_UNAVAILABLE; }
r_pttl() { redis-cli PTTL "$1" 2>/dev/null || echo REDIS_UNAVAILABLE; }

ORDERS_BEFORE="$(r_xlen orders:mme:stream)"
RISK_BEFORE="$(r_xlen risk:mme:stream)"
EXEC_BEFORE="$(r_xlen execution:mme:stream)"
LOCK_FEEDS_TYPE_BEFORE="$(r_type lock:feeds)"
LOCK_EXEC_TYPE_BEFORE="$(r_type lock:execution)"
LOCK_FEEDS_PTTL_BEFORE="$(r_pttl lock:feeds)"
LOCK_EXEC_PTTL_BEFORE="$(r_pttl lock:execution)"
RISK_PIDS_BEFORE="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service risk' | grep -v grep | wc -l | tr -d ' ')"
EXEC_PIDS_BEFORE="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service execution' | grep -v grep | wc -l | tr -d ' ')"

# Back up only if dashboard files already exist.
if [ -f app/mme_scalpx/ops_dashboard/server.py ]; then
  cp -a app/mme_scalpx/ops_dashboard/server.py "run/_code_backups/${TAG}_server.py.bak"
fi
if [ -f app/mme_scalpx/ops_dashboard/__init__.py ]; then
  cp -a app/mme_scalpx/ops_dashboard/__init__.py "run/_code_backups/${TAG}___init__.py.bak"
fi

cat > app/mme_scalpx/ops_dashboard/__init__.py <<'PY_INIT'
"""Read-only browser dashboard for MME-ScalpX operator visibility."""
PY_INIT

cat > app/mme_scalpx/ops_dashboard/server.py <<'PY_SERVER'
"""
MME-ScalpX OPS Dashboard R0.

Read-only local browser dashboard over existing Redis and artifact surfaces.

Safety contract
---------------
- No Redis writes.
- No broker calls.
- No service start/stop.
- No order, paper, or live enablement controls.
- Defaults to 127.0.0.1 only; pass --host 0.0.0.0 intentionally for LAN/mobile view.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlparse

try:  # redis is already a project dependency.
    import redis
except Exception:  # pragma: no cover - graceful dashboard degradation.
    redis = None  # type: ignore[assignment]

try:
    from app.mme_scalpx.core import names
except Exception:  # pragma: no cover - fallback keeps dashboard importable during rescue.
    names = None  # type: ignore[assignment]

DASHBOARD_VERSION: Final[str] = "OPS-DASH-R0"
DEFAULT_HOST: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 8765


def _name(attr: str, fallback: str) -> str:
    return str(getattr(names, attr, fallback)) if names is not None else fallback


STREAMS: Final[tuple[tuple[str, str], ...]] = (
    ("fut zerodha", _name("STREAM_TICKS_MME_FUT_ZERODHA", "ticks:mme:fut:zerodha:stream")),
    ("fut dhan", _name("STREAM_TICKS_MME_FUT_DHAN", "ticks:mme:fut:dhan:stream")),
    ("opt selected zerodha", _name("STREAM_TICKS_MME_OPT_SELECTED_ZERODHA", "ticks:mme:opt:selected:zerodha:stream")),
    ("opt selected dhan", _name("STREAM_TICKS_MME_OPT_SELECTED_DHAN", "ticks:mme:opt:selected:dhan:stream")),
    ("opt context dhan", _name("STREAM_TICKS_MME_OPT_CONTEXT_DHAN", "ticks:mme:opt:context:dhan:stream")),
    ("features", _name("STREAM_FEATURES_MME", "features:mme:stream")),
    ("decisions", _name("STREAM_DECISIONS_MME", "decisions:mme:stream")),
    ("risk", _name("STREAM_RISK_MME", "risk:mme:stream")),
    ("execution", _name("STREAM_EXECUTION_MME", "execution:mme:stream")),
    ("errors", _name("STREAM_SYSTEM_ERRORS", "system:errors:stream")),
    ("orders", _name("STREAM_ORDERS_MME", "orders:mme:stream")),
)

LOCKS: Final[tuple[tuple[str, str], ...]] = (
    ("feeds", _name("KEY_LOCK_FEEDS", "lock:feeds")),
    ("execution", _name("KEY_LOCK_EXECUTION", "lock:execution")),
)

STATE_HASHES: Final[tuple[tuple[str, str], ...]] = (
    ("position", _name("HASH_STATE_POSITION_MME", "state:position:mme")),
)

HEALTH_KEYS: Final[tuple[tuple[str, str], ...]] = (
    ("login", _name("KEY_HEALTH_LOGIN", "health:login")),
    ("instruments", _name("KEY_HEALTH_INSTRUMENTS", "health:instruments")),
    ("feeds", _name("KEY_HEALTH_FEEDS", "health:feeds")),
    ("features", _name("KEY_HEALTH_FEATURES", "health:features")),
    ("strategy", _name("KEY_HEALTH_STRATEGY", "health:strategy")),
    ("risk", _name("KEY_HEALTH_RISK", "health:risk")),
    ("execution", _name("KEY_HEALTH_EXECUTION", "health:execution")),
    ("zerodha auth", _name("KEY_HEALTH_ZERODHA_AUTH", "health:zerodha:auth")),
    ("zerodha marketdata", _name("KEY_HEALTH_ZERODHA_MARKETDATA", "health:zerodha:marketdata")),
    ("dhan auth", _name("KEY_HEALTH_DHAN_AUTH", "health:dhan:auth")),
    ("dhan marketdata", _name("KEY_HEALTH_DHAN_MARKETDATA", "health:dhan:marketdata")),
    ("provider runtime", _name("KEY_HEALTH_PROVIDER_RUNTIME", "health:provider:runtime")),
)

RISKY_ENV_FLAGS: Final[tuple[str, ...]] = (
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
    "SCALPX_REAL_LIVE_ALLOWED",
    "SCALPX_ALLOW_REAL_LIVE",
    "SCALPX_ALLOW_BROKER_ORDERS",
    "SCALPX_PAPER_ARMED",
    "SCALPX_ENABLE_PAPER",
    "SCALPX_ENABLE_LIVE",
    "MME_ALLOW_BROKER_ORDERS",
    "MME_ENABLE_PAPER",
    "MME_ENABLE_LIVE",
)

SERVICE_TOKENS: Final[dict[str, tuple[str, ...]]] = {
    "feeds": ("app.mme_scalpx.main", "--service", "feeds"),
    "features": ("app.mme_scalpx.main", "--service", "features"),
    "strategy": ("app.mme_scalpx.main", "--service", "strategy"),
    "risk": ("app.mme_scalpx.main", "--service", "risk"),
    "execution": ("app.mme_scalpx.main", "--service", "execution"),
}


def _project_root() -> Path:
    env_root = os.getenv("MME_PROJECT_ROOT") or os.getenv("SCALPX_PROJECT_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _redis_url() -> str:
    return (
        os.getenv("MME_REDIS_URL")
        or os.getenv("SCALPX_REDIS_URL")
        or os.getenv("REDIS_URL")
        or "redis://localhost:6379/0"
    )


def _redis_client() -> Any:
    if redis is None:
        raise RuntimeError("redis package is not importable")
    return redis.Redis.from_url(
        _redis_url(),
        decode_responses=True,
        socket_connect_timeout=1.0,
        socket_timeout=1.0,
        health_check_interval=15,
    )


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _maybe_json(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    raw = value.strip()
    if not raw or raw[0] not in "[{\"":
        return value
    try:
        return json.loads(raw)
    except Exception:
        return value


def _compact_fields(fields: dict[str, Any], limit: int = 40) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in list(fields.items())[:limit]:
        decoded = _maybe_json(value)
        if isinstance(decoded, (dict, list)):
            rendered = json.dumps(decoded, ensure_ascii=False, sort_keys=True)
            out[str(key)] = rendered[:500]
        else:
            out[str(key)] = str(decoded)[:500]
    return out


def _first_present(mapping: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    lowered = {str(k).lower(): v for k, v in mapping.items()}
    for key in keys:
        value = lowered.get(key.lower())
        if value not in (None, ""):
            return str(value)
    return None


def _decode_latest_entry(client: Any, stream: str) -> dict[str, Any] | None:
    rows = client.xrevrange(stream, max="+", min="-", count=1)
    if not rows:
        return None
    entry_id, fields = rows[0]
    if not isinstance(fields, dict):
        fields = {}
    compact = _compact_fields(fields)
    return {"id": str(entry_id), "fields": compact}


def _stream_snapshot(client: Any, label: str, stream: str) -> dict[str, Any]:
    try:
        length = _safe_int(client.xlen(stream))
        latest = _decode_latest_entry(client, stream) if length > 0 else None
        if length <= 0:
            status = "IDLE"
        elif label == "errors" and length > 0:
            status = "WARN"
        elif label == "orders" and length > 0:
            status = "DANGER"
        else:
            status = "LIVE"
        return {"label": label, "stream": stream, "length": length, "latest": latest, "status": status}
    except Exception as exc:
        return {"label": label, "stream": stream, "length": None, "latest": None, "status": "UNAVAILABLE", "error": str(exc)[:240]}


def _lock_snapshot(client: Any, label: str, key: str) -> dict[str, Any]:
    try:
        key_type = client.type(key)
        ttl_ms = client.pttl(key)
        value: str | None = None
        if key_type == "string":
            value = client.get(key)
        return {"label": label, "key": key, "type": key_type, "ttl_ms": ttl_ms, "value": value, "locked": ttl_ms and ttl_ms > 0}
    except Exception as exc:
        return {"label": label, "key": key, "type": "unknown", "ttl_ms": None, "value": None, "locked": False, "error": str(exc)[:240]}


def _hash_snapshot(client: Any, label: str, key: str) -> dict[str, Any]:
    try:
        payload = client.hgetall(key)
        if not isinstance(payload, dict):
            payload = {}
        return {"label": label, "key": key, "fields": _compact_fields(payload), "exists": bool(payload)}
    except Exception as exc:
        return {"label": label, "key": key, "fields": {}, "exists": False, "error": str(exc)[:240]}


def _health_snapshot(client: Any, label: str, key: str) -> dict[str, Any]:
    item = _hash_snapshot(client, label, key)
    fields = item.get("fields", {}) if isinstance(item.get("fields"), dict) else {}
    ttl_ms: int | None
    try:
        ttl_ms = client.pttl(key)
    except Exception:
        ttl_ms = None
    status = _first_present(fields, ("status", "health", "state", "provider_status"))
    item.update({"ttl_ms": ttl_ms, "status": status or ("PRESENT" if item.get("exists") else "MISSING")})
    return item


def _latest_files(root: Path, relative_dir: str, suffixes: tuple[str, ...], limit: int = 5) -> list[dict[str, Any]]:
    base = root / relative_dir
    if not base.exists():
        return []
    files = [p for p in base.iterdir() if p.is_file() and p.name.endswith(suffixes)]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    out = []
    for path in files[:limit]:
        st = path.stat()
        out.append(
            {
                "name": path.name,
                "path": str(path.relative_to(root)),
                "size_bytes": st.st_size,
                "modified_epoch": st.st_mtime,
                "modified": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
            }
        )
    return out


def _read_pointer(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        return {"path": relative_path, "exists": path.exists(), "value": path.read_text(encoding="utf-8", errors="replace").strip()[:1000] if path.exists() else None}
    except Exception as exc:
        return {"path": relative_path, "exists": False, "value": None, "error": str(exc)[:240]}


def _process_snapshot() -> dict[str, Any]:
    result: dict[str, Any] = {name: 0 for name in SERVICE_TOKENS}
    proc = Path("/proc")
    if not proc.exists():
        result["unsupported"] = True  # type: ignore[index]
        return result
    for item in proc.iterdir():
        if not item.name.isdigit():
            continue
        try:
            raw = (item / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", "ignore")
        except Exception:
            continue
        for service, tokens in SERVICE_TOKENS.items():
            if all(token in raw for token in tokens):
                result[service] = result.get(service, 0) + 1
    return result


def _safety_from_snapshot(streams: list[dict[str, Any]], hashes: list[dict[str, Any]], locks: list[dict[str, Any]]) -> dict[str, Any]:
    by_label = {item["label"]: item for item in streams}
    orders_len = by_label.get("orders", {}).get("length")
    risk_len = by_label.get("risk", {}).get("length")
    execution_len = by_label.get("execution", {}).get("length")
    position_fields = next((h.get("fields", {}) for h in hashes if h.get("label") == "position"), {})
    position_state = _first_present(position_fields if isinstance(position_fields, dict) else {}, ("has_position", "position", "side", "state")) or "UNKNOWN"
    risky_flags = {name: os.getenv(name) for name in RISKY_ENV_FLAGS if os.getenv(name) not in (None, "", "0", "false", "False", "off", "OFF")}
    danger = bool(_safe_int(orders_len) > 0 or risky_flags)
    return {
        "orders_stream_length": orders_len,
        "risk_stream_length": risk_len,
        "execution_stream_length": execution_len,
        "position_state": position_state,
        "risky_env_flags_set": risky_flags,
        "locks": locks,
        "read_only_contract": True,
        "danger": danger,
    }


def _latest_decision(streams: list[dict[str, Any]]) -> dict[str, Any]:
    decision_stream = next((item for item in streams if item.get("label") == "decisions"), None)
    if not decision_stream or not decision_stream.get("latest"):
        return {"present": False}
    latest = decision_stream["latest"]
    fields = latest.get("fields", {}) if isinstance(latest, dict) else {}
    if not isinstance(fields, dict):
        fields = {}
    return {
        "present": True,
        "id": latest.get("id"),
        "action": _first_present(fields, ("action", "decision_action", "signal", "status")) or "UNKNOWN",
        "family": _first_present(fields, ("family", "strategy_family", "strategy_id", "strategy")) or "UNKNOWN",
        "branch": _first_present(fields, ("branch", "side", "option_side")) or "UNKNOWN",
        "blocker": _first_present(fields, ("blocker", "blocker_reason", "reason", "reject_reason", "status_reason")) or "UNKNOWN",
        "selected_option": _first_present(fields, ("selected_option", "instrument_key", "tradingsymbol", "symbol")) or "UNKNOWN",
        "fields": fields,
    }


def build_snapshot() -> dict[str, Any]:
    root = _project_root()
    snapshot: dict[str, Any] = {
        "version": DASHBOARD_VERSION,
        "created_at_utc": _utc_now(),
        "project_root": str(root),
        "redis_url_source": "MME_REDIS_URL/SCALPX_REDIS_URL/REDIS_URL/default",
        "redis_connected": False,
        "redis_error": None,
        "streams": [],
        "locks": [],
        "state_hashes": [],
        "health": [],
        "processes": _process_snapshot(),
        "artifacts": {
            "proofs": _latest_files(root, "run/proofs", (".json",), 8),
            "milestones": _latest_files(root, "docs/milestones", (".md",), 8),
            "runbooks": _latest_files(root, "docs/runbooks", (".md",), 8),
            "evidence_bundles": _latest_files(root, "run/evidence_bundles", (".tar.gz", ".tgz", ".zip"), 8),
            "latest_evidence_pointer": _read_pointer(root, "run/evidence_bundles/LATEST_EVIDENCE_BUNDLE.txt"),
            "latest_live_handoff_pointer": _read_pointer(root, "run/handoffs/LATEST_LIVE_OBSERVE_ONLY_SEALED_HANDOFF.txt"),
        },
        "environment": {
            "observe_only": os.getenv("SCALPX_OBSERVE_ONLY") or os.getenv("MME_OBSERVE_ONLY"),
            "host_default": DEFAULT_HOST,
        },
    }
    try:
        client = _redis_client()
        client.ping()
        snapshot["redis_connected"] = True
        streams = [_stream_snapshot(client, label, stream) for label, stream in STREAMS]
        locks = [_lock_snapshot(client, label, key) for label, key in LOCKS]
        hashes = [_hash_snapshot(client, label, key) for label, key in STATE_HASHES]
        snapshot["streams"] = streams
        snapshot["locks"] = locks
        snapshot["state_hashes"] = hashes
        snapshot["health"] = [_health_snapshot(client, label, key) for label, key in HEALTH_KEYS]
        snapshot["latest_decision"] = _latest_decision(streams)
        snapshot["safety"] = _safety_from_snapshot(streams, hashes, locks)
    except Exception as exc:
        snapshot["redis_error"] = str(exc)[:400]
        snapshot["latest_decision"] = {"present": False}
        snapshot["safety"] = {"read_only_contract": True, "danger": False, "redis_unavailable": True}
    return snapshot


INDEX_HTML: Final[str] = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>MME-ScalpX OPS Dashboard R0</title>
  <style>
    :root { color-scheme: dark; --bg:#07111f; --panel:#101c2d; --panel2:#0d1929; --line:#233a59; --text:#eaf3ff; --muted:#9eb3cc; --blue:#51a8ff; --green:#34d05c; --yellow:#f5c542; --red:#ff5a5f; --purple:#c782ff; }
    *{box-sizing:border-box} body{margin:0;background:radial-gradient(circle at top left,#10233f 0,#07111f 42%,#050b14 100%);font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--text)}
    header{height:72px;display:flex;align-items:center;justify-content:space-between;padding:0 20px;border-bottom:1px solid var(--line);background:rgba(5,13,24,.82);position:sticky;top:0;z-index:3;backdrop-filter:blur(8px)}
    .brand{display:flex;gap:14px;align-items:center}.brand b{font-size:21px}.brand span{font-size:13px;color:var(--muted)}.pill{border:1px solid var(--line);background:#0c192b;border-radius:999px;padding:7px 11px;font-size:12px}.ok{color:var(--green)}.warn{color:var(--yellow)}.bad{color:var(--red)}.blue{color:var(--blue)}
    .layout{display:grid;grid-template-columns:210px 1fr;min-height:calc(100vh - 72px)}
    aside{border-right:1px solid var(--line);padding:18px 14px;background:rgba(8,17,30,.7)} aside .nav{display:grid;gap:8px} aside a{color:var(--text);text-decoration:none;padding:12px;border-radius:10px;background:transparent} aside a.active,aside a:hover{background:linear-gradient(135deg,#1b63b6,#16345f)} .r0{margin-top:36px;border:1px solid var(--blue);border-radius:12px;padding:14px;color:var(--muted);font-size:12px;line-height:1.8}.r0 b{color:var(--blue)}
    main{padding:20px;display:grid;gap:16px}.cards{display:grid;grid-template-columns:repeat(5,minmax(150px,1fr));gap:14px}.card,.panel{background:linear-gradient(180deg,rgba(18,34,54,.94),rgba(11,23,38,.94));border:1px solid var(--line);border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.20)}.card{padding:18px}.label{font-size:12px;color:#cfe0f6;font-weight:700;text-transform:uppercase}.big{font-size:28px;font-weight:800;margin-top:16px}.sub{color:var(--muted);font-size:13px;margin-top:8px}.grid{display:grid;grid-template-columns:1.25fr .85fr;gap:16px}.panel{padding:16px;overflow:hidden}.panel h2{margin:0 0 14px;font-size:15px}.table{width:100%;border-collapse:collapse;font-size:13px}.table th{text-align:left;color:#bdd1eb;font-size:11px;text-transform:uppercase;padding:8px;border-bottom:1px solid var(--line)}.table td{padding:8px;border-bottom:1px solid rgba(35,58,89,.55);vertical-align:top}.badge{border-radius:7px;padding:3px 7px;font-size:11px;font-weight:800;display:inline-block}.LIVE,.GOOD,.ON,.LOCKED{background:#103e22;color:var(--green)}.WARN{background:#4a3d10;color:var(--yellow)}.DANGER,.BAD,.OFF{background:#4a1e24;color:var(--red)}.IDLE,.UNAVAILABLE,.UNKNOWN{background:#143250;color:#8fc6ff}.mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.kv{display:grid;grid-template-columns:170px 1fr;gap:10px;border-bottom:1px solid rgba(35,58,89,.55);padding:9px 0;font-size:13px}.kv span:first-child{color:#bdd1eb}.footer{color:var(--muted);font-size:12px;border-top:1px solid var(--line);padding:12px 20px}.small{font-size:12px;color:var(--muted)}
    @media(max-width:900px){header{height:auto;align-items:flex-start;gap:10px;flex-direction:column;padding:14px}.layout{grid-template-columns:1fr}aside{display:none}main{padding:12px}.cards{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.table{font-size:12px}.kv{grid-template-columns:1fr}.brand b{font-size:18px}}
    @media(max-width:520px){.cards{grid-template-columns:1fr}.card{padding:15px}.big{font-size:24px}}
  </style>
</head>
<body>
<header>
  <div class="brand"><b>MME-Scalp<span class="blue">X</span></b><span>OPS DASHBOARD · R0 READ ONLY</span></div>
  <div><span id="healthPill" class="pill">Loading...</span> <span id="updated" class="pill">--</span></div>
</header>
<div class="layout">
<aside><div class="nav"><a class="active">Overview</a><a>Streams</a><a>Strategy</a><a>Safety</a><a>Evidence</a><a>Errors</a></div><div class="r0"><b>DASHBOARD R0</b><br/>READ ONLY<br/><br/>No Redis Writes<br/>No Service Start/Stop<br/>No Broker Calls<br/>No Orders<br/>No Paper/Live Controls</div></aside>
<main>
  <section class="cards">
    <div class="card"><div class="label">System Status</div><div id="systemStatus" class="big">--</div><div class="sub">Redis + process visibility</div></div>
    <div class="card"><div class="label">Feeds Health</div><div id="feedsStatus" class="big">--</div><div class="sub">Zerodha / Dhan streams</div></div>
    <div class="card"><div class="label">Decisions</div><div id="decisionCount" class="big">--</div><div class="sub">decisions:mme:stream</div></div>
    <div class="card"><div class="label">Errors</div><div id="errorCount" class="big">--</div><div class="sub">system:errors:stream</div></div>
    <div class="card"><div class="label">Orders</div><div id="orderCount" class="big">--</div><div class="sub">orders:mme:stream</div></div>
  </section>
  <section class="grid">
    <div class="panel"><h2>Redis Stream Health</h2><div id="streams"></div></div>
    <div class="panel"><h2>Latest Strategy View</h2><div id="decision"></div></div>
  </section>
  <section class="grid">
    <div class="panel"><h2>Safety Panel</h2><div id="safety"></div></div>
    <div class="panel"><h2>Provider / Service Health</h2><div id="providers"></div></div>
  </section>
  <section class="grid">
    <div class="panel"><h2>Evidence & Proofs</h2><div id="artifacts"></div></div>
    <div class="panel"><h2>Quick Info</h2><div id="quick"></div></div>
  </section>
</main>
</div>
<div class="footer">MME-ScalpX OPS Dashboard R0 | Read Only | No Redis Write | No Orders | No Paper/Live Controls</div>
<script>
const esc = (v)=>String(v ?? '').replace(/[&<>'"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
const cls = (s)=>['LIVE','GOOD','ON','LOCKED'].includes(s)?'LIVE':(['WARN'].includes(s)?'WARN':(['DANGER','BAD','OFF'].includes(s)?'DANGER':'IDLE'));
const badge = (s)=>`<span class="badge ${cls(s)}">${esc(s)}</span>`;
const byLabel = (arr,l)=> (arr||[]).find(x=>x.label===l)||{};
function kv(k,v){return `<div class="kv"><span>${esc(k)}</span><b>${esc(v)}</b></div>`}
function render(d){
  const redisOk = !!d.redis_connected;
  const orders = byLabel(d.streams,'orders'); const errors = byLabel(d.streams,'errors'); const decisions = byLabel(d.streams,'decisions');
  document.getElementById('healthPill').innerHTML = redisOk ? '<span class="ok">● SYSTEM HEALTH: CONNECTED</span>' : '<span class="bad">● REDIS UNAVAILABLE</span>';
  document.getElementById('updated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
  document.getElementById('systemStatus').innerHTML = redisOk ? '<span class="ok">Running</span>' : '<span class="bad">Offline</span>';
  const liveFeeds = ['fut zerodha','fut dhan','opt selected zerodha','opt selected dhan','opt context dhan'].filter(x=>byLabel(d.streams,x).status==='LIVE').length;
  document.getElementById('feedsStatus').innerHTML = `<span class="ok">${liveFeeds} / 5</span>`;
  document.getElementById('decisionCount').innerHTML = `<span style="color:var(--purple)">${esc(decisions.length ?? 0)}</span>`;
  document.getElementById('errorCount').innerHTML = `<span class="${(errors.length||0)>0?'warn':'ok'}">${esc(errors.length ?? 0)}</span>`;
  document.getElementById('orderCount').innerHTML = `<span class="${(orders.length||0)>0?'bad':'blue'}">${esc(orders.length ?? 0)}</span>`;
  document.getElementById('streams').innerHTML = `<table class="table"><thead><tr><th>Label</th><th>Stream</th><th>Length</th><th>Last ID</th><th>Status</th></tr></thead><tbody>` + (d.streams||[]).map(s=>`<tr><td>${esc(s.label)}</td><td class="mono">${esc(s.stream)}</td><td>${esc(s.length)}</td><td class="mono">${esc(s.latest && s.latest.id || '-')}</td><td>${badge(s.status)}</td></tr>`).join('') + `</tbody></table>`;
  const dec = d.latest_decision || {};
  document.getElementById('decision').innerHTML = dec.present ? [kv('Entry ID', dec.id),kv('Action', dec.action),kv('Family', dec.family),kv('Branch', dec.branch),kv('Selected Option', dec.selected_option),kv('Blocker / Reason', dec.blocker)].join('') : '<p class="small">No latest decision visible.</p>';
  const safe = d.safety || {}; const flags = safe.risky_env_flags_set || {};
  document.getElementById('safety').innerHTML = [kv('Read-only contract','TRUE'),kv('Orders Stream Length',safe.orders_stream_length),kv('Risk Stream Length',safe.risk_stream_length),kv('Execution Stream Length',safe.execution_stream_length),kv('Position State',safe.position_state),kv('Risky Env Flags Set',Object.keys(flags).length?Object.keys(flags).join(', '):'NONE')].join('') + `<div class="kv"><span>Overall Safety</span><b>${safe.danger?badge('DANGER'):badge('GOOD')}</b></div>`;
  document.getElementById('providers').innerHTML = `<table class="table"><thead><tr><th>Key</th><th>Status</th><th>TTL</th></tr></thead><tbody>` + (d.health||[]).map(h=>`<tr><td>${esc(h.label)}</td><td>${badge((h.status||'UNKNOWN').toUpperCase())}</td><td>${esc(h.ttl_ms)}</td></tr>`).join('') + `</tbody></table>`;
  const art = d.artifacts || {}; const pf=(art.proofs||[])[0]; const ms=(art.milestones||[])[0]; const eb=(art.evidence_bundles||[])[0];
  document.getElementById('artifacts').innerHTML = [kv('Latest Proof', pf?pf.path:'-'),kv('Latest Milestone', ms?ms.path:'-'),kv('Latest Evidence Bundle', eb?eb.path:'-'),kv('Pointer', art.latest_evidence_pointer && art.latest_evidence_pointer.value || '-')].join('');
  const p=d.processes||{};
  document.getElementById('quick').innerHTML = [kv('Dashboard Version',d.version),kv('Project Root',d.project_root),kv('Redis Connected',redisOk?'YES':'NO'),kv('Redis Error',d.redis_error||'-'),kv('Processes feeds/features/strategy',`${p.feeds||0}/${p.features||0}/${p.strategy||0}`),kv('Processes risk/execution',`${p.risk||0}/${p.execution||0}`)].join('');
}
async function load(){try{const r=await fetch('/api/snapshot',{cache:'no-store'}); render(await r.json());}catch(e){document.getElementById('healthPill').innerHTML='<span class="bad">● DASHBOARD ERROR</span>';}}
load(); setInterval(load,2000);
</script>
</body>
</html>"""


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "MMEOPS/0.1"

    def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract.
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self._send_html(INDEX_HTML)
            return
        if path == "/api/snapshot":
            self._send_json(build_snapshot())
            return
        if path == "/healthz":
            self._send_json({"ok": True, "version": DASHBOARD_VERSION, "ts": _utc_now()})
            return
        self._send_json({"error": "not_found", "path": path}, HTTPStatus.NOT_FOUND)

    def log_message(self, fmt: str, *args: Any) -> None:
        ts = datetime.now().isoformat(timespec="seconds")
        print(f"{ts} dashboard_http {self.address_string()} {fmt % args}")


def run(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"{DASHBOARD_VERSION} read-only dashboard running at http://{host}:{port}")
    print("Safety: no Redis writes, no broker calls, no start/stop, no paper/live controls.")
    httpd.serve_forever(poll_interval=0.5)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MME-ScalpX read-only OPS Dashboard R0")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Bind host. Default is 127.0.0.1. Use 0.0.0.0 only for trusted LAN/VPN access.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port. Default 8765.")
    args = parser.parse_args(argv)
    run(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY_SERVER

COMPILE_OK=0
if "$PY" -m py_compile app/mme_scalpx/ops_dashboard/__init__.py app/mme_scalpx/ops_dashboard/server.py; then
  COMPILE_OK=1
fi

AST_AUDIT_OK=0
if "$PY" - <<'PY_AUDIT'
import ast
from pathlib import Path
p = Path('app/mme_scalpx/ops_dashboard/server.py')
tree = ast.parse(p.read_text(encoding='utf-8'))
forbidden = {
    'xadd','set','setex','psetex','hset','hmset','delete','unlink','publish',
    'lpush','rpush','sadd','zadd','expire','pexpire','eval','execute_command',
    'system','popen','run','call','check_call','check_output'
}
seen = []
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and node.attr in forbidden:
        seen.append((node.lineno, node.attr))
if seen:
    raise SystemExit(f'FORBIDDEN_METHOD_NAMES_FOUND={seen}')
print('AST_READ_ONLY_NO_REDIS_WRITE_NO_SUBPROCESS_METHODS_OK')
PY_AUDIT
then
  AST_AUDIT_OK=1
fi

IMPORT_SMOKE_OK=0
SNAPSHOT_SMOKE_OK=0
if PYTHONPATH="app:${PYTHONPATH:-}" "$PY" - <<'PY_SMOKE' > "run/audits/${TAG}_snapshot_smoke.json"
import json
from app.mme_scalpx.ops_dashboard.server import DASHBOARD_VERSION, build_snapshot
snap = build_snapshot()
out = {
    'version': DASHBOARD_VERSION,
    'redis_connected': snap.get('redis_connected'),
    'read_only_contract': snap.get('safety', {}).get('read_only_contract'),
    'stream_count': len(snap.get('streams', [])),
    'has_project_root': bool(snap.get('project_root')),
}
print(json.dumps(out, indent=2, sort_keys=True))
PY_SMOKE
then
  IMPORT_SMOKE_OK=1
  SNAPSHOT_SMOKE_OK=1
fi

ORDERS_AFTER="$(r_xlen orders:mme:stream)"
RISK_AFTER="$(r_xlen risk:mme:stream)"
EXEC_AFTER="$(r_xlen execution:mme:stream)"
RISK_PIDS_AFTER="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service risk' | grep -v grep | wc -l | tr -d ' ')"
EXEC_PIDS_AFTER="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service execution' | grep -v grep | wc -l | tr -d ' ')"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  git diff -- app/mme_scalpx/ops_dashboard > "$PATCH_DIFF" || true
else
  : > "$PATCH_DIFF"
fi

CLASSIFICATION="PASS_OPS_DASH_R0_READ_ONLY_DASHBOARD_CREATED_NO_START_NO_ORDER_NO_PAPER"
if [ "$COMPILE_OK" != "1" ] || [ "$AST_AUDIT_OK" != "1" ] || [ "$IMPORT_SMOKE_OK" != "1" ] || [ "$SNAPSHOT_SMOKE_OK" != "1" ]; then
  CLASSIFICATION="FAIL_OPS_DASH_R0_STATIC_OR_SMOKE_CHECK_FAILED"
fi

SNAPSHOT_JSON="$(cat "run/audits/${TAG}_snapshot_smoke.json" 2>/dev/null || echo '{}')"

cat > "$PROOF" <<JSON
{
  "batch": "$BATCH",
  "purpose": "$PURPOSE",
  "tag": "$TAG",
  "classification": "$CLASSIFICATION",
  "created_at_ist": "$(date -Is)",
  "source_patch": {
    "created_files": [
      "app/mme_scalpx/ops_dashboard/__init__.py",
      "app/mme_scalpx/ops_dashboard/server.py"
    ],
    "patch_diff": "$PATCH_DIFF"
  },
  "checks": {
    "compile_ok": $COMPILE_OK,
    "ast_read_only_no_redis_write_no_subprocess_methods_ok": $AST_AUDIT_OK,
    "import_smoke_ok": $IMPORT_SMOKE_OK,
    "snapshot_smoke_ok": $SNAPSHOT_SMOKE_OK,
    "snapshot_summary_compact": $SNAPSHOT_JSON
  },
  "safety": {
    "redis_writes_attempted": false,
    "service_start_attempted": false,
    "service_stop_attempted": false,
    "broker_call_attempted": false,
    "order_attempted": false,
    "paper_live_enablement_attempted": false,
    "orders_before": "$ORDERS_BEFORE",
    "orders_after": "$ORDERS_AFTER",
    "risk_stream_before": "$RISK_BEFORE",
    "risk_stream_after": "$RISK_AFTER",
    "execution_stream_before": "$EXEC_BEFORE",
    "execution_stream_after": "$EXEC_AFTER",
    "risk_pids_before": "$RISK_PIDS_BEFORE",
    "risk_pids_after": "$RISK_PIDS_AFTER",
    "execution_pids_before": "$EXEC_PIDS_BEFORE",
    "execution_pids_after": "$EXEC_PIDS_AFTER",
    "lock_feeds_type_before": "$LOCK_FEEDS_TYPE_BEFORE",
    "lock_execution_type_before": "$LOCK_EXEC_TYPE_BEFORE",
    "lock_feeds_pttl_before": "$LOCK_FEEDS_PTTL_BEFORE",
    "lock_execution_pttl_before": "$LOCK_EXEC_PTTL_BEFORE"
  },
  "run_commands": {
    "local_only": "$PY -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765",
    "trusted_lan_mobile_chrome": "$PY -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765"
  }
}
JSON
cp "$PROOF" "$AUDIT"

cat > "$REPORT" <<MD
# $BATCH

Classification: **$CLASSIFICATION**

## What changed
Created a first-phase read-only browser dashboard module:

- \`app/mme_scalpx/ops_dashboard/__init__.py\`
- \`app/mme_scalpx/ops_dashboard/server.py\`

## Safety contract
- No Redis writes
- No broker calls
- No service start/stop
- No orders
- No paper/live controls
- Default bind host: \`127.0.0.1\`

## Checks
- compile_ok=$COMPILE_OK
- ast_read_only_no_redis_write_no_subprocess_methods_ok=$AST_AUDIT_OK
- import_smoke_ok=$IMPORT_SMOKE_OK
- snapshot_smoke_ok=$SNAPSHOT_SMOKE_OK

## How to run after review
Local machine only:

\`\`\`bash
$PY -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765
\`\`\`

Trusted LAN/mobile Chrome:

\`\`\`bash
$PY -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765
\`\`\`

Then open browser:

\`\`\`text
http://127.0.0.1:8765
\`\`\`

For mobile Chrome on same network, open:

\`\`\`text
http://<VM_OR_LAPTOP_IP>:8765
\`\`\`

Proof: \`$PROOF\`
Patch diff: \`$PATCH_DIFF\`
MD

cp "$REPORT" "$MILESTONE"
cp "$REPORT" "$RUNBOOK"
cp "$REPORT" "$HANDOFF"

echo "===== OPS-DASH-R0 RESULT ====="
echo "classification=$CLASSIFICATION"
echo "proof=$PROOF"
echo "report=$REPORT"
echo "patch_diff=$PATCH_DIFF"
echo
if [ "$CLASSIFICATION" = "PASS_OPS_DASH_R0_READ_ONLY_DASHBOARD_CREATED_NO_START_NO_ORDER_NO_PAPER" ]; then
  echo "To run locally after review:"
  echo "  $PY -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765"
  echo "Open: http://127.0.0.1:8765"
  echo
  echo "For mobile Chrome on trusted same Wi-Fi/LAN:"
  echo "  $PY -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765"
  echo "Open: http://<VM_OR_LAPTOP_IP>:8765"
else
  echo "FAILED: inspect $REPORT and $PROOF before doing anything else."
  exit 1
fi
