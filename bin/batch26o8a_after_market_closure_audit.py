#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx")
OUTDIR = Path(sys.argv[1])
OUTDIR.mkdir(parents=True, exist_ok=True)

def sh(cmd: list[str], timeout: int = 10) -> str:
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return (p.stdout or "") + (p.stderr or "")
    except Exception as exc:
        return f"ERROR: {cmd}: {exc}"

def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(errors="replace"))
    except Exception:
        return None

def grep_files(pattern: str) -> list[Path]:
    return sorted(ROOT.glob(pattern))

def latest(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda p: p.stat().st_mtime)

def truthy(v: Any) -> bool:
    return v is True or str(v).lower() in ("true", "1", "pass", "ok")

def find_latest_json(patterns: list[str]) -> tuple[str, Path | None, Any]:
    found: list[Path] = []
    for pat in patterns:
        found.extend(grep_files(pat))
    p = latest(found)
    return (str(p.relative_to(ROOT)) if p else "", p, read_json(p) if p else None)

proofs = {}

proof_specs = {
    "O1_recovery_singleton_baseline": [
        "run/proofs/*26o1*recovery*singleton*.json",
        "run/proofs/*batch26o1*.json",
    ],
    "O2_position_flat_guard": [
        "run/proofs/*26o2*position*flat*.json",
        "run/proofs/*batch26o2*.json",
    ],
    "O3_provider_runtime_publication": [
        "run/proofs/*26o3*provider*runtime*.json",
        "run/proofs/*provider_runtime*publication*.json",
    ],
    "O4_feed_snapshot_publication": [
        "run/proofs/*26o4*feed*snapshot*.json",
        "run/proofs/*feed_snapshot*publication*.json",
    ],
    "O5_topology_ownership": [
        "run/proofs/*26o5*topology*.json",
        "run/proofs/*live_key_topology*.json",
    ],
    "O6_observer_guard": [
        "run/proofs/*26o6*observer*.json",
        "run/proofs/*observer_guard*.json",
    ],
    "O7_controlled_runtime_preflight": [
        "run/proofs/*26o7*controlled*.json",
        "run/proofs/*controlled_runtime_start_preflight*.json",
    ],
    "O8_install_or_gate": [
        "run/proofs/*26o8*live*25v*gate*.json",
        "run/proofs/*batch26o8*.json",
    ],
}

for name, pats in proof_specs.items():
    rel, path, obj = find_latest_json(pats)
    proofs[name] = {
        "latest_file": rel,
        "present": path is not None,
        "json_loaded": obj is not None,
        "top_level": obj if isinstance(obj, dict) else {},
    }

# Current runtime safety snapshot.
health = {
    "generated_at": datetime.now().isoformat(),
    "df_h_root": sh(["df", "-h", "/"]),
    "free_h": sh(["free", "-h"]),
    "redis_ping": sh(["redis-cli", "PING"], 3),
    "redis_memory": sh(["redis-cli", "INFO", "memory"], 5),
    "redis_persistence": sh(["redis-cli", "INFO", "persistence"], 5),
    "orders_xlen": sh(["redis-cli", "XLEN", "orders:mme:stream"], 5),
    "position": sh(["redis-cli", "HGETALL", "state:position:mme"], 5),
    "processes": sh([
        "bash", "-lc",
        "ps -eo pid,ppid,pcpu,pmem,etime,cmd | grep -E 'app.mme_scalpx.main|batch26|observer|redis-server|python' | grep -v grep || true"
    ]),
}

o8_script = ROOT / "bin/run_batch26o8_live_25v_gate.py"
o8_status = {
    "script_path": str(o8_script.relative_to(ROOT)),
    "exists": o8_script.exists(),
    "executable": os.access(o8_script, os.X_OK) if o8_script.exists() else False,
    "compile_ok": False,
    "compile_output": "",
}
if o8_script.exists():
    cp = sh([sys.executable, "-m", "py_compile", str(o8_script)], 10)
    o8_status["compile_output"] = cp
    o8_status["compile_ok"] = "Traceback" not in cp and "Error" not in cp

# Closure matrix.
closure = [
    {
        "earlier_gap": "Disk full / Redis MISCONF / memory pressure",
        "addressed_by": "26-O0 + VM upgrade + Redis 6GB cap",
        "after_market_status": "CLOSED_IF_CURRENT_HEALTH_OK",
        "live_dependency": "Monitor disk <85%, Redis PONG, bgsave ok during session",
    },
    {
        "earlier_gap": "Position hash empty / unsafe paper start state",
        "addressed_by": "26-O2 position FLAT guard",
        "after_market_status": "CLOSED_IF_POSITION_FLAT_AND_ORDERS_ZERO",
        "live_dependency": "Re-check immediately before O9/P0",
    },
    {
        "earlier_gap": "Provider runtime missing/not canonical",
        "addressed_by": "26-O3 provider runtime publication",
        "after_market_status": "STRUCTURALLY_CLOSED",
        "live_dependency": "O8 live provider_runtime proof must pass",
    },
    {
        "earlier_gap": "Feed snapshot hashes missing/not canonical",
        "addressed_by": "26-O4 feed snapshot publication",
        "after_market_status": "STRUCTURALLY_CLOSED",
        "live_dependency": "O8 live feed_snapshot proof must pass",
    },
    {
        "earlier_gap": "Redis key topology mismatch between feeds/features/proofs",
        "addressed_by": "26-O5R2 topology ownership correction",
        "after_market_status": "STRUCTURALLY_CLOSED",
        "live_dependency": "O8 live feature_payload/family_surfaces must pass",
    },
    {
        "earlier_gap": "Heavy watchers caused Redis/disk pressure",
        "addressed_by": "26-O6 lightweight observer guard",
        "after_market_status": "CLOSED_IF_NO_HEAVY_WATCHERS_RUNNING",
        "live_dependency": "Use only one lightweight observer tomorrow",
    },
    {
        "earlier_gap": "Risk/execution duplicate or unsafe start risk",
        "addressed_by": "26-O7R controlled runtime start preflight",
        "after_market_status": "STRUCTURALLY_CLOSED",
        "live_dependency": "O9 controlled paper preflight must pass",
    },
    {
        "earlier_gap": "Need one live 25V go/no-go gate",
        "addressed_by": "26-O8 aggregator install",
        "after_market_status": "INSTALLED_NOT_LIVE_PASSED",
        "live_dependency": "Run O8 with --run during market",
    },
    {
        "earlier_gap": "O2 false flags mixed good-false safety flags with bad-false readiness flags",
        "addressed_by": "Reporting classification",
        "after_market_status": "CLOSED_BY_POLICY",
        "live_dependency": "Future reports must classify false safety flags separately",
    },
    {
        "earlier_gap": "MIST dry paper not tied to canonical candidate/PnL artifact",
        "addressed_by": "Not yet fully solved",
        "after_market_status": "OPEN_REPORTING_DEBT",
        "live_dependency": "Candidate-shadow/PnL artifact needed after O8 live pass",
    },
    {
        "earlier_gap": "No event-level deduplication of repeated family surface blocker counts",
        "addressed_by": "Not yet fully solved",
        "after_market_status": "OPEN_REPORTING_DEBT",
        "live_dependency": "Useful after O8 live pass; not blocker for O8",
    },
    {
        "earlier_gap": "MISO runtime_disabled ambiguity",
        "addressed_by": "Scope decision",
        "after_market_status": "ACCEPT_AS_INTENTIONAL_IF_MISO_NOT_IN_PAPER_SCOPE",
        "live_dependency": "If MISO shadow required, set explicit non-DISABLED shadow mode later",
    },
    {
        "earlier_gap": "No hypothetical PnL when no candidate/entry/exit exists",
        "addressed_by": "Artifact design required",
        "after_market_status": "OPEN_REPORTING_DEBT",
        "live_dependency": "Only computable after candidates emit entry/exit reference prices",
    },
]

# Basic computed verdict.
redis_ok = "PONG" in health["redis_ping"]
persistence_ok = "rdb_last_bgsave_status:ok" in health["redis_persistence"]
orders_zero = bool(re.search(r"\b0\b", health["orders_xlen"]))
position_flat = "position_side\nFLAT" in health["position"] or "position_side\r\nFLAT" in health["position"] or "has_position\n0" in health["position"]

install_ready = bool(o8_status["exists"] and o8_status["compile_ok"])

hard_after_market_blockers = []
if not redis_ok:
    hard_after_market_blockers.append("Redis PING failed")
if not persistence_ok:
    hard_after_market_blockers.append("Redis persistence not ok")
if not orders_zero:
    hard_after_market_blockers.append("orders:mme:stream not zero")
if not position_flat:
    hard_after_market_blockers.append("position state not FLAT-safe")
if not install_ready:
    hard_after_market_blockers.append("O8 live gate script missing or not compiling")

after_market_verdict = "PASS_AFTER_MARKET_READY_FOR_O8_LIVE_RUN" if not hard_after_market_blockers else "FAIL_AFTER_MARKET_FIX_REQUIRED"

result = {
    "generated_at": datetime.now().isoformat(),
    "after_market_verdict": after_market_verdict,
    "hard_after_market_blockers": hard_after_market_blockers,
    "proofs": proofs,
    "o8_status": o8_status,
    "health": health,
    "closure": closure,
    "tomorrow_command": "BATCH25V_OBSERVE_SECONDS=60 .venv/bin/python bin/run_batch26o8_live_25v_gate.py --run --observe-seconds 60 --timeout-sec 120",
    "go_no_go_rule": "No O9 or paper start until O8 live gate returns PASS_BATCH26O8_LIVE_25V_GATE_OK.",
}

(OUTDIR / "closure_audit.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

md = []
md.append("# Batch 26-O8A After-Market Blocker Closure Audit")
md.append("")
md.append(f"Generated: `{result['generated_at']}`")
md.append("")
md.append("## Verdict")
md.append("")
md.append(f"```text\n{after_market_verdict}\n```")
md.append("")
md.append("## Hard After-Market Blockers")
md.append("")
if hard_after_market_blockers:
    for b in hard_after_market_blockers:
        md.append(f"- {b}")
else:
    md.append("- None.")
md.append("")
md.append("## Current Safety Snapshot")
md.append("")
md.append("```text")
md.append("Redis PING:")
md.append(health["redis_ping"].strip())
md.append("")
md.append("Redis persistence:")
md.append("\n".join([x for x in health["redis_persistence"].splitlines() if "rdb_last_bgsave_status" in x or "rdb_bgsave_in_progress" in x or "rdb_changes_since_last_save" in x]))
md.append("")
md.append("Orders:")
md.append(health["orders_xlen"].strip())
md.append("")
md.append("Position:")
md.append(health["position"].strip())
md.append("```")
md.append("")
md.append("## O8 Aggregator")
md.append("")
md.append(f"- Script exists: `{o8_status['exists']}`")
md.append(f"- Script executable: `{o8_status['executable']}`")
md.append(f"- Script compile OK: `{o8_status['compile_ok']}`")
md.append("")
md.append("## Closure Matrix")
md.append("")
md.append("| Earlier gap | Addressed by | After-market status | Live dependency |")
md.append("|---|---|---|---|")
for r in closure:
    md.append(f"| {r['earlier_gap']} | {r['addressed_by']} | {r['after_market_status']} | {r['live_dependency']} |")
md.append("")
md.append("## Tomorrow Go/No-Go")
md.append("")
md.append("Run only during live market after feeds/features/strategy are up:")
md.append("")
md.append("```bash")
md.append(result["tomorrow_command"])
md.append("```")
md.append("")
md.append("Required:")
md.append("")
md.append("```text")
md.append("PASS_BATCH26O8_LIVE_25V_GATE_OK")
md.append("```")
md.append("")
md.append("No O9 or controlled paper start until O8 live gate passes.")
md.append("")
(OUTDIR / "REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

print("===== BATCH 26-O8A AFTER-MARKET CLOSURE AUDIT COMPLETE =====")
print(f"OUTDIR={OUTDIR}")
print(f"REPORT={OUTDIR / 'REPORT.md'}")
print("")
print((OUTDIR / "REPORT.md").read_text(encoding="utf-8"))
