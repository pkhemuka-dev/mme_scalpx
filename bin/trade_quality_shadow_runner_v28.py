from __future__ import annotations

"""Read-only live/shadow adapter for Trade Quality Authorization Gate v28.

Reads existing Redis streams and state, creates no candidate, writes no Redis data,
and places no paper/broker order. Authorization records are appended to local NDJSON.
"""

import argparse
import json
import os
import subprocess
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.core.redisx import get_redis_client
from app.mme_scalpx.shadow_paper.trade_quality_authorization_gate_v28 import (
    GateConfig,
    ObservationState,
    config_from_json,
    evaluate,
)

DECISION_STREAM = "decisions:mme:stream"
FEATURE_STREAMS = ("features:mme:stream", "features:mme:fut:stream")
OPTION_STREAMS = (
    "ticks:mme:opt:selected:zerodha:stream",
    "ticks:mme:opt:selected:stream",
    "ticks:mme:opt:stream",
)
FUTURES_STREAMS = ("ticks:mme:fut:zerodha:stream", "ticks:mme:fut:stream")
POSITION_KEY = "state:position:mme"


def text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def mapping(fields: Mapping[Any, Any]) -> dict[str, Any]:
    return {text(k): text(v) for k, v in fields.items()}


def number(value: Any, default: float | None = None) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result


def boolean(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return text(value).strip().lower() in {"1", "true", "yes", "y", "on"}




def object_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}

def nested_json(row: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(row)
    for key in (
        "payload_json", "metadata_json", "activation_selected_json",
        "activation_report_json", "family_scope_candidates_json",
        "family_features_json",
    ):
        raw = row.get(key)
        if not raw:
            continue
        try:
            obj = json.loads(text(raw))
        except Exception:
            continue
        if isinstance(obj, dict):
            merged[key] = obj
            for k, v in obj.items():
                merged.setdefault(k, v)
    metadata = merged.get("metadata")
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except Exception:
            metadata = {}
    if isinstance(metadata, dict):
        merged["metadata"] = metadata
        for k, v in metadata.items():
            merged.setdefault(k, v)
    return merged


def pick(row: Mapping[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return row[key]
    return default


def latest_rows(redis, stream: str, count: int = 1):
    try:
        return redis.xrevrange(stream, count=count)
    except Exception:
        return []


def latest_enter_candidate(redis) -> tuple[str, dict[str, Any]] | None:
    for rid, fields in latest_rows(redis, DECISION_STREAM, count=250):
        row = nested_json(mapping(fields))
        action = text(pick(row, "action", "activation_selected_action", "candidate_action_shadow")).upper()
        if action in {"ENTER_CALL", "ENTER_PUT"}:
            return text(rid), row
    return None


def row_matches(row: Mapping[str, Any], symbol: str, token: str) -> bool:
    row_symbol = text(pick(row, "symbol", "trading_symbol", "tradingsymbol", "option_symbol")).upper()
    row_token = text(pick(row, "instrument_token", "token", "instrument", "option_token"))
    return bool((symbol and row_symbol == symbol) or (token and row_token == token))


def latest_matching_quote(redis, symbol: str, token: str) -> tuple[str, dict[str, Any]] | None:
    for stream in OPTION_STREAMS:
        for rid, fields in latest_rows(redis, stream, count=300):
            row = nested_json(mapping(fields))
            if row_matches(row, symbol, token):
                row["_stream"] = stream
                return text(rid), row
    return None


def latest_feature(redis) -> tuple[str, dict[str, Any]] | None:
    for stream in FEATURE_STREAMS:
        rows = latest_rows(redis, stream, count=1)
        if rows:
            rid, fields = rows[0]
            row = nested_json(mapping(fields))
            row["_stream"] = stream
            return text(rid), row
    return None


def latest_futures(redis) -> tuple[str, dict[str, Any]] | None:
    for stream in FUTURES_STREAMS:
        rows = latest_rows(redis, stream, count=1)
        if rows:
            rid, fields = rows[0]
            row = nested_json(mapping(fields))
            row["_stream"] = stream
            return text(rid), row
    return None


def stream_ms(rid: str) -> int:
    try:
        return int(rid.split("-", 1)[0])
    except Exception:
        return 0


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def newest_broker_report(project: Path, max_age_seconds: int) -> dict[str, Any]:
    now = time.time()
    candidates = sorted(
        project.glob("run/proofs/**/broker/*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in candidates[:100]:
        if now - path.stat().st_mtime > max_age_seconds:
            continue
        obj = load_json(path)
        if obj:
            obj["_path"] = str(path)
            obj["_age_seconds"] = round(now - path.stat().st_mtime, 3)
            return obj
    return {}


def process_count(service: str) -> int:
    cp = subprocess.run(
        ["ps", "-eo", "args="], capture_output=True, text=True, check=False
    )
    needle1 = f"--service {service}"
    needle2 = f"--service={service}"
    return sum(1 for line in cp.stdout.splitlines() if "app.mme_scalpx.main" in line and (needle1 in line or needle2 in line))


def quote_values(row: Mapping[str, Any]) -> dict[str, Any]:
    bid = number(pick(row, "best_bid", "bid", "bid_price"))
    ask = number(pick(row, "best_ask", "ask", "ask_price"))
    ltp = number(pick(row, "ltp", "price", "last_price", "last_traded_price"))
    bid_qty = number(pick(row, "bid_qty", "best_bid_qty", "bid_quantity", "bid_qty_5"), 0.0) or 0.0
    ask_qty = number(pick(row, "ask_qty", "best_ask_qty", "ask_quantity", "ask_qty_5"), 0.0) or 0.0
    spread = (ask - bid) if bid is not None and ask is not None and ask >= bid else None
    mid = (ask + bid) / 2 if bid is not None and ask is not None and ask >= bid else ltp
    return {
        "bid": bid, "ask": ask, "ltp": ltp, "bid_qty": bid_qty,
        "ask_qty": ask_qty, "spread": spread, "mid": mid,
        "tick_size": number(pick(row, "tick_size", "option_tick_size"), 0.05) or 0.05,
    }


def normalized(value: Any, low: float, high: float, reverse: bool = False) -> float:
    x = number(value)
    if x is None or high <= low:
        return 0.0
    score = min(1.0, max(0.0, (x - low) / (high - low)))
    return 1.0 - score if reverse else score


def build_packet(
    decision_id: str,
    decision: Mapping[str, Any],
    feature: Mapping[str, Any],
    futures: Mapping[str, Any],
    quote_id: str,
    quote: Mapping[str, Any],
    position: Mapping[str, Any],
    broker: Mapping[str, Any],
    trigger_memory: Mapping[str, Any],
) -> dict[str, Any]:
    metadata = decision.get("metadata") if isinstance(decision.get("metadata"), dict) else {}
    action = text(pick(decision, "action", "activation_selected_action", "candidate_action_shadow")).upper()
    side = text(pick(decision, "side", "branch_id", "activation_selected_branch_id", "candidate_branch_id_shadow")).upper()
    if not side:
        side = "CALL" if action == "ENTER_CALL" else "PUT" if action == "ENTER_PUT" else ""
    family = text(pick(decision, "family_id", "strategy_family_id", "doctrine_id", "activation_selected_family_id", "candidate_family_id_shadow")).upper()
    symbol = text(pick(decision, "option_symbol", "symbol", "candidate_symbol_shadow", default=metadata.get("option_symbol", ""))).upper()
    token = text(pick(decision, "option_token", "instrument_token", "instrument_key", "candidate_instrument_token_shadow", default=metadata.get("option_token", "")))
    score = number(pick(decision, "activation_selected_score", "confidence", "score", default=metadata.get("confidence")), 0.0) or 0.0
    strike = text(pick(decision, "strike", default=metadata.get("strike", "")))
    q = quote_values(quote)
    now_ms = int(time.time() * 1000)
    quote_age_ms = max(0, now_ms - stream_ms(quote_id)) if quote_id else 10**12
    data_valid = boolean(pick(decision, "data_valid", "safe_to_consume"), False)
    warmup = boolean(pick(decision, "warmup_complete"), False)
    feature_valid = boolean(pick(feature, "frame_valid", "snapshot_valid", "valid", "data_valid"), data_valid)
    packet_gap = number(pick(feature, "packet_gap_ms", "hard_packet_gap_ms", "max_member_age_ms"), 10**12) or 10**12
    fut_price = number(pick(futures, "ltp", "price", "last_price", "last_traded_price", default=pick(feature, "futures_ltp")))
    spot_price = number(pick(feature, "spot_ltp", "underlying_spot", "nifty_spot"), fut_price)
    vwap = number(pick(feature, "vwap", "futures_vwap", "session_vwap"), fut_price)
    vwap_slope = number(pick(feature, "vwap_slope", "futures_vwap_slope"), 0.0) or 0.0
    direction_call = side == "CALL"
    alignment = False
    if fut_price is not None and vwap is not None:
        alignment = fut_price >= vwap if direction_call else fut_price <= vwap
    if fut_price is not None and spot_price is not None:
        alignment = alignment and (fut_price >= spot_price if direction_call else fut_price <= spot_price)
    broker_flat = boolean(broker.get("broker_flat"), False) and int(broker.get("broker_nonflat_position_count", 999)) == 0
    broker_orders_zero = int(broker.get("broker_active_order_count", 999)) == 0
    local_flat = text(position.get("has_position")) == "0" and text(position.get("position_side")).upper() == "FLAT"
    risk_gate_open = process_count("risk") == 0 and process_count("execution") == 0 and local_flat
    spread_cap = number(trigger_memory.get("spread_cap"), None)
    if spread_cap is None and q["spread"] is not None:
        spread_cap = max(q["spread"] * 1.25, 0.25)
    spread_ok = q["spread"] is not None and spread_cap is not None and q["spread"] <= spread_cap
    quote_fresh = quote_age_ms <= 3000
    timeframe_complete = data_valid and warmup and feature_valid
    atr = number(pick(feature, "short_term_atr", "atr", "atr_3m", "futures_atr"), 0.0) or 0.0
    trigger_underlying = number(trigger_memory.get("trigger_underlying_price"), fut_price)
    trigger_mid = number(trigger_memory.get("trigger_option_mid"), q["mid"])
    trigger_spread = number(trigger_memory.get("trigger_spread"), q["spread"])
    target_points = number(pick(decision, "target_points", default=metadata.get("target_points")), 5.0) or 5.0
    spread_points = q["spread"] or 0.0
    conservative_cost = spread_points + max(spread_points, 0.10) + max(spread_points * 0.5, 0.10)

    score01 = min(1.0, max(0.0, score))
    depth_quality = min(1.0, min(q["bid_qty"], q["ask_qty"]) / 500.0)
    spread_quality = 0.0 if q["spread"] is None else normalized(q["spread"], 0.05, max(spread_cap or 1.0, 0.10), reverse=True)
    source_age_quality = normalized(quote_age_ms, 0, 3000, reverse=True)
    packet_gap_quality = normalized(packet_gap, 0, 3000, reverse=True)

    return {
        "family": family,
        "side": side,
        "setup_origin": text(pick(decision, "reason_code", "activation_reason", "explain", default="strategy_candidate")),
        "regime_id": text(pick(feature, "regime_id", "regime", default="UNKNOWN")),
        "trigger_level_bucket": text(pick(decision, "trigger_level_bucket", "strike", default=strike)),
        "selected_symbol": symbol,
        "selected_token": token,
        "strike_classification": text(pick(decision, "strike_classification", "selection_label", default=strike)),
        "observation_window_id": decision_id,
        "direction_owner": "NIFTY_FUTURES_SPOT_VWAP_STRUCTURE",
        "hard_veto_checks": {
            "QUOTE_FRESH": quote_fresh,
            "BID_QTY_VALID": q["bid_qty"] > 0,
            "ASK_QTY_VALID": q["ask_qty"] > 0,
            "SPREAD_ACCEPTABLE": spread_ok,
            "OPTION_SYMBOL_STABLE": bool(symbol and token),
            "INSTRUMENT_LOCK_VALID": bool(symbol and token),
            "UNDERLYING_OPTION_ALIGNED": alignment,
            "NO_CHASE": False,
            "EDGE_AFTER_COST_POSITIVE": False,
            "BROKER_FLAT": broker_flat,
            "ACTIVE_BROKER_ORDERS_ZERO": broker_orders_zero,
            "RISK_GATE_OPEN": risk_gate_open,
            "TIMEFRAME_COMPLETE": timeframe_complete,
            "DATA_GAP_PRESENT": packet_gap > 3000,
            "PENDING_ORDER_PRESENT": not broker_orders_zero,
            "ENTRY_CUTOFF_PASSED": False,
        },
        "components": {
            "regime_15m": {
                "futures_spot_alignment": 1.0 if alignment else 0.0,
                "vwap_relation": 1.0 if alignment else 0.0,
                "vwap_slope": 1.0 if ((vwap_slope >= 0) == direction_call) else 0.0,
                "market_structure": score01,
                "breadth": normalized(pick(feature, "breadth_score", "breadth_alignment"), 0, 1),
            },
            "setup_5m": {
                "strategy_score": score01,
                "data_valid": 1.0 if data_valid else 0.0,
                "warmup": 1.0 if warmup else 0.0,
                "feature_valid": 1.0 if feature_valid else 0.0,
                "packet_gap_quality": packet_gap_quality,
            },
            "trigger_3m": {
                "natural_enter_action": 1.0 if action in {"ENTER_CALL", "ENTER_PUT"} else 0.0,
                "safe_to_consume": 1.0 if boolean(pick(decision, "safe_to_consume"), data_valid) else 0.0,
                "candidate_present": 1.0 if boolean(pick(decision, "candidate_present_shadow", "candidate_true_shadow"), True) else 0.0,
                "source_age_quality": source_age_quality,
                "timeframe_complete": 1.0 if timeframe_complete else 0.0,
            },
            "option_microstructure": {
                "quote_fresh": 1.0 if quote_fresh else 0.0,
                "symbol_stable": 1.0 if symbol and token else 0.0,
                "alignment": 1.0 if alignment else 0.0,
                "source_age_quality": source_age_quality,
                "spread_quality": spread_quality,
            },
            "liquidity_execution": {
                "bid_qty": min(1.0, q["bid_qty"] / 500.0),
                "ask_qty": min(1.0, q["ask_qty"] / 500.0),
                "depth": depth_quality,
                "spread_quality": spread_quality,
                "exit_liquidity": depth_quality,
            },
        },
        "candidate_creation": {
            "trigger_underlying_price": trigger_underlying,
            "trigger_option_mid": trigger_mid,
            "trigger_option_ask": number(trigger_memory.get("trigger_option_ask"), q["ask"]),
            "trigger_spread": trigger_spread,
            "short_term_atr": atr,
            "candidate_created_ts": trigger_memory.get("candidate_created_ts", ""),
        },
        "current_market": {
            "underlying_price": fut_price,
            "option_mid": q["mid"],
            "ask": q["ask"],
            "spread": q["spread"],
            "recent_ask_volatility": number(pick(quote, "recent_ask_volatility", "ask_volatility"), spread_points * 0.5) or 0.0,
            "tick_size": q["tick_size"],
        },
        "edge_after_cost": {
            "expected_gross_move_points": target_points,
            "optimistic_entry_cost_points": spread_points * 0.5,
            "optimistic_exit_cost_points": spread_points * 0.5,
            "optimistic_slippage_points": max(spread_points * 0.25, 0.05),
            "conservative_entry_cost_points": spread_points,
            "conservative_exit_cost_points": spread_points,
            "conservative_slippage_points": max(spread_points * 0.5, 0.10),
            "brokerage_points": number(trigger_memory.get("brokerage_points"), 0.0) or 0.0,
            "taxes_exchange_points": number(trigger_memory.get("taxes_exchange_points"), 0.0) or 0.0,
            "conservative_cost_indication": conservative_cost,
        },
        "source_evidence": {
            "decision_stream_id": decision_id,
            "feature_stream": feature.get("_stream", ""),
            "quote_stream": quote.get("_stream", ""),
            "quote_stream_id": quote_id,
            "broker_report": broker.get("_path", ""),
            "broker_report_age_seconds": broker.get("_age_seconds", ""),
        },
    }


def append(path: Path, obj: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(obj, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("etc/strategy_family/trade_quality_authorization_v28.json"))
    parser.add_argument("--state", type=Path, default=Path("run/state/trade_quality_authorization_v28/state.json"))
    parser.add_argument("--records", type=Path, default=Path("run/shadow/trade_quality_authorization_v28/records.ndjson"))
    parser.add_argument("--packets", type=Path, default=Path("run/shadow/trade_quality_authorization_v28/packets.ndjson"))
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--duration-seconds", type=int, default=0)
    parser.add_argument("--poll-seconds", type=float, default=1.0)
    parser.add_argument("--broker-report-max-age-seconds", type=int, default=120)
    args = parser.parse_args()

    config_raw = load_json(args.config)
    config = config_from_json(config_raw) if config_raw else GateConfig()
    state = ObservationState()
    if args.state.exists():
        raw = load_json(args.state)
        state = ObservationState(**{k: raw.get(k, getattr(state, k)) for k in asdict(state)})

    redis = get_redis_client()
    project = Path.cwd()
    last_id = ""
    start = time.monotonic()

    while True:
        found = latest_enter_candidate(redis)
        if found:
            decision_id, decision = found
            if decision_id != last_id:
                symbol = text(pick(decision, "option_symbol", "symbol", "candidate_symbol_shadow", default=object_mapping(decision.get("metadata")).get("option_symbol", ""))).upper()
                token = text(pick(decision, "option_token", "instrument_token", "instrument_key", "candidate_instrument_token_shadow", default=object_mapping(decision.get("metadata")).get("option_token", "")))
                feature_found = latest_feature(redis)
                futures_found = latest_futures(redis)
                quote_found = latest_matching_quote(redis, symbol, token)
                feature = feature_found[1] if feature_found else {}
                futures = futures_found[1] if futures_found else {}
                quote_id, quote = quote_found if quote_found else ("", {})
                position = mapping(redis.hgetall(POSITION_KEY))
                broker = newest_broker_report(project, args.broker_report_max_age_seconds)
                trigger_memory = {
                    "trigger_underlying_price": pick(futures, "ltp", "price", "last_price", default=pick(feature, "futures_ltp")),
                    "trigger_option_mid": quote_values(quote).get("mid"),
                    "trigger_option_ask": quote_values(quote).get("ask"),
                    "trigger_spread": quote_values(quote).get("spread"),
                    "candidate_created_ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                }
                packet = build_packet(
                    decision_id, decision, feature, futures, quote_id, quote,
                    position, broker, trigger_memory,
                )
                record, state = evaluate(packet, state=state, config=config)
                append(args.packets, packet)
                append(args.records, record)
                args.state.parent.mkdir(parents=True, exist_ok=True)
                args.state.write_text(json.dumps(asdict(state), indent=2, sort_keys=True) + "\n")
                print(json.dumps({
                    "decision_stream_id": decision_id,
                    "verdict": record["verdict"],
                    "reason": record["reason"],
                    "candidate_identity": record["candidate_identity"],
                    "hard_vetoes": record.get("hard_vetoes", []),
                    "broker_order": 0,
                    "redis_write": 0,
                }, sort_keys=True), flush=True)
                last_id = decision_id

        if args.once:
            break
        if args.duration_seconds > 0 and time.monotonic() - start >= args.duration_seconds:
            break
        time.sleep(max(0.2, args.poll_seconds))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
