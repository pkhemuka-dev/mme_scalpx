"""Lane D D22 match-key discovery audit.

This module inventories candidate rows and verified replay result rows to
discover possible future join keys for candidate-to-trade matching.

D22 is audit-only. It does not perform matching, bind labels, calculate PnL,
train/predict models, execute replay, call brokers, write live Redis, mutate
doctrine, or approve paper/live.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .contracts import OUTPUT_ROOT

MATCH_KEY_DISCOVERY_CONTRACT_VERSION = "replay_optimization_d22_match_key_discovery_contract_v1"
MATCH_KEY_DISCOVERY_ACCEPTED_FOR = "MATCH_KEY_DISCOVERY_AUDIT_ONLY"

DISCOVERY_STATUS_BLOCKED_NO_MATCHING_ROWS = "BLOCKED_NO_MATCHING_ROWS"
DISCOVERY_STATUS_BLOCKED_NO_RESULT_ROWS = "BLOCKED_NO_RESULT_ROWS"
DISCOVERY_STATUS_BLOCKED_NO_COMMON_KEYS = "BLOCKED_NO_COMMON_KEYS"
DISCOVERY_STATUS_READY_FOR_MATCHING_DRY_RUN_CONTRACT = "READY_FOR_MATCHING_DRY_RUN_CONTRACT_ONLY"

RESULT_ARTIFACT_FIELDS = (
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)

PREFERRED_JOIN_KEYS = (
    "frame_ts_ns",
    "ts_ns",
    "timestamp_ns",
    "event_ts_ns",
    "decision_ts_ns",
    "frame_id",
    "bar_id",
    "symbol",
    "instrument_key",
    "instrument_token",
    "strategy_family",
    "family",
    "side",
    "candidate_id",
    "decision_id",
    "signal_id",
    "entry_id",
    "run_id",
    "selected_date",
)


@dataclass(frozen=True, slots=True)
class MatchKeyDiscoveryAudit:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    matching_rows_path: str | None
    nonzero_verification_report_path: str | None
    candidate_row_count: int
    features_row_count: int
    strategy_row_count: int
    risk_row_count: int
    execution_shadow_row_count: int
    candidate_keys: tuple[str, ...]
    features_keys: tuple[str, ...]
    strategy_keys: tuple[str, ...]
    risk_keys: tuple[str, ...]
    execution_shadow_keys: tuple[str, ...]
    common_candidate_result_keys: tuple[str, ...]
    preferred_common_keys: tuple[str, ...]
    result_artifact_common_keys: tuple[str, ...]
    discovery_status: str
    candidate_trade_matching_allowed: bool = False
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
    production_claim_allowed: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class MatchKeyDiscoveryBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    match_key_discovery_path: str
    optimizer_verdict_path: str
    discovery_status: str
    candidate_row_count: int
    result_min_row_count: int
    preferred_common_key_count: int
    candidate_trade_matching_allowed: bool = False
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


def _keys_from_rows(rows: list[dict[str, Any]]) -> tuple[str, ...]:
    keys: set[str] = set()
    for row in rows:
        keys.update(str(k) for k in row.keys())
    return tuple(sorted(keys))


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
        raise ValueError(f"D22 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _d19_audit(report: Any) -> dict[str, Any]:
    if isinstance(report, dict):
        audit = report.get("audit")
        if isinstance(audit, dict):
            return audit
    return {}


def build_match_key_discovery_audit(
    optimization_id: str,
    *,
    matching_rows_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
) -> MatchKeyDiscoveryAudit:
    matching_payload = _safe_load_json(matching_rows_path)
    candidate_rows = _rows_from_payload(matching_payload)

    d19_report = _safe_load_json(nonzero_verification_report_path)
    d19 = _d19_audit(d19_report)

    artifact_rows: dict[str, list[dict[str, Any]]] = {}
    artifact_keys: dict[str, tuple[str, ...]] = {}
    artifact_counts: dict[str, int] = {}

    for ref_field in RESULT_ARTIFACT_FIELDS:
        ref = d19.get(ref_field)
        rows = _rows_from_payload(_safe_load_json(ref))
        artifact_rows[ref_field] = rows
        artifact_keys[ref_field] = _keys_from_rows(rows)
        artifact_counts[ref_field] = len(rows)

    candidate_keys = _keys_from_rows(candidate_rows)
    candidate_key_set = set(candidate_keys)

    result_key_sets = [set(artifact_keys[field]) for field in RESULT_ARTIFACT_FIELDS if artifact_keys[field]]
    if result_key_sets:
        result_common = set.intersection(*result_key_sets)
        result_union = set.union(*result_key_sets)
    else:
        result_common = set()
        result_union = set()

    common_candidate_result = tuple(sorted(candidate_key_set & result_union))
    preferred_common = tuple(key for key in PREFERRED_JOIN_KEYS if key in common_candidate_result)

    result_min_count = min(artifact_counts.values()) if artifact_counts else 0

    if not candidate_rows:
        status = DISCOVERY_STATUS_BLOCKED_NO_MATCHING_ROWS
        remarks = "D20 matching rows are missing."
    elif result_min_count <= 0:
        status = DISCOVERY_STATUS_BLOCKED_NO_RESULT_ROWS
        remarks = "Verified replay result rows are missing."
    elif not common_candidate_result:
        status = DISCOVERY_STATUS_BLOCKED_NO_COMMON_KEYS
        remarks = "No common candidate/result key names were found; future adapter mapping is required."
    else:
        status = DISCOVERY_STATUS_READY_FOR_MATCHING_DRY_RUN_CONTRACT
        remarks = "Possible join keys discovered. Only future dry-run matching contract may proceed; labels remain blocked."

    return MatchKeyDiscoveryAudit(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=MATCH_KEY_DISCOVERY_CONTRACT_VERSION,
        accepted_for=MATCH_KEY_DISCOVERY_ACCEPTED_FOR,
        matching_rows_path=str(matching_rows_path) if matching_rows_path else None,
        nonzero_verification_report_path=str(nonzero_verification_report_path) if nonzero_verification_report_path else None,
        candidate_row_count=len(candidate_rows),
        features_row_count=artifact_counts.get("features_ref", 0),
        strategy_row_count=artifact_counts.get("strategy_ref", 0),
        risk_row_count=artifact_counts.get("risk_ref", 0),
        execution_shadow_row_count=artifact_counts.get("execution_shadow_ref", 0),
        candidate_keys=candidate_keys,
        features_keys=artifact_keys.get("features_ref", tuple()),
        strategy_keys=artifact_keys.get("strategy_ref", tuple()),
        risk_keys=artifact_keys.get("risk_ref", tuple()),
        execution_shadow_keys=artifact_keys.get("execution_shadow_ref", tuple()),
        common_candidate_result_keys=common_candidate_result,
        preferred_common_keys=preferred_common,
        result_artifact_common_keys=tuple(sorted(result_common)),
        discovery_status=status,
        remarks=remarks,
    )


def write_match_key_discovery_audit(
    optimization_id: str,
    output_dir: str | Path,
    *,
    matching_rows_path: str | Path | None,
    nonzero_verification_report_path: str | Path | None,
) -> MatchKeyDiscoveryBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit = build_match_key_discovery_audit(
        optimization_id,
        matching_rows_path=matching_rows_path,
        nonzero_verification_report_path=nonzero_verification_report_path,
    )

    audit_path = out / "25_match_key_discovery_audit.json"
    verdict_path = out / "09_optimizer_verdict.json"

    audit_path.write_text(json.dumps(asdict(audit), indent=2, sort_keys=True), encoding="utf-8")

    result_counts = [
        audit.features_row_count,
        audit.strategy_row_count,
        audit.risk_row_count,
        audit.execution_shadow_row_count,
    ]
    result_min = min(result_counts) if result_counts else 0

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": MATCH_KEY_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": MATCH_KEY_DISCOVERY_ACCEPTED_FOR,
        "discovery_status": audit.discovery_status,
        "candidate_row_count": audit.candidate_row_count,
        "result_min_row_count": result_min,
        "preferred_common_key_count": len(audit.preferred_common_keys),
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": audit.remarks,
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return MatchKeyDiscoveryBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=MATCH_KEY_DISCOVERY_CONTRACT_VERSION,
        accepted_for=MATCH_KEY_DISCOVERY_ACCEPTED_FOR,
        match_key_discovery_path=audit_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        discovery_status=audit.discovery_status,
        candidate_row_count=audit.candidate_row_count,
        result_min_row_count=result_min,
        preferred_common_key_count=len(audit.preferred_common_keys),
    )


__all__ = (
    "MATCH_KEY_DISCOVERY_CONTRACT_VERSION",
    "MATCH_KEY_DISCOVERY_ACCEPTED_FOR",
    "DISCOVERY_STATUS_BLOCKED_NO_MATCHING_ROWS",
    "DISCOVERY_STATUS_BLOCKED_NO_RESULT_ROWS",
    "DISCOVERY_STATUS_BLOCKED_NO_COMMON_KEYS",
    "DISCOVERY_STATUS_READY_FOR_MATCHING_DRY_RUN_CONTRACT",
    "RESULT_ARTIFACT_FIELDS",
    "PREFERRED_JOIN_KEYS",
    "MatchKeyDiscoveryAudit",
    "MatchKeyDiscoveryBuildResult",
    "build_match_key_discovery_audit",
    "write_match_key_discovery_audit",
)
