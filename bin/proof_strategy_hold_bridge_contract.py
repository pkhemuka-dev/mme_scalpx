#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = ROOT / "run" / "proofs" / "strategy_hold_bridge_contract.json"

def assert_case(name: str, condition: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"name": name, "ok": bool(condition), "details": details or {}}
    if not condition:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row

class FakeRedis:
    def __init__(self, hash_payload: Mapping[str, Any] | None = None) -> None:
        self.hash_payload = dict(hash_payload or {})
        self.xadds: list[dict[str, Any]] = []
        self.hsets: list[dict[str, Any]] = []
        self.pexpires: list[tuple[str, int]] = []

    def hgetall(self, key: str) -> Mapping[str, Any]:
        return dict(self.hash_payload)

    def xadd(self, stream: str, fields: Mapping[str, Any], maxlen: int | None = None, approximate: bool = True) -> str:
        self.xadds.append({
            "stream": stream,
            "fields": dict(fields),
            "maxlen": maxlen,
            "approximate": approximate,
        })
        return "1-0"

    def hset(self, key: str, mapping: Mapping[str, Any]) -> int:
        self.hsets.append({"key": key, "mapping": dict(mapping)})
        return 1

    def pexpire(self, key: str, ttl_ms: int) -> bool:
        self.pexpires.append((key, ttl_ms))
        return True

class FakeClock:
    def __init__(self, now_ns: int = 1_777_000_000_000_000_000) -> None:
        self.now_ns_value = now_ns

    def now_ns(self) -> int:
        self.now_ns_value += 1_000_000
        return self.now_ns_value

class FakeShutdown:
    def is_set(self) -> bool:
        return True

    def wait(self, seconds: float) -> bool:
        return True

def build_surfaces_and_frames(strategy_mod: Any, contracts_mod: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    family_surfaces = {
        "families": {},
        "surfaces_by_branch": {},
    }
    family_frames: dict[str, Any] = {}

    for family_id in contracts_mod.FAMILY_IDS:
        family_surfaces["families"][family_id] = {
            "family_id": family_id,
            "eligible": False,
        }
        for branch_id in contracts_mod.BRANCH_IDS:
            key = f"{family_id.lower()}_{branch_id.lower()}"
            family_surfaces["surfaces_by_branch"][key] = {
                "family_id": family_id,
                "branch_id": branch_id,
                "eligible": False,
            }
            family_frames[key] = {
                "family_id": family_id,
                "branch_id": branch_id,
                "side": "",
                "eligible": False,
                "tradability_ok": False,
                "instrument_key": "",
                "instrument_token": "",
                "option_symbol": "",
                "strike": "",
                "option_price": "",
            }

    return family_surfaces, family_frames

def main() -> int:
    sys.path.insert(0, str(ROOT))

    from app.mme_scalpx.core import names as N
    from app.mme_scalpx.services.feature_family import contracts as FF_C
    from app.mme_scalpx.services import strategy as S

    cases: list[dict[str, Any]] = []

    family_features = FF_C.build_empty_family_features_payload(generated_at_ns=123)
    family_features["snapshot"]["samples_seen"] = 1
    family_features["stage_flags"]["data_valid"] = True
    family_features["stage_flags"]["warmup_complete"] = True
    family_features["stage_flags"]["provider_ready_classic"] = False
    family_features["stage_flags"]["provider_ready_miso"] = False

    family_surfaces, family_frames = build_surfaces_and_frames(S, FF_C)

    valid_hash = {
        "family_features_json": json.dumps(family_features, separators=(",", ":")),
        "family_surfaces_json": json.dumps(family_surfaces, separators=(",", ":")),
        "family_frames_json": json.dumps(family_frames, separators=(",", ":")),
        "payload_json": json.dumps({"frame_id": "features-frame-1", "frame_ts_ns": 777}, separators=(",", ":")),
        "frame_id": "features-frame-1",
        "frame_ts_ns": "777",
    }

    redis = FakeRedis(valid_hash)
    bridge = S.StrategyFamilyConsumerBridge(redis_client=redis)
    bundle = bridge.read_feature_bundle()
    view = bridge.build_consumer_view(bundle, now_ns=1_000)
    decision = bridge.build_hold_decision(view, now_ns=2_000)

    cases.append(assert_case(
        "build_hold_decision_is_hold_qty_zero_report_only",
        decision["action"] == S.ACTION_HOLD
        and decision["qty"] == 0
        and decision["hold_only"] == 1
        and decision["activation_report_only"] == 1
        and decision["activation_promoted"] == 0
        and decision["activation_safe_to_promote"] == 0,
        {
            "action": decision["action"],
            "qty": decision["qty"],
            "hold_only": decision["hold_only"],
            "activation_promoted": decision["activation_promoted"],
        },
    ))

    service = S.StrategyService(
        redis_client=redis,
        clock=FakeClock(),
        shutdown=FakeShutdown(),
        instance_id="proof-strategy",
    )
    service.publish_decision(decision)

    published = redis.xadds[-1]
    fields = published["fields"]
    payload = json.loads(fields["payload_json"])

    cases.append(assert_case(
        "publish_decision_writes_payload_json_with_matching_hold_action_qty",
        fields["action"] == S.ACTION_HOLD
        and int(fields["qty"]) == 0
        and payload["action"] == S.ACTION_HOLD
        and int(payload["qty"]) == 0
        and payload["hold_only"] == 1,
        {
            "flat_action": fields.get("action"),
            "payload_action": payload.get("action"),
            "flat_qty": fields.get("qty"),
            "payload_qty": payload.get("qty"),
        },
    ))

    try:
        service.publish_decision({
            "action": "ENTER_CALL",
            "qty": 1,
            "hold_only": 0,
            "activation_report_only": 0,
            "activation_action": "ENTER_CALL",
            "activation_promoted": 1,
            "activation_safe_to_promote": 1,
        })
        rejected_non_hold = False
    except S.StrategyBridgeError:
        rejected_non_hold = True

    cases.append(assert_case(
        "publish_decision_rejects_non_hold",
        rejected_non_hold is True,
    ))

    try:
        service.publish_decision({
            "action": S.ACTION_HOLD,
            "qty": 1,
            "hold_only": 1,
            "activation_report_only": 1,
            "activation_action": S.ACTION_HOLD,
            "activation_promoted": 0,
            "activation_safe_to_promote": 0,
        })
        rejected_nonzero_qty = False
    except S.StrategyBridgeError:
        rejected_nonzero_qty = True

    cases.append(assert_case(
        "publish_decision_rejects_hold_with_nonzero_qty",
        rejected_nonzero_qty is True,
    ))

    try:
        service.publish_decision({
            "action": S.ACTION_HOLD,
            "qty": 0,
            "hold_only": 1,
            "activation_report_only": 1,
            "activation_action": S.ACTION_HOLD,
            "activation_promoted": 1,
            "activation_safe_to_promote": 0,
        })
        rejected_promoted = False
    except S.StrategyBridgeError:
        rejected_promoted = True

    cases.append(assert_case(
        "publish_decision_rejects_promoted_hold_payload",
        rejected_promoted is True,
    ))

    override_fields = S._redis_stream_fields({
        "payload_json": json.dumps({"action": "ENTER_CALL", "qty": 999}),
        "action": S.ACTION_HOLD,
        "qty": 0,
        "hold_only": 1,
        "activation_report_only": 1,
        "activation_action": S.ACTION_HOLD,
        "activation_promoted": 0,
        "activation_safe_to_promote": 0,
    })
    override_payload = json.loads(override_fields["payload_json"])

    cases.append(assert_case(
        "incoming_payload_json_field_cannot_override_canonical_payload_action",
        override_payload["action"] == S.ACTION_HOLD
        and int(override_payload["qty"]) == 0
        and isinstance(override_payload.get("payload_json"), str),
        {
            "payload_action": override_payload.get("action"),
            "payload_qty": override_payload.get("qty"),
            "nested_payload_json_present": "payload_json" in override_payload,
        },
    ))

    malformed_bridge = S.StrategyFamilyConsumerBridge(
        redis_client=FakeRedis({
            "family_features_json": "{not-json",
            "family_surfaces_json": "{}",
            "family_frames_json": "{}",
        })
    )
    try:
        malformed_bridge.read_feature_bundle()
        malformed_visible = False
        malformed_message = ""
    except S.StrategyBridgeError as exc:
        malformed_visible = "family_features_json invalid json" in str(exc)
        malformed_message = str(exc)

    cases.append(assert_case(
        "read_feature_bundle_does_not_mask_invalid_json_as_empty_hash",
        malformed_visible is True,
        {"error": malformed_message},
    ))

    class FakeActivationDecision:
        def to_dict(self) -> dict[str, Any]:
            return {
                "activation_mode": "dry_run",
                "action": "ENTER_CALL",
                "hold": False,
                "promoted": True,
                "safe_to_promote": True,
                "reason": "proof_forced_promotion",
                "selected": {
                    "family_id": FF_C.FAMILY_ID_MISO,
                    "branch_id": FF_C.BRANCH_CALL,
                    "action": "ENTER_CALL",
                    "score": 0.99,
                },
                "candidates": [],
                "blocked": [],
                "no_signal": [],
            }

    original_activation_fn = S.SF_ACT.build_activation_decision
    S.SF_ACT.build_activation_decision = lambda view, config: FakeActivationDecision()
    try:
        clamp_report = bridge.build_activation_report(view, now_ns=3_000)
    finally:
        S.SF_ACT.build_activation_decision = original_activation_fn

    cases.append(assert_case(
        "activation_report_clamps_future_promoted_enter_to_hold",
        clamp_report["action"] == S.ACTION_HOLD
        and clamp_report["promoted"] is False
        and clamp_report["safe_to_promote"] is False
        and clamp_report["strategy_clamp"] == "forced_hold_report_only"
        and clamp_report["observed_action_before_strategy_clamp"] == "ENTER_CALL"
        and clamp_report["live_orders_allowed"] is False,
        clamp_report,
    ))

    err_redis = FakeRedis()
    err_service = S.StrategyService(
        redis_client=err_redis,
        clock=FakeClock(),
        shutdown=FakeShutdown(),
        instance_id="proof-strategy",
    )
    err_service.publish_error(where="proof", exc=RuntimeError("boom"))
    err_fields = err_redis.xadds[-1]["fields"]

    cases.append(assert_case(
        "publish_error_includes_ts_event_ns",
        "ts_ns" in err_fields
        and "ts_event_ns" in err_fields
        and err_fields["ts_ns"] == err_fields["ts_event_ns"],
        err_fields,
    ))

    service_redis = FakeRedis(valid_hash)
    run_service = S.StrategyService(
        redis_client=service_redis,
        clock=FakeClock(),
        shutdown=FakeShutdown(),
        instance_id="proof-strategy",
    )
    run_decision = run_service.run_once()

    cases.append(assert_case(
        "run_once_publishes_one_hold_decision_only",
        len(service_redis.xadds) == 1
        and run_decision["action"] == S.ACTION_HOLD
        and run_decision["qty"] == 0
        and run_decision["hold_only"] == 1,
        {
            "xadd_count": len(service_redis.xadds),
            "action": run_decision.get("action"),
            "qty": run_decision.get("qty"),
        },
    ))

    proof = {
        "proof_name": "strategy_hold_bridge_contract",
        "status": "PASS",
        "ts_epoch": time.time(),
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "hold_only_publication_guard": True,
            "payload_json_flat_action_match": True,
            "invalid_json_not_masked": True,
            "activation_promotion_clamped": True,
            "publish_error_has_ts_event_ns": True,
            "run_once_hold_only": True,
        },
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(proof["summary"], indent=2, sort_keys=True))
    print(f"proof_artifact={PROOF_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
