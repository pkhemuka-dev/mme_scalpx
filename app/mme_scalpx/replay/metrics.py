"""
app/mme_scalpx/replay/metrics.py

Replay comparison metrics for baseline-vs-shadow studies.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


class ReplayMetricsError(RuntimeError):
    """Base error for replay metrics handling."""


class ReplayMetricsValidationError(ReplayMetricsError):
    """Raised when replay metric inputs are structurally invalid."""


@dataclass(frozen=True, slots=True)
class ComparisonMetricsBundle:
    healthy_frame_count: int
    baseline_regime_pass_count: int
    shadow_regime_pass_count: int
    baseline_economics_valid_count: int
    shadow_economics_valid_count: int
    baseline_economics_source_insufficient_count: int
    shadow_economics_source_insufficient_count: int
    baseline_candidate_count: int
    shadow_candidate_count: int
    baseline_put_candidate_count: int
    shadow_put_candidate_count: int
    baseline_put_atm_count: int
    shadow_put_atm_count: int
    baseline_put_atm1_candidate_count: int
    shadow_put_atm1_candidate_count: int
    newly_admitted_shadow_frames: int
    new_shadow_put_atm_count: int
    new_shadow_put_atm1_count: int
    blocker_mix_baseline: dict[str, int]
    blocker_mix_shadow: dict[str, int]
    ambiguity_rate_baseline: float
    ambiguity_rate_shadow: float
    reward_cost_fail_count_baseline: int
    reward_cost_fail_count_shadow: int
    frame_alignment_mismatch_count: int


def compute_comparison_metrics(
    *,
    baseline_frames: Iterable[Mapping[str, Any]],
    shadow_frames: Iterable[Mapping[str, Any]],
) -> ComparisonMetricsBundle:
    baseline_index = _index_frames(baseline_frames, context="baseline_frames")
    shadow_index = _index_frames(shadow_frames, context="shadow_frames")

    baseline_ids = set(baseline_index)
    shadow_ids = set(shadow_index)

    shared_ids = sorted(baseline_ids & shadow_ids)
    mismatch_count = len(baseline_ids ^ shadow_ids)

    baseline_shared = [baseline_index[frame_id] for frame_id in shared_ids]
    shadow_shared = [shadow_index[frame_id] for frame_id in shared_ids]

    healthy_frame_count = sum(
        1
        for b_frame, s_frame in zip(baseline_shared, shadow_shared)
        if _as_bool(b_frame["healthy"], "baseline.healthy")
        and _as_bool(s_frame["healthy"], "shadow.healthy")
    )

    baseline_regime_pass_count = sum(
        1 for frame in baseline_shared if _as_bool(frame["regime_pass"], "baseline.regime_pass")
    )
    shadow_regime_pass_count = sum(
        1 for frame in shadow_shared if _as_bool(frame["regime_pass"], "shadow.regime_pass")
    )

    baseline_economics_valid_count = sum(
        1 for frame in baseline_shared if _as_bool(frame["economics_valid"], "baseline.economics_valid")
    )
    shadow_economics_valid_count = sum(
        1 for frame in shadow_shared if _as_bool(frame["economics_valid"], "shadow.economics_valid")
    )
    baseline_economics_source_insufficient_count = sum(
        1 for frame in baseline_shared if frame.get("economics_source_insufficient") is True
    )
    shadow_economics_source_insufficient_count = sum(
        1 for frame in shadow_shared if frame.get("economics_source_insufficient") is True
    )

    baseline_candidate_count = sum(
        1 for frame in baseline_shared if _as_bool(frame["candidate"], "baseline.candidate")
    )
    shadow_candidate_count = sum(
        1 for frame in shadow_shared if _as_bool(frame["candidate"], "shadow.candidate")
    )

    baseline_put_candidate_count = sum(1 for frame in baseline_shared if _is_put_candidate(frame))
    shadow_put_candidate_count = sum(1 for frame in shadow_shared if _is_put_candidate(frame))

    baseline_put_atm_count = sum(
        1 for frame in baseline_shared if _is_put_leg_candidate(frame, "PUT_ATM")
    )
    shadow_put_atm_count = sum(
        1 for frame in shadow_shared if _is_put_leg_candidate(frame, "PUT_ATM")
    )

    baseline_put_atm1_candidate_count = sum(
        1 for frame in baseline_shared if _is_put_leg_candidate(frame, "PUT_ATM1")
    )
    shadow_put_atm1_candidate_count = sum(
        1 for frame in shadow_shared if _is_put_leg_candidate(frame, "PUT_ATM1")
    )

    newly_admitted_ids = [
        frame_id
        for frame_id in shared_ids
        if not _as_bool(baseline_index[frame_id]["candidate"], "baseline.candidate")
        and _as_bool(shadow_index[frame_id]["candidate"], "shadow.candidate")
    ]

    newly_admitted_shadow_frames = len(newly_admitted_ids)

    new_shadow_put_atm_count = sum(
        1 for frame_id in newly_admitted_ids if _is_put_leg_candidate(shadow_index[frame_id], "PUT_ATM")
    )
    new_shadow_put_atm1_count = sum(
        1 for frame_id in newly_admitted_ids if _is_put_leg_candidate(shadow_index[frame_id], "PUT_ATM1")
    )

    blocker_mix_baseline = _blocker_mix(baseline_shared)
    blocker_mix_shadow = _blocker_mix(shadow_shared)

    ambiguity_rate_baseline = _ambiguity_rate(baseline_shared)
    ambiguity_rate_shadow = _ambiguity_rate(shadow_shared)

    reward_cost_fail_count_baseline = sum(1 for frame in baseline_shared if _is_reward_cost_fail(frame))
    reward_cost_fail_count_shadow = sum(1 for frame in shadow_shared if _is_reward_cost_fail(frame))

    return ComparisonMetricsBundle(
        healthy_frame_count=healthy_frame_count,
        baseline_regime_pass_count=baseline_regime_pass_count,
        shadow_regime_pass_count=shadow_regime_pass_count,
        baseline_economics_valid_count=baseline_economics_valid_count,
        shadow_economics_valid_count=shadow_economics_valid_count,
        baseline_economics_source_insufficient_count=baseline_economics_source_insufficient_count,
        shadow_economics_source_insufficient_count=shadow_economics_source_insufficient_count,
        baseline_candidate_count=baseline_candidate_count,
        shadow_candidate_count=shadow_candidate_count,
        baseline_put_candidate_count=baseline_put_candidate_count,
        shadow_put_candidate_count=shadow_put_candidate_count,
        baseline_put_atm_count=baseline_put_atm_count,
        shadow_put_atm_count=shadow_put_atm_count,
        baseline_put_atm1_candidate_count=baseline_put_atm1_candidate_count,
        shadow_put_atm1_candidate_count=shadow_put_atm1_candidate_count,
        newly_admitted_shadow_frames=newly_admitted_shadow_frames,
        new_shadow_put_atm_count=new_shadow_put_atm_count,
        new_shadow_put_atm1_count=new_shadow_put_atm1_count,
        blocker_mix_baseline=blocker_mix_baseline,
        blocker_mix_shadow=blocker_mix_shadow,
        ambiguity_rate_baseline=ambiguity_rate_baseline,
        ambiguity_rate_shadow=ambiguity_rate_shadow,
        reward_cost_fail_count_baseline=reward_cost_fail_count_baseline,
        reward_cost_fail_count_shadow=reward_cost_fail_count_shadow,
        frame_alignment_mismatch_count=mismatch_count,
    )


def comparison_metrics_to_dict(bundle: ComparisonMetricsBundle) -> dict[str, Any]:
    return {
        "healthy_frame_count": bundle.healthy_frame_count,
        "baseline_regime_pass_count": bundle.baseline_regime_pass_count,
        "shadow_regime_pass_count": bundle.shadow_regime_pass_count,
        "baseline_economics_valid_count": bundle.baseline_economics_valid_count,
        "shadow_economics_valid_count": bundle.shadow_economics_valid_count,
        "baseline_economics_source_insufficient_count": bundle.baseline_economics_source_insufficient_count,
        "shadow_economics_source_insufficient_count": bundle.shadow_economics_source_insufficient_count,
        "baseline_candidate_count": bundle.baseline_candidate_count,
        "shadow_candidate_count": bundle.shadow_candidate_count,
        "baseline_put_candidate_count": bundle.baseline_put_candidate_count,
        "shadow_put_candidate_count": bundle.shadow_put_candidate_count,
        "baseline_put_atm_count": bundle.baseline_put_atm_count,
        "shadow_put_atm_count": bundle.shadow_put_atm_count,
        "baseline_put_atm1_candidate_count": bundle.baseline_put_atm1_candidate_count,
        "shadow_put_atm1_candidate_count": bundle.shadow_put_atm1_candidate_count,
        "newly_admitted_shadow_frames": bundle.newly_admitted_shadow_frames,
        "new_shadow_put_atm_count": bundle.new_shadow_put_atm_count,
        "new_shadow_put_atm1_count": bundle.new_shadow_put_atm1_count,
        "blocker_mix_baseline": dict(sorted(bundle.blocker_mix_baseline.items())),
        "blocker_mix_shadow": dict(sorted(bundle.blocker_mix_shadow.items())),
        "ambiguity_rate_baseline": bundle.ambiguity_rate_baseline,
        "ambiguity_rate_shadow": bundle.ambiguity_rate_shadow,
        "reward_cost_fail_count_baseline": bundle.reward_cost_fail_count_baseline,
        "reward_cost_fail_count_shadow": bundle.reward_cost_fail_count_shadow,
        "frame_alignment_mismatch_count": bundle.frame_alignment_mismatch_count,
    }


def _index_frames(
    frames: Iterable[Mapping[str, Any]],
    *,
    context: str,
) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for position, frame in enumerate(frames):
        if not isinstance(frame, Mapping):
            raise ReplayMetricsValidationError(f"{context}[{position}] must be a mapping")
        frame_id = frame.get("frame_id")
        if not isinstance(frame_id, str) or not frame_id.strip():
            raise ReplayMetricsValidationError(
                f"{context}[{position}].frame_id must be a non-empty string"
            )
        normalized_id = frame_id.strip()
        if normalized_id in indexed:
            raise ReplayMetricsValidationError(
                f"{context} contains duplicate frame_id: {normalized_id}"
            )
        _validate_frame_shape(frame, context=f"{context}[{normalized_id}]")
        indexed[normalized_id] = frame
    return indexed


def _validate_frame_shape(frame: Mapping[str, Any], *, context: str) -> None:
    required_keys = (
        "frame_id",
        "healthy",
        "regime_pass",
        "economics_valid",
        "candidate",
        "side",
        "leg",
        "blocker",
        "ambiguity",
        "reward_cost_valid",
    )
    for key in required_keys:
        if key not in frame:
            raise ReplayMetricsValidationError(f"{context} missing required key: {key}")

    _as_bool(frame["healthy"], f"{context}.healthy")
    _as_bool(frame["regime_pass"], f"{context}.regime_pass")
    _as_bool(frame["economics_valid"], f"{context}.economics_valid")
    _as_bool(frame["candidate"], f"{context}.candidate")
    _as_bool(frame["ambiguity"], f"{context}.ambiguity")

    side = frame["side"]
    if not isinstance(side, str) or not side.strip():
        raise ReplayMetricsValidationError(f"{context}.side must be a non-empty string")

    leg = frame["leg"]
    if not isinstance(leg, str) or not leg.strip():
        raise ReplayMetricsValidationError(f"{context}.leg must be a non-empty string")

    blocker = frame["blocker"]
    if blocker is not None and not isinstance(blocker, str):
        raise ReplayMetricsValidationError(f"{context}.blocker must be string or null")

    reward_cost_valid = frame["reward_cost_valid"]
    if reward_cost_valid is not None and not isinstance(reward_cost_valid, bool):
        raise ReplayMetricsValidationError(f"{context}.reward_cost_valid must be bool or null")


def _as_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise ReplayMetricsValidationError(f"{context} must be bool")
    return value


def _normalized_side(frame: Mapping[str, Any]) -> str:
    side = frame["side"]
    assert isinstance(side, str)
    return side.strip().upper()


def _normalized_leg(frame: Mapping[str, Any]) -> str:
    leg = frame["leg"]
    assert isinstance(leg, str)
    return leg.strip().upper()


def _is_put_candidate(frame: Mapping[str, Any]) -> bool:
    return _as_bool(frame["candidate"], "candidate") and _normalized_side(frame) == "PUT"


def _is_put_leg_candidate(frame: Mapping[str, Any], leg_name: str) -> bool:
    return _is_put_candidate(frame) and _normalized_leg(frame) == leg_name.upper()


def _blocker_mix(frames: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for frame in frames:
        blocker = frame["blocker"]
        if blocker is None:
            continue
        assert isinstance(blocker, str)
        normalized = blocker.strip()
        if not normalized:
            continue
        counter[normalized] += 1
    return dict(sorted(counter.items()))


def _ambiguity_rate(frames: Iterable[Mapping[str, Any]]) -> float:
    candidate_frames = [frame for frame in frames if _as_bool(frame["candidate"], "candidate")]
    if not candidate_frames:
        return 0.0
    ambiguous = sum(1 for frame in candidate_frames if _as_bool(frame["ambiguity"], "ambiguity"))
    return ambiguous / len(candidate_frames)


def _is_reward_cost_fail(frame: Mapping[str, Any]) -> bool:
    blocker = frame["blocker"]
    reward_cost_valid = frame["reward_cost_valid"]
    if reward_cost_valid is True:
        return False
    if reward_cost_valid is False:
        return True
    if isinstance(blocker, str) and blocker.strip().lower() in {
        "reward_cost_fail",
        "reward_cost_invalid",
        "economics_reward_cost_fail",
    }:
        return True
    return False


__all__ = [
    "ComparisonMetricsBundle",
    "ReplayMetricsError",
    "ReplayMetricsValidationError",
    "comparison_metrics_to_dict",
    "compute_comparison_metrics",
]
