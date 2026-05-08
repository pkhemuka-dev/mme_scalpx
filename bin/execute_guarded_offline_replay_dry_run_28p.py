#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

REQUIRED_FLAGS = [
    "--offline",
    "--dataset-candidate",
    "--output-root",
    "--no-broker",
    "--no-live-redis",
    "--observe-only",
    "--dry-run",
]

NO_ENABLEMENT_FIELDS = [
    "starts_services",
    "reads_live_redis",
    "writes_live_redis",
    "calls_broker_api",
    "broker_call_reachable",
    "live_redis_write_reachable",
    "runtime_promotion_reachable",
    "paper_armed_approved",
    "live_trading_approved",
    "execution_arming_created",
    "real_order_sent",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "production_doctrine_changed",
]

def sha256_file(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": type(exc).__name__, "_read_error_text": str(exc), "_path": str(path)}

def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def rel(root: pathlib.Path, path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except Exception:
        return str(path)

def file_state(root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    return {
        "path": rel(root, path),
        "present": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256_file(path),
    }

def dir_inventory(root: pathlib.Path, path: pathlib.Path) -> dict[str, Any]:
    files = []
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file():
                files.append(file_state(root, child))
    return {
        "path": rel(root, path),
        "present": path.exists(),
        "is_dir": path.is_dir(),
        "file_count": len(files),
        "files": files[:500],
    }

def safe_under_run_replay(project_root: pathlib.Path, path: pathlib.Path) -> bool:
    replay_root = (project_root / "run" / "replay").resolve()
    target = path.resolve()
    return str(target).startswith(str(replay_root) + "/")

def command_arg_value(command: list[str], flag: str) -> str | None:
    if flag not in command:
        return None
    idx = command.index(flag)
    if idx + 1 >= len(command):
        return None
    return command[idx + 1]

def no_enablement_clean(payloads: dict[str, dict[str, Any]]) -> tuple[bool, dict[str, Any]]:
    observed: dict[str, Any] = {}
    clean = True
    for name, payload in payloads.items():
        observed[name] = {}
        for field in NO_ENABLEMENT_FIELDS:
            if field in payload:
                observed[name][field] = payload.get(field)
            if payload.get(field) is True:
                clean = False
    return clean, observed

def normalize_command(project_root: pathlib.Path, command: list[str]) -> list[str]:
    if not command:
        return []
    out = list(command)
    if out[0] in ("python", "python3"):
        out[0] = sys.executable
    if len(out) > 1 and out[1] == "bin/replay_run.py":
        out[1] = str(project_root / "bin" / "replay_run.py")
    return out

def run_command(project_root: pathlib.Path, command: list[str], timeout_sec: int) -> dict[str, Any]:
    env = os.environ.copy()
    env.update({
        "MME_SCALPX_REPLAY_OFFLINE_ONLY": "1",
        "MME_SCALPX_NO_BROKER": "1",
        "MME_SCALPX_NO_LIVE_REDIS": "1",
        "MME_SCALPX_RUNTIME_MODE": "observe_only",
        "SCALPX_REPLAY_DRY_RUN": "1",
    })
    try:
        proc = subprocess.run(
            command,
            cwd=str(project_root),
            text=True,
            capture_output=True,
            timeout=timeout_sec,
            env=env,
        )
        return {
            "args": command,
            "returncode": proc.returncode,
            "ok": proc.returncode == 0,
            "timeout": False,
            "stdout": proc.stdout[-60000:],
            "stderr": proc.stderr[-60000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "args": command,
            "returncode": None,
            "ok": False,
            "timeout": True,
            "stdout": (exc.stdout or "")[-60000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-60000:] if isinstance(exc.stderr, str) else "",
        }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--contract-root", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--proof-28o", required=True)
    parser.add_argument("--timeout-sec", type=int, default=120)
    args = parser.parse_args()

    project_root = pathlib.Path(args.project_root).resolve()
    contract_root = pathlib.Path(args.contract_root).resolve()
    output_root = pathlib.Path(args.output_root).resolve()
    proof_28o_path = pathlib.Path(args.proof_28o).resolve()

    if not safe_under_run_replay(project_root, contract_root):
        raise SystemExit(f"contract root must stay under run/replay: {contract_root}")
    if not safe_under_run_replay(project_root, output_root):
        raise SystemExit(f"output root must stay under run/replay: {output_root}")

    proof_28o = read_json(proof_28o_path)
    command_contract = read_json(contract_root / "00_dry_run_command_contract.json")
    input_contract = read_json(contract_root / "01_input_surface_contract.json")
    safety_boundary = read_json(contract_root / "02_no_broker_no_live_redis_boundary.json")
    readiness = read_json(contract_root / "04_readiness_report.json")

    proposed = command_contract.get("proposed_future_command_not_executed")
    if not isinstance(proposed, list):
        proposed = []

    command = normalize_command(project_root, [str(x) for x in proposed])

    dataset_candidate_raw = command_arg_value(command, "--dataset-candidate")
    output_root_raw = command_arg_value(command, "--output-root")

    dataset_candidate = pathlib.Path(dataset_candidate_raw).resolve() if dataset_candidate_raw else None
    command_output_root = pathlib.Path(output_root_raw).resolve() if output_root_raw else None

    missing_flags = [flag for flag in REQUIRED_FLAGS if flag not in command]
    command_path_ok = len(command) >= 2 and pathlib.Path(command[1]).resolve() == (project_root / "bin" / "replay_run.py").resolve()
    dataset_candidate_safe = bool(dataset_candidate and dataset_candidate.is_dir() and safe_under_run_replay(project_root, dataset_candidate))
    command_output_safe = bool(command_output_root and safe_under_run_replay(project_root, command_output_root))
    command_output_matches = bool(command_output_root and command_output_root == output_root)

    no_enablement_ok, observed = no_enablement_clean({
        "proof_28o": proof_28o,
        "command_contract": command_contract,
        "safety_boundary": safety_boundary,
        "readiness": readiness,
    })

    input_surfaces = input_contract.get("input_surfaces")
    missing_surfaces = input_contract.get("missing_surfaces")
    if not isinstance(input_surfaces, dict):
        input_surfaces = {}
    if not isinstance(missing_surfaces, list):
        missing_surfaces = []

    contract_valid = (
        proof_28o.get("guarded_offline_replay_dry_run_contract_28o_ok") is True
        and proof_28o.get("contract_ready") is True
        and proof_28o.get("future_command_prepared") is True
        and proof_28o.get("future_command_executed") is False
        and proof_28o.get("replay_run_completed") is False
        and command_contract.get("contract_ready") is True
        and command_path_ok
        and not missing_flags
        and dataset_candidate_safe
        and command_output_safe
        and command_output_matches
        and no_enablement_ok
        and not missing_surfaces
    )

    output_root.mkdir(parents=True, exist_ok=True)

    validation = {
        "schema_version": "guarded_offline_replay_dry_run_command_validation_28p_v1",
        "contract_valid": bool(contract_valid),
        "command": command,
        "missing_flags": missing_flags,
        "command_path_ok": bool(command_path_ok),
        "dataset_candidate": str(dataset_candidate) if dataset_candidate else None,
        "dataset_candidate_safe": bool(dataset_candidate_safe),
        "command_output_root": str(command_output_root) if command_output_root else None,
        "command_output_safe": bool(command_output_safe),
        "command_output_matches": bool(command_output_matches),
        "no_enablement_ok": bool(no_enablement_ok),
        "observed_no_enablement_fields": observed,
        "missing_surfaces": missing_surfaces,
    }
    write_json(output_root / "01_command_validation.json", validation)

    process_result = {
        "skipped": True,
        "reason": "contract_not_valid",
        "ok": False,
    }

    if contract_valid:
        process_result = run_command(project_root, command, args.timeout_sec)

    output_inventory = dir_inventory(project_root, output_root)

    no_boundary = {
        "schema_version": "guarded_offline_replay_dry_run_no_boundary_28p_v1",
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "broker_call_reachable": False,
        "live_redis_write_reachable": False,
        "runtime_promotion_reachable": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28P",
    }

    execution_ok = bool(
        contract_valid
        and process_result.get("ok") is True
        and process_result.get("timeout") is False
    )

    manifest = {
        "schema_version": "guarded_offline_replay_dry_run_execution_manifest_28p_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "GUARDED_OFFLINE_REPLAY_DRY_RUN_EXECUTION_ONLY",
        "contract_valid": bool(contract_valid),
        "execution_ok": bool(execution_ok),
        "future_command_executed": bool(contract_valid),
        "replay_run_completed": bool(execution_ok),
        "comparison_completed": False,
        "output_root": str(output_root),
        "command": command,
        "process_returncode": process_result.get("returncode"),
        "process_timeout": process_result.get("timeout"),
        "dataset_materialized_for_replay_run": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28P",
        **no_boundary,
        "next_batch": "Batch 28Q — inspect guarded offline replay dry-run outputs and build replay/live comparison preflight, still not paper/live enablement.",
    }

    next_contract = {
        "schema_version": "guarded_offline_replay_dry_run_next_comparison_contract_28p_v1",
        "execution_ok": bool(execution_ok),
        "next_batch": manifest["next_batch"] if execution_ok else "Repair guarded replay dry-run command/interface before comparison.",
        "allowed_next_actions": [
            "inspect dry-run output root",
            "build replay/live comparison preflight",
            "write no-broker/no-live-redis proof",
        ],
        "forbidden_next_actions_without_new_gate": [
            "approve paper_armed",
            "approve live trading",
            "call broker APIs",
            "write live Redis",
            "claim full replay/live parity",
        ],
    }

    write_json(output_root / "00_execution_manifest.json", manifest)
    write_json(output_root / "02_process_result.json", process_result)
    write_json(output_root / "03_output_root_inventory.json", output_inventory)
    write_json(output_root / "04_no_broker_no_live_redis_boundary.json", no_boundary)
    write_json(output_root / "05_next_comparison_contract.json", next_contract)

    result = {
        "schema_version": "guarded_offline_replay_dry_run_execution_result_28p_v1",
        "accepted_for": "GUARDED_OFFLINE_REPLAY_DRY_RUN_EXECUTION_ONLY",
        "contract_valid": bool(contract_valid),
        "execution_ok": bool(execution_ok),
        "future_command_executed": bool(contract_valid),
        "replay_run_completed": bool(execution_ok),
        "comparison_completed": False,
        "process_returncode": process_result.get("returncode"),
        "process_timeout": process_result.get("timeout"),
        "output_root": str(output_root),
        "written_count": 6,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "production_doctrine_changed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28P",
        "next_batch": next_contract["next_batch"],
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if execution_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
