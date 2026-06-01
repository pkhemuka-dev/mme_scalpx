#!/usr/bin/env bash
set -Eeuo pipefail

# OPS-DASH-R0B
# Small freeze-grade read-only browser dashboard MVP.
# Safety: no Redis writes, no service start/stop, no broker calls, no orders, no paper/live.

cd /home/Lenovo/scalpx/projects/mme_scalpx

BATCH="OPS-DASH-R0B_SMALL_READ_ONLY_BROWSER_DASHBOARD_NO_REDIS_WRITE_NO_START_NO_ORDER_NO_PAPER"
PURPOSE="create_small_stdlib_dashboard_compile_smoke_proof"
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
SNAPSHOT_SMOKE="run/audits/${TAG}_snapshot_smoke.json"

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

ORDERS_BEFORE="$(r_xlen orders:mme:stream)"
RISK_BEFORE="$(r_xlen risk:mme:stream)"
EXEC_BEFORE="$(r_xlen execution:mme:stream)"
RISK_PIDS_BEFORE="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service risk' | grep -v grep | wc -l | tr -d ' ')"
EXEC_PIDS_BEFORE="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service execution' | grep -v grep | wc -l | tr -d ' ')"

if [ -f app/mme_scalpx/ops_dashboard/server.py ]; then
  cp -a app/mme_scalpx/ops_dashboard/server.py "run/_code_backups/${TAG}_server.py.bak"
fi
if [ -f app/mme_scalpx/ops_dashboard/__init__.py ]; then
  cp -a app/mme_scalpx/ops_dashboard/__init__.py "run/_code_backups/${TAG}___init__.py.bak"
fi

cat > app/mme_scalpx/ops_dashboard/__init__.py <<'PY_INIT'
"""MME-ScalpX read-only OPS dashboard."""
PY_INIT

cat > app/mme_scalpx/ops_dashboard/server.py <<'PY_SERVER'
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import redis
except Exception:
    redis = None  # type: ignore[assignment]

try:
    from app.mme_scalpx.core import names
except Exception:
    names = None  # type: ignore[assignment]

VERSION = "OPS-DASH-R0B"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def n(attr: str, fallback: str) -> str:
    return str(getattr(names, attr, fallback)) if names is not None else fallback


STREAMS = [
    ("fut zerodha", n("STREAM_TICKS_MME_FUT_ZERODHA", "ticks:mme:fut:zerodha:stream")),
    ("fut dhan", n("STREAM_TICKS_MME_FUT_DHAN", "ticks:mme:fut:dhan:stream")),
    ("opt zerodha", n("STREAM_TICKS_MME_OPT_SELECTED_ZERODHA", "ticks:mme:opt:selected:zerodha:stream")),
    ("opt dhan", n("STREAM_TICKS_MME_OPT_SELECTED_DHAN", "ticks:mme:opt:selected:dhan:stream")),
    ("dhan context", n("STREAM_TICKS_MME_OPT_CONTEXT_DHAN", "ticks:mme:opt:context:dhan:stream")),
    ("features", n("STREAM_FEATURES_MME", "features:mme:stream")),
    ("decisions", n("STREAM_DECISIONS_MME", "decisions:mme:stream")),
    ("risk", n("STREAM_RISK_MME", "risk:mme:stream")),
    ("execution", n("STREAM_EXECUTION_MME", "execution:mme:stream")),
    ("errors", n("STREAM_SYSTEM_ERRORS", "system:errors:stream")),
    ("orders", n("STREAM_ORDERS_MME", "orders:mme:stream")),
]

LOCKS = [
    ("feeds", n("KEY_LOCK_FEEDS", "lock:feeds")),
    ("execution", n("KEY_LOCK_EXECUTION", "lock:execution")),
]

POSITION_HASH = n("HASH_STATE_POSITION_MME", "state:position:mme")

RISKY_ENV = [
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
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def redis_url() -> str:
    return os.getenv("MME_REDIS_URL") or os.getenv("SCALPX_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"


def redis_client() -> Any:
    if redis is None:
        raise RuntimeError("redis package not importable")
    return redis.Redis.from_url(redis_url(), decode_responses=True, socket_connect_timeout=1.0, socket_timeout=1.0)


def compact(value: Any, limit: int = 240) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", " ")[:limit]


def latest_files(rel: str, suffix: str, limit: int = 5) -> list[dict[str, Any]]:
    base = root() / rel
    if not base.exists():
        return []
    files = [p for p in base.iterdir() if p.is_file() and p.name.endswith(suffix)]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [{"name": p.name, "path": str(p.relative_to(root())), "mtime": int(p.stat().st_mtime), "size": p.stat().st_size} for p in files[:limit]]


def stream_info(r: Any, label: str, stream: str) -> dict[str, Any]:
    try:
        length = int(r.xlen(stream))
        latest_id = "-"
        latest_fields: dict[str, str] = {}
        if length > 0:
            row = r.xrevrange(stream, count=1)
            if row:
                latest_id = str(row[0][0])
                raw_fields = row[0][1] if isinstance(row[0][1], dict) else {}
                latest_fields = {compact(k, 60): compact(v, 180) for k, v in list(raw_fields.items())[:12]}
        status = "IDLE"
        if label == "orders" and length > 0:
            status = "DANGER"
        elif label == "errors" and length > 0:
            status = "WARN"
        elif length > 0:
            status = "LIVE"
        return {"label": label, "stream": stream, "length": length, "latest_id": latest_id, "latest_fields": latest_fields, "status": status}
    except Exception as exc:
        return {"label": label, "stream": stream, "length": None, "latest_id": "-", "latest_fields": {}, "status": "UNAVAILABLE", "error": compact(exc)}


def lock_info(r: Any, label: str, key: str) -> dict[str, Any]:
    try:
        return {"label": label, "key": key, "type": compact(r.type(key)), "pttl": r.pttl(key), "status": "LOCKED" if r.pttl(key) > 0 else "FREE"}
    except Exception as exc:
        return {"label": label, "key": key, "type": "unknown", "pttl": None, "status": "UNAVAILABLE", "error": compact(exc)}


def process_counts() -> dict[str, int]:
    checks = {
        "feeds": ["app.mme_scalpx.main", "--service", "feeds"],
        "features": ["app.mme_scalpx.main", "--service", "features"],
        "strategy": ["app.mme_scalpx.main", "--service", "strategy"],
        "risk": ["app.mme_scalpx.main", "--service", "risk"],
        "execution": ["app.mme_scalpx.main", "--service", "execution"],
    }
    out = {k: 0 for k in checks}
    proc = Path("/proc")
    if not proc.exists():
        return out
    for p in proc.iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", "ignore")
        except Exception:
            continue
        for name, tokens in checks.items():
            if all(t in cmd for t in tokens):
                out[name] += 1
    return out


def build_snapshot() -> dict[str, Any]:
    snap: dict[str, Any] = {
        "version": VERSION,
        "time_utc": utc_now(),
        "project_root": str(root()),
        "redis_connected": False,
        "redis_error": None,
        "streams": [],
        "locks": [],
        "position": {},
        "processes": process_counts(),
        "artifacts": {
            "proofs": latest_files("run/proofs", ".json"),
            "milestones": latest_files("docs/milestones", ".md"),
            "runbooks": latest_files("docs/runbooks", ".md"),
            "evidence_bundles": latest_files("run/evidence_bundles", ".tar.gz"),
        },
        "safety": {"read_only_contract": True, "risky_env_flags_set": {k: os.getenv(k) for k in RISKY_ENV if os.getenv(k)}},
    }
    try:
        r = redis_client()
        r.ping()
        snap["redis_connected"] = True
        snap["streams"] = [stream_info(r, label, stream) for label, stream in STREAMS]
        snap["locks"] = [lock_info(r, label, key) for label, key in LOCKS]
        try:
            snap["position"] = {compact(k, 80): compact(v, 160) for k, v in r.hgetall(POSITION_HASH).items()}
        except Exception as exc:
            snap["position"] = {"error": compact(exc)}
    except Exception as exc:
        snap["redis_error"] = compact(exc, 400)
    return snap


HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MME-ScalpX OPS Dashboard R0B</title>
<style>
:root{color-scheme:dark;--bg:#07111f;--card:#101d30;--line:#29405f;--text:#ecf5ff;--muted:#9fb3ca;--green:#35d067;--yellow:#f0c447;--red:#ff5964;--blue:#58aaff}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(135deg,#08111e,#071d35 45%,#040914);font-family:Segoe UI,Arial,sans-serif;color:var(--text)}
header{padding:18px 22px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;align-items:center;position:sticky;top:0;background:#07111fee;backdrop-filter:blur(8px)}
h1{font-size:22px;margin:0}.sub{color:var(--muted);font-size:13px}.wrap{padding:18px;display:grid;gap:16px}.cards{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}.card,.panel{background:linear-gradient(180deg,#112039,#0c1829);border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 12px 30px #0005}.label{color:#bdd3ec;font-size:12px;font-weight:700;text-transform:uppercase}.big{font-size:28px;font-weight:800;margin-top:12px}.grid{display:grid;grid-template-columns:1.25fr .75fr;gap:16px}table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:8px;border-bottom:1px solid #29405f99;text-align:left;vertical-align:top}th{color:#bdd3ec;font-size:11px;text-transform:uppercase}.pill{border-radius:999px;padding:6px 10px;background:#13243b;border:1px solid var(--line);font-size:12px}.badge{border-radius:7px;padding:3px 7px;font-weight:800;font-size:11px}.LIVE,.LOCKED{background:#123b24;color:var(--green)}.WARN{background:#3c3312;color:var(--yellow)}.DANGER{background:#46202a;color:var(--red)}.IDLE,.FREE,.UNAVAILABLE{background:#123456;color:#9bd0ff}.mono{font-family:Consolas,monospace}.kv{display:grid;grid-template-columns:160px 1fr;gap:8px;padding:8px 0;border-bottom:1px solid #29405f99}.kv span{color:#bdd3ec}.ok{color:var(--green)}.warn{color:var(--yellow)}.bad{color:var(--red)}.blue{color:var(--blue)}
@media(max-width:900px){header{display:block}.cards{grid-template-columns:1fr 1fr}.grid{grid-template-columns:1fr}.wrap{padding:10px}}@media(max-width:520px){.cards{grid-template-columns:1fr}.big{font-size:24px}.kv{grid-template-columns:1fr}}
</style>
</head>
<body>
<header><div><h1>MME-Scalp<span class="blue">X</span> OPS Dashboard</h1><div class="sub">R0B read-only browser control room · no orders · no paper/live controls</div></div><div><span id="health" class="pill">loading</span> <span id="clock" class="pill">--</span></div></header>
<div class="wrap">
<div class="cards">
<div class="card"><div class="label">Redis</div><div id="redis" class="big">--</div><div class="sub">connection</div></div>
<div class="card"><div class="label">Feeds</div><div id="feeds" class="big">--</div><div class="sub">live stream count</div></div>
<div class="card"><div class="label">Decisions</div><div id="decisions" class="big">--</div><div class="sub">decisions stream</div></div>
<div class="card"><div class="label">Errors</div><div id="errors" class="big">--</div><div class="sub">system errors</div></div>
<div class="card"><div class="label">Orders</div><div id="orders" class="big">--</div><div class="sub">must remain zero</div></div>
</div>
<div class="grid"><div class="panel"><h3>Stream Health</h3><div id="streams"></div></div><div class="panel"><h3>Safety</h3><div id="safety"></div></div></div>
<div class="grid"><div class="panel"><h3>Processes</h3><div id="processes"></div></div><div class="panel"><h3>Evidence</h3><div id="evidence"></div></div></div>
</div>
<script>
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pick=(a,l)=>(a||[]).find(x=>x.label===l)||{};
const badge=s=>`<span class="badge ${esc(s||'IDLE')}">${esc(s||'IDLE')}</span>`;
const kv=(k,v)=>`<div class="kv"><span>${esc(k)}</span><b>${esc(v)}</b></div>`;
function render(d){
 document.getElementById('clock').textContent=new Date().toLocaleTimeString();
 document.getElementById('health').innerHTML=d.redis_connected?'<span class="ok">● connected</span>':'<span class="bad">● redis unavailable</span>';
 document.getElementById('redis').innerHTML=d.redis_connected?'<span class="ok">OK</span>':'<span class="bad">NO</span>';
 const feeds=['fut zerodha','fut dhan','opt zerodha','opt dhan','dhan context'].filter(x=>pick(d.streams,x).status==='LIVE').length;
 document.getElementById('feeds').innerHTML=`<span class="ok">${feeds}/5</span>`;
 document.getElementById('decisions').textContent=pick(d.streams,'decisions').length??0;
 const el=pick(d.streams,'errors').length??0; document.getElementById('errors').innerHTML=`<span class="${el>0?'warn':'ok'}">${el}</span>`;
 const ol=pick(d.streams,'orders').length??0; document.getElementById('orders').innerHTML=`<span class="${ol>0?'bad':'blue'}">${ol}</span>`;
 document.getElementById('streams').innerHTML='<table><tr><th>Label</th><th>Stream</th><th>Length</th><th>Latest ID</th><th>Status</th></tr>'+(d.streams||[]).map(s=>`<tr><td>${esc(s.label)}</td><td class="mono">${esc(s.stream)}</td><td>${esc(s.length)}</td><td class="mono">${esc(s.latest_id)}</td><td>${badge(s.status)}</td></tr>`).join('')+'</table>';
 const flags=Object.keys((d.safety||{}).risky_env_flags_set||{});
 document.getElementById('safety').innerHTML=kv('Read-only contract','TRUE')+kv('Risky env flags',flags.length?flags.join(', '):'NONE')+kv('Position',JSON.stringify(d.position||{}).slice(0,300))+(d.locks||[]).map(l=>kv('Lock '+l.label,`${l.status} ttl=${l.pttl}`)).join('');
 document.getElementById('processes').innerHTML='<table><tr><th>Service</th><th>Count</th></tr>'+Object.entries(d.processes||{}).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('')+'</table>';
 const a=d.artifacts||{}; const p=(a.proofs||[])[0], m=(a.milestones||[])[0], e=(a.evidence_bundles||[])[0];
 document.getElementById('evidence').innerHTML=kv('Latest proof',p?p.path:'-')+kv('Latest milestone',m?m.path:'-')+kv('Latest bundle',e?e.path:'-')+kv('Project root',d.project_root);
}
async function load(){try{const r=await fetch('/api/snapshot',{cache:'no-store'});render(await r.json())}catch(e){document.getElementById('health').innerHTML='<span class="bad">dashboard error</span>'}}
load(); setInterval(load,2000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, payload: str) -> None:
        body = payload.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self.send_html(HTML)
        elif path == "/api/snapshot":
            self.send_json(build_snapshot())
        elif path == "/healthz":
            self.send_json({"ok": True, "version": VERSION, "time_utc": utc_now()})
        else:
            self.send_json({"error": "not_found", "path": path}, HTTPStatus.NOT_FOUND)

    def log_message(self, fmt: str, *args: Any) -> None:
        print(datetime.now().isoformat(timespec="seconds"), "ops_dashboard", fmt % args)


def main() -> int:
    parser = argparse.ArgumentParser(description="MME-ScalpX OPS Dashboard R0B read-only")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    print(f"{VERSION} read-only dashboard: http://{args.host}:{args.port}")
    print("Safety: no Redis writes, no broker calls, no start/stop, no orders, no paper/live controls.")
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY_SERVER

COMPILE_OK=0
if "$PY" -m py_compile app/mme_scalpx/ops_dashboard/__init__.py app/mme_scalpx/ops_dashboard/server.py; then
  COMPILE_OK=1
fi

AST_OK=0
if "$PY" - <<'PY_AUDIT'
import ast
from pathlib import Path
p = Path("app/mme_scalpx/ops_dashboard/server.py")
tree = ast.parse(p.read_text(encoding="utf-8"))
forbidden_attrs = {
    "xadd", "set", "setex", "psetex", "hset", "delete", "unlink", "publish",
    "lpush", "rpush", "sadd", "zadd", "expire", "pexpire", "execute_command",
    "system", "popen", "run", "call", "check_call", "check_output"
}
bad = []
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and node.attr in forbidden_attrs:
        bad.append((node.lineno, node.attr))
if bad:
    raise SystemExit(f"FORBIDDEN_ATTRS={bad}")
print("AST_OK_READ_ONLY_NO_REDIS_WRITE_NO_SUBPROCESS")
PY_AUDIT
then
  AST_OK=1
fi

IMPORT_OK=0
SNAPSHOT_OK=0
if "$PY" - <<'PY_SMOKE' > "$SNAPSHOT_SMOKE"
import json
from app.mme_scalpx.ops_dashboard.server import VERSION, build_snapshot
s = build_snapshot()
print(json.dumps({
    "version": VERSION,
    "redis_connected": s.get("redis_connected"),
    "stream_count": len(s.get("streams", [])),
    "read_only_contract": s.get("safety", {}).get("read_only_contract"),
    "has_project_root": bool(s.get("project_root")),
}, indent=2, sort_keys=True))
PY_SMOKE
then
  IMPORT_OK=1
  SNAPSHOT_OK=1
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

CLASSIFICATION="PASS_OPS_DASH_R0B_SMALL_READ_ONLY_DASHBOARD_CREATED_NO_START_NO_ORDER_NO_PAPER"
if [ "$COMPILE_OK" != "1" ] || [ "$AST_OK" != "1" ] || [ "$IMPORT_OK" != "1" ] || [ "$SNAPSHOT_OK" != "1" ]; then
  CLASSIFICATION="FAIL_OPS_DASH_R0B_CHECK_FAILED"
fi

export BATCH PURPOSE TAG CLASSIFICATION PROOF AUDIT REPORT MILESTONE RUNBOOK HANDOFF PATCH_DIFF SNAPSHOT_SMOKE
export COMPILE_OK AST_OK IMPORT_OK SNAPSHOT_OK
export ORDERS_BEFORE ORDERS_AFTER RISK_BEFORE RISK_AFTER EXEC_BEFORE EXEC_AFTER
export RISK_PIDS_BEFORE RISK_PIDS_AFTER EXEC_PIDS_BEFORE EXEC_PIDS_AFTER

"$PY" - <<'PY_PROOF'
import json
import os
from pathlib import Path

def env(name, default=""):
    return os.environ.get(name, default)

snapshot = {}
p = Path(env("SNAPSHOT_SMOKE"))
if p.exists():
    try:
        snapshot = json.loads(p.read_text())
    except Exception as exc:
        snapshot = {"read_error": str(exc)}

proof = {
    "batch": env("BATCH"),
    "purpose": env("PURPOSE"),
    "tag": env("TAG"),
    "classification": env("CLASSIFICATION"),
    "source_files": [
        "app/mme_scalpx/ops_dashboard/__init__.py",
        "app/mme_scalpx/ops_dashboard/server.py",
    ],
    "checks": {
        "compile_ok": env("COMPILE_OK"),
        "ast_ok_read_only_no_redis_write_no_subprocess": env("AST_OK"),
        "import_ok": env("IMPORT_OK"),
        "snapshot_ok": env("SNAPSHOT_OK"),
        "snapshot_smoke": snapshot,
    },
    "safety": {
        "redis_writes_attempted": False,
        "service_start_attempted": False,
        "service_stop_attempted": False,
        "broker_call_attempted": False,
        "order_attempted": False,
        "paper_live_enablement_attempted": False,
        "orders_before": env("ORDERS_BEFORE"),
        "orders_after": env("ORDERS_AFTER"),
        "risk_stream_before": env("RISK_BEFORE"),
        "risk_stream_after": env("RISK_AFTER"),
        "execution_stream_before": env("EXEC_BEFORE"),
        "execution_stream_after": env("EXEC_AFTER"),
        "risk_pids_before": env("RISK_PIDS_BEFORE"),
        "risk_pids_after": env("RISK_PIDS_AFTER"),
        "execution_pids_before": env("EXEC_PIDS_BEFORE"),
        "execution_pids_after": env("EXEC_PIDS_AFTER"),
    },
    "run_commands": {
        "local_only": ".venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765",
        "trusted_lan_mobile": ".venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765",
    },
    "patch_diff": env("PATCH_DIFF"),
}
Path(env("PROOF")).write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
Path(env("AUDIT")).write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
PY_PROOF

cat > "$REPORT" <<MD
# $BATCH

Classification: **$CLASSIFICATION**

## Created
- \`app/mme_scalpx/ops_dashboard/__init__.py\`
- \`app/mme_scalpx/ops_dashboard/server.py\`

## Safety
- No Redis writes
- No service start/stop
- No broker call
- No orders
- No paper/live enablement
- Default host is local-only: \`127.0.0.1\`

## Checks
- compile_ok=$COMPILE_OK
- ast_ok=$AST_OK
- import_ok=$IMPORT_OK
- snapshot_ok=$SNAPSHOT_OK

## Safety counters
- orders_before=$ORDERS_BEFORE
- orders_after=$ORDERS_AFTER
- risk_stream_before=$RISK_BEFORE
- risk_stream_after=$RISK_AFTER
- execution_stream_before=$EXEC_BEFORE
- execution_stream_after=$EXEC_AFTER
- risk_pids_before=$RISK_PIDS_BEFORE
- risk_pids_after=$RISK_PIDS_AFTER
- execution_pids_before=$EXEC_PIDS_BEFORE
- execution_pids_after=$EXEC_PIDS_AFTER

## Run locally after PASS
\`\`\`bash
.venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765
\`\`\`

Open:
\`\`\`text
http://127.0.0.1:8765
\`\`\`

## Run for mobile Chrome on trusted same Wi-Fi/LAN
\`\`\`bash
.venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765
\`\`\`

Open on phone:
\`\`\`text
http://<VM_OR_LAPTOP_IP>:8765
\`\`\`

Proof: \`$PROOF\`
Patch diff: \`$PATCH_DIFF\`
MD

cp "$REPORT" "$MILESTONE"
cp "$REPORT" "$RUNBOOK"
cp "$REPORT" "$HANDOFF"

echo "===== OPS-DASH-R0B RESULT ====="
echo "classification=$CLASSIFICATION"
echo "proof=$PROOF"
echo "report=$REPORT"
echo "patch_diff=$PATCH_DIFF"

if [ "$CLASSIFICATION" != "PASS_OPS_DASH_R0B_SMALL_READ_ONLY_DASHBOARD_CREATED_NO_START_NO_ORDER_NO_PAPER" ]; then
  echo "FAILED: inspect proof/report before doing anything else."
  exit 1
fi

echo
echo "Run locally:"
echo "  .venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765"
echo "Open:"
echo "  http://127.0.0.1:8765"
echo
echo "Mobile Chrome on trusted same Wi-Fi/LAN:"
echo "  .venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765"
echo "  http://<VM_OR_LAPTOP_IP>:8765"
