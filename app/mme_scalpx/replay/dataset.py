"""
app/mme_scalpx/replay/dataset.py

Freeze-grade dataset foundation for the MME-ScalpX Permanent Replay & Validation
Framework.

R2 Dataset Foundation
---------------------
This module owns:
- replay dataset root discovery
- deterministic trading-day enumeration
- dataset/day/session metadata extraction
- dataset fingerprinting
- file-level validation and coverage summaries
- replay dataset loading for canonical JSONL/CSV capture files

This module does not own:
- replay date/window selection policy
- replay clock mechanics
- replay injection/orchestration
- experiment overrides
- report generation
- live runtime state mutation

Design rules
------------
- dataset discovery must be deterministic and auditable
- fingerprints must be stable for unchanged inputs
- replay must consume historical artifacts only
- no hidden mutation of source files
- no doctrine logic belongs here
- this module should be useful to both locked and shadow replay equally
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence

DATASET_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEFAULT_SUPPORTED_SUFFIXES: tuple[str, ...] = (".jsonl", ".json", ".csv")
DEFAULT_DAY_REQUIRED_STEMS: tuple[str, ...] = ()
DEFAULT_DAY_OPTIONAL_STEMS: tuple[str, ...] = ()


class ReplayDatasetError(RuntimeError):
    """Base exception for replay dataset failures."""


class ReplayDatasetNotFoundError(ReplayDatasetError):
    """Raised when a dataset root or trading day cannot be found."""


class ReplayDatasetValidationError(ReplayDatasetError):
    """Raised when a dataset or file violates replay dataset rules."""


class ReplayDatasetFormatError(ReplayDatasetError):
    """Raised when a dataset file cannot be parsed according to its format."""


@dataclass(frozen=True, slots=True)
class DatasetDiscoveryConfig:
    """
    Discovery-time configuration for replay datasets.
    """

    root: Path | str
    required_file_stems: tuple[str, ...] = DEFAULT_DAY_REQUIRED_STEMS
    optional_file_stems: tuple[str, ...] = DEFAULT_DAY_OPTIONAL_STEMS
    supported_suffixes: tuple[str, ...] = DEFAULT_SUPPORTED_SUFFIXES
    recurse: bool = False
    ignore_hidden: bool = True


@dataclass(frozen=True, slots=True)
class ReplayFileSummary:
    """Stable metadata summary for a replay file."""

    name: str
    relative_path: str
    suffix: str
    stem: str
    size_bytes: int
    sha256: str
    line_count: int | None
    row_count: int | None
    modified_at_utc: str


@dataclass(frozen=True, slots=True)
class ReplayDayCoverage:
    """Coverage summary for a trading day."""

    required_present: tuple[str, ...]
    required_missing: tuple[str, ...]
    optional_present: tuple[str, ...]
    optional_missing: tuple[str, ...]
    readable_files: int
    total_size_bytes: int
    validity: str


@dataclass(frozen=True, slots=True)
class ReplayTradingDay:
    """Canonical trading-day object for replay."""

    date_str: str
    day_path: str
    files: tuple[ReplayFileSummary, ...]
    coverage: ReplayDayCoverage
    day_fingerprint: str


@dataclass(frozen=True, slots=True)
class ReplayDatasetSummary:
    """Canonical dataset summary used by runner/manifests/reports."""

    dataset_id: str
    dataset_root: str
    dataset_fingerprint: str
    trading_days: tuple[str, ...]
    total_days: int
    valid_days: int
    invalid_days: int
    total_files: int
    total_size_bytes: int
    required_file_stems: tuple[str, ...]
    optional_file_stems: tuple[str, ...]
    supported_suffixes: tuple[str, ...]
    created_at_utc: str
    observed_source_fields: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayDatasetRepository:
    """
    Deterministic replay dataset repository.
    """

    def __init__(self, config: DatasetDiscoveryConfig) -> None:
        self._config = _normalize_config(config)
        self._root = self._config.root

    @property
    def root(self) -> Path:
        return self._root

    @property
    def config(self) -> DatasetDiscoveryConfig:
        return self._config

    def ensure_root_exists(self) -> Path:
        root = self._root
        if not root.exists():
            raise ReplayDatasetNotFoundError(f"dataset root not found: {root}")
        if not root.is_dir():
            raise ReplayDatasetValidationError(f"dataset root is not a directory: {root}")
        return root

    def list_trading_dates(self) -> tuple[str, ...]:
        root = self.ensure_root_exists()
        dates: list[str] = []

        for entry in sorted(root.iterdir(), key=lambda p: p.name):
            if self._should_ignore_path(entry):
                continue
            if not entry.is_dir():
                continue
            if DATASET_DATE_RE.match(entry.name):
                dates.append(entry.name)

        return tuple(dates)

    def has_trading_day(self, date_str: str) -> bool:
        _validate_date_str(date_str)
        return (self._root / date_str).is_dir()

    def get_trading_day_path(self, date_str: str) -> Path:
        _validate_date_str(date_str)
        path = self._root / date_str
        if not path.exists() or not path.is_dir():
            raise ReplayDatasetNotFoundError(f"trading day not found: {date_str}")
        return path

    def load_trading_day(self, date_str: str) -> ReplayTradingDay:
        day_path = self.get_trading_day_path(date_str)
        file_paths = self._discover_day_files(day_path)
        file_summaries = tuple(self._build_file_summary(day_path, path) for path in file_paths)
        coverage = self._build_day_coverage(file_summaries)
        day_fingerprint = _fingerprint_text(
            _stable_json_dumps(
                {
                    "date": date_str,
                    "files": [file_summary_to_dict(x) for x in file_summaries],
                    "coverage": coverage_to_dict(coverage),
                }
            )
        )
        return ReplayTradingDay(
            date_str=date_str,
            day_path=str(day_path),
            files=file_summaries,
            coverage=coverage,
            day_fingerprint=day_fingerprint,
        )

    def load_all_trading_days(self) -> tuple[ReplayTradingDay, ...]:
        return tuple(self.load_trading_day(date_str) for date_str in self.list_trading_dates())

    def build_dataset_summary(
        self,
        *,
        dataset_id: str | None = None,
        notes: Sequence[str] | None = None,
    ) -> ReplayDatasetSummary:
        root = self.ensure_root_exists()
        trading_days = self.load_all_trading_days()
        dataset_id_final = dataset_id or root.name or "replay_dataset"

        total_files = sum(len(day.files) for day in trading_days)
        total_size_bytes = sum(
            file_summary.size_bytes for day in trading_days for file_summary in day.files
        )
        valid_days = sum(1 for day in trading_days if day.coverage.validity == "valid")
        invalid_days = len(trading_days) - valid_days

        fingerprint_payload = {
            "dataset_id": dataset_id_final,
            "dataset_root": str(root),
            "trading_days": [trading_day_to_dict(day) for day in trading_days],
            "required_file_stems": list(self._config.required_file_stems),
            "optional_file_stems": list(self._config.optional_file_stems),
            "supported_suffixes": list(self._config.supported_suffixes),
        }
        dataset_fingerprint = _fingerprint_text(_stable_json_dumps(fingerprint_payload))
        observed_source_fields = _collect_observed_source_fields_for_dataset(
            self,
            tuple(day.date_str for day in trading_days),
        )

        return ReplayDatasetSummary(
            dataset_id=dataset_id_final,
            dataset_root=str(root),
            dataset_fingerprint=dataset_fingerprint,
            trading_days=tuple(day.date_str for day in trading_days),
            total_days=len(trading_days),
            valid_days=valid_days,
            invalid_days=invalid_days,
            total_files=total_files,
            total_size_bytes=total_size_bytes,
            required_file_stems=self._config.required_file_stems,
            optional_file_stems=self._config.optional_file_stems,
            supported_suffixes=self._config.supported_suffixes,
            created_at_utc=_utc_now_iso(),
            observed_source_fields=observed_source_fields,
            notes=tuple(notes or ()),
        )

    def read_jsonl(self, path: Path | str) -> tuple[dict[str, Any], ...]:
        file_path = self._resolve_file_path(path)
        _validate_supported_suffix(file_path, expected=(".jsonl",))
        records: list[dict[str, Any]] = []

        with file_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    obj = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ReplayDatasetFormatError(
                        f"invalid JSONL at {file_path} line {line_number}: {exc}"
                    ) from exc
                if not isinstance(obj, dict):
                    raise ReplayDatasetFormatError(
                        f"JSONL record must be object at {file_path} line {line_number}"
                    )
                records.append(obj)

        return tuple(records)

    def iter_jsonl(self, path: Path | str) -> Iterator[dict[str, Any]]:
        file_path = self._resolve_file_path(path)
        _validate_supported_suffix(file_path, expected=(".jsonl",))

        with file_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    obj = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ReplayDatasetFormatError(
                        f"invalid JSONL at {file_path} line {line_number}: {exc}"
                    ) from exc
                if not isinstance(obj, dict):
                    raise ReplayDatasetFormatError(
                        f"JSONL record must be object at {file_path} line {line_number}"
                    )
                yield obj

    def read_json(self, path: Path | str) -> Any:
        file_path = self._resolve_file_path(path)
        _validate_supported_suffix(file_path, expected=(".json",))

        with file_path.open("r", encoding="utf-8") as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError as exc:
                raise ReplayDatasetFormatError(f"invalid JSON at {file_path}: {exc}") from exc

    def read_csv_rows(self, path: Path | str) -> tuple[dict[str, str], ...]:
        file_path = self._resolve_file_path(path)
        _validate_supported_suffix(file_path, expected=(".csv",))

        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows: list[dict[str, str]] = [dict(row) for row in reader]
        return tuple(rows)

    def iter_csv_rows(self, path: Path | str) -> Iterator[dict[str, str]]:
        file_path = self._resolve_file_path(path)
        _validate_supported_suffix(file_path, expected=(".csv",))

        with file_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                yield dict(row)

    def _resolve_file_path(self, path: Path | str) -> Path:
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = (self._root / file_path).resolve()
        if not file_path.exists():
            raise ReplayDatasetNotFoundError(f"replay file not found: {file_path}")
        if not file_path.is_file():
            raise ReplayDatasetValidationError(f"replay path is not a file: {file_path}")
        return file_path

    def _discover_day_files(self, day_path: Path) -> tuple[Path, ...]:
        paths: Iterable[Path]
        if self._config.recurse:
            paths = day_path.rglob("*")
        else:
            paths = day_path.iterdir()

        collected: list[Path] = []
        for path in sorted(paths, key=lambda p: str(p.relative_to(day_path))):
            if self._should_ignore_path(path):
                continue
            if not path.is_file():
                continue
            if path.suffix.lower() not in self._config.supported_suffixes:
                continue
            collected.append(path)

        return tuple(collected)

    def _build_file_summary(self, day_path: Path, path: Path) -> ReplayFileSummary:
        stat = path.stat()
        suffix = path.suffix.lower()
        relative_path = str(path.relative_to(day_path))
        line_count, row_count = _derive_counts(path, suffix)

        return ReplayFileSummary(
            name=path.name,
            relative_path=relative_path,
            suffix=suffix,
            stem=path.stem,
            size_bytes=stat.st_size,
            sha256=_sha256_file(path),
            line_count=line_count,
            row_count=row_count,
            modified_at_utc=_timestamp_to_utc_iso(stat.st_mtime),
        )

    def _build_day_coverage(
        self,
        file_summaries: Sequence[ReplayFileSummary],
    ) -> ReplayDayCoverage:
        present_stems = {item.stem for item in file_summaries}

        required_present = tuple(
            stem for stem in self._config.required_file_stems if stem in present_stems
        )
        required_missing = tuple(
            stem for stem in self._config.required_file_stems if stem not in present_stems
        )
        optional_present = tuple(
            stem for stem in self._config.optional_file_stems if stem in present_stems
        )
        optional_missing = tuple(
            stem for stem in self._config.optional_file_stems if stem not in present_stems
        )

        validity = "valid" if not required_missing else "invalid"
        total_size_bytes = sum(item.size_bytes for item in file_summaries)

        return ReplayDayCoverage(
            required_present=required_present,
            required_missing=required_missing,
            optional_present=optional_present,
            optional_missing=optional_missing,
            readable_files=len(file_summaries),
            total_size_bytes=total_size_bytes,
            validity=validity,
        )

    def _should_ignore_path(self, path: Path) -> bool:
        if not self._config.ignore_hidden:
            return False
        return any(part.startswith(".") for part in path.parts)


def discover_replay_dataset(
    config: DatasetDiscoveryConfig,
    *,
    dataset_id: str | None = None,
    notes: Sequence[str] | None = None,
) -> ReplayDatasetSummary:
    repo = ReplayDatasetRepository(config)
    return repo.build_dataset_summary(dataset_id=dataset_id, notes=notes)



def load_replay_dataset_declaration_for_summary(dataset_summary):
    from pathlib import Path
    import json as _json
    from app.mme_scalpx.replay.contracts import (
        REPLAY_DATASET_DECLARATION_VERSION,
        ReplayDatasetDeclaration,
        replay_dataset_declaration_to_dict,
        validate_replay_dataset_declaration,
    )

    if not isinstance(dataset_summary, Mapping):
        raise TypeError("dataset_summary must be a mapping")

    dataset_id = str(dataset_summary.get("dataset_id") or "").strip()
    if not dataset_id:
        return None

    declaration_path = (
        Path("etc/replay/datasets")
        / f"replay_dataset_declaration_{dataset_id}_{REPLAY_DATASET_DECLARATION_VERSION}.json"
    )
    if not declaration_path.exists():
        return None

    payload = _json.loads(declaration_path.read_text(encoding="utf-8"))
    notes_value = payload.get("notes") or ()
    if isinstance(notes_value, list):
        notes_value = tuple(str(item) for item in notes_value)
    elif isinstance(notes_value, tuple):
        notes_value = tuple(str(item) for item in notes_value)
    else:
        notes_value = ()

    declaration = ReplayDatasetDeclaration(
        declaration_version=str(payload.get("declaration_version") or ""),
        dataset_id=str(payload.get("dataset_id") or ""),
        dataset_root=str(payload.get("dataset_root") or ""),
        capability_profile_id=str(payload.get("capability_profile_id") or ""),
        capability_profile_version=str(payload.get("capability_profile_version") or ""),
        notes=notes_value,
    )
    validate_replay_dataset_declaration(declaration)

    return {
        "dataset_declaration_present": True,
        "dataset_declaration_path": str(declaration_path),
        "dataset_declaration": replay_dataset_declaration_to_dict(declaration),
        "declared_capability_profile_id": declaration.capability_profile_id,
        "declared_capability_profile_version": declaration.capability_profile_version,
    }


def attach_replay_dataset_declaration_to_dataset_summary(dataset_summary):
    from pathlib import Path
    from app.mme_scalpx.replay.contracts import REPLAY_DATASET_DECLARATION_VERSION

    if not isinstance(dataset_summary, dict):
        raise TypeError("dataset_summary must be a dict")

    payload = dict(dataset_summary)
    dataset_id = str(payload.get("dataset_id") or "").strip()
    declaration_path = (
        Path("etc/replay/datasets")
        / f"replay_dataset_declaration_{dataset_id}_{REPLAY_DATASET_DECLARATION_VERSION}.json"
    ) if dataset_id else None

    loaded = load_replay_dataset_declaration_for_summary(payload)
    if loaded is None:
        payload["dataset_declaration_present"] = False
        payload["dataset_declaration_path"] = str(declaration_path) if declaration_path is not None else None
        payload["dataset_declaration"] = None
        payload["declared_capability_profile_id"] = None
        payload["declared_capability_profile_version"] = None
        return payload

    payload.update(loaded)
    return payload




def load_replay_dataset_capability_profile_for_summary(dataset_summary):
    from pathlib import Path
    import json as _json

    if not isinstance(dataset_summary, Mapping):
        raise TypeError("dataset_summary must be a mapping")

    profile_id = str(dataset_summary.get("declared_capability_profile_id") or "").strip()
    if not profile_id:
        return None

    profile_path = Path("etc/replay/datasets") / f"{profile_id}.json"
    if not profile_path.exists():
        return {
            "dataset_capability_profile_present": False,
            "dataset_capability_profile_path": str(profile_path),
            "dataset_capability_profile": None,
            "declared_source_mode": None,
        }

    payload = _json.loads(profile_path.read_text(encoding="utf-8"))
    return {
        "dataset_capability_profile_present": True,
        "dataset_capability_profile_path": str(profile_path),
        "dataset_capability_profile": payload,
        "declared_source_mode": payload.get("declared_source_mode"),
    }





def attach_replay_dataset_readiness_verdict_to_dataset_summary(dataset_summary):
    if not isinstance(dataset_summary, dict):
        raise TypeError("dataset_summary must be a dict")

    payload = dict(dataset_summary)

    declared_source_mode = payload.get("declared_source_mode")
    admissibility_ok = payload.get("dataset_declaration_admissibility_ok")
    admissibility_status = payload.get("dataset_declaration_admissibility_status")
    economics_evaluable = payload.get("feed_input_economics_evaluable")
    economics_source_status = payload.get("economics_source_status")

    if admissibility_status == "no_declaration":
        payload["replay_dataset_readiness_status"] = "no_declaration"
        payload["replay_dataset_readiness_ok"] = None
        payload["replay_dataset_economics_comparison_ready"] = False
        payload["replay_dataset_readiness_message"] = "dataset declaration not present"
        return payload

    if admissibility_ok is not True:
        payload["replay_dataset_readiness_status"] = "rejected"
        payload["replay_dataset_readiness_ok"] = False
        payload["replay_dataset_economics_comparison_ready"] = False
        payload["replay_dataset_readiness_message"] = payload.get(
            "dataset_declaration_admissibility_message"
        )
        return payload

    if declared_source_mode == "quote_only_recorded":
        payload["replay_dataset_readiness_status"] = "admitted_quote_only"
        payload["replay_dataset_readiness_ok"] = True
        payload["replay_dataset_economics_comparison_ready"] = False
        payload["replay_dataset_readiness_message"] = (
            "dataset is admissible as quote-only; economics comparison remains not ready"
        )
        return payload

    if declared_source_mode == "economics_enriched_recorded":
        ready = (
            economics_evaluable is True
            and economics_source_status == "ready"
        )
        payload["replay_dataset_readiness_status"] = (
            "admitted_economics_enriched" if ready else "admitted_but_not_economics_ready"
        )
        payload["replay_dataset_readiness_ok"] = True
        payload["replay_dataset_economics_comparison_ready"] = ready
        payload["replay_dataset_readiness_message"] = (
            "dataset is admissible as economics-enriched and ready for economics comparison"
            if ready
            else "dataset is admissible as economics-enriched but not yet economics-comparison ready"
        )
        return payload

    payload["replay_dataset_readiness_status"] = "unknown_declared_mode"
    payload["replay_dataset_readiness_ok"] = False
    payload["replay_dataset_economics_comparison_ready"] = False
    payload["replay_dataset_readiness_message"] = (
        f"unsupported declared_source_mode: {declared_source_mode}"
    )
    return payload


def attach_replay_dataset_declaration_admissibility_to_dataset_summary(dataset_summary):
    if not isinstance(dataset_summary, dict):
        raise TypeError("dataset_summary must be a dict")

    payload = dict(dataset_summary)

    declared_profile_id = payload.get("declared_capability_profile_id")
    declared_source_mode = payload.get("declared_source_mode")
    inferred_source_mode = payload.get("feed_input_source_mode")
    consistency_ok = payload.get("dataset_capability_consistency_ok")
    field_coverage_ok = payload.get("declared_profile_field_coverage_ok")
    economics_evaluable = payload.get("feed_input_economics_evaluable")

    if declared_profile_id is None:
        payload["dataset_declaration_admissibility_status"] = "no_declaration"
        payload["dataset_declaration_admissibility_ok"] = None
        payload["dataset_declaration_admissibility_message"] = "dataset declaration not present"
        return payload

    if consistency_ok is not True:
        payload["dataset_declaration_admissibility_status"] = "rejected_profile_mismatch"
        payload["dataset_declaration_admissibility_ok"] = False
        payload["dataset_declaration_admissibility_message"] = (
            f"declared profile {declared_profile_id} is not admissible because "
            f"declared_source_mode={declared_source_mode} but inferred_source_mode={inferred_source_mode}"
        )
        return payload

    if field_coverage_ok is not True:
        payload["dataset_declaration_admissibility_status"] = "rejected_missing_required_fields"
        payload["dataset_declaration_admissibility_ok"] = False
        payload["dataset_declaration_admissibility_message"] = (
            f"declared profile {declared_profile_id} is not admissible because required declared fields are missing: "
            f"{payload.get('declared_profile_missing_required_fields')}"
        )
        return payload

    if declared_source_mode == "economics_enriched_recorded" and economics_evaluable is not True:
        payload["dataset_declaration_admissibility_status"] = "rejected_not_economics_evaluable"
        payload["dataset_declaration_admissibility_ok"] = False
        payload["dataset_declaration_admissibility_message"] = (
            f"declared profile {declared_profile_id} is not admissible because feed_input_economics_evaluable is not true"
        )
        return payload

    payload["dataset_declaration_admissibility_status"] = "admissible"
    payload["dataset_declaration_admissibility_ok"] = True
    payload["dataset_declaration_admissibility_message"] = (
        f"declared profile {declared_profile_id} is admissible for this dataset summary"
    )
    return payload


def attach_replay_declared_profile_field_coverage_to_dataset_summary(dataset_summary):
    if not isinstance(dataset_summary, dict):
        raise TypeError("dataset_summary must be a dict")

    payload = dict(dataset_summary)

    observed = _phase_a5_normalize_observed_feed_input_fields(
        payload.get("observed_source_fields") or []
    )

    profile_payload = payload.get("dataset_capability_profile")
    if not isinstance(profile_payload, dict):
        payload["declared_profile_required_fields"] = []
        payload["declared_profile_missing_required_fields"] = []
        payload["declared_profile_field_coverage_status"] = "no_profile_payload"
        payload["declared_profile_field_coverage_ok"] = None
        return payload

    required_fields = list(profile_payload.get("required_normalized_observed_fields") or [])
    missing_fields = [
        field_name
        for field_name in required_fields
        if field_name not in observed
    ]

    payload["declared_profile_required_fields"] = required_fields
    payload["declared_profile_missing_required_fields"] = missing_fields
    payload["declared_profile_field_coverage_status"] = (
        "complete" if not missing_fields else "incomplete"
    )
    payload["declared_profile_field_coverage_ok"] = (len(missing_fields) == 0)
    return payload


def attach_replay_dataset_capability_consistency_to_dataset_summary(dataset_summary):
    if not isinstance(dataset_summary, dict):
        raise TypeError("dataset_summary must be a dict")

    payload = dict(dataset_summary)

    declared_profile_id = payload.get("declared_capability_profile_id")
    inferred_source_mode = payload.get("feed_input_source_mode")

    if declared_profile_id is None:
        payload["dataset_capability_profile_present"] = False
        payload["dataset_capability_profile_path"] = None
        payload["dataset_capability_profile"] = None
        payload["declared_source_mode"] = None
        payload["dataset_capability_consistency_status"] = "no_declaration"
        payload["dataset_capability_consistency_ok"] = None
        payload["dataset_capability_consistency_message"] = "dataset declaration not present"
        return payload

    loaded_profile = load_replay_dataset_capability_profile_for_summary(payload)
    if loaded_profile is not None:
        payload.update(loaded_profile)

    declared_source_mode = payload.get("declared_source_mode")

    if not payload.get("dataset_capability_profile_present"):
        payload["dataset_capability_consistency_status"] = "missing_declared_profile_file"
        payload["dataset_capability_consistency_ok"] = False
        payload["dataset_capability_consistency_message"] = (
            f"declared capability profile file not found for {declared_profile_id}"
        )
        return payload

    if declared_source_mode is None:
        payload["dataset_capability_consistency_status"] = "unknown_declared_profile"
        payload["dataset_capability_consistency_ok"] = False
        payload["dataset_capability_consistency_message"] = (
            f"declared capability profile {declared_profile_id} does not expose declared_source_mode"
        )
        return payload

    if inferred_source_mode == declared_source_mode:
        payload["dataset_capability_consistency_status"] = "aligned"
        payload["dataset_capability_consistency_ok"] = True
        payload["dataset_capability_consistency_message"] = (
            f"declared capability {declared_profile_id} matches inferred source mode {inferred_source_mode}"
        )
        return payload

    payload["dataset_capability_consistency_status"] = "mismatch"
    payload["dataset_capability_consistency_ok"] = False
    payload["dataset_capability_consistency_message"] = (
        f"declared capability {declared_profile_id} implies {declared_source_mode}, "
        f"but inferred source mode is {inferred_source_mode}"
    )
    return payload


def dataset_summary_to_dict(summary: ReplayDatasetSummary) -> dict[str, Any]:
    payload = {
        "dataset_id": summary.dataset_id,
        "dataset_root": summary.dataset_root,
        "dataset_fingerprint": summary.dataset_fingerprint,
        "trading_days": list(summary.trading_days),
        "total_days": summary.total_days,
        "valid_days": summary.valid_days,
        "invalid_days": summary.invalid_days,
        "total_files": summary.total_files,
        "total_size_bytes": summary.total_size_bytes,
        "required_file_stems": list(summary.required_file_stems),
        "optional_file_stems": list(summary.optional_file_stems),
        "supported_suffixes": list(summary.supported_suffixes),
        "created_at_utc": summary.created_at_utc,
        "observed_source_fields": list(summary.observed_source_fields),
        "notes": list(summary.notes),
    }
    payload = attach_replay_dataset_declaration_to_dataset_summary(payload)
    payload = attach_replay_feed_input_contract_summary_to_dataset_summary(payload)
    payload = attach_replay_dataset_capability_consistency_to_dataset_summary(payload)
    payload = attach_replay_declared_profile_field_coverage_to_dataset_summary(payload)
    payload = attach_replay_dataset_declaration_admissibility_to_dataset_summary(payload)
    payload = attach_economics_source_summary_to_dataset_summary(
        dataset_summary=payload,
        recorded_surface=build_dataset_economics_recorded_surface(payload),
        effective_inputs=None,
    )
    payload = attach_replay_dataset_readiness_verdict_to_dataset_summary(payload)
    return payload

def trading_day_to_dict(day: ReplayTradingDay) -> dict[str, Any]:
    return {
        "date_str": day.date_str,
        "day_path": day.day_path,
        "files": [file_summary_to_dict(item) for item in day.files],
        "coverage": coverage_to_dict(day.coverage),
        "day_fingerprint": day.day_fingerprint,
    }


def file_summary_to_dict(summary: ReplayFileSummary) -> dict[str, Any]:
    return {
        "name": summary.name,
        "relative_path": summary.relative_path,
        "suffix": summary.suffix,
        "stem": summary.stem,
        "size_bytes": summary.size_bytes,
        "sha256": summary.sha256,
        "line_count": summary.line_count,
        "row_count": summary.row_count,
        "modified_at_utc": summary.modified_at_utc,
    }


def coverage_to_dict(coverage: ReplayDayCoverage) -> dict[str, Any]:
    return {
        "required_present": list(coverage.required_present),
        "required_missing": list(coverage.required_missing),
        "optional_present": list(coverage.optional_present),
        "optional_missing": list(coverage.optional_missing),
        "readable_files": coverage.readable_files,
        "total_size_bytes": coverage.total_size_bytes,
        "validity": coverage.validity,
    }





ECONOMICS_DECLARED_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "ts": ("ts_event",),
}

# === Phase A.4 observed source field discovery ===

def _collect_observed_source_fields_for_day(
    repository: "ReplayDatasetRepository",
    date_str: str,
) -> tuple[str, ...]:
    observed: list[str] = []
    seen: set[str] = set()

    day_path = repository.get_trading_day_path(date_str)
    file_paths = repository._discover_day_files(day_path)

    for file_path in file_paths:
        suffix = file_path.suffix.lower()
        try:
            if suffix == ".jsonl":
                rows = repository.read_jsonl(file_path)
                candidates = rows[:1]
            elif suffix == ".json":
                payload = repository.read_json(file_path)
                if isinstance(payload, Mapping):
                    candidates = [payload]
                elif isinstance(payload, list) and payload and isinstance(payload[0], Mapping):
                    candidates = [payload[0]]
                else:
                    candidates = []
            elif suffix == ".csv":
                rows = repository.read_csv_rows(file_path)
                candidates = rows[:1]
            else:
                candidates = []
        except Exception:
            candidates = []

        for candidate in candidates:
            if isinstance(candidate, Mapping):
                for key in candidate.keys():
                    key_str = str(key).strip()
                    if key_str and key_str not in seen:
                        seen.add(key_str)
                        observed.append(key_str)

    return tuple(sorted(observed))


def _collect_observed_source_fields_for_dataset(
    repository: "ReplayDatasetRepository",
    trading_dates: Sequence[str],
) -> tuple[str, ...]:
    observed: list[str] = []
    seen: set[str] = set()

    for date_str in trading_dates:
        for key in _collect_observed_source_fields_for_day(repository, date_str):
            if key not in seen:
                seen.add(key)
                observed.append(key)

    return tuple(sorted(observed))


def _normalize_config(config: DatasetDiscoveryConfig) -> DatasetDiscoveryConfig:
    root = Path(config.root).expanduser().resolve()
    required_file_stems = tuple(sorted(dict.fromkeys(config.required_file_stems)))
    optional_file_stems = tuple(
        stem for stem in sorted(dict.fromkeys(config.optional_file_stems))
        if stem not in required_file_stems
    )
    supported_suffixes = tuple(
        sorted(
            {
                suffix.lower() if suffix.startswith(".") else f".{suffix.lower()}"
                for suffix in config.supported_suffixes
            }
        )
    )
    return DatasetDiscoveryConfig(
        root=root,
        required_file_stems=required_file_stems,
        optional_file_stems=optional_file_stems,
        supported_suffixes=supported_suffixes,
        recurse=config.recurse,
        ignore_hidden=config.ignore_hidden,
    )


def _validate_date_str(date_str: str) -> None:
    if not DATASET_DATE_RE.match(date_str):
        raise ReplayDatasetValidationError(
            f"trading day must be YYYY-MM-DD, got {date_str!r}"
        )
    try:
        date.fromisoformat(date_str)
    except ValueError as exc:
        raise ReplayDatasetValidationError(
            f"invalid trading day date: {date_str!r}"
        ) from exc


def _validate_supported_suffix(path: Path, *, expected: Sequence[str]) -> None:
    suffix = path.suffix.lower()
    allowed = tuple(x.lower() for x in expected)
    if suffix not in allowed:
        raise ReplayDatasetValidationError(
            f"unsupported file suffix for {path}: {suffix!r}; expected one of {allowed}"
        )


def _derive_counts(path: Path, suffix: str) -> tuple[int | None, int | None]:
    if suffix == ".jsonl":
        return _count_non_empty_lines(path), None
    if suffix == ".csv":
        line_count = _count_lines(path)
        row_count = _count_csv_rows(path)
        return line_count, row_count
    if suffix == ".json":
        return _count_lines(path), None
    return None, None


def _count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for _ in handle)


def _count_non_empty_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for _ in reader)


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _fingerprint_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _stable_json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _timestamp_to_utc_iso(timestamp: float) -> str:
    return datetime.utcfromtimestamp(timestamp).replace(microsecond=0).isoformat() + "Z"


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


__all__ = [
    "DATASET_DATE_RE",
    "DEFAULT_SUPPORTED_SUFFIXES",
    "DEFAULT_DAY_REQUIRED_STEMS",
    "DEFAULT_DAY_OPTIONAL_STEMS",
    "ReplayDatasetError",
    "ReplayDatasetNotFoundError",
    "ReplayDatasetValidationError",
    "ReplayDatasetFormatError",
    "DatasetDiscoveryConfig",
    "ReplayFileSummary",
    "ReplayDayCoverage",
    "ReplayTradingDay",
    "ReplayDatasetSummary",
    "ReplayDatasetRepository",
    "discover_replay_dataset",
    "dataset_summary_to_dict",
    "trading_day_to_dict",
    "file_summary_to_dict",
    "coverage_to_dict",
]

# === Phase A.4 dataset-side economics source classification ===

def _economics_dataset_value_present(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _economics_dataset_as_mapping(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "__dataclass_fields__"):
        return {
            field_name: getattr(value, field_name)
            for field_name in value.__dataclass_fields__
        }
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    raise TypeError(f"unsupported economics mapping source type: {type(value)!r}")


def _economics_dataset_collect_present_fields(source, required_fields):
    mapping = _economics_dataset_as_mapping(source)
    present = []
    for field_name in required_fields:
        if field_name in mapping and _economics_dataset_value_present(mapping[field_name]):
            present.append(field_name)
    return tuple(present)


def _economics_dataset_missing_fields(required_fields, present_fields):
    present_set = set(present_fields)
    return tuple(field_name for field_name in required_fields if field_name not in present_set)


def _economics_dataset_choose_policy_path(
    recorded_policy_present,
    effective_policy_present,
    recorded_policy_required,
    effective_policy_required,
):
    recorded_missing = _economics_dataset_missing_fields(
        recorded_policy_required,
        recorded_policy_present,
    )
    effective_missing = _economics_dataset_missing_fields(
        effective_policy_required,
        effective_policy_present,
    )

    if not recorded_missing:
        return "recorded", recorded_missing
    if not effective_missing:
        return "effective_inputs", effective_missing

    any_effective_present = len(effective_policy_present) > 0
    if any_effective_present:
        return "effective_inputs", effective_missing
    return "recorded", recorded_missing



def _economics_dataset_choose_source_mode(
    *,
    quote_cost_present,
    candidate_context_present,
    recorded_policy_present,
    effective_policy_present,
):
    from app.mme_scalpx.replay.contracts import (
        ECONOMICS_EFFECTIVE_INPUT_POLICY_FIELDS,
        ECONOMICS_RECORDED_POLICY_FIELDS,
        ECONOMICS_REQUIRED_CANDIDATE_CONTEXT_FIELDS,
        ECONOMICS_REQUIRED_QUOTE_COST_FIELDS,
    )

    quote_cost_present = tuple(quote_cost_present or ())
    candidate_context_present = tuple(candidate_context_present or ())
    recorded_policy_present = tuple(recorded_policy_present or ())
    effective_policy_present = tuple(effective_policy_present or ())

    quote_missing = tuple(
        field_name
        for field_name in ECONOMICS_REQUIRED_QUOTE_COST_FIELDS
        if field_name not in quote_cost_present
    )
    candidate_missing = tuple(
        field_name
        for field_name in ECONOMICS_REQUIRED_CANDIDATE_CONTEXT_FIELDS
        if field_name not in candidate_context_present
    )
    recorded_policy_missing = tuple(
        field_name
        for field_name in ECONOMICS_RECORDED_POLICY_FIELDS
        if field_name not in recorded_policy_present
    )
    effective_policy_missing = tuple(
        field_name
        for field_name in ECONOMICS_EFFECTIVE_INPUT_POLICY_FIELDS
        if field_name not in effective_policy_present
    )

    recorded_missing = tuple(dict.fromkeys(
        quote_missing + candidate_missing + recorded_policy_missing
    ))
    effective_missing = tuple(dict.fromkeys(
        quote_missing + candidate_missing + effective_policy_missing
    ))

    if not recorded_missing:
        return "recorded", recorded_missing
    if not effective_missing:
        return "effective_inputs", effective_missing

    any_effective_present = len(effective_policy_present) > 0
    if any_effective_present:
        return "effective_inputs", effective_missing
    return "recorded", recorded_missing


def classify_economics_source_coverage_for_dataset(
    recorded_surface,
    effective_inputs=None,
):
    from app.mme_scalpx.replay.contracts import (
        ECONOMICS_EFFECTIVE_INPUT_POLICY_FIELDS,
        ECONOMICS_RECORDED_POLICY_FIELDS,
        ECONOMICS_REQUIRED_CANDIDATE_CONTEXT_FIELDS,
        ECONOMICS_REQUIRED_QUOTE_COST_FIELDS,
        ECONOMICS_SOURCE_MODE_DERIVED_FROM_EFFECTIVE_INPUTS,
        ECONOMICS_SOURCE_MODE_RECORDED,
        ECONOMICS_SOURCE_MODE_UNAVAILABLE,
        ECONOMICS_SOURCE_STATUS_INSUFFICIENT_SOURCE_TRUTH,
        ECONOMICS_SOURCE_STATUS_READY,
        EconomicsSourceCoverage,
        validate_economics_source_coverage,
    )

    quote_cost_present = _economics_dataset_collect_present_fields(
        recorded_surface,
        ECONOMICS_REQUIRED_QUOTE_COST_FIELDS,
    )
    candidate_context_present = _economics_dataset_collect_present_fields(
        recorded_surface,
        ECONOMICS_REQUIRED_CANDIDATE_CONTEXT_FIELDS,
    )
    recorded_policy_present = _economics_dataset_collect_present_fields(
        recorded_surface,
        ECONOMICS_RECORDED_POLICY_FIELDS,
    )
    effective_policy_present = _economics_dataset_collect_present_fields(
        effective_inputs,
        ECONOMICS_EFFECTIVE_INPUT_POLICY_FIELDS,
    )

    source_mode, missing_required_fields = _economics_dataset_choose_source_mode(
        quote_cost_present=quote_cost_present,
        candidate_context_present=candidate_context_present,
        recorded_policy_present=recorded_policy_present,
        effective_policy_present=effective_policy_present,
    )

    if source_mode == ECONOMICS_SOURCE_MODE_RECORDED:
        source_mode_value = ECONOMICS_SOURCE_MODE_RECORDED
    elif source_mode == ECONOMICS_SOURCE_MODE_DERIVED_FROM_EFFECTIVE_INPUTS:
        source_mode_value = ECONOMICS_SOURCE_MODE_DERIVED_FROM_EFFECTIVE_INPUTS
    else:
        source_mode_value = ECONOMICS_SOURCE_MODE_UNAVAILABLE

    source_status = (
        ECONOMICS_SOURCE_STATUS_READY
        if not missing_required_fields
        else ECONOMICS_SOURCE_STATUS_INSUFFICIENT_SOURCE_TRUTH
    )

    provenance_fields_present = ["economics_source_mode", "economics_source_status"]
    if (
        source_mode_value == ECONOMICS_SOURCE_MODE_DERIVED_FROM_EFFECTIVE_INPUTS
        and "economics_formula_version" in effective_policy_present
    ):
        provenance_fields_present.append("economics_formula_version")

    coverage = EconomicsSourceCoverage(
        source_mode=source_mode_value,
        source_status=source_status,
        quote_cost_fields_present=tuple(quote_cost_present),
        candidate_context_fields_present=tuple(candidate_context_present),
        recorded_policy_fields_present=tuple(recorded_policy_present),
        effective_input_policy_fields_present=tuple(effective_policy_present),
        provenance_fields_present=tuple(provenance_fields_present),
        missing_required_fields=tuple(missing_required_fields),
        eligible_for_economics_evaluation=(len(missing_required_fields) == 0),
    )
    validate_economics_source_coverage(coverage)
    return coverage


def build_economics_source_summary_for_dataset(
    recorded_surface,
    effective_inputs=None,
):
    from app.mme_scalpx.replay.contracts import economics_source_coverage_to_dict

    coverage = classify_economics_source_coverage_for_dataset(
        recorded_surface=recorded_surface,
        effective_inputs=effective_inputs,
    )
    return economics_source_coverage_to_dict(coverage)


if "__all__" in globals():
    __all__ = tuple(__all__) + (
        "classify_replay_feed_input_source_mode_for_dataset",
        "attach_replay_feed_input_contract_summary_to_dataset_summary",
        "classify_economics_source_coverage_for_dataset",
        "build_economics_source_summary_for_dataset",
    )
else:
    __all__ = (
        "classify_replay_feed_input_source_mode_for_dataset",
        "attach_replay_feed_input_contract_summary_to_dataset_summary",
        "classify_economics_source_coverage_for_dataset",
        "build_economics_source_summary_for_dataset",
    )


# === Phase A.4 dataset-aware economics source basis helper ===

def _economics_summary_collect_declared_field_names(value):
    if value is None:
        return ()
    if isinstance(value, Mapping):
        iterable = value.keys()
    elif isinstance(value, (list, tuple, set)):
        iterable = value
    else:
        return ()

    names = []
    for item in iterable:
        if isinstance(item, str):
            normalized = item.strip()
            if normalized:
                names.append(normalized)
                for alias_target in ECONOMICS_DECLARED_FIELD_ALIASES.get(normalized, ()):
                    names.append(alias_target)
    return tuple(sorted(dict.fromkeys(names)))



def _phase_a5_present(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True



def _phase_a5_normalize_observed_feed_input_fields(observed_fields):
    normalized = set(observed_fields or [])

    alias_map = {
        "ts": "ts_event",
        "event_time": "ts_event",
        "exchange_ts": "ts_event",
        "frame_id": "source_frame_id",
        "leg": "selected_leg",
    }

    for source_name, target_name in alias_map.items():
        if source_name in normalized:
            normalized.add(target_name)

    return normalized


def classify_replay_feed_input_source_mode_for_dataset(dataset_summary):
    from app.mme_scalpx.replay.contracts import (
        REPLAY_FEED_INPUT_CONTRACT_VERSION,
        REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED,
        REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED,
        build_default_replay_feed_input_contract,
        replay_feed_input_contract_to_dict,
        validate_replay_feed_input_row,
    )

    contract = build_default_replay_feed_input_contract()
    observed = _phase_a5_normalize_observed_feed_input_fields(
        dataset_summary.get("observed_source_fields") or []
    )

    quote_row = {}
    enriched_row = {}

    for field_name in contract.common_required_fields:
        if field_name in observed:
            quote_row[field_name] = "__present__"
            enriched_row[field_name] = "__present__"

    for field_name in contract.economics_enriched_mode.required_fields:
        if field_name in observed:
            enriched_row[field_name] = "__present__"

    try:
        validate_replay_feed_input_row(
            REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED,
            enriched_row,
        )
        source_mode = REPLAY_FEED_INPUT_SOURCE_MODE_ECONOMICS_ENRICHED_RECORDED
        missing_fields = []
        economics_evaluable = True
    except Exception:
        validate_replay_feed_input_row(
            REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED,
            quote_row,
        )
        source_mode = REPLAY_FEED_INPUT_SOURCE_MODE_QUOTE_ONLY_RECORDED
        missing_fields = [
            field_name
            for field_name in contract.economics_enriched_mode.required_fields
            if field_name not in observed
        ]
        economics_evaluable = False

    return {
        "feed_input_contract_version": REPLAY_FEED_INPUT_CONTRACT_VERSION,
        "feed_input_source_mode": source_mode,
        "feed_input_missing_enriched_fields": missing_fields,
        "feed_input_economics_evaluable": economics_evaluable,
        "feed_input_contract": replay_feed_input_contract_to_dict(contract),
    }


def attach_replay_feed_input_contract_summary_to_dataset_summary(dataset_summary):
    payload = dict(dataset_summary)
    payload.update(classify_replay_feed_input_source_mode_for_dataset(payload))
    return payload


def build_dataset_economics_recorded_surface(dataset_summary):
    if not isinstance(dataset_summary, Mapping):
        raise TypeError("dataset_summary must be a mapping")

    surface = {}

    nested_mapping_keys = (
        "economics_recorded_surface",
        "recorded_source_surface",
        "replay_source_surface",
    )
    for key in nested_mapping_keys:
        value = dataset_summary.get(key)
        if isinstance(value, Mapping):
            for field_name, field_value in value.items():
                if _economics_dataset_value_present(field_value):
                    surface[str(field_name)] = field_value

    declared_field_name_keys = (
        "observed_source_fields",
        "sample_field_names",
        "replay_input_field_names",
        "economics_observed_fields",
    )
    for key in declared_field_name_keys:
        for field_name in _economics_summary_collect_declared_field_names(dataset_summary.get(key)):
            surface.setdefault(field_name, "__declared_present__")

    return surface


if "__all__" in globals():
    __all__ = tuple(__all__) + (
        "build_dataset_economics_recorded_surface",
    )
else:
    __all__ = (
        "build_dataset_economics_recorded_surface",
    )

# === Phase A.4 dataset summary economics attachment surface ===

def attach_economics_source_summary_to_dataset_summary(
    dataset_summary,
    recorded_surface=None,
    effective_inputs=None,
):
    if not isinstance(dataset_summary, dict):
        raise TypeError("dataset_summary must be a dict")

    economics_summary = build_economics_source_summary_for_dataset(
        recorded_surface=recorded_surface,
        effective_inputs=effective_inputs,
    )

    enriched = dict(dataset_summary)
    enriched["economics_source_mode"] = economics_summary["source_mode"]
    enriched["economics_source_status"] = economics_summary["source_status"]
    enriched["economics_eligible_for_evaluation"] = economics_summary["eligible_for_economics_evaluation"]
    enriched["economics_missing_required_fields"] = list(
        economics_summary["missing_required_fields"]
    )
    enriched["economics_source_summary"] = economics_summary
    return enriched


if "__all__" in globals():
    __all__ = tuple(__all__) + (
        "attach_economics_source_summary_to_dataset_summary",
    )
else:
    __all__ = (
        "attach_economics_source_summary_to_dataset_summary",
    )

# phase_a5_contract_aligned_source_mode

# ===== BATCH16_REPLAY_PACKAGE_FREEZE_GUARDS START =====
# Batch 16 freeze-final guard:
# Dataset owns historical artifact discovery only. This helper gives dataset
# proofs a replay-local way to validate captured feature-frame rows against the
# modern provider-aware / five-family MME payload contract without importing or
# mutating live runtime services.

def validate_mme_feature_frame_record(record: Mapping[str, Any]) -> dict[str, Any]:
    from .contracts import validate_mme_replay_feature_frame

    return validate_mme_replay_feature_frame(record)
# ===== BATCH16_REPLAY_PACKAGE_FREEZE_GUARDS END =====
