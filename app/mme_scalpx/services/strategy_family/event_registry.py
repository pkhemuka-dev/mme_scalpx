from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/event_registry.py

Pure consumed-event registry helpers for strategy-family doctrine leaves.

Ownership
---------
This module does not own Redis, persistence, orders, fills, cooldowns, or broker
truth. It only defines deterministic event-registry payload handling that
strategy leaves can consume to block same-event retry when the strategy service
or proof harness supplies consumed event state.

Freeze law
----------
- A trap_event_id is consumed when an external strategy/execution lifecycle
  records it as sent, filled, canceled, timed out, rejected, or flattened.
- This helper never mutates external state. mark_* returns a new payload.
"""

from typing import Any, Final, Mapping, Sequence

CONSUMED_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "ORDER_SENT",
        "SENT",
        "FILLED",
        "PARTIAL_FILL",
        "CANCELED",
        "CANCELLED",
        "TIMEOUT",
        "TIMED_OUT",
        "REJECTED",
        "FAILED",
        "FLATTENED",
        "CONSUMED",
    }
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _nested(root: Any, *path: str, default: Any = None) -> Any:
    cur = root
    for key in path:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def _iter_ids(value: Any) -> set[str]:
    out: set[str] = set()

    if value is None:
        return out

    if isinstance(value, str):
        for part in value.replace(",", " ").split():
            text = part.strip()
            if text:
                out.add(text)
        return out

    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = _safe_str(key)
            if not key_text:
                continue

            if isinstance(item, Mapping):
                status = _safe_str(item.get("status")).upper()
                consumed = item.get("consumed")
                if consumed is True or status in CONSUMED_STATUSES:
                    out.add(key_text)
            elif item is True:
                out.add(key_text)
            elif _safe_str(item).upper() in CONSUMED_STATUSES:
                out.add(key_text)
        return out

    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            if isinstance(item, Mapping):
                event_id = _safe_str(
                    item.get("trap_event_id")
                    or item.get("event_id")
                    or item.get("id")
                )
                status = _safe_str(item.get("status")).upper()
                consumed = item.get("consumed")
                if event_id and (consumed is True or status in CONSUMED_STATUSES or not status):
                    out.add(event_id)
            else:
                text = _safe_str(item)
                if text:
                    out.add(text)
        return out

    return out


def consumed_event_ids(view: Mapping[str, Any], *, family_id: str = "MISR") -> set[str]:
    """Collect consumed trap_event_id values from known strategy-view surfaces."""
    family = str(family_id).strip().upper() or "MISR"
    sources = (
        _nested(view, "common", "consumed_trap_event_ids", default=None),
        _nested(view, "common", "misr_consumed_event_ids", default=None),
        _nested(view, "common", "event_registry", family, default=None),
        _nested(view, "family_status", family, "consumed_trap_event_ids", default=None),
        _nested(view, "family_status", family, "consumed_event_ids", default=None),
        _nested(view, "family_surfaces", "families", family, "consumed_trap_event_ids", default=None),
        _nested(view, "family_surfaces", "families", family, "event_registry", default=None),
        _nested(view, "strategy_state", family, "consumed_trap_event_ids", default=None),
        _nested(view, "strategy_state", family, "event_registry", default=None),
    )

    out: set[str] = set()
    for source in sources:
        out.update(_iter_ids(source))
    return out


def is_trap_event_consumed(
    view: Mapping[str, Any],
    *,
    trap_event_id: str,
    family_id: str = "MISR",
) -> bool:
    event_id = _safe_str(trap_event_id)
    if not event_id:
        return False
    return event_id in consumed_event_ids(view, family_id=family_id)


def mark_trap_event_consumed(
    registry: Mapping[str, Any] | None,
    *,
    trap_event_id: str,
    status: str,
    ts_ms: int | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """Return a new registry payload with trap_event_id marked consumed."""
    event_id = _safe_str(trap_event_id)
    if not event_id:
        raise ValueError("trap_event_id is required")

    status_text = _safe_str(status, "CONSUMED").upper()
    payload = dict(_as_mapping(registry))
    payload[event_id] = {
        "trap_event_id": event_id,
        "status": status_text,
        "consumed": status_text in CONSUMED_STATUSES or status_text == "CONSUMED",
        "ts_ms": ts_ms,
        "reason": reason or "",
    }
    return payload


__all__ = [
    "CONSUMED_STATUSES",
    "consumed_event_ids",
    "is_trap_event_consumed",
    "mark_trap_event_consumed",
]
