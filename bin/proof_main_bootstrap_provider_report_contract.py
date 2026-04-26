#!/usr/bin/env python3
from __future__ import annotations

import importlib
import inspect
import json
import os
import py_compile
import sys
import types
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MAIN_PATH = PROJECT_ROOT / "app" / "mme_scalpx" / "main.py"
PROVIDER_PATH = PROJECT_ROOT / "app" / "mme_scalpx" / "integrations" / "bootstrap_provider.py"
PROOF_PATH = PROJECT_ROOT / "run" / "proofs" / "proof_main_bootstrap_provider_report_contract.json"

proof: dict[str, Any] = {
    "proof_name": "proof_main_bootstrap_provider_report_contract",
    "batch": "26A",
    "status": "FAIL",
    "checks": {},
    "details": {},
    "errors": [],
    "safety": {
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_changed": False,
        "redis_names_changed": False,
        "strategy_logic_changed": False,
        "systemd_changed": False,
    },
}

def check(name: str, ok: bool, detail: Any = None) -> None:
    proof["checks"][name] = bool(ok)
    if detail is not None:
        proof["details"][name] = detail

def add_error(label: str, exc: BaseException) -> None:
    proof["errors"].append({
        "label": label,
        "type": type(exc).__name__,
        "error": str(exc),
    })

def compile_file(path: Path, label: str) -> None:
    try:
        py_compile.compile(str(path), doraise=True)
        check(f"{label}_compile_ok", True)
    except BaseException as exc:
        check(f"{label}_compile_ok", False)
        add_error(f"{label}_compile", exc)

compile_file(MAIN_PATH, "main_py")
compile_file(PROVIDER_PATH, "bootstrap_provider_py")

main_src = MAIN_PATH.read_text(encoding="utf-8")
provider_src = PROVIDER_PATH.read_text(encoding="utf-8")

static_checks = {
    "provider_mentions_report": "provider_bootstrap_report" in provider_src,
    "main_has_report_field": "provider_bootstrap_report: Mapping[str, Any] | None = None" in main_src,
    "main_has_report_safe_dict_flag": '"provider_bootstrap_report_registered": isinstance(self.provider_bootstrap_report, Mapping),' in main_src,
    "main_register_accepts_report": "provider_bootstrap_report: Mapping[str, Any] | None = None,\n) -> None:" in main_src,
    "main_validates_report_mapping": "provider_bootstrap_report must be a mapping when provided" in main_src,
    "main_stores_report": "provider_bootstrap_report=normalized_provider_bootstrap_report" in main_src,
    "main_allowlist_accepts_report": '"provider_bootstrap_report",' in main_src,
    "main_passes_returned_report": 'provider_bootstrap_report=result.get("provider_bootstrap_report")' in main_src,
    "no_full_main_payload_pattern": "main.py.gz.b64" not in main_src,
}
for name, ok in static_checks.items():
    check(name, ok)

try:
    os.environ.pop("MME_BOOTSTRAP_PROVIDER", None)
    M = importlib.import_module("app.mme_scalpx.main")
    check("main_import_ok", True)

    sig = inspect.signature(M.register_bootstrap_dependencies)
    check("runtime_signature_accepts_report", "provider_bootstrap_report" in sig.parameters, list(sig.parameters))

    sentinel_report = {
        "version": "proof",
        "provider_runtime_status": "DEGRADED",
        "dhan_context_bootstrap_status": "DEGRADED",
        "dhan_execution_fallback_status": "DISABLED",
    }

    good_mod = types.ModuleType("_scalpx_proof_good_bootstrap_provider")

    def good_provide() -> dict[str, Any]:
        return {"provider_bootstrap_report": sentinel_report}

    good_mod.provide = good_provide
    sys.modules[good_mod.__name__] = good_mod

    M.clear_bootstrap_dependencies()
    M.maybe_register_bootstrap_dependencies(provider_ref=f"{good_mod.__name__}:provide")
    deps = M.get_bootstrap_dependencies()

    check(
        "returned_provider_report_registered",
        getattr(deps, "provider_bootstrap_report", None) == sentinel_report,
        getattr(deps, "provider_bootstrap_report", None),
    )

    safe_dict = deps.to_safe_dict()
    check(
        "safe_dict_exposes_presence_not_payload",
        safe_dict.get("provider_bootstrap_report_registered") is True
        and "version" not in safe_dict
        and "provider_runtime_status" not in safe_dict,
        safe_dict,
    )

    unknown_mod = types.ModuleType("_scalpx_proof_unknown_key_bootstrap_provider")

    def unknown_provide() -> dict[str, Any]:
        return {"unknown_key": True}

    unknown_mod.provide = unknown_provide
    sys.modules[unknown_mod.__name__] = unknown_mod

    unknown_rejected = False
    try:
        M.maybe_register_bootstrap_dependencies(provider_ref=f"{unknown_mod.__name__}:provide")
    except M.BootstrapError:
        unknown_rejected = True
    check("unknown_keys_still_rejected", unknown_rejected)

    bad_report_mod = types.ModuleType("_scalpx_proof_bad_report_bootstrap_provider")

    def bad_report_provide() -> dict[str, Any]:
        return {"provider_bootstrap_report": "not-a-mapping"}

    bad_report_mod.provide = bad_report_provide
    sys.modules[bad_report_mod.__name__] = bad_report_mod

    bad_report_rejected = False
    try:
        M.maybe_register_bootstrap_dependencies(provider_ref=f"{bad_report_mod.__name__}:provide")
    except M.BootstrapError:
        bad_report_rejected = True
    check("non_mapping_report_rejected", bad_report_rejected)

    M.clear_bootstrap_dependencies()

except BaseException as exc:
    check("dynamic_contract_checks_ok", False)
    add_error("dynamic_contract_checks", exc)

all_ok = all(proof["checks"].values()) and not proof["errors"]
proof["main_bootstrap_provider_report_contract_ok"] = all_ok
proof["status"] = "PASS" if all_ok else "FAIL"
proof["final_verdict"] = (
    "PASS_MAIN_BOOTSTRAP_PROVIDER_REPORT_CONTRACT"
    if all_ok
    else "FAIL_MAIN_BOOTSTRAP_PROVIDER_REPORT_CONTRACT"
)

PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
print(json.dumps(proof, indent=2, sort_keys=True))
raise SystemExit(0 if all_ok else 1)
