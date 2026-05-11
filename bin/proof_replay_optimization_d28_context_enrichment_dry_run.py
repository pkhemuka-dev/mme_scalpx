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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d28_context_enrichment_dry_run_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/context_enrichment_dry_run.py",
    "etc/replay_optimization/context/context_enrichment_dry_run_contract.json",
    "bin/proof_replay_optimization_d28_context_enrichment_dry_run.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/context_enrichment_dry_run.py",
    "bin/proof_replay_optimization_d28_context_enrichment_dry_run.py",
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
    raise SystemExit(f"missing expected D28 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/context_enrichment_dry_run.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/context_enrichment_dry_run.py",
    "etc/replay_optimization/context/context_enrichment_dry_run_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/context/context_enrichment_dry_run_contract.json"])
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
        raise SystemExit(f"D28 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.context_enrichment_dry_run")

d25_latest = ROOT / "run" / "proofs" / "proof_lane_d_d25_candidate_context_enrichment_latest.json"
d27_latest = ROOT / "run" / "proofs" / "proof_lane_d_d27_context_source_mapping_latest.json"

context_rows_path = latest_path_from_proof(d25_latest, "context_rows_json_path")
mapping_rows_path = latest_path_from_proof(d27_latest, "mapping_rows_json_path")

optimization_id = f"D28_CONTEXT_ENRICHMENT_DRY_RUN_PROBE_{TS}"
result = mod.write_context_enrichment_dry_run(
    optimization_id,
    ARTIFACT_ROOT,
    context_rows_path=context_rows_path,
    mapping_rows_path=mapping_rows_path,
)

for path_value in [
    result.dry_run_report_path,
    result.result_context_rows_json_path,
    result.result_context_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D28 output missing: {path_value}")

report = load_json(Path(result.dry_run_report_path))
rows_payload = load_json(Path(result.result_context_rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list) or not rows:
    raise SystemExit("D28 result-context rows missing")

sample_row = rows[0]
for key in [
    "candidate_context_attached",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if sample_row.get(key) is not False:
        raise SystemExit(f"D28 row safety failed: {key}")

if sample_row.get("candidate_id") is not None:
    raise SystemExit("D28 must not attach candidate_id to result context row")
if sample_row.get("label_pnl") is not None:
    raise SystemExit("D28 must not bind label_pnl")
if sample_row.get("label_profitable") is not None:
    raise SystemExit("D28 must not bind label_profitable")

for key in [
    "candidate_context_inference_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if report.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D28 report safety failed: {key}")

if result.candidate_context_inference_allowed is not False:
    raise SystemExit("D28 unexpectedly allowed context inference")
if result.candidate_context_attached is not False:
    raise SystemExit("D28 unexpectedly attached candidate context")
if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D28 unexpectedly allowed matching")
if result.candidate_trade_matching_performed is not False:
    raise SystemExit("D28 unexpectedly performed matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D28 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D28 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D28 unexpectedly executed replay")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D28 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D28 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D28 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D28 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D28 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D28 unexpectedly enabled paper/live")

if result.candidate_context_row_count != 810:
    raise SystemExit(f"D28 expected 810 candidate context rows, got {result.candidate_context_row_count}")
if result.candidate_context_complete_count != 0:
    raise SystemExit(f"D28 expected zero complete candidate context rows, got {result.candidate_context_complete_count}")
if result.candidate_context_attached_count != 0:
    raise SystemExit(f"D28 expected zero candidate context attachments, got {result.candidate_context_attached_count}")
if result.mapping_row_count != 5:
    raise SystemExit(f"D28 expected 5 mapping rows, got {result.mapping_row_count}")
if result.result_context_row_count != 4:
    raise SystemExit(f"D28 expected 4 result-context rows, got {result.result_context_row_count}")
if result.result_context_complete_count != 4:
    raise SystemExit(f"D28 expected 4 complete result-context rows, got {result.result_context_complete_count}")
if result.dry_run_status != "RESULT_CONTEXT_CATALOG_DRY_RUN_READY_NOT_LABEL_READY":
    raise SystemExit(f"D28 unexpected dry-run status: {result.dry_run_status}")

next_batch = "LANE-D-D29_CANDIDATE_RESULT_BRIDGE_KEY_DISCOVERY_AUDIT_NO_LABEL_BINDING"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D28",
    "name": "context_enrichment_dry_run_audit_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CONTEXT_ENRICHMENT_DRY_RUN_AUDIT_ONLY",
    "d25_dependency_observed": bool(context_rows_path),
    "d27_dependency_observed": bool(mapping_rows_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "context_rows_path": context_rows_path,
    "mapping_rows_path": mapping_rows_path,
    "dry_run_report_path": result.dry_run_report_path,
    "result_context_rows_json_path": result.result_context_rows_json_path,
    "result_context_rows_csv_path": result.result_context_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "candidate_context_row_count": result.candidate_context_row_count,
    "candidate_context_complete_count": result.candidate_context_complete_count,
    "candidate_context_attached_count": result.candidate_context_attached_count,
    "mapping_row_count": result.mapping_row_count,
    "result_context_row_count": result.result_context_row_count,
    "result_context_complete_count": result.result_context_complete_count,
    "dry_run_status": result.dry_run_status,
    "sample_result_context_row": sample_row,
    "report": report,
    "safety": {
        "context_enrichment_dry_run_built": True,
        "result_context_catalog_built": result.result_context_catalog_built,
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

proof_path = PROOF_DIR / f"proof_lane_d_d28_context_enrichment_dry_run_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d28_context_enrichment_dry_run_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d28_context_enrichment_dry_run_{TS}.md"
milestone_path.write_text(
    "# LANE D D28 — Context Enrichment Dry-Run Audit\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D28 result-context catalog dry-run created and proved.\n\n"
    "## Dry-Run Status\n\n"
    f"{result.dry_run_status}\n\n"
    "## Important Limitation\n\n"
    "D28 builds a result-context catalog only. It does not attach context to candidate rows, match candidates to trades, bind labels, calculate PnL, train/predict, execute replay, or approve optimization.\n\n"
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
    "dry_run_report_path": result.dry_run_report_path,
    "result_context_rows_json_path": result.result_context_rows_json_path,
    "result_context_rows_csv_path": result.result_context_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "candidate_context_row_count": result.candidate_context_row_count,
    "candidate_context_complete_count": result.candidate_context_complete_count,
    "candidate_context_attached_count": result.candidate_context_attached_count,
    "mapping_row_count": result.mapping_row_count,
    "result_context_row_count": result.result_context_row_count,
    "result_context_complete_count": result.result_context_complete_count,
    "dry_run_status": result.dry_run_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
