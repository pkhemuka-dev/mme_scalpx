#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_DIRS = [
    "run",
    "run/recordings",
    "run/research",
    "run/research_capture",
    "run/archive",
    "run/data",
    "data",
    "archive",
    "research",
    "recordings",
]

DATA_SUFFIXES = {
    ".jsonl",
    ".json",
    ".csv",
    ".parquet",
    ".pq",
    ".ndjson",
    ".log",
}

REPLAY_TOOLS = [
    "bin/replay_run.py",
    "bin/replay_compare.py",
    "bin/replay_export_frames_real.py",
    "bin/replay_export_frames_smoke.py",
    "bin/replay_build_comparison_summary.py",
    "bin/proof_replay_engine_contracts.py",
    "bin/proof_replay_batch16_freeze.py",
]

KEYWORDS = [
    "tick",
    "ticks",
    "feed",
    "feeds",
    "zerodha",
    "dhan",
    "nifty",
    "option",
    "fut",
    "future",
    "depth",
    "chain",
    "context",
    "research",
    "capture",
    "replay",
]

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def safe_stat(p: Path) -> dict[str, Any]:
    try:
        st = p.stat()
        return {
            "path": rel(p),
            "size_bytes": st.st_size,
            "mtime_ns": st.st_mtime_ns,
            "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
            "suffix": p.suffix.lower(),
        }
    except OSError as exc:
        return {"path": rel(p), "error": repr(exc)}

def head_lines(p: Path, n: int = 3) -> list[str]:
    out: list[str] = []
    try:
        with p.open("r", encoding="utf-8", errors="replace") as f:
            for _ in range(n):
                line = f.readline()
                if not line:
                    break
                out.append(line[:500].rstrip())
    except Exception:
        pass
    return out

def sh(cmd: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        return {
            "cmd": cmd,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-8000:],
            "stderr": proc.stderr[-8000:],
        }
    except Exception as exc:
        return {"cmd": cmd, "error": repr(exc)}

def main() -> int:
    files: list[dict[str, Any]] = []

    for d in CANDIDATE_DIRS:
        base = ROOT / d
        if not base.exists():
            continue

        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in DATA_SUFFIXES:
                continue

            path_text = str(p).lower()
            if not any(k in path_text for k in KEYWORDS):
                continue

            item = safe_stat(p)
            if p.suffix.lower() in {".jsonl", ".json", ".csv", ".ndjson", ".log"}:
                item["head"] = head_lines(p)
            files.append(item)

    files.sort(key=lambda x: x.get("mtime_ns", 0), reverse=True)

    replay_tools = []
    for t in REPLAY_TOOLS:
        p = ROOT / t
        replay_tools.append({
            "path": t,
            "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else 0,
        })

    proof_scripts = sorted(rel(p) for p in (ROOT / "bin").glob("proof_*replay*.py"))
    research_scripts = sorted(rel(p) for p in (ROOT / "bin").glob("*research*"))

    result = {
        "proof_name": "recorded_live_replay_readiness_inventory",
        "proof_version": "1",
        "status": "PASS",
        "timestamp_ns": time.time_ns(),
        "market_status": "CLOSED_ASSUMED_BY_OPERATOR",
        "writes_live_redis": False,
        "places_orders": False,
        "uses_broker": False,
        "candidate_data_file_count": len(files),
        "candidate_data_files_top_80": files[:80],
        "largest_candidate_files_top_30": sorted(files, key=lambda x: x.get("size_bytes", 0), reverse=True)[:30],
        "replay_tools": replay_tools,
        "proof_scripts_replay": proof_scripts,
        "research_scripts": research_scripts,
        "git_status_short": sh(["git", "status", "--short"]),
        "does_not_prove": [
            "recorded data is semantically valid",
            "full replay succeeds",
            "live observation readiness",
            "paper armed readiness",
        ],
        "next_recommended_step": (
            "Choose best recorded data source from candidate_data_files_top_80, "
            "then run a replay dry-run/integration audit against replay namespace only."
        ),
    }

    out = ROOT / "run/proofs/recorded_live_replay_readiness_latest.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": result["status"],
        "candidate_data_file_count": result["candidate_data_file_count"],
        "replay_tools_available": [x for x in replay_tools if x["exists"]],
        "top_candidate_files": [
            {
                "path": x["path"],
                "size_bytes": x.get("size_bytes"),
                "mtime": x.get("mtime"),
            }
            for x in files[:20]
        ],
        "artifact": rel(out),
    }, indent=2))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
