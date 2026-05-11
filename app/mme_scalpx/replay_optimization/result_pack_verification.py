"""Lane D D16 replay result-pack verification audit.

This module verifies discovered complete replay result packs at a shallow
read-only level: referenced files exist, JSON loads, row counts are coherent,
and integrity/manifest surfaces are present.

It does not execute replay, bind labels, calculate PnL, train/predict models,
call brokers, write live Redis, mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

RESULT_PACK_VERIFICATION_CONTRACT_VERSION = "replay_optimization_d16_result_pack_verification_contract_v1"
RESULT_PACK_VERIFICATION_ACCEPTED_FOR = "RESULT_PACK_VERIFICATION_AUDIT_ONLY"

VERIFY_STATUS_PASS_AUDIT_ONLY = "RESULT_PACK_VERIFY_PASS_AUDIT_ONLY"
VERIFY_STATUS_BLOCKED_NO_DISCOVERY = "BLOCKED_NO_DISCOVERY_REPORT"
VERIFY_STATUS_BLOCKED_NO_COMPLETE_PACK = "BLOCKED_NO_COMPLETE_PACK"
VERIFY_STATUS_BLOCKED_MISSING_REF_FILE = "BLOCKED_MISSING_REF_FILE"
VERIFY_STATUS_BLOCKED_BAD_JSON = "BLOCKED_BAD_JSON"
VERIFY_STATUS_BLOCKED_ROW_COUNT_MISMATCH = "BLOCKED_ROW_COUNT_MISMATCH"
VERIFY_STATUS_BLOCKED_INTEGRITY_NOT_PASS = "BLOCKED_INTEGRITY_NOT_PASS_OR_UNKNOWN"

REQUIRED_REFS = (
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)

ARTIFACT_ROW_REFS = (
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)


@dataclass(frozen=True, slots=True)
class VerifiedReplayResultPack:
    optimization_id: str
    pack_id: str
    candidate_root: str
    manifest_ref: str
    integrity_ref: str
    features_ref: str
    strategy_ref: str
    risk_ref: str
    execution_shadow_ref: str
    manifest_exists: bool
    integrity_exists: bool
    features_exists: bool
    strategy_exists: bool
    risk_exists: bool
    execution_shadow_exists: bool
    manifest_json_ok: bool
    integrity_json_ok: bool
    features_json_ok: bool
    strategy_json_ok: bool
    risk_json_ok: bool
    execution_shadow_json_ok: bool
    features_row_count: int
    strategy_row_count: int
    risk_row_count: int
    execution_shadow_row_count: int
    row_counts_match: bool
    integrity_verdict: str | None
    verification_status: str
    label_binding_allowed: bool = False
    labels_bound: bool = False
    replay_execution_performed: bool = False
    real_pnl_calculation_performed: bool = False
    model_training_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ResultPackVerificationBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    discovery_report_path: str | None
    verification_report_path: str
    optimizer_verdict_path: str
    verified_pack_count: int
    selected_pack_id: str | None
    selected_candidate_root: str | None
    verification_status: str
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


def _safe_load_json(path: str | Path | None) -> dict[str, Any] | list[Any] | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


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
        raise ValueError(f"D16 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _json_ok(path_value: str | None) -> bool:
    return _safe_load_json(path_value) is not None


def _exists(path_value: str | None) -> bool:
    return bool(path_value) and Path(str(path_value)).is_file()


def _row_count(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("rows", "items", "records", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
        return 1
    return 0


def _integrity_verdict(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("integrity_verdict", "verdict", "final_verdict", "status"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
    return None


def _discovery_pack_candidates(discovery_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not discovery_payload:
        return []
    rows = discovery_payload.get("top_pack_candidates")
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    rows = discovery_payload.get("pack_candidates")
    if isinstance(rows, list):
        return [row for row in rows if isinstance(row, dict)]
    return []


def _select_complete_pack(discovery_payload: Mapping[str, Any] | None) -> dict[str, Any] | None:
    candidates = _discovery_pack_candidates(discovery_payload)
    complete = [row for row in candidates if row.get("complete") is True]
    if not complete:
        return None

    def score(row: Mapping[str, Any]) -> tuple[int, int, str]:
        root = str(row.get("candidate_root") or "")
        # Prefer the most specific replay_locked root over broader parent dirs.
        specificity = root.count("/")
        artifact_count = int(row.get("artifact_count", 0)) if isinstance(row.get("artifact_count"), int) else 0
        return (specificity, artifact_count, root)

    return sorted(complete, key=score, reverse=True)[0]


def verify_selected_result_pack(
    optimization_id: str,
    *,
    discovery_report_path: str | Path | None,
) -> VerifiedReplayResultPack | None:
    discovery_payload = _safe_load_json(discovery_report_path)
    if not isinstance(discovery_payload, dict):
        return None

    pack = _select_complete_pack(discovery_payload)
    if not pack:
        return None

    refs = {name: pack.get(name) for name in REQUIRED_REFS}
    exists = {name: _exists(refs[name]) for name in REQUIRED_REFS}
    json_ok = {name: _json_ok(refs[name]) for name in REQUIRED_REFS}

    payloads = {name: _safe_load_json(refs[name]) for name in REQUIRED_REFS}
    row_counts = {name: _row_count(payloads[name]) for name in ARTIFACT_ROW_REFS}
    row_values = [row_counts[name] for name in ARTIFACT_ROW_REFS]
    nonzero_rows = [value for value in row_values if value > 0]
    row_counts_match = bool(nonzero_rows) and len(set(nonzero_rows)) == 1

    integrity_verdict = _integrity_verdict(payloads["integrity_ref"])

    if not all(exists.values()):
        status = VERIFY_STATUS_BLOCKED_MISSING_REF_FILE
        remarks = "One or more required refs do not exist."
    elif not all(json_ok.values()):
        status = VERIFY_STATUS_BLOCKED_BAD_JSON
        remarks = "One or more required refs are not valid JSON."
    elif not row_counts_match:
        status = VERIFY_STATUS_BLOCKED_ROW_COUNT_MISMATCH
        remarks = (
            "features/strategy/risk/execution-shadow row counts do not match. "
            "This is a blocking audit result, not a proof-script failure."
        )
    elif integrity_verdict and integrity_verdict.upper() not in {"PASS", "OK", "SAFE", "TRUE"}:
        status = VERIFY_STATUS_BLOCKED_INTEGRITY_NOT_PASS
        remarks = f"Integrity verdict is not pass-like: {integrity_verdict}"
    else:
        status = VERIFY_STATUS_PASS_AUDIT_ONLY
        remarks = "Selected replay result pack verifies at read-only audit level. Label binding remains blocked."

    return VerifiedReplayResultPack(
        optimization_id=optimization_id,
        pack_id=str(pack.get("pack_id") or "UNKNOWN_PACK"),
        candidate_root=str(pack.get("candidate_root") or ""),
        manifest_ref=str(refs["manifest_ref"] or ""),
        integrity_ref=str(refs["integrity_ref"] or ""),
        features_ref=str(refs["features_ref"] or ""),
        strategy_ref=str(refs["strategy_ref"] or ""),
        risk_ref=str(refs["risk_ref"] or ""),
        execution_shadow_ref=str(refs["execution_shadow_ref"] or ""),
        manifest_exists=exists["manifest_ref"],
        integrity_exists=exists["integrity_ref"],
        features_exists=exists["features_ref"],
        strategy_exists=exists["strategy_ref"],
        risk_exists=exists["risk_ref"],
        execution_shadow_exists=exists["execution_shadow_ref"],
        manifest_json_ok=json_ok["manifest_ref"],
        integrity_json_ok=json_ok["integrity_ref"],
        features_json_ok=json_ok["features_ref"],
        strategy_json_ok=json_ok["strategy_ref"],
        risk_json_ok=json_ok["risk_ref"],
        execution_shadow_json_ok=json_ok["execution_shadow_ref"],
        features_row_count=row_counts["features_ref"],
        strategy_row_count=row_counts["strategy_ref"],
        risk_row_count=row_counts["risk_ref"],
        execution_shadow_row_count=row_counts["execution_shadow_ref"],
        row_counts_match=row_counts_match,
        integrity_verdict=integrity_verdict,
        verification_status=status,
        remarks=remarks,
    )


def write_result_pack_verification(
    optimization_id: str,
    output_dir: str | Path,
    *,
    discovery_report_path: str | Path | None,
) -> ResultPackVerificationBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    discovery_payload = _safe_load_json(discovery_report_path)
    selected = verify_selected_result_pack(
        optimization_id,
        discovery_report_path=discovery_report_path,
    )

    if not isinstance(discovery_payload, dict):
        status = VERIFY_STATUS_BLOCKED_NO_DISCOVERY
    elif selected is None:
        status = VERIFY_STATUS_BLOCKED_NO_COMPLETE_PACK
    else:
        status = selected.verification_status

    report_path = out / "19_result_pack_verification_report.json"
    verdict_path = out / "09_optimizer_verdict.json"

    report_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Result Pack Verification Audit",
        "contract_version": RESULT_PACK_VERIFICATION_CONTRACT_VERSION,
        "accepted_for": RESULT_PACK_VERIFICATION_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "discovery_report_path": str(discovery_report_path) if discovery_report_path else None,
        "verification_status": status,
        "verified_pack_count": 1 if selected else 0,
        "selected_pack": asdict(selected) if selected else None,
        "safety": {
            "label_binding_allowed": False,
            "labels_bound": False,
            "candidate_trade_matching_allowed": False,
            "replay_execution_performed": False,
            "real_pnl_calculation_performed": False,
            "model_training_performed": False,
            "model_prediction_performed": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False
        },
    }
    report_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")

    verdict_payload = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": RESULT_PACK_VERIFICATION_CONTRACT_VERSION,
        "accepted_for": RESULT_PACK_VERIFICATION_ACCEPTED_FOR,
        "verification_status": status,
        "implementation_allowed": False,
        "candidate_trade_matching_allowed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D16 verifies one complete replay result pack only. It does not bind labels or calculate PnL.",
    }
    verdict_path.write_text(json.dumps(verdict_payload, indent=2, sort_keys=True), encoding="utf-8")

    return ResultPackVerificationBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=RESULT_PACK_VERIFICATION_CONTRACT_VERSION,
        accepted_for=RESULT_PACK_VERIFICATION_ACCEPTED_FOR,
        discovery_report_path=str(discovery_report_path) if discovery_report_path else None,
        verification_report_path=report_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        verified_pack_count=1 if selected else 0,
        selected_pack_id=selected.pack_id if selected else None,
        selected_candidate_root=selected.candidate_root if selected else None,
        verification_status=status,
    )


__all__ = (
    "RESULT_PACK_VERIFICATION_CONTRACT_VERSION",
    "RESULT_PACK_VERIFICATION_ACCEPTED_FOR",
    "VERIFY_STATUS_PASS_AUDIT_ONLY",
    "VERIFY_STATUS_BLOCKED_NO_DISCOVERY",
    "VERIFY_STATUS_BLOCKED_NO_COMPLETE_PACK",
    "VERIFY_STATUS_BLOCKED_MISSING_REF_FILE",
    "VERIFY_STATUS_BLOCKED_BAD_JSON",
    "VERIFY_STATUS_BLOCKED_ROW_COUNT_MISMATCH",
    "VERIFY_STATUS_BLOCKED_INTEGRITY_NOT_PASS",
    "REQUIRED_REFS",
    "ARTIFACT_ROW_REFS",
    "VerifiedReplayResultPack",
    "ResultPackVerificationBuildResult",
    "verify_selected_result_pack",
    "write_result_pack_verification",
)
