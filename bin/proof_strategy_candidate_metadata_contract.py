#!/usr/bin/env python3
from __future__ import annotations

import inspect
import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services.strategy_family import activation as SF_ACT
from app.mme_scalpx.services.strategy_family import common as SF_COMMON
from app.mme_scalpx.services.strategy_family import mist, misb, misc, misr, miso


FAMILY_SPECS = (
    (N.STRATEGY_FAMILY_MIST, N.DOCTRINE_MIST, N.BRANCH_CALL, mist, "MistCandidate", "MistEvaluationResult"),
    (N.STRATEGY_FAMILY_MISB, N.DOCTRINE_MISB, N.BRANCH_CALL, misb, "MisbCandidate", "MisbEvaluationResult"),
    (N.STRATEGY_FAMILY_MISC, N.DOCTRINE_MISC, N.BRANCH_CALL, misc, "MiscCandidate", "MiscEvaluationResult"),
    (N.STRATEGY_FAMILY_MISR, N.DOCTRINE_MISR, N.BRANCH_CALL, misr, "MisrCandidate", "MisrEvaluationResult"),
    (N.STRATEGY_FAMILY_MISO, N.DOCTRINE_MISO, N.BRANCH_CALL, miso, "MisoCandidate", "MisoEvaluationResult"),
)



def _filter_kwargs_for_callable(callable_obj: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Filter synthetic proof kwargs to the actual dataclass/constructor ABI.

    Strategy-family candidate classes are not required to accept identical
    constructor fields. Batch 25P proves metadata standardization, not identical
    candidate constructor ABIs.
    """
    try:
        sig = inspect.signature(callable_obj)
    except Exception:
        return dict(kwargs)

    params = sig.parameters
    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params.values()):
        return dict(kwargs)

    accepted = {
        name
        for name, param in params.items()
        if name != "self"
        and param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    }
    return {key: value for key, value in kwargs.items() if key in accepted}

def _action_for_branch(branch_id: str) -> str:
    if branch_id == N.BRANCH_CALL:
        return getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
    return getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")


def _side_for_branch(branch_id: str) -> str:
    if branch_id == N.BRANCH_CALL:
        return getattr(N, "SIDE_CALL", "CALL")
    return getattr(N, "SIDE_PUT", "PUT")


def _view(now_ns: int) -> dict[str, Any]:
    return {
        "frame_id": "feature-frame-25p-proof",
        "frame_ts_ns": now_ns,
        "features_generated_at_ns": now_ns,
        "provider_runtime": {
            "selected_option_marketdata_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
            "active_selected_option_provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
            "execution_primary_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
            "active_execution_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        },
        "risk": {
            "preview_quantity_lots": 1,
        },
        "stage_flags": {
            "risk_gate_required": True,
        },
    }


def _candidate_kwargs(
    *,
    family_id: str,
    doctrine_id: str,
    branch_id: str,
    now_ns: int,
) -> dict[str, Any]:
    side = _side_for_branch(branch_id)
    return {
        "family_id": family_id,
        "doctrine_id": doctrine_id,
        "branch_id": branch_id,
        "side": side,
        "action": _action_for_branch(branch_id),
        "score": 0.91,
        "priority": 91.0,
        "instrument_key": f"{family_id}-{branch_id}-IK",
        "instrument_token": f"{family_id}-{branch_id}-TOKEN",
        "option_symbol": f"NIFTY-25000-{side}-25P",
        "strike": 25000.0,
        "option_price": 110.0,
        "tick_size": 0.05,
        "quantity_lots_hint": 1,
        "source_event_id": f"source-{now_ns}",
        "metadata": {
            "entry_mode": getattr(N, "ENTRY_MODE_ATM", "ATM"),
            "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
            "execution_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
            "blockers": [],
        },
    }


def _build_result(
    *,
    family_id: str,
    doctrine_id: str,
    branch_id: str,
    module: Any,
    candidate_class_name: str,
    result_class_name: str,
    now_ns: int,
) -> Any:
    Candidate = getattr(module, candidate_class_name)
    Result = getattr(module, result_class_name)

    candidate_kwargs = _candidate_kwargs(
        family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=branch_id,
        now_ns=now_ns,
    )
    candidate = Candidate(**_filter_kwargs_for_callable(Candidate, candidate_kwargs))

    return Result(
        family_id=family_id,
        doctrine_id=doctrine_id,
        branch_id=branch_id,
        action=_action_for_branch(branch_id),
        is_candidate=True,
        is_blocked=False,
        candidate=candidate,
        blocker=None,
        metadata={"reason": "batch25p_synthetic_candidate"},
    )


def _candidate_metadata(result: Any) -> dict[str, Any]:
    candidate = getattr(result, "candidate", None)
    if candidate is None:
        return {}
    data = candidate.to_dict() if hasattr(candidate, "to_dict") else dict(candidate)
    metadata = data.get("metadata")
    return dict(metadata) if isinstance(metadata, dict) else {}


def main() -> int:
    now_ns = time.time_ns()
    view = _view(now_ns)

    family_checks: dict[str, dict[str, bool]] = {}
    family_metadata: dict[str, dict[str, Any]] = {}
    missing_by_family: dict[str, list[str]] = {}

    for family_id, doctrine_id, branch_id, module, candidate_cls, result_cls in FAMILY_SPECS:
        raw_result = _build_result(
            family_id=family_id,
            doctrine_id=doctrine_id,
            branch_id=branch_id,
            module=module,
            candidate_class_name=candidate_cls,
            result_class_name=result_cls,
            now_ns=now_ns,
        )

        standardized = SF_COMMON.standardize_candidate_result(
            raw_result,
            view_like=view,
            family_id=family_id,
            doctrine_id=doctrine_id,
        )
        metadata = _candidate_metadata(standardized)
        complete, missing = SF_COMMON.candidate_metadata_contract_status(metadata)
        missing_by_family[family_id] = missing
        family_metadata[family_id] = metadata

        family_checks[family_id] = {
            "identity": all(
                metadata.get(key)
                for key in (
                    "candidate_id",
                    "strategy_family",
                    "strategy_branch",
                    "doctrine_id",
                    "action_hint",
                    "side",
                    "source_feature_frame_id",
                    "source_feature_ts_ns",
                )
            ),
            "option_identity_when_candidate": all(
                metadata.get(key)
                for key in (
                    "instrument_key",
                    "option_symbol",
                    "option_token",
                    "strike",
                )
            ),
            "price_hint_when_candidate": bool(metadata.get("limit_price_hint")),
            "quantity_hint_when_candidate": bool(metadata.get("quantity_lots_hint")),
            "provider_identity": bool(metadata.get("provider_id") and metadata.get("execution_provider_id")),
            "risk_gate_required": metadata.get("risk_gate_required") is True,
            "blockers_list": isinstance(metadata.get("blockers"), list),
            "contract_complete": complete,
        }

    leaf_wrappers_present = all(
        hasattr(module, "_BATCH25P_ORIGINAL_EVALUATE_BRANCH")
        for _family, _doctrine, _branch, module, _candidate_cls, _result_cls in FAMILY_SPECS
    )

    cfg = SF_ACT.StrategyFamilyActivationConfig().normalized()
    activation_still_report_only = (
        cfg.activation_mode == SF_ACT.ACTIVATION_MODE_HOLD_ONLY
        and cfg.allow_candidate_promotion is False
        and cfg.allow_live_orders is False
    )

    strategy_text = Path("app/mme_scalpx/services/strategy.py").read_text(encoding="utf-8")
    strategy_py_still_publishes_hold = all(
        token in strategy_text
        for token in (
            "ACTIVATION_REPORT_ONLY: Final[bool] = True",
            "ACTIVATION_ALLOW_CANDIDATE_PROMOTION: Final[bool] = False",
            '"action": ACTION_HOLD',
            '"quantity_lots": 0',
            '"position_effect": POSITION_EFFECT_NONE',
        )
    )

    activation_helper_present = hasattr(SF_ACT, "candidate_metadata_contract_report")

    checks = {
        "all_family_candidates_have_identity": all(item["identity"] for item in family_checks.values()),
        "all_family_candidates_have_option_identity_when_candidate": all(item["option_identity_when_candidate"] for item in family_checks.values()),
        "all_family_candidates_have_price_hint_when_candidate": all(item["price_hint_when_candidate"] for item in family_checks.values()),
        "all_family_candidates_have_quantity_hint_when_candidate": all(item["quantity_hint_when_candidate"] for item in family_checks.values()),
        "all_family_candidates_have_provider_identity": all(item["provider_identity"] for item in family_checks.values()),
        "all_family_candidates_have_risk_gate_required": all(item["risk_gate_required"] for item in family_checks.values()),
        "all_family_candidates_have_blockers_list": all(item["blockers_list"] for item in family_checks.values()),
        "all_family_candidate_metadata_contracts_complete": all(item["contract_complete"] for item in family_checks.values()),
        "leaf_wrappers_present": leaf_wrappers_present,
        "activation_metadata_report_helper_present": activation_helper_present,
        "activation_still_report_only": activation_still_report_only,
        "strategy_py_still_publishes_hold": strategy_py_still_publishes_hold,
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_strategy_candidate_metadata_contract",
        "batch": "25P",
        "generated_at_ns": now_ns,
        "strategy_candidate_metadata_contract_ok": proof_ok,
        "checks": checks,
        "required_candidate_metadata": list(SF_COMMON.CANDIDATE_METADATA_REQUIRED_KEYS),
        "family_checks": family_checks,
        "missing_by_family": missing_by_family,
        "family_metadata": family_metadata,
        "runtime_safety": {
            "activation_mode_default": cfg.activation_mode,
            "activation_allow_candidate_promotion": cfg.allow_candidate_promotion,
            "activation_allow_live_orders": cfg.allow_live_orders,
            "strategy_report_only": True,
            "strategy_hold_only": True,
        },
    }

    out = Path("run/proofs/proof_strategy_candidate_metadata_contract.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "strategy_candidate_metadata_contract_ok": proof_ok,
        "all_family_candidates_have_identity": checks["all_family_candidates_have_identity"],
        "all_family_candidates_have_option_identity_when_candidate": checks["all_family_candidates_have_option_identity_when_candidate"],
        "all_family_candidates_have_price_hint_when_candidate": checks["all_family_candidates_have_price_hint_when_candidate"],
        "activation_still_report_only": checks["activation_still_report_only"],
        "strategy_py_still_publishes_hold": checks["strategy_py_still_publishes_hold"],
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
