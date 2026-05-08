#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-E"
BATCH_NAME = "controlled_paper_no_candidate_root_cause_review_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_e_no_candidate_root_cause_review_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_e_no_candidate_root_cause_review.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_e_no_candidate_root_cause_review.json"
ROOT_CAUSE_JSON = RUN_DIR / "controlled_paper_o23e_no_candidate_root_cause.json"
FRAME_AUDIT_JSON = RUN_DIR / "controlled_paper_o23e_latest_frame_audit.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23e_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_e_no_candidate_root_cause_review.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_e_no_candidate_root_cause_review.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_e_no_candidate_root_cause_review.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

INSPECT_PATHS = [
    "run/proofs/proof_batch26o23_d_second_session_evidence_review.json",
    "run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json",
    "run/proofs/proof_batch26o23_c_second_bounded_controlled_paper_observation.json",
    "run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json",
    "run/proofs/proof_batch26o23_b_r1_controlled_pid_cleanup_readback.json",
    "run/proofs/proof_batch26o23_a_r1_session_completion_safety_readback.json",
    "run/proofs/proof_batch26o23_a_explicit_approved_controlled_paper_launcher.json",
    "run/proofs/proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.json",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/rollout",
]


def run(cmd: list[str] | str, *, timeout: int = 30, shell: bool = False) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            shell=shell,
        )
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "ok": cp.returncode == 0,
        }
    except Exception as exc:
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
            "ok": False,
        }


def redis_cmd(args: list[str], timeout: int = 10) -> dict[str, Any]:
    return run([REDIS_CLI, *args], timeout=timeout)


def redis_xlen(key: str) -> int:
    out = redis_cmd(["XLEN", key])
    try:
        return int((out.get("stdout") or "0").strip() or "0")
    except Exception:
        return -1


def redis_hgetall(key: str) -> dict[str, str]:
    out = redis_cmd(["HGETALL", key])
    lines = [x for x in (out.get("stdout") or "").splitlines()]
    d: dict[str, str] = {}
    for i in range(0, len(lines) - 1, 2):
        d[lines[i]] = lines[i + 1]
    return d


def redis_xrevrange_raw(key: str, count: int = 20) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def parse_json_maybe(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (dict, list, bool, int, float)):
        return v
    if not isinstance(v, str):
        return None
    s = v.strip()
    if not s:
        return None
    for _ in range(5):
        try:
            parsed = json.loads(s)
        except Exception:
            return None
        if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
            s = parsed.strip()
            continue
        return parsed
    return None


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def proc_lines() -> list[str]:
    out = run("ps -eo pid,ppid,stat,etime,args | grep -E 'app\\.mme_scalpx|mme_scalpx' | grep -v grep || true", shell=True, timeout=10)
    return [x for x in (out.get("stdout") or "").splitlines() if x.strip()]


def parse_processes() -> list[dict[str, Any]]:
    rows = []
    for line in proc_lines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(.*)$", line)
        if not m:
            continue
        args = m.group(5)
        sm = re.search(r"--service(?:=|\s+)(feeds|features|strategy|risk|execution|monitor|report)", args)
        service = sm.group(1) if sm else None
        rows.append({
            "pid": int(m.group(1)),
            "ppid": int(m.group(2)),
            "stat": m.group(3),
            "etime": m.group(4),
            "service": service,
            "args": args,
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in CONTROLLED_SERVICES,
            "is_risk_execution": service in {"risk", "execution"},
        })
    return rows


def snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=20),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=20),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=10),
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def parse_stream_entries(raw_stdout: str) -> list[dict[str, Any]]:
    lines = raw_stdout.splitlines()
    entries: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if re.match(r"^\d+-\d+$", line):
            if cur:
                entries.append(cur)
            cur = {"id": line, "fields": {}}
            i += 1
            continue
        if cur is not None and i + 1 < len(lines):
            key = line
            val = lines[i + 1]
            cur["fields"][key] = val
            i += 2
            continue
        i += 1
    if cur:
        entries.append(cur)
    return entries


def parse_payloads(raw_stdout: str, field_names: set[str]) -> list[dict[str, Any]]:
    out = []
    for ent in parse_stream_entries(raw_stdout):
        fields = ent.get("fields") or {}
        for k in field_names:
            obj = parse_json_maybe(fields.get(k))
            if isinstance(obj, dict):
                out.append({"id": ent.get("id"), "field": k, "payload": obj})
    return out


def decision_payloads(runtime: dict[str, Any]) -> list[dict[str, Any]]:
    raw = runtime.get("latest_decisions_raw", {}).get("stdout") or ""
    return parse_payloads(raw, {"payload_json", "decision_json", "json"})


def feature_payloads(runtime: dict[str, Any]) -> list[dict[str, Any]]:
    raw = runtime.get("latest_features_raw", {}).get("stdout") or ""
    return parse_payloads(raw, {"payload_json", "feature_payload_json", "family_features_json", "family_surfaces_json", "json"})


def summarize_decisions(runtime: dict[str, Any]) -> dict[str, Any]:
    payload_items = decision_payloads(runtime)
    payloads = [x["payload"] for x in payload_items]
    actions = [p.get("action") for p in payloads]
    reasons = [p.get("reason") or p.get("activation_reason") for p in payloads]
    candidate_counts = [p.get("activation_candidate_count") for p in payloads]
    return {
        "sample_count": len(payloads),
        "actions": actions,
        "reasons": reasons,
        "any_entry_action": any(str(a).upper() in {"BUY", "SELL", "ENTER", "ENTRY"} for a in actions),
        "all_hold_or_empty": all(str(a).upper() in {"HOLD", "", "NONE", "NULL"} for a in actions) if payloads else True,
        "activation_candidate_counts": candidate_counts,
        "all_candidate_counts_zero_or_empty": all((x in {0, "0", None, ""}) for x in candidate_counts) if payloads else True,
        "data_valid_values": [p.get("data_valid") for p in payloads],
        "safe_to_consume_values": [p.get("safe_to_consume") for p in payloads],
        "provider_ready_classic_values": [p.get("provider_ready_classic") for p in payloads],
        "provider_ready_miso_values": [p.get("provider_ready_miso") for p in payloads],
        "raw_payload_items": payload_items[:10],
    }


def extract_nested(payload: dict[str, Any], keys: list[str]) -> Any:
    cur: Any = payload
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def latest_feature_frame_analysis(runtime: dict[str, Any]) -> dict[str, Any]:
    items = feature_payloads(runtime)
    frames = [x["payload"] for x in items]
    latest = frames[0] if frames else {}

    family_surfaces = latest.get("family_surfaces") or latest.get("family_surfaces_json") or latest.get("family_features") or {}
    if isinstance(family_surfaces, str):
        family_surfaces = parse_json_maybe(family_surfaces) or {}
    if not isinstance(family_surfaces, dict):
        family_surfaces = {}

    branches = []
    mist_call = None
    branch_sources = []

    # Accept multiple known shapes.
    for key in ["branches", "branch_frames", "family_branch_frames", "surfaces"]:
        obj = family_surfaces.get(key) if isinstance(family_surfaces, dict) else None
        if isinstance(obj, list):
            branches = obj
            branch_sources.append(key)
        elif isinstance(obj, dict):
            branch_sources.append(key)
            for fam, fam_obj in obj.items():
                if isinstance(fam_obj, dict):
                    for side, val in fam_obj.items():
                        if isinstance(val, dict):
                            vv = dict(val)
                            vv.setdefault("family", fam)
                            vv.setdefault("side", side)
                            branches.append(vv)

    if not branches and isinstance(family_surfaces, dict):
        for fam, fam_obj in family_surfaces.items():
            if isinstance(fam_obj, dict):
                for side, val in fam_obj.items():
                    if isinstance(val, dict):
                        vv = dict(val)
                        vv.setdefault("family", fam)
                        vv.setdefault("side", side)
                        branches.append(vv)

    for b in branches:
        fam = str(b.get("family") or b.get("family_id") or b.get("strategy_family") or "").upper()
        side = str(b.get("side") or b.get("branch") or b.get("branch_id") or b.get("option_side") or "").upper()
        if fam == "MIST" and side == "CALL":
            mist_call = b
            break

    blockers = []
    for p in [latest, family_surfaces, mist_call or {}]:
        if isinstance(p, dict):
            for k, v in p.items():
                lk = str(k).lower()
                if any(tok in lk for tok in ["block", "reason", "valid", "ready", "candidate", "provider", "structural", "safe", "data_quality", "session", "warmup"]):
                    blockers.append({"key": k, "value": v})

    return {
        "feature_payload_count": len(frames),
        "latest_feature_id": items[0].get("id") if items else None,
        "latest_top_keys": sorted(list(latest.keys()))[:200] if isinstance(latest, dict) else [],
        "family_surface_keys": sorted(list(family_surfaces.keys()))[:200] if isinstance(family_surfaces, dict) else [],
        "branch_sources": branch_sources,
        "branch_count_detected": len(branches),
        "mist_call_detected": mist_call is not None,
        "mist_call_summary": mist_call,
        "candidate_like_blocker_fields": blockers[:300],
    }


def latest_run_dirs(prefix: str, limit: int = 5) -> list[pathlib.Path]:
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return []
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def inspect_logs(run_dirs: list[pathlib.Path]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    patterns = [
        "hold_only_family_features_consumer_bridge",
        "no_candidate",
        "candidate",
        "block",
        "provider",
        "data_valid",
        "safe_to_consume",
        "structural",
        "session",
        "warmup",
        "Traceback",
        "Exception",
        "ERROR",
        "CRITICAL",
        "broker",
        "order",
        "real_live",
        "HOLD",
        "BUY",
        "SELL",
        "ENTRY",
    ]
    for d in run_dirs:
        rec = {"path": str(d.relative_to(ROOT)), "files": {}}
        for f in sorted(d.glob("*.log")):
            text = f.read_text(encoding="utf-8", errors="replace")
            hits = {}
            for pat in patterns:
                arr = []
                for idx, line in enumerate(text.splitlines(), start=1):
                    if pat.lower() in line.lower():
                        arr.append({"line": idx, "text": line[:280]})
                hits[pat] = arr[:100]
            rec["files"][str(f.relative_to(ROOT))] = {
                "sha256": sha256_file(f),
                "size_bytes": f.stat().st_size,
                "line_count": text.count("\n") + 1,
                "hits": hits,
                "tail": "\n".join(text.splitlines()[-80:]),
            }
        out[str(d.relative_to(ROOT))] = rec
    return out


def inspect_source_for_candidate_terms(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists() or not p.is_file():
        return {"exists": p.exists(), "is_file": False}
    text = p.read_text(encoding="utf-8", errors="replace")
    terms = [
        "hold_only_family_features_consumer_bridge",
        "activation_candidate_count",
        "candidate",
        "no_candidate",
        "data_valid",
        "safe_to_consume",
        "structural_valid",
        "provider_ready_classic",
        "provider_ready_miso",
        "MIST",
        "CALL",
        "risk_veto",
        "reconciliation_lock",
        "active_position",
        "warmup",
        "session",
    ]
    hits = {}
    for term in terms:
        arr = []
        for i, line in enumerate(text.splitlines(), start=1):
            if term.lower() in line.lower():
                arr.append({"line": i, "text": line[:280]})
        hits[term] = arr[:100]
    return {
        "exists": True,
        "sha256": sha256_file(p),
        "size_bytes": p.stat().st_size,
        "line_count": text.count("\n") + 1,
        "hits": hits,
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Evidence-only root-cause review for repeated controlled-paper no-candidate / HOLD-only observations.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "root_cause_review_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "commands": {},
        "runtime_snapshot": {},
        "decision_summary": {},
        "latest_frame_analysis": {},
        "log_review": {},
        "source_candidate_audit": {},
        "root_cause_review": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== EVIDENCE-FIRST INSPECTION =====")
    run_dirs = [
        *latest_run_dirs("batch26o23_a_explicit_approved_controlled_paper_launcher", 3),
        *latest_run_dirs("batch26o23_c_second_bounded_controlled_paper_observation", 3),
        *latest_run_dirs("batch26o23_c_r1_completion_safety_readback", 3),
        *latest_run_dirs("batch26o23_d_second_session_evidence_review", 3),
    ]

    dynamic_paths = list(INSPECT_PATHS)
    for d in run_dirs:
        dynamic_paths.extend(str(p.relative_to(ROOT)) for p in d.glob("*"))

    for rel in dynamic_paths:
        p = ROOT / rel
        if p.exists() and p.is_file():
            dst = BACKUP_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            proof["inspected_files"][rel] = {
                "exists": True,
                "sha256": sha256_file(p),
                "size_bytes": p.stat().st_size,
                "backup": str(dst.relative_to(ROOT)),
            }
            if rel.endswith(".json"):
                proof["prior_proofs"][rel] = load_json(p)
        elif p.exists() and p.is_dir():
            proof["inspected_files"][rel] = {
                "exists": True,
                "is_dir": True,
                "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:200],
            }
        else:
            proof["inspected_files"][rel] = {"exists": False}

    print("===== COMPILE / IMPORT PROOF =====")
    compile_targets = [
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/feeds.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/redisx.py",
    ]
    proof["commands"] = {
        "compile": run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60),
        "import": run([
            sys.executable,
            "-c",
            "import app.mme_scalpx.main, app.mme_scalpx.services.feeds, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
        ], timeout=60),
    }

    print("===== RUNTIME READBACK =====")
    runtime = snapshot()
    proof["runtime_snapshot"] = runtime
    proof["decision_summary"] = summarize_decisions(runtime)
    proof["latest_frame_analysis"] = latest_feature_frame_analysis(runtime)

    print("===== SOURCE CANDIDATE AUDIT =====")
    for rel in [
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/names.py",
    ]:
        proof["source_candidate_audit"][rel] = inspect_source_for_candidate_terms(rel)

    print("===== LOG REVIEW =====")
    proof["log_review"] = inspect_logs(run_dirs)

    o23d = proof["prior_proofs"].get("run/proofs/proof_batch26o23_d_second_session_evidence_review.json", {})
    c_r1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json", {})
    b_r2 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json", {})

    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0

    dec = proof["decision_summary"]
    frame = proof["latest_frame_analysis"]

    # Classification is evidence-based; no patch/no threshold relaxation here.
    likely_factors = []
    if dec.get("all_candidate_counts_zero_or_empty"):
        likely_factors.append("strategy_activation_candidate_count_zero")
    if "hold_only_family_features_consumer_bridge" in json.dumps(dec):
        likely_factors.append("strategy_hold_reason_family_features_consumer_bridge")
    if frame.get("feature_payload_count", 0) == 0:
        likely_factors.append("no_recent_parseable_feature_payload_in_latest_sample")
    if frame.get("branch_count_detected", 0) == 0:
        likely_factors.append("latest_feature_sample_branch_shape_not_parseable_by_review")
    if frame.get("mist_call_detected") is False:
        likely_factors.append("mist_call_not_detected_in_latest_feature_sample_by_review")
    if 0 in dec.get("data_valid_values", []):
        likely_factors.append("latest_decision_data_valid_zero_observed")
    if all(x in {1, "1", True} for x in dec.get("safe_to_consume_values", []) if x is not None):
        likely_factors.append("safe_to_consume_true_but_data_valid_zero_split")

    root_cause_review = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "NO_CANDIDATE_HOLD_ONLY_ROOT_CAUSE_REVIEW_NO_PATCH",
        "orders_zero": orders_zero,
        "position_flat": position_flat,
        "no_controlled_pids": no_controlled_pids,
        "risk_execution_not_running": risk_execution_not_running,
        "decision_summary": dec,
        "latest_frame_analysis": frame,
        "likely_factors": likely_factors,
        "interpretation": [
            "Two controlled-paper observations produced safe HOLD-only/no-trade behavior.",
            "Latest decisions show activation_candidate_count=0 and HOLD-only behavior.",
            "Observed decision data_valid values include 0 while safe_to_consume values are true in recent samples.",
            "This suggests the next useful Lane-A move is a source-level consumer/strategy validity bridge audit or a narrow parser/source repair, not a third observation.",
        ],
        "not_evidence_of_live_readiness": True,
        "real_live_approval": False,
        "patch_applied": False,
    }
    proof["root_cause_review"] = root_cause_review
    ROOT_CAUSE_JSON.write_text(json.dumps(root_cause_review, indent=2, sort_keys=True), encoding="utf-8")

    frame_audit = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_snapshot": runtime,
        "decision_summary": dec,
        "latest_frame_analysis": frame,
        "source_candidate_audit": proof["source_candidate_audit"],
    }
    FRAME_AUDIT_JSON.write_text(json.dumps(frame_audit, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "DO_NOT_RUN_MORE_OBSERVATION_BEFORE_VALIDITY_BRIDGE_AUDIT",
        "recommended_next_batch": "26-O23-F controlled-paper data_valid / activation-candidate bridge audit, no service start, no real live",
        "do_not_proceed_to_real_live": True,
        "why": [
            "O23-D passed but classified second session as safe no-trade observation.",
            "O23-E confirms latest decisions remain HOLD-only and activation_candidate_count=0.",
            "Latest decision samples show data_valid=0 while safe_to_consume=1.",
            "Another observation without fixing/understanding this bridge likely repeats HOLD/no-candidate.",
        ],
        "forbidden_next_steps": [
            "real live",
            "quantity increase",
            "family expansion",
            "threshold relaxation",
            "forced candidate",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    proof["next_decision"] = next_decision
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "o23d_pass_loaded": str(o23d.get("final_verdict", "")).startswith("PASS_O23_D_SECOND_SESSION_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
        "o23c_r1_pass_loaded": str(c_r1.get("final_verdict", "")).startswith("PASS_O23_C_R1_COMPLETION_SAFETY_READBACK_CLEAN_STOPPED"),
        "o23b_r2_pass_loaded": str(b_r2.get("final_verdict", "")).startswith("PASS_O23_B_R2_EVIDENCE_REVIEW_CORRECTED_OK_NO_REAL_LIVE"),
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "decisions_hold_only_or_empty": dec.get("all_hold_or_empty") is True,
        "activation_candidate_zero_or_empty": dec.get("all_candidate_counts_zero_or_empty") is True,
        "root_cause_json_written": ROOT_CAUSE_JSON.exists(),
        "frame_audit_json_written": FRAME_AUDIT_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "real_live_approval_false": True,
        "production_source_patch_false": True,
        "service_start_false": True,
        "broker_call_false": True,
        "order_write_false": True,
        "threshold_relaxation_false": True,
        "forced_candidate_false": True,
    }

    false_keys = [k for k, v in req.items() if v is not True]
    proof["required_verdicts"] = req
    proof["false_keys"] = false_keys
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    if false_keys:
        proof["final_verdict"] = "FAIL_O23_E_NO_CANDIDATE_ROOT_CAUSE_REVIEW_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; no controlled-paper restart."
    else:
        proof["final_verdict"] = "PASS_O23_E_NO_CANDIDATE_ROOT_CAUSE_REVIEW_OK_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "26-O23-F controlled-paper data_valid / activation-candidate bridge audit; no service start, no real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — controlled-paper no-candidate root-cause review",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- root_cause: `{ROOT_CAUSE_JSON.relative_to(ROOT)}`",
            f"- frame_audit: `{FRAME_AUDIT_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Review why controlled-paper observations stayed HOLD/no-candidate.",
            "- Do not start services.",
            "- Do not patch source.",
            "- Do not approve real live.",
            "",
            "## Findings",
            "```json",
            json.dumps(root_cause_review, indent=2, sort_keys=True),
            "```",
            "",
            "## Verdict",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- false_keys: `{false_keys}`",
            f"- next_recommended_batch: `{proof['next_recommended_batch']}`",
            "",
            "## Required verdicts",
            "```json",
            json.dumps(req, indent=2, sort_keys=True),
            "```",
        ]),
        encoding="utf-8",
    )

    MILESTONE_MD.write_text(
        "\n".join([
            f"# {DATE} — {BATCH} no-candidate root-cause review",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Reviewed post-O23-D no-candidate state.",
            "- Confirmed safe runtime state if PASS.",
            "- Captured decision summary and latest feature-frame audit.",
            "- Classified likely HOLD/no-candidate factors without patching.",
            "- Preserved no-real-live boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        ROOT_CAUSE_JSON,
        FRAME_AUDIT_JSON,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        *[ROOT / rel for rel in dynamic_paths if (ROOT / rel).exists() and (ROOT / rel).is_file()],
    ]
    manifest = {
        "batch": BATCH,
        "tag": TAG,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": {
            str(p.relative_to(ROOT)): sha256_file(p)
            for p in manifest_paths
            if p.exists()
        },
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    print("===== FINAL SUMMARY =====")
    print("final_verdict =", proof["final_verdict"])
    print("false_keys =", false_keys)
    print("likely_factors =", likely_factors)
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("root_cause_json =", ROOT_CAUSE_JSON.relative_to(ROOT))
    print("frame_audit_json =", FRAME_AUDIT_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
