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
from typing import Any

ROOT = Path.cwd().resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
NOW = datetime.now(timezone.utc).isoformat()

PROOF_DIR = ROOT / "run" / "proofs"
MILESTONE_DIR = ROOT / "docs" / "milestones"
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d3_d42_result_registry_ingestion_audit_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

D41_LATEST = PROOF_DIR / "proof_lane_d3_d41_result_registry_schema_contract_latest.json"

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/result_registry.py",
    "app/mme_scalpx/replay_optimization/analytics_registry.py",
    "etc/replay_optimization/registry/result_registry_contract.json",
    "etc/replay_optimization/registry/result_registry_ingestion_audit_contract.json",
    "bin/proof_replay_optimization_d3_d42_result_registry_ingestion_audit.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/result_registry.py",
    "app/mme_scalpx/replay_optimization/analytics_registry.py",
    "bin/proof_replay_optimization_d3_d42_result_registry_ingestion_audit.py",
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
    "result_registry",
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

# Build forbidden runtime tokens without storing full target strings in this proof.
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


def assert_safe_proof(name: str, payload: dict[str, Any]) -> None:
    if payload.get("verdict") != "PASS":
        raise SystemExit(f"{name} verdict not PASS: {payload.get('verdict')}")
    safety = payload.get("safety")
    if not isinstance(safety, dict):
        raise SystemExit(f"{name} safety missing")
    unsafe = []
    for key in sorted(RISKY_TRUE_KEYS):
        if key in safety and safety[key] is not False:
            unsafe.append(f"{key}={safety[key]!r}")
    if unsafe:
        raise SystemExit(f"{name} unsafe safety keys: {unsafe}")


if not D41_LATEST.exists():
    raise SystemExit(f"missing D41 latest proof: {D41_LATEST}")

d41 = load_json(D41_LATEST)
assert_safe_proof("D41", d41)

if d41.get("accepted_for") != "RESULT_REGISTRY_SCHEMA_CONTRACT_NO_EXECUTION":
    raise SystemExit(f"D41 accepted_for mismatch: {d41.get('accepted_for')}")
if d41.get("schema_validation_errors") != []:
    raise SystemExit(f"D41 schema validation errors present: {d41.get('schema_validation_errors')}")
if d41.get("sample_row_validation_errors") != []:
    raise SystemExit(f"D41 sample row validation errors present: {d41.get('sample_row_validation_errors')}")
if d41.get("candidate_count_from_d38") != 810:
    raise SystemExit(f"D41 candidate_count_from_d38 expected 810, got {d41.get('candidate_count_from_d38')}")

files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D3-D42 files: {missing}")

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

result_registry = importlib.import_module("app.mme_scalpx.replay_optimization.result_registry")
analytics_registry = importlib.import_module("app.mme_scalpx.replay_optimization.analytics_registry")

registry_schema = result_registry.schema_payload()
registry_schema_errors = result_registry.validate_schema_payload(registry_schema)
if registry_schema_errors:
    raise SystemExit(f"result registry schema errors: {registry_schema_errors}")

sample_row = result_registry.make_unbound_registry_row(
    candidate_id="CANDIDATE_ID_PLACEHOLDER_UNBOUND",
    candidate_fingerprint="CANDIDATE_FINGERPRINT_PLACEHOLDER_UNBOUND",
    subset_id=None,
    handoff_id=None,
    package_requirement_id=None,
    planned_result_pack_id=None,
    planned_result_pack_root=None,
)
sample_row_payload = result_registry.row_to_dict(sample_row)
sample_row_errors = result_registry.validate_result_registry_row(sample_row_payload)
if sample_row_errors:
    raise SystemExit(f"sample result registry row errors: {sample_row_errors}")

ingestion_schema = analytics_registry.ingestion_audit_schema_payload()
ingestion_schema_errors = analytics_registry.validate_ingestion_audit_schema_payload(ingestion_schema)
if ingestion_schema_errors:
    raise SystemExit(f"ingestion audit schema errors: {ingestion_schema_errors}")

audit = analytics_registry.make_ingestion_audit_for_unverified_registry_row(sample_row_payload)
audit_payload = analytics_registry.audit_to_dict(audit)
audit_errors = analytics_registry.validate_ingestion_audit(audit_payload)
if audit_errors:
    raise SystemExit(f"ingestion audit sample errors: {audit_errors}")

if audit_payload["ingestion_allowed"] is not False:
    raise SystemExit("ingestion_allowed must remain false")
if audit_payload["verified_result_pack_present"] is not False:
    raise SystemExit("verified_result_pack_present must remain false")
if audit_payload["label_binding_allowed"] is not False:
    raise SystemExit("label_binding_allowed must remain false")
if audit_payload["real_pnl_calculation_allowed"] is not False:
    raise SystemExit("real_pnl_calculation_allowed must remain false")
if audit_payload["leaderboard_allowed"] is not False:
    raise SystemExit("leaderboard_allowed must remain false")
if audit_payload["ml_export_allowed"] is not False:
    raise SystemExit("ml_export_allowed must remain false")

contract = load_json(ROOT / "etc/replay_optimization/registry/result_registry_ingestion_audit_contract.json")
contract_safety = contract.get("safety", {})
for key, expected in {
    "schema_contract_only": True,
    "ingestion_audit_contract_only": True,
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

schema_path = ARTIFACT_ROOT / "43_result_registry_ingestion_audit_schema.json"
contract_snapshot_path = ARTIFACT_ROOT / "43_result_registry_ingestion_audit_contract_snapshot.json"
sample_audit_path = ARTIFACT_ROOT / "43_unverified_ingestion_audit_sample.json"
progress_report_path = ARTIFACT_ROOT / "43_result_registry_ingestion_audit_progress_report.json"
optimizer_verdict_path = ARTIFACT_ROOT / "10_optimizer_verdict.json"

write_json(schema_path, ingestion_schema)
write_json(contract_snapshot_path, contract)
write_json(sample_audit_path, audit_payload)

progress_report = {
    "schema_name": "MME-ScalpX Lane D3 Result Registry Ingestion Audit Progress Report",
    "contract_version": analytics_registry.INGESTION_AUDIT_CONTRACT_VERSION,
    "accepted_for": analytics_registry.ACCEPTED_FOR,
    "created_at": NOW,
    "d41_proof_path": D41_LATEST.as_posix(),
    "result_registry_contract_version": result_registry.CONTRACT_VERSION,
    "candidate_count_from_d38": d41.get("candidate_count_from_d38"),
    "ingestion_audit_schema_frozen": True,
    "future_verified_result_pack_audit_surface_frozen": True,
    "label_binding_gate_surface_frozen_blocked": True,
    "real_pnl_gate_surface_frozen_blocked": True,
    "leaderboard_gate_surface_frozen_blocked": True,
    "ml_export_gate_surface_frozen_blocked": True,
    "ingestion_allowed": False,
    "verified_result_pack_present": False,
    "label_binding_allowed": False,
    "real_pnl_calculation_allowed": False,
    "leaderboard_built": False,
    "ml_export_performed": False,
    "replay_execution_performed": False,
    "broker_calls_executed": False,
    "live_redis_writes_executed": False,
    "paper_or_live_enabled": False,
    "runtime_services_started": False,
    "important_limitation": "D3-D42 freezes ingestion-audit storage surfaces only. It does not ingest real result packs, execute replay, bind labels, calculate real PnL, build leaderboard, export ML data, or claim profitability.",
    "next_recommended_batch": "LANE-D3-D43_LEADERBOARD_AND_ML_ELIGIBILITY_STORAGE_PLACEHOLDER_CONTRACT_NO_EXECUTION",
}
write_json(progress_report_path, progress_report)

optimizer_verdict = {
    "verdict": "PASS",
    "status": "RESULT_REGISTRY_INGESTION_AUDIT_CONTRACT_READY_NO_EXECUTION",
    "created_at": NOW,
    "blocked_until": {
        "actual_result_pack_ingestion": "Lane E verified candidate-specific result packs required",
        "label_binding": "verified candidate-specific result pack integrity PASS required",
        "real_pnl": "verified candidate-specific result pack integrity PASS required",
        "leaderboard": "verified labels required",
        "ml_export": "verified labels plus sample-size/overfit gates required",
    },
}
write_json(optimizer_verdict_path, optimizer_verdict)

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D3-D42",
    "name": "result_registry_ingestion_audit_contract_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": analytics_registry.ACCEPTED_FOR,
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "source_proofs": {
        "d41": D41_LATEST.as_posix(),
        "d38": d41.get("source_proofs", {}).get("d38"),
        "d39": d41.get("source_proofs", {}).get("d39"),
        "d40": d41.get("source_proofs", {}).get("d40"),
    },
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "schema_path": schema_path.as_posix(),
    "contract_snapshot_path": contract_snapshot_path.as_posix(),
    "sample_audit_path": sample_audit_path.as_posix(),
    "progress_report_path": progress_report_path.as_posix(),
    "optimizer_verdict_path": optimizer_verdict_path.as_posix(),
    "candidate_count_from_d38": d41.get("candidate_count_from_d38"),
    "ingestion_audit_column_count": len(analytics_registry.INGESTION_AUDIT_COLUMNS),
    "registry_schema_validation_errors": registry_schema_errors,
    "sample_registry_row_validation_errors": sample_row_errors,
    "ingestion_schema_validation_errors": ingestion_schema_errors,
    "sample_ingestion_audit_validation_errors": audit_errors,
    "safety": {
        "schema_contract_only": True,
        "ingestion_audit_contract_only": True,
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
    "next_recommended_batch": "LANE-D3-D43_LEADERBOARD_AND_ML_ELIGIBILITY_STORAGE_PLACEHOLDER_CONTRACT_NO_EXECUTION",
}

proof_path = PROOF_DIR / f"proof_lane_d3_d42_result_registry_ingestion_audit_contract_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d3_d42_result_registry_ingestion_audit_contract_latest.json"
write_json(proof_path, proof)
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d3_d42_result_registry_ingestion_audit_contract_{TS}.md"
milestone_path.write_text(
    "# LANE D3 D42 — Result Registry Ingestion Audit Contract\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — Result registry ingestion-audit contract frozen with no replay execution and no result-pack, label, PnL, leaderboard, or ML activation.\n\n"
    "## Source Proofs\n\n"
    f"- D41: `{D41_LATEST.as_posix()}`\n"
    f"- D38: `{d41.get('source_proofs', {}).get('d38')}`\n"
    f"- D39: `{d41.get('source_proofs', {}).get('d39')}`\n"
    f"- D40: `{d41.get('source_proofs', {}).get('d40')}`\n\n"
    "## Frozen Surfaces\n\n"
    "- Future result-pack ingestion audit columns\n"
    "- Verified result-pack presence gate\n"
    "- Label-binding gate, blocked\n"
    "- Real-PnL calculation gate, blocked\n"
    "- Leaderboard gate, blocked\n"
    "- ML-export gate, blocked\n"
    "- SQLite/DuckDB-ready ingestion audit type map\n\n"
    "## Important Limitation\n\n"
    "D3-D42 does not execute replay, create result packs, attach candidate context, match trades, bind labels, calculate real PnL, build leaderboard, export ML data, train models, write live Redis, call brokers, or enable paper/live.\n\n"
    "## Next\n\n"
    "LANE-D3-D43_LEADERBOARD_AND_ML_ELIGIBILITY_STORAGE_PLACEHOLDER_CONTRACT_NO_EXECUTION\n",
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
    "sample_audit_path": sample_audit_path.as_posix(),
    "progress_report_path": progress_report_path.as_posix(),
    "optimizer_verdict_path": optimizer_verdict_path.as_posix(),
    "candidate_count_from_d38": d41.get("candidate_count_from_d38"),
    "next": "LANE-D3-D43_LEADERBOARD_AND_ML_ELIGIBILITY_STORAGE_PLACEHOLDER_CONTRACT_NO_EXECUTION",
}, indent=2, sort_keys=True))
