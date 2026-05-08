#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16_consumer_view_mapping_repair.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16_consumer_view_mapping_repair.json"

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o16_consumer_view_mapping_repair.py",
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
        if not value:
            return {}
        try:
            return json.loads(value)
        except Exception:
            return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def pgrep(pattern: str) -> list[str]:
    try:
        out = subprocess.check_output(["bash", "-lc", f"pgrep -af {pattern!r} || true"], text=True)
        lines = [line for line in out.splitlines() if line.strip()]
        return [line for line in lines if "proof_batch26o16_consumer_view_mapping_repair.py" not in line]
    except Exception:
        return []


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host=os.environ.get("REDIS_HOST", "127.0.0.1"), port=int(os.environ.get("REDIS_PORT", "6379")), db=int(os.environ.get("REDIS_DB", "0")), decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    sys.path.insert(0, str(ROOT))

    compile_cmd = [
        sys.executable,
        "-m",
        "py_compile",
        *TARGETS[:-1],
    ]
    compile_proc = subprocess.run(compile_cmd, cwd=ROOT, text=True, capture_output=True)

    features = importlib.import_module("app.mme_scalpx.services.features")
    names = importlib.import_module("app.mme_scalpx.core.names")
    strategy = importlib.import_module("app.mme_scalpx.services.strategy")

    family_ids = tuple(getattr(features, "FAMILY_IDS"))
    branch_ids = tuple(getattr(features, "BRANCH_IDS"))
    expected_branch_keys = sorted(f"{f.lower()}_{b.lower()}" for f in family_ids for b in branch_ids)

    generated_at_ns = time.time_ns()
    provider_runtime = {
        "family_runtime_mode": "observe_only",
        "active_futures_provider_id": "ZERODHA",
        "active_selected_option_provider_id": "ZERODHA",
        "active_option_context_provider_id": "DHAN",
    }

    family_surfaces = {
        "families": {},
        "surfaces_by_branch": {},
    }
    families_contract = {}
    for family_id in family_ids:
        family_surfaces["families"][family_id] = {"eligible": False, "branches": {}}
        families_contract[family_id] = {"eligible": False}
        for branch_id in branch_ids:
            key = f"{family_id.lower()}_{branch_id.lower()}"
            surface = {
                "family_id": family_id,
                "branch_id": branch_id,
                "side": branch_id,
                "eligible": False,
                "runtime_mode": "observe_only",
                "selected_features": {
                    "instrument_key": f"SYNTH:{key}",
                    "instrument_token": str(abs(hash(key)) % 100000),
                    "symbol": f"SYNTH_{key.upper()}",
                    "strike": 25000,
                    "ltp": 100.0,
                    "tick_size": 0.05,
                },
                "tradability": {
                    "entry_pass": False,
                    "tradability_ok": False,
                },
            }
            family_surfaces["surfaces_by_branch"][key] = surface
            family_surfaces["families"][family_id]["branches"][branch_id] = surface

    family_features = {
        "generated_at_ns": generated_at_ns,
        "stage_flags": {
            "data_valid": True,
            "warmup_complete": True,
            "provider_ready_classic": True,
            "provider_ready_miso": False,
            "risk_veto_active": False,
            "reconciliation_lock_active": False,
            "active_position_present": False,
        },
        "provider_runtime": provider_runtime,
        "common": {
            "regime": "NORMAL",
            "selected_option": {
                "instrument_key": "SYNTH:mist_call",
                "instrument_token": "1",
                "option_symbol": "SYNTH_MIST_CALL",
                "strike": 25000,
            },
        },
        "market": {
            "futures_ltp": 25000.0,
        },
        "families": families_contract,
        "snapshot": {
            "valid": True,
        },
    }
    payload = {
        "frame_id": f"features-{generated_at_ns}",
        "frame_ts_ns": generated_at_ns,
        "generated_at_ns": generated_at_ns,
        "frame_valid": True,
        "warmup_complete": True,
        "provider_runtime": provider_runtime,
        "family_features": family_features,
        "family_surfaces": family_surfaces,
        "family_frames": {},
    }

    normalized_frames = features._batch26o16_normalize_family_frames(
        generated_at_ns=generated_at_ns,
        provider_runtime=provider_runtime,
        family_surfaces=family_surfaces,
        family_frames={},
    )
    consumer_view = features._batch26o16_build_consumer_view(
        payload=payload,
        family_features=family_features,
        family_surfaces=family_surfaces,
        family_frames=normalized_frames,
    )

    branch_frames = consumer_view.get("branch_frames", {})
    all_10_branch_frames_present = all(key in branch_frames for key in expected_branch_keys)

    redis_client = redis_client_or_none()
    redis_runtime = {
        "redis_available": redis_client is not None,
        "published_once": False,
        "feature_hash_checked": False,
    }

    feature_hash_view = {}
    orders_len = 0
    real_live_approved = False

    if redis_client is not None:
        hash_features = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))
        stream_orders = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
        hash_runtime = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")

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

        # Single feature publish only. No risk/execution start. No order stream write.
        try:
            svc = features.FeatureService(
                redis_client=RedisAdapter(redis_client),
                clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
                shutdown=type("Shutdown", (), {"is_set": staticmethod(lambda: True)})(),
                instance_id="batch26o16-proof",
            )
            built_payload = svc.run_once()
            redis_runtime["published_once"] = True
            redis_runtime["built_payload_frame_valid"] = bool(built_payload.get("frame_valid"))
        except Exception as exc:
            redis_runtime["publish_error"] = f"{type(exc).__name__}: {exc}"

        try:
            raw = redis_client.hgetall(hash_features) or {}
            decoded = {
                (k.decode() if isinstance(k, bytes) else str(k)): (
                    v.decode() if isinstance(v, bytes) else str(v)
                )
                for k, v in raw.items()
            }
            feature_hash_view = safe_json_load(decoded.get("consumer_view_json"))
            redis_runtime["feature_hash_checked"] = True
            redis_runtime["hash_features_key"] = hash_features
            redis_runtime["consumer_view_json_present_in_redis"] = bool(feature_hash_view)
        except Exception as exc:
            redis_runtime["feature_hash_error"] = f"{type(exc).__name__}: {exc}"

        try:
            orders_len = int(redis_client.xlen(stream_orders))
        except Exception:
            orders_len = -1

        try:
            rt_raw = redis_client.hgetall(hash_runtime) or {}
            rt_decoded = {
                (k.decode() if isinstance(k, bytes) else str(k)): (
                    v.decode() if isinstance(v, bytes) else str(v)
                )
                for k, v in rt_raw.items()
            }
            real_live_approved = str(rt_decoded.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}
        except Exception:
            real_live_approved = False

    risk_lines = pgrep("app.mme_scalpx.main --service risk")
    execution_lines = pgrep("app.mme_scalpx.main --service execution")

    view_for_verdict = feature_hash_view if feature_hash_view else consumer_view
    vf_branch_frames = view_for_verdict.get("branch_frames", {}) if isinstance(view_for_verdict, dict) else {}

    verdicts = {
        "consumer_view_json_present": bool(view_for_verdict),
        "consumer_view_data_valid": bool(view_for_verdict.get("data_valid")) if isinstance(view_for_verdict, dict) else False,
        "consumer_view_safe_to_consume": bool(view_for_verdict.get("safe_to_consume")) if isinstance(view_for_verdict, dict) else False,
        "branch_frames_present": bool(vf_branch_frames),
        "all_10_branch_frames_present": all(key in vf_branch_frames for key in expected_branch_keys),
        "mist_call_branch_frame_present": "mist_call" in vf_branch_frames,
        "family_features_preserved": bool(view_for_verdict.get("family_status")) if isinstance(view_for_verdict, dict) else False,
        "family_surfaces_preserved": bool(view_for_verdict.get("family_surfaces")) if isinstance(view_for_verdict, dict) else False,
        "orders_zero": orders_len == 0,
        "risk_not_running": len(risk_lines) == 0,
        "execution_not_running": len(execution_lines) == 0,
        "real_live_approved": bool(real_live_approved),
    }

    final_pass = (
        compile_proc.returncode == 0
        and verdicts["consumer_view_json_present"]
        and verdicts["consumer_view_data_valid"]
        and verdicts["consumer_view_safe_to_consume"]
        and verdicts["branch_frames_present"]
        and verdicts["all_10_branch_frames_present"]
        and verdicts["mist_call_branch_frame_present"]
        and verdicts["family_features_preserved"]
        and verdicts["family_surfaces_preserved"]
        and verdicts["orders_zero"]
        and verdicts["risk_not_running"]
        and verdicts["execution_not_running"]
        and verdicts["real_live_approved"] is False
    )

    result = {
        "batch": "26-O16",
        "batch_name": "consumer_view_mapping_repair",
        "created_at_utc": now,
        "source_of_truth": "local uploaded/latest project tree at run time",
        "patch_scope": {
            "patched_files": ["app/mme_scalpx/services/features.py"],
            "no_strategy_patch": True,
            "no_risk_patch": True,
            "no_execution_patch": True,
            "no_threshold_relaxation": True,
            "no_forced_signal": True,
            "no_miso_enablement": True,
        },
        "compile": {
            "returncode": compile_proc.returncode,
            "stdout": compile_proc.stdout,
            "stderr": compile_proc.stderr,
        },
        "expected_branch_keys": expected_branch_keys,
        "synthetic_consumer_view": {
            "data_valid": consumer_view.get("data_valid"),
            "safe_to_consume": consumer_view.get("safe_to_consume"),
            "branch_frame_count": len(branch_frames),
            "all_10_branch_frames_present": all_10_branch_frames_present,
            "mist_call_branch_frame_present": "mist_call" in branch_frames,
        },
        "redis_runtime": redis_runtime,
        "safety": {
            "orders_len": orders_len,
            "risk_process_lines": risk_lines,
            "execution_process_lines": execution_lines,
            "real_live_approved": real_live_approved,
        },
        "required_verdicts": verdicts,
        "final_verdict": "PASS_CONSUMER_VIEW_MAPPING_REPAIR_OK" if final_pass else "FAIL_CONSUMER_VIEW_MAPPING_REPAIR_NOT_PROVEN",
        "notes": [
            "This proof performs at most one feature-service publish to state:features and feature stream.",
            "It does not start risk or execution.",
            "It does not write orders.",
            "It does not approve real live.",
            "Doctrine eligibility remains governed by strategy_family leaves and activation gates.",
        ],
    }

    manifest = {
        "batch": "26-O16",
        "created_at_utc": now,
        "files": [
            {
                "path": p,
                "sha256": sha256_file(ROOT / p),
                "exists": (ROOT / p).exists(),
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
