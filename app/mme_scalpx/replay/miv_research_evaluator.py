from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import deque
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from app.mme_scalpx.services.strategy_family import miv_r_contract as MIV


MIV_EVALUATOR_VERSION = "miv_zerodha_lite_research_evaluator_v0_1_r2"

_CALL_TYPES = {"CALL", "CE", "C", "CALL_PRESSURE_BURST"}
_PUT_TYPES = {"PUT", "PE", "P", "PUT_PRESSURE_BURST"}

_FUTURE_KEYS = (
    "futures_ltp",
    "future_ltp",
    "fut_ltp",
    "underlying_ltp",
    "index_ltp",
    "nifty_ltp",
    "spot_ltp",
)

_OPTION_KEYS = (
    "selected_option_ltp",
    "option_ltp",
    "selected_ltp",
    "ltp",
    "ce_ltp",
    "pe_ltp",
)

_BID_KEYS = (
    "selected_bid",
    "option_bid",
    "bid",
    "best_bid",
)

_ASK_KEYS = (
    "selected_ask",
    "option_ask",
    "ask",
    "best_ask",
)

_SYMBOL_KEYS = (
    "option_symbol",
    "selected_symbol",
    "selected_option_symbol",
    "trading_symbol",
    "symbol",
)

_OPTION_TYPE_KEYS = (
    "selected_option_type",
    "option_type",
    "right",
    "side",
    "branch",
)


def _flatten(payload: Mapping[str, Any], prefix: str = "", out: dict[str, Any] | None = None) -> dict[str, Any]:
    if out is None:
        out = {}
    for key, value in payload.items():
        k = str(key)
        out[k] = value
        if prefix:
            out[f"{prefix}.{k}"] = value
        if isinstance(value, Mapping):
            _flatten(value, f"{prefix}.{k}" if prefix else k, out)
    return out


def _first(payload: Mapping[str, Any], keys: Sequence[str], default: Any = None) -> Any:
    flat = _flatten(payload)
    lower = {str(k).lower(): v for k, v in flat.items()}
    for key in keys:
        if key in flat:
            return flat[key]
        if key.lower() in lower:
            return lower[key.lower()]
    for existing, value in lower.items():
        for key in keys:
            if existing.endswith("." + key.lower()) or existing.endswith("_" + key.lower()):
                return value
    return default


def _num(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, str) and not value.strip():
            return default
        x = float(value)
        if math.isnan(x) or math.isinf(x):
            return default
        return x
    except Exception:
        return default


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _event_ns(row: Mapping[str, Any], fallback: int) -> int:
    for key in ("event_ns", "ts_ns", "timestamp_ns", "exchange_ts_ns"):
        v = _first(row, (key,), None)
        if v is not None:
            try:
                return int(float(v))
            except Exception:
                pass
    return int(fallback)


def _event_ts(row: Mapping[str, Any], fallback: int) -> str:
    for key in ("event_ts", "timestamp", "ts", "exchange_ts", "created_at"):
        v = _first(row, (key,), None)
        if v:
            return str(v)
    return str(fallback)


def _option_type(row: Mapping[str, Any]) -> str:
    value = _text(_first(row, _OPTION_TYPE_KEYS, ""), "").upper()
    if value in _CALL_TYPES:
        return "CALL"
    if value in _PUT_TYPES:
        return "PUT"
    symbol = _text(_first(row, _SYMBOL_KEYS, ""), "").upper()
    if "CE" in symbol or "CALL" in symbol:
        return "CALL"
    if "PE" in symbol or "PUT" in symbol:
        return "PUT"
    return ""


def _symbol(row: Mapping[str, Any]) -> str:
    return _text(_first(row, _SYMBOL_KEYS, ""), "")


def _spread_score(bid: float, ask: float, option_ltp: float) -> tuple[float, bool, str]:
    if bid <= 0 or ask <= 0:
        return 0.2, False, "bid_ask_missing_or_non_positive"
    if ask < bid:
        return 0.0, False, "ask_below_bid"
    mid = (bid + ask) / 2.0
    spread = ask - bid
    max_allowed = max(6.0, 0.12 * max(mid, option_ltp, 1.0))
    if spread <= 0:
        return 0.0, False, "non_positive_spread"
    if spread > max_allowed:
        return 0.0, False, "spread_too_wide"
    ratio = spread / max(mid, option_ltp, 1.0)
    if ratio <= 0.025:
        return 1.0, True, ""
    if ratio <= 0.06:
        return 0.75, True, ""
    return 0.45, True, "spread_wide_but_research_acceptable"


def _depth_score(row: Mapping[str, Any]) -> tuple[float, str]:
    bid_depth = _num(_first(row, ("selected_depth_bid", "depth_bid", "bid_qty", "best_bid_qty"), None), -1.0)
    ask_depth = _num(_first(row, ("selected_depth_ask", "depth_ask", "ask_qty", "best_ask_qty"), None), -1.0)
    if bid_depth < 0 and ask_depth < 0:
        return 0.35, "UNKNOWN"
    if bid_depth <= 0 and ask_depth <= 0:
        return 0.0, "INVALID"
    if bid_depth > 0 and ask_depth > 0:
        return 0.8, "OK"
    return 0.45, "PARTIAL"


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _score_velocity(delta: float, scale: float, max_score: float) -> float:
    if delta <= 0:
        return 0.0
    return round(max_score * _clamp(delta / max(scale, 1e-9)), 6)


def _candidate_id(
    run_id: str,
    dataset_id: str,
    candidate_type: str,
    symbol: str,
    event_ns: int,
    score: float,
) -> str:
    raw = f"{run_id}|{dataset_id}|MIV_R|{candidate_type}|{symbol}|{event_ns}|{score:.3f}"
    return "miv_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _base_output_row(
    *,
    row: Mapping[str, Any],
    run_id: str,
    dataset_id: str,
    candidate_type: str,
    score_total: float,
    components: Mapping[str, float],
    event_ns: int,
    window_start_ns: int,
    window_end_ns: int,
    hard_blocked: bool,
    hard_block_reasons: Sequence[str],
    soft_block_reasons: Sequence[str],
    tradability_ok: bool,
    freshness_ok: bool,
    depth_quality: str,
    futures_ltp: float,
    option_ltp: float,
    bid: float,
    ask: float,
) -> dict[str, Any]:
    label_only = candidate_type == MIV.MIV_NEUTRAL_ACTIVE_LABEL
    trade_shadow_eligible = not label_only and score_total >= MIV.MIV_SCORE_MIN_RESEARCH and not hard_blocked
    side = ""
    if candidate_type == MIV.MIV_CALL_PRESSURE_BURST:
        side = "CALL"
    elif candidate_type == MIV.MIV_PUT_PRESSURE_BURST:
        side = "PUT"

    symbol = _symbol(row)
    if not symbol:
        symbol = "MIV_UNKNOWN_SELECTED_OPTION"

    out = {
        "schema_version": "miv_research_candidate_v0_1",
        "contract_version": MIV.MIV_CONTRACT_VERSION,
        "evaluator_version": MIV_EVALUATOR_VERSION,
        "run_id": run_id,
        "dataset_id": dataset_id,
        "family_id": MIV.MIV_FAMILY_ID,
        "research_mode": MIV.MIV_MODE_ZERODHA_LITE,
        "candidate_type": candidate_type,
        "miv_candidate_id": _candidate_id(run_id, dataset_id, candidate_type, symbol, event_ns, score_total),
        "event_ts": _event_ts(row, event_ns),
        "event_ns": event_ns,
        "window_start_ns": window_start_ns,
        "window_end_ns": window_end_ns,
        "symbol": symbol,
        "option_symbol": symbol,
        "side": side,
        "action": "LABEL_ONLY" if label_only else "ENTRY",
        "qty": int(_num(_first(row, ("qty", "lot_size", "quantity"), 75), 75)),
        "price": float(option_ltp),
        "score": float(round(score_total, 6)),
        "score_total": float(round(score_total, 6)),
        "research_shadow_only": True,
        "label_only": bool(label_only),
        "trade_shadow_eligible": bool(trade_shadow_eligible),
        "route_to_candidate_audit": True,
        "route_to_risk_shadow": bool(trade_shadow_eligible),
        "route_to_execution_shadow": bool(trade_shadow_eligible),
        "route_to_order_intent_ledger": bool(trade_shadow_eligible),
        "order_allowed": False,
        "broker_send_enabled": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
        "dhan_context_status": _text(_first(row, ("dhan_context_status", "option_context_status"), "UNAVAILABLE")),
        "dhan_full_enabled": False,
        "hard_blocked": bool(hard_blocked),
        "hard_block_reasons": list(hard_block_reasons),
        "soft_block_reasons": list(soft_block_reasons),
        "tradability_ok": bool(tradability_ok),
        "freshness_ok": bool(freshness_ok),
        "depth_quality": depth_quality,
        "futures_ltp": float(futures_ltp),
        "selected_option_ltp": float(option_ltp),
        "selected_bid": float(bid),
        "selected_ask": float(ask),
        "selected_spread": float(max(0.0, ask - bid)) if bid > 0 and ask > 0 else 0.0,
        "selected_mid": float((bid + ask) / 2.0) if bid > 0 and ask > 0 else float(option_ltp),
        "cvd_type": "proxy",
        "cvd_proxy_method": "tick_direction_and_ltp_proxy",
        "cvd_proxy_confidence": "LOW",
    }
    out.update({k: float(round(v, 6)) for k, v in components.items()})
    validation = MIV.validate_miv_candidate_row(out)
    out["contract_validation_ok"] = bool(validation["ok"])
    out["contract_validation_errors"] = list(validation["hard_errors"])
    return out


def evaluate_miv_zerodha_lite_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    run_id: str,
    dataset_id: str,
    emit_neutral_labels: bool = True,
) -> dict[str, Any]:
    history: deque[dict[str, Any]] = deque(maxlen=8)
    candidates: list[dict[str, Any]] = []
    factor_rows: list[dict[str, Any]] = []
    blocker_rows: list[dict[str, Any]] = []

    for idx, row in enumerate(rows):
        event_ns = _event_ns(row, idx)
        option_type = _option_type(row)
        futures_ltp = _num(_first(row, _FUTURE_KEYS, 0.0), 0.0)
        option_ltp = _num(_first(row, _OPTION_KEYS, 0.0), 0.0)
        bid = _num(_first(row, _BID_KEYS, 0.0), 0.0)
        ask = _num(_first(row, _ASK_KEYS, 0.0), 0.0)

        prev = history[-1] if history else {}
        prev_futures = _num(prev.get("futures_ltp"), futures_ltp)
        prev_option = _num(prev.get("option_ltp"), option_ltp)
        fut_delta = futures_ltp - prev_futures
        opt_delta = option_ltp - prev_option

        hard_reasons: list[str] = []
        soft_reasons: list[str] = []

        if futures_ltp <= 0:
            hard_reasons.append("missing_or_invalid_futures_ltp")
        if option_ltp <= 0:
            hard_reasons.append("missing_or_invalid_selected_option_ltp")
        if not _symbol(row):
            hard_reasons.append("missing_selected_option_symbol")
        if not option_type:
            soft_reasons.append("option_type_unknown_inferred_neutral_possible")

        spread_score, spread_ok, spread_reason = _spread_score(bid, ask, option_ltp)
        if not spread_ok:
            hard_reasons.append(spread_reason)
        elif spread_reason:
            soft_reasons.append(spread_reason)

        depth_score, depth_quality = _depth_score(row)
        if depth_quality == "INVALID":
            hard_reasons.append("invalid_depth")
        elif depth_quality in {"UNKNOWN", "PARTIAL"}:
            soft_reasons.append(f"depth_quality_{depth_quality.lower()}")

        tradability_ok = not hard_reasons
        freshness_ok = True
        hard_blocked = not tradability_ok

        abs_fut_scale = max(abs(prev_futures) * 0.00015, 1.0)
        abs_opt_scale = max(abs(prev_option) * 0.02, 0.5)

        call_fut = _score_velocity(fut_delta, abs_fut_scale, 1.3)
        put_fut = _score_velocity(-fut_delta, abs_fut_scale, 1.3)
        call_opt = _score_velocity(opt_delta, abs_opt_scale, 1.6)
        put_opt = _score_velocity(opt_delta, abs_opt_scale, 1.6)

        tickrate_score = 0.7 if history else 0.25
        option_tickrate_score = 0.9 if abs(opt_delta) > 0 else 0.35

        response_eff = 0.0
        if abs(fut_delta) > 0 and opt_delta > 0:
            response_eff = min(1.1, 0.35 + min(0.75, abs(opt_delta / max(abs(fut_delta), 1e-9))))

        persistence = 0.0
        if len(history) >= 2:
            recent_opt_up = sum(1 for h in history if _num(h.get("option_delta"), 0.0) > 0)
            persistence = min(0.7, 0.2 + 0.18 * recent_opt_up)

        candidates_to_try: list[tuple[str, float, float, float]] = []

        if option_type == "CALL":
            alignment = 1.3 if fut_delta >= 0 and opt_delta > 0 else 0.45 if opt_delta > 0 else 0.0
            total = call_fut + tickrate_score + call_opt + option_tickrate_score + spread_score + depth_score + response_eff + alignment + persistence
            candidates_to_try.append((MIV.MIV_CALL_PRESSURE_BURST, total, call_fut, alignment))
        elif option_type == "PUT":
            alignment = 1.3 if fut_delta <= 0 and opt_delta > 0 else 0.45 if opt_delta > 0 else 0.0
            total = put_fut + tickrate_score + put_opt + option_tickrate_score + spread_score + depth_score + response_eff + alignment + persistence
            candidates_to_try.append((MIV.MIV_PUT_PRESSURE_BURST, total, put_fut, alignment))
        else:
            activity = tickrate_score + option_tickrate_score + spread_score + depth_score + response_eff + persistence
            if emit_neutral_labels:
                candidates_to_try.append((MIV.MIV_NEUTRAL_ACTIVE_LABEL, activity, max(call_fut, put_fut), 0.0))

        window_start_ns = _num(history[0].get("event_ns"), event_ns) if history else event_ns
        for candidate_type, total, fut_component, alignment in candidates_to_try:
            components = {
                "futures_velocity_score": fut_component,
                "futures_tickrate_score": tickrate_score,
                "selected_option_velocity_score": call_opt if candidate_type == MIV.MIV_CALL_PRESSURE_BURST else put_opt if candidate_type == MIV.MIV_PUT_PRESSURE_BURST else max(call_opt, put_opt),
                "selected_option_tickrate_score": option_tickrate_score,
                "selected_option_spread_score": spread_score,
                "selected_option_depth_score": depth_score,
                "option_response_efficiency_score": response_eff,
                "direction_alignment_score": alignment,
                "micro_momentum_persistence_score": persistence,
                "chain_context_score": 0.0,
                "nfo_volume_oi_score": 0.0,
                "cvd_or_flow_context_score": 0.0,
            }
            factor = {
                "window_id": f"miv_window_{idx}",
                "event_ts": _event_ts(row, event_ns),
                "event_ns": event_ns,
                "candidate_type": candidate_type,
                "score_total": round(total, 6),
                "hard_blocked": hard_blocked,
                "hard_block_reasons": list(hard_reasons),
                "soft_block_reasons": list(soft_reasons),
                "candidate_emitted": False,
            }
            factor.update(components)
            factor_rows.append(factor)

            should_emit = False
            if candidate_type == MIV.MIV_NEUTRAL_ACTIVE_LABEL:
                should_emit = emit_neutral_labels and total >= MIV.MIV_SCORE_MIN_RESEARCH and not hard_blocked
            else:
                should_emit = total >= MIV.MIV_SCORE_MIN_RESEARCH and not hard_blocked

            if should_emit:
                cand = _base_output_row(
                    row=row,
                    run_id=run_id,
                    dataset_id=dataset_id,
                    candidate_type=candidate_type,
                    score_total=total,
                    components=components,
                    event_ns=event_ns,
                    window_start_ns=int(window_start_ns),
                    window_end_ns=int(event_ns),
                    hard_blocked=hard_blocked,
                    hard_block_reasons=hard_reasons,
                    soft_block_reasons=soft_reasons,
                    tradability_ok=tradability_ok,
                    freshness_ok=freshness_ok,
                    depth_quality=depth_quality,
                    futures_ltp=futures_ltp,
                    option_ltp=option_ltp,
                    bid=bid,
                    ask=ask,
                )
                factor["candidate_emitted"] = True
                candidates.append(cand)

            for reason in hard_reasons:
                blocker_rows.append({
                    "event_ts": _event_ts(row, event_ns),
                    "event_ns": event_ns,
                    "blocker_type": "hard",
                    "blocker_name": reason,
                    "candidate_type": candidate_type,
                    "candidate_suppressed": not should_emit,
                    "research_mode": MIV.MIV_MODE_ZERODHA_LITE,
                })
            for reason in soft_reasons:
                blocker_rows.append({
                    "event_ts": _event_ts(row, event_ns),
                    "event_ns": event_ns,
                    "blocker_type": "soft",
                    "blocker_name": reason,
                    "candidate_type": candidate_type,
                    "candidate_suppressed": not should_emit,
                    "research_mode": MIV.MIV_MODE_ZERODHA_LITE,
                })

        history.append({
            "event_ns": event_ns,
            "futures_ltp": futures_ltp,
            "option_ltp": option_ltp,
            "option_delta": opt_delta,
        })

    trade_candidates = [c for c in candidates if c["trade_shadow_eligible"]]
    neutral_labels = [c for c in candidates if c["label_only"]]

    return {
        "schema_version": "miv_research_evaluation_result_v0_1",
        "contract_version": MIV.MIV_CONTRACT_VERSION,
        "evaluator_version": MIV_EVALUATOR_VERSION,
        "family_id": MIV.MIV_FAMILY_ID,
        "research_mode": MIV.MIV_MODE_ZERODHA_LITE,
        "research_shadow_only": True,
        "run_id": run_id,
        "dataset_id": dataset_id,
        "input_row_count": idx + 1 if "idx" in locals() else 0,
        "candidate_count": len(candidates),
        "trade_candidate_count": len(trade_candidates),
        "neutral_label_count": len(neutral_labels),
        "candidates": candidates,
        "factor_rows": factor_rows,
        "blocker_rows": blocker_rows,
    }


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True) if isinstance(v, (list, tuple, dict)) else v for k, v in row.items()})


def write_miv_research_artifacts(result: Mapping[str, Any], out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    candidates = list(result.get("candidates", []))
    factor_rows = list(result.get("factor_rows", []))
    blocker_rows = list(result.get("blocker_rows", []))
    shadow_decisions = [
        {
            "miv_candidate_id": c.get("miv_candidate_id"),
            "decision_type": "RESEARCH_SHADOW_ENTRY" if c.get("trade_shadow_eligible") else "RESEARCH_LABEL_ONLY",
            "family_id": c.get("family_id"),
            "side": c.get("side"),
            "action": c.get("action"),
            "score": c.get("score"),
            "research_shadow_only": True,
            "risk_shadow_eligible": bool(c.get("route_to_risk_shadow")),
            "execution_shadow_eligible": bool(c.get("route_to_execution_shadow")),
            "order_intent_ledger_eligible": bool(c.get("route_to_order_intent_ledger")),
            "broker_send_enabled": False,
            "real_order_sent": False,
        }
        for c in candidates
    ]

    paths = {
        "miv_research_candidates.json": out / "miv_research_candidates.json",
        "miv_candidate_audit.csv": out / "miv_candidate_audit.csv",
        "miv_factor_surface.csv": out / "miv_factor_surface.csv",
        "miv_blocker_surface.csv": out / "miv_blocker_surface.csv",
        "miv_shadow_decisions.json": out / "miv_shadow_decisions.json",
        "miv_shadow_pnl.csv": out / "miv_shadow_pnl.csv",
    }

    paths["miv_research_candidates.json"].write_text(
        json.dumps({
            "schema_version": result.get("schema_version"),
            "contract_version": result.get("contract_version"),
            "evaluator_version": result.get("evaluator_version"),
            "family_id": result.get("family_id"),
            "research_mode": result.get("research_mode"),
            "research_shadow_only": True,
            "run_id": result.get("run_id"),
            "dataset_id": result.get("dataset_id"),
            "candidate_count": result.get("candidate_count", 0),
            "trade_candidate_count": result.get("trade_candidate_count", 0),
            "neutral_label_count": result.get("neutral_label_count", 0),
            "candidates": candidates,
        }, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _write_csv(paths["miv_candidate_audit.csv"], candidates)
    _write_csv(paths["miv_factor_surface.csv"], factor_rows)
    _write_csv(paths["miv_blocker_surface.csv"], blocker_rows)
    paths["miv_shadow_decisions.json"].write_text(
        json.dumps({
            "schema_version": "miv_shadow_decisions_v0_1",
            "contract_version": result.get("contract_version"),
            "family_id": result.get("family_id"),
            "research_shadow_only": True,
            "decision_count": len(shadow_decisions),
            "decisions": shadow_decisions,
        }, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    paths["miv_shadow_pnl.csv"].write_text(
        "miv_candidate_id,event_ts,side,entry_ref_price,shadow_fill_price,shadow_exit_price,shadow_exit_reason,gross_points,cost_points,net_points,filled,pnl_surface_version,remarks\n",
        encoding="utf-8",
    )

    return {name: str(path) for name, path in paths.items()}


__all__ = (
    "MIV_EVALUATOR_VERSION",
    "evaluate_miv_zerodha_lite_rows",
    "write_miv_research_artifacts",
)
