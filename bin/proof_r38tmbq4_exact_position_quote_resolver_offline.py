#!/usr/bin/env python3
from __future__ import annotations

# R38TMBQ4_OFFLINE_PROOF_V1

import ast
import json
from pathlib import Path
from typing import Any

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family.exact_position_quote_resolver import (
    CALL_PATH,
    PUT_PATH,
    RESOLVER_VERSION,
    ExactPositionQuoteResolver,
)
from app.mme_scalpx.services.strategy_family.position_exit_manager import (
    POLICY_VERSION,
    PositionExitManager,
)


ROOT = Path(__file__).resolve().parents[1]

MODULE_PATH = (
    ROOT
    / "app/mme_scalpx/services/"
      "strategy_family/"
      "exact_position_quote_resolver.py"
)

OUTPUT = (
    ROOT
    / "run/proofs/"
      "proof_r38tmbq4_exact_position_quote_resolver_offline.json"
)

NOW_NS = 1_783_928_900_000_000_000
LOCAL_OFFSET_NS = 19_800_000_000_000

CALL_SYMBOL = "NIFTY2671424100CE"
CALL_TOKEN = "13152002"

PUT_SYMBOL = "NIFTY2671424100PE"
PUT_TOKEN = "13152258"


def leg(
    *,
    symbol: str,
    token: str,
    bid: str,
    ask: str,
    ts_event_ns: int,
) -> dict[str, Any]:
    return {
        "option_symbol": symbol,
        "instrument_token": token,
        "bid": bid,
        "ask": ask,
        "ts_event_ns":
            ts_event_ns,
    }


def surface(
    *,
    call: dict[str, Any] | None,
    put: dict[str, Any] | None,
    selected: dict[str, Any] | None,
) -> dict[str, Any]:
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
                    "raw": selected,
                },
            }
        }
    }


def position_call(
    *,
    avg_price: str = "100",
    entry_ts_ns: int = (
        NOW_NS - 10_000_000_000
    ),
) -> dict[str, Any]:
    return {
        "has_position": "1",
        "position_side": "LONG_CALL",
        "qty_lots": "1",
        "qty_units": "65",
        "avg_price": avg_price,
        "entry_ts_ns":
            str(entry_ts_ns),
        "entry_option_symbol":
            CALL_SYMBOL,
        "entry_option_token":
            CALL_TOKEN,
        "strategy_family_id":
            "MIST",
        "branch_id": "CALL",
        "entry_strike": "24100",
        "entry_mode": "DIRECT",
        "decision_id":
            "proof-entry-call",
        "broker_order_id":
            "proof-order-call",
    }


def position_put() -> dict[str, Any]:
    return {
        "has_position": "1",
        "position_side": "LONG_PUT",
        "qty_lots": "1",
        "qty_units": "65",
        "avg_price": "50",
        "entry_ts_ns":
            str(
                NOW_NS
                - 10_000_000_000
            ),
        "entry_option_symbol":
            PUT_SYMBOL,
        "entry_option_token":
            PUT_TOKEN,
        "strategy_family_id":
            "MIST",
        "branch_id": "PUT",
        "entry_strike": "24100",
        "entry_mode": "DIRECT",
        "decision_id":
            "proof-entry-put",
        "broker_order_id":
            "proof-order-put",
    }


def local_wallclock_ts(
    age_ms: int,
) -> int:
    return (
        NOW_NS
        + LOCAL_OFFSET_NS
        - age_ms * 1_000_000
    )


def epoch_ts(
    age_ms: int,
) -> int:
    return (
        NOW_NS
        - age_ms * 1_000_000
    )


def _canonical_payload_value(
    payload: dict[str, Any],
    *names: str,
) -> Any:
    """
    Read canonical decision identity without assuming that
    contract fields are top-level.

    Active StrategyDecision.to_dict() may keep option identity
    inside metadata. ExecutionService already accepts that
    canonical shape.
    """
    containers: list[dict[str, Any]] = [
        payload,
    ]

    for container_name in (
        "metadata",
        "contract",
        "instrument",
        "quote",
    ):
        candidate = payload.get(
            container_name
        )

        if isinstance(candidate, str):
            try:
                candidate = json.loads(
                    candidate
                )
            except Exception:
                candidate = None

        if isinstance(candidate, dict):
            containers.append(
                candidate
            )

    for container in containers:
        for name in names:
            value = container.get(name)

            if value not in (
                None,
                "",
            ):
                return value

    return ""


# R38TMBQ4_PAYLOAD_METADATA_COMPAT_PROOF_V2
def main() -> int:
    resolver = (
        ExactPositionQuoteResolver()
    )

    manager = PositionExitManager()

    scenarios: dict[
        str,
        dict[str, Any],
    ] = {}

    # 1. CALL resolves from call.raw.
    # selected.raw intentionally points to PUT.
    local_call_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="105",
            ask="105.20",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="53.40",
            ask="53.50",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="53.40",
            ask="53.50",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
    )

    call_result = resolver.resolve(
        family_surfaces=(
            local_call_surface
        ),
        position=position_call(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert call_result.resolved
    assert not call_result.blocked
    assert call_result.quote is not None
    assert (
        call_result.quote[
            "quote_owner_path"
        ]
        == CALL_PATH
    )
    assert (
        call_result.quote[
            "timestamp_domain"
        ]
        == "LOCAL_WALLCLOCK_AS_EPOCH_NS"
    )
    assert (
        call_result.quote[
            "option_symbol"
        ]
        == CALL_SYMBOL
    )
    assert (
        call_result.quote[
            "option_token"
        ]
        == CALL_TOKEN
    )
    assert (
        call_result.quote[
            "bid"
        ]
        == "105"
    )
    assert (
        call_result.quote[
            "ts_event_ns"
        ]
        == epoch_ts(3_000)
    )

    scenarios[
        "local_wallclock_call"
    ] = call_result.to_dict()

    # 2. PUT resolves from put.raw even when selected=CALL.
    put_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="158.55",
            ask="158.85",
            ts_event_ns=(
                local_wallclock_ts(
                    2_500
                )
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="54.05",
            ask="54.20",
            ts_event_ns=(
                local_wallclock_ts(
                    2_500
                )
            ),
        ),
        selected=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="158.55",
            ask="158.85",
            ts_event_ns=(
                local_wallclock_ts(
                    2_500
                )
            ),
        ),
    )

    put_result = resolver.resolve(
        family_surfaces=put_surface,
        position=position_put(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert put_result.resolved
    assert put_result.quote is not None
    assert (
        put_result.quote[
            "quote_owner_path"
        ]
        == PUT_PATH
    )
    assert (
        put_result.quote[
            "option_symbol"
        ]
        == PUT_SYMBOL
    )
    assert (
        put_result.quote[
            "option_token"
        ]
        == PUT_TOKEN
    )

    scenarios[
        "local_wallclock_put"
    ] = put_result.to_dict()

    # 3. Genuine epoch timestamp remains supported.
    epoch_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="102",
            ask="102.20",
            ts_event_ns=epoch_ts(
                2_000
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="50",
            ask="50.10",
            ts_event_ns=epoch_ts(
                2_000
            ),
        ),
        selected=None,
    )

    epoch_result = resolver.resolve(
        family_surfaces=epoch_surface,
        position=position_call(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert epoch_result.resolved
    assert epoch_result.quote is not None
    assert (
        epoch_result.quote[
            "timestamp_domain"
        ]
        == "UNIX_EPOCH_NS"
    )

    scenarios[
        "epoch_timestamp"
    ] = epoch_result.to_dict()

    # 4. Stale quote rejected.
    stale_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="105",
            ask="105.20",
            ts_event_ns=(
                local_wallclock_ts(
                    6_001
                )
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="50",
            ask="50.10",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=None,
    )

    stale_result = resolver.resolve(
        family_surfaces=stale_surface,
        position=position_call(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert stale_result.blocked
    assert (
        stale_result.reason_code
        == "exact_position_quote_stale_or_future"
    )

    scenarios[
        "stale_quote"
    ] = stale_result.to_dict()

    # 5. Quote too far in future rejected.
    future_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="105",
            ask="105.20",
            ts_event_ns=(
                NOW_NS
                + LOCAL_OFFSET_NS
                + 2_000_000_000
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="50",
            ask="50.10",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=None,
    )

    future_result = resolver.resolve(
        family_surfaces=future_surface,
        position=position_call(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert future_result.blocked
    assert (
        future_result.reason_code
        == "exact_position_quote_stale_or_future"
    )

    scenarios[
        "future_quote"
    ] = future_result.to_dict()

    # 6. Symbol mismatch rejected.
    symbol_mismatch = (
        position_call()
    )
    symbol_mismatch[
        "entry_option_symbol"
    ] = "NIFTY2671424200CE"

    symbol_result = resolver.resolve(
        family_surfaces=(
            local_call_surface
        ),
        position=symbol_mismatch,
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert symbol_result.blocked
    assert (
        symbol_result.reason_code
        == "exact_position_quote_not_found"
    )

    scenarios[
        "symbol_mismatch"
    ] = symbol_result.to_dict()

    # 7. Token mismatch rejected.
    token_mismatch = position_call()
    token_mismatch[
        "entry_option_token"
    ] = "99999999"

    token_result = resolver.resolve(
        family_surfaces=(
            local_call_surface
        ),
        position=token_mismatch,
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert token_result.blocked
    assert (
        token_result.reason_code
        == "exact_position_quote_not_found"
    )

    scenarios[
        "token_mismatch"
    ] = token_result.to_dict()

    # 8. Position branch mismatch rejected.
    branch_mismatch = position_call()
    branch_mismatch[
        "branch_id"
    ] = "PUT"
    branch_mismatch[
        "position_side"
    ] = "LONG_PUT"

    branch_result = resolver.resolve(
        family_surfaces=(
            local_call_surface
        ),
        position=branch_mismatch,
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert branch_result.blocked
    assert (
        branch_result.reason_code
        == "position_branch_quote_mismatch"
    )

    scenarios[
        "branch_mismatch"
    ] = branch_result.to_dict()

    # 9. Duplicate exact identity rejected as ambiguous.
    duplicate_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="105",
            ask="105.20",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        put=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="105",
            ask="105.20",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=None,
    )

    duplicate_result = resolver.resolve(
        family_surfaces=(
            duplicate_surface
        ),
        position=position_call(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert duplicate_result.blocked
    assert (
        duplicate_result.reason_code
        == "exact_position_quote_ambiguous"
    )

    scenarios[
        "duplicate_identity"
    ] = duplicate_result.to_dict()

    # 10. Crossed BID/ASK rejected.
    crossed_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="106",
            ask="105",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="50",
            ask="50.10",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=None,
    )

    crossed_result = resolver.resolve(
        family_surfaces=(
            crossed_surface
        ),
        position=position_call(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert crossed_result.blocked
    assert (
        crossed_result.reason_code
        == "exact_position_bid_ask_invalid"
    )

    scenarios[
        "crossed_bid_ask"
    ] = crossed_result.to_dict()

    # 11. Missing CALL path rejected.
    missing_call_surface = surface(
        call=None,
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="50",
            ask="50.10",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=None,
    )

    missing_result = resolver.resolve(
        family_surfaces=(
            missing_call_surface
        ),
        position=position_call(),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert missing_result.blocked
    assert (
        missing_result.reason_code
        == "exact_position_quote_not_found"
    )

    scenarios[
        "missing_call_path"
    ] = missing_result.to_dict()

    # 12. Flat position rejected.
    flat_position = position_call()
    flat_position.update(
        {
            "has_position": "0",
            "position_side": "FLAT",
            "qty_lots": "0",
            "qty_units": "0",
        }
    )

    flat_result = resolver.resolve(
        family_surfaces=(
            local_call_surface
        ),
        position=flat_position,
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert flat_result.blocked
    assert (
        flat_result.reason_code
        == "position_not_open"
    )

    scenarios[
        "flat_position"
    ] = flat_result.to_dict()

    # 13. Resolver output drives target EXIT.
    target_evaluation = manager.evaluate(
        now_ns=NOW_NS,
        family_id="MIST",
        position=position_call(
            avg_price="100"
        ),
        quote=call_result.quote,
        signal_changed=False,
    )

    assert target_evaluation.should_exit
    assert (
        target_evaluation.reason_code
        == "target_points"
    )
    assert (
        target_evaluation.decision
        is not None
    )

    target_payload = (
        target_evaluation
        .decision
        .to_dict()
    )

    assert (
        target_payload["action"]
        == N.ACTION_EXIT
    )
    assert (
        target_payload[
            "position_effect"
        ]
        == N.POSITION_EFFECT_CLOSE
    )
    # R38TMBQ4_SYMBOL_NOT_INSTRUMENT_KEY_COMPAT_V3
    # Active manager payload semantics:
    #   top-level instrument_key = option token
    #   metadata.option_symbol = trading symbol
    target_symbol = str(
        _canonical_payload_value(
            target_payload,
            "option_symbol",
            "trading_symbol",
            "tradingsymbol",
            "symbol",
        )
    ).strip().upper()

    if ":" in target_symbol:
        target_symbol = target_symbol.split(
            ":",
            1,
        )[1]

    target_token = str(
        _canonical_payload_value(
            target_payload,
            "option_token",
            "instrument_token",
            "token",
        )
    ).strip()

    assert target_symbol == CALL_SYMBOL, (
        target_payload
    )
    assert target_token == CALL_TOKEN, (
        target_payload
    )

    top_level_instrument_key = str(
        target_payload.get(
            "instrument_key",
            "",
        )
    ).strip()

    assert (
        top_level_instrument_key
        == CALL_TOKEN
    ), target_payload

    # 14. Resolver output drives hard-stop EXIT.
    stop_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="96",
            ask="96.20",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="50",
            ask="50.10",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=None,
    )

    stop_quote = resolver.resolve(
        family_surfaces=stop_surface,
        position=position_call(
            avg_price="100"
        ),
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert stop_quote.resolved
    assert stop_quote.quote is not None

    stop_evaluation = manager.evaluate(
        now_ns=NOW_NS,
        family_id="MIST",
        position=position_call(
            avg_price="100"
        ),
        quote=stop_quote.quote,
        signal_changed=False,
    )

    assert stop_evaluation.should_exit
    assert (
        stop_evaluation.reason_code
        == "hard_stop_points"
    )

    # 15. Resolver output drives time-stop EXIT.
    time_position = position_call(
        avg_price="100",
        entry_ts_ns=(
            NOW_NS
            - 301_000_000_000
        ),
    )

    time_surface = surface(
        call=leg(
            symbol=CALL_SYMBOL,
            token=CALL_TOKEN,
            bid="100.50",
            ask="100.70",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        put=leg(
            symbol=PUT_SYMBOL,
            token=PUT_TOKEN,
            bid="50",
            ask="50.10",
            ts_event_ns=(
                local_wallclock_ts(
                    3_000
                )
            ),
        ),
        selected=None,
    )

    time_quote = resolver.resolve(
        family_surfaces=time_surface,
        position=time_position,
        now_ns=NOW_NS,
        local_utc_offset_ns=(
            LOCAL_OFFSET_NS
        ),
    )

    assert time_quote.resolved
    assert time_quote.quote is not None

    time_evaluation = manager.evaluate(
        now_ns=NOW_NS,
        family_id="MIST",
        position=time_position,
        quote=time_quote.quote,
        signal_changed=False,
    )

    assert time_evaluation.should_exit
    assert (
        time_evaluation.reason_code
        == "max_hold_seconds"
    )

    # 16. Static purity proof.
    module_source = MODULE_PATH.read_text()
    ast.parse(module_source)

    forbidden = [
        "import redis",
        "from redis",
        ".xadd(",
        ".hset(",
        ".set(",
        "place_entry_order",
        "place_exit_order",
        "broker.",
    ]

    present_forbidden = [
        token
        for token in forbidden
        if token in module_source
    ]

    assert not present_forbidden, (
        present_forbidden
    )

    assert (
        "SELECTED_PATH"
        in module_source
    )
    assert (
        "diagnostic_alias_only"
        in module_source
    )
    assert (
        "LOCAL_WALLCLOCK_AS_EPOCH_NS"
        in module_source
    )
    assert (
        "exact_position_quote_ambiguous"
        in module_source
    )

    report = {
        "classification":
            "PASS_R38TMBQ4_PURE_EXACT_POSITION_QUOTE_RESOLVER_OFFLINE",
        "resolver_version":
            RESOLVER_VERSION,
        "manager_policy_version":
            POLICY_VERSION,
        "scenario_count":
            len(scenarios),
        "scenarios": scenarios,
        "manager_integration": {
            "target_reason":
                target_evaluation.reason_code,
            "hard_stop_reason":
                stop_evaluation.reason_code,
            "time_stop_reason":
                time_evaluation.reason_code,
            "position_effect":
                target_payload[
                    "position_effect"
                ],
            "exact_symbol":
                target_symbol,
            "exact_token":
                target_token,
            "decision_top_level_keys":
                sorted(
                    target_payload.keys()
                ),
            "identity_source":
                "metadata_option_symbol_and_metadata_option_token",
            "top_level_instrument_key":
                top_level_instrument_key,
            "top_level_instrument_key_semantics":
                "OPTION_TOKEN_NOT_SYMBOL",
        },
        "selected_alias_used_as_owner":
            False,
        "redis_used": False,
        "broker_used": False,
        "runtime_started": False,
        "strategy_modified": False,
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
        "PASS_R38TMBQ4_PURE_EXACT_POSITION_QUOTE_RESOLVER_OFFLINE"
    )
    print(
        "RESOLVER_VERSION="
        + RESOLVER_VERSION
    )
    print(
        "SCENARIO_COUNT="
        + str(len(scenarios))
    )
    print(
        "CALL_LOCAL_WALLCLOCK_RESOLUTION=PASS"
    )
    print(
        "PUT_LOCAL_WALLCLOCK_RESOLUTION=PASS"
    )
    print(
        "RAW_EPOCH_RESOLUTION=PASS"
    )
    print(
        "SELECTED_ALIAS_IGNORED_FOR_OWNERSHIP=PASS"
    )
    print(
        "STALE_QUOTE_REJECTION=PASS"
    )
    print(
        "FUTURE_QUOTE_REJECTION=PASS"
    )
    print(
        "SYMBOL_MISMATCH_REJECTION=PASS"
    )
    print(
        "TOKEN_MISMATCH_REJECTION=PASS"
    )
    print(
        "BRANCH_MISMATCH_REJECTION=PASS"
    )
    print(
        "DUPLICATE_IDENTITY_REJECTION=PASS"
    )
    print(
        "CROSSED_BID_ASK_REJECTION=PASS"
    )
    print(
        "FLAT_POSITION_REJECTION=PASS"
    )
    print(
        "TARGET_EXIT_MANAGER_INTEGRATION=PASS"
    )
    print(
        "HARD_STOP_EXIT_MANAGER_INTEGRATION=PASS"
    )
    print(
        "TIME_STOP_EXIT_MANAGER_INTEGRATION=PASS"
    )
    print(
        "POSITION_EFFECT=CLOSE"
    )
    print(
        "TARGET_SYMBOL_CANONICAL_METADATA_COMPAT=PASS"
    )
    print(
        "TARGET_TOKEN_CANONICAL_METADATA_COMPAT=PASS"
    )
    print(
        "TOP_LEVEL_INSTRUMENT_KEY_TOKEN_SEMANTICS=PASS"
    )
    print(
        "PURE_NO_REDIS_BROKER_CALLS=1"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
