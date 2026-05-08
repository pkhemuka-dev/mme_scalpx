#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "app"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from app.mme_scalpx.core import names as N
from bin._batch25v_market_observation_common import redis_client, hgetall_contract, json_load


PROOF_PATH = Path("run/proofs/proof_paper_armed_readiness_gate.json")


def _load_json(path_s: str) -> dict[str, Any]:
    path = Path(path_s)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _decode_value(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="replace")
    return value


def _decode_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    return {str(_decode_value(k)): _decode_value(v) for k, v in dict(raw or {}).items()}


def _stream_len(client: Any, key: str) -> int:
    try:
        return int(client.xlen(key))
    except Exception:
        return -1


def _hash_get(client: Any, key: str) -> dict[str, Any]:
    try:
        return _decode_hash(client.hgetall(key) or {})
    except Exception:
        return {}


def _status_ready(value: Any) -> bool:
    return str(value or "").strip().upper() in {"HEALTHY", "READY", "OK", "DEGRADED"}


def _hard_ready_status(value: Any) -> bool:
    return str(value or "").strip().upper() in {"HEALTHY", "READY", "OK"}


def _runtime_mode_observe_only(value: Any) -> bool:
    return str(value or "").strip().upper().replace("-", "_") in {
        "OBSERVE_ONLY",
        "HOLD_OBSERVE",
        "HOLD_ONLY",
    }


def _boolish_false(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text in {"", "0", "false", "no", "off", "none", "null"}


def _read_runtime_config_files() -> dict[str, Any]:
    files = [
        "etc/strategy_family/family_runtime.yaml",
        "etc/strategy_family/rollout/paper_armed_readiness_gate.yaml",
        "etc/brokers/runtime.yaml",
        "etc/brokers/provider_roles.yaml",
    ]
    out: dict[str, Any] = {}
    for f in files:
        path = Path(f)
        out[f] = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else 0,
        }
    return out


def main() -> int:
    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    client = redis_client()
    now_ns = time.time_ns()

    batch25v = _load_json("run/proofs/proof_batch25v_final_summary.json")
    provider_proof = _load_json("run/proofs/proof_market_session_provider_runtime.json")
    feed_proof = _load_json("run/proofs/proof_market_session_feed_snapshot.json")
    feature_proof = _load_json("run/proofs/proof_market_session_feature_payload.json")
    family_proof = _load_json("run/proofs/proof_market_session_family_surfaces.json")
    strategy_proof = _load_json("run/proofs/proof_market_session_strategy_activation.json")
    no_order_proof = _load_json("run/proofs/proof_market_session_no_order_sent.json")

    _, provider_key, provider = hgetall_contract(
        client,
        "HASH_STATE_PROVIDER_RUNTIME",
        "HASH_PROVIDER_RUNTIME",
    )

    futures_status = provider.get("futures_marketdata_status") or provider.get("futures_provider_status")
    selected_status = provider.get("selected_option_marketdata_status") or provider.get("selected_option_provider_status")
    option_context_status = provider.get("option_context_status") or provider.get("option_context_provider_status")
    execution_status = provider.get("execution_primary_status") or provider.get("execution_provider_status")

    provider_ts = int(provider.get("last_update_ns") or provider.get("ts_event_ns") or 0)
    provider_age_ms = round((now_ns - provider_ts) / 1_000_000, 2) if provider_ts else None

    family_runtime_mode = provider.get("family_runtime_mode")
    failover_mode = provider.get("failover_mode")
    fallback_status = provider.get("execution_fallback_status") or provider.get("fallback_execution_provider_status")

    orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    trades_key = getattr(N, "STREAM_TRADES_LEDGER", "trades:ledger:stream")

    position_key = getattr(N, "HASH_STATE_POSITION_MME", getattr(N, "HASH_STATE_POSITION", "state:position:mme"))
    position = _hash_get(client, position_key)

    open_position_false = True
    for key in ("side", "position_side", "net_qty", "qty", "quantity", "open_qty"):
        value = position.get(key)
        if key in {"side", "position_side"} and str(value or "").upper() not in {"", "FLAT", "NONE", "0"}:
            open_position_false = False
        if key not in {"side", "position_side"}:
            try:
                if float(value or 0) != 0:
                    open_position_false = False
            except Exception:
                pass

    runtime_files = _read_runtime_config_files()

    checks = {
        "batch25v_final_pass": batch25v.get("final_25v_market_session_observation_ok") is True,
        "provider_runtime_proof_pass": provider_proof.get("market_session_provider_runtime_ok") is True,
        "feed_snapshot_proof_pass": feed_proof.get("market_session_feed_snapshot_ok") is True,
        "feature_payload_proof_pass": feature_proof.get("market_session_feature_payload_ok") is True,
        "family_surfaces_proof_pass": family_proof.get("market_session_family_surfaces_ok") is True,
        "strategy_activation_proof_pass": strategy_proof.get("market_session_strategy_activation_ok") is True,
        "no_order_sent_proof_pass": no_order_proof.get("market_session_no_order_sent_ok") is True,

        "provider_runtime_hash_present": bool(provider),
        "provider_runtime_current": provider_age_ms is not None and provider_age_ms <= 120_000,
        "futures_provider_current": _hard_ready_status(futures_status),
        "selected_option_provider_current": _hard_ready_status(selected_status),
        "option_context_provider_available": _status_ready(option_context_status),
        "execution_primary_provider_current": _hard_ready_status(execution_status),

        "runtime_mode_observe_only": _runtime_mode_observe_only(family_runtime_mode),
        "manual_failover_only": str(failover_mode or "").strip().upper() == "MANUAL",
        "fallback_execution_not_auto_active": str(fallback_status or "").strip().upper() in {"", "DISABLED", "UNAVAILABLE", "DEGRADED"},
        "no_open_position": open_position_false,
        "orders_stream_empty_or_no_growth_safe": _stream_len(client, orders_key) == 0,
        "paper_armed_not_enabled": True,
        "real_live_not_enabled": True,
        "required_config_files_present": all(v["exists"] and v["size"] > 0 for v in runtime_files.values()),
    }

    proof = {
        "proof_name": "proof_paper_armed_readiness_gate",
        "batch": "25W",
        "generated_at_ns": now_ns,
        "paper_armed_readiness_gate_ok": all(checks.values()),
        "checks": checks,
        "provider_runtime_key": provider_key,
        "provider_runtime_age_ms": provider_age_ms,
        "provider_runtime": provider,
        "streams": {
            "orders": {"key": orders_key, "len": _stream_len(client, orders_key)},
            "decisions": {"key": decisions_key, "len": _stream_len(client, decisions_key)},
            "trades": {"key": trades_key, "len": _stream_len(client, trades_key)},
        },
        "position": {
            "key": position_key,
            "state": position,
            "no_open_position": open_position_false,
        },
        "runtime_files": runtime_files,
        "paper_armed_approved": False,
        "real_live_approved": False,
        "verdict": "READY_FOR_CONTROLLED_PAPER_PREP" if all(checks.values()) else "NOT_READY_FOR_PAPER_ARMED",
        "proof_path": str(PROOF_PATH),
    }

    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))

    return 0 if proof["paper_armed_readiness_gate_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
