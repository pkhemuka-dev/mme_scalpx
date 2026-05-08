#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
PROOF_DIR = ROOT / "run" / "proofs"

MANIFEST_28I = ROOT / "etc" / "replay" / "parity" / "observe_only_replay_live_parity_manifest_28i.json"
FINAL_MAP = ROOT / "etc" / "replay" / "parity" / "observe_only_actual_generated_evidence_map.json"

PROOF_28I_LATEST = PROOF_DIR / "proof_observe_only_replay_live_parity_manifest_28i_latest.json"
PROOF_28F_LATEST = PROOF_DIR / "proof_observe_only_market_session_package_collection_28f_latest.json"
PROOF_28F_R4_LATEST = PROOF_DIR / "proof_observe_only_market_session_package_collection_28f_r4_replay_safe_root_from_final_map_latest.json"

PREFLIGHT_MANIFEST = ROOT / "etc" / "replay" / "parity" / "observe_only_replay_input_dataset_preflight_28j.json"
PROOF_MAIN = PROOF_DIR / "proof_observe_only_replay_input_dataset_preflight_28j.json"
PROOF_LATEST = PROOF_DIR / "proof_observe_only_replay_input_dataset_preflight_28j_latest.json"

EXPECTED_EVIDENCE_KEYS = [
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

PREFLIGHT_ARTIFACTS = [
    "00_replay_input_preflight_manifest.json",
    "01_live_package_integrity_index.json",
    "02_replay_input_requirements.json",
    "03_no_enablement_boundary.json",
    "04_materialization_readiness.json",
]

def rel(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)

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
            "_path": rel(path),
        }

def write_json(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    tmp.replace(path)

def file_state(path: pathlib.Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "present": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256_file(path),
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

def resolve_package_root(manifest_28i: dict[str, Any], proof_28f: dict[str, Any], proof_28f_r4: dict[str, Any]) -> tuple[pathlib.Path | None, str | None]:
    req = manifest_28i.get("replay_inputs_required_next")
    if isinstance(req, dict):
        raw = req.get("read_only_live_package_root")
        if isinstance(raw, str) and raw:
            return (ROOT / raw if not pathlib.Path(raw).is_absolute() else pathlib.Path(raw)), "manifest_28i.replay_inputs_required_next.read_only_live_package_root"

    for source_name, payload in (
        ("manifest_28i.artifact_root", manifest_28i),
        ("proof_28f.artifact_root", proof_28f),
        ("proof_28f_r4.artifact_root", proof_28f_r4),
    ):
        raw = payload.get("artifact_root")
        if isinstance(raw, str) and raw:
            return (ROOT / raw if not pathlib.Path(raw).is_absolute() else pathlib.Path(raw)), source_name

    return None, None

def copied_evidence_path(package_root: pathlib.Path, key: str) -> pathlib.Path:
    evidence_dir = package_root / "evidence_files"
    for suffix in (".json", ".log", ".txt", ".csv"):
        candidate = evidence_dir / f"{key}{suffix}"
        if candidate.is_file():
            return candidate
    return evidence_dir / f"{key}.json"

manifest_28i = read_json(MANIFEST_28I)
proof_28i = read_json(PROOF_28I_LATEST)
proof_28f = read_json(PROOF_28F_LATEST)
proof_28f_r4 = read_json(PROOF_28F_R4_LATEST)
final_map = read_json(FINAL_MAP)

evidence_map, evidence_map_shape = normalize_evidence_map(final_map)
package_root, package_root_source = resolve_package_root(manifest_28i, proof_28f, proof_28f_r4)

capture_id = (
    manifest_28i.get("capture_id")
    or proof_28f.get("capture_id")
    or proof_28f_r4.get("capture_id")
    or (package_root.name if package_root else None)
)

package_root_safe = bool(
    package_root
    and package_root.exists()
    and str(package_root.resolve()).startswith(str((ROOT / "run" / "replay").resolve()) + "/")
)

preflight_root = ROOT / "run" / "replay" / "parity" / "dataset_preflight" / str(capture_id or "unknown_capture")
preflight_root_safe = str(preflight_root.resolve()).startswith(str((ROOT / "run" / "replay").resolve()) + "/")

source_evidence_states = {
    key: file_state(ROOT / path)
    for key, path in evidence_map.items()
}

package_artifact_states = {}
if package_root:
    package_artifact_states = {
        name: file_state(package_root / name)
        for name in REQUIRED_COLLECTION_ARTIFACTS
    }

copied_evidence_states = {}
source_copy_hash_checks = {}
if package_root:
    for key in EXPECTED_EVIDENCE_KEYS:
        copied = copied_evidence_path(package_root, key)
        copied_state = file_state(copied)
        copied_evidence_states[key] = copied_state

        source_path_raw = evidence_map.get(key)
        source = ROOT / source_path_raw if source_path_raw else None
        source_state = file_state(source) if source else {
            "path": None,
            "present": False,
            "size_bytes": 0,
            "sha256": None,
        }

        source_copy_hash_checks[key] = {
            "source": source_state,
            "copied": copied_state,
            "hash_match": bool(source_state.get("present") and copied_state.get("present") and source_state.get("sha256") == copied_state.get("sha256")),
        }

missing_source_keys = sorted(set(EXPECTED_EVIDENCE_KEYS) - set(evidence_map.keys()))
missing_source_files = sorted(key for key, state in source_evidence_states.items() if not state.get("present"))
missing_package_artifacts = sorted(key for key, state in package_artifact_states.items() if not state.get("present"))
missing_copied_evidence = sorted(key for key, state in copied_evidence_states.items() if not state.get("present"))
hash_mismatch_keys = sorted(key for key, state in source_copy_hash_checks.items() if not state.get("hash_match"))

closed_28f_ok = (
    proof_28f.get("observe_only_market_session_package_collection_28f_ok") is True
    and proof_28f.get("actual_package_collected") is True
    and proof_28f.get("collection_deferred") is False
    and proof_28f.get("paper_armed_approved") is False
    and proof_28f.get("live_trading_approved") is False
)

manifest_28i_ok = (
    manifest_28i.get("manifest_ready") is True
    and manifest_28i.get("closed_28f_ok") is True
    and manifest_28i.get("full_live_replay_parity") == "NOT_PROVEN_IN_28I"
)

package_integrity_ok = (
    package_root_safe
    and not missing_source_keys
    and not missing_source_files
    and not missing_package_artifacts
    and not missing_copied_evidence
    and not hash_mismatch_keys
)

dataset_preflight_ready = bool(
    manifest_28i_ok
    and closed_28f_ok
    and package_integrity_ok
    and preflight_root_safe
)

package_sha_material = {
    "final_map_sha256": sha256_file(FINAL_MAP),
    "package_manifest_sha256": sha256_file(package_root / "00_collection_manifest.json") if package_root else None,
    "copied_index_sha256": sha256_file(package_root / "02_copied_evidence_index.json") if package_root else None,
}
dataset_id_source = json.dumps(package_sha_material, sort_keys=True)
dataset_id = "observe_only_replay_input_" + hashlib.sha256(dataset_id_source.encode("utf-8")).hexdigest()[:16]

preflight_root.mkdir(parents=True, exist_ok=True)

preflight_manifest = {
    "schema_version": "observe_only_replay_input_dataset_preflight_28j_v1",
    "batch": "28J",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "accepted_for": "REPLAY_INPUT_DATASET_PREFLIGHT_ONLY",
    "dataset_id": dataset_id,
    "capture_id": capture_id,
    "dataset_preflight_ready": bool(dataset_preflight_ready),

    "source_manifest_28i": rel(MANIFEST_28I),
    "source_manifest_28i_sha256": sha256_file(MANIFEST_28I),
    "manifest_28i_ok": bool(manifest_28i_ok),

    "closed_package_proof": rel(PROOF_28F_LATEST),
    "closed_package_proof_sha256": sha256_file(PROOF_28F_LATEST),
    "closed_28f_ok": bool(closed_28f_ok),

    "final_evidence_map": rel(FINAL_MAP),
    "final_evidence_map_sha256": sha256_file(FINAL_MAP),
    "final_evidence_map_shape": evidence_map_shape,
    "source_evidence_count": len(evidence_map),

    "package_root": rel(package_root) if package_root else None,
    "package_root_source": package_root_source,
    "package_root_replay_safe": bool(package_root_safe),

    "preflight_root": rel(preflight_root),
    "preflight_root_replay_safe": bool(preflight_root_safe),

    "source_evidence_states": source_evidence_states,
    "copied_evidence_states": copied_evidence_states,
    "package_artifact_states": package_artifact_states,
    "source_copy_hash_checks": source_copy_hash_checks,

    "missing_source_keys": missing_source_keys,
    "missing_source_files": missing_source_files,
    "missing_package_artifacts": missing_package_artifacts,
    "missing_copied_evidence": missing_copied_evidence,
    "hash_mismatch_keys": hash_mismatch_keys,

    "materialization_status": {
        "dataset_materialized": False,
        "dataset_preflight_ready": bool(dataset_preflight_ready),
        "replay_run_completed": False,
        "comparison_completed": False,
        "full_live_replay_parity": "NOT_PROVEN_IN_28J",
    },

    "next_required_replay_inputs": {
        "read_only_package_root": rel(package_root) if package_root else None,
        "preflight_root": rel(preflight_root),
        "dataset_id": dataset_id,
        "required_mode": "offline_replay_input_materialization_only",
        "forbidden": [
            "paper_armed approval",
            "live trading approval",
            "broker API call",
            "live Redis write",
            "runtime promotion",
            "production doctrine mutation",
            "claiming replay/live parity",
        ],
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

    "paper_armed_readiness": "NOT_APPROVED_IN_28J",
    "live_trading_readiness": "NOT_APPROVED_IN_28J",
    "production_strategy_improvement_claim": "NOT_PROVEN_IN_28J",
    "production_doctrine_revision": "NOT_APPROVED_IN_28J",
    "full_live_replay_parity": "NOT_PROVEN_IN_28J",

    "next_batch": "Batch 28K — build offline replay materialization harness from the 28J preflight, still not paper/live enablement.",
}

write_json(preflight_root / "00_replay_input_preflight_manifest.json", preflight_manifest)

package_integrity_index = {
    "schema_version": "observe_only_package_integrity_index_28j_v1",
    "dataset_id": dataset_id,
    "package_root": rel(package_root) if package_root else None,
    "package_artifact_states": package_artifact_states,
    "copied_evidence_states": copied_evidence_states,
    "source_copy_hash_checks": source_copy_hash_checks,
    "package_integrity_ok": bool(package_integrity_ok),
}
write_json(preflight_root / "01_live_package_integrity_index.json", package_integrity_index)

requirements = {
    "schema_version": "observe_only_replay_input_requirements_28j_v1",
    "dataset_id": dataset_id,
    "required_future_batch": "28K",
    "required_inputs": {
        "package_root": rel(package_root) if package_root else None,
        "preflight_manifest": rel(preflight_root / "00_replay_input_preflight_manifest.json"),
        "integrity_index": rel(preflight_root / "01_live_package_integrity_index.json"),
        "final_evidence_map": rel(FINAL_MAP),
        "closed_package_proof": rel(PROOF_28F_LATEST),
    },
    "required_outputs_for_future_replay": [
        "offline replay materialization manifest",
        "dataset coverage report",
        "service-surface replay feasibility report",
        "no-broker/no-live-redis proof",
    ],
    "not_allowed_in_28J": [
        "running replay",
        "starting services",
        "reading live Redis",
        "writing live Redis",
        "calling broker APIs",
        "approving paper_armed",
        "approving live trading",
    ],
}
write_json(preflight_root / "02_replay_input_requirements.json", requirements)

no_enablement = {
    "schema_version": "observe_only_replay_input_no_enablement_boundary_28j_v1",
    "dataset_id": dataset_id,
    "starts_services": False,
    "reads_live_redis": False,
    "writes_live_redis": False,
    "calls_broker_api": False,
    "paper_armed_approved": False,
    "live_trading_approved": False,
    "execution_arming_created": False,
    "real_order_sent": False,
    "production_doctrine_changed": False,
    "full_live_replay_parity": "NOT_PROVEN_IN_28J",
}
write_json(preflight_root / "03_no_enablement_boundary.json", no_enablement)

readiness = {
    "schema_version": "observe_only_replay_input_materialization_readiness_28j_v1",
    "dataset_id": dataset_id,
    "dataset_preflight_ready": bool(dataset_preflight_ready),
    "manifest_28i_ok": bool(manifest_28i_ok),
    "closed_28f_ok": bool(closed_28f_ok),
    "package_integrity_ok": bool(package_integrity_ok),
    "preflight_root_replay_safe": bool(preflight_root_safe),
    "replay_run_completed": False,
    "comparison_completed": False,
    "full_live_replay_parity": "NOT_PROVEN_IN_28J",
}
write_json(preflight_root / "04_materialization_readiness.json", readiness)

write_json(PREFLIGHT_MANIFEST, preflight_manifest)

preflight_artifact_states = {
    name: file_state(preflight_root / name)
    for name in PREFLIGHT_ARTIFACTS
}

preflight_artifacts_ok = all(state.get("present") for state in preflight_artifact_states.values())

proof_ok = bool(dataset_preflight_ready and preflight_artifacts_ok)

proof = {
    "schema_version": "proof_observe_only_replay_input_dataset_preflight_28j_v1",
    "batch": "28J",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "accepted_for": "REPLAY_INPUT_DATASET_PREFLIGHT_ONLY",
    "verdict": "PASS_OBSERVE_ONLY_REPLAY_INPUT_DATASET_PREFLIGHT_28J" if proof_ok else "FAIL_OBSERVE_ONLY_REPLAY_INPUT_DATASET_PREFLIGHT_28J",
    "observe_only_replay_input_dataset_preflight_28j_ok": bool(proof_ok),

    "dataset_id": dataset_id,
    "capture_id": capture_id,
    "preflight_manifest": rel(PREFLIGHT_MANIFEST),
    "preflight_manifest_sha256": sha256_file(PREFLIGHT_MANIFEST),
    "preflight_root": rel(preflight_root),
    "preflight_root_replay_safe": bool(preflight_root_safe),
    "preflight_artifacts_ok": bool(preflight_artifacts_ok),
    "preflight_artifact_states": preflight_artifact_states,

    "manifest_28i_ok": bool(manifest_28i_ok),
    "closed_28f_ok": bool(closed_28f_ok),
    "package_integrity_ok": bool(package_integrity_ok),
    "dataset_preflight_ready": bool(dataset_preflight_ready),

    "source_evidence_count": len(evidence_map),
    "missing_source_keys": missing_source_keys,
    "missing_source_files": missing_source_files,
    "missing_package_artifacts": missing_package_artifacts,
    "missing_copied_evidence": missing_copied_evidence,
    "hash_mismatch_keys": hash_mismatch_keys,

    "dataset_materialized": False,
    "replay_run_completed": False,
    "comparison_completed": False,

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
    "full_live_replay_parity": "NOT_PROVEN_IN_28J",

    "next_batch": preflight_manifest["next_batch"],
}

write_json(PROOF_MAIN, proof)
write_json(PROOF_LATEST, proof)

print(json.dumps(proof, indent=2, sort_keys=True))
raise SystemExit(0 if proof_ok else 1)
