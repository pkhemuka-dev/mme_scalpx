#!/usr/bin/env python3
from __future__ import annotations

import argparse, datetime as dt, json, pathlib
from typing import Any
import redis

STREAMS = [
    "trades:mme:stream",
    "trades:ledger:stream",
    "execution:mme:stream",
    "orders:mme:stream",
    "risk:mme:stream",
    "decisions:mme:stream",
]

def dec(x: Any) -> str:
    return x.decode("utf-8", "replace") if isinstance(x, bytes) else str(x)

def fields(d: dict[Any, Any]) -> dict[str, str]:
    return {dec(k): dec(v) for k, v in d.items()}

def flt(x: Any, default: float = 0.0) -> float:
    try:
        s = dec(x).strip()
        return float(s) if s else default
    except Exception:
        return default

def read_stream(r: redis.Redis, name: str, count: int) -> list[dict[str, Any]]:
    try:
        rows = r.xrevrange(name, "+", "-", count=count)
    except Exception:
        return []
    return [{"id": dec(i), "fields": fields(f)} for i, f in reversed(rows)]

def maybe_trade(row: dict[str, Any], stream: str) -> dict[str, Any] | None:
    f = row["fields"]
    blob = json.dumps(f, sort_keys=True).lower()
    pnl_keys = ["net_pnl", "gross_pnl", "pnl", "realized_pnl", "paper_pnl"]
    has_pnl = any(k in f for k in pnl_keys)
    is_trade = stream in {"trades:mme:stream", "trades:ledger:stream"} or has_pnl or "fill" in blob or "exit" in blob or "closed" in blob
    if not is_trade:
        return None
    pnl = next((flt(f[k]) for k in pnl_keys if k in f), 0.0)
    gross = flt(f.get("gross_pnl"), pnl)
    net = flt(f.get("net_pnl"), pnl if pnl else gross)
    return {
        "stream": stream,
        "id": row["id"],
        "symbol": f.get("tradingsymbol") or f.get("symbol") or f.get("instrument") or "",
        "side": f.get("side") or f.get("transaction_type") or f.get("action") or "",
        "gross_pnl": gross,
        "net_pnl": net,
        "entry_mode": f.get("entry_mode") or f.get("family") or f.get("family_id") or "",
        "exit_reason": f.get("exit_reason") or f.get("reason") or f.get("status") or "",
        "raw": f,
    }

def bucket(t: dict[str, Any]) -> str:
    b = json.dumps(t.get("raw") or {}, sort_keys=True).lower()
    if "stop" in b or "sl" in b:
        return "stop_loss_or_adverse_move"
    if "target" in b or "profit" in b:
        return "target_or_profit_exit"
    if "spread" in b:
        return "spread_quality_issue"
    if "depth" in b or "liquid" in b:
        return "liquidity_depth_issue"
    if "timeout" in b or "time" in b:
        return "time_exit_or_delayed_exit"
    if "hold" in b:
        return "hold_or_no_trade_context"
    return "unclassified"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="paper")
    ap.add_argument("--session-tag", required=True)
    ap.add_argument("--capture-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--redis-host", default="127.0.0.1")
    ap.add_argument("--redis-port", type=int, default=6379)
    ap.add_argument("--redis-db", type=int, default=0)
    ap.add_argument("--count", type=int, default=5000)
    args = ap.parse_args()

    outdir = pathlib.Path(args.output_dir); outdir.mkdir(parents=True, exist_ok=True)
    r = redis.Redis(host=args.redis_host, port=args.redis_port, db=args.redis_db, decode_responses=False)

    trades = []
    stream_counts = {}
    for s in STREAMS:
        rows = read_stream(r, s, args.count)
        stream_counts[s] = len(rows)
        for row in rows:
            t = maybe_trade(row, s)
            if t:
                trades.append(t)

    seen, uniq = set(), []
    for t in trades:
        k = (t["stream"], t["id"])
        if k not in seen:
            seen.add(k); uniq.append(t)
    trades = uniq

    closed = [t for t in trades if t["stream"] in {"trades:mme:stream", "trades:ledger:stream"} or abs(float(t["net_pnl"])) > 0]
    wins = [t for t in closed if float(t["net_pnl"]) > 0]
    losses = [t for t in closed if float(t["net_pnl"]) < 0]
    flats = [t for t in closed if float(t["net_pnl"]) == 0]

    gross = round(sum(float(t["gross_pnl"]) for t in closed), 4)
    net = round(sum(float(t["net_pnl"]) for t in closed), 4)
    win_rate = round((len(wins) / len(closed)) * 100, 2) if closed else 0.0
    avg_win = round(sum(float(t["net_pnl"]) for t in wins) / len(wins), 4) if wins else 0.0
    avg_loss = round(sum(float(t["net_pnl"]) for t in losses) / len(losses), 4) if losses else 0.0
    expectancy = round((win_rate / 100) * avg_win + (1 - win_rate / 100) * avg_loss, 4) if closed else 0.0

    buckets = {}
    for t in closed:
        b = bucket(t)
        buckets[b] = buckets.get(b, 0) + 1

    review = {
        "session_tag": args.session_tag,
        "mode": args.mode,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "capture_dir": args.capture_dir,
        "streams_read": stream_counts,
        "trade_like_rows": len(trades),
        "closed_trades": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "flats": len(flats),
        "win_rate_pct": win_rate,
        "gross_pnl": gross,
        "net_pnl": net,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy_per_trade": expectancy,
        "bad_trade_buckets": buckets,
        "top_trades_sample": closed[-20:],
        "next": "if no trades, fix paper projection path; if trades exist, patch filters only from losing buckets",
    }

    (outdir / f"{args.session_tag}_pnl_review.json").write_text(json.dumps(review, indent=2, sort_keys=True))
    (outdir / "pnl_review.json").write_text(json.dumps(review, indent=2, sort_keys=True))
    (outdir / f"{args.session_tag}_pnl_review.md").write_text(
        "\n".join([
            f"# PnL Review — {args.session_tag}",
            f"- Mode: {args.mode}",
            f"- Closed trades: {review['closed_trades']}",
            f"- Wins: {review['wins']}",
            f"- Losses: {review['losses']}",
            f"- Win rate: {review['win_rate_pct']}%",
            f"- Gross PnL: {review['gross_pnl']}",
            f"- Net PnL: {review['net_pnl']}",
            f"- Avg win: {review['avg_win']}",
            f"- Avg loss: {review['avg_loss']}",
            f"- Expectancy/trade: {review['expectancy_per_trade']}",
            "",
            "## Bad-trade buckets",
            json.dumps(review["bad_trade_buckets"], indent=2, sort_keys=True),
            "",
        ])
    )
    print(json.dumps(review, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
