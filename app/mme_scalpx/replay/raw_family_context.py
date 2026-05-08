"""Replay family/side/strategy context helpers for RAW evidence.

Pure replay-only helper. No broker IO. No Redis. No strategy/risk/execution calls.
"""

from __future__ import annotations

# RAW-X source-row lineage hook -- replay/research only.
try:
    from app.mme_scalpx.replay.raw_source_lineage import inject_source_lineage as _raw_x_inject_source_lineage
except Exception:
    def _raw_x_inject_source_lineage(value, *, source_artifact=''):
        return value


def _raw_x_lineage(value, *, source_artifact=''):
    return _raw_x_inject_source_lineage(value, source_artifact=source_artifact)
# END RAW-X source-row lineage hook.

import json
import re
from typing import Any

RAW_FAMILY_CONTEXT_SCHEMA_VERSION = "RAW-P.2"

FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
SIDES = ("CALL", "PUT")


def is_unknown(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.upper() in {"UNKNOWN", "NONE", "NULL", "NO_BLOCKER"}


def _blob(row: dict[str, Any], source_artifact: str = "") -> str:
    parts: list[str] = [source_artifact]
    for key, value in row.items():
        if value is None:
            continue
        parts.append(str(key))
        if isinstance(value, (dict, list, tuple)):
            try:
                parts.append(json.dumps(value, sort_keys=True))
            except Exception:
                parts.append(str(value))
        else:
            parts.append(str(value))
    return " ".join(parts).upper()


def detect_family(row: dict[str, Any], source_artifact: str = "") -> tuple[str, str]:
    current = row.get("family")
    if not is_unknown(current):
        return str(current).upper(), "existing"

    strategy_id = str(row.get("strategy_id") or "").upper()
    for family in FAMILIES:
        if family in strategy_id:
            return family, "strategy_id"

    blob = _blob(row, source_artifact)
    for family in FAMILIES:
        if re.search(rf"(^|[^A-Z0-9]){family}([^A-Z0-9]|$)", blob):
            return family, "source_lineage"

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

    blob = _blob(row, source_artifact)
    if re.search(r"(^|[^A-Z])CALL([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])CE([^A-Z]|$)", blob):
        return "CALL", "source_lineage"
    if re.search(r"(^|[^A-Z])PUT([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])PE([^A-Z]|$)", blob):
        return "PUT", "source_lineage"

    action = str(row.get("decision_action") or row.get("action") or "").upper()
    if "CALL" in action or action.endswith("_CE"):
        return "CALL", "decision_action"
    if "PUT" in action or action.endswith("_PE"):
        return "PUT", "decision_action"

    return "UNKNOWN", "unresolved"


def detect_strategy_id(row: dict[str, Any], family: str, side: str) -> tuple[str, str]:
    current = row.get("strategy_id")
    if not is_unknown(current):
        return str(current).upper(), "existing"
    if family in FAMILIES and side in SIDES:
        return f"{family}_{side}", "family_side"
    if family in FAMILIES:
        return family, "family"
    return "UNKNOWN", "unresolved"


def apply_family_context(row: dict[str, Any], source_artifact: str = "") -> dict[str, Any]:
    out = dict(row)
    family, family_source = detect_family(out, source_artifact)
    side, side_source = detect_side(out, source_artifact)
    strategy_id, strategy_source = detect_strategy_id(out, family, side)

    out["family"] = family
    out["side"] = side
    out["strategy_id"] = strategy_id
    out["raw_p_family_source"] = family_source
    out["raw_p_side_source"] = side_source
    out["raw_p_strategy_id_source"] = strategy_source
    out["raw_p_family_context_schema_version"] = RAW_FAMILY_CONTEXT_SCHEMA_VERSION
    return _raw_x_lineage(out, source_artifact=(out.get('source_artifact', '') if isinstance(out, dict) else ''))