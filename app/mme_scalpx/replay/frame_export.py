"""
app/mme_scalpx/replay/frame_export.py

Freeze-grade comparison frame export contract for replay studies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


class ReplayFrameExportError(RuntimeError):
    """Base exception for replay frame export failures."""


class ReplayFrameExportValidationError(ReplayFrameExportError):
    """Raised when a comparison frame or export bundle is invalid."""


@dataclass(frozen=True, slots=True)
class ReplayComparisonFrame:
    """
    Canonical comparison frame row for baseline-vs-shadow replay studies.
    """

    frame_id: str
    healthy: bool | None
    regime_pass: bool | None
    economics_valid: bool | None
    candidate: bool | None
    side: str
    leg: str
    blocker: str | None
    ambiguity: bool
    reward_cost_valid: bool | None


@dataclass(frozen=True, slots=True)
class ReplayFrameExportBundle:
    """
    Canonical exported frame bundle.
    """

    rows: tuple[ReplayComparisonFrame, ...]
    row_count: int


def validate_comparison_frame(frame: ReplayComparisonFrame) -> None:
    if not frame.frame_id.strip():
        raise ReplayFrameExportValidationError("frame_id must be non-empty")
    if not frame.side.strip():
        raise ReplayFrameExportValidationError("side must be non-empty")
    if not frame.leg.strip():
        raise ReplayFrameExportValidationError("leg must be non-empty")
    if frame.blocker is not None and not frame.blocker.strip():
        raise ReplayFrameExportValidationError("blocker must be non-empty when provided")


def comparison_frame_to_dict(frame: ReplayComparisonFrame) -> dict[str, Any]:
    validate_comparison_frame(frame)
    return {
        "frame_id": frame.frame_id,
        "healthy": frame.healthy,
        "regime_pass": frame.regime_pass,
        "economics_valid": frame.economics_valid,
        "candidate": frame.candidate,
        "side": frame.side,
        "leg": frame.leg,
        "blocker": frame.blocker,
        "ambiguity": frame.ambiguity,
        "reward_cost_valid": frame.reward_cost_valid,
    }


def comparison_frames_to_rows(
    frames: Sequence[ReplayComparisonFrame],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for frame in frames:
        validate_comparison_frame(frame)
        if frame.frame_id in seen:
            raise ReplayFrameExportValidationError(
                f"duplicate frame_id in export: {frame.frame_id}"
            )
        seen.add(frame.frame_id)
        rows.append(comparison_frame_to_dict(frame))

    return rows


def build_comparison_frames(
    frames: Iterable[ReplayComparisonFrame],
) -> ReplayFrameExportBundle:
    normalized = tuple(frames)
    rows = comparison_frames_to_rows(normalized)
    return ReplayFrameExportBundle(
        rows=tuple(normalized),
        row_count=len(rows),
    )


__all__ = [
    "ReplayComparisonFrame",
    "ReplayFrameExportBundle",
    "ReplayFrameExportError",
    "ReplayFrameExportValidationError",
    "build_comparison_frames",
    "comparison_frame_to_dict",
    "comparison_frames_to_rows",
    "validate_comparison_frame",
]
