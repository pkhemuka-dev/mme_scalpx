#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
os.chdir(ROOT)

ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

PYBIN = ROOT / ".venv/bin/python"
if not PYBIN.exists():
    PYBIN = Path(sys.executable)

os.environ["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] = "1"
os.environ["SCALPX_CONTROLLED_PAPER_SCOPE_ACK"] = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

from app.mme_scalpx.services.controlled_paper_runtime import controlled_runtime_report

report = controlled_runtime_report(ignore_time_gate=False)
if report.get("enabled") is not True:
    out = {
        "start_refused": True,
        "reason": report.get("reason"),
        "controlled_runtime_report": report,
        "real_live_allowed": False,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    raise SystemExit(1)

services = ["features", "strategy", "risk", "execution"]
log_dir = ROOT / "run/controlled_paper"
log_dir.mkdir(parents=True, exist_ok=True)

def pgrep() -> str:
    return subprocess.run(
        ["bash", "-lc", "pgrep -af 'app.mme_scalpx.main|pfeeds|mme_scalpx' || true"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    ).stdout

before = pgrep()
started = []
already = []

for service in services:
    if f"--service {service}" in before:
        already.append(service)
        continue

    log_path = log_dir / f"{service}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    cmd = [
        str(PYBIN),
        "-m",
        "app.mme_scalpx.main",
        "--service",
        service,
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ]

    with log_path.open("ab") as log:
        proc = subprocess.Popen(
            cmd,
            cwd=ROOT,
            env=os.environ.copy(),
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    started.append({"service": service, "pid": proc.pid, "log": str(log_path.relative_to(ROOT))})
    time.sleep(1)

time.sleep(3)
after = pgrep()

proof = {
    "proof": "start_controlled_paper_runtime_chain",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "controlled_runtime_report": report,
    "services_requested": services,
    "already_running": already,
    "started": started,
    "processes_before": before,
    "processes_after": after,
    "real_live_allowed": False,
    "selected_family": "MIST",
    "selected_side": "CALL",
    "quantity_lots": 1,
}

out = ROOT / "run/proofs/start_controlled_paper_runtime_chain.json"
out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

print(json.dumps({
    "start_controlled_paper_runtime_chain_written": str(out.relative_to(ROOT)),
    "already_running": already,
    "started": started,
    "real_live_allowed": False,
}, indent=2, sort_keys=True))
