from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

CONTROL = Path("run/controls/pshadowgate_v26_regime_gate.env")
STATE_DIR = Path("run/state/regime_direction_v26")
CURRENT = STATE_DIR / "current.json"
BLOCKED_DIR = Path("run/paper_shadow_regime_v26")


def now_ms() -> int:
    return int(time.time() * 1000)


def day() -> str:
    return time.strftime("%Y%m%d")


def parse_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[len("export "):]
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def cfg_bool(c: dict[str, str], k: str, default: bool) -> bool:
    v = c.get(k, os.environ.get(k, str(int(default))))
    return str(v).strip().lower() in {"1", "true", "yes", "on", "y"}


def cfg_int(c: dict[str, str], k: str, default: int) -> int:
    try:
        return int(str(c.get(k, os.environ.get(k, default))).strip())
    except Exception:
        return default


def load_cfg() -> dict[str, Any]:
    c = parse_env(CONTROL)
    return {
        "enabled": cfg_bool(c, "V26_REGIME_GATE_ENABLED", True),
        "require_regime_authority": cfg_bool(c, "V26_REQUIRE_REGIME_AUTHORITY", True),
        "fail_closed_unknown": cfg_bool(c, "V26_FAIL_CLOSED_UNKNOWN", True),
        "max_regime_age_ms": cfg_int(c, "V26_MAX_REGIME_AGE_MS", 300000),
        "allow_countertrend": cfg_bool(c, "V26_ALLOW_COUNTERTREND", False),
        "require_reversal_proof_for_countertrend": cfg_bool(c, "V26_REQUIRE_REVERSAL_PROOF_FOR_COUNTERTREND", True),
        "allow_manual_override": cfg_bool(c, "V26_ALLOW_MANUAL_REGIME_OVERRIDE", False),
        "manual_market_regime": c.get("V26_MANUAL_MARKET_REGIME", "UNKNOWN").strip().upper(),
        "manual_trend_bias": c.get("V26_MANUAL_TREND_BIAS", "NO_TRADE").strip().upper(),
        "range_chop_default_no_trade": cfg_bool(c, "V26_RANGE_CHOP_DEFAULT_NO_TRADE", True),
        "log_blocked_events": cfg_bool(c, "V26_LOG_BLOCKED_EVENTS", True),
    }


def read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def append_ndjson(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def normalize_regime(v: Any) -> str:
    s = str(v or "UNKNOWN").upper().strip()
    aliases = {
        "UP": "UPTREND",
        "BULL": "UPTREND",
        "BULLISH": "UPTREND",
        "LONG": "UPTREND",
        "DOWN": "DOWNTREND",
        "BEAR": "DOWNTREND",
        "BEARISH": "DOWNTREND",
        "SHORT": "DOWNTREND",
        "SIDEWAYS": "RANGE",
        "RANGING": "RANGE",
        "NOISE": "CHOP",
        "UNKNOWN": "UNKNOWN",
        "": "UNKNOWN",
    }
    return aliases.get(s, s)


def derive_bias(regime: str) -> str:
    if regime == "UPTREND":
        return "CALL_ONLY"
    if regime == "DOWNTREND":
        return "PUT_ONLY"
    if regime in {"RANGE", "CHOP", "UNKNOWN"}:
        return "NO_TRADE"
    return "NO_TRADE"


def load_regime_snapshot(cfg: dict[str, Any]) -> dict[str, Any]:
    src = read_json(CURRENT)
    if src:
        src = dict(src)
        src.setdefault("source", "file:run/state/regime_direction_v26/current.json")
        return src

    if cfg["allow_manual_override"]:
        return {
            "schema": "regime_direction_v26.manual_override.v1",
            "source": "manual_override_control_file",
            "market_regime": cfg["manual_market_regime"],
            "trend_bias": cfg["manual_trend_bias"],
            "created_at_ms": now_ms(),
            "manual_override": True,
            "warning": "manual override is audit-only and not live-promotion proof",
        }

    return {
        "schema": "regime_direction_v26.missing.v1",
        "source": "missing",
        "market_regime": "UNKNOWN",
        "trend_bias": "NO_TRADE",
        "created_at_ms": 0,
        "missing": True,
    }


def reversal_confirmed_from_fields(fields: dict[str, Any]) -> bool:
    # Conservative. Defaults false unless an upstream module explicitly proves reversal.
    for k in [
        "reversal_confirmed",
        "countertrend_reversal_confirmed",
        "trend_break_confirmed",
        "vwap_break_confirmed",
    ]:
        v = fields.get(k)
        if str(v).strip().lower() in {"1", "true", "yes", "y"}:
            return True
    return False


def evaluate_direction(action: str, family: str = "", symbol: str = "", score: str = "", source_age_ms: str = "", **extra: Any) -> dict[str, Any]:
    cfg = load_cfg()
    action = str(action or "").upper().strip()
    family = str(family or "").upper().strip()
    symbol = str(symbol or "").upper().strip()

    if not cfg["enabled"]:
        return {
            "allowed": True,
            "reason": "V26_GATE_DISABLED",
            "market_regime": "UNKNOWN",
            "trend_bias": "BOTH_ALLOWED",
            "broker_order": 0,
            "paper_engine_order": 0,
            "risk_started": 0,
            "execution_started": 0,
            "redis_destructive": 0,
        }

    snap = load_regime_snapshot(cfg)
    regime = normalize_regime(snap.get("market_regime"))
    trend_bias = str(snap.get("trend_bias") or derive_bias(regime)).upper().strip()
    created = int(float(snap.get("created_at_ms") or 0))
    age_ms = now_ms() - created if created else 10**12
    stale = age_ms > int(cfg["max_regime_age_ms"])

    base = {
        "schema": "pshadowgate_v26_regime_direction_verdict.v1",
        "checked_at_ms": now_ms(),
        "action": action,
        "family": family,
        "symbol": symbol,
        "score": score,
        "source_age_ms": source_age_ms,
        "market_regime": regime,
        "trend_bias": trend_bias or derive_bias(regime),
        "regime_source": snap.get("source", ""),
        "regime_created_at_ms": created,
        "regime_age_ms": age_ms,
        "regime_snapshot": snap,
        "broker_order": 0,
        "paper_engine_order": 0,
        "risk_started": 0,
        "execution_started": 0,
        "redis_destructive": 0,
    }

    if cfg["require_regime_authority"] and (not created or snap.get("missing")):
        base.update({"allowed": False, "reason": "REGIME_MISSING_FAIL_CLOSED"})
        return base

    if stale:
        base.update({"allowed": False, "reason": "REGIME_STALE_FAIL_CLOSED"})
        return base

    if regime in {"UNKNOWN", ""} and cfg["fail_closed_unknown"]:
        base.update({"allowed": False, "reason": "REGIME_UNKNOWN_FAIL_CLOSED"})
        return base

    if regime in {"RANGE", "CHOP"} and cfg["range_chop_default_no_trade"]:
        base.update({"allowed": False, "reason": "REGIME_RANGE_OR_CHOP_NO_TRADE"})
        return base

    reversal = reversal_confirmed_from_fields(extra)

    if regime == "UPTREND":
        if action == "ENTER_CALL":
            base.update({"allowed": True, "reason": "DIRECTION_ALLOWED_UPTREND_CALL"})
            return base
        if action == "ENTER_PUT":
            if cfg["allow_countertrend"] and reversal:
                base.update({"allowed": True, "reason": "COUNTERTREND_PUT_ALLOWED_WITH_REVERSAL_PROOF"})
                return base
            base.update({"allowed": False, "reason": "DIRECTION_BLOCKED_UPTREND_PUT"})
            return base

    if regime == "DOWNTREND":
        if action == "ENTER_PUT":
            base.update({"allowed": True, "reason": "DIRECTION_ALLOWED_DOWNTREND_PUT"})
            return base
        if action == "ENTER_CALL":
            if cfg["allow_countertrend"] and reversal:
                base.update({"allowed": True, "reason": "COUNTERTREND_CALL_ALLOWED_WITH_REVERSAL_PROOF"})
                return base
            base.update({"allowed": False, "reason": "DIRECTION_BLOCKED_DOWNTREND_CALL"})
            return base

    # Unknown action or unclassified action must fail closed.
    base.update({"allowed": False, "reason": "DIRECTION_UNCLASSIFIED_FAIL_CLOSED"})
    return base


def log_block(verdict: dict[str, Any]) -> None:
    cfg = load_cfg()
    if not cfg.get("log_blocked_events"):
        return
    if verdict.get("allowed"):
        return
    append_ndjson(BLOCKED_DIR / f"blocked_{day()}.ndjson", verdict)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--action", default="")
    ap.add_argument("--family", default="")
    ap.add_argument("--symbol", default="")
    ap.add_argument("--score", default="")
    ap.add_argument("--source-age-ms", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    verdict = evaluate_direction(
        action=args.action,
        family=args.family,
        symbol=args.symbol,
        score=args.score,
        source_age_ms=args.source_age_ms,
    )
    log_block(verdict)

    if args.json:
        print(json.dumps(verdict, sort_keys=True))
        return 0 if verdict.get("allowed") else 3

    print("V26_ALLOWED=" + str(int(bool(verdict.get("allowed")))))
    print("V26_REASON=" + str(verdict.get("reason")))
    print("V26_MARKET_REGIME=" + str(verdict.get("market_regime")))
    print("V26_TREND_BIAS=" + str(verdict.get("trend_bias")))
    print("V26_REGIME_SOURCE=" + str(verdict.get("regime_source")))
    print("V26_REGIME_AGE_MS=" + str(verdict.get("regime_age_ms")))
    print("BROKER_ORDER=0")
    print("PAPER_ENGINE_ORDER=0")
    print("RISK_STARTED=0")
    print("EXECUTION_STARTED=0")
    print("REDIS_DESTRUCTIVE=0")
    return 0 if verdict.get("allowed") else 3


if __name__ == "__main__":
    raise SystemExit(main())
