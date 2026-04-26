#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SEARCH_ROOTS = [
    "run",
    "data",
    "archive",
    "research",
    "recordings",
]

EXCLUDE_PARTS = {
    "proofs",
    "_code_backups",
    "_quarantine",
    "__pycache__",
    ".git",
    ".venv",
}

DATA_SUFFIXES = {
    ".jsonl",
    ".ndjson",
    ".json",
    ".csv",
    ".parquet",
    ".pq",
    ".log",
}

STRONG_MARKET_KEYWORDS = [
    "tick",
    "ticks",
    "depth",
    "quote",
    "quotes",
    "ltp",
    "feed",
    "feeds",
    "market",
    "marketdata",
    "option",
    "options",
    "chain",
    "dhan",
    "zerodha",
    "nifty",
    "fut",
    "future",
    "instrument",
    "raw",
    "capture",
    "recording",
    "session",
]

PROOF_NOISE_KEYWORDS = [
    "proof",
    "freeze",
    "milestone",
    "bundle",
    "readiness_inventory",
    "final_freeze",
]

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def excluded(p: Path) -> bool:
    try:
        rp = p.relative_to(ROOT)
    except Exception:
        return True
    return bool(set(rp.parts) & EXCLUDE_PARTS)

def score_file(p: Path) -> int:
    s = rel(p).lower()
    score = 0

    for k in STRONG_MARKET_KEYWORDS:
        if k in s:
            score += 2

    for k in PROOF_NOISE_KEYWORDS:
        if k in s:
            score -= 5

    if "research_capture" in s:
        score += 5
    if "raw" in s:
        score += 4
    if "archive" in s:
        score += 3
    if "record" in s:
        score += 3
    if "session" in s:
        score += 2
    if p.suffix.lower() in {".parquet", ".pq"}:
        score += 5
    if p.suffix.lower() in {".jsonl", ".ndjson"}:
        score += 4
    if p.suffix.lower() == ".csv":
        score += 2

    try:
        size = p.stat().st_size
        if size > 10_000_000:
            score += 5
        elif size > 1_000_000:
            score += 4
        elif size > 100_000:
            score += 2
        elif size < 100:
            score -= 2
    except OSError:
        pass

    return score

def head_lines(p: Path, n: int = 5) -> list[str]:
    if p.suffix.lower() not in {".jsonl", ".ndjson", ".json", ".csv", ".log"}:
        return []
    out: list[str] = []
    try:
        with p.open("r", encoding="utf-8", errors="replace") as f:
            for _ in range(n):
                line = f.readline()
                if not line:
                    break
                out.append(line[:700].rstrip())
    except Exception as exc:
        out.append(f"HEAD_READ_ERROR: {exc!r}")
    return out

def main() -> int:
    rows: list[dict[str, Any]] = []

    for root in SEARCH_ROOTS:
        base = ROOT / root
        if not base.exists():
            continue

        for p in base.rglob("*"):
            if not p.is_file() or excluded(p):
                continue
            if p.suffix.lower() not in DATA_SUFFIXES:
                continue

            sc = score_file(p)
            if sc <= 0:
                continue

            st = p.stat()
            rows.append({
                "path": rel(p),
                "score": sc,
                "size_bytes": st.st_size,
                "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
                "suffix": p.suffix.lower(),
                "head": head_lines(p),
            })

    rows.sort(key=lambda x: (x["score"], x["size_bytes"], x["mtime"]), reverse=True)

    result = {
        "proof_name": "recorded_live_data_clean_inventory",
        "proof_version": "1",
        "status": "PASS",
        "timestamp_ns": time.time_ns(),
        "candidate_count": len(rows),
        "top_candidates": rows[:100],
        "largest_candidates": sorted(rows, key=lambda x: x["size_bytes"], reverse=True)[:50],
        "does_not_prove": [
            "data is semantically valid",
            "data is replay-compatible",
            "replay succeeds",
        ],
    }

    out = ROOT / "run/proofs/recorded_live_data_clean_inventory_latest.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("candidate_count:", len(rows))
    print()
    print("TOP 40 REAL DATA CANDIDATES")
    for r in rows[:40]:
        print(f"- score={r['score']} size={r['size_bytes']} mtime={r['mtime']} path={r['path']}")
        for h in r.get("head", [])[:2]:
            print("  head:", h[:250])

    print()
    print("LARGEST 20 CANDIDATES")
    for r in result["largest_candidates"][:20]:
        print(f"- size={r['size_bytes']} score={r['score']} path={r['path']}")

    print()
    print("artifact: run/proofs/recorded_live_data_clean_inventory_latest.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
