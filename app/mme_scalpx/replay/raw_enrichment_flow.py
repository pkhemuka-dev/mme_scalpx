"""Optional replay RAW-enrichment flow hook.

RAW-M wires RAW-L enrichment into a replay/export workflow as an explicit opt-in
post-export step. Existing replay behavior is unchanged by default.

No broker IO. No Redis IO. No orders. No live/paper enablement.
"""

from __future__ import annotations

# RAW-X source-row lineage hook -- replay/research only.
try:
    from app.mme_scalpx.replay.raw_source_lineage import inject_source_lineage as _raw_x_inject_source_lineage
except Exception:
    def _raw_x_inject_source_lineage(value, *, source_artifact=''):
        return value


def _raw_x_lineage(value, *, source_artifact=''):
    return _raw_x_inject_source_lineage(value, source_artifact=source_artifact)
# END RAW-X source-row lineage hook.

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.mme_scalpx.replay.raw_artifact_enricher import (
    ENRICHED_RECORDS_JSONL,
    ENRICHMENT_MANIFEST_JSON,
    ENRICHMENT_SUMMARY_JSON,
    enrich_replay_artifacts,
)

RAW_M_SCHEMA_VERSION = "RAW-M.1"
FLOW_MANIFEST_JSON = "raw_enrichment_flow_manifest.json"
FLOW_SUMMARY_JSON = "raw_enrichment_flow_summary.json"

ENV_ENABLE_RAW_REPLAY_ENRICHMENT = "MME_REPLAY_RAW_ENRICH"
ENV_RAW_REPLAY_ENRICH_OUTPUT_DIR = "MME_REPLAY_RAW_ENRICH_OUTPUT_DIR"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bool_from_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def default_enabled_from_env() -> bool:
    return _bool_from_env(ENV_ENABLE_RAW_REPLAY_ENRICHMENT, default=False)


def _default_output_dir(project_root: Path, run_id: str) -> Path:
    env_dir = os.environ.get(ENV_RAW_REPLAY_ENRICH_OUTPUT_DIR, "").strip()
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return project_root / "run" / "replay" / run_id


def build_flow_summary(
    *,
    run_id: str,
    enabled: bool,
    enrichment_result: dict[str, Any] | None,
    reason: str,
) -> dict[str, Any]:
    return {
        "schema_version": RAW_M_SCHEMA_VERSION,
        "run_id": run_id,
        "generated_utc": utc_now_iso(),
        "enabled": enabled,
        "reason": reason,
        "enrichment_result": enrichment_result,
        "non_live": True,
        "non_mutating": True,
        "replay_post_export_hook_included": True,
        "default_enabled": False,
        "broker_io_included": False,
        "redis_live_write_included": False,
        "order_sending_included": False,
        "risk_override_included": False,
        "execution_override_included": False,
        "strategy_mutation_included": False,
        "production_config_mutation_included": False,
        "paper_live_enablement_included": False,
        "remarks": [
            "RAW-M is an optional replay post-export enrichment flow.",
            "Existing replay behavior is unchanged unless enabled explicitly.",
            "Unknown evidence remains UNKNOWN/null through RAW-L enricher.",
        ],
    }


def write_flow_artifacts(output_dir: Path, summary: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / FLOW_SUMMARY_JSON
    manifest_path = output_dir / FLOW_MANIFEST_JSON

    manifest = {
        "schema_version": RAW_M_SCHEMA_VERSION,
        "run_id": summary["run_id"],
        "generated_utc": utc_now_iso(),
        "artifacts": [
            {"path": FLOW_SUMMARY_JSON, "artifact_type": "raw_enrichment_flow_summary"},
            {"path": FLOW_MANIFEST_JSON, "artifact_type": "raw_enrichment_flow_manifest"},
            {"path": ENRICHED_RECORDS_JSONL, "artifact_type": "enriched_replay_records_jsonl"},
            {"path": ENRICHMENT_SUMMARY_JSON, "artifact_type": "enrichment_summary"},
            {"path": ENRICHMENT_MANIFEST_JSON, "artifact_type": "enrichment_manifest"},
        ],
        "enabled": summary["enabled"],
        "default_enabled": False,
        "non_live": True,
        "non_mutating": True,
    }

    tmp_summary = summary_path.with_suffix(summary_path.suffix + ".tmp")
    tmp_manifest = manifest_path.with_suffix(manifest_path.suffix + ".tmp")
    tmp_summary.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    tmp_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(tmp_summary, summary_path)
    os.replace(tmp_manifest, manifest_path)

    return {"flow_summary": str(summary_path), "flow_manifest": str(manifest_path)}


def maybe_run_raw_enrichment_after_replay(
    *,
    project_root: str | Path,
    run_id: str,
    output_dir: str | Path | None = None,
    enabled: bool | None = None,
    max_files: int = 100,
    max_rows_per_file: int = 5000,
) -> dict[str, Any]:
    root = Path(project_root).resolve()
    effective_enabled = default_enabled_from_env() if enabled is None else bool(enabled)
    out = Path(output_dir).resolve() if output_dir is not None else _default_output_dir(root, run_id)

    if not effective_enabled:
        summary = build_flow_summary(
            run_id=run_id,
            enabled=False,
            enrichment_result=None,
            reason="disabled_by_default_or_env",
        )
        paths = write_flow_artifacts(out, summary)
        return {
            "schema_version": RAW_M_SCHEMA_VERSION,
            "run_id": run_id,
            "enabled": False,
            "output_dir": str(out),
            "reason": summary["reason"],
            **paths,
        }

    enrichment_result = enrich_replay_artifacts(
        project_root=root,
        output_dir=out,
        run_id=run_id,
        max_files=max_files,
        max_rows_per_file=max_rows_per_file,
    )

    summary = build_flow_summary(
        run_id=run_id,
        enabled=True,
        enrichment_result=enrichment_result,
        reason="enabled_explicitly",
    )
    paths = write_flow_artifacts(out, summary)

    return {
        "schema_version": RAW_M_SCHEMA_VERSION,
        "run_id": run_id,
        "enabled": True,
        "output_dir": str(out),
        "reason": summary["reason"],
        "enrichment_result": enrichment_result,
        **paths,
    }


def assert_flow_safety(result: dict[str, Any]) -> bool:
    summary_path = result.get("flow_summary")
    if not summary_path:
        return False
    payload = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    required_false = [
        "broker_io_included",
        "redis_live_write_included",
        "order_sending_included",
        "risk_override_included",
        "execution_override_included",
        "strategy_mutation_included",
        "production_config_mutation_included",
        "paper_live_enablement_included",
        "default_enabled",
    ]
    for key in required_false:
        if payload.get(key) is not False:
            return False
    if payload.get("replay_post_export_hook_included") is not True:
        return False
    return True
