from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from app.mme_scalpx.core.redisx import get_redis_client
from app.mme_scalpx.shadow_paper.config import load_config
from app.mme_scalpx.shadow_paper.ltp_reader import find_live_ltp
from app.mme_scalpx.shadow_paper.models import ShadowExit, ShadowOpenPosition
from app.mme_scalpx.shadow_paper.pnl import calculate_long_option_metrics
from app.mme_scalpx.shadow_paper.report import write_daily_summary


def now_ms() -> int:
    return int(time.time() * 1000)


def today() -> str:
    return time.strftime("%Y%m%d")


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
    out: list[dict[str, Any]] = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def latest_pshadow_event(day: str) -> dict[str, Any] | None:
    path = Path("run/paper_shadow") / f"pshadowgate_shadow_paper_events_{day}.ndjson"
    rows = read_ndjson(path)
    valid = []
    for row in rows:
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
    if not valid:
        return None
    return valid[-1]


def entries_path(day: str) -> Path:
    return Path("run/paper_shadow_lifecycle") / f"entries_{day}.ndjson"


def exits_path(day: str) -> Path:
    return Path("run/paper_shadow_lifecycle") / f"exits_{day}.ndjson"


def state_path() -> Path:
    return Path("run/state/pshadowgate_lifecycle/open_position.json")


def count_today_entries(day: str) -> int:
    return len(read_ndjson(entries_path(day)))


def already_entered(day: str, event_id: str) -> bool:
    for row in read_ndjson(entries_path(day)):
        if row.get("event_id") == event_id:
            return True
    return False


def open_position() -> ShadowOpenPosition | None:
    data = read_json(state_path())
    if not data or data.get("status") != "OPEN":
        return None
    return ShadowOpenPosition(**data)


def save_open(pos: ShadowOpenPosition) -> None:
    write_json(state_path(), pos.to_dict())


def clear_open(exit_obj: ShadowExit) -> None:
    write_json(
        state_path(),
        {
            "status": "FLAT",
            "last_exit": exit_obj.to_dict(),
            "updated_at_ms": now_ms(),
        },
    )


def safety_streams_zero() -> tuple[bool, dict[str, int]]:
    r = get_redis_client()
    streams = {
        "risk": "risk:mme:stream",
        "execution": "execution:mme:stream",
        "orders": "orders:mme:stream",
        "trades": "trades:ledger:stream",
        "cmd": "cmd:mme:stream",
    }
    vals = {}
    for k, s in streams.items():
        try:
            vals[k] = int(r.xlen(s))
        except Exception:
            vals[k] = -1
    return all(v == 0 for v in vals.values()), vals


def enter_if_possible() -> dict[str, Any]:
    cfg = load_config()
    day = today()
    r = get_redis_client()

    if not cfg.enabled:
        return {"action": "NO_ENTRY", "reason": "lifecycle_disabled"}

    zero, safety = safety_streams_zero()
    if not zero:
        return {"action": "NO_ENTRY", "reason": "safety_streams_not_zero", "safety": safety}

    if cfg.one_open_position_only and open_position() is not None:
        return {"action": "NO_ENTRY", "reason": "open_position_exists"}

    if count_today_entries(day) >= cfg.max_daily_trades:
        return {"action": "NO_ENTRY", "reason": "max_daily_trades_reached"}

    event = latest_pshadow_event(day)
    if not event:
        return {"action": "NO_ENTRY", "reason": "no_valid_pshadow_event"}

    event_id = str(event.get("event_id") or "")
    created_at_ms = int(event.get("created_at_ms") or 0)
    event_age_ms = now_ms() - created_at_ms

    if already_entered(day, event_id):
        return {"action": "NO_ENTRY", "reason": "event_already_entered", "event_id": event_id}

    if event_age_ms > cfg.entry_event_max_age_ms:
        return {
            "action": "NO_ENTRY",
            "reason": "entry_event_too_old",
            "event_age_ms": event_age_ms,
            "max_ms": cfg.entry_event_max_age_ms,
        }

    ltp = find_live_ltp(
        redis_client=r,
        symbol=str(event.get("symbol") or ""),
        instrument_token=str(event.get("instrument_token") or ""),
        max_age_ms=cfg.ltp_max_age_ms,
    )

    if ltp is None:
        return {"action": "NO_ENTRY", "reason": "no_fresh_ltp_found", "event": event}

    if not (cfg.min_entry_price <= ltp.ltp <= cfg.max_entry_price):
        return {
            "action": "NO_ENTRY",
            "reason": "ltp_out_of_range",
            "ltp": ltp.to_dict(),
            "min_entry_price": cfg.min_entry_price,
            "max_entry_price": cfg.max_entry_price,
        }

    pos = ShadowOpenPosition(
        event_id=event_id,
        source_decision_id=str(event.get("source_decision_id") or ""),
        action=str(event.get("action") or ""),
        symbol=str(event.get("symbol") or ""),
        instrument_token=str(event.get("instrument_token") or ""),
        family_id=str(event.get("family_id") or ""),
        score=float(event.get("score") or 0.0),
        qty_lots=int(event.get("qty_lots") or 1),
        lot_size=cfg.lot_size,
        entry_price=float(ltp.ltp),
        entry_created_at_ms=now_ms(),
        entry_ltp_source=ltp.to_dict(),
        highest_seen=float(ltp.ltp),
        lowest_seen=float(ltp.ltp),
        last_ltp=float(ltp.ltp),
        last_ltp_at_ms=now_ms(),
    )

    save_open(pos)
    append_ndjson(entries_path(day), pos.to_dict())
    write_daily_summary(day)

    return {
        "action": "ENTRY_WRITTEN",
        "position": pos.to_dict(),
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
    }


def update_or_exit() -> dict[str, Any]:
    cfg = load_config()
    day = today()
    r = get_redis_client()

    pos = open_position()
    if pos is None:
        return {"action": "NO_POSITION", "reason": "flat"}

    zero, safety = safety_streams_zero()
    if not zero:
        return {"action": "NO_EXIT", "reason": "safety_streams_not_zero", "safety": safety}

    ltp = find_live_ltp(
        redis_client=r,
        symbol=pos.symbol,
        instrument_token=pos.instrument_token,
        max_age_ms=cfg.ltp_max_age_ms,
    )
    if ltp is None:
        return {"action": "NO_EXIT", "reason": "no_fresh_ltp_found", "position": pos.to_dict()}

    current = float(ltp.ltp)
    pos.last_ltp = current
    pos.last_ltp_at_ms = now_ms()
    pos.highest_seen = max(float(pos.highest_seen), current)
    pos.lowest_seen = min(float(pos.lowest_seen), current)

    age_ms = now_ms() - int(pos.entry_created_at_ms)
    exit_reason = ""

    if current <= float(pos.entry_price) - cfg.synthetic_sl_points:
        exit_reason = "SYNTHETIC_STOP_LOSS"
    elif current >= float(pos.entry_price) + cfg.synthetic_tp_points:
        exit_reason = "SYNTHETIC_TARGET_HIT"
    elif age_ms >= cfg.max_holding_time_ms:
        exit_reason = "SYNTHETIC_MAX_HOLDING_TIME"

    if not exit_reason:
        save_open(pos)
        write_daily_summary(day)
        return {
            "action": "POSITION_UPDATED",
            "position": pos.to_dict(),
            "unrealized_pnl_points_proxy": round(current - float(pos.entry_price), 4),
            "broker_order": 0,
            "paper_engine_order": 0,
            "risk_started": 0,
            "execution_started": 0,
        }

    metrics = calculate_long_option_metrics(
        entry_price=float(pos.entry_price),
        exit_price=current,
        highest_seen=float(pos.highest_seen),
        lowest_seen=float(pos.lowest_seen),
        qty_lots=int(pos.qty_lots),
        lot_size=int(pos.lot_size),
        assumed_slippage_points=float(cfg.assumed_slippage_points),
    )

    exit_obj = ShadowExit(
        event_id=pos.event_id,
        source_decision_id=pos.source_decision_id,
        action=pos.action,
        symbol=pos.symbol,
        instrument_token=pos.instrument_token,
        family_id=pos.family_id,
        score=float(pos.score),
        qty_lots=int(pos.qty_lots),
        lot_size=int(pos.lot_size),
        entry_price=float(pos.entry_price),
        exit_price=current,
        entry_created_at_ms=int(pos.entry_created_at_ms),
        exit_created_at_ms=now_ms(),
        holding_time_ms=age_ms,
        exit_reason=exit_reason,
        highest_seen=float(pos.highest_seen),
        lowest_seen=float(pos.lowest_seen),
        exit_ltp_source=ltp.to_dict(),
        **metrics,
    )

    append_ndjson(exits_path(day), exit_obj.to_dict())
    clear_open(exit_obj)
    summary_path = write_daily_summary(day)

    return {
        "action": "EXIT_WRITTEN",
        "exit": exit_obj.to_dict(),
        "summary_path": str(summary_path),
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
    }


def run_once() -> dict[str, Any]:
    pos = open_position()
    if pos is None:
        result = enter_if_possible()
    else:
        result = update_or_exit()

    day = today()
    write_daily_summary(day)
    result.setdefault("day", day)
    result.setdefault("final_classification", "PSHADOW_LIFECYCLE_V2_ONCE_COMPLETE_NO_BROKER_ORDER")
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
    else:
        print("FINAL_CLASSIFICATION=" + str(result.get("final_classification")))
        print("LIFECYCLE_ACTION=" + str(result.get("action")))
        print("REASON=" + str(result.get("reason", "")))
        if "position" in result:
            p = result["position"]
            print("POSITION_SYMBOL=" + str(p.get("symbol")))
            print("POSITION_ACTION=" + str(p.get("action")))
            print("POSITION_ENTRY_PRICE=" + str(p.get("entry_price")))
            print("POSITION_LAST_LTP=" + str(p.get("last_ltp")))
            print("POSITION_HIGH=" + str(p.get("highest_seen")))
            print("POSITION_LOW=" + str(p.get("lowest_seen")))
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
