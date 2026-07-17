#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

import redis


def main() -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--entry-stream-id",
        required=True,
    )
    parser.add_argument(
        "--symbol",
        required=True,
    )
    parser.add_argument(
        "--out",
        required=True,
    )

    args = parser.parse_args()

    client = redis.Redis(
        host="127.0.0.1",
        port=6379,
        decode_responses=True,
    )

    entry_rows = client.xrange(
        "trades:ledger:stream",
        min=args.entry_stream_id,
        max=args.entry_stream_id,
    )

    if len(entry_rows) != 1:
        raise SystemExit(
            "ENTRY_FILL_NOT_FOUND"
        )

    _, entry = entry_rows[0]

    if str(
        entry.get("event_type", "")
    ).upper() != "ENTRY_FILL":
        raise SystemExit(
            "ENTRY_ID_NOT_ENTRY_FILL"
        )

    symbol = args.symbol.upper()
    exit_row = None

    for stream_id, row in client.xrange(
        "trades:ledger:stream",
        min=args.entry_stream_id,
        max="+",
    ):
        if stream_id == args.entry_stream_id:
            continue

        if (
            str(
                row.get("event_type", "")
            ).upper()
            == "EXIT_FILL"
            and str(
                row.get("option_symbol", "")
            ).upper()
            == symbol
        ):
            exit_row = {
                "stream_id": stream_id,
                **row,
            }
            break

    if exit_row is None:
        raise SystemExit(
            "EXIT_FILL_NOT_FOUND"
        )

    entry_price = Decimal(
        str(entry.get("price") or "0")
    )
    exit_price = Decimal(
        str(exit_row.get("price") or "0")
    )
    quantity = Decimal(
        str(
            exit_row.get("quantity")
            or entry.get("quantity")
            or "0"
        )
    )

    calculated_pnl = (
        exit_price - entry_price
    ) * quantity

    ledger_pnl = Decimal(
        str(exit_row.get("pnl") or "0")
    )

    entry_ns = int(
        entry.get("ts_event_ns")
        or entry.get("ts_ns")
        or 0
    )
    exit_ns = int(
        exit_row.get("ts_event_ns")
        or exit_row.get("ts_ns")
        or 0
    )

    hold_seconds = (
        Decimal(exit_ns - entry_ns)
        / Decimal(1_000_000_000)
        if entry_ns and exit_ns
        else None
    )

    result = {
        "classification": (
            "PASS_PAIRED_PAPER_LIFECYCLE"
            if calculated_pnl == ledger_pnl
            else "FAIL_PNL_MISMATCH"
        ),
        "symbol": symbol,
        "quantity_units": int(quantity),
        "entry_price": str(entry_price),
        "exit_price": str(exit_price),
        "premium_points_pnl": str(
            exit_price - entry_price
        ),
        "calculated_gross_rupee_pnl":
            str(calculated_pnl),
        "ledger_pnl": str(ledger_pnl),
        "pnl_matches":
            calculated_pnl == ledger_pnl,
        "hold_seconds": (
            str(hold_seconds)
            if hold_seconds is not None
            else None
        ),
        "fees_and_costs_included": False,
        "entry_fill": {
            "stream_id":
                args.entry_stream_id,
            **entry,
        },
        "exit_fill": exit_row,
        "final_position":
            client.hgetall(
                "state:position:mme"
            ),
    }

    Path(args.out).write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )

    print(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        )
    )

    return (
        0
        if calculated_pnl == ledger_pnl
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
