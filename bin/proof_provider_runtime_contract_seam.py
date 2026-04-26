#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import features as F
from app.mme_scalpx.services.feature_family import contracts as C


class StubRedis:
    def __init__(self, hashes: dict[str, dict[str, Any]] | None = None):
        self.hashes = hashes or {}

    def hgetall(self, key: str) -> dict[str, Any]:
        return dict(self.hashes.get(key, {}))


def _status(name: str, fallback: str) -> str:
    return getattr(N, name, fallback)


def _canonical_raw() -> dict[str, Any]:
    return {
        "futures_marketdata_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "selected_option_marketdata_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "option_context_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "execution_primary_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "execution_fallback_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "futures_marketdata_status": _status("PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "selected_option_marketdata_status": _status("PROVIDER_STATUS_STALE", "STALE"),
        "option_context_status": _status("PROVIDER_STATUS_DEGRADED", "DEGRADED"),
        "execution_primary_status": _status("PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "execution_fallback_status": _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE"),
        "family_runtime_mode": getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
        "failover_mode": getattr(N, "PROVIDER_FAILOVER_MODE_MANUAL", "MANUAL"),
        "override_mode": getattr(N, "PROVIDER_OVERRIDE_MODE_AUTO", "AUTO"),
        "transition_reason": getattr(N, "PROVIDER_TRANSITION_REASON_BOOTSTRAP", "BOOTSTRAP"),
        "provider_transition_seq": 25,
        "failover_active": False,
        "pending_failover": False,
    }


def _compat_raw() -> dict[str, Any]:
    return {
        "active_futures_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "active_selected_option_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "active_option_context_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "active_execution_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "fallback_execution_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "futures_provider_status": _status("PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "selected_option_provider_status": _status("PROVIDER_STATUS_STALE", "STALE"),
        "option_context_provider_status": _status("PROVIDER_STATUS_DEGRADED", "DEGRADED"),
        "execution_provider_status": _status("PROVIDER_STATUS_HEALTHY", "HEALTHY"),
        "execution_fallback_provider_status": _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE"),
        "family_runtime_mode": getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
        "failover_mode": getattr(N, "PROVIDER_FAILOVER_MODE_MANUAL", "MANUAL"),
        "override_mode": getattr(N, "PROVIDER_OVERRIDE_MODE_AUTO", "AUTO"),
        "transition_reason": getattr(N, "PROVIDER_TRANSITION_REASON_BOOTSTRAP", "BOOTSTRAP"),
        "provider_transition_seq": 26,
        "failover_active": False,
        "pending_failover": False,
    }


def main() -> int:
    generated_at_ns = time.time_ns()
    errors: list[str] = []
    checks: dict[str, bool] = {}

    proof25g_path = Path("run/proofs/proof_contract_field_registry.json")
    if not proof25g_path.exists():
        raise SystemExit("Missing Batch 25G proof; refusing Batch 25H-C proof")

    proof25g = json.loads(proof25g_path.read_text(encoding="utf-8"))
    if not proof25g.get("contract_field_registry_ok"):
        raise SystemExit("Batch 25G proof is not true; refusing Batch 25H-C proof")

    engine = F.FeatureEngine(redis_client=StubRedis())

    canonical_runtime = engine._provider_runtime(_canonical_raw())
    compat_runtime = engine._provider_runtime(_compat_raw())
    missing_runtime = engine._provider_runtime({})
    contract_provider = engine._contract_provider(canonical_runtime, {})
    empty_contract_block = C.build_empty_provider_runtime_block()

    payload = C.build_empty_family_features_payload()
    payload["provider_runtime"] = contract_provider

    try:
        C.validate_provider_runtime_block(empty_contract_block)
        C.validate_provider_runtime_block(contract_provider)
        C.validate_family_features_payload(payload)
        checks["feature_family_contract_validation_ok"] = True
    except Exception as exc:
        checks["feature_family_contract_validation_ok"] = False
        errors.append(f"contract_validation_failed: {exc}")

    checks["provider_runtime_contract_keys_include_canonical"] = all(
        key in C.PROVIDER_RUNTIME_KEYS for key in N.CONTRACT_PROVIDER_RUNTIME_KEYS
    )

    checks["provider_runtime_contract_keys_include_compatibility"] = all(
        key in C.PROVIDER_RUNTIME_KEYS
        for key in (
            "active_futures_provider_id",
            "active_selected_option_provider_id",
            "active_option_context_provider_id",
            "active_execution_provider_id",
            "fallback_execution_provider_id",
            "futures_provider_status",
            "selected_option_provider_status",
            "option_context_provider_status",
            "execution_provider_status",
        )
    )

    checks["canonical_keys_present_in_runtime"] = all(
        key in canonical_runtime for key in N.CONTRACT_PROVIDER_RUNTIME_KEYS
    )

    checks["canonical_keys_present_in_contract_provider"] = all(
        key in contract_provider for key in N.CONTRACT_PROVIDER_RUNTIME_KEYS
    )

    checks["canonical_keys_present_in_empty_contract_block"] = all(
        key in empty_contract_block for key in N.CONTRACT_PROVIDER_RUNTIME_KEYS
    )

    checks["canonical_to_compat_aliases_derived"] = (
        canonical_runtime.get("active_futures_provider_id")
        == canonical_runtime.get("futures_marketdata_provider_id")
        and canonical_runtime.get("active_selected_option_provider_id")
        == canonical_runtime.get("selected_option_marketdata_provider_id")
        and canonical_runtime.get("active_option_context_provider_id")
        == canonical_runtime.get("option_context_provider_id")
        and canonical_runtime.get("active_execution_provider_id")
        == canonical_runtime.get("execution_primary_provider_id")
        and canonical_runtime.get("fallback_execution_provider_id")
        == canonical_runtime.get("execution_fallback_provider_id")
        and canonical_runtime.get("futures_provider_status")
        == canonical_runtime.get("futures_marketdata_status")
        and canonical_runtime.get("selected_option_provider_status")
        == canonical_runtime.get("selected_option_marketdata_status")
        and canonical_runtime.get("option_context_provider_status")
        == canonical_runtime.get("option_context_status")
        and canonical_runtime.get("execution_provider_status")
        == canonical_runtime.get("execution_primary_status")
    )

    checks["compat_to_canonical_aliases_accepted"] = (
        compat_runtime.get("futures_marketdata_provider_id")
        == compat_runtime.get("active_futures_provider_id")
        and compat_runtime.get("selected_option_marketdata_provider_id")
        == compat_runtime.get("active_selected_option_provider_id")
        and compat_runtime.get("option_context_provider_id")
        == compat_runtime.get("active_option_context_provider_id")
        and compat_runtime.get("execution_primary_provider_id")
        == compat_runtime.get("active_execution_provider_id")
        and compat_runtime.get("execution_fallback_provider_id")
        == compat_runtime.get("fallback_execution_provider_id")
    )

    checks["status_values_preserved_not_collapsed"] = (
        canonical_runtime.get("selected_option_marketdata_status")
        == _status("PROVIDER_STATUS_STALE", "STALE")
        and canonical_runtime.get("option_context_status")
        == _status("PROVIDER_STATUS_DEGRADED", "DEGRADED")
        and canonical_runtime.get("execution_fallback_status")
        == _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
    )

    checks["missing_required_signals_become_blocker"] = (
        missing_runtime.get("provider_runtime_blocked") is True
        and bool(missing_runtime.get("provider_runtime_missing_keys"))
        and "missing_required_provider_runtime_keys" in str(missing_runtime.get("provider_runtime_block_reason"))
    )

    checks["no_silent_provider_id_default_on_missing_raw"] = (
        missing_runtime.get("futures_marketdata_provider_id") in (None, "")
        and missing_runtime.get("selected_option_marketdata_provider_id") in (None, "")
        and missing_runtime.get("option_context_provider_id") in (None, "")
        and missing_runtime.get("execution_primary_provider_id") in (None, "")
    )

    checks["missing_statuses_are_unavailable"] = (
        missing_runtime.get("futures_marketdata_status") == _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
        and missing_runtime.get("selected_option_marketdata_status") == _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
        and missing_runtime.get("option_context_status") == _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
        and missing_runtime.get("execution_primary_status") == _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
        and missing_runtime.get("execution_fallback_status") == _status("PROVIDER_STATUS_UNAVAILABLE", "UNAVAILABLE")
    )

    checks["observe_only_remains_default"] = (
        canonical_runtime.get("family_runtime_mode")
        == getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only")
        and contract_provider.get("family_runtime_mode")
        == getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only")
    )

    checks["no_provider_failover_performed"] = (
        canonical_runtime.get("failover_active") is False
        and canonical_runtime.get("pending_failover") is False
    )

    proof_ok = all(checks.values()) and not errors

    proof = {
        "proof_name": "proof_provider_runtime_contract_seam",
        "batch": "25H-C",
        "generated_at_ns": generated_at_ns,
        "provider_runtime_contract_seam_ok": proof_ok,
        "checks": checks,
        "errors": errors,
        "inputs": {
            "canonical_raw": _canonical_raw(),
            "compat_raw": _compat_raw(),
            "missing_raw": {},
        },
        "observed": {
            "provider_runtime_keys": tuple(C.PROVIDER_RUNTIME_KEYS),
            "canonical_runtime": canonical_runtime,
            "compat_runtime": compat_runtime,
            "missing_runtime": missing_runtime,
            "contract_provider": contract_provider,
            "empty_contract_block": empty_contract_block,
        },
    }

    out = Path("run/proofs/proof_provider_runtime_contract_seam.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "provider_runtime_contract_seam_ok": proof_ok,
        "failed_checks": {
            key: value for key, value in checks.items() if value is not True
        },
        "errors": errors,
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
