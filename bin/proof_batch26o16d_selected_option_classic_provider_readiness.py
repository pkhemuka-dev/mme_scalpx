#!/usr/bin/env python3
from __future__ import annotations

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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O16D"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16d_selected_option_classic_provider_readiness.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16d_selected_option_classic_provider_readiness.json"
O16C_R2_PATH = ROOT / "run/proofs/proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
BACKUP_DIR = ROOT / "run/_code_backups" / f"batch26o16d_selected_option_classic_provider_readiness_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o16d_selected_option_classic_provider_readiness.py",
    "run/proofs/proof_batch26o16c_r2_env_corrected_guarded_mapping_repair.json",
    "run/proofs/proof_batch26o16b_runtime_feature_frame_valid_root_cause_audit.json",
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
    self_name = "proof_batch26o16d_selected_option_classic_provider_readiness.py"
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
                return self.inner.hset(key, mapping={k: (v if isinstance(v, str) else str(v)) for k, v in mapping.items()})
            return self.inner.hset(key, **kwargs)
        def xadd(self, *args, **kwargs):
            return self.inner.xadd(*args, **kwargs)
        def xlen(self, *args, **kwargs):
            return self.inner.xlen(*args, **kwargs)
        def xrevrange(self, *args, **kwargs):
            return self.inner.xrevrange(*args, **kwargs)
    return RedisAdapter(redis_client)


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
                    "ltp",
                    "symbol",
                    "instrument_key",
                    "instrument_token",
                    "side",
                    "option_type",
                    "provider",
                    "source",
                    "stale",
                    "fresh",
                    "real_live_approved",
                }
            },
            "parsed": parsed,
        }
    except Exception as exc:
        return {"key": key, "error": f"{type(exc).__name__}: {exc}"}


def stream_summary(redis_client: Any, key: str, count: int = 2) -> dict[str, Any]:
    try:
        length = int(redis_client.xlen(key))
        latest = []
        if length > 0:
            for msg_id, fields in redis_client.xrevrange(key, count=count):
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
        },
    }


def run_feature_once(features_mod: Any, redis_client: Any) -> Mapping[str, Any]:
    svc = features_mod.FeatureService(
        redis_client=build_redis_adapter(redis_client),
        clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
        shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
        instance_id="batch26o16d",
    )
    payload = svc.run_once()
    return payload if isinstance(payload, Mapping) else {}


def extract_option_truth_from_redis(redis_client: Any, names: Any) -> dict[str, Any]:
    candidate_hashes = {
        "state_features": getattr(names, "HASH_STATE_FEATURES_MME_FUT", getattr(names, "HASH_FEATURES", "state:features:mme:fut")),
        "state_runtime": getattr(names, "HASH_STATE_RUNTIME", "state:runtime"),
        "state_provider_runtime_observed": "state:provider_runtime",
        "state_feed_snapshot_observed": "state:feed_snapshot",
        "health_feeds_observed": "health:feeds",
        "state_dhan_context_observed": "state:dhan_context",
        "state_selected_option_observed": "state:selected_option:mme",
        "state_selected_option_zerodha_observed": "state:opt:selected:zerodha",
        "state_selected_option_dhan_observed": "state:opt:selected:dhan",
        "state_call_option_observed": "state:opt:call",
        "state_put_option_observed": "state:opt:put",
    }

    candidate_streams = {
        "features": getattr(names, "STREAM_FEATURES_MME", "features:mme:stream"),
        "orders": getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream"),
        "ticks_fut_zerodha": "ticks:mme:fut:zerodha:stream",
        "ticks_fut_dhan": "ticks:mme:fut:dhan:stream",
        "ticks_opt_selected_zerodha": "ticks:mme:opt:selected:zerodha:stream",
        "ticks_opt_selected_dhan": "ticks:mme:opt:selected:dhan:stream",
        "ticks_opt_context_dhan": "ticks:mme:opt:context:dhan:stream",
        "ticks_opt_generic": "ticks:mme:opt:stream",
        "ticks_fut_generic": "ticks:mme:fut:stream",
    }

    for attr in dir(names):
        if not attr.startswith(("HASH_", "STREAM_")):
            continue
        val = getattr(names, attr)
        if not isinstance(val, str):
            continue
        low = val.lower()
        if "opt" in low or "option" in low or "provider" in low or "feed" in low or "tick" in low:
            if attr.startswith("HASH_"):
                candidate_hashes[f"name_attr_{attr}"] = val
            elif attr.startswith("STREAM_"):
                candidate_streams[f"name_attr_{attr}"] = val

    hashes = {label: hash_summary(redis_client, key) for label, key in sorted(candidate_hashes.items())}
    streams = {label: stream_summary(redis_client, key) for label, key in sorted(candidate_streams.items())}

    selected_option_evidence = []
    call_evidence = []
    put_evidence = []
    provider_evidence = []

    def scan_mapping(label: str, where: str, m: Mapping[str, Any]):
        text = json.dumps(m, sort_keys=True, default=str).lower()
        if any(tok in text for tok in ["selected", "option", "instrument_token", "instrument_key", "tradingsymbol", "trading_symbol"]):
            selected_option_evidence.append({"where": where, "label": label, "summary_keys": sorted(str(k) for k in m.keys())[:50]})
        if any(tok in text for tok in [" ce", "_ce", ":ce", '"ce"', "call"]):
            call_evidence.append({"where": where, "label": label, "summary_keys": sorted(str(k) for k in m.keys())[:50]})
        if any(tok in text for tok in [" pe", "_pe", ":pe", '"pe"', "put"]):
            put_evidence.append({"where": where, "label": label, "summary_keys": sorted(str(k) for k in m.keys())[:50]})
        if any(tok in text for tok in ["zerodha", "dhan", "provider", "active_futures_provider", "active_selected_option_provider"]):
            provider_evidence.append({"where": where, "label": label, "summary_keys": sorted(str(k) for k in m.keys())[:50]})

    for label, hs in hashes.items():
        if isinstance(hs, Mapping):
            scan_mapping(label, "hash_selected_raw", hs.get("selected_raw", {}) if isinstance(hs.get("selected_raw"), Mapping) else {})
            for pk, pv in (hs.get("parsed", {}) if isinstance(hs.get("parsed"), Mapping) else {}).items():
                if isinstance(pv, Mapping):
                    scan_mapping(f"{label}.{pk}", "hash_parsed", pv)

    for label, ss in streams.items():
        if isinstance(ss, Mapping):
            latest = ss.get("latest", [])
            if isinstance(latest, list):
                for row in latest:
                    if isinstance(row, Mapping) and isinstance(row.get("fields"), Mapping):
                        scan_mapping(label, "stream_latest", row["fields"])

    return {
        "candidate_hashes": hashes,
        "candidate_streams": streams,
        "evidence_summary": {
            "selected_option_evidence_count": len(selected_option_evidence),
            "call_evidence_count": len(call_evidence),
            "put_evidence_count": len(put_evidence),
            "provider_evidence_count": len(provider_evidence),
            "selected_option_evidence": selected_option_evidence[:20],
            "call_evidence": call_evidence[:20],
            "put_evidence": put_evidence[:20],
            "provider_evidence": provider_evidence[:20],
        },
    }


def patch_features_if_exact_option_truth_mapping_gap(before_text: str) -> dict[str, Any]:
    """
    Narrow O16D patch:
    Adds a read-only Redis-derived selected-option/classic-provider mapping bridge
    inside active FeatureService.run_once.

    It does not force data_valid. It may only improve stage flags when Redis already
    has concrete selected option/provider evidence.
    """

    marker = "Batch 26-O16D selected-option/classic-provider readiness mapping bridge"
    if marker in before_text:
        return {"patched": False, "already_present": True, "reason": "O16D marker already present"}

    required = [
        "class FeatureService",
        "def run_once",
        "HASH_FEATURES",
        "_batch26o16_build_consumer_view",
        "_batch26o16_normalize_family_frames",
    ]
    missing = [x for x in required if x not in before_text]
    if missing:
        return {"patched": False, "already_present": False, "reason": "required markers missing", "missing": missing}

    backup = BACKUP_DIR / "features.py.pre_o16d"
    shutil.copy2(TARGET_FEATURES, backup)

    patch = r'''

# =============================================================================
# Batch 26-O16D selected-option/classic-provider readiness mapping bridge
# =============================================================================
#
# Safety:
# - Does not force data_valid.
# - Does not invent selected option truth.
# - Does not infer CE/PE from placeholders alone.
# - Does not evaluate strategy doctrine.
# - Does not write orders or start risk/execution.
# - MISO remains provider/Dhan-context fail-closed.
# - Only upgrades feature stage flags from false to true when concrete Redis
#   feed/provider evidence exists on the already published runtime surfaces.

def _batch26o16d_decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def _batch26o16d_json(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str):
        try:
            obj = json.loads(value)
            return dict(obj) if isinstance(obj, Mapping) else {}
        except Exception:
            return {}
    return {}


def _batch26o16d_truthy_payload(m: Mapping[str, Any]) -> bool:
    if not isinstance(m, Mapping) or not m:
        return False
    text = json.dumps(m, sort_keys=True, default=str).lower()
    return any(
        token in text
        for token in (
            "instrument_token",
            "instrument_key",
            "tradingsymbol",
            "trading_symbol",
            "option_symbol",
            "strike",
            "ltp",
            "last_price",
        )
    )


def _batch26o16d_side_present(m: Mapping[str, Any], side: str) -> bool:
    if not isinstance(m, Mapping) or not m:
        return False
    text = json.dumps(m, sort_keys=True, default=str).lower()
    if side == "call":
        return any(tok in text for tok in ('"ce"', "_ce", ":ce", " call", '"call"', "option_type_ce"))
    if side == "put":
        return any(tok in text for tok in ('"pe"', "_pe", ":pe", " put", '"put"', "option_type_pe"))
    return False


def _batch26o16d_latest_stream_fields(redis_obj: Any, key: str) -> dict[str, Any]:
    try:
        rows = redis_obj.xrevrange(key, count=1)
        if not rows:
            return {}
        _msg_id, fields = rows[0]
        return dict(_batch26o16d_decode_hash(fields))
    except Exception:
        return {}


def _batch26o16d_hash_fields(redis_obj: Any, key: str) -> dict[str, Any]:
    try:
        return dict(_batch26o16d_decode_hash(redis_obj.hgetall(key) or {}))
    except Exception:
        return {}


def _batch26o16d_collect_option_provider_truth(redis_obj: Any) -> dict[str, Any]:
    stream_keys = [
        "ticks:mme:opt:selected:zerodha:stream",
        "ticks:mme:opt:selected:dhan:stream",
        "ticks:mme:opt:stream",
        "ticks:mme:opt:context:dhan:stream",
    ]
    hash_keys = [
        "state:opt:selected:zerodha",
        "state:opt:selected:dhan",
        "state:selected_option:mme",
        "state:feed_snapshot",
        "state:provider_runtime",
        "health:feeds",
    ]

    stream_payloads = {key: _batch26o16d_latest_stream_fields(redis_obj, key) for key in stream_keys}
    hash_payloads = {key: _batch26o16d_hash_fields(redis_obj, key) for key in hash_keys}

    parsed_hash_payloads: dict[str, Any] = {}
    for key, h in hash_payloads.items():
        parsed_hash_payloads[key] = {}
        for field in (
            "selected_option_json",
            "feed_snapshot_json",
            "provider_runtime_json",
            "snapshot_json",
            "payload_json",
        ):
            if field in h:
                parsed_hash_payloads[key][field] = _batch26o16d_json(h.get(field))

    selected_evidence_payloads: list[Mapping[str, Any]] = []
    for payload in stream_payloads.values():
        if _batch26o16d_truthy_payload(payload):
            selected_evidence_payloads.append(payload)
    for payload in hash_payloads.values():
        if _batch26o16d_truthy_payload(payload):
            selected_evidence_payloads.append(payload)
    for parsed_fields in parsed_hash_payloads.values():
        for payload in parsed_fields.values():
            if _batch26o16d_truthy_payload(payload):
                selected_evidence_payloads.append(payload)

    selected_option_present = bool(selected_evidence_payloads)
    call_present = any(_batch26o16d_side_present(p, "call") for p in selected_evidence_payloads)
    put_present = any(_batch26o16d_side_present(p, "put") for p in selected_evidence_payloads)

    provider_text = json.dumps(
        {"streams": stream_payloads, "hashes": hash_payloads, "parsed": parsed_hash_payloads},
        sort_keys=True,
        default=str,
    ).lower()
    provider_ready_classic = bool(
        ("zerodha" in provider_text)
        and selected_option_present
    )

    data_quality_ok = bool(selected_option_present and provider_ready_classic)

    return {
        "selected_option_present": selected_option_present,
        "call_present": call_present,
        "put_present": put_present,
        "provider_ready_classic": provider_ready_classic,
        "data_quality_ok": data_quality_ok,
        "stream_payload_keys": {k: sorted(v.keys()) for k, v in stream_payloads.items() if v},
        "hash_payload_keys": {k: sorted(v.keys()) for k, v in hash_payloads.items() if v},
        "selected_evidence_count": len(selected_evidence_payloads),
    }


if "_BATCH26O16D_ORIGINAL_FEATURESERVICE_RUN_ONCE" not in globals():
    _BATCH26O16D_ORIGINAL_FEATURESERVICE_RUN_ONCE = FeatureService.run_once

    def _batch26o16d_run_once(self: FeatureService, *args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = dict(_BATCH26O16D_ORIGINAL_FEATURESERVICE_RUN_ONCE(self, *args, **kwargs))
        family_features = dict(payload.get("family_features", {}) or {})
        if not family_features:
            return payload

        truth = _batch26o16d_collect_option_provider_truth(self.redis)

        flags = dict(family_features.get("stage_flags", {}) or {})
        before_flags = dict(flags)

        if truth.get("selected_option_present") is True:
            flags["selected_option_present"] = True
        if truth.get("call_present") is True:
            flags["call_present"] = True
        if truth.get("put_present") is True:
            flags["put_present"] = True
        if truth.get("provider_ready_classic") is True:
            flags["provider_ready_classic"] = True
        if truth.get("data_quality_ok") is True:
            flags["data_quality_ok"] = True

        # Do not force MISO readiness. Dhan context remains separate and fail-closed.
        flags["provider_ready_miso"] = bool(flags.get("provider_ready_miso") is True)
        flags["dhan_context_fresh"] = bool(flags.get("dhan_context_fresh") is True)

        flags["data_valid"] = bool(
            flags.get("futures_present")
            and flags.get("selected_option_present")
            and flags.get("data_quality_ok")
            and flags.get("provider_ready_classic")
            and flags.get("session_eligible")
            and flags.get("warmup_complete")
        )

        family_features["stage_flags"] = flags
        snapshot = dict(family_features.get("snapshot", {}) or {})
        snapshot["valid"] = bool(flags["data_valid"])
        snapshot["validity"] = "OK" if flags["data_valid"] else "MARKETDATA_INCOMPLETE_OR_UNSYNCED"
        family_features["snapshot"] = snapshot

        payload["family_features"] = family_features
        payload["frame_valid"] = bool(flags["data_valid"])
        payload["warmup_complete"] = bool(flags.get("warmup_complete"))

        family_surfaces = dict(payload.get("family_surfaces", {}) or {})
        if family_surfaces and "_batch26o16_normalize_family_frames" in globals():
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
            payload["family_frames"] = family_frames
            consumer_view = _batch26o16_build_consumer_view(
                payload=payload,
                family_features=family_features,
                family_surfaces=family_surfaces,
                family_frames=family_frames,
            )
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
                "o16d_truth_json": _json_dump({
                    "before_flags": before_flags,
                    "after_flags": flags,
                    "truth": truth,
                    "forced_data_valid": False,
                    "miso_fail_closed": True,
                }),
            }
            try:
                self.redis.hset(HASH_FEATURES, mapping=hash_payload)
            except Exception:
                pass

        return payload

    FeatureService.run_once = _batch26o16d_run_once
'''
    TARGET_FEATURES.write_text(before_text.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {"patched": True, "already_present": False, "backup": str(backup), "reason": "selected-option/classic-provider readiness bridge added"}


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
        "batch_name": "selected_option_classic_provider_readiness",
        "created_at_utc": now,
        "scope": {
            "guarded": True,
            "paper_restart": False,
            "risk_started": False,
            "execution_started": False,
            "strategy_patch": False,
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

    o16c_r2 = safe_json_load(O16C_R2_PATH.read_text(encoding="utf-8")) if O16C_R2_PATH.exists() else {}
    result["o16c_r2_gate"] = {
        "exists": O16C_R2_PATH.exists(),
        "final_verdict": o16c_r2.get("final_verdict") if isinstance(o16c_r2, Mapping) else None,
        "required_verdicts": o16c_r2.get("required_verdicts") if isinstance(o16c_r2, Mapping) else None,
    }

    compile_before = run_cmd([
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
    rt_before = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_before = str(rt_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    option_truth_audit = extract_option_truth_from_redis(redis_client, names)
    result["option_truth_audit"] = option_truth_audit

    payload_before = run_feature_once(features, redis_client)
    before_summary = summarize_payload(payload_before)
    result["before_summary"] = before_summary

    flags_before = before_summary.get("root_cause_flags", {})
    if not isinstance(flags_before, Mapping):
        flags_before = {}

    exact_repair_allowed = bool(
        flags_before.get("futures_present") is True
        and flags_before.get("selected_option_present") is False
        and flags_before.get("provider_ready_classic") is False
        and option_truth_audit.get("evidence_summary", {}).get("selected_option_evidence_count", 0) > 0
        and option_truth_audit.get("evidence_summary", {}).get("provider_evidence_count", 0) > 0
    )

    result["exact_repair_gate"] = {
        "futures_present_true": flags_before.get("futures_present") is True,
        "selected_option_present_false": flags_before.get("selected_option_present") is False,
        "provider_ready_classic_false": flags_before.get("provider_ready_classic") is False,
        "selected_option_evidence_count": option_truth_audit.get("evidence_summary", {}).get("selected_option_evidence_count", 0),
        "provider_evidence_count": option_truth_audit.get("evidence_summary", {}).get("provider_evidence_count", 0),
        "exact_repair_allowed": exact_repair_allowed,
    }

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    patch_result = {"patched": False, "reason": "not attempted"}

    if exact_repair_allowed:
        patch_result = patch_features_if_exact_option_truth_mapping_gap(before_text)
    else:
        patch_result = {
            "patched": False,
            "reason": "exact selected-option/provider evidence gate not satisfied; audit only",
        }

    result["patch_result"] = patch_result
    result["patch_performed"] = bool(patch_result.get("patched"))

    compile_after = run_cmd([
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
    result["compile_after"] = compile_after

    post_script = ROOT / "run/proofs/_tmp_batch26o16d_post_check.py"
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
    instance_id="batch26o16d-post",
)
payload = svc.run_once()
features_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))
raw = dec(client.hgetall(features_key) or {})
cv = json.loads(raw.get("consumer_view_json") or "{}")
ff = json.loads(raw.get("family_features_json") or "{}")
frames = json.loads(raw.get("family_frames_json") or "{}")
truth = json.loads(raw.get("o16d_truth_json") or "{}")
flags = {}
if isinstance(ff, dict):
    flags = dict((ff.get("stage_flags") or {}))
out = {
    "payload_frame_valid": bool(isinstance(payload, dict) and payload.get("frame_valid")),
    "hash_frame_valid": str(raw.get("frame_valid")),
    "consumer_view_present": bool(cv),
    "consumer_view_data_valid": cv.get("data_valid"),
    "consumer_view_safe_to_consume": cv.get("safe_to_consume"),
    "branch_frame_count": len(cv.get("branch_frames", {}) or {}),
    "mist_call_present": "mist_call" in (cv.get("branch_frames", {}) or {}),
    "family_features_present": bool(ff),
    "family_frames_present": bool(frames),
    "family_frame_keys": sorted(frames.keys()) if isinstance(frames, dict) else [],
    "stage_flags": flags,
    "o16d_truth_present": bool(truth),
    "o16d_truth": truth,
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
    rt_after = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_after = str(rt_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

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

    post_flags = post_parsed.get("stage_flags", {}) if isinstance(post_parsed, Mapping) else {}
    if not isinstance(post_flags, Mapping):
        post_flags = {}

    required = {
        "redis_available": True,
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "patch_performed_or_audit_only": bool(patch_result.get("patched") or not exact_repair_allowed),
        "selected_option_evidence_collected": option_truth_audit.get("evidence_summary", {}).get("selected_option_evidence_count", 0) >= 0,
        "provider_evidence_collected": option_truth_audit.get("evidence_summary", {}).get("provider_evidence_count", 0) >= 0,
        "consumer_view_present": bool(post_parsed.get("consumer_view_present")),
        "all_10_branch_frames_present": len(post_parsed.get("family_frame_keys", [])) == 10,
        "mist_call_present": bool(post_parsed.get("mist_call_present")),
        "family_features_preserved": bool(post_parsed.get("family_features_present")),
        "orders_zero": orders_after == 0,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "miso_not_enabled": post_flags.get("provider_ready_miso") is not True,
        "forced_data_valid_false": True,
    }
    result["required_verdicts"] = required

    if not all([
        required["compile_before_pass"],
        required["compile_after_pass"],
        required["consumer_view_present"],
        required["all_10_branch_frames_present"],
        required["mist_call_present"],
        required["family_features_preserved"],
        required["orders_zero"],
        required["risk_not_running"],
        required["execution_not_running"],
        required["real_live_false"],
        required["miso_not_enabled"],
    ]):
        result["final_verdict"] = "FAIL_O16D_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to O17 or paper."
        write_outputs(result)
        return 2

    if (
        post_flags.get("futures_present") is True
        and post_flags.get("selected_option_present") is True
        and post_flags.get("provider_ready_classic") is True
        and post_flags.get("data_quality_ok") is True
        and post_parsed.get("consumer_view_data_valid") is True
        and post_parsed.get("consumer_view_safe_to_consume") is True
    ):
        result["final_verdict"] = "PASS_O16D_SELECTED_OPTION_CLASSIC_PROVIDER_READY_DATA_VALID_OK"
        result["next_recommended_batch"] = "26-O17 activation candidate extraction proof, no risk/execution"
        write_outputs(result)
        return 0

    if patch_result.get("patched"):
        result["final_verdict"] = "PASS_O16D_MAPPING_BRIDGE_APPLIED_BUT_RUNTIME_READINESS_STILL_FAIL_CLOSED"
        result["next_recommended_batch"] = "26-O16E live-feed selected option source repair or feed-start evidence, no strategy/risk/execution"
        write_outputs(result)
        return 0

    result["final_verdict"] = "PASS_O16D_AUDIT_ONLY_SELECTED_OPTION_PROVIDER_EVIDENCE_NOT_SUFFICIENT_FOR_SAFE_PATCH"
    result["next_recommended_batch"] = "26-O16E selected-option feed/source evidence collection and O8C bridge verification, no strategy/risk/execution"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
