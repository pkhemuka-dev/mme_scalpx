#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]

# Batch 26A v3 proof-harness repair:
# The script is executed from bin/, so Python may not include repo root on sys.path.
# Add repo root explicitly before importlib.import_module checks.
# This changes only proof behavior; it does not patch runtime trading code.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TARGET_FILES = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/controlled_paper_runtime.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/strategy_family/mist.py",
    "app/mme_scalpx/services/strategy_family/misb.py",
    "app/mme_scalpx/services/strategy_family/misc.py",
    "app/mme_scalpx/services/strategy_family/misr.py",
    "app/mme_scalpx/services/strategy_family/miso.py",
    "app/mme_scalpx/services/feature_family/misr_surface.py",
    "app/mme_scalpx/services/feature_family/miso_surface.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/settings.py",
]

CONFIG_FILES = [
    "etc/runtime.yaml",
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/arbitration.yaml",
    "etc/strategy_family/doctrine_registry.yaml",
    "etc/strategy_family/rollout/paper_armed_readiness_gate.yaml",
    "etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml",
    "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml",
]

PROOF_FILES = [
    "run/proofs/proof_market_session_provider_runtime.json",
    "run/proofs/proof_market_session_feed_snapshot.json",
    "run/proofs/proof_market_session_feature_payload.json",
    "run/proofs/proof_feature_raw_selected_split.json",
    "run/proofs/proof_feature_call_put_side_separation.json",
    "run/proofs/proof_market_session_family_surfaces.json",
    "run/proofs/proof_market_session_strategy_activation.json",
    "run/proofs/proof_market_session_no_order_sent.json",
    "run/proofs/proof_batch25v_final_summary.json",
    "run/proofs/proof_paper_armed_readiness_gate.json",
    "run/proofs/proof_controlled_paper_runtime_wiring.json",
    "run/proofs/batch26p_controlled_paper_runtime_wiring.json",
]

STRATEGY_LEAVES = {
    "MIST": "app/mme_scalpx/services/strategy_family/mist.py",
    "MISB": "app/mme_scalpx/services/strategy_family/misb.py",
    "MISC": "app/mme_scalpx/services/strategy_family/misc.py",
    "MISR": "app/mme_scalpx/services/strategy_family/misr.py",
    "MISO": "app/mme_scalpx/services/strategy_family/miso.py",
}

REQUIRED_STAGE_TERMS = [
    "data_valid",
    "data_quality_ok",
    "session_eligible",
    "warmup_complete",
    "provider_current",
    "selected_option_ready",
    "feed_fresh",
]

IMPORT_MODULES = [
    "app.mme_scalpx.core.names",
    "app.mme_scalpx.core.settings",
    "app.mme_scalpx.services.strategy",
    "app.mme_scalpx.services.execution",
    "app.mme_scalpx.services.risk",
]

REDIS_KEYS = {
    "orders_stream": "orders:mme:stream",
    "position_hash": "state:position:mme",
    "runtime_hash": "state:runtime",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def p(rel: str) -> pathlib.Path:
    return ROOT / rel


def read_text(rel: str) -> str:
    path = p(rel)
    if not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def sha256(rel: str) -> str | None:
    path = p(rel)
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_summary(rel: str) -> dict[str, Any]:
    path = p(rel)
    text = read_text(rel)
    return {
        "path": rel,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "line_count": len(text.splitlines()) if text else 0,
        "sha256": sha256(rel),
    }


def grep(rel: str, pattern: str, flags: int = 0, max_hits: int = 80) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    rx = re.compile(pattern, flags)
    for idx, line in enumerate(read_text(rel).splitlines(), 1):
        if rx.search(line):
            hits.append({"line": idx, "text": line.rstrip()[:260]})
            if len(hits) >= max_hits:
                break
    return hits


def run_cmd(cmd: list[str], timeout: int = 60) -> dict[str, Any]:
    try:
        cp = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout[-6000:],
            "stderr": cp.stderr[-6000:],
        }
    except Exception as exc:
        return {"cmd": cmd, "returncode": None, "stdout": "", "stderr": repr(exc)}


def redis_cmd(args: list[str]) -> dict[str, Any]:
    if shutil.which("redis-cli") is None:
        return {"available": False, "cmd": ["redis-cli"] + args, "returncode": None, "stdout": "", "stderr": "redis-cli not found"}
    out = run_cmd(["redis-cli"] + args, timeout=8)
    out["available"] = True
    return out


def redis_xlen(key: str) -> dict[str, Any]:
    out = redis_cmd(["XLEN", key])
    try:
        out["parsed_int"] = int(str(out.get("stdout", "")).strip())
    except Exception:
        out["parsed_int"] = None
    return out


def redis_hgetall(key: str) -> dict[str, Any]:
    out = redis_cmd(["HGETALL", key])
    lines = str(out.get("stdout") or "").splitlines()
    parsed: dict[str, str] = {}
    for i in range(0, len(lines) - 1, 2):
        parsed[lines[i]] = lines[i + 1]
    out["parsed_hash"] = parsed
    return out


def read_json(rel: str) -> dict[str, Any]:
    path = p(rel)
    out: dict[str, Any] = {"path": rel, "exists": path.exists(), "parse_ok": False, "sha256": sha256(rel), "important": {}, "error": None}
    if not path.exists() or not path.is_file():
        return out
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        out["parse_ok"] = True
    except Exception as exc:
        out["error"] = repr(exc)
        return out

    keys = [
        "ok", "pass", "passed", "status", "verdict",
        "final_25v_market_session_observation_ok",
        "paper_armed_readiness_gate_ok",
        "paper_armed_enabled",
        "real_live_allowed",
        "orders_sent",
        "orders_len",
        "market_session_no_order_sent_ok",
        "batch26p_controlled_paper_runtime_wiring_ok",
    ]

    found: dict[str, list[Any]] = {k: [] for k in keys}

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                if str(k) in found:
                    found[str(k)].append(v)
                walk(v)
        elif isinstance(x, list):
            for item in x:
                walk(item)

    walk(data)
    out["important"] = {k: v for k, v in found.items() if v}
    return out


def compile_check() -> dict[str, Any]:
    targets = [x for x in ["app", "bin"] if p(x).exists()]
    if not targets:
        return {"skipped": True, "reason": "no app/bin paths"}
    return run_cmd([sys.executable, "-m", "compileall", "-q", *targets], timeout=120)


def import_check() -> dict[str, Any]:
    results: dict[str, Any] = {}
    for mod in IMPORT_MODULES:
        try:
            importlib.import_module(mod)
            results[mod] = {"ok": True, "error": None}
        except Exception as exc:
            results[mod] = {"ok": False, "error": repr(exc)}
    return results


def scan_leaf(rel: str) -> dict[str, Any]:
    text = read_text(rel)
    return {
        "summary": file_summary(rel),
        "required_stage_terms_present": {term: (term in text) for term in REQUIRED_STAGE_TERMS},
        "optional_stage_get_patterns": grep(rel, r"\.get\([^)]*(data_valid|warmup|session|provider|feed|selected_option)", re.IGNORECASE, 80),
        "fail_closed_terms": grep(rel, r"fail.?closed|missing|required|blocker|veto|deny|return\s+False", re.IGNORECASE, 80),
    }


def derive_flat(redis_position_hash: dict[str, str]) -> dict[str, Any]:
    qty_raw = redis_position_hash.get("qty") or redis_position_hash.get("quantity") or redis_position_hash.get("qty_lots") or "0"
    open_raw = redis_position_hash.get("open") or redis_position_hash.get("has_position") or redis_position_hash.get("position_open")
    try:
        qty = float(str(qty_raw))
    except Exception:
        qty = None

    open_false = str(open_raw).strip().lower() in {"false", "0", "no", "none", ""} if open_raw is not None else None
    flat = (qty == 0) or (open_false is True) or (not redis_position_hash)
    return {
        "position_hash": redis_position_hash,
        "qty_raw": qty_raw,
        "qty_float": qty,
        "open_raw": open_raw,
        "flat_or_empty": flat,
        "verdict": "FLAT_OR_EMPTY" if flat else "NOT_PROVEN_FLAT",
    }


def main() -> int:
    started = time.time()

    all_manifest_paths = sorted(set(TARGET_FILES + CONFIG_FILES + PROOF_FILES + [__file__.replace(str(ROOT) + "/", "")]))
    manifest_lines = []
    for rel in all_manifest_paths:
        h = sha256(rel)
        manifest_lines.append(f"{h or 'MISSING'}  {rel}")
    manifest_path = p("run/proofs/batch26a_current_repo_truth_file_manifest.sha256")
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    redis = {
        "orders_stream": {"key": REDIS_KEYS["orders_stream"], "xlen": redis_xlen(REDIS_KEYS["orders_stream"])},
        "position_hash": {"key": REDIS_KEYS["position_hash"], "hgetall": redis_hgetall(REDIS_KEYS["position_hash"])},
        "runtime_hash": {"key": REDIS_KEYS["runtime_hash"], "hgetall": redis_hgetall(REDIS_KEYS["runtime_hash"])},
    }

    position_hash = redis["position_hash"]["hgetall"].get("parsed_hash", {})
    position_truth = derive_flat(position_hash)

    config_text = "\n".join(read_text(x) for x in CONFIG_FILES)
    live_true_hits = []
    for rel in CONFIG_FILES:
        live_true_hits.extend(grep(rel, r"(real_live_allowed|allow_live_orders|live_trading|trading_enabled)\s*[:=]\s*(true|1|yes|on)", re.IGNORECASE, 40))

    proof = {
        "batch": "26A_current_repo_truth_v2",
        "generated_at_utc": now_utc(),
        "project_root": str(ROOT),
        "safety_posture": {
            "trading_code_patched": False,
            "runtime_promotion_attempted": False,
            "paper_armed_enabled": False,
            "real_live_enabled": False,
            "services_started": False,
            "redis_writes": False,
        },
        "git_status": {
            "status_short": run_cmd(["git", "status", "--short"], 20),
            "head": run_cmd(["git", "rev-parse", "HEAD"], 20),
        },
        "manifest_path": "run/proofs/batch26a_current_repo_truth_file_manifest.sha256",
        "target_files": {x: file_summary(x) for x in TARGET_FILES},
        "config_files": {x: file_summary(x) for x in CONFIG_FILES},
        "compile_check": compile_check(),
        "import_check": import_check(),
        "redis_readonly_snapshot": redis,
        "position_truth": position_truth,
        "real_live_truth": {
            "live_true_config_hits": live_true_hits,
            "real_live_false_or_not_found": len(live_true_hits) == 0,
        },
        "current_guard_scans": {
            "strategy": {
                "controlled_paper_terms": grep("app/mme_scalpx/services/strategy.py", r"controlled_paper|paper_armed|observe_only|HOLD|report_only|promotion|order_intent", re.IGNORECASE, 120),
            },
            "execution": {
                "broker_call_terms": grep("app/mme_scalpx/services/execution.py", r"place_order|place_entry|send_order|broker|buy|sell|flatten|exit", re.IGNORECASE, 160),
                "arming_terms": grep("app/mme_scalpx/services/execution.py", r"paper_armed|real_live|allow_live|controlled_paper|runtime_mode|observe_only|entry_allowed|orders_allowed", re.IGNORECASE, 160),
            },
            "risk": {
                "entry_veto_terms": grep("app/mme_scalpx/services/risk.py", r"veto|block|deny|reject|entry|paper_armed|real_live|controlled_paper|allow_live", re.IGNORECASE, 160),
                "exit_terms": grep("app/mme_scalpx/services/risk.py", r"exit|flatten|position", re.IGNORECASE, 100),
            },
        },
        "strategy_leaf_stage_state": {fam: scan_leaf(rel) for fam, rel in STRATEGY_LEAVES.items()},
        "misr_event_state": {
            "surface_trap_event_id": grep("app/mme_scalpx/services/feature_family/misr_surface.py", r"trap_event_id", re.IGNORECASE, 120),
            "leaf_trap_event_id": grep("app/mme_scalpx/services/strategy_family/misr.py", r"trap_event_id", re.IGNORECASE, 120),
            "leaf_consumption_terms": grep("app/mme_scalpx/services/strategy_family/misr.py", r"consumed|registry|retry|same.*event|already", re.IGNORECASE, 160),
        },
        "miso_event_state": {
            "surface_burst_event_id": grep("app/mme_scalpx/services/feature_family/miso_surface.py", r"burst_event_id|event_id", re.IGNORECASE, 120),
            "leaf_burst_event_id": grep("app/mme_scalpx/services/strategy_family/miso.py", r"burst_event_id|event_id", re.IGNORECASE, 120),
            "leaf_consumption_terms": grep("app/mme_scalpx/services/strategy_family/miso.py", r"consumed|registry|retry|same.*burst|already", re.IGNORECASE, 160),
        },
        "proof_files": {x: read_json(x) for x in PROOF_FILES},
    }

    derived = {}
    derived["main_py_present"] = p("app/mme_scalpx/main.py").exists()
    derived["controlled_paper_runtime_present"] = p("app/mme_scalpx/services/controlled_paper_runtime.py").exists()
    derived["compile_ok"] = proof["compile_check"].get("returncode") == 0
    derived["imports_ok"] = all(v["ok"] for v in proof["import_check"].values())
    derived["orders_stream_len"] = redis["orders_stream"]["xlen"].get("parsed_int")
    derived["orders_zero"] = derived["orders_stream_len"] == 0
    derived["position_verdict"] = position_truth["verdict"]
    derived["real_live_false_or_not_found"] = proof["real_live_truth"]["real_live_false_or_not_found"]
    derived["execution_has_broker_call_terms"] = bool(proof["current_guard_scans"]["execution"]["broker_call_terms"])
    derived["execution_has_arming_terms"] = bool(proof["current_guard_scans"]["execution"]["arming_terms"])
    derived["risk_has_entry_veto_terms"] = bool(proof["current_guard_scans"]["risk"]["entry_veto_terms"])
    derived["misr_trap_event_id_present"] = bool(proof["misr_event_state"]["surface_trap_event_id"] or proof["misr_event_state"]["leaf_trap_event_id"])
    derived["misr_consumption_terms_present"] = bool(proof["misr_event_state"]["leaf_consumption_terms"])
    derived["miso_burst_event_id_present"] = bool(proof["miso_event_state"]["surface_burst_event_id"] or proof["miso_event_state"]["leaf_burst_event_id"])
    derived["miso_consumption_terms_present"] = bool(proof["miso_event_state"]["leaf_consumption_terms"])
    derived["missing_proof_files"] = [x for x, y in proof["proof_files"].items() if not y["exists"]]
    derived["unparseable_proof_files"] = [x for x, y in proof["proof_files"].items() if y["exists"] and not y["parse_ok"]]
    derived["leaf_optional_stage_patterns_present"] = {
        fam: bool(info["optional_stage_get_patterns"])
        for fam, info in proof["strategy_leaf_stage_state"].items()
    }

    blockers = []
    warnings = []

    if not derived["main_py_present"]:
        blockers.append("MAIN_PY_MISSING")
    if not derived["compile_ok"]:
        blockers.append("COMPILEALL_FAILED")
    if not derived["imports_ok"]:
        blockers.append("IMPORT_CHECK_FAILED")
    if derived["execution_has_broker_call_terms"] and not derived["execution_has_arming_terms"]:
        blockers.append("EXECUTION_BROKER_TERMS_WITHOUT_ARMING_TERMS")
    if not derived["risk_has_entry_veto_terms"]:
        blockers.append("RISK_ENTRY_VETO_TERMS_NOT_PROVEN")
    if derived["position_verdict"] != "FLAT_OR_EMPTY":
        blockers.append("POSITION_NOT_PROVEN_FLAT")
    if not derived["real_live_false_or_not_found"]:
        blockers.append("REAL_LIVE_TRUE_CONFIG_HIT_FOUND")
    if derived["orders_stream_len"] is not None and not derived["orders_zero"]:
        warnings.append("ORDERS_STREAM_LEN_NOT_ZERO_REVIEW_HISTORY_OR_ACTIVE_ORDERS")
    if derived["missing_proof_files"]:
        warnings.append("EXPECTED_PRIOR_PROOF_FILES_MISSING")
    if derived["unparseable_proof_files"]:
        blockers.append("UNPARSEABLE_PRIOR_PROOF_FILES")
    if any(derived["leaf_optional_stage_patterns_present"].values()):
        warnings.append("OPTIONAL_STAGE_GET_PATTERNS_FOUND_IN_STRATEGY_LEAVES")
    if derived["misr_trap_event_id_present"] and not derived["misr_consumption_terms_present"]:
        warnings.append("MISR_TRAP_EVENT_ID_PRESENT_BUT_CONSUMPTION_TERMS_NOT_PROVEN")
    if derived["miso_burst_event_id_present"] and not derived["miso_consumption_terms_present"]:
        warnings.append("MISO_BURST_EVENT_ID_PRESENT_BUT_CONSUMPTION_TERMS_NOT_PROVEN")

    proof["derived_verdicts"] = derived
    proof["final_batch26a_verdict"] = {
        "batch26a_current_repo_truth_ok": len(blockers) == 0,
        "paper_armed_approved": False,
        "real_live_approved": False,
        "runtime_promotion_allowed": False,
        "blockers": blockers,
        "warnings": warnings,
        "recommended_next_batch": "review_batch26a_findings_first" if blockers else "26B_execution_hard_arming_guard_or_next_audit_seam",
        "elapsed_seconds": round(time.time() - started, 3),
    }

    proof_path = p("run/proofs/batch26a_current_repo_truth.json")
    proof_path.write_text(json.dumps(proof, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    milestone_lines = [
        "# Batch 26A — Current Repo Truth + Evidence Repair",
        "",
        f"Date: {datetime.now().date().isoformat()}",
        "",
        "## Verdict",
        "",
        f"- batch26a_current_repo_truth_ok: `{proof['final_batch26a_verdict']['batch26a_current_repo_truth_ok']}`",
        "- paper_armed_approved: `False`",
        "- real_live_approved: `False`",
        "- runtime_promotion_allowed: `False`",
        f"- recommended_next_batch: `{proof['final_batch26a_verdict']['recommended_next_batch']}`",
        "",
        "## Core Truth",
        "",
        f"- main.py present: `{derived['main_py_present']}`",
        f"- controlled_paper_runtime.py present: `{derived['controlled_paper_runtime_present']}`",
        f"- compile_ok: `{derived['compile_ok']}`",
        f"- imports_ok: `{derived['imports_ok']}`",
        f"- orders_stream_len: `{derived['orders_stream_len']}`",
        f"- orders_zero: `{derived['orders_zero']}`",
        f"- position_verdict: `{derived['position_verdict']}`",
        f"- real_live_false_or_not_found: `{derived['real_live_false_or_not_found']}`",
        f"- execution_has_broker_call_terms: `{derived['execution_has_broker_call_terms']}`",
        f"- execution_has_arming_terms: `{derived['execution_has_arming_terms']}`",
        f"- risk_has_entry_veto_terms: `{derived['risk_has_entry_veto_terms']}`",
        "",
        "## MISR / MISO Event Truth",
        "",
        f"- MISR trap_event_id present: `{derived['misr_trap_event_id_present']}`",
        f"- MISR consumption terms present: `{derived['misr_consumption_terms_present']}`",
        f"- MISO burst_event_id present: `{derived['miso_burst_event_id_present']}`",
        f"- MISO consumption terms present: `{derived['miso_consumption_terms_present']}`",
        "",
        "## Strategy Leaf Optional Stage Patterns",
        "",
        "```json",
        json.dumps(derived["leaf_optional_stage_patterns_present"], indent=2, sort_keys=True),
        "```",
        "",
        "## Prior Proof File State",
        "",
        f"- missing_proof_files: `{derived['missing_proof_files']}`",
        f"- unparseable_proof_files: `{derived['unparseable_proof_files']}`",
        "",
        "## Blockers",
        "",
    ]

    if blockers:
        milestone_lines.extend([f"- `{x}`" for x in blockers])
    else:
        milestone_lines.append("- none")

    milestone_lines.extend(["", "## Warnings", ""])
    if warnings:
        milestone_lines.extend([f"- `{x}`" for x in warnings])
    else:
        milestone_lines.append("- none")

    milestone_lines.extend([
        "",
        "## Artifacts",
        "",
        "- `bin/proof_batch26a_current_repo_truth.py`",
        "- `run/proofs/batch26a_current_repo_truth.json`",
        "- `run/proofs/batch26a_current_repo_truth_file_manifest.sha256`",
        "",
        "## Safety",
        "",
        "This batch did not patch trading code, did not start services, did not enable paper_armed, and did not enable real live.",
        "",
    ])

    milestone_path = p(f"docs/milestones/{datetime.now().date().isoformat()}_batch26a_current_repo_truth.md")
    milestone_path.write_text("\n".join(milestone_lines), encoding="utf-8")

    print(json.dumps(proof["final_batch26a_verdict"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
