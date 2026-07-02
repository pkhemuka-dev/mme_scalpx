from __future__ import annotations

# R32D_INTERNAL_ORDER_INTENT_PIPELINE_NO_BROKER_SEND
# Internal pipeline only:
# candidate_intent -> risk_decision_shadow -> execution_sim_shadow -> order_intent_ledger.
# Real broker transport is deliberately hard-blocked.

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


PIPELINE_VERSION = "r32d_internal_order_intent_pipeline_v1"
BROKER_TRANSPORT_BLOCK_REASON = "R32D_BROKER_TRANSPORT_HARD_BLOCKED_NO_SEND"


class BrokerTransportHardBlocked(RuntimeError):
    pass


_DANGEROUS_ENV_FLAGS = (
    "SCALPX_ENABLE_LIVE",
    "SCALPX_ENABLE_PAPER",
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
)


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on", "enable", "enabled"}


def assert_broker_transport_hard_blocked(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    env_map = dict(os.environ if env is None else env)
    enabled = [name for name in _DANGEROUS_ENV_FLAGS if _truthy(env_map.get(name))]
    if enabled:
        raise BrokerTransportHardBlocked(
            "broker transport refused because live/paper/control flags are enabled: " + ",".join(enabled)
        )
    return {
        "broker_transport_enabled": False,
        "broker_send_enabled": False,
        "dangerous_env_enabled": enabled,
        "block_reason": BROKER_TRANSPORT_BLOCK_REASON,
    }


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    raw = json.dumps(dict(payload), sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:24]}"


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except Exception:
        return default


# R32G_REAL_CANDIDATE_HOLD_TO_INTERNAL_ENTRY_NORMALIZER
def _r32g_candidate_truth_for_internal_entry(candidate: Mapping[str, Any]) -> bool:
    if _truthy(candidate.get("candidate_present")) or _truthy(candidate.get("eligible")):
        return True
    if _as_int(candidate.get("strict_candidate_count"), 0) > 0:
        return True
    # R32E real-candidate bridge has already filtered candidate-positive R9X rows.
    src = str(candidate.get("source") or "")
    if src.startswith("r32e_real_r9x_candidate_bridge") and _as_float(candidate.get("score"), 0.0) > 0:
        return True
    # Generic internal candidate-intent input: positive score + family + symbol/side.
    if _as_float(candidate.get("score"), 0.0) > 0 and str(candidate.get("family_id") or candidate.get("family") or ""):
        return True
    return False


def _r32g_normalize_internal_entry_action(
    candidate: Mapping[str, Any],
    source_action: str,
    *,
    side: str,
    symbol: str,
) -> tuple[str, str]:
    action = str(source_action or "").upper()
    if action in {"ENTRY", "ENTER", "ENTER_CALL", "ENTER_PUT", "BUY", "LONG"}:
        return action, "source_action_already_entry_like"
    if (
        action == "HOLD"
        and side in {"CALL", "PUT", "CE", "PE"}
        and bool(symbol)
        and _r32g_candidate_truth_for_internal_entry(candidate)
    ):
        return "ENTRY", "r32g_candidate_present_hold_to_internal_entry_shadow_only"
    return action, "source_action_preserved"


@dataclass(frozen=True)
class InternalPipelineConfig:
    default_qty: int = 75
    max_qty: int = 75
    default_product: str = "MIS"
    default_order_type: str = "MARKET"
    default_variety: str = "regular"
    allow_real_broker_transport: bool = False


def build_candidate_intent(candidate: Mapping[str, Any], *, now_ns: int | None = None) -> dict[str, Any]:
    ts_ns = int(now_ns or time.time_ns())
    side = str(candidate.get("side") or candidate.get("option_side") or "").upper()
    symbol = str(candidate.get("symbol") or candidate.get("trading_symbol") or candidate.get("option_symbol") or "")
    source_action = str(candidate.get("action") or candidate.get("decision_action") or candidate.get("risk_action") or "ENTRY").upper()
    action, action_normalization_reason = _r32g_normalize_internal_entry_action(
        candidate,
        source_action,
        side=side,
        symbol=symbol,
    )
    family_id = str(candidate.get("family_id") or candidate.get("family") or "UNKNOWN")
    score = _as_float(candidate.get("score", candidate.get("candidate_score", 0.0)))
    qty = _as_int(candidate.get("qty", candidate.get("quantity", 75)), 75)
    price = _as_float(candidate.get("price", candidate.get("ltp", candidate.get("entry_price", 0.0))))

    intent = {
        "schema_version": 1,
        "pipeline_version": PIPELINE_VERSION,
        "record_type": "candidate_intent",
        "ts_ns": ts_ns,
        "family_id": family_id,
        "side": side,
        "action": action,
        "source_action": source_action,
        "action_normalization_reason": action_normalization_reason,
        "r32g_action_normalized": action != source_action,
        "symbol": symbol,
        "qty": qty,
        "price": price,
        "score": score,
        "source": str(candidate.get("source") or "r32d_internal_pipeline"),
        "raw_candidate": dict(candidate),
        "real_order_intent_generated": False,
        "broker_send_enabled": False,
        "broker_transport_block_reason": BROKER_TRANSPORT_BLOCK_REASON,
    }
    intent["candidate_intent_id"] = _stable_id("cand", intent)
    return intent


def build_risk_decision_shadow(candidate_intent: Mapping[str, Any], config: InternalPipelineConfig | None = None) -> dict[str, Any]:
    cfg = config or InternalPipelineConfig()
    side = str(candidate_intent.get("side") or "").upper()
    symbol = str(candidate_intent.get("symbol") or "")
    action = str(candidate_intent.get("action") or "").upper()
    qty = min(max(_as_int(candidate_intent.get("qty"), cfg.default_qty), 0), cfg.max_qty)
    reasons: list[str] = []

    if side not in {"CALL", "PUT", "CE", "PE"}:
        reasons.append("invalid_or_missing_side")
    if not symbol:
        reasons.append("missing_symbol")
    if action not in {"ENTRY", "ENTER", "ENTER_CALL", "ENTER_PUT", "BUY", "LONG"}:
        reasons.append("unsupported_action_for_internal_entry")
    if qty <= 0:
        reasons.append("invalid_qty")

    status = "ACCEPT_SHADOW" if not reasons else "REJECT_SHADOW"
    row = {
        "schema_version": 1,
        "pipeline_version": PIPELINE_VERSION,
        "record_type": "risk_decision_shadow",
        "candidate_intent_id": candidate_intent.get("candidate_intent_id"),
        "risk_status": status,
        "risk_reasons": reasons,
        "side": side,
        "symbol": symbol,
        "action": action,
        "qty": qty,
        "max_qty": cfg.max_qty,
        "real_order_intent_generated": False,
        "broker_send_enabled": False,
        "broker_transport_block_reason": BROKER_TRANSPORT_BLOCK_REASON,
    }
    row["risk_decision_id"] = _stable_id("risk", row)
    return row


def build_execution_sim_shadow(
    candidate_intent: Mapping[str, Any],
    risk_decision: Mapping[str, Any],
) -> dict[str, Any]:
    accepted = str(risk_decision.get("risk_status") or "") == "ACCEPT_SHADOW"
    qty = _as_int(risk_decision.get("qty"), 0) if accepted else 0
    price = _as_float(candidate_intent.get("price"), 0.0)
    row = {
        "schema_version": 1,
        "pipeline_version": PIPELINE_VERSION,
        "record_type": "execution_sim_shadow",
        "candidate_intent_id": candidate_intent.get("candidate_intent_id"),
        "risk_decision_id": risk_decision.get("risk_decision_id"),
        "execution_status": "FILLED_SIM_SHADOW" if accepted else "BLOCKED_BY_RISK_SHADOW",
        "side": risk_decision.get("side"),
        "symbol": risk_decision.get("symbol"),
        "qty": qty,
        "fill_price": price if accepted else 0.0,
        "filled_qty": qty,
        "net_pnl": 0.0,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "broker_send_enabled": False,
        "broker_transport_block_reason": BROKER_TRANSPORT_BLOCK_REASON,
    }
    row["execution_sim_id"] = _stable_id("execsim", row)
    return row


def build_order_intent_ledger(
    candidate_intent: Mapping[str, Any],
    risk_decision: Mapping[str, Any],
    execution_sim: Mapping[str, Any],
    config: InternalPipelineConfig | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    cfg = config or InternalPipelineConfig()
    if cfg.allow_real_broker_transport:
        raise BrokerTransportHardBlocked("R32D refuses allow_real_broker_transport=True")
    block = assert_broker_transport_hard_blocked(env)
    would_have_order = str(execution_sim.get("execution_status") or "") == "FILLED_SIM_SHADOW"

    row = {
        "schema_version": 1,
        "pipeline_version": PIPELINE_VERSION,
        "record_type": "order_intent_ledger",
        "candidate_intent_id": candidate_intent.get("candidate_intent_id"),
        "risk_decision_id": risk_decision.get("risk_decision_id"),
        "execution_sim_id": execution_sim.get("execution_sim_id"),
        "order_intent_status": "BROKER_BLOCKED_INTENT_RECORDED" if would_have_order else "NO_ORDER_INTENT_RISK_BLOCKED",
        "would_have_order": bool(would_have_order),
        "side": risk_decision.get("side"),
        "symbol": risk_decision.get("symbol"),
        "qty": execution_sim.get("qty", 0),
        "order_type": cfg.default_order_type,
        "product": cfg.default_product,
        "variety": cfg.default_variety,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "broker_order_id": None,
        **block,
    }
    row["order_intent_id"] = _stable_id("orderintent", row)
    return row


def run_internal_order_intent_pipeline(
    candidates: list[Mapping[str, Any]],
    *,
    outdir: str | Path,
    config: InternalPipelineConfig | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    cfg = config or InternalPipelineConfig()
    assert_broker_transport_hard_blocked(env)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    ledgers = {
        "candidate_intents": [],
        "risk_decision_shadow": [],
        "execution_sim_shadow": [],
        "order_intent_ledger": [],
    }

    for candidate in candidates:
        ci = build_candidate_intent(candidate)
        rd = build_risk_decision_shadow(ci, cfg)
        ex = build_execution_sim_shadow(ci, rd)
        oi = build_order_intent_ledger(ci, rd, ex, cfg, env)
        ledgers["candidate_intents"].append(ci)
        ledgers["risk_decision_shadow"].append(rd)
        ledgers["execution_sim_shadow"].append(ex)
        ledgers["order_intent_ledger"].append(oi)

    for name, rows in ledgers.items():
        path = out / f"{name}.jsonl"
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True, default=str) + "\n")

    summary = {
        "schema_version": 1,
        "pipeline_version": PIPELINE_VERSION,
        "candidate_intent_count": len(ledgers["candidate_intents"]),
        "risk_accept_shadow_count": sum(1 for r in ledgers["risk_decision_shadow"] if r.get("risk_status") == "ACCEPT_SHADOW"),
        "risk_reject_shadow_count": sum(1 for r in ledgers["risk_decision_shadow"] if r.get("risk_status") != "ACCEPT_SHADOW"),
        "execution_sim_filled_count": sum(1 for r in ledgers["execution_sim_shadow"] if r.get("execution_status") == "FILLED_SIM_SHADOW"),
        "order_intent_recorded_count": len(ledgers["order_intent_ledger"]),
        "would_have_order_count": sum(1 for r in ledgers["order_intent_ledger"] if r.get("would_have_order") is True),
        "real_order_sent_count": sum(1 for r in ledgers["order_intent_ledger"] if r.get("real_order_sent") is True),
        "broker_calls_executed_count": sum(1 for r in ledgers["order_intent_ledger"] if r.get("broker_calls_executed") is True),
        "broker_send_enabled": False,
        "broker_transport_block_reason": BROKER_TRANSPORT_BLOCK_REASON,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return {"summary": summary, "ledgers": ledgers, "outdir": str(out)}
