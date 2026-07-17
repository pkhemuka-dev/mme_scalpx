#!/usr/bin/env python3
from __future__ import annotations

# R38TMB1_OFFLINE_INTEGRATION_PROOF_V1

from contextlib import contextmanager
import copy
import json
import os
from pathlib import Path
from typing import Any

import app.mme_scalpx.services.strategy as strategy_module
from app.mme_scalpx.services.strategy import (
    StrategyBridgeError,
    StrategyService,
)


ROOT = Path(__file__).resolve().parents[1]

STRATEGY_PATH = (
    ROOT
    / "app/mme_scalpx/services/strategy.py"
)

RESULT_PATH = (
    ROOT
    / "run/proofs/"
      "proof_r38tmb1_active_strategy_exit_integration_offline.json"
)

NOW_NS = 1_783_928_900_000_000_000
LOCAL_OFFSET_NS = 19_800_000_000_000

POLICY_ACK = (
    "R38TK3_FAMILY_CONTRACT_EXIT_V3_TARGET5_STOP4_STRUCTURAL_TIME300"
)

SCOPE_ACK = (
    "R38TMB1_EXACT_OPEN_POSITION_ONE_LOT_ONE_EVENT_NO_REAL_LIVE_NO_BROKER"
)

CALL_SYMBOL = "NIFTY2671424100CE"
CALL_TOKEN = "13152002"

PUT_SYMBOL = "NIFTY2671424100PE"
PUT_TOKEN = "13152258"


class DummyShutdown:
    def is_set(self) -> bool:
        return False

    def wait(self, _: float) -> bool:
        return False


class FakeRedis:
    def __init__(
        self,
        *,
        position: dict[str, Any],
        family_surfaces: dict[str, Any],
    ):
        self.position = {
            str(key): str(value)
            for key, value
            in position.items()
        }

        self.feature_hash = {
            "family_surfaces_json":
                json.dumps(
                    family_surfaces,
                    sort_keys=True,
                )
        }

        self.xadd_writes: list[
            tuple[str, dict[str, Any]]
        ] = []

        self.forbidden_writes: list[
            tuple[str, Any]
        ] = []

    def hgetall(self, key):
        key = str(key)

        if key == "state:position:mme":
            return dict(self.position)

        if key == "state:features:mme:fut":
            return dict(
                self.feature_hash
            )

        return {}

    def hget(self, key, field):
        key = str(key)
        field = str(field)

        if (
            key
            == "state:features:mme:fut"
        ):
            return self.feature_hash.get(
                field
            )

        if (
            key
            == "state:position:mme"
        ):
            return self.position.get(
                field
            )

        return None

    def xadd(
        self,
        stream,
        fields,
        *args,
        **kwargs,
    ):
        stream_text = str(stream)

        self.xadd_writes.append(
            (
                stream_text,
                dict(fields),
            )
        )

        return (
            f"{NOW_NS // 1_000_000}-0"
        )

    def hset(self, *args, **kwargs):
        self.forbidden_writes.append(
            ("hset", (args, kwargs))
        )
        raise AssertionError(
            "unexpected_fake_redis_hset"
        )

    def set(self, *args, **kwargs):
        self.forbidden_writes.append(
            ("set", (args, kwargs))
        )
        raise AssertionError(
            "unexpected_fake_redis_set"
        )

    def pexpire(
        self,
        *args,
        **kwargs,
    ):
        self.forbidden_writes.append(
            ("pexpire", (args, kwargs))
        )
        raise AssertionError(
            "unexpected_fake_redis_pexpire"
        )


def local_wallclock_ts(
    age_ms: int,
) -> int:
    return (
        NOW_NS
        + LOCAL_OFFSET_NS
        - age_ms * 1_000_000
    )


def leg(
    *,
    symbol: str,
    token: str,
    bid: str,
    ask: str,
    age_ms: int = 3_000,
) -> dict[str, Any]:
    return {
        "option_symbol": symbol,
        "instrument_token": token,
        "bid": bid,
        "ask": ask,
        "ts_event_ns":
            local_wallclock_ts(
                age_ms
            ),
    }


def surfaces(
    *,
    call_bid: str = "105",
    call_ask: str = "105.20",
    put_bid: str = "55",
    put_ask: str = "55.20",
    age_ms: int = 3_000,
) -> dict[str, Any]:
    call = leg(
        symbol=CALL_SYMBOL,
        token=CALL_TOKEN,
        bid=call_bid,
        ask=call_ask,
        age_ms=age_ms,
    )

    put = leg(
        symbol=PUT_SYMBOL,
        token=PUT_TOKEN,
        bid=put_bid,
        ask=put_ask,
        age_ms=age_ms,
    )

    return {
        "shared_core": {
            "options": {
                "call": {
                    "raw": call,
                },
                "put": {
                    "raw": put,
                },
                "selected": {
                    "raw": call,
                },
            }
        }
    }


def position(
    *,
    branch: str = "CALL",
    family: str = "MIST",
    avg_price: str = "100",
    holding_seconds: int = 10,
    exit_pending: str = "0",
) -> dict[str, Any]:
    if branch == "CALL":
        symbol = CALL_SYMBOL
        token = CALL_TOKEN
        side = "LONG_CALL"
    else:
        symbol = PUT_SYMBOL
        token = PUT_TOKEN
        side = "LONG_PUT"

    return {
        "has_position": "1",
        "position_side": side,
        "qty_lots": "1",
        "qty_units": "65",
        "avg_price": avg_price,
        "entry_price": avg_price,
        "entry_ts_ns": str(
            NOW_NS
            - holding_seconds
            * 1_000_000_000
        ),
        "entry_option_symbol":
            symbol,
        "entry_option_token":
            token,
        "option_symbol": symbol,
        "option_token": token,
        "instrument_token": token,
        "strategy_family_id":
            family,
        "branch_id": branch,
        "entry_strike": "24100",
        # R38TMB1_PROOF_ENTRY_MODE_DIRECT_V2
        # Execution-owned open positions persist canonical entry_mode=DIRECT.
        # CONTROLLED_PAPER_PROJECTED is an order-intent route label and is
        # not an allowed StrategyDecision.entry_mode model value.
        "entry_mode":
            "DIRECT",
        "decision_id":
            "proof-entry-"
            + branch.lower(),
        "broker_order_id":
            "R38KR-PAPER-PROOF",
        "exit_pending":
            exit_pending,
        "mfe_points": "0",
        "mae_points": "0",
    }


def flat_position() -> dict[str, Any]:
    return {
        "has_position": "0",
        "position_side": "FLAT",
        "qty_lots": "0",
        "qty_units": "0",
    }


@contextmanager
def exact_env(
    *,
    branch: str,
    family: str = "MIST",
    enabled: bool = True,
    live_flag: bool = False,
    symbol_override: str = "",
):
    symbol = (
        CALL_SYMBOL
        if branch == "CALL"
        else PUT_SYMBOL
    )

    token = (
        CALL_TOKEN
        if branch == "CALL"
        else PUT_TOKEN
    )

    if symbol_override:
        symbol = symbol_override

    values = {
        "SCALPX_ENABLE_STRATEGY_OWNED_EXIT_MANAGER":
            "1" if enabled else "0",
        "SCALPX_STRATEGY_EXIT_POLICY_ACK":
            POLICY_ACK,
        "SCALPX_STRATEGY_EXIT_SCOPE_ACK":
            SCOPE_ACK,
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME":
            "1",
        "SCALPX_CONTROLLED_PAPER_ARMED":
            "1",
        "SCALPX_PAPER_ARMED":
            "1",
        "SCALPX_CONTROLLED_PAPER_QTY_LOTS":
            "1",
        "SCALPX_CONTROLLED_PAPER_MAX_EVENTS":
            "1",
        "SCALPX_CONTROLLED_PAPER_FAMILY":
            family,
        "SCALPX_CONTROLLED_PAPER_SIDE":
            branch,
        "SCALPX_CONTROLLED_PAPER_BRANCH":
            branch,
        "SCALPX_CONTROLLED_PAPER_OPTION_SYMBOL":
            symbol,
        "SCALPX_CONTROLLED_PAPER_INSTRUMENT_TOKEN":
            token,
        # Entry may remain scoped to ENTER_CALL/ENTER_PUT.
        # The dedicated exit ACK authorizes the strategy-owned close.
        "SCALPX_CONTROLLED_PAPER_ACTION":
            "ENTER_" + branch,
        "SCALPX_OBSERVE_ONLY":
            "0",
        "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY":
            "0",
        "SCALPX_ENABLE_LIVE":
            "1" if live_flag else "0",
        "SCALPX_REAL_LIVE_ALLOWED":
            "0",
        "SCALPX_ALLOW_REAL_LIVE":
            "0",
        "SCALPX_ALLOW_BROKER_ORDERS":
            "0",
        "SCALPX_BROKER_ORDER_ENABLED":
            "0",
        "MME_ENABLE_LIVE":
            "0",
        "MME_ALLOW_LIVE_ORDER":
            "0",
    }

    old = {
        key: os.environ.get(key)
        for key in values
    }

    try:
        os.environ.update(values)
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(
                    key,
                    None,
                )
            else:
                os.environ[key] = value


def make_service(
    *,
    position_state:
        dict[str, Any],
    family_surfaces:
        dict[str, Any],
):
    fake = FakeRedis(
        position=position_state,
        family_surfaces=(
            family_surfaces
        ),
    )

    service = StrategyService(
        redis_client=fake,
        clock=object(),
        shutdown=DummyShutdown(),
        instance_id=(
            "r38tmb1-offline-proof"
        ),
        settings=None,
    )

    service._now_ns = (
        lambda: NOW_NS
    )

    return service, fake


def decision_stream_writes(
    fake: FakeRedis,
):
    return [
        (stream, fields)
        for stream, fields
        in fake.xadd_writes
        if "decision" in stream.lower()
    ]


def order_stream_writes(
    fake: FakeRedis,
):
    return [
        (stream, fields)
        for stream, fields
        in fake.xadd_writes
        if "order" in stream.lower()
    ]


def parse_payload_json(
    fields: dict[str, Any],
) -> dict[str, Any]:
    raw = fields.get(
        "payload_json"
    )

    if isinstance(raw, bytes):
        raw = raw.decode(
            "utf-8",
            errors="replace",
        )

    if isinstance(raw, dict):
        return dict(raw)

    assert isinstance(raw, str), (
        fields
    )

    parsed = json.loads(raw)

    assert isinstance(
        parsed,
        dict,
    )

    return parsed


def assert_exit_publish(
    *,
    service: StrategyService,
    fake: FakeRedis,
    expected_reason: str,
    expected_branch: str,
    expected_symbol: str,
    expected_token: str,
):
    result = service.run_once()

    assert result["action"] == "EXIT"
    assert (
        result["position_effect"]
        == "CLOSE"
    )
    assert (
        result["reason"]
        == expected_reason
    )
    assert (
        result["branch_id"]
        == expected_branch
    )
    assert (
        result["option_symbol"]
        == expected_symbol
    )
    assert (
        result["option_token"]
        == expected_token
    )
    assert (
        result[
            "r38tmb1_strategy_owned_exit"
        ]
        == 1
    )
    assert (
        result[
            "r38tmb1_exit_latched"
        ]
        == 1
    )

    writes = decision_stream_writes(
        fake
    )

    assert len(writes) == 1, (
        fake.xadd_writes
    )

    assert not order_stream_writes(
        fake
    )

    assert not fake.forbidden_writes

    _, fields = writes[0]

    assert str(
        fields.get("action")
    ).upper() == "EXIT"

    payload = parse_payload_json(
        fields
    )

    assert payload["action"] == "EXIT"
    assert (
        payload["position_effect"]
        == "CLOSE"
    )
    assert (
        payload["option_symbol"]
        == expected_symbol
    )
    assert (
        payload["option_token"]
        == expected_token
    )
    assert (
        payload[
            "r38tmb1_strategy_owned_exit"
        ]
        == 1
    )

    return result, payload


def main() -> int:
    report: dict[
        str,
        Any,
    ] = {
        "classification":
            "PASS_R38TMB1_ACTIVE_STRATEGY_EXIT_GATE_INTEGRATION_OFFLINE",
        "scenarios": {},
    }

    # 1. CALL target publishes one canonical EXIT.
    with exact_env(
        branch="CALL",
    ):
        service, fake = make_service(
            position_state=position(
                branch="CALL",
                avg_price="100",
                holding_seconds=10,
            ),
            family_surfaces=surfaces(
                call_bid="105",
                call_ask="105.20",
            ),
        )

        target_result, target_payload = (
            assert_exit_publish(
                service=service,
                fake=fake,
                expected_reason=(
                    "target_points"
                ),
                expected_branch="CALL",
                expected_symbol=CALL_SYMBOL,
                expected_token=CALL_TOKEN,
            )
        )

        # Same open position cannot publish a second EXIT.
        duplicate_result = (
            service.run_once()
        )

        assert (
            duplicate_result["action"]
            == "HOLD"
        )
        assert (
            duplicate_result["reason"]
            == "R38TMB1_EXIT_ALREADY_LATCHED"
        )
        assert len(
            decision_stream_writes(
                fake
            )
        ) == 1

        report["scenarios"][
            "call_target"
        ] = {
            "decision_id":
                target_result[
                    "decision_id"
                ],
            "payload":
                target_payload,
            "duplicate_suppressed":
                True,
        }

    # 2. CALL hard stop.
    with exact_env(
        branch="CALL",
    ):
        service, fake = make_service(
            position_state=position(
                branch="CALL",
                avg_price="100",
            ),
            family_surfaces=surfaces(
                call_bid="96",
                call_ask="96.20",
            ),
        )

        assert_exit_publish(
            service=service,
            fake=fake,
            expected_reason=(
                "hard_stop_points"
            ),
            expected_branch="CALL",
            expected_symbol=CALL_SYMBOL,
            expected_token=CALL_TOKEN,
        )

        report["scenarios"][
            "call_hard_stop"
        ] = True

    # 3. CALL time stop.
    with exact_env(
        branch="CALL",
    ):
        service, fake = make_service(
            position_state=position(
                branch="CALL",
                avg_price="100",
                holding_seconds=301,
            ),
            family_surfaces=surfaces(
                call_bid="100.50",
                call_ask="100.70",
            ),
        )

        assert_exit_publish(
            service=service,
            fake=fake,
            expected_reason=(
                "max_hold_seconds"
            ),
            expected_branch="CALL",
            expected_symbol=CALL_SYMBOL,
            expected_token=CALL_TOKEN,
        )

        report["scenarios"][
            "call_time_stop"
        ] = True

    # 4. PUT target.
    with exact_env(
        branch="PUT",
    ):
        service, fake = make_service(
            position_state=position(
                branch="PUT",
                avg_price="50",
            ),
            family_surfaces=surfaces(
                put_bid="55",
                put_ask="55.20",
            ),
        )

        assert_exit_publish(
            service=service,
            fake=fake,
            expected_reason=(
                "target_points"
            ),
            expected_branch="PUT",
            expected_symbol=PUT_SYMBOL,
            expected_token=PUT_TOKEN,
        )

        report["scenarios"][
            "put_target"
        ] = True

    # 5. Open position, no exit trigger:
    # no ENTER and no Redis publication.
    with exact_env(
        branch="CALL",
    ):
        service, fake = make_service(
            position_state=position(
                branch="CALL",
                avg_price="100",
                holding_seconds=10,
            ),
            family_surfaces=surfaces(
                call_bid="102",
                call_ask="102.20",
            ),
        )

        result = service.run_once()

        assert result["action"] == "HOLD"
        assert result[
            "r38tmb1_open_position_entry_suppressed"
        ] == 1
        assert not fake.xadd_writes
        assert not fake.forbidden_writes

        report["scenarios"][
            "open_position_no_exit"
        ] = True

    # 6. Stale exact quote fails closed.
    with exact_env(
        branch="CALL",
    ):
        service, fake = make_service(
            position_state=position(
                branch="CALL",
            ),
            family_surfaces=surfaces(
                call_bid="105",
                call_ask="105.20",
                age_ms=6_001,
            ),
        )

        result = service.run_once()

        assert result["action"] == "HOLD"
        assert result["reason"].startswith(
            "R38TMB1_QUOTE_BLOCKED:"
        )
        assert not fake.xadd_writes

        report["scenarios"][
            "stale_quote_blocked"
        ] = True

    # 7. Exit manager disabled.
    with exact_env(
        branch="CALL",
        enabled=False,
    ):
        service, fake = make_service(
            position_state=position(),
            family_surfaces=surfaces(),
        )

        result = service.run_once()

        assert result["action"] == "HOLD"
        assert (
            "EXIT_MANAGER_NOT_ENABLED"
            in result["reason"]
        )
        assert not fake.xadd_writes

        report["scenarios"][
            "manager_disabled"
        ] = True

    # 8. Exact symbol mismatch.
    with exact_env(
        branch="CALL",
        symbol_override=(
            "NIFTY2671424200CE"
        ),
    ):
        service, fake = make_service(
            position_state=position(),
            family_surfaces=surfaces(),
        )

        result = service.run_once()

        assert result["action"] == "HOLD"
        assert (
            "SYMBOL_SCOPE_MISMATCH"
            in result["reason"]
        )
        assert not fake.xadd_writes

        report["scenarios"][
            "symbol_scope_blocked"
        ] = True

    # 9. Any live flag blocks exit publication.
    with exact_env(
        branch="CALL",
        live_flag=True,
    ):
        service, fake = make_service(
            position_state=position(),
            family_surfaces=surfaces(),
        )

        result = service.run_once()

        assert result["action"] == "HOLD"
        assert (
            "SCALPX_ENABLE_LIVE_MUST_BE_FALSE"
            in result["reason"]
        )
        assert not fake.xadd_writes

        report["scenarios"][
            "live_flag_blocked"
        ] = True

    # 10. MISO excluded.
    with exact_env(
        branch="CALL",
        family="MISO",
    ):
        service, fake = make_service(
            position_state=position(
                family="MISO",
            ),
            family_surfaces=surfaces(),
        )

        result = service.run_once()

        assert result["action"] == "HOLD"
        assert (
            "FAMILY_NOT_ELIGIBLE"
            in result["reason"]
        )
        assert not fake.xadd_writes

        report["scenarios"][
            "miso_excluded"
        ] = True

    # 11. Execution-owned exit_pending suppresses duplicate.
    with exact_env(
        branch="CALL",
    ):
        service, fake = make_service(
            position_state=position(
                exit_pending="1",
            ),
            family_surfaces=surfaces(),
        )

        result = service.run_once()

        assert result["action"] == "HOLD"
        assert (
            "EXIT_ALREADY_PENDING"
            in result["reason"]
        )
        assert not fake.xadd_writes

        report["scenarios"][
            "exit_pending_suppressed"
        ] = True

    # 12. Forged EXIT is rejected by HOLD validator.
    forged = copy.deepcopy(
        target_result
    )
    forged[
        "r38tmb1_strategy_owned_exit"
    ] = 0

    metadata = dict(
        forged.get("metadata") or {}
    )
    metadata[
        "r38tmb1_strategy_owned_exit"
    ] = 0
    forged["metadata"] = metadata

    rejected = False

    try:
        strategy_module._validate_hold_decision_for_publish(
            forged
        )
    except StrategyBridgeError:
        rejected = True

    assert rejected

    report["scenarios"][
        "forged_exit_rejected"
    ] = True

    # 13. FLAT state preserves the original entry/HOLD path.
    original_run_once = (
        strategy_module
        ._R38TMB1_ORIGINAL_RUN_ONCE
    )

    strategy_module._R38TMB1_ORIGINAL_RUN_ONCE = (
        lambda self: {
            "action": "HOLD",
            "reason":
                "ORIGINAL_FLAT_PATH_CALLED",
        }
    )

    try:
        with exact_env(
            branch="CALL",
        ):
            service, fake = make_service(
                position_state=(
                    flat_position()
                ),
                family_surfaces=surfaces(),
            )

            flat_result = (
                service.run_once()
            )

            assert (
                flat_result["reason"]
                == "ORIGINAL_FLAT_PATH_CALLED"
            )
            assert not fake.xadd_writes
    finally:
        strategy_module._R38TMB1_ORIGINAL_RUN_ONCE = (
            original_run_once
        )

    report["scenarios"][
        "flat_original_path"
    ] = True

    # 14. Static block safety.
    source = STRATEGY_PATH.read_text()

    marker = (
        "# BEGIN "
        "R38TMB1_ACTIVE_STRATEGY_EXIT_GATE_V1"
    )

    assert source.count(marker) == 1

    block = source.split(
        marker,
        1,
    )[1]

    forbidden_direct_tokens = (
        "orders:mme:stream",
        "risk:mme:stream",
        "execution:mme:stream",
        "place_entry_order(",
        "place_exit_order(",
        ".hset(",
        ".set(",
        ".xadd(",
    )

    present = [
        token
        for token
        in forbidden_direct_tokens
        if token in block
    ]

    assert not present, present

    report.update(
        {
            "scenario_count":
                len(
                    report["scenarios"]
                ),
            "target_exit":
                "PASS",
            "hard_stop_exit":
                "PASS",
            "time_stop_exit":
                "PASS",
            "put_exit":
                "PASS",
            "duplicate_suppression":
                "PASS",
            "open_position_entry_suppression":
                "PASS",
            "exact_gate_fail_closed":
                "PASS",
            "forged_exit_rejection":
                "PASS",
            "flat_original_path":
                "PASS",
            "proof_position_entry_mode":
                "DIRECT",
            "proof_entry_mode_contract":
                "EXECUTION_OWNED_CANONICAL_MODEL_VALUE",
            "direct_order_stream_write":
                False,
            "direct_risk_stream_write":
                False,
            "direct_execution_stream_write":
                False,
            "broker_call":
                False,
            "real_redis_used":
                False,
        }
    )

    RESULT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RESULT_PATH.write_text(
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
        "PASS_R38TMB1_ACTIVE_STRATEGY_EXIT_GATE_INTEGRATION_OFFLINE"
    )
    print(
        "SCENARIO_COUNT="
        + str(
            report[
                "scenario_count"
            ]
        )
    )
    print(
        "CALL_TARGET_EXIT_PUBLISH=PASS"
    )
    print(
        "CALL_HARD_STOP_EXIT_PUBLISH=PASS"
    )
    print(
        "CALL_TIME_STOP_EXIT_PUBLISH=PASS"
    )
    print(
        "PUT_TARGET_EXIT_PUBLISH=PASS"
    )
    print(
        "POSITION_EFFECT=CLOSE"
    )
    print(
        "EXACT_SYMBOL_TOKEN_PUBLICATION=PASS"
    )
    print(
        "CANONICAL_PAYLOAD_JSON_EXIT=PASS"
    )
    print(
        "LOCAL_EXIT_LATCH_DUPLICATE_SUPPRESSION=PASS"
    )
    print(
        "EXECUTION_EXIT_PENDING_SUPPRESSION=PASS"
    )
    print(
        "OPEN_POSITION_NEW_ENTER_SUPPRESSION=PASS"
    )
    print(
        "STALE_QUOTE_FAIL_CLOSED=PASS"
    )
    print(
        "EXACT_SCOPE_MISMATCH_FAIL_CLOSED=PASS"
    )
    print(
        "LIVE_FLAG_FAIL_CLOSED=PASS"
    )
    print(
        "MISO_EXCLUDED=PASS"
    )
    print(
        "FORGED_EXIT_VALIDATOR_REJECTION=PASS"
    )
    print(
        "FLAT_ORIGINAL_ENTRY_PATH_PRESERVED=PASS"
    )
    print(
        "PROOF_POSITION_ENTRY_MODE=DIRECT"
    )
    print(
        "DIRECT_ORDER_RISK_EXECUTION_WRITE=0"
    )
    print(
        "BROKER_CALLS=0"
    )
    print(
        "REAL_REDIS_USED=0"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
