from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from app.mme_scalpx.core.redisx import get_redis_client

CONTROL = Path("run/controls/pshadowgate_v27_entry_quality.env")
BLOCKED_DIR = Path("run/paper_shadow_entry_quality_v27")


def now_ms() -> int:
    return int(time.time() * 1000)


def day() -> str:
    return time.strftime("%Y%m%d")


def parse_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def cfg_bool(c: dict[str, str], k: str, default: bool) -> bool:
    v = c.get(k, os.environ.get(k, str(int(default))))
    return str(v).strip().lower() in {"1", "true", "yes", "on", "y"}


def cfg_int(c: dict[str, str], k: str, default: int) -> int:
    try:
        return int(str(c.get(k, os.environ.get(k, default))).strip())
    except Exception:
        return default


def cfg_float(c: dict[str, str], k: str, default: float) -> float:
    try:
        return float(str(c.get(k, os.environ.get(k, default))).strip())
    except Exception:
        return default


def load_cfg() -> dict[str, Any]:
    c = parse_env(CONTROL)
    return {
        "enabled": cfg_bool(c, "V27_ENTRY_QUALITY_ENABLED", True),
        "fail_closed_missing_ticks": cfg_bool(c, "V27_FAIL_CLOSED_MISSING_TICKS", True),
        "max_packet_source_age_ms": cfg_int(c, "V27_MAX_PACKET_SOURCE_AGE_MS", 7000),
        "tick_lookback_count": cfg_int(c, "V27_TICK_LOOKBACK_COUNT", 30),
        "min_ticks_required": cfg_int(c, "V27_MIN_TICKS_REQUIRED", 8),
        "max_last_tick_age_ms": cfg_int(c, "V27_MAX_LAST_TICK_AGE_MS", 30000),
        "min_recent_momentum_points": cfg_float(c, "V27_MIN_RECENT_MOMENTUM_POINTS", 0.10),
        "max_pullback_from_recent_high_points": cfg_float(c, "V27_MAX_PULLBACK_FROM_RECENT_HIGH_POINTS", 1.20),
        "max_chase_extension_from_recent_low_points": cfg_float(c, "V27_MAX_CHASE_EXTENSION_FROM_RECENT_LOW_POINTS", 7.50),
        "max_recent_range_points": cfg_float(c, "V27_MAX_RECENT_RANGE_POINTS", 12.00),
        "min_distance_from_recent_low_points": cfg_float(c, "V27_MIN_DISTANCE_FROM_RECENT_LOW_POINTS", 0.20),
        "min_score_soft": cfg_float(c, "V27_MIN_SCORE_SOFT", 0.60),
        "log_blocked_events": cfg_bool(c, "V27_LOG_BLOCKED_EVENTS", True),
    }


def dec(x: Any) -> str:
    if isinstance(x, bytes):
        return x.decode("utf-8", errors="replace")
    return str(x)


def to_float(v: Any, default: float | None = None) -> float | None:
    try:
        return float(v)
    except Exception:
        return default


def field_dict(fields: dict[Any, Any]) -> dict[str, str]:
    return {dec(k): dec(v) for k, v in fields.items()}


def price_from_fields(fields: dict[str, str]) -> float | None:
    for k in ["ltp", "price", "last_price", "last_traded_price", "close"]:
        if k in fields:
            px = to_float(fields[k])
            if px is not None and px > 0:
                return px
    for k, v in fields.items():
        lk = k.lower()
        if "ltp" in lk or "price" in lk:
            px = to_float(v)
            if px is not None and px > 0:
                return px
    return None


def ts_from_id(rid: str) -> int:
    try:
        return int(str(rid).split("-")[0])
    except Exception:
        return 0


def match_tick(fields: dict[str, str], symbol: str, token: str) -> bool:
    symbol = str(symbol or "").upper()
    token = str(token or "")
    vals = {k.lower(): v for k, v in fields.items()}
    sym_candidates = [
        vals.get("symbol"),
        vals.get("trading_symbol"),
        vals.get("tradingsymbol"),
        vals.get("instrument_key"),
    ]
    tok_candidates = [
        vals.get("instrument_token"),
        vals.get("token"),
        vals.get("instrument"),
    ]
    if symbol and any(str(x or "").upper() == symbol for x in sym_candidates):
        return True
    if token and any(str(x or "") == token for x in tok_candidates):
        return True
    return False


def collect_ticks(symbol: str, token: str, lookback_count: int) -> tuple[str, list[tuple[int, float]]]:
    r = get_redis_client()
    streams = [
        "ticks:mme:opt:selected:zerodha:stream",
        "ticks:mme:opt:selected:stream",
        "ticks:mme:opt:stream",
        "ticks:mme:options:zerodha:stream",
    ]
    best_stream = ""
    best: list[tuple[int, float]] = []

    for s in streams:
        try:
            rows = r.xrevrange(s, count=max(lookback_count * 8, 120))
        except Exception:
            rows = []

        vals: list[tuple[int, float]] = []
        for rid, fields0 in reversed(rows):
            rid_s = dec(rid)
            fields = field_dict(fields0)
            if not match_tick(fields, symbol=symbol, token=token):
                continue
            px = price_from_fields(fields)
            ts = ts_from_id(rid_s)
            if px is not None and ts > 0:
                vals.append((ts, px))

        if len(vals) > len(best):
            best_stream = s
            best = vals[-lookback_count:]

    return best_stream, best


def append_ndjson(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def log_block(verdict: dict[str, Any]) -> None:
    cfg = load_cfg()
    if cfg.get("log_blocked_events") and not verdict.get("allowed"):
        append_ndjson(BLOCKED_DIR / f"blocked_{day()}.ndjson", verdict)


def evaluate_entry_quality(
    action: str,
    family: str = "",
    symbol: str = "",
    token: str = "",
    score: str = "",
    source_age_ms: str = "",
    synthetic_ticks_json: str = "",
) -> dict[str, Any]:
    cfg = load_cfg()
    action = str(action or "").upper().strip()
    family = str(family or "").upper().strip()
    symbol = str(symbol or "").upper().strip()
    token = str(token or "").strip()
    score_f = to_float(score, -1.0) or -1.0
    source_age = int(to_float(source_age_ms, 10**12) or 10**12)

    base = {
        "schema": "pshadowgate_v27_entry_quality_verdict.v1",
        "checked_at_ms": now_ms(),
        "action": action,
        "family": family,
        "symbol": symbol,
        "token": token,
        "score": score_f,
        "source_age_ms": source_age,
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
        "redis_destructive": 0,
    }

    if not cfg["enabled"]:
        base.update({"allowed": True, "reason": "V27_ENTRY_QUALITY_DISABLED"})
        return base

    if source_age > int(cfg["max_packet_source_age_ms"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_STALE_PACKET"})
        return base

    if score_f >= 0 and score_f < float(cfg["min_score_soft"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_SCORE_TOO_LOW"})
        return base

    if synthetic_ticks_json:
        try:
            raw = json.loads(synthetic_ticks_json)
            ticks = [(int(x[0]), float(x[1])) for x in raw]
            stream = "synthetic_test"
        except Exception:
            ticks = []
            stream = "synthetic_parse_failed"
    else:
        stream, ticks = collect_ticks(symbol=symbol, token=token, lookback_count=int(cfg["tick_lookback_count"]))

    base["tick_stream"] = stream
    base["ticks_count"] = len(ticks)

    if len(ticks) < int(cfg["min_ticks_required"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_INSUFFICIENT_TICKS"})
        return base

    last_ts = ticks[-1][0]
    last_px = ticks[-1][1]
    first_px = ticks[0][1]
    recent = [p for _, p in ticks]
    recent_high = max(recent)
    recent_low = min(recent)
    recent_range = recent_high - recent_low
    recent_momentum = last_px - first_px
    pullback_from_high = recent_high - last_px
    extension_from_low = last_px - recent_low
    last_tick_age_ms = max(0, now_ms() - last_ts)

    base.update({
        "last_price": round(last_px, 4),
        "first_price": round(first_px, 4),
        "recent_high": round(recent_high, 4),
        "recent_low": round(recent_low, 4),
        "recent_range_points": round(recent_range, 4),
        "recent_momentum_points": round(recent_momentum, 4),
        "pullback_from_recent_high_points": round(pullback_from_high, 4),
        "extension_from_recent_low_points": round(extension_from_low, 4),
        "last_tick_age_ms": last_tick_age_ms,
    })

    if last_tick_age_ms > int(cfg["max_last_tick_age_ms"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_STALE_OPTION_TICK"})
        return base

    # Long-option logic: CALL and PUT are both long options in our shadow lifecycle.
    # A valid entry needs the selected option to be responding now, not collapsing.
    if recent_momentum < float(cfg["min_recent_momentum_points"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_OPTION_MOMENTUM_WEAK"})
        return base

    if pullback_from_high > float(cfg["max_pullback_from_recent_high_points"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_PULLBACK_FROM_HIGH"})
        return base

    if extension_from_low > float(cfg["max_chase_extension_from_recent_low_points"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_LATE_CHASE_EXTENSION"})
        return base

    if recent_range > float(cfg["max_recent_range_points"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_RECENT_RANGE_TOO_WIDE"})
        return base

    if extension_from_low < float(cfg["min_distance_from_recent_low_points"]):
        base.update({"allowed": False, "reason": "ENTRY_QUALITY_FAIL_TOO_CLOSE_TO_RECENT_LOW"})
        return base

    base.update({"allowed": True, "reason": "ENTRY_QUALITY_ALLOWED"})
    return base


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", default="")
    ap.add_argument("--family", default="")
    ap.add_argument("--symbol", default="")
    ap.add_argument("--token", default="")
    ap.add_argument("--score", default="")
    ap.add_argument("--source-age-ms", default="")
    ap.add_argument("--synthetic-ticks-json", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    verdict = evaluate_entry_quality(
        action=args.action,
        family=args.family,
        symbol=args.symbol,
        token=args.token,
        score=args.score,
        source_age_ms=args.source_age_ms,
        synthetic_ticks_json=args.synthetic_ticks_json,
    )
    log_block(verdict)

    if args.json:
        print(json.dumps(verdict, sort_keys=True))
        return 0 if verdict.get("allowed") else 4

    print("V27_ALLOWED=" + str(int(bool(verdict.get("allowed")))))
    print("V27_REASON=" + str(verdict.get("reason")))
    print("V27_SYMBOL=" + str(verdict.get("symbol")))
    print("V27_TOKEN=" + str(verdict.get("token")))
    print("V27_TICK_STREAM=" + str(verdict.get("tick_stream", "")))
    print("V27_TICKS_COUNT=" + str(verdict.get("ticks_count", "")))
    print("V27_RECENT_MOMENTUM_POINTS=" + str(verdict.get("recent_momentum_points", "")))
    print("V27_PULLBACK_FROM_HIGH_POINTS=" + str(verdict.get("pullback_from_recent_high_points", "")))
    print("V27_EXTENSION_FROM_LOW_POINTS=" + str(verdict.get("extension_from_recent_low_points", "")))
    print("V27_RECENT_RANGE_POINTS=" + str(verdict.get("recent_range_points", "")))
    print("V27_LAST_TICK_AGE_MS=" + str(verdict.get("last_tick_age_ms", "")))
    print("BROKER_ORDER=0")
    print("PAPER_ENGINE_ORDER=0")
    print("RISK_STARTED=0")
    print("EXECUTION_STARTED=0")
    print("REDIS_DESTRUCTIVE=0")
    return 0 if verdict.get("allowed") else 4


if __name__ == "__main__":
    raise SystemExit(main())
