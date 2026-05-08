#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O16E"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16e_selected_option_feed_source_o8c_bridge.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16e_selected_option_feed_source_o8c_bridge.json"
O16D_PATH = ROOT / "run/proofs/proof_batch26o16d_selected_option_classic_provider_readiness.json"
CAPTURE_DIR = ROOT / "run/live_capture"
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/zerodha_feed_adapter.py",
    "app/mme_scalpx/integrations/dhan_marketdata.py",
    "app/mme_scalpx/integrations/runtime_instruments_factory.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o16e_selected_option_feed_source_o8c_bridge.py",
    "run/proofs/proof_batch26o16d_selected_option_classic_provider_readiness.json",
]


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


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def run_cmd(args: list[str], timeout: int = 60, env_extra: dict[str, str] | None = None) -> dict[str, Any]:
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout, env=env)
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def pgrep_service(service: str) -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
    except Exception:
        return []

    matches: list[str] = []
    self_name = "proof_batch26o16e_selected_option_feed_source_o8c_bridge.py"
    for line in out.splitlines():
        clean = " ".join(line.split())
        lower = clean.lower()
        if not clean or self_name in clean:
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


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def stream_summary(redis_client: Any, key: str, count: int = 3) -> dict[str, Any]:
    try:
        length = int(redis_client.xlen(key))
        latest = []
        if length > 0:
            rows = redis_client.xrevrange(key, count=count)
            for msg_id, fields in rows:
                latest.append({
                    "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                    "fields": decode_hash(fields),
                })
        return {
            "key": key,
            "exists": length > 0,
            "length": length,
            "latest": latest,
        }
    except Exception as exc:
        return {"key": key, "error": f"{type(exc).__name__}: {exc}"}


def hash_summary(redis_client: Any, key: str) -> dict[str, Any]:
    try:
        raw = decode_hash(redis_client.hgetall(key) or {})
        parsed = {}
        for f in [
            "payload_json",
            "feature_state_json",
            "family_features_json",
            "family_surfaces_json",
            "family_frames_json",
            "consumer_view_json",
            "snapshot_json",
            "feed_snapshot_json",
            "provider_runtime_json",
            "selected_option_json",
            "o16d_truth_json",
        ]:
            if f in raw:
                parsed[f] = safe_json_load(raw.get(f))
        return {
            "key": key,
            "exists": bool(raw),
            "field_count": len(raw),
            "fields": sorted(raw.keys()),
            "selected_raw": {
                k: raw.get(k)
                for k in sorted(raw.keys())
                if k in {
                    "frame_id",
                    "frame_ts_ns",
                    "frame_valid",
                    "warmup_complete",
                    "system_state",
                    "service",
                    "status",
                    "runtime_mode",
                    "active_futures_provider_id",
                    "active_selected_option_provider_id",
                    "active_option_context_provider_id",
                    "futures_present",
                    "selected_option_present",
                    "call_present",
                    "put_present",
                    "data_quality_ok",
                    "provider_ready_classic",
                    "provider",
                    "source",
                    "instrument_key",
                    "instrument_token",
                    "trading_symbol",
                    "option_symbol",
                    "option_token",
                    "side",
                    "option_side",
                    "role",
                    "ltp",
                    "best_bid",
                    "best_ask",
                    "stale",
                    "fresh",
                    "real_live_approved",
                }
            },
            "parsed": parsed,
        }
    except Exception as exc:
        return {"key": key, "error": f"{type(exc).__name__}: {exc}"}


def collect_surface(redis_client: Any, names: Any) -> dict[str, Any]:
    streams = {
        "features": getattr(names, "STREAM_FEATURES_MME", "features:mme:stream"),
        "orders": getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream"),
        "ticks_fut_zerodha": "ticks:mme:fut:zerodha:stream",
        "ticks_fut_dhan": "ticks:mme:fut:dhan:stream",
        "ticks_opt_selected_zerodha": "ticks:mme:opt:selected:zerodha:stream",
        "ticks_opt_selected_dhan": "ticks:mme:opt:selected:dhan:stream",
        "ticks_opt_context_dhan": "ticks:mme:opt:context:dhan:stream",
        "ticks_opt_generic": "ticks:mme:opt:stream",
        "ticks_fut_generic": "ticks:mme:fut:stream",
        "system_health": "system:health:stream",
        "system_errors": "system:errors:stream",
    }

    hashes = {
        "features": getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut")),
        "runtime": getattr(names, "HASH_STATE_RUNTIME", "state:runtime"),
        "position": getattr(names, "HASH_STATE_POSITION_MME", "state:position:mme"),
        "provider_runtime": "state:provider_runtime",
        "feed_snapshot": "state:feed_snapshot",
        "health_feeds": "health:feeds",
        "selected_option_mme": "state:selected_option:mme",
        "selected_option_zerodha": "state:opt:selected:zerodha",
        "selected_option_dhan": "state:opt:selected:dhan",
        "call_option": "state:opt:call",
        "put_option": "state:opt:put",
    }

    for attr in dir(names):
        if not attr.startswith(("STREAM_", "HASH_")):
            continue
        value = getattr(names, attr)
        if not isinstance(value, str):
            continue
        low = value.lower()
        if any(tok in low for tok in ["tick", "opt", "option", "provider", "feed", "health"]):
            if attr.startswith("STREAM_"):
                streams[f"name_attr_{attr}"] = value
            else:
                hashes[f"name_attr_{attr}"] = value

    return {
        "streams": {label: stream_summary(redis_client, key) for label, key in sorted(streams.items())},
        "hashes": {label: hash_summary(redis_client, key) for label, key in sorted(hashes.items())},
    }


def summarize_growth(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    growth: dict[str, Any] = {}
    b_streams = before.get("streams", {}) if isinstance(before, Mapping) else {}
    a_streams = after.get("streams", {}) if isinstance(after, Mapping) else {}
    for label, a in a_streams.items():
        b = b_streams.get(label, {}) if isinstance(b_streams, Mapping) else {}
        bl = b.get("length") if isinstance(b, Mapping) else None
        al = a.get("length") if isinstance(a, Mapping) else None
        if isinstance(bl, int) and isinstance(al, int):
            growth[label] = {
                "before": bl,
                "after": al,
                "delta": al - bl,
                "key": a.get("key"),
            }
    return growth


def evidence_counts(surface: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(surface, sort_keys=True, default=str).lower()
    selected_tokens = [
        "ticks:mme:opt:selected",
        "selected_option",
        "selected_option_present",
        "instrument_token",
        "instrument_key",
        "trading_symbol",
        "option_symbol",
        "option_token",
        "selected_call",
        "selected_put",
    ]
    provider_tokens = [
        "zerodha",
        "dhan",
        "active_selected_option_provider",
        "active_futures_provider",
        "provider_ready",
        "provider_runtime",
    ]
    ce_tokens = ['"ce"', "_ce", ":ce", " selected_call", '"call"', "option_side\":\"call"]
    pe_tokens = ['"pe"', "_pe", ":pe", " selected_put", '"put"', "option_side\":\"put"]

    return {
        "selected_option_mentions": sum(text.count(tok) for tok in selected_tokens),
        "provider_mentions": sum(text.count(tok) for tok in provider_tokens),
        "ce_mentions": sum(text.count(tok) for tok in ce_tokens),
        "pe_mentions": sum(text.count(tok) for tok in pe_tokens),
        "has_selected_option_evidence": any(tok in text for tok in selected_tokens),
        "has_provider_evidence": any(tok in text for tok in provider_tokens),
        "has_ce_evidence": any(tok in text for tok in ce_tokens),
        "has_pe_evidence": any(tok in text for tok in pe_tokens),
    }


def grep_context(path: pathlib.Path, patterns: list[str], radius: int = 4) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    out = []
    for idx, line in enumerate(lines, start=1):
        if any(re.search(p, line) for p in patterns):
            out.append({
                "lineno": idx,
                "line": line,
                "context": "\n".join(lines[max(0, idx - radius - 1): min(len(lines), idx + radius)]),
            })
    return out


def maybe_start_feeds() -> dict[str, Any]:
    existing = pgrep_service("feeds")
    if existing:
        return {
            "started": False,
            "already_running": True,
            "process_lines_before": existing,
            "pid": None,
            "log_path": None,
        }

    log_path = CAPTURE_DIR / f"o16e_feeds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    cmd = [
        sys.executable,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        "feeds",
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ]
    log_f = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        cmd,
        cwd=ROOT,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    pid_path = CAPTURE_DIR / "o16e_feeds.pid"
    pid_path.write_text(str(proc.pid), encoding="utf-8")
    time.sleep(10)
    after = pgrep_service("feeds")
    return {
        "started": True,
        "already_running": False,
        "pid": proc.pid,
        "pid_path": str(pid_path),
        "log_path": str(log_path),
        "process_lines_after": after,
        "cmd": cmd,
    }


def build_redis_adapter(redis_client: Any):
    class RedisAdapter:
        def __init__(self, inner):
            self.inner = inner
        def hgetall(self, key):
            return self.inner.hgetall(key)
        def hset(self, key, mapping=None, **kwargs):
            if mapping is not None:
                return self.inner.hset(key, mapping={k: (v if isinstance(v, str) else str(v)) for k, v in mapping.items()})
            return self.inner.hset(key, **kwargs)
        def xadd(self, *args, **kwargs):
            return self.inner.xadd(*args, **kwargs)
        def xlen(self, *args, **kwargs):
            return self.inner.xlen(*args, **kwargs)
        def xrevrange(self, *args, **kwargs):
            return self.inner.xrevrange(*args, **kwargs)
    return RedisAdapter(redis_client)


def run_feature_once(features_mod: Any, redis_client: Any) -> Mapping[str, Any]:
    svc = features_mod.FeatureService(
        redis_client=build_redis_adapter(redis_client),
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o16e",
    )
    payload = svc.run_once()
    return payload if isinstance(payload, Mapping) else {}


def summarize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    ff = payload.get("family_features", {})
    if not isinstance(ff, Mapping):
        ff = {}
    flags = ff.get("stage_flags", {})
    if not isinstance(flags, Mapping):
        flags = {}
    common = ff.get("common", {})
    if not isinstance(common, Mapping):
        common = {}
    market = ff.get("market", {})
    if not isinstance(market, Mapping):
        market = {}
    return {
        "frame_valid": bool(payload.get("frame_valid")),
        "warmup_complete": bool(payload.get("warmup_complete")),
        "frame_id": payload.get("frame_id"),
        "frame_ts_ns": payload.get("frame_ts_ns"),
        "family_features_present": bool(ff),
        "stage_flags": dict(flags),
        "selected_option": common.get("selected_option"),
        "futures_ltp": market.get("futures_ltp"),
        "root_cause_flags": {
            "data_valid": flags.get("data_valid"),
            "data_quality_ok": flags.get("data_quality_ok"),
            "futures_present": flags.get("futures_present"),
            "selected_option_present": flags.get("selected_option_present"),
            "call_present": flags.get("call_present"),
            "put_present": flags.get("put_present"),
            "provider_ready_classic": flags.get("provider_ready_classic"),
            "provider_ready_miso": flags.get("provider_ready_miso"),
            "dhan_context_fresh": flags.get("dhan_context_fresh"),
            "session_eligible": flags.get("session_eligible"),
            "warmup_complete": flags.get("warmup_complete"),
        },
    }


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": [
            {"path": p, "exists": (ROOT / p).exists(), "sha256": sha256_file(ROOT / p)}
            for p in TARGETS
        ],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "selected_option_feed_source_o8c_bridge",
        "created_at_utc": now,
        "scope": {
            "audit_only": True,
            "patch_performed": False,
            "paper_restart": False,
            "risk_started": False,
            "execution_started": False,
            "strategy_patch": False,
            "feature_patch": False,
            "order_write_intended": False,
            "real_live_approval": False,
            "forced_data_valid": False,
            "threshold_relaxation": False,
            "miso_enablement": False,
            "feeds_only_start_allowed": True,
        },
    }

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None
    if redis_client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    o16d = safe_json_load(O16D_PATH.read_text(encoding="utf-8")) if O16D_PATH.exists() else {}
    result["o16d_gate"] = {
        "exists": O16D_PATH.exists(),
        "final_verdict": o16d.get("final_verdict") if isinstance(o16d, Mapping) else None,
        "next_recommended_batch": o16d.get("next_recommended_batch") if isinstance(o16d, Mapping) else None,
    }

    if o16d.get("final_verdict") != "PASS_O16D_AUDIT_ONLY_SELECTED_OPTION_PROVIDER_EVIDENCE_NOT_SUFFICIENT_FOR_SAFE_PATCH":
        result["final_verdict"] = "FAIL_CLOSED_O16D_NOT_EXPECTED_AUDIT_ONLY_VERDICT"
        write_outputs(result)
        return 2

    compile_result = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/feeds.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/feature_family/tradability.py",
        "app/mme_scalpx/services/feature_family/mist_surface.py",
        "app/mme_scalpx/integrations/bootstrap_provider.py",
        "app/mme_scalpx/integrations/provider_runtime.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile"] = compile_result

    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
    except Exception as exc:
        result["final_verdict"] = "FAIL_IMPORT_CONTEXT_NOT_READY"
        result["import_error"] = f"{type(exc).__name__}: {exc}"
        write_outputs(result)
        return 2

    orders_key = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
    runtime_key = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")
    features_key = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))

    orders_before = int(redis_client.xlen(orders_key))
    rt_before = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_before = str(rt_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    before_surface = collect_surface(redis_client, names)
    before_counts = evidence_counts(before_surface)
    result["before_surface"] = before_surface
    result["before_evidence_counts"] = before_counts

    feeds_start = maybe_start_feeds()
    result["feeds_start"] = feeds_start

    # Capture short growth windows without starting strategy/risk/execution.
    time.sleep(8)
    mid_surface = collect_surface(redis_client, names)
    time.sleep(8)
    after_surface = collect_surface(redis_client, names)

    result["mid_surface"] = mid_surface
    result["after_surface"] = after_surface
    result["stream_growth_before_to_mid"] = summarize_growth(before_surface, mid_surface)
    result["stream_growth_mid_to_after"] = summarize_growth(mid_surface, after_surface)

    after_counts = evidence_counts(after_surface)
    result["after_evidence_counts"] = after_counts

    try:
        payload = run_feature_once(features, redis_client)
        result["feature_once_summary"] = summarize_payload(payload)
    except Exception as exc:
        result["feature_once_summary"] = {"error": f"{type(exc).__name__}: {exc}"}

    source_audit = {
        "feeds_o8c_bridge_contexts": grep_context(
            ROOT / "app/mme_scalpx/services/feeds.py",
            [
                r"O8C",
                r"selected",
                r"selected_option",
                r"ZERODHA",
                r"Dhan",
                r"ticks:mme:opt:selected",
                r"STREAM_",
                r"HASH_",
                r"xadd",
                r"hset",
            ],
        ),
        "features_selected_option_contexts": grep_context(
            ROOT / "app/mme_scalpx/services/features.py",
            [
                r"selected_option_present",
                r"call_present",
                r"put_present",
                r"provider_ready_classic",
                r"ticks:mme:opt:selected",
                r"selected_option",
                r"stage_flags",
            ],
        ),
        "names_option_contexts": grep_context(
            ROOT / "app/mme_scalpx/core/names.py",
            [
                r"selected",
                r"option",
                r"ticks:mme:opt",
                r"provider",
                r"HASH_",
                r"STREAM_",
            ],
        ),
    }
    result["source_audit"] = source_audit

    orders_after = int(redis_client.xlen(orders_key))
    rt_after = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_after = str(rt_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    safety = {
        "orders_before": orders_before,
        "orders_after": orders_after,
        "orders_zero": orders_after == 0,
        "real_live_before": real_live_before,
        "real_live_after": real_live_after,
        "risk_process_lines": pgrep_service("risk"),
        "execution_process_lines": pgrep_service("execution"),
        "strategy_process_lines": pgrep_service("strategy"),
        "feeds_process_lines": pgrep_service("feeds"),
    }
    result["safety"] = safety

    growth_mid_after = result["stream_growth_mid_to_after"]
    selected_stream_growth = {
        k: v for k, v in growth_mid_after.items()
        if "opt_selected" in k or "selected" in k or "opt" in k
    }

    feature_flags = result.get("feature_once_summary", {}).get("root_cause_flags", {})
    if not isinstance(feature_flags, Mapping):
        feature_flags = {}

    required = {
        "compile_pass": compile_result["returncode"] == 0,
        "redis_available": True,
        "o16d_gate_pass": result["o16d_gate"]["final_verdict"] == "PASS_O16D_AUDIT_ONLY_SELECTED_OPTION_PROVIDER_EVIDENCE_NOT_SUFFICIENT_FOR_SAFE_PATCH",
        "selected_option_evidence_seen": after_counts.get("has_selected_option_evidence") is True,
        "provider_evidence_seen": after_counts.get("has_provider_evidence") is True,
        "selected_option_stream_growth_or_existing": bool(selected_stream_growth) or before_counts.get("has_selected_option_evidence") is True,
        "features_run_once_observed": "error" not in result.get("feature_once_summary", {}),
        "orders_zero": orders_after == 0,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "strategy_not_started_by_batch": True,
        "feature_patch_performed": False,
        "forced_data_valid": False,
    }
    result["required_verdicts"] = required

    if not (
        required["compile_pass"]
        and required["redis_available"]
        and required["o16d_gate_pass"]
        and required["orders_zero"]
        and required["risk_not_running"]
        and required["execution_not_running"]
        and required["real_live_false"]
    ):
        result["final_verdict"] = "FAIL_O16E_SAFETY_OR_BASELINE_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to O17 or paper."
        write_outputs(result)
        return 2

    if (
        feature_flags.get("selected_option_present") is True
        and feature_flags.get("provider_ready_classic") is True
        and feature_flags.get("data_quality_ok") is True
        and feature_flags.get("data_valid") is True
    ):
        result["final_verdict"] = "PASS_O16E_SELECTED_OPTION_SOURCE_READY_DATA_VALID_OK"
        result["next_recommended_batch"] = "26-O17 activation candidate extraction proof, no risk/execution"
        write_outputs(result)
        return 0

    if required["selected_option_evidence_seen"] and required["provider_evidence_seen"]:
        result["final_verdict"] = "PASS_O16E_SOURCE_EVIDENCE_FOUND_MAPPING_REPAIR_NEEDED"
        result["next_recommended_batch"] = "26-O16F exact selected-option source-to-feature mapping repair, no strategy/risk/execution"
        write_outputs(result)
        return 0

    result["final_verdict"] = "PASS_O16E_SELECTED_OPTION_SOURCE_NOT_LIVE_OR_O8C_BRIDGE_NOT_PUBLISHING"
    result["next_recommended_batch"] = "26-O16F feeds/O8C selected-option bridge repair or market-session feed-start diagnosis, no strategy/risk/execution"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
