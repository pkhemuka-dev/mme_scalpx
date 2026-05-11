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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d23_matching_dry_run_probe_{TS}"

PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/matching_dry_run.py",
    "etc/replay_optimization/matching/matching_dry_run_contract.json",
    "bin/proof_replay_optimization_d23_matching_dry_run.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/matching_dry_run.py",
    "bin/proof_replay_optimization_d23_matching_dry_run.py",
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
    raise SystemExit(f"missing expected D23 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in ["app/mme_scalpx/replay_optimization/matching_dry_run.py"]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

for rel in [
    "app/mme_scalpx/replay_optimization/matching_dry_run.py",
    "etc/replay_optimization/matching/matching_dry_run_contract.json",
]:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/matching/matching_dry_run_contract.json"])
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
        raise SystemExit(f"D23 config safety failed: {key}")

mod = importlib.import_module("app.mme_scalpx.replay_optimization.matching_dry_run")

d20_latest = ROOT / "run" / "proofs" / "proof_lane_d_d20_candidate_trade_matching_schema_latest.json"
d22_latest = ROOT / "run" / "proofs" / "proof_lane_d_d22_match_key_discovery_latest.json"
d19_latest = ROOT / "run" / "proofs" / "proof_lane_d_d19_nonzero_pack_verification_latest.json"

matching_rows_path = latest_path_from_proof(d20_latest, "matching_rows_json_path")
match_key_discovery_path = latest_path_from_proof(d22_latest, "match_key_discovery_path")
nonzero_verification_report_path = latest_path_from_proof(d19_latest, "nonzero_verification_report_path")

optimization_id = f"D23_MATCHING_DRY_RUN_PROBE_{TS}"
result = mod.write_matching_dry_run(
    optimization_id,
    ARTIFACT_ROOT,
    matching_rows_path=matching_rows_path,
    match_key_discovery_path=match_key_discovery_path,
    nonzero_verification_report_path=nonzero_verification_report_path,
    max_rows=10000,
)

for path_value in [
    result.dry_run_report_path,
    result.dry_run_rows_json_path,
    result.dry_run_rows_csv_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D23 output missing: {path_value}")

report = load_json(Path(result.dry_run_report_path))
rows_payload = load_json(Path(result.dry_run_rows_json_path))
rows = rows_payload.get("rows")
if not isinstance(rows, list) or not rows:
    raise SystemExit("D23 dry-run rows missing")

sample_row = rows[0]
for key in [
    "candidate_trade_matching_performed",
    "label_binding_allowed",
    "labels_bound",
]:
    if sample_row.get(key) is not False:
        raise SystemExit(f"D23 sample row safety failed: {key}")

if sample_row.get("label_pnl") is not None:
    raise SystemExit("D23 must not bind label_pnl")
if result.candidate_trade_matching_performed is not False:
    raise SystemExit("D23 unexpectedly performed real matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D23 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D23 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D23 unexpectedly executed replay")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D23 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D23 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D23 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D23 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D23 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D23 unexpectedly enabled paper/live")

if result.dry_run_row_count != 810:
    raise SystemExit(f"D23 expected 810 dry-run rows, got {result.dry_run_row_count}")

allowed_statuses = {
    "BLOCKED_NO_DRY_RUN_KEYS",
    "BLOCKED_NO_DRY_RUN_ROWS",
    "DRY_RUN_WEAK_SIDE_ONLY_NOT_LABEL_READY",
    "DRY_RUN_DIAGNOSTIC_READY_NOT_LABEL_READY",
}
if result.dry_run_status not in allowed_statuses:
    raise SystemExit(f"D23 unexpected dry-run status: {result.dry_run_status}")

if result.weak_side_only:
    next_batch = "LANE-D-D24_MATCH_KEY_ADAPTER_SCHEMA_CONTRACT_NO_LABEL_BINDING"
else:
    next_batch = "LANE-D-D24_DRY_RUN_MATCH_QUALITY_AUDIT_NO_LABEL_BINDING"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D23",
    "name": "matching_dry_run_contract_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "MATCHING_DRY_RUN_DIAGNOSTIC_ONLY",
    "d20_dependency_observed": bool(matching_rows_path),
    "d22_dependency_observed": bool(match_key_discovery_path),
    "d19_dependency_observed": bool(nonzero_verification_report_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "matching_rows_path": matching_rows_path,
    "match_key_discovery_path": match_key_discovery_path,
    "nonzero_verification_report_path": nonzero_verification_report_path,
    "dry_run_report_path": result.dry_run_report_path,
    "dry_run_rows_json_path": result.dry_run_rows_json_path,
    "dry_run_rows_csv_path": result.dry_run_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "dry_run_row_count": result.dry_run_row_count,
    "dry_run_status": result.dry_run_status,
    "weak_side_only": result.weak_side_only,
    "sample_dry_run_row": sample_row,
    "report": report,
    "safety": {
        "matching_dry_run_built": True,
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

proof_path = PROOF_DIR / f"proof_lane_d_d23_matching_dry_run_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d23_matching_dry_run_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d23_matching_dry_run_{TS}.md"
milestone_path.write_text(
    "# LANE D D23 — Matching Dry-Run Contract\n\n"
    f"Created at: {NOW}\n\n"
    "## Verdict\n\n"
    "PASS — D23 matching dry-run diagnostic contract created and proved.\n\n"
    "## Dry-Run Status\n\n"
    f"{result.dry_run_status}\n\n"
    "## Important Limitation\n\n"
    "D23 is diagnostics-only. It does not perform real candidate-to-trade matching, bind labels, calculate PnL, train/predict, execute replay, or approve optimization.\n\n"
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
    "dry_run_report_path": result.dry_run_report_path,
    "dry_run_rows_json_path": result.dry_run_rows_json_path,
    "dry_run_rows_csv_path": result.dry_run_rows_csv_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "dry_run_row_count": result.dry_run_row_count,
    "dry_run_status": result.dry_run_status,
    "weak_side_only": result.weak_side_only,
    "next": next_batch,
}, indent=2, sort_keys=True))
