#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SESSION_DIRS = [
    ROOT / "run/session_exports/2026-04-17",
    ROOT / "run/session_exports/2026-04-20",
    ROOT / "run/session_exports/2026-04-21",
]

CSV_FILES = []
for d in SESSION_DIRS:
    CSV_FILES.extend(sorted(d.glob("ticks_mme_*_stream.csv")))

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def parse_num(v: str) -> float | None:
    try:
        if v is None or v == "":
            return None
        return float(v)
    except Exception:
        return None

def audit_csv(path: Path, max_rows: int = 250000) -> dict[str, Any]:
    row_count = 0
    header: list[str] = []
    sample_rows: list[dict[str, str]] = []
    nonempty = Counter()
    values = defaultdict(Counter)

    ts_candidates = [
        "ts_event_ns",
        "event_ts_ns",
        "timestamp_ns",
        "ts_ns",
        "time_ns",
        "ts",
        "timestamp",
        "exchange_ts",
        "received_ts",
    ]

    symbol_candidates = [
        "symbol",
        "tradingsymbol",
        "trading_symbol",
        "instrument_key",
        "instrument_token",
        "option_symbol",
        "contract_name",
    ]

    provider_candidates = [
        "provider",
        "broker",
        "broker_name",
        "source",
        "adapter",
    ]

    ts_min = None
    ts_max = None

    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])

        for row in reader:
            row_count += 1

            if len(sample_rows) < 3:
                sample_rows.append({k: (v[:150] if isinstance(v, str) else v) for k, v in row.items()})

            for k, v in row.items():
                if v not in (None, ""):
                    nonempty[k] += 1

            for k in symbol_candidates + provider_candidates:
                if k in row and row.get(k):
                    values[k][row[k]] += 1

            for k in ts_candidates:
                if k in row:
                    n = parse_num(row.get(k, ""))
                    if n is not None:
                        ts_min = n if ts_min is None else min(ts_min, n)
                        ts_max = n if ts_max is None else max(ts_max, n)

            if row_count >= max_rows:
                break

    required_market_fields = {
        "timestamp": any(x in header for x in ts_candidates),
        "provider_or_broker": any(x in header for x in provider_candidates),
        "instrument_identity": any(x in header for x in symbol_candidates),
        "ltp_or_price": any(x in header for x in ["ltp", "last_price", "price", "last_traded_price"]),
        "bid_ask": any(x in header for x in ["best_bid", "bid", "bid_price", "best_ask", "ask", "ask_price"]),
        "depth": any(x in header for x in ["bid_qty", "ask_qty", "best_bid_qty", "best_ask_qty", "bid_qty_5", "ask_qty_5", "depth"]),
    }

    missing_core = [k for k, ok in required_market_fields.items() if not ok]

    return {
        "path": rel(path),
        "size_bytes": path.stat().st_size,
        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(path.stat().st_mtime)),
        "header": header,
        "row_count_sampled": row_count,
        "sample_limited": row_count >= max_rows,
        "nonempty_top": nonempty.most_common(40),
        "identity_values": {
            k: v.most_common(20)
            for k, v in values.items()
        },
        "ts_min": ts_min,
        "ts_max": ts_max,
        "ts_span_raw": None if ts_min is None or ts_max is None else ts_max - ts_min,
        "required_market_fields": required_market_fields,
        "missing_core": missing_core,
        "sample_rows": sample_rows,
    }

def main() -> int:
    audits = []
    for p in CSV_FILES:
        audits.append(audit_csv(p))

    by_date: dict[str, list[dict[str, Any]]] = {}
    for a in audits:
        parts = Path(a["path"]).parts
        date = "unknown"
        for part in parts:
            if part.startswith("2026-"):
                date = part
                break
        by_date.setdefault(date, []).append(a)

    date_pairs = {}
    for date, rows in by_date.items():
        has_fut = any("fut" in Path(r["path"]).name for r in rows)
        has_opt = any("opt" in Path(r["path"]).name for r in rows)
        total_size = sum(r["size_bytes"] for r in rows)
        core_missing = {r["path"]: r["missing_core"] for r in rows if r["missing_core"]}
        date_pairs[date] = {
            "has_fut": has_fut,
            "has_opt": has_opt,
            "file_count": len(rows),
            "total_size_bytes": total_size,
            "core_missing": core_missing,
        }

    result = {
        "proof_name": "session_export_schema_audit",
        "proof_version": "1",
        "status": "PASS",
        "timestamp_ns": time.time_ns(),
        "audits": audits,
        "date_pairs": date_pairs,
        "best_candidate_dates": [
            d for d, x in date_pairs.items()
            if x["has_fut"] and x["has_opt"] and not x["core_missing"]
        ],
        "does_not_prove": [
            "full replay succeeds",
            "features consume this schema directly",
            "market data is semantically clean",
        ],
    }

    out = ROOT / "run/proofs/session_export_schema_audit_latest.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("===== DATE PAIRS =====")
    for d, x in date_pairs.items():
        print(d, x)

    print()
    print("===== FILE AUDITS COMPACT =====")
    for a in audits:
        print()
        print("path:", a["path"])
        print("size:", a["size_bytes"], "rows_sampled:", a["row_count_sampled"])
        print("required_market_fields:", a["required_market_fields"])
        print("missing_core:", a["missing_core"])
        print("header:", ",".join(a["header"][:80]))
        print("identity_values:", a["identity_values"])
        print("sample_row_1:", json.dumps(a["sample_rows"][:1], ensure_ascii=False)[:1200])

    print()
    print("best_candidate_dates:", result["best_candidate_dates"])
    print("artifact: run/proofs/session_export_schema_audit_latest.json")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
