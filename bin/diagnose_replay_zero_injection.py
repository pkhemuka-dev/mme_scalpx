#!/usr/bin/env python3
from __future__ import annotations

import ast
import csv
import json
import re
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

FILES_TO_SCAN = [
    "bin/replay_run.py",
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/injector.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/selectors.py",
    "app/mme_scalpx/replay/clock.py",
    "app/mme_scalpx/replay/contracts.py",
]

KEY_PATTERNS = [
    "required_file_stems",
    "supported_suffixes",
    "csv",
    "DictReader",
    "ts_event",
    "timestamp",
    "datetime",
    "fromtimestamp",
    "clock_start",
    "window_start",
    "window_end",
    "session",
    "inject",
    "injected_count",
    "total_injected",
    "source_mode",
    "quote_only_recorded",
    "economics_enriched_recorded",
    "row_count",
    "selection_mode",
]

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def read(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def grep_context(path: str, patterns: list[str], radius: int = 3) -> list[dict[str, Any]]:
    text = read(path)
    lines = text.splitlines()
    hits = []
    for i, line in enumerate(lines):
        low = line.lower()
        if any(p.lower() in low for p in patterns):
            start = max(0, i - radius)
            end = min(len(lines), i + radius + 1)
            hits.append({
                "path": path,
                "line_no": i + 1,
                "line": line[:300],
                "context": lines[start:end],
            })
    return hits[:120]

def audit_csv(path: Path, max_rows: int = 5) -> dict[str, Any]:
    rows = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        for idx, row in enumerate(reader):
            if idx >= max_rows:
                break
            rows.append(row)

    # Also count total quickly
    total = 0
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        total = max(0, sum(1 for _ in f) - 1)

    return {
        "path": rel(path),
        "header": header,
        "row_count": total,
        "sample_rows": rows,
        "ts_event_values": [r.get("ts_event") for r in rows],
        "symbol_values": [r.get("symbol") for r in rows],
    }

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--compat-root", required=True)
    ap.add_argument("--day", required=True)
    args = ap.parse_args()

    compat_root = ROOT / args.compat_root
    day_dir = compat_root / args.day

    csv_audits = []
    for name in ["ticks_mme_fut_stream.csv", "ticks_mme_opt_stream.csv"]:
        p = day_dir / name
        csv_audits.append(audit_csv(p) if p.exists() else {"path": rel(p), "missing": True})

    grep_hits = {}
    for f in FILES_TO_SCAN:
        grep_hits[f] = grep_context(f, KEY_PATTERNS)

    result = {
        "proof_name": "replay_zero_injection_diagnosis",
        "proof_version": "1",
        "status": "PASS",
        "timestamp_ns": time.time_ns(),
        "compat_root": args.compat_root,
        "day": args.day,
        "csv_audits": csv_audits,
        "grep_hits": grep_hits,
        "hypotheses": [
            "replay feed injector may only read canonical file stems different from ticks_mme_*",
            "replay feed injector may require JSON/JSONL not CSV despite dataset accepting CSV",
            "replay feed injector may filter by clock/window and timestamps are nanoseconds not ISO/datetime",
            "replay feed injector may require ts_event in seconds/ISO while CSV uses ns",
            "replay clock default may be 2026-04-17 while selected day is 2026-04-21",
        ],
        "does_not_prove": [
            "exact patch needed",
            "replay success",
        ],
    }

    out = ROOT / "run/proofs/replay_zero_injection_diagnosis_latest.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("===== CSV AUDITS =====")
    for a in csv_audits:
        print(json.dumps({
            "path": a.get("path"),
            "missing": a.get("missing", False),
            "header": a.get("header"),
            "row_count": a.get("row_count"),
            "ts_event_values": a.get("ts_event_values"),
            "symbol_values": a.get("symbol_values"),
            "sample_rows": a.get("sample_rows", [])[:1],
        }, indent=2)[:4000])

    print()
    print("===== CODE CONTEXT HITS COMPACT =====")
    for f, hits in grep_hits.items():
        print()
        print("###", f, "hit_count=", len(hits))
        for h in hits[:25]:
            print(f"L{h['line_no']}: {h['line']}")

    print()
    print("artifact: run/proofs/replay_zero_injection_diagnosis_latest.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
