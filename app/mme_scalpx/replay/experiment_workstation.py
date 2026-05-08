from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from app.mme_scalpx.replay.batch_runner import (
    build_scenario_matrix_plan,
    simulate_replay_batch_plan,
)
from app.mme_scalpx.replay.integrity import replay_fingerprint
from app.mme_scalpx.replay.report_exporter import (
    build_baseline_shadow_comparison,
    materialize_replay_report_exports,
)
from app.mme_scalpx.replay.safety import assert_replay_artifact_path
from app.mme_scalpx.replay.scenarios import REPLAY_REQUIRED_SCENARIOS
from app.mme_scalpx.replay.strategy_adapter import REPLAY_STRATEGY_FAMILIES, REPLAY_STRATEGY_SIDES


REPLAY_EXPERIMENT_WORKSTATION_CONTRACT_VERSION = "replay_experiment_workstation_v1"

REPLAY_EXPERIMENT_TYPES = (
    "baseline_vs_shadow",
    "parameter_sweep",
    "threshold_sweep",
    "family_enable_disable",
    "side_only",
    "scenario_matrix_comparison",
)

REPLAY_EXPERIMENT_REQUIRED_PROFILE_FIELDS = (
    "profile_id",
    "experiment_type",
    "description",
    "baseline",
    "variants",
    "dates",
    "scenario_ids",
    "parameter_overrides",
    "threshold_overrides",
    "family_filter",
    "side_filter",
    "explicit_replay_only",
    "paper_armed_approved",
    "live_trading_approved",
    "production_doctrine_changed",
)

REPLAY_EXPERIMENT_REQUIRED_EXPORTS = (
    "00_experiment_manifest.json",
    "01_experiment_summary.json",
    "02_variant_results.json",
    "03_differential_summary.json",
    "04_parameter_sweep_summary.json",
    "05_threshold_sweep_summary.json",
    "06_family_side_summary.json",
    "07_experiment_reproducibility.json",
    "08_experiment_comparison_export.json",
)


@dataclass(frozen=True)
class ReplayExperimentProfile:
    profile_id: str
    experiment_type: str
    description: str
    baseline: dict[str, Any]
    variants: tuple[dict[str, Any], ...]
    dates: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    parameter_overrides: dict[str, Any]
    threshold_overrides: dict[str, Any]
    family_filter: tuple[str, ...]
    side_filter: tuple[str, ...]
    explicit_replay_only: bool = True
    paper_armed_approved: bool = False
    live_trading_approved: bool = False
    execution_arming_created: bool = False
    broker_calls_allowed: bool = False
    live_redis_writes_allowed: bool = False
    production_doctrine_changed: bool = False


def _profile(
    profile_id: str,
    experiment_type: str,
    description: str,
    *,
    baseline: Mapping[str, Any] | None = None,
    variants: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]] | None = None,
    dates: tuple[str, ...] | list[str] = ("2026-05-01",),
    scenario_ids: tuple[str, ...] | list[str] = ("full_fill",),
    parameter_overrides: Mapping[str, Any] | None = None,
    threshold_overrides: Mapping[str, Any] | None = None,
    family_filter: tuple[str, ...] | list[str] = REPLAY_STRATEGY_FAMILIES,
    side_filter: tuple[str, ...] | list[str] = REPLAY_STRATEGY_SIDES,
) -> ReplayExperimentProfile:
    if experiment_type not in REPLAY_EXPERIMENT_TYPES:
        raise ValueError(f"unsupported experiment_type: {experiment_type}")
    return ReplayExperimentProfile(
        profile_id=profile_id,
        experiment_type=experiment_type,
        description=description,
        baseline=dict(baseline or {"label": "baseline", "scenario_ids": ("full_fill",)}),
        variants=tuple(dict(v) for v in (variants or ())),
        dates=tuple(str(x) for x in dates),
        scenario_ids=tuple(str(x) for x in scenario_ids),
        parameter_overrides=dict(parameter_overrides or {}),
        threshold_overrides=dict(threshold_overrides or {}),
        family_filter=tuple(str(x) for x in family_filter),
        side_filter=tuple(str(x) for x in side_filter),
    )


REPLAY_EXPERIMENT_PROFILES = {
    "baseline_vs_shadow": _profile(
        "baseline_vs_shadow",
        "baseline_vs_shadow",
        "Compare a baseline full-fill replay against full scenario-matrix shadow replay.",
        baseline={"label": "baseline_full_fill", "scenario_ids": ("full_fill",)},
        variants=(
            {"label": "shadow_scenario_matrix", "scenario_ids": REPLAY_REQUIRED_SCENARIOS},
        ),
        scenario_ids=REPLAY_REQUIRED_SCENARIOS,
    ),
    "parameter_sweep": _profile(
        "parameter_sweep",
        "parameter_sweep",
        "Replay-only parameter sweep shape for non-production research.",
        baseline={"label": "baseline_full_fill", "scenario_ids": ("full_fill",)},
        variants=(
            {"label": "slippage_0_5", "scenario_ids": ("full_fill",), "parameter_overrides": {"slippage_points": 0.5}},
            {"label": "slippage_2_0", "scenario_ids": ("high_slippage",), "parameter_overrides": {"slippage_points": 2.0}},
            {"label": "slippage_5_0", "scenario_ids": ("high_slippage",), "parameter_overrides": {"slippage_points": 5.0}},
        ),
        scenario_ids=("full_fill", "high_slippage"),
        parameter_overrides={"sweep_field": "slippage_points", "values": (0.5, 2.0, 5.0)},
    ),
    "threshold_sweep": _profile(
        "threshold_sweep",
        "threshold_sweep",
        "Replay-only threshold sweep shape for non-production research.",
        baseline={"label": "baseline_full_fill", "scenario_ids": ("full_fill",)},
        variants=(
            {"label": "risk_threshold_low", "scenario_ids": ("forced_risk_veto",), "threshold_overrides": {"risk_score_min": 0.25}},
            {"label": "risk_threshold_mid", "scenario_ids": ("full_fill",), "threshold_overrides": {"risk_score_min": 0.50}},
            {"label": "risk_threshold_high", "scenario_ids": ("no_fill",), "threshold_overrides": {"risk_score_min": 0.75}},
        ),
        scenario_ids=("forced_risk_veto", "full_fill", "no_fill"),
        threshold_overrides={"sweep_field": "risk_score_min", "values": (0.25, 0.50, 0.75)},
    ),
    "family_enable_disable": _profile(
        "family_enable_disable",
        "family_enable_disable",
        "Replay-only family enable/disable comparison shape.",
        baseline={"label": "all_families", "scenario_ids": ("full_fill",), "family_filter": REPLAY_STRATEGY_FAMILIES},
        variants=tuple(
            {"label": f"only_{family.lower()}", "scenario_ids": ("full_fill",), "family_filter": (family,)}
            for family in REPLAY_STRATEGY_FAMILIES
        ),
        scenario_ids=("full_fill",),
        family_filter=REPLAY_STRATEGY_FAMILIES,
    ),
    "side_only": _profile(
        "side_only",
        "side_only",
        "Replay-only CALL-only and PUT-only comparison shape.",
        baseline={"label": "both_sides", "scenario_ids": ("full_fill",), "side_filter": REPLAY_STRATEGY_SIDES},
        variants=(
            {"label": "call_only", "scenario_ids": ("full_fill",), "side_filter": ("CALL",)},
            {"label": "put_only", "scenario_ids": ("full_fill",), "side_filter": ("PUT",)},
        ),
        scenario_ids=("full_fill",),
        side_filter=REPLAY_STRATEGY_SIDES,
    ),
    "scenario_matrix_comparison": _profile(
        "scenario_matrix_comparison",
        "scenario_matrix_comparison",
        "Replay-only comparison across all scenario profiles.",
        baseline={"label": "baseline_full_fill", "scenario_ids": ("full_fill",)},
        variants=(
            {"label": "all_scenarios", "scenario_ids": REPLAY_REQUIRED_SCENARIOS},
            {"label": "liquidity_scenarios", "scenario_ids": ("wide_spread", "low_depth", "liquidity_shock")},
            {"label": "provider_scenarios", "scenario_ids": ("dhan_context_unavailable", "dhan_context_stale", "oi_ladder_missing")},
        ),
        scenario_ids=REPLAY_REQUIRED_SCENARIOS,
    ),
}


def replay_experiment_profile(profile_id: str) -> dict[str, Any]:
    if profile_id not in REPLAY_EXPERIMENT_PROFILES:
        raise KeyError(f"unknown replay experiment profile: {profile_id}")
    p = REPLAY_EXPERIMENT_PROFILES[profile_id]
    return {
        "schema_version": REPLAY_EXPERIMENT_WORKSTATION_CONTRACT_VERSION,
        "profile_id": p.profile_id,
        "experiment_type": p.experiment_type,
        "description": p.description,
        "baseline": p.baseline,
        "variants": p.variants,
        "dates": p.dates,
        "scenario_ids": p.scenario_ids,
        "parameter_overrides": p.parameter_overrides,
        "threshold_overrides": p.threshold_overrides,
        "family_filter": p.family_filter,
        "side_filter": p.side_filter,
        "explicit_replay_only": p.explicit_replay_only,
        "paper_armed_approved": p.paper_armed_approved,
        "live_trading_approved": p.live_trading_approved,
        "execution_arming_created": p.execution_arming_created,
        "broker_calls_allowed": p.broker_calls_allowed,
        "live_redis_writes_allowed": p.live_redis_writes_allowed,
        "production_doctrine_changed": p.production_doctrine_changed,
    }


def list_replay_experiment_profiles() -> tuple[dict[str, Any], ...]:
    return tuple(replay_experiment_profile(k) for k in REPLAY_EXPERIMENT_TYPES)


def validate_replay_experiment_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    missing = tuple(field for field in REPLAY_EXPERIMENT_REQUIRED_PROFILE_FIELDS if field not in profile)
    type_ok = profile.get("experiment_type") in REPLAY_EXPERIMENT_TYPES
    variants_ok = isinstance(profile.get("variants"), (tuple, list)) and len(profile.get("variants") or ()) > 0
    explicit_ok = profile.get("explicit_replay_only") is True
    no_live_ok = (
        profile.get("paper_armed_approved") is False
        and profile.get("live_trading_approved") is False
        and profile.get("execution_arming_created") is False
        and profile.get("broker_calls_allowed") is False
        and profile.get("live_redis_writes_allowed") is False
        and profile.get("production_doctrine_changed") is False
    )
    ok = bool(not missing and type_ok and variants_ok and explicit_ok and no_live_ok)
    return {
        "ok": ok,
        "missing": missing,
        "type_ok": type_ok,
        "variants_ok": variants_ok,
        "explicit_ok": explicit_ok,
        "no_live_ok": no_live_ok,
    }


def _scenario_ids_from_variant(variant: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(str(x) for x in (variant.get("scenario_ids") or ("full_fill",)))


def run_replay_experiment_profile(
    profile_id: str,
    *,
    dates: tuple[str, ...] | list[str] | None = None,
) -> dict[str, Any]:
    profile = replay_experiment_profile(profile_id)
    validation = validate_replay_experiment_profile(profile)
    if not validation["ok"]:
        raise ValueError(f"invalid replay experiment profile: {validation}")

    experiment_dates = tuple(str(x) for x in (dates or profile["dates"]))
    baseline = dict(profile["baseline"])
    baseline_label = str(baseline.get("label", "baseline"))
    baseline_scenarios = _scenario_ids_from_variant(baseline)

    baseline_plan = build_scenario_matrix_plan(dates=experiment_dates, scenarios=baseline_scenarios)
    baseline_result = simulate_replay_batch_plan(baseline_plan)

    variant_results = []
    for variant in tuple(profile["variants"]):
        variant = dict(variant)
        label = str(variant.get("label", "variant"))
        scenario_ids = _scenario_ids_from_variant(variant)
        variant_plan = build_scenario_matrix_plan(dates=experiment_dates, scenarios=scenario_ids)
        variant_result = simulate_replay_batch_plan(variant_plan)
        comparison = build_baseline_shadow_comparison(
            baseline_label=baseline_label,
            baseline_result=baseline_result,
            shadow_label=label,
            shadow_result=variant_result,
        )
        variant_results.append({
            "label": label,
            "scenario_ids": scenario_ids,
            "plan": variant_plan,
            "result": variant_result,
            "comparison": comparison,
            "parameter_overrides": dict(variant.get("parameter_overrides") or profile.get("parameter_overrides") or {}),
            "threshold_overrides": dict(variant.get("threshold_overrides") or profile.get("threshold_overrides") or {}),
            "family_filter": tuple(variant.get("family_filter") or profile.get("family_filter") or ()),
            "side_filter": tuple(variant.get("side_filter") or profile.get("side_filter") or ()),
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "execution_arming_created": False,
            "real_order_sent": False,
            "broker_calls_executed": False,
            "live_redis_writes_executed": False,
            "production_doctrine_changed": False,
        })

    differential_summary = build_replay_differential_summary(
        profile=profile,
        baseline_result=baseline_result,
        variant_results=tuple(variant_results),
    )

    experiment = {
        "schema_version": "replay_experiment_result_v1",
        "profile": profile,
        "experiment_id": deterministic_replay_experiment_id(profile),
        "dates": experiment_dates,
        "baseline_label": baseline_label,
        "baseline_plan": baseline_plan,
        "baseline_result": baseline_result,
        "variant_results": tuple(variant_results),
        "differential_summary": differential_summary,
        "experiment_reproducibility_hash": replay_fingerprint({
            "profile": profile,
            "dates": experiment_dates,
            "baseline_result": baseline_result,
            "variant_results": variant_results,
            "differential_summary": differential_summary,
        }),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "full_live_replay_parity": "NOT_PROVEN_IN_27M",
    }
    return experiment


def deterministic_replay_experiment_id(profile: Mapping[str, Any]) -> str:
    return f"replay_experiment_{profile.get('profile_id')}_{replay_fingerprint(profile)[:16]}"


def build_replay_differential_summary(
    *,
    profile: Mapping[str, Any],
    baseline_result: Mapping[str, Any],
    variant_results: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]],
) -> dict[str, Any]:
    baseline_pnl = float(baseline_result.get("total_shadow_pnl") or 0.0)
    rows = []
    for variant in tuple(variant_results):
        result = dict(variant.get("result") or {})
        comparison = dict(variant.get("comparison") or {})
        rows.append({
            "label": variant.get("label"),
            "scenario_count": result.get("scenario_count"),
            "result_count": result.get("result_count"),
            "total_shadow_pnl": result.get("total_shadow_pnl"),
            "delta_shadow_pnl": comparison.get("delta_shadow_pnl"),
            "delta_result_count": comparison.get("delta_result_count"),
            "parameter_overrides": variant.get("parameter_overrides"),
            "threshold_overrides": variant.get("threshold_overrides"),
            "family_filter": variant.get("family_filter"),
            "side_filter": variant.get("side_filter"),
            "paper_armed_approved": False,
            "live_trading_approved": False,
            "production_doctrine_changed": False,
        })
    best_by_pnl = max(rows, key=lambda r: float(r.get("total_shadow_pnl") or 0.0)) if rows else None
    return {
        "schema_version": "replay_differential_summary_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_type": profile.get("experiment_type"),
        "baseline_total_shadow_pnl": baseline_pnl,
        "variant_count": len(rows),
        "rows": tuple(rows),
        "best_by_shadow_pnl": best_by_pnl,
        "differential_summary_shape": "PROVEN_BY_27M",
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def build_parameter_sweep_summary(experiment_result: Mapping[str, Any]) -> dict[str, Any]:
    profile = dict(experiment_result.get("profile") or {})
    rows = tuple((experiment_result.get("differential_summary") or {}).get("rows") or ())
    parameter_rows = tuple(r for r in rows if r.get("parameter_overrides"))
    return {
        "schema_version": "replay_parameter_sweep_summary_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_type": profile.get("experiment_type"),
        "parameter_sweep_row_count": len(parameter_rows),
        "parameter_rows": parameter_rows,
        "parameter_sweep_shape": "PROVEN_BY_27M",
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }


def build_threshold_sweep_summary(experiment_result: Mapping[str, Any]) -> dict[str, Any]:
    profile = dict(experiment_result.get("profile") or {})
    rows = tuple((experiment_result.get("differential_summary") or {}).get("rows") or ())
    threshold_rows = tuple(r for r in rows if r.get("threshold_overrides"))
    return {
        "schema_version": "replay_threshold_sweep_summary_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_type": profile.get("experiment_type"),
        "threshold_sweep_row_count": len(threshold_rows),
        "threshold_rows": threshold_rows,
        "threshold_sweep_shape": "PROVEN_BY_27M",
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }


def build_family_side_experiment_summary(experiment_result: Mapping[str, Any]) -> dict[str, Any]:
    profile = dict(experiment_result.get("profile") or {})
    rows = tuple((experiment_result.get("differential_summary") or {}).get("rows") or ())
    family_rows = tuple(r for r in rows if r.get("family_filter"))
    side_rows = tuple(r for r in rows if r.get("side_filter"))
    return {
        "schema_version": "replay_family_side_experiment_summary_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_type": profile.get("experiment_type"),
        "family_row_count": len(family_rows),
        "side_row_count": len(side_rows),
        "family_rows": family_rows,
        "side_rows": side_rows,
        "family_side_filter_shape": "PROVEN_BY_27M",
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }


def materialize_replay_experiment_artifacts(
    *,
    experiment_result: Mapping[str, Any],
    export_root: str,
) -> dict[str, Any]:
    root = Path(export_root)
    assert_replay_artifact_path(str(root / "00_experiment_manifest.json"))
    root.mkdir(parents=True, exist_ok=True)

    profile = dict(experiment_result.get("profile") or {})
    variant_results = tuple(experiment_result.get("variant_results") or ())
    differential_summary = dict(experiment_result.get("differential_summary") or {})
    parameter_summary = build_parameter_sweep_summary(experiment_result)
    threshold_summary = build_threshold_sweep_summary(experiment_result)
    family_side_summary = build_family_side_experiment_summary(experiment_result)

    comparison_export = {
        "schema_version": "replay_experiment_comparison_export_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_type": profile.get("experiment_type"),
        "comparisons": tuple(v.get("comparison") for v in variant_results),
        "comparison_count": len(variant_results),
        "baseline_shadow_comparison_shape": "PROVEN_BY_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    reproducibility = {
        "schema_version": "replay_experiment_reproducibility_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_id": experiment_result.get("experiment_id"),
        "experiment_reproducibility_hash": experiment_result.get("experiment_reproducibility_hash"),
        "artifact_payload_hash": replay_fingerprint({
            "profile": profile,
            "variant_results": variant_results,
            "differential_summary": differential_summary,
            "parameter_summary": parameter_summary,
            "threshold_summary": threshold_summary,
            "family_side_summary": family_side_summary,
            "comparison_export": comparison_export,
        }),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }

    manifest = {
        "schema_version": REPLAY_EXPERIMENT_WORKSTATION_CONTRACT_VERSION,
        "profile_id": profile.get("profile_id"),
        "experiment_id": experiment_result.get("experiment_id"),
        "experiment_type": profile.get("experiment_type"),
        "export_root": str(root),
        "required_exports": REPLAY_EXPERIMENT_REQUIRED_EXPORTS,
        "materialized_at_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_reproducibility_hash": experiment_result.get("experiment_reproducibility_hash"),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
        "experiment_profile_shape": "PROVEN_BY_27M",
        "full_live_replay_parity": "NOT_PROVEN_IN_27M",
    }

    experiment_summary = {
        "schema_version": "replay_experiment_summary_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_type": profile.get("experiment_type"),
        "variant_count": len(variant_results),
        "baseline_label": experiment_result.get("baseline_label"),
        "dates": experiment_result.get("dates"),
        "experiment_reproducibility_hash": experiment_result.get("experiment_reproducibility_hash"),
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

    payloads = {
        "00_experiment_manifest.json": manifest,
        "01_experiment_summary.json": experiment_summary,
        "02_variant_results.json": tuple(variant_results),
        "03_differential_summary.json": differential_summary,
        "04_parameter_sweep_summary.json": parameter_summary,
        "05_threshold_sweep_summary.json": threshold_summary,
        "06_family_side_summary.json": family_side_summary,
        "07_experiment_reproducibility.json": reproducibility,
        "08_experiment_comparison_export.json": comparison_export,
    }

    written = {}
    for name, payload in payloads.items():
        path = root / name
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
        written[name] = str(path)

    return {
        "schema_version": "replay_experiment_artifact_materialization_result_v1",
        "profile_id": profile.get("profile_id"),
        "experiment_id": experiment_result.get("experiment_id"),
        "export_root": str(root),
        "required_exports": REPLAY_EXPERIMENT_REQUIRED_EXPORTS,
        "written_exports": written,
        "written_count": len(written),
        "experiment_reproducibility_hash": experiment_result.get("experiment_reproducibility_hash"),
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "real_order_sent": False,
        "broker_calls_executed": False,
        "live_redis_writes_executed": False,
        "production_doctrine_changed": False,
    }


def validate_replay_experiment_artifacts(result: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(str(result.get("export_root")))
    written = dict(result.get("written_exports") or {})
    missing = tuple(name for name in REPLAY_EXPERIMENT_REQUIRED_EXPORTS if name not in written or not Path(written[name]).exists())
    root_ok = str(root).startswith("run/replay") or "/run/replay/" in str(root)
    count_ok = int(result.get("written_count", -1)) == len(REPLAY_EXPERIMENT_REQUIRED_EXPORTS)
    hash_ok = bool(result.get("experiment_reproducibility_hash"))
    no_live_ok = (
        result.get("paper_armed_approved") is False
        and result.get("live_trading_approved") is False
        and result.get("execution_arming_created") is False
        and result.get("real_order_sent") is False
        and result.get("broker_calls_executed") is False
        and result.get("live_redis_writes_executed") is False
        and result.get("production_doctrine_changed") is False
    )
    ok = bool(not missing and root_ok and count_ok and hash_ok and no_live_ok)
    return {
        "ok": ok,
        "missing": missing,
        "root_ok": root_ok,
        "count_ok": count_ok,
        "hash_ok": hash_ok,
        "no_live_ok": no_live_ok,
    }


def replay_experiment_profile_manifest() -> dict[str, Any]:
    profiles = list_replay_experiment_profiles()
    return {
        "schema_version": "replay_experiment_profile_manifest_v1",
        "profile_count": len(profiles),
        "experiment_types": REPLAY_EXPERIMENT_TYPES,
        "profiles": profiles,
        "required_exports": REPLAY_EXPERIMENT_REQUIRED_EXPORTS,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


def replay_experiment_profile_manifest_json() -> str:
    return json.dumps(replay_experiment_profile_manifest(), indent=2, sort_keys=True, default=str)


def replay_experiment_workstation_contract_summary() -> dict[str, Any]:
    return {
        "schema_version": REPLAY_EXPERIMENT_WORKSTATION_CONTRACT_VERSION,
        "experiment_types": REPLAY_EXPERIMENT_TYPES,
        "required_profile_fields": REPLAY_EXPERIMENT_REQUIRED_PROFILE_FIELDS,
        "required_exports": REPLAY_EXPERIMENT_REQUIRED_EXPORTS,
        "experiment_profile_shape": "PROVEN_BY_27M",
        "differential_summary_shape": "PROVEN_BY_27M",
        "parameter_sweep_shape": "PROVEN_BY_27M",
        "threshold_sweep_shape": "PROVEN_BY_27M",
        "family_side_filter_shape": "PROVEN_BY_27M",
        "experiment_reproducibility_hash": "PROVEN_BY_27M",
        "strategy_improvement_claim": "NOT_PROVEN_IN_27M",
        "full_live_replay_parity": "NOT_PROVEN_IN_27M",
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "execution_arming_created": False,
        "broker_calls_allowed": False,
        "live_redis_writes_allowed": False,
        "production_doctrine_changed": False,
    }


try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "REPLAY_EXPERIMENT_WORKSTATION_CONTRACT_VERSION",
    "REPLAY_EXPERIMENT_TYPES",
    "REPLAY_EXPERIMENT_REQUIRED_PROFILE_FIELDS",
    "REPLAY_EXPERIMENT_REQUIRED_EXPORTS",
    "ReplayExperimentProfile",
    "REPLAY_EXPERIMENT_PROFILES",
    "replay_experiment_profile",
    "list_replay_experiment_profiles",
    "validate_replay_experiment_profile",
    "run_replay_experiment_profile",
    "deterministic_replay_experiment_id",
    "build_replay_differential_summary",
    "build_parameter_sweep_summary",
    "build_threshold_sweep_summary",
    "build_family_side_experiment_summary",
    "materialize_replay_experiment_artifacts",
    "validate_replay_experiment_artifacts",
    "replay_experiment_profile_manifest",
    "replay_experiment_profile_manifest_json",
    "replay_experiment_workstation_contract_summary",
)))
