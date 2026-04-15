"""
app/mme_scalpx/integrations/runtime_instruments_factory.py

Freeze-grade runtime instruments factory for ScalpX MME.

Responsibilities
----------------
- fetch bootstrap underlying LTP through bootstrap_quote
- construct canonical InstrumentConfig
- resolve RuntimeInstrumentSet through domain/instruments.py

Non-responsibilities
--------------------
- no streaming feeds
- no broker order integration
- no Redis publication
- no service supervision
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.mme_scalpx.domain.instruments import (
    InstrumentConfig,
    RuntimeInstrumentSet,
    resolve_runtime_instruments,
)
from app.mme_scalpx.integrations.bootstrap_quote import (
    BootstrapQuote,
    fetch_underlying_ltp,
)

CANONICAL_SOURCE_PATH = Path(
    "/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv"
)
DEFAULT_UNDERLYING_SYMBOL = "NIFTY"
DEFAULT_QUOTE_KEY = "NSE:NIFTY 50"


class RuntimeInstrumentsFactoryError(RuntimeError):
    """Base runtime instruments factory error."""


@dataclass(frozen=True)
class RuntimeInstrumentsBuildResult:
    quote: BootstrapQuote
    config: InstrumentConfig
    runtime_instruments: RuntimeInstrumentSet


def build_instrument_config(
    *,
    source_path: Path = CANONICAL_SOURCE_PATH,
    underlying_symbol: str = DEFAULT_UNDERLYING_SYMBOL,
) -> InstrumentConfig:
    return InstrumentConfig(
        source_path=source_path,
        underlying_symbol=underlying_symbol,
        future_root=underlying_symbol,
        option_root=underlying_symbol,
        field_map={},
    )


def build_runtime_instruments(
    *,
    quote_key: str = DEFAULT_QUOTE_KEY,
    source_path: Path = CANONICAL_SOURCE_PATH,
    underlying_symbol: str = DEFAULT_UNDERLYING_SYMBOL,
) -> RuntimeInstrumentsBuildResult:
    quote = fetch_underlying_ltp(quote_key)
    config = build_instrument_config(
        source_path=source_path,
        underlying_symbol=underlying_symbol,
    )
    runtime = resolve_runtime_instruments(
        config=config,
        underlying_ltp=quote.ltp,
    )
    return RuntimeInstrumentsBuildResult(
        quote=quote,
        config=config,
        runtime_instruments=runtime,
    )


def build_runtime_context_payload() -> dict[str, Any]:
    """
    Thin helper for bootstrap/provider integration.

    Returns both canonical keys because existing runtime callers may look for:
    - runtime_instruments
    - instrument_set
    """
    built = build_runtime_instruments()
    return {
        "bootstrap_quote": {
            "instrument_key": built.quote.instrument_key,
            "ltp": str(built.quote.ltp),
        },
        "runtime_instruments": built.runtime_instruments,
        "instrument_set": built.runtime_instruments,
    }
