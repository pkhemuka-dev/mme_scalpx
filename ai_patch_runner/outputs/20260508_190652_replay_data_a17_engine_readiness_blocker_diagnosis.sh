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

# REPLAY-DATA-A17
# engine_readiness_blocker
# blocker_diagnosis_ok
# engine_ready_candidate
# blocker_count
# recommended_next_batch
# proof_replay_data_a17_engine_readiness_blocker
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
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
A16_PROOF = ROOT / "run/proofs/proof_replay_data_a16_contract_shape_audit_20260508T190013Z.json"

def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except Exception:
        return str(p)

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(path: Path, limit=500000):
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception as exc:
        return f"__READ_ERROR__ {type(exc).__name__}: {exc}"

def csv_header_row_count(path: Path):
    if not path.exists():
        return {"exists": False, "header": [], "row_count": 0, "size_bytes": None, "sha256": None}
    header = []
    rows = 0
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            header = []
        for _ in reader:
            rows += 1
    return {
        "exists": True,
        "header": header,
        "row_count": rows,
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }

def ast_importable(path: Path):
    if not path.exists():
        return {"exists": False, "parse_ok": False, "error": "missing"}
    try:
        ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        return {"exists": True, "parse_ok": True, "error": None}
    except Exception as exc:
        return {"exists": True, "parse_ok": False, "error": repr(exc)}

a16 = load_json(A16_PROOF)
a16_summary = a16.get("summary") or a16

canonical_root = (
    a16_summary.get("canonical_root")
    or a16.get("canonical_root")
    or "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z"
)
source_date = a16_summary.get("source_date") or a16.get("source_date") or "2026-04-17"

date_dir = ROOT / canonical_root / source_date
if not date_dir.exists():
    date_dir = ROOT / "run/replay/parity/offline_materialization/session_exports_canonical_candidate_20260417_a7_20260508T173739Z/2026-04-17"

candidate_files = [
    "quote_ticks_mme_fut_stream.csv",
    "quote_ticks_mme_opt_stream.csv",
    "features_rows_candidate.csv",
    "strategy_decisions_candidate.csv",
    "risk_outputs_candidate.csv",
    "execution_shadow_candidate.csv",
]

candidate_surfaces = {name: csv_header_row_count(date_dir / name) for name in candidate_files}

replay_files = [
    "app/mme_scalpx/replay/contracts.py",
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/selectors.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/runner.py",
    "bin/replay_run.py",
]

replay_source_status = {}
combined_text = ""
for rf in replay_files:
    p = ROOT / rf
    replay_source_status[rf] = {
        **ast_importable(p),
        "path": rf,
        "size_bytes": p.stat().st_size if p.exists() else None,
        "sha256": sha256(p) if p.exists() else None,
    }
    combined_text += f"\n\n### {rf}\n" + read_text(p)

blockers = []

missing_files = [name for name, info in candidate_surfaces.items() if not info["exists"]]
empty_files = [name for name, info in candidate_surfaces.items() if info["exists"] and info["row_count"] <= 0]

if missing_files:
    blockers.append({
        "kind": "candidate_surface_quality_blocker",
        "severity": "FAIL",
        "message": "Required candidate surface file missing.",
        "details": {"missing_files": missing_files},
    })

if empty_files:
    blockers.append({
        "kind": "candidate_surface_quality_blocker",
        "severity": "FAIL",
        "message": "Required candidate surface file is empty/header-only.",
        "details": {"empty_files": empty_files},
    })

# Identify expected replay engine concepts from source text.
text_lower = combined_text.lower()

expected_terms = {
    "dataset_manifest": "dataset_manifest",
    "selector_available_dates": "selector_available_dates",
    "required_file_stems": "required_file_stems",
    "quote_only_recorded": "quote_only_recorded",
    "features_rows": "features_rows",
    "strategy_decisions": "strategy_decisions",
    "risk_outputs": "risk_outputs",
    "execution_shadow": "execution_shadow",
}

term_presence = {k: (v in text_lower) for k, v in expected_terms.items()}

# Check date root support files.
support_files = {
    "dataset_manifest_root": ROOT / canonical_root / "dataset_manifest.json",
    "selector_available_dates_root": ROOT / canonical_root / "selector_available_dates.json",
    "source_manifest_date": date_dir / "source_manifest.json",
    "health_features_date": date_dir / "health_features.json",
}

support_status = {
    name: {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256(path) if path.exists() else None,
    }
    for name, path in support_files.items()
}

if not support_files["dataset_manifest_root"].exists():
    blockers.append({
        "kind": "artifact_manifest_blocker",
        "severity": "REVIEW",
        "message": "Root dataset_manifest.json missing or not found at inferred canonical root.",
        "details": {"path": rel(support_files["dataset_manifest_root"])},
    })

if not support_files["selector_available_dates_root"].exists():
    blockers.append({
        "kind": "selector_contract_blocker",
        "severity": "REVIEW",
        "message": "selector_available_dates.json missing or not found at inferred canonical root.",
        "details": {"path": rel(support_files["selector_available_dates_root"])},
    })

# The A16 proof explicitly reported engine_ready_candidate false, so diagnose this as a blocker until proven.
if a16_summary.get("engine_ready_candidate") is False:
    blockers.append({
        "kind": "engine_input_blocker",
        "severity": "REVIEW",
        "message": "A16 reported engine_ready_candidate=false; full engine dry-run remains blocked until exact engine input contract is proven.",
        "details": {
            "contract_shape_ok": a16_summary.get("contract_shape_ok"),
            "missing_expected_surfaces": a16_summary.get("missing_expected_surfaces"),
            "incompatible_surfaces": a16_summary.get("incompatible_surfaces"),
        },
    })

# The execution shadow candidate is structurally weak if rows are blank under a header.
exec_info = candidate_surfaces.get("execution_shadow_candidate.csv", {})
exec_header = exec_info.get("header") or []
if exec_info.get("exists") and exec_info.get("row_count", 0) > 0:
    sample_blank_like = False
    try:
        with (date_dir / "execution_shadow_candidate.csv").open("r", encoding="utf-8", errors="replace") as f:
            next(f, "")
            rows = [next(f, "").strip() for _ in range(5)]
        sample_blank_like = any(row and set(row) <= {","} for row in rows)
    except Exception:
        sample_blank_like = False
    if sample_blank_like:
        blockers.append({
            "kind": "candidate_surface_quality_blocker",
            "severity": "REVIEW",
            "message": "execution_shadow_candidate has header but sample rows appear blank/comma-only; engine dry-run should not trust it as semantic execution shadow.",
            "details": {"header": exec_header[:50], "path": rel(date_dir / "execution_shadow_candidate.csv")},
        })

blocker_diagnosis_ok = True
engine_ready_candidate = False
blocker_count = len(blockers)

if blocker_count == 0:
    recommended_next_batch = "REPLAY-DATA-A18 selector/engine dry-run plan"
    next_batch = "REPLAY-DATA-A18"
else:
    recommended_next_batch = "REPLAY-DATA-A18 targeted blocker repair/normalization plan"
    next_batch = "REPLAY-DATA-A18"

summary = {
    "blocker_diagnosis_ok": blocker_diagnosis_ok,
    "engine_ready_candidate": engine_ready_candidate,
    "blocker_count": blocker_count,
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
proof_path = ROOT / "run/proofs" / f"proof_replay_data_a17_engine_readiness_blocker_{stamp}.json"
audit_path = ROOT / "run/audits" / f"replay_data_a17_engine_readiness_blocker_{stamp}.json"
milestone_path = ROOT / "docs/milestones" / f"replay_data_a17_engine_readiness_blocker_{stamp}.md"

proof = {
    "batch": "REPLAY-DATA-A17",
    "title": "engine readiness blocker diagnosis",
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "source_a16_proof": rel(A16_PROOF),
    "canonical_root": canonical_root,
    "source_date": source_date,
    "date_dir": rel(date_dir),
    "candidate_surfaces": candidate_surfaces,
    "support_status": support_status,
    "replay_source_status": replay_source_status,
    "term_presence": term_presence,
    "summary": summary,
    "safety": {
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
    "candidate_surfaces": candidate_surfaces,
    "support_status": support_status,
    "term_presence": term_presence,
}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

milestone_path.write_text(
    "# REPLAY-DATA-A17 — Engine Readiness Blocker Diagnosis\n\n"
    f"- UTC: {proof['created_at_utc']}\n"
    f"- blocker_diagnosis_ok: {blocker_diagnosis_ok}\n"
    f"- engine_ready_candidate: {engine_ready_candidate}\n"
    f"- blocker_count: {blocker_count}\n"
    f"- recommended_next_batch: {recommended_next_batch}\n"
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
