#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = ROOT / "run" / "proofs" / "integrations_batch5_freeze.json"

def rel(path: str) -> Path:
    return ROOT / path

def read(path: str) -> str:
    return rel(path).read_text(encoding="utf-8")

def assert_true(name: str, condition: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {
        "name": name,
        "ok": bool(condition),
        "details": details or {},
    }
    if not condition:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row

def main() -> int:
    sys.path.insert(0, str(ROOT))

    from app.mme_scalpx.core import names
    from app.mme_scalpx.integrations import provider_runtime
    from app.mme_scalpx.integrations import broker_api
    from app.mme_scalpx.integrations import bootstrap_provider
    from app.mme_scalpx.integrations import feed_adapter
    from app.mme_scalpx.integrations import dhan_execution

    results: list[dict[str, Any]] = []

    provider_src = read("app/mme_scalpx/integrations/provider_runtime.py")
    broker_src = read("app/mme_scalpx/integrations/broker_api.py")
    bootstrap_src = read("app/mme_scalpx/integrations/bootstrap_provider.py")
    feed_src = read("app/mme_scalpx/integrations/feed_adapter.py")
    dhan_exec_src = read("app/mme_scalpx/integrations/dhan_execution.py")

    results.append(assert_true(
        "provider_runtime_has_strict_dhan_context_no_state_unavailable",
        "Dhan provider-level health is not option-chain/context health" in provider_src
        and "if dhan_context_state is None:" in provider_src
        and "return names.PROVIDER_STATUS_UNAVAILABLE" in provider_src,
    ))

    results.append(assert_true(
        "provider_runtime_has_dhan_execution_fallback_disabled_by_default",
        "enable_dhan_execution_fallback: bool = False" in provider_src
        and "Dhan execution fallback disabled until concrete Dhan execution transport" in provider_src
        and "execution_fallback_status = names.PROVIDER_STATUS_DISABLED" in provider_src,
    ))

    results.append(assert_true(
        "broker_api_validates_payload_before_transport",
        broker_src.index("payload = self._build_order_payload(")
        < broker_src.index("transport = self._require_transport()", broker_src.index("def _place_order_common")),
    ))

    results.append(assert_true(
        "bootstrap_provider_reports_provider_bootstrap_truth",
        "provider_bootstrap_report" in bootstrap_src
        and "dhan_context_first_poll_required" in bootstrap_src
        and "dhan_execution_fallback_status" in bootstrap_src,
    ))

    results.append(assert_true(
        "bootstrap_provider_uses_names_provider_constants",
        'PROVIDER_ZERODHA = getattr(names, "PROVIDER_ZERODHA", "ZERODHA")' in bootstrap_src
        and 'PROVIDER_DHAN = getattr(names, "PROVIDER_DHAN", "DHAN")' in bootstrap_src,
    ))

    results.append(assert_true(
        "feed_adapter_uses_names_provider_constant",
        '"provider": names.PROVIDER_ZERODHA' in feed_src,
    ))

    results.append(assert_true(
        "dhan_execution_is_explicitly_disabled_not_empty",
        "DisabledDhanExecutionTransport" in dhan_exec_src
        and "execution_supported" in dhan_exec_src
        and "False" in dhan_exec_src
        and len(dhan_exec_src.strip()) > 500,
    ))

    healthy = SimpleNamespace(
        status=names.PROVIDER_STATUS_HEALTHY,
        authenticated=True,
        stale=False,
        marketdata_healthy=True,
        execution_healthy=True,
    )
    stale = SimpleNamespace(
        status=names.PROVIDER_STATUS_HEALTHY,
        authenticated=True,
        stale=True,
        marketdata_healthy=True,
        execution_healthy=True,
    )
    auth_failed = SimpleNamespace(
        status=names.PROVIDER_STATUS_HEALTHY,
        authenticated=False,
        stale=False,
        marketdata_healthy=True,
        execution_healthy=True,
    )

    status_no_ctx = provider_runtime._determine_provider_status(
        provider_id=names.PROVIDER_DHAN,
        role=names.PROVIDER_ROLE_OPTION_CONTEXT,
        provider_health_map={names.PROVIDER_DHAN: healthy},
        dhan_context_state=None,
    )
    results.append(assert_true(
        "dynamic_dhan_context_no_state_is_unavailable",
        status_no_ctx == names.PROVIDER_STATUS_UNAVAILABLE,
        {"actual": status_no_ctx},
    ))

    status_ctx_healthy = provider_runtime._determine_provider_status(
        provider_id=names.PROVIDER_DHAN,
        role=names.PROVIDER_ROLE_OPTION_CONTEXT,
        provider_health_map={names.PROVIDER_DHAN: healthy},
        dhan_context_state=SimpleNamespace(context_status=names.PROVIDER_STATUS_HEALTHY),
    )
    results.append(assert_true(
        "dynamic_dhan_context_state_healthy_passes",
        status_ctx_healthy == names.PROVIDER_STATUS_HEALTHY,
        {"actual": status_ctx_healthy},
    ))

    status_ctx_stale = provider_runtime._determine_provider_status(
        provider_id=names.PROVIDER_DHAN,
        role=names.PROVIDER_ROLE_OPTION_CONTEXT,
        provider_health_map={names.PROVIDER_DHAN: healthy},
        dhan_context_state=SimpleNamespace(context_status=names.PROVIDER_STATUS_STALE),
    )
    results.append(assert_true(
        "dynamic_dhan_context_state_stale_passes_stale",
        status_ctx_stale == names.PROVIDER_STATUS_STALE,
        {"actual": status_ctx_stale},
    ))

    status_ctx_auth_failed = provider_runtime._determine_provider_status(
        provider_id=names.PROVIDER_DHAN,
        role=names.PROVIDER_ROLE_OPTION_CONTEXT,
        provider_health_map={names.PROVIDER_DHAN: healthy},
        dhan_context_state=SimpleNamespace(context_status=names.PROVIDER_STATUS_AUTH_FAILED),
    )
    results.append(assert_true(
        "dynamic_dhan_context_state_auth_failed_passes_auth_failed",
        status_ctx_auth_failed == names.PROVIDER_STATUS_AUTH_FAILED,
        {"actual": status_ctx_auth_failed},
    ))

    status_generic_auth_failed = provider_runtime._determine_provider_status(
        provider_id=names.PROVIDER_DHAN,
        role=names.PROVIDER_ROLE_OPTION_CONTEXT,
        provider_health_map={names.PROVIDER_DHAN: auth_failed},
        dhan_context_state=SimpleNamespace(context_status=names.PROVIDER_STATUS_HEALTHY),
    )
    results.append(assert_true(
        "dynamic_dhan_context_generic_auth_failed_blocks_context",
        status_generic_auth_failed == names.PROVIDER_STATUS_AUTH_FAILED,
        {"actual": status_generic_auth_failed},
    ))

    status_generic_stale = provider_runtime._determine_provider_status(
        provider_id=names.PROVIDER_DHAN,
        role=names.PROVIDER_ROLE_OPTION_CONTEXT,
        provider_health_map={names.PROVIDER_DHAN: stale},
        dhan_context_state=SimpleNamespace(context_status=names.PROVIDER_STATUS_HEALTHY),
    )
    results.append(assert_true(
        "dynamic_dhan_context_generic_stale_blocks_context",
        status_generic_stale == names.PROVIDER_STATUS_STALE,
        {"actual": status_generic_stale},
    ))

    adapter = broker_api.ZerodhaBrokerAdapter(transport_client=None, requires_auth=False)

    try:
        adapter.place_entry_order(
            tradingsymbol="NIFTYTEST",
            exchange="NFO",
            transaction_type="BUY",
            quantity=0,
            product="NRML",
            order_type="MARKET",
        )
        malformed_result = "no_exception"
    except broker_api.BrokerAdapterValidationError:
        malformed_result = "validation_error"
    except broker_api.BrokerAdapterUnavailableError:
        malformed_result = "transport_error"

    results.append(assert_true(
        "broker_api_malformed_order_fails_validation_before_transport",
        malformed_result == "validation_error",
        {"actual": malformed_result},
    ))

    try:
        adapter.place_entry_order(
            tradingsymbol="NIFTYTEST",
            exchange="NFO",
            transaction_type="BUY",
            quantity=1,
            product="NRML",
            order_type="MARKET",
        )
        valid_no_transport_result = "no_exception"
    except broker_api.BrokerAdapterUnavailableError:
        valid_no_transport_result = "transport_error"

    results.append(assert_true(
        "broker_api_valid_order_without_transport_fails_unavailable",
        valid_no_transport_result == "transport_error",
        {"actual": valid_no_transport_result},
    ))

    disabled_transport = dhan_execution.build_disabled_dhan_execution_transport()
    health = disabled_transport.healthcheck()
    results.append(assert_true(
        "dhan_execution_disabled_transport_health_is_disabled",
        health.get("status") == names.PROVIDER_STATUS_DISABLED
        and health.get("execution_supported") is False
        and health.get("transport_configured") is False,
        health,
    ))

    try:
        disabled_transport.place_order({"symbol": "NIFTYTEST"})
        dhan_order_result = "no_exception"
    except dhan_execution.DhanExecutionUnavailableError:
        dhan_order_result = "disabled_error"

    results.append(assert_true(
        "dhan_execution_disabled_transport_rejects_order",
        dhan_order_result == "disabled_error",
        {"actual": dhan_order_result},
    ))

    callable_transport = broker_api.CallableBrokerTransportClient(
        place_order_fn=lambda payload, **kwargs: {
            "ok": True,
            "order_id": "TEST123",
            "payload_seen": dict(payload),
        }
    )
    live_adapter = broker_api.ZerodhaBrokerAdapter(
        transport_client=callable_transport,
        requires_auth=False,
    )
    response = live_adapter.place_entry_order(
        tradingsymbol="NIFTYTEST",
        exchange="NFO",
        transaction_type="BUY",
        quantity=1,
        product="NRML",
        order_type="MARKET",
    )
    results.append(assert_true(
        "broker_api_positive_callable_transport_order_passes",
        response.get("ok") is True
        and response.get("order_id") == "TEST123"
        and response.get("request", {}).get("quantity") == 1,
        response,
    ))

    proof = {
        "proof_name": "integrations_batch5_freeze",
        "status": "PASS",
        "ts_epoch": time.time(),
        "cases": results,
        "summary": {
            "case_count": len(results),
            "provider_context_false_health_closed": True,
            "dhan_execution_fallback_disabled_until_proven": True,
            "broker_validation_before_transport": True,
            "bootstrap_truth_report_present": True,
        },
    }

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(proof["summary"], indent=2, sort_keys=True))
    print(f"proof_artifact={PROOF_PATH}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
