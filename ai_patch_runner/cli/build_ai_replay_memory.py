#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
CTX = ROOT / "ai_patch_runner" / "context"
CTX.mkdir(parents=True, exist_ok=True)

REPLAY_PROOF_PATTERNS = [
    "run/proofs/proof_replay_data_a26_guarded_selector_execution_decision_*.json",
    "run/proofs/proof_replay_data_a25_guarded_selector_command_gate_*.json",
    "run/proofs/proof_replay_data_a24_guarded_selector_cli_command_construction_*.json",
    "run/proofs/proof_replay_data_a23_selector_cli_scope_blocker_classifier_*.json",
    "run/proofs/proof_replay_data_a21_guarded_selector_only_dry_run_*.json",
    "run/proofs/proof_replay_data_a20_guarded_selector_only_plan_run_*.json",
    "run/proofs/proof_replay_data_a19_selector_engine_consumption_probe_*.json",
    "run/proofs/proof_replay_data_a18_execution_shadow_semantic_normalization_*.json",
    "run/proofs/proof_replay_data_a17_engine_readiness_blocker_*.json",
    "run/proofs/proof_replay_data_a16_contract_shape_audit_*.json",
    "run/proofs/proof_replay_data_a15_selector_surface_probe_*.json",
    "run/proofs/proof_replay_data_a14_execution_shadow_*.json",
    "run/proofs/proof_replay_data_a13_risk_outputs_shadow_*.json",
    "run/proofs/proof_replay_data_a12_strategy_decisions_shadow_*.json",
    "run/proofs/proof_replay_data_a11_features_rows_reconstruction_*.json",
    "run/proofs/proof_replay_data_a10_selector_only_cli_dry_probe_*.json",
    "run/proofs/proof_replay_data_a9_quote_schema_transform_*.json",
    "run/proofs/proof_replay_data_a8b_deep_csv_payload_schema_*.json",
    "run/proofs/proof_replay_data_a8_quote_schema_mapping_*.json",
    "run/proofs/proof_replay_data_a7_sandbox_canonical_day_dataset_*.json",
    "run/proofs/proof_replay_data_a6_real_session_export_schema_plan_*.json",
    "run/proofs/proof_replay_data_a5_canonical_materialization_plan_*.json",
    "run/proofs/proof_replay_data_a4b_failed_patch_reconcile_dataset_topology_*.json",
    "run/proofs/proof_replay_data_a3_selector_date_mismatch_*.json",
    "run/proofs/proof_replay_data_a2_targeted_real_session_dataset_date_*.json",
    "run/proofs/proof_replay_data_a1_live_session_inventory_*.json",
]

AI_PROOF_PATTERNS = [
    "run/proofs/proof_ai_replay_r23_local_memory_a13_to_a14_*.json",
    "run/proofs/proof_ai_replay_r22_mme_ai_shortcuts_*.json",
    "run/proofs/proof_ai_replay_r21_a11_to_a12_classifier_repair_*.json",
    "run/proofs/proof_ai_replay_r2_proof_driven_next_batch_*.json",
    "run/proofs/proof_ai_replay_r1_next_batch_generator_*.json",
]


def rel(p: Path | str) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except Exception:
        return str(p)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_from_patterns(patterns: list[str]) -> Path | None:
    found: list[Path] = []
    for pat in patterns:
        found.extend(ROOT.glob(pat))
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def all_from_patterns(patterns: list[str]) -> list[Path]:
    found: list[Path] = []
    for pat in patterns:
        found.extend(ROOT.glob(pat))
    return sorted(set(found), key=lambda p: p.stat().st_mtime)


def compact_proof(path: Path) -> dict[str, Any]:
    try:
        data = load_json(path)
    except Exception as exc:
        return {"path": rel(path), "parse_ok": False, "error": repr(exc)}

    summary = data.get("summary") or {}
    findings = data.get("findings") or []

    # Prefer compact signpost only.
    out = {
        "path": rel(path),
        "mtime_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "batch": data.get("batch") or summary.get("batch"),
        "title": data.get("title"),
        "verdict": data.get("verdict") or summary.get("overall_verdict"),
        "summary_keys": sorted(summary.keys())[:80],
        "next_batch": summary.get("next_batch") or data.get("next_batch"),
        "engine_ready": summary.get("engine_ready", data.get("engine_ready")),
        "engine_execution_performed": summary.get("engine_execution_performed", data.get("engine_execution_performed")),
        "row_count": summary.get("row_count", data.get("row_count")),
        "source_date": summary.get("source_date") or data.get("source_date"),
        "canonical_root": summary.get("canonical_root") or data.get("canonical_root"),
        "candidate_path": summary.get("candidate_path") or data.get("candidate_path") or data.get("path"),
        "safety": data.get("safety", {}),
        "finding_count": len(findings),
        "findings_compact": [
            {
                "severity": f.get("severity"),
                "area": f.get("area"),
                "message": f.get("message"),
            }
            for f in findings[:10]
        ],
    }

    # Add known boolean flags if present.
    for key in [
        "selector_plan_ok",
        "features_rows_candidate_written",
        "strategy_decisions_candidate_written",
        "risk_outputs_candidate_written",
        "execution_shadow_candidate_written",
        "full_engine_execution_allowed",
        "selector_only_execution_performed",
        "selector_only_execution_allowed",
        "full_command_allowed",
        "selector_command_executed",
        "selector_execution_gate_pass",
        "selector_command_validated",
        "planned_command_path",
        "planned_command_safe",
        "selector_cli_command_executed",
        "selector_cli_command_constructed",
        "exact_feeds_only_present",
        "scope_blocker_resolved_as",
        "selector_scope_classification_ok",
        "selector_modules_import_ok",
        "selector_date_present",
        "selector_only_dry_run_performed",
        "selector_only_dry_run_ok",
        "selector_only_probe_performed",
        "selector_only_plan_ok",
        "surface_compatibility_ok",
        "engine_consumption_candidate",
        "selector_consumption_candidate",
        "consumption_probe_ok",
        "semantic_rows_nonblank",
        "row_count_parity",
        "execution_shadow_semantic_ok",
        "blocker_count",
        "blocker_diagnosis_ok",
        "engine_ready_candidate",
        "contract_shape_ok",
        "all_required_surfaces_present",
        "surface_probe_ok",
        "quote_transform_written",
    ]:
        if key in summary:
            out[key] = summary.get(key)
        elif key in data:
            out[key] = data.get(key)

    return out


def latest_meta() -> Path | None:
    metas = sorted((ROOT / "ai_patch_runner" / "reports").glob("*_meta.json"), key=lambda p: p.stat().st_mtime)
    return metas[-1] if metas else None


def compact_meta(path: Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    try:
        data = load_json(path)
    except Exception as exc:
        return {"path": rel(path), "parse_ok": False, "error": repr(exc)}
    return {
        "path": rel(path),
        "expected_batch": data.get("expected_batch"),
        "output_script": data.get("output_script"),
        "static_validation_ok": data.get("static_validation_ok"),
        "policy_validation_ok": (data.get("policy_validation") or {}).get("ok"),
        "classification": (data.get("local_classification") or {}).get("verdict"),
        "created_at_utc": data.get("created_at_utc"),
    }


def infer_current_state(latest_replay: dict[str, Any] | None) -> dict[str, Any]:
    state = {
        "paper_live_status": "BLOCKED_NOT_IN_SCOPE",
        "full_live_replay_parity": "NOT_PROVEN",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "starts_services": False,
        "reads_live_redis": False,
        "writes_live_redis": False,
        "calls_broker_api": False,
        "real_order_sent": False,
        "code_patch_applied": False,
        "engine_ready": False,
    }

    if latest_replay:
        state.update({
            "latest_passed_or_latest_replay_batch": latest_replay.get("batch"),
            "latest_replay_proof": latest_replay.get("path"),
            "canonical_root": latest_replay.get("canonical_root"),
            "source_date": latest_replay.get("source_date"),
            "latest_candidate_path": latest_replay.get("candidate_path"),
            "latest_row_count": latest_replay.get("row_count"),
            "engine_ready": latest_replay.get("engine_ready") or False,
            "engine_ready_candidate": latest_replay.get("engine_ready_candidate"),
            "contract_shape_ok": latest_replay.get("contract_shape_ok"),
            "engine_execution_performed": latest_replay.get("engine_execution_performed") or False,
        })

        nb = latest_replay.get("next_batch")
        if nb:
            state["next_expected_batch"] = nb
        elif latest_replay.get("batch") == "REPLAY-DATA-A13":
            state["next_expected_batch"] = "REPLAY-DATA-A14 execution shadow reconstruction audit"

    return state


def main() -> int:
    replay_proofs = all_from_patterns(REPLAY_PROOF_PATTERNS)
    ai_proofs = all_from_patterns(AI_PROOF_PATTERNS)

    compact_replay = [compact_proof(p) for p in replay_proofs][-50:]
    latest_replay_path = replay_proofs[-1] if replay_proofs else None
    latest_ai_path = ai_proofs[-1] if ai_proofs else None

    latest_replay = compact_proof(latest_replay_path) if latest_replay_path else None
    latest_ai = compact_proof(latest_ai_path) if latest_ai_path else None
    meta = compact_meta(latest_meta())

    current_state = infer_current_state(latest_replay)

    safety_boundary = {
        "version": "mme_ai_safety_boundary_v1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "hard_blocks": {
            "paper_live_status": "BLOCKED_NOT_IN_SCOPE",
            "full_live_replay_parity": "NOT_PROVEN",
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "starts_services": False,
            "reads_live_redis": False,
            "writes_live_redis": False,
            "calls_broker_api": False,
            "real_order_sent": False,
            "broker_login_allowed": False,
            "redis_mutation_allowed": False,
        },
        "allowed_ai_runner_actions": [
            "read latest proof JSON",
            "generate next replay/offline command package",
            "write proof JSON",
            "write milestone markdown",
            "write compact context memory",
            "write sandbox/candidate replay data under run/replay/parity/offline_materialization",
            "run guarded offline replay-data command only after static and policy validation",
        ],
        "blocked_paths": [
            "common/secrets/",
            "etc/brokers/",
            "app/mme_scalpx/main.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/integrations/",
        ],
    }

    allowed_paths = {
        "version": "mme_ai_allowed_paths_v1",
        "allowed_write_roots": [
            "run/proofs/",
            "run/audits/",
            "docs/milestones/",
            "ai_patch_runner/outputs/",
            "ai_patch_runner/reports/",
            "ai_patch_runner/prompts/",
            "ai_patch_runner/logs/",
            "ai_patch_runner/context/",
            "run/replay/parity/offline_materialization/",
        ],
        "allowed_read_roots": [
            "run/proofs/",
            "docs/milestones/",
            "ai_patch_runner/",
            "app/mme_scalpx/replay/",
            "app/mme_scalpx/services/",
            "run/replay/parity/offline_materialization/",
        ],
    }

    blocked_paths = {
        "version": "mme_ai_blocked_paths_v1",
        "blocked_write_roots": safety_boundary["hard_blocks"],
        "blocked_path_patterns": safety_boundary["blocked_paths"],
        "blocked_runtime_patterns": [
            "nohup",
            "systemctl",
            "python -m app.mme_scalpx.main",
            "redis-cli SET/HSET/XADD/DEL",
            "broker login/API call",
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1",
            "SCALPX_REAL_LIVE_ALLOWED=1",
            "SCALPX_ALLOW_REAL_LIVE=1",
        ],
    }

    latest_chain_md = []
    latest_chain_md.append("# MME AI Runner Local Memory — Latest Chain Summary")
    latest_chain_md.append("")
    latest_chain_md.append(f"Updated UTC: {datetime.now(timezone.utc).isoformat()}")
    latest_chain_md.append("")
    latest_chain_md.append("## Current State")
    latest_chain_md.append("")
    latest_chain_md.append(f"- Latest replay proof: `{current_state.get('latest_replay_proof')}`")
    latest_chain_md.append(f"- Latest replay batch: `{current_state.get('latest_passed_or_latest_replay_batch')}`")
    latest_chain_md.append(f"- Next expected batch: `{current_state.get('next_expected_batch')}`")
    latest_chain_md.append(f"- Canonical root: `{current_state.get('canonical_root')}`")
    latest_chain_md.append(f"- Source date: `{current_state.get('source_date')}`")
    latest_chain_md.append(f"- Engine ready: `{current_state.get('engine_ready')}`")
    latest_chain_md.append("")
    latest_chain_md.append("## Safety Boundary")
    latest_chain_md.append("")
    latest_chain_md.append("- paper_live_status = BLOCKED_NOT_IN_SCOPE")
    latest_chain_md.append("- full_live_replay_parity = NOT_PROVEN")
    latest_chain_md.append("- paper_armed_approved = false")
    latest_chain_md.append("- live_trading_approved = false")
    latest_chain_md.append("- services/broker/Redis/live execution remain blocked")
    latest_chain_md.append("")
    latest_chain_md.append("## Recent Replay Signposts")
    latest_chain_md.append("")
    for item in compact_replay[-12:]:
        latest_chain_md.append(
            f"- `{item.get('batch')}` | proof=`{item.get('path')}` | "
            f"row_count=`{item.get('row_count')}` | next=`{item.get('next_batch')}` | "
            f"engine_ready=`{item.get('engine_ready')}`"
        )
    latest_chain_md.append("")

    known_contracts_md = """# Known Contracts — MME AI Runner

## Replay chain current contract

- A7/A8/A8B/A9/A10 built selector-ready quote dataset.
- A11 wrote features_rows_candidate.csv.
- A12 wrote strategy_decisions_candidate.csv with conservative HOLD/NO_TRADE shadow rows.
- A13 wrote risk_outputs_candidate.csv with conservative risk/no-order shadow rows.
- A14 should create execution_shadow_candidate.csv only if schema-safe.
- Full replay engine remains disabled until all required candidate surfaces exist and selector/probe proofs pass.

## Safety contract

- No live/paper approval.
- No broker/API call.
- No service start.
- No Redis write.
- No production risk/execution/main patch.
- Candidate reconstruction is sandbox/offline under run/replay/parity/offline_materialization only.
"""

    project_constitution_md = """# MME AI Runner Project Constitution

The local AI runner accelerates offline replay-data development only. It is not authorized to approve paper/live trading, start services, call brokers, mutate live Redis, or modify production trading logic.

Every generated package must be proof-driven, one-batch scoped, statically validated, policy validated, and manually or guarded-run executed only through mrun.

Latest proof beats memory. Uploaded evidence/proof artifacts beat old summaries. If memory conflicts with proof, proof wins.
"""

    (CTX / "replay_current_state.json").write_text(json.dumps(current_state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CTX / "replay_chain_signposts.json").write_text(json.dumps(compact_replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CTX / "latest_ai_meta.json").write_text(json.dumps(meta or {}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CTX / "latest_ai_proof.json").write_text(json.dumps(latest_ai or {}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CTX / "safety_boundary.json").write_text(json.dumps(safety_boundary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CTX / "allowed_paths.json").write_text(json.dumps(allowed_paths, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CTX / "blocked_paths.json").write_text(json.dumps(blocked_paths, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (CTX / "latest_chain_summary.md").write_text("\n".join(latest_chain_md), encoding="utf-8")
    (CTX / "known_contracts.md").write_text(known_contracts_md, encoding="utf-8")
    (CTX / "project_constitution.md").write_text(project_constitution_md, encoding="utf-8")

    inventory = []
    total = 0
    for p in sorted(CTX.glob("*")):
        if p.is_file():
            size = p.stat().st_size
            total += size
            inventory.append({"path": rel(p), "size_bytes": size})

    result = {
        "context_dir": rel(CTX),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(inventory),
        "total_size_bytes": total,
        "inventory": inventory,
        "latest_replay_proof": rel(latest_replay_path) if latest_replay_path else None,
        "latest_ai_proof": rel(latest_ai_path) if latest_ai_path else None,
        "current_state": current_state,
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
