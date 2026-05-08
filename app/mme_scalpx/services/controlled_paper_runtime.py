from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENABLEMENT_FILE = PROJECT_ROOT / "etc/strategy_family/rollout/controlled_paper_trial_enablement_from_25v25w.yaml"
ENABLEMENT_PROOF = PROJECT_ROOT / "run/proofs/controlled_paper_trial_enablement_from_25v25w.json"
PREP_PROOF = PROJECT_ROOT / "run/proofs/controlled_paper_trial_preparation_from_25v25w.json"
PROVIDER_PROOF = PROJECT_ROOT / "run/proofs/proof_market_session_provider_runtime.json"
POSITION_GUARD = PROJECT_ROOT / "run/proofs/controlled_paper_enablement_position_guard.json"

ENV_FLAG = "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME"
ENV_ACK = "SCALPX_CONTROLLED_PAPER_SCOPE_ACK"
ACK_VALUE = "I_ACCEPT_MIST_CALL_1LOT_PAPER_ONLY"


@dataclass(frozen=True)
class ControlledPaperTruth:
    enabled: bool
    reason: str
    selected_family: str = ""
    selected_side: str = ""
    quantity_lots: int = 0
    real_live_allowed: bool = False
    paper_orders_allowed: bool = False
    automatic_broker_failover_allowed: bool = False
    mid_position_provider_migration_allowed: bool = False
    auto_stop_after_first_paper_order: bool = False
    forced_flatten_active: bool = False
    kill_switch_active: bool = False
    broker_path: str = ""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(_read(path))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _scalar(raw: str) -> Any:
    text = raw.strip().strip('"').strip("'")
    low = text.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(text)
    except Exception:
        return text


def _yaml(path: Path) -> dict[str, Any]:
    text = _read(path)
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#") or ":" not in raw:
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1] if stack else root

        if not value:
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = _scalar(value)

    return root


def _nested(root: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    cur: Any = root
    for key in keys:
        if not isinstance(cur, Mapping):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def _env_ok() -> bool:
    return os.getenv(ENV_FLAG, "") == "1" and os.getenv(ENV_ACK, "") == ACK_VALUE


def _safe_entry_window_ist() -> bool:
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        if now.isoweekday() > 5:
            return False
        hhmm = now.hour * 100 + now.minute
        return 915 <= hhmm <= 1510
    except Exception:
        return False


def controlled_paper_truth(*, ignore_time_gate: bool = False) -> ControlledPaperTruth:
    if not _env_ok():
        return ControlledPaperTruth(False, "explicit env flag and scope ack required")

    if not ignore_time_gate and not _safe_entry_window_ist():
        return ControlledPaperTruth(False, "safe entry window required: weekday 09:15-15:10 IST")

    cfg = _yaml(ENABLEMENT_FILE)
    if not cfg:
        return ControlledPaperTruth(False, "enablement yaml missing or unreadable")

    enablement = _json(ENABLEMENT_PROOF)
    prep = _json(PREP_PROOF)
    provider = _json(PROVIDER_PROOF)
    position = _json(POSITION_GUARD)

    family = str(_nested(cfg, "selection", "selected_family", default="")).upper()
    side = str(_nested(cfg, "selection", "selected_side", default="")).upper()
    qty = int(_nested(cfg, "selection", "quantity_lots", default=0) or 0)

    real_live_allowed = bool(cfg.get("real_live_allowed"))
    paper_enabled = bool(cfg.get("paper_trial_enabled"))
    paper_armed = bool(cfg.get("paper_armed_enabled"))
    broker_path = str(_nested(cfg, "provider_safety", "broker_path", default=""))

    paper_orders = bool(_nested(cfg, "order_safety", "paper_orders_allowed", default=False))
    real_orders = bool(_nested(cfg, "order_safety", "real_orders_allowed", default=True))
    auto_failover = bool(_nested(cfg, "provider_safety", "automatic_broker_failover_allowed", default=True))
    mid_migration = bool(_nested(cfg, "provider_safety", "mid_position_provider_migration_allowed", default=True))
    stop_after_first = bool(_nested(cfg, "order_safety", "auto_stop_after_first_paper_order", default=False))
    forced_flatten = bool(_nested(cfg, "risk_safety", "forced_flatten_active", default=False))
    kill_switch = bool(_nested(cfg, "risk_safety", "kill_switch_active", default=False))

    checks = {
        "paper_enabled": paper_enabled is True,
        "paper_armed": paper_armed is True,
        "real_live_false": real_live_allowed is False,
        "real_orders_false": real_orders is False,
        "family_mist": family == "MIST",
        "side_call": side == "CALL",
        "qty_one": qty == 1,
        "paper_path": broker_path == "PAPER_OR_SANDBOX_ONLY",
        "paper_orders": paper_orders is True,
        "no_auto_failover": auto_failover is False,
        "no_mid_migration": mid_migration is False,
        "stop_after_first": stop_after_first is True,
        "forced_flatten": forced_flatten is True,
        "kill_switch": kill_switch is True,
        "enablement_proof": enablement.get("controlled_paper_trial_enablement_from_25v25w_ok") is True,
        "enablement_real_live_false": enablement.get("real_live_allowed") is False,
        "prep_proof": prep.get("controlled_paper_trial_preparation_from_25v25w_ok") is True,
        "provider_proof": provider.get("market_session_provider_runtime_ok") is True,
        "position_flat_proof": position.get("no_open_position_ok") is True,
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        return ControlledPaperTruth(
            False,
            "checks failed: " + ",".join(failed),
            family,
            side,
            qty,
            real_live_allowed,
            paper_orders,
            auto_failover,
            mid_migration,
            stop_after_first,
            forced_flatten,
            kill_switch,
            broker_path,
        )

    return ControlledPaperTruth(
        True,
        "MIST CALL 1-lot controlled paper runtime enabled",
        family,
        side,
        qty,
        False,
        True,
        False,
        False,
        True,
        True,
        True,
        broker_path,
    )


def controlled_strategy_promotion_enabled() -> bool:
    return controlled_paper_truth(ignore_time_gate=False).enabled


def controlled_order_intent_adapter_enabled() -> bool:
    return controlled_paper_truth(ignore_time_gate=False).enabled


def controlled_runtime_report(*, ignore_time_gate: bool = False) -> dict[str, Any]:
    t = controlled_paper_truth(ignore_time_gate=ignore_time_gate)
    return {
        "enabled": t.enabled,
        "reason": t.reason,
        "selected_family": t.selected_family,
        "selected_side": t.selected_side,
        "quantity_lots": t.quantity_lots,
        "real_live_allowed": t.real_live_allowed,
        "paper_orders_allowed": t.paper_orders_allowed,
        "automatic_broker_failover_allowed": t.automatic_broker_failover_allowed,
        "mid_position_provider_migration_allowed": t.mid_position_provider_migration_allowed,
        "auto_stop_after_first_paper_order": t.auto_stop_after_first_paper_order,
        "forced_flatten_active": t.forced_flatten_active,
        "kill_switch_active": t.kill_switch_active,
        "broker_path": t.broker_path,
    }

# BEGIN BATCH26B_CONTROLLED_EXECUTION_ENTRY_ARMING_CONTRACT
def controlled_execution_entry_allowed() -> bool:
    """
    Fail-closed execution-entry arming contract.

    Current safety state:
    - observe_only / HOLD-report-only remains default
    - paper_armed is blocked
    - real live trading is blocked

    This function intentionally returns False in Batch 26B.
    Any future change to True requires a separate explicit proof batch.
    """
    return False
# END BATCH26B_CONTROLLED_EXECUTION_ENTRY_ARMING_CONTRACT

