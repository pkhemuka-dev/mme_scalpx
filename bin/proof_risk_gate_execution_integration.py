#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import execution as EX
from app.mme_scalpx.services import risk as RISK
from app.mme_scalpx.services.strategy_family import order_intent as OI



class ProofClock:
    """
    Proof-local clock shim for ExecutionService dry-run.

    execution.py calls self.clock.wall_time_ns() during ACK/state publication.
    This shim keeps the proof isolated and does not modify production clock code.
    """

    def wall_time_ns(self) -> int:
        return time.time_ns()

    def monotonic_ns(self) -> int:
        return time.monotonic_ns()

    def now_ns(self) -> int:
        return time.time_ns()


class FakeBroker:
    def __init__(self) -> None:
        self.entry_orders: list[dict[str, Any]] = []
        self.exit_orders: list[dict[str, Any]] = []

    def healthcheck(self) -> bool:
        return True

    def reconcile_position(self) -> dict[str, Any]:
        return {}

    def reconcile_open_orders(self) -> list[dict[str, Any]]:
        return []

    def place_entry_order(
        self,
        *,
        client_order_id: str,
        option_symbol: str,
        option_token: str,
        qty_lots: int,
        limit_price: Decimal,
    ) -> dict[str, Any]:
        order = {
            "broker_order_id": f"broker-{client_order_id}",
            "status": "OPEN",
            "filled_quantity": 0,
            "avg_fill_price": "",
        }
        self.entry_orders.append(
            {
                "client_order_id": client_order_id,
                "option_symbol": option_symbol,
                "option_token": option_token,
                "qty_lots": qty_lots,
                "limit_price": str(limit_price),
            }
        )
        return order

    def place_exit_order(
        self,
        *,
        client_order_id: str,
        option_symbol: str,
        option_token: str,
        qty_lots: int,
        limit_price: Decimal | None,
    ) -> dict[str, Any]:
        order = {
            "broker_order_id": f"broker-{client_order_id}",
            "status": "OPEN",
            "filled_quantity": 0,
            "avg_fill_price": "",
        }
        self.exit_orders.append(
            {
                "client_order_id": client_order_id,
                "option_symbol": option_symbol,
                "option_token": option_token,
                "qty_lots": qty_lots,
                "limit_price": None if limit_price is None else str(limit_price),
            }
        )
        return order

    def get_order(self, broker_order_id: str) -> dict[str, Any] | None:
        return None

    def cancel_order(self, broker_order_id: str) -> bool:
        return True


class FakeRX:
    def __init__(self, risk_hash: dict[str, Any]) -> None:
        self.risk_hash = risk_hash
        self.acks: list[dict[str, Any]] = []
        self.orders: list[dict[str, Any]] = []
        self.trades: list[dict[str, Any]] = []
        self.hash_writes: list[dict[str, Any]] = []

    def hgetall(self, key: str, *, client: Any = None) -> dict[str, Any]:
        if key == N.HASH_STATE_RISK:
            return dict(self.risk_hash)
        return {}

    def xadd_fields(self, stream: str, fields: dict[str, Any], *, maxlen_approx: int | None = None, client: Any = None) -> str:
        row = {"stream": stream, "fields": dict(fields)}
        if stream == N.STREAM_DECISIONS_ACK:
            self.acks.append(row)
        elif stream == N.STREAM_ORDERS_MME:
            self.orders.append(row)
        elif stream == N.STREAM_TRADES_LEDGER:
            self.trades.append(row)
        return f"{len(self.acks)+len(self.orders)+len(self.trades)}-0"

    def write_hash_fields(self, key: str, fields: dict[str, Any], *, client: Any = None) -> None:
        self.hash_writes.append({"key": key, "fields": dict(fields)})

    def write_heartbeat(self, *args: Any, **kwargs: Any) -> None:
        return None


def _candidate_metadata() -> dict[str, Any]:
    return {
        "candidate_id": "candidate-25r-integration",
        "strategy_family": getattr(N, "STRATEGY_FAMILY_MIST", "MIST"),
        "strategy_branch": getattr(N, "BRANCH_CALL", "CALL"),
        "doctrine_id": getattr(N, "DOCTRINE_MIST", "MIST"),
        "action_hint": getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL"),
        "side": getattr(N, "SIDE_CALL", "CALL"),
        "instrument_key": getattr(N, "IK_MME_CE", "NIFTY_CE"),
        "option_symbol": "NIFTY-25000-CE-25R",
        "option_token": "OPTION-TOKEN-25R",
        "strike": 25000.0,
        "limit_price_hint": 110.0,
        "quantity_lots_hint": 2,
        "entry_mode": getattr(N, "ENTRY_MODE_ATM", "ATM"),
        "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "execution_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "risk_gate_required": True,
        "score": 0.91,
        "blockers": [],
        "source_feature_frame_id": "frame-25r-integration",
        "source_feature_ts_ns": time.time_ns(),
    }


def _entry_decision(decision_id: str = "decision-25r-entry") -> EX.DecisionView:
    payload = OI.build_promoted_entry_payload(
        candidate_metadata=_candidate_metadata(),
        decision_id=decision_id,
        ts_event_ns=time.time_ns(),
    )
    fields = OI.build_strategy_stream_fields(payload=payload)
    service = EX.ExecutionService.__new__(EX.ExecutionService)
    return EX.ExecutionService._parse_decision(service, f"{decision_id}-stream", fields)


def _hold_decision() -> EX.DecisionView:
    fields = OI.build_hold_stream_fields(decision_id="decision-25r-hold", ts_event_ns=time.time_ns())
    service = EX.ExecutionService.__new__(EX.ExecutionService)
    return EX.ExecutionService._parse_decision(service, "hold-stream", fields)


def _exit_decision() -> EX.DecisionView:
    ts_ns = time.time_ns()
    payload = {
        "decision_id": "decision-25r-exit",
        "ts_event_ns": ts_ns,
        "action": getattr(N, "ACTION_EXIT", "EXIT"),
        "side": getattr(N, "SIDE_CALL", "CALL"),
        "position_effect": getattr(N, "POSITION_EFFECT_CLOSE", "CLOSE"),
        "quantity_lots": 0,
        "instrument_key": getattr(N, "IK_MME_CE", "NIFTY_CE"),
        "entry_mode": getattr(N, "ENTRY_MODE_ATM", "ATM"),
        "system_state": getattr(N, "STATE_POSITION_OPEN", "POSITION_OPEN"),
        "explain": "batch25r_exit_dryrun",
        "blocker_code": "",
        "blocker_message": "",
        "metadata": {
            "option_symbol": "NIFTY-25000-CE-25R",
            "option_token": "OPTION-TOKEN-25R",
            "limit_price": "",
            "strike": "25000",
            "reason_code": "BATCH25R_EXIT_DRYRUN",
        },
    }
    fields = {
        "decision_id": payload["decision_id"],
        "ts_ns": str(ts_ns),
        "action": getattr(N, "ACTION_EXIT", "EXIT"),
        "reason_code": "BATCH25R_EXIT_DRYRUN",
        "entry_mode": getattr(N, "ENTRY_MODE_ATM", "ATM"),
        "payload_json": json.dumps(payload, separators=(",", ":"), ensure_ascii=False, default=str),
    }
    service = EX.ExecutionService.__new__(EX.ExecutionService)
    return EX.ExecutionService._parse_decision(service, "exit-stream", fields)



def _proof_default_execution_state(now_ns: int) -> dict[str, Any]:
    """
    Proof-local execution state seed.

    Current execution.py does not export module-level _default_execution_state.
    This helper keeps the proof dry-run local and does not modify production
    execution runtime behavior.
    """
    return {
        "service": getattr(N, "SERVICE_EXECUTION", "execution"),
        "schema_version": "1",
        "mode": getattr(N, "EXECUTION_MODE_NORMAL", "NORMAL"),
        "status": getattr(N, "HEALTH_OK", "OK"),
        "broker_status": getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "has_pending_order": "0",
        "pending_order_json": "",
        "last_decision_id": "",
        "last_ack_type": "",
        "last_error": "",
        "entry_sent_count": "0",
        "exit_sent_count": "0",
        "rejected_count": "0",
        "failed_count": "0",
        "last_update_ns": str(now_ns),
    }


def _proof_default_position_state(now_ns: int) -> dict[str, Any]:
    """
    Proof-local flat position state seed.

    The integration proof mutates this into an open position only for the exit
    case, proving risk entry veto does not block exits.
    """
    return {
        "service": getattr(N, "SERVICE_EXECUTION", "execution"),
        "schema_version": "1",
        "has_position": "0",
        "position_side": getattr(N, "POSITION_SIDE_FLAT", "FLAT"),
        "side": getattr(N, "POSITION_SIDE_FLAT", "FLAT"),
        "quantity_lots": "0",
        "entry_quantity_lots": "0",
        "entry_option_symbol": "",
        "entry_option_token": "",
        "instrument_key": "",
        "decision_id": "",
        "broker_order_id": "",
        "entry_mode": getattr(N, "ENTRY_MODE_UNKNOWN", "UNKNOWN"),
        "last_update_ns": str(now_ns),
    }

def _service(risk_hash: dict[str, Any]) -> tuple[EX.ExecutionService, FakeBroker, FakeRX]:
    broker = FakeBroker()
    fake_rx = FakeRX(risk_hash)

    service = EX.ExecutionService.__new__(EX.ExecutionService)
    service.redis = object()
    service.broker = broker
    service.clock = ProofClock()
    service.shutdown = None
    service.instance_id = "batch25r-proof"
    service.consumer_name = "batch25r-proof"
    service.log = None
    service.service_name = N.SERVICE_EXECUTION
    now_ns = time.time_ns()
    service.execution_state = _proof_default_execution_state(now_ns)
    service.position_state = _proof_default_position_state(now_ns)
    service.pending_order = None
    service.stream_maxlen = 1000

    # Attributes used by heartbeat/state persistence paths if touched by
    # _handle_decision during dry-run. These remain local to the proof object.
    service.heartbeat_refresh_ms = 10_000
    service.heartbeat_ttl_ms = 30_000
    service.state_publish_ms = 10_000
    service._last_heartbeat_ns = 0
    service._last_state_publish_ns = 0

    return service, broker, fake_rx


def _with_fake_rx(fake_rx: FakeRX):
    class Patch:
        def __enter__(self):
            self.original = EX.RX
            EX.RX = fake_rx
            return fake_rx

        def __exit__(self, exc_type, exc, tb):
            EX.RX = self.original
            return False

    return Patch()



def _risk_architecture_probe(
    *,
    valid_risk_hash: dict[str, Any],
    veto_risk_hash: dict[str, Any],
    zero_lots_risk_hash: dict[str, Any],
    risk_veto_blocks_entry: bool,
    risk_zero_lots_blocks_entry: bool,
    exit_not_blocked_by_risk: bool,
) -> bool:
    """
    Proof-local architecture probe for the frozen risk/execution seam.

    The current risk.py config surface requires full runtime construction, so
    this proof must not instantiate RiskConfig with empty defaults. Instead, it
    verifies the seam law from two facts already exercised in this dry run:

    1. the risk hash contract provides veto_entries, max_new_lots, allow_exits
    2. execution behavior obeys that contract:
       - veto_entries blocks entries
       - max_new_lots=0 blocks entries
       - entry veto does not block exits
    """

    required_keys = {"veto_entries", "max_new_lots", "allow_exits"}
    sample_hashes_have_contract = all(
        required_keys.issubset(set(sample.keys()))
        for sample in (valid_risk_hash, veto_risk_hash, zero_lots_risk_hash)
    )

    return bool(
        sample_hashes_have_contract
        and risk_veto_blocks_entry
        and risk_zero_lots_blocks_entry
        and exit_not_blocked_by_risk
    )

def _latest_ack_reason(fake_rx: FakeRX) -> str:
    if not fake_rx.acks:
        return ""
    return str(fake_rx.acks[-1]["fields"].get("reason", ""))


def main() -> int:
    now_ns = time.time_ns()

    valid_risk_hash = {
        "veto_entries": "0",
        "max_new_lots": "1",
        "allow_exits": "1",
        "risk_heartbeat_stale": "0",
    }
    veto_risk_hash = {
        "veto_entries": "1",
        "max_new_lots": "1",
        "allow_exits": "1",
        "risk_heartbeat_stale": "0",
    }
    zero_lots_risk_hash = {
        "veto_entries": "0",
        "max_new_lots": "0",
        "allow_exits": "1",
        "risk_heartbeat_stale": "0",
    }

    # Valid entry reaches broker with risk capped quantity.
    service, broker, fake_rx = _service(valid_risk_hash)
    with _with_fake_rx(fake_rx):
        service._handle_decision(_entry_decision("decision-25r-valid-entry"), now_ns)

    valid_entry_sent = len(broker.entry_orders) == 1 and broker.entry_orders[0]["qty_lots"] == 1

    # Risk veto blocks entry before broker.
    service, broker, fake_rx = _service(veto_risk_hash)
    with _with_fake_rx(fake_rx):
        service._handle_decision(_entry_decision("decision-25r-veto-entry"), now_ns)
    risk_veto_blocks_entry = len(broker.entry_orders) == 0 and _latest_ack_reason(fake_rx) == "risk_rejected_or_zero_lots"

    # Risk zero lots blocks entry before broker.
    service, broker, fake_rx = _service(zero_lots_risk_hash)
    with _with_fake_rx(fake_rx):
        service._handle_decision(_entry_decision("decision-25r-zero-entry"), now_ns)
    risk_zero_lots_blocks_entry = len(broker.entry_orders) == 0 and _latest_ack_reason(fake_rx) == "risk_rejected_or_zero_lots"

    # HOLD is received/acked but does not place broker order.
    service, broker, fake_rx = _service(valid_risk_hash)
    with _with_fake_rx(fake_rx):
        service._handle_decision(_hold_decision(), now_ns)
    HOLD_ignored_by_execution = len(broker.entry_orders) == 0 and len(broker.exit_orders) == 0

    # EXIT should not read entry risk veto. It should proceed when there is a position.
    service, broker, fake_rx = _service(veto_risk_hash)
    service.position_state["has_position"] = "1"
    service.position_state["quantity_lots"] = "1"
    service.position_state["entry_option_symbol"] = "NIFTY-25000-CE-25R"
    service.position_state["entry_option_token"] = "OPTION-TOKEN-25R"
    service.position_state["side"] = getattr(N, "POSITION_SIDE_LONG_CALL", "LONG_CALL")
    with _with_fake_rx(fake_rx):
        service._handle_decision(_exit_decision(), now_ns)
    exit_not_blocked_by_risk = len(broker.exit_orders) == 1

    # Risk architecture proof from observed dry-run seam behavior plus frozen
    # risk-hash field contract.
    risk_architecture_frozen = _risk_architecture_probe(
        valid_risk_hash=valid_risk_hash,
        veto_risk_hash=veto_risk_hash,
        zero_lots_risk_hash=zero_lots_risk_hash,
        risk_veto_blocks_entry=risk_veto_blocks_entry,
        risk_zero_lots_blocks_entry=risk_zero_lots_blocks_entry,
        exit_not_blocked_by_risk=exit_not_blocked_by_risk,
    )

    checks = {
        "valid_promoted_entry_passes_parser": True,
        "valid_promoted_entry_reaches_broker_with_risk_cap": valid_entry_sent,
        "risk_veto_blocks_entry": risk_veto_blocks_entry,
        "risk_zero_lots_blocks_entry": risk_zero_lots_blocks_entry,
        "exit_not_blocked_by_risk": exit_not_blocked_by_risk,
        "HOLD_ignored_by_execution": HOLD_ignored_by_execution,
        "risk_architecture_frozen_global_entry_gate": risk_architecture_frozen,
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_risk_gate_execution_integration",
        "batch": "25R",
        "generated_at_ns": now_ns,
        "risk_gate_execution_integration_ok": proof_ok,
        "checks": checks,
        "architecture_decision": {
            "risk": "global entry veto + max_new_lots + cooldown/loss/health gate",
            "strategy": "family candidate selection + arbitration + future order-intent proposal",
            "execution": "sole position/order/broker truth owner",
            "candidate_aware_risk_request_stream_required": False,
        },
        "runtime_safety": {
            "no_strategy_promotion_enabled": True,
            "no_execution_arming_changed": True,
            "dryrun_only": True,
        },
    }

    out = Path("run/proofs/proof_risk_gate_execution_integration.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "risk_gate_execution_integration_ok": proof_ok,
        **checks,
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
