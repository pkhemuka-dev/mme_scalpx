#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.execution import (
    ExecutionService,
)
from app.mme_scalpx.services.strategy_family.position_exit_manager import (
    ELIGIBLE_FAMILIES,
    POLICY_VERSION,
    PositionExitManager,
)


ROOT = Path(__file__).resolve().parents[1]

MANAGER_PATH = (
    ROOT
    / "app/mme_scalpx/services/strategy_family/"
      "position_exit_manager.py"
)

EXECUTION_PATH = (
    ROOT
    / "app/mme_scalpx/services/execution.py"
)

OUTPUT = (
    ROOT
    / "run/proofs/"
      "proof_r38tk2_exit_execution_contract_offline.json"
)


def make_position(
    *,
    side: str,
    symbol: str,
    token: str,
    entry_price: str = "100",
    entry_ts_ns: int = 1_000_000_000,
) -> dict[str, Any]:
    branch = (
        "CALL"
        if side == "LONG_CALL"
        else "PUT"
    )

    return {
        "has_position": "1",
        "position_side": side,
        "qty_lots": "1",
        "qty_units": "65",
        "avg_price": entry_price,
        "entry_ts_ns": str(entry_ts_ns),
        "entry_option_symbol": symbol,
        "entry_option_token": token,
        "entry_strike": "24100",
        "entry_mode": "DIRECT",
        "decision_id": "proof-entry",
        "broker_order_id": "proof-entry-order",
        "strategy_family_id": "MIST",
        "branch_id": branch,
    }


def make_quote(
    *,
    symbol: str,
    token: str,
    bid: str,
    ask: str,
    now_ns: int,
) -> dict[str, Any]:
    return {
        "option_symbol": symbol,
        "option_token": token,
        "bid": bid,
        "ask": ask,
        "ts_event_ns": str(now_ns),
    }


def parse_through_execution(
    payload: dict[str, Any],
    *,
    sequence: int,
):
    fields = {
        "decision_id":
            payload["decision_id"],
        "action":
            payload["action"],
        "ts_ns":
            str(payload["ts_event_ns"]),
        "payload_json":
            json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
            ),
    }

    parsed = ExecutionService._parse_decision(
        object(),
        f"{sequence}-0",
        fields,
    )

    return parsed, fields


def evaluate_exit(
    *,
    now_ns: int,
    position: dict[str, Any],
    quote: dict[str, Any],
    expected_reason: str,
    sequence: int,
) -> dict[str, Any]:
    manager = PositionExitManager()

    result = manager.evaluate(
        now_ns=now_ns,
        family_id="MIST",
        position=position,
        quote=quote,
        signal_changed=False,
    )

    assert result.blocked is False, result
    assert result.should_exit is True, result
    assert result.reason_code == expected_reason, result
    assert result.decision is not None, result

    payload = result.decision.to_dict()

    assert payload["action"] == N.ACTION_EXIT, payload
    assert payload["position_effect"] == (
        N.POSITION_EFFECT_CLOSE
    ), payload
    assert payload["quantity_lots"] == 1, payload
    assert payload["strategy_family_id"] == "MIST", payload
    assert payload["branch_id"] in {
        N.BRANCH_CALL,
        N.BRANCH_PUT,
    }, payload

    parsed, fields = parse_through_execution(
        payload,
        sequence=sequence,
    )

    assert parsed.action == N.ACTION_EXIT, parsed
    assert parsed.position_effect == (
        N.POSITION_EFFECT_CLOSE
    ), parsed
    assert parsed.quantity_lots == 1, parsed
    assert parsed.instrument_key == (
        payload["instrument_key"]
    ), parsed
    assert parsed.strategy_family_id == "MIST", parsed
    assert parsed.branch_id == payload["branch_id"], parsed
    assert parsed.reason_code == expected_reason, parsed

    return {
        "payload": payload,
        "parsed": {
            "action": parsed.action,
            "position_effect":
                parsed.position_effect,
            "quantity_lots":
                parsed.quantity_lots,
            "instrument_key":
                parsed.instrument_key,
            "strategy_family_id":
                parsed.strategy_family_id,
            "branch_id":
                parsed.branch_id,
            "reason_code":
                parsed.reason_code,
        },
        "stream_fields": fields,
    }


def main() -> int:
    assert POLICY_VERSION == (
        "R38TK3_FAMILY_CONTRACT_EXIT_V3_TARGET_STOP_STRUCTURAL_TIME"
    )

    assert ELIGIBLE_FAMILIES == {
        "MIST",
        "MISB",
        "MISC",
        "MISR",
    }

    call_symbol = "NIFTY2671424100CE"
    call_token = "13152002"

    put_symbol = "NIFTY2671424100PE"
    put_token = "13152258"

    target_now = 30_000_000_000

    target_call = evaluate_exit(
        now_ns=target_now,
        position=make_position(
            side="LONG_CALL",
            symbol=call_symbol,
            token=call_token,
        ),
        quote=make_quote(
            symbol=call_symbol,
            token=call_token,
            bid="105",
            ask="105.10",
            now_ns=target_now,
        ),
        expected_reason="target_points",
        sequence=1,
    )

    stop_call = evaluate_exit(
        now_ns=target_now,
        position=make_position(
            side="LONG_CALL",
            symbol=call_symbol,
            token=call_token,
        ),
        quote=make_quote(
            symbol=call_symbol,
            token=call_token,
            bid="96",
            ask="96.10",
            now_ns=target_now,
        ),
        expected_reason="hard_stop_points",
        sequence=2,
    )

    time_now = 301_000_000_000

    time_call = evaluate_exit(
        now_ns=time_now,
        position=make_position(
            side="LONG_CALL",
            symbol=call_symbol,
            token=call_token,
            entry_ts_ns=1_000_000_000,
        ),
        quote=make_quote(
            symbol=call_symbol,
            token=call_token,
            bid="100.50",
            ask="100.60",
            now_ns=time_now,
        ),
        expected_reason="max_hold_seconds",
        sequence=3,
    )

    target_put = evaluate_exit(
        now_ns=target_now,
        position=make_position(
            side="LONG_PUT",
            symbol=put_symbol,
            token=put_token,
        ),
        quote=make_quote(
            symbol=put_symbol,
            token=put_token,
            bid="105",
            ask="105.10",
            now_ns=target_now,
        ),
        expected_reason="target_points",
        sequence=4,
    )

    manager = PositionExitManager()

    hold = manager.evaluate(
        now_ns=target_now,
        family_id="MIST",
        position=make_position(
            side="LONG_CALL",
            symbol=call_symbol,
            token=call_token,
        ),
        quote=make_quote(
            symbol=call_symbol,
            token=call_token,
            bid="101",
            ask="101.10",
            now_ns=target_now,
        ),
    )

    assert hold.blocked is False, hold
    assert hold.should_exit is False, hold
    assert hold.reason_code == "position_hold", hold
    assert hold.decision is None, hold

    manager_source = MANAGER_PATH.read_text()
    execution_source = EXECUTION_PATH.read_text()

    ast.parse(manager_source)
    ast.parse(execution_source)

    assert (
        "POSITION_EFFECT_FLATTEN"
        not in manager_source
    )
    assert (
        "POSITION_EFFECT_CLOSE"
        in manager_source
    )

    assert (
        "R38TH_CANONICAL_PAPER_EXIT_ADAPTER_CONTRACT"
        in execution_source
    )
    assert (
        "R38TH_EXIT_FILL_QUANTITY_FAIL_CLOSED"
        in execution_source
    )

    forbidden_manager_tokens = {
        "place_entry_order(",
        "place_exit_order(",
        ".xadd(",
        ".hset(",
        "import redis",
    }

    present_forbidden = sorted(
        token
        for token in forbidden_manager_tokens
        if token in manager_source
    )

    assert not present_forbidden, present_forbidden

    report = {
        "classification":
            "PASS_R38TK3_EXIT_PRIORITY_EXECUTION_CONTRACT_OFFLINE",
        "policy_version": POLICY_VERSION,
        "position_effect":
            N.POSITION_EFFECT_CLOSE,
        "execution_parser_accepts_exit": True,
        "target_call": target_call,
        "hard_stop_call": stop_call,
        "time_stop_call": time_call,
        "target_put": target_put,
        "hold_has_no_decision": True,
        "manager_pure_no_redis_broker_calls": True,
        "runtime_started": False,
        "order_attempted": False,
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        "CLASSIFICATION="
        "PASS_R38TK3_EXIT_PRIORITY_EXECUTION_CONTRACT_OFFLINE"
    )
    print(
        "POLICY_VERSION="
        + POLICY_VERSION
    )
    print(
        "POSITION_EFFECT="
        + N.POSITION_EFFECT_CLOSE
    )
    print(
        "TARGET_CALL_EXECUTION_PARSE=PASS"
    )
    print(
        "HARD_STOP_CALL_EXECUTION_PARSE=PASS"
    )
    print(
        "TIME_STOP_CALL_EXECUTION_PARSE=PASS"
    )
    print(
        "TARGET_PUT_EXECUTION_PARSE=PASS"
    )
    print(
        "HOLD_DECISION_SUPPRESSED=PASS"
    )
    print(
        "PURE_NO_REDIS_BROKER_CALLS=1"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
