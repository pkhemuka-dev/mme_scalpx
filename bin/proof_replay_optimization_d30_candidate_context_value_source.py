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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d30_candidate_context_value_source_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_context_value_source.py",
    "etc/replay_optimization/context/candidate_context_value_source_contract.json",
    "bin/proof_replay_optimization_d30_candidate_context_value_source.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_context_value_source.py",
    "bin/proof_replay_optimization_d30_candidate_context_value_source.py",
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
    raise SystemExit(f"missing expected D30 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/candidate_context_value_source.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/candidate_context_value_source.py",
    "etc/replay_optimization/context/candidate_context_value_source_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/context/candidate_context_value_source_contract.json"])
safety = config["safety"]
for key in [
    "replay_execution_allowed",
    "result_pack_assembly_allowed",
    "candidate_context_inference_allowed",
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
        raise SystemExit(f"D30 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.candidate_context_value_source")

d25_latest = ROOT / "run" / "proofs" / "proof_lane_d_d25_candidate_context_enrichment_latest.json"
d20_latest = ROOT / "run" / "proofs" / "proof_lane_d_d20_candidate_trade_matching_schema_latest.json"
d5_latest = ROOT / "run" / "proofs" / "proof_lane_d_d5_candidate_matrix_latest.json"

candidate_context_rows_path = latest_path_from_proof(d25_latest, "context_rows_json_path")
matching_rows_path = latest_path_from_proof(d20_latest, "matching_rows_json_path")
candidate_matrix_path = latest_path_from_proof(d5_latest, "candidate_matrix_path")

optimization_id = f"D30_CANDIDATE_CONTEXT_VALUE_SOURCE_PROBE_{TS}"
result = mod.write_candidate_context_value_source_audit(
    optimization_id,
    ARTIFACT_ROOT,
    candidate_context_rows_path=candidate_context_rows_path,
    matching_rows_path=matching_rows_path,
    candidate_matrix_path=candidate_matrix_path,
)

for path_value in [
    result.value_source_report_path,
    result.value_source_rows_json_path,
    result.value_source_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D30 output missing: {path_value}")

report = load_json(Path(result.value_source_report_path))
rows_payload = load_json(Path(result.value_source_rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list) or len(rows) != 15:
    raise SystemExit("D30 expected exactly 15 value-source rows")

sample_row = rows[0]
for key in [
    "candidate_context_inference_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if sample_row.get(key) is not False:
        raise SystemExit(f"D30 row safety failed: {key}")

for key in [
    "candidate_context_inference_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if report.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D30 report safety failed: {key}")

if result.candidate_context_inference_allowed is not False:
    raise SystemExit("D30 unexpectedly allowed candidate context inference")
if result.candidate_context_attached is not False:
    raise SystemExit("D30 unexpectedly attached candidate context")
if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D30 unexpectedly allowed matching")
if result.candidate_trade_matching_performed is not False:
    raise SystemExit("D30 unexpectedly performed matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D30 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D30 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D30 unexpectedly executed replay")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D30 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D30 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D30 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D30 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D30 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D30 unexpectedly enabled paper/live")

if result.candidate_context_row_count != 810:
    raise SystemExit(f"D30 expected 810 candidate context rows, got {result.candidate_context_row_count}")
if result.matching_row_count != 810:
    raise SystemExit(f"D30 expected 810 matching rows, got {result.matching_row_count}")
if result.value_source_row_count != 15:
    raise SystemExit(f"D30 expected 15 value-source rows, got {result.value_source_row_count}")

allowed_statuses = {
    "BLOCKED_NO_CANDIDATE_CONTEXT_ROWS",
    "BLOCKED_NO_CANDIDATE_INPUT_ROWS",
    "BLOCKED_REQUIRED_CANDIDATE_CONTEXT_VALUES_NOT_AVAILABLE",
    "CANDIDATE_CONTEXT_VALUE_SOURCES_FOUND_AUDIT_ONLY_NOT_LABEL_READY",
}
if result.value_source_status not in allowed_statuses:
    raise SystemExit(f"D30 unexpected value source status: {result.value_source_status}")

if result.required_context_keys_with_value_sources_count > 0:
    next_batch = "LANE-D-D31_CANDIDATE_CONTEXT_ENRICHMENT_DRY_RUN_NO_LABEL_BINDING"
else:
    next_batch = "LANE-D-D31_CANDIDATE_REPLAY_BINDING_REQUIREMENT_AUDIT_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D30",
    "name": "candidate_context_value_source_audit_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CANDIDATE_CONTEXT_VALUE_SOURCE_AUDIT_ONLY",
    "d25_dependency_observed": bool(candidate_context_rows_path),
    "d20_dependency_observed": bool(matching_rows_path),
    "d5_dependency_observed": bool(candidate_matrix_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "candidate_context_rows_path": candidate_context_rows_path,
    "matching_rows_path": matching_rows_path,
    "candidate_matrix_path": candidate_matrix_path,
    "value_source_report_path": result.value_source_report_path,
    "value_source_rows_json_path": result.value_source_rows_json_path,
    "value_source_rows_csv_path": result.value_source_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "candidate_context_row_count": result.candidate_context_row_count,
    "matching_row_count": result.matching_row_count,
    "candidate_matrix_row_count": result.candidate_matrix_row_count,
    "value_source_row_count": result.value_source_row_count,
    "required_context_keys_with_value_sources_count": result.required_context_keys_with_value_sources_count,
    "required_context_keys_missing_value_sources_count": result.required_context_keys_missing_value_sources_count,
    "value_source_status": result.value_source_status,
    "sample_value_source_row": sample_row,
    "report": report,
    "safety": {
        "candidate_context_value_source_audit_built": True,
        "candidate_context_inference_allowed": False,
        "candidate_context_attached": False,
        "candidate_trade_matching_allowed": False,
        "candidate_trade_matching_performed": False,
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
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d30_candidate_context_value_source_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d30_candidate_context_value_source_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d30_candidate_context_value_source_{TS}.md"
milestone_path.write_text(
    "# LANE D D30 — Candidate Context Value Source Audit\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D30 candidate-context value-source audit created and proved.\n\n"
    "## Value Source Status\n\n"
    f"{result.value_source_status}\n\n"
    "## Important Limitation\n\n"
    "D30 audits candidate-side value sources only. It does not infer/fill context, attach candidate context, match candidates to trades, bind labels, calculate PnL, train/predict, execute replay, or approve optimization.\n\n"
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
    "value_source_report_path": result.value_source_report_path,
    "value_source_rows_json_path": result.value_source_rows_json_path,
    "value_source_rows_csv_path": result.value_source_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "candidate_context_row_count": result.candidate_context_row_count,
    "matching_row_count": result.matching_row_count,
    "candidate_matrix_row_count": result.candidate_matrix_row_count,
    "value_source_row_count": result.value_source_row_count,
    "required_context_keys_with_value_sources_count": result.required_context_keys_with_value_sources_count,
    "required_context_keys_missing_value_sources_count": result.required_context_keys_missing_value_sources_count,
    "value_source_status": result.value_source_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
