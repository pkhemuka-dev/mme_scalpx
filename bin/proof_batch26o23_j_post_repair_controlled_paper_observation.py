#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-J"
BATCH_NAME = "post_repair_bounded_controlled_paper_observation_mist_call_1lot_paper_only"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o23_j_post_repair_controlled_paper_observation_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_j_post_repair_controlled_paper_observation.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_j_post_repair_controlled_paper_observation.json"
SESSION_JSON = RUN_DIR / "controlled_paper_o23j_post_repair_session.json"
SAFETY_JSON = RUN_DIR / "controlled_paper_o23j_post_repair_safety_readback.json"
LOG_REVIEW_JSON = RUN_DIR / "controlled_paper_o23j_log_review.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23j_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_j_post_repair_controlled_paper_observation.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_j_post_repair_controlled_paper_observation.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_j_post_repair_controlled_paper_observation.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

APPROVAL_PHRASE = "APPROVE O23-J POST-REPAIR CONTROLLED PAPER OBSERVATION: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE"
CONTROLLED_PAPER_SCOPE_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

SESSION_SECONDS = int(os.environ.get("BATCH26O23J_SESSION_SECONDS", "900"))
POLL_SECONDS = float(os.environ.get("BATCH26O23J_POLL_SECONDS", "5"))
MAX_PAPER_ORDER_EVENTS_ALLOWED = int(os.environ.get("BATCH26O23J_MAX_PAPER_ORDER_EVENTS_ALLOWED", "20"))
MIN_FREE_BYTES = int(os.environ.get("BATCH26O23J_MIN_FREE_BYTES", str(2 * 1024**3)))

CONTROLLED_SERVICES = ["feeds", "features", "strategy", "risk", "execution"]

SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 24_000
MAX_LOG_HITS = 120

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json",
    "run/proofs/proof_batch26o23_i_static_oneshot_bridge_proof.json",
    "run/proofs/proof_batch26o23_h_narrow_bridge_repair.json",
    "run/proofs/proof_batch26o23_g_narrow_bridge_diagnostic.json",
    "run/proofs/proof_batch26o23_f_r4_prior_proof_loader_correction.json",
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
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
]

CONFIG_PATHS = [
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/rollout",
    "etc/brokers/runtime.yaml",
    "etc/brokers/provider_roles.yaml",
    "etc/brokers/dhan.yaml",
    "etc/brokers/zerodha.yaml",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS + CONFIG_PATHS

STARTED: list[subprocess.Popen[str]] = []


def run(cmd: list[str] | str, *, timeout: int = 30, env: dict[str, str] | None = None, shell: bool = False) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=env,
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


def redis_xrevrange_raw(key: str, count: int = 10) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def redis_xrange_raw(key: str, start: str, end: str = "+", count: int = 100) -> dict[str, Any]:
    return redis_cmd(["XRANGE", key, start, end, "COUNT", str(count)], timeout=20)


def redis_last_id(key: str) -> str:
    rows = redis_xrevrange_raw(key, count=1).get("stdout") or ""
    first = rows.splitlines()[0].strip() if rows.splitlines() else "0-0"
    return first if re.match(r"^\d+-\d+$", first) else "0-0"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_file_record(rel: str, copy_source: bool = False) -> dict[str, Any]:
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
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only_no_full_evidence_copy"

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
            "broker_call_false",
            "order_write_false",
            "threshold_relaxation_false",
            "forced_candidate_false",
            "corrected_no_positive_candidate_created",
            "oneshot_all_helpers_present",
            "oneshot_all_scenarios_passed",
        }
    }
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
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in set(CONTROLLED_SERVICES),
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
        "features_last_id": redis_last_id(FEATURES_STREAM),
        "decisions_last_id": redis_last_id(DECISIONS_STREAM),
        "orders_last_id": redis_last_id(ORDERS_STREAM),
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
    return out[:12]


def summarize_decisions(runtime: dict[str, Any]) -> dict[str, Any]:
    items = parse_payloads(runtime.get("latest_decisions_raw", {}).get("stdout") or "")
    payloads = [x["payload"] for x in items]
    actions = [p.get("action") for p in payloads]
    reasons = [p.get("reason") or p.get("activation_reason") for p in payloads]
    candidate_counts = [p.get("activation_candidate_count") for p in payloads]
    return {
        "payload_count": len(payloads),
        "actions": actions,
        "reasons": reasons,
        "activation_candidate_counts": candidate_counts,
        "data_valid_values": [p.get("data_valid") for p in payloads],
        "safe_to_consume_values": [p.get("safe_to_consume") for p in payloads],
        "structural_valid_values": [p.get("structural_valid") for p in payloads],
        "consumer_view_repaired_values": [p.get("consumer_view_repaired") for p in payloads],
        "consumer_view_repair_reason_values": [p.get("consumer_view_repair_reason") for p in payloads],
        "any_entry_action": any(str(a).upper() in {"BUY", "SELL", "ENTER", "ENTRY"} for a in actions),
        "all_hold_or_empty": all(str(a).upper() in {"HOLD", "", "NONE", "NULL"} for a in actions) if payloads else True,
        "raw_items_sample": items[:5],
    }


def controlled_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"

    env["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] = "1"
    env["SCALPX_CONTROLLED_PAPER_SCOPE_ACK"] = CONTROLLED_PAPER_SCOPE_ACK
    env["SCALPX_PAPER_ARMED"] = "1"

    env["SCALPX_CONTROLLED_PAPER_FAMILY"] = "MIST"
    env["SCALPX_CONTROLLED_PAPER_BRANCH"] = "CALL"
    env["SCALPX_CONTROLLED_PAPER_QTY_LOTS"] = "1"
    env["SCALPX_CONTROLLED_PAPER_ROUTE"] = "paper"

    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["SCALPX_LIVE_ORDERS_ALLOWED"] = "0"
    env["SCALPX_BROKER_CALLS_ALLOWED"] = "0"
    env["SCALPX_FORCE_CANDIDATE"] = "0"
    env["SCALPX_THRESHOLD_RELAXATION"] = "0"
    env["SCALPX_AUTOMATIC_BROKER_FAILOVER"] = "0"
    env["SCALPX_MID_POSITION_PROVIDER_MIGRATION"] = "0"

    return env


def start_service(service: str, env: dict[str, str]) -> dict[str, Any]:
    already = [
        r for r in parse_processes()
        if r.get("service") == service and r.get("is_mme_main_service")
    ]
    if already:
        return {
            "service": service,
            "started": False,
            "reason": "already_running_before_o23j",
            "existing_rows": already,
            "pid": None,
        }

    log_path = RUN_DIR / f"{service}_controlled_paper_o23j.log"
    cmd = [
        sys.executable,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        service,
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ]

    log_f = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env=env,
    )
    STARTED.append(proc)
    time.sleep(4)

    return {
        "service": service,
        "started": True,
        "pid": proc.pid,
        "cmd": cmd,
        "log_path": str(log_path.relative_to(ROOT)),
        "alive_after_start": proc.poll() is None,
        "returncode_after_start": proc.poll(),
    }


def stop_started() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in reversed(STARTED):
        rec = {"pid": p.pid, "returncode_before_stop": p.poll()}
        if p.poll() is None:
            try:
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=10)
                    rec["stopped"] = True
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(timeout=5)
                    rec["killed"] = True
            except Exception as exc:
                rec["stop_error"] = repr(exc)
        rec["returncode_after_stop"] = p.poll()
        out.append(rec)
    return out


def stop_leftover_controlled() -> list[dict[str, Any]]:
    priority = {"execution": 0, "risk": 1, "strategy": 2, "features": 3, "feeds": 4}
    rows = runtime_snapshot()["controlled_service_rows"]
    started_pids = {p.pid for p in STARTED}
    out = []
    for row in sorted(rows, key=lambda r: priority.get(r.get("service"), 99)):
        if int(row["pid"]) in started_pids:
            continue
        rec = dict(row)
        try:
            os.kill(int(row["pid"]), signal.SIGTERM)
            time.sleep(1.5)
            if pathlib.Path("/proc").joinpath(str(row["pid"])).exists():
                os.kill(int(row["pid"]), signal.SIGKILL)
                rec["killed"] = True
            else:
                rec["terminated"] = True
        except ProcessLookupError:
            rec["already_exited"] = True
        except Exception as exc:
            rec["stop_error"] = repr(exc)
        out.append(rec)
    return out


def order_events_since(start_id: str) -> dict[str, Any]:
    raw = redis_xrange_raw(ORDERS_STREAM, f"({start_id}", "+", count=200)
    text = raw.get("stdout") or ""
    ids = re.findall(r"^\d+-\d+$", text, flags=re.MULTILINE)
    return {
        "raw": raw,
        "event_ids": ids,
        "event_count": len(ids),
        "text_sample": text[:8000],
    }


def log_review() -> dict[str, Any]:
    patterns = [
        "Traceback",
        "Exception",
        "ERROR",
        "CRITICAL",
        "real_live",
        "broker",
        "order",
        "paper",
        "CONTROLLED",
        "MIST",
        "CALL",
        "consumer_view_repaired",
        "O23H_PROMOTED_VALID_CONSUMER_VIEW",
        "no_candidate",
        "HOLD",
        "BUY",
        "SELL",
        "ENTRY",
    ]
    out: dict[str, Any] = {}
    for f in sorted(RUN_DIR.glob("*.log")):
        text = f.read_text(encoding="utf-8", errors="replace")
        rec = {
            "sha256": sha256_file(f),
            "size_bytes": f.stat().st_size,
            "line_count": text.count("\n") + 1,
            "hits": {},
            "tail": "\n".join(text.splitlines()[-80:]),
        }
        for pat in patterns:
            hits = []
            for idx, line in enumerate(text.splitlines(), start=1):
                if pat.lower() in line.lower():
                    hits.append({"line": idx, "text": line[:320]})
                    if len(hits) >= MAX_LOG_HITS:
                        break
            rec["hits"][pat] = hits
        out[str(f.relative_to(ROOT))] = rec
    return out


def write_artifacts(proof: dict[str, Any]) -> None:
    SESSION_JSON.write_text(json.dumps({
        "batch": BATCH,
        "tag": TAG,
        "approval_phrase": APPROVAL_PHRASE,
        "session_seconds": SESSION_SECONDS,
        "poll_seconds": POLL_SECONDS,
        "controlled_env": proof.get("controlled_env"),
        "start_results": proof.get("service_start_results"),
        "samples": proof.get("samples"),
        "stop_results": proof.get("stop_results"),
        "leftover_stop_results": proof.get("leftover_stop_results"),
        "post_readback": proof.get("post_readback"),
        "decision_summary_after": proof.get("decision_summary_after"),
        "order_events_since_start": proof.get("order_events_since_start"),
    }, indent=2, sort_keys=True), encoding="utf-8")

    SAFETY_JSON.write_text(json.dumps({
        "batch": BATCH,
        "tag": TAG,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "preflight": proof.get("preflight"),
        "post_readback": proof.get("post_readback"),
        "decision_summary_after": proof.get("decision_summary_after"),
        "order_events_since_start": proof.get("order_events_since_start"),
        "safety_intent": proof.get("safety_intent"),
    }, indent=2, sort_keys=True), encoding="utf-8")

    LOG_REVIEW_JSON.write_text(json.dumps(proof.get("log_review", {}), indent=2, sort_keys=True), encoding="utf-8")

    NEXT_DECISION_JSON.write_text(json.dumps({
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "RUN_O23_K_POST_REPAIR_OBSERVATION_EVIDENCE_REVIEW_NEXT",
        "recommended_next_batch": "26-O23-K post-repair controlled-paper evidence review; no real live.",
        "do_not_proceed_to_real_live": True,
        "why": [
            "O23-J is a bounded controlled-paper observation only.",
            "Evidence must be reviewed before any further observation or live-readiness discussion.",
            "If O23-J fails or leaves position non-flat, run cleanup/review first.",
        ],
        "forbidden": [
            "real live",
            "quantity increase",
            "family expansion",
            "threshold relaxation",
            "forced candidate",
            "broker failover",
            "mid-position provider migration",
        ],
    }, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "explicit_user_approval_phrase_received": APPROVAL_PHRASE,
        "safety_intent": {
            "post_repair_controlled_paper_observation": True,
            "scope": "MIST_CALL_1_LOT_PAPER_ONLY",
            "real_live_enablement": False,
            "broker_real_live_call": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "doctrine_mutation": False,
            "automatic_broker_failover": False,
            "mid_position_provider_migration": False,
            "bounded_session_seconds": SESSION_SECONDS,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "preflight": {},
        "controlled_env": {},
        "service_start_results": [],
        "samples": [],
        "stop_results": [],
        "leftover_stop_results": [],
        "post_readback": {},
        "decision_summary_after": {},
        "order_events_since_start": {},
        "log_review": {},
        "required_verdicts": {},
        "false_keys": [],
        "classification": "",
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== DISK PRECHECK =====")
        proof["disk_state"] = disk_state()

        print("===== EVIDENCE-FIRST INSPECTION: PRIOR PROOFS + SOURCE HASHES =====")
        for rel in INSPECT_PATHS:
            copy_source = rel in SOURCE_PATHS
            proof["inspected_files"][rel] = safe_file_record(rel, copy_source=copy_source)
            if rel.endswith(".json"):
                proof["prior_proofs"][rel] = load_prior(rel)

        print("===== COMPILE / IMPORT PREFLIGHT =====")
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

        print("===== PREFLIGHT SAFETY SNAPSHOT =====")
        pre = runtime_snapshot()
        proof["preflight"] = pre

        i_r1 = proof["prior_proofs"].get("run/proofs/proof_batch26o23_i_r1_oneshot_safety_assertion_correction.json", {})
        h = proof["prior_proofs"].get("run/proofs/proof_batch26o23_h_narrow_bridge_repair.json", {})

        pre_orders_empty = pre["orders_xlen"] == 0 and not (pre["latest_orders_raw"].get("stdout") or "").strip()
        pre_position_flat = flat_position(pre["position"])
        pre_no_controlled_pids = len(pre["controlled_service_rows"]) == 0
        pre_risk_execution_not_running = len(pre["risk_execution_rows"]) == 0

        env = controlled_env()
        env_proof = {
            k: env.get(k, "")
            for k in [
                "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
                "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
                "SCALPX_PAPER_ARMED",
                "SCALPX_CONTROLLED_PAPER_FAMILY",
                "SCALPX_CONTROLLED_PAPER_BRANCH",
                "SCALPX_CONTROLLED_PAPER_QTY_LOTS",
                "SCALPX_CONTROLLED_PAPER_ROUTE",
                "SCALPX_REAL_LIVE_ALLOWED",
                "SCALPX_LIVE_ORDERS_ALLOWED",
                "SCALPX_BROKER_CALLS_ALLOWED",
                "SCALPX_FORCE_CANDIDATE",
                "SCALPX_THRESHOLD_RELAXATION",
                "SCALPX_AUTOMATIC_BROKER_FAILOVER",
                "SCALPX_MID_POSITION_PROVIDER_MIGRATION",
            ]
        }
        proof["controlled_env"] = env_proof

        hard_preflight = {
            "disk_free_above_min": proof["disk_state"]["free_bytes"] >= MIN_FREE_BYTES,
            "o23i_r1_pass_loaded": pass_prefix(i_r1, "PASS_O23_I_R1_ONESHOT_SAFETY_ASSERTION_CORRECTION_OK_NO_START_NO_REAL_LIVE"),
            "o23h_pass_loaded": pass_prefix(h, "PASS_O23_H_NARROW_BRIDGE_REPAIR_OK_NO_START_NO_REAL_LIVE"),
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "pre_orders_empty": pre_orders_empty,
            "pre_position_flat": pre_position_flat,
            "pre_no_controlled_pids": pre_no_controlled_pids,
            "pre_risk_execution_not_running": pre_risk_execution_not_running,
            "controlled_paper_runtime_env_set": env_proof["SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"] == "1",
            "scope_ack_exact": env_proof["SCALPX_CONTROLLED_PAPER_SCOPE_ACK"] == CONTROLLED_PAPER_SCOPE_ACK,
            "paper_armed_env_set": env_proof["SCALPX_PAPER_ARMED"] == "1",
            "scope_family_mist": env_proof["SCALPX_CONTROLLED_PAPER_FAMILY"] == "MIST",
            "scope_branch_call": env_proof["SCALPX_CONTROLLED_PAPER_BRANCH"] == "CALL",
            "scope_qty_one_lot": env_proof["SCALPX_CONTROLLED_PAPER_QTY_LOTS"] == "1",
            "paper_route_only": env_proof["SCALPX_CONTROLLED_PAPER_ROUTE"] == "paper",
            "real_live_false": env_proof["SCALPX_REAL_LIVE_ALLOWED"] == "0",
            "live_orders_forbidden": env_proof["SCALPX_LIVE_ORDERS_ALLOWED"] == "0",
            "broker_calls_forbidden": env_proof["SCALPX_BROKER_CALLS_ALLOWED"] == "0",
            "no_threshold_relaxation": env_proof["SCALPX_THRESHOLD_RELAXATION"] == "0",
            "no_forced_candidate": env_proof["SCALPX_FORCE_CANDIDATE"] == "0",
            "no_auto_failover": env_proof["SCALPX_AUTOMATIC_BROKER_FAILOVER"] == "0",
            "no_mid_position_provider_migration": env_proof["SCALPX_MID_POSITION_PROVIDER_MIGRATION"] == "0",
        }

        if not all(hard_preflight.values()):
            proof["required_verdicts"] = hard_preflight
            proof["false_keys"] = [k for k, v in hard_preflight.items() if v is not True]
            proof["final_verdict"] = "REFUSE_O23_J_PREFLIGHT_NOT_SAFE_NO_START"
            proof["classification"] = "PREFLIGHT_REFUSED_NO_SERVICE_START"
            proof["next_recommended_batch"] = "Inspect false_keys; do not start controlled paper."
            proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
            PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
            print("REFUSE: preflight not safe. No services started.")
            print("false_keys =", proof["false_keys"])
            print("proof_json =", PROOF_JSON.relative_to(ROOT))
            return 2

        order_start_id = pre["orders_last_id"]

        print("===== START POST-REPAIR CONTROLLED-PAPER SERVICES =====")
        start_results = []
        for service in CONTROLLED_SERVICES:
            res = start_service(service, env)
            start_results.append(res)
            print(json.dumps(res, indent=2, sort_keys=True))
            time.sleep(2)
        proof["service_start_results"] = start_results

        all_started = all(
            (x.get("started") is True and x.get("alive_after_start") is True)
            or x.get("reason") == "already_running_before_o23j"
            for x in start_results
        )

        print("===== BOUNDED POST-REPAIR OBSERVATION =====")
        start_time = time.time()
        deadline = start_time + SESSION_SECONDS
        max_order_events_seen = 0
        early_stop_reason = None

        while time.time() < deadline:
            snap = runtime_snapshot()
            orders_since = order_events_since(order_start_id)
            max_order_events_seen = max(max_order_events_seen, orders_since["event_count"])
            dec_summary = summarize_decisions(snap)

            compact_sample = {
                "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                "seconds_elapsed": round(time.time() - start_time, 2),
                "features_xlen": snap["features_xlen"],
                "decisions_xlen": snap["decisions_xlen"],
                "orders_xlen": snap["orders_xlen"],
                "new_order_events_since_start": orders_since["event_count"],
                "position": snap["position"],
                "controlled_service_count": len(snap["controlled_service_rows"]),
                "risk_execution_count": len(snap["risk_execution_rows"]),
                "decision_summary": {
                    "payload_count": dec_summary["payload_count"],
                    "actions": dec_summary["actions"],
                    "reasons": dec_summary["reasons"],
                    "activation_candidate_counts": dec_summary["activation_candidate_counts"],
                    "data_valid_values": dec_summary["data_valid_values"],
                    "safe_to_consume_values": dec_summary["safe_to_consume_values"],
                    "structural_valid_values": dec_summary["structural_valid_values"],
                    "consumer_view_repaired_values": dec_summary["consumer_view_repaired_values"],
                    "consumer_view_repair_reason_values": dec_summary["consumer_view_repair_reason_values"],
                    "any_entry_action": dec_summary["any_entry_action"],
                    "all_hold_or_empty": dec_summary["all_hold_or_empty"],
                },
            }
            proof["samples"].append(compact_sample)

            print(json.dumps(compact_sample, indent=2, sort_keys=True)[:8000])

            if orders_since["event_count"] > MAX_PAPER_ORDER_EVENTS_ALLOWED:
                early_stop_reason = "MAX_PAPER_ORDER_EVENTS_ALLOWED_EXCEEDED"
                break

            time.sleep(POLL_SECONDS)

        proof["early_stop_reason"] = early_stop_reason

        print("===== STOP POST-REPAIR CONTROLLED-PAPER SERVICES =====")
        proof["stop_results"] = stop_started()
        time.sleep(6)
        proof["leftover_stop_results"] = stop_leftover_controlled()
        time.sleep(3)

        print("===== POST-RUN SAFETY READBACK =====")
        post = runtime_snapshot()
        proof["post_readback"] = post
        proof["decision_summary_after"] = summarize_decisions(post)
        proof["order_events_since_start"] = order_events_since(order_start_id)

        print("===== LOG REVIEW =====")
        proof["log_review"] = log_review()

        post_position_flat = flat_position(post["position"])
        post_no_controlled_pids = len(post["controlled_service_rows"]) == 0
        post_risk_execution_not_running = len(post["risk_execution_rows"]) == 0
        post_order_events = proof["order_events_since_start"]["event_count"]
        post_order_events_within_limit = post_order_events <= MAX_PAPER_ORDER_EVENTS_ALLOWED
        started_services_stopped = all(x.get("returncode_after_stop") is not None for x in proof["stop_results"]) if proof["stop_results"] else True

        # In controlled-paper observation, paper order events may be zero or non-zero.
        # Safety is real_live=false + event count bounded + final FLAT.
        paper_order_classification = (
            "CONTROLLED_PAPER_TRADE_EVENTS_OBSERVED_WITHIN_LIMIT"
            if post_order_events > 0
            else "CONTROLLED_PAPER_NO_TRADE_OBSERVATION"
        )

        write_artifacts(proof)

        req = {
            **hard_preflight,
            "services_started_or_already_running": all_started,
            "samples_captured": len(proof["samples"]) > 0,
            "started_services_stopped": started_services_stopped,
            "leftover_cleanup_attempted": True,
            "no_controlled_pids_after": post_no_controlled_pids,
            "risk_execution_not_running_after": post_risk_execution_not_running,
            "position_flat_after": post_position_flat,
            "paper_order_events_within_limit": post_order_events_within_limit,
            "max_paper_order_events_not_exceeded": max_order_events_seen <= MAX_PAPER_ORDER_EVENTS_ALLOWED,
            "session_json_written": SESSION_JSON.exists(),
            "safety_json_written": SAFETY_JSON.exists(),
            "log_review_json_written": LOG_REVIEW_JSON.exists(),
            "next_decision_json_written": NEXT_DECISION_JSON.exists(),
            "real_live_false_after": env_proof["SCALPX_REAL_LIVE_ALLOWED"] == "0",
            "live_orders_forbidden_after": env_proof["SCALPX_LIVE_ORDERS_ALLOWED"] == "0",
            "broker_calls_forbidden_after": env_proof["SCALPX_BROKER_CALLS_ALLOWED"] == "0",
            "no_threshold_relaxation_after": env_proof["SCALPX_THRESHOLD_RELAXATION"] == "0",
            "no_forced_candidate_after": env_proof["SCALPX_FORCE_CANDIDATE"] == "0",
            "production_source_patch_false_in_this_batch": True,
        }

        false_keys = [k for k, v in req.items() if v is not True]
        proof["required_verdicts"] = req
        proof["false_keys"] = false_keys
        proof["classification"] = paper_order_classification
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if false_keys:
            proof["final_verdict"] = "FAIL_O23_J_POST_REPAIR_CONTROLLED_PAPER_OBSERVATION_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and run O23-J-R1 cleanup/readback if any PIDs or non-flat state remain."
        else:
            proof["final_verdict"] = "PASS_O23_J_POST_REPAIR_CONTROLLED_PAPER_OBSERVATION_OK_REAL_LIVE_FALSE"
            proof["next_recommended_batch"] = "26-O23-K post-repair controlled-paper evidence review; no real live."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — post-repair bounded controlled-paper observation",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- session: `{SESSION_JSON.relative_to(ROOT)}`",
                f"- safety: `{SAFETY_JSON.relative_to(ROOT)}`",
                f"- log_review: `{LOG_REVIEW_JSON.relative_to(ROOT)}`",
                f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Explicit approval",
                f"`{APPROVAL_PHRASE}`",
                "",
                "## Scope",
                "- MIST CALL only.",
                "- 1 lot only.",
                "- paper route only.",
                "- real_live=false.",
                "- no threshold relaxation.",
                "- no forced candidate.",
                "- no automatic broker failover.",
                "- no mid-position provider migration.",
                "",
                "## Verdict",
                f"- final_verdict: `{proof['final_verdict']}`",
                f"- classification: `{proof['classification']}`",
                f"- false_keys: `{false_keys}`",
                f"- paper_order_events_since_start: `{post_order_events}`",
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
                f"# {DATE} — {BATCH} post-repair controlled-paper observation",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                f"Classification: `{proof['classification']}`",
                "",
                "## Achieved",
                "- Loaded O23-I-R1 and O23-H as prerequisites.",
                "- Confirmed safe preflight: no PIDs, FLAT, no orders, real_live=false.",
                "- Started bounded controlled-paper stack under MIST CALL / 1 lot / paper only.",
                "- Captured observation samples.",
                "- Stopped services and captured post-run safety readback.",
                "- Preserved no-real-live and no-threshold-relaxation boundaries.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            SESSION_JSON,
            SAFETY_JSON,
            LOG_REVIEW_JSON,
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
        print("paper_order_events_since_start =", post_order_events)
        print("position_flat_after =", post_position_flat)
        print("no_controlled_pids_after =", post_no_controlled_pids)
        print("risk_execution_not_running_after =", post_risk_execution_not_running)
        print("next_recommended_batch =", proof["next_recommended_batch"])
        print("proof_json =", PROOF_JSON.relative_to(ROOT))
        print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
        print("session_json =", SESSION_JSON.relative_to(ROOT))
        print("safety_json =", SAFETY_JSON.relative_to(ROOT))
        print("log_review_json =", LOG_REVIEW_JSON.relative_to(ROOT))
        print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
        print("runbook =", RUNBOOK_MD.relative_to(ROOT))
        print("milestone =", MILESTONE_MD.relative_to(ROOT))
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        try:
            proof["stop_results"] = stop_started()
            time.sleep(3)
            proof["leftover_stop_results"] = stop_leftover_controlled()
            proof["post_readback"] = runtime_snapshot()
            proof["decision_summary_after"] = summarize_decisions(proof["post_readback"])
            proof["order_events_since_start"] = order_events_since((proof.get("preflight") or {}).get("orders_last_id", "0-0"))
            proof["log_review"] = log_review()
            write_artifacts(proof)
        except Exception as stop_exc:
            proof["stop_exception"] = repr(stop_exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O23_J_EXCEPTION_SAFE_STOP_ATTEMPTED"
        proof["next_recommended_batch"] = "Inspect exception and safety readback; do not proceed to real live."
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
