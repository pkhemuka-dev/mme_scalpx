#!/usr/bin/env python3
"""Fail-closed Zerodha broker GET-only flat/order/session gate.

This helper performs only provider construction and the adapter's read-only
healthcheck, position reconciliation and open-order reconciliation calls. It
never calls place_entry_order, place_exit_order, place_order, cancel_order or
any Redis write API.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Mapping

from app.mme_scalpx.integrations.bootstrap_provider import provide

TERMINAL = {
    "COMPLETE", "COMPLETED", "CANCELLED", "CANCELED", "REJECTED",
    "EXPIRED", "FILLED", "TRADED",
}


def text(value: Any) -> str:
    return str(value or "").strip()


def number(value: Any) -> float:
    try:
        return float(str(value or "0").strip())
    except Exception:
        return 0.0


def rows_from_positions(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, Mapping)]
    if not isinstance(payload, Mapping):
        return []
    rows: list[Mapping[str, Any]] = []
    for key in ("net", "day", "positions"):
        value = payload.get(key)
        if isinstance(value, list):
            rows.extend(row for row in value if isinstance(row, Mapping))
    if not rows and any(key in payload for key in ("quantity", "net_quantity", "net_qty", "qty")):
        rows.append(payload)
    return rows


def position_quantity(row: Mapping[str, Any]) -> float:
    for key in ("quantity", "net_quantity", "net_qty", "qty", "netPosition", "net_position"):
        if key in row:
            return number(row.get(key))
    buy = number(row.get("buy_quantity") or row.get("buy_qty"))
    sell = number(row.get("sell_quantity") or row.get("sell_qty"))
    return buy - sell


def sanitize_position(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "tradingsymbol": text(row.get("tradingsymbol") or row.get("trading_symbol") or row.get("symbol")),
        "exchange": text(row.get("exchange")),
        "product": text(row.get("product")),
        "quantity": position_quantity(row),
    }


def rows_from_orders(payload: Any) -> list[Mapping[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, Mapping)]
    if isinstance(payload, Mapping):
        value = payload.get("orders")
        if isinstance(value, list):
            return [row for row in value if isinstance(row, Mapping)]
    return []


def active_order(row: Mapping[str, Any]) -> bool:
    status = text(row.get("status") or row.get("order_status")).upper()
    return not status or status not in TERMINAL


def sanitize_order(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "order_id": text(row.get("order_id") or row.get("broker_order_id")),
        "tradingsymbol": text(row.get("tradingsymbol") or row.get("trading_symbol") or row.get("symbol")),
        "status": text(row.get("status") or row.get("order_status")),
        "transaction_type": text(row.get("transaction_type") or row.get("side")),
        "quantity": number(row.get("quantity") or row.get("qty")),
        "pending_quantity": number(row.get("pending_quantity") or row.get("pending_qty")),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--stage", default="audit")
    args = parser.parse_args()

    report: dict[str, Any] = {
        "schema": "lane_x_broker_readonly_flat_gate_v1",
        "stage": args.stage,
        "created_at_ns": time.time_ns(),
        "provider_constructed": False,
        "zerodha_health_ok": False,
        "broker_nonflat_position_count": 999,
        "broker_active_order_count": 999,
        "broker_flat": False,
        "order_method_called": False,
        "cancel_method_called": False,
        "redis_write_attempted": False,
        "dhan_execution_required": False,
        "dhan_execution_fallback_expected_disabled": True,
        "classification": "BLOCK_BROKER_READONLY_GATE_UNSET",
        "error": "",
    }

    try:
        payload = provide()
        report["provider_constructed"] = True
        provider_report = payload.get("provider_bootstrap_report") or {}
        report["provider_bootstrap_report"] = {
            "version": provider_report.get("version"),
            "zerodha_feed_adapter_configured": bool(provider_report.get("zerodha_feed_adapter_configured")),
            "zerodha_broker_configured": bool(provider_report.get("zerodha_broker_configured")),
            "dhan_feed_adapter_configured": bool(provider_report.get("dhan_feed_adapter_configured")),
            "dhan_context_adapter_configured": bool(provider_report.get("dhan_context_adapter_configured")),
            "dhan_context_bootstrap_status": provider_report.get("dhan_context_bootstrap_status"),
            "dhan_execution_fallback_status": provider_report.get("dhan_execution_fallback_status"),
        }

        broker = payload.get("broker")
        if broker is None:
            raise RuntimeError("bootstrap provider returned no Zerodha broker adapter")

        health = broker.healthcheck()
        report["zerodha_health_ok"] = bool(health.get("ok")) if isinstance(health, Mapping) else bool(health)
        report["zerodha_health_type"] = type(health).__name__
        report["zerodha_health_keys"] = sorted(str(key) for key in health.keys())[:40] if isinstance(health, Mapping) else []

        positions_payload = broker.reconcile_position()
        position_rows = rows_from_positions(positions_payload)
        nonflat = [row for row in position_rows if abs(position_quantity(row)) > 0.0]

        orders_payload = broker.reconcile_open_orders()
        order_rows = rows_from_orders(orders_payload)
        active = [row for row in order_rows if active_order(row)]

        report["broker_position_row_count"] = len(position_rows)
        report["broker_nonflat_position_count"] = len(nonflat)
        report["broker_nonflat_positions"] = [sanitize_position(row) for row in nonflat]
        report["broker_order_row_count"] = len(order_rows)
        report["broker_active_order_count"] = len(active)
        report["broker_active_orders"] = [sanitize_order(row) for row in active]
        report["broker_flat"] = bool(
            report["zerodha_health_ok"]
            and len(nonflat) == 0
            and len(active) == 0
        )
        report["classification"] = (
            "PASS_BROKER_READONLY_HEALTH_FLAT_NO_ACTIVE_ORDERS"
            if report["broker_flat"]
            else "BLOCK_BROKER_NONFLAT_OR_ACTIVE_ORDER"
        )
    except Exception as exc:
        report["error"] = f"{exc.__class__.__name__}: {exc}"
        report["classification"] = "BLOCK_BROKER_READONLY_GATE_ERROR"

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    print(f"BROKER_GATE_CLASSIFICATION={report['classification']}")
    print(f"ZERODHA_HEALTH_OK={1 if report['zerodha_health_ok'] else 0}")
    print(f"BROKER_NONFLAT_POSITION_COUNT={report['broker_nonflat_position_count']}")
    print(f"BROKER_ACTIVE_ORDER_COUNT={report['broker_active_order_count']}")
    print(f"BROKER_FLAT={1 if report['broker_flat'] else 0}")
    print("BROKER_ORDER_METHOD_CALLED=0")
    print("BROKER_CANCEL_METHOD_CALLED=0")
    print("REDIS_WRITE_ATTEMPTED=0")
    print(f"BROKER_GATE_REPORT={out}")

    return 0 if report["broker_flat"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
