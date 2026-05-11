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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d35_candidate_replay_materialization_validator_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_replay_materialization_validator.py",
    "etc/replay_optimization/binding/candidate_replay_materialization_validator_contract.json",
    "bin/proof_replay_optimization_d35_candidate_replay_materialization_validator.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_replay_materialization_validator.py",
    "bin/proof_replay_optimization_d35_candidate_replay_materialization_validator.py",
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
    roots = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
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
    raise SystemExit(f"missing expected D35 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/candidate_replay_materialization_validator.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/candidate_replay_materialization_validator.py",
    "etc/replay_optimization/binding/candidate_replay_materialization_validator_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/binding/candidate_replay_materialization_validator_contract.json"])
safety = config["safety"]
for key in [
    "replay_execution_allowed",
    "result_pack_creation_allowed",
    "artifact_file_creation_allowed",
    "candidate_context_attachment_allowed",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "real_pnl_calculation_allowed",
    "model_training_allowed",
    "model_prediction_allowed",
    "broker_calls_allowed",
    "live_redis_writes_allowed",
    "paper_live_enablement_allowed",
]:
    if safety[key] is not False:
        raise SystemExit(f"D35 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.candidate_replay_materialization_validator")

d34_latest = ROOT / "run" / "proofs" / "proof_lane_d_d34_candidate_replay_materialization_latest.json"
materialization_rows_path = latest_path_from_proof(d34_latest, "materialization_rows_json_path")

optimization_id = f"D35_CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_PROBE_{TS}"
result = mod.write_candidate_replay_materialization_validation(
    optimization_id,
    ARTIFACT_ROOT,
    materialization_rows_path=materialization_rows_path,
)

for path_value in [
    result.validation_report_path,
    result.validation_rows_json_path,
    result.validation_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D35 output missing: {path_value}")

report = load_json(Path(result.validation_report_path))
rows_payload = load_json(Path(result.validation_rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list) or not rows:
    raise SystemExit("D35 validation rows missing")

sample_row = rows[0]
for key in [
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
]:
    if sample_row.get(key) is not False:
        raise SystemExit(f"D35 row safety failed: {key}")

for key in [
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if report.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D35 report safety failed: {key}")

if result.replay_execution_allowed is not False:
    raise SystemExit("D35 unexpectedly allowed replay execution")
if result.replay_execution_performed is not False:
    raise SystemExit("D35 unexpectedly executed replay")
if result.result_pack_created is not False:
    raise SystemExit("D35 unexpectedly created result pack")
if result.candidate_context_attached is not False:
    raise SystemExit("D35 unexpectedly attached candidate context")
if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D35 unexpectedly allowed matching")
if result.candidate_trade_matching_performed is not False:
    raise SystemExit("D35 unexpectedly performed matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D35 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D35 unexpectedly bound labels")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D35 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D35 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D35 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D35 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D35 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D35 unexpectedly enabled paper/live")

if result.materialization_row_count != 810:
    raise SystemExit(f"D35 expected 810 materialization rows, got {result.materialization_row_count}")
if result.validation_row_count != 810:
    raise SystemExit(f"D35 expected 810 validation rows, got {result.validation_row_count}")
if result.valid_no_execution_count != 810:
    raise SystemExit(f"D35 expected 810 valid rows, got {result.valid_no_execution_count}")
if result.invalid_row_count != 0:
    raise SystemExit(f"D35 expected zero invalid rows, got {result.invalid_row_count}")
if result.duplicate_materialization_id_count != 0:
    raise SystemExit(f"D35 expected zero duplicate materialization IDs, got {result.duplicate_materialization_id_count}")
if result.duplicate_candidate_id_count != 0:
    raise SystemExit(f"D35 expected zero duplicate candidate IDs, got {result.duplicate_candidate_id_count}")
if result.path_policy_violation_row_count != 0:
    raise SystemExit(f"D35 expected zero path policy violations, got {result.path_policy_violation_row_count}")
if result.validation_status != "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATION_PASS_NO_EXECUTION":
    raise SystemExit(f"D35 unexpected validation status: {result.validation_status}")

next_batch = "LANE-D-D36_CANDIDATE_REPLAY_MATERIALIZATION_PREFLIGHT_CONTRACT_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D35",
    "name": "candidate_replay_materialization_validator_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CANDIDATE_REPLAY_MATERIALIZATION_VALIDATOR_NO_EXECUTION",
    "d34_dependency_observed": bool(materialization_rows_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "materialization_rows_path": materialization_rows_path,
    "validation_report_path": result.validation_report_path,
    "validation_rows_json_path": result.validation_rows_json_path,
    "validation_rows_csv_path": result.validation_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "materialization_row_count": result.materialization_row_count,
    "validation_row_count": result.validation_row_count,
    "valid_no_execution_count": result.valid_no_execution_count,
    "invalid_row_count": result.invalid_row_count,
    "duplicate_materialization_id_count": result.duplicate_materialization_id_count,
    "duplicate_candidate_id_count": result.duplicate_candidate_id_count,
    "missing_required_field_row_count": result.missing_required_field_row_count,
    "path_policy_violation_row_count": result.path_policy_violation_row_count,
    "safety_violation_row_count": result.safety_violation_row_count,
    "unexpected_execution_state_row_count": result.unexpected_execution_state_row_count,
    "validation_status": result.validation_status,
    "sample_validation_row": sample_row,
    "safety": {
        "candidate_replay_materialization_validation_built": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_created": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "real_pnl_calculation_performed": False,
        "prediction_performed": False,
        "model_training_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
        "runtime_services_started": False,
        "strategy_doctrine_changed": False,
        "replay_engine_changed": False,
        "production_profit_claim_allowed": False
    },
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d35_candidate_replay_materialization_validator_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d35_candidate_replay_materialization_validator_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d35_candidate_replay_materialization_validator_{TS}.md"
milestone_path.write_text(
    "# LANE D D35 — Candidate Replay Materialization Validator\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D35 candidate replay materialization validator created and proved.\n\n"
    "## Validation Status\n\n"
    f"{result.validation_status}\n\n"
    "## Important Limitation\n\n"
    "D35 is validator-only. It does not execute replay, create artifacts/result packs, attach candidate context, match trades, bind labels, calculate PnL, train/predict, or approve optimization.\n\n"
    "## Next\n\n"
    f"{next_batch}\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "validation_report_path": result.validation_report_path,
    "validation_rows_json_path": result.validation_rows_json_path,
    "validation_rows_csv_path": result.validation_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "materialization_row_count": result.materialization_row_count,
    "validation_row_count": result.validation_row_count,
    "valid_no_execution_count": result.valid_no_execution_count,
    "invalid_row_count": result.invalid_row_count,
    "duplicate_materialization_id_count": result.duplicate_materialization_id_count,
    "duplicate_candidate_id_count": result.duplicate_candidate_id_count,
    "path_policy_violation_row_count": result.path_policy_violation_row_count,
    "validation_status": result.validation_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
