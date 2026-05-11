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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d38_phase_gate_summary_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/phase_gate_summary.py",
    "etc/replay_optimization/handoff/phase_gate_summary_contract.json",
    "bin/proof_replay_optimization_d38_phase_gate_summary.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/phase_gate_summary.py",
    "bin/proof_replay_optimization_d38_phase_gate_summary.py",
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
    raise SystemExit(f"missing expected D38 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/phase_gate_summary.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/phase_gate_summary.py",
    "etc/replay_optimization/handoff/phase_gate_summary_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/handoff/phase_gate_summary_contract.json"])
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
        raise SystemExit(f"D38 config safety failed: {key}")
if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D38 config must require Lane C/E execution ownership")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.phase_gate_summary")

optimization_id = f"D38_PHASE_GATE_SUMMARY_PROBE_{TS}"
result = mod.write_phase_gate_summary(
    optimization_id,
    ARTIFACT_ROOT,
)

for path_value in [
    result.phase_schema_path,
    result.phase_summary_path,
    result.phase_rows_json_path,
    result.phase_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D38 output missing: {path_value}")

summary = load_json(Path(result.phase_summary_path))
rows_payload = load_json(Path(result.phase_rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list) or len(rows) != 7:
    raise SystemExit("D38 expected exactly 7 phase gate rows")

for row in rows:
    if row.get("gate_row_status") != "PASS":
        raise SystemExit(f"D38 gate row not PASS: {row}")

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
        raise SystemExit(f"D38 summary safety failed: {key}")

if summary.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D38 summary must require Lane C/E execution ownership")

if result.required_gate_count != 7:
    raise SystemExit(f"D38 expected 7 required gates, got {result.required_gate_count}")
if result.passed_gate_count != 7:
    raise SystemExit(f"D38 expected 7 passed gates, got {result.passed_gate_count}")
if result.missing_gate_count != 0:
    raise SystemExit(f"D38 expected zero missing gates, got {result.missing_gate_count}")
if result.failed_gate_count != 0:
    raise SystemExit(f"D38 expected zero failed gates, got {result.failed_gate_count}")
if result.unsafe_gate_count != 0:
    raise SystemExit(f"D38 expected zero unsafe gates, got {result.unsafe_gate_count}")
if result.candidate_count != 810:
    raise SystemExit(f"D38 expected 810 candidates, got {result.candidate_count}")
if result.handoff_row_count != 810:
    raise SystemExit(f"D38 expected 810 handoff rows, got {result.handoff_row_count}")
if result.handoff_ready_count != 810:
    raise SystemExit(f"D38 expected 810 handoff-ready rows, got {result.handoff_ready_count}")
if result.phase_status != "REPLAY_OPTIMIZATION_PHASE_READY_FOR_LANE_CE_HANDOFF_NO_EXECUTION":
    raise SystemExit(f"D38 unexpected phase status: {result.phase_status}")

next_batch = "LANE-D-D39_LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D38",
    "name": "replay_optimization_phase_gate_summary_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "REPLAY_OPTIMIZATION_PHASE_GATE_SUMMARY_NO_EXECUTION",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "phase_schema_path": result.phase_schema_path,
    "phase_summary_path": result.phase_summary_path,
    "phase_rows_json_path": result.phase_rows_json_path,
    "phase_rows_csv_path": result.phase_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "required_gate_count": result.required_gate_count,
    "passed_gate_count": result.passed_gate_count,
    "missing_gate_count": result.missing_gate_count,
    "failed_gate_count": result.failed_gate_count,
    "unsafe_gate_count": result.unsafe_gate_count,
    "candidate_count": result.candidate_count,
    "handoff_row_count": result.handoff_row_count,
    "handoff_ready_count": result.handoff_ready_count,
    "phase_status": result.phase_status,
    "summary": summary,
    "safety": {
        "phase_gate_summary_built": True,
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

proof_path = PROOF_DIR / f"proof_lane_d_d38_phase_gate_summary_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d38_phase_gate_summary_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d38_phase_gate_summary_{TS}.md"
milestone_path.write_text(
    "# LANE D D38 — Replay Optimization Phase Gate Summary\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D38 phase gate summary created and proved.\n\n"
    "## Phase Status\n\n"
    f"{result.phase_status}\n\n"
    "## Gate Counts\n\n"
    f"- Required gates: {result.required_gate_count}\n"
    f"- Passed gates: {result.passed_gate_count}\n"
    f"- Missing gates: {result.missing_gate_count}\n"
    f"- Failed gates: {result.failed_gate_count}\n"
    f"- Unsafe gates: {result.unsafe_gate_count}\n\n"
    "## Ownership\n\n"
    "Lane D is complete up to handoff. Future execution/materialization must be Lane C/E-owned.\n\n"
    "## Important Limitation\n\n"
    "D38 does not execute replay, create artifacts/result packs, attach candidate context, match trades, bind labels, calculate PnL, train/predict, or approve optimization.\n\n"
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
    "phase_schema_path": result.phase_schema_path,
    "phase_summary_path": result.phase_summary_path,
    "phase_rows_json_path": result.phase_rows_json_path,
    "phase_rows_csv_path": result.phase_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "required_gate_count": result.required_gate_count,
    "passed_gate_count": result.passed_gate_count,
    "missing_gate_count": result.missing_gate_count,
    "failed_gate_count": result.failed_gate_count,
    "unsafe_gate_count": result.unsafe_gate_count,
    "candidate_count": result.candidate_count,
    "handoff_row_count": result.handoff_row_count,
    "handoff_ready_count": result.handoff_ready_count,
    "phase_status": result.phase_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
