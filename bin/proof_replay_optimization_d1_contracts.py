#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import importlib
import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd().resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
NOW = datetime.now(timezone.utc).isoformat()
PROOF_DIR = ROOT / "run" / "proofs"
MILESTONE_DIR = ROOT / "docs" / "milestones"
PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "etc/replay_optimization/optimization_policy.json",
    "etc/replay_optimization/sweep_space_contract.json",
    "etc/replay_optimization/ml_export_contract.json",
    "bin/proof_replay_optimization_d1_contracts.py",
]

FORBIDDEN_RUNTIME_TOKENS = [
    "from kiteconnect",
    "KiteConnect(",
    "DhanHQ(",
    "place_order(",
    ".place_order(",
    "redis.Redis(",
    ".xadd(",
    "subprocess.Popen(",
    "app.mme_scalpx.main",
]

ALLOWED_CONTRACT_IMPORT_ROOTS = {"__future__", "dataclasses", "pathlib", "typing"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def imported_roots(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.append(node.module.split(".")[0])
    return sorted(set(roots))


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected Lane D D1 files: {missing}")

compile_targets = [
    files["app/mme_scalpx/replay_optimization/__init__.py"],
    files["app/mme_scalpx/replay_optimization/contracts.py"],
    files["bin/proof_replay_optimization_d1_contracts.py"],
]
compile_results = {}
for path in compile_targets:
    py_compile.compile(str(path), doraise=True)
    compile_results[path.as_posix()] = "PASS"

contracts_path = files["app/mme_scalpx/replay_optimization/contracts.py"]
contract_import_roots = imported_roots(contracts_path)
for root in contract_import_roots:
    if root not in ALLOWED_CONTRACT_IMPORT_ROOTS:
        raise SystemExit(f"unexpected import in Lane D contracts.py: {root}")

contracts_text = contracts_path.read_text(encoding="utf-8")
forbidden_hits = [tok for tok in FORBIDDEN_RUNTIME_TOKENS if tok in contracts_text]
if forbidden_hits:
    raise SystemExit(f"forbidden runtime tokens in Lane D contracts.py: {forbidden_hits}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.contracts")
summary = mod.contract_summary()
policy = load_json(files["etc/replay_optimization/optimization_policy.json"])
sweep = load_json(files["etc/replay_optimization/sweep_space_contract.json"])
ml_export = load_json(files["etc/replay_optimization/ml_export_contract.json"])

assert summary["lane"] == "LANE_D_REPLAY_OPTIMIZATION"
assert summary["accepted_for"] == "CONTRACT_ONLY"
assert summary["replay_execution_performed"] is False
assert summary["ml_training_performed"] is False
assert summary["broker_calls_allowed"] is False
assert summary["live_redis_writes_allowed"] is False
assert summary["paper_live_approved"] is False
assert summary["production_claim_allowed"] is False

safety = mod.LaneDSafetyPolicy()
mod.validate_safety_policy(safety)
manifest = mod.OptimizationManifest(
    optimization_id="D1_CONTRACT_PROBE",
    created_at=NOW,
    replay_input_root="run/replay/example",
    raw_input_root="run/research_gate/example",
)
mod.validate_manifest(manifest)
row = mod.SweepCandidateRow(
    optimization_id="D1_CONTRACT_PROBE",
    candidate_id="D1_SAMPLE_MIST_CALL_NORMAL",
    strategy_family="MIST",
    side="CALL",
    regime="NORMAL",
    parameter_group="entry_filters",
    parameter_name="volume_thresholds",
    baseline_value="contract_only",
    candidate_value="contract_only",
)
mod.validate_sweep_candidate(row)

required_surfaces = [
    "optimization_run",
    "sweep_candidate",
    "replay_result_ref",
    "raw_feature_ref",
    "leaderboard",
    "ml_dataset",
    "optimizer_verdict",
]
column_counts = {name: len(mod.columns_for(name)) for name in required_surfaces}

for config_name, payload in {
    "optimization_policy": policy,
    "sweep_space_contract": sweep,
    "ml_export_contract": ml_export,
}.items():
    if payload.get("contract_version") != "replay_optimization_d1_contract_v1":
        raise SystemExit(f"{config_name} contract_version mismatch")
    if payload.get("accepted_for") != "CONTRACT_ONLY":
        raise SystemExit(f"{config_name} accepted_for mismatch")

if policy["governance"]["may_call_broker"] is not False:
    raise SystemExit("optimization policy broker safety failed")
if policy["governance"]["may_write_live_redis"] is not False:
    raise SystemExit("optimization policy Redis safety failed")
if policy["governance"]["may_enable_paper_or_live"] is not False:
    raise SystemExit("optimization policy paper/live safety failed")
if ml_export["forbidden_ml_routes"]["live_order_decisioning"] is not True:
    raise SystemExit("ML export live-order forbidden route missing")

file_hashes = {rel: sha256(path) for rel, path in files.items()}
proof = {
    "batch": "LANE-D-D1",
    "name": "replay_optimization_constitution_contract_freeze",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CONTRACT_ONLY",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "contract_import_roots": contract_import_roots,
    "column_counts": column_counts,
    "contract_summary": summary,
    "safety": {
        "replay_execution_performed": False,
        "ml_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
        "runtime_services_started": False,
        "strategy_doctrine_changed": False,
        "replay_engine_changed": False,
        "production_profit_claim_allowed": False
    },
    "next_recommended_batch": "LANE-D-D2_SWEEP_SPACE_SCHEMA_AND_PROFILE_GENERATOR_CONTRACT"
}

proof_path = PROOF_DIR / f"proof_lane_d_d1_replay_optimization_contracts_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d1_replay_optimization_contracts_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d1_replay_optimization_contracts_{TS}.md"
milestone_path.write_text(
    "# LANE D D1 — Replay Optimization Constitution + Contract Surface Freeze\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — contract-only additive Lane D package created.\n\n"
    "## Scope\n\n"
    "- Added `app/mme_scalpx/replay_optimization/` package.\n"
    "- Added offline optimization policy and schema contracts under `etc/replay_optimization/`.\n"
    "- Added proof script `bin/proof_replay_optimization_d1_contracts.py`.\n"
    "- No replay execution, no ML training, no broker calls, no live Redis writes, no paper/live enablement.\n\n"
    "## Next\n\n"
    "LANE-D-D2: sweep-space schema and profile-generator contract.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
