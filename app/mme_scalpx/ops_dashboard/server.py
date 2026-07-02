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
from urllib.parse import urlparse, parse_qs

try:
    import redis
except Exception:
    redis = None

VERSION = "OPS-DASH-R4F-LX-R3E-EXPORT-PATHS-ONLY"
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


# LANE_X_DASH_R4B_INTEGRATED_REPLAY_BACKTEST_UI_SKELETON
# LANE_X_DASH_R4B_R2_PNL_LABEL_MARKER_HARDEN
REPLAY_UI_ROW_CAP = 500
REPLAY_LATEST_RUN_LIMIT = 20
REPLAY_LATEST_FILE_LIMIT = 50

REPLAY_REPORT_TYPES = [
    "candidate_summary",
    "trade_candidates",
    "near_candidates",
    "shadow_fills",
    "pnl",
    "strategy_wise_pnl",
    "day_wise_pnl",
    "blocker_summary",
    "failed_stage_summary",
    "score_distribution",
    "full_replay_report",
]
REPLAY_STRATEGIES = ["all", "MIST", "MISB", "MISC", "MISR", "MISO", "MIV-R"]
REPLAY_SIDES = ["all", "CALL", "PUT"]
REPLAY_DATE_MODES = ["single_day", "date_range"]
REPLAY_DATASET_SOURCES = ["latest_available", "sealed_live_capture", "replay_dataset", "evidence_bundle"]


def _r4b_param(params, name: str, default: str = "") -> str:
    try:
        raw = params.get(name, [default]) if isinstance(params, dict) else [default]
        val = raw[0] if isinstance(raw, list) else raw
        val = "" if val is None else str(val)
        return val[:80]
    except Exception:
        return default


def _r4b_choice(params, name: str, choices, default: str) -> str:
    val = _r4b_param(params, name, default)
    return val if val in choices else default


def _r4b_date_param(params, name: str) -> str:
    val = _r4b_param(params, name, "")
    clean = "".join(ch for ch in val if ch.isdigit() or ch == "-")[:10]
    return clean


def _r4b_select(name: str, choices, selected: str) -> str:
    opts = []
    for item in choices:
        sel = " selected" if item == selected else ""
        opts.append("<option value='%s'%s>%s</option>" % (esc(item), sel, esc(item)))
    return "<select name='%s'>%s</select>" % (esc(name), "".join(opts))


def _r4b_file_row(path: Path) -> dict:
    st = path.stat()
    return {
        "path": str(path.relative_to(project_root())),
        "mtime": st.st_mtime,
        "size": st.st_size,
        "when": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
    }


def _r4b_bounded_files(base_rel: str, suffixes, keywords, limit: int, max_depth: int = 1, max_seen: int = 1200):
    base = project_root() / base_rel
    if not base.exists():
        return []
    suffixes = tuple(suffixes or [])
    keywords = [str(x).lower() for x in (keywords or [])]
    rows = []
    queue = [(base, 0)]
    seen = 0
    while queue and seen < max_seen:
        current, depth = queue.pop(0)
        try:
            children = list(current.iterdir())
        except Exception:
            continue
        for child in children:
            seen += 1
            if seen > max_seen:
                break
            try:
                if child.is_dir():
                    if depth < max_depth:
                        queue.append((child, depth + 1))
                    continue
                if not child.is_file():
                    continue
                name = child.name.lower()
                full = str(child).lower()
                if suffixes and not name.endswith(suffixes):
                    continue
                if keywords and not any(k in name or k in full for k in keywords):
                    continue
                rows.append(_r4b_file_row(child))
            except Exception:
                continue
    rows.sort(key=lambda x: x["mtime"], reverse=True)
    return rows[:limit]


def _r4b_latest_replay_runs(limit: int = REPLAY_LATEST_RUN_LIMIT):
    base = project_root() / "run" / "replay"
    if not base.exists():
        return []
    rows = []
    try:
        for p in list(base.iterdir())[:800]:
            if not p.is_dir():
                continue
            st = p.stat()
            summary_names = []
            fixed = {"10_run_summary.json", "engine_result.json", "00_manifest.json", "03_integrity_report.json", "04_metrics_summary.json"}
            try:
                for child in list(p.iterdir())[:160]:
                    if child.is_file() and child.name in fixed:
                        summary_names.append(child.name)
                    elif child.is_dir():
                        try:
                            for grand in list(child.iterdir())[:80]:
                                if grand.is_file() and grand.name in fixed:
                                    summary_names.append(child.name + "/" + grand.name)
                        except Exception:
                            pass
            except Exception:
                pass
            rows.append({
                "path": str(p.relative_to(project_root())),
                "mtime": st.st_mtime,
                "when": datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                "summaries": ", ".join(summary_names[:6]) if summary_names else "-",
            })
    except Exception:
        return []
    rows.sort(key=lambda x: x["mtime"], reverse=True)
    return rows[:limit]


def _r4b_find_key(obj, key: str, depth: int = 0):
    if depth > 6:
        return None
    if isinstance(obj, dict):
        if key in obj:
            return obj.get(key)
        for v in list(obj.values())[:250]:
            found = _r4b_find_key(v, key, depth + 1)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj[:250]:
            found = _r4b_find_key(v, key, depth + 1)
            if found is not None:
                return found
    return None


def _r4b_json_summary_from_file(rel_path: str):
    try:
        p = project_root() / rel_path
        if not p.is_file() or p.stat().st_size > 2 * 1024 * 1024:
            return None
        obj = json.loads(p.read_text(errors="replace"))
        keys = [
            "classification",
            "replay_rc",
            "trade_count",
            "pnl_total",
            "shadow_pnl_total",
            "win_count",
            "big_files_over_50mb",
            "safety_post",
            "replay_proc",
            "pnl_label",
        ]
        out = {}
        for key in keys:
            val = _r4b_find_key(obj, key)
            if val is not None:
                out[key] = val
        return out
    except Exception:
        return None


def _r4b_latest_reports():
    keywords = ["replay", "backtest", "pnl", "shadow", "candidate", "r35c", "r5d"]
    suffixes = [".json", ".md", ".txt", ".csv"]
    rows = []
    rows.extend(_r4b_bounded_files("run/proofs", suffixes, keywords, REPLAY_LATEST_FILE_LIMIT, max_depth=1, max_seen=1800))
    rows.extend(_r4b_bounded_files("run/audits", suffixes, keywords, REPLAY_LATEST_FILE_LIMIT, max_depth=1, max_seen=1800))
    rows.sort(key=lambda x: x["mtime"], reverse=True)
    return rows[:REPLAY_LATEST_FILE_LIMIT]


def _r4b_synthetic_pnl_rows(report_rows):
    rows = []
    for row in report_rows:
        low = row["path"].lower()
        if "r35c" in low and "r5d" in low and ("pnl" in low or "summary" in low or "synthetic" in low):
            summary = _r4b_json_summary_from_file(row["path"]) if low.endswith(".json") else None
            if summary:
                detail = " | ".join("%s=%s" % (k, summary.get(k)) for k in sorted(summary.keys()))
            else:
                detail = "existing artifact; open file for full details"
            rows.append((row, detail))
    return rows[:8]



# LANE_X_DASH_R4C_R3_MINIMAL_SAFE_READ_ONLY_REPLAY_SUMMARY_PANEL
def _r4c_r3_short(value, limit: int = 140) -> str:
    try:
        text = "-" if value is None else str(value)
    except Exception:
        text = "-"
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def r4c_r3_minimal_replay_summary_panel(replay_runs, report_rows, synthetic_rows) -> str:
    try:
        replay_run_count = len(replay_runs or [])
        report_count = len(report_rows or [])
        synthetic_count = len(synthetic_rows or [])
    except Exception:
        replay_run_count = report_count = synthetic_count = 0

    latest_run = "-"
    latest_report = "-"
    latest_synthetic = "-"

    try:
        if replay_runs:
            latest_run = replay_runs[0].get("path", "-")
    except Exception:
        latest_run = "-"

    try:
        if report_rows:
            latest_report = report_rows[0].get("path", "-")
    except Exception:
        latest_report = "-"

    try:
        if synthetic_rows:
            latest_synthetic = synthetic_rows[0][0].get("path", "-")
    except Exception:
        latest_synthetic = "-"

    return (
        "<h3>Minimal Existing Replay Summary</h3>"
        "<p class='mono'>R4C-R3 summary is read-only and index-only. It does not execute replay, parse raw datasets, call subprocess, call broker, or touch paper/live/risk/execution.</p>"
        "<table>"
        "<tr><th>Metric</th><th>Value</th></tr>"
        "<tr><td>Mode</td><td class='mono'>R4C_R3_MINIMAL_SAFE_READ_ONLY_PANEL</td></tr>"
        "<tr><td>Bounded replay runs visible</td><td class='mono'>%s</td></tr>"
        "<tr><td>Bounded replay/proof/report files visible</td><td class='mono'>%s</td></tr>"
        "<tr><td>Synthetic shadow PnL artifacts visible</td><td class='mono'>%s</td></tr>"
        "<tr><td>Latest replay run</td><td class='mono'>%s</td></tr>"
        "<tr><td>Latest replay/proof/report</td><td class='mono'>%s</td></tr>"
        "<tr><td>Latest synthetic shadow PnL artifact</td><td class='mono'>%s</td></tr>"
        "<tr><td>PNL label</td><td class='mono'>Replay-only synthetic/shadow PnL; not broker PnL; not paper PnL; not live PnL</td></tr>"
        "</table>"
        % (
            replay_run_count,
            report_count,
            synthetic_count,
            esc(_r4c_r3_short(latest_run, 180)),
            esc(_r4c_r3_short(latest_report, 180)),
            esc(_r4c_r3_short(latest_synthetic, 180)),
        )
    )


# LANE_X_DASH_R4D_SMALL_READ_ONLY_STRATEGY_DAY_BLOCKER_TABLES
def _r4d_short(value, limit: int = 150) -> str:
    try:
        text = "-" if value is None else str(value)
    except Exception:
        text = "-"
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _r4d_collect_artifact_text(replay_runs, report_rows, synthetic_rows):
    items = []

    try:
        for row in (replay_runs or [])[:20]:
            path = row.get("path", "-") if isinstance(row, dict) else str(row)
            items.append(("replay_run", path, ""))
    except Exception:
        pass

    try:
        for row in (report_rows or [])[:50]:
            path = row.get("path", "-") if isinstance(row, dict) else str(row)
            items.append(("proof_report", path, ""))
    except Exception:
        pass

    try:
        for row in (synthetic_rows or [])[:20]:
            if isinstance(row, (list, tuple)) and row:
                artifact = row[0]
                summary = row[1] if len(row) > 1 else ""
                path = artifact.get("path", "-") if isinstance(artifact, dict) else str(artifact)
            elif isinstance(row, dict):
                path = row.get("path", "-")
                summary = row.get("summary", "")
            else:
                path = str(row)
                summary = ""
            items.append(("synthetic_pnl", path, summary))
    except Exception:
        pass

    return items


def _r4d_bucket_count(items, terms):
    count = 0
    latest = "-"
    for kind, path, summary in items:
        hay = (str(kind) + " " + str(path) + " " + str(summary)).lower()
        if any(str(t).lower() in hay for t in terms):
            count += 1
            if latest == "-":
                latest = path
    return count, latest


def _r4d_bucket_rows(items, buckets):
    out = []
    for label, terms, meaning in buckets:
        count, latest = _r4d_bucket_count(items, terms)
        out.append(
            "<tr>"
            "<td class='mono'>%s</td>"
            "<td class='mono'>%s</td>"
            "<td class='mono'>%s</td>"
            "<td class='mono'>%s</td>"
            "</tr>"
            % (
                esc(label),
                esc(str(count)),
                esc(_r4d_short(latest, 180)),
                esc(meaning),
            )
        )
    return "".join(out)


def r4d_small_readonly_tables_panel(replay_runs, report_rows, synthetic_rows) -> str:
    items = _r4d_collect_artifact_text(replay_runs, report_rows, synthetic_rows)

    strategy_buckets = [
        ("MIST", ["mist"], "strategy artifact mention only"),
        ("MISB", ["misb"], "strategy artifact mention only"),
        ("MISC", ["misc"], "strategy artifact mention only"),
        ("MISR", ["misr"], "strategy artifact mention only"),
        ("MISO", ["miso"], "strategy artifact mention only"),
        ("MIV-R", ["miv-r", "miv_r", "miv"], "research/audit probe only"),
        ("Synthetic/R35C", ["r35c", "synthetic", "shadow_pnl"], "offline synthetic/shadow replay artifacts"),
    ]

    day_buckets = [
        ("2026-06-01 / Jun01", ["2026-06-01", "20260601", "june01", "jun01"], "day artifact mention only"),
        ("2026-06-02 / Jun02", ["2026-06-02", "20260602", "june02", "jun02"], "day artifact mention only"),
        ("R35C replay family", ["r35c"], "latest replay/backtest family"),
        ("R35B replay family", ["r35b"], "earlier replay/backtest family"),
    ]

    blocker_buckets = [
        ("PnL / synthetic / shadow", ["pnl", "synthetic", "shadow"], "PnL-related artifact mention only"),
        ("Candidate", ["candidate"], "candidate/report artifact mention only"),
        ("Blocker / failed stage", ["blocker", "failed_stage", "failed-stage"], "blocker artifact mention only"),
        ("Provider / not ready", ["provider", "not_ready", "failover"], "provider-readiness artifact mention only"),
        ("Safety / no order", ["no_order", "no-order", "safety"], "safety artifact mention only"),
    ]

    return (
        "<h3>Small Read-only Replay Artifact Index</h3>"
        "<p class='mono'>R4D_SMALL_READ_ONLY_TABLES. These are bounded artifact-index tables only. They do not run replay, do not parse raw datasets, and do not calculate official PnL.</p>"
        "<h4>Strategy artifact index</h4>"
        "<table><tr><th>Bucket</th><th>Count</th><th>Latest matching artifact</th><th>Meaning</th></tr>"
        + _r4d_bucket_rows(items, strategy_buckets)
        + "</table>"
        "<h4>Day / replay-family artifact index</h4>"
        "<table><tr><th>Bucket</th><th>Count</th><th>Latest matching artifact</th><th>Meaning</th></tr>"
        + _r4d_bucket_rows(items, day_buckets)
        + "</table>"
        "<h4>Blocker / PnL / safety artifact index</h4>"
        "<table><tr><th>Bucket</th><th>Count</th><th>Latest matching artifact</th><th>Meaning</th></tr>"
        + _r4d_bucket_rows(items, blocker_buckets)
        + "</table>"
    )


# LANE_X_DASH_R4E_EXACT_R35C_R5D_SYNTHETIC_PNL_PROOF_PARSER
R4E_MAX_PROOF_BYTES = 512 * 1024


def _r4e_short(value, limit: int = 180) -> str:
    try:
        text = "-" if value is None else str(value)
    except Exception:
        text = "-"
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _r4e_find_latest_r35c_r5d_proof():
    try:
        root = project_root()
        proof_dir = root / "run" / "proofs"
        patterns = [
            "*R35C*R5D*SYNTHETIC*PNL*.json",
            "*R35C_R5D*.json",
            "*R35C*R5D*.json",
        ]
        found = []
        for pat in patterns:
            for p in proof_dir.glob(pat):
                try:
                    if p.is_file() and p.stat().st_size <= R4E_MAX_PROOF_BYTES:
                        found.append(p)
                except Exception:
                    pass
        found = sorted(set(found), key=lambda p: p.stat().st_mtime, reverse=True)
        if not found:
            return None
        return found[0]
    except Exception:
        return None


def _r4e_find_value(obj, names, depth: int = 0):
    if depth > 8:
        return None
    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj.get(name)
        for v in list(obj.values())[:200]:
            found = _r4e_find_value(v, names, depth + 1)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for v in obj[:100]:
            found = _r4e_find_value(v, names, depth + 1)
            if found is not None:
                return found
    return None


def _r4e_load_r35c_r5d_row():
    p = _r4e_find_latest_r35c_r5d_proof()
    if p is None:
        return {
            "found": False,
            "path": "-",
            "classification": "R35C_R5D_PROOF_NOT_FOUND",
        }

    try:
        data = json.loads(p.read_text(errors="replace"))
    except Exception as e:
        return {
            "found": False,
            "path": str(p.relative_to(project_root())),
            "classification": "R35C_R5D_PROOF_LOAD_ERROR",
            "detail": repr(e),
        }

    row = {
        "found": True,
        "path": str(p.relative_to(project_root())),
        "classification": _r4e_find_value(data, ["classification"]),
        "replay_rc": _r4e_find_value(data, ["replay_rc"]),
        "trade_count": _r4e_find_value(data, ["trade_count"]),
        "pnl_total": _r4e_find_value(data, ["pnl_total"]),
        "shadow_pnl_total": _r4e_find_value(data, ["shadow_pnl_total"]),
        "win_count": _r4e_find_value(data, ["win_count"]),
        "big_files_over_50mb": _r4e_find_value(data, ["big_files_over_50mb"]),
        "safety_post": _r4e_find_value(data, ["safety_post"]),
        "replay_proc": _r4e_find_value(data, ["replay_proc"]),
        "pnl_label": _r4e_find_value(data, ["pnl_label"]),
    }

    if not row.get("pnl_label"):
        row["pnl_label"] = "Replay-only synthetic shadow PnL; not broker PnL; not paper PnL; not live PnL"

    return row


def r4e_exact_r35c_r5d_synthetic_pnl_panel() -> str:
    row = _r4e_load_r35c_r5d_row()

    return (
        "<h3>Exact R35C-R5D Synthetic PnL Proof</h3>"
        "<p class='mono'>R4E_EXACT_R35C_R5D_PROOF_ONLY. This reads one known-small proof JSON only. It does not run replay, parse raw datasets, call subprocess, call broker, or touch paper/live/risk/execution.</p>"
        "<table>"
        "<tr><th>Field</th><th>Value</th></tr>"
        "<tr><td>Found</td><td class='mono'>%s</td></tr>"
        "<tr><td>Proof path</td><td class='mono'>%s</td></tr>"
        "<tr><td>Classification</td><td class='mono'>%s</td></tr>"
        "<tr><td>Replay rc</td><td class='mono'>%s</td></tr>"
        "<tr><td>Trade count</td><td class='mono'>%s</td></tr>"
        "<tr><td>PnL total</td><td class='mono'>%s</td></tr>"
        "<tr><td>Shadow PnL total</td><td class='mono'>%s</td></tr>"
        "<tr><td>Win count</td><td class='mono'>%s</td></tr>"
        "<tr><td>Big files over 50MB</td><td class='mono'>%s</td></tr>"
        "<tr><td>Safety post</td><td class='mono'>%s</td></tr>"
        "<tr><td>Replay proc</td><td class='mono'>%s</td></tr>"
        "<tr><td>PNL label</td><td class='mono'>%s</td></tr>"
        "</table>"
        % (
            esc(_r4e_short(row.get("found"))),
            esc(_r4e_short(row.get("path"), 220)),
            esc(_r4e_short(row.get("classification"), 220)),
            esc(_r4e_short(row.get("replay_rc"))),
            esc(_r4e_short(row.get("trade_count"))),
            esc(_r4e_short(row.get("pnl_total"))),
            esc(_r4e_short(row.get("shadow_pnl_total"))),
            esc(_r4e_short(row.get("win_count"))),
            esc(_r4e_short(row.get("big_files_over_50mb"))),
            esc(_r4e_short(row.get("safety_post"))),
            esc(_r4e_short(row.get("replay_proc"))),
            esc(_r4e_short(row.get("pnl_label"), 220)),
        )
    )


# LANE_X_DASH_R4F_EXPORT_PATHS_ONLY_EXISTING_ARTIFACTS
def _r4f_short(value, limit: int = 220) -> str:
    try:
        text = "-" if value is None else str(value)
    except Exception:
        text = "-"
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _r4f_row(label, path, note):
    return (
        "<tr>"
        "<td class='mono'>%s</td>"
        "<td class='mono'>%s</td>"
        "<td class='mono'>%s</td>"
        "</tr>"
        % (
            esc(_r4f_short(label, 120)),
            esc(_r4f_short(path, 260)),
            esc(_r4f_short(note, 180)),
        )
    )


def r4f_export_paths_only_panel(replay_runs, report_rows, synthetic_rows) -> str:
    rows = []

    # Exact known-small R35C-R5D proof path, if R4E helper exists.
    try:
        p = _r4e_find_latest_r35c_r5d_proof()
        if p is not None:
            rows.append(_r4f_row("exact_r35c_r5d_synthetic_pnl_proof", str(p.relative_to(project_root())), "copy path only; dashboard does not serve file"))
    except Exception:
        pass

    try:
        for row in (synthetic_rows or [])[:8]:
            if isinstance(row, (list, tuple)) and row:
                artifact = row[0]
                path = artifact.get("path", "-") if isinstance(artifact, dict) else str(artifact)
            elif isinstance(row, dict):
                path = row.get("path", "-")
            else:
                path = str(row)
            rows.append(_r4f_row("synthetic_shadow_pnl_artifact", path, "copy path only; replay-only synthetic/shadow"))
    except Exception:
        pass

    try:
        for row in (report_rows or [])[:12]:
            path = row.get("path", "-") if isinstance(row, dict) else str(row)
            label = "proof_or_report"
            low = str(path).lower()
            if "proof" in low:
                label = "proof_json"
            elif "report" in low:
                label = "report_md"
            elif "handoff" in low:
                label = "handoff_md"
            rows.append(_r4f_row(label, path, "existing bounded artifact path"))
    except Exception:
        pass

    try:
        for row in (replay_runs or [])[:8]:
            path = row.get("path", "-") if isinstance(row, dict) else str(row)
            rows.append(_r4f_row("replay_run_directory", path, "directory path only; no raw parse"))
    except Exception:
        pass

    if not rows:
        rows.append(_r4f_row("none", "-", "no bounded existing artifacts found"))

    return (
        "<h3>Existing Artifact Export Paths</h3>"
        "<p class='mono'>R4F_EXPORT_PATHS_ONLY. Copy paths only. The dashboard does not serve files, does not run replay, does not parse raw datasets, and does not create broker/paper/live PnL.</p>"
        "<table>"
        "<tr><th>Artifact type</th><th>Path</th><th>Note</th></tr>"
        + "".join(rows[:30])
        + "</table>"
    )

def replay_backtest_panel(params=None) -> str:
    params = params or {}
    date_from = _r4b_date_param(params, "date_from")
    date_to = _r4b_date_param(params, "date_to")
    date_mode = _r4b_choice(params, "date_mode", REPLAY_DATE_MODES, "single_day")
    strategy = _r4b_choice(params, "strategy", REPLAY_STRATEGIES, "all")
    side = _r4b_choice(params, "side", REPLAY_SIDES, "all")
    report_type = _r4b_choice(params, "report_type", REPLAY_REPORT_TYPES, "candidate_summary")
    dataset_source = _r4b_choice(params, "dataset_source", REPLAY_DATASET_SOURCES, "latest_available")

    replay_runs = _r4b_latest_replay_runs()
    report_rows = _r4b_latest_reports()
    synthetic_rows = _r4b_synthetic_pnl_rows(report_rows)

    run_html = []
    for row in replay_runs:
        run_html.append(
            "<tr><td class='mono'>%s</td><td class='mono'>%s</td><td class='mono'>%s</td></tr>"
            % (esc(row["when"]), esc(row["path"]), esc(row["summaries"]))
        )
    if not run_html:
        run_html.append("<tr><td>-</td><td class='mono'>NO_REPLAY_RUNS_FOUND_IN_BOUNDED_SCAN</td><td>-</td></tr>")

    report_html = []
    for row in report_rows[:20]:
        report_html.append(
            "<tr><td class='mono'>%s</td><td class='mono'>%.3f MB</td><td class='mono'>%s</td></tr>"
            % (esc(row["when"]), float(row["size"]) / 1024.0 / 1024.0, esc(row["path"]))
        )
    if not report_html:
        report_html.append("<tr><td>-</td><td>-</td><td class='mono'>NO_REPLAY_REPORTS_FOUND_IN_BOUNDED_SCAN</td></tr>")

    synthetic_html = []
    for row, detail in synthetic_rows:
        synthetic_html.append(
            "<tr><td class='mono'>%s</td><td class='mono'>%s</td><td class='mono'>%s</td></tr>"
            % (esc(row["when"]), esc(row["path"]), esc(detail[:500]))
        )
    if not synthetic_html:
        synthetic_html.append(
            "<tr><td>-</td><td class='mono'>R35C-R5D artifact not found in bounded latest scan</td>"
            "<td class='mono'>Synthetic Shadow PnL panel is ready; values appear when proof/report files are present.</td></tr>"
        )

    form = (
        "<form method='get' action='/' class='mono'>"
        "<table>"
        "<tr><td>Date from</td><td><input name='date_from' value='%s' placeholder='YYYY-MM-DD'></td>"
        "<td>Date to</td><td><input name='date_to' value='%s' placeholder='YYYY-MM-DD'></td></tr>"
        "<tr><td>Date mode</td><td>%s</td><td>Strategy</td><td>%s</td></tr>"
        "<tr><td>Side</td><td>%s</td><td>Report type</td><td>%s</td></tr>"
        "<tr><td>Dataset source</td><td>%s</td><td>Action</td><td><button type='submit'>Apply display filter</button></td></tr>"
        "</table></form>"
        % (
            esc(date_from),
            esc(date_to),
            _r4b_select("date_mode", REPLAY_DATE_MODES, date_mode),
            _r4b_select("strategy", REPLAY_STRATEGIES, strategy),
            _r4b_select("side", REPLAY_SIDES, side),
            _r4b_select("report_type", REPLAY_REPORT_TYPES, report_type),
            _r4b_select("dataset_source", REPLAY_DATASET_SOURCES, dataset_source),
        )
    )

    selected_table = (
        "<table>"
        "<tr><td>Mode</td><td class='mono'>R4B_UI_ONLY_SKELETON</td></tr>"
        "<tr><td>Selected filter</td><td class='mono'>date_from=%s date_to=%s date_mode=%s strategy=%s side=%s report_type=%s dataset_source=%s</td></tr>"
        "<tr><td>Safety</td><td class='mono'>READ_ONLY_FILES_ONLY | NO_REPLAY_EXECUTION | NO_SHELL_COMMAND | NO_LIVE_STATE_MUTATION</td></tr>"
        "<tr><td>UI caps</td><td class='mono'>runs=%s files=%s rows=%s</td></tr>"
        "<tr><td>Source hierarchy</td><td class='mono'>proof/report JSON/MD → 10_run_summary.json → engine_result.json → capped summaries → raw datasets only by later explicit action</td></tr>"
        "<tr><td>MIV-R label</td><td class='mono'>MIV-R = research/audit probe only, not production strategy, not paper/live candidate source</td></tr>"
        "</table>"
        % (
            esc(date_from), esc(date_to), esc(date_mode), esc(strategy), esc(side), esc(report_type), esc(dataset_source),
            REPLAY_LATEST_RUN_LIMIT, REPLAY_LATEST_FILE_LIMIT, REPLAY_UI_ROW_CAP,
        )
    )

    return (
        "<div class='panel' id='replay-backtest'><h2>Replay / Backtest</h2>"
        "<p class='mono'>Historical what-would-have-happened view only. This section never changes the Live Truth Board or paper/live readiness.</p>"
        + form
        + "<h3>Selected Replay View</h3>" + selected_table
        + r4c_r3_minimal_replay_summary_panel(replay_runs, report_rows, synthetic_rows)  # R4C_R3_PANEL_CALL_ANCHOR
        + r4d_small_readonly_tables_panel(replay_runs, report_rows, synthetic_rows)  # R4D_SMALL_TABLES_PANEL_CALL_ANCHOR
        + r4e_exact_r35c_r5d_synthetic_pnl_panel()  # R4E_EXACT_R35C_R5D_PROOF_PANEL_CALL_ANCHOR
        + r4f_export_paths_only_panel(replay_runs, report_rows, synthetic_rows)  # R4F_EXPORT_PATHS_PANEL_CALL_ANCHOR
        + "<h3>Synthetic Shadow PnL</h3>"
        + "<p class='mono'>Replay-only synthetic shadow model. not broker PnL, not paper PnL, not live PnL. PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_NOT_BROKER_NOT_PAPER_NOT_LIVE. Keep separate from Official closed-trade PnL, Broker/Paper/Live PnL, and Live Truth Board.</p>"
        + "<table><tr><th>Time</th><th>Artifact</th><th>Summary</th></tr>" + "".join(synthetic_html) + "</table>"
        + "<h3>Latest Replay Runs</h3>"
        + "<table><tr><th>Modified</th><th>Run path</th><th>Summary artifacts</th></tr>" + "".join(run_html) + "</table>"
        + "<h3>Latest Existing Replay / PnL / Candidate Reports</h3>"
        + "<table><tr><th>Modified</th><th>Size</th><th>Path</th></tr>" + "".join(report_html) + "</table>"
        + "<h3>R4B Output Tables Planned</h3>"
        + "<p class='mono'>strategy_candidate_summary | trade_candidate_table | near_candidate_table | shadow_fill_table | pnl_summary | strategy_wise_pnl | day_wise_pnl | blocker_summary | failed_stage_summary | score_distribution | latest_exports</p>"
        + "</div>"
    )

def build_html(params=None) -> str:
    params = params or {}
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
    lane_x_truth_board_html = lane_x_truth_board()
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
    replay_backtest_html = replay_backtest_panel(params)
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="2">
<title>MME-ScalpX OPS Dashboard R3H-LX-R3E</title>
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
<div><h1>MME-ScalpX OPS Dashboard R3H-LX-R3E</h1><div class="sub">R3H-LX-R3E read-only · HOLD reason capped · action distribution · capture progress · paper blocked · no writes · no orders</div></div>
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

{lane_x_truth_board_html}
{replay_backtest_html}
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
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query, keep_blank_values=True)
        if path in ("/", "/index.html"):
            body = build_html(params).encode("utf-8")
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


# LANE_X_DASH_R3B_DYNAMIC_TRUTH_BOARD
def lane_x_truth_board() -> str:
    def xlen(k):
        try:
            return int(redis_client().xlen(k))
        except Exception:
            return -1

    def latest_age_sec(k):
        try:
            rows = redis_client().xrevrange(k, count=1)
            if not rows:
                return None
            sid = rows[0][0]
            if isinstance(sid, bytes):
                sid = sid.decode()
            ms = int(str(sid).split("-", 1)[0])
            now_ms = int(time.time() * 1000)
            return max(0, round((now_ms - ms) / 1000, 1))
        except Exception:
            return None

    def status_by_age(age):
        if age is None:
            return "DEAD"
        if age <= 20:
            return "LIVE"
        if age <= 120:
            return "STALE"
        return "DEAD"

    orders = xlen("orders:mme:stream")
    risk_stream = xlen("risk:mme:stream")
    execution_stream = xlen("execution:mme:stream")
    risk_proc = proc_count("risk")
    execution_proc = proc_count("execution")
    safety_clean = orders == 0 and risk_stream == 0 and execution_stream == 0 and risk_proc == 0 and execution_proc == 0
    safety_state = "PASS" if safety_clean else "FAIL"
    safety_msg = "SAFETY CLEAN — OBSERVE ONLY" if safety_clean else "SAFETY NOT CLEAN — DO NOT START PAPER/LIVE"

    streams = [
        ("fut", "ticks:mme:fut:zerodha:stream"),
        ("opt", "ticks:mme:opt:selected:zerodha:stream"),
        ("features", "features:mme:stream"),
        ("decisions", "decisions:mme:stream"),
        ("errors", "system:errors:stream"),
    ]
    stream_rows = []
    for name, key in streams:
        ln = xlen(key)
        age = latest_age_sec(key)
        st = status_by_age(age)
        if name == "errors" and ln > 0:
            st = "REVIEW_ERRORS"
        stream_rows.append((name, ln, "-" if age is None else age, st))

    latest_action = latest_reason = latest_family = latest_side = latest_failed = latest_blocker = "-"
    candidate_count = "-"
    try:
        rows = redis_client().xrevrange("decisions:mme:stream", count=1)
        if rows:
            payload = _decision_payload(rows[0][1]) or {}
            latest_action = _infer_action(payload)
            latest_reason = _pick_first(payload, ["reason", "hold_reason", "blocker"], "-")
            latest_family = _pick_first(payload, ["family", "strategy_family"], "-")
            latest_side = _pick_first(payload, ["side", "direction"], "-")
            latest_failed = _pick_first(payload, ["failed_stage", "stage"], "-")
            latest_blocker = _pick_first(payload, ["blocker", "reason", "hold_reason"], "-")
            candidate_count = _pick_first(payload, ["candidate_count", "candidates_count"], "-")
    except Exception as exc:
        latest_reason = "decision_parse_error=" + str(exc)

    text = ""
    try:
        files = list((project_root() / "run" / "audits").glob("*shadow_near_candidate_output.txt"))
        f = max(files, key=lambda x: x.stat().st_mtime) if files else None
        text = f.read_text(errors="replace") if f else ""
    except Exception:
        text = ""
    table = text.split("{", 1)[0].strip()
    lines = [x for x in table.splitlines() if x.strip()]
    mist_put = next((x for x in lines if x.startswith("MIST | PUT")), "MIST | PUT | not present")
    miso = "\n".join([x for x in lines if x.startswith("MISO |")]) or "MISO not present"

    # LANE_X_DASH_R3E_FRESH_ERROR_ONLY_NEXT_ACTION
    errors_len = xlen("system:errors:stream")
    latest_error_age = latest_age_sec("system:errors:stream")
    fresh_error = latest_error_age is not None and latest_error_age <= 180
    next_action = "OBSERVE_ONLY_CONTINUE"
    if not safety_clean:
        next_action = "DO_NOT_START_PAPER_LIVE"
    elif fresh_error:
        next_action = "REVIEW_ERRORS"
    elif "provider_not_ready" in mist_put:
        next_action = "FIX_PROVIDER_NOT_READY_OR_WAIT_FOR_LIVE_VALIDATION"
    elif "runtime_disabled" in miso:
        next_action = "MISO_BLOCKED_DOCTRINE_CORRECT"
    elif latest_reason in ("view_data_invalid", "data_invalid"):
        next_action = "FIX_VIEW_DATA_INVALID"

    flow_html = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td class='mono'>%s</td></tr>" % (esc(a), esc(b), esc(c), esc(d)) for a,b,c,d in stream_rows)

    return (
        "<h2>Lane X Dynamic Truth Board</h2>"
        "<div class='grid'>"
        "<div class='panel'><h3>1. SAFETY</h3><table><tr><td>state</td><td class='mono'>%s</td></tr><tr><td>message</td><td class='mono'>%s</td></tr><tr><td>orders/risk/execution</td><td class='mono'>%s/%s/%s</td></tr><tr><td>risk_proc/execution_proc</td><td class='mono'>%s/%s</td></tr></table></div>"
        "<div class='panel'><h3>2. LIVE DATA FLOW</h3><table><tr><th>stream</th><th>len</th><th>age sec</th><th>status</th></tr>%s</table></div>"
        "<div class='panel'><h3>3. STRATEGY STATE</h3><table><tr><td>action</td><td class='mono'>%s</td></tr><tr><td>reason</td><td class='mono'>%s</td></tr><tr><td>family/side</td><td class='mono'>%s/%s</td></tr><tr><td>failed_stage</td><td class='mono'>%s</td></tr><tr><td>blocker</td><td class='mono'>%s</td></tr><tr><td>candidate_count</td><td class='mono'>%s</td></tr></table></div>"
        "<div class='panel'><h3>4. LANE X FOCUS — MIST PUT</h3><pre class='mono'>%s</pre><p class='mono'>diagnostic only; never production candidate</p></div>"
        "<div class='panel'><h3>5. NEXT ACTION</h3><h2 class='mono'>%s</h2><p>Dashboard is read-only. It must not promote paper/live.</p></div>"
        "<div class='panel'><h3>MISO Doctrine</h3><pre class='mono'>%s</pre><p>Do not hide MISO. Do not weaken MISO.</p></div>"
        "</div>"
    ) % (
        esc(safety_state), esc(safety_msg), esc(orders), esc(risk_stream), esc(execution_stream), esc(risk_proc), esc(execution_proc),
        flow_html,
        esc(latest_action), esc(latest_reason), esc(latest_family), esc(latest_side), esc(latest_failed), esc(latest_blocker), esc(candidate_count),
        esc(mist_put),
        esc(next_action),
        esc(miso),
    )

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
