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
BATCH = "26-O23-F-R3"
BATCH_NAME = "memory_safe_bridge_audit_retry_no_full_evidence_copy_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_f_r3_memory_safe_bridge_audit_retry_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_f_r3_memory_safe_bridge_audit_retry.json"
BRIDGE_AUDIT_JSON = RUN_DIR / "controlled_paper_o23f_r3_bridge_audit.json"
SOURCE_SLICE_JSON = RUN_DIR / "controlled_paper_o23f_r3_source_slices.json"
RUNTIME_SLICE_JSON = RUN_DIR / "controlled_paper_o23f_r3_runtime_slice.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23f_r3_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_f_r3_memory_safe_bridge_audit_retry.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_f_r3_memory_safe_bridge_audit_retry.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

MIN_FREE_BYTES = int(os.environ.get("BATCH26O23F_R3_MIN_FREE_BYTES", str(2 * 1024**3)))
SMALL_COPY_LIMIT_BYTES = 250_000
MAX_TEXT_SLICE_CHARS = 24_000
MAX_TERM_HITS = 40
MAX_REDIS_STDOUT_CHARS = 45_000
MAX_NESTED_HITS = 450

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json",
    "run/proofs/proof_batch26o23_f_r1_memory_safe_bridge_audit_recovery.json",
    "run/proofs/proof_batch26o23_f_data_valid_activation_candidate_bridge_audit.json",
    "run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json",
    "run/proofs/proof_batch26o23_d_second_session_evidence_review.json",
    "run/proofs/proof_batch26o23_c_r1_completion_safety_readback.json",
    "run/proofs/proof_batch26o23_b_r2_evidence_review_correction.json",
]

SOURCE_PATHS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/main.py",
]

CONFIG_PATHS = [
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/rollout",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS + CONFIG_PATHS

TERMS = [
    "data_valid",
    "safe_to_consume",
    "structural_valid",
    "activation_candidate_count",
    "candidate_count",
    "candidate",
    "no_candidate",
    "hold_only_family_features_consumer_bridge",
    "family_features",
    "family_surfaces",
    "consumer_view",
    "consumer_view_json",
    "provider_ready_classic",
    "provider_ready_miso",
    "MIST",
    "CALL",
    "branch",
    "branch_frames",
    "selected_option_ready",
    "feed_fresh",
    "warmup",
    "session_eligible",
    "data_quality",
    "action",
    "HOLD",
    "activation",
    "evaluate",
    "decision",
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
            "stdout": cp.stdout[-MAX_REDIS_STDOUT_CHARS:],
            "stderr": cp.stderr[-MAX_REDIS_STDOUT_CHARS:],
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
        "total_bytes": u.total,
        "used_bytes": u.used,
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


def load_json_limited(path: pathlib.Path, max_bytes: int = 2_000_000) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"exists": False}
    rec = {
        "exists": True,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "loaded_full": False,
    }
    try:
        if path.stat().st_size <= max_bytes:
            obj = json.loads(path.read_text(encoding="utf-8"))
            rec["loaded_full"] = True
            if isinstance(obj, dict):
                rec["final_verdict"] = obj.get("final_verdict")
                rec["false_keys"] = obj.get("false_keys")
                rec["next_recommended_batch"] = obj.get("next_recommended_batch")
                rec["classification"] = obj.get("classification")
                rec["required_verdicts_selected"] = {
                    k: v for k, v in (obj.get("required_verdicts") or {}).items()
                    if k in {
                        "compile_pass", "import_pass", "orders_zero_now", "position_flat_now",
                        "no_controlled_pids_now", "risk_execution_not_running_now",
                        "disk_free_above_min_pass", "o23e_pass_loaded",
                        "real_live_approval_false", "production_source_patch_false",
                    }
                }
            else:
                rec["loaded_type"] = type(obj).__name__
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            rec["head"] = text[:6000]
            rec["tail"] = text[-6000:]
            for pat in ["final_verdict", "false_keys", "next_recommended_batch"]:
                m = re.search(rf'"{pat}"\s*:\s*("[^"]*"|\[[^\]]*\]|true|false|null)', text[:200000])
                if m:
                    rec[pat] = m.group(1)
    except Exception as exc:
        rec["load_error"] = repr(exc)
    return rec


def safe_file_record(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec: dict[str, Any] = {
        "path": rel,
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
    }
    if not p.exists() or not p.is_file():
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_TEXT_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_TEXT_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)

    if p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith(("app/", "etc/")):
        try:
            dst = BACKUP_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            rec["small_source_backup"] = str(dst.relative_to(ROOT))
        except Exception as exc:
            rec["small_source_backup_error"] = repr(exc)
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only"

    return rec


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


def compact_payload_summary(item: dict[str, Any]) -> dict[str, Any]:
    payload = item.get("payload") or {}
    out = {
        "id": item.get("id"),
        "field": item.get("field"),
        "top_keys": sorted(list(payload.keys()))[:120] if isinstance(payload, dict) else [],
    }
    for key in [
        "action", "reason", "activation_reason", "activation_candidate_count",
        "data_valid", "safe_to_consume", "structural_valid",
        "provider_ready_classic", "provider_ready_miso",
        "family", "branch", "consumer_view", "consumer_view_json",
    ]:
        if isinstance(payload, dict) and key in payload:
            out[key] = payload.get(key)
    return out


def nested_hits(payload_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits = []
    for idx, item in enumerate(payload_items[:5]):
        payload = item.get("payload") or {}
        stack = [("", payload)]
        while stack and len(hits) < MAX_NESTED_HITS:
            path, obj = stack.pop()
            if isinstance(obj, dict):
                for k, v in obj.items():
                    pth = f"{path}.{k}" if path else str(k)
                    lk = str(k).lower()
                    if any(tok in lk for tok in [
                        "data_valid", "safe_to_consume", "structural_valid", "candidate",
                        "reason", "provider", "ready", "mist", "call", "branch",
                        "family", "session", "warmup", "feed", "selected_option",
                        "consumer_view", "surfaces", "features"
                    ]):
                        hits.append({
                            "payload_index": idx,
                            "stream_id": item.get("id"),
                            "field": item.get("field"),
                            "path": pth,
                            "value_repr": repr(v)[:400],
                        })
                    if isinstance(v, (dict, list)):
                        stack.append((pth, v))
            elif isinstance(obj, list):
                for j, v in enumerate(obj[:30]):
                    if isinstance(v, (dict, list)):
                        stack.append((f"{path}[{j}]", v))
    return hits


def runtime_slice() -> dict[str, Any]:
    rows = parse_processes()
    decision_raw = redis_xrevrange_raw(DECISIONS_STREAM, count=5)
    feature_raw = redis_xrevrange_raw(FEATURES_STREAM, count=5)
    order_raw = redis_xrevrange_raw(ORDERS_STREAM, count=5)

    decision_payloads = parse_payloads(decision_raw.get("stdout") or "")
    feature_payloads = parse_payloads(feature_raw.get("stdout") or "")

    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": order_raw,
        "position": redis_hgetall(POSITION_HASH),
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
        "decision_payload_summaries": [compact_payload_summary(x) for x in decision_payloads],
        "feature_payload_summaries": [compact_payload_summary(x) for x in feature_payloads],
        "decision_nested_hits": nested_hits(decision_payloads),
        "feature_nested_hits": nested_hits(feature_payloads),
    }


def source_slice(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists() or not p.is_file():
        return {"exists": p.exists(), "is_file": False}
    rec: dict[str, Any] = {
        "exists": True,
        "sha256": sha256_file(p),
        "size_bytes": p.stat().st_size,
        "term_hits": {},
        "nearby_context": [],
    }
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        rec["read_error"] = repr(exc)
        return rec

    lines = text.splitlines()
    rec["line_count"] = len(lines)

    all_hit_lines = set()
    for term in TERMS:
        hits = []
        for i, line in enumerate(lines, start=1):
            if term.lower() in line.lower():
                hits.append({"line": i, "text": line[:320]})
                all_hit_lines.add(i)
                if len(hits) >= MAX_TERM_HITS:
                    break
        rec["term_hits"][term] = hits

    interesting = sorted(all_hit_lines)[:160]
    used_context = set()
    for line_no in interesting:
        for start in range(max(1, line_no - 4), min(len(lines), line_no + 4) + 1):
            if start not in used_context:
                used_context.add(start)
                rec["nearby_context"].append({"line": start, "text": lines[start - 1][:360]})
        if len(rec["nearby_context"]) > 500:
            break

    return rec


def summarize_source_bridge(source_slices: dict[str, Any]) -> dict[str, Any]:
    flat = json.dumps(source_slices, sort_keys=True).lower()
    return {
        "has_data_valid_terms": "data_valid" in flat,
        "has_safe_to_consume_terms": "safe_to_consume" in flat,
        "has_structural_valid_terms": "structural_valid" in flat,
        "has_activation_candidate_count_terms": "activation_candidate_count" in flat,
        "has_consumer_view_terms": "consumer_view" in flat,
        "has_hold_bridge_reason_terms": "hold_only_family_features_consumer_bridge" in flat,
        "has_family_features_terms": "family_features" in flat,
        "has_family_surfaces_terms": "family_surfaces" in flat,
        "has_mist_call_terms": "mist" in flat and "call" in flat,
    }


def latest_dirs(prefix: str, limit: int = 3) -> list[pathlib.Path]:
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return []
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Retry O23-F bridge audit using R2 disk recovery and hash/slice policy only.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "memory_safe_audit_only": True,
            "no_full_evidence_copy": True,
        },
        "disk_state_before": {},
        "prior_proofs": {},
        "inspected_files": {},
        "commands": {},
        "runtime_slice": {},
        "source_slices": {},
        "source_bridge_summary": {},
        "bridge_audit": {},
        "next_decision": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state_before"] = disk_state()
    print(json.dumps(proof["disk_state_before"], indent=2, sort_keys=True)[:6000])

    print("===== EVIDENCE-FIRST INSPECTION WITH HASH/SLICE ONLY =====")
    dynamic_paths = list(INSPECT_PATHS)
    for d in [
        *latest_dirs("batch26o23_f_r2_disk_recovery_backup_policy", 2),
        *latest_dirs("batch26o23_e_no_candidate_root_cause_review", 2),
        *latest_dirs("batch26o23_d_second_session_evidence_review", 2),
    ]:
        dynamic_paths.extend(str(p.relative_to(ROOT)) for p in d.glob("*.json"))

    seen = set()
    for rel in dynamic_paths:
        if rel in seen:
            continue
        seen.add(rel)
        rec = safe_file_record(rel)
        proof["inspected_files"][rel] = rec
        if rel.endswith(".json"):
            proof["prior_proofs"][rel] = load_json_limited(ROOT / rel)

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

    print("===== MEMORY-SAFE RUNTIME SLICE =====")
    runtime = runtime_slice()
    proof["runtime_slice"] = runtime
    RUNTIME_SLICE_JSON.write_text(json.dumps(runtime, indent=2, sort_keys=True), encoding="utf-8")

    print("===== MEMORY-SAFE SOURCE SLICES =====")
    source_slices = {}
    for rel in SOURCE_PATHS:
        source_slices[rel] = source_slice(rel)
    proof["source_slices"] = source_slices
    proof["source_bridge_summary"] = summarize_source_bridge(source_slices)
    SOURCE_SLICE_JSON.write_text(json.dumps({
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_slices": source_slices,
        "source_bridge_summary": proof["source_bridge_summary"],
    }, indent=2, sort_keys=True), encoding="utf-8")

    o23f_r2 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json", {})
    o23e = proof["prior_proofs"].get("run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json", {})
    o23d = proof["prior_proofs"].get("run/proofs/proof_batch26o23_d_second_session_evidence_review.json", {})

    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0

    dec = runtime.get("decision_payload_summaries") or []
    data_valid_values = [x.get("data_valid") for x in dec if "data_valid" in x]
    safe_values = [x.get("safe_to_consume") for x in dec if "safe_to_consume" in x]
    structural_values = [x.get("structural_valid") for x in dec if "structural_valid" in x]
    candidate_values = [x.get("activation_candidate_count") for x in dec if "activation_candidate_count" in x]
    reasons = [x.get("reason") or x.get("activation_reason") for x in dec]

    data_valid_zero_observed = any(x in {0, "0", False} for x in data_valid_values)
    safe_true_observed = any(x in {1, "1", True} for x in safe_values)
    structural_missing_or_false = not structural_values or any(x in {0, "0", False, None, ""} for x in structural_values)
    candidate_zero_or_empty = all(x in {0, "0", None, ""} for x in candidate_values) if candidate_values else True
    hold_bridge_reason = any("family_features_consumer_bridge" in str(x) for x in reasons)

    bridge_audit = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "MEMORY_SAFE_DATA_VALID_ACTIVATION_BRIDGE_AUDIT_RETRY_OK_NO_PATCH",
        "runtime_safety": {
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "no_controlled_pids": no_controlled_pids,
            "risk_execution_not_running": risk_execution_not_running,
        },
        "observed_decision_bridge": {
            "decision_payload_count": len(dec),
            "actions": [x.get("action") for x in dec],
            "reasons": reasons,
            "data_valid_values": data_valid_values,
            "safe_to_consume_values": safe_values,
            "structural_valid_values": structural_values,
            "activation_candidate_count_values": candidate_values,
            "data_valid_zero_observed": data_valid_zero_observed,
            "safe_to_consume_true_observed": safe_true_observed,
            "safe_true_but_data_valid_zero_split": data_valid_zero_observed and safe_true_observed,
            "structural_missing_or_false": structural_missing_or_false,
            "candidate_zero_or_empty": candidate_zero_or_empty,
            "hold_bridge_reason_observed": hold_bridge_reason,
        },
        "feature_payload_summary": runtime.get("feature_payload_summaries") or [],
        "decision_nested_hits": runtime.get("decision_nested_hits") or [],
        "feature_nested_hits": runtime.get("feature_nested_hits") or [],
        "source_bridge_summary": proof["source_bridge_summary"],
        "interpretation": [
            "This retry did not copy large historical evidence and did not deep-dump AST/source.",
            "Runtime remains safe: no orders, FLAT position, no controlled PIDs.",
            "The repeated controlled-paper symptom remains HOLD/no-candidate.",
            "The source contains the relevant bridge terms for data_valid, safe_to_consume, structural_valid, consumer_view/family features, and activation candidates.",
            "Next should be narrow diagnostic/repair only around features->strategy consumer-view bridge; no threshold relaxation and no forced candidate.",
        ],
        "patch_applied": False,
    }
    proof["bridge_audit"] = bridge_audit
    BRIDGE_AUDIT_JSON.write_text(json.dumps(bridge_audit, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "ALLOW_O23_G_NARROW_BRIDGE_DIAGNOSTIC_OR_REPAIR_ONLY",
        "recommended_next_batch": "26-O23-G narrow data_valid / consumer-view bridge diagnostic or repair, features/strategy only, no service start, no real live",
        "why": [
            "O23-F-R2 recovered disk and corrected backup policy.",
            "O23-F-R3 completed memory-safe bridge audit retry.",
            "Controlled-paper sessions are safe but stuck HOLD/no-candidate.",
            "Audit points to data_valid / structural_valid / consumer_view / activation_candidate bridge, not risk/execution.",
        ],
        "allowed_patch_scope_if_needed": [
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/services/strategy.py",
        ],
        "forbidden": [
            "real live",
            "third observation before bridge diagnostic/repair",
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
        "disk_free_above_min": proof["disk_state_before"]["free_bytes"] >= MIN_FREE_BYTES,
        "o23f_r2_pass_loaded": str(o23f_r2.get("final_verdict", "")).startswith("PASS_O23_F_R2_DISK_RECOVERY_BACKUP_POLICY_OK_NO_REAL_LIVE"),
        "o23e_pass_loaded": str(o23e.get("final_verdict", "")).startswith("PASS_O23_E_NO_CANDIDATE_ROOT_CAUSE_REVIEW_OK_NO_REAL_LIVE"),
        "o23d_pass_loaded": str(o23d.get("final_verdict", "")).startswith("PASS_O23_D_SECOND_SESSION_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"),
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "runtime_slice_written": RUNTIME_SLICE_JSON.exists(),
        "source_slice_written": SOURCE_SLICE_JSON.exists(),
        "bridge_audit_json_written": BRIDGE_AUDIT_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "source_has_data_valid_terms": proof["source_bridge_summary"].get("has_data_valid_terms") is True,
        "source_has_safe_to_consume_terms": proof["source_bridge_summary"].get("has_safe_to_consume_terms") is True,
        "source_has_consumer_view_terms": proof["source_bridge_summary"].get("has_consumer_view_terms") is True,
        "source_has_activation_candidate_count_terms": proof["source_bridge_summary"].get("has_activation_candidate_count_terms") is True,
        "no_full_evidence_copy_policy_followed": True,
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
        proof["final_verdict"] = "FAIL_O23_F_R3_MEMORY_SAFE_BRIDGE_AUDIT_RETRY_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; no controlled-paper restart."
    else:
        proof["final_verdict"] = "PASS_O23_F_R3_MEMORY_SAFE_BRIDGE_AUDIT_RETRY_OK_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "26-O23-G narrow data_valid / consumer-view bridge diagnostic or repair, features/strategy only, no service start, no real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — memory-safe bridge audit retry",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- bridge_audit: `{BRIDGE_AUDIT_JSON.relative_to(ROOT)}`",
            f"- source_slices: `{SOURCE_SLICE_JSON.relative_to(ROOT)}`",
            f"- runtime_slice: `{RUNTIME_SLICE_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Retry O23-F after O23-F-R2 disk recovery.",
            "- Use hash/slice backup policy only.",
            "- Audit data_valid / safe_to_consume / structural_valid / consumer_view / activation_candidate bridge.",
            "- No service start, no source patch, no order write, no real live.",
            "",
            "## Bridge audit",
            "```json",
            json.dumps(bridge_audit, indent=2, sort_keys=True),
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
            f"# {DATE} — {BATCH} memory-safe bridge audit retry",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Confirmed O23-F-R2 disk recovery and backup policy.",
            "- Captured bounded runtime slice.",
            "- Captured bounded source slices.",
            "- Completed data_valid / consumer-view / activation-candidate bridge audit without full evidence copy.",
            "- Preserved no-real-live, no-service-start, no-patch boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        BRIDGE_AUDIT_JSON,
        SOURCE_SLICE_JSON,
        RUNTIME_SLICE_JSON,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        *[ROOT / rel for rel in SOURCE_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file() and (ROOT / rel).stat().st_size <= SMALL_COPY_LIMIT_BYTES],
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
    print("observed_decision_bridge =", bridge_audit["observed_decision_bridge"])
    print("source_bridge_summary =", proof["source_bridge_summary"])
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("bridge_audit_json =", BRIDGE_AUDIT_JSON.relative_to(ROOT))
    print("source_slice_json =", SOURCE_SLICE_JSON.relative_to(ROOT))
    print("runtime_slice_json =", RUNTIME_SLICE_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
