"""
app/mme_scalpx/replay/selectors.py

Freeze-grade replay selection layer for the MME-ScalpX Permanent Replay &
Validation Framework.

R2 Dataset Foundation
---------------------
This module owns:
- replay trading-day selection from dataset truth
- selection-plan creation for single day / range / custom list / batches
- intraday window validation
- session-segment validation
- deterministic output ordering
- selection metadata for manifests and reports

This module does not own:
- dataset discovery/loading internals
- replay clock mechanics
- replay injection/orchestration
- experiment overrides
- report generation
- doctrine logic
- live runtime mutation

Design rules
------------
- selection must be fact-based on discovered dataset truth
- outputs must be deterministic and auditable
- no hidden mutation of dataset state
- no casual assumptions about missing dates
- all invalid requests should fail explicitly
- selection must be reusable by locked, shadow, and differential replay equally
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Any, Mapping, Sequence

from .dataset import (
    DATASET_DATE_RE,
    ReplayDatasetRepository,
    ReplayDatasetSummary,
    ReplayTradingDay,
    dataset_summary_to_dict,
    trading_day_to_dict,
)
from .modes import ReplaySelectionMode


class ReplaySelectionError(RuntimeError):
    """Base exception for replay selection failures."""


class ReplaySelectionValidationError(ReplaySelectionError):
    """Raised when a replay selection request is invalid."""


class ReplaySelectionUnavailableError(ReplaySelectionError):
    """Raised when requested dates/windows are unavailable in dataset truth."""


SESSION_SEGMENT_OPENING = "opening"
SESSION_SEGMENT_MORNING = "morning"
SESSION_SEGMENT_MIDDAY = "midday"
SESSION_SEGMENT_AFTERNOON = "afternoon"
SESSION_SEGMENT_CLOSING = "closing"
SESSION_SEGMENT_FULL = "full"

DEFAULT_SESSION_SEGMENTS: Mapping[str, tuple[str, str]] = {
    SESSION_SEGMENT_OPENING: ("09:15:00", "09:45:00"),
    SESSION_SEGMENT_MORNING: ("09:45:00", "11:30:00"),
    SESSION_SEGMENT_MIDDAY: ("11:30:00", "13:30:00"),
    SESSION_SEGMENT_AFTERNOON: ("13:30:00", "14:45:00"),
    SESSION_SEGMENT_CLOSING: ("14:45:00", "15:30:00"),
    SESSION_SEGMENT_FULL: ("09:15:00", "15:30:00"),
}


@dataclass(frozen=True, slots=True)
class ReplayTimeWindow:
    """Canonical intraday window for replay selection."""

    start: str | None = None
    end: str | None = None


@dataclass(frozen=True, slots=True)
class ReplaySelectionRequest:
    """
    Input request for building a replay selection plan.
    """

    selection_mode: ReplaySelectionMode
    single_day: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    custom_dates: tuple[str, ...] = field(default_factory=tuple)
    intraday_window: ReplayTimeWindow = field(default_factory=ReplayTimeWindow)
    session_segment: str | None = None
    weekdays: tuple[int, ...] = field(default_factory=tuple)
    months: tuple[int, ...] = field(default_factory=tuple)
    market_tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplaySelectionPlan:
    """
    Canonical resolved replay selection plan.
    """

    selection_mode: ReplaySelectionMode
    trading_dates: tuple[str, ...]
    intraday_window: ReplayTimeWindow
    session_segment: str | None
    market_tags: tuple[str, ...]
    dataset_summary: ReplayDatasetSummary
    selected_days: tuple[ReplayTradingDay, ...]
    selection_fingerprint: str
    selection_notes: tuple[str, ...] = field(default_factory=tuple)


class ReplaySelector:
    """
    Deterministic replay selector built on dataset truth.
    """

    def __init__(
        self,
        repository: ReplayDatasetRepository,
        *,
        session_segments: Mapping[str, tuple[str, str]] | None = None,
    ) -> None:
        self._repository = repository
        self._session_segments = _normalize_session_segments(
            session_segments or DEFAULT_SESSION_SEGMENTS
        )

    @property
    def repository(self) -> ReplayDatasetRepository:
        return self._repository

    @property
    def session_segments(self) -> Mapping[str, tuple[str, str]]:
        return self._session_segments

    def build_plan(
        self,
        request: ReplaySelectionRequest,
        *,
        dataset_id: str | None = None,
        dataset_notes: Sequence[str] | None = None,
        selection_notes: Sequence[str] | None = None,
    ) -> ReplaySelectionPlan:
        _validate_request(request, self._session_segments)

        dataset_summary = self._repository.build_dataset_summary(
            dataset_id=dataset_id,
            notes=dataset_notes,
        )

        available_dates = dataset_summary.trading_days
        selected_dates = self._resolve_dates(request, available_dates)
        selected_days = tuple(self._repository.load_trading_day(x) for x in selected_dates)
        resolved_window, resolved_segment = self._resolve_window_and_segment(request)

        fingerprint_payload = {
            "selection_mode": request.selection_mode.value,
            "trading_dates": list(selected_dates),
            "intraday_window": {
                "start": resolved_window.start,
                "end": resolved_window.end,
            },
            "session_segment": resolved_segment,
            "market_tags": list(request.market_tags),
            "dataset_summary": dataset_summary_to_dict(dataset_summary),
            "selected_days": [trading_day_to_dict(day) for day in selected_days],
        }

        selection_fingerprint = _stable_sha256_json(fingerprint_payload)

        return ReplaySelectionPlan(
            selection_mode=request.selection_mode,
            trading_dates=selected_dates,
            intraday_window=resolved_window,
            session_segment=resolved_segment,
            market_tags=request.market_tags,
            dataset_summary=dataset_summary,
            selected_days=selected_days,
            selection_fingerprint=selection_fingerprint,
            selection_notes=tuple(selection_notes or ()),
        )

    def _resolve_dates(
        self,
        request: ReplaySelectionRequest,
        available_dates: Sequence[str],
    ) -> tuple[str, ...]:
        available = tuple(available_dates)
        available_set = set(available)

        mode = request.selection_mode

        if mode is ReplaySelectionMode.SINGLE_DAY:
            assert request.single_day is not None
            if request.single_day not in available_set:
                raise ReplaySelectionUnavailableError(
                    f"requested single_day not present in dataset: {request.single_day}"
                )
            return (request.single_day,)

        if mode is ReplaySelectionMode.DATE_RANGE:
            assert request.start_date is not None
            assert request.end_date is not None
            selected = tuple(
                date_str
                for date_str in available
                if request.start_date <= date_str <= request.end_date
            )
            if not selected:
                raise ReplaySelectionUnavailableError(
                    f"no trading days found in range {request.start_date} .. {request.end_date}"
                )
            return selected

        if mode is ReplaySelectionMode.CUSTOM_DATE_LIST:
            selected = tuple(dict.fromkeys(request.custom_dates))
            missing = [date_str for date_str in selected if date_str not in available_set]
            if missing:
                raise ReplaySelectionUnavailableError(
                    f"custom dates not present in dataset: {missing}"
                )
            return tuple(sorted(selected))

        if mode is ReplaySelectionMode.INTRADAY_WINDOW:
            assert request.single_day is not None
            if request.single_day not in available_set:
                raise ReplaySelectionUnavailableError(
                    f"requested single_day not present in dataset: {request.single_day}"
                )
            return (request.single_day,)

        if mode is ReplaySelectionMode.SESSION_SEGMENT:
            assert request.single_day is not None
            if request.single_day not in available_set:
                raise ReplaySelectionUnavailableError(
                    f"requested single_day not present in dataset: {request.single_day}"
                )
            return (request.single_day,)

        if mode is ReplaySelectionMode.WEEKDAY_BATCH:
            selected = tuple(
                date_str
                for date_str in available
                if _date_to_weekday(date_str) in request.weekdays
            )
            if not selected:
                raise ReplaySelectionUnavailableError(
                    f"no trading days matched weekday batch filter: {request.weekdays}"
                )
            return selected

        if mode is ReplaySelectionMode.MONTHLY_BATCH:
            selected = tuple(
                date_str
                for date_str in available
                if _date_to_month(date_str) in request.months
            )
            if not selected:
                raise ReplaySelectionUnavailableError(
                    f"no trading days matched monthly batch filter: {request.months}"
                )
            return selected

        raise ReplaySelectionValidationError(
            f"unsupported selection_mode: {request.selection_mode!r}"
        )

    def _resolve_window_and_segment(
        self,
        request: ReplaySelectionRequest,
    ) -> tuple[ReplayTimeWindow, str | None]:
        if request.session_segment is not None:
            start, end = self._session_segments[request.session_segment]
            segment_window = ReplayTimeWindow(start=start, end=end)

            if request.intraday_window.start is not None or request.intraday_window.end is not None:
                if request.intraday_window != segment_window:
                    raise ReplaySelectionValidationError(
                        "intraday_window and session_segment conflict"
                    )

            return segment_window, request.session_segment

        if request.intraday_window.start is not None or request.intraday_window.end is not None:
            return request.intraday_window, None

        return ReplayTimeWindow(), None


def build_selection_plan(
    repository: ReplayDatasetRepository,
    request: ReplaySelectionRequest,
    *,
    dataset_id: str | None = None,
    dataset_notes: Sequence[str] | None = None,
    selection_notes: Sequence[str] | None = None,
    session_segments: Mapping[str, tuple[str, str]] | None = None,
) -> ReplaySelectionPlan:
    selector = ReplaySelector(repository, session_segments=session_segments)
    return selector.build_plan(
        request,
        dataset_id=dataset_id,
        dataset_notes=dataset_notes,
        selection_notes=selection_notes,
    )


def selection_plan_to_dict(plan: ReplaySelectionPlan) -> dict[str, Any]:
    return {
        "selection_mode": plan.selection_mode.value,
        "trading_dates": list(plan.trading_dates),
        "intraday_window": {
            "start": plan.intraday_window.start,
            "end": plan.intraday_window.end,
        },
        "session_segment": plan.session_segment,
        "market_tags": list(plan.market_tags),
        "dataset_summary": dataset_summary_to_dict(plan.dataset_summary),
        "selected_days": [trading_day_to_dict(day) for day in plan.selected_days],
        "selection_fingerprint": plan.selection_fingerprint,
        "selection_notes": list(plan.selection_notes),
    }


def _validate_request(
    request: ReplaySelectionRequest,
    session_segments: Mapping[str, tuple[str, str]],
) -> None:
    _validate_market_tags(request.market_tags)
    _validate_intraday_window(request.intraday_window)

    if request.single_day is not None:
        _validate_date_str(request.single_day)
    if request.start_date is not None:
        _validate_date_str(request.start_date)
    if request.end_date is not None:
        _validate_date_str(request.end_date)
    for item in request.custom_dates:
        _validate_date_str(item)

    if request.start_date and request.end_date and request.start_date > request.end_date:
        raise ReplaySelectionValidationError(
            f"start_date must be <= end_date, got {request.start_date} > {request.end_date}"
        )

    if request.session_segment is not None and request.session_segment not in session_segments:
        raise ReplaySelectionValidationError(
            f"unknown session_segment: {request.session_segment!r}"
        )

    if request.selection_mode is ReplaySelectionMode.SINGLE_DAY:
        _require_only(
            request,
            required=("single_day",),
            mode_name="single_day",
        )
        return

    if request.selection_mode is ReplaySelectionMode.DATE_RANGE:
        _require_only(
            request,
            required=("start_date", "end_date"),
            mode_name="date_range",
            allow_market_tags=True,
        )
        return

    if request.selection_mode is ReplaySelectionMode.CUSTOM_DATE_LIST:
        if not request.custom_dates:
            raise ReplaySelectionValidationError(
                "custom_date_list mode requires custom_dates"
            )
        _forbid_fields(
            request,
            forbidden=("single_day", "start_date", "end_date", "weekdays", "months"),
            mode_name="custom_date_list",
        )
        return

    if request.selection_mode is ReplaySelectionMode.INTRADAY_WINDOW:
        if request.single_day is None:
            raise ReplaySelectionValidationError(
                "intraday_window mode requires single_day"
            )
        if request.intraday_window.start is None or request.intraday_window.end is None:
            raise ReplaySelectionValidationError(
                "intraday_window mode requires intraday_window.start and intraday_window.end"
            )
        _forbid_fields(
            request,
            forbidden=("start_date", "end_date", "custom_dates", "weekdays", "months"),
            mode_name="intraday_window",
        )
        if request.session_segment is not None:
            raise ReplaySelectionValidationError(
                "intraday_window mode must not also set session_segment"
            )
        return

    if request.selection_mode is ReplaySelectionMode.SESSION_SEGMENT:
        if request.single_day is None:
            raise ReplaySelectionValidationError(
                "session_segment mode requires single_day"
            )
        if request.session_segment is None:
            raise ReplaySelectionValidationError(
                "session_segment mode requires session_segment"
            )
        _forbid_fields(
            request,
            forbidden=("start_date", "end_date", "custom_dates", "weekdays", "months"),
            mode_name="session_segment",
        )
        return

    if request.selection_mode is ReplaySelectionMode.WEEKDAY_BATCH:
        if not request.weekdays:
            raise ReplaySelectionValidationError(
                "weekday_batch mode requires weekdays"
            )
        _validate_weekdays(request.weekdays)
        _forbid_fields(
            request,
            forbidden=("single_day", "start_date", "end_date", "custom_dates", "months"),
            mode_name="weekday_batch",
            allow_window=True,
            allow_market_tags=True,
        )
        return

    if request.selection_mode is ReplaySelectionMode.MONTHLY_BATCH:
        if not request.months:
            raise ReplaySelectionValidationError(
                "monthly_batch mode requires months"
            )
        _validate_months(request.months)
        _forbid_fields(
            request,
            forbidden=("single_day", "start_date", "end_date", "custom_dates", "weekdays"),
            mode_name="monthly_batch",
            allow_window=True,
            allow_market_tags=True,
        )
        return

    raise ReplaySelectionValidationError(
        f"unsupported selection_mode: {request.selection_mode!r}"
    )


def _require_only(
    request: ReplaySelectionRequest,
    *,
    required: Sequence[str],
    mode_name: str,
    allow_window: bool = False,
    allow_market_tags: bool = False,
) -> None:
    required_set = set(required)

    values = {
        "single_day": request.single_day,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "custom_dates": request.custom_dates,
        "weekdays": request.weekdays,
        "months": request.months,
        "session_segment": request.session_segment,
    }

    for field_name in required:
        value = values[field_name]
        if value is None or value == ():
            raise ReplaySelectionValidationError(
                f"{mode_name} mode requires {field_name}"
            )

    forbidden = set(values.keys()) - required_set
    if allow_window:
        forbidden.discard("session_segment")
    for field_name in sorted(forbidden):
        value = values[field_name]
        if value is not None and value != ():
            raise ReplaySelectionValidationError(
                f"{mode_name} mode must not set {field_name}"
            )

    if not allow_window:
        if request.intraday_window.start is not None or request.intraday_window.end is not None:
            raise ReplaySelectionValidationError(
                f"{mode_name} mode must not set intraday_window"
            )

    if not allow_market_tags and request.market_tags:
        raise ReplaySelectionValidationError(
            f"{mode_name} mode must not set market_tags"
        )


def _forbid_fields(
    request: ReplaySelectionRequest,
    *,
    forbidden: Sequence[str],
    mode_name: str,
    allow_window: bool = False,
    allow_market_tags: bool = False,
) -> None:
    values = {
        "single_day": request.single_day,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "custom_dates": request.custom_dates,
        "weekdays": request.weekdays,
        "months": request.months,
    }

    for field_name in forbidden:
        value = values[field_name]
        if value is not None and value != ():
            raise ReplaySelectionValidationError(
                f"{mode_name} mode must not set {field_name}"
            )

    if not allow_window:
        if request.intraday_window.start is not None or request.intraday_window.end is not None:
            raise ReplaySelectionValidationError(
                f"{mode_name} mode must not set intraday_window"
            )

    if not allow_market_tags and request.market_tags:
        raise ReplaySelectionValidationError(
            f"{mode_name} mode must not set market_tags"
        )


def _validate_intraday_window(window: ReplayTimeWindow) -> None:
    if window.start is None and window.end is None:
        return
    if window.start is None or window.end is None:
        raise ReplaySelectionValidationError(
            "intraday_window must provide both start and end, or neither"
        )

    start_t = _parse_time_str(window.start)
    end_t = _parse_time_str(window.end)
    if start_t >= end_t:
        raise ReplaySelectionValidationError(
            f"intraday_window start must be < end, got {window.start} >= {window.end}"
        )


def _normalize_session_segments(
    session_segments: Mapping[str, tuple[str, str]],
) -> Mapping[str, tuple[str, str]]:
    normalized: dict[str, tuple[str, str]] = {}

    for name in sorted(session_segments.keys()):
        start, end = session_segments[name]
        _ = _parse_time_str(start)
        _ = _parse_time_str(end)
        if _parse_time_str(start) >= _parse_time_str(end):
            raise ReplaySelectionValidationError(
                f"session segment {name!r} has invalid window: {start} >= {end}"
            )
        normalized[name] = (start, end)

    return normalized


def _validate_market_tags(market_tags: Sequence[str]) -> None:
    for tag in market_tags:
        if not isinstance(tag, str) or not tag.strip():
            raise ReplaySelectionValidationError(
                f"market_tags must contain non-empty strings, got {tag!r}"
            )


def _validate_weekdays(weekdays: Sequence[int]) -> None:
    for day_index in weekdays:
        if not isinstance(day_index, int) or not (0 <= day_index <= 6):
            raise ReplaySelectionValidationError(
                f"weekday must be integer in [0, 6], got {day_index!r}"
            )


def _validate_months(months: Sequence[int]) -> None:
    for month_index in months:
        if not isinstance(month_index, int) or not (1 <= month_index <= 12):
            raise ReplaySelectionValidationError(
                f"month must be integer in [1, 12], got {month_index!r}"
            )


def _validate_date_str(date_str: str) -> None:
    if not DATASET_DATE_RE.match(date_str):
        raise ReplaySelectionValidationError(
            f"date must be YYYY-MM-DD, got {date_str!r}"
        )
    try:
        date.fromisoformat(date_str)
    except ValueError as exc:
        raise ReplaySelectionValidationError(
            f"invalid date: {date_str!r}"
        ) from exc


def _parse_time_str(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise ReplaySelectionValidationError(
            f"time must be HH:MM[:SS], got {value!r}"
        ) from exc


def _date_to_weekday(date_str: str) -> int:
    return date.fromisoformat(date_str).weekday()


def _date_to_month(date_str: str) -> int:
    return date.fromisoformat(date_str).month


def _stable_sha256_json(value: Mapping[str, Any]) -> str:
    import hashlib
    import json

    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__ = [
    "ReplaySelectionError",
    "ReplaySelectionValidationError",
    "ReplaySelectionUnavailableError",
    "SESSION_SEGMENT_OPENING",
    "SESSION_SEGMENT_MORNING",
    "SESSION_SEGMENT_MIDDAY",
    "SESSION_SEGMENT_AFTERNOON",
    "SESSION_SEGMENT_CLOSING",
    "SESSION_SEGMENT_FULL",
    "DEFAULT_SESSION_SEGMENTS",
    "ReplayTimeWindow",
    "ReplaySelectionRequest",
    "ReplaySelectionPlan",
    "ReplaySelector",
    "build_selection_plan",
    "selection_plan_to_dict",
]
