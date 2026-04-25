#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF_ROOT = ROOT / "run" / "proofs"

def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except Exception:
        return str(p)

def read_text(p: Path, limit: int = 12000) -> str:
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8", errors="replace")
    if len(text) > limit:
        return text[:limit] + "\n\n...[TRUNCATED]...\n"
    return text

def latest_bundle() -> Path:
    bundles = sorted(PROOF_ROOT.glob("final_freeze_bundle_*"), key=lambda p: p.stat().st_mtime_ns)
    if not bundles:
        raise SystemExit("No final_freeze_bundle_* found under run/proofs")
    return bundles[-1]

def sh(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, cwd=ROOT, shell=True, text=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        return exc.output

def main() -> int:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle = latest_bundle()
    index_path = bundle / "final_freeze_bundle_index.json"

    if not index_path.exists():
        raise SystemExit(f"Missing index: {index_path}")

    data = json.loads(index_path.read_text(encoding="utf-8"))

    triage_dir = PROOF_ROOT / f"final_freeze_gap_triage_{ts}"
    triage_dir.mkdir(parents=True, exist_ok=True)

    results = data.get("results", [])
    bad = [r for r in results if r.get("status") != "PASS"]
    missing = [r for r in results if r.get("status") == "MISSING"]
    failed = [r for r in results if r.get("status") == "FAIL"]
    timeout = [r for r in results if r.get("status") == "TIMEOUT"]
    errored = [r for r in results if r.get("status") == "ERROR"]

    fail_logs: dict[str, Any] = {}
    for r in failed + timeout + errored:
        name = r.get("name") or r.get("path") or "unknown"
        stdout_log = ROOT / str(r.get("stdout_log", ""))
        stderr_log = ROOT / str(r.get("stderr_log", ""))
        fail_logs[name] = {
            "stdout_log": r.get("stdout_log"),
            "stderr_log": r.get("stderr_log"),
            "stdout_excerpt": read_text(stdout_log),
            "stderr_excerpt": read_text(stderr_log),
        }

    hygiene_path = bundle / "hygiene_scan.json"
    hygiene = json.loads(hygiene_path.read_text(encoding="utf-8")) if hygiene_path.exists() else {}

    proof_scripts = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "bin").glob("proof_*.py"))

    registry_path = ROOT / "etc" / "proof_registry.yaml"
    registry_text = read_text(registry_path, limit=30000) if registry_path.exists() else ""

    triage = {
        "triage_name": "final_freeze_gap_triage",
        "timestamp_ns": time.time_ns(),
        "source_bundle": rel(bundle),
        "source_index": rel(index_path),
        "source_status": data.get("status"),
        "source_verdict": data.get("freeze_verdict"),
        "counts": data.get("counts"),
        "hygiene_status": hygiene.get("status"),
        "missing_count": len(missing),
        "failed_count": len(failed),
        "timeout_count": len(timeout),
        "error_count": len(errored),
        "missing_proofs": [
            {
                "name": r.get("name"),
                "path": r.get("path"),
                "status": r.get("status"),
            }
            for r in missing
        ],
        "failed_proofs": [
            {
                "name": r.get("name"),
                "path": r.get("path"),
                "stdout_log": r.get("stdout_log"),
                "stderr_log": r.get("stderr_log"),
            }
            for r in failed
        ],
        "fail_logs": fail_logs,
        "hygiene": hygiene,
        "existing_proof_scripts": proof_scripts,
        "proof_registry_exists": registry_path.exists(),
        "proof_registry_excerpt": registry_text,
        "git_status_short": sh("git status --short"),
        "recommendation": [
            "Do not run live observation while market is closed.",
            "Do not delete missing proofs from the final runner merely to get PASS.",
            "First fix proof_proof_layer_contracts.py failure.",
            "Then implement or formally quarantine every missing proof.",
            "Then rerun bin/run_final_freeze_bundle.py.",
        ],
    }

    out_json = triage_dir / "final_freeze_gap_triage.json"
    out_json.write_text(json.dumps(triage, indent=2), encoding="utf-8")

    md = ROOT / "docs" / "milestones" / f"{datetime.now().date()}_final_freeze_gap_triage_{ts}.md"
    md.write_text(
        "\n".join([
            f"# Final Freeze Gap Triage — {datetime.now().date()}",
            "",
            f"- Source bundle: `{rel(bundle)}`",
            f"- Source status: `{data.get('status')}`",
            f"- Source verdict: `{data.get('freeze_verdict')}`",
            f"- Counts: `{data.get('counts')}`",
            f"- Hygiene: `{hygiene.get('status')}`",
            f"- Missing proofs: `{len(missing)}`",
            f"- Failed proofs: `{len(failed)}`",
            "",
            "## Failed proofs",
            "",
            *[
                f"- `{r.get('name')}` stdout=`{r.get('stdout_log')}` stderr=`{r.get('stderr_log')}`"
                for r in failed
            ],
            "",
            "## Missing proofs",
            "",
            *[
                f"- `{r.get('path')}`"
                for r in missing
            ],
            "",
            "## Next action",
            "",
            "Market is closed, so live report-only observation is deferred.",
            "Fix proof-governance failure and missing proof coverage first.",
            "Do not move to paper_armed until final bundle is PASS and live observation later passes during market hours.",
            "",
        ]),
        encoding="utf-8",
    )

    print("===== FINAL FREEZE GAP TRIAGE =====")
    print("source_bundle:", rel(bundle))
    print("source_status:", data.get("status"))
    print("counts:", data.get("counts"))
    print("hygiene:", hygiene.get("status"))
    print("missing_count:", len(missing))
    print("failed_count:", len(failed))
    print("triage_json:", rel(out_json))
    print("milestone:", rel(md))

    print()
    print("===== FAILED PROOFS =====")
    for r in failed:
        print("-", r.get("name"), r.get("stdout_log"), r.get("stderr_log"))

    print()
    print("===== MISSING PROOFS =====")
    for r in missing:
        print("-", r.get("path"))

    print()
    print("===== HYGIENE WARN DETAILS =====")
    for k, v in hygiene.items():
        print(k, "=", v)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
