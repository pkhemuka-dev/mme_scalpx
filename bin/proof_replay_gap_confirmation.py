#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import compileall
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
# Batch 27B-R1B proof-harness fix:
# When this proof is executed as bin/proof_replay_gap_confirmation.py,
# Python places bin/ on sys.path. Add project root so app.mme_scalpx imports resolve.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REPLAY_EXPECTED_CURRENT_FILES = [
    "app/mme_scalpx/replay/__init__.py",
    "app/mme_scalpx/replay/artifacts.py",
    "app/mme_scalpx/replay/clock.py",
    "app/mme_scalpx/replay/contracts.py",
    "app/mme_scalpx/replay/dataset.py",
    "app/mme_scalpx/replay/differential.py",
    "app/mme_scalpx/replay/engine.py",
    "app/mme_scalpx/replay/experiments.py",
    "app/mme_scalpx/replay/fill_model.py",
    "app/mme_scalpx/replay/frame_export.py",
    "app/mme_scalpx/replay/injector.py",
    "app/mme_scalpx/replay/integrity.py",
    "app/mme_scalpx/replay/metrics.py",
    "app/mme_scalpx/replay/modes.py",
    "app/mme_scalpx/replay/overrides.py",
    "app/mme_scalpx/replay/reports.py",
    "app/mme_scalpx/replay/runner.py",
    "app/mme_scalpx/replay/selectors.py",
    "bin/replay_run.py",
    "bin/replay_compare.py",
]

REPLAY_TARGET_MISSING_OR_TO_CONFIRM_FILES = [
    "app/mme_scalpx/replay/reset.py",
    "app/mme_scalpx/replay/scenarios.py",
    "app/mme_scalpx/replay/live_adapter.py",
    "app/mme_scalpx/replay/transport.py",
    "app/mme_scalpx/replay/feature_adapter.py",
    "app/mme_scalpx/replay/strategy_adapter.py",
    "app/mme_scalpx/replay/risk_adapter.py",
    "app/mme_scalpx/replay/evaluators.py",
    "app/mme_scalpx/replay/forensics.py",
    "app/mme_scalpx/replay/oi_context.py",
    "app/mme_scalpx/replay/oi_wall.py",
    "bin/replay_batch.py",
    "bin/replay_forensics.py",
    "bin/replay_integrity.py",
    "bin/replay_sweep.py",
    "bin/proof_replay_no_broker_call.py",
    "bin/proof_replay_no_live_redis_write.py",
    "bin/proof_replay_no_runtime_promotion.py",
    "bin/proof_replay_dataset_manifest.py",
    "bin/proof_replay_deterministic_repeatability.py",
    "bin/proof_replay_contract_surface.py",
    "bin/proof_replay_feature_family_parity.py",
    "bin/proof_replay_family_coverage.py",
    "bin/proof_replay_family_arbitration.py",
    "bin/proof_replay_risk_execution_shadow.py",
    "bin/proof_replay_oi_wall_context.py",
    "bin/proof_replay_assumption_profiles.py",
    "bin/proof_replay_batch_runner.py",
    "bin/proof_replay_report_artifacts.py",
    "bin/proof_replay_shadow_vs_baseline_diff.py",
    "bin/proof_replay_full_5_family_certification.py",
]

LIVE_MIMIC_COUNTERPARTS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/codec.py",
    "app/mme_scalpx/core/clock.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
]

LIVE_MIMIC_DIRS = [
    "app/mme_scalpx/services/feature_family",
    "app/mme_scalpx/services/strategy_family",
    "app/mme_scalpx/domain",
    "app/mme_scalpx/integrations",
    "etc/replay",
    "etc/strategy_family",
    "etc/brokers",
]

REPLAY_REQUIRED_CONTRACT_TOKENS = [
    "family_features_json",
    "family_surfaces_json",
    "family_frames_json",
    "surface_kind",
    "branch_side",
    "provider_ready_miso",
    "dhan_context",
    "oi_ladder",
    "oi_wall",
    "trap_event_id",
    "burst_event_id",
    "execution_shadow",
    "LocalReplay",
    "ReplayClock",
    "run_id",
    "manifest",
]

FAMILY_TOKENS = {
    "MIST": [
        "trend_confirmed",
        "pullback_detected",
        "resume_confirmed",
        "micro_trap",
        "futures_impulse",
    ],
    "MISB": [
        "shelf_confirmed",
        "breakout_triggered",
        "breakout_accepted",
        "shelf_high",
        "shelf_low",
    ],
    "MISC": [
        "compression_detected",
        "directional_breakout_triggered",
        "expansion_accepted",
        "retest",
        "hesitation",
    ],
    "MISR": [
        "active_zone",
        "zone_id",
        "fake_break",
        "range_reentry",
        "flow_flip",
        "trap_event_id",
    ],
    "MISO": [
        "burst_detected",
        "burst_event_id",
        "aggression",
        "tape_speed",
        "imbalance_persistence",
        "queue_reload",
        "provider_ready_miso",
        "oi_wall",
    ],
}

# Dangerous token scan is intentionally conservative and path scoped.
# We do not fail for documentation words like "broker"; we fail for likely executable imports/calls.
DANGEROUS_EXECUTION_PATTERNS = [
    r"\bKiteConnect\s*\(",
    r"\bDhanHQ\s*\(",
    r"\bdhanhq\s*\.",
    r"\bplace_order\s*\(",
    r"\bmodify_order\s*\(",
    r"\bcancel_order\s*\(",
    r"\bexit_order\s*\(",
    r"\bflatten_position\s*\(",
    r"\bsend_order\s*\(",
    r"\bsubmit_order\s*\(",
    r"\bpaper_armed\s*=\s*True\b",
    r"\blive_trading\s*=\s*True\b",
    r"\bruntime_mode\s*=\s*[\"']live[\"']",
    r"\bruntime_mode\s*=\s*[\"']paper_armed[\"']",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def file_info(path_str: str) -> dict[str, Any]:
    path = ROOT / path_str
    info: dict[str, Any] = {
        "path": path_str,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "sha256": None,
        "line_count": None,
        "size_bytes": None,
    }
    if path.is_file():
        txt = read_text(path)
        info["sha256"] = sha256_file(path)
        info["line_count"] = txt.count("\n") + (1 if txt and not txt.endswith("\n") else 0)
        info["size_bytes"] = path.stat().st_size
    return info


def list_py_files(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        path = ROOT / p
        if path.is_file() and path.suffix == ".py":
            out.append(path)
        elif path.is_dir():
            out.extend(sorted(path.rglob("*.py")))
    # deterministic unique order
    uniq = sorted({x.resolve() for x in out})
    return [Path(x) for x in uniq]


def grep_tokens(files: list[Path], tokens: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for token in tokens:
        hits: list[dict[str, Any]] = []
        pattern = re.compile(re.escape(token), re.IGNORECASE)
        for f in files:
            if not f.exists() or not f.is_file():
                continue
            text = read_text(f)
            for idx, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    hits.append({
                        "file": rel(f),
                        "line": idx,
                        "text": line[:260],
                    })
        result[token] = {
            "hit_count": len(hits),
            "hits": hits[:50],
            "truncated": len(hits) > 50,
        }
    return result


def grep_regex(files: list[Path], patterns: list[str]) -> list[dict[str, Any]]:
    compiled = [(p, re.compile(p)) for p in patterns]
    hits: list[dict[str, Any]] = []
    for f in files:
        if not f.exists() or not f.is_file():
            continue
        text = read_text(f)
        for idx, line in enumerate(text.splitlines(), start=1):
            for pattern_text, pattern in compiled:
                if pattern.search(line):
                    hits.append({
                        "file": rel(f),
                        "line": idx,
                        "pattern": pattern_text,
                        "text": line[:260],
                    })
    return hits


def ast_imports_for_file(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"path": rel(path), "exists": False, "parse_ok": False, "imports": []}
    try:
        tree = ast.parse(read_text(path), filename=str(path))
    except SyntaxError as exc:
        return {
            "path": rel(path),
            "exists": True,
            "parse_ok": False,
            "syntax_error": str(exc),
            "imports": [],
        }
    imports: list[str] = []
    calls: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports.append(mod)
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                calls.append(func.id)
            elif isinstance(func, ast.Attribute):
                calls.append(func.attr)
    return {
        "path": rel(path),
        "exists": True,
        "parse_ok": True,
        "imports": sorted(set(imports)),
        "calls": sorted(set(calls)),
    }


def module_name_from_path(path: Path) -> str | None:
    try:
        rel_path = path.relative_to(ROOT)
    except ValueError:
        return None
    if rel_path.suffix != ".py":
        return None
    parts = list(rel_path.with_suffix("").parts)
    if not parts:
        return None
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return None
    if parts[0] != "app":
        return None
    return ".".join(parts)


def safe_import_replay_modules() -> dict[str, Any]:
    replay_dir = ROOT / "app/mme_scalpx/replay"
    results: list[dict[str, Any]] = []
    if not replay_dir.exists():
        return {
            "ok": False,
            "reason": "app/mme_scalpx/replay missing",
            "results": results,
        }

    py_files = sorted(replay_dir.rglob("*.py"))
    ok = True
    for f in py_files:
        mod = module_name_from_path(f)
        if not mod:
            continue
        try:
            importlib.import_module(mod)
            results.append({"module": mod, "ok": True})
        except Exception as exc:  # noqa: BLE001 - proof script reports exact import failure
            ok = False
            results.append({
                "module": mod,
                "ok": False,
                "error_type": type(exc).__name__,
                "error": str(exc),
            })
    return {"ok": ok, "results": results}


def run_compileall() -> dict[str, Any]:
    targets = [x for x in ["app", "bin", "tests"] if (ROOT / x).exists()]
    if not targets:
        return {"ok": False, "reason": "no compileall targets exist", "targets": targets}
    cmd = [sys.executable, "-m", "compileall", "-q", *targets]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "targets": targets,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def detect_replay_bridge_gap() -> dict[str, Any]:
    replay_run = ROOT / "bin/replay_run.py"
    replay_py_files = list_py_files(["app/mme_scalpx/replay"])
    replay_files_plus_runner = replay_py_files + ([replay_run] if replay_run.exists() else [])

    import_inspection = [ast_imports_for_file(p) for p in replay_files_plus_runner]

    all_imports = set()
    all_calls = set()
    for item in import_inspection:
        all_imports.update(item.get("imports") or [])
        all_calls.update(item.get("calls") or [])

    expected_live_reuse_import_needles = [
        "app.mme_scalpx.services.features",
        "app.mme_scalpx.services.strategy",
        "app.mme_scalpx.services.risk",
        "app.mme_scalpx.services.execution",
        "app.mme_scalpx.services.feature_family",
        "app.mme_scalpx.services.strategy_family",
    ]

    live_reuse_imports_found = {
        needle: any(str(imp).startswith(needle) or needle in str(imp) for imp in all_imports)
        for needle in expected_live_reuse_import_needles
    }

    missing_target_files = [
        p for p in REPLAY_TARGET_MISSING_OR_TO_CONFIRM_FILES
        if not (ROOT / p).exists()
    ]

    # Bridge gap is confirmed if the missing adapter set exists OR live reuse imports are not proven.
    required_adapter_files = [
        "app/mme_scalpx/replay/live_adapter.py",
        "app/mme_scalpx/replay/feature_adapter.py",
        "app/mme_scalpx/replay/strategy_adapter.py",
        "app/mme_scalpx/replay/risk_adapter.py",
        "app/mme_scalpx/replay/scenarios.py",
        "app/mme_scalpx/replay/reset.py",
    ]

    missing_required_adapters = [
        p for p in required_adapter_files if not (ROOT / p).exists()
    ]

    not_proven_live_reuse = [
        k for k, found in live_reuse_imports_found.items() if not found
    ]

    bridge_gap_confirmed = bool(missing_required_adapters or not_proven_live_reuse)

    return {
        "bridge_gap_confirmed": bridge_gap_confirmed,
        "missing_required_adapters": missing_required_adapters,
        "not_proven_live_reuse_imports": not_proven_live_reuse,
        "live_reuse_imports_found": live_reuse_imports_found,
        "all_replay_imports_sample": sorted(str(x) for x in all_imports)[:250],
        "all_replay_calls_sample": sorted(str(x) for x in all_calls)[:250],
        "missing_target_files": missing_target_files,
        "inspection": import_inspection,
    }


def detect_placeholder_integrity_gap() -> dict[str, Any]:
    integrity = ROOT / "app/mme_scalpx/replay/integrity.py"
    if not integrity.exists():
        return {
            "integrity_file_exists": False,
            "placeholder_or_partial_integrity_confirmed": True,
            "evidence": ["app/mme_scalpx/replay/integrity.py missing"],
        }

    text = read_text(integrity)
    placeholder_words = [
        "placeholder",
        "TODO",
        "stub",
        "not implemented",
        "pass",
        "advisory",
    ]
    hits = []
    for idx, line in enumerate(text.splitlines(), start=1):
        low = line.lower()
        if any(w.lower() in low for w in placeholder_words):
            hits.append({"line": idx, "text": line[:260]})

    required_integrity_tokens = [
        "dataset_hash",
        "profile_hash",
        "event_order",
        "timestamp",
        "monotonic",
        "heartbeat",
        "stale",
        "reset",
        "reproducibility",
    ]
    required_presence = {
        token: (token.lower() in text.lower())
        for token in required_integrity_tokens
    }
    missing_required = [k for k, v in required_presence.items() if not v]

    return {
        "integrity_file_exists": True,
        "placeholder_or_partial_integrity_confirmed": bool(hits or missing_required),
        "placeholder_hits": hits[:50],
        "missing_required_integrity_tokens": missing_required,
        "required_presence": required_presence,
    }


def collect_file_tree_summary() -> dict[str, Any]:
    replay_files = []
    if (ROOT / "app/mme_scalpx/replay").exists():
        replay_files = [rel(p) for p in sorted((ROOT / "app/mme_scalpx/replay").rglob("*")) if p.is_file()]

    replay_bins = [rel(p) for p in sorted((ROOT / "bin").glob("*replay*.py"))] if (ROOT / "bin").exists() else []
    proof_replay_bins = [rel(p) for p in sorted((ROOT / "bin").glob("proof_*replay*.py"))] if (ROOT / "bin").exists() else []

    replay_configs = []
    if (ROOT / "etc/replay").exists():
        replay_configs = [rel(p) for p in sorted((ROOT / "etc/replay").rglob("*")) if p.is_file()]

    replay_docs = []
    for d in ["docs", "tests"]:
        base = ROOT / d
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file() and "replay" in str(p).lower():
                    replay_docs.append(rel(p))

    return {
        "replay_files": replay_files,
        "replay_bins": replay_bins,
        "proof_replay_bins": proof_replay_bins,
        "replay_configs": replay_configs,
        "replay_docs_or_tests": replay_docs,
        "counts": {
            "replay_files": len(replay_files),
            "replay_bins": len(replay_bins),
            "proof_replay_bins": len(proof_replay_bins),
            "replay_configs": len(replay_configs),
            "replay_docs_or_tests": len(replay_docs),
        },
    }


def write_read_snapshots(inspection_dir: Path, files: list[str]) -> None:
    read_dir = inspection_dir / "file_reads"
    read_dir.mkdir(parents=True, exist_ok=True)
    index: list[dict[str, Any]] = []
    for f in files:
        p = ROOT / f
        info = file_info(f)
        index.append(info)
        if p.is_file():
            out_name = f.replace("/", "__")
            out = read_dir / f"{out_name}.txt"
            out.write_text(read_text(p), encoding="utf-8")
    (read_dir / "READ_INDEX.json").write_text(
        json.dumps(index, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--inspection-dir", required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()

    out_path = ROOT / args.out
    inspection_dir = ROOT / args.inspection_dir
    inspection_dir.mkdir(parents=True, exist_ok=True)

    current_file_infos = [file_info(p) for p in REPLAY_EXPECTED_CURRENT_FILES]
    target_file_infos = [file_info(p) for p in REPLAY_TARGET_MISSING_OR_TO_CONFIRM_FILES]
    live_file_infos = [file_info(p) for p in LIVE_MIMIC_COUNTERPARTS]
    live_dir_infos = [file_info(p) for p in LIVE_MIMIC_DIRS]

    files_to_read = sorted(set(
        REPLAY_EXPECTED_CURRENT_FILES
        + REPLAY_TARGET_MISSING_OR_TO_CONFIRM_FILES
        + LIVE_MIMIC_COUNTERPARTS
    ))
    write_read_snapshots(inspection_dir, files_to_read)

    tree_summary = collect_file_tree_summary()

    replay_py_scan_files = list_py_files([
        "app/mme_scalpx/replay",
        "bin/replay_run.py",
        "bin/replay_compare.py",
    ])

    # Exclude proof script itself from dangerous scan to avoid self-triggering on pattern strings.
    replay_py_scan_files = [
        p for p in replay_py_scan_files
        if rel(p) != "bin/proof_replay_gap_confirmation.py"
    ]

    dangerous_hits = grep_regex(replay_py_scan_files, DANGEROUS_EXECUTION_PATTERNS)

    contract_grep = grep_tokens(
        replay_py_scan_files,
        REPLAY_REQUIRED_CONTRACT_TOKENS,
    )

    family_grep = {
        family: grep_tokens(replay_py_scan_files, tokens)
        for family, tokens in FAMILY_TOKENS.items()
    }

    bridge_gap = detect_replay_bridge_gap()
    integrity_gap = detect_placeholder_integrity_gap()

    compileall_result = run_compileall()
    import_result = safe_import_replay_modules()

    # No-arm proof is static: this batch must not execute replay_run, services, Redis, or broker.
    no_arm_static = {
        "paper_armed_enabled_by_this_batch": False,
        "live_enabled_by_this_batch": False,
        "services_started_by_this_batch": False,
        "broker_calls_executed_by_this_batch": False,
        "live_redis_writes_executed_by_this_batch": False,
        "app_runtime_files_modified_by_this_batch": False,
        "notes": [
            "Batch 27B writes only proof and milestone artifacts.",
            "Deeper replay patching is intentionally deferred to Batch 27C+.",
        ],
    }

    missing_current_replay_files = [
        x["path"] for x in current_file_infos if not x["exists"]
    ]
    missing_live_counterpart_files = [
        x["path"] for x in live_file_infos if not x["exists"]
    ]

    safety_static_ok = len(dangerous_hits) == 0
    bridge_gap_confirmed = bool(bridge_gap["bridge_gap_confirmed"])
    placeholder_integrity_confirmed = bool(integrity_gap["placeholder_or_partial_integrity_confirmed"])

    # 27B pass condition:
    #   - Existing code compiles.
    #   - Replay modules import.
    #   - No obvious broker/arming tokens in replay path.
    #   - Gap is confirmed, not hidden.
    # This is not a replay success verdict.
    pass_gap_confirmed_no_arm = (
        compileall_result.get("ok") is True
        and import_result.get("ok") is True
        and safety_static_ok
        and bridge_gap_confirmed
    )

    verdict = "PASS_GAP_CONFIRMED_NO_ARM" if pass_gap_confirmed_no_arm else "FAIL_REVIEW_REQUIRED"

    proof: dict[str, Any] = {
        "schema_version": "batch27b_replay_gap_confirmation_v1",
        "tag": args.tag,
        "generated_at_utc": utc_now_iso(),
        "project_root": str(ROOT),
        "verdict": verdict,
        "important_interpretation": {
            "this_is_not_replay_success": True,
            "this_is_gap_confirmation_only": True,
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "next_batch": "Batch 27C — Replay safety firewall",
        },
        "summary": {
            "compileall_ok": compileall_result.get("ok"),
            "replay_import_ok": import_result.get("ok"),
            "static_no_broker_or_arm_hits_ok": safety_static_ok,
            "dangerous_hit_count": len(dangerous_hits),
            "bridge_gap_confirmed": bridge_gap_confirmed,
            "placeholder_or_partial_integrity_confirmed": placeholder_integrity_confirmed,
            "missing_current_replay_files": missing_current_replay_files,
            "missing_live_counterpart_files": missing_live_counterpart_files,
            "missing_target_files_count": len(bridge_gap.get("missing_target_files") or []),
        },
        "no_arm_static_assertion": no_arm_static,
        "file_tree_summary": tree_summary,
        "file_inventory": {
            "current_replay_expected_files": current_file_infos,
            "target_missing_or_to_confirm_files": target_file_infos,
            "live_mimic_counterpart_files": live_file_infos,
            "live_mimic_dirs": live_dir_infos,
        },
        "compileall": compileall_result,
        "replay_imports": import_result,
        "static_safety_scan": {
            "scan_files": [rel(p) for p in replay_py_scan_files],
            "dangerous_patterns": DANGEROUS_EXECUTION_PATTERNS,
            "dangerous_hits": dangerous_hits,
            "ok": safety_static_ok,
        },
        "bridge_gap_analysis": bridge_gap,
        "integrity_gap_analysis": integrity_gap,
        "contract_token_scan": contract_grep,
        "family_token_scan": family_grep,
        "required_patch_direction": [
            {
                "batch": "27C",
                "name": "Replay safety firewall",
                "purpose": "Add hard no-broker/no-live-Redis/no-runtime-promotion proofs before deeper replay patching.",
                "severity": "P0",
            },
            {
                "batch": "27D",
                "name": "Replay dataset contract expansion",
                "purpose": "Add full futures, selected option, Dhan context, OI ladder/wall, provider runtime surfaces.",
                "severity": "P1",
            },
            {
                "batch": "27E",
                "name": "Deterministic reset and replay integrity",
                "purpose": "Add deterministic reset, reproducible run_id, and real integrity checks.",
                "severity": "P1",
            },
            {
                "batch": "27F",
                "name": "Isolated live-shape transport",
                "purpose": "Replay live-compatible surfaces without touching live Redis.",
                "severity": "P1",
            },
            {
                "batch": "27G",
                "name": "Feature-family replay adapter",
                "purpose": "Reuse live feature_family builders under replay isolation.",
                "severity": "P1",
            },
            {
                "batch": "27H",
                "name": "Strategy-family replay adapter and arbitration",
                "purpose": "Reuse real strategy_family evaluators and arbitration under replay isolation.",
                "severity": "P1",
            },
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    latest = ROOT / "run/proofs/batch27b_replay_gap_confirmation_latest.json"
    latest.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({
        "verdict": verdict,
        "out": rel(out_path),
        "latest": rel(latest),
        "compileall_ok": compileall_result.get("ok"),
        "replay_import_ok": import_result.get("ok"),
        "dangerous_hit_count": len(dangerous_hits),
        "bridge_gap_confirmed": bridge_gap_confirmed,
        "paper_armed_approved": False,
        "live_trading_approved": False,
    }, indent=2, sort_keys=True))

    return 0 if pass_gap_confirmed_no_arm else 1


if __name__ == "__main__":
    raise SystemExit(main())
