#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SOURCE_TO_DEST = {
    "ts_event_ns": "ts_event",
    "trading_symbol": "symbol",
    "best_bid": "bid",
    "best_ask": "ask",
}

EXTRA_ALIASES = {
    "ts_exchange_ns": "ts_exchange",
    "ts_recv_ns": "ts_recv",
    "ltp": "ltp",
    "provider": "provider",
    "instrument_token": "instrument_token",
    "selection_role": "selection_role",
    "bid_qty_5": "bid_qty",
    "ask_qty_5": "ask_qty",
    "strike": "strike",
    "spread": "spread",
    "mid": "mid",
    "validity": "validity",
    "validity_reason": "validity_reason",
}

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def convert_file(src: Path, dst: Path) -> dict[str, Any]:
    dst.parent.mkdir(parents=True, exist_ok=True)

    row_count = 0
    bad_rows = 0
    sample_out = []

    with src.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        src_header = list(reader.fieldnames or [])

        required_src = list(SOURCE_TO_DEST.keys())
        missing_src = [x for x in required_src if x not in src_header]
        if missing_src:
            raise ValueError(f"{src} missing source columns {missing_src}")

        canonical_cols = ["ts_event", "symbol", "bid", "ask"]
        alias_cols = [v for k, v in EXTRA_ALIASES.items() if k in src_header and v not in canonical_cols]
        passthrough_cols = [c for c in src_header if c not in SOURCE_TO_DEST and c not in EXTRA_ALIASES]
        out_header = canonical_cols + alias_cols + passthrough_cols

        with dst.open("w", encoding="utf-8", newline="") as g:
            writer = csv.DictWriter(g, fieldnames=out_header)
            writer.writeheader()

            for row in reader:
                out = {}

                for src_col, dst_col in SOURCE_TO_DEST.items():
                    out[dst_col] = row.get(src_col, "")

                for src_col, dst_col in EXTRA_ALIASES.items():
                    if src_col in src_header and dst_col in out_header:
                        out[dst_col] = row.get(src_col, "")

                for c in passthrough_cols:
                    out[c] = row.get(c, "")

                if not out.get("ts_event") or not out.get("symbol") or not out.get("bid") or not out.get("ask"):
                    bad_rows += 1

                if len(sample_out) < 3:
                    sample_out.append(dict(out))

                writer.writerow(out)
                row_count += 1

    return {
        "src": rel(src),
        "dst": rel(dst),
        "src_size_bytes": src.stat().st_size,
        "dst_size_bytes": dst.stat().st_size,
        "row_count": row_count,
        "bad_rows": bad_rows,
        "sample_out": sample_out,
    }

def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--src-root", required=True)
    ap.add_argument("--src-day", required=True)
    ap.add_argument("--dst-root", required=True)
    args = ap.parse_args()

    src_dir = ROOT / args.src_root / args.src_day
    dst_dir = ROOT / args.dst_root / args.src_day

    files = [
        "ticks_mme_fut_stream.csv",
        "ticks_mme_opt_stream.csv",
    ]

    results = []
    for name in files:
        src = src_dir / name
        dst = dst_dir / name
        if not src.exists():
            raise FileNotFoundError(src)
        results.append(convert_file(src, dst))

    failed = [r for r in results if r["bad_rows"] > 0 or r["row_count"] <= 0]

    manifest = {
        "proof_name": "replay_quote_compat_dataset",
        "proof_version": "1",
        "status": "PASS" if not failed else "FAIL",
        "timestamp_ns": time.time_ns(),
        "source_root": args.src_root,
        "source_day": args.src_day,
        "dest_root": args.dst_root,
        "dest_day": args.src_day,
        "files": results,
        "failed": failed,
        "canonical_mapping": SOURCE_TO_DEST,
        "does_not_prove": [
            "full replay succeeds",
            "features accept replay rows semantically",
            "strategy candidates are meaningful",
        ],
    }

    out = ROOT / args.dst_root / args.src_day / "replay_quote_compat_manifest.json"
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(json.dumps(manifest, indent=2))
    return 0 if not failed else 1

if __name__ == "__main__":
    raise SystemExit(main())
