#!/usr/bin/env python3
"""
bin/replay_export_frames_real.py

Real comparison-frame exporter for replay-produced feature and strategy artifacts.

Purpose
-------
Build baseline/shadow comparison-frame JSONs from replay-generated feature rows
and strategy decision rows, then persist:

- baseline_frames.json
- shadow_frames.json

This is the bridge from real replay outputs into the comparison CLI.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.frame_export import (
    ReplayComparisonFrame,
    comparison_frames_to_rows,
)


class ReplayExportFramesError(RuntimeError):
    """Base error for real replay frame export."""


class ReplayExportFramesValidationError(ReplayExportFramesError):
    """Raised when export inputs are missing or malformed."""


@dataclass(frozen=True, slots=True)
class ExportConfig:
    focus_side: str
    primary_leg: str
    secondary_leg: str


def main() -> int:
    args = _parse_args()
    cfg = ExportConfig(
        focus_side=args.focus_side.strip().upper(),
        primary_leg=args.primary_leg.strip().upper(),
        secondary_leg=args.secondary_leg.strip().upper(),
    )

    baseline_feature_rows = _load_rows(args.baseline_features, label="baseline_features")
    baseline_decision_rows = _load_rows(args.baseline_decisions, label="baseline_decisions")
    shadow_feature_rows = _load_rows(args.shadow_features, label="shadow_features")
    shadow_decision_rows = _load_rows(args.shadow_decisions, label="shadow_decisions")

    baseline_frames = _build_export_rows(
        feature_rows=baseline_feature_rows,
        decision_rows=baseline_decision_rows,
        cfg=cfg,
    )
    shadow_frames = _build_export_rows(
        feature_rows=shadow_feature_rows,
        decision_rows=shadow_decision_rows,
        cfg=cfg,
    )

    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    baseline_feature_index_overlay = _index_by_frame_id(
        baseline_feature_rows,
        kind="baseline_feature_rows_overlay",
    )
    baseline_decision_index_overlay = _index_by_frame_id(
        baseline_decision_rows,
        kind="baseline_decision_rows_overlay",
    )
    shadow_feature_index_overlay = _index_by_frame_id(
        shadow_feature_rows,
        kind="shadow_feature_rows_overlay",
    )
    shadow_decision_index_overlay = _index_by_frame_id(
        shadow_decision_rows,
        kind="shadow_decision_rows_overlay",
    )

    baseline_frames = [
        _phase_a4_overlay_export_truth_fields(
            row,
            baseline_feature_index_overlay.get(str(row.get("frame_id") or "")),
            baseline_decision_index_overlay.get(str(row.get("frame_id") or "")),
        )
        for row in baseline_frames
    ]
    shadow_frames = [
        _phase_a4_overlay_export_truth_fields(
            row,
            shadow_feature_index_overlay.get(str(row.get("frame_id") or "")),
            shadow_decision_index_overlay.get(str(row.get("frame_id") or "")),
        )
        for row in shadow_frames
    ]

    baseline_dataset_summary = _load_dataset_summary_near_features(Path(args.baseline_features))
    shadow_dataset_summary = _load_dataset_summary_near_features(Path(args.shadow_features))

    baseline_frames = [
        _apply_dataset_summary_economics_guard(row, baseline_dataset_summary)
        for row in baseline_frames
    ]
    shadow_frames = [
        _apply_dataset_summary_economics_guard(row, shadow_dataset_summary)
        for row in shadow_frames
    ]

    baseline_path = output_root / "baseline_frames.json"
    shadow_path = output_root / "shadow_frames.json"

    _write_json(baseline_path, baseline_frames)
    _write_json(shadow_path, shadow_frames)

    aligned = len(set(_frame_ids(baseline_frames)) & set(_frame_ids(shadow_frames)))

    print("output_root", str(output_root))
    print("baseline_frame_count", len(baseline_frames))
    print("shadow_frame_count", len(shadow_frames))
    print("aligned_frame_count", aligned)
    if baseline_frames:
        print("baseline_sample", json.dumps(baseline_frames[0], sort_keys=True))
    if shadow_frames:
        print("shadow_sample", json.dumps(shadow_frames[0], sort_keys=True))
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export real replay comparison frames from feature/strategy artifacts"
    )
    parser.add_argument("--baseline-features", required=True, help="Baseline replay feature rows JSON")
    parser.add_argument("--baseline-decisions", required=True, help="Baseline replay strategy decisions JSON")
    parser.add_argument("--shadow-features", required=True, help="Shadow replay feature rows JSON")
    parser.add_argument("--shadow-decisions", required=True, help="Shadow replay strategy decisions JSON")
    parser.add_argument("--output-root", required=True, help="Output directory")
    parser.add_argument("--focus-side", default="PUT", choices=("PUT", "CALL"))
    parser.add_argument("--primary-leg", default="ATM1", choices=("ATM", "ATM1"))
    parser.add_argument("--secondary-leg", default="ATM", choices=("ATM", "ATM1"))
    return parser.parse_args()


def _load_rows(path: str, *, label: str) -> list[dict[str, Any]]:
    source = Path(path).expanduser().resolve()
    if not source.exists():
        raise ReplayExportFramesValidationError(f"{label} file not found: {source}")

    with source.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        if isinstance(payload.get("rows"), list):
            rows = payload["rows"]
        elif isinstance(payload.get("items"), list):
            rows = payload["items"]
        else:
            raise ReplayExportFramesValidationError(
                f"{label} must be a list or a mapping containing 'rows'/'items': {source}"
            )
    else:
        raise ReplayExportFramesValidationError(
            f"{label} must be a list or mapping: {source}"
        )

    normalized: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ReplayExportFramesValidationError(f"{label}[{idx}] must be an object")
        normalized.append(row)
    return normalized




def _build_export_rows(
    *,
    feature_rows: list[dict[str, Any]],
    decision_rows: list[dict[str, Any]],
    cfg: ExportConfig,
) -> list[dict[str, Any]]:
    feature_index = _index_by_frame_id(feature_rows, kind="feature_rows")
    decision_index = _index_by_frame_id(decision_rows, kind="decision_rows")

    frame_ids = sorted(feature_index)
    frames: list[ReplayComparisonFrame] = []

    def _clean_text(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _normalized_side(value: Any) -> str | None:
        text = _clean_text(value)
        return text.upper() if text is not None else None

    def _normalized_leg(value: Any) -> str | None:
        text = _clean_text(value)
        return text.upper() if text is not None else None

    def _first_boolish(*values: Any) -> bool | None:
        for value in values:
            result = _boolish(value)
            if result is not None:
                return result
        return None

    def _legacy_payloads(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
        return (
            _mapping(row.get("futures")),
            _mapping(row.get("ce_atm")),
            _mapping(row.get("ce_atm1")),
            _mapping(row.get("pe_atm")),
            _mapping(row.get("pe_atm1")),
        )

    for frame_id in frame_ids:
        feature_row = feature_index[frame_id]
        decision_row = decision_index.get(frame_id)

        futures, ce_atm, ce_atm1, pe_atm, pe_atm1 = _legacy_payloads(feature_row)
        has_legacy_nested = bool(futures or ce_atm or ce_atm1 or pe_atm or pe_atm1)

        healthy = _first_boolish(feature_row.get("healthy"))
        regime_pass = _first_boolish(
            feature_row.get("regime_pass"),
            feature_row.get("regime_ok"),
        )
        economics_valid = _first_boolish(feature_row.get("economics_valid"))
        reward_cost_valid = _first_boolish(feature_row.get("reward_cost_valid"))
        candidate = _first_boolish(feature_row.get("candidate"))
        ambiguity = _first_boolish(feature_row.get("ambiguity"))

        side = _normalized_side(feature_row.get("side"))
        leg = _normalized_leg(feature_row.get("leg"))
        blocker = _clean_text(feature_row.get("blocker"))

        decision_candidate = _decision_is_candidate(decision_row)
        decision_side = _decision_side(decision_row)
        decision_leg = _decision_leg(decision_row, decision_side)

        # only promote positive evidence from decisions; do not convert unknown to false
        if candidate is None and decision_candidate is True:
            candidate = True

        if side is None and decision_side is not None:
            side = decision_side
        if leg is None and decision_leg is not None:
            leg = decision_leg

        if has_legacy_nested:
            legacy_healthy = (
                _boolish(futures.get("fresh"))
                and _boolish(futures.get("valid_tick"))
                and _boolish(futures.get("sync_valid"))
            )
            legacy_regime_pass = _boolish(futures.get("regime_ok"))

            if healthy is None:
                healthy = legacy_healthy
            if regime_pass is None:
                regime_pass = legacy_regime_pass

            if side is None or leg is None:
                if candidate is True and decision_side is not None and decision_leg is not None:
                    side = decision_side if side is None else side
                    leg = decision_leg if leg is None else leg
                else:
                    fallback_side = cfg.focus_side
                    fallback_leg = _default_focus_leg(
                        side=fallback_side,
                        primary_leg=cfg.primary_leg,
                        secondary_leg=cfg.secondary_leg,
                        ce_atm=ce_atm,
                        ce_atm1=ce_atm1,
                        pe_atm=pe_atm,
                        pe_atm1=pe_atm1,
                    )
                    if side is None:
                        side = fallback_side
                    if leg is None:
                        leg = fallback_leg

            option_payload = _select_option_payload(
                leg=leg or "",
                ce_atm=ce_atm,
                ce_atm1=ce_atm1,
                pe_atm=pe_atm,
                pe_atm1=pe_atm1,
            )

            if economics_valid is None:
                economics_valid = _boolish(option_payload.get("economics_valid"))
            if reward_cost_valid is None:
                reward_cost_valid = _reward_cost_valid(option_payload)
            if ambiguity is None:
                ambiguity = _derive_ambiguity(
                    regime_pass=bool(regime_pass) if regime_pass is not None else False,
                    ce_atm=ce_atm,
                    ce_atm1=ce_atm1,
                    pe_atm=pe_atm,
                    pe_atm1=pe_atm1,
                )

        # only derive blocker when there is explicit blocker evidence and candidate is explicitly false
        if blocker is None and candidate is False:
            blocker = _explicit_decision_blocker(decision_row)

        if healthy is None:
            healthy = False
        if ambiguity is None:
            ambiguity = False

        if side is None:
            side = "UNKNOWN"
        if leg is None:
            leg = "UNKNOWN"

        frames.append(
            ReplayComparisonFrame(
                frame_id=frame_id,
                healthy=healthy,
                regime_pass=regime_pass,
                economics_valid=economics_valid,
                candidate=candidate,
                side=side,
                leg=leg,
                blocker=blocker,
                ambiguity=ambiguity,
                reward_cost_valid=reward_cost_valid,
            )
        )

    return comparison_frames_to_rows(frames)


def _index_by_frame_id(
    rows: Iterable[dict[str, Any]],
    *,
    kind: str,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for pos, row in enumerate(rows):
        frame_id = _extract_frame_id(row)
        if frame_id in indexed:
            raise ReplayExportFramesValidationError(
                f"{kind} contains duplicate frame_id: {frame_id}"
            )
        indexed[frame_id] = row
    return indexed


def _extract_frame_id(row: Mapping[str, Any]) -> str:
    candidates = [
        row.get("frame_id"),
        row.get("source_frame_id"),
        row.get("frame_ts_ns"),
        _mapping(row.get("metadata")).get("frame_id"),
        _mapping(row.get("metadata")).get("source_frame_id"),
        _mapping(row.get("metadata")).get("frame_ts_ns"),
        _mapping(row.get("metadata")).get("signal_reference_ts_ns"),
        row.get("signal_reference_ts_ns"),
        row.get("ts_event_ns"),
    ]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, int):
            return str(value)
    raise ReplayExportFramesValidationError("unable to extract frame_id from row")


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}



def _boolish(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False
        return None

    text = str(value).strip().lower()
    if not text:
        return None
    if text in {"true", "1", "yes", "y", "pass", "ok"}:
        return True
    if text in {"false", "0", "no", "n", "fail", "failed"}:
        return False
    if text in {"none", "null", "na", "n/a", "unknown"}:
        return None
    return None


def _decision_is_candidate(decision_row: dict[str, Any] | None) -> bool:
    if not decision_row:
        return False
    action = str(decision_row.get("action") or "").upper()
    return action in {"ENTER_CALL", "ENTER_PUT", "ACTION_ENTER_CALL", "ACTION_ENTER_PUT"}


def _decision_side(decision_row: dict[str, Any] | None) -> str | None:
    if not decision_row:
        return None
    side = str(decision_row.get("side") or "").upper()
    action = str(decision_row.get("action") or "").upper()

    if side in {"CALL", "PUT"}:
        return side
    if "CALL" in action:
        return "CALL"
    if "PUT" in action:
        return "PUT"
    return None


def _decision_leg(decision_row: dict[str, Any] | None, side: str | None) -> str | None:
    if not decision_row or side is None:
        return None
    entry_mode = str(decision_row.get("entry_mode") or "").upper()
    metadata = _mapping(decision_row.get("metadata"))
    if not entry_mode:
        entry_mode = str(metadata.get("entry_mode") or "").upper()

    if entry_mode == "ATM1":
        return f"{side}_ATM1"
    if entry_mode == "ATM":
        return f"{side}_ATM"

    signal_reason = str(metadata.get("reason_code") or decision_row.get("explain") or "").lower()
    if "atm1" in signal_reason:
        return f"{side}_ATM1"
    if "atm" in signal_reason:
        return f"{side}_ATM"

    return f"{side}_ATM"


def _default_focus_leg(
    *,
    side: str,
    primary_leg: str,
    secondary_leg: str,
    ce_atm: Mapping[str, Any],
    ce_atm1: Mapping[str, Any],
    pe_atm: Mapping[str, Any],
    pe_atm1: Mapping[str, Any],
) -> str:
    first = f"{side}_{primary_leg}"
    second = f"{side}_{secondary_leg}"

    first_payload = _select_option_payload(
        leg=first,
        ce_atm=ce_atm,
        ce_atm1=ce_atm1,
        pe_atm=pe_atm,
        pe_atm1=pe_atm1,
    )
    if first_payload:
        return first

    second_payload = _select_option_payload(
        leg=second,
        ce_atm=ce_atm,
        ce_atm1=ce_atm1,
        pe_atm=pe_atm,
        pe_atm1=pe_atm1,
    )
    if second_payload:
        return second

    return first


def _select_option_payload(
    *,
    leg: str,
    ce_atm: Mapping[str, Any],
    ce_atm1: Mapping[str, Any],
    pe_atm: Mapping[str, Any],
    pe_atm1: Mapping[str, Any],
) -> Mapping[str, Any]:
    mapping = {
        "CALL_ATM": ce_atm,
        "CALL_ATM1": ce_atm1,
        "PUT_ATM": pe_atm,
        "PUT_ATM1": pe_atm1,
    }
    return mapping.get(leg.upper(), {})


def _explicit_decision_blocker(decision_row: dict[str, Any] | None) -> str | None:
    if not decision_row:
        return None
    candidates = [
        decision_row.get("blocker_code"),
        decision_row.get("blocker_reason"),
        decision_row.get("blocker_message"),
    ]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None




def _decision_blocker(decision_row: dict[str, Any] | None) -> str | None:
    if not decision_row:
        return "missing_decision"
    metadata = _mapping(decision_row.get("metadata"))
    candidates = [
        decision_row.get("blocker_code"),
        metadata.get("reason_code"),
        decision_row.get("blocker_message"),
        decision_row.get("explain"),
        decision_row.get("reason"),
    ]
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value.strip()
    action = str(decision_row.get("action") or "").upper()
    if action == "HOLD":
        return "hold"
    return "no_candidate"



# === Phase A.4 dataset-summary economics insufficiency guard v2 ===

def _load_dataset_summary_near_features(features_path: Path) -> dict[str, object]:
    artifacts_dir = features_path.resolve().parent
    run_dir = artifacts_dir.parent
    dataset_summary_path = run_dir / "01_dataset_summary.json"
    if not dataset_summary_path.exists():
        return {}
    with dataset_summary_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def _resolve_dataset_summary_economics_state(dataset_summary: dict[str, object]) -> dict[str, object]:
    source_mode = dataset_summary.get("economics_source_mode")
    source_status = dataset_summary.get("economics_source_status")
    eligible = dataset_summary.get("economics_eligible_for_evaluation")
    missing = dataset_summary.get("economics_missing_required_fields") or []

    economics_surface_present = any(
        key in dataset_summary
        for key in (
            "economics_source_mode",
            "economics_source_status",
            "economics_eligible_for_evaluation",
            "economics_missing_required_fields",
            "economics_source_summary",
        )
    )

    if not economics_surface_present:
        source_mode = "unavailable"
        source_status = "insufficient_source_truth"
        eligible = False
        missing = ["dataset_summary_economics_surface_missing"]

    insufficient = (
        source_mode == "unavailable"
        or source_status == "insufficient_source_truth"
        or eligible is False
    )

    return {
        "economics_source_mode": source_mode,
        "economics_source_status": source_status,
        "economics_eligible_for_evaluation": eligible,
        "economics_missing_required_fields": list(missing),
        "economics_source_insufficient": insufficient,
    }



def _apply_row_context_aliases_to_missing_fields(
    exported_row: dict[str, object],
    missing_required_fields: list[str],
) -> list[str]:
    present_aliases: set[str] = set()

    def _present(value: object) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() != ""
        return True

    if _present(exported_row.get("frame_id")) or _present(exported_row.get("source_frame_id")):
        present_aliases.add("source_frame_id")
    if _present(exported_row.get("symbol")):
        present_aliases.add("symbol")
    if _present(exported_row.get("side")):
        present_aliases.add("side")
    if _present(exported_row.get("leg")) or _present(exported_row.get("selected_leg")):
        present_aliases.add("selected_leg")
    if _present(exported_row.get("entry_mode")):
        present_aliases.add("entry_mode")
    if _present(exported_row.get("tick_size")):
        present_aliases.add("tick_size")

    return [field_name for field_name in missing_required_fields if field_name not in present_aliases]



def _phase_a4_present(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _phase_a4_first_present(*values: object) -> object:
    for value in values:
        if _phase_a4_present(value):
            return value
    return None


def _phase_a4_overlay_export_truth_fields(
    exported_row: dict[str, object],
    feature_row: dict[str, object] | None,
    decision_row: dict[str, object] | None,
) -> dict[str, object]:
    row = dict(exported_row)
    feature = feature_row if isinstance(feature_row, dict) else {}
    decision = decision_row if isinstance(decision_row, dict) else {}

    row["ts_event"] = _phase_a4_first_present(
        decision.get("ts_event"),
        feature.get("ts_event"),
        decision.get("event_time"),
        feature.get("event_time"),
    )
    row["selected_leg"] = _phase_a4_first_present(
        decision.get("selected_leg"),
        feature.get("selected_leg"),
        decision.get("leg"),
        feature.get("leg"),
    )
    row["entry_mode"] = _phase_a4_first_present(
        decision.get("entry_mode"),
        feature.get("entry_mode"),
    )
    row["tick_size"] = _phase_a4_first_present(
        decision.get("tick_size"),
        feature.get("tick_size"),
    )
    row["target_ticks"] = _phase_a4_first_present(
        decision.get("target_ticks"),
        feature.get("target_ticks"),
    )
    row["stop_ticks"] = _phase_a4_first_present(
        decision.get("stop_ticks"),
        feature.get("stop_ticks"),
    )
    row["reward_ticks"] = _phase_a4_first_present(
        decision.get("reward_ticks"),
        feature.get("reward_ticks"),
    )
    row["reward_cost_ratio"] = _phase_a4_first_present(
        decision.get("reward_cost_ratio"),
        feature.get("reward_cost_ratio"),
    )
    row["economics_reason"] = _phase_a4_first_present(
        decision.get("economics_reason"),
        feature.get("economics_reason"),
        decision.get("reason"),
    )
    return row


def _apply_dataset_summary_economics_guard(
    exported_row: dict[str, object],
    dataset_summary: dict[str, object],
) -> dict[str, object]:
    state = _resolve_dataset_summary_economics_state(dataset_summary)
    row = dict(exported_row)

    refined_missing_required_fields = _apply_row_context_aliases_to_missing_fields(
        row,
        state["economics_missing_required_fields"],
    )

    row["economics_source_mode"] = state["economics_source_mode"]
    row["economics_source_status"] = state["economics_source_status"]
    row["economics_eligible_for_evaluation"] = state["economics_eligible_for_evaluation"]
    row["economics_missing_required_fields"] = refined_missing_required_fields
    row["economics_source_insufficient"] = (
        state["economics_source_insufficient"] or len(refined_missing_required_fields) > 0
    )

    if row["economics_source_insufficient"]:
        row["economics_valid"] = None
        row["reward_cost_valid"] = None
        if "candidate_seed" in row:
            row["candidate_seed"] = None
        if row.get("blocker") == "economics_fail":
            row["blocker"] = "economics_source_insufficient"
        if row.get("blocker_name") == "economics_fail":
            row["blocker_name"] = "economics_source_insufficient"
        if row.get("blocker_reason") == "economics_fail":
            row["blocker_reason"] = "economics_source_insufficient"

    return row


def _reward_cost_valid(option_payload: Mapping[str, Any]) -> bool | None:
    if not option_payload:
        return None
    if "reward_to_cost" in option_payload:
        try:
            return float(option_payload.get("reward_to_cost") or 0.0) >= 2.5
        except Exception:
            return None
    if "economics_valid" in option_payload:
        return bool(option_payload.get("economics_valid"))
    return None


def _derive_ambiguity(
    *,
    regime_pass: bool,
    ce_atm: Mapping[str, Any],
    ce_atm1: Mapping[str, Any],
    pe_atm: Mapping[str, Any],
    pe_atm1: Mapping[str, Any],
) -> bool:
    if not regime_pass:
        return False
    call_ok = _boolish(ce_atm.get("economics_valid")) or _boolish(ce_atm1.get("economics_valid"))
    put_ok = _boolish(pe_atm.get("economics_valid")) or _boolish(pe_atm1.get("economics_valid"))
    return call_ok and put_ok


def _frame_ids(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    result: list[str] = []
    for row in rows:
        frame_id = row.get("frame_id")
        if isinstance(frame_id, str):
            result.append(frame_id)
    return result


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())

# phase_a4_truth_passthrough_v2
