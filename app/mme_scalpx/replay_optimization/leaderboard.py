"""Lane D D6 leaderboard schema and builder.

This module builds a research-only leaderboard shell from a D5 candidate matrix.
It does not claim profitability because verified replay PnL/result binding is
not introduced in D6.

It must not execute replay, train models, call brokers, write live state,
start runtime services, mutate strategy doctrine, or mutate replay engine code.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import (
    LEADERBOARD_COLUMNS,
    OUTPUT_ROOT,
    VERDICT_NOT_READY_REPLAY_SOURCE_MISSING,
    VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
    LeaderboardRow,
    OptimizerVerdictRow,
    row_to_dict,
)

LEADERBOARD_CONTRACT_VERSION = "replay_optimization_d6_leaderboard_contract_v1"
LEADERBOARD_ACCEPTED_FOR = "LEADERBOARD_CONTRACT_ONLY"


@dataclass(frozen=True, slots=True)
class LeaderboardBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    leaderboard_row_count: int
    candidate_matrix_path: str | None
    leaderboard_csv_path: str
    leaderboard_json_path: str
    result_summary_csv_path: str
    optimizer_verdict_path: str
    readiness_verdict: str
    replay_execution_performed: bool = False
    model_training_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_json(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    try:
        payload = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


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
        raise ValueError(f"D6 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _matrix_rows(candidate_matrix_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not candidate_matrix_payload:
        return []
    rows = candidate_matrix_payload.get("rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _readiness_from_matrix(candidate_matrix_payload: Mapping[str, Any] | None) -> str:
    rows = _matrix_rows(candidate_matrix_payload)
    if not rows:
        return VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    value = rows[0].get("readiness_verdict")
    if isinstance(value, str) and value:
        return value
    return VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE


def build_leaderboard_rows(
    optimization_id: str,
    *,
    candidate_matrix_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[LeaderboardRow, ...]:
    if max_rows <= 0:
        raise ValueError("max_rows must be positive")

    matrix_payload = _safe_load_json(candidate_matrix_path)
    matrix_rows = _matrix_rows(matrix_payload)
    readiness = _readiness_from_matrix(matrix_payload)

    out: list[LeaderboardRow] = []
    for rank, row in enumerate(matrix_rows[:max_rows], start=1):
        out.append(
            LeaderboardRow(
                optimization_id=optimization_id,
                rank=rank,
                candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{rank:06d}"),
                strategy_family=str(row.get("strategy_family") or "UNKNOWN"),
                side=str(row.get("side") or "UNKNOWN"),
                regime=str(row.get("regime") or "UNKNOWN"),
                total_pnl=0.0,
                trade_count=0,
                win_count=0,
                loss_count=0,
                win_rate=0.0,
                avg_pnl_per_trade=0.0,
                max_drawdown=None,
                profit_factor=None,
                candidate_count=0,
                blocker_count=0,
                sample_days=0,
                overfit_risk_flag=True,
                optimizer_verdict=readiness,
                remarks=(
                    "D6 contract-only leaderboard placeholder. "
                    "No replay result PnL has been bound yet."
                ),
            )
        )
    return tuple(out)


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_leaderboard(
    optimization_id: str,
    output_dir: str | Path,
    *,
    candidate_matrix_path: str | Path | None,
    max_rows: int = 10000,
) -> LeaderboardBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_leaderboard_rows(
        optimization_id,
        candidate_matrix_path=candidate_matrix_path,
        max_rows=max_rows,
    )
    row_dicts = [row_to_dict(row) for row in rows]
    readiness = rows[0].optimizer_verdict if rows else VERDICT_NOT_READY_REPLAY_SOURCE_MISSING

    leaderboard_csv = out / "06_leaderboard.csv"
    leaderboard_json = out / "06_leaderboard.json"
    result_summary_csv = out / "05_result_summary.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    _write_csv(leaderboard_csv, LEADERBOARD_COLUMNS, row_dicts)
    leaderboard_json.write_text(
        json.dumps(
            {
                "schema_name": "MME-ScalpX Replay Optimization Leaderboard",
                "contract_version": LEADERBOARD_CONTRACT_VERSION,
                "accepted_for": LEADERBOARD_ACCEPTED_FOR,
                "optimization_id": optimization_id,
                "created_at": _utc_now(),
                "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else None,
                "leaderboard_row_count": len(rows),
                "rows": row_dicts,
                "safety": {
                    "replay_execution_performed": False,
                    "model_training_performed": False,
                    "broker_calls_executed": False,
                    "live_redis_writes_executed": False,
                    "paper_or_live_enabled": False,
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    summary_rows = [
        {
            "optimization_id": optimization_id,
            "created_at": _utc_now(),
            "contract_version": LEADERBOARD_CONTRACT_VERSION,
            "accepted_for": LEADERBOARD_ACCEPTED_FOR,
            "candidate_matrix_path": str(candidate_matrix_path) if candidate_matrix_path else "",
            "leaderboard_row_count": len(rows),
            "readiness_verdict": readiness,
            "total_pnl": 0.0,
            "trade_count": 0,
            "sample_days": 0,
            "remarks": "D6 contract-only summary. No realized PnL bound yet.",
        }
    ]
    _write_csv(
        result_summary_csv,
        (
            "optimization_id",
            "created_at",
            "contract_version",
            "accepted_for",
            "candidate_matrix_path",
            "leaderboard_row_count",
            "readiness_verdict",
            "total_pnl",
            "trade_count",
            "sample_days",
            "remarks",
        ),
        summary_rows,
    )

    verdict_row = OptimizerVerdictRow(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        verdict=readiness,
        sample_days=0,
        sample_trades=0,
        risk_notes=(
            "D6 creates leaderboard schema only. No replay PnL/result binding, "
            "ML training, paper, or live approval."
        ),
        production_claim_allowed=False,
        paper_live_approved=False,
        remarks="Leaderboard is a placeholder until replay result binding exists.",
    )
    verdict_path.write_text(json.dumps(row_to_dict(verdict_row), indent=2, sort_keys=True), encoding="utf-8")

    return LeaderboardBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=LEADERBOARD_CONTRACT_VERSION,
        accepted_for=LEADERBOARD_ACCEPTED_FOR,
        leaderboard_row_count=len(rows),
        candidate_matrix_path=str(candidate_matrix_path) if candidate_matrix_path else None,
        leaderboard_csv_path=leaderboard_csv.as_posix(),
        leaderboard_json_path=leaderboard_json.as_posix(),
        result_summary_csv_path=result_summary_csv.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        readiness_verdict=readiness,
    )


def leaderboard_summary(
    *,
    candidate_matrix_path: str | Path | None,
    max_rows: int = 10000,
) -> dict[str, Any]:
    rows = build_leaderboard_rows(
        "D6_SUMMARY",
        candidate_matrix_path=candidate_matrix_path,
        max_rows=max_rows,
    )
    readiness = rows[0].optimizer_verdict if rows else VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    return {
        "contract_version": LEADERBOARD_CONTRACT_VERSION,
        "accepted_for": LEADERBOARD_ACCEPTED_FOR,
        "leaderboard_row_count": len(rows),
        "readiness_verdict": readiness,
        "replay_execution_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "LEADERBOARD_CONTRACT_VERSION",
    "LEADERBOARD_ACCEPTED_FOR",
    "LeaderboardBuildResult",
    "build_leaderboard_rows",
    "write_leaderboard",
    "leaderboard_summary",
)
