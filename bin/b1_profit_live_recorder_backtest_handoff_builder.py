#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import pathlib
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")

MARKET_HINTS = (
    "ticks:mme:fut",
    "ticks:mme:opt:selected",
    "ticks:mme:opt:context",
    "fut_zerodha",
    "fut_dhan",
    "opt_selected_zerodha",
    "opt_selected_dhan",
    "opt_context_dhan",
)

CORE_STREAM_HINTS = {
    "fut_zerodha": ("ticks:mme:fut:zerodha", "fut_zerodha"),
    "opt_selected_zerodha": ("ticks:mme:opt:selected:zerodha", "opt_selected_zerodha"),
    "features": ("features:mme:stream", "features"),
    "decisions": ("decisions:mme:stream", "decisions"),
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sh(cmd: list[str], timeout: int = 20) -> tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as exc:
        return 999, "", repr(exc)


def pcnt(pattern: str) -> int:
    rc, out, _ = sh(["pgrep", "-af", pattern])
    if rc not in (0, 1):
        return 0
    return len([x for x in out.splitlines() if x.strip() and "grep" not in x])


def redis_xlen(stream: str) -> int:
    rc, out, _ = sh(["redis-cli", "XLEN", stream])
    try:
        return int(out or "0")
    except Exception:
        return -1


def safety() -> dict[str, Any]:
    return {
        "orders": redis_xlen("orders:mme:stream"),
        "risk": redis_xlen("risk:mme:stream"),
        "execution": redis_xlen("execution:mme:stream"),
        "risk_pids": pcnt(r"app\.mme_scalpx\.main --service risk"),
        "execution_pids": pcnt(r"app\.mme_scalpx\.main --service execution"),
    }


def safe_clean(s: dict[str, Any]) -> bool:
    return s == {"orders": 0, "risk": 0, "execution": 0, "risk_pids": 0, "execution_pids": 0}


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def read_json_lines_gz(path: pathlib.Path, max_rows: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    sample: list[dict[str, Any]] = []
    stats: dict[str, Any] = {
        "file": str(path),
        "kind": "jsonl_gz",
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "sha256": sha256_file(path) if path.exists() and path.stat().st_size <= 200_000_000 else "",
        "rows_seen": 0,
        "json_rows": 0,
        "bad_rows": 0,
        "stream_counts": {},
        "first_ts": None,
        "last_ts": None,
        "max_gap_sec_by_stream": {},
        "gap_count_gt_5s_by_stream": {},
        "sample_keys": [],
    }
    stream_counts: Counter[str] = Counter()
    last_ts_by_stream: dict[str, float] = {}
    max_gap_by_stream: defaultdict[str, float] = defaultdict(float)
    gap_count_by_stream: Counter[str] = Counter()
    sample_keys: set[str] = set()

    try:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            for line in f:
                stats["rows_seen"] += 1
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        stats["bad_rows"] += 1
                        continue
                except Exception:
                    stats["bad_rows"] += 1
                    continue

                stats["json_rows"] += 1
                if len(sample) < 3:
                    sample.append(obj)

                for k in obj.keys():
                    if len(sample_keys) < 80:
                        sample_keys.add(str(k))

                stream = str(
                    obj.get("stream")
                    or obj.get("stream_name")
                    or obj.get("redis_stream")
                    or obj.get("label")
                    or obj.get("source")
                    or path.stem
                )
                stream_counts[stream] += 1

                ts_val = (
                    obj.get("ts")
                    or obj.get("timestamp")
                    or obj.get("ts_event_ns")
                    or obj.get("ts_ns")
                    or obj.get("wall_time_ns")
                    or obj.get("created_at")
                )
                ts_float = None
                try:
                    if isinstance(ts_val, (int, float)):
                        if ts_val > 10**15:
                            ts_float = float(ts_val) / 1e9
                        elif ts_val > 10**12:
                            ts_float = float(ts_val) / 1000.0
                        else:
                            ts_float = float(ts_val)
                    elif isinstance(ts_val, str) and ts_val:
                        if ts_val.isdigit():
                            n = int(ts_val)
                            ts_float = n / 1e9 if n > 10**15 else n / 1000.0 if n > 10**12 else float(n)
                        else:
                            ts_float = datetime.fromisoformat(ts_val.replace("Z", "+00:00")).timestamp()
                except Exception:
                    ts_float = None

                if ts_float is not None:
                    if stats["first_ts"] is None or ts_float < stats["first_ts"]:
                        stats["first_ts"] = ts_float
                    if stats["last_ts"] is None or ts_float > stats["last_ts"]:
                        stats["last_ts"] = ts_float
                    if stream in last_ts_by_stream:
                        gap = ts_float - last_ts_by_stream[stream]
                        if gap > max_gap_by_stream[stream]:
                            max_gap_by_stream[stream] = gap
                        if gap > 5:
                            gap_count_by_stream[stream] += 1
                    last_ts_by_stream[stream] = ts_float

                if stats["rows_seen"] >= max_rows:
                    break
    except Exception as exc:
        stats["error"] = repr(exc)

    stats["stream_counts"] = dict(stream_counts)
    stats["max_gap_sec_by_stream"] = {k: round(v, 3) for k, v in max_gap_by_stream.items()}
    stats["gap_count_gt_5s_by_stream"] = dict(gap_count_by_stream)
    stats["sample_keys"] = sorted(sample_keys)

    if stats["first_ts"] is not None:
        stats["first_dt_utc"] = datetime.fromtimestamp(stats["first_ts"], timezone.utc).isoformat()
    if stats["last_ts"] is not None:
        stats["last_dt_utc"] = datetime.fromtimestamp(stats["last_ts"], timezone.utc).isoformat()
    if stats["first_ts"] is not None and stats["last_ts"] is not None:
        stats["duration_sec"] = round(stats["last_ts"] - stats["first_ts"], 3)

    return stats, sample


def inspect_gz_generic(path: pathlib.Path) -> dict[str, Any]:
    stat: dict[str, Any] = {
        "file": str(path),
        "kind": "gz",
        "size_bytes": path.stat().st_size if path.exists() else 0,
        "sha256": sha256_file(path) if path.exists() and path.stat().st_size <= 200_000_000 else "",
        "line_sample_count": 0,
        "first_lines": [],
        "is_probably_jsonl": False,
    }
    try:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if i < 5:
                    stat["first_lines"].append(line[:500].rstrip())
                if line.strip().startswith("{"):
                    stat["is_probably_jsonl"] = True
                stat["line_sample_count"] += 1
                if i >= 100:
                    break
    except Exception as exc:
        stat["error"] = repr(exc)
    return stat


def scan_capture_files(root: pathlib.Path) -> list[pathlib.Path]:
    base = root / "run" / "live_capture"
    if not base.exists():
        return []
    pats = ["*.jsonl.gz", "*.redisraw.gz", "*.gz", "manifest.json", "streams_summary.tsv"]
    seen: dict[str, pathlib.Path] = {}
    for pat in pats:
        for p in base.rglob(pat):
            if p.is_file():
                seen[str(p)] = p
    return sorted(seen.values(), key=lambda p: p.stat().st_mtime, reverse=True)


def infer_candidate_sessions(files: list[pathlib.Path]) -> list[dict[str, Any]]:
    sessions: dict[str, dict[str, Any]] = {}
    for p in files:
        try:
            rel_parent = p.parent.relative_to(ROOT).as_posix()
        except Exception:
            rel_parent = str(p.parent)
        rec = sessions.setdefault(rel_parent, {"dir": rel_parent, "files": [], "total_size_bytes": 0})
        rec["files"].append(p.name)
        rec["total_size_bytes"] += p.stat().st_size
    out = list(sessions.values())
    out.sort(key=lambda x: x["total_size_bytes"], reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--proof", required=True)
    ap.add_argument("--audit-dir", required=True)
    ap.add_argument("--replay-handoff", required=True)
    ap.add_argument("--max-jsonl-rows", type=int, default=250000)
    args = ap.parse_args()

    audit_dir = ROOT / args.audit_dir
    audit_dir.mkdir(parents=True, exist_ok=True)

    before = safety()
    result: dict[str, Any] = {
        "batch": "B1-PROFIT-LIVE-R37I_CONTINUOUS_RECORDER_BACKTEST_HANDOFF_BUILDER_NO_ORDER",
        "tag": args.tag,
        "created_at_utc": now_utc(),
        "source_patch_applied": True,
        "service_start_attempted": False,
        "service_stop_attempted": False,
        "process_kill_attempted": False,
        "redis_delete_attempted": False,
        "redis_write_attempted": False,
        "replay_start_attempted": False,
        "risk_start_attempted": False,
        "execution_start_attempted": False,
        "order_attempted": False,
        "safety_before": before,
    }

    if not safe_clean(before):
        result["classification"] = "BLOCKED_R37I_SAFETY_NOT_CLEAN_NO_ORDER"
        result["safety_after"] = safety()
        pathlib.Path(args.proof).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return 2

    files = scan_capture_files(ROOT)
    sessions = infer_candidate_sessions(files)

    jsonl_stats = []
    jsonl_samples = {}
    gz_stats = []
    for p in files[:200]:
        name = p.name.lower()
        if name.endswith(".jsonl.gz"):
            st, sample = read_json_lines_gz(p, args.max_jsonl_rows)
            jsonl_stats.append(st)
            jsonl_samples[str(p)] = sample
        elif name.endswith(".gz"):
            gz_stats.append(inspect_gz_generic(p))

    recorder_jsonl = [x for x in jsonl_stats if x.get("json_rows", 0) > 0]
    market_jsonl = []
    for x in recorder_jsonl:
        hay = (x.get("file", "") + " " + " ".join(x.get("stream_counts", {}).keys())).lower()
        if any(h.lower() in hay for h in MARKET_HINTS):
            market_jsonl.append(x)

    total_json_rows = sum(int(x.get("json_rows", 0)) for x in recorder_jsonl)
    total_market_rows = sum(int(x.get("json_rows", 0)) for x in market_jsonl)

    has_features = any(
        "features" in (x.get("file", "") + " " + " ".join(x.get("stream_counts", {}).keys())).lower()
        for x in recorder_jsonl
    )
    has_decisions = any(
        "decisions" in (x.get("file", "") + " " + " ".join(x.get("stream_counts", {}).keys())).lower()
        for x in recorder_jsonl
    )
    has_market = total_market_rows > 0

    if has_market and has_features and has_decisions:
        classification = "PASS_R37I_RECORDER_HANDOFF_READY_FOR_OFFLINE_REPLAY_ADMISSION_NO_ORDER"
    elif recorder_jsonl:
        classification = "REVIEW_R37I_RECORDER_JSONL_FOUND_BUT_CORE_COVERAGE_INCOMPLETE_NO_ORDER"
    else:
        classification = "REVIEW_R37I_NO_CONTINUOUS_RECORDER_JSONL_FOUND_YET_BUILDER_READY_NO_ORDER"

    handoff = {
        "tag": args.tag,
        "classification": classification,
        "created_at_utc": now_utc(),
        "purpose": "Replay/backtest admission handoff manifest from continuous recorder outputs. This does not run replay.",
        "candidate_sessions": sessions[:50],
        "recorder_jsonl_files": recorder_jsonl,
        "market_jsonl_files": market_jsonl,
        "generic_gz_files_sample": gz_stats[:80],
        "coverage": {
            "jsonl_files": len(recorder_jsonl),
            "market_jsonl_files": len(market_jsonl),
            "total_json_rows_sampled": total_json_rows,
            "total_market_rows_sampled": total_market_rows,
            "has_market": has_market,
            "has_features": has_features,
            "has_decisions": has_decisions,
        },
        "admission_notes": [
            "Use only if classification is PASS or a later operator accepts incomplete coverage for limited-window replay.",
            "This handoff was built without service start, replay start, Redis write/delete, risk/execution, or order.",
            "If no continuous recorder JSONL is found, next live session must run pauto_start and pseal after market.",
        ],
    }

    pathlib.Path(args.replay_handoff).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.replay_handoff).write_text(json.dumps(handoff, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (audit_dir / "candidate_sessions.json").write_text(json.dumps(sessions[:100], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (audit_dir / "recorder_jsonl_stats.json").write_text(json.dumps(recorder_jsonl, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (audit_dir / "generic_gz_stats.json").write_text(json.dumps(gz_stats[:120], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (audit_dir / "jsonl_samples.json").write_text(json.dumps(jsonl_samples, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    result.update({
        "classification": classification,
        "audit_dir": str(audit_dir.relative_to(ROOT)),
        "replay_handoff_manifest": str(pathlib.Path(args.replay_handoff)),
        "coverage": handoff["coverage"],
        "candidate_session_count": len(sessions),
        "top_candidate_sessions": sessions[:10],
        "safety_after": safety(),
    })

    pathlib.Path(args.proof).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.proof).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
