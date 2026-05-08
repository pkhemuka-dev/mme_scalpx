from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Mapping

from app.mme_scalpx.replay.execution_shadow import (
    replay_shadow_assumption_profile,
    simulate_replay_execution_shadow,
)
from app.mme_scalpx.replay.feature_adapter import build_replay_feature_payload
from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.risk_adapter import build_replay_risk_decision
from app.mme_scalpx.replay.scenarios import (
    REPLAY_REQUIRED_SCENARIOS,
    apply_replay_scenario_to_row,
    build_scenario_execution_assumption,
    scenario_risk_effects,
)
from app.mme_scalpx.replay.strategy_adapter import build_replay_strategy_decision_payload


REPLAY_BATCH_RUNNER_CONTRACT_VERSION = "replay_batch_runner_v1"

REPLAY_BATCH_SUPPORTED_RUN_SCOPES = (
    "single_day",
    "date_range",
    "date_list",
    "intraday_window",
    "scenario_matrix",
)

REPLAY_BATCH_REQUIRED_REQUEST_FIELDS = (
    "schema_version",
    "run_id",
    "scope",
    "date",
    "dates",
    "start_time",
    "end_time",
    "scenario_id",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)


@dataclass(frozen=True)
class ReplayRunRequest:
    schema_version: str
    run_id: str
    scope: str
    date: str | None
    dates: tuple[str, ...]
    start_time: str | None
    end_time: str | None
    scenario_id: str | None
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    broker_calls_allowed: bool = False
    live_redis_writes_allowed: bool = False
    production_doctrine_changed: bool = False


def _iso_date(value: str) -> str:
    return date.fromisoformat(str(value)).isoformat()


def _date_range(start_date: str, end_date: str) -> tuple[str, ...]:
    start = date.fromisoformat(str(start_date))
    end = date.fromisoformat(str(end_date))
    if end < start:
        raise ValueError("end_date must be >= start_date")
    out = []
    cur = start
    while cur <= end:
        out.append(cur.isoformat())
        cur += timedelta(days=1)
    return tuple(out)


def deterministic_replay_batch_id(payload: Mapping[str, Any], *, prefix: str = "replay_batch") -> str:
    return f"{prefix}_{replay_fingerprint(payload)[:24]}"


def build_replay_run_request(
    *,
    scope: str,
    run_id: str,
    date_value: str | None = None,
    dates: tuple[str, ...] | list[str] | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    if scope not in REPLAY_BATCH_SUPPORTED_RUN_SCOPES:
        raise ValueError(f"unsupported replay batch scope: {scope}")
    normalized_dates = tuple(_iso_date(d) for d in (dates or ()))
    normalized_date = _iso_date(date_value) if date_value else (normalized_dates[0] if normalized_dates else None)
    req = ReplayRunRequest(
        schema_version=REPLAY_BATCH_RUNNER_CONTRACT_VERSION,
        run_id=str(run_id),
        scope=str(scope),
        date=normalized_date,
        dates=normalized_dates,
        start_time=str(start_time) if start_time else None,
        end_time=str(end_time) if end_time else None,
        scenario_id=str(scenario_id) if scenario_id else None,
    )
    return {
        "schema_version": req.schema_version,
        "run_id": req.run_id,
        "scope": req.scope,
        "date": req.date,
        "dates": req.dates,
        "start_time": req.start_time,
        "end_time": req.end_time,
        "scenario_id": req.scenario_id,
        "paper_armed_approved": req.paper_armed_approved,
        "live_trading_approved": req.live_trading_approved,
        "execution_arming_created": req.execution_arming_created,
        "broker_calls_allowed": req.broker_calls_allowed,
        "live_redis_writes_allowed": req.live_redis_writes_allowed,
        "production_doctrine_changed": req.production_doctrine_changed,
    }


def build_single_day_plan(*, day: str, scenario_id: str | None = None) -> dict[str, Any]:
    seed = {"scope": "single_day", "day": _iso_date(day), "scenario_id": scenario_id}
    plan_id = deterministic_replay_batch_id(seed)
    request = build_replay_run_request(
        scope="single_day",
        run_id=f"{plan_id}_0",
        date_value=day,
        dates=(day,),
        scenario_id=scenario_id,
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="single_day", requests=(request,))


def build_date_range_plan(*, start_date: str, end_date: str, scenario_id: str | None = None) -> dict[str, Any]:
    dates = _date_range(start_date, end_date)
    seed = {"scope": "date_range", "dates": dates, "scenario_id": scenario_id}
    plan_id = deterministic_replay_batch_id(seed)
    requests = tuple(
        build_replay_run_request(
            scope="date_range",
            run_id=f"{plan_id}_{idx}",
            date_value=day,
            dates=dates,
            scenario_id=scenario_id,
        )
        for idx, day in enumerate(dates)
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="date_range", requests=requests)


def build_date_list_plan(*, dates: tuple[str, ...] | list[str], scenario_id: str | None = None) -> dict[str, Any]:
    normalized = tuple(_iso_date(day) for day in dates)
    seed = {"scope": "date_list", "dates": normalized, "scenario_id": scenario_id}
    plan_id = deterministic_replay_batch_id(seed)
    requests = tuple(
        build_replay_run_request(
            scope="date_list",
            run_id=f"{plan_id}_{idx}",
            date_value=day,
            dates=normalized,
            scenario_id=scenario_id,
        )
        for idx, day in enumerate(normalized)
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="date_list", requests=requests)


def build_intraday_window_plan(
    *,
    day: str,
    start_time: str,
    end_time: str,
    scenario_id: str | None = None,
) -> dict[str, Any]:
    seed = {
        "scope": "intraday_window",
        "day": _iso_date(day),
        "start_time": start_time,
        "end_time": end_time,
        "scenario_id": scenario_id,
    }
    plan_id = deterministic_replay_batch_id(seed)
    request = build_replay_run_request(
        scope="intraday_window",
        run_id=f"{plan_id}_0",
        date_value=day,
        dates=(day,),
        start_time=start_time,
        end_time=end_time,
        scenario_id=scenario_id,
    )
    return build_replay_batch_plan(plan_id=plan_id, scope="intraday_window", requests=(request,))


def build_scenario_matrix_plan(
    *,
    dates: tuple[str, ...] | list[str],
    scenarios: tuple[str, ...] | list[str] = REPLAY_REQUIRED_SCENARIOS,
    start_time: str | None = None,
    end_time: str | None = None,
) -> dict[str, Any]:
    normalized_dates = tuple(_iso_date(day) for day in dates)
    normalized_scenarios = tuple(str(s) for s in scenarios)
    seed = {
        "scope": "scenario_matrix",
        "dates": normalized_dates,
        "scenarios": normalized_scenarios,
        "start_time": start_time,
        "end_time": end_time,
    }
    plan_id = deterministic_replay_batch_id(seed)
    requests = []
    idx = 0
    for day in normalized_dates:
        for scenario_id in normalized_scenarios:
            requests.append(
                build_replay_run_request(
                    scope="scenario_matrix",
                    run_id=f"{plan_id}_{idx}",
                    date_value=day,
                    dates=normalized_dates,
                    start_time=start_time,
                    end_time=end_time,
                    scenario_id=scenario_id,
                )
            )
            idx += 1
    return build_replay_batch_plan(plan_id=plan_id, scope="scenario_matrix", requests=tuple(requests))


def build_replay_batch_plan(
    *,
    plan_id: str,
    scope: str,
    requests: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> dict[str, Any]:
    reqs = tuple(dict(r) for r in requests)
    return {
        "schema_version": REPLAY_BATCH_RUNNER_CONTRACT_VERSION,
        "plan_id": str(plan_id),
        "scope": str(scope),
        "request_count": len(reqs),
        "requests": reqs,
        "created_at_utc": datetime.utcnow().isoformat() + "Z",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


def validate_replay_run_request(request: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(field for field in REPLAY_BATCH_REQUIRED_REQUEST_FIELDS if field not in request)
    scope_ok = request.get("scope") in REPLAY_BATCH_SUPPORTED_RUN_SCOPES
    no_live_ok = (
        request.get("paper_armed_approved") is False
        and request.get("live_trading_approved") is False
        and request.get("execution_arming_created") is False
        and request.get("broker_calls_allowed") is False
        and request.get("live_redis_writes_allowed") is False
        and request.get("production_doctrine_changed") is False
    )
    ok = bool(not missing and scope_ok and no_live_ok)
    return {
        "ok": ok,
        "missing": missing,
        "scope_ok": scope_ok,
        "no_live_ok": no_live_ok,
    }


def validate_replay_batch_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    requests = tuple(plan.get("requests") or ())
    request_validations = tuple(validate_replay_run_request(r) for r in requests)
    scope_ok = plan.get("scope") in REPLAY_BATCH_SUPPORTED_RUN_SCOPES
    count_ok = int(plan.get("request_count", -1)) == len(requests)
    requests_ok = all(v["ok"] for v in request_validations)
    no_live_ok = (
        plan.get("paper_armed_approved") is False
        and plan.get("live_trading_approved") is False
        and plan.get("execution_arming_created") is False
        and plan.get("broker_calls_allowed") is False
        and plan.get("live_redis_writes_allowed") is False
        and plan.get("production_doctrine_changed") is False
    )
    ok = bool(scope_ok and count_ok and requests_ok and no_live_ok)
    return {
        "ok": ok,
        "scope_ok": scope_ok,
        "count_ok": count_ok,
        "requests_ok": requests_ok,
        "no_live_ok": no_live_ok,
        "request_validations": request_validations,
    }


def replay_batch_base_row(*, day: str, event_ts_ns: int = 1_000_000_000) -> dict[str, Any]:
    return {
        "event_ts_ns": int(event_ts_ns),
        "sequence_id": 1,
        "replay_day": _iso_date(day),
        "data_valid": True,
        "fut_ltp": 22500.0,
        "fut_best_bid": 22499.5,
        "fut_best_ask": 22500.5,
        "fut_local_ts": event_ts_ns,
        "opt_ltp": 100.0,
        "opt_best_bid": 99.5,
        "opt_best_ask": 100.5,
        "opt_bid_qty_1": 100,
        "opt_ask_qty_1": 100,
        "opt_local_ts": event_ts_ns,
        "provider_ready_miso": True,
        "chain_context_fresh": True,
        "dhan_context_ready": True,
        "oi_context_fresh": True,
        "selected_security_id": "REPLAY-SEC",
        "selected_tradingsymbol": "NIFTY-REPLAY",
        "selected_expiry": "2026-05-07",
        "selected_strike": 22500,
        "selected_option_type": "CE",
        "nearest_call_wall": 22600,
        "nearest_put_wall": 22400,
        "oi_wall_strength": 1.25,
        "trend_confirmed": True,
        "pullback_detected": True,
        "resume_confirmed": True,
        "micro_trap_flag": True,
        "futures_impulse_ok": True,
        "shelf_confirmed": True,
        "breakout_triggered": True,
        "breakout_accepted": True,
        "shelf_high": 22520,
        "shelf_low": 22490,
        "compression_detected": True,
        "directional_breakout_triggered": True,
        "expansion_accepted": True,
        "retest_monitor_active": True,
        "hesitation_retest": True,
        "active_zone_valid": True,
        "active_zone": "ORB_LOW",
        "fake_break": True,
        "range_reentry": True,
        "flow_flip": True,
        "trap_event_id": "CALL|ORB_LOW|1000|2000",
        "burst_detected": True,
        "burst_event_id": "CALL|REPLAY-SEC|1000",
        "aggression_ok": True,
        "tape_speed_ok": True,
        "imbalance_persistence_ok": True,
        "queue_reload_veto": True,
    }


def simulate_replay_request(request: Mapping[str, Any]) -> dict[str, Any]:
    day = request.get("date") or (tuple(request.get("dates") or ("2026-05-01",))[0])
    row = replay_batch_base_row(day=str(day))
    scenario_id = request.get("scenario_id")
    if scenario_id:
        row = apply_replay_scenario_to_row(row, str(scenario_id))

    feature_result = build_replay_feature_payload(run_id=str(request["run_id"]), row=row)
    strategy_result = build_replay_strategy_decision_payload(
        run_id=str(request["run_id"]),
        feature_payload=feature_result.payload,
    )

    risk_effects = scenario_risk_effects(str(scenario_id)) if scenario_id else {}
    risk_decision = build_replay_risk_decision(
        run_id=str(request["run_id"]),
        strategy_decision=strategy_result.decision_payload,
        force_veto_reasons=risk_effects.get("force_veto_reasons"),
    )

    if scenario_id:
        assumption = build_scenario_execution_assumption(str(scenario_id))
    else:
        assumption = replay_shadow_assumption_profile(fill_policy="FULL_FILL")

    execution_shadow = simulate_replay_execution_shadow(
        run_id=str(request["run_id"]),
        strategy_decision=strategy_result.decision_payload,
        risk_decision=risk_decision,
        assumption_profile=assumption,
    )

    return {
        "schema_version": "replay_batch_request_result_v1",
        "run_id": request["run_id"],
        "scope": request["scope"],
        "date": request.get("date"),
        "start_time": request.get("start_time"),
        "end_time": request.get("end_time"),
        "scenario_id": scenario_id,
        "feature_summary": {
            "family_features_json_present": isinstance(feature_result.payload.get("family_features_json"), str),
            "family_surfaces_json_present": isinstance(feature_result.payload.get("family_surfaces_json"), str),
            "provider_ready_miso": feature_result.payload.get("provider_ready_miso"),
        },
        "strategy_summary": {
            "candidate_count": strategy_result.decision_payload.get("candidate_count"),
            "final_action": strategy_result.decision_payload.get("final_action"),
            "order_allowed": strategy_result.decision_payload.get("order_allowed"),
        },
        "risk_summary": {
            "risk_evaluated": risk_decision.get("risk_evaluated"),
            "entry_vetoed": risk_decision.get("entry_vetoed"),
            "research_trade_allowed": risk_decision.get("research_trade_allowed"),
            "veto_reasons": risk_decision.get("veto_reasons"),
        },
        "execution_shadow_summary": {
            "fill_policy": execution_shadow.get("fill_policy"),
            "fill_status": execution_shadow.get("fill_status"),
            "filled_qty": execution_shadow.get("filled_qty"),
            "net_pnl": execution_shadow.get("shadow_pnl_summary", {}).get("net_pnl"),
            "real_order_sent": execution_shadow.get("real_order_sent"),
            "broker_calls_executed": execution_shadow.get("broker_calls_executed"),
        },
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def simulate_replay_batch_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    validation = validate_replay_batch_plan(plan)
    if not validation["ok"]:
        raise ValueError(f"invalid replay batch plan: {validation}")
    results = tuple(simulate_replay_request(r) for r in tuple(plan.get("requests") or ()))
    scenario_ids = tuple(sorted({str(r.get("scenario_id")) for r in results if r.get("scenario_id")}))
    total_pnl = sum(float(r.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for r in results)
    return {
        "schema_version": "replay_batch_simulation_result_v1",
        "plan_id": plan.get("plan_id"),
        "scope": plan.get("scope"),
        "request_count": plan.get("request_count"),
        "result_count": len(results),
        "scenario_ids": scenario_ids,
        "scenario_count": len(scenario_ids),
        "total_shadow_pnl": total_pnl,
        "results": results,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def replay_batch_profile_manifest() -> dict[str, Any]:
    return {
        "schema_version": "replay_batch_profile_manifest_v1",
        "supported_run_scopes": REPLAY_BATCH_SUPPORTED_RUN_SCOPES,
        "required_request_fields": REPLAY_BATCH_REQUIRED_REQUEST_FIELDS,
        "example_scopes": {
            "single_day": {"day": "2026-05-01"},
            "date_range": {"start_date": "2026-05-01", "end_date": "2026-05-03"},
            "date_list": {"dates": ("2026-05-01", "2026-05-03")},
            "intraday_window": {"day": "2026-05-01", "start_time": "09:30:00", "end_time": "10:30:00"},
            "scenario_matrix": {"dates": ("2026-05-01",), "scenarios": REPLAY_REQUIRED_SCENARIOS},
        },
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


def replay_batch_profile_manifest_json() -> str:
    return json.dumps(replay_batch_profile_manifest(), indent=2, sort_keys=True, default=str)


def replay_batch_runner_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_BATCH_RUNNER_CONTRACT_VERSION,
        "supported_run_scopes": REPLAY_BATCH_SUPPORTED_RUN_SCOPES,
        "required_request_fields": REPLAY_BATCH_REQUIRED_REQUEST_FIELDS,
        "batch_runner_shape": "PROVEN_BY_27K",
        "artifact_materialization": "PROVEN_BY_27K",
        "full_live_replay_parity": "NOT_PROVEN_IN_27K",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_BATCH_RUNNER_CONTRACT_VERSION",
    "REPLAY_BATCH_SUPPORTED_RUN_SCOPES",
    "REPLAY_BATCH_REQUIRED_REQUEST_FIELDS",
    "ReplayRunRequest",
    "deterministic_replay_batch_id",
    "build_replay_run_request",
    "build_single_day_plan",
    "build_date_range_plan",
    "build_date_list_plan",
    "build_intraday_window_plan",
    "build_scenario_matrix_plan",
    "build_replay_batch_plan",
    "validate_replay_run_request",
    "validate_replay_batch_plan",
    "replay_batch_base_row",
    "simulate_replay_request",
    "simulate_replay_batch_plan",
    "replay_batch_profile_manifest",
    "replay_batch_profile_manifest_json",
    "replay_batch_runner_contract_summary",
)))
