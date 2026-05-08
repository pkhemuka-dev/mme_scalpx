#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.batch_runner import build_scenario_matrix_plan, simulate_replay_batch_plan  # noqa: E402
from app.mme_scalpx.replay.report_exporter import (  # noqa: E402
    REPLAY_REQUIRED_REPORT_EXPORTS,
    build_baseline_shadow_comparison,
    materialize_replay_report_exports,
    replay_report_export_contract_summary,
    validate_replay_report_exports,
)
from app.mme_scalpx.replay.scenarios import REPLAY_REQUIRED_SCENARIOS  # noqa: E402


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return sum(1 for _ in csv.DictReader(fh))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_report_exports.json")
    args = parser.parse_args()

    contract_file = ROOT / "etc/replay/schemas/replay_report_export_contract_v1.json"
    manifest_file = ROOT / "etc/replay/forensics/replay_report_export_manifest_v1.json"

    contract = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}

    baseline_plan = build_scenario_matrix_plan(dates=("2026-05-01",), scenarios=("full_fill",))
    shadow_plan = build_scenario_matrix_plan(dates=("2026-05-01",), scenarios=REPLAY_REQUIRED_SCENARIOS)
    baseline_result = simulate_replay_batch_plan(baseline_plan)
    shadow_result = simulate_replay_batch_plan(shadow_plan)

    comparison = build_baseline_shadow_comparison(
        baseline_label="baseline_full_fill",
        baseline_result=baseline_result,
        shadow_label="shadow_scenario_matrix",
        shadow_result=shadow_result,
    )

    run_id = f"batch27l_report_export_{shadow_plan['plan_id']}"
    export_root = f"run/replay/{run_id}/exports"
    result = materialize_replay_report_exports(
        run_id=run_id,
        simulation_result=shadow_result,
        export_root=export_root,
        baseline_comparison=comparison,
    )

    validation = validate_replay_report_exports(result)
    root = Path(result["export_root"])

    required_exports_ok = all((root / name).exists() for name in REPLAY_REQUIRED_REPORT_EXPORTS)
    manifest_json = read_json(root / "00_export_manifest.json")
    trade_json = read_json(root / "01_trade_log.json")
    candidate_json = read_json(root / "02_candidate_log.json")
    blocker_json = read_json(root / "03_blocker_chain.json")
    side_json = read_json(root / "04_side_split_summary.json")
    family_json = read_json(root / "05_family_split_summary.json")
    scenario_json = read_json(root / "06_scenario_summary.json")
    pnl_json = read_json(root / "07_pnl_execution_shadow_summary.json")
    comparison_json = read_json(root / "08_baseline_vs_shadow_comparison.json")
    reproducibility_json = read_json(root / "09_export_reproducibility.json")

    trade_log_ok = len(trade_json) == len(REPLAY_REQUIRED_SCENARIOS) and csv_row_count(root / "01_trade_log.csv") == len(trade_json)
    candidate_log_ok = len(candidate_json) == len(REPLAY_REQUIRED_SCENARIOS) * 10 and csv_row_count(root / "02_candidate_log.csv") == len(candidate_json)
    blocker_chain_ok = len(blocker_json) >= len(REPLAY_REQUIRED_SCENARIOS) and csv_row_count(root / "03_blocker_chain.csv") == len(blocker_json)
    side_split_ok = len(side_json) == 2 and csv_row_count(root / "04_side_split_summary.csv") == 2
    family_split_ok = len(family_json) == 5 and csv_row_count(root / "05_family_split_summary.csv") == 5
    scenario_summary_ok = len(scenario_json) == len(REPLAY_REQUIRED_SCENARIOS) and csv_row_count(root / "06_scenario_summary.csv") == len(scenario_json)
    pnl_summary_ok = len(pnl_json) == 1 and csv_row_count(root / "07_pnl_execution_shadow_summary.csv") == 1
    comparison_ok = (
        comparison_json.get("schema_version") == "replay_baseline_shadow_comparison_v1"
        and comparison_json.get("baseline_label") == "baseline_full_fill"
        and comparison_json.get("shadow_label") == "shadow_scenario_matrix"
        and comparison_json.get("paper_armed_approved") is False
    )
    reproducibility_ok = (
        bool(reproducibility_json.get("export_reproducibility_hash"))
        and reproducibility_json.get("export_reproducibility_hash") == result.get("export_reproducibility_hash")
    )

    json_no_live_ok = all(
        payload.get("paper_armed_approved") is False
        and payload.get("live_trading_approved") is False
        and payload.get("production_doctrine_changed") is False
        for payload in (
            manifest_json,
            comparison_json,
            reproducibility_json,
        )
    )
    collection_no_live_ok = all(
        all(
            row.get("paper_armed_approved") is False
            and row.get("live_trading_approved") is False
            and row.get("production_doctrine_changed") is False
            for row in rows
        )
        for rows in (
            trade_json,
            candidate_json,
            blocker_json,
            side_json,
            family_json,
            scenario_json,
            pnl_json,
        )
    )

    contract_ok = (
        contract_file.exists()
        and manifest_file.exists()
        and tuple(contract.get("required_exports", ())) == tuple(REPLAY_REQUIRED_REPORT_EXPORTS)
        and tuple(manifest.get("required_exports", ())) == tuple(REPLAY_REQUIRED_REPORT_EXPORTS)
    )

    summary = replay_report_export_contract_summary()

    report_exports_ok = bool(
        validation.get("ok") is True
        and contract_ok
        and required_exports_ok
        and trade_log_ok
        and candidate_log_ok
        and blocker_chain_ok
        and side_split_ok
        and family_split_ok
        and scenario_summary_ok
        and pnl_summary_ok
        and comparison_ok
        and reproducibility_ok
        and json_no_live_ok
        and collection_no_live_ok
        and summary.get("paper_armed_approved") is False
    )

    proof = {
        "schema_version": "proof_replay_report_exports_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "report_exports_ok": report_exports_ok,
        "validation_ok": validation.get("ok"),
        "contract_ok": contract_ok,
        "required_exports_ok": required_exports_ok,
        "trade_log_ok": trade_log_ok,
        "candidate_log_ok": candidate_log_ok,
        "blocker_chain_ok": blocker_chain_ok,
        "side_split_ok": side_split_ok,
        "family_split_ok": family_split_ok,
        "scenario_summary_ok": scenario_summary_ok,
        "pnl_summary_ok": pnl_summary_ok,
        "comparison_ok": comparison_ok,
        "reproducibility_ok": reproducibility_ok,
        "json_no_live_ok": json_no_live_ok,
        "collection_no_live_ok": collection_no_live_ok,
        "run_id": run_id,
        "export_root": str(root),
        "written_exports": result.get("written_exports"),
        "export_reproducibility_hash": result.get("export_reproducibility_hash"),
        "validation": validation,
        "contract_summary": summary,
        "report_export_shape": "PROVEN_BY_27L",
        "export_reproducibility_hash_status": "PROVEN_BY_27L",
        "full_report_semantic_accuracy": "NOT_PROVEN_IN_27L",
        "full_live_replay_parity": "NOT_PROVEN_IN_27L",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if report_exports_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "report_exports_ok": report_exports_ok,
        "required_exports_ok": required_exports_ok,
        "trade_log_ok": trade_log_ok,
        "candidate_log_ok": candidate_log_ok,
        "blocker_chain_ok": blocker_chain_ok,
        "side_split_ok": side_split_ok,
        "family_split_ok": family_split_ok,
        "scenario_summary_ok": scenario_summary_ok,
        "pnl_summary_ok": pnl_summary_ok,
        "comparison_ok": comparison_ok,
        "reproducibility_ok": reproducibility_ok,
        "export_root": str(root),
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if report_exports_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
