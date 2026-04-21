"""
app/mme_scalpx/replay/artifacts.py

Freeze-grade artifact persistence layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Artifact responsibilities
-------------------------
This module owns:
- canonical replay run directory creation
- stable JSON artifact writing
- stable CSV artifact writing
- manifest persistence
- persistence of dataset / selection / topology / engine summaries
- replay artifact existence helpers

This module does not own:
- replay execution
- dataset discovery/loading logic
- selection policy
- topology truth
- metric computation
- report interpretation
- doctrine logic
- live runtime mutation

Design rules
------------
- artifact persistence must be deterministic and auditable
- file writes must be explicit and path-safe
- JSON output must be stable and machine-readable first
- CSV output must have stable column ordering
- this layer must consume canonical contracts from runner/engine/selectors/topology
- no hidden directory creation outside the planned artifact root
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import manifest_to_dict
from .dataset import dataset_summary_to_dict
from .engine import engine_result_to_dict
from .runner import (
    ReplayArtifactPlan,
    ReplayRunContext,
    build_effective_inputs_snapshot,
    build_flattened_override_payload,
    effective_inputs_snapshot_to_dict,
    flattened_override_payload_to_dict,
)
from .selectors import ReplaySelectionPlan, selection_plan_to_dict
from .topology import ReplayTopologyPlan, topology_plan_to_dict


class ReplayArtifactsError(RuntimeError):
    """Base exception for replay artifact persistence failures."""


class ReplayArtifactsValidationError(ReplayArtifactsError):
    """Raised when artifact inputs or paths are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayArtifactWriteResult:
    """
    Canonical result for one artifact write.
    """

    path: str
    bytes_written: int


@dataclass(frozen=True, slots=True)
class ReplayArtifactBundleResult:
    """
    Canonical result summary for a bundle write.
    """

    root_dir: str
    written_paths: tuple[str, ...]

    @property
    def artifact_count(self) -> int:
        return len(self.written_paths)


class ReplayArtifactsWriter:
    """
    Freeze-grade replay artifact writer.
    """

    def ensure_directories(self, artifact_plan: ReplayArtifactPlan) -> None:
        _validate_artifact_plan(artifact_plan)
        Path(artifact_plan.root_dir).mkdir(parents=True, exist_ok=True)
        Path(artifact_plan.log_dir).mkdir(parents=True, exist_ok=True)
        Path(artifact_plan.artifacts_dir).mkdir(parents=True, exist_ok=True)

    def write_json_artifact(
        self,
        path: str | Path,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        file_path = _normalize_file_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        text = _stable_json_dumps(payload) + "\n"
        file_path.write_text(text, encoding="utf-8")

        return ReplayArtifactWriteResult(
            path=str(file_path),
            bytes_written=len(text.encode("utf-8")),
        )

    def write_csv_artifact(
        self,
        path: str | Path,
        rows: Sequence[Mapping[str, Any]],
        *,
        fieldnames: Sequence[str] | None = None,
    ) -> ReplayArtifactWriteResult:
        file_path = _normalize_file_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        normalized_rows = [dict(row) for row in rows]
        resolved_fieldnames = tuple(
            fieldnames if fieldnames is not None else _derive_csv_fieldnames(normalized_rows)
        )

        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=resolved_fieldnames,
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in normalized_rows:
                writer.writerow(
                    {name: _csv_safe_value(row.get(name)) for name in resolved_fieldnames}
                )

        return ReplayArtifactWriteResult(
            path=str(file_path),
            bytes_written=file_path.stat().st_size,
        )

    def write_manifest(
        self,
        run_context: ReplayRunContext,
    ) -> ReplayArtifactWriteResult:
        payload = manifest_to_dict(run_context.manifest)
        return self.write_json_artifact(run_context.artifact_plan.manifest_path, payload)

    def write_dataset_summary(
        self,
        selection_plan: ReplaySelectionPlan,
        artifact_plan: ReplayArtifactPlan,
    ) -> ReplayArtifactWriteResult:
        payload = dataset_summary_to_dict(selection_plan.dataset_summary)
        return self.write_json_artifact(artifact_plan.dataset_summary_path, payload)

    def write_scope_profile(
        self,
        selection_plan: ReplaySelectionPlan,
        topology_plan: ReplayTopologyPlan,
        artifact_plan: ReplayArtifactPlan,
    ) -> ReplayArtifactWriteResult:
        payload = {
            "selection_plan": selection_plan_to_dict(selection_plan),
            "topology_plan": topology_plan_to_dict(topology_plan),
        }
        return self.write_json_artifact(artifact_plan.scope_profile_path, payload)

    def write_integrity_report_placeholder(
        self,
        artifact_plan: ReplayArtifactPlan,
        *,
        verdict: str | None = None,
        checks: Sequence[Mapping[str, Any]] = (),
        notes: Sequence[str] = (),
    ) -> ReplayArtifactWriteResult:
        payload = {
            "verdict": verdict,
            "checks": [dict(item) for item in checks],
            "notes": list(notes),
        }
        return self.write_json_artifact(artifact_plan.integrity_report_path, payload)

    def write_metrics_summary_placeholder(
        self,
        artifact_plan: ReplayArtifactPlan,
        *,
        metrics: Mapping[str, Any] = {},
        notes: Sequence[str] = (),
    ) -> ReplayArtifactWriteResult:
        payload = {
            "metrics": dict(metrics),
            "notes": list(notes),
        }
        return self.write_json_artifact(artifact_plan.metrics_summary_path, payload)

    def write_effective_inputs(
        self,
        run_context: ReplayRunContext,
    ) -> ReplayArtifactWriteResult:
        snapshot = build_effective_inputs_snapshot(run_context)
        payload = effective_inputs_snapshot_to_dict(snapshot)
        return self.write_json_artifact(
            run_context.artifact_plan.effective_inputs_path,
            payload,
        )

    def write_effective_overrides_flat(
        self,
        run_context: ReplayRunContext,
    ) -> ReplayArtifactWriteResult:
        payload = build_flattened_override_payload(run_context)
        return self.write_json_artifact(
            run_context.artifact_plan.effective_overrides_flat_path,
            flattened_override_payload_to_dict(payload),
        )

    def write_engine_result(
        self,
        engine_result,
        artifact_plan: ReplayArtifactPlan,
    ) -> ReplayArtifactWriteResult:
        payload = engine_result_to_dict(engine_result)
        engine_result_path = Path(artifact_plan.artifacts_dir) / "engine_result.json"
        return self.write_json_artifact(engine_result_path, payload)

    def write_trade_log_csv(
        self,
        artifact_plan: ReplayArtifactPlan,
        rows: Sequence[Mapping[str, Any]],
        *,
        fieldnames: Sequence[str] | None = None,
    ) -> ReplayArtifactWriteResult:
        return self.write_csv_artifact(
            artifact_plan.trade_log_path,
            rows,
            fieldnames=fieldnames,
        )

    def write_candidate_audit_csv(
        self,
        artifact_plan: ReplayArtifactPlan,
        rows: Sequence[Mapping[str, Any]],
        *,
        fieldnames: Sequence[str] | None = None,
    ) -> ReplayArtifactWriteResult:
        return self.write_csv_artifact(
            artifact_plan.candidate_audit_path,
            rows,
            fieldnames=fieldnames,
        )

    def write_blocker_breakdown(
        self,
        artifact_plan: ReplayArtifactPlan,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        return self.write_json_artifact(artifact_plan.blocker_breakdown_path, payload)

    def write_exit_breakdown(
        self,
        artifact_plan: ReplayArtifactPlan,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        return self.write_json_artifact(artifact_plan.exit_breakdown_path, payload)

    def write_differential_report(
        self,
        artifact_plan: ReplayArtifactPlan,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        return self.write_json_artifact(artifact_plan.differential_report_path, payload)

    def write_core_artifact_bundle(
        self,
        run_context: ReplayRunContext,
        topology_plan: ReplayTopologyPlan,
        *,
        integrity_verdict: str | None = None,
        integrity_checks: Sequence[Mapping[str, Any]] = (),
        integrity_notes: Sequence[str] = (),
        metrics: Mapping[str, Any] = {},
        metrics_notes: Sequence[str] = (),
    ) -> ReplayArtifactBundleResult:
        artifact_plan = run_context.artifact_plan
        self.ensure_directories(artifact_plan)

        written: list[str] = []

        written.append(self.write_manifest(run_context).path)
        written.append(
            self.write_dataset_summary(run_context.selection_plan, artifact_plan).path
        )
        written.append(
            self.write_scope_profile(
                run_context.selection_plan,
                topology_plan,
                artifact_plan,
            ).path
        )
        written.append(
            self.write_integrity_report_placeholder(
                artifact_plan,
                verdict=integrity_verdict,
                checks=integrity_checks,
                notes=integrity_notes,
            ).path
        )
        written.append(
            self.write_metrics_summary_placeholder(
                artifact_plan,
                metrics=metrics,
                notes=metrics_notes,
            ).path
        )
        written.append(self.write_effective_inputs(run_context).path)
        written.append(self.write_effective_overrides_flat(run_context).path)

        return ReplayArtifactBundleResult(
            root_dir=artifact_plan.root_dir,
            written_paths=tuple(written),
        )


def ensure_artifact_directories(artifact_plan: ReplayArtifactPlan) -> None:
    writer = ReplayArtifactsWriter()
    writer.ensure_directories(artifact_plan)


def artifact_exists(path: str | Path) -> bool:
    return _normalize_file_path(path).exists()


def read_json_artifact(path: str | Path) -> dict[str, Any]:
    file_path = _normalize_file_path(path)
    if not file_path.exists():
        raise ReplayArtifactsValidationError(f"artifact not found: {file_path}")
    if not file_path.is_file():
        raise ReplayArtifactsValidationError(f"artifact path is not a file: {file_path}")

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReplayArtifactsValidationError(
            f"artifact is not valid JSON: {file_path}"
        ) from exc

    if not isinstance(payload, dict):
        raise ReplayArtifactsValidationError(
            f"JSON artifact must decode to object: {file_path}"
        )

    return payload


def _validate_artifact_plan(artifact_plan: ReplayArtifactPlan) -> None:
    required = (
        artifact_plan.root_dir,
        artifact_plan.manifest_path,
        artifact_plan.log_dir,
        artifact_plan.artifacts_dir,
        artifact_plan.dataset_summary_path,
        artifact_plan.scope_profile_path,
        artifact_plan.integrity_report_path,
        artifact_plan.metrics_summary_path,
        artifact_plan.effective_inputs_path,
        artifact_plan.effective_overrides_flat_path,
    )
    for value in required:
        if not isinstance(value, str) or not value.strip():
            raise ReplayArtifactsValidationError(
                f"artifact plan contains invalid path value: {value!r}"
            )


def _normalize_file_path(path: str | Path) -> Path:
    file_path = Path(path).expanduser()
    if not file_path.name:
        raise ReplayArtifactsValidationError(f"invalid file path: {path!r}")
    return file_path


def _stable_json_dumps(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def _derive_csv_fieldnames(rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    if not rows:
        return tuple()
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            key_str = str(key)
            if key_str not in seen:
                seen.add(key_str)
                keys.append(key_str)
    return tuple(keys)


def _csv_safe_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


__all__ = [
    "ReplayArtifactsError",
    "ReplayArtifactsValidationError",
    "ReplayArtifactWriteResult",
    "ReplayArtifactBundleResult",
    "ReplayArtifactsWriter",
    "ensure_artifact_directories",
    "artifact_exists",
    "read_json_artifact",
]
