"""Lane D D13 grouped source-map repair contract.

This module repairs the D11 reference-only source map by grouping replay
artifacts by a single replay root before assigning source refs.

It does not bind labels, calculate PnL, execute replay, train/predict models,
call brokers, write live Redis, mutate strategy doctrine, or approve paper/live.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import OUTPUT_ROOT

SOURCE_MAP_GROUPING_CONTRACT_VERSION = "replay_optimization_d13_source_map_grouping_contract_v1"
SOURCE_MAP_GROUPING_ACCEPTED_FOR = "SOURCE_MAP_GROUPING_REPAIR_CONTRACT_ONLY"

GROUP_STATUS_COMPLETE_REFERENCE_ONLY = "GROUPED_COMPLETE_REFERENCE_ONLY_NO_LABEL_BINDING"
GROUP_STATUS_PARTIAL_REFERENCE_ONLY = "GROUPED_PARTIAL_REFERENCE_ONLY_NO_LABEL_BINDING"
GROUP_STATUS_BLOCKED_NO_REPLAY_GROUP = "BLOCKED_NO_REPLAY_GROUP"
GROUP_STATUS_BLOCKED_NO_BINDING_ROWS = "BLOCKED_NO_BINDING_ROWS"

GROUPED_SOURCE_MAP_COLUMNS = (
    "optimization_id",
    "grouped_source_map_id",
    "binding_id",
    "candidate_id",
    "ml_row_id",
    "feature_vector_ref",
    "selected_replay_root",
    "selected_group_complete",
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
    "source_map_status",
    "label_binding_allowed",
    "labels_bound",
    "remarks",
)

REQUIRED_GROUP_FIELDS = (
    "manifest_ref",
    "integrity_ref",
    "features_ref",
    "strategy_ref",
    "risk_ref",
    "execution_shadow_ref",
)


@dataclass(frozen=True, slots=True)
class ReplayArtifactGroup:
    replay_root: str
    artifact_count: int
    artifact_kinds: tuple[str, ...]
    manifest_ref: str | None = None
    integrity_ref: str | None = None
    features_ref: str | None = None
    strategy_ref: str | None = None
    risk_ref: str | None = None
    execution_shadow_ref: str | None = None
    complete: bool = False
    missing_fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class GroupedSourceMapRow:
    optimization_id: str
    grouped_source_map_id: str
    binding_id: str
    candidate_id: str
    ml_row_id: str
    feature_vector_ref: str
    selected_replay_root: str | None
    selected_group_complete: bool
    manifest_ref: str | None = None
    integrity_ref: str | None = None
    features_ref: str | None = None
    strategy_ref: str | None = None
    risk_ref: str | None = None
    execution_shadow_ref: str | None = None
    source_map_status: str = GROUP_STATUS_PARTIAL_REFERENCE_ONLY
    label_binding_allowed: bool = False
    labels_bound: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class SourceMapGroupingBuildResult:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    replay_index_path: str | None
    result_binding_rows_path: str | None
    grouping_report_path: str
    grouped_source_map_json_path: str
    grouped_source_map_csv_path: str
    optimizer_verdict_path: str
    replay_group_count: int
    complete_group_count: int
    grouped_source_map_row_count: int
    mixed_root_row_count: int
    source_map_status: str
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


def _rows_from_payload(payload: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not payload:
        return []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


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
        raise ValueError(f"D13 output must stay under {OUTPUT_ROOT}: {output_dir}")
    return out


def _root_signature(path_value: str) -> str:
    path = Path(path_value)
    parent = path.parent
    if parent.name == "artifacts":
        return parent.parent.as_posix()
    return parent.as_posix()


def _field_for_kind(kind: str, filename: str) -> str | None:
    if kind in {"manifest", "replay_manifest"} or filename in {"manifest.json", "replay_manifest.json"}:
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


def build_replay_artifact_groups(
    *,
    replay_index_path: str | Path | None,
) -> tuple[ReplayArtifactGroup, ...]:
    payload = _safe_load_json(replay_index_path)
    artifacts = payload.get("artifacts") if payload else None
    if not isinstance(artifacts, list):
        return tuple()

    grouped: dict[str, dict[str, Any]] = {}
    for item in artifacts:
        if not isinstance(item, dict):
            continue
        path_value = item.get("path")
        if not isinstance(path_value, str) or not path_value:
            continue

        root = _root_signature(path_value)
        kind = str(item.get("artifact_kind") or "")
        filename = str(item.get("filename") or Path(path_value).name)
        field_name = _field_for_kind(kind, filename)

        bucket = grouped.setdefault(
            root,
            {
                "replay_root": root,
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

    out: list[ReplayArtifactGroup] = []
    for root, bucket in grouped.items():
        missing = tuple(field for field in REQUIRED_GROUP_FIELDS if not bucket.get(field))
        out.append(
            ReplayArtifactGroup(
                replay_root=root,
                artifact_count=int(bucket["artifact_count"]),
                artifact_kinds=tuple(sorted(bucket["artifact_kinds"])),
                manifest_ref=bucket.get("manifest_ref"),
                integrity_ref=bucket.get("integrity_ref"),
                features_ref=bucket.get("features_ref"),
                strategy_ref=bucket.get("strategy_ref"),
                risk_ref=bucket.get("risk_ref"),
                execution_shadow_ref=bucket.get("execution_shadow_ref"),
                complete=not missing,
                missing_fields=missing,
            )
        )

    return tuple(
        sorted(
            out,
            key=lambda group: (
                0 if group.complete else 1,
                -group.artifact_count,
                group.replay_root,
            ),
        )
    )


def _select_group(groups: Sequence[ReplayArtifactGroup]) -> ReplayArtifactGroup | None:
    if not groups:
        return None
    complete = [group for group in groups if group.complete]
    if complete:
        return complete[0]
    return groups[0]


def build_grouped_source_map_rows(
    optimization_id: str,
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> tuple[GroupedSourceMapRow, ...]:
    groups = build_replay_artifact_groups(replay_index_path=replay_index_path)
    selected = _select_group(groups)

    binding_payload = _safe_load_json(result_binding_rows_path)
    binding_rows = _rows_from_payload(binding_payload)

    if not binding_rows:
        status = GROUP_STATUS_BLOCKED_NO_BINDING_ROWS
    elif not selected:
        status = GROUP_STATUS_BLOCKED_NO_REPLAY_GROUP
    elif selected.complete:
        status = GROUP_STATUS_COMPLETE_REFERENCE_ONLY
    else:
        status = GROUP_STATUS_PARTIAL_REFERENCE_ONLY

    rows: list[GroupedSourceMapRow] = []
    for i, row in enumerate(binding_rows[:max_rows], start=1):
        rows.append(
            GroupedSourceMapRow(
                optimization_id=optimization_id,
                grouped_source_map_id=f"GSMAP_{i:06d}",
                binding_id=str(row.get("binding_id") or f"BIND_UNKNOWN_{i:06d}"),
                candidate_id=str(row.get("candidate_id") or f"UNKNOWN_{i:06d}"),
                ml_row_id=str(row.get("ml_row_id") or ""),
                feature_vector_ref=str(row.get("feature_vector_ref") or ""),
                selected_replay_root=selected.replay_root if selected else None,
                selected_group_complete=bool(selected.complete) if selected else False,
                manifest_ref=selected.manifest_ref if selected else None,
                integrity_ref=selected.integrity_ref if selected else None,
                features_ref=selected.features_ref if selected else None,
                strategy_ref=selected.strategy_ref if selected else None,
                risk_ref=selected.risk_ref if selected else None,
                execution_shadow_ref=selected.execution_shadow_ref if selected else None,
                source_map_status=status,
                label_binding_allowed=False,
                labels_bound=False,
                remarks=(
                    "D13 grouped source map uses a single replay artifact root. "
                    "It remains reference-only; no candidate-to-trade matching or label binding."
                ),
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


def _mixed_root_count(rows: Sequence[GroupedSourceMapRow]) -> int:
    count = 0
    for row in rows:
        refs = [
            row.manifest_ref,
            row.integrity_ref,
            row.features_ref,
            row.strategy_ref,
            row.risk_ref,
            row.execution_shadow_ref,
        ]
        roots = {_root_signature(ref) for ref in refs if ref}
        if len(roots) > 1:
            count += 1
    return count


def write_grouped_source_map(
    optimization_id: str,
    output_dir: str | Path,
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
    max_rows: int = 10000,
) -> SourceMapGroupingBuildResult:
    out = _output_guard(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    groups = build_replay_artifact_groups(replay_index_path=replay_index_path)
    rows = build_grouped_source_map_rows(
        optimization_id,
        replay_index_path=replay_index_path,
        result_binding_rows_path=result_binding_rows_path,
        max_rows=max_rows,
    )
    row_dicts = [asdict(row) for row in rows]
    selected_status = rows[0].source_map_status if rows else GROUP_STATUS_BLOCKED_NO_BINDING_ROWS
    mixed_count = _mixed_root_count(rows)

    grouping_report_path = out / "16_source_map_grouping_report.json"
    grouped_json_path = out / "16_grouped_replay_result_source_map.json"
    grouped_csv_path = out / "16_grouped_replay_result_source_map.csv"
    verdict_path = out / "09_optimizer_verdict.json"

    grouping_report = {
        "schema_name": "MME-ScalpX Replay Optimization Source Map Grouping Report",
        "contract_version": SOURCE_MAP_GROUPING_CONTRACT_VERSION,
        "accepted_for": SOURCE_MAP_GROUPING_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "replay_index_path": str(replay_index_path) if replay_index_path else None,
        "result_binding_rows_path": str(result_binding_rows_path) if result_binding_rows_path else None,
        "replay_group_count": len(groups),
        "complete_group_count": sum(1 for group in groups if group.complete),
        "selected_group": asdict(_select_group(groups)) if _select_group(groups) else None,
        "groups": [asdict(group) for group in groups[:100]],
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
    grouping_report_path.write_text(json.dumps(grouping_report, indent=2, sort_keys=True), encoding="utf-8")

    grouped_payload = {
        "schema_name": "MME-ScalpX Replay Optimization Grouped Replay Result Source Map",
        "contract_version": SOURCE_MAP_GROUPING_CONTRACT_VERSION,
        "accepted_for": SOURCE_MAP_GROUPING_ACCEPTED_FOR,
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "source_map_row_count": len(rows),
        "source_map_status": selected_status,
        "mixed_root_row_count": mixed_count,
        "rows": row_dicts,
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
    grouped_json_path.write_text(json.dumps(grouped_payload, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(grouped_csv_path, GROUPED_SOURCE_MAP_COLUMNS, row_dicts)

    verdict = {
        "optimization_id": optimization_id,
        "created_at": _utc_now(),
        "contract_version": SOURCE_MAP_GROUPING_CONTRACT_VERSION,
        "accepted_for": SOURCE_MAP_GROUPING_ACCEPTED_FOR,
        "source_map_status": selected_status,
        "mixed_root_row_count": mixed_count,
        "label_binding_allowed": False,
        "labels_bound": False,
        "implementation_allowed": False,
        "model_training_allowed": False,
        "paper_live_approved": False,
        "production_claim_allowed": False,
        "remarks": "D13 repairs source-map grouping only. Label binding remains blocked.",
    }
    verdict_path.write_text(json.dumps(verdict, indent=2, sort_keys=True), encoding="utf-8")

    return SourceMapGroupingBuildResult(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=SOURCE_MAP_GROUPING_CONTRACT_VERSION,
        accepted_for=SOURCE_MAP_GROUPING_ACCEPTED_FOR,
        replay_index_path=str(replay_index_path) if replay_index_path else None,
        result_binding_rows_path=str(result_binding_rows_path) if result_binding_rows_path else None,
        grouping_report_path=grouping_report_path.as_posix(),
        grouped_source_map_json_path=grouped_json_path.as_posix(),
        grouped_source_map_csv_path=grouped_csv_path.as_posix(),
        optimizer_verdict_path=verdict_path.as_posix(),
        replay_group_count=len(groups),
        complete_group_count=sum(1 for group in groups if group.complete),
        grouped_source_map_row_count=len(rows),
        mixed_root_row_count=mixed_count,
        source_map_status=selected_status,
    )


def source_map_grouping_summary(
    *,
    replay_index_path: str | Path | None,
    result_binding_rows_path: str | Path | None,
) -> dict[str, Any]:
    groups = build_replay_artifact_groups(replay_index_path=replay_index_path)
    rows = build_grouped_source_map_rows(
        "D13_SUMMARY",
        replay_index_path=replay_index_path,
        result_binding_rows_path=result_binding_rows_path,
        max_rows=10000,
    )
    return {
        "contract_version": SOURCE_MAP_GROUPING_CONTRACT_VERSION,
        "accepted_for": SOURCE_MAP_GROUPING_ACCEPTED_FOR,
        "replay_group_count": len(groups),
        "complete_group_count": sum(1 for group in groups if group.complete),
        "grouped_source_map_row_count": len(rows),
        "mixed_root_row_count": _mixed_root_count(rows),
        "source_map_status": rows[0].source_map_status if rows else GROUP_STATUS_BLOCKED_NO_BINDING_ROWS,
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
    "SOURCE_MAP_GROUPING_CONTRACT_VERSION",
    "SOURCE_MAP_GROUPING_ACCEPTED_FOR",
    "GROUP_STATUS_COMPLETE_REFERENCE_ONLY",
    "GROUP_STATUS_PARTIAL_REFERENCE_ONLY",
    "GROUP_STATUS_BLOCKED_NO_REPLAY_GROUP",
    "GROUP_STATUS_BLOCKED_NO_BINDING_ROWS",
    "GROUPED_SOURCE_MAP_COLUMNS",
    "REQUIRED_GROUP_FIELDS",
    "ReplayArtifactGroup",
    "GroupedSourceMapRow",
    "SourceMapGroupingBuildResult",
    "build_replay_artifact_groups",
    "build_grouped_source_map_rows",
    "write_grouped_source_map",
    "source_map_grouping_summary",
)
