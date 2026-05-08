"""RAW-U constructor-level family emission helper.

Pure replay helper for dict rows created inside replay reports/artifacts constructors.
No broker IO. No Redis. No live runtime. No risk/execution/strategy mutation.
"""

from __future__ import annotations

import json
import re
from typing import Any

RAW_U_SCHEMA_VERSION = "RAW-U.2"
FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
SIDES = ("CALL", "PUT")


def is_unknown(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip().upper()
    return text in {"", "UNKNOWN", "NONE", "NULL", "NO_BLOCKER"}


def _blob(row: dict[str, Any], source_artifact: str = "", constructor_name: str = "") -> str:
    parts = [source_artifact, constructor_name]
    for key, item in row.items():
        if item is None:
            continue
        parts.append(str(key))
        if isinstance(item, (dict, list, tuple)):
            try:
                parts.append(json.dumps(item, sort_keys=True))
            except Exception:
                parts.append(str(item))
        else:
            parts.append(str(item))
    return " ".join(parts).upper()


def detect_family(row: dict[str, Any], source_artifact: str = "", constructor_name: str = "") -> tuple[str, str]:
    current = row.get("family")
    if not is_unknown(current):
        return str(current).upper(), "existing"

    for key in ("strategy_id", "strategy", "strategy_family", "family_id", "source_family"):
        text = str(row.get(key) or "").upper()
        for family in FAMILIES:
            if family in text:
                return family, key

    blob = _blob(row, source_artifact, constructor_name)
    for family in FAMILIES:
        if re.search(rf"(^|[^A-Z0-9]){family}([^A-Z0-9]|$)", blob):
            return family, "constructor_or_source_lineage"

    return "UNKNOWN", "unresolved"


def detect_side(row: dict[str, Any], source_artifact: str = "", constructor_name: str = "") -> tuple[str, str]:
    current = row.get("side")
    if not is_unknown(current):
        text = str(current).upper()
        if "CALL" in text or text == "CE":
            return "CALL", "existing"
        if "PUT" in text or text == "PE":
            return "PUT", "existing"
        return text, "existing"

    blob = _blob(row, source_artifact, constructor_name)
    if re.search(r"(^|[^A-Z])CALL([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])CE([^A-Z]|$)", blob):
        return "CALL", "constructor_or_source_lineage"
    if re.search(r"(^|[^A-Z])PUT([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])PE([^A-Z]|$)", blob):
        return "PUT", "constructor_or_source_lineage"

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
        return f"{family}_{side}", "constructed_family_side"
    if family in FAMILIES:
        return family, "constructed_family"
    return "UNKNOWN", "unresolved"


def emit_constructor_family(value: Any, *, source_artifact: str = "", constructor_name: str = "") -> Any:
    if not isinstance(value, dict):
        return value

    out = dict(value)
    family, family_source = detect_family(out, source_artifact, constructor_name)
    side, side_source = detect_side(out, source_artifact, constructor_name)
    strategy_id, strategy_source = detect_strategy_id(out, family, side)

    out["family"] = family
    out["side"] = side
    out["strategy_id"] = strategy_id
    out["raw_u_family_source"] = family_source
    out["raw_u_side_source"] = side_source
    out["raw_u_strategy_id_source"] = strategy_source
    out["raw_u_constructor_name"] = constructor_name
    out["raw_u_schema_version"] = RAW_U_SCHEMA_VERSION
    out["raw_u_constructor_family_emission_applied"] = True
    return out
