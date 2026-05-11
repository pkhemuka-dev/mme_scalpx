"""Lane D D5 candidate matrix builder.

This module combines proposed sweep candidates with read-only replay and RAW
index summaries. It creates a research-only matrix used by later leaderboard
and export stages.

It must not execute replay, train models, call brokers, write live state,
start runtime services, mutate strategy doctrine, or mutate replay engine code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import (
    OUTPUT_ROOT,
    VERDICT_NOT_READY_RAW_SOURCE_MISSING,
    VERDICT_NOT_READY_REPLAY_SOURCE_MISSING,
    VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
    OptimizerVerdictRow,
    row_to_dict,
)
from .sweep_space import (
    SweepSpaceSpec,
    default_sweep_space,
    generate_sweep_candidates,
)

CANDIDATE_MATRIX_CONTRACT_VERSION = "replay_optimization_d5_candidate_matrix_contract_v1"
CANDIDATE_MATRIX_ACCEPTED_FOR = "CANDIDATE_MATRIX_CONTRACT_ONLY"


@dataclass(frozen=True, slots=True)
class CandidateMatrixRow:
    optimization_id: str
    matrix_id: str
    candidate_id: str
    strategy_family: str
    side: str
    regime: str
    parameter_group: str
    parameter_name: str
    candidate_value: str
    replay_index_available: bool
    replay_artifact_count: int
    replay_artifact_kinds: tuple[str, ...]
    raw_index_available: bool
    raw_artifact_count: int
    raw_feature_families: tuple[str, ...]
    status: str
    readiness_verdict: str
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateMatrixBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    matrix_row_count: int
    replay_index_path: str | None
    raw_index_path: str | None
    replay_artifact_count: int
    raw_artifact_count: int
    readiness_verdict: str
    candidate_matrix_path: str
    optimizer_verdict_path: str
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


def _tuple_of_strings(value: Any) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(str(x) for x in value)
    return tuple()


def _replay_stats(replay_index_payload: Mapping[str, Any] | None) -> tuple[bool, int, tuple[str, ...]]:
    if not replay_index_payload:
        return False, 0, tuple()
    count = replay_index_payload.get("artifact_count")
    kinds = replay_index_payload.get("artifact_kinds")
    return True, int(count) if isinstance(count, int) else 0, _tuple_of_strings(kinds)


def _raw_stats(raw_index_payload: Mapping[str, Any] | None) -> tuple[bool, int, tuple[str, ...]]:
    if not raw_index_payload:
        return False, 0, tuple()
    count = raw_index_payload.get("artifact_count")
    families = raw_index_payload.get("feature_families")
    return True, int(count) if isinstance(count, int) else 0, _tuple_of_strings(families)


def _matrix_verdict(
    replay_available: bool,
    replay_count: int,
    raw_available: bool,
    raw_count: int,
) -> str:
    if not replay_available or replay_count <= 0:
        return VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    if not raw_available or raw_count <= 0:
        return VERDICT_NOT_READY_RAW_SOURCE_MISSING
    return VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE


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
        raise ValueError(f"D5 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def build_candidate_matrix_rows(
    optimization_id: str,
    *,
    replay_index_path: str | Path | None = None,
    raw_index_path: str | Path | None = None,
    space: SweepSpaceSpec | None = None,
    max_candidates: int = 10000,
) -> tuple[CandidateMatrixRow, ...]:
    candidates = generate_sweep_candidates(
        optimization_id,
        space or default_sweep_space(),
        max_candidates=max_candidates,
    )
    replay_payload = _safe_load_json(replay_index_path)
    raw_payload = _safe_load_json(raw_index_path)

    replay_available, replay_count, replay_kinds = _replay_stats(replay_payload)
    raw_available, raw_count, raw_families = _raw_stats(raw_payload)
    verdict = _matrix_verdict(replay_available, replay_count, raw_available, raw_count)

    rows: list[CandidateMatrixRow] = []
    for i, candidate in enumerate(candidates, start=1):
        rows.append(
            CandidateMatrixRow(
                optimization_id=optimization_id,
                matrix_id=f"MATRIX_{i:06d}",
                candidate_id=candidate.candidate_id,
                strategy_family=candidate.strategy_family,
                side=candidate.side,
                regime=candidate.regime,
                parameter_group=candidate.parameter_group,
                parameter_name=candidate.parameter_name,
                candidate_value=candidate.candidate_value,
                replay_index_available=replay_available,
                replay_artifact_count=replay_count,
                replay_artifact_kinds=replay_kinds,
                raw_index_available=raw_available,
                raw_artifact_count=raw_count,
                raw_feature_families=raw_families,
                status="PROPOSED_ONLY",
                readiness_verdict=verdict,
                remarks="D5 candidate matrix row. No replay execution or training performed.",
            )
        )
    return tuple(rows)


def write_candidate_matrix(
    optimization_id: str,
    output_dir: str | Path,
    *,
    replay_index_path: str | Path | None = None,
    raw_index_path: str | Path | None = None,
    space: SweepSpaceSpec | None = None,
    max_candidates: int = 10000,
) -> CandidateMatrixBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_candidate_matrix_rows(
        optimization_id,
        replay_index_path=replay_index_path,
        raw_index_path=raw_index_path,
        space=space,
        max_candidates=max_candidates,
    )

    if rows:
        verdict = rows[0].readiness_verdict
        replay_count = rows[0].replay_artifact_count
        raw_count = rows[0].raw_artifact_count
    else:
        verdict = VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
        replay_count = 0
        raw_count = 0

    matrix_path = out / "02_candidate_matrix.json"
    verdict_path = out / "09_optimizer_verdict.json"

    matrix_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Candidate Matrix",
        "contract_version": CANDIDATE_MATRIX_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_MATRIX_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "replay_index_path": str(replay_index_path) if replay_index_path else None,
        "raw_index_path": str(raw_index_path) if raw_index_path else None,
        "matrix_row_count": len(rows),
        "rows": [asdict(row) for row in rows],
        "safety": {
            "replay_execution_performed": False,
            "model_training_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False,
        },
    }
    matrix_path.write_text(json.dumps(matrix_payload, indent=2, sort_keys=True), encoding="utf-8")

    verdict_row = OptimizerVerdictRow(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        verdict=verdict,
        sample_days=0,
        sample_trades=0,
        risk_notes="D5 builds candidate matrix only. It does not approve replay source, RAW source, model training, paper, or live.",
        production_claim_allowed=False,
        paper_live_approved=False,
        remarks="Candidate matrix contract built from read-only indexes.",
    )
    verdict_path.write_text(json.dumps(row_to_dict(verdict_row), indent=2, sort_keys=True), encoding="utf-8")

    return CandidateMatrixBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=CANDIDATE_MATRIX_CONTRACT_VERSION,
        accepted_for=CANDIDATE_MATRIX_ACCEPTED_FOR,
        matrix_row_count=len(rows),
        replay_index_path=str(replay_index_path) if replay_index_path else None,
        raw_index_path=str(raw_index_path) if raw_index_path else None,
        replay_artifact_count=replay_count,
        raw_artifact_count=raw_count,
        readiness_verdict=verdict,
        candidate_matrix_path=matrix_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
    )


def candidate_matrix_summary(
    *,
    replay_index_path: str | Path | None = None,
    raw_index_path: str | Path | None = None,
    max_candidates: int = 10000,
) -> dict[str, Any]:
    rows = build_candidate_matrix_rows(
        "D5_SUMMARY",
        replay_index_path=replay_index_path,
        raw_index_path=raw_index_path,
        max_candidates=max_candidates,
    )
    verdict = rows[0].readiness_verdict if rows else VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    return {
        "contract_version": CANDIDATE_MATRIX_CONTRACT_VERSION,
        "accepted_for": CANDIDATE_MATRIX_ACCEPTED_FOR,
        "matrix_row_count": len(rows),
        "readiness_verdict": verdict,
        "replay_execution_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "CANDIDATE_MATRIX_CONTRACT_VERSION",
    "CANDIDATE_MATRIX_ACCEPTED_FOR",
    "CandidateMatrixRow",
    "CandidateMatrixBuildResult",
    "build_candidate_matrix_rows",
    "write_candidate_matrix",
    "candidate_matrix_summary",
)
