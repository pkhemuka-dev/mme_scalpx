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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d5_candidate_matrix_probe_{TS}"
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
    "etc/replay_optimization/matrix/candidate_matrix_contract.json",
    "bin/proof_replay_optimization_d5_candidate_matrix.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "bin/proof_replay_optimization_d5_candidate_matrix.py",
]

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
    raise SystemExit(f"missing expected D5 files: {missing}")

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
    "etc/replay_optimization/matrix/candidate_matrix_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/matrix/candidate_matrix_contract.json"])
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D5 config replay execution safety failed")
if config["safety"]["model_training_allowed"] is not False:
    raise SystemExit("D5 config model training safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D5 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D5 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D5 config paper/live safety failed")

candidate_matrix = importlib.import_module("app.mme_scalpx.replay_optimization.candidate_matrix")

d3_latest = ROOT / "run" / "proofs" / "proof_lane_d_d3_replay_result_indexer_latest.json"
d4_latest = ROOT / "run" / "proofs" / "proof_lane_d_d4_raw_feature_indexer_latest.json"

replay_index_path = latest_path_from_proof(d3_latest, "replay_input_index_path")
raw_index_path = latest_path_from_proof(d4_latest, "raw_feature_index_path")

optimization_id = f"D5_CANDIDATE_MATRIX_PROBE_{TS}"
result = candidate_matrix.write_candidate_matrix(
    optimization_id,
    ARTIFACT_ROOT,
    replay_index_path=replay_index_path,
    raw_index_path=raw_index_path,
    max_candidates=10000,
)

if not Path(result.candidate_matrix_path).exists():
    raise SystemExit("D5 candidate matrix file missing")
if not Path(result.optimizer_verdict_path).exists():
    raise SystemExit("D5 optimizer verdict file missing")

matrix_payload = load_json(Path(result.candidate_matrix_path))
matrix_rows = matrix_payload.get("rows", [])
if not isinstance(matrix_rows, list) or not matrix_rows:
    raise SystemExit("D5 candidate matrix rows missing")

if result.replay_execution_performed is not False:
    raise SystemExit("D5 unexpectedly performed replay execution")
if result.model_training_performed is not False:
    raise SystemExit("D5 unexpectedly performed model training")
if result.broker_calls_executed is not False:
    raise SystemExit("D5 unexpectedly executed broker calls")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D5 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D5 unexpectedly enabled paper/live")

sample_row = matrix_rows[0]
if sample_row.get("status") != "PROPOSED_ONLY":
    raise SystemExit("D5 matrix row status must remain PROPOSED_ONLY")
if sample_row.get("readiness_verdict") != result.readiness_verdict:
    raise SystemExit("D5 readiness verdict mismatch")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D5",
    "name": "candidate_matrix_builder_contract",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CANDIDATE_MATRIX_CONTRACT_ONLY",
    "d3_dependency_observed": bool(replay_index_path),
    "d4_dependency_observed": bool(raw_index_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "candidate_matrix_path": result.candidate_matrix_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "matrix_row_count": result.matrix_row_count,
    "replay_index_path": replay_index_path,
    "raw_index_path": raw_index_path,
    "replay_artifact_count": result.replay_artifact_count,
    "raw_artifact_count": result.raw_artifact_count,
    "readiness_verdict": result.readiness_verdict,
    "sample_matrix_row": sample_row,
    "safety": {
        "candidate_matrix_built": True,
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
    "next_recommended_batch": "LANE-D-D6_LEADERBOARD_SCHEMA_AND_BUILDER_CONTRACT"
}

proof_path = PROOF_DIR / f"proof_lane_d_d5_candidate_matrix_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d5_candidate_matrix_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d5_candidate_matrix_{TS}.md"
milestone_path.write_text(
    "# LANE D D5 — Candidate Matrix Builder Contract\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D5 candidate matrix builder contract created and proved.\n\n"
    "## Scope\n\n"
    "- Added `candidate_matrix.py`.\n"
    "- Added candidate matrix config contract.\n"
    "- Generated `02_candidate_matrix.json` under `run/replay_optimization/`.\n"
    "- Linked D2 proposed candidates with D3/D4 index references where present.\n\n"
    "## Safety\n\n"
    "- Candidate matrix only.\n"
    "- No replay execution.\n"
    "- No model training.\n"
    "- No broker calls.\n"
    "- No live Redis writes.\n"
    "- No paper/live enablement.\n"
    "- No runtime service start.\n"
    "- No strategy doctrine mutation.\n"
    "- No replay engine mutation.\n\n"
    "## Next\n\n"
    "LANE-D-D6: leaderboard schema and builder contract.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "candidate_matrix_path": result.candidate_matrix_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "matrix_row_count": result.matrix_row_count,
    "readiness_verdict": result.readiness_verdict,
    "replay_artifact_count": result.replay_artifact_count,
    "raw_artifact_count": result.raw_artifact_count,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
