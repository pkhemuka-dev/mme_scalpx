#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import strategy as S
from app.mme_scalpx.services.strategy_family import activation as A
from app.mme_scalpx.services.strategy_family import order_intent as OI


def _sample_candidate() -> dict[str, Any]:
    return {
        "candidate_id": "candidate-25q-proof",
        "strategy_family": getattr(N, "STRATEGY_FAMILY_MIST", "MIST"),
        "strategy_branch": getattr(N, "BRANCH_CALL", "CALL"),
        "family_id": getattr(N, "STRATEGY_FAMILY_MIST", "MIST"),
        "branch_id": getattr(N, "BRANCH_CALL", "CALL"),
        "doctrine_id": getattr(N, "DOCTRINE_MIST", "MIST"),
        "action_hint": getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL"),
        "side": getattr(N, "SIDE_CALL", getattr(N, "BRANCH_CALL", "CALL")),
        "instrument_key": getattr(N, "IK_MME_CE", "NIFTY_CE_PROOF"),
        "option_symbol": "NIFTY-25000-CE-25Q",
        "option_token": "TOKEN-25Q-CE",
        "strike": 25000.0,
        "limit_price_hint": 101.25,
        "quantity_lots_hint": 1,
        "entry_mode": getattr(N, "ENTRY_MODE_ATM", "ATM"),
        "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "execution_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "risk_gate_required": True,
        "score": 0.91,
        "blockers": [],
        "source_feature_frame_id": "feature-frame-25q",
        "source_feature_ts_ns": time.time_ns(),
    }


def _flat_hold_decision() -> dict[str, Any]:
    return {
        "action": getattr(N, "ACTION_HOLD", "HOLD"),
        "qty": 0,
        "hold_only": 1,
        "activation_report_only": 1,
        "activation_action": getattr(N, "ACTION_HOLD", "HOLD"),
        "activation_promoted": 0,
        "activation_safe_to_promote": 0,
        "live_orders_allowed": 0,
    }


def main() -> int:
    generated_at_ns = time.time_ns()
    errors: list[str] = []
    checks: dict[str, bool] = {}

    candidate = _sample_candidate()

    preview = OI.build_order_intent_preview(
        candidate,
        runtime_mode=getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
        adapter_enabled=False,
        arming_proof_ok=False,
        final_readiness_ok=False,
    ).to_dict()

    decision = dict(preview["decision"])
    metadata = dict(decision.get("metadata") or {})
    fields_ok, blockers = OI.validate_execution_contract_fields(decision)

    checks["order_intent_preview_valid"] = preview.get("preview_valid") is True
    checks["execution_contract_fields_complete"] = fields_ok and not blockers
    checks["publication_disabled_by_default"] = preview.get("publication_allowed") is False
    checks["adapter_enabled_false_by_default"] = preview.get("adapter_enabled") is False

    checks["execution_top_level_fields_complete"] = all(
        decision.get(key) not in (None, "")
        for key in ("action", "side", "position_effect", "quantity_lots", "instrument_key", "entry_mode")
    )

    checks["execution_metadata_fields_complete"] = all(
        metadata.get(key) not in (None, "")
        for key in (
            "option_symbol",
            "option_token",
            "strike",
            "limit_price",
            "provider_id",
            "execution_provider_id",
            "strategy_family",
            "strategy_branch",
            "doctrine_id",
            "candidate_id",
        )
    )

    activation_selected = SimpleNamespace(
        family_id=candidate["family_id"],
        branch_id=candidate["branch_id"],
        action=candidate["action_hint"],
        score=candidate["score"],
        priority=1.0,
        candidate=candidate,
    )
    activation_decision = SimpleNamespace(selected=activation_selected)

    activation_preview = A.build_order_intent_preview_for_activation(
        activation_decision,
        runtime_mode=getattr(N, "FAMILY_RUNTIME_MODE_OBSERVE_ONLY", "observe_only"),
        adapter_enabled=False,
        arming_proof_ok=False,
        final_readiness_ok=False,
    )

    checks["activation_preview_bridge_ok"] = (
        activation_preview.get("preview_valid") is True
        and activation_preview.get("publication_allowed") is False
    )

    try:
        S._validate_hold_decision_for_publish(_flat_hold_decision())
        hold_guard_accepts_hold = True
    except Exception as exc:
        hold_guard_accepts_hold = False
        errors.append(f"hold_guard_rejected_hold: {exc}")

    checks["observe_only_still_publishes_hold"] = (
        hold_guard_accepts_hold
        and S.strategy_order_intent_adapter_runtime_law().get("strategy_publishes_hold_only") is True
        and S.strategy_order_intent_adapter_runtime_law().get("publication_enabled") is False
    )

    try:
        S._validate_hold_decision_for_publish(
            {
                **decision,
                "qty": decision.get("quantity_lots"),
                "hold_only": 0,
                "activation_report_only": 0,
                "activation_action": decision.get("action"),
                "activation_promoted": 1,
                "activation_safe_to_promote": 1,
                "live_orders_allowed": 1,
            }
        )
        non_hold_blocked = False
    except Exception:
        non_hold_blocked = True

    checks["non_hold_publication_guard_still_blocks"] = non_hold_blocked

    config_text = Path("etc/strategy_family/family_runtime.yaml").read_text(encoding="utf-8")
    checks["runtime_config_adapter_disabled"] = (
        "enabled: false" in config_text
        and "publication_enabled: false" in config_text
        and "default_runtime_mode: observe_only" in config_text
    )

    checks["family_live_only_forbidden"] = (
        OI.is_publication_allowed(
            runtime_mode=getattr(N, "FAMILY_RUNTIME_MODE_FAMILY_LIVE_ONLY", "family_live_only"),
            adapter_enabled=True,
            arming_proof_ok=True,
            final_readiness_ok=True,
        )
        is False
    )

    checks["family_live_legacy_shadow_requires_later_arming"] = (
        OI.is_publication_allowed(
            runtime_mode=getattr(N, "FAMILY_RUNTIME_MODE_FAMILY_LIVE_LEGACY_SHADOW", "family_live_legacy_shadow"),
            adapter_enabled=False,
            arming_proof_ok=False,
            final_readiness_ok=False,
        )
        is False
    )

    proof_ok = all(checks.values()) and not errors

    proof = {
        "proof_name": "proof_order_intent_adapter_disabled",
        "batch": "25Q",
        "generated_at_ns": generated_at_ns,
        "order_intent_adapter_disabled_ok": proof_ok,
        "order_intent_preview_valid": checks["order_intent_preview_valid"],
        "execution_contract_fields_complete": checks["execution_contract_fields_complete"],
        "observe_only_still_publishes_hold": checks["observe_only_still_publishes_hold"],
        "non_hold_publication_guard_still_blocks": checks["non_hold_publication_guard_still_blocks"],
        "checks": checks,
        "errors": errors,
        "observed": {
            "preview": preview,
            "activation_preview": activation_preview,
            "strategy_runtime_law": S.strategy_order_intent_adapter_runtime_law(),
            "validation_blockers": list(blockers),
        },
    }

    out = Path("run/proofs/proof_order_intent_adapter_disabled.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(
        {
            "order_intent_adapter_disabled_ok": proof_ok,
            "order_intent_preview_valid": proof["order_intent_preview_valid"],
            "execution_contract_fields_complete": proof["execution_contract_fields_complete"],
            "observe_only_still_publishes_hold": proof["observe_only_still_publishes_hold"],
            "non_hold_publication_guard_still_blocks": proof["non_hold_publication_guard_still_blocks"],
            "proof_path": str(out),
        },
        indent=2,
        sort_keys=True,
    ))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
