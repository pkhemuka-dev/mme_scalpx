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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d9_sample_risk_probe_{TS}"
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
    "etc/replay_optimization/risk/sample_size_overfit_contract.json",
    "bin/proof_replay_optimization_d9_sample_risk.py",
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
    "bin/proof_replay_optimization_d9_sample_risk.py",
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
    raise SystemExit(f"missing expected D9 files: {missing}")

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
    "etc/replay_optimization/risk/sample_size_overfit_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/risk/sample_size_overfit_contract.json"])
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D9 config replay execution safety failed")
if config["safety"]["label_binding_allowed"] is not False:
    raise SystemExit("D9 config label binding safety failed")
if config["safety"]["real_pnl_calculation_allowed"] is not False:
    raise SystemExit("D9 config real PnL safety failed")
if config["safety"]["model_training_allowed"] is not False:
    raise SystemExit("D9 config model training safety failed")
if config["safety"]["model_prediction_allowed"] is not False:
    raise SystemExit("D9 config prediction safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D9 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D9 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D9 config paper/live safety failed")

sample_risk = importlib.import_module("app.mme_scalpx.replay_optimization.sample_risk")

d8_latest = ROOT / "run" / "proofs" / "proof_lane_d_d8_result_binding_latest.json"
result_binding_rows_path = latest_path_from_proof(d8_latest, "result_binding_rows_json_path")

optimization_id = f"D9_SAMPLE_RISK_PROBE_{TS}"
result = sample_risk.write_sample_risk_reports(
    optimization_id,
    ARTIFACT_ROOT,
    result_binding_rows_path=result_binding_rows_path,
)

for path_value in [
    result.sample_size_report_path,
    result.overfit_risk_report_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D9 output missing: {path_value}")

sample_report = load_json(Path(result.sample_size_report_path))
overfit_report = load_json(Path(result.overfit_risk_report_path))

if sample_report.get("training_allowed") is not False:
    raise SystemExit("D9 sample report must forbid training")
if sample_report.get("labeled_row_count") != 0:
    raise SystemExit("D9 expected zero labeled rows from D8")
if overfit_report.get("model_training_allowed") is not False:
    raise SystemExit("D9 overfit report must forbid model training")
if overfit_report.get("overfit_risk_level") != "HIGH_NOT_READY":
    raise SystemExit("D9 expected HIGH_NOT_READY overfit risk for unlabeled rows")

if result.training_allowed is not False:
    raise SystemExit("D9 unexpectedly allowed training")
if result.replay_execution_performed is not False:
    raise SystemExit("D9 unexpectedly performed replay execution")
if result.model_training_performed is not False:
    raise SystemExit("D9 unexpectedly performed model training")
if result.model_prediction_performed is not False:
    raise SystemExit("D9 unexpectedly performed prediction")
if result.broker_calls_executed is not False:
    raise SystemExit("D9 unexpectedly executed broker calls")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D9 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D9 unexpectedly enabled paper/live")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D9",
    "name": "sample_size_and_overfit_risk_contract",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "SAMPLE_SIZE_OVERFIT_RISK_CONTRACT_ONLY",
    "d8_dependency_observed": bool(result_binding_rows_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "result_binding_rows_path": result_binding_rows_path,
    "sample_size_report_path": result.sample_size_report_path,
    "overfit_risk_report_path": result.overfit_risk_report_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "readiness_verdict": result.readiness_verdict,
    "overfit_risk_level": result.overfit_risk_level,
    "sample_report": sample_report,
    "overfit_report": overfit_report,
    "safety": {
        "sample_size_report_built": True,
        "overfit_risk_report_built": True,
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
    "next_recommended_batch": "LANE-D-D10_REPLAY_RESULT_BINDING_IMPLEMENTATION_GATE_AUDIT_NO_EXECUTION"
}

proof_path = PROOF_DIR / f"proof_lane_d_d9_sample_risk_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d9_sample_risk_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d9_sample_risk_{TS}.md"
milestone_path.write_text(
    "# LANE D D9 — Sample Size + Overfit Risk Contract\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D9 sample-size and overfit-risk contract created and proved.\n\n"
    "## Scope\n\n"
    "- Added `sample_risk.py`.\n"
    "- Added sample-size / overfit-risk config contract.\n"
    "- Generated `11_sample_size_report.json`.\n"
    "- Generated `12_overfit_risk_report.json`.\n"
    "- Generated `09_optimizer_verdict.json`.\n\n"
    "## Important Limitation\n\n"
    "D9 is a gate/report only. It does not bind labels, does not calculate real PnL, "
    "does not train or predict, and does not approve optimization.\n\n"
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
    "LANE-D-D10: replay result-binding implementation gate audit, no execution.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "sample_size_report_path": result.sample_size_report_path,
    "overfit_risk_report_path": result.overfit_risk_report_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "readiness_verdict": result.readiness_verdict,
    "overfit_risk_level": result.overfit_risk_level,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
