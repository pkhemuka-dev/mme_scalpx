from __future__ import annotations

import argparse
import html
import json
import shutil
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

VERSION = "OPS-DASH-R3H-LITE"
DASHBOARD_BASELINE_MS = int(time.time() * 1000)
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


def _gb(n: int) -> str:
    try:
        return "%.1f GB" % (float(n) / (1024.0 ** 3))
    except Exception:
        return "NA"



def _safe_xlen(r, key: str) -> int:
    try:
        return int(r.xlen(key))
    except Exception:
        return -1


def _status_cell(value: str) -> str:
    return "<td class='mono'>%s</td>" % esc(value)



def _stream_first_last_ms(r, key: str):
    try:
        first = r.xrange(key, count=1)
        last = r.xrevrange(key, count=1)
        first_id = first[0][0].decode() if first and isinstance(first[0][0], bytes) else (first[0][0] if first else "-")
        last_id = last[0][0].decode() if last and isinstance(last[0][0], bytes) else (last[0][0] if last else "-")
        first_ms = int(str(first_id).split("-")[0]) if first_id != "-" else None
        last_ms = int(str(last_id).split("-")[0]) if last_id != "-" else None
        count = int(r.xlen(key))
        return count, str(first_id), str(last_id), first_ms, last_ms
    except Exception:
        return -1, "-", "-", None, None


def _capture_band(minutes: float) -> str:
    if minutes < 10:
        return "FORENSIC_ONLY_LT_10_MIN"
    if minutes < 30:
        return "DIAGNOSTIC_CAPTURE_10_TO_30_MIN"
    if minutes < 120:
        return "PARTIAL_CANDIDATE_WATCH_30_TO_120_MIN"
    if minutes < 240:
        return "MINIMUM_USEFUL_CAPTURE_120_TO_240_MIN"
    return "PREFERRED_BACKTEST_GRADE_CAPTURE_240_MIN_PLUS"



def _decode_text(x) -> str:
    if isinstance(x, bytes):
        return x.decode("utf-8", "replace")
    return "" if x is None else str(x)


def _error_fields_text(fields) -> str:
    try:
        if not isinstance(fields, dict):
            return _decode_text(fields)
        parts = []
        for k, v in fields.items():
            ks = _decode_text(k)
            vs = _decode_text(v)
            if ks in ("payload_json", "error", "message", "exception", "exc", "reason", "kind", "service", "traceback"):
                parts.append("%s=%s" % (ks, vs[:500]))
        if not parts:
            for k, v in list(fields.items())[:6]:
                parts.append("%s=%s" % (_decode_text(k), _decode_text(v)[:240]))
        text = " | ".join(parts)
        if "payload_json=" in text:
            raw = text.split("payload_json=", 1)[1]
            try:
                obj = json.loads(raw)
                obj_parts = []
                for key in ("type", "error_type", "exception", "message", "reason", "service", "instance_id"):
                    if key in obj:
                        obj_parts.append("%s=%s" % (key, str(obj.get(key))[:240]))
                if obj_parts:
                    text = text + " | parsed:" + " | ".join(obj_parts)
            except Exception:
                pass
        return text
    except Exception as exc:
        return "ERR_DECODING_ERROR_FIELDS: %s" % str(exc)[:120]


def _error_kind(text: str) -> str:
    if "FeatureFamilyContractError" in text:
        return "FeatureFamilyContractError"
    if "LockError" in text:
        return "LockError"
    if "FeedStartupError" in text:
        return "FeedStartupError"
    if "Timeout" in text or "timeout" in text:
        return "Timeout"
    if "Connection" in text or "connection" in text:
        return "Connection"
    if "Traceback" in text:
        return "Traceback"
    if "error_type=" in text:
        return text.split("error_type=", 1)[1].split("|", 1)[0].strip()[:80]
    if "type=" in text:
        return text.split("type=", 1)[1].split("|", 1)[0].strip()[:80]
    return "Other"



def _decision_text(x) -> str:
    if isinstance(x, bytes):
        return x.decode("utf-8", "replace")
    return "" if x is None else str(x)


def _decision_payload(fields):
    out = {}
    try:
        if not isinstance(fields, dict):
            return out
        for k, v in fields.items():
            ks = _decision_text(k)
            vs = _decision_text(v)
            out[ks] = vs
        raw = out.get("payload_json") or out.get("payload") or ""
        if raw:
            try:
                obj = json.loads(raw)
                if isinstance(obj, dict):
                    out.update(obj)
            except Exception:
                pass
    except Exception:
        pass
    return out


def _pick_first(obj, keys, default="-"):
    for key in keys:
        if key in obj and obj.get(key) not in (None, ""):
            return obj.get(key)
    return default


def _infer_action(obj) -> str:
    action = str(_pick_first(obj, [
        "action", "final_action", "decision_action", "order_action",
        "strategy_action", "activation_action", "signal", "verdict"
    ], "")).upper()
    did = str(obj.get("decision_id", "")).upper()
    text = json.dumps(obj, sort_keys=True, default=str)[:2500].upper()
    if action:
        if "HOLD" in action:
            return "HOLD"
        if "CANDIDATE" in action:
            return "CANDIDATE"
        if "ENTRY_READY" in action or "ENTRY" in action:
            return "ENTRY_READY"
        return action[:60]
    if "STRATEGY-HOLD" in did or "HOLD" in did or '"HOLD"' in text:
        return "HOLD"
    if "CANDIDATE" in text:
        return "CANDIDATE"
    if "ENTRY_READY" in text:
        return "ENTRY_READY"
    return "UNKNOWN"


def _hold_interpretation(obj, action: str) -> str:
    text = json.dumps(obj, sort_keys=True, default=str)[:2500]
    upper = text.upper()
    if action != "HOLD":
        return "NOT_HOLD_REVIEW_SIGNAL"
    if "VIEW_DATA_INVALID" in upper or "DATA_INVALID" in upper:
        return "HOLD_INFRA_OR_VIEW_DATA_INVALID"
    if "PROVIDER" in upper and ("INVALID" in upper or "NOT_READY" in upper or "STALE" in upper):
        return "HOLD_PROVIDER_OR_SNAPSHOT_NOT_READY"
    if "REPORT_ONLY" in upper or "ACTIVATION_REPORT_ONLY" in upper:
        return "HOLD_REPORT_ONLY_SAFETY_LAYER"
    if "SAFE_TO_PROMOTE" in upper and "TRUE" in upper:
        return "HOLD_CANDIDATE_VISIBLE_BUT_PAPER_BLOCKED_UNTIL_APPROVAL"
    if "FAILED_STAGE" in upper or "BLOCKER" in upper or "ELIGIBLE" in upper:
        return "HOLD_STRATEGY_GATE_OR_BRANCH_BLOCKER"
    return "HOLD_REASON_NOT_EXPLICIT_IN_SAMPLE"


def decision_hold_reason_panel() -> str:
    try:
        r = redis_client()
        items = r.xrevrange("decisions:mme:stream", count=40)
        if not items:
            return "<table><tr><td>Decision status</td><td class='mono'>NO_DECISIONS_VISIBLE</td></tr></table>"

        dist = {}
        interpretation_dist = {}
        rows = []
        newest_ms = None
        oldest_ms = None
        latest_action = "UNKNOWN"
        latest_interp = "NA"
        latest_reason = "-"
        latest_family = "-"
        latest_side = "-"
        latest_safe = "-"
        latest_candidate_count = "-"

        for idx, (item_id, fields) in enumerate(items):
            sid = _decision_text(item_id)
            try:
                ms = int(str(sid).split("-", 1)[0])
                newest_ms = ms if newest_ms is None else max(newest_ms, ms)
                oldest_ms = ms if oldest_ms is None else min(oldest_ms, ms)
            except Exception:
                pass

            obj = _decision_payload(fields)
            action = _infer_action(obj)
            interp = _hold_interpretation(obj, action)
            dist[action] = dist.get(action, 0) + 1
            interpretation_dist[interp] = interpretation_dist.get(interp, 0) + 1

            reason = _pick_first(obj, [
                "activation_reason", "hold_reason", "reason", "failed_stage",
                "primary_blocker", "blocker", "status_reason", "consumer_view_reason"
            ], "-")
            family = _pick_first(obj, ["family", "selected_family", "strategy_family", "branch_family"], "-")
            side = _pick_first(obj, ["side", "selected_side", "branch_side"], "-")
            safe = _pick_first(obj, ["safe_to_promote", "live_orders_allowed", "activation_report_only"], "-")
            ccount = _pick_first(obj, ["candidate_count", "candidates", "candidate_total"], "-")

            if idx == 0:
                latest_action = action
                latest_interp = interp
                latest_reason = reason
                latest_family = family
                latest_side = side
                latest_safe = safe
                latest_candidate_count = ccount

            if idx < 6:
                rows.append(
                    "<tr><td class='mono'>%s</td><td class='mono'>%s</td><td class='mono'>%s</td>"
                    "<td class='mono'>%s</td><td class='mono'>%s/%s</td><td class='mono'>%s</td></tr>"
                    % (esc(sid), esc(action), esc(interp), esc(str(reason)[:160]), esc(family), esc(side), esc(str(ccount)[:80]))
                )

        span_min = ((newest_ms - oldest_ms) / 60000.0) if newest_ms is not None and oldest_ms is not None and newest_ms >= oldest_ms else 0.0
        rate = (len(items) / span_min) if span_min > 0 else 0.0
        dist_txt = ", ".join("%s=%s" % (esc(k), v) for k, v in sorted(dist.items(), key=lambda kv: (-kv[1], kv[0]))) or "NONE"
        interp_txt = ", ".join("%s=%s" % (esc(k), v) for k, v in sorted(interpretation_dist.items(), key=lambda kv: (-kv[1], kv[0]))[:6]) or "NONE"

        headline = (
            "<table>"
            "<tr><td>Latest action</td><td class='mono'>%s</td></tr>"
            "<tr><td>Latest HOLD interpretation</td><td class='mono'>%s</td></tr>"
            "<tr><td>Latest reason/blocker</td><td class='mono'>%s</td></tr>"
            "<tr><td>Latest family/side</td><td class='mono'>%s/%s</td></tr>"
            "<tr><td>Latest safe/candidate fields</td><td class='mono'>safe_or_report=%s candidate_count=%s</td></tr>"
            "<tr><td>Sampled decisions</td><td class='mono'>%s</td></tr>"
            "<tr><td>Sampled span/rate</td><td class='mono'>%.1f min / %.1f decisions per min</td></tr>"
            "<tr><td>Action distribution</td><td class='mono'>%s</td></tr>"
            "<tr><td>HOLD interpretation distribution</td><td class='mono'>%s</td></tr>"
            "<tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - dashboard never promotes paper</td></tr>"
            "</table>"
            % (
                esc(latest_action),
                esc(latest_interp),
                esc(str(latest_reason)[:220]),
                esc(latest_family),
                esc(latest_side),
                esc(str(latest_safe)[:120]),
                esc(str(latest_candidate_count)[:80]),
                len(items),
                span_min,
                rate,
                dist_txt,
                interp_txt,
            )
        )
        detail = (
            "<table><tr><th>ID</th><th>Action</th><th>Interpretation</th><th>Reason/blocker</th><th>Family/side</th><th>Candidate count</th></tr>"
            + "".join(rows)
            + "</table>"
        )
        return headline + detail
    except Exception as exc:
        return "<table><tr><td>decision hold reason</td><td class='mono'>ERR: %s</td></tr></table>" % esc(str(exc)[:180])

def new_errors_since_baseline_panel() -> str:
    try:
        r = redis_client()
        total = int(r.xlen("system:errors:stream"))
        baseline_id = "%d-0" % DASHBOARD_BASELINE_MS
        now_ms = int(time.time() * 1000)

        latest = r.xrevrange("system:errors:stream", count=1)
        latest_id = "-"
        latest_age = "NA"
        if latest:
            latest_id = _decode_text(latest[0][0])
            try:
                latest_ms = int(str(latest_id).split("-", 1)[0])
                latest_age = "%.1f min" % ((now_ms - latest_ms) / 60000.0)
            except Exception:
                latest_age = "NA"

        # Intentionally capped for dashboard speed. It is a live visibility panel, not an audit engine.
        new_items = r.xrange("system:errors:stream", min=baseline_id, max="+", count=200)
        new_count_sample = len(new_items)

        kinds = {}
        feature_contract_count = 0
        rows = []
        for item_id, fields in new_items[-10:]:
            sid = _decode_text(item_id)
            text = _error_fields_text(fields)
            kind = _error_kind(text)
            kinds[kind] = kinds.get(kind, 0) + 1
            if kind == "FeatureFamilyContractError":
                feature_contract_count += 1
            rows.append(
                "<tr><td class='mono'>%s</td><td class='mono'>%s</td><td class='mono'>%s</td></tr>"
                % (esc(sid), esc(kind), esc(text[:360]))
            )

        if not rows:
            rows.append("<tr><td>-</td><td class='mono'>NO_NEW_ERRORS_SINCE_DASHBOARD_BASELINE</td><td>-</td></tr>")

        top = ", ".join("%s=%s" % (esc(k), v) for k, v in sorted(kinds.items(), key=lambda kv: (-kv[1], kv[0]))[:6]) or "NONE"
        continuing = "YES_REVIEW_NOW" if new_count_sample > 0 else "NO_NEW_ERRORS_SINCE_BASELINE"
        fc_status = "YES" if feature_contract_count > 0 else "NO"

        headline = (
            "<table>"
            "<tr><td>Dashboard baseline ID</td><td class='mono'>%s</td></tr>"
            "<tr><td>Total errors stream length</td><td class='mono'>%s</td></tr>"
            "<tr><td>New errors sample since baseline</td><td class='mono'>%s</td></tr>"
            "<tr><td>Continuing after baseline?</td><td class='mono'>%s</td></tr>"
            "<tr><td>FeatureFamilyContractError since baseline?</td><td class='mono'>%s</td></tr>"
            "<tr><td>Latest error ID</td><td class='mono'>%s</td></tr>"
            "<tr><td>Latest error age</td><td class='mono'>%s</td></tr>"
            "<tr><td>Top new error types</td><td class='mono'>%s</td></tr>"
            "</table>"
            % (
                esc(baseline_id),
                total,
                new_count_sample,
                esc(continuing),
                esc(fc_status),
                esc(latest_id),
                esc(latest_age),
                top,
            )
        )
        detail = (
            "<table><tr><th>ID</th><th>Kind</th><th>Message sample</th></tr>"
            + "".join(rows)
            + "</table>"
        )
        return headline + detail
    except Exception as exc:
        return "<table><tr><td>new errors since baseline</td><td class='mono'>ERR: %s</td></tr></table>" % esc(str(exc)[:180])

def capture_grade_panel() -> str:
    streams = [
        ("fut zerodha", "ticks:mme:fut:zerodha:stream"),
        ("opt zerodha", "ticks:mme:opt:selected:zerodha:stream"),
        ("features", "features:mme:stream"),
        ("decisions", "decisions:mme:stream"),
        ("errors", "system:errors:stream"),
        ("orders", "orders:mme:stream"),
    ]
    try:
        r = redis_client()
        rows = []
        first_points = []
        last_points = []
        for label, key in streams:
            count, first_id, last_id, first_ms, last_ms = _stream_first_last_ms(r, key)
            if first_ms is not None:
                first_points.append(first_ms)
            if last_ms is not None:
                last_points.append(last_ms)
            span_min = ((last_ms - first_ms) / 60000.0) if first_ms is not None and last_ms is not None and last_ms >= first_ms else 0.0
            rate = (count / span_min) if span_min > 0 and count >= 0 else 0.0
            rows.append(
                "<tr><td>%s</td><td class='mono'>%s</td><td class='mono'>%s</td>"
                "<td class='mono'>%s</td><td class='mono'>%.1f</td><td class='mono'>%.1f/min</td></tr>"
                % (esc(label), esc(count), esc(first_id), esc(last_id), span_min, rate)
            )
        overall_min = ((max(last_points) - min(first_points)) / 60000.0) if first_points and last_points and max(last_points) >= min(first_points) else 0.0
        band = _capture_band(overall_min)
        headline = (
            "<table>"
            "<tr><td>Visible stream span</td><td class='mono'>%.1f min</td></tr>"
            "<tr><td>Capture progress band</td><td class='mono'>%s</td></tr>"
            "<tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - requires sealed day + candidate/shadow proof + approval</td></tr>"
            "<tr><td>B3 handoff</td><td class='mono'>B3 NEEDS CLEAN SEALED DAY</td></tr>"
            "</table>" % (overall_min, esc(band))
        )
        detail = (
            "<table><tr><th>Label</th><th>Count</th><th>First ID</th><th>Latest ID</th><th>Span min</th><th>Rate</th></tr>"
            + "".join(rows)
            + "</table>"
        )
        return headline + detail
    except Exception as exc:
        return "<table><tr><td>capture-grade progress</td><td class='mono'>ERR: %s</td></tr></table>" % esc(str(exc)[:180])

def mission_state_panel() -> str:
    env_names = [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_ALLOW_REAL_LIVE",
        "SCALPX_ALLOW_BROKER_ORDERS",
        "SCALPX_PAPER_ARMED",
        "SCALPX_ENABLE_PAPER",
        "SCALPX_ENABLE_LIVE",
    ]
    dangerous_env = [name for name in env_names if os.environ.get(name)]
    try:
        r = redis_client()
        counts = {
            "fut_zerodha": _safe_xlen(r, "ticks:mme:fut:zerodha:stream"),
            "opt_zerodha": _safe_xlen(r, "ticks:mme:opt:selected:zerodha:stream"),
            "features": _safe_xlen(r, "features:mme:stream"),
            "decisions": _safe_xlen(r, "decisions:mme:stream"),
            "errors": _safe_xlen(r, "system:errors:stream"),
            "orders": _safe_xlen(r, "orders:mme:stream"),
            "risk": _safe_xlen(r, "risk:mme:stream"),
            "execution": _safe_xlen(r, "execution:mme:stream"),
        }
    except Exception:
        counts = {k: -1 for k in ("fut_zerodha", "opt_zerodha", "features", "decisions", "errors", "orders", "risk", "execution")}

    feeds_p = proc_count("feeds")
    features_p = proc_count("features")
    strategy_p = proc_count("strategy")
    risk_p = proc_count("risk")
    exec_p = proc_count("execution")

    safe = (
        counts["orders"] == 0
        and counts["risk"] == 0
        and counts["execution"] == 0
        and risk_p == 0
        and exec_p == 0
        and not dangerous_env
    )
    observe_running = feeds_p > 0 and features_p > 0 and strategy_p > 0
    capture_visible = counts["fut_zerodha"] > 0 and counts["opt_zerodha"] > 0 and counts["features"] > 0
    decisions_growing_visible = counts["decisions"] > 0

    if not safe:
        state = "SAFETY_BLOCKED"
    elif not observe_running:
        state = "OBSERVE_ONLY_NOT_RUNNING"
    elif not capture_visible:
        state = "OBSERVE_ONLY_RUNNING_INFRA_INVALID"
    elif decisions_growing_visible:
        state = "DECISIONS_GROWING_HOLD_ONLY"
    else:
        state = "OBSERVE_ONLY_RUNNING_FEATURE_VALID"

    one_line = (
        ("SAFE" if safe else "NOT SAFE")
        + " | "
        + ("OBSERVE-ONLY RUNNING" if observe_running else "OBSERVE-ONLY NOT RUNNING")
        + " | "
        + ("CAPTURE DATA VISIBLE" if capture_visible else "CAPTURE DATA NOT READY")
        + " | "
        + ("DECISIONS PRESENT" if decisions_growing_visible else "DECISIONS NOT PRESENT")
        + " | NEW ERRORS TOTAL="
        + str(counts["errors"])
        + " | PAPER BLOCKED"
    )

    rows = [
        ("Mission", one_line),
        ("High-level state", state),
        ("Paper status", "PAPER BLOCKED - needs capture-grade + candidate/shadow proof + explicit approval"),
        ("Safety", "SAFE" if safe else "NOT SAFE"),
        ("Processes", "feeds=%s features=%s strategy=%s risk=%s execution=%s" % (feeds_p, features_p, strategy_p, risk_p, exec_p)),
        ("Streams", "fut_z=%s opt_z=%s features=%s decisions=%s errors=%s orders=%s risk=%s execution=%s" % (
            counts["fut_zerodha"], counts["opt_zerodha"], counts["features"], counts["decisions"],
            counts["errors"], counts["orders"], counts["risk"], counts["execution"]
        )),
        ("Risky env flags", ",".join(dangerous_env) if dangerous_env else "NONE"),
        ("A7 interpretation", "capture/readiness visibility only - dashboard must not control live/paper services"),
    ]
    return "<table>" + "".join("<tr><td>%s</td>%s</tr>" % (esc(k), _status_cell(v)) for k, v in rows) + "</table>"

def disk_space_panel() -> str:
    rows = []
    targets = [
        ("project", project_root()),
        ("home", Path.home()),
        ("tmp", Path("/tmp")),
    ]
    seen = set()
    for label, path in targets:
        try:
            resolved = str(path.resolve())
        except Exception:
            resolved = str(path)
        if resolved in seen:
            continue
        seen.add(resolved)
        try:
            usage = shutil.disk_usage(str(path))
            used_pct = (float(usage.used) / float(usage.total) * 100.0) if usage.total else 0.0
            status = "WARN" if usage.free < 10 * 1024**3 or used_pct >= 90.0 else "OK"
            rows.append(
                "<tr><td>%s</td><td class='mono'>%s</td>"
                "<td class='mono'>%s</td><td class='mono'>%s</td>"
                "<td class='mono'>%s</td><td class='mono'>%.1f%%</td>"
                "<td class='mono'>%s</td></tr>"
                % (
                    esc(label),
                    esc(resolved),
                    esc(_gb(usage.total)),
                    esc(_gb(usage.used)),
                    esc(_gb(usage.free)),
                    used_pct,
                    esc(status),
                )
            )
        except Exception as exc:
            rows.append(
                "<tr><td>%s</td><td class='mono'>%s</td>"
                "<td colspan='5' class='mono'>ERR: %s</td></tr>"
                % (esc(label), esc(resolved), esc(str(exc)[:160]))
            )
    return (
        "<table><tr><th>Label</th><th>Path</th><th>Total</th>"
        "<th>Used</th><th>Free</th><th>Used %</th><th>Status</th></tr>"
        + "".join(rows)
        + "</table>"
    )

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

    disk_space = disk_space_panel()
    mission_state = mission_state_panel()
    capture_grade = capture_grade_panel()
    new_errors_panel = new_errors_since_baseline_panel()
    decision_hold_panel = decision_hold_reason_panel()
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="2">
<title>MME-ScalpX OPS Dashboard R3H-LITE</title>
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
<div><h1>MME-ScalpX OPS Dashboard R3H-LITE</h1><div class="sub">R3H-LITE read-only · HOLD reason capped · action distribution · capture progress · paper blocked · no writes · no orders</div></div>
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
<div class="panel"><h3>A7 Mission State</h3>{mission_state}</div>
<div class="panel"><h3>Capture-Grade Progress</h3>{capture_grade}</div>
<div class="panel"><h3>New Errors Since Dashboard Baseline</h3>{new_errors_panel}</div>
<div class="panel"><h3>Decision HOLD Reason</h3>{decision_hold_panel}</div>
<div class="panel"><h3>Redis Stream Health</h3><table><tr><th>Label</th><th>Stream</th><th>Length</th><th>Latest ID</th><th>Status</th></tr>{stream_table}</table></div>
<div class="panel"><h3>Disk Space</h3>{disk_space}</div>
<div style="display:none">OPS Dashboard R2C compatibility marker</div>
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
