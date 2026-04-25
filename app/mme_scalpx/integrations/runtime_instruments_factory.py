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
from datetime import timedelta
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

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_SOURCE_PATH = Path(
    "/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv"
)
DEFAULT_SYMBOLS_PATH = PROJECT_ROOT / "etc" / "symbols.yaml"
DEFAULT_UNDERLYING_SYMBOL = "NIFTY"
DEFAULT_QUOTE_KEY = "NSE:NIFTY 50"

_WEEKDAY_BY_NAME = {
    "MONDAY": 0,
    "MON": 0,
    "TUESDAY": 1,
    "TUE": 1,
    "TUES": 1,
    "WEDNESDAY": 2,
    "WED": 2,
    "THURSDAY": 3,
    "THU": 3,
    "THURS": 3,
    "FRIDAY": 4,
    "FRI": 4,
    "SATURDAY": 5,
    "SAT": 5,
    "SUNDAY": 6,
    "SUN": 6,
}




def _parse_bool_text(value: object, *, default: bool) -> bool:
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _parse_decimal_text(value: object) -> Decimal | None:
    if value is None:
        return None
    text = str(value).strip().strip('"').strip("'")
    if not text:
        return None
    return Decimal(text)


def _parse_weekday(value: object, *, default: int) -> int:
    if value is None:
        return default
    text = str(value).strip().strip('"').strip("'")
    if not text:
        return default
    if text.lstrip("+-").isdigit():
        parsed = int(text)
    else:
        parsed = _WEEKDAY_BY_NAME.get(text.upper(), default)
    if parsed < 0 or parsed > 6:
        raise RuntimeInstrumentsFactoryError(
            f"weekday must resolve to 0..6, got {value!r}"
        )
    return parsed


def _coerce_scalar(value: str) -> object:
    raw = value.strip().strip('"').strip("'")
    lowered = raw.lower()
    if lowered in {"true", "yes", "on"}:
        return True
    if lowered in {"false", "no", "off"}:
        return False
    if raw.lstrip("+-").isdigit():
        return int(raw)
    return raw


def _load_symbols_yaml_subset(path: Path) -> dict[str, object]:
    """Targeted dependency-light parser for etc/symbols.yaml domain fields."""
    result: dict[str, object] = {
        "exists": path.exists(),
        "path": str(path),
    }
    if not path.exists() or not path.is_file():
        return result

    section: str | None = None
    subsection: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()

        if content.endswith(":"):
            key = content[:-1].strip()
            if indent == 0:
                section = key
                subsection = None
            elif indent == 2 and section is not None:
                subsection = f"{section}.{key}"
            continue

        if ":" not in content:
            continue

        key, value = content.split(":", 1)
        key = key.strip()
        value_obj = _coerce_scalar(value)

        if indent == 2 and section is not None:
            result[f"{section}.{key}"] = value_obj
        elif indent == 4 and subsection is not None:
            result[f"{subsection}.{key}"] = value_obj

    return result


def build_instrument_config_from_symbols_yaml(
    *,
    symbols_path: Path = DEFAULT_SYMBOLS_PATH,
    source_path: Path = CANONICAL_SOURCE_PATH,
    underlying_symbol: str | None = None,
    weekly_expiry_weekday: int | str | None = None,
    monthly_expiry_weekday: int | str | None = None,
) -> InstrumentConfig:
    symbols = _load_symbols_yaml_subset(symbols_path)

    configured_underlying = str(
        underlying_symbol
        or symbols.get("underlying.canonical")
        or DEFAULT_UNDERLYING_SYMBOL
    ).strip().upper()

    future_root = str(
        symbols.get("instrument_family.futures_root")
        or symbols.get("instrument_family.underlying_root")
        or configured_underlying
    ).strip().upper()

    option_root = str(
        symbols.get("instrument_family.options_root")
        or symbols.get("options.root")
        or configured_underlying
    ).strip().upper()

    strike_step = (
        _parse_decimal_text(symbols.get("options.strike_step"))
        if symbols.get("options.strike_step") is not None
        else None
    )

    require_weekly = _parse_bool_text(
        symbols.get("options.expiry_selection.include_weekly"),
        default=True,
    )
    allow_monthly = _parse_bool_text(
        symbols.get("options.expiry_selection.include_monthly"),
        default=True,
    )

    weekly_value = (
        weekly_expiry_weekday
        if weekly_expiry_weekday is not None
        else symbols.get("options.expiry_selection.weekly_expiry_weekday")
    )
    monthly_value = (
        monthly_expiry_weekday
        if monthly_expiry_weekday is not None
        else symbols.get("options.expiry_selection.monthly_expiry_weekday")
    )

    return InstrumentConfig(
        source_path=source_path,
        underlying_symbol=configured_underlying,
        future_root=future_root,
        option_root=option_root,
        require_weekly_options=require_weekly,
        allow_monthly_fallback=allow_monthly,
        weekly_expiry_weekday=_parse_weekday(weekly_value, default=1),
        monthly_expiry_weekday=_parse_weekday(monthly_value, default=1),
        strike_step_override=strike_step,
        freshness_max_age=timedelta(days=7),
        field_map={},
    )


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
    symbols_path: Path = DEFAULT_SYMBOLS_PATH,
    weekly_expiry_weekday: int | str | None = None,
    monthly_expiry_weekday: int | str | None = None,
) -> InstrumentConfig:
    return build_instrument_config_from_symbols_yaml(
        symbols_path=symbols_path,
        source_path=source_path,
        underlying_symbol=underlying_symbol,
        weekly_expiry_weekday=weekly_expiry_weekday,
        monthly_expiry_weekday=monthly_expiry_weekday,
    )


def build_runtime_instruments(
    *,
    quote_key: str = DEFAULT_QUOTE_KEY,
    source_path: Path = CANONICAL_SOURCE_PATH,
    underlying_symbol: str = DEFAULT_UNDERLYING_SYMBOL,
    symbols_path: Path = DEFAULT_SYMBOLS_PATH,
) -> RuntimeInstrumentsBuildResult:
    quote = fetch_underlying_ltp(quote_key)
    config = build_instrument_config(
        source_path=source_path,
        underlying_symbol=underlying_symbol,
        symbols_path=symbols_path,
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
