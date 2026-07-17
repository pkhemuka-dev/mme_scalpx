#!/usr/bin/env python3
"""Broker GET-only preflight probe.

Fail-closed. No order-writing method is ever called.

Allowed only when:
  SCALPX_ALLOW_BROKER_GET_ONLY=1

The probe recursively searches the bootstrap provider output for an object that
has GET-style broker methods such as profile(), margins(), positions(), orders().
It captures noisy bootstrap stdout/stderr so the script always emits clean JSON.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
from dataclasses import asdict, dataclass
from typing import Any


FORBIDDEN_METHODS = {
    "place_order",
    "modify_order",
    "cancel_order",
    "submit_order",
    "send_order",
    "exit_order",
}

READ_METHODS = {
    "profile",
    "margins",
    "positions",
    "orders",
    "holdings",
    "order_margins",
    "basket_margins",
}


SENSITIVE_WORDS = (
    "token",
    "secret",
    "password",
    "apikey",
    "api_key",
    "access",
    "refresh",
    "jwt",
    "auth",
    "email",
    "user_id",
    "user_name",
    "user_shortname",
    "phone",
    "mobile",
)


@dataclass(frozen=True)
class BrokerGetOnlyResult:
    decision: str
    blockers: tuple[str, ...]
    profile_ok: bool
    margins_ok: bool
    positions_flat: bool
    active_orders_zero: bool
    raw: dict[str, Any]

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        record.update(
            {
                "can_create_order": False,
                "can_route_order": False,
                "can_modify_order": False,
                "can_cancel_order": False,
                "can_send_broker_order": False,
            }
        )
        return record


def _safe_repr(value: Any, max_len: int = 500) -> str:
    try:
        text = repr(value)
    except Exception:
        text = f"<unreprable {type(value).__name__}>"
    return text[:max_len]


def _redact_key(key: str, value: Any) -> Any:
    lowered = str(key).lower()
    if any(word in lowered for word in SENSITIVE_WORDS):
        return "***REDACTED***"
    return value


def _sanitize(value: Any, depth: int = 0) -> Any:
    if depth > 5:
        return f"<max_depth {type(value).__name__}>"

    if isinstance(value, dict):
        out = {}
        for key, child in list(value.items())[:80]:
            out[str(key)] = _sanitize(_redact_key(str(key), child), depth + 1)
        return out

    if isinstance(value, (list, tuple)):
        return [_sanitize(x, depth + 1) for x in list(value)[:80]]

    if isinstance(value, (str, int, float, bool)) or value is None:
        if isinstance(value, str) and len(value) > 500:
            return value[:500] + "...<truncated>"
        return value

    return {
        "_type": type(value).__name__,
        "_module": getattr(type(value), "__module__", ""),
        "_repr": _safe_repr(value, 300),
    }


def _has_read_method(obj: Any) -> bool:
    for name in READ_METHODS:
        try:
            if callable(getattr(obj, name, None)):
                return True
        except Exception:
            continue
    return False


def _method_presence(obj: Any) -> dict[str, bool]:
    out = {}
    for name in sorted(READ_METHODS | FORBIDDEN_METHODS):
        try:
            out[name] = callable(getattr(obj, name, None))
        except Exception:
            out[name] = False
    return out


def _walk_clients(obj: Any, path: str = "provider", depth: int = 0, seen: set[int] | None = None):
    if seen is None:
        seen = set()

    if depth > 8:
        return

    ident = id(obj)
    if ident in seen:
        return
    seen.add(ident)

    if _has_read_method(obj):
        yield path, obj

    if isinstance(obj, dict):
        for key, child in list(obj.items())[:120]:
            yield from _walk_clients(child, f"{path}.{key}", depth + 1, seen)

    elif isinstance(obj, (list, tuple)):
        for index, child in enumerate(list(obj)[:120]):
            yield from _walk_clients(child, f"{path}[{index}]", depth + 1, seen)

    else:
        for name in (
            "transport_client",
            "kite",
            "kite_client",
            "client",
            "broker",
            "zerodha",
            "zerodha_client",
            "execution_client",
            "marketdata_client",
            "order_client",
            "api",
            "_transport_client",
            "_client",
            "_kite",
        ):
            try:
                child = getattr(obj, name, None)
            except Exception:
                child = None

            if child is not None:
                yield from _walk_clients(child, f"{path}.{name}", depth + 1, seen)


def _safe_call(client: Any, method_name: str) -> tuple[bool, Any]:
    if method_name in FORBIDDEN_METHODS:
        return False, {"error": "FORBIDDEN_METHOD"}

    method = getattr(client, method_name, None)

    if not callable(method):
        return False, {"error": "METHOD_NOT_FOUND"}

    try:
        return True, method()
    except Exception as exc:
        return False, {"error": type(exc).__name__, "message": str(exc)[:500]}


def _positions_flat(positions: Any) -> bool:
    if isinstance(positions, dict):
        rows = []

        for bucket in ("net", "day"):
            val = positions.get(bucket)
            if isinstance(val, list):
                rows.extend(val)

        if not rows and isinstance(positions.get("data"), list):
            rows.extend(positions["data"])

        for row in rows:
            if not isinstance(row, dict):
                continue

            qty = row.get("quantity", row.get("net_quantity", row.get("qty", 0)))

            try:
                if float(qty) != 0.0:
                    return False
            except Exception:
                return False

        return True

    if isinstance(positions, list):
        for row in positions:
            if not isinstance(row, dict):
                continue
            qty = row.get("quantity", row.get("net_quantity", row.get("qty", 0)))
            try:
                if float(qty) != 0.0:
                    return False
            except Exception:
                return False
        return True

    return False


def _orders_active_zero(orders: Any) -> bool:
    open_statuses = {
        "OPEN",
        "TRIGGER PENDING",
        "VALIDATION PENDING",
        "PUT ORDER REQ RECEIVED",
        "MODIFY VALIDATION PENDING",
        "AMO REQ RECEIVED",
        "OPEN PENDING",
    }

    rows = []

    if isinstance(orders, list):
        rows = orders
    elif isinstance(orders, dict):
        if isinstance(orders.get("data"), list):
            rows = orders["data"]
        elif isinstance(orders.get("orders"), list):
            rows = orders["orders"]

    for row in rows:
        if not isinstance(row, dict):
            continue

        status = str(row.get("status", "")).upper()

        if status in open_statuses:
            return False

    return True


def _margins_ok(margins: Any) -> bool:
    if not margins:
        return False

    if isinstance(margins, dict):
        text = json.dumps(_sanitize(margins), sort_keys=True).lower()
        if "error" in text and "available" not in text:
            return False
        return True

    return True


def run_probe() -> BrokerGetOnlyResult:
    if os.environ.get("SCALPX_ALLOW_BROKER_GET_ONLY") != "1":
        return BrokerGetOnlyResult(
            decision="BLOCK",
            blockers=("ENV_FLAG_SCALPX_ALLOW_BROKER_GET_ONLY_NOT_SET",),
            profile_ok=False,
            margins_ok=False,
            positions_flat=False,
            active_orders_zero=False,
            raw={},
        )

    blockers: list[str] = []
    raw: dict[str, Any] = {}

    try:
        from app.mme_scalpx.integrations.bootstrap_provider import provide

        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()

        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(captured_stderr):
            provided = provide()

        raw["bootstrap_stdout"] = captured_stdout.getvalue()[-2000:]
        raw["bootstrap_stderr"] = captured_stderr.getvalue()[-2000:]
        raw["provider_type"] = type(provided).__name__
        raw["provider_sanitized"] = _sanitize(provided, 0)

    except Exception as exc:
        blockers.append("BOOTSTRAP_PROVIDER_IMPORT_OR_PROVIDE_FAILED")
        raw["bootstrap_error"] = {
            "type": type(exc).__name__,
            "message": str(exc)[:500],
        }
        provided = None

    discovered = list(_walk_clients(provided)) if provided is not None else []

    # De-duplicate by object id while retaining the first path.
    seen = set()
    clients: list[tuple[str, Any]] = []

    for path, client in discovered:
        ident = id(client)
        if ident not in seen:
            seen.add(ident)
            clients.append((path, client))

    raw["client_count"] = len(clients)
    raw["client_paths"] = [path for path, _ in clients]
    raw["client_types"] = [type(client).__name__ for _, client in clients]

    profile_ok = False
    margins_ok = False
    positions_flat = False
    active_orders_zero = False

    if not clients:
        blockers.append("NO_BROKER_CLIENT_WITH_GET_METHODS_FOUND")

    for index, (path, client) in enumerate(clients):
        client_key = f"client_{index}_{type(client).__name__}"
        raw[client_key] = {
            "path": path,
            "type": type(client).__name__,
            "module": getattr(type(client), "__module__", ""),
            "method_presence": _method_presence(client),
        }

        ok, profile = _safe_call(client, "profile")
        raw[client_key]["profile"] = _sanitize(profile)
        profile_ok = profile_ok or ok

        ok, margins = _safe_call(client, "margins")
        raw[client_key]["margins"] = _sanitize(margins)
        margins_ok = margins_ok or (ok and _margins_ok(margins))

        ok, positions = _safe_call(client, "positions")
        raw[client_key]["positions"] = _sanitize(positions)
        positions_flat = positions_flat or (ok and _positions_flat(positions))

        ok, orders = _safe_call(client, "orders")
        raw[client_key]["orders"] = _sanitize(orders)
        active_orders_zero = active_orders_zero or (ok and _orders_active_zero(orders))

    if not profile_ok:
        blockers.append("PROFILE_GET_FAILED")
    if not margins_ok:
        blockers.append("MARGINS_GET_FAILED")
    if not positions_flat:
        blockers.append("POSITIONS_NOT_PROVEN_FLAT")
    if not active_orders_zero:
        blockers.append("ACTIVE_ORDERS_NOT_PROVEN_ZERO")

    return BrokerGetOnlyResult(
        decision="PASS" if not blockers else "BLOCK",
        blockers=tuple(dict.fromkeys(blockers)),
        profile_ok=profile_ok,
        margins_ok=margins_ok,
        positions_flat=positions_flat,
        active_orders_zero=active_orders_zero,
        raw=raw,
    )


def main() -> int:
    result = run_probe()
    print(json.dumps(result.to_record(), indent=2, sort_keys=True))
    return 0 if result.decision == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
