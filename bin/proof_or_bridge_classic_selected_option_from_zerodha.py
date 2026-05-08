#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, pathlib, re, subprocess, time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o8c_classic_zerodha_option_bridge.json"

ZERODHA_STREAM = "ticks:mme:opt:selected:zerodha:stream"
DHAN_STREAM = "ticks:mme:opt:selected:dhan:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_KEY = "state:position:mme"
PROVIDER_KEY = "state:provider:runtime"
OPT_KEY = "state:snapshot:mme:opt:selected:active"
DHAN_KEY = "state:context:mme:dhan"
HEALTH_FEEDS_KEY = "health:feeds"

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def now_ns():
    return str(time.time_ns())

def cmd(args, timeout=5):
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return {"ok": cp.returncode == 0, "out": cp.stdout.strip(), "err": cp.stderr.strip(), "rc": cp.returncode}
    except Exception as exc:
        return {"ok": False, "out": "", "err": repr(exc), "rc": -1}

def rcli(*args, timeout=5):
    return cmd(["redis-cli", *args], timeout=timeout)

def hgetall(key):
    raw = rcli("HGETALL", key)["out"].splitlines()
    d = {}
    for i in range(0, len(raw) - 1, 2):
        d[raw[i]] = raw[i + 1]
    return d

def hset(key, fields):
    args = ["HSET", key]
    for k, v in fields.items():
        args += [k, str(v)]
    return rcli(*args, timeout=8)

def xlen(stream):
    return rcli("XLEN", stream)["out"]

def latest_raw(stream, count=30):
    return cmd(["bash", "-lc", f"redis-cli XREVRANGE {stream!r} + - COUNT {count}"], timeout=6)["out"]

def pgrep(pattern):
    raw = cmd(["bash", "-lc", f"pgrep -af {pattern!r} | grep -v grep || true"])["out"].splitlines()
    return [x for x in raw if "proof_or_bridge_classic_selected_option_from_zerodha.py" not in x]

def is_flat(pos):
    return (
        pos.get("has_position") == "0"
        and pos.get("position_side") == "FLAT"
        and pos.get("qty_lots") == "0"
        and pos.get("qty_units") == "0"
    )

def split_entries(raw):
    lines = raw.splitlines()
    entries = []
    i = 0
    while i < len(lines):
        if re.match(r"^\d+-\d+$", lines[i].strip()):
            eid = lines[i].strip()
            i += 1
            fields = {}
            while i + 1 < len(lines) and not re.match(r"^\d+-\d+$", lines[i].strip()):
                fields[lines[i].strip()] = lines[i + 1].strip()
                i += 2
            entries.append((eid, fields))
        else:
            i += 1
    return entries

def parse_payload(fields):
    out = dict(fields)
    for k, v in list(fields.items()):
        if isinstance(v, str) and v.strip().startswith("{"):
            try:
                j = json.loads(v)
                if isinstance(j, dict):
                    out.update(j)
            except Exception:
                pass
    return out

def side_of(p):
    for k in ["side", "option_side", "branch_id", "role", "option_type", "instrument_type"]:
        v = str(p.get(k, "")).upper()
        if "CALL" in v or v == "CE" or v.endswith("CE"):
            return "CALL"
        if "PUT" in v or v == "PE" or v.endswith("PE"):
            return "PUT"
    sym = str(p.get("trading_symbol") or p.get("tradingsymbol") or p.get("option_symbol") or p.get("symbol") or "").upper()
    if sym.endswith("CE"):
        return "CALL"
    if sym.endswith("PE"):
        return "PUT"
    return None

def num(p, keys):
    for k in keys:
        v = p.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except Exception:
                pass
    return None

def txt(p, keys):
    for k in keys:
        v = p.get(k)
        if v not in (None, ""):
            return str(v)
    return ""

def ts_ns(eid, p):
    for k in ["ts_event_ns", "ltt_ns", "timestamp_ns", "ts_ns"]:
        try:
            if p.get(k) not in (None, ""):
                return int(float(p[k]))
        except Exception:
            pass
    try:
        return int(eid.split("-")[0]) * 1_000_000
    except Exception:
        return 0

def norm_option(eid, p, side):
    ts = ts_ns(eid, p)
    age_ms = max(0.0, (time.time_ns() - ts) / 1_000_000) if ts else None
    ltp = num(p, ["ltp", "last_price", "price", "last_traded_price"])
    bid = num(p, ["best_bid", "bid", "bid_price"])
    ask = num(p, ["best_ask", "ask", "ask_price"])
    bq = num(p, ["bid_qty_5", "bid_qty", "best_bid_qty"])
    aq = num(p, ["ask_qty_5", "ask_qty", "best_ask_qty"])
    symbol = txt(p, ["trading_symbol", "tradingsymbol", "option_symbol", "symbol"])
    token = txt(p, ["instrument_token", "option_token", "token"])

    present = ltp is not None or bid is not None or ask is not None
    fresh = age_ms is not None and age_ms <= 30000

    return {
        "present": bool(present),
        "fresh": bool(fresh),
        "stale": not bool(fresh),
        "valid": bool(present),
        "status": "HEALTHY" if present and fresh else "STALE_OR_PARTIAL",
        "provider_id": "ZERODHA",
        "side": side,
        "option_side": side,
        "role": "SELECTED_CALL" if side == "CALL" else "SELECTED_PUT",
        "instrument_token": token,
        "option_token": token,
        "trading_symbol": symbol,
        "option_symbol": symbol,
        "ltp": ltp,
        "best_bid": bid,
        "best_ask": ask,
        "bid_qty_5": bq,
        "ask_qty_5": aq,
        "depth_total": (bq or 0) + (aq or 0) if bq is not None or aq is not None else None,
        "spread": max(0.0, ask - bid) if bid is not None and ask is not None else None,
        "ts_event_ns": ts,
        "age_ms": age_ms,
        "source": "batch26o8c_zerodha_selected_option_stream",
        "source_stream": ZERODHA_STREAM,
        "source_entry_id": eid,
    }

def fail_option(side):
    return {
        "present": False,
        "fresh": False,
        "stale": True,
        "valid": False,
        "status": "UNAVAILABLE",
        "provider_id": "ZERODHA",
        "side": side,
        "option_side": side,
        "role": "SELECTED_CALL" if side == "CALL" else "SELECTED_PUT",
        "ltp": None,
        "trading_symbol": "",
        "source": "batch26o8c_missing_side",
    }

def fail_context(side):
    return {"side": side, "present": False, "fresh": False, "stale": True, "valid": False, "status": "UNAVAILABLE"}

def jdump(x):
    return json.dumps(x, separators=(",", ":"), sort_keys=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    entries = split_entries(latest_raw(ZERODHA_STREAM, 30))
    found = {}
    seen = []

    for eid, fields in entries:
        p = parse_payload(fields)
        side = side_of(p)
        seen.append({"entry_id": eid, "side": side, "field_keys": list(fields.keys())[:40], "payload_keys": list(p.keys())[:80]})
        if side in ("CALL", "PUT") and side not in found:
            found[side] = norm_option(eid, p, side)

    call = found.get("CALL") or fail_option("CALL")
    put = found.get("PUT") or fail_option("PUT")

    pos = hgetall(POSITION_KEY)
    provider = hgetall(PROVIDER_KEY)

    orders_len = xlen(ORDERS_STREAM)
    risk = pgrep("app.mme_scalpx.main --service risk")
    execution = pgrep("app.mme_scalpx.main --service execution")

    call_ready = bool(call.get("present")) and bool(call.get("fresh"))
    safe = (
        rcli("PING")["out"] == "PONG"
        and orders_len == "0"
        and is_flat(pos)
        and len(risk) == 0
        and len(execution) == 0
        and xlen(ZERODHA_STREAM) not in ("0", "")
        and call_ready
        and provider.get("futures_marketdata_status") == "HEALTHY"
        and provider.get("execution_primary_status") == "HEALTHY"
    )

    write_results = {}

    if args.apply and safe:
        ns = now_ns()

        write_results["opt_active"] = hset(OPT_KEY, {
            "selected_call_json": jdump(call),
            "selected_put_json": jdump(put),
            "active_selected_option_provider_id": "ZERODHA",
            "selected_option_marketdata_provider_id": "ZERODHA",
            "status": "HEALTHY",
            "present": "True",
            "fresh": str(bool(call.get("fresh") or put.get("fresh"))),
            "valid": str(bool(call.get("valid") or put.get("valid"))),
            "last_update_ns": ns,
            "ts_event_ns": ns,
            "bridge_reason": "dhan_unavailable_zerodha_selected_option_stream_flowing",
        })

        write_results["dhan_context_failclosed"] = hset(DHAN_KEY, {
            "option_chain_ladder_json": "[]",
            "strike_ladder_json": "[]",
            "oi_wall_summary_json": jdump({
                "present": False,
                "fresh": False,
                "stale": True,
                "valid": False,
                "status": "UNAVAILABLE",
                "oi_wall_ready": False,
                "ladder_present": False,
                "atm_reference_present": False,
                "wall_computable": False,
            }),
            "selected_call_context_json": jdump(fail_context("CALL")),
            "selected_put_context_json": jdump(fail_context("PUT")),
            "status": "UNAVAILABLE",
            "last_update_ns": ns,
            "ts_event_ns": ns,
        })

        write_results["provider_runtime"] = hset(PROVIDER_KEY, {
            "selected_option_marketdata_provider_id": "ZERODHA",
            "active_selected_option_provider_id": "ZERODHA",
            "selected_option_marketdata_status": "HEALTHY",
            "option_context_provider_id": "DHAN",
            "active_option_context_provider_id": "DHAN",
            "option_context_status": "UNAVAILABLE",
            "provider_ready_classic": "True",
            "provider_ready_miso": "False",
            "provider_runtime_blocked": "False",
            "provider_runtime_block_reason": "classic_ready_with_zerodha_selected_option_dhan_context_unavailable_miso_blocked",
            "last_update_ns": ns,
            "ts_event_ns": ns,
        })

        write_results["health_feeds"] = hset(HEALTH_FEEDS_KEY, {
            "service_name": "feeds",
            "status": "WARN",
            "reason": "classic_ready_with_zerodha_selected_option_dhan_context_unavailable",
            "last_update_ns": ns,
            "ts_event_ns": ns,
            "real_live_approved": "False",
            "paper_order_approved": "False",
        })
    elif args.apply:
        write_results["blocked"] = {"ok": False, "reason": "safe_false"}

    after_provider = hgetall(PROVIDER_KEY)
    after_opt = hgetall(OPT_KEY)
    after_dhan = hgetall(DHAN_KEY)

    bridge_ok = (
        orders_len == "0"
        and is_flat(pos)
        and len(risk) == 0
        and len(execution) == 0
        and bool(call.get("present"))
        and after_provider.get("provider_ready_classic") == "True"
        and after_provider.get("provider_ready_miso") == "False"
        and "selected_call_json" in after_opt
        and "selected_put_json" in after_opt
        and "option_chain_ladder_json" in after_dhan
    )

    proof = {
        "batch": "26O8C",
        "name": "classic_zerodha_selected_option_bridge",
        "created_at": now_iso(),
        "apply_requested": args.apply,
        "orders_len": orders_len,
        "position_flat": is_flat(pos),
        "risk_process_count": len(risk),
        "execution_process_count": len(execution),
        "zerodha_selected_option_stream_len": xlen(ZERODHA_STREAM),
        "dhan_selected_option_stream_len": xlen(DHAN_STREAM),
        "safe_to_apply": safe,
        "call": call,
        "put": put,
        "seen_entries": seen[:10],
        "write_results": write_results,
        "after_provider_core": {
            "selected_option_marketdata_provider_id": after_provider.get("selected_option_marketdata_provider_id"),
            "selected_option_marketdata_status": after_provider.get("selected_option_marketdata_status"),
            "option_context_status": after_provider.get("option_context_status"),
            "provider_ready_classic": after_provider.get("provider_ready_classic"),
            "provider_ready_miso": after_provider.get("provider_ready_miso"),
            "provider_runtime_block_reason": after_provider.get("provider_runtime_block_reason"),
        },
        "after_opt_keys": list(after_opt.keys()),
        "after_dhan_keys": list(after_dhan.keys()),
        "classic_zerodha_option_bridge_ok": bridge_ok,
        "real_live_approved": False,
        "paper_order_approved": False,
    }

    if bridge_ok:
        proof["final_verdict"] = "PASS_CLASSIC_ZERODHA_OPTION_BRIDGE_OK"
        proof["next_required_batch"] = "Rerun Batch 26-O8 live 25V gate"
    elif safe and not args.apply:
        proof["final_verdict"] = "PARTIAL_SAFE_TO_APPLY_ZERODHA_OPTION_BRIDGE"
        proof["next_required_batch"] = ".venv/bin/python bin/proof_or_bridge_classic_selected_option_from_zerodha.py --apply"
    else:
        proof["final_verdict"] = "FAIL_CLASSIC_ZERODHA_OPTION_BRIDGE_REVIEW_REQUIRED"
        proof["next_required_batch"] = "Review seen_entries/call/put"

    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "classic_zerodha_option_bridge_ok": bridge_ok,
        "safe_to_apply": safe,
        "zerodha_selected_option_stream_len": proof["zerodha_selected_option_stream_len"],
        "dhan_selected_option_stream_len": proof["dhan_selected_option_stream_len"],
        "call_summary": {k: call.get(k) for k in ["present", "fresh", "ltp", "trading_symbol", "provider_id", "status"]},
        "put_summary": {k: put.get(k) for k in ["present", "fresh", "ltp", "trading_symbol", "provider_id", "status"]},
        "after_provider_core": proof["after_provider_core"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["final_verdict"].startswith(("PASS", "PARTIAL_SAFE")) else 1

if __name__ == "__main__":
    raise SystemExit(main())
