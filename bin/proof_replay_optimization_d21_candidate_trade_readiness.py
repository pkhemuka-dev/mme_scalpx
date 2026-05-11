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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d21_candidate_trade_readiness_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_trade_readiness.py",
    "etc/replay_optimization/matching/candidate_trade_matching_readiness_contract.json",
    "bin/proof_replay_optimization_d21_candidate_trade_readiness.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/candidate_trade_readiness.py",
    "bin/proof_replay_optimization_d21_candidate_trade_readiness.py",
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
    raise SystemExit(f"missing expected D21 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/candidate_trade_readiness.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/candidate_trade_readiness.py",
    "etc/replay_optimization/matching/candidate_trade_matching_readiness_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/matching/candidate_trade_matching_readiness_contract.json"])
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
        raise SystemExit(f"D21 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.candidate_trade_readiness")

d20_latest = ROOT / "run" / "proofs" / "proof_lane_d_d20_candidate_trade_matching_schema_latest.json"
d19_latest = ROOT / "run" / "proofs" / "proof_lane_d_d19_nonzero_pack_verification_latest.json"

matching_rows_path = latest_path_from_proof(d20_latest, "matching_rows_json_path")
nonzero_verification_report_path = latest_path_from_proof(d19_latest, "nonzero_verification_report_path")

optimization_id = f"D21_CANDIDATE_TRADE_READINESS_PROBE_{TS}"
result = mod.write_candidate_trade_readiness_audit(
    optimization_id,
    ARTIFACT_ROOT,
    matching_rows_path=matching_rows_path,
    nonzero_verification_report_path=nonzero_verification_report_path,
)

for path_value in [result.readiness_audit_path, result.optimizer_verdict_path]:
    if not Path(path_value).exists():
        raise SystemExit(f"D21 output missing: {path_value}")

audit = load_json(Path(result.readiness_audit_path))

for key in [
    "candidate_trade_matching_allowed",
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
    "replay_execution_performed",
    "real_pnl_calculation_performed",
    "model_training_performed",
    "model_prediction_performed",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
]:
    if audit.get(key) is not False:
        raise SystemExit(f"D21 audit safety failed: {key}")

if result.candidate_trade_matching_allowed is not False:
    raise SystemExit("D21 unexpectedly allowed matching")
if result.candidate_trade_matching_performed is not False:
    raise SystemExit("D21 unexpectedly performed matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D21 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D21 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D21 unexpectedly executed replay")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D21 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D21 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D21 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D21 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D21 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D21 unexpectedly enabled paper/live")

if result.matching_row_count != 810:
    raise SystemExit(f"D21 expected 810 matching rows, got {result.matching_row_count}")
if result.unmatched_row_count != 810:
    raise SystemExit(f"D21 expected all 810 rows unmatched, got {result.unmatched_row_count}")
if result.labels_bound_row_count != 0:
    raise SystemExit(f"D21 expected zero labels bound, got {result.labels_bound_row_count}")

allowed_statuses = {
    "BLOCKED_SCHEMA_ONLY_UNMATCHED_ROWS",
    "BLOCKED_RESULT_SCOPE_TOO_SMALL_FOR_810_CANDIDATES",
    "READY_FOR_MATCH_KEY_DISCOVERY_AUDIT_ONLY",
}
if result.readiness_status not in allowed_statuses:
    raise SystemExit(f"D21 unexpected readiness status: {result.readiness_status}")

next_batch = "LANE-D-D22_MATCH_KEY_DISCOVERY_AUDIT_NO_LABEL_BINDING"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D21",
    "name": "candidate_trade_matching_readiness_audit_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "CANDIDATE_TRADE_MATCHING_READINESS_AUDIT_ONLY",
    "d20_dependency_observed": bool(matching_rows_path),
    "d19_dependency_observed": bool(nonzero_verification_report_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "matching_rows_path": matching_rows_path,
    "nonzero_verification_report_path": nonzero_verification_report_path,
    "readiness_audit_path": result.readiness_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "readiness_status": result.readiness_status,
    "matching_row_count": result.matching_row_count,
    "unmatched_row_count": result.unmatched_row_count,
    "labels_bound_row_count": result.labels_bound_row_count,
    "audit": audit,
    "safety": {
        "candidate_trade_readiness_audit_built": True,
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

proof_path = PROOF_DIR / f"proof_lane_d_d21_candidate_trade_readiness_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d21_candidate_trade_readiness_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d21_candidate_trade_readiness_{TS}.md"
milestone_path.write_text(
    "# LANE D D21 — Candidate Trade Matching Readiness Audit\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D21 candidate-to-trade matching readiness audit created and proved.\n\n"
    "## Readiness Status\n\n"
    f"{result.readiness_status}\n\n"
    "## Important Limitation\n\n"
    "D21 is audit-only. It does not match candidates to trades, bind labels, calculate PnL, train/predict, execute replay, or approve optimization.\n\n"
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
    "readiness_audit_path": result.readiness_audit_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "readiness_status": result.readiness_status,
    "matching_row_count": result.matching_row_count,
    "unmatched_row_count": result.unmatched_row_count,
    "labels_bound_row_count": result.labels_bound_row_count,
    "next": next_batch,
}, indent=2, sort_keys=True))
