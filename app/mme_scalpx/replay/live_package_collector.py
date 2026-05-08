from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.safety import assert_replay_artifact_path

OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_COLLECTION_VERSION = "observe_only_actual_evidence_map_collection_v1"

REQUIRED_ACTUAL_EVIDENCE_ITEMS = tuple([
    "provider_runtime",
    "feed_snapshot",
    "feature_payload",
    "family_surfaces",
    "strategy_activation",
    "no_order_sent",
    "live_capture_log",
    "live_stream_inventory",
    "live_hash_inventory",
    "provider_health_snapshot",
    "selected_option_context",
    "dhan_oi_ladder_context_if_available",
])

REQUIRED_COLLECTION_ARTIFACTS = tuple([
    "00_collection_manifest.json",
    "01_evidence_map_validation.json",
    "02_copied_evidence_index.json",
    "03_capture_completeness.json",
    "04_no_enablement_boundary.json",
    "05_reproducibility.json",
])


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_actual_evidence_map_collection_contract() -> dict[str, Any]:
    safety = {
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }
    boundary = {
        "paper_armed_readiness": "NOT_APPROVED_IN_28F",
        "live_trading_readiness": "NOT_APPROVED_IN_28F",
        "production_strategy_improvement_claim": "NOT_PROVEN_IN_28F",
        "production_doctrine_revision": "NOT_APPROVED_IN_28F",
        "full_live_replay_parity": "NOT_PROVEN_IN_28F",
    }
    contract = {
        "schema_version": OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_COLLECTION_VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "accepted_for": "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_PACKAGE_COLLECTION_ONLY",
        "actual_live_market_capture_started_by_28f": False,
        "collection_requires_actual_evidence_map": True,
        "collection_only_copies_existing_evidence_files": True,
        "required_actual_evidence_items": REQUIRED_ACTUAL_EVIDENCE_ITEMS,
        "required_collection_artifacts": REQUIRED_COLLECTION_ARTIFACTS,
        "safety_boundary": safety,
        "not_approved_or_not_proven_boundary": boundary,
    }
    contract["collection_contract_hash"] = replay_fingerprint({
        "schema_version": contract["schema_version"],
        "required_actual_evidence_items": contract["required_actual_evidence_items"],
        "required_collection_artifacts": contract["required_collection_artifacts"],
        "safety_boundary": safety,
        "boundary": boundary,
    })
    return contract


def validate_actual_evidence_map(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    if not path.is_file():
        return {
            "ok": False,
            "present": False,
            "reason": "actual_evidence_map_missing",
            "path": path_text,
            "missing_keys": REQUIRED_ACTUAL_EVIDENCE_ITEMS,
            "missing_files": tuple(),
        }

    data = json.loads(path.read_text(encoding="utf-8"))
    missing_keys = tuple(item for item in REQUIRED_ACTUAL_EVIDENCE_ITEMS if item not in data)
    missing_files = tuple(
        {"item": item, "path": str(data.get(item))}
        for item in REQUIRED_ACTUAL_EVIDENCE_ITEMS
        if item in data and not Path(str(data.get(item))).is_file()
    )
    ok = not missing_keys and not missing_files

    return {
        "ok": ok,
        "present": True,
        "path": path_text,
        "item_count": len(data),
        "missing_keys": missing_keys,
        "missing_files": missing_files,
        "evidence_paths": {str(k): str(v) for k, v in data.items()},
    }


def collect_actual_observe_only_evidence_package(
    *,
    capture_id: str,
    evidence_map: str,
    root: str,
    require_actual_map: bool = True,
) -> dict[str, Any]:
    artifact_root = Path(root)
    assert_replay_artifact_path(str(artifact_root / "00_collection_manifest.json"))
    artifact_root.mkdir(parents=True, exist_ok=True)

    contract = build_actual_evidence_map_collection_contract()
    validation = validate_actual_evidence_map(evidence_map)

    if require_actual_map and not validation.get("ok"):
        payloads = {
            "00_collection_manifest.json": {
                "schema_version": "observe_only_actual_collection_manifest_v1",
                "capture_id": capture_id,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "collection_deferred": True,
                "defer_reason": validation.get("reason", "actual_evidence_map_invalid_or_incomplete"),
                "actual_evidence_map": evidence_map,
                "accepted_for": "DEFERRED_ACTUAL_EVIDENCE_MAP_REQUIRED",
                **contract["safety_boundary"],
                **contract["not_approved_or_not_proven_boundary"],
            },
            "01_evidence_map_validation.json": validation,
            "02_copied_evidence_index.json": {
                "copied": {},
                "copied_count": 0,
                "deferred": True,
            },
            "03_capture_completeness.json": {
                "complete": False,
                "deferred": True,
                "missing_keys": validation.get("missing_keys", ()),
                "missing_files": validation.get("missing_files", ()),
            },
            "04_no_enablement_boundary.json": {
                **contract["safety_boundary"],
                **contract["not_approved_or_not_proven_boundary"],
            },
            "05_reproducibility.json": {
                "capture_id": capture_id,
                "actual_evidence_map": evidence_map,
                "collection_contract_hash": contract["collection_contract_hash"],
                "collection_deferred": True,
            },
        }
        for name, payload in payloads.items():
            (artifact_root / name).write_text(
                json.dumps(payload, indent=2, sort_keys=True, default=str),
                encoding="utf-8",
            )
        return {
            "schema_version": "observe_only_actual_evidence_package_collection_result_v1",
            "capture_id": capture_id,
            "artifact_root": str(artifact_root),
            "actual_evidence_map": evidence_map,
            "actual_evidence_map_present": validation.get("present") is True,
            "actual_evidence_map_valid": False,
            "actual_package_collected": False,
            "collection_deferred": True,
            "defer_reason": validation.get("reason", "actual_evidence_map_invalid_or_incomplete"),
            "written_artifacts": {name: str(artifact_root / name) for name in REQUIRED_COLLECTION_ARTIFACTS},
            "written_count": len(REQUIRED_COLLECTION_ARTIFACTS),
            "copied_count": 0,
            "accepted_for": "DEFERRED_ACTUAL_EVIDENCE_MAP_REQUIRED",
            **contract["safety_boundary"],
            **contract["not_approved_or_not_proven_boundary"],
        }

    evidence_paths = dict(validation.get("evidence_paths") or {})
    evidence_dir = artifact_root / "evidence_files"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    copied = {}
    for item in REQUIRED_ACTUAL_EVIDENCE_ITEMS:
        src = Path(str(evidence_paths[item]))
        suffix = src.suffix or ".artifact"
        dst = evidence_dir / (item + suffix)
        shutil.copy2(src, dst)
        copied[item] = {
            "source": str(src),
            "target": str(dst),
            "sha256": _sha256(dst),
            "size_bytes": dst.stat().st_size,
        }

    manifest = {
        "schema_version": "observe_only_actual_collection_manifest_v1",
        "capture_id": capture_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "collection_deferred": False,
        "actual_evidence_map": evidence_map,
        "actual_evidence_map_valid": True,
        "actual_package_collected": True,
        "accepted_for": "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_PACKAGE_COLLECTION_ONLY",
        **contract["safety_boundary"],
        **contract["not_approved_or_not_proven_boundary"],
    }

    payloads = {
        "00_collection_manifest.json": manifest,
        "01_evidence_map_validation.json": validation,
        "02_copied_evidence_index.json": {
            "copied": copied,
            "copied_count": len(copied),
            "deferred": False,
        },
        "03_capture_completeness.json": {
            "complete": len(copied) == len(REQUIRED_ACTUAL_EVIDENCE_ITEMS),
            "deferred": False,
            "missing_keys": tuple(),
            "missing_files": tuple(),
        },
        "04_no_enablement_boundary.json": {
            **contract["safety_boundary"],
            **contract["not_approved_or_not_proven_boundary"],
        },
        "05_reproducibility.json": {
            "capture_id": capture_id,
            "actual_evidence_map": evidence_map,
            "collection_contract_hash": contract["collection_contract_hash"],
            "collection_hash": replay_fingerprint({
                "capture_id": capture_id,
                "actual_evidence_map": evidence_map,
                "copied": copied,
            }),
            "collection_deferred": False,
        },
    }

    for name, payload in payloads.items():
        (artifact_root / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=str),
            encoding="utf-8",
        )

    return {
        "schema_version": "observe_only_actual_evidence_package_collection_result_v1",
        "capture_id": capture_id,
        "artifact_root": str(artifact_root),
        "actual_evidence_map": evidence_map,
        "actual_evidence_map_present": True,
        "actual_evidence_map_valid": True,
        "actual_package_collected": True,
        "collection_deferred": False,
        "written_artifacts": {name: str(artifact_root / name) for name in REQUIRED_COLLECTION_ARTIFACTS},
        "written_count": len(REQUIRED_COLLECTION_ARTIFACTS),
        "copied_count": len(copied),
        "accepted_for": "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_PACKAGE_COLLECTION_ONLY",
        **contract["safety_boundary"],
        **contract["not_approved_or_not_proven_boundary"],
    }


def validate_actual_observe_only_evidence_package_result(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("artifact_root")))
    written = dict(result.get("written_artifacts") or {})
    missing_artifacts = tuple(
        name for name in REQUIRED_COLLECTION_ARTIFACTS
        if name not in written or not Path(str(written[name])).is_file()
    )
    safety_ok = (
        result.get("starts_services") is False
        and result.get("reads_live_redis") is False
        and result.get("writes_live_redis") is False
        and result.get("calls_broker_api") is False
        and result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("execution_arming_created") is False
        and result.get("real_order_sent") is False
        and result.get("broker_calls_executed") is False
        and result.get("live_redis_writes_executed") is False
        and result.get("production_doctrine_changed") is False
        and result.get("full_live_replay_parity") == "NOT_PROVEN_IN_28F"
    )
    root_ok = str(root).startswith("run/replay") or "/run/replay/" in str(root)
    deferred = result.get("collection_deferred") is True
    collected = result.get("actual_package_collected") is True
    ok = not missing_artifacts and root_ok and safety_ok and (deferred or collected)
    return {
        "ok": bool(ok),
        "root_ok": root_ok,
        "safety_ok": safety_ok,
        "collection_deferred": deferred,
        "actual_package_collected": collected,
        "missing_artifacts": missing_artifacts,
    }


__all__ = tuple([
    "OBSERVE_ONLY_ACTUAL_EVIDENCE_MAP_COLLECTION_VERSION",
    "REQUIRED_ACTUAL_EVIDENCE_ITEMS",
    "REQUIRED_COLLECTION_ARTIFACTS",
    "build_actual_evidence_map_collection_contract",
    "validate_actual_evidence_map",
    "collect_actual_observe_only_evidence_package",
    "validate_actual_observe_only_evidence_package_result",
])
