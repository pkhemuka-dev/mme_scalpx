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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d39_lane_ce_execution_package_requirement_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/lane_ce_execution_package_requirement.py",
    "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_contract.json",
    "bin/proof_replay_optimization_d39_lane_ce_execution_package_requirement.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/lane_ce_execution_package_requirement.py",
    "bin/proof_replay_optimization_d39_lane_ce_execution_package_requirement.py",
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
    raise SystemExit(f"missing expected D39 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/lane_ce_execution_package_requirement.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/lane_ce_execution_package_requirement.py",
    "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/handoff/lane_ce_execution_package_requirement_contract.json"])
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
        raise SystemExit(f"D39 config safety failed: {key}")
if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D39 config must require Lane C/E execution ownership")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.lane_ce_execution_package_requirement")

d38_latest = ROOT / "run" / "proofs" / "proof_lane_d_d38_phase_gate_summary_latest.json"
d37_latest = ROOT / "run" / "proofs" / "proof_lane_d_d37_lane_ce_handoff_latest.json"

phase_summary_path = latest_path_from_proof(d38_latest, "phase_summary_path")
handoff_rows_path = latest_path_from_proof(d37_latest, "handoff_rows_json_path")

optimization_id = f"D39_LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_PROBE_{TS}"
result = mod.write_lane_ce_execution_package_requirement(
    optimization_id,
    ARTIFACT_ROOT,
    phase_summary_path=phase_summary_path,
    handoff_rows_path=handoff_rows_path,
    max_rows=10000,
)

for path_value in [
    result.package_schema_path,
    result.package_rows_json_path,
    result.package_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D39 output missing: {path_value}")

rows_payload = load_json(Path(result.package_rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list) or not rows:
    raise SystemExit("D39 package requirement rows missing")

sample_row = rows[0]
for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed_in_lane_d",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "artifact_file_creation_allowed_in_lane_d",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "label_binding_allowed",
    "labels_bound",
]:
    if sample_row.get(key) is not False:
        raise SystemExit(f"D39 row safety failed: {key}")

if sample_row.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D39 row must require Lane C/E execution ownership")

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
    if rows_payload.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D39 rows safety failed: {key}")
if rows_payload.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D39 rows safety must require Lane C/E execution ownership")

if result.lane_d_execution_allowed is not False:
    raise SystemExit("D39 unexpectedly allowed Lane D execution")
if result.lane_c_or_e_execution_required is not True:
    raise SystemExit("D39 must require Lane C/E execution")
if result.replay_execution_allowed is not False:
    raise SystemExit("D39 unexpectedly allowed replay execution")
if result.replay_execution_performed is not False:
    raise SystemExit("D39 unexpectedly executed replay")
if result.result_pack_creation_allowed is not False:
    raise SystemExit("D39 unexpectedly allowed result-pack creation")
if result.result_pack_created is not False:
    raise SystemExit("D39 unexpectedly created result pack")
if result.artifact_file_creation_allowed is not False:
    raise SystemExit("D39 unexpectedly allowed artifact creation")
if result.candidate_context_attached is not False:
    raise SystemExit("D39 unexpectedly attached candidate context")
if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D39 unexpectedly allowed matching")
if result.candidate_trade_matching_performed is not False:
    raise SystemExit("D39 unexpectedly performed matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D39 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D39 unexpectedly bound labels")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D39 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D39 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D39 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D39 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D39 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D39 unexpectedly enabled paper/live")

if result.handoff_row_count != 810:
    raise SystemExit(f"D39 expected 810 handoff rows, got {result.handoff_row_count}")
if result.package_row_count != 810:
    raise SystemExit(f"D39 expected 810 package rows, got {result.package_row_count}")
if result.package_ready_count != 810:
    raise SystemExit(f"D39 expected 810 ready rows, got {result.package_ready_count}")
if result.blocked_row_count != 0:
    raise SystemExit(f"D39 expected zero blocked rows, got {result.blocked_row_count}")
if result.missing_package_requirement_row_count != 0:
    raise SystemExit(f"D39 expected zero missing package requirements, got {result.missing_package_requirement_row_count}")
if result.package_status != "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_READY_NO_EXECUTION":
    raise SystemExit(f"D39 unexpected package status: {result.package_status}")

next_batch = "LANE-D-D40_REPLAY_OPTIMIZATION_LANE_D_FREEZE_SUMMARY_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D39",
    "name": "lane_ce_execution_package_requirement_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION",
    "d38_dependency_observed": bool(phase_summary_path),
    "d37_dependency_observed": bool(handoff_rows_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "phase_summary_path": phase_summary_path,
    "handoff_rows_path": handoff_rows_path,
    "package_schema_path": result.package_schema_path,
    "package_rows_json_path": result.package_rows_json_path,
    "package_rows_csv_path": result.package_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "handoff_row_count": result.handoff_row_count,
    "package_row_count": result.package_row_count,
    "package_ready_count": result.package_ready_count,
    "blocked_row_count": result.blocked_row_count,
    "missing_package_requirement_row_count": result.missing_package_requirement_row_count,
    "package_status": result.package_status,
    "sample_package_row": sample_row,
    "safety": {
        "lane_ce_execution_package_requirement_built": True,
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
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d39_lane_ce_execution_package_requirement_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d39_lane_ce_execution_package_requirement_{TS}.md"
milestone_path.write_text(
    "# LANE D D39 — Lane C/E Execution Package Requirement\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D39 Lane C/E execution-package requirement created and proved.\n\n"
    "## Package Status\n\n"
    f"{result.package_status}\n\n"
    "## Ownership\n\n"
    "Lane D remains requirement-only. Future execution/materialization must be Lane C/E-owned.\n\n"
    "## Important Limitation\n\n"
    "D39 does not execute replay, create artifacts/result packs, attach candidate context, match trades, bind labels, calculate PnL, train/predict, or approve optimization.\n\n"
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
    "package_schema_path": result.package_schema_path,
    "package_rows_json_path": result.package_rows_json_path,
    "package_rows_csv_path": result.package_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "handoff_row_count": result.handoff_row_count,
    "package_row_count": result.package_row_count,
    "package_ready_count": result.package_ready_count,
    "blocked_row_count": result.blocked_row_count,
    "missing_package_requirement_row_count": result.missing_package_requirement_row_count,
    "package_status": result.package_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
