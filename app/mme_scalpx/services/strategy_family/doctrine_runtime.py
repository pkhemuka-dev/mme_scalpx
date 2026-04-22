from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/doctrine_runtime.py

Shared runtime dataclasses for doctrine evaluators and the thin strategy-family
coordinator.

Purpose
-------
This module OWNS:
- family-neutral runtime input views
- family-neutral doctrine candidate / action / result dataclasses
- no-signal / blocked / candidate / action result builders
- provider / risk / position runtime view adapters
- temporary backward-compatible aliases required while doctrine leaf files are
  still being migrated from stub surfaces to final production surfaces

This module DOES NOT own:
- Redis reads or writes
- live publication
- doctrine-specific math
- arbitration
- feature math
- composition wiring

Design rules
------------
- Runtime input is immutable after construction.
- Nested metadata mappings are frozen at construction time.
- The module is tolerant of partial upstream feature/runtime payloads during
  staged migration.
- The module preserves backward-compatible aliases DoctrineCandidate and
  DoctrineCandidateContext until every doctrine leaf is rewritten.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N

from .common import doctrine_for_family, safe_bool, safe_float, safe_int, safe_str

# ============================================================================
# Frozen evaluation statuses
# ============================================================================

EVAL_STATUS_BLOCKED: Final[str] = "BLOCKED"
EVAL_STATUS_NO_SIGNAL: Final[str] = "NO_SIGNAL"
EVAL_STATUS_ENTRY_CANDIDATE: Final[str] = "ENTRY_CANDIDATE"
EVAL_STATUS_ACTION_REQUEST: Final[str] = "ACTION_REQUEST"

_ALLOWED_EVAL_STATUSES: Final[tuple[str, ...]] = (
    EVAL_STATUS_BLOCKED,
    EVAL_STATUS_NO_SIGNAL,
    EVAL_STATUS_ENTRY_CANDIDATE,
    EVAL_STATUS_ACTION_REQUEST,
)

# names.py owns the canonical action symbols, but does not export a single
# ALLOWED_ACTIONS aggregate. Freeze the admissible action literals locally
# from canonical names.py symbols to stay spine-aligned without depending on
# models.py for schema vocabularies here.
_REQUIRED_ACTION_SYMBOLS: Final[tuple[str, ...]] = (
    "ACTION_ENTER_CALL",
    "ACTION_ENTER_PUT",
    "ACTION_EXIT",
    "ACTION_HOLD",
)
_OPTIONAL_ACTION_SYMBOLS: Final[tuple[str, ...]] = (
    "ACTION_BLOCK",
)

# ============================================================================
# Exceptions / helpers
# ============================================================================


class DoctrineRuntimeError(ValueError):
    """Raised when runtime view construction or runtime invariants are invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DoctrineRuntimeError(message)


_missing_required_actions = [
    name for name in _REQUIRED_ACTION_SYMBOLS if not hasattr(N, name)
]
if _missing_required_actions:
    raise DoctrineRuntimeError(
        "names.py missing required action symbols for doctrine_runtime: "
        + ", ".join(_missing_required_actions)
    )

_ALLOWED_ACTIONS: Final[tuple[str, ...]] = tuple(
    value
    for value in (
        *(getattr(N, name) for name in _REQUIRED_ACTION_SYMBOLS),
        *(getattr(N, name) for name in _OPTIONAL_ACTION_SYMBOLS if hasattr(N, name)),
    )
    if isinstance(value, str) and value.strip()
)


def _freeze_mapping(mapping: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if mapping is None:
        return MappingProxyType({})
    return MappingProxyType(dict(mapping))


def _pick(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _normalize_optional_str(
    value: Any,
    *,
    default: str | None = None,
) -> str | None:
    token = safe_str(value, default or "")
    return token or None


def _normalize_known_literal(
    value: Any,
    *,
    allowed: tuple[str, ...],
    default: str,
) -> str:
    token = safe_str(value, default).strip()
    if token not in allowed:
        return default
    return token


# ============================================================================
# Runtime truth views
# ============================================================================


@dataclass(frozen=True, slots=True)
class ProviderTruthView:
    active_futures_provider_id: str | None = None
    active_selected_option_provider_id: str | None = None
    active_option_context_provider_id: str | None = None
    active_execution_provider_id: str | None = None
    fallback_execution_provider_id: str | None = None

    futures_status: str | None = None
    selected_option_status: str | None = None
    option_context_status: str | None = None
    execution_status: str | None = None

    execution_bridge_ok: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in (
            "active_futures_provider_id",
            "active_selected_option_provider_id",
            "active_option_context_provider_id",
            "active_execution_provider_id",
            "fallback_execution_provider_id",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require(
                    value in N.ALLOWED_PROVIDER_IDS,
                    f"{field_name} has unsupported provider id: {value!r}",
                )

        for field_name in (
            "futures_status",
            "selected_option_status",
            "option_context_status",
            "execution_status",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require(
                    value in N.ALLOWED_PROVIDER_STATUSES,
                    f"{field_name} has unsupported provider status: {value!r}",
                )

        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | None) -> "ProviderTruthView":
        data = dict(raw or {})

        return cls(
            active_futures_provider_id=_normalize_optional_str(
                _pick(data, "active_futures_provider_id", "futures_provider_id")
            ),
            active_selected_option_provider_id=_normalize_optional_str(
                _pick(
                    data,
                    "active_selected_option_provider_id",
                    "selected_option_provider_id",
                    "option_provider_id",
                )
            ),
            active_option_context_provider_id=_normalize_optional_str(
                _pick(
                    data,
                    "active_option_context_provider_id",
                    "option_context_provider_id",
                    "context_provider_id",
                )
            ),
            active_execution_provider_id=_normalize_optional_str(
                _pick(data, "active_execution_provider_id", "execution_provider_id")
            ),
            fallback_execution_provider_id=_normalize_optional_str(
                _pick(
                    data,
                    "fallback_execution_provider_id",
                    "execution_fallback_provider_id",
                )
            ),
            futures_status=_normalize_optional_str(
                _pick(data, "futures_status", "active_futures_status")
            ),
            selected_option_status=_normalize_optional_str(
                _pick(
                    data,
                    "selected_option_status",
                    "active_selected_option_status",
                )
            ),
            option_context_status=_normalize_optional_str(
                _pick(
                    data,
                    "option_context_status",
                    "active_option_context_status",
                )
            ),
            execution_status=_normalize_optional_str(
                _pick(data, "execution_status", "active_execution_status")
            ),
            execution_bridge_ok=safe_bool(
                _pick(data, "execution_bridge_ok", "bridge_ok"),
                False,
            ),
            metadata=data,
        )


@dataclass(frozen=True, slots=True)
class RiskGateView:
    veto_entries: bool = False
    preview_quantity_lots: int = 0
    daily_loss_lock: bool = False
    consecutive_loss_pause: bool = False
    session_close_lock: bool = False
    reconciliation_lock: bool = False
    unresolved_disaster_lock: bool = False
    daily_trade_cap_reached: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(
            self.preview_quantity_lots >= 0,
            "preview_quantity_lots must be >= 0",
        )
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | None) -> "RiskGateView":
        data = dict(raw or {})

        return cls(
            veto_entries=safe_bool(_pick(data, "veto_entries"), False),
            preview_quantity_lots=max(
                0,
                safe_int(
                    _pick(
                        data,
                        "preview_quantity_lots",
                        "preview_entry_quantity_lots",
                        "quantity_lots_hint",
                    ),
                    0,
                ),
            ),
            daily_loss_lock=safe_bool(_pick(data, "daily_loss_lock"), False),
            consecutive_loss_pause=safe_bool(
                _pick(data, "consecutive_loss_pause"),
                False,
            ),
            session_close_lock=safe_bool(_pick(data, "session_close_lock"), False),
            reconciliation_lock=safe_bool(_pick(data, "reconciliation_lock"), False),
            unresolved_disaster_lock=safe_bool(
                _pick(data, "unresolved_disaster_lock"),
                False,
            ),
            daily_trade_cap_reached=safe_bool(
                _pick(data, "daily_trade_cap_reached"),
                False,
            ),
            metadata=data,
        )


@dataclass(frozen=True, slots=True)
class PositionTruthView:
    has_position: bool = False
    position_side: str = N.POSITION_SIDE_FLAT
    qty_lots: int = 0
    avg_price: float | None = None
    entry_mode: str = N.ENTRY_MODE_UNKNOWN
    instrument_key: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(
            self.position_side in N.ALLOWED_POSITION_SIDES,
            f"unsupported position_side: {self.position_side!r}",
        )
        _require(self.qty_lots >= 0, "qty_lots must be >= 0")
        _require(
            self.entry_mode in N.ALLOWED_ENTRY_MODES,
            f"unsupported entry_mode: {self.entry_mode!r}",
        )
        if self.avg_price is not None:
            _require(self.avg_price >= 0.0, "avg_price must be >= 0.0")
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any] | None) -> "PositionTruthView":
        data = dict(raw or {})
        position_side = _normalize_known_literal(
            _pick(data, "position_side", "side"),
            allowed=N.ALLOWED_POSITION_SIDES,
            default=N.POSITION_SIDE_FLAT,
        )
        qty_lots = max(
            0,
            safe_int(_pick(data, "qty_lots", "quantity_lots"), 0),
        )
        has_position = safe_bool(
            _pick(data, "has_position"),
            position_side != N.POSITION_SIDE_FLAT and qty_lots > 0,
        )
        avg_price_raw = _pick(data, "avg_price", "entry_avg_price")
        avg_price = (
            max(0.0, safe_float(avg_price_raw, 0.0))
            if avg_price_raw is not None
            else None
        )
        entry_mode = _normalize_known_literal(
            _pick(data, "entry_mode"),
            allowed=N.ALLOWED_ENTRY_MODES,
            default=N.ENTRY_MODE_UNKNOWN,
        )

        return cls(
            has_position=has_position,
            position_side=position_side,
            qty_lots=qty_lots,
            avg_price=avg_price,
            entry_mode=entry_mode,
            instrument_key=_normalize_optional_str(
                _pick(data, "instrument_key", "selected_instrument_key")
            ),
            metadata=data,
        )


# ============================================================================
# Shared doctrine runtime surfaces
# ============================================================================


@dataclass(frozen=True, slots=True)
class DoctrineRuntimeInput:
    now_ns: int
    family_id: str
    doctrine_id: str | None = None
    branch_id: str | None = None
    family_runtime_mode: str | None = None
    strategy_runtime_mode: str | None = None
    provider: ProviderTruthView = field(default_factory=ProviderTruthView)
    risk: RiskGateView = field(default_factory=RiskGateView)
    position: PositionTruthView = field(default_factory=PositionTruthView)
    shared_features: Mapping[str, Any] = field(default_factory=dict)
    family_features: Mapping[str, Any] = field(default_factory=dict)
    machine_state: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(self.now_ns >= 0, "now_ns must be >= 0")
        _require(
            self.family_id in N.ALLOWED_STRATEGY_FAMILY_IDS,
            f"unsupported family_id: {self.family_id!r}",
        )
        if self.doctrine_id is not None:
            _require(
                self.doctrine_id in N.ALLOWED_DOCTRINE_IDS,
                f"unsupported doctrine_id: {self.doctrine_id!r}",
            )
        if self.branch_id is not None:
            _require(
                self.branch_id in N.ALLOWED_BRANCH_IDS,
                f"unsupported branch_id: {self.branch_id!r}",
            )
        if self.family_runtime_mode is not None:
            _require(
                self.family_runtime_mode in N.ALLOWED_FAMILY_RUNTIME_MODES,
                f"unsupported family_runtime_mode: {self.family_runtime_mode!r}",
            )
        if self.strategy_runtime_mode is not None:
            _require(
                self.strategy_runtime_mode in N.ALLOWED_STRATEGY_RUNTIME_MODES,
                f"unsupported strategy_runtime_mode: {self.strategy_runtime_mode!r}",
            )

        object.__setattr__(self, "shared_features", _freeze_mapping(self.shared_features))
        object.__setattr__(self, "family_features", _freeze_mapping(self.family_features))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @property
    def resolved_doctrine_id(self) -> str:
        return self.doctrine_id or doctrine_for_family(self.family_id)


@dataclass(frozen=True, slots=True)
class DoctrineBlocker:
    code: str
    message: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(bool(safe_str(self.code)), "blocker code must be non-empty")
        _require(bool(safe_str(self.message)), "blocker message must be non-empty")
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class DoctrineSignalCandidate:
    family_id: str
    doctrine_id: str
    branch_id: str
    side: str
    instrument_key: str | None
    entry_mode: str
    family_runtime_mode: str | None
    strategy_runtime_mode: str | None
    score: float = 0.0
    priority: float = 0.0
    setup_kind: str | None = None
    target_points: float | None = None
    stop_points: float | None = None
    tick_size: float = 0.05
    quantity_lots_hint: int | None = None
    source_event_id: str | None = None
    trap_event_id: str | None = None
    burst_event_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(
            self.family_id in N.ALLOWED_STRATEGY_FAMILY_IDS,
            f"unsupported candidate family_id: {self.family_id!r}",
        )
        _require(
            self.doctrine_id in N.ALLOWED_DOCTRINE_IDS,
            f"unsupported candidate doctrine_id: {self.doctrine_id!r}",
        )
        _require(
            self.branch_id in N.ALLOWED_BRANCH_IDS,
            f"unsupported candidate branch_id: {self.branch_id!r}",
        )
        _require(
            self.side in (N.SIDE_CALL, N.SIDE_PUT),
            f"unsupported candidate side: {self.side!r}",
        )
        _require(
            self.entry_mode in N.ALLOWED_ENTRY_MODES,
            f"unsupported candidate entry_mode: {self.entry_mode!r}",
        )
        _require(self.tick_size > 0.0, "tick_size must be > 0.0")
        if self.quantity_lots_hint is not None:
            _require(
                self.quantity_lots_hint >= 0,
                "quantity_lots_hint must be >= 0",
            )
        if self.target_points is not None:
            _require(self.target_points > 0.0, "target_points must be > 0.0")
        if self.stop_points is not None:
            _require(self.stop_points > 0.0, "stop_points must be > 0.0")

        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class DoctrineActionRequest:
    action: str
    side: str
    position_effect: str
    reason_code: str
    explain: str
    quantity_lots: int = 0
    instrument_key: str | None = None
    blocker: DoctrineBlocker | None = None
    stop_plan: Mapping[str, Any] | None = None
    target_plan: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(
            self.action in _ALLOWED_ACTIONS,
            f"unsupported action: {self.action!r}",
        )
        _require(
            self.side in (N.SIDE_CALL, N.SIDE_PUT),
            f"unsupported action side: {self.side!r}",
        )
        _require(
            self.position_effect in N.ALLOWED_POSITION_EFFECTS,
            f"unsupported position_effect: {self.position_effect!r}",
        )
        _require(bool(safe_str(self.reason_code)), "reason_code must be non-empty")
        _require(bool(safe_str(self.explain)), "explain must be non-empty")
        _require(self.quantity_lots >= 0, "quantity_lots must be >= 0")

        if self.stop_plan is not None:
            object.__setattr__(self, "stop_plan", _freeze_mapping(self.stop_plan))
        if self.target_plan is not None:
            object.__setattr__(self, "target_plan", _freeze_mapping(self.target_plan))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True, slots=True)
class DoctrineEvaluationResult:
    status: str
    family_id: str
    doctrine_id: str
    branch_id: str | None = None
    candidate: DoctrineSignalCandidate | None = None
    action: DoctrineActionRequest | None = None
    blocker: DoctrineBlocker | None = None
    cooldown_hint_sec: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(
            self.status in _ALLOWED_EVAL_STATUSES,
            f"unsupported evaluation status: {self.status!r}",
        )
        _require(
            self.family_id in N.ALLOWED_STRATEGY_FAMILY_IDS,
            f"unsupported result family_id: {self.family_id!r}",
        )
        _require(
            self.doctrine_id in N.ALLOWED_DOCTRINE_IDS,
            f"unsupported result doctrine_id: {self.doctrine_id!r}",
        )
        if self.branch_id is not None:
            _require(
                self.branch_id in N.ALLOWED_BRANCH_IDS,
                f"unsupported result branch_id: {self.branch_id!r}",
            )
        if self.cooldown_hint_sec is not None:
            _require(
                self.cooldown_hint_sec >= 0.0,
                "cooldown_hint_sec must be >= 0.0",
            )

        if self.status == EVAL_STATUS_BLOCKED:
            _require(self.blocker is not None, "blocked result requires blocker")
            _require(self.candidate is None, "blocked result must not carry candidate")
        elif self.status == EVAL_STATUS_ENTRY_CANDIDATE:
            _require(self.candidate is not None, "candidate result requires candidate")
            _require(self.blocker is None, "candidate result must not carry blocker")
        elif self.status == EVAL_STATUS_ACTION_REQUEST:
            _require(self.action is not None, "action result requires action")
        elif self.status == EVAL_STATUS_NO_SIGNAL:
            _require(self.candidate is None, "no-signal result must not carry candidate")
            _require(self.action is None, "no-signal result must not carry action")

        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))

    @property
    def is_candidate(self) -> bool:
        return self.status == EVAL_STATUS_ENTRY_CANDIDATE and self.candidate is not None

    @property
    def is_blocked(self) -> bool:
        return self.status == EVAL_STATUS_BLOCKED and self.blocker is not None

    @property
    def is_action(self) -> bool:
        return self.status == EVAL_STATUS_ACTION_REQUEST and self.action is not None

    @property
    def is_no_signal(self) -> bool:
        return self.status == EVAL_STATUS_NO_SIGNAL


# ============================================================================
# Result builders
# ============================================================================


def blocked_result(
    *,
    family_id: str,
    doctrine_id: str,
    branch_id: str | None,
    code: str,
    message: str,
    metadata: Mapping[str, Any] | None = None,
) -> DoctrineEvaluationResult:
    blocker = DoctrineBlocker(
        code=code,
        message=message,
        metadata=dict(metadata or {}),
    )
    return DoctrineEvaluationResult(
        status=EVAL_STATUS_BLOCKED,
        family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=branch_id,
        blocker=blocker,
        metadata=dict(metadata or {}),
    )


def no_signal_result(
    *,
    family_id: str,
    doctrine_id: str,
    branch_id: str | None,
    metadata: Mapping[str, Any] | None = None,
) -> DoctrineEvaluationResult:
    return DoctrineEvaluationResult(
        status=EVAL_STATUS_NO_SIGNAL,
        family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=branch_id,
        metadata=dict(metadata or {}),
    )


def candidate_result(candidate: DoctrineSignalCandidate) -> DoctrineEvaluationResult:
    return DoctrineEvaluationResult(
        status=EVAL_STATUS_ENTRY_CANDIDATE,
        family_id=candidate.family_id,
        doctrine_id=candidate.doctrine_id,
        branch_id=candidate.branch_id,
        candidate=candidate,
        metadata=dict(candidate.metadata),
    )


def action_result(
    *,
    family_id: str,
    doctrine_id: str,
    branch_id: str | None,
    action: DoctrineActionRequest,
    cooldown_hint_sec: float | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> DoctrineEvaluationResult:
    return DoctrineEvaluationResult(
        status=EVAL_STATUS_ACTION_REQUEST,
        family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=branch_id,
        action=action,
        cooldown_hint_sec=cooldown_hint_sec,
        metadata=dict(metadata or {}),
    )


# ============================================================================
# Backward-compatible aliases
# ============================================================================

DoctrineCandidate = DoctrineSignalCandidate
DoctrineCandidateContext = DoctrineRuntimeInput

# ============================================================================
# Exports
# ============================================================================

__all__ = [
    "DoctrineActionRequest",
    "DoctrineBlocker",
    "DoctrineCandidate",
    "DoctrineCandidateContext",
    "DoctrineEvaluationResult",
    "DoctrineRuntimeError",
    "DoctrineRuntimeInput",
    "DoctrineSignalCandidate",
    "EVAL_STATUS_ACTION_REQUEST",
    "EVAL_STATUS_BLOCKED",
    "EVAL_STATUS_ENTRY_CANDIDATE",
    "EVAL_STATUS_NO_SIGNAL",
    "PositionTruthView",
    "ProviderTruthView",
    "RiskGateView",
    "action_result",
    "blocked_result",
    "candidate_result",
    "no_signal_result",
]
