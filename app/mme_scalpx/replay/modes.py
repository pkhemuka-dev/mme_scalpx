"""
app/mme_scalpx/replay/modes.py

Canonical replay enums for the MME-ScalpX Permanent Replay & Validation Framework.

R1 Constitution Freeze
----------------------
This module owns:
- canonical replay enums
- stable replay taxonomy labels
- central string surfaces for replay mode declarations

This module does not own:
- replay orchestration
- dataset loading
- experiment logic
- manifest writing
- report generation

Design rules
------------
- enums are contract surfaces
- values must remain stable and serializable
- downstream replay modules must import these enums rather than redefining strings
- locked/shadow/differential separation is non-negotiable
"""

from __future__ import annotations

from enum import Enum
from typing import Tuple


class _ReplayEnum(str, Enum):
    """Base class for replay contract enums."""

    @classmethod
    def values(cls) -> Tuple[str, ...]:
        return tuple(member.value for member in cls)

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls.values()


class DoctrineMode(_ReplayEnum):
    """Doctrine mode for a replay run."""

    LOCKED = "locked"
    SHADOW = "shadow"
    DIFFERENTIAL = "differential"


class ReplayScope(_ReplayEnum):
    """How much of the system chain is active for a replay run."""

    FEEDS_ONLY = "feeds_only"
    FEEDS_FEATURES = "feeds_features"
    FEEDS_FEATURES_STRATEGY = "feeds_features_strategy"
    FEEDS_FEATURES_STRATEGY_RISK = "feeds_features_strategy_risk"
    FEEDS_FEATURES_STRATEGY_RISK_EXECUTION_SHADOW = (
        "feeds_features_strategy_risk_execution_shadow"
    )
    FULL_SYSTEM_REPLAY = "full_system_replay"


class ReplaySpeedMode(_ReplayEnum):
    """Replay pacing mode."""

    ACCELERATED = "accelerated"
    REALTIME_1X = "realtime_1x"
    PAUSED = "paused"
    STEP = "step"
    BREAKPOINT = "breakpoint"


class ReplaySelectionMode(_ReplayEnum):
    """Input selection mode for replay date/session slicing."""

    SINGLE_DAY = "single_day"
    DATE_RANGE = "date_range"
    CUSTOM_DATE_LIST = "custom_date_list"
    INTRADAY_WINDOW = "intraday_window"
    SESSION_SEGMENT = "session_segment"
    WEEKDAY_BATCH = "weekday_batch"
    MONTHLY_BATCH = "monthly_batch"


class MarketDayTag(_ReplayEnum):
    """Optional market-day classification tags."""

    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    REVERSAL = "reversal"
    RANGE_EXPANSION = "range_expansion"
    FAKE_BREAKOUT = "fake_breakout"
    VOLATILE_CHOP = "volatile_chop"
    LOW_LIQUIDITY = "low_liquidity"
    EVENT_DAY = "event_day"


class ReplaySideMode(_ReplayEnum):
    """Side selection / reporting mode."""

    CALL_ONLY = "call_only"
    PUT_ONLY = "put_only"
    MIRRORED_BOTH = "mirrored_both"
    SIDE_SEPARATED = "side_separated"


class ExperimentFamily(_ReplayEnum):
    """High-level experiment family labels."""

    BASELINE_LOCKED = "baseline_locked"
    ECONOMICS_DISABLED = "economics_disabled"
    CONFIRMATION_VARIANT = "confirmation_variant"
    TP_SL_VARIANT = "tp_sl_variant"
    CONTEXT_GATE_VARIANT = "context_gate_variant"
    SIDE_FILTER_VARIANT = "side_filter_variant"
    EXIT_ARCH_VARIANT = "exit_arch_variant"
    PARAMETER_SWEEP = "parameter_sweep"
    THRESHOLD_SWEEP = "threshold_sweep"
    FAULT_INJECTION = "fault_injection"


class IntegrityVerdict(_ReplayEnum):
    """Verdict for replay integrity checks."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class ReplayVerdictTag(_ReplayEnum):
    """Interpretation tags attached to a replay run."""

    CONTRACTUAL_BASELINE = "contractual_baseline"
    SHADOW_EVIDENCE_ONLY = "shadow_evidence_only"
    DIFFERENTIAL_COMPARISON = "differential_comparison"
    INVALIDATED_BY_INTEGRITY = "invalidated_by_integrity"


class ReportFamily(_ReplayEnum):
    """Replay report family classification."""

    CORE = "core"
    FORENSIC = "forensic"
    COMPARISON = "comparison"
    INTEGRITY = "integrity"


class ReplayRunState(_ReplayEnum):
    """High-level replay lifecycle states."""

    CREATED = "created"
    RESETTING = "resetting"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


ALL_REPLAY_ENUMS = (
    DoctrineMode,
    ReplayScope,
    ReplaySpeedMode,
    ReplaySelectionMode,
    MarketDayTag,
    ReplaySideMode,
    ExperimentFamily,
    IntegrityVerdict,
    ReplayVerdictTag,
    ReportFamily,
    ReplayRunState,
)
