#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
RISK = ROOT / "app/mme_scalpx/services/risk.py"
PATCH_STEP = ROOT / "run/proofs/proof_risk_controlled_paper_veto_patch_step.json"

HELPER_BEGIN = "# BEGIN BATCH26C_RISK_CONTROLLED_PAPER_VETO"
HELPER_END = "# END BATCH26C_RISK_CONTROLLED_PAPER_VETO"

REQUIRED_REASONS = [
    "CONTROLLED_PAPER_NOT_ARMED",
    "CONTROLLED_PAPER_SCOPE_MISMATCH",
    "CONTROLLED_PAPER_QTY_CAP_FAIL",
    "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN",
    "CONTROLLED_PAPER_TIME_GATE_FAIL",
    "CONTROLLED_PAPER_POSITION_NOT_FLAT",
]

RELATED_FILES = [
    "app/mme_scalpx/services/risk.py",
    "app/mme_scalpx/services/execution.py",
    "app/mme_scalpx/services/strategy.py",
    "app/mme_scalpx/services/controlled_paper_runtime.py",
    "app/mme_scalpx/services/strategy_family/order_intent.py",
    "app/mme_scalpx/core/names.py",
    "app/mme_scalpx/core/settings.py",
    "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml",
    "etc/strategy_family/rollout/controlled_paper_trial_scope_from_25v25w.yaml",
    "etc/strategy_family/rollout/paper_armed_readiness_gate.yaml",
]

HELPER = r'''
# BEGIN BATCH26C_RISK_CONTROLLED_PAPER_VETO

BATCH26C_CONTROLLED_PAPER_NOT_ARMED = "CONTROLLED_PAPER_NOT_ARMED"
BATCH26C_CONTROLLED_PAPER_SCOPE_MISMATCH = "CONTROLLED_PAPER_SCOPE_MISMATCH"
BATCH26C_CONTROLLED_PAPER_QTY_CAP_FAIL = "CONTROLLED_PAPER_QTY_CAP_FAIL"
BATCH26C_CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN = "CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN"
BATCH26C_CONTROLLED_PAPER_TIME_GATE_FAIL = "CONTROLLED_PAPER_TIME_GATE_FAIL"
BATCH26C_CONTROLLED_PAPER_POSITION_NOT_FLAT = "CONTROLLED_PAPER_POSITION_NOT_FLAT"


def _batch26c_truthy(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {
        "1", "true", "yes", "y", "on", "enabled", "allow", "allowed", "pass", "passed", "ok"
    }


def _batch26c_falsey(value):
    if isinstance(value, bool):
        return value is False
    if value is None:
        return False
    return str(value).strip().lower() in {
        "0", "false", "no", "n", "off", "disabled", "deny", "denied", "blocked", "fail", "failed"
    }


def _batch26c_numeric(value):
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except Exception:
        return None


def _batch26c_project_root():
    import pathlib
    return pathlib.Path(__file__).resolve().parents[3]


def _batch26c_getattr(obj, names, default=None):
    if isinstance(names, str):
        names = [names]
    if obj is None:
        return default
    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj.get(name)
        return default
    for name in names:
        try:
            if hasattr(obj, name):
                return getattr(obj, name)
        except Exception:
            pass
    return default


def _batch26c_load_yaml_like(path):
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return loaded if isinstance(loaded, dict) else {}
    except Exception:
        data = {}
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            low = value.lower()
            if low in {"true", "false"}:
                data[key] = low == "true"
            else:
                data[key] = value
        return data


def _batch26c_flatten_values(obj):
    out = {}

    def walk(prefix, value, depth):
        if depth > 8:
            return
        if isinstance(value, dict):
            for key, child in value.items():
                next_key = f"{prefix}.{key}" if prefix else str(key)
                out[next_key] = child
                walk(next_key, child, depth + 1)

    walk("", obj, 0)
    return out


def _batch26c_find_flat(flat, names):
    names = set(names)
    for key, value in flat.items():
        if key.split(".")[-1] in names:
            return value
    return None


def _batch26c_controlled_config(self):
    override = _batch26c_getattr(self, "_batch26c_controlled_paper_config_override")
    if isinstance(override, dict):
        return override

    root = _batch26c_project_root()
    path = root / "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml"
    return _batch26c_load_yaml_like(path)


def _batch26c_position_hash_key():
    try:
        from app.mme_scalpx.core import names as N
    except Exception:
        return None

    for attr in (
        "HASH_STATE_POSITION_MME",
        "HASH_POSITION_MME",
        "KEY_STATE_POSITION_MME",
        "STATE_POSITION_MME",
    ):
        value = getattr(N, attr, None)
        if value:
            return str(value)
    return None


def _batch26c_redis_position_flat(self):
    redis_client = _batch26c_getattr(self, "redis")
    if redis_client is None:
        return None

    key = _batch26c_position_hash_key()
    if not key:
        return None

    try:
        raw = redis_client.hgetall(key)
    except Exception:
        return None

    if not raw:
        return True

    decoded = {}
    try:
        for k, v in dict(raw).items():
            kk = k.decode() if isinstance(k, bytes) else str(k)
            vv = v.decode() if isinstance(v, bytes) else str(v)
            decoded[kk] = vv
    except Exception:
        return None

    has_position = decoded.get("has_position") or decoded.get("position_open") or decoded.get("open")
    qty = decoded.get("qty_lots") or decoded.get("quantity") or decoded.get("qty") or "0"
    qty_num = _batch26c_numeric(qty)

    if _batch26c_falsey(has_position):
        return True
    if qty_num == 0:
        return True
    return False


def _batch26c_position_flat(self):
    redis_flat = _batch26c_redis_position_flat(self)
    if redis_flat is not None:
        return redis_flat

    runtime = _batch26c_getattr(self, "runtime")
    position_open = _batch26c_getattr(runtime, "position_open")
    if position_open is not None:
        return not _batch26c_truthy(position_open)

    has_position = _batch26c_getattr(runtime, "has_position")
    if has_position is not None:
        return not _batch26c_truthy(has_position)

    qty = _batch26c_getattr(runtime, ("qty_lots", "quantity", "qty"))
    qty_num = _batch26c_numeric(qty)
    if qty_num is not None:
        return qty_num == 0

    return None


def _batch26c_time_gate_ok(self, now_ns):
    override = _batch26c_getattr(self, "_batch26c_time_gate_override")
    if override is not None:
        return bool(override)

    from datetime import datetime, timedelta, timezone

    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.fromtimestamp(now_ns / 1_000_000_000, tz=ist) if now_ns else datetime.now(tz=ist)

    if now.weekday() >= 5:
        return False

    hhmm = now.hour * 100 + now.minute
    return 915 <= hhmm <= 1510


def _batch26c_controlled_paper_veto_reason(self, now_ns):
    """
    Return (reason, details). A None reason means no Batch 26C controlled-paper
    veto was found. This is ENTRY-veto only; exits remain allowed.
    """
    import os

    cfg = _batch26c_controlled_config(self)
    flat = _batch26c_flatten_values(cfg)

    env_enabled = os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME") == "1"
    env_ack = os.environ.get("SCALPX_CONTROLLED_PAPER_SCOPE_ACK") == "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"

    enabled = _batch26c_find_flat(flat, {"controlled_paper_trial_enabled", "paper_armed_enabled", "enabled"})
    real_live_allowed = _batch26c_find_flat(flat, {"real_live_allowed", "live_allowed", "allow_live_orders"})
    family = _batch26c_find_flat(flat, {"selected_family", "family"})
    side = _batch26c_find_flat(flat, {"selected_side", "side"})
    qty = _batch26c_find_flat(flat, {"quantity_lots", "qty_lots", "quantity", "qty"})

    details = {
        "batch26c": "risk_controlled_paper_entry_veto",
        "config_present": bool(cfg),
        "env_enabled": env_enabled,
        "env_ack": env_ack,
        "enabled": enabled,
        "real_live_allowed": real_live_allowed,
        "selected_family": family,
        "selected_side": side,
        "qty": qty,
        "paper_armed_approved_by_patch": False,
        "real_live_approved_by_patch": False,
    }

    if real_live_allowed is not None and not _batch26c_falsey(real_live_allowed):
        return BATCH26C_CONTROLLED_PAPER_REAL_LIVE_FORBIDDEN, details

    if not env_enabled or not env_ack or not _batch26c_truthy(enabled):
        return BATCH26C_CONTROLLED_PAPER_NOT_ARMED, details

    if str(family or "").strip().upper() != "MIST" or str(side or "").strip().upper() != "CALL":
        return BATCH26C_CONTROLLED_PAPER_SCOPE_MISMATCH, details

    if _batch26c_numeric(qty) != 1:
        return BATCH26C_CONTROLLED_PAPER_QTY_CAP_FAIL, details

    position_flat = _batch26c_position_flat(self)
    details["position_flat"] = position_flat
    if position_flat is not True:
        return BATCH26C_CONTROLLED_PAPER_POSITION_NOT_FLAT, details

    time_gate_ok = _batch26c_time_gate_ok(self, now_ns)
    details["time_gate_ok"] = time_gate_ok
    if time_gate_ok is not True:
        return BATCH26C_CONTROLLED_PAPER_TIME_GATE_FAIL, details

    return None, details


_BATCH26C_PREVIOUS_RECOMPUTE_VETO = RiskService._recompute_veto


def _batch26c_recompute_veto(self, now_ns: int) -> None:
    reason, details = _batch26c_controlled_paper_veto_reason(self, now_ns)
    if reason:
        self.runtime.veto_entries = True
        self.runtime.veto_reason = reason
        try:
            import json
            self.runtime.batch26c_controlled_paper_veto_detail = json.dumps(details, sort_keys=True, default=str)
        except Exception:
            try:
                self.runtime.batch26c_controlled_paper_veto_detail = str(details)
            except Exception:
                pass
        return

    _BATCH26C_PREVIOUS_RECOMPUTE_VETO(self, now_ns)

    try:
        import json
        self.runtime.batch26c_controlled_paper_veto_detail = json.dumps(details, sort_keys=True, default=str)
    except Exception:
        try:
            self.runtime.batch26c_controlled_paper_veto_detail = str(details)
        except Exception:
            pass


RiskService._recompute_veto = _batch26c_recompute_veto


_BATCH26C_PREVIOUS_BUILD_SNAPSHOT = RiskService._build_snapshot


def _batch26c_build_snapshot(self, now_ns: int) -> dict[str, str]:
    snapshot = _BATCH26C_PREVIOUS_BUILD_SNAPSHOT(self, now_ns)

    snapshot["allow_exits"] = "1"
    snapshot["risk_blocks_entries_only"] = "1"

    reason = str(getattr(self.runtime, "veto_reason", "") or "")
    if reason.startswith("CONTROLLED_PAPER_"):
        snapshot["controlled_paper_entry_veto"] = "1"
        snapshot["controlled_paper_veto_reason"] = reason
    else:
        snapshot["controlled_paper_entry_veto"] = "0"
        snapshot["controlled_paper_veto_reason"] = ""

    snapshot["controlled_paper_veto_detail"] = str(
        getattr(self.runtime, "batch26c_controlled_paper_veto_detail", "")
    )
    return snapshot


RiskService._build_snapshot = _batch26c_build_snapshot

# END BATCH26C_RISK_CONTROLLED_PAPER_VETO
'''


def sha(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def inspect_file(path: str) -> dict[str, Any]:
    p = ROOT / path
    text = read(p) if p.exists() and p.is_file() else ""
    return {
        "path": path,
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
        "size_bytes": p.stat().st_size if p.exists() and p.is_file() else None,
        "line_count": len(text.splitlines()) if text else 0,
        "sha256": sha(p),
        "has_recompute_veto": "_recompute_veto" in text,
        "has_build_snapshot": "_build_snapshot" in text,
        "has_veto_entries": "veto_entries" in text,
        "has_allow_exits": "allow_exits" in text,
        "has_batch26c": "BATCH26C_RISK_CONTROLLED_PAPER_VETO" in text,
    }


def grep(path: str, pattern: str, max_hits: int = 120) -> list[dict[str, Any]]:
    p = ROOT / path
    if not p.exists():
        return []
    rx = re.compile(pattern, re.IGNORECASE)
    out = []
    for lineno, line in enumerate(read(p).splitlines(), 1):
        if rx.search(line):
            out.append({"line": lineno, "text": line.rstrip()[:260]})
            if len(out) >= max_hits:
                break
    return out


def main() -> int:
    if not RISK.exists():
        raise SystemExit("risk.py missing; refusing patch")

    before = read(RISK)

    required_existing = {
        "RiskService_class": "class RiskService" in before,
        "recompute_veto": "_recompute_veto" in before,
        "build_snapshot": "_build_snapshot" in before,
        "veto_entries": "veto_entries" in before,
        "allow_exits": "allow_exits" in before,
    }
    missing = [k for k, ok in required_existing.items() if not ok]
    if missing:
        raise SystemExit("risk.py missing required surfaces; refusing blind patch: " + ", ".join(missing))

    pre_inspection = {path: inspect_file(path) for path in RELATED_FILES}

    if HELPER_BEGIN in before:
        patched = before
        inserted = False
    else:
        patched = before.rstrip() + "\n\n" + HELPER + "\n"
        inserted = True

    write(RISK, patched)
    after = read(RISK)

    required_tokens = REQUIRED_REASONS + [
        "RiskService._recompute_veto = _batch26c_recompute_veto",
        "RiskService._build_snapshot = _batch26c_build_snapshot",
        'snapshot["allow_exits"] = "1"',
        'snapshot["risk_blocks_entries_only"] = "1"',
        "_batch26c_position_hash_key",
    ]
    missing_tokens = [x for x in required_tokens if x not in after]

    post_inspection = {path: inspect_file(path) for path in RELATED_FILES}

    report = {
        "batch": "26C_risk_controlled_paper_veto_patch_step",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": "app/mme_scalpx/services/risk.py",
        "source_code_patched": inserted,
        "idempotent_existing_patch_detected": not inserted,
        "paper_armed_enabled": False,
        "real_live_enabled": False,
        "services_started": False,
        "redis_writes": False,
        "pre_inspection": pre_inspection,
        "post_inspection": post_inspection,
        "required_existing_surface": required_existing,
        "missing_tokens_after_patch": missing_tokens,
        "risk_controlled_paper_lines": grep("app/mme_scalpx/services/risk.py", r"CONTROLLED_PAPER|controlled_paper|real_live_allowed|paper_armed", 240),
        "risk_allow_exits_lines": grep("app/mme_scalpx/services/risk.py", r"allow_exits|risk_blocks_entries_only", 120),
        "verdict": {
            "patch_step_ok": len(missing_tokens) == 0,
            "risk_blocks_entries_only_preserved": 'snapshot["allow_exits"] = "1"' in after,
            "paper_armed_approved": False,
            "real_live_approved": False,
        },
    }

    PATCH_STEP.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["verdict"], indent=2, sort_keys=True))
    return 0 if len(missing_tokens) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
