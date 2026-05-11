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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d17_row_count_normalization_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/row_count_normalization.py",
    "etc/replay_optimization/normalization/row_count_normalization_contract.json",
    "bin/proof_replay_optimization_d17_row_count_normalization.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/row_count_normalization.py",
    "bin/proof_replay_optimization_d17_row_count_normalization.py",
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
    raise SystemExit(f"missing expected D17 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/row_count_normalization.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/row_count_normalization.py",
    "etc/replay_optimization/normalization/row_count_normalization_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/normalization/row_count_normalization_contract.json"])
safety = config["safety"]
for key in [
    "replay_execution_allowed",
    "result_pack_assembly_allowed",
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
        raise SystemExit(f"D17 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.row_count_normalization")

d16_latest = ROOT / "run" / "proofs" / "proof_lane_d_d16_result_pack_verification_latest.json"
verification_report_path = latest_path_from_proof(d16_latest, "verification_report_path")

optimization_id = f"D17_ROW_COUNT_NORMALIZATION_PROBE_{TS}"
result = mod.write_row_count_normalization_audit(
    optimization_id,
    ARTIFACT_ROOT,
    verification_report_path=verification_report_path,
)

for path_value in [result.row_count_audit_path, result.optimizer_verdict_path]:
    if not Path(path_value).exists():
        raise SystemExit(f"D17 output missing: {path_value}")

audit = load_json(Path(result.row_count_audit_path))

if audit.get("label_binding_allowed") is not False:
    raise SystemExit("D17 must not allow label binding")
if audit.get("labels_bound") is not False:
    raise SystemExit("D17 must not bind labels")
if audit.get("candidate_trade_matching_allowed") is not False:
    raise SystemExit("D17 must not allow candidate-trade matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D17 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D17 unexpectedly bound labels")
if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D17 unexpectedly allowed candidate-trade matching")
if result.replay_execution_performed is not False:
    raise SystemExit("D17 unexpectedly executed replay")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D17 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D17 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D17 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D17 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D17 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D17 unexpectedly enabled paper/live")

allowed_statuses = {
    "BLOCKED_ALL_ZERO_ROWS_NO_LABEL_SOURCE",
    "ROW_COUNTS_EQUAL_POSITIVE_AUDIT_ONLY",
    "BLOCKED_UNEQUAL_ROW_COUNTS",
    "BLOCKED_INTEGRITY_FAIL_OR_UNKNOWN",
    "BLOCKED_MISSING_SELECTED_PACK",
}
if result.normalized_row_status not in allowed_statuses:
    raise SystemExit(f"D17 unexpected normalized status: {result.normalized_row_status}")

if audit.get("all_zero_rows") is True:
    next_batch = "LANE-D-D18_NONZERO_RESULT_PACK_DISCOVERY_AUDIT_NO_EXECUTION"
elif result.normalized_row_status == "ROW_COUNTS_EQUAL_POSITIVE_AUDIT_ONLY":
    next_batch = "LANE-D-D18_INTEGRITY_PASS_FILTER_AUDIT_NO_LABEL_BINDING"
elif result.normalized_row_status == "BLOCKED_INTEGRITY_FAIL_OR_UNKNOWN":
    next_batch = "LANE-D-D18_INTEGRITY_PASS_FILTER_AUDIT_NO_LABEL_BINDING"
else:
    next_batch = "LANE-D-D18_ROW_COUNT_SOURCE_DIAGNOSTIC_AUDIT_NO_LABEL_BINDING"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D17",
    "name": "row_count_normalization_audit_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "ROW_COUNT_NORMALIZATION_AUDIT_ONLY",
    "d16_dependency_observed": bool(verification_report_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "verification_report_path": verification_report_path,
    "row_count_audit_path": result.row_count_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "normalized_row_status": result.normalized_row_status,
    "selected_pack_id": result.selected_pack_id,
    "selected_candidate_root": result.selected_candidate_root,
    "audit": audit,
    "safety": {
        "row_count_normalization_audit_built": True,
        "result_pack_assembly_allowed": False,
        "candidate_trade_matching_allowed": False,
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

proof_path = PROOF_DIR / f"proof_lane_d_d17_row_count_normalization_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d17_row_count_normalization_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d17_row_count_normalization_{TS}.md"
milestone_path.write_text(
    "# LANE D D17 — Row Count Normalization Audit\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D17 row-count normalization audit created and proved.\n\n"
    "## Normalized Row Status\n\n"
    f"{result.normalized_row_status}\n\n"
    "## Important Limitation\n\n"
    "D17 is audit-only. It does not execute replay, assemble packs, match candidates to trades, bind labels, calculate PnL, train/predict, or approve optimization.\n\n"
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
    "row_count_audit_path": result.row_count_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "normalized_row_status": result.normalized_row_status,
    "selected_pack_id": result.selected_pack_id,
    "selected_candidate_root": result.selected_candidate_root,
    "next": next_batch,
}, indent=2, sort_keys=True))
