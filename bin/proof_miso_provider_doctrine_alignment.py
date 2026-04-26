#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family import doctrine_contracts as D
from app.mme_scalpx.services.strategy_family import miso


def _healthy_provider_runtime(
    *,
    futures_provider: str,
    selected_provider: str,
    context_provider: str,
    futures_status: str,
    selected_status: str,
    context_status: str,
    dhan_futures_rollout: bool = False,
) -> dict[str, Any]:
    return {
        "futures_marketdata_provider_id": futures_provider,
        "active_futures_provider_id": futures_provider,
        "selected_option_marketdata_provider_id": selected_provider,
        "active_selected_option_provider_id": selected_provider,
        "option_context_provider_id": context_provider,
        "active_option_context_provider_id": context_provider,
        "futures_marketdata_status": futures_status,
        "futures_provider_status": futures_status,
        "selected_option_marketdata_status": selected_status,
        "selected_option_provider_status": selected_status,
        "option_context_status": context_status,
        "option_context_provider_status": context_status,
        "cross_provider_sync_ok": True,
        "miso_dhan_futures_rollout_enabled": dhan_futures_rollout,
    }


def _view(provider_runtime: dict[str, Any], *, stage_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    stage = {
        "data_valid": True,
        "data_quality_ok": True,
        "session_eligible": True,
        "warmup_complete": True,
        "provider_ready_miso": True,
        "dhan_context_fresh": True,
        "selected_option_marketdata_fresh": True,
        "futures_marketdata_fresh": True,
        "cross_provider_sync_ok": True,
    }
    if stage_overrides:
        stage.update(stage_overrides)
    return {
        "safe_to_consume": True,
        "provider_runtime": provider_runtime,
        "stage_flags": stage,
    }


def _provider_gate(view: dict[str, Any]) -> tuple[bool, str | None]:
    return miso.provider_gate_pass(view)


def main() -> int:
    now_ns = time.time_ns()

    healthy = getattr(N, "PROVIDER_STATUS_HEALTHY", "HEALTHY")
    stale = getattr(N, "PROVIDER_STATUS_STALE", "STALE")

    miso_spec = D.get_doctrine_contract(N.STRATEGY_FAMILY_MISO)
    profile = D.get_required_provider_profile(miso_spec.required_provider_profile_id)

    view_baseline = _view(
        _healthy_provider_runtime(
            futures_provider=N.PROVIDER_ZERODHA,
            selected_provider=N.PROVIDER_DHAN,
            context_provider=N.PROVIDER_DHAN,
            futures_status=healthy,
            selected_status=healthy,
            context_status=healthy,
        )
    )
    pass_ok, pass_reason = _provider_gate(view_baseline)

    view_futures_stale = _view(
        _healthy_provider_runtime(
            futures_provider=N.PROVIDER_ZERODHA,
            selected_provider=N.PROVIDER_DHAN,
            context_provider=N.PROVIDER_DHAN,
            futures_status=stale,
            selected_status=healthy,
            context_status=healthy,
        )
    )
    fut_fail, fut_reason = _provider_gate(view_futures_stale)

    view_context_stale = _view(
        _healthy_provider_runtime(
            futures_provider=N.PROVIDER_ZERODHA,
            selected_provider=N.PROVIDER_DHAN,
            context_provider=N.PROVIDER_DHAN,
            futures_status=healthy,
            selected_status=healthy,
            context_status=stale,
        )
    )
    ctx_fail, ctx_reason = _provider_gate(view_context_stale)

    view_selected_stale = _view(
        _healthy_provider_runtime(
            futures_provider=N.PROVIDER_ZERODHA,
            selected_provider=N.PROVIDER_DHAN,
            context_provider=N.PROVIDER_DHAN,
            futures_status=healthy,
            selected_status=stale,
            context_status=healthy,
        )
    )
    sel_fail, sel_reason = _provider_gate(view_selected_stale)

    view_sync_failed = _view(
        _healthy_provider_runtime(
            futures_provider=N.PROVIDER_ZERODHA,
            selected_provider=N.PROVIDER_DHAN,
            context_provider=N.PROVIDER_DHAN,
            futures_status=healthy,
            selected_status=healthy,
            context_status=healthy,
        ),
        stage_overrides={"cross_provider_sync_ok": False},
    )
    sync_fail, sync_reason = _provider_gate(view_sync_failed)

    view_rollout_requires_dhan = _view(
        _healthy_provider_runtime(
            futures_provider=N.PROVIDER_ZERODHA,
            selected_provider=N.PROVIDER_DHAN,
            context_provider=N.PROVIDER_DHAN,
            futures_status=healthy,
            selected_status=healthy,
            context_status=healthy,
            dhan_futures_rollout=True,
        )
    )
    rollout_fail, rollout_reason = _provider_gate(view_rollout_requires_dhan)

    view_dhan_futures = _view(
        _healthy_provider_runtime(
            futures_provider=N.PROVIDER_DHAN,
            selected_provider=N.PROVIDER_DHAN,
            context_provider=N.PROVIDER_DHAN,
            futures_status=healthy,
            selected_status=healthy,
            context_status=healthy,
        )
    )
    dhan_fut_pass, dhan_fut_reason = _provider_gate(view_dhan_futures)

    provider_roles = Path("etc/brokers/provider_roles.yaml").read_text(encoding="utf-8")
    runtime = Path("etc/brokers/runtime.yaml").read_text(encoding="utf-8")
    miso_call = Path("etc/strategy_family/frozen/miso_call.yaml").read_text(encoding="utf-8")
    miso_put = Path("etc/strategy_family/frozen/miso_put.yaml").read_text(encoding="utf-8")

    checks = {
        "miso_uses_current_baseline_profile": (
            miso_spec.required_provider_profile_id
            == D.PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE
        ),
        "profile_allows_zerodha_and_dhan_futures": (
            profile.futures_provider_id is None
            and profile.allowed_futures_provider_ids == (N.PROVIDER_ZERODHA, N.PROVIDER_DHAN)
        ),
        "profile_requires_dhan_selected_option": profile.selected_option_provider_id == N.PROVIDER_DHAN,
        "profile_requires_dhan_option_context": profile.option_context_provider_id == N.PROVIDER_DHAN,
        "zerodha_futures_dhan_option_dhan_context_provider_pass": pass_ok is True and pass_reason is None,
        "dhan_futures_dhan_option_dhan_context_provider_pass": dhan_fut_pass is True and dhan_fut_reason is None,
        "zerodha_futures_stale_provider_fail": fut_fail is False and fut_reason == "miso_futures_provider_unhealthy_or_stale",
        "dhan_context_stale_provider_fail": ctx_fail is False and ctx_reason == "miso_option_context_provider_unhealthy_or_stale",
        "dhan_selected_option_stale_provider_fail": sel_fail is False and sel_reason == "miso_selected_option_provider_unhealthy_or_stale",
        "cross_provider_sync_failed_provider_fail": sync_fail is False and sync_reason == "miso_cross_provider_sync_failed",
        "dhan_futures_rollout_requires_dhan_futures": (
            rollout_fail is False
            and rollout_reason == "miso_dhan_futures_rollout_requires_dhan_futures_provider"
        ),
        "config_provider_roles_alignment_ok": all(
            token in provider_roles
            for token in (
                "miso_requires_dhan_option_context: true",
                "miso_requires_dhan_selected_option_marketdata: true",
                "miso_requires_dhan_futures_current_baseline: false",
                "miso_allows_zerodha_futures_when_healthy_and_synced: true",
                "miso_requires_futures_health_and_cross_provider_sync: true",
            )
        ),
        "config_runtime_alignment_ok": all(
            token in runtime
            for token in (
                "miso_futures_policy_current_baseline: ZERODHA_OR_DHAN_HEALTHY_SYNCED",
                "miso_dhan_futures_rollout_enabled: false",
            )
        ),
        "miso_yaml_alignment_ok": all(
            token in miso_call and token in miso_put
            for token in (
                "batch25n_miso_provider_doctrine_alignment",
                "ZERODHA_OR_DHAN_HEALTHY_SYNCED",
                "require_cross_provider_sync: true",
                "when_enabled_requires_futures_provider: DHAN",
            )
        ),
    }

    checks["config_doctrine_provider_alignment_ok"] = all(
        checks[key]
        for key in (
            "miso_uses_current_baseline_profile",
            "profile_allows_zerodha_and_dhan_futures",
            "profile_requires_dhan_selected_option",
            "profile_requires_dhan_option_context",
            "config_provider_roles_alignment_ok",
            "config_runtime_alignment_ok",
            "miso_yaml_alignment_ok",
        )
    )

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_miso_provider_doctrine_alignment",
        "batch": "25N",
        "generated_at_ns": now_ns,
        "miso_provider_doctrine_alignment_ok": proof_ok,
        "checks": checks,
        "provider_gate_cases": {
            "zerodha_futures_dhan_option_dhan_context": {
                "pass": pass_ok,
                "reason": pass_reason,
            },
            "dhan_futures_dhan_option_dhan_context": {
                "pass": dhan_fut_pass,
                "reason": dhan_fut_reason,
            },
            "zerodha_futures_stale": {
                "pass": fut_fail,
                "reason": fut_reason,
            },
            "dhan_context_stale": {
                "pass": ctx_fail,
                "reason": ctx_reason,
            },
            "dhan_selected_option_stale": {
                "pass": sel_fail,
                "reason": sel_reason,
            },
            "cross_provider_sync_failed": {
                "pass": sync_fail,
                "reason": sync_reason,
            },
            "dhan_futures_rollout_with_zerodha_futures": {
                "pass": rollout_fail,
                "reason": rollout_reason,
            },
        },
        "doctrine": {
            "miso_required_provider_profile_id": miso_spec.required_provider_profile_id,
            "profile": {
                "profile_id": profile.profile_id,
                "futures_provider_id": profile.futures_provider_id,
                "allowed_futures_provider_ids": profile.allowed_futures_provider_ids,
                "selected_option_provider_id": profile.selected_option_provider_id,
                "option_context_provider_id": profile.option_context_provider_id,
                "execution_primary_provider_id": profile.execution_primary_provider_id,
                "execution_fallback_provider_id": profile.execution_fallback_provider_id,
                "allow_dhan_degraded": profile.allow_dhan_degraded,
                "execution_bridge_required": profile.execution_bridge_required,
            },
        },
    }

    out = Path("run/proofs/proof_miso_provider_doctrine_alignment.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "miso_provider_doctrine_alignment_ok": proof_ok,
        "zerodha_futures_dhan_option_dhan_context_provider_pass": checks["zerodha_futures_dhan_option_dhan_context_provider_pass"],
        "zerodha_futures_stale_provider_fail": checks["zerodha_futures_stale_provider_fail"],
        "dhan_context_stale_provider_fail": checks["dhan_context_stale_provider_fail"],
        "dhan_selected_option_stale_provider_fail": checks["dhan_selected_option_stale_provider_fail"],
        "config_doctrine_provider_alignment_ok": checks["config_doctrine_provider_alignment_ok"],
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
