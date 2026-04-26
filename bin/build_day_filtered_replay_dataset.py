#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    "ticks_mme_fut_stream.csv",
    "ticks_mme_opt_stream.csv",
]

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def event_date_from_value(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("empty ts_event")

    if "-" in raw and ("T" in raw or " " in raw):
        text = raw.replace(" ", "T")
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).date().isoformat()

    n = int(float(raw))
    digits = len(str(abs(n)))
    if digits >= 18:
        seconds = n / 1_000_000_000.0
    elif digits >= 15:
        seconds = n / 1_000_000.0
    elif digits >= 12:
        seconds = n / 1_000.0
    else:
        seconds = float(n)

    return datetime.fromtimestamp(seconds, tz=timezone.utc).date().isoformat()

def find_source_day_dir(src_root: Path) -> Path:
    # The quote-compatible builder wrote one selected day folder, usually 2026-04-21.
    day_dirs = sorted([p for p in src_root.iterdir() if p.is_dir()])
    if not day_dirs:
        raise FileNotFoundError(f"no day directories under {src_root}")
    usable = []
    for d in day_dirs:
        if all((d / f).exists() for f in FILES):
            usable.append(d)
    if not usable:
        raise FileNotFoundError(f"no day directory contains required files under {src_root}")
    return usable[-1]

def split_file(src_file: Path, dst_root: Path, stem_name: str) -> dict[str, Any]:
    writers: dict[str, csv.DictWriter] = {}
    handles: dict[str, Any] = {}
    counts: Counter[str] = Counter()
    bad_rows: list[dict[str, Any]] = []
    header: list[str] = []

    try:
        with src_file.open("r", encoding="utf-8", errors="replace", newline="") as f:
            reader = csv.DictReader(f)
            header = list(reader.fieldnames or [])
            if "ts_event" not in header:
                raise ValueError(f"{src_file} missing ts_event")

            for row_no, row in enumerate(reader, start=2):
                try:
                    day = event_date_from_value(row.get("ts_event"))
                except Exception as exc:
                    if len(bad_rows) < 20:
                        bad_rows.append({
                            "row_no": row_no,
                            "error": repr(exc),
                            "row": {k: row.get(k) for k in list(row.keys())[:20]},
                        })
                    continue

                out_dir = dst_root / day
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = out_dir / stem_name

                if day not in writers:
                    h = out_file.open("w", encoding="utf-8", newline="")
                    handles[day] = h
                    w = csv.DictWriter(h, fieldnames=header)
                    w.writeheader()
                    writers[day] = w

                writers[day].writerow(row)
                counts[day] += 1
    finally:
        for h in handles.values():
            h.close()

    return {
        "source_file": rel(src_file),
        "output_file_name": stem_name,
        "header": header,
        "counts_by_event_date": dict(sorted(counts.items())),
        "bad_row_count": sum(1 for _ in bad_rows),
        "bad_rows_sample": bad_rows,
    }

def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return max(0, sum(1 for _ in f) - 1)

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--src-root", required=True)
    ap.add_argument("--dst-root", required=True)
    args = ap.parse_args()

    src_root = ROOT / args.src_root
    dst_root = ROOT / args.dst_root
    src_day_dir = find_source_day_dir(src_root)

    file_results = []
    for file_name in FILES:
        file_results.append(split_file(src_day_dir / file_name, dst_root, file_name))

    day_summary = {}
    for day_dir in sorted([p for p in dst_root.iterdir() if p.is_dir()]):
        fut = day_dir / "ticks_mme_fut_stream.csv"
        opt = day_dir / "ticks_mme_opt_stream.csv"
        fut_rows = count_rows(fut)
        opt_rows = count_rows(opt)
        total = fut_rows + opt_rows
        day_summary[day_dir.name] = {
            "day_dir": rel(day_dir),
            "fut_rows": fut_rows,
            "opt_rows": opt_rows,
            "total_rows": total,
            "has_fut": fut.exists(),
            "has_opt": opt.exists(),
            "complete_pair": fut.exists() and opt.exists(),
        }

    complete_days = {
        day: info
        for day, info in day_summary.items()
        if info["complete_pair"] and info["total_rows"] > 0
    }

    best_day = None
    if complete_days:
        best_day = max(complete_days.items(), key=lambda kv: kv[1]["total_rows"])[0]

    manifest = {
        "proof_name": "day_filtered_replay_dataset",
        "proof_version": "1",
        "status": "PASS" if best_day else "FAIL",
        "timestamp_ns": time.time_ns(),
        "source_root": args.src_root,
        "source_day_dir": rel(src_day_dir),
        "dest_root": args.dst_root,
        "file_results": file_results,
        "day_summary": day_summary,
        "best_day": best_day,
        "does_not_prove": [
            "market data economic quality",
            "paper armed readiness",
            "live observation readiness",
        ],
    }

    out = dst_root / "day_filtered_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    latest = ROOT / "run/proofs/day_filtered_replay_dataset_latest.json"
    latest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": manifest["status"],
        "source_root": args.src_root,
        "source_day_dir": rel(src_day_dir),
        "dest_root": args.dst_root,
        "day_summary": day_summary,
        "best_day": best_day,
        "manifest": rel(out),
    }, indent=2))

    return 0 if best_day else 1

if __name__ == "__main__":
    raise SystemExit(main())
