#!/usr/bin/env bash
set -Eeuo pipefail

# OPS-DASH-R0C
# Ultra-small read-only browser dashboard.
# No Redis writes. No service start/stop. No broker call. No orders. No paper/live.

cd /home/Lenovo/scalpx/projects/mme_scalpx

BATCH="OPS-DASH-R0C_ATOMIC_SMALL_DASHBOARD_NO_REDIS_WRITE_NO_START_NO_ORDER_NO_PAPER"
PURPOSE="create_ultra_small_dashboard_compile_smoke_proof"
TS="$(date +%Y%m%d_%H%M%S)"
TAG="${BATCH}_${PURPOSE}_${TS}"

mkdir -p app/mme_scalpx/ops_dashboard run/proofs run/audits docs/milestones docs/runbooks run/handoffs run/patches run/_code_backups

PROOF="run/proofs/${TAG}.json"
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

ORDERS_BEFORE="$(r_xlen orders:mme:stream)"
RISK_BEFORE="$(r_xlen risk:mme:stream)"
EXEC_BEFORE="$(r_xlen execution:mme:stream)"
RISK_PIDS_BEFORE="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service risk' | grep -v grep | wc -l | tr -d ' ')"
EXEC_PIDS_BEFORE="$(ps -eo args | grep -E 'app\.mme_scalpx\.main --service execution' | grep -v grep | wc -l | tr -d ' ')"

if [ -f app/mme_scalpx/ops_dashboard/server.py ]; then
  cp -a app/mme_scalpx/ops_dashboard/server.py "run/_code_backups/${TAG}_server.py.bak"
fi

cat > app/mme_scalpx/ops_dashboard/__init__.py <<'PY'
"""MME-ScalpX read-only OPS dashboard."""
PY

cat > app/mme_scalpx/ops_dashboard/server.py <<'PY'
from __future__ import annotations

import argparse
import html
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    import redis
except Exception:
    redis = None

try:
    from app.mme_scalpx.core import names
except Exception:
    names = None

VERSION = "OPS-DASH-R0C"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

def name(attr: str, fallback: str) -> str:
    return str(getattr(names, attr, fallback)) if names else fallback

STREAMS = [
    ("fut zerodha", name("STREAM_TICKS_MME_FUT_ZERODHA", "ticks:mme:fut:zerodha:stream")),
    ("fut dhan", name("STREAM_TICKS_MME_FUT_DHAN", "ticks:mme:fut:dhan:stream")),
    ("opt zerodha", name("STREAM_TICKS_MME_OPT_SELECTED_ZERODHA", "ticks:mme:opt:selected:zerodha:stream")),
    ("opt dhan", name("STREAM_TICKS_MME_OPT_SELECTED_DHAN", "ticks:mme:opt:selected:dhan:stream")),
    ("dhan context", name("STREAM_TICKS_MME_OPT_CONTEXT_DHAN", "ticks:mme:opt:context:dhan:stream")),
    ("features", name("STREAM_FEATURES_MME", "features:mme:stream")),
    ("decisions", name("STREAM_DECISIONS_MME", "decisions:mme:stream")),
    ("risk", name("STREAM_RISK_MME", "risk:mme:stream")),
    ("execution", name("STREAM_EXECUTION_MME", "execution:mme:stream")),
    ("errors", name("STREAM_SYSTEM_ERRORS", "system:errors:stream")),
    ("orders", name("STREAM_ORDERS_MME", "orders:mme:stream")),
]

LOCKS = [
    ("feeds", name("KEY_LOCK_FEEDS", "lock:feeds")),
    ("execution", name("KEY_LOCK_EXECUTION", "lock:execution")),
]

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

def project_root() -> Path:
    return Path(__file__).resolve().parents[3]

def redis_client():
    if redis is None:
        raise RuntimeError("redis package not importable")
    url = os.getenv("MME_REDIS_URL") or os.getenv("SCALPX_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    return redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=1.0, socket_timeout=1.0)

def esc(x) -> str:
    return html.escape("" if x is None else str(x))

def proc_count(service: str) -> int:
    count = 0
    proc = Path("/proc")
    if not proc.exists():
        return 0
    for p in proc.iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", "ignore")
        except Exception:
            continue
        if "app.mme_scalpx.main" in cmd and "--service" in cmd and service in cmd:
            count += 1
    return count

def latest_files(rel: str, suffix: str, limit: int = 5):
    base = project_root() / rel
    if not base.exists():
        return []
    files = [p for p in base.iterdir() if p.is_file() and p.name.endswith(suffix)]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [str(p.relative_to(project_root())) for p in files[:limit]]

def stream_row(r, label: str, key: str):
    try:
        length = int(r.xlen(key))
        latest = "-"
        if length:
            rows = r.xrevrange(key, count=1)
            latest = rows[0][0] if rows else "-"
        status = "IDLE"
        if label == "orders" and length > 0:
            status = "DANGER"
        elif label == "errors" and length > 0:
            status = "WARN"
        elif length > 0:
            status = "LIVE"
        return label, key, length, latest, status
    except Exception as e:
        return label, key, "ERR", str(e)[:80], "UNAVAILABLE"

def build_html() -> str:
    now = datetime.now().isoformat(timespec="seconds")
    redis_ok = False
    redis_err = ""
    rows = []
    locks = []
    try:
        r = redis_client()
        r.ping()
        redis_ok = True
        rows = [stream_row(r, label, key) for label, key in STREAMS]
        for label, key in LOCKS:
            try:
                locks.append((label, key, r.type(key), r.pttl(key)))
            except Exception as e:
                locks.append((label, key, "ERR", str(e)[:80]))
    except Exception as e:
        redis_err = str(e)[:200]
        rows = [(label, key, "-", "-", "REDIS_DOWN") for label, key in STREAMS]

    by_label = {x[0]: x for x in rows}
    orders = by_label.get("orders", ("orders", "", 0, "", ""))[2]
    errors = by_label.get("errors", ("errors", "", 0, "", ""))[2]
    decisions = by_label.get("decisions", ("decisions", "", 0, "", ""))[2]
    feed_live = sum(1 for x in rows[:5] if x[4] == "LIVE")
    risky = [k for k in RISKY_ENV if os.getenv(k)]

    def badge(s):
        c = "idle"
        if s in ("LIVE", "OK"):
            c = "good"
        elif s in ("WARN",):
            c = "warn"
        elif s in ("DANGER", "REDIS_DOWN"):
            c = "bad"
        return f"<span class='{c}'>{esc(s)}</span>"

    stream_table = "".join(
        f"<tr><td>{esc(a)}</td><td class='mono'>{esc(b)}</td><td>{esc(c)}</td><td class='mono'>{esc(d)}</td><td>{badge(e)}</td></tr>"
        for a,b,c,d,e in rows
    )

    lock_table = "".join(
        f"<tr><td>{esc(a)}</td><td class='mono'>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td></tr>"
        for a,b,c,d in locks
    )

    proc_table = "".join(
        f"<tr><td>{s}</td><td>{proc_count(s)}</td></tr>"
        for s in ["feeds", "features", "strategy", "risk", "execution"]
    )

    proof_list = "".join(f"<li class='mono'>{esc(x)}</li>" for x in latest_files("run/proofs", ".json"))
    milestone_list = "".join(f"<li class='mono'>{esc(x)}</li>" for x in latest_files("docs/milestones", ".md"))

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="2">
<title>MME-ScalpX OPS Dashboard R0C</title>
<style>
body{{margin:0;background:#07111f;color:#eaf3ff;font-family:Segoe UI,Arial,sans-serif}}
header{{padding:18px 22px;background:#0b1728;border-bottom:1px solid #25415f;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}}
h1{{margin:0;font-size:22px}} .sub{{color:#9db1c8;font-size:13px;margin-top:4px}}
.wrap{{padding:16px;display:grid;gap:16px}}
.cards{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}}
.card,.panel{{background:#101d30;border:1px solid #29405f;border-radius:14px;padding:14px;box-shadow:0 10px 25px #0006}}
.label{{color:#b7cde6;font-size:12px;text-transform:uppercase;font-weight:700}}
.big{{font-size:28px;font-weight:800;margin-top:10px}}
.grid{{display:grid;grid-template-columns:1.3fr .7fr;gap:16px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
td,th{{padding:8px;border-bottom:1px solid #29405f;text-align:left;vertical-align:top}}
th{{color:#b7cde6;font-size:11px;text-transform:uppercase}}
.mono{{font-family:Consolas,monospace;font-size:12px}}
.good{{color:#36d46a}} .warn{{color:#f0c64a}} .bad{{color:#ff5f6b}} .idle{{color:#89c7ff}}
.safe{{border:1px solid #36d46a;color:#36d46a;border-radius:999px;padding:6px 10px;font-size:12px}}
@media(max-width:850px){{.cards{{grid-template-columns:1fr 1fr}}.grid{{grid-template-columns:1fr}}}}
@media(max-width:520px){{.cards{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header>
<div><h1>MME-ScalpX OPS Dashboard R0C</h1><div class="sub">Read-only · no Redis writes · no broker calls · no orders · no paper/live controls</div></div>
<div><span class="safe">READ ONLY</span> <span>{esc(now)}</span></div>
</header>
<div class="wrap">
<div class="cards">
<div class="card"><div class="label">Redis</div><div class="big">{badge("OK" if redis_ok else "REDIS_DOWN")}</div><div class="sub">{esc(redis_err)}</div></div>
<div class="card"><div class="label">Feeds Live</div><div class="big">{feed_live}/5</div></div>
<div class="card"><div class="label">Decisions</div><div class="big">{esc(decisions)}</div></div>
<div class="card"><div class="label">Errors</div><div class="big">{esc(errors)}</div></div>
<div class="card"><div class="label">Orders</div><div class="big">{esc(orders)}</div></div>
</div>
<div class="grid">
<div class="panel"><h3>Redis Stream Health</h3><table><tr><th>Label</th><th>Stream</th><th>Length</th><th>Latest ID</th><th>Status</th></tr>{stream_table}</table></div>
<div class="panel"><h3>Safety</h3><p>Risky env flags: <b>{esc(", ".join(risky) if risky else "NONE")}</b></p><p>Project root: <span class="mono">{esc(project_root())}</span></p></div>
</div>
<div class="grid">
<div class="panel"><h3>Processes</h3><table><tr><th>Service</th><th>Count</th></tr>{proc_table}</table><h3>Locks</h3><table><tr><th>Name</th><th>Key</th><th>Type</th><th>PTTL</th></tr>{lock_table}</table></div>
<div class="panel"><h3>Latest Proofs</h3><ul>{proof_list}</ul><h3>Latest Milestones</h3><ul>{milestone_list}</ul></div>
</div>
</div>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            body = build_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/healthz":
            body = b"OK\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    print(f"{VERSION} running at http://{args.host}:{args.port}", flush=True)
    print("Safety: read-only dashboard only.", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()

if __name__ == "__main__":
    main()
PY

COMPILE_OK=0
if "$PY" -m py_compile app/mme_scalpx/ops_dashboard/__init__.py app/mme_scalpx/ops_dashboard/server.py; then
  COMPILE_OK=1
fi

AST_OK=0
if "$PY" - <<'PY'
import ast
from pathlib import Path
tree = ast.parse(Path("app/mme_scalpx/ops_dashboard/server.py").read_text())
bad = []
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and node.attr in {"xadd","set","hset","delete","publish","execute_command","system","popen","run","call","check_output"}:
        bad.append((node.lineno, node.attr))
if bad:
    raise SystemExit(f"FORBIDDEN={bad}")
print("AST_OK")
PY
then
  AST_OK=1
fi

IMPORT_OK=0
if "$PY" - <<'PY'
from app.mme_scalpx.ops_dashboard.server import VERSION, build_html
html = build_html()
assert VERSION == "OPS-DASH-R0C"
assert "READ ONLY" in html
assert "orders" in html
print("IMPORT_SMOKE_OK")
PY
then
  IMPORT_OK=1
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

CLASSIFICATION="PASS_OPS_DASH_R0C_ATOMIC_SMALL_DASHBOARD_CREATED_NO_START_NO_ORDER_NO_PAPER"
if [ "$COMPILE_OK" != "1" ] || [ "$AST_OK" != "1" ] || [ "$IMPORT_OK" != "1" ]; then
  CLASSIFICATION="FAIL_OPS_DASH_R0C_CHECK_FAILED"
fi

cat > "$PROOF" <<JSON
{
  "batch": "$BATCH",
  "purpose": "$PURPOSE",
  "tag": "$TAG",
  "classification": "$CLASSIFICATION",
  "checks": {
    "compile_ok": "$COMPILE_OK",
    "ast_ok": "$AST_OK",
    "import_smoke_ok": "$IMPORT_OK"
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
    "execution_pids_after": "$EXEC_PIDS_AFTER"
  },
  "run_local": ".venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765",
  "run_mobile_lan": ".venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765",
  "patch_diff": "$PATCH_DIFF"
}
JSON

cat > "$REPORT" <<MD
# $BATCH

Classification: **$CLASSIFICATION**

Created ultra-small read-only browser dashboard:

- \`app/mme_scalpx/ops_dashboard/__init__.py\`
- \`app/mme_scalpx/ops_dashboard/server.py\`

Safety:
- No Redis writes
- No service start/stop
- No broker call
- No orders
- No paper/live

Checks:
- compile_ok=$COMPILE_OK
- ast_ok=$AST_OK
- import_smoke_ok=$IMPORT_OK

Safety counters:
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

Run local:
\`\`\`bash
.venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765
\`\`\`

Open:
\`\`\`text
http://127.0.0.1:8765
\`\`\`

Mobile Chrome same trusted Wi-Fi/LAN:
\`\`\`bash
.venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 0.0.0.0 --port 8765
\`\`\`
MD

cp "$REPORT" "$MILESTONE"
cp "$REPORT" "$RUNBOOK"
cp "$REPORT" "$HANDOFF"

echo "===== OPS-DASH-R0C RESULT ====="
echo "classification=$CLASSIFICATION"
echo "proof=$PROOF"
echo "report=$REPORT"
echo "patch_diff=$PATCH_DIFF"

if [ "$CLASSIFICATION" != "PASS_OPS_DASH_R0C_ATOMIC_SMALL_DASHBOARD_CREATED_NO_START_NO_ORDER_NO_PAPER" ]; then
  exit 1
fi

echo
echo "Now start local dashboard with:"
echo ".venv/bin/python -m app.mme_scalpx.ops_dashboard.server --host 127.0.0.1 --port 8765"
