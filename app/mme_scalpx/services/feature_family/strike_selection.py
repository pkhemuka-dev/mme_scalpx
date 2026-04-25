from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/strike_selection.py

Canonical strike-selection and slow-context OI wall helper surface for ScalpX MME.

Purpose
-------
This module OWNS:
- deterministic strike-ladder normalization from Dhan context payloads
- side-aware strike candidate extraction for CALL / PUT families
- nearest OI wall summaries for classic MIS doctrines and MISO
- wall-distance, wall-strength, and OI-bias derivation
- explicit, serializable helper payloads for features.py publication

This module DOES NOT own:
- provider selection / failover policy
- raw Dhan ingestion
- live option tradability truth
- sub-second trigger logic
- doctrine-specific entry / exit decisions
- broker execution feasibility
- Redis I/O

Frozen design law
-----------------
- OI is a slow-context / strike-quality surface only.
- OI may influence strike relevance, ranking, veto quality, and context quality.
- OI may never be treated as immediate trigger truth.
- This module must remain deterministic and side-effect free.
- Inputs may be partial / evolving during migration; outputs must degrade explicitly.

Important migration note
------------------------
The current WIP surface is still stabilizing around DhanContextState and the
family feature seam. This module therefore accepts tolerant mapping-shaped
inputs and normalizes them into explicit package-owned structures instead of
assuming one perfectly frozen upstream chain schema already exists.

Returned surfaces are intentionally JSON-friendly plain mappings so features.py
can publish them directly into ``family_surfaces`` / ``family_features`` payloads.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Any, Final, Iterable, Mapping, Sequence

from app.mme_scalpx.core import names as N

try:  # optional during isolated proofing
    from . import common as FF_H
except Exception:  # pragma: no cover
    FF_H = None  # type: ignore[assignment]


EPSILON: Final[float] = 1e-8
DEFAULT_MAX_MONITORED_PER_SIDE: Final[int] = 5
DEFAULT_MAX_TRADABLE_PER_SIDE: Final[int] = 3
DEFAULT_WALL_NEAR_DISTANCE_MULTIPLIER: Final[float] = 1.0
DEFAULT_WALL_PRESSURE_STRONG_MIN: Final[float] = 0.62

# conservative aliases to avoid coupling too tightly to still-moving upstream
# chain field names during the WIP seam-stabilization phase.
_SIDE_ALIASES: Final[dict[str, tuple[str, ...]]] = {
    N.SIDE_CALL: ("CALL", "CE", "C", "call", "ce", "c"),
    N.SIDE_PUT: ("PUT", "PE", "P", "put", "pe", "p"),
}

_CALL_RANK_KEYS: Final[tuple[str, ...]] = (
    "call_rank",
    "ce_rank",
    "rank_call",
    "rank_ce",
    "call_chain_rank",
    "ce_chain_rank",
)
_PUT_RANK_KEYS: Final[tuple[str, ...]] = (
    "put_rank",
    "pe_rank",
    "rank_put",
    "rank_pe",
    "put_chain_rank",
    "pe_chain_rank",
)

_STRIKE_KEYS: Final[tuple[str, ...]] = (
    "strike",
    "strike_price",
    "strike_value",
)
_SIDE_KEYS: Final[tuple[str, ...]] = (
    "side",
    "option_side",
    "instrument_side",
    "right",
)
_LTP_KEYS: Final[tuple[str, ...]] = (
    "ltp",
    "last_price",
    "last_traded_price",
    "price",
    "chain_last_price",
)
_OI_KEYS: Final[tuple[str, ...]] = (
    "oi",
    "open_interest",
    "chain_oi",
)
_OI_CHANGE_KEYS: Final[tuple[str, ...]] = (
    "oi_change",
    "oi_delta",
    "change_in_oi",
    "open_interest_change",
)
_VOLUME_KEYS: Final[tuple[str, ...]] = (
    "volume",
    "vol",
    "chain_volume",
    "traded_volume",
)
_IV_KEYS: Final[tuple[str, ...]] = (
    "iv",
    "implied_volatility",
    "chain_iv",
)
_BID_KEYS: Final[tuple[str, ...]] = (
    "bid",
    "best_bid",
    "best_bid_price",
    "chain_best_bid",
)
_ASK_KEYS: Final[tuple[str, ...]] = (
    "ask",
    "best_ask",
    "best_ask_price",
    "chain_best_ask",
)
_BID_QTY_KEYS: Final[tuple[str, ...]] = (
    "bid_qty",
    "best_bid_qty",
    "bid_quantity",
    "chain_best_bid_qty",
)
_ASK_QTY_KEYS: Final[tuple[str, ...]] = (
    "ask_qty",
    "best_ask_qty",
    "ask_quantity",
    "chain_best_ask_qty",
)
_DELTA_KEYS: Final[tuple[str, ...]] = (
    "delta",
    "option_delta",
)
_GAMMA_KEYS: Final[tuple[str, ...]] = (
    "gamma",
    "option_gamma",
)
_SCORE_KEYS: Final[tuple[str, ...]] = (
    "strike_score",
    "score",
    "chain_score",
    "rank_score",
)

_CONTAINER_KEYS: Final[tuple[str, ...]] = (
    "strike_ladder",
    "strike_ladder_rows",
    "chain_rows",
    "option_chain",
    "chain",
    "rows",
    "strikes",
    "ladder",
)

__all__ = [
    "StrikeLadderRow",
    "build_classic_strike_surface",
    "build_miso_strike_surface",
    "build_oi_wall_summary",
    "build_strike_ladder_surface",
    "normalize_strike_ladder_rows",
    "select_classic_candidates",
    "select_miso_candidates",
]


@dataclass(frozen=True, slots=True)
class StrikeLadderRow:
    strike: float
    side: str
    ltp: float | None = None
    oi: int | None = None
    oi_change: int | None = None
    volume: int | None = None
    iv: float | None = None
    bid: float | None = None
    ask: float | None = None
    bid_qty: int | None = None
    ask_qty: int | None = None
    delta: float | None = None
    gamma: float | None = None
    strike_score: float | None = None
    rank_hint: int | None = None
    raw: Mapping[str, Any] | None = None

    def spread(self) -> float | None:
        if self.bid is None or self.ask is None:
            return None
        if self.ask < self.bid:
            return None
        return self.ask - self.bid

    def spread_ratio(self) -> float | None:
        if self.bid is None or self.ask is None:
            return None
        mid = (self.bid + self.ask) / 2.0
        if mid <= EPSILON:
            return None
        spread = self.ask - self.bid
        if spread < 0:
            return None
        return spread / max(mid, EPSILON)

    def touch_depth(self) -> int | None:
        if self.bid_qty is None and self.ask_qty is None:
            return None
        return int(max((self.bid_qty or 0) + (self.ask_qty or 0), 0))

    def to_dict(self) -> dict[str, Any]:
        return {
            "strike": self.strike,
            "side": self.side,
            "ltp": self.ltp,
            "oi": self.oi,
            "oi_change": self.oi_change,
            "volume": self.volume,
            "iv": self.iv,
            "bid": self.bid,
            "ask": self.ask,
            "spread": self.spread(),
            "spread_ratio": self.spread_ratio(),
            "bid_qty": self.bid_qty,
            "ask_qty": self.ask_qty,
            "touch_depth": self.touch_depth(),
            "delta": self.delta,
            "gamma": self.gamma,
            "strike_score": self.strike_score,
            "rank_hint": self.rank_hint,
        }


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        number = float(value)
    except Exception:
        return default
    if not isfinite(number):
        return default
    return number


def _safe_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        return int(float(value))
    except Exception:
        return default


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = _safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _pick(mapping: Mapping[str, Any] | None, keys: Sequence[str]) -> Any:
    if not isinstance(mapping, Mapping):
        return None
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _is_side(value: Any, side: str) -> bool:
    text = _safe_str(value)
    if not text:
        return False
    normalized = text.upper()
    allowed = {alias.upper() for alias in _SIDE_ALIASES.get(side, ())}
    return normalized in allowed


def _normalize_side(value: Any) -> str | None:
    text = _safe_str(value)
    if not text:
        return None
    if _is_side(text, N.SIDE_CALL):
        return N.SIDE_CALL
    if _is_side(text, N.SIDE_PUT):
        return N.SIDE_PUT
    return None


def _coalesce_container(context: Mapping[str, Any] | None) -> Sequence[Mapping[str, Any]]:
    if not isinstance(context, Mapping):
        return ()
    direct = [item for item in _extract_rows(context) if isinstance(item, Mapping)]
    if direct:
        return tuple(direct)
    for key in _CONTAINER_KEYS:
        value = context.get(key)
        extracted = [item for item in _extract_rows(value) if isinstance(item, Mapping)]
        if extracted:
            return tuple(extracted)
    return ()


def _extract_rows(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        maybe_rows = value.get("rows")
        if isinstance(maybe_rows, Sequence) and not isinstance(maybe_rows, (str, bytes)):
            return [row for row in maybe_rows if isinstance(row, Mapping)]
        if any(k in value for k in _STRIKE_KEYS) and any(k in value for k in _SIDE_KEYS):
            return [value]
        nested_rows: list[Mapping[str, Any]] = []
        for key in _CONTAINER_KEYS:
            nested = value.get(key)
            if isinstance(nested, Sequence) and not isinstance(nested, (str, bytes)):
                nested_rows.extend(row for row in nested if isinstance(row, Mapping))
        return nested_rows
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [row for row in value if isinstance(row, Mapping)]
    return []


def _resolve_rank_hint(row: Mapping[str, Any], side: str) -> int | None:
    keys = _CALL_RANK_KEYS if side == N.SIDE_CALL else _PUT_RANK_KEYS
    return _safe_int(_pick(row, keys), None)


def _atm_reference(
    *,
    dhan_context: Mapping[str, Any] | None,
    futures_features: Mapping[str, Any] | None,
    selected_features: Mapping[str, Any] | None,
) -> float | None:
    value = (
        _safe_float(_pick(dhan_context, ("atm_strike", "atm", "atm_reference_strike")), None)
        or _safe_float(_pick(selected_features, ("atm_strike", "atm")), None)
        or _safe_float(_pick(futures_features, ("atm_strike", "atm")), None)
        or _safe_float(_pick(dhan_context, ("underlying_atm_strike",)), None)
    )
    return value


def normalize_strike_ladder_rows(
    dhan_context: Mapping[str, Any] | None,
) -> tuple[StrikeLadderRow, ...]:
    """
    Normalize the evolving Dhan context strike-ladder payload into canonical rows.

    This function is intentionally tolerant to several plausible upstream field
    names so the family seam can stabilize without forcing repeated rewrites.
    """
    rows: list[StrikeLadderRow] = []
    for raw_row in _coalesce_container(dhan_context):
        side = _normalize_side(_pick(raw_row, _SIDE_KEYS))
        strike = _safe_float(_pick(raw_row, _STRIKE_KEYS), None)
        if side is None or strike is None or strike <= 0.0:
            continue
        rows.append(
            StrikeLadderRow(
                strike=strike,
                side=side,
                ltp=_safe_float(_pick(raw_row, _LTP_KEYS), None),
                oi=_safe_int(_pick(raw_row, _OI_KEYS), None),
                oi_change=_safe_int(_pick(raw_row, _OI_CHANGE_KEYS), None),
                volume=_safe_int(_pick(raw_row, _VOLUME_KEYS), None),
                iv=_safe_float(_pick(raw_row, _IV_KEYS), None),
                bid=_safe_float(_pick(raw_row, _BID_KEYS), None),
                ask=_safe_float(_pick(raw_row, _ASK_KEYS), None),
                bid_qty=_safe_int(_pick(raw_row, _BID_QTY_KEYS), None),
                ask_qty=_safe_int(_pick(raw_row, _ASK_QTY_KEYS), None),
                delta=_safe_float(_pick(raw_row, _DELTA_KEYS), None),
                gamma=_safe_float(_pick(raw_row, _GAMMA_KEYS), None),
                strike_score=_safe_float(_pick(raw_row, _SCORE_KEYS), None),
                rank_hint=_resolve_rank_hint(raw_row, side),
                raw=raw_row,
            )
        )

    rows.sort(key=lambda item: (item.side, item.strike))
    return tuple(rows)


def _rows_for_side(rows: Iterable[StrikeLadderRow], side: str) -> tuple[StrikeLadderRow, ...]:
    side_rows = [row for row in rows if row.side == side]
    side_rows.sort(key=lambda item: item.strike)
    return tuple(side_rows)


def _distance_points(strike: float | None, reference_strike: float | None) -> float | None:
    if strike is None or reference_strike is None:
        return None
    return abs(strike - reference_strike)


def _distance_steps(
    strike: float | None,
    reference_strike: float | None,
    strike_step: float | None,
) -> float | None:
    if strike is None or reference_strike is None:
        return None
    raw_distance = abs(strike - reference_strike)
    if strike_step is None or strike_step <= EPSILON:
        return raw_distance
    return raw_distance / strike_step


def _infer_strike_step(rows: Sequence[StrikeLadderRow]) -> float | None:
    positive_diffs: list[float] = []
    by_side = {
        N.SIDE_CALL: _rows_for_side(rows, N.SIDE_CALL),
        N.SIDE_PUT: _rows_for_side(rows, N.SIDE_PUT),
    }
    for side_rows in by_side.values():
        for prev, curr in zip(side_rows, side_rows[1:]):
            diff = curr.strike - prev.strike
            if diff > EPSILON:
                positive_diffs.append(diff)
    if not positive_diffs:
        return None
    return min(positive_diffs)


def _resolve_strike_step(
    *,
    dhan_context: Mapping[str, Any] | None,
    rows: Sequence[StrikeLadderRow],
) -> float | None:
    explicit = _safe_float(_pick(dhan_context, ("strike_step", "chain_strike_step")), None)
    if explicit is not None and explicit > EPSILON:
        return explicit
    return _infer_strike_step(rows)


def _otm_directional_distance(
    *,
    row: StrikeLadderRow,
    reference_strike: float | None,
) -> float | None:
    if reference_strike is None:
        return None
    if row.side == N.SIDE_CALL:
        return row.strike - reference_strike
    if row.side == N.SIDE_PUT:
        return reference_strike - row.strike
    return None


def _score_row_for_classic(
    row: StrikeLadderRow,
    *,
    reference_strike: float | None,
    strike_step: float | None,
) -> float:
    score = 0.0

    if row.strike_score is not None:
        score += row.strike_score * 1.60

    if row.volume is not None:
        score += min(max(row.volume, 0) / 10_000.0, 1.25) * 0.55

    if row.oi is not None:
        score += min(max(row.oi, 0) / 100_000.0, 1.25) * 0.55

    if row.oi_change is not None:
        score += min(max(row.oi_change, 0) / 25_000.0, 1.0) * 0.35

    spread_ratio = row.spread_ratio()
    if spread_ratio is not None:
        score += max(0.0, 1.0 - min(spread_ratio, 1.0)) * 0.65

    touch_depth = row.touch_depth()
    if touch_depth is not None:
        score += min(max(touch_depth, 0) / 2_500.0, 1.0) * 0.40

    directional_distance = _otm_directional_distance(row=row, reference_strike=reference_strike)
    if directional_distance is not None:
        if directional_distance < -EPSILON:
            score -= 0.80
        else:
            steps = _distance_steps(row.strike, reference_strike, strike_step)
            if steps is not None:
                if steps <= 0.15:
                    score += 0.80
                elif steps <= 1.15:
                    score += 0.95
                elif steps <= 2.15:
                    score += 0.40
                else:
                    score -= min((steps - 2.15) * 0.20, 1.0)

    if row.rank_hint is not None:
        score += max(0.0, 1.0 - (max(row.rank_hint, 1) - 1) * 0.10) * 0.25

    return score


def _score_row_for_miso(
    row: StrikeLadderRow,
    *,
    reference_strike: float | None,
    strike_step: float | None,
) -> float:
    score = 0.0

    if row.strike_score is not None:
        score += row.strike_score * 2.40

    spread_ratio = row.spread_ratio()
    if spread_ratio is not None:
        score += max(0.0, 1.0 - min(spread_ratio, 1.0)) * 1.10

    touch_depth = row.touch_depth()
    if touch_depth is not None:
        score += min(max(touch_depth, 0) / 2_000.0, 1.25) * 1.00

    if row.volume is not None:
        score += min(max(row.volume, 0) / 8_000.0, 1.25) * 0.80

    if row.oi is not None:
        score += min(max(row.oi, 0) / 80_000.0, 1.20) * 0.50

    if row.delta is not None:
        # prefer moderate tradable deltas, not ultra-deep ITM/OTM
        score += max(0.0, 1.0 - abs(abs(row.delta) - 0.35) / 0.35) * 0.65

    if row.gamma is not None:
        score += min(max(row.gamma, 0.0) / 0.05, 1.10) * 0.45

    directional_distance = _otm_directional_distance(row=row, reference_strike=reference_strike)
    if directional_distance is not None:
        steps = _distance_steps(row.strike, reference_strike, strike_step)
        if steps is not None:
            if steps <= 1.10:
                score += 0.95
            elif steps <= 2.10:
                score += 0.45
            else:
                score -= min((steps - 2.10) * 0.25, 1.2)

    return score


def _sort_candidates(
    rows: Iterable[StrikeLadderRow],
    *,
    scorer: Any,
    reference_strike: float | None,
    strike_step: float | None,
) -> tuple[dict[str, Any], ...]:
    ranked: list[dict[str, Any]] = []
    for row in rows:
        score = float(scorer(row, reference_strike=reference_strike, strike_step=strike_step))
        ranked.append(
            {
                "strike": row.strike,
                "side": row.side,
                "ltp": row.ltp,
                "oi": row.oi,
                "oi_change": row.oi_change,
                "volume": row.volume,
                "iv": row.iv,
                "bid": row.bid,
                "ask": row.ask,
                "spread": row.spread(),
                "spread_ratio": row.spread_ratio(),
                "touch_depth": row.touch_depth(),
                "delta": row.delta,
                "gamma": row.gamma,
                "strike_score": row.strike_score,
                "rank_hint": row.rank_hint,
                "selection_score": score,
                "distance_from_atm_points": _distance_points(row.strike, reference_strike),
                "distance_from_atm_steps": _distance_steps(row.strike, reference_strike, strike_step),
                "otm_directional_distance": _otm_directional_distance(row=row, reference_strike=reference_strike),
            }
        )

    ranked.sort(
        key=lambda item: (
            -float(item["selection_score"]),
            float(item["spread_ratio"] if item["spread_ratio"] is not None else 9_999.0),
            -float(item["touch_depth"] if item["touch_depth"] is not None else -1.0),
            float(item["distance_from_atm_steps"] if item["distance_from_atm_steps"] is not None else 9_999.0),
            float(item["strike"]),
        )
    )
    return tuple(ranked)


def select_classic_candidates(
    *,
    dhan_context: Mapping[str, Any] | None,
    side: str,
    max_candidates: int = DEFAULT_MAX_TRADABLE_PER_SIDE,
) -> tuple[dict[str, Any], ...]:
    rows = normalize_strike_ladder_rows(dhan_context)
    side_rows = _rows_for_side(rows, side)
    reference = _atm_reference(
        dhan_context=dhan_context,
        futures_features=None,
        selected_features=None,
    )
    strike_step = _resolve_strike_step(dhan_context=dhan_context, rows=rows)
    ranked = _sort_candidates(
        side_rows,
        scorer=_score_row_for_classic,
        reference_strike=reference,
        strike_step=strike_step,
    )
    return ranked[: max(0, int(max_candidates))]


def select_miso_candidates(
    *,
    dhan_context: Mapping[str, Any] | None,
    side: str,
    max_monitored: int = DEFAULT_MAX_MONITORED_PER_SIDE,
    max_tradable: int = DEFAULT_MAX_TRADABLE_PER_SIDE,
) -> dict[str, Any]:
    rows = normalize_strike_ladder_rows(dhan_context)
    side_rows = _rows_for_side(rows, side)
    reference = _atm_reference(
        dhan_context=dhan_context,
        futures_features=None,
        selected_features=None,
    )
    strike_step = _resolve_strike_step(dhan_context=dhan_context, rows=rows)
    ranked = _sort_candidates(
        side_rows,
        scorer=_score_row_for_miso,
        reference_strike=reference,
        strike_step=strike_step,
    )

    monitored = tuple(ranked[: max(0, int(max_monitored))])
    tradable = tuple(monitored[: max(0, int(max_tradable))])
    shadow = tuple(monitored[max(0, int(max_tradable)) :])

    selected = tradable[0] if tradable else None
    return {
        "side": side,
        "atm_reference_strike": reference,
        "max_monitored": int(max_monitored),
        "max_tradable": int(max_tradable),
        "selected": selected,
        "monitored": monitored,
        "tradable": tradable,
        "shadow": shadow,
        "present": bool(monitored),
    }


def _sum_positive(rows: Iterable[StrikeLadderRow], attr: str) -> float:
    total = 0.0
    for row in rows:
        value = getattr(row, attr)
        if value is None:
            continue
        total += max(float(value), 0.0)
    return total


def _best_wall(
    rows: Iterable[StrikeLadderRow],
    *,
    reference_strike: float | None,
    side: str,
    strike_step: float | None,
) -> StrikeLadderRow | None:
    candidates: list[StrikeLadderRow] = []
    for row in rows:
        if row.oi is None or row.oi <= 0:
            continue
        directional_distance = _otm_directional_distance(row=row, reference_strike=reference_strike)
        if directional_distance is None:
            continue
        if directional_distance < -EPSILON:
            continue
        candidates.append(row)

    if not candidates:
        return None

    candidates.sort(
        key=lambda row: (
            _distance_steps(row.strike, reference_strike, strike_step) if _distance_steps(row.strike, reference_strike, strike_step) is not None else 9_999.0,
            -float(row.oi or 0),
            -float(max(row.oi_change or 0, 0)),
            -float(max(row.volume or 0, 0)),
        )
    )
    return candidates[0]


def _wall_strength_score(
    *,
    wall: StrikeLadderRow | None,
    side_rows: Sequence[StrikeLadderRow],
) -> float | None:
    if wall is None or wall.oi is None or wall.oi <= 0:
        return None
    oi_values = [float(row.oi) for row in side_rows if row.oi is not None and row.oi > 0]
    if not oi_values:
        return None
    max_oi = max(oi_values)
    mean_oi = sum(oi_values) / max(len(oi_values), 1)
    oi_change = max(float(wall.oi_change or 0), 0.0)
    max_change = max((max(float(row.oi_change or 0), 0.0) for row in side_rows), default=0.0)
    volume = max(float(wall.volume or 0), 0.0)
    max_volume = max((max(float(row.volume or 0), 0.0) for row in side_rows), default=0.0)

    oi_component = min(float(wall.oi) / max(max_oi, EPSILON), 1.0)
    mean_component = min(float(wall.oi) / max(mean_oi, EPSILON), 2.0) / 2.0
    oi_change_component = 0.0 if max_change <= EPSILON else min(oi_change / max_change, 1.0)
    volume_component = 0.0 if max_volume <= EPSILON else min(volume / max_volume, 1.0)

    score = (
        (oi_component * 0.45)
        + (mean_component * 0.25)
        + (oi_change_component * 0.20)
        + (volume_component * 0.10)
    )
    return max(0.0, min(score, 1.0))


def _near_wall_flag(
    *,
    wall_distance_steps: float | None,
    wall_distance_points: float | None = None,
    strike_step: float | None = None,
) -> bool:
    if strike_step is not None and strike_step > EPSILON and wall_distance_steps is not None:
        return wall_distance_steps <= DEFAULT_WALL_NEAR_DISTANCE_MULTIPLIER
    if wall_distance_points is None:
        return False
    fallback_threshold = (
        strike_step
        if strike_step is not None and strike_step > EPSILON
        else 50.0
    ) * DEFAULT_WALL_NEAR_DISTANCE_MULTIPLIER
    return wall_distance_points <= fallback_threshold


def build_oi_wall_summary(
    *,
    dhan_context: Mapping[str, Any] | None,
    futures_features: Mapping[str, Any] | None = None,
    selected_features: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build side-aware nearest OI wall summaries and overall OI bias.

    CALL wall:
        nearest CALL strike at/above ATM with meaningful OI
        interpreted as nearest CALL OI resistance wall

    PUT wall:
        nearest PUT strike at/below ATM with meaningful OI
        interpreted as nearest PUT OI support wall
    """
    rows = normalize_strike_ladder_rows(dhan_context)
    call_rows = _rows_for_side(rows, N.SIDE_CALL)
    put_rows = _rows_for_side(rows, N.SIDE_PUT)

    reference = _atm_reference(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )
    strike_step = _resolve_strike_step(dhan_context=dhan_context, rows=rows)

    call_wall = _best_wall(
        call_rows,
        reference_strike=reference,
        side=N.SIDE_CALL,
        strike_step=strike_step,
    )
    put_wall = _best_wall(
        put_rows,
        reference_strike=reference,
        side=N.SIDE_PUT,
        strike_step=strike_step,
    )

    call_wall_strength = _wall_strength_score(wall=call_wall, side_rows=call_rows)
    put_wall_strength = _wall_strength_score(wall=put_wall, side_rows=put_rows)

    call_distance_points = None if call_wall is None else _distance_points(call_wall.strike, reference)
    put_distance_points = None if put_wall is None else _distance_points(put_wall.strike, reference)
    call_distance_steps = None if call_wall is None else _distance_steps(call_wall.strike, reference, strike_step)
    put_distance_steps = None if put_wall is None else _distance_steps(put_wall.strike, reference, strike_step)

    total_call_oi = _sum_positive(call_rows, "oi")
    total_put_oi = _sum_positive(put_rows, "oi")
    total_call_oi_change = _sum_positive(call_rows, "oi_change")
    total_put_oi_change = _sum_positive(put_rows, "oi_change")

    oi_ratio = None
    if total_call_oi > EPSILON and total_put_oi > EPSILON:
        oi_ratio = total_put_oi / max(total_call_oi, EPSILON)

    oi_bias_score = 0.0
    if total_call_oi > 0 or total_put_oi > 0:
        oi_bias_score = (total_put_oi - total_call_oi) / max(total_put_oi + total_call_oi, EPSILON)

    oi_bias_change_score = 0.0
    if total_call_oi_change > 0 or total_put_oi_change > 0:
        oi_bias_change_score = (total_put_oi_change - total_call_oi_change) / max(
            total_put_oi_change + total_call_oi_change,
            EPSILON,
        )

    combined_bias = (oi_bias_score * 0.70) + (oi_bias_change_score * 0.30)

    if combined_bias >= 0.15:
        oi_bias_label = "PUT_SUPPORTIVE"
    elif combined_bias <= -0.15:
        oi_bias_label = "CALL_SUPPORTIVE"
    else:
        oi_bias_label = "NEUTRAL"

    return {
        "present": bool(rows),
        "atm_reference_strike": reference,
        "strike_step": strike_step,
        "nearest_call_oi_resistance_strike": None if call_wall is None else call_wall.strike,
        "nearest_put_oi_support_strike": None if put_wall is None else put_wall.strike,
        "call_wall": None
        if call_wall is None
        else {
            **call_wall.to_dict(),
            "wall_kind": "CALL_OI_RESISTANCE",
            "wall_distance_points": call_distance_points,
            "wall_distance_steps": call_distance_steps,
            "wall_strength_score": call_wall_strength,
            "wall_strength_label": (
                "STRONG" if (call_wall_strength or 0.0) >= DEFAULT_WALL_PRESSURE_STRONG_MIN else "MODERATE"
            ),
            "near_wall": _near_wall_flag(
                wall_distance_steps=call_distance_steps,
                wall_distance_points=call_distance_points,
                strike_step=strike_step,
            ),
        },
        "put_wall": None
        if put_wall is None
        else {
            **put_wall.to_dict(),
            "wall_kind": "PUT_OI_SUPPORT",
            "wall_distance_points": put_distance_points,
            "wall_distance_steps": put_distance_steps,
            "wall_strength_score": put_wall_strength,
            "wall_strength_label": (
                "STRONG" if (put_wall_strength or 0.0) >= DEFAULT_WALL_PRESSURE_STRONG_MIN else "MODERATE"
            ),
            "near_wall": _near_wall_flag(
                wall_distance_steps=put_distance_steps,
                wall_distance_points=put_distance_points,
                strike_step=strike_step,
            ),
        },
        "call_wall_distance_points": call_distance_points,
        "put_wall_distance_points": put_distance_points,
        "call_wall_strength_score": call_wall_strength,
        "put_wall_strength_score": put_wall_strength,
        "call_wall_near": _near_wall_flag(
            wall_distance_steps=call_distance_steps,
            wall_distance_points=call_distance_points,
            strike_step=strike_step,
        ),
        "put_wall_near": _near_wall_flag(
            wall_distance_steps=put_distance_steps,
            wall_distance_points=put_distance_points,
            strike_step=strike_step,
        ),
        "total_call_oi": total_call_oi,
        "total_put_oi": total_put_oi,
        "total_call_oi_change": total_call_oi_change,
        "total_put_oi_change": total_put_oi_change,
        "oi_ratio_put_to_call": oi_ratio,
        "oi_bias_score": combined_bias,
        "oi_bias": oi_bias_label,
    }


def build_strike_ladder_surface(
    *,
    dhan_context: Mapping[str, Any] | None,
    futures_features: Mapping[str, Any] | None = None,
    selected_features: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    rows = normalize_strike_ladder_rows(dhan_context)
    reference = _atm_reference(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )
    strike_step = _resolve_strike_step(dhan_context=dhan_context, rows=rows)
    wall_summary = build_oi_wall_summary(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )

    calls = _rows_for_side(rows, N.SIDE_CALL)
    puts = _rows_for_side(rows, N.SIDE_PUT)

    return {
        "present": bool(rows),
        "row_count": len(rows),
        "call_row_count": len(calls),
        "put_row_count": len(puts),
        "atm_reference_strike": reference,
        "strike_step": strike_step,
        "calls": tuple(row.to_dict() for row in calls),
        "puts": tuple(row.to_dict() for row in puts),
        "oi_wall_summary": wall_summary,
    }


def build_classic_strike_surface(
    *,
    dhan_context: Mapping[str, Any] | None,
    side: str,
    futures_features: Mapping[str, Any] | None = None,
    selected_features: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    reference = _atm_reference(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )
    strike_step = _resolve_strike_step(
        dhan_context=dhan_context,
        rows=normalize_strike_ladder_rows(dhan_context),
    )
    candidates = select_classic_candidates(dhan_context=dhan_context, side=side)
    wall_summary = build_oi_wall_summary(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )

    selected = candidates[0] if candidates else None
    wall = wall_summary["call_wall"] if side == N.SIDE_CALL else wall_summary["put_wall"]
    near_same_side_wall = bool(wall and wall.get("near_wall"))
    wall_strength_score = None if wall is None else wall.get("wall_strength_score")
    oi_bias = _safe_str(wall_summary.get("oi_bias"))

    context_alignment = None
    if oi_bias:
        if side == N.SIDE_CALL:
            context_alignment = oi_bias == "PUT_SUPPORTIVE"
        else:
            context_alignment = oi_bias == "CALL_SUPPORTIVE"

    return {
        "present": bool(selected),
        "side": side,
        "atm_reference_strike": reference,
        "strike_step": strike_step,
        "selected": selected,
        "candidates": candidates,
        "nearest_same_side_wall": wall,
        "near_same_side_wall": near_same_side_wall,
        "same_side_wall_strength_score": wall_strength_score,
        "oi_bias": oi_bias,
        "oi_bias_score": wall_summary.get("oi_bias_score"),
        "oi_context_alignment": context_alignment,
        "oi_wall_summary": wall_summary,
        "selection_mode_hint": "Dhan-enhanced strike quality context only",
    }


def build_miso_strike_surface(
    *,
    dhan_context: Mapping[str, Any] | None,
    side: str,
    futures_features: Mapping[str, Any] | None = None,
    selected_features: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    reference = _atm_reference(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )
    strike_step = _resolve_strike_step(
        dhan_context=dhan_context,
        rows=normalize_strike_ladder_rows(dhan_context),
    )
    candidate_bundle = select_miso_candidates(dhan_context=dhan_context, side=side)
    wall_summary = build_oi_wall_summary(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )
    selected = candidate_bundle.get("selected")
    wall = wall_summary["call_wall"] if side == N.SIDE_CALL else wall_summary["put_wall"]

    return {
        "present": bool(selected),
        "side": side,
        "atm_reference_strike": reference,
        "strike_step": strike_step,
        "selected": selected,
        "monitored": candidate_bundle.get("monitored"),
        "tradable": candidate_bundle.get("tradable"),
        "shadow": candidate_bundle.get("shadow"),
        "nearest_same_side_wall": wall,
        "near_same_side_wall": bool(wall and wall.get("near_wall")),
        "same_side_wall_strength_score": None if wall is None else wall.get("wall_strength_score"),
        "oi_bias": wall_summary.get("oi_bias"),
        "oi_bias_score": wall_summary.get("oi_bias_score"),
        "oi_wall_summary": wall_summary,
        "selection_mode_hint": "Dhan-mandatory strike ladder context",
    }

# ===== BATCH8_SHARED_CORE_GUARDS START =====
# Batch 8 freeze-final guard:
# OI rows without ATM/reference are not OI-wall-ready.

_BATCH8_ORIGINAL_SELECT_MISO_CANDIDATES = select_miso_candidates
_BATCH8_ORIGINAL_BUILD_OI_WALL_SUMMARY = build_oi_wall_summary
_BATCH8_ORIGINAL_BUILD_MISO_STRIKE_SURFACE = build_miso_strike_surface
_BATCH8_ORIGINAL_BUILD_CLASSIC_STRIKE_SURFACE = build_classic_strike_surface
_BATCH8_ORIGINAL_BUILD_STRIKE_LADDER_SURFACE = build_strike_ladder_surface


def _batch8_readiness(
    *,
    dhan_context: Mapping[str, Any] | None,
    futures_features: Mapping[str, Any] | None = None,
    selected_features: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    rows = normalize_strike_ladder_rows(dhan_context)
    reference = _atm_reference(
        dhan_context=dhan_context,
        futures_features=futures_features,
        selected_features=selected_features,
    )
    ladder_present = bool(rows)
    atm_reference_present = reference is not None
    wall_computable = bool(ladder_present and atm_reference_present)
    return {
        "ladder_present": ladder_present,
        "atm_reference_present": atm_reference_present,
        "wall_computable": wall_computable,
    }


def select_miso_candidates(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH8_ORIGINAL_SELECT_MISO_CANDIDATES(*args, **kwargs)
    readiness = _batch8_readiness(dhan_context=kwargs.get("dhan_context"))
    out.update(readiness)
    out["present"] = bool(out.get("present") and readiness["ladder_present"] and readiness["atm_reference_present"])
    return out


def build_oi_wall_summary(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH8_ORIGINAL_BUILD_OI_WALL_SUMMARY(*args, **kwargs)
    readiness = _batch8_readiness(
        dhan_context=kwargs.get("dhan_context"),
        futures_features=kwargs.get("futures_features"),
        selected_features=kwargs.get("selected_features"),
    )
    call_wall = out.get("call_wall")
    put_wall = out.get("put_wall")
    oi_wall_ready = bool(readiness["wall_computable"] and (call_wall is not None or put_wall is not None))
    out.update(readiness)
    out["oi_wall_ready"] = oi_wall_ready
    if not oi_wall_ready:
        out["near_any_wall"] = False
    return out


def build_miso_strike_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH8_ORIGINAL_BUILD_MISO_STRIKE_SURFACE(*args, **kwargs)
    wall_summary = out.get("oi_wall_summary") if isinstance(out.get("oi_wall_summary"), Mapping) else {}
    readiness = _batch8_readiness(
        dhan_context=kwargs.get("dhan_context"),
        futures_features=kwargs.get("futures_features"),
        selected_features=kwargs.get("selected_features"),
    )
    out.update(readiness)
    out["oi_wall_ready"] = bool(wall_summary.get("oi_wall_ready", False))
    out["chain_context_ready"] = bool(readiness["ladder_present"] and readiness["atm_reference_present"])
    out["present"] = bool(out.get("present") and out["chain_context_ready"])
    return out


def build_classic_strike_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH8_ORIGINAL_BUILD_CLASSIC_STRIKE_SURFACE(*args, **kwargs)
    wall_summary = out.get("oi_wall_summary") if isinstance(out.get("oi_wall_summary"), Mapping) else {}
    readiness = _batch8_readiness(
        dhan_context=kwargs.get("dhan_context"),
        futures_features=kwargs.get("futures_features"),
        selected_features=kwargs.get("selected_features"),
    )
    out.update(readiness)
    out["oi_wall_ready"] = bool(wall_summary.get("oi_wall_ready", False))
    return out


def build_strike_ladder_surface(*args: Any, **kwargs: Any) -> dict[str, Any]:
    out = _BATCH8_ORIGINAL_BUILD_STRIKE_LADDER_SURFACE(*args, **kwargs)
    readiness = _batch8_readiness(dhan_context=kwargs.get("dhan_context"))
    out.update(readiness)
    return out
# ===== BATCH8_SHARED_CORE_GUARDS END =====
