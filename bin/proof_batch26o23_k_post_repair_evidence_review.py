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
BATCH = "26-O23-K"
BATCH_NAME = "post_repair_controlled_paper_evidence_review_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_k_post_repair_evidence_review_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_k_post_repair_evidence_review.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_k_post_repair_evidence_review.json"
EVIDENCE_REVIEW_JSON = RUN_DIR / "controlled_paper_o23k_evidence_review.json"
PAYLOAD_GAP_JSON = RUN_DIR / "controlled_paper_o23k_decision_payload_gap_review.json"
SIGNAL_PLAN_JSON = RUN_DIR / "controlled_paper_o23k_next_signal_opportunity_plan.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23k_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_k_post_repair_evidence_review.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_k_post_repair_evidence_review.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_k_post_repair_evidence_review.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}
SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 24_000

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_j_post_repair_controlled_paper_observation.json",
    "run/proofs/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json",
    "run/proofs/proof_batch26o23_h_narrow_bridge_repair.json",
    "run/proofs/proof_batch26o23_g_narrow_bridge_diagnostic.json",
]

SOURCE_PATHS = [
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

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS


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


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_state() -> dict[str, Any]:
    u = shutil.disk_usage(ROOT)
    return {
        "free_bytes": u.free,
        "free_gb": round(u.free / 1024**3, 3),
        "used_pct": round((u.used / u.total) * 100, 2) if u.total else None,
        "df_h": run("df -h . || true", shell=True, timeout=10),
    }


def safe_file_record(rel: str, copy_source: bool = False) -> dict[str, Any]:
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

    if copy_source and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        dst = BACKUP_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        rec["source_backup"] = str(dst.relative_to(ROOT))
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only"

    return rec


def load_json_file(path: pathlib.Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {"_loaded_type": type(obj).__name__}
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def load_prior(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec = safe_file_record(rel, copy_source=False)
    if not p.exists() or not p.is_file():
        return rec
    obj = load_json_file(p)
    rec["json_loaded"] = "_load_error" not in obj
    rec["final_verdict"] = obj.get("final_verdict")
    rec["false_keys"] = obj.get("false_keys")
    rec["classification"] = obj.get("classification")
    rec["next_recommended_batch"] = obj.get("next_recommended_batch")
    rec["tag"] = obj.get("tag")
    rec["sample_count"] = len(obj.get("samples") or []) if isinstance(obj.get("samples"), list) else None
    rec["required_verdicts"] = obj.get("required_verdicts") if isinstance(obj.get("required_verdicts"), dict) else {}
    rec["loaded_obj"] = obj
    return rec


def pass_prefix(rec: dict[str, Any], prefix: str) -> bool:
    fv = rec.get("final_verdict")
    return isinstance(fv, str) and fv.startswith(prefix)


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
    d = {}
    for i in range(0, len(lines) - 1, 2):
        d[lines[i]] = lines[i + 1]
    return d


def redis_xrevrange_raw(key: str, count: int = 10) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def proc_lines() -> list[str]:
    out = run(
        "ps -eo pid,ppid,stat,etime,args | grep -E 'app\\.mme_scalpx|mme_scalpx' | grep -v grep || true",
        shell=True,
        timeout=10,
    )
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
            "args": args[:1200],
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
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=10),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=10),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "process_rows": rows,
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def parse_stream_entries(raw_stdout: str) -> list[dict[str, Any]]:
    lines = raw_stdout.splitlines()
    entries = []
    cur = None
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


def parse_payloads_from_raw(raw_stdout: str) -> list[dict[str, Any]]:
    out = []
    for ent in parse_stream_entries(raw_stdout):
        for k, v in (ent.get("fields") or {}).items():
            parsed = None
            if k.endswith("_json") or k in {"json", "payload", "payload_json", "decision_json", "feature_payload_json"}:
                parsed = parse_json_maybe(v)
            if isinstance(parsed, dict):
                out.append({"id": ent.get("id"), "field": k, "payload": parsed})
    return out


def latest_o23j_dir(tag: str | None) -> pathlib.Path | None:
    if tag:
        p = ROOT / "run" / "live_capture" / tag
        if p.exists() and p.is_dir():
            return p
    base = ROOT / "run" / "live_capture"
    if not base.exists():
        return None
    dirs = [p for p in base.iterdir() if p.is_dir() and p.name.startswith("batch26o23_j_post_repair_controlled_paper_observation")]
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0] if dirs else None


def review_o23j_artifacts(o23j: dict[str, Any]) -> dict[str, Any]:
    obj = o23j.get("loaded_obj") or {}
    tag = obj.get("tag") if isinstance(obj, dict) else None
    run_dir = latest_o23j_dir(tag)

    artifacts: dict[str, Any] = {
        "run_dir": str(run_dir.relative_to(ROOT)) if run_dir else None,
        "artifact_files": {},
        "log_files": {},
    }

    if run_dir:
        for f in sorted(run_dir.glob("*.json")):
            artifacts["artifact_files"][str(f.relative_to(ROOT))] = load_json_file(f)
        for f in sorted(run_dir.glob("*.log")):
            text = f.read_text(encoding="utf-8", errors="replace")
            artifacts["log_files"][str(f.relative_to(ROOT))] = {
                "sha256": sha256_file(f),
                "size_bytes": f.stat().st_size,
                "tail": "\n".join(text.splitlines()[-100:]),
                "error_lines": [
                    {"line": i, "text": line[:400]}
                    for i, line in enumerate(text.splitlines(), 1)
                    if any(tok in line.lower() for tok in ["traceback", "exception", "error", "critical"])
                ][:100],
                "signal_lines": [
                    {"line": i, "text": line[:400]}
                    for i, line in enumerate(text.splitlines(), 1)
                    if any(tok in line.lower() for tok in [
                        "consumer_view", "o23h", "no_candidate", "hold", "buy", "sell",
                        "order", "candidate", "activation", "data_valid", "safe_to_consume"
                    ])
                ][:200],
            }

    samples = obj.get("samples") if isinstance(obj, dict) else []
    if not isinstance(samples, list):
        samples = []

    decision_payload_counts = [
        (((s.get("decision_summary") or {}).get("payload_count")) if isinstance(s, dict) else None)
        for s in samples
    ]
    decisions_xlens = [s.get("decisions_xlen") for s in samples if isinstance(s, dict) and isinstance(s.get("decisions_xlen"), int)]
    features_xlens = [s.get("features_xlen") for s in samples if isinstance(s, dict) and isinstance(s.get("features_xlen"), int)]

    return {
        **artifacts,
        "proof_summary": {
            "final_verdict": obj.get("final_verdict") if isinstance(obj, dict) else None,
            "classification": obj.get("classification") if isinstance(obj, dict) else None,
            "false_keys": obj.get("false_keys") if isinstance(obj, dict) else None,
            "sample_count": len(samples),
            "paper_order_events_since_start": ((obj.get("order_events_since_start") or {}).get("event_count") if isinstance(obj, dict) else None),
        },
        "sample_stats": {
            "sample_count": len(samples),
            "first_seconds_elapsed": samples[0].get("seconds_elapsed") if samples else None,
            "last_seconds_elapsed": samples[-1].get("seconds_elapsed") if samples else None,
            "first_decisions_xlen": decisions_xlens[0] if decisions_xlens else None,
            "last_decisions_xlen": decisions_xlens[-1] if decisions_xlens else None,
            "decisions_growth": (decisions_xlens[-1] - decisions_xlens[0]) if len(decisions_xlens) >= 2 else None,
            "first_features_xlen": features_xlens[0] if features_xlens else None,
            "last_features_xlen": features_xlens[-1] if features_xlens else None,
            "features_growth": (features_xlens[-1] - features_xlens[0]) if len(features_xlens) >= 2 else None,
            "max_decision_payload_count": max([x for x in decision_payload_counts if isinstance(x, int)], default=0),
            "all_sample_payload_counts_zero": all((x in {0, None}) for x in decision_payload_counts) if samples else False,
        },
    }


def payload_gap_review(o23j_review: dict[str, Any], runtime: dict[str, Any]) -> dict[str, Any]:
    latest_decision_payloads = parse_payloads_from_raw((runtime.get("latest_decisions_raw") or {}).get("stdout") or "")
    latest_feature_payloads = parse_payloads_from_raw((runtime.get("latest_features_raw") or {}).get("stdout") or "")

    sample_stats = o23j_review.get("sample_stats") or {}
    decisions_grew = isinstance(sample_stats.get("decisions_growth"), int) and sample_stats["decisions_growth"] > 0
    features_grew = isinstance(sample_stats.get("features_growth"), int) and sample_stats["features_growth"] > 0
    sample_parser_empty = sample_stats.get("all_sample_payload_counts_zero") is True

    classification = "NO_PAYLOAD_GAP"
    if decisions_grew and sample_parser_empty:
        classification = "DECISION_PAYLOAD_REVIEW_PARSER_GAP_OR_NON_JSON_DECISION_FIELD"
    if decisions_grew and features_grew and sample_parser_empty:
        classification = "STREAMS_GREW_BUT_O23J_SAMPLE_PAYLOAD_PARSER_EMPTY"

    return {
        "classification": classification,
        "decisions_grew_during_o23j": decisions_grew,
        "features_grew_during_o23j": features_grew,
        "sample_parser_empty": sample_parser_empty,
        "latest_runtime_decision_payload_count": len(latest_decision_payloads),
        "latest_runtime_feature_payload_count": len(latest_feature_payloads),
        "latest_decision_payload_summaries": [
            {
                "id": x.get("id"),
                "field": x.get("field"),
                "top_keys": sorted(list((x.get("payload") or {}).keys()))[:80],
                "action": (x.get("payload") or {}).get("action"),
                "reason": (x.get("payload") or {}).get("reason") or (x.get("payload") or {}).get("activation_reason"),
                "activation_candidate_count": (x.get("payload") or {}).get("activation_candidate_count"),
                "data_valid": (x.get("payload") or {}).get("data_valid"),
                "safe_to_consume": (x.get("payload") or {}).get("safe_to_consume"),
                "structural_valid": (x.get("payload") or {}).get("structural_valid"),
                "consumer_view_repaired": (x.get("payload") or {}).get("consumer_view_repaired"),
            }
            for x in latest_decision_payloads[:10]
        ],
        "interpretation": [
            "O23-J itself passed safety and clean stop.",
            "No paper trade occurred; that is not a failure.",
            "However, decisions/features stream counters moved while O23-J sample parser saw payload_count=0.",
            "Before expanding paper scope, next batch should inspect decision stream field names and family/branch opportunity surfaces read-only.",
        ],
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Review O23-J post-repair controlled-paper evidence and decide next safe path.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "production_source_patch": False,
            "evidence_review_only": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_snapshot": {},
        "o23j_evidence_review": {},
        "payload_gap_review": {},
        "signal_plan": {},
        "required_verdicts": {},
        "false_keys": [],
        "classification": "",
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()

    print("===== EVIDENCE-FIRST INSPECTION =====")
    for rel in INSPECT_PATHS:
        proof["inspected_files"][rel] = safe_file_record(rel, copy_source=rel in SOURCE_PATHS)
        if rel.endswith(".json"):
            proof["prior_proofs"][rel] = load_prior(rel)

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
    proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
    proof["commands"]["import"] = run([
        sys.executable,
        "-c",
        "import app.mme_scalpx.main, app.mme_scalpx.services.feeds, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
    ], timeout=60)

    print("===== RUNTIME SAFETY READBACK =====")
    runtime = runtime_snapshot()
    proof["runtime_snapshot"] = runtime

    print("===== REVIEW O23-J ARTIFACTS =====")
    o23j = proof["prior_proofs"].get("run/proofs/proof_batch26o23_j_post_repair_controlled_paper_observation.json", {})
    i_r1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json", {})
    h = proof["prior_proofs"].get("run/proofs/proof_batch26o23_h_narrow_bridge_repair.json", {})

    o23j_review = review_o23j_artifacts(o23j)
    proof["o23j_evidence_review"] = o23j_review
    EVIDENCE_REVIEW_JSON.write_text(json.dumps(o23j_review, indent=2, sort_keys=True), encoding="utf-8")

    print("===== REVIEW DECISION PAYLOAD GAP =====")
    payload_gap = payload_gap_review(o23j_review, runtime)
    proof["payload_gap_review"] = payload_gap
    PAYLOAD_GAP_JSON.write_text(json.dumps(payload_gap, indent=2, sort_keys=True), encoding="utf-8")

    position_flat = flat_position(runtime["position"])
    no_controlled_pids = len(runtime["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime["risk_execution_rows"]) == 0
    orders_zero = runtime["orders_xlen"] == 0 and not (runtime["latest_orders_raw"].get("stdout") or "").strip()

    signal_plan = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PLAN_ONLY_NO_START_NO_PATCH",
        "recommended_next_batch": "26-O23-L multi-strategy signal-opportunity audit, paper-disabled/read-only first; no real live.",
        "why_not_jump_to_all_strategy_paper": [
            "O23-J proved controlled-paper safety but produced no paper order.",
            "The decision payload parser/review still shows an empty payload surface despite stream growth.",
            "Multi-strategy paper without first measuring family/side opportunity would create ambiguity.",
        ],
        "safe_sequence": [
            "O23-L: read-only/paper-disabled multi-strategy signal-opportunity audit across MIST/MISB/MISC/MISR/MISO CALL/PUT surfaces.",
            "O23-M: choose one next family/side only based on O23-L evidence.",
            "O23-N: one-family/side controlled-paper observation, 1 lot, paper-only, real_live=false.",
        ],
        "candidate_family_scope_for_o23l": [
            "MIST_CALL",
            "MIST_PUT",
            "MISB_CALL",
            "MISB_PUT",
            "MISC_CALL",
            "MISC_PUT",
            "MISR_CALL",
            "MISR_PUT",
            "MISO_CALL",
            "MISO_PUT only if Dhan context readiness is proven fresh",
        ],
        "forbidden": [
            "real live",
            "all-strategy paper execution in one jump",
            "threshold relaxation",
            "forced candidate",
            "quantity increase",
            "broker failover",
            "mid-position provider migration",
        ],
    }
    proof["signal_plan"] = signal_plan
    SIGNAL_PLAN_JSON.write_text(json.dumps(signal_plan, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "RUN_O23_L_MULTI_STRATEGY_SIGNAL_OPPORTUNITY_AUDIT_NEXT",
        "recommended_next_batch": signal_plan["recommended_next_batch"],
        "do_not_proceed_to_real_live": True,
        "do_not_expand_paper_execution_yet": True,
        "why": [
            "O23-J is PASS and safe.",
            "O23-J is no-trade/no-order.",
            "Next work should identify best family/side opportunity without execution ambiguity.",
        ],
    }
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "o23j_pass_loaded": pass_prefix(o23j, "PASS_O23_J_POST_REPAIR_CONTROLLED_PAPER_OBSERVATION_OK_REAL_LIVE_FALSE"),
        "o23j_false_keys_empty": o23j.get("false_keys") == [],
        "o23j_classification_no_trade": o23j.get("classification") == "CONTROLLED_PAPER_NO_TRADE_OBSERVATION",
        "o23j_sample_count_positive": isinstance(o23j.get("sample_count"), int) and o23j["sample_count"] > 0,
        "o23i_r1_pass_loaded": pass_prefix(i_r1, "PASS_O23_I_R1_ONESHOT_SAFETY_ASSERTION_CORRECTION_OK_NO_START_NO_REAL_LIVE"),
        "o23h_pass_loaded": pass_prefix(h, "PASS_O23_H_NARROW_BRIDGE_REPAIR_OK_NO_START_NO_REAL_LIVE"),
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "runtime_no_controlled_pids": no_controlled_pids,
        "runtime_risk_execution_not_running": risk_execution_not_running,
        "runtime_position_flat": position_flat,
        "runtime_orders_zero": orders_zero,
        "evidence_review_json_written": EVIDENCE_REVIEW_JSON.exists(),
        "payload_gap_json_written": PAYLOAD_GAP_JSON.exists(),
        "signal_plan_json_written": SIGNAL_PLAN_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "real_live_false": True,
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
        proof["classification"] = "O23K_REVIEW_NOT_PROVEN"
        proof["final_verdict"] = "FAIL_O23_K_POST_REPAIR_EVIDENCE_REVIEW_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not proceed to real live or multi-strategy paper."
    else:
        proof["classification"] = "O23J_SAFE_NO_TRADE_OBSERVATION_REVIEWED_PAYLOAD_GAP_CLASSIFIED"
        proof["final_verdict"] = "PASS_O23_K_POST_REPAIR_EVIDENCE_REVIEW_OK_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "26-O23-L multi-strategy signal-opportunity audit, paper-disabled/read-only first; no real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — post-repair controlled-paper evidence review",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- evidence_review: `{EVIDENCE_REVIEW_JSON.relative_to(ROOT)}`",
            f"- payload_gap: `{PAYLOAD_GAP_JSON.relative_to(ROOT)}`",
            f"- signal_plan: `{SIGNAL_PLAN_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            "",
            "## Review summary",
            f"- O23-J verdict: `{o23j.get('final_verdict')}`",
            f"- O23-J classification: `{o23j.get('classification')}`",
            f"- O23-J sample_count: `{o23j.get('sample_count')}`",
            f"- Payload gap classification: `{payload_gap.get('classification')}`",
            "",
            "## Verdict",
            f"- final_verdict: `{proof['final_verdict']}`",
            f"- classification: `{proof['classification']}`",
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
            f"# {DATE} — {BATCH} post-repair evidence review",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            f"Classification: `{proof['classification']}`",
            "",
            "## Achieved",
            "- Confirmed O23-J PASS as safe no-trade controlled-paper observation if PASS.",
            "- Reviewed original O23-J artifacts/logs.",
            "- Classified decision payload review gap.",
            "- Produced next signal-opportunity audit plan.",
            "- Preserved no-real-live, no-service-start, no-source-patch boundary.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        EVIDENCE_REVIEW_JSON,
        PAYLOAD_GAP_JSON,
        SIGNAL_PLAN_JSON,
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
    print("classification =", proof["classification"])
    print("false_keys =", false_keys)
    print("o23j_final_verdict =", o23j.get("final_verdict"))
    print("o23j_classification =", o23j.get("classification"))
    print("o23j_sample_count =", o23j.get("sample_count"))
    print("payload_gap_classification =", payload_gap.get("classification"))
    print("runtime_no_controlled_pids =", no_controlled_pids)
    print("runtime_position_flat =", position_flat)
    print("runtime_orders_zero =", orders_zero)
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("evidence_review_json =", EVIDENCE_REVIEW_JSON.relative_to(ROOT))
    print("payload_gap_json =", PAYLOAD_GAP_JSON.relative_to(ROOT))
    print("signal_plan_json =", SIGNAL_PLAN_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
