"""
app/mme_scalpx/integrations/bootstrap_provider_null_broker.py

Additive fully-offline diagnostic bootstrap provider.

Purpose:
- provide RuntimeInstrumentSet using explicit offline fallback LTP
- provide NullBrokerAdapter instead of a real broker
- provide NullFeedAdapter surfaces instead of live Zerodha/Dhan feeds
- never build KiteTicker / KiteConnect / KiteTransportClient
- never call build_real_feed_adapter()
- never call build_real_broker_adapter()
- never call build_runtime_instruments()
- never call fetch_underlying_ltp()
- never construct Dhan live/context clients
- never place, cancel, reconcile, connect, poll, or publish

Use only with explicit:
  MME_BOOTSTRAP_PROVIDER=app.mme_scalpx.integrations.bootstrap_provider_null_broker:provide

Offline LTP:
  SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK must be a positive number.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import os
from pathlib import Path
from typing import Any

from app.mme_scalpx.core import names
from app.mme_scalpx.domain.instruments import resolve_runtime_instruments
from app.mme_scalpx.integrations.bootstrap_quote import BootstrapQuote
from app.mme_scalpx.integrations.broker_api import build_null_broker_adapter
from app.mme_scalpx.integrations.feed_adapter import NullFeedAdapter
from app.mme_scalpx.integrations.runtime_instruments_factory import (
    RuntimeInstrumentsBuildResult,
    build_instrument_config,
)

VERSION = "mme-bootstrap-provider-null-broker-v4-offline-ltp-null-feeds-main-compatible"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_QUOTE_KEY = "NSE:NIFTY 50"

PROVIDER_ZERODHA = getattr(names, "PROVIDER_ZERODHA", "ZERODHA")
PROVIDER_DHAN = getattr(names, "PROVIDER_DHAN", "DHAN")


@dataclass(frozen=True)
class BootstrapProviderNullBrokerResult:
    version: str
    runtime_build: RuntimeInstrumentsBuildResult
    payload: dict[str, Any]


class BootstrapProviderNullBrokerError(RuntimeError):
    """Raised when the explicit null-broker provider cannot build safely."""


def _offline_bootstrap_ltp() -> Decimal:
    raw = str(os.environ.get("SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK", "")).strip()
    if not raw:
        raise BootstrapProviderNullBrokerError(
            "SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK is required for null-provider offline bootstrap"
        )

    try:
        ltp = Decimal(raw)
    except Exception as exc:
        raise BootstrapProviderNullBrokerError(
            f"invalid SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK={raw!r}"
        ) from exc

    if ltp <= 0:
        raise BootstrapProviderNullBrokerError(
            f"SCALPX_OBSERVE_ONLY_BOOTSTRAP_LTP_FALLBACK must be positive, got {ltp}"
        )

    return ltp


def _build_offline_runtime_instruments() -> RuntimeInstrumentsBuildResult:
    ltp = _offline_bootstrap_ltp()
    quote = BootstrapQuote(instrument_key=DEFAULT_QUOTE_KEY, ltp=ltp)
    config = build_instrument_config()
    runtime = resolve_runtime_instruments(
        config=config,
        underlying_ltp=ltp,
    )
    return RuntimeInstrumentsBuildResult(
        quote=quote,
        config=config,
        runtime_instruments=runtime,
    )


def _build_bootstrap_payload_for_runtime_instruments(
    runtime_instruments: Any,
) -> dict[str, Any]:
    zerodha_feed_adapter = NullFeedAdapter()
    dhan_feed_adapter = NullFeedAdapter()

    broker = build_null_broker_adapter(
        provider_id=PROVIDER_ZERODHA,
        reason="explicit additive offline-ltp null-broker null-feed diagnostic provider",
    )

    feed_adapters: dict[str, Any] = {
        PROVIDER_ZERODHA: zerodha_feed_adapter,
        PROVIDER_DHAN: dhan_feed_adapter,
    }

    ltp = _offline_bootstrap_ltp()

    provider_bootstrap_report = {
        "version": VERSION,
        "diagnostic_provider": True,
        "offline_ltp_bootstrap": True,
        "bootstrap_quote_instrument_key": DEFAULT_QUOTE_KEY,
        "bootstrap_quote_ltp": str(ltp),
        "zerodha_feed_adapter_configured": False,
        "dhan_feed_adapter_configured": False,
        "null_feed_adapters_configured": True,
        "zerodha_broker_configured": False,
        "null_broker_configured": broker is not None,
        "broker_mode": getattr(broker, "mode", "unknown"),
        "broker_provider_id": getattr(broker, "provider_id", ""),
        "dhan_context_adapter_configured": False,
        "dhan_context_first_poll_required": False,
        "dhan_live_error": None,
        "dhan_selected_expiry": None,
        "dhan_underlying_scrip": None,
        "dhan_execution_fallback_status": names.PROVIDER_STATUS_DISABLED,
        "dhan_execution_fallback_reason": (
            "Dhan execution fallback disabled; diagnostic null provider supplies no real execution transport"
        ),
        "real_broker_order_enabled": False,
        "kite_ticker_built": False,
        "kite_connect_built": False,
        "kite_transport_client_built": False,
        "build_real_feed_adapter_called": False,
        "build_runtime_instruments_called": False,
        "fetch_underlying_ltp_called": False,
        "feed_connect_called": False,
        "feed_poll_called": False,
    }

    return {
        "runtime_instruments": runtime_instruments,
        "feed_adapter": zerodha_feed_adapter,
        "zerodha_feed_adapter": zerodha_feed_adapter,
        "dhan_feed_adapter": dhan_feed_adapter,
        "dhan_context_adapter": None,
        "feed_adapters": feed_adapters,
        "broker": broker,
        "provider_bootstrap_report": provider_bootstrap_report,
    }


def build_bootstrap_payload() -> dict[str, Any]:
    built = _build_offline_runtime_instruments()
    return _build_bootstrap_payload_for_runtime_instruments(
        built.runtime_instruments
    )


def build_bootstrap_result() -> BootstrapProviderNullBrokerResult:
    runtime_build = _build_offline_runtime_instruments()
    payload = _build_bootstrap_payload_for_runtime_instruments(
        runtime_build.runtime_instruments
    )
    return BootstrapProviderNullBrokerResult(
        version=VERSION,
        runtime_build=runtime_build,
        payload=payload,
    )


def provide() -> dict[str, Any]:
    return build_bootstrap_payload()
