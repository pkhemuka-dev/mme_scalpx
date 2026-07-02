from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any
from collections import Counter, defaultdict

from app.mme_scalpx.core.redisx import get_redis_client
from app.mme_scalpx.shadow_paper.ltp_reader import find_live_ltp
from app.mme_scalpx.shadow_paper.pnl import calculate_long_option_metrics


CONTROL = Path("run/controls/pshadowgate_lifecycle_v23.env")
STATE_DIR = Path("run/state/pshadowgate_lifecycle_v23")
LEDGER_DIR = Path("run/paper_shadow_lifecycle_v23")
PSHADOW_DIR = Path("run/paper_shadow")


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
        "enabled": cfg_bool(c, "SHADOW_V23_ENABLED", True),
        "entry_event_max_age_ms": cfg_int(c, "ENTRY_EVENT_MAX_AGE_MS", 600000),
        "ltp_max_age_ms": cfg_int(c, "LTP_MAX_AGE_MS", 30000),
        "max_daily_trades": cfg_int(c, "MAX_DAILY_TRADES", 20),
        "one_open_position_only": cfg_bool(c, "ONE_OPEN_POSITION_ONLY", True),
        "lot_size": cfg_int(c, "LOT_SIZE", 65),
        "min_entry_price": cfg_float(c, "MIN_ENTRY_PRICE", 1.0),
        "max_entry_price": cfg_float(c, "MAX_ENTRY_PRICE", 1000.0),
        "assumed_slippage_points": cfg_float(c, "ASSUMED_SLIPPAGE_POINTS", 0.5),
        "abs_stop_points": cfg_float(c, "ABS_STOP_POINTS", 2.0),
        "hard_target_points": cfg_float(c, "HARD_TARGET_POINTS", 3.0),
        "max_holding_time_ms": cfg_int(c, "MAX_HOLDING_TIME_MS", 90000),
        "breakeven_enable": cfg_bool(c, "BREAKEVEN_ENABLE", True),
        "breakeven_after_mfe_points": cfg_float(c, "BREAKEVEN_AFTER_MFE_POINTS", 0.75),
        "breakeven_exit_buffer_points": cfg_float(c, "BREAKEVEN_EXIT_BUFFER_POINTS", 0.05),
        "trailing_enable": cfg_bool(c, "TRAILING_ENABLE", True),
        "trailing_activate_mfe_points": cfg_float(c, "TRAILING_ACTIVATE_MFE_POINTS", 1.0),
        "trailing_giveback_points": cfg_float(c, "TRAILING_GIVEBACK_POINTS", 0.45),
        "stale_ltp_exit_enable": cfg_bool(c, "STALE_LTP_EXIT_ENABLE", True),
        "stale_ltp_grace_ms": cfg_int(c, "STALE_LTP_GRACE_MS", 30000),
    }


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def append_ndjson(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def entries_path(d: str) -> Path:
    return LEDGER_DIR / f"entries_{d}.ndjson"


def exits_path(d: str) -> Path:
    return LEDGER_DIR / f"exits_{d}.ndjson"


def summary_path(d: str) -> Path:
    return LEDGER_DIR / f"summary_{d}.json"


def state_path() -> Path:
    return STATE_DIR / "open_position.json"


def safety_streams_zero() -> tuple[bool, dict[str, int]]:
    r = get_redis_client()
    names = {
        "risk": "risk:mme:stream",
        "execution": "execution:mme:stream",
        "orders": "orders:mme:stream",
        "trades": "trades:ledger:stream",
        "cmd": "cmd:mme:stream",
    }
    vals: dict[str, int] = {}
    for k, s in names.items():
        try:
            vals[k] = int(r.xlen(s))
        except Exception:
            vals[k] = -1
    return all(v == 0 for v in vals.values()), vals


def current_position() -> dict[str, Any] | None:
    data = read_json(state_path())
    if isinstance(data, dict) and data.get("status") == "OPEN":
        return data
    return None


def entered_event_ids(d: str) -> set[str]:
    ids: set[str] = set()
    for row in read_ndjson(entries_path(d)):
        eid = str(row.get("event_id") or "")
        if eid:
            ids.add(eid)
    return ids


def latest_pshadow_event_not_entered(d: str) -> dict[str, Any] | None:
    rows = read_ndjson(PSHADOW_DIR / f"pshadowgate_shadow_paper_events_{d}.ndjson")
    already = entered_event_ids(d)
    valid: list[dict[str, Any]] = []
    for row in rows:
        event_id = str(row.get("event_id") or "")
        if not event_id or event_id in already:
            continue
        if row.get("mode") != "LOCAL_SHADOW_PAPER_ONLY_NO_BROKER":
            continue
        if row.get("broker_order_sent") is not False:
            continue
        if row.get("real_paper_engine_used") is not False:
            continue
        if row.get("risk_execution_used") is not False:
            continue
        if not row.get("symbol") or not row.get("instrument_token"):
            continue
        valid.append(row)
    return valid[-1] if valid else None


def count_entries(d: str) -> int:
    return len(read_ndjson(entries_path(d)))


def write_summary(d: str) -> dict[str, Any]:
    entries = read_ndjson(entries_path(d))
    exits = read_ndjson(exits_path(d))
    pnl = [float(x.get("pnl_rupees_net_proxy") or 0.0) for x in exits]
    wins = [x for x in pnl if x > 0]
    losses = [x for x in pnl if x <= 0]
    by_reason = Counter(str(x.get("exit_reason") or "UNKNOWN") for x in exits)
    by_symbol = defaultdict(lambda: {"count": 0, "pnl_rupees_net_proxy": 0.0})
    by_family = defaultdict(lambda: {"count": 0, "pnl_rupees_net_proxy": 0.0})
    for x in exits:
        sym = str(x.get("symbol") or "UNKNOWN")
        fam = str(x.get("family_id") or "UNKNOWN")
        val = float(x.get("pnl_rupees_net_proxy") or 0.0)
        by_symbol[sym]["count"] += 1
        by_symbol[sym]["pnl_rupees_net_proxy"] += val
        by_family[fam]["count"] += 1
        by_family[fam]["pnl_rupees_net_proxy"] += val

    out = {
        "schema": "pshadow_lifecycle_v23_summary.v1",
        "day": d,
        "entries_count": len(entries),
        "exits_count": len(exits),
        "closed_pnl_rupees_net_proxy": round(sum(pnl), 2),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round((len(wins) / len(pnl)) if pnl else 0.0, 4),
        "exit_reason_counts": dict(by_reason),
        "by_symbol": by_symbol,
        "by_family": by_family,
        "latest_entry": entries[-1] if entries else None,
        "latest_exit": exits[-1] if exits else None,
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
    }
    write_json(summary_path(d), out)
    return out


def enter_if_possible() -> dict[str, Any]:
    c = load_cfg()
    d = day()
    r = get_redis_client()

    if not c["enabled"]:
        return {"action": "NO_ENTRY", "reason": "disabled"}

    zero, safety = safety_streams_zero()
    if not zero:
        return {"action": "NO_ENTRY", "reason": "safety_streams_not_zero", "safety": safety}

    if c["one_open_position_only"] and current_position() is not None:
        return {"action": "NO_ENTRY", "reason": "open_position_exists"}

    if count_entries(d) >= c["max_daily_trades"]:
        return {"action": "NO_ENTRY", "reason": "max_daily_trades_reached"}

    ev = latest_pshadow_event_not_entered(d)
    if not ev:
        return {"action": "NO_ENTRY", "reason": "no_new_valid_pshadow_event"}

    created_at_ms = int(ev.get("created_at_ms") or 0)
    age_ms = now_ms() - created_at_ms
    if age_ms > c["entry_event_max_age_ms"]:
        return {"action": "NO_ENTRY", "reason": "entry_event_too_old", "event_age_ms": age_ms}

    ltp = find_live_ltp(
        redis_client=r,
        symbol=str(ev.get("symbol") or ""),
        instrument_token=str(ev.get("instrument_token") or ""),
        max_age_ms=int(c["ltp_max_age_ms"]),
    )
    if ltp is None:
        return {"action": "NO_ENTRY", "reason": "no_fresh_ltp_found"}

    if not (float(c["min_entry_price"]) <= float(ltp.ltp) <= float(c["max_entry_price"])):
        return {"action": "NO_ENTRY", "reason": "entry_ltp_out_of_range", "ltp": ltp.to_dict()}

    pos = {
        "schema": "pshadow_lifecycle_v23_open_position.v1",
        "status": "OPEN",
        "event_id": str(ev.get("event_id") or ""),
        "source_decision_id": str(ev.get("source_decision_id") or ""),
        "action": str(ev.get("action") or ""),
        "symbol": str(ev.get("symbol") or ""),
        "instrument_token": str(ev.get("instrument_token") or ""),
        "family_id": str(ev.get("family_id") or ""),
        "score": float(ev.get("score") or 0.0),
        "qty_lots": int(ev.get("qty_lots") or 1),
        "lot_size": int(c["lot_size"]),
        "entry_price": float(ltp.ltp),
        "entry_created_at_ms": now_ms(),
        "entry_ltp_source": ltp.to_dict(),
        "highest_seen": float(ltp.ltp),
        "lowest_seen": float(ltp.ltp),
        "last_ltp": float(ltp.ltp),
        "last_ltp_at_ms": now_ms(),
        "exit_policy": c,
        "broker_order_sent": False,
        "paper_engine_used": False,
        "risk_execution_used": False,
    }

    write_json(state_path(), pos)
    append_ndjson(entries_path(d), pos)
    write_summary(d)

    return {
        "action": "ENTRY_WRITTEN",
        "position": pos,
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
    }


def decide_exit(pos: dict[str, Any], c: dict[str, Any], fresh_ltp_ok: bool) -> str:
    entry = float(pos["entry_price"])
    current = float(pos["last_ltp"])
    high = float(pos["highest_seen"])
    age_ms = now_ms() - int(pos["entry_created_at_ms"])
    mfe = high - entry

    if fresh_ltp_ok:
        if current <= entry - float(c["abs_stop_points"]):
            return "V23_ABS_STOP"
        if current >= entry + float(c["hard_target_points"]):
            return "V23_HARD_TARGET"

        if c["breakeven_enable"] and mfe >= float(c["breakeven_after_mfe_points"]):
            if current <= entry + float(c["breakeven_exit_buffer_points"]):
                return "V23_BREAKEVEN_AFTER_MFE"

        if c["trailing_enable"] and mfe >= float(c["trailing_activate_mfe_points"]):
            if current <= high - float(c["trailing_giveback_points"]):
                return "V23_TRAILING_GIVEBACK"

        if age_ms >= int(c["max_holding_time_ms"]):
            return "V23_MAX_HOLDING_TIME"

    else:
        if c["stale_ltp_exit_enable"] and age_ms >= int(c["max_holding_time_ms"]) + int(c["stale_ltp_grace_ms"]):
            return "V23_STALE_LTP_MAX_HOLD_LAST_KNOWN"

    return ""


def update_or_exit() -> dict[str, Any]:
    c = load_cfg()
    d = day()
    r = get_redis_client()
    pos = current_position()

    if not pos:
        return {"action": "NO_POSITION", "reason": "flat"}

    zero, safety = safety_streams_zero()
    if not zero:
        return {"action": "NO_EXIT", "reason": "safety_streams_not_zero", "safety": safety}

    fresh_ltp_ok = False
    ltp_source: dict[str, Any] | None = None

    ltp = find_live_ltp(
        redis_client=r,
        symbol=str(pos["symbol"]),
        instrument_token=str(pos["instrument_token"]),
        max_age_ms=int(c["ltp_max_age_ms"]),
    )

    if ltp is not None:
        fresh_ltp_ok = True
        current = float(ltp.ltp)
        pos["last_ltp"] = current
        pos["last_ltp_at_ms"] = now_ms()
        pos["highest_seen"] = max(float(pos["highest_seen"]), current)
        pos["lowest_seen"] = min(float(pos["lowest_seen"]), current)
        ltp_source = ltp.to_dict()

    exit_reason = decide_exit(pos, c, fresh_ltp_ok=fresh_ltp_ok)

    if not exit_reason:
        write_json(state_path(), pos)
        write_summary(d)
        return {
            "action": "POSITION_UPDATED",
            "position": pos,
            "fresh_ltp_ok": fresh_ltp_ok,
            "unrealized_pnl_points_proxy": round(float(pos["last_ltp"]) - float(pos["entry_price"]), 4),
            "mfe_points": round(float(pos["highest_seen"]) - float(pos["entry_price"]), 4),
            "mae_points": round(float(pos["lowest_seen"]) - float(pos["entry_price"]), 4),
            "broker_order": 0,
            "paper_engine_order": 0,
            "risk_started": 0,
            "execution_started": 0,
        }

    metrics = calculate_long_option_metrics(
        entry_price=float(pos["entry_price"]),
        exit_price=float(pos["last_ltp"]),
        highest_seen=float(pos["highest_seen"]),
        lowest_seen=float(pos["lowest_seen"]),
        qty_lots=int(pos["qty_lots"]),
        lot_size=int(pos["lot_size"]),
        assumed_slippage_points=float(c["assumed_slippage_points"]),
    )

    exit_obj = {
        "schema": "pshadow_lifecycle_v23_exit.v1",
        "event_id": pos["event_id"],
        "source_decision_id": pos.get("source_decision_id", ""),
        "action": pos["action"],
        "symbol": pos["symbol"],
        "instrument_token": pos["instrument_token"],
        "family_id": pos.get("family_id", ""),
        "score": float(pos.get("score") or 0.0),
        "qty_lots": int(pos["qty_lots"]),
        "lot_size": int(pos["lot_size"]),
        "entry_price": float(pos["entry_price"]),
        "exit_price": float(pos["last_ltp"]),
        "entry_created_at_ms": int(pos["entry_created_at_ms"]),
        "exit_created_at_ms": now_ms(),
        "holding_time_ms": now_ms() - int(pos["entry_created_at_ms"]),
        "exit_reason": exit_reason,
        "highest_seen": float(pos["highest_seen"]),
        "lowest_seen": float(pos["lowest_seen"]),
        "exit_ltp_source": ltp_source or {"source": "last_known_ltp", "fresh_ltp_ok": False},
        "exit_policy": c,
        "broker_order_sent": False,
        "paper_engine_used": False,
        "risk_execution_used": False,
        **metrics,
    }

    append_ndjson(exits_path(d), exit_obj)
    write_json(state_path(), {"status": "FLAT", "last_exit": exit_obj, "updated_at_ms": now_ms()})
    write_summary(d)

    return {
        "action": "EXIT_WRITTEN",
        "exit": exit_obj,
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
    }


def run_once() -> dict[str, Any]:
    if current_position() is None:
        result = enter_if_possible()
    else:
        result = update_or_exit()

    d = day()
    write_summary(d)
    result.setdefault("day", d)
    result.setdefault("final_classification", "PSHADOW_LIFECYCLE_V23_ONCE_COMPLETE_NO_BROKER_ORDER")
    result.setdefault("broker_order", 0)
    result.setdefault("paper_engine_order", 0)
    result.setdefault("risk_started", 0)
    result.setdefault("execution_started", 0)
    result.setdefault("redis_destructive", 0)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = run_once()

    if args.json:
        print(json.dumps(result, sort_keys=True))
        return 0

    print("FINAL_CLASSIFICATION=" + str(result.get("final_classification")))
    print("V23_ACTION=" + str(result.get("action")))
    print("REASON=" + str(result.get("reason", "")))

    if "position" in result:
        p = result["position"]
        print("POSITION_SYMBOL=" + str(p.get("symbol")))
        print("POSITION_ACTION=" + str(p.get("action")))
        print("POSITION_ENTRY_PRICE=" + str(p.get("entry_price")))
        print("POSITION_LAST_LTP=" + str(p.get("last_ltp")))
        print("POSITION_HIGH=" + str(p.get("highest_seen")))
        print("POSITION_LOW=" + str(p.get("lowest_seen")))
        print("MFE_POINTS=" + str(round(float(p.get("highest_seen", 0)) - float(p.get("entry_price", 0)), 4)))
        print("MAE_POINTS=" + str(round(float(p.get("lowest_seen", 0)) - float(p.get("entry_price", 0)), 4)))

    if "exit" in result:
        e = result["exit"]
        print("EXIT_SYMBOL=" + str(e.get("symbol")))
        print("EXIT_REASON=" + str(e.get("exit_reason")))
        print("EXIT_PRICE=" + str(e.get("exit_price")))
        print("PNL_POINTS_NET=" + str(e.get("pnl_points_net")))
        print("PNL_RUPEES_NET_PROXY=" + str(e.get("pnl_rupees_net_proxy")))
        print("MFE_POINTS=" + str(e.get("mfe_points")))
        print("MAE_POINTS=" + str(e.get("mae_points")))

    print("BROKER_ORDER=0")
    print("PAPER_ENGINE_ORDER=0")
    print("RISK_STARTED=0")
    print("EXECUTION_STARTED=0")
    print("REDIS_DESTRUCTIVE=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
