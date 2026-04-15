"""
app/mme_scalpx/integrations/instrument_master_sync.py

Freeze-grade Zerodha instrument master acquisition for ScalpX MME.

Responsibilities
----------------
- load broker api config and token state
- authenticate Kite client using persisted access token
- fetch NFO instrument master from official Kite instruments API
- validate minimum required schema
- write canonical instrument CSV for domain/instruments.py consumption

Non-responsibilities
--------------------
- no runtime instrument resolution logic
- no ATM / ATM+1 derivation
- no websocket subscription
- no order placement
- no Redis publication
- no fallback guessed schema generation

Design rules
------------
- source of truth for credentials: integrations.token_store
- canonical output path:
  /home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv
- fail fast on missing access token
- fail fast on missing required columns
"""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

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
        "kiteconnect is required by app.mme_scalpx.integrations.instrument_master_sync"
    ) from exc


VERSION = "mme-instrument-master-sync-v1-freeze"
CANONICAL_OUTPUT = Path(
    "/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv"
)

REQUIRED_COLUMNS: tuple[str, ...] = (
    "instrument_token",
    "exchange_token",
    "tradingsymbol",
    "name",
    "last_price",
    "expiry",
    "strike",
    "tick_size",
    "lot_size",
    "instrument_type",
    "segment",
    "exchange",
)

logger = logging.getLogger("scalpx.mme.integrations.instrument_master_sync")


class InstrumentSyncError(RuntimeError):
    """Base error for instrument master sync."""


class StartupValidationError(InstrumentSyncError):
    """Raised for fail-fast validation errors."""


class BrokerAccessError(InstrumentSyncError):
    """Raised when broker access is invalid or unavailable."""


class InstrumentSchemaError(InstrumentSyncError):
    """Raised when fetched instrument rows are malformed."""


@dataclass(frozen=True)
class RuntimeConfig:
    output_path: Path
    exchange: str
    log_level: str


def setup_logging(level: str = "INFO") -> None:
    if logger.handlers:
        return
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(handler)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ScalpX MME Zerodha instrument master sync"
    )
    parser.add_argument(
        "--output",
        default=str(CANONICAL_OUTPUT),
        help="Canonical output CSV path",
    )
    parser.add_argument(
        "--exchange",
        default="NFO",
        help="Exchange segment to fetch from Kite instruments()",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level",
    )
    return parser.parse_args(argv)


def runtime_config_from_args(args: argparse.Namespace) -> RuntimeConfig:
    output_path = Path(args.output)
    exchange = str(args.exchange).strip().upper()
    if not exchange:
        raise StartupValidationError("exchange cannot be empty")
    return RuntimeConfig(
        output_path=output_path,
        exchange=exchange,
        log_level=str(args.log_level),
    )


def validate_api_config_for_zerodha(api: BrokerApiConfig) -> None:
    broker = api.broker.strip().lower()
    if broker != "zerodha":
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


def fetch_instruments(kite: KiteConnect, exchange: str) -> list[dict[str, Any]]:
    try:
        rows = kite.instruments(exchange)
    except Exception as exc:
        raise BrokerAccessError(
            f"kite.instruments({exchange!r}) failed: {exc}"
        ) from exc

    if not isinstance(rows, list):
        raise InstrumentSchemaError("kite.instruments() returned non-list payload")
    if not rows:
        raise InstrumentSchemaError("kite.instruments() returned empty payload")
    return rows


def validate_rows(rows: Sequence[dict[str, Any]]) -> None:
    first = rows[0]
    if not isinstance(first, dict):
        raise InstrumentSchemaError("instrument row 0 is not a dict")

    missing = [col for col in REQUIRED_COLUMNS if col not in first]
    if missing:
        raise InstrumentSchemaError(
            "instrument payload missing required column(s): " + ", ".join(missing)
        )


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=list(REQUIRED_COLUMNS),
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in REQUIRED_COLUMNS})


def summarize(rows: Sequence[dict[str, Any]], output_path: Path, exchange: str) -> None:
    segments = sorted({str(row.get("segment", "")).strip() for row in rows if row.get("segment")})
    instrument_types = sorted(
        {str(row.get("instrument_type", "")).strip() for row in rows if row.get("instrument_type")}
    )
    exchanges = sorted({str(row.get("exchange", "")).strip() for row in rows if row.get("exchange")})

    print("sync_ok = True")
    print("version =", VERSION)
    print("exchange =", exchange)
    print("rows =", len(rows))
    print("output =", str(output_path))
    print("segments =", ",".join(segments[:20]))
    print("instrument_types =", ",".join(instrument_types[:20]))
    print("exchanges =", ",".join(exchanges[:20]))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cfg = runtime_config_from_args(args)
    setup_logging(cfg.log_level)

    try:
        api = load_api_config()
        state = load_token_state()
        validate_api_config_for_zerodha(api)
        validate_token_state_for_zerodha(state)

        kite = build_kite(api, state)
        rows = fetch_instruments(kite, cfg.exchange)
        validate_rows(rows)
        write_csv(cfg.output_path, rows)
        summarize(rows, cfg.output_path, cfg.exchange)
        return 0

    except (
        SecretFileMissingError,
        SecretFileFormatError,
        TokenStoreError,
        StartupValidationError,
        BrokerAccessError,
        InstrumentSchemaError,
    ) as exc:
        logger.error("instrument sync failed: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover
        logger.error("unexpected instrument sync failure: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
