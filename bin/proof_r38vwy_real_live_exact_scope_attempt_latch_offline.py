from __future__ import annotations

import os
from types import SimpleNamespace

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import execution
from app.mme_scalpx.services import strategy


AUTH_1 = "AUTH-R38VWY-ONE"
AUTH_2 = "AUTH-R38VWY-TWO"
TOKEN = "14681090"
SYMBOL = "NIFTY2672124200CE"

LIVE_KEYS = {
    "SCALPX_RUNTIME_MODE": "live",
    "SCALPX_TRADING_ENABLED": "1",
    "SCALPX_ALLOW_LIVE_ORDERS": "1",
    "SCALPX_ENABLE_LIVE": "1",
    "MME_ENABLE_LIVE": "1",
    "SCALPX_ALLOW_REAL_LIVE": "1",
    "SCALPX_REAL_LIVE_ALLOWED": "1",
    "SCALPX_ALLOW_BROKER_ORDERS": "1",
    "SCALPX_LIVE_ONE_EVENT_ONLY": "1",
    "SCALPX_NO_RETRY": "1",
    "SCALPX_DISABLE_RETRY": "1",
    "SCALPX_DISABLE_AVERAGING": "1",
    "SCALPX_POSITION_FLAT_VERIFIED": "1",
    "SCALPX_MAX_LIVE_EVENTS": "1",
    "SCALPX_MAX_ORDERS": "1",
    "SCALPX_ORDER_LOTS": "1",
    "SCALPX_ORDER_MAX_LOTS": "1",
    "MME_ORDER_LOTS": "1",
    "MME_MAX_LOTS": "1",
    "SCALPX_REAL_LIVE_SCOPE_ACK": (
        strategy._R38TZ_REAL_LIVE_SCOPE_ACK_PREFIX
        + "R38VWY"
    ),
    "SCALPX_REAL_LIVE_AUTHORIZATION_ID":
        AUTH_1,
    "SCALPX_REAL_LIVE_FAMILY": "MIST",
    "SCALPX_REAL_LIVE_SIDE": "CALL",
    "SCALPX_REAL_LIVE_ACTION": "ENTER_CALL",
    "SCALPX_REAL_LIVE_INSTRUMENT_TOKEN":
        TOKEN,
    "SCALPX_REAL_LIVE_OPTION_SYMBOL":
        SYMBOL,
    "SCALPX_REAL_LIVE_ENTRY_MODE":
        "DIRECT",
}

FORBIDDEN_KEYS = (
    "SCALPX_OBSERVE_ONLY",
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY",
    "SCALPX_ENABLE_PAPER",
    "MME_ENABLE_PAPER",
    "SCALPX_PAPER_ARMED",
    "SCALPX_CONTROLLED_PAPER_ARMED",
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_AVERAGING_ENABLED",
)

for key in FORBIDDEN_KEYS:
    os.environ.pop(key, None)

for key, value in LIVE_KEYS.items():
    os.environ[key] = value


def strategy_decision(**updates):
    row = {
        "strategy_family_id": "MIST",
        "side": "CALL",
        "action": "ENTER_CALL",
        "instrument_token": TOKEN,
        "instrument_key": TOKEN,
        "option_symbol": SYMBOL,
        "entry_mode": "DIRECT",
        "qty": 1,
        "metadata": {
            "strategy_family": "MIST",
            "side": "CALL",
            "option_token": TOKEN,
            "option_symbol": SYMBOL,
            "entry_mode": "DIRECT",
            "qty": 1,
        },
    }
    row.update(updates)
    return row


def execution_decision(
    *,
    decision_id: str,
    family: str = "MIST",
    side: str = "CALL",
    action: str = "ENTER_CALL",
    token: str = TOKEN,
    symbol: str = SYMBOL,
    entry_mode: str = "DIRECT",
):
    return execution.DecisionView(
        decision_id=decision_id,
        ts_event_ns=1,
        action=action,
        side=side,
        position_effect="OPEN",
        quantity_lots=1,
        instrument_key=token,
        entry_mode=entry_mode,
        system_state="LIVE",
        explain="r38vwy_proof",
        blocker_code="",
        blocker_message="",
        reason_code="r38vwy_proof",
        confidence=1.0,
        metadata={
            "option_symbol": symbol,
            "option_token": token,
            "strike": "24200",
            "limit_price": "100.00",
            "entry_mode": entry_mode,
        },
        payload_json="{}",
        strategy_family_id=family,
        branch_id=side,
    )


assert strategy._r38tz_live_one_event_bridge_allowed(
    strategy_decision()
)

for bad in (
    strategy_decision(
        strategy_family_id="MISB",
    ),
    strategy_decision(
        entry_mode="FALLBACK",
    ),
    strategy_decision(
        instrument_token="999",
        instrument_key="999",
    ),
    strategy_decision(
        option_symbol="NIFTY2672124200PE",
    ),
    strategy_decision(
        side="PUT",
        action="ENTER_CALL",
    ),
):
    assert not (
        strategy._r38tz_live_one_event_bridge_allowed(
            bad
        )
    )

saved_auth = os.environ.pop(
    "SCALPX_REAL_LIVE_AUTHORIZATION_ID"
)

assert not (
    strategy._r38tz_live_one_event_bridge_allowed(
        strategy_decision()
    )
)

os.environ[
    "SCALPX_REAL_LIVE_AUTHORIZATION_ID"
] = saved_auth

allowed, reason = (
    execution
    ._r38tzk_execution_real_live_one_event_entry_allowed(
        execution_decision(
            decision_id="decision-one"
        )
    )
)

assert allowed is True
assert reason == (
    "execution_entry_armed_"
    "r38tzk_real_live_one_event"
)

for bad in (
    execution_decision(
        decision_id="bad-family",
        family="MISB",
    ),
    execution_decision(
        decision_id="bad-mode",
        entry_mode="FALLBACK",
    ),
    execution_decision(
        decision_id="bad-token",
        token="999",
    ),
    execution_decision(
        decision_id="bad-symbol",
        symbol="NIFTY2672124200PE",
    ),
    execution_decision(
        decision_id="bad-side-action",
        side="PUT",
        action="ENTER_CALL",
    ),
):
    allowed, _ = (
        execution
        ._r38tzk_execution_real_live_one_event_entry_allowed(
            bad
        )
    )
    assert allowed is False


store: dict[str, dict[str, object]] = {}


def fake_write_hash_fields(
    key,
    values,
    *,
    client=None,
):
    bucket = store.setdefault(
        str(key),
        {},
    )
    bucket.update(dict(values))


def fake_hgetall(
    key,
    *,
    client=None,
):
    return dict(
        store.get(
            str(key),
            {},
        )
    )


execution.RX.write_hash_fields = (
    fake_write_hash_fields
)
execution.RX.hgetall = fake_hgetall

execution._r38tzq_compute_broker_qty_units = (
    lambda **kwargs: (65, 65)
)


class FakeBroker:
    def __init__(self):
        self.calls = 0

    def place_entry_order(self, **kwargs):
        auth_id = os.environ[
            "SCALPX_REAL_LIVE_AUTHORIZATION_ID"
        ]

        attempts = store.get(
            N.HASH_STATE_EXECUTION_REAL_LIVE_ATTEMPTS,
            {},
        )

        assert auth_id in attempts

        state = store.get(
            N.HASH_STATE_EXECUTION,
            {},
        )

        assert state.get(
            "real_live_entry_attempt_consumed"
        ) == 1

        self.calls += 1

        return {
            "broker_order_id":
                f"FAKE-{self.calls}",
            "status": "COMPLETE",
            "filled_units": 65,
            "filled_quantity": 65,
            "avg_fill_price": "100.00",
        }


def make_service(
    broker,
    *,
    execution_state=None,
):
    service = (
        execution.ExecutionService.__new__(
            execution.ExecutionService
        )
    )

    service.redis = object()
    service.broker = broker
    service.pending_order = None
    service.execution_state = (
        execution_state
        if execution_state is not None
        else service._default_execution_state()
    )
    service.position_state = {
        "has_position": 0,
        "position_side": "FLAT",
        "qty_lots": 0,
        "qty_units": 0,
    }

    service._entries_blocked_by_execution_mode = (
        lambda: False
    )
    service._read_risk_entry_gate = (
        lambda: execution.RiskEntryGate(
            veto_entries=False,
            max_new_lots=1,
        )
    )
    service._resolve_entry_lots = (
        lambda **kwargs: 1
    )

    service.rejections = []
    service.failures = []

    service._reject_decision = (
        lambda decision, reason:
            service.rejections.append(reason)
    )
    service._fail_decision = (
        lambda decision, reason:
            service.failures.append(reason)
    )
    service._publish_order_event = (
        lambda *args, **kwargs: None
    )
    service._publish_ack = (
        lambda *args, **kwargs: None
    )
    service._apply_broker_order_update = (
        lambda *args, **kwargs: None
    )

    return service


broker = FakeBroker()
service = make_service(broker)

first = execution_decision(
    decision_id="live-entry-one"
)

service._handle_entry_decision(
    first,
    1000,
)

assert broker.calls == 1
assert not service.failures

service.pending_order = None

second = execution_decision(
    decision_id="live-entry-two"
)

service._handle_entry_decision(
    second,
    2000,
)

assert broker.calls == 1
assert (
    "r38vwy_real_live_entry_"
    "attempt_already_consumed"
) in service.failures

restart_state = service._load_execution_state(
    store[N.HASH_STATE_EXECUTION]
)

restart_service = make_service(
    broker,
    execution_state=restart_state,
)

restart_service._handle_entry_decision(
    execution_decision(
        decision_id="live-entry-after-restart"
    ),
    3000,
)

assert broker.calls == 1
assert (
    "r38vwy_real_live_entry_"
    "attempt_already_consumed"
) in restart_service.failures

os.environ[
    "SCALPX_REAL_LIVE_AUTHORIZATION_ID"
] = AUTH_2

new_auth_service = make_service(
    broker,
    execution_state=restart_state,
)

new_auth_service._handle_entry_decision(
    execution_decision(
        decision_id="live-entry-new-auth"
    ),
    4000,
)

assert broker.calls == 2

attempts = store[
    N.HASH_STATE_EXECUTION_REAL_LIVE_ATTEMPTS
]

assert AUTH_1 in attempts
assert AUTH_2 in attempts

os.environ[
    "SCALPX_REAL_LIVE_AUTHORIZATION_ID"
] = AUTH_1

reuse_old_auth_service = make_service(
    broker,
)

reuse_old_auth_service._handle_entry_decision(
    execution_decision(
        decision_id="reuse-old-auth"
    ),
    5000,
)

assert broker.calls == 2
assert (
    "r38vwy_real_live_entry_"
    "attempt_already_consumed"
) in reuse_old_auth_service.failures

print(
    "PASS_STRATEGY_MIST_DIRECT_EXACT_SCOPE=1"
)
print(
    "PASS_EXECUTION_MIST_DIRECT_EXACT_SCOPE=1"
)
print(
    "PASS_ATTEMPT_LATCH_PERSISTED_BEFORE_BROKER_CALL=1"
)
print(
    "PASS_SECOND_ATTEMPT_SAME_AUTHORIZATION_BLOCKED=1"
)
print(
    "PASS_RESTART_SAME_AUTHORIZATION_BLOCKED=1"
)
print(
    "PASS_OLD_AUTHORIZATION_REUSE_BLOCKED_AFTER_NEW_AUTH=1"
)
print(
    "PASS_NEW_AUTHORIZATION_ID_CAN_BE_SEPARATELY_CONSUMED=1"
)
print(
    "BROKER_CALL_COUNT=2"
)
print(
    "REAL_REDIS_WRITE_PERFORMED=0"
)
print(
    "REAL_BROKER_REQUEST_PERFORMED=0"
)
print(
    "CLASSIFICATION="
    "PASS_R38VWY_REAL_LIVE_EXACT_SCOPE_"
    "DURABLE_ATTEMPT_LATCH_OFFLINE"
)
