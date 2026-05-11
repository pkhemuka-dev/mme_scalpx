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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d14_grouped_precondition_audit_probe_{TS}"
PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
    "app/mme_scalpx/replay_optimization/precondition_audit.py",
    "app/mme_scalpx/replay_optimization/source_map_grouping.py",
    "app/mme_scalpx/replay_optimization/grouped_precondition_audit.py",
    "etc/replay_optimization/preconditions/grouped_source_map_precondition_contract.json",
    "bin/proof_replay_optimization_d14_grouped_precondition_audit.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
    "app/mme_scalpx/replay_optimization/precondition_audit.py",
    "app/mme_scalpx/replay_optimization/source_map_grouping.py",
    "app/mme_scalpx/replay_optimization/grouped_precondition_audit.py",
    "bin/proof_replay_optimization_d14_grouped_precondition_audit.py",
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
    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module:
                roots.append(node.module.split(".")[0])
            elif node.module:
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
    raise SystemExit(f"missing expected D14 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in [
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
    "app/mme_scalpx/replay_optimization/precondition_audit.py",
    "app/mme_scalpx/replay_optimization/source_map_grouping.py",
    "app/mme_scalpx/replay_optimization/grouped_precondition_audit.py",
]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {
            "contracts",
            "sweep_space",
            "result_indexer",
            "raw_indexer",
            "candidate_matrix",
            "leaderboard",
            "ml_dataset",
            "result_binding",
            "sample_risk",
            "implementation_gate",
            "source_map",
            "precondition_audit",
            "source_map_grouping",
            "grouped_precondition_audit",
        }:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

TEXT_AUDIT_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/contracts.py",
    "app/mme_scalpx/replay_optimization/sweep_space.py",
    "app/mme_scalpx/replay_optimization/profile_generator.py",
    "app/mme_scalpx/replay_optimization/result_indexer.py",
    "app/mme_scalpx/replay_optimization/raw_indexer.py",
    "app/mme_scalpx/replay_optimization/candidate_matrix.py",
    "app/mme_scalpx/replay_optimization/leaderboard.py",
    "app/mme_scalpx/replay_optimization/ml_dataset.py",
    "app/mme_scalpx/replay_optimization/result_binding.py",
    "app/mme_scalpx/replay_optimization/sample_risk.py",
    "app/mme_scalpx/replay_optimization/implementation_gate.py",
    "app/mme_scalpx/replay_optimization/source_map.py",
    "app/mme_scalpx/replay_optimization/precondition_audit.py",
    "app/mme_scalpx/replay_optimization/source_map_grouping.py",
    "app/mme_scalpx/replay_optimization/grouped_precondition_audit.py",
    "etc/replay_optimization/preconditions/grouped_source_map_precondition_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/preconditions/grouped_source_map_precondition_contract.json"])
if config["safety"]["replay_execution_allowed"] is not False:
    raise SystemExit("D14 config replay execution safety failed")
if config["safety"]["candidate_trade_matching_allowed"] is not False:
    raise SystemExit("D14 config candidate-trade matching safety failed")
if config["safety"]["label_binding_allowed"] is not False:
    raise SystemExit("D14 config label binding safety failed")
if config["safety"]["real_pnl_calculation_allowed"] is not False:
    raise SystemExit("D14 config PnL safety failed")
if config["safety"]["model_training_allowed"] is not False:
    raise SystemExit("D14 config training safety failed")
if config["safety"]["model_prediction_allowed"] is not False:
    raise SystemExit("D14 config prediction safety failed")
if config["safety"]["broker_calls_allowed"] is not False:
    raise SystemExit("D14 config broker safety failed")
if config["safety"]["live_redis_writes_allowed"] is not False:
    raise SystemExit("D14 config Redis safety failed")
if config["safety"]["paper_live_enablement_allowed"] is not False:
    raise SystemExit("D14 config paper/live safety failed")

audit_mod = importlib.import_module("app.mme_scalpx.replay_optimization.grouped_precondition_audit")

d13_latest = ROOT / "run" / "proofs" / "proof_lane_d_d13_source_map_grouping_latest.json"
grouped_source_map_path = latest_path_from_proof(d13_latest, "grouped_source_map_json_path")
grouping_report_path = latest_path_from_proof(d13_latest, "grouping_report_path")

optimization_id = f"D14_GROUPED_PRECONDITION_AUDIT_PROBE_{TS}"
result = audit_mod.write_grouped_precondition_audit(
    optimization_id,
    ARTIFACT_ROOT,
    grouped_source_map_path=grouped_source_map_path,
    grouping_report_path=grouping_report_path,
    max_rows=10000,
)

for path_value in [
    result.grouped_precondition_audit_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D14 output missing: {path_value}")

audit = load_json(Path(result.grouped_precondition_audit_path))
if audit.get("label_binding_allowed") is not False:
    raise SystemExit("D14 must not allow label binding")
if audit.get("labels_bound") is not False:
    raise SystemExit("D14 must not bind labels")
if audit.get("candidate_trade_matching_allowed") is not False:
    raise SystemExit("D14 must not allow candidate-trade matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D14 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D14 unexpectedly bound labels")
if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D14 unexpectedly allowed candidate-trade matching")
if result.replay_execution_performed is not False:
    raise SystemExit("D14 unexpectedly performed replay execution")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D14 unexpectedly calculated real PnL")
if result.model_training_performed is not False:
    raise SystemExit("D14 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D14 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D14 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D14 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D14 unexpectedly enabled paper/live")

if result.grouped_source_map_row_count != 810:
    raise SystemExit(f"D14 expected 810 grouped rows, got {result.grouped_source_map_row_count}")
if result.mixed_root_row_count != 0:
    raise SystemExit(f"D14 expected mixed_root_row_count=0, got {result.mixed_root_row_count}")
if result.complete_group_count != 0:
    raise SystemExit(f"D14 expected complete_group_count=0 from D13 evidence, got {result.complete_group_count}")
if result.precondition_status != "BLOCKED_INCOMPLETE_REPLAY_GROUP":
    raise SystemExit(f"D14 expected BLOCKED_INCOMPLETE_REPLAY_GROUP, got {result.precondition_status}")

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D14",
    "name": "grouped_source_map_precondition_audit_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "GROUPED_SOURCE_MAP_PRECONDITION_AUDIT_ONLY",
    "d13_dependency_observed": bool(grouped_source_map_path and grouping_report_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "grouped_source_map_path": grouped_source_map_path,
    "grouping_report_path": grouping_report_path,
    "grouped_precondition_audit_path": result.grouped_precondition_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "precondition_status": result.precondition_status,
    "grouped_source_map_row_count": result.grouped_source_map_row_count,
    "complete_group_count": result.complete_group_count,
    "mixed_root_row_count": result.mixed_root_row_count,
    "partial_row_count": result.partial_row_count,
    "audit": audit,
    "safety": {
        "grouped_precondition_audit_built": True,
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
    "next_recommended_batch": "LANE-D-D15_REPLAY_RESULT_PACK_DISCOVERY_AUDIT_NO_EXECUTION"
}

proof_path = PROOF_DIR / f"proof_lane_d_d14_grouped_precondition_audit_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d14_grouped_precondition_audit_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d14_grouped_precondition_audit_{TS}.md"
milestone_path.write_text(
    "# LANE D D14 — Grouped Source-Map Precondition Audit\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D14 grouped source-map precondition audit created and proved.\n\n"
    "## Precondition Status\n\n"
    f"`{result.precondition_status}`\n\n"
    "## Scope\n\n"
    "- Added `grouped_precondition_audit.py`.\n"
    "- Added grouped source-map precondition config.\n"
    "- Generated `17_grouped_source_map_precondition_audit.json`.\n"
    "- Generated `09_optimizer_verdict.json`.\n\n"
    "## Important Limitation\n\n"
    "D14 is audit-only. Mixed replay roots are repaired, but the selected grouped source map is incomplete. "
    "No candidate-to-trade matching, label binding, PnL calculation, training, prediction, or optimization approval occurred.\n\n"
    "## Safety\n\n"
    "- No replay execution.\n"
    "- No candidate-to-trade matching.\n"
    "- No label binding.\n"
    "- No real PnL calculation.\n"
    "- No model training.\n"
    "- No model prediction.\n"
    "- No broker calls.\n"
    "- No live Redis writes.\n"
    "- No paper/live enablement.\n"
    "- No runtime service start.\n"
    "- No strategy doctrine mutation.\n"
    "- No replay engine mutation.\n\n"
    "## Next\n\n"
    "LANE-D-D15: replay result pack discovery audit, no execution.\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "grouped_precondition_audit_path": result.grouped_precondition_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "precondition_status": result.precondition_status,
    "grouped_source_map_row_count": result.grouped_source_map_row_count,
    "complete_group_count": result.complete_group_count,
    "mixed_root_row_count": result.mixed_root_row_count,
    "partial_row_count": result.partial_row_count,
    "next": proof["next_recommended_batch"],
}, indent=2, sort_keys=True))
