#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.execution import (
    ExecutionService,
    PendingOrder,
)
from app.mme_scalpx.services.strategy_family.position_exit_manager import (
    POLICY_VERSION,
    PositionExitManager,
)


ROOT = Path(__file__).resolve().parents[1]

EXECUTION_PATH = (
    ROOT
    / "app/mme_scalpx/services/execution.py"
)

OUTPUT = (
    ROOT
    / "run/proofs/"
      "proof_r38tma1_execution_ownership_offline.json"
)


def build_exit_payload() -> dict[str, Any]:
    now_ns = 30_000_000_000

    manager = PositionExitManager()

    evaluation = manager.evaluate(
        now_ns=now_ns,
        family_id="MIST",
        position={
            "has_position": "1",
            "position_side": "LONG_CALL",
            "qty_lots": "1",
            "qty_units": "65",
            "avg_price": "100",
            "entry_ts_ns": "1000000000",
            "entry_option_symbol":
                "NIFTY2671424100CE",
            "entry_option_token": "13152002",
            "entry_strike": "24100",
            "entry_mode": "DIRECT",
            "strategy_family_id": "MIST",
            "branch_id": "CALL",
            "decision_id": "proof-entry",
            "broker_order_id": "proof-order",
        },
        quote={
            "option_symbol":
                "NIFTY2671424100CE",
            "option_token": "13152002",
            "bid": "105",
            "ask": "105.10",
            "ts_event_ns": str(now_ns),
        },
    )

    assert evaluation.should_exit is True
    assert evaluation.decision is not None

    return evaluation.decision.to_dict()


def parse_payload(
    payload: dict[str, Any],
):
    return ExecutionService._parse_decision(
        object(),
        "1-0",
        {
            "decision_id":
                payload["decision_id"],
            "action": payload["action"],
            "ts_ns":
                str(payload["ts_event_ns"]),
            "payload_json": json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
            ),
        },
    )


def main() -> int:
    assert POLICY_VERSION == (
        "R38TK2_FAMILY_CONTRACT_EXIT_V2_CLOSE"
    )

    # Strategy EXIT → execution parser.
    payload = build_exit_payload()
    parsed = parse_payload(payload)

    assert parsed.action == N.ACTION_EXIT
    assert (
        parsed.position_effect
        == N.POSITION_EFFECT_CLOSE
    )
    assert parsed.strategy_family_id == "MIST"
    assert parsed.branch_id == N.BRANCH_CALL
    assert parsed.reason_code == "target_points"

    # PendingOrder ownership serialization.
    pending = PendingOrder(
        intent="ENTRY",
        action=N.ACTION_ENTER_CALL,
        decision_id="proof-entry-decision",
        client_order_id="proof-entry-client",
        option_symbol="NIFTY2671424100CE",
        option_token="13152002",
        qty_lots=1,
        requested_limit_price="100",
        entry_mode="DIRECT",
        strike="24100",
        created_ts_ns=2_000_000_000,
        strategy_family_id="MIST",
        branch_id=N.BRANCH_CALL,
    )

    pending_json = pending.to_json_dict()
    restored = PendingOrder.from_json_dict(
        pending_json
    )

    assert restored.strategy_family_id == "MIST"
    assert restored.branch_id == N.BRANCH_CALL

    # Historical pending JSON remains loadable.
    historical = dict(pending_json)
    historical.pop("strategy_family_id")
    historical.pop("branch_id")

    historical_restored = (
        PendingOrder.from_json_dict(
            historical
        )
    )

    assert (
        historical_restored.strategy_family_id
        == ""
    )
    assert historical_restored.branch_id == ""

    # ENTRY_FILL position persistence without Redis/broker.
    service = object.__new__(
        ExecutionService
    )

    service.position_state = (
        ExecutionService._default_position_state(
            service
        )
    )

    service.execution_state = {
        "entry_pending": 1,
        "exit_pending": 0,
        "pending_order_json":
            json.dumps(pending_json),
        "last_ack_type": "",
        "updated_at_ns": 0,
        "ts_ns": 0,
    }

    service.pending_order = pending

    ledger_events: list[dict[str, Any]] = []
    ack_events: list[dict[str, Any]] = []

    service._publish_trade_ledger = (
        lambda **kwargs:
            ledger_events.append(kwargs)
    )

    service._publish_ack_simple = (
        lambda **kwargs:
            ack_events.append(kwargs)
    )

    ExecutionService._apply_entry_fill(
        service,
        pending,
        {
            "broker_order_id":
                "R38TMA1-PAPER-PROOF",
            "status": "COMPLETE",
            "filled_quantity": 65,
            "filled_units": 65,
            "avg_fill_price": "100",
        },
        3_000_000_000,
    )

    position = dict(service.position_state)

    assert position["has_position"] == 1
    assert (
        position["position_side"]
        == N.POSITION_SIDE_LONG_CALL
    )
    assert position["qty_lots"] == 1
    assert position["qty_units"] == 65
    assert (
        position["strategy_family_id"]
        == "MIST"
    )
    assert position["branch_id"] == N.BRANCH_CALL
    assert (
        position["decision_id"]
        == "proof-entry-decision"
    )

    assert len(ledger_events) == 1
    assert len(ack_events) == 1

    loaded = ExecutionService._load_position_state(
        service,
        position,
    )

    assert loaded["strategy_family_id"] == "MIST"
    assert loaded["branch_id"] == N.BRANCH_CALL

    flat = ExecutionService._default_position_state(
        service
    )

    assert flat["strategy_family_id"] == ""
    assert flat["branch_id"] == ""

    # Every PendingOrder constructor now carries ownership.
    execution_source = EXECUTION_PATH.read_text()
    tree = ast.parse(execution_source)

    pending_calls = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        name = ""

        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr

        if name != "PendingOrder":
            continue

        keywords = {
            keyword.arg
            for keyword in node.keywords
            if keyword.arg
        }

        pending_calls.append(
            {
                "lineno": node.lineno,
                "keywords": sorted(keywords),
            }
        )

        assert "strategy_family_id" in keywords, (
            node.lineno,
            keywords,
        )
        assert "branch_id" in keywords, (
            node.lineno,
            keywords,
        )

    assert len(pending_calls) == 4, pending_calls

    required_markers = [
        "R38TMA1_EXECUTION_ENTRY_OWNERSHIP_EXACT_V1",
        "R38TH_CANONICAL_PAPER_EXIT_ADAPTER_CONTRACT",
        "R38TH_EXIT_FILL_QUANTITY_FAIL_CLOSED",
        'strategy_family_id: str = ""',
        'branch_id: str = ""',
        'self.position_state["strategy_family_id"]',
        'self.position_state["branch_id"]',
    ]

    for marker in required_markers:
        assert marker in execution_source, marker

    report = {
        "classification":
            "PASS_R38TMA1_EXECUTION_OWNERSHIP_EXACT_OFFLINE",
        "policy_version": POLICY_VERSION,
        "decision_parser": {
            "action": parsed.action,
            "position_effect":
                parsed.position_effect,
            "strategy_family_id":
                parsed.strategy_family_id,
            "branch_id": parsed.branch_id,
            "reason_code":
                parsed.reason_code,
        },
        "pending_order_roundtrip": {
            "strategy_family_id":
                restored.strategy_family_id,
            "branch_id":
                restored.branch_id,
        },
        "historical_pending_compatible":
            True,
        "entry_fill_position": position,
        "loaded_position": loaded,
        "flat_position": flat,
        "pending_order_calls":
            pending_calls,
        "pending_order_call_count":
            len(pending_calls),
        "redis_used": False,
        "broker_used": False,
        "runtime_started": False,
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
            default=str,
        )
        + "\n"
    )

    print(
        "CLASSIFICATION="
        "PASS_R38TMA1_EXECUTION_OWNERSHIP_EXACT_OFFLINE"
    )
    print("DECISION_FAMILY=MIST")
    print("DECISION_BRANCH=CALL")
    print("POSITION_EFFECT=CLOSE")
    print("PENDING_ORDER_CALL_COUNT=4")
    print("ALL_PENDING_ORDER_CALLS_OWNERSHIP=PASS")
    print("PENDING_JSON_ROUNDTRIP=PASS")
    print("HISTORICAL_PENDING_COMPATIBILITY=PASS")
    print("ENTRY_FILL_FAMILY_PERSISTENCE=PASS")
    print("ENTRY_FILL_BRANCH_PERSISTENCE=PASS")
    print("POSITION_LOAD_PERSISTENCE=PASS")
    print("DEFAULT_FLAT_OWNERSHIP_CLEAR=PASS")
    print("NO_REDIS_BROKER_CALLS=1")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
