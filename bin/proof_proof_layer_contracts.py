#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from bin.prooflib import standard_result, write_result  # noqa: E402

PROOF_NAME = "proof_layer_contracts"


def exists_nonempty(path: str) -> dict[str, Any]:
    p = PROJECT_ROOT / path
    return {
        "case": f"exists_nonempty:{path}",
        "status": "PASS" if p.exists() and p.stat().st_size > 0 else "FAIL",
        "path": path,
    }


def text_contains(path: str, needle: str, case: str) -> dict[str, Any]:
    p = PROJECT_ROOT / path
    text = p.read_text() if p.exists() else ""
    return {
        "case": case,
        "status": "PASS" if needle in text else "FAIL",
        "path": path,
        "needle": needle,
    }


def no_active_noise() -> dict[str, Any]:
    violations = []
    for root_name in ("bin",):
        root = PROJECT_ROOT / root_name
        if not root.exists():
            continue
        for p in root.rglob("*"):
            n = p.name
            if n == "__pycache__" or n.endswith(".pyc") or ".bak" in n:
                violations.append(str(p.relative_to(PROJECT_ROOT)))
    return {
        "case": "no_active_bin_bak_pyc_pycache",
        "status": "PASS" if not violations else "FAIL",
        "violations": violations[:200],
        "violation_count": len(violations),
    }


def main() -> int:
    checks: list[dict[str, Any]] = []

    checks.extend([
        exists_nonempty("etc/proof_registry.yaml"),
        exists_nonempty("bin/prooflib.py"),
        exists_nonempty("bin/proof_strategy_activation_report_redis_smoke.py"),
        exists_nonempty("bin/observe_strategy_activation_report_live.py"),
        exists_nonempty("bin/build_proof_bundle.py"),
    ])

    registry_required = [
        "proof_strategy_activation_report_redis_smoke.py",
        "observe_strategy_activation_report_live.py",
        "proof_execution_family_entry_safety.py",
        "proof_runtime_instrument_provider_equivalence.py",
        "MISSING_REQUIRED_BEFORE_PAPER_ARMED",
        "live_write_env_guard",
    ]
    for needle in registry_required:
        checks.append(text_contains("etc/proof_registry.yaml", needle, f"registry_contains:{needle}"))

    smoke_required = [
        "--publish-hold-live",
        "--publish-hold-replay",
        "I_UNDERSTAND_THIS_WRITES_LIVE_DECISION_STREAM",
        "writes_live_redis",
        "writes_replay_redis",
        "proof_scope",
        "paper_armed_ready",
    ]
    for needle in smoke_required:
        checks.append(text_contains("bin/proof_strategy_activation_report_redis_smoke.py", needle, f"smoke_contains:{needle}"))

    # Old ambiguous flag must not remain.
    smoke = PROJECT_ROOT / "bin/proof_strategy_activation_report_redis_smoke.py"
    smoke_text = smoke.read_text() if smoke.exists() else ""
    checks.append({
        "case": "smoke_old_publish_hold_flag_removed",
        "status": "PASS" if '"--publish-hold"' not in smoke_text else "FAIL",
    })

    observer_required = [
        '"proof_scope": "HOLD_REPORT_ONLY_LIVE_OBSERVATION"',
        '"activation_ready": False',
        '"paper_armed_ready": False',
        '"does_not_prove":',
        '"writes_live_redis": False',
    ]
    for needle in observer_required:
        checks.append(text_contains("bin/observe_strategy_activation_report_live.py", needle, f"observer_contains:{needle}"))

    checks.append(no_active_noise())

    result = standard_result(
        proof_name=PROOF_NAME,
        status="AUTO",
        scope="proof_tooling_governance",
        checks=checks,
        does_not_prove=[
            "execution_family_entry_safety",
            "risk_exit_never_blocked",
            "provider_token_equivalence",
            "paper_armed_readiness",
            "live_trading_readiness",
        ],
        writes_live_redis=False,
        uses_broker=False,
        places_orders=False,
    )
    out = write_result(result, proof_name=PROOF_NAME)
    print(json.dumps(result, indent=2, sort_keys=True))
    print("dumped =", out.relative_to(PROJECT_ROOT))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
