#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


EXPECTED_CONTRACT_FILES = [
    "etc/replay/datasets/replay_live_surface_contract_v2.json",
    "etc/replay/datasets/replay_dhan_context_contract_v1.json",
    "etc/replay/datasets/replay_oi_ladder_contract_v1.json",
    "etc/replay/datasets/replay_provider_runtime_contract_v1.json",
    "etc/replay/datasets/replay_dataset_contract_manifest_v1.json",
]

EXPECTED_SURFACES = [
    "futures",
    "selected_option",
    "dhan_context",
    "oi_ladder",
    "provider_runtime",
    "call_put_separation",
    "miso_readiness",
]

REQUIRED_SENTINEL_FIELDS = {
    "futures": [
        "fut_ltp",
        "fut_best_bid",
        "fut_best_ask",
        "fut_bid_qty_1",
        "fut_ask_qty_1",
        "fut_volume",
        "fut_local_ts",
        "fut_vwap",
        "fut_ema_9",
        "fut_ema_21",
    ],
    "selected_option": [
        "selected_option_provider",
        "branch_side",
        "side",
        "option_type",
        "security_id",
        "tradingsymbol",
        "expiry",
        "strike",
        "opt_ltp",
        "opt_best_bid",
        "opt_best_ask",
        "opt_bid_qty_1",
        "opt_ask_qty_1",
        "opt_volume",
        "opt_local_ts",
        "ce_ltp",
        "pe_ltp",
        "ce_strike",
        "pe_strike",
    ],
    "dhan_context": [
        "dhan_context_ts_ns",
        "dhan_context_age_ms",
        "chain_context_fresh",
        "strike_score",
        "iv",
        "iv_change",
        "oi",
        "oi_change",
        "delta",
        "gamma",
        "theta",
        "vega",
        "cross_strike_spread_rank",
        "cross_strike_volume_rank",
    ],
    "oi_ladder": [
        "call_oi_ladder_json",
        "put_oi_ladder_json",
        "nearest_call_wall",
        "nearest_put_wall",
        "oi_wall_distance_points",
        "oi_wall_strength",
        "oi_support_resistance_bias",
        "oi_wall_blocking_side",
        "production_doctrine_changed",
    ],
    "provider_runtime": [
        "futures_provider",
        "selected_option_provider",
        "option_context_provider",
        "execution_provider",
        "fallback_execution_provider",
        "zerodha_ready",
        "dhan_ready",
        "dhan_context_ready",
        "provider_ready_miso",
        "provider_mode",
        "provider_degraded_reason",
    ],
    "call_put_separation": [
        "branch_side",
        "side",
        "option_type",
        "ce_ltp",
        "pe_ltp",
        "ce_strike",
        "pe_strike",
        "ce_local_ts",
        "pe_local_ts",
    ],
    "miso_readiness": [
        "provider_ready_miso",
        "dhan_context_ts_ns",
        "chain_context_fresh",
        "selected_security_id",
        "burst_event_id",
        "oi_context_fresh",
        "call_oi_ladder_json",
        "put_oi_ladder_json",
        "nearest_call_wall",
        "nearest_put_wall",
        "oi_wall_strength",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="run/proofs/proof_replay_dataset_manifest.json")
    args = parser.parse_args()

    file_results = []
    json_ok = True
    for rel_path in EXPECTED_CONTRACT_FILES:
        path = ROOT / rel_path
        row = {
            "path": rel_path,
            "exists": path.exists(),
            "sha256": sha256_file(path),
            "json_ok": False,
            "schema_version": None,
            "error": None,
        }
        if not path.exists():
            json_ok = False
            row["error"] = "missing"
        else:
            try:
                payload = load_json(path)
                row["json_ok"] = True
                row["schema_version"] = payload.get("schema_version")
            except Exception as exc:  # noqa: BLE001
                json_ok = False
                row["error"] = f"{type(exc).__name__}: {exc}"
        file_results.append(row)

    contracts_mod = importlib.import_module("app.mme_scalpx.replay.contracts")
    dataset_mod = importlib.import_module("app.mme_scalpx.replay.dataset")
    safety_mod = importlib.import_module("app.mme_scalpx.replay.safety")

    contract_summary = contracts_mod.replay_dataset_contract_summary()
    required_surfaces = contracts_mod.replay_required_dataset_fields()

    surface_results = {}
    all_surfaces_ok = True
    for surface in EXPECTED_SURFACES:
        fields = tuple(required_surfaces.get(surface, ()))
        missing_sentinels = tuple(
            field for field in REQUIRED_SENTINEL_FIELDS[surface]
            if field not in fields
        )
        surface_ok = not missing_sentinels
        all_surfaces_ok = all_surfaces_ok and surface_ok
        surface_results[surface] = {
            "field_count": len(fields),
            "sentinel_required": REQUIRED_SENTINEL_FIELDS[surface],
            "missing_sentinels": missing_sentinels,
            "ok": surface_ok,
        }

    dataset_helpers_ok = all(
        hasattr(dataset_mod, name)
        for name in [
            "replay_dataset_required_fields",
            "replay_dataset_all_required_fields",
            "validate_replay_dataset_row",
        ]
    )

    validation_smoke = {}
    for surface in EXPECTED_SURFACES:
        fields = tuple(required_surfaces[surface])
        row = {field: None for field in fields}
        result = dataset_mod.validate_replay_dataset_row(row, surface=surface)
        validation_smoke[surface] = result

    validation_smoke_ok = all(item.get("ok") is True for item in validation_smoke.values())

    # Safety guard smoke checks.
    safety_checks = {
        "artifact_root_rejects_live_path": False,
        "config_root_rejects_live_path": False,
        "replay_key_accepts_replay_prefix": False,
        "runtime_blocks_paper_armed": False,
        "runtime_blocks_live": False,
    }

    try:
        safety_mod.assert_replay_artifact_path("run/live_capture/not_replay.json")
    except Exception:
        safety_checks["artifact_root_rejects_live_path"] = True

    try:
        safety_mod.assert_replay_config_path("etc/strategy_family/family_runtime.yaml")
    except Exception:
        safety_checks["config_root_rejects_live_path"] = True

    try:
        safety_mod.assert_replay_key("replay:dataset:test")
        safety_checks["replay_key_accepts_replay_prefix"] = True
    except Exception:
        pass

    try:
        safety_mod.assert_runtime_mode_not_promoted("paper_armed")
    except Exception:
        safety_checks["runtime_blocks_paper_armed"] = True

    try:
        safety_mod.assert_runtime_mode_not_promoted("live")
    except Exception:
        safety_checks["runtime_blocks_live"] = True

    safety_smoke_ok = all(safety_checks.values())

    manifest_path = ROOT / "etc/replay/datasets/replay_dataset_contract_manifest_v1.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    manifest_laws = manifest.get("laws", {})

    no_approval_ok = (
        manifest_laws.get("paper_armed_approved") is False
        and manifest_laws.get("live_trading_approved") is False
        and manifest_laws.get("execution_arming_created") is False
        and manifest_laws.get("broker_calls_allowed") is False
        and manifest_laws.get("live_redis_writes_allowed") is False
        and manifest_laws.get("production_doctrine_changed") is False
    )

    firewall_latest = ROOT / "run/proofs/proof_replay_safety_firewall_latest.json"
    firewall_ok = False
    firewall_summary = {"exists": firewall_latest.exists()}
    if firewall_latest.exists():
        fw = load_json(firewall_latest)
        firewall_summary.update({
            "verdict": fw.get("verdict"),
            "replay_safety_firewall_ok": fw.get("replay_safety_firewall_ok"),
            "broker_call_reachable": fw.get("broker_call_reachable"),
            "live_redis_write_reachable": fw.get("live_redis_write_reachable"),
            "runtime_promotion_reachable": fw.get("runtime_promotion_reachable"),
        })
        firewall_ok = (
            fw.get("verdict") == "PASS_REPLAY_SAFETY_FIREWALL"
            and fw.get("replay_safety_firewall_ok") is True
            and fw.get("broker_call_reachable") is False
            and fw.get("live_redis_write_reachable") is False
            and fw.get("runtime_promotion_reachable") is False
        )

    dataset_contract_ok = bool(
        json_ok
        and all_surfaces_ok
        and dataset_helpers_ok
        and validation_smoke_ok
        and safety_smoke_ok
        and no_approval_ok
        and firewall_ok
    )

    proof = {
        "schema_version": "proof_replay_dataset_manifest_v1",
        "generated_at_utc": utc_now(),
        "batch": "27D",
        "dataset_contract_ok": dataset_contract_ok,
        "contract_files_ok": json_ok,
        "all_required_surfaces_present": all_surfaces_ok,
        "dataset_helpers_ok": dataset_helpers_ok,
        "validation_smoke_ok": validation_smoke_ok,
        "safety_smoke_ok": safety_smoke_ok,
        "no_approval_or_doctrine_mutation_ok": no_approval_ok,
        "firewall_prerequisite_ok": firewall_ok,
        "futures_surface_ok": surface_results["futures"]["ok"],
        "selected_option_surface_ok": surface_results["selected_option"]["ok"],
        "dhan_context_surface_ok": surface_results["dhan_context"]["ok"],
        "oi_ladder_surface_ok": surface_results["oi_ladder"]["ok"],
        "provider_runtime_surface_ok": surface_results["provider_runtime"]["ok"],
        "call_put_separation_surface_ok": surface_results["call_put_separation"]["ok"],
        "miso_readiness_surface_ok": surface_results["miso_readiness"]["ok"],
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "contract_summary": contract_summary,
        "contract_file_results": file_results,
        "surface_results": surface_results,
        "validation_smoke": validation_smoke,
        "safety_checks": safety_checks,
        "firewall_summary": firewall_summary,
        "verdict": "PASS_REPLAY_DATASET_CONTRACT_EXPANSION" if dataset_contract_ok else "FAIL_REVIEW_REQUIRED",
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    latest = ROOT / "run/proofs/proof_replay_dataset_contract_expansion_latest.json"
    latest.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "verdict": proof["verdict"],
        "dataset_contract_ok": proof["dataset_contract_ok"],
        "futures_surface_ok": proof["futures_surface_ok"],
        "selected_option_surface_ok": proof["selected_option_surface_ok"],
        "dhan_context_surface_ok": proof["dhan_context_surface_ok"],
        "oi_ladder_surface_ok": proof["oi_ladder_surface_ok"],
        "provider_runtime_surface_ok": proof["provider_runtime_surface_ok"],
        "call_put_separation_surface_ok": proof["call_put_separation_surface_ok"],
        "miso_readiness_surface_ok": proof["miso_readiness_surface_ok"],
        "paper_armed_approved": proof["paper_armed_approved"],
        "live_trading_approved": proof["live_trading_approved"],
        "proof": str(out),
        "latest": str(latest),
    }, indent=2, sort_keys=True))

    return 0 if dataset_contract_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
