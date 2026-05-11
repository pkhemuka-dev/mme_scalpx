"""Lane D D19 nonzero result-pack verification audit.

This module verifies the selected D18 nonzero complete replay result pack at
read-only level before any future candidate-to-trade matching.

It does not execute replay, assemble packs, match candidates to trades, bind
labels, calculate PnL, train/predict models, call brokers, write live Redis,
mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .contracts import OUTPUT_ROOT

NONZERO_VERIFY_CONTRACT_VERSION = "replay_optimization_d19_nonzero_pack_verification_contract_v1"
NONZERO_VERIFY_ACCEPTED_FOR = "NONZERO_RESULT_PACK_VERIFICATION_AUDIT_ONLY"

NONZERO_VERIFY_STATUS_PASS_AUDIT_ONLY = "NONZERO_RESULT_PACK_VERIFY_PASS_AUDIT_ONLY"
NONZERO_VERIFY_STATUS_BLOCKED_NO_D18_REPORT = "BLOCKED_NO_D18_NONZERO_REPORT"
NONZERO_VERIFY_STATUS_BLOCKED_NO_SELECTED_PACK = "BLOCKED_NO_SELECTED_NONZERO_PACK"
NONZERO_VERIFY_STATUS_BLOCKED_REF_MISSING = "BLOCKED_SELECTED_PACK_REF_MISSING"
NONZERO_VERIFY_STATUS_BLOCKED_BAD_JSON = "BLOCKED_SELECTED_PACK_BAD_JSON"
NONZERO_VERIFY_STATUS_BLOCKED_NOT_EQUAL_POSITIVE = "BLOCKED_SELECTED_PACK_NOT_EQUAL_POSITIVE"
NONZERO_VERIFY_STATUS_BLOCKED_INTEGRITY_NOT_PASS = "BLOCKED_SELECTED_PACK_INTEGRITY_NOT_PASS"

CORE_REFS = (
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)

REQUIRED_REFS = (
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)


@dataclass(frozen=True, slots=True)
class NonzeroPackVerificationAudit:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    nonzero_discovery_report_path: str | None
    selected_pack_id: str | None
    selected_candidate_root: str | None
    manifest_ref: str | None
    integrity_ref: str | None
    features_ref: str | None
    strategy_ref: str | None
    risk_ref: str | None
    execution_shadow_ref: str | None
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
    min_row_count: int
    max_row_count: int
    equal_positive_rows: bool
    integrity_verdict: str | None
    verification_status: str
    candidate_trade_matching_allowed: bool = False
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
class NonzeroPackVerificationBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    nonzero_verification_report_path: str
    optimizer_verdict_path: str
    verification_status: str
    selected_pack_id: str | None
    selected_candidate_root: str | None
    candidate_trade_matching_allowed: bool = False
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
        raise ValueError(f"D19 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _exists(path_value: str | None) -> bool:
    return bool(path_value) and Path(str(path_value)).is_file()


def _json_ok(path_value: str | None) -> bool:
    return _safe_load_json(path_value) is not None


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


def build_nonzero_pack_verification_audit(
    optimization_id: str,
    *,
    nonzero_discovery_report_path: str | Path | None,
) -> NonzeroPackVerificationAudit:
    report = _safe_load_json(nonzero_discovery_report_path)

    if not isinstance(report, dict):
        return NonzeroPackVerificationAudit(
            optimization_id=optimization_id,
            created_at=_utc_now(),
            contract_version=NONZERO_VERIFY_CONTRACT_VERSION,
            accepted_for=NONZERO_VERIFY_ACCEPTED_FOR,
            nonzero_discovery_report_path=str(nonzero_discovery_report_path) if nonzero_discovery_report_path else None,
            selected_pack_id=None,
            selected_candidate_root=None,
            manifest_ref=None,
            integrity_ref=None,
            features_ref=None,
            strategy_ref=None,
            risk_ref=None,
            execution_shadow_ref=None,
            manifest_exists=False,
            integrity_exists=False,
            features_exists=False,
            strategy_exists=False,
            risk_exists=False,
            execution_shadow_exists=False,
            manifest_json_ok=False,
            integrity_json_ok=False,
            features_json_ok=False,
            strategy_json_ok=False,
            risk_json_ok=False,
            execution_shadow_json_ok=False,
            features_row_count=0,
            strategy_row_count=0,
            risk_row_count=0,
            execution_shadow_row_count=0,
            min_row_count=0,
            max_row_count=0,
            equal_positive_rows=False,
            integrity_verdict=None,
            verification_status=NONZERO_VERIFY_STATUS_BLOCKED_NO_D18_REPORT,
            remarks="D18 nonzero discovery report missing or invalid.",
        )

    selected = report.get("selected_pack")
    if not isinstance(selected, dict):
        return NonzeroPackVerificationAudit(
            optimization_id=optimization_id,
            created_at=_utc_now(),
            contract_version=NONZERO_VERIFY_CONTRACT_VERSION,
            accepted_for=NONZERO_VERIFY_ACCEPTED_FOR,
            nonzero_discovery_report_path=str(nonzero_discovery_report_path) if nonzero_discovery_report_path else None,
            selected_pack_id=None,
            selected_candidate_root=None,
            manifest_ref=None,
            integrity_ref=None,
            features_ref=None,
            strategy_ref=None,
            risk_ref=None,
            execution_shadow_ref=None,
            manifest_exists=False,
            integrity_exists=False,
            features_exists=False,
            strategy_exists=False,
            risk_exists=False,
            execution_shadow_exists=False,
            manifest_json_ok=False,
            integrity_json_ok=False,
            features_json_ok=False,
            strategy_json_ok=False,
            risk_json_ok=False,
            execution_shadow_json_ok=False,
            features_row_count=0,
            strategy_row_count=0,
            risk_row_count=0,
            execution_shadow_row_count=0,
            min_row_count=0,
            max_row_count=0,
            equal_positive_rows=False,
            integrity_verdict=None,
            verification_status=NONZERO_VERIFY_STATUS_BLOCKED_NO_SELECTED_PACK,
            remarks="D18 selected_pack missing.",
        )

    refs = {name: selected.get(name) for name in REQUIRED_REFS}
    exists = {name: _exists(refs[name]) for name in REQUIRED_REFS}
    json_ok = {name: _json_ok(refs[name]) for name in REQUIRED_REFS}

    payloads = {name: _safe_load_json(refs[name]) for name in REQUIRED_REFS}
    counts = {name: _row_count(payloads[name]) for name in CORE_REFS}
    count_values = list(counts.values())
    min_count = min(count_values) if count_values else 0
    max_count = max(count_values) if count_values else 0
    equal_positive = bool(count_values) and len(set(count_values)) == 1 and count_values[0] > 0

    integrity = _integrity_verdict(payloads["integrity_ref"])
    integrity_text = str(integrity).strip().lower() if integrity is not None else ""

    if not all(exists.values()):
        status = NONZERO_VERIFY_STATUS_BLOCKED_REF_MISSING
        remarks = "One or more selected-pack refs are missing."
    elif not all(json_ok.values()):
        status = NONZERO_VERIFY_STATUS_BLOCKED_BAD_JSON
        remarks = "One or more selected-pack refs are invalid JSON."
    elif not equal_positive:
        status = NONZERO_VERIFY_STATUS_BLOCKED_NOT_EQUAL_POSITIVE
        remarks = "Selected pack row counts are not equal positive."
    elif integrity_text not in {"pass", "ok", "safe", "true"}:
        status = NONZERO_VERIFY_STATUS_BLOCKED_INTEGRITY_NOT_PASS
        remarks = f"Selected pack integrity is not pass-like: {integrity!r}."
    else:
        status = NONZERO_VERIFY_STATUS_PASS_AUDIT_ONLY
        remarks = "Selected nonzero result pack verifies read-only. Candidate-trade matching may be contracted next; labels remain blocked."

    return NonzeroPackVerificationAudit(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=NONZERO_VERIFY_CONTRACT_VERSION,
        accepted_for=NONZERO_VERIFY_ACCEPTED_FOR,
        nonzero_discovery_report_path=str(nonzero_discovery_report_path) if nonzero_discovery_report_path else None,
        selected_pack_id=str(selected.get("pack_id") or "") or None,
        selected_candidate_root=str(selected.get("candidate_root") or "") or None,
        manifest_ref=str(refs["manifest_ref"] or "") or None,
        integrity_ref=str(refs["integrity_ref"] or "") or None,
        features_ref=str(refs["features_ref"] or "") or None,
        strategy_ref=str(refs["strategy_ref"] or "") or None,
        risk_ref=str(refs["risk_ref"] or "") or None,
        execution_shadow_ref=str(refs["execution_shadow_ref"] or "") or None,
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
        features_row_count=counts["features_ref"],
        strategy_row_count=counts["strategy_ref"],
        risk_row_count=counts["risk_ref"],
        execution_shadow_row_count=counts["execution_shadow_ref"],
        min_row_count=min_count,
        max_row_count=max_count,
        equal_positive_rows=equal_positive,
        integrity_verdict=integrity,
        verification_status=status,
        remarks=remarks,
    )


def write_nonzero_pack_verification(
    optimization_id: str,
    output_dir: str | Path,
    *,
    nonzero_discovery_report_path: str | Path | None,
) -> NonzeroPackVerificationBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audit = build_nonzero_pack_verification_audit(
        optimization_id,
        nonzero_discovery_report_path=nonzero_discovery_report_path,
    )

    report_path = out / "22_nonzero_result_pack_verification.json"
    verdict_path = out / "09_optimizer_verdict.json"

    report_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Nonzero Result Pack Verification Audit",
        "contract_version": NONZERO_VERIFY_CONTRACT_VERSION,
        "accepted_for": NONZERO_VERIFY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "verification_status": audit.verification_status,
        "audit": asdict(audit),
        "safety": {
            "candidate_trade_matching_allowed": False,
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
    report_path.write_text(json.dumps(report_payload, indent=2, sort_keys=True), encoding="utf-8")

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": NONZERO_VERIFY_CONTRACT_VERSION,
        "accepted_for": NONZERO_VERIFY_ACCEPTED_FOR,
        "verification_status": audit.verification_status,
        "selected_pack_id": audit.selected_pack_id,
        "selected_candidate_root": audit.selected_candidate_root,
        "candidate_trade_matching_allowed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": audit.remarks,
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return NonzeroPackVerificationBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=NONZERO_VERIFY_CONTRACT_VERSION,
        accepted_for=NONZERO_VERIFY_ACCEPTED_FOR,
        nonzero_verification_report_path=report_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        verification_status=audit.verification_status,
        selected_pack_id=audit.selected_pack_id,
        selected_candidate_root=audit.selected_candidate_root,
    )


__all__ = (
    "NONZERO_VERIFY_CONTRACT_VERSION",
    "NONZERO_VERIFY_ACCEPTED_FOR",
    "NONZERO_VERIFY_STATUS_PASS_AUDIT_ONLY",
    "NONZERO_VERIFY_STATUS_BLOCKED_NO_D18_REPORT",
    "NONZERO_VERIFY_STATUS_BLOCKED_NO_SELECTED_PACK",
    "NONZERO_VERIFY_STATUS_BLOCKED_REF_MISSING",
    "NONZERO_VERIFY_STATUS_BLOCKED_BAD_JSON",
    "NONZERO_VERIFY_STATUS_BLOCKED_NOT_EQUAL_POSITIVE",
    "NONZERO_VERIFY_STATUS_BLOCKED_INTEGRITY_NOT_PASS",
    "CORE_REFS",
    "REQUIRED_REFS",
    "NonzeroPackVerificationAudit",
    "NonzeroPackVerificationBuildResult",
    "build_nonzero_pack_verification_audit",
    "write_nonzero_pack_verification",
)
