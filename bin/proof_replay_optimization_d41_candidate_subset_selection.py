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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d41_candidate_subset_selection_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement_validator.py",
    "app/mme_scalpx/replay_optimization/candidate_subset_selection.py",
    "etc/replay_optimization/handoff/candidate_subset_execution_handoff_contract.json",
    "bin/proof_replay_optimization_d41_candidate_subset_selection.py",
    "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json",
    "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json",
    "run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json",
    "run/proofs/proof_lane_d_d40_execution_package_requirement_validator_latest.json",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement.py",
    "app/mme_scalpx/replay_optimization/execution_package_requirement_validator.py",
    "app/mme_scalpx/replay_optimization/candidate_subset_selection.py",
    "bin/proof_replay_optimization_d41_candidate_subset_selection.py",
]

ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "csv",
    "dataclasses",
    "json",
    "pathlib",
    "typing",
}

BANNED_IMPORT_ROOTS = {
    "kiteconnect",
    "redis",
    "requests",
    "websocket",
    "subprocess",
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
    raise SystemExit(f"missing expected D41 dependency/target files: {missing}")

d32 = load_json(ROOT / "run/proofs/proof_lane_d_d32_candidate_replay_binding_plan_latest.json")
d37 = load_json(ROOT / "run/proofs/proof_lane_d_d37_lane_ce_handoff_latest.json")
d39 = load_json(ROOT / "run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json")
d40 = load_json(ROOT / "run/proofs/proof_lane_d_d40_execution_package_requirement_validator_latest.json")

if d32.get("verdict") != "PASS":
    raise SystemExit("D32 proof is not PASS")
if d37.get("verdict") != "PASS":
    raise SystemExit("D37 proof is not PASS")
if d39.get("verdict") != "PASS":
    raise SystemExit("D39 proof is not PASS")
if d40.get("verdict") != "PASS":
    raise SystemExit("D40 proof is not PASS")
if d32.get("candidate_count") != 810:
    raise SystemExit(f"D32 candidate_count expected 810, got {d32.get('candidate_count')}")
if d37.get("handoff_ready_count") != 810:
    raise SystemExit(f"D37 handoff_ready_count expected 810, got {d37.get('handoff_ready_count')}")
if d39.get("package_requirement_ready_count") != 810:
    raise SystemExit(f"D39 package_requirement_ready_count expected 810, got {d39.get('package_requirement_ready_count')}")
if d40.get("validated_row_count") != 810:
    raise SystemExit(f"D40 validated_row_count expected 810, got {d40.get('validated_row_count')}")
if d40.get("failed_row_count") != 0:
    raise SystemExit(f"D40 failed_row_count expected 0, got {d40.get('failed_row_count')}")
if d40.get("next_recommended_batch") != "LANE-D1-D41_CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION":
    raise SystemExit(f"D40 next batch does not point to D41: {d40.get('next_recommended_batch')}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/candidate_subset_selection.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/candidate_subset_selection.py",
    "etc/replay_optimization/handoff/candidate_subset_execution_handoff_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(ROOT / "etc/replay_optimization/handoff/candidate_subset_execution_handoff_contract.json")
safety = config["safety"]

if config.get("selection_policy", {}).get("full_universe_count") != 810:
    raise SystemExit("D41 contract full_universe_count must be 810")
if config.get("selection_policy", {}).get("subset_count") != 5:
    raise SystemExit("D41 contract subset_count must be 5")
if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D41 config must require Lane C/E execution")
if safety.get("full_universe_preserved") is not True:
    raise SystemExit("D41 config must preserve full universe")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "candidate_context_attached",
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "real_pnl_calculation_allowed",
    "real_pnl_calculation_performed",
    "model_training_allowed",
    "model_training_performed",
    "model_prediction_allowed",
    "model_prediction_performed",
    "broker_calls_allowed",
    "live_redis_writes_allowed",
    "runtime_services_allowed",
    "paper_live_enablement_allowed",
    "production_profit_claim_allowed",
]:
    if safety.get(key) is not False:
        raise SystemExit(f"D41 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.candidate_subset_selection")

selection_id = f"D41_FIRST5_LANE_CE_HANDOFF_{TS}"
result = mod.select_candidate_subset_for_execution_handoff(
    selection_id=selection_id,
    artifact_root=ARTIFACT_ROOT,
    root=ROOT,
    subset_count=5,
)

for path_value in [
    result.schema_path,
    result.summary_path,
    result.subset_rows_json_path,
    result.subset_rows_csv_path,
    result.handoff_manifest_json_path,
    result.handoff_manifest_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D41 output missing: {path_value}")

summary = load_json(Path(result.summary_path))
rows_payload = load_json(Path(result.subset_rows_json_path))
manifest = load_json(Path(result.handoff_manifest_json_path))
verdict = load_json(Path(result.optimizer_verdict_path))

rows = rows_payload.get("rows")
if verdict.get("verdict") != "PASS":
    raise SystemExit(f"D41 optimizer verdict not PASS: {verdict}")
if result.full_universe_count != 810:
    raise SystemExit(f"D41 result full_universe_count expected 810, got {result.full_universe_count}")
if result.subset_count != 5:
    raise SystemExit(f"D41 result subset_count expected 5, got {result.subset_count}")
if not isinstance(rows, list) or len(rows) != 5:
    raise SystemExit("D41 subset rows expected list of 5 rows")
if manifest.get("subset_count") != 5:
    raise SystemExit(f"D41 manifest subset_count expected 5, got {manifest.get('subset_count')}")
if manifest.get("full_universe_count") != 810:
    raise SystemExit(f"D41 manifest full_universe_count expected 810, got {manifest.get('full_universe_count')}")
if manifest.get("handoff_status") != "SUBSET_EXECUTION_HANDOFF_MANIFEST_READY_NO_EXECUTION":
    raise SystemExit(f"D41 bad handoff_status: {manifest.get('handoff_status')}")

seen_candidates = set()
for row in rows:
    if row.get("candidate_id") in seen_candidates:
        raise SystemExit(f"D41 duplicate candidate_id: {row.get('candidate_id')}")
    seen_candidates.add(row.get("candidate_id"))

    if row.get("subset_row_status") != "CANDIDATE_SUBSET_SELECTED_FOR_LANE_CE_EXECUTION_NO_EXECUTION":
        raise SystemExit(f"D41 row has bad status: {row}")
    if row.get("lane_c_or_e_execution_required") is not True:
        raise SystemExit(f"D41 row must require Lane C/E execution: {row}")
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
            raise SystemExit(f"D41 row safety failed {key}: {row}")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
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
        raise SystemExit(f"D41 summary safety failed: {key}")
if summary.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D41 summary must require Lane C/E execution")
if summary.get("safety", {}).get("full_universe_preserved") is not True:
    raise SystemExit("D41 summary must preserve full universe")

next_batch = "LANE-D1-D42_POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items() if path.exists()}

proof = {
    "batch": "LANE-D1-D41",
    "chat_lane": "Lane D1 only",
    "name": "candidate_subset_selection_execution_handoff_manifest_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CANDIDATE_SUBSET_SELECTION_EXECUTION_HANDOFF_MANIFEST_NO_EXECUTION",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "schema_path": result.schema_path,
    "summary_path": result.summary_path,
    "subset_rows_json_path": result.subset_rows_json_path,
    "subset_rows_csv_path": result.subset_rows_csv_path,
    "handoff_manifest_json_path": result.handoff_manifest_json_path,
    "handoff_manifest_csv_path": result.handoff_manifest_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "full_universe_count": result.full_universe_count,
    "full_universe_preserved": True,
    "subset_count": result.subset_count,
    "selected_candidate_ids": summary.get("selected_candidate_ids"),
    "handoff_status": result.handoff_status,
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
    "d39_dependency_observed": {
        "path": "run/proofs/proof_lane_d_d39_lane_ce_execution_package_requirement_latest.json",
        "verdict": d39.get("verdict"),
        "candidate_count": d39.get("candidate_count"),
        "package_requirement_row_count": d39.get("package_requirement_row_count"),
        "package_requirement_ready_count": d39.get("package_requirement_ready_count")
    },
    "d40_dependency_observed": {
        "path": "run/proofs/proof_lane_d_d40_execution_package_requirement_validator_latest.json",
        "verdict": d40.get("verdict"),
        "candidate_count": d40.get("candidate_count"),
        "validated_row_count": d40.get("validated_row_count"),
        "failed_row_count": d40.get("failed_row_count"),
        "validation_status": d40.get("validation_status")
    },
    "safety": {
        "candidate_subset_selected": True,
        "handoff_manifest_created": True,
        "full_universe_preserved": True,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed_in_lane_d": False,
        "result_pack_created": False,
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
    "important_limitation": "D41 selects first 5 candidates and creates a handoff manifest only. It does not execute replay, create real result packs, bind labels, calculate PnL, train/predict, or approve optimization.",
    "lane_ce_next_external_step": "Lane C/E may use D41 handoff manifest to execute/materialize only these five candidates under their lane ownership.",
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d41_candidate_subset_selection_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d41_candidate_subset_selection_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d1_d41_candidate_subset_selection_{TS}.md"
milestone_path.write_text(
    "# LANE D1 D41 — Candidate Subset Selection / Execution Handoff Manifest / No Execution\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — First 5-candidate subset selected and execution handoff manifest created.\n\n"
    "## Evidence Chain\n\n"
    "- D32 candidate replay binding plan PASS observed.\n"
    "- D37 Lane C/E handoff PASS observed.\n"
    "- D39 execution package requirement PASS observed.\n"
    "- D40 execution package requirement validator PASS observed.\n\n"
    "## Output\n\n"
    f"- Artifact root: `{ARTIFACT_ROOT.as_posix()}`\n"
    f"- Subset rows: `{result.subset_rows_json_path}`\n"
    f"- Handoff manifest: `{result.handoff_manifest_json_path}`\n"
    f"- Selected candidates: `{summary.get('selected_candidate_ids')}`\n\n"
    "## Safety\n\n"
    "- Full universe preserved: true / 810 candidates\n"
    "- First subset count: 5 candidates\n"
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
    "subset_rows_json_path": result.subset_rows_json_path,
    "subset_rows_csv_path": result.subset_rows_csv_path,
    "handoff_manifest_json_path": result.handoff_manifest_json_path,
    "handoff_manifest_csv_path": result.handoff_manifest_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "full_universe_count": result.full_universe_count,
    "subset_count": result.subset_count,
    "selected_candidate_ids": summary.get("selected_candidate_ids"),
    "handoff_status": result.handoff_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
