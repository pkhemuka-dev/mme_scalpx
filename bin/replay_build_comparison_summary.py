#!/usr/bin/env python3
"""
bin/replay_build_comparison_summary.py

Freeze-grade comparison summary builder for replay runs.

This script reads two replay run summaries and writes:
- 20_comparison_summary.json
- 21_comparison_summary.csv

It is intentionally thin:
- no replay execution
- no metrics recomputation
- no hidden defaults beyond explicit fallback handling
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.contracts import COMPARISON_SUMMARY_COLUMNS


@dataclass(frozen=True, slots=True)
class ComparisonSummaryInput:
    run_dir: Path
    summary_path: Path
    payload: dict[str, Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON payload must be an object: {path}")
    return payload


def _normalize_run_input(run_dir: Path) -> ComparisonSummaryInput:
    summary_path = run_dir / "artifacts" / "10_run_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"missing run summary: {summary_path}")
    return ComparisonSummaryInput(
        run_dir=run_dir,
        summary_path=summary_path,
        payload=_load_json(summary_path),
    )


def _as_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return int(str(value))


def _as_float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value))


def _diff_num(lhs: float | int | None, rhs: float | int | None) -> float | int | None:
    if lhs is None or rhs is None:
        return None
    return rhs - lhs


def _comparison_integrity_status(
    baseline_verdict: str | None,
    shadow_verdict: str | None,
) -> str:
    verdicts = {baseline_verdict, shadow_verdict}
    if "fail" in verdicts:
        return "fail"
    if "warn" in verdicts:
        return "warn"
    return "pass"


def _changed_parameters(
    baseline: dict[str, Any],
    shadow: dict[str, Any],
) -> list[str]:
    tracked = [
        "doctrine_mode",
        "replay_scope",
        "speed_mode",
        "side_mode",
        "dataset_profile",
        "replay_profile",
        "experiment_profile",
        "batch_profile",
        "forensic_profile",
        "integrity_profile",
        "override_pack_id",
        "shadow_label",
        "input_fingerprint",
    ]
    changed: list[str] = []
    for key in tracked:
        if baseline.get(key) != shadow.get(key):
            changed.append(key)
    return changed


def _csv_scalar(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {column: _csv_scalar(payload.get(column)) for column in COMPARISON_SUMMARY_COLUMNS}
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(COMPARISON_SUMMARY_COLUMNS),
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerow(row)


def build_comparison_summary_payload(
    *,
    comparison_id: str,
    baseline: ComparisonSummaryInput,
    shadow: ComparisonSummaryInput,
    operator_verdict: str | None,
    narration: str | None,
) -> dict[str, Any]:
    b = baseline.payload
    s = shadow.payload

    baseline_pnl = _as_float_or_none(b.get("pnl_total"))
    shadow_pnl = _as_float_or_none(s.get("pnl_total"))

    baseline_trade_count = _as_int(b.get("trade_count"))
    shadow_trade_count = _as_int(s.get("trade_count"))

    baseline_candidate_count = _as_int(b.get("candidate_count"))
    shadow_candidate_count = _as_int(s.get("candidate_count"))

    baseline_blocker_count = _as_int(b.get("blocker_count"))
    shadow_blocker_count = _as_int(s.get("blocker_count"))

    baseline_regime_pass_count = _as_int(b.get("regime_pass_count"))
    shadow_regime_pass_count = _as_int(s.get("regime_pass_count"))

    dataset_fingerprint_match = b.get("dataset_fingerprint") == s.get("dataset_fingerprint")
    identical_input_basis = (
        dataset_fingerprint_match
        and b.get("trading_dates") == s.get("trading_dates")
        and b.get("selection_mode") == s.get("selection_mode")
    )

    return {
        "comparison_id": comparison_id,
        "comparison_created_at": _utc_now_iso(),
        "baseline_run_id": b.get("run_id"),
        "shadow_run_id": s.get("run_id"),
        "identical_input_basis": identical_input_basis,
        "dataset_fingerprint_match": dataset_fingerprint_match,
        "baseline_override_id": b.get("override_pack_id"),
        "shadow_override_id": s.get("override_pack_id"),
        "changed_parameters": _changed_parameters(b, s),
        "baseline_pnl": baseline_pnl,
        "shadow_pnl": shadow_pnl,
        "pnl_diff": _diff_num(baseline_pnl, shadow_pnl),
        "baseline_trade_count": baseline_trade_count,
        "shadow_trade_count": shadow_trade_count,
        "trade_count_diff": shadow_trade_count - baseline_trade_count,
        "baseline_candidate_count": baseline_candidate_count,
        "shadow_candidate_count": shadow_candidate_count,
        "candidate_diff": shadow_candidate_count - baseline_candidate_count,
        "baseline_blocker_count": baseline_blocker_count,
        "shadow_blocker_count": shadow_blocker_count,
        "blocker_diff": shadow_blocker_count - baseline_blocker_count,
        "baseline_regime_pass_count": baseline_regime_pass_count,
        "shadow_regime_pass_count": shadow_regime_pass_count,
        "regime_pass_diff": shadow_regime_pass_count - baseline_regime_pass_count,
        "integrity_status": _comparison_integrity_status(
            str(b.get("integrity_verdict")) if b.get("integrity_verdict") is not None else None,
            str(s.get("integrity_verdict")) if s.get("integrity_verdict") is not None else None,
        ),
        "operator_verdict": operator_verdict,
        "narration": narration,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build replay comparison summary artifacts")
    parser.add_argument("--baseline-run-dir", required=True)
    parser.add_argument("--shadow-run-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--comparison-id", default=None)
    parser.add_argument("--operator-verdict", default=None)
    parser.add_argument("--narration", default=None)
    args = parser.parse_args()

    baseline = _normalize_run_input(Path(args.baseline_run_dir))
    shadow = _normalize_run_input(Path(args.shadow_run_dir))
    output_dir = Path(args.output_dir)

    comparison_id = args.comparison_id or (
        f"comparison_{baseline.payload.get('run_id')}_vs_{shadow.payload.get('run_id')}"
    )

    payload = build_comparison_summary_payload(
        comparison_id=comparison_id,
        baseline=baseline,
        shadow=shadow,
        operator_verdict=args.operator_verdict,
        narration=args.narration,
    )

    json_path = output_dir / "20_comparison_summary.json"
    csv_path = output_dir / "21_comparison_summary.csv"

    _write_json(json_path, payload)
    _write_csv(csv_path, payload)

    print(json.dumps(
        {
            "status": "ok",
            "comparison_id": comparison_id,
            "json_path": str(json_path),
            "csv_path": str(csv_path),
            "baseline_run_id": payload["baseline_run_id"],
            "shadow_run_id": payload["shadow_run_id"],
            "dataset_fingerprint_match": payload["dataset_fingerprint_match"],
            "changed_parameters": payload["changed_parameters"],
        },
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
