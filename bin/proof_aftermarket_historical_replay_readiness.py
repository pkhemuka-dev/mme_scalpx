#!/usr/bin/env python3
from __future__ import annotations

"""
After-market historical replay readiness proof.

Read-only inventory proof:
- detects recorded/historical data files
- detects replay runner/proof scripts
- detects existing replay proof artifacts
- does not write live Redis
- does not call broker APIs
- does not place orders

This is not a full semantic replay pass. It tells us whether the project has
enough local historical material and replay tooling to proceed to a full
after-market replay dry-run batch.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "run" / "proofs" / "proof_aftermarket_historical_replay_readiness.json"

DATA_ROOTS = [
    "run/recordings",
    "run/replay",
    "run/research_capture",
    "run/research_capture/archive",
    "run/archive",
    "run/data",
    "data",
    "archive",
]

DATA_SUFFIXES = {
    ".jsonl",
    ".ndjson",
    ".csv",
    ".parquet",
    ".json",
    ".gz",
}

REPLAY_SCRIPTS = [
    "bin/replay_run.py",
    "bin/replay.py",
    "bin/proof_replay_batch16_freeze.py",
    "bin/proof_replay_csv_materialization.py",
    "bin/proof_replay_contracts.py",
    "bin/proof_replay_isolation.py",
]

REPLAY_PROOFS = [
    "run/proofs/replay_batch16_freeze.json",
    "run/proofs/recorded_live_replay_readiness_latest.json",
    "run/proofs/replay_csv_materialization_latest.json",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(errors="replace"))
    except Exception as exc:
        return {"parse_error": repr(exc)}


def main() -> int:
    data_files = []
    for root_rel in DATA_ROOTS:
        root = ROOT / root_rel
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in DATA_SUFFIXES:
                continue
            # avoid counting proof JSONs as historical data
            rel = p.relative_to(ROOT)
            if str(rel).startswith("run/proofs/"):
                continue
            try:
                size = p.stat().st_size
            except OSError:
                size = 0
            if size <= 0:
                continue
            data_files.append({
                "path": str(rel),
                "bytes": size,
                "suffix": p.suffix.lower(),
            })

    data_files = sorted(data_files, key=lambda x: x["bytes"], reverse=True)[:200]

    scripts = []
    for rel in REPLAY_SCRIPTS:
        p = ROOT / rel
        scripts.append({"path": rel, "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else 0})

    proofs = []
    for rel in REPLAY_PROOFS:
        p = ROOT / rel
        item = {"path": rel, "exists": p.exists(), "bytes": p.stat().st_size if p.exists() else 0}
        if p.exists():
            data = load_json(p)
            if isinstance(data, dict):
                item["status"] = data.get("status") or data.get("overall_status") or data.get("result")
                item["top_level_keys"] = sorted(list(data.keys()))[:50]
        proofs.append(item)

    replay_runner_present = any(s["exists"] and s["path"] in {"bin/replay_run.py", "bin/replay.py"} for s in scripts)
    any_data = len(data_files) > 0
    any_replay_proof = any(p["exists"] for p in proofs)

    findings = []
    if not any_data:
        findings.append({
            "severity": "P1",
            "owner": "replay/data",
            "finding": "No local historical data files found in scanned after-market data roots.",
        })
    if not replay_runner_present:
        findings.append({
            "severity": "P1",
            "owner": "replay",
            "finding": "No replay runner detected at bin/replay_run.py or bin/replay.py.",
        })
    if not any_replay_proof:
        findings.append({
            "severity": "P2",
            "owner": "replay/proofs",
            "finding": "No existing replay proof artifact found from expected list.",
        })

    status = "PASS" if any_data and replay_runner_present else "WARN"

    result = {
        "proof": "proof_aftermarket_historical_replay_readiness",
        "generated_at": now_iso(),
        "status": status,
        "historical_data_files_found": len(data_files),
        "top_historical_data_files": data_files[:50],
        "replay_scripts": scripts,
        "existing_replay_proofs": proofs,
        "findings": findings,
        "notes": [
            "Read-only proof.",
            "Does not use live Redis.",
            "Does not call brokers.",
            "Does not prove full semantic replay success.",
            "Use this output to choose the input file for the next full replay dry-run proof.",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps({
        "status": status,
        "historical_data_files_found": len(data_files),
        "replay_runner_present": replay_runner_present,
        "findings": findings,
        "out": str(OUT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
