"""Replay producer family emission helper for RAW evidence.

RAW-W strengthens the RAW-S hook lineage path. It derives family/side/strategy_id
from row lineage and source artifact names when production labels are absent, and
creates a deterministic candidate_id for research evidence only.

Pure replay helper. No broker IO. No Redis. No orders. No strategy/risk/execution calls.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

RAW_W_SCHEMA_VERSION = "RAW-W.1"
FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
SIDES = ("CALL", "PUT")


def is_unknown(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip().upper()
    return text in {"", "UNKNOWN", "NONE", "NULL", "NO_BLOCKER"}


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, default=str)
    except Exception:
        return str(value)


def _flatten(value: Any, limit: int = 20000) -> str:
    parts: list[str] = []

    def visit(obj: Any, depth: int = 0) -> None:
        if len(" ".join(parts)) > limit or depth > 5:
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                parts.append(str(k))
                visit(v, depth + 1)
        elif isinstance(obj, (list, tuple, set)):
            for item in obj:
                visit(item, depth + 1)
        elif obj is not None:
            parts.append(str(obj))

    visit(value)
    return " ".join(parts).upper()


def _blob(row: dict[str, Any], source_artifact: str = "") -> str:
    return f"{source_artifact} {_flatten(row)}".upper()


def _first_present(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in row and not is_unknown(row.get(key)):
            return row.get(key)
    return None


def detect_family(row: dict[str, Any], source_artifact: str = "") -> tuple[str, str]:
    current = row.get("family")
    if not is_unknown(current):
        return str(current).upper(), "existing"

    for key in (
        "strategy_id",
        "strategy",
        "strategy_family",
        "family_id",
        "source_family",
        "doctrine",
        "doctrine_family",
        "selected_family",
        "winning_family",
        "family_name",
    ):
        text = str(row.get(key) or "").upper()
        for family in FAMILIES:
            if family in text:
                return family, key

    blob = _blob(row, source_artifact)
    for family in FAMILIES:
        if re.search(rf"(^|[^A-Z0-9]){family}([^A-Z0-9]|$)", blob):
            return family, "row_or_source_lineage"

    return "UNKNOWN", "unresolved"


def detect_side(row: dict[str, Any], source_artifact: str = "") -> tuple[str, str]:
    current = row.get("side")
    if not is_unknown(current):
        text = str(current).upper()
        if "CALL" in text or text == "CE":
            return "CALL", "existing"
        if "PUT" in text or text == "PE":
            return "PUT", "existing"
        return text, "existing"

    for key in ("option_type", "right", "strike_side", "selected_side", "instrument_side"):
        text = str(row.get(key) or "").upper()
        if "CALL" in text or text == "CE":
            return "CALL", key
        if "PUT" in text or text == "PE":
            return "PUT", key

    action = str(row.get("decision_action") or row.get("action") or row.get("decision") or "").upper()
    if "CALL" in action or action.endswith("_CE") or action == "CE":
        return "CALL", "decision_action"
    if "PUT" in action or action.endswith("_PE") or action == "PE":
        return "PUT", "decision_action"

    blob = _blob(row, source_artifact)
    if re.search(r"(^|[^A-Z])CALL([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])CE([^A-Z]|$)", blob):
        return "CALL", "row_or_source_lineage"
    if re.search(r"(^|[^A-Z])PUT([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])PE([^A-Z]|$)", blob):
        return "PUT", "row_or_source_lineage"

    return "UNKNOWN", "unresolved"


def detect_strategy_id(row: dict[str, Any], family: str, side: str) -> tuple[str, str]:
    current = row.get("strategy_id")
    if not is_unknown(current):
        return str(current).upper(), "existing"

    for key in ("strategy", "strategy_name", "doctrine", "doctrine_id", "source_strategy_id"):
        value = row.get(key)
        if not is_unknown(value):
            text = str(value).upper()
            if any(f in text for f in FAMILIES):
                return text, key

    if family in FAMILIES and side in SIDES:
        return f"{family}_{side}", "constructed_family_side"
    if family in FAMILIES:
        return family, "constructed_family"

    return "UNKNOWN", "unresolved"


def derive_candidate_id(row: dict[str, Any], source_artifact: str = "") -> tuple[str, str]:
    current = row.get("candidate_id")
    if not is_unknown(current):
        return str(current), "existing"

    for key in ("event_id", "trade_id", "order_id", "decision_id", "signal_id"):
        value = row.get(key)
        if not is_unknown(value):
            return f"RAW_W_{key.upper()}_{value}", key

    material = {
        "source_artifact": source_artifact,
        "source_run_id": row.get("source_run_id"),
        "row_kind": row.get("row_kind"),
        "artifact_kind": row.get("artifact_kind"),
        "decision_action": row.get("decision_action") or row.get("action"),
        "entry_ts": row.get("entry_ts"),
        "exit_ts": row.get("exit_ts"),
        "entry_price": row.get("entry_price"),
        "exit_price": row.get("exit_price"),
        "gross_pnl": row.get("gross_pnl"),
        "net_pnl_after_costs": row.get("net_pnl_after_costs"),
        "family": row.get("family"),
        "side": row.get("side"),
        "strategy_id": row.get("strategy_id"),
    }
    digest = hashlib.sha256(_safe_json(material).encode("utf-8")).hexdigest()[:16]
    return f"RAW_W_SYNTH_{digest}", "synthetic_lineage_hash"


def choose_source_artifact(row: dict[str, Any], source_artifact: str = "") -> str:
    if isinstance(row, dict):
        value = _first_present(
            row,
            (
                "source_artifact",
                "raw_source_artifact",
                "source_path",
                "artifact_path",
                "input_file",
                "input_path",
                "source_file",
            ),
        )
        if value is not None:
            return str(value)
    return source_artifact


def emit_family_context(value: Any, *, source_artifact: str = "") -> Any:
    """Return value with RAW lineage labels when value is a dict.

    This function intentionally marks labels as RAW-W lineage-derived. It does not
    make them production/doctrine truth.
    """
    if not isinstance(value, dict):
        return value

    out = dict(value)
    chosen_source_artifact = choose_source_artifact(out, source_artifact)

    family, family_source = detect_family(out, chosen_source_artifact)
    side, side_source = detect_side(out, chosen_source_artifact)

    # Fill first so strategy_id and candidate hash can include the derived context.
    out["family"] = family
    out["side"] = side

    strategy_id, strategy_source = detect_strategy_id(out, family, side)
    out["strategy_id"] = strategy_id

    candidate_id, candidate_source = derive_candidate_id(out, chosen_source_artifact)
    out["candidate_id"] = candidate_id

    out["raw_s_family_source"] = family_source
    out["raw_s_side_source"] = side_source
    out["raw_s_strategy_id_source"] = strategy_source
    out["raw_w_family_source"] = family_source
    out["raw_w_side_source"] = side_source
    out["raw_w_strategy_id_source"] = strategy_source
    out["raw_w_candidate_id_source"] = candidate_source
    out["raw_w_chosen_source_artifact"] = chosen_source_artifact
    out["raw_w_hook_lineage_applied"] = True
    out["raw_w_schema_version"] = RAW_W_SCHEMA_VERSION

    # Preserve previous RAW-S compatibility marker.
    out["raw_s_producer_family_emission_applied"] = True
    return out
