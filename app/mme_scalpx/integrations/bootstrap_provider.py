"""
app/mme_scalpx/integrations/bootstrap_provider.py

Freeze-grade bootstrap provider for ScalpX MME.

This version keeps Dhan live feed active but makes Dhan context best-effort.
If Dhan /optionchain is throttled or unavailable, bootstrap still succeeds and
returns Dhan live feed surfaces while omitting the Dhan context adapter.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import logging
from pathlib import Path
from typing import Any

from app.mme_scalpx.core import names
from app.mme_scalpx.integrations.bootstrap_quote import build_kite
from app.mme_scalpx.integrations.broker_api import (
    KiteTransportClient,
    build_real_broker_adapter,
)
from app.mme_scalpx.integrations.dhan_marketdata import (
    DhanMarketdataConfig,
    DhanMarketdataManager,
)
from app.mme_scalpx.integrations.dhan_runtime_clients import (
    DhanFullFeedPollingAdapter,
    DhanNiftyRuntimeResolver,
    DhanOptionChainContextClient,
    DhanContextPollingAdapter,
    ResolvedDhanRuntimeIds,
)
from app.mme_scalpx.integrations.feed_adapter import build_real_feed_adapter
from app.mme_scalpx.integrations.runtime_instruments_factory import (
    RuntimeInstrumentsBuildResult,
    build_runtime_instruments,
)
from app.mme_scalpx.integrations.zerodha_feed_adapter import (
    load_api_config,
    load_token_state,
    validate_api_config_for_zerodha,
    validate_token_state_for_zerodha,
)

LOGGER = logging.getLogger(__name__)

VERSION = "mme-bootstrap-provider-v6-provider-truth-freeze"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DHAN_CONFIG_PATH = PROJECT_ROOT / "etc" / "brokers" / "dhan.yaml"

PROVIDER_ZERODHA = getattr(names, "PROVIDER_ZERODHA", "ZERODHA")
PROVIDER_DHAN = getattr(names, "PROVIDER_DHAN", "DHAN")


class BootstrapProviderError(RuntimeError):
    """Base bootstrap provider error."""


@dataclass(frozen=True)
class BootstrapProviderResult:
    version: str
    runtime_build: RuntimeInstrumentsBuildResult
    payload: dict[str, Any]


def _build_real_zerodha_broker() -> Any:
    api = load_api_config()
    state = load_token_state()
    validate_api_config_for_zerodha(api)
    validate_token_state_for_zerodha(state)

    kite = build_kite(api, state)
    transport = KiteTransportClient(kite=kite)

    return build_real_broker_adapter(
        broker="zerodha",
        transport_client=transport,
        auth_manager=None,
        requires_auth=False,
        metadata={
            "bootstrap_provider_version": VERSION,
            "transport_mode": "kite_transport_from_bootstrap_quote",
        },
    )


def _build_dhan_live_feed(
    *,
    runtime_instruments: Any,
) -> tuple[Any, ResolvedDhanRuntimeIds]:
    resolver = DhanNiftyRuntimeResolver()
    resolved_ids = resolver.resolve_from_runtime_instruments(runtime_instruments)

    adapter = DhanFullFeedPollingAdapter(
        runtime_instruments=runtime_instruments,
        resolved_ids=resolved_ids,
    )
    return adapter, resolved_ids


def _build_dhan_context_best_effort(
    *,
    runtime_instruments: Any,
    resolved_ids: ResolvedDhanRuntimeIds,
) -> Any | None:
    raw_cfg = DhanMarketdataConfig.from_yaml_file(DHAN_CONFIG_PATH)
    context_cfg = replace(raw_cfg, auth_required=False)

    try:
        context_client = DhanOptionChainContextClient(
            expiry=resolved_ids.selected_expiry,
            underlying_scrip=resolved_ids.underlying_scrip,
        )
        return DhanContextPollingAdapter(
            client=context_client,
            runtime_instruments=runtime_instruments,
            min_poll_interval_sec=max(float(context_cfg.context_refresh_ms) / 1000.0, 0.0),
            stale_after_sec=max(float(context_cfg.option_context_stale_after_ms) / 1000.0, 1.0),
            backoff_base_sec=max(float(context_cfg.option_context_dead_after_ms) / 3000.0, 1.0),
            backoff_max_sec=max(float(context_cfg.option_context_dead_after_ms) / 1000.0, 5.0),
        )
    except Exception as exc:
        LOGGER.warning(
            "bootstrap_provider_dhan_context_unavailable "
            "expiry=%s underlying_scrip=%s error=%s",
            resolved_ids.selected_expiry,
            resolved_ids.underlying_scrip,
            exc,
        )
        return None


def _build_bootstrap_payload_for_runtime_instruments(
    runtime_instruments: Any,
) -> dict[str, Any]:
    zerodha_feed_adapter = build_real_feed_adapter(
        runtime_instruments=runtime_instruments,
        broker="zerodha",
    )
    broker = _build_real_zerodha_broker()

    feed_adapters: dict[str, Any] = {
        PROVIDER_ZERODHA: zerodha_feed_adapter,
    }

    dhan_feed_adapter = None
    dhan_context_adapter = None
    resolved_ids: ResolvedDhanRuntimeIds | None = None
    dhan_live_error: str | None = None

    try:
        dhan_feed_adapter, resolved_ids = _build_dhan_live_feed(
            runtime_instruments=runtime_instruments,
        )
        feed_adapters[PROVIDER_DHAN] = dhan_feed_adapter
        dhan_context_adapter = _build_dhan_context_best_effort(
            runtime_instruments=runtime_instruments,
            resolved_ids=resolved_ids,
        )
    except Exception as exc:
        dhan_live_error = str(exc) or exc.__class__.__name__
        LOGGER.warning(
            "bootstrap_provider_dhan_live_unavailable error=%s",
            exc,
        )

    provider_bootstrap_report = {
        "version": VERSION,
        "zerodha_feed_adapter_configured": zerodha_feed_adapter is not None,
        "zerodha_broker_configured": broker is not None,
        "dhan_feed_adapter_configured": dhan_feed_adapter is not None,
        "dhan_context_adapter_configured": dhan_context_adapter is not None,
        "dhan_context_first_poll_required": dhan_context_adapter is not None,
        "dhan_live_error": dhan_live_error,
        "dhan_selected_expiry": None if resolved_ids is None else resolved_ids.selected_expiry,
        "dhan_underlying_scrip": None if resolved_ids is None else resolved_ids.underlying_scrip,
        "dhan_live_depth_mode_active": "FULL_TOP5_BASE",
        "dhan_live_depth_mode_target": "TOP20_ENHANCED",
        "dhan_context_bootstrap_status": (
            names.PROVIDER_STATUS_DEGRADED
            if dhan_context_adapter is not None
            else names.PROVIDER_STATUS_UNAVAILABLE
        ),
        "dhan_execution_fallback_status": names.PROVIDER_STATUS_DISABLED,
        "dhan_execution_fallback_reason": (
            "Dhan execution fallback disabled until concrete Dhan execution transport "
            "is implemented and proof-enabled"
        ),
    }

    return {
        "runtime_instruments": runtime_instruments,
        "feed_adapter": zerodha_feed_adapter,
        "zerodha_feed_adapter": zerodha_feed_adapter,
        "dhan_feed_adapter": dhan_feed_adapter,
        "dhan_context_adapter": dhan_context_adapter,
        "feed_adapters": feed_adapters,
        "broker": broker,
        "provider_bootstrap_report": provider_bootstrap_report,
    }


def build_bootstrap_payload() -> dict[str, Any]:
    built = build_runtime_instruments()
    return _build_bootstrap_payload_for_runtime_instruments(
        built.runtime_instruments
    )


def build_bootstrap_result() -> BootstrapProviderResult:
    runtime_build = build_runtime_instruments()
    payload = _build_bootstrap_payload_for_runtime_instruments(
        runtime_build.runtime_instruments
    )
    return BootstrapProviderResult(
        version=VERSION,
        runtime_build=runtime_build,
        payload=payload,
    )


def provide() -> dict[str, Any]:
    return build_bootstrap_payload()
