#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import execution as X


SIDE_CALL = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT = getattr(N, "SIDE_PUT", "PUT")
OPEN = getattr(N, "POSITION_EFFECT_OPEN", "OPEN")
CLOSE = getattr(N, "POSITION_EFFECT_CLOSE", "CLOSE")


class FakeShutdown:
    def __init__(self) -> None:
        self.wait_calls = 0

    def is_set(self) -> bool:
        return False

    def wait(self, seconds: float) -> None:
        self.wait_calls += 1


class FakeClock:
    def __init__(self) -> None:
        self.t = 1_000_000_000

    def wall_time_ns(self) -> int:
        self.t += 1_000_000
        return self.t

    def utc_datetime(self, ts_ns: int):
        from datetime import datetime, timezone
        return datetime.fromtimestamp(ts_ns / 1_000_000_000, tz=timezone.utc)


class FakeRedis:
    def __init__(self, *, risk: Mapping[str, Any] | None = None) -> None:
        self.risk = dict(risk or {})
        self.streams: dict[str, list[dict[str, Any]]] = {}
        self.xacks: list[tuple[str, str, list[str]]] = []
        self.queue: list[tuple[str, list[tuple[str, dict[str, str]]]]] = []

    def hgetall(self, key: str) -> dict[str, Any]:
        if key == N.HASH_STATE_RISK:
            return dict(self.risk)
        return {}

    def xadd(self, stream: str, fields: Mapping[str, Any]) -> str:
        self.streams.setdefault(stream, []).append(dict(fields))
        return f"{len(self.streams[stream])}-0"


class FakeBroker:
    def __init__(self) -> None:
        self.entry_orders: list[dict[str, Any]] = []
        self.exit_orders: list[dict[str, Any]] = []
        self.open_orders: list[dict[str, Any]] = []
        self.orders_by_id: dict[str, dict[str, Any]] = {}
        self.cancelled: list[str] = []

    def healthcheck(self) -> bool:
        return True

    def reconcile_position(self) -> Mapping[str, Any] | None:
        return None

    def reconcile_open_orders(self) -> list[Mapping[str, Any]] | None:
        return list(self.open_orders)

    def place_entry_order(
        self,
        *,
        client_order_id: str,
        option_symbol: str,
        option_token: str,
        qty_lots: int,
        limit_price: Decimal,
    ) -> Mapping[str, Any]:
        row = {
            "client_order_id": client_order_id,
            "option_symbol": option_symbol,
            "option_token": option_token,
            "qty_lots": qty_lots,
            "limit_price": str(limit_price),
            "broker_order_id": f"bo-entry-{len(self.entry_orders)+1}",
            "status": "SUBMITTED",
            "filled_quantity": 0,
        }
        self.entry_orders.append(row)
        self.orders_by_id[row["broker_order_id"]] = row
        return row

    def place_exit_order(
        self,
        *,
        client_order_id: str,
        option_symbol: str,
        option_token: str,
        qty_lots: int,
        limit_price: Decimal | None,
    ) -> Mapping[str, Any]:
        row = {
            "client_order_id": client_order_id,
            "option_symbol": option_symbol,
            "option_token": option_token,
            "qty_lots": qty_lots,
            "limit_price": "" if limit_price is None else str(limit_price),
            "broker_order_id": f"bo-exit-{len(self.exit_orders)+1}",
            "status": "SUBMITTED",
            "filled_quantity": 0,
        }
        self.exit_orders.append(row)
        self.orders_by_id[row["broker_order_id"]] = row
        return row

    def get_order(self, broker_order_id: str) -> Mapping[str, Any] | None:
        return self.orders_by_id.get(broker_order_id)

    def cancel_order(self, broker_order_id: str) -> Any:
        self.cancelled.append(broker_order_id)
        return {"status": "CANCELLED"}


def patch_rx() -> None:
    X.RX.hgetall = lambda key, client=None: client.hgetall(key)
    X.RX.xadd_fields = lambda stream, fields, maxlen_approx=None, client=None: client.xadd(stream, fields)
    X.RX.xreadgroup = lambda group, consumer, streams, count=None, block_ms=None, client=None: list(client.queue)
    X.RX.xack = lambda stream, group, ids, client=None: client.xacks.append((stream, group, list(ids)))
    X.RX.STREAM_ID_NEW_ONLY = getattr(X.RX, "STREAM_ID_NEW_ONLY", ">")


def make_service(
    *,
    risk: Mapping[str, Any] | None = None,
    broker: FakeBroker | None = None,
) -> tuple[X.ExecutionService, FakeRedis, FakeBroker]:
    redis = FakeRedis(risk=risk)
    br = broker or FakeBroker()
    svc = X.ExecutionService(
        redis_client=redis,
        broker=br,
        clock=FakeClock(),
        shutdown=FakeShutdown(),
        instance_id="proof-exec",
        consumer_name="proof-consumer",
    )
    return svc, redis, br


def fields(
    *,
    action: str,
    payload_action: str | None = None,
    decision_id: str,
    quantity_lots: int = 1,
    side: str | None = None,
    position_effect: str = OPEN,
    instrument_key: str = "NFO:TESTCE",
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    payload = {
        "decision_id": decision_id,
        "ts_event_ns": 1_000_000_000,
        "action": payload_action if payload_action is not None else action,
        "side": side or (SIDE_CALL if action == N.ACTION_ENTER_CALL else SIDE_PUT if action == N.ACTION_ENTER_PUT else ""),
        "position_effect": position_effect,
        "quantity_lots": quantity_lots,
        "instrument_key": instrument_key,
        "entry_mode": "ATM",
        "metadata": dict(metadata or {}),
    }
    return {
        "decision_id": decision_id,
        "ts_ns": "1000000000",
        "action": action,
        "reason_code": "proof",
        "entry_mode": "ATM",
        "payload_json": json.dumps(payload, separators=(",", ":")),
    }


def valid_meta(**overrides: Any) -> dict[str, Any]:
    meta = {
        "option_symbol": "NIFTY_TEST_CE",
        "option_token": "TOKEN123",
        "strike": "22500",
        "limit_price": "100.50",
        "reason_code": "proof_entry",
    }
    meta.update(overrides)
    return meta


def parse(svc: X.ExecutionService, row: Mapping[str, Any]) -> X.DecisionView:
    return svc._parse_decision("1-0", row)


def ack_rejected(redis: FakeRedis, reason_contains: str) -> bool:
    rows = redis.streams.get(N.STREAM_DECISIONS_ACK, [])
    return any(
        row.get("ack_type") == N.ACK_REJECTED and reason_contains in str(row.get("reason"))
        for row in rows
    )


def no_broker_call(br: FakeBroker) -> bool:
    return not br.entry_orders and not br.exit_orders


def main() -> int:
    patch_rx()
    cases: list[dict[str, Any]] = []

    # HOLD with order-like metadata must not place an order.
    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
    hold = parse(
        svc,
        fields(
            action=N.ACTION_HOLD,
            decision_id="hold-1",
            quantity_lots=9,
            metadata={**valid_meta(), "activation_selected_action": N.ACTION_ENTER_CALL},
        ),
    )
    svc._handle_decision(hold, svc.now_ns())
    cases.append({
        "case": "hold_with_option_metadata_no_broker_call",
        "status": "PASS" if no_broker_call(br) else "FAIL",
        "entry_orders": br.entry_orders,
        "exit_orders": br.exit_orders,
    })

    # Flat/payload action mismatch rejected through poll path, with ACK_REJECTED and XACK.
    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
    redis.queue = [(N.STREAM_DECISIONS_MME, [("bad-1", fields(
        action=N.ACTION_ENTER_CALL,
        payload_action=N.ACTION_HOLD,
        decision_id="mismatch-1",
        metadata=valid_meta(),
    ))])]
    svc._poll_decisions(svc.now_ns())
    cases.append({
        "case": "flat_payload_action_mismatch_rejected_ack_xack_no_order",
        "status": "PASS"
        if ack_rejected(redis, "flat action")
        and redis.xacks
        and no_broker_call(br)
        else "FAIL",
        "acks": redis.streams.get(N.STREAM_DECISIONS_ACK, []),
        "xacks": redis.xacks,
    })

    # Zero quantity must not widen via risk cap.
    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
    redis.queue = [(N.STREAM_DECISIONS_MME, [("bad-qty", fields(
        action=N.ACTION_ENTER_CALL,
        decision_id="qty-zero",
        quantity_lots=0,
        metadata=valid_meta(),
    ))])]
    svc._poll_decisions(svc.now_ns())
    cases.append({
        "case": "enter_qty_zero_risk_cap_one_rejected_no_order",
        "status": "PASS" if ack_rejected(redis, "missing_or_zero_entry_quantity") and no_broker_call(br) else "FAIL",
        "acks": redis.streams.get(N.STREAM_DECISIONS_ACK, []),
    })

    # Valid quantity 2 with risk cap 1 should send qty 1.
    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
    decision = parse(
        svc,
        fields(
            action=N.ACTION_ENTER_CALL,
            decision_id="valid-cap",
            quantity_lots=2,
            side=SIDE_CALL,
            metadata=valid_meta(),
        ),
    )
    svc._handle_decision(decision, svc.now_ns())
    cases.append({
        "case": "enter_qty_two_risk_cap_one_sends_one_lot",
        "status": "PASS" if len(br.entry_orders) == 1 and br.entry_orders[0]["qty_lots"] == 1 else "FAIL",
        "entry_orders": br.entry_orders,
    })

    # Risk cap zero rejects.
    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "0"})
    decision = parse(svc, fields(action=N.ACTION_ENTER_CALL, decision_id="risk-zero", metadata=valid_meta()))
    svc._handle_decision(decision, svc.now_ns())
    cases.append({
        "case": "enter_risk_cap_zero_rejected_no_order",
        "status": "PASS" if no_broker_call(br) else "FAIL",
        "entry_orders": br.entry_orders,
    })

    invalids = [
        ("missing_option_symbol", valid_meta(option_symbol=""), "missing_option_symbol"),
        ("missing_option_token_no_instrument_fallback", valid_meta(option_token=""), "missing_option_token"),
        ("missing_entry_strike", valid_meta(strike=""), "missing_entry_strike"),
        (
            "missing_or_invalid_limit_price_missing",
            {k: v for k, v in valid_meta().items() if k != "limit_price"},
            "missing_or_invalid_limit_price",
        ),
        ("missing_or_invalid_limit_price_zero", valid_meta(limit_price="0"), "missing_or_invalid_limit_price"),
        ("missing_or_invalid_limit_price_negative", valid_meta(limit_price="-1"), "missing_or_invalid_limit_price"),
    ]
    for label, meta, expected_reason in invalids:
        svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
        redis.queue = [(N.STREAM_DECISIONS_MME, [("bad-"+label, fields(
            action=N.ACTION_ENTER_CALL,
            decision_id=label,
            instrument_key="INSTRUMENT_KEY_PRESENT",
            metadata=meta,
        ))])]
        svc._poll_decisions(svc.now_ns())
        cases.append({
            "case": f"{label}_rejected_no_order",
            "status": "PASS" if ack_rejected(redis, expected_reason) and no_broker_call(br) else "FAIL",
            "expected_reason": expected_reason,
            "acks": redis.streams.get(N.STREAM_DECISIONS_ACK, []),
        })

    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
    redis.queue = [(N.STREAM_DECISIONS_MME, [("bad-side", fields(
        action=N.ACTION_ENTER_CALL,
        decision_id="side-mismatch",
        side=SIDE_PUT,
        metadata=valid_meta(),
    ))])]
    svc._poll_decisions(svc.now_ns())
    cases.append({
        "case": "enter_call_side_put_rejected_no_order",
        "status": "PASS" if ack_rejected(redis, "entry_side_action_mismatch") and no_broker_call(br) else "FAIL",
        "acks": redis.streams.get(N.STREAM_DECISIONS_ACK, []),
    })

    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
    redis.queue = [(N.STREAM_DECISIONS_MME, [("bad-effect", fields(
        action=N.ACTION_ENTER_CALL,
        decision_id="effect-close",
        position_effect=CLOSE,
        metadata=valid_meta(),
    ))])]
    svc._poll_decisions(svc.now_ns())
    cases.append({
        "case": "enter_position_effect_close_rejected_no_order",
        "status": "PASS" if ack_rejected(redis, "entry_position_effect_not_open") and no_broker_call(br) else "FAIL",
        "acks": redis.streams.get(N.STREAM_DECISIONS_ACK, []),
    })

    # Missing risk state fails closed.
    svc, redis, br = make_service(risk={})
    decision = parse(svc, fields(action=N.ACTION_ENTER_CALL, decision_id="risk-missing", metadata=valid_meta()))
    svc._handle_decision(decision, svc.now_ns())
    cases.append({
        "case": "missing_risk_state_rejects_entry_no_order",
        "status": "PASS" if no_broker_call(br) else "FAIL",
    })

    # Exit is allowed even if risk vetoes entries.
    svc, redis, br = make_service(risk={"veto_entries": "1", "max_new_lots": "0"})
    svc.position_state.update({
        "has_position": 1,
        "position_side": N.POSITION_SIDE_LONG_CALL,
        "qty_lots": 1,
        "qty_units": 1,
        "entry_option_symbol": "NIFTY_TEST_CE",
        "entry_option_token": "TOKEN123",
        "entry_strike": "22500",
        "entry_mode": "ATM",
    })
    exit_decision = parse(
        svc,
        fields(
            action=N.ACTION_EXIT,
            decision_id="exit-risk-veto",
            quantity_lots=1,
            side=SIDE_CALL,
            position_effect=CLOSE,
            metadata={"limit_price": "99.0"},
        ),
    )
    svc._handle_decision(exit_decision, svc.now_ns())
    cases.append({
        "case": "exit_allowed_while_risk_veto_true",
        "status": "PASS" if len(br.exit_orders) == 1 else "FAIL",
        "exit_orders": br.exit_orders,
    })

    # Recovered CE/PE entry action inference.
    for label, symbol, expected_action, expected_side in (
        ("recovered_ce_entry_long_call", "NIFTY_TEST_CE", N.ACTION_ENTER_CALL, N.POSITION_SIDE_LONG_CALL),
        ("recovered_pe_entry_long_put", "NIFTY_TEST_PE", N.ACTION_ENTER_PUT, N.POSITION_SIDE_LONG_PUT),
    ):
        br = FakeBroker()
        br.open_orders = [{
            "client_order_id": f"entry-{label}",
            "option_symbol": symbol,
            "option_token": f"{label}-TOKEN",
            "qty_lots": 1,
            "limit_price": "100",
            "entry_mode": "ATM",
            "strike": "22500",
            "created_ts_ns": 1,
            "broker_order_id": f"bo-{label}",
            "status": "OPEN",
        }]
        svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"}, broker=br)
        svc._reconcile_open_orders()
        ok_action = svc.pending_order is not None and svc.pending_order.action == expected_action
        svc._apply_entry_fill(
            svc.pending_order,
            {
                "status": "FILLED",
                "filled_quantity": 1,
                "filled_units": 1,
                "avg_fill_price": "100",
                "broker_order_id": f"bo-{label}",
            },
            svc.now_ns(),
        )
        cases.append({
            "case": label,
            "status": "PASS" if ok_action and svc.position_state["position_side"] == expected_side else "FAIL",
            "position_state": dict(svc.position_state),
        })

    br = FakeBroker()
    br.open_orders = [{
        "client_order_id": "entry-unknown",
        "option_symbol": "NIFTY_TEST_UNKNOWN",
        "option_token": "UNK",
        "qty_lots": 1,
        "limit_price": "100",
        "entry_mode": "ATM",
        "strike": "22500",
        "created_ts_ns": 1,
        "broker_order_id": "bo-unknown",
        "status": "OPEN",
    }]
    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"}, broker=br)
    try:
        svc._reconcile_open_orders()
    except Exception as exc:
        cases.append({
            "case": "recovered_unknown_entry_fails_closed",
            "status": "PASS" if "cannot infer recovered open ENTRY order side" in str(exc) else "FAIL",
            "error": str(exc),
        })
    else:
        cases.append({
            "case": "recovered_unknown_entry_fails_closed",
            "status": "FAIL",
            "error": "unknown entry accepted",
        })

    # Terminal broker rejection publishes terminal order event.
    svc, redis, br = make_service(risk={"veto_entries": "0", "max_new_lots": "1"})
    pending = X.PendingOrder(
        intent="ENTRY",
        action=N.ACTION_ENTER_CALL,
        decision_id="terminal-reject",
        client_order_id="entry-terminal-reject",
        option_symbol="NIFTY_TEST_CE",
        option_token="TOKEN123",
        qty_lots=1,
        requested_limit_price="100",
        entry_mode="ATM",
        strike="22500",
        created_ts_ns=1,
        broker_order_id="bo-terminal",
        broker_status="OPEN",
    )
    svc.pending_order = pending
    svc._apply_broker_order_update(
        pending,
        {"status": "REJECTED", "broker_order_id": "bo-terminal", "message": "rejected_by_broker"},
        svc.now_ns(),
    )
    order_events = redis.streams.get(N.STREAM_ORDERS_MME, [])
    cases.append({
        "case": "terminal_rejected_order_publishes_order_terminal_event",
        "status": "PASS"
        if any(row.get("event_type") == "ENTRY_ORDER_TERMINAL" for row in order_events)
        else "FAIL",
        "order_events": order_events,
    })

    # Every execution stream event emitted by this proof should carry ts_event_ns when ts_ns is present.
    all_events = []
    for stream_rows in redis.streams.values():
        all_events.extend(stream_rows)
    missing_ts_event = [
        row for row in all_events
        if "ts_ns" in row and "ts_event_ns" not in row
    ]
    cases.append({
        "case": "execution_stream_events_include_ts_event_ns",
        "status": "PASS" if not missing_ts_event else "FAIL",
        "missing": missing_ts_event,
    })

    failed = [case for case in cases if case.get("status") != "PASS"]
    proof = {
        "proof": "execution_family_entry_safety",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out = PROJECT_ROOT / "run" / "proofs" / "execution_family_entry_safety.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str))
    print(json.dumps(proof, indent=2, sort_keys=True, default=str))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
