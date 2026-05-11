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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d40_execution_package_requirement_validator_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement_validator.py",
    "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_contract.json",
    "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_validator_contract.json",
    "bin/proof_replay_optimization_d39_execution_package_requirement.py",
    "bin/proof_replay_optimization_d40_execution_package_requirement_validator.py",
    "run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement_validator.py",
    "bin/proof_replay_optimization_d40_execution_package_requirement_validator.py",
]

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "json",
    "dataclasses",
    "pathlib",
    "typing",
}

BANNED_IMPORT_ROOTS = {
    "kiteconnect",
    "redis",
    "requests",
    "websocket",
    "subprocess",
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


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D40 dependency/target files: {missing}")

d39_proof_path = ROOT / "run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json"
d39 = load_json(d39_proof_path)

if d39.get("verdict") != "PASS":
    raise SystemExit("D39 proof is not PASS")
if d39.get("batch") != "LANE-D1-D39":
    raise SystemExit(f"unexpected D39 batch: {d39.get('batch')}")
if d39.get("candidate_count") != 810:
    raise SystemExit(f"D39 candidate_count expected 810, got {d39.get('candidate_count')}")
if d39.get("package_requirement_row_count") != 810:
    raise SystemExit(f"D39 package_requirement_row_count expected 810, got {d39.get('package_requirement_row_count')}")
if d39.get("package_requirement_ready_count") != 810:
    raise SystemExit(f"D39 package_requirement_ready_count expected 810, got {d39.get('package_requirement_ready_count')}")
if d39.get("next_recommended_batch") != "LANE-D1-D40_EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_NO_EXECUTION":
    raise SystemExit(f"D39 next batch does not point to D40: {d39.get('next_recommended_batch')}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/execution_package_requirement_validator.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/execution_package_requirement_validator.py",
    "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_validator_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(ROOT / "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_validator_contract.json")
safety = config["safety"]

if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D40 config must require Lane C/E execution")
for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_allowed",
    "real_pnl_calculation_performed",
    "model_training_allowed",
    "model_training_performed",
    "model_prediction_allowed",
    "model_prediction_performed",
    "broker_calls_allowed",
    "live_redis_writes_allowed",
    "runtime_services_allowed",
    "paper_live_enablement_allowed",
]:
    if safety.get(key) is not False:
        raise SystemExit(f"D40 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.execution_package_requirement_validator")

validation_id = f"D40_EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_PROBE_{TS}"
result = mod.validate_execution_package_requirements(
    validation_id=validation_id,
    d39_proof_path=d39_proof_path,
    artifact_root=ARTIFACT_ROOT,
    root=ROOT,
)

for path_value in [
    result.validation_schema_path,
    result.validation_summary_path,
    result.validation_rows_path,
    result.validation_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D40 output missing: {path_value}")

validation_summary = load_json(Path(result.validation_summary_path))
validation_rows_payload = load_json(Path(result.validation_rows_path))
validation_verdict = load_json(Path(result.validation_verdict_path))
validation_rows = validation_rows_payload.get("rows")

if validation_verdict.get("verdict") != "PASS":
    raise SystemExit(f"D40 validation verdict not PASS: {validation_verdict}")
if validation_summary.get("validation_status") != "EXECUTION_PACKAGE_REQUIREMENT_VALIDATED_NO_EXECUTION":
    raise SystemExit(f"D40 unexpected validation_status: {validation_summary.get('validation_status')}")
if validation_summary.get("candidate_count") != 810:
    raise SystemExit(f"D40 summary candidate_count expected 810, got {validation_summary.get('candidate_count')}")
if validation_summary.get("validated_row_count") != 810:
    raise SystemExit(f"D40 summary validated_row_count expected 810, got {validation_summary.get('validated_row_count')}")
if validation_summary.get("failed_row_count") != 0:
    raise SystemExit(f"D40 summary failed_row_count expected 0, got {validation_summary.get('failed_row_count')}")
if not isinstance(validation_rows, list) or len(validation_rows) != 810:
    raise SystemExit("D40 validation rows expected list of 810 rows")

for row in validation_rows:
    if row.get("validation_pass") is not True:
        raise SystemExit(f"D40 validation row did not pass: {row}")
    if row.get("validation_status") != "EXECUTION_PACKAGE_REQUIREMENT_VALIDATED_NO_EXECUTION":
        raise SystemExit(f"D40 bad validation row status: {row}")
    if row.get("lane_c_or_e_execution_required") is not True:
        raise SystemExit(f"D40 row must require Lane C/E execution: {row}")
    for key in [
        "lane_d_execution_allowed",
        "replay_execution_performed",
        "result_pack_created",
        "label_binding_allowed",
        "labels_bound",
        "real_pnl_calculation_performed",
        "model_training_performed",
        "model_prediction_performed",
    ]:
        if row.get(key) is not False:
            raise SystemExit(f"D40 row safety failed {key}: {row}")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "model_prediction_performed",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
    "runtime_services_started",
    "strategy_doctrine_changed",
    "replay_engine_changed",
    "production_profit_claim_allowed",
]:
    if validation_summary.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D40 summary safety failed: {key}")
if validation_summary.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D40 summary must require Lane C/E execution")

next_batch = "LANE-D1-D41_CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items() if path.exists()}

proof = {
    "batch": "LANE-D1-D40",
    "chat_lane": "Lane D1 only",
    "name": "execution_package_requirement_validator_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_NO_EXECUTION",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "source_d39_proof_path": d39_proof_path.as_posix(),
    "source_d39_artifact_root": result.source_d39_artifact_root,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "validation_schema_path": result.validation_schema_path,
    "validation_summary_path": result.validation_summary_path,
    "validation_rows_path": result.validation_rows_path,
    "validation_verdict_path": result.validation_verdict_path,
    "candidate_count": result.candidate_count,
    "validated_row_count": result.validated_row_count,
    "failed_row_count": result.failed_row_count,
    "validation_status": result.validation_status,
    "d39_dependency_observed": {
        "path": d39_proof_path.as_posix(),
        "verdict": d39.get("verdict"),
        "batch": d39.get("batch"),
        "candidate_count": d39.get("candidate_count"),
        "package_requirement_row_count": d39.get("package_requirement_row_count"),
        "package_requirement_ready_count": d39.get("package_requirement_ready_count"),
        "next_recommended_batch": d39.get("next_recommended_batch")
    },
    "safety": {
        "validator_built": True,
        "validator_executed_against_d39_artifacts": True,
        "full_universe_preserved": True,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed_in_lane_d": False,
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
    "important_limitation": "D40 validates D39 requirement rows only. It does not execute replay, create real result packs, bind labels, calculate PnL, train/predict, or approve optimization.",
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d40_execution_package_requirement_validator_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d40_execution_package_requirement_validator_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d1_d40_execution_package_requirement_validator_{TS}.md"
milestone_path.write_text(
    "# LANE D1 D40 — Execution Package Requirement Validator / No Execution\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D39 execution package requirement rows validated with no execution.\n\n"
    "## Evidence Chain\n\n"
    "- D39 proof PASS observed.\n"
    "- 810 package requirement rows observed.\n"
    "- 810 package requirement rows validated.\n"
    "- 0 validation failures.\n\n"
    "## Output\n\n"
    f"- Artifact root: `{ARTIFACT_ROOT.as_posix()}`\n"
    f"- Validation summary: `{result.validation_summary_path}`\n"
    f"- Validation rows: `{result.validation_rows_path}`\n"
    f"- Validation verdict: `{result.validation_verdict_path}`\n\n"
    "## Safety\n\n"
    "- Replay execution performed: false\n"
    "- Result pack created: false\n"
    "- Label binding allowed: false\n"
    "- PnL calculation performed: false\n"
    "- ML training/prediction performed: false\n"
    "- Broker calls / live Redis / paper-live enablement: false\n\n"
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
    "validation_schema_path": result.validation_schema_path,
    "validation_summary_path": result.validation_summary_path,
    "validation_rows_path": result.validation_rows_path,
    "validation_verdict_path": result.validation_verdict_path,
    "candidate_count": result.candidate_count,
    "validated_row_count": result.validated_row_count,
    "failed_row_count": result.failed_row_count,
    "validation_status": result.validation_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
