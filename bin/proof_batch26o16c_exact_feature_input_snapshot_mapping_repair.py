#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import importlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16c_exact_feature_input_snapshot_mapping_repair.json"
O16B_PATH = ROOT / "run/proofs/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.json"

BATCH = "26-O16C"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
BACKUP_DIR = ROOT / "run/_code_backups" / f"batch26o16c_exact_feature_input_snapshot_mapping_repair_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.py",
    "run/proofs/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.json",
    "run/proofs/proof_batch26o16a_consumer_view_proof_correction_runtime_data_valid_audit.json",
    "run/proofs/proof_batch26o16_consumer_view_mapping_repair.json",
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
    self_name = "proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.py"
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
            "selected_raw": {
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
            "parsed": parsed,
        }
    except Exception as exc:
        return {
            "key": key,
            "error": f"{type(exc).__name__}: {exc}",
        }


def stream_latest(redis_client: Any, key: str) -> dict[str, Any]:
    try:
        length = int(redis_client.xlen(key))
        latest = None
        if length > 0:
            rows = redis_client.xrevrange(key, count=1)
            if rows:
                msg_id, fields = rows[0]
                latest = {
                    "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                    "fields": decode_hash(fields),
                }
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


def summarize_feature_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
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
        "family_features_present": bool(family_features),
        "family_surfaces_present": bool(family_surfaces),
        "family_frames_present": bool(family_frames),
        "consumer_view_present": bool(consumer_view),
        "family_frame_keys": sorted(str(k) for k in family_frames.keys()),
        "stage_flags": dict(stage_flags),
        "snapshot": dict(snapshot),
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
        def xrevrange(self, *args, **kwargs):
            return self.inner.xrevrange(*args, **kwargs)
        def xlen(self, *args, **kwargs):
            return self.inner.xlen(*args, **kwargs)
    return RedisAdapter(redis_client)


def build_runtime_payload(features_mod: Any, redis_client: Any) -> Mapping[str, Any]:
    svc = features_mod.FeatureService(
        redis_client=build_redis_adapter(redis_client),
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("Shutdown", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o16c-diagnostic",
    )
    payload = svc.run_once()
    if not isinstance(payload, Mapping):
        return {}
    return payload


def patch_features_if_exact_consumer_view_publish_gap(
    *,
    features_path: pathlib.Path,
    before_text: str,
) -> dict[str, Any]:
    """
    O16C narrow patch:
    Only patches the proven case where:
    - O16 helper functions exist.
    - FeatureService.run_once returns payload with family_features/family_surfaces/family_frames.
    - But runtime payload/hash lacks consumer_view.
    - Existing O16 publish block may not be on the active run_once path.

    The patch wraps FeatureService.run_once after class definition and republishes only feature-state
    consumer_view fields to HASH_FEATURES. It does NOT force data_valid and does NOT infer market truth.
    """

    marker = "Batch 26-O16C active run_once consumer_view publication bridge"
    if marker in before_text:
        return {
            "patched": False,
            "already_present": True,
            "reason": "O16C marker already present",
        }

    required_markers = [
        "_batch26o16_normalize_family_frames",
        "_batch26o16_build_consumer_view",
        "class FeatureService",
        "def run_once",
        "HASH_FEATURES",
    ]
    missing = [m for m in required_markers if m not in before_text]
    if missing:
        return {
            "patched": False,
            "already_present": False,
            "reason": "required markers missing",
            "missing_markers": missing,
        }

    backup_path = BACKUP_DIR / "features.py.pre_o16c"
    shutil.copy2(features_path, backup_path)

    patch = r'''

# =============================================================================
# Batch 26-O16C active run_once consumer_view publication bridge
# =============================================================================
#
# Safety:
# - Does not force data_valid.
# - Does not mark futures/option/provider readiness true.
# - Does not evaluate doctrine leaves.
# - Does not write orders.
# - Does not start risk/execution.
# - Only ensures the already-built family_features/family_surfaces/family_frames
#   are visible to the strategy consumer view on the active run_once path.

if "_BATCH26O16C_ORIGINAL_FEATURESERVICE_RUN_ONCE" not in globals():
    _BATCH26O16C_ORIGINAL_FEATURESERVICE_RUN_ONCE = FeatureService.run_once

    def _batch26o16c_run_once(self: FeatureService, *args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = dict(_BATCH26O16C_ORIGINAL_FEATURESERVICE_RUN_ONCE(self, *args, **kwargs))

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
            # Fail closed: run_once payload still returns, but no readiness is forged.
            pass

        return payload

    FeatureService.run_once = _batch26o16c_run_once
'''

    features_path.write_text(before_text.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {
        "patched": True,
        "already_present": False,
        "backup_path": str(backup_path),
        "reason": "active run_once path lacked consumer_view publication despite O16 helper availability",
    }


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    sys.path.insert(0, str(ROOT))

    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "exact_feature_input_snapshot_mapping_repair",
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
        "bin/proof_batch26o16c_exact_feature_input_snapshot_mapping_repair.py",
    ])

    result["compile_before"] = compile_before

    o16b = {}
    if O16B_PATH.exists():
        o16b = safe_json_load(O16B_PATH.read_text(encoding="utf-8"))

    o16b_final = o16b.get("final_verdict") if isinstance(o16b, Mapping) else None
    o16b_likely = o16b.get("likely_source_family") if isinstance(o16b, Mapping) else None

    result["o16b_gate"] = {
        "path": str(O16B_PATH),
        "exists": O16B_PATH.exists(),
        "final_verdict": o16b_final,
        "likely_source_family": o16b_likely,
        "root_cause_classification": o16b.get("root_cause_classification") if isinstance(o16b, Mapping) else None,
    }

    allowed_likely_sources = {
        "FEATURE_INPUT_SNAPSHOT_OR_REDIS_KEY_MAPPING_GAP",
        "DATA_QUALITY_OR_FRESHNESS_GATE_GAP",
        "COMPOSED_DATA_VALID_GATE_GAP",
    }

    if o16b_final != "PASS_O16B_RUNTIME_FRAME_VALID_ROOT_CAUSE_AUDIT_OK":
        result["final_verdict"] = "FAIL_CLOSED_O16B_NOT_PASS"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    if o16b_likely not in allowed_likely_sources:
        result["final_verdict"] = "FAIL_CLOSED_O16B_SOURCE_FAMILY_NOT_ALLOWED_FOR_O16C"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None

    try:
        names = importlib.import_module("app.mme_scalpx.core.names")
        features = importlib.import_module("app.mme_scalpx.services.features")
    except Exception as exc:
        result["import_error"] = f"{type(exc).__name__}: {exc}"
        result["final_verdict"] = "FAIL_IMPORTS_NOT_PROVEN"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    redis_before = {}
    payload_before_summary = {}
    orders_len_before = None
    real_live_approved_before = False

    if redis_client is not None:
        known_hashes = {
            "features_hash": getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut")),
            "runtime_hash": getattr(names, "HASH_STATE_RUNTIME", "state:runtime"),
            "provider_runtime_observed": "state:provider_runtime",
            "feed_snapshot_observed": "state:feed_snapshot",
            "health_feeds_observed": "health:feeds",
            "dhan_context_observed": "state:dhan_context",
        }
        known_streams = {
            "orders": getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream"),
            "features": getattr(names, "STREAM_FEATURES_MME", "features:mme:stream"),
            "ticks_fut_generic": "ticks:mme:fut:stream",
            "ticks_opt_generic": "ticks:mme:opt:stream",
            "ticks_fut_zerodha": "ticks:mme:fut:zerodha:stream",
            "ticks_opt_selected_zerodha": "ticks:mme:opt:selected:zerodha:stream",
            "ticks_fut_dhan": "ticks:mme:fut:dhan:stream",
            "ticks_opt_selected_dhan": "ticks:mme:opt:selected:dhan:stream",
        }

        redis_before = {
            "hashes": {label: hash_summary(redis_client, key) for label, key in known_hashes.items()},
            "streams": {label: stream_latest(redis_client, key) for label, key in known_streams.items()},
        }

        try:
            payload_before = build_runtime_payload(features, redis_client)
            payload_before_summary = summarize_feature_payload(payload_before)
        except Exception as exc:
            payload_before_summary = {"error": f"{type(exc).__name__}: {exc}"}

        try:
            orders_len_before = int(redis_client.xlen(known_streams["orders"]))
        except Exception:
            orders_len_before = None

        try:
            rt = decode_hash(redis_client.hgetall(known_hashes["runtime_hash"]) or {})
            real_live_approved_before = str(rt.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}
        except Exception:
            real_live_approved_before = False

    result["redis_before"] = redis_before
    result["payload_before_summary"] = payload_before_summary
    result["safety_before"] = {
        "orders_len": orders_len_before,
        "real_live_approved": real_live_approved_before,
        "risk_process_lines": pgrep_python_service("risk"),
        "execution_process_lines": pgrep_python_service("execution"),
    }

    # Exact gap detection:
    # O16B proved branch frames exist but runtime consumer_view absent. If the active run_once
    # returns no consumer_view despite O16 helpers, repair active publication bridge only.
    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    exact_gap = {
        "o16_helper_present": "_batch26o16_build_consumer_view" in before_text,
        "o16_normalizer_present": "_batch26o16_normalize_family_frames" in before_text,
        "o16c_marker_present_before": "Batch 26-O16C active run_once consumer_view publication bridge" in before_text,
        "payload_before_has_family_features": bool(payload_before_summary.get("family_features_present")),
        "payload_before_has_family_surfaces": bool(payload_before_summary.get("family_surfaces_present")),
        "payload_before_has_family_frames": bool(payload_before_summary.get("family_frames_present")),
        "payload_before_has_consumer_view": bool(payload_before_summary.get("consumer_view_present")),
        "runtime_frame_valid_before": payload_before_summary.get("frame_valid"),
    }

    result["exact_gap_detection"] = exact_gap

    patch_performed = False
    patch_result = {
        "patched": False,
        "reason": "not attempted",
    }

    if (
        exact_gap["o16_helper_present"]
        and exact_gap["o16_normalizer_present"]
        and exact_gap["payload_before_has_family_features"]
        and exact_gap["payload_before_has_family_surfaces"]
        and exact_gap["payload_before_has_family_frames"]
        and not exact_gap["payload_before_has_consumer_view"]
    ):
        patch_result = patch_features_if_exact_consumer_view_publish_gap(
            features_path=TARGET_FEATURES,
            before_text=before_text,
        )
        patch_performed = bool(patch_result.get("patched"))

    result["patch_result"] = patch_result
    result["patch_performed"] = patch_performed

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

    # Re-import in a fresh subprocess so the monkeypatch appended to features.py is active.
    post_check = run_cmd([
        sys.executable,
        "- <<'PYPOST'\n"
        "import json, pathlib, time\n"
        "from typing import Any, Mapping\n"
        "import redis\n"
        "from app.mme_scalpx.core import names as N\n"
        "from app.mme_scalpx.services import features\n"
        "\n"
        "def dec(raw):\n"
        "    return {(k.decode() if isinstance(k, bytes) else str(k)):(v.decode() if isinstance(v, bytes) else str(v)) for k,v in dict(raw or {}).items()}\n"
        "\n"
        "class R:\n"
        "    def __init__(self, inner): self.inner=inner\n"
        "    def hgetall(self, key): return self.inner.hgetall(key)\n"
        "    def hset(self, key, mapping=None, **kwargs):\n"
        "        if mapping is not None:\n"
        "            return self.inner.hset(key, mapping={k:(v if isinstance(v, str) else str(v)) for k,v in mapping.items()})\n"
        "        return self.inner.hset(key, **kwargs)\n"
        "    def xadd(self, *a, **k): return self.inner.xadd(*a, **k)\n"
        "\n"
        "client=redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=False)\n"
        "client.ping()\n"
        "svc=features.FeatureService(redis_client=R(client), clock=type('Clock',(),{'now_ns':staticmethod(time.time_ns)})(), shutdown=type('S',(),{'is_set':staticmethod(lambda: True)})(), instance_id='batch26o16c-post')\n"
        "payload=svc.run_once()\n"
        "hash_key=getattr(N,'HASH_STATE_FEATURES_MME_FUT',getattr(N,'HASH_FEATURES','state:features:mme:fut'))\n"
        "raw=dec(client.hgetall(hash_key) or {})\n"
        "cv=json.loads(raw.get('consumer_view_json') or '{}')\n"
        "ff=json.loads(raw.get('family_features_json') or '{}')\n"
        "frames=json.loads(raw.get('family_frames_json') or '{}')\n"
        "out={\n"
        "  'payload_has_consumer_view': bool(isinstance(payload, dict) and payload.get('consumer_view')),\n"
        "  'payload_frame_valid': bool(isinstance(payload, dict) and payload.get('frame_valid')),\n"
        "  'hash_consumer_view_present': bool(cv),\n"
        "  'hash_consumer_view_data_valid': cv.get('data_valid'),\n"
        "  'hash_consumer_view_safe_to_consume': cv.get('safe_to_consume'),\n"
        "  'hash_branch_frame_count': len(cv.get('branch_frames',{}) or {}),\n"
        "  'hash_mist_call_present': 'mist_call' in (cv.get('branch_frames',{}) or {}),\n"
        "  'hash_family_features_present': bool(ff),\n"
        "  'hash_family_frames_present': bool(frames),\n"
        "  'hash_family_frame_keys': sorted(frames.keys()) if isinstance(frames, dict) else [],\n"
        "}\n"
        "print(json.dumps(out, indent=2, sort_keys=True))\n"
        "PYPOST"
    ], timeout=60)

    # The above "- <<" form cannot be passed as argv to Python. Fall back to a temp script.
    post_tmp = ROOT / "run/proofs/_tmp_batch26o16c_post_check.py"
    post_tmp.write_text(r'''
import json
import time
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
    instance_id="batch26o16c-post",
)
payload = svc.run_once()
hash_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))
raw = dec(client.hgetall(hash_key) or {})
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
    post_check = run_cmd([sys.executable, str(post_tmp)], timeout=60)

    post_parsed = {}
    try:
        post_parsed = json.loads(post_check.get("stdout") or "{}")
    except Exception:
        post_parsed = {}

    result["post_check"] = post_check
    result["post_check_parsed"] = post_parsed

    orders_len_after = None
    real_live_approved_after = False
    if redis_client is not None:
        try:
            orders_len_after = int(redis_client.xlen(getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")))
        except Exception:
            orders_len_after = None
        try:
            rt = decode_hash(redis_client.hgetall(getattr(names, "HASH_STATE_RUNTIME", "state:runtime")) or {})
            real_live_approved_after = str(rt.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}
        except Exception:
            real_live_approved_after = False

    result["safety_after"] = {
        "orders_len": orders_len_after,
        "real_live_approved": real_live_approved_after,
        "risk_process_lines": pgrep_python_service("risk"),
        "execution_process_lines": pgrep_python_service("execution"),
    }

    required_verdicts = {
        "o16b_pass_gate": o16b_final == "PASS_O16B_RUNTIME_FRAME_VALID_ROOT_CAUSE_AUDIT_OK",
        "o16b_allowed_source_family": o16b_likely in allowed_likely_sources,
        "compile_before_pass": compile_before.get("returncode") == 0,
        "compile_after_pass": compile_after.get("returncode") == 0,
        "patch_performed_or_already_present": bool(patch_performed or patch_result.get("already_present")),
        "post_hash_consumer_view_present": bool(post_parsed.get("hash_consumer_view_present")),
        "post_all_10_family_frames_present": len(post_parsed.get("hash_family_frame_keys", [])) == 10,
        "post_mist_call_present": bool(post_parsed.get("hash_mist_call_present")),
        "family_features_preserved": bool(post_parsed.get("hash_family_features_present")),
        "orders_zero": orders_len_after == 0,
        "risk_not_running": len(result["safety_after"]["risk_process_lines"]) == 0,
        "execution_not_running": len(result["safety_after"]["execution_process_lines"]) == 0,
        "real_live_approved_false": real_live_approved_after is False,
        "runtime_data_valid_not_forced": post_parsed.get("payload_frame_valid") == payload_before_summary.get("frame_valid"),
    }

    result["required_verdicts"] = required_verdicts

    if (
        required_verdicts["o16b_pass_gate"]
        and required_verdicts["o16b_allowed_source_family"]
        and required_verdicts["compile_before_pass"]
        and required_verdicts["compile_after_pass"]
        and required_verdicts["patch_performed_or_already_present"]
        and required_verdicts["post_hash_consumer_view_present"]
        and required_verdicts["post_all_10_family_frames_present"]
        and required_verdicts["post_mist_call_present"]
        and required_verdicts["family_features_preserved"]
        and required_verdicts["orders_zero"]
        and required_verdicts["risk_not_running"]
        and required_verdicts["execution_not_running"]
        and required_verdicts["real_live_approved_false"]
        and required_verdicts["runtime_data_valid_not_forced"]
    ):
        if post_parsed.get("hash_consumer_view_data_valid") is True and post_parsed.get("hash_consumer_view_safe_to_consume") is True:
            final_verdict = "PASS_O16C_CONSUMER_VIEW_AND_RUNTIME_DATA_VALID_OK"
            next_batch = "26-O17 activation candidate extraction proof, no risk/execution"
        else:
            final_verdict = "PASS_O16C_CONSUMER_VIEW_PUBLICATION_REPAIRED_RUNTIME_DATA_VALID_STILL_FAIL_CLOSED"
            next_batch = "26-O16D exact marketdata/provider readiness mapping repair, no strategy/risk/execution"
        exit_code = 0
    else:
        final_verdict = "FAIL_O16C_EXACT_MAPPING_REPAIR_NOT_PROVEN"
        next_batch = "Inspect proof JSON; do not proceed to O17 or paper."
        exit_code = 2

    result["final_verdict"] = final_verdict
    result["next_recommended_batch"] = next_batch

    write_outputs(result)
    return exit_code


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
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
    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
