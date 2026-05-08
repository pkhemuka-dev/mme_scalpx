#!/usr/bin/env python3
from __future__ import annotations

import ast
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
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16b_runtime_feature_frame_valid_root_cause_audit.json"

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "etc/brokers/runtime.yaml",
    "etc/brokers/provider_roles.yaml",
    "etc/brokers/dhan.yaml",
    "etc/brokers/zerodha.yaml",
    "run/proofs/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.json",
    "run/proofs/proof_batch26o16_consumer_view_mapping_repair.json",
    "run/proofs/proof_batch26o15_activation_candidate_surface_audit.json",
    "bin/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.py",
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


def run_cmd(args: list[str], *, timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def pgrep_python_service(service: str) -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
    except Exception:
        return []

    matches: list[str] = []
    self_name = "proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.py"
    for line in out.splitlines():
        clean = " ".join(line.split())
        if not clean:
            continue
        lower = clean.lower()
        if self_name in clean:
            continue
        if "pgrep" in lower or "grep" in lower:
            continue
        if "bash -lc" in lower or " sh -c " in lower:
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

        client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "127.0.0.1"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            db=int(os.environ.get("REDIS_DB", "0")),
            decode_responses=False,
        )
        client.ping()
        return client
    except Exception:
        return None


def grep_context(path: pathlib.Path, patterns: list[str], radius: int = 5) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    out: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        if any(re.search(p, line) for p in patterns):
            out.append({
                "lineno": idx,
                "line": line,
                "context": "\n".join(lines[max(0, idx - radius - 1): min(len(lines), idx + radius)]),
            })
    return out


def ast_function_inventory(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(text)
    out: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.append({
                "kind": type(node).__name__,
                "name": node.name,
                "lineno": getattr(node, "lineno", None),
                "end_lineno": getattr(node, "end_lineno", None),
            })
    return sorted(out, key=lambda x: (x.get("lineno") or 0, x["name"]))


def summarize_json_mapping(m: Any, max_keys: int = 80) -> dict[str, Any]:
    if not isinstance(m, Mapping):
        return {
            "present": False,
            "type": type(m).__name__,
        }
    keys = sorted(str(k) for k in m.keys())
    return {
        "present": bool(m),
        "type": type(m).__name__,
        "key_count": len(keys),
        "keys": keys[:max_keys],
    }


def stream_summary(redis_client: Any, key: str) -> dict[str, Any]:
    try:
        length = int(redis_client.xlen(key))
        latest = []
        if length > 0:
            rows = redis_client.xrevrange(key, count=1)
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
        return {
            "key": key,
            "error": f"{type(exc).__name__}: {exc}",
        }


def hash_summary(redis_client: Any, key: str) -> dict[str, Any]:
    try:
        raw = decode_hash(redis_client.hgetall(key) or {})
        parsed = {}
        for field in [
            "family_features_json",
            "family_surfaces_json",
            "family_frames_json",
            "consumer_view_json",
            "payload_json",
            "feature_state_json",
            "provider_runtime_json",
            "feed_snapshot_json",
            "snapshot_json",
        ]:
            if field in raw:
                parsed[field] = safe_json_load(raw.get(field))
        return {
            "key": key,
            "exists": bool(raw),
            "field_count": len(raw),
            "fields": sorted(raw.keys()),
            "raw_selected": {
                k: raw.get(k)
                for k in sorted(raw.keys())
                if k in {
                    "frame_id",
                    "frame_ts_ns",
                    "ts_event_ns",
                    "frame_valid",
                    "warmup_complete",
                    "system_state",
                    "strategy_mode",
                    "service",
                    "status",
                    "runtime_mode",
                    "active_futures_provider_id",
                    "active_selected_option_provider_id",
                    "active_option_context_provider_id",
                    "real_live_approved",
                }
            },
            "parsed_summaries": {
                k: summarize_json_mapping(v)
                for k, v in parsed.items()
            },
            "parsed": parsed,
        }
    except Exception as exc:
        return {
            "key": key,
            "error": f"{type(exc).__name__}: {exc}",
        }


def summarize_feature_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    family_features = payload.get("family_features", {})
    family_surfaces = payload.get("family_surfaces", {})
    family_frames = payload.get("family_frames", {})
    provider_runtime = payload.get("provider_runtime", {})
    shared_core = payload.get("shared_core", {})
    explain = payload.get("explain", {})

    if not isinstance(family_features, Mapping):
        family_features = {}
    if not isinstance(family_surfaces, Mapping):
        family_surfaces = {}
    if not isinstance(family_frames, Mapping):
        family_frames = {}
    if not isinstance(provider_runtime, Mapping):
        provider_runtime = {}
    if not isinstance(shared_core, Mapping):
        shared_core = {}
    if not isinstance(explain, Mapping):
        explain = {}

    stage_flags = family_features.get("stage_flags", {})
    if not isinstance(stage_flags, Mapping):
        stage_flags = {}

    common = family_features.get("common", {})
    if not isinstance(common, Mapping):
        common = {}

    market = family_features.get("market", {})
    if not isinstance(market, Mapping):
        market = {}

    snapshot = family_features.get("snapshot", {})
    if not isinstance(snapshot, Mapping):
        snapshot = {}

    return {
        "frame_id": payload.get("frame_id"),
        "frame_ts_ns": payload.get("frame_ts_ns"),
        "frame_valid": bool(payload.get("frame_valid")),
        "warmup_complete": bool(payload.get("warmup_complete")),
        "top_level_keys": sorted(str(k) for k in payload.keys()),
        "explain_summary": summarize_json_mapping(explain),
        "provider_runtime_summary": summarize_json_mapping(provider_runtime),
        "provider_runtime": dict(provider_runtime),
        "shared_core_summary": summarize_json_mapping(shared_core),
        "family_features_summary": summarize_json_mapping(family_features),
        "family_surfaces_summary": summarize_json_mapping(family_surfaces),
        "family_frames_summary": summarize_json_mapping(family_frames),
        "family_frame_keys": sorted(str(k) for k in family_frames.keys()),
        "stage_flags": dict(stage_flags),
        "snapshot": dict(snapshot),
        "common_summary": summarize_json_mapping(common),
        "market_summary": summarize_json_mapping(market),
        "selected_option": common.get("selected_option"),
        "futures_ltp": market.get("futures_ltp"),
        "root_cause_flags": {
            "data_valid": stage_flags.get("data_valid"),
            "data_quality_ok": stage_flags.get("data_quality_ok"),
            "futures_present": stage_flags.get("futures_present"),
            "selected_option_present": stage_flags.get("selected_option_present"),
            "call_present": stage_flags.get("call_present"),
            "put_present": stage_flags.get("put_present"),
            "provider_ready_classic": stage_flags.get("provider_ready_classic"),
            "provider_ready_miso": stage_flags.get("provider_ready_miso"),
            "dhan_context_fresh": stage_flags.get("dhan_context_fresh"),
            "session_eligible": stage_flags.get("session_eligible"),
            "warmup_complete": stage_flags.get("warmup_complete"),
            "risk_veto_active": stage_flags.get("risk_veto_active"),
            "reconciliation_lock_active": stage_flags.get("reconciliation_lock_active"),
            "active_position_present": stage_flags.get("active_position_present"),
        },
    }


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    sys.path.insert(0, str(ROOT))

    compile_result = run_cmd([
        sys.executable,
        "-m",
        "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/feeds.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/integrations/bootstrap_provider.py",
        "app/mme_scalpx/integrations/provider_runtime.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "bin/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.py",
    ])

    imports: dict[str, Any] = {}
    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
        feeds = importlib.import_module("app.mme_scalpx.services.feeds")
        provider_runtime_mod = importlib.import_module("app.mme_scalpx.integrations.provider_runtime")
        imports = {
            "names": True,
            "features": True,
            "feeds": True,
            "provider_runtime": True,
            "features_file": getattr(features, "__file__", None),
            "feeds_file": getattr(feeds, "__file__", None),
            "provider_runtime_file": getattr(provider_runtime_mod, "__file__", None),
        }
    except Exception as exc:
        names = None
        features = None
        imports = {
            "error": f"{type(exc).__name__}: {exc}",
        }

    source_audit = {
        "features": {
            "sha256": sha256_file(ROOT / "app/mme_scalpx/services/features.py"),
            "function_inventory": ast_function_inventory(ROOT / "app/mme_scalpx/services/features.py"),
            "frame_valid_contexts": grep_context(
                ROOT / "app/mme_scalpx/services/features.py",
                [
                    r"frame_valid",
                    r"data_valid",
                    r"data_quality_ok",
                    r"futures_present",
                    r"selected_option_present",
                    r"call_present",
                    r"put_present",
                    r"provider_ready_classic",
                    r"provider_ready_miso",
                    r"HASH_",
                    r"STREAM_",
                    r"xrevrange",
                    r"hgetall",
                    r"build_payload",
                    r"run_once",
                ],
            ),
        },
        "feeds": {
            "sha256": sha256_file(ROOT / "app/mme_scalpx/services/feeds.py"),
            "function_inventory": ast_function_inventory(ROOT / "app/mme_scalpx/services/feeds.py"),
            "producer_contexts": grep_context(
                ROOT / "app/mme_scalpx/services/feeds.py",
                [
                    r"HASH_",
                    r"STREAM_",
                    r"xadd",
                    r"hset",
                    r"futures",
                    r"selected",
                    r"option",
                    r"snapshot",
                    r"provider",
                    r"zerodha",
                    r"dhan",
                ],
            ),
        },
        "names": {
            "sha256": sha256_file(ROOT / "app/mme_scalpx/core/names.py"),
            "redis_name_contexts": grep_context(
                ROOT / "app/mme_scalpx/core/names.py",
                [
                    r"HASH_",
                    r"STREAM_",
                    r"ticks:mme",
                    r"state:",
                    r"health:",
                    r"orders:",
                ],
            ),
        },
        "provider_runtime": {
            "sha256": sha256_file(ROOT / "app/mme_scalpx/integrations/provider_runtime.py"),
            "contexts": grep_context(
                ROOT / "app/mme_scalpx/integrations/provider_runtime.py",
                [
                    r"active_futures",
                    r"active_selected",
                    r"option_context",
                    r"provider_ready",
                    r"ZERODHA",
                    r"DHAN",
                    r"fallback",
                    r"runtime",
                ],
            ),
        },
    }

    redis_client = redis_client_or_none()
    redis_audit: dict[str, Any] = {
        "redis_available": redis_client is not None,
    }

    feature_payload_summary: dict[str, Any] = {}
    feature_hash_summary_now: dict[str, Any] = {}
    stream_hash_key_audit: dict[str, Any] = {}
    order_len = None
    real_live_approved = False

    if redis_client is not None and names is not None:
        candidate_hash_attrs = [
            "HASH_STATE_FEATURES_MME_FUT",
            "HASH_FEATURES",
            "HASH_STATE_RUNTIME",
            "HASH_PROVIDER_RUNTIME",
            "HASH_STATE_PROVIDER_RUNTIME",
            "HASH_STATE_FEED_SNAPSHOT",
            "HASH_FEED_SNAPSHOT",
            "HASH_STATE_DHAN_CONTEXT",
            "HASH_STATE_ZERODHA_CONTEXT",
            "HASH_HEALTH_FEEDS",
            "KEY_HEALTH_FEEDS",
            "HASH_STATE_POSITION_MME",
        ]
        candidate_stream_attrs = [
            "STREAM_FEATURES_MME",
            "STREAM_ORDERS_MME",
            "STREAM_TICKS_MME_FUT",
            "STREAM_TICKS_MME_OPT",
            "STREAM_TICKS_MME_FUT_ZERODHA",
            "STREAM_TICKS_MME_FUT_DHAN",
            "STREAM_TICKS_MME_OPT_SELECTED_ZERODHA",
            "STREAM_TICKS_MME_OPT_SELECTED_DHAN",
            "STREAM_FEED_SNAPSHOT",
        ]

        resolved_hash_keys = {}
        for attr in candidate_hash_attrs:
            if hasattr(names, attr):
                resolved_hash_keys[attr] = getattr(names, attr)

        resolved_stream_keys = {}
        for attr in candidate_stream_attrs:
            if hasattr(names, attr):
                resolved_stream_keys[attr] = getattr(names, attr)

        # Also include known observed runtime keys, without requiring names.py constants.
        known_hash_keys = {
            "OBSERVED_state_features_mme_fut": "state:features:mme:fut",
            "OBSERVED_state_runtime": "state:runtime",
            "OBSERVED_health_feeds": "health:feeds",
            "OBSERVED_state_provider_runtime": "state:provider_runtime",
            "OBSERVED_state_feed_snapshot": "state:feed_snapshot",
            "OBSERVED_state_dhan_context": "state:dhan_context",
            "OBSERVED_state_position_mme": "state:position:mme",
        }

        known_stream_keys = {
            "OBSERVED_ticks_fut_generic": "ticks:mme:fut:stream",
            "OBSERVED_ticks_opt_generic": "ticks:mme:opt:stream",
            "OBSERVED_ticks_fut_zerodha": "ticks:mme:fut:zerodha:stream",
            "OBSERVED_ticks_fut_dhan": "ticks:mme:fut:dhan:stream",
            "OBSERVED_ticks_opt_selected_zerodha": "ticks:mme:opt:selected:zerodha:stream",
            "OBSERVED_ticks_opt_selected_dhan": "ticks:mme:opt:selected:dhan:stream",
            "OBSERVED_orders": "orders:mme:stream",
            "OBSERVED_features": "features:mme:stream",
        }

        all_hash_keys = {**known_hash_keys, **resolved_hash_keys}
        all_stream_keys = {**known_stream_keys, **resolved_stream_keys}

        stream_hash_key_audit = {
            "resolved_hash_keys": resolved_hash_keys,
            "resolved_stream_keys": resolved_stream_keys,
            "hashes": {
                label: hash_summary(redis_client, key)
                for label, key in sorted(all_hash_keys.items())
            },
            "streams": {
                label: stream_summary(redis_client, key)
                for label, key in sorted(all_stream_keys.items())
            },
        }

        try:
            orders_key = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
            order_len = int(redis_client.xlen(orders_key))
        except Exception:
            order_len = None

        try:
            rt = decode_hash(redis_client.hgetall(getattr(names, "HASH_STATE_RUNTIME", "state:runtime")) or {})
            real_live_approved = str(rt.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}
        except Exception:
            real_live_approved = False

        if features is not None:
            try:
                class RedisAdapter:
                    def __init__(self, inner):
                        self.inner = inner
                    def hgetall(self, key):
                        return self.inner.hgetall(key)
                    def hset(self, key, mapping=None, **kwargs):
                        if mapping is not None:
                            enc = {}
                            for k, v in mapping.items():
                                if isinstance(v, bytes):
                                    enc[k] = v
                                elif isinstance(v, str):
                                    enc[k] = v
                                else:
                                    enc[k] = str(v)
                            return self.inner.hset(key, mapping=enc)
                        return self.inner.hset(key, **kwargs)
                    def xadd(self, *args, **kwargs):
                        return self.inner.xadd(*args, **kwargs)

                svc = features.FeatureService(
                    redis_client=RedisAdapter(redis_client),
                    clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
                    shutdown=type("Shutdown", (), {"is_set": staticmethod(lambda: True)})(),
                    instance_id="batch26o16b-diagnostic",
                )
                payload = svc.run_once()
                feature_payload_summary = summarize_feature_payload(payload if isinstance(payload, Mapping) else {})
            except Exception as exc:
                feature_payload_summary = {
                    "run_once_error": f"{type(exc).__name__}: {exc}",
                }

        try:
            feature_key = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))
            feature_hash_summary_now = hash_summary(redis_client, feature_key)
        except Exception as exc:
            feature_hash_summary_now = {
                "error": f"{type(exc).__name__}: {exc}",
            }

    risk_process_lines = pgrep_python_service("risk")
    execution_process_lines = pgrep_python_service("execution")

    o16a = {}
    o16a_path = ROOT / "run/proofs/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.json"
    if o16a_path.exists():
        o16a = safe_json_load(o16a_path.read_text(encoding="utf-8"))

    root_flags = feature_payload_summary.get("root_cause_flags", {}) if isinstance(feature_payload_summary, Mapping) else {}
    if not isinstance(root_flags, Mapping):
        root_flags = {}

    root_cause_classification = {
        "runtime_frame_valid": feature_payload_summary.get("frame_valid") if isinstance(feature_payload_summary, Mapping) else None,
        "flags": dict(root_flags),
        "blocking_false_flags": sorted(
            k for k, v in root_flags.items()
            if k in {
                "data_valid",
                "data_quality_ok",
                "futures_present",
                "selected_option_present",
                "call_present",
                "put_present",
                "provider_ready_classic",
            }
            and v is False
        ),
        "miso_expected_blocked": root_flags.get("provider_ready_miso") is False,
        "dhan_context_fresh": root_flags.get("dhan_context_fresh"),
        "warmup_complete": root_flags.get("warmup_complete"),
        "session_eligible": root_flags.get("session_eligible"),
    }

    # Plan classification: no patch. Identify likely source family.
    blocking = set(root_cause_classification["blocking_false_flags"])
    if {"futures_present", "selected_option_present", "call_present", "put_present", "provider_ready_classic"} & blocking:
        likely_source = "FEATURE_INPUT_SNAPSHOT_OR_REDIS_KEY_MAPPING_GAP"
    elif "data_quality_ok" in blocking:
        likely_source = "DATA_QUALITY_OR_FRESHNESS_GATE_GAP"
    elif "data_valid" in blocking:
        likely_source = "COMPOSED_DATA_VALID_GATE_GAP"
    else:
        likely_source = "NO_RUNTIME_BLOCKER_OBSERVED_OR_NOT_CLASSIFIED"

    required_verdicts = {
        "production_patch_performed": False,
        "compile_pass": compile_result.get("returncode") == 0,
        "o16a_pass_confirmed": o16a.get("final_verdict") == "PASS_O16A_PROOF_CORRECTED_RUNTIME_DATA_VALID_SOURCE_BLOCKER_CONFIRMED",
        "redis_available": redis_client is not None,
        "runtime_feature_payload_observed": bool(feature_payload_summary),
        "runtime_frame_valid_false_confirmed": feature_payload_summary.get("frame_valid") is False if isinstance(feature_payload_summary, Mapping) else False,
        "root_cause_flags_present": bool(root_flags),
        "blocking_false_flags_identified": bool(root_cause_classification["blocking_false_flags"]),
        "futures_present_false_identified": root_flags.get("futures_present") is False,
        "selected_option_present_false_identified": root_flags.get("selected_option_present") is False,
        "call_present_false_identified": root_flags.get("call_present") is False,
        "put_present_false_identified": root_flags.get("put_present") is False,
        "data_quality_ok_false_identified": root_flags.get("data_quality_ok") is False,
        "provider_ready_classic_false_identified": root_flags.get("provider_ready_classic") is False,
        "miso_remains_blocked": root_flags.get("provider_ready_miso") is False,
        "risk_not_running": len(risk_process_lines) == 0,
        "execution_not_running": len(execution_process_lines) == 0,
        "orders_zero": order_len == 0,
        "real_live_approved_false": real_live_approved is False,
        "source_contexts_collected": bool(source_audit["features"]["frame_valid_contexts"]) and bool(source_audit["feeds"]["producer_contexts"]),
        "redis_key_audit_collected": bool(stream_hash_key_audit),
    }

    final_pass = (
        required_verdicts["compile_pass"]
        and required_verdicts["o16a_pass_confirmed"]
        and required_verdicts["redis_available"]
        and required_verdicts["runtime_feature_payload_observed"]
        and required_verdicts["runtime_frame_valid_false_confirmed"]
        and required_verdicts["root_cause_flags_present"]
        and required_verdicts["blocking_false_flags_identified"]
        and required_verdicts["risk_not_running"]
        and required_verdicts["execution_not_running"]
        and required_verdicts["orders_zero"]
        and required_verdicts["real_live_approved_false"]
        and required_verdicts["source_contexts_collected"]
        and required_verdicts["redis_key_audit_collected"]
    )

    result = {
        "batch": "26-O16B",
        "batch_name": "runtime_feature_frame_valid_root_cause_audit",
        "created_at_utc": now,
        "scope": {
            "production_patch_performed": False,
            "audit_only": True,
            "plan_only": True,
            "paper_restart": False,
            "risk_started": False,
            "execution_started": False,
            "order_write_intended": False,
            "real_live_approval": False,
            "forced_data_valid": False,
            "threshold_relaxation": False,
            "miso_enablement": False,
        },
        "compile": compile_result,
        "imports": imports,
        "o16a_summary": {
            "path": str(o16a_path),
            "exists": o16a_path.exists(),
            "final_verdict": o16a.get("final_verdict") if isinstance(o16a, Mapping) else None,
            "classification": o16a.get("classification") if isinstance(o16a, Mapping) else None,
        },
        "runtime_feature_payload_summary": feature_payload_summary,
        "feature_hash_summary_now": feature_hash_summary_now,
        "root_cause_classification": root_cause_classification,
        "likely_source_family": likely_source,
        "redis_stream_hash_key_audit": stream_hash_key_audit,
        "source_audit": source_audit,
        "safety": {
            "risk_process_lines": risk_process_lines,
            "execution_process_lines": execution_process_lines,
            "orders_len": order_len,
            "real_live_approved": real_live_approved,
        },
        "required_verdicts": required_verdicts,
        "repair_plan_next_batch": {
            "batch": "26-O16C",
            "name": "exact feature input snapshot mapping repair",
            "allowed_scope": [
                "patch only the proven producer/consumer key mapping if O16B identifies exact mismatch",
                "preserve O16 consumer_view mapping",
                "preserve Dhan/MISO fail-closed",
                "do not patch activation thresholds",
                "do not start risk/execution",
                "do not start paper",
            ],
            "must_not_do": [
                "do not force data_valid true",
                "do not mark futures/selected-option present unless Redis/source truth exists",
                "do not infer CE/PE presence from branch-frame placeholders",
                "do not enable MISO without Dhan selected-option/context readiness",
                "do not write orders",
                "do not approve real live",
            ],
            "primary_questions_to_answer": [
                "Which Redis hash/stream does features.py read for futures snapshot?",
                "Which Redis hash/stream does feeds.py publish for futures snapshot?",
                "Which Redis hash/stream does features.py read for selected option snapshot?",
                "Which Redis hash/stream does feeds.py publish for selected option snapshot?",
                "Are the keys mismatched, absent, stale, or structurally incompatible?",
                "Is provider_ready_classic false because provider_runtime is missing, stale, or mapped under different field names?",
            ],
        },
        "final_verdict": "PASS_O16B_RUNTIME_FRAME_VALID_ROOT_CAUSE_AUDIT_OK" if final_pass else "FAIL_O16B_RUNTIME_FRAME_VALID_ROOT_CAUSE_NOT_PROVEN",
    }

    manifest = {
        "batch": "26-O16B",
        "created_at_utc": now,
        "files": [
            {
                "path": p,
                "exists": (ROOT / p).exists(),
                "sha256": sha256_file(ROOT / p),
            }
            for p in TARGETS
        ],
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if final_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
