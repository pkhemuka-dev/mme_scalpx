"""
app/mme_scalpx/replay/comparison_artifacts.py

Deterministic baseline-vs-shadow comparison artifact builder for replay studies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .metrics import ComparisonMetricsBundle, comparison_metrics_to_dict


class ReplayComparisonArtifactsError(RuntimeError):
    """Base error for comparison artifact handling."""


class ReplayComparisonArtifactsValidationError(ReplayComparisonArtifactsError):
    """Raised when comparison artifact inputs are invalid."""


@dataclass(frozen=True, slots=True)
class ComparisonArtifacts:
    candidate_diff_rows: tuple[dict[str, Any], ...]
    blocker_diff: dict[str, Any]
    economics_diff: dict[str, Any]
    side_split: dict[str, Any]
    put_leg_focus: dict[str, Any]
    differential_report: dict[str, Any]


def build_comparison_artifacts(
    *,
    baseline_frames: Iterable[Mapping[str, Any]],
    shadow_frames: Iterable[Mapping[str, Any]],
    metrics_bundle: ComparisonMetricsBundle,
    baseline_label: str = "baseline_locked",
    shadow_label: str = "shadow",
) -> ComparisonArtifacts:
    baseline_index = _index_frames(baseline_frames, context="baseline_frames")
    shadow_index = _index_frames(shadow_frames, context="shadow_frames")

    baseline_ids = set(baseline_index)
    shadow_ids = set(shadow_index)
    shared_ids = sorted(baseline_ids & shadow_ids)

    candidate_rows: list[dict[str, Any]] = []
    newly_admitted_ids: list[str] = []

    for frame_id in shared_ids:
        baseline = baseline_index[frame_id]
        shadow = shadow_index[frame_id]

        baseline_candidate = _as_bool(baseline["candidate"], "baseline.candidate")
        shadow_candidate = _as_bool(shadow["candidate"], "shadow.candidate")

        changed = baseline_candidate != shadow_candidate
        newly_admitted = (not baseline_candidate) and shadow_candidate
        removed_in_shadow = baseline_candidate and (not shadow_candidate)

        if newly_admitted:
            newly_admitted_ids.append(frame_id)

        if changed or newly_admitted:
            candidate_rows.append(
                {
                    "frame_id": frame_id,
                    "baseline_candidate": baseline_candidate,
                    "shadow_candidate": shadow_candidate,
                    "newly_admitted_in_shadow": newly_admitted,
                    "removed_in_shadow": removed_in_shadow,
                    "baseline_side": _normalized_side(baseline),
                    "shadow_side": _normalized_side(shadow),
                    "baseline_leg": _normalized_leg(baseline),
                    "shadow_leg": _normalized_leg(shadow),
                    "baseline_blocker": _normalized_blocker(baseline),
                    "shadow_blocker": _normalized_blocker(shadow),
                    "baseline_regime_pass": _as_bool(baseline["regime_pass"], "baseline.regime_pass"),
                    "shadow_regime_pass": _as_bool(shadow["regime_pass"], "shadow.regime_pass"),
                    "baseline_economics_valid": _as_bool(
                        baseline["economics_valid"], "baseline.economics_valid"
                    ),
                    "shadow_economics_valid": _as_bool(
                        shadow["economics_valid"], "shadow.economics_valid"
                    ),
                    "baseline_ambiguity": _as_bool(baseline["ambiguity"], "baseline.ambiguity"),
                    "shadow_ambiguity": _as_bool(shadow["ambiguity"], "shadow.ambiguity"),
                }
            )

    blocker_diff = _build_blocker_diff(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
        metrics_bundle=metrics_bundle,
    )
    economics_diff = _build_economics_diff(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
        metrics_bundle=metrics_bundle,
    )
    side_split = _build_side_split(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
        newly_admitted_ids=newly_admitted_ids,
    )
    put_leg_focus = _build_put_leg_focus(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
        newly_admitted_ids=newly_admitted_ids,
    )
    differential_report = _build_differential_report(
        baseline_label=baseline_label,
        shadow_label=shadow_label,
        metrics_bundle=metrics_bundle,
        newly_admitted_ids=newly_admitted_ids,
        blocker_diff=blocker_diff,
        economics_diff=economics_diff,
        side_split=side_split,
        put_leg_focus=put_leg_focus,
    )

    return ComparisonArtifacts(
        candidate_diff_rows=tuple(candidate_rows),
        blocker_diff=blocker_diff,
        economics_diff=economics_diff,
        side_split=side_split,
        put_leg_focus=put_leg_focus,
        differential_report=differential_report,
    )


def comparison_artifacts_to_dict(artifacts: ComparisonArtifacts) -> dict[str, Any]:
    return {
        "candidate_diff_rows": list(artifacts.candidate_diff_rows),
        "blocker_diff": artifacts.blocker_diff,
        "economics_diff": artifacts.economics_diff,
        "side_split": artifacts.side_split,
        "put_leg_focus": artifacts.put_leg_focus,
        "differential_report": artifacts.differential_report,
    }


def _build_blocker_diff(
    *,
    baseline_index: Mapping[str, Mapping[str, Any]],
    shadow_index: Mapping[str, Mapping[str, Any]],
    metrics_bundle: ComparisonMetricsBundle,
) -> dict[str, Any]:
    shared_ids = sorted(set(baseline_index) & set(shadow_index))

    relocation_rows: list[dict[str, Any]] = []
    for frame_id in shared_ids:
        baseline_blocker = _normalized_blocker(baseline_index[frame_id])
        shadow_blocker = _normalized_blocker(shadow_index[frame_id])
        if baseline_blocker != shadow_blocker:
            relocation_rows.append(
                {
                    "frame_id": frame_id,
                    "baseline_blocker": baseline_blocker,
                    "shadow_blocker": shadow_blocker,
                }
            )

    return {
        "baseline_blocker_mix": dict(sorted(metrics_bundle.blocker_mix_baseline.items())),
        "shadow_blocker_mix": dict(sorted(metrics_bundle.blocker_mix_shadow.items())),
        "blocker_relocation_rows": relocation_rows,
        "expected_regime_improvement_signal": (
            metrics_bundle.shadow_regime_pass_count
            - metrics_bundle.baseline_regime_pass_count
        ),
    }


def _build_economics_diff(
    *,
    baseline_index: Mapping[str, Mapping[str, Any]],
    shadow_index: Mapping[str, Mapping[str, Any]],
    metrics_bundle: ComparisonMetricsBundle,
) -> dict[str, Any]:
    shared_ids = sorted(set(baseline_index) & set(shadow_index))

    flips_to_valid: list[str] = []
    reward_cost_relief_ids: list[str] = []

    for frame_id in shared_ids:
        baseline_econ = _as_bool(baseline_index[frame_id]["economics_valid"], "baseline.economics_valid")
        shadow_econ = _as_bool(shadow_index[frame_id]["economics_valid"], "shadow.economics_valid")

        if (not baseline_econ) and shadow_econ:
            flips_to_valid.append(frame_id)

        if _is_reward_cost_fail(baseline_index[frame_id]) and not _is_reward_cost_fail(shadow_index[frame_id]):
            reward_cost_relief_ids.append(frame_id)

    return {
        "baseline_economics_valid_count": metrics_bundle.baseline_economics_valid_count,
        "shadow_economics_valid_count": metrics_bundle.shadow_economics_valid_count,
        "baseline_economics_source_insufficient_count": metrics_bundle.baseline_economics_source_insufficient_count,
        "shadow_economics_source_insufficient_count": metrics_bundle.shadow_economics_source_insufficient_count,
        "economics_flip_to_valid_count": len(flips_to_valid),
        "economics_flip_to_valid_frame_ids": flips_to_valid,
        "reward_cost_fail_count_baseline": metrics_bundle.reward_cost_fail_count_baseline,
        "reward_cost_fail_count_shadow": metrics_bundle.reward_cost_fail_count_shadow,
        "reward_cost_relief_count": len(reward_cost_relief_ids),
        "reward_cost_relief_frame_ids": reward_cost_relief_ids,
    }


def _build_side_split(
    *,
    baseline_index: Mapping[str, Mapping[str, Any]],
    shadow_index: Mapping[str, Mapping[str, Any]],
    newly_admitted_ids: list[str],
) -> dict[str, Any]:
    baseline_candidate_side_counts = _candidate_side_counts(baseline_index.values())
    shadow_candidate_side_counts = _candidate_side_counts(shadow_index.values())
    new_shadow_side_counts = _candidate_side_counts(shadow_index[frame_id] for frame_id in newly_admitted_ids)

    return {
        "baseline_candidate_side_counts": baseline_candidate_side_counts,
        "shadow_candidate_side_counts": shadow_candidate_side_counts,
        "new_shadow_side_counts": new_shadow_side_counts,
    }


def _build_put_leg_focus(
    *,
    baseline_index: Mapping[str, Mapping[str, Any]],
    shadow_index: Mapping[str, Mapping[str, Any]],
    newly_admitted_ids: list[str],
) -> dict[str, Any]:
    baseline_put_leg_counts = _put_leg_counts(baseline_index.values())
    shadow_put_leg_counts = _put_leg_counts(shadow_index.values())
    new_shadow_put_leg_counts = _put_leg_counts(shadow_index[frame_id] for frame_id in newly_admitted_ids)

    return {
        "baseline_put_leg_counts": baseline_put_leg_counts,
        "shadow_put_leg_counts": shadow_put_leg_counts,
        "new_shadow_put_leg_counts": new_shadow_put_leg_counts,
        "primary_focus_new_shadow_count": new_shadow_put_leg_counts.get("PUT_ATM1", 0),
        "secondary_focus_new_shadow_count": new_shadow_put_leg_counts.get("PUT_ATM", 0),
    }


def _build_differential_report(
    *,
    baseline_label: str,
    shadow_label: str,
    metrics_bundle: ComparisonMetricsBundle,
    newly_admitted_ids: list[str],
    blocker_diff: Mapping[str, Any],
    economics_diff: Mapping[str, Any],
    side_split: Mapping[str, Any],
    put_leg_focus: Mapping[str, Any],
) -> dict[str, Any]:
    shadow_candidate_gain = (
        metrics_bundle.shadow_candidate_count - metrics_bundle.baseline_candidate_count
    )
    shadow_put_gain = (
        metrics_bundle.shadow_put_candidate_count - metrics_bundle.baseline_put_candidate_count
    )

    return {
        "baseline_label": baseline_label,
        "shadow_label": shadow_label,
        "summary": {
            "shadow_candidate_gain": shadow_candidate_gain,
            "shadow_put_gain": shadow_put_gain,
            "newly_admitted_shadow_frames": len(newly_admitted_ids),
            "frame_alignment_mismatch_count": metrics_bundle.frame_alignment_mismatch_count,
            "ambiguity_rate_baseline": metrics_bundle.ambiguity_rate_baseline,
            "ambiguity_rate_shadow": metrics_bundle.ambiguity_rate_shadow,
        },
        "expected_signal_checks": {
            "regime_improved": metrics_bundle.shadow_regime_pass_count >= metrics_bundle.baseline_regime_pass_count,
            "economics_improved": metrics_bundle.shadow_economics_valid_count >= metrics_bundle.baseline_economics_valid_count,
            "baseline_economics_source_insufficient_count": metrics_bundle.baseline_economics_source_insufficient_count,
            "shadow_economics_source_insufficient_count": metrics_bundle.shadow_economics_source_insufficient_count,
            "economics_source_insufficiency_changed": (
                metrics_bundle.shadow_economics_source_insufficient_count
                != metrics_bundle.baseline_economics_source_insufficient_count
            ),
            "reward_cost_fail_reduced": (
                metrics_bundle.reward_cost_fail_count_shadow
                <= metrics_bundle.reward_cost_fail_count_baseline
            ),
            "put_focus_preserved": (
                put_leg_focus.get("primary_focus_new_shadow_count", 0)
                + put_leg_focus.get("secondary_focus_new_shadow_count", 0)
            ) > 0,
        },
        "blocker_diff": dict(blocker_diff),
        "economics_diff": dict(economics_diff),
        "side_split": dict(side_split),
        "put_leg_focus": dict(put_leg_focus),
        "metrics": comparison_metrics_to_dict(metrics_bundle),
    }


def _index_frames(
    frames: Iterable[Mapping[str, Any]],
    *,
    context: str,
) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for position, frame in enumerate(frames):
        if not isinstance(frame, Mapping):
            raise ReplayComparisonArtifactsValidationError(f"{context}[{position}] must be a mapping")
        frame_id = frame.get("frame_id")
        if not isinstance(frame_id, str) or not frame_id.strip():
            raise ReplayComparisonArtifactsValidationError(
                f"{context}[{position}].frame_id must be a non-empty string"
            )
        normalized = frame_id.strip()
        if normalized in indexed:
            raise ReplayComparisonArtifactsValidationError(
                f"{context} contains duplicate frame_id: {normalized}"
            )
        indexed[normalized] = frame
    return indexed


def _as_bool(value: Any, context: str) -> bool:
    if not isinstance(value, bool):
        raise ReplayComparisonArtifactsValidationError(f"{context} must be bool")
    return value


def _normalized_side(frame: Mapping[str, Any]) -> str:
    side = frame.get("side")
    if not isinstance(side, str) or not side.strip():
        raise ReplayComparisonArtifactsValidationError("frame.side must be non-empty string")
    return side.strip().upper()


def _normalized_leg(frame: Mapping[str, Any]) -> str:
    leg = frame.get("leg")
    if not isinstance(leg, str) or not leg.strip():
        raise ReplayComparisonArtifactsValidationError("frame.leg must be non-empty string")
    return leg.strip().upper()


def _normalized_blocker(frame: Mapping[str, Any]) -> str | None:
    blocker = frame.get("blocker")
    if blocker is None:
        return None
    if not isinstance(blocker, str):
        raise ReplayComparisonArtifactsValidationError("frame.blocker must be string or null")
    normalized = blocker.strip()
    return normalized or None


def _is_reward_cost_fail(frame: Mapping[str, Any]) -> bool:
    reward_cost_valid = frame.get("reward_cost_valid")
    blocker = frame.get("blocker")

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


def _candidate_side_counts(frames: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for frame in frames:
        candidate = frame.get("candidate")
        if candidate is not True:
            continue
        side = _normalized_side(frame)
        counts[side] = counts.get(side, 0) + 1
    return dict(sorted(counts.items()))


def _put_leg_counts(frames: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for frame in frames:
        if frame.get("candidate") is not True:
            continue
        if _normalized_side(frame) != "PUT":
            continue
        leg = _normalized_leg(frame)
        counts[leg] = counts.get(leg, 0) + 1
    return dict(sorted(counts.items()))


__all__ = [
    "ComparisonArtifacts",
    "ReplayComparisonArtifactsError",
    "ReplayComparisonArtifactsValidationError",
    "build_comparison_artifacts",
    "comparison_artifacts_to_dict",
]
