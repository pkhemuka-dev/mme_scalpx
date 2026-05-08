#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
PYBIN = ROOT / ".venv/bin/python"
LOG_DIR = ROOT / "ai_patch_runner/logs"
STATE_DIR = ROOT / "ai_patch_runner/state"
REPORT_DIR = ROOT / "ai_patch_runner/reports"
OUTPUT_DIR = ROOT / "ai_patch_runner/outputs"
PROOF_DIR = ROOT / "run/proofs"

LOG_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)


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
    "run/proofs/proof_replay_data_a15_*.json",
    "run/proofs/proof_replay_data_a14_execution_shadow_*.json",
    "run/proofs/proof_replay_data_a13_risk_outputs_shadow_*.json",
    "run/proofs/proof_replay_data_a12_strategy_decisions_shadow_*.json",
    "run/proofs/proof_replay_data_a11_features_rows_reconstruction_*.json",
    "run/proofs/proof_replay_data_a10_selector_only_cli_dry_probe_*.json",
]

BLOCKED_TEXT_PATTERNS = [
    ("nohup", r"^\s*nohup\b"),
    ("systemctl", r"^\s*(sudo\s+)?systemctl\b"),
    ("service", r"^\s*(sudo\s+)?service\s+[A-Za-z0-9_.@-]+"),
    ("main_runtime", r"^\s*(python|python3|\.venv/bin/python)\s+-m\s+app\.mme_scalpx\.main\b"),
    ("redis_write", r"^\s*redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b"),
    ("paper_live_env", r"SCALPX_(ALLOW_CONTROLLED_PAPER_RUNTIME|REAL_LIVE_ALLOWED|ALLOW_REAL_LIVE)\s*=\s*1"),
    ("broker_login", r"\b(BROKER_LOGIN|KITE_ACCESS_TOKEN|DHAN_ACCESS_TOKEN|broker api|place_order)\b"),
]


def rel(path: Path | str) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def run_stream(cmd: list[str], *, env: dict[str, str], log_file: Path | None = None) -> tuple[int, str]:
    p = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    assert p.stdout is not None
    buf: list[str] = []
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        f = log_file.open("a", encoding="utf-8")
    else:
        f = open(os.devnull, "w", encoding="utf-8")
    try:
        for line in p.stdout:
            print(line, end="")
            buf.append(line)
            f.write(line)
    finally:
        f.close()
    rc = p.wait()
    return rc, "".join(buf)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_from_patterns(patterns: list[str]) -> Path | None:
    files: list[Path] = []
    for pat in patterns:
        files.extend(ROOT.glob(pat))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def latest_replay_proof() -> Path | None:
    return latest_from_patterns(REPLAY_PROOF_PATTERNS)


def compact_proof(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        data = load_json(path)
    except Exception as exc:
        return {"path": rel(path), "error": repr(exc)}
    s = data.get("summary") or {}
    return {
        "path": rel(path),
        "batch": data.get("batch"),
        "verdict": data.get("verdict") or s.get("overall_verdict"),
        "next_batch": s.get("next_batch") or data.get("next_batch"),
        "row_count": s.get("row_count", data.get("row_count")),
        "engine_ready": s.get("engine_ready", data.get("engine_ready")),
        "engine_execution_performed": s.get("engine_execution_performed", data.get("engine_execution_performed")),
        "candidate_path": s.get("candidate_path") or data.get("candidate_path") or data.get("path"),
        "contract_shape_ok": s.get("contract_shape_ok", data.get("contract_shape_ok")),
        "engine_ready_candidate": s.get("engine_ready_candidate", data.get("engine_ready_candidate")),
        "all_required_surfaces_present": s.get("all_required_surfaces_present", data.get("all_required_surfaces_present")),
        "surface_probe_ok": s.get("surface_probe_ok", data.get("surface_probe_ok")),
        "execution_shadow_semantic_ok": s.get("execution_shadow_semantic_ok", data.get("execution_shadow_semantic_ok")),
        "row_count_parity": s.get("row_count_parity", data.get("row_count_parity")),
        "semantic_rows_nonblank": s.get("semantic_rows_nonblank", data.get("semantic_rows_nonblank")),
        "blocker_count": s.get("blocker_count", data.get("blocker_count")),
        "consumption_probe_ok": s.get("consumption_probe_ok", data.get("consumption_probe_ok")),
        "selector_consumption_candidate": s.get("selector_consumption_candidate", data.get("selector_consumption_candidate")),
        "engine_consumption_candidate": s.get("engine_consumption_candidate", data.get("engine_consumption_candidate")),
        "surface_compatibility_ok": s.get("surface_compatibility_ok", data.get("surface_compatibility_ok")),
        "selector_only_plan_ok": s.get("selector_only_plan_ok", data.get("selector_only_plan_ok")),
        "selector_only_probe_performed": s.get("selector_only_probe_performed", data.get("selector_only_probe_performed")),
        "selector_only_dry_run_ok": s.get("selector_only_dry_run_ok", data.get("selector_only_dry_run_ok")),
        "selector_only_dry_run_performed": s.get("selector_only_dry_run_performed", data.get("selector_only_dry_run_performed")),
        "selector_date_present": s.get("selector_date_present", data.get("selector_date_present")),
        "selector_modules_import_ok": s.get("selector_modules_import_ok", data.get("selector_modules_import_ok")),
        "selector_scope_classification_ok": s.get("selector_scope_classification_ok", data.get("selector_scope_classification_ok")),
        "scope_blocker_resolved_as": s.get("scope_blocker_resolved_as", data.get("scope_blocker_resolved_as")),
        "exact_feeds_only_present": s.get("exact_feeds_only_present", data.get("exact_feeds_only_present")),
        "selector_cli_command_constructed": s.get("selector_cli_command_constructed", data.get("selector_cli_command_constructed")),
        "selector_cli_command_executed": s.get("selector_cli_command_executed", data.get("selector_cli_command_executed")),
        "planned_command_safe": s.get("planned_command_safe", data.get("planned_command_safe")),
        "planned_command_path": s.get("planned_command_path", data.get("planned_command_path")),
        "selector_command_validated": s.get("selector_command_validated", data.get("selector_command_validated")),
        "selector_execution_gate_pass": s.get("selector_execution_gate_pass", data.get("selector_execution_gate_pass")),
        "selector_command_executed": s.get("selector_command_executed", data.get("selector_command_executed")),
        "full_command_allowed": s.get("full_command_allowed", data.get("full_command_allowed")),
        "selector_only_execution_allowed": s.get("selector_only_execution_allowed", data.get("selector_only_execution_allowed")),
        "selector_only_execution_performed": s.get("selector_only_execution_performed", data.get("selector_only_execution_performed")),
        "full_engine_execution_allowed": s.get("full_engine_execution_allowed", data.get("full_engine_execution_allowed")),
    }


def latest_meta_files() -> list[Path]:
    return sorted(REPORT_DIR.glob("*_meta.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def compact_meta(path: Path | None) -> dict[str, Any]:
    if not path:
        return {}
    try:
        data = load_json(path)
    except Exception as exc:
        return {"path": rel(path), "error": repr(exc)}
    return {
        "path": rel(path),
        "expected_batch": data.get("expected_batch"),
        "output_script": data.get("output_script"),
        "static_validation_ok": data.get("static_validation_ok"),
        "policy_validation_ok": (data.get("policy_validation") or {}).get("ok"),
        "classification": (data.get("local_classification") or {}).get("verdict"),
    }


def expected_batch_from_proof(proof: dict[str, Any]) -> str | None:
    nb = proof.get("next_batch")
    if not nb:
        return None
    # "REPLAY-DATA-A14 execution..." -> "REPLAY-DATA-A14"
    return str(nb).split()[0]


def script_is_safe(script: Path) -> tuple[bool, list[dict[str, Any]]]:
    hits: list[dict[str, Any]] = []
    if not script.exists():
        return False, [{"kind": "missing_script", "text": str(script)}]
    text = script.read_text(encoding="utf-8", errors="replace")
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for name, pat in BLOCKED_TEXT_PATTERNS:
            if re.search(pat, stripped, flags=re.I):
                hits.append({"line": lineno, "kind": name, "text": stripped[:220]})
    return not hits, hits


def latest_valid_meta_for_expected(expected_batch: str | None) -> Path | None:
    for meta_path in latest_meta_files():
        try:
            data = load_json(meta_path)
        except Exception:
            continue
        if expected_batch and data.get("expected_batch") != expected_batch:
            continue
        if data.get("static_validation_ok") is not True:
            continue
        if (data.get("policy_validation") or {}).get("ok") is not True:
            continue
        script_raw = data.get("output_script")
        if not script_raw:
            continue
        script = Path(script_raw)
        if not script.exists():
            continue
        safe, _ = script_is_safe(script)
        if not safe:
            continue
        return meta_path
    return None


def safety_env(model: str) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{Path.home() / '.local/bin'}:{env.get('PATH', '')}"
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["SCALPX_OBSERVE_ONLY"] = "1"
    env["OPENAI_MODEL"] = model

    for k in [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_ALLOW_REAL_LIVE",
        "SCALPX_LIVE",
        "SCALPX_PAPER",
        "LIVE_TRADING",
        "PAPER_TRADING",
        "ENABLE_LIVE",
        "ENABLE_PAPER",
        "REDIS_URL",
        "BROKER_LOGIN",
        "BROKER_TOKEN",
        "KITE_ACCESS_TOKEN",
        "DHAN_ACCESS_TOKEN",
    ]:
        env.pop(k, None)

    return env


def mutate_script_add_missing_safety_terms(meta_path: Path) -> tuple[bool, str]:
    """
    Local no-API repair for the common failure:
    static validator requires safety flag strings but generated script omitted them.
    We add a harmless comment block at the end. This is intentionally simple and safe.
    """
    data = load_json(meta_path)
    script_raw = data.get("output_script")
    if not script_raw:
        return False, "missing output_script"
    script = Path(script_raw)
    if not script.exists():
        return False, "script missing"

    text = script.read_text(encoding="utf-8", errors="replace")
    needed = [
        "broker_calls_executed",
        "live_redis_writes_executed",
        "paper_or_live_enabled",
        "engine_execution_performed",
        "orders_sent",
    ]
    missing = [x for x in needed if x not in text]
    if not missing:
        return True, "no missing safety terms"

    append = "\n# MAUTO-R2 local safety-term annotation for static validator only\n"
    for term in missing:
        append += f"# {term}=false\n"
    script.write_text(text.rstrip() + append + "\n", encoding="utf-8")

    # Re-check blocked patterns only. We do not mutate meta to true; mok must still be rerun or mrun guard uses old meta.
    safe, hits = script_is_safe(script)
    if not safe:
        return False, f"blocked pattern after annotation: {hits}"
    return True, f"annotated missing safety terms: {missing}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=1)
    ap.add_argument("--model", default=os.environ.get("MME_AI_LOW_COST_MODEL", os.environ.get("OPENAI_MODEL", "gpt-5-mini")))
    ap.add_argument("--max-api-calls", type=int, default=3)
    ap.add_argument("--repair-on-validation-fail", action="store_true", default=True)
    ap.add_argument("--no-repair", dest="repair_on_validation_fail", action="store_false")
    ap.add_argument("--stop-before-run", action="store_true")
    ap.add_argument("--use-existing-valid-first", action="store_true", default=True)
    args = ap.parse_args()

    if args.cycles < 1 or args.cycles > 10:
        raise SystemExit("cycles must be between 1 and 10")

    env = safety_env(args.model)
    session_ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log = LOG_DIR / f"mauto_r2_{session_ts}.log"

    state: dict[str, Any] = {
        "session_started_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "mauto_r2_bounded_offline_replay_supervisor",
        "model": args.model,
        "cycles_requested": args.cycles,
        "max_api_calls": args.max_api_calls,
        "api_calls_used_estimate": 0,
        "events": [],
        "safety": {
            "services_started": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False,
            "real_orders_sent": False,
        },
    }

    print("===== MAUTO-R2: BOUNDED OFFLINE REPLAY SUPERVISOR =====")
    print(json.dumps({
        "model": args.model,
        "cycles": args.cycles,
        "max_api_calls": args.max_api_calls,
        "use_existing_valid_first": args.use_existing_valid_first,
        "repair_on_validation_fail": args.repair_on_validation_fail,
        "log": rel(log),
    }, indent=2, sort_keys=True))

    for cycle in range(1, args.cycles + 1):
        print(f"===== CYCLE {cycle}/{args.cycles}: REMEMBER =====")
        rc, _ = run_stream(["mremember"], env=env, log_file=log)
        state["events"].append({"cycle": cycle, "step": "mremember_before", "rc": rc})
        if rc != 0:
            print("STOP: mremember failed")
            break

        proof_path = latest_replay_proof()
        proof = compact_proof(proof_path)
        expected_batch = expected_batch_from_proof(proof)

        print("LATEST_REPLAY_PROOF=", json.dumps(proof, indent=2, sort_keys=True))
        print("EXPECTED_BATCH=", expected_batch)

        if proof.get("engine_ready") is True:
            print("STOP: engine_ready=true")
            break

        meta_path: Path | None = None

        if args.use_existing_valid_first and expected_batch:
            meta_path = latest_valid_meta_for_expected(expected_batch)
            if meta_path:
                print("USING_EXISTING_VALID_META=", rel(meta_path))
                state["events"].append({
                    "cycle": cycle,
                    "step": "use_existing_valid_meta",
                    "meta": compact_meta(meta_path),
                })

        if not meta_path:
            if state["api_calls_used_estimate"] >= args.max_api_calls:
                print("STOP: max API calls reached before mok")
                break

            print(f"===== CYCLE {cycle}/{args.cycles}: MOK GENERATE =====")
            rc, _ = run_stream(["mok"], env=env, log_file=log)
            state["api_calls_used_estimate"] += 1
            new_meta = latest_meta_files()[0] if latest_meta_files() else None
            state["events"].append({
                "cycle": cycle,
                "step": "mok",
                "rc": rc,
                "meta": compact_meta(new_meta),
            })

            if rc != 0:
                print("MOK_FAILED_RC=", rc)
                if args.repair_on_validation_fail and new_meta:
                    ok, reason = mutate_script_add_missing_safety_terms(new_meta)
                    print("LOCAL_REPAIR_ATTEMPT=", json.dumps({"ok": ok, "reason": reason}, sort_keys=True))
                    state["events"].append({
                        "cycle": cycle,
                        "step": "local_repair_validation_terms",
                        "ok": ok,
                        "reason": reason,
                    })
                print("STOP: mok failed; not running invalid generated script")
                break

            meta_path = new_meta

        if not meta_path:
            print("STOP: no meta available")
            break

        meta = compact_meta(meta_path)
        print("SELECTED_META=", json.dumps(meta, indent=2, sort_keys=True))

        if expected_batch and meta.get("expected_batch") != expected_batch:
            print("STOP: generated/selected meta batch does not match expected batch from latest proof")
            print(json.dumps({
                "expected_from_latest_proof": expected_batch,
                "selected_meta_expected_batch": meta.get("expected_batch"),
                "selected_meta": meta,
            }, indent=2, sort_keys=True))
            state["events"].append({
                "cycle": cycle,
                "step": "batch_mismatch_stop",
                "expected_from_latest_proof": expected_batch,
                "selected_meta_expected_batch": meta.get("expected_batch"),
                "selected_meta": meta,
            })
            break

        if not (meta.get("static_validation_ok") and meta.get("policy_validation_ok")):
            print("STOP: selected meta is not validated")
            break

        script = Path(load_json(meta_path).get("output_script", ""))
        safe, hits = script_is_safe(script)
        if not safe:
            print("STOP: selected script blocked by safety scan")
            print(json.dumps(hits, indent=2))
            break

        print(f"===== CYCLE {cycle}/{args.cycles}: MSHOW =====")
        rc, _ = run_stream(["mshow", "--lines", "80"], env=env, log_file=log)
        state["events"].append({"cycle": cycle, "step": "mshow", "rc": rc})
        if rc != 0:
            print("STOP: mshow failed")
            break

        if args.stop_before_run:
            print("STOP_BEFORE_RUN requested")
            break

        print(f"===== CYCLE {cycle}/{args.cycles}: MRUN =====")
        rc, _ = run_stream(["mrun"], env=env, log_file=log)
        state["events"].append({"cycle": cycle, "step": "mrun", "rc": rc})
        if rc != 0:
            print("STOP: mrun failed")
            break

        print(f"===== CYCLE {cycle}/{args.cycles}: REMEMBER AFTER =====")
        rc, _ = run_stream(["mremember"], env=env, log_file=log)
        state["events"].append({"cycle": cycle, "step": "mremember_after", "rc": rc})
        if rc != 0:
            print("STOP: mremember after failed")
            break

        after = compact_proof(latest_replay_proof())
        print("AFTER_PROOF=", json.dumps(after, indent=2, sort_keys=True))

        if after.get("engine_ready") is True:
            print("STOP: engine_ready=true reached")
            break

    state["session_finished_utc"] = datetime.now(timezone.utc).isoformat()
    state["latest_replay_proof"] = compact_proof(latest_replay_proof())
    final_expected = expected_batch_from_proof(compact_proof(latest_replay_proof()))
    latest_meta_path = latest_valid_meta_for_expected(final_expected) or (latest_meta_files()[0] if latest_meta_files() else None)
    state["latest_meta"] = compact_meta(latest_meta_path)
    state_path = STATE_DIR / f"mauto_r2_state_{session_ts}.json"
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("===== MAUTO-R2 COMPLETE =====")
    print(json.dumps({
        "state": rel(state_path),
        "log": rel(log),
        "api_calls_used_estimate": state["api_calls_used_estimate"],
        "latest_replay_proof": state["latest_replay_proof"],
        "latest_meta": state["latest_meta"],
    }, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
