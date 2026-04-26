#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml

SECRET_PATTERNS = re.compile(
    r"(access_token|refresh_token|client_secret|api_secret|api_key|authorization|bearer\s+|password|passwd|pin|totp|jwt|enctoken)",
    re.IGNORECASE,
)

CONFIG_FILES = (
    "etc/brokers/runtime.yaml",
    "etc/brokers/provider_roles.yaml",
    "etc/brokers/dhan.yaml",
    "etc/brokers/zerodha.yaml",
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/rollout/observe_only.yaml",
    "etc/strategy_family/rollout/legacy_live_family_shadow.yaml",
    "etc/strategy_family/rollout/family_live_legacy_shadow.yaml",
    "etc/strategy_family/rollout/family_live_only.yaml",
)


def load_yaml(path_s: str) -> dict[str, Any]:
    path = Path(path_s)
    if not path.exists():
        raise SystemExit(f"Missing required config: {path_s}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be YAML mapping: {path_s}")
    return data


def upper_text(value: Any) -> str:
    return str(value or "").strip().upper()


def no_secrets_in_files(paths: tuple[str, ...]) -> tuple[bool, list[str]]:
    hits = []
    for path_s in paths:
        path = Path(path_s)
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and SECRET_PATTERNS.search(stripped):
                hits.append(f"{path_s}:{lineno}:{stripped[:120]}")
    return (not hits, hits)


def main() -> int:
    generated_at_ns = time.time_ns()
    errors: list[str] = []
    checks: dict[str, bool] = {}

    runtime = load_yaml("etc/brokers/runtime.yaml")
    roles = load_yaml("etc/brokers/provider_roles.yaml")
    dhan = load_yaml("etc/brokers/dhan.yaml")
    zerodha = load_yaml("etc/brokers/zerodha.yaml")
    family_runtime = load_yaml("etc/strategy_family/family_runtime.yaml")
    rollout_observe = load_yaml("etc/strategy_family/rollout/observe_only.yaml")
    rollout_legacy_shadow = load_yaml("etc/strategy_family/rollout/legacy_live_family_shadow.yaml")
    rollout_family_shadow = load_yaml("etc/strategy_family/rollout/family_live_legacy_shadow.yaml")
    rollout_family_live_only = load_yaml("etc/strategy_family/rollout/family_live_only.yaml")

    runtime_block = runtime.get("provider_runtime") or {}
    operating_defaults = runtime.get("operating_defaults") or {}
    roles_block = roles.get("provider_roles") or {}
    miso_alignment = roles.get("miso_provider_doctrine_alignment") or {}
    dhan_depth = dhan.get("depth_policy") or {}

    checks["rollout_observe_only_default"] = (
        family_runtime.get("default_runtime_mode") == "observe_only"
        and (family_runtime.get("rollout") or {}).get("default") == "observe_only"
        and rollout_observe.get("default") is True
        and rollout_observe.get("rollout_mode") == "observe_only"
        and rollout_observe.get("family_order_intent_publish") is False
        and rollout_observe.get("broker_orders_allowed") is False
    )

    checks["strategy_promotion_and_execution_arming_disabled"] = (
        (family_runtime.get("order_intent_adapter") or {}).get("publication_enabled") is False
        and (family_runtime.get("order_intent_adapter") or {}).get("enabled") is False
        and (family_runtime.get("rollout") or {}).get("promotion_enabled") is False
        and (family_runtime.get("rollout") or {}).get("execution_arming_enabled") is False
        and rollout_legacy_shadow.get("family_order_intent_publish") is False
        and rollout_family_shadow.get("family_order_intent_publish") is False
        and rollout_family_live_only.get("family_order_intent_publish") is False
        and rollout_family_live_only.get("forbidden_until_full_readiness_milestone") is True
    )

    checks["runtime_provider_laws_present"] = (
        runtime_block.get("enabled") is True
        and runtime_block.get("family_runtime_mode") == "observe_only"
        and upper_text(runtime_block.get("failover_mode")) == "MANUAL"
        and runtime_block.get("require_flat_for_role_switch") is True
        and runtime_block.get("invalidate_preposition_setup_on_switch") is True
        and runtime_block.get("prohibit_silent_provider_switch") is True
        and runtime_block.get("prohibit_mid_position_provider_migration") is True
    )

    checks["provider_doctrine_alignment_ok"] = (
        (roles_block.get("futures_marketdata") or {}).get("preferred_provider") == "ZERODHA"
        and (roles_block.get("selected_option_marketdata") or {}).get("preferred_provider") == "DHAN"
        and (roles_block.get("option_context") or {}).get("preferred_provider") == "DHAN"
        and (roles_block.get("execution_primary") or {}).get("preferred_provider") == "ZERODHA"
        and (roles_block.get("execution_fallback") or {}).get("preferred_provider") == "DHAN"
        and miso_alignment.get("selected_option_provider_required") == "DHAN"
        and miso_alignment.get("option_context_provider_required") == "DHAN"
        and "ZERODHA" in (miso_alignment.get("futures_providers_allowed_when_healthy_and_synced") or [])
        and "DHAN" in (miso_alignment.get("futures_providers_allowed_when_healthy_and_synced") or [])
        and miso_alignment.get("dhan_futures_required_only_in_explicit_future_rollout_mode") is True
        and operating_defaults.get("futures_marketdata_preferred_provider") == "ZERODHA"
        and operating_defaults.get("selected_option_marketdata_preferred_provider") == "DHAN"
        and operating_defaults.get("option_context_preferred_provider") == "DHAN"
        and operating_defaults.get("execution_primary_provider") == "ZERODHA"
        and operating_defaults.get("execution_fallback_provider") == "DHAN"
    )

    checks["dhan_top20_honest_reporting_ok"] = (
        dhan_depth.get("configured_target") == "TOP20_ENHANCED"
        and dhan_depth.get("must_not_report_top20_without_runtime_activation_proof") is True
        and dhan_depth.get("runtime_active_mode") in {"FULL_TOP5_BASE", "DEGRADED_TOP5_OR_UNAVAILABLE", "TOP20_ENHANCED"}
        and not (
            dhan_depth.get("runtime_active_mode") == "TOP20_ENHANCED"
            and not dhan_depth.get("runtime_top20_activation_proof")
        )
    )

    checks["provider_role_files_aligned"] = (
        (dhan.get("provider_roles") or {}).get("selected_option_marketdata") is True
        and (dhan.get("provider_roles") or {}).get("option_context") is True
        and (zerodha.get("provider_roles") or {}).get("futures_marketdata") is True
        and (zerodha.get("provider_roles") or {}).get("execution_primary") is True
    )

    no_secret_values, secret_hits = no_secrets_in_files(CONFIG_FILES)
    checks["no_secret_values_in_configs"] = no_secret_values
    if secret_hits:
        errors.extend(f"secret_like_config_value:{hit}" for hit in secret_hits)

    proof_ok = all(checks.values()) and not errors

    proof = {
        "proof_name": "proof_runtime_config_alignment",
        "batch": "25S",
        "generated_at_ns": generated_at_ns,
        "runtime_config_alignment_ok": proof_ok,
        "rollout_observe_only_default": checks["rollout_observe_only_default"],
        "provider_doctrine_alignment_ok": checks["provider_doctrine_alignment_ok"],
        "no_secret_values_in_configs": checks["no_secret_values_in_configs"],
        "checks": checks,
        "errors": errors,
        "config_files_checked": CONFIG_FILES,
        "observed": {
            "runtime_provider_runtime": runtime_block,
            "runtime_operating_defaults": operating_defaults,
            "provider_roles": roles_block,
            "miso_provider_doctrine_alignment": miso_alignment,
            "dhan_depth_policy": dhan_depth,
            "family_runtime_rollout": family_runtime.get("rollout"),
        },
    }

    out = Path("run/proofs/proof_runtime_config_alignment.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "runtime_config_alignment_ok": proof_ok,
        "rollout_observe_only_default": checks["rollout_observe_only_default"],
        "provider_doctrine_alignment_ok": checks["provider_doctrine_alignment_ok"],
        "dhan_top20_honest_reporting_ok": checks["dhan_top20_honest_reporting_ok"],
        "no_secret_values_in_configs": checks["no_secret_values_in_configs"],
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
