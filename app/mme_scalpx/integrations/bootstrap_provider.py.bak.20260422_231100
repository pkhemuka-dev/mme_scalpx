"""
app/mme_scalpx/integrations/bootstrap_provider.py

Freeze-grade bootstrap provider for ScalpX MME.

Responsibilities
----------------
- build a deterministic bootstrap payload for main.py
- provide runtime instruments from:
  - persisted broker session
  - live bootstrap quote
  - real instrument master
- expose canonical aliases expected by runtime callers

Non-responsibilities
--------------------
- no runtime supervision
- no Redis writes
- no market-data streaming
- no order placement
- no alternate composition root
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.mme_scalpx.integrations.bootstrap_quote import build_kite
from app.mme_scalpx.integrations.broker_api import (
    KiteTransportClient,
    build_real_broker_adapter,
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

VERSION = "mme-bootstrap-provider-v3-zerodha-kite-transport"


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


def build_bootstrap_payload() -> dict[str, Any]:
    """
    Canonical provider payload for main.py dependency registration.

    Current intended keys:
    - runtime_instruments
    - feed_adapter
    - broker
    """
    built = build_runtime_instruments()
    feed_adapter = build_real_feed_adapter(
        runtime_instruments=built.runtime_instruments,
        broker="zerodha",
    )
    broker = _build_real_zerodha_broker()
    return {
        "runtime_instruments": built.runtime_instruments,
        "feed_adapter": feed_adapter,
        "broker": broker,
    }


def build_bootstrap_result() -> BootstrapProviderResult:
    runtime_build = build_runtime_instruments()
    feed_adapter = build_real_feed_adapter(
        runtime_instruments=runtime_build.runtime_instruments,
        broker="zerodha",
    )
    broker = _build_real_zerodha_broker()
    payload = {
        "runtime_instruments": runtime_build.runtime_instruments,
        "feed_adapter": feed_adapter,
        "broker": broker,
    }
    return BootstrapProviderResult(
        version=VERSION,
        runtime_build=runtime_build,
        payload=payload,
    )


def provide() -> dict[str, Any]:
    """
    Thin canonical entrypoint for main.py bootstrap-provider hook.

    This returns only the payload dictionary expected for dependency injection.
    """
    return build_bootstrap_payload()
