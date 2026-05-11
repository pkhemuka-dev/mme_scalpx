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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d40_lane_d_freeze_summary_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/lane_d_freeze_summary.py",
    "etc/replay_optimization/handoff/lane_d_freeze_summary_contract.json",
    "bin/proof_replay_optimization_d40_lane_d_freeze_summary.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/lane_d_freeze_summary.py",
    "bin/proof_replay_optimization_d40_lane_d_freeze_summary.py",
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


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D40 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/lane_d_freeze_summary.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/lane_d_freeze_summary.py",
    "etc/replay_optimization/handoff/lane_d_freeze_summary_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/handoff/lane_d_freeze_summary_contract.json"])
safety = config["safety"]
for key in [
    "lane_d_execution_allowed",
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
        raise SystemExit(f"D40 config safety failed: {key}")
if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D40 config must require Lane C/E execution ownership")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.lane_d_freeze_summary")

optimization_id = f"D40_LANE_D_FREEZE_SUMMARY_PROBE_{TS}"
result = mod.write_lane_d_freeze_summary(
    optimization_id,
    ARTIFACT_ROOT,
)

for path_value in [
    result.freeze_schema_path,
    result.freeze_summary_path,
    result.freeze_rows_json_path,
    result.freeze_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D40 output missing: {path_value}")

summary = load_json(Path(result.freeze_summary_path))
rows_payload = load_json(Path(result.freeze_rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list) or len(rows) != 9:
    raise SystemExit("D40 expected exactly 9 freeze rows")

for row in rows:
    if row.get("freeze_row_status") != "PASS":
        raise SystemExit(f"D40 freeze row not PASS: {row}")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed",
    "result_pack_created",
    "artifact_file_creation_allowed",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if summary.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D40 summary safety failed: {key}")

if summary.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D40 summary must require Lane C/E execution ownership")

if result.required_proof_count != 9:
    raise SystemExit(f"D40 expected 9 required proofs, got {result.required_proof_count}")
if result.passed_proof_count != 9:
    raise SystemExit(f"D40 expected 9 passed proofs, got {result.passed_proof_count}")
if result.missing_proof_count != 0:
    raise SystemExit(f"D40 expected zero missing proofs, got {result.missing_proof_count}")
if result.failed_proof_count != 0:
    raise SystemExit(f"D40 expected zero failed proofs, got {result.failed_proof_count}")
if result.unsafe_proof_count != 0:
    raise SystemExit(f"D40 expected zero unsafe proofs, got {result.unsafe_proof_count}")
if result.candidate_count != 810:
    raise SystemExit(f"D40 expected 810 candidates, got {result.candidate_count}")
if result.package_ready_count != 810:
    raise SystemExit(f"D40 expected 810 package-ready rows, got {result.package_ready_count}")
if result.freeze_status != "LANE_D_REPLAY_OPTIMIZATION_FREEZE_COMPLETE_NO_EXECUTION":
    raise SystemExit(f"D40 unexpected freeze status: {result.freeze_status}")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D40",
    "name": "replay_optimization_lane_d_freeze_summary_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "LANE_D_FREEZE_SUMMARY_NO_EXECUTION",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "freeze_schema_path": result.freeze_schema_path,
    "freeze_summary_path": result.freeze_summary_path,
    "freeze_rows_json_path": result.freeze_rows_json_path,
    "freeze_rows_csv_path": result.freeze_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "required_proof_count": result.required_proof_count,
    "passed_proof_count": result.passed_proof_count,
    "missing_proof_count": result.missing_proof_count,
    "failed_proof_count": result.failed_proof_count,
    "unsafe_proof_count": result.unsafe_proof_count,
    "candidate_count": result.candidate_count,
    "package_ready_count": result.package_ready_count,
    "freeze_status": result.freeze_status,
    "summary": summary,
    "safety": {
        "lane_d_freeze_summary_built": True,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed": False,
        "result_pack_created": False,
        "artifact_file_creation_allowed": False,
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
    "next_recommended_batch": "LANE-D-COMPLETE_HANDOFF_TO_LANE_C_OR_E_FOR_EXECUTION_PACKAGE"
}

proof_path = PROOF_DIR / f"proof_lane_d_d40_lane_d_freeze_summary_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d40_lane_d_freeze_summary_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d40_lane_d_freeze_summary_{TS}.md"
milestone_path.write_text(
    "# LANE D D40 — Replay Optimization Lane D Freeze Summary\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — Lane D replay optimization freeze summary created and proved.\n\n"
    "## Freeze Status\n\n"
    f"{result.freeze_status}\n\n"
    "## Required Proofs\n\n"
    f"- Required proofs: {result.required_proof_count}\n"
    f"- Passed proofs: {result.passed_proof_count}\n"
    f"- Missing proofs: {result.missing_proof_count}\n"
    f"- Failed proofs: {result.failed_proof_count}\n"
    f"- Unsafe proofs: {result.unsafe_proof_count}\n\n"
    "## Scope Complete\n\n"
    "Lane D completed replay-optimization contract/schema/validator/preflight/handoff surfaces through the Lane C/E execution-package requirement.\n\n"
    "## Ownership Stop Point\n\n"
    "Lane D must stop here. Future candidate replay/result-pack materialization must be Lane C/E-owned.\n\n"
    "## Important Limitation\n\n"
    "D40 does not execute replay, create artifacts/result packs, attach candidate context, match trades, bind labels, calculate PnL, train/predict, or approve optimization.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "freeze_schema_path": result.freeze_schema_path,
    "freeze_summary_path": result.freeze_summary_path,
    "freeze_rows_json_path": result.freeze_rows_json_path,
    "freeze_rows_csv_path": result.freeze_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "required_proof_count": result.required_proof_count,
    "passed_proof_count": result.passed_proof_count,
    "missing_proof_count": result.missing_proof_count,
    "failed_proof_count": result.failed_proof_count,
    "unsafe_proof_count": result.unsafe_proof_count,
    "candidate_count": result.candidate_count,
    "package_ready_count": result.package_ready_count,
    "freeze_status": result.freeze_status,
    "next": "LANE-D-COMPLETE_HANDOFF_TO_LANE_C_OR_E_FOR_EXECUTION_PACKAGE",
}, indent=2, sort_keys=True))
