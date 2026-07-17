from __future__ import annotations

import argparse
import html
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Mapping

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


STREAMS = (
    "decisions:mme:stream",
    "orders:mme:stream",
    "risk:mme:stream",
    "execution:mme:stream",
    "trades:mme:stream",
    "trades:ledger:stream",
    "features:mme:stream",
)

POSITION_KEYS = (
    "state:position:mme",
    "state:position",
    "state:position:nifty",
)

ERROR_PATTERNS = (
    "DecisionContractError",
    "missing_entry_strike",
    "entry_position_effect_not_open",
    "missing_option_symbol",
    "missing_option_token",
    "missing_or_invalid_limit_price",
    "Redis timeout",
    "LOADING",
)

FORBIDDEN_RUNTIME_MARKER = "PDASH_READ_ONLY_NO_ORDER_NO_WRITE"


def _decode(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    if isinstance(value, dict):
        return {_decode(k): _decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_decode(v) for v in value]
    if isinstance(value, tuple):
        return tuple(_decode(v) for v in value)
    return value


def _json_load(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    if value is None:
        return {}
    text = _decode(value)
    if not isinstance(text, str) or not text.strip():
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except Exception:
        return default


def _first(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def _redis_client() -> Any:
    if redis is None:
        return None
    url = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
    try:
        return redis.Redis.from_url(url, socket_timeout=0.35, socket_connect_timeout=0.35)
    except Exception:
        return None


def _stream_lengths(r: Any) -> dict[str, int | str]:
    out: dict[str, int | str] = {}
    for stream in STREAMS:
        try:
            out[stream] = int(r.xlen(stream)) if r is not None else "NA"
        except Exception as exc:
            out[stream] = f"ERR:{type(exc).__name__}"
    return out


def _latest_stream_payload(r: Any, stream: str, count: int = 1) -> list[dict[str, Any]]:
    if r is None:
        return []
    try:
        rows = r.xrevrange(stream, "+", "-", count=count)
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for row_id, fields in rows:
        fields = _decode(fields)
        payload = _json_load(fields.get("payload_json")) or _json_load(fields.get("payload")) or fields
        out.append({"id": _decode(row_id), "fields": fields, "payload": payload if isinstance(payload, dict) else {}})
    return out


def _position_snapshot(r: Any) -> dict[str, Any]:
    if r is None:
        return {"status": "redis_unavailable", "has_position": False, "position_side": "UNKNOWN"}
    for key in POSITION_KEYS:
        try:
            raw = _decode(r.hgetall(key))
        except Exception:
            raw = {}
        if raw:
            side = str(_first(raw.get("side"), raw.get("position_side"), raw.get("direction"), "UNKNOWN"))
            qty = _safe_float(_first(raw.get("qty"), raw.get("quantity"), raw.get("net_qty")), 0.0)
            has_position = bool(qty) or side.upper() not in {"", "FLAT", "NONE", "UNKNOWN"}
            return {
                "key": key,
                "status": "OPEN" if has_position else "FLAT",
                "has_position": has_position,
                "position_side": side,
                "qty": qty,
                "raw": raw,
            }
    return {"status": "FLAT_OR_MISSING", "has_position": False, "position_side": "FLAT", "qty": 0.0}


def _decision_projection(rows: list[dict[str, Any]]) -> dict[str, Any]:
    latest = rows[0] if rows else {}
    payload = latest.get("payload", {}) if isinstance(latest, dict) else {}
    consumer = _json_load(payload.get("consumer_view_json"))

    action = _first(payload.get("action"), consumer.get("action"), "")
    family = _first(
        payload.get("strategy_family_id"),
        payload.get("family_id"),
        payload.get("activation_selected_family_id"),
        payload.get("candidate_family_id_shadow"),
        "",
    )
    side = _first(
        payload.get("side"),
        payload.get("branch_id"),
        payload.get("activation_selected_branch_id"),
        payload.get("candidate_branch_id_shadow"),
        "",
    )
    option_symbol = _first(payload.get("option_symbol"), payload.get("entry_option_symbol"), payload.get("symbol"), "")
    token = _first(payload.get("instrument_token"), payload.get("option_token"), payload.get("entry_option_token"), "")
    strike = _first(payload.get("strike"), payload.get("entry_strike"), payload.get("entry_option_strike"), "")
    price = _first(payload.get("price"), payload.get("limit_price"), payload.get("entry_price"), 0.0)
    qty = _first(payload.get("qty"), payload.get("quantity"), payload.get("lots"), 0)
    score = _first(payload.get("activation_selected_score"), payload.get("score"), payload.get("setup_score"), "")
    reason = _first(
        payload.get("reason"),
        payload.get("reject_reason"),
        payload.get("blocker"),
        payload.get("activation_reason"),
        "",
    )
    candidate_count = _safe_int(_first(payload.get("activation_candidate_count"), payload.get("candidate_count"), 0), 0)

    projected_enter = False
    flags = []
    for key, value in payload.items():
        lk = str(key).lower()
        if "project" in lk or "shadow" in lk or "enter" in lk:
            flags.append(f"{key}={value}")
            if "enter" in str(value).upper() or "ENTER" in str(key):
                projected_enter = True
    if str(action).upper() == "ENTER":
        projected_enter = True

    return {
        "id": latest.get("id", ""),
        "action": action,
        "family": family,
        "side": side,
        "option_symbol": option_symbol,
        "token": token,
        "strike": strike,
        "price": price,
        "qty": qty,
        "strategy_score": score,
        "candidate_count": candidate_count,
        "projected_enter": projected_enter,
        "projection_flags": flags[:12],
        "reason": reason,
    }


def _latest_events(r: Any) -> dict[str, list[dict[str, Any]]]:
    return {
        "orders": _latest_stream_payload(r, "orders:mme:stream", 5),
        "risk": _latest_stream_payload(r, "risk:mme:stream", 5),
        "execution": _latest_stream_payload(r, "execution:mme:stream", 5),
        "trades": _latest_stream_payload(r, "trades:mme:stream", 5),
        "ledger": _latest_stream_payload(r, "trades:ledger:stream", 5),
    }


def _pnl_from_events(events: Mapping[str, list[dict[str, Any]]]) -> dict[str, Any]:
    total = 0.0
    count = 0
    last = None
    for group in ("trades", "ledger"):
        for row in events.get(group, []):
            p = row.get("payload", {})
            value = _first(
                p.get("pnl"),
                p.get("net_pnl"),
                p.get("realized_pnl"),
                p.get("shadow_pnl"),
                p.get("paper_pnl"),
            )
            if value is not None:
                fv = _safe_float(value, 0.0)
                total += fv
                count += 1
                last = fv
    return {"pnl_seen_count": count, "latest_pnl": last, "visible_pnl_sum_last_events": total}


def _safety_status(r: Any, lengths: Mapping[str, Any], position: Mapping[str, Any]) -> dict[str, Any]:
    env = {
        "SCALPX_ENABLE_LIVE": os.environ.get("SCALPX_ENABLE_LIVE", ""),
        "SCALPX_ENABLE_PAPER": os.environ.get("SCALPX_ENABLE_PAPER", ""),
        "SCALPX_ALLOW_BROKER_ORDERS": os.environ.get("SCALPX_ALLOW_BROKER_ORDERS", ""),
        "SCALPX_REAL_LIVE_ALLOWED": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", ""),
        "SCALPX_OBSERVE_ONLY": os.environ.get("SCALPX_OBSERVE_ONLY", ""),
        "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY": os.environ.get("B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY", ""),
    }
    return {
        "real_broker_enabled": bool(env["SCALPX_ALLOW_BROKER_ORDERS"] or env["SCALPX_REAL_LIVE_ALLOWED"]),
        "paper_enabled": bool(env["SCALPX_ENABLE_PAPER"]),
        "live_enabled": bool(env["SCALPX_ENABLE_LIVE"]),
        "position_status": position.get("status"),
        "orders_len": lengths.get("orders:mme:stream"),
        "risk_len": lengths.get("risk:mme:stream"),
        "execution_len": lengths.get("execution:mme:stream"),
        "trades_len": lengths.get("trades:mme:stream"),
        "env": env,
    }


def _error_monitor(r: Any) -> list[str]:
    found: list[str] = []
    rows = _latest_stream_payload(r, "system:errors:stream", 20)
    for row in rows:
        blob = json.dumps(row.get("payload", {}), ensure_ascii=False) + " " + json.dumps(row.get("fields", {}), ensure_ascii=False)
        for pattern in ERROR_PATTERNS:
            if pattern in blob and pattern not in found:
                found.append(pattern)
    return found


def build_snapshot() -> dict[str, Any]:
    r = _redis_client()
    lengths = _stream_lengths(r)
    decision_rows = _latest_stream_payload(r, "decisions:mme:stream", 5)
    latest_decision = _decision_projection(decision_rows)
    position = _position_snapshot(r)
    events = _latest_events(r)
    pnl = _pnl_from_events(events)
    safety = _safety_status(r, lengths, position)
    errors = _error_monitor(r)
    return {
        "schema": "pdash_stream_lite_readonly_v1",
        "marker": FORBIDDEN_RUNTIME_MARKER,
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stream_lengths": lengths,
        "latest_decision": latest_decision,
        "position": position,
        "pnl": pnl,
        "events": events,
        "safety": safety,
        "errors": errors,
        "read_only": True,
    }


def _card(title: str, body: str) -> str:
    return f"<section class='card'><h2>{html.escape(title)}</h2>{body}</section>"


def _kv_table(data: Mapping[str, Any]) -> str:
    rows = []
    for k, v in data.items():
        rows.append(f"<tr><th>{html.escape(str(k))}</th><td>{html.escape(str(v))}</td></tr>")
    return "<table>" + "".join(rows) + "</table>"


def render_html(snapshot: Mapping[str, Any]) -> str:
    decision = snapshot["latest_decision"]
    position = snapshot["position"]
    pnl = snapshot["pnl"]
    safety = snapshot["safety"]
    lengths = snapshot["stream_lengths"]

    simple = {
        "Trade candidate count": decision.get("candidate_count"),
        "Best/latest strategy": decision.get("family"),
        "Strategy score": decision.get("strategy_score"),
        "Latest action": decision.get("action"),
        "Projected ENTER": decision.get("projected_enter"),
        "Side": decision.get("side"),
        "Option": decision.get("option_symbol"),
        "Strike": decision.get("strike"),
        "Token": decision.get("token"),
        "Price": decision.get("price"),
        "Qty/Lots": decision.get("qty"),
        "Open position": position.get("status"),
        "Position qty": position.get("qty"),
        "Visible PnL": pnl.get("latest_pnl"),
        "PnL sum last events": pnl.get("visible_pnl_sum_last_events"),
        "Last blocker/reason": decision.get("reason"),
    }

    readiness = {
        "Runtime mode": "READ_ONLY_MONITOR",
        "Paper enabled": safety.get("paper_enabled"),
        "Real broker enabled": safety.get("real_broker_enabled"),
        "Live enabled": safety.get("live_enabled"),
        "Route visible": bool(decision.get("id")),
        "Flat position": not bool(position.get("has_position")),
        "Orders len": lengths.get("orders:mme:stream"),
        "Risk len": lengths.get("risk:mme:stream"),
        "Execution len": lengths.get("execution:mme:stream"),
        "Trades len": lengths.get("trades:mme:stream"),
        "Last projected ENTER": decision.get("projected_enter"),
        "Last rejection": decision.get("reason"),
    }

    body = []
    body.append(_card("Simple Trade View", _kv_table(simple)))
    body.append(_card("Session Readiness", _kv_table(readiness)))
    body.append(_card("Stream Lengths", _kv_table(lengths)))
    body.append(_card("Safety", _kv_table(safety)))
    body.append(_card("Error / Reject Monitor", "<pre>" + html.escape(json.dumps(snapshot.get("errors", []), indent=2)) + "</pre>"))
    body.append(_card("Latest Events", "<pre>" + html.escape(json.dumps(snapshot.get("events", {}), indent=2, default=str)[:7000]) + "</pre>"))

    css = """
    body{font-family:Arial,sans-serif;background:#0f172a;color:#e5e7eb;margin:0;padding:18px}
    h1{font-size:24px;margin:0 0 12px}
    .sub{color:#94a3b8;margin-bottom:16px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:14px}
    .card{background:#111827;border:1px solid #334155;border-radius:12px;padding:14px}
    h2{font-size:18px;margin:0 0 10px;color:#f8fafc}
    table{width:100%;border-collapse:collapse}
    th{text-align:left;color:#93c5fd;width:45%;padding:6px;border-bottom:1px solid #1f2937}
    td{padding:6px;border-bottom:1px solid #1f2937}
    pre{white-space:pre-wrap;word-break:break-word;max-height:420px;overflow:auto}
    .safe{color:#86efac}.warn{color:#facc15}
    """
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta http-equiv="refresh" content="3">
<title>PDASH Stream Lite</title><style>{css}</style></head>
<body>
<h1>PDASH UI Stream Lite</h1>
<div class="sub">Read-only monitoring only. No strategy/risk/execution/broker/order mutation. Updated: {html.escape(str(snapshot.get("ts")))}</div>
<div class="grid">{''.join(body)}</div>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path.startswith("/json"):
            data = json.dumps(build_snapshot(), indent=2, default=str).encode("utf-8")
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.send_header("cache-control", "no-store")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        data = render_html(build_snapshot()).encode("utf-8")
        self.send_response(200)
        self.send_header("content-type", "text/html; charset=utf-8")
        self.send_header("cache-control", "no-store")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PDASH read-only stream lite UI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--once-json", action="store_true")
    args = parser.parse_args(argv)

    if args.once_json:
        print(json.dumps(build_snapshot(), indent=2, default=str))
        return 0

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"PDASH Stream Lite read-only UI on http://{args.host}:{args.port}/")
    server.serve_forever()
    return 0



# BEGIN PDASH_R2_PLAIN_LANGUAGE_BLOCKER_CONTRACT_WATCH
# Dashboard-only wrapper. No Redis writes. No service start. No broker/order/risk/execution calls.

_PDASH_R2_BASE_BUILD_SNAPSHOT = build_snapshot
_PDASH_R2_BASE_RENDER_HTML = render_html


def _pdash_r2_text(v):
    return "" if v is None else str(v)


def _pdash_r2_html(v):
    s = _pdash_r2_text(v)
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )


def _pdash_r2_yes(v):
    return _pdash_r2_text(v).strip().upper() in ("1", "TRUE", "YES", "Y", "ON", "ENTER")


def _pdash_r2_plain_reason(reason):
    raw = _pdash_r2_text(reason).strip()
    low = raw.lower()

    if not raw:
        return "No rejection reason is visible."

    known = (
        ("hold_only_family_features_consumer_bridge", "No trade candidate is cleared yet by the family/features bridge."),
        ("decisioncontracterror", "Execution contract rejected the projected decision payload."),
        ("missing_entry_strike", "Projected ENTER is missing strike, so execution would reject it."),
        ("entry_position_effect_not_open", "Projected ENTER does not clearly say it opens a position."),
        ("missing_option_symbol", "Projected ENTER is missing the option symbol."),
        ("missing_option_token", "Projected ENTER is missing the option token."),
        ("missing_or_invalid_limit_price", "Projected ENTER has missing or invalid price."),
        ("redis timeout", "Redis timeout is visible. Recheck before trusting dashboard state."),
        ("loading", "Redis/loading condition is visible. Recheck before any paper/live decision."),
    )

    for token, plain in known:
        if token in low:
            return plain

    return "Latest blocker/reason: " + raw


def _pdash_r2_contract_tokens(snapshot):
    hay = _pdash_r2_text(snapshot).lower()
    checks = (
        ("decisioncontracterror", "DecisionContractError"),
        ("missing_entry_strike", "missing_entry_strike"),
        ("entry_position_effect_not_open", "entry_position_effect_not_open"),
        ("missing_option_symbol", "missing_option_symbol"),
        ("missing_option_token", "missing_option_token"),
        ("missing_or_invalid_limit_price", "missing_or_invalid_limit_price"),
        ("redis timeout", "Redis timeout"),
        ("loading", "LOADING"),
    )
    found = []
    for needle, label in checks:
        if needle in hay and label not in found:
            found.append(label)
    return found


def _pdash_r2_enrich(snapshot):
    s = dict(snapshot or {})
    latest = s.get("latest_decision") or {}
    position = s.get("position") or {}
    pnl = s.get("pnl") or {}
    safety = s.get("safety") or {}
    streams = s.get("stream_lengths") or {}

    reason = (
        latest.get("reason")
        or latest.get("reject_reason")
        or latest.get("last_reason")
        or s.get("last_reason")
        or ""
    )

    projected_enter = (
        _pdash_r2_yes(latest.get("projected_enter"))
        or _pdash_r2_text(latest.get("action")).upper() == "ENTER"
    )

    paper = _pdash_r2_yes(safety.get("paper_enabled"))
    live = _pdash_r2_yes(safety.get("live_enabled"))
    broker = _pdash_r2_yes(safety.get("real_broker_enabled"))

    contract_tokens = _pdash_r2_contract_tokens(s)

    s["pdash_r2_human_summary"] = {
        "trade_candidates": latest.get("candidate_count", s.get("candidate_count", 0)),
        "active_strategy_or_family": latest.get("strategy") or latest.get("family") or latest.get("strategy_family") or "-",
        "latest_score": latest.get("strategy_score") or latest.get("score") or latest.get("score_total") or "-",
        "projected_enter": projected_enter,
        "last_blocker_plain": _pdash_r2_plain_reason(reason),
        "pnl_visible": pnl.get("visible_pnl_sum_last_events", pnl.get("latest_pnl", 0)),
        "position_status": position.get("status", safety.get("position_status", "-")),
        "orders_len": streams.get("orders:mme:stream", safety.get("orders_len", "-")),
        "risk_len": streams.get("risk:mme:stream", safety.get("risk_len", "-")),
        "execution_len": streams.get("execution:mme:stream", safety.get("execution_len", "-")),
        "trades_len": streams.get("trades:mme:stream", safety.get("trades_len", "-")),
        "safety_plain": "WARNING: paper/live/broker flag appears enabled." if (paper or live or broker) else "SAFE: paper/live/broker flags appear disabled.",
        "contract_status_plain": "Contract blocker visible: " + ", ".join(contract_tokens) if contract_tokens else "No known contract error token is visible.",
        "contract_error_tokens": contract_tokens,
    }

    s["pdash_r2_contract_watch"] = {
        "read_only": True,
        "tokens_found": contract_tokens,
    }

    return s


def build_snapshot():
    return _pdash_r2_enrich(_PDASH_R2_BASE_BUILD_SNAPSHOT())


def _pdash_r2_panel(snapshot):
    x = (snapshot or {}).get("pdash_r2_human_summary") or {}

    rows = (
        ("Trade candidates", x.get("trade_candidates", "-")),
        ("Active strategy / family", x.get("active_strategy_or_family", "-")),
        ("Latest score", x.get("latest_score", "-")),
        ("Projected ENTER", "YES" if x.get("projected_enter") else "NO"),
        ("Last blocker", x.get("last_blocker_plain", "-")),
        ("PnL", x.get("pnl_visible", "-")),
        ("Position", x.get("position_status", "-")),
        ("Orders / Risk / Execution / Trades", "%s / %s / %s / %s" % (
            x.get("orders_len", "-"),
            x.get("risk_len", "-"),
            x.get("execution_len", "-"),
            x.get("trades_len", "-"),
        )),
        ("Safety", x.get("safety_plain", "-")),
        ("Contract watch", x.get("contract_status_plain", "-")),
    )

    body = "".join(
        "<tr><td>%s</td><td class='mono'>%s</td></tr>" % (_pdash_r2_html(k), _pdash_r2_html(v))
        for k, v in rows
    )

    return (
        "<section class='card'>"
        "<h2>Simple Blocker & Contract Watch</h2>"
        "<table>" + body + "</table>"
        "<p class='muted'>PDASH R2 is display-only. It does not start services, place orders, or mutate Redis.</p>"
        "</section>"
    )


def render_html(snapshot):
    enriched = _pdash_r2_enrich(snapshot)
    html = _PDASH_R2_BASE_RENDER_HTML(enriched)
    panel = _pdash_r2_panel(enriched)

    if "</body>" in html:
        return html.replace("</body>", panel + "</body>", 1)
    if "</html>" in html:
        return html.replace("</html>", panel + "</html>", 1)
    return html + panel

# END PDASH_R2_PLAIN_LANGUAGE_BLOCKER_CONTRACT_WATCH

if __name__ == "__main__":
    raise SystemExit(main())
