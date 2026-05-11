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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d26_context_source_discovery_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/context_source_discovery.py",
    "etc/replay_optimization/context/context_source_discovery_contract.json",
    "bin/proof_replay_optimization_d26_context_source_discovery.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/context_source_discovery.py",
    "bin/proof_replay_optimization_d26_context_source_discovery.py",
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
    raise SystemExit(f"missing expected D26 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/context_source_discovery.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/context_source_discovery.py",
    "etc/replay_optimization/context/context_source_discovery_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/context/context_source_discovery_contract.json"])
safety = config["safety"]
for key in [
    "replay_execution_allowed",
    "result_pack_assembly_allowed",
    "candidate_context_inference_allowed",
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
        raise SystemExit(f"D26 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.context_source_discovery")

d25_latest = ROOT / "run" / "proofs" / "proof_lane_d_d25_candidate_context_enrichment_latest.json"
d19_latest = ROOT / "run" / "proofs" / "proof_lane_d_d19_nonzero_pack_verification_latest.json"

context_rows_path = latest_path_from_proof(d25_latest, "context_rows_json_path")
nonzero_verification_report_path = latest_path_from_proof(d19_latest, "nonzero_verification_report_path")

optimization_id = f"D26_CONTEXT_SOURCE_DISCOVERY_PROBE_{TS}"
result = mod.write_context_source_discovery_audit(
    optimization_id,
    ARTIFACT_ROOT,
    context_rows_path=context_rows_path,
    nonzero_verification_report_path=nonzero_verification_report_path,
)

for path_value in [
    result.source_discovery_report_path,
    result.source_discovery_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D26 output missing: {path_value}")

report = load_json(Path(result.source_discovery_report_path))
rows = report.get("rows")
if not isinstance(rows, list) or not rows:
    raise SystemExit("D26 source discovery rows missing")

for key in [
    "candidate_context_inference_allowed",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if report.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D26 report safety failed: {key}")

sample_row = rows[0]
for key in [
    "candidate_context_inference_allowed",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if sample_row.get(key) is not False:
        raise SystemExit(f"D26 row safety failed: {key}")

if result.candidate_context_inference_allowed is not False:
    raise SystemExit("D26 unexpectedly allowed context inference")
if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D26 unexpectedly allowed matching")
if result.candidate_trade_matching_performed is not False:
    raise SystemExit("D26 unexpectedly performed matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D26 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D26 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D26 unexpectedly executed replay")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D26 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D26 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D26 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D26 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D26 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D26 unexpectedly enabled paper/live")

if result.context_row_count != 810:
    raise SystemExit(f"D26 expected 810 context rows, got {result.context_row_count}")
if result.complete_context_row_count != 0:
    raise SystemExit(f"D26 expected zero complete context rows, got {result.complete_context_row_count}")
if result.missing_required_context_row_count != 810:
    raise SystemExit(f"D26 expected 810 missing-context rows, got {result.missing_required_context_row_count}")
if result.source_discovery_row_count != 20:
    raise SystemExit(f"D26 expected 20 discovery rows, got {result.source_discovery_row_count}")

allowed_statuses = {
    "BLOCKED_NO_D25_CONTEXT_ROWS",
    "BLOCKED_NO_D19_VERIFIED_RESULT_REFS",
    "BLOCKED_NO_RESULT_SOURCE_KEYS_FOR_REQUIRED_CONTEXT",
    "CONTEXT_SOURCE_KEYS_FOUND_SCHEMA_ONLY_NOT_LABEL_READY",
}
if result.discovery_status not in allowed_statuses:
    raise SystemExit(f"D26 unexpected discovery status: {result.discovery_status}")

if result.required_context_keys_with_sources_count > 0:
    next_batch = "LANE-D-D27_CONTEXT_SOURCE_MAPPING_SCHEMA_CONTRACT_NO_LABEL_BINDING"
else:
    next_batch = "LANE-D-D27_REPLAY_RESULT_CONTEXT_KEY_REQUIREMENT_AUDIT_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D26",
    "name": "candidate_context_source_discovery_audit_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CANDIDATE_CONTEXT_SOURCE_DISCOVERY_AUDIT_ONLY",
    "d25_dependency_observed": bool(context_rows_path),
    "d19_dependency_observed": bool(nonzero_verification_report_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "context_rows_path": context_rows_path,
    "nonzero_verification_report_path": nonzero_verification_report_path,
    "source_discovery_report_path": result.source_discovery_report_path,
    "source_discovery_rows_csv_path": result.source_discovery_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "context_row_count": result.context_row_count,
    "complete_context_row_count": result.complete_context_row_count,
    "missing_required_context_row_count": result.missing_required_context_row_count,
    "source_discovery_row_count": result.source_discovery_row_count,
    "required_context_keys_with_sources_count": result.required_context_keys_with_sources_count,
    "discovery_status": result.discovery_status,
    "sample_source_discovery_row": sample_row,
    "report": report,
    "safety": {
        "candidate_context_source_discovery_built": True,
        "candidate_context_inference_allowed": False,
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

proof_path = PROOF_DIR / f"proof_lane_d_d26_context_source_discovery_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d26_context_source_discovery_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d26_context_source_discovery_{TS}.md"
milestone_path.write_text(
    "# LANE D D26 — Candidate Context Source Discovery Audit\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D26 candidate-context source discovery audit created and proved.\n\n"
    "## Discovery Status\n\n"
    f"{result.discovery_status}\n\n"
    "## Important Limitation\n\n"
    "D26 is audit-only. It discovers possible source keys only. It does not infer/fill context, match candidates to trades, bind labels, calculate PnL, train/predict, execute replay, or approve optimization.\n\n"
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
    "source_discovery_report_path": result.source_discovery_report_path,
    "source_discovery_rows_csv_path": result.source_discovery_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "context_row_count": result.context_row_count,
    "complete_context_row_count": result.complete_context_row_count,
    "missing_required_context_row_count": result.missing_required_context_row_count,
    "source_discovery_row_count": result.source_discovery_row_count,
    "required_context_keys_with_sources_count": result.required_context_keys_with_sources_count,
    "discovery_status": result.discovery_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
