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

TARGETS = {
    "MIST": "app/mme_scalpx/services/strategy_family/mist.py",
    "MISB": "app/mme_scalpx/services/strategy_family/misb.py",
    "MISC": "app/mme_scalpx/services/strategy_family/misc.py",
    "MISR": "app/mme_scalpx/services/strategy_family/misr.py",
    "MISO": "app/mme_scalpx/services/strategy_family/miso.py",
}

IMPORTS = {
    "MIST": "app.mme_scalpx.services.strategy_family.mist",
    "MISB": "app.mme_scalpx.services.strategy_family.misb",
    "MISC": "app.mme_scalpx.services.strategy_family.misc",
    "MISR": "app.mme_scalpx.services.strategy_family.misr",
    "MISO": "app.mme_scalpx.services.strategy_family.miso",
}

PROOF = ROOT / "run/proofs/proof_batch26d_strategy_leaf_required_surface_failclosed.json"
MILESTONE = ROOT / f"docs/milestones/{datetime.now().date().isoformat()}_batch26d_strategy_leaf_required_surface_failclosed.md"

HELPER_BEGIN = "# BEGIN BATCH26D_STRATEGY_LEAF_REQUIRED_COMMON_SURFACE"
HELPER_END = "# END BATCH26D_STRATEGY_LEAF_REQUIRED_COMMON_SURFACE"

UNSAFE_PROVIDER = 'return as_mapping(view.get("provider_runtime"))'
UNSAFE_SELECTED = 'selected = as_mapping(common.get("selected_option"))'


def sha(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def run_cmd(args: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": args,
            "returncode": cp.returncode,
            "stdout": cp.stdout[-6000:],
            "stderr": cp.stderr[-6000:],
        }
    except Exception as exc:
        return {"cmd": args, "returncode": None, "stdout": "", "stderr": repr(exc)}


def helper_block(text: str) -> str:
    start = text.find(HELPER_BEGIN)
    end = text.find(HELPER_END)
    if start < 0 or end < 0:
        raise RuntimeError("Batch 26D helper block missing")
    return text[start:end + len(HELPER_END)]


def helper_dynamic_test(text: str, family: str) -> dict[str, Any]:
    ns: dict[str, Any] = {}
    exec(helper_block(text), ns)
    fn = ns["_batch26d_required_common_surface"]

    cases = {}

    def call_case(name: str, container: Any, key: str, expect_raise: bool) -> None:
        try:
            value = fn(container, key, family=family, source="dynamic_test")
            cases[name] = {
                "raised": False,
                "value_repr": repr(value)[:120],
                "pass": expect_raise is False,
            }
        except Exception as exc:
            cases[name] = {
                "raised": True,
                "error": str(exc),
                "pass": expect_raise is True and "BATCH26D_REQUIRED_SURFACE_MISSING" in str(exc),
            }

    call_case("missing_provider_runtime", {}, "provider_runtime", True)
    call_case("none_provider_runtime", {"provider_runtime": None}, "provider_runtime", True)
    call_case("empty_provider_runtime", {"provider_runtime": {}}, "provider_runtime", True)
    call_case("present_provider_runtime", {"provider_runtime": {"provider_status": "OK"}}, "provider_runtime", False)

    call_case("missing_selected_option", {}, "selected_option", True)
    call_case("none_selected_option", {"selected_option": None}, "selected_option", True)
    call_case("empty_selected_option", {"selected_option": {}}, "selected_option", True)
    call_case("present_selected_option", {"selected_option": {"symbol": "NIFTY_CE"}}, "selected_option", False)

    return {
        "cases": cases,
        "all_pass": all(item["pass"] for item in cases.values()),
    }


def static_leaf_check(family: str, rel: str) -> dict[str, Any]:
    path = ROOT / rel
    text = read(path)

    return {
        "family": family,
        "path": rel,
        "sha256": sha(path),
        "helper_present": HELPER_BEGIN in text and HELPER_END in text,
        "unsafe_provider_get_present": UNSAFE_PROVIDER in text,
        "unsafe_selected_get_present": UNSAFE_SELECTED in text,
        "safe_provider_present": "_batch26d_required_common_surface(view, \"provider_runtime\"" in text,
        "safe_selected_present": "_batch26d_required_common_surface(common, \"selected_option\"" in text,
        "batch26d_error_token_present": "BATCH26D_REQUIRED_SURFACE_MISSING" in text,
        "provider_runtime_line_hits": [
            {"line": i, "text": line.rstrip()[:220]}
            for i, line in enumerate(text.splitlines(), 1)
            if "provider_runtime" in line
        ][:80],
        "selected_option_line_hits": [
            {"line": i, "text": line.rstrip()[:220]}
            for i, line in enumerate(text.splitlines(), 1)
            if "selected_option" in line
        ][:80],
    }


def main() -> int:
    started = time.time()

    py_compile_results = {}
    for family, rel in TARGETS.items():
        path = ROOT / rel
        try:
            py_compile.compile(str(path), doraise=True)
            py_compile_results[family] = {"ok": True, "error": None}
        except Exception as exc:
            py_compile_results[family] = {"ok": False, "error": repr(exc)}

    compileall = run_cmd([sys.executable, "-m", "compileall", "-q"] + list(TARGETS.values()), timeout=120)

    import_results = {}
    for family, mod in IMPORTS.items():
        try:
            importlib.import_module(mod)
            import_results[family] = {"ok": True, "error": None}
        except Exception as exc:
            import_results[family] = {"ok": False, "error": repr(exc)}

    static_checks = {}
    dynamic_checks = {}
    for family, rel in TARGETS.items():
        path = ROOT / rel
        text = read(path)
        static_checks[family] = static_leaf_check(family, rel)
        dynamic_checks[family] = helper_dynamic_test(text, family)

    derived = {
        "py_compile_ok": all(v["ok"] for v in py_compile_results.values()),
        "compileall_ok": compileall.get("returncode") == 0,
        "imports_ok": all(v["ok"] for v in import_results.values()),
        "all_helpers_present": all(v["helper_present"] for v in static_checks.values()),
        "unsafe_provider_get_removed_all": all(not v["unsafe_provider_get_present"] for v in static_checks.values()),
        "unsafe_selected_get_removed_all": all(not v["unsafe_selected_get_present"] for v in static_checks.values()),
        "safe_provider_present_all": all(v["safe_provider_present"] for v in static_checks.values()),
        "safe_selected_present_all": all(v["safe_selected_present"] for v in static_checks.values()),
        "dynamic_required_surface_tests_pass_all": all(v["all_pass"] for v in dynamic_checks.values()),
        "paper_armed_approved": False,
        "real_live_approved": False,
        "runtime_promotion_allowed": False,
    }

    blockers = []
    if not derived["py_compile_ok"]:
        blockers.append("PY_COMPILE_FAILED")
    if not derived["compileall_ok"]:
        blockers.append("COMPILEALL_FAILED")
    if not derived["imports_ok"]:
        blockers.append("IMPORT_FAILED")
    if not derived["all_helpers_present"]:
        blockers.append("HELPER_MISSING_IN_ONE_OR_MORE_LEAVES")
    if not derived["unsafe_provider_get_removed_all"]:
        blockers.append("UNSAFE_PROVIDER_RUNTIME_GET_REMAINS")
    if not derived["unsafe_selected_get_removed_all"]:
        blockers.append("UNSAFE_SELECTED_OPTION_GET_REMAINS")
    if not derived["safe_provider_present_all"]:
        blockers.append("SAFE_PROVIDER_RUNTIME_ACCESSOR_MISSING")
    if not derived["safe_selected_present_all"]:
        blockers.append("SAFE_SELECTED_OPTION_ACCESSOR_MISSING")
    if not derived["dynamic_required_surface_tests_pass_all"]:
        blockers.append("DYNAMIC_REQUIRED_SURFACE_TEST_FAILED")

    report = {
        "batch": "26D_strategy_leaf_required_surface_failclosed",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_files": TARGETS,
        "safety_posture": {
            "paper_armed_enabled_by_this_proof": False,
            "real_live_enabled_by_this_proof": False,
            "services_started_by_this_proof": False,
            "redis_writes_by_this_proof": False,
            "execution_patched_by_this_batch": False,
            "risk_patched_by_this_batch": False,
            "strategy_bridge_patched_by_this_batch": False,
        },
        "compile_checks": {
            "py_compile": py_compile_results,
            "compileall": compileall,
        },
        "import_results": import_results,
        "static_checks": static_checks,
        "dynamic_checks": dynamic_checks,
        "derived": derived,
        "final_verdict": {
            "batch26d_strategy_leaf_required_surface_failclosed_ok": len(blockers) == 0,
            "all_five_leaves_fail_closed_on_missing_required_common_surface": derived["dynamic_required_surface_tests_pass_all"],
            "blockers": blockers,
            "paper_armed_approved": False,
            "real_live_approved": False,
            "runtime_promotion_allowed": False,
            "recommended_next_batch": "26E_post_guard_consolidated_safety_proof" if len(blockers) == 0 else "review_26d_blockers",
            "elapsed_seconds": round(time.time() - started, 3),
        },
    }

    PROOF.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Batch 26D — Strategy Leaf Required Common Surface Fail-Closed",
        "",
        f"Date: {datetime.now().date().isoformat()}",
        "",
        "## Verdict",
        "",
        f"- batch26d_strategy_leaf_required_surface_failclosed_ok: `{report['final_verdict']['batch26d_strategy_leaf_required_surface_failclosed_ok']}`",
        f"- all_five_leaves_fail_closed_on_missing_required_common_surface: `{report['final_verdict']['all_five_leaves_fail_closed_on_missing_required_common_surface']}`",
        "- paper_armed_approved: `False`",
        "- real_live_approved: `False`",
        "- runtime_promotion_allowed: `False`",
        "",
        "## Patched Files",
        "",
    ]

    for rel in TARGETS.values():
        lines.append(f"- `{rel}`")

    lines.extend([
        "",
        "## Scope",
        "",
        "- Replaced unsafe `view.get(\"provider_runtime\")` common-surface read with fail-closed required accessor.",
        "- Replaced unsafe `common.get(\"selected_option\")` common-surface read with fail-closed required accessor.",
        "- Added local Batch 26D helper to each family leaf.",
        "- Did not patch strategy bridge, risk, execution, features, names, models, or configs.",
        "",
        "## Derived Proof",
        "",
    ])

    for k, v in derived.items():
        lines.append(f"- {k}: `{v}`")

    lines.extend(["", "## Blockers", ""])
    if blockers:
        lines.extend([f"- `{x}`" for x in blockers])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Artifacts",
        "",
        "- `bin/patch_batch26d_strategy_leaf_required_surface_failclosed.py`",
        "- `bin/proof_batch26d_strategy_leaf_required_surface_failclosed.py`",
        "- `run/proofs/proof_batch26d_strategy_leaf_required_surface_failclosed.json`",
        "- `run/proofs/proof_batch26d_strategy_leaf_required_surface_failclosed_patch_step.json`",
        "",
        "## Continuation",
        "",
        "Do not enable paper_armed.",
        "Do not enable real live.",
        "Do not start controlled paper runtime chain from this batch.",
        "",
    ])

    MILESTONE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report["final_verdict"], indent=2, sort_keys=True))
    return 0 if len(blockers) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
