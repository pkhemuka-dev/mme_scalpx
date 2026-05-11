"""Lane D D23 matching dry-run contract.

This module performs diagnostics-only candidate/result key probing using the
keys discovered by D22. It may count possible dry-run matches, but it does not
perform real candidate-to-trade matching, does not bind labels, does not
calculate PnL, does not train/predict models, does not execute replay, does not
call brokers, does not write live Redis, does not mutate doctrine, and does not
approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

MATCHING_DRY_RUN_CONTRACT_VERSION = "replay_optimization_d23_matching_dry_run_contract_v1"
MATCHING_DRY_RUN_ACCEPTED_FOR = "MATCHING_DRY_RUN_DIAGNOSTIC_ONLY"

DRY_STATUS_BLOCKED_NO_KEYS = "BLOCKED_NO_DRY_RUN_KEYS"
DRY_STATUS_BLOCKED_NO_ROWS = "BLOCKED_NO_DRY_RUN_ROWS"
DRY_STATUS_WEAK_SIDE_ONLY = "DRY_RUN_WEAK_SIDE_ONLY_NOT_LABEL_READY"
DRY_STATUS_DIAGNOSTIC_READY = "DRY_RUN_DIAGNOSTIC_READY_NOT_LABEL_READY"

DRY_RUN_COLUMNS = (
    "optimization_id",
    "dry_run_id",
    "candidate_id",
    "strategy_family",
    "side",
    "parameter_group",
    "parameter_name",
    "dry_run_keys",
    "features_match_count",
    "strategy_match_count",
    "risk_match_count",
    "execution_shadow_match_count",
    "min_match_count",
    "max_match_count",
    "dry_run_status",
    "confidence_level",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "label_pnl",
    "label_profitable",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class MatchingDryRunRow:
    optimization_id: str
    dry_run_id: str
    candidate_id: str
    strategy_family: str
    side: str
    parameter_group: str
    parameter_name: str
    dry_run_keys: str
    features_match_count: int
    strategy_match_count: int
    risk_match_count: int
    execution_shadow_match_count: int
    min_match_count: int
    max_match_count: int
    dry_run_status: str
    confidence_level: str
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    label_pnl: float | None = None
    label_profitable: bool | None = None
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class MatchingDryRunBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    matching_rows_path: str | None
    match_key_discovery_path: str | None
    nonzero_verification_report_path: str | None
    dry_run_report_path: str
    dry_run_rows_json_path: str
    dry_run_rows_csv_path: str
    optimizer_verdict_path: str
    dry_run_row_count: int
    dry_run_status: str
    weak_side_only: bool
    candidate_trade_matching_performed: bool = False
    label_binding_allowed: bool = False
    labels_bound: bool = False
    replay_execution_performed: bool = False
    real_pnl_calculation_performed: bool = False
    model_training_performed: bool = False
    model_prediction_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_json(path_value: str | Path | None) -> Any:
    if not path_value:
        return None
    p = Path(path_value)
    if not p.exists() or not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _rows_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("rows", "items", "records", "data", "results"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, dict)]
    return []


def _output_guard(output_dir: str | Path) -> Path:
    out = Path(output_dir)
    normalized = out.as_posix().rstrip("/")
    allowed_guard = "/" + OUTPUT_ROOT.strip("/") + "/"
    normalized_guard = "/" + normalized.strip("/") + "/"
    if not (
        normalized == OUTPUT_ROOT
        or normalized.startswith(OUTPUT_ROOT + "/")
        or normalized.startswith("run/replay_optimization/")
        or allowed_guard in normalized_guard
    ):
        raise ValueError(f"D23 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _d19_audit(report: Any) -> dict[str, Any]:
    if isinstance(report, dict):
        audit = report.get("audit")
        if isinstance(audit, dict):
            return audit
    return {}


def _preferred_keys(discovery_payload: Any) -> tuple[str, ...]:
    if isinstance(discovery_payload, dict):
        keys = discovery_payload.get("preferred_common_keys")
        if isinstance(keys, list):
            return tuple(str(k) for k in keys if k)
        audit = discovery_payload.get("audit")
        if isinstance(audit, dict):
            keys = audit.get("preferred_common_keys")
            if isinstance(keys, list):
                return tuple(str(k) for k in keys if k)
    return tuple()


def _row_matches(candidate: Mapping[str, Any], result_row: Mapping[str, Any], keys: Sequence[str]) -> bool:
    if not keys:
        return False
    for key in keys:
        if key not in candidate or key not in result_row:
            return False
        if str(candidate.get(key)) != str(result_row.get(key)):
            return False
    return True


def _count_matches(candidate: Mapping[str, Any], rows: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> int:
    return sum(1 for row in rows if _row_matches(candidate, row, keys))


def build_matching_dry_run_rows(
    optimization_id: str,
    *,
    matching_rows_path: str | Path | None,
    match_key_discovery_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[MatchingDryRunRow, ...]:
    matching_payload = _safe_load_json(matching_rows_path)
    candidate_rows = _rows_from_payload(matching_payload)

    discovery_payload = _safe_load_json(match_key_discovery_path)
    dry_keys = _preferred_keys(discovery_payload)

    d19_report = _safe_load_json(nonzero_verification_report_path)
    d19 = _d19_audit(d19_report)

    result_sets = {
        "features": _rows_from_payload(_safe_load_json(d19.get("features_ref"))),
        "strategy": _rows_from_payload(_safe_load_json(d19.get("strategy_ref"))),
        "risk": _rows_from_payload(_safe_load_json(d19.get("risk_ref"))),
        "execution_shadow": _rows_from_payload(_safe_load_json(d19.get("execution_shadow_ref"))),
    }

    if not candidate_rows or not any(result_sets.values()):
        return tuple()

    weak_side_only = tuple(dry_keys) == ("side",)
    key_text = ",".join(dry_keys)

    rows: list[MatchingDryRunRow] = []
    for i, candidate in enumerate(candidate_rows[:max_rows], start=1):
        features_count = _count_matches(candidate, result_sets["features"], dry_keys)
        strategy_count = _count_matches(candidate, result_sets["strategy"], dry_keys)
        risk_count = _count_matches(candidate, result_sets["risk"], dry_keys)
        execution_count = _count_matches(candidate, result_sets["execution_shadow"], dry_keys)
        counts = [features_count, strategy_count, risk_count, execution_count]
        min_count = min(counts)
        max_count = max(counts)

        if not dry_keys:
            status = DRY_STATUS_BLOCKED_NO_KEYS
            confidence = "none"
            remarks = "No dry-run keys available."
        elif weak_side_only:
            status = DRY_STATUS_WEAK_SIDE_ONLY
            confidence = "weak"
            remarks = "Only side is common. This is not sufficient for label binding."
        else:
            status = DRY_STATUS_DIAGNOSTIC_READY
            confidence = "diagnostic_only"
            remarks = "Dry-run keys exist, but this batch does not perform real matching or labels."

        rows.append(
            MatchingDryRunRow(
                optimization_id=optimization_id,
                dry_run_id=f"DRY_{i:06d}",
                candidate_id=str(candidate.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                strategy_family=str(candidate.get("strategy_family") or "UNKNOWN"),
                side=str(candidate.get("side") or "UNKNOWN"),
                parameter_group=str(candidate.get("parameter_group") or "UNKNOWN"),
                parameter_name=str(candidate.get("parameter_name") or "UNKNOWN"),
                dry_run_keys=key_text,
                features_match_count=features_count,
                strategy_match_count=strategy_count,
                risk_match_count=risk_count,
                execution_shadow_match_count=execution_count,
                min_match_count=min_count,
                max_match_count=max_count,
                dry_run_status=status,
                confidence_level=confidence,
                candidate_trade_matching_performed=False,
                label_binding_allowed=False,
                labels_bound=False,
                label_pnl=None,
                label_profitable=None,
                remarks=remarks,
            )
        )
    return tuple(rows)


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_matching_dry_run(
    optimization_id: str,
    output_dir: str | Path,
    *,
    matching_rows_path: str | Path | None,
    match_key_discovery_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
    max_rows: int = 10000,
) -> MatchingDryRunBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    discovery_payload = _safe_load_json(match_key_discovery_path)
    dry_keys = _preferred_keys(discovery_payload)
    weak_side_only = tuple(dry_keys) == ("side",)

    rows = build_matching_dry_run_rows(
        optimization_id,
        matching_rows_path=matching_rows_path,
        match_key_discovery_path=match_key_discovery_path,
        nonzero_verification_report_path=nonzero_verification_report_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in rows]

    if not rows:
        status = DRY_STATUS_BLOCKED_NO_ROWS
    elif not dry_keys:
        status = DRY_STATUS_BLOCKED_NO_KEYS
    elif weak_side_only:
        status = DRY_STATUS_WEAK_SIDE_ONLY
    else:
        status = DRY_STATUS_DIAGNOSTIC_READY

    report_path = out / "26_matching_dry_run_report.json"
    rows_json_path = out / "26_matching_dry_run_rows.json"
    rows_csv_path = out / "26_matching_dry_run_rows.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    report = {
        "schema_name": "MME-ScalpX Replay Optimization Matching Dry-Run Diagnostic",
        "contract_version": MATCHING_DRY_RUN_CONTRACT_VERSION,
        "accepted_for": MATCHING_DRY_RUN_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "matching_rows_path": str(matching_rows_path) if matching_rows_path else None,
        "match_key_discovery_path": str(match_key_discovery_path) if match_key_discovery_path else None,
        "nonzero_verification_report_path": str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        "dry_run_keys": list(dry_keys),
        "weak_side_only": weak_side_only,
        "dry_run_row_count": len(rows),
        "dry_run_status": status,
        "safety": {
            "candidate_trade_matching_performed": False,
            "label_binding_allowed": False,
            "labels_bound": False,
            "replay_execution_performed": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False
        },
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    rows_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Matching Dry-Run Rows",
        "contract_version": MATCHING_DRY_RUN_CONTRACT_VERSION,
        "accepted_for": MATCHING_DRY_RUN_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "dry_run_status": status,
        "dry_run_row_count": len(rows),
        "rows": row_dicts,
        "safety": report["safety"],
    }
    rows_json_path.write_text(json.dumps(rows_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(rows_csv_path, DRY_RUN_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": MATCHING_DRY_RUN_CONTRACT_VERSION,
        "accepted_for": MATCHING_DRY_RUN_ACCEPTED_FOR,
        "dry_run_status": status,
        "dry_run_row_count": len(rows),
        "weak_side_only": weak_side_only,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D23 is dry-run diagnostics only. No real matching or labels.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return MatchingDryRunBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=MATCHING_DRY_RUN_CONTRACT_VERSION,
        accepted_for=MATCHING_DRY_RUN_ACCEPTED_FOR,
        matching_rows_path=str(matching_rows_path) if matching_rows_path else None,
        match_key_discovery_path=str(match_key_discovery_path) if match_key_discovery_path else None,
        nonzero_verification_report_path=str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        dry_run_report_path=report_path.as_posix(),
        dry_run_rows_json_path=rows_json_path.as_posix(),
        dry_run_rows_csv_path=rows_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        dry_run_row_count=len(rows),
        dry_run_status=status,
        weak_side_only=weak_side_only,
    )


__all__ = (
    "MATCHING_DRY_RUN_CONTRACT_VERSION",
    "MATCHING_DRY_RUN_ACCEPTED_FOR",
    "DRY_STATUS_BLOCKED_NO_KEYS",
    "DRY_STATUS_BLOCKED_NO_ROWS",
    "DRY_STATUS_WEAK_SIDE_ONLY",
    "DRY_STATUS_DIAGNOSTIC_READY",
    "DRY_RUN_COLUMNS",
    "MatchingDryRunRow",
    "MatchingDryRunBuildResult",
    "build_matching_dry_run_rows",
    "write_matching_dry_run",
)
