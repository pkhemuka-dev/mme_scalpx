"""
app/mme_scalpx/services/strategy_family/misls_shadow_logger.py

MISLS R4B shadow logger skeleton.

This module is intentionally:
- pure
- dormant
- research-only
- no Redis
- no broker
- no paper/live
- no risk/execution
- no registry wiring
- no FAMILY_ORDER wiring

It only builds and validates MISLS research/shadow event dictionaries.

Canonical in-memory output surface:
    research.misls.events

Research JSONL paths, for explicit offline/static callers only:
    run/research/misls_r3/events_YYYYMMDD.jsonl
    run/research/misls_r3/candidates_YYYYMMDD.jsonl
    run/research/misls_r3/rejections_YYYYMMDD.jsonl
    run/research/misls_r3/forward_paths_YYYYMMDD.jsonl
"""

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping


FAMILY_ID = "MISLS"

BRANCH_CALL = "CALL"
BRANCH_PUT = "PUT"
SUPPORTED_BRANCHES = (BRANCH_CALL, BRANCH_PUT)

FULL_CALL = "FULL_MISLS_R3_CALL_CANDIDATE"
FULL_PUT = "FULL_MISLS_R3_PUT_CANDIDATE"

TERMINAL_FULL_BY_BRANCH = {
    BRANCH_CALL: FULL_CALL,
    BRANCH_PUT: FULL_PUT,
}

RESEARCH_ROOT = Path("run/research/misls_r3")

RESEARCH_FILE_KINDS = {
    "events": "events_YYYYMMDD.jsonl",
    "candidates": "candidates_YYYYMMDD.jsonl",
    "rejections": "rejections_YYYYMMDD.jsonl",
    "forward_paths": "forward_paths_YYYYMMDD.jsonl",
}

MINIMUM_FULL_CANDIDATE_FIELDS = (
    "family_id",
    "branch_id",
    "side",
    "final_classification",
    "event_id",
    "candidate_id",
    "shadow_entry_price",
    "shadow_entry_underlying_price",
    "selected_option_bid_post",
    "selected_option_ask_post",
    "selected_option_bid_qty_post",
    "selected_option_ask_qty_post",
    "selected_option_quote_age_ms",
    "paired_option_bid_post",
    "paired_option_ask_post",
    "paired_option_bid_qty_post",
    "paired_option_ask_qty_post",
    "score",
)

FORBIDDEN_FIELDS = (
    "order_requested",
    "order_sent",
    "paper_order_requested",
    "paper_order_sent",
    "risk_start_requested",
    "execution_start_requested",
    "risk_event_emitted",
    "execution_event_emitted",
    "broker_order_api_called",
)

FORBIDDEN_POSITIVE_FIELDS = (
    "orders_stream_count",
    "risk_stream_count",
    "execution_stream_count",
    "paper_order_stream_count",
    "broker_order_api_call_count",
    "paper_order_count",
    "live_order_count",
    "position_change_count",
    "redis_delete_count",
    "lock_delete_count",
)


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        out = float(str(value).strip())
    except Exception:
        return default
    return out if math.isfinite(out) else default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "pass", "passed"}:
        return True
    if text in {"0", "false", "no", "n", "off", "fail", "failed", "none", "null"}:
        return False
    return default


def as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def normalize_branch(value: Any) -> str | None:
    text = safe_str(value).upper()
    if text in {"CALL", "CE", "C"}:
        return BRANCH_CALL
    if text in {"PUT", "PE", "P"}:
        return BRANCH_PUT
    return None


def normalize_score(value: Any) -> float:
    raw = safe_float(value, 0.0)
    if 1.0 < raw <= 100.0:
        raw = raw / 100.0
    return max(0.0, min(1.0, raw))


def stable_id(*parts: Any, prefix: str = "MISLS") -> str:
    clean = [safe_str(p, "NA").replace(" ", "_") for p in parts]
    digest = hashlib.sha256("|".join(clean).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{'_'.join(clean[:6])}_{digest}"


def final_classification_for_branch(branch_id: str) -> str:
    branch = normalize_branch(branch_id)
    if branch not in SUPPORTED_BRANCHES:
        raise ValueError(f"unsupported MISLS branch: {branch_id!r}")
    return TERMINAL_FULL_BY_BRANCH[branch]


def build_empty_misls_research_surface() -> dict[str, Any]:
    return {
        "research": {
            "misls": {
                "family_id": FAMILY_ID,
                "schema_version": "misls_r4b_shadow_logger_surface_v1",
                "research_only": True,
                "shadow_only": True,
                "events": [],
                "candidates": [],
                "rejections": [],
                "forward_paths": [],
            }
        }
    }


def ensure_misls_surface(container: Mapping[str, Any] | None = None) -> dict[str, Any]:
    out = dict(container or {})
    research = dict(out.get("research") or {})
    misls = dict(research.get("misls") or {})
    misls.setdefault("family_id", FAMILY_ID)
    misls.setdefault("schema_version", "misls_r4b_shadow_logger_surface_v1")
    misls.setdefault("research_only", True)
    misls.setdefault("shadow_only", True)
    misls.setdefault("events", [])
    misls.setdefault("candidates", [])
    misls.setdefault("rejections", [])
    misls.setdefault("forward_paths", [])
    research["misls"] = misls
    out["research"] = research
    return out


def validate_no_forbidden_runtime_surface(event: Mapping[str, Any]) -> tuple[bool, str | None]:
    item = as_mapping(event)

    for key in FORBIDDEN_FIELDS:
        if safe_bool(item.get(key), False):
            return False, f"FORBIDDEN_RUNTIME_FIELD:{key}"

    for key in FORBIDDEN_POSITIVE_FIELDS:
        if safe_float(item.get(key), 0.0) > 0.0:
            return False, f"FORBIDDEN_RUNTIME_COUNTER:{key}"

    action = safe_str(item.get("action") or item.get("action_hint")).upper()
    if action in {"ENTER", "ENTER_CALL", "ENTER_PUT", "BUY", "SELL"}:
        return False, "FORBIDDEN_TRADE_ACTION"

    return True, None


def validate_quote_fields(event: Mapping[str, Any]) -> tuple[bool, str | None]:
    item = as_mapping(event)

    for key in (
        "selected_option_bid_post",
        "selected_option_ask_post",
        "selected_option_bid_qty_post",
        "selected_option_ask_qty_post",
        "selected_option_quote_age_ms",
        "paired_option_bid_post",
        "paired_option_ask_post",
        "paired_option_bid_qty_post",
        "paired_option_ask_qty_post",
    ):
        if key not in item or item.get(key) in (None, ""):
            return False, f"QUOTE_FIELD_MISSING:{key}"

    selected_bid = safe_float(item.get("selected_option_bid_post"))
    selected_ask = safe_float(item.get("selected_option_ask_post"))
    paired_bid = safe_float(item.get("paired_option_bid_post"))
    paired_ask = safe_float(item.get("paired_option_ask_post"))

    if selected_bid <= 0.0 or selected_ask <= 0.0 or selected_ask <= selected_bid:
        return False, "SELECTED_QUOTE_PRICE_INVALID"

    if paired_bid <= 0.0 or paired_ask <= 0.0 or paired_ask <= paired_bid:
        return False, "PAIRED_QUOTE_PRICE_INVALID"

    for key in (
        "selected_option_bid_qty_post",
        "selected_option_ask_qty_post",
        "paired_option_bid_qty_post",
        "paired_option_ask_qty_post",
    ):
        if safe_float(item.get(key), 0.0) <= 0.0:
            return False, f"QUOTE_ZERO_QTY:{key}"

    if safe_float(item.get("selected_option_quote_age_ms"), 999999.0) > 250.0:
        return False, "SELECTED_QUOTE_STALE"

    return True, None


def validate_misls_event_contract(event: Mapping[str, Any]) -> tuple[bool, str | None]:
    item = as_mapping(event)

    ok, reason = validate_no_forbidden_runtime_surface(item)
    if not ok:
        return False, reason

    for key in MINIMUM_FULL_CANDIDATE_FIELDS:
        if key not in item or item.get(key) in (None, ""):
            return False, f"FIELD_MISSING:{key}"

    branch = normalize_branch(item.get("branch_id"))
    if branch not in SUPPORTED_BRANCHES:
        return False, "BRANCH_INVALID"

    if safe_str(item.get("family_id")).upper() != FAMILY_ID:
        return False, "FAMILY_ID_INVALID"

    if safe_str(item.get("side")).upper() not in SUPPORTED_BRANCHES:
        return False, "SIDE_INVALID"

    if safe_str(item.get("final_classification")) != final_classification_for_branch(branch):
        return False, "FINAL_CLASSIFICATION_INVALID"

    if not safe_str(item.get("event_id")):
        return False, "EVENT_ID_BLANK"

    if not safe_str(item.get("candidate_id")) or safe_str(item.get("candidate_id")).upper() == "NONE":
        return False, "CANDIDATE_ID_BLANK"

    ok, reason = validate_quote_fields(item)
    if not ok:
        return False, reason

    return True, None


def build_full_candidate_event(
    *,
    branch_id: str,
    event_ns: int,
    symbol: str,
    option_symbol: str,
    shadow_entry_price: float,
    shadow_entry_underlying_price: float,
    selected_option_bid_post: float,
    selected_option_ask_post: float,
    selected_option_bid_qty_post: float,
    selected_option_ask_qty_post: float,
    selected_option_quote_age_ms: float,
    paired_option_bid_post: float,
    paired_option_ask_post: float,
    paired_option_bid_qty_post: float,
    paired_option_ask_qty_post: float,
    score: float,
    level_type: str = "",
    variant: str = "",
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    branch = normalize_branch(branch_id)
    if branch not in SUPPORTED_BRANCHES:
        raise ValueError(f"unsupported MISLS branch: {branch_id!r}")

    event_id = stable_id(event_ns, symbol, branch, level_type, variant, "EVENT", prefix="MISLSR4B")
    candidate_id = stable_id(event_id, option_symbol, branch, "CANDIDATE", prefix="MISLSR4B")

    event = {
        "family_id": FAMILY_ID,
        "branch_id": branch,
        "side": branch,
        "final_classification": final_classification_for_branch(branch),
        "event_id": event_id,
        "candidate_id": candidate_id,
        "symbol": safe_str(symbol),
        "selected_option_symbol": safe_str(option_symbol),
        "option_symbol": safe_str(option_symbol),
        "level_type": safe_str(level_type),
        "variant": safe_str(variant),
        "shadow_entry_price": float(shadow_entry_price),
        "shadow_entry_underlying_price": float(shadow_entry_underlying_price),
        "selected_option_bid_post": float(selected_option_bid_post),
        "selected_option_ask_post": float(selected_option_ask_post),
        "selected_option_bid_qty_post": float(selected_option_bid_qty_post),
        "selected_option_ask_qty_post": float(selected_option_ask_qty_post),
        "selected_option_quote_age_ms": float(selected_option_quote_age_ms),
        "paired_option_bid_post": float(paired_option_bid_post),
        "paired_option_ask_post": float(paired_option_ask_post),
        "paired_option_bid_qty_post": float(paired_option_bid_qty_post),
        "paired_option_ask_qty_post": float(paired_option_ask_qty_post),
        "score": normalize_score(score),
        "research_only": True,
        "shadow_only": True,
        "no_order": True,
        "no_paper": True,
        "no_risk": True,
        "no_execution": True,
    }

    if extra:
        for key, value in dict(extra).items():
            if key not in event:
                event[key] = value

    ok, reason = validate_misls_event_contract(event)
    if not ok:
        raise ValueError(f"MISLS event contract failed: {reason}")

    return event


def append_misls_event(
    surface: Mapping[str, Any] | None,
    event: Mapping[str, Any],
    *,
    also_candidate: bool = True,
) -> dict[str, Any]:
    out = ensure_misls_surface(surface)
    event_dict = as_mapping(event)

    ok, reason = validate_misls_event_contract(event_dict)
    if not ok:
        rejection = {
            "family_id": FAMILY_ID,
            "event_id": safe_str(event_dict.get("event_id")),
            "candidate_id": safe_str(event_dict.get("candidate_id")),
            "reason": reason,
            "research_only": True,
            "shadow_only": True,
        }
        out["research"]["misls"]["rejections"].append(rejection)
        return out

    out["research"]["misls"]["events"].append(event_dict)
    if also_candidate:
        out["research"]["misls"]["candidates"].append(event_dict)
    return out


def jsonl_path_for_session(kind: str, session_yyyymmdd: str, root: str | Path = RESEARCH_ROOT) -> Path:
    if kind not in RESEARCH_FILE_KINDS:
        raise ValueError(f"unsupported MISLS research file kind: {kind!r}")
    day = safe_str(session_yyyymmdd)
    if len(day) != 8 or not day.isdigit():
        raise ValueError("session_yyyymmdd must be YYYYMMDD")
    return Path(root) / RESEARCH_FILE_KINDS[kind].replace("YYYYMMDD", day)


def to_jsonl_line(record: Mapping[str, Any]) -> str:
    return json.dumps(dict(record), sort_keys=True, separators=(",", ":"), default=str)


def write_jsonl_records_explicit_offline_only(
    records: list[Mapping[str, Any]],
    *,
    kind: str,
    session_yyyymmdd: str,
    root: str | Path = RESEARCH_ROOT,
) -> Path:
    path = jsonl_path_for_session(kind, session_yyyymmdd, root=root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for record in records:
            fh.write(to_jsonl_line(record))
            fh.write("\n")
    return path


__all__ = [
    "FAMILY_ID",
    "SUPPORTED_BRANCHES",
    "MINIMUM_FULL_CANDIDATE_FIELDS",
    "RESEARCH_ROOT",
    "build_empty_misls_research_surface",
    "ensure_misls_surface",
    "build_full_candidate_event",
    "append_misls_event",
    "validate_misls_event_contract",
    "jsonl_path_for_session",
    "to_jsonl_line",
    "write_jsonl_records_explicit_offline_only",
]
# === MISLS_R2A_RESEARCH_SHADOW_LOGGER_APPEND_ONLY ===
# Additive helper block. Writes MISLS research rows to local files only when called.

def misls_r2a_research_log_path(root_dir=None, day=None):
    import os
    import time

    root = root_dir or "run/research/misls_shadow"
    os.makedirs(root, exist_ok=True)
    day_value = day or time.strftime("%Y%m%d")
    return os.path.join(root, "misls_shadow_" + str(day_value) + ".jsonl")


def misls_r2a_append_shadow_row(row, root_dir=None):
    import json
    import time

    if not hasattr(row, "get"):
        row = {"raw_value": row}

    action = str(row.get("action") or "HOLD").upper()
    if action != "HOLD":
        return {
            "ok": False,
            "reason": "NON_HOLD_ACTION_REJECTED",
            "path": None,
            "bytes_written": 0,
        }

    envelope = {
        "schema": "misls_r2a_shadow_row_v1",
        "family": "MISLS",
        "research_only": True,
        "write_ts": time.time(),
        "row": dict(row),
    }

    path = misls_r2a_research_log_path(root_dir=root_dir)
    payload = json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(payload)

    return {
        "ok": True,
        "reason": None,
        "path": path,
        "bytes_written": len(payload.encode("utf-8")),
    }
# === /MISLS_R2A_RESEARCH_SHADOW_LOGGER_APPEND_ONLY ===
