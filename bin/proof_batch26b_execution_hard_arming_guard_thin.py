#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import pathlib
import py_compile
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXECUTION = ROOT / "app/mme_scalpx/services/execution.py"
CPR = ROOT / "app/mme_scalpx/services/controlled_paper_runtime.py"
PROOF = ROOT / "run/proofs/batch26b_execution_hard_arming_guard_thin.json"
GUARD_MARKER = "# BATCH26B_EXECUTION_ENTRY_HARD_ARMING_GUARD"


def sha256(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run_cmd(cmd: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        cp = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout[-6000:],
            "stderr": cp.stderr[-6000:],
        }
    except Exception as exc:
        return {"cmd": cmd, "returncode": None, "stdout": "", "stderr": repr(exc)}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def actual_entry_calls(text: str) -> list[dict[str, Any]]:
    out = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if "self.broker.place_entry_order(" in line and not line.strip().startswith("#"):
            out.append({"line": lineno, "text": line.rstrip()})
    return out


def actual_exit_calls(text: str) -> list[dict[str, Any]]:
    out = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if "self.broker.place_exit_order(" in line and not line.strip().startswith("#"):
            out.append({"line": lineno, "text": line.rstrip()})
    return out


def guard_status(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    guarded = []
    unguarded = []
    for call in actual_entry_calls(text):
        idx = call["line"] - 1
        window = "\n".join(lines[max(0, idx - 12):idx])
        ok = (
            GUARD_MARKER in window
            and "entry_armed, entry_arm_reason = _batch26b_execution_entry_hard_arming_verdict()" in window
            and "self._fail_decision(decision, entry_arm_reason)" in window
            and "return" in window
        )
        if ok:
            guarded.append(call)
        else:
            unguarded.append(call)

    guard_near_exit = []
    for call in actual_exit_calls(text):
        idx = call["line"] - 1
        window = "\n".join(lines[max(0, idx - 12):idx])
        if GUARD_MARKER in window:
            guard_near_exit.append(call)

    return {
        "guarded_entry_calls": guarded,
        "unguarded_entry_calls": unguarded,
        "guard_near_exit_calls": guard_near_exit,
    }


def redis_readonly_snapshot() -> dict[str, Any]:
    # No new Redis names are introduced here. This proof relies primarily on
    # Batch 26A current-repo truth for orders/position. If Redis is unavailable,
    # this remains informational only.
    result = {
        "available": False,
        "orders_stream_len": None,
        "position_hash": None,
        "error": None,
    }
    try:
        from app.mme_scalpx.core import names as N
        import shutil

        redis_cli = shutil.which("redis-cli")
        if not redis_cli:
            result["error"] = "redis-cli not found"
            return result

        orders_key = getattr(N, "STREAM_ORDERS_MME", None)
        position_key = getattr(N, "HASH_STATE_POSITION_MME", None)

        if not orders_key or not position_key:
            result["error"] = "names.py orders/position constants not found; redis check skipped"
            return result

        result["available"] = True
        result["orders_key_constant"] = "STREAM_ORDERS_MME"
        result["position_key_constant"] = "HASH_STATE_POSITION_MME"

        xlen = run_cmd(["redis-cli", "XLEN", str(orders_key)], timeout=8)
        try:
            result["orders_stream_len"] = int(str(xlen.get("stdout", "")).strip())
        except Exception:
            result["orders_stream_len"] = None

        hget = run_cmd(["redis-cli", "HGETALL", str(position_key)], timeout=8)
        lines = str(hget.get("stdout") or "").splitlines()
        parsed = {}
        for i in range(0, len(lines) - 1, 2):
            parsed[lines[i]] = lines[i + 1]
        result["position_hash"] = parsed
        return result
    except Exception as exc:
        result["error"] = repr(exc)
        return result


def prior_26a_safety_truth() -> dict[str, Any]:
    path = ROOT / "run/proofs/batch26a_current_repo_truth.json"
    out = {
        "exists": path.exists(),
        "orders_zero": None,
        "position_verdict": None,
        "real_live_false_or_not_found": None,
        "error": None,
    }
    if not path.exists():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        d = data.get("derived_verdicts", {})
        out["orders_zero"] = d.get("orders_zero")
        out["position_verdict"] = d.get("position_verdict")
        out["real_live_false_or_not_found"] = d.get("real_live_false_or_not_found")
    except Exception as exc:
        out["error"] = repr(exc)
    return out


def main() -> int:
    started = time.time()
    execution_text = read(EXECUTION)
    cpr_text = read(CPR)

    py_compile_results = {}
    for path in [EXECUTION, CPR]:
        try:
            py_compile.compile(str(path), doraise=True)
            py_compile_results[str(path.relative_to(ROOT))] = {"ok": True, "error": None}
        except Exception as exc:
            py_compile_results[str(path.relative_to(ROOT))] = {"ok": False, "error": repr(exc)}

    compileall = run_cmd([sys.executable, "-m", "compileall", "-q", "app/mme_scalpx/services/execution.py", "app/mme_scalpx/services/controlled_paper_runtime.py"], timeout=120)

    import_results = {}
    for mod in [
        "app.mme_scalpx.services.controlled_paper_runtime",
        "app.mme_scalpx.services.execution",
        "app.mme_scalpx.services.risk",
        "app.mme_scalpx.services.strategy",
    ]:
        try:
            importlib.import_module(mod)
            import_results[mod] = {"ok": True, "error": None}
        except Exception as exc:
            import_results[mod] = {"ok": False, "error": repr(exc)}

    cpr_call_result = {"called": False, "allowed": None, "error": None}
    helper_call_result = {"called": False, "allowed": None, "reason": None, "error": None}

    try:
        cpr = importlib.import_module("app.mme_scalpx.services.controlled_paper_runtime")
        fn = getattr(cpr, "controlled_execution_entry_allowed")
        cpr_call_result = {"called": True, "allowed": bool(fn()), "error": None}
    except Exception as exc:
        cpr_call_result = {"called": False, "allowed": None, "error": repr(exc)}

    try:
        execution = importlib.import_module("app.mme_scalpx.services.execution")
        helper = getattr(execution, "_batch26b_execution_entry_hard_arming_verdict")
        allowed, reason = helper()
        helper_call_result = {
            "called": True,
            "allowed": bool(allowed),
            "reason": str(reason),
            "error": None,
        }
    except Exception as exc:
        helper_call_result = {
            "called": False,
            "allowed": None,
            "reason": None,
            "error": repr(exc),
        }

    gs = guard_status(execution_text)
    prior_26a = prior_26a_safety_truth()
    redis_snapshot = redis_readonly_snapshot()

    derived = {
        "py_compile_ok": all(x["ok"] for x in py_compile_results.values()),
        "compileall_ok": compileall.get("returncode") == 0,
        "imports_ok": all(x["ok"] for x in import_results.values()),
        "controlled_execution_entry_allowed_present": "def controlled_execution_entry_allowed(" in cpr_text,
        "controlled_execution_entry_allowed_currently_false": cpr_call_result.get("allowed") is False,
        "execution_helper_present": "_batch26b_execution_entry_hard_arming_verdict" in execution_text,
        "execution_helper_currently_false": helper_call_result.get("allowed") is False,
        "execution_helper_reason": helper_call_result.get("reason"),
        "entry_call_count": len(actual_entry_calls(execution_text)),
        "exit_call_count": len(actual_exit_calls(execution_text)),
        "guarded_entry_call_count": len(gs["guarded_entry_calls"]),
        "unguarded_entry_call_count": len(gs["unguarded_entry_calls"]),
        "guard_near_exit_call_count": len(gs["guard_near_exit_calls"]),
        "entry_guard_fails_closed_now": helper_call_result.get("allowed") is False and helper_call_result.get("reason") == "execution_entry_not_armed",
        "exit_path_preserved_by_static_check": len(actual_exit_calls(execution_text)) >= 1 and len(gs["guard_near_exit_calls"]) == 0,
        "paper_armed_approved": False,
        "real_live_approved": False,
        "runtime_promotion_allowed": False,
        "prior_26a_orders_zero": prior_26a.get("orders_zero"),
        "prior_26a_position_verdict": prior_26a.get("position_verdict"),
        "prior_26a_real_live_false_or_not_found": prior_26a.get("real_live_false_or_not_found"),
    }

    blockers = []
    if not derived["py_compile_ok"]:
        blockers.append("PY_COMPILE_FAILED")
    if not derived["compileall_ok"]:
        blockers.append("COMPILEALL_FAILED")
    if not derived["imports_ok"]:
        blockers.append("IMPORT_FAILED")
    if not derived["controlled_execution_entry_allowed_present"]:
        blockers.append("CONTROLLED_EXECUTION_ENTRY_ALLOWED_MISSING")
    if not derived["controlled_execution_entry_allowed_currently_false"]:
        blockers.append("CONTROLLED_EXECUTION_ENTRY_ALLOWED_NOT_FALSE")
    if not derived["execution_helper_present"]:
        blockers.append("EXECUTION_HELPER_MISSING")
    if not derived["entry_guard_fails_closed_now"]:
        blockers.append("ENTRY_GUARD_DOES_NOT_FAIL_CLOSED_NOW")
    if derived["entry_call_count"] < 1:
        blockers.append("ENTRY_CALL_NOT_FOUND")
    if derived["exit_call_count"] < 1:
        blockers.append("EXIT_CALL_NOT_FOUND")
    if derived["unguarded_entry_call_count"] != 0:
        blockers.append("UNGUARDED_ENTRY_CALL_REMAINS")
    if derived["guarded_entry_call_count"] < 1:
        blockers.append("NO_GUARDED_ENTRY_CALL_FOUND")
    if derived["guard_near_exit_call_count"] != 0:
        blockers.append("ENTRY_GUARD_APPEARS_NEAR_EXIT_CALL")
    if not derived["exit_path_preserved_by_static_check"]:
        blockers.append("EXIT_PATH_NOT_PROVEN_PRESERVED")

    warnings = []
    if prior_26a.get("exists") is not True:
        warnings.append("PRIOR_26A_PROOF_NOT_FOUND_FOR_SAFETY_CONTEXT")
    if redis_snapshot.get("available") is not True:
        warnings.append("REDIS_READONLY_CHECK_SKIPPED_OR_UNAVAILABLE")

    proof = {
        "batch": "26B_execution_hard_arming_guard_thin",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "safety_posture": {
            "services_started": False,
            "redis_writes": False,
            "paper_armed_approved": False,
            "real_live_approved": False,
            "runtime_promotion_allowed": False,
            "entry_guard_fails_closed": True,
            "exit_guarded_by_this_batch": False,
        },
        "files": {
            "execution.py": {
                "path": str(EXECUTION.relative_to(ROOT)),
                "sha256": sha256(EXECUTION),
            },
            "controlled_paper_runtime.py": {
                "path": str(CPR.relative_to(ROOT)),
                "sha256": sha256(CPR),
            },
        },
        "py_compile_results": py_compile_results,
        "compileall": compileall,
        "import_results": import_results,
        "controlled_runtime_call_result": cpr_call_result,
        "execution_helper_call_result": helper_call_result,
        "static_checks": {
            "entry_calls": actual_entry_calls(execution_text),
            "exit_calls": actual_exit_calls(execution_text),
            "guarded_entry_calls": gs["guarded_entry_calls"],
            "unguarded_entry_calls": gs["unguarded_entry_calls"],
            "guard_near_exit_calls": gs["guard_near_exit_calls"],
        },
        "prior_26a_safety_truth": prior_26a,
        "redis_readonly_snapshot": redis_snapshot,
        "derived": derived,
        "final_verdict": {
            "batch26b_execution_hard_arming_guard_thin_ok": len(blockers) == 0,
            "blockers": blockers,
            "warnings": warnings,
            "paper_armed_approved": False,
            "real_live_approved": False,
            "runtime_promotion_allowed": False,
            "recommended_next_batch": "26C_strategy_leaf_required_signal_audit" if len(blockers) == 0 else "review_26b_thin_blockers",
            "elapsed_seconds": round(time.time() - started, 3),
        },
    }

    PROOF.write_text(json.dumps(proof, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    milestone = ROOT / f"docs/milestones/{datetime.now().date().isoformat()}_batch26b_execution_hard_arming_guard_thin.md"
    lines = [
        "# Batch 26B — Execution Hard Arming Guard, Thin Patch",
        "",
        f"Date: {datetime.now().date().isoformat()}",
        "",
        "## Verdict",
        "",
        f"- batch26b_execution_hard_arming_guard_thin_ok: `{proof['final_verdict']['batch26b_execution_hard_arming_guard_thin_ok']}`",
        "- paper_armed_approved: `False`",
        "- real_live_approved: `False`",
        "- runtime_promotion_allowed: `False`",
        "",
        "## Patched Files",
        "",
        "- `app/mme_scalpx/services/controlled_paper_runtime.py`",
        "- `app/mme_scalpx/services/execution.py`",
        "",
        "## Scope",
        "",
        "- Added fail-closed `controlled_execution_entry_allowed() -> False` contract if missing.",
        "- Added execution-owned `_batch26b_execution_entry_hard_arming_verdict()` helper.",
        "- Inserted direct guard before actual `self.broker.place_entry_order(...)` call.",
        "- On blocked entry, execution uses native `_fail_decision(decision, reason)` and returns.",
        "- Exit broker call path is intentionally not guarded by this entry guard.",
        "",
        "## Derived Proof",
        "",
    ]

    for k, v in derived.items():
        lines.append(f"- {k}: `{v}`")

    lines.extend(["", "## Blockers", ""])
    if blockers:
        lines.extend([f"- `{x}`" for x in blockers])
    else:
        lines.append("- none")

    lines.extend(["", "## Warnings", ""])
    if warnings:
        lines.extend([f"- `{x}`" for x in warnings])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Artifacts",
        "",
        "- `bin/patch_batch26b_execution_hard_arming_guard_thin.py`",
        "- `bin/proof_batch26b_execution_hard_arming_guard_thin.py`",
        "- `run/proofs/batch26b_execution_hard_arming_guard_thin.json`",
        "",
        "## Continuation",
        "",
        "Do not enable paper_armed.",
        "Do not enable real live.",
        "Do not start controlled paper runtime chain from this batch.",
        "",
    ])

    milestone.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(proof["final_verdict"], indent=2, sort_keys=True))
    return 0 if len(blockers) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
