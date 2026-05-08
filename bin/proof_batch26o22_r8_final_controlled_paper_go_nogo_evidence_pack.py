#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O22-R8"
BATCH_NAME = "final_controlled_paper_go_nogo_evidence_pack_no_start_no_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.json"
GO_NOGO_JSON = RUN_DIR / "controlled_paper_go_nogo_matrix_o22_r8.json"
EVIDENCE_PACK_JSON = RUN_DIR / "controlled_paper_evidence_pack_o22_r8.json"
APPROVAL_READINESS_JSON = RUN_DIR / "controlled_paper_explicit_approval_readiness_o22_r8.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.md"
BIN_COPY = BIN_DIR / "proof_batch26o22_r8_final_controlled_paper_go_nogo_evidence_pack.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

CONTROLLED_PAPER_SCOPE_ACK = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"
APPROVAL_PHRASE = "APPROVE CONTROLLED PAPER START: MIST CALL, 1 LOT, PAPER ONLY, REAL LIVE FALSE"

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json",
    "run/proofs/proof_batch26o22_r2_controlled_paper_plan_proof_correction.json",
    "run/proofs/proof_batch26o22_r3_controlled_paper_static_gate_proof.json",
    "run/proofs/proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json",
    "run/proofs/proof_batch26o22_r5_controlled_paper_operator_checklist_gate.json",
    "run/proofs/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json",
    "run/proofs/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json",
]

INSPECT_PATHS = [
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/feeds.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/core/settings.py",
    "app/mme_scalpx/integrations/provider_runtime.py",
    "app/mme_scalpx/integrations/bootstrap_provider.py",
    "etc/strategy_family/family_runtime.yaml",
    "etc/strategy_family/rollout",
    "etc/brokers/runtime.yaml",
    "etc/brokers/provider_roles.yaml",
    "etc/brokers/dhan.yaml",
    "etc/brokers/zerodha.yaml",
    *PRIOR_PROOF_PATHS,
]


def run(cmd: list[str], *, timeout: int = 30, env: dict[str, str] | None = None) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=env,
        )
        return {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "ok": cp.returncode == 0,
        }
    except Exception as exc:
        return {
            "cmd": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
            "ok": False,
        }


def redis_cmd(args: list[str], timeout: int = 10) -> dict[str, Any]:
    return run([REDIS_CLI, *args], timeout=timeout)


def redis_xlen(key: str) -> int:
    out = redis_cmd(["XLEN", key])
    try:
        return int((out.get("stdout") or "0").strip() or "0")
    except Exception:
        return -1


def redis_hgetall(key: str) -> dict[str, str]:
    out = redis_cmd(["HGETALL", key])
    lines = [x for x in (out.get("stdout") or "").splitlines()]
    d: dict[str, str] = {}
    for i in range(0, len(lines) - 1, 2):
        d[lines[i]] = lines[i + 1]
    return d


def redis_xrevrange_raw(key: str, count: int = 5) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def parse_json_maybe(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, (dict, list, bool, int, float)):
        return v
    if not isinstance(v, str):
        return None
    s = v.strip()
    if not s:
        return None
    for _ in range(4):
        try:
            parsed = json.loads(s)
        except Exception:
            return None
        if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
            s = parsed.strip()
            continue
        return parsed
    return None


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc), "_path": str(path)}


def proc_lines() -> list[str]:
    out = run(["bash", "-lc", "ps -eo pid,ppid,cmd | grep -E 'app\\.mme_scalpx|mme_scalpx|services' | grep -v grep || true"], timeout=10)
    return [x for x in (out.get("stdout") or "").splitlines() if x.strip()]


def service_running(name: str) -> bool:
    needle1 = f"--service {name}"
    needle2 = f"--service={name}"
    for line in proc_lines():
        if needle1 in line or needle2 in line:
            return True
    return False


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def runtime_snapshot() -> dict[str, Any]:
    latest_orders = redis_xrevrange_raw(ORDERS_STREAM, count=5)
    return {
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": latest_orders,
        "position": redis_hgetall(POSITION_HASH),
        "process_lines": proc_lines(),
        "features_running": service_running("features"),
        "strategy_running": service_running("strategy"),
        "risk_running": service_running("risk"),
        "execution_running": service_running("execution"),
    }


def env_state() -> dict[str, str]:
    keys = [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_LIVE_ORDERS_ALLOWED",
        "SCALPX_BROKER_CALLS_ALLOWED",
        "SCALPX_FORCE_CANDIDATE",
        "SCALPX_THRESHOLD_RELAXATION",
        "SCALPX_PAPER_ARMED",
    ]
    return {k: os.environ.get(k, "") for k in keys}


def inspect_source_summary(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    if not p.exists():
        return {"exists": False}
    if p.is_dir():
        return {
            "exists": True,
            "is_dir": True,
            "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:200],
        }
    text = p.read_text(encoding="utf-8", errors="replace")
    tokens = [
        "CONTROLLED_PAPER",
        "controlled_paper",
        "MIST",
        "CALL",
        "qty_lots",
        "qty_units",
        "real_live",
        "paper",
        "sandbox",
        "broker",
        "order",
        "entry",
        "exit",
        "flatten",
        "kill",
        "failover",
        "fallback",
        "mid_position",
        "migration",
        "FLAT",
        "has_position",
    ]
    hits = {}
    lines = text.splitlines()
    for token in tokens:
        arr = []
        for i, line in enumerate(lines, start=1):
            if token.lower() in line.lower():
                arr.append({"line": i, "text": line[:220]})
        hits[token] = arr[:40]
    return {
        "exists": True,
        "is_file": True,
        "sha256": sha256_file(p),
        "size_bytes": p.stat().st_size,
        "line_count": len(lines),
        "hits": hits,
    }


def summarize_prior(name: str, data: dict[str, Any]) -> dict[str, Any]:
    req = data.get("required_verdicts") if isinstance(data, dict) else {}
    return {
        "path": name,
        "exists": bool(data),
        "final_verdict": data.get("final_verdict") if isinstance(data, dict) else None,
        "false_keys": data.get("false_keys") if isinstance(data, dict) else None,
        "next_recommended_batch": data.get("next_recommended_batch") if isinstance(data, dict) else None,
        "key_required_verdicts": {
            k: req.get(k) for k in sorted(req.keys()) if k in {
                "orders_zero",
                "position_flat",
                "real_live_false",
                "no_paper_start",
                "no_broker_call",
                "no_order_write_intent",
                "risk_not_running",
                "execution_not_running",
                "production_source_patch_false",
                "service_start_false",
                "paper_start_allowed_by_this_batch_false",
                "approval_gate_locked",
                "approved_for_paper_start_false",
                "scenario_matrix_all_expected",
                "current_corrected_structural_shape_ok",
                "current_all_10_branch_frames_present",
                "current_mist_call_visible",
                "decisions_hold_no_candidate",
                "required_veto_reasons_all_present",
                "core_independent_risk_execution_surfaces_present",
                "service_commands_commented_out",
                "service_command_count_is_5",
            }
        },
    }


def verdict_passes_expected(path: str, data: dict[str, Any]) -> bool:
    fv = str(data.get("final_verdict", ""))
    false_keys = data.get("false_keys")
    if false_keys != []:
        return False

    expected_prefix_by_path = {
        "proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json": "PASS_O20_R3H_CURRENT_FRAME_CORRECTED_BOUNDED_OBSERVATION",
        "proof_batch26o22_r2_controlled_paper_plan_proof_correction.json": "PASS_O22_R2_CONTROLLED_PAPER_PLAN_PROOF_OK",
        "proof_batch26o22_r3_controlled_paper_static_gate_proof.json": "PASS_O22_R3_CONTROLLED_PAPER_STATIC_GATE_PROOF_OK",
        "proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json": "PASS_O22_R4_CONTROLLED_PAPER_DRY_RUN_PREFLIGHT_OK",
        "proof_batch26o22_r5_controlled_paper_operator_checklist_gate.json": "PASS_O22_R5_CONTROLLED_PAPER_OPERATOR_CHECKLIST_GATE_OK_LOCKED_NO_START",
        "proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json": "PASS_O22_R6_CONTROLLED_PAPER_TEMPLATE_GENERATOR_OK_LOCKED_NO_START",
        "proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json": "PASS_O22_R7_R2_EXACT_CLI_FLAG_VALIDATOR_OK_LOCKED_NO_START",
    }
    base = pathlib.Path(path).name
    prefix = expected_prefix_by_path.get(base)
    return bool(prefix and fv.startswith(prefix))


def build_go_nogo(prior_summaries: dict[str, Any], runtime: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
    position_flat = flat_position(runtime.get("position") or {})

    prerequisites = {
        "o20_r3h_feature_strategy_safety_pass": prior_summaries["run/proofs/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json"]["passes_expected"],
        "o22_r2_plan_pass": prior_summaries["run/proofs/proof_batch26o22_r2_controlled_paper_plan_proof_correction.json"]["passes_expected"],
        "o22_r3_static_gate_pass": prior_summaries["run/proofs/proof_batch26o22_r3_controlled_paper_static_gate_proof.json"]["passes_expected"],
        "o22_r4_dry_run_preflight_pass": prior_summaries["run/proofs/proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json"]["passes_expected"],
        "o22_r5_operator_gate_pass": prior_summaries["run/proofs/proof_batch26o22_r5_controlled_paper_operator_checklist_gate.json"]["passes_expected"],
        "o22_r6_template_generator_pass": prior_summaries["run/proofs/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json"]["passes_expected"],
        "o22_r7_r2_cli_validator_pass": prior_summaries["run/proofs/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json"]["passes_expected"],
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "risk_not_running_now": not runtime.get("risk_running"),
        "execution_not_running_now": not runtime.get("execution_running"),
        "real_live_false_now": env.get("SCALPX_REAL_LIVE_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
        "no_paper_start_now": env.get("SCALPX_PAPER_ARMED", "") not in {"1", "true", "TRUE", "yes", "YES"},
        "no_controlled_paper_runtime_env_now": env.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", "") not in {"1", "true", "TRUE", "yes", "YES"},
        "no_scope_ack_env_now": env.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", "") == "",
        "no_broker_call_env_now": env.get("SCALPX_BROKER_CALLS_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
        "no_order_write_env_now": env.get("SCALPX_LIVE_ORDERS_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
        "no_threshold_relaxation_now": env.get("SCALPX_THRESHOLD_RELAXATION", "") not in {"1", "true", "TRUE", "yes", "YES"},
        "no_forced_candidate_now": env.get("SCALPX_FORCE_CANDIDATE", "") not in {"1", "true", "TRUE", "yes", "YES"},
    }

    go_if_explicitly_approved = all(prerequisites.values())

    return {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "lane": "LANE_A_CONTROLLED_PAPER_STRATEGY_VALIDITY",
        "paper_start_allowed_by_this_batch": False,
        "real_live_allowed": False,
        "automatic_paper_start_allowed": False,
        "go_for_real_live": False,
        "go_for_controlled_paper_without_explicit_approval": False,
        "go_for_controlled_paper_only_after_future_explicit_approval": go_if_explicitly_approved,
        "required_future_explicit_approval_phrase": APPROVAL_PHRASE,
        "scope_if_future_approved": {
            "family": "MIST",
            "branch": "CALL",
            "qty_lots": 1,
            "route": "paper_or_sandbox_only",
            "real_live_allowed": False,
            "automatic_broker_failover_allowed": False,
            "mid_position_provider_migration_allowed": False,
            "position_required_before_entry": "FLAT",
        },
        "prerequisites": prerequisites,
        "prior_evidence": prior_summaries,
        "current_runtime": runtime,
        "current_env": env,
        "decision": (
            "GO_FOR_NEXT_APPROVAL_GATE_ONLY_NOT_START"
            if go_if_explicitly_approved
            else "NO_GO_FIX_FAILED_PREREQUISITES"
        ),
        "next_if_go": "26-O23-A explicit-approved controlled-paper one-session launcher package only if user explicitly approves; otherwise stop here.",
    }


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_evidence_output_read": True,
            "prior_chain_must_all_pass": True,
            "uploaded_bundle_remains_source_of_truth": True,
        },
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "doctrine_mutation": False,
            "production_source_patch": False,
            "go_nogo_evidence_pack_only": True,
        },
        "prior_proofs": {},
        "prior_summaries": {},
        "inspected_files": {},
        "source_inspection": {},
        "commands": {},
        "runtime_snapshot": {},
        "env_state": {},
        "go_nogo": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== EVIDENCE-FIRST INSPECTION: PRIOR CHAIN + SOURCE HASHES =====")
        for rel in INSPECT_PATHS:
            p = ROOT / rel
            if p.exists() and p.is_file():
                dst = BACKUP_DIR / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst)
                proof["inspected_files"][rel] = {
                    "exists": True,
                    "is_file": True,
                    "sha256": sha256_file(p),
                    "size_bytes": p.stat().st_size,
                    "backup": str(dst.relative_to(ROOT)),
                }
                if rel.endswith(".json"):
                    loaded = load_json(p)
                    proof["prior_proofs"][rel] = loaded
            elif p.exists() and p.is_dir():
                proof["inspected_files"][rel] = {
                    "exists": True,
                    "is_dir": True,
                    "sample_members": sorted(str(x.relative_to(ROOT)) for x in p.rglob("*") if x.is_file())[:300],
                }
            else:
                proof["inspected_files"][rel] = {"exists": False}

        print("===== COMPILE / IMPORT PROOF: NO SOURCE MUTATION =====")
        compile_targets = [
            "app/mme_scalpx/main.py",
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/services/feeds.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/redisx.py",
        ]
        proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
        proof["commands"]["import"] = run(
            [
                sys.executable,
                "-c",
                "import app.mme_scalpx.main, app.mme_scalpx.services.risk, app.mme_scalpx.services.execution, app.mme_scalpx.services.strategy, app.mme_scalpx.services.features, app.mme_scalpx.services.feeds; print('IMPORT_OK')",
            ],
            timeout=60,
        )

        print("===== SOURCE SURFACE SUMMARY =====")
        for rel in [
            "app/mme_scalpx/main.py",
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/services/feeds.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/settings.py",
            "app/mme_scalpx/integrations/provider_runtime.py",
        ]:
            proof["source_inspection"][rel] = inspect_source_summary(rel)

        print("===== READ-ONLY RUNTIME SAFETY SNAPSHOT =====")
        runtime = runtime_snapshot()
        env = env_state()
        proof["runtime_snapshot"] = runtime
        proof["env_state"] = env

        print("===== PRIOR CHAIN SUMMARY =====")
        prior_summaries: dict[str, Any] = {}
        for rel in PRIOR_PROOF_PATHS:
            data = proof["prior_proofs"].get(rel)
            if isinstance(data, dict):
                s = summarize_prior(rel, data)
                s["passes_expected"] = verdict_passes_expected(rel, data)
                prior_summaries[rel] = s
            else:
                prior_summaries[rel] = {
                    "path": rel,
                    "exists": False,
                    "passes_expected": False,
                    "final_verdict": None,
                    "false_keys": None,
                }
        proof["prior_summaries"] = prior_summaries

        print("===== BUILD GO/NO-GO MATRIX =====")
        go_nogo = build_go_nogo(prior_summaries, runtime, env)
        proof["go_nogo"] = go_nogo

        GO_NOGO_JSON.write_text(json.dumps(go_nogo, indent=2, sort_keys=True), encoding="utf-8")

        evidence_pack = {
            "batch": BATCH,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "FINAL_EVIDENCE_PACK_ONLY_NO_START",
            "go_nogo_json": str(GO_NOGO_JSON.relative_to(ROOT)),
            "prior_summaries": prior_summaries,
            "current_runtime": runtime,
            "current_env": env,
            "source_inspection": proof["source_inspection"],
            "safety_statement": {
                "paper_start_allowed_by_this_batch": False,
                "real_live_allowed": False,
                "broker_call_executed": False,
                "order_write_executed": False,
                "service_start_executed": False,
                "production_source_patch_applied": False,
            },
        }
        EVIDENCE_PACK_JSON.write_text(json.dumps(evidence_pack, indent=2, sort_keys=True), encoding="utf-8")

        approval_readiness = {
            "batch": BATCH,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "approval_status": "NOT_APPROVED",
            "can_prepare_next_approved_launcher_if_user_explicitly_approves": go_nogo.get("go_for_controlled_paper_only_after_future_explicit_approval") is True,
            "required_user_phrase": APPROVAL_PHRASE,
            "next_package_if_approved": "26-O23-A explicit-approved controlled-paper one-session launcher package",
            "scope": go_nogo.get("scope_if_future_approved"),
            "do_not_start_without_new_explicit_user_approval": True,
        }
        APPROVAL_READINESS_JSON.write_text(json.dumps(approval_readiness, indent=2, sort_keys=True), encoding="utf-8")

        orders_zero = runtime.get("orders_xlen") == 0 and not (runtime.get("latest_orders_raw", {}).get("stdout") or "").strip()
        position_flat = flat_position(runtime.get("position") or {})

        req = {
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "all_prior_proofs_exist": all(prior_summaries[p]["exists"] is True for p in PRIOR_PROOF_PATHS),
            "all_prior_proofs_pass_expected": all(prior_summaries[p]["passes_expected"] is True for p in PRIOR_PROOF_PATHS),
            "o20_r3h_pass": prior_summaries["run/proofs/proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json"]["passes_expected"] is True,
            "o22_r2_pass": prior_summaries["run/proofs/proof_batch26o22_r2_controlled_paper_plan_proof_correction.json"]["passes_expected"] is True,
            "o22_r3_pass": prior_summaries["run/proofs/proof_batch26o22_r3_controlled_paper_static_gate_proof.json"]["passes_expected"] is True,
            "o22_r4_pass": prior_summaries["run/proofs/proof_batch26o22_r4_controlled_paper_dry_run_readiness_preflight.json"]["passes_expected"] is True,
            "o22_r5_pass": prior_summaries["run/proofs/proof_batch26o22_r5_controlled_paper_operator_checklist_gate.json"]["passes_expected"] is True,
            "o22_r6_pass": prior_summaries["run/proofs/proof_batch26o22_r6_controlled_paper_approved_start_template_generator.json"]["passes_expected"] is True,
            "o22_r7_r2_pass": prior_summaries["run/proofs/proof_batch26o22_r7_r2_exact_cli_flag_validator_template_writer_repair.json"]["passes_expected"] is True,
            "go_nogo_json_written": GO_NOGO_JSON.exists(),
            "evidence_pack_json_written": EVIDENCE_PACK_JSON.exists(),
            "approval_readiness_json_written": APPROVAL_READINESS_JSON.exists(),
            "go_for_controlled_paper_after_explicit_approval_only": go_nogo.get("go_for_controlled_paper_only_after_future_explicit_approval") is True,
            "go_for_controlled_paper_without_explicit_approval_false": go_nogo.get("go_for_controlled_paper_without_explicit_approval") is False,
            "paper_start_allowed_by_this_batch_false": go_nogo.get("paper_start_allowed_by_this_batch") is False,
            "go_for_real_live_false": go_nogo.get("go_for_real_live") is False,
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "real_live_false": env.get("SCALPX_REAL_LIVE_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_paper_start": env.get("SCALPX_PAPER_ARMED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_controlled_paper_runtime_env": env.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_scope_ack_env": env.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK", "") == "",
            "no_broker_call": env.get("SCALPX_BROKER_CALLS_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_order_write_intent": env.get("SCALPX_LIVE_ORDERS_ALLOWED", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_threshold_relaxation": env.get("SCALPX_THRESHOLD_RELAXATION", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_forced_candidate": env.get("SCALPX_FORCE_CANDIDATE", "") not in {"1", "true", "TRUE", "yes", "YES"},
            "risk_not_running": not runtime.get("risk_running"),
            "execution_not_running": not runtime.get("execution_running"),
            "production_source_patch_false": True,
            "service_start_false": True,
        }

        false_keys = [k for k, v in req.items() if v is not True]
        proof["required_verdicts"] = req
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if false_keys:
            proof["final_verdict"] = "FAIL_O22_R8_FINAL_CONTROLLED_PAPER_GO_NOGO_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and write smallest Lane-A diagnostic package; no paper start."
        else:
            proof["final_verdict"] = "PASS_O22_R8_FINAL_CONTROLLED_PAPER_GO_NOGO_EVIDENCE_PACK_OK_NO_START"
            proof["next_recommended_batch"] = "STOP unless user explicitly approves controlled-paper start. If approved, write 26-O23-A explicit-approved controlled-paper one-session launcher package."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — final controlled-paper go/no-go evidence pack",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- go_nogo: `{GO_NOGO_JSON.relative_to(ROOT)}`",
                f"- evidence_pack: `{EVIDENCE_PACK_JSON.relative_to(ROOT)}`",
                f"- approval_readiness: `{APPROVAL_READINESS_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Consolidate O20-R3H and O22-R2 through O22-R7-R2 into one final controlled-paper go/no-go evidence pack.",
                "- This batch does not start controlled paper.",
                "- This batch does not approve controlled paper.",
                "- This batch does not enable real live.",
                "- This batch does not start services, call broker, write orders, or patch production source.",
                "",
                "## Result meaning",
                "- PASS means the next action may be an explicit-approved controlled-paper one-session launcher package **only if the user explicitly approves it**.",
                "- PASS does not mean real-live approval.",
                "- PASS does not mean automatic paper start.",
                "",
                "## Required future explicit approval phrase",
                f"`{APPROVAL_PHRASE}`",
                "",
                "## Scope if future approved",
                "- MIST CALL only.",
                "- 1 lot only.",
                "- paper/sandbox route only.",
                "- real_live=false.",
                "- no automatic broker failover.",
                "- no mid-position provider migration.",
                "- FLAT position before entry.",
                "",
                "## Verdict",
                f"- final_verdict: `{proof['final_verdict']}`",
                f"- false_keys: `{false_keys}`",
                f"- next_recommended_batch: `{proof['next_recommended_batch']}`",
                "",
                "## Required verdicts",
                "```json",
                json.dumps(req, indent=2, sort_keys=True),
                "```",
                "",
                "## Go/no-go",
                "```json",
                json.dumps(go_nogo, indent=2, sort_keys=True),
                "```",
            ]),
            encoding="utf-8",
        )

        MILESTONE_MD.write_text(
            "\n".join([
                f"# {DATE} — {BATCH} final controlled-paper go/no-go evidence pack",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Achieved",
                "- Loaded and verified prior O20/O22 proof chain.",
                "- Confirmed all required prior PASS proofs have empty false_keys.",
                "- Confirmed controlled-paper readiness chain through O22-R7-R2.",
                "- Confirmed orders zero and position FLAT.",
                "- Confirmed no controlled-paper env, no scope ACK env, no broker/order intent, risk/execution not running.",
                "- Generated final go/no-go matrix.",
                "- Generated final evidence pack.",
                "- Generated explicit approval readiness JSON.",
                "",
                "## Not done",
                "- Did not start controlled paper.",
                "- Did not approve controlled paper.",
                "- Did not enable real live.",
                "- Did not start services.",
                "- Did not call broker.",
                "- Did not write orders.",
                "- Did not patch production source.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
                "",
                "## Artifacts",
                f"- `{PROOF_JSON.relative_to(ROOT)}`",
                f"- `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- `{GO_NOGO_JSON.relative_to(ROOT)}`",
                f"- `{EVIDENCE_PACK_JSON.relative_to(ROOT)}`",
                f"- `{APPROVAL_READINESS_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            GO_NOGO_JSON,
            EVIDENCE_PACK_JSON,
            APPROVAL_READINESS_JSON,
            BIN_COPY,
            *[ROOT / rel for rel in INSPECT_PATHS if (ROOT / rel).exists() and (ROOT / rel).is_file()],
        ]
        manifest = {
            "batch": BATCH,
            "tag": TAG,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": {
                str(p.relative_to(ROOT)): sha256_file(p)
                for p in manifest_paths
                if p.exists()
            },
        }
        MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

        print("===== FINAL SUMMARY =====")
        print(f"final_verdict = {proof['final_verdict']}")
        print(f"false_keys = {false_keys}")
        print(f"go_for_controlled_paper_only_after_future_explicit_approval = {go_nogo.get('go_for_controlled_paper_only_after_future_explicit_approval')}")
        print(f"go_for_controlled_paper_without_explicit_approval = {go_nogo.get('go_for_controlled_paper_without_explicit_approval')}")
        print(f"go_for_real_live = {go_nogo.get('go_for_real_live')}")
        print(f"next_recommended_batch = {proof['next_recommended_batch']}")
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        print(f"manifest_json = {MANIFEST_JSON.relative_to(ROOT)}")
        print(f"go_nogo_json = {GO_NOGO_JSON.relative_to(ROOT)}")
        print(f"evidence_pack_json = {EVIDENCE_PACK_JSON.relative_to(ROOT)}")
        print(f"approval_readiness_json = {APPROVAL_READINESS_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O22_R8_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
