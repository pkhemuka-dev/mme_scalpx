from __future__ import annotations

"""
app/mme_scalpx/research_capture/router.py

Frozen routing layer for the MME research data capture chapter.

Purpose
-------
This module owns deterministic routing of canonical CaptureRecord objects into
logical archive buckets. It decides which normalized/enriched records belong to:

- ticks_fut
- ticks_opt
- signals_audit
- runtime_audit

Owns
----
- route configuration
- route membership rules
- immutable route-plan construction
- deterministic grouping of records by logical archive bucket

Does not own
------------
- normalization
- enrichment
- partition path construction
- parquet writing
- manifest writing
- runtime orchestration
- production strategy doctrine

Design laws
-----------
- routing must be deterministic and side-effect free
- routing must not mutate records
- base tick routing follows the canonical dataset on the record
- runtime audit routing follows presence of runtime_audit
- signals audit routing follows presence of meaningful strategy_audit payload
- empty buckets are excluded by default unless explicitly requested
"""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterator, Mapping, Sequence

from app.mme_scalpx.research_capture.models import CaptureRecord

ROUTE_TICKS_FUT = "ticks_fut"
ROUTE_TICKS_OPT = "ticks_opt"
ROUTE_SIGNALS_AUDIT = "signals_audit"
ROUTE_RUNTIME_AUDIT = "runtime_audit"

CANONICAL_ROUTE_NAMES: tuple[str, ...] = (
    ROUTE_TICKS_FUT,
    ROUTE_TICKS_OPT,
    ROUTE_SIGNALS_AUDIT,
    ROUTE_RUNTIME_AUDIT,
)


def _ensure_non_empty_str(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty str")
    return value


def _freeze_record_buckets(
    buckets: Mapping[str, Sequence[CaptureRecord]],
) -> Mapping[str, tuple[CaptureRecord, ...]]:
    frozen: dict[str, tuple[CaptureRecord, ...]] = {}
    for route_name, records in buckets.items():
        _ensure_non_empty_str("route_name", route_name)
        if route_name not in CANONICAL_ROUTE_NAMES:
            raise ValueError(f"Unknown route name: {route_name!r}")
        tuple_records = tuple(records)
        for record in tuple_records:
            if not isinstance(record, CaptureRecord):
                raise TypeError("route bucket members must be CaptureRecord instances")
        frozen[route_name] = tuple_records
    return MappingProxyType(frozen)


def _strategy_audit_has_payload(record: CaptureRecord) -> bool:
    """
    Return True when the record contains meaningful strategy-audit content.
    """
    if record.strategy_audit is None:
        return False

    payload = record.strategy_audit.to_field_map(include_none=False)
    return any(value is not None for value in payload.values())


@dataclass(frozen=True, slots=True)
class RouteConfig:
    """
    Frozen route configuration.

    Defaults:
    - include base tick routes
    - include runtime audit route
    - include signals audit only when strategy_audit is present and meaningful
    - exclude empty buckets
    - require a single session_date across a route plan
    """
    include_base_tick_routes: bool = True
    include_runtime_audit_route: bool = True
    include_signals_audit_route: bool = True
    include_empty_routes: bool = False
    require_single_session: bool = True

    def __post_init__(self) -> None:
        for name in (
            "include_base_tick_routes",
            "include_runtime_audit_route",
            "include_signals_audit_route",
            "include_empty_routes",
            "require_single_session",
        ):
            value = getattr(self, name)
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be bool")


DEFAULT_ROUTE_CONFIG = RouteConfig()


@dataclass(frozen=True, slots=True)
class RoutePlan:
    """
    Immutable routing result.

    Behaves like a read-only mapping:
        route_name -> tuple[CaptureRecord, ...]
    """
    buckets: Mapping[str, tuple[CaptureRecord, ...]]
    session_date: str | None = None
    config: RouteConfig = DEFAULT_ROUTE_CONFIG

    def __post_init__(self) -> None:
        object.__setattr__(self, "buckets", _freeze_record_buckets(self.buckets))

        if self.session_date is not None:
            _ensure_non_empty_str("session_date", self.session_date)

        if not isinstance(self.config, RouteConfig):
            raise TypeError("config must be RouteConfig")

        if self.config.require_single_session and self.session_date is not None:
            for route_name, records in self.buckets.items():
                for record in records:
                    if record.timing.session_date != self.session_date:
                        raise ValueError(
                            f"route {route_name!r} contains mixed session dates: "
                            f"{record.timing.session_date!r} != {self.session_date!r}"
                        )

    def __getitem__(self, key: str) -> tuple[CaptureRecord, ...]:
        return self.buckets[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.buckets)

    def __len__(self) -> int:
        return len(self.buckets)

    def keys(self):
        return self.buckets.keys()

    def items(self):
        return self.buckets.items()

    def values(self):
        return self.buckets.values()

    def get(self, key: str, default: Any = None):
        return self.buckets.get(key, default)

    @property
    def counts(self) -> Mapping[str, int]:
        return MappingProxyType({route_name: len(records) for route_name, records in self.buckets.items()})

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_date": self.session_date,
            "routes": {route_name: len(records) for route_name, records in self.buckets.items()},
            "config": {
                "include_base_tick_routes": self.config.include_base_tick_routes,
                "include_runtime_audit_route": self.config.include_runtime_audit_route,
                "include_signals_audit_route": self.config.include_signals_audit_route,
                "include_empty_routes": self.config.include_empty_routes,
                "require_single_session": self.config.require_single_session,
            },
        }


def route_record(
    record: CaptureRecord,
    *,
    config: RouteConfig = DEFAULT_ROUTE_CONFIG,
) -> tuple[str, ...]:
    """
    Return the canonical route names for a single record.
    """
    if not isinstance(record, CaptureRecord):
        raise TypeError("record must be CaptureRecord")

    routes: list[str] = []

    if config.include_base_tick_routes:
        dataset_route = record.dataset.value
        if dataset_route not in (ROUTE_TICKS_FUT, ROUTE_TICKS_OPT):
            raise ValueError(f"Unsupported base dataset route: {dataset_route!r}")
        routes.append(dataset_route)

    if config.include_runtime_audit_route and record.runtime_audit is not None:
        routes.append(ROUTE_RUNTIME_AUDIT)

    if config.include_signals_audit_route and _strategy_audit_has_payload(record):
        routes.append(ROUTE_SIGNALS_AUDIT)

    # Preserve order while removing duplicates.
    return tuple(dict.fromkeys(routes))


def build_route_plan(
    records: Sequence[CaptureRecord],
    *,
    config: RouteConfig = DEFAULT_ROUTE_CONFIG,
) -> RoutePlan:
    """
    Build the immutable route plan for a sequence of records.
    """
    if not isinstance(config, RouteConfig):
        raise TypeError("config must be RouteConfig")

    if not records:
        empty_buckets = {route_name: () for route_name in CANONICAL_ROUTE_NAMES} if config.include_empty_routes else {}
        return RoutePlan(
            buckets=empty_buckets,
            session_date=None,
            config=config,
        )

    for record in records:
        if not isinstance(record, CaptureRecord):
            raise TypeError("records must contain only CaptureRecord instances")

    session_date = records[0].timing.session_date
    if config.require_single_session:
        for index, record in enumerate(records):
            if record.timing.session_date != session_date:
                raise ValueError(
                    f"Mixed session dates in records at index {index}: "
                    f"{record.timing.session_date!r} != {session_date!r}"
                )

    buckets: dict[str, list[CaptureRecord]] = {}
    if config.include_empty_routes:
        for route_name in CANONICAL_ROUTE_NAMES:
            buckets[route_name] = []

    for record in records:
        for route_name in route_record(record, config=config):
            buckets.setdefault(route_name, []).append(record)

    if not config.include_empty_routes:
        buckets = {route_name: routed_records for route_name, routed_records in buckets.items() if routed_records}

    # Canonical ordering of route keys.
    ordered_buckets: dict[str, tuple[CaptureRecord, ...]] = {}
    for route_name in CANONICAL_ROUTE_NAMES:
        if route_name in buckets:
            ordered_buckets[route_name] = tuple(buckets[route_name])

    return RoutePlan(
        buckets=ordered_buckets,
        session_date=session_date,
        config=config,
    )


def route_records(
    records: Sequence[CaptureRecord],
    *,
    config: RouteConfig = DEFAULT_ROUTE_CONFIG,
) -> RoutePlan:
    """
    Alias for build_route_plan for ergonomic call sites.
    """
    return build_route_plan(records, config=config)


__all__ = [
    "CANONICAL_ROUTE_NAMES",
    "DEFAULT_ROUTE_CONFIG",
    "ROUTE_RUNTIME_AUDIT",
    "ROUTE_SIGNALS_AUDIT",
    "ROUTE_TICKS_FUT",
    "ROUTE_TICKS_OPT",
    "RouteConfig",
    "RoutePlan",
    "build_route_plan",
    "route_record",
    "route_records",
]
