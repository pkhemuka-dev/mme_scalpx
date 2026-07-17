"""R29B selector-state shadow evidence helper.

Pure shadow helper for decision-stream observability.
No broker calls. No order calls. No Redis writes by this module except field enrichment
on an already-attempted decisions:mme:stream XADD made by strategy.py.
"""
from __future__ import annotations

import json
import re
import time
from collections import deque
from collections.abc import MutableMapping
from typing import Any

R29B_SELECTOR_STATE_SHADOW_HELPER = True
POLICY_VERSION = "R29B_SELECTOR_STABILITY_V1"

_ALLOWED_FAMILIES = {"MIST", "MISB"}
_ALLOWED_ACTION_INITIAL = "ENTER_PUT"
_MIN_PERSISTENCE_SEC = 10.0
_MIN_SAMPLES = 3
_MAX_SWITCHES_60S = 6
_COOLDOWN_AFTER_SWITCH_SEC = 20.0
_SYMBOL_RE = re.compile(r"\bNIFTY[A-Z0-9]+(?:CE|PE)\b", re.I)

def new_selector_state() -> dict[str, Any]:
    return {
        "key": None,
        "since": None,
        "samples": 0,
        "switch_times": deque(maxlen=512),
        "last_switch_at": None,
    }

_GLOBAL_STATE = new_selector_state()

def _to_text(v: Any) -> str:
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    return str(v)

def _parse_json_maybe(v: Any) -> Any:
    if not isinstance(v, str):
        return v
    s = v.strip()
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            return v
    return v

def _flatten(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    obj = _parse_json_maybe(obj)
    if isinstance(obj, MutableMapping):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            out.append((p, v))
            out.extend(_flatten(v, p))
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            out.extend(_flatten(x, f"{prefix}[{i}]"))
    return out

def _get_any(flat: list[tuple[str, Any]], names: list[str]) -> Any:
    names_l = {n.lower() for n in names}
    for p, v in flat:
        base = p.lower().split(".")[-1]
        if base in names_l and v is not None and _to_text(v) != "":
            return v
    return None

def _extract_symbol(flat: list[tuple[str, Any]], blob: str) -> str | None:
    for name in ["candidate_symbol_shadow", "r38ee_extracted_symbol", "symbol", "option_symbol", "tradingsymbol", "instrument_key"]:
        v = _get_any(flat, [name])
        if v:
            m = _SYMBOL_RE.search(_to_text(v))
            if m:
                return m.group(0).upper()
    m = _SYMBOL_RE.search(blob)
    return m.group(0).upper() if m else None

def _extract_selector(fields: MutableMapping[str, Any]) -> dict[str, str | None]:
    flat = _flatten(dict(fields))
    blob = json.dumps(dict(fields), sort_keys=True, default=str)

    family = None
    for name in ["activation_selected_family_id", "candidate_family_id_shadow", "r38fe_decision_family_evidence", "r38ee_extracted_family", "strategy_family_id", "family"]:
        v = _get_any(flat, [name])
        if v:
            vv = _to_text(v).upper()
            if vv in _ALLOWED_FAMILIES:
                family = vv
                break

    action = None
    for name in ["activation_selected_action", "candidate_action_shadow", "r38fe_decision_action_evidence", "r38ee_extracted_action", "action"]:
        v = _get_any(flat, [name])
        if v:
            vv = _to_text(v).upper()
            if vv in {"ENTER_PUT", "ENTER_CALL"}:
                action = vv
                break

    symbol = _extract_symbol(flat, blob)

    token = None
    for name in ["candidate_instrument_token_shadow", "r38ee_extracted_token", "instrument_token", "token"]:
        v = _get_any(flat, [name])
        if v and _to_text(v).isdigit():
            token = _to_text(v)
            break

    return {"family": family, "action": action, "symbol": symbol, "token": token}

def _prune_switches(state: dict[str, Any], now: float) -> int:
    q = state.setdefault("switch_times", deque(maxlen=512))
    while q and q[0] < now - 60.0:
        q.popleft()
    return len(q)

def build_selector_state_shadow_fields(
    fields: MutableMapping[str, Any],
    *,
    state: dict[str, Any] | None = None,
    now: float | None = None,
) -> dict[str, str]:
    state = state if state is not None else _GLOBAL_STATE
    now = float(now if now is not None else time.time())

    selector = _extract_selector(fields)
    family = selector.get("family") or ""
    action = selector.get("action") or ""
    symbol = selector.get("symbol") or ""
    token = selector.get("token") or ""
    key = f"{family}|{action}|{symbol}|{token}"

    previous_key = state.get("key")
    if key != previous_key:
        if previous_key is not None:
            state.setdefault("switch_times", deque(maxlen=512)).append(now)
            state["last_switch_at"] = now
        state["key"] = key
        state["since"] = now
        state["samples"] = 1
    else:
        state["samples"] = int(state.get("samples") or 0) + 1

    since = float(state.get("since") if state.get("since") is not None else now)
    stable_for = max(0.0, now - since)
    samples = int(state.get("samples") or 0)
    switch_count_60s = _prune_switches(state, now)

    last_switch = state.get("last_switch_at")
    cooldown_active = bool(last_switch is not None and (now - float(last_switch)) < _COOLDOWN_AFTER_SWITCH_SEC)

    missing = [k for k, v in selector.items() if not v]
    block_reasons: list[str] = []
    if missing:
        block_reasons.append("missing_" + "_".join(missing))
    if action != _ALLOWED_ACTION_INITIAL:
        block_reasons.append("action_not_ENTER_PUT")
    if stable_for < _MIN_PERSISTENCE_SEC:
        block_reasons.append("selector_not_stable_10s")
    if samples < _MIN_SAMPLES:
        block_reasons.append("selector_samples_lt_3")
    if switch_count_60s > _MAX_SWITCHES_60S:
        block_reasons.append("selector_switch_count_gt_6_per_60s")
    if cooldown_active:
        block_reasons.append("selector_cooldown_active")

    entry_allowed = not block_reasons

    return {
        "selector_key_shadow": key,
        "selector_family_shadow": family,
        "selector_action_shadow": action,
        "selector_symbol_shadow": symbol,
        "selector_token_shadow": token,
        "selector_stable_for_sec_shadow": f"{stable_for:.3f}",
        "selector_sample_count_shadow": str(samples),
        "selector_switch_count_60s_shadow": str(switch_count_60s),
        "selector_cooldown_active_shadow": "true" if cooldown_active else "false",
        "entry_allowed_shadow": "true" if entry_allowed else "false",
        "entry_block_reason_shadow": "NONE" if entry_allowed else "|".join(block_reasons),
        "entry_policy_version_shadow": POLICY_VERSION,
    }

def apply_selector_state_shadow_fields(
    fields: MutableMapping[str, Any],
    *,
    state: dict[str, Any] | None = None,
    now: float | None = None,
) -> MutableMapping[str, Any]:
    shadow = build_selector_state_shadow_fields(fields, state=state, now=now)
    for k, v in shadow.items():
        fields.setdefault(k, v)
    return fields

def patch_redis_xadd_for_selector_shadow() -> bool:
    try:
        import redis
    except Exception:
        return False

    Redis = redis.Redis
    current = getattr(Redis, "xadd", None)
    if getattr(current, "_r29b_selector_shadow_patched", False):
        return True

    original_xadd = current

    def xadd_with_selector_shadow(self, name, fields, *args, **kwargs):
        try:
            stream_name = name.decode("utf-8", errors="replace") if isinstance(name, bytes) else str(name)
            if stream_name == "decisions:mme:stream" and isinstance(fields, MutableMapping):
                apply_selector_state_shadow_fields(fields)
        except Exception:
            # Shadow enrichment must never break the strategy process.
            pass
        return original_xadd(self, name, fields, *args, **kwargs)

    xadd_with_selector_shadow._r29b_selector_shadow_patched = True
    xadd_with_selector_shadow._r29b_original_xadd = original_xadd
    Redis.xadd = xadd_with_selector_shadow
    return True
