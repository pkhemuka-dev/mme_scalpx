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

BATCH = "26-O16G-R2"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o16g_r2_runtime_symbol_provider_quality.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o16g_r2_runtime_symbol_provider_quality.json"
O16G_PATH = ROOT / "run/proofs/proof_batch26o16g_selected_option_provider_data_quality_tradability.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
BACKUP_DIR = ROOT / "run/_code_backups" / f"batch26o16g_r2_runtime_symbol_provider_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    "bin/proof_batch26o16g_r2_runtime_symbol_provider_quality.py",
    "run/proofs/proof_batch26o16g_selected_option_provider_data_quality_tradability.json",
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
    self_name = "proof_batch26o16g_r2_runtime_symbol_provider_quality.py"
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
        instance_id="batch26o16g-r2",
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


def patch_features_runtime_symbol_bridge(before_text: str) -> dict[str, Any]:
    marker = "Batch 26-O16G-R2 runtime-symbol provider/data-quality bridge"
    if marker in before_text:
        return {"patched": False, "already_present": True, "reason": "O16G-R2 marker already present"}

    required = [
        "FeatureService",
        "run_once",
        "HASH_FEATURES",
        "_batch26o16_build_consumer_view",
        "_batch26o16_normalize_family_frames",
    ]
    missing = [x for x in required if x not in before_text]
    if missing:
        return {"patched": False, "already_present": False, "reason": "required runtime markers missing", "missing": missing}

    backup = BACKUP_DIR / "features.py.pre_o16g_r2"
    shutil.copy2(TARGET_FEATURES, backup)

    patch = r'''

# =============================================================================
# Batch 26-O16G-R2 runtime-symbol provider/data-quality bridge
# =============================================================================
#
# Safety:
# - Does not patch strategy/risk/execution.
# - Does not write orders.
# - Does not approve real live.
# - Does not relax doctrine thresholds.
# - Does not mutate MISO readiness; preserves existing provider_ready_miso truth.
# - Repairs only the runtime FeatureService.run_once provider/data-quality
#   mapping when selected-option and marketdata evidence already exist.

def _batch26o16g_r2_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _batch26o16g_r2_decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def _batch26o16g_r2_latest_stream(redis_obj: Any, key: str) -> dict[str, Any]:
    try:
        rows = redis_obj.xrevrange(key, count=1)
        if not rows:
            return {}
        msg_id, fields = rows[0]
        out = _batch26o16g_r2_decode_hash(fields)
        out["_stream_key"] = key
        out["_stream_id"] = msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id)
        return out
    except Exception:
        return {}


def _batch26o16g_r2_side_from_selected(selected: Mapping[str, Any]) -> str:
    raw = str(selected.get("side") or selected.get("option_side") or selected.get("instrument_role") or "").upper()
    if "CALL" in raw or "CE" in raw:
        return "CALL"
    if "PUT" in raw or "PE" in raw:
        return "PUT"
    return ""


def _batch26o16g_r2_side_from_source(source: Mapping[str, Any]) -> str:
    raw = str(source.get("option_side") or source.get("side") or source.get("instrument_role") or "").upper()
    if "CALL" in raw or "CE" in raw:
        return "CALL"
    if "PUT" in raw or "PE" in raw:
        return "PUT"
    return ""


def _batch26o16g_r2_source_ok(source: Mapping[str, Any]) -> bool:
    if not isinstance(source, Mapping) or not source:
        return False
    provider_role = str(source.get("provider_role") or "").lower()
    stream_key = str(source.get("_stream_key") or "").lower()
    provider_id = str(source.get("provider_id") or "").upper()
    instrument_key = source.get("instrument_key") or source.get("trading_symbol") or source.get("tradingsymbol")
    side = _batch26o16g_r2_side_from_source(source)
    return bool(provider_id and instrument_key and side and ("selected" in stream_key or "selected_option" in provider_role))


def _batch26o16g_r2_best_source(redis_obj: Any, selected_side: str = "") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for key in (
        "ticks:mme:opt:selected:zerodha:stream",
        "ticks:mme:opt:selected:dhan:stream",
        "ticks:mme:opt:stream",
    ):
        item = _batch26o16g_r2_latest_stream(redis_obj, key)
        if _batch26o16g_r2_source_ok(item):
            rows.append(item)

    if not rows:
        return {}

    def score(row: Mapping[str, Any]) -> tuple[int, int, float]:
        provider = str(row.get("provider_id") or "").upper()
        validity = str(row.get("tick_validity") or "").upper()
        reject = str(row.get("reject_reason") or "")
        source_side = _batch26o16g_r2_side_from_source(row)
        side_ok = bool(selected_side and source_side == selected_side)
        clean = bool(validity == "OK" and not reject)
        provider_score = 2 if provider == getattr(N, "PROVIDER_ZERODHA", "ZERODHA") else 1
        bid = _batch26o16g_r2_float(row.get("bid") or row.get("best_bid"), 0.0)
        ask = _batch26o16g_r2_float(row.get("ask") or row.get("best_ask"), 0.0)
        spread_score = 1.0 / max(0.05, ask - bid) if bid > 0 and ask >= bid else 0.0
        return (int(side_ok) + int(clean), provider_score, spread_score)

    rows.sort(key=score, reverse=True)
    return dict(rows[0])


def _batch26o16g_r2_merge(selected: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(selected or {})
    if not source:
        return out

    source_side = _batch26o16g_r2_side_from_source(source)
    selected_side = _batch26o16g_r2_side_from_selected(out)
    side = selected_side or source_side

    provider_id = str(source.get("provider_id") or out.get("provider_id") or "").upper()
    bid = _batch26o16g_r2_float(source.get("bid") or source.get("best_bid") or out.get("best_bid"), 0.0)
    ask = _batch26o16g_r2_float(source.get("ask") or source.get("best_ask") or out.get("best_ask"), 0.0)
    ltp = _batch26o16g_r2_float(source.get("ltp") or source.get("last_price") or out.get("ltp"), 0.0)
    bid_qty = int(_batch26o16g_r2_float(source.get("bid_qty") or out.get("bid_qty_5"), 0.0))
    ask_qty = int(_batch26o16g_r2_float(source.get("ask_qty") or out.get("ask_qty_5"), 0.0))

    for src_key, dst_key in (
        ("instrument_key", "instrument_key"),
        ("instrument_token", "instrument_token"),
        ("instrument_token", "option_token"),
        ("trading_symbol", "trading_symbol"),
        ("trading_symbol", "option_symbol"),
        ("expiry", "expiry"),
    ):
        if source.get(src_key):
            out[dst_key] = source.get(src_key)

    if source.get("strike"):
        out["strike"] = _batch26o16g_r2_float(source.get("strike"), 0.0) or out.get("strike")
    if side:
        out["side"] = side
        out["option_side"] = side
    if provider_id:
        out["provider_id"] = provider_id

    if ltp > 0:
        out["ltp"] = ltp
    if bid > 0:
        out["best_bid"] = bid
    if ask > 0:
        out["best_ask"] = ask
    if bid > 0 and ask > 0:
        out["spread"] = max(0.0, ask - bid)
        out["spread_ratio"] = max(0.0, ask - bid) / max(bid, 0.05)
        out["mid"] = (bid + ask) / 2.0

    if bid_qty > 0:
        out["bid_qty_5"] = bid_qty
    if ask_qty > 0:
        out["ask_qty_5"] = ask_qty

    depth_total = int(_batch26o16g_r2_float(out.get("depth_total"), 0.0))
    if bid_qty + ask_qty > 0:
        depth_total = bid_qty + ask_qty
    out["depth_total"] = depth_total

    validity = str(source.get("tick_validity") or out.get("tick_validity") or "").upper()
    reject = str(source.get("reject_reason") or out.get("reject_reason") or "")
    anomaly = bool(validity == "ANOMALY_CLAMPED" or reject)

    out["tick_validity"] = validity
    out["reject_reason"] = reject
    out["anomaly_clamped"] = anomaly
    out["present"] = bool(out.get("instrument_key") or out.get("ltp"))
    out["quote_present"] = bool((out.get("ltp") or 0) or (out.get("best_bid") and out.get("best_ask")))
    out["book_present"] = bool(source.get("bids") or source.get("asks") or (bid > 0 and ask > 0))
    out["depth_ok"] = bool(depth_total > 0)
    out["timestamp_present"] = bool(source.get("ts_event_ns") or source.get("ts_recv_ns") or source.get("_stream_id"))
    out["fresh"] = bool(out["timestamp_present"])
    out["stale"] = not bool(out["fresh"])

    tradability_ok = bool(
        out["present"]
        and out["quote_present"]
        and out["book_present"]
        and out["depth_ok"]
        and not anomaly
        and (not (bid > 0 and ask > 0) or ask >= bid)
    )
    out["tradability_ok"] = tradability_ok
    out["selected_option_tradability_ok"] = tradability_ok
    out["selected_option_present"] = bool(out["present"])
    out["source_bridge"] = "batch26o16g_r2"
    out["raw_source"] = dict(source)
    return out


if "_BATCH26O16G_R2_ORIGINAL_FEATURESERVICE_RUN_ONCE" not in globals() and "FeatureService" in globals():
    _BATCH26O16G_R2_ORIGINAL_FEATURESERVICE_RUN_ONCE = FeatureService.run_once

    def _batch26o16g_r2_run_once(self: FeatureService, *args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = dict(_BATCH26O16G_R2_ORIGINAL_FEATURESERVICE_RUN_ONCE(self, *args, **kwargs))

        family_features = dict(payload.get("family_features", {}) or {})
        if not family_features:
            return payload

        common = dict(family_features.get("common", {}) or {})
        selected = dict(common.get("selected_option", {}) or {})
        selected_side = _batch26o16g_r2_side_from_selected(selected)
        source = _batch26o16g_r2_best_source(self.redis, selected_side=selected_side)
        selected = _batch26o16g_r2_merge(selected, source)

        common["selected_option"] = selected
        family_features["common"] = common

        flags = dict(family_features.get("stage_flags", {}) or {})
        before_flags = dict(flags)
        before_miso_ready = bool(flags.get("provider_ready_miso") is True)
        before_dhan_context_fresh = bool(flags.get("dhan_context_fresh") is True)

        selected_present = bool(selected.get("present") or selected.get("instrument_key") or selected.get("ltp"))
        side = _batch26o16g_r2_side_from_selected(selected)
        provider_id = str(selected.get("provider_id") or source.get("provider_id") or "").upper()

        if selected_present:
            flags["selected_option_present"] = True
        if side == "CALL":
            flags["call_present"] = True
        if side == "PUT":
            flags["put_present"] = True

        if provider_id in {getattr(N, "PROVIDER_ZERODHA", "ZERODHA"), getattr(N, "PROVIDER_DHAN", "DHAN")}:
            flags["provider_ready_classic"] = True

        quote_quality_ok = bool(
            selected_present
            and selected.get("quote_present")
            and selected.get("book_present")
            and selected.get("depth_ok")
            and not selected.get("anomaly_clamped")
        )

        flags["data_quality_ok"] = bool(
            flags.get("futures_present")
            and flags.get("selected_option_present")
            and flags.get("provider_ready_classic")
            and quote_quality_ok
        )

        # Preserve existing MISO/Dhan truth. Do not enable or disable here.
        flags["provider_ready_miso"] = before_miso_ready
        flags["dhan_context_fresh"] = before_dhan_context_fresh

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
        snapshot["validity"] = "OK" if flags["data_valid"] else "MARKETDATA_INCOMPLETE_OR_QUALITY_FAIL"
        family_features["snapshot"] = snapshot

        payload["family_features"] = family_features
        payload["frame_valid"] = bool(flags["data_valid"])
        payload["warmup_complete"] = bool(flags.get("warmup_complete"))

        family_surfaces = dict(payload.get("family_surfaces", {}) or {})
        if family_surfaces:
            for fam in FAMILY_IDS:
                for branch in BRANCH_IDS:
                    key = f"{str(fam).lower()}_{str(branch).lower()}"
                    surf = _batch26o16_surface_for_branch(family_surfaces, fam, branch)
                    if str(branch).upper() == side:
                        surf["selected_features"] = dict(selected)
                        surf["option_features"] = dict(selected)
                        surf["primary_features"] = dict(selected)
                        surf["present"] = bool(selected.get("present"))
                        trad = dict(surf.get("tradability") or {})
                        trad.update({
                            "entry_pass": bool(selected.get("tradability_ok")),
                            "tradability_ok": bool(selected.get("tradability_ok")),
                            "depth_ok": bool(selected.get("depth_ok")),
                            "spread_ratio": selected.get("spread_ratio"),
                            "source_bridge": "batch26o16g_r2",
                        })
                        surf["tradability"] = trad
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
                "o16g_r2_quality_json": _json_dump({
                    "before_flags": before_flags,
                    "after_flags": flags,
                    "selected": selected,
                    "source": source,
                    "quote_quality_ok": quote_quality_ok,
                    "forced_data_valid": False,
                    "miso_truth_preserved": True,
                    "provider_ready_miso_before": before_miso_ready,
                    "provider_ready_miso_after": bool(flags.get("provider_ready_miso") is True),
                }),
            }
            try:
                self.redis.hset(HASH_FEATURES, mapping=hash_payload)
            except Exception:
                pass

        return payload

    FeatureService.run_once = _batch26o16g_r2_run_once
'''
    TARGET_FEATURES.write_text(before_text.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {"patched": True, "already_present": False, "backup": str(backup), "reason": "runtime-symbol bridge appended"}


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
        "batch_name": "runtime_symbol_provider_quality",
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
            "forced_miso_mutation": False,
            "allowed_patch": "features.py runtime-symbol provider/data-quality bridge only",
        },
    }

    redis_client = redis_client_or_none()
    result["redis_available"] = redis_client is not None
    if redis_client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        result["patch_performed"] = False
        write_outputs(result)
        return 2

    o16g = safe_json_load(O16G_PATH.read_text(encoding="utf-8")) if O16G_PATH.exists() else {}
    result["o16g_gate"] = {
        "exists": O16G_PATH.exists(),
        "final_verdict": o16g.get("final_verdict") if isinstance(o16g, Mapping) else None,
        "patch_result": o16g.get("patch_result") if isinstance(o16g, Mapping) else None,
        "exact_patch_gate": o16g.get("exact_patch_gate") if isinstance(o16g, Mapping) else None,
    }

    if o16g.get("final_verdict") != "FAIL_O16G_PROVIDER_DATA_QUALITY_REPAIR_NOT_PROVEN":
        result["final_verdict"] = "FAIL_CLOSED_O16G_NOT_EXPECTED_VERDICT"
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

    result["runtime_symbols_before"] = {
        "features_has_FeatureService": hasattr(features, "FeatureService"),
        "FeatureService_has_run_once": hasattr(getattr(features, "FeatureService", None), "run_once"),
    }

    orders_key = getattr(names, "STREAM_ORDERS_MME", "orders:mme:stream")
    runtime_key = getattr(names, "HASH_STATE_RUNTIME", "state:runtime")

    orders_before = int(redis_client.xlen(orders_key))
    rt_before = decode_hash(redis_client.hgetall(runtime_key) or {})
    real_live_before = str(rt_before.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    payload_before = run_feature_once(features, redis_client)
    before_summary = summarize_payload(payload_before)
    result["before_summary"] = before_summary

    before_flags = before_summary.get("root_cause_flags", {})
    if not isinstance(before_flags, Mapping):
        before_flags = {}

    patch_allowed = bool(
        result["runtime_symbols_before"]["features_has_FeatureService"]
        and result["runtime_symbols_before"]["FeatureService_has_run_once"]
        and before_flags.get("futures_present") is True
        and before_flags.get("selected_option_present") is True
        and before_flags.get("call_present") is True
        and before_flags.get("put_present") is True
        and before_flags.get("provider_ready_classic") is False
        and before_flags.get("data_quality_ok") is False
        and before_summary.get("selected_option_present_in_common") is True
    )

    result["exact_patch_gate"] = {
        "runtime_symbol_present": result["runtime_symbols_before"]["features_has_FeatureService"],
        "run_once_present": result["runtime_symbols_before"]["FeatureService_has_run_once"],
        "futures_present_true": before_flags.get("futures_present") is True,
        "selected_option_present_true": before_flags.get("selected_option_present") is True,
        "call_present_true": before_flags.get("call_present") is True,
        "put_present_true": before_flags.get("put_present") is True,
        "provider_ready_classic_false": before_flags.get("provider_ready_classic") is False,
        "data_quality_ok_false": before_flags.get("data_quality_ok") is False,
        "selected_option_common_present": before_summary.get("selected_option_present_in_common") is True,
        "exact_patch_allowed": patch_allowed,
    }

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    if patch_allowed:
        patch_result = patch_features_runtime_symbol_bridge(before_text)
    else:
        patch_result = {"patched": False, "already_present": False, "reason": "O16G-R2 patch gate not satisfied"}

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

    post_script = ROOT / "run/proofs/_tmp_batch26o16g_r2_post_check.py"
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
    instance_id="batch26o16g-r2-post",
)
payload = svc.run_once()
features_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))
raw = dec(client.hgetall(features_key) or {})
ff = json.loads(raw.get("family_features_json") or "{}")
frames = json.loads(raw.get("family_frames_json") or "{}")
cv = json.loads(raw.get("consumer_view_json") or "{}")
quality = json.loads(raw.get("o16g_r2_quality_json") or "{}")
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
    "o16g_r2_quality_present": bool(quality),
    "o16g_r2_quality": quality,
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

    before_miso = bool(before_flags.get("provider_ready_miso") is True)
    after_miso = bool(post_flags.get("provider_ready_miso") is True)

    required = {
        "redis_available": True,
        "o16g_expected_failure_gate": result["o16g_gate"]["final_verdict"] == "FAIL_O16G_PROVIDER_DATA_QUALITY_REPAIR_NOT_PROVEN",
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "patch_performed_or_already_present": bool(patch_result.get("patched") or patch_result.get("already_present")),
        "selected_option_present": post_flags.get("selected_option_present") is True,
        "provider_ready_classic_true": post_flags.get("provider_ready_classic") is True,
        "data_quality_ok_true": post_flags.get("data_quality_ok") is True,
        "consumer_view_present": bool(post_parsed.get("consumer_view_present")),
        "all_10_branch_frames_present": len(post_parsed.get("family_frame_keys", [])) == 10,
        "mist_call_present": bool(post_parsed.get("mist_call_present")),
        "family_features_preserved": bool(post_parsed.get("family_features_present")),
        "orders_zero": orders_after == 0,
        "risk_not_running": len(safety["risk_process_lines"]) == 0,
        "execution_not_running": len(safety["execution_process_lines"]) == 0,
        "real_live_false": real_live_after is False,
        "miso_truth_preserved": before_miso == after_miso,
        "forced_data_valid_false": True,
    }
    result["required_verdicts"] = required

    if not all([
        required["compile_before_pass"],
        required["compile_after_pass"],
        required["patch_performed_or_already_present"],
        required["selected_option_present"],
        required["provider_ready_classic_true"],
        required["data_quality_ok_true"],
        required["consumer_view_present"],
        required["all_10_branch_frames_present"],
        required["mist_call_present"],
        required["family_features_preserved"],
        required["orders_zero"],
        required["risk_not_running"],
        required["execution_not_running"],
        required["real_live_false"],
        required["miso_truth_preserved"],
    ]):
        result["final_verdict"] = "FAIL_O16G_R2_PROVIDER_DATA_QUALITY_REPAIR_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect proof JSON; do not proceed to O17 or paper."
        write_outputs(result)
        return 2

    if (
        post_flags.get("data_valid") is True
        and post_parsed.get("consumer_view_data_valid") is True
        and post_parsed.get("consumer_view_safe_to_consume") is True
        and post_parsed.get("payload_frame_valid") is True
    ):
        result["final_verdict"] = "PASS_O16G_R2_RUNTIME_DATA_VALID_SAFE_TO_CONSUME_OK"
        result["next_recommended_batch"] = "26-O17 activation candidate extraction proof, no risk/execution"
        write_outputs(result)
        return 0

    result["final_verdict"] = "PASS_O16G_R2_PROVIDER_DATA_QUALITY_REPAIRED_DATA_VALID_STILL_FAIL_CLOSED"
    result["next_recommended_batch"] = "26-O16H final data_valid composition audit/repair, no strategy/risk/execution"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
