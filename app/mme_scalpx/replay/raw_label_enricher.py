"""RAW-O replay label enricher.

Adds conservative replay-side labels to RAW-M/RAW-L enriched replay rows.

The module does not trade, does not call brokers, does not write Redis, does not mutate
risk/execution/strategy, and does not enable paper/live.
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
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAW_O_SCHEMA_VERSION = "RAW-O.1"

LABEL_ENRICHED_JSONL = "label_enriched_replay_records.jsonl"
LABEL_SUMMARY_JSON = "label_enrichment_summary.json"
LABEL_MANIFEST_JSON = "label_enrichment_manifest.json"

FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
SIDES = ("CALL", "PUT")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_unknown(value: Any) -> bool:
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.upper() in {"UNKNOWN", "NONE", "NULL", "NO_BLOCKER"}


def safe_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text or text.upper() == "UNKNOWN":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "pass", "filled", "executed", "closed"}:
        return True
    if text in {"0", "false", "no", "n", "fail", "none", "unknown"}:
        return False
    return None


def row_blob(row: dict[str, Any]) -> str:
    parts: list[str] = []
    for key, value in row.items():
        if value is None:
            continue
        if isinstance(value, (dict, list, tuple)):
            try:
                parts.append(json.dumps(value, sort_keys=True))
            except Exception:
                parts.append(str(value))
        else:
            parts.append(str(key))
            parts.append(str(value))
    return " ".join(parts).upper()


def detect_family(row: dict[str, Any]) -> tuple[str, str]:
    current = row.get("family")
    if not is_unknown(current):
        return str(current).upper(), "existing"

    blob = row_blob(row)
    for family in FAMILIES:
        if re.search(rf"(^|[^A-Z0-9]){family}([^A-Z0-9]|$)", blob):
            return family, "inferred_from_row_or_source_lineage"

    strategy_id = str(row.get("strategy_id") or "").upper()
    for family in FAMILIES:
        if family in strategy_id:
            return family, "inferred_from_strategy_id"

    return "UNKNOWN", "unresolved"


def detect_side(row: dict[str, Any]) -> tuple[str, str]:
    current = row.get("side")
    if not is_unknown(current):
        text = str(current).upper()
        if "CALL" in text or text == "CE":
            return "CALL", "existing"
        if "PUT" in text or text == "PE":
            return "PUT", "existing"
        return text, "existing"

    blob = row_blob(row)
    if re.search(r"(^|[^A-Z])CALL([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])CE([^A-Z]|$)", blob):
        return "CALL", "inferred_from_row_or_source_lineage"
    if re.search(r"(^|[^A-Z])PUT([^A-Z]|$)", blob) or re.search(r"(^|[^A-Z])PE([^A-Z]|$)", blob):
        return "PUT", "inferred_from_row_or_source_lineage"
    return "UNKNOWN", "unresolved"


def detect_strategy_id(row: dict[str, Any], family: str, side: str) -> tuple[str, str]:
    current = row.get("strategy_id")
    if not is_unknown(current):
        return str(current).upper(), "existing"
    if family in FAMILIES and side in SIDES:
        return f"{family}_{side}", "constructed_from_family_side"
    if family in FAMILIES:
        return family, "constructed_from_family"
    return "UNKNOWN", "unresolved"


def detect_oi_state(row: dict[str, Any]) -> tuple[str, str]:
    current = row.get("oi_wall_state")
    if not is_unknown(current):
        return str(current).upper(), "existing"

    blob = row_blob(row)
    if "CALL_WALL" in blob or "CE_WALL" in blob:
        return "CALL_WALL_CONTEXT", "inferred_from_row_or_source_lineage"
    if "PUT_WALL" in blob or "PE_WALL" in blob:
        return "PUT_WALL_CONTEXT", "inferred_from_row_or_source_lineage"
    if "OI_WALL" in blob or "OI WALL" in blob or "WALL" in blob:
        return "OI_WALL_CONTEXT_PRESENT", "inferred_from_row_or_source_lineage"
    return "UNKNOWN", "unresolved"


def derive_outcomes(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    updates: dict[str, Any] = {}
    sources: dict[str, str] = {}

    executed = str(row.get("candidate_vs_executed") or "").upper() == "EXECUTED"
    blocked = not is_unknown(row.get("blocker"))
    pnl = safe_float(row.get("net_pnl_after_costs"))
    hypo = safe_float(row.get("hypothetical_pnl_after_block"))
    target_after_block = safe_bool(row.get("target_hit_after_block"))
    stop_after_block = safe_bool(row.get("stop_hit_after_block"))

    if safe_bool(row.get("false_entry")) is None and executed and pnl is not None and pnl < 0:
        updates["false_entry"] = True
        sources["false_entry_source"] = "derived_executed_negative_pnl"

    if safe_bool(row.get("good_blocker")) is None and blocked:
        if stop_after_block is True or (hypo is not None and hypo < 0):
            updates["good_blocker"] = True
            sources["good_blocker_source"] = "derived_blocked_negative_future_or_stop"

    if safe_bool(row.get("missed_trade")) is None and blocked:
        if target_after_block is True or (hypo is not None and hypo > 0):
            updates["missed_trade"] = True
            sources["missed_trade_source"] = "derived_blocked_positive_future_or_target"

    return updates, sources


def enrich_label_row(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)

    family, family_source = detect_family(out)
    side, side_source = detect_side(out)
    strategy_id, strategy_source = detect_strategy_id(out, family, side)
    oi_state, oi_source = detect_oi_state(out)

    out["family"] = family
    out["side"] = side
    out["strategy_id"] = strategy_id
    out["oi_wall_state"] = oi_state

    out["raw_o_family_label_source"] = family_source
    out["raw_o_side_label_source"] = side_source
    out["raw_o_strategy_id_source"] = strategy_source
    out["raw_o_oi_wall_state_source"] = oi_source

    outcome_updates, outcome_sources = derive_outcomes(out)
    out.update(outcome_updates)
    out.update(outcome_sources)

    out["raw_o_schema_version"] = RAW_O_SCHEMA_VERSION
    out["raw_o_created_by"] = "app.mme_scalpx.replay.raw_label_enricher"
    out["raw_o_non_live"] = True
    out["raw_o_non_mutating"] = True
    return _raw_x_lineage(out, source_artifact=(out.get('source_artifact', '') if isinstance(out, dict) else ''))
def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(_raw_x_lineage(payload, source_artifact=(payload.get('source_artifact', '') if isinstance(payload, dict) else '')))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def label_enrich_replay_records(
    *,
    input_jsonl: str | Path,
    output_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(input_jsonl)
    enriched_rows = [enrich_label_row(row) for row in rows]

    output_jsonl = out_dir / LABEL_ENRICHED_JSONL
    with output_jsonl.open("w", encoding="utf-8") as f:
        for row in enriched_rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    total = len(enriched_rows)
    family_resolved = sum(1 for row in enriched_rows if not is_unknown(row.get("family")))
    side_resolved = sum(1 for row in enriched_rows if not is_unknown(row.get("side")))
    strategy_resolved = sum(1 for row in enriched_rows if not is_unknown(row.get("strategy_id")))
    oi_resolved = sum(1 for row in enriched_rows if not is_unknown(row.get("oi_wall_state")))
    false_entries = sum(1 for row in enriched_rows if safe_bool(row.get("false_entry")) is True)
    missed = sum(1 for row in enriched_rows if safe_bool(row.get("missed_trade")) is True)
    good_blockers = sum(1 for row in enriched_rows if safe_bool(row.get("good_blocker")) is True)

    family_unknown_ratio = round(1.0 - (family_resolved / max(total, 1)), 6)
    outcome_labeled = false_entries + missed + good_blockers
    unknown_outcome_rate = round(1.0 - (outcome_labeled / max(total, 1)), 6)

    summary = {
        "schema_version": RAW_O_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "input_jsonl": str(input_jsonl),
        "output_jsonl": str(output_jsonl),
        "row_count": total,
        "family_resolved_count": family_resolved,
        "side_resolved_count": side_resolved,
        "strategy_id_resolved_count": strategy_resolved,
        "oi_wall_state_resolved_count": oi_resolved,
        "family_unknown_ratio": family_unknown_ratio,
        "false_entry_count": false_entries,
        "missed_trade_count": missed,
        "good_blocker_count": good_blockers,
        "unknown_outcome_rate": unknown_outcome_rate,
        "label_enrichment_added": True,
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
        "paper_live_enablement_added": False,
        "remarks": [
            "Only conservative labels from existing row/source lineage are added.",
            "Unresolved labels remain UNKNOWN/null.",
            "Promotion is not allowed by RAW-O.",
        ],
    }

    manifest = {
        "schema_version": RAW_O_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "artifacts": [
            LABEL_ENRICHED_JSONL,
            LABEL_SUMMARY_JSON,
            LABEL_MANIFEST_JSON,
        ],
        "label_enrichment_added": True,
        "non_live": True,
        "non_mutating": True,
    }

    write_json(out_dir / LABEL_SUMMARY_JSON, summary)
    write_json(out_dir / LABEL_MANIFEST_JSON, manifest)

    return {
        "run_id": run_id,
        "output_dir": str(out_dir),
        "label_enriched_jsonl": str(output_jsonl),
        "label_summary": str(out_dir / LABEL_SUMMARY_JSON),
        "label_manifest": str(out_dir / LABEL_MANIFEST_JSON),
        "row_count": total,
        "family_resolved_count": family_resolved,
        "side_resolved_count": side_resolved,
        "strategy_id_resolved_count": strategy_resolved,
        "oi_wall_state_resolved_count": oi_resolved,
        "family_unknown_ratio": family_unknown_ratio,
        "false_entry_count": false_entries,
        "missed_trade_count": missed,
        "good_blocker_count": good_blockers,
        "unknown_outcome_rate": unknown_outcome_rate,
        "label_enrichment_added": True,
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
        "paper_live_enablement_added": False,
    }
