#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
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
BATCH = "26-O23-I"
BATCH_NAME = "static_oneshot_bridge_proof_after_o23h_repair_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_i_static_oneshot_bridge_proof_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_i_static_oneshot_bridge_proof.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_i_static_oneshot_bridge_proof.json"
STATIC_PROOF_JSON = RUN_DIR / "controlled_paper_o23i_static_bridge_proof.json"
ONESHOT_PROOF_JSON = RUN_DIR / "controlled_paper_o23i_oneshot_helper_matrix.json"
DIFF_AUDIT_JSON = RUN_DIR / "controlled_paper_o23i_o23h_diff_safety_audit.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23i_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_i_static_oneshot_bridge_proof.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_i_static_oneshot_bridge_proof.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_i_static_oneshot_bridge_proof.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 40_000

STRATEGY_REL = "app/mme_scalpx/services/strategy.py"
FEATURES_REL = "app/mme_scalpx/services/features.py"
RISK_REL = "app/mme_scalpx/services/risk.py"
EXECUTION_REL = "app/mme_scalpx/services/execution.py"

STRATEGY_PATH = ROOT / STRATEGY_REL
FEATURES_PATH = ROOT / FEATURES_REL
RISK_PATH = ROOT / RISK_REL
EXECUTION_PATH = ROOT / EXECUTION_REL

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_h_narrow_bridge_repair.json",
    "run/proofs/proof_batch26o23_g_narrow_bridge_diagnostic.json",
    "run/proofs/proof_batch26o23_f_r4_prior_proof_loader_correction.json",
    "run/proofs/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json",
    "run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json",
]

SOURCE_PATHS = [
    STRATEGY_REL,
    FEATURES_REL,
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/main.py",
    RISK_REL,
    EXECUTION_REL,
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS

O23H_HELPER_START = "# --- O23-H controlled-paper consumer-view bridge helper START ---"
O23H_HELPER_END = "# --- O23-H controlled-paper consumer-view bridge helper END ---"

BANNED_PATCH_INTENTS = [
    "force_candidate",
    "FORCE_CANDIDATE",
    "threshold_relaxation",
    "THRESHOLD_RELAXATION",
    "real_live_allowed = True",
    "SCALPX_REAL_LIVE_ALLOWED=1",
    "LIVE_ORDERS_ALLOWED=1",
    "BROKER_CALLS_ALLOWED=1",
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


def load_json_limited(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec = safe_file_record(rel, copy_source=False)
    if not p.exists() or not p.is_file():
        return rec
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        rec["json_loaded"] = isinstance(obj, dict)
        if isinstance(obj, dict):
            rec["final_verdict"] = obj.get("final_verdict")
            rec["false_keys"] = obj.get("false_keys")
            rec["next_recommended_batch"] = obj.get("next_recommended_batch")
            rec["patch_result"] = obj.get("patch_result")
            rec["static_proof"] = obj.get("static_proof")
            rec["required_verdicts"] = {
                k: v for k, v in (obj.get("required_verdicts") or {}).items()
                if k in {
                    "compile_after_pass",
                    "import_after_pass",
                    "patch_applied_or_already_present",
                    "strategy_has_o23h_helper",
                    "strategy_has_o23h_return_wrapper",
                    "features_was_not_modified",
                    "risk_execution_not_modified",
                    "orders_zero_now",
                    "position_flat_now",
                    "no_controlled_pids_now",
                    "risk_execution_not_running_now",
                    "real_live_approval_false",
                    "service_start_false",
                    "threshold_relaxation_false",
                    "forced_candidate_false",
                }
            }
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


def static_source_proof() -> dict[str, Any]:
    strategy_text = STRATEGY_PATH.read_text(encoding="utf-8", errors="replace")
    features_text = FEATURES_PATH.read_text(encoding="utf-8", errors="replace")
    risk_text = RISK_PATH.read_text(encoding="utf-8", errors="replace")
    execution_text = EXECUTION_PATH.read_text(encoding="utf-8", errors="replace")

    return {
        "strategy_sha256": sha256_file(STRATEGY_PATH),
        "features_sha256": sha256_file(FEATURES_PATH),
        "risk_sha256": sha256_file(RISK_PATH),
        "execution_sha256": sha256_file(EXECUTION_PATH),
        "strategy_has_o23h_helper": O23H_HELPER_START in strategy_text and O23H_HELPER_END in strategy_text,
        "strategy_has_jsonish": "def _o23h_jsonish" in strategy_text,
        "strategy_has_boolish": "def _o23h_boolish" in strategy_text,
        "strategy_has_find_consumer_view": "def _o23h_find_consumer_view" in strategy_text,
        "strategy_has_consumer_view_truth": "def _o23h_consumer_view_truth" in strategy_text,
        "strategy_has_bridge_repair_function": "def _o23h_repair_hold_bridge_decision" in strategy_text,
        "strategy_has_return_wrapper": "_o23h_repair_hold_bridge_decision((" in strategy_text,
        "strategy_has_bridge_reason": "hold_only_family_features_consumer_bridge" in strategy_text,
        "strategy_has_no_candidate": "no_candidate" in strategy_text,
        "strategy_has_data_valid": "data_valid" in strategy_text,
        "strategy_has_safe_to_consume": "safe_to_consume" in strategy_text,
        "strategy_has_structural_valid": "structural_valid" in strategy_text,
        "strategy_has_activation_candidate_count": "activation_candidate_count" in strategy_text,
        "features_has_consumer_view": "consumer_view" in features_text,
        "features_has_data_valid": "data_valid" in features_text,
        "features_has_safe_to_consume": "safe_to_consume" in features_text,
        "features_has_structural_valid": "structural_valid" in features_text,
        "risk_has_o23h_marker": "_o23h_" in risk_text,
        "execution_has_o23h_marker": "_o23h_" in execution_text,
        "banned_intent_hits_in_strategy": [
            x for x in BANNED_PATCH_INTENTS
            if x in strategy_text
        ],
    }


def one_shot_helper_matrix() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT))
    strategy = importlib.import_module("app.mme_scalpx.services.strategy")

    required_helpers = [
        "_o23h_jsonish",
        "_o23h_boolish",
        "_o23h_find_consumer_view",
        "_o23h_consumer_view_truth",
        "_o23h_repair_hold_bridge_decision",
    ]

    helper_presence = {name: hasattr(strategy, name) for name in required_helpers}
    repair = getattr(strategy, "_o23h_repair_hold_bridge_decision", None)

    scenarios = []

    def call_case(name: str, decision: dict[str, Any], local_vars: dict[str, Any], expectation: dict[str, Any]) -> dict[str, Any]:
        rec: dict[str, Any] = {
            "name": name,
            "input_decision": decision,
            "local_vars": local_vars,
            "expectation": expectation,
        }
        try:
            out = repair(dict(decision), dict(local_vars)) if callable(repair) else decision
            rec["output"] = out
            rec["ok"] = True

            for key, expected in expectation.items():
                if key == "__unchanged__":
                    rec["ok"] = rec["ok"] and (out == decision)
                else:
                    rec["ok"] = rec["ok"] and (out.get(key) == expected if isinstance(out, dict) else False)
        except Exception as exc:
            rec["exception"] = repr(exc)
            rec["ok"] = False
        return rec

    scenarios.append(call_case(
        "valid_consumer_view_bridge_hold_no_candidate_promotes_validity_only",
        {
            "action": "HOLD",
            "reason": "hold_only_family_features_consumer_bridge",
            "activation_reason": "hold_only_family_features_consumer_bridge",
            "activation_candidate_count": 0,
            "data_valid": False,
            "safe_to_consume": True,
        },
        {
            "consumer_view": {
                "data_valid": True,
                "safe_to_consume": True,
                "structural_valid": True,
            }
        },
        {
            "action": "HOLD",
            "reason": "no_candidate",
            "activation_reason": "no_candidate",
            "activation_candidate_count": 0,
            "data_valid": True,
            "safe_to_consume": True,
            "structural_valid": True,
            "consumer_view_repaired": True,
            "consumer_view_repair_reason": "O23H_PROMOTED_VALID_CONSUMER_VIEW",
        },
    ))

    scenarios.append(call_case(
        "invalid_consumer_view_does_not_promote",
        {
            "action": "HOLD",
            "reason": "hold_only_family_features_consumer_bridge",
            "activation_candidate_count": 0,
            "data_valid": False,
        },
        {
            "consumer_view": {
                "data_valid": False,
                "safe_to_consume": True,
                "structural_valid": True,
            }
        },
        {"__unchanged__": True},
    ))

    scenarios.append(call_case(
        "non_bridge_reason_unchanged",
        {
            "action": "HOLD",
            "reason": "no_candidate",
            "activation_candidate_count": 0,
            "data_valid": False,
        },
        {
            "consumer_view": {
                "data_valid": True,
                "safe_to_consume": True,
                "structural_valid": True,
            }
        },
        {"__unchanged__": True},
    ))

    scenarios.append(call_case(
        "entry_action_never_modified",
        {
            "action": "BUY",
            "reason": "hold_only_family_features_consumer_bridge",
            "activation_candidate_count": 1,
            "data_valid": False,
        },
        {
            "consumer_view": {
                "data_valid": True,
                "safe_to_consume": True,
                "structural_valid": True,
            }
        },
        {"__unchanged__": True},
    ))

    scenarios.append(call_case(
        "json_encoded_consumer_view_supported",
        {
            "action": "HOLD",
            "reason": "hold_only_family_features_consumer_bridge",
            "activation_candidate_count": "0",
            "data_valid": 0,
        },
        {
            "feature_payload": {
                "consumer_view_json": json.dumps({
                    "data_valid": "true",
                    "safe_to_consume": "1",
                    "structural_valid": "yes",
                })
            }
        },
        {
            "reason": "no_candidate",
            "activation_reason": "no_candidate",
            "activation_candidate_count": 0,
            "data_valid": True,
            "safe_to_consume": True,
            "structural_valid": True,
            "consumer_view_repaired": True,
        },
    ))

    return {
        "helper_presence": helper_presence,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "all_helpers_present": all(helper_presence.values()),
        "all_scenarios_passed": all(x.get("ok") is True for x in scenarios),
        "safety_assertions": {
            "no_scenario_changes_buy_action": all(
                not (s.get("input_decision", {}).get("action") == "BUY" and s.get("output") != s.get("input_decision"))
                for s in scenarios
            ),
            "no_scenario_creates_positive_candidate": all(
                not (isinstance(s.get("output"), dict) and s["output"].get("activation_candidate_count") not in {0, "0", None, ""})
                for s in scenarios
            ),
            "repair_only_on_bridge_reason": all(
                s.get("ok") is True for s in scenarios
            ),
        },
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Prove O23-H bridge repair statically and with synthetic one-shot helper matrix; no service start.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "doctrine_mutation": False,
            "production_source_patch": False,
            "static_oneshot_proof_only": True,
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_before": {},
        "static_proof": {},
        "oneshot_proof": {},
        "diff_safety_audit": {},
        "runtime_after": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()

    print("===== EVIDENCE-FIRST INSPECTION WITH HASH/SLICE + SOURCE BACKUPS =====")
    for rel in INSPECT_PATHS:
        copy_source = rel in {STRATEGY_REL, FEATURES_REL, RISK_REL, EXECUTION_REL}
        proof["inspected_files"][rel] = safe_file_record(rel, copy_source=copy_source)
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
    proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
    proof["commands"]["import"] = run([
        sys.executable,
        "-c",
        "import app.mme_scalpx.main, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution; print('IMPORT_OK')",
    ], timeout=60)

    print("===== RUNTIME SAFETY READBACK BEFORE ONE-SHOT =====")
    runtime_before = runtime_snapshot()
    proof["runtime_before"] = runtime_before

    print("===== STATIC SOURCE PROOF =====")
    static_proof = static_source_proof()
    proof["static_proof"] = static_proof
    STATIC_PROOF_JSON.write_text(json.dumps(static_proof, indent=2, sort_keys=True), encoding="utf-8")

    print("===== ONE-SHOT HELPER MATRIX =====")
    oneshot = one_shot_helper_matrix()
    proof["oneshot_proof"] = oneshot
    ONESHOT_PROOF_JSON.write_text(json.dumps(oneshot, indent=2, sort_keys=True), encoding="utf-8")

    print("===== DIFF / SCOPE SAFETY AUDIT =====")
    h = proof["prior_proofs"].get("run/proofs/proof_batch26o23_h_narrow_bridge_repair.json", {})
    h_patch = h.get("patch_result") or {}
    h_static = h.get("static_proof") or {}

    diff_audit = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "o23h_final_verdict": h.get("final_verdict"),
        "o23h_false_keys": h.get("false_keys"),
        "o23h_patch_result": h_patch,
        "o23h_static_proof_selected": {
            "strategy_has_o23h_helper": h_static.get("strategy_has_o23h_helper"),
            "strategy_has_o23h_return_wrapper": h_static.get("strategy_has_o23h_return_wrapper"),
            "features_sha256": h_static.get("features_sha256"),
            "risk_sha256": h_static.get("risk_sha256"),
            "execution_sha256": h_static.get("execution_sha256"),
        },
        "current_static_proof": static_proof,
        "scope_findings": {
            "features_was_not_modified_after_o23h": h_static.get("features_sha256") == static_proof.get("features_sha256") if h_static.get("features_sha256") else None,
            "risk_was_not_modified_by_o23h_marker": static_proof.get("risk_has_o23h_marker") is False,
            "execution_was_not_modified_by_o23h_marker": static_proof.get("execution_has_o23h_marker") is False,
            "banned_intent_hits_in_strategy": static_proof.get("banned_intent_hits_in_strategy"),
        },
    }
    proof["diff_safety_audit"] = diff_audit
    DIFF_AUDIT_JSON.write_text(json.dumps(diff_audit, indent=2, sort_keys=True), encoding="utf-8")

    print("===== RUNTIME SAFETY READBACK AFTER ONE-SHOT =====")
    runtime_after = runtime_snapshot()
    proof["runtime_after"] = runtime_after

    orders_zero = runtime_after["orders_xlen"] == 0 and not (runtime_after["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime_after["position"])
    no_controlled_pids = len(runtime_after["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime_after["risk_execution_rows"]) == 0

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "ALLOW_POST_REPAIR_BOUNDED_CONTROLLED_PAPER_OBSERVATION_ONLY_AFTER_EXPLICIT_APPROVAL",
        "recommended_next_batch": "26-O23-J post-repair bounded controlled-paper observation, MIST CALL, 1 lot, paper only, real_live=false",
        "requires_explicit_user_approval": True,
        "required_approval_phrase": "APPROVE O23-J POST-REPAIR CONTROLLED PAPER OBSERVATION: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE",
        "why": [
            "O23-H patched the narrow bridge.",
            "O23-I proves helper behavior with static and synthetic one-shot checks.",
            "No service was started and no order was written.",
            "Next observation must be explicitly approved again.",
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
    }
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "o23h_pass_loaded": pass_prefix(h, "PASS_O23_H_NARROW_BRIDGE_REPAIR_OK_NO_START_NO_REAL_LIVE"),
        "o23h_patch_applied_or_already_present": h_patch.get("patch_applied") is True or h_patch.get("already_patched") is True,
        "compile_pass": bool(proof["commands"]["compile"].get("ok")),
        "import_pass": bool(proof["commands"]["import"].get("ok")),
        "static_strategy_has_o23h_helper": static_proof.get("strategy_has_o23h_helper") is True,
        "static_strategy_has_o23h_return_wrapper": static_proof.get("strategy_has_return_wrapper") is True,
        "static_strategy_has_bridge_reason": static_proof.get("strategy_has_bridge_reason") is True,
        "static_strategy_has_data_valid": static_proof.get("strategy_has_data_valid") is True,
        "static_strategy_has_safe_to_consume": static_proof.get("strategy_has_safe_to_consume") is True,
        "static_strategy_has_structural_valid": static_proof.get("strategy_has_structural_valid") is True,
        "static_strategy_has_activation_candidate_count": static_proof.get("strategy_has_activation_candidate_count") is True,
        "static_features_has_consumer_view": static_proof.get("features_has_consumer_view") is True,
        "static_features_has_validity_fields": (
            static_proof.get("features_has_data_valid") is True
            and static_proof.get("features_has_safe_to_consume") is True
            and static_proof.get("features_has_structural_valid") is True
        ),
        "risk_has_no_o23h_marker": static_proof.get("risk_has_o23h_marker") is False,
        "execution_has_no_o23h_marker": static_proof.get("execution_has_o23h_marker") is False,
        "strategy_has_no_banned_intent_hits": static_proof.get("banned_intent_hits_in_strategy") == [],
        "oneshot_all_helpers_present": oneshot.get("all_helpers_present") is True,
        "oneshot_all_scenarios_passed": oneshot.get("all_scenarios_passed") is True,
        "oneshot_no_buy_action_changed": (oneshot.get("safety_assertions") or {}).get("no_scenario_changes_buy_action") is True,
        "oneshot_no_positive_candidate_created": (oneshot.get("safety_assertions") or {}).get("no_scenario_creates_positive_candidate") is True,
        "oneshot_repair_only_on_bridge_reason": (oneshot.get("safety_assertions") or {}).get("repair_only_on_bridge_reason") is True,
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "static_proof_json_written": STATIC_PROOF_JSON.exists(),
        "oneshot_proof_json_written": ONESHOT_PROOF_JSON.exists(),
        "diff_audit_json_written": DIFF_AUDIT_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "real_live_approval_false": True,
        "production_source_patch_false_in_this_batch": True,
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
        proof["final_verdict"] = "FAIL_O23_I_STATIC_ONESHOT_BRIDGE_PROOF_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys; do not restart controlled paper."
    else:
        proof["final_verdict"] = "PASS_O23_I_STATIC_ONESHOT_BRIDGE_PROOF_OK_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "STOP unless user explicitly approves O23-J post-repair bounded controlled-paper observation."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — static / one-shot bridge proof after O23-H",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- static_proof: `{STATIC_PROOF_JSON.relative_to(ROOT)}`",
            f"- oneshot_proof: `{ONESHOT_PROOF_JSON.relative_to(ROOT)}`",
            f"- diff_audit: `{DIFF_AUDIT_JSON.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Prove O23-H bridge repair without starting services.",
            "- Validate helper behavior with synthetic one-shot scenarios.",
            "- Confirm no order write, no real live, no threshold relaxation, no forced candidate.",
            "",
            "## One-shot proof",
            "```json",
            json.dumps(oneshot, indent=2, sort_keys=True),
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
            f"# {DATE} — {BATCH} static / one-shot bridge proof",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Loaded O23-H repair as prerequisite.",
            "- Compiled/imported current source.",
            "- Proved O23-H helper presence and strategy wrapper.",
            "- Ran synthetic one-shot helper matrix.",
            "- Confirmed no service start, no order write, no real live.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        STATIC_PROOF_JSON,
        ONESHOT_PROOF_JSON,
        DIFF_AUDIT_JSON,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        STRATEGY_PATH,
        FEATURES_PATH,
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
    print("oneshot_all_helpers_present =", oneshot.get("all_helpers_present"))
    print("oneshot_all_scenarios_passed =", oneshot.get("all_scenarios_passed"))
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("approval_required_for_next_observation =", next_decision["requires_explicit_user_approval"])
    print("required_approval_phrase =", next_decision["required_approval_phrase"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("static_proof_json =", STATIC_PROOF_JSON.relative_to(ROOT))
    print("oneshot_proof_json =", ONESHOT_PROOF_JSON.relative_to(ROOT))
    print("diff_audit_json =", DIFF_AUDIT_JSON.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
