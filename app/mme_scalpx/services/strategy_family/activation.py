from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/activation.py

Freeze-grade strategy-family activation bridge for ScalpX MME.

Purpose
-------
This module OWNS:
- safe consumption of the proven StrategyFamilyConsumerView / mapping seam
- invocation of pure doctrine leaves:
  - MIST
  - MISB
  - MISC
  - MISR
  - MISO
- normalization of candidate / blocked / no-signal evaluator outputs
- deterministic candidate ranking and selection
- HOLD-safe activation gating
- dry-run / paper-only candidate promotion boundary

This module DOES NOT own:
- Redis reads or writes
- broker calls
- execution mutation
- risk mutation
- cooldown mutation
- order placement
- strategy service lifecycle
- feature computation

Safety law
----------
Default behavior is HOLD.

A candidate may be promoted only when activation mode is explicitly armed via
configuration and runtime activation flags. Even then, this module only returns
an activation decision object; it does not publish decisions or place orders.

This is the bridge between proven doctrine leaves and future strategy.py
activation. It is intentionally pure and side-effect free.
"""

import importlib
import math
from dataclasses import dataclass, field
from typing import Any, Final, Mapping, Sequence

from app.mme_scalpx.core import names as N


FAMILY_MIST: Final[str] = getattr(N, "STRATEGY_FAMILY_MIST", "MIST")
FAMILY_MISB: Final[str] = getattr(N, "STRATEGY_FAMILY_MISB", "MISB")
FAMILY_MISC: Final[str] = getattr(N, "STRATEGY_FAMILY_MISC", "MISC")
FAMILY_MISR: Final[str] = getattr(N, "STRATEGY_FAMILY_MISR", "MISR")
FAMILY_MISO: Final[str] = getattr(N, "STRATEGY_FAMILY_MISO", "MISO")

FAMILY_ORDER: Final[tuple[str, ...]] = (
    FAMILY_MIST,
    FAMILY_MISB,
    FAMILY_MISC,
    FAMILY_MISR,
    FAMILY_MISO,
)

BRANCH_CALL: Final[str] = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT: Final[str] = getattr(N, "BRANCH_PUT", "PUT")
BRANCH_ORDER: Final[tuple[str, ...]] = (BRANCH_CALL, BRANCH_PUT)

ACTION_HOLD: Final[str] = getattr(N, "ACTION_HOLD", "HOLD")
ACTION_ENTER_CALL: Final[str] = getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
ACTION_ENTER_PUT: Final[str] = getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")

ACTIVATION_MODE_HOLD_ONLY: Final[str] = "hold_only"
ACTIVATION_MODE_DRY_RUN: Final[str] = "dry_run"
ACTIVATION_MODE_PAPER_ARMED: Final[str] = "paper_armed"

_ALLOWED_ACTIVATION_MODES: Final[tuple[str, ...]] = (
    ACTIVATION_MODE_HOLD_ONLY,
    ACTIVATION_MODE_DRY_RUN,
    ACTIVATION_MODE_PAPER_ARMED,
)

_DOCTRINE_MODULES: Final[Mapping[str, str]] = {
    FAMILY_MIST: "app.mme_scalpx.services.strategy_family.mist",
    FAMILY_MISB: "app.mme_scalpx.services.strategy_family.misb",
    FAMILY_MISC: "app.mme_scalpx.services.strategy_family.misc",
    FAMILY_MISR: "app.mme_scalpx.services.strategy_family.misr",
    FAMILY_MISO: "app.mme_scalpx.services.strategy_family.miso",
}


class StrategyFamilyActivationError(RuntimeError):
    """Raised when the activation bridge cannot safely evaluate."""


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "pass", "passed", "available", "armed"}:
        return True
    if text in {"0", "false", "no", "n", "off", "fail", "failed", "none", "null", "disabled"}:
        return False
    return default


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        text = safe_str(value)
        if not text:
            return default
        out = float(text)
    except Exception:
        return default
    return out if math.isfinite(out) else default


def safe_int(value: Any, default: int = 0) -> int:
    if value is None or isinstance(value, bool):
        return default
    try:
        text = safe_str(value)
        if not text:
            return default
        return int(float(text))
    except Exception:
        return default


def as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def nested(root: Any, *path: str, default: Any = None) -> Any:
    cur = root
    for key in path:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def normalize_family_id(value: Any) -> str | None:
    text = safe_str(value).upper()
    for family_id in FAMILY_ORDER:
        if text == family_id:
            return family_id
    return None


def normalize_branch_id(value: Any) -> str | None:
    text = safe_str(value).upper()
    if text in {"CALL", "CE", "C", BRANCH_CALL}:
        return BRANCH_CALL
    if text in {"PUT", "PE", "P", BRANCH_PUT}:
        return BRANCH_PUT
    return None


def normalize_activation_mode(value: Any) -> str:
    text = safe_str(value, ACTIVATION_MODE_HOLD_ONLY).lower().replace("-", "_")
    aliases = {
        "hold": ACTIVATION_MODE_HOLD_ONLY,
        "hold_only": ACTIVATION_MODE_HOLD_ONLY,
        "observe": ACTIVATION_MODE_HOLD_ONLY,
        "observe_only": ACTIVATION_MODE_HOLD_ONLY,
        "dry": ACTIVATION_MODE_DRY_RUN,
        "dry_run": ACTIVATION_MODE_DRY_RUN,
        "paper": ACTIVATION_MODE_PAPER_ARMED,
        "paper_armed": ACTIVATION_MODE_PAPER_ARMED,
        "armed": ACTIVATION_MODE_PAPER_ARMED,
    }
    return aliases.get(text, ACTIVATION_MODE_HOLD_ONLY)


@dataclass(frozen=True, slots=True)
class StrategyFamilyActivationConfig:
    activation_mode: str = ACTIVATION_MODE_HOLD_ONLY
    allow_candidate_promotion: bool = False
    allow_live_orders: bool = False
    require_hold_only_view: bool = True
    require_safe_to_consume: bool = True
    require_data_valid: bool = True
    require_warmup_complete: bool = True
    min_candidate_score: float = 0.0
    max_candidates: int = 10
    enabled_families: tuple[str, ...] = FAMILY_ORDER
    enabled_branches: tuple[str, ...] = BRANCH_ORDER

    def normalized(self) -> StrategyFamilyActivationConfig:
        mode = normalize_activation_mode(self.activation_mode)
        families = tuple(
            family for family in (normalize_family_id(v) for v in self.enabled_families)
            if family is not None
        ) or FAMILY_ORDER
        branches = tuple(
            branch for branch in (normalize_branch_id(v) for v in self.enabled_branches)
            if branch is not None
        ) or BRANCH_ORDER

        return StrategyFamilyActivationConfig(
            activation_mode=mode,
            allow_candidate_promotion=bool(self.allow_candidate_promotion),
            allow_live_orders=False,
            require_hold_only_view=bool(self.require_hold_only_view),
            require_safe_to_consume=bool(self.require_safe_to_consume),
            require_data_valid=bool(self.require_data_valid),
            require_warmup_complete=bool(self.require_warmup_complete),
            min_candidate_score=max(float(self.min_candidate_score), 0.0),
            max_candidates=max(int(self.max_candidates), 1),
            enabled_families=families,
            enabled_branches=branches,
        )


@dataclass(frozen=True, slots=True)
class DoctrineEvaluationFrame:
    family_id: str
    branch_id: str
    is_candidate: bool
    is_blocked: bool
    is_no_signal: bool
    action: str
    score: float
    priority: float
    candidate: Mapping[str, Any] | None
    blocker: Mapping[str, Any] | None
    reason: str
    raw: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "branch_id": self.branch_id,
            "is_candidate": self.is_candidate,
            "is_blocked": self.is_blocked,
            "is_no_signal": self.is_no_signal,
            "action": self.action,
            "score": self.score,
            "priority": self.priority,
            "candidate": dict(self.candidate or {}),
            "blocker": dict(self.blocker or {}),
            "reason": self.reason,
            "raw": dict(self.raw),
        }


@dataclass(frozen=True, slots=True)
class StrategyFamilyActivationDecision:
    activation_mode: str
    action: str
    hold: bool
    promoted: bool
    safe_to_promote: bool
    reason: str
    selected: DoctrineEvaluationFrame | None
    candidates: tuple[DoctrineEvaluationFrame, ...]
    blocked: tuple[DoctrineEvaluationFrame, ...]
    no_signal: tuple[DoctrineEvaluationFrame, ...]
    family_count: int
    branch_count: int
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "activation_mode": self.activation_mode,
            "action": self.action,
            "hold": self.hold,
            "promoted": self.promoted,
            "safe_to_promote": self.safe_to_promote,
            "reason": self.reason,
            "selected": self.selected.to_dict() if self.selected else None,
            "candidates": [item.to_dict() for item in self.candidates],
            "blocked": [item.to_dict() for item in self.blocked],
            "no_signal": [item.to_dict() for item in self.no_signal],
            "family_count": self.family_count,
            "branch_count": self.branch_count,
            "metadata": dict(self.metadata),
        }


def _hold_decision(
    *,
    config: StrategyFamilyActivationConfig,
    reason: str,
    candidates: Sequence[DoctrineEvaluationFrame] = (),
    blocked: Sequence[DoctrineEvaluationFrame] = (),
    no_signal: Sequence[DoctrineEvaluationFrame] = (),
    selected: DoctrineEvaluationFrame | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> StrategyFamilyActivationDecision:
    return StrategyFamilyActivationDecision(
        activation_mode=config.activation_mode,
        action=ACTION_HOLD,
        hold=True,
        promoted=False,
        safe_to_promote=False,
        reason=reason,
        selected=selected,
        candidates=tuple(candidates),
        blocked=tuple(blocked),
        no_signal=tuple(no_signal),
        family_count=len(config.enabled_families),
        branch_count=len(config.enabled_branches),
        metadata=dict(metadata or {}),
    )


def _module_for_family(family_id: str) -> Any:
    path = _DOCTRINE_MODULES.get(family_id)
    if not path:
        raise StrategyFamilyActivationError(f"no doctrine module for family_id={family_id!r}")
    return importlib.import_module(path)


def _evaluate_leaf(view: Any, *, family_id: str, branch_id: str) -> Any:
    module = _module_for_family(family_id)
    fn = getattr(module, "evaluate", None)
    if not callable(fn):
        raise StrategyFamilyActivationError(f"{family_id}: evaluate is not callable")
    return fn(view, branch_id=branch_id)


def _evaluation_to_frame(result: Any, *, family_id: str, branch_id: str) -> DoctrineEvaluationFrame:
    raw = as_mapping(result)
    if not raw and hasattr(result, "to_dict"):
        raw = as_mapping(result.to_dict())

    candidate_obj = getattr(result, "candidate", None)
    blocker_obj = getattr(result, "blocker", None)

    candidate = as_mapping(candidate_obj) or as_mapping(raw.get("candidate"))
    blocker = as_mapping(blocker_obj) or as_mapping(raw.get("blocker"))

    is_candidate = safe_bool(getattr(result, "is_candidate", raw.get("is_candidate")), False)
    is_blocked = safe_bool(getattr(result, "is_blocked", raw.get("is_blocked")), False)
    is_no_signal = safe_bool(getattr(result, "is_no_signal", raw.get("is_no_signal")), False)
    if not is_candidate and not is_blocked:
        is_no_signal = True

    metadata = as_mapping(getattr(result, "metadata", raw.get("metadata")))
    reason = (
        safe_str(metadata.get("reason"))
        or safe_str(raw.get("reason"))
        or safe_str(nested(candidate, "metadata", "reason", default=""))
        or safe_str(nested(blocker, "code", default=""))
        or ("candidate" if is_candidate else "blocked" if is_blocked else "no_signal")
    )

    score = safe_float(candidate.get("score"), safe_float(raw.get("score"), 0.0))
    priority = safe_float(candidate.get("priority"), safe_float(raw.get("priority"), score * 100.0))
    action = safe_str(getattr(result, "action", raw.get("action")), ACTION_HOLD)

    return DoctrineEvaluationFrame(
        family_id=normalize_family_id(raw.get("family_id")) or family_id,
        branch_id=normalize_branch_id(raw.get("branch_id")) or branch_id,
        is_candidate=is_candidate,
        is_blocked=is_blocked,
        is_no_signal=is_no_signal,
        action=action,
        score=score,
        priority=priority,
        candidate=candidate or None,
        blocker=blocker or None,
        reason=reason,
        raw=raw,
    )


def _view_mapping(view: Any) -> dict[str, Any]:
    return as_mapping(view)


def _global_view_gate(view: Any, config: StrategyFamilyActivationConfig) -> tuple[bool, str]:
    mapping = _view_mapping(view)

    if config.require_hold_only_view and not safe_bool(mapping.get("hold_only"), False):
        return False, "view_not_hold_only"

    if config.require_safe_to_consume and not safe_bool(mapping.get("safe_to_consume"), False):
        return False, "view_not_safe_to_consume"

    if config.require_data_valid:
        data_valid = safe_bool(mapping.get("data_valid"), safe_bool(nested(mapping, "stage_flags", "data_valid", default=False), False))
        if not data_valid:
            return False, "view_data_invalid"

    if config.require_warmup_complete:
        warmup = safe_bool(mapping.get("warmup_complete"), safe_bool(nested(mapping, "stage_flags", "warmup_complete", default=False), False))
        if not warmup:
            return False, "view_warmup_incomplete"

    stage_flags = as_mapping(mapping.get("stage_flags"))
    if safe_bool(stage_flags.get("risk_veto_active"), False):
        return False, "risk_veto_active"
    if safe_bool(stage_flags.get("reconciliation_lock_active"), False):
        return False, "reconciliation_lock_active"
    if safe_bool(stage_flags.get("active_position_present"), False):
        return False, "active_position_present"

    return True, "global_gate_pass"


def collect_doctrine_evaluations(
    view: Any,
    *,
    config: StrategyFamilyActivationConfig | None = None,
) -> tuple[DoctrineEvaluationFrame, ...]:
    cfg = (config or StrategyFamilyActivationConfig()).normalized()
    frames: list[DoctrineEvaluationFrame] = []

    for family_id in cfg.enabled_families:
        for branch_id in cfg.enabled_branches:
            try:
                result = _evaluate_leaf(view, family_id=family_id, branch_id=branch_id)
                frames.append(_evaluation_to_frame(result, family_id=family_id, branch_id=branch_id))
            except Exception as exc:
                frames.append(
                    DoctrineEvaluationFrame(
                        family_id=family_id,
                        branch_id=branch_id,
                        is_candidate=False,
                        is_blocked=True,
                        is_no_signal=False,
                        action=ACTION_HOLD,
                        score=0.0,
                        priority=0.0,
                        candidate=None,
                        blocker={
                            "code": "doctrine_leaf_exception",
                            "message": f"{type(exc).__name__}: {exc}",
                        },
                        reason="doctrine_leaf_exception",
                        raw={},
                    )
                )

    return tuple(frames)


def rank_activation_candidates(
    frames: Sequence[DoctrineEvaluationFrame],
    *,
    config: StrategyFamilyActivationConfig | None = None,
) -> tuple[DoctrineEvaluationFrame, ...]:
    cfg = (config or StrategyFamilyActivationConfig()).normalized()
    usable = [
        frame for frame in frames
        if frame.is_candidate
        and frame.score >= cfg.min_candidate_score
        and frame.action in {ACTION_ENTER_CALL, ACTION_ENTER_PUT}
    ]

    family_rank = {family_id: index for index, family_id in enumerate(FAMILY_ORDER)}
    branch_rank = {BRANCH_CALL: 0, BRANCH_PUT: 1}

    usable.sort(
        key=lambda frame: (
            -frame.priority,
            -frame.score,
            family_rank.get(frame.family_id, 999),
            branch_rank.get(frame.branch_id, 999),
        )
    )
    return tuple(usable[: cfg.max_candidates])


def build_activation_decision(
    view: Any,
    *,
    config: StrategyFamilyActivationConfig | None = None,
) -> StrategyFamilyActivationDecision:
    cfg = (config or StrategyFamilyActivationConfig()).normalized()

    global_ok, global_reason = _global_view_gate(view, cfg)
    frames = collect_doctrine_evaluations(view, config=cfg)

    candidates = rank_activation_candidates(frames, config=cfg)
    blocked = tuple(frame for frame in frames if frame.is_blocked)
    no_signal = tuple(frame for frame in frames if frame.is_no_signal)

    if not global_ok:
        return _hold_decision(
            config=cfg,
            reason=global_reason,
            candidates=candidates,
            blocked=blocked,
            no_signal=no_signal,
            metadata={"gate": "global"},
        )

    if not candidates:
        return _hold_decision(
            config=cfg,
            reason="no_candidate",
            candidates=candidates,
            blocked=blocked,
            no_signal=no_signal,
            metadata={"gate": "candidate"},
        )

    selected = candidates[0]

    # Default and dry-run both remain HOLD. Dry-run only reports selected candidate.
    if cfg.activation_mode in {ACTIVATION_MODE_HOLD_ONLY, ACTIVATION_MODE_DRY_RUN}:
        return _hold_decision(
            config=cfg,
            reason="candidate_observed_hold_only" if cfg.activation_mode == ACTIVATION_MODE_HOLD_ONLY else "candidate_observed_dry_run",
            candidates=candidates,
            blocked=blocked,
            no_signal=no_signal,
            selected=selected,
            metadata={
                "selected_family_id": selected.family_id,
                "selected_branch_id": selected.branch_id,
                "selected_action": selected.action,
                "candidate_count": len(candidates),
            },
        )

    safe_to_promote = bool(
        cfg.activation_mode == ACTIVATION_MODE_PAPER_ARMED
        and cfg.allow_candidate_promotion
        and not cfg.allow_live_orders
        and selected.is_candidate
        and selected.action in {ACTION_ENTER_CALL, ACTION_ENTER_PUT}
    )

    if not safe_to_promote:
        return _hold_decision(
            config=cfg,
            reason="promotion_not_allowed",
            candidates=candidates,
            blocked=blocked,
            no_signal=no_signal,
            selected=selected,
            metadata={
                "selected_family_id": selected.family_id,
                "selected_branch_id": selected.branch_id,
                "selected_action": selected.action,
            },
        )

    return StrategyFamilyActivationDecision(
        activation_mode=cfg.activation_mode,
        action=selected.action,
        hold=False,
        promoted=True,
        safe_to_promote=True,
        reason="paper_candidate_promoted",
        selected=selected,
        candidates=candidates,
        blocked=blocked,
        no_signal=no_signal,
        family_count=len(cfg.enabled_families),
        branch_count=len(cfg.enabled_branches),
        metadata={
            "live_orders_allowed": False,
            "paper_only": True,
            "selected_family_id": selected.family_id,
            "selected_branch_id": selected.branch_id,
            "selected_score": selected.score,
            "selected_priority": selected.priority,
        },
    )


def evaluate_activation(
    view: Any,
    *,
    activation_mode: str = ACTIVATION_MODE_HOLD_ONLY,
    allow_candidate_promotion: bool = False,
    min_candidate_score: float = 0.0,
    enabled_families: Sequence[str] = FAMILY_ORDER,
    enabled_branches: Sequence[str] = BRANCH_ORDER,
) -> StrategyFamilyActivationDecision:
    config = StrategyFamilyActivationConfig(
        activation_mode=activation_mode,
        allow_candidate_promotion=allow_candidate_promotion,
        allow_live_orders=False,
        min_candidate_score=min_candidate_score,
        enabled_families=tuple(enabled_families),
        enabled_branches=tuple(enabled_branches),
    )
    return build_activation_decision(view, config=config)


__all__ = [
    "ACTIVATION_MODE_DRY_RUN",
    "ACTIVATION_MODE_HOLD_ONLY",
    "ACTIVATION_MODE_PAPER_ARMED",
    "BRANCH_ORDER",
    "FAMILY_ORDER",
    "DoctrineEvaluationFrame",
    "StrategyFamilyActivationConfig",
    "StrategyFamilyActivationDecision",
    "StrategyFamilyActivationError",
    "build_activation_decision",
    "collect_doctrine_evaluations",
    "evaluate_activation",
    "rank_activation_candidates",
]

# =============================================================================
# Batch 11 freeze hardening: activation is candidate-selection, not execution
# =============================================================================

_BATCH11_ACTIVATION_SEAM_VERSION = "1"
_BATCH11_PROMOTION_REQUIRED_FLAGS = (
    "strategy_order_intent_valid",
    "execution_contract_ready",
    "risk_gate_ready",
    "provider_identity_ready",
)
_BATCH11_PROMOTION_REQUIRED_METADATA = (
    "option_symbol",
    "option_token",
    "strike",
    "limit_price",
    "instrument_key",
)


def _batch11_plain_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, Mapping):
        return {str(k): _batch11_plain_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_batch11_plain_value(v) for v in value]
    if isinstance(value, set) or isinstance(value, frozenset):
        return sorted(_batch11_plain_value(v) for v in value)
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return _batch11_plain_value(value.to_dict())
    if hasattr(value, "__dataclass_fields__"):
        return {
            str(name): _batch11_plain_value(getattr(value, name))
            for name in value.__dataclass_fields__.keys()
        }
    if hasattr(value, "__dict__"):
        return {str(k): _batch11_plain_value(v) for k, v in vars(value).items()}
    return str(value)


def as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if value is None:
        return {}
    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
        except Exception:
            pass
    if hasattr(value, "__dataclass_fields__"):
        converted = _batch11_plain_value(value)
        return dict(converted) if isinstance(converted, Mapping) else {}
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def validate_registry_activation_parity() -> dict[str, str]:
    from app.mme_scalpx.services.strategy_family import registry as _registry

    mismatches: dict[str, str] = {}
    for family_id in FAMILY_ORDER:
        activation_path = _DOCTRINE_MODULES.get(family_id)
        registry_path = _registry.FAMILY_MODULE_PATHS.get(family_id)
        if activation_path != registry_path:
            mismatches[family_id] = f"{activation_path!r} != {registry_path!r}"
    if mismatches:
        raise StrategyFamilyActivationError(
            "activation/registry doctrine path mismatch: " + repr(mismatches)
        )
    return dict(_DOCTRINE_MODULES)


_BATCH11_ORIGINAL_EVALUATE_LEAF = _evaluate_leaf


def _evaluate_leaf(view: Any, *, family_id: str, branch_id: str) -> Any:
    validate_registry_activation_parity()
    return _BATCH11_ORIGINAL_EVALUATE_LEAF(
        view,
        family_id=family_id,
        branch_id=branch_id,
    )


def _batch11_candidate_metadata(frame: DoctrineEvaluationFrame | None) -> dict[str, Any]:
    if frame is None or not isinstance(frame.candidate, Mapping):
        return {}
    metadata = frame.candidate.get("metadata")
    return dict(metadata) if isinstance(metadata, Mapping) else {}


def _batch11_candidate_has_order_intent_contract(frame: DoctrineEvaluationFrame | None) -> bool:
    if frame is None:
        return False

    candidate = dict(frame.candidate or {})
    metadata = _batch11_candidate_metadata(frame)

    flags_ok = all(safe_bool(metadata.get(key), False) for key in _BATCH11_PROMOTION_REQUIRED_FLAGS)

    required_ok = True
    for key in _BATCH11_PROMOTION_REQUIRED_METADATA:
        value = metadata.get(key)
        if value in (None, "") and key in candidate:
            value = candidate.get(key)
        if value in (None, ""):
            required_ok = False
            break

    return bool(flags_ok and required_ok)


_BATCH11_ORIGINAL_BUILD_ACTIVATION_DECISION = build_activation_decision


def build_activation_decision(
    view: Any,
    *,
    config: StrategyFamilyActivationConfig | None = None,
) -> StrategyFamilyActivationDecision:
    cfg = (config or StrategyFamilyActivationConfig()).normalized()

    global_ok, global_reason = _global_view_gate(view, cfg)
    if not global_ok:
        return _hold_decision(
            config=cfg,
            reason=global_reason,
            candidates=(),
            blocked=(),
            no_signal=(),
            metadata={
                "gate": "global",
                "leaf_evaluation_skipped": True,
                "batch11_fail_closed": True,
            },
        )

    decision = _BATCH11_ORIGINAL_BUILD_ACTIVATION_DECISION(view, config=cfg)

    if decision.promoted or decision.safe_to_promote:
        if not _batch11_candidate_has_order_intent_contract(decision.selected):
            return _hold_decision(
                config=cfg,
                reason="order_intent_contract_not_ready",
                candidates=decision.candidates,
                blocked=decision.blocked,
                no_signal=decision.no_signal,
                selected=decision.selected,
                metadata={
                    "gate": "batch11_promotion_contract",
                    "required_flags": list(_BATCH11_PROMOTION_REQUIRED_FLAGS),
                    "required_metadata": list(_BATCH11_PROMOTION_REQUIRED_METADATA),
                    "activation_candidate_only": True,
                },
            )

    return decision

# =============================================================================
# Batch 11 corrective closure: infer candidate entry action
# =============================================================================
#
# Shared DoctrineEvaluationResult carries candidate truth but does not carry a
# direct action literal. Activation ranking filters candidates by ENTER_CALL /
# ENTER_PUT, so candidate frames must infer action from branch when result.action
# is absent. This keeps activation as candidate-selection only; it does not place
# orders or publish decisions.

_BATCH11_CANDIDATE_ACTION_INFERENCE_VERSION = "1"

if "_BATCH11_ORIGINAL_EVALUATION_TO_FRAME" not in globals():
    _BATCH11_ORIGINAL_EVALUATION_TO_FRAME = _evaluation_to_frame


def _batch11_action_for_candidate_frame(frame: DoctrineEvaluationFrame) -> str:
    branch = normalize_branch_id(frame.branch_id)
    candidate = as_mapping(frame.candidate)
    candidate_branch = normalize_branch_id(candidate.get("branch_id"))
    resolved_branch = branch or candidate_branch

    if resolved_branch == BRANCH_CALL:
        return ACTION_ENTER_CALL
    if resolved_branch == BRANCH_PUT:
        return ACTION_ENTER_PUT
    return frame.action


def _evaluation_to_frame(result: Any, *, family_id: str, branch_id: str) -> DoctrineEvaluationFrame:
    frame = _BATCH11_ORIGINAL_EVALUATION_TO_FRAME(
        result,
        family_id=family_id,
        branch_id=branch_id,
    )

    if (
        frame.is_candidate
        and frame.candidate is not None
        and frame.action not in {ACTION_ENTER_CALL, ACTION_ENTER_PUT}
    ):
        inferred_action = _batch11_action_for_candidate_frame(frame)
        return DoctrineEvaluationFrame(
            family_id=frame.family_id,
            branch_id=frame.branch_id,
            is_candidate=frame.is_candidate,
            is_blocked=frame.is_blocked,
            is_no_signal=frame.is_no_signal,
            action=inferred_action,
            score=frame.score,
            priority=frame.priority,
            candidate=frame.candidate,
            blocker=frame.blocker,
            reason=frame.reason,
            raw={
                **dict(frame.raw),
                "batch11_inferred_candidate_action": inferred_action,
            },
        )

    return frame
