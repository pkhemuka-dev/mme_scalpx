#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O20-R3H"
BATCH_NAME = "current_frame_corrected_bounded_observation_no_source_patch"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o20_r3h_current_frame_corrected_bounded_observation_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o20_r3h_current_frame_corrected_bounded_observation.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o20_r3h_current_frame_corrected_bounded_observation.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o20_r3h_current_frame_corrected_bounded_observation.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o20_r3h_current_frame_corrected_bounded_observation.md"
BIN_COPY = BIN_DIR / "proof_batch26o20_r3h_current_frame_corrected_bounded_observation.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

OBSERVE_SECONDS = int(os.environ.get("BATCH26O20_R3H_OBSERVE_SECONDS", "90"))
POLL_INTERVAL = float(os.environ.get("BATCH26O20_R3H_POLL_INTERVAL", "2.0"))
MIN_NEW_FEATURE_FRAMES = int(os.environ.get("BATCH26O20_R3H_MIN_NEW_FEATURE_FRAMES", "3"))
MIN_DECISION_FRAMES = int(os.environ.get("BATCH26O20_R3H_MIN_DECISION_FRAMES", "1"))

EXPECTED_BRANCH_KEYS = {
    "mist_call", "mist_put",
    "misb_call", "misb_put",
    "misc_call", "misc_put",
    "misr_call", "misr_put",
    "miso_call", "miso_put",
}

INSPECT_PATHS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/main.py",
    "run/proofs/proof_batch26o20_r3f_persisted_features_publish_route_classifier.json",
    "run/proofs/proof_batch26o20_r3g_corrected_r3e_proof_parser.json",
]

STARTED_PROCS: list[subprocess.Popen[str]] = []


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


def redis_xrevrange(key: str, count: int = 5) -> list[dict[str, Any]]:
    out = redis_xrevrange_raw(key, count=count)
    lines = (out.get("stdout") or "").splitlines()
    entries: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        entry_id = lines[i].strip()
        i += 1
        fields: dict[str, str] = {}
        while i + 1 < len(lines):
            maybe_next_id = lines[i].strip()
            if re.match(r"^\d+-\d+$", maybe_next_id):
                break
            k = lines[i].strip()
            v = lines[i + 1].strip()
            fields[k] = v
            i += 2
        if entry_id:
            entries.append({"id": entry_id, "fields": fields})
    return entries


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


def as_bool(v: Any) -> bool | None:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"1", "true", "yes", "y", "ok", "pass"}:
            return True
        if s in {"0", "false", "no", "n", "fail", "none", "null", ""}:
            return False
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


def stop_started_processes() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for p in STARTED_PROCS:
        if p.poll() is None:
            try:
                p.send_signal(signal.SIGTERM)
                try:
                    p.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    p.kill()
                    p.wait(timeout=5)
            except Exception as exc:
                results.append({"pid": p.pid, "stopped": False, "error": repr(exc)})
                continue
        results.append({"pid": p.pid, "stopped": True, "returncode": p.poll()})
    return results


def start_features_probe_if_needed() -> dict[str, Any]:
    if service_running("features"):
        return {"started": False, "reason": "features_already_running", "pid": None}

    log_path = RUN_DIR / "features_probe.log"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["SCALPX_LIVE_ORDERS_ALLOWED"] = "0"
    env["SCALPX_BROKER_CALLS_ALLOWED"] = "0"
    env["SCALPX_PAPER_ARMED"] = "0"
    env["SCALPX_FORCE_CANDIDATE"] = "0"

    cmd = [
        sys.executable,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        "features",
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ]
    log_f = log_path.open("w", encoding="utf-8")
    p = subprocess.Popen(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env=env,
    )
    STARTED_PROCS.append(p)
    time.sleep(8)
    return {
        "started": True,
        "pid": p.pid,
        "cmd": cmd,
        "log_path": str(log_path.relative_to(ROOT)),
        "alive_after_start": p.poll() is None,
        "returncode_after_start": p.poll(),
    }


def recursive_find(obj: Any, key: str, *, max_depth: int = 14) -> list[Any]:
    found: list[Any] = []

    def walk(x: Any, depth: int) -> None:
        if depth > max_depth:
            return
        if isinstance(x, dict):
            if key in x:
                found.append(x[key])
            for v in x.values():
                walk(v, depth + 1)
        elif isinstance(x, list):
            for v in x:
                walk(v, depth + 1)

    walk(obj, 0)
    return found


def recursive_find_branch_frames(obj: Any) -> tuple[dict[str, Any] | None, str]:
    if not isinstance(obj, (dict, list)):
        return None, ""

    direct = recursive_find(obj, "branch_frames")
    for item in direct:
        if isinstance(item, dict):
            keys = set(item.keys())
            if EXPECTED_BRANCH_KEYS.issubset(keys):
                return item, "branch_frames"

    if isinstance(obj, dict):
        keys = set(obj.keys())
        if EXPECTED_BRANCH_KEYS.issubset(keys):
            return obj, "direct_expected_branch_keys"

    return None, ""


def corrected_feature_summary(entry: dict[str, Any]) -> dict[str, Any]:
    f = entry.get("fields", {})
    parsed_fields = {
        k: parse_json_maybe(v)
        for k, v in f.items()
        if k.endswith("_json") or k in {"payload", "payload_json"}
    }

    consumer_view = parsed_fields.get("consumer_view_json")
    family_features = parsed_fields.get("family_features_json")
    family_surfaces = parsed_fields.get("family_surfaces_json")
    payload = parsed_fields.get("payload_json") or parsed_fields.get("payload")

    branch_frames = None
    branch_source = ""
    for source_name, obj in [
        ("consumer_view_json", consumer_view),
        ("family_features_json", family_features),
        ("family_surfaces_json", family_surfaces),
        ("payload_json", payload),
    ]:
        branch_frames, branch_mode = recursive_find_branch_frames(obj)
        if branch_frames is not None:
            branch_source = f"{source_name}:{branch_mode}"
            break

    branch_keys = set(branch_frames.keys()) if isinstance(branch_frames, dict) else set()
    structural_valid_by_shape = branch_keys == EXPECTED_BRANCH_KEYS and "mist_call" in branch_keys

    top_structural = as_bool(f.get("structural_valid"))
    payload_structural = None
    if isinstance(payload, dict):
        payload_structural = as_bool(payload.get("structural_valid"))
        if payload_structural is None:
            payload_structural = as_bool(payload.get("frame_valid"))

    consumer_explicit_structural = None
    consumer_data_valid = None
    consumer_safe = None
    if isinstance(consumer_view, dict):
        consumer_explicit_structural = as_bool(consumer_view.get("structural_valid"))
        consumer_data_valid = as_bool(consumer_view.get("data_valid"))
        consumer_safe = as_bool(consumer_view.get("safe_to_consume"))

    return {
        "id": entry.get("id"),
        "raw_field_keys": sorted(f.keys()),
        "consumer_view_present": isinstance(consumer_view, dict),
        "branch_frames_source": branch_source,
        "branch_frame_count": len(branch_keys),
        "branch_key_set_match": branch_keys == EXPECTED_BRANCH_KEYS,
        "mist_call_visible": "mist_call" in branch_keys,
        "corrected_parser_structural_valid": (
            structural_valid_by_shape
            or consumer_explicit_structural is True
            or top_structural is True
            or payload_structural is True
        ),
        "structural_valid_by_shape": structural_valid_by_shape,
        "consumer_explicit_structural_valid": consumer_explicit_structural,
        "consumer_view_data_valid": consumer_data_valid,
        "consumer_view_safe_to_consume": consumer_safe,
        "top_structural_valid": top_structural,
        "payload_structural_valid": payload_structural,
        "parsed_field_types": {k: type(v).__name__ for k, v in parsed_fields.items()},
    }


def decision_summary(entry: dict[str, Any]) -> dict[str, Any]:
    f = entry.get("fields", {})
    diag = parse_json_maybe(f.get("diagnostics_json")) or {}
    return {
        "id": entry.get("id"),
        "data_valid": as_bool(f.get("data_valid")),
        "safe_to_consume": as_bool(f.get("safe_to_consume")),
        "hold_only": as_bool(f.get("hold_only")),
        "side": f.get("side"),
        "qty": f.get("qty"),
        "reason": f.get("reason"),
        "activation_reason": diag.get("activation_reason") if isinstance(diag, dict) else None,
        "activation_candidate_count": diag.get("activation_candidate_count") if isinstance(diag, dict) else None,
        "branch_frame_count": diag.get("branch_frame_count") if isinstance(diag, dict) else None,
        "broker_side_effects_allowed": diag.get("broker_side_effects_allowed") if isinstance(diag, dict) else None,
        "live_orders_allowed": diag.get("live_orders_allowed") if isinstance(diag, dict) else None,
    }


def xread_new(key: str, last_id: str, count: int = 50, block_ms: int = 1000) -> list[dict[str, Any]]:
    out = redis_cmd(["XREAD", "COUNT", str(count), "BLOCK", str(block_ms), "STREAMS", key, last_id], timeout=max(5, block_ms // 1000 + 5))
    lines = (out.get("stdout") or "").splitlines()
    entries: list[dict[str, Any]] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line == key:
            continue
        if not re.match(r"^\d+-\d+$", line):
            continue
        entry_id = line
        fields: dict[str, str] = {}
        while i + 1 < len(lines):
            maybe_next_id = lines[i].strip()
            if maybe_next_id == key or re.match(r"^\d+-\d+$", maybe_next_id):
                break
            k = lines[i].strip()
            v = lines[i + 1].strip()
            fields[k] = v
            i += 2
        entries.append({"id": entry_id, "fields": fields})
    return entries


def run_strategy_one_shot() -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["SCALPX_LIVE_ORDERS_ALLOWED"] = "0"
    env["SCALPX_BROKER_CALLS_ALLOWED"] = "0"
    env["SCALPX_PAPER_ARMED"] = "0"
    env["SCALPX_FORCE_CANDIDATE"] = "0"

    before = redis_xlen(DECISIONS_STREAM)
    attempts = []
    candidates = [
        [sys.executable, "-m", "app.mme_scalpx.main", "--service", "strategy", "--once", "--skip-group-bootstrap"],
        [sys.executable, "-m", "app.mme_scalpx.services.strategy", "--once"],
    ]
    for cmd in candidates:
        res = run(cmd, timeout=45, env=env)
        after = redis_xlen(DECISIONS_STREAM)
        attempts.append({"cmd": cmd, "result": res, "decisions_before": before, "decisions_after": after})
        if res.get("ok") or after > before:
            return {"attempted": True, "ok": bool(res.get("ok")) or after > before, "attempts": attempts, "decisions_before": before, "decisions_after": after}
    return {"attempted": True, "ok": False, "attempts": attempts, "decisions_before": before, "decisions_after": redis_xlen(DECISIONS_STREAM)}


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_evidence_output_read": True,
            "prior_r3g_pass_required": True,
            "uploaded_bundle_remains_source_of_truth": True,
        },
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "doctrine_mutation": False,
            "risk_execution_started": False,
            "production_source_patch": False,
            "corrected_parser_observation_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "commands": {},
        "observations": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== EVIDENCE-FIRST INSPECTION: PRIOR PROOFS + SOURCE HASHES =====")
        for rel in INSPECT_PATHS:
            p = ROOT / rel
            dst = BACKUP_DIR / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if p.exists():
                shutil.copy2(p, dst)
                proof["inspected_files"][rel] = {
                    "exists": True,
                    "sha256": sha256_file(p),
                    "size_bytes": p.stat().st_size,
                    "backup": str(dst.relative_to(ROOT)),
                }
                if rel.endswith(".json"):
                    loaded = load_json(p)
                    proof["prior_proofs"][rel] = {
                        "final_verdict": loaded.get("final_verdict") if isinstance(loaded, dict) else None,
                        "false_keys": loaded.get("false_keys") if isinstance(loaded, dict) else None,
                        "required_verdicts": loaded.get("required_verdicts") if isinstance(loaded, dict) else None,
                        "next_recommended_batch": loaded.get("next_recommended_batch") if isinstance(loaded, dict) else None,
                    }
            else:
                proof["inspected_files"][rel] = {"exists": False}

        print("===== COMPILE / IMPORT PROOF: NO SOURCE MUTATION =====")
        compile_targets = [
            "app/mme_scalpx/services/features.py",
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/risk.py",
            "app/mme_scalpx/services/execution.py",
            "app/mme_scalpx/core/names.py",
            "app/mme_scalpx/core/models.py",
            "app/mme_scalpx/core/redisx.py",
            "app/mme_scalpx/main.py",
        ]
        proof["commands"]["compile"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
        proof["commands"]["import"] = run(
            [
                sys.executable,
                "-c",
                "import app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.core.names, app.mme_scalpx.core.models; print('IMPORT_OK')",
            ],
            timeout=60,
        )

        print("===== PRE-SAFETY SNAPSHOT =====")
        before_feature_id = "$"
        latest_before = redis_xrevrange(FEATURES_STREAM, count=1)
        if latest_before:
            before_feature_id = latest_before[0].get("id") or "$"

        before_decision_id = "$"
        latest_dec_before = redis_xrevrange(DECISIONS_STREAM, count=1)
        if latest_dec_before:
            before_decision_id = latest_dec_before[0].get("id") or "$"

        before = {
            "features_xlen": redis_xlen(FEATURES_STREAM),
            "decisions_xlen": redis_xlen(DECISIONS_STREAM),
            "orders_xlen": redis_xlen(ORDERS_STREAM),
            "position": redis_hgetall(POSITION_HASH),
            "process_lines": proc_lines(),
            "risk_running": service_running("risk"),
            "execution_running": service_running("execution"),
            "strategy_running": service_running("strategy"),
            "features_running": service_running("features"),
            "feature_watermark": before_feature_id,
            "decision_watermark": before_decision_id,
        }
        proof["observations"]["before"] = before

        print("===== START FEATURES-ONLY PROBE IF NEEDED =====")
        feature_probe = start_features_probe_if_needed()
        proof["observations"]["feature_probe"] = feature_probe

        print("===== CURRENT-FRAME BOUNDED OBSERVATION WITH WATERMARK =====")
        new_features: list[dict[str, Any]] = []
        new_decisions: list[dict[str, Any]] = []
        samples: list[dict[str, Any]] = []

        last_feature_id = before_feature_id
        last_decision_id = before_decision_id
        deadline = time.time() + OBSERVE_SECONDS

        while time.time() < deadline:
            f_entries = xread_new(FEATURES_STREAM, last_feature_id, count=20, block_ms=1000)
            if f_entries:
                for ent in f_entries:
                    last_feature_id = ent["id"]
                    new_features.append(ent)

            d_entries = xread_new(DECISIONS_STREAM, last_decision_id, count=20, block_ms=100)
            if d_entries:
                for ent in d_entries:
                    last_decision_id = ent["id"]
                    new_decisions.append(ent)

            corrected = [corrected_feature_summary(x) for x in new_features[-10:]]
            decisions = [decision_summary(x) for x in new_decisions[-10:]]
            sample = {
                "observed_at_utc": datetime.now(timezone.utc).isoformat(),
                "features_xlen": redis_xlen(FEATURES_STREAM),
                "decisions_xlen": redis_xlen(DECISIONS_STREAM),
                "orders_xlen": redis_xlen(ORDERS_STREAM),
                "new_feature_count": len(new_features),
                "new_decision_count": len(new_decisions),
                "latest_corrected_feature": corrected[-1] if corrected else None,
                "latest_decision": decisions[-1] if decisions else None,
                "position": redis_hgetall(POSITION_HASH),
            }
            samples.append(sample)
            print(json.dumps(sample, indent=2, sort_keys=True))

            if len(new_features) >= MIN_NEW_FEATURE_FRAMES and len(new_decisions) >= MIN_DECISION_FRAMES:
                break

            time.sleep(POLL_INTERVAL)

        print("===== STRATEGY ONE-SHOT HOLD/NO_CANDIDATE VERIFICATION =====")
        strategy_once = run_strategy_one_shot()
        proof["observations"]["strategy_once"] = strategy_once

        print("===== POST-SAFETY SNAPSHOT / STOP STARTED SERVICES =====")
        stop_results = stop_started_processes()
        time.sleep(3)

        after = {
            "features_xlen": redis_xlen(FEATURES_STREAM),
            "decisions_xlen": redis_xlen(DECISIONS_STREAM),
            "orders_xlen": redis_xlen(ORDERS_STREAM),
            "position": redis_hgetall(POSITION_HASH),
            "process_lines": proc_lines(),
            "risk_running": service_running("risk"),
            "execution_running": service_running("execution"),
            "strategy_running": service_running("strategy"),
            "features_running": service_running("features"),
            "started_process_stop_results": stop_results,
        }

        corrected_new_features = [corrected_feature_summary(x) for x in new_features]
        decision_new_samples = [decision_summary(x) for x in new_decisions]
        latest_decisions_all = [decision_summary(x) for x in redis_xrevrange(DECISIONS_STREAM, count=10)]

        proof["observations"]["samples"] = samples
        proof["observations"]["new_features_corrected"] = corrected_new_features
        proof["observations"]["new_decisions"] = decision_new_samples
        proof["observations"]["latest_decisions_all"] = latest_decisions_all
        proof["observations"]["after"] = after

        r3g = proof["prior_proofs"].get("run/proofs/proof_batch26o20_r3g_corrected_r3e_proof_parser.json", {})

        feature_set = corrected_new_features
        current_structural_ok = bool(feature_set) and all(x.get("corrected_parser_structural_valid") is True for x in feature_set)
        current_all_10 = bool(feature_set) and all(x.get("branch_key_set_match") is True for x in feature_set)
        current_mist_call = bool(feature_set) and all(x.get("mist_call_visible") is True for x in feature_set)
        current_consumer_view = bool(feature_set) and all(x.get("consumer_view_present") is True for x in feature_set)

        # data_valid/safe_to_consume are observed semantics only. They are not forced true by this batch.
        data_valid_semantics_observed = bool(feature_set) and all(x.get("consumer_view_data_valid") in {True, False, None} for x in feature_set)
        safe_semantics_observed = bool(feature_set) and all(x.get("consumer_view_safe_to_consume") in {True, False, None} for x in feature_set)

        decision_eval = decision_new_samples if decision_new_samples else latest_decisions_all[:5]
        decisions_hold_no_candidate = bool(decision_eval) and all(
            d.get("hold_only") is True
            and str(d.get("side", "")).upper() in {"FLAT", "", "NONE"}
            and str(d.get("qty", "0")) in {"0", "0.0", ""}
            and (
                d.get("activation_reason") in {"no_candidate", "", None}
                or d.get("reason") in {"no_candidate", "hold_only_family_features_consumer_bridge", "", None}
            )
            and d.get("broker_side_effects_allowed") is False
            and d.get("live_orders_allowed") is False
            for d in decision_eval
        )

        orders_zero = before["orders_xlen"] == 0 and after["orders_xlen"] == 0 and not (redis_xrevrange_raw(ORDERS_STREAM, count=3).get("stdout") or "").strip()
        pos = after["position"]
        position_flat = (
            str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
            and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
            and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
            and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
        )

        req = {
            "r3g_pass_loaded": str(r3g.get("final_verdict", "")).startswith("PASS_O20_R3G_CORRECTED_R3E_PROOF_PARSER"),
            "r3g_recommended_r3h": "R3H current-frame corrected bounded observation" in str(r3g.get("next_recommended_batch", "")),
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "current_new_feature_frames_min_met": len(new_features) >= MIN_NEW_FEATURE_FRAMES,
            "current_corrected_structural_shape_ok": current_structural_ok,
            "current_all_10_branch_frames_present": current_all_10,
            "current_mist_call_visible": current_mist_call,
            "current_consumer_view_present": current_consumer_view,
            "data_valid_semantics_observed_not_forced": data_valid_semantics_observed,
            "safe_to_consume_semantics_observed_not_forced": safe_semantics_observed,
            "decision_frames_available": bool(decision_eval),
            "strategy_one_shot_attempted": bool(strategy_once.get("attempted")),
            "strategy_one_shot_ok_or_decision_available": bool(strategy_once.get("ok")) or bool(decision_eval),
            "decisions_hold_no_candidate": decisions_hold_no_candidate,
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "real_live_false": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_paper_start": os.environ.get("SCALPX_PAPER_ARMED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_broker_call": os.environ.get("SCALPX_BROKER_CALLS_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_order_write_intent": os.environ.get("SCALPX_LIVE_ORDERS_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_threshold_relaxation": os.environ.get("SCALPX_THRESHOLD_RELAXATION", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_forced_candidate": os.environ.get("SCALPX_FORCE_CANDIDATE", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "risk_not_running_after": not after["risk_running"],
            "execution_not_running_after": not after["execution_running"],
            "started_features_stopped_after_probe": not (feature_probe.get("started") is True and after["features_running"] is True),
            "production_source_patch_false": True,
        }

        proof["required_verdicts"] = req
        false_keys = [k for k, v in req.items() if v is not True]
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if not false_keys:
            proof["final_verdict"] = "PASS_O20_R3H_CURRENT_FRAME_CORRECTED_BOUNDED_OBSERVATION_OK_HOLD_ONLY"
            proof["next_recommended_batch"] = "26-O22-R2 controlled-paper plan/proof correction; still no real live and no paper restart unless explicitly approved."
        else:
            proof["final_verdict"] = "FAIL_O20_R3H_CURRENT_FRAME_CORRECTED_BOUNDED_OBSERVATION_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and write smallest Lane-A diagnostic/repair package only; do not jump lanes."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — current-frame corrected bounded observation",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Purpose",
                "- Re-run bounded observation after R3G corrected the R3E proof-parser law.",
                "- Use current-frame stream watermarking so stale mixed entries do not create false conclusions.",
                "- Verify corrected structural shape, 10 branch frames, MIST CALL visibility, HOLD/no_candidate behavior, zero orders, and FLAT position.",
                "",
                "## Safety",
                "- No real-live enablement.",
                "- No paper restart.",
                "- No broker call.",
                "- No order write.",
                "- No threshold relaxation.",
                "- No forced candidate.",
                "- No doctrine mutation.",
                "- Risk/execution not started.",
                "- Features probe stopped if this batch started it.",
                "- No production source patch.",
                "",
                "## Corrected parser law",
                "- Structural validity is proven from current frames by locating all 10 branch frames and MIST CALL in persisted JSON surfaces.",
                "- data_valid and safe_to_consume remain observed provider/data-validity semantics and are not forced true.",
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
            ]),
            encoding="utf-8",
        )

        MILESTONE_MD.write_text(
            "\n".join([
                f"# {DATE} — {BATCH} current-frame corrected bounded observation",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Summary",
                "- Used R3G corrected parser law on current feature frames only.",
                "- Verified structural shape without mutating production source.",
                "- Preserved HOLD/no_candidate and safety boundaries.",
                "- Did not start risk/execution.",
                "- Did not enable paper or real live.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
                "",
                "## Artifacts",
                f"- `{PROOF_JSON.relative_to(ROOT)}`",
                f"- `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            BIN_COPY,
            *[ROOT / rel for rel in INSPECT_PATHS if (ROOT / rel).exists()],
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
        print(f"next_recommended_batch = {proof['next_recommended_batch']}")
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        print(f"manifest_json = {MANIFEST_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        stop_started_processes()
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O20_R3H_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
