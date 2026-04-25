#!/usr/bin/env python3
from __future__ import annotations

"""Validate runtime instrument source/config without owning runtime services."""

import argparse
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.domain.instruments import (
    IST,
    load_instrument_repository,
)
from app.mme_scalpx.integrations.runtime_instruments_factory import (
    CANONICAL_SOURCE_PATH,
    DEFAULT_SYMBOLS_PATH,
    build_instrument_config,
)


def _contract_summary(contract: Any) -> dict[str, Any]:
    return {
        "tradingsymbol": contract.tradingsymbol,
        "instrument_token": contract.instrument_token,
        "exchange": contract.exchange.value,
        "segment": contract.segment,
        "kind": contract.kind.value,
        "expiry": contract.expiry.isoformat() if contract.expiry else None,
        "strike": str(contract.strike) if contract.strike is not None else None,
        "option_right": contract.option_right.value if contract.option_right else None,
        "tick_size": str(contract.tick_size),
        "lot_size": contract.lot_size,
        "broker": contract.broker,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-path", type=Path, default=CANONICAL_SOURCE_PATH)
    parser.add_argument("--symbols-path", type=Path, default=DEFAULT_SYMBOLS_PATH)
    parser.add_argument("--underlying", default="NIFTY")
    parser.add_argument("--underlying-ltp", default="")
    parser.add_argument("--now-iso", default="")
    args = parser.parse_args()

    now = (
        datetime.fromisoformat(args.now_iso)
        if args.now_iso.strip()
        else datetime.now(tz=timezone.utc)
    )
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    config = build_instrument_config(
        source_path=args.source_path,
        symbols_path=args.symbols_path,
        underlying_symbol=args.underlying,
    )

    source_path = config.source_path_resolved
    stat = source_path.stat() if source_path.exists() else None

    report: dict[str, Any] = {
        "proof": "validate_runtime_instruments",
        "source_path": str(source_path),
        "source_exists": source_path.exists(),
        "source_size_bytes": None if stat is None else stat.st_size,
        "source_modified_at_utc": None
        if stat is None
        else datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "symbols_path": str(args.symbols_path),
        "symbols_exists": args.symbols_path.exists(),
        "config": {
            "underlying_symbol": config.underlying_symbol,
            "future_root": config.future_root,
            "option_root": config.option_root,
            "require_weekly_options": config.require_weekly_options,
            "allow_monthly_fallback": config.allow_monthly_fallback,
            "weekly_expiry_weekday": config.weekly_expiry_weekday,
            "monthly_expiry_weekday": config.monthly_expiry_weekday,
            "strike_step_override": None
            if config.strike_step_override is None
            else str(config.strike_step_override),
            "option_expiry_days_guard": config.option_expiry_days_guard,
        },
        "resolved": None,
    }

    if args.underlying_ltp.strip():
        repo = load_instrument_repository(config=config, now=now)
        runtime = repo.build_runtime_set(
            underlying_ltp=Decimal(args.underlying_ltp),
            now=now,
        )
        report["resolved"] = {
            "exchange_date_ist": now.astimezone(IST).date().isoformat(),
            "option_expiry": runtime.option_expiry.isoformat(),
            "strike_step": str(runtime.strike_step),
            "underlying_reference": str(runtime.underlying_reference),
            "current_future": _contract_summary(runtime.current_future),
            "ce_atm": _contract_summary(runtime.ce_atm),
            "ce_atm1": _contract_summary(runtime.ce_atm1),
            "pe_atm": _contract_summary(runtime.pe_atm),
            "pe_atm1": _contract_summary(runtime.pe_atm1),
        }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
