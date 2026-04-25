#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return ""


def _git_dirty() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--short"],
            cwd=PROJECT_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return bool(out.strip())
    except Exception:
        return True


def standard_result(
    *,
    proof_name: str,
    status: str,
    scope: str,
    checks: list[dict[str, Any]],
    does_not_prove: list[str] | None = None,
    artifacts: list[str] | None = None,
    writes_live_redis: bool = False,
    writes_replay_redis: bool = False,
    uses_broker: bool = False,
    places_orders: bool = False,
    requires_fresh_market: bool = False,
    proof_version: str = "1",
) -> dict[str, Any]:
    failed = [c for c in checks if c.get("status") not in {"PASS", "SKIP"}]
    if status == "AUTO":
        status = "PASS" if not failed else "FAIL"

    return {
        "proof_name": proof_name,
        "proof_version": proof_version,
        "project_root": str(PROJECT_ROOT),
        "git_commit": _git_commit(),
        "tree_dirty": _git_dirty(),
        "timestamp_ns": time.time_ns(),
        "scope": scope,
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "does_not_prove": does_not_prove or [],
        "artifacts": artifacts or [],
        "requires_fresh_market": requires_fresh_market,
        "writes_live_redis": writes_live_redis,
        "writes_replay_redis": writes_replay_redis,
        "uses_broker": uses_broker,
        "places_orders": places_orders,
    }


def write_result(result: dict[str, Any], *, proof_name: str | None = None) -> Path:
    name = proof_name or str(result["proof_name"])
    proof_dir = PROJECT_ROOT / "run/proofs"
    latest_dir = proof_dir / "latest"
    proof_dir.mkdir(parents=True, exist_ok=True)
    latest_dir.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d_%H%M%S")
    stamped = proof_dir / f"{name}_{stamp}.json"
    latest = latest_dir / f"{name}.json"
    legacy_latest = proof_dir / f"{name}.json"

    payload = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    stamped.write_text(payload)
    latest.write_text(payload)
    legacy_latest.write_text(payload)
    return legacy_latest


def env_guard_enabled(name: str) -> bool:
    return os.environ.get(name, "").strip() in {"1", "true", "TRUE", "yes", "YES", "on", "ON"}
