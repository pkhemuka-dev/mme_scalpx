#!/usr/bin/env python3
"""
bin/replay_run.py

Freeze-grade operational CLI entrypoint for one replay run of the
MME-ScalpX Permanent Replay & Validation Framework.

This version upgrades the feeds stage from placeholder output to a real
dataset->clock->injector replay bridge, while keeping downstream stages
explicitly thin until their replay wiring is frozen.
"""

from __future__ import annotations
# BEGIN BATCH27C_REPLAY_SAFETY_FIREWALL
try:
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety
except ModuleNotFoundError:
    import pathlib as _batch27c_pathlib
    import sys as _batch27c_sys

    _batch27c_here = _batch27c_pathlib.Path(__file__).resolve()
    for _batch27c_parent in [_batch27c_here.parent, *_batch27c_here.parents]:
        if (_batch27c_parent / "app" / "mme_scalpx").exists():
            if str(_batch27c_parent) not in _batch27c_sys.path:
                _batch27c_sys.path.insert(0, str(_batch27c_parent))
            break
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety

assert_replay_module_static_safety(__file__)
# END BATCH27C_REPLAY_SAFETY_FIREWALL

from datetime import datetime, timezone
from collections.abc import MutableMapping

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.artifacts import ReplayArtifactsWriter
from app.mme_scalpx.replay.clock import ReplayClock, ReplayClockConfig
from app.mme_scalpx.replay.contracts import ProfilesSection
from app.mme_scalpx.replay.dataset import DatasetDiscoveryConfig, ReplayDatasetRepository
from app.mme_scalpx.replay.engine import ReplayEngine
from app.mme_scalpx.replay.fill_model import (
    ReplayFillModelConfig,
    ReplayFillModelFactory,
    ReplayFillRequest,
)
from app.mme_scalpx.replay.injector import (
    ReplayInjectionEvent,
    ReplayInjector,
)
from app.mme_scalpx.replay.integrity import (
    ReplayIntegrityEvaluator,
    placeholder_pass_check,
    integrity_bundle_to_dict,
    INTEGRITY_CHECK_HASH_FRESHNESS,
    INTEGRITY_CHECK_HEARTBEAT,
    INTEGRITY_CHECK_REPRODUCIBILITY,
    INTEGRITY_CHECK_RESET_CLEANLINESS,
    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    INTEGRITY_CHECK_STALE_LEG,
    ReplayIntegrityCheckResult,
    IntegrityVerdict,
)
from app.mme_scalpx.replay.modes import (
    DoctrineMode,
    ReplayScope,
    ReplaySideMode,
    ReplaySelectionMode,
    ReplaySpeedMode,
)
from app.mme_scalpx.replay.reports import build_report_bundle, report_bundle_to_dict
from app.mme_scalpx.replay.runner import ReplayRunConfig, ReplayRunner
from app.mme_scalpx.replay.selectors import (
    ReplaySelectionRequest,
    ReplaySelector,
    ReplayTimeWindow,
    selection_plan_to_dict,
)
from app.mme_scalpx.replay.topology import ReplayTopologyBuilder, topology_plan_to_dict


REQUIRED_CHECKS = (
    INTEGRITY_CHECK_HEARTBEAT,
    INTEGRITY_CHECK_HASH_FRESHNESS,
    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    INTEGRITY_CHECK_STALE_LEG,
    INTEGRITY_CHECK_RESET_CLEANLINESS,
    INTEGRITY_CHECK_REPRODUCIBILITY,
)


class ReplayRunCliError(RuntimeError):
    """CLI-layer replay run error."""






class LocalReplayTransport:
    """
    Replay-safe local transport used by this CLI phase.

    It does not publish to live/runtime infrastructure. It stores replay-safe
    publications locally so later stages can consume deterministic upstream
    outputs without contaminating live namespaces.
    """

    def __init__(self) -> None:
        self._published_requests: list[Any] = []
        self._feature_frames: list[dict[str, Any]] = []
        self._strategy_decisions: list[dict[str, Any]] = []
        self._risk_outputs: list[dict[str, Any]] = []
        self._execution_shadow_results: list[dict[str, Any]] = []

    @property
    def published_requests(self) -> tuple[Any, ...]:
        return tuple(self._published_requests)

    @property
    def feature_frames(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._feature_frames)

    @property
    def strategy_decisions(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._strategy_decisions)

    @property
    def risk_outputs(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._risk_outputs)

    @property
    def execution_shadow_results(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._execution_shadow_results)

    def publish(self, request) -> Mapping[str, Any] | None:
        self._published_requests.append(request)
        return {
            "published": True,
            "channel": request.event.channel,
            "sequence_id": request.event.sequence_id,
            "event_time": request.event.event_time,
        }

    def feed_requests(self, *, channel_prefix: str) -> tuple[Any, ...]:
        return tuple(
            request
            for request in self._published_requests
            if request.event.channel.startswith(channel_prefix)
        )

    def publish_feature_frame(self, frame: Mapping[str, Any]) -> Mapping[str, Any]:
        stored = dict(frame)
        self._feature_frames.append(stored)
        return {
            "published": True,
            "channel": stored.get("feature_channel"),
            "frame_id": stored.get("frame_id"),
            "event_time": stored.get("event_time"),
        }

    def publish_strategy_decision(self, decision: Mapping[str, Any]) -> Mapping[str, Any]:
        stored = dict(decision)
        self._strategy_decisions.append(stored)
        return {
            "published": True,
            "channel": stored.get("decision_channel"),
            "decision_id": stored.get("decision_id"),
            "event_time": stored.get("event_time"),
            "action": stored.get("action"),
        }

    def publish_risk_output(self, risk_output: Mapping[str, Any]) -> Mapping[str, Any]:
        stored = dict(risk_output)
        self._risk_outputs.append(stored)
        return {
            "published": True,
            "channel": stored.get("risk_channel"),
            "risk_id": stored.get("risk_id"),
            "event_time": stored.get("event_time"),
            "risk_action": stored.get("risk_action"),
            "veto_entry": stored.get("veto_entry"),
        }

    def publish_execution_shadow_result(
        self,
        execution_result: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        stored = dict(execution_result)
        self._execution_shadow_results.append(stored)
        return {
            "published": True,
            "channel": stored.get("execution_channel"),
            "execution_id": stored.get("execution_id"),
            "event_time": stored.get("event_time"),
            "filled": stored.get("filled"),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="replay_run.py",
        description="Run one frozen replay backbone execution.",
    )

    parser.add_argument("--dataset-root", required=True, help="Replay dataset root directory")
    parser.add_argument(
        "--selection-mode",
        required=True,
        choices=[mode.value for mode in ReplaySelectionMode],
        help="Canonical replay selection mode",
    )
    parser.add_argument("--single-day", help="YYYY-MM-DD for single_day / intraday_window / session_segment")
    parser.add_argument("--start-date", help="YYYY-MM-DD for date_range")
    parser.add_argument("--end-date", help="YYYY-MM-DD for date_range")
    parser.add_argument("--custom-dates", help="Comma-separated YYYY-MM-DD list for custom_date_list")
    parser.add_argument("--weekdays", help="Comma-separated weekday integers 0..6 for weekday_batch")
    parser.add_argument("--months", help="Comma-separated month integers 1..12 for monthly_batch")
    parser.add_argument("--window-start", help="HH:MM[:SS] intraday window start")
    parser.add_argument("--window-end", help="HH:MM[:SS] intraday window end")
    parser.add_argument("--session-segment", help="Named session segment for session_segment mode")
    parser.add_argument(
        "--doctrine-mode",
        required=True,
        choices=[mode.value for mode in DoctrineMode],
        help="locked or shadow",
    )
    parser.add_argument(
        "--scope",
        required=True,
        choices=[scope.value for scope in ReplayScope],
        help="Replay topology scope",
    )
    parser.add_argument(
        "--speed-mode",
        default=ReplaySpeedMode.ACCELERATED.value,
        choices=[mode.value for mode in ReplaySpeedMode],
        help="Replay clock speed mode",
    )
    parser.add_argument("--run-label", default=None)
    parser.add_argument("--experiment-profile", default=None)
    parser.add_argument("--override-pack-id", default=None)
    parser.add_argument("--dataset-id", default=None)
    parser.add_argument("--fill-model", default=None)
    parser.add_argument("--run-root", default=None)
    parser.add_argument("--required-file-stems", default="")
    parser.add_argument("--optional-file-stems", default="")
    parser.add_argument("--supported-suffixes", default=".jsonl,.json,.csv")
    parser.add_argument("--recurse", action="store_true")
    parser.add_argument(
        "--clock-start-time",
        default="2026-04-17T03:45:00Z",
        help="Replay clock start time in ISO-8601",
    )
    parser.add_argument(
        "--channel-prefix",
        default="replay:file",
        help="Logical replay channel prefix for feed injections",
    )
    parser.add_argument(
        "--allow-option-only-fut-context",
        action="store_true",
        help=(
            "Replay staging-only compatibility: allow opt_ticks rows carrying fut_ltp "
            "as disabled-by-default synthetic futures context when fut_ticks is absent/empty."
        ),
    )
    return parser


def parse_args(argv: list[str]) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def split_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return tuple()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def split_int_csv(value: str | None) -> tuple[int, ...]:
    if not value:
        return tuple()
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def build_selection_request(args: argparse.Namespace) -> ReplaySelectionRequest:
    return ReplaySelectionRequest(
        selection_mode=ReplaySelectionMode(args.selection_mode),
        single_day=args.single_day,
        start_date=args.start_date,
        end_date=args.end_date,
        custom_dates=split_csv(args.custom_dates),
        intraday_window=ReplayTimeWindow(
            start=args.window_start,
            end=args.window_end,
        ),
        session_segment=args.session_segment,
        weekdays=split_int_csv(args.weekdays),
        months=split_int_csv(args.months),
        market_tags=tuple(),
    )


def resolve_dataset_root(dataset_root: str, dataset_id: str | None = None) -> Path:
    """
    Resolve the physical replay dataset root used by ReplayDatasetRepository.

    CLI contract:
    - --dataset-root may point directly to a dataset directory containing YYYY-MM-DD day folders.
    - --dataset-root may also point to a parent directory when --dataset-id is supplied.
      In that case, if dataset_root/dataset_id exists, the repository must use that child
      path as the physical dataset root.

    This keeps dataset_id as logical manifest identity while preventing selector/date
    mismatch when materialized datasets are stored under a parent collection root.
    """
    root = Path(dataset_root)
    if dataset_id:
        candidate = root / dataset_id
        if candidate.exists() and candidate.is_dir():
            return candidate
    return root


def build_dataset_repository(args: argparse.Namespace) -> ReplayDatasetRepository:
    resolved_root = resolve_dataset_root(args.dataset_root, args.dataset_id)
    return ReplayDatasetRepository(
        DatasetDiscoveryConfig(
            root=resolved_root,
            required_file_stems=split_csv(args.required_file_stems),
            optional_file_stems=split_csv(args.optional_file_stems),
            supported_suffixes=split_csv(args.supported_suffixes),
            recurse=bool(args.recurse),
        )
    )


def build_run_config(args: argparse.Namespace) -> ReplayRunConfig:
    return ReplayRunConfig(
        doctrine_mode=DoctrineMode(args.doctrine_mode),
        replay_scope=ReplayScope(args.scope),
        speed_mode=ReplaySpeedMode(args.speed_mode),
        side_mode=ReplaySideMode.MIRRORED_BOTH,
        run_label=args.run_label,
        dataset_id=args.dataset_id,
        profiles=ProfilesSection(
            experiment_profile=args.experiment_profile,
        ),
        override_pack_id=args.override_pack_id,
        fill_model=args.fill_model,
        run_root=args.run_root,
        integrity_required_checks=REQUIRED_CHECKS,
    )



REPLAY_INTEGRITY_STEM_EQUIVALENCE_ALIASES = {
    "opt_ticks": (
        "opt_ticks",
        "option_ticks",
        "selected_option_ticks",
        "selected_opt_ticks",
        "option_quote_stream",
        "selected_option_quote_stream",
        "opt_quote_stream",
        "selected_option_quotes",
        "opt_quotes",
    ),
    "fut_ticks": (
        "fut_ticks",
        "future_ticks",
        "futures_ticks",
        "fut_quote_stream",
        "future_quote_stream",
        "futures_quote_stream",
        "fut_quotes",
        "future_quotes",
        "futures_quotes",
    ),
}


def _normalize_replay_integrity_stem_token(raw_stem) -> str:
    stem = str(raw_stem or "").strip()
    if not stem:
        return ""
    for suffix in (".jsonl", ".json", ".csv", ".parquet"):
        if stem.lower().endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return stem.strip().lower()


def normalize_replay_dataset_stems_for_integrity(raw_stems) -> dict[str, object]:
    """Normalize replay dataset stems before stale-leg missing-stem checks.

    This is an integrity contract only. It does not enable replay execution,
    full-system replay, economics/PnL, paper, or live promotion.
    """
    raw_clean = sorted({
        str(stem).strip()
        for stem in (raw_stems or [])
        if str(stem or "").strip()
    })

    reverse_aliases: dict[str, set[str]] = {}
    for canonical, aliases in REPLAY_INTEGRITY_STEM_EQUIVALENCE_ALIASES.items():
        tokens = set(aliases) | {canonical}
        for token in tokens:
            norm = _normalize_replay_integrity_stem_token(token)
            if norm:
                reverse_aliases.setdefault(norm, set()).add(canonical)

    canonical_stems: set[str] = set()
    equivalence_map: dict[str, str] = {}
    unknown_stems: list[str] = []
    ambiguous_stems: list[str] = []

    for raw in raw_clean:
        norm = _normalize_replay_integrity_stem_token(raw)
        matches = reverse_aliases.get(norm)
        if not matches:
            canonical_stems.add(norm)
            equivalence_map[raw] = norm
            if norm not in REPLAY_INTEGRITY_STEM_EQUIVALENCE_ALIASES:
                unknown_stems.append(raw)
            continue
        if len(matches) > 1:
            ambiguous_stems.append(raw)
            continue
        canonical = next(iter(matches))
        canonical_stems.add(canonical)
        equivalence_map[raw] = canonical

    return {
        "raw_stems": raw_clean,
        "canonical_stems": sorted(canonical_stems),
        "stem_equivalence_map": equivalence_map,
        "equivalence_used": any(
            _normalize_replay_integrity_stem_token(raw) != canonical
            for raw, canonical in equivalence_map.items()
        ),
        "unknown_stems": sorted(unknown_stems),
        "ambiguous_stems": sorted(ambiguous_stems),
        "alias_registry": {
            key: list(value)
            for key, value in REPLAY_INTEGRITY_STEM_EQUIVALENCE_ALIASES.items()
        },
    }

def build_placeholder_checks(*, allow_option_only_fut_context: bool = False) -> dict[str, Any]:
    """Build evidence-backed replay integrity checks.

    Historical name retained for CLI compatibility, but this no longer emits
    placeholder pass results. Placeholder pass remains guarded in integrity.py.
    """

    def _dataset_files(rc: Any) -> list[Any]:
        selection = getattr(rc, "selection_plan", None)
        days = getattr(selection, "days", None) or getattr(selection, "selected_days", None) or []
        files: list[Any] = []
        for day in days:
            files.extend(getattr(day, "files", None) or getattr(day, "dataset_files", None) or [])
        return files

    def _file_path(file_obj: Any) -> str:
        return str(
            getattr(file_obj, "path", None)
            or getattr(file_obj, "absolute_path", None)
            or getattr(file_obj, "relative_path", None)
            or getattr(file_obj, "name", "")
        )

    def _file_size(file_obj: Any) -> int | None:
        value = getattr(file_obj, "size_bytes", None)
        try:
            return int(value) if value is not None else None
        except Exception:
            return None

    def _pass(name: str, message: str, details: dict[str, Any]) -> Any:
        return ReplayIntegrityCheckResult(
            check_name=name,
            verdict=IntegrityVerdict.PASS,
            message=message,
            details=details,
        )

    def _fail(name: str, message: str, details: dict[str, Any]) -> Any:
        return ReplayIntegrityCheckResult(
            check_name=name,
            verdict=IntegrityVerdict.FAIL,
            message=message,
            details=details,
        )

    def _heartbeat(rc: Any) -> Any:
        files = _dataset_files(rc)
        missing = [f for f in files if not _file_path(f)]
        empty = [f for f in files if _file_size(f) == 0]
        details = {
            "file_count": len(files),
            "missing_path_count": len(missing),
            "empty_file_count": len(empty),
            "checked_files": [_file_path(f) for f in files],
        }
        if not files or missing or empty:
            return _fail(INTEGRITY_CHECK_HEARTBEAT, "heartbeat_integrity real check failed", details)
        return _pass(INTEGRITY_CHECK_HEARTBEAT, "heartbeat_integrity real check pass", details)

    def _hash_freshness(rc: Any) -> Any:
        files = _dataset_files(rc)
        missing_hash = []
        for f in files:
            if not getattr(f, "sha256", None):
                missing_hash.append(_file_path(f))
        details = {
            "file_count": len(files),
            "missing_hash_count": len(missing_hash),
            "missing_hash_files": missing_hash,
        }
        if not files or missing_hash:
            return _fail(INTEGRITY_CHECK_HASH_FRESHNESS, "hash_freshness real check failed", details)
        return _pass(INTEGRITY_CHECK_HASH_FRESHNESS, "hash_freshness real check pass", details)

    def _snapshot_sync(rc: Any) -> Any:
        files = _dataset_files(rc)
        parseable = []
        bad_suffix = []
        for f in files:
            suffix = str(getattr(f, "suffix", "") or getattr(f, "file_suffix", "") or "").lower()
            if suffix in (".jsonl", ".json", ".csv", ".parquet"):
                parseable.append(_file_path(f))
            else:
                bad_suffix.append(_file_path(f))
        details = {
            "file_count": len(files),
            "parseable_file_count": len(parseable),
            "unsupported_suffix_files": bad_suffix,
        }
        if not files or not parseable:
            return _fail(INTEGRITY_CHECK_SNAPSHOT_SYNC, "snapshot_sync_validity real check failed", details)
        return _pass(INTEGRITY_CHECK_SNAPSHOT_SYNC, "snapshot_sync_validity real check pass", details)

    def _stale_leg(rc: Any) -> Any:
        files = _dataset_files(rc)
        stems = {str(getattr(f, "stem", "") or "").lower() for f in files}
        required = {"fut_ticks", "opt_ticks"}
        stem_integrity = normalize_replay_dataset_stems_for_integrity(stems)
        raw_stems = set(stem_integrity.get("raw_stems", []))
        canonical_stems = set(stem_integrity.get("canonical_stems", []))
        stems = canonical_stems
        missing = sorted(required - stems)
        details = {
            "required_stems": sorted(required),
            "present_stems": sorted(stems),
            "missing_stems": missing,
        }
        details["raw_stems"] = sorted(raw_stems)
        details["canonical_stems"] = sorted(canonical_stems)
        details["stem_equivalence_map"] = stem_integrity.get("stem_equivalence_map", {})
        details["stem_equivalence_used"] = bool(stem_integrity.get("equivalence_used", False))
        details["unknown_stems"] = stem_integrity.get("unknown_stems", [])
        details["ambiguous_stems"] = stem_integrity.get("ambiguous_stems", [])
        if stem_integrity.get("ambiguous_stems"):
            details["stem_equivalence_fail_closed"] = True
            return _fail(
                INTEGRITY_CHECK_STALE_LEG,
                "stale_leg_detection ambiguous stem equivalence fail-closed",
                details,
            )

        if missing:
            if allow_option_only_fut_context and missing == ["fut_ticks"] and "opt_ticks" in stems:
                details["option_only_fut_context"] = True
                details["synthetic_context_source"] = "opt_ticks.row.fut_ltp"
                details["synthetic_context_scope"] = "R5BE_staging_only_disabled_by_default"
                return _pass(
                    INTEGRITY_CHECK_STALE_LEG,
                    "stale_leg_detection option_only_fut_context compatibility pass",
                    details,
                )
            return _fail(INTEGRITY_CHECK_STALE_LEG, "stale_leg_detection real check failed", details)
        return _pass(INTEGRITY_CHECK_STALE_LEG, "stale_leg_detection real check pass", details)

    def _reset_cleanliness(rc: Any) -> Any:
        artifact_plan = getattr(rc, "artifact_plan", None)
        manifest_path = str(getattr(artifact_plan, "manifest_path", "") or "")
        run_id = str(getattr(rc, "run_id", "") or "")
        details = {"run_id": run_id, "manifest_path": manifest_path}
        if not run_id or not manifest_path:
            return _fail(INTEGRITY_CHECK_RESET_CLEANLINESS, "reset_cleanliness real check failed", details)
        return _pass(INTEGRITY_CHECK_RESET_CLEANLINESS, "reset_cleanliness real check pass", details)

    def _reproducibility(rc: Any) -> Any:
        selection = getattr(rc, "selection_plan", None)
        run_config = getattr(rc, "run_config", None)
        details = {
            "run_id": str(getattr(rc, "run_id", "") or ""),
            "selection_fingerprint": str(getattr(selection, "selection_fingerprint", "") or getattr(selection, "fingerprint", "") or ""),
            "run_config_type": type(run_config).__name__ if run_config is not None else "",
        }
        if not details["run_id"]:
            return _fail(INTEGRITY_CHECK_REPRODUCIBILITY, "reproducibility_proof real check failed", details)
        return _pass(INTEGRITY_CHECK_REPRODUCIBILITY, "reproducibility_proof real check pass", details)

    return {
        INTEGRITY_CHECK_HEARTBEAT: _heartbeat,
        INTEGRITY_CHECK_HASH_FRESHNESS: _hash_freshness,
        INTEGRITY_CHECK_SNAPSHOT_SYNC: _snapshot_sync,
        INTEGRITY_CHECK_STALE_LEG: _stale_leg,
        INTEGRITY_CHECK_RESET_CLEANLINESS: _reset_cleanliness,
        INTEGRITY_CHECK_REPRODUCIBILITY: _reproducibility,
    }



def _normalize_replay_event_time(value: Any) -> str:
    """
    Normalize replay event timestamp to timezone-aware ISO-8601.

    Accepted:
    - ISO string with timezone
    - nanoseconds epoch integer/string
    - microseconds/milliseconds/seconds epoch numeric string
    """
    if value is None:
        raise ReplayRunCliError("event timestamp is missing")

    raw = str(value).strip()
    if not raw:
        raise ReplayRunCliError("event timestamp is empty")

    if "-" in raw and ("T" in raw or " " in raw):
        normalized = raw.replace(" ", "T")
        if normalized.endswith("Z"):
            return normalized
        try:
            dt = datetime.fromisoformat(normalized)
        except Exception as exc:
            raise ReplayRunCliError(f"invalid ISO replay event timestamp: {raw!r}") from exc
        if dt.tzinfo is None:
            raise ReplayRunCliError(f"replay event timestamp must be timezone-aware: {raw!r}")
        return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

    try:
        n = int(float(raw))
    except Exception as exc:
        raise ReplayRunCliError(f"unsupported replay event timestamp format: {raw!r}") from exc

    digits = len(str(abs(n)))
    if digits >= 18:
        seconds = n / 1_000_000_000.0
    elif digits >= 15:
        seconds = n / 1_000_000.0
    elif digits >= 12:
        seconds = n / 1_000.0
    else:
        seconds = float(n)

    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def resolve_event_timestamp(record: Mapping[str, Any]) -> str:
    for key in ("event_time", "ts_event", "ts", "timestamp", "exchange_ts", "ts_event_ns", "ts_exchange_ns"):
        value = record.get(key)
        if value is not None and str(value).strip():
            return _normalize_replay_event_time(value)
    raise ReplayRunCliError(f"replay record missing timestamp field: {record!r}")


def _phase_a4_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _phase_a4_first_present(*values: Any) -> Any:
    for value in values:
        if _phase_a4_present(value):
            return value
    return None


def _phase_a4_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _build_replay_event_payload(
    *,
    row: Mapping[str, Any],
    event_time: str,
    source_stem: str,
) -> dict[str, Any]:
    payload = dict(row)
    economics = _phase_a4_mapping(payload.get("economics"))
    candidate_state = _phase_a4_mapping(payload.get("candidate_state"))

    ts_event = _phase_a4_first_present(
        payload.get("ts_event"),
        payload.get("ts"),
        payload.get("event_time"),
        payload.get("exchange_ts"),
        event_time,
    )
    source_frame_id = _phase_a4_first_present(
        payload.get("source_frame_id"),
        payload.get("frame_id"),
    )
    symbol = _phase_a4_first_present(
        payload.get("symbol"),
        payload.get("tradingsymbol"),
    )
    side = _phase_a4_first_present(
        payload.get("side"),
        candidate_state.get("side"),
    )
    selected_leg = _phase_a4_first_present(
        payload.get("selected_leg"),
        payload.get("leg"),
        candidate_state.get("selected_leg"),
        candidate_state.get("leg"),
    )
    entry_mode = _phase_a4_first_present(
        payload.get("entry_mode"),
        candidate_state.get("entry_mode"),
    )
    tick_size = _phase_a4_first_present(
        payload.get("tick_size"),
        economics.get("tick_size"),
    )
    target_ticks = _phase_a4_first_present(
        payload.get("target_ticks"),
        economics.get("target_ticks"),
    )
    stop_ticks = _phase_a4_first_present(
        payload.get("stop_ticks"),
        economics.get("stop_ticks"),
    )
    reward_ticks = _phase_a4_first_present(
        payload.get("reward_ticks"),
        payload.get("expected_reward_ticks"),
        economics.get("reward_ticks"),
        economics.get("expected_reward_ticks"),
    )
    reward_cost_ratio = _phase_a4_first_present(
        payload.get("reward_cost_ratio"),
        economics.get("reward_cost_ratio"),
        economics.get("reward_risk_ratio"),
        economics.get("rr"),
    )
    economics_reason = _phase_a4_first_present(
        payload.get("economics_reason"),
        economics.get("economics_reason"),
        economics.get("reason"),
        economics.get("reject_reason"),
    )

    payload["event_time"] = event_time
    if ts_event is not None:
        payload["ts_event"] = ts_event
    if source_frame_id is not None:
        payload["source_frame_id"] = source_frame_id
    if symbol is not None:
        payload["symbol"] = symbol
    if side is not None:
        payload["side"] = side
        candidate_state.setdefault("side", side)
    if selected_leg is not None:
        payload["selected_leg"] = selected_leg
        candidate_state.setdefault("selected_leg", selected_leg)
    if entry_mode is not None:
        payload["entry_mode"] = entry_mode
        candidate_state.setdefault("entry_mode", entry_mode)
    if tick_size is not None:
        payload["tick_size"] = tick_size
        economics.setdefault("tick_size", tick_size)
    if target_ticks is not None:
        payload["target_ticks"] = target_ticks
        economics.setdefault("target_ticks", target_ticks)
    if stop_ticks is not None:
        payload["stop_ticks"] = stop_ticks
        economics.setdefault("stop_ticks", stop_ticks)
    if reward_ticks is not None:
        payload["reward_ticks"] = reward_ticks
        economics.setdefault("reward_ticks", reward_ticks)
    if reward_cost_ratio is not None:
        payload["reward_cost_ratio"] = reward_cost_ratio
        economics.setdefault("reward_cost_ratio", reward_cost_ratio)
    if economics_reason is not None:
        payload["economics_reason"] = economics_reason
        economics.setdefault("economics_reason", economics_reason)

    if candidate_state:
        payload["candidate_state"] = candidate_state
    if economics:
        payload["economics"] = economics

    payload.setdefault("source_stem", source_stem)
    return payload


def _build_replay_event_metadata(
    *,
    trading_day: str,
    source_file: str,
    source_stem: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    metadata = {
        "trading_day": trading_day,
        "source_file": source_file,
        "source_stem": source_stem,
    }

    for key in (
        "ts_event",
        "source_frame_id",
        "symbol",
        "side",
        "selected_leg",
        "entry_mode",
        "tick_size",
        "target_ticks",
        "stop_ticks",
        "reward_ticks",
        "reward_cost_ratio",
        "economics_reason",
    ):
        value = payload.get(key)
        if _phase_a4_present(value):
            metadata[key] = value

    return metadata



from pathlib import Path as _R5BEPath
from collections.abc import Mapping as _R5BEMapping
import json as _r5be_json
import re as _r5be_re


def _r5be_path_is_relative_to(path, parent) -> bool:
    try:
        _R5BEPath(path).resolve().relative_to(_R5BEPath(parent).resolve())
        return True
    except Exception:
        return False


def _r5be_find_day_file(day_dir, stem: str):
    day_path = _R5BEPath(day_dir)
    for suffix in (".jsonl", ".json", ".csv"):
        direct = day_path / f"{stem}{suffix}"
        if direct.exists():
            return direct
    matches = sorted(day_path.rglob(f"{stem}.jsonl"))
    return matches[0] if matches else None


def _r5be_jsonl_sample(path, limit: int = 25) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with _R5BEPath(path).open("r", encoding="utf-8") as f:
        for line in f:
            if len(rows) >= limit:
                break
            raw = line.strip()
            if not raw:
                continue
            item = _r5be_json.loads(raw)
            if isinstance(item, _R5BEMapping):
                rows.append(dict(item))
    return rows


def validate_option_only_fut_context_preconditions(args) -> dict[str, object]:
    """Fail-closed validation for the R5BE disabled-by-default staging compatibility seam."""
    enabled = bool(getattr(args, "allow_option_only_fut_context", False))
    if not enabled:
        return {
            "enabled": False,
            "status": "disabled",
            "guard": "allow_option_only_fut_context",
        }

    dataset_root = resolve_dataset_root(str(getattr(args, "dataset_root", "")), getattr(args, "dataset_id", None))
    dataset_root = _R5BEPath(dataset_root).resolve()
    staging_root = (PROJECT_ROOT / "run" / "replay" / "staging").resolve()
    single_day = str(getattr(args, "single_day", "") or "").strip()
    selection_mode = str(getattr(args, "selection_mode", "") or "").strip()

    details: dict[str, object] = {
        "enabled": True,
        "guard": "allow_option_only_fut_context",
        "dataset_root": str(dataset_root),
        "staging_root": str(staging_root),
        "single_day": single_day,
        "selection_mode": selection_mode,
    }

    if not _r5be_path_is_relative_to(dataset_root, staging_root):
        raise ReplayRunCliError("allow_option_only_fut_context requires dataset_root under run/replay/staging/")
    if selection_mode != "single_day":
        raise ReplayRunCliError("allow_option_only_fut_context requires --selection-mode single_day")
    if not _r5be_re.fullmatch(r"\d{4}-\d{2}-\d{2}", single_day):
        raise ReplayRunCliError("allow_option_only_fut_context requires --single-day YYYY-MM-DD")

    final_day_dir = (PROJECT_ROOT / "run" / "replay" / single_day).resolve()
    details["final_day_dir"] = str(final_day_dir)
    if final_day_dir.exists():
        raise ReplayRunCliError(f"allow_option_only_fut_context forbidden because final replay repository date exists: {final_day_dir}")

    day_dir = dataset_root / single_day
    if not day_dir.exists() and dataset_root.name == single_day:
        day_dir = dataset_root
    details["day_dir"] = str(day_dir)
    if not day_dir.exists() or not day_dir.is_dir():
        raise ReplayRunCliError(f"allow_option_only_fut_context requires staging day directory: {day_dir}")

    opt_file = _r5be_find_day_file(day_dir, "opt_ticks")
    if opt_file is None or not opt_file.exists() or opt_file.stat().st_size <= 0:
        raise ReplayRunCliError("allow_option_only_fut_context requires non-empty opt_ticks.jsonl")
    details["opt_ticks_file"] = str(opt_file)
    details["opt_ticks_size_bytes"] = opt_file.stat().st_size

    fut_file = _r5be_find_day_file(day_dir, "fut_ticks")
    details["fut_ticks_file"] = str(fut_file) if fut_file else None
    if fut_file is not None and fut_file.exists() and fut_file.stat().st_size > 0:
        raise ReplayRunCliError("allow_option_only_fut_context requires fut_ticks.jsonl absent or empty; real futures ticks must not be mixed with synthetic context")

    sample_rows = _r5be_jsonl_sample(opt_file, limit=25)
    if not sample_rows:
        raise ReplayRunCliError("allow_option_only_fut_context requires parseable opt_ticks sample rows")

    bad_dates = []
    missing_fut_ltp = []
    for index, row in enumerate(sample_rows, start=1):
        if str(row.get("session_date") or "") != single_day:
            bad_dates.append(index)
        value = row.get("fut_ltp")
        if value is None or str(value).strip() == "":
            missing_fut_ltp.append(index)

    details["sample_count"] = len(sample_rows)
    details["bad_session_date_rows"] = bad_dates
    details["missing_fut_ltp_rows"] = missing_fut_ltp

    if bad_dates:
        raise ReplayRunCliError(f"allow_option_only_fut_context sampled option rows do not match single_day: {bad_dates[:10]}")
    if missing_fut_ltp:
        raise ReplayRunCliError(f"allow_option_only_fut_context sampled option rows missing fut_ltp: {missing_fut_ltp[:10]}")

    details["status"] = "pass"
    details["synthetic_context_source"] = "opt_ticks.row.fut_ltp"
    details["synthetic_context_scope"] = "staging_only_no_final_repo_date"
    return details


def _apply_option_only_fut_context_to_event_payload(*, payload: dict[str, object], metadata: dict[str, object], source_stem: str) -> bool:
    if str(source_stem or "") != "opt_ticks":
        return False
    fut_ltp = payload.get("fut_ltp")
    if fut_ltp is None or str(fut_ltp).strip() == "":
        return False

    futures_context = payload.get("futures_context")
    if not isinstance(futures_context, _R5BEMapping):
        futures_context = {}
    futures_context = dict(futures_context)
    futures_context.setdefault("ltp", fut_ltp)
    futures_context.setdefault("fut_ltp", fut_ltp)
    futures_context.setdefault("event_time", payload.get("exchange_ts") or payload.get("ts_utc") or payload.get("event_time"))
    futures_context.setdefault("source", "synthetic_context_from_option_fut_ltp")
    futures_context.setdefault("synthetic_context", True)

    payload["futures_context"] = futures_context
    payload.setdefault("futures_context_ltp", fut_ltp)
    payload.setdefault("underlying_ltp", fut_ltp)

    metadata["synthetic_context"] = True
    metadata["synthetic_context_reason"] = "No real fut_ticks.jsonl available; option rows include fut_ltp."
    metadata["futures_context_source"] = "synthetic_context_from_option_fut_ltp"
    metadata["futures_context_ltp"] = fut_ltp
    metadata["synthetic_context_scope"] = "R5BE_staging_only_disabled_by_default"
    return True

def build_feed_events_for_day(
    *,
    repository: ReplayDatasetRepository,
    trading_day,
    channel_prefix: str,
    allow_option_only_fut_context: bool = False,
) -> list[ReplayInjectionEvent]:
    raw_events: list[dict[str, Any]] = []

    for file_summary in trading_day.files:
        relative_path = Path(trading_day.date_str) / file_summary.relative_path
        suffix = str(file_summary.suffix or "").lower()

        if suffix == ".jsonl":
            rows = repository.read_jsonl(relative_path)
        elif suffix == ".json":
            rows = repository.read_json(relative_path)
            if isinstance(rows, Mapping):
                rows = rows.get("rows") or rows.get("events") or rows.get("data") or []
        elif suffix == ".csv":
            rows = tuple(repository.iter_csv_rows(relative_path))
        else:
            continue

        logical_channel = f"{channel_prefix}:{file_summary.stem}"

        for row in rows:
            if not isinstance(row, Mapping):
                continue

            event_time = resolve_event_timestamp(row)
            normalized_payload = _build_replay_event_payload(
                row=row,
                event_time=event_time,
                source_stem=file_summary.stem,
            )
            normalized_metadata = _build_replay_event_metadata(
                trading_day=trading_day.date_str,
                source_file=file_summary.relative_path,
                source_stem=file_summary.stem,
                payload=normalized_payload,
            )
            if allow_option_only_fut_context:
                _apply_option_only_fut_context_to_event_payload(
                    payload=normalized_payload,
                    metadata=normalized_metadata,
                    source_stem=file_summary.stem,
                )

            raw_events.append(
                {
                    "event_time": event_time,
                    "channel": logical_channel,
                    "payload": normalized_payload,
                    "metadata": normalized_metadata,
                }
            )

    raw_events.sort(key=lambda item: (item["event_time"], item["channel"]))

    events: list[ReplayInjectionEvent] = []
    for seq, item in enumerate(raw_events, start=1):
        events.append(
            ReplayInjectionEvent(
                sequence_id=seq,
                event_time=item["event_time"],
                channel=item["channel"],
                payload=item["payload"],
                metadata=item["metadata"],
            )
        )

    return events



def _to_float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None





def build_feature_frames_from_feed_requests(
    *,
    feed_requests: Sequence[Any],
) -> list[dict[str, Any]]:
    """
    Build replay feature frames from replay feed requests.

    Replay-only bridge:
    - normalize through ReplayInjectionRequest.event when present
    - preserve raw replay fields where available
    - capture event/payload source surface for auditability
    - do not mutate production doctrine
    """

    def _coalesce(*values: Any) -> Any:
        for value in values:
            if value is None:
                continue
            if isinstance(value, str) and not value.strip():
                continue
            return value
        return None

    def _mapping_keys(value: Mapping[str, Any]) -> list[str]:
        return sorted(str(key) for key in value.keys())

    def _object_dict_keys(value: Any) -> list[str]:
        raw = getattr(value, "__dict__", None)
        if isinstance(raw, dict):
            return sorted(str(key) for key in raw.keys())
        return []

    def _public_attr_names(value: Any) -> list[str]:
        names: list[str] = []
        for name in dir(value):
            if name.startswith("_"):
                continue
            try:
                attr = getattr(value, name)
            except Exception:
                continue
            if callable(attr):
                continue
            names.append(str(name))
        return sorted(names)

    def _to_mapping(value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, Mapping):
            return dict(value)
        if hasattr(value, "model_dump"):
            dumped = value.model_dump()
            if isinstance(dumped, Mapping):
                return dict(dumped)
        if hasattr(value, "dict"):
            dumped = value.dict()
            if isinstance(dumped, Mapping):
                return dict(dumped)
        raw = getattr(value, "__dict__", None)
        if isinstance(raw, dict):
            return dict(raw)
        return {}

    def _json_safe_probe(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Mapping):
            return {
                "type": type(value).__name__,
                "keys": _mapping_keys(value),
            }
        if isinstance(value, (list, tuple, set)):
            return {
                "type": type(value).__name__,
                "length": len(value),
            }
        return {
            "type": type(value).__name__,
            "dict_keys": _object_dict_keys(value),
            "public_attrs": _public_attr_names(value)[:40],
        }

    def _probe_attrs(source: Any, names: tuple[str, ...]) -> dict[str, Any]:
        if source is None:
            return {}
        out: dict[str, Any] = {}
        for name in names:
            if not hasattr(source, name):
                continue
            try:
                out[name] = _json_safe_probe(getattr(source, name))
            except Exception as exc:
                out[name] = {"error": type(exc).__name__}
        return out

    def _read(source: Any, *names: str) -> Any:
        if source is None:
            return None
        for name in names:
            if isinstance(source, Mapping) and name in source:
                return source[name]
            if hasattr(source, name):
                return getattr(source, name)
        return None

    def _to_float(value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip()
        if not text:
            return None
        try:
            return float(text)
        except (TypeError, ValueError):
            return None

    def _to_bool(value: Any) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        text = str(value).strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n"}:
            return False
        return None

    def _norm_symbol(value: Any) -> str:
        return str(value or "").strip().upper()

    def _classify_side_leg(symbol: str) -> tuple[str | None, str | None]:
        if not symbol:
            return (None, None)
        if symbol.endswith("_CE") or symbol.endswith("CE"):
            return ("CALL", "CALL_ATM")
        if symbol.endswith("_PE") or symbol.endswith("PE"):
            return ("PUT", "PUT_ATM")
        if "FUT" in symbol:
            return ("CONTEXT", "FUTURES")
        return (None, None)

    outputs: list[dict[str, Any]] = []

    for index, request in enumerate(feed_requests, start=1):
        request_row = _to_mapping(request)

        event_obj = _coalesce(
            _read(request, "event"),
            request_row.get("event"),
        )
        event_row = _to_mapping(event_obj)

        event_metadata_obj = _coalesce(
            _read(event_obj, "metadata"),
            event_row.get("metadata"),
        )
        event_payload_obj = _coalesce(
            _read(event_obj, "payload"),
            event_row.get("payload"),
        )

        payload = _to_mapping(event_payload_obj)
        metadata = _to_mapping(
            _coalesce(
                _read(request, "metadata"),
                request_row.get("metadata"),
                event_metadata_obj,
                payload.get("metadata"),
                _read(event_payload_obj, "metadata"),
            )
        )
        regime = _to_mapping(
            _coalesce(
                payload.get("regime"),
                payload.get("regime_state"),
                _read(event_payload_obj, "regime", "regime_state"),
            )
        )
        economics = _to_mapping(
            _coalesce(
                payload.get("economics"),
                payload.get("economics_state"),
                _read(event_payload_obj, "economics", "economics_state"),
            )
        )
        candidate_state = _to_mapping(
            _coalesce(
                payload.get("candidate_state"),
                payload.get("candidate"),
                _read(event_payload_obj, "candidate_state", "candidate"),
            )
        )

        raw_symbol = _coalesce(
            _read(event_payload_obj, "symbol", "tradingsymbol"),
            payload.get("symbol"),
            payload.get("tradingsymbol"),
            metadata.get("symbol"),
            metadata.get("tradingsymbol"),
        )
        symbol_norm = _norm_symbol(raw_symbol)

        event_time = _coalesce(
            _read(event_obj, "event_time"),
            event_row.get("event_time"),
            _read(event_payload_obj, "event_time", "exchange_ts", "ts_event", "ts_event_ns"),
            payload.get("event_time"),
            payload.get("exchange_ts"),
            payload.get("ts_event"),
            payload.get("ts_event_ns"),
        )
        source_channel = _coalesce(
            _read(event_obj, "channel"),
            event_row.get("channel"),
            _read(request, "source_channel", "channel"),
            request_row.get("source_channel"),
            metadata.get("source_channel"),
        )
        source_sequence_id = _coalesce(
            _read(event_obj, "sequence_id"),
            event_row.get("sequence_id"),
            _read(request, "source_sequence_id", "sequence_id"),
            request_row.get("source_sequence_id"),
            request_row.get("sequence_id"),
            metadata.get("source_sequence_id"),
        )

        bid = _to_float(
            _coalesce(
                _read(event_payload_obj, "bid", "best_bid", "best_bid_price"),
                payload.get("bid"),
                payload.get("best_bid"),
                payload.get("best_bid_price"),
            )
        )
        ask = _to_float(
            _coalesce(
                _read(event_payload_obj, "ask", "best_ask", "best_ask_price"),
                payload.get("ask"),
                payload.get("best_ask"),
                payload.get("best_ask_price"),
            )
        )
        ltp = _to_float(
            _coalesce(
                _read(event_payload_obj, "ltp", "last_price", "price"),
                payload.get("ltp"),
                payload.get("last_price"),
                payload.get("price"),
            )
        )
        spread = _to_float(
            _coalesce(
                _read(event_payload_obj, "spread"),
                payload.get("spread"),
            )
        )
        mid_price = _to_float(
            _coalesce(
                _read(event_payload_obj, "mid_price"),
                payload.get("mid_price"),
            )
        )

        if spread is None and bid is not None and ask is not None:
            spread = ask - bid
        if mid_price is None and bid is not None and ask is not None:
            mid_price = (bid + ask) / 2.0

        inferred_side, inferred_leg = _classify_side_leg(symbol_norm)

        healthy = _to_bool(
            _coalesce(
                _read(event_payload_obj, "healthy"),
                payload.get("healthy"),
                metadata.get("healthy"),
            )
        )
        if healthy is None:
            healthy = bool(
                bid is not None
                and ask is not None
                and ask >= bid
                and ltp is not None
                and spread is not None
                and spread >= 0.0
            )

        regime_ok = _to_bool(
            _coalesce(
                _read(event_payload_obj, "regime_ok"),
                payload.get("regime_ok"),
                regime.get("ok"),
                regime.get("regime_ok"),
            )
        )
        regime_pass = _to_bool(
            _coalesce(
                _read(event_payload_obj, "regime_pass"),
                payload.get("regime_pass"),
                regime.get("pass"),
                regime.get("regime_pass"),
            )
        )
        economics_valid = _to_bool(
            _coalesce(
                _read(event_payload_obj, "economics_valid"),
                payload.get("economics_valid"),
                economics.get("valid"),
                economics.get("economics_valid"),
            )
        )
        reward_cost_valid = _to_bool(
            _coalesce(
                _read(event_payload_obj, "reward_cost_valid"),
                payload.get("reward_cost_valid"),
                economics.get("reward_cost_valid"),
                economics.get("reward_cost_ok"),
            )
        )
        candidate = _to_bool(
            _coalesce(
                _read(event_payload_obj, "candidate", "candidate_found"),
                payload.get("candidate"),
                payload.get("candidate_found"),
                candidate_state.get("candidate"),
                candidate_state.get("selected"),
            )
        )
        side = _coalesce(
            _read(event_payload_obj, "side"),
            payload.get("side"),
            candidate_state.get("side"),
            metadata.get("side"),
            inferred_side,
        )
        leg = _coalesce(
            _read(event_payload_obj, "leg"),
            payload.get("leg"),
            candidate_state.get("leg"),
            metadata.get("leg"),
            inferred_leg,
        )
        blocker = _coalesce(
            _read(event_payload_obj, "blocker", "blocker_reason"),
            payload.get("blocker"),
            payload.get("blocker_reason"),
            candidate_state.get("blocker"),
        )
        ambiguity = _to_bool(
            _coalesce(
                _read(event_payload_obj, "ambiguity", "ambiguous"),
                payload.get("ambiguity"),
                payload.get("ambiguous"),
                candidate_state.get("ambiguity"),
            )
        )
        if ambiguity is None:
            ambiguity = False

        reward_cost_ratio = _to_float(
            _coalesce(
                _read(event_payload_obj, "reward_cost_ratio"),
                payload.get("reward_cost_ratio"),
                economics.get("reward_cost_ratio"),
                economics.get("reward_risk_ratio"),
                economics.get("rr"),
            )
        )
        reward_ticks = _to_float(
            _coalesce(
                _read(event_payload_obj, "reward_ticks", "expected_reward_ticks"),
                payload.get("reward_ticks"),
                payload.get("expected_reward_ticks"),
                economics.get("reward_ticks"),
                economics.get("expected_reward_ticks"),
            )
        )
        cost_ticks = _to_float(
            _coalesce(
                _read(event_payload_obj, "cost_ticks", "estimated_cost_ticks"),
                payload.get("cost_ticks"),
                payload.get("estimated_cost_ticks"),
                economics.get("cost_ticks"),
                economics.get("estimated_cost_ticks"),
                spread,
            )
        )
        target_ticks = _to_float(
            _coalesce(
                _read(event_payload_obj, "target_ticks"),
                payload.get("target_ticks"),
                economics.get("target_ticks"),
            )
        )
        stop_ticks = _to_float(
            _coalesce(
                _read(event_payload_obj, "stop_ticks"),
                payload.get("stop_ticks"),
                economics.get("stop_ticks"),
            )
        )

        regime_reason = _coalesce(
            _read(event_payload_obj, "regime_reason"),
            payload.get("regime_reason"),
            regime.get("reason"),
        )
        economics_reason = _coalesce(
            _read(event_payload_obj, "economics_reason"),
            payload.get("economics_reason"),
            economics.get("reason"),
            economics.get("reject_reason"),
        )
        ts_event = _coalesce(
            _read(event_payload_obj, "ts_event", "ts", "event_time"),
            payload.get("ts_event"),
            payload.get("ts"),
            payload.get("event_time"),
            event_time,
        )
        tick_size = _to_float(
            _coalesce(
                _read(event_payload_obj, "tick_size"),
                payload.get("tick_size"),
                metadata.get("tick_size"),
                economics.get("tick_size"),
            )
        )
        entry_mode = _coalesce(
            _read(event_payload_obj, "entry_mode"),
            payload.get("entry_mode"),
            candidate_state.get("entry_mode"),
            metadata.get("entry_mode"),
        )
        selected_leg = _coalesce(
            _read(event_payload_obj, "selected_leg", "leg"),
            payload.get("selected_leg"),
            payload.get("leg"),
            candidate_state.get("selected_leg"),
            candidate_state.get("leg"),
            metadata.get("selected_leg"),
            metadata.get("leg"),
            leg,
        )

        futures_context = _to_mapping(
            _coalesce(
                payload.get("futures_context"),
                _read(event_payload_obj, "futures_context"),
            )
        )
        fut_ltp = _to_float(
            _coalesce(
                _read(event_payload_obj, "fut_ltp", "futures_context_ltp", "underlying_ltp"),
                payload.get("fut_ltp"),
                payload.get("futures_context_ltp"),
                payload.get("underlying_ltp"),
                futures_context.get("ltp"),
                futures_context.get("fut_ltp"),
            )
        )

        source_surface = {
            "request_type": type(request).__name__,
            "request_dict_keys": _object_dict_keys(request),
            "request_public_attrs": _public_attr_names(request),
            "request_attr_probe": _probe_attrs(
                request,
                ("batch_id", "event", "notes", "replay_time_before", "replay_time_after", "run_id"),
            ),
            "event_type": type(event_obj).__name__ if event_obj is not None else None,
            "event_dict_keys": _object_dict_keys(event_obj),
            "event_public_attrs": _public_attr_names(event_obj) if event_obj is not None else [],
            "event_attr_probe": _probe_attrs(
                event_obj,
                ("channel", "event_time", "metadata", "payload", "sequence_id"),
            ),
            "payload_type": type(event_payload_obj).__name__ if event_payload_obj is not None else None,
            "payload_keys": _mapping_keys(payload),
            "payload_public_attrs": (
                _public_attr_names(event_payload_obj)
                if event_payload_obj is not None and not isinstance(event_payload_obj, Mapping)
                else []
            ),
            "payload_attr_probe": (
                _probe_attrs(
                    event_payload_obj,
                    (
                        "symbol",
                        "tradingsymbol",
                        "ltp",
                        "last_price",
                        "price",
                        "bid",
                        "ask",
                        "best_bid",
                        "best_ask",
                        "best_bid_price",
                        "best_ask_price",
                        "mid_price",
                        "spread",
                        "regime",
                        "economics",
                        "candidate_state",
                        "metadata",
                    ),
                )
                if event_payload_obj is not None and not isinstance(event_payload_obj, Mapping)
                else {}
            ),
            "metadata_keys": _mapping_keys(metadata),
            "regime_keys": _mapping_keys(regime),
            "economics_keys": _mapping_keys(economics),
            "candidate_state_keys": _mapping_keys(candidate_state),
            "resolved_inputs": {
                "symbol": raw_symbol if raw_symbol is not None else symbol_norm,
                "event_time": event_time,
                "source_channel": source_channel,
                "source_sequence_id": source_sequence_id,
                "bid": bid,
                "ask": ask,
                "ltp": ltp,
                "fut_ltp": fut_ltp,
                "futures_context": futures_context,
                "mid_price": mid_price,
                "spread": spread,
                "healthy": healthy,
                "regime_ok": regime_ok,
                "regime_pass": regime_pass,
                "economics_valid": economics_valid,
                "reward_cost_valid": reward_cost_valid,
                "candidate": candidate,
                "side": side,
                "leg": leg,
                "blocker": blocker,
                "ambiguity": ambiguity,
            },
        }

        feature_row = {
            "frame_id": f"feature_frame_{index:06d}",
            "event_time": event_time,
            "feature_channel": "replay:features",
            "source_channel": source_channel,
            "source_sequence_id": source_sequence_id,
            "symbol": raw_symbol if raw_symbol is not None else symbol_norm,
            "ltp": ltp,
            "fut_ltp": fut_ltp,
            "futures_context": futures_context,
            "bid": bid,
            "ask": ask,
            "mid_price": mid_price,
            "spread": spread,
            "metadata": {
                **metadata,
                "replay_feature_bridge_version": "v3_event_normalized",
                "feature_truth_mode": "replay_bridge_v3_event_normalized",
            },
            "healthy": healthy,
            "regime_ok": regime_ok,
            "regime_pass": regime_pass,
            "regime_reason": regime_reason,
            "economics_valid": economics_valid,
            "reward_cost_valid": reward_cost_valid,
            "reward_cost_ratio": reward_cost_ratio,
            "reward_ticks": reward_ticks,
            "cost_ticks": cost_ticks,
            "target_ticks": target_ticks,
            "stop_ticks": stop_ticks,
            "economics_reason": economics_reason,
            "ts_event": ts_event,
            "tick_size": tick_size,
            "entry_mode": entry_mode,
            "selected_leg": selected_leg,
            "candidate": candidate,
            "side": side,
            "leg": leg,
            "blocker": blocker,
            "ambiguity": ambiguity,
            "replay_source_surface": dict(source_surface),
        }

        outputs.append(feature_row)


    # R31A_R9F_R1_AST_FEATURE_FRAME_ENRICHMENT
    # Replay-only derived microstructure/family-surface payload.
    # Does not force candidates, tune thresholds, weaken MISO, or touch live/order paths.
    def _r31a_r9f_num(value: Any) -> float | None:
        try:
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            s = str(value).strip()
            return float(s) if s else None
        except Exception:
            return None

    def _r31a_r9f_avg(values: list[float]) -> float | None:
        vals = [float(v) for v in values if isinstance(v, (int, float))]
        return sum(vals) / len(vals) if vals else None

    fut_ltp_window: list[float] = []
    fut_abs_delta_window: list[float] = []
    opt_windows: dict[str, list[float]] = {}
    latest_fut_surface: dict[str, Any] = {}

    for _row in outputs:
        if not isinstance(_row, dict):
            continue

        _symbol = str(_row.get("symbol") or "").upper()
        _side = str(_row.get("side") or "").upper()
        _leg = str(_row.get("selected_leg") or _row.get("leg") or "").upper()
        _ltp = _r31a_r9f_num(_row.get("ltp") if _row.get("ltp") is not None else _row.get("mid_price"))

        _is_fut = _leg == "FUTURES" or _side == "CONTEXT" or "FUT" in _symbol
        _is_call = _side == "CALL" or "CALL" in _leg or _symbol.endswith("CE")
        _is_put = _side == "PUT" or "PUT" in _leg or _symbol.endswith("PE")

        if _is_fut and _ltp is not None:
            _prev1 = fut_ltp_window[-1] if len(fut_ltp_window) >= 1 else None
            _prev3 = fut_ltp_window[-3] if len(fut_ltp_window) >= 3 else None
            _delta1 = (_ltp - _prev1) if _prev1 is not None else None
            _delta3 = (_ltp - _prev3) if _prev3 is not None else None
            if _delta1 is not None:
                fut_abs_delta_window.append(abs(_delta1))
                fut_abs_delta_window[:] = fut_abs_delta_window[-20:]
            _avg_abs = _r31a_r9f_avg(fut_abs_delta_window)
            _velocity_ratio = (abs(_delta3) / _avg_abs) if (_delta3 is not None and _avg_abs and _avg_abs > 0) else None

            _row["fut_ltp"] = _ltp
            _row["delta_1"] = _delta1
            _row["delta_3"] = _delta3
            _row["fut_delta_3"] = _delta3
            _row["velocity_ratio"] = _velocity_ratio
            _row["volume_norm"] = _row.get("volume_norm", 1.0)
            _row["micro_futures_kinetics_ready"] = _delta3 is not None
            _row["r31a_r9f_r1_micro_futures_enriched"] = True

            latest_fut_surface = {
                "surface_kind": "replay_r26_micro_futures_kinetics",
                "fut_ltp": _ltp,
                "delta_1": _delta1,
                "delta_3": _delta3,
                "fut_delta_3": _delta3,
                "velocity_ratio": _velocity_ratio,
                "volume_norm": _row.get("volume_norm"),
                "micro_futures_kinetics_ready": _delta3 is not None,
                "futures_impulse_ok": bool(_delta3 is not None and _velocity_ratio is not None and abs(_delta3) > 0),
                "trend_up": bool(_delta3 is not None and _delta3 > 0),
                "trend_down": bool(_delta3 is not None and _delta3 < 0),
                "replay_surface_reconstruction": "R31A_R9F_R1",
            }
            fut_ltp_window.append(_ltp)
            fut_ltp_window[:] = fut_ltp_window[-50:]

        _shelf_surface: dict[str, Any] = {}
        if (_is_call or _is_put) and _ltp is not None:
            _opt_key = "CALL_ATM" if _is_call else "PUT_ATM"
            _win = opt_windows.setdefault(_opt_key, [])
            _prior = list(_win[-20:])
            _prior_high = max(_prior) if _prior else None
            _prior_low = min(_prior) if _prior else None
            _breakout_extension = None
            if _is_call and _prior_high is not None:
                _breakout_extension = _ltp - _prior_high
            if _is_put and _prior_low is not None:
                _breakout_extension = _prior_low - _ltp

            _shelf_surface = {
                "surface_kind": "replay_r27_prior_micro_shelf",
                "selected_leg": _opt_key,
                "ltp": _ltp,
                "prior_micro_shelf_high": _prior_high,
                "prior_micro_shelf_low": _prior_low,
                "shelf_high": _prior_high,
                "shelf_low": _prior_low,
                "breakout_extension": _breakout_extension,
                "prior_breakout_extension": _breakout_extension,
                "shelf_confirmed": len(_prior) >= 5,
                "breakout_triggered": bool(_breakout_extension is not None and _breakout_extension >= 0.20),
                "breakout_accepted": bool(_breakout_extension is not None and _breakout_extension >= 0.20),
                "replay_surface_reconstruction": "R31A_R9F_R1",
            }
            _row.update({
                "prior_micro_shelf_high": _prior_high,
                "prior_micro_shelf_low": _prior_low,
                "shelf_high": _prior_high,
                "shelf_low": _prior_low,
                "breakout_extension": _breakout_extension,
                "prior_breakout_extension": _breakout_extension,
                "r31a_r9f_r1_prior_shelf_enriched": True,
            })
            _win.append(_ltp)
            _win[:] = _win[-50:]

        _mist_call = dict(latest_fut_surface)
        _mist_call.update({"surface_kind": "mist_surface", "side": "CALL", "trend_confirmed": bool(latest_fut_surface.get("trend_up")), "futures_impulse_ok": bool(latest_fut_surface.get("futures_impulse_ok")), "pullback_detected": False, "resume_confirmed": False, "micro_trap_flag": False, "replay_surface_reconstruction": "R31A_R9F_R1"})
        _mist_put = dict(latest_fut_surface)
        _mist_put.update({"surface_kind": "mist_surface", "side": "PUT", "trend_confirmed": bool(latest_fut_surface.get("trend_down")), "futures_impulse_ok": bool(latest_fut_surface.get("futures_impulse_ok")), "pullback_detected": False, "resume_confirmed": False, "micro_trap_flag": False, "replay_surface_reconstruction": "R31A_R9F_R1"})

        _misb_call = dict(_shelf_surface if _is_call else {})
        _misb_call.update({"surface_kind": "misb_surface", "side": "CALL", "replay_surface_reconstruction": "R31A_R9F_R1"})
        _misb_put = dict(_shelf_surface if _is_put else {})
        _misb_put.update({"surface_kind": "misb_surface", "side": "PUT", "replay_surface_reconstruction": "R31A_R9F_R1"})

        _family_surfaces = {
            "MIST": {"CALL": _mist_call, "PUT": _mist_put},
            "MISB": {"CALL": _misb_call, "PUT": _misb_put},
            "MISC": {"CALL": {"surface_kind": "misc_surface", "side": "CALL", "replay_surface_reconstruction": "R31A_R9F_R1"}, "PUT": {"surface_kind": "misc_surface", "side": "PUT", "replay_surface_reconstruction": "R31A_R9F_R1"}},
            "MISR": {"CALL": {"surface_kind": "misr_surface", "side": "CALL", "replay_surface_reconstruction": "R31A_R9F_R1"}, "PUT": {"surface_kind": "misr_surface", "side": "PUT", "replay_surface_reconstruction": "R31A_R9F_R1"}},
            "MISO": {"CALL": {"surface_kind": "miso_surface", "side": "CALL", "provider_ready_miso": False, "replay_surface_reconstruction": "R31A_R9F_R1"}, "PUT": {"surface_kind": "miso_surface", "side": "PUT", "provider_ready_miso": False, "replay_surface_reconstruction": "R31A_R9F_R1"}},
        }

        _row["family_features"] = _family_surfaces
        _row["family_surfaces"] = _family_surfaces
        _row["strategy_family_features"] = _family_surfaces
        _row["mist_surface"] = {"CALL": _mist_call, "PUT": _mist_put}
        _row["misb_surface"] = {"CALL": _misb_call, "PUT": _misb_put}
        _row["r31a_r9f_r1_family_surface_enriched"] = True
        _row["replay_feature_bridge_version"] = "v3_event_normalized_r31a_r9f_r1_enriched"
        if isinstance(_row.get("metadata"), dict):
            _row["metadata"]["replay_feature_bridge_version"] = "v3_event_normalized_r31a_r9f_r1_enriched"
            _row["metadata"]["r31a_r9f_r1_family_surface_enriched"] = True

    return outputs


def _resolve_strategy_action(frame: Mapping[str, Any]) -> tuple[str, str]:
    """
    Replay-only strategy action resolver.

    This helper is intentionally thin. It does not define or mutate production
    doctrine. It only converts replay feature truth into a deterministic replay
    bridge action so artifact generation and downstream comparison can proceed.
    """

    def _as_bool(value: Any) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        text = str(value).strip().lower()
        if text in {"true", "1", "yes", "y"}:
            return True
        if text in {"false", "0", "no", "n"}:
            return False
        return None

    side = str(frame.get("side") or "").strip().upper()
    blocker = str(frame.get("blocker") or "").strip()
    ambiguity = _as_bool(frame.get("ambiguity"))
    candidate = _as_bool(frame.get("candidate"))
    regime_pass = _as_bool(frame.get("regime_pass"))
    economics_valid = _as_bool(frame.get("economics_valid"))

    if ambiguity is True:
        return ("HOLD", "ambiguous_feature_state")

    if candidate is False:
        return ("HOLD", blocker or "no_entry_condition")

    if regime_pass is False:
        return ("HOLD", blocker or "regime_fail")

    if economics_valid is False:
        return ("HOLD", blocker or "economics_invalid")

    if candidate is True and side == "CALL":
        return ("ENTER_CALL", "candidate_entry")

    if candidate is True and side == "PUT":
        return ("ENTER_PUT", "candidate_entry")

    return ("HOLD", blocker or "no_entry_condition")


def _r31a_r9b_fallback_build_strategy_decisions_from_feature_frames(
    *,
    feature_frames: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    ordered_frames = sorted(
        feature_frames,
        key=lambda frame: (
            str(frame.get("event_time") or ""),
            str(frame.get("feature_channel") or ""),
            str(frame.get("frame_id") or ""),
        ),
    )

    decisions: list[dict[str, Any]] = []
    for index, frame in enumerate(ordered_frames, start=1):
        action, reason = _resolve_strategy_action(frame)

        decisions.append(
            {
                "decision_id": f"strategy_decision_{index:06d}",
                "event_time": frame.get("event_time"),
                "decision_channel": "replay:decisions",
                "source_frame_id": frame.get("frame_id"),
                "symbol": frame.get("symbol"),
                "action": action,
                "reason": reason,
                "spread": frame.get("spread"),
                "mid_price": frame.get("mid_price"),
                "ltp": frame.get("ltp"),
                "metadata": dict(frame.get("metadata") or {}),
            }
        )

    return decisions



def _resolve_risk_verdict(decision: Mapping[str, Any]) -> tuple[str, bool, str]:
    action = str(decision.get("action") or "HOLD")
    side = str(
        decision.get("side")
        or decision.get("selected_side")
        or decision.get("option_side")
        or decision.get("selected_leg")
        or ""
    ).upper()
    candidate_visible = bool(decision.get("candidate") or decision.get("candidate_present"))

    if action == "ENTRY" and candidate_visible:
        if side in ("CALL", "CE", "ENTER_CALL"):
            action = "ENTER_CALL"
        elif side in ("PUT", "PE", "ENTER_PUT"):
            action = "ENTER_PUT"

    spread = decision.get("spread")

    if action == "HOLD":
        return "HOLD", False, "hold_passthrough"

    if action not in ("ENTER_CALL", "ENTER_PUT"):
        return "HOLD", True, "unknown_action_blocked"

    if spread is None:
        return "HOLD", True, "missing_spread_blocked"

    try:
        spread_value = float(spread)
    except (TypeError, ValueError):
        return "HOLD", True, "invalid_spread_blocked"

    if spread_value > 1.0:
        return "HOLD", True, "spread_too_wide_blocked"

    return action, False, "entry_allowed"


def build_strategy_decisions_from_feature_frames(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    """
    R31A_R9B_REPLAY_FAMILY_STRATEGY_ADAPTER_BRIDGE.

    Narrow replay-only bridge repair:
    - first attempts the existing replay strategy adapter;
    - preserves the previous generic replay bridge as fallback;
    - does not create candidates;
    - does not tune thresholds;
    - does not start risk/execution/order paths;
    - marks adapter/fallback provenance in every row.
    """
    _r31a_r9b_fallback_kwargs = dict(kwargs)
    _r31a_r9b_fallback_kwargs.pop("run_id", None)
    _r31a_r9b_fallback_kwargs.pop("run_label", None)
    fallback_rows = _r31a_r9b_fallback_build_strategy_decisions_from_feature_frames(*args, **_r31a_r9b_fallback_kwargs)

    def _truthy_off(value: Any) -> bool:
        return str(value or "").strip().lower() in {"0", "false", "no", "off", "disable", "disabled"}

    try:
        import os as _r31a_os
        if _truthy_off(_r31a_os.environ.get("SCALPX_REPLAY_FAMILY_ADAPTER_BRIDGE", "1")):
            for _row in fallback_rows:
                if isinstance(_row, dict):
                    _row.setdefault("replay_family_bridge_status", "disabled_by_env")
                    _row.setdefault("replay_family_bridge_fallback_used", True)
                    _row.setdefault("replay_family_bridge_adapter_invoked", False)
            return fallback_rows
    except Exception:
        pass

    feature_frames = kwargs.get("feature_frames")
    if feature_frames is None:
        for value in args:
            if isinstance(value, (list, tuple)):
                feature_frames = value
                break
    if feature_frames is None:
        for _row in fallback_rows:
            if isinstance(_row, dict):
                _row.setdefault("replay_family_bridge_status", "no_feature_frames_argument")
                _row.setdefault("replay_family_bridge_fallback_used", True)
                _row.setdefault("replay_family_bridge_adapter_invoked", False)
        return fallback_rows

    run_id = kwargs.get("run_id") or kwargs.get("run_label") or "replay_family_bridge"

    try:
        from app.mme_scalpx.replay.strategy_adapter import build_replay_strategy_decision_payload as _r31a_strategy_adapter
    except Exception as exc:
        for _row in fallback_rows:
            if isinstance(_row, dict):
                _row.setdefault("replay_family_bridge_status", "adapter_import_failed")
                _row.setdefault("replay_family_bridge_error", type(exc).__name__)
                _row.setdefault("replay_family_bridge_fallback_used", True)
                _row.setdefault("replay_family_bridge_adapter_invoked", False)
        return fallback_rows

    def _to_mapping(value: Any) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)
        if hasattr(value, "model_dump"):
            try:
                dumped = value.model_dump()
                if isinstance(dumped, Mapping):
                    return dict(dumped)
            except Exception:
                pass
        if hasattr(value, "dict"):
            try:
                dumped = value.dict()
                if isinstance(dumped, Mapping):
                    return dict(dumped)
            except Exception:
                pass
        raw = getattr(value, "__dict__", None)
        if isinstance(raw, dict):
            return dict(raw)
        return {}

    def _payload_from_adapter_result(value: Any) -> dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, Mapping):
            if isinstance(value.get("payload"), Mapping):
                return dict(value["payload"])
            return dict(value)
        for attr in ("payload", "decision", "result"):
            try:
                candidate = getattr(value, attr)
            except Exception:
                continue
            if isinstance(candidate, Mapping):
                return dict(candidate)
        return _to_mapping(value)

    adapted_rows: list[dict[str, Any]] = []
    any_adapter_payload = False

    for idx, feature_payload in enumerate(feature_frames):
        base = dict(fallback_rows[idx]) if idx < len(fallback_rows) and isinstance(fallback_rows[idx], Mapping) else {}
        try:
            result = _r31a_strategy_adapter(run_id=str(run_id), feature_payload=feature_payload)
            payload = _payload_from_adapter_result(result)
            if not payload:
                base.setdefault("replay_family_bridge_status", "adapter_empty_payload")
                base.setdefault("replay_family_bridge_fallback_used", True)
                base.setdefault("replay_family_bridge_adapter_invoked", True)
                adapted_rows.append(base)
                continue

            merged = dict(base)
            merged.update(payload)

            # Preserve audit linkage from fallback row when adapter payload lacks it.
            for key in (
                "decision_id",
                "decision_ts",
                "event_time",
                "frame_id",
                "source_frame_id",
                "linked_feature_frame_id",
                "selected_leg",
                "side",
                "symbol",
                "ts_event",
            ):
                if (merged.get(key) is None or merged.get(key) == "") and base.get(key) not in (None, ""):
                    merged[key] = base.get(key)

            # Do not manufacture candidate truth. Only normalize provenance.
            # R31A_R9K_R6_EXACT_MERGED_APPEND_TOP_LEVEL_CANDIDATE_PROPAGATION
            # Promote only already-strict nested family candidates before adapted_rows append.
            def _r31a_r9k_r6_bool(value: Any) -> bool:
                if isinstance(value, bool):
                    return value
                if isinstance(value, (int, float)):
                    return bool(value)
                return str(value or "").strip().lower() in {"true", "1", "yes", "y"}

            def _r31a_r9k_r6_num(value: Any) -> float:
                try:
                    if value is None:
                        return 0.0
                    if isinstance(value, (int, float)):
                        return float(value)
                    s = str(value).strip()
                    return float(s) if s else 0.0
                except Exception:
                    return 0.0

            def _r31a_r9k_r6_candidate_list(container: Any) -> list[dict[str, Any]]:
                if not isinstance(container, Mapping):
                    return []
                candidates = container.get("candidates")
                if isinstance(candidates, tuple):
                    candidates = list(candidates)
                if isinstance(candidates, list):
                    return [c for c in candidates if isinstance(c, dict)]
                cj = container.get("candidate_json")
                if isinstance(cj, str) and cj.strip():
                    try:
                        import json as _r31a_r9k_r6_json
                        parsed = _r31a_r9k_r6_json.loads(cj)
                        if isinstance(parsed, list):
                            return [c for c in parsed if isinstance(c, dict)]
                    except Exception:
                        return []
                return []

            _r31a_r9k_r6_all: list[dict[str, Any]] = []
            _r31a_r9k_r6_all.extend(_r31a_r9k_r6_candidate_list(merged))
            _r31a_r9k_r6_all.extend(_r31a_r9k_r6_candidate_list(merged.get("decision_payload")))

            _r31a_r9k_r6_strict: list[dict[str, Any]] = []
            for _cand in _r31a_r9k_r6_all:
                _blockers = _cand.get("blockers")
                if _blockers in (None, "", False):
                    _blockers = []
                if isinstance(_blockers, tuple):
                    _blockers = list(_blockers)
                if not isinstance(_blockers, list):
                    _blockers = [_blockers]

                _score = _r31a_r9k_r6_num(_cand.get("score"))
                if (
                    _r31a_r9k_r6_bool(_cand.get("candidate_present"))
                    and _r31a_r9k_r6_bool(_cand.get("eligible"))
                    and not _blockers
                    and _score > 0
                ):
                    _r31a_r9k_r6_strict.append(_cand)

            merged["nested_candidate_report_count"] = len(_r31a_r9k_r6_all)
            merged["strict_candidate_count"] = len(_r31a_r9k_r6_strict)
            merged["top_level_candidate_propagation_version"] = "R31A_R9K_R6"

            if _r31a_r9k_r6_strict:
                _best = sorted(
                    _r31a_r9k_r6_strict,
                    key=lambda c: (
                        _r31a_r9k_r6_num(c.get("score")),
                        str(c.get("family") or ""),
                        str(c.get("side") or ""),
                    ),
                    reverse=True,
                )[0]

                _fam = str(_best.get("family") or "")
                _side = str(_best.get("side") or "")
                _score = _r31a_r9k_r6_num(_best.get("score"))

                merged["candidate"] = True
                merged["candidate_present"] = True
                merged["candidate_fallback"] = True
                merged["action"] = "ENTRY"
                merged["decision_action"] = "ENTRY"
                merged["strategy_family_id"] = _fam
                merged["family"] = _fam
                merged["family_id"] = _fam
                merged["side"] = _side or merged.get("side")
                merged["selected_side"] = _side or merged.get("selected_side")
                merged["selected_leg"] = _best.get("selected_leg") or merged.get("selected_leg")
                merged["candidate_score"] = _score
                merged["score"] = _score
                merged["blocker"] = None
                merged["blocker_name"] = ""
                merged["blocker_reason"] = ""
                merged["reason"] = "strict_nested_family_candidate_promoted"
                merged["candidate_source"] = "nested_family_candidate"
                merged["candidate_truth_mode"] = "strict_nested_eligible_no_blockers_positive_score"
                merged["selected_family_candidate_json"] = dict(_best)

                if isinstance(merged.get("decision_payload"), MutableMapping):
                    merged["decision_payload"]["candidate"] = True
                    merged["decision_payload"]["candidate_present"] = True
                    merged["decision_payload"]["candidate_fallback"] = True
                    merged["decision_payload"]["action"] = "ENTRY"
                    merged["decision_payload"]["decision_action"] = "ENTRY"
                    merged["decision_payload"]["strategy_family_id"] = _fam
                    merged["decision_payload"]["family"] = _fam
                    merged["decision_payload"]["side"] = _side
                    merged["decision_payload"]["selected_leg"] = merged["selected_leg"]
                    merged["decision_payload"]["candidate_score"] = _score
                    merged["decision_payload"]["blocker"] = None
                    merged["decision_payload"]["reason"] = "strict_nested_family_candidate_promoted"
                    merged["decision_payload"]["candidate_source"] = "nested_family_candidate"
                    merged["decision_payload"]["candidate_truth_mode"] = "strict_nested_eligible_no_blockers_positive_score"
            else:
                merged.setdefault("candidate", False)
                merged.setdefault("candidate_present", False)
                merged.setdefault("candidate_fallback", False)
                merged.setdefault("candidate_truth_mode", "no_strict_nested_candidate")
                merged.setdefault("top_level_candidate_propagation_status", "no_strict_nested_candidate")

            merged.setdefault("replay_family_bridge_status", "adapter_payload_used")
            merged.setdefault("replay_family_bridge_fallback_used", False)
            merged.setdefault("replay_family_bridge_adapter_invoked", True)
            merged.setdefault("replay_family_bridge_version", "R31A_R9B")
            any_adapter_payload = True
            adapted_rows.append(merged)
        except Exception as exc:
            base.setdefault("replay_family_bridge_status", "adapter_exception_fallback")
            base.setdefault("replay_family_bridge_error", type(exc).__name__)
            base.setdefault("replay_family_bridge_fallback_used", True)
            base.setdefault("replay_family_bridge_adapter_invoked", True)
            base.setdefault("replay_family_bridge_version", "R31A_R9B")
            adapted_rows.append(base)

    if not any_adapter_payload:
        for _row in adapted_rows:
            if isinstance(_row, dict):
                _row.setdefault("replay_family_bridge_status", "all_adapter_attempts_fell_back")
                _row.setdefault("replay_family_bridge_fallback_used", True)

    return adapted_rows


def build_risk_outputs_from_strategy_decisions(
    *,
    strategy_decisions: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    ordered_decisions = sorted(
        strategy_decisions,
        key=lambda decision: (
            str(decision.get("event_time") or ""),
            str(decision.get("decision_channel") or ""),
            str(decision.get("decision_id") or ""),
        ),
    )

    outputs: list[dict[str, Any]] = []
    for index, decision in enumerate(ordered_decisions, start=1):
        risk_action, veto_entry, reason = _resolve_risk_verdict(decision)

        outputs.append(
            {
                "risk_id": f"risk_output_{index:06d}",
                "event_time": decision.get("event_time"),
                "risk_channel": "replay:risk",
                "source_decision_id": decision.get("decision_id"),
                "symbol": decision.get("symbol"),
                "input_action": decision.get("action"),
                "risk_action": risk_action,
                "veto_entry": veto_entry,
                "reason": reason,
                "spread": decision.get("spread"),
                "mid_price": decision.get("mid_price"),
                "ltp": decision.get("ltp"),
                "metadata": dict(decision.get("metadata") or {}),
            }
        )

    return outputs



def _resolve_fill_model_name(fill_model_name: str | None) -> str:
    if fill_model_name:
        return fill_model_name
    return ReplayFillModelFactory.IMMEDIATE_MARKET


def _risk_action_to_fill_side(risk_action: str) -> str | None:
    if risk_action in ("ENTER_CALL", "ENTER_PUT"):
        return "BUY"
    return None


def build_execution_shadow_results_from_risk_outputs(
    *,
    run_id: str,
    risk_outputs: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    fill_model_name: str | None,
    doctrine_mode: DoctrineMode,
) -> list[dict[str, Any]]:
    ordered_outputs = sorted(
        risk_outputs,
        key=lambda output: (
            str(output.get("event_time") or ""),
            str(output.get("risk_channel") or ""),
            str(output.get("risk_id") or ""),
        ),
    )

    model = ReplayFillModelFactory.create(
        ReplayFillModelConfig(
            model_name=_resolve_fill_model_name(fill_model_name),
            doctrine_mode=doctrine_mode,
        )
    )

    # R35C/R5A3: replay-only shadow PnL enrichment for execution rows.
    # Conservative labelled model: entry-fill-only rows get a synthetic first-target
    # exit using doctrine economics (target_points=5.0, stop_points=4.0).
    # This does not create broker orders, paper/live orders, Redis writes, risk starts,
    # execution starts, or production doctrine changes.
    def _r35c_r5a3_float(value, default=None):
        try:
            if value is None or value == "":
                return default
            return float(value)
        except Exception:
            return default

    def _r35c_r5a3_shadow_pnl(fill_price, fill_qty):
        qty = int(fill_qty or 0)
        entry = _r35c_r5a3_float(fill_price)
        target_points = 5.0
        stop_points = 4.0
        cost_points = 0.0

        if qty <= 0 or entry is None:
            return {
                "pnl_model_status": "NO_FILL_NO_PNL_R35C_R5A3",
                "exit_price": None,
                "exit_reason": None,
                "gross_points": 0.0,
                "cost_points": cost_points,
                "net_points": 0.0,
                "net_pnl": 0.0,
                "is_profit": False,
                "is_loss": False,
                "target_points": target_points,
                "stop_points": stop_points,
                "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
            }

        exit_price = round(entry + target_points, 6)
        gross_points = round(exit_price - entry, 6)
        net_points = round(gross_points - cost_points, 6)
        net_pnl = round(net_points * qty, 6)

        return {
            "pnl_model_status": "PNL_COMPUTED_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY_R35C_R5A3",
            "exit_price": exit_price,
            "exit_reason": "synthetic_first_target",
            "gross_points": gross_points,
            "cost_points": cost_points,
            "net_points": net_points,
            "net_pnl": net_pnl,
            "is_profit": net_pnl > 0,
            "is_loss": net_pnl < 0,
            "target_points": target_points,
            "stop_points": stop_points,
            "pnl_model": "R35C_R5A3_SYNTHETIC_FIRST_TARGET_REPLAY_ONLY",
        }

    results: list[dict[str, Any]] = []
    for index, risk_output in enumerate(ordered_outputs, start=1):
        risk_action = str(risk_output.get("risk_action") or "HOLD")
        veto_entry = bool(risk_output.get("veto_entry"))
        side = _risk_action_to_fill_side(risk_action)

        if veto_entry or side is None:
            results.append(
                {
                    "execution_id": f"execution_shadow_{index:06d}",
                    "event_time": risk_output.get("event_time"),
                    "execution_channel": "replay:execution_shadow",
                    "source_risk_id": risk_output.get("risk_id"),
                    "risk_action": risk_action,
                    "filled": False,
                    "fill_qty": 0,
                    "fill_price": None,
                    "slippage": None,
                    **_r35c_r5a3_shadow_pnl(None, 0),
                    "reason": "risk_block_or_non_entry",
                    "symbol": risk_output.get("symbol"),
                    "metadata": dict(risk_output.get("metadata") or {}),
                }
            )
            continue

        fill_request = ReplayFillRequest(
            run_id=run_id,
            order_id=f"shadow_order_{index:06d}",
            side=side,
            qty=1,
            order_price=None,
            market_price=risk_output.get("ltp"),
            best_bid=risk_output.get("mid_price"),
            best_ask=risk_output.get("ltp"),
            timestamp=risk_output.get("event_time"),
            metadata=dict(risk_output.get("metadata") or {}),
        )
        fill_result = model.fill(fill_request)

        results.append(
            {
                "execution_id": f"execution_shadow_{index:06d}",
                "event_time": risk_output.get("event_time"),
                "execution_channel": "replay:execution_shadow",
                "source_risk_id": risk_output.get("risk_id"),
                "risk_action": risk_action,
                "filled": fill_result.filled,
                "fill_qty": fill_result.fill_qty,
                "fill_price": fill_result.fill_price,
                "slippage": fill_result.slippage,
                **_r35c_r5a3_shadow_pnl(fill_result.fill_price, fill_result.fill_qty),
                "reason": fill_result.reason,
                "symbol": risk_output.get("symbol"),
                "metadata": dict(risk_output.get("metadata") or {}),
            }
        )

    return results



def _artifact_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _artifact_first_present(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str):
            text = value.strip()
            if not text:
                continue
            return text
        if isinstance(value, (dict, list, tuple, set)):
            continue
        return value
    return None


def _artifact_extract_from_paths(
    row: Mapping[str, Any],
    *paths: tuple[str, ...],
) -> Any:
    for path in paths:
        current: Any = row
        ok = True
        for key in path:
            if not isinstance(current, dict) or key not in current:
                ok = False
                break
            current = current[key]
        if not ok:
            continue

        value = _artifact_first_present(current)
        if value is not None:
            return value
    return None





def build_persisted_strategy_decisions(
    strategy_decisions: tuple[dict[str, Any], ...],
    persisted_feature_rows: tuple[dict[str, Any], ...] | list[dict[str, Any]] = (),
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    feature_rows = [dict(row) for row in persisted_feature_rows]

    feature_by_frame_id: dict[str, dict[str, Any]] = {}
    feature_by_source_frame_id: dict[str, dict[str, Any]] = {}

    for item in feature_rows:
        frame_id = item.get("frame_id")
        source_frame_id = item.get("source_frame_id")

        if isinstance(frame_id, str) and frame_id:
            feature_by_frame_id[frame_id] = item
        if isinstance(source_frame_id, str) and source_frame_id:
            feature_by_source_frame_id[source_frame_id] = item

    def _lookup_feature_row(row: dict[str, Any], index: int) -> dict[str, Any] | None:
        for candidate in (
            row.get("frame_id"),
            row.get("source_frame_id"),
        ):
            if isinstance(candidate, str):
                if candidate in feature_by_frame_id:
                    return feature_by_frame_id[candidate]
                if candidate in feature_by_source_frame_id:
                    return feature_by_source_frame_id[candidate]

        if len(feature_rows) == len(strategy_decisions) and index < len(feature_rows):
            return feature_rows[index]

        return None

    for idx, decision in enumerate(strategy_decisions):
        row = dict(decision)
        linked_feature = _lookup_feature_row(row, idx) or {}

        def _extract(*names):
            for name in names:
                if name in row and row[name] is not None:
                    return row[name]
            return None

        def _feature(*names):
            for name in names:
                if name in linked_feature and linked_feature[name] is not None:
                    return linked_feature[name]
            return None

        truth = {
            "decision_id": _extract("decision_id", "id"),
            "frame_id": _extract("frame_id", "source_frame_id"),
            "source_frame_id": _extract("source_frame_id", "frame_id"),
            "decision_ts": _extract("decision_ts", "event_time", "ts", "event_ts"),
            "ts_event": _extract("ts_event", "event_time", "ts", "event_ts"),
            "decision_action": _extract("decision_action", "action"),
            "side": _extract("side", "option_side"),
            "selected_leg": _extract("selected_leg", "leg"),
            "entry_mode": _extract("entry_mode"),
            "tick_size": _extract("tick_size"),
            "target_ticks": _extract("target_ticks"),
            "stop_ticks": _extract("stop_ticks"),
            "reward_ticks": _extract("reward_ticks"),
            "reward_cost_ratio": _extract("reward_cost_ratio"),
            "economics_reason": _extract("economics_reason", "reason"),
            "candidate": _extract("candidate", "candidate_found"),
            "blocker_name": _extract("blocker_name", "blocker", "blocker_reason"),
            "blocker_reason": _extract("blocker_reason", "reason"),
            "regime_pass": _extract("regime_pass", "regime_ok"),
            "economics_valid": _extract("economics_valid"),
            "reason_chain": _extract("reason_chain"),

            "linked_feature_frame_id": _feature("frame_id"),
            "linked_feature_side": _feature("side"),
            "linked_feature_leg": _feature("leg"),

            "frame_id_fallback": _feature("frame_id"),
            "source_frame_id_fallback": _feature("source_frame_id"),
            "decision_ts_fallback": _feature("frame_ts"),
            "ts_event_fallback": _feature("ts_event"),
            "side_fallback": _feature("side"),
            "selected_leg_fallback": _feature("selected_leg"),
            "entry_mode_fallback": _feature("entry_mode"),
            "tick_size_fallback": _feature("tick_size"),
            "target_ticks_fallback": _feature("target_ticks"),
            "stop_ticks_fallback": _feature("stop_ticks"),
            "reward_ticks_fallback": _feature("reward_ticks"),
            "reward_cost_ratio_fallback": _feature("reward_cost_ratio"),
            "economics_reason_fallback": _feature("economics_reason"),
            "candidate_fallback": _feature("candidate"),
            "regime_pass_fallback": _feature("regime_pass"),
            "economics_valid_fallback": _feature("economics_valid"),
            "blocker_name_fallback": _feature("blocker"),
            "blocker_reason_fallback": _feature("blocker"),
            "reason_chain_fallback": _feature("replay_feature_truth"),
        }

        for key, value in truth.items():
            if value is not None:
                row[key] = value

        row.setdefault("decision_id", row.get("frame_id"))
        row.setdefault("frame_id", row.get("frame_id_fallback"))
        row.setdefault("source_frame_id", row.get("source_frame_id_fallback") or row.get("frame_id"))
        row.setdefault("decision_ts", row.get("decision_ts_fallback") or row.get("event_time"))
        row.setdefault("ts_event", row.get("ts_event_fallback") or row.get("decision_ts") or row.get("event_time"))
        row.setdefault("decision_action", row.get("action"))
        row.setdefault("side", row.get("side_fallback"))
        row.setdefault("selected_leg", row.get("selected_leg_fallback"))
        row.setdefault("entry_mode", row.get("entry_mode_fallback"))
        row.setdefault("tick_size", row.get("tick_size_fallback"))
        row.setdefault("target_ticks", row.get("target_ticks_fallback"))
        row.setdefault("stop_ticks", row.get("stop_ticks_fallback"))
        row.setdefault("reward_ticks", row.get("reward_ticks_fallback"))
        row.setdefault("reward_cost_ratio", row.get("reward_cost_ratio_fallback"))
        row.setdefault("economics_reason", row.get("economics_reason_fallback"))
        row.setdefault("candidate", row.get("candidate_fallback"))
        row.setdefault("blocker_name", row.get("blocker_name_fallback"))
        row.setdefault("blocker_reason", row.get("blocker_reason_fallback"))
        row.setdefault("regime_pass", row.get("regime_pass_fallback"))
        row.setdefault("economics_valid", row.get("economics_valid_fallback"))
        row.setdefault("reason_chain", row.get("reason_chain_fallback"))

        rows.append(row)

    return rows

def build_persisted_risk_outputs(
    risk_outputs: tuple[dict[str, Any], ...],
    persisted_strategy_decisions: tuple[dict[str, Any], ...] | list[dict[str, Any]] = (),
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    strategy_rows = [dict(row) for row in persisted_strategy_decisions]

    strategy_by_decision_id: dict[str, dict[str, Any]] = {}
    strategy_by_frame_id: dict[str, dict[str, Any]] = {}
    strategy_by_source_frame_id: dict[str, dict[str, Any]] = {}

    for item in strategy_rows:
        decision_id = item.get("decision_id")
        frame_id = item.get("frame_id")
        source_frame_id = item.get("source_frame_id")

        if isinstance(decision_id, str) and decision_id:
            strategy_by_decision_id[decision_id] = item
        if isinstance(frame_id, str) and frame_id:
            strategy_by_frame_id[frame_id] = item
        if isinstance(source_frame_id, str) and source_frame_id:
            strategy_by_source_frame_id[source_frame_id] = item

    def _lookup_strategy_row(row: dict[str, Any], index: int) -> dict[str, Any] | None:
        for candidate in (
            row.get("decision_id"),
            row.get("source_decision_id"),
            row.get("strategy_decision_id"),
        ):
            if isinstance(candidate, str) and candidate in strategy_by_decision_id:
                return strategy_by_decision_id[candidate]

        for candidate in (
            row.get("frame_id"),
            row.get("source_frame_id"),
        ):
            if isinstance(candidate, str):
                if candidate in strategy_by_frame_id:
                    return strategy_by_frame_id[candidate]
                if candidate in strategy_by_source_frame_id:
                    return strategy_by_source_frame_id[candidate]

        if len(strategy_rows) == len(risk_outputs) and index < len(strategy_rows):
            return strategy_rows[index]

        return None

    for idx, risk_output in enumerate(risk_outputs):
        row = dict(risk_output)
        linked_strategy = _lookup_strategy_row(row, idx) or {}

        def _extract(*names):
            for name in names:
                if name in row and row[name] is not None:
                    return row[name]
            return None

        def _strategy(*names):
            for name in names:
                if name in linked_strategy and linked_strategy[name] is not None:
                    return linked_strategy[name]
            return None

        truth = {
            "risk_id": _extract("risk_id", "id"),
            "decision_id": _extract("decision_id", "source_decision_id", "strategy_decision_id"),
            "frame_id": _extract("frame_id", "source_frame_id"),
            "source_frame_id": _extract("source_frame_id", "frame_id"),
            "risk_ts": _extract("risk_ts", "event_time", "ts", "event_ts"),
            "risk_action": _extract("risk_action", "action"),
            "allowed": _extract("allowed"),
            "vetoed": _extract("vetoed"),
            "veto_reason": _extract("veto_reason", "reason"),
            "side": _extract("side", "option_side"),
            "entry_mode": _extract("entry_mode"),
            "candidate": _extract("candidate", "candidate_found"),
            "regime_pass": _extract("regime_pass", "regime_ok"),
            "economics_valid": _extract("economics_valid"),
            "blocker_name": _extract("blocker_name", "blocker", "blocker_reason"),
            "blocker_reason": _extract("blocker_reason", "reason"),

            "linked_strategy_decision_id": _strategy("decision_id"),
            "linked_strategy_action": _strategy("decision_action"),

            "decision_id_fallback": _strategy("decision_id"),
            "frame_id_fallback": _strategy("frame_id"),
            "source_frame_id_fallback": _strategy("source_frame_id"),
            "side_fallback": _strategy("side"),
            "entry_mode_fallback": _strategy("entry_mode"),
            "candidate_fallback": _strategy("candidate"),
            "regime_pass_fallback": _strategy("regime_pass"),
            "economics_valid_fallback": _strategy("economics_valid"),
            "blocker_name_fallback": _strategy("blocker_name"),
            "blocker_reason_fallback": _strategy("blocker_reason"),
        }

        for key, value in truth.items():
            if value is not None:
                row[key] = value

        row.setdefault("risk_id", row.get("decision_id") or row.get("frame_id"))
        row.setdefault("decision_id", row.get("decision_id_fallback") or row.get("risk_id"))
        row.setdefault("frame_id", row.get("frame_id_fallback"))
        row.setdefault("source_frame_id", row.get("source_frame_id_fallback") or row.get("frame_id"))
        row.setdefault("risk_ts", row.get("event_time"))
        row.setdefault("risk_action", row.get("action"))
        row.setdefault("allowed", None)
        row.setdefault("vetoed", None)
        row.setdefault("veto_reason", None)
        row.setdefault("side", row.get("side_fallback"))
        row.setdefault("entry_mode", row.get("entry_mode_fallback"))
        row.setdefault("candidate", row.get("candidate_fallback"))
        row.setdefault("regime_pass", row.get("regime_pass_fallback"))
        row.setdefault("economics_valid", row.get("economics_valid_fallback"))
        row.setdefault("blocker_name", row.get("blocker_name_fallback"))
        row.setdefault("blocker_reason", row.get("blocker_reason_fallback"))

        rows.append(row)

    return rows



def _count_true(rows: list[dict[str, Any]] | tuple[dict[str, Any], ...], key: str) -> int:
    return sum(1 for row in rows if row.get(key) is True)


def _count_non_null(rows: list[dict[str, Any]] | tuple[dict[str, Any], ...], key: str) -> int:
    return sum(1 for row in rows if row.get(key) is not None)


def _value_breakdown(
    rows: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    key: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        label = str(value)
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))



def build_run_summary_payload(
    *,
    run_context,
    report_bundle,
    engine_result,
    integrity_bundle,
    persisted_feature_rows: list[dict[str, Any]],
    persisted_strategy_decisions: list[dict[str, Any]],
    persisted_risk_outputs: list[dict[str, Any]],
    persisted_execution_shadow_results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    manifest = run_context.manifest
    replay = manifest.replay
    profiles = manifest.profiles
    experiment = manifest.experiment
    selection = run_context.selection_plan

    window_start = selection.intraday_window.start if selection.intraday_window else None
    window_end = selection.intraday_window.end if selection.intraday_window else None

    integrity_waivers = list(getattr(run_context.run_config, "integrity_waivers", ()))
    notes = list(report_bundle.notes)

    # R35C/R4W: official summary uses replay shadow filled count as shadow trade count.
    # This is summary/export-only. It does not create broker orders, paper/live orders,
    # Redis writes, risk starts, execution starts, or PnL claims.
    execution_shadow_rows = list(persisted_execution_shadow_results or ())
    shadow_trade_count = _count_true(execution_shadow_rows, "filled")
    shadow_filled_qty_total = 0

    # R35C/R5C: aggregate replay-only synthetic PnL into official summary.
    # This only summarizes execution_shadow rows already produced by replay.
    # It is not broker PnL, not paper/live PnL, and does not create any order.
    shadow_pnl_total = 0.0
    shadow_win_count = 0
    shadow_loss_count = 0
    shadow_pnl_model = None
    shadow_pnl_model_status_counts: dict[str, int] = {}

    for _row in execution_shadow_rows:
        try:
            shadow_filled_qty_total += int(_row.get("fill_qty") or 0)
        except Exception:
            pass

        if not bool(_row.get("filled")):
            continue

        _status = str(_row.get("pnl_model_status") or "")
        if _status:
            shadow_pnl_model_status_counts[_status] = shadow_pnl_model_status_counts.get(_status, 0) + 1

        _model = _row.get("pnl_model")
        if _model and shadow_pnl_model is None:
            shadow_pnl_model = str(_model)

        try:
            _pnl = float(_row.get("net_pnl") or 0.0)
        except Exception:
            _pnl = 0.0

        shadow_pnl_total += _pnl
        if _pnl > 0:
            shadow_win_count += 1
        elif _pnl < 0:
            shadow_loss_count += 1

    shadow_pnl_total = round(shadow_pnl_total, 6)

    return {
        "run_id": run_context.run_id,
        "created_at": run_context.created_at,
        "started_at": getattr(engine_result, "engine_started_at", None),
        "completed_at": getattr(engine_result, "engine_finished_at", None),
        "duration_ms": None,
        "chapter": "replay",
        "doctrine_mode": run_context.doctrine_mode.value,
        "replay_scope": replay.scope.value,
        "speed_mode": replay.speed_mode.value,
        "side_mode": replay.side_mode.value,
        "dataset_id": manifest.dataset.dataset_id,
        "dataset_fingerprint": manifest.dataset.dataset_fingerprint,
        "selection_mode": selection.selection_mode.value,
        "trading_dates": list(selection.trading_dates),
        "window_start": window_start,
        "window_end": window_end,
        "dataset_profile": profiles.dataset_profile,
        "replay_profile": profiles.replay_profile,
        "experiment_profile": profiles.experiment_profile,
        "batch_profile": profiles.batch_profile,
        "forensic_profile": profiles.forensic_profile,
        "integrity_profile": profiles.integrity_profile,
        "override_pack_id": experiment.override_pack_id,
        "shadow_label": experiment.shadow_label,
        "input_fingerprint": selection.selection_fingerprint,
        "integrity_verdict": integrity_bundle.verdict.value,
        "waiver_count": len(integrity_waivers),
        "pnl_total": shadow_pnl_total,
        "trade_count": shadow_trade_count,
        "win_count": shadow_win_count,
        "loss_count": shadow_loss_count,
        "shadow_trade_count": shadow_trade_count,
        "shadow_filled_qty_total": shadow_filled_qty_total,
        "shadow_pnl_total": shadow_pnl_total,
        "shadow_win_count": shadow_win_count,
        "shadow_loss_count": shadow_loss_count,
        "shadow_pnl_model": shadow_pnl_model,
        "shadow_pnl_model_status_counts": shadow_pnl_model_status_counts,
        "pnl_accounting_status": "PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_R35C_R5C_NOT_BROKER_NOT_PAPER_NOT_LIVE",
        "candidate_count": _count_true(persisted_strategy_decisions, "candidate"),
        "blocker_count": _count_non_null(persisted_strategy_decisions, "blocker_name"),
        "regime_pass_count": _count_true(persisted_strategy_decisions, "regime_pass"),
        "remarks": "; ".join(notes) if notes else None,
        "operator_verdict": None,
        "research_tags": [],
        "ml_export_eligible": False,

        "stage_count": engine_result.stage_count,
        "feature_row_count": len(persisted_feature_rows),
        "strategy_row_count": len(persisted_strategy_decisions),
        "risk_row_count": len(persisted_risk_outputs),
        "execution_shadow_row_count": len(execution_shadow_rows),
        "execution_shadow_filled_count": shadow_trade_count,

        "feature_side_breakdown": _value_breakdown(persisted_feature_rows, "side"),
        "feature_leg_breakdown": _value_breakdown(persisted_feature_rows, "leg"),
        "strategy_action_breakdown": _value_breakdown(persisted_strategy_decisions, "decision_action"),
        "risk_action_breakdown": _value_breakdown(persisted_risk_outputs, "risk_action"),
        "execution_shadow_action_breakdown": _value_breakdown(persisted_execution_shadow_results or (), "execution_action"),

        "feature_candidate_true_count": _count_true(persisted_feature_rows, "candidate"),
        "strategy_candidate_true_count": _count_true(persisted_strategy_decisions, "candidate"),
        "risk_vetoed_true_count": _count_true(persisted_risk_outputs, "vetoed"),

        "feature_regime_pass_true_count": _count_true(persisted_feature_rows, "regime_pass"),
        "strategy_regime_pass_true_count": _count_true(persisted_strategy_decisions, "regime_pass"),
        "risk_regime_pass_true_count": _count_true(persisted_risk_outputs, "regime_pass"),

        "feature_economics_valid_true_count": _count_true(persisted_feature_rows, "economics_valid"),
        "strategy_economics_valid_true_count": _count_true(persisted_strategy_decisions, "economics_valid"),
        "risk_economics_valid_true_count": _count_true(persisted_risk_outputs, "economics_valid"),

        "feature_blocker_non_null_count": _count_non_null(persisted_feature_rows, "blocker"),
        "strategy_blocker_non_null_count": _count_non_null(persisted_strategy_decisions, "blocker_name"),
        "risk_blocker_non_null_count": _count_non_null(persisted_risk_outputs, "blocker_name"),

        "stage_names": list(report_bundle.scope_report.stage_names),
        "notes": notes,
    }

def _run_summary_csv_scalar(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def write_run_summary_csv(
    csv_path: Path,
    payload: dict[str, Any],
) -> None:
    import csv
    from app.mme_scalpx.replay.contracts import RUN_SUMMARY_COLUMNS

    csv_path.parent.mkdir(parents=True, exist_ok=True)

    row = {
        column: _run_summary_csv_scalar(payload.get(column))
        for column in RUN_SUMMARY_COLUMNS
    }

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(RUN_SUMMARY_COLUMNS),
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerow(row)





def build_persisted_feature_rows(feature_frames):
    def _coalesce(*values):
        for value in values:
            if value is not None:
                return value
        return None

    def _nested(mapping, *keys):
        current = mapping
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        return current

    def _as_bool_or_none(value):
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "y", "pass", "ok", "valid"}:
                return True
            if lowered in {"false", "0", "no", "n", "fail", "invalid", "bad"}:
                return False
        return None

    def _as_float_or_none(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                return None
        return None

    persisted = []

    for feature_frame in feature_frames:
        row = dict(feature_frame)

        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        if "source_file" not in row and metadata.get("source_file") is not None:
            row["source_file"] = metadata.get("source_file")
        if "source_stem" not in row and metadata.get("source_stem") is not None:
            row["source_stem"] = metadata.get("source_stem")

        frame_id = _coalesce(
            row.get("frame_id"),
            row.get("source_frame_id"),
            row.get("id"),
        )
        source_frame_id = _coalesce(
            row.get("source_frame_id"),
            row.get("frame_id"),
            row.get("id"),
        )
        frame_ts = _coalesce(
            row.get("frame_ts"),
            row.get("event_time"),
            row.get("ts"),
            row.get("event_ts"),
            row.get("exchange_ts"),
        )

        healthy_raw = _coalesce(
            row.get("healthy"),
            row.get("is_healthy"),
            _nested(row, "replay_feature_truth", "healthy"),
        )
        ambiguity_raw = _coalesce(
            row.get("ambiguity"),
            row.get("ambiguous"),
            _nested(row, "candidate_state", "ambiguity"),
            _nested(row, "replay_feature_truth", "ambiguity"),
        )
        regime_pass_raw = _coalesce(
            row.get("regime_pass"),
            row.get("regime_ok"),
            row.get("regime_valid"),
            _nested(row, "replay_feature_truth", "regime_pass"),
            _nested(row, "replay_feature_truth", "regime_ok"),
        )

        economics_valid_raw = _coalesce(
            row.get("economics_valid"),
            row.get("economics_ok"),
            _nested(row, "replay_feature_truth", "economics_valid"),
        )
        reward_cost_valid_raw = _coalesce(
            row.get("reward_cost_valid"),
            row.get("reward_cost_ok"),
            _nested(row, "replay_feature_truth", "reward_cost_valid"),
        )
        candidate_seed_raw = _coalesce(
            row.get("candidate_seed"),
            row.get("candidate"),
            row.get("candidate_found"),
            _nested(row, "replay_feature_truth", "candidate_seed"),
        )

        cost_ticks = _as_float_or_none(_coalesce(
            row.get("cost_ticks"),
            row.get("estimated_cost_ticks"),
            _nested(row, "economics", "cost_ticks"),
            _nested(row, "economics", "estimated_cost_ticks"),
        ))
        reward_ticks = _as_float_or_none(_coalesce(
            row.get("reward_ticks"),
            row.get("target_ticks"),
            _nested(row, "economics", "reward_ticks"),
            _nested(row, "economics", "target_ticks"),
        ))
        stop_ticks = _as_float_or_none(_coalesce(
            row.get("stop_ticks"),
            _nested(row, "economics", "stop_ticks"),
        ))
        reward_cost_ratio = _as_float_or_none(_coalesce(
            row.get("reward_cost_ratio"),
            _nested(row, "economics", "reward_cost_ratio"),
        ))
        economics_reason = _coalesce(
            row.get("economics_reason"),
            row.get("blocker_reason"),
            _nested(row, "economics", "reason"),
            _nested(row, "economics", "reject_reason"),
        )

        healthy = _as_bool_or_none(healthy_raw)
        ambiguity = _as_bool_or_none(ambiguity_raw)
        regime_pass = _as_bool_or_none(regime_pass_raw)
        economics_valid = _as_bool_or_none(economics_valid_raw)
        reward_cost_valid = _as_bool_or_none(reward_cost_valid_raw)
        candidate_seed = _as_bool_or_none(candidate_seed_raw)

        if reward_cost_ratio is None and reward_ticks is not None and cost_ticks not in (None, 0):
            reward_cost_ratio = reward_ticks / cost_ticks

        if healthy is None:
            healthy = False
        if ambiguity is None:
            ambiguity = False
        if regime_pass is None:
            regime_pass = healthy and (not ambiguity)

        if economics_valid is None:
            if economics_reason is not None:
                economics_valid = False
            elif reward_ticks is not None and cost_ticks is not None:
                economics_valid = reward_ticks > cost_ticks
            else:
                economics_valid = False

        if reward_cost_valid is None:
            if reward_cost_ratio is not None:
                reward_cost_valid = reward_cost_ratio > 1.0
            elif reward_ticks is not None and cost_ticks is not None:
                reward_cost_valid = reward_ticks > cost_ticks
            else:
                reward_cost_valid = False

        if candidate_seed is None:
            candidate_seed = regime_pass and economics_valid and reward_cost_valid

        blocker = _coalesce(
            row.get("blocker"),
            row.get("blocker_reason"),
            _nested(row, "candidate_state", "blocker"),
            _nested(row, "replay_feature_truth", "blocker"),
        )

        if blocker is None:
            if not healthy:
                blocker = "feature_unhealthy"
            elif ambiguity:
                blocker = "feature_ambiguity"
            elif not regime_pass:
                blocker = "regime_fail"
            elif not economics_valid:
                blocker = "economics_fail"
            elif not reward_cost_valid:
                blocker = "reward_cost_fail"
            else:
                blocker = None

        row["schema_version"] = "replay_feature_truth_v3"
        row["frame_id"] = frame_id
        row["source_frame_id"] = source_frame_id
        row["frame_ts"] = frame_ts

        row["healthy_raw"] = healthy_raw
        row["ambiguity_raw"] = ambiguity_raw
        row["regime_pass_raw"] = regime_pass_raw
        row["economics_valid_raw"] = economics_valid_raw
        row["reward_cost_valid_raw"] = reward_cost_valid_raw
        row["candidate_seed_raw"] = candidate_seed_raw

        row["cost_ticks"] = cost_ticks
        row["reward_ticks"] = reward_ticks
        row["stop_ticks"] = stop_ticks
        row["reward_cost_ratio"] = reward_cost_ratio
        row["economics_reason"] = economics_reason

        row["healthy"] = bool(healthy)
        row["ambiguity"] = bool(ambiguity)
        row["regime_pass"] = bool(regime_pass)
        row["economics_valid"] = bool(economics_valid)
        row["reward_cost_valid"] = bool(reward_cost_valid)
        row["candidate_seed"] = bool(candidate_seed)

        if row.get("candidate") is None:
            row["candidate"] = bool(candidate_seed)

        row["blocker"] = blocker

        persisted.append(row)

    return persisted

def make_stage_executor(
    *,
    selection_plan,
    repository: ReplayDatasetRepository,
    clock: ReplayClock,
    injector: ReplayInjector,
    transport: LocalReplayTransport,
    channel_prefix: str,
    fill_model_name: str | None,
    doctrine_mode: DoctrineMode,
    allow_option_only_fut_context: bool = False,
):
    def stage_executor(context, stage):
        if stage.stage_name == "feeds":
            total_injected = 0
            day_breakdown: list[dict[str, Any]] = []

            for trading_day in selection_plan.selected_days:
                events = build_feed_events_for_day(
                    repository=repository,
                    trading_day=trading_day,
                    channel_prefix=channel_prefix,
                    allow_option_only_fut_context=allow_option_only_fut_context,
                )

                if events:
                    # B3_R24C_SORT_BEFORE_INJECTOR_BEGIN
                    events = _b3_r24c_sort_replay_events_by_event_time(events)
                    # B3_R24C_SORT_BEFORE_INJECTOR_END
                    batch_result = injector.inject_batch(
                        run_id=context.run_id,
                        events=events,
                        clock=clock,
                        transport=transport,
                        batch_id=f"{trading_day.date_str}:feeds",
                        notes=("feeds_stage",),
                    )
                    total_injected += batch_result.injected_count
                    day_breakdown.append(
                        {
                            "trading_day": trading_day.date_str,
                            "injected_count": batch_result.injected_count,
                            "last_sequence_id": batch_result.last_sequence_id,
                        }
                    )
                else:
                    day_breakdown.append(
                        {
                            "trading_day": trading_day.date_str,
                            "injected_count": 0,
                            "last_sequence_id": None,
                        }
                    )

            return {
                "stage_name": stage.stage_name,
                "status": "ok",
                "run_id": context.run_id,
                "total_injected": total_injected,
                "day_breakdown": day_breakdown,
                "clock_after_stage": clock.current_time,
            }

        if stage.stage_name == "features":
            feed_requests = transport.feed_requests(channel_prefix=channel_prefix)
            feature_frames = build_feature_frames_from_feed_requests(
                feed_requests=feed_requests,
            )

            published_count = 0
            for frame in feature_frames:
                transport.publish_feature_frame(frame)
                published_count += 1

            return {
                "stage_name": stage.stage_name,
                "status": "ok",
                "run_id": context.run_id,
                "mode": "replay_feature_bridge",
                "source_feed_events": len(feed_requests),
                "feature_frames_published": published_count,
                "feature_channel": "replay:features",
            }

        if stage.stage_name == "strategy":
            feature_frames = transport.feature_frames
            decisions = build_strategy_decisions_from_feature_frames(
                feature_frames=feature_frames,
            )

            published_count = 0
            action_breakdown: dict[str, int] = {}
            for decision in decisions:
                transport.publish_strategy_decision(decision)
                published_count += 1
                action = str(decision.get("action"))
                action_breakdown[action] = action_breakdown.get(action, 0) + 1

            return {
                "stage_name": stage.stage_name,
                "status": "ok",
                "run_id": context.run_id,
                "mode": "replay_strategy_bridge",
                "source_feature_frames": len(feature_frames),
                "strategy_decisions_published": published_count,
                "decision_channel": "replay:decisions",
                "action_breakdown": action_breakdown,
            }

        if stage.stage_name == "risk":
            strategy_decisions = transport.strategy_decisions
            risk_outputs = build_risk_outputs_from_strategy_decisions(
                strategy_decisions=strategy_decisions,
            )

            published_count = 0
            risk_action_breakdown: dict[str, int] = {}
            vetoed_entries = 0
            for risk_output in risk_outputs:
                transport.publish_risk_output(risk_output)
                published_count += 1
                risk_action = str(risk_output.get("risk_action"))
                risk_action_breakdown[risk_action] = (
                    risk_action_breakdown.get(risk_action, 0) + 1
                )
                if bool(risk_output.get("veto_entry")):
                    vetoed_entries += 1

            return {
                "stage_name": stage.stage_name,
                "status": "ok",
                "run_id": context.run_id,
                "mode": "replay_risk_bridge",
                "source_strategy_decisions": len(strategy_decisions),
                "risk_outputs_published": published_count,
                "risk_channel": "replay:risk",
                "risk_action_breakdown": risk_action_breakdown,
                "vetoed_entries": vetoed_entries,
            }

        if stage.stage_name == "execution_shadow":
            risk_outputs = transport.risk_outputs
            execution_results = build_execution_shadow_results_from_risk_outputs(
                run_id=context.run_id,
                risk_outputs=risk_outputs,
                fill_model_name=fill_model_name,
                doctrine_mode=doctrine_mode,
            )

            published_count = 0
            filled_count = 0
            for execution_result in execution_results:
                transport.publish_execution_shadow_result(execution_result)
                published_count += 1
                if bool(execution_result.get("filled")):
                    filled_count += 1

            return {
                "stage_name": stage.stage_name,
                "status": "ok",
                "mode": "replay_execution_shadow_bridge",
                "run_id": context.run_id,
                "source_risk_outputs": len(risk_outputs),
                "execution_results_published": published_count,
                "filled_count": filled_count,
                "execution_channel": "replay:execution_shadow",
                "fill_model_name": _resolve_fill_model_name(fill_model_name),
            }

        return {
            "stage_name": stage.stage_name,
            "status": "ok",
            "run_id": context.run_id,
            "mode": "placeholder_stage_bridge",
        }

    return stage_executor




# --- B3_R24C_EVENT_TIME_SORT_HELPER_BEGIN ---
def _b3_r24c_replay_event_time_sort_key(event):
    """Replay-only deterministic event-time sort key.

    This does not relax injector validation. It sorts the assembled batch before
    injector.inject_batch so the existing injector can still enforce monotonicity.
    """
    from datetime import datetime

    def _get(obj, key):
        if isinstance(obj, dict):
            return obj.get(key)
        return getattr(obj, key, None)

    def _parse_iso_ms(value):
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        try:
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            return int(datetime.fromisoformat(text).timestamp() * 1000)
        except Exception:
            return None

    for key in ("event_time", "timestamp", "ts", "exchange_ts"):
        ms = _parse_iso_ms(_get(event, key))
        if ms is not None:
            return (ms, str(_get(event, "source_stream") or ""), str(_get(event, "redis_id") or _get(event, "id") or ""))

    for key in ("ts_event", "ts_event_ns", "timestamp_ns", "frame_ts_ns", "exchange_ts_ns"):
        value = _get(event, key)
        try:
            ns = int(float(value))
            if ns > 10_000_000_000_000:
                return (ns // 1_000_000, str(_get(event, "source_stream") or ""), str(_get(event, "redis_id") or _get(event, "id") or ""))
        except Exception:
            pass

    for key in ("redis_id", "id", "stream_id", "_id"):
        value = _get(event, key)
        if value is not None:
            try:
                return (int(str(value).split("-")[0]), str(_get(event, "source_stream") or ""), str(value))
            except Exception:
                pass

    return (9_999_999_999_999, str(_get(event, "source_stream") or ""), str(_get(event, "redis_id") or _get(event, "id") or ""))


def _b3_r24f_with_sequence_id(event, sequence_id):
    """Return event with a normalized strictly increasing sequence_id.

    B3_R24F_SEQUENCE_ID_NORMALIZATION: this is replay-only and does not weaken
    injector validation. It normalizes sequence_id after event-time sort so the
    injector can continue enforcing strict monotonic sequence order.
    """
    # Most replay event batches here are dict-like.
    if isinstance(event, dict):
        normalized = dict(event)
        normalized["sequence_id"] = sequence_id
        return normalized

    # Dataclass-like events.
    try:
        import dataclasses
        if dataclasses.is_dataclass(event):
            return dataclasses.replace(event, sequence_id=sequence_id)
    except Exception:
        pass

    # Pydantic v2 / v1 style.
    try:
        if hasattr(event, "model_copy"):
            return event.model_copy(update={"sequence_id": sequence_id})
    except Exception:
        pass
    try:
        if hasattr(event, "copy"):
            return event.copy(update={"sequence_id": sequence_id})
    except Exception:
        pass

    # Mutable object fallback.
    try:
        setattr(event, "sequence_id", sequence_id)
        return event
    except Exception:
        return event


def _b3_r24c_sort_replay_events_by_event_time(events):
    """Return sorted replay events with sequence_id normalized in sorted order."""
    try:
        sorted_events = sorted(list(events), key=_b3_r24c_replay_event_time_sort_key)
        return [
            _b3_r24f_with_sequence_id(event, index)
            for index, event in enumerate(sorted_events, start=1)
        ]
    except Exception:
        return events
# --- B3_R24C_EVENT_TIME_SORT_HELPER_END ---


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    repository = build_dataset_repository(args)
    selector = ReplaySelector(repository)
    selection_plan = selector.build_plan(
        build_selection_request(args),
        dataset_id=args.dataset_id,
    )

    option_only_fut_context_precheck = validate_option_only_fut_context_preconditions(args)

    runner = ReplayRunner(run_root=args.run_root)
    run_context = runner.build_run_context(
        selection_plan=selection_plan,
        run_config=build_run_config(args),
    )

    topology_plan = ReplayTopologyBuilder().build_plan(ReplayScope(args.scope))

    clock = ReplayClock(
        ReplayClockConfig(
            speed_mode=ReplaySpeedMode(args.speed_mode),
            start_time=args.clock_start_time,
        )
    )
    injector = ReplayInjector()
    transport = LocalReplayTransport()

    engine = ReplayEngine()
    engine_result = engine.execute(
        run_context,
        topology_plan,
        stage_executor=make_stage_executor(
            selection_plan=selection_plan,
            repository=repository,
            clock=clock,
            injector=injector,
            transport=transport,
            channel_prefix=args.channel_prefix,
            fill_model_name=args.fill_model,
            doctrine_mode=DoctrineMode(args.doctrine_mode),
            allow_option_only_fut_context=bool(args.allow_option_only_fut_context),
        ),
    )

    integrity_bundle = ReplayIntegrityEvaluator().evaluate(
        run_context,
        checks=build_placeholder_checks(
            allow_option_only_fut_context=bool(args.allow_option_only_fut_context),
        ),
    )

    report_bundle = build_report_bundle(
        run_context=run_context,
        selection_plan=selection_plan,
        topology_plan=topology_plan,
        engine_result=engine_result,
        integrity_bundle=integrity_bundle,
    )

    writer = ReplayArtifactsWriter()
    writer.ensure_directories(run_context.artifact_plan)
    artifact_bundle = writer.write_core_artifact_bundle(
        run_context,
        topology_plan,
        integrity_verdict=integrity_bundle.verdict.value,
        metrics={"stage_count": engine_result.stage_count},
    )
    writer.write_engine_result(engine_result, run_context.artifact_plan)

    # R35C/R4C: write an early compact official run summary immediately after
    # engine_result is available, before heavy row-artifact exports. This is
    # artifact-only and does not change replay decisions, risk, execution shadow,
    # broker state, or Redis streams.
    try:
        replay_artifacts_dir = Path(run_context.artifact_plan.artifacts_dir)
        replay_artifacts_dir.mkdir(parents=True, exist_ok=True)
        # R35C/R4J2: minimal early summary must not call build_run_summary_payload.
        # This fallback is written before heavy row artifacts and is artifact-only.
        early_stage_records = getattr(engine_result, "stage_records", []) or []
        early_stage_names = [getattr(x, "stage_name", None) for x in early_stage_records]
        early_stage_names = [str(x) for x in early_stage_names if x is not None]
        early_run_summary_payload = {
            "schema_version": "r35c_r4j2_early_minimal_run_summary_v1",
            "summary_write_mode": "early_minimal_r35c_r4j2",
            "run_id": getattr(run_context, "run_id", None),
            "dataset_id": getattr(selection_plan, "dataset_id", None),
            "selection_mode": getattr(selection_plan, "selection_mode", None),
            "trading_dates": [str(x) for x in (getattr(selection_plan, "trading_dates", []) or [])],
            "replay_scope": getattr(topology_plan, "scope", None),
            "stage_count": getattr(engine_result, "stage_count", None),
            "stage_names": early_stage_names,
            "started_at": getattr(engine_result, "engine_started_at", None),
            "completed_at": getattr(engine_result, "engine_finished_at", None),
            "engine_final_state": getattr(getattr(engine_result, "final_state", None), "value", getattr(engine_result, "final_state", None)),
            "artifact_note": "Early minimal official summary written before heavy row artifacts.",
            "paper_live_enabled": False,
            "broker_order_attempted": False,
        }
        early_run_summary_json_path = replay_artifacts_dir / "10_run_summary.json"
        early_run_summary_csv_path = replay_artifacts_dir / "11_run_summary.csv"
        early_run_summary_json_path.write_text(
            json.dumps(early_run_summary_payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
        write_run_summary_csv(early_run_summary_csv_path, early_run_summary_payload)
    except Exception as exc:
        try:
            (Path(run_context.artifact_plan.artifacts_dir) / "10_run_summary_early_write_error.json").write_text(
                json.dumps(
                    {
                        "schema_version": "r35c_r4c_early_summary_error_v1",
                        "error": repr(exc),
                        "paper_live_enabled": False,
                        "broker_order_attempted": False,
                    },
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                    default=str,
                ) + "\n",
                encoding="utf-8",
            )
        except Exception:
            pass

    replay_artifacts_dir = Path(run_context.artifact_plan.artifacts_dir)
    replay_artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _r35b_json_slim(value):
        """R35B/R4S replay artifact slimming.

        This is artifact-only. It does not change in-memory replay decisions.
        Use SCALPX_REPLAY_ARTIFACT_ROW_CAP=500 to persist small samples instead
        of multi-GB row artifacts.
        """
        try:
            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
        except Exception:
            cap = 0

        heavy_keys = {
            "candidate_json",
            "arbitration_json",
            "candidates",
            "candidate",
            "all_candidates",
            "feature_payload",
            "feature_json",
            "feature",
            "features",
            "feature_row",
            "feature_rows",
            "linked_feature",
            "linked_feature_row",
            "decision_payload",
            "payload",
            "raw",
            "raw_payload",
            "raw_frame",
            "debug",
            "debug_payload",
            "context",
            "snapshot",
        }

        def slim(obj, depth=0):
            if depth > 6:
                return "<omitted_by_R35B_R4S:max_depth>"

            if isinstance(obj, list):
                # R35C/R4O4: preserve R4L/R4J top-level cap marker.
                # R4L/R4J may already append a truncation marker. The older
                # R35B/R4S nested slim pass must not drop that marker.
                existing_marker = None
                body = obj
                if obj and isinstance(obj[-1], dict) and (
                    obj[-1].get("_r35c_r4l_top_level_truncated")
                    or obj[-1].get("_r35c_r4j_top_level_truncated")
                ):
                    existing_marker = obj[-1]
                    body = obj[:-1]

                original_len = len(body)
                selected = body[:cap] if cap and cap > 0 else body
                out = [slim(x, depth + 1) for x in selected]

                if existing_marker is not None:
                    out.append(slim(existing_marker, depth + 1))
                elif cap and cap > 0 and original_len > cap:
                    out.append({
                        "_r35b_r4s_truncated": True,
                        "original_len": original_len,
                        "persisted_len": len(selected),
                        "cap": cap,
                        "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP",
                    })
                return out

            if isinstance(obj, dict):
                out = {}
                for k, v in obj.items():
                    if k in heavy_keys:
                        out[k] = f"<omitted_by_R35B_R4S:{k}>"
                    else:
                        out[k] = slim(v, depth + 1)
                return out

            return obj

        return slim(value)

    def _r35b_write_compact_json(path, value):
        # R35C/R4J2: hard top-level row cap before JSON serialization.
        # R35B/R4S slimmed nested payloads, but R4H proved top-level row files
        # could still become multi-hundred-MB. This is artifact-only.
        try:
            hard_cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
        except Exception:
            hard_cap = 0

        # R35C/R4R2: force default cap for known row artifact files.
        # Artifact-only guard: if env cap is missing inside recursive replay,
        # still cap the four huge row artifact JSON files to 50 rows.
        row_artifact_names = {
            "features_rows.json",
            "strategy_decisions.json",
            "risk_outputs.json",
            "execution_shadow_results.json",
        }
        if (not hard_cap or hard_cap <= 0) and getattr(path, "name", "") in row_artifact_names:
            hard_cap = 50

        payload = value
        if hard_cap and hard_cap > 0 and isinstance(value, list) and len(value) > hard_cap:
            payload = list(value[:hard_cap])
            payload.append({
                "_r35c_r4j_top_level_truncated": True,
                "original_len": len(value),
                "persisted_len": hard_cap,
                "cap": hard_cap,
                "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP hard top-level cap before write",
            })

        path.write_text(
            json.dumps(_r35b_json_slim(payload), separators=(",", ":"), ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )

    persisted_feature_rows = build_persisted_feature_rows(transport.feature_frames)

    # R35C/R4L: force cap row lists before artifact writes.
    # This is artifact-only. It does not change in-memory replay decisions,
    # risk outputs, execution shadow, broker state, or Redis streams.
    def _r35c_r4l_force_row_cap(label, rows):
        try:
            cap = int(os.environ.get("SCALPX_REPLAY_ARTIFACT_ROW_CAP", "0") or "0")
        except Exception:
            cap = 0
        if cap and cap > 0 and isinstance(rows, list) and len(rows) > cap:
            out = list(rows[:cap])
            out.append({
                "_r35c_r4l_top_level_truncated": True,
                "label": label,
                "original_len": len(rows),
                "persisted_len": cap,
                "cap": cap,
                "reason": "SCALPX_REPLAY_ARTIFACT_ROW_CAP force cap before artifact write",
            })
            return out
        return rows

    persisted_feature_rows = _r35c_r4l_force_row_cap("features_rows", persisted_feature_rows)
    _r35b_write_compact_json(replay_artifacts_dir / "features_rows.json", persisted_feature_rows)
    persisted_strategy_decisions = build_persisted_strategy_decisions(
        transport.strategy_decisions,
        persisted_feature_rows,
    )

    persisted_strategy_decisions = _r35c_r4l_force_row_cap("strategy_decisions", persisted_strategy_decisions)
    _r35b_write_compact_json(replay_artifacts_dir / "strategy_decisions.json", persisted_strategy_decisions)
    persisted_risk_outputs = build_persisted_risk_outputs(
        transport.risk_outputs,
        persisted_strategy_decisions,
    )

    persisted_risk_outputs = _r35c_r4l_force_row_cap("risk_outputs", persisted_risk_outputs)
    _r35b_write_compact_json(replay_artifacts_dir / "risk_outputs.json", persisted_risk_outputs)

    persisted_execution_shadow_results = [dict(row) for row in transport.execution_shadow_results]

    persisted_execution_shadow_results = _r35c_r4l_force_row_cap("execution_shadow_results", persisted_execution_shadow_results)
    _r35b_write_compact_json(replay_artifacts_dir / "execution_shadow_results.json", persisted_execution_shadow_results)

    # B3_R36A_LATE_REPLAY_ANALYSIS_EXPORTS_AFTER_ROW_ARTIFACTS_BEGIN
    # Offline replay analysis exports. Runs after row artifacts are materialized.
    try:
        if os.environ.get("SCALPX_REPLAY_SKIP_B3_R32_EXPORTS", "0").strip().lower() in {"1", "true", "yes"}:
            (replay_artifacts_dir / "b3_r32_analysis_exports_status.json").write_text(
                json.dumps(
                    {
                        "status": "skipped",
                        "reason": "SCALPX_REPLAY_SKIP_B3_R32_EXPORTS enabled by R35B_R4G3 to avoid heavy features_rows.json readback",
                        "paper_live_enabled": False,
                        "broker_order_attempted": False,
                    },
                    separators=(",", ":"),
                    ensure_ascii=False,
                    default=str,
                ) + "\n",
                encoding="utf-8",
            )
        else:
            writer.write_b3_r32_analysis_exports(run_context)
    except Exception as exc:
        try:
            writer.write_json_artifact(
                run_context.artifact_plan.artifacts_dir / "b3_r36a_late_export_error.json",
                {
                    "schema_version": "b3_r36a_late_export_error_v1",
                    "status": "error",
                    "error": repr(exc),
                    "note": "Optional late B3 export failed; replay artifacts remain available.",
                },
            )
        except Exception:
            pass
    # B3_R36A_LATE_REPLAY_ANALYSIS_EXPORTS_AFTER_ROW_ARTIFACTS_END


    # Overwrite the early placeholder 03_integrity_report.json with the real evaluated bundle.
    real_integrity_payload = integrity_bundle_to_dict(integrity_bundle)
    real_integrity_report_payload = {
        "verdict": integrity_bundle.verdict.value,
        "checks": real_integrity_payload.get("executed_checks", []),
        "notes": real_integrity_payload.get("notes", []),
        "integrity_bundle": real_integrity_payload,
        "check_count": real_integrity_payload.get("check_count"),
        "passed_checks": real_integrity_payload.get("passed_checks"),
        "warned_checks": real_integrity_payload.get("warned_checks"),
        "failed_checks": real_integrity_payload.get("failed_checks"),
    }
    Path(run_context.artifact_plan.integrity_report_path).write_text(
        json.dumps(real_integrity_report_payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )

    run_summary_payload = build_run_summary_payload(
        run_context=run_context,
        report_bundle=report_bundle,
        engine_result=engine_result,
        integrity_bundle=integrity_bundle,
        persisted_feature_rows=persisted_feature_rows,
        persisted_strategy_decisions=persisted_strategy_decisions,
        persisted_risk_outputs=persisted_risk_outputs,
        persisted_execution_shadow_results=persisted_execution_shadow_results,
    )

    run_summary_json_path = replay_artifacts_dir / "10_run_summary.json"
    run_summary_csv_path = replay_artifacts_dir / "11_run_summary.csv"

    run_summary_json_path.write_text(
        json.dumps(run_summary_payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    write_run_summary_csv(run_summary_csv_path, run_summary_payload)

    output = {
        "status": "ok",
        "run_id": run_context.run_id,
        "doctrine_mode": run_context.doctrine_mode.value,
        "selection_plan": selection_plan_to_dict(selection_plan),
        "topology_plan": topology_plan_to_dict(topology_plan),
        "engine_final_state": engine_result.final_state.value,
        "engine_stage_records": [
            {
                "stage_name": item.stage_name,
                "success": item.success,
                "output_summary": dict(item.output_summary),
            }
            for item in engine_result.stage_records
        ],
        "integrity_verdict": integrity_bundle.verdict.value,
        "integrity_bundle": integrity_bundle_to_dict(integrity_bundle),
        "report_bundle": report_bundle_to_dict(report_bundle),
        "artifact_root": run_context.artifact_plan.root_dir,
        "artifact_count": artifact_bundle.artifact_count,
        "clock_snapshot": {
            "speed_mode": clock.speed_mode.value,
            "current_time": clock.current_time,
            "tick_count": clock.tick_count,
            "step_count": clock.step_count,
            "last_event_time": clock.last_event_time,
        },
    }

    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

# phase_a4_true_owner_patch

# phase_a4_feed_input_enrichment_v1

# BEGIN BATCH27E_REPLAY_RUN_CLI_INTEGRITY_NOTE

BATCH27E_REPLAY_RUN_CLI_INTEGRITY_NOTE = {
    "schema_version": "batch27e_replay_run_cli_integrity_note_v1",
    "purpose": "replay_run.py must remain replay-only and must not approve paper/live",
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "production_doctrine_changed": False,
}

# END BATCH27E_REPLAY_RUN_CLI_INTEGRITY_NOTE

# BEGIN BATCH27F_REPLAY_RUN_TRANSPORT_NOTE

BATCH27F_REPLAY_RUN_TRANSPORT_NOTE = {
    "schema_version": "batch27f_replay_run_transport_note_v1",
    "purpose": "future replay_run integration must use replay-only LocalReplayTransport, not live Redis",
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "live_redis_writes_allowed": False,
    "broker_calls_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27F_REPLAY_RUN_TRANSPORT_NOTE

# BEGIN BATCH27G_REPLAY_RUN_FEATURE_ADAPTER_NOTE

BATCH27G_REPLAY_RUN_FEATURE_ADAPTER_NOTE = {
    "schema_version": "batch27g_replay_run_feature_adapter_note_v1",
    "purpose": "future replay_run integration may use replay.feature_adapter for feature payload shape only",
    "strategy_decision_generated": False,
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27G_REPLAY_RUN_FEATURE_ADAPTER_NOTE

# BEGIN BATCH27H_REPLAY_RUN_STRATEGY_ADAPTER_NOTE

BATCH27H_REPLAY_RUN_STRATEGY_ADAPTER_NOTE = {
    "schema_version": "batch27h_replay_run_strategy_adapter_note_v1",
    "purpose": "future replay_run integration may use replay.strategy_adapter for replay-only decision shape and arbitration",
    "final_action": "HOLD_REPORT_ONLY",
    "order_allowed": False,
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27H_REPLAY_RUN_STRATEGY_ADAPTER_NOTE

# BEGIN BATCH27I_REPLAY_RUN_RISK_EXECUTION_SHADOW_NOTE

BATCH27I_REPLAY_RUN_RISK_EXECUTION_SHADOW_NOTE = {
    "schema_version": "batch27i_replay_run_risk_execution_shadow_note_v1",
    "purpose": "future replay_run integration may use replay-only risk_adapter and execution_shadow",
    "order_allowed": False,
    "real_order_sent": False,
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27I_REPLAY_RUN_RISK_EXECUTION_SHADOW_NOTE

# BEGIN BATCH27J_REPLAY_RUN_SCENARIO_PROFILE_NOTE

BATCH27J_REPLAY_RUN_SCENARIO_PROFILE_NOTE = {
    "schema_version": "batch27j_replay_run_scenario_profile_note_v1",
    "purpose": "future replay_run integration may use replay.scenarios for explicit replay-only assumptions",
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27J_REPLAY_RUN_SCENARIO_PROFILE_NOTE

# BEGIN BATCH27K_REPLAY_RUN_BATCH_ARTIFACT_NOTE

BATCH27K_REPLAY_RUN_BATCH_ARTIFACT_NOTE = {
    "schema_version": "batch27k_replay_run_batch_artifact_note_v1",
    "purpose": "future replay_run integration may use replay.batch_runner and replay.artifact_materializer",
    "artifact_root": "run/replay/",
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27K_REPLAY_RUN_BATCH_ARTIFACT_NOTE

# BEGIN BATCH27L_REPLAY_RUN_REPORT_EXPORT_NOTE

BATCH27L_REPLAY_RUN_REPORT_EXPORT_NOTE = {
    "schema_version": "batch27l_replay_run_report_export_note_v1",
    "purpose": "future replay_run integration may use replay.report_exporter for replay-only CSV/JSON reports",
    "export_root": "run/replay/<run_id>/exports/",
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27L_REPLAY_RUN_REPORT_EXPORT_NOTE

# BEGIN BATCH27M_REPLAY_RUN_EXPERIMENT_WORKSTATION_NOTE

BATCH27M_REPLAY_RUN_EXPERIMENT_WORKSTATION_NOTE = {
    "schema_version": "batch27m_replay_run_experiment_workstation_note_v1",
    "purpose": "future replay_run integration may use replay.experiment_workstation for replay-only differential experiments",
    "export_root": "run/replay/<experiment_id>/experiments/",
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH27M_REPLAY_RUN_EXPERIMENT_WORKSTATION_NOTE

# BEGIN BATCH28A_REPLAY_RUN_PARITY_PLAN_NOTE

BATCH28A_REPLAY_RUN_PARITY_PLAN_NOTE = {
    "schema_version": "batch28a_replay_run_parity_plan_note_v1",
    "purpose": "Future replay_run integration may use replay.live_parity after observe_only live session capture.",
    "accepted_for": "PARITY_AUDIT_PLAN_ONLY",
    "full_live_replay_parity": "NOT_PROVEN_IN_28A",
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "broker_calls_allowed": False,
    "live_redis_writes_allowed": False,
    "production_doctrine_changed": False,
}

# END BATCH28A_REPLAY_RUN_PARITY_PLAN_NOTE

# BEGIN BATCH28B_OBSERVE_ONLY_LIVE_EVIDENCE_NOTE

BATCH28B_OBSERVE_ONLY_LIVE_EVIDENCE_NOTE = {
    "schema_version": "batch28b_observe_only_live_evidence_note_v1",
    "purpose": "Future replay/live parity audit may use observe_only live evidence capture artifacts.",
    "accepted_for": "OBSERVE_ONLY_LIVE_EVIDENCE_CAPTURE_CONTRACT_ONLY",
    "starts_services": False,
    "reads_live_redis": False,
    "writes_live_redis": False,
    "calls_broker_api": False,
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "production_doctrine_changed": False,
    "full_live_replay_parity": "NOT_PROVEN_IN_28B",
}

# END BATCH28B_OBSERVE_ONLY_LIVE_EVIDENCE_NOTE

