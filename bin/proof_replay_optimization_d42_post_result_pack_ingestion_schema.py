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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d42_post_result_pack_ingestion_schema_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_subset_selection.py",
    "app/mme_scalpx/replay_optimization/result_pack_ingestion_schema.py",
    "etc/replay_optimization/handoff/candidate_subset_execution_handoff_contract.json",
    "etc/replay_optimization/ingestion/post_result_pack_ingestion_schema_contract.json",
    "bin/proof_replay_optimization_d41_candidate_subset_selection.py",
    "bin/proof_replay_optimization_d42_post_result_pack_ingestion_schema.py",
    "run/proofs/proof_lane_d_d41_candidate_subset_selection_latest.json",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_subset_selection.py",
    "app/mme_scalpx/replay_optimization/result_pack_ingestion_schema.py",
    "bin/proof_replay_optimization_d42_post_result_pack_ingestion_schema.py",
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
    raise SystemExit(f"missing expected D42 dependency/target files: {missing}")

d41_path = ROOT / "run/proofs/proof_lane_d_d41_candidate_subset_selection_latest.json"
d41 = load_json(d41_path)

if d41.get("verdict") != "PASS":
    raise SystemExit("D41 proof is not PASS")
if d41.get("batch") != "LANE-D1-D41":
    raise SystemExit(f"unexpected D41 batch: {d41.get('batch')}")
if d41.get("full_universe_count") != 810:
    raise SystemExit(f"D41 full_universe_count expected 810, got {d41.get('full_universe_count')}")
if d41.get("full_universe_preserved") is not True:
    raise SystemExit("D41 did not preserve full universe")
if d41.get("subset_count") != 5:
    raise SystemExit(f"D41 subset_count expected 5, got {d41.get('subset_count')}")
if d41.get("handoff_status") != "SUBSET_EXECUTION_HANDOFF_MANIFEST_READY_NO_EXECUTION":
    raise SystemExit(f"D41 handoff_status unexpected: {d41.get('handoff_status')}")
if d41.get("next_recommended_batch") != "LANE-D1-D42_POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION":
    raise SystemExit(f"D41 next batch does not point to D42: {d41.get('next_recommended_batch')}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/result_pack_ingestion_schema.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/result_pack_ingestion_schema.py",
    "etc/replay_optimization/ingestion/post_result_pack_ingestion_schema_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(ROOT / "etc/replay_optimization/ingestion/post_result_pack_ingestion_schema_contract.json")
safety = config["safety"]

if config.get("expected_full_universe_count") != 810:
    raise SystemExit("D42 contract expected_full_universe_count must be 810")
if config.get("expected_subset_count") != 5:
    raise SystemExit("D42 contract expected_subset_count must be 5")
if safety.get("schema_only") is not True:
    raise SystemExit("D42 config must be schema_only=true")
if safety.get("full_universe_preserved") is not True:
    raise SystemExit("D42 config must preserve full universe")
if safety.get("subset_preserved") is not True:
    raise SystemExit("D42 config must preserve subset")
if safety.get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D42 config must require Lane C/E execution")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "result_pack_exists_checked",
    "result_pack_verified",
    "result_pack_ingestion_performed",
    "candidate_result_verified",
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
        raise SystemExit(f"D42 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.result_pack_ingestion_schema")

schema_id = f"D42_POST_RESULT_PACK_INGESTION_SCHEMA_{TS}"
result = mod.write_post_result_pack_ingestion_schema(
    schema_id=schema_id,
    artifact_root=ARTIFACT_ROOT,
    root=ROOT,
)

for path_value in [
    result.ingestion_schema_path,
    result.acceptance_requirements_path,
    result.ingestion_summary_path,
    result.label_binding_precondition_stub_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D42 output missing: {path_value}")

ingestion_schema = load_json(Path(result.ingestion_schema_path))
acceptance = load_json(Path(result.acceptance_requirements_path))
summary = load_json(Path(result.ingestion_summary_path))
label_stub = load_json(Path(result.label_binding_precondition_stub_path))
verdict = load_json(Path(result.optimizer_verdict_path))

if verdict.get("verdict") != "PASS":
    raise SystemExit(f"D42 optimizer verdict not PASS: {verdict}")
if result.full_universe_count != 810:
    raise SystemExit(f"D42 full_universe_count expected 810, got {result.full_universe_count}")
if result.subset_count != 5:
    raise SystemExit(f"D42 subset_count expected 5, got {result.subset_count}")
if result.schema_status != "POST_RESULT_PACK_INGESTION_SCHEMA_READY_NO_EXECUTION":
    raise SystemExit(f"D42 schema_status unexpected: {result.schema_status}")

rows = acceptance.get("ingestion_requirements")
if not isinstance(rows, list) or len(rows) != 5:
    raise SystemExit("D42 acceptance requirements expected 5 rows")

for row in rows:
    if row.get("ingestion_row_status") != "RESULT_PACK_INGESTION_REQUIREMENT_READY_NO_INGESTION":
        raise SystemExit(f"D42 bad row status: {row}")
    if row.get("lane_c_or_e_execution_required") is not True:
        raise SystemExit(f"D42 row must require Lane C/E execution: {row}")
    for key in [
        "lane_d_execution_allowed",
        "result_pack_exists_checked",
        "result_pack_verified",
        "result_pack_ingestion_performed",
        "candidate_result_verified",
        "label_binding_allowed",
        "labels_bound",
        "real_pnl_calculation_performed",
        "model_training_performed",
        "model_prediction_performed",
    ]:
        if row.get(key) is not False:
            raise SystemExit(f"D42 row safety failed {key}: {row}")

if summary.get("schema_status") != "POST_RESULT_PACK_INGESTION_SCHEMA_READY_NO_EXECUTION":
    raise SystemExit(f"D42 summary schema_status unexpected: {summary.get('schema_status')}")
if summary.get("result_pack_verified_count") != 0:
    raise SystemExit(f"D42 summary result_pack_verified_count expected 0, got {summary.get('result_pack_verified_count')}")
if summary.get("result_pack_ingestion_performed") is not False:
    raise SystemExit("D42 must not perform result-pack ingestion")
if summary.get("label_binding_allowed") is not False:
    raise SystemExit("D42 must keep label binding blocked")
if label_stub.get("label_binding_allowed") is not False:
    raise SystemExit("D42 label stub must block label binding")
if label_stub.get("current_verified_result_pack_count") != 0:
    raise SystemExit("D42 label stub current_verified_result_pack_count must be 0")

for key in [
    "lane_d_execution_allowed",
    "replay_execution_allowed",
    "replay_execution_performed",
    "result_pack_creation_allowed_in_lane_d",
    "result_pack_created",
    "result_pack_exists_checked",
    "result_pack_verified",
    "result_pack_ingestion_performed",
    "candidate_result_verified",
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
        raise SystemExit(f"D42 summary safety failed: {key}")
if summary.get("safety", {}).get("schema_only") is not True:
    raise SystemExit("D42 summary must be schema_only")
if summary.get("safety", {}).get("lane_c_or_e_execution_required") is not True:
    raise SystemExit("D42 summary must require Lane C/E execution")

next_batch = "LANE-D1-D43_LABEL_BINDING_PRECONDITION_VALIDATOR_NO_EXECUTION"

file_hashes = {rel: sha256(path) for rel, path in files.items() if path.exists()}

proof = {
    "batch": "LANE-D1-D42",
    "chat_lane": "Lane D1 only",
    "name": "post_result_pack_ingestion_schema_no_execution",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "POST_RESULT_PACK_INGESTION_SCHEMA_NO_EXECUTION",
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "ingestion_schema_path": result.ingestion_schema_path,
    "acceptance_requirements_path": result.acceptance_requirements_path,
    "ingestion_summary_path": result.ingestion_summary_path,
    "label_binding_precondition_stub_path": result.label_binding_precondition_stub_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "full_universe_count": result.full_universe_count,
    "full_universe_preserved": True,
    "subset_count": result.subset_count,
    "selected_candidate_ids": summary.get("selected_candidate_ids"),
    "schema_status": result.schema_status,
    "d41_dependency_observed": {
        "path": d41_path.as_posix(),
        "verdict": d41.get("verdict"),
        "batch": d41.get("batch"),
        "full_universe_count": d41.get("full_universe_count"),
        "full_universe_preserved": d41.get("full_universe_preserved"),
        "subset_count": d41.get("subset_count"),
        "handoff_status": d41.get("handoff_status"),
        "next_recommended_batch": d41.get("next_recommended_batch")
    },
    "safety": {
        "post_result_pack_ingestion_schema_created": True,
        "acceptance_requirements_created": True,
        "label_binding_precondition_stub_created": True,
        "schema_only": True,
        "full_universe_preserved": True,
        "subset_preserved": True,
        "lane_d_execution_allowed": False,
        "lane_c_or_e_execution_required": True,
        "replay_execution_allowed": False,
        "replay_execution_performed": False,
        "result_pack_creation_allowed_in_lane_d": False,
        "result_pack_created": False,
        "result_pack_exists_checked": False,
        "result_pack_verified": False,
        "result_pack_ingestion_performed": False,
        "candidate_result_verified": False,
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
    "important_limitation": "D42 freezes post-result-pack ingestion schemas only. It does not inspect, ingest, validate, create, or accept real candidate result packs.",
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d42_post_result_pack_ingestion_schema_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d42_post_result_pack_ingestion_schema_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d1_d42_post_result_pack_ingestion_schema_{TS}.md"
milestone_path.write_text(
    "# LANE D1 D42 — Post Result-Pack Ingestion Schema / No Execution\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — Post-result-pack ingestion schema and acceptance requirements frozen for the D41 five-candidate subset.\n\n"
    "## Evidence Chain\n\n"
    "- D41 candidate subset selection PASS observed.\n"
    "- 810-candidate full universe preserved.\n"
    "- 5-candidate first subset preserved.\n"
    "- D41 handoff manifest observed.\n\n"
    "## Output\n\n"
    f"- Artifact root: `{ARTIFACT_ROOT.as_posix()}`\n"
    f"- Ingestion schema: `{result.ingestion_schema_path}`\n"
    f"- Acceptance requirements: `{result.acceptance_requirements_path}`\n"
    f"- Label-binding precondition stub: `{result.label_binding_precondition_stub_path}`\n"
    f"- Selected candidates: `{summary.get('selected_candidate_ids')}`\n\n"
    "## Safety\n\n"
    "- Schema only: true\n"
    "- Replay execution performed: false\n"
    "- Result pack created: false\n"
    "- Result pack checked/verified/ingested: false\n"
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
    "ingestion_schema_path": result.ingestion_schema_path,
    "acceptance_requirements_path": result.acceptance_requirements_path,
    "ingestion_summary_path": result.ingestion_summary_path,
    "label_binding_precondition_stub_path": result.label_binding_precondition_stub_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "full_universe_count": result.full_universe_count,
    "subset_count": result.subset_count,
    "selected_candidate_ids": summary.get("selected_candidate_ids"),
    "schema_status": result.schema_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
