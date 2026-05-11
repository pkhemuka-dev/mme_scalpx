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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d10_binding_gate_probe_{TS}"
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
    "etc/replay_optimization/gates/result_binding_implementation_gate.json",
    "bin/proof_replay_optimization_d10_binding_gate.py",
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
    "bin/proof_replay_optimization_d10_binding_gate.py",
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
    raise SystemExit(f"missing expected D10 files: {missing}")

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
    "etc/replay_optimization/gates/result_binding_implementation_gate.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/gates/result_binding_implementation_gate.json"])
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D10 config replay execution safety failed")
if config["safety"]["label_binding_allowed"] is not False:
    raise SystemExit("D10 config label binding safety failed")
if config["safety"]["real_pnl_calculation_allowed"] is not False:
    raise SystemExit("D10 config PnL safety failed")
if config["safety"]["model_training_allowed"] is not False:
    raise SystemExit("D10 config model training safety failed")
if config["safety"]["model_prediction_allowed"] is not False:
    raise SystemExit("D10 config model prediction safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D10 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D10 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D10 config paper/live safety failed")

gate = importlib.import_module("app.mme_scalpx.replay_optimization.implementation_gate")

d3_latest = ROOT / "run" / "proofs" / "proof_lane_d_d3_replay_result_indexer_latest.json"
d8_latest = ROOT / "run" / "proofs" / "proof_lane_d_d8_result_binding_latest.json"
d9_latest = ROOT / "run" / "proofs" / "proof_lane_d_d9_sample_risk_latest.json"

replay_index_path = latest_path_from_proof(d3_latest, "replay_input_index_path")
result_binding_rows_path = latest_path_from_proof(d8_latest, "result_binding_rows_json_path")
sample_size_report_path = latest_path_from_proof(d9_latest, "sample_size_report_path")
overfit_risk_report_path = latest_path_from_proof(d9_latest, "overfit_risk_report_path")

optimization_id = f"D10_BINDING_GATE_PROBE_{TS}"
result = gate.write_gate_audit(
    optimization_id,
    ARTIFACT_ROOT,
    replay_index_path=replay_index_path,
    result_binding_rows_path=result_binding_rows_path,
    sample_size_report_path=sample_size_report_path,
    overfit_risk_report_path=overfit_risk_report_path,
)

for path_value in [
    result.gate_audit_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D10 output missing: {path_value}")

gate_audit = load_json(Path(result.gate_audit_path))
if gate_audit.get("implementation_allowed") is not False:
    raise SystemExit("D10 must not allow implementation")
if gate_audit.get("label_binding_allowed") is not False:
    raise SystemExit("D10 must not allow label binding")
if gate_audit.get("model_training_allowed") is not False:
    raise SystemExit("D10 must not allow model training")
if gate_audit.get("labeled_row_count") != 0:
    raise SystemExit("D10 expected zero labeled rows from D9")
if result.gate_status != "BLOCKED_NO_LABELS_BOUND_EXPECTED":
    raise SystemExit(f"D10 expected BLOCKED_NO_LABELS_BOUND_EXPECTED, got {result.gate_status}")

if result.implementation_allowed is not False:
    raise SystemExit("D10 unexpectedly allowed implementation")
if result.label_binding_allowed is not False:
    raise SystemExit("D10 unexpectedly allowed label binding")
if result.model_training_allowed is not False:
    raise SystemExit("D10 unexpectedly allowed model training")
if result.replay_execution_performed is not False:
    raise SystemExit("D10 unexpectedly performed replay execution")
if result.labels_bound is not False:
    raise SystemExit("D10 unexpectedly bound labels")
if result.broker_calls_executed is not False:
    raise SystemExit("D10 unexpectedly executed broker calls")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D10 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D10 unexpectedly enabled paper/live")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D10",
    "name": "replay_result_binding_implementation_gate_audit_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "RESULT_BINDING_IMPLEMENTATION_GATE_AUDIT_ONLY",
    "d3_dependency_observed": bool(replay_index_path),
    "d8_dependency_observed": bool(result_binding_rows_path),
    "d9_dependency_observed": bool(sample_size_report_path and overfit_risk_report_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "replay_index_path": replay_index_path,
    "result_binding_rows_path": result_binding_rows_path,
    "sample_size_report_path": sample_size_report_path,
    "overfit_risk_report_path": overfit_risk_report_path,
    "gate_audit_path": result.gate_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "gate_status": result.gate_status,
    "gate_audit": gate_audit,
    "safety": {
        "gate_audit_built": True,
        "implementation_allowed": False,
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
    "next_recommended_batch": "LANE-D-D11_REPLAY_RESULT_SOURCE_MAP_CONTRACT_NO_LABEL_BINDING"
}

proof_path = PROOF_DIR / f"proof_lane_d_d10_binding_gate_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d10_binding_gate_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d10_binding_gate_{TS}.md"
milestone_path.write_text(
    "# LANE D D10 — Result-Binding Implementation Gate Audit\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D10 gate audit created and proved.\n\n"
    "## Gate Status\n\n"
    f"`{result.gate_status}`\n\n"
    "## Scope\n\n"
    "- Added `implementation_gate.py`.\n"
    "- Added result-binding implementation gate config.\n"
    "- Generated `13_result_binding_implementation_gate.json`.\n"
    "- Generated `09_optimizer_verdict.json`.\n\n"
    "## Important Limitation\n\n"
    "D10 is an audit only. It does not implement label binding, does not calculate PnL, "
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
    "LANE-D-D11: replay result source-map contract, no label binding.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "gate_audit_path": result.gate_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "gate_status": result.gate_status,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
