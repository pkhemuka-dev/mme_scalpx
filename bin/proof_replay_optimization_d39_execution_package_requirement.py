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
    "app/mme_scalpx/replay_optimization/execution_package_requirement.py",
    "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_contract.json",
    "bin/proof_replay_optimization_d39_execution_package_requirement.py",
    "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json",
    "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json",
    "run/proofs/proof_lane_d_d38_phase_gate_summary_latest.json",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement.py",
    "bin/proof_replay_optimization_d39_execution_package_requirement.py",
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


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


files = {rel: ROOT / rel for rel in EXPECTED_FILES}
missing = [rel for rel, path in files.items() if not path.exists()]
if missing:
    raise SystemExit(f"missing expected D39 dependency/target files: {missing}")

d32 = load_json(ROOT / "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json")
d37 = load_json(ROOT / "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json")
d38 = load_json(ROOT / "run/proofs/proof_lane_d_d38_phase_gate_summary_latest.json")

if d32.get("verdict") != "PASS":
    raise SystemExit("D32 proof is not PASS")
if d37.get("verdict") != "PASS":
    raise SystemExit("D37 proof is not PASS")
if d38.get("verdict") != "PASS":
    raise SystemExit("D38 proof is not PASS")
if d38.get("next_recommended_batch") != "LANE-D-D39_LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION":
    raise SystemExit(f"D38 next batch does not point to D39: {d38.get('next_recommended_batch')}")
if d32.get("candidate_count") != 810:
    raise SystemExit(f"D32 candidate_count expected 810, got {d32.get('candidate_count')}")
if d37.get("handoff_row_count") != 810:
    raise SystemExit(f"D37 handoff_row_count expected 810, got {d37.get('handoff_row_count')}")
if d37.get("handoff_ready_count") != 810:
    raise SystemExit(f"D37 handoff_ready_count expected 810, got {d37.get('handoff_ready_count')}")
if d38.get("candidate_count") != 810:
    raise SystemExit(f"D38 candidate_count expected 810, got {d38.get('candidate_count')}")
if d38.get("handoff_ready_count") != 810:
    raise SystemExit(f"D38 handoff_ready_count expected 810, got {d38.get('handoff_ready_count')}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/execution_package_requirement.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/execution_package_requirement.py",
    "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(ROOT / "etc/replay_optimization/handoff/lane_ce_execution_package_requirement_contract.json")
safety = config["safety"]
for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "artifact_file_creation_allowed_in_lane_d",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_allowed",
    "real_pnl_calculation_performed",
    "model_training_allowed",
    "model_prediction_allowed",
    "broker_calls_allowed",
    "live_redis_writes_allowed",
    "paper_live_enablement_allowed",
]:
    if safety.get(key) is not False:
        raise SystemExit(f"D39 config safety failed: {key}")
if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D39 config must require Lane C/E execution ownership")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.execution_package_requirement")

optimization_id = f"D39_LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_PROBE_{TS}"
result = mod.write_execution_package_requirements(
    optimization_id,
    ARTIFACT_ROOT,
    root=ROOT,
)

for path_value in [
    result.schema_path,
    result.summary_path,
    result.rows_json_path,
    result.rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D39 output missing: {path_value}")

summary = load_json(Path(result.summary_path))
rows_payload = load_json(Path(result.rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list):
    raise SystemExit("D39 rows payload missing rows list")
if len(rows) != 810:
    raise SystemExit(f"D39 expected 810 requirement rows, got {len(rows)}")

for row in rows:
    if row.get("package_row_status") != "PACKAGE_REQUIREMENT_READY_NO_EXECUTION":
        raise SystemExit(f"D39 row has unexpected status: {row}")
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
            raise SystemExit(f"D39 row safety failed {key}: {row}")
    if row.get("lane_c_or_e_execution_required") is not True:
        raise SystemExit(f"D39 row must require Lane C/E execution: {row}")
    if not row.get("candidate_id"):
        raise SystemExit(f"D39 row missing candidate_id: {row}")
    if not row.get("candidate_fingerprint"):
        raise SystemExit(f"D39 row missing candidate_fingerprint: {row}")
    if not row.get("planned_result_pack_root"):
        raise SystemExit(f"D39 row missing planned_result_pack_root: {row}")

if summary.get("candidate_count") != 810:
    raise SystemExit(f"D39 summary candidate_count expected 810, got {summary.get('candidate_count')}")
if summary.get("package_requirement_ready_count") != 810:
    raise SystemExit(f"D39 summary ready count expected 810, got {summary.get('package_requirement_ready_count')}")
if summary.get("full_universe_preserved") is not True:
    raise SystemExit("D39 summary must preserve full universe")
if summary.get("requirement_status") != "LANE_CE_EXECUTION_PACKAGE_REQUIREMENTS_READY_NO_EXECUTION":
    raise SystemExit(f"D39 unexpected requirement status: {summary.get('requirement_status')}")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "artifact_file_creation_allowed_in_lane_d",
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
    if summary.get("safety", {}).get(key) is not False:
        raise SystemExit(f"D39 summary safety failed: {key}")
if summary.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D39 summary must require Lane C/E execution ownership")

next_batch = "LANE-D1-D40_EXECUTION_PACKAGE_REQUIREMENT_VALIDATOR_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items() if path.exists()}

proof = {
    "batch": "LANE-D1-D39",
    "legacy_sequence_batch": "LANE-D-D39",
    "chat_lane": "Lane D1 only",
    "name": "lane_ce_execution_package_requirement_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "schema_path": result.schema_path,
    "summary_path": result.summary_path,
    "rows_json_path": result.rows_json_path,
    "rows_csv_path": result.rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "candidate_count": result.candidate_count,
    "source_handoff_row_count": result.source_handoff_row_count,
    "package_requirement_row_count": result.package_requirement_row_count,
    "package_requirement_ready_count": result.package_requirement_ready_count,
    "phase_status": result.phase_status,
    "d32_dependency_observed": {
        "path": "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json",
        "verdict": d32.get("verdict"),
        "candidate_count": d32.get("candidate_count")
    },
    "d37_dependency_observed": {
        "path": "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json",
        "verdict": d37.get("verdict"),
        "handoff_row_count": d37.get("handoff_row_count"),
        "handoff_ready_count": d37.get("handoff_ready_count")
    },
    "d38_dependency_observed": {
        "path": "run/proofs/proof_lane_d_d38_phase_gate_summary_latest.json",
        "verdict": d38.get("verdict"),
        "candidate_count": d38.get("candidate_count"),
        "handoff_ready_count": d38.get("handoff_ready_count"),
        "next_recommended_batch": d38.get("next_recommended_batch")
    },
    "safety": {
        "execution_package_requirement_built": True,
        "full_universe_preserved": True,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed_in_lane_d": False,
        "result_pack_created": False,
        "artifact_file_creation_allowed_in_lane_d": False,
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
    "important_limitation": "D39 does not execute replay, create real result packs, bind labels, calculate PnL, train/predict, or approve optimization.",
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d39_lane_ce_execution_package_requirement_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d1_d39_lane_ce_execution_package_requirement_{TS}.md"
milestone_path.write_text(
    "# LANE D1 D39 — Lane C/E Execution Package Requirement / No Execution\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D39 execution package requirement contract and rows created.\n\n"
    "## Evidence Chain\n\n"
    "- D32 proof PASS observed.\n"
    "- D37 handoff proof PASS observed with 810 handoff-ready candidates.\n"
    "- D38 phase gate summary PASS observed with 810 candidates and next batch D39.\n\n"
    "## Output\n\n"
    f"- Artifact root: `{ARTIFACT_ROOT.as_posix()}`\n"
    f"- Requirement rows: `{result.rows_json_path}`\n"
    f"- Requirement summary: `{result.summary_path}`\n\n"
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
    "schema_path": result.schema_path,
    "summary_path": result.summary_path,
    "rows_json_path": result.rows_json_path,
    "rows_csv_path": result.rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "candidate_count": result.candidate_count,
    "source_handoff_row_count": result.source_handoff_row_count,
    "package_requirement_row_count": result.package_requirement_row_count,
    "package_requirement_ready_count": result.package_requirement_ready_count,
    "phase_status": result.phase_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
