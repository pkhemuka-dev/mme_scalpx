#!/usr/bin/env python3
from __future__ import annotations

"""
Redis/hash smoke proof for patched strategy.py activation report-only bridge.

This proof:
- connects to Redis
- reads latest HASH_STATE_FEATURES_MME_FUT
- builds StrategyFamilyConsumerView
- builds HOLD-only decision with activation_report_json
- proves action remains HOLD, qty remains 0, promotion remains disabled
- defaults to read-only
- can publish HOLD to replay decision stream with --publish-hold-replay
- can publish HOLD to live decision stream only with --publish-hold-live and an explicit env guard

No broker call.
No execution call.
No order placement.
No live activation.
"""

import argparse
import contextlib
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Mapping


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.mme_scalpx.core import names as N  # noqa: E402
from app.mme_scalpx.services import strategy  # noqa: E402


ENV_FILES = (
    PROJECT_ROOT / ".env",
    PROJECT_ROOT / "etc/project.env",
    PROJECT_ROOT / "etc/redis.env",
    Path.home() / "scalpx/common/etc/redis.env",
)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        with contextlib.suppress(Exception):
            return _jsonable(value.to_dict())
    if hasattr(value, "__dict__"):
        return _jsonable(vars(value))
    return str(value)


def _json_dump(value: Any) -> str:
    return json.dumps(
        _jsonable(value),
        ensure_ascii=False,
        sort_keys=False,
        separators=(",", ":"),
        allow_nan=False,
    )


def _load_env_files() -> None:
    for path in ENV_FILES:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export "):].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = value


def _redis_client_from_project_factory() -> Any | None:
    """
    Try project redisx factories first, without assuming a specific function name.
    """
    try:
        from app.mme_scalpx.core import redisx as RX  # type: ignore
    except Exception:
        return None

    for name in (
        "create_redis_client",
        "get_redis_client",
        "make_redis_client",
        "build_redis_client",
        "new_redis_client",
        "connect",
    ):
        fn = getattr(RX, name, None)
        if not callable(fn):
            continue
        try:
            client = fn()
            if client is not None:
                with contextlib.suppress(Exception):
                    client.ping()
                return client
        except TypeError:
            continue
        except Exception:
            continue

    return None


def _redis_client_from_env() -> Any:
    _load_env_files()

    try:
        import redis
    except Exception as exc:
        raise RuntimeError("python redis package is not importable") from exc

    url = (
        os.environ.get("REDIS_URL")
        or os.environ.get("SCALPX_REDIS_URL")
        or os.environ.get("UPSTASH_REDIS_URL")
    )
    if url:
        client = redis.Redis.from_url(
            url,
            decode_responses=False,
            socket_timeout=5,
            socket_connect_timeout=5,
        )
        client.ping()
        return client

    host = (
        os.environ.get("REDIS_HOST")
        or os.environ.get("SCALPX_REDIS_HOST")
        or os.environ.get("UPSTASH_REDIS_HOST")
    )
    if not host:
        raise RuntimeError(
            "Redis config not found. Set REDIS_URL, or REDIS_HOST/REDIS_PORT/REDIS_PASSWORD."
        )

    port = int(
        os.environ.get("REDIS_PORT")
        or os.environ.get("SCALPX_REDIS_PORT")
        or os.environ.get("UPSTASH_REDIS_PORT")
        or "6379"
    )
    username = (
        os.environ.get("REDIS_USERNAME")
        or os.environ.get("SCALPX_REDIS_USERNAME")
        or os.environ.get("UPSTASH_REDIS_USERNAME")
        or None
    )
    password = (
        os.environ.get("REDIS_PASSWORD")
        or os.environ.get("SCALPX_REDIS_PASSWORD")
        or os.environ.get("UPSTASH_REDIS_PASSWORD")
        or None
    )
    db = int(os.environ.get("REDIS_DB") or os.environ.get("SCALPX_REDIS_DB") or "0")
    ssl_flag = (
        os.environ.get("REDIS_SSL")
        or os.environ.get("REDIS_TLS")
        or os.environ.get("SCALPX_REDIS_SSL")
        or os.environ.get("SCALPX_REDIS_TLS")
        or ""
    ).lower() in {"1", "true", "yes", "y", "on"}

    client = redis.Redis(
        host=host,
        port=port,
        username=username,
        password=password,
        db=db,
        ssl=ssl_flag,
        decode_responses=False,
        socket_timeout=5,
        socket_connect_timeout=5,
    )
    client.ping()
    return client


def make_redis_client() -> Any:
    client = _redis_client_from_project_factory()
    if client is not None:
        return client
    return _redis_client_from_env()


def _decode_hash(raw: Mapping[Any, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in (raw or {}).items():
        k = _safe_str(key)
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        out[k] = value
    return out


def _read_feature_hash(client: Any) -> dict[str, Any]:
    raw = client.hgetall(strategy.HASH_FEATURES) or {}
    return _decode_hash(raw)


def _redis_stream_value(value: Any) -> str | int | float:
    """
    Redis XADD cannot accept None, dict, list, tuple, set, or bool reliably
    across clients. Convert all fields into Redis-safe scalar values.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, (int, float, str, bytes)):
        return value
    if isinstance(value, (dict, list, tuple, set)):
        return _json_dump(value)
    return _safe_str(value)


def _resolve_replay_decision_stream() -> str:
    for name in (
        "STREAM_REPLAY_DECISIONS_MME",
        "STREAM_REPLAY_DECISIONS",
        "REPLAY_STREAM_DECISIONS_MME",
        "REPLAY_STREAM_DECISIONS",
    ):
        value = getattr(N, name, None)
        if value:
            return _safe_str(value)

    replay_name = getattr(N, "replay_name", None)
    if callable(replay_name):
        return _safe_str(replay_name(strategy.STREAM_DECISIONS))

    raise RuntimeError("No replay decision stream name available in names.py")


def _publish_hold_decision(client: Any, decision: Mapping[str, Any], stream_name: str) -> str:
    fields = {
        str(k): _redis_stream_value(v)
        for k, v in decision.items()
    }

    # Final defensive sweep: no None may reach Redis.
    fields = {
        str(k): ("" if v is None else v)
        for k, v in fields.items()
    }

    msg_id = client.xadd(
        stream_name,
        fields=fields,
        maxlen=strategy.DEFAULT_STREAM_MAXLEN,
        approximate=True,
    )
    return _safe_str(msg_id)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--publish-hold-replay",
        action="store_true",
        help="Publish one HOLD diagnostic decision to replay decision stream.",
    )
    parser.add_argument(
        "--publish-hold-live",
        action="store_true",
        help=(
            "Publish one HOLD diagnostic decision to LIVE STREAM_DECISIONS_MME. "
            "Requires I_UNDERSTAND_THIS_WRITES_LIVE_DECISION_STREAM=1."
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if feature hash is unavailable. Default: skip cleanly.",
    )
    args = parser.parse_args()

    client = make_redis_client()

    feature_hash = _read_feature_hash(client)
    if not feature_hash:
        msg = f"SKIP: feature hash empty/unavailable: {strategy.HASH_FEATURES}"
        print(msg)
        report = {
            "skipped": True,
            "reason": "feature_hash_empty",
            "hash_key": strategy.HASH_FEATURES,
            "ts_ns": time.time_ns(),
        }
        out_path = PROJECT_ROOT / "run/proofs/strategy_activation_report_redis_smoke.json"
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        return 1 if args.strict else 0

    bridge = strategy.StrategyFamilyConsumerBridge(redis_client=client)
    bundle = bridge._bundle_from_hash(feature_hash)
    now_ns = time.time_ns()
    view = bridge.build_consumer_view(bundle, now_ns=now_ns)
    decision = bridge.build_hold_decision(view, now_ns=now_ns)

    assert decision["action"] == strategy.ACTION_HOLD, decision
    assert int(decision["qty"]) == 0, decision
    assert int(decision["hold_only"]) == 1, decision
    assert int(decision["activation_bridge_enabled"]) == 1, decision
    assert int(decision["activation_report_only"]) == 1, decision
    assert int(decision["activation_promoted"]) == 0, decision
    assert int(decision["activation_safe_to_promote"]) == 0, decision
    assert decision.get("activation_report_json"), decision

    activation_report = json.loads(_safe_str(decision["activation_report_json"]))
    assert activation_report["action"] == strategy.ACTION_HOLD, activation_report
    assert activation_report["hold"] is True, activation_report
    assert activation_report["promoted"] is False, activation_report
    assert activation_report["safe_to_promote"] is False, activation_report
    assert activation_report["strategy_report_only"] is True, activation_report
    assert activation_report["live_orders_allowed"] is False, activation_report

    diagnostics = json.loads(_safe_str(decision["diagnostics_json"]))
    assert diagnostics["activation_bridge_report_only"] is True, diagnostics
    assert diagnostics["doctrine_leaves_observed"] is True, diagnostics
    assert diagnostics["doctrine_leaves_active"] is False, diagnostics
    assert diagnostics["broker_side_effects_allowed"] is False, diagnostics
    assert diagnostics["live_orders_allowed"] is False, diagnostics

    published_id = None
    published_stream = None
    publish_mode = "read_only"
    writes_live_redis = False
    writes_replay_redis = False

    if args.publish_hold_live and args.publish_hold_replay:
        raise SystemExit("choose only one: --publish-hold-live or --publish-hold-replay")

    if args.publish_hold_live:
        if os.environ.get("I_UNDERSTAND_THIS_WRITES_LIVE_DECISION_STREAM", "").strip() != "1":
            raise SystemExit(
                "--publish-hold-live requires "
                "I_UNDERSTAND_THIS_WRITES_LIVE_DECISION_STREAM=1"
            )
        published_stream = strategy.STREAM_DECISIONS
        published_id = _publish_hold_decision(client, decision, published_stream)
        publish_mode = "live_decision_stream_guarded"
        writes_live_redis = True
        assert published_id, "xadd returned empty message id"

    elif args.publish_hold_replay:
        published_stream = _resolve_replay_decision_stream()
        published_id = _publish_hold_decision(client, decision, published_stream)
        publish_mode = "replay_decision_stream"
        writes_replay_redis = True
        assert published_id, "xadd returned empty message id"

    report = {
        "proof_name": "strategy_activation_report_redis_smoke",
        "proof_scope": "HOLD_REPORT_ONLY_REDIS_SMOKE",
        "activation_ready": False,
        "paper_armed_ready": False,
        "writes_live_redis": writes_live_redis,
        "writes_replay_redis": writes_replay_redis,
        "uses_broker": False,
        "places_orders": False,
        "publish_mode": publish_mode,
        "does_not_prove": [
            "activation_readiness",
            "paper_armed_readiness",
            "provider_token_equivalence",
            "execution_safety",
            "order_intent_validity",
            "risk_exit_never_blocked",
        ],
        "skipped": False,
        "hash_key": strategy.HASH_FEATURES,
        "stream_decisions": strategy.STREAM_DECISIONS,
        "feature_hash_field_count": len(feature_hash),
        "feature_frame_id": bundle.feature_frame_id,
        "feature_frame_ts_ns": bundle.feature_frame_ts_ns,
        "view": {
            "safe_to_consume": view.safe_to_consume,
            "hold_only": view.hold_only,
            "data_valid": view.data_valid,
            "warmup_complete": view.warmup_complete,
            "provider_ready_classic": view.provider_ready_classic,
            "provider_ready_miso": view.provider_ready_miso,
            "regime": view.regime,
            "family_ids": list(view.family_status.keys()),
            "branch_frame_count": len(view.branch_frames),
        },
        "decision": {
            "decision_id": decision.get("decision_id"),
            "action": decision.get("action"),
            "qty": decision.get("qty"),
            "hold_only": decision.get("hold_only"),
            "activation_mode": decision.get("activation_mode"),
            "activation_reason": decision.get("activation_reason"),
            "activation_candidate_count": decision.get("activation_candidate_count"),
            "activation_selected_family_id": decision.get("activation_selected_family_id"),
            "activation_selected_branch_id": decision.get("activation_selected_branch_id"),
            "activation_selected_action": decision.get("activation_selected_action"),
            "activation_promoted": decision.get("activation_promoted"),
            "activation_safe_to_promote": decision.get("activation_safe_to_promote"),
        },
        "activation_report": activation_report,
        "diagnostics": diagnostics,
        "published_hold_decision_id": published_id,
        "published_hold_stream": published_stream,
        "ts_ns": now_ns,
    }

    out_path = PROJECT_ROOT / "run/proofs/strategy_activation_report_redis_smoke.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")

    print("===== STRATEGY ACTIVATION REPORT REDIS/HASH SMOKE =====")
    print("hash_key =", strategy.HASH_FEATURES)
    print("feature_hash_field_count =", len(feature_hash))
    print("safe_to_consume =", view.safe_to_consume)
    print("decision_action =", decision["action"])
    print("qty =", decision["qty"])
    print("hold_only =", decision["hold_only"])
    print("activation_mode =", decision["activation_mode"])
    print("activation_reason =", decision["activation_reason"])
    print("activation_candidate_count =", decision["activation_candidate_count"])
    print("activation_selected_family_id =", decision["activation_selected_family_id"])
    print("activation_selected_branch_id =", decision["activation_selected_branch_id"])
    print("activation_selected_action =", decision["activation_selected_action"])
    print("activation_promoted =", decision["activation_promoted"])
    print("activation_safe_to_promote =", decision["activation_safe_to_promote"])
    print("live_orders_allowed =", activation_report["live_orders_allowed"])
    print("publish_mode =", publish_mode)
    print("writes_live_redis =", writes_live_redis)
    print("writes_replay_redis =", writes_replay_redis)
    print("published_hold_stream =", published_stream)
    print("published_hold_decision_id =", published_id)
    print("dumped =", out_path.relative_to(PROJECT_ROOT))
    print("strategy activation report Redis/hash smoke: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
