from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.safety import assert_replay_artifact_path
from app.mme_scalpx.replay.strategy_adapter import REPLAY_STRATEGY_FAMILIES, REPLAY_STRATEGY_SIDES


REPLAY_REPORT_EXPORT_CONTRACT_VERSION = "replay_report_exporter_v1"

REPLAY_REQUIRED_REPORT_EXPORTS = (
    "00_export_manifest.json",
    "01_trade_log.csv",
    "01_trade_log.json",
    "02_candidate_log.csv",
    "02_candidate_log.json",
    "03_blocker_chain.csv",
    "03_blocker_chain.json",
    "04_side_split_summary.csv",
    "04_side_split_summary.json",
    "05_family_split_summary.csv",
    "05_family_split_summary.json",
    "06_scenario_summary.csv",
    "06_scenario_summary.json",
    "07_pnl_execution_shadow_summary.csv",
    "07_pnl_execution_shadow_summary.json",
    "08_baseline_vs_shadow_comparison.json",
    "09_export_reproducibility.json",
)


def _json_ready(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, default=str))


def _write_json(path: Path, payload: Any) -> str:
    assert_replay_artifact_path(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True), encoding="utf-8")
    return str(path)


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]], *, fieldnames: tuple[str, ...]) -> str:
    assert_replay_artifact_path(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = tuple(dict(row) for row in rows)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})
    return str(path)


def _results(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(dict(row) for row in (simulation_result.get("results") or ()))


def build_replay_trade_log(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    rows = []
    for index, result in enumerate(_results(simulation_result)):
        exec_summary = dict(result.get("execution_shadow_summary") or {})
        risk_summary = dict(result.get("risk_summary") or {})
        strategy_summary = dict(result.get("strategy_summary") or {})
        rows.append({
            "row_id": index,
            "run_id": result.get("run_id"),
            "date": result.get("date"),
            "scope": result.get("scope"),
            "scenario_id": result.get("scenario_id"),
            "final_action": strategy_summary.get("final_action"),
            "entry_vetoed": risk_summary.get("entry_vetoed"),
            "research_trade_allowed": risk_summary.get("research_trade_allowed"),
            "fill_policy": exec_summary.get("fill_policy"),
            "fill_status": exec_summary.get("fill_status"),
            "filled_qty": exec_summary.get("filled_qty"),
            "net_pnl": exec_summary.get("net_pnl"),
            "real_order_sent": exec_summary.get("real_order_sent"),
            "broker_calls_executed": exec_summary.get("broker_calls_executed"),
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        })
    return tuple(rows)


def build_replay_candidate_log(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    rows = []
    for result in _results(simulation_result):
        strategy_summary = dict(result.get("strategy_summary") or {})
        for family in REPLAY_STRATEGY_FAMILIES:
            for side in REPLAY_STRATEGY_SIDES:
                rows.append({
                    "run_id": result.get("run_id"),
                    "date": result.get("date"),
                    "scope": result.get("scope"),
                    "scenario_id": result.get("scenario_id"),
                    "family": family,
                    "side": side,
                    "candidate_id": f"{result.get('run_id')}|{family}|{side}",
                    "candidate_present": True,
                    "candidate_count": strategy_summary.get("candidate_count"),
                    "final_action": strategy_summary.get("final_action"),
                    "order_allowed": False,
                    "paper_armed_approved": False,
                    "live_trading_approved": False,
                    "production_doctrine_changed": False,
                })
    return tuple(rows)


def build_replay_blocker_chain(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    rows = []
    for result in _results(simulation_result):
        risk_summary = dict(result.get("risk_summary") or {})
        veto_reasons = tuple(risk_summary.get("veto_reasons") or ())
        if not veto_reasons:
            veto_reasons = ("NO_VETO",)
        for index, reason in enumerate(veto_reasons):
            rows.append({
                "run_id": result.get("run_id"),
                "date": result.get("date"),
                "scope": result.get("scope"),
                "scenario_id": result.get("scenario_id"),
                "blocker_index": index,
                "blocker": reason,
                "entry_vetoed": risk_summary.get("entry_vetoed"),
                "paper_armed_approved": False,
                "live_trading_approved": False,
                "production_doctrine_changed": False,
            })
    return tuple(rows)


def build_side_split_summary(candidate_log: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    rows = tuple(dict(row) for row in candidate_log)
    out = []
    for side in REPLAY_STRATEGY_SIDES:
        side_rows = [row for row in rows if row.get("side") == side]
        out.append({
            "side": side,
            "candidate_count": len(side_rows),
            "order_allowed_true_count": sum(1 for row in side_rows if row.get("order_allowed") is True),
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        })
    return tuple(out)


def build_family_split_summary(candidate_log: Iterable[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    rows = tuple(dict(row) for row in candidate_log)
    out = []
    for family in REPLAY_STRATEGY_FAMILIES:
        family_rows = [row for row in rows if row.get("family") == family]
        out.append({
            "family": family,
            "candidate_count": len(family_rows),
            "order_allowed_true_count": sum(1 for row in family_rows if row.get("order_allowed") is True),
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        })
    return tuple(out)


def build_scenario_summary(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    results = _results(simulation_result)
    scenario_ids = tuple(sorted({str(row.get("scenario_id")) for row in results if row.get("scenario_id")}))
    out = []
    for scenario_id in scenario_ids:
        subset = [row for row in results if row.get("scenario_id") == scenario_id]
        out.append({
            "scenario_id": scenario_id,
            "result_count": len(subset),
            "entry_vetoed_count": sum(1 for row in subset if row.get("risk_summary", {}).get("entry_vetoed") is True),
            "filled_qty_total": sum(int(row.get("execution_shadow_summary", {}).get("filled_qty") or 0) for row in subset),
            "net_pnl_total": sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in subset),
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        })
    return tuple(out)


def build_pnl_execution_shadow_summary(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    results = _results(simulation_result)
    return ({
        "result_count": len(results),
        "filled_qty_total": sum(int(row.get("execution_shadow_summary", {}).get("filled_qty") or 0) for row in results),
        "net_pnl_total": sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in results),
        "real_order_sent_count": sum(1 for row in results if row.get("execution_shadow_summary", {}).get("real_order_sent") is True),
        "broker_calls_executed_count": sum(1 for row in results if row.get("execution_shadow_summary", {}).get("broker_calls_executed") is True),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    },)


def build_baseline_shadow_comparison(
    *,
    baseline_label: str,
    baseline_result: Mapping[str, Any],
    shadow_label: str,
    shadow_result: Mapping[str, Any],
) -> dict[str, Any]:
    base_pnl = sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in _results(baseline_result))
    shadow_pnl = sum(float(row.get("execution_shadow_summary", {}).get("net_pnl") or 0.0) for row in _results(shadow_result))
    base_trades = len(_results(baseline_result))
    shadow_trades = len(_results(shadow_result))
    comparison = {
        "schema_version": "replay_baseline_shadow_comparison_v1",
        "baseline_label": str(baseline_label),
        "shadow_label": str(shadow_label),
        "baseline_result_count": base_trades,
        "shadow_result_count": shadow_trades,
        "baseline_total_shadow_pnl": base_pnl,
        "shadow_total_shadow_pnl": shadow_pnl,
        "delta_result_count": shadow_trades - base_trades,
        "delta_shadow_pnl": shadow_pnl - base_pnl,
        "comparison_reproducibility_hash": replay_fingerprint({
            "baseline_label": baseline_label,
            "baseline_result": baseline_result,
            "shadow_label": shadow_label,
            "shadow_result": shadow_result,
        }),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "comparison_shape": "PROVEN_BY_27L",
        "full_report_semantic_accuracy": "NOT_PROVEN_IN_27L",
    }
    return comparison


def build_replay_export_reproducibility(
    *,
    run_id: str,
    simulation_result: Mapping[str, Any],
    exports_payload: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "replay_export_reproducibility_v1",
        "run_id": str(run_id),
        "export_reproducibility_hash": replay_fingerprint({
            "run_id": run_id,
            "simulation_result": simulation_result,
            "exports_payload": exports_payload,
        }),
        "simulation_fingerprint": replay_fingerprint(simulation_result),
        "exports_payload_fingerprint": replay_fingerprint(exports_payload),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def materialize_replay_report_exports(
    *,
    run_id: str,
    simulation_result: Mapping[str, Any],
    export_root: str,
    baseline_comparison: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(export_root)
    assert_replay_artifact_path(str(root / "00_export_manifest.json"))
    root.mkdir(parents=True, exist_ok=True)

    trade_log = build_replay_trade_log(simulation_result)
    candidate_log = build_replay_candidate_log(simulation_result)
    blocker_chain = build_replay_blocker_chain(simulation_result)
    side_summary = build_side_split_summary(candidate_log)
    family_summary = build_family_split_summary(candidate_log)
    scenario_summary = build_scenario_summary(simulation_result)
    pnl_summary = build_pnl_execution_shadow_summary(simulation_result)

    comparison = dict(baseline_comparison or {
        "schema_version": "replay_baseline_shadow_comparison_v1",
        "baseline_label": "self",
        "shadow_label": "self",
        "baseline_result_count": len(_results(simulation_result)),
        "shadow_result_count": len(_results(simulation_result)),
        "delta_result_count": 0,
        "delta_shadow_pnl": 0.0,
        "comparison_reproducibility_hash": replay_fingerprint(simulation_result),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "comparison_shape": "PROVEN_BY_27L",
    })

    payloads_for_hash = {
        "trade_log": trade_log,
        "candidate_log": candidate_log,
        "blocker_chain": blocker_chain,
        "side_summary": side_summary,
        "family_summary": family_summary,
        "scenario_summary": scenario_summary,
        "pnl_summary": pnl_summary,
        "comparison": comparison,
    }
    reproducibility = build_replay_export_reproducibility(
        run_id=run_id,
        simulation_result=simulation_result,
        exports_payload=payloads_for_hash,
    )

    manifest = {
        "schema_version": REPLAY_REPORT_EXPORT_CONTRACT_VERSION,
        "run_id": str(run_id),
        "export_root": str(root),
        "required_exports": REPLAY_REQUIRED_REPORT_EXPORTS,
        "materialized_at_utc": datetime.now(timezone.utc).isoformat(),
        "export_reproducibility_hash": reproducibility["export_reproducibility_hash"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "report_export_shape": "PROVEN_BY_27L",
        "full_report_semantic_accuracy": "NOT_PROVEN_IN_27L",
    }

    written = {
        "00_export_manifest.json": _write_json(root / "00_export_manifest.json", manifest),
        "01_trade_log.csv": _write_csv(root / "01_trade_log.csv", trade_log, fieldnames=(
            "row_id", "run_id", "date", "scope", "scenario_id", "final_action", "entry_vetoed",
            "research_trade_allowed", "fill_policy", "fill_status", "filled_qty", "net_pnl",
            "real_order_sent", "broker_calls_executed", "paper_armed_approved",
            "live_trading_approved", "production_doctrine_changed"
        )),
        "01_trade_log.json": _write_json(root / "01_trade_log.json", trade_log),
        "02_candidate_log.csv": _write_csv(root / "02_candidate_log.csv", candidate_log, fieldnames=(
            "run_id", "date", "scope", "scenario_id", "family", "side", "candidate_id",
            "candidate_present", "candidate_count", "final_action", "order_allowed",
            "paper_armed_approved", "live_trading_approved", "production_doctrine_changed"
        )),
        "02_candidate_log.json": _write_json(root / "02_candidate_log.json", candidate_log),
        "03_blocker_chain.csv": _write_csv(root / "03_blocker_chain.csv", blocker_chain, fieldnames=(
            "run_id", "date", "scope", "scenario_id", "blocker_index", "blocker", "entry_vetoed",
            "paper_armed_approved", "live_trading_approved", "production_doctrine_changed"
        )),
        "03_blocker_chain.json": _write_json(root / "03_blocker_chain.json", blocker_chain),
        "04_side_split_summary.csv": _write_csv(root / "04_side_split_summary.csv", side_summary, fieldnames=(
            "side", "candidate_count", "order_allowed_true_count", "paper_armed_approved",
            "live_trading_approved", "production_doctrine_changed"
        )),
        "04_side_split_summary.json": _write_json(root / "04_side_split_summary.json", side_summary),
        "05_family_split_summary.csv": _write_csv(root / "05_family_split_summary.csv", family_summary, fieldnames=(
            "family", "candidate_count", "order_allowed_true_count", "paper_armed_approved",
            "live_trading_approved", "production_doctrine_changed"
        )),
        "05_family_split_summary.json": _write_json(root / "05_family_split_summary.json", family_summary),
        "06_scenario_summary.csv": _write_csv(root / "06_scenario_summary.csv", scenario_summary, fieldnames=(
            "scenario_id", "result_count", "entry_vetoed_count", "filled_qty_total",
            "net_pnl_total", "paper_armed_approved", "live_trading_approved",
            "production_doctrine_changed"
        )),
        "06_scenario_summary.json": _write_json(root / "06_scenario_summary.json", scenario_summary),
        "07_pnl_execution_shadow_summary.csv": _write_csv(root / "07_pnl_execution_shadow_summary.csv", pnl_summary, fieldnames=(
            "result_count", "filled_qty_total", "net_pnl_total", "real_order_sent_count",
            "broker_calls_executed_count", "paper_armed_approved", "live_trading_approved",
            "production_doctrine_changed"
        )),
        "07_pnl_execution_shadow_summary.json": _write_json(root / "07_pnl_execution_shadow_summary.json", pnl_summary),
        "08_baseline_vs_shadow_comparison.json": _write_json(root / "08_baseline_vs_shadow_comparison.json", comparison),
        "09_export_reproducibility.json": _write_json(root / "09_export_reproducibility.json", reproducibility),
    }

    return {
        "schema_version": "replay_report_export_result_v1",
        "run_id": str(run_id),
        "export_root": str(root),
        "required_exports": REPLAY_REQUIRED_REPORT_EXPORTS,
        "written_exports": written,
        "written_count": len(written),
        "trade_log_count": len(trade_log),
        "candidate_log_count": len(candidate_log),
        "blocker_chain_count": len(blocker_chain),
        "side_summary_count": len(side_summary),
        "family_summary_count": len(family_summary),
        "scenario_summary_count": len(scenario_summary),
        "export_reproducibility_hash": reproducibility["export_reproducibility_hash"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def validate_replay_report_exports(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("export_root")))
    written = dict(result.get("written_exports") or {})
    missing = tuple(name for name in REPLAY_REQUIRED_REPORT_EXPORTS if name not in written or not Path(written[name]).exists())
    root_ok = str(root).startswith("run/replay") or "/run/replay/" in str(root)
    count_ok = int(result.get("written_count", -1)) == len(REPLAY_REQUIRED_REPORT_EXPORTS)
    counts_ok = (
        int(result.get("trade_log_count", 0)) > 0
        and int(result.get("candidate_log_count", 0)) > 0
        and int(result.get("blocker_chain_count", 0)) > 0
        and int(result.get("side_summary_count", 0)) == len(REPLAY_STRATEGY_SIDES)
        and int(result.get("family_summary_count", 0)) == len(REPLAY_STRATEGY_FAMILIES)
    )
    reproducibility_ok = bool(result.get("export_reproducibility_hash"))
    no_live_ok = (
        result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("execution_arming_created") is False
        and result.get("real_order_sent") is False
        and result.get("broker_calls_executed") is False
        and result.get("live_redis_writes_executed") is False
        and result.get("production_doctrine_changed") is False
    )
    ok = bool(not missing and root_ok and count_ok and counts_ok and reproducibility_ok and no_live_ok)
    return {
        "ok": ok,
        "missing": missing,
        "root_ok": root_ok,
        "count_ok": count_ok,
        "counts_ok": counts_ok,
        "reproducibility_ok": reproducibility_ok,
        "no_live_ok": no_live_ok,
    }


def replay_report_export_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_REPORT_EXPORT_CONTRACT_VERSION,
        "required_exports": REPLAY_REQUIRED_REPORT_EXPORTS,
        "export_root": "run/replay/<run_id>/exports/",
        "report_export_shape": "PROVEN_BY_27L",
        "baseline_shadow_comparison_shape": "PROVEN_BY_27L",
        "export_reproducibility_hash": "PROVEN_BY_27L",
        "full_report_semantic_accuracy": "NOT_PROVEN_IN_27L",
        "full_live_replay_parity": "NOT_PROVEN_IN_27L",
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
    "REPLAY_REPORT_EXPORT_CONTRACT_VERSION",
    "REPLAY_REQUIRED_REPORT_EXPORTS",
    "build_replay_trade_log",
    "build_replay_candidate_log",
    "build_replay_blocker_chain",
    "build_side_split_summary",
    "build_family_split_summary",
    "build_scenario_summary",
    "build_pnl_execution_shadow_summary",
    "build_baseline_shadow_comparison",
    "build_replay_export_reproducibility",
    "materialize_replay_report_exports",
    "validate_replay_report_exports",
    "replay_report_export_contract_summary",
)))
