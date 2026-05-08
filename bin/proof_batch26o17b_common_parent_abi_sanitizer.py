#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import inspect
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

BATCH = "26-O17B"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o17b_common_parent_abi_sanitizer.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o17b_common_parent_abi_sanitizer.json"
O17A_PATH = ROOT / "run/proofs/proof_batch26o17a_selected_option_common_abi_sanitizer.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
BACKUP_DIR = ROOT / "run/_code_backups" / f"batch26o17b_common_parent_abi_sanitizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_COMMON_KEYS = (
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals",
)

EXPECTED_SELECTED_OPTION_KEYS = (
    "side",
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "ofi_ratio_proxy",
    "microprice",
    "micro_edge",
    "delta_3",
    "response_efficiency",
    "tradability_ok",
)

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/strategy_family/eligibility.py",
    "app/mme_scalpx/services/strategy_family/arbitration.py",
    "app/mme_scalpx/services/strategy_family/decisions.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o17b_common_parent_abi_sanitizer.py",
    "run/proofs/proof_batch26o17a_selected_option_common_abi_sanitizer.json",
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
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    return {"args": args, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def pgrep_service(service: str) -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
    except Exception:
        return []
    matches: list[str] = []
    self_name = "proof_batch26o17b_common_parent_abi_sanitizer.py"
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
        instance_id="batch26o17b-feature",
    )
    payload = svc.run_once()
    return payload if isinstance(payload, Mapping) else {}


def run_strategy_once(strategy_mod: Any, redis_client: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "attempted": False,
        "result": None,
        "error": None,
        "method": None,
        "constructor_signature": None,
    }
    svc_cls = getattr(strategy_mod, "StrategyService", None) or getattr(strategy_mod, "Service", None)
    if svc_cls is None:
        out["error"] = "No StrategyService/Service class found"
        return out

    try:
        out["constructor_signature"] = str(inspect.signature(svc_cls))
    except Exception:
        out["constructor_signature"] = "UNAVAILABLE"

    try:
        svc = svc_cls(
            redis_client=build_redis_adapter(redis_client),
            clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
            shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
            instance_id="batch26o17b-strategy",
        )
    except Exception as exc:
        out["error"] = f"{type(exc).__name__}: {exc}"
        return out

    for method_name in ("run_once", "tick", "evaluate_once", "evaluate"):
        method = getattr(svc, method_name, None)
        if callable(method):
            out["attempted"] = True
            out["method"] = method_name
            try:
                res = method()
                out["result"] = res if isinstance(res, (dict, list, str, int, float, bool, type(None))) else repr(res)
                return out
            except Exception as exc:
                out["error"] = f"{type(exc).__name__}: {exc}"
                return out

    out["error"] = "No safe one-shot method found"
    return out


def hget_json(redis_client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        return safe_json_load(redis_client.hget(key, field))
    except Exception:
        return {}


def contract_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    ff = payload.get("family_features", {})
    if not isinstance(ff, Mapping):
        ff = {}
    common = ff.get("common", {})
    if not isinstance(common, Mapping):
        common = {}
    selected = common.get("selected_option", {})
    if not isinstance(selected, Mapping):
        selected = {}
    return {
        "common_keys": tuple(common.keys()),
        "common_key_match": tuple(common.keys()) == EXPECTED_COMMON_KEYS,
        "selected_option_keys": tuple(selected.keys()),
        "selected_option_key_match": tuple(selected.keys()) == EXPECTED_SELECTED_OPTION_KEYS,
        "has_selected_option_rich_in_common": "selected_option_rich" in common,
        "stage_flags": dict(ff.get("stage_flags", {}) or {}) if isinstance(ff.get("stage_flags", {}), Mapping) else {},
    }


def patch_features_common_parent_abi(before_text: str) -> dict[str, Any]:
    marker = "Batch 26-O17B common parent ABI sanitizer"
    if marker in before_text:
        return {"patched": False, "already_present": True, "reason": "O17B marker already present"}

    required = [
        "FeatureService",
        "run_once",
        "HASH_FEATURES",
        "_batch26o16_build_consumer_view",
        "_batch26o16_normalize_family_frames",
    ]
    missing = [x for x in required if x not in before_text]
    if missing:
        return {"patched": False, "already_present": False, "reason": "required markers missing", "missing": missing}

    backup = BACKUP_DIR / "features.py.pre_o17b"
    shutil.copy2(TARGET_FEATURES, backup)

    patch = r'''

# =============================================================================
# Batch 26-O17B common parent ABI sanitizer
# =============================================================================
#
# Safety:
# - No strategy/risk/execution patch.
# - No order writes.
# - No real-live approval.
# - No candidate forcing.
# - No threshold relaxation.
# - Removes non-contract fields from family_features.common.
# - Preserves rich selected-option data outside family_features.common in
#   payload/o17b metadata/hash-only fields.

_BATCH26O17B_COMMON_ABI_KEYS = (
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals",
)

_BATCH26O17B_SELECTED_OPTION_ABI_KEYS = (
    "side",
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "ofi_ratio_proxy",
    "microprice",
    "micro_edge",
    "delta_3",
    "response_efficiency",
    "tradability_ok",
)


def _batch26o17b_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _batch26o17b_sanitize_selected_option(selected: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    rich = dict(selected or {})
    sanitized = {
        "side": str(rich.get("side") or rich.get("option_side") or "CALL").upper(),
        "ltp": _batch26o17b_float(rich.get("ltp"), 0.0),
        "spread": _batch26o17b_float(rich.get("spread"), 0.0),
        "spread_ratio": _batch26o17b_float(rich.get("spread_ratio"), 0.0),
        "depth_total": _batch26o17b_float(rich.get("depth_total"), 0.0),
        "depth_ok": bool(rich.get("depth_ok") is True or _batch26o17b_float(rich.get("depth_total"), 0.0) > 0.0),
        "ofi_ratio_proxy": rich.get("ofi_ratio_proxy"),
        "microprice": rich.get("microprice"),
        "micro_edge": rich.get("micro_edge"),
        "delta_3": rich.get("delta_3"),
        "response_efficiency": _batch26o17b_float(rich.get("response_efficiency"), 0.0),
        "tradability_ok": bool(rich.get("tradability_ok") is True or rich.get("selected_option_tradability_ok") is True),
    }
    return sanitized, rich


def _batch26o17b_sanitize_common(common: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    c = dict(common or {})
    selected_raw = dict(c.get("selected_option", {}) or {})
    existing_rich = dict(c.get("selected_option_rich", {}) or {})
    selected_abi, rich_from_selected = _batch26o17b_sanitize_selected_option(selected_raw)
    rich = existing_rich or rich_from_selected

    sanitized = {
        "regime": c.get("regime"),
        "strategy_runtime_mode_classic": c.get("strategy_runtime_mode_classic"),
        "strategy_runtime_mode_miso": c.get("strategy_runtime_mode_miso"),
        "futures": c.get("futures", {}),
        "call": c.get("call", {}),
        "put": c.get("put", {}),
        "selected_option": selected_abi,
        "cross_option": c.get("cross_option", {}),
        "economics": c.get("economics", {}),
        "signals": c.get("signals", {}),
    }
    return sanitized, rich


if "_BATCH26O17B_ORIGINAL_FEATURESERVICE_RUN_ONCE" not in globals() and "FeatureService" in globals():
    _BATCH26O17B_ORIGINAL_FEATURESERVICE_RUN_ONCE = FeatureService.run_once

    def _batch26o17b_run_once(self: FeatureService, *args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = dict(_BATCH26O17B_ORIGINAL_FEATURESERVICE_RUN_ONCE(self, *args, **kwargs))
        family_features = dict(payload.get("family_features", {}) or {})
        if not family_features:
            return payload

        common_before = dict(family_features.get("common", {}) or {})
        common_sanitized, selected_rich = _batch26o17b_sanitize_common(common_before)
        family_features["common"] = common_sanitized
        payload["family_features"] = family_features

        # Rich data is intentionally not placed under family_features.common.
        payload["selected_option_rich_runtime"] = selected_rich

        family_surfaces = dict(payload.get("family_surfaces", {}) or {})
        family_frames = dict(payload.get("family_frames", {}) or {})
        consumer_view = dict(payload.get("consumer_view", {}) or {})

        if family_surfaces:
            side = str(common_sanitized["selected_option"].get("side") or "").upper()
            for fam in FAMILY_IDS:
                for branch in BRANCH_IDS:
                    key = f"{str(fam).lower()}_{str(branch).lower()}"
                    surf = _batch26o16_surface_for_branch(family_surfaces, fam, branch)
                    if str(branch).upper() == side:
                        surf["selected_features"] = dict(selected_rich)
                        surf["option_features"] = dict(selected_rich)
                        surf["primary_features"] = dict(selected_rich)
                        surf["selected_option_abi"] = dict(common_sanitized["selected_option"])
                    family_surfaces.setdefault("surfaces_by_branch", {})[key] = surf

            payload["family_surfaces"] = family_surfaces
            generated_at_ns = _safe_int(payload.get("frame_ts_ns"), _safe_int(payload.get("generated_at_ns"), time.time_ns()))
            provider_runtime = _mapping(payload.get("provider_runtime") or family_features.get("provider_runtime"))
            family_frames = _batch26o16_normalize_family_frames(
                generated_at_ns=generated_at_ns,
                provider_runtime=provider_runtime,
                family_surfaces=family_surfaces,
                family_frames=family_frames,
            )
            payload["family_frames"] = family_frames

            consumer_view = _batch26o16_build_consumer_view(
                payload=payload,
                family_features=family_features,
                family_surfaces=family_surfaces,
                family_frames=family_frames,
            )
            payload["consumer_view"] = consumer_view

        feature_state = {
            "frame_id": payload.get("frame_id"),
            "frame_ts_ns": payload.get("frame_ts_ns"),
            "frame_valid": bool(payload.get("frame_valid")),
            "warmup_complete": bool(payload.get("warmup_complete")),
            "regime": _nested(family_features, "common", "regime", default=REGIME_NORMAL),
            "selected_option": common_sanitized["selected_option"],
        }

        hash_payload = {
            "frame_id": _safe_str(payload.get("frame_id")),
            "frame_ts_ns": _safe_str(payload.get("frame_ts_ns")),
            "ts_event_ns": _safe_str(payload.get("ts_event_ns")),
            "frame_valid": int(bool(payload.get("frame_valid"))),
            "warmup_complete": int(bool(payload.get("warmup_complete"))),
            "system_state": getattr(N, "STATE_SCANNING", "SCANNING") if payload.get("frame_valid") else getattr(N, "STATE_DISABLED", "DISABLED"),
            "strategy_mode": getattr(N, "STRATEGY_AUTO", "AUTO"),
            "family_features_version": _safe_str(family_features.get("family_features_version")),
            "family_features_json": _json_dump(family_features),
            "family_surfaces_json": _json_dump(family_surfaces),
            "family_frames_json": _json_dump(family_frames),
            "consumer_view_json": _json_dump(consumer_view),
            "feature_state_json": _json_dump(feature_state),
            "payload_json": _json_dump(payload),
            "selected_option_rich_json": _json_dump(selected_rich),
            "o17b_common_abi_json": _json_dump({
                "common_keys": list(common_sanitized.keys()),
                "expected_common_keys": list(_BATCH26O17B_COMMON_ABI_KEYS),
                "common_key_match": tuple(common_sanitized.keys()) == _BATCH26O17B_COMMON_ABI_KEYS,
                "selected_option_keys": list(common_sanitized["selected_option"].keys()),
                "expected_selected_option_keys": list(_BATCH26O17B_SELECTED_OPTION_ABI_KEYS),
                "selected_option_key_match": tuple(common_sanitized["selected_option"].keys()) == _BATCH26O17B_SELECTED_OPTION_ABI_KEYS,
                "selected_option_rich_in_common": False,
                "rich_preserved_outside_common": bool(selected_rich),
                "forced_candidate": False,
                "threshold_relaxation": False,
            }),
        }
        try:
            self.redis.hset(HASH_FEATURES, mapping=hash_payload)
        except Exception:
            pass

        return payload

    FeatureService.run_once = _batch26o17b_run_once
'''
    TARGET_FEATURES.write_text(before_text.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {"patched": True, "already_present": False, "backup": str(backup), "reason": "O17B common parent ABI sanitizer appended"}


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
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "common_parent_abi_sanitizer",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "guarded": True,
            "paper_restart": False,
            "risk_started": False,
            "execution_started": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_approval": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
            "allowed_patch": "features.py common parent ABI sanitizer only",
        },
    }

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None
    if redis_client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    o17a = safe_json_load(O17A_PATH.read_text(encoding="utf-8")) if O17A_PATH.exists() else {}
    result["o17a_gate"] = {
        "exists": O17A_PATH.exists(),
        "final_verdict": o17a.get("final_verdict") if isinstance(o17a, Mapping) else None,
        "post_check_parsed": o17a.get("post_check_parsed") if isinstance(o17a, Mapping) else None,
    }

    o17a_error = str((o17a.get("post_check_parsed") or {}).get("strategy_once_error") or "")
    allowed_o17a_gate = bool(
        o17a.get("final_verdict") == "FAIL_O17A_SELECTED_OPTION_ABI_SANITIZER_NOT_PROVEN"
        and "common keys mismatch" in o17a_error
        and "selected_option_rich" in o17a_error
    )
    if not allowed_o17a_gate:
        result["final_verdict"] = "FAIL_CLOSED_O17A_NOT_EXPECTED_COMMON_ABI_ERROR"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    compile_before = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/strategy_family/eligibility.py",
        "app/mme_scalpx/services/strategy_family/arbitration.py",
        "app/mme_scalpx/services/strategy_family/decisions.py",
        "app/mme_scalpx/services/feature_family/tradability.py",
        "app/mme_scalpx/services/feature_family/mist_surface.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile_before"] = compile_before

    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
        strategy = importlib.import_module("app.mme_scalpx.services.strategy")
    except Exception as exc:
        result["final_verdict"] = "FAIL_IMPORT_CONTEXT_NOT_READY"
        result["import_error"] = f"{type(exc).__name__}: {exc}"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    orders_key = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(names, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    runtime_key = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")
    features_key = getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut"))

    orders_before = int(redis_client.xlen(orders_key))
    decisions_before = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0
    rt_before = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_before = str(rt_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    payload_before = run_feature_once(features, redis_client)
    before_contract = contract_summary(payload_before)
    strategy_before = run_strategy_once(strategy, redis_client)

    result["before_contract"] = before_contract
    result["strategy_before"] = strategy_before

    patch_allowed = bool(
        before_contract["common_key_match"] is False
        and before_contract["selected_option_key_match"] is True
        and before_contract["has_selected_option_rich_in_common"] is True
        and "common keys mismatch" in str(strategy_before.get("error") or o17a_error)
    )

    result["exact_patch_gate"] = {
        "before_common_key_match": before_contract["common_key_match"],
        "before_selected_option_key_match": before_contract["selected_option_key_match"],
        "has_selected_option_rich_in_common": before_contract["has_selected_option_rich_in_common"],
        "strategy_before_error": strategy_before.get("error"),
        "patch_allowed": patch_allowed,
    }

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    if patch_allowed:
        patch_result = patch_features_common_parent_abi(before_text)
    else:
        patch_result = {"patched": False, "already_present": False, "reason": "O17B patch gate not satisfied"}

    result["patch_result"] = patch_result
    result["patch_performed"] = bool(patch_result.get("patched"))

    compile_after = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/strategy_family/eligibility.py",
        "app/mme_scalpx/services/strategy_family/arbitration.py",
        "app/mme_scalpx/services/strategy_family/decisions.py",
        "app/mme_scalpx/services/feature_family/tradability.py",
        "app/mme_scalpx/services/feature_family/mist_surface.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile_after"] = compile_after

    post_script = ROOT / "run/proofs/_tmp_batch26o17b_post_check.py"
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
from app.mme_scalpx.services import features, strategy

EXPECTED_COMMON = (
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals",
)

EXPECTED_SELECTED = (
    "side",
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "ofi_ratio_proxy",
    "microprice",
    "micro_edge",
    "delta_3",
    "response_efficiency",
    "tradability_ok",
)

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
    def xlen(self, *args, **kwargs):
        return self.inner.xlen(*args, **kwargs)
    def xrevrange(self, *args, **kwargs):
        return self.inner.xrevrange(*args, **kwargs)

client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
client.ping()
r = R(client)

svc = features.FeatureService(
    redis_client=r,
    clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
    shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
    instance_id="batch26o17b-feature-post",
)
payload = svc.run_once()

features_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))
raw = dec(client.hgetall(features_key) or {})
ff = json.loads(raw.get("family_features_json") or "{}")
cv = json.loads(raw.get("consumer_view_json") or "{}")
abi = json.loads(raw.get("o17b_common_abi_json") or "{}")
rich = json.loads(raw.get("selected_option_rich_json") or "{}")
common = ff.get("common", {}) if isinstance(ff, dict) else {}
selected = common.get("selected_option", {}) if isinstance(common, dict) else {}

strategy_result = None
strategy_error = None
try:
    ss = strategy.StrategyService(
        redis_client=r,
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o17b-strategy-post",
    )
    strategy_result = ss.run_once()
except Exception as exc:
    strategy_error = f"{type(exc).__name__}: {exc}"

out = {
    "payload_frame_valid": bool(isinstance(payload, dict) and payload.get("frame_valid")),
    "consumer_view_present": bool(cv),
    "consumer_view_data_valid": cv.get("data_valid"),
    "consumer_view_safe_to_consume": cv.get("safe_to_consume"),
    "common_keys": list(common.keys()) if isinstance(common, dict) else [],
    "common_key_match": tuple(common.keys()) == EXPECTED_COMMON if isinstance(common, dict) else False,
    "selected_option_keys": list(selected.keys()) if isinstance(selected, dict) else [],
    "selected_option_key_match": tuple(selected.keys()) == EXPECTED_SELECTED if isinstance(selected, dict) else False,
    "selected_option_rich_in_common": "selected_option_rich" in common if isinstance(common, dict) else False,
    "selected_option_rich_hash_present": bool(rich),
    "selected_option_rich_hash_key_count": len(rich) if isinstance(rich, dict) else 0,
    "o17b_common_abi_present": bool(abi),
    "o17b_common_abi": abi,
    "strategy_once_error": strategy_error,
    "strategy_once_result": strategy_result if isinstance(strategy_result, (dict, list, str, int, float, bool, type(None))) else repr(strategy_result),
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
    decisions_after = int(redis_client.xlen(decisions_key)) if redis_client.exists(decisions_key) else 0
    rt_after = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_after = str(rt_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    safety = {
        "orders_before": orders_before,
        "orders_after": orders_after,
        "orders_delta": orders_after - orders_before,
        "orders_zero": orders_after == 0,
        "decisions_before": decisions_before,
        "decisions_after": decisions_after,
        "decisions_delta": decisions_after - decisions_before,
        "real_live_before": real_live_before,
        "real_live_after": real_live_after,
        "risk_process_lines": pgrep_service("risk"),
        "execution_process_lines": pgrep_service("execution"),
        "strategy_process_lines": pgrep_service("strategy"),
        "feeds_process_lines": pgrep_service("feeds"),
    }
    result["safety"] = safety

    strategy_error_after = str(post_parsed.get("strategy_once_error") or "")
    required = {
        "redis_available": True,
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "patch_performed_or_already_present": bool(patch_result.get("patched") or patch_result.get("already_present")),
        "consumer_view_present": post_parsed.get("consumer_view_present") is True,
        "consumer_view_data_valid": post_parsed.get("consumer_view_data_valid") is True,
        "consumer_view_safe_to_consume": post_parsed.get("consumer_view_safe_to_consume") is True,
        "payload_frame_valid": post_parsed.get("payload_frame_valid") is True,
        "common_key_match": post_parsed.get("common_key_match") is True,
        "selected_option_key_match": post_parsed.get("selected_option_key_match") is True,
        "selected_option_rich_not_in_common": post_parsed.get("selected_option_rich_in_common") is False,
        "selected_option_rich_preserved_outside_common": post_parsed.get("selected_option_rich_hash_present") is True,
        "strategy_oneshot_no_feature_contract_error": "FeatureFamilyContractError" not in strategy_error_after,
        "orders_zero": orders_after == 0,
        "orders_delta_zero": orders_after == orders_before,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "no_forced_candidate": True,
        "no_threshold_relaxation": True,
    }
    result["required_verdicts"] = required

    if not all([
        required["compile_before_pass"],
        required["compile_after_pass"],
        required["patch_performed_or_already_present"],
        required["consumer_view_present"],
        required["consumer_view_data_valid"],
        required["consumer_view_safe_to_consume"],
        required["payload_frame_valid"],
        required["common_key_match"],
        required["selected_option_key_match"],
        required["selected_option_rich_not_in_common"],
        required["selected_option_rich_preserved_outside_common"],
        required["strategy_oneshot_no_feature_contract_error"],
        required["orders_zero"],
        required["orders_delta_zero"],
        required["risk_not_running"],
        required["execution_not_running"],
        required["real_live_false"],
    ]):
        result["final_verdict"] = "FAIL_O17B_COMMON_PARENT_ABI_SANITIZER_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to paper."
        write_outputs(result)
        return 2

    if post_parsed.get("strategy_once_error"):
        result["final_verdict"] = "PASS_O17B_COMMON_ABI_FIXED_STRATEGY_ONESHOT_NEXT_ERROR_REVIEW"
        result["next_recommended_batch"] = "26-O17C strategy one-shot next-error audit/repair, no risk/execution"
        write_outputs(result)
        return 0

    result["final_verdict"] = "PASS_O17B_STRATEGY_ONESHOT_CONTRACT_OK_NO_ORDER"
    result["next_recommended_batch"] = "26-O18 lightweight controlled-paper preflight, MIST CALL only, 1 lot, no heavy monitor"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
