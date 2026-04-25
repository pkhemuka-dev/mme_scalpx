#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import names as N
from app.mme_scalpx.services import feeds as F
from app.mme_scalpx.services import features as FE


class DummyAdapter:
    def poll(self):
        return []


class FakeRedis:
    def __init__(self, hashes: dict[str, dict[str, Any]] | None = None) -> None:
        self.hashes = hashes or {}

    def hgetall(self, key: str):
        return self.hashes.get(key, {})


@contextmanager
def patched_env(**values: str | None) -> Iterator[None]:
    old = {key: os.environ.get(key) for key in values}
    try:
        for key, value in values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _expect_reject(label: str, fn) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        return {"case": label, "status": "PASS", "error": str(exc)}
    return {"case": label, "status": "FAIL", "error": "accepted invalid state"}


def _expect_pass(label: str, fn) -> dict[str, Any]:
    try:
        value = fn()
    except Exception as exc:
        return {"case": label, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
    return {"case": label, "status": "PASS", "value": value}


def _context_only_context() -> Any:
    class Ctx:
        feed_adapter = None
        market_data_adapter = None
        feed_adapters = {}
        zerodha_feed_adapter = None
        dhan_feed_adapter = None
        dhan_context_adapter = DummyAdapter()
    return Ctx()


def _dual_feed_context() -> Any:
    class Ctx:
        feed_adapter = None
        market_data_adapter = None
        feed_adapters = {
            N.PROVIDER_ZERODHA: DummyAdapter(),
            N.PROVIDER_DHAN: DummyAdapter(),
        }
        zerodha_feed_adapter = DummyAdapter()
        dhan_feed_adapter = DummyAdapter()
        dhan_context_adapter = DummyAdapter()
    return Ctx()



def _extract_adapter_keys(context: Any) -> list[str]:
    result = F._extract_adapter_surfaces(context)
    if isinstance(result, tuple) and len(result) == 2:
        adapters = result[0]
    else:
        adapters = result
    return sorted(dict(adapters).keys())

def _mk_features_engine(hashes: dict[str, dict[str, Any]]) -> FE.FeatureEngine:
    return FE.FeatureEngine(redis_client=FakeRedis(hashes))


def main() -> int:
    cases: list[dict[str, Any]] = []

    cases.append({
        "case": "feeds_config_has_explicit_snapshot_sync_tolerance",
        "status": "PASS"
        if hasattr(F.FeedConfig(), "snapshot_sync_max_ms") and F.FeedConfig().snapshot_sync_max_ms > 0
        else "FAIL",
        "snapshot_sync_max_ms": getattr(F.FeedConfig(), "snapshot_sync_max_ms", None),
    })

    if hasattr(F, "_extract_adapter_surfaces"):
        with patched_env(MME_PROVIDER_RUNTIME_STRICT=None):
            def _context_only_must_fail() -> None:
                try:
                    F._extract_adapter_surfaces(_context_only_context())
                except Exception as exc:
                    message = str(exc)
                    if "true market-data adapter" in message or "market-data" in message:
                        raise
                    raise AssertionError(f"wrong rejection reason: {type(exc).__name__}: {exc}") from exc

            cases.append(_expect_reject(
                "context_only_adapter_rejected_as_marketdata",
                _context_only_must_fail,
            ))

        with patched_env(MME_PROVIDER_RUNTIME_STRICT="1"):
            cases.append(_expect_pass(
                "strict_dual_marketdata_adapters_accepted",
                lambda: _extract_adapter_keys(_dual_feed_context()),
            ))
    else:
        cases.append({
            "case": "feeds_extract_adapter_surface_exists",
            "status": "FAIL",
            "error": "_extract_adapter_surfaces missing",
        })

    empty_engine = _mk_features_engine({})
    empty_payload = empty_engine.build_payload(now_ns=1_000_000_000)
    empty_ff = empty_payload["family_features"]
    empty_statuses = empty_ff["provider_runtime"]

    cases.append({
        "case": "empty_provider_runtime_does_not_default_healthy",
        "status": "PASS"
        if empty_statuses["futures_provider_status"] != N.PROVIDER_STATUS_HEALTHY
        and empty_statuses["selected_option_provider_status"] != N.PROVIDER_STATUS_HEALTHY
        and empty_statuses["option_context_provider_status"] != N.PROVIDER_STATUS_HEALTHY
        else "FAIL",
        "provider_runtime": empty_statuses,
    })

    hashes_context_only = {
        N.HASH_STATE_DHAN_CONTEXT: {
            "provider_id": N.PROVIDER_DHAN,
            "context_status": N.PROVIDER_STATUS_UNAVAILABLE,
            "ts_event_ns": "999000000",
            "selected_call_instrument_key": "CALL",
            "strike_ladder": json.dumps([{"strike": 22500, "side": "CE"}]),
        }
    }
    context_only_payload = _mk_features_engine(hashes_context_only).build_payload(now_ns=1_000_000_000)
    context_only_ff = context_only_payload["family_features"]

    cases.append({
        "case": "dhan_context_alone_does_not_make_data_valid",
        "status": "PASS"
        if context_only_payload["frame_valid"] is False
        and context_only_ff["stage_flags"]["data_valid"] is False
        and context_only_ff["snapshot"]["valid"] is False
        else "FAIL",
        "frame_valid": context_only_payload["frame_valid"],
        "stage_flags": context_only_ff["stage_flags"],
        "snapshot": context_only_ff["snapshot"],
    })

    cases.append({
        "case": "unavailable_context_not_fresh_or_miso_ready",
        "status": "PASS"
        if context_only_ff["stage_flags"]["dhan_context_fresh"] is False
        and context_only_ff["stage_flags"]["provider_ready_miso"] is False
        and context_only_ff["families"][FE.FAMILY_MISO]["eligible"] is False
        else "FAIL",
        "stage_flags": context_only_ff["stage_flags"],
        "miso": context_only_ff["families"][FE.FAMILY_MISO],
    })

    active_hashes = {
        N.HASH_STATE_PROVIDER_RUNTIME: {
            "active_futures_provider_id": N.PROVIDER_DHAN,
            "active_selected_option_provider_id": N.PROVIDER_DHAN,
            "active_option_context_provider_id": N.PROVIDER_DHAN,
            "futures_provider_status": N.PROVIDER_STATUS_HEALTHY,
            "selected_option_provider_status": N.PROVIDER_STATUS_HEALTHY,
            "option_context_provider_status": N.PROVIDER_STATUS_UNAVAILABLE,
        },
        N.HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE: {
            "ltp": "22500",
            "bid": "22499",
            "ask": "22501",
            "ts_event_ns": "1000000000",
            "provider_id": N.PROVIDER_DHAN,
        },
        N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE: {
            "ltp": "100",
            "bid": "99",
            "ask": "101",
            "ts_event_ns": "1000000000",
            "provider_id": N.PROVIDER_DHAN,
            "option_side": N.SIDE_CALL,
            "instrument_key": "ACTIVE_CALL",
            "instrument_token": "ACTIVE_TOKEN",
        },
        N.HASH_STATE_DHAN_CONTEXT: {
            "provider_id": N.PROVIDER_DHAN,
            "context_status": N.PROVIDER_STATUS_UNAVAILABLE,
            "ts_event_ns": "1000000000",
            "selected_call_instrument_key": "CTX_CALL",
            "selected_call_option_token": "CTX_TOKEN",
            "strike_ladder": json.dumps([{"strike": 22500, "side": "CE"}]),
        },
    }

    active_payload = _mk_features_engine(active_hashes).build_payload(now_ns=1_000_000_000)
    active_ff = active_payload["family_features"]
    shared = active_payload["shared_core"]

    cases.append({
        "case": "active_marketdata_can_be_valid_but_unavailable_context_blocks_miso",
        "status": "PASS"
        if active_ff["stage_flags"]["data_valid"] is True
        and active_ff["stage_flags"]["dhan_context_fresh"] is False
        and active_ff["stage_flags"]["provider_ready_miso"] is False
        else "FAIL",
        "stage_flags": active_ff["stage_flags"],
        "miso": active_ff["families"][FE.FAMILY_MISO],
    })

    selected = shared["options"]["selected"]
    call = shared["options"]["call"]
    cases.append({
        "case": "active_option_marketdata_truth_not_overwritten_by_context",
        "status": "PASS"
        if str(call.get("instrument_token") or "") in {"ACTIVE_TOKEN", ""}
        and float(call.get("ltp") or selected.get("ltp") or 0.0) == 100.0
        else "FAIL",
        "selected": selected,
        "call": call,
    })

    unsynced_hashes = {
        N.HASH_STATE_PROVIDER_RUNTIME: {
            "active_futures_provider_id": N.PROVIDER_DHAN,
            "active_selected_option_provider_id": N.PROVIDER_DHAN,
            "active_option_context_provider_id": N.PROVIDER_DHAN,
            "futures_provider_status": N.PROVIDER_STATUS_HEALTHY,
            "selected_option_provider_status": N.PROVIDER_STATUS_HEALTHY,
            "option_context_provider_status": N.PROVIDER_STATUS_HEALTHY,
        },
        N.HASH_STATE_SNAPSHOT_MME_FUT_ACTIVE: {
            "ltp": "22500",
            "ts_event_ns": "1000000000",
            "provider_id": N.PROVIDER_DHAN,
        },
        N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED_ACTIVE: {
            "ltp": "100",
            "ts_event_ns": str(1_000_000_000 + (FE.DEFAULT_SYNC_MAX_MS + 100) * 1_000_000),
            "provider_id": N.PROVIDER_DHAN,
            "option_side": N.SIDE_CALL,
        },
    }
    unsynced_payload = _mk_features_engine(unsynced_hashes).build_payload(
        now_ns=1_000_000_000 + (FE.DEFAULT_SYNC_MAX_MS + 100) * 1_000_000
    )
    unsynced_ff = unsynced_payload["family_features"]
    cases.append({
        "case": "sync_span_above_threshold_invalidates_snapshot",
        "status": "PASS"
        if unsynced_ff["stage_flags"]["data_valid"] is False
        and unsynced_ff["snapshot"]["valid"] is False
        else "FAIL",
        "snapshot": unsynced_ff["snapshot"],
        "stage_flags": unsynced_ff["stage_flags"],
    })

    failed = [case for case in cases if case.get("status") != "PASS"]
    proof = {
        "proof": "feeds_features_batch7_freeze",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out = PROJECT_ROOT / "run" / "proofs" / "feeds_features_batch7_freeze.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True))
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
