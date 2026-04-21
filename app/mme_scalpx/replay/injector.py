"""
app/mme_scalpx/replay/injector.py

Freeze-grade replay injection layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Injector responsibilities
-------------------------
This module owns:
- canonical replay injection request/result contracts
- deterministic input ordering validation
- replay-safe injection orchestration
- transport abstraction for replay publication
- machine-readable injection serialization helpers

This module does not own:
- dataset discovery/loading
- selection policy
- replay clock ownership
- replay engine lifecycle ownership
- topology truth
- doctrine logic
- live runtime side effects

Design rules
------------
- injection order must be explicit and auditable
- identical ordered input + identical transport behavior must yield identical
  injection results
- injector must remain transport-agnostic
- injector must not directly own Redis or broker runtime specifics
- replay-safe namespace policy must be respected by the transport implementation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .clock import ReplayClock, replay_clock_snapshot_to_dict


class ReplayInjectorError(RuntimeError):
    """Base exception for replay injector failures."""


class ReplayInjectorValidationError(ReplayInjectorError):
    """Raised when replay injection inputs are invalid."""


class ReplayInjectorTransportError(ReplayInjectorError):
    """Raised when the replay transport fails while injecting."""


class ReplayTransport(Protocol):
    """
    Protocol for replay-safe injection transport.
    """

    def publish(
        self,
        request: "ReplayInjectionRequest",
    ) -> Mapping[str, Any] | None:
        ...


@dataclass(frozen=True, slots=True)
class ReplayInjectionEvent:
    """
    Canonical replay injection event.
    """

    sequence_id: int
    event_time: str
    channel: str
    payload: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReplayInjectionRequest:
    """
    Canonical replay injection request.
    """

    run_id: str
    event: ReplayInjectionEvent
    replay_time_before: str
    replay_time_after: str
    batch_id: str | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReplayInjectionResult:
    """
    Canonical replay injection result.
    """

    run_id: str
    sequence_id: int
    channel: str
    event_time: str
    replay_time_before: str
    replay_time_after: str
    transport_summary: Mapping[str, Any] = field(default_factory=dict)
    success: bool = True


@dataclass(frozen=True, slots=True)
class ReplayInjectionBatchResult:
    """
    Canonical replay injection batch result.
    """

    run_id: str
    batch_id: str | None
    injected_count: int
    first_sequence_id: int | None
    last_sequence_id: int | None
    results: tuple[ReplayInjectionResult, ...]
    clock_snapshot: Mapping[str, Any]
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayInjector:
    """
    Freeze-grade replay injector.
    """

    def inject_event(
        self,
        *,
        run_id: str,
        event: ReplayInjectionEvent,
        clock: ReplayClock,
        transport: ReplayTransport,
        batch_id: str | None = None,
        notes: Sequence[str] = (),
    ) -> ReplayInjectionResult:
        _validate_run_id(run_id)
        _validate_event(event)

        replay_time_before = clock.current_time
        replay_time_after = clock.sync_if_needed(event.event_time)

        request = ReplayInjectionRequest(
            run_id=run_id,
            event=event,
            replay_time_before=replay_time_before,
            replay_time_after=replay_time_after,
            batch_id=batch_id,
            notes=tuple(notes),
        )

        try:
            raw_summary = transport.publish(request)
        except Exception as exc:
            raise ReplayInjectorTransportError(
                f"transport publish failed for run_id={run_id} sequence_id={event.sequence_id}: {exc}"
            ) from exc

        return ReplayInjectionResult(
            run_id=run_id,
            sequence_id=event.sequence_id,
            channel=event.channel,
            event_time=event.event_time,
            replay_time_before=replay_time_before,
            replay_time_after=replay_time_after,
            transport_summary=dict(raw_summary or {}),
            success=True,
        )

    def inject_batch(
        self,
        *,
        run_id: str,
        events: Sequence[ReplayInjectionEvent],
        clock: ReplayClock,
        transport: ReplayTransport,
        batch_id: str | None = None,
        notes: Sequence[str] = (),
    ) -> ReplayInjectionBatchResult:
        _validate_run_id(run_id)
        _validate_event_batch(events)

        results: list[ReplayInjectionResult] = []

        for event in events:
            result = self.inject_event(
                run_id=run_id,
                event=event,
                clock=clock,
                transport=transport,
                batch_id=batch_id,
                notes=notes,
            )
            results.append(result)

        clock_snapshot = replay_clock_snapshot_to_dict(
            clock.snapshot(notes=("post_injection_batch",))
        )

        return ReplayInjectionBatchResult(
            run_id=run_id,
            batch_id=batch_id,
            injected_count=len(results),
            first_sequence_id=events[0].sequence_id if events else None,
            last_sequence_id=events[-1].sequence_id if events else None,
            results=tuple(results),
            clock_snapshot=clock_snapshot,
            notes=tuple(notes),
        )


def injection_event_to_dict(event: ReplayInjectionEvent) -> dict[str, Any]:
    return {
        "sequence_id": event.sequence_id,
        "event_time": event.event_time,
        "channel": event.channel,
        "payload": dict(event.payload),
        "metadata": dict(event.metadata),
    }


def injection_request_to_dict(request: ReplayInjectionRequest) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "event": injection_event_to_dict(request.event),
        "replay_time_before": request.replay_time_before,
        "replay_time_after": request.replay_time_after,
        "batch_id": request.batch_id,
        "notes": list(request.notes),
    }


def injection_result_to_dict(result: ReplayInjectionResult) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "sequence_id": result.sequence_id,
        "channel": result.channel,
        "event_time": result.event_time,
        "replay_time_before": result.replay_time_before,
        "replay_time_after": result.replay_time_after,
        "transport_summary": dict(result.transport_summary),
        "success": result.success,
    }


def injection_batch_result_to_dict(
    result: ReplayInjectionBatchResult,
) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "batch_id": result.batch_id,
        "injected_count": result.injected_count,
        "first_sequence_id": result.first_sequence_id,
        "last_sequence_id": result.last_sequence_id,
        "results": [injection_result_to_dict(item) for item in result.results],
        "clock_snapshot": dict(result.clock_snapshot),
        "notes": list(result.notes),
    }


def _validate_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or not run_id.strip():
        raise ReplayInjectorValidationError(f"run_id must be non-empty string, got {run_id!r}")


def _validate_event(event: ReplayInjectionEvent) -> None:
    if event.sequence_id < 0:
        raise ReplayInjectorValidationError(
            f"sequence_id must be >= 0, got {event.sequence_id}"
        )
    if not isinstance(event.channel, str) or not event.channel.strip():
        raise ReplayInjectorValidationError(
            f"channel must be non-empty string, got {event.channel!r}"
        )
    if not isinstance(event.payload, Mapping):
        raise ReplayInjectorValidationError(
            f"payload must be mapping, got {type(event.payload)!r}"
        )
    if not isinstance(event.metadata, Mapping):
        raise ReplayInjectorValidationError(
            f"metadata must be mapping, got {type(event.metadata)!r}"
        )
    if not isinstance(event.event_time, str) or not event.event_time.strip():
        raise ReplayInjectorValidationError(
            f"event_time must be non-empty ISO string, got {event.event_time!r}"
        )


def _validate_event_batch(events: Sequence[ReplayInjectionEvent]) -> None:
    if not events:
        raise ReplayInjectorValidationError("events batch must be non-empty")

    previous_sequence: int | None = None
    previous_event_time: str | None = None

    for event in events:
        _validate_event(event)

        if previous_sequence is not None and event.sequence_id <= previous_sequence:
            raise ReplayInjectorValidationError(
                "event batch must be strictly increasing by sequence_id; "
                f"got {event.sequence_id} after {previous_sequence}"
            )

        if previous_event_time is not None and event.event_time < previous_event_time:
            raise ReplayInjectorValidationError(
                "event batch must be non-decreasing by event_time string order; "
                f"got {event.event_time!r} after {previous_event_time!r}"
            )

        previous_sequence = event.sequence_id
        previous_event_time = event.event_time


__all__ = [
    "ReplayInjectorError",
    "ReplayInjectorValidationError",
    "ReplayInjectorTransportError",
    "ReplayTransport",
    "ReplayInjectionEvent",
    "ReplayInjectionRequest",
    "ReplayInjectionResult",
    "ReplayInjectionBatchResult",
    "ReplayInjector",
    "injection_event_to_dict",
    "injection_request_to_dict",
    "injection_result_to_dict",
    "injection_batch_result_to_dict",
]
