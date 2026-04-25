#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.domain import InstrumentConfig, RuntimeInstrumentSet, resolve_runtime_instruments
from app.mme_scalpx.domain.instruments import (
    IST,
    InstrumentValidationError,
    load_instrument_repository,
)
from app.mme_scalpx.integrations.runtime_instruments_factory import (
    build_instrument_config_from_symbols_yaml,
)


def _write_csv(path: Path, *, include_apr20_future: bool = False, token_field: str = "instrument_token") -> None:
    fieldnames = [
        token_field,
        "tradingsymbol",
        "exchange",
        "segment",
        "underlying",
        "expiry",
        "strike",
        "option_type",
        "tick_size",
        "lot_size",
        "broker",
    ]

    rows: list[dict[str, Any]] = []

    if include_apr20_future:
        rows.append({
            token_field: "FUT_OLD",
            "tradingsymbol": "NIFTY20APRFUT",
            "exchange": "NFO",
            "segment": "NFO-FUT",
            "underlying": "NIFTY",
            "expiry": "2026-04-20",
            "strike": "",
            "option_type": "FUT",
            "tick_size": "0.05",
            "lot_size": "75",
            "broker": "zerodha",
        })

    rows.append({
        token_field: "FUT_NEW",
        "tradingsymbol": "NIFTY28APRFUT",
        "exchange": "NFO",
        "segment": "NFO-FUT",
        "underlying": "NIFTY",
        "expiry": "2026-04-28",
        "strike": "",
        "option_type": "FUT",
        "tick_size": "0.05",
        "lot_size": "75",
        "broker": "zerodha",
    })

    for expiry in ("2026-04-21", "2026-04-23"):
        for side, strikes in (("CE", ("22500", "22550")), ("PE", ("22500", "22450"))):
            for strike in strikes:
                rows.append({
                    token_field: f"{side}_{expiry}_{strike}",
                    "tradingsymbol": f"NIFTY{expiry.replace('-', '')}{strike}{side}",
                    "exchange": "NFO",
                    "segment": "NFO-OPT",
                    "underlying": "NIFTY",
                    "expiry": expiry,
                    "strike": strike,
                    "option_type": side,
                    "tick_size": "0.05",
                    "lot_size": "75",
                    "broker": "zerodha",
                })

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_symbols(path: Path, *, weekly: str = "TUESDAY", monthly: str = "TUESDAY") -> None:
    path.write_text(
        f"""version: 1
underlying:
  canonical: NIFTY
instrument_family:
  underlying_root: NIFTY
  futures_root: NIFTY
  options_root: NIFTY
options:
  root: NIFTY
  strike_step: 50
  expiry_selection:
    include_weekly: true
    include_monthly: true
    weekly_expiry_weekday: {weekly}
    monthly_expiry_weekday: {monthly}
""",
        encoding="utf-8",
    )


def _expect_reject(label: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        return {"case": label, "status": "PASS", "error": str(exc)}
    return {"case": label, "status": "FAIL", "error": "accepted invalid input"}


def _contract_exec_projection(contract: Any, *, role: str) -> dict[str, Any]:
    return {
        "role": role,
        "option_symbol": contract.tradingsymbol,
        "option_token": contract.instrument_token,
        "instrument_key": f"{contract.exchange.value}:{contract.tradingsymbol}",
        "strike": None if contract.strike is None else str(contract.strike),
        "expiry": None if contract.expiry is None else contract.expiry.isoformat(),
        "option_right": None if contract.option_right is None else contract.option_right.value,
        "tick_size": str(contract.tick_size),
        "lot_size": contract.lot_size,
    }


def main() -> int:
    cases: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        csv_path = tmpdir / "instruments.csv"
        symbols_path = tmpdir / "symbols.yaml"
        _write_csv(csv_path)
        _write_symbols(symbols_path)

        config = InstrumentConfig(
            source_path=csv_path,
            underlying_symbol="NIFTY",
            future_root="NIFTY",
            option_root="NIFTY",
            require_weekly_options=True,
            allow_monthly_fallback=True,
            weekly_expiry_weekday=1,
            monthly_expiry_weekday=1,
            strike_step_override=Decimal("50"),
        )
        runtime = resolve_runtime_instruments(
            config=config,
            underlying_ltp=Decimal("22510"),
            now=datetime(2026, 4, 20, 10, 0, tzinfo=IST),
        )
        cases.append({
            "case": "tuesday_expiry_selected_over_thursday",
            "status": "PASS" if runtime.option_expiry.isoformat() == "2026-04-21" else "FAIL",
            "option_expiry": runtime.option_expiry.isoformat(),
        })

        thursday_config = InstrumentConfig(
            source_path=csv_path,
            underlying_symbol="NIFTY",
            future_root="NIFTY",
            option_root="NIFTY",
            require_weekly_options=True,
            allow_monthly_fallback=True,
            weekly_expiry_weekday=3,
            monthly_expiry_weekday=3,
            strike_step_override=Decimal("50"),
        )
        thursday_runtime = resolve_runtime_instruments(
            config=thursday_config,
            underlying_ltp=Decimal("22510"),
            now=datetime(2026, 4, 20, 10, 0, tzinfo=IST),
        )
        cases.append({
            "case": "expiry_weekday_is_configurable_for_future_rule_changes",
            "status": "PASS" if thursday_runtime.option_expiry.isoformat() == "2026-04-23" else "FAIL",
            "option_expiry": thursday_runtime.option_expiry.isoformat(),
        })

        csv_ist_path = tmpdir / "instruments_ist.csv"
        _write_csv(csv_ist_path, include_apr20_future=True)
        ist_config = InstrumentConfig(
            source_path=csv_ist_path,
            underlying_symbol="NIFTY",
            future_root="NIFTY",
            option_root="NIFTY",
            require_weekly_options=True,
            allow_monthly_fallback=True,
            weekly_expiry_weekday=1,
            monthly_expiry_weekday=1,
            strike_step_override=Decimal("50"),
        )
        repo = load_instrument_repository(config=ist_config, now=datetime.now(tz=timezone.utc))
        future = repo.get_current_future(now=datetime(2026, 4, 20, 20, 0, tzinfo=timezone.utc))
        cases.append({
            "case": "current_future_uses_ist_exchange_date",
            "status": "PASS" if future.expiry.isoformat() == "2026-04-28" else "FAIL",
            "selected_future_expiry": future.expiry.isoformat(),
        })

        csv_dhan_path = tmpdir / "instruments_dhan.csv"
        _write_csv(csv_dhan_path, token_field="security_id")
        dhan_config = InstrumentConfig(
            source_path=csv_dhan_path,
            underlying_symbol="NIFTY",
            future_root="NIFTY",
            option_root="NIFTY",
            require_weekly_options=True,
            allow_monthly_fallback=True,
            weekly_expiry_weekday=1,
            monthly_expiry_weekday=1,
            strike_step_override=Decimal("50"),
        )
        dhan_runtime = resolve_runtime_instruments(
            config=dhan_config,
            underlying_ltp=Decimal("22510"),
            now=datetime(2026, 4, 20, 10, 0, tzinfo=IST),
        )
        cases.append({
            "case": "dhan_security_id_alias_normalizes_as_token",
            "status": "PASS" if dhan_runtime.ce_atm.instrument_token.startswith("CE_") else "FAIL",
            "ce_atm_token": dhan_runtime.ce_atm.instrument_token,
        })

        parsed_config = build_instrument_config_from_symbols_yaml(
            symbols_path=symbols_path,
            source_path=csv_path,
        )
        cases.append({
            "case": "runtime_factory_consumes_symbols_yaml_policy",
            "status": "PASS"
            if parsed_config.weekly_expiry_weekday == 1
            and parsed_config.monthly_expiry_weekday == 1
            and parsed_config.strike_step_override == Decimal("50")
            else "FAIL",
            "weekly_expiry_weekday": parsed_config.weekly_expiry_weekday,
            "monthly_expiry_weekday": parsed_config.monthly_expiry_weekday,
            "strike_step_override": str(parsed_config.strike_step_override),
        })

        cases.append({
            "case": "runtime_instrument_set_has_execution_projection_fields",
            "status": "PASS"
            if all(
                _contract_exec_projection(contract, role=role)["option_token"]
                for role, contract in (
                    ("CE_ATM", runtime.ce_atm),
                    ("CE_ATM1", runtime.ce_atm1),
                    ("PE_ATM", runtime.pe_atm),
                    ("PE_ATM1", runtime.pe_atm1),
                )
            )
            else "FAIL",
            "projection": [
                _contract_exec_projection(runtime.ce_atm, role="CE_ATM"),
                _contract_exec_projection(runtime.ce_atm1, role="CE_ATM1"),
                _contract_exec_projection(runtime.pe_atm, role="PE_ATM"),
                _contract_exec_projection(runtime.pe_atm1, role="PE_ATM1"),
            ],
        })

        cases.append(
            _expect_reject(
                "invalid_weekday_rejected",
                lambda: InstrumentConfig(
                    source_path=csv_path,
                    weekly_expiry_weekday=9,
                    monthly_expiry_weekday=1,
                ),
            )
        )

    # Domain package exports.
    import app.mme_scalpx.domain as domain

    required_exports = (
        "InstrumentConfig",
        "RuntimeInstrumentSet",
        "resolve_runtime_instruments",
        "load_instrument_repository",
    )
    missing_exports = [name for name in required_exports if not hasattr(domain, name)]
    cases.append({
        "case": "domain_package_exports_required_surfaces",
        "status": "PASS" if not missing_exports else "FAIL",
        "missing_exports": missing_exports,
    })

    failed = [case for case in cases if case["status"] != "PASS"]
    proof = {
        "proof": "domain_instruments_batch6_freeze",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out = PROJECT_ROOT / "run" / "proofs" / "domain_instruments_batch6_freeze.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
