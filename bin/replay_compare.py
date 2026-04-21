#!/usr/bin/env python3
"""
bin/replay_compare.py

Freeze-grade frame-based replay comparison CLI.

This command compares exported baseline/shadow frame files and writes:
- 04_metrics_summary.json
- 05_candidate_diff_report.json
- 06_blocker_diff_report.json
- 07_economics_diff_report.json
- 08_side_split_report.json
- 09_put_leg_focus_report.json
- 11_differential_report.json
- 12_operator_verdict.txt
- profile_snapshot.json
- shadow_override_flattened.json

Optional:
- 20_comparison_summary.json
- 21_comparison_summary.csv
  when baseline/shadow run dirs are supplied

Design note
-----------
This CLI is intentionally frame-based. It does not call differential.py because
the current differential contract is engine/integrity-bundle based rather than
frame-export based.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.metrics import (
    ComparisonMetricsBundle,
    comparison_metrics_to_dict,
    compute_comparison_metrics,
)


class ReplayCompareCliError(RuntimeError):
    """CLI-level replay comparison failure."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay frame comparison CLI")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--shadow-override", required=True)
    parser.add_argument("--baseline-frames", required=True)
    parser.add_argument("--shadow-frames", required=True)
    parser.add_argument("--output-root", required=True)

    parser.add_argument("--baseline-run-dir", default=None)
    parser.add_argument("--shadow-run-dir", default=None)
    parser.add_argument("--comparison-id", default=None)

    return parser.parse_args()


def _load_yaml_mapping(path: str) -> dict[str, Any]:
    source = Path(path).expanduser().resolve()
    if not source.exists():
        raise ReplayCompareCliError(f"yaml file not found: {source}")
    with source.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ReplayCompareCliError(f"yaml root must be mapping: {source}")
    return data


def _load_json_list(path: str, *, label: str) -> list[dict[str, Any]]:
    source = Path(path).expanduser().resolve()
    if not source.exists():
        raise ReplayCompareCliError(f"{label} file not found: {source}")
    with source.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ReplayCompareCliError(f"{label} root must be a list: {source}")
    out: list[dict[str, Any]] = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ReplayCompareCliError(f"{label}[{idx}] must be an object")
        out.append(item)
    return out


def _bool_or_false(value: Any) -> bool:
    return True if value is True else False


def _normalize_metric_frames(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for frame in frames:
        item = dict(frame)

        for key in (
            "candidate",
            "regime_pass",
            "economics_valid",
            "reward_cost_valid",
            "healthy",
            "ambiguity",
        ):
            raw_key = f"{key}_raw"
            if raw_key not in item:
                item[raw_key] = item.get(key)
            item[key] = _bool_or_false(item.get(key))

        normalized.append(item)
    return normalized


def _json_safe_value(value: Any) -> Any:
    from datetime import date, datetime
    from pathlib import Path

    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {
            str(k): _json_safe_value(v)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [_json_safe_value(v) for v in value]
    return str(value)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_safe_value(payload), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _index_by_frame_id(frames: Iterable[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for frame in frames:
        frame_id = frame.get("frame_id")
        if not isinstance(frame_id, str) or not frame_id:
            raise ReplayCompareCliError(f"frame missing non-empty frame_id: {frame!r}")
        index[frame_id] = frame
    return index


def _as_bool(value: Any) -> bool:
    return value is True


def _normalized_side(frame: Mapping[str, Any]) -> str | None:
    side = frame.get("side")
    if side is None:
        return None
    return str(side)


def _normalized_leg(frame: Mapping[str, Any]) -> str | None:
    leg = frame.get("leg")
    if leg is None:
        return None
    return str(leg)


def _is_put_candidate(frame: Mapping[str, Any]) -> bool:
    return _as_bool(frame.get("candidate")) and _normalized_side(frame) == "PUT"


def _is_put_leg_candidate(frame: Mapping[str, Any], leg_name: str) -> bool:
    return _is_put_candidate(frame) and _normalized_leg(frame) == leg_name


def _candidate_side_counts(frames: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for frame in frames:
        if not _as_bool(frame.get("candidate")):
            continue
        side = _normalized_side(frame)
        if side is None:
            continue
        counts[side] = counts.get(side, 0) + 1
    return dict(sorted(counts.items()))


def _put_leg_counts(frames: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for frame in frames:
        if not _is_put_candidate(frame):
            continue
        leg = _normalized_leg(frame)
        if leg is None:
            continue
        counts[leg] = counts.get(leg, 0) + 1
    return dict(sorted(counts.items()))


def _is_reward_cost_fail(frame: Mapping[str, Any]) -> bool:
    rcv = frame.get("reward_cost_valid")
    return rcv is False


def _build_candidate_diff(
    *,
    baseline_index: Mapping[str, Mapping[str, Any]],
    shadow_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    shared_ids = sorted(set(baseline_index) & set(shadow_index))
    newly_admitted = [
        frame_id
        for frame_id in shared_ids
        if not _as_bool(baseline_index[frame_id].get("candidate"))
        and _as_bool(shadow_index[frame_id].get("candidate"))
    ]
    lost = [
        frame_id
        for frame_id in shared_ids
        if _as_bool(baseline_index[frame_id].get("candidate"))
        and not _as_bool(shadow_index[frame_id].get("candidate"))
    ]
    return {
        "newly_admitted_shadow_frames": newly_admitted,
        "lost_shadow_frames": lost,
        "newly_admitted_count": len(newly_admitted),
        "lost_count": len(lost),
    }


def _build_blocker_diff(
    *,
    baseline_index: Mapping[str, Mapping[str, Any]],
    shadow_index: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    shared_ids = sorted(set(baseline_index) & set(shadow_index))
    changed: list[dict[str, Any]] = []
    for frame_id in shared_ids:
        b = baseline_index[frame_id].get("blocker")
        s = shadow_index[frame_id].get("blocker")
        if b != s:
            changed.append(
                {
                    "frame_id": frame_id,
                    "baseline_blocker": b,
                    "shadow_blocker": s,
                }
            )
    return {
        "changed_blocker_count": len(changed),
        "changed_blockers": changed,
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
        b = baseline_index[frame_id]
        s = shadow_index[frame_id]
        if b.get("economics_valid") is False and s.get("economics_valid") is True:
            flips_to_valid.append(frame_id)
        if _is_reward_cost_fail(b) and not _is_reward_cost_fail(s):
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
    return {
        "baseline_candidate_side_counts": _candidate_side_counts(baseline_index.values()),
        "shadow_candidate_side_counts": _candidate_side_counts(shadow_index.values()),
        "new_shadow_side_counts": _candidate_side_counts(
            shadow_index[frame_id] for frame_id in newly_admitted_ids
        ),
    }


def _build_put_leg_focus(
    *,
    baseline_index: Mapping[str, Mapping[str, Any]],
    shadow_index: Mapping[str, Mapping[str, Any]],
    newly_admitted_ids: list[str],
) -> dict[str, Any]:
    baseline_put_leg_counts = _put_leg_counts(baseline_index.values())
    shadow_put_leg_counts = _put_leg_counts(shadow_index.values())
    new_shadow_put_leg_counts = _put_leg_counts(
        shadow_index[frame_id] for frame_id in newly_admitted_ids
    )
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

    expected_signal_checks = {
        "regime_improved": metrics_bundle.shadow_regime_pass_count >= metrics_bundle.baseline_regime_pass_count,
        "economics_comparable": (
            metrics_bundle.baseline_economics_source_insufficient_count == 0
            and metrics_bundle.shadow_economics_source_insufficient_count == 0
        ),
        "economics_improved": (
            metrics_bundle.baseline_economics_source_insufficient_count == 0
            and metrics_bundle.shadow_economics_source_insufficient_count == 0
            and metrics_bundle.shadow_economics_valid_count >= metrics_bundle.baseline_economics_valid_count
        ),
        "baseline_economics_source_insufficient_count": metrics_bundle.baseline_economics_source_insufficient_count,
        "shadow_economics_source_insufficient_count": metrics_bundle.shadow_economics_source_insufficient_count,
        "economics_source_insufficiency_changed": (
            metrics_bundle.shadow_economics_source_insufficient_count
            != metrics_bundle.baseline_economics_source_insufficient_count
        ),
        "reward_cost_fail_reduced": (
            metrics_bundle.baseline_economics_source_insufficient_count == 0
            and metrics_bundle.shadow_economics_source_insufficient_count == 0
            and metrics_bundle.reward_cost_fail_count_shadow <= metrics_bundle.reward_cost_fail_count_baseline
        ),
        "put_focus_preserved": put_leg_focus["primary_focus_new_shadow_count"] >= 0,
    }

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
        "expected_signal_checks": expected_signal_checks,
        "blocker_diff": blocker_diff,
        "economics_diff": economics_diff,
        "side_split": side_split,
        "put_leg_focus": put_leg_focus,
    }


def _build_operator_verdict(
    *,
    metrics_bundle: ComparisonMetricsBundle,
    differential_report: Mapping[str, Any],
) -> str:
    checks = differential_report["expected_signal_checks"]

    promote_ready = (
        metrics_bundle.shadow_put_candidate_count > metrics_bundle.baseline_put_candidate_count
        and metrics_bundle.ambiguity_rate_shadow <= 0.25
        and checks["regime_improved"]
        and checks["economics_comparable"]
        and checks["economics_improved"]
        and checks["reward_cost_fail_reduced"]
        and checks["put_focus_preserved"]
        and metrics_bundle.frame_alignment_mismatch_count == 0
    )

    lines = [
        "REPLAY OPERATOR VERDICT",
        "",
        f"shadow_put_candidate_gain={metrics_bundle.shadow_put_candidate_count - metrics_bundle.baseline_put_candidate_count}",
        f"newly_admitted_shadow_frames={differential_report['summary']['newly_admitted_shadow_frames']}",
        f"ambiguity_rate_shadow={metrics_bundle.ambiguity_rate_shadow}",
        f"frame_alignment_mismatch_count={metrics_bundle.frame_alignment_mismatch_count}",
        f"regime_improved={checks['regime_improved']}",
        f"economics_comparable={checks['economics_comparable']}",
        f"economics_improved={checks['economics_improved']}",
        f"baseline_economics_source_insufficient_count={checks['baseline_economics_source_insufficient_count']}",
        f"shadow_economics_source_insufficient_count={checks['shadow_economics_source_insufficient_count']}",
        f"economics_source_insufficiency_changed={checks['economics_source_insufficiency_changed']}",
        f"reward_cost_fail_reduced={checks['reward_cost_fail_reduced']}",
        f"put_focus_preserved={checks['put_focus_preserved']}",
        "",
    ]
    if promote_ready:
        lines.append("decision=shadow_candidate_promotable_for_broader_replay")
    else:
        lines.append("decision=continue_shadow_evidence_only")
    lines.append("note=test_not_contract_change")
    lines.append("note=replay_result_not_production_truth")
    return "\n".join(lines) + "\n"


def _extract_decision_label(verdict_text: str) -> str:
    for line in verdict_text.splitlines():
        if line.startswith("decision="):
            return line.split("=", 1)[1].strip()
    return "comparison_completed"


def _write_comparison_summary_artifacts(
    *,
    baseline_run_dir: Path,
    shadow_run_dir: Path,
    output_root: Path,
    operator_verdict: str,
    narration: str,
    comparison_id: str | None,
) -> None:
    builder = PROJECT_ROOT / "bin" / "replay_build_comparison_summary.py"
    if not builder.exists():
        raise ReplayCompareCliError(f"comparison summary builder not found: {builder}")

    cmd = [
        sys.executable,
        str(builder),
        "--baseline-run-dir", str(baseline_run_dir),
        "--shadow-run-dir", str(shadow_run_dir),
        "--output-dir", str(output_root),
        "--operator-verdict", operator_verdict,
        "--narration", narration,
    ]
    if comparison_id:
        cmd.extend(["--comparison-id", comparison_id])

    result = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ReplayCompareCliError(
            "comparison summary builder failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def main() -> int:
    args = _parse_args()

    profile = _load_yaml_mapping(args.profile)
    shadow_override = _load_yaml_mapping(args.shadow_override)

    baseline_frames = _normalize_metric_frames(
        _load_json_list(args.baseline_frames, label="baseline_frames")
    )
    shadow_frames = _normalize_metric_frames(
        _load_json_list(args.shadow_frames, label="shadow_frames")
    )

    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    metrics_bundle = compute_comparison_metrics(
        baseline_frames=baseline_frames,
        shadow_frames=shadow_frames,
    )
    metrics_dict = comparison_metrics_to_dict(metrics_bundle)

    baseline_index = _index_by_frame_id(baseline_frames)
    shadow_index = _index_by_frame_id(shadow_frames)

    candidate_diff = _build_candidate_diff(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
    )
    blocker_diff = _build_blocker_diff(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
    )
    economics_diff = _build_economics_diff(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
        metrics_bundle=metrics_bundle,
    )
    side_split = _build_side_split(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
        newly_admitted_ids=candidate_diff["newly_admitted_shadow_frames"],
    )
    put_leg_focus = _build_put_leg_focus(
        baseline_index=baseline_index,
        shadow_index=shadow_index,
        newly_admitted_ids=candidate_diff["newly_admitted_shadow_frames"],
    )

    baseline_label = str(profile.get("experiment", {}).get("baseline_label", "baseline_locked"))
    shadow_label = str(
        shadow_override.get("pack_id")
        or shadow_override.get("label")
        or Path(args.shadow_override).stem
    )

    differential_report = _build_differential_report(
        baseline_label=baseline_label,
        shadow_label=shadow_label,
        metrics_bundle=metrics_bundle,
        newly_admitted_ids=candidate_diff["newly_admitted_shadow_frames"],
        blocker_diff=blocker_diff,
        economics_diff=economics_diff,
        side_split=side_split,
        put_leg_focus=put_leg_focus,
    )

    verdict_text = _build_operator_verdict(
        metrics_bundle=metrics_bundle,
        differential_report=differential_report,
    )

    _write_json(output_root / "04_metrics_summary.json", metrics_dict)
    _write_json(output_root / "05_candidate_diff_report.json", candidate_diff)
    _write_json(output_root / "06_blocker_diff_report.json", blocker_diff)
    _write_json(output_root / "07_economics_diff_report.json", economics_diff)
    _write_json(output_root / "08_side_split_report.json", side_split)
    _write_json(output_root / "09_put_leg_focus_report.json", put_leg_focus)
    _write_json(output_root / "11_differential_report.json", differential_report)
    _write_json(output_root / "profile_snapshot.json", profile)
    _write_json(output_root / "shadow_override_flattened.json", shadow_override)
    (output_root / "12_operator_verdict.txt").write_text(verdict_text, encoding="utf-8")

    comparison_summary_written = False
    if args.baseline_run_dir and args.shadow_run_dir:
        _write_comparison_summary_artifacts(
            baseline_run_dir=Path(args.baseline_run_dir).expanduser().resolve(),
            shadow_run_dir=Path(args.shadow_run_dir).expanduser().resolve(),
            output_root=output_root,
            operator_verdict=_extract_decision_label(verdict_text),
            narration="Auto-generated by replay_compare.py from baseline/shadow run summaries",
            comparison_id=args.comparison_id,
        )
        comparison_summary_written = True

    print("output_root", str(output_root))
    print("shadow_override_id", shadow_label)
    print("metrics", json.dumps(metrics_dict, sort_keys=True))
    print("comparison_summary_written", comparison_summary_written)
    print("verdict")
    print(verdict_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
