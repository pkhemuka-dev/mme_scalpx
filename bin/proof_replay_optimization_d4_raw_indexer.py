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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d4_raw_index_probe_{TS}"
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
    "etc/replay_optimization/indexers/raw_feature_index_contract.json",
    "bin/proof_replay_optimization_d4_raw_indexer.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "bin/proof_replay_optimization_d4_raw_indexer.py",
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


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D4 files: {missing}")

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
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "etc/replay_optimization/indexers/raw_feature_index_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

contracts = importlib.import_module("app.mme_scalpx.replay_optimization.contracts")
raw_indexer = importlib.import_module("app.mme_scalpx.replay_optimization.raw_indexer")

config = json.loads(files["etc/replay_optimization/indexers/raw_feature_index_contract.json"].read_text(encoding="utf-8"))
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D4 config replay execution safety failed")
if config["safety"]["ml_training_allowed"] is not False:
    raise SystemExit("D4 config ML training safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D4 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D4 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D4 config paper/live safety failed")

optimization_id = f"D4_RAW_INDEX_PROBE_{TS}"
index = raw_indexer.build_raw_feature_index(
    optimization_id,
    ("run/research_gate", "run/research_capture"),
    max_files=5000,
)
index_path = raw_indexer.write_raw_feature_index(index, ARTIFACT_ROOT)
rows = raw_indexer.raw_feature_ref_rows_from_index(index)
summary = raw_indexer.raw_indexer_summary(("run/research_gate", "run/research_capture"))

if not Path(index_path).exists():
    raise SystemExit("D4 raw feature index was not written")

if index.replay_execution_performed is not False:
    raise SystemExit("D4 unexpectedly performed replay execution")
if index.ml_training_performed is not False:
    raise SystemExit("D4 unexpectedly performed ML training")
if index.broker_calls_executed is not False:
    raise SystemExit("D4 unexpectedly executed broker calls")
if index.live_redis_writes_executed is not False:
    raise SystemExit("D4 unexpectedly wrote live Redis")
if index.paper_or_live_enabled is not False:
    raise SystemExit("D4 unexpectedly enabled paper/live")

for row in rows[:50]:
    if not isinstance(row, contracts.RawFeatureRefRow):
        raise SystemExit("D4 raw feature ref row type mismatch")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D4",
    "name": "read_only_raw_research_feature_indexer_contract",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "READ_ONLY_RAW_INDEX_CONTRACT",
    "d3_dependency_observed": True,
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "raw_feature_index_path": index_path.as_posix(),
    "artifact_count": index.artifact_count,
    "feature_families": list(index.feature_families),
    "raw_feature_ref_row_count": len(rows),
    "optimizer_verdict": index.optimizer_verdict,
    "summary": summary,
    "safety": {
        "read_only_indexing_performed": True,
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
    "next_recommended_batch": "LANE-D-D5_CANDIDATE_MATRIX_BUILDER_CONTRACT"
}

proof_path = PROOF_DIR / f"proof_lane_d_d4_raw_feature_indexer_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d4_raw_feature_indexer_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d4_raw_feature_indexer_{TS}.md"
milestone_path.write_text(
    "# LANE D D4 — Read-only RAW / Research Feature Indexer Contract\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D4 read-only RAW / Research Gate feature indexer contract created and proved.\n\n"
    "## Scope\n\n"
    "- Added `raw_indexer.py`.\n"
    "- Added RAW feature indexer config contract.\n"
    "- Generated `04_raw_feature_index.json` under `run/replay_optimization/`.\n"
    "- Created RAW feature reference rows where matching artifacts exist.\n\n"
    "## Safety\n\n"
    "- Read-only indexing only.\n"
    "- No replay execution.\n"
    "- No ML training.\n"
    "- No broker calls.\n"
    "- No live Redis writes.\n"
    "- No paper/live enablement.\n"
    "- No runtime service start.\n"
    "- No strategy doctrine mutation.\n"
    "- No replay engine mutation.\n\n"
    "## Next\n\n"
    "LANE-D-D5: candidate matrix builder contract.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "raw_feature_index_path": index_path.as_posix(),
    "artifact_count": index.artifact_count,
    "feature_families": list(index.feature_families),
    "raw_feature_ref_row_count": len(rows),
    "optimizer_verdict": index.optimizer_verdict,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
