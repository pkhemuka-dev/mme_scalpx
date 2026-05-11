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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d8_result_binding_probe_{TS}"
PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
    "etc/replay_optimization/result_binding/result_binding_contract.json",
    "bin/proof_replay_optimization_d8_result_binding.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
    "bin/proof_replay_optimization_d8_result_binding.py",
]

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "ast",
    "csv",
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_path_from_proof(proof_path: Path, key: str) -> str | None:
    if not proof_path.exists():
        return None
    try:
        payload = load_json(proof_path)
    except Exception:
        return None
    value = payload.get(key)
    return value if isinstance(value, str) else None


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D8 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in [
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {
            "contracts",
            "sweep_space",
            "result_indexer",
            "raw_indexer",
            "candidate_matrix",
            "leaderboard",
            "ml_dataset",
            "result_binding",
        }:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

TEXT_AUDIT_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
    "etc/replay_optimization/result_binding/result_binding_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/result_binding/result_binding_contract.json"])
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D8 config replay execution safety failed")
if config["safety"]["label_binding_allowed"] is not False:
    raise SystemExit("D8 config label binding safety failed")
if config["safety"]["model_training_allowed"] is not False:
    raise SystemExit("D8 config model training safety failed")
if config["safety"]["model_prediction_allowed"] is not False:
    raise SystemExit("D8 config model prediction safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D8 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D8 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D8 config paper/live safety failed")
if config["binding_policy"]["labels_bound_in_d8"] is not False:
    raise SystemExit("D8 labels must not be bound")
if config["binding_policy"]["real_pnl_calculation_allowed"] is not False:
    raise SystemExit("D8 real PnL calculation must not be allowed")

result_binding = importlib.import_module("app.mme_scalpx.replay_optimization.result_binding")

d3_latest = ROOT / "run" / "proofs" / "proof_lane_d_d3_replay_result_indexer_latest.json"
d5_latest = ROOT / "run" / "proofs" / "proof_lane_d_d5_candidate_matrix_latest.json"
d7_latest = ROOT / "run" / "proofs" / "proof_lane_d_d7_ml_dataset_latest.json"

replay_index_path = latest_path_from_proof(d3_latest, "replay_input_index_path")
candidate_matrix_path = latest_path_from_proof(d5_latest, "candidate_matrix_path")
ml_dataset_path = latest_path_from_proof(d7_latest, "ml_dataset_json_path")

optimization_id = f"D8_RESULT_BINDING_PROBE_{TS}"
result = result_binding.write_result_binding_schema(
    optimization_id,
    ARTIFACT_ROOT,
    candidate_matrix_path=candidate_matrix_path,
    ml_dataset_path=ml_dataset_path,
    replay_index_path=replay_index_path,
    max_rows=10000,
)

for path_value in [
    result.result_binding_schema_path,
    result.result_binding_rows_json_path,
    result.result_binding_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D8 output missing: {path_value}")

rows_payload = load_json(Path(result.result_binding_rows_json_path))
rows = rows_payload.get("rows", [])
if not isinstance(rows, list) or not rows:
    raise SystemExit("D8 result binding rows missing")

sample_row = rows[0]
if sample_row.get("label_pnl") is not None:
    raise SystemExit("D8 label_pnl must remain null")
if sample_row.get("label_profitable") is not None:
    raise SystemExit("D8 label_profitable must remain null")
if sample_row.get("label_exit_reason") is not None:
    raise SystemExit("D8 label_exit_reason must remain null")
if sample_row.get("label_binding_status") != "UNBOUND_PENDING_VERIFIED_REPLAY_RESULT":
    raise SystemExit("D8 binding status must remain unbound")

if result.labels_bound is not False:
    raise SystemExit("D8 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D8 unexpectedly performed replay execution")
if result.model_training_performed is not False:
    raise SystemExit("D8 unexpectedly performed model training")
if result.broker_calls_executed is not False:
    raise SystemExit("D8 unexpectedly executed broker calls")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D8 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D8 unexpectedly enabled paper/live")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D8",
    "name": "result_binding_schema_contract_no_replay_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "RESULT_BINDING_SCHEMA_CONTRACT_ONLY",
    "d3_dependency_observed": bool(replay_index_path),
    "d5_dependency_observed": bool(candidate_matrix_path),
    "d7_dependency_observed": bool(ml_dataset_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "candidate_matrix_path": candidate_matrix_path,
    "ml_dataset_path": ml_dataset_path,
    "replay_index_path": replay_index_path,
    "result_binding_schema_path": result.result_binding_schema_path,
    "result_binding_rows_json_path": result.result_binding_rows_json_path,
    "result_binding_rows_csv_path": result.result_binding_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "binding_row_count": result.binding_row_count,
    "readiness_verdict": result.readiness_verdict,
    "sample_result_binding_row": sample_row,
    "safety": {
        "result_binding_schema_exported": True,
        "labels_bound": False,
        "real_pnl_calculation_performed": False,
        "prediction_performed": False,
        "replay_execution_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
        "runtime_services_started": False,
        "strategy_doctrine_changed": False,
        "replay_engine_changed": False,
        "production_profit_claim_allowed": False
    },
    "next_recommended_batch": "LANE-D-D9_SAMPLE_SIZE_AND_OVERFIT_RISK_CONTRACT"
}

proof_path = PROOF_DIR / f"proof_lane_d_d8_result_binding_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d8_result_binding_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d8_result_binding_{TS}.md"
milestone_path.write_text(
    "# LANE D D8 — Result Binding Schema Contract\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D8 result-binding schema contract created and proved.\n\n"
    "## Scope\n\n"
    "- Added `result_binding.py`.\n"
    "- Added result-binding config contract.\n"
    "- Generated `10_result_binding_schema.json`.\n"
    "- Generated `10_result_binding_rows.json` and `10_result_binding_rows.csv`.\n"
    "- Generated `09_optimizer_verdict.json`.\n\n"
    "## Important Limitation\n\n"
    "D8 is schema-only. It does not bind real replay PnL labels, does not calculate profit, "
    "does not train a model, and does not approve strategy ranking.\n\n"
    "## Safety\n\n"
    "- No replay execution.\n"
    "- No label binding.\n"
    "- No real PnL calculation.\n"
    "- No model training.\n"
    "- No model prediction.\n"
    "- No broker calls.\n"
    "- No live Redis writes.\n"
    "- No paper/live enablement.\n"
    "- No runtime service start.\n"
    "- No strategy doctrine mutation.\n"
    "- No replay engine mutation.\n\n"
    "## Next\n\n"
    "LANE-D-D9: sample size and overfit-risk contract.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "result_binding_schema_path": result.result_binding_schema_path,
    "result_binding_rows_json_path": result.result_binding_rows_json_path,
    "result_binding_rows_csv_path": result.result_binding_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "binding_row_count": result.binding_row_count,
    "readiness_verdict": result.readiness_verdict,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
