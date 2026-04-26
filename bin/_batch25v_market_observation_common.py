from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N

try:
    from app.mme_scalpx.services import features as F
except Exception:  # pragma: no cover
    F = None  # type: ignore[assignment]


class Batch25VError(RuntimeError):
    pass


# ============================================================================
# Basic helpers
# ============================================================================

def decode(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    return {str(decode(k)): decode(v) for k, v in dict(raw or {}).items()}


def json_load(value: Any, default: Any = None) -> Any:
    value = decode(value)
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return default
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in {"null", "none"}:
            return default
        try:
            return json.loads(text)
        except Exception:
            return default
    return default


def proof_path(name: str) -> Path:
    out = Path("run/proofs") / name
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def write_proof(path: str | Path, proof: Mapping[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(dict(proof), indent=2, sort_keys=True, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        out = float(value)
        if out != out or out in (float("inf"), float("-inf")):
            return default
        return out
    except Exception:
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"1", "true", "yes", "y", "ok", "on", "healthy", "available", "ready", "current"}:
            return True
        if text in {"0", "false", "no", "n", "off", "stale", "unavailable", "dead", "error", "fatal", "disabled"}:
            return False
    return bool(value)


def pick(mapping: Mapping[str, Any] | None, *keys: str, default: Any = None) -> Any:
    if not isinstance(mapping, Mapping):
        return default
    for key in keys:
        if key in mapping and mapping[key] not in (None, ""):
            return mapping[key]
    return default


def nested(root: Any, *path: str, default: Any = None) -> Any:
    cur = root
    for key in path:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def required_constant(*names: str) -> tuple[str, Any]:
    for name in names:
        if hasattr(N, name):
            return name, getattr(N, name)
    if F is not None:
        for name in names:
            if hasattr(F, name):
                return name, getattr(F, name)
    raise Batch25VError(f"missing required names.py/features constant from candidates: {names!r}")


def redis_client() -> Any:
    errors: list[str] = []

    try:
        from app.mme_scalpx.core import redisx as RX  # type: ignore

        for fn_name in (
            "get_redis_client",
            "create_redis_client",
            "build_redis_client",
            "redis_client",
            "get_client",
            "create_client",
            "client",
        ):
            fn = getattr(RX, fn_name, None)
            if callable(fn):
                try:
                    client = fn()
                    if hasattr(client, "hgetall"):
                        return client
                except Exception as exc:
                    errors.append(f"redisx.{fn_name}: {exc}")
    except Exception as exc:
        errors.append(f"redisx import: {exc}")

    try:
        import redis  # type: ignore

        url = os.getenv("REDIS_URL") or os.getenv("SCALPX_REDIS_URL")
        if url:
            return redis.Redis.from_url(url, decode_responses=False)

        host = os.getenv("REDIS_HOST")
        port = os.getenv("REDIS_PORT")
        if host and port:
            return redis.Redis(
                host=host,
                port=int(port),
                password=os.getenv("REDIS_PASSWORD") or None,
                ssl=(os.getenv("REDIS_SSL", "0").lower() in {"1", "true", "yes"}),
                decode_responses=False,
            )
    except Exception as exc:
        errors.append(f"redis env fallback: {exc}")

    raise Batch25VError(
        "Could not create Redis client. Configure project redisx or REDIS_URL. "
        f"Errors: {errors}"
    )


def hgetall_contract(client: Any, *constant_candidates: str) -> tuple[str, str, dict[str, Any]]:
    const_name, key = required_constant(*constant_candidates)
    raw = client.hgetall(key)
    return const_name, str(key), decode_hash(raw)


def stream_len_contract(client: Any, *constant_candidates: str) -> tuple[str, str, int]:
    const_name, key = required_constant(*constant_candidates)
    if not hasattr(client, "xlen"):
        raise Batch25VError("Redis client has no xlen()")
    return const_name, str(key), int(client.xlen(key))


def stream_recent_contract(client: Any, *constant_candidates: str, count: int = 20) -> tuple[str, str, list[dict[str, Any]]]:
    const_name, key = required_constant(*constant_candidates)
    if not hasattr(client, "xrevrange"):
        raise Batch25VError("Redis client has no xrevrange()")
    rows = []
    for row_id, fields in client.xrevrange(key, count=count):
        rows.append(
            {
                "id": str(decode(row_id)),
                "fields": decode_hash(fields),
            }
        )
    return const_name, str(key), rows


def status_ready(value: Any) -> bool:
    text = str(decode(value) or "").strip().upper()
    blocked = {
        "UNAVAILABLE",
        "STALE",
        "DEAD",
        "ERROR",
        "FATAL",
        "DISABLED",
        "UNKNOWN",
        "",
    }
    return text not in blocked


def member_from_json(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    parsed = json_load(mapping.get(key), {})
    return dict(parsed) if isinstance(parsed, Mapping) else {}


def depth_from(mapping: Mapping[str, Any]) -> float:
    bid = safe_float(pick(mapping, "bid_qty_5", "top5_bid_qty", "bid_qty", "best_bid_qty"), 0.0)
    ask = safe_float(pick(mapping, "ask_qty_5", "top5_ask_qty", "ask_qty", "best_ask_qty"), 0.0)
    return bid + ask


def option_present(member: Mapping[str, Any]) -> bool:
    return safe_float(pick(member, "ltp", "last_price", "price"), 0.0) > 0.0 and depth_from(member) > 0.0


def family_ids() -> tuple[str, ...]:
    if hasattr(N, "STRATEGY_FAMILY_IDS"):
        return tuple(getattr(N, "STRATEGY_FAMILY_IDS"))
    return ("MIST", "MISB", "MISC", "MISR", "MISO")


def branch_ids() -> tuple[str, ...]:
    if hasattr(N, "BRANCH_IDS"):
        return tuple(getattr(N, "BRANCH_IDS"))
    return ("CALL", "PUT")


# ============================================================================
# Batch 26I canonical producer-consumer matrix
# ============================================================================

BATCH26I_CANONICAL_BRANCH_FIELDS: dict[str, tuple[str, ...]] = {
    "MIST": (
        "trend_confirmed",
        "futures_impulse_ok",
        "pullback_detected",
        "micro_trap_resolved",
        "resume_confirmed",
        "option_tradability_pass",
    ),
    "MISB": (
        "shelf_confirmed",
        "breakout_shelf_valid",
        "breakout_triggered",
        "breakout_accepted",
        "option_tradability_pass",
    ),
    "MISC": (
        "compression_detected",
        "directional_breakout_triggered",
        "expansion_accepted",
        "retest_monitor_active",
        "resume_confirmed",
        "option_tradability_pass",
    ),
    "MISR": (
        "active_zone_valid",
        "active_zone",
        "trap_event_id",
        "fake_break_triggered",
        "absorption_pass",
        "range_reentry_confirmed",
        "flow_flip_confirmed",
        "hold_inside_range_proved",
        "no_mans_land_cleared",
        "reversal_impulse_confirmed",
        "option_tradability_pass",
    ),
    "MISO": (
        "burst_event_id",
        "burst_detected",
        "aggression_ok",
        "tape_speed_ok",
        "imbalance_persist_ok",
        "queue_reload_blocked",
        "futures_vwap_align_ok",
        "futures_contradiction_blocked",
        "tradability_pass",
    ),
}

BATCH26I_CANONICAL_BLOCKER_FIELDS: dict[str, tuple[str, ...]] = {
    "MISO": (
        "queue_reload_blocked",
        "futures_contradiction_blocked",
    ),
}

BATCH26I_INVERTED_ALIAS_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "MISO": {
        "queue_reload_blocked": ("queue_ok", "queue_clear", "queue_reload_clear"),
        "futures_contradiction_blocked": ("futures_veto_clear", "futures_clear"),
    }
}

BATCH26I_SOURCE_PRODUCER_EXPECTATIONS: dict[str, dict[str, tuple[str, tuple[str, ...]]]] = {
    "MIST": {
        "trend_confirmed": ("app/mme_scalpx/services/feature_family/mist_surface.py", ('"trend_confirmed":',)),
        "futures_impulse_ok": ("app/mme_scalpx/services/feature_family/mist_surface.py", ('"futures_impulse_ok":',)),
        "pullback_detected": ("app/mme_scalpx/services/feature_family/mist_surface.py", ('"pullback_detected":',)),
        "micro_trap_resolved": ("app/mme_scalpx/services/feature_family/mist_surface.py", ('"micro_trap_resolved":',)),
        "resume_confirmed": ("app/mme_scalpx/services/feature_family/mist_surface.py", ('"resume_confirmed":',)),
        "option_tradability_pass": ("app/mme_scalpx/services/feature_family/mist_surface.py", ('"option_tradability_pass":',)),
    },
    "MISB": {
        "shelf_confirmed": ("app/mme_scalpx/services/feature_family/misb_surface.py", ('"shelf_confirmed":',)),
        "breakout_shelf_valid": ("app/mme_scalpx/services/feature_family/misb_surface.py", ('"breakout_shelf_valid":',)),
        "breakout_triggered": ("app/mme_scalpx/services/feature_family/misb_surface.py", ('"breakout_triggered":',)),
        "breakout_accepted": ("app/mme_scalpx/services/feature_family/misb_surface.py", ('"breakout_accepted":',)),
        "option_tradability_pass": ("app/mme_scalpx/services/feature_family/misb_surface.py", ('"option_tradability_pass":',)),
    },
    "MISC": {
        "compression_detected": ("app/mme_scalpx/services/feature_family/misc_surface.py", ('"compression_detected":',)),
        "directional_breakout_triggered": ("app/mme_scalpx/services/feature_family/misc_surface.py", ('"directional_breakout_triggered":',)),
        "expansion_accepted": ("app/mme_scalpx/services/feature_family/misc_surface.py", ('"expansion_accepted":',)),
        "retest_monitor_active": ("app/mme_scalpx/services/feature_family/misc_surface.py", ('"retest_monitor_active":',)),
        "resume_confirmed": ("app/mme_scalpx/services/feature_family/misc_surface.py", ('"resume_confirmed":',)),
        "option_tradability_pass": ("app/mme_scalpx/services/feature_family/misc_surface.py", ('"option_tradability_pass":',)),
    },
    "MISR": {
        "active_zone_valid": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"active_zone_valid":',)),
        "active_zone": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"active_zone":',)),
        "trap_event_id": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"trap_event_id":',)),
        "fake_break_triggered": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"fake_break_triggered":',)),
        "absorption_pass": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"absorption_pass":',)),
        "range_reentry_confirmed": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"range_reentry_confirmed":',)),
        "flow_flip_confirmed": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"flow_flip_confirmed":',)),
        "hold_inside_range_proved": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"hold_inside_range_proved":',)),
        "no_mans_land_cleared": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"no_mans_land_cleared":',)),
        "reversal_impulse_confirmed": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"reversal_impulse_confirmed":',)),
        "option_tradability_pass": ("app/mme_scalpx/services/feature_family/misr_surface.py", ('"option_tradability_pass":',)),
    },
    "MISO": {
        "burst_event_id": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"burst_event_id":',)),
        "burst_detected": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"burst_detected":',)),
        "aggression_ok": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"aggression_ok":',)),
        "tape_speed_ok": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"tape_speed_ok":',)),
        "imbalance_persist_ok": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"imbalance_persist_ok":',)),
        "queue_reload_blocked": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"queue_reload_blocked":',)),
        "futures_vwap_align_ok": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"futures_vwap_align_ok":',)),
        "futures_contradiction_blocked": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"futures_contradiction_blocked":',)),
        "tradability_pass": ("app/mme_scalpx/services/feature_family/miso_surface.py", ('"tradability_pass":',)),
    },
}

BATCH26I_SOURCE_CONSUMER_EXPECTATIONS: dict[str, dict[str, tuple[str, tuple[str, ...]]]] = {
    "MIST": {
        "trend_confirmed": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("trend_confirmed")',)),
        "futures_impulse_ok": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("futures_impulse_ok")',)),
        "pullback_detected": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("pullback_detected")',)),
        "micro_trap_resolved": ("app/mme_scalpx/services/strategy_family/mist.py", ("micro_trap_resolved", "micro_trap_clear")),
        "resume_confirmed": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("resume_confirmed")',)),
        "option_tradability_pass": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('option_tradability_pass',)),
    },
    "MISB": {
        "shelf_confirmed": ("app/mme_scalpx/services/strategy_family/misb.py", ("shelf_confirmed", "breakout_shelf_valid")),
        "breakout_shelf_valid": ("app/mme_scalpx/services/strategy_family/misb.py", ("breakout_shelf_valid",)),
        "breakout_triggered": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("breakout_triggered")',)),
        "breakout_accepted": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("breakout_accepted")',)),
        "option_tradability_pass": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('option_tradability_pass',)),
    },
    "MISC": {
        "compression_detected": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("compression_detected")',)),
        "directional_breakout_triggered": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("directional_breakout_triggered")',)),
        "expansion_accepted": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("expansion_accepted")',)),
        "retest_monitor_active": ("app/mme_scalpx/services/strategy_family/misc.py", ("retest_monitor_active",)),
        "resume_confirmed": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("resume_confirmed")',)),
        "option_tradability_pass": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('option_tradability_pass',)),
    },
    "MISR": {
        "active_zone_valid": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("active_zone_valid")',)),
        "active_zone": ("app/mme_scalpx/services/strategy_family/misr.py", ("active_zone(",)),
        "trap_event_id": ("app/mme_scalpx/services/strategy_family/misr.py", ("trap_event_id_missing", "trap_event_already_consumed")),
        "fake_break_triggered": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("fake_break_triggered")',)),
        "absorption_pass": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("absorption_pass")',)),
        "range_reentry_confirmed": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("range_reentry_confirmed")',)),
        "flow_flip_confirmed": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("flow_flip_confirmed")',)),
        "hold_inside_range_proved": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("hold_inside_range_proved")',)),
        "no_mans_land_cleared": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("no_mans_land_cleared")',)),
        "reversal_impulse_confirmed": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("reversal_impulse_confirmed")',)),
        "option_tradability_pass": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('option_tradability_pass',)),
    },
    "MISO": {
        "burst_event_id": ("app/mme_scalpx/services/strategy_family/miso.py", ("burst_event_id_missing", "burst_event_id=burst_event_id")),
        "burst_detected": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("burst_detected")',)),
        "aggression_ok": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("aggression_ok")',)),
        "tape_speed_ok": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("tape_speed_ok")',)),
        "imbalance_persist_ok": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("imbalance_persist_ok")',)),
        "queue_reload_blocked": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('queue_reload_blocked',)),
        "futures_vwap_align_ok": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('support.get("futures_vwap_align_ok")',)),
        "futures_contradiction_blocked": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('futures_contradiction_blocked',)),
        "tradability_pass": ("app/mme_scalpx/services/strategy_family/eligibility.py", ('tradability_pass',)),
    },
}


def read_source(path_text: str) -> str:
    path = PROJECT_ROOT / path_text
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def source_has_all(path_text: str, snippets: Sequence[str]) -> bool:
    source = read_source(path_text)
    return bool(source) and all(snippet in source for snippet in snippets)


def source_has_any(path_text: str, snippets: Sequence[str]) -> bool:
    source = read_source(path_text)
    return bool(source) and any(snippet in source for snippet in snippets)


def producer_consumer_matrix() -> dict[str, Any]:
    report: dict[str, Any] = {}
    ok = True

    for family, fields in BATCH26I_CANONICAL_BRANCH_FIELDS.items():
        family_report: dict[str, Any] = {}
        for field in fields:
            producer_path, producer_snippets = BATCH26I_SOURCE_PRODUCER_EXPECTATIONS.get(family, {}).get(field, ("", ()))
            consumer_path, consumer_snippets = BATCH26I_SOURCE_CONSUMER_EXPECTATIONS.get(family, {}).get(field, ("", ()))

            producer_ok = source_has_all(producer_path, producer_snippets)
            consumer_ok = source_has_any(consumer_path, consumer_snippets)

            field_ok = producer_ok and consumer_ok
            if not field_ok:
                ok = False

            family_report[field] = {
                "producer_path": producer_path,
                "producer_snippets": list(producer_snippets),
                "producer_ok": producer_ok,
                "consumer_path": consumer_path,
                "consumer_snippets": list(consumer_snippets),
                "consumer_ok": consumer_ok,
                "field_ok": field_ok,
            }
        report[family] = family_report

    return {
        "ok": ok,
        "families": report,
    }


def inverted_alias_report() -> dict[str, Any]:
    from app.mme_scalpx.services.feature_family import contracts as C

    global_aliases = getattr(N, "CONTRACT_FIELD_COMPATIBILITY_ALIASES", {})
    if not isinstance(global_aliases, Mapping):
        global_aliases = {}

    report: dict[str, Any] = {
        "ok": True,
        "global_alias_violations": [],
        "family_inverted_alias_checks": {},
    }

    inverted = getattr(C, "FAMILY_SUPPORT_INVERTED_ALIAS_MAP", {})
    if not isinstance(inverted, Mapping):
        report["ok"] = False
        report["family_inverted_alias_checks"]["missing_inverted_map"] = True
        return report

    for family, mapping in BATCH26I_INVERTED_ALIAS_RULES.items():
        family_inv = inverted.get(family, {})
        family_report: dict[str, Any] = {}
        for canonical, aliases in mapping.items():
            actual_aliases = tuple(family_inv.get(canonical, ())) if isinstance(family_inv, Mapping) else ()
            alias_ok = all(alias in actual_aliases for alias in aliases)
            family_report[canonical] = {
                "expected_inverted_aliases": list(aliases),
                "actual_inverted_aliases": list(actual_aliases),
                "ok": alias_ok,
            }
            if not alias_ok:
                report["ok"] = False

            for alias in aliases:
                if alias in global_aliases:
                    report["ok"] = False
                    report["global_alias_violations"].append(
                        {
                            "alias": alias,
                            "global_target": global_aliases.get(alias),
                            "canonical": canonical,
                            "reason": "inverted boolean alias must not be in non-inverting global alias map",
                        }
                    )
        report["family_inverted_alias_checks"][family] = family_report

    return report


def missing_mode_report() -> dict[str, Any]:
    from app.mme_scalpx.services.strategy_family import common as SF_COMMON

    classic_missing = SF_COMMON.normalize_classic_runtime_mode(None)
    classic_unknown = SF_COMMON.normalize_classic_runtime_mode("UNKNOWN_TRADE_MODE")
    miso_missing = SF_COMMON.normalize_miso_runtime_mode(None)
    miso_unknown = SF_COMMON.normalize_miso_runtime_mode("UNKNOWN_BASE_MODE")

    ok = (
        classic_missing == "DISABLED"
        and classic_unknown == "DISABLED"
        and miso_missing == "DISABLED"
        and miso_unknown == "DISABLED"
    )

    return {
        "ok": ok,
        "classic_missing": classic_missing,
        "classic_unknown": classic_unknown,
        "miso_missing": miso_missing,
        "miso_unknown": miso_unknown,
    }


def unavailable_provider_report() -> dict[str, Any]:
    from app.mme_scalpx.services import features as FEATURES

    fn = getattr(FEATURES, "_batch26c_miso_provider_ready", None)
    if not callable(fn):
        return {
            "ok": False,
            "reason": "features._batch26c_miso_provider_ready missing",
        }

    unavailable_provider_runtime = {
        "active_futures_provider_id": "ZERODHA",
        "active_selected_option_provider_id": "DHAN",
        "active_option_context_provider_id": "DHAN",
        "futures_provider_status": "UNAVAILABLE",
        "selected_option_provider_status": "UNAVAILABLE",
        "option_context_provider_status": "UNAVAILABLE",
    }
    ready = bool(
        fn(
            unavailable_provider_runtime,
            miso_mode="BASE-5DEPTH",
            futures_present=True,
            selected_option_present=True,
            dhan_context_ready=True,
            dhan_context_fresh=True,
        )
    )

    return {
        "ok": ready is False,
        "provider_unavailable_becomes_ready": ready,
        "provider_runtime": unavailable_provider_runtime,
    }


def branch_surface_canonical_report(branch_surface: Mapping[str, Any], family_id: str) -> dict[str, Any]:
    required = BATCH26I_CANONICAL_BRANCH_FIELDS.get(str(family_id).upper(), ())
    missing = [key for key in required if key not in branch_surface]
    return {
        "family_id": str(family_id).upper(),
        "ok": not missing,
        "missing": missing,
        "required": list(required),
    }


def family_surfaces_canonical_report(family_surfaces: Mapping[str, Any]) -> dict[str, Any]:
    families = family_surfaces.get("families", {})
    surfaces_by_branch = family_surfaces.get("surfaces_by_branch", {})
    families = families if isinstance(families, Mapping) else {}
    surfaces_by_branch = surfaces_by_branch if isinstance(surfaces_by_branch, Mapping) else {}

    report: dict[str, Any] = {}
    ok = True

    for family in family_ids():
        family_block = families.get(family, {})
        branches = family_block.get("branches", {}) if isinstance(family_block, Mapping) else {}
        if not isinstance(branches, Mapping):
            branches = {}

        family_report: dict[str, Any] = {}
        for branch in branch_ids():
            flat_key = f"{family.lower()}_{branch.lower()}"
            branch_surface = branches.get(branch) or surfaces_by_branch.get(flat_key) or {}
            branch_surface = branch_surface if isinstance(branch_surface, Mapping) else {}
            branch_report = branch_surface_canonical_report(branch_surface, family)
            if not branch_report["ok"]:
                ok = False
            family_report[branch] = branch_report
        report[family] = family_report

    return {
        "ok": ok,
        "families": report,
    }


def eligible_truth_ok(families: Mapping[str, Any]) -> tuple[bool, dict[str, Any]]:
    """Fail if a family is eligible without canonical branch truth.

    This helper intentionally understands blocker semantics:
    - MISO queue_reload_blocked and futures_contradiction_blocked must be false
    - other canonical support keys must be true when family says eligible
    """
    report: dict[str, Any] = {}
    ok = True

    for family_id, block_any in dict(families or {}).items():
        family = str(family_id).upper()
        block = dict(block_any or {})
        eligible = safe_bool(block.get("eligible"), False)

        branches = dict(block.get("branches") or {})
        if not branches and family == "MISO":
            branches = {
                "CALL": dict(block.get("call_support") or {}),
                "PUT": dict(block.get("put_support") or {}),
            }

        required = BATCH26I_CANONICAL_BRANCH_FIELDS.get(family, ())
        blockers = BATCH26I_CANONICAL_BLOCKER_FIELDS.get(family, ())

        branch_reports = {}
        branch_truth_ok = False

        for branch_id, branch_any in branches.items():
            branch = dict(branch_any or {})
            positives = [field for field in required if field not in blockers]
            positives_ok = all(safe_bool(branch.get(field), False) for field in positives)
            blockers_clear = all(not safe_bool(branch.get(field), False) for field in blockers)
            canonical_present = all(field in branch for field in required)

            this_ok = positives_ok and blockers_clear and canonical_present
            branch_truth_ok = branch_truth_ok or this_ok
            branch_reports[str(branch_id)] = {
                "canonical_present": canonical_present,
                "positives_ok": positives_ok,
                "blockers_clear": blockers_clear,
                "ok": this_ok,
                "missing": [field for field in required if field not in branch],
            }

        family_ok = (not eligible) or branch_truth_ok
        if not family_ok:
            ok = False

        report[family] = {
            "eligible": eligible,
            "required_truth_present_when_eligible": branch_truth_ok,
            "ok": family_ok,
            "branches": branch_reports,
        }

    return ok, report


def build_all_static_guard_report() -> dict[str, Any]:
    matrix = producer_consumer_matrix()
    inverted = inverted_alias_report()
    modes = missing_mode_report()
    provider = unavailable_provider_report()
    return {
        "ok": bool(matrix.get("ok") and inverted.get("ok") and modes.get("ok") and provider.get("ok")),
        "producer_consumer_matrix": matrix,
        "inverted_alias_report": inverted,
        "missing_mode_report": modes,
        "unavailable_provider_report": provider,
    }


__all__ = [
    "Batch25VError",
    "BATCH26I_CANONICAL_BRANCH_FIELDS",
    "BATCH26I_CANONICAL_BLOCKER_FIELDS",
    "BATCH26I_INVERTED_ALIAS_RULES",
    "build_all_static_guard_report",
    "branch_ids",
    "branch_surface_canonical_report",
    "decode",
    "decode_hash",
    "depth_from",
    "eligible_truth_ok",
    "family_ids",
    "family_surfaces_canonical_report",
    "hgetall_contract",
    "inverted_alias_report",
    "json_load",
    "member_from_json",
    "missing_mode_report",
    "nested",
    "option_present",
    "pick",
    "producer_consumer_matrix",
    "proof_path",
    "redis_client",
    "required_constant",
    "safe_bool",
    "safe_float",
    "safe_int",
    "status_ready",
    "stream_len_contract",
    "stream_recent_contract",
    "unavailable_provider_report",
    "write_proof",
]
