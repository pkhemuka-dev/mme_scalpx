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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d7_ml_dataset_probe_{TS}"
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
    "etc/replay_optimization/ml_profiles/ml_dataset_export_contract.json",
    "bin/proof_replay_optimization_d7_ml_dataset.py",
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
    "bin/proof_replay_optimization_d7_ml_dataset.py",
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
    raise SystemExit(f"missing expected D7 files: {missing}")

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
    "etc/replay_optimization/ml_profiles/ml_dataset_export_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/ml_profiles/ml_dataset_export_contract.json"])
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D7 config replay execution safety failed")
if config["safety"]["model_training_allowed"] is not False:
    raise SystemExit("D7 config model training safety failed")
if config["safety"]["model_prediction_allowed"] is not False:
    raise SystemExit("D7 config model prediction safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D7 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D7 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D7 config paper/live safety failed")
if config["dataset_policy"]["labels_bound_in_d7"] is not False:
    raise SystemExit("D7 labels must not be bound")
if config["dataset_policy"]["training_allowed_in_d7"] is not False:
    raise SystemExit("D7 training must not be allowed")

ml_dataset = importlib.import_module("app.mme_scalpx.replay_optimization.ml_dataset")

d5_latest = ROOT / "run" / "proofs" / "proof_lane_d_d5_candidate_matrix_latest.json"
candidate_matrix_path = latest_path_from_proof(d5_latest, "candidate_matrix_path")

optimization_id = f"D7_ML_DATASET_PROBE_{TS}"
result = ml_dataset.write_ml_dataset_export(
    optimization_id,
    ARTIFACT_ROOT,
    candidate_matrix_path=candidate_matrix_path,
    max_rows=10000,
)

for path_value in [
    result.ml_dataset_schema_path,
    result.ml_dataset_json_path,
    result.ml_dataset_csv_path,
    result.ml_training_manifest_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D7 output missing: {path_value}")

dataset_payload = load_json(Path(result.ml_dataset_json_path))
rows = dataset_payload.get("rows", [])
if not isinstance(rows, list) or not rows:
    raise SystemExit("D7 ML dataset rows missing")

sample_row = rows[0]
if sample_row.get("label_pnl") is not None:
    raise SystemExit("D7 label_pnl must remain null")
if sample_row.get("label_profitable") is not None:
    raise SystemExit("D7 label_profitable must remain null")
if sample_row.get("usage_class") != "research_only_unlabeled":
    raise SystemExit("D7 usage_class must remain research_only_unlabeled")

training_manifest = load_json(Path(result.ml_training_manifest_path))
if training_manifest.get("training_allowed") is not False:
    raise SystemExit("D7 training manifest must forbid training")
if training_manifest.get("label_pnl_bound") is not False:
    raise SystemExit("D7 training manifest label_pnl_bound must be false")
if training_manifest.get("production_claim_allowed") is not False:
    raise SystemExit("D7 training manifest production claim must be false")

if result.replay_execution_performed is not False:
    raise SystemExit("D7 unexpectedly performed replay execution")
if result.model_training_performed is not False:
    raise SystemExit("D7 unexpectedly performed model training")
if result.broker_calls_executed is not False:
    raise SystemExit("D7 unexpectedly executed broker calls")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D7 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D7 unexpectedly enabled paper/live")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D7",
    "name": "ml_dataset_schema_exporter_contract",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "ML_DATASET_SCHEMA_EXPORT_CONTRACT_ONLY",
    "d5_dependency_observed": bool(candidate_matrix_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "candidate_matrix_path": candidate_matrix_path,
    "ml_dataset_schema_path": result.ml_dataset_schema_path,
    "ml_dataset_json_path": result.ml_dataset_json_path,
    "ml_dataset_csv_path": result.ml_dataset_csv_path,
    "ml_training_manifest_path": result.ml_training_manifest_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "ml_dataset_row_count": result.ml_dataset_row_count,
    "readiness_verdict": result.readiness_verdict,
    "sample_ml_dataset_row": sample_row,
    "training_manifest": training_manifest,
    "safety": {
        "ml_dataset_exported": True,
        "labels_bound": False,
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
    "next_recommended_batch": "LANE-D-D8_RESULT_BINDING_SCHEMA_CONTRACT_NO_REPLAY_EXECUTION"
}

proof_path = PROOF_DIR / f"proof_lane_d_d7_ml_dataset_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d7_ml_dataset_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d7_ml_dataset_{TS}.md"
milestone_path.write_text(
    "# LANE D D7 — ML Dataset Schema Exporter Contract\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D7 ML dataset schema/exporter contract created and proved.\n\n"
    "## Scope\n\n"
    "- Added `ml_dataset.py`.\n"
    "- Added ML dataset export config contract.\n"
    "- Generated `07_ml_dataset_schema.json`.\n"
    "- Generated `07_ml_dataset_rows.json` and `07_ml_dataset_rows.csv`.\n"
    "- Generated `08_ml_training_manifest.json`.\n"
    "- Generated `09_optimizer_verdict.json`.\n\n"
    "## Important Limitation\n\n"
    "D7 exports unlabeled research-only ML dataset rows. It does not bind replay PnL labels, "
    "does not train a model, does not predict, and does not approve strategy ranking.\n\n"
    "## Safety\n\n"
    "- No replay execution.\n"
    "- No model training.\n"
    "- No model prediction.\n"
    "- No broker calls.\n"
    "- No live Redis writes.\n"
    "- No paper/live enablement.\n"
    "- No runtime service start.\n"
    "- No strategy doctrine mutation.\n"
    "- No replay engine mutation.\n\n"
    "## Next\n\n"
    "LANE-D-D8: result binding schema contract, no replay execution.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "ml_dataset_schema_path": result.ml_dataset_schema_path,
    "ml_dataset_json_path": result.ml_dataset_json_path,
    "ml_dataset_csv_path": result.ml_dataset_csv_path,
    "ml_training_manifest_path": result.ml_training_manifest_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "ml_dataset_row_count": result.ml_dataset_row_count,
    "readiness_verdict": result.readiness_verdict,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
