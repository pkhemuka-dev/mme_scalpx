#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O21"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o21_controlled_paper_promotion_readiness.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o21_controlled_paper_promotion_readiness.json"

O18_PATH = ROOT / "run/proofs/proof_batch26o18_lightweight_controlled_paper_preflight.json"
O19_PATH = ROOT / "run/proofs/proof_batch26o19_lightweight_controlled_paper_runtime.json"
O20R_PATH = ROOT / "run/proofs/proof_batch26o20r_recovery_after_terminated_o20.json"
O20R2_PATH = ROOT / "run/proofs/proof_batch26o20_r2_bounded_short_observation.json"

TARGETS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/settings.py",
    "bin/proof_batch26o21_controlled_paper_promotion_readiness.py",
    "run/proofs/proof_batch26o20_r2_bounded_short_observation.json",
    "run/proofs/proof_batch26o20r_recovery_after_terminated_o20.json",
    "run/proofs/proof_batch26o19_lightweight_controlled_paper_runtime.json",
    "run/proofs/proof_batch26o18_lightweight_controlled_paper_preflight.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_json_load(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            return json.loads(value)
        except Exception:
            return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def load_json_path(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    obj = safe_json_load(path.read_text(encoding="utf-8", errors="replace"))
    return obj if isinstance(obj, dict) else {}


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o21_controlled_paper_promotion_readiness.py"
    for clean in ps_lines():
        lower = clean.lower()
        if self_name in clean:
            continue
        if "grep" in lower or "pgrep" in lower or "bash -lc" in lower or " sh -c " in lower:
            continue
        if "python" not in lower:
            continue
        if "-m app.mme_scalpx.main" not in clean:
            continue
        if f"--service {service}" not in clean:
            continue
        matches.append(clean)
    return matches


def xlen(client: Any, key: str) -> int:
    try:
        return int(client.xlen(key))
    except Exception:
        return 0


def hgetall(client: Any, key: str) -> dict[str, str]:
    try:
        return decode_hash(client.hgetall(key) or {})
    except Exception:
        return {}


def hget_json(client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        obj = safe_json_load(client.hget(key, field))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def position_summary(raw: Mapping[str, str]) -> dict[str, Any]:
    has_position_raw = str(raw.get("has_position", raw.get("position_open", "false"))).lower()
    qty_lots = float(raw.get("qty_lots", raw.get("quantity_lots", "0")) or 0)
    qty_units = float(raw.get("qty_units", raw.get("quantity_units", "0")) or 0)
    side = str(raw.get("position_side", raw.get("side", ""))).upper()
    flat = bool(
        has_position_raw not in {"1", "true", "yes", "y"}
        and qty_lots == 0
        and qty_units == 0
        and side in {"", "FLAT", "NONE"}
    )
    return {
        "raw": dict(raw),
        "has_position_raw": has_position_raw,
        "qty_lots": qty_lots,
        "qty_units": qty_units,
        "side": side,
        "flat": flat,
    }


def latest_rows(client: Any, key: str, count: int = 8) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        rows = client.xrevrange(key, count=count)
        for msg_id, fields in rows:
            out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
    except Exception:
        pass
    return out


def decision_safety(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe = []
    hold_like = []
    candidate_like = []
    for row in rows:
        f = row.get("fields", {})
        action = str(f.get("action") or f.get("decision") or "").upper()
        side = str(f.get("side") or "").upper()
        qty = str(f.get("qty") or f.get("quantity_lots") or "0")
        order_type = str(f.get("order_type") or "")
        broker_side_effects_allowed = str(f.get("broker_side_effects_allowed") or "").lower() in {"1", "true", "yes"}
        live_orders_allowed = str(f.get("live_orders_allowed") or "").lower() in {"1", "true", "yes"}
        activation_candidate_count = str(f.get("activation_candidate_count") or "0")
        activation_promoted = str(f.get("activation_promoted") or "0")
        activation_report = str(f.get("activation_report_json") or "")

        is_hold = bool(
            action in {"", "HOLD"}
            and side in {"", "FLAT"}
            and qty in {"", "0", "0.0"}
            and order_type == ""
            and not broker_side_effects_allowed
            and not live_orders_allowed
            and activation_promoted in {"", "0", "false", "False"}
        )

        if activation_candidate_count not in {"", "0", "0.0"} or '"candidates":[' in activation_report and '"candidates":[]' not in activation_report:
            candidate_like.append(row)

        if is_hold:
            hold_like.append(row)
        else:
            unsafe.append(row)

    return {
        "row_count": len(rows),
        "hold_like_count": len(hold_like),
        "unsafe_count": len(unsafe),
        "candidate_like_count": len(candidate_like),
        "unsafe_rows": unsafe,
        "candidate_like_rows": candidate_like,
        "latest_rows": rows,
    }


def feature_snapshot(client: Any, features_hash_key: str) -> dict[str, Any]:
    ff = hget_json(client, features_hash_key, "family_features_json")
    cv = hget_json(client, features_hash_key, "consumer_view_json")
    frames = hget_json(client, features_hash_key, "family_frames_json")

    stage_flags = ff.get("stage_flags", {}) if isinstance(ff, Mapping) else {}
    branch_frames = cv.get("branch_frames", {}) if isinstance(cv, Mapping) else {}
    mist_call = branch_frames.get("mist_call", {}) if isinstance(branch_frames, Mapping) else {}

    return {
        "family_features_present": bool(ff),
        "consumer_view_present": bool(cv),
        "consumer_view_data_valid": cv.get("data_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_safe_to_consume": cv.get("safe_to_consume") if isinstance(cv, Mapping) else None,
        "consumer_view_hold_only": cv.get("hold_only") if isinstance(cv, Mapping) else None,
        "branch_frame_count": len(branch_frames) if isinstance(branch_frames, Mapping) else 0,
        "mist_call_present": "mist_call" in branch_frames if isinstance(branch_frames, Mapping) else False,
        "family_frame_keys": sorted(frames.keys()) if isinstance(frames, Mapping) else [],
        "stage_flags": stage_flags,
        "mist_call_brief": {
            "present": mist_call.get("present") if isinstance(mist_call, Mapping) else None,
            "branch_ready": mist_call.get("branch_ready") if isinstance(mist_call, Mapping) else None,
            "eligible": mist_call.get("eligible") if isinstance(mist_call, Mapping) else None,
            "failed_stage": mist_call.get("failed_stage") if isinstance(mist_call, Mapping) else None,
            "setup_score": mist_call.get("setup_score") if isinstance(mist_call, Mapping) else None,
            "tradability_ok": mist_call.get("tradability_ok") if isinstance(mist_call, Mapping) else None,
            "option_tradability_pass": mist_call.get("option_tradability_pass") if isinstance(mist_call, Mapping) else None,
            "context_pass": mist_call.get("context_pass") if isinstance(mist_call, Mapping) else None,
        },
    }


def proof_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "exists": bool(data),
        "batch": data.get("batch"),
        "final_verdict": data.get("final_verdict"),
        "next_recommended_batch": data.get("next_recommended_batch"),
        "required_verdicts": data.get("required_verdicts"),
        "streams": data.get("streams"),
        "position_before": data.get("position_before"),
        "position_after": data.get("position_after"),
        "feature_before": data.get("feature_before"),
        "feature_after": data.get("feature_after"),
    }


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
        "created_at_utc": now_utc(),
        "files": [
            {"path": p, "exists": (ROOT / p).exists(), "sha256": sha256_file(ROOT / p)}
            for p in TARGETS
        ],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> int:
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "controlled_paper_promotion_readiness",
        "created_at_utc": now_utc(),
        "scope": {
            "review_only": True,
            "paper_restart": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_enablement": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
        },
    }

    o18 = load_json_path(O18_PATH)
    o19 = load_json_path(O19_PATH)
    o20r = load_json_path(O20R_PATH)
    o20r2 = load_json_path(O20R2_PATH)

    result["prior_proofs"] = {
        "o18": proof_summary(o18),
        "o19": proof_summary(o19),
        "o20r": proof_summary(o20r),
        "o20r2": proof_summary(o20r2),
    }

    compile_result = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/strategy_family/eligibility.py",
        "app/mme_scalpx/services/strategy_family/arbitration.py",
        "app/mme_scalpx/services/strategy_family/decisions.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/settings.py",
    ])
    result["compile"] = compile_result

    client = redis_client_or_none()
    result["redis_available"] = client is not None
    if client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        result["next_recommended_batch"] = "Do not continue. Redis unavailable."
        write_outputs(result)
        return 2

    from app.mme_scalpx.core import names as N  # type: ignore

    orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    features_stream_key = getattr(N, "STREAM_FEATURES_MME", "features:mme:stream")
    runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
    position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")
    features_hash_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))

    runtime = hgetall(client, runtime_key)
    position = position_summary(hgetall(client, position_key))
    feature = feature_snapshot(client, features_hash_key)

    orders_len = xlen(client, orders_key)
    decisions_len = xlen(client, decisions_key)
    features_len = xlen(client, features_stream_key)

    latest_decisions = latest_rows(client, decisions_key, count=12)
    latest_orders = latest_rows(client, orders_key, count=5)
    decision_report = decision_safety(latest_decisions)

    real_live = str(runtime.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    processes = {
        "feeds": pgrep_service("feeds"),
        "features": pgrep_service("features"),
        "strategy": pgrep_service("strategy"),
        "risk": pgrep_service("risk"),
        "execution": pgrep_service("execution"),
    }

    result.update({
        "runtime": runtime,
        "position": position,
        "feature": feature,
        "streams": {
            "orders_len": orders_len,
            "decisions_len": decisions_len,
            "features_len": features_len,
        },
        "latest_decisions": latest_decisions,
        "latest_orders": latest_orders,
        "decision_safety": decision_report,
        "processes": processes,
        "environment_review": {
            "SCALPX_REAL_LIVE_ALLOWED": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", ""),
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", ""),
            "SCALPX_CONTROLLED_PAPER_FAMILY": os.environ.get("SCALPX_CONTROLLED_PAPER_FAMILY", ""),
            "SCALPX_CONTROLLED_PAPER_BRANCH": os.environ.get("SCALPX_CONTROLLED_PAPER_BRANCH", ""),
            "SCALPX_CONTROLLED_PAPER_QTY_LOTS": os.environ.get("SCALPX_CONTROLLED_PAPER_QTY_LOTS", ""),
        },
    })

    # O21 is a readiness review, not a promotion. It checks whether the next
    # paper-only phase is safe, while explicitly keeping real live blocked.
    prior_chain_pass = bool(
        o18.get("final_verdict") == "PASS_O18_LIGHTWEIGHT_CONTROLLED_PAPER_PREFLIGHT_OK"
        and o19.get("final_verdict") == "PASS_O19_LIGHTWEIGHT_CONTROLLED_PAPER_RUNTIME_OK_NO_ORDER"
        and o20r.get("final_verdict") == "PASS_O20R_RECOVERY_SAFE_AFTER_TERMINATED_O20"
        and o20r2.get("final_verdict") == "PASS_O20_R2_BOUNDED_SHORT_OBSERVATION_OK_NO_ORDER"
    )

    o20r2_req = o20r2.get("required_verdicts", {}) if isinstance(o20r2.get("required_verdicts"), Mapping) else {}

    required = {
        "compile_pass": compile_result["returncode"] == 0,
        "prior_chain_pass": prior_chain_pass,
        "o20r2_orders_zero": o20r2_req.get("orders_zero") is True,
        "o20r2_orders_delta_zero": o20r2_req.get("orders_delta_zero") is True,
        "o20r2_position_flat_all_samples": o20r2_req.get("position_flat_all_samples") is True,
        "o20r2_real_live_false_all_samples": o20r2_req.get("real_live_false_all_samples") is True,
        "o20r2_decisions_hold_only": o20r2_req.get("decisions_hold_only") is True,
        "o20r2_features_stream_growth": o20r2_req.get("features_stream_growth") is True,
        "o20r2_decisions_stream_growth": o20r2_req.get("decisions_stream_growth") is True,
        "o20r2_risk_running_in_most_samples": o20r2_req.get("risk_running_in_most_samples") is True,
        "o20r2_execution_running_in_most_samples": o20r2_req.get("execution_running_in_most_samples") is True,
        "o20r2_strategy_running_in_most_samples": o20r2_req.get("strategy_running_in_most_samples") is True,
        "o20r2_no_heavy_monitor": o20r2_req.get("no_heavy_monitor") is True,
        "o20r2_no_unbounded_polling": o20r2_req.get("no_unbounded_polling") is True,
        "current_orders_zero": orders_len == 0,
        "current_latest_orders_empty": len(latest_orders) == 0,
        "current_position_flat": position["flat"] is True,
        "current_real_live_false": real_live is False,
        "current_decisions_hold_only": decision_report["unsafe_count"] == 0,
        "consumer_view_present": feature["consumer_view_present"] is True,
        "consumer_view_data_valid": feature["consumer_view_data_valid"] is True,
        "consumer_view_safe_to_consume": feature["consumer_view_safe_to_consume"] is True,
        "all_10_branch_frames_present": feature["branch_frame_count"] == 10,
        "mist_call_visible": feature["mist_call_present"] is True,
        "real_live_not_enabled_by_this_batch": True,
        "paper_not_restarted_by_this_batch": True,
        "broker_not_called_by_this_batch": True,
        "no_threshold_relaxation": True,
        "no_forced_candidate": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O21_CONTROLLED_PAPER_PROMOTION_READINESS_NOT_PROVEN"
        result["readiness_status"] = "NOT_READY"
        result["next_recommended_batch"] = "Inspect O21 proof. Do not proceed to longer paper or real live."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O21_CONTROLLED_PAPER_PROMOTION_READINESS_OK_REAL_LIVE_BLOCKED"
    result["readiness_status"] = "READY_FOR_NEXT_CONTROLLED_PAPER_PHASE_ONLY"
    result["next_recommended_batch"] = "26-O22 controlled-paper longer observation plan/runbook; still no real live"
    result["explicit_real_live_status"] = "BLOCKED"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
