#!/usr/bin/env python3
from __future__ import annotations

import json, os, pathlib, subprocess, time
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUT = ROOT / "run/proofs/proof_batch26o10_controlled_paper_start.json"

ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

ORDERS = "orders:mme:stream"
POSITION = "state:position:mme"
PROVIDER = "state:provider:runtime"

def now():
    return datetime.now(timezone.utc).isoformat()

def cmd(args, timeout=8, env=None):
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, env=env)
        return {"ok": cp.returncode == 0, "rc": cp.returncode, "out": cp.stdout.strip(), "err": cp.stderr.strip()}
    except Exception as exc:
        return {"ok": False, "rc": -1, "out": "", "err": repr(exc)}

def rcli(*args):
    return cmd(["redis-cli", *args], timeout=5)

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
    return [x for x in raw if "start_batch26o10_controlled_paper.py" not in x]

def is_flat(pos):
    return (
        pos.get("has_position") == "0"
        and pos.get("position_side") == "FLAT"
        and pos.get("qty_lots") == "0"
        and pos.get("qty_units") == "0"
    )

def read_json(path):
    p = ROOT / path
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(errors="replace"))
    except Exception:
        return {}

def start_service(service, logfile):
    env = dict(os.environ)
    env["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] = "1"
    env["SCALPX_CONTROLLED_PAPER_SCOPE_ACK"] = ACK
    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["ALLOW_LIVE_ORDERS"] = "0"
    env["LIVE_ORDERS_ALLOWED"] = "0"
    env["REAL_LIVE_ALLOWED"] = "0"
    env["TRADING_ENABLED"] = "0"

    log = ROOT / logfile
    log.parent.mkdir(parents=True, exist_ok=True)

    with log.open("ab") as f:
        p = subprocess.Popen(
            [
                str(ROOT / ".venv/bin/python"),
                "-m", "app.mme_scalpx.main",
                "--service", service,
                "--bootstrap-provider", "app.mme_scalpx.integrations.bootstrap_provider:provide",
                "--skip-group-bootstrap",
            ],
            cwd=ROOT,
            stdout=f,
            stderr=subprocess.STDOUT,
            env=env,
            stdin=subprocess.DEVNULL,
        )
    return {"service": service, "pid": p.pid, "log": str(log.relative_to(ROOT))}

def main():
    o8 = read_json("run/proofs/proof_batch26o8_live_25v_gate.json")
    o9 = read_json("run/proofs/proof_batch26o9_controlled_paper_preflight.json")
    pos = hgetall(POSITION)
    provider = hgetall(PROVIDER)

    before_risk = pgrep("app.mme_scalpx.main --service risk")
    before_execution = pgrep("app.mme_scalpx.main --service execution")
    before_orders = xlen(ORDERS)

    preflight = {
        "redis_ping": rcli("PING")["out"],
        "orders_zero": before_orders == "0",
        "position_flat": is_flat(pos),
        "o8_passed": o8.get("batch26o8_live_25v_gate_ok") is True,
        "o9_passed": o9.get("controlled_paper_preflight_ok") is True,
        "provider_ready_classic": provider.get("provider_ready_classic") == "True",
        "provider_ready_miso": provider.get("provider_ready_miso") == "False",
        "no_existing_risk": len(before_risk) == 0,
        "no_existing_execution": len(before_execution) == 0,
        "real_live_blocked": True,
        "scope_ack": ACK,
    }

    start_allowed = all(preflight.values())

    started = []
    if start_allowed:
        started.append(start_service("risk", f"run/controlled_paper/o10_risk_{int(time.time())}.log"))
        time.sleep(4)
        started.append(start_service("execution", f"run/controlled_paper/o10_execution_{int(time.time())}.log"))
        time.sleep(8)

    after_risk = pgrep("app.mme_scalpx.main --service risk")
    after_execution = pgrep("app.mme_scalpx.main --service execution")
    after_orders = xlen(ORDERS)
    after_pos = hgetall(POSITION)

    proof = {
        "batch": "26O10",
        "name": "controlled_paper_start",
        "created_at": now(),
        "preflight": preflight,
        "start_allowed": start_allowed,
        "started": started,
        "before": {
            "orders_len": before_orders,
            "risk_processes": before_risk,
            "execution_processes": before_execution,
            "position": pos,
        },
        "after": {
            "orders_len": after_orders,
            "risk_processes": after_risk,
            "execution_processes": after_execution,
            "risk_count": len(after_risk),
            "execution_count": len(after_execution),
            "position": after_pos,
        },
        "scope": {
            "family": "MIST",
            "side": "CALL",
            "quantity_lots": 1,
            "paper_or_sandbox_only": True,
            "real_live_allowed": False,
            "automatic_broker_failover_allowed": False,
            "mid_position_provider_migration_allowed": False,
        },
        "paper_start_allowed_by_this_batch": bool(start_allowed),
        "real_live_approved": False,
        "rollback_commands": [
            "pkill -f 'app.mme_scalpx.main --service risk'",
            "pkill -f 'app.mme_scalpx.main --service execution'",
            "redis-cli XLEN orders:mme:stream",
            "redis-cli HGETALL state:position:mme",
        ],
    }

    proof["controlled_paper_start_ok"] = (
        start_allowed
        and len(after_risk) == 1
        and len(after_execution) == 1
        and proof["scope"]["real_live_allowed"] is False
    )

    proof["final_verdict"] = (
        "PASS_CONTROLLED_PAPER_STARTED_MIST_CALL_1LOT"
        if proof["controlled_paper_start_ok"]
        else "FAIL_CONTROLLED_PAPER_START_REVIEW_REQUIRED"
    )
    proof["next_required_batch"] = (
        "Batch 26-O11 controlled paper live monitor"
        if proof["controlled_paper_start_ok"]
        else "Review O10 proof and do not continue"
    )

    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps({
        "final_verdict": proof["final_verdict"],
        "controlled_paper_start_ok": proof["controlled_paper_start_ok"],
        "paper_start_allowed_by_this_batch": proof["paper_start_allowed_by_this_batch"],
        "real_live_approved": proof["real_live_approved"],
        "risk_count": proof["after"]["risk_count"],
        "execution_count": proof["after"]["execution_count"],
        "orders_before": before_orders,
        "orders_after": after_orders,
        "next_required_batch": proof["next_required_batch"],
    }, indent=2, sort_keys=True))

    return 0 if proof["controlled_paper_start_ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
