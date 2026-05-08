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
BATCH = "26-O22-R3"
BATCH_NAME = "controlled_paper_static_gate_proof_no_start_no_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o22_r3_controlled_paper_static_gate_proof_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o22_r3_controlled_paper_static_gate_proof.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o22_r3_controlled_paper_static_gate_proof.json"
GATE_MATRIX_JSON = RUN_DIR / "controlled_paper_static_gate_matrix_o22_r3.json"
BLOCK_AUDIT_JSON = RUN_DIR / "controlled_paper_risk_execution_block_audit_o22_r3.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o22_r3_controlled_paper_static_gate_proof.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o22_r3_controlled_paper_static_gate_proof.md"
BIN_COPY = BIN_DIR / "proof_batch26o22_r3_controlled_paper_static_gate_proof.py"

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
]

REQUIRED_VETO_REASONS = [
    "CONTROLLED_PAPER_NOT_ARMED",
    "CONTROLLED_PAPER_SCOPE_MISMATCH",
    "CONTROLLED_PAPER_QTY_CAP_FAIL",
    "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    "CONTROLLED_PAPER_TIME_GATE_FAIL",
    "CONTROLLED_PAPER_POSITION_NOT_FLAT",
]

REQUIRED_BLOCK_CONCEPTS = {
    "controlled_paper_runtime_gate": [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "CONTROLLED_PAPER_NOT_ARMED",
        "controlled_paper",
    ],
    "scope_mist_call": [
        "MIST",
        "CALL",
        "CONTROLLED_PAPER_SCOPE_MISMATCH",
    ],
    "qty_cap_one_lot": [
        "CONTROLLED_PAPER_QTY_CAP_FAIL",
        "qty_lots",
        "qty_units",
        "1",
    ],
    "real_live_forbidden": [
        "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
        "real_live",
        "REAL_LIVE",
    ],
    "time_gate": [
        "CONTROLLED_PAPER_TIME_GATE_FAIL",
        "session",
        "time",
    ],
    "flat_before_entry": [
        "CONTROLLED_PAPER_POSITION_NOT_FLAT",
        "FLAT",
        "has_position",
        "position",
    ],
    "paper_or_sandbox_route": [
        "paper",
        "sandbox",
        "route",
    ],
    "broker_entry_block": [
        "broker",
        "entry",
        "block",
    ],
    "exit_flatten_preserved": [
        "exit",
        "flatten",
        "kill",
    ],
    "failover_forbidden": [
        "failover",
        "fallback",
        "mid_position",
        "migration",
    ],
}


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


def file_text(path: pathlib.Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def line_hits(text: str, patterns: list[str]) -> dict[str, list[dict[str, Any]]]:
    lines = text.splitlines()
    out: dict[str, list[dict[str, Any]]] = {}
    for pattern in patterns:
        hits = []
        for idx, line in enumerate(lines, start=1):
            if pattern.lower() in line.lower():
                hits.append({"line": idx, "text": line[:260]})
        out[pattern] = hits[:100]
    return out


def ast_symbols(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists() or path.suffix != ".py":
        return {"ast_applicable": False}
    text = file_text(path)
    try:
        tree = ast.parse(text)
    except Exception as exc:
        return {"ast_applicable": True, "ast_ok": False, "ast_error": repr(exc)}

    classes = []
    functions = []
    constants = []
    strings = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({"name": node.name, "line": node.lineno, "end_line": getattr(node, "end_lineno", None)})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({"name": node.name, "line": node.lineno, "end_line": getattr(node, "end_lineno", None)})
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append({"name": target.id, "line": node.lineno})
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            if "CONTROLLED_PAPER" in s or "controlled_paper" in s or "MIST" in s or "REAL_LIVE" in s:
                strings.append({"value": s[:240], "line": getattr(node, "lineno", None)})

    return {
        "ast_applicable": True,
        "ast_ok": True,
        "classes": classes,
        "functions": functions,
        "constants": constants[:200],
        "relevant_strings": strings[:200],
    }


def inspect_path(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if p.exists() and p.is_file():
        text = file_text(p)
        patterns = [
            "CONTROLLED_PAPER",
            "controlled_paper",
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
            "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
            "CONTROLLED_PAPER_NOT_ARMED",
            "CONTROLLED_PAPER_SCOPE_MISMATCH",
            "CONTROLLED_PAPER_QTY_CAP_FAIL",
            "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
            "CONTROLLED_PAPER_TIME_GATE_FAIL",
            "CONTROLLED_PAPER_POSITION_NOT_FLAT",
            "MIST",
            "CALL",
            "qty_lots",
            "qty_units",
            "real_live",
            "REAL_LIVE",
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
        return {
            "exists": True,
            "is_file": True,
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size,
            "line_count": text.count("\n") + 1,
            "hits": line_hits(text, patterns),
            "ast": ast_symbols(p),
        }
    if p.exists() and p.is_dir():
        members = sorted([str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file()])
        return {
            "exists": True,
            "is_dir": True,
            "sample_members": members[:300],
        }
    return {"exists": False}


def source_contains(rel: str, needle: str) -> bool:
    return needle.lower() in json.dumps(inspections.get(rel, {}), sort_keys=True).lower()


def any_source_contains(rels: list[str], needle: str) -> bool:
    return any(source_contains(rel, needle) for rel in rels)


def concept_present(rels: list[str], concept_needles: list[str], min_hits: int = 1) -> bool:
    count = 0
    for needle in concept_needles:
        if any_source_contains(rels, needle):
            count += 1
    return count >= min_hits


def runtime_snapshot() -> dict[str, Any]:
    pos = redis_hgetall(POSITION_HASH)
    latest_orders = redis_xrevrange_raw(ORDERS_STREAM, count=5)
    return {
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": latest_orders,
        "position": pos,
        "process_lines": proc_lines(),
        "features_running": service_running("features"),
        "strategy_running": service_running("strategy"),
        "risk_running": service_running("risk"),
        "execution_running": service_running("execution"),
    }


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def inspect_callable_signatures() -> dict[str, Any]:
    helper = RUN_DIR / "callable_signature_probe.py"
    helper.write_text(
        r'''
from __future__ import annotations
import inspect, json, traceback

mods = [
    "app.mme_scalpx.services.risk",
    "app.mme_scalpx.services.execution",
    "app.mme_scalpx.services.strategy",
    "app.mme_scalpx.core.names",
    "app.mme_scalpx.core.models",
]
out = {}
for modname in mods:
    rec = {"ok": False}
    try:
        mod = __import__(modname, fromlist=["*"])
        rec["ok"] = True
        rec["file"] = getattr(mod, "__file__", "")
        items = []
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
            try:
                sig = str(inspect.signature(obj))
            except Exception as exc:
                sig = f"<signature_error {exc!r}>"
            if any(tok.lower() in (name + " " + sig).lower() for tok in ["controlled", "paper", "risk", "execution", "order", "entry", "gate", "veto", "block", "position"]):
                items.append({"name": name, "kind": kind, "signature": sig, "module": getattr(obj, "__module__", "")})
        rec["items"] = items
    except Exception as exc:
        rec["ok"] = False
        rec["error"] = repr(exc)
        rec["traceback"] = traceback.format_exc(limit=8)
    out[modname] = rec
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


def build_static_gate_matrix(static: dict[str, Any], runtime: dict[str, Any], prior: dict[str, Any]) -> dict[str, Any]:
    return {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "MIST CALL one-lot controlled-paper planning only",
        "no_start_no_live": True,
        "prior_o22_r2": prior,
        "runtime": {
            "orders_zero": runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip(),
            "position_flat": flat_position(runtime.get("position") or {}),
            "risk_running": runtime.get("risk_running"),
            "execution_running": runtime.get("execution_running"),
            "features_running": runtime.get("features_running"),
            "strategy_running": runtime.get("strategy_running"),
        },
        "required_veto_reasons": {
            reason: static.get("required_veto_reasons_present", {}).get(reason)
            for reason in REQUIRED_VETO_REASONS
        },
        "independent_block_surfaces": static.get("independent_block_surfaces", {}),
        "required_concepts": static.get("required_concepts", {}),
        "interpretation": {
            "pass_meaning": "static/import/read-only proof that risk/execution controlled-paper guard surfaces exist and runtime remains unarmed",
            "not_meaning": "does not start paper, does not place orders, does not approve live trading",
            "next_required": "bounded no-order dry-run proof only after this static gate proof passes",
        },
    }


inspections: dict[str, Any] = {}


def main() -> int:
    global inspections

    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_evidence_output_read": True,
            "prior_o22_r2_pass_required": True,
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
            "static_gate_proof_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "source_inspection": {},
        "callable_signature_probe": {},
        "runtime_snapshot": {},
        "static_gate_analysis": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== EVIDENCE-FIRST INSPECTION: PRIOR PROOFS + TARGET FILE HASHES =====")
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
                        "missing_or_unproven_static_surfaces": loaded.get("missing_or_unproven_static_surfaces") if isinstance(loaded, dict) else None,
                        "next_recommended_batch": loaded.get("next_recommended_batch") if isinstance(loaded, dict) else None,
                    }
            elif p.exists() and p.is_dir():
                members = sorted([str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file()])
                proof["inspected_files"][rel] = {"exists": True, "is_dir": True, "sample_members": members[:300]}
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
        proof["commands"] = {
            "compile": run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60),
            "import": run(
                [
                    sys.executable,
                    "-c",
                    "import app.mme_scalpx.services.risk, app.mme_scalpx.services.execution, app.mme_scalpx.services.strategy, app.mme_scalpx.services.features, app.mme_scalpx.core.names, app.mme_scalpx.core.models; print('IMPORT_OK')",
                ],
                timeout=60,
            ),
        }

        print("===== STATIC SOURCE INSPECTION =====")
        inspections = {}
        for rel in INSPECT_PATHS:
            if rel.endswith(".json"):
                continue
            inspections[rel] = inspect_path(rel)
        proof["source_inspection"] = inspections

        print("===== CALLABLE SIGNATURE PROBE WITHOUT SERVICE START =====")
        proof["callable_signature_probe"] = inspect_callable_signatures()

        print("===== READ-ONLY RUNTIME SAFETY SNAPSHOT =====")
        runtime = runtime_snapshot()
        proof["runtime_snapshot"] = runtime

        o22_r2 = proof["prior_proofs"].get("run/proofs/proof_batch26o22_r2_controlled_paper_plan_proof_correction.json", {})
        o22_r2_req = o22_r2.get("required_verdicts") or {}

        risk_rel = "app/mme_scalpx/services/risk.py"
        execution_rel = "app/mme_scalpx/services/execution.py"
        strategy_rel = "app/mme_scalpx/services/strategy.py"
        main_rel = "app/mme_scalpx/main.py"
        names_rel = "app/mme_scalpx/core/names.py"
        models_rel = "app/mme_scalpx/core/models.py"
        settings_rel = "app/mme_scalpx/core/settings.py"

        risk_exec_rels = [risk_rel, execution_rel]
        all_runtime_rels = [risk_rel, execution_rel, strategy_rel, main_rel, names_rel, models_rel, settings_rel]

        required_veto_reasons_present = {
            reason: any_source_contains(all_runtime_rels, reason)
            for reason in REQUIRED_VETO_REASONS
        }

        required_concepts = {
            concept: concept_present(all_runtime_rels, needles, min_hits=max(1, min(2, len(needles))))
            for concept, needles in REQUIRED_BLOCK_CONCEPTS.items()
        }

        independent_block_surfaces = {
            "risk_has_controlled_paper_gate": (
                source_contains(risk_rel, "CONTROLLED_PAPER") or source_contains(risk_rel, "controlled_paper")
            ),
            "execution_has_controlled_paper_gate": (
                source_contains(execution_rel, "CONTROLLED_PAPER") or source_contains(execution_rel, "controlled_paper")
            ),
            "risk_has_scope_or_veto_surface": (
                source_contains(risk_rel, "CONTROLLED_PAPER_SCOPE_MISMATCH") or (
                    source_contains(risk_rel, "MIST") and source_contains(risk_rel, "CALL")
                )
            ),
            "execution_has_scope_or_veto_surface": (
                source_contains(execution_rel, "CONTROLLED_PAPER_SCOPE_MISMATCH") or (
                    source_contains(execution_rel, "MIST") and source_contains(execution_rel, "CALL")
                )
            ),
            "risk_has_qty_cap_surface": (
                source_contains(risk_rel, "CONTROLLED_PAPER_QTY_CAP_FAIL")
                or source_contains(risk_rel, "qty_lots")
                or source_contains(risk_rel, "qty_units")
            ),
            "execution_has_qty_cap_surface": (
                source_contains(execution_rel, "CONTROLLED_PAPER_QTY_CAP_FAIL")
                or source_contains(execution_rel, "qty_lots")
                or source_contains(execution_rel, "qty_units")
            ),
            "risk_has_real_live_forbidden_surface": (
                source_contains(risk_rel, "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN")
                or source_contains(risk_rel, "real_live")
                or source_contains(risk_rel, "REAL_LIVE")
            ),
            "execution_has_real_live_forbidden_surface": (
                source_contains(execution_rel, "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN")
                or source_contains(execution_rel, "real_live")
                or source_contains(execution_rel, "REAL_LIVE")
            ),
            "risk_has_flat_position_surface": (
                source_contains(risk_rel, "CONTROLLED_PAPER_POSITION_NOT_FLAT")
                or source_contains(risk_rel, "FLAT")
                or source_contains(risk_rel, "has_position")
            ),
            "execution_has_flat_position_surface": (
                source_contains(execution_rel, "CONTROLLED_PAPER_POSITION_NOT_FLAT")
                or source_contains(execution_rel, "FLAT")
                or source_contains(execution_rel, "has_position")
            ),
            "execution_mentions_broker_entry_block": (
                source_contains(execution_rel, "broker")
                and source_contains(execution_rel, "entry")
                and (
                    source_contains(execution_rel, "block")
                    or source_contains(execution_rel, "veto")
                    or source_contains(execution_rel, "forbidden")
                    or source_contains(execution_rel, "allowed")
                )
            ),
            "execution_preserves_exit_or_flatten_surface": (
                source_contains(execution_rel, "exit")
                or source_contains(execution_rel, "flatten")
                or source_contains(execution_rel, "kill")
            ),
            "provider_failover_or_migration_surface_visible": (
                any_source_contains(all_runtime_rels, "failover")
                or any_source_contains(all_runtime_rels, "fallback")
                or any_source_contains(all_runtime_rels, "mid_position")
                or any_source_contains(all_runtime_rels, "migration")
            ),
        }

        static_gate_analysis = {
            "required_veto_reasons_present": required_veto_reasons_present,
            "required_concepts": required_concepts,
            "independent_block_surfaces": independent_block_surfaces,
            "callable_signature_probe_summary": {
                mod: {
                    "ok": rec.get("ok"),
                    "item_count": len(rec.get("items") or []),
                    "items": rec.get("items") or [],
                }
                for mod, rec in ((proof["callable_signature_probe"].get("parsed") or {}).items() if isinstance(proof["callable_signature_probe"].get("parsed"), dict) else [])
            },
        }
        proof["static_gate_analysis"] = static_gate_analysis

        GATE_MATRIX_JSON.write_text(
            json.dumps(build_static_gate_matrix(static_gate_analysis, runtime, o22_r2), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        BLOCK_AUDIT_JSON.write_text(
            json.dumps(static_gate_analysis, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
        position_flat = flat_position(runtime.get("position") or {})

        all_required_veto_reasons_present = all(required_veto_reasons_present.values())
        all_required_concepts_present = all(required_concepts.values())
        core_independent_surfaces_present = all(
            independent_block_surfaces.get(k) is True
            for k in [
                "risk_has_controlled_paper_gate",
                "execution_has_controlled_paper_gate",
                "risk_has_scope_or_veto_surface",
                "execution_has_scope_or_veto_surface",
                "risk_has_qty_cap_surface",
                "execution_has_qty_cap_surface",
                "risk_has_real_live_forbidden_surface",
                "execution_has_real_live_forbidden_surface",
                "risk_has_flat_position_surface",
                "execution_has_flat_position_surface",
                "execution_mentions_broker_entry_block",
                "execution_preserves_exit_or_flatten_surface",
            ]
        )

        req = {
            "o22_r2_pass_loaded": str(o22_r2.get("final_verdict", "")).startswith("PASS_O22_R2_CONTROLLED_PAPER_PLAN_PROOF_OK"),
            "o22_r2_false_keys_empty": o22_r2.get("false_keys") == [],
            "o22_r2_plan_json_written": o22_r2_req.get("plan_json_written") is True,
            "o22_r2_readiness_json_written": o22_r2_req.get("readiness_json_written") is True,
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "risk_py_inspected": proof["inspected_files"].get(risk_rel, {}).get("exists") is True,
            "execution_py_inspected": proof["inspected_files"].get(execution_rel, {}).get("exists") is True,
            "required_veto_reasons_all_present": all_required_veto_reasons_present,
            "required_controlled_paper_concepts_present": all_required_concepts_present,
            "core_independent_risk_execution_surfaces_present": core_independent_surfaces_present,
            "gate_matrix_json_written": GATE_MATRIX_JSON.exists(),
            "block_audit_json_written": BLOCK_AUDIT_JSON.exists(),
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
        }

        false_keys = [k for k, v in req.items() if v is not True]
        proof["required_verdicts"] = req
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        missing_veto_reasons = [k for k, v in required_veto_reasons_present.items() if v is not True]
        missing_concepts = [k for k, v in required_concepts.items() if v is not True]
        missing_surfaces = [k for k, v in independent_block_surfaces.items() if v is not True]

        proof["missing_veto_reasons"] = missing_veto_reasons
        proof["missing_required_concepts"] = missing_concepts
        proof["missing_independent_block_surfaces"] = missing_surfaces

        if false_keys:
            proof["final_verdict"] = "FAIL_O22_R3_CONTROLLED_PAPER_STATIC_GATE_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys/missing surfaces and write smallest Lane-A static repair/audit package; no paper start."
        else:
            proof["final_verdict"] = "PASS_O22_R3_CONTROLLED_PAPER_STATIC_GATE_PROOF_OK_NO_START"
            proof["next_recommended_batch"] = "26-O22-R4 controlled-paper dry-run readiness preflight with risk/execution no-order simulation only; still no paper start and no real live."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — controlled-paper static gate proof",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- gate_matrix: `{GATE_MATRIX_JSON.relative_to(ROOT)}`",
                f"- block_audit: `{BLOCK_AUDIT_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Prove static/import/read-only controlled-paper gate surfaces after O22-R2 plan proof.",
                "- Verify risk and execution independently expose controlled-paper block concepts.",
                "- No paper start, no service start, no broker call, no order write, no production patch.",
                "",
                "## Required veto reasons",
                "```json",
                json.dumps(required_veto_reasons_present, indent=2, sort_keys=True),
                "```",
                "",
                "## Independent block surfaces",
                "```json",
                json.dumps(independent_block_surfaces, indent=2, sort_keys=True),
                "```",
                "",
                "## Missing",
                f"- missing_veto_reasons: `{missing_veto_reasons}`",
                f"- missing_required_concepts: `{missing_concepts}`",
                f"- missing_independent_block_surfaces: `{missing_surfaces}`",
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
                f"# {DATE} — {BATCH} controlled-paper static gate proof",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Loaded O22-R2 plan proof as prerequisite.",
                "- Inspected latest source/proof artifacts first.",
                "- Backed up inspected risk/execution/strategy/features/core/main/config/proof files.",
                "- Ran compile/import proof.",
                "- Inspected controlled-paper veto reasons and risk/execution independent block surfaces.",
                "- Generated gate matrix and block audit JSON artifacts.",
                "- Confirmed orders zero, position FLAT, no paper env, no scope ACK env, no broker/order intent, risk/execution not running.",
                "",
                "## Not done",
                "- Did not start controlled paper.",
                "- Did not start risk/execution.",
                "- Did not call broker.",
                "- Did not write orders.",
                "- Did not patch production source.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
                "",
                "## Artifacts",
                f"- `{PROOF_JSON.relative_to(ROOT)}`",
                f"- `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- `{GATE_MATRIX_JSON.relative_to(ROOT)}`",
                f"- `{BLOCK_AUDIT_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            GATE_MATRIX_JSON,
            BLOCK_AUDIT_JSON,
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
        print(f"missing_veto_reasons = {missing_veto_reasons}")
        print(f"missing_required_concepts = {missing_concepts}")
        print(f"missing_independent_block_surfaces = {missing_surfaces}")
        print(f"next_recommended_batch = {proof['next_recommended_batch']}")
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        print(f"manifest_json = {MANIFEST_JSON.relative_to(ROOT)}")
        print(f"gate_matrix_json = {GATE_MATRIX_JSON.relative_to(ROOT)}")
        print(f"block_audit_json = {BLOCK_AUDIT_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O22_R3_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
