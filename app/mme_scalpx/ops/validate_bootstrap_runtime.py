"""
app/mme_scalpx/ops/validate_bootstrap_runtime.py

Freeze-grade validation command for bootstrap quote + runtime instrument factory.
"""

from __future__ import annotations

from app.mme_scalpx.integrations.runtime_instruments_factory import (
    build_runtime_instruments,
)


def main() -> int:
    built = build_runtime_instruments()

    print("=== BOOTSTRAP QUOTE ===")
    print("instrument_key =", built.quote.instrument_key)
    print("ltp =", built.quote.ltp)

    print("=== CONFIG ===")
    print("source_path =", built.config.source_path_resolved)
    print("underlying_symbol =", built.config.underlying_symbol)
    print("future_root =", built.config.future_root)
    print("option_root =", built.config.option_root)

    runtime = built.runtime_instruments

    print("=== RUNTIME INSTRUMENTS ===")
    print("current_future =", runtime.current_future.tradingsymbol)
    print("ce_atm =", runtime.ce_atm.tradingsymbol, runtime.ce_atm.strike)
    print("ce_atm1 =", runtime.ce_atm1.tradingsymbol, runtime.ce_atm1.strike)
    print("pe_atm =", runtime.pe_atm.tradingsymbol, runtime.pe_atm.strike)
    print("pe_atm1 =", runtime.pe_atm1.tradingsymbol, runtime.pe_atm1.strike)
    print("option_expiry =", runtime.option_expiry)
    print("strike_step =", runtime.strike_step)
    print("selection_version =", runtime.selection_version)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
