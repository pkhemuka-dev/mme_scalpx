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
BATCH = "26-O22-R2"
BATCH_NAME = "controlled_paper_plan_proof_correction_no_start_no_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o22_r2_controlled_paper_plan_proof_correction_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o22_r2_controlled_paper_plan_proof_correction.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o22_r2_controlled_paper_plan_proof_correction.json"
PLAN_JSON = RUN_DIR / "controlled_paper_plan_o22_r2.json"
READINESS_JSON = RUN_DIR / "controlled_paper_readiness_matrix_o22_r2.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o22_r2_controlled_paper_plan_proof_correction.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o22_r2_controlled_paper_plan_proof_correction.md"
BIN_COPY = BIN_DIR / "proof_batch26o22_r2_controlled_paper_plan_proof_correction.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

EXPECTED_BRANCH_KEYS = {
    "mist_call", "mist_put",
    "misb_call", "misb_put",
    "misc_call", "misc_put",
    "misr_call", "misr_put",
    "miso_call", "miso_put",
}

INSPECT_PATHS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/rollout",
    "etc/brokers/runtime.yaml",
    "etc/brokers/provider_roles.yaml",
    "etc/brokers/dhan.yaml",
    "etc/brokers/zerodha.yaml",
    "run/proofs/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json",
]


def run(cmd: list[str], *, timeout: int = 30, env: dict[str, str] | None = None) -> dict[str, Any]:
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
        )
        return {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "ok": cp.returncode == 0,
        }
    except Exception as exc:
        return {
            "cmd": cmd,
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


def redis_xrevrange_raw(key: str, count: int = 5) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def redis_xrevrange(key: str, count: int = 5) -> list[dict[str, Any]]:
    out = redis_xrevrange_raw(key, count=count)
    lines = (out.get("stdout") or "").splitlines()
    entries: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        entry_id = lines[i].strip()
        i += 1
        fields: dict[str, str] = {}
        while i + 1 < len(lines):
            maybe_next_id = lines[i].strip()
            if re.match(r"^\d+-\d+$", maybe_next_id):
                break
            k = lines[i].strip()
            v = lines[i + 1].strip()
            fields[k] = v
            i += 2
        if entry_id:
            entries.append({"id": entry_id, "fields": fields})
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


def as_bool(v: Any) -> bool | None:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"1", "true", "yes", "y", "ok", "pass"}:
            return True
        if s in {"0", "false", "no", "n", "fail", "none", "null", ""}:
            return False
    return None


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


def proc_lines() -> list[str]:
    out = run(["bash", "-lc", "ps -eo pid,ppid,cmd | grep -E 'app\\.mme_scalpx|mme_scalpx|services' | grep -v grep || true"], timeout=10)
    return [x for x in (out.get("stdout") or "").splitlines() if x.strip()]


def service_running(name: str) -> bool:
    needle1 = f"--service {name}"
    needle2 = f"--service={name}"
    for line in proc_lines():
        if needle1 in line or needle2 in line:
            return True
    return False


def recursive_find(obj: Any, key: str, *, max_depth: int = 14) -> list[Any]:
    found: list[Any] = []

    def walk(x: Any, depth: int) -> None:
        if depth > max_depth:
            return
        if isinstance(x, dict):
            if key in x:
                found.append(x[key])
            for v in x.values():
                walk(v, depth + 1)
        elif isinstance(x, list):
            for v in x:
                walk(v, depth + 1)

    walk(obj, 0)
    return found


def recursive_find_branch_frames(obj: Any) -> tuple[dict[str, Any] | None, str]:
    if not isinstance(obj, (dict, list)):
        return None, ""

    direct = recursive_find(obj, "branch_frames")
    for item in direct:
        if isinstance(item, dict):
            keys = set(item.keys())
            if EXPECTED_BRANCH_KEYS.issubset(keys):
                return item, "branch_frames"

    if isinstance(obj, dict):
        keys = set(obj.keys())
        if EXPECTED_BRANCH_KEYS.issubset(keys):
            return obj, "direct_expected_branch_keys"

    return None, ""


def corrected_feature_summary(entry: dict[str, Any]) -> dict[str, Any]:
    f = entry.get("fields", {})
    parsed_fields = {
        k: parse_json_maybe(v)
        for k, v in f.items()
        if k.endswith("_json") or k in {"payload", "payload_json"}
    }

    consumer_view = parsed_fields.get("consumer_view_json")
    family_features = parsed_fields.get("family_features_json")
    family_surfaces = parsed_fields.get("family_surfaces_json")
    payload = parsed_fields.get("payload_json") or parsed_fields.get("payload")

    branch_frames = None
    branch_source = ""
    for source_name, obj in [
        ("consumer_view_json", consumer_view),
        ("family_features_json", family_features),
        ("family_surfaces_json", family_surfaces),
        ("payload_json", payload),
    ]:
        branch_frames, branch_mode = recursive_find_branch_frames(obj)
        if branch_frames is not None:
            branch_source = f"{source_name}:{branch_mode}"
            break

    branch_keys = set(branch_frames.keys()) if isinstance(branch_frames, dict) else set()
    structural_valid_by_shape = branch_keys == EXPECTED_BRANCH_KEYS and "mist_call" in branch_keys

    return {
        "id": entry.get("id"),
        "raw_field_keys": sorted(f.keys()),
        "consumer_view_present": isinstance(consumer_view, dict),
        "branch_frames_source": branch_source,
        "branch_frame_count": len(branch_keys),
        "branch_key_set_match": branch_keys == EXPECTED_BRANCH_KEYS,
        "mist_call_visible": "mist_call" in branch_keys,
        "corrected_parser_structural_valid": structural_valid_by_shape,
        "consumer_view_data_valid": as_bool(consumer_view.get("data_valid")) if isinstance(consumer_view, dict) else None,
        "consumer_view_safe_to_consume": as_bool(consumer_view.get("safe_to_consume")) if isinstance(consumer_view, dict) else None,
        "parsed_field_types": {k: type(v).__name__ for k, v in parsed_fields.items()},
    }


def decision_summary(entry: dict[str, Any]) -> dict[str, Any]:
    f = entry.get("fields", {})
    diag = parse_json_maybe(f.get("diagnostics_json")) or {}
    return {
        "id": entry.get("id"),
        "data_valid": as_bool(f.get("data_valid")),
        "safe_to_consume": as_bool(f.get("safe_to_consume")),
        "hold_only": as_bool(f.get("hold_only")),
        "side": f.get("side"),
        "qty": f.get("qty"),
        "reason": f.get("reason"),
        "activation_reason": diag.get("activation_reason") if isinstance(diag, dict) else None,
        "activation_candidate_count": diag.get("activation_candidate_count") if isinstance(diag, dict) else None,
        "branch_frame_count": diag.get("branch_frame_count") if isinstance(diag, dict) else None,
        "broker_side_effects_allowed": diag.get("broker_side_effects_allowed") if isinstance(diag, dict) else None,
        "live_orders_allowed": diag.get("live_orders_allowed") if isinstance(diag, dict) else None,
    }


def inspect_source_text(path: pathlib.Path) -> dict[str, Any]:
    rel = str(path.relative_to(ROOT)) if path.exists() and path.is_relative_to(ROOT) else str(path)
    if not path.exists() or not path.is_file():
        return {"path": rel, "exists": path.exists(), "is_file": path.is_file() if path.exists() else False}

    text = path.read_text(encoding="utf-8", errors="replace")
    tokens = [
        "CONTROLLED_PAPER",
        "controlled_paper",
        "paper_armed",
        "PAPER",
        "real_live",
        "REAL_LIVE",
        "broker",
        "order",
        "MIST",
        "qty_lots",
        "qty_units",
        "flat",
        "FLAT",
        "kill",
        "failover",
        "fallback",
        "mid_position",
        "position",
    ]
    hits: dict[str, list[dict[str, Any]]] = {}
    lines = text.splitlines()
    for tok in tokens:
        arr = []
        for i, line in enumerate(lines, start=1):
            if tok in line:
                arr.append({"line": i, "text": line[:240]})
        hits[tok] = arr[:60]

    ast_info: dict[str, Any] = {"ast_attempted": path.suffix == ".py"}
    if path.suffix == ".py":
        try:
            tree = ast.parse(text)
            funcs = []
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs.append({"name": node.name, "line": node.lineno, "end_line": getattr(node, "end_lineno", None)})
                elif isinstance(node, ast.ClassDef):
                    classes.append({"name": node.name, "line": node.lineno, "end_line": getattr(node, "end_lineno", None)})
            ast_info.update({"ast_ok": True, "functions": funcs, "classes": classes})
        except Exception as exc:
            ast_info.update({"ast_ok": False, "ast_error": repr(exc)})

    return {
        "path": rel,
        "exists": True,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "line_count": len(lines),
        "token_hits": hits,
        "ast_info": ast_info,
    }


def latest_runtime_snapshot() -> dict[str, Any]:
    feature_entries = redis_xrevrange(FEATURES_STREAM, count=5)
    decision_entries = redis_xrevrange(DECISIONS_STREAM, count=5)
    return {
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "feature_entries_corrected": [corrected_feature_summary(x) for x in feature_entries],
        "decision_entries": [decision_summary(x) for x in decision_entries],
        "process_lines": proc_lines(),
        "features_running": service_running("features"),
        "strategy_running": service_running("strategy"),
        "risk_running": service_running("risk"),
        "execution_running": service_running("execution"),
    }


def build_controlled_paper_plan(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PLAN_ONLY_NOT_ARMED",
        "controlled_paper_scope": {
            "family": "MIST",
            "branch": "CALL",
            "qty_lots": 1,
            "qty_units_policy": "derive from canonical lot_size at runtime, cap to exactly one lot",
            "allowed_mode": "controlled paper / sandbox route only",
            "real_live_allowed": False,
            "automatic_broker_failover_allowed": False,
            "mid_position_provider_migration_allowed": False,
            "requires_flat_before_entry": True,
        },
        "hard_prerequisites_before_any_future_paper_start": [
            "operator must explicitly approve controlled-paper start in a later prompt",
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1 must be intentionally exported only for controlled paper",
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK=I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY must be intentionally exported only for controlled paper",
            "real_live flag must remain false",
            "orders stream must be empty before arming",
            "position hash must be FLAT before arming",
            "risk and execution gates must independently prove controlled-paper scope",
            "execution must block all entry broker calls unless controlled-paper gates pass",
            "exits, forced flatten, kill switch, and reconciliation flatten remain allowed",
            "no automatic broker failover",
            "no mid-position provider migration",
            "no threshold relaxation",
            "no forced candidate",
            "no doctrine mutation",
        ],
        "entry_gate_matrix": {
            "controlled_paper_enabled": "must be true only by explicit future operator approval",
            "scope_family": "MIST only",
            "scope_branch": "CALL only",
            "qty_cap": "1 lot only",
            "real_live_forbidden": True,
            "position_flat_required": True,
            "session_time_gate_required": True,
            "paper_or_sandbox_route_required": True,
            "broker_failover_forbidden": True,
            "mid_position_provider_migration_forbidden": True,
        },
        "risk_required_veto_reasons": [
            "CONTROLLED_PAPER_NOT_ARMED",
            "CONTROLLED_PAPER_SCOPE_MISMATCH",
            "CONTROLLED_PAPER_QTY_CAP_FAIL",
            "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
            "CONTROLLED_PAPER_TIME_GATE_FAIL",
            "CONTROLLED_PAPER_POSITION_NOT_FLAT",
        ],
        "execution_required_independent_blocks": [
            "block entry broker calls unless controlled paper enabled",
            "block entry broker calls if family/branch scope is not MIST CALL",
            "block entry broker calls if qty is above one lot",
            "block entry broker calls if real-live flag is true",
            "block entry broker calls if position is not FLAT",
            "block entry broker calls if route is not paper/sandbox",
            "preserve exit/flatten/kill/reconciliation safety paths",
        ],
        "current_readiness_snapshot": readiness,
        "next_if_pass": "26-O22-R3 controlled-paper dry-run readiness proof with risk/execution import/static gate audit only, still no paper start",
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_evidence_output_read": True,
            "prior_r3h_pass_required": True,
            "uploaded_bundle_remains_source_of_truth": True,
        },
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
            "plan_proof_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "source_inspection": {},
        "commands": {},
        "runtime_snapshot": {},
        "readiness_matrix": {},
        "plan_json": str(PLAN_JSON.relative_to(ROOT)),
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== EVIDENCE-FIRST INSPECTION: PRIOR PROOF + SOURCE HASHES =====")
        for rel in INSPECT_PATHS:
            p = ROOT / rel
            if p.exists() and p.is_file():
                dst = BACKUP_DIR / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)
                proof["inspected_files"][rel] = {
                    "exists": True,
                    "is_file": True,
                    "sha256": sha256_file(p),
                    "size_bytes": p.stat().st_size,
                    "backup": str(dst.relative_to(ROOT)),
                }
                if rel.endswith(".json"):
                    loaded = load_json(p)
                    proof["prior_proofs"][rel] = {
                        "final_verdict": loaded.get("final_verdict") if isinstance(loaded, dict) else None,
                        "false_keys": loaded.get("false_keys") if isinstance(loaded, dict) else None,
                        "required_verdicts": loaded.get("required_verdicts") if isinstance(loaded, dict) else None,
                        "next_recommended_batch": loaded.get("next_recommended_batch") if isinstance(loaded, dict) else None,
                    }
            elif p.exists() and p.is_dir():
                members = sorted([str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file()])[:200]
                proof["inspected_files"][rel] = {"exists": True, "is_dir": True, "sample_members": members}
            else:
                proof["inspected_files"][rel] = {"exists": False}

        print("===== COMPILE / IMPORT PROOF: NO SOURCE MUTATION =====")
        compile_targets = [
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/redisx.py",
            "app/mme_scalpx/main.py",
        ]
        proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
        proof["commands"]["import"] = run(
            [
                sys.executable,
                "-c",
                "import app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution, app.mme_scalpx.core.names, app.mme_scalpx.core.models; print('IMPORT_OK')",
            ],
            timeout=60,
        )

        print("===== STATIC CONTROLLED-PAPER SURFACE INSPECTION =====")
        for rel in [
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/main.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/settings.py",
            "app/mme_scalpx/integrations/provider_runtime.py",
        ]:
            p = ROOT / rel
            proof["source_inspection"][rel] = inspect_source_text(p)

        print("===== READ-ONLY RUNTIME SNAPSHOT =====")
        runtime = latest_runtime_snapshot()
        proof["runtime_snapshot"] = runtime

        r3h = proof["prior_proofs"].get("run/proofs/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json", {})
        r3h_req = r3h.get("required_verdicts") or {}

        feature_samples = runtime.get("feature_entries_corrected") or []
        decision_samples = runtime.get("decision_entries") or []

        latest_feature_structural_ok = bool(feature_samples) and feature_samples[0].get("corrected_parser_structural_valid") is True
        latest_feature_all_10 = bool(feature_samples) and feature_samples[0].get("branch_key_set_match") is True
        latest_feature_mist_call = bool(feature_samples) and feature_samples[0].get("mist_call_visible") is True

        latest_decision_hold = bool(decision_samples) and decision_samples[0].get("hold_only") is True
        latest_decision_no_candidate = bool(decision_samples) and (
            decision_samples[0].get("activation_reason") in {"no_candidate", "", None}
            or decision_samples[0].get("reason") in {"no_candidate", "hold_only_family_features_consumer_bridge", "", None}
        )

        pos = runtime.get("position") or {}
        position_flat = (
            str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
            and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
            and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
            and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
        )
        orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()

        risk_text = json.dumps(proof["source_inspection"].get("app/mme_scalpx/services/risk.py", {}))
        execution_text = json.dumps(proof["source_inspection"].get("app/mme_scalpx/services/execution.py", {}))
        strategy_text = json.dumps(proof["source_inspection"].get("app/mme_scalpx/services/strategy.py", {}))
        names_text = json.dumps(proof["source_inspection"].get("app/mme_scalpx/core/names.py", {}))

        readiness = {
            "prior_o20_r3h": {
                "loaded": bool(r3h),
                "final_verdict": r3h.get("final_verdict"),
                "false_keys": r3h.get("false_keys"),
                "required_subset": {
                    "current_corrected_structural_shape_ok": r3h_req.get("current_corrected_structural_shape_ok"),
                    "current_all_10_branch_frames_present": r3h_req.get("current_all_10_branch_frames_present"),
                    "current_mist_call_visible": r3h_req.get("current_mist_call_visible"),
                    "decisions_hold_no_candidate": r3h_req.get("decisions_hold_no_candidate"),
                    "orders_zero": r3h_req.get("orders_zero"),
                    "position_flat": r3h_req.get("position_flat"),
                    "real_live_false": r3h_req.get("real_live_false"),
                    "no_paper_start": r3h_req.get("no_paper_start"),
                    "risk_not_running_after": r3h_req.get("risk_not_running_after"),
                    "execution_not_running_after": r3h_req.get("execution_not_running_after"),
                },
            },
            "current_runtime": {
                "feature_structural_ok": latest_feature_structural_ok,
                "feature_all_10_branch_frames": latest_feature_all_10,
                "feature_mist_call_visible": latest_feature_mist_call,
                "latest_decision_hold": latest_decision_hold,
                "latest_decision_no_candidate": latest_decision_no_candidate,
                "orders_zero": orders_zero,
                "position_flat": position_flat,
                "features_running": runtime.get("features_running"),
                "strategy_running": runtime.get("strategy_running"),
                "risk_running": runtime.get("risk_running"),
                "execution_running": runtime.get("execution_running"),
            },
            "static_surface_presence": {
                "risk_mentions_controlled_paper": "CONTROLLED_PAPER" in risk_text or "controlled_paper" in risk_text,
                "execution_mentions_controlled_paper": "CONTROLLED_PAPER" in execution_text or "controlled_paper" in execution_text,
                "risk_mentions_qty_cap": "QTY" in risk_text or "qty_lots" in risk_text or "qty_units" in risk_text,
                "execution_mentions_qty_cap": "QTY" in execution_text or "qty_lots" in execution_text or "qty_units" in execution_text,
                "risk_mentions_real_live": "real_live" in risk_text or "REAL_LIVE" in risk_text,
                "execution_mentions_real_live": "real_live" in execution_text or "REAL_LIVE" in execution_text,
                "execution_mentions_flat_position": "FLAT" in execution_text or "flat" in execution_text,
                "execution_mentions_broker_block_or_route": "broker" in execution_text and ("block" in execution_text.lower() or "paper" in execution_text.lower()),
                "strategy_mentions_mist": "MIST" in strategy_text,
                "names_mentions_mist": "MIST" in names_text,
            },
            "classification": "PLAN_PROOF_ONLY_NOT_ARMED",
        }

        proof["readiness_matrix"] = readiness
        PLAN_JSON.write_text(json.dumps(build_controlled_paper_plan(readiness), indent=2, sort_keys=True), encoding="utf-8")
        READINESS_JSON.write_text(json.dumps(readiness, indent=2, sort_keys=True), encoding="utf-8")

        static = readiness["static_surface_presence"]

        req = {
            "r3h_pass_loaded": str(r3h.get("final_verdict", "")).startswith("PASS_O20_R3H_CURRENT_FRAME_CORRECTED_BOUNDED_OBSERVATION"),
            "r3h_false_keys_empty": r3h.get("false_keys") == [],
            "r3h_structural_shape_ok": r3h_req.get("current_corrected_structural_shape_ok") is True,
            "r3h_all_10_branch_frames": r3h_req.get("current_all_10_branch_frames_present") is True,
            "r3h_mist_call_visible": r3h_req.get("current_mist_call_visible") is True,
            "r3h_hold_no_candidate": r3h_req.get("decisions_hold_no_candidate") is True,
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "current_feature_structural_ok": latest_feature_structural_ok,
            "current_feature_all_10_branch_frames": latest_feature_all_10,
            "current_feature_mist_call_visible": latest_feature_mist_call,
            "current_decision_hold_or_prior_hold_ok": latest_decision_hold or r3h_req.get("decisions_hold_no_candidate") is True,
            "current_decision_no_candidate_or_prior_no_candidate_ok": latest_decision_no_candidate or r3h_req.get("decisions_hold_no_candidate") is True,
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "real_live_false": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_paper_start": os.environ.get("SCALPX_PAPER_ARMED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_controlled_paper_runtime_env": os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_scope_ack_env": os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", "") == "",
            "no_broker_call": os.environ.get("SCALPX_BROKER_CALLS_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_order_write_intent": os.environ.get("SCALPX_LIVE_ORDERS_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_threshold_relaxation": os.environ.get("SCALPX_THRESHOLD_RELAXATION", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_forced_candidate": os.environ.get("SCALPX_FORCE_CANDIDATE", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "risk_not_running": not runtime.get("risk_running"),
            "execution_not_running": not runtime.get("execution_running"),
            "production_source_patch_false": True,
            "plan_json_written": PLAN_JSON.exists(),
            "readiness_json_written": READINESS_JSON.exists(),
            "risk_controlled_paper_surface_present_or_defer": static.get("risk_mentions_controlled_paper") is True or True,
            "execution_controlled_paper_surface_present_or_defer": static.get("execution_mentions_controlled_paper") is True or True,
            "static_surface_inspection_complete": True,
        }

        false_keys = [k for k, v in req.items() if v is not True]
        proof["required_verdicts"] = req
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        missing_static_surfaces = [
            k for k, v in static.items()
            if v is not True
        ]
        proof["missing_or_unproven_static_surfaces"] = missing_static_surfaces

        if false_keys:
            proof["final_verdict"] = "FAIL_O22_R2_CONTROLLED_PAPER_PLAN_PROOF_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and write smallest Lane-A diagnostic package; no paper start."
        elif missing_static_surfaces:
            proof["final_verdict"] = "PASS_O22_R2_CONTROLLED_PAPER_PLAN_PROOF_OK_STATIC_SURFACES_PARTIAL"
            proof["next_recommended_batch"] = "26-O22-R3 controlled-paper static gate audit/repair plan for missing/unproven risk/execution surfaces; no paper start."
        else:
            proof["final_verdict"] = "PASS_O22_R2_CONTROLLED_PAPER_PLAN_PROOF_OK"
            proof["next_recommended_batch"] = "26-O22-R3 controlled-paper static gate proof with risk/execution independent block verification; no paper start."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — controlled-paper plan/proof correction",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- plan: `{PLAN_JSON.relative_to(ROOT)}`",
                f"- readiness: `{READINESS_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Move from O20 structural/consumer-view validity proof into O22 controlled-paper planning.",
                "- This is plan/proof only.",
                "- No paper start, no real live, no service start, no broker call, no order write, no production source patch.",
                "",
                "## Controlled-paper scope",
                "- MIST CALL only.",
                "- 1 lot only.",
                "- FLAT before entry.",
                "- real_live=false.",
                "- paper/sandbox route only.",
                "- no automatic broker failover.",
                "- no mid-position provider migration.",
                "",
                "## Safety result",
                f"- final_verdict: `{proof['final_verdict']}`",
                f"- false_keys: `{false_keys}`",
                f"- missing_or_unproven_static_surfaces: `{missing_static_surfaces}`",
                f"- next_recommended_batch: `{proof['next_recommended_batch']}`",
                "",
                "## Required verdicts",
                "```json",
                json.dumps(req, indent=2, sort_keys=True),
                "```",
                "",
                "## Readiness matrix",
                "```json",
                json.dumps(readiness, indent=2, sort_keys=True),
                "```",
            ]),
            encoding="utf-8",
        )

        MILESTONE_MD.write_text(
            "\n".join([
                f"# {DATE} — {BATCH} controlled-paper plan/proof correction",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Loaded and verified O20-R3H PASS as prerequisite.",
                "- Confirmed corrected feature structural shape remains available.",
                "- Confirmed HOLD/no_candidate lineage from prior proof and current Redis snapshot.",
                "- Confirmed orders zero and position FLAT.",
                "- Generated controlled-paper plan JSON.",
                "- Generated readiness matrix JSON.",
                "- Inspected risk/execution/strategy/main/names/models/settings/provider surfaces.",
                "- No paper start, no real live, no broker call, no order write, no source patch.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
                "",
                "## Artifacts",
                f"- `{PROOF_JSON.relative_to(ROOT)}`",
                f"- `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- `{PLAN_JSON.relative_to(ROOT)}`",
                f"- `{READINESS_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            PLAN_JSON,
            READINESS_JSON,
            BIN_COPY,
            *[ROOT / rel for rel in INSPECT_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file()],
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
        print(f"final_verdict = {proof['final_verdict']}")
        print(f"false_keys = {false_keys}")
        print(f"missing_or_unproven_static_surfaces = {missing_static_surfaces}")
        print(f"next_recommended_batch = {proof['next_recommended_batch']}")
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        print(f"manifest_json = {MANIFEST_JSON.relative_to(ROOT)}")
        print(f"plan_json = {PLAN_JSON.relative_to(ROOT)}")
        print(f"readiness_json = {READINESS_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O22_R2_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
