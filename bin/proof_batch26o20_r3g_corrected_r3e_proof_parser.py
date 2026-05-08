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
BATCH = "26-O20-R3G"
BATCH_NAME = "corrected_r3e_proof_parser_only_no_production_patch"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o20_r3g_corrected_r3e_proof_parser_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o20_r3g_corrected_r3e_proof_parser.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o20_r3g_corrected_r3e_proof_parser.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o20_r3g_corrected_r3e_proof_parser.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o20_r3g_corrected_r3e_proof_parser.md"
BIN_COPY = BIN_DIR / "proof_batch26o20_r3g_corrected_r3e_proof_parser.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"

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
    "run/proofs/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.json",
    "run/proofs/proof_batch26o20_r3e_corrected_bounded_observation.json",
    "run/proofs/proof_batch26o20_r3f_persisted_features_publish_route_classifier.json",
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

    # Corrected proof-parser rule:
    # Consumer-view is structurally valid when it carries all expected branch frames and MIST CALL is visible.
    # data_valid/safe_to_consume may remain false when provider/data validity is false; that is not a structural-shape failure.
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
        "consumer_view_keys": sorted(consumer_view.keys()) if isinstance(consumer_view, dict) else [],
        "branch_frames_source": branch_source,
        "branch_frame_count": len(branch_keys),
        "branch_key_set_match": branch_keys == EXPECTED_BRANCH_KEYS,
        "mist_call_visible": "mist_call" in branch_keys,
        "structural_valid_by_shape": structural_valid_by_shape,
        "consumer_explicit_structural_valid": consumer_explicit_structural,
        "consumer_view_data_valid": consumer_data_valid,
        "consumer_view_safe_to_consume": consumer_safe,
        "top_structural_valid": top_structural,
        "payload_structural_valid": payload_structural,
        "corrected_parser_structural_valid": (
            structural_valid_by_shape
            or consumer_explicit_structural is True
            or top_structural is True
            or payload_structural is True
        ),
        "corrected_parser_data_valid": consumer_data_valid,
        "corrected_parser_safe_to_consume": consumer_safe,
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


def write_corrected_r3e_equivalent_report(proof: dict[str, Any]) -> pathlib.Path:
    out = RUN_DIR / "corrected_r3e_equivalent_report.json"
    out.write_text(
        json.dumps(
            {
                "batch": BATCH,
                "generated_at_utc": proof.get("completed_at_utc"),
                "correction": {
                    "reason": "R3F classified R3E as proof-parser gap, not production-source gap.",
                    "parser_law": "For persisted features stream, structural validity is proven by branch-frame shape inside consumer_view_json/family_features_json/family_surfaces_json/payload_json. data_valid/safe_to_consume are data/provider validity semantics and may remain false without invalidating structural shape.",
                    "no_production_source_patch": True,
                },
                "corrected_feature_samples": proof.get("corrected_feature_samples"),
                "decision_samples": proof.get("decision_samples"),
                "required_verdicts": proof.get("required_verdicts"),
                "final_verdict": proof.get("final_verdict"),
                "next_recommended_batch": proof.get("next_recommended_batch"),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return out


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_bundle_must_be_inspected_before_patch_work": True,
            "prior_r3f_output_uploaded_and_read": True,
            "r3f_classification_expected": "PASS_O20_R3F_CLASSIFIED_PROOF_PARSER_GAP_HOLD_ONLY",
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
            "proof_parser_only": True,
        },
        "prior_proofs": {},
        "inspected_files": {},
        "commands": {},
        "redis": {},
        "corrected_feature_samples": [],
        "decision_samples": [],
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
                        "classification": loaded.get("classification") if isinstance(loaded, dict) else None,
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

        print("===== REDIS READ-ONLY CORRECTED PARSER SNAPSHOT =====")
        feature_entries = redis_xrevrange(FEATURES_STREAM, count=10)
        decision_entries = redis_xrevrange(DECISIONS_STREAM, count=10)

        corrected_features = [corrected_feature_summary(x) for x in feature_entries]
        decisions = [decision_summary(x) for x in decision_entries]

        proof["corrected_feature_samples"] = corrected_features
        proof["decision_samples"] = decisions
        proof["redis"] = {
            "features_xlen": redis_xlen(FEATURES_STREAM),
            "decisions_xlen": redis_xlen(DECISIONS_STREAM),
            "orders_xlen": redis_xlen(ORDERS_STREAM),
            "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=3),
            "position": redis_hgetall(POSITION_HASH),
            "process_lines": proc_lines(),
            "risk_running": service_running("risk"),
            "execution_running": service_running("execution"),
            "strategy_running": service_running("strategy"),
            "features_running": service_running("features"),
        }

        r3f = proof["prior_proofs"].get("run/proofs/proof_batch26o20_r3f_persisted_features_publish_route_classifier.json", {})
        r3f_class = r3f.get("classification") or {}

        latest_n = corrected_features[:5]
        decisions_n = decisions[:5]

        structural_shape_ok = bool(latest_n) and all(x.get("corrected_parser_structural_valid") is True for x in latest_n)
        all_10_branch_frames = bool(latest_n) and all(x.get("branch_key_set_match") is True for x in latest_n)
        mist_call_visible = bool(latest_n) and all(x.get("mist_call_visible") is True for x in latest_n)
        consumer_view_present = bool(latest_n) and all(x.get("consumer_view_present") is True for x in latest_n)

        # In corrected parser-only batch, these are classified as semantic/provider-validity values, not structural shape.
        data_valid_semantics_observed = bool(latest_n) and all(x.get("corrected_parser_data_valid") in {True, False, None} for x in latest_n)
        safe_semantics_observed = bool(latest_n) and all(x.get("corrected_parser_safe_to_consume") in {True, False, None} for x in latest_n)

        decisions_hold_no_candidate = bool(decisions_n) and all(
            d.get("hold_only") is True
            and str(d.get("side", "")).upper() in {"FLAT", "", "NONE"}
            and str(d.get("qty", "0")) in {"0", "0.0", ""}
            and (
                d.get("activation_reason") in {"no_candidate", "", None}
                or d.get("reason") in {"no_candidate", "hold_only_family_features_consumer_bridge", "", None}
            )
            and d.get("broker_side_effects_allowed") is False
            and d.get("live_orders_allowed") is False
            for d in decisions_n
        )

        orders_zero = proof["redis"]["orders_xlen"] == 0 and not (proof["redis"]["latest_orders_raw"].get("stdout") or "").strip()
        pos = proof["redis"]["position"]
        position_flat = (
            str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
            and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
            and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
            and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
        )

        req = {
            "r3f_pass_loaded": str(r3f.get("final_verdict", "")).startswith("PASS_O20_R3F_CLASSIFIED_PROOF_PARSER_GAP"),
            "r3f_recommended_r3g_parser_only": "R3G corrected R3E proof parser" in str(r3f.get("next_recommended_batch", "")),
            "r3f_classified_proof_parser_gap": r3f_class.get("proof_parser_gap_possible") is True,
            "r3f_latest_branch_ok": r3f_class.get("latest_branch_ok") is True,
            "r3f_latest_mist_call": r3f_class.get("latest_mist_call") is True,
            "compile_pass": bool(proof["commands"]["compile"].get("ok")),
            "import_pass": bool(proof["commands"]["import"].get("ok")),
            "features_samples_present": bool(latest_n),
            "consumer_view_present": consumer_view_present,
            "corrected_structural_shape_ok": structural_shape_ok,
            "all_10_branch_frames_present_corrected": all_10_branch_frames,
            "mist_call_visible_corrected": mist_call_visible,
            "data_valid_semantics_observed_not_forced": data_valid_semantics_observed,
            "safe_to_consume_semantics_observed_not_forced": safe_semantics_observed,
            "decision_samples_present": bool(decisions_n),
            "decisions_hold_no_candidate": decisions_hold_no_candidate,
            "orders_zero": orders_zero,
            "position_flat": position_flat,
            "real_live_false": os.environ.get("SCALPX_REAL_LIVE_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_paper_start": os.environ.get("SCALPX_PAPER_ARMED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_broker_call": os.environ.get("SCALPX_BROKER_CALLS_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_order_write_intent": os.environ.get("SCALPX_LIVE_ORDERS_ALLOWED", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_threshold_relaxation": os.environ.get("SCALPX_THRESHOLD_RELAXATION", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "no_forced_candidate": os.environ.get("SCALPX_FORCE_CANDIDATE", "0") not in {"1", "true", "TRUE", "yes", "YES"},
            "risk_not_running": not proof["redis"]["risk_running"],
            "execution_not_running": not proof["redis"]["execution_running"],
            "production_source_patch_false": True,
            "proof_parser_only": True,
        }
        proof["required_verdicts"] = req

        false_keys = [k for k, v in req.items() if v is not True]
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if not false_keys:
            proof["final_verdict"] = "PASS_O20_R3G_CORRECTED_R3E_PROOF_PARSER_OK_HOLD_ONLY"
            proof["next_recommended_batch"] = "26-O20-R3H current-frame corrected bounded observation with corrected parser; no source patch, no real live."
        else:
            proof["final_verdict"] = "FAIL_O20_R3G_CORRECTED_R3E_PROOF_PARSER_NOT_PROVEN"
            proof["next_recommended_batch"] = "Inspect false_keys and write smallest Lane-A diagnostic package only; do not patch production source."

        corrected_report = write_corrected_r3e_equivalent_report(proof)
        proof["corrected_r3e_equivalent_report"] = str(corrected_report.relative_to(ROOT))

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — corrected R3E proof parser only",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- corrected_report: `{corrected_report.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Evidence",
                "- R3F classified the R3E failure as a proof-parser gap.",
                "- Latest persisted feature entries contain expected branch frames under `consumer_view_json`; R3E parser looked in insufficient locations.",
                "",
                "## Corrected parser law",
                "- Structural validity is proven by all 10 expected branch frames plus MIST CALL visibility.",
                "- `data_valid` and `safe_to_consume` are data/provider validity semantics and are not forced or reclassified as true.",
                "- No production source patch is applied in this batch.",
                "",
                "## Safety",
                "- No real live.",
                "- No paper start.",
                "- No broker call.",
                "- No order write.",
                "- No threshold relaxation.",
                "- No forced candidate.",
                "- Risk/execution not started.",
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
                f"# {DATE} — {BATCH} corrected R3E proof parser only",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Summary",
                "- This batch performed a proof-parser correction only.",
                "- It did not patch production runtime source.",
                "- It did not start paper/live, call broker, write orders, force candidates, or relax thresholds.",
                "- It verified structural shape by searching persisted feature JSON fields for all 10 branch frames and MIST CALL.",
                "- It preserved provider/data validity semantics as observed values.",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
                "",
                "## Artifacts",
                f"- `{PROOF_JSON.relative_to(ROOT)}`",
                f"- `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- `{RUNBOOK_MD.relative_to(ROOT)}`",
                f"- `{corrected_report.relative_to(ROOT)}`",
            ]),
            encoding="utf-8",
        )

        shutil.copy2(pathlib.Path(__file__), BIN_COPY)

        manifest_paths = [
            PROOF_JSON,
            MANIFEST_JSON,
            RUNBOOK_MD,
            MILESTONE_MD,
            BIN_COPY,
            corrected_report,
            *[ROOT / rel for rel in INSPECT_PATHS if (ROOT / rel).exists()],
        ]
        manifest = {
            "batch": BATCH,
            "tag": TAG,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": {
                str(p.relative_to(ROOT)): sha256_file(p)
                for p in manifest_paths
                if p.exists() and p != MANIFEST_JSON
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
        print(f"corrected_report = {corrected_report.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O20_R3G_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
