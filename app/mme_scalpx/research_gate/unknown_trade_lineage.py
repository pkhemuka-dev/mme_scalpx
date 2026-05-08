"""RAW-V unknown-trade lineage tracer.

Reads RAW-T/RAW-Q backfilled replay evidence and traces UNKNOWN-family trade
rows to source artifacts, likely producer files/functions, missing fields, and
recommended patch targets.

Review only. No replay mutation. No broker IO. No Redis. No orders. No paper/live.
"""

from __future__ import annotations

import ast
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RAW_V_SCHEMA_VERSION = "RAW-V.1"

TRACE_JSON = "unknown_trade_lineage_trace.json"
LINEAGE_CSV = "unknown_trade_lineage_map.csv"
PATCH_TARGETS_CSV = "producer_patch_targets.csv"
SOURCE_ARTIFACTS_CSV = "unknown_trade_source_artifacts.csv"
SUMMARY_MD = "RAW_V_UNKNOWN_TRADE_LINEAGE_TRACE.md"
MANIFEST_JSON = "manifest.json"

FAMILIES = {"MIST", "MISB", "MISC", "MISR", "MISO"}

PATCH_TARGET_FILES = [
    "app/mme_scalpx/replay/reports.py",
    "app/mme_scalpx/replay/artifacts.py",
    "app/mme_scalpx/replay/runner.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/metrics.py",
    "app/mme_scalpx/replay/comparison_artifacts.py",
    "app/mme_scalpx/replay/frame_export.py",
    "app/mme_scalpx/replay/raw_artifact_enricher.py",
]

PRODUCER_KEYWORDS = [
    "net_pnl_after_costs",
    "gross_pnl",
    "closed_trade_truth",
    "candidate_vs_executed",
    "trade_id",
    "candidate_id",
    "event_id",
    "decision_action",
    "source_artifact",
    "strategy_id",
    "family",
    "side",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def upper(value: Any) -> str:
    return norm(value).upper()


def is_unknown(value: Any) -> bool:
    text = upper(value)
    return text in {"", "UNKNOWN", "NONE", "NULL", "NO_BLOCKER"}


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


def is_trade_row(row: dict[str, Any]) -> bool:
    closed = safe_bool(row.get("closed_trade_truth"))
    executed = upper(row.get("candidate_vs_executed")) == "EXECUTED"
    row_kind = upper(row.get("row_kind"))
    net = safe_float(row.get("net_pnl_after_costs"))
    gross = safe_float(row.get("gross_pnl"))
    return closed is True or (executed and net is not None) or (row_kind == "TRADE" and (net is not None or gross is not None))


def is_unknown_family_trade(row: dict[str, Any]) -> bool:
    if not is_trade_row(row):
        return False
    family = upper(row.get("family"))
    return family not in FAMILIES


def pnl_value(row: dict[str, Any]) -> float:
    net = safe_float(row.get("net_pnl_after_costs"))
    if net is not None:
        return net
    gross = safe_float(row.get("gross_pnl"))
    costs = safe_float(row.get("costs")) or 0.0
    if gross is not None:
        return gross - costs
    return 0.0


def source_parent(source_artifact: str) -> str:
    if not source_artifact:
        return ""
    return str(Path(source_artifact).parent)


def file_sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_artifact_info(project_root: Path, source_artifact: str) -> dict[str, Any]:
    if not source_artifact:
        return {
            "source_artifact": "",
            "exists": False,
            "bytes": None,
            "sha256": None,
            "ext": "",
            "parent": "",
        }

    p = Path(source_artifact)
    if not p.is_absolute():
        p = project_root / p

    return {
        "source_artifact": source_artifact,
        "resolved_path": str(p),
        "exists": p.exists(),
        "bytes": p.stat().st_size if p.exists() and p.is_file() else None,
        "sha256": file_sha256(p),
        "ext": p.suffix.lower(),
        "parent": source_parent(source_artifact),
    }


def probable_transformation_kind(row: dict[str, Any]) -> str:
    markers = []
    for key in row.keys():
        if str(key).startswith("raw_q_"):
            markers.append("raw_q_trade_family_backfill")
        if str(key).startswith("raw_p_"):
            markers.append("raw_p_family_context")
        if str(key).startswith("raw_o_"):
            markers.append("raw_o_label_enrichment")
        if str(key).startswith("raw_s_"):
            markers.append("raw_s_producer_hook")
        if str(key).startswith("raw_u_"):
            markers.append("raw_u_constructor_hook")
    if markers:
        return "+".join(sorted(set(markers)))
    artifact_kind = upper(row.get("artifact_kind"))
    row_kind = upper(row.get("row_kind"))
    if artifact_kind or row_kind:
        return f"artifact_row:{artifact_kind or row_kind}"
    return "unknown_or_copied_row"


def infer_likely_producer_from_source(source_artifact: str, row: dict[str, Any]) -> str:
    src = source_artifact.lower()
    artifact_kind = upper(row.get("artifact_kind"))
    row_kind = upper(row.get("row_kind"))

    if "comparison" in src:
        return "app/mme_scalpx/replay/comparison_artifacts.py"
    if "metric" in src:
        return "app/mme_scalpx/replay/metrics.py"
    if "frame" in src:
        return "app/mme_scalpx/replay/frame_export.py"
    if "trade" in src or "ledger" in src or artifact_kind == "TRADE_LOG" or row_kind == "TRADE":
        return "app/mme_scalpx/replay/reports.py or app/mme_scalpx/replay/artifacts.py"
    if "decision" in src or "candidate" in src or "audit" in src:
        return "app/mme_scalpx/replay/artifacts.py or app/mme_scalpx/replay/runner.py"
    if "proof" in src:
        return "proof harness / run/proofs producer"
    if "replay" in src:
        return "app/mme_scalpx/replay/runner.py or app/mme_scalpx/replay/engine.py"
    return "unknown producer"


def missing_field_list(row: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    if upper(row.get("family")) not in FAMILIES:
        missing.append("family")
    if is_unknown(row.get("side")):
        missing.append("side")
    if is_unknown(row.get("strategy_id")):
        missing.append("strategy_id")
    if is_unknown(row.get("source_run_id")):
        missing.append("source_run_id")
    if is_unknown(row.get("event_id")):
        missing.append("event_id")
    if is_unknown(row.get("candidate_id")):
        missing.append("candidate_id")
    return missing


def ast_function_sources(project_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for relpath in PATCH_TARGET_FILES:
        path = project_root / relpath
        if not path.exists() or not path.is_file():
            results.append({
                "file": relpath,
                "exists": False,
                "function": "",
                "lineno": None,
                "score": 0,
                "matched_keywords": [],
            })
            continue

        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            results.append({
                "file": relpath,
                "exists": True,
                "syntax_ok": False,
                "function": "",
                "lineno": None,
                "score": 0,
                "matched_keywords": [],
            })
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            segment = ast.get_source_segment(text, node) or ""
            matched = [kw for kw in PRODUCER_KEYWORDS if kw in segment]
            score = len(matched)
            if score <= 0:
                continue
            results.append({
                "file": relpath,
                "exists": True,
                "syntax_ok": True,
                "function": node.name,
                "lineno": int(node.lineno),
                "end_lineno": int(getattr(node, "end_lineno", node.lineno) or node.lineno),
                "score": score,
                "matched_keywords": matched,
            })

    results.sort(key=lambda x: (x.get("score", 0), x.get("file", ""), x.get("function", "")), reverse=True)
    return results


def choose_patch_target(row: dict[str, Any], producer_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    likely = infer_likely_producer_from_source(norm(row.get("source_artifact")), row)

    exact_files: list[str] = []
    if "reports.py" in likely:
        exact_files.append("app/mme_scalpx/replay/reports.py")
    if "artifacts.py" in likely:
        exact_files.append("app/mme_scalpx/replay/artifacts.py")
    if "runner.py" in likely:
        exact_files.append("app/mme_scalpx/replay/runner.py")
    if "engine.py" in likely:
        exact_files.append("app/mme_scalpx/replay/engine.py")
    if "metrics.py" in likely:
        exact_files.append("app/mme_scalpx/replay/metrics.py")
    if "comparison_artifacts.py" in likely:
        exact_files.append("app/mme_scalpx/replay/comparison_artifacts.py")
    if "frame_export.py" in likely:
        exact_files.append("app/mme_scalpx/replay/frame_export.py")

    if exact_files:
        candidates = [c for c in producer_candidates if c.get("file") in exact_files]
    else:
        candidates = producer_candidates

    if candidates:
        best = max(candidates, key=lambda c: (int(c.get("score", 0) or 0), -int(c.get("lineno", 999999) or 999999)))
        return {
            "target_file": best.get("file", ""),
            "target_function": best.get("function", ""),
            "target_lineno": best.get("lineno"),
            "target_score": best.get("score"),
            "matched_keywords": ",".join(best.get("matched_keywords", [])),
            "patch_reason": "highest static keyword score within likely producer family",
        }

    return {
        "target_file": exact_files[0] if exact_files else "",
        "target_function": "",
        "target_lineno": None,
        "target_score": 0,
        "matched_keywords": "",
        "patch_reason": "likely producer inferred from source artifact but no function detected",
    }


def recommendation_for(row: dict[str, Any], patch_target: dict[str, Any]) -> str:
    missing = missing_field_list(row)
    target_file = patch_target.get("target_file") or "producer source"
    target_function = patch_target.get("target_function") or "row creation function"
    return (
        f"Patch {target_file}:{target_function} to emit {', '.join(missing)} "
        "at original trade/candidate row creation time before RAW backfill."
    )


def build_trace(project_root: Path, rows: list[dict[str, Any]], input_jsonl: str) -> dict[str, Any]:
    trades = [row for row in rows if is_trade_row(row)]
    unknown_trades = [row for row in trades if is_unknown_family_trade(row)]
    producer_candidates = ast_function_sources(project_root)

    trace_rows: list[dict[str, Any]] = []
    producer_counter: Counter[str] = Counter()
    target_counter: Counter[str] = Counter()
    source_counter: Counter[str] = Counter()
    transformation_counter: Counter[str] = Counter()
    missing_counter: Counter[str] = Counter()

    for idx, row in enumerate(unknown_trades, start=1):
        source_artifact = norm(row.get("source_artifact"))
        source_info = source_artifact_info(project_root, source_artifact)
        likely_producer = infer_likely_producer_from_source(source_artifact, row)
        patch_target = choose_patch_target(row, producer_candidates)
        missing = missing_field_list(row)
        transform = probable_transformation_kind(row)

        producer_counter[likely_producer] += 1
        target_key = f"{patch_target.get('target_file')}::{patch_target.get('target_function')}"
        target_counter[target_key] += 1
        source_counter[source_artifact or "UNKNOWN_SOURCE"] += 1
        transformation_counter[transform] += 1
        for field in missing:
            missing_counter[field] += 1

        trace_rows.append({
            "unknown_trade_index": idx,
            "source_artifact": source_artifact,
            "source_exists": source_info["exists"],
            "source_ext": source_info["ext"],
            "source_bytes": source_info["bytes"],
            "source_sha256": source_info["sha256"],
            "source_parent": source_info["parent"],
            "source_run_id": norm(row.get("source_run_id")),
            "row_kind": norm(row.get("row_kind")),
            "artifact_kind": norm(row.get("artifact_kind")),
            "trade_id": norm(row.get("trade_id")),
            "candidate_id": norm(row.get("candidate_id")),
            "event_id": norm(row.get("event_id")),
            "decision_action": norm(row.get("decision_action")),
            "side": norm(row.get("side")),
            "strategy_id": norm(row.get("strategy_id")),
            "family": norm(row.get("family")),
            "net_pnl_after_costs": pnl_value(row),
            "exit_reason": norm(row.get("exit_reason")),
            "raw_p_family_source": norm(row.get("raw_p_family_source")),
            "raw_q_family_source": norm(row.get("raw_q_family_source")),
            "raw_s_family_source": norm(row.get("raw_s_family_source")),
            "raw_u_family_source": norm(row.get("raw_u_family_source")),
            "transformation_kind": transform,
            "likely_producer": likely_producer,
            "target_file": patch_target.get("target_file", ""),
            "target_function": patch_target.get("target_function", ""),
            "target_lineno": patch_target.get("target_lineno"),
            "target_score": patch_target.get("target_score"),
            "matched_keywords": patch_target.get("matched_keywords", ""),
            "missing_fields": ",".join(missing),
            "patch_reason": patch_target.get("patch_reason", ""),
            "recommended_patch": recommendation_for(row, patch_target),
        })

    patch_targets = []
    for key, count in target_counter.most_common():
        target_file, _, target_function = key.partition("::")
        sample = next((r for r in trace_rows if r["target_file"] == target_file and r["target_function"] == target_function), {})
        patch_targets.append({
            "target_file": target_file,
            "target_function": target_function,
            "unknown_trade_count": count,
            "target_lineno": sample.get("target_lineno"),
            "target_score": sample.get("target_score"),
            "matched_keywords": sample.get("matched_keywords"),
            "missing_fields_observed": ",".join(sorted(set(
                field for row in trace_rows
                if row["target_file"] == target_file and row["target_function"] == target_function
                for field in row["missing_fields"].split(",")
                if field
            ))),
            "recommended_patch": sample.get("recommended_patch", ""),
        })

    return {
        "schema_version": RAW_V_SCHEMA_VERSION,
        "generated_utc": utc_now_iso(),
        "input_jsonl": input_jsonl,
        "row_count": len(rows),
        "trade_count": len(trades),
        "unknown_trade_count": len(unknown_trades),
        "unknown_trade_ratio": round(len(unknown_trades) / max(len(trades), 1), 6),
        "producer_counts": dict(producer_counter.most_common()),
        "target_counts": dict(target_counter.most_common()),
        "source_counts": dict(source_counter.most_common()),
        "transformation_counts": dict(transformation_counter.most_common()),
        "missing_field_counts": dict(missing_counter.most_common()),
        "producer_candidates": producer_candidates[:100],
        "trace_rows": trace_rows,
        "producer_patch_targets": patch_targets,
        "lineage_verdict": lineage_verdict(len(trades), len(unknown_trades), patch_targets),
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }


def lineage_verdict(trade_count: int, unknown_count: int, patch_targets: list[dict[str, Any]]) -> str:
    if trade_count <= 0:
        return "NO_TRADE_ROWS_FOUND"
    if unknown_count <= 0:
        return "NO_UNKNOWN_TRADE_ROWS"
    if patch_targets:
        return "PATCH_TARGETS_IDENTIFIED"
    return "UNKNOWN_TRADES_FOUND_TARGETS_INCONCLUSIVE"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def write_markdown(path: Path, trace: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# RAW-V Unknown Trade Lineage Trace")
    lines.append("")
    lines.append(f"Generated UTC: {utc_now_iso()}")
    lines.append("")
    lines.append("## Verdict")
    lines.append(f"- lineage_verdict: {trace['lineage_verdict']}")
    lines.append(f"- promotion_allowed: {trace['promotion_allowed']}")
    lines.append(f"- paper_live_allowed: {trace['paper_live_allowed']}")
    lines.append("")
    lines.append("## Coverage")
    lines.append(f"- trade_count: {trace['trade_count']}")
    lines.append(f"- unknown_trade_count: {trace['unknown_trade_count']}")
    lines.append(f"- unknown_trade_ratio: {trace['unknown_trade_ratio']}")
    lines.append("")
    lines.append("## Producer counts")
    for producer, count in trace["producer_counts"].items():
        lines.append(f"- {producer}: {count}")
    lines.append("")
    lines.append("## Top patch targets")
    for target in trace["producer_patch_targets"][:20]:
        lines.append(
            f"- {target['target_file']}::{target['target_function']} "
            f"unknown_trades={target['unknown_trade_count']} "
            f"missing={target['missing_fields_observed']}"
        )
        lines.append(f"  - {target['recommended_patch']}")
    lines.append("")
    lines.append("## Governance")
    lines.append("RAW-V is lineage trace only. No producer patching, no replay mutation, no paper/live enablement.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_unknown_trade_lineage_trace(
    *,
    input_jsonl: str | Path,
    project_root: str | Path,
    output_dir: str | Path,
    run_id: str,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(input_jsonl)
    trace = build_trace(root, rows, str(input_jsonl))
    trace["run_id"] = run_id

    trace_json = out / TRACE_JSON
    lineage_csv = out / LINEAGE_CSV
    patch_targets_csv = out / PATCH_TARGETS_CSV
    source_artifacts_csv = out / SOURCE_ARTIFACTS_CSV
    summary_md = out / SUMMARY_MD
    manifest = out / MANIFEST_JSON

    trace_for_json = dict(trace)
    trace_rows = trace_for_json.pop("trace_rows")
    patch_targets = trace_for_json.get("producer_patch_targets", [])

    write_json(trace_json, trace_for_json)

    lineage_fields = [
        "unknown_trade_index",
        "source_artifact",
        "source_exists",
        "source_ext",
        "source_bytes",
        "source_sha256",
        "source_parent",
        "source_run_id",
        "row_kind",
        "artifact_kind",
        "trade_id",
        "candidate_id",
        "event_id",
        "decision_action",
        "side",
        "strategy_id",
        "family",
        "net_pnl_after_costs",
        "exit_reason",
        "raw_p_family_source",
        "raw_q_family_source",
        "raw_s_family_source",
        "raw_u_family_source",
        "transformation_kind",
        "likely_producer",
        "target_file",
        "target_function",
        "target_lineno",
        "target_score",
        "matched_keywords",
        "missing_fields",
        "patch_reason",
        "recommended_patch",
    ]
    write_csv(lineage_csv, trace_rows, lineage_fields)

    patch_fields = [
        "target_file",
        "target_function",
        "target_lineno",
        "target_score",
        "unknown_trade_count",
        "matched_keywords",
        "missing_fields_observed",
        "recommended_patch",
    ]
    write_csv(patch_targets_csv, patch_targets, patch_fields)

    source_rows = [
        {"source_artifact": source, "unknown_trade_count": count}
        for source, count in trace["source_counts"].items()
    ]
    write_csv(source_artifacts_csv, source_rows, ["source_artifact", "unknown_trade_count"])

    write_markdown(summary_md, {**trace_for_json, "trace_rows": trace_rows})

    manifest_payload = {
        "schema_version": RAW_V_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "input_jsonl": str(input_jsonl),
        "artifacts": [
            TRACE_JSON,
            LINEAGE_CSV,
            PATCH_TARGETS_CSV,
            SOURCE_ARTIFACTS_CSV,
            SUMMARY_MD,
        ],
        "lineage_verdict": trace["lineage_verdict"],
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }
    write_json(manifest, manifest_payload)

    return {
        "run_id": run_id,
        "output_dir": str(out),
        "trace_json": str(trace_json),
        "lineage_csv": str(lineage_csv),
        "patch_targets_csv": str(patch_targets_csv),
        "source_artifacts_csv": str(source_artifacts_csv),
        "summary_md": str(summary_md),
        "manifest": str(manifest),
        "lineage_verdict": trace["lineage_verdict"],
        "row_count": trace["row_count"],
        "trade_count": trace["trade_count"],
        "unknown_trade_count": trace["unknown_trade_count"],
        "unknown_trade_ratio": trace["unknown_trade_ratio"],
        "producer_counts": trace["producer_counts"],
        "target_counts": trace["target_counts"],
        "missing_field_counts": trace["missing_field_counts"],
        "producer_patch_target_count": len(patch_targets),
        "top_patch_targets": patch_targets[:10],
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
    }
