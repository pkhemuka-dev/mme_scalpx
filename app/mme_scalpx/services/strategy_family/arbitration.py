from __future__ import annotations

"""
app/mme_scalpx/strategy_family/arbitration.py

Deterministic family candidate arbitration helpers.

Purpose
-------
This module OWNS:
- deterministic ranking of doctrine entry candidates
- stable tie-break behavior across families and branches

This module DOES NOT own:
- doctrine signal generation
- live publication
- Redis access
"""

from typing import Sequence

from .common import FAMILY_ORDER, safe_float, safe_str
from .doctrine_runtime import DoctrineSignalCandidate


def _family_rank(family_id: str) -> int:
    try:
        return FAMILY_ORDER.index(family_id)
    except ValueError:
        return len(FAMILY_ORDER) + 1


def _branch_rank(branch_id: str) -> int:
    if branch_id == "CALL":
        return 0
    if branch_id == "PUT":
        return 1
    return 9


def _sort_key(candidate: DoctrineSignalCandidate) -> tuple[float, float, int, int, str, str, str, str]:
    meta = dict(candidate.metadata)
    explicit_priority = safe_float(meta.get("arbitration_priority"), candidate.priority)
    explicit_score = safe_float(meta.get("arbitration_score"), candidate.score)
    return (
        explicit_priority,
        -explicit_score,
        _family_rank(candidate.family_id),
        _branch_rank(candidate.branch_id),
        safe_str(candidate.instrument_key),
        safe_str(candidate.source_event_id),
        safe_str(candidate.trap_event_id),
        safe_str(candidate.burst_event_id),
    )


def rank_candidates(candidates: Sequence[DoctrineSignalCandidate]) -> list[DoctrineSignalCandidate]:
    valid = [candidate for candidate in candidates if candidate is not None]
    return sorted(valid, key=_sort_key)


def select_best_candidate(
    candidates: Sequence[DoctrineSignalCandidate],
) -> DoctrineSignalCandidate | None:
    ranked = rank_candidates(candidates)
    return ranked[0] if ranked else None


__all__ = ["rank_candidates", "select_best_candidate"]
