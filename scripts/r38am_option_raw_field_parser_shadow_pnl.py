#!/usr/bin/env python3
from __future__ import annotations

import bisect
import gzip
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HORIZONS_SEC = [15, 30, 60, 120, 180, 300]
STREAM_ID_RE = re.compile(r"^[0-9]{13}-[0-9]+$")


def safe_float(v: Any, d: float = 0.0) -> float:
    try:
        if v in (None, ""):
            return d
        return float(v)
    except Exception:
        return d


def safe_int(v: Any, d: int = 0) -> int:
    try:
        if v in (None, ""):
            return d
        return int(float(v))
    except Exception:
        return d


def stream_id_to_ns(s: str) -> int:
    if STREAM_ID_RE.match(str(s).strip()):
        return int(str(s).split("-", 1)[0]) * 1_000_000
    return 0


def parse_redis_raw_field_value_gz(path: Path):
    """
    Parse redisraw.gz emitted as:
      stream-id
      field
      value
      field
      value
      next-stream-id
      ...
    """
    current_id = ""
    fields: dict[str, str] = {}
    pending_key: str | None = None

    def flush():
        nonlocal fields, current_id, pending_key
        if current_id or fields:
            out = dict(fields)
            out["_stream_id"] = current_id
            out["_stream_ts_ns"] = str(stream_id_to_ns(current_id))
            yield out
        fields = {}
        pending_key = None

    with gzip.open(path, "rt", errors="ignore") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line:
                continue

            if STREAM_ID_RE.match(line.strip()):
                yield from flush()
                current_id = line.strip()
                continue

            if pending_key is None:
                pending_key = line
            else:
                fields[pending_key] = line
                pending_key = None

    yield from flush()


def parse_option_ticks(opt_gz: Path):
    ticks = defaultdict(list)

    for rec in parse_redis_raw_field_value_gz(opt_gz):
        token = (
            rec.get("instrument_token")
            or rec.get("option_token")
            or rec.get("instrument_key")
            or ""
        )
        symbol = rec.get("trading_symbol") or rec.get("option_symbol") or ""
        ltp = safe_float(rec.get("ltp") or rec.get("last_price"), 0.0)
        ts = (
            safe_int(rec.get("ts_event_ns"), 0)
            or safe_int(rec.get("ts_provider_ns"), 0)
            or safe_int(rec.get("ts_recv_ns"), 0)
            or safe_int(rec.get("_stream_ts_ns"), 0)
        )

        if token and ltp > 0 and ts > 0:
            ticks[str(token)].append((ts, ltp, str(symbol)))

    for token in list(ticks):
        ticks[token].sort(key=lambda x: x[0])

    return ticks


def load_near_rows(jsonl: Path):
    rows = []
    with jsonl.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            if safe_int(r.get("entry_ts_ns"), 0) > 0 and str(r.get("instrument_token") or ""):
                rows.append(r)

    # light dedupe
    seen = set()
    out = []
    for r in sorted(rows, key=lambda x: (safe_int(x.get("entry_ts_ns"), 0), safe_float(x.get("setup_score"), 0)), reverse=True):
        key = (
            safe_int(r.get("entry_ts_ns"), 0),
            str(r.get("instrument_token")),
            str(r.get("branch_id")),
            str(r.get("failed_stage")),
            round(safe_float(r.get("setup_score"), 0.0), 6),
            safe_float(r.get("entry_ltp"), 0.0),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def forward_ltp(ticks, token: str, ts: int, horizon_sec: int):
    arr = ticks.get(token) or []
    if not arr or ts <= 0:
        return None
    target = ts + horizon_sec * 1_000_000_000
    idx = bisect.bisect_left(arr, (target, -1.0, ""))
    if idx >= len(arr):
        return None
    return arr[idx][1], arr[idx][0]


def main() -> int:
    if len(sys.argv) != 5:
        print("usage: SCRIPT near_jsonl opt_selected_zerodha.redisraw.gz out_jsonl out_summary", file=sys.stderr)
        return 2

    near_jsonl, opt_gz, out_jsonl, out_summary = map(Path, sys.argv[1:])
    near = load_near_rows(near_jsonl)
    ticks = parse_option_ticks(opt_gz)

    enriched = []
    for r in near:
        token = str(r.get("instrument_token"))
        ts = safe_int(r.get("entry_ts_ns"), 0)
        entry = safe_float(r.get("entry_ltp"), 0.0)

        for h in HORIZONS_SEC:
            got = forward_ltp(ticks, token, ts, h)
            if got:
                exit_ltp, exit_ts = got
                r[f"ltp_plus_{h}s"] = exit_ltp
                r[f"exit_ts_plus_{h}s"] = exit_ts
                r[f"pnl_points_plus_{h}s"] = round(exit_ltp - entry, 6)
                r[f"pnl_pct_plus_{h}s"] = round((exit_ltp - entry) / entry * 100.0, 6) if entry else None
            else:
                r[f"ltp_plus_{h}s"] = None
                r[f"exit_ts_plus_{h}s"] = None
                r[f"pnl_points_plus_{h}s"] = None
                r[f"pnl_pct_plus_{h}s"] = None

        enriched.append(r)

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as fp:
        for r in enriched:
            fp.write(json.dumps(r, sort_keys=True, default=str) + "\n")

    summary = {
        "schema": "r38am_mist_near_option_raw_field_shadow_pnl_summary_v1",
        "near_source": str(near_jsonl),
        "option_source": str(opt_gz),
        "near_rows": len(enriched),
        "rows_with_ts": sum(1 for r in enriched if safe_int(r.get("entry_ts_ns"), 0) > 0),
        "option_tick_tokens": {k: len(v) for k, v in sorted(ticks.items())},
        "branch_counts": dict(Counter(str(r.get("branch_id")) for r in enriched)),
        "stage_counts": dict(Counter(str(r.get("failed_stage")) for r in enriched)),
        "horizons": {},
        "top_rows": enriched[:30],
        "safety": {
            "shadow_only": True,
            "paper_allowed": False,
            "live_allowed": False,
            "routable_to_risk": False,
            "routable_to_execution": False,
            "order_attempt": False,
            "redis_write": False,
        },
    }

    for h in HORIZONS_SEC:
        vals = [
            r.get(f"pnl_points_plus_{h}s")
            for r in enriched
            if isinstance(r.get(f"pnl_points_plus_{h}s"), (int, float))
        ]
        by_branch = {}
        by_stage = {}

        for key_name, key_field, target in [
            ("branch", "branch_id", by_branch),
            ("stage", "failed_stage", by_stage),
        ]:
            groups = defaultdict(list)
            for r in enriched:
                v = r.get(f"pnl_points_plus_{h}s")
                if isinstance(v, (int, float)):
                    groups[str(r.get(key_field))].append(v)
            for k, arr in groups.items():
                target[k] = {
                    "count": len(arr),
                    "avg_points": round(sum(arr) / len(arr), 6),
                    "median_points": round(statistics.median(arr), 6),
                    "win_pct": round(sum(1 for x in arr if x > 0) / len(arr) * 100.0, 4),
                    "min_points": round(min(arr), 6),
                    "max_points": round(max(arr), 6),
                }

        if vals:
            summary["horizons"][f"{h}s"] = {
                "count": len(vals),
                "avg_points": round(sum(vals) / len(vals), 6),
                "median_points": round(statistics.median(vals), 6),
                "win_pct": round(sum(1 for v in vals if v > 0) / len(vals) * 100.0, 4),
                "min_points": round(min(vals), 6),
                "max_points": round(max(vals), 6),
                "by_branch": by_branch,
                "by_stage": by_stage,
            }
        else:
            summary["horizons"][f"{h}s"] = {"count": 0}

    out_summary.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print("near_rows=" + str(summary["near_rows"]))
    print("rows_with_ts=" + str(summary["rows_with_ts"]))
    print("option_tick_tokens=" + json.dumps(summary["option_tick_tokens"], sort_keys=True))
    print("branch_counts=" + json.dumps(summary["branch_counts"], sort_keys=True))
    print("stage_counts=" + json.dumps(summary["stage_counts"], sort_keys=True))
    print("horizons=" + json.dumps(summary["horizons"], sort_keys=True))
    print("out_jsonl=" + str(out_jsonl))
    print("out_summary=" + str(out_summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
