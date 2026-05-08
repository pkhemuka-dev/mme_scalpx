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

from app.mme_scalpx.replay.contracts import replay_scenario_profile_engine_contract_summary  # noqa: E402
from app.mme_scalpx.replay.scenarios import (  # noqa: E402
    REPLAY_REQUIRED_SCENARIOS,
    list_replay_scenario_profiles,
    replay_scenario_engine_contract_summary,
    replay_scenario_manifest,
    validate_replay_scenario_profile,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_scenario_profiles.json")
    args = parser.parse_args()

    contract_file = ROOT / "etc/replay/schemas/replay_scenario_profile_contract_v1.json"
    manifest_file = ROOT / "etc/replay/scenarios/replay_scenario_profile_manifest_v1.json"

    contract = json.loads(contract_file.read_text(encoding="utf-8")) if contract_file.exists() else {}
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}

    profiles = list_replay_scenario_profiles()
    validations = {
        profile["scenario_id"]: validate_replay_scenario_profile(profile)
        for profile in profiles
    }

    required_set = set(REPLAY_REQUIRED_SCENARIOS)
    profile_set = {profile["scenario_id"] for profile in profiles}
    contract_set = set(contract.get("required_scenarios", ()))
    manifest_set = set(manifest.get("required_scenarios", ()))

    required_scenarios_ok = required_set == profile_set == contract_set == manifest_set
    validations_ok = all(v.get("ok") is True for v in validations.values())

    no_live_ok = (
        contract.get("paper_armed_approved") is False
        and contract.get("live_trading_approved") is False
        and contract.get("execution_arming_created") is False
        and contract.get("broker_calls_allowed") is False
        and contract.get("live_redis_writes_allowed") is False
        and contract.get("production_doctrine_changed") is False
        and manifest.get("paper_armed_approved") is False
        and manifest.get("live_trading_approved") is False
        and manifest.get("execution_arming_created") is False
        and manifest.get("broker_calls_allowed") is False
        and manifest.get("live_redis_writes_allowed") is False
        and manifest.get("production_doctrine_changed") is False
    )

    scenario_families = {profile["family"] for profile in profiles}
    expected_families = {
        "feed_availability",
        "feed_freshness",
        "provider_context",
        "oi_context",
        "liquidity",
        "execution_assumption",
        "event_integrity",
        "risk",
        "session_control",
    }
    families_ok = expected_families.issubset(scenario_families)

    manifest_generated = replay_scenario_manifest()
    manifest_runtime_ok = manifest_generated.get("scenario_count") == len(REPLAY_REQUIRED_SCENARIOS)

    contracts_summary = replay_scenario_profile_engine_contract_summary()
    engine_summary = replay_scenario_engine_contract_summary()

    profiles_ok = bool(
        contract_file.exists()
        and manifest_file.exists()
        and required_scenarios_ok
        and validations_ok
        and no_live_ok
        and families_ok
        and manifest_runtime_ok
        and contracts_summary.get("paper_armed_approved") is False
        and engine_summary.get("paper_armed_approved") is False
    )

    proof = {
        "schema_version": "proof_replay_scenario_profiles_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_profiles_ok": profiles_ok,
        "contract_file_exists": contract_file.exists(),
        "manifest_file_exists": manifest_file.exists(),
        "required_scenarios_ok": required_scenarios_ok,
        "validations_ok": validations_ok,
        "no_live_ok": no_live_ok,
        "families_ok": families_ok,
        "manifest_runtime_ok": manifest_runtime_ok,
        "scenario_count": len(profiles),
        "required_scenarios": tuple(REPLAY_REQUIRED_SCENARIOS),
        "scenario_families": sorted(scenario_families),
        "validations": validations,
        "contracts_summary": contracts_summary,
        "engine_summary": engine_summary,
        "scenario_profile_shape": "PROVEN_BY_27J",
        "scenario_application_shape": "NOT_PROVEN_BY_THIS_PROOF",
        "full_replay_scenario_outcome_parity": "NOT_PROVEN_IN_27J",
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
        "scenario_profiles_ok": profiles_ok,
        "scenario_count": proof["scenario_count"],
        "required_scenarios_ok": required_scenarios_ok,
        "validations_ok": validations_ok,
        "no_live_ok": no_live_ok,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if profiles_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
