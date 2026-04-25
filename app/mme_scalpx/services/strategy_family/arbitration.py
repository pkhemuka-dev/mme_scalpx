from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/arbitration.py

Freeze-grade deterministic candidate arbitration for ScalpX MME strategy-family.

Purpose
-------
This module OWNS:
- deterministic ordering of doctrine entry candidates across families/branches
- stable tie-break logic for candidate arbitration
- canonical arbitration result packaging for downstream thin strategy
  orchestration

This module DOES NOT own:
- Redis reads or writes
- feature computation
- eligibility evaluation
- doctrine scoring logic
- cooldown state mutation
- decision publication
- broker truth
- risk truth

Frozen design law
-----------------
- Arbitration consumes already-built doctrine candidates only.
- It must not mutate candidates.
- It must not invent new family/branch vocabularies.
- It must remain deterministic and replay-safe.
- Candidate ordering must be stable across runs for identical inputs.
- Malformed arbitration metadata must fail fast, not silently degrade.
"""

from dataclasses import dataclass
from typing import Any, Final, Mapping, Sequence

from app.mme_scalpx.core import names as N

from .common import FAMILY_ORDER
from .doctrine_runtime import DoctrineSignalCandidate


# ============================================================================
# Exceptions
# ============================================================================


class ArbitrationError(ValueError):
    """Raised when candidate arbitration input is invalid."""


# ============================================================================
# Typed outputs
# ============================================================================


@dataclass(frozen=True, slots=True)
class RankedCandidate:
    """Candidate plus its frozen arbitration sort components."""

    candidate: DoctrineSignalCandidate
    effective_priority: float
    effective_score: float
    family_rank: int
    branch_rank: int
    doctrine_id: str
    entry_mode: str
    setup_kind: str
    instrument_key: str
    source_event_id: str
    trap_event_id: str
    burst_event_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": {
                "family_id": self.candidate.family_id,
                "doctrine_id": self.candidate.doctrine_id,
                "branch_id": self.candidate.branch_id,
                "side": self.candidate.side,
                "instrument_key": self.candidate.instrument_key,
                "entry_mode": self.candidate.entry_mode,
                "family_runtime_mode": self.candidate.family_runtime_mode,
                "strategy_runtime_mode": self.candidate.strategy_runtime_mode,
                "score": self.candidate.score,
                "priority": self.candidate.priority,
                "setup_kind": self.candidate.setup_kind,
                "target_points": self.candidate.target_points,
                "stop_points": self.candidate.stop_points,
                "tick_size": self.candidate.tick_size,
                "quantity_lots_hint": self.candidate.quantity_lots_hint,
                "source_event_id": self.candidate.source_event_id,
                "trap_event_id": self.candidate.trap_event_id,
                "burst_event_id": self.candidate.burst_event_id,
                "metadata": dict(self.candidate.metadata),
            },
            "effective_priority": self.effective_priority,
            "effective_score": self.effective_score,
            "family_rank": self.family_rank,
            "branch_rank": self.branch_rank,
            "doctrine_id": self.doctrine_id,
            "entry_mode": self.entry_mode,
            "setup_kind": self.setup_kind,
            "instrument_key": self.instrument_key,
            "source_event_id": self.source_event_id,
            "trap_event_id": self.trap_event_id,
            "burst_event_id": self.burst_event_id,
        }


@dataclass(frozen=True, slots=True)
class ArbitrationResult:
    """Deterministic arbitration result over a candidate set."""

    selected: DoctrineSignalCandidate | None
    ranked: tuple[RankedCandidate, ...]

    @property
    def has_selection(self) -> bool:
        return self.selected is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_selection": self.has_selection,
            "selected": (
                None
                if self.selected is None
                else {
                    "family_id": self.selected.family_id,
                    "doctrine_id": self.selected.doctrine_id,
                    "branch_id": self.selected.branch_id,
                    "side": self.selected.side,
                    "instrument_key": self.selected.instrument_key,
                    "entry_mode": self.selected.entry_mode,
                    "family_runtime_mode": self.selected.family_runtime_mode,
                    "strategy_runtime_mode": self.selected.strategy_runtime_mode,
                    "score": self.selected.score,
                    "priority": self.selected.priority,
                    "setup_kind": self.selected.setup_kind,
                    "target_points": self.selected.target_points,
                    "stop_points": self.selected.stop_points,
                    "tick_size": self.selected.tick_size,
                    "quantity_lots_hint": self.selected.quantity_lots_hint,
                    "source_event_id": self.selected.source_event_id,
                    "trap_event_id": self.selected.trap_event_id,
                    "burst_event_id": self.selected.burst_event_id,
                    "metadata": dict(self.selected.metadata),
                }
            ),
            "ranked": [item.to_dict() for item in self.ranked],
        }


# ============================================================================
# Frozen ranking constants
# ============================================================================

_BRANCH_ORDER: Final[tuple[str, ...]] = (
    N.BRANCH_CALL,
    N.BRANCH_PUT,
)

_METADATA_PRIORITY_KEYS: Final[tuple[str, ...]] = (
    "arbitration_priority",
    "priority",
    "candidate_priority",
)

_METADATA_SCORE_KEYS: Final[tuple[str, ...]] = (
    "arbitration_score",
    "candidate_score",
    "score",
)


# ============================================================================
# Internal helpers
# ============================================================================


def _fail(message: str) -> None:
    raise ArbitrationError(message)


def _require(condition: bool, message: str) -> None:
    if not condition:
        _fail(message)


def _non_empty_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        _fail(f"{field_name} must be str")
    text = value.strip()
    if not text:
        _fail(f"{field_name} must be non-empty")
    return text


def _optional_clean_str(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return str(value)
    return value.strip()


def _strict_float(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or value is None:
        _fail(f"{field_name} must be a finite float-compatible value")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ArbitrationError(f"{field_name} must be float-compatible") from exc
    if out != out or out in (float("inf"), float("-inf")):
        _fail(f"{field_name} must be finite")
    return out


def _metadata(candidate: DoctrineSignalCandidate) -> Mapping[str, Any]:
    return dict(candidate.metadata)


def _family_rank(family_id: str) -> int:
    try:
        return FAMILY_ORDER.index(family_id)
    except ValueError:
        return len(FAMILY_ORDER) + 1


def _branch_rank(branch_id: str) -> int:
    try:
        return _BRANCH_ORDER.index(branch_id)
    except ValueError:
        return len(_BRANCH_ORDER) + 1


def _expected_side_for_branch(branch_id: str) -> str:
    if branch_id == N.BRANCH_CALL:
        return N.SIDE_CALL
    if branch_id == N.BRANCH_PUT:
        return N.SIDE_PUT
    _fail(f"unsupported branch_id: {branch_id!r}")


def _effective_priority(candidate: DoctrineSignalCandidate) -> float:
    meta = _metadata(candidate)
    for key in _METADATA_PRIORITY_KEYS:
        if key in meta and meta[key] is not None:
            return _strict_float(meta[key], f"candidate.metadata[{key!r}]")
    return _strict_float(candidate.priority, "candidate.priority")


def _effective_score(candidate: DoctrineSignalCandidate) -> float:
    meta = _metadata(candidate)
    for key in _METADATA_SCORE_KEYS:
        if key in meta and meta[key] is not None:
            return _strict_float(meta[key], f"candidate.metadata[{key!r}]")
    return _strict_float(candidate.score, "candidate.score")


def _ranked_candidate(candidate: DoctrineSignalCandidate) -> RankedCandidate:
    return RankedCandidate(
        candidate=candidate,
        effective_priority=_effective_priority(candidate),
        effective_score=_effective_score(candidate),
        family_rank=_family_rank(candidate.family_id),
        branch_rank=_branch_rank(candidate.branch_id),
        doctrine_id=_non_empty_str(candidate.doctrine_id, "candidate.doctrine_id"),
        entry_mode=_non_empty_str(candidate.entry_mode, "candidate.entry_mode"),
        setup_kind=_optional_clean_str(candidate.setup_kind),
        instrument_key=_non_empty_str(candidate.instrument_key, "candidate.instrument_key"),
        source_event_id=_optional_clean_str(candidate.source_event_id),
        trap_event_id=_optional_clean_str(candidate.trap_event_id),
        burst_event_id=_optional_clean_str(candidate.burst_event_id),
    )


def _sort_key(
    item: RankedCandidate,
) -> tuple[float, float, int, int, str, str, str, str, str, str, str]:
    return (
        item.effective_priority,
        -item.effective_score,
        item.family_rank,
        item.branch_rank,
        item.doctrine_id,
        item.entry_mode,
        item.setup_kind,
        item.instrument_key,
        item.source_event_id,
        item.trap_event_id,
        item.burst_event_id,
    )


def _validate_candidate(candidate: DoctrineSignalCandidate) -> None:
    family_id = _non_empty_str(candidate.family_id, "candidate.family_id")
    branch_id = _non_empty_str(candidate.branch_id, "candidate.branch_id")
    side = _non_empty_str(candidate.side, "candidate.side")

    _require(
        family_id in FAMILY_ORDER,
        f"candidate.family_id must be in FAMILY_ORDER, got {family_id!r}",
    )
    _require(
        branch_id in _BRANCH_ORDER,
        f"candidate.branch_id must be one of {_BRANCH_ORDER!r}, got {branch_id!r}",
    )
    _require(
        side in (N.SIDE_CALL, N.SIDE_PUT),
        f"candidate.side must be one of {(N.SIDE_CALL, N.SIDE_PUT)!r}, got {side!r}",
    )
    _require(
        side == _expected_side_for_branch(branch_id),
        f"candidate.side {side!r} must match candidate.branch_id {branch_id!r}",
    )
    _non_empty_str(candidate.doctrine_id, "candidate.doctrine_id")
    _non_empty_str(candidate.entry_mode, "candidate.entry_mode")
    _non_empty_str(candidate.instrument_key, "candidate.instrument_key")
    _strict_float(candidate.priority, "candidate.priority")
    _strict_float(candidate.score, "candidate.score")


# ============================================================================
# Public helpers
# ============================================================================


def rank_candidates(
    candidates: Sequence[DoctrineSignalCandidate],
) -> tuple[RankedCandidate, ...]:
    """
    Deterministically rank doctrine candidates.

    Ordering precedence:
    1. effective priority (lower is better)
    2. effective score (higher is better)
    3. family order (FAMILY_ORDER)
    4. branch order (CALL before PUT)
    5. doctrine_id
    6. entry_mode
    7. setup_kind
    8. instrument_key
    9. source_event_id
    10. trap_event_id
    11. burst_event_id
    """
    ranked: list[RankedCandidate] = []
    for candidate in candidates:
        _validate_candidate(candidate)
        ranked.append(_ranked_candidate(candidate))
    return tuple(sorted(ranked, key=_sort_key))


def select_best_candidate(
    candidates: Sequence[DoctrineSignalCandidate],
) -> DoctrineSignalCandidate | None:
    """
    Return the top-ranked candidate or None when no candidates are present.
    """
    ranked = rank_candidates(candidates)
    return ranked[0].candidate if ranked else None


def arbitrate_candidates(
    candidates: Sequence[DoctrineSignalCandidate],
) -> ArbitrationResult:
    """
    Return the full arbitration result including the selected candidate and full
    deterministic ranking.
    """
    ranked = rank_candidates(candidates)
    selected = ranked[0].candidate if ranked else None
    return ArbitrationResult(
        selected=selected,
        ranked=ranked,
    )


__all__ = [
    "ArbitrationError",
    "ArbitrationResult",
    "RankedCandidate",
    "arbitrate_candidates",
    "rank_candidates",
    "select_best_candidate",
]

# =============================================================================
# Batch 11 freeze hardening: activation/arbitration priority semantics
# =============================================================================
#
# Family leaves and activation treat priority as a score: higher is better.
# Keep deterministic tie-breaks unchanged after priority/score.

_BATCH11_ARBITRATION_PRIORITY_SEMANTICS = "higher_priority_is_better"


def _sort_key(
    item: RankedCandidate,
) -> tuple[float, float, int, int, str, str, str, str, str, str, str]:
    return (
        -item.effective_priority,
        -item.effective_score,
        item.family_rank,
        item.branch_rank,
        item.doctrine_id,
        item.entry_mode,
        item.setup_kind,
        item.instrument_key,
        item.source_event_id,
        item.trap_event_id,
        item.burst_event_id,
    )
