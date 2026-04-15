"""
app/mme_scalpx/ops/validate_bootstrap_provider.py

Freeze-grade validation for bootstrap_provider.py.
"""

from __future__ import annotations

from app.mme_scalpx.integrations.bootstrap_provider import (
    build_bootstrap_result,
    provide,
)


def main() -> int:
    result = build_bootstrap_result()

    print("=== PROVIDER RESULT ===")
    print("version =", result.version)
    print("quote_key =", result.runtime_build.quote.instrument_key)
    print("quote_ltp =", result.runtime_build.quote.ltp)

    runtime = result.runtime_build.runtime_instruments
    print("future =", runtime.current_future.tradingsymbol)
    print("ce_atm =", runtime.ce_atm.tradingsymbol, runtime.ce_atm.strike)
    print("ce_atm1 =", runtime.ce_atm1.tradingsymbol, runtime.ce_atm1.strike)
    print("pe_atm =", runtime.pe_atm.tradingsymbol, runtime.pe_atm.strike)
    print("pe_atm1 =", runtime.pe_atm1.tradingsymbol, runtime.pe_atm1.strike)

    payload = provide()
    print("=== PROVIDER PAYLOAD ===")
    print("keys =", sorted(payload.keys()))
    print("bootstrap_quote =", payload["bootstrap_quote"])
    print("runtime_instruments_type =", type(payload["runtime_instruments"]).__name__)
    print("instrument_set_same_object =", payload["runtime_instruments"] is payload["instrument_set"])
    print("future_alias =", payload["runtime_instruments"].current_future.tradingsymbol)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
