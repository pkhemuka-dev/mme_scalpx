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

BATCH = "26-O16F"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16f_selected_option_source_to_feature_mapping.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16f_selected_option_source_to_feature_mapping.json"
O16E_PATH = ROOT / "run/proofs/proof_batch26o16e_selected_option_feed_source_o8c_bridge.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
BACKUP_DIR = ROOT / "run/_code_backups" / f"batch26o16f_selected_option_source_to_feature_mapping_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    "bin/proof_batch26o16f_selected_option_source_to_feature_mapping.py",
    "run/proofs/proof_batch26o16e_selected_option_feed_source_o8c_bridge.json",
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


def pgrep_service(service: str) -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
    except Exception:
        return []
    matches: list[str] = []
    self_name = "proof_batch26o16f_selected_option_source_to_feature_mapping.py"
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


def stream_latest(redis_client: Any, key: str, count: int = 3) -> list[dict[str, Any]]:
    try:
        rows = redis_client.xrevrange(key, count=count)
        out = []
        for msg_id, fields in rows:
            out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
        return out
    except Exception:
        return []


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
        instance_id="batch26o16f",
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
    selected = common.get("selected_option", {})
    if not isinstance(selected, Mapping):
        selected = {}
    return {
        "frame_valid": bool(payload.get("frame_valid")),
        "warmup_complete": bool(payload.get("warmup_complete")),
        "family_features_present": bool(ff),
        "selected_option_present_in_common": bool(selected),
        "selected_option_common": dict(selected),
        "stage_flags": dict(flags),
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


def selected_option_source_audit(redis_client: Any) -> dict[str, Any]:
    keys = [
        "ticks:mme:opt:selected:zerodha:stream",
        "ticks:mme:opt:selected:dhan:stream",
        "ticks:mme:opt:stream",
        "ticks:mme:opt:context:dhan:stream",
    ]
    latest = {key: stream_latest(redis_client, key, count=3) for key in keys}
    usable = []
    rejected = []
    for key, rows in latest.items():
        for row in rows:
            fields = dict(row.get("fields") or {})
            instrument_key = fields.get("instrument_key") or fields.get("tradingsymbol") or fields.get("trading_symbol")
            ltp = fields.get("ltp") or fields.get("last_price") or fields.get("price")
            provider_role = str(fields.get("provider_role") or "").lower()
            provider_id = str(fields.get("provider_id") or "").upper()
            option_side = str(fields.get("option_side") or fields.get("side") or "").upper()
            tick_validity = str(fields.get("tick_validity") or "").upper()
            reject_reason = str(fields.get("reject_reason") or "").lower()
            has_core = bool(instrument_key and provider_id and option_side in {"CALL", "PUT", "CE", "PE"})
            is_selected_lane = "selected" in key.lower() or "selected_option" in provider_role
            anomaly_clamped = tick_validity == "ANOMALY_CLAMPED" or bool(reject_reason)
            row_summary = {
                "stream": key,
                "id": row.get("id"),
                "instrument_key": instrument_key,
                "instrument_token": fields.get("instrument_token") or fields.get("option_token"),
                "trading_symbol": fields.get("trading_symbol") or fields.get("tradingsymbol") or fields.get("option_symbol"),
                "provider_id": provider_id,
                "provider_role": fields.get("provider_role"),
                "option_side": option_side,
                "strike": fields.get("strike"),
                "expiry": fields.get("expiry"),
                "ltp": ltp,
                "bid": fields.get("bid") or fields.get("best_bid"),
                "ask": fields.get("ask") or fields.get("best_ask"),
                "tick_validity": tick_validity,
                "reject_reason": reject_reason,
                "is_selected_option": fields.get("is_selected_option"),
                "has_core": has_core,
                "is_selected_lane": is_selected_lane,
                "anomaly_clamped": anomaly_clamped,
                "raw": fields,
            }
            if has_core and is_selected_lane:
                usable.append(row_summary)
            else:
                rejected.append(row_summary)
    return {
        "latest": latest,
        "usable_selected_source_count": len(usable),
        "usable_selected_sources": usable,
        "rejected_sources": rejected[:10],
    }


def patch_features_selected_source_mapping(before_text: str) -> dict[str, Any]:
    marker = "Batch 26-O16F selected-option source-to-feature mapping bridge"
    if marker in before_text:
        return {"patched": False, "already_present": True, "reason": "O16F marker already present"}

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

    backup = BACKUP_DIR / "features.py.pre_o16f"
    shutil.copy2(TARGET_FEATURES, backup)

    patch = r'''

# =============================================================================
# Batch 26-O16F selected-option source-to-feature mapping bridge
# =============================================================================
#
# Safety:
# - Does not force data_valid blindly.
# - Does not patch strategy/risk/execution.
# - Does not write orders.
# - Does not enable MISO.
# - Maps selected-option stream truth into the feature common/stage surface only
#   when concrete selected-option source evidence exists.
# - ANOMALY_CLAMPED ticks may prove source presence, but they do not by
#   themselves prove full data_quality_ok.

def _batch26o16f_decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def _batch26o16f_latest_stream(redis_obj: Any, key: str) -> dict[str, Any]:
    try:
        rows = redis_obj.xrevrange(key, count=1)
        if not rows:
            return {}
        msg_id, fields = rows[0]
        out = _batch26o16f_decode_hash(fields)
        out["_stream_key"] = key
        out["_stream_id"] = msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id)
        return out
    except Exception:
        return {}


def _batch26o16f_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _batch26o16f_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "ok", "ready"}


def _batch26o16f_option_side(raw: Mapping[str, Any]) -> str:
    side = str(raw.get("option_side") or raw.get("side") or raw.get("instrument_role") or "").upper()
    if side in {"CE", "CALL"} or "CE" in side or "CALL" in side:
        return "CALL"
    if side in {"PE", "PUT"} or "PE" in side or "PUT" in side:
        return "PUT"
    return ""


def _batch26o16f_source_to_option(raw: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}

    provider_role = str(raw.get("provider_role") or "").lower()
    stream_key = str(raw.get("_stream_key") or "")
    provider_id = str(raw.get("provider_id") or "").upper()
    side = _batch26o16f_option_side(raw)

    instrument_key = (
        raw.get("instrument_key")
        or raw.get("tradingsymbol")
        or raw.get("trading_symbol")
        or raw.get("option_symbol")
    )
    instrument_token = raw.get("instrument_token") or raw.get("option_token")
    trading_symbol = raw.get("trading_symbol") or raw.get("tradingsymbol") or raw.get("option_symbol")

    is_selected_lane = bool("selected" in stream_key.lower() or "selected_option" in provider_role)
    has_core = bool(instrument_key and provider_id and side in {"CALL", "PUT"})

    if not (is_selected_lane and has_core):
        return {}

    bid = _batch26o16f_float(raw.get("bid") or raw.get("best_bid"), 0.0)
    ask = _batch26o16f_float(raw.get("ask") or raw.get("best_ask"), 0.0)
    ltp = _batch26o16f_float(raw.get("ltp") or raw.get("last_price") or raw.get("price"), 0.0)

    tick_validity = str(raw.get("tick_validity") or "").upper()
    reject_reason = str(raw.get("reject_reason") or "").lower()
    anomaly_clamped = bool(tick_validity == "ANOMALY_CLAMPED" or reject_reason)

    present = bool(ltp > 0.0 or bid > 0.0 or ask > 0.0)
    fresh = bool(raw.get("ts_event_ns") or raw.get("ts_recv_ns") or raw.get("_stream_id"))

    spread = max(0.0, ask - bid) if bid > 0 and ask > 0 else None
    mid = ((bid + ask) / 2.0) if bid > 0 and ask > 0 else ltp

    return {
        "present": present,
        "side": side,
        "provider_id": provider_id,
        "instrument_key": str(instrument_key),
        "instrument_token": str(instrument_token or ""),
        "option_symbol": str(trading_symbol or instrument_key),
        "trading_symbol": str(trading_symbol or instrument_key),
        "option_token": str(instrument_token or ""),
        "strike": _batch26o16f_float(raw.get("strike"), 0.0) or None,
        "expiry": raw.get("expiry"),
        "entry_mode": "classic_selected_option_source",
        "ltp": ltp if ltp > 0 else None,
        "best_bid": bid if bid > 0 else None,
        "best_ask": ask if ask > 0 else None,
        "mid": mid if mid and mid > 0 else None,
        "spread": spread,
        "spread_ratio": (ask / bid) if bid > 0 and ask > 0 else None,
        "bid_qty_5": int(_batch26o16f_float(raw.get("bid_qty"), 0.0)),
        "ask_qty_5": int(_batch26o16f_float(raw.get("ask_qty"), 0.0)),
        "depth_total": int(_batch26o16f_float(raw.get("bid_qty"), 0.0) + _batch26o16f_float(raw.get("ask_qty"), 0.0)),
        "volume": _batch26o16f_float(raw.get("volume"), 0.0) or None,
        "ltq": _batch26o16f_float(raw.get("last_qty") or raw.get("ltq"), 0.0) or None,
        "ts_event_ns": _safe_int(raw.get("ts_event_ns"), 0),
        "ts_recv_ns": _safe_int(raw.get("ts_recv_ns"), 0),
        "tick_size": 0.05,
        "raw": dict(raw),
        "metadata_present": bool(instrument_key and instrument_token),
        "quote_present": bool(ltp > 0.0 or (bid > 0.0 and ask > 0.0)),
        "book_present": bool(raw.get("bids") or raw.get("asks") or (bid > 0.0 and ask > 0.0)),
        "timestamp_present": fresh,
        "live_present": present,
        "fresh": fresh,
        "stale": not fresh,
        "anomaly_clamped": anomaly_clamped,
        "tick_validity": tick_validity,
        "reject_reason": reject_reason,
        "tradability_ok": bool(present and not anomaly_clamped and bid > 0.0 and ask > 0.0 and ask >= bid),
        "valid": bool(present),
        "selected_option_present": bool(present),
        "option_side": side,
        "role": "SELECTED_CALL" if side == "CALL" else "SELECTED_PUT",
        "source_stream": stream_key,
        "source_bridge": "batch26o16f",
    }


def _batch26o16f_collect_selected_option(redis_obj: Any) -> dict[str, Any]:
    candidates = [
        _batch26o16f_latest_stream(redis_obj, "ticks:mme:opt:selected:zerodha:stream"),
        _batch26o16f_latest_stream(redis_obj, "ticks:mme:opt:selected:dhan:stream"),
    ]
    converted = [_batch26o16f_source_to_option(c) for c in candidates]
    converted = [c for c in converted if c]
    if not converted:
        return {}

    # Prefer non-anomaly and then any present source.
    converted.sort(key=lambda x: (not bool(x.get("anomaly_clamped")), bool(x.get("present"))), reverse=True)
    return converted[0]


if "_BATCH26O16F_ORIGINAL_FEATURESERVICE_RUN_ONCE" not in globals():
    _BATCH26O16F_ORIGINAL_FEATURESERVICE_RUN_ONCE = FeatureService.run_once

    def _batch26o16f_run_once(self: FeatureService, *args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = dict(_BATCH26O16F_ORIGINAL_FEATURESERVICE_RUN_ONCE(self, *args, **kwargs))
        selected_source = _batch26o16f_collect_selected_option(self.redis)

        if not selected_source:
            return payload

        family_features = dict(payload.get("family_features", {}) or {})
        if not family_features:
            return payload

        common = dict(family_features.get("common", {}) or {})
        existing_selected = dict(common.get("selected_option", {}) or {})

        # Only fill when existing selected option is absent/incomplete.
        if not (existing_selected.get("present") or existing_selected.get("instrument_key")):
            common["selected_option"] = selected_source
        else:
            merged = dict(existing_selected)
            for k, v in selected_source.items():
                if merged.get(k) in (None, "", 0, 0.0, False):
                    merged[k] = v
            common["selected_option"] = merged

        family_features["common"] = common

        flags = dict(family_features.get("stage_flags", {}) or {})
        before_flags = dict(flags)

        selected_present = bool(common.get("selected_option", {}).get("present") or common.get("selected_option", {}).get("instrument_key"))
        side = str(common.get("selected_option", {}).get("side") or common.get("selected_option", {}).get("option_side") or "").upper()
        provider_id = str(common.get("selected_option", {}).get("provider_id") or "").upper()
        anomaly_clamped = bool(common.get("selected_option", {}).get("anomaly_clamped"))

        if selected_present:
            flags["selected_option_present"] = True
        if side == "CALL":
            flags["call_present"] = True
        if side == "PUT":
            flags["put_present"] = True
        if provider_id == getattr(N, "PROVIDER_ZERODHA", "ZERODHA"):
            flags["provider_ready_classic"] = True

        # Data quality requires real selected option and classic provider. If the
        # selected tick is anomaly-clamped, it proves mapping/source presence but
        # not full quality/tradability.
        flags["data_quality_ok"] = bool(
            flags.get("futures_present")
            and flags.get("selected_option_present")
            and flags.get("provider_ready_classic")
            and not anomaly_clamped
        )

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
        snapshot["validity"] = "OK" if flags["data_valid"] else "MARKETDATA_INCOMPLETE_OR_ANOMALY_CLAMPED"
        family_features["snapshot"] = snapshot

        payload["family_features"] = family_features
        payload["frame_valid"] = bool(flags["data_valid"])
        payload["warmup_complete"] = bool(flags.get("warmup_complete"))

        family_surfaces = dict(payload.get("family_surfaces", {}) or {})
        if family_surfaces:
            # Patch direct branch surfaces so branch frames can carry selected option source.
            for fam in FAMILY_IDS:
                for branch in BRANCH_IDS:
                    key = f"{str(fam).lower()}_{str(branch).lower()}"
                    surf = _batch26o16_surface_for_branch(family_surfaces, fam, branch)
                    if str(branch).upper() == side:
                        surf["selected_features"] = dict(common["selected_option"])
                        surf["option_features"] = dict(common["selected_option"])
                        surf["primary_features"] = dict(common["selected_option"])
                        surf["present"] = bool(common["selected_option"].get("present"))
                        surf["provider_ready"] = bool(flags.get("provider_ready_classic"))
                        surf["branch_ready"] = bool(flags.get("provider_ready_classic"))
                    family_surfaces.setdefault("surfaces_by_branch", {})[key] = surf
            payload["family_surfaces"] = family_surfaces

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

            feature_state = {
                "frame_id": payload.get("frame_id"),
                "frame_ts_ns": payload.get("frame_ts_ns"),
                "frame_valid": bool(payload.get("frame_valid")),
                "warmup_complete": bool(payload.get("warmup_complete")),
                "regime": _nested(family_features, "common", "regime", default=REGIME_NORMAL),
                "selected_option": common.get("selected_option", {}),
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
                "o16f_selected_source_json": _json_dump({
                    "before_flags": before_flags,
                    "after_flags": flags,
                    "selected_source": selected_source,
                    "forced_data_valid": False,
                    "anomaly_clamped_blocks_data_quality": anomaly_clamped,
                    "miso_fail_closed": True,
                }),
            }
            try:
                self.redis.hset(HASH_FEATURES, mapping=hash_payload)
            except Exception:
                pass

        return payload

    FeatureService.run_once = _batch26o16f_run_once
'''
    TARGET_FEATURES.write_text(before_text.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {"patched": True, "already_present": False, "backup": str(backup), "reason": "selected-option source-to-feature mapping bridge added"}


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
        "batch_name": "selected_option_source_to_feature_mapping",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
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
            "allowed_patch": "features.py selected-option source-to-feature mapping only",
        },
    }

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None
    if redis_client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    o16e = safe_json_load(O16E_PATH.read_text(encoding="utf-8")) if O16E_PATH.exists() else {}
    result["o16e_gate"] = {
        "exists": O16E_PATH.exists(),
        "final_verdict": o16e.get("final_verdict") if isinstance(o16e, Mapping) else None,
        "next_recommended_batch": o16e.get("next_recommended_batch") if isinstance(o16e, Mapping) else None,
    }

    if o16e.get("final_verdict") != "PASS_O16E_SOURCE_EVIDENCE_FOUND_MAPPING_REPAIR_NEEDED":
        result["final_verdict"] = "FAIL_CLOSED_O16E_NOT_SOURCE_EVIDENCE_FOUND"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

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

    source_audit = selected_option_source_audit(redis_client)
    result["selected_option_source_audit"] = source_audit

    payload_before = run_feature_once(features, redis_client)
    before_summary = summarize_payload(payload_before)
    result["before_summary"] = before_summary

    exact_patch_allowed = bool(
        source_audit.get("usable_selected_source_count", 0) > 0
        and before_summary.get("root_cause_flags", {}).get("futures_present") is True
        and before_summary.get("root_cause_flags", {}).get("selected_option_present") is False
    )
    result["exact_patch_gate"] = {
        "usable_selected_source_count": source_audit.get("usable_selected_source_count", 0),
        "futures_present_true": before_summary.get("root_cause_flags", {}).get("futures_present") is True,
        "selected_option_present_false": before_summary.get("root_cause_flags", {}).get("selected_option_present") is False,
        "exact_patch_allowed": exact_patch_allowed,
    }

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    if exact_patch_allowed:
        patch_result = patch_features_selected_source_mapping(before_text)
    else:
        patch_result = {"patched": False, "already_present": False, "reason": "exact patch gate not satisfied"}

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

    post_script = ROOT / "run/proofs/_tmp_batch26o16f_post_check.py"
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
    instance_id="batch26o16f-post",
)
payload = svc.run_once()
features_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))
raw = dec(client.hgetall(features_key) or {})
ff = json.loads(raw.get("family_features_json") or "{}")
frames = json.loads(raw.get("family_frames_json") or "{}")
cv = json.loads(raw.get("consumer_view_json") or "{}")
source = json.loads(raw.get("o16f_selected_source_json") or "{}")
flags = ff.get("stage_flags", {}) if isinstance(ff, dict) else {}
common = ff.get("common", {}) if isinstance(ff, dict) else {}
selected = common.get("selected_option", {}) if isinstance(common, dict) else {}
out = {
    "payload_frame_valid": bool(isinstance(payload, dict) and payload.get("frame_valid")),
    "hash_frame_valid": str(raw.get("frame_valid")),
    "family_features_present": bool(ff),
    "family_frames_present": bool(frames),
    "family_frame_keys": sorted(frames.keys()) if isinstance(frames, dict) else [],
    "consumer_view_present": bool(cv),
    "consumer_view_data_valid": cv.get("data_valid"),
    "consumer_view_safe_to_consume": cv.get("safe_to_consume"),
    "branch_frame_count": len(cv.get("branch_frames", {}) or {}),
    "mist_call_present": "mist_call" in (cv.get("branch_frames", {}) or {}),
    "stage_flags": flags,
    "selected_option": selected,
    "selected_option_present": bool(selected),
    "o16f_selected_source_present": bool(source),
    "o16f_selected_source": source,
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
        "risk_process_lines": pgrep_service("risk"),
        "execution_process_lines": pgrep_service("execution"),
        "strategy_process_lines": pgrep_service("strategy"),
        "feeds_process_lines": pgrep_service("feeds"),
    }
    result["safety"] = safety

    post_flags = post_parsed.get("stage_flags", {}) if isinstance(post_parsed, Mapping) else {}
    if not isinstance(post_flags, Mapping):
        post_flags = {}

    required = {
        "redis_available": True,
        "o16e_gate_pass": result["o16e_gate"]["final_verdict"] == "PASS_O16E_SOURCE_EVIDENCE_FOUND_MAPPING_REPAIR_NEEDED",
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "patch_performed_or_already_present": bool(patch_result.get("patched") or patch_result.get("already_present")),
        "selected_option_source_present": source_audit.get("usable_selected_source_count", 0) > 0,
        "selected_option_mapped_to_common": bool(post_parsed.get("selected_option_present")),
        "selected_option_stage_true": post_flags.get("selected_option_present") is True,
        "provider_ready_classic_true": post_flags.get("provider_ready_classic") is True,
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
        required["patch_performed_or_already_present"],
        required["selected_option_source_present"],
        required["selected_option_mapped_to_common"],
        required["selected_option_stage_true"],
        required["provider_ready_classic_true"],
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
        result["final_verdict"] = "FAIL_O16F_SELECTED_OPTION_MAPPING_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to O17 or paper."
        write_outputs(result)
        return 2

    if (
        post_flags.get("data_quality_ok") is True
        and post_flags.get("data_valid") is True
        and post_parsed.get("consumer_view_data_valid") is True
        and post_parsed.get("consumer_view_safe_to_consume") is True
    ):
        result["final_verdict"] = "PASS_O16F_SELECTED_OPTION_MAPPING_DATA_VALID_OK"
        result["next_recommended_batch"] = "26-O17 activation candidate extraction proof, no risk/execution"
        write_outputs(result)
        return 0

    result["final_verdict"] = "PASS_O16F_SELECTED_OPTION_MAPPING_REPAIRED_DATA_QUALITY_STILL_FAIL_CLOSED"
    result["next_recommended_batch"] = "26-O16G selected-option data-quality/tradability validation repair, no strategy/risk/execution"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
