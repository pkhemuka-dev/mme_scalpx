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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d2_contract_probe_{TS}"
PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "etc/replay_optimization/optimization_policy.json",
    "etc/replay_optimization/sweep_space_contract.json",
    "etc/replay_optimization/ml_export_contract.json",
    "etc/replay_optimization/sweep_spaces/base_research_sweep_space.json",
    "etc/replay_optimization/optimizer_profiles/offline_contract_profile.json",
    "bin/proof_replay_optimization_d2_sweep_space.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "bin/proof_replay_optimization_d2_sweep_space.py",
]

FORBIDDEN_TOKENS = [
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

BANNED_IMPORT_ROOTS = {
    "kiteconnect",
    "redis",
    "requests",
    "websocket",
    "pandas",
    "numpy",
    "sklearn",
    "xgboost",
    "lightgbm",
}

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "ast",
    "dataclasses",
    "datetime",
    "hashlib",
    "importlib",
    "json",
    "pathlib",
    "py_compile",
    "shutil",
    "typing",
}


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
            if node.level and node.module:
                roots.append(node.module.split(".")[0])
            elif node.module:
                roots.append(node.module.split(".")[0])
    return sorted(set(roots))


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D2 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in [
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts", "sweep_space"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

TEXT_AUDIT_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "etc/replay_optimization/optimization_policy.json",
    "etc/replay_optimization/sweep_space_contract.json",
    "etc/replay_optimization/ml_export_contract.json",
    "etc/replay_optimization/sweep_spaces/base_research_sweep_space.json",
    "etc/replay_optimization/optimizer_profiles/offline_contract_profile.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

contracts = importlib.import_module("app.mme_scalpx.replay_optimization.contracts")
sweep_mod = importlib.import_module("app.mme_scalpx.replay_optimization.sweep_space")
profile_mod = importlib.import_module("app.mme_scalpx.replay_optimization.profile_generator")

policy = load_json(files["etc/replay_optimization/optimization_policy.json"])
sweep_config = load_json(files["etc/replay_optimization/sweep_spaces/base_research_sweep_space.json"])
profile_config = load_json(files["etc/replay_optimization/optimizer_profiles/offline_contract_profile.json"])

if policy["governance"]["may_call_broker"] is not False:
    raise SystemExit("D2 policy broker safety failed")
if policy["governance"]["may_write_live_redis"] is not False:
    raise SystemExit("D2 policy Redis safety failed")
if sweep_config["safety"]["replay_engine_mutation_allowed"] is not False:
    raise SystemExit("D2 sweep config replay-engine mutation safety failed")
if profile_config["profile_generation"]["execute_replay"] is not False:
    raise SystemExit("D2 profile config replay execution safety failed")
if profile_config["profile_generation"]["train_ml"] is not False:
    raise SystemExit("D2 profile config ML training safety failed")

space = sweep_mod.default_sweep_space()
sweep_mod.validate_sweep_space(space)

optimization_id = f"D2_CONTRACT_PROBE_{TS}"
candidates = sweep_mod.generate_sweep_candidates(optimization_id, space, max_candidates=10000)

if len(candidates) <= 0:
    raise SystemExit("D2 candidate generation returned zero rows")

expected_min = len(contracts.STRATEGY_FAMILIES) * len(contracts.SIDES) * len(contracts.REGIMES)
if len(candidates) < expected_min:
    raise SystemExit("D2 candidate count unexpectedly below strategy/side/regime minimum")

for row in candidates[:50]:
    contracts.validate_sweep_candidate(row)
    if row.status != "PROPOSED_ONLY":
        raise SystemExit("D2 candidate status must remain PROPOSED_ONLY")

artifact_result = profile_mod.build_d2_contract_artifacts(
    optimization_id,
    ARTIFACT_ROOT,
    space=space,
    max_candidates=10000,
    max_profiles=100,
)

for key in [
    "sweep_space_path",
    "candidate_matrix_path",
    "profile_catalog_path",
]:
    path = Path(artifact_result[key])
    if not path.exists():
        raise SystemExit(f"D2 artifact missing: {key}={path}")

if artifact_result["replay_execution_performed"] is not False:
    raise SystemExit("D2 artifact unexpectedly performed replay execution")
if artifact_result["ml_training_performed"] is not False:
    raise SystemExit("D2 artifact unexpectedly performed ML training")
if artifact_result["broker_calls_executed"] is not False:
    raise SystemExit("D2 artifact unexpectedly executed broker calls")
if artifact_result["live_redis_writes_executed"] is not False:
    raise SystemExit("D2 artifact unexpectedly wrote live Redis")
if artifact_result["paper_or_live_enabled"] is not False:
    raise SystemExit("D2 artifact unexpectedly enabled paper/live")

manifest = contracts.OptimizationManifest(
    optimization_id=optimization_id,
    created_at=NOW,
    mode="CONTRACT_ONLY_PROFILE_GENERATION",
    output_root=ARTIFACT_ROOT.relative_to(ROOT).as_posix(),
    optimizer_verdict=contracts.VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
)
contracts.validate_manifest(manifest)
profile_mod.write_json(ARTIFACT_ROOT / "00_optimization_manifest.json", contracts.row_to_dict(manifest))
profile_mod.write_json(
    ARTIFACT_ROOT / "09_optimizer_verdict.json",
    contracts.row_to_dict(
        contracts.OptimizerVerdictRow(
            optimization_id=optimization_id,
            created_at=NOW,
            verdict=contracts.VERDICT_NOT_READY_UNVERIFIED_REPLAY_SOURCE,
            sample_days=0,
            sample_trades=0,
            risk_notes="D2 is contract/profile-generation only. Replay source is not consumed.",
            production_claim_allowed=False,
            paper_live_approved=False,
            remarks="No optimization result, no replay execution, no ML training.",
        )
    ),
)

sample_profile = profile_mod.candidate_to_profile(candidates[0])
if sample_profile["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D2 sample profile broker safety failed")
if sample_profile["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D2 sample profile Redis safety failed")
if sample_profile["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D2 sample profile paper/live safety failed")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D2",
    "name": "sweep_space_schema_and_profile_generator_contract",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CONTRACT_ONLY_PROFILE_GENERATION",
    "d1_dependency_observed": True,
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "sweep_summary": sweep_mod.sweep_contract_summary(),
    "artifact_result": artifact_result,
    "candidate_count": len(candidates),
    "candidate_status": "PROPOSED_ONLY",
    "strategy_families": list(contracts.STRATEGY_FAMILIES),
    "sides": list(contracts.SIDES),
    "regimes": list(contracts.REGIMES),
    "sample_candidate": contracts.row_to_dict(candidates[0]),
    "sample_profile": sample_profile,
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
    "next_recommended_batch": "LANE-D-D3_READ_ONLY_REPLAY_RESULT_INDEXER_CONTRACT"
}

proof_path = PROOF_DIR / f"proof_lane_d_d2_sweep_space_profile_generator_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d2_sweep_space_profile_generator_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d2_sweep_space_profile_generator_{TS}.md"
milestone_path.write_text(
    "# LANE D D2 — Sweep Space Schema + Profile Generator Contract\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D2 contract-only sweep-space and profile-generator surfaces created.\n\n"
    "## Scope\n\n"
    "- Added `sweep_space.py`.\n"
    "- Added `profile_generator.py`.\n"
    "- Added base research sweep-space config.\n"
    "- Added offline contract profile config.\n"
    "- Generated contract probe artifacts under `run/replay_optimization/`.\n\n"
    "## Safety\n\n"
    "- No replay execution.\n"
    "- No ML training.\n"
    "- No broker calls.\n"
    "- No live Redis writes.\n"
    "- No paper/live enablement.\n"
    "- No strategy doctrine mutation.\n"
    "- No replay engine mutation.\n\n"
    "## Next\n\n"
    "LANE-D-D3: read-only replay result indexer contract.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "candidate_count": len(candidates),
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
