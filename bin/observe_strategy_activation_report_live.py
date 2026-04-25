#!/usr/bin/env python3
from __future__ import annotations

"""
Rolling live-feature observation harness for strategy.py activation report-only mode.

Purpose
-------
Repeatedly read the latest Redis feature hash, build the strategy HOLD decision,
extract activation report metadata, and record a JSONL audit trail.

Safety law
----------
This script does not publish decisions.
This script does not call broker/execution.
This script does not place orders.
This script fails immediately if strategy.py returns anything other than HOLD
or if activation promotion/live-orders appear enabled.
"""

import argparse
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.mme_scalpx.services import strategy  # noqa: E402
from bin.proof_strategy_activation_report_redis_smoke import (  # noqa: E402
    _read_feature_hash,
    _safe_str,
    make_redis_client,
)


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        try:
            return _jsonable(value.to_dict())
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return _jsonable(vars(value))
    return str(value)


def _json_loads_field(value: Any) -> dict[str, Any]:
    text = _safe_str(value)
    if not text:
        return {}
    try:
        out = json.loads(text)
    except Exception:
        return {"_parse_error": text[:500]}
    return out if isinstance(out, dict) else {"_value": out}


def _assert_hold_safe(decision: Mapping[str, Any], activation_report: Mapping[str, Any]) -> None:
    if _safe_str(decision.get("action")) != strategy.ACTION_HOLD:
        raise RuntimeError(f"strategy decision action drifted from HOLD: {decision.get('action')!r}")

    if str(decision.get("qty")) != "0":
        raise RuntimeError(f"strategy decision qty drifted from 0: {decision.get('qty')!r}")

    if str(decision.get("hold_only")) not in {"1", "True", "true"}:
        raise RuntimeError(f"strategy decision hold_only invalid: {decision.get('hold_only')!r}")

    if str(decision.get("activation_promoted")) not in {"0", "False", "false"}:
        raise RuntimeError(f"activation_promoted drifted: {decision.get('activation_promoted')!r}")

    if str(decision.get("activation_safe_to_promote")) not in {"0", "False", "false"}:
        raise RuntimeError(f"activation_safe_to_promote drifted: {decision.get('activation_safe_to_promote')!r}")

    if activation_report:
        if activation_report.get("promoted") is True:
            raise RuntimeError("activation_report.promoted became True")
        if activation_report.get("safe_to_promote") is True:
            raise RuntimeError("activation_report.safe_to_promote became True")
        if activation_report.get("live_orders_allowed") is True:
            raise RuntimeError("activation_report.live_orders_allowed became True")


def _observe_once(client: Any, bridge: Any) -> dict[str, Any]:
    feature_hash = _read_feature_hash(client)
    now_ns = time.time_ns()

    if not feature_hash:
        return {
            "ts_ns": now_ns,
            "skipped": True,
            "reason": "feature_hash_empty",
            "hash_key": strategy.HASH_FEATURES,
        }

    bundle = bridge._bundle_from_hash(feature_hash)
    view = bridge.build_consumer_view(bundle, now_ns=now_ns)
    decision = bridge.build_hold_decision(view, now_ns=now_ns)

    activation_report = _json_loads_field(decision.get("activation_report_json"))
    diagnostics = _json_loads_field(decision.get("diagnostics_json"))

    _assert_hold_safe(decision, activation_report)

    selected = activation_report.get("selected")
    selected = selected if isinstance(selected, dict) else {}

    row = {
        "ts_ns": now_ns,
        "skipped": False,
        "hash_key": strategy.HASH_FEATURES,
        "feature_hash_field_count": len(feature_hash),
        "feature_frame_id": bundle.feature_frame_id,
        "feature_frame_ts_ns": bundle.feature_frame_ts_ns,
        "safe_to_consume": view.safe_to_consume,
        "data_valid": view.data_valid,
        "warmup_complete": view.warmup_complete,
        "provider_ready_classic": view.provider_ready_classic,
        "provider_ready_miso": view.provider_ready_miso,
        "regime": view.regime,
        "family_ids": list(view.family_status.keys()),
        "branch_frame_count": len(view.branch_frames),
        "decision_action": decision.get("action"),
        "qty": decision.get("qty"),
        "hold_only": decision.get("hold_only"),
        "activation_mode": decision.get("activation_mode"),
        "activation_reason": decision.get("activation_reason"),
        "activation_candidate_count": decision.get("activation_candidate_count"),
        "activation_selected_family_id": decision.get("activation_selected_family_id"),
        "activation_selected_branch_id": decision.get("activation_selected_branch_id"),
        "activation_selected_action": decision.get("activation_selected_action"),
        "activation_selected_score": decision.get("activation_selected_score"),
        "activation_promoted": decision.get("activation_promoted"),
        "activation_safe_to_promote": decision.get("activation_safe_to_promote"),
        "activation_report_reason": activation_report.get("reason"),
        "activation_report_selected_family_id": selected.get("family_id"),
        "activation_report_selected_branch_id": selected.get("branch_id"),
        "activation_report_selected_action": selected.get("action"),
        "activation_report_candidate_count": len(activation_report.get("candidates") or []),
        "activation_report_blocked_count": len(activation_report.get("blocked") or []),
        "activation_report_no_signal_count": len(activation_report.get("no_signal") or []),
        "live_orders_allowed": activation_report.get("live_orders_allowed"),
        "doctrine_leaves_observed": diagnostics.get("doctrine_leaves_observed"),
        "doctrine_leaves_active": diagnostics.get("doctrine_leaves_active"),
        "broker_side_effects_allowed": diagnostics.get("broker_side_effects_allowed"),
    }
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--interval-sec", type=float, default=5.0)
    parser.add_argument("--strict", action="store_true", help="Fail if all samples are skipped.")
    args = parser.parse_args()

    samples = max(int(args.samples), 1)
    interval = max(float(args.interval_sec), 0.0)

    client = make_redis_client()
    bridge = strategy.StrategyFamilyConsumerBridge(redis_client=client)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    jsonl_path = PROJECT_ROOT / f"run/proofs/strategy_activation_report_observe_{stamp}.jsonl"
    summary_path = PROJECT_ROOT / "run/proofs/strategy_activation_report_observe_summary.json"

    rows: list[dict[str, Any]] = []

    print("===== STRATEGY ACTIVATION REPORT LIVE OBSERVATION =====")
    print("hash_key =", strategy.HASH_FEATURES)
    print("samples =", samples)
    print("interval_sec =", interval)
    print("jsonl =", jsonl_path.relative_to(PROJECT_ROOT))

    with jsonl_path.open("w", encoding="utf-8") as fh:
        for i in range(samples):
            row = _observe_once(client, bridge)
            row["sample_index"] = i + 1
            rows.append(row)
            fh.write(json.dumps(_jsonable(row), ensure_ascii=False, sort_keys=False) + "\n")
            fh.flush()

            print(
                "sample={idx} skipped={skipped} action={action} reason={reason} "
                "candidates={candidates} selected={family}/{branch} promoted={promoted}".format(
                    idx=i + 1,
                    skipped=row.get("skipped"),
                    action=row.get("decision_action", ""),
                    reason=row.get("activation_reason", row.get("reason", "")),
                    candidates=row.get("activation_candidate_count", ""),
                    family=row.get("activation_selected_family_id", ""),
                    branch=row.get("activation_selected_branch_id", ""),
                    promoted=row.get("activation_promoted", ""),
                )
            )

            if i < samples - 1 and interval > 0:
                time.sleep(interval)

    usable = [row for row in rows if not row.get("skipped")]
    selected_counter = Counter(
        f"{row.get('activation_selected_family_id')}/{row.get('activation_selected_branch_id')}"
        for row in usable
        if row.get("activation_selected_family_id")
    )
    reason_counter = Counter(str(row.get("activation_reason", "")) for row in usable)

    summary = {
        "proof_name": "strategy_activation_report_live_observer",
        "proof_scope": "HOLD_REPORT_ONLY_LIVE_OBSERVATION",
        "activation_ready": False,
        "paper_armed_ready": False,
        "writes_live_redis": False,
        "uses_broker": False,
        "places_orders": False,
        "does_not_prove": [
            "candidate_quality",
            "provider_token_equivalence",
            "Dhan context truth",
            "execution_metadata_completeness",
            "risk_exit_never_blocked",
            "order_intent_validity",
            "MISC/MISR event sequencing",
            "MISO chain/live distinction",
        ],
        "hash_key": strategy.HASH_FEATURES,
        "samples_requested": samples,
        "samples_total": len(rows),
        "samples_usable": len(usable),
        "samples_skipped": len(rows) - len(usable),
        "all_hold": all(row.get("decision_action") == strategy.ACTION_HOLD for row in usable),
        "all_qty_zero": all(str(row.get("qty")) == "0" for row in usable),
        "all_not_promoted": all(str(row.get("activation_promoted")) in {"0", "False", "false"} for row in usable),
        "all_live_orders_disabled": all(row.get("live_orders_allowed") is False for row in usable),
        "selected_counter": dict(selected_counter),
        "reason_counter": dict(reason_counter),
        "jsonl_path": str(jsonl_path.relative_to(PROJECT_ROOT)),
        "ts_ns": time.time_ns(),
    }

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")

    print()
    print("===== SUMMARY =====")
    print("samples_total =", summary["samples_total"])
    print("samples_usable =", summary["samples_usable"])
    print("samples_skipped =", summary["samples_skipped"])
    print("all_hold =", summary["all_hold"])
    print("all_qty_zero =", summary["all_qty_zero"])
    print("all_not_promoted =", summary["all_not_promoted"])
    print("all_live_orders_disabled =", summary["all_live_orders_disabled"])
    print("proof_scope =", summary["proof_scope"])
    print("activation_ready =", summary["activation_ready"])
    print("paper_armed_ready =", summary["paper_armed_ready"])
    print("selected_counter =", summary["selected_counter"])
    print("reason_counter =", summary["reason_counter"])
    print("summary =", summary_path.relative_to(PROJECT_ROOT))

    if args.strict and not usable:
        raise SystemExit("strict mode failed: no usable feature-hash samples")

    if usable and not (
        summary["all_hold"]
        and summary["all_qty_zero"]
        and summary["all_not_promoted"]
        and summary["all_live_orders_disabled"]
    ):
        raise SystemExit("HOLD/report-only safety invariant failed")

    print("strategy activation report live observation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
