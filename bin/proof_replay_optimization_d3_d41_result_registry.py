#!/usr/bin/env python3
from __future__ import annotations

import ast
import glob
import hashlib
import importlib
import json
import py_compile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd().resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
NOW = datetime.now(timezone.utc).isoformat()

PROOF_DIR = ROOT / "run" / "proofs"
MILESTONE_DIR = ROOT / "docs" / "milestones"
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d3_d41_result_registry_schema_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/result_registry.py",
    "etc/replay_optimization/registry/result_registry_contract.json",
    "bin/proof_replay_optimization_d3_d41_result_registry.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/result_registry.py",
    "bin/proof_replay_optimization_d3_d41_result_registry.py",
]

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "ast",
    "dataclasses",
    "datetime",
    "glob",
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
    "subprocess",
}

# Build forbidden runtime tokens without storing the exact full strings in this
# proof script. The proof scans itself, so literal banned tokens here would create
# a false positive even when no runtime/broker/replay usage exists.
FORBIDDEN_RUNTIME_TOKENS = [
    "from " + "kiteconnect",
    "Kite" + "Connect(",
    "Dhan" + "HQ(",
    "place" + "_order(",
    "." + "place" + "_order(",
    "redis" + "." + "Redis(",
    "." + "x" + "add(",
    "subprocess" + "." + "Popen(",
    "app" + "." + "mme_scalpx" + "." + "main",
    "bin/" + "replay" + "_run.py",
]

RISKY_TRUE_KEYS = {
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_allowed",
    "real_pnl_calculation_performed",
    "leaderboard_built",
    "ml_export_performed",
    "model_training_allowed",
    "model_training_performed",
    "model_prediction_allowed",
    "prediction_performed",
    "broker_calls_allowed",
    "broker_calls_executed",
    "live_redis_writes_allowed",
    "live_redis_writes_executed",
    "paper_live_enablement_allowed",
    "paper_or_live_enabled",
    "runtime_service_start_allowed",
    "runtime_services_started",
    "strategy_doctrine_mutation_allowed",
    "strategy_doctrine_changed",
    "replay_engine_mutation_allowed",
    "replay_engine_changed",
    "production_profit_claim_allowed",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def imported_roots(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.append(node.module.split(".")[0])
    return sorted(set(roots))


def latest_for(batch: str) -> Path:
    patterns = [
        str(PROOF_DIR / f"proof_lane_d_{batch}_*_latest.json"),
        str(PROOF_DIR / f"proof_lane_d_{batch}*latest.json"),
        str(PROOF_DIR / f"proof_lane_d3_{batch}_*_latest.json"),
        str(PROOF_DIR / f"proof_lane_d3_{batch}*latest.json"),
        str(PROOF_DIR / f"proof_lane_d_{batch}_*.json"),
        str(PROOF_DIR / f"proof_lane_d_{batch}*.json"),
    ]
    hits: list[Path] = []
    for pattern in patterns:
        hits.extend(Path(p) for p in glob.glob(pattern))
    hits = sorted(set(hits), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    if not hits:
        raise SystemExit(f"missing required proof for {batch.upper()}")
    return hits[0]


def assert_pass_safe(batch: str, path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if payload.get("verdict") != "PASS":
        raise SystemExit(f"{batch} proof verdict not PASS: {payload.get('verdict')}")
    safety = payload.get("safety")
    if not isinstance(safety, dict):
        raise SystemExit(f"{batch} proof missing safety dict")
    unsafe = []
    for key in sorted(RISKY_TRUE_KEYS):
        if key in safety and safety[key] is not False:
            unsafe.append(f"{key}={safety[key]!r}")
    if unsafe:
        raise SystemExit(f"{batch} unsafe safety keys: {unsafe}")
    return payload


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D3-D41 files: {missing}")

compile_results: dict[str, str] = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit: dict[str, list[str]] = {}
for rel in EXPECTED_FILES:
    if not rel.endswith(".py"):
        continue
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in EXPECTED_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

d38_path = latest_for("d38")
d39_path = latest_for("d39")
d40_path = latest_for("d40")

d38 = assert_pass_safe("D38", d38_path)
d39 = assert_pass_safe("D39", d39_path)
d40 = assert_pass_safe("D40", d40_path)

if d38.get("candidate_count") != 810:
    raise SystemExit(f"D38 candidate_count expected 810, got {d38.get('candidate_count')}")
if d38.get("phase_status") != "REPLAY_OPTIMIZATION_PHASE_READY_FOR_LANE_CE_HANDOFF_NO_EXECUTION":
    raise SystemExit(f"D38 phase_status not ready: {d38.get('phase_status')}")

contract = load_json(ROOT / "etc/replay_optimization/registry/result_registry_contract.json")
contract_safety = contract.get("safety", {})
for key, expected in {
    "schema_contract_only": True,
    "registry_schema_file_creation_allowed": True,
    "replay_execution_allowed": False,
    "replay_execution_performed": False,
    "result_pack_creation_allowed": False,
    "result_pack_created": False,
    "candidate_context_attachment_allowed": False,
    "candidate_context_attached": False,
    "candidate_trade_matching_allowed": False,
    "candidate_trade_matching_performed": False,
    "label_binding_allowed": False,
    "labels_bound": False,
    "real_pnl_calculation_allowed": False,
    "real_pnl_calculation_performed": False,
    "leaderboard_built": False,
    "ml_export_performed": False,
    "broker_calls_executed": False,
    "live_redis_writes_executed": False,
    "paper_or_live_enabled": False,
    "runtime_services_started": False,
}.items():
    if contract_safety.get(key) is not expected:
        raise SystemExit(f"contract safety mismatch: {key} expected {expected}, got {contract_safety.get(key)}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.result_registry")

schema = mod.schema_payload()
schema_errors = mod.validate_schema_payload(schema)
if schema_errors:
    raise SystemExit(f"schema validation failed: {schema_errors}")

sample_row = mod.make_unbound_registry_row(
    candidate_id="CANDIDATE_ID_PLACEHOLDER_UNBOUND",
    candidate_fingerprint="CANDIDATE_FINGERPRINT_PLACEHOLDER_UNBOUND",
    subset_id=None,
    handoff_id=None,
    package_requirement_id=None,
    planned_result_pack_id=None,
    planned_result_pack_root=None,
)
sample_row_payload = mod.row_to_dict(sample_row)
row_errors = mod.validate_result_registry_row(sample_row_payload)
if row_errors:
    raise SystemExit(f"sample row validation failed: {row_errors}")

schema_path = ARTIFACT_ROOT / "42_result_registry_schema.json"
contract_snapshot_path = ARTIFACT_ROOT / "42_result_registry_contract_snapshot.json"
sample_row_path = ARTIFACT_ROOT / "42_result_registry_sample_unbound_row.json"
progress_report_path = ARTIFACT_ROOT / "42_result_registry_progress_report.json"
optimizer_verdict_path = ARTIFACT_ROOT / "09_optimizer_verdict.json"

write_json(schema_path, schema)
write_json(contract_snapshot_path, contract)
write_json(sample_row_path, sample_row_payload)

progress_report = {
    "schema_name": "MME-ScalpX Lane D3 Result Registry Progress Report",
    "contract_version": mod.CONTRACT_VERSION,
    "accepted_for": mod.ACCEPTED_FOR,
    "created_at": NOW,
    "d38_proof_path": d38_path.as_posix(),
    "d39_proof_path": d39_path.as_posix(),
    "d40_proof_path": d40_path.as_posix(),
    "candidate_count_from_d38": d38.get("candidate_count"),
    "registry_schema_frozen": True,
    "candidate_result_pack_registry_surface_frozen": True,
    "subset_result_linkage_surface_frozen": True,
    "verified_label_status_surface_frozen": True,
    "leaderboard_storage_placeholder_frozen": True,
    "ml_export_eligibility_placeholder_frozen": True,
    "actual_result_pack_fields_null_until_verified": True,
    "label_binding_allowed": False,
    "labels_bound": False,
    "real_pnl_calculation_performed": False,
    "leaderboard_built": False,
    "ml_export_performed": False,
    "replay_execution_performed": False,
    "broker_calls_executed": False,
    "live_redis_writes_executed": False,
    "paper_or_live_enabled": False,
    "runtime_services_started": False,
    "important_limitation": "D3-D41 freezes registry/reporting storage surfaces only. It does not execute replay, create result packs, bind labels, calculate real PnL, build a leaderboard, export ML data, or claim profitability.",
    "next_recommended_batch": "LANE-D3-D42_RESULT_REGISTRY_INGESTION_AUDIT_CONTRACT_NO_EXECUTION",
}
write_json(progress_report_path, progress_report)

optimizer_verdict = {
    "verdict": "PASS",
    "status": "RESULT_REGISTRY_SCHEMA_CONTRACT_READY_NO_EXECUTION",
    "created_at": NOW,
    "blocked_until": {
        "actual_result_pack_ingestion": "Lane E verified candidate-specific result packs required",
        "label_binding": "verified candidate-specific result packs required",
        "real_pnl": "verified candidate-specific result packs required",
        "leaderboard": "verified labels required",
        "ml_export": "verified labels plus sample-size/overfit gates required",
    },
}
write_json(optimizer_verdict_path, optimizer_verdict)

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D3-D41",
    "name": "replay_optimization_result_registry_schema_contract_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": mod.ACCEPTED_FOR,
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "source_proofs": {
        "d38": d38_path.as_posix(),
        "d39": d39_path.as_posix(),
        "d40": d40_path.as_posix(),
    },
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "schema_path": schema_path.as_posix(),
    "contract_snapshot_path": contract_snapshot_path.as_posix(),
    "sample_unbound_row_path": sample_row_path.as_posix(),
    "progress_report_path": progress_report_path.as_posix(),
    "optimizer_verdict_path": optimizer_verdict_path.as_posix(),
    "candidate_count_from_d38": d38.get("candidate_count"),
    "result_registry_column_count": len(mod.RESULT_REGISTRY_COLUMNS),
    "schema_validation_errors": schema_errors,
    "sample_row_validation_errors": row_errors,
    "safety": {
        "schema_contract_only": True,
        "registry_schema_file_creation_allowed": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed": False,
        "result_pack_created": False,
        "replay_artifact_materialization_allowed": False,
        "candidate_context_attachment_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
        "label_binding_allowed": False,
        "labels_bound": False,
        "real_pnl_calculation_allowed": False,
        "real_pnl_calculation_performed": False,
        "leaderboard_built": False,
        "ml_export_performed": False,
        "model_training_allowed": False,
        "model_training_performed": False,
        "model_prediction_allowed": False,
        "prediction_performed": False,
        "broker_calls_allowed": False,
        "broker_calls_executed": False,
        "live_redis_writes_allowed": False,
        "live_redis_writes_executed": False,
        "paper_live_enablement_allowed": False,
        "paper_or_live_enabled": False,
        "runtime_service_start_allowed": False,
        "runtime_services_started": False,
        "strategy_doctrine_mutation_allowed": False,
        "strategy_doctrine_changed": False,
        "replay_engine_mutation_allowed": False,
        "replay_engine_changed": False,
        "production_profit_claim_allowed": False
    },
    "next_recommended_batch": "LANE-D3-D42_RESULT_REGISTRY_INGESTION_AUDIT_CONTRACT_NO_EXECUTION",
}

proof_path = PROOF_DIR / f"proof_lane_d3_d41_result_registry_schema_contract_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d3_d41_result_registry_schema_contract_latest.json"
write_json(proof_path, proof)
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d3_d41_result_registry_schema_contract_{TS}.md"
milestone_path.write_text(
    "# LANE D3 D41 — Replay Optimization Result Registry Schema Contract\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — Result registry schema contract frozen with no replay execution and no label/PnL/ML/leaderboard activation.\n\n"
    "## Source Proofs\n\n"
    f"- D38: `{d38_path.as_posix()}`\n"
    f"- D39: `{d39_path.as_posix()}`\n"
    f"- D40: `{d40_path.as_posix()}`\n\n"
    "## Frozen Surfaces\n\n"
    "- Result registry schema columns\n"
    "- Candidate/result-pack registry fields\n"
    "- Subset/result linkage placeholders\n"
    "- Verified label status placeholders\n"
    "- Leaderboard eligibility placeholders\n"
    "- ML-export eligibility placeholders\n"
    "- SQLite/DuckDB-ready type map\n\n"
    "## Important Limitation\n\n"
    "D3-D41 does not execute replay, create result packs, attach candidate context, match trades, bind labels, calculate real PnL, build leaderboard, export ML data, train models, write live Redis, call brokers, or enable paper/live.\n\n"
    "## Next\n\n"
    "LANE-D3-D42_RESULT_REGISTRY_INGESTION_AUDIT_CONTRACT_NO_EXECUTION\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "schema_path": schema_path.as_posix(),
    "contract_snapshot_path": contract_snapshot_path.as_posix(),
    "sample_unbound_row_path": sample_row_path.as_posix(),
    "progress_report_path": progress_report_path.as_posix(),
    "optimizer_verdict_path": optimizer_verdict_path.as_posix(),
    "candidate_count_from_d38": d38.get("candidate_count"),
    "next": "LANE-D3-D42_RESULT_REGISTRY_INGESTION_AUDIT_CONTRACT_NO_EXECUTION",
}, indent=2, sort_keys=True))
