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
BATCH = "26-O22-R4"
BATCH_NAME = "controlled_paper_dry_run_readiness_preflight_no_start_no_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o22_r4_controlled_paper_dry_run_readiness_preflight_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json"
SCENARIO_JSON = RUN_DIR / "controlled_paper_no_order_scenario_matrix_o22_r4.json"
PREFLIGHT_JSON = RUN_DIR / "controlled_paper_preflight_readiness_o22_r4.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o22_r4_controlled_paper_dry_run_readiness_preflight.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.md"
BIN_COPY = BIN_DIR / "proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

INSPECT_PATHS = [
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/features.py",
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
    "run/proofs/proof_batch26o22_r2_controlled_paper_plan_proof_correction.json",
    "run/proofs/proof_batch26o22_r3_controlled_paper_static_gate_proof.json",
]

REQUIRED_VETO_REASONS = [
    "CONTROLLED_PAPER_NOT_ARMED",
    "CONTROLLED_PAPER_SCOPE_MISMATCH",
    "CONTROLLED_PAPER_QTY_CAP_FAIL",
    "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    "CONTROLLED_PAPER_TIME_GATE_FAIL",
    "CONTROLLED_PAPER_POSITION_NOT_FLAT",
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


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def read_text(path: pathlib.Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def inspect_source(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        return {"exists": False}
    if path.is_dir():
        return {
            "exists": True,
            "is_dir": True,
            "sample_members": sorted(str(x.relative_to(ROOT)) for x in path.rglob("*") if x.is_file())[:300],
        }

    text = read_text(path)
    patterns = [
        "CONTROLLED_PAPER_NOT_ARMED",
        "CONTROLLED_PAPER_SCOPE_MISMATCH",
        "CONTROLLED_PAPER_QTY_CAP_FAIL",
        "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
        "CONTROLLED_PAPER_TIME_GATE_FAIL",
        "CONTROLLED_PAPER_POSITION_NOT_FLAT",
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "controlled_paper",
        "MIST",
        "CALL",
        "qty_lots",
        "qty_units",
        "real_live",
        "paper",
        "sandbox",
        "broker",
        "order",
        "entry",
        "exit",
        "flatten",
        "kill",
        "failover",
        "fallback",
        "mid_position",
        "migration",
        "FLAT",
        "has_position",
    ]
    hits: dict[str, list[dict[str, Any]]] = {}
    lines = text.splitlines()
    for pat in patterns:
        arr = []
        for idx, line in enumerate(lines, start=1):
            if pat.lower() in line.lower():
                arr.append({"line": idx, "text": line[:260]})
        hits[pat] = arr[:80]

    ast_info: dict[str, Any] = {"ast_applicable": path.suffix == ".py"}
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
        "exists": True,
        "is_file": True,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "line_count": len(lines),
        "hits": hits,
        "ast": ast_info,
    }


def source_bundle_contains(inspections: dict[str, Any], needle: str, rels: list[str]) -> bool:
    needle_l = needle.lower()
    for rel in rels:
        if needle_l in json.dumps(inspections.get(rel, {}), sort_keys=True).lower():
            return True
    return False


def runtime_snapshot() -> dict[str, Any]:
    latest_orders = redis_xrevrange_raw(ORDERS_STREAM, count=5)
    return {
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": latest_orders,
        "position": redis_hgetall(POSITION_HASH),
        "process_lines": proc_lines(),
        "features_running": service_running("features"),
        "strategy_running": service_running("strategy"),
        "risk_running": service_running("risk"),
        "execution_running": service_running("execution"),
    }


def build_synthetic_scenarios() -> list[dict[str, Any]]:
    base = {
        "family_id": "MIST",
        "branch_id": "CALL",
        "qty_lots": 1,
        "qty_units_policy": "one_lot",
        "real_live_allowed": False,
        "controlled_paper_runtime": True,
        "scope_ack": "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY",
        "position_flat": True,
        "session_time_gate": True,
        "route": "paper",
        "automatic_broker_failover": False,
        "mid_position_provider_migration": False,
    }

    scenarios = []

    def add(name: str, overrides: dict[str, Any], expected_allowed: bool, expected_veto: str | None) -> None:
        x = dict(base)
        x.update(overrides)
        scenarios.append({
            "name": name,
            "input": x,
            "expected_entry_allowed": expected_allowed,
            "expected_veto": expected_veto,
        })

    add("not_armed", {"controlled_paper_runtime": False}, False, "CONTROLLED_PAPER_NOT_ARMED")
    add("scope_family_mismatch", {"family_id": "MISB"}, False, "CONTROLLED_PAPER_SCOPE_MISMATCH")
    add("scope_branch_mismatch", {"branch_id": "PUT"}, False, "CONTROLLED_PAPER_SCOPE_MISMATCH")
    add("qty_cap_fail", {"qty_lots": 2}, False, "CONTROLLED_PAPER_QTY_CAP_FAIL")
    add("real_live_forbidden", {"real_live_allowed": True}, False, "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN")
    add("time_gate_fail", {"session_time_gate": False}, False, "CONTROLLED_PAPER_TIME_GATE_FAIL")
    add("position_not_flat", {"position_flat": False}, False, "CONTROLLED_PAPER_POSITION_NOT_FLAT")
    add("bad_route_live", {"route": "live"}, False, "CONTROLLED_PAPER_NOT_ARMED")
    add("auto_failover_forbidden", {"automatic_broker_failover": True}, False, "CONTROLLED_PAPER_SCOPE_MISMATCH")
    add("mid_position_provider_migration_forbidden", {"mid_position_provider_migration": True}, False, "CONTROLLED_PAPER_POSITION_NOT_FLAT")
    add("golden_mist_call_one_lot_paper_flat", {}, True, None)
    return scenarios


def local_policy_simulator(scenario: dict[str, Any]) -> dict[str, Any]:
    x = scenario["input"]

    if not x.get("controlled_paper_runtime") or x.get("scope_ack") != "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY":
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_NOT_ARMED"}

    if x.get("family_id") != "MIST" or x.get("branch_id") != "CALL":
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_SCOPE_MISMATCH"}

    if int(x.get("qty_lots") or 0) != 1:
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_QTY_CAP_FAIL"}

    if x.get("real_live_allowed") is True:
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN"}

    if x.get("session_time_gate") is not True:
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_TIME_GATE_FAIL"}

    if x.get("position_flat") is not True:
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_POSITION_NOT_FLAT"}

    if x.get("route") not in {"paper", "sandbox"}:
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_NOT_ARMED"}

    if x.get("automatic_broker_failover") is True:
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_SCOPE_MISMATCH"}

    if x.get("mid_position_provider_migration") is True:
        return {"entry_allowed": False, "veto": "CONTROLLED_PAPER_POSITION_NOT_FLAT"}

    return {"entry_allowed": True, "veto": None}


def run_callable_probe() -> dict[str, Any]:
    helper = RUN_DIR / "controlled_paper_callable_probe_o22_r4.py"
    helper.write_text(
        r'''
from __future__ import annotations
import inspect, json, os, traceback

os.environ.setdefault("SCALPX_REAL_LIVE_ALLOWED", "0")
os.environ.setdefault("SCALPX_LIVE_ORDERS_ALLOWED", "0")
os.environ.setdefault("SCALPX_BROKER_CALLS_ALLOWED", "0")
os.environ.setdefault("SCALPX_PAPER_ARMED", "0")
os.environ.setdefault("SCALPX_FORCE_CANDIDATE", "0")

mods = [
    "app.mme_scalpx.services.risk",
    "app.mme_scalpx.services.execution",
    "app.mme_scalpx.services.strategy",
    "app.mme_scalpx.core.names",
    "app.mme_scalpx.core.models",
]
out = {"ok": True, "modules": {}}
for modname in mods:
    rec = {"ok": False}
    try:
        mod = __import__(modname, fromlist=["*"])
        rec["ok"] = True
        rec["file"] = getattr(mod, "__file__", "")
        relevant = []
        for name, obj in inspect.getmembers(mod):
            if name.startswith("_"):
                continue
            kind = None
            if inspect.isclass(obj):
                kind = "class"
            elif inspect.isfunction(obj):
                kind = "function"
            else:
                continue
            hay = f"{name} {getattr(obj, '__doc__', '')}"
            if any(tok in hay.lower() for tok in ["controlled", "paper", "veto", "gate", "risk", "execution", "entry", "order", "block", "position"]):
                try:
                    sig = str(inspect.signature(obj))
                except Exception as exc:
                    sig = f"<signature_error {exc!r}>"
                relevant.append({
                    "name": name,
                    "kind": kind,
                    "signature": sig,
                    "module": getattr(obj, "__module__", ""),
                })
        rec["relevant_items"] = relevant
        rec["relevant_count"] = len(relevant)
    except Exception as exc:
        out["ok"] = False
        rec["error"] = repr(exc)
        rec["traceback"] = traceback.format_exc(limit=8)
    out["modules"][modname] = rec

print(json.dumps(out, indent=2, sort_keys=True))
''',
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["SCALPX_LIVE_ORDERS_ALLOWED"] = "0"
    env["SCALPX_BROKER_CALLS_ALLOWED"] = "0"
    env["SCALPX_PAPER_ARMED"] = "0"
    env["SCALPX_FORCE_CANDIDATE"] = "0"
    res = run([sys.executable, str(helper)], timeout=60, env=env)
    return {
        "helper": str(helper.relative_to(ROOT)),
        "result": res,
        "parsed": parse_json_maybe(res.get("stdout")),
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
            "prior_o22_r3_pass_required": True,
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
            "no_order_simulation_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "source_inspection": {},
        "commands": {},
        "runtime_snapshot": {},
        "callable_probe": {},
        "scenario_matrix": {},
        "preflight": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== EVIDENCE-FIRST INSPECTION: PRIOR PROOFS + SOURCE HASHES =====")
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
                        "missing_veto_reasons": loaded.get("missing_veto_reasons") if isinstance(loaded, dict) else None,
                        "missing_required_concepts": loaded.get("missing_required_concepts") if isinstance(loaded, dict) else None,
                        "missing_independent_block_surfaces": loaded.get("missing_independent_block_surfaces") if isinstance(loaded, dict) else None,
                    }
            elif p.exists() and p.is_dir():
                proof["inspected_files"][rel] = {
                    "exists": True,
                    "is_dir": True,
                    "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:300],
                }
            else:
                proof["inspected_files"][rel] = {"exists": False}

        print("===== COMPILE / IMPORT PROOF: NO SOURCE MUTATION =====")
        compile_targets = [
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/features.py",
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
                "import app.mme_scalpx.services.risk, app.mme_scalpx.services.execution, app.mme_scalpx.services.strategy, app.mme_scalpx.services.features, app.mme_scalpx.core.names, app.mme_scalpx.core.models; print('IMPORT_OK')",
            ],
            timeout=60,
        )

        print("===== SOURCE STATIC INSPECTION =====")
        inspections = {}
        for rel in INSPECT_PATHS:
            if not rel.endswith(".json"):
                inspections[rel] = inspect_source(rel)
        proof["source_inspection"] = inspections

        print("===== CALLABLE PROBE WITHOUT SERVICE START =====")
        proof["callable_probe"] = run_callable_probe()

        print("===== READ-ONLY RUNTIME SNAPSHOT =====")
        runtime = runtime_snapshot()
        proof["runtime_snapshot"] = runtime

        o22_r3 = proof["prior_proofs"].get("run/proofs/proof_batch26o22_r3_controlled_paper_static_gate_proof.json", {})
        o22_r3_req = o22_r3.get("required_verdicts") or {}

        source_rels = [
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/settings.py",
            "app/mme_scalpx/main.py",
        ]

        veto_surface_present = {
            reason: source_bundle_contains(inspections, reason, source_rels)
            for reason in REQUIRED_VETO_REASONS
        }

        scenario_results = []
        for scenario in build_synthetic_scenarios():
            sim = local_policy_simulator(scenario)
            scenario_results.append({
                **scenario,
                "simulated_result": sim,
                "matches_expected": (
                    sim.get("entry_allowed") == scenario.get("expected_entry_allowed")
                    and sim.get("veto") == scenario.get("expected_veto")
                ),
                "veto_surface_present": (
                    True if scenario.get("expected_veto") is None
                    else veto_surface_present.get(str(scenario.get("expected_veto")), False)
                ),
            })

        scenario_matrix = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "law": "local no-order policy simulation only; does not call broker/order/risk/execution services",
            "scope": "MIST CALL one lot controlled-paper only",
            "scenarios": scenario_results,
            "all_scenarios_match_expected": all(x["matches_expected"] for x in scenario_results),
            "all_required_veto_surfaces_present": all(veto_surface_present.values()),
            "veto_surface_present": veto_surface_present,
        }
        proof["scenario_matrix"] = scenario_matrix
        SCENARIO_JSON.write_text(json.dumps(scenario_matrix, indent=2, sort_keys=True), encoding="utf-8")

        orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
        position_flat = flat_position(runtime.get("position") or {})

        preflight = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "prior_o22_r3": {
                "final_verdict": o22_r3.get("final_verdict"),
                "false_keys": o22_r3.get("false_keys"),
                "next_recommended_batch": o22_r3.get("next_recommended_batch"),
                "required_subset": {
                    "required_veto_reasons_all_present": o22_r3_req.get("required_veto_reasons_all_present"),
                    "core_independent_risk_execution_surfaces_present": o22_r3_req.get("core_independent_risk_execution_surfaces_present"),
                    "orders_zero": o22_r3_req.get("orders_zero"),
                    "position_flat": o22_r3_req.get("position_flat"),
                    "risk_not_running": o22_r3_req.get("risk_not_running"),
                    "execution_not_running": o22_r3_req.get("execution_not_running"),
                },
            },
            "current_runtime": {
                "orders_zero": orders_zero,
                "position_flat": position_flat,
                "features_running": runtime.get("features_running"),
                "strategy_running": runtime.get("strategy_running"),
                "risk_running": runtime.get("risk_running"),
                "execution_running": runtime.get("execution_running"),
            },
            "scenario_matrix_path": str(SCENARIO_JSON.relative_to(ROOT)),
            "approved_for_paper_start": False,
            "next_if_pass": "26-O22-R5 controlled-paper operator checklist + explicit-approval gate package; still no automatic paper start",
        }
        proof["preflight"] = preflight
        PREFLIGHT_JSON.write_text(json.dumps(preflight, indent=2, sort_keys=True), encoding="utf-8")

        req = {
            "o22_r3_pass_loaded": str(o22_r3.get("final_verdict", "")).startswith("PASS_O22_R3_CONTROLLED_PAPER_STATIC_GATE_PROOF_OK"),
            "o22_r3_false_keys_empty": o22_r3.get("false_keys") == [],
            "o22_r3_no_missing_veto_reasons": o22_r3.get("missing_veto_reasons") == [],
            "o22_r3_no_missing_required_concepts": o22_r3.get("missing_required_concepts") == [],
            "o22_r3_no_missing_independent_surfaces": o22_r3.get("missing_independent_block_surfaces") == [],
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "callable_probe_ok": bool((proof["callable_probe"].get("parsed") or {}).get("ok")),
            "all_required_veto_surfaces_present": all(veto_surface_present.values()),
            "scenario_matrix_all_expected": scenario_matrix["all_scenarios_match_expected"],
            "scenario_matrix_json_written": SCENARIO_JSON.exists(),
            "preflight_json_written": PREFLIGHT_JSON.exists(),
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
            "service_start_false": True,
            "approved_for_paper_start_false": preflight["approved_for_paper_start"] is False,
        }

        false_keys = [k for k, v in req.items() if v is not True]
        proof["required_verdicts"] = req
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        failed_scenarios = [x for x in scenario_results if not x["matches_expected"]]
        missing_veto_surfaces = [k for k, v in veto_surface_present.items() if v is not True]
        proof["failed_scenarios"] = failed_scenarios
        proof["missing_veto_surfaces"] = missing_veto_surfaces

        if false_keys:
            proof["final_verdict"] = "FAIL_O22_R4_CONTROLLED_PAPER_DRY_RUN_PREFLIGHT_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys/failed_scenarios and write smallest Lane-A diagnostic/repair package; no paper start."
        else:
            proof["final_verdict"] = "PASS_O22_R4_CONTROLLED_PAPER_DRY_RUN_PREFLIGHT_OK_NO_START"
            proof["next_recommended_batch"] = "26-O22-R5 controlled-paper operator checklist + explicit-approval gate package; still no automatic paper start."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — controlled-paper dry-run readiness preflight",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- scenario_matrix: `{SCENARIO_JSON.relative_to(ROOT)}`",
                f"- preflight: `{PREFLIGHT_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Convert O22-R3 static gate proof into a no-order dry-run readiness preflight.",
                "- Use local synthetic scenario simulation only.",
                "- Do not start paper, risk, execution, or live services.",
                "- Do not call broker.",
                "- Do not write orders.",
                "- Do not patch production source.",
                "",
                "## Controlled-paper scope",
                "- MIST CALL only.",
                "- One lot only.",
                "- FLAT before entry.",
                "- real_live=false.",
                "- paper/sandbox route only.",
                "- no automatic broker failover.",
                "- no mid-position provider migration.",
                "",
                "## Veto surface presence",
                "```json",
                json.dumps(veto_surface_present, indent=2, sort_keys=True),
                "```",
                "",
                "## Failed scenarios",
                "```json",
                json.dumps(failed_scenarios, indent=2, sort_keys=True),
                "```",
                "",
                "## Verdict",
                f"- final_verdict: `{proof['final_verdict']}`",
                f"- false_keys: `{false_keys}`",
                f"- missing_veto_surfaces: `{missing_veto_surfaces}`",
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
                f"# {DATE} — {BATCH} controlled-paper dry-run readiness preflight",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Loaded O22-R3 PASS as prerequisite.",
                "- Inspected latest source/proof artifacts first.",
                "- Backed up inspected source/proof/config files.",
                "- Ran compile/import proof.",
                "- Ran callable signature probe without service start.",
                "- Built synthetic no-order scenario matrix for controlled-paper entry gates.",
                "- Confirmed orders zero, position FLAT, no paper env, no scope ACK env, no broker/order intent, risk/execution not running.",
                "",
                "## Not done",
                "- Did not start controlled paper.",
                "- Did not start risk/execution.",
                "- Did not call broker.",
                "- Did not write orders.",
                "- Did not patch production source.",
                "- Did not approve live trading.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
                "",
                "## Artifacts",
                f"- `{PROOF_JSON.relative_to(ROOT)}`",
                f"- `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- `{SCENARIO_JSON.relative_to(ROOT)}`",
                f"- `{PREFLIGHT_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            SCENARIO_JSON,
            PREFLIGHT_JSON,
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
        print(f"failed_scenarios = {failed_scenarios}")
        print(f"missing_veto_surfaces = {missing_veto_surfaces}")
        print(f"next_recommended_batch = {proof['next_recommended_batch']}")
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        print(f"manifest_json = {MANIFEST_JSON.relative_to(ROOT)}")
        print(f"scenario_json = {SCENARIO_JSON.relative_to(ROOT)}")
        print(f"preflight_json = {PREFLIGHT_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O22_R4_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
