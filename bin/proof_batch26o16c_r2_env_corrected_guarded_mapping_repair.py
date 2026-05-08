#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PROOF_PATH = ROOT / "run/proofs/proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16c_r2_env_corrected_guarded_mapping_repair.json"
O16B_PATH = ROOT / "run/proofs/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
BACKUP_DIR = ROOT / "run/_code_backups" / f"batch26o16c_r2_env_corrected_guarded_mapping_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.py",
    "run/proofs/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.json",
    "run/proofs/proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.json",
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


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout, env={**os.environ, "PYTHONPATH": str(ROOT)})
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
    self_name = "proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.py"
    for line in out.splitlines():
        clean = " ".join(line.split())
        lower = clean.lower()
        if not clean or self_name in clean:
            continue
        if "pgrep" in lower or "grep" in lower or "bash -lc" in lower or " sh -c " in lower:
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


def build_redis_adapter(redis_client: Any):
    class RedisAdapter:
        def __init__(self, inner):
            self.inner = inner
        def hgetall(self, key):
            return self.inner.hgetall(key)
        def hset(self, key, mapping=None, **kwargs):
            if mapping is not None:
                enc = {}
                for k, v in mapping.items():
                    enc[k] = v if isinstance(v, str) else str(v)
                return self.inner.hset(key, mapping=enc)
            return self.inner.hset(key, **kwargs)
        def xadd(self, *args, **kwargs):
            return self.inner.xadd(*args, **kwargs)
        def xlen(self, *args, **kwargs):
            return self.inner.xlen(*args, **kwargs)
        def xrevrange(self, *args, **kwargs):
            return self.inner.xrevrange(*args, **kwargs)
    return RedisAdapter(redis_client)


def summarize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    family_features = payload.get("family_features", {})
    family_surfaces = payload.get("family_surfaces", {})
    family_frames = payload.get("family_frames", {})
    consumer_view = payload.get("consumer_view", {})

    if not isinstance(family_features, Mapping):
        family_features = {}
    if not isinstance(family_surfaces, Mapping):
        family_surfaces = {}
    if not isinstance(family_frames, Mapping):
        family_frames = {}
    if not isinstance(consumer_view, Mapping):
        consumer_view = {}

    stage_flags = family_features.get("stage_flags", {})
    if not isinstance(stage_flags, Mapping):
        stage_flags = {}

    return {
        "frame_id": payload.get("frame_id"),
        "frame_ts_ns": payload.get("frame_ts_ns"),
        "frame_valid": bool(payload.get("frame_valid")),
        "warmup_complete": bool(payload.get("warmup_complete")),
        "family_features_present": bool(family_features),
        "family_surfaces_present": bool(family_surfaces),
        "family_frames_present": bool(family_frames),
        "consumer_view_present": bool(consumer_view),
        "family_frame_keys": sorted(str(k) for k in family_frames.keys()),
        "stage_flags": dict(stage_flags),
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
        },
    }


def run_feature_once(features_mod: Any, redis_client: Any) -> Mapping[str, Any]:
    svc = features_mod.FeatureService(
        redis_client=build_redis_adapter(redis_client),
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("Shutdown", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o16c-r2",
    )
    payload = svc.run_once()
    return payload if isinstance(payload, Mapping) else {}


def patch_features_run_once_bridge(before_text: str) -> dict[str, Any]:
    marker = "Batch 26-O16C-R2 active FeatureService.run_once consumer_view bridge"
    if marker in before_text:
        return {
            "patched": False,
            "already_present": True,
            "reason": "O16C-R2 marker already present",
        }

    required = [
        "_batch26o16_normalize_family_frames",
        "_batch26o16_build_consumer_view",
        "class FeatureService",
        "def run_once",
        "HASH_FEATURES",
    ]
    missing = [x for x in required if x not in before_text]
    if missing:
        return {
            "patched": False,
            "already_present": False,
            "reason": "required markers missing",
            "missing": missing,
        }

    backup = BACKUP_DIR / "features.py.pre_o16c_r2"
    shutil.copy2(TARGET_FEATURES, backup)

    patch = r'''

# =============================================================================
# Batch 26-O16C-R2 active FeatureService.run_once consumer_view bridge
# =============================================================================
#
# Safety:
# - Does not force data_valid.
# - Does not mark futures/option/provider readiness true.
# - Does not evaluate doctrine leaves.
# - Does not write orders.
# - Does not start risk/execution.
# - Only publishes consumer_view_json when the active run_once path already
#   produced family_features, family_surfaces, and family_frames.

if "_BATCH26O16C_R2_ORIGINAL_FEATURESERVICE_RUN_ONCE" not in globals():
    _BATCH26O16C_R2_ORIGINAL_FEATURESERVICE_RUN_ONCE = FeatureService.run_once

    def _batch26o16c_r2_run_once(self: FeatureService, *args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = dict(_BATCH26O16C_R2_ORIGINAL_FEATURESERVICE_RUN_ONCE(self, *args, **kwargs))

        family_features = dict(payload.get("family_features", {}) or {})
        family_surfaces = dict(payload.get("family_surfaces", {}) or {})
        if not family_features or not family_surfaces:
            return payload

        generated_at_ns = _safe_int(
            payload.get("frame_ts_ns"),
            _safe_int(payload.get("generated_at_ns"), time.time_ns()),
        )
        provider_runtime = _mapping(payload.get("provider_runtime") or family_features.get("provider_runtime"))

        family_frames = _batch26o16_normalize_family_frames(
            generated_at_ns=generated_at_ns,
            provider_runtime=provider_runtime,
            family_surfaces=family_surfaces,
            family_frames=dict(payload.get("family_frames") or {}),
        )

        consumer_view = _batch26o16_build_consumer_view(
            payload=payload,
            family_features=family_features,
            family_surfaces=family_surfaces,
            family_frames=family_frames,
        )

        payload["family_frames"] = family_frames
        payload["consumer_view"] = consumer_view

        selected = _nested(family_features, "common", "selected_option", default={})
        feature_state = {
            "frame_id": payload.get("frame_id"),
            "frame_ts_ns": payload.get("frame_ts_ns"),
            "frame_valid": bool(payload.get("frame_valid")),
            "warmup_complete": bool(payload.get("warmup_complete")),
            "regime": _nested(family_features, "common", "regime", default=REGIME_NORMAL),
            "selected_option": selected,
        }

        hash_payload = {
            "frame_id": _safe_str(payload.get("frame_id")),
            "frame_ts_ns": _safe_str(payload.get("frame_ts_ns")),
            "ts_event_ns": _safe_str(payload.get("ts_event_ns")),
            "frame_valid": int(bool(payload.get("frame_valid"))),
            "warmup_complete": int(bool(payload.get("warmup_complete"))),
            "system_state": getattr(N, "STATE_SCANNING", "SCANNING")
            if payload.get("frame_valid")
            else getattr(N, "STATE_DISABLED", "DISABLED"),
            "strategy_mode": getattr(N, "STRATEGY_AUTO", "AUTO"),
            "family_features_version": _safe_str(family_features.get("family_features_version")),
            "family_features_json": _json_dump(family_features),
            "family_surfaces_json": _json_dump(family_surfaces),
            "family_frames_json": _json_dump(family_frames),
            "consumer_view_json": _json_dump(consumer_view),
            "feature_state_json": _json_dump(feature_state),
            "payload_json": _json_dump(payload),
        }

        try:
            self.redis.hset(HASH_FEATURES, mapping=hash_payload)
        except Exception:
            pass

        return payload

    FeatureService.run_once = _batch26o16c_r2_run_once
'''
    TARGET_FEATURES.write_text(before_text.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {
        "patched": True,
        "already_present": False,
        "backup": str(backup),
        "reason": "active run_once path had family payload but lacked consumer_view publication",
    }


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": "26-O16C-R2",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": [
            {
                "path": p,
                "exists": (ROOT / p).exists(),
                "sha256": sha256_file(ROOT / p),
            }
            for p in TARGETS
        ],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()

    result: dict[str, Any] = {
        "batch": "26-O16C-R2",
        "batch_name": "env_corrected_guarded_mapping_repair",
        "created_at_utc": now,
        "scope": {
            "guarded": True,
            "paper_restart": False,
            "risk_started": False,
            "execution_started": False,
            "order_write_intended": False,
            "real_live_approval": False,
            "forced_data_valid": False,
            "threshold_relaxation": False,
            "miso_enablement": False,
        },
    }

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None
    if redis_client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    o16b = safe_json_load(O16B_PATH.read_text(encoding="utf-8")) if O16B_PATH.exists() else {}
    o16b_final = o16b.get("final_verdict") if isinstance(o16b, Mapping) else None
    o16b_source = o16b.get("likely_source_family") if isinstance(o16b, Mapping) else None

    result["o16b_gate"] = {
        "exists": O16B_PATH.exists(),
        "final_verdict": o16b_final,
        "likely_source_family": o16b_source,
    }

    if o16b_final != "PASS_O16B_RUNTIME_FRAME_VALID_ROOT_CAUSE_AUDIT_OK":
        result["final_verdict"] = "FAIL_CLOSED_O16B_NOT_PASS"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    if o16b_source != "FEATURE_INPUT_SNAPSHOT_OR_REDIS_KEY_MAPPING_GAP":
        result["final_verdict"] = "FAIL_CLOSED_O16B_SOURCE_NOT_EXACT_FEATURE_INPUT_MAPPING_GAP"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    compile_before = run_cmd([
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
    ])
    result["compile_before"] = compile_before

    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
    except Exception as exc:
        result["final_verdict"] = "FAIL_IMPORT_CONTEXT_NOT_READY"
        result["import_error"] = f"{type(exc).__name__}: {exc}"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    orders_key = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
    runtime_key = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")
    features_key = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))

    orders_before = int(redis_client.xlen(orders_key))
    runtime_hash = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_before = str(runtime_hash.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    payload_before = run_feature_once(features, redis_client)
    before_summary = summarize_payload(payload_before)
    result["before_summary"] = before_summary

    before_hash = decode_hash(redis_client.hgetall(features_key) or {})
    before_consumer_view = safe_json_load(before_hash.get("consumer_view_json"))

    result["before_hash_summary"] = {
        "features_key": features_key,
        "hash_present": bool(before_hash),
        "hash_fields": sorted(before_hash.keys()),
        "consumer_view_json_present": bool(before_consumer_view),
    }

    exact_gap = {
        "family_features_present": before_summary["family_features_present"],
        "family_surfaces_present": before_summary["family_surfaces_present"],
        "family_frames_present": before_summary["family_frames_present"],
        "consumer_view_present": before_summary["consumer_view_present"] or bool(before_consumer_view),
        "frame_valid_before": before_summary["frame_valid"],
    }
    result["exact_gap"] = exact_gap

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    patch_result = {"patched": False, "reason": "not attempted"}

    if (
        exact_gap["family_features_present"]
        and exact_gap["family_surfaces_present"]
        and exact_gap["family_frames_present"]
        and not exact_gap["consumer_view_present"]
    ):
        patch_result = patch_features_run_once_bridge(before_text)
    else:
        patch_result = {
            "patched": False,
            "reason": "exact consumer_view publication gap not present or not safely patchable",
        }

    result["patch_result"] = patch_result
    result["patch_performed"] = bool(patch_result.get("patched"))

    compile_after = run_cmd([
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
    ])
    result["compile_after"] = compile_after

    # Fresh subprocess post-check to ensure appended bridge is active.
    post_script = ROOT / "run/proofs/_tmp_batch26o16c_r2_post_check.py"
    post_script.write_text(r'''
import json
import pathlib
import sys
import time

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import redis
from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import features

def dec(raw):
    return {
        (k.decode() if isinstance(k, bytes) else str(k)):
        (v.decode() if isinstance(v, bytes) else str(v))
        for k, v in dict(raw or {}).items()
    }

class R:
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

client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
client.ping()

svc = features.FeatureService(
    redis_client=R(client),
    clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
    shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
    instance_id="batch26o16c-r2-post",
)
payload = svc.run_once()

features_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))
raw = dec(client.hgetall(features_key) or {})
cv = json.loads(raw.get("consumer_view_json") or "{}")
ff = json.loads(raw.get("family_features_json") or "{}")
frames = json.loads(raw.get("family_frames_json") or "{}")

out = {
    "payload_has_consumer_view": bool(isinstance(payload, dict) and payload.get("consumer_view")),
    "payload_frame_valid": bool(isinstance(payload, dict) and payload.get("frame_valid")),
    "hash_consumer_view_present": bool(cv),
    "hash_consumer_view_data_valid": cv.get("data_valid"),
    "hash_consumer_view_safe_to_consume": cv.get("safe_to_consume"),
    "hash_branch_frame_count": len(cv.get("branch_frames", {}) or {}),
    "hash_mist_call_present": "mist_call" in (cv.get("branch_frames", {}) or {}),
    "hash_family_features_present": bool(ff),
    "hash_family_frames_present": bool(frames),
    "hash_family_frame_keys": sorted(frames.keys()) if isinstance(frames, dict) else [],
}
print(json.dumps(out, indent=2, sort_keys=True))
''', encoding="utf-8")

    post = run_cmd([sys.executable, str(post_script)])
    result["post_check"] = post
    try:
        post_parsed = json.loads(post.get("stdout") or "{}")
    except Exception:
        post_parsed = {}
    result["post_check_parsed"] = post_parsed

    orders_after = int(redis_client.xlen(orders_key))
    runtime_hash_after = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_after = str(runtime_hash_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    safety = {
        "orders_before": orders_before,
        "orders_after": orders_after,
        "orders_zero": orders_after == 0,
        "real_live_before": real_live_before,
        "real_live_after": real_live_after,
        "risk_process_lines": pgrep_python_service("risk"),
        "execution_process_lines": pgrep_python_service("execution"),
    }
    result["safety"] = safety

    required = {
        "redis_available": True,
        "o16b_gate_pass": o16b_final == "PASS_O16B_RUNTIME_FRAME_VALID_ROOT_CAUSE_AUDIT_OK",
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "patch_performed_or_already_present": bool(patch_result.get("patched") or patch_result.get("already_present")),
        "consumer_view_present_after": bool(post_parsed.get("hash_consumer_view_present")),
        "all_10_branch_frames_after": len(post_parsed.get("hash_family_frame_keys", [])) == 10,
        "mist_call_present_after": bool(post_parsed.get("hash_mist_call_present")),
        "family_features_preserved": bool(post_parsed.get("hash_family_features_present")),
        "orders_zero": orders_after == 0,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "data_valid_not_forced": post_parsed.get("payload_frame_valid") == before_summary.get("frame_valid"),
    }
    result["required_verdicts"] = required

    if (
        required["compile_before_pass"]
        and required["compile_after_pass"]
        and required["patch_performed_or_already_present"]
        and required["consumer_view_present_after"]
        and required["all_10_branch_frames_after"]
        and required["mist_call_present_after"]
        and required["family_features_preserved"]
        and required["orders_zero"]
        and required["risk_not_running"]
        and required["execution_not_running"]
        and required["real_live_false"]
        and required["data_valid_not_forced"]
    ):
        if post_parsed.get("hash_consumer_view_data_valid") is True and post_parsed.get("hash_consumer_view_safe_to_consume") is True:
            result["final_verdict"] = "PASS_O16C_R2_CONSUMER_VIEW_AND_RUNTIME_DATA_VALID_OK"
            result["next_recommended_batch"] = "26-O17 activation candidate extraction proof, no risk/execution"
        else:
            result["final_verdict"] = "PASS_O16C_R2_CONSUMER_VIEW_REPAIRED_RUNTIME_DATA_VALID_STILL_FAIL_CLOSED"
            result["next_recommended_batch"] = "26-O16D marketdata/provider readiness mapping repair, no strategy/risk/execution"
        write_outputs(result)
        return 0

    result["final_verdict"] = "FAIL_O16C_R2_REPAIR_NOT_PROVEN"
    result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to O17 or paper."
    write_outputs(result)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
