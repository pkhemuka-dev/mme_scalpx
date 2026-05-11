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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d11_source_map_probe_{TS}"
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
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
    "etc/replay_optimization/source_map/replay_result_source_map_contract.json",
    "bin/proof_replay_optimization_d11_source_map.py",
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
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
    "bin/proof_replay_optimization_d11_source_map.py",
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
    raise SystemExit(f"missing expected D11 files: {missing}")

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
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
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
            "sample_risk",
            "implementation_gate",
            "source_map",
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
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
    "etc/replay_optimization/source_map/replay_result_source_map_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/source_map/replay_result_source_map_contract.json"])
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D11 config replay execution safety failed")
if config["safety"]["label_binding_allowed"] is not False:
    raise SystemExit("D11 config label binding safety failed")
if config["safety"]["real_pnl_calculation_allowed"] is not False:
    raise SystemExit("D11 config real PnL safety failed")
if config["safety"]["model_training_allowed"] is not False:
    raise SystemExit("D11 config model training safety failed")
if config["safety"]["model_prediction_allowed"] is not False:
    raise SystemExit("D11 config prediction safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D11 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D11 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D11 config paper/live safety failed")

source_map = importlib.import_module("app.mme_scalpx.replay_optimization.source_map")

d3_latest = ROOT / "run" / "proofs" / "proof_lane_d_d3_replay_result_indexer_latest.json"
d8_latest = ROOT / "run" / "proofs" / "proof_lane_d_d8_result_binding_latest.json"

replay_index_path = latest_path_from_proof(d3_latest, "replay_input_index_path")
result_binding_rows_path = latest_path_from_proof(d8_latest, "result_binding_rows_json_path")

optimization_id = f"D11_SOURCE_MAP_PROBE_{TS}"
result = source_map.write_source_map(
    optimization_id,
    ARTIFACT_ROOT,
    replay_index_path=replay_index_path,
    result_binding_rows_path=result_binding_rows_path,
    max_rows=10000,
)

for path_value in [
    result.source_map_json_path,
    result.source_map_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D11 output missing: {path_value}")

source_map_payload = load_json(Path(result.source_map_json_path))
rows = source_map_payload.get("rows", [])
if not isinstance(rows, list) or not rows:
    raise SystemExit("D11 source map rows missing")

sample_row = rows[0]
if sample_row.get("label_binding_allowed") is not False:
    raise SystemExit("D11 must not allow label binding")
if sample_row.get("labels_bound") is not False:
    raise SystemExit("D11 must not bind labels")
if result.label_binding_allowed is not False:
    raise SystemExit("D11 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D11 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D11 unexpectedly performed replay execution")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D11 unexpectedly calculated real PnL")
if result.model_training_performed is not False:
    raise SystemExit("D11 unexpectedly trained a model")
if result.model_prediction_performed is not False:
    raise SystemExit("D11 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D11 unexpectedly executed broker calls")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D11 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D11 unexpectedly enabled paper/live")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D11",
    "name": "replay_result_source_map_contract_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "REPLAY_RESULT_SOURCE_MAP_CONTRACT_ONLY",
    "d3_dependency_observed": bool(replay_index_path),
    "d8_dependency_observed": bool(result_binding_rows_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "replay_index_path": replay_index_path,
    "result_binding_rows_path": result_binding_rows_path,
    "source_map_json_path": result.source_map_json_path,
    "source_map_csv_path": result.source_map_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "source_map_row_count": result.source_map_row_count,
    "source_map_status": result.source_map_status,
    "sample_source_map_row": sample_row,
    "safety": {
        "source_map_built": True,
        "label_binding_allowed": False,
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
    "next_recommended_batch": "LANE-D-D12_REPLAY_RESULT_BINDING_PRECONDITION_AUDIT_NO_LABEL_BINDING"
}

proof_path = PROOF_DIR / f"proof_lane_d_d11_source_map_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d11_source_map_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d11_source_map_{TS}.md"
milestone_path.write_text(
    "# LANE D D11 — Replay Result Source Map Contract\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D11 replay result source-map contract created and proved.\n\n"
    "## Scope\n\n"
    "- Added `source_map.py`.\n"
    "- Added replay result source-map config contract.\n"
    "- Generated `14_replay_result_source_map.json`.\n"
    "- Generated `14_replay_result_source_map.csv`.\n"
    "- Generated `09_optimizer_verdict.json`.\n\n"
    "## Important Limitation\n\n"
    "D11 is source-map only. It does not map candidates to actual trades, does not bind labels, "
    "does not calculate PnL, does not train/predict, and does not approve optimization.\n\n"
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
    "LANE-D-D12: replay result-binding precondition audit, no label binding.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "source_map_json_path": result.source_map_json_path,
    "source_map_csv_path": result.source_map_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "source_map_row_count": result.source_map_row_count,
    "source_map_status": result.source_map_status,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
