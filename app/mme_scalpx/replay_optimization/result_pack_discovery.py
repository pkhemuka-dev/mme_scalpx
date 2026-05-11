"""Lane D D15 replay result-pack discovery audit.

This module scans the existing D3 replay index and discovers whether any replay
artifact root contains a complete replay result pack:

- manifest
- integrity report
- features rows
- strategy decisions
- risk outputs
- execution-shadow / execution results

It does not execute replay, assemble missing artifacts, bind labels, calculate
PnL, train/predict models, call brokers, write live Redis, mutate doctrine, or
approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

RESULT_PACK_DISCOVERY_CONTRACT_VERSION = "replay_optimization_d15_result_pack_discovery_contract_v1"
RESULT_PACK_DISCOVERY_ACCEPTED_FOR = "REPLAY_RESULT_PACK_DISCOVERY_AUDIT_ONLY"

DISCOVERY_STATUS_BLOCKED_NO_REPLAY_INDEX = "BLOCKED_NO_REPLAY_INDEX"
DISCOVERY_STATUS_BLOCKED_NO_ARTIFACTS = "BLOCKED_NO_REPLAY_ARTIFACTS"
DISCOVERY_STATUS_BLOCKED_NO_COMPLETE_PACK = "BLOCKED_NO_COMPLETE_REPLAY_RESULT_PACK"
DISCOVERY_STATUS_COMPLETE_PACK_FOUND_AUDIT_ONLY = "COMPLETE_REPLAY_RESULT_PACK_FOUND_AUDIT_ONLY"

PACK_REQUIRED_FIELDS = (
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)

PACK_CANDIDATE_COLUMNS = (
    "optimization_id",
    "pack_id",
    "candidate_root",
    "artifact_count",
    "complete",
    "missing_fields",
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
    "discovery_status",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)


@dataclass(frozen=True, slots=True)
class ReplayResultPackCandidate:
    optimization_id: str
    pack_id: str
    candidate_root: str
    artifact_count: int
    artifact_kinds: tuple[str, ...]
    complete: bool
    missing_fields: tuple[str, ...]
    manifest_ref: str | None = None
    integrity_ref: str | None = None
    features_ref: str | None = None
    strategy_ref: str | None = None
    risk_ref: str | None = None
    execution_shadow_ref: str | None = None
    discovery_status: str = DISCOVERY_STATUS_BLOCKED_NO_COMPLETE_PACK
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ResultPackDiscoveryBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    replay_index_path: str | None
    discovery_report_path: str
    pack_candidates_csv_path: str
    optimizer_verdict_path: str
    artifact_count: int
    pack_candidate_count: int
    complete_pack_count: int
    discovery_status: str
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
        raise ValueError(f"D15 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _field_for_artifact(kind: str, filename: str) -> str | None:
    if kind in {"manifest", "replay_manifest"} or filename in {"manifest.json", "replay_manifest.json", "00_manifest.json"}:
        return "manifest_ref"
    if kind == "integrity_report" or filename in {"03_integrity_report.json", "integrity_report.json"}:
        return "integrity_ref"
    if kind == "features_rows" or filename == "features_rows.json":
        return "features_ref"
    if kind == "strategy_decisions" or filename == "strategy_decisions.json":
        return "strategy_ref"
    if kind == "risk_outputs" or filename == "risk_outputs.json":
        return "risk_ref"
    if kind in {"execution_shadow_results", "execution_results"} or filename in {
        "execution_shadow_results.json",
        "execution_results.json",
    }:
        return "execution_shadow_ref"
    return None


def _candidate_roots_for_path(path_value: str) -> tuple[str, ...]:
    path = Path(path_value)
    parents = list(path.parents)
    roots: list[str] = []

    def add(candidate: Path) -> None:
        value = candidate.as_posix().rstrip("/")
        if not value:
            return
        if value in {"run", "run/replay"}:
            return
        if not (value == "run/replay" or value.startswith("run/replay/") or "/run/replay/" in "/" + value + "/"):
            return
        if value not in roots:
            roots.append(value)

    if path.parent:
        add(path.parent)

    if path.parent.name == "artifacts":
        add(path.parent.parent)

    parts = path.parts
    for marker in ("artifacts", "exports", "runs", "run"):
        if marker in parts:
            idx = parts.index(marker)
            if idx > 0:
                add(Path(*parts[:idx]))
            if idx + 1 < len(parts):
                add(Path(*parts[:idx + 1]))

    # Add a few parents so split artifact layouts can still be detected
    for parent in parents[:6]:
        add(parent)

    return tuple(roots)


def _artifact_list(replay_index_payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not replay_index_payload:
        return []
    artifacts = replay_index_payload.get("artifacts")
    if not isinstance(artifacts, list):
        return []
    return [row for row in artifacts if isinstance(row, dict)]


def discover_replay_result_packs(
    optimization_id: str,
    *,
    replay_index_path: str | Path | None,
) -> tuple[ReplayResultPackCandidate, ...]:
    payload = _safe_load_json(replay_index_path)
    artifacts = _artifact_list(payload)

    buckets: dict[str, dict[str, Any]] = {}

    for artifact in artifacts:
        path_value = artifact.get("path")
        if not isinstance(path_value, str) or not path_value:
            continue
        kind = str(artifact.get("artifact_kind") or "")
        filename = str(artifact.get("filename") or Path(path_value).name)
        field_name = _field_for_artifact(kind, filename)

        for root in _candidate_roots_for_path(path_value):
            bucket = buckets.setdefault(
                root,
                {
                    "candidate_root": root,
                    "artifact_count": 0,
                    "artifact_kinds": set(),
                    "manifest_ref": None,
                    "integrity_ref": None,
                    "features_ref": None,
                    "strategy_ref": None,
                    "risk_ref": None,
                    "execution_shadow_ref": None,
                },
            )
            bucket["artifact_count"] += 1
            if kind:
                bucket["artifact_kinds"].add(kind)
            if field_name and not bucket.get(field_name):
                bucket[field_name] = path_value

    rows: list[ReplayResultPackCandidate] = []
    for idx, (root, bucket) in enumerate(sorted(buckets.items()), start=1):
        missing = tuple(field for field in PACK_REQUIRED_FIELDS if not bucket.get(field))
        complete = not missing
        status = (
            DISCOVERY_STATUS_COMPLETE_PACK_FOUND_AUDIT_ONLY
            if complete
            else DISCOVERY_STATUS_BLOCKED_NO_COMPLETE_PACK
        )
        rows.append(
            ReplayResultPackCandidate(
                optimization_id=optimization_id,
                pack_id=f"RPACK_{idx:06d}",
                candidate_root=root,
                artifact_count=int(bucket["artifact_count"]),
                artifact_kinds=tuple(sorted(bucket["artifact_kinds"])),
                complete=complete,
                missing_fields=missing,
                manifest_ref=bucket.get("manifest_ref"),
                integrity_ref=bucket.get("integrity_ref"),
                features_ref=bucket.get("features_ref"),
                strategy_ref=bucket.get("strategy_ref"),
                risk_ref=bucket.get("risk_ref"),
                execution_shadow_ref=bucket.get("execution_shadow_ref"),
                discovery_status=status,
                label_binding_allowed=False,
                labels_bound=False,
                remarks="D15 discovery candidate only. No label binding or PnL calculation.",
            )
        )

    return tuple(
        sorted(
            rows,
            key=lambda row: (
                0 if row.complete else 1,
                -row.artifact_count,
                row.candidate_root,
            ),
        )
    )


def _write_csv(path: Path, columns: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_result_pack_discovery(
    optimization_id: str,
    output_dir: str | Path,
    *,
    replay_index_path: str | Path | None,
) -> ResultPackDiscoveryBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    replay_index = _safe_load_json(replay_index_path)
    artifacts = _artifact_list(replay_index)
    candidates = discover_replay_result_packs(
        optimization_id,
        replay_index_path=replay_index_path,
    )
    complete_count = sum(1 for row in candidates if row.complete)

    if not replay_index:
        status = DISCOVERY_STATUS_BLOCKED_NO_REPLAY_INDEX
    elif not artifacts:
        status = DISCOVERY_STATUS_BLOCKED_NO_ARTIFACTS
    elif complete_count <= 0:
        status = DISCOVERY_STATUS_BLOCKED_NO_COMPLETE_PACK
    else:
        status = DISCOVERY_STATUS_COMPLETE_PACK_FOUND_AUDIT_ONLY

    report_path = out / "18_replay_result_pack_discovery.json"
    csv_path = out / "18_replay_result_pack_candidates.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    candidate_dicts = [asdict(row) for row in candidates]
    report_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Result Pack Discovery Audit",
        "contract_version": RESULT_PACK_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": RESULT_PACK_DISCOVERY_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "replay_index_path": str(replay_index_path) if replay_index_path else None,
        "artifact_count": len(artifacts),
        "pack_candidate_count": len(candidates),
        "complete_pack_count": complete_count,
        "discovery_status": status,
        "top_pack_candidates": candidate_dicts[:50],
        "safety": {
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
    _write_csv(csv_path, PACK_CANDIDATE_COLUMNS, candidate_dicts)

    verdict_payload = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": RESULT_PACK_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": RESULT_PACK_DISCOVERY_ACCEPTED_FOR,
        "discovery_status": status,
        "complete_pack_count": complete_count,
        "implementation_allowed": False,
        "candidate_trade_matching_allowed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D15 discovers replay result packs only. It does not bind labels or calculate PnL.",
    }
    verdict_path.write_text(json.dumps(verdict_payload, indent=2, sort_keys=True), encoding="utf-8")

    return ResultPackDiscoveryBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=RESULT_PACK_DISCOVERY_CONTRACT_VERSION,
        accepted_for=RESULT_PACK_DISCOVERY_ACCEPTED_FOR,
        replay_index_path=str(replay_index_path) if replay_index_path else None,
        discovery_report_path=report_path.as_posix(),
        pack_candidates_csv_path=csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        artifact_count=len(artifacts),
        pack_candidate_count=len(candidates),
        complete_pack_count=complete_count,
        discovery_status=status,
    )


def result_pack_discovery_summary(*, replay_index_path: str | Path | None) -> dict[str, Any]:
    replay_index = _safe_load_json(replay_index_path)
    artifacts = _artifact_list(replay_index)
    candidates = discover_replay_result_packs(
        "D15_SUMMARY",
        replay_index_path=replay_index_path,
    )
    complete_count = sum(1 for row in candidates if row.complete)
    return {
        "contract_version": RESULT_PACK_DISCOVERY_CONTRACT_VERSION,
        "accepted_for": RESULT_PACK_DISCOVERY_ACCEPTED_FOR,
        "artifact_count": len(artifacts),
        "pack_candidate_count": len(candidates),
        "complete_pack_count": complete_count,
        "discovery_status": (
            DISCOVERY_STATUS_COMPLETE_PACK_FOUND_AUDIT_ONLY
            if complete_count > 0
            else DISCOVERY_STATUS_BLOCKED_NO_COMPLETE_PACK
        ),
        "label_binding_allowed": False,
        "labels_bound": False,
        "replay_execution_performed": False,
        "real_pnl_calculation_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "RESULT_PACK_DISCOVERY_CONTRACT_VERSION",
    "RESULT_PACK_DISCOVERY_ACCEPTED_FOR",
    "DISCOVERY_STATUS_BLOCKED_NO_REPLAY_INDEX",
    "DISCOVERY_STATUS_BLOCKED_NO_ARTIFACTS",
    "DISCOVERY_STATUS_BLOCKED_NO_COMPLETE_PACK",
    "DISCOVERY_STATUS_COMPLETE_PACK_FOUND_AUDIT_ONLY",
    "PACK_REQUIRED_FIELDS",
    "PACK_CANDIDATE_COLUMNS",
    "ReplayResultPackCandidate",
    "ResultPackDiscoveryBuildResult",
    "discover_replay_result_packs",
    "write_result_pack_discovery",
    "result_pack_discovery_summary",
)
