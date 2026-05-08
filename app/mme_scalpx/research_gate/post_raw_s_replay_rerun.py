"""RAW-T post-RAW-S replay-only rerun orchestrator.

Runs a post-RAW-S replay evidence export, then RAW-N/Q/R equivalent reruns.
Review only. No broker IO. No Redis. No orders. No live/paper enablement.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RAW_T_SCHEMA_VERSION = "RAW-T.1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_json_command(cmd: list[str]) -> dict[str, Any]:
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Command did not return JSON: {cmd}\nSTDOUT={result.stdout}\nSTDERR={result.stderr}") from exc


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp, path)


def run_post_raw_s_rerun(
    *,
    project_root: str | Path,
    run_id: str,
    output_dir: str | Path,
    replay_export_dir: str | Path,
    raw_n_before_dir: str | Path,
    raw_q_dir: str | Path,
    raw_n_after_dir: str | Path,
    raw_r_dir: str | Path,
    old_raw_j_proof: str | Path,
    old_raw_m_proof: str | Path,
    baseline_raw_q_proof: str | Path,
    baseline_raw_r_proof: str | Path,
    max_files: int = 150,
    max_rows_per_file: int = 8000,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    out = Path(output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    replay_export_dir = Path(replay_export_dir).resolve()
    raw_n_before_dir = Path(raw_n_before_dir).resolve()
    raw_q_dir = Path(raw_q_dir).resolve()
    raw_n_after_dir = Path(raw_n_after_dir).resolve()
    raw_r_dir = Path(raw_r_dir).resolve()

    replay_export_dir.mkdir(parents=True, exist_ok=True)
    raw_n_before_dir.mkdir(parents=True, exist_ok=True)
    raw_q_dir.mkdir(parents=True, exist_ok=True)
    raw_n_after_dir.mkdir(parents=True, exist_ok=True)
    raw_r_dir.mkdir(parents=True, exist_ok=True)

    replay_probe = root / "bin" / "replay_true_family_enrich_probe.py"
    raw_n_cli = root / "bin" / "raw_enriched_rerun.py"
    raw_q_cli = root / "bin" / "replay_trade_family_backfill.py"
    raw_r_cli = root / "bin" / "raw_family_gap_review.py"

    missing = [str(p) for p in [replay_probe, raw_n_cli, raw_q_cli, raw_r_cli] if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required RAW-T command(s): {missing}")

    export_cmd = [
        sys.executable,
        str(replay_probe),
        "--project-root",
        str(root),
        "--output-dir",
        str(replay_export_dir),
        "--run-id",
        run_id,
        "--max-files",
        str(max_files),
        "--max-rows-per-file",
        str(max_rows_per_file),
    ]
    export_result = run_json_command(export_cmd)
    enriched_jsonl = replay_export_dir / "enriched_replay_records.jsonl"
    if not enriched_jsonl.exists():
        raise FileNotFoundError(f"Post-RAW-S enriched output missing: {enriched_jsonl}")

    raw_n_before_cmd = [
        sys.executable,
        str(raw_n_cli),
        "--enriched-jsonl",
        str(enriched_jsonl),
        "--output-dir",
        str(raw_n_before_dir),
        "--run-id",
        f"{run_id}_raw_n_before",
        "--old-raw-j-proof",
        str(old_raw_j_proof),
        "--old-raw-m-proof",
        str(old_raw_m_proof),
    ]
    raw_n_before_result = run_json_command(raw_n_before_cmd)

    raw_q_cmd = [
        sys.executable,
        str(raw_q_cli),
        "--input-jsonl",
        str(enriched_jsonl),
        "--output-dir",
        str(raw_q_dir),
        "--run-id",
        f"{run_id}_raw_q",
    ]
    raw_q_result = run_json_command(raw_q_cmd)
    backfilled_jsonl = raw_q_dir / "trade_family_backfilled_records.jsonl"
    if not backfilled_jsonl.exists():
        raise FileNotFoundError(f"RAW-Q backfilled output missing: {backfilled_jsonl}")

    raw_n_after_cmd = [
        sys.executable,
        str(raw_n_cli),
        "--enriched-jsonl",
        str(backfilled_jsonl),
        "--output-dir",
        str(raw_n_after_dir),
        "--run-id",
        f"{run_id}_raw_n_after",
        "--old-raw-j-proof",
        str(old_raw_j_proof),
        "--old-raw-m-proof",
        str(old_raw_m_proof),
    ]
    raw_n_after_result = run_json_command(raw_n_after_cmd)

    raw_r_cmd = [
        sys.executable,
        str(raw_r_cli),
        "--input-jsonl",
        str(backfilled_jsonl),
        "--output-dir",
        str(raw_r_dir),
        "--run-id",
        f"{run_id}_raw_r",
    ]
    raw_r_result = run_json_command(raw_r_cmd)

    baseline_q = read_json(baseline_raw_q_proof)
    baseline_r = read_json(baseline_raw_r_proof)
    after_r = read_json(raw_r_dir / "family_pnl_review.json")
    after_q_summary = read_json(raw_q_dir / "trade_family_backfill_summary.json")

    before_unknown_ratio = baseline_r.get("unknown_family_ratio")
    after_unknown_ratio = after_r.get("unknown_family_ratio")
    unknown_ratio_delta = None
    if isinstance(before_unknown_ratio, (int, float)) and isinstance(after_unknown_ratio, (int, float)):
        unknown_ratio_delta = round(float(after_unknown_ratio) - float(before_unknown_ratio), 6)

    comparison = {
        "schema_version": RAW_T_SCHEMA_VERSION,
        "generated_utc": utc_now_iso(),
        "baseline_raw_q": {
            "trade_count": baseline_q.get("trade_count"),
            "trade_family_after_count": baseline_q.get("trade_family_after_count"),
            "trade_family_unknown_ratio_after": baseline_q.get("trade_family_unknown_ratio_after"),
            "rank_verdict": baseline_q.get("rank_verdict"),
        },
        "baseline_raw_r": {
            "review_verdict": baseline_r.get("review_verdict"),
            "trade_count": baseline_r.get("trade_count"),
            "known_family_trade_count": baseline_r.get("known_family_trade_count"),
            "unknown_family_trade_count": baseline_r.get("unknown_family_trade_count"),
            "unknown_family_ratio": baseline_r.get("unknown_family_ratio"),
            "rank_candidate_family_count": baseline_r.get("rank_candidate_family_count"),
        },
        "post_raw_s_raw_q": {
            "trade_count": after_q_summary.get("trade_count"),
            "trade_family_before_count": after_q_summary.get("trade_family_before_count"),
            "trade_family_after_count": after_q_summary.get("trade_family_after_count"),
            "trade_backfilled_count": after_q_summary.get("trade_backfilled_count"),
            "trade_family_unknown_ratio_after": after_q_summary.get("trade_family_unknown_ratio_after"),
            "rank_candidate_family_count": after_q_summary.get("rank_candidate_family_count"),
        },
        "post_raw_s_raw_r": {
            "review_verdict": after_r.get("review_verdict"),
            "trade_count": after_r.get("trade_count"),
            "known_family_trade_count": after_r.get("known_family_trade_count"),
            "unknown_family_trade_count": after_r.get("unknown_family_trade_count"),
            "unknown_family_ratio": after_r.get("unknown_family_ratio"),
            "rank_candidate_family_count": after_r.get("rank_candidate_family_count"),
            "best_family": after_r.get("best_family"),
            "worst_family": after_r.get("worst_family"),
            "likely_producer_counts": after_r.get("likely_producer_counts"),
        },
        "unknown_family_ratio_delta_after_minus_before": unknown_ratio_delta,
        "coverage_improved": (
            isinstance(unknown_ratio_delta, (int, float)) and unknown_ratio_delta < 0
        ),
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }

    write_json(out / "raw_t_before_after_family_coverage_comparison.json", comparison)

    manifest = {
        "schema_version": RAW_T_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "export_mode": "post_raw_s_replay_true_family_enrich_probe",
        "artifacts": {
            "replay_export_dir": str(replay_export_dir),
            "raw_n_before_dir": str(raw_n_before_dir),
            "raw_q_dir": str(raw_q_dir),
            "raw_n_after_dir": str(raw_n_after_dir),
            "raw_r_dir": str(raw_r_dir),
            "comparison": str(out / "raw_t_before_after_family_coverage_comparison.json"),
        },
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
    }
    write_json(out / "manifest.json", manifest)

    return {
        "schema_version": RAW_T_SCHEMA_VERSION,
        "run_id": run_id,
        "output_dir": str(out),
        "export_mode": "post_raw_s_replay_true_family_enrich_probe",
        "export_result": export_result,
        "raw_n_before_result": raw_n_before_result,
        "raw_q_result": raw_q_result,
        "raw_n_after_result": raw_n_after_result,
        "raw_r_result": raw_r_result,
        "comparison": comparison,
        "manifest": str(out / "manifest.json"),
        "comparison_path": str(out / "raw_t_before_after_family_coverage_comparison.json"),
        "promotion_allowed": False,
        "paper_live_allowed": False,
        "non_live": True,
        "non_mutating": True,
        "broker_io_added": False,
        "redis_live_writer_added": False,
        "order_sending_added": False,
    }
