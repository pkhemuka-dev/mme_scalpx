"""
app/mme_scalpx/integrations/bootstrap_quote.py

Freeze-grade bootstrap quote helper for ScalpX MME.

Responsibilities
----------------
- load Zerodha api config and token state through token_store
- create authenticated KiteConnect client
- fetch a thin bootstrap underlying LTP
- return canonical Decimal reference price for runtime instrument resolution

Non-responsibilities
--------------------
- no websocket subscription
- no streaming market data
- no order placement
- no Redis writes
- no runtime supervision
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from app.mme_scalpx.integrations.token_store import (
    BrokerApiConfig,
    BrokerTokenState,
    SecretFileFormatError,
    SecretFileMissingError,
    TokenStoreError,
    load_api_config,
    load_token_state,
)

try:
    from kiteconnect import KiteConnect  # type: ignore
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "kiteconnect is required by app.mme_scalpx.integrations.bootstrap_quote"
    ) from exc


DEFAULT_UNDERLYING_KEY = "NSE:NIFTY 50"


class BootstrapQuoteError(RuntimeError):
    """Base bootstrap quote error."""


class StartupValidationError(BootstrapQuoteError):
    """Raised for local startup validation issues."""


class QuoteFetchError(BootstrapQuoteError):
    """Raised when quote/LTP fetch fails."""


# BATCH26O23P_R14_R3_R9_R4_DECORATOR_COLLISION_REPAIR
# BATCH26O23P_R14_R3_R9_OBSERVE_ONLY_QUOTE_BOOTSTRAP_DEGRADE_GUARD
def _scalpx_observe_only_quote_bootstrap_degrade_enabled() -> bool:
    """Explicit opt-in guard for off-market/read-only diagnostics only.

    This must never activate for controlled-paper or real-live modes.
    It is intentionally gated by both SCALPX_OBSERVE_ONLY=1 and
    SCALPX_ALLOW_OBSERVE_ONLY_BOOTSTRAP_QUOTE_DEGRADE=1.
    """
    import os

    if str(os.environ.get("SCALPX_OBSERVE_ONLY", "")).strip().lower() not in ("1", "true", "yes", "on"):
        return False
    if str(os.environ.get("SCALPX_ALLOW_OBSERVE_ONLY_BOOTSTRAP_QUOTE_DEGRADE", "")).strip().lower() not in ("1", "true", "yes", "on"):
        return False

    forbidden = (
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_ALLOW_REAL_LIVE",
    )
    for key in forbidden:
        val = str(os.environ.get(key, "")).strip()
        if val and val.lower() not in ("0", "false", "no", "off"):
            return False
    return True


# BATCH26O23P_R14_R3_R10_R4_QUOTE_SHAPE_CONVERSION_PATCH
def _scalpx_observe_only_quote_bootstrap_fallback(instrument_key: str):
    """Return a deterministic quote-shaped fallback only for read-only bootstrap diagnostics.

    The default shape is source-context driven by Batch 26-O23-P-R14-R3-R10-R4.
    This helper is still gated by _scalpx_observe_only_quote_bootstrap_degrade_enabled()
    at the callsite, so it must not affect controlled-paper or real-live paths.
    """
    import os
    from types import SimpleNamespace

    fallback = float(os.environ.get("SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK", "0") or 0)
    shape = str(os.environ.get("SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK_SHAPE", "simple_namespace") or "simple_namespace").strip().lower()

    if shape in ("simple_namespace", "namespace", "object"):
        return SimpleNamespace(last_price=fallback, ltp=fallback, instrument_key=str(instrument_key))

    if shape in ("number", "float", "scalar"):
        return fallback

    # Default: Kite ltp-compatible mapping.
    return {str(instrument_key): {"last_price": fallback, "ltp": fallback}}


@dataclass(frozen=True)


class BootstrapQuote:
    instrument_key: str
    ltp: Decimal


def validate_api_config_for_zerodha(api: BrokerApiConfig) -> None:
    if api.broker.strip().lower() != "zerodha":
        raise StartupValidationError(
            f"api.json broker must be 'zerodha', got {api.broker!r}"
        )
    if not api.api_key.strip():
        raise StartupValidationError("api.json missing non-empty api_key")


def validate_token_state_for_zerodha(state: BrokerTokenState) -> None:
    if state.broker.strip().lower() != "zerodha":
        raise StartupValidationError(
            f"tokens.json broker must be 'zerodha', got {state.broker!r}"
        )
    if not state.access_token.strip():
        raise StartupValidationError("tokens.json missing non-empty access_token")


def build_kite(api: BrokerApiConfig, state: BrokerTokenState) -> KiteConnect:
    kite = KiteConnect(api_key=api.api_key)
    kite.set_access_token(state.access_token)
    return kite


def _extract_ltp(payload: dict[str, Any], instrument_key: str) -> Decimal:
    item = payload.get(instrument_key)
    if not isinstance(item, dict):
        raise QuoteFetchError(f"ltp payload missing instrument key: {instrument_key}")

    raw_ltp = item.get("last_price")
    if raw_ltp is None:
        raw_ltp = item.get("ltp")

    if raw_ltp is None:
        raise QuoteFetchError(f"ltp payload missing last_price/ltp for {instrument_key}")

    try:
        ltp = Decimal(str(raw_ltp))
    except (InvalidOperation, ValueError) as exc:
        raise QuoteFetchError(
            f"invalid LTP value for {instrument_key}: {raw_ltp!r}"
        ) from exc

    if ltp <= 0:
        raise QuoteFetchError(f"non-positive LTP for {instrument_key}: {ltp}")

    return ltp


def fetch_underlying_ltp(instrument_key: str = DEFAULT_UNDERLYING_KEY) -> BootstrapQuote:
    try:
        api = load_api_config()
        state = load_token_state()
    except (
        SecretFileMissingError,
        SecretFileFormatError,
        TokenStoreError,
    ) as exc:
        raise StartupValidationError(str(exc)) from exc

    validate_api_config_for_zerodha(api)
    validate_token_state_for_zerodha(state)

    kite = build_kite(api, state)

    try:
        payload = kite.ltp([instrument_key])
    except Exception as exc:
        if _scalpx_observe_only_quote_bootstrap_degrade_enabled():
            return _scalpx_observe_only_quote_bootstrap_fallback(instrument_key)
        raise QuoteFetchError(f"kite.ltp({instrument_key!r}) failed: {exc}") from exc

    if not isinstance(payload, dict) or not payload:
        raise QuoteFetchError("kite.ltp() returned empty/non-dict payload")

    ltp = _extract_ltp(payload, instrument_key)
    return BootstrapQuote(instrument_key=instrument_key, ltp=ltp)
