#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "run/proofs/proof_aftermarket_strong_replay_sample.json"
EVENTS_OUT = ROOT / "run/replay/batch23_strong_replay_sample_events.jsonl"

MIN_EVENTS_TOTAL = int(os.environ.get("MME_BATCH23_MIN_EVENTS_TOTAL", "150"))
MIN_KINDS = int(os.environ.get("MME_BATCH23_MIN_KINDS", "3"))
MAX_ROWS_PER_FILE = int(os.environ.get("MME_BATCH23_MAX_ROWS_PER_FILE", "300"))

DATA_ROOTS = [
    ROOT / "run/research_capture",
    ROOT / "run/replay",
    ROOT / "run/recordings",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)


def sha256_file(path: Path, max_bytes: int = 2_000_000) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        left = max_bytes
        while left > 0:
            chunk = f.read(min(65536, left))
            if not chunk:
                break
            h.update(chunk)
            left -= len(chunk)
    return h.hexdigest()


def kind_of(p: Path) -> str:
    s = str(p).lower()
    if "ticks_fut" in s or "instrument_type=fut" in s:
        return "FUT"
    if "option_type=ce" in s or "instrument_type=ce" in s:
        return "CE"
    if "option_type=pe" in s or "instrument_type=pe" in s:
        return "PE"
    if "features_rows" in s:
        return "FEATURE_ROWS"
    if "ticks_opt" in s:
        return "OPT"
    return "UNKNOWN"


def date_of(p: Path) -> str:
    s = str(p)
    m = re.search(r"/(20\d{2}-\d{2}-\d{2})/", s)
    if m:
        return m.group(1)
    m = re.search(r"(20\d{6})", s)
    if m:
        raw = m.group(1)
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
    return "unknown"


def discover() -> list[Path]:
    out = []
    for root in DATA_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.stat().st_size <= 0:
                continue
            name = p.name.lower()
            if name.endswith((".parquet", ".jsonl", ".ndjson", ".csv", ".json", ".gz")):
                if "/run/proofs/" not in str(p):
                    out.append(p)
    return sorted(out)


def read_rows(p: Path, limit: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    suffixes = "".join(p.suffixes).lower()
    meta: dict[str, Any] = {"reader": None, "error": None, "columns": [], "rows": 0}

    try:
        if suffixes.endswith(".parquet"):
            import pandas as pd  # type: ignore
            df = pd.read_parquet(p)
            df = df.head(limit)
            rows = json.loads(df.to_json(orient="records", date_format="iso"))
            meta.update({"reader": "parquet", "columns": list(map(str, df.columns)), "rows": len(rows)})
            return rows, meta

        opener = gzip.open if suffixes.endswith(".gz") else open
        mode = "rt" if suffixes.endswith(".gz") else "r"

        if ".jsonl" in suffixes or ".ndjson" in suffixes:
            rows = []
            with opener(p, mode, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if len(rows) >= limit:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if isinstance(obj, dict):
                        rows.append(obj)
            meta.update({"reader": "jsonl", "columns": sorted({k for r in rows for k in r}), "rows": len(rows)})
            return rows, meta

        if suffixes.endswith(".json"):
            data = json.loads(p.read_text(errors="replace"))
            if isinstance(data, list):
                rows = [x for x in data if isinstance(x, dict)][:limit]
            elif isinstance(data, dict):
                rows = []
                for k in ("rows", "events", "data", "features", "records"):
                    if isinstance(data.get(k), list):
                        rows = [x for x in data[k] if isinstance(x, dict)][:limit]
                        break
                if not rows:
                    rows = [data]
            else:
                rows = []
            meta.update({"reader": "json", "columns": sorted({k for r in rows for k in r}), "rows": len(rows)})
            return rows, meta

        if suffixes.endswith(".csv") or suffixes.endswith(".csv.gz"):
            rows = []
            with opener(p, mode, encoding="utf-8", errors="replace", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if len(rows) >= limit:
                        break
                    rows.append(dict(row))
            meta.update({"reader": "csv", "columns": sorted({k for r in rows for k in r}), "rows": len(rows)})
            return rows, meta

    except Exception as exc:
        meta["reader"] = "failed"
        meta["error"] = repr(exc)
        return [], meta

    meta["reader"] = "unsupported"
    return [], meta


def first_key(row: dict[str, Any], needles: tuple[str, ...]) -> str | None:
    low = {str(k).lower(): str(k) for k in row}
    for n in needles:
        for lk, orig in low.items():
            if n in lk:
                return orig
    return None


def event_for(kind: str, p: Path, idx: int, row: dict[str, Any]) -> dict[str, Any]:
    if kind == "FUT":
        channel = "replay:ticks:mme:fut:stream"
    elif kind in {"CE", "PE", "OPT"}:
        channel = "replay:ticks:mme:opt:stream"
    elif kind == "FEATURE_ROWS":
        channel = "replay:features:mme:stream"
    else:
        channel = "replay:local:unknown"

    ts_key = first_key(row, ("ts_event_ns", "timestamp_ns", "exchange_ts", "timestamp", "time", "ts"))
    px_key = first_key(row, ("ltp", "last_price", "price", "mid", "close", "bid", "ask"))
    sym_key = first_key(row, ("instrument_key", "symbol", "tradingsymbol", "trading_symbol", "security_id", "token"))

    return {
        "channel": channel,
        "source_file": rel(p),
        "source_kind": kind,
        "source_row_index": idx,
        "ts_key": ts_key,
        "price_key": px_key,
        "symbol_key": sym_key,
        "ts_value": row.get(ts_key) if ts_key else None,
        "price_value": row.get(px_key) if px_key else None,
        "symbol_value": row.get(sym_key) if sym_key else None,
        "raw_keys": sorted(map(str, row.keys()))[:80],
        "payload_json": json.dumps(row, sort_keys=True, default=str),
    }


def pick_files(candidates: list[Path]) -> tuple[str | None, list[Path]]:
    grouped: dict[str, dict[str, list[Path]]] = {}
    for p in candidates:
        grouped.setdefault(date_of(p), {}).setdefault(kind_of(p), []).append(p)

    # Prefer a date with FUT + CE + PE.
    for d in sorted(grouped.keys(), reverse=True):
        g = grouped[d]
        if g.get("FUT") and g.get("CE") and g.get("PE"):
            return d, [g["FUT"][0], g["CE"][0], g["PE"][0]]

    # Fallback: any three useful files from same date.
    for d in sorted(grouped.keys(), reverse=True):
        selected = []
        for k in ("FUT", "CE", "PE", "OPT", "FEATURE_ROWS"):
            selected.extend(grouped[d].get(k, [])[:1])
        if selected:
            return d, selected[:3]

    return None, []


def main() -> int:
    candidates = discover()
    selected_date, selected = pick_files(candidates)

    file_results = []
    events = []
    findings = []

    for p in selected:
        k = kind_of(p)
        rows, meta = read_rows(p, MAX_ROWS_PER_FILE)
        item = {
            "path": rel(p),
            "kind": k,
            "date": date_of(p),
            "bytes": p.stat().st_size,
            "sha256_first_2mb": sha256_file(p),
            "reader": meta.get("reader"),
            "error": meta.get("error"),
            "columns": meta.get("columns", [])[:120],
            "row_count_sampled": meta.get("rows", 0),
        }

        if not rows:
            item["status"] = "FAIL"
            findings.append({
                "severity": "P1",
                "owner": "replay/data",
                "finding": "selected file produced zero readable rows",
                "path": rel(p),
                "reader": meta.get("reader"),
                "error": meta.get("error"),
            })
        else:
            item["status"] = "PASS"
            for i, row in enumerate(rows):
                events.append(event_for(k, p, i, row))

        file_results.append(item)

    channels = sorted({str(e["channel"]) for e in events})
    kinds = sorted({str(e["source_kind"]) for e in events})
    replay_only = bool(channels) and all(ch.startswith("replay:") for ch in channels)

    missing_ts = sum(1 for e in events if e.get("ts_value") in (None, ""))
    missing_price = sum(1 for e in events if e.get("price_value") in (None, ""))
    missing_symbol = sum(1 for e in events if e.get("symbol_value") in (None, ""))

    if len(events) < MIN_EVENTS_TOTAL:
        findings.append({
            "severity": "P1",
            "owner": "replay/sample_strength",
            "finding": "strong replay sample has too few materialized events",
            "events_materialized": len(events),
            "minimum_required": MIN_EVENTS_TOTAL,
        })

    if len(kinds) < MIN_KINDS:
        findings.append({
            "severity": "P1",
            "owner": "replay/sample_strength",
            "finding": "strong replay sample has too few instrument kinds",
            "kinds": kinds,
            "minimum_required": MIN_KINDS,
        })

    if not replay_only:
        findings.append({
            "severity": "P0",
            "owner": "replay/isolation",
            "finding": "non-replay channel found",
            "channels": channels,
        })

    if not events:
        findings.append({
            "severity": "P1",
            "owner": "replay/materialization",
            "finding": "no replay events materialized",
        })

    EVENTS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_OUT.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, sort_keys=True, default=str) + "\n")

    p0 = [f for f in findings if f["severity"] == "P0"]
    p1 = [f for f in findings if f["severity"] == "P1"]

    status = "PASS" if not p0 and not p1 and replay_only else "WARN"

    result = {
        "proof": "proof_aftermarket_strong_replay_sample",
        "generated_at": now_iso(),
        "status": status,
        "selected_date": selected_date,
        "selected_files": file_results,
        "candidate_file_count": len(candidates),
        "events_materialized": len(events),
        "kinds": kinds,
        "channels": channels,
        "replay_only_channels": replay_only,
        "missing_ts_count": missing_ts,
        "missing_price_count": missing_price,
        "missing_symbol_count": missing_symbol,
        "events_output": rel(EVENTS_OUT),
        "minimum_events_required": MIN_EVENTS_TOTAL,
        "minimum_kinds_required": MIN_KINDS,
        "writes_live_redis": False,
        "uses_broker": False,
        "places_orders": False,
        "starts_services": False,
        "findings": findings,
        "does_not_prove": [
            "live provider freshness",
            "broker token validity",
            "actual order routing",
            "market-session paper_armed behavior",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))

    print(json.dumps({
        "status": status,
        "selected_date": selected_date,
        "events_materialized": len(events),
        "kinds": kinds,
        "replay_only_channels": replay_only,
        "findings": findings,
        "out": rel(OUT),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
