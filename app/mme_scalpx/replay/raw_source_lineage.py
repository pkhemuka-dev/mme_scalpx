"""RAW-X source-row lineage injector.

Compatibility shim around RAW-W/RAW-S replay lineage helper.
Research-only. No broker IO, Redis writes, orders, risk, execution, or live runtime.
"""

from __future__ import annotations

from typing import Any

from app.mme_scalpx.replay.raw_producer_family_emission import emit_family_context


RAW_X_SCHEMA_VERSION = "RAW-X.3"


def inject_source_lineage(value: Any, *, source_artifact: str = "") -> Any:
    out = emit_family_context(value, source_artifact=source_artifact)
    if isinstance(out, dict):
        out["raw_x_source_lineage_applied"] = True
        out["raw_x_schema_version"] = RAW_X_SCHEMA_VERSION
        out.setdefault("raw_x_family_source", out.get("raw_w_family_source") or out.get("raw_s_family_source") or "unknown")
        out.setdefault("raw_x_side_source", out.get("raw_w_side_source") or out.get("raw_s_side_source") or "unknown")
        out.setdefault("raw_x_strategy_id_source", out.get("raw_w_strategy_id_source") or out.get("raw_s_strategy_id_source") or "unknown")
        out.setdefault("raw_x_candidate_id_source", out.get("raw_w_candidate_id_source") or "unknown")
        out.setdefault("raw_x_chosen_source_artifact", source_artifact)
    return out
