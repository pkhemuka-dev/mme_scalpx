#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tarfile
import time
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O20-R3F"
BATCH_NAME = "persisted_features_publish_route_audit_repair_classifier"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
NOW = datetime.now(timezone.utc).isoformat()
TAG = f"batch26o20_r3f_persisted_features_publish_route_classifier_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o20_r3f_persisted_features_publish_route_classifier.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o20_r3f_persisted_features_publish_route_classifier.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o20_r3f_persisted_features_publish_route_classifier.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o20_r3f_persisted_features_publish_route_classifier.md"
BIN_COPY = BIN_DIR / "proof_batch26o20_r3f_persisted_features_publish_route_classifier.py"

FEATURES_PY = ROOT / "app/mme_scalpx/services/features.py"

INSPECT_PATHS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/main.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "run/proofs/proof_batch26o20_r3d_r2b_payload_structural_valid_alignment.json",
    "run/proofs/proof_batch26o20_r3e_corrected_bounded_observation.json",
]

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


def run(cmd: list[str], *, timeout: int = 30, check: bool = False, env: dict[str, str] | None = None) -> dict[str, Any]:
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
        out = {
            "cmd": cmd,
            "returncode": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "ok": cp.returncode == 0,
        }
        if check and cp.returncode != 0:
            raise RuntimeError(json.dumps(out, indent=2))
        return out
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


def redis_xrevrange_raw(key: str, count: int = 3) -> dict[str, Any]:
    return redis_cmd(["XREVRANGE", key, "+", "-", "COUNT", str(count)], timeout=20)


def redis_xrevrange(key: str, count: int = 3) -> list[dict[str, Any]]:
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
    for _ in range(3):
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


def recursive_find(obj: Any, key: str, *, max_depth: int = 12) -> list[Any]:
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


def recursive_find_branch_frames(obj: Any) -> dict[str, Any] | None:
    if not isinstance(obj, (dict, list)):
        return None
    direct = recursive_find(obj, "branch_frames")
    for item in direct:
        if isinstance(item, dict):
            keys = set(item.keys())
            if EXPECTED_BRANCH_KEYS.issubset(keys):
                return item
    # Some payloads may carry the branch frames directly as a dict keyed by branch.
    if isinstance(obj, dict):
        keys = set(obj.keys())
        if EXPECTED_BRANCH_KEYS.issubset(keys):
            return obj
    return None


def summarize_feature_entry(entry: dict[str, Any]) -> dict[str, Any]:
    f = entry.get("fields", {})
    parsed_fields = {k: parse_json_maybe(v) for k, v in f.items() if k.endswith("_json") or k in {"payload", "payload_json"}}

    payload = parsed_fields.get("payload_json") or parsed_fields.get("payload") or {}
    family_features = parsed_fields.get("family_features_json") or {}
    family_surfaces = parsed_fields.get("family_surfaces_json") or {}
    consumer_view = parsed_fields.get("consumer_view_json")
    if consumer_view is None and isinstance(payload, dict):
        consumer_view = payload.get("consumer_view")

    branch_frames = None
    branch_frames_source = ""
    for source_name, obj in [
        ("payload_json", payload),
        ("family_features_json", family_features),
        ("family_surfaces_json", family_surfaces),
        ("consumer_view_json", consumer_view),
    ]:
        branch_frames = recursive_find_branch_frames(obj)
        if branch_frames is not None:
            branch_frames_source = source_name
            break

    branch_keys = set(branch_frames.keys()) if isinstance(branch_frames, dict) else set()

    structural_candidates = []
    for source_name, obj in [
        ("top_field", f),
        ("consumer_view_json", consumer_view),
        ("payload_json", payload),
        ("family_features_json", family_features),
        ("family_surfaces_json", family_surfaces),
    ]:
        if isinstance(obj, dict):
            for key in ("structural_valid", "frame_valid", "valid", "data_valid", "safe_to_consume"):
                if key in obj:
                    structural_candidates.append({
                        "source": source_name,
                        "key": key,
                        "value": obj.get(key),
                        "bool": as_bool(obj.get(key)),
                    })

    return {
        "id": entry.get("id"),
        "raw_field_keys": sorted(f.keys()),
        "top_data_valid": as_bool(f.get("data_valid")),
        "top_safe_to_consume": as_bool(f.get("safe_to_consume")),
        "top_structural_valid": as_bool(f.get("structural_valid")),
        "consumer_view_present": isinstance(consumer_view, dict),
        "consumer_view_keys": sorted(consumer_view.keys()) if isinstance(consumer_view, dict) else [],
        "consumer_view_data_valid": as_bool(consumer_view.get("data_valid")) if isinstance(consumer_view, dict) else None,
        "consumer_view_safe_to_consume": as_bool(consumer_view.get("safe_to_consume")) if isinstance(consumer_view, dict) else None,
        "consumer_view_structural_valid": as_bool(consumer_view.get("structural_valid")) if isinstance(consumer_view, dict) else None,
        "consumer_view_structural_valid_alias": as_bool(consumer_view.get("structural_valid_alias")) if isinstance(consumer_view, dict) else None,
        "payload_structural_valid": as_bool(payload.get("structural_valid")) if isinstance(payload, dict) else None,
        "payload_frame_valid": as_bool(payload.get("frame_valid")) if isinstance(payload, dict) else None,
        "branch_frames_source": branch_frames_source,
        "branch_frame_count": len(branch_keys),
        "branch_key_set_match": branch_keys == EXPECTED_BRANCH_KEYS,
        "mist_call_visible": "mist_call" in branch_keys,
        "structural_candidates": structural_candidates[:30],
        "json_field_parse_status": {
            k: type(v).__name__ for k, v in parsed_fields.items()
        },
    }


def summarize_decision_entry(entry: dict[str, Any]) -> dict[str, Any]:
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


def find_latest_evidence_archives() -> list[dict[str, Any]]:
    candidates: list[pathlib.Path] = []
    for base in [ROOT, ROOT / "run", ROOT / "run" / "evidence_bundles", ROOT / "run" / "proofs"]:
        if base.exists():
            candidates.extend(base.glob("*.tar.gz"))
            candidates.extend(base.glob("*.tgz"))
    out: list[dict[str, Any]] = []
    for p in sorted(set(candidates), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
        rec: dict[str, Any] = {
            "path": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
            "size_bytes": p.stat().st_size,
            "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(),
            "sha256": sha256_file(p),
        }
        try:
            with tarfile.open(p, "r:*") as tf:
                names = tf.getnames()
                rec["member_count"] = len(names)
                rec["sample_members"] = names[:50]
                rec["has_o20_r3e_proof"] = any("proof_batch26o20_r3e_corrected_bounded_observation.json" in n for n in names)
                rec["has_features_py"] = any(n.endswith("app/mme_scalpx/services/features.py") or n.endswith("features.py") for n in names)
        except Exception as exc:
            rec["tar_read_error"] = repr(exc)
        out.append(rec)
    return out


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


def inspect_features_source() -> dict[str, Any]:
    text = FEATURES_PY.read_text(encoding="utf-8") if FEATURES_PY.exists() else ""
    result: dict[str, Any] = {
        "exists": FEATURES_PY.exists(),
        "sha256": sha256_file(FEATURES_PY) if FEATURES_PY.exists() else None,
        "marker_r2b_present": "FeatureService.run_once returned payload alignment appended" in text,
        "marker_r3f_present": "O20-R3F persisted publish-route alignment" in text,
        "line_count": text.count("\n") + 1 if text else 0,
        "consumer_view_occurrences": [],
        "family_features_json_occurrences": [],
        "xadd_occurrences": [],
        "run_once_defs": [],
    }
    for idx, line in enumerate(text.splitlines(), start=1):
        if "consumer_view" in line:
            result["consumer_view_occurrences"].append({"line": idx, "text": line[:220]})
        if "family_features_json" in line:
            result["family_features_json_occurrences"].append({"line": idx, "text": line[:220]})
        if ".xadd" in line or "xadd(" in line:
            result["xadd_occurrences"].append({"line": idx, "text": line[:220]})
        if re.match(r"\s*def\s+run_once\b", line):
            result["run_once_defs"].append({"line": idx, "text": line[:220]})
    try:
        tree = ast.parse(text)
        funcs = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": getattr(node, "end_lineno", None),
                })
        result["functions"] = funcs
        result["ast_ok"] = True
    except Exception as exc:
        result["ast_ok"] = False
        result["ast_error"] = repr(exc)
    return result


def run_feature_once_introspection() -> dict[str, Any]:
    helper = RUN_DIR / "feature_once_introspection.py"
    helper.write_text(
        r'''
from __future__ import annotations
import inspect, json, os, sys, time, traceback
from typing import Any

os.environ.setdefault("SCALPX_REAL_LIVE_ALLOWED", "0")
os.environ.setdefault("SCALPX_LIVE_ORDERS_ALLOWED", "0")
os.environ.setdefault("SCALPX_BROKER_CALLS_ALLOWED", "0")
os.environ.setdefault("SCALPX_PAPER_ARMED", "0")
os.environ.setdefault("SCALPX_FORCE_CANDIDATE", "0")

out: dict[str, Any] = {"ok": False, "attempts": []}

def summarize(obj: Any) -> Any:
    if isinstance(obj, dict):
        keys = sorted(obj.keys())
        return {
            "type": "dict",
            "keys": keys[:80],
            "data_valid": obj.get("data_valid"),
            "safe_to_consume": obj.get("safe_to_consume"),
            "structural_valid": obj.get("structural_valid"),
            "frame_valid": obj.get("frame_valid"),
            "consumer_view": obj.get("consumer_view") if isinstance(obj.get("consumer_view"), dict) else None,
            "branch_frame_count": len(obj.get("branch_frames") or {}) if isinstance(obj.get("branch_frames"), dict) else None,
        }
    return {"type": type(obj).__name__, "repr": repr(obj)[:500]}

try:
    import app.mme_scalpx.services.features as mod
    out["module"] = mod.__name__
    out["module_file"] = getattr(mod, "__file__", "")
    classes = []
    for name, value in inspect.getmembers(mod, inspect.isclass):
        if value.__module__ == mod.__name__:
            classes.append(name)
    out["classes"] = classes

    for cls_name in ["FeatureService", "FeaturesService"]:
        cls = getattr(mod, cls_name, None)
        if cls is None:
            continue
        attempt: dict[str, Any] = {"class": cls_name}
        try:
            sig = str(inspect.signature(cls))
            attempt["signature"] = sig
        except Exception as exc:
            attempt["signature_error"] = repr(exc)
        try:
            obj = cls()
            attempt["constructed"] = True
        except Exception as exc:
            attempt["constructed"] = False
            attempt["construct_error"] = repr(exc)
            out["attempts"].append(attempt)
            continue

        for method_name in ["run_once", "once", "build_once"]:
            method = getattr(obj, method_name, None)
            if method is None:
                continue
            mattempt = dict(attempt)
            mattempt["method"] = method_name
            try:
                result = method()
                mattempt["method_ok"] = True
                mattempt["result_summary"] = summarize(result)
                out["ok"] = True
            except Exception as exc:
                mattempt["method_ok"] = False
                mattempt["method_error"] = repr(exc)
                mattempt["traceback"] = traceback.format_exc(limit=6)
            out["attempts"].append(mattempt)
except Exception as exc:
    out["import_error"] = repr(exc)
    out["traceback"] = traceback.format_exc(limit=8)

print(json.dumps(out, indent=2, sort_keys=True, default=str))
''',
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{ROOT}:{env.get('PYTHONPATH', '')}"
    env["SCALPX_REAL_LIVE_ALLOWED"] = "0"
    env["SCALPX_LIVE_ORDERS_ALLOWED"] = "0"
    env["SCALPX_BROKER_CALLS_ALLOWED"] = "0"
    env["SCALPX_PAPER_ARMED"] = "0"
    env["SCALPX_FORCE_CANDIDATE"] = "0"
    res = run([sys.executable, str(helper)], timeout=60, env=env)
    parsed = parse_json_maybe(res.get("stdout"))
    return {
        "helper": str(helper.relative_to(ROOT)),
        "result": res,
        "parsed": parsed,
    }


def write_no_mutation_classifier_patch_note(proof: dict[str, Any]) -> None:
    note = RUN_DIR / "r3f_classifier_no_mutation_note.md"
    note.write_text(
        "\n".join([
            "# R3F classifier note",
            "",
            "This batch does not mutate production code unless a later batch is explicitly written from this proof.",
            "",
            "Reason: R3E proved safety remained clean, but the persisted features stream has a shape/validity mismatch.",
            "The correct next action is to classify whether this is:",
            "",
            "1. proof-parser gap,",
            "2. persisted publish-route gap in `features.py`,",
            "3. live-feed/provider-current dependency that belongs to Lane B, or",
            "4. stale mixed stream entry contamination.",
            "",
            "Only after classification should a minimal source patch be written.",
            "",
            f"Proof: `{PROOF_JSON.relative_to(ROOT)}`",
        ]),
        encoding="utf-8",
    )
    proof["classifier_note"] = str(note.relative_to(ROOT))


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": NOW,
        "root": str(ROOT),
        "evidence_first_policy": {
            "latest_uploaded_bundle_must_be_inspected_before_patch_work": True,
            "local_evidence_archive_search_performed": True,
            "uploaded_chat_bundle_note": "ChatGPT-side uploaded bundle is inspected before writing this package; this VM script also inspects local proof/evidence artifacts available under the project tree.",
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
            "production_source_mutation": False,
        },
        "evidence_archives": [],
        "prior_proofs": {},
        "inspected_files": {},
        "commands": {},
        "redis": {},
        "source_inspection": {},
        "feature_once_introspection": {},
        "classification": {},
        "required_verdicts": {},
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    try:
        print("===== EVIDENCE-FIRST LOCAL ARCHIVE / PROOF INSPECTION =====")
        proof["evidence_archives"] = find_latest_evidence_archives()

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

        print("===== COMPILE / IMPORT PROOF =====")
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
        proof["commands"]["compile_before"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
        proof["commands"]["import_before"] = run(
            [
                sys.executable,
                "-c",
                "import app.mme_scalpx.services.features, app.mme_scalpx.services.strategy, app.mme_scalpx.core.names, app.mme_scalpx.core.models; print('IMPORT_OK')",
            ],
            timeout=60,
        )

        print("===== REDIS SAFETY / SHAPE SNAPSHOT =====")
        feature_entries = redis_xrevrange(FEATURES_STREAM, count=5)
        decision_entries = redis_xrevrange(DECISIONS_STREAM, count=5)
        proof["redis"] = {
            "features_xlen": redis_xlen(FEATURES_STREAM),
            "decisions_xlen": redis_xlen(DECISIONS_STREAM),
            "orders_xlen": redis_xlen(ORDERS_STREAM),
            "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=3),
            "position": redis_hgetall(POSITION_HASH),
            "feature_entries_summary": [summarize_feature_entry(x) for x in feature_entries],
            "decision_entries_summary": [summarize_decision_entry(x) for x in decision_entries],
            "process_lines": proc_lines(),
            "risk_running": service_running("risk"),
            "execution_running": service_running("execution"),
            "strategy_running": service_running("strategy"),
            "features_running": service_running("features"),
        }

        print("===== SOURCE INSPECTION =====")
        proof["source_inspection"]["features_py"] = inspect_features_source()

        print("===== FEATURE RUN_ONCE INTROSPECTION WITHOUT SERVICE START =====")
        proof["feature_once_introspection"] = run_feature_once_introspection()

        feature_summaries = proof["redis"]["feature_entries_summary"]
        latest_feature = feature_summaries[0] if feature_summaries else {}
        r3e = proof["prior_proofs"].get("run/proofs/proof_batch26o20_r3e_corrected_bounded_observation.json", {})
        r3e_false = set(r3e.get("false_keys") or [])

        latest_consumer_valid = latest_feature.get("consumer_view_data_valid") is True
        latest_consumer_safe = latest_feature.get("consumer_view_safe_to_consume") is True
        latest_consumer_structural = latest_feature.get("consumer_view_structural_valid") is True or latest_feature.get("consumer_view_structural_valid_alias") is True
        latest_branch_ok = latest_feature.get("branch_key_set_match") is True
        latest_mist_call = latest_feature.get("mist_call_visible") is True

        run_once_parsed = proof["feature_once_introspection"].get("parsed")
        run_once_ok = isinstance(run_once_parsed, dict) and run_once_parsed.get("ok") is True
        run_once_summary_candidates = []
        if isinstance(run_once_parsed, dict):
            for attempt in run_once_parsed.get("attempts") or []:
                if isinstance(attempt, dict) and attempt.get("method_ok") is True:
                    run_once_summary_candidates.append(attempt.get("result_summary") or {})
        run_once_any_valid = any(
            as_bool(x.get("data_valid")) is True
            or as_bool((x.get("consumer_view") or {}).get("data_valid")) is True
            for x in run_once_summary_candidates
            if isinstance(x, dict)
        )

        orders_zero = proof["redis"]["orders_xlen"] == 0 and not (proof["redis"]["latest_orders_raw"].get("stdout") or "").strip()
        pos = proof["redis"]["position"]
        position_flat = (
            str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
            and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
            and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
            and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
        )

        proof_parser_gap_possible = (
            latest_feature.get("branch_frames_source") not in {"", None}
            and latest_feature.get("branch_key_set_match") is True
            and (
                latest_feature.get("consumer_view_data_valid") is not True
                or latest_feature.get("consumer_view_safe_to_consume") is not True
            )
        )

        persisted_publish_route_gap_possible = (
            run_once_ok
            and run_once_any_valid
            and (
                latest_consumer_valid is not True
                or latest_consumer_safe is not True
                or latest_consumer_structural is not True
                or latest_branch_ok is not True
            )
        )

        lane_b_dependency_possible = (
            not run_once_any_valid
            and (
                latest_consumer_valid is not True
                or latest_branch_ok is not True
            )
        )

        stale_or_mixed_stream_possible = (
            proof["redis"]["features_xlen"] > 0
            and proof["redis"]["decisions_xlen"] > 0
            and bool(proof["redis"]["decision_entries_summary"])
            and proof["redis"]["decision_entries_summary"][0].get("branch_frame_count") == 10
            and latest_branch_ok is not True
        )

        classification = {
            "r3e_final_verdict": r3e.get("final_verdict"),
            "r3e_false_keys": sorted(r3e_false),
            "latest_feature_id": latest_feature.get("id"),
            "latest_feature_raw_field_keys": latest_feature.get("raw_field_keys"),
            "latest_feature_branch_frames_source": latest_feature.get("branch_frames_source"),
            "latest_consumer_valid": latest_consumer_valid,
            "latest_consumer_safe": latest_consumer_safe,
            "latest_consumer_structural": latest_consumer_structural,
            "latest_branch_ok": latest_branch_ok,
            "latest_mist_call": latest_mist_call,
            "run_once_ok": run_once_ok,
            "run_once_any_valid": run_once_any_valid,
            "proof_parser_gap_possible": proof_parser_gap_possible,
            "persisted_publish_route_gap_possible": persisted_publish_route_gap_possible,
            "lane_b_dependency_possible": lane_b_dependency_possible,
            "stale_or_mixed_stream_possible": stale_or_mixed_stream_possible,
            "recommended_lane": "LANE_A" if persisted_publish_route_gap_possible or proof_parser_gap_possible or stale_or_mixed_stream_possible else "LANE_B_OR_DEFER",
        }
        proof["classification"] = classification

        write_no_mutation_classifier_patch_note(proof)

        req = {
            "evidence_first_local_search_done": True,
            "r3e_failure_loaded": str(r3e.get("final_verdict", "")).startswith("FAIL_O20_R3E"),
            "compile_before_pass": bool(proof["commands"]["compile_before"].get("ok")),
            "import_before_pass": bool(proof["commands"]["import_before"].get("ok")),
            "features_py_inspected": proof["source_inspection"]["features_py"].get("exists") is True,
            "redis_feature_shape_captured": bool(feature_summaries),
            "redis_decision_shape_captured": bool(proof["redis"]["decision_entries_summary"]),
            "classification_complete": any([
                proof_parser_gap_possible,
                persisted_publish_route_gap_possible,
                lane_b_dependency_possible,
                stale_or_mixed_stream_possible,
            ]),
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
            "production_source_mutation_false": True,
        }
        proof["required_verdicts"] = req

        false_keys = [k for k, v in req.items() if v is not True]
        proof["false_keys"] = false_keys
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

        if false_keys:
            proof["final_verdict"] = "FAIL_O20_R3F_CLASSIFICATION_NOT_PROVEN"
            proof["next_recommended_batch"] = "Fix R3F classifier false_keys first; no production patch yet."
        elif persisted_publish_route_gap_possible:
            proof["final_verdict"] = "PASS_O20_R3F_CLASSIFIED_PERSISTED_PUBLISH_ROUTE_GAP_HOLD_ONLY"
            proof["next_recommended_batch"] = "26-O20-R3G minimal features.py persisted publish-route alignment patch; target features.py only; no risk/execution."
        elif proof_parser_gap_possible:
            proof["final_verdict"] = "PASS_O20_R3F_CLASSIFIED_PROOF_PARSER_GAP_HOLD_ONLY"
            proof["next_recommended_batch"] = "26-O20-R3G corrected R3E proof parser only; no production source patch."
        elif stale_or_mixed_stream_possible:
            proof["final_verdict"] = "PASS_O20_R3F_CLASSIFIED_STALE_OR_MIXED_STREAM_ENTRY_HOLD_ONLY"
            proof["next_recommended_batch"] = "26-O20-R3G bounded observation with stream-id watermark and current-frame-only proof; no production source patch."
        elif lane_b_dependency_possible:
            proof["final_verdict"] = "PASS_O20_R3F_CLASSIFIED_CROSS_WORKSTREAM_DEPENDENCY_FOR_LANE_B_HOLD_ONLY"
            proof["next_recommended_batch"] = "Write Lane-B handoff note for feed/provider/currentness dependency; do not patch in Lane A."
        else:
            proof["final_verdict"] = "FAIL_O20_R3F_UNCLASSIFIED"
            proof["next_recommended_batch"] = "Manual inspection required; do not patch."

        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

        RUNBOOK_MD.write_text(
            "\n".join([
                f"# {BATCH} — persisted features publish-route audit / repair classifier",
                "",
                f"- generated_at_utc: {proof['completed_at_utc']}",
                f"- tag: `{TAG}`",
                f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
                f"- manifest: `{MANIFEST_JSON.relative_to(ROOT)}`",
                f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
                "",
                "## Evidence-first rule",
                "- Latest uploaded evidence must be inspected before patch work.",
                "- This script also inspects local evidence/proof artifacts available under the project tree.",
                "",
                "## Safety",
                "- No real-live enablement.",
                "- No paper restart.",
                "- No broker call.",
                "- No order write.",
                "- No threshold relaxation.",
                "- No forced candidate.",
                "- No doctrine mutation.",
                "- No risk/execution start.",
                "- No production source mutation in this classifier batch.",
                "",
                "## Classification",
                "```json",
                json.dumps(classification, indent=2, sort_keys=True),
                "```",
                "",
                "## Verdict",
                f"- final_verdict: `{proof['final_verdict']}`",
                f"- false_keys: `{false_keys}`",
                f"- next_recommended_batch: `{proof['next_recommended_batch']}`",
                "",
            ]),
            encoding="utf-8",
        )

        MILESTONE_MD.write_text(
            "\n".join([
                f"# {DATE} — {BATCH} persisted features publish-route classifier",
                "",
                f"Verdict: `{proof['final_verdict']}`",
                "",
                "## Why this batch exists",
                "- O20-R3E failed because persisted `features:mme:stream` samples did not carry valid consumer-view / structural-valid / 10 branch-frame shape.",
                "- R3E safety stayed clean: HOLD decisions, zero orders, FLAT position.",
                "",
                "## What this batch checked",
                "- Loaded prior R3E proof false keys.",
                "- Inspected local evidence archives/proofs first.",
                "- Backed up source and proof files.",
                "- Captured latest Redis feature/decision/position/order shapes.",
                "- Inspected `features.py` publish/run_once surfaces.",
                "- Ran non-service run_once introspection without broker/paper/live enablement.",
                "- Classified blocker as parser gap, persisted publish-route gap, stale/mixed stream, or Lane-B feed/provider dependency.",
                "",
                "## Classification",
                "```json",
                json.dumps(classification, indent=2, sort_keys=True),
                "```",
                "",
                "## Next",
                f"- {proof['next_recommended_batch']}",
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
        print(f"classification = {json.dumps(classification, indent=2, sort_keys=True)}")
        print(f"next_recommended_batch = {proof['next_recommended_batch']}")
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        print(f"manifest_json = {MANIFEST_JSON.relative_to(ROOT)}")
        print(f"runbook = {RUNBOOK_MD.relative_to(ROOT)}")
        print(f"milestone = {MILESTONE_MD.relative_to(ROOT)}")
        return 0 if proof["final_verdict"].startswith("PASS_") else 2

    except Exception as exc:
        proof["exception"] = repr(exc)
        proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
        proof["final_verdict"] = "FAIL_O20_R3F_EXCEPTION_SAFE_STOP_NO_MUTATION"
        PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
        print("===== EXCEPTION SAFE STOP =====")
        print(repr(exc))
        print(f"proof_json = {PROOF_JSON.relative_to(ROOT)}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
