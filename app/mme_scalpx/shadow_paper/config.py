from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


CONTROL_FILE = Path("run/controls/pshadowgate_lifecycle.env")


def _parse_env_file(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def _get_bool(data: dict[str, str], key: str, default: bool) -> bool:
    value = data.get(key, os.environ.get(key, str(int(default))))
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(data: dict[str, str], key: str, default: int) -> int:
    try:
        return int(str(data.get(key, os.environ.get(key, default))).strip())
    except Exception:
        return default


def _get_float(data: dict[str, str], key: str, default: float) -> float:
    try:
        return float(str(data.get(key, os.environ.get(key, default))).strip())
    except Exception:
        return default


@dataclass(frozen=True)
class LifecycleConfig:
    enabled: bool
    max_daily_trades: int
    one_open_position_only: bool
    entry_event_max_age_ms: int
    ltp_max_age_ms: int
    synthetic_sl_points: float
    synthetic_tp_points: float
    max_holding_time_ms: int
    assumed_slippage_points: float
    lot_size: int
    min_entry_price: float
    max_entry_price: float

    state_dir: Path = Path("run/state/pshadowgate_lifecycle")
    shadow_event_dir: Path = Path("run/paper_shadow")
    ledger_dir: Path = Path("run/paper_shadow_lifecycle")


def load_config() -> LifecycleConfig:
    data = _parse_env_file(CONTROL_FILE)
    return LifecycleConfig(
        enabled=_get_bool(data, "SHADOW_LIFECYCLE_ENABLED", True),
        max_daily_trades=_get_int(data, "MAX_DAILY_TRADES", 3),
        one_open_position_only=_get_bool(data, "ONE_OPEN_POSITION_ONLY", True),
        entry_event_max_age_ms=_get_int(data, "ENTRY_EVENT_MAX_AGE_MS", 900000),
        ltp_max_age_ms=_get_int(data, "LTP_MAX_AGE_MS", 30000),
        synthetic_sl_points=_get_float(data, "SYNTHETIC_SL_POINTS", 15.0),
        synthetic_tp_points=_get_float(data, "SYNTHETIC_TP_POINTS", 45.0),
        max_holding_time_ms=_get_int(data, "MAX_HOLDING_TIME_MS", 300000),
        assumed_slippage_points=_get_float(data, "ASSUMED_SLIPPAGE_POINTS", 0.5),
        lot_size=_get_int(data, "LOT_SIZE", 65),
        min_entry_price=_get_float(data, "MIN_ENTRY_PRICE", 1.0),
        max_entry_price=_get_float(data, "MAX_ENTRY_PRICE", 1000.0),
    )
