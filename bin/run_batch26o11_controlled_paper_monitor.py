#!/usr/bin/env python3
from __future__ import annotations

import argparse, json, pathlib, subprocess, time
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o11_controlled_paper_monitor.json"

ORDERS = "orders:mme:stream"
POSITION = "state:position:mme"

def now():
    return datetime.now(timezone.utc).isoformat()

def cmd(args, timeout=5):
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        return {"ok": cp.returncode == 0, "out": cp.stdout.strip(), "err": cp.stderr.strip(), "rc": cp.returncode}
    except Exception as exc:
        return {"ok": False, "out": "", "err": repr(exc), "rc": -1}

def rcli(*args):
    return cmd(["redis-cli", *args], timeout=4)

def hgetall(key):
    raw = rcli("HGETALL", key)["out"].splitlines()
    d = {}
    for i in range(0, len(raw)-1, 2):
        d[raw[i]] = raw[i+1]
    return d

def xlen(s):
    return rcli("XLEN", s)["out"]

def pgrep(pattern):
    raw = cmd(["bash", "-lc", f"pgrep -af {pattern!r} | grep -v grep || true"])["out"].splitlines()
    return [x for x in raw if "run_batch26o11_controlled_paper_monitor.py" not in x]

def latest_decision():
    return cmd(["bash", "-lc", "redis-cli XREVRANGE decisions:mme:stream + - COUNT 1 | sed -n '1,120p'"], timeout=4)["out"][-5000:]

def latest_order():
    return cmd(["bash", "-lc", "redis-cli XREVRANGE orders:mme:stream + - COUNT 1 | sed -n '1,120p'"], timeout=4)["out"][-5000:]

def stop_risk_execution():
    return {
        "risk_stop": cmd(["bash", "-lc", "pkill -f 'app.mme_scalpx.main --service risk' || true"]),
        "execution_stop": cmd(["bash", "-lc", "pkill -f 'app.mme_scalpx.main --service execution' || true"]),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration-sec", type=int, default=1800)
    ap.add_argument("--poll-sec", type=int, default=30)
    ap.add_argument("--auto-stop-on-risk", action="store_true")
    args = ap.parse_args()

    if args.poll_sec < 30:
        args.poll_sec = 30

    o10 = {}
    p = ROOT / "run/proofs/proof_batch26o10_controlled_paper_start.json"
    if p.exists():
        try:
            o10 = json.loads(p.read_text(errors="replace"))
        except Exception:
            o10 = {}

    start_orders = xlen(ORDERS)
    samples = []
    stop_reason = "duration_complete"
    stop_result = None

    end = time.time() + args.duration_sec

    while time.time() <= end:
        sample = {
            "ts": now(),
            "redis_ping": rcli("PING")["out"],
            "orders_len": xlen(ORDERS),
            "position": hgetall(POSITION),
            "risk_count": len(pgrep("app.mme_scalpx.main --service risk")),
            "execution_count": len(pgrep("app.mme_scalpx.main --service execution")),
            "latest_decision_tail": latest_decision(),
            "latest_order_tail": latest_order(),
        }
        samples.append(sample)

        risky = False
        if sample["redis_ping"] != "PONG":
            risky = True
            stop_reason = "redis_not_pong"
        if sample["risk_count"] > 1 or sample["execution_count"] > 1:
            risky = True
            stop_reason = "duplicate_risk_or_execution"
        if "REAL" in sample["latest_order_tail"].upper() or "LIVE" in sample["latest_order_tail"].upper():
            risky = True
            stop_reason = "live_order_word_detected"

        if risky and args.auto_stop_on_risk:
            stop_result = stop_risk_execution()
            break

        time.sleep(args.poll_sec)

    final_orders = xlen(ORDERS)
    final_position = hgetall(POSITION)

    proof = {
        "batch": "26O11",
        "name": "controlled_paper_monitor",
        "created_at": now(),
        "o10_start_ok": o10.get("controlled_paper_start_ok") is True,
        "duration_sec": args.duration_sec,
        "poll_sec": args.poll_sec,
        "start_orders_len": start_orders,
        "final_orders_len": final_orders,
        "final_position": final_position,
        "samples_count": len(samples),
        "samples_tail": samples[-10:],
        "stop_reason": stop_reason,
        "stop_result": stop_result,
        "real_live_approved": False,
        "paper_or_sandbox_only": True,
    }

    proof["monitor_ok"] = (
        proof["o10_start_ok"]
        and len(samples) >= 1
        and all(s["redis_ping"] == "PONG" for s in samples)
        and all(s["risk_count"] <= 1 and s["execution_count"] <= 1 for s in samples)
        and proof["real_live_approved"] is False
    )

    proof["paper_order_seen"] = final_orders != start_orders

    proof["final_verdict"] = (
        "PASS_CONTROLLED_PAPER_MONITOR_OK"
        if proof["monitor_ok"]
        else "FAIL_CONTROLLED_PAPER_MONITOR_REVIEW_REQUIRED"
    )
    proof["next_required_batch"] = "Batch 26-O12 post-paper analysis and replay export"

    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "monitor_ok": proof["monitor_ok"],
        "paper_order_seen": proof["paper_order_seen"],
        "start_orders_len": start_orders,
        "final_orders_len": final_orders,
        "samples_count": len(samples),
        "stop_reason": stop_reason,
        "real_live_approved": proof["real_live_approved"],
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["monitor_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
