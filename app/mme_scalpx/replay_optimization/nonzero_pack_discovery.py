"""Lane D D18 nonzero replay result-pack discovery audit.

This module scans replay result-pack candidates and identifies whether any
complete pack has positive row counts in features/strategy/risk/execution-shadow.

It does not execute replay, assemble packs, match candidates to trades, bind
labels, calculate PnL, train/predict models, call brokers, write live Redis,
mutate doctrine, or approve paper/live.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import OUTPUT_ROOT
from .result_pack_discovery import discover_replay_result_packs

NONZERO_PACK_DISCOVERY_CONTRACT_VERSION = "replay_optimization_d18_nonzero_pack_discovery_contract_v1"
NONZERO_PACK_DISCOVERY_ACCEPTED_FOR = "NONZERO_RESULT_PACK_DISCOVERY_AUDIT_ONLY"

NONZERO_STATUS_FOUND_AUDIT_ONLY = "NONZERO_COMPLETE_RESULT_PACK_FOUND_AUDIT_ONLY"
NONZERO_STATUS_BLOCKED_NO_REPLAY_INDEX = "BLOCKED_NO_REPLAY_INDEX"
NONZERO_STATUS_BLOCKED_NO_COMPLETE_PACK = "BLOCKED_NO_COMPLETE_PACK"
NONZERO_STATUS_BLOCKED_ONLY_ZERO_PACKS = "BLOCKED_ONLY_ZERO_RESULT_PACKS"
NONZERO_STATUS_BLOCKED_BAD_JSON = "BLOCKED_BAD_JSON_IN_CANDIDATE_PACK"

CORE_REFS = (
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)


@dataclass(frozen=True, slots=True)
class NonzeroPackCandidateAudit:
    optimization_id: str
    pack_id: str
    candidate_root: str
    complete: bool
    manifest_ref: str | None
    integrity_ref: str | None
    features_ref: str | None
    strategy_ref: str | None
    risk_ref: str | None
    execution_shadow_ref: str | None
    features_row_count: int
    strategy_row_count: int
    risk_row_count: int
    execution_shadow_row_count: int
    min_row_count: int
    max_row_count: int
    all_zero_rows: bool
    all_positive_rows: bool
    equal_positive_rows: bool
    integrity_verdict: str | None
    candidate_status: str
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
class NonzeroPackDiscoveryBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    replay_index_path: str | None
    nonzero_discovery_report_path: str
    optimizer_verdict_path: str
    complete_pack_count: int
    audited_pack_count: int
    nonzero_pack_count: int
    equal_positive_pack_count: int
    zero_pack_count: int
    discovery_status: str
    selected_pack_id: str | None = None
    selected_candidate_root: str | None = None
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


def _safe_load_json_any(path_value: str | None) -> Any:
    if not path_value:
        return None
    p = Path(path_value)
    if not p.exists() or not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


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
        raise ValueError(f"D18 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def audit_nonzero_pack_candidates(
    optimization_id: str,
    *,
    replay_index_path: str | Path | None,
) -> tuple[NonzeroPackCandidateAudit, ...]:
    packs = discover_replay_result_packs(
        optimization_id,
        replay_index_path=replay_index_path,
    )

    audits: list[NonzeroPackCandidateAudit] = []
    for pack in packs:
        if not pack.complete:
            continue

        payloads = {
            "features_ref": _safe_load_json_any(pack.features_ref),
            "strategy_ref": _safe_load_json_any(pack.strategy_ref),
            "risk_ref": _safe_load_json_any(pack.risk_ref),
            "execution_shadow_ref": _safe_load_json_any(pack.execution_shadow_ref),
        }
        counts = {key: _row_count(payload) for key, payload in payloads.items()}
        values = list(counts.values())
        min_count = min(values) if values else 0
        max_count = max(values) if values else 0
        all_zero = all(value == 0 for value in values)
        all_positive = all(value > 0 for value in values)
        equal_positive = all_positive and len(set(values)) == 1

        integrity_payload = _safe_load_json_any(pack.integrity_ref)
        integrity = _integrity_verdict(integrity_payload)

        if any(payload is None for payload in payloads.values()):
            status = NONZERO_STATUS_BLOCKED_BAD_JSON
            remarks = "One or more row artifacts are missing or invalid JSON."
        elif equal_positive:
            status = NONZERO_STATUS_FOUND_AUDIT_ONLY
            remarks = "Complete result pack has equal positive row counts. Still audit-only; no label binding."
        elif all_zero:
            status = NONZERO_STATUS_BLOCKED_ONLY_ZERO_PACKS
            remarks = "Complete result pack is all-zero and cannot produce labels."
        elif all_positive:
            status = NONZERO_STATUS_FOUND_AUDIT_ONLY
            remarks = "Complete result pack has positive rows but unequal counts; future normalization required."
        else:
            status = NONZERO_STATUS_BLOCKED_ONLY_ZERO_PACKS
            remarks = "Complete result pack does not have usable positive rows."

        audits.append(
            NonzeroPackCandidateAudit(
                optimization_id=optimization_id,
                pack_id=pack.pack_id,
                candidate_root=pack.candidate_root,
                complete=pack.complete,
                manifest_ref=pack.manifest_ref,
                integrity_ref=pack.integrity_ref,
                features_ref=pack.features_ref,
                strategy_ref=pack.strategy_ref,
                risk_ref=pack.risk_ref,
                execution_shadow_ref=pack.execution_shadow_ref,
                features_row_count=counts["features_ref"],
                strategy_row_count=counts["strategy_ref"],
                risk_row_count=counts["risk_ref"],
                execution_shadow_row_count=counts["execution_shadow_ref"],
                min_row_count=min_count,
                max_row_count=max_count,
                all_zero_rows=all_zero,
                all_positive_rows=all_positive,
                equal_positive_rows=equal_positive,
                integrity_verdict=integrity,
                candidate_status=status,
                remarks=remarks,
            )
        )

    return tuple(
        sorted(
            audits,
            key=lambda row: (
                0 if row.equal_positive_rows else 1,
                0 if row.all_positive_rows else 1,
                -row.min_row_count,
                row.candidate_root,
            ),
        )
    )


def write_nonzero_pack_discovery(
    optimization_id: str,
    output_dir: str | Path,
    *,
    replay_index_path: str | Path | None,
) -> NonzeroPackDiscoveryBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    audits = audit_nonzero_pack_candidates(
        optimization_id,
        replay_index_path=replay_index_path,
    )

    complete_count = len(audits)
    nonzero = [row for row in audits if row.all_positive_rows]
    equal_positive = [row for row in audits if row.equal_positive_rows]
    zero = [row for row in audits if row.all_zero_rows]

    if not replay_index_path:
        status = NONZERO_STATUS_BLOCKED_NO_REPLAY_INDEX
    elif complete_count <= 0:
        status = NONZERO_STATUS_BLOCKED_NO_COMPLETE_PACK
    elif nonzero:
        status = NONZERO_STATUS_FOUND_AUDIT_ONLY
    else:
        status = NONZERO_STATUS_BLOCKED_ONLY_ZERO_PACKS

    selected = equal_positive[0] if equal_positive else (nonzero[0] if nonzero else None)

    report_path = out / "21_nonzero_result_pack_discovery.json"
    verdict_path = out / "09_optimizer_verdict.json"

    report = {
        "schema_name": "MME-ScalpX Replay Optimization Nonzero Result Pack Discovery Audit",
        "contract_version": NONZERO_PACK_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": NONZERO_PACK_DISCOVERY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "replay_index_path": str(replay_index_path) if replay_index_path else None,
        "complete_pack_count": complete_count,
        "audited_pack_count": len(audits),
        "nonzero_pack_count": len(nonzero),
        "equal_positive_pack_count": len(equal_positive),
        "zero_pack_count": len(zero),
        "discovery_status": status,
        "selected_pack": asdict(selected) if selected else None,
        "pack_audits": [asdict(row) for row in audits[:100]],
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
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": NONZERO_PACK_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": NONZERO_PACK_DISCOVERY_ACCEPTED_FOR,
        "discovery_status": status,
        "selected_pack_id": selected.pack_id if selected else None,
        "selected_candidate_root": selected.candidate_root if selected else None,
        "nonzero_pack_count": len(nonzero),
        "equal_positive_pack_count": len(equal_positive),
        "label_binding_allowed": False,
        "labels_bound": False,
        "candidate_trade_matching_allowed": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D18 discovers nonzero packs only. No label binding or PnL calculation.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return NonzeroPackDiscoveryBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=NONZERO_PACK_DISCOVERY_CONTRACT_VERSION,
        accepted_for=NONZERO_PACK_DISCOVERY_ACCEPTED_FOR,
        replay_index_path=str(replay_index_path) if replay_index_path else None,
        nonzero_discovery_report_path=report_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        complete_pack_count=complete_count,
        audited_pack_count=len(audits),
        nonzero_pack_count=len(nonzero),
        equal_positive_pack_count=len(equal_positive),
        zero_pack_count=len(zero),
        discovery_status=status,
        selected_pack_id=selected.pack_id if selected else None,
        selected_candidate_root=selected.candidate_root if selected else None,
    )


__all__ = (
    "NONZERO_PACK_DISCOVERY_CONTRACT_VERSION",
    "NONZERO_PACK_DISCOVERY_ACCEPTED_FOR",
    "NONZERO_STATUS_FOUND_AUDIT_ONLY",
    "NONZERO_STATUS_BLOCKED_NO_REPLAY_INDEX",
    "NONZERO_STATUS_BLOCKED_NO_COMPLETE_PACK",
    "NONZERO_STATUS_BLOCKED_ONLY_ZERO_PACKS",
    "NONZERO_STATUS_BLOCKED_BAD_JSON",
    "CORE_REFS",
    "NonzeroPackCandidateAudit",
    "NonzeroPackDiscoveryBuildResult",
    "audit_nonzero_pack_candidates",
    "write_nonzero_pack_discovery",
)
