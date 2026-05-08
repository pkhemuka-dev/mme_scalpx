#!/usr/bin/env python3
from __future__ import annotations

import inspect
import json
import sys
import time
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "app"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from app.mme_scalpx.core import names as N
from bin._batch25v_market_observation_common import redis_client


PROOF_PATH = Path("run/proofs/proof_market_session_strategy_activation.json")


class ProofFeatureBundle:
    """Proof-local adapter for StrategyFamilyConsumerBridge bundle API."""

    def __init__(self, payload: Mapping[str, Any]):
        self.payload = dict(payload or {})
        self.family_features = dict(self.payload.get("family_features") or {})
        self.family_surfaces = dict(self.payload.get("family_surfaces") or {})
        self.family_frames = dict(self.payload.get("family_frames") or {})
        self.frame_id = self.payload.get("frame_id")
        self.frame_ts_ns = self.payload.get("frame_ts_ns") or self.payload.get("ts_event_ns")
        self.ts_event_ns = self.payload.get("ts_event_ns") or self.frame_ts_ns
        self.provider_runtime = dict(
            self.payload.get("provider_runtime")
            or self.family_features.get("provider_runtime")
            or {}
        )

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


def _decode_value(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return value


def _decode_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    return {str(_decode_value(k)): _decode_value(v) for k, v in dict(raw or {}).items()}


def _json_load(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return default
    try:
        return json.loads(text)
    except Exception:
        return default


def _first_redis_hash(client: Any, candidates: list[str]) -> tuple[str, dict[str, Any]]:
    for key in candidates:
        if not key:
            continue
        try:
            raw = client.hgetall(key) or {}
        except Exception:
            continue
        data = _decode_hash(raw)
        if data:
            return key, data
    return "", {}


def _feature_hash_candidates() -> list[str]:
    names = [
        "HASH_STATE_FEATURES_MME_FUT",
        "HASH_STATE_FEATURES",
        "HASH_FEATURES",
        "HASH_FEATURES_MME",
        "HASH_STATE_FEATURES_MME",
    ]
    keys: list[str] = []
    for name in names:
        value = getattr(N, name, None)
        if isinstance(value, str) and value:
            keys.append(value)

    keys.extend(
        [
            "state:features:mme:fut",
            "state:features:mme",
            "features:mme:state",
            "state:features",
        ]
    )

    deduped: list[str] = []
    for key in keys:
        if key not in deduped:
            deduped.append(key)
    return deduped


def _read_feature_payload(client: Any) -> tuple[str, dict[str, Any], dict[str, Any]]:
    key, data = _first_redis_hash(client, _feature_hash_candidates())

    payload = _json_load(data.get("payload_json"), {})
    if not isinstance(payload, dict):
        payload = {}

    if not payload:
        family_features = _json_load(data.get("family_features_json"), {})
        family_surfaces = _json_load(data.get("family_surfaces_json"), {})
        family_frames = _json_load(data.get("family_frames_json"), {})
        payload = {
            "frame_id": data.get("frame_id"),
            "frame_ts_ns": data.get("frame_ts_ns"),
            "ts_event_ns": data.get("ts_event_ns") or data.get("frame_ts_ns"),
            "family_features": family_features if isinstance(family_features, dict) else {},
            "family_surfaces": family_surfaces if isinstance(family_surfaces, dict) else {},
            "family_frames": family_frames if isinstance(family_frames, dict) else {},
        }

    return key, data, payload


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    raw = getattr(value, "__dict__", None)
    if isinstance(raw, Mapping):
        return dict(raw)
    return {}


def _view_to_dict(view: Any) -> dict[str, Any]:
    if isinstance(view, Mapping):
        return dict(view)
    to_dict = getattr(view, "to_dict", None)
    if callable(to_dict):
        result = to_dict()
        if isinstance(result, Mapping):
            return dict(result)
    return _mapping(view)


def _build_consumer_view(client: Any, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    from app.mme_scalpx.services import strategy as strategy_mod

    bridge_cls = getattr(strategy_mod, "StrategyFamilyConsumerBridge", None)
    if bridge_cls is None:
        return "missing_bridge_class", {}

    try:
        bridge = bridge_cls(redis_client=client)
    except TypeError:
        bridge = bridge_cls()

    bundle = ProofFeatureBundle(payload)

    if hasattr(bridge, "build_consumer_view"):
        fn = bridge.build_consumer_view
        sig = inspect.signature(fn)
        if "now_ns" in sig.parameters:
            view = fn(bundle, now_ns=time.time_ns())
        else:
            view = fn(bundle)
        return "build_consumer_view", _view_to_dict(view)

    if hasattr(bridge, "build_view"):
        fn = bridge.build_view
        sig = inspect.signature(fn)
        if "now_ns" in sig.parameters:
            view = fn(bundle, now_ns=time.time_ns())
        else:
            view = fn(bundle)
        return "build_view", _view_to_dict(view)

    return "missing_build_method", {}


def _family_surface_count(payload: Mapping[str, Any]) -> int:
    surfaces = payload.get("family_surfaces") or {}
    if not isinstance(surfaces, Mapping):
        return 0

    direct = surfaces.get("surfaces_by_branch")
    if isinstance(direct, Mapping):
        return len(direct)

    fams = surfaces.get("families")
    if isinstance(fams, Mapping):
        count = 0
        for family in fams.values():
            if isinstance(family, Mapping):
                for side in ("CALL", "PUT"):
                    if isinstance(family.get(side), Mapping):
                        count += 1
        return count

    return 0


def _extract_strategy_action(view: Mapping[str, Any]) -> str:
    for key in ("action", "strategy_action", "decision_action", "published_action"):
        value = view.get(key)
        if value not in (None, ""):
            return str(value).upper()

    decision = view.get("decision")
    if isinstance(decision, Mapping):
        for key in ("action", "strategy_action"):
            value = decision.get(key)
            if value not in (None, ""):
                return str(value).upper()

    return "HOLD"


def main() -> int:
    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)

    client = redis_client()
    feature_hash_key, feature_hash, payload = _read_feature_payload(client)

    family_features = payload.get("family_features")
    family_surfaces = payload.get("family_surfaces")
    family_frames = payload.get("family_frames")

    bridge_method, view = _build_consumer_view(client, payload)
    action = _extract_strategy_action(view)

    family_features_present = isinstance(family_features, Mapping) and bool(family_features)
    family_surfaces_present = isinstance(family_surfaces, Mapping) and bool(family_surfaces)
    family_frames_present = isinstance(family_frames, Mapping) and bool(family_frames)
    bridge_view_built = bool(view)
    family_surface_count = _family_surface_count(payload)

    non_hold_action = action not in {"", "HOLD", "NONE", "NOOP", "NO_OP"}

    checks = {
        "feature_hash_present": bool(feature_hash_key and feature_hash),
        "feature_payload_present": bool(payload),
        "family_features_present": family_features_present,
        "family_surfaces_present": family_surfaces_present,
        "family_frames_present": family_frames_present,
        "family_surface_count_at_least_10": family_surface_count >= 10,
        "strategy_bridge_method_present": bridge_method not in {"missing_bridge_class", "missing_build_method"},
        "strategy_consumer_view_built": bridge_view_built,
        "strategy_activation_report_only": not non_hold_action,
        "paper_armed_not_approved": True,
        "real_live_not_approved": True,
    }

    proof = {
        "proof_name": "proof_market_session_strategy_activation",
        "batch": "25V",
        "generated_at_ns": time.time_ns(),
        "market_session_strategy_activation_ok": all(checks.values()),
        "checks": checks,
        "feature_hash_key": feature_hash_key,
        "bridge_method": bridge_method,
        "strategy_action": action,
        "family_surface_count": family_surface_count,
        "view_keys": sorted(view.keys()),
        "paper_armed_approved": False,
        "real_live_approved": False,
        "proof_path": str(PROOF_PATH),
    }

    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))

    return 0 if proof["market_session_strategy_activation_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
