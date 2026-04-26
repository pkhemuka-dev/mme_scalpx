from __future__ import annotations

"""
Batch 25Q disabled promoted-decision adapter.

This module builds an execution-entry-shaped PREVIEW from standardized
strategy-family candidate metadata, but it does not publish, place orders,
mutate risk, mutate execution, or enable strategy promotion.

Default law:
- observe_only: preview allowed, publish forbidden
- legacy_live_family_shadow: preview allowed, publish forbidden
- family_live_legacy_shadow: publish forbidden until later arming proof
- family_live_only: forbidden in this batch
"""

import math
from dataclasses import dataclass, field
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N


ACTION_ENTER_CALL: Final[str] = getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
ACTION_ENTER_PUT: Final[str] = getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")
SIDE_CALL: Final[str] = getattr(N, "SIDE_CALL", getattr(N, "BRANCH_CALL", "CALL"))
SIDE_PUT: Final[str] = getattr(N, "SIDE_PUT", getattr(N, "BRANCH_PUT", "PUT"))
BRANCH_CALL: Final[str] = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT: Final[str] = getattr(N, "BRANCH_PUT", "PUT")
POSITION_EFFECT_OPEN: Final[str] = getattr(N, "POSITION_EFFECT_OPEN", "OPEN")

FAMILY_RUNTIME_MODE_OBSERVE_ONLY: Final[str] = getattr(
    N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"
)
FAMILY_RUNTIME_MODE_LEGACY_LIVE_FAMILY_SHADOW: Final[str] = getattr(
    N, "FAMILY_RUNTIME_MODE_LEGACY_LIVE_FAMILY_SHADOW", "legacy_live_family_shadow"
)
FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW: Final[str] = getattr(
    N, "FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW", "family_live_legacy_shadow"
)
FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY: Final[str] = getattr(
    N, "FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY", "family_live_only"
)

REQUIRED_TOP_LEVEL_FIELDS: Final[tuple[str, ...]] = (
    "action",
    "side",
    "position_effect",
    "quantity_lots",
    "instrument_key",
    "entry_mode",
)

REQUIRED_METADATA_FIELDS: Final[tuple[str, ...]] = (
    "option_symbol",
    "option_token",
    "strike",
    "limit_price",
    "provider_id",
    "execution_provider_id",
    "strategy_family",
    "strategy_branch",
    "doctrine_id",
    "candidate_id",
)

UNKNOWN_ENTRY_MODES: Final[set[str]] = {"", "UNKNOWN", "NONE", "NULL", "N/A"}


class OrderIntentAdapterError(ValueError):
    """Raised when a candidate cannot satisfy the order-intent preview contract."""


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        out = float(str(value).strip())
    except Exception:
        return default
    return out if math.isfinite(out) else default


def _safe_int(value: Any, default: int = 0) -> int:
    if value is None or isinstance(value, bool):
        return default
    try:
        return int(float(str(value).strip()))
    except Exception:
        return default


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        out = value.to_dict()
        if isinstance(out, Mapping):
            return dict(out)
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def _metadata(candidate: Mapping[str, Any]) -> dict[str, Any]:
    meta = candidate.get("metadata")
    return dict(meta) if isinstance(meta, Mapping) else {}


def _pick(candidate: Mapping[str, Any], metadata: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = candidate.get(key)
        if value not in (None, ""):
            return value
        value = metadata.get(key)
        if value not in (None, ""):
            return value
    return None


def normalize_side(value: Any, *, branch_id: Any = None, action: Any = None) -> str:
    text = _safe_str(value).upper()
    branch = _safe_str(branch_id).upper()
    action_text = _safe_str(action).upper()

    if text in {"CALL", "CE", "C", SIDE_CALL, BRANCH_CALL}:
        return SIDE_CALL
    if text in {"PUT", "PE", "P", SIDE_PUT, BRANCH_PUT}:
        return SIDE_PUT
    if branch in {"CALL", "CE", "C", SIDE_CALL, BRANCH_CALL}:
        return SIDE_CALL
    if branch in {"PUT", "PE", "P", SIDE_PUT, BRANCH_PUT}:
        return SIDE_PUT
    if action_text == ACTION_ENTER_CALL:
        return SIDE_CALL
    if action_text == ACTION_ENTER_PUT:
        return SIDE_PUT
    return ""


def action_for_side(side: str) -> str:
    if side == SIDE_CALL:
        return ACTION_ENTER_CALL
    if side == SIDE_PUT:
        return ACTION_ENTER_PUT
    return ""


def is_publication_allowed(
    *,
    runtime_mode: str,
    adapter_enabled: bool = False,
    arming_proof_ok: bool = False,
    final_readiness_ok: bool = False,
) -> bool:
    mode = _safe_str(runtime_mode, FAMILY_RUNTIME_MODE_OBSERVE_ONLY)

    if mode in {
        FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
        FAMILY_RUNTIME_MODE_LEGACY_LIVE_FAMILY_SHADOW,
        FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY,
    }:
        return False

    if mode != FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW:
        return False

    return bool(adapter_enabled and arming_proof_ok and final_readiness_ok)


@dataclass(frozen=True, slots=True)
class OrderIntentPreview:
    preview_valid: bool
    execution_contract_fields_complete: bool
    publication_allowed: bool
    runtime_mode: str
    adapter_enabled: bool
    blockers: tuple[str, ...]
    decision: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "preview_valid": self.preview_valid,
            "execution_contract_fields_complete": self.execution_contract_fields_complete,
            "publication_allowed": self.publication_allowed,
            "runtime_mode": self.runtime_mode,
            "adapter_enabled": self.adapter_enabled,
            "blockers": list(self.blockers),
            "decision": dict(self.decision),
            "metadata": dict(self.metadata),
        }


def build_execution_entry_decision(candidate_like: Any) -> dict[str, Any]:
    candidate = _as_mapping(candidate_like)
    metadata = _metadata(candidate)

    family = _safe_str(_pick(candidate, metadata, "strategy_family", "family_id", "strategy_family_id"))
    branch = _safe_str(_pick(candidate, metadata, "strategy_branch", "branch_id", "strategy_branch_id"))
    action_hint = _safe_str(_pick(candidate, metadata, "action", "action_hint"))
    side = normalize_side(_pick(candidate, metadata, "side", "option_side"), branch_id=branch, action=action_hint)
    action = action_hint if action_hint in {ACTION_ENTER_CALL, ACTION_ENTER_PUT} else action_for_side(side)

    quantity_lots = _safe_int(_pick(candidate, metadata, "quantity_lots", "quantity_lots_hint", "qty_lots"), 0)
    limit_price = _safe_float(_pick(candidate, metadata, "limit_price", "limit_price_hint"), 0.0)
    strike = _safe_float(_pick(candidate, metadata, "strike", "strike_price"), 0.0)

    decision_metadata = {
        "option_symbol": _safe_str(_pick(candidate, metadata, "option_symbol", "trading_symbol", "symbol")),
        "option_token": _safe_str(_pick(candidate, metadata, "option_token", "instrument_token", "token")),
        "strike": strike,
        "limit_price": limit_price,
        "provider_id": _safe_str(_pick(candidate, metadata, "provider_id", "marketdata_provider_id")),
        "execution_provider_id": _safe_str(_pick(candidate, metadata, "execution_provider_id")),
        "strategy_family": family,
        "strategy_branch": branch,
        "doctrine_id": _safe_str(_pick(candidate, metadata, "doctrine_id")),
        "candidate_id": _safe_str(_pick(candidate, metadata, "candidate_id")),
        "reason_code": _safe_str(_pick(candidate, metadata, "reason_code", "reason")),
        "confidence": _safe_float(_pick(candidate, metadata, "confidence", "score"), 0.0),
        "order_intent_adapter": "batch25q_disabled_preview",
    }

    return {
        "action": action,
        "side": side,
        "position_effect": POSITION_EFFECT_OPEN,
        "quantity_lots": quantity_lots,
        "instrument_key": _safe_str(_pick(candidate, metadata, "instrument_key")),
        "entry_mode": _safe_str(_pick(candidate, metadata, "entry_mode")),
        "metadata": decision_metadata,
    }


def validate_execution_contract_fields(decision: Mapping[str, Any]) -> tuple[bool, tuple[str, ...]]:
    blockers: list[str] = []
    metadata = _as_mapping(decision.get("metadata"))

    for key in REQUIRED_TOP_LEVEL_FIELDS:
        if decision.get(key) in (None, ""):
            blockers.append(f"missing_top_level.{key}")

    if decision.get("action") not in {ACTION_ENTER_CALL, ACTION_ENTER_PUT}:
        blockers.append("invalid_action")
    if decision.get("side") not in {SIDE_CALL, SIDE_PUT}:
        blockers.append("invalid_side")
    if decision.get("position_effect") != POSITION_EFFECT_OPEN:
        blockers.append("invalid_position_effect")
    if _safe_int(decision.get("quantity_lots"), 0) <= 0:
        blockers.append("invalid_quantity_lots")
    if _safe_str(decision.get("entry_mode")).upper() in UNKNOWN_ENTRY_MODES:
        blockers.append("invalid_entry_mode")

    for key in REQUIRED_METADATA_FIELDS:
        if metadata.get(key) in (None, ""):
            blockers.append(f"missing_metadata.{key}")

    if _safe_float(metadata.get("strike"), 0.0) <= 0:
        blockers.append("invalid_metadata.strike")
    if _safe_float(metadata.get("limit_price"), 0.0) <= 0:
        blockers.append("invalid_metadata.limit_price")

    return (not blockers, tuple(blockers))


def build_order_intent_preview(
    candidate_like: Any,
    *,
    runtime_mode: str = FAMILY_RUNTIME_MODE_OBSERVE_ONLY,
    adapter_enabled: bool = False,
    arming_proof_ok: bool = False,
    final_readiness_ok: bool = False,
) -> OrderIntentPreview:
    decision = build_execution_entry_decision(candidate_like)
    fields_ok, blockers = validate_execution_contract_fields(decision)

    publish_allowed = is_publication_allowed(
        runtime_mode=runtime_mode,
        adapter_enabled=adapter_enabled,
        arming_proof_ok=arming_proof_ok,
        final_readiness_ok=final_readiness_ok,
    )

    preview_blockers = list(blockers)
    if publish_allowed:
        preview_blockers.append("batch25q_publication_must_remain_disabled")

    preview_valid = fields_ok and not publish_allowed

    return OrderIntentPreview(
        preview_valid=preview_valid,
        execution_contract_fields_complete=fields_ok,
        publication_allowed=publish_allowed,
        runtime_mode=_safe_str(runtime_mode, FAMILY_RUNTIME_MODE_OBSERVE_ONLY),
        adapter_enabled=bool(adapter_enabled),
        blockers=tuple(preview_blockers),
        decision=decision,
        metadata={
            "law": "disabled_preview_only",
            "strategy_publication_owner": "strategy.py",
            "execution_owner": "execution.py",
            "risk_owner": "risk.py",
        },
    )


__all__ = [
    "ACTION_ENTER_CALL",
    "ACTION_ENTER_PUT",
    "OrderIntentAdapterError",
    "OrderIntentPreview",
    "build_execution_entry_decision",
    "build_order_intent_preview",
    "is_publication_allowed",
    "validate_execution_contract_fields",
]
