#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
PROOF_DIR = ROOT / "run" / "proofs"

FINAL_MAP = ROOT / "etc" / "replay" / "parity" / "observe_only_actual_generated_evidence_map.json"
PROOF_28F_LATEST = PROOF_DIR / "proof_observe_only_market_session_package_collection_28f_latest.json"
PROOF_28F_R4_LATEST = PROOF_DIR / "proof_observe_only_market_session_package_collection_28f_r4_replay_safe_root_from_final_map_latest.json"

MANIFEST = ROOT / "etc" / "replay" / "parity" / "observe_only_replay_live_parity_manifest_28i.json"
PROOF_MAIN = PROOF_DIR / "proof_observe_only_replay_live_parity_manifest_28i.json"
PROOF_LATEST = PROOF_DIR / "proof_observe_only_replay_live_parity_manifest_28i_latest.json"

EXPECTED_LIVE_EVIDENCE_KEYS = [
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
]

REQUIRED_COLLECTION_ARTIFACTS = [
    "00_collection_manifest.json",
    "01_evidence_map_validation.json",
    "02_copied_evidence_index.json",
    "03_capture_completeness.json",
    "04_no_enablement_boundary.json",
    "05_reproducibility.json",
]

COMPARISON_DIMENSIONS = [
    {
        "dimension": "package_integrity",
        "live_source": "closed 28F package hashes and copied evidence index",
        "replay_source_required": "same package read-only input validation",
        "required_result": "all expected files present and hashes stable",
        "status": "MANIFESTED_NOT_COMPARED",
    },
    {
        "dimension": "provider_runtime_boundary",
        "live_source": "provider_runtime.json and provider_health_snapshot.json",
        "replay_source_required": "replay runtime input surface derived from package only",
        "required_result": "replay must not require live provider access and must preserve observe_only provider facts",
        "status": "MANIFESTED_NOT_COMPARED",
    },
    {
        "dimension": "feed_snapshot_surface",
        "live_source": "feed_snapshot.json, live_stream_inventory.json, live_hash_inventory.json",
        "replay_source_required": "replay dataset/feed reconstruction preflight",
        "required_result": "replay input coverage must match captured live surface inventory",
        "status": "MANIFESTED_NOT_COMPARED",
    },
    {
        "dimension": "feature_payload_surface",
        "live_source": "feature_payload.json",
        "replay_source_required": "replay-generated feature payload from captured evidence",
        "required_result": "feature keys, family_features, family_surfaces, side separation, and canonical fields must be comparable",
        "status": "MANIFESTED_NOT_COMPARED",
    },
    {
        "dimension": "strategy_activation_surface",
        "live_source": "strategy_activation.json and family_surfaces.json",
        "replay_source_required": "replay strategy activation/report-only output",
        "required_result": "five-family activation shape must be comparable and replay must remain HOLD/report-only unless explicitly proven otherwise",
        "status": "MANIFESTED_NOT_COMPARED",
    },
    {
        "dimension": "no_order_boundary",
        "live_source": "no_order_sent.json and 04_no_enablement_boundary.json",
        "replay_source_required": "replay execution-shadow/no-order proof",
        "required_result": "no real order, no broker call, no live Redis write, no runtime promotion",
        "status": "MANIFESTED_NOT_COMPARED",
    },
    {
        "dimension": "miso_context_boundary",
        "live_source": "selected_option_context.json and dhan_oi_ladder_context_if_available.json",
        "replay_source_required": "replay context-consumption evidence only",
        "required_result": "Dhan/OI context remains selection/evidence context only; no live trigger or production promotion claim",
        "status": "MANIFESTED_NOT_COMPARED",
    },
    {
        "dimension": "parity_verdict",
        "live_source": "closed observe_only package",
        "replay_source_required": "future replay run output",
        "required_result": "parity may only be marked proven after replay outputs are generated and compared",
        "status": "NOT_PROVEN_IN_28I",
    },
]

def sha256_file(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "_read_error": type(exc).__name__,
            "_read_error_text": str(exc),
            "_path": str(path),
        }

def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)

def file_state(path: pathlib.Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "present": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256_file(path),
    }

def dir_file_states(path: pathlib.Path) -> dict[str, Any]:
    files = []
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file():
                files.append(file_state(child))
    return {
        "path": rel(path),
        "present": path.exists(),
        "is_dir": path.is_dir(),
        "file_count": len(files),
        "files": files,
    }

def looks_like_project_path(value: Any) -> bool:
    return isinstance(value, str) and (
        value.startswith("run/")
        or value.startswith("etc/")
        or value.startswith("docs/")
        or value.startswith("reports/")
        or value.startswith("data/")
        or value.startswith("var/")
    )

def normalize_evidence_map(obj: dict[str, Any]) -> tuple[dict[str, str], str]:
    if not isinstance(obj, dict):
        return {}, "not_dict"
    for key in ("evidence", "evidence_map", "artifacts", "files"):
        nested = obj.get(key)
        if isinstance(nested, dict):
            out = {str(k): str(v) for k, v in nested.items() if looks_like_project_path(v)}
            if out:
                return out, f"nested_{key}"
    direct = {str(k): str(v) for k, v in obj.items() if looks_like_project_path(v)}
    if direct:
        return direct, "direct_top_level_path_map"
    return {}, "unknown"

proof_28f = read_json(PROOF_28F_LATEST)
proof_28f_r4 = read_json(PROOF_28F_R4_LATEST)
final_map = read_json(FINAL_MAP)
evidence_map, evidence_map_shape = normalize_evidence_map(final_map)

capture_id = proof_28f.get("capture_id") or proof_28f_r4.get("capture_id")
artifact_root_raw = proof_28f.get("artifact_root") or proof_28f_r4.get("artifact_root")
artifact_root = ROOT / artifact_root_raw if artifact_root_raw else None

closed_28f_ok = (
    proof_28f.get("observe_only_market_session_package_collection_28f_ok") is True
    and proof_28f.get("actual_package_collected") is True
    and proof_28f.get("collection_deferred") is False
    and proof_28f.get("paper_armed_approved") is False
    and proof_28f.get("live_trading_approved") is False
)

artifact_root_safe = bool(
    artifact_root
    and artifact_root.exists()
    and str(artifact_root.resolve()).startswith(str((ROOT / "run" / "replay").resolve()) + "/")
)

package_artifact_states = {}
if artifact_root:
    for name in REQUIRED_COLLECTION_ARTIFACTS:
        package_artifact_states[name] = file_state(artifact_root / name)

copied_evidence_dir = artifact_root / "evidence_files" if artifact_root else None
copied_evidence_states = {}
if copied_evidence_dir:
    for key in EXPECTED_LIVE_EVIDENCE_KEYS:
        candidates = [
            copied_evidence_dir / f"{key}.json",
            copied_evidence_dir / f"{key}.log",
        ]
        found = next((p for p in candidates if p.is_file()), candidates[0])
        copied_evidence_states[key] = file_state(found)

source_evidence_states = {
    key: file_state(ROOT / path)
    for key, path in evidence_map.items()
}

missing_source_keys = sorted(set(EXPECTED_LIVE_EVIDENCE_KEYS) - set(evidence_map.keys()))
missing_copied_keys = [
    key
    for key, state in copied_evidence_states.items()
    if not state.get("present")
]
missing_package_artifacts = [
    key
    for key, state in package_artifact_states.items()
    if not state.get("present")
]

manifest_ready = (
    closed_28f_ok
    and artifact_root_safe
    and not missing_source_keys
    and not missing_copied_keys
    and not missing_package_artifacts
)

manifest = {
    "schema_version": "observe_only_replay_live_parity_manifest_28i_v1",
    "batch": "28I",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "accepted_for": "REPLAY_LIVE_PARITY_COMPARISON_MANIFEST_ONLY",
    "manifest_ready": bool(manifest_ready),

    "capture_id": capture_id,
    "artifact_root": rel(artifact_root) if artifact_root else None,
    "artifact_root_replay_safe": bool(artifact_root_safe),

    "source_final_evidence_map": rel(FINAL_MAP),
    "source_final_evidence_map_sha256": sha256_file(FINAL_MAP),
    "source_final_evidence_map_shape": evidence_map_shape,
    "source_evidence_count": len(evidence_map),
    "source_evidence_states": source_evidence_states,

    "closed_package_proof": rel(PROOF_28F_LATEST),
    "closed_package_proof_sha256": sha256_file(PROOF_28F_LATEST),
    "closed_28f_ok": bool(closed_28f_ok),

    "package_artifact_states": package_artifact_states,
    "copied_evidence_states": copied_evidence_states,

    "missing_source_keys": missing_source_keys,
    "missing_copied_keys": missing_copied_keys,
    "missing_package_artifacts": missing_package_artifacts,

    "comparison_dimensions": COMPARISON_DIMENSIONS,

    "replay_inputs_required_next": {
        "read_only_live_package_root": rel(artifact_root) if artifact_root else None,
        "dataset_materialization_required": True,
        "replay_run_required": True,
        "replay_output_required": True,
        "comparison_report_required": True,
        "allowed_runtime_mode": "observe_only_or_offline_replay_only",
        "forbidden": [
            "paper_armed approval",
            "live trading approval",
            "broker API call",
            "live Redis write",
            "runtime promotion",
            "production doctrine mutation",
        ],
    },

    "parity_status": {
        "package_closed": bool(closed_28f_ok),
        "manifest_built": bool(manifest_ready),
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28I",
    },

    "starts_services": False,
    "reads_live_redis": False,
    "writes_live_redis": False,
    "calls_broker_api": False,
    "broker_call_reachable": False,
    "live_redis_write_reachable": False,
    "runtime_promotion_reachable": False,
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "real_order_sent": False,
    "broker_calls_executed": False,
    "live_redis_writes_executed": False,
    "production_doctrine_changed": False,

    "paper_armed_readiness": "NOT_APPROVED_IN_28I",
    "live_trading_readiness": "NOT_APPROVED_IN_28I",
    "production_strategy_improvement_claim": "NOT_PROVEN_IN_28I",
    "production_doctrine_revision": "NOT_APPROVED_IN_28I",
    "full_live_replay_parity": "NOT_PROVEN_IN_28I",

    "next_batch": "Batch 28J — materialize a replay input/dataset preflight from the closed observe_only package, still not paper/live enablement.",
}

write_json(MANIFEST, manifest)

proof = {
    "schema_version": "proof_observe_only_replay_live_parity_manifest_28i_v1",
    "batch": "28I",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "accepted_for": "REPLAY_LIVE_PARITY_COMPARISON_MANIFEST_ONLY",
    "verdict": "PASS_OBSERVE_ONLY_REPLAY_LIVE_PARITY_MANIFEST_28I" if manifest_ready else "FAIL_OBSERVE_ONLY_REPLAY_LIVE_PARITY_MANIFEST_28I",
    "observe_only_replay_live_parity_manifest_28i_ok": bool(manifest_ready),
    "manifest": rel(MANIFEST),
    "manifest_sha256": sha256_file(MANIFEST),
    "closed_28f_ok": bool(closed_28f_ok),
    "artifact_root_replay_safe": bool(artifact_root_safe),
    "source_evidence_count": len(evidence_map),
    "missing_source_keys": missing_source_keys,
    "missing_copied_keys": missing_copied_keys,
    "missing_package_artifacts": missing_package_artifacts,

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
    "full_live_replay_parity": "NOT_PROVEN_IN_28I",

    "next_batch": manifest["next_batch"],
}

write_json(PROOF_MAIN, proof)
write_json(PROOF_LATEST, proof)
print(json.dumps(proof, indent=2, sort_keys=True))

raise SystemExit(0 if manifest_ready else 1)
