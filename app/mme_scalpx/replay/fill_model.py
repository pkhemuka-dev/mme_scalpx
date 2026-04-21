"""
app/mme_scalpx/replay/fill_model.py

Freeze-grade replay-only fill model layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Fill-model responsibilities
---------------------------
This module owns:
- canonical replay-only fill request/result contracts
- deterministic fill model taxonomy
- replay-only fill decision logic
- machine-readable serialization helpers

This module does not own:
- live broker execution
- production execution truth
- replay orchestration
- dataset discovery/loading
- doctrine mutation
- artifact persistence

Design rules
------------
- fill behavior here is replay-only and must never be treated as broker truth
- all fill assumptions must be explicit and auditable
- identical inputs + identical model must yield identical output
- no hidden live-side effects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .modes import DoctrineMode


class ReplayFillModelError(RuntimeError):
    """Base exception for replay fill-model failures."""


class ReplayFillModelValidationError(ReplayFillModelError):
    """Raised when fill-model inputs are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayFillRequest:
    """
    Canonical replay-only fill request.

    Fields are intentionally generic and broker-agnostic.
    """

    run_id: str
    order_id: str
    side: str
    qty: int
    order_price: float | None = None
    market_price: float | None = None
    best_bid: float | None = None
    best_ask: float | None = None
    timestamp: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReplayFillResult:
    """
    Canonical replay-only fill result.
    """

    order_id: str
    model_name: str
    filled: bool
    fill_qty: int
    fill_price: float | None
    slippage: float | None
    reason: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReplayFillModelConfig:
    """
    Canonical fill model config.
    """

    model_name: str
    doctrine_mode: DoctrineMode
    allow_partial_fills: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayFillModel(Protocol):
    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
        ...


class ImmediateMarketFillModel:
    """
    Replay-only model:
    - BUY fills at best_ask if present, else market_price
    - SELL fills at best_bid if present, else market_price
    - full fill only
    """

    def __init__(self, config: ReplayFillModelConfig) -> None:
        _validate_config(config)
        self._config = config

    @property
    def config(self) -> ReplayFillModelConfig:
        return self._config

    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
        _validate_request(request)

        fill_price = _resolve_immediate_market_fill_price(request)
        if fill_price is None:
            return ReplayFillResult(
                order_id=request.order_id,
                model_name=self._config.model_name,
                filled=False,
                fill_qty=0,
                fill_price=None,
                slippage=None,
                reason="no_fill_price_available",
                metadata={},
            )

        reference = request.market_price
        slippage = None
        if reference is not None:
            slippage = fill_price - reference

        return ReplayFillResult(
            order_id=request.order_id,
            model_name=self._config.model_name,
            filled=True,
            fill_qty=request.qty,
            fill_price=fill_price,
            slippage=slippage,
            reason="immediate_market_fill",
            metadata={},
        )


class LimitTouchFillModel:
    """
    Replay-only model:
    - BUY fills if market/ask <= order_price
    - SELL fills if market/bid >= order_price
    - full fill only
    """

    def __init__(self, config: ReplayFillModelConfig) -> None:
        _validate_config(config)
        self._config = config

    @property
    def config(self) -> ReplayFillModelConfig:
        return self._config

    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
        _validate_request(request)
        if request.order_price is None:
            raise ReplayFillModelValidationError(
                "limit-touch fill model requires order_price"
            )

        fill_price = _resolve_limit_touch_fill_price(request)
        if fill_price is None:
            return ReplayFillResult(
                order_id=request.order_id,
                model_name=self._config.model_name,
                filled=False,
                fill_qty=0,
                fill_price=None,
                slippage=None,
                reason="limit_not_touched",
                metadata={},
            )

        reference = request.market_price
        slippage = None
        if reference is not None:
            slippage = fill_price - reference

        return ReplayFillResult(
            order_id=request.order_id,
            model_name=self._config.model_name,
            filled=True,
            fill_qty=request.qty,
            fill_price=fill_price,
            slippage=slippage,
            reason="limit_touch_fill",
            metadata={},
        )


class ReplayFillModelFactory:
    """
    Freeze-grade replay fill model factory.
    """

    IMMEDIATE_MARKET = "immediate_market"
    LIMIT_TOUCH = "limit_touch"

    @classmethod
    def create(
        cls,
        config: ReplayFillModelConfig,
    ) -> ReplayFillModel:
        _validate_config(config)

        if config.model_name == cls.IMMEDIATE_MARKET:
            return ImmediateMarketFillModel(config)
        if config.model_name == cls.LIMIT_TOUCH:
            return LimitTouchFillModel(config)

        raise ReplayFillModelValidationError(
            f"unsupported fill model name: {config.model_name!r}"
        )


def fill_request_to_dict(request: ReplayFillRequest) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "order_id": request.order_id,
        "side": request.side,
        "qty": request.qty,
        "order_price": request.order_price,
        "market_price": request.market_price,
        "best_bid": request.best_bid,
        "best_ask": request.best_ask,
        "timestamp": request.timestamp,
        "metadata": dict(request.metadata),
    }


def fill_result_to_dict(result: ReplayFillResult) -> dict[str, Any]:
    return {
        "order_id": result.order_id,
        "model_name": result.model_name,
        "filled": result.filled,
        "fill_qty": result.fill_qty,
        "fill_price": result.fill_price,
        "slippage": result.slippage,
        "reason": result.reason,
        "metadata": dict(result.metadata),
    }


def _validate_config(config: ReplayFillModelConfig) -> None:
    if not isinstance(config.model_name, str) or not config.model_name.strip():
        raise ReplayFillModelValidationError(
            f"model_name must be non-empty string, got {config.model_name!r}"
        )
    if config.allow_partial_fills:
        raise ReplayFillModelValidationError(
            "partial fills are not yet supported in frozen fill model"
        )
    for note in config.notes:
        if not isinstance(note, str):
            raise ReplayFillModelValidationError(
                f"config note must be string, got {note!r}"
            )


def _validate_request(request: ReplayFillRequest) -> None:
    if not isinstance(request.run_id, str) or not request.run_id.strip():
        raise ReplayFillModelValidationError(
            f"run_id must be non-empty string, got {request.run_id!r}"
        )
    if not isinstance(request.order_id, str) or not request.order_id.strip():
        raise ReplayFillModelValidationError(
            f"order_id must be non-empty string, got {request.order_id!r}"
        )
    if request.side not in ("BUY", "SELL"):
        raise ReplayFillModelValidationError(
            f"side must be 'BUY' or 'SELL', got {request.side!r}"
        )
    if not isinstance(request.qty, int) or request.qty <= 0:
        raise ReplayFillModelValidationError(
            f"qty must be positive int, got {request.qty!r}"
        )
    if not isinstance(request.metadata, Mapping):
        raise ReplayFillModelValidationError(
            f"metadata must be mapping, got {type(request.metadata)!r}"
        )


def _resolve_immediate_market_fill_price(request: ReplayFillRequest) -> float | None:
    if request.side == "BUY":
        if request.best_ask is not None:
            return request.best_ask
        return request.market_price
    if request.best_bid is not None:
        return request.best_bid
    return request.market_price


def _resolve_limit_touch_fill_price(request: ReplayFillRequest) -> float | None:
    assert request.order_price is not None

    if request.side == "BUY":
        touch_price = request.best_ask if request.best_ask is not None else request.market_price
        if touch_price is not None and touch_price <= request.order_price:
            return touch_price
        return None

    touch_price = request.best_bid if request.best_bid is not None else request.market_price
    if touch_price is not None and touch_price >= request.order_price:
        return touch_price
    return None


__all__ = [
    "ReplayFillModelError",
    "ReplayFillModelValidationError",
    "ReplayFillRequest",
    "ReplayFillResult",
    "ReplayFillModelConfig",
    "ReplayFillModel",
    "ImmediateMarketFillModel",
    "LimitTouchFillModel",
    "ReplayFillModelFactory",
    "fill_request_to_dict",
    "fill_result_to_dict",
]
