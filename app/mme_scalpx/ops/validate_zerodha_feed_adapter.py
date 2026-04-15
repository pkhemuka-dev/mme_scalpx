"""
app/mme_scalpx/ops/validate_zerodha_feed_adapter.py

Freeze-grade standalone validation for the real Zerodha feed adapter.
"""

from __future__ import annotations

import argparse
import time

from app.mme_scalpx.integrations.runtime_instruments_factory import build_runtime_instruments
from app.mme_scalpx.integrations.zerodha_feed_adapter import ZerodhaFeedAdapter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate real Zerodha websocket feed adapter"
    )
    parser.add_argument("--wait-seconds", type=float, default=10.0)
    parser.add_argument("--poll-timeout", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    built = build_runtime_instruments()
    runtime = built.runtime_instruments

    print("=== BOOTSTRAP ===")
    print("quote_key =", built.quote.instrument_key)
    print("quote_ltp =", built.quote.ltp)
    print("future =", runtime.current_future.tradingsymbol)
    print("ce_atm =", runtime.ce_atm.tradingsymbol)
    print("ce_atm1 =", runtime.ce_atm1.tradingsymbol)
    print("pe_atm =", runtime.pe_atm.tradingsymbol)
    print("pe_atm1 =", runtime.pe_atm1.tradingsymbol)

    adapter = ZerodhaFeedAdapter(runtime_instruments=runtime)

    print("=== CONNECT ===")
    adapter.connect()
    print("connected =", adapter.is_connected())
    print("subscribed_tokens =", adapter.subscribed_tokens)

    deadline = time.time() + args.wait_seconds
    bundle = None

    while time.time() < deadline:
        bundle = adapter.poll(timeout=args.poll_timeout)
        if bundle is not None and bundle.tick_count > 0:
            break

    print("=== POLL RESULT ===")
    if bundle is None:
        print("bundle = None")
        print("last_error =", adapter.last_error)
        adapter.close()
        return 1

    payload = bundle.to_dict()
    print("received_at_utc =", payload["received_at_utc"])
    print("connected =", payload["connected"])
    print("tick_count =", payload["tick_count"])
    print("families =", sorted(payload["by_family"].keys()))

    for family in sorted(payload["by_family"].keys()):
        tick = payload["by_family"][family]
        print(
            family,
            "tradingsymbol=",
            tick["tradingsymbol"],
            "mode=",
            tick["mode"],
            "last_price=",
            tick["last_price"],
            "exchange_timestamp=",
            tick["exchange_timestamp"],
        )

    adapter.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
