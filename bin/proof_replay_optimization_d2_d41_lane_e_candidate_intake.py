#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import py_compile
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd().resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
NOW = datetime.now(timezone.utc).isoformat()
PROOF_DIR = ROOT / "run" / "proofs"
MILESTONE_DIR = ROOT / "docs" / "milestones"
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d2_d41_r2_lane_e_candidate_intake_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/lane_e_candidate_intake.py",
    "etc/replay_optimization/handoff/lane_e_candidate_materialization_intake_contract.json",
    "bin/proof_replay_optimization_d2_d41_lane_e_candidate_intake.py",
    "docs/runbooks/LANE_D2_D41_LANE_E_CANDIDATE_MATERIALIZATION_INTAKE_RUNBOOK.md",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/lane_e_candidate_intake.py",
    "bin/proof_replay_optimization_d2_d41_lane_e_candidate_intake.py",
]

BANNED_IMPORT_ROOTS = {"redis", "requests", "websocket", "kiteconnect", "pandas", "numpy", "sklearn", "xgboost", "lightgbm", "subprocess"}
FORBIDDEN_TEXT = ["KiteConnect(", "DhanHQ(", "place_order(", ".place_order(", "redis.Redis(", ".xadd(", "subprocess.Popen(", "app.mme_scalpx.main"]
UNSAFE_TRUE_KEYS = {
    "broker_calls_executed", "broker_calls_allowed",
    "live_redis_writes_executed", "live_redis_writes_allowed",
    "paper_or_live_enabled", "paper_live_enablement_allowed",
    "runtime_services_started", "runtime_service_start_allowed",
    "replay_execution_performed", "replay_execution_allowed",
    "result_pack_created", "result_pack_creation_allowed",
    "labels_bound", "label_binding_allowed",
    "real_pnl_calculation_performed", "real_pnl_calculation_allowed",
    "model_training_performed", "model_training_allowed",
    "prediction_performed", "production_profit_claim_allowed",
    "strategy_doctrine_changed", "replay_engine_changed",
}

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def imported_roots(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.append(node.module.split(".")[0])
    return sorted(set(roots))

def walk_unsafe(obj: Any, prefix: str = "") -> list[str]:
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            if k in UNSAFE_TRUE_KEYS and v is True:
                hits.append(p)
            hits.extend(walk_unsafe(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(walk_unsafe(v, f"{prefix}[{i}]"))
    return hits

def load_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location("lane_e_candidate_intake_d2d41", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["lane_e_candidate_intake_d2d41"] = mod
    spec.loader.exec_module(mod)
    return mod

missing = [rel for rel in FILES if not (ROOT / rel).exists()]
if missing:
    raise SystemExit(f"missing D2-D41 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/lane_e_candidate_intake.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    banned = sorted(set(roots) & BANNED_IMPORT_ROOTS)
    if banned:
        raise SystemExit(f"banned import roots in {rel}: {banned}")

for rel in [
    "app/mme_scalpx/replay_optimization/lane_e_candidate_intake.py",
    "etc/replay_optimization/handoff/lane_e_candidate_materialization_intake_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_TEXT if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

proof_paths = {
    "D37": ROOT / "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json",
    "D39": ROOT / "run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json",
    "D40": ROOT / "run/proofs/proof_lane_d_d40_lane_d_freeze_summary_latest.json",
}

source_proofs = {}
for label, path in proof_paths.items():
    if not path.exists():
        raise SystemExit(f"missing predecessor proof {label}: {path}")
    data = load_json(path)
    source_proofs[label] = data
    if data.get("verdict") != "PASS":
        raise SystemExit(f"{label} proof is not PASS: {data.get('verdict')}")
    unsafe = walk_unsafe(data)
    if unsafe:
        raise SystemExit(f"{label} proof has unsafe true flags: {unsafe[:20]}")

if source_proofs["D37"].get("handoff_ready_count") != 810:
    raise SystemExit(f"D37 expected handoff_ready_count=810, got {source_proofs['D37'].get('handoff_ready_count')}")
if source_proofs["D37"].get("handoff_status") != "LANE_CE_HANDOFF_READY_NO_EXECUTION":
    raise SystemExit(f"D37 unexpected handoff_status={source_proofs['D37'].get('handoff_status')}")

d40 = source_proofs["D40"]
if d40.get("freeze_status") != "LANE_D_REPLAY_OPTIMIZATION_FREEZE_COMPLETE_NO_EXECUTION":
    raise SystemExit(f"D40 unexpected freeze_status={d40.get('freeze_status')}")

summary = d40.get("summary") if isinstance(d40.get("summary"), dict) else {}
rows = summary.get("rows") if isinstance(summary.get("rows"), list) else []
d39_rows = [r for r in rows if isinstance(r, dict) and r.get("batch") == "D39"]
if not d39_rows:
    raise SystemExit("D40 freeze summary missing D39 row")
d39_row = d39_rows[0]
if d39_row.get("proof_verdict") != "PASS":
    raise SystemExit(f"D40 D39 row proof_verdict not PASS: {d39_row.get('proof_verdict')}")
if d39_row.get("freeze_row_status") != "PASS":
    raise SystemExit(f"D40 D39 row freeze_row_status not PASS: {d39_row.get('freeze_row_status')}")
if d39_row.get("observed_status") != "LANE_CE_EXECUTION_PACKAGE_REQUIREMENT_READY_NO_EXECUTION":
    raise SystemExit(f"D40 D39 row observed_status unexpected: {d39_row.get('observed_status')}")
if d39_row.get("safety_ok") is not True:
    raise SystemExit(f"D40 D39 row safety_ok not true: {d39_row.get('safety_ok')}")

config = load_json(ROOT / "etc/replay_optimization/handoff/lane_e_candidate_materialization_intake_contract.json")
for key in [
    "lane_d2_execution_allowed", "lane_d_execution_allowed", "replay_execution_allowed",
    "result_pack_creation_allowed", "candidate_replay_artifact_file_creation_allowed",
    "candidate_context_attachment_allowed", "candidate_trade_matching_allowed",
    "label_binding_allowed", "real_pnl_calculation_allowed", "model_training_allowed",
    "model_prediction_allowed", "broker_calls_allowed", "live_redis_writes_allowed",
    "paper_live_enablement_allowed", "runtime_service_start_allowed",
    "strategy_doctrine_mutation_allowed", "replay_engine_mutation_allowed",
    "production_claim_allowed",
]:
    if config["safety"].get(key) is not False:
        raise SystemExit(f"config safety key must be false: {key}")

if config["safety"].get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("config must require Lane C/E execution ownership")

mod = load_module_from_path(ROOT / "app/mme_scalpx/replay_optimization/lane_e_candidate_intake.py")
subset_manifest = os.environ.get("LANE_D1_SUBSET_MANIFEST", "").strip() or None

result = mod.write_lane_e_candidate_materialization_intake_contract(
    f"D2_D41_R2_LANE_E_CANDIDATE_INTAKE_PROBE_{TS}",
    ARTIFACT_ROOT,
    d1_subset_manifest_path=subset_manifest,
)

for path_text in [
    result.intake_schema_path,
    result.intake_requirements_path,
    result.intake_checklist_json_path,
    result.intake_checklist_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_text).exists():
        raise SystemExit(f"missing generated D2-D41 artifact: {path_text}")

for attr in [
    "replay_execution_performed", "result_pack_created", "labels_bound",
    "real_pnl_calculation_performed", "model_training_performed",
    "model_prediction_performed", "broker_calls_executed",
    "live_redis_writes_executed", "paper_or_live_enabled",
    "runtime_services_started", "strategy_doctrine_changed",
    "replay_engine_changed", "production_profit_claim_allowed",
]:
    if getattr(result, attr) is not False:
        raise SystemExit(f"unsafe result flag not false: {attr}")

if result.source_candidate_count != 810:
    raise SystemExit(f"expected source_candidate_count=810, got {result.source_candidate_count}")
if result.recommended_initial_subset_size != 5:
    raise SystemExit(f"expected recommended_initial_subset_size=5, got {result.recommended_initial_subset_size}")
if result.lane_e_execution_required is not True:
    raise SystemExit("Lane E execution requirement not declared")
if result.lane_c_stop_rule_declared is not True:
    raise SystemExit("Lane C stop rule not declared")

proof = {
    "batch": "LANE-D2-D41-R2",
    "name": "lane_e_candidate_materialization_intake_contract_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "LANE_E_CANDIDATE_MATERIALIZATION_INTAKE_CONTRACT_NO_EXECUTION",
    "files_checked": FILES,
    "file_hashes": {rel: sha256(ROOT / rel) for rel in FILES},
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "source_proofs": {label: path.as_posix() for label, path in proof_paths.items()},
    "d39_status_validated_via_d40_freeze_row": True,
    "d39_d40_row": d39_row,
    "intake_status": result.intake_status,
    "source_candidate_count": result.source_candidate_count,
    "recommended_initial_subset_size": result.recommended_initial_subset_size,
    "d1_subset_manifest_path": subset_manifest,
    "subset_manifest_observed": result.subset_manifest_observed,
    "subset_validation_status": result.subset_validation_status,
    "selected_candidate_count": result.selected_candidate_count,
    "intake_schema_path": result.intake_schema_path,
    "intake_requirements_path": result.intake_requirements_path,
    "intake_checklist_json_path": result.intake_checklist_json_path,
    "intake_checklist_csv_path": result.intake_checklist_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "safety": {
        "intake_contract_built": True,
        "candidate_selection_performed_by_d2": False,
        "lane_e_execution_required": True,
        "lane_c_stop_rule_declared": True,
        "replay_execution_performed": False,
        "result_pack_created": False,
        "labels_bound": False,
        "real_pnl_calculation_performed": False,
        "model_training_performed": False,
        "model_prediction_performed": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
        "runtime_services_started": False,
        "strategy_doctrine_changed": False,
        "replay_engine_changed": False,
        "production_profit_claim_allowed": False
    },
    "next_recommended_batch": "LANE-D2-D42_LANE_E_SUBSET_INTAKE_VALIDATOR_NO_EXECUTION_AFTER_D1_SUBSET"
}

proof_path = PROOF_DIR / f"proof_lane_d2_d41_lane_e_candidate_materialization_intake_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d2_d41_lane_e_candidate_materialization_intake_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d2_d41_lane_e_candidate_materialization_intake_{TS}.md"
milestone_path.write_text(
    "# LANE D2 D41-R2 — Lane E Candidate Materialization Intake Contract\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — Lane E candidate materialization intake contract created and proved.\n\n"
    "## R2 Correction\n\n"
    "D39 status was validated through the D40 freeze-summary D39 row because the D39 proof did not expose package_status as a top-level field.\n\n"
    "## Status\n\n"
    f"{result.intake_status}\n\n"
    "## Evidence\n\n"
    "- D37 PASS observed.\n"
    "- D39 PASS observed.\n"
    "- D40 PASS observed.\n"
    "- D40 D39 row PASS observed.\n"
    "- 810 source candidates preserved.\n"
    "- Recommended first D1 subset size: 5.\n\n"
    "## Safety\n\n"
    "- No replay executed.\n"
    "- No result pack created.\n"
    "- No labels bound.\n"
    "- No PnL calculated.\n"
    "- No ML trained or predicted.\n"
    "- No broker calls.\n"
    "- No live Redis writes.\n"
    "- No paper/live enabled.\n"
    "- No runtime services started.\n"
    "- No replay engine or strategy doctrine changed.\n\n"
    "## Next\n\n"
    "LANE-D2-D42_LANE_E_SUBSET_INTAKE_VALIDATOR_NO_EXECUTION_AFTER_D1_SUBSET\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "intake_status": result.intake_status,
    "source_candidate_count": result.source_candidate_count,
    "recommended_initial_subset_size": result.recommended_initial_subset_size,
    "subset_validation_status": result.subset_validation_status,
    "d39_status_validated_via_d40_freeze_row": True,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
