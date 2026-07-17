#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from decimal import Decimal
from pathlib import Path

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family.position_exit_manager import (
    ELIGIBLE_FAMILIES,
    POLICY_VERSION,
    ExitPolicy,
    PositionExitManager,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = (
    ROOT
    / "app/mme_scalpx/services/strategy_family/"
      "position_exit_manager.py"
)
OUT = (
    ROOT
    / "run/proofs/"
      "proof_r38tk_position_exit_manager_offline.json"
)


def position(
    *,
    entry_price: str = "100",
    entry_ts_ns: int = 1_000_000_000,
) -> dict[str, object]:
    return {
        "has_position": "1",
        "position_side": "LONG_CALL",
        "qty_lots": "1",
        "qty_units": "65",
        "avg_price": entry_price,
        "entry_ts_ns": str(entry_ts_ns),
        "entry_option_symbol":
            "NIFTY2671424100CE",
        "entry_option_token": "13152002",
        "entry_strike": "24100",
        "entry_mode": "DIRECT",
        "decision_id": "proof-entry",
        "broker_order_id": "proof-order",
    }


def quote(
    *,
    bid: str,
    ask: str,
    ts_ns: int,
    symbol: str = "NIFTY2671424100CE",
    token: str = "13152002",
) -> dict[str, object]:
    return {
        "option_symbol": symbol,
        "option_token": token,
        "bid": bid,
        "ask": ask,
        "ts_event_ns": str(ts_ns),
    }


def assert_exit(
    result,
    *,
    reason: str,
    priority: str,
    bid: str,
) -> dict:
    assert result.should_exit is True, result
    assert result.blocked is False, result
    assert result.reason_code == reason, result
    assert result.exit_priority == priority, result
    assert result.decision is not None, result

    payload = result.decision.to_dict()

    assert payload["action"] == N.ACTION_EXIT, payload
    assert payload["position_effect"] == (
        N.POSITION_EFFECT_CLOSE
    ), payload
    assert payload["quantity_lots"] == 1, payload
    assert payload["instrument_key"] == "13152002", payload
    assert payload["strategy_family_id"] == "MIST", payload
    assert payload["doctrine_id"] == "MIST", payload
    assert payload["branch_id"] == N.BRANCH_CALL, payload

    metadata = payload["metadata"]

    assert metadata["reason_code"] == reason, metadata
    assert metadata["exit_priority"] == priority, metadata
    assert metadata["option_symbol"] == (
        "NIFTY2671424100CE"
    ), metadata
    assert metadata["option_token"] == "13152002", metadata
    assert Decimal(
        str(metadata["limit_price"])
    ) == Decimal(bid), metadata
    assert metadata["exit_policy_version"] == (
        POLICY_VERSION
    ), metadata
    assert metadata["no_real_live"] is True, metadata
    assert metadata["no_broker_order"] is True, metadata

    return payload


def main() -> int:
    policy = ExitPolicy()
    policy.validate()

    assert policy.target_points == Decimal("5")
    assert policy.stop_points == Decimal("4")
    assert policy.max_hold_sec == Decimal("300")
    assert policy.signal_change_enabled is False

    assert ELIGIBLE_FAMILIES == {
        "MIST",
        "MISB",
        "MISC",
        "MISR",
    }

    results: dict[str, object] = {}

    # No position must block.
    manager = PositionExitManager()

    no_position = manager.evaluate(
        now_ns=2_000_000_000,
        family_id="MIST",
        position={
            "has_position": "0",
            "position_side": "FLAT",
        },
        quote={},
    )

    assert no_position.blocked
    assert no_position.reason_code == "no_open_position"
    results["no_position"] = no_position.to_dict()

    # Exact symbol mismatch must block.
    manager = PositionExitManager()

    mismatch = manager.evaluate(
        now_ns=2_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="105",
            ask="105.10",
            ts_ns=2_000_000_000,
            symbol="NIFTY2671424000CE",
        ),
    )

    assert mismatch.blocked
    assert mismatch.reason_code == (
        "exit_quote_symbol_mismatch"
    )
    results["symbol_mismatch"] = mismatch.to_dict()

    # Stale quote must block.
    manager = PositionExitManager()

    stale = manager.evaluate(
        now_ns=10_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="105",
            ask="105.10",
            ts_ns=1_000_000_000,
        ),
    )

    assert stale.blocked
    assert stale.reason_code == "exit_quote_stale"
    results["stale_quote"] = stale.to_dict()

    # Neutral position remains HOLD.
    manager = PositionExitManager()

    hold = manager.evaluate(
        now_ns=30_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="101",
            ask="101.10",
            ts_ns=30_000_000_000,
        ),
    )

    assert not hold.should_exit
    assert not hold.blocked
    assert hold.reason_code == "position_hold"
    assert hold.decision is None
    results["hold"] = hold.to_dict()

    # Target exit uses the exact BID.
    manager = PositionExitManager()

    target = manager.evaluate(
        now_ns=30_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="105",
            ask="105.10",
            ts_ns=30_000_000_000,
        ),
    )

    results["target"] = assert_exit(
        target,
        reason="target_points",
        priority="P0_TARGET",
        bid="105",
    )

    # Hard stop follows target and precedes structural/time exits.
    manager = PositionExitManager()

    stop = manager.evaluate(
        now_ns=30_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="96",
            ask="96.10",
            ts_ns=30_000_000_000,
        ),
    )

    results["hard_stop"] = assert_exit(
        stop,
        reason="hard_stop_points",
        priority="P1_HARD_STOP",
        bid="96",
    )

    # Maximum hold exits at a fresh BID.
    manager = PositionExitManager()

    time_stop = manager.evaluate(
        now_ns=301_000_000_000,
        family_id="MIST",
        position=position(
            entry_ts_ns=1_000_000_000,
        ),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=301_000_000_000,
        ),
    )

    results["time_stop"] = assert_exit(
        time_stop,
        reason="max_hold_seconds",
        priority="P3_TIME_STOP",
        bid="100.50",
    )

    # Signal change is deliberately disabled.
    manager = PositionExitManager()

    signal_disabled_1 = manager.evaluate(
        now_ns=30_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=30_000_000_000,
        ),
        signal_changed=True,
    )

    signal_disabled_2 = manager.evaluate(
        now_ns=31_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=31_000_000_000,
        ),
        signal_changed=True,
    )

    assert not signal_disabled_1.should_exit
    assert not signal_disabled_2.should_exit
    assert signal_disabled_2.reason_code == "position_hold"

    results["signal_change_disabled"] = (
        signal_disabled_2.to_dict()
    )

    # Enabled structural exit requires two confirmed samples.
    structural_policy = ExitPolicy(
        signal_change_enabled=True,
    )
    manager = PositionExitManager(
        policy=structural_policy,
    )

    structural_sample_1 = manager.evaluate(
        now_ns=30_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=30_000_000_000,
        ),
        signal_changed=True,
    )

    assert not structural_sample_1.should_exit

    structural_sample_2 = manager.evaluate(
        now_ns=31_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=31_000_000_000,
        ),
        signal_changed=True,
    )

    results["structural_exit"] = assert_exit(
        structural_sample_2,
        reason="confirmed_signal_change",
        priority="P2_STRUCTURAL_EXIT",
        bid="100.50",
    )

    # Structural exit must beat the 300-second time exit.
    manager = PositionExitManager(
        policy=structural_policy,
    )

    structural_time_sample_1 = manager.evaluate(
        now_ns=300_000_000_000,
        family_id="MIST",
        position=position(
            entry_ts_ns=1_000_000_000,
        ),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=300_000_000_000,
        ),
        signal_changed=True,
    )

    assert not structural_time_sample_1.should_exit

    structural_time_overlap = manager.evaluate(
        now_ns=301_000_000_000,
        family_id="MIST",
        position=position(
            entry_ts_ns=1_000_000_000,
        ),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=301_000_000_000,
        ),
        signal_changed=True,
    )

    results["structural_beats_time"] = assert_exit(
        structural_time_overlap,
        reason="confirmed_signal_change",
        priority="P2_STRUCTURAL_EXIT",
        bid="100.50",
    )

    # Target must beat an otherwise confirmed structural exit.
    manager = PositionExitManager(
        policy=structural_policy,
    )

    manager.evaluate(
        now_ns=30_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=30_000_000_000,
        ),
        signal_changed=True,
    )

    target_structural_overlap = manager.evaluate(
        now_ns=31_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="105",
            ask="105.10",
            ts_ns=31_000_000_000,
        ),
        signal_changed=True,
    )

    results["target_beats_structural"] = assert_exit(
        target_structural_overlap,
        reason="target_points",
        priority="P0_TARGET",
        bid="105",
    )

    # Hard stop must beat an otherwise confirmed structural exit.
    manager = PositionExitManager(
        policy=structural_policy,
    )

    manager.evaluate(
        now_ns=30_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="100.50",
            ask="100.60",
            ts_ns=30_000_000_000,
        ),
        signal_changed=True,
    )

    stop_structural_overlap = manager.evaluate(
        now_ns=31_000_000_000,
        family_id="MIST",
        position=position(),
        quote=quote(
            bid="96",
            ask="96.10",
            ts_ns=31_000_000_000,
        ),
        signal_changed=True,
    )

    results["hard_stop_beats_structural"] = assert_exit(
        stop_structural_overlap,
        reason="hard_stop_points",
        priority="P1_HARD_STOP",
        bid="96",
    )

    # MFE and MAE must track the same exact position.
    manager = PositionExitManager()

    sequence = [
        ("102", "102.10", 10_000_000_000),
        ("98", "98.10", 11_000_000_000),
        ("103", "103.10", 12_000_000_000),
    ]

    sequence_results = []

    for bid, ask, now_ns in sequence:
        result = manager.evaluate(
            now_ns=now_ns,
            family_id="MIST",
            position=position(),
            quote=quote(
                bid=bid,
                ask=ask,
                ts_ns=now_ns,
            ),
        )
        sequence_results.append(result.to_dict())

    assert manager.tracker.mfe_points == Decimal("3")
    assert manager.tracker.mae_points == Decimal("-2")

    results["mfe_mae_sequence"] = sequence_results

    # Static purity check.
    source = MODULE.read_text()
    tree = ast.parse(source)

    forbidden_imports = {
        "redis",
        "kiteconnect",
        "dhanhq",
    }

    seen_forbidden = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in forbidden_imports:
                    seen_forbidden.append(alias.name)

        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in forbidden_imports:
                seen_forbidden.append(module)

    assert not seen_forbidden, seen_forbidden

    forbidden_calls = {
        "xadd",
        "hset",
        "place_entry_order",
        "place_exit_order",
        "orders",
        "positions",
    }

    called = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)
            elif isinstance(node.func, ast.Name):
                called.add(node.func.id)

    assert not (
        called & forbidden_calls
    ), sorted(called & forbidden_calls)

    report = {
        "classification":
            "PASS_R38TK3_EXIT_PRIORITY_TIMING_CONTRACT_OFFLINE",
        "policy_version": POLICY_VERSION,
        "eligible_families":
            sorted(ELIGIBLE_FAMILIES),
        "target_points":
            str(policy.target_points),
        "stop_points":
            str(policy.stop_points),
        "max_hold_sec":
            str(policy.max_hold_sec),
        "signal_change_enabled":
            policy.signal_change_enabled,
        "exit_priority_order": [
            "TARGET",
            "HARD_STOP",
            "STRUCTURAL_EXIT",
            "TIME_EXIT",
        ],
        "pure_no_redis_broker_calls": True,
        "scenario_count": len(results),
        "results": results,
    }

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUT.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
    )

    print(
        "CLASSIFICATION="
        "PASS_R38TK3_EXIT_PRIORITY_TIMING_CONTRACT_OFFLINE"
    )
    print("TARGET_POINTS=5")
    print("STOP_POINTS=4")
    print("MAX_HOLD_SEC=300")
    print("SIGNAL_CHANGE_EXIT_DEFAULT=DISABLED")
    print("STRUCTURAL_EXIT_WHEN_ENABLED=PASS")
    print("EXIT_PRIORITY=TARGET,HARD_STOP,STRUCTURAL_EXIT,TIME_EXIT")
    print("PURE_NO_REDIS_BROKER_CALLS=1")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
