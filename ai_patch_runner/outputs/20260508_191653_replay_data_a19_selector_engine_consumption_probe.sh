#!/usr/bin/env bash
set -euo pipefail

export SCALPX_OBSERVE_ONLY=1
unset SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME || true
unset SCALPX_CONTROLLED_PAPER_SCOPE_ACK || true
unset SCALPX_REAL_LIVE_ALLOWED || true
unset SCALPX_ALLOW_REAL_LIVE || true
unset SCALPX_LIVE || true
unset SCALPX_PAPER || true
unset LIVE_TRADING || true
unset PAPER_TRADING || true
unset REDIS_URL || true
unset BROKER_LOGIN || true
unset BROKER_TOKEN || true

# REPLAY-DATA-A19
# selector_engine_consumption_compatibility_probe
# consumption_probe_ok
# selector_consumption_candidate
# engine_consumption_candidate
# engine_ready_candidate
# proof_replay_data_a19_selector_engine_consumption_probe
# SCALPX_OBSERVE_ONLY=1
# engine_execution_performed=false
# broker_calls_executed=false
# live_redis_writes_executed=false
# paper_or_live_enabled=false
# orders_sent=false

.venv/bin/python - <<'PY'
from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
A18_PROOF = ROOT / "run/proofs/proof_replay_data_a18_execution_shadow_semantic_normalization_20260508T191103Z.json"

def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except Exception:
        return str(p)

def sha256(path: Path):
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def read_text(path: Path, limit=600000):
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")[:limit]

def py_parse_status(path: Path):
    if not path.exists():
        return {"exists": False, "parse_ok": False, "error": "missing"}
    try:
        ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return {"exists": True, "parse_ok": True, "error": None, "sha256": sha256(path), "size_bytes": path.stat().st_size}
    except Exception as exc:
        return {"exists": True, "parse_ok": False, "error": repr(exc), "sha256": sha256(path), "size_bytes": path.stat().st_size}

def csv_info(path: Path, sample_n=3):
    if not path.exists():
        return {"exists": False, "header": [], "row_count": 0, "sample_rows": [], "sha256": None}
    rows = []
    count = 0
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        rdr = csv.DictReader(f)
        header = list(rdr.fieldnames or [])
        for row in rdr:
            if count < sample_n:
                rows.append({k: row.get(k, "") for k in header[:60]})
            count += 1
    return {"exists": True, "header": header, "row_count": count, "sample_rows": rows, "sha256": sha256(path)}

a18 = load_json(A18_PROOF)
a18_summary = a18.get("summary") or {}

canonical_root = a18.get("canonical_root") or "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z"
source_date = a18.get("source_date") or "2026-04-17"
date_dir = ROOT / canonical_root / source_date

surface_files = [
    "quote_ticks_mme_fut_stream.csv",
    "quote_ticks_mme_opt_stream.csv",
    "features_rows_candidate.csv",
    "strategy_decisions_candidate.csv",
    "risk_outputs_candidate.csv",
    "execution_shadow_candidate.csv",
]

surface_info = {name: csv_info(date_dir / name) for name in surface_files}

replay_files = [
    "app/mme_scalpx/replay/contracts.py",
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/selectors.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/runner.py",
    "app/mme_scalpx/replay/topology.py",
    "bin/replay_run.py",
]

source_status = {rf: py_parse_status(ROOT / rf) for rf in replay_files}
combined = "\n\n".join(f"### {rf}\n{read_text(ROOT / rf)}" for rf in replay_files)

required_quote_cols = {"ts_event", "symbol", "bid", "ask"}
required_feature_cols = {"ts_event", "symbol"}
required_strategy_cols = {"ts_event", "symbol", "decision", "action"}
required_risk_cols = {"ts_event", "symbol", "risk_allowed", "order_intent"}
required_exec_cols = {
    "ts_event",
    "symbol",
    "execution_action",
    "execution_status",
    "orders_sent",
    "broker_calls_executed",
    "live_redis_writes_executed",
    "paper_or_live_enabled",
    "engine_execution_performed",
    "shadow_reconstruction",
}

surface_requirements = {
    "quote_ticks_mme_fut_stream.csv": required_quote_cols,
    "quote_ticks_mme_opt_stream.csv": required_quote_cols,
    "features_rows_candidate.csv": required_feature_cols,
    "strategy_decisions_candidate.csv": required_strategy_cols,
    "risk_outputs_candidate.csv": required_risk_cols,
    "execution_shadow_candidate.csv": required_exec_cols,
}

surface_compatibility = {}
blockers = []

for name, required in surface_requirements.items():
    info = surface_info[name]
    header = set(info.get("header") or [])
    missing = sorted(required - header)
    ok = info.get("exists") is True and info.get("row_count", 0) > 0 and not missing
    surface_compatibility[name] = {
        "exists": info.get("exists"),
        "row_count": info.get("row_count"),
        "required_columns": sorted(required),
        "missing_columns": missing,
        "compatible": ok,
    }
    if not ok:
        blockers.append({
            "kind": "schema_header_blocker",
            "surface": name,
            "message": "Surface missing required consumption columns or rows.",
            "details": surface_compatibility[name],
        })

selector_terms = {
    "quote_only_recorded": "quote_only_recorded" in combined,
    "required_file_stems": "required_file_stems" in combined,
    "supported_suffixes": "supported_suffixes" in combined,
    "single_day": "single_day" in combined,
    "available_dates": "available_dates" in combined,
    "ts_event_required": "ts_event" in combined,
    "bid_ask_required": "bid" in combined and "ask" in combined,
}

engine_terms = {
    "features_rows": "features_rows" in combined,
    "strategy_decisions": "strategy_decisions" in combined,
    "risk_outputs": "risk_outputs" in combined,
    "execution_shadow": "execution_shadow" in combined,
    "feeds_features_strategy_risk_execution_shadow": "feeds_features_strategy_risk_execution_shadow" in combined,
    "engine_run_function_present": bool(re.search(r"def\s+(run|execute|replay)", combined)),
}

support_files = {
    "dataset_manifest.json": ROOT / canonical_root / "dataset_manifest.json",
    "selector_available_dates.json": ROOT / canonical_root / "selector_available_dates.json",
    "source_manifest.json": date_dir / "source_manifest.json",
    "health_features.json": date_dir / "health_features.json",
}

support_status = {
    name: {"path": rel(path), "exists": path.exists(), "sha256": sha256(path), "size_bytes": path.stat().st_size if path.exists() else None}
    for name, path in support_files.items()
}

if not support_status["dataset_manifest.json"]["exists"]:
    blockers.append({"kind": "artifact_manifest_blocker", "message": "dataset_manifest.json missing at canonical root", "path": support_status["dataset_manifest.json"]["path"]})

if not support_status["selector_available_dates.json"]["exists"]:
    blockers.append({"kind": "selector_contract_blocker", "message": "selector_available_dates.json missing at canonical root", "path": support_status["selector_available_dates.json"]["path"]})

# The package is only a compatibility probe, not a selector execution and not engine execution.
selector_consumption_candidate = (
    surface_compatibility["quote_ticks_mme_fut_stream.csv"]["compatible"]
    and surface_compatibility["quote_ticks_mme_opt_stream.csv"]["compatible"]
    and support_status["selector_available_dates.json"]["exists"]
)

engine_consumption_candidate = (
    all(v["compatible"] for v in surface_compatibility.values())
    and all(v.get("parse_ok") is not False for v in source_status.values() if v.get("exists"))
)

# Keep engine_ready_candidate false until an actual guarded selector/engine dry-run proves consumption.
engine_ready_candidate = False

consumption_probe_ok = len([b for b in blockers if b["kind"] in {"schema_header_blocker", "artifact_manifest_blocker", "selector_contract_blocker"}]) == 0

next_batch = "REPLAY-DATA-A20"
if consumption_probe_ok:
    recommended_next_batch = "REPLAY-DATA-A20 guarded selector-only plan/run; still no full engine unless selector consumption is proven"
else:
    recommended_next_batch = "REPLAY-DATA-A20 targeted consumption blocker repair"

summary = {
    "consumption_probe_ok": consumption_probe_ok,
    "selector_consumption_candidate": selector_consumption_candidate,
    "engine_consumption_candidate": engine_consumption_candidate,
    "engine_ready_candidate": engine_ready_candidate,
    "surface_compatibility_ok": all(v["compatible"] for v in surface_compatibility.values()),
    "blocker_count": len(blockers),
    "blockers": blockers,
    "recommended_next_batch": recommended_next_batch,
    "next_batch": next_batch,
    "engine_execution_performed": False,
    "broker_calls_executed": False,
    "live_redis_writes_executed": False,
    "paper_or_live_enabled": False,
    "orders_sent": False,
}

stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
proof_path = ROOT / "run/proofs" / f"proof_replay_data_a19_selector_engine_consumption_probe_{stamp}.json"
audit_path = ROOT / "run/audits" / f"replay_data_a19_selector_engine_consumption_probe_{stamp}.json"
milestone_path = ROOT / "docs/milestones" / f"replay_data_a19_selector_engine_consumption_probe_{stamp}.md"

proof = {
    "batch": "REPLAY-DATA-A19",
    "title": "selector / engine consumption compatibility probe",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "source_a18_proof": rel(A18_PROOF),
    "canonical_root": canonical_root,
    "source_date": source_date,
    "date_dir": rel(date_dir),
    "surface_info": surface_info,
    "surface_compatibility": surface_compatibility,
    "support_status": support_status,
    "selector_terms": selector_terms,
    "engine_terms": engine_terms,
    "source_status": source_status,
    "summary": summary,
    "safety": {
        "api_calls_executed": False,
        "engine_execution_performed": False,
        "services_started": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "paper_or_live_enabled": False,
        "orders_sent": False,
    },
}

proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
audit_path.write_text(json.dumps({
    "summary": summary,
    "surface_compatibility": surface_compatibility,
    "support_status": support_status,
    "selector_terms": selector_terms,
    "engine_terms": engine_terms,
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

milestone_path.write_text(
    "# REPLAY-DATA-A19 — Selector / Engine Consumption Compatibility Probe\n\n"
    f"- consumption_probe_ok: \n"
    f"- selector_consumption_candidate: \n"
    f"- engine_consumption_candidate: \n"
    f"- engine_ready_candidate: \n"
    f"- blocker_count: \n"
    f"- next_batch: \n"
    f"- proof: \n",
    encoding="utf-8",
)

print(json.dumps({
    "proof_written": rel(proof_path),
    "audit_written": rel(audit_path),
    "milestone_written": rel(milestone_path),
    **summary,
}, indent=2, sort_keys=True))
PY
