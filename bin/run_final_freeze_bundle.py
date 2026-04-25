#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PYBIN = ROOT / ".venv" / "bin" / "python"
if not PYBIN.exists():
    PYBIN = Path(sys.executable)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
tag = f"final_freeze_bundle_{ts}"

bundle = ROOT / "run" / "proofs" / tag
logs = bundle / "logs"
snapshots = bundle / "snapshots"
artifacts = bundle / "artifacts"

for d in (bundle, logs, snapshots, artifacts):
    d.mkdir(parents=True, exist_ok=True)

timeout_sec = int(os.environ.get("PROOF_TIMEOUT_SEC", "240"))

SAFE_ENV = os.environ.copy()
SAFE_ENV.update(
    {
        "MME_FINAL_FREEZE_PROOF": "1",
        "MME_PROOF_MODE": "offline_first",
        "PYTHONDONTWRITEBYTECODE": "1",
        "MME_ALLOW_LIVE_ORDERS": "0",
        "SCALPX_ALLOW_LIVE_ORDERS": "0",
        "MME_LIVE_ORDERS_ALLOWED": "0",
        "SCALPX_LIVE_ORDERS_ALLOWED": "0",
        "MME_DISABLE_BROKER_ORDERS": "1",
        "SCALPX_DISABLE_BROKER_ORDERS": "1",
    }
)

PROOFS = [
    # Core / Redis contract
    "bin/proof_redis_contract_matrix.py",
    "bin/proof_core_codec_transport.py",
    "bin/proof_redisx_typed_stream_helpers.py",
    "bin/proof_names_alias_lifecycle.py",

    # Runtime / config truth
    "bin/proof_runtime_effective_config.py",
    "bin/proof_config_runtime_truth.py",
    "bin/proof_runtime_dependency_lock.py",
    "bin/proof_logging_redaction.py",

    # Provider / broker / instruments
    "bin/proof_provider_runtime_roles.py",
    "bin/proof_provider_auth_sources.py",
    "bin/proof_dhan_context_quality.py",
    "bin/proof_dhan_execution_fallback_policy.py",
    "bin/proof_runtime_instrument_source.py",
    "bin/proof_runtime_instrument_provider_equivalence.py",

    # Feeds / features
    "bin/proof_feeds_provider_surface_strictness.py",
    "bin/proof_features_false_readiness_guards.py",
    "bin/proof_features_active_vs_context_option_truth.py",

    # Feature-family
    "bin/proof_feature_family_shared_core_guards.py",
    "bin/proof_feature_family_strategy_surfaces.py",

    # Strategy-family / strategy bridge
    "bin/proof_strategy_family_shared_layer_contracts.py",
    "bin/proof_strategy_family_doctrine_leaves.py",
    "bin/proof_strategy_promoted_decision_contract.py",
    "bin/proof_strategy_hold_bridge_offline.py",
    "bin/proof_strategy_activation_report_only.py",

    # Execution
    "bin/proof_execution_hold_no_order.py",
    "bin/proof_execution_family_entry_safety.py",

    # Risk
    "bin/proof_risk_exit_never_blocked.py",
    "bin/proof_risk_restart_rebuild.py",
    "bin/proof_risk_replay_key_separation.py",
    "bin/proof_risk_trade_ledger_idempotency.py",

    # Monitor / report / ops
    "bin/proof_monitor_report_ops_contracts.py",

    # Replay
    "bin/proof_replay_engine_contracts.py",

    # Research
    "bin/proof_research_capture_contracts.py",
    "bin/proof_research_capture_production_firewall.py",

    # Proof governance / legacy
    "bin/proof_proof_layer_contracts.py",
    "bin/proof_legacy_quarantine_contracts.py",
]

SENSITIVE_RE = re.compile(
    r"(?i)(password|passwd|secret|token|access_token|refresh_token|api_key|apikey|authorization|enctoken|jwt|client_secret)\s*[:=]\s*['\"]?[^'\"\n\r]+"
)

def now_ns() -> int:
    return time.time_ns()

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)

def run_cmd(name: str, cmd: list[str], *, timeout: int | None = None) -> dict[str, Any]:
    out_path = logs / f"{name}.stdout.log"
    err_path = logs / f"{name}.stderr.log"
    started = now_ns()

    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env=SAFE_ENV,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        out_path.write_text(proc.stdout or "", encoding="utf-8")
        err_path.write_text(proc.stderr or "", encoding="utf-8")
        return {
            "name": name,
            "cmd": cmd,
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "returncode": proc.returncode,
            "started_ns": started,
            "finished_ns": now_ns(),
            "stdout_log": rel(out_path),
            "stderr_log": rel(err_path),
        }
    except subprocess.TimeoutExpired as exc:
        out_path.write_text(exc.stdout or "", encoding="utf-8")
        err_path.write_text((exc.stderr or "") + f"\nTIMEOUT after {timeout}s\n", encoding="utf-8")
        return {
            "name": name,
            "cmd": cmd,
            "status": "TIMEOUT",
            "returncode": None,
            "started_ns": started,
            "finished_ns": now_ns(),
            "stdout_log": rel(out_path),
            "stderr_log": rel(err_path),
        }
    except Exception as exc:
        err_path.write_text(repr(exc), encoding="utf-8")
        return {
            "name": name,
            "cmd": cmd,
            "status": "ERROR",
            "returncode": None,
            "started_ns": started,
            "finished_ns": now_ns(),
            "stdout_log": rel(out_path),
            "stderr_log": rel(err_path),
        }

def capture_text(name: str, cmd: list[str]) -> None:
    result = run_cmd(name, cmd, timeout=60)
    (snapshots / f"{name}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

def redact_and_copy_configs() -> None:
    target = snapshots / "redacted_configs"
    target.mkdir(parents=True, exist_ok=True)

    roots = [ROOT / "etc", ROOT / "docs"]
    suffixes = {".yaml", ".yml", ".json", ".env", ".md", ".txt"}

    for base in roots:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in suffixes:
                continue
            relp = p.relative_to(ROOT)
            out = target / relp
            out.parent.mkdir(parents=True, exist_ok=True)
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
                text = SENSITIVE_RE.sub(lambda m: m.group(1) + ": <REDACTED>", text)
                out.write_text(text, encoding="utf-8")
            except Exception as exc:
                out.write_text(f"FAILED_TO_COPY: {exc!r}", encoding="utf-8")

def copy_recent_json_artifacts() -> None:
    candidates = []
    proof_root = ROOT / "run" / "proofs"
    if proof_root.exists():
        for p in proof_root.rglob("*.json"):
            if tag in str(p):
                continue
            try:
                candidates.append((p.stat().st_mtime_ns, p))
            except OSError:
                pass

    candidates.sort(reverse=True)
    for _, p in candidates[:300]:
        try:
            dest = artifacts / p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
        except Exception:
            pass

def clean_active_python_cache() -> dict[str, Any]:
    """
    Remove generated bytecode from active source folders.

    compileall is still executed as a syntax gate, but freeze hygiene should not
    leave active app/bin __pycache__ or *.pyc artifacts behind.
    """
    removed: list[str] = []
    errors: list[str] = []

    roots = [ROOT / "app", ROOT / "bin"]

    for base in roots:
        if not base.exists():
            continue

        for pyc in list(base.rglob("*.pyc")) + list(base.rglob("*.pyo")):
            try:
                removed.append(rel(pyc))
                pyc.unlink()
            except Exception as exc:
                errors.append(f"{rel(pyc)}: {exc!r}")

        for cache in sorted(base.rglob("__pycache__"), key=lambda x: len(x.parts), reverse=True):
            try:
                removed.append(rel(cache))
                shutil.rmtree(cache, ignore_errors=False)
            except Exception as exc:
                errors.append(f"{rel(cache)}: {exc!r}")

    return {
        "removed_count": len(set(removed)),
        "removed": sorted(set(removed)),
        "errors": errors,
        "status": "PASS" if not errors else "WARN",
    }

def hygiene_scan() -> dict[str, Any]:
    """
    Project hygiene scan.

    Important:
    - Do not scan .venv/site-packages. Python environments naturally contain
      __pycache__ and *.pyc files and are not repository hygiene failures.
    - Do not scan generated proof bundles.
    - Do not scan archived code backups/quarantine folders.
    """
    excluded_parts = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "site-packages",
        "run/proofs",
        "run/_code_backups",
        "run/_quarantine",
        "run/freeze_work",
        "run/migration_cleanup",
    }

    def is_excluded(path: Path) -> bool:
        try:
            rp = path.relative_to(ROOT)
        except Exception:
            return True
        parts = set(rp.parts)
        rels = {"/".join(rp.parts[:i]) for i in range(1, len(rp.parts) + 1)}
        return bool(parts & excluded_parts) or bool(rels & excluded_parts)

    found: list[str] = []

    for p in ROOT.rglob("*"):
        if is_excluded(p):
            continue
        name = p.name
        if (
            name == "__pycache__"
            or name.endswith(".pyc")
            or name.endswith(".pyo")
            or name.endswith(".bak")
            or ".bak." in name
        ):
            found.append(rel(p))

    temp_patch_files = []
    for base in (ROOT, ROOT / "run"):
        if not base.exists():
            continue
        for p in base.glob("_patch_*"):
            if not is_excluded(p):
                temp_patch_files.append(rel(p))

    return {
        "status": "PASS" if not found and not temp_patch_files else "WARN",
        "cache_or_backup_files": sorted(set(found)),
        "temporary_patch_files": sorted(set(temp_patch_files)),
    }

def main() -> int:
    print(f"===== FINAL FREEZE BUNDLE: {tag} =====")
    print(f"bundle={bundle}")

    results: list[dict[str, Any]] = []

    # Static snapshots
    capture_text("git_rev_parse_head", ["git", "rev-parse", "HEAD"])
    capture_text("git_status_short", ["git", "status", "--short"])
    capture_text("git_diff_stat", ["git", "diff", "--stat"])
    capture_text("git_ls_files", ["git", "ls-files"])

    capture_text("project_tree_find", ["bash", "-lc", "find app bin etc docs -maxdepth 5 -type f 2>/dev/null | sort"])
    capture_text("systemd_scalpx_snapshot", ["bash", "-lc", "systemctl list-units --type=service --all | grep -E 'scalpx|mme' || true"])
    capture_text("systemd_scalpx_status", ["bash", "-lc", "systemctl status scalpx-mme.service --no-pager || true"])

    redact_and_copy_configs()

    # Hygiene
    hygiene = hygiene_scan()
    (bundle / "hygiene_scan.json").write_text(json.dumps(hygiene, indent=2), encoding="utf-8")

    # Compile gates
    results.append(run_cmd("compileall_app_bin", [str(PYBIN), "-m", "compileall", "app", "bin"], timeout=timeout_sec))

    dataset = ROOT / "app" / "mme_scalpx" / "replay" / "dataset.py"
    if dataset.exists():
        results.append(run_cmd("py_compile_replay_dataset", [str(PYBIN), "-m", "py_compile", rel(dataset)], timeout=timeout_sec))
    else:
        results.append({
            "name": "py_compile_replay_dataset",
            "status": "MISSING",
            "path": "app/mme_scalpx/replay/dataset.py",
        })

    cache_cleanup = clean_active_python_cache()
    (bundle / "active_python_cache_cleanup.json").write_text(json.dumps(cache_cleanup, indent=2), encoding="utf-8")

    # Required proof scripts
    for proof in PROOFS:
        path = ROOT / proof
        name = Path(proof).stem
        if not path.exists():
            results.append({
                "name": name,
                "path": proof,
                "status": "MISSING",
                "returncode": None,
                "does_not_prove": ["Proof script is missing from patched tree."],
            })
            continue

        print(f"===== RUN {proof} =====")
        results.append(run_cmd(name, [str(PYBIN), proof], timeout=timeout_sec))

    copy_recent_json_artifacts()

    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    required_bad = [
        r for r in results
        if r["status"] not in {"PASS"}
    ]

    overall = "PASS" if not required_bad and hygiene["status"] == "PASS" else "FAIL"

    index = {
        "bundle_name": tag,
        "proof_name": "final_integration_freeze_bundle",
        "proof_version": "1.0",
        "status": overall,
        "timestamp_ns": now_ns(),
        "python": str(PYBIN),
        "root": str(ROOT),
        "bundle_dir": rel(bundle),
        "safe_env_assertions": {
            "PYTHONDONTWRITEBYTECODE": SAFE_ENV.get("PYTHONDONTWRITEBYTECODE"),
            "MME_ALLOW_LIVE_ORDERS": SAFE_ENV.get("MME_ALLOW_LIVE_ORDERS"),
            "SCALPX_ALLOW_LIVE_ORDERS": SAFE_ENV.get("SCALPX_ALLOW_LIVE_ORDERS"),
            "MME_DISABLE_BROKER_ORDERS": SAFE_ENV.get("MME_DISABLE_BROKER_ORDERS"),
        },
        "hygiene": hygiene,
        "counts": counts,
        "results": results,
        "freeze_verdict": (
            "FREEZE_READY_CANDIDATE" if overall == "PASS"
            else "NOT_FREEZE_READY_REVIEW_FAILED_OR_MISSING_PROOFS"
        ),
        "does_not_prove": [
            "This bundle does not prove live profitability.",
            "This bundle does not arm live trading.",
            "This bundle does not place broker orders.",
            "Live report-only observation must be run separately after offline/static PASS.",
        ],
    }

    (bundle / "final_freeze_bundle_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    md = ROOT / "docs" / "milestones" / f"{datetime.now().date()}_final_freeze_bundle_{ts}.md"
    md.write_text(
        "\n".join([
            f"# Final Integration Freeze Bundle — {datetime.now().date()}",
            "",
            f"- Bundle: `{rel(bundle)}`",
            f"- Status: `{overall}`",
            f"- Verdict: `{index['freeze_verdict']}`",
            f"- Counts: `{counts}`",
            f"- Hygiene: `{hygiene['status']}`",
            "",
            "## Required next action",
            "",
            "Review `final_freeze_bundle_index.json` and every FAIL / MISSING / TIMEOUT item.",
            "Only after all offline/static proofs pass should live report-only observation be run.",
            "",
        ]),
        encoding="utf-8",
    )

    print()
    print("===== FINAL BUNDLE SUMMARY =====")
    print(json.dumps({
        "status": overall,
        "bundle": rel(bundle),
        "index": rel(bundle / "final_freeze_bundle_index.json"),
        "milestone": rel(md),
        "counts": counts,
        "hygiene": hygiene["status"],
    }, indent=2))

    return 0 if overall == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
