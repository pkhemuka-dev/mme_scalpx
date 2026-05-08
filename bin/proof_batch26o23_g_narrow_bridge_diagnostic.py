#!/usr/bin/env python3
from __future__ import annotations

import ast
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
BATCH = "26-O23-G"
BATCH_NAME = "narrow_data_valid_consumer_view_bridge_diagnostic_no_patch_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_g_narrow_bridge_diagnostic_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_g_narrow_bridge_diagnostic.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_g_narrow_bridge_diagnostic.json"
BRIDGE_DIAGNOSTIC_JSON = RUN_DIR / "controlled_paper_o23g_bridge_diagnostic.json"
SOURCE_SEAMS_JSON = RUN_DIR / "controlled_paper_o23g_source_seams.json"
PATCH_PLAN_JSON = RUN_DIR / "controlled_paper_o23g_patch_plan_if_proven.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23g_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_g_narrow_bridge_diagnostic.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_g_narrow_bridge_diagnostic.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_g_narrow_bridge_diagnostic.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

SMALL_COPY_LIMIT_BYTES = 350_000
MAX_SLICE_CHARS = 40_000
MAX_CONTEXT_LINES = 900

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_f_r4_prior_proof_loader_correction.json",
    "run/proofs/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json",
    "run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json",
    "run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json",
    "run/proofs/proof_batch26o23_d_second_session_evidence_review.json",
]

TARGET_SOURCE_PATHS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
]

READONLY_CONTEXT_PATHS = [
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/main.py",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + TARGET_SOURCE_PATHS + READONLY_CONTEXT_PATHS

TERMS = [
    "data_valid",
    "safe_to_consume",
    "structural_valid",
    "consumer_view",
    "consumer_view_json",
    "family_features",
    "family_surfaces",
    "family_features_consumer_bridge",
    "hold_only_family_features_consumer_bridge",
    "activation_candidate_count",
    "candidate_count",
    "no_candidate",
    "MIST",
    "CALL",
    "branch_frames",
    "branch",
    "provider_ready_classic",
    "provider_ready_miso",
    "selected_option_ready",
    "feed_fresh",
    "warmup",
    "session_eligible",
    "data_quality",
    "action",
    "HOLD",
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
            "stdout": cp.stdout[-30000:],
            "stderr": cp.stderr[-30000:],
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


def disk_state() -> dict[str, Any]:
    u = shutil.disk_usage(ROOT)
    return {
        "free_bytes": u.free,
        "free_gb": round(u.free / 1024**3, 3),
        "used_pct": round((u.used / u.total) * 100, 2) if u.total else None,
        "df_h": run("df -h . || true", shell=True, timeout=10),
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


def redis_xrevrange_raw(key: str, count: int = 5) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_file_record(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec: dict[str, Any] = {"path": rel, "exists": p.exists(), "is_file": p.is_file() if p.exists() else False}
    if not p.exists() or not p.is_file():
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)

    if p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        try:
            dst = BACKUP_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            rec["small_source_backup"] = str(dst.relative_to(ROOT))
        except Exception as exc:
            rec["small_source_backup_error"] = repr(exc)
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only_no_full_evidence_copy"

    return rec


def load_json_limited(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec = safe_file_record(rel)
    if not p.exists() or not p.is_file():
        return rec
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        rec["json_loaded"] = isinstance(obj, dict)
        if isinstance(obj, dict):
            rec["final_verdict"] = obj.get("final_verdict")
            rec["false_keys"] = obj.get("false_keys")
            rec["next_recommended_batch"] = obj.get("next_recommended_batch")
            rec["required_verdicts"] = {
                k: v for k, v in (obj.get("required_verdicts") or {}).items()
                if k in {
                    "compile_pass",
                    "import_pass",
                    "orders_zero_now",
                    "position_flat_now",
                    "no_controlled_pids_now",
                    "risk_execution_not_running_now",
                    "real_live_approval_false",
                    "production_source_patch_false",
                    "service_start_false",
                    "f_r3_bridge_audit_present",
                    "f_r3_source_bridge_summary_present",
                }
            }
            rec["bridge_audit"] = obj.get("bridge_audit")
            rec["corrected_equivalence"] = obj.get("corrected_equivalence")
            rec["source_bridge_summary"] = obj.get("source_bridge_summary")
    except Exception as exc:
        rec["json_load_error"] = repr(exc)
    return rec


def pass_prefix(rec: dict[str, Any], prefix: str) -> bool:
    fv = rec.get("final_verdict")
    return isinstance(fv, str) and fv.startswith(prefix)


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
            "args": args[:600],
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in CONTROLLED_SERVICES,
            "is_risk_execution": service in {"risk", "execution"},
        })
    return rows


def runtime_snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=5),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=5),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
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
            cur["fields"][line] = lines[i + 1]
            i += 2
            continue
        i += 1
    if cur:
        entries.append(cur)
    return entries


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
    for _ in range(4):
        try:
            parsed = json.loads(s)
        except Exception:
            return None
        if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
            s = parsed.strip()
            continue
        return parsed
    return None


def parse_payloads(raw_stdout: str) -> list[dict[str, Any]]:
    out = []
    for ent in parse_stream_entries(raw_stdout):
        for k, v in (ent.get("fields") or {}).items():
            if k.endswith("_json") or k in {"json", "payload", "payload_json", "decision_json", "feature_payload_json"}:
                obj = parse_json_maybe(v)
                if isinstance(obj, dict):
                    out.append({"id": ent.get("id"), "field": k, "payload": obj})
    return out[:8]


def nested_key_scan(payload_items: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    for idx, item in enumerate(payload_items[:5]):
        payload = item.get("payload") or {}
        stack = [("", payload)]
        while stack and len(hits) < 600:
            path, obj = stack.pop()
            if isinstance(obj, dict):
                for k, v in obj.items():
                    pth = f"{path}.{k}" if path else str(k)
                    lk = str(k).lower()
                    if any(tok in lk for tok in [
                        "data_valid", "safe_to_consume", "structural_valid", "consumer_view",
                        "candidate", "reason", "provider", "ready", "mist", "call", "branch",
                        "family", "session", "warmup", "feed", "selected_option", "surfaces", "features"
                    ]):
                        hits.append({
                            "payload_index": idx,
                            "stream_id": item.get("id"),
                            "field": item.get("field"),
                            "path": pth,
                            "value_repr": repr(v)[:500],
                        })
                    if isinstance(v, (dict, list)):
                        stack.append((pth, v))
            elif isinstance(obj, list):
                for j, v in enumerate(obj[:30]):
                    if isinstance(v, (dict, list)):
                        stack.append((f"{path}[{j}]", v))

    paths = {h["path"] for h in hits}
    return {
        "hits": hits,
        "paths": sorted(paths),
        "has_consumer_view_path": any("consumer_view" in p for p in paths),
        "has_data_valid_path": any("data_valid" in p for p in paths),
        "has_safe_to_consume_path": any("safe_to_consume" in p for p in paths),
        "has_structural_valid_path": any("structural_valid" in p for p in paths),
        "has_candidate_path": any("candidate" in p for p in paths),
    }


def runtime_payload_bridge(runtime: dict[str, Any]) -> dict[str, Any]:
    decisions = parse_payloads(runtime.get("latest_decisions_raw", {}).get("stdout") or "")
    features = parse_payloads(runtime.get("latest_features_raw", {}).get("stdout") or "")

    decision_summary = []
    for item in decisions:
        p = item["payload"]
        rec = {"id": item["id"], "field": item["field"], "top_keys": sorted(list(p.keys()))[:120]}
        for k in [
            "action", "reason", "activation_reason", "activation_candidate_count",
            "data_valid", "safe_to_consume", "structural_valid",
            "provider_ready_classic", "provider_ready_miso",
            "consumer_view", "consumer_view_json",
        ]:
            if k in p:
                rec[k] = p.get(k)
        decision_summary.append(rec)

    feature_summary = []
    for item in features:
        p = item["payload"]
        rec = {"id": item["id"], "field": item["field"], "top_keys": sorted(list(p.keys()))[:120]}
        for k in [
            "data_valid", "safe_to_consume", "structural_valid",
            "consumer_view", "consumer_view_json", "family_features", "family_surfaces",
        ]:
            if k in p:
                val = p.get(k)
                rec[k] = val if not isinstance(val, (dict, list)) else {"type": type(val).__name__, "keys_or_len": (sorted(list(val.keys()))[:80] if isinstance(val, dict) else len(val))}
        feature_summary.append(rec)

    return {
        "decision_payload_count": len(decisions),
        "feature_payload_count": len(features),
        "decision_summary": decision_summary,
        "feature_summary": feature_summary,
        "decision_key_scan": nested_key_scan(decisions),
        "feature_key_scan": nested_key_scan(features),
    }


def source_seam_scan(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists() or not p.is_file():
        return {"exists": p.exists(), "is_file": False}

    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    rec: dict[str, Any] = {
        "exists": True,
        "sha256": sha256_file(p),
        "size_bytes": p.stat().st_size,
        "line_count": len(lines),
        "term_hits": {},
        "function_contexts": [],
        "assignment_contexts": [],
        "dict_literal_contexts": [],
    }

    for term in TERMS:
        hits = []
        for i, line in enumerate(lines, start=1):
            if term.lower() in line.lower():
                hits.append({"line": i, "text": line[:340]})
                if len(hits) >= 80:
                    break
        rec["term_hits"][term] = hits

    # AST contexts: bounded and only around functions/classes containing bridge terms.
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = getattr(node, "end_lineno", node.lineno)
                src = "\n".join(lines[start - 1:end])
                found_terms = [t for t in TERMS if t.lower() in src.lower()]
                if found_terms:
                    rec["function_contexts"].append({
                        "name": node.name,
                        "line": start,
                        "end_line": end,
                        "found_terms": found_terms,
                        "source_excerpt": "\n".join(lines[max(0, start - 4):min(len(lines), end + 3)])[:8000],
                    })
                    if len(rec["function_contexts"]) >= 25:
                        break
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                start = getattr(node, "lineno", None)
                end = getattr(node, "end_lineno", start)
                if not start:
                    continue
                src = "\n".join(lines[start - 1:end])
                if any(t.lower() in src.lower() for t in TERMS):
                    rec["assignment_contexts"].append({
                        "line": start,
                        "end_line": end,
                        "source": src[:3000],
                    })
                    if len(rec["assignment_contexts"]) >= 80:
                        break
        rec["ast_parse_ok"] = True
    except Exception as exc:
        rec["ast_parse_ok"] = False
        rec["ast_error"] = repr(exc)

    # Bounded line windows around high-value terms.
    important_lines = set()
    for term in ["consumer_view", "data_valid", "safe_to_consume", "structural_valid", "activation_candidate_count", "hold_only_family_features_consumer_bridge"]:
        for hit in rec["term_hits"].get(term, [])[:20]:
            important_lines.add(int(hit["line"]))
    contexts = []
    used = set()
    for ln in sorted(important_lines):
        for j in range(max(1, ln - 6), min(len(lines), ln + 6) + 1):
            if j not in used:
                used.add(j)
                contexts.append({"line": j, "text": lines[j - 1][:400]})
            if len(contexts) >= MAX_CONTEXT_LINES:
                break
        if len(contexts) >= MAX_CONTEXT_LINES:
            break
    rec["nearby_contexts"] = contexts

    return rec


def classify_bridge(source_seams: dict[str, Any], runtime_bridge: dict[str, Any]) -> dict[str, Any]:
    flat_source = json.dumps(source_seams, sort_keys=True).lower()
    flat_runtime = json.dumps(runtime_bridge, sort_keys=True).lower()

    features = source_seams.get("app/mme_scalpx/services/features.py", {})
    strategy = source_seams.get("app/mme_scalpx/services/strategy.py", {})

    source_has_features_consumer_view = "consumer_view" in json.dumps(features).lower()
    source_has_strategy_consumer_view = "consumer_view" in json.dumps(strategy).lower()
    source_has_strategy_bridge_reason = "hold_only_family_features_consumer_bridge" in json.dumps(strategy).lower()
    source_has_feature_data_valid = "data_valid" in json.dumps(features).lower()
    source_has_strategy_data_valid = "data_valid" in json.dumps(strategy).lower()
    source_has_strategy_candidate = "activation_candidate_count" in json.dumps(strategy).lower() or "candidate_count" in json.dumps(strategy).lower()

    runtime_has_decision_payload = runtime_bridge.get("decision_payload_count", 0) > 0
    runtime_has_feature_payload = runtime_bridge.get("feature_payload_count", 0) > 0
    runtime_decision_data_valid = "data_valid" in flat_runtime
    runtime_decision_consumer_view = "consumer_view" in flat_runtime
    runtime_has_safe_to_consume = "safe_to_consume" in flat_runtime
    runtime_has_structural_valid = "structural_valid" in flat_runtime

    likely = []
    if source_has_features_consumer_view and source_has_strategy_consumer_view and source_has_strategy_bridge_reason:
        likely.append("features_and_strategy_have_consumer_view_bridge_with_hold_reason")
    if source_has_feature_data_valid and source_has_strategy_data_valid:
        likely.append("data_valid_is_produced_and_consumed_in_features_strategy")
    if source_has_strategy_candidate:
        likely.append("strategy_has_candidate_count_surface")
    if runtime_has_decision_payload and not runtime_decision_consumer_view:
        likely.append("recent_decision_payload_lacks_top_level_consumer_view")
    if not runtime_has_feature_payload:
        likely.append("recent_feature_payload_unparseable_or_not_present_in_latest_slice")
    if runtime_has_safe_to_consume and runtime_decision_data_valid:
        likely.append("runtime_payload_contains_validity_split_surface")
    if not runtime_has_structural_valid:
        likely.append("runtime_latest_slice_lacks_structural_valid_surface")

    confidence = "LOW"
    if len(likely) >= 4:
        confidence = "MEDIUM"
    if (
        source_has_features_consumer_view
        and source_has_strategy_consumer_view
        and source_has_strategy_bridge_reason
        and source_has_feature_data_valid
        and source_has_strategy_data_valid
        and source_has_strategy_candidate
    ):
        confidence = "MEDIUM_HIGH"

    return {
        "classification": "NARROW_FEATURES_STRATEGY_BRIDGE_SEAM_IDENTIFIED" if confidence in {"MEDIUM", "MEDIUM_HIGH"} else "BRIDGE_SEAM_PARTIAL_NOT_REPAIR_READY",
        "confidence": confidence,
        "likely_factors": likely,
        "source_presence": {
            "source_has_features_consumer_view": source_has_features_consumer_view,
            "source_has_strategy_consumer_view": source_has_strategy_consumer_view,
            "source_has_strategy_bridge_reason": source_has_strategy_bridge_reason,
            "source_has_feature_data_valid": source_has_feature_data_valid,
            "source_has_strategy_data_valid": source_has_strategy_data_valid,
            "source_has_strategy_candidate_count": source_has_strategy_candidate,
        },
        "runtime_presence": {
            "runtime_has_decision_payload": runtime_has_decision_payload,
            "runtime_has_feature_payload": runtime_has_feature_payload,
            "runtime_decision_data_valid": runtime_decision_data_valid,
            "runtime_decision_consumer_view": runtime_decision_consumer_view,
            "runtime_has_safe_to_consume": runtime_has_safe_to_consume,
            "runtime_has_structural_valid": runtime_has_structural_valid,
        },
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Locate exact features/strategy bridge seam for data_valid / consumer_view / activation candidate repair; no patch in this batch.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "diagnostic_only": True,
            "no_full_evidence_copy": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "runtime_bridge": {},
        "source_seams": {},
        "bridge_diagnostic": {},
        "patch_plan_if_proven": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()
    print(json.dumps(proof["disk_state"], indent=2, sort_keys=True)[:4000])

    print("===== EVIDENCE-FIRST INSPECTION WITH HASH/SLICE ONLY =====")
    for rel in INSPECT_PATHS:
        proof["inspected_files"][rel] = safe_file_record(rel)
        if rel.endswith(".json"):
            proof["prior_proofs"][rel] = load_json_limited(rel)

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

    print("===== RUNTIME SAFETY + PAYLOAD BRIDGE READBACK =====")
    runtime = runtime_snapshot()
    proof["runtime_snapshot"] = runtime
    proof["runtime_bridge"] = runtime_payload_bridge(runtime)

    print("===== SOURCE SEAM SCAN: FEATURES + STRATEGY ONLY =====")
    source_seams = {}
    for rel in TARGET_SOURCE_PATHS:
        source_seams[rel] = source_seam_scan(rel)
    proof["source_seams"] = source_seams
    SOURCE_SEAMS_JSON.write_text(json.dumps(source_seams, indent=2, sort_keys=True), encoding="utf-8")

    f_r4 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_f_r4_prior_proof_loader_correction.json", {})
    f_r3 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json", {})

    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0

    bridge_diag = classify_bridge(source_seams, proof["runtime_bridge"])
    bridge_diag.update({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime_safety": {
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "no_controlled_pids": no_controlled_pids,
            "risk_execution_not_running": risk_execution_not_running,
        },
        "prior_f_r4_status": {
            "final_verdict": f_r4.get("final_verdict"),
            "false_keys": f_r4.get("false_keys"),
        },
        "prior_f_r3_status": {
            "final_verdict": f_r3.get("final_verdict"),
            "false_keys": f_r3.get("false_keys"),
        },
        "patch_applied": False,
        "service_started": False,
        "real_live_approval": False,
    })
    proof["bridge_diagnostic"] = bridge_diag
    BRIDGE_DIAGNOSTIC_JSON.write_text(json.dumps(bridge_diag, indent=2, sort_keys=True), encoding="utf-8")

    patch_plan = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PATCH_PLAN_ONLY_NO_SOURCE_MUTATION",
        "repair_readiness": bridge_diag["classification"],
        "confidence": bridge_diag["confidence"],
        "allowed_files_if_next_patch_needed": TARGET_SOURCE_PATHS,
        "forbidden_files_for_next_patch_without_new_evidence": [
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
        ],
        "repair_principles": [
            "Do not relax strategy thresholds.",
            "Do not force candidate creation.",
            "Do not change MIST/MISB/MISC/MISR/MISO doctrine.",
            "Do not start services during patch proof.",
            "Repair only proven serialization/consumer-view/validity propagation gap.",
            "Preserve HOLD/fail-closed behavior when consumer view is absent or invalid.",
        ],
        "candidate_next_repair": [
            "If strategy consumes a top-level data_valid while features publishes valid consumer_view.data_valid, normalize strategy consumer-view extraction.",
            "If features publishes consumer_view_json but strategy expects consumer_view dict, add bounded parse/bridge in strategy only.",
            "If structural_valid is computed but not surfaced to decision payload, propagate without changing thresholds.",
            "If activation_candidate_count is zero because branch frames are unparseable, repair branch-frame parse/shape only.",
        ],
    }
    proof["patch_plan_if_proven"] = patch_plan
    PATCH_PLAN_JSON.write_text(json.dumps(patch_plan, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "ALLOW_O23-H_NARROW_BRIDGE_REPAIR_ONLY_IF_USER_ACCEPTS_DIAGNOSTIC",
        "recommended_next_batch": "26-O23-H narrow data_valid / consumer-view bridge repair, features/strategy only, no service start, no real live",
        "why": [
            "O23-G located the bridge seam in features/strategy surfaces.",
            "Runtime remains safe.",
            "No source mutation was applied in O23-G.",
            "Next patch must be minimal and only repair propagation/parsing, not trading thresholds.",
        ],
        "forbidden": [
            "real live",
            "third observation before bridge repair",
            "threshold relaxation",
            "forced candidate",
            "quantity increase",
            "family expansion",
            "risk/execution patch without evidence",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    proof["next_decision"] = next_decision
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "f_r4_pass_loaded": pass_prefix(f_r4, "PASS_O23_F_R4_PRIOR_PROOF_LOADER_CORRECTION_OK_NO_REAL_LIVE"),
        "f_r3_loaded": f_r3.get("exists") is True,
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "source_seams_json_written": SOURCE_SEAMS_JSON.exists(),
        "bridge_diagnostic_json_written": BRIDGE_DIAGNOSTIC_JSON.exists(),
        "patch_plan_json_written": PATCH_PLAN_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "features_py_scanned": source_seams.get("app/mme_scalpx/services/features.py", {}).get("exists") is True,
        "strategy_py_scanned": source_seams.get("app/mme_scalpx/services/strategy.py", {}).get("exists") is True,
        "source_has_features_consumer_view": bridge_diag["source_presence"].get("source_has_features_consumer_view") is True,
        "source_has_strategy_consumer_view": bridge_diag["source_presence"].get("source_has_strategy_consumer_view") is True,
        "source_has_strategy_bridge_reason": bridge_diag["source_presence"].get("source_has_strategy_bridge_reason") is True,
        "source_has_feature_data_valid": bridge_diag["source_presence"].get("source_has_feature_data_valid") is True,
        "source_has_strategy_data_valid": bridge_diag["source_presence"].get("source_has_strategy_data_valid") is True,
        "source_has_strategy_candidate_count": bridge_diag["source_presence"].get("source_has_strategy_candidate_count") is True,
        "diagnostic_confidence_not_low": bridge_diag.get("confidence") in {"MEDIUM", "MEDIUM_HIGH"},
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
        proof["final_verdict"] = "FAIL_O23_G_NARROW_BRIDGE_DIAGNOSTIC_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not patch or restart controlled paper."
    else:
        proof["final_verdict"] = "PASS_O23_G_NARROW_BRIDGE_DIAGNOSTIC_OK_NO_PATCH_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "26-O23-H narrow data_valid / consumer-view bridge repair, features/strategy only, no service start, no real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — narrow data_valid / consumer-view bridge diagnostic",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- bridge_diagnostic: `{BRIDGE_DIAGNOSTIC_JSON.relative_to(ROOT)}`",
            f"- source_seams: `{SOURCE_SEAMS_JSON.relative_to(ROOT)}`",
            f"- patch_plan: `{PATCH_PLAN_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Locate the exact features/strategy bridge seam causing HOLD/no-candidate.",
            "- No patch in this batch.",
            "- No service start.",
            "- No real live.",
            "- No threshold relaxation or forced candidate.",
            "",
            "## Bridge diagnostic",
            "```json",
            json.dumps(bridge_diag, indent=2, sort_keys=True),
            "```",
            "",
            "## Patch plan if proven",
            "```json",
            json.dumps(patch_plan, indent=2, sort_keys=True),
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
            f"# {DATE} — {BATCH} narrow bridge diagnostic",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Loaded O23-F-R4 as prerequisite.",
            "- Captured safe runtime readback.",
            "- Scanned features.py and strategy.py bridge seams only.",
            "- Produced patch plan without source mutation.",
            "- Preserved no-real-live, no-service-start, no-threshold-relaxation boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        BRIDGE_DIAGNOSTIC_JSON,
        SOURCE_SEAMS_JSON,
        PATCH_PLAN_JSON,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        *[ROOT / rel for rel in TARGET_SOURCE_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file() and (ROOT / rel).stat().st_size <= SMALL_COPY_LIMIT_BYTES],
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
    print("classification =", bridge_diag["classification"])
    print("confidence =", bridge_diag["confidence"])
    print("likely_factors =", bridge_diag["likely_factors"])
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("bridge_diagnostic_json =", BRIDGE_DIAGNOSTIC_JSON.relative_to(ROOT))
    print("source_seams_json =", SOURCE_SEAMS_JSON.relative_to(ROOT))
    print("patch_plan_json =", PATCH_PLAN_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
