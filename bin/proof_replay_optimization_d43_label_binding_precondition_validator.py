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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d43_label_binding_precondition_validator_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/result_pack_ingestion_schema.py",
    "app/mme_scalpx/replay_optimization/label_binding_precondition_validator.py",
    "etc/replay_optimization/ingestion/post_result_pack_ingestion_schema_contract.json",
    "etc/replay_optimization/labeling/label_binding_precondition_validator_contract.json",
    "bin/proof_replay_optimization_d42_post_result_pack_ingestion_schema.py",
    "bin/proof_replay_optimization_d43_label_binding_precondition_validator.py",
    "run/proofs/proof_lane_d_d42_post_result_pack_ingestion_schema_latest.json",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/result_pack_ingestion_schema.py",
    "app/mme_scalpx/replay_optimization/label_binding_precondition_validator.py",
    "bin/proof_replay_optimization_d43_label_binding_precondition_validator.py",
]

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "dataclasses",
    "json",
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
    raise SystemExit(f"missing expected D43 dependency/target files: {missing}")

d42_path = ROOT / "run/proofs/proof_lane_d_d42_post_result_pack_ingestion_schema_latest.json"
d42 = load_json(d42_path)

if d42.get("verdict") != "PASS":
    raise SystemExit("D42 proof is not PASS")
if d42.get("batch") != "LANE-D1-D42":
    raise SystemExit(f"unexpected D42 batch: {d42.get('batch')}")
if d42.get("full_universe_count") != 810:
    raise SystemExit(f"D42 full_universe_count expected 810, got {d42.get('full_universe_count')}")
if d42.get("full_universe_preserved") is not True:
    raise SystemExit("D42 did not preserve full universe")
if d42.get("subset_count") != 5:
    raise SystemExit(f"D42 subset_count expected 5, got {d42.get('subset_count')}")
if d42.get("schema_status") != "POST_RESULT_PACK_INGESTION_SCHEMA_READY_NO_EXECUTION":
    raise SystemExit(f"D42 schema_status unexpected: {d42.get('schema_status')}")
if d42.get("next_recommended_batch") != "LANE-D1-D43_LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION":
    raise SystemExit(f"D42 next batch does not point to D43: {d42.get('next_recommended_batch')}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/label_binding_precondition_validator.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/label_binding_precondition_validator.py",
    "etc/replay_optimization/labeling/label_binding_precondition_validator_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(ROOT / "etc/replay_optimization/labeling/label_binding_precondition_validator_contract.json")
safety = config["safety"]

if config.get("expected_full_universe_count") != 810:
    raise SystemExit("D43 contract expected_full_universe_count must be 810")
if config.get("expected_subset_count") != 5:
    raise SystemExit("D43 contract expected_subset_count must be 5")
if config.get("required_verified_result_pack_count") != 5:
    raise SystemExit("D43 contract required_verified_result_pack_count must be 5")
if config.get("current_verified_result_pack_count") != 0:
    raise SystemExit("D43 contract current_verified_result_pack_count must be 0")
if config.get("label_binding_precondition_status") != "BLOCKED_UNTIL_VERIFIED_RESULT_PACKS_EXIST":
    raise SystemExit("D43 contract must keep label binding blocked")
if safety.get("validator_only") is not True:
    raise SystemExit("D43 config must be validator_only=true")
if safety.get("full_universe_preserved") is not True:
    raise SystemExit("D43 config must preserve full universe")
if safety.get("subset_preserved") is not True:
    raise SystemExit("D43 config must preserve subset")
if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D43 config must require Lane C/E execution")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "result_pack_exists_checked",
    "result_pack_verified",
    "result_pack_ingestion_performed",
    "candidate_result_verified",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_allowed",
    "real_pnl_calculation_performed",
    "leaderboard_allowed",
    "leaderboard_created",
    "model_training_allowed",
    "model_training_performed",
    "model_prediction_allowed",
    "model_prediction_performed",
    "broker_calls_allowed",
    "live_redis_writes_allowed",
    "runtime_services_allowed",
    "paper_live_enablement_allowed",
    "production_profit_claim_allowed",
]:
    if safety.get(key) is not False:
        raise SystemExit(f"D43 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.label_binding_precondition_validator")

validation_id = f"D43_LABEL_BINDING_PRECONDITION_VALIDATOR_{TS}"
result = mod.validate_label_binding_preconditions(
    validation_id=validation_id,
    artifact_root=ARTIFACT_ROOT,
    root=ROOT,
)

for path_value in [
    result.validator_schema_path,
    result.validation_summary_path,
    result.candidate_rows_path,
    result.blocker_report_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D43 output missing: {path_value}")

schema = load_json(Path(result.validator_schema_path))
summary = load_json(Path(result.validation_summary_path))
rows_payload = load_json(Path(result.candidate_rows_path))
blocker_report = load_json(Path(result.blocker_report_path))
verdict = load_json(Path(result.optimizer_verdict_path))

rows = rows_payload.get("rows")
if verdict.get("verdict") != "PASS":
    raise SystemExit(f"D43 optimizer verdict not PASS: {verdict}")
if result.full_universe_count != 810:
    raise SystemExit(f"D43 full_universe_count expected 810, got {result.full_universe_count}")
if result.subset_count != 5:
    raise SystemExit(f"D43 subset_count expected 5, got {result.subset_count}")
if result.required_verified_result_pack_count != 5:
    raise SystemExit("D43 required verified result-pack count must be 5")
if result.current_verified_result_pack_count != 0:
    raise SystemExit("D43 current verified result-pack count must be 0")
if result.label_binding_allowed is not False:
    raise SystemExit("D43 must keep label_binding_allowed=false")
if result.validation_status != "LABEL_BINDING_PRECONDITION_VALIDATED_BLOCKED_NO_EXECUTION":
    raise SystemExit(f"D43 validation_status unexpected: {result.validation_status}")

if not isinstance(rows, list) or len(rows) != 5:
    raise SystemExit("D43 candidate rows expected 5 rows")

for row in rows:
    if row.get("blocked") is not True:
        raise SystemExit(f"D43 candidate row must be blocked: {row}")
    if row.get("candidate_row_status") != "LABEL_BINDING_BLOCKED_PENDING_VERIFIED_RESULT_PACK":
        raise SystemExit(f"D43 bad candidate row status: {row}")
    for key in [
        "result_pack_exists_checked",
        "result_pack_verified",
        "candidate_result_verified",
        "result_pack_ingestion_performed",
        "label_binding_allowed",
        "labels_bound",
        "real_pnl_calculation_performed",
        "model_training_performed",
        "model_prediction_performed",
    ]:
        if row.get(key) is not False:
            raise SystemExit(f"D43 row safety failed {key}: {row}")

if summary.get("label_binding_precondition_status") != "BLOCKED_UNTIL_VERIFIED_RESULT_PACKS_EXIST":
    raise SystemExit("D43 summary must keep label binding blocked")
if summary.get("current_verified_result_pack_count") != 0:
    raise SystemExit("D43 summary current verified count must be 0")
if summary.get("candidate_blocked_count") != 5:
    raise SystemExit("D43 summary candidate_blocked_count must be 5")
if summary.get("label_binding_allowed") is not False:
    raise SystemExit("D43 summary label_binding_allowed must be false")
if summary.get("leaderboard_allowed") is not False:
    raise SystemExit("D43 summary leaderboard_allowed must be false")
if summary.get("ml_dataset_allowed") is not False:
    raise SystemExit("D43 summary ml_dataset_allowed must be false")
if blocker_report.get("label_binding_allowed") is not False:
    raise SystemExit("D43 blocker report must keep label_binding_allowed=false")
if blocker_report.get("current_verified_result_pack_count") != 0:
    raise SystemExit("D43 blocker report current verified count must be 0")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "result_pack_exists_checked",
    "result_pack_verified",
    "result_pack_ingestion_performed",
    "candidate_result_verified",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_performed",
    "leaderboard_created",
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
    if summary.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D43 summary safety failed: {key}")

if summary.get("safety", {}).get("validator_only") is not True:
    raise SystemExit("D43 summary must be validator_only")
if summary.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D43 summary must require Lane C/E execution")
if schema.get("validation_status") != "LABEL_BINDING_PRECONDITION_VALIDATED_BLOCKED_NO_EXECUTION":
    raise SystemExit("D43 schema validation status mismatch")

next_required_external_step = "LANE_C_OR_E_EXECUTE_D41_SUBSET_AND_RETURN_VERIFIED_RESULT_PACKS"
next_d1_batch_after_verified_result_packs = "LANE-D1-D44_RESULT_PACK_INTAKE_AUDIT_AFTER_LANE_CE_RESULTS_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items() if path.exists()}

proof = {
    "batch": "LANE-D1-D43",
    "chat_lane": "Lane D1 only",
    "name": "label_binding_precondition_validator_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "validator_schema_path": result.validator_schema_path,
    "validation_summary_path": result.validation_summary_path,
    "candidate_rows_path": result.candidate_rows_path,
    "blocker_report_path": result.blocker_report_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "full_universe_count": result.full_universe_count,
    "full_universe_preserved": True,
    "subset_count": result.subset_count,
    "subset_preserved": True,
    "required_verified_result_pack_count": result.required_verified_result_pack_count,
    "current_verified_result_pack_count": result.current_verified_result_pack_count,
    "candidate_blocked_count": summary.get("candidate_blocked_count"),
    "label_binding_allowed": result.label_binding_allowed,
    "labels_bound": False,
    "validation_status": result.validation_status,
    "label_binding_precondition_status": "BLOCKED_UNTIL_VERIFIED_RESULT_PACKS_EXIST",
    "d42_dependency_observed": {
        "path": d42_path.as_posix(),
        "verdict": d42.get("verdict"),
        "batch": d42.get("batch"),
        "full_universe_count": d42.get("full_universe_count"),
        "full_universe_preserved": d42.get("full_universe_preserved"),
        "subset_count": d42.get("subset_count"),
        "schema_status": d42.get("schema_status"),
        "next_recommended_batch": d42.get("next_recommended_batch")
    },
    "safety": {
        "label_binding_precondition_validator_created": True,
        "label_binding_precondition_validated_blocked": True,
        "validator_only": True,
        "full_universe_preserved": True,
        "subset_preserved": True,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed_in_lane_d": False,
        "result_pack_created": False,
        "result_pack_exists_checked": False,
        "result_pack_verified": False,
        "result_pack_ingestion_performed": False,
        "candidate_result_verified": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "real_pnl_calculation_performed": False,
        "leaderboard_created": False,
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
    "important_limitation": "D43 validates that label binding remains blocked. It does not inspect real result packs, ingest result packs, execute replay, bind labels, calculate PnL, train/predict, create leaderboard outputs, or claim profitability.",
    "next_required_external_step": next_required_external_step,
    "next_d1_batch_after_verified_result_packs": next_d1_batch_after_verified_result_packs
}

proof_path = PROOF_DIR / f"proof_lane_d_d43_label_binding_precondition_validator_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d43_label_binding_precondition_validator_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d1_d43_label_binding_precondition_validator_{TS}.md"
milestone_path.write_text(
    "# LANE D1 D43 — Label Binding Precondition Validator / No Execution\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — Label binding precondition validator confirms labels remain blocked until verified Lane C/E result packs exist.\n\n"
    "## Evidence Chain\n\n"
    "- D42 post-result-pack ingestion schema PASS observed.\n"
    "- 810-candidate full universe preserved.\n"
    "- 5-candidate first subset preserved.\n"
    "- Current verified result-pack count remains 0.\n"
    "- Required verified result-pack count is 5.\n\n"
    "## Output\n\n"
    f"- Artifact root: `{ARTIFACT_ROOT.as_posix()}`\n"
    f"- Validation summary: `{result.validation_summary_path}`\n"
    f"- Candidate precondition rows: `{result.candidate_rows_path}`\n"
    f"- Blocker report: `{result.blocker_report_path}`\n\n"
    "## Safety\n\n"
    "- Validator only: true\n"
    "- Replay execution performed: false\n"
    "- Result pack created/checked/verified/ingested: false\n"
    "- Candidate result verified: false\n"
    "- Label binding allowed: false\n"
    "- Labels bound: false\n"
    "- PnL calculation performed: false\n"
    "- Leaderboard created: false\n"
    "- ML training/prediction performed: false\n"
    "- Broker calls / live Redis / paper-live enablement: false\n\n"
    "## Next Required External Step\n\n"
    f"{next_required_external_step}\n\n"
    "## Next D1 Batch After Verified Result Packs Exist\n\n"
    f"{next_d1_batch_after_verified_result_packs}\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "validator_schema_path": result.validator_schema_path,
    "validation_summary_path": result.validation_summary_path,
    "candidate_rows_path": result.candidate_rows_path,
    "blocker_report_path": result.blocker_report_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "full_universe_count": result.full_universe_count,
    "subset_count": result.subset_count,
    "required_verified_result_pack_count": result.required_verified_result_pack_count,
    "current_verified_result_pack_count": result.current_verified_result_pack_count,
    "label_binding_allowed": result.label_binding_allowed,
    "validation_status": result.validation_status,
    "label_binding_precondition_status": "BLOCKED_UNTIL_VERIFIED_RESULT_PACKS_EXIST",
    "next_required_external_step": next_required_external_step,
    "next_d1_batch_after_verified_result_packs": next_d1_batch_after_verified_result_packs,
}, indent=2, sort_keys=True))
