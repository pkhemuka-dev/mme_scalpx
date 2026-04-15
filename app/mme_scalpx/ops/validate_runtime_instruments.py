"""
app/mme_scalpx/ops/validate_runtime_instruments.py

Freeze-grade validator for domain/instruments.py against the real Zerodha NFO dump.

Purpose
-------
- inspect resolver signature
- construct canonical InstrumentConfig
- invoke resolve_runtime_instruments(...) correctly with keyword arguments
- supply a real underlying_ltp
- print returned runtime instrument contract surface
"""

from __future__ import annotations

import argparse
import inspect
import logging
from dataclasses import fields
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from app.mme_scalpx.domain.instruments import (
    InstrumentConfig,
    RuntimeInstrumentSet,
    resolve_runtime_instruments,
)

CSV_PATH = Path("/home/Lenovo/scalpx/projects/mme_scalpx/data/instruments/nfo_instruments.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate runtime instrument resolution against real NFO CSV"
    )
    parser.add_argument(
        "--underlying-ltp",
        required=True,
        help="Underlying reference LTP, e.g. 22850 or 22850.25",
    )
    return parser.parse_args()


def build_config() -> InstrumentConfig:
    return InstrumentConfig(
        source_path=CSV_PATH,
        field_map={},
    )


def print_dataclass(title: str, obj: object) -> None:
    print(f"=== {title} ===")
    for f in fields(obj):
        print(f"{f.name} = {getattr(obj, f.name)!r}")


def print_contract(title: str, obj: object) -> None:
    print(f"=== {title} ===")
    if hasattr(obj, "__dataclass_fields__"):
        for f in fields(obj):
            print(f"{f.name} = {getattr(obj, f.name)!r}")
    else:
        print(repr(obj))


def main() -> int:
    args = parse_args()

    print("=== CSV PATH ===")
    print(CSV_PATH)
    print("exists =", CSV_PATH.exists())
    print("size_bytes =", CSV_PATH.stat().st_size if CSV_PATH.exists() else 0)

    print("=== RESOLVER SIGNATURE ===")
    print(inspect.signature(resolve_runtime_instruments))

    cfg = build_config()
    print_dataclass("INSTRUMENT CONFIG", cfg)

    underlying_ltp = Decimal(str(args.underlying_ltp))
    print("=== UNDERLYING INPUT ===")
    print("underlying_ltp =", underlying_ltp)

    result = resolve_runtime_instruments(
        config=cfg,
        underlying_ltp=underlying_ltp,
        now=datetime.now(timezone.utc),
        logger=logging.getLogger("validate_runtime_instruments"),
    )

    print("=== RESULT TYPE ===")
    print(type(result))

    if isinstance(result, RuntimeInstrumentSet):
        print("RuntimeInstrumentSet confirmed")

    print_contract("RUNTIME INSTRUMENT SET", result)
    print_contract("CURRENT FUTURE", result.current_future)
    print_contract("CE ATM", result.ce_atm)
    print_contract("CE ATM+1", result.ce_atm1)
    print_contract("PE ATM", result.pe_atm)
    print_contract("PE ATM+1", result.pe_atm1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
