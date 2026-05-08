"""RAW-Q replay trade-row family backfill.

Backfills family/side/strategy_id specifically on closed-trade rows by using nearby
candidate/decision/source lineage from the same enriched replay evidence set.

Replay-only. No broker IO. No Redis. No orders. No strategy/risk/execution mutation.
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.mme_scalpx.replay.raw_family_context import apply_family_context, is_unknown

RAW_Q_SCHEMA_VERSION = "RAW-Q.1"

TRADE_BACKFILLED_JSONL = "trade_family_backfilled_records.jsonl"
TRADE_BACKFILL_SUMMARY_JSON = "trade_family_backfill_summary.json"
TRADE_BACKFILL_MANIFEST_JSON = "trade_family_backfill_manifest.json"

FAMILIES = {"MIST", "MISB", "MISC", "MISR", "MISO"}
SIDES = {"CALL", "PUT"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text or text.upper() in {"UNKNOWN", "NONE", "NULL"}:
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


def norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def norm_upper(value: Any) -> str:
    return norm(value).upper()


def is_trade_row(row: dict[str, Any]) -> bool:
    closed = safe_bool(row.get("closed_trade_truth"))
    executed = norm_upper(row.get("candidate_vs_executed")) == "EXECUTED"
    row_kind = norm_upper(row.get("row_kind"))
    net = safe_float(row.get("net_pnl_after_costs"))
    gross = safe_float(row.get("gross_pnl"))
    return closed is True or (executed and net is not None) or (row_kind == "TRADE" and (net is not None or gross is not None))


def is_labeled_family(value: Any) -> bool:
    return norm_upper(value) in FAMILIES


def is_labeled_side(value: Any) -> bool:
    return norm_upper(value) in SIDES


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
                rows.append(payload)
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def source_parent_key(source_artifact: Any) -> str:
    text = norm(source_artifact)
    if not text:
        return ""
    return str(Path(text).parent)


def source_file_key(source_artifact: Any) -> str:
    return norm(source_artifact)


def row_keys(row: dict[str, Any]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    for name in ["candidate_id", "event_id", "trade_id", "source_run_id"]:
        value = norm(row.get(name))
        if value:
            keys.append((name, value))
    sf = source_file_key(row.get("source_artifact"))
    sp = source_parent_key(row.get("source_artifact"))
    if sf:
        keys.append(("source_artifact", sf))
    if sp:
        keys.append(("source_parent", sp))
    return keys


def build_context_maps(rows: list[dict[str, Any]]) -> dict[str, dict[tuple[str, str], Counter]]:
    maps: dict[str, dict[tuple[str, str], Counter]] = {
        "family": defaultdict(Counter),
        "side": defaultdict(Counter),
        "strategy_id": defaultdict(Counter),
    }

    for row in rows:
        family = norm_upper(row.get("family"))
        side = norm_upper(row.get("side"))
        strategy_id = norm_upper(row.get("strategy_id"))

        for key in row_keys(row):
            if family in FAMILIES:
                maps["family"][key][family] += 1
            if side in SIDES:
                maps["side"][key][side] += 1
            if strategy_id and strategy_id not in {"UNKNOWN", "NONE", "NULL"}:
                maps["strategy_id"][key][strategy_id] += 1

    return maps


def choose_from_counter(counter: Counter) -> tuple[str, str]:
    if not counter:
        return "UNKNOWN", "no_context"
    most = counter.most_common()
    if len(most) == 1:
        return str(most[0][0]), "unique_context"
    if most[0][1] > most[1][1]:
        return str(most[0][0]), "dominant_context"
    return "UNKNOWN", "conflicting_context"


def lookup_context(row: dict[str, Any], maps: dict[str, dict[tuple[str, str], Counter]], field: str) -> tuple[str, str, str]:
    priority = ["candidate_id", "event_id", "trade_id", "source_artifact", "source_parent", "source_run_id"]
    keyed = dict(row_keys(row))
    for key_name in priority:
        key_value = keyed.get(key_name)
        if not key_value:
            continue
        value, method = choose_from_counter(maps[field].get((key_name, key_value), Counter()))
        if value != "UNKNOWN":
            return value, method, key_name
    return "UNKNOWN", "unresolved", ""


def backfill_trade_row(row: dict[str, Any], maps: dict[str, dict[tuple[str, str], Counter]]) -> dict[str, Any]:
    out = apply_family_context(dict(row), source_artifact=norm(row.get("source_artifact")))

    original_family = norm_upper(row.get("family"))
    original_side = norm_upper(row.get("side"))
    original_strategy = norm_upper(row.get("strategy_id"))

    family_before = original_family if original_family else "UNKNOWN"
    side_before = original_side if original_side else "UNKNOWN"
    strategy_before = original_strategy if original_strategy else "UNKNOWN"

    family_source = out.get("raw_p_family_source", "unknown")
    side_source = out.get("raw_p_side_source", "unknown")
    strategy_source = out.get("raw_p_strategy_id_source", "unknown")

    if not is_labeled_family(out.get("family")):
        family, method, key = lookup_context(out, maps, "family")
        if family != "UNKNOWN":
            out["family"] = family
            family_source = f"raw_q_{method}_{key}"

    if not is_labeled_side(out.get("side")):
        side, method, key = lookup_context(out, maps, "side")
        if side != "UNKNOWN":
            out["side"] = side
            side_source = f"raw_q_{method}_{key}"

    if is_unknown(out.get("strategy_id")):
        strategy, method, key = lookup_context(out, maps, "strategy_id")
        if strategy != "UNKNOWN":
            out["strategy_id"] = strategy
            strategy_source = f"raw_q_{method}_{key}"

    if is_unknown(out.get("strategy_id")) and is_labeled_family(out.get("family")) and is_labeled_side(out.get("side")):
        out["strategy_id"] = f"{norm_upper(out.get('family'))}_{norm_upper(out.get('side'))}"
        strategy_source = "raw_q_constructed_from_family_side"

    out["raw_q_trade_family_backfill_applied"] = True
    out["raw_q_family_before"] = family_before
    out["raw_q_side_before"] = side_before
    out["raw_q_strategy_id_before"] = strategy_before
    out["raw_q_family_source"] = family_source
    out["raw_q_side_source"] = side_source
    out["raw_q_strategy_id_source"] = strategy_source
    out["raw_q_schema_version"] = RAW_Q_SCHEMA_VERSION
    out["raw_q_non_live"] = True
    out["raw_q_non_mutating"] = True
    return out


def backfill_trade_families(
    *,
    input_jsonl: str | Path,
    output_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(input_jsonl)
    maps = build_context_maps(rows)

    output_rows: list[dict[str, Any]] = []
    trade_count = 0
    trade_family_before = 0
    trade_family_after = 0
    trade_side_before = 0
    trade_side_after = 0
    trade_strategy_before = 0
    trade_strategy_after = 0
    trade_backfilled_count = 0

    for row in rows:
        if not is_trade_row(row):
            output_rows.append(row)
            continue

        trade_count += 1
        if is_labeled_family(row.get("family")):
            trade_family_before += 1
        if is_labeled_side(row.get("side")):
            trade_side_before += 1
        if not is_unknown(row.get("strategy_id")):
            trade_strategy_before += 1

        new_row = backfill_trade_row(row, maps)

        if is_labeled_family(new_row.get("family")):
            trade_family_after += 1
        if is_labeled_side(new_row.get("side")):
            trade_side_after += 1
        if not is_unknown(new_row.get("strategy_id")):
            trade_strategy_after += 1

        if (
            norm_upper(new_row.get("family")) != norm_upper(row.get("family"))
            or norm_upper(new_row.get("side")) != norm_upper(row.get("side"))
            or norm_upper(new_row.get("strategy_id")) != norm_upper(row.get("strategy_id"))
        ):
            trade_backfilled_count += 1

        output_rows.append(new_row)

    output_jsonl = out_dir / TRADE_BACKFILLED_JSONL
    with output_jsonl.open("w", encoding="utf-8") as f:
        for row in output_rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    family_trade_counts = Counter()
    for row in output_rows:
        if is_trade_row(row):
            family_trade_counts[norm_upper(row.get("family")) or "UNKNOWN"] += 1

    summary = {
        "schema_version": RAW_Q_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "input_jsonl": str(input_jsonl),
        "output_jsonl": str(output_jsonl),
        "row_count": len(rows),
        "trade_count": trade_count,
        "trade_family_before_count": trade_family_before,
        "trade_family_after_count": trade_family_after,
        "trade_side_before_count": trade_side_before,
        "trade_side_after_count": trade_side_after,
        "trade_strategy_before_count": trade_strategy_before,
        "trade_strategy_after_count": trade_strategy_after,
        "trade_backfilled_count": trade_backfilled_count,
        "trade_family_unknown_ratio_after": round(1.0 - (trade_family_after / max(trade_count, 1)), 6),
        "family_trade_counts": dict(sorted(family_trade_counts.items())),
        "rank_candidate_family_count": sum(1 for k, v in family_trade_counts.items() if k in FAMILIES and v >= 3),
        "trade_family_backfill_added": True,
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
        "paper_live_enablement_added": False,
    }

    manifest = {
        "schema_version": RAW_Q_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "artifacts": [
            TRADE_BACKFILLED_JSONL,
            TRADE_BACKFILL_SUMMARY_JSON,
            TRADE_BACKFILL_MANIFEST_JSON,
        ],
        "trade_family_backfill_added": True,
        "non_live": True,
        "non_mutating": True,
    }

    write_json(out_dir / TRADE_BACKFILL_SUMMARY_JSON, summary)
    write_json(out_dir / TRADE_BACKFILL_MANIFEST_JSON, manifest)

    return {
        "run_id": run_id,
        "output_dir": str(out_dir),
        "trade_backfilled_jsonl": str(output_jsonl),
        "summary": str(out_dir / TRADE_BACKFILL_SUMMARY_JSON),
        "manifest": str(out_dir / TRADE_BACKFILL_MANIFEST_JSON),
        "row_count": len(rows),
        "trade_count": trade_count,
        "trade_family_before_count": trade_family_before,
        "trade_family_after_count": trade_family_after,
        "trade_side_before_count": trade_side_before,
        "trade_side_after_count": trade_side_after,
        "trade_strategy_before_count": trade_strategy_before,
        "trade_strategy_after_count": trade_strategy_after,
        "trade_backfilled_count": trade_backfilled_count,
        "trade_family_unknown_ratio_after": summary["trade_family_unknown_ratio_after"],
        "rank_candidate_family_count": summary["rank_candidate_family_count"],
        "family_trade_counts": summary["family_trade_counts"],
        "trade_family_backfill_added": True,
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
        "paper_live_enablement_added": False,
    }
