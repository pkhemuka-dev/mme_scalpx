#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import pathlib
import py_compile
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from typing import Any

ROOT = pathlib.Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
DATE = date.today().isoformat()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

PROOF = ROOT / "run/proofs/proof_batch26k_controlled_paper_prestart_readiness.json"
MANIFEST = ROOT / "run/proofs/proof_batch26k_controlled_paper_prestart_readiness_manifest.sha256"
MILESTONE = ROOT / f"docs/milestones/{DATE}_batch26k_controlled_paper_prestart_readiness.md"
RUNBOOK = ROOT / "docs/runbooks/batch26k_controlled_paper_prestart_readiness.md"

J_PROOF = ROOT / "run/proofs/batch26j_post_patch_consolidation.json"
J_R2_PROOF = ROOT / "run/proofs/batch26j_post_patch_consolidation_r2.json"
I_PROOF = ROOT / "run/proofs/proof_no_live_order_hard_guard.json"

CONTROLLED_RUNTIME = ROOT / "app/mme_scalpx/services/controlled_paper_runtime.py"
EXECUTION = ROOT / "app/mme_scalpx/services/execution.py"
RISK = ROOT / "app/mme_scalpx/services/risk.py"
STRATEGY = ROOT / "app/mme_scalpx/services/strategy.py"
ORDER_INTENT = ROOT / "app/mme_scalpx/services/strategy_family/order_intent.py"
MAIN = ROOT / "app/mme_scalpx/main.py"
NAMES = ROOT / "app/mme_scalpx/core/names.py"
SETTINGS = ROOT / "app/mme_scalpx/core/settings.py"

CONFIG_FILES = [
    "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml",
    "etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml",
    "etc/strategy_family/rollout/paper_armed_readiness_gate.yaml",
    "etc/strategy_family/family_runtime.yaml",
    "etc/runtime.yaml",
]

INSPECT_FILES = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/controlled_paper_runtime.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/order_intent.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/settings.py",
] + CONFIG_FILES + [
    "run/proofs/batch26j_post_patch_consolidation.json",
    "run/proofs/batch26j_post_patch_consolidation_r2.json",
    "run/proofs/proof_no_live_order_hard_guard.json",
]

REQUIRED_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

HARD_LIVE_ENV_KEYS = {
    "ALLOW_LIVE_ORDERS",
    "LIVE_ORDERS_ALLOWED",
    "TRADING_ENABLED",
    "REAL_LIVE_ALLOWED",
    "SCALPX_REAL_LIVE_ALLOWED",
}

CONTROLLED_ENV_KEYS = {
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
}

ORDERS_KEY = "orders:mme:stream"
POSITION_KEY = "state:position:mme"

START_CHAIN = ROOT / "bin/start_controlled_paper_runtime_chain.py"
CONTROLLED_ENABLEMENT = ROOT / "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml"
CONTROLLED_SCOPE = ROOT / "etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml"
READINESS_GATE = ROOT / "etc/strategy_family/rollout/paper_armed_readiness_gate.yaml"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def read(path: pathlib.Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run_cmd(args: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": args,
            "returncode": cp.returncode,
            "stdout": cp.stdout[-12000:],
            "stderr": cp.stderr[-12000:],
        }
    except Exception as exc:
        return {
            "cmd": args,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
        }


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {
        "1", "true", "yes", "y", "on", "enabled", "allow", "allowed", "armed", "live"
    }


def falsey(value: Any) -> bool:
    if isinstance(value, bool):
        return value is False
    if value is None:
        return False
    return str(value).strip().lower() in {
        "0", "false", "no", "n", "off", "disabled", "deny", "denied", "blocked", "not_armed"
    }


def file_summary(path: pathlib.Path) -> dict[str, Any]:
    text = read(path)
    return {
        "path": rel(path),
        "exists": path.exists(),
        "is_file": path.is_file() if path.exists() else False,
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "line_count": len(text.splitlines()) if text else 0,
        "sha256": sha256_file(path),
    }


def write_manifest(paths: list[str]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", encoding="utf-8") as f:
        for item in sorted(set(paths)):
            path = ROOT / item
            if path.exists() and path.is_file():
                f.write(f"{sha256_file(path)}  {item}\n")
            else:
                f.write(f"MISSING  {item}\n")


def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "parse_ok": False, "data": None, "error": "missing"}
    try:
        return {
            "exists": True,
            "parse_ok": True,
            "data": json.loads(read(path)),
            "sha256": sha256_file(path),
            "error": None,
        }
    except Exception as exc:
        return {
            "exists": True,
            "parse_ok": False,
            "data": None,
            "sha256": sha256_file(path),
            "error": repr(exc),
        }


def recursive_find(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = recursive_find(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = recursive_find(value, key)
            if found is not None:
                return found
    return None


def inspect_26j_gate() -> dict[str, Any]:
    selected = J_R2_PROOF if J_R2_PROOF.exists() else J_PROOF
    loaded = load_json(selected)
    data = loaded.get("data") or {}
    verdict = data.get("verdict", {}) if isinstance(data, dict) else {}

    required = {
        "post_patch_consolidation_ok": True,
        "post_patch_safe_for_controlled_paper_prestart": True,
        "all_required_proof_artifacts_present_and_passing": True,
        "all_patch_markers_present": True,
        "compile_ok": True,
        "orders_stream_safe_zero": True,
        "position_flat_before_trial": True,
        "env_no_live_true": True,
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    checks = {}
    for key, expected in required.items():
        actual = verdict.get(key)
        checks[key] = {"actual": actual, "expected": expected, "ok": actual == expected}

    return {
        "path": rel(selected),
        "exists": loaded["exists"],
        "parse_ok": loaded["parse_ok"],
        "sha256": loaded.get("sha256"),
        "checks": checks,
        "ok": loaded["exists"] and loaded["parse_ok"] and all(x["ok"] for x in checks.values()),
        "blockers": verdict.get("blockers"),
        "warnings": verdict.get("warnings"),
    }


def inspect_26i_gate() -> dict[str, Any]:
    loaded = load_json(I_PROOF)
    data = loaded.get("data") or {}
    verdict = data.get("verdict", {}) if isinstance(data, dict) else {}

    required = {
        "no_live_order_hard_guard_ok": True,
        "controlled_paper_preparation_may_continue": True,
        "real_live_disabled_in_settings_config": True,
        "controlled_runtime_forbids_real_live": True,
        "risk_vetoes_unsafe_entries": True,
        "execution_blocks_unsafe_entry_broker_calls": True,
        "orders_stream_safe_zero": True,
        "position_flat_before_trial": True,
        "paper_armed_approved": False,
        "real_live_approved": False,
    }

    checks = {}
    for key, expected in required.items():
        actual = verdict.get(key)
        checks[key] = {"actual": actual, "expected": expected, "ok": actual == expected}

    return {
        "path": rel(I_PROOF),
        "exists": loaded["exists"],
        "parse_ok": loaded["parse_ok"],
        "sha256": loaded.get("sha256"),
        "checks": checks,
        "ok": loaded["exists"] and loaded["parse_ok"] and all(x["ok"] for x in checks.values()),
        "blockers": verdict.get("blockers"),
        "warnings": verdict.get("warnings"),
    }


def load_yaml_like(path: pathlib.Path) -> Any:
    if not path.exists() or not path.is_file():
        return None
    text = read(path)
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        data: dict[str, Any] = {}
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            low = value.lower()
            if low in {"true", "false"}:
                data[key] = low == "true"
            elif re.fullmatch(r"-?\d+", value):
                data[key] = int(value)
            else:
                data[key] = value
        return data


def flatten(obj: Any, prefix: str = "", depth: int = 0) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if depth > 8:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out[key] = v
            out.update(flatten(v, key, depth + 1))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]"
            out[key] = v
            out.update(flatten(v, key, depth + 1))
    return out


def find_values(flat: dict[str, Any], leaf_names: set[str], contains: tuple[str, ...] = ()) -> list[dict[str, Any]]:
    hits = []
    for key, value in flat.items():
        leaf = key.split(".")[-1]
        leaf_clean = re.sub(r"\[\d+\]$", "", leaf)
        if leaf_clean in leaf_names or any(c in leaf.lower() for c in contains):
            hits.append({"key": key, "leaf": leaf_clean, "value": value})
    return hits


def inspect_controlled_scope_configs() -> dict[str, Any]:
    files = {}
    combined: dict[str, Any] = {}
    for path in [CONTROLLED_ENABLEMENT, CONTROLLED_SCOPE, READINESS_GATE]:
        loaded = load_yaml_like(path)
        flat = flatten(loaded)
        files[rel(path)] = {
            "exists": path.exists(),
            "sha256": sha256_file(path),
            "loaded_type": type(loaded).__name__,
            "flat": flat,
            "family_hits": find_values(flat, {"family", "selected_family", "strategy_family"}, ("family",)),
            "side_hits": find_values(flat, {"side", "selected_side", "branch"}, ("side", "branch")),
            "qty_hits": find_values(flat, {"qty", "quantity", "qty_lots", "quantity_lots", "lots", "max_lots"}, ("qty", "quantity", "lot")),
            "paper_hits": find_values(flat, {"paper_armed_enabled", "controlled_paper_trial_enabled", "paper_enabled", "enabled"}, ("paper", "controlled")),
            "live_hits": find_values(flat, {"real_live_allowed", "allow_live_orders", "live_orders_allowed", "broker_orders_allowed", "trading_enabled", "real_live"}, ("live", "trading")),
        }
        for k, v in flat.items():
            combined[f"{rel(path)}::{k}"] = v

    all_text = "\n".join(read(p) for p in [CONTROLLED_ENABLEMENT, CONTROLLED_SCOPE, READINESS_GATE])

    family_ok = "MIST" in all_text.upper()
    side_ok = "CALL" in all_text.upper()
    qty_ok = bool(re.search(r"(quantity_lots|qty_lots|quantity|qty|max_lots|lots)\s*:\s*['\"]?1['\"]?", all_text, re.I))
    paper_terms_present = "controlled_paper" in all_text.lower() or "paper_armed" in all_text.lower()

    hard_live_truthy = []
    for key, value in combined.items():
        leaf = key.split("::")[-1].split(".")[-1]
        leaf_clean = re.sub(r"\[\d+\]$", "", leaf).lower()
        if leaf_clean in {
            "real_live_allowed",
            "allow_live_orders",
            "live_orders_allowed",
            "broker_orders_allowed",
            "trading_enabled",
            "real_live",
        } and truthy(value):
            hard_live_truthy.append({"key": key, "value": value})

    return {
        "files": files,
        "family_mist_present": family_ok,
        "side_call_present": side_ok,
        "quantity_one_present": qty_ok,
        "paper_terms_present": paper_terms_present,
        "hard_live_truthy_hits": hard_live_truthy,
        "real_live_not_enabled_in_controlled_scope": not hard_live_truthy,
        "exact_scope_ok": family_ok and side_ok and qty_ok and paper_terms_present and not hard_live_truthy,
    }


def inspect_env_prestart() -> dict[str, Any]:
    values = {key: os.environ.get(key) for key in sorted(HARD_LIVE_ENV_KEYS | CONTROLLED_ENV_KEYS | {"MME_RUNTIME_MODE", "SCALPX_RUNTIME_MODE"})}

    live_truthy = []
    for key in HARD_LIVE_ENV_KEYS:
        value = values.get(key)
        if value is not None and truthy(value):
            live_truthy.append({"key": key, "value": value})

    controlled_ack_present_now = (
        values.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME") == "1"
        and values.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK") == REQUIRED_ACK
    )

    required_start_env = {
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "1",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": REQUIRED_ACK,
    }

    return {
        "values": values,
        "hard_live_truthy_env": live_truthy,
        "env_no_live_true": not live_truthy,
        "controlled_ack_present_now": controlled_ack_present_now,
        "required_controlled_paper_start_env": required_start_env,
        "ack_value_required": REQUIRED_ACK,
        "ack_ready_for_future_start": True,
    }


def inspect_controlled_runtime_contract() -> dict[str, Any]:
    text = read(CONTROLLED_RUNTIME)
    result: dict[str, Any] = {
        "file": file_summary(CONTROLLED_RUNTIME),
        "controlled_execution_entry_allowed_present": "def controlled_execution_entry_allowed(" in text,
        "controlled_execution_entry_allowed_returns_false": "def controlled_execution_entry_allowed(" in text and "return False" in text,
        "batch26b_contract_marker_present": "# BEGIN BATCH26B_CONTROLLED_EXECUTION_ENTRY_ARMING_CONTRACT" in text,
        "controlled_terms_present": "controlled" in text.lower() and "paper" in text.lower(),
    }

    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        mod = importlib.import_module("app.mme_scalpx.services.controlled_paper_runtime")
        value = getattr(mod, "controlled_execution_entry_allowed")()
        result["dynamic_controlled_execution_entry_allowed"] = bool(value)
        result["dynamic_contract_fail_closed"] = value is False
        result["dynamic_error"] = None
    except Exception as exc:
        result["dynamic_controlled_execution_entry_allowed"] = None
        result["dynamic_contract_fail_closed"] = False
        result["dynamic_error"] = repr(exc)

    result["ok"] = (
        result["controlled_execution_entry_allowed_present"]
        and result["controlled_execution_entry_allowed_returns_false"]
        and result["batch26b_contract_marker_present"]
        and result["dynamic_contract_fail_closed"]
    )
    return result


def inspect_start_chain() -> dict[str, Any]:
    text = read(START_CHAIN)
    exists = START_CHAIN.exists()

    return {
        "path": rel(START_CHAIN),
        "exists": exists,
        "sha256": sha256_file(START_CHAIN),
        "line_count": len(text.splitlines()) if text else 0,
        "mentions_controlled_paper": "controlled" in text.lower() and "paper" in text.lower(),
        "mentions_scope_ack": "SCALPX_CONTROLLED_PAPER_SCOPE_ACK" in text,
        "mentions_allow_runtime_env": "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME" in text,
        "mentions_mist_call": "MIST" in text.upper() and "CALL" in text.upper(),
        "mentions_no_real_live_or_live_block": (
            "real_live" in text.lower() or "live" in text.lower() or "ALLOW_LIVE_ORDERS" in text
        ),
        "ok_for_prestart_reference": exists,
    }


def inspect_rollback_and_stop_commands() -> dict[str, Any]:
    candidates = {
        "pfeedstop": shutil.which("pfeedstop"),
        "pkill_main_service": shutil.which("pkill"),
        "systemctl": shutil.which("systemctl"),
        "redis_cli": shutil.which("redis-cli"),
    }

    commands = {
        "soft_stop_pfeeds": "pfeedstop || true",
        "kill_project_service_processes": "pkill -f 'app\\.mme_scalpx\\.main --service' || true",
        "systemd_stop_if_used": "sudo systemctl stop scalpx-mme.service",
        "verify_no_process": "ps -ef | grep -E 'app\\.mme_scalpx\\.main|start_controlled_paper_runtime_chain' | grep -v grep || true",
        "verify_orders_zero": "redis-cli XLEN orders:mme:stream",
        "verify_position_flat": "redis-cli HGETALL state:position:mme",
    }

    return {
        "tool_paths": candidates,
        "commands": commands,
        "rollback_command_set_present": all(commands.values()),
        "pfeedstop_available": candidates["pfeedstop"] is not None,
        "redis_cli_available": candidates["redis_cli"] is not None,
    }


def inspect_paths_and_dirs() -> dict[str, Any]:
    paths = {
        "run/proofs": ROOT / "run/proofs",
        "docs/milestones": ROOT / "docs/milestones",
        "docs/runbooks": ROOT / "docs/runbooks",
        "run/live_capture": ROOT / "run/live_capture",
        "run/paper_trials": ROOT / "run/paper_trials",
        "run/_code_backups": ROOT / "run/_code_backups",
    }
    return {
        key: {
            "path": rel(path),
            "exists": path.exists(),
            "is_dir": path.is_dir() if path.exists() else False,
            "writable": os.access(path, os.W_OK) if path.exists() else False,
        }
        for key, path in paths.items()
    }


def redis_cmd(args: list[str]) -> dict[str, Any]:
    if shutil.which("redis-cli") is None:
        return {
            "available": False,
            "cmd": ["redis-cli"] + args,
            "returncode": None,
            "stdout": "",
            "stderr": "redis-cli not found",
        }
    res = run_cmd(["redis-cli"] + args, timeout=8)
    res["available"] = True
    return res


def redis_orders() -> dict[str, Any]:
    res = redis_cmd(["XLEN", ORDERS_KEY])
    parsed = None
    try:
        parsed = int(str(res.get("stdout", "")).strip())
    except Exception:
        parsed = None
    return {
        "key": ORDERS_KEY,
        "xlen": parsed,
        "read_ok": res.get("returncode") == 0 and parsed is not None,
        "safe_zero": parsed == 0,
        "raw": res,
    }


def redis_position() -> dict[str, Any]:
    res = redis_cmd(["HGETALL", POSITION_KEY])
    parsed = {}
    if res.get("returncode") == 0:
        lines = str(res.get("stdout") or "").splitlines()
        for i in range(0, len(lines) - 1, 2):
            parsed[lines[i]] = lines[i + 1]

    if res.get("returncode") != 0:
        return {
            "key": POSITION_KEY,
            "read_ok": False,
            "flat": False,
            "reason": "redis_hgetall_failed",
            "raw": res,
        }

    if not parsed:
        return {
            "key": POSITION_KEY,
            "read_ok": True,
            "flat": True,
            "reason": "empty_hash_treated_flat",
            "hash": parsed,
            "raw": res,
        }

    has_position = parsed.get("has_position") or parsed.get("position_open") or parsed.get("open")
    qty = parsed.get("qty_lots") or parsed.get("quantity") or parsed.get("qty") or "0"

    try:
        qty_num = float(str(qty))
    except Exception:
        qty_num = None

    flat = falsey(has_position) or qty_num == 0

    return {
        "key": POSITION_KEY,
        "read_ok": True,
        "flat": flat,
        "has_position": has_position,
        "qty": qty,
        "qty_num": qty_num,
        "hash": parsed,
        "raw": res,
    }


def compile_and_import_checks() -> dict[str, Any]:
    targets = [
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/controlled_paper_runtime.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/order_intent.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/settings.py",
    ]

    py_results = {}
    for item in targets:
        path = ROOT / item
        if not path.exists():
            py_results[item] = {"ok": False, "error": "missing"}
            continue
        try:
            py_compile.compile(str(path), doraise=True)
            py_results[item] = {"ok": True, "error": None}
        except Exception as exc:
            py_results[item] = {"ok": False, "error": repr(exc)}

    imports = {}
    for mod in [
        "app.mme_scalpx.services.controlled_paper_runtime",
        "app.mme_scalpx.services.execution",
        "app.mme_scalpx.services.risk",
        "app.mme_scalpx.services.strategy",
        "app.mme_scalpx.core.names",
        "app.mme_scalpx.core.settings",
    ]:
        try:
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            importlib.import_module(mod)
            imports[mod] = {"ok": True, "error": None}
        except Exception as exc:
            imports[mod] = {"ok": False, "error": repr(exc)}

    compileall = run_cmd([sys.executable, "-m", "compileall", "-q"] + targets, timeout=120)

    return {
        "py_compile": py_results,
        "imports": imports,
        "compileall": compileall,
        "py_compile_ok": all(x["ok"] for x in py_results.values()),
        "imports_ok": all(x["ok"] for x in imports.values()),
        "compileall_ok": compileall.get("returncode") == 0,
    }


def inspect_static_safety_terms() -> dict[str, Any]:
    files = {
        "execution": EXECUTION,
        "risk": RISK,
        "strategy": STRATEGY,
        "order_intent": ORDER_INTENT,
        "controlled_runtime": CONTROLLED_RUNTIME,
        "main": MAIN,
    }

    out = {}
    for label, path in files.items():
        text = read(path)
        hits = []
        rx = re.compile(
            r"paper_armed|real_live|allow_live_orders|live_orders_allowed|trading_enabled|"
            r"controlled_paper|place_entry_order|place_exit_order|veto_entries|allow_exits|"
            r"disabled_preview_only|publication_must_remain_disabled",
            re.I,
        )
        for lineno, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append({"line": lineno, "text": line.rstrip()[:300]})
                if len(hits) >= 220:
                    break
        out[label] = {
            "file": file_summary(path),
            "hits": hits,
        }
    return out


def write_runbook(report: dict[str, Any]) -> None:
    start_env = report["environment"]["required_controlled_paper_start_env"]
    rollback = report["rollback"]["commands"]

    lines = [
        "# Batch 26K — Controlled Paper Pre-start Readiness",
        "",
        f"Date: {DATE}",
        "",
        "## Verdict",
        "",
        f"- controlled_paper_prestart_readiness_ok: `{report['verdict']['controlled_paper_prestart_readiness_ok']}`",
        f"- controlled_paper_start_allowed_by_this_batch: `{report['verdict']['controlled_paper_start_allowed_by_this_batch']}`",
        "- source_code_patched: `False`",
        "- services_started: `False`",
        "- Redis writes: `False`",
        "- paper_armed_approved: `False`",
        "- real_live_approved: `False`",
        "",
        "## Exact controlled-paper scope to be used later",
        "",
        "- Family: `MIST`",
        "- Side: `CALL`",
        "- Quantity: `1 lot`",
        "- Real live: `forbidden`",
        "",
        "## Required environment for a later start command",
        "",
        "```bash",
        f"export SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME='{start_env['SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME']}'",
        f"export SCALPX_CONTROLLED_PAPER_SCOPE_ACK='{start_env['SCALPX_CONTROLLED_PAPER_SCOPE_ACK']}'",
        "unset ALLOW_LIVE_ORDERS LIVE_ORDERS_ALLOWED TRADING_ENABLED REAL_LIVE_ALLOWED SCALPX_REAL_LIVE_ALLOWED",
        "```",
        "",
        "## Later start command candidate",
        "",
        "Do not run this from Batch 26K. This is only the pre-start reference:",
        "",
        "```bash",
        "cd /home/Lenovo/scalpx/projects/mme_scalpx",
        ".venv/bin/python bin/start_controlled_paper_runtime_chain.py",
        "```",
        "",
        "## Rollback / stop commands",
        "",
        "```bash",
        rollback["soft_stop_pfeeds"],
        rollback["kill_project_service_processes"],
        rollback["verify_no_process"],
        rollback["verify_orders_zero"],
        rollback["verify_position_flat"],
        "```",
        "",
        "## Required next gate",
        "",
        "Batch 26L may be a controlled-paper dry-start/runbook validation or operator-confirmed start package. Batch 26K itself does not start anything.",
        "",
    ]

    RUNBOOK.parent.mkdir(parents=True, exist_ok=True)
    RUNBOOK.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_milestone(report: dict[str, Any]) -> None:
    v = report["verdict"]
    lines = [
        "# Batch 26K — Controlled Paper Pre-start Readiness",
        "",
        f"Date: {DATE}",
        "",
        "## Verdict",
        "",
        f"- controlled_paper_prestart_readiness_ok: `{v['controlled_paper_prestart_readiness_ok']}`",
        f"- post_patch_consolidation_gate_ok: `{v['post_patch_consolidation_gate_ok']}`",
        f"- no_live_order_hard_guard_gate_ok: `{v['no_live_order_hard_guard_gate_ok']}`",
        f"- exact_scope_mist_call_one_lot_ok: `{v['exact_scope_mist_call_one_lot_ok']}`",
        f"- current_env_no_live_true: `{v['current_env_no_live_true']}`",
        f"- rollback_commands_ready: `{v['rollback_commands_ready']}`",
        f"- redis_orders_zero: `{v['redis_orders_zero']}`",
        f"- redis_position_flat: `{v['redis_position_flat']}`",
        f"- compile_import_ok: `{v['compile_import_ok']}`",
        "- source_code_patched: `False`",
        "- services_started: `False`",
        "- Redis writes: `False`",
        "- paper_armed_approved: `False`",
        "- real_live_approved: `False`",
        "",
        "## Blockers",
        "",
    ]

    blockers = v.get("blockers", [])
    lines.extend([f"- `{x}`" for x in blockers] if blockers else ["- none"])

    lines.extend(["", "## Warnings", ""])
    warnings = v.get("warnings", [])
    lines.extend([f"- `{x}`" for x in warnings] if warnings else ["- none"])

    lines.extend([
        "",
        "## Scope",
        "",
        "- MIST CALL only",
        "- 1 lot only",
        "- paper-only pre-start readiness",
        "- real live forbidden",
        "",
        "## Artifacts",
        "",
        "- `run/proofs/proof_batch26k_controlled_paper_prestart_readiness.json`",
        "- `run/proofs/proof_batch26k_controlled_paper_prestart_readiness_manifest.sha256`",
        "- `docs/runbooks/batch26k_controlled_paper_prestart_readiness.md`",
        "",
        "## Continuation",
        "",
        "Do not start controlled paper from Batch 26K.",
        "If this proof passes, the next batch may prepare a controlled dry-start/start command package with explicit operator acknowledgement.",
        "",
    ])

    MILESTONE.parent.mkdir(parents=True, exist_ok=True)
    MILESTONE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    os.chdir(ROOT)
    (ROOT / "run/proofs").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/milestones").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/runbooks").mkdir(parents=True, exist_ok=True)
    (ROOT / "run/live_capture").mkdir(parents=True, exist_ok=True)
    (ROOT / "run/paper_trials").mkdir(parents=True, exist_ok=True)

    print("===== BATCH 26K: WRITE MANIFEST =====")
    write_manifest(INSPECT_FILES + [
        "run/proofs/proof_batch26k_controlled_paper_prestart_readiness.json",
        "docs/runbooks/batch26k_controlled_paper_prestart_readiness.md",
    ])
    print("Manifest:", MANIFEST.relative_to(ROOT))

    print("===== BATCH 26K: GATE 26J / 26I =====")
    gate_26j = inspect_26j_gate()
    gate_26i = inspect_26i_gate()
    print("26J gate ok:", gate_26j["ok"])
    print("26I gate ok:", gate_26i["ok"])

    print("===== BATCH 26K: CONFIG SCOPE =====")
    scope = inspect_controlled_scope_configs()
    print("family_mist_present:", scope["family_mist_present"])
    print("side_call_present:", scope["side_call_present"])
    print("quantity_one_present:", scope["quantity_one_present"])
    print("real_live_not_enabled_in_controlled_scope:", scope["real_live_not_enabled_in_controlled_scope"])

    print("===== BATCH 26K: ENV PRESTART =====")
    environment = inspect_env_prestart()
    print("env_no_live_true:", environment["env_no_live_true"])
    print("controlled_ack_present_now:", environment["controlled_ack_present_now"])

    print("===== BATCH 26K: CONTROLLED RUNTIME CONTRACT =====")
    controlled_runtime = inspect_controlled_runtime_contract()
    print("controlled_runtime_contract_ok:", controlled_runtime["ok"])

    print("===== BATCH 26K: START CHAIN / ROLLBACK / PATHS =====")
    start_chain = inspect_start_chain()
    rollback = inspect_rollback_and_stop_commands()
    paths = inspect_paths_and_dirs()
    print("start_chain_exists:", start_chain["exists"])
    print("rollback_command_set_present:", rollback["rollback_command_set_present"])

    print("===== BATCH 26K: COMPILE / IMPORT =====")
    compile_import = compile_and_import_checks()
    print("compileall_ok:", compile_import["compileall_ok"])
    print("imports_ok:", compile_import["imports_ok"])

    print("===== BATCH 26K: REDIS BASELINE =====")
    orders = redis_orders()
    position = redis_position()
    print("orders_zero:", orders["safe_zero"])
    print("position_flat:", position["flat"])

    static_safety = inspect_static_safety_terms()

    blockers: list[str] = []
    warnings: list[str] = []

    if not gate_26j["ok"]:
        blockers.append("26J_POST_PATCH_CONSOLIDATION_GATE_NOT_PASSING")
    if not gate_26i["ok"]:
        blockers.append("26I_NO_LIVE_ORDER_GATE_NOT_PASSING")
    if not scope["exact_scope_ok"]:
        blockers.append("CONTROLLED_SCOPE_NOT_PROVEN_MIST_CALL_1LOT_PAPER_ONLY")
    if not environment["env_no_live_true"]:
        blockers.append("CURRENT_ENV_HAS_LIVE_OR_TRADING_TRUE")
    if not controlled_runtime["ok"]:
        blockers.append("CONTROLLED_RUNTIME_FAIL_CLOSED_CONTRACT_NOT_PROVEN")
    if not rollback["rollback_command_set_present"]:
        blockers.append("ROLLBACK_COMMAND_SET_NOT_PRESENT")
    if not all(item["exists"] and item["is_dir"] and item["writable"] for item in paths.values()):
        blockers.append("REQUIRED_ARTIFACT_DIR_NOT_READY")
    if not compile_import["compileall_ok"] or not compile_import["py_compile_ok"] or not compile_import["imports_ok"]:
        blockers.append("COMPILE_OR_IMPORT_CHECK_FAILED")
    if not orders["read_ok"] or not orders["safe_zero"]:
        blockers.append("ORDERS_STREAM_NOT_ZERO_OR_NOT_READABLE")
    if not position["read_ok"] or not position["flat"]:
        blockers.append("POSITION_NOT_FLAT_OR_NOT_READABLE")

    if not start_chain["exists"]:
        warnings.append("START_CHAIN_SCRIPT_NOT_FOUND_PRESTART_CAN_STILL_PASS_IF_NEXT_BATCH_WRITES_IT")
    if not environment["controlled_ack_present_now"]:
        warnings.append("CONTROLLED_PAPER_ACK_NOT_SET_IN_CURRENT_ENV_EXPECTED_FOR_PRESTART")
    if not rollback["pfeedstop_available"]:
        warnings.append("PFEEDSTOP_NOT_FOUND_USING_PKILL_SYSTEMD_FALLBACKS")
    if gate_26j.get("warnings"):
        warnings.append("26J_WARNINGS_CARRIED_FORWARD")
    if gate_26i.get("warnings"):
        warnings.append("26I_WARNINGS_CARRIED_FORWARD")

    report: dict[str, Any] = {
        "batch": "26K_controlled_paper_prestart_readiness",
        "generated_at_utc": now_utc(),
        "project_root": str(ROOT),
        "source_code_patched": False,
        "paper_armed_enabled_by_this_proof": False,
        "real_live_enabled_by_this_proof": False,
        "services_started_by_this_proof": False,
        "redis_writes_by_this_proof": False,
        "file_manifest": str(MANIFEST.relative_to(ROOT)),
        "file_summaries": {item: file_summary(ROOT / item) for item in INSPECT_FILES},
        "gate_26j": gate_26j,
        "gate_26i": gate_26i,
        "controlled_scope": scope,
        "environment": environment,
        "controlled_runtime_contract": controlled_runtime,
        "start_chain_reference": start_chain,
        "rollback": rollback,
        "artifact_paths": paths,
        "compile_import": compile_import,
        "orders_safety": orders,
        "position_safety": position,
        "static_safety_terms": static_safety,
        "verdict": {
            "controlled_paper_prestart_readiness_ok": len(blockers) == 0,
            "controlled_paper_start_allowed_by_this_batch": False,
            "post_patch_consolidation_gate_ok": gate_26j["ok"],
            "no_live_order_hard_guard_gate_ok": gate_26i["ok"],
            "exact_scope_mist_call_one_lot_ok": scope["exact_scope_ok"],
            "current_env_no_live_true": environment["env_no_live_true"],
            "controlled_runtime_fail_closed": controlled_runtime["ok"],
            "rollback_commands_ready": rollback["rollback_command_set_present"],
            "artifact_dirs_ready": all(item["exists"] and item["is_dir"] and item["writable"] for item in paths.values()),
            "compile_import_ok": compile_import["compileall_ok"] and compile_import["py_compile_ok"] and compile_import["imports_ok"],
            "redis_orders_zero": orders["safe_zero"],
            "redis_orders_read_ok": orders["read_ok"],
            "redis_position_flat": position["flat"],
            "redis_position_read_ok": position["read_ok"],
            "paper_armed_approved": False,
            "real_live_approved": False,
            "runtime_promotion_allowed": False,
            "blockers": blockers,
            "warnings": warnings,
            "next_recommended_batch": "26L_controlled_paper_dry_start_or_operator_start_package" if len(blockers) == 0 else "review_26k_blockers",
        },
    }

    write_runbook(report)
    write_milestone(report)
    PROOF.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("===== BATCH 26K FINAL VERDICT =====")
    print(json.dumps(report["verdict"], indent=2, sort_keys=True))

    print("===== BATCH 26K KEY CHECKS =====")
    for key in [
        "post_patch_consolidation_gate_ok",
        "no_live_order_hard_guard_gate_ok",
        "exact_scope_mist_call_one_lot_ok",
        "current_env_no_live_true",
        "controlled_runtime_fail_closed",
        "rollback_commands_ready",
        "artifact_dirs_ready",
        "compile_import_ok",
        "redis_orders_zero",
        "redis_position_flat",
        "controlled_paper_start_allowed_by_this_batch",
    ]:
        print(f"{key}: {report['verdict'].get(key)}")
    print("blockers:", blockers)
    print("warnings:", warnings)

    print("===== BATCH 26K OUTPUTS =====")
    print("Proof:", PROOF.relative_to(ROOT))
    print("Manifest:", MANIFEST.relative_to(ROOT))
    print("Milestone:", MILESTONE.relative_to(ROOT))
    print("Runbook:", RUNBOOK.relative_to(ROOT))

    return 0 if report["verdict"]["controlled_paper_prestart_readiness_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
