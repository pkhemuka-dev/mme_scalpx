from __future__ import annotations

import argparse
import html
import os
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    import redis
except Exception:
    redis = None

VERSION = "OPS-DASH-R2C"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

STREAMS = [
    ("fut zerodha", "ticks:mme:fut:zerodha:stream"),
    ("fut dhan", "ticks:mme:fut:dhan:stream"),
    ("opt zerodha", "ticks:mme:opt:selected:zerodha:stream"),
    ("opt dhan", "ticks:mme:opt:selected:dhan:stream"),
    ("dhan context", "ticks:mme:opt:context:dhan:stream"),
    ("features", "features:mme:stream"),
    ("decisions", "decisions:mme:stream"),
    ("risk", "risk:mme:stream"),
    ("execution", "execution:mme:stream"),
    ("errors", "system:errors:stream"),
    ("orders", "orders:mme:stream"),
]

LOCKS = [
    ("feeds", "lock:feeds"),
    ("execution", "lock:execution"),
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

def esc(x) -> str:
    return html.escape("" if x is None else str(x))

def project_root() -> Path:
    return Path(__file__).resolve().parents[3]

def redis_client():
    if redis is None:
        raise RuntimeError("redis package not importable")
    url = os.getenv("MME_REDIS_URL") or os.getenv("SCALPX_REDIS_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
    return redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=1.0, socket_timeout=1.0)

def proc_count(service: str) -> int:
    proc = Path("/proc")
    if not proc.exists():
        return 0
    count = 0
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
        return label, key, "-", str(e)[:80], "UNAVAILABLE"


def mini_tail_table(key: str, limit: int = 10) -> str:
    try:
        r = redis_client()
        rows = r.xrevrange(key, count=limit)
    except Exception as e:
        return "<table><tr><td>ERR</td><td>%s</td></tr></table>" % esc(str(e)[:180])
    if not rows:
        return "<table><tr><td>-</td><td>empty</td></tr></table>"
    body = []
    for xid, fields in rows:
        if not isinstance(fields, dict):
            fields = {}
        msg = " | ".join("%s=%s" % (str(k)[:28], str(v)[:100]) for k, v in list(fields.items())[:6])
        body.append("<tr><td class='mono'>%s</td><td class='mono'>%s</td></tr>" % (esc(xid), esc(msg or "-")))
    return "<table><tr><th>ID</th><th>Fields</th></tr>%s</table>" % "".join(body)

def badge(status: str) -> str:
    css = "idle"
    if status in ("LIVE", "OK"):
        css = "good"
    elif status == "WARN":
        css = "warn"
    elif status in ("DANGER", "REDIS_DOWN"):
        css = "bad"
    return "<span class='%s'>%s</span>" % (css, esc(status))

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
    live_feeds = sum(1 for x in rows[:5] if x[4] == "LIVE")
    risky = [k for k in RISKY_ENV if os.getenv(k)]

    stream_table = "".join(
        "<tr><td>%s</td><td class='mono'>%s</td><td>%s</td><td class='mono'>%s</td><td>%s</td></tr>"
        % (esc(a), esc(b), esc(c), esc(d), badge(e))
        for a, b, c, d, e in rows
    )

    lock_table = "".join(
        "<tr><td>%s</td><td class='mono'>%s</td><td>%s</td><td>%s</td></tr>"
        % (esc(a), esc(b), esc(c), esc(d))
        for a, b, c, d in locks
    )

    proc_table = "".join(
        "<tr><td>%s</td><td>%s</td></tr>" % (esc(s), proc_count(s))
        for s in ["feeds", "features", "strategy", "risk", "execution"]
    )

    proof_items = "".join("<li class='mono'>%s</li>" % esc(x) for x in latest_files("run/proofs", ".json"))
    milestone_items = "".join("<li class='mono'>%s</li>" % esc(x) for x in latest_files("docs/milestones", ".md"))
    runtime_seal = "<table><tr><th>Check</th><th>Value</th></tr>" + "".join([
        "<tr><td>Dashboard version</td><td class='mono'>%s</td></tr>" % esc(VERSION),
        "<tr><td>Redis connected</td><td class='mono'>%s</td></tr>" % esc("YES" if redis_ok else "NO"),
        "<tr><td>Read-only contract</td><td class='mono'>TRUE</td></tr>",
        "<tr><td>Orders stream length</td><td class='mono'>%s</td></tr>" % esc(orders),
        "<tr><td>Errors stream length</td><td class='mono'>%s</td></tr>" % esc(errors),
        "<tr><td>Decisions stream length</td><td class='mono'>%s</td></tr>" % esc(decisions),
        "<tr><td>Risky env flags</td><td class='mono'>%s</td></tr>" % esc(", ".join(risky) if risky else "NONE"),
        "<tr><td>Risk/execution proc</td><td class='mono'>%s/%s</td></tr>" % (proc_count("risk"), proc_count("execution")),
    ]) + "</table>"
    error_tail_panel = mini_tail_table("system:errors:stream", 10)
    decision_tail_panel = mini_tail_table("decisions:mme:stream", 10)
    r2c_error_summary_panel = mini_tail_table("system:errors:stream", 5)
    try:
        _r2c_r = redis_client()
        _r2c_t0 = time.perf_counter()
        _r2c_ping = _r2c_r.ping()
        _r2c_ms = (time.perf_counter() - _r2c_t0) * 1000.0
        _r2c_lock_rows = []
        for _r2c_key in ("lock:feeds", "lock:execution"):
            _r2c_type = _r2c_r.type(_r2c_key)
            if isinstance(_r2c_type, bytes):
                _r2c_type = _r2c_type.decode("utf-8", "replace")
            _r2c_pttl = _r2c_r.pttl(_r2c_key)
            _r2c_lock_rows.append(
                "<tr><td class='mono'>%s</td><td>%s</td><td>%s</td></tr>"
                % (esc(_r2c_key), esc(_r2c_type), esc(_r2c_pttl))
            )
        r2c_feed_lock_diag_panel = (
            "<table><tr><th>Key</th><th>Type</th><th>PTTL ms</th></tr>%s</table>"
            % "".join(_r2c_lock_rows)
        )
        r2c_redis_latency_panel = (
            "<table><tr><th>Check</th><th>Value</th></tr>"
            "<tr><td>ping</td><td>%s</td></tr>"
            "<tr><td>latency_ms</td><td>%.3f</td></tr></table>"
            % (esc(_r2c_ping), _r2c_ms)
        )
    except Exception as _r2c_exc:
        r2c_feed_lock_diag_panel = "<table><tr><td>ERR</td><td>%s</td></tr></table>" % esc(str(_r2c_exc)[:180])
        r2c_redis_latency_panel = r2c_feed_lock_diag_panel

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="2">
<title>MME-ScalpX OPS Dashboard R2C</title>
<style>
body{{margin:0;background:#07111f;color:#eaf3ff;font-family:Segoe UI,Arial,sans-serif}}
header{{padding:18px 22px;background:#0b1728;border-bottom:1px solid #25415f;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap}}
h1{{margin:0;font-size:22px}}
.sub{{color:#9db1c8;font-size:13px;margin-top:4px}}
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
<div><h1>MME-ScalpX OPS Dashboard R2C</h1><div class="sub">R2C read-only · error summary · feed lock diagnostics · Redis latency · no writes · no orders</div></div>
<div><span class="safe">READ ONLY</span> <span>{esc(now)}</span></div>
</header>
<div class="wrap">
<div class="cards">
<div class="card"><div class="label">Redis</div><div class="big">{badge("OK" if redis_ok else "REDIS_DOWN")}</div><div class="sub">{esc(redis_err)}</div></div>
<div class="card"><div class="label">Feeds Live</div><div class="big">{live_feeds}/5</div></div>
<div class="card"><div class="label">Decisions</div><div class="big">{esc(decisions)}</div></div>
<div class="card"><div class="label">Errors</div><div class="big">{esc(errors)}</div></div>
<div class="card"><div class="label">Orders</div><div class="big">{esc(orders)}</div></div>
</div>
<div class="grid">
<div class="panel"><h3>Redis Stream Health</h3><table><tr><th>Label</th><th>Stream</th><th>Length</th><th>Latest ID</th><th>Status</th></tr>{stream_table}</table></div>
<div class="panel"><h3>Safety</h3><p>Risky env flags: <b>{esc(", ".join(risky) if risky else "NONE")}</b></p><p>Project root: <span class="mono">{esc(project_root())}</span></p></div>
</div>
<div class="grid">
<div class="grid">
<div class="panel"><h3>Error Summary</h3>{r2c_error_summary_panel}</div>
<div class="panel"><h3>Feed Lock Diagnostics</h3>{r2c_feed_lock_diag_panel}<h3>Redis Ping Latency</h3>{r2c_redis_latency_panel}</div>
</div>
<div class="panel"><h3>Runtime Seal</h3>{runtime_seal}</div>
<div class="panel"><h3>Latest Error Tail</h3>{error_tail_panel}</div>
</div>
<div class="grid">
<div class="panel"><h3>Latest Decision Tail</h3>{decision_tail_panel}</div>
<div class="panel"><h3>R1 Notes</h3><p>Read-only visibility only. No Redis writes, no broker calls, no service controls, no orders.</p></div>
</div>
<div class="grid">
<div class="panel"><h3>Processes</h3><table><tr><th>Service</th><th>Count</th></tr>{proc_table}</table><h3>Locks</h3><table><tr><th>Name</th><th>Key</th><th>Type</th><th>PTTL</th></tr>{lock_table}</table></div>
<div class="panel"><h3>Latest Proofs</h3><ul>{proof_items}</ul><h3>Latest Milestones</h3><ul>{milestone_items}</ul></div>
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
