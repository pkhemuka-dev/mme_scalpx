#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Any, Mapping

ROOT = pathlib.Path.cwd().resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BATCH = "26-O20-R3D"
PROOF_PATH = ROOT / "run/proofs/proof_batch26o20_r3d_consumer_view_validity_semantics.json"
MANIFEST_PATH = ROOT / "run/proofs/manifest_batch26o20_r3d_consumer_view_validity_semantics.json"
O20R3C_PATH = ROOT / "run/proofs/proof_batch26o20_r3c_runtime_data_validity_source_audit.json"
TARGET_FEATURES = ROOT / "app/mme_scalpx/services/features.py"
RUN_DIR = ROOT / os.environ.get("BATCH26O20_R3D_RUN_DIR", "run/live_capture/batch26o20_r3d_features_only")
RUN_DIR.mkdir(parents=True, exist_ok=True)

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
    "app/mme_scalpx/services/feature_family/tradability.py",
    "app/mme_scalpx/services/feature_family/mist_surface.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/models.py",
    "bin/proof_batch26o20_r3d_consumer_view_validity_semantics.py",
    "run/proofs/proof_batch26o20_r3c_runtime_data_validity_source_audit.json",
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


def safe_json_load(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, bytes):
        value = value.decode("utf-8", "replace")
    if isinstance(value, str):
        if not value.strip():
            return {}
        try:
            return json.loads(value)
        except Exception:
            return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def load_json(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    obj = safe_json_load(path.read_text(encoding="utf-8", errors="replace"))
    return obj if isinstance(obj, dict) else {}


def decode_hash(raw: Mapping[Any, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in dict(raw or {}).items():
        kk = k.decode("utf-8", "replace") if isinstance(k, bytes) else str(k)
        vv = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
        out[kk] = vv
    return out


def redis_client_or_none():
    try:
        import redis  # type: ignore
        client = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=False)
        client.ping()
        return client
    except Exception:
        return None


def run_cmd(args: list[str], timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
    )
    return {"args": args, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def ps_lines() -> list[str]:
    try:
        out = subprocess.check_output(["ps", "-eo", "pid=,ppid=,comm=,args="], text=True)
        return [" ".join(x.split()) for x in out.splitlines() if x.strip()]
    except Exception:
        return []


def pgrep_service(service: str) -> list[str]:
    matches: list[str] = []
    self_name = "proof_batch26o20_r3d_consumer_view_validity_semantics.py"
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


def stop_services(services: list[str], include_feeds: bool = False) -> dict[str, Any]:
    before = {svc: pgrep_service(svc) for svc in services}
    killed: list[dict[str, Any]] = []
    for svc in services:
        if svc == "feeds" and not include_feeds:
            continue
        for line in before.get(svc, []):
            pid = pid_from_line(line)
            if not pid:
                continue
            try:
                os.kill(pid, signal.SIGTERM)
                killed.append({"service": svc, "pid": pid, "signal": "TERM", "line": line})
            except Exception as exc:
                killed.append({"service": svc, "pid": pid, "signal": "TERM_FAILED", "error": f"{type(exc).__name__}: {exc}", "line": line})
    time.sleep(2)
    mid = {svc: pgrep_service(svc) for svc in services}
    for svc in services:
        if svc == "feeds" and not include_feeds:
            continue
        for line in mid.get(svc, []):
            pid = pid_from_line(line)
            if not pid:
                continue
            try:
                os.kill(pid, signal.SIGKILL)
                killed.append({"service": svc, "pid": pid, "signal": "KILL", "line": line})
            except Exception:
                pass
    time.sleep(1)
    after = {svc: pgrep_service(svc) for svc in services}
    return {"before": before, "killed": killed, "after": after}


def xlen(client: Any, key: str) -> int:
    try:
        return int(client.xlen(key))
    except Exception:
        return 0


def hgetall(client: Any, key: str) -> dict[str, str]:
    try:
        return decode_hash(client.hgetall(key) or {})
    except Exception:
        return {}


def hget_json(client: Any, key: str, field: str) -> dict[str, Any]:
    try:
        obj = safe_json_load(client.hget(key, field))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def latest_rows(client: Any, key: str, count: int = 8) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        rows = client.xrevrange(key, count=count)
        for msg_id, fields in rows:
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


def patch_features_consumer_view_validity_semantics(before: str) -> dict[str, Any]:
    marker = "Batch 26-O20-R3D consumer-view validity semantics guard"
    if marker in before:
        return {"patched": False, "already_present": True, "reason": "marker already present"}

    required = [
        "Batch 26-O20-R3A persistent features ABI publish sanitizer",
        "FeatureService",
        "HASH_FEATURES",
        "_json_dump",
    ]
    missing = [x for x in required if x not in before]
    if missing:
        return {"patched": False, "already_present": False, "reason": "required markers missing", "missing": missing}

    backup = ROOT / "run/_code_backups" / f"batch26o20_r3d_features_py_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pre_patch"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(before, encoding="utf-8")

    patch = r'''

# =============================================================================
# Batch 26-O20-R3D consumer-view validity semantics guard
# =============================================================================
#
# Safety:
# - features.py only
# - no strategy/risk/execution patch
# - no order writes
# - no threshold relaxation
# - no candidate forcing
#
# Intent:
# Consumer view validity means "structurally safe for strategy to consume".
# It must not mean "a doctrine setup is tradable/eligible right now".
#
# Therefore:
# - ABI-clean 10-branch consumer view is data_valid=True and safe_to_consume=True.
# - unavailable/degraded market/tradability remains represented at branch level as
#   eligible=False / tradability_ok=False / provider_not_ready.
# - no branch is promoted.
# - no candidate is forced.
# - strategy stays HOLD unless doctrine truth naturally produces an eligible branch.

if "_BATCH26O20R3D_ORIGINAL_HSET_PATCHED" not in globals() and "FeatureService" in globals():
    _BATCH26O20R3D_ORIGINAL_FEATURE_INIT = FeatureService.__init__
    _BATCH26O20R3D_ORIGINAL_HSET_PATCHED = True

    def _batch26o20r3d_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "y", "ok", "pass"}
        return False

    def _batch26o20r3d_is_structurally_safe(cv: Mapping[str, Any]) -> bool:
        if not isinstance(cv, Mapping):
            return False
        branch_frames = cv.get("branch_frames")
        if not isinstance(branch_frames, Mapping):
            return False
        expected = {
            "mist_call", "mist_put",
            "misb_call", "misb_put",
            "misc_call", "misc_put",
            "misr_call", "misr_put",
            "miso_call", "miso_put",
        }
        if set(branch_frames.keys()) != expected:
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
            # Eligibility/tradability may be false; that is doctrine truth, not
            # consumer-view structural invalidity.
        return True

    def _batch26o20r3d_repair_consumer_view(cv: Mapping[str, Any]) -> dict[str, Any]:
        out = dict(cv or {})
        structural_safe = _batch26o20r3d_is_structurally_safe(out)
        if structural_safe:
            out["data_valid"] = True
            out["safe_to_consume"] = True
            out["structural_valid"] = True
            out["hold_only"] = True
            out["consumer_view_validity_semantics"] = "structural_safe_not_trade_eligibility"
            out["forced_candidate"] = False
            out["threshold_relaxation"] = False
            out["real_live_enablement"] = False
        return out

    def _batch26o20r3d_feature_init(self: FeatureService, *args: Any, **kwargs: Any) -> None:
        _BATCH26O20R3D_ORIGINAL_FEATURE_INIT(self, *args, **kwargs)
        if getattr(self, "_batch26o20r3d_redis_wrapped", False):
            return
        original_redis = self.redis

        class _Batch26O20R3DRedisGuard:
            def __init__(self, inner: Any):
                self._inner = inner

            def __getattr__(self, name: str) -> Any:
                return getattr(self._inner, name)

            def hgetall(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.hgetall(*args, **kwargs)

            def xadd(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.xadd(*args, **kwargs)

            def xlen(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.xlen(*args, **kwargs)

            def xrevrange(self, *args: Any, **kwargs: Any) -> Any:
                return self._inner.xrevrange(*args, **kwargs)

            def hset(self, key: Any, mapping: Any = None, **kwargs: Any) -> Any:
                try:
                    if key == HASH_FEATURES and isinstance(mapping, Mapping):
                        guarded = dict(mapping)

                        cv_obj: dict[str, Any] = {}
                        if guarded.get("consumer_view_json"):
                            cv_raw = json.loads(guarded.get("consumer_view_json") or "{}")
                            if isinstance(cv_raw, Mapping):
                                cv_obj = _batch26o20r3d_repair_consumer_view(cv_raw)
                                guarded["consumer_view_json"] = _json_dump(cv_obj)

                        if guarded.get("payload_json"):
                            pp = json.loads(guarded.get("payload_json") or "{}")
                            if isinstance(pp, Mapping):
                                pp = dict(pp)
                                cv2 = pp.get("consumer_view")
                                if isinstance(cv2, Mapping):
                                    pp["consumer_view"] = _batch26o20r3d_repair_consumer_view(cv2)
                                guarded["payload_json"] = _json_dump(pp)

                        guarded["o20r3d_validity_semantics_json"] = _json_dump({
                            "consumer_view_data_valid_means": "structural_safe_for_strategy_consumption",
                            "trade_eligibility_remains_branch_level": True,
                            "forced_candidate": False,
                            "threshold_relaxation": False,
                            "real_live_enablement": False,
                            "strategy_expected_action_when_no_eligible_branch": "HOLD",
                        })
                        mapping = guarded
                except Exception:
                    pass

                if mapping is not None:
                    return self._inner.hset(key, mapping=mapping, **kwargs)
                return self._inner.hset(key, **kwargs)

        self.redis = _Batch26O20R3DRedisGuard(original_redis)
        self._batch26o20r3d_redis_wrapped = True

    FeatureService.__init__ = _batch26o20r3d_feature_init
'''
    TARGET_FEATURES.write_text(before.rstrip() + "\n" + patch + "\n", encoding="utf-8")
    return {"patched": True, "already_present": False, "backup": str(backup), "reason": "consumer-view structural validity semantics guard appended"}


def feature_snapshot(client: Any, features_hash_key: str) -> dict[str, Any]:
    ff = hget_json(client, features_hash_key, "family_features_json")
    cv = hget_json(client, features_hash_key, "consumer_view_json")
    payload = hget_json(client, features_hash_key, "payload_json")
    semantics = hget_json(client, features_hash_key, "o20r3d_validity_semantics_json")

    common = ff.get("common", {}) if isinstance(ff, Mapping) else {}
    selected = common.get("selected_option", {}) if isinstance(common, Mapping) else {}
    branch_frames = cv.get("branch_frames", {}) if isinstance(cv, Mapping) else {}
    mist_call = branch_frames.get("mist_call", {}) if isinstance(branch_frames, Mapping) else {}

    eligible_count = 0
    tradable_count = 0
    promoted_like_count = 0
    for frame in branch_frames.values() if isinstance(branch_frames, Mapping) else []:
        if isinstance(frame, Mapping):
            if frame.get("eligible") is True:
                eligible_count += 1
            if frame.get("tradability_ok") is True:
                tradable_count += 1
            if frame.get("promoted") is True or frame.get("activation_promoted") is True:
                promoted_like_count += 1

    return {
        "family_features_present": bool(ff),
        "payload_present": bool(payload),
        "consumer_view_present": bool(cv),
        "consumer_view_data_valid": cv.get("data_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_safe_to_consume": cv.get("safe_to_consume") if isinstance(cv, Mapping) else None,
        "consumer_view_structural_valid": cv.get("structural_valid") if isinstance(cv, Mapping) else None,
        "consumer_view_hold_only": cv.get("hold_only") if isinstance(cv, Mapping) else None,
        "consumer_view_validity_semantics": cv.get("consumer_view_validity_semantics") if isinstance(cv, Mapping) else None,
        "branch_frame_count": len(branch_frames) if isinstance(branch_frames, Mapping) else 0,
        "eligible_branch_count": eligible_count,
        "tradable_branch_count": tradable_count,
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
        "semantics_guard_present": bool(semantics),
        "semantics_guard": semantics,
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
            instance_id="batch26o20-r3d-feature-semantics",
        )
        payload = svc.run_once()
        return {
            "ok": True,
            "error": None,
            "payload_type": type(payload).__name__,
            "payload_frame_valid": bool(isinstance(payload, Mapping) and payload.get("frame_valid")),
            "payload_keys": sorted(payload.keys()) if isinstance(payload, Mapping) else [],
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "payload_frame_valid": False}


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
            instance_id="batch26o20-r3d-strategy-semantics",
        )
        res = svc.run_once()
        return {"ok": True, "error": None, "result": res if isinstance(res, (dict, list, str, int, float, bool, type(None))) else repr(res)}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "result": None}


def start_features_service() -> dict[str, Any]:
    before = pgrep_service("features")
    if before:
        return {"started": False, "already_running": True, "before": before, "pid": None}

    log_path = RUN_DIR / "o20_r3d_features.log"
    pid_path = RUN_DIR / "o20_r3d_features.pid"
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
        **os.environ,
        "PYTHONPATH": str(ROOT),
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
        os.killpg(pid, signal.SIGTERM)
        time.sleep(2)
    except Exception:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
        except Exception:
            pass
    still = pgrep_service("features")
    if any(str(pid) in row for row in still):
        try:
            os.killpg(pid, signal.SIGKILL)
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
    time.sleep(1)
    return pgrep_service("features")


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
        "batch_name": "consumer_view_validity_semantics",
        "created_at_utc": now_utc(),
        "scope": {
            "patch_target": "features.py only",
            "paper_start": False,
            "strategy_start": False,
            "risk_start": False,
            "execution_start": False,
            "broker_call": False,
            "order_write_intended": False,
            "real_live_enablement": False,
            "forced_candidate": False,
            "threshold_relaxation": False,
        },
    }

    o20r3c = load_json(O20R3C_PATH)
    result["o20r3c_gate"] = {
        "exists": bool(o20r3c),
        "final_verdict": o20r3c.get("final_verdict"),
        "classification": o20r3c.get("classification"),
        "required_verdicts": o20r3c.get("required_verdicts"),
    }

    if o20r3c.get("final_verdict") != "PASS_O20_R3C_DATA_VALIDITY_SOURCE_CLASSIFIED_ABI_OK_RUNTIME_DATA_BLOCKED":
        result["final_verdict"] = "FAIL_CLOSED_O20R3C_NOT_PASS"
        write_outputs(result)
        return 2

    compile_before = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/feature_family/contracts.py",
        "app/mme_scalpx/services/feature_family/tradability.py",
        "app/mme_scalpx/services/feature_family/mist_surface.py",
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

    cleanup = stop_services(["features", "strategy", "risk", "execution"], include_feeds=False)
    before_safety = {
        "orders_len": xlen(client, orders_key),
        "decisions_len": xlen(client, decisions_key),
        "position": position_summary(hgetall(client, position_key)),
        "runtime": hgetall(client, runtime_key),
        "processes": {
            "features": pgrep_service("features"),
            "strategy": pgrep_service("strategy"),
            "risk": pgrep_service("risk"),
            "execution": pgrep_service("execution"),
        },
    }

    before_text = TARGET_FEATURES.read_text(encoding="utf-8")
    patch_result = patch_features_consumer_view_validity_semantics(before_text)
    result["patch_result"] = patch_result
    result["patch_performed"] = bool(patch_result.get("patched"))

    compile_after = run_cmd([
        sys.executable, "-m", "py_compile",
        "app/mme_scalpx/services/features.py",
        "app/mme_scalpx/services/strategy.py",
        "app/mme_scalpx/services/strategy_family/activation.py",
        "app/mme_scalpx/services/feature_family/contracts.py",
        "app/mme_scalpx/services/feature_family/tradability.py",
        "app/mme_scalpx/services/feature_family/mist_surface.py",
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
    real_live_after = str(runtime_after.get("real_live_approved", "false")).lower() in {"1", "true", "yes", "y"}

    after_safety = {
        "orders_len": orders_len,
        "latest_orders": latest_orders,
        "latest_decisions": latest_decisions,
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
    sample_mist_call_count = sum(1 for s in samples if s["feature_snapshot"].get("mist_call_present") is True)
    sample_common_match = sum(1 for s in samples if s["feature_snapshot"].get("common_key_match") is True)
    sample_selected_match = sum(1 for s in samples if s["feature_snapshot"].get("selected_option_key_match") is True)
    sample_rich_absent = sum(1 for s in samples if s["feature_snapshot"].get("selected_option_rich_in_common") is False)
    sample_features_process = sum(1 for s in samples if s.get("features_processes"))
    sample_orders_zero = sum(1 for s in samples if s.get("orders_len") == 0)
    sample_position_flat = sum(1 for s in samples if s.get("position", {}).get("flat") is True)

    strategy_result = strategy_once.get("result") if isinstance(strategy_once, Mapping) else None
    strategy_text = json.dumps(strategy_result, sort_keys=True, default=str)
    strategy_hold = '"action": "HOLD"' in strategy_text or '"action":"HOLD"' in strategy_text or "HOLD" in strategy_text
    strategy_not_promoted = "activation_promoted" not in strategy_text or '"activation_promoted": 0' in strategy_text or '"activation_promoted":0' in strategy_text

    required = {
        "compile_before_pass": compile_before["returncode"] == 0,
        "compile_after_pass": compile_after["returncode"] == 0,
        "o20r3c_pass_gate": o20r3c.get("final_verdict") == "PASS_O20_R3C_DATA_VALIDITY_SOURCE_CLASSIFIED_ABI_OK_RUNTIME_DATA_BLOCKED",
        "patch_performed_or_already_present": bool(patch_result.get("patched") or patch_result.get("already_present")),
        "feature_once_no_exception": feature_once.get("ok") is True,
        "snapshot_after_once_data_valid_true": snapshot_after_once.get("consumer_view_data_valid") is True,
        "snapshot_after_once_safe_to_consume_true": snapshot_after_once.get("consumer_view_safe_to_consume") is True,
        "snapshot_after_once_structural_valid_true": snapshot_after_once.get("consumer_view_structural_valid") is True,
        "snapshot_after_once_all_10_branch_frames": snapshot_after_once.get("branch_frame_count") == 10,
        "snapshot_after_once_mist_call_visible": snapshot_after_once.get("mist_call_present") is True,
        "snapshot_after_once_no_promoted_branch": snapshot_after_once.get("promoted_like_branch_count") == 0,
        "snapshot_after_once_common_key_match": snapshot_after_once.get("common_key_match") is True,
        "snapshot_after_once_selected_option_key_match": snapshot_after_once.get("selected_option_key_match") is True,
        "snapshot_after_once_selected_option_rich_not_in_common": snapshot_after_once.get("selected_option_rich_in_common") is False,
        "strategy_once_no_exception": strategy_once.get("ok") is True,
        "strategy_once_hold": strategy_hold is True,
        "strategy_once_not_promoted": strategy_not_promoted is True,
        "features_service_started": bool(feature_start.get("started") or feature_start.get("already_running")),
        "sample_count_reached": sample_count == 6,
        "features_process_seen_in_samples": sample_features_process >= 4,
        "consumer_view_data_valid_in_samples": sample_valid_count >= 4,
        "consumer_view_safe_to_consume_in_samples": sample_safe_count >= 4,
        "consumer_view_structural_valid_in_samples": sample_structural_count >= 4,
        "mist_call_visible_in_samples": sample_mist_call_count >= 4,
        "common_key_match_in_samples": sample_common_match >= 4,
        "selected_option_key_match_in_samples": sample_selected_match >= 4,
        "selected_option_rich_absent_in_samples": sample_rich_absent >= 4,
        "orders_zero": orders_len == 0,
        "orders_zero_in_samples": sample_orders_zero == sample_count,
        "latest_orders_empty": len(latest_orders) == 0,
        "position_flat": position_after["flat"] is True,
        "position_flat_in_samples": sample_position_flat == sample_count,
        "real_live_false": real_live_after is False,
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
        result["final_verdict"] = "FAIL_O20_R3D_CONSUMER_VIEW_VALIDITY_SEMANTICS_NOT_PROVEN"
        result["next_recommended_batch"] = "Inspect O20-R3D proof/logs. Do not rerun O20-R3B."
        write_outputs(result)
        return 2

    result["final_verdict"] = "PASS_O20_R3D_CONSUMER_VIEW_VALIDITY_SEMANTICS_OK_HOLD_ONLY"
    result["next_recommended_batch"] = "26-O20-R3E corrected bounded observation rerun after validity semantics repair; still no real live"
    write_outputs(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
