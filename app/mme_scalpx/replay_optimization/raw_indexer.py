"""Lane D D4 read-only RAW / Research Gate feature indexer.

This module reads offline RAW, research_capture, and research_gate artifacts
and writes Lane D index artifacts under run/replay_optimization.

It must not execute replay, train models, call brokers, write live state,
start runtime services, mutate strategy doctrine, or mutate replay engine code.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from .contracts import (
    OUTPUT_ROOT,
    RawFeatureRefRow,
    VERDICT_NOT_READY_RAW_SOURCE_MISSING,
    VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
)

RAW_FEATURE_INDEXER_CONTRACT_VERSION = "replay_optimization_d4_raw_feature_indexer_contract_v1"
RAW_FEATURE_INDEXER_ACCEPTED_FOR = "READ_ONLY_RAW_INDEX_CONTRACT"

DEFAULT_RAW_INPUT_ROOTS = (
    "run/research_gate",
    "run/research_capture",
)

KNOWN_RAW_ARTIFACT_HINTS = {
    "oi": "oi_wall",
    "wall": "oi_wall",
    "pnl": "pnl",
    "rank": "strategy_rank",
    "verdict": "replay_verdict",
    "promotion": "promotion",
    "enriched": "enriched_rerun",
    "feature": "feature",
    "capture": "research_capture",
    "manifest": "manifest",
    "session": "session",
    "raw": "raw",
}

MAX_RAW_FILE_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class RawFeatureArtifactRef:
    path: str
    source_root: str
    source_family: str
    feature_family: str
    feature_name: str
    filename: str
    suffix: str
    size_bytes: int
    sha256: str
    row_count: int | None = None
    top_level_keys: tuple[str, ...] = field(default_factory=tuple)
    join_key_candidates: tuple[str, ...] = field(default_factory=tuple)
    coverage_pct: float | None = None
    source_verified: bool = False
    remarks: str | None = None


@dataclass(frozen=True, slots=True)
class RawFeatureIndex:
    optimization_id: str
    created_at: str
    contract_version: str
    accepted_for: str
    input_roots: tuple[str, ...]
    artifact_count: int
    feature_families: tuple[str, ...]
    artifacts: tuple[RawFeatureArtifactRef, ...]
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


def _safe_read_jsonish(path: Path) -> Any | None:
    try:
        if path.stat().st_size > MAX_RAW_FILE_BYTES:
            return None
        if path.suffix.lower() == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        if path.suffix.lower() == ".jsonl":
            rows = []
            with path.open("r", encoding="utf-8") as fh:
                for i, line in enumerate(fh):
                    if i >= 250:
                        break
                    line = line.strip()
                    if line:
                        try:
                            rows.append(json.loads(line))
                        except Exception:
                            continue
            return rows
    except Exception:
        return None
    return None


def _row_count(payload: Any, path: Path) -> int | None:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for key in ("rows", "items", "records", "data", "results", "features"):
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
        return 1
    if path.suffix.lower() == ".csv":
        try:
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                count = max(sum(1 for _ in fh) - 1, 0)
            return count
        except Exception:
            return None
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


def _join_key_candidates(payload: Any, path: Path) -> tuple[str, ...]:
    keys = set(_top_level_keys(payload))
    common = {
        "ts",
        "timestamp",
        "frame_ts_ns",
        "source_file",
        "source_stem",
        "session_date",
        "symbol",
        "instrument_token",
        "strategy_family",
        "side",
        "candidate_id",
        "replay_run_id",
    }
    found = sorted(keys.intersection(common))
    if not found and path.suffix.lower() == ".csv":
        try:
            first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
            header_keys = {x.strip() for x in first.split(",") if x.strip()}
            found = sorted(header_keys.intersection(common))
        except Exception:
            found = []
    return tuple(found)


def _source_family(path: Path) -> str:
    text = path.as_posix()
    if "/run/research_gate/" in "/" + text.strip("/") + "/":
        return "research_gate"
    if "/run/research_capture/" in "/" + text.strip("/") + "/":
        return "research_capture"
    return "raw_unknown"


def _infer_feature_family(path: Path, payload: Any) -> str:
    name = path.name.lower()
    parent = path.parent.name.lower()
    search = f"{parent}_{name}"
    for hint, family in KNOWN_RAW_ARTIFACT_HINTS.items():
        if hint in search:
            return family
    if isinstance(payload, dict):
        for key in ("feature_family", "family", "artifact_family", "report_type"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
    return "raw_feature"


def _infer_feature_name(path: Path, payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("feature_name", "name", "artifact_name", "report_name"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
    return path.stem


def _path_under_allowed_root(path: Path, allowed_root: str) -> bool:
    normalized = path.as_posix().rstrip("/")
    root = allowed_root.strip("/")
    guard = "/" + normalized.strip("/") + "/"
    root_guard = "/" + root + "/"
    return normalized == allowed_root or normalized.startswith(allowed_root + "/") or root_guard in guard


def validate_raw_input_roots(input_roots: Sequence[str]) -> tuple[str, ...]:
    if not input_roots:
        raise ValueError("at least one RAW input root is required")
    out: list[str] = []
    for root in input_roots:
        normalized = Path(root).as_posix().rstrip("/")
        if not (
            _path_under_allowed_root(Path(normalized), "run/research_gate")
            or _path_under_allowed_root(Path(normalized), "run/research_capture")
        ):
            raise ValueError(
                "D4 may only index read-only roots under run/research_gate or run/research_capture: "
                f"{root}"
            )
        out.append(normalized)
    return tuple(out)


def iter_raw_feature_artifact_paths(input_roots: Sequence[str], *, max_files: int = 5000) -> tuple[Path, ...]:
    roots = validate_raw_input_roots(input_roots)
    found: list[Path] = []
    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        if root_path.is_file():
            if root_path.suffix.lower() in {".json", ".jsonl", ".csv"}:
                found.append(root_path)
            continue
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".json", ".jsonl", ".csv"}:
                continue
            found.append(path)
            if len(found) >= max_files:
                return tuple(sorted(found, key=lambda p: p.as_posix()))
    return tuple(sorted(found, key=lambda p: p.as_posix()))


def build_raw_feature_artifact_ref(path: Path, source_root: str) -> RawFeatureArtifactRef:
    payload = _safe_read_jsonish(path)
    family = _infer_feature_family(path, payload)
    name = _infer_feature_name(path, payload)
    join_keys = _join_key_candidates(payload, path)
    source_verified = bool(join_keys or family != "raw_feature" or path.suffix.lower() in {".json", ".jsonl", ".csv"})
    return RawFeatureArtifactRef(
        path=path.as_posix(),
        source_root=source_root,
        source_family=_source_family(path),
        feature_family=family,
        feature_name=name,
        filename=path.name,
        suffix=path.suffix.lower(),
        size_bytes=path.stat().st_size,
        sha256=_sha256(path),
        row_count=_row_count(payload, path),
        top_level_keys=_top_level_keys(payload),
        join_key_candidates=join_keys,
        coverage_pct=None,
        source_verified=source_verified,
        remarks="D4 read-only RAW feature index row. No replay execution or ML training performed.",
    )


def build_raw_feature_index(
    optimization_id: str,
    input_roots: Sequence[str] = DEFAULT_RAW_INPUT_ROOTS,
    *,
    max_files: int = 5000,
) -> RawFeatureIndex:
    roots = validate_raw_input_roots(input_roots)
    paths = iter_raw_feature_artifact_paths(roots, max_files=max_files)
    artifacts: list[RawFeatureArtifactRef] = []
    for path in paths:
        source_root = next((root for root in roots if _path_under_allowed_root(path, root)), roots[0])
        artifacts.append(build_raw_feature_artifact_ref(path, source_root))

    families = tuple(sorted({row.feature_family for row in artifacts}))
    if not artifacts:
        verdict = VERDICT_NOT_READY_RAW_SOURCE_MISSING
    elif not any(row.source_verified for row in artifacts):
        verdict = VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE
    else:
        verdict = VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE

    return RawFeatureIndex(
        optimization_id=optimization_id,
        created_at=_utc_now(),
        contract_version=RAW_FEATURE_INDEXER_CONTRACT_VERSION,
        accepted_for=RAW_FEATURE_INDEXER_ACCEPTED_FOR,
        input_roots=roots,
        artifact_count=len(artifacts),
        feature_families=families,
        artifacts=tuple(artifacts),
        optimizer_verdict=verdict,
    )


def raw_feature_index_to_dict(index: RawFeatureIndex) -> dict[str, Any]:
    return asdict(index)


def write_raw_feature_index(
    index: RawFeatureIndex,
    output_dir: str | Path,
    *,
    filename: str = "04_raw_feature_index.json",
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
        raise ValueError(f"D4 output must stay under {OUTPUT_ROOT}: {output_dir}")
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename
    path.write_text(json.dumps(raw_feature_index_to_dict(index), indent=2, sort_keys=True), encoding="utf-8")
    return path


def raw_feature_ref_rows_from_index(index: RawFeatureIndex) -> tuple[RawFeatureRefRow, ...]:
    rows: list[RawFeatureRefRow] = []
    for artifact in index.artifacts:
        rows.append(
            RawFeatureRefRow(
                optimization_id=index.optimization_id,
                candidate_id="UNASSIGNED_D4_READ_ONLY_INDEX",
                raw_source_root=artifact.source_root,
                research_gate_root=artifact.source_root if artifact.source_family == "research_gate" else None,
                feature_family=artifact.feature_family,
                feature_name=artifact.feature_name,
                feature_window=None,
                join_key=",".join(artifact.join_key_candidates) if artifact.join_key_candidates else None,
                coverage_pct=artifact.coverage_pct,
                source_verified=artifact.source_verified,
                remarks="D4 read-only RAW feature reference. Candidate not assigned yet.",
            )
        )
    return tuple(rows)


def raw_indexer_summary(input_roots: Sequence[str] = DEFAULT_RAW_INPUT_ROOTS) -> dict[str, Any]:
    index = build_raw_feature_index("D4_SUMMARY", input_roots, max_files=500)
    return {
        "contract_version": RAW_FEATURE_INDEXER_CONTRACT_VERSION,
        "accepted_for": RAW_FEATURE_INDEXER_ACCEPTED_FOR,
        "input_roots": index.input_roots,
        "artifact_count": index.artifact_count,
        "feature_families": index.feature_families,
        "optimizer_verdict": index.optimizer_verdict,
        "replay_execution_performed": False,
        "ml_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
    }


__all__ = (
    "RAW_FEATURE_INDEXER_CONTRACT_VERSION",
    "RAW_FEATURE_INDEXER_ACCEPTED_FOR",
    "DEFAULT_RAW_INPUT_ROOTS",
    "KNOWN_RAW_ARTIFACT_HINTS",
    "MAX_RAW_FILE_BYTES",
    "RawFeatureArtifactRef",
    "RawFeatureIndex",
    "validate_raw_input_roots",
    "iter_raw_feature_artifact_paths",
    "build_raw_feature_artifact_ref",
    "build_raw_feature_index",
    "raw_feature_index_to_dict",
    "write_raw_feature_index",
    "raw_feature_ref_rows_from_index",
    "raw_indexer_summary",
)
