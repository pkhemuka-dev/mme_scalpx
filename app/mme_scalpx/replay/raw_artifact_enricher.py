"""Replay RAW artifact enrichment utilities.

This module is a replay-output enrichment stage. It creates enriched copies of existing
replay/trade/candidate/decision artifacts with the RAW-K frozen fields.

Safety:
- no broker IO
- no Redis IO
- no live runtime writes
- no order sending
- no strategy/risk/execution mutation
- no replay doctrine mutation
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

# RAW-AA2-R1 family preservation helper -- replay/research only.
_RAW_AA2_FAMILIES = ("MIST", "MISB", "MISC", "MISR", "MISO")
_RAW_AA2_UNKNOWN_FAMILY_VALUES = {
    "", "UNKNOWN", "NONE", "NULL", "NA", "N/A", "UNSET", "NO_FAMILY", "UNKNOWN_FAMILY"
}
_RAW_AA2_FAMILY_FIELDS = (
    "family",
    "strategy_family",
    "candidate_family",
    "resolved_family",
    "source_row_family",
    "source_family",
    "raw_family",
    "raw_x_family",
    "entry_family",
    "selected_family",
    "leaf_family",
    "producer_family",
    "report_family",
    "replay_family",
)
_RAW_AA2_TEXT_FAMILY_FIELDS = (
    "strategy_id",
    "strategy_name",
    "candidate_id",
    "event_id",
    "source_row_id",
    "decision_id",
    "blocker_chain",
    "reason_chain",
)


def _raw_aa2_normalize_family(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    folded = text.upper().replace("-", "").replace("_", "")
    if folded in _RAW_AA2_UNKNOWN_FAMILY_VALUES:
        return None
    for family_name in _RAW_AA2_FAMILIES:
        if family_name in folded:
            return family_name
    return None


def _raw_aa2_find_family(value: Any) -> tuple[str | None, str | None]:
    if not isinstance(value, dict):
        return None, None

    for field in _RAW_AA2_FAMILY_FIELDS:
        family_name = _raw_aa2_normalize_family(value.get(field))
        if family_name:
            return family_name, field

    for field in _RAW_AA2_TEXT_FAMILY_FIELDS:
        family_name = _raw_aa2_normalize_family(value.get(field))
        if family_name:
            return family_name, field

    return None, None


def _raw_aa2_preserve_family_context(
    enriched: dict[str, Any],
    source_row: dict[str, Any],
    *,
    source_artifact: str = "",
) -> dict[str, Any]:
    current_family = _raw_aa2_normalize_family(enriched.get("family"))
    if current_family:
        enriched["family"] = current_family
        enriched.setdefault("raw_aa2_family_source", "existing_family")
        return enriched

    for label, candidate in (
        ("source_row", source_row),
        ("enriched_row", enriched),
    ):
        family_name, field = _raw_aa2_find_family(candidate)
        if family_name:
            enriched["family"] = family_name
            enriched["raw_aa2_family_source"] = f"{label}:{field}"
            return enriched

    if source_artifact:
        family_name = _raw_aa2_normalize_family(source_artifact)
        if family_name:
            enriched["family"] = family_name
            enriched["raw_aa2_family_source"] = "source_artifact"
            return enriched

    if enriched.get("family") in (None, ""):
        enriched["family"] = "UNKNOWN"
    enriched.setdefault("raw_aa2_family_source", "unresolved")
    return enriched

# END RAW-AA2-R1 family preservation helper.


import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.mme_scalpx.replay.raw_family_context import apply_family_context


RAW_L_SCHEMA_VERSION = "RAW-L.1"

ENRICHED_RECORDS_JSONL = "enriched_replay_records.jsonl"
ENRICHMENT_MANIFEST_JSON = "enrichment_manifest.json"
ENRICHMENT_SUMMARY_JSON = "enrichment_summary.json"

REQUIRED_FIELD_GROUPS: dict[str, tuple[str, ...]] = {
    "identity": (
        "run_id",
        "source_run_id",
        "artifact_kind",
        "row_kind",
        "event_id",
        "event_ts",
    ),
    "strategy_context": (
        "family",
        "strategy_id",
        "side",
        "regime",
        "provider_mode",
    ),
    "candidate_truth": (
        "candidate_id",
        "candidate_state",
        "candidate_vs_executed",
        "decision_action",
        "blocker",
        "blocker_chain",
    ),
    "trade_truth": (
        "trade_id",
        "closed_trade_truth",
        "entry_ts",
        "exit_ts",
        "entry_price",
        "exit_price",
        "qty",
        "gross_pnl",
        "net_pnl_after_costs",
        "costs",
        "exit_reason",
    ),
    "outcome_labels": (
        "false_entry",
        "missed_trade",
        "good_blocker",
        "target_hit_after_block",
        "stop_hit_after_block",
        "hypothetical_pnl_after_block",
    ),
    "oi_wall_context": (
        "oi_wall_state",
        "oi_wall_distance_points",
        "oi_wall_strength",
        "strike_score",
        "selected_strike",
        "selected_strike_source",
    ),
    "audit_lineage": (
        "source_artifact",
        "source_row_index",
        "schema_version",
        "created_by",
        "remarks",
    ),
}

REQUIRED_FIELDS: tuple[str, ...] = tuple(
    field for fields in REQUIRED_FIELD_GROUPS.values() for field in fields
)

ALIASES: dict[str, tuple[str, ...]] = {
    "net_pnl_after_costs": ("net_pnl", "realized_net_pnl", "pnl_net", "closed_net_pnl"),
    "gross_pnl": ("pnl", "realized_pnl", "trade_pnl", "closed_pnl", "points_pnl"),
    "family": ("strategy_family", "family_id", "doctrine"),
    "side": ("branch_side", "option_side", "direction"),
    "provider_mode": ("runtime_mode", "dhan_mode", "mode"),
    "blocker": ("primary_blocker", "block_reason", "reject_reason", "veto_reason", "reason"),
    "candidate_vs_executed": ("row_kind", "executed", "entered", "filled"),
    "costs": ("cost", "charges", "fees", "brokerage", "transaction_cost"),
    "event_ts": ("ts", "timestamp", "ts_event_ns", "event_time", "created_at"),
    "event_id": ("candidate_id", "trade_id", "decision_id", "trap_event_id", "burst_event_id"),
    "decision_action": ("action", "decision", "final_action", "strategy_action"),
    "exit_reason": ("close_reason", "final_exit_reason"),
    "oi_wall_state": ("wall_state", "oi_context_state", "oi_bias", "near_oi_wall"),
    "oi_wall_distance_points": ("oi_wall_distance", "wall_distance", "distance_to_oi_wall"),
    "oi_wall_strength": ("wall_strength", "call_wall_strength", "put_wall_strength"),
    "strike_score": ("selected_strike_score", "oi_score"),
}

SUPPORTED_SUFFIXES = (".csv", ".json", ".jsonl", ".ndjson")

CANDIDATE_FILE_TOKENS = (
    "trade",
    "trades",
    "ledger",
    "candidate",
    "audit",
    "decision",
    "decisions",
    "pnl",
    "summary",
    "replay",
    "comparison",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _lower_key_map(row: dict[str, Any]) -> dict[str, str]:
    return {str(k).strip().lower(): str(k) for k in row.keys()}


def _first_value(row: dict[str, Any], field: str) -> Any:
    lower_map = _lower_key_map(row)
    direct = lower_map.get(field.lower())
    if direct is not None:
        value = row.get(direct)
        if value not in (None, ""):
            return value
    for alias in ALIASES.get(field, ()):
        key = lower_map.get(alias.lower())
        if key is not None:
            value = row.get(key)
            if value not in (None, ""):
                return value
    return None


def _safe_text(value: Any, default: str = "UNKNOWN") -> str:
    if value in (None, ""):
        return default
    return str(value)


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "filled", "entered", "executed", "closed"}:
        return True
    if text in {"0", "false", "no", "n", "none", "candidate", "not_executed"}:
        return False
    return None


def _safe_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def infer_artifact_kind(path: Path) -> str:
    low = path.name.lower()
    if "candidate" in low or "audit" in low:
        return "candidate_audit"
    if "decision" in low:
        return "decision_audit"
    if "summary" in low or "metrics" in low or "comparison" in low:
        return "replay_summary"
    if "trade" in low or "ledger" in low or "pnl" in low:
        return "trade_log"
    return "replay_artifact"


def infer_row_kind(row: dict[str, Any], artifact_kind: str) -> str:
    raw = _first_value(row, "row_kind")
    if raw not in (None, ""):
        return str(raw)

    if artifact_kind == "candidate_audit":
        return "candidate"
    if artifact_kind == "decision_audit":
        return "decision"
    if artifact_kind == "trade_log":
        return "trade"
    return "summary"


def infer_candidate_vs_executed(row: dict[str, Any], row_kind: str) -> str:
    raw = _first_value(row, "candidate_vs_executed")
    if raw not in (None, ""):
        text = str(raw).strip().upper()
        if text in {"CANDIDATE", "EXECUTED", "BOTH", "UNKNOWN"}:
            return text

    for field in ("executed", "entered", "filled", "entry_sent", "order_sent", "position_open"):
        b = _safe_bool(_first_value(row, field))
        if b is True:
            return "EXECUTED"

    if row_kind == "trade":
        return "EXECUTED"
    if row_kind == "candidate":
        return "CANDIDATE"
    return "UNKNOWN"


def infer_closed_trade_truth(row: dict[str, Any], row_kind: str) -> bool | None:
    raw = _first_value(row, "closed_trade_truth")
    b = _safe_bool(raw)
    if b is not None:
        return b

    has_entry = _first_value(row, "entry_price") not in (None, "")
    has_exit = _first_value(row, "exit_price") not in (None, "")
    has_pnl = (
        _first_value(row, "net_pnl_after_costs") not in (None, "")
        or _first_value(row, "gross_pnl") not in (None, "")
    )
    if row_kind == "trade" and (has_exit or has_pnl):
        return True
    if has_entry and has_exit:
        return True
    return None


def normalize_blocker_chain(value: Any) -> Any:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        if "|" in stripped:
            return [x.strip() for x in stripped.split("|") if x.strip()]
        if "," in stripped:
            return [x.strip() for x in stripped.split(",") if x.strip()]
        return [stripped]
    return [str(value)]


def enrich_row(
    row: dict[str, Any],
    *,
    source_artifact: str,
    source_row_index: int,
    run_id: str,
    source_run_id: str,
    artifact_kind: str,
) -> dict[str, Any]:
    row_kind = infer_row_kind(row, artifact_kind)
    candidate_vs_executed = infer_candidate_vs_executed(row, row_kind)

    enriched: dict[str, Any] = dict(row)
    enriched = apply_family_context(enriched, source_artifact=source_artifact)

    for field in REQUIRED_FIELDS:
        if field in enriched:
            continue
        value = _first_value(row, field)

        if field == "run_id":
            value = run_id
        elif field == "source_run_id":
            value = source_run_id
        elif field == "artifact_kind":
            value = artifact_kind
        elif field == "row_kind":
            value = row_kind
        elif field == "event_id":
            value = value if value not in (None, "") else f"{source_run_id}:{source_row_index}"
        elif field == "event_ts":
            value = value
        elif field in {"family", "strategy_id", "side", "regime", "provider_mode"}:
            value = _safe_text(value)
        elif field == "candidate_id":
            value = value if value not in (None, "") else None
        elif field == "candidate_state":
            value = _safe_text(value, default="UNKNOWN")
        elif field == "candidate_vs_executed":
            value = candidate_vs_executed
        elif field == "decision_action":
            value = _safe_text(value, default="UNKNOWN")
        elif field == "blocker":
            value = _safe_text(value, default="NO_BLOCKER")
        elif field == "blocker_chain":
            value = normalize_blocker_chain(value)
        elif field == "trade_id":
            value = value if value not in (None, "") else None
        elif field == "closed_trade_truth":
            value = infer_closed_trade_truth(row, row_kind)
        elif field in {"entry_price", "exit_price", "qty", "gross_pnl", "net_pnl_after_costs", "costs"}:
            value = _safe_float(value)
        elif field in {
            "false_entry",
            "missed_trade",
            "good_blocker",
            "target_hit_after_block",
            "stop_hit_after_block",
        }:
            value = _safe_bool(value)
        elif field == "hypothetical_pnl_after_block":
            value = _safe_float(value)
        elif field in {"oi_wall_distance_points", "oi_wall_strength", "strike_score"}:
            value = _safe_float(value)
        elif field == "source_artifact":
            value = source_artifact
        elif field == "source_row_index":
            value = source_row_index
        elif field == "schema_version":
            value = RAW_L_SCHEMA_VERSION
        elif field == "created_by":
            value = "app.mme_scalpx.replay.raw_artifact_enricher"
        elif field == "remarks":
            value = "RAW-L enriched copy; unknown values are not inferred."
        else:
            value = value if value not in (None, "") else None

        enriched[field] = value

    enriched = apply_family_context(enriched, source_artifact=source_artifact)
    enriched = _raw_aa2_preserve_family_context(enriched, row, source_artifact=source_artifact)
    enriched["raw_p_family_context_applied"] = True
    enriched["raw_aa2_family_preservation_applied"] = True
    return _raw_x_lineage(enriched, source_artifact=(enriched.get('source_artifact', '') if isinstance(enriched, dict) else ''))
def _dict_rows_from_json_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in (
            "trades",
            "trade_log",
            "rows",
            "records",
            "fills",
            "orders",
            "data",
            "candidate_audit",
            "decisions",
            "events",
            "summary",
        ):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return [payload]
    return []


def read_rows(path: Path, max_rows: int) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    rows: list[dict[str, Any]] = []

    if suffix == ".csv":
        with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                if idx > max_rows:
                    break
                rows.append(dict(row))
        return rows

    if suffix == ".json":
        if path.stat().st_size > 50 * 1024 * 1024:
            return []
        payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return _dict_rows_from_json_payload(payload)[:max_rows]

    if suffix in (".jsonl", ".ndjson"):
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if len(rows) >= max_rows:
                    break
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

    return rows


def find_candidate_artifacts(project_root: str | Path, max_files: int = 100) -> list[Path]:
    root = Path(project_root).resolve()
    scan_roots = [
        root / "run" / "replay",
        root / "run" / "research_capture",
        root / "run" / "proofs",
        root / "reports",
        root / "data",
    ]
    candidates: list[Path] = []
    skip = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}

    for scan_root in scan_roots:
        if not scan_root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(scan_root):
            dirnames[:] = [d for d in dirnames if d not in skip]
            for filename in filenames:
                path = Path(dirpath) / filename
                low = filename.lower()
                if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                    continue
                if not any(token in low for token in CANDIDATE_FILE_TOKENS):
                    continue
                # avoid repeatedly enriching RAW-L outputs as inputs
                if "raw_l_replay_enriched" in str(path) or "raw_l_enriched" in str(path):
                    continue
                candidates.append(path)
                if len(candidates) >= max_files:
                    return sorted(candidates)
    return sorted(candidates)


def verify_required_fields(row: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = [field for field in REQUIRED_FIELDS if field not in row]
    return len(missing) == 0, missing


def enrich_replay_artifacts(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    run_id: str,
    max_files: int = 100,
    max_rows_per_file: int = 5000,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    output_jsonl = out / ENRICHED_RECORDS_JSONL
    source_summaries: list[dict[str, Any]] = []
    total_rows = 0
    total_enriched_rows = 0
    missing_required_failures = 0

    with output_jsonl.open("w", encoding="utf-8") as wf:
        for path in find_candidate_artifacts(root, max_files=max_files):
            relative = str(path.relative_to(root))
            source_run_id = path.parent.name
            artifact_kind = infer_artifact_kind(path)
            before = total_enriched_rows
            status = "ENRICHED"
            error = None

            try:
                rows = read_rows(path, max_rows=max_rows_per_file)
                for idx, row in enumerate(rows, start=1):
                    total_rows += 1
                    enriched = enrich_row(
                        row,
                        source_artifact=relative,
                        source_row_index=idx,
                        run_id=run_id,
                        source_run_id=source_run_id,
                        artifact_kind=artifact_kind,
                    )
                    ok, missing = verify_required_fields(enriched)
                    if not ok:
                        missing_required_failures += 1
                        enriched["_raw_l_missing_required_fields"] = missing
                    wf.write(json.dumps(enriched, sort_keys=True) + "\n")
                    total_enriched_rows += 1
            except Exception as exc:
                status = "ERROR"
                error = str(exc)

            source_summaries.append({
                "source_artifact": relative,
                "artifact_kind": artifact_kind,
                "status": status,
                "error": error,
                "input_bytes": path.stat().st_size,
                "rows_enriched": total_enriched_rows - before,
            })

    coverage_ok = missing_required_failures == 0
    summary = {
        "schema_version": RAW_L_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "non_live": True,
        "non_mutating": True,
        "project_root": str(root),
        "output_dir": str(out),
        "output_jsonl": str(output_jsonl),
        "source_artifact_count": len(source_summaries),
        "total_input_rows_seen": total_rows,
        "total_enriched_rows": total_enriched_rows,
        "required_field_count": len(REQUIRED_FIELDS),
        "missing_required_failures": missing_required_failures,
        "required_field_coverage_ok": coverage_ok,
        "replay_output_enrichment_added": True,
        "replay_engine_mutation_included": False,
        "live_runtime_touched": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "paper_live_enablement_included": False,
        "source_summaries": source_summaries,
    }

    manifest = {
        "schema_version": RAW_L_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "artifacts": [
            {"path": ENRICHED_RECORDS_JSONL, "artifact_type": "enriched_replay_records_jsonl"},
            {"path": ENRICHMENT_SUMMARY_JSON, "artifact_type": "enrichment_summary"},
            {"path": ENRICHMENT_MANIFEST_JSON, "artifact_type": "enrichment_manifest"},
        ],
        "required_field_coverage_ok": coverage_ok,
        "total_enriched_rows": total_enriched_rows,
    }

    (out / ENRICHMENT_SUMMARY_JSON).write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (out / ENRICHMENT_MANIFEST_JSON).write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "output_dir": str(out),
        "enriched_records_jsonl": str(output_jsonl),
        "enrichment_summary": str(out / ENRICHMENT_SUMMARY_JSON),
        "enrichment_manifest": str(out / ENRICHMENT_MANIFEST_JSON),
        "source_artifact_count": len(source_summaries),
        "total_enriched_rows": total_enriched_rows,
        "required_field_count": len(REQUIRED_FIELDS),
        "missing_required_failures": missing_required_failures,
        "required_field_coverage_ok": coverage_ok,
    }
