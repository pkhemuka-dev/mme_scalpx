from __future__ import annotations

"""
app/mme_scalpx/services/features.py

ScalpX MME - deterministic feature service for the locked CALL / PUT doctrine.

Ownership
---------
This module owns:
- reconstruction of the latest synchronized snapshot from canonical snapshot hashes
- rolling futures / option history buffers for the active five-leg universe
- deterministic locked-spec feature computation
- futures-only regime filter computation
- economics computation for ATM / ATM+1 CALL and PUT legs
- additive publication to the canonical frozen names surface
- feature-service heartbeat publication
- runtime entrypoint `run(context)`

This module does NOT own:
- instrument discovery / strike selection outside the active universe
- strategy decision generation
- risk truth / execution truth / position truth
- Redis helper implementation
- runtime composition root

Freeze rule
-----------
names.py proves SERVICE_FEATURES owns KEY_HEALTH_FEATURES only.
It does NOT own any lock. Therefore this service must not acquire KEY_LOCK_FEEDS
or any other singleton lock.

Spec-critical corrections
-------------------------
This rewrite fixes the fatal deviations identified in the reviews:
- velocity = (ltp_now - ltp_t-3) / dt_seconds
- velocity_ratio = |velocity| / EMA(|velocity|)
- futures spread_ratio = spread / EMA(spread)
- option spread_ratio = spread / EMA(spread)
- nof_slope_5 = nof_now - nof_t-5
- option delta_3 = ltp_now - ltp_t-3
- ladder acceleration uses t-1 / t-2 bid/ask ladder logic
- regime filter uses the locked futures-only conditions
"""

import contextlib
import json
import logging
import math
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Final, Mapping

from app.mme_scalpx.core import names as N
from app.mme_scalpx.core import redisx as RX
from app.mme_scalpx.core.settings import AppSettings, get_settings

LOGGER = logging.getLogger("app.mme_scalpx.services.features")


# =============================================================================
# Required surface validation
# =============================================================================

_REQUIRED_NAME_EXPORTS: Final[tuple[str, ...]] = (
    "SERVICE_FEATURES",
    "STREAM_FEATURES_MME",
    "STREAM_SYSTEM_HEALTH",
    "STREAM_SYSTEM_ERRORS",
    "HASH_STATE_SNAPSHOT_MME_FUT",
    "HASH_STATE_SNAPSHOT_MME_OPT_SELECTED",
    "HASH_STATE_FEATURES_MME_FUT",
    "HASH_STATE_OPTION_CONFIRM",
    "HASH_STATE_BASELINES_MME_FUT",
    "KEY_HEALTH_FEATURES",
    "HEALTH_STATUS_OK",
    "HEALTH_STATUS_WARN",
    "HEALTH_STATUS_ERROR",
)


def _validate_name_surface_or_die() -> None:
    missing = [name for name in _REQUIRED_NAME_EXPORTS if not hasattr(N, name)]
    if missing:
        raise RuntimeError(
            "features.py missing required names.py exports: "
            + ", ".join(sorted(missing))
        )


# =============================================================================
# Locked constants
# =============================================================================

EPSILON: Final[float] = 1e-8
PREMIUM_FLOOR: Final[float] = 40.0
TARGET_PCT: Final[float] = 0.12
STOP_PCT: Final[float] = 0.07
MIN_TARGET: Final[float] = 5.0
MAX_TARGET: Final[float] = 10.0
MIN_STOP: Final[float] = 3.0
MAX_STOP: Final[float] = 7.0

OPT_SPREAD_MAX: Final[float] = 1.5
FUT_SPREAD_MAX: Final[float] = 1.5
FUT_DEPTH_MIN: Final[int] = 500
OPT_DEPTH_MIN: Final[int] = 100
FEED_STALE_MS: Final[int] = 1000
SYNC_WINDOW_MS: Final[int] = 200
DELTA_MIN: Final[float] = 0.35

EMA_PERIOD: Final[int] = 20
EMA_ALPHA: Final[float] = 2.0 / (EMA_PERIOD + 1.0)
HISTORY_BUFFER_SIZE: Final[int] = 10
WARMUP_MIN_VALID_SNAPSHOTS: Final[int] = 6
REGIME_MIN_HISTORY: Final[int] = 10
VELOCITY_REGIME_MIN: Final[float] = 1.5
SPREAD_REGIME_MAX: Final[float] = 1.5
NOF_FLIP_MAX_10: Final[int] = 3

DEFAULT_HEALTH_STREAM_MAXLEN: Final[int] = 10_000
DEFAULT_ERROR_STREAM_MAXLEN: Final[int] = 10_000
NO_FRAME_WARN_AFTER_LOOPS: Final[int] = 20


# =============================================================================
# Utility helpers
# =============================================================================


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False, default=str)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except Exception:
        return default
    if math.isnan(out) or math.isinf(out):
        return default
    return out


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def _safe_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "ok", "on"}
    return bool(value)


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    out = str(value).strip()
    return out if out else default


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _sign_eps(value: float) -> int:
    if value > EPSILON:
        return 1
    if value < -EPSILON:
        return -1
    return 0


def _to_float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    out = _safe_float(value, math.nan)
    if math.isnan(out) or math.isinf(out):
        return None
    return out


# =============================================================================
# Internal runtime contracts
# =============================================================================


@dataclass(slots=True, frozen=True)
class SnapshotMemberView:
    role: str
    instrument_token: str
    trading_symbol: str
    ts_event_ns: int
    ltp: float
    best_bid: float
    best_ask: float
    bid_qty_5: int
    ask_qty_5: int
    spread: float
    spread_ticks: float
    age_ms: int
    tick_size: float
    lot_size: int | None
    strike: float | None
    validity: str

    @property
    def depth_total(self) -> int:
        return int(self.bid_qty_5 + self.ask_qty_5)

    @property
    def valid_tick(self) -> bool:
        validity = str(self.validity).upper()
        return validity.endswith("OK") or validity == "OK"

    @property
    def fresh(self) -> bool:
        return self.age_ms <= FEED_STALE_MS


@dataclass(slots=True, frozen=True)
class SnapshotFrameView:
    frame_id: str
    selection_version: str
    ts_frame_ns: int
    validity: str
    validity_reason: str
    sync_ok: bool
    ts_span_ms: int
    stale_mask: tuple[str, ...]
    future: SnapshotMemberView | None
    ce_atm: SnapshotMemberView | None
    ce_atm1: SnapshotMemberView | None
    pe_atm: SnapshotMemberView | None
    pe_atm1: SnapshotMemberView | None

    @property
    def frame_valid(self) -> bool:
        validity = str(self.validity).upper()
        return validity.endswith("OK") or validity == "OK"

    @property
    def sync_valid(self) -> bool:
        return bool(self.sync_ok) and self.ts_span_ms <= SYNC_WINDOW_MS


@dataclass(slots=True, frozen=True)
class RollingPoint:
    instrument_token: str
    trading_symbol: str
    ts_ns: int
    ltp: float
    best_bid: float
    best_ask: float
    bid_qty_5: int
    ask_qty_5: int
    spread: float
    depth_total: int
    tick_size: float
    strike: float | None


@dataclass(slots=True)
class EmaState:
    value: float | None = None

    def update(self, observed: float) -> float:
        if self.value is None:
            self.value = observed
        else:
            self.value = (observed * EMA_ALPHA) + (self.value * (1.0 - EMA_ALPHA))
        return self.value


@dataclass(slots=True)
class LegHistory:
    role: str
    points: Deque[RollingPoint] = field(
        default_factory=lambda: deque(maxlen=HISTORY_BUFFER_SIZE)
    )
    spread_ema: EmaState = field(default_factory=EmaState)

    def append(self, point: RollingPoint) -> None:
        self.points.append(point)
        self.spread_ema.update(max(point.spread, EPSILON))

    def count(self) -> int:
        return len(self.points)

    def latest(self) -> RollingPoint | None:
        return self.points[-1] if self.points else None

    def back(self, k: int) -> RollingPoint | None:
        if k <= 0 or len(self.points) < k:
            return None
        return self.points[-k]

    def nof_series(self) -> list[float]:
        return [float(p.bid_qty_5 - p.ask_qty_5) for p in self.points]


@dataclass(slots=True)
class FuturesBaselines:
    abs_velocity_ema: EmaState = field(default_factory=EmaState)


# =============================================================================
# Snapshot reader
# =============================================================================


class SnapshotReader:
    def __init__(self, redis_client: Any) -> None:
        self.redis = redis_client

    def read(self) -> SnapshotFrameView | None:
        fut_hash = RX.hgetall(N.HASH_STATE_SNAPSHOT_MME_FUT, client=self.redis)
        opt_hash = RX.hgetall(N.HASH_STATE_SNAPSHOT_MME_OPT_SELECTED, client=self.redis)
        if not fut_hash or not opt_hash:
            return None

        future = self._decode_member_json(fut_hash.get("future_json"), role="FUTURES")
        ce_atm = self._decode_member_json(opt_hash.get("ce_atm_json"), role="CE_ATM")
        ce_atm1 = self._decode_member_json(opt_hash.get("ce_atm1_json"), role="CE_ATM1")
        pe_atm = self._decode_member_json(opt_hash.get("pe_atm_json"), role="PE_ATM")
        pe_atm1 = self._decode_member_json(opt_hash.get("pe_atm1_json"), role="PE_ATM1")

        stale_mask_raw = _safe_str(opt_hash.get("stale_mask_json")) or _safe_str(
            fut_hash.get("stale_mask_json")
        )
        stale_mask: tuple[str, ...] = tuple()
        if stale_mask_raw:
            with contextlib.suppress(Exception):
                decoded = json.loads(stale_mask_raw)
                if isinstance(decoded, list):
                    stale_mask = tuple(
                        _safe_str(item) for item in decoded if _safe_str(item)
                    )

        return SnapshotFrameView(
            frame_id=_safe_str(
                opt_hash.get("frame_id") or fut_hash.get("frame_id") or "snapshot-frame"
            ),
            selection_version=_safe_str(
                opt_hash.get("selection_version") or fut_hash.get("selection_version")
            ),
            ts_frame_ns=_safe_int(
                opt_hash.get("ts_frame_ns") or fut_hash.get("ts_frame_ns"),
                0,
            ),
            validity=_safe_str(
                opt_hash.get("validity") or fut_hash.get("validity") or "UNKNOWN"
            ),
            validity_reason=_safe_str(
                opt_hash.get("validity_reason") or fut_hash.get("validity_reason")
            ),
            sync_ok=_safe_bool(opt_hash.get("sync_ok") or fut_hash.get("sync_ok")),
            ts_span_ms=_safe_int(
                opt_hash.get("ts_span_ms") or fut_hash.get("ts_span_ms"),
                0,
            ),
            stale_mask=stale_mask,
            future=future,
            ce_atm=ce_atm,
            ce_atm1=ce_atm1,
            pe_atm=pe_atm,
            pe_atm1=pe_atm1,
        )

    def _decode_member_json(self, raw: Any, *, role: str) -> SnapshotMemberView | None:
        if not raw:
            return None
        with contextlib.suppress(Exception):
            data = json.loads(raw)
            if isinstance(data, Mapping):
                return SnapshotMemberView(
                    role=role,
                    instrument_token=_safe_str(
                        data.get("instrument_token") or data.get("token")
                    ),
                    trading_symbol=_safe_str(
                        data.get("trading_symbol") or data.get("symbol")
                    ),
                    ts_event_ns=_safe_int(
                        data.get("local_ts_ns") or data.get("ts_event_ns"),
                        0,
                    ),
                    ltp=_safe_float(data.get("ltp"), 0.0),
                    best_bid=_safe_float(data.get("best_bid"), 0.0),
                    best_ask=_safe_float(data.get("best_ask"), 0.0),
                    bid_qty_5=_safe_int(data.get("bid_qty_5"), 0),
                    ask_qty_5=_safe_int(data.get("ask_qty_5"), 0),
                    spread=_safe_float(data.get("spread"), 0.0),
                    spread_ticks=_safe_float(data.get("spread_ticks"), 0.0),
                    age_ms=_safe_int(data.get("age_ms"), 0),
                    tick_size=_safe_float(data.get("tick_size"), 0.0),
                    lot_size=_safe_int(data.get("lot_size"), 0) or None,
                    strike=_to_float_or_none(data.get("strike")),
                    validity=_safe_str(data.get("validity"), "UNKNOWN"),
                )
        return None


# =============================================================================
# Feature engine
# =============================================================================


class FeatureEngine:
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.log = logger or LOGGER.getChild("FeatureEngine")
        self.legs: dict[str, LegHistory] = {
            "FUTURES": LegHistory("FUTURES"),
            "CE_ATM": LegHistory("CE_ATM"),
            "CE_ATM1": LegHistory("CE_ATM1"),
            "PE_ATM": LegHistory("PE_ATM"),
            "PE_ATM1": LegHistory("PE_ATM1"),
        }
        self.fut_baselines = FuturesBaselines()

    def build_payload(self, frame: SnapshotFrameView, *, now_ns: int) -> dict[str, Any]:
        self._append_member("FUTURES", frame.future)
        self._append_member("CE_ATM", frame.ce_atm)
        self._append_member("CE_ATM1", frame.ce_atm1)
        self._append_member("PE_ATM", frame.pe_atm)
        self._append_member("PE_ATM1", frame.pe_atm1)

        futures_payload = self._compute_futures_features(
            frame=frame,
            member=frame.future,
            now_ns=now_ns,
        )
        ce_atm_payload = self._compute_option_features(
            frame=frame,
            role="CE_ATM",
            member=frame.ce_atm,
        )
        ce_atm1_payload = self._compute_option_features(
            frame=frame,
            role="CE_ATM1",
            member=frame.ce_atm1,
        )
        pe_atm_payload = self._compute_option_features(
            frame=frame,
            role="PE_ATM",
            member=frame.pe_atm,
        )
        pe_atm1_payload = self._compute_option_features(
            frame=frame,
            role="PE_ATM1",
            member=frame.pe_atm1,
        )

        ce_atm_econ = self._compute_option_economics(ce_atm_payload)
        ce_atm1_econ = self._compute_option_economics(ce_atm1_payload)
        pe_atm_econ = self._compute_option_economics(pe_atm_payload)
        pe_atm1_econ = self._compute_option_economics(pe_atm1_payload)

        warmup_complete = self._warmup_complete()
        readiness = {
            "frame_valid": frame.frame_valid,
            "frame_reason": frame.validity_reason,
            "warmup_complete": warmup_complete,
            "futures_ready": futures_payload.get("ready", False),
            "options_ready": all(
                self._leg_ready(x)
                for x in (
                    ce_atm_payload,
                    ce_atm1_payload,
                    pe_atm_payload,
                    pe_atm1_payload,
                )
            ),
            "economics_ready": any(
                bool(x.get("economics_valid", False))
                for x in (ce_atm_econ, ce_atm1_econ, pe_atm_econ, pe_atm1_econ)
            ),
            "sync_valid": frame.sync_valid,
        }

        return {
            "frame_id": frame.frame_id,
            "selection_version": frame.selection_version,
            "frame_ts_ns": frame.ts_frame_ns,
            "futures": futures_payload,
            "ce_atm": ce_atm_payload,
            "ce_atm1": ce_atm1_payload,
            "pe_atm": pe_atm_payload,
            "pe_atm1": pe_atm1_payload,
            "ce_atm_econ": ce_atm_econ,
            "ce_atm1_econ": ce_atm1_econ,
            "pe_atm_econ": pe_atm_econ,
            "pe_atm1_econ": pe_atm1_econ,
            "readiness": readiness,
            "raw_futures": self._raw_latest_dict("FUTURES"),
            "raw_ce_atm": self._raw_latest_dict("CE_ATM"),
            "raw_ce_atm1": self._raw_latest_dict("CE_ATM1"),
            "raw_pe_atm": self._raw_latest_dict("PE_ATM"),
            "raw_pe_atm1": self._raw_latest_dict("PE_ATM1"),
        }

    @staticmethod
    def _leg_ready(raw: Mapping[str, Any]) -> bool:
        return (
            bool(raw)
            and _safe_bool(raw.get("ready"))
            and _safe_bool(raw.get("valid_tick"))
            and _safe_bool(raw.get("fresh"))
            and _safe_bool(raw.get("sync_valid"))
        )

    def _append_member(self, role: str, member: SnapshotMemberView | None) -> None:
        if member is None:
            return
        point = RollingPoint(
            instrument_token=member.instrument_token,
            trading_symbol=member.trading_symbol,
            ts_ns=member.ts_event_ns,
            ltp=member.ltp,
            best_bid=member.best_bid,
            best_ask=member.best_ask,
            bid_qty_5=member.bid_qty_5,
            ask_qty_5=member.ask_qty_5,
            spread=max(member.spread, 0.0),
            depth_total=member.depth_total,
            tick_size=member.tick_size,
            strike=member.strike,
        )
        self.legs[role].append(point)

    def _warmup_complete(self) -> bool:
        return all(
            history.count() >= WARMUP_MIN_VALID_SNAPSHOTS
            for history in self.legs.values()
        )

    def _raw_latest_dict(self, role: str) -> dict[str, Any]:
        latest = self.legs[role].latest()
        if latest is None:
            return {}
        return {
            "instrument_token": latest.instrument_token,
            "trading_symbol": latest.trading_symbol,
            "ts_ns": latest.ts_ns,
            "ltp": latest.ltp,
            "best_bid": latest.best_bid,
            "best_ask": latest.best_ask,
            "bid_qty_5": latest.bid_qty_5,
            "ask_qty_5": latest.ask_qty_5,
            "spread": latest.spread,
            "depth_total": latest.depth_total,
            "tick_size": latest.tick_size,
            "strike": latest.strike,
        }

    def _compute_futures_features(
        self,
        *,
        frame: SnapshotFrameView,
        member: SnapshotMemberView | None,
        now_ns: int,
    ) -> dict[str, Any]:
        history = self.legs["FUTURES"]
        latest = history.latest()
        if latest is None or member is None:
            return {"ready": False, "history_count": 0}

        # back(1)=latest, back(2)=t-1, back(3)=t-2, back(4)=t-3, back(6)=t-5
        t1 = history.back(2)
        t2 = history.back(3)
        t3 = history.back(4)
        t5 = history.back(6)

        nof_now = float(latest.bid_qty_5 - latest.ask_qty_5)
        nof_5_ago = float(t5.bid_qty_5 - t5.ask_qty_5) if t5 is not None else nof_now
        nof_slope_5 = nof_now - nof_5_ago

        velocity = 0.0
        if t3 is not None:
            dt_sec = max((latest.ts_ns - t3.ts_ns) / 1_000_000_000.0, EPSILON)
            velocity = (latest.ltp - t3.ltp) / dt_sec

        abs_velocity_ema = self.fut_baselines.abs_velocity_ema.update(abs(velocity))
        velocity_ratio = abs(velocity) / max(abs_velocity_ema, EPSILON)

        spread_ema = (
            history.spread_ema.value
            if history.spread_ema.value is not None
            else max(latest.spread, EPSILON)
        )
        spread_ratio = latest.spread / max(spread_ema, EPSILON)

        bid_dominance = latest.bid_qty_5 / max(latest.ask_qty_5, 1)
        ask_dominance = latest.ask_qty_5 / max(latest.bid_qty_5, 1)

        nof_series = history.nof_series()[-10:]
        flips = 0
        prev_sign = None
        for val in nof_series:
            sign = _sign_eps(val)
            if sign == 0:
                continue
            if prev_sign is not None and sign != prev_sign:
                flips += 1
            prev_sign = sign

        ask_reduced = bool(t1 is not None and latest.ask_qty_5 < t1.ask_qty_5)
        ask_absorbed = bool(
            t1 is not None and latest.best_ask == t1.best_ask and ask_reduced
        )
        ladder_accel_call = bool(
            t2 is not None and latest.best_bid > t2.best_bid and (ask_reduced or ask_absorbed)
        )

        bid_reduced = bool(t1 is not None and latest.bid_qty_5 < t1.bid_qty_5)
        bid_absorbed = bool(
            t1 is not None and latest.best_bid == t1.best_bid and bid_reduced
        )
        ladder_accel_put = bool(
            t2 is not None and latest.best_ask < t2.best_ask and (bid_reduced or bid_absorbed)
        )

        regime_ok = (
            history.count() >= REGIME_MIN_HISTORY
            and velocity_ratio >= VELOCITY_REGIME_MIN
            and spread_ratio <= SPREAD_REGIME_MAX
            and flips <= NOF_FLIP_MAX_10
            and member.valid_tick
            and member.fresh
            and frame.sync_valid
        )

        frame_age_ms = int(max(0, (now_ns - latest.ts_ns) / 1_000_000))
        return {
            "ready": history.count() >= 4,
            "history_count": history.count(),
            "ltp": latest.ltp,
            "best_bid": latest.best_bid,
            "best_ask": latest.best_ask,
            "bid_qty_5": latest.bid_qty_5,
            "ask_qty_5": latest.ask_qty_5,
            "depth_total": latest.depth_total,
            "tick_size": latest.tick_size,
            "spread": latest.spread,
            "spread_ema": spread_ema,
            "spread_ratio": spread_ratio,
            "velocity": velocity,
            "velocity_ratio": velocity_ratio,
            "abs_velocity_ema": abs_velocity_ema,
            "nof": nof_now,
            "nof_slope_5": nof_slope_5,
            "nof_flip_count_10": flips,
            "bid_dominance": bid_dominance,
            "ask_dominance": ask_dominance,
            "ask_reduced": ask_reduced,
            "ask_absorbed": ask_absorbed,
            "bid_reduced": bid_reduced,
            "bid_absorbed": bid_absorbed,
            "ladder_accel_call": ladder_accel_call,
            "ladder_accel_put": ladder_accel_put,
            "regime_ok": regime_ok,
            "frame_age_ms": frame_age_ms,
            "fresh": member.fresh,
            "sync_valid": frame.sync_valid,
            "valid_tick": member.valid_tick,
        }

    def _compute_option_features(
        self,
        *,
        frame: SnapshotFrameView,
        role: str,
        member: SnapshotMemberView | None,
    ) -> dict[str, Any]:
        history = self.legs[role]
        latest = history.latest()
        if latest is None or member is None:
            return {
                "ready": False,
                "role": role,
                "valid_tick": False,
                "fresh": False,
                "sync_valid": False,
            }

        t3 = history.back(4)
        delta_3 = latest.ltp - t3.ltp if t3 is not None else 0.0

        best_bid = latest.best_bid
        best_ask = latest.best_ask
        mid = (best_bid + best_ask) / 2.0 if best_bid > 0 and best_ask > 0 else latest.ltp

        spread_ema = (
            history.spread_ema.value
            if history.spread_ema.value is not None
            else max(latest.spread, EPSILON)
        )
        spread_ratio = latest.spread / max(spread_ema, EPSILON)

        fut_latest = self.legs["FUTURES"].latest()
        fut_ltp = fut_latest.ltp if fut_latest is not None else 0.0
        distance = abs((latest.strike or 0.0) - fut_ltp)
        delta_proxy = max(0.25, 0.55 - 0.0005 * distance)

        return {
            "ready": history.count() >= 1,
            "role": role,
            "instrument_token": latest.instrument_token,
            "trading_symbol": latest.trading_symbol,
            "ltp": latest.ltp,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "mid": mid,
            "bid_qty_5": latest.bid_qty_5,
            "ask_qty_5": latest.ask_qty_5,
            "depth_total": latest.depth_total,
            "spread": latest.spread,
            "spread_ema": spread_ema,
            "spread_ratio": spread_ratio,
            "tick_size": latest.tick_size,
            "strike": latest.strike,
            "delta_3": delta_3,
            "delta_proxy": delta_proxy,
            "valid_tick": member.valid_tick,
            "fresh": member.fresh,
            "sync_valid": frame.sync_valid,
            "lot_size": member.lot_size,
            "age_ms": member.age_ms,
        }

    def _compute_option_economics(self, option_payload: Mapping[str, Any]) -> dict[str, Any]:
        if not option_payload or not _safe_bool(option_payload.get("ready")):
            return {"economics_valid": False}

        premium = _safe_float(option_payload.get("ltp"), 0.0)
        target_abs = _clamp(premium * TARGET_PCT, MIN_TARGET, MAX_TARGET)
        stop_abs = _clamp(premium * STOP_PCT, MIN_STOP, MAX_STOP)
        estimated_cost = max(0.05 * premium, 2.0) + 1.0
        economics_valid = (
            premium >= PREMIUM_FLOOR
            and target_abs >= MIN_TARGET
            and target_abs >= (2.5 * estimated_cost)
        )

        return {
            "economics_valid": economics_valid,
            "premium_floor_ok": premium >= PREMIUM_FLOOR,
            "premium": premium,
            "target_abs": target_abs,
            "target": target_abs,
            "stop_abs": stop_abs,
            "stop": stop_abs,
            "estimated_cost": estimated_cost,
            "reward_to_cost": (target_abs / estimated_cost) if estimated_cost > EPSILON else 0.0,
        }


# =============================================================================
# Publisher
# =============================================================================


class FeaturesPublisher:
    def __init__(self, redis_client: Any, logger: logging.Logger | None = None) -> None:
        self.redis = redis_client
        self.log = logger or LOGGER.getChild("FeaturesPublisher")

    def publish(self, payload: Mapping[str, Any]) -> None:
        frame_ts_ns = _safe_int(payload.get("frame_ts_ns"), 0)
        futures = payload.get("futures") or {}

        feature_state = {
            "frame_id": str(payload.get("frame_id", "")),
            "selection_version": str(payload.get("selection_version", "")),
            "frame_ts_ns": str(frame_ts_ns),
            "warmup_complete": "1"
            if _safe_bool((payload.get("readiness") or {}).get("warmup_complete"))
            else "0",
            "payload_json": _json_dumps(payload),
        }
        RX.write_hash_fields(
            N.HASH_STATE_FEATURES_MME_FUT,
            feature_state,
            client=self.redis,
        )

        option_confirm = {
            "frame_ts_ns": str(frame_ts_ns),
            "ce_atm_ready": "1" if self._option_ready(payload.get("ce_atm")) else "0",
            "ce_atm1_ready": "1" if self._option_ready(payload.get("ce_atm1")) else "0",
            "pe_atm_ready": "1" if self._option_ready(payload.get("pe_atm")) else "0",
            "pe_atm1_ready": "1" if self._option_ready(payload.get("pe_atm1")) else "0",
            "ce_atm1_fallback_eligible": "1"
            if self._fallback_ready(payload.get("ce_atm1"))
            else "0",
            "pe_atm1_fallback_eligible": "1"
            if self._fallback_ready(payload.get("pe_atm1"))
            else "0",
        }
        RX.write_hash_fields(
            N.HASH_STATE_OPTION_CONFIRM,
            option_confirm,
            client=self.redis,
        )

        baselines = {
            "frame_ts_ns": str(frame_ts_ns),
            "fut_abs_velocity_ema": str(futures.get("abs_velocity_ema", "")),
            "fut_spread_ema": str(futures.get("spread_ema", "")),
            "payload_json": _json_dumps(
                {
                    "regime_ok": futures.get("regime_ok", False),
                    "nof_flip_count_10": futures.get("nof_flip_count_10", 0),
                    "abs_velocity_ema": futures.get("abs_velocity_ema", 0.0),
                    "spread_ema": futures.get("spread_ema", 0.0),
                }
            ),
        }
        RX.write_hash_fields(
            N.HASH_STATE_BASELINES_MME_FUT,
            baselines,
            client=self.redis,
        )

        RX.xadd_fields(
            N.STREAM_FEATURES_MME,
            {
                "frame_ts_ns": str(frame_ts_ns),
                "selection_version": str(payload.get("selection_version", "")),
                "payload_json": _json_dumps(payload),
            },
            client=self.redis,
        )

    @staticmethod
    def _option_ready(raw: Any) -> bool:
        if not isinstance(raw, Mapping):
            return False
        return (
            _safe_bool(raw.get("valid_tick"))
            and _safe_bool(raw.get("fresh"))
            and _safe_bool(raw.get("sync_valid"))
            and _safe_float(raw.get("delta_3"), -999999.0) >= 0.0
            and _safe_float(raw.get("spread_ratio"), 999.0) <= OPT_SPREAD_MAX
            and _safe_int(raw.get("depth_total"), 0) >= OPT_DEPTH_MIN
            and _safe_float(raw.get("tick_size"), 0.0) > 0.0
        )

    @staticmethod
    def _fallback_ready(raw: Any) -> bool:
        if not isinstance(raw, Mapping):
            return False
        return (
            FeaturesPublisher._option_ready(raw)
            and _safe_float(raw.get("delta_proxy"), 0.0) >= DELTA_MIN
        )


# =============================================================================
# Service
# =============================================================================


class FeaturesService:
    def __init__(
        self,
        *,
        redis_client: Any,
        clock: Any,
        shutdown: Any,
        instance_id: str,
        settings: AppSettings,
        logger: logging.Logger | None = None,
    ) -> None:
        self.redis = redis_client
        self.clock = clock
        self.shutdown = shutdown
        self.instance_id = instance_id
        self.settings = settings
        self.poll_interval_s = max(int(self.settings.redis.xread_block_ms), 10) / 1000.0
        self.log = logger or LOGGER.getChild("FeaturesService")
        self.reader = SnapshotReader(redis_client)
        self.engine = FeatureEngine(self.log)
        self.publisher = FeaturesPublisher(redis_client, self.log)

        self.publish_only_complete = bool(
            self.settings.feeds.publish_snapshots_only_when_complete
        )
        self.max_frame_staleness_ms = int(self.settings.feeds.max_frame_staleness_ms)
        self.heartbeat_ttl_ms = int(self.settings.runtime.heartbeat_ttl_ms)
        self.heartbeat_refresh_ms = max(
            1, int(self.settings.runtime.heartbeat_ttl_ms // 3)
        )
        self.health_stream_maxlen = DEFAULT_HEALTH_STREAM_MAXLEN
        self.error_stream_maxlen = DEFAULT_ERROR_STREAM_MAXLEN

        self._last_heartbeat_ns = 0
        self._no_frame_loops = 0
        self._consecutive_errors = 0

        self._validate_runtime_contract()

    def _validate_runtime_contract(self) -> None:
        if self.redis is None:
            raise RuntimeError("features requires redis client")
        if self.clock is None or not hasattr(self.clock, "wall_time_ns"):
            raise RuntimeError("features requires context.clock.wall_time_ns()")
        if self.shutdown is None or not hasattr(self.shutdown, "is_set") or not hasattr(
            self.shutdown, "wait"
        ):
            raise RuntimeError("features requires context.shutdown")
        if not self.instance_id:
            raise RuntimeError("features requires non-empty instance_id")
        if not RX.ping_redis(client=self.redis):
            raise RuntimeError("features redis ping failed during startup")

    def _now_ns(self) -> int:
        return int(self.clock.wall_time_ns())

    def _publish_health(self, *, status: str, detail: str) -> None:
        now_ns = self._now_ns()
        RX.write_heartbeat(
            N.KEY_HEALTH_FEATURES,
            service=N.SERVICE_FEATURES,
            instance_id=self.instance_id,
            status=status,
            ts_event_ns=now_ns,
            message=detail,
            ttl_ms=self.heartbeat_ttl_ms,
            client=self.redis,
        )
        self._last_heartbeat_ns = now_ns

    def _emit_health_event(self, *, status: str, event: str, detail: str) -> None:
        RX.xadd_fields(
            N.STREAM_SYSTEM_HEALTH,
            {
                "event_type": event,
                "service_name": N.SERVICE_FEATURES,
                "instance_id": self.instance_id,
                "status": status,
                "detail": detail,
                "ts_ns": str(self._now_ns()),
            },
            maxlen_approx=self.health_stream_maxlen,
            client=self.redis,
        )

    def publish_error(self, *, where: str, exc: Exception) -> None:
        RX.xadd_fields(
            N.STREAM_SYSTEM_ERRORS,
            {
                "event_type": "features_service_error",
                "service_name": N.SERVICE_FEATURES,
                "instance_id": self.instance_id,
                "where": where,
                "error_type": type(exc).__name__,
                "detail": str(exc),
                "ts_ns": str(self._now_ns()),
            },
            maxlen_approx=self.error_stream_maxlen,
            client=self.redis,
        )

    def run_once(self) -> dict[str, Any] | None:
        frame = self.reader.read()
        if frame is None:
            return None

        if self.max_frame_staleness_ms > 0 and frame.ts_frame_ns > 0:
            age_ms = max(0, int((self._now_ns() - frame.ts_frame_ns) / 1_000_000))
            if age_ms > self.max_frame_staleness_ms:
                raise RuntimeError(f"snapshot_frame_stale age_ms={age_ms}")

        payload = self.engine.build_payload(frame, now_ns=self._now_ns())

        readiness = dict(payload.get("readiness") or {})
        if self.publish_only_complete and not _safe_bool(readiness.get("frame_valid")):
            return payload
        if self.publish_only_complete and not _safe_bool(readiness.get("sync_valid")):
            return payload

        self.publisher.publish(payload)
        return payload

    def start(self) -> int:
        self._emit_health_event(
            status=N.HEALTH_STATUS_OK,
            event="features_bootstrap_complete",
            detail="features_initialized",
        )
        self._publish_health(status=N.HEALTH_STATUS_OK, detail="features_started")

        try:
            while not self.shutdown.is_set():
                loop_status = N.HEALTH_STATUS_OK
                loop_detail = "features_idle"

                try:
                    payload = self.run_once()
                    self._consecutive_errors = 0

                    if payload is None:
                        self._no_frame_loops += 1
                        if self._no_frame_loops >= NO_FRAME_WARN_AFTER_LOOPS:
                            loop_status = N.HEALTH_STATUS_WARN
                            loop_detail = "no_snapshot_frame_available"
                        else:
                            loop_detail = "waiting_for_snapshot_frame"
                    else:
                        self._no_frame_loops = 0
                        readiness = dict(payload.get("readiness") or {})
                        if not _safe_bool(readiness.get("frame_valid")) or not _safe_bool(
                            readiness.get("sync_valid")
                        ):
                            loop_status = N.HEALTH_STATUS_WARN
                            loop_detail = "frame_invalid_or_unsynced"
                        elif not _safe_bool(readiness.get("warmup_complete")):
                            loop_status = N.HEALTH_STATUS_WARN
                            loop_detail = "warmup_incomplete"
                        else:
                            loop_detail = "features_ready"

                except Exception as exc:
                    self._consecutive_errors += 1
                    self.log.exception("features_service_loop_error")
                    with contextlib.suppress(Exception):
                        self.publish_error(where="features_service_loop_error", exc=exc)
                    loop_status = N.HEALTH_STATUS_ERROR
                    loop_detail = f"loop_error:{type(exc).__name__}"

                now_ns = self._now_ns()
                if (now_ns - self._last_heartbeat_ns) >= (
                    self.heartbeat_refresh_ms * 1_000_000
                ):
                    with contextlib.suppress(Exception):
                        self._publish_health(status=loop_status, detail=loop_detail)

                self.shutdown.wait(self.poll_interval_s)
        finally:
            with contextlib.suppress(Exception):
                self._publish_health(status=N.HEALTH_STATUS_WARN, detail="features_stopping")

        self.log.info("features_service_stopped")
        return 0


# =============================================================================
# Canonical entrypoint
# =============================================================================


def run(context: Any) -> int:
    _validate_name_surface_or_die()

    settings = getattr(context, "settings", None) or get_settings()
    if not isinstance(settings, AppSettings):
        raise RuntimeError(
            "features requires context.settings or get_settings() returning AppSettings"
        )

    redis_runtime = getattr(context, "redis", None)
    if redis_runtime is None:
        raise RuntimeError("features requires context.redis")
    redis_client = redis_runtime.sync if hasattr(redis_runtime, "sync") else redis_runtime

    shutdown = getattr(context, "shutdown", None)
    clock = getattr(context, "clock", None)
    instance_id = _safe_str(getattr(context, "instance_id", ""))

    if shutdown is None:
        raise RuntimeError("features requires context.shutdown")
    if clock is None:
        raise RuntimeError("features requires context.clock")
    if not instance_id:
        raise RuntimeError("features requires context.instance_id")

    service = FeaturesService(
        redis_client=redis_client,
        clock=clock,
        shutdown=shutdown,
        instance_id=instance_id,
        settings=settings,
        logger=LOGGER,
    )
    return service.start()