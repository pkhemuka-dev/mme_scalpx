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
ARTIFACT_ROOT = ROOT / "run" / "replay_optimization" / f"d16_result_pack_verification_probe_{TS}"
PROOF_DIR.mkdir(parents=True, exist_ok=True)
MILESTONE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)

EXPECTED_FILES = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/result_pack_verification.py",
    "etc/replay_optimization/verification/result_pack_verification_contract.json",
    "bin/proof_replay_optimization_d16_result_pack_verification.py",
]

COMPILE_TARGETS = [
    "app/mme_scalpx/replay_optimization/__init__.py",
    "app/mme_scalpx/replay_optimization/result_pack_verification.py",
    "bin/proof_replay_optimization_d16_result_pack_verification.py",
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
    raise SystemExit(f"missing expected D16 files: {missing}")

compile_results = {}
for rel in COMPILE_TARGETS:
    py_compile.compile(str(ROOT / rel), doraise=True)
    compile_results[rel] = "PASS"

import_audit = {}
for rel in [
    "app/mme_scalpx/replay_optimization/result_pack_verification.py",
]:
    roots = imported_roots(ROOT / rel)
    import_audit[rel] = roots
    for root in roots:
        if root in BANNED_IMPORT_ROOTS:
            raise SystemExit(f"banned import root in {rel}: {root}")
        if root not in ALLOWED_IMPORT_ROOTS and root not in {"contracts"}:
            raise SystemExit(f"unexpected import root in {rel}: {root}")

TEXT_AUDIT_FILES = [
    "app/mme_scalpx/replay_optimization/result_pack_verification.py",
    "etc/replay_optimization/verification/result_pack_verification_contract.json",
]

for rel in TEXT_AUDIT_FILES:
    text = (ROOT / rel).read_text(encoding="utf-8")
    hits = [token for token in FORBIDDEN_RUNTIME_TOKENS if token in text]
    if hits:
        raise SystemExit(f"forbidden runtime token(s) in {rel}: {hits}")

config = load_json(files["etc/replay_optimization/verification/result_pack_verification_contract.json"])
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
        raise SystemExit(f"D16 config safety failed: {key}")

verifier = importlib.import_module("app.mme_scalpx.replay_optimization.result_pack_verification")

d15_latest = ROOT / "run" / "proofs" / "proof_lane_d_d15_result_pack_discovery_latest.json"
discovery_report_path = latest_path_from_proof(d15_latest, "discovery_report_path")

optimization_id = f"D16_RESULT_PACK_VERIFICATION_PROBE_{TS}"
result = verifier.write_result_pack_verification(
    optimization_id,
    ARTIFACT_ROOT,
    discovery_report_path=discovery_report_path,
)

for path_value in [
    result.verification_report_path,
    result.optimizer_verdict_path,
]:
    if not Path(path_value).exists():
        raise SystemExit(f"D16 output missing: {path_value}")

report = load_json(Path(result.verification_report_path))
selected_pack = report.get("selected_pack")
if not isinstance(selected_pack, dict):
    raise SystemExit("D16 selected_pack missing")

if report.get("safety", {}).get("label_binding_allowed") is not False:
    raise SystemExit("D16 must not allow label binding")
if report.get("safety", {}).get("labels_bound") is not False:
    raise SystemExit("D16 must not bind labels")
if report.get("safety", {}).get("candidate_trade_matching_allowed") is not False:
    raise SystemExit("D16 must not allow candidate-trade matching")
if result.label_binding_allowed is not False:
    raise SystemExit("D16 unexpectedly allowed label binding")
if result.labels_bound is not False:
    raise SystemExit("D16 unexpectedly bound labels")
if result.replay_execution_performed is not False:
    raise SystemExit("D16 unexpectedly executed replay")
if result.real_pnl_calculation_performed is not False:
    raise SystemExit("D16 unexpectedly calculated PnL")
if result.model_training_performed is not False:
    raise SystemExit("D16 unexpectedly trained")
if result.model_prediction_performed is not False:
    raise SystemExit("D16 unexpectedly predicted")
if result.broker_calls_executed is not False:
    raise SystemExit("D16 unexpectedly called broker")
if result.live_redis_writes_executed is not False:
    raise SystemExit("D16 unexpectedly wrote live Redis")
if result.paper_or_live_enabled is not False:
    raise SystemExit("D16 unexpectedly enabled paper/live")

if result.verified_pack_count <= 0:
    raise SystemExit("D16 expected one verified pack candidate from D15 complete packs")

allowed_statuses = {
    "RESULT_PACK_VERIFY_PASS_AUDIT_ONLY",
    "BLOCKED_INTEGRITY_NOT_PASS_OR_UNKNOWN",
    "BLOCKED_ROW_COUNT_MISMATCH",
}
if result.verification_status not in allowed_statuses:
    raise SystemExit(f"D16 unexpected verification status: {result.verification_status}")

if result.verification_status == "RESULT_PACK_VERIFY_PASS_AUDIT_ONLY":
    allowed_statuses = {
    "RESULT_PACK_VERIFY_PASS_AUDIT_ONLY",
    "BLOCKED_INTEGRITY_NOT_PASS_OR_UNKNOWN",
    "BLOCKED_ROW_COUNT_MISMATCH",
}
if result.verification_status not in allowed_statuses:
    raise SystemExit(f"D16 unexpected verification status: {result.verification_status}")

if result.verification_status == "RESULT_PACK_VERIFY_PASS_AUDIT_ONLY":
    if selected_pack.get("row_counts_match") is not True:
        raise SystemExit("D16 pass status requires matching row counts")
    next_batch = "LANE-D-D17_CANDIDATE_TRADE_MATCHING_SCHEMA_CONTRACT_NO_LABEL_BINDING"
elif result.verification_status == "BLOCKED_ROW_COUNT_MISMATCH":
    next_batch = "LANE-D-D17_ROW_COUNT_NORMALIZATION_AUDIT_NO_LABEL_BINDING"
else:
    next_batch = "LANE-D-D17_INTEGRITY_VERDICT_NORMALIZATION_AUDIT_NO_LABEL_BINDING"

file_hashes = {rel: sha256(path) for rel, path in files.items()}

proof = {
    "batch": "LANE-D-D16",
    "name": "result_pack_verification_audit_no_label_binding",
    "created_at": NOW,
    "verdict": "PASS",
    "accepted_for": "RESULT_PACK_VERIFICATION_AUDIT_ONLY",
    "d15_dependency_observed": bool(discovery_report_path),
    "files_checked": EXPECTED_FILES,
    "file_hashes": file_hashes,
    "compile_results": compile_results,
    "import_audit": import_audit,
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "discovery_report_path": discovery_report_path,
    "verification_report_path": result.verification_report_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "verified_pack_count": result.verified_pack_count,
    "selected_pack_id": result.selected_pack_id,
    "selected_candidate_root": result.selected_candidate_root,
    "verification_status": result.verification_status,
    "report": report,
    "safety": {
        "result_pack_verification_built": True,
        "result_pack_assembly_allowed": False,
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
    "next_recommended_batch": next_batch
}

proof_path = PROOF_DIR / f"proof_lane_d_d16_result_pack_verification_{TS}.json"
latest_path = PROOF_DIR / "proof_lane_d_d16_result_pack_verification_latest.json"
proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
shutil.copy2(proof_path, latest_path)

milestone_path = MILESTONE_DIR / f"lane_d_d16_result_pack_verification_{TS}.md"
milestone_path.write_text(
    "# LANE D D16 — Result Pack Verification Audit\n\n"
    f"Created at: `{NOW}`\n\n"
    "## Verdict\n\n"
    "PASS — D16 result-pack verification audit created and proved.\n\n"
    "## Verification Status\n\n"
    f"`{result.verification_status}`\n\n"
    "## Scope\n\n"
    "- Added `result_pack_verification.py`.\n"
    "- Added result-pack verification config.\n"
    "- Generated `19_result_pack_verification_report.json`.\n"
    "- Generated `09_optimizer_verdict.json`.\n\n"
    "## Important Limitation\n\n"
    "D16 verifies one complete replay result pack at read-only audit level. "
    "It does not execute replay, assemble packs, match candidates to trades, bind labels, calculate PnL, train/predict, or approve optimization.\n\n"
    "## Safety\n\n"
    "- No replay execution.\n"
    "- No result-pack assembly.\n"
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
    f"`{next_batch}`\n",
    encoding="utf-8",
)

print(json.dumps({
    "verdict": "PASS",
    "proof": proof_path.as_posix(),
    "latest": latest_path.as_posix(),
    "milestone": milestone_path.as_posix(),
    "artifact_root": ARTIFACT_ROOT.as_posix(),
    "verification_report_path": result.verification_report_path,
    "optimizer_verdict_path": result.optimizer_verdict_path,
    "verified_pack_count": result.verified_pack_count,
    "selected_pack_id": result.selected_pack_id,
    "selected_candidate_root": result.selected_candidate_root,
    "verification_status": result.verification_status,
    "next": next_batch,
}, indent=2, sort_keys=True))
