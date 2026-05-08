#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.mme_scalpx.replay.experiment_workstation import (  # noqa: E402
    REPLAY_EXPERIMENT_TYPES,
    list_replay_experiment_profiles,
    replay_experiment_profile_manifest,
    replay_experiment_workstation_contract_summary,
    validate_replay_experiment_profile,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_experiment_profiles.json")
    args = parser.parse_args()

    contract_file = ROOT / "etc/replay/schemas/replay_experiment_workstation_contract_v1.json"
    manifest_file = ROOT / "etc/replay/experiments/replay_experiment_profile_manifest_v1.json"

    contract = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}

    profiles = list_replay_experiment_profiles()
    validations = {
        profile["profile_id"]: validate_replay_experiment_profile(profile)
        for profile in profiles
    }

    profile_types = {profile["experiment_type"] for profile in profiles}
    required_types_ok = profile_types == set(REPLAY_EXPERIMENT_TYPES) == set(contract.get("supported_experiment_types", ()))
    validations_ok = all(v.get("ok") is True for v in validations.values())
    manifest_ok = (
        manifest_file.exists()
        and manifest.get("profile_count") == len(REPLAY_EXPERIMENT_TYPES)
        and set(manifest.get("experiment_types", ())) == set(REPLAY_EXPERIMENT_TYPES)
    )
    no_live_ok = (
        contract.get("paper_armed_approved") is False
        and contract.get("live_trading_approved") is False
        and contract.get("execution_arming_created") is False
        and contract.get("broker_calls_allowed") is False
        and contract.get("live_redis_writes_allowed") is False
        and contract.get("production_doctrine_changed") is False
        and manifest.get("paper_armed_approved") is False
        and manifest.get("live_trading_approved") is False
        and manifest.get("production_doctrine_changed") is False
    )
    summary = replay_experiment_workstation_contract_summary()
    runtime_manifest = replay_experiment_profile_manifest()

    profiles_ok = bool(
        contract_file.exists()
        and manifest_file.exists()
        and required_types_ok
        and validations_ok
        and manifest_ok
        and no_live_ok
        and summary.get("paper_armed_approved") is False
        and runtime_manifest.get("profile_count") == len(REPLAY_EXPERIMENT_TYPES)
    )

    proof = {
        "schema_version": "proof_replay_experiment_profiles_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_profiles_ok": profiles_ok,
        "contract_file_exists": contract_file.exists(),
        "manifest_file_exists": manifest_file.exists(),
        "required_types_ok": required_types_ok,
        "validations_ok": validations_ok,
        "manifest_ok": manifest_ok,
        "no_live_ok": no_live_ok,
        "profile_count": len(profiles),
        "experiment_types": tuple(REPLAY_EXPERIMENT_TYPES),
        "validations": validations,
        "contract_summary": summary,
        "runtime_manifest": runtime_manifest,
        "experiment_profile_shape": "PROVEN_BY_27M",
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "full_live_replay_parity": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "verdict": "PASS" if profiles_ok else "FAIL",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str), encoding="utf-8")

    print(json.dumps({
        "proof": str(out),
        "verdict": proof["verdict"],
        "experiment_profiles_ok": profiles_ok,
        "profile_count": proof["profile_count"],
        "required_types_ok": required_types_ok,
        "validations_ok": validations_ok,
        "manifest_ok": manifest_ok,
        "no_live_ok": no_live_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if profiles_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
