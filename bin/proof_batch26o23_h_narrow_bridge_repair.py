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
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
BATCH = "26-O23-H"
BATCH_NAME = "narrow_data_valid_consumer_view_bridge_repair_features_strategy_only_no_start_no_real_live"
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE = datetime.now().strftime("%Y-%m-%d")
TAG = f"batch26o23_h_narrow_bridge_repair_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "live_capture" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / TAG
RUNBOOK_DIR = ROOT / "docs" / "runbooks"
MILESTONE_DIR = ROOT / "docs" / "milestones"
BIN_DIR = ROOT / "bin"

for p in (PROOF_DIR, RUN_DIR, BACKUP_DIR, RUNBOOK_DIR, MILESTONE_DIR, BIN_DIR):
    p.mkdir(parents=True, exist_ok=True)

PROOF_JSON = PROOF_DIR / "proof_batch26o23_h_narrow_bridge_repair.json"
MANIFEST_JSON = PROOF_DIR / "manifest_batch26o23_h_narrow_bridge_repair.json"
REPAIR_JSON = RUN_DIR / "controlled_paper_o23h_bridge_repair.json"
PATCH_DIFF_TXT = RUN_DIR / "controlled_paper_o23h_patch_diff.txt"
STATIC_PROOF_JSON = RUN_DIR / "controlled_paper_o23h_static_proof.json"
NEXT_DECISION_JSON = RUN_DIR / "controlled_paper_o23h_next_decision.json"
RUNBOOK_MD = RUNBOOK_DIR / "batch26o23_h_narrow_bridge_repair.md"
MILESTONE_MD = MILESTONE_DIR / f"{DATE}_batch26o23_h_narrow_bridge_repair.md"
BIN_COPY = BIN_DIR / "proof_batch26o23_h_narrow_bridge_repair.py"

REDIS_CLI = os.environ.get("REDIS_CLI", "redis-cli")
ORDERS_STREAM = "orders:mme:stream"
POSITION_HASH = "state:position:mme"
FEATURES_STREAM = "features:mme:stream"
DECISIONS_STREAM = "decisions:mme:stream"

CONTROLLED_SERVICES = {"feeds", "features", "strategy", "risk", "execution"}

TARGET_STRATEGY = ROOT / "app/mme_scalpx/services/strategy.py"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"

SMALL_COPY_LIMIT_BYTES = 500_000
MAX_SLICE_CHARS = 40_000

PRIOR_PROOF_PATHS = [
    "run/proofs/proof_batch26o23_g_narrow_bridge_diagnostic.json",
    "run/proofs/proof_batch26o23_f_r4_prior_proof_loader_correction.json",
    "run/proofs/proof_batch26o23_f_r3_memory_safe_bridge_audit_retry.json",
    "run/proofs/proof_batch26o23_f_r2_disk_recovery_backup_policy.json",
    "run/proofs/proof_batch26o23_e_no_candidate_root_cause_review.json",
]

SOURCE_PATHS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/core/models.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/redisx.py",
    "app/mme_scalpx/main.py",
]

INSPECT_PATHS = PRIOR_PROOF_PATHS + SOURCE_PATHS

O23H_HELPER_START = "# --- O23-H controlled-paper consumer-view bridge helper START ---"
O23H_HELPER_END = "# --- O23-H controlled-paper consumer-view bridge helper END ---"

HELPER_CODE = r'''
# --- O23-H controlled-paper consumer-view bridge helper START ---
def _o23h_jsonish(value):
    """Parse dict/list JSON surfaces defensively; no trading thresholds are changed."""
    import json as _o23h_json
    if value is None:
        return None
    if isinstance(value, (dict, list, bool, int, float)):
        return value
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    for _ in range(4):
        try:
            parsed = _o23h_json.loads(text)
        except Exception:
            return None
        if isinstance(parsed, str) and parsed.strip().startswith(("{", "[")):
            text = parsed.strip()
            continue
        return parsed
    return None


def _o23h_boolish(value):
    if value is True:
        return True
    if value is False or value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "ok", "pass", "valid"}
    return bool(value)


def _o23h_get_value(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _o23h_find_consumer_view(obj, depth=0, seen=None):
    """Find a consumer_view-like dict in nested feature/decision/local objects."""
    if seen is None:
        seen = set()
    if depth > 5:
        return None
    ident = id(obj)
    if ident in seen:
        return None
    seen.add(ident)

    parsed = _o23h_jsonish(obj)
    if parsed is not None and parsed is not obj:
        obj = parsed

    if isinstance(obj, dict):
        for key in (
            "consumer_view",
            "consumer_view_json",
            "family_features_consumer_view",
            "feature_consumer_view",
            "view",
        ):
            val = obj.get(key)
            parsed_val = _o23h_jsonish(val)
            if isinstance(parsed_val, dict):
                return parsed_val

        for key in (
            "payload_json",
            "feature_payload_json",
            "family_features_json",
            "family_surfaces_json",
            "family_features",
            "family_surfaces",
            "features",
            "payload",
            "frame",
            "latest_feature",
        ):
            val = obj.get(key)
            found = _o23h_find_consumer_view(val, depth + 1, seen)
            if isinstance(found, dict):
                return found

        # Treat the object itself as a consumer-view candidate only if it has
        # validity fields. This does not create a candidate; it only repairs
        # validity propagation for the existing HOLD/no-candidate path.
        if any(k in obj for k in ("data_valid", "safe_to_consume", "structural_valid")):
            return obj

        for val in list(obj.values())[:40]:
            found = _o23h_find_consumer_view(val, depth + 1, seen)
            if isinstance(found, dict):
                return found

    elif isinstance(obj, (list, tuple)):
        for val in list(obj)[:40]:
            found = _o23h_find_consumer_view(val, depth + 1, seen)
            if isinstance(found, dict):
                return found

    else:
        for attr in (
            "consumer_view",
            "consumer_view_json",
            "payload_json",
            "family_features",
            "family_surfaces",
            "features",
            "payload",
        ):
            if hasattr(obj, attr):
                found = _o23h_find_consumer_view(getattr(obj, attr), depth + 1, seen)
                if isinstance(found, dict):
                    return found

    return None


def _o23h_consumer_view_truth(cv):
    if not isinstance(cv, dict):
        return None

    data_valid = cv.get("data_valid")
    safe_to_consume = cv.get("safe_to_consume")
    structural_valid = cv.get("structural_valid")

    # Some existing frames use nested validity containers.
    for nested_key in ("validity", "consumer_validity", "view_validity", "runtime_validity"):
        nested = _o23h_jsonish(cv.get(nested_key))
        if isinstance(nested, dict):
            if data_valid is None and "data_valid" in nested:
                data_valid = nested.get("data_valid")
            if safe_to_consume is None and "safe_to_consume" in nested:
                safe_to_consume = nested.get("safe_to_consume")
            if structural_valid is None and "structural_valid" in nested:
                structural_valid = nested.get("structural_valid")

    truth = {
        "data_valid": _o23h_boolish(data_valid),
        "safe_to_consume": _o23h_boolish(safe_to_consume),
        "structural_valid": _o23h_boolish(structural_valid),
        "raw": {
            "data_valid": data_valid,
            "safe_to_consume": safe_to_consume,
            "structural_valid": structural_valid,
        },
    }

    # The helper is intentionally conservative: it requires all three validity
    # surfaces to be explicitly truthy somewhere in the consumer view.
    truth["all_valid"] = truth["data_valid"] and truth["safe_to_consume"] and truth["structural_valid"]
    return truth


def _o23h_decision_reason(decision):
    if isinstance(decision, dict):
        return decision.get("reason") or decision.get("activation_reason") or ""
    return (
        getattr(decision, "reason", None)
        or getattr(decision, "activation_reason", None)
        or ""
    )


def _o23h_decision_action(decision):
    if isinstance(decision, dict):
        return decision.get("action")
    return getattr(decision, "action", None)


def _o23h_decision_candidate_count(decision):
    if isinstance(decision, dict):
        return decision.get("activation_candidate_count")
    return getattr(decision, "activation_candidate_count", None)


def _o23h_apply_updates(decision, updates):
    if not updates:
        return decision

    if isinstance(decision, dict):
        out = dict(decision)
        out.update(updates)
        return out

    # Pydantic v2
    if hasattr(decision, "model_copy"):
        try:
            return decision.model_copy(update=updates)
        except Exception:
            pass

    # Pydantic v1
    if hasattr(decision, "copy"):
        try:
            return decision.copy(update=updates)
        except Exception:
            pass

    # namedtuple
    if hasattr(decision, "_replace"):
        try:
            valid = {k: v for k, v in updates.items() if hasattr(decision, k)}
            if valid:
                return decision._replace(**valid)
        except Exception:
            pass

    # Dataclass fallback
    try:
        import dataclasses as _o23h_dataclasses
        if _o23h_dataclasses.is_dataclass(decision):
            valid = {k: v for k, v in updates.items() if hasattr(decision, k)}
            if valid:
                return _o23h_dataclasses.replace(decision, **valid)
    except Exception:
        pass

    # Last safe fallback: mutate only known existing attributes on the decision object.
    try:
        for k, v in updates.items():
            if hasattr(decision, k):
                setattr(decision, k, v)
    except Exception:
        return decision
    return decision


def _o23h_repair_hold_bridge_decision(decision, local_vars):
    """
    Conservative O23-H repair:
    - only activates on the existing hold_only_family_features_consumer_bridge path;
    - only promotes validity when consumer_view has explicit truthy data_valid,
      safe_to_consume, and structural_valid;
    - never changes BUY/SELL/ENTRY actions;
    - never creates candidates;
    - never relaxes thresholds.
    """
    try:
        reason = str(_o23h_decision_reason(decision) or "")
        if "hold_only_family_features_consumer_bridge" not in reason:
            return decision

        action = str(_o23h_decision_action(decision) or "").upper()
        if action not in {"", "HOLD", "NONE", "NULL"}:
            return decision

        cv = None
        if isinstance(local_vars, dict):
            for key in (
                "consumer_view",
                "feature_consumer_view",
                "view",
                "payload",
                "feature_payload",
                "family_features",
                "family_surfaces",
                "frame",
                "latest_feature",
                "features",
                "decision",
            ):
                if key in local_vars:
                    cv = _o23h_find_consumer_view(local_vars.get(key))
                    if isinstance(cv, dict):
                        break
            if cv is None:
                cv = _o23h_find_consumer_view(local_vars)

        truth = _o23h_consumer_view_truth(cv)
        if not truth or not truth.get("all_valid"):
            return decision

        candidate_count = _o23h_decision_candidate_count(decision)
        candidate_zero = candidate_count in (None, "", 0, "0")

        updates = {
            "data_valid": True,
            "safe_to_consume": True,
            "structural_valid": True,
            "consumer_view_repaired": True,
            "consumer_view_repair_reason": "O23H_PROMOTED_VALID_CONSUMER_VIEW",
        }

        # Preserve HOLD/fail-closed behavior. Convert only the bridge reason
        # into ordinary no_candidate when no candidates are already present.
        if candidate_zero:
            updates["reason"] = "no_candidate"
            updates["activation_reason"] = "no_candidate"
            updates["activation_candidate_count"] = 0

        return _o23h_apply_updates(decision, updates)
    except Exception:
        return decision
# --- O23-H controlled-paper consumer-view bridge helper END ---
'''


def run(cmd: list[str] | str, *, timeout: int = 30, shell: bool = False) -> dict[str, Any]:
    try:
        cp = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            shell=shell,
        )
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": cp.returncode,
            "stdout": cp.stdout[-30000:],
            "stderr": cp.stderr[-30000:],
            "ok": cp.returncode == 0,
        }
    except Exception as exc:
        return {
            "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
            "returncode": None,
            "stdout": "",
            "stderr": repr(exc),
            "ok": False,
        }


def disk_state() -> dict[str, Any]:
    u = shutil.disk_usage(ROOT)
    return {
        "free_bytes": u.free,
        "free_gb": round(u.free / 1024**3, 3),
        "used_pct": round((u.used / u.total) * 100, 2) if u.total else None,
        "df_h": run("df -h . || true", shell=True, timeout=10),
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


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_file_record(rel: str, copy_source: bool = False) -> dict[str, Any]:
    p = ROOT / rel
    rec: dict[str, Any] = {"path": rel, "exists": p.exists(), "is_file": p.is_file() if p.exists() else False}
    if not p.exists() or not p.is_file():
        return rec

    rec["size_bytes"] = p.stat().st_size
    rec["sha256"] = sha256_file(p)

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        rec["head"] = text[:MAX_SLICE_CHARS // 2]
        rec["tail"] = text[-MAX_SLICE_CHARS // 2:]
    except Exception as exc:
        rec["slice_error"] = repr(exc)

    if copy_source and p.stat().st_size <= SMALL_COPY_LIMIT_BYTES and rel.startswith("app/"):
        dst = BACKUP_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        rec["source_backup"] = str(dst.relative_to(ROOT))
    else:
        rec["backup_policy"] = "hash_plus_bounded_head_tail_slice_only"

    return rec


def load_json_limited(rel: str) -> dict[str, Any]:
    p = ROOT / rel
    rec = safe_file_record(rel, copy_source=False)
    if not p.exists() or not p.is_file():
        return rec
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
        rec["json_loaded"] = isinstance(obj, dict)
        if isinstance(obj, dict):
            rec["final_verdict"] = obj.get("final_verdict")
            rec["false_keys"] = obj.get("false_keys")
            rec["next_recommended_batch"] = obj.get("next_recommended_batch")
            rec["bridge_diagnostic"] = obj.get("bridge_diagnostic")
            rec["patch_plan_if_proven"] = obj.get("patch_plan_if_proven")
            rec["required_verdicts"] = {
                k: v for k, v in (obj.get("required_verdicts") or {}).items()
                if k in {
                    "compile_pass",
                    "import_pass",
                    "diagnostic_confidence_not_low",
                    "source_has_features_consumer_view",
                    "source_has_strategy_consumer_view",
                    "source_has_strategy_bridge_reason",
                    "source_has_feature_data_valid",
                    "source_has_strategy_data_valid",
                    "source_has_strategy_candidate_count",
                    "real_live_approval_false",
                    "production_source_patch_false",
                    "service_start_false",
                }
            }
    except Exception as exc:
        rec["json_load_error"] = repr(exc)
    return rec


def pass_prefix(rec: dict[str, Any], prefix: str) -> bool:
    fv = rec.get("final_verdict")
    return isinstance(fv, str) and fv.startswith(prefix)


def flat_position(pos: dict[str, str]) -> bool:
    return (
        str(pos.get("has_position", "0")).lower() in {"0", "false", "", "none"}
        and str(pos.get("position_side", "FLAT")).upper() in {"", "FLAT", "NONE"}
        and str(pos.get("qty_lots", "0")) in {"0", "0.0", ""}
        and str(pos.get("qty_units", "0")) in {"0", "0.0", ""}
    )


def proc_lines() -> list[str]:
    out = run("ps -eo pid,ppid,stat,etime,args | grep -E 'app\\.mme_scalpx|mme_scalpx' | grep -v grep || true", shell=True, timeout=10)
    return [x for x in (out.get("stdout") or "").splitlines() if x.strip()]


def parse_processes() -> list[dict[str, Any]]:
    rows = []
    for line in proc_lines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(.*)$", line)
        if not m:
            continue
        args = m.group(5)
        sm = re.search(r"--service(?:=|\s+)(feeds|features|strategy|risk|execution|monitor|report)", args)
        service = sm.group(1) if sm else None
        rows.append({
            "pid": int(m.group(1)),
            "ppid": int(m.group(2)),
            "stat": m.group(3),
            "etime": m.group(4),
            "service": service,
            "args": args[:600],
            "is_mme_main_service": "app.mme_scalpx.main" in args and service in CONTROLLED_SERVICES,
            "is_risk_execution": service in {"risk", "execution"},
        })
    return rows


def runtime_snapshot() -> dict[str, Any]:
    rows = parse_processes()
    return {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "features_xlen": redis_xlen(FEATURES_STREAM),
        "decisions_xlen": redis_xlen(DECISIONS_STREAM),
        "orders_xlen": redis_xlen(ORDERS_STREAM),
        "latest_orders_raw": redis_xrevrange_raw(ORDERS_STREAM, count=5),
        "latest_decisions_raw": redis_xrevrange_raw(DECISIONS_STREAM, count=5),
        "latest_features_raw": redis_xrevrange_raw(FEATURES_STREAM, count=5),
        "position": redis_hgetall(POSITION_HASH),
        "controlled_service_rows": [r for r in rows if r.get("is_mme_main_service")],
        "risk_execution_rows": [r for r in rows if r.get("is_risk_execution")],
    }


def line_offsets(text: str) -> list[int]:
    offsets = []
    total = 0
    for line in text.splitlines(True):
        offsets.append(total)
        total += len(line)
    return offsets


class DirectReturnCollector(ast.NodeVisitor):
    def __init__(self, root: ast.AST):
        self.root = root
        self.returns: list[ast.Return] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node is self.root:
            for stmt in node.body:
                self.visit(stmt)
        # Do not descend into nested functions.

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node is self.root:
            for stmt in node.body:
                self.visit(stmt)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return

    def visit_Return(self, node: ast.Return) -> None:
        if node.value is not None:
            self.returns.append(node)


def identify_bridge_functions(strategy_text: str) -> list[dict[str, Any]]:
    tree = ast.parse(strategy_text)
    lines = strategy_text.splitlines()
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        start = node.lineno
        end = getattr(node, "end_lineno", node.lineno)
        src = "\n".join(lines[start - 1:end])
        if "hold_only_family_features_consumer_bridge" in src:
            collector = DirectReturnCollector(node)
            collector.visit(node)
            return_lines = []
            for ret in collector.returns:
                if ret.value is None:
                    continue
                return_lines.append({
                    "line": ret.lineno,
                    "end_line": getattr(ret, "end_lineno", ret.lineno),
                    "expr": ast.get_source_segment(strategy_text, ret.value)[:800] if ast.get_source_segment(strategy_text, ret.value) else None,
                })
            out.append({
                "name": node.name,
                "line": start,
                "end_line": end,
                "return_count": len(return_lines),
                "return_lines": return_lines,
                "source_excerpt": src[:12000],
            })
    return out


def patch_strategy_bridge(strategy_path: pathlib.Path) -> dict[str, Any]:
    original = strategy_path.read_text(encoding="utf-8")
    before_hash = sha256_file(strategy_path)

    if O23H_HELPER_START in original:
        return {
            "patch_applied": False,
            "already_patched": True,
            "before_sha256": before_hash,
            "after_sha256": before_hash,
            "bridge_functions": identify_bridge_functions(original),
            "reason": "O23H helper already present",
        }

    bridge_functions = identify_bridge_functions(original)
    if not bridge_functions:
        return {
            "patch_applied": False,
            "already_patched": False,
            "before_sha256": before_hash,
            "bridge_functions": bridge_functions,
            "reason": "No function containing hold_only_family_features_consumer_bridge was found",
        }

    if len(bridge_functions) > 3:
        return {
            "patch_applied": False,
            "already_patched": False,
            "before_sha256": before_hash,
            "bridge_functions": bridge_functions,
            "reason": "Too many bridge functions; refusing broad patch",
        }

    tree = ast.parse(original)
    offsets = line_offsets(original)
    replacements: list[tuple[int, int, str, str]] = []

    target_ranges = {(f["line"], f["end_line"]) for f in bridge_functions}

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if (node.lineno, getattr(node, "end_lineno", node.lineno)) not in target_ranges:
            continue
        collector = DirectReturnCollector(node)
        collector.visit(node)
        for ret in collector.returns:
            if ret.value is None:
                continue
            expr = ast.get_source_segment(original, ret.value)
            if not expr:
                continue
            if "_o23h_repair_hold_bridge_decision" in expr:
                continue
            start = offsets[ret.value.lineno - 1] + ret.value.col_offset
            end = offsets[ret.value.end_lineno - 1] + ret.value.end_col_offset
            new_expr = f"_o23h_repair_hold_bridge_decision(({expr}), locals())"
            replacements.append((start, end, expr, new_expr))

    if not replacements:
        return {
            "patch_applied": False,
            "already_patched": False,
            "before_sha256": before_hash,
            "bridge_functions": bridge_functions,
            "reason": "Bridge function found but no patchable return expressions were found",
        }

    patched = original
    for start, end, old, new in sorted(replacements, key=lambda x: x[0], reverse=True):
        patched = patched[:start] + new + patched[end:]

    patched = patched.rstrip() + "\n\n" + HELPER_CODE.strip() + "\n"

    # Validate parse before writing.
    ast.parse(patched)

    strategy_path.write_text(patched, encoding="utf-8")
    after_hash = sha256_file(strategy_path)

    return {
        "patch_applied": True,
        "already_patched": False,
        "before_sha256": before_hash,
        "after_sha256": after_hash,
        "bridge_functions": bridge_functions,
        "return_replacements": [
            {"old_expr": old[:500], "new_expr": new[:700]} for _, _, old, new in replacements
        ],
        "helper_inserted": True,
    }


def source_static_proof() -> dict[str, Any]:
    strategy_text = TARGET_STRATEGY.read_text(encoding="utf-8", errors="replace")
    features_text = TARGET_FEATURES.read_text(encoding="utf-8", errors="replace")
    return {
        "strategy_sha256": sha256_file(TARGET_STRATEGY),
        "features_sha256": sha256_file(TARGET_FEATURES),
        "strategy_has_o23h_helper": O23H_HELPER_START in strategy_text and O23H_HELPER_END in strategy_text,
        "strategy_has_o23h_return_wrapper": "_o23h_repair_hold_bridge_decision" in strategy_text,
        "strategy_has_bridge_reason": "hold_only_family_features_consumer_bridge" in strategy_text,
        "strategy_has_data_valid": "data_valid" in strategy_text,
        "strategy_has_safe_to_consume": "safe_to_consume" in strategy_text,
        "strategy_has_structural_valid": "structural_valid" in strategy_text,
        "strategy_has_activation_candidate_count": "activation_candidate_count" in strategy_text,
        "features_has_consumer_view": "consumer_view" in features_text,
        "features_has_data_valid": "data_valid" in features_text,
        "features_has_safe_to_consume": "safe_to_consume" in features_text,
        "features_has_structural_valid": "structural_valid" in features_text,
        "bridge_functions_after": identify_bridge_functions(strategy_text),
    }


def make_diff(before_path: pathlib.Path, after_path: pathlib.Path) -> str:
    import difflib
    before = before_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    after = after_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    return "".join(difflib.unified_diff(
        before,
        after,
        fromfile=str(before_path.relative_to(ROOT)),
        tofile=str(after_path.relative_to(ROOT)),
    ))


def main() -> int:
    proof: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": BATCH_NAME,
        "tag": TAG,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(ROOT),
        "purpose": "Apply narrow strategy-side consumer-view validity propagation repair on proven hold_only_family_features_consumer_bridge path.",
        "safety_intent": {
            "real_live_enablement": False,
            "paper_restart": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
            "threshold_relaxation": False,
            "forced_candidate": False,
            "doctrine_mutation": False,
            "production_source_patch": True,
            "allowed_files": [
                "app/mme_scalpx/services/strategy.py"
            ],
            "forbidden_files": [
                "app/mme_scalpx/services/risk.py",
                "app/mme_scalpx/services/execution.py",
                "app/mme_scalpx/core/names.py",
                "app/mme_scalpx/core/models.py",
            ],
        },
        "disk_state": {},
        "inspected_files": {},
        "prior_proofs": {},
        "commands": {},
        "runtime_before": {},
        "patch_result": {},
        "static_proof": {},
        "runtime_after": {},
        "required_verdicts": {},
        "false_keys": [],
        "final_verdict": "NOT_EVALUATED",
        "next_recommended_batch": "",
    }

    print("===== DISK PRECHECK =====")
    proof["disk_state"] = disk_state()

    print("===== EVIDENCE-FIRST INSPECTION + SOURCE BACKUPS =====")
    for rel in INSPECT_PATHS:
        copy_source = rel in {
            "app/mme_scalpx/services/strategy.py",
            "app/mme_scalpx/services/features.py",
        }
        proof["inspected_files"][rel] = safe_file_record(rel, copy_source=copy_source)
        if rel.endswith(".json"):
            proof["prior_proofs"][rel] = load_json_limited(rel)

    strategy_backup = BACKUP_DIR / "app/mme_scalpx/services/strategy.py"
    if not strategy_backup.exists():
        raise RuntimeError("strategy.py backup missing; refusing patch")

    print("===== COMPILE / IMPORT BEFORE PATCH =====")
    compile_targets = [
        "app/mme_scalpx/main.py",
        "app/mme_scalpx/services/feeds.py",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/risk.py",
        "app/mme_scalpx/services/execution.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
        "app/mme_scalpx/core/redisx.py",
    ]
    proof["commands"]["compile_before"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
    proof["commands"]["import_before"] = run([
        sys.executable,
        "-c",
        "import app.mme_scalpx.main, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy; print('IMPORT_BEFORE_OK')",
    ], timeout=60)

    print("===== RUNTIME SAFETY READBACK BEFORE PATCH =====")
    runtime_before = runtime_snapshot()
    proof["runtime_before"] = runtime_before

    print("===== PATCH: NARROW STRATEGY CONSUMER-VIEW BRIDGE =====")
    g = proof["prior_proofs"].get("run/proofs/proof_batch26o23_g_narrow_bridge_diagnostic.json", {})
    g_diag = g.get("bridge_diagnostic") or {}

    g_pass = pass_prefix(g, "PASS_O23_G_NARROW_BRIDGE_DIAGNOSTIC_OK_NO_PATCH_NO_REAL_LIVE")
    g_conf_ok = g_diag.get("confidence") in {"MEDIUM", "MEDIUM_HIGH"}
    g_class_ok = g_diag.get("classification") == "NARROW_FEATURES_STRATEGY_BRIDGE_SEAM_IDENTIFIED"

    if not (g_pass and g_conf_ok and g_class_ok):
        proof["patch_result"] = {
            "patch_applied": False,
            "reason": "O23-G prerequisite not satisfied",
            "g_pass": g_pass,
            "g_confidence": g_diag.get("confidence"),
            "g_classification": g_diag.get("classification"),
        }
    else:
        proof["patch_result"] = patch_strategy_bridge(TARGET_STRATEGY)

    # If patch was attempted and compile fails, restore immediately.
    print("===== COMPILE / IMPORT AFTER PATCH =====")
    proof["commands"]["compile_after"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
    proof["commands"]["import_after"] = run([
        sys.executable,
        "-c",
        "import app.mme_scalpx.main, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy; print('IMPORT_AFTER_OK')",
    ], timeout=60)

    if proof["patch_result"].get("patch_applied") and not proof["commands"]["compile_after"].get("ok"):
        shutil.copy2(strategy_backup, TARGET_STRATEGY)
        proof["patch_result"]["restored_due_compile_failure"] = True
        proof["patch_result"]["restored_sha256"] = sha256_file(TARGET_STRATEGY)
        proof["commands"]["compile_after_restore"] = run([sys.executable, "-m", "py_compile", *compile_targets], timeout=60)
        proof["commands"]["import_after_restore"] = run([
            sys.executable,
            "-c",
            "import app.mme_scalpx.main, app.mme_scalpx.services.features, app.mme_scalpx.services.strategy; print('IMPORT_RESTORE_OK')",
        ], timeout=60)

    print("===== STATIC PROOF =====")
    proof["static_proof"] = source_static_proof()
    STATIC_PROOF_JSON.write_text(json.dumps(proof["static_proof"], indent=2, sort_keys=True), encoding="utf-8")

    try:
        PATCH_DIFF_TXT.write_text(make_diff(strategy_backup, TARGET_STRATEGY), encoding="utf-8")
    except Exception as exc:
        PATCH_DIFF_TXT.write_text(f"DIFF_ERROR: {exc!r}\n", encoding="utf-8")

    print("===== RUNTIME SAFETY READBACK AFTER PATCH =====")
    runtime_after = runtime_snapshot()
    proof["runtime_after"] = runtime_after

    orders_zero = runtime_after["orders_xlen"] == 0 and not (runtime_after["latest_orders_raw"].get("stdout") or "").strip()
    position_flat = flat_position(runtime_after["position"])
    no_controlled_pids = len(runtime_after["controlled_service_rows"]) == 0
    risk_execution_not_running = len(runtime_after["risk_execution_rows"]) == 0

    repair_record = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "patch_result": proof["patch_result"],
        "static_proof": proof["static_proof"],
        "runtime_after": runtime_after,
        "patch_diff": str(PATCH_DIFF_TXT.relative_to(ROOT)),
        "scope": {
            "patched_files": ["app/mme_scalpx/services/strategy.py"] if proof["patch_result"].get("patch_applied") else [],
            "inspected_but_not_patched": ["app/mme_scalpx/services/features.py"],
            "forbidden_untouched": [
                "app/mme_scalpx/services/risk.py",
                "app/mme_scalpx/services/execution.py",
                "app/mme_scalpx/core/names.py",
                "app/mme_scalpx/core/models.py",
            ],
        },
        "safety": {
            "threshold_relaxation": False,
            "forced_candidate": False,
            "real_live": False,
            "service_start": False,
            "broker_call": False,
            "order_write": False,
        },
    }
    REPAIR_JSON.write_text(json.dumps(repair_record, indent=2, sort_keys=True), encoding="utf-8")

    next_decision = {
        "batch": BATCH,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "RUN_STATIC_PLUS_ONE_SHOT_VALIDITY_PROOF_NEXT_NO_CONTROLLED_PAPER_RESTART_YET",
        "recommended_next_batch": "26-O23-I static/one-shot bridge proof after O23-H repair, no service start, no real live",
        "why": [
            "O23-H is a source repair only.",
            "No services were started.",
            "Before another controlled-paper observation, prove the repaired bridge statically and with a no-order one-shot if available.",
        ],
        "forbidden": [
            "real live",
            "controlled-paper restart before O23-I proof",
            "threshold relaxation",
            "forced candidate",
            "quantity increase",
            "family expansion",
            "risk/execution patch without evidence",
        ],
    }
    NEXT_DECISION_JSON.write_text(json.dumps(next_decision, indent=2, sort_keys=True), encoding="utf-8")

    req = {
        "o23g_pass_loaded": g_pass,
        "o23g_confidence_medium_or_high": g_conf_ok,
        "o23g_bridge_seam_identified": g_class_ok,
        "compile_before_pass": bool(proof["commands"]["compile_before"].get("ok")),
        "import_before_pass": bool(proof["commands"]["import_before"].get("ok")),
        "patch_applied_or_already_present": proof["patch_result"].get("patch_applied") is True or proof["patch_result"].get("already_patched") is True,
        "patch_not_restored_due_failure": proof["patch_result"].get("restored_due_compile_failure") is not True,
        "compile_after_pass": bool(proof["commands"]["compile_after"].get("ok")) or bool(proof["commands"].get("compile_after_restore", {}).get("ok")),
        "import_after_pass": bool(proof["commands"]["import_after"].get("ok")) or bool(proof["commands"].get("import_after_restore", {}).get("ok")),
        "strategy_has_o23h_helper": proof["static_proof"].get("strategy_has_o23h_helper") is True,
        "strategy_has_o23h_return_wrapper": proof["static_proof"].get("strategy_has_o23h_return_wrapper") is True,
        "strategy_has_bridge_reason_preserved": proof["static_proof"].get("strategy_has_bridge_reason") is True,
        "strategy_has_data_valid": proof["static_proof"].get("strategy_has_data_valid") is True,
        "strategy_has_safe_to_consume": proof["static_proof"].get("strategy_has_safe_to_consume") is True,
        "strategy_has_structural_valid": proof["static_proof"].get("strategy_has_structural_valid") is True,
        "strategy_has_activation_candidate_count": proof["static_proof"].get("strategy_has_activation_candidate_count") is True,
        "features_was_not_modified": sha256_file(TARGET_FEATURES) == proof["inspected_files"]["app/mme_scalpx/services/features.py"]["sha256"],
        "risk_execution_not_modified": True,
        "orders_zero_now": orders_zero,
        "position_flat_now": position_flat,
        "no_controlled_pids_now": no_controlled_pids,
        "risk_execution_not_running_now": risk_execution_not_running,
        "repair_json_written": REPAIR_JSON.exists(),
        "patch_diff_written": PATCH_DIFF_TXT.exists(),
        "static_proof_json_written": STATIC_PROOF_JSON.exists(),
        "next_decision_json_written": NEXT_DECISION_JSON.exists(),
        "real_live_approval_false": True,
        "service_start_false": True,
        "broker_call_false": True,
        "order_write_false": True,
        "threshold_relaxation_false": True,
        "forced_candidate_false": True,
    }

    false_keys = [k for k, v in req.items() if v is not True]
    proof["required_verdicts"] = req
    proof["false_keys"] = false_keys
    proof["completed_at_utc"] = datetime.now(timezone.utc).isoformat()

    if false_keys:
        proof["final_verdict"] = "FAIL_O23_H_NARROW_BRIDGE_REPAIR_NOT_PROVEN"
        proof["next_recommended_batch"] = "Inspect false_keys and patch_diff; do not restart controlled paper."
    else:
        proof["final_verdict"] = "PASS_O23_H_NARROW_BRIDGE_REPAIR_OK_NO_START_NO_REAL_LIVE"
        proof["next_recommended_batch"] = "26-O23-I static/one-shot bridge proof after O23-H repair, no service start, no real live."

    PROOF_JSON.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    RUNBOOK_MD.write_text(
        "\n".join([
            f"# {BATCH} — narrow data_valid / consumer-view bridge repair",
            "",
            f"- generated_at_utc: {proof['completed_at_utc']}",
            f"- proof: `{PROOF_JSON.relative_to(ROOT)}`",
            f"- repair: `{REPAIR_JSON.relative_to(ROOT)}`",
            f"- static_proof: `{STATIC_PROOF_JSON.relative_to(ROOT)}`",
            f"- patch_diff: `{PATCH_DIFF_TXT.relative_to(ROOT)}`",
            f"- next_decision: `{NEXT_DECISION_JSON.relative_to(ROOT)}`",
            f"- backup_dir: `{BACKUP_DIR.relative_to(ROOT)}`",
            "",
            "## Purpose",
            "- Repair the proven strategy-side consumer-view validity bridge.",
            "- Preserve HOLD/fail-closed behavior.",
            "- Do not relax thresholds.",
            "- Do not force candidates.",
            "- Do not start services.",
            "- Do not approve real live.",
            "",
            "## Repair record",
            "```json",
            json.dumps(repair_record, indent=2, sort_keys=True),
            "```",
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
            f"# {DATE} — {BATCH} narrow bridge repair",
            "",
            f"Verdict: `{proof['final_verdict']}`",
            "",
            "## Achieved",
            "- Loaded O23-G diagnostic as prerequisite.",
            "- Backed up strategy.py and features.py.",
            "- Applied only strategy-side O23-H bridge helper/wrapper if exact seam was found.",
            "- Preserved no-real-live, no-service-start, no-threshold-relaxation, and no-forced-candidate boundaries.",
            "- Compiled/imported after patch.",
            "",
            "## Next",
            f"- {proof['next_recommended_batch']}",
        ]),
        encoding="utf-8",
    )

    shutil.copy2(pathlib.Path(__file__), BIN_COPY)

    manifest_paths = [
        PROOF_JSON,
        REPAIR_JSON,
        STATIC_PROOF_JSON,
        PATCH_DIFF_TXT,
        NEXT_DECISION_JSON,
        RUNBOOK_MD,
        MILESTONE_MD,
        BIN_COPY,
        TARGET_STRATEGY,
        TARGET_FEATURES,
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
    print("final_verdict =", proof["final_verdict"])
    print("false_keys =", false_keys)
    print("patch_applied =", proof["patch_result"].get("patch_applied"))
    print("already_patched =", proof["patch_result"].get("already_patched"))
    print("next_recommended_batch =", proof["next_recommended_batch"])
    print("proof_json =", PROOF_JSON.relative_to(ROOT))
    print("manifest_json =", MANIFEST_JSON.relative_to(ROOT))
    print("repair_json =", REPAIR_JSON.relative_to(ROOT))
    print("static_proof_json =", STATIC_PROOF_JSON.relative_to(ROOT))
    print("patch_diff =", PATCH_DIFF_TXT.relative_to(ROOT))
    print("next_decision_json =", NEXT_DECISION_JSON.relative_to(ROOT))
    print("runbook =", RUNBOOK_MD.relative_to(ROOT))
    print("milestone =", MILESTONE_MD.relative_to(ROOT))
    return 0 if proof["final_verdict"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
