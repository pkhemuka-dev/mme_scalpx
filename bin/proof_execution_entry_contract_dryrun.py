#!/usr/bin/env python3
from __future__ import annotations

import copy
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
from app.mme_scalpx.services import execution as EX
from app.mme_scalpx.services.strategy_family import order_intent as OI


def _candidate_metadata() -> dict[str, Any]:
    return {
        "candidate_id": "candidate-25r-proof",
        "strategy_family": getattr(N, "STRATEGY_FAMILY_MIST", "MIST"),
        "strategy_branch": getattr(N, "BRANCH_CALL", "CALL"),
        "doctrine_id": getattr(N, "DOCTRINE_MIST", "MIST"),
        "action_hint": getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL"),
        "side": getattr(N, "SIDE_CALL", "CALL"),
        "instrument_key": getattr(N, "IK_MME_CE", "NIFTY_CE"),
        "option_symbol": "NIFTY-25000-CE-25R",
        "option_token": "OPTION-TOKEN-25R",
        "strike": 25000.0,
        "limit_price_hint": 110.0,
        "quantity_lots_hint": 1,
        "entry_mode": getattr(N, "ENTRY_MODE_ATM", "ATM"),
        "provider_id": getattr(N, "PROVIDER_DHAN", "DHAN"),
        "execution_provider_id": getattr(N, "PROVIDER_ZERODHA", "ZERODHA"),
        "risk_gate_required": True,
        "score": 0.91,
        "blockers": [],
        "source_feature_frame_id": "frame-25r-proof",
        "source_feature_ts_ns": time.time_ns(),
    }


def _parse(fields: dict[str, str]) -> EX.DecisionView:
    service = EX.ExecutionService.__new__(EX.ExecutionService)
    return EX.ExecutionService._parse_decision(service, "25R-1", fields)


def _mutated_fields(remove_meta_key: str | None = None) -> dict[str, str]:
    payload = OI.build_promoted_entry_payload(
        candidate_metadata=_candidate_metadata(),
        decision_id="decision-25r-proof",
        ts_event_ns=time.time_ns(),
    )
    if remove_meta_key is not None:
        payload = copy.deepcopy(payload)
        payload["metadata"].pop(remove_meta_key, None)
        fields = {
            "decision_id": str(payload["decision_id"]),
            "ts_ns": str(payload["ts_event_ns"]),
            "action": str(payload["action"]),
            "reason_code": "BATCH25R_MUTATION",
            "entry_mode": str(payload["entry_mode"]),
            "payload_json": json.dumps(payload, separators=(",", ":"), ensure_ascii=False, default=str),
        }
        return fields
    return OI.build_strategy_stream_fields(payload=payload)


def _parse_rejects(fields: dict[str, str], expected_reason: str) -> bool:
    try:
        _parse(fields)
    except Exception as exc:
        return expected_reason in str(exc)
    return False


def main() -> int:
    payload = OI.build_promoted_entry_payload(
        candidate_metadata=_candidate_metadata(),
        decision_id="decision-25r-valid",
        ts_event_ns=time.time_ns(),
    )
    fields = OI.build_strategy_stream_fields(payload=payload)
    decision = _parse(fields)

    checks = {
        "valid_promoted_entry_passes_parser": (
            decision.action == getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
            and decision.quantity_lots == 1
            and decision.instrument_key == getattr(N, "IK_MME_CE", "NIFTY_CE")
            and decision.metadata.get("option_symbol") == "NIFTY-25000-CE-25R"
            and decision.metadata.get("option_token") == "OPTION-TOKEN-25R"
            and str(decision.metadata.get("limit_price")) == "110.0"
        ),
        "missing_option_symbol_rejected": _parse_rejects(
            _mutated_fields("option_symbol"),
            "missing_option_symbol",
        ),
        "missing_option_token_rejected": _parse_rejects(
            _mutated_fields("option_token"),
            "missing_option_token",
        ),
        "missing_limit_price_rejected": _parse_rejects(
            _mutated_fields("limit_price"),
            "missing_or_invalid_limit_price",
        ),
        "order_intent_contract_exports_present": all(
            hasattr(OI, name)
            for name in (
                "PROMOTED_ENTRY_REQUIRED_TOP_LEVEL_KEYS",
                "PROMOTED_ENTRY_REQUIRED_METADATA_KEYS",
                "build_promoted_entry_payload",
                "build_strategy_stream_fields",
            )
        ),
    }

    proof_ok = all(checks.values())

    proof = {
        "proof_name": "proof_execution_entry_contract_dryrun",
        "batch": "25R",
        "generated_at_ns": time.time_ns(),
        "execution_entry_contract_dryrun_ok": proof_ok,
        "checks": checks,
        "valid_decision": {
            "decision_id": decision.decision_id,
            "action": decision.action,
            "side": decision.side,
            "position_effect": decision.position_effect,
            "quantity_lots": decision.quantity_lots,
            "instrument_key": decision.instrument_key,
            "entry_mode": decision.entry_mode,
            "metadata_keys": sorted(decision.metadata.keys()),
        },
        "runtime_safety": {
            "no_strategy_promotion_enabled": True,
            "no_execution_arming_changed": True,
            "parser_dryrun_only": True,
        },
    }

    out = Path("run/proofs/proof_execution_entry_contract_dryrun.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "execution_entry_contract_dryrun_ok": proof_ok,
        **checks,
        "proof_path": str(out),
    }, indent=2, sort_keys=True))

    return 0 if proof_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
