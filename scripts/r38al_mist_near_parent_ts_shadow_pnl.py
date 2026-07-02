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
from typing import Any, Mapping

decoder = json.JSONDecoder()
FAMILY = "MIST"
VALID_BRANCHES = {"CALL", "PUT"}
FAILS = {"pullback", "futures_impulse", "futures_bias", "score_below_threshold", "futures_impulse_insufficient"}
HORIZONS_SEC = [15, 30, 60, 120, 180, 300]

TS_KEYS = (
    "frame_ts_ns",
    "features_generated_at_ns",
    "ts_event_ns",
    "ts_provider_ns",
    "ts_recv_ns",
    "timestamp_ns",
    "event_ts_ns",
    "generated_at_ns",
    "created_at_ns",
    "published_at_ns",
    "frame_time_ns",
)


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


def safe_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"1", "true", "yes", "y", "on", "pass", "passed"}


def as_map(v: Any) -> dict[str, Any]:
    return dict(v) if isinstance(v, Mapping) else {}


def redis_stream_id_ns(line: str) -> int:
    # Accept 1712345678901-0 style stream id, convert ms -> ns.
    m = re.search(r"\b([0-9]{13})-[0-9]+\b", line)
    if m:
        return int(m.group(1)) * 1_000_000
    return 0


def iter_json_objects(text: str):
    s = text.strip()
    if not s:
        return
    if s.startswith("{"):
        try:
            yield json.loads(s)
            return
        except Exception:
            pass
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = decoder.raw_decode(text[m.start():])
            if isinstance(obj, dict):
                yield obj
        except Exception:
            continue


def extract_ts_from_map(obj: Mapping[str, Any]) -> int:
    for k in TS_KEYS:
        val = safe_int(obj.get(k), 0)
        if val > 0:
            # If timestamp looks like milliseconds, convert to ns.
            if 1_000_000_000_000 <= val < 10_000_000_000_000:
                return val * 1_000_000
            return val

    # Search one level deeper for common timestamp containers.
    for k in ("metadata", "frame", "common", "consumer_view", "payload", "features", "selected_features", "option_features"):
        v = obj.get(k)
        if isinstance(v, Mapping):
            ts = extract_ts_from_map(v)
            if ts > 0:
                return ts
    return 0


def walk_with_context(obj: Any, ctx_ts: int = 0):
    if isinstance(obj, dict):
        own_ts = extract_ts_from_map(obj) or ctx_ts
        yield obj, own_ts
        for v in obj.values():
            yield from walk_with_context(v, own_ts)
    elif isinstance(obj, list):
        for x in obj:
            yield from walk_with_context(x, ctx_ts)


def extract_near(obj: Mapping[str, Any], ctx_ts: int, line_ts: int, line_no: int):
    fid = str(obj.get("family_id") or obj.get("doctrine_id") or "").upper()
    if fid != FAMILY:
        return None

    branch = str(obj.get("branch_id") or obj.get("side") or "").upper()
    if branch not in VALID_BRANCHES:
        return None

    if safe_bool(obj.get("eligible")):
        return None

    failed = str(
        obj.get("failed_stage")
        or obj.get("batch9_freeze_blocked_reason")
        or obj.get("pre_batch9_failed_stage")
        or ""
    ).strip()

    if failed not in FAILS:
        return None

    selected = as_map(obj.get("selected_features"))
    option = as_map(obj.get("option_features"))
    trad = as_map(obj.get("tradability") or obj.get("tradability_surface"))

    token = str(selected.get("option_token") or selected.get("instrument_token") or option.get("option_token") or option.get("instrument_token") or "")
    symbol = str(selected.get("trading_symbol") or selected.get("option_symbol") or option.get("trading_symbol") or option.get("option_symbol") or "")
    ltp = safe_float(selected.get("ltp") or option.get("ltp"), 0.0)

    passed = obj.get("passed_stages") or []
    if not isinstance(passed, list):
        passed = []

    selected_ts = extract_ts_from_map(selected)
    option_ts = extract_ts_from_map(option)
    obj_ts = extract_ts_from_map(obj)
    ts = obj_ts or selected_ts or option_ts or ctx_ts or line_ts

    if not (
        safe_bool(selected.get("present"))
        and safe_bool(option.get("present"))
        and safe_bool(trad.get("present"))
        and safe_bool(obj.get("provider_ready"))
        and token
        and symbol
        and ltp > 0
        and len(passed) >= 4
    ):
        return None

    return {
        "family_id": FAMILY,
        "branch_id": branch,
        "failed_stage": failed,
        "setup_score": safe_float(obj.get("setup_score"), 0.0),
        "passed_stage_count": len(passed),
        "passed_stages": passed,
        "instrument_token": token,
        "option_symbol": symbol,
        "entry_ltp": ltp,
        "entry_ts_ns": ts,
        "ts_source": "obj/selected/option/parent/redis_line",
        "source_line_no": line_no,
        "shadow_only": True,
        "paper_allowed": False,
        "live_allowed": False,
        "routable_to_risk": False,
        "routable_to_execution": False,
    }


def parse_near(features_gz: Path):
    rows = []
    line_no = 0
    with gzip.open(features_gz, "rt", errors="ignore") as f:
        for line in f:
            line_no += 1
            if "MIST" not in line:
                continue
            line_ts = redis_stream_id_ns(line)
            for root in iter_json_objects(line):
                root_ts = extract_ts_from_map(root) or line_ts
                for obj, ctx_ts in walk_with_context(root, root_ts):
                    if isinstance(obj, dict):
                        r = extract_near(obj, ctx_ts, line_ts, line_no)
                        if r:
                            rows.append(r)

    seen = set()
    out = []
    for r in sorted(rows, key=lambda x: (x["entry_ts_ns"], x["setup_score"], x["source_line_no"]), reverse=True):
        key = (
            r["entry_ts_ns"],
            r["instrument_token"],
            r["branch_id"],
            r["failed_stage"],
            round(r["setup_score"], 6),
            r["source_line_no"],
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def parse_option_ticks(opt_gz: Path):
    ticks = defaultdict(list)
    line_no = 0
    with gzip.open(opt_gz, "rt", errors="ignore") as f:
        for line in f:
            line_no += 1
            line_ts = redis_stream_id_ns(line)
            for root in iter_json_objects(line):
                root_ts = extract_ts_from_map(root) or line_ts
                for obj, ctx_ts in walk_with_context(root, root_ts):
                    if not isinstance(obj, dict):
                        continue
                    token = str(obj.get("instrument_token") or obj.get("option_token") or obj.get("instrument_key") or "")
                    symbol = str(obj.get("trading_symbol") or obj.get("option_symbol") or "")
                    ltp = safe_float(obj.get("ltp") or obj.get("last_price"), 0.0)
                    ts = extract_ts_from_map(obj) or ctx_ts or line_ts
                    if token and ltp > 0 and ts > 0:
                        ticks[token].append((ts, ltp, symbol))

    for token in list(ticks):
        ticks[token].sort(key=lambda x: x[0])
    return ticks


def forward_ltp(ticks, token, ts, horizon_sec):
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
        print("usage: SCRIPT features.redisraw.gz opt_selected_zerodha.redisraw.gz out_jsonl out_summary", file=sys.stderr)
        return 2

    features_gz, opt_gz, out_jsonl, out_summary = map(Path, sys.argv[1:])
    near = parse_near(features_gz)
    ticks = parse_option_ticks(opt_gz)

    enriched = []
    for r in near:
        entry = r["entry_ltp"]
        for h in HORIZONS_SEC:
            got = forward_ltp(ticks, r["instrument_token"], r["entry_ts_ns"], h)
            if got:
                exit_ltp, exit_ts = got
                r[f"ltp_plus_{h}s"] = exit_ltp
                r[f"pnl_points_plus_{h}s"] = round(exit_ltp - entry, 6)
                r[f"pnl_pct_plus_{h}s"] = round((exit_ltp - entry) / entry * 100.0, 6) if entry else None
                r[f"exit_ts_plus_{h}s"] = exit_ts
            else:
                r[f"ltp_plus_{h}s"] = None
                r[f"pnl_points_plus_{h}s"] = None
                r[f"pnl_pct_plus_{h}s"] = None
                r[f"exit_ts_plus_{h}s"] = None
        enriched.append(r)

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as fp:
        for r in enriched:
            fp.write(json.dumps(r, sort_keys=True, default=str) + "\n")

    summary = {
        "schema": "r38al_mist_near_parent_ts_shadow_pnl_summary_v1",
        "features_source": str(features_gz),
        "option_source": str(opt_gz),
        "near_rows": len(enriched),
        "rows_with_ts": sum(1 for r in enriched if r["entry_ts_ns"] > 0),
        "option_tick_tokens": {k: len(v) for k, v in sorted(ticks.items())},
        "branch_counts": dict(Counter(r["branch_id"] for r in enriched)),
        "stage_counts": dict(Counter(r["failed_stage"] for r in enriched)),
        "horizons": {},
        "top_rows": enriched[:20],
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
        vals = [r[f"pnl_points_plus_{h}s"] for r in enriched if isinstance(r.get(f"pnl_points_plus_{h}s"), (int, float))]
        if vals:
            summary["horizons"][f"{h}s"] = {
                "count": len(vals),
                "avg_points": round(sum(vals) / len(vals), 6),
                "median_points": round(statistics.median(vals), 6),
                "win_pct": round(sum(1 for v in vals if v > 0) / len(vals) * 100.0, 4),
                "min_points": round(min(vals), 6),
                "max_points": round(max(vals), 6),
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
