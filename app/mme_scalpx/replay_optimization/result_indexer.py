"""Lane D D3 read-only replay result indexer.

This module reads verified/offline replay artifact directories and produces
Lane D index artifacts under run/replay_optimization.

It must not execute replay, train ML, call brokers, write live Redis, start
runtime services, mutate strategy doctrine, or mutate replay engine code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .contracts import (
    OUTPUT_ROOT,
    ReplayResultRefRow,
    VERDICT_NOT_READY_REPLAY_SOURCE_MISSING,
    VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
)

REPLAY_RESULT_INDEXER_CONTRACT_VERSION = "replay_optimization_d3_replay_result_indexer_contract_v1"
REPLAY_RESULT_INDEXER_ACCEPTED_FOR = "READ_ONLY_INDEX_CONTRACT"

DEFAULT_REPLAY_INPUT_ROOTS = ("run/replay",)

KNOWN_REPLAY_ARTIFACT_NAMES = {
    "features_rows.json": "features_rows",
    "strategy_decisions.json": "strategy_decisions",
    "risk_outputs.json": "risk_outputs",
    "execution_shadow_results.json": "execution_shadow_results",
    "execution_results.json": "execution_results",
    "result_summary.json": "result_summary",
    "replay_manifest.json": "replay_manifest",
    "manifest.json": "manifest",
    "03_integrity_report.json": "integrity_report",
    "integrity_report.json": "integrity_report",
}

MAX_JSON_FILE_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class ReplayArtifactRef:
    path: str
    source_root: str
    artifact_kind: str
    filename: str
    suffix: str
    size_bytes: int
    sha256: str
    row_count: int | None = None
    top_level_keys: tuple[str, ...] = field(default_factory=tuple)
    integrity_verdict: str | None = None
    source_file: str | None = None
    source_stem: str | None = None
    source_verified: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class ReplayInputIndex:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    input_roots: tuple[str, ...]
    artifact_count: int
    artifact_kinds: tuple[str, ...]
    artifacts: tuple[ReplayArtifactRef, ...]
    optimizer_verdict: str
    replay_execution_performed: bool = False
    ml_training_performed: bool = False
    broker_calls_executed: bool = False
    live_redis_writes_executed: bool = False
    paper_or_live_enabled: bool = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_read_json(path: Path) -> Any | None:
    try:
        if path.stat().st_size > MAX_JSON_FILE_BYTES:
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _row_count(payload: Any) -> int | None:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("rows", "items", "records", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
        return 1
    return None


def _top_level_keys(payload: Any) -> tuple[str, ...]:
    if isinstance(payload, dict):
        return tuple(sorted(str(k) for k in payload.keys())[:100])
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        keys: set[str] = set()
        for row in payload[:25]:
            if isinstance(row, dict):
                keys.update(str(k) for k in row.keys())
        return tuple(sorted(keys)[:100])
    return tuple()


def _first_source_meta(payload: Any) -> tuple[str | None, str | None]:
    if isinstance(payload, dict):
        source_file = payload.get("source_file")
        source_stem = payload.get("source_stem")
        if isinstance(source_file, str) or isinstance(source_stem, str):
            return source_file, source_stem
        for key in ("rows", "items", "records", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list) and value and isinstance(value[0], dict):
                return (
                    value[0].get("source_file") if isinstance(value[0].get("source_file"), str) else None,
                    value[0].get("source_stem") if isinstance(value[0].get("source_stem"), str) else None,
                )
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return (
            payload[0].get("source_file") if isinstance(payload[0].get("source_file"), str) else None,
            payload[0].get("source_stem") if isinstance(payload[0].get("source_stem"), str) else None,
        )
    return None, None


def _integrity_verdict(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("integrity_verdict", "verdict", "final_verdict", "status"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
    return None


def _artifact_kind(path: Path) -> str:
    name = path.name
    if name in KNOWN_REPLAY_ARTIFACT_NAMES:
        return KNOWN_REPLAY_ARTIFACT_NAMES[name]
    if name.endswith(".json"):
        return "json_other"
    if name.endswith(".csv"):
        return "csv_other"
    return "other"


def _path_under_allowed_root(path: Path, allowed_root: str) -> bool:
    normalized = path.as_posix().rstrip("/")
    root = allowed_root.strip("/")
    guard = "/" + normalized.strip("/") + "/"
    root_guard = "/" + root + "/"
    return normalized == allowed_root or normalized.startswith(allowed_root + "/") or root_guard in guard


def validate_input_roots(input_roots: Sequence[str]) -> tuple[str, ...]:
    if not input_roots:
        raise ValueError("at least one replay input root is required")
    out: list[str] = []
    for root in input_roots:
        normalized = Path(root).as_posix().rstrip("/")
        if not _path_under_allowed_root(Path(normalized), "run/replay"):
            raise ValueError(f"D3 may only index read-only replay roots under run/replay: {root}")
        out.append(normalized)
    return tuple(out)


def iter_replay_artifact_paths(input_roots: Sequence[str], *, max_files: int = 5000) -> tuple[Path, ...]:
    roots = validate_input_roots(input_roots)
    found: list[Path] = []
    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        if root_path.is_file():
            if root_path.suffix.lower() in {".json", ".csv"}:
                found.append(root_path)
            continue
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".json", ".csv"}:
                continue
            found.append(path)
            if len(found) >= max_files:
                return tuple(sorted(found, key=lambda p: p.as_posix()))
    return tuple(sorted(found, key=lambda p: p.as_posix()))


def build_artifact_ref(path: Path, source_root: str) -> ReplayArtifactRef:
    size = path.stat().st_size
    payload = _safe_read_json(path) if path.suffix.lower() == ".json" else None
    source_file, source_stem = _first_source_meta(payload)
    integrity = _integrity_verdict(payload)
    source_verified = bool(
        source_file
        or source_stem
        or integrity
        or path.name in KNOWN_REPLAY_ARTIFACT_NAMES
    )
    return ReplayArtifactRef(
        path=path.as_posix(),
        source_root=source_root,
        artifact_kind=_artifact_kind(path),
        filename=path.name,
        suffix=path.suffix.lower(),
        size_bytes=size,
        sha256=_sha256(path),
        row_count=_row_count(payload),
        top_level_keys=_top_level_keys(payload),
        integrity_verdict=integrity,
        source_file=source_file,
        source_stem=source_stem,
        source_verified=source_verified,
        remarks="D3 read-only index row. No replay execution performed.",
    )


def build_replay_input_index(
    optimization_id: str,
    input_roots: Sequence[str] = DEFAULT_REPLAY_INPUT_ROOTS,
    *,
    max_files: int = 5000,
) -> ReplayInputIndex:
    roots = validate_input_roots(input_roots)
    paths = iter_replay_artifact_paths(roots, max_files=max_files)
    artifacts: list[ReplayArtifactRef] = []
    for path in paths:
        source_root = next((root for root in roots if _path_under_allowed_root(path, root)), roots[0])
        artifacts.append(build_artifact_ref(path, source_root))

    kinds = tuple(sorted({row.artifact_kind for row in artifacts}))
    if not roots:
        verdict = VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    elif not artifacts:
        verdict = VERDICT_NOT_READY_REPLAY_SOURCE_MISSING
    elif not any(row.source_verified for row in artifacts):
        verdict = VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE
    else:
        verdict = VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE

    return ReplayInputIndex(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=REPLAY_RESULT_INDEXER_CONTRACT_VERSION,
        accepted_for=REPLAY_RESULT_INDEXER_ACCEPTED_FOR,
        input_roots=roots,
        artifact_count=len(artifacts),
        artifact_kinds=kinds,
        artifacts=tuple(artifacts),
        optimizer_verdict=verdict,
    )


def replay_index_to_dict(index: ReplayInputIndex) -> dict[str, Any]:
    return asdict(index)


def write_replay_input_index(
    index: ReplayInputIndex,
    output_dir: str | Path,
    *,
    filename: str = "03_replay_input_index.json",
) -> Path:
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
        raise ValueError(f"D3 output must stay under {OUTPUT_ROOT}: {output_dir}")
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename
    path.write_text(json.dumps(replay_index_to_dict(index), indent=2, sort_keys=True), encoding="utf-8")
    return path


def replay_result_ref_rows_from_index(index: ReplayInputIndex) -> tuple[ReplayResultRefRow, ...]:
    rows: list[ReplayResultRefRow] = []
    for artifact in index.artifacts:
        if artifact.artifact_kind not in {
            "result_summary",
            "replay_manifest",
            "manifest",
            "integrity_report",
            "execution_shadow_results",
            "execution_results",
        }:
            continue
        rows.append(
            ReplayResultRefRow(
                optimization_id=index.optimization_id,
                candidate_id="UNASSIGNED_D3_READ_ONLY_INDEX",
                replay_run_id=Path(artifact.path).parent.name,
                replay_artifact_root=Path(artifact.path).parent.as_posix(),
                manifest_path=artifact.path if artifact.artifact_kind in {"manifest", "replay_manifest"} else "",
                result_summary_path=artifact.path if artifact.artifact_kind == "result_summary" else None,
                trade_log_path=None,
                candidate_audit_path=None,
                integrity_verdict=artifact.integrity_verdict,
                input_fingerprint=artifact.sha256,
                source_verified=artifact.source_verified,
                remarks="D3 read-only replay result reference. Candidate not assigned yet.",
            )
        )
    return tuple(rows)


def result_indexer_summary(input_roots: Sequence[str] = DEFAULT_REPLAY_INPUT_ROOTS) -> dict[str, Any]:
    index = build_replay_input_index("D3_SUMMARY", input_roots, max_files=500)
    return {
        "contract_version": REPLAY_RESULT_INDEXER_CONTRACT_VERSION,
        "accepted_for": REPLAY_RESULT_INDEXER_ACCEPTED_FOR,
        "input_roots": index.input_roots,
        "artifact_count": index.artifact_count,
        "artifact_kinds": index.artifact_kinds,
        "optimizer_verdict": index.optimizer_verdict,
        "replay_execution_performed": False,
        "ml_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "REPLAY_RESULT_INDEXER_CONTRACT_VERSION",
    "REPLAY_RESULT_INDEXER_ACCEPTED_FOR",
    "DEFAULT_REPLAY_INPUT_ROOTS",
    "KNOWN_REPLAY_ARTIFACT_NAMES",
    "MAX_JSON_FILE_BYTES",
    "ReplayArtifactRef",
    "ReplayInputIndex",
    "validate_input_roots",
    "iter_replay_artifact_paths",
    "build_artifact_ref",
    "build_replay_input_index",
    "replay_index_to_dict",
    "write_replay_input_index",
    "replay_result_ref_rows_from_index",
    "result_indexer_summary",
)
