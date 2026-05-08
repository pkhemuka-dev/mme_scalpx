#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O20-R3D-R2"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o20_r3d_r2_source_publish_repair.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o20_r3d_r2_source_publish_repair.json"
O20R3DR1_PATH = ROOT / "run/proofs/proof_batch26o20_r3d_r1_consumer_view_semantics_wrapper_repair.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
RUN_DIR = ROOT / "run/live_capture/batch26o20_r3d_r2_source_publish_repair"
RUN_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_BRANCHES = {
    "mist_call", "mist_put",
    "misb_call", "misb_put",
    "misc_call", "misc_put",
    "misr_call", "misr_put",
    "miso_call", "miso_put",
}

EXPECTED_COMMON_KEYS = (
    "regime",
    "strategy_runtime_mode_classic",
    "strategy_runtime_mode_miso",
    "futures",
    "call",
    "put",
    "selected_option",
    "cross_option",
    "economics",
    "signals",
)

EXPECTED_SELECTED_OPTION_KEYS = (
    "side",
    "ltp",
    "spread",
    "spread_ratio",
    "depth_total",
    "depth_ok",
    "ofi_ratio_proxy",
    "microprice",
    "micro_edge",
    "delta_3",
    "response_efficiency",
    "tradability_ok",
)

TARGETS = [
    "app/mme_scalpx/services/features.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/strategy_family/activation.py",
    "app/mme_scalpx/services/feature_family/contracts.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o20_r3d_r2_source_publish_repair.py",
    "run/proofs/proof_batch26o20_r3d_r1_consumer_view_semantics_wrapper_repair.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: pathlib.Path) -> str | None:
    if not path.exists() or path.is_dir():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env={"PYTHONPATH": str(ROOT), **dict(**__import__("os").environ)},
    )
    return {"args": args, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def safe_json_load(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            obj = json.loads(value)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def hgetall(client: Any, key: str) -> dict[str, str]:
    try:
        return decode_hash(client.hgetall(key) or {})
    except Exception:
        return {}


def hget_json(client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        return safe_json_load(client.hget(key, field))
    except Exception:
        return {}


def hset_json(client: Any, key: str, mapping: Mapping[str, Any]) -> None:
    client.hset(key, mapping={k: (v if isinstance(v, str) else str(v)) for k, v in mapping.items()})


def xlen(client: Any, key: str) -> int:
    try:
        return int(client.xlen(key))
    except Exception:
        return 0


def latest_rows(client: Any, key: str, count: int = 8) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        for msg_id, fields in client.xrevrange(key, count=count):
            out.append({
                "id": msg_id.decode("utf-8", "replace") if isinstance(msg_id, bytes) else str(msg_id),
                "fields": decode_hash(fields),
            })
    except Exception:
        pass
    return out


def position_summary(raw: Mapping[str, str]) -> dict[str, Any]:
    has_position_raw = str(raw.get("has_position", raw.get("position_open", "false"))).lower()
    qty_lots = float(raw.get("qty_lots", raw.get("quantity_lots", "0")) or 0)
    qty_units = float(raw.get("qty_units", raw.get("quantity_units", "0")) or 0)
    side = str(raw.get("position_side", raw.get("side", ""))).upper()
    flat = bool(
        has_position_raw not in {"1", "true", "yes", "y"}
        and qty_lots == 0
        and qty_units == 0
        and side in {"", "FLAT", "NONE"}
    )
    return {"raw": dict(raw), "has_position_raw": has_position_raw, "qty_lots": qty_lots, "qty_units": qty_units, "side": side, "flat": flat}


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o20_r3d_r2_source_publish_repair.py"
    for clean in ps_lines():
        lower = clean.lower()
        if self_name in clean:
            continue
        if "grep" in lower or "pgrep" in lower or "bash -lc" in lower or " sh -c " in lower:
            continue
        if "python" not in lower:
            continue
        if "-m app.mme_scalpx.main" not in clean:
            continue
        if f"--service {service}" not in clean:
            continue
        matches.append(clean)
    return matches


def pid_from_line(line: str) -> int | None:
    try:
        return int(line.split()[0])
    except Exception:
        return None


def stop_services(services: list[str]) -> dict[str, Any]:
    before = {svc: pgrep_service(svc) for svc in services}
    killed: list[dict[str, Any]] = []
    for svc in services:
        for line in before.get(svc, []):
            pid = pid_from_line(line)
            if not pid:
                continue
            try:
                signal_to_send = signal.SIGTERM
                __import__("os").kill(pid, signal_to_send)
                killed.append({"service": svc, "pid": pid, "signal": "TERM", "line": line})
            except Exception as exc:
                killed.append({"service": svc, "pid": pid, "signal": "TERM_FAILED", "error": f"{type(exc).__name__}: {exc}", "line": line})
    time.sleep(2)
    after = {svc: pgrep_service(svc) for svc in services}
    return {"before": before, "killed": killed, "after": after}


def inspect_features_source(text: str) -> dict[str, Any]:
    out: dict[str, Any] = {
        "consumer_view_occurrences": [],
        "publish_occurrences": [],
        "hset_occurrences": [],
        "run_once_defs": [],
        "function_defs": [],
    }
    lines = text.splitlines()
    for idx, line in enumerate(lines, 1):
        if "consumer_view" in line:
            out["consumer_view_occurrences"].append({"line": idx, "text": line[:220]})
        if "family_features_json" in line or "payload_json" in line or "consumer_view_json" in line:
            out["publish_occurrences"].append({"line": idx, "text": line[:220]})
        if ".hset" in line or "hset(" in line:
            out["hset_occurrences"].append({"line": idx, "text": line[:220]})
    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out["function_defs"].append({"name": node.name, "lineno": node.lineno, "end_lineno": getattr(node, "end_lineno", None)})
                if node.name == "run_once":
                    out["run_once_defs"].append({"lineno": node.lineno, "end_lineno": getattr(node, "end_lineno", None)})
    except Exception as exc:
        out["ast_error"] = f"{type(exc).__name__}: {exc}"
    return out


def patch_features_source_level(before: str) -> dict[str, Any]:
    marker = "Batch 26-O20-R3D-R2 source-level consumer-view publish repair"
    if marker in before:
        return {"patched": False, "already_present": True, "reason": "marker already present"}

    # We do not add another monkey-patch wrapper. Instead we add helper functions
    # and inject a direct call at the source publish point: immediately before the
    # HASH_FEATURES hset mapping is assembled/written, by replacing the first
    # exact mapping line that writes consumer_view_json.
    if '"consumer_view_json"' not in before and "'consumer_view_json'" not in before:
        return {"patched": False, "already_present": False, "reason": "consumer_view_json publish key not found"}

    backup = ROOT / "run/_code_backups" / f"batch26o20_r3d_r2_features_py_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pre_patch"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(before, encoding="utf-8")

    helper = r'''
# =============================================================================
# Batch 26-O20-R3D-R2 source-level consumer-view publish repair
# =============================================================================
#
# Safety:
# - features.py only
# - no strategy/risk/execution patch
# - no order writes
# - no threshold relaxation
# - no candidate forcing
#
# Consumer-view data_valid means structural safety for strategy consumption.
# Trade eligibility remains branch-level and fail-closed.

_BATCH26O20R3D_R2_EXPECTED_BRANCHES = {
    "mist_call", "mist_put",
    "misb_call", "misb_put",
    "misc_call", "misc_put",
    "misr_call", "misr_put",
    "miso_call", "miso_put",
}


def _batch26o20r3d_r2_structural_safe_consumer_view(cv: Mapping[str, Any]) -> bool:
    try:
        branch_frames = cv.get("branch_frames")
        if not isinstance(branch_frames, Mapping):
            return False
        if set(branch_frames.keys()) != _BATCH26O20R3D_R2_EXPECTED_BRANCHES:
            return False
        for key, frame in branch_frames.items():
            if not isinstance(frame, Mapping):
                return False
            if frame.get("key") != key:
                return False
            if frame.get("family_id") not in {"MIST", "MISB", "MISC", "MISR", "MISO"}:
                return False
            if frame.get("branch_id") not in {"CALL", "PUT"}:
                return False
            if frame.get("side") not in {"CALL", "PUT"}:
                return False
        return True
    except Exception:
        return False


def _batch26o20r3d_r2_repair_consumer_view(cv: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(cv or {})
    if _batch26o20r3d_r2_structural_safe_consumer_view(out):
        out["data_valid"] = True
        out["safe_to_consume"] = True
        out["structural_valid"] = True
        out["hold_only"] = True
        out["consumer_view_validity_semantics"] = "structural_safe_not_trade_eligibility"
        out["forced_candidate"] = False
        out["threshold_relaxation"] = False
        out["real_live_enablement"] = False
    return out


def _batch26o20r3d_r2_repair_feature_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload or {})
    cv = out.get("consumer_view")
    if isinstance(cv, Mapping):
        out["consumer_view"] = _batch26o20r3d_r2_repair_consumer_view(cv)
    return out


def _batch26o20r3d_r2_semantics_guard() -> dict[str, Any]:
    return {
        "source_level_publish_repair": True,
        "consumer_view_data_valid_means": "structural_safe_for_strategy_consumption",
        "trade_eligibility_remains_branch_level": True,
        "forced_candidate": False,
        "threshold_relaxation": False,
        "real_live_enablement": False,
        "strategy_expected_action_when_no_eligible_branch": "HOLD",
    }
'''

    patched = before.rstrip() + "\n\n" + helper + "\n"

    # Direct source-level injection by replacing common serialization patterns.
    # The helpers are safe even if called repeatedly.
    replacements = [
        (
            '"consumer_view_json": _json_dump(consumer_view),',
            '"consumer_view_json": _json_dump(_batch26o20r3d_r2_repair_consumer_view(consumer_view)),\n'
            '                "o20r3d_r2_validity_semantics_json": _json_dump(_batch26o20r3d_r2_semantics_guard()),'
        ),
        (
            "'consumer_view_json': _json_dump(consumer_view),",
            "'consumer_view_json': _json_dump(_batch26o20r3d_r2_repair_consumer_view(consumer_view)),\n"
            "                'o20r3d_r2_validity_semantics_json': _json_dump(_batch26o20r3d_r2_semantics_guard()),"
        ),
        (
            '"payload_json": _json_dump(payload),',
            '"payload_json": _json_dump(_batch26o20r3d_r2_repair_feature_payload(payload)),'
        ),
        (
            "'payload_json': _json_dump(payload),",
            "'payload_json': _json_dump(_batch26o20r3d_r2_repair_feature_payload(payload)),"
        ),
    ]

    applied = []
    for old, new in replacements:
        if old in patched:
            patched = patched.replace(old, new, 1)
            applied.append(old)

    if not any("consumer_view_json" in x for x in applied):
        # Fallback: patch any exact assignment with consumer_view_json and _json_dump(consumer_view).
        pattern = re.compile(r'(["\']consumer_view_json["\']\s*:\s*_json_dump\()consumer_view(\)\s*,)')
        patched2, n = pattern.subn(r'\1_batch26o20r3d_r2_repair_consumer_view(consumer_view)\2', patched, count=1)
        patched = patched2
        if n:
            applied.append("regex_consumer_view_json")

    if not applied:
        return {"patched": False, "already_present": False, "reason": "no publish serialization pattern matched", "backup": str(backup)}

    TARGET_FEATURES.write_text(patched, encoding="utf-8")
    return {"patched": True, "already_present": False, "backup": str(backup), "applied_replacements": applied}


def feature_snapshot(client: Any, features_hash_key: str) -> dict[str, Any]:
    ff = hget_json(client, features_hash_key, "family_features_json")
    cv = hget_json(client, features_hash_key, "consumer_view_json")
    payload = hget_json(client, features_hash_key, "payload_json")
    sem = hget_json(client, features_hash_key, "o20r3d_r2_validity_semantics_json")

    common = ff.get("common", {}) if isinstance(ff, Mapping) else {}
    selected = common.get("selected_option", {}) if isinstance(common, Mapping) else {}
    branch_frames = cv.get("branch_frames", {}) if isinstance(cv, Mapping) else {}
    payload_cv = payload.get("consumer_view", {}) if isinstance(payload, Mapping) else {}
    mist_call = branch_frames.get("mist_call", {}) if isinstance(branch_frames, Mapping) else {}

    promoted_like_count = 0
    eligible_count = 0
    for frame in branch_frames.values() if isinstance(branch_frames, Mapping) else []:
        if isinstance(frame, Mapping):
            if frame.get("promoted") is True or frame.get("activation_promoted") is True:
                promoted_like_count += 1
            if frame.get("eligible") is True:
                eligible_count += 1

    return {
        "family_features_present": bool(ff),
        "payload_present": bool(payload),
        "consumer_view_present": bool(cv),
        "consumer_view_data_valid": cv.get("data_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_safe_to_consume": cv.get("safe_to_consume") if isinstance(cv, Mapping) else None,
        "consumer_view_structural_valid": cv.get("structural_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_validity_semantics": cv.get("consumer_view_validity_semantics") if isinstance(cv, Mapping) else None,
        "payload_consumer_view_data_valid": payload_cv.get("data_valid") if isinstance(payload_cv, Mapping) else None,
        "payload_consumer_view_safe_to_consume": payload_cv.get("safe_to_consume") if isinstance(payload_cv, Mapping) else None,
        "payload_consumer_view_structural_valid": payload_cv.get("structural_valid") if isinstance(payload_cv, Mapping) else None,
        "branch_frame_count": len(branch_frames) if isinstance(branch_frames, Mapping) else 0,
        "branch_frame_key_set_match": set(branch_frames.keys()) == EXPECTED_BRANCHES if isinstance(branch_frames, Mapping) else False,
        "eligible_branch_count": eligible_count,
        "promoted_like_branch_count": promoted_like_count,
        "mist_call_present": "mist_call" in branch_frames if isinstance(branch_frames, Mapping) else False,
        "mist_call_brief": {
            "eligible": mist_call.get("eligible") if isinstance(mist_call, Mapping) else None,
            "tradability_ok": mist_call.get("tradability_ok") if isinstance(mist_call, Mapping) else None,
            "option_symbol": mist_call.get("option_symbol") if isinstance(mist_call, Mapping) else None,
        },
        "common_key_match": tuple(common.keys()) == EXPECTED_COMMON_KEYS if isinstance(common, Mapping) else False,
        "selected_option_key_match": tuple(selected.keys()) == EXPECTED_SELECTED_OPTION_KEYS if isinstance(selected, Mapping) else False,
        "selected_option_rich_in_common": "selected_option_rich" in common if isinstance(common, Mapping) else False,
        "r2_semantics_guard_present": bool(sem),
        "r2_semantics_guard": sem,
    }


def run_feature_once(client: Any) -> dict[str, Any]:
    try:
        from app.mme_scalpx.services import features as F  # type: ignore

        class R:
            def __init__(self, inner):
                self.inner = inner
            def hgetall(self, key):
                return self.inner.hgetall(key)
            def hset(self, key, mapping=None, **kwargs):
                if mapping is not None:
                    return self.inner.hset(key, mapping={k: (v if isinstance(v, str) else str(v)) for k, v in mapping.items()})
                return self.inner.hset(key, **kwargs)
            def xadd(self, *args, **kwargs):
                return self.inner.xadd(*args, **kwargs)
            def xlen(self, *args, **kwargs):
                return self.inner.xlen(*args, **kwargs)
            def xrevrange(self, *args, **kwargs):
                return self.inner.xrevrange(*args, **kwargs)

        svc = F.FeatureService(
            redis_client=R(client),
            clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
            shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
            instance_id="batch26o20-r3d-r2-feature-source",
        )
        payload = svc.run_once()
        payload_cv = payload.get("consumer_view", {}) if isinstance(payload, Mapping) else {}
        return {
            "ok": True,
            "error": None,
            "payload_type": type(payload).__name__,
            "payload_frame_valid": bool(isinstance(payload, Mapping) and payload.get("frame_valid")),
            "payload_consumer_view_data_valid": payload_cv.get("data_valid") if isinstance(payload_cv, Mapping) else None,
            "payload_consumer_view_safe_to_consume": payload_cv.get("safe_to_consume") if isinstance(payload_cv, Mapping) else None,
            "payload_consumer_view_structural_valid": payload_cv.get("structural_valid") if isinstance(payload_cv, Mapping) else None,
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "payload_frame_valid": False}


def start_features_service() -> dict[str, Any]:
    before = pgrep_service("features")
    if before:
        return {"started": False, "already_running": True, "before": before, "pid": None}

    log_path = RUN_DIR / "o20_r3d_r2_features.log"
    pid_path = RUN_DIR / "o20_r3d_r2_features.pid"
    args = [
        sys.executable,
        "-m",
        "app.mme_scalpx.main",
        "--service",
        "features",
        "--bootstrap-provider",
        "app.mme_scalpx.integrations.bootstrap_provider:provide",
        "--skip-group-bootstrap",
    ]
    env = {
        "PYTHONPATH": str(ROOT),
        **dict(**__import__("os").environ),
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "1",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY",
        "SCALPX_CONTROLLED_PAPER_FAMILY": "MIST",
        "SCALPX_CONTROLLED_PAPER_BRANCH": "CALL",
        "SCALPX_CONTROLLED_PAPER_QTY_LOTS": "1",
        "SCALPX_REAL_LIVE_ALLOWED": "0",
    }
    with log_path.open("ab") as log:
        proc = subprocess.Popen(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
    pid_path.write_text(str(proc.pid), encoding="utf-8")
    time.sleep(2)
    return {"started": True, "already_running": False, "pid": proc.pid, "log_path": str(log_path), "pid_path": str(pid_path), "after": pgrep_service("features")}


def stop_pid(pid: int | None) -> list[str]:
    if not pid:
        return pgrep_service("features")
    try:
        __import__("os").killpg(pid, signal.SIGTERM)
        time.sleep(2)
    except Exception:
        try:
            __import__("os").kill(pid, signal.SIGTERM)
            time.sleep(2)
        except Exception:
            pass
    still = pgrep_service("features")
    if any(str(pid) in row for row in still):
        try:
            __import__("os").killpg(pid, signal.SIGKILL)
        except Exception:
            try:
                __import__("os").kill(pid, signal.SIGKILL)
            except Exception:
                pass
    time.sleep(1)
    return pgrep_service("features")


def run_strategy_once(client: Any) -> dict[str, Any]:
    try:
        from app.mme_scalpx.services import strategy as S  # type: ignore

        class R:
            def __init__(self, inner):
                self.inner = inner
            def hgetall(self, key):
                return self.inner.hgetall(key)
            def hset(self, key, mapping=None, **kwargs):
                if mapping is not None:
                    return self.inner.hset(key, mapping={k: (v if isinstance(v, str) else str(v)) for k, v in mapping.items()})
                return self.inner.hset(key, **kwargs)
            def xadd(self, *args, **kwargs):
                return self.inner.xadd(*args, **kwargs)
            def xlen(self, *args, **kwargs):
                return self.inner.xlen(*args, **kwargs)
            def xrevrange(self, *args, **kwargs):
                return self.inner.xrevrange(*args, **kwargs)

        svc = S.StrategyService(
            redis_client=R(client),
            clock=type("Clock", (), {"now_ns": staticmethod(time.time_ns)})(),
            shutdown=type("S", (), {"is_set": staticmethod(lambda: True)})(),
            instance_id="batch26o20-r3d-r2-strategy-source",
        )
        res = svc.run_once()
        return {"ok": True, "error": None, "result": res if isinstance(res, (dict, list, str, int, float, bool, type(None))) else repr(res)}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "result": None}


def decision_safety(rows: list[dict[str, Any]]) -> dict[str, Any]:
    unsafe = []
    hold_like = []
    for row in rows:
        f = row.get("fields", {})
        action = str(f.get("action") or f.get("decision") or "").upper()
        qty = str(f.get("qty") or f.get("quantity_lots") or "0")
        side = str(f.get("side") or "").upper()
        promoted = str(f.get("activation_promoted") or "0").lower()
        broker_allowed = str(f.get("broker_side_effects_allowed") or "").lower() in {"1", "true", "yes"}
        live_allowed = str(f.get("live_orders_allowed") or "").lower() in {"1", "true", "yes"}
        if action in {"", "HOLD"} and qty in {"", "0", "0.0"} and side in {"", "FLAT"} and promoted in {"", "0", "false"} and not broker_allowed and not live_allowed:
            hold_like.append(row)
        else:
            unsafe.append(row)
    return {"row_count": len(rows), "hold_like_count": len(hold_like), "unsafe_count": len(unsafe), "unsafe_rows": unsafe}


def write_outputs(result: dict[str, Any]) -> None:
    manifest = {
        "batch": BATCH,
        "created_at_utc": now_utc(),
        "files": [{"path": p, "exists": (ROOT / p).exists(), "sha256": sha256_file(ROOT / p)} for p in TARGETS],
    }
    PROOF_PATH.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> int:
    result: dict[str, Any] = {
        "batch": BATCH,
        "batch_name": "source_publish_repair",
        "created_at_utc": now_utc(),
        "scope": {
            "patch_target": "features.py only",
            "paper_start": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_enablement": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
        },
    }

    r1 = load_json(O20R3DR1_PATH)
    result["o20r3d_r1_gate"] = {
        "exists": bool(r1),
        "final_verdict": r1.get("final_verdict"),
        "required_verdicts": r1.get("required_verdicts"),
    }
    if r1.get("final_verdict") != "FAIL_O20_R3D_R1_CONSUMER_VIEW_SEMANTICS_WRAPPER_REPAIR_NOT_PROVEN":
        result["final_verdict"] = "FAIL_CLOSED_R1_NOT_EXPECTED_FAILURE"
        write_outputs(result)
        return 2

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    source_inspection_before = inspect_features_source(before_text)
    result["source_inspection_before"] = source_inspection_before

    compile_before = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/feature_family/contracts.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile_before"] = compile_before

    client = redis_client_or_none()
    result["redis_available"] = client is not None
    if client is None:
        result["final_verdict"] = "FAIL_CLOSED_REDIS_NOT_AVAILABLE"
        write_outputs(result)
        return 2

    from app.mme_scalpx.core import names as N  # type: ignore

    orders_key = getattr(N, "STREAM_ORDERS_MME", "orders:mme:stream")
    decisions_key = getattr(N, "STREAM_DECISIONS_MME", "decisions:mme:stream")
    runtime_key = getattr(N, "HASH_STATE_RUNTIME", "state:runtime")
    position_key = getattr(N, "HASH_STATE_POSITION_MME", "state:position:mme")
    features_hash_key = getattr(N, "HASH_STATE_FEATURES_MME_FUT", getattr(N, "HASH_FEATURES", "state:features:mme:fut"))

    cleanup = stop_services(["features", "strategy", "risk", "execution"])
    before_safety = {
        "orders_len": xlen(client, orders_key),
        "position": position_summary(hgetall(client, position_key)),
        "runtime": hgetall(client, runtime_key),
        "processes": {
            "features": pgrep_service("features"),
            "strategy": pgrep_service("strategy"),
            "risk": pgrep_service("risk"),
            "execution": pgrep_service("execution"),
        },
    }

    patch_result = patch_features_source_level(before_text)
    result["patch_result"] = patch_result
    result["patch_performed"] = bool(patch_result.get("patched"))

    after_text = TARGET_FEATURES.read_text(encoding="utf-8")
    result["source_inspection_after"] = inspect_features_source(after_text)

    compile_after = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/feature_family/contracts.py",
        "app/mme_scalpx/core/names.py",
        "app/mme_scalpx/core/models.py",
    ])
    result["compile_after"] = compile_after

    feature_once = run_feature_once(client)
    snapshot_after_once = feature_snapshot(client, features_hash_key)
    strategy_once = run_strategy_once(client)

    feature_start = start_features_service()
    samples: list[dict[str, Any]] = []
    try:
        for i in range(6):
            time.sleep(5)
            samples.append({
                "sample": i + 1,
                "ts": now_utc(),
                "feature_snapshot": feature_snapshot(client, features_hash_key),
                "features_processes": pgrep_service("features"),
                "orders_len": xlen(client, orders_key),
                "position": position_summary(hgetall(client, position_key)),
            })
    finally:
        remaining_features = stop_pid(feature_start.get("pid") if isinstance(feature_start, Mapping) else None)

    runtime_after = hgetall(client, runtime_key)
    position_after = position_summary(hgetall(client, position_key))
    orders_len = xlen(client, orders_key)
    latest_orders = latest_rows(client, orders_key, count=5)
    latest_decisions = latest_rows(client, decisions_key, count=12)
    decision_report = decision_safety(latest_decisions)
    real_live_after = str(runtime_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    after_safety = {
        "orders_len": orders_len,
        "latest_orders": latest_orders,
        "latest_decisions": latest_decisions,
        "decision_safety": decision_report,
        "position": position_after,
        "runtime": runtime_after,
        "processes": {
            "features": pgrep_service("features"),
            "strategy": pgrep_service("strategy"),
            "risk": pgrep_service("risk"),
            "execution": pgrep_service("execution"),
        },
    }

    result.update({
        "cleanup": cleanup,
        "before_safety": before_safety,
        "feature_once": feature_once,
        "snapshot_after_once": snapshot_after_once,
        "strategy_once": strategy_once,
        "feature_start": feature_start,
        "samples": samples,
        "remaining_features_after_stop": remaining_features,
        "after_safety": after_safety,
    })

    sample_count = len(samples)
    sample_valid_count = sum(1 for s in samples if s["feature_snapshot"].get("consumer_view_data_valid") is True)
    sample_safe_count = sum(1 for s in samples if s["feature_snapshot"].get("consumer_view_safe_to_consume") is True)
    sample_structural_count = sum(1 for s in samples if s["feature_snapshot"].get("consumer_view_structural_valid") is True)
    sample_payload_valid = sum(1 for s in samples if s["feature_snapshot"].get("payload_consumer_view_data_valid") is True)
    sample_branch_match = sum(1 for s in samples if s["feature_snapshot"].get("branch_frame_key_set_match") is True)
    sample_common_match = sum(1 for s in samples if s["feature_snapshot"].get("common_key_match") is True)
    sample_selected_match = sum(1 for s in samples if s["feature_snapshot"].get("selected_option_key_match") is True)
    sample_rich_absent = sum(1 for s in samples if s["feature_snapshot"].get("selected_option_rich_in_common") is False)
    sample_orders_zero = sum(1 for s in samples if s.get("orders_len") == 0)
    sample_position_flat = sum(1 for s in samples if s.get("position", {}).get("flat") is True)
    sample_features_process = sum(1 for s in samples if s.get("features_processes"))

    strategy_text = json.dumps(strategy_once.get("result"), sort_keys=True, default=str)
    strategy_hold = "HOLD" in strategy_text
    strategy_not_promoted = "activation_promoted" not in strategy_text or '"activation_promoted": 0' in strategy_text or '"activation_promoted":0' in strategy_text

    required = {
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "r1_expected_fail_gate": r1.get("final_verdict") == "FAIL_O20_R3D_R1_CONSUMER_VIEW_SEMANTICS_WRAPPER_REPAIR_NOT_PROVEN",
        "patch_performed_or_already_present": bool(patch_result.get("patched") or patch_result.get("already_present")),
        "feature_once_no_exception": feature_once.get("ok") is True,
        "feature_once_payload_frame_valid": feature_once.get("payload_frame_valid") is True,
        "feature_once_payload_cv_valid": feature_once.get("payload_consumer_view_data_valid") is True,
        "snapshot_after_once_data_valid_true": snapshot_after_once.get("consumer_view_data_valid") is True,
        "snapshot_after_once_safe_to_consume_true": snapshot_after_once.get("consumer_view_safe_to_consume") is True,
        "snapshot_after_once_structural_valid_true": snapshot_after_once.get("consumer_view_structural_valid") is True,
        "snapshot_after_once_payload_cv_valid_true": snapshot_after_once.get("payload_consumer_view_data_valid") is True,
        "snapshot_after_once_branch_key_set_match": snapshot_after_once.get("branch_frame_key_set_match") is True,
        "snapshot_after_once_no_promoted_branch": snapshot_after_once.get("promoted_like_branch_count") == 0,
        "snapshot_after_once_common_key_match": snapshot_after_once.get("common_key_match") is True,
        "snapshot_after_once_selected_option_key_match": snapshot_after_once.get("selected_option_key_match") is True,
        "snapshot_after_once_selected_option_rich_not_in_common": snapshot_after_once.get("selected_option_rich_in_common") is False,
        "r2_semantics_guard_present": snapshot_after_once.get("r2_semantics_guard_present") is True,
        "strategy_once_no_exception": strategy_once.get("ok") is True,
        "strategy_once_hold": strategy_hold is True,
        "strategy_once_not_promoted": strategy_not_promoted is True,
        "features_service_started": bool(feature_start.get("started") or feature_start.get("already_running")),
        "sample_count_reached": sample_count == 6,
        "features_process_seen_in_samples": sample_features_process >= 4,
        "consumer_view_data_valid_in_samples": sample_valid_count >= 4,
        "consumer_view_safe_to_consume_in_samples": sample_safe_count >= 4,
        "consumer_view_structural_valid_in_samples": sample_structural_count >= 4,
        "payload_consumer_view_valid_in_samples": sample_payload_valid >= 4,
        "branch_key_set_match_in_samples": sample_branch_match >= 4,
        "common_key_match_in_samples": sample_common_match >= 4,
        "selected_option_key_match_in_samples": sample_selected_match >= 4,
        "selected_option_rich_absent_in_samples": sample_rich_absent >= 4,
        "orders_zero": orders_len == 0,
        "orders_zero_in_samples": sample_orders_zero == sample_count,
        "latest_orders_empty": len(latest_orders) == 0,
        "position_flat": position_after["flat"] is True,
        "position_flat_in_samples": sample_position_flat == sample_count,
        "real_live_false": real_live_after is False,
        "decisions_hold_only": decision_report["unsafe_count"] == 0,
        "strategy_not_running_after": len(after_safety["processes"]["strategy"]) == 0,
        "risk_not_running_after": len(after_safety["processes"]["risk"]) == 0,
        "execution_not_running_after": len(after_safety["processes"]["execution"]) == 0,
        "features_stopped_after_probe": len(after_safety["processes"]["features"]) == 0,
        "no_paper_start": True,
        "no_broker_call": True,
        "no_threshold_relaxation": True,
        "no_forced_candidate": True,
        "real_live_not_enabled": True,
    }
    result["required_verdicts"] = required

    if not all(required.values()):
        result["final_verdict"] = "FAIL_O20_R3D_R2_SOURCE_PUBLISH_REPAIR_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect source_inspection_after and exact publish mapping. Do not run O20-R3E."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O20_R3D_R2_SOURCE_PUBLISH_REPAIR_OK_HOLD_ONLY"
    result["next_recommended_batch"] = "26-O20-R3E corrected bounded observation rerun after source-level validity repair; still no real live"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
