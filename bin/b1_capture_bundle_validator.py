#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

FAMILIES = ["MIST", "MISB", "MISC", "MISR", "MISO"]

REQUIRED_FILES = [
    "capture_manifest.json",
    "features_rows.jsonl",
    "decision_rows.jsonl",
    "risk_lifecycle_rows.jsonl",
    "execution_shadow_rows.jsonl",
    "position_safety_snapshot.json",
    "order_safety_snapshot.json",
    "identity_continuity_report.json",
    "lifecycle_presence_report.json",
    "backtest_admission_precheck.json",
    "safety_no_order_no_broker_report.json",
]

REQUIRED_FIELDS = {
    "capture_manifest.json": [
        "capture_id",
        "capture_started_at_utc",
        "capture_finished_at_utc",
        "observe_only",
        "paper_or_live_enabled",
        "families_requested",
        "families_observed",
        "source_streams",
        "artifact_fingerprints",
    ],
    "features_rows.jsonl": [
        "frame_id",
        "frame_ts_ns",
        "family_features_json",
        "family_surfaces_json",
        "consumer_view_json",
    ],
    "decision_rows.jsonl": [
        "decision_id",
        "frame_id",
        "frame_ts_ns",
        "action",
        "activation_action",
        "activation_selected_family_id",
        "activation_selected_branch_id",
        "activation_candidate_count",
        "activation_report_only",
        "activation_promoted",
        "activation_safe_to_promote",
        "family_features_json",
        "family_surfaces_json",
    ],
    "risk_lifecycle_rows.jsonl": [
        "decision_id",
        "family_id",
        "branch_id",
        "side",
        "risk_status",
        "risk_action",
        "risk_reason",
        "veto_entries",
        "max_new_lots",
        "risk_lifecycle_state",
        "risk_approval_lifecycle_present",
        "backtest_admission_status",
    ],
    "execution_shadow_rows.jsonl": [
        "decision_id",
        "family_id",
        "branch_id",
        "side",
        "execution_action",
        "shadow_action",
        "pending_order_json",
        "consumed_risk_evidence",
        "order_sent",
        "broker_order_id",
        "broker_status",
    ],
}

OUTPUT_FILES = [
    "capture_validator_report.json",
    "family_admission_matrix.json",
    "identity_continuity_report.json",
    "lifecycle_presence_report.json",
    "safety_validation_report.json",
    "lane_e_handoff_precheck.json",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {"__load_error__": "json root is not object"}
    except Exception as exc:
        return {"__load_error__": repr(exc)}


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line_no, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
                else:
                    rows.append({"__line_error__": f"non-dict JSON at line {line_no}"})
            except Exception as exc:
                rows.append({"__line_error__": f"{repr(exc)} at line {line_no}"})
    except Exception as exc:
        rows.append({"__file_error__": repr(exc)})
    return rows


def missing_fields(row: dict[str, Any], required: list[str]) -> list[str]:
    return [field for field in required if field not in row]


def load_bundle(bundle: pathlib.Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for name in REQUIRED_FILES:
        path = bundle / name
        if not path.exists():
            data[name] = None
        elif name.endswith(".jsonl"):
            data[name] = read_jsonl(path)
        else:
            data[name] = read_json(path)
    return data


def validate_bundle_shape(bundle: pathlib.Path, data: dict[str, Any]) -> dict[str, Any]:
    missing_files = [name for name in REQUIRED_FILES if data.get(name) is None]
    field_errors: dict[str, Any] = {}

    for name, required in REQUIRED_FIELDS.items():
        obj = data.get(name)
        if obj is None:
            continue
        if name.endswith(".jsonl"):
            rows = obj if isinstance(obj, list) else []
            if not rows:
                field_errors[name] = {"empty": True, "missing_fields": required}
            else:
                row_errors = []
                for idx, row in enumerate(rows[:50]):
                    if not isinstance(row, dict):
                        row_errors.append({"row": idx, "error": "non-dict"})
                    else:
                        miss = missing_fields(row, required)
                        if miss:
                            row_errors.append({"row": idx, "missing": miss})
                if row_errors:
                    field_errors[name] = row_errors
        else:
            if not isinstance(obj, dict):
                field_errors[name] = {"error": "non-dict-json"}
            else:
                miss = missing_fields(obj, required)
                if miss:
                    field_errors[name] = {"missing": miss}

    return {
        "pass": not missing_files and not field_errors,
        "missing_files": missing_files,
        "field_errors": field_errors,
    }


def validate_safety(data: dict[str, Any]) -> dict[str, Any]:
    manifest = data.get("capture_manifest.json") or {}
    position = data.get("position_safety_snapshot.json") or {}
    order = data.get("order_safety_snapshot.json") or {}
    safety = data.get("safety_no_order_no_broker_report.json") or {}

    failures = []

    if manifest.get("observe_only") is not True:
        failures.append("manifest.observe_only is not true")
    if manifest.get("paper_or_live_enabled") is True:
        failures.append("manifest.paper_or_live_enabled is true")
    if safety.get("broker_calls_executed") is True:
        failures.append("broker_calls_executed is true")
    if safety.get("orders_sent") is True:
        failures.append("orders_sent is true")
    if order.get("orders_stream_delta", 0) not in (0, "0", None):
        failures.append("orders_stream_delta > 0")
    if position.get("has_position") is True:
        failures.append("position has_position is true")

    for key in ["qty_lots", "qty_units"]:
        try:
            if float(position.get(key, 0) or 0) > 0:
                failures.append(f"position {key} > 0")
        except Exception:
            failures.append(f"position {key} not numeric")

    return {"pass": not failures, "failures": failures}


def normalize_family(value: Any) -> str:
    s = str(value or "").upper()
    for family in FAMILIES:
        if family in s:
            return family
    return ""


def truthy_candidate_count(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0


def validate_identity_and_lifecycle(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    decisions = data.get("decision_rows.jsonl") or []
    risks = data.get("risk_lifecycle_rows.jsonl") or []
    executions = data.get("execution_shadow_rows.jsonl") or []

    risks_by_decision = {str(r.get("decision_id")): r for r in risks if isinstance(r, dict)}
    exec_by_decision = {str(e.get("decision_id")): e for e in executions if isinstance(e, dict)}

    identity_failures = []
    lifecycle_failures = []
    family_matrix = {
        family: {
            "family_id": family,
            "admission_status": "NOT_ADMITTED",
            "candidate_count": 0,
            "risk_lifecycle_count": 0,
            "execution_shadow_count": 0,
            "blockers": [],
        }
        for family in FAMILIES
    }

    for row in decisions:
        if not isinstance(row, dict):
            continue

        decision_id = str(row.get("decision_id") or "")
        family = normalize_family(
            row.get("activation_selected_family_id")
            or row.get("family_id")
            or row.get("activation_selected_branch_id")
        )
        candidate_count = truthy_candidate_count(row.get("activation_candidate_count"))

        if family in family_matrix and candidate_count > 0:
            family_matrix[family]["candidate_count"] += candidate_count

        risk = risks_by_decision.get(decision_id)
        exe = exec_by_decision.get(decision_id)

        if candidate_count > 0:
            if not risk:
                lifecycle_failures.append(f"{decision_id}: candidate has no risk lifecycle")
                if family in family_matrix:
                    family_matrix[family]["blockers"].append("candidate_without_risk")
            else:
                if family in family_matrix:
                    family_matrix[family]["risk_lifecycle_count"] += 1

            if not exe:
                lifecycle_failures.append(f"{decision_id}: candidate has no execution shadow")
                if family in family_matrix:
                    family_matrix[family]["blockers"].append("candidate_without_execution_shadow")
            else:
                if family in family_matrix:
                    family_matrix[family]["execution_shadow_count"] += 1

        if risk:
            risk_family = normalize_family(risk.get("family_id") or risk.get("branch_id"))
            if family and risk_family and family != risk_family:
                identity_failures.append(f"{decision_id}: family mismatch decision={family} risk={risk_family}")

        if exe:
            exe_family = normalize_family(exe.get("family_id") or exe.get("branch_id"))
            if family and exe_family and family != exe_family:
                identity_failures.append(f"{decision_id}: family mismatch decision={family} execution={exe_family}")
            if not exe.get("consumed_risk_evidence"):
                lifecycle_failures.append(f"{decision_id}: execution missing consumed_risk_evidence")
                if family in family_matrix:
                    family_matrix[family]["blockers"].append("missing_consumed_risk_evidence")
            if exe.get("order_sent") is True:
                lifecycle_failures.append(f"{decision_id}: execution has order_sent=true")
                if family in family_matrix:
                    family_matrix[family]["blockers"].append("order_sent_true")

    for family, row in family_matrix.items():
        if (
            row["candidate_count"] > 0
            and row["risk_lifecycle_count"] > 0
            and row["execution_shadow_count"] > 0
            and not row["blockers"]
        ):
            row["admission_status"] = "ADMITTED_FOR_LANE_E_REVIEW"

    identity = {"pass": not identity_failures, "failures": identity_failures}
    lifecycle = {"pass": not lifecycle_failures, "failures": lifecycle_failures}
    return identity, lifecycle, family_matrix


def validate_capture_bundle(bundle_path: pathlib.Path) -> dict[str, Any]:
    bundle = bundle_path.resolve()
    data = load_bundle(bundle)

    shape = validate_bundle_shape(bundle, data)
    safety = validate_safety(data)
    identity, lifecycle, family_matrix = validate_identity_and_lifecycle(data)

    any_family_admitted = any(
        row["admission_status"] == "ADMITTED_FOR_LANE_E_REVIEW"
        for row in family_matrix.values()
    )

    lane_e_handoff_allowed = (
        shape["pass"]
        and safety["pass"]
        and identity["pass"]
        and lifecycle["pass"]
        and any_family_admitted
    )

    blockers = []
    if not shape["pass"]:
        blockers.append("bundle_shape_failed")
    if not safety["pass"]:
        blockers.append("safety_failed")
    if not identity["pass"]:
        blockers.append("identity_continuity_failed")
    if not lifecycle["pass"]:
        blockers.append("lifecycle_presence_failed")
    if not any_family_admitted:
        blockers.append("no_family_admitted_for_lane_e_review")

    return {
        "capture_id": (data.get("capture_manifest.json") or {}).get("capture_id"),
        "validated_at_utc": now_utc(),
        "bundle_path": str(bundle),
        "safety_pass": safety["pass"],
        "identity_continuity_pass": identity["pass"],
        "lifecycle_presence_pass": lifecycle["pass"],
        "bundle_shape_pass": shape["pass"],
        "family_admission_matrix": family_matrix,
        "lane_e_handoff_allowed": lane_e_handoff_allowed,
        "blockers": blockers,
        "details": {
            "shape": shape,
            "safety": safety,
            "identity": identity,
            "lifecycle": lifecycle,
        },
        "does_not": {
            "run_replay": True,
            "calculate_pnl": True,
            "approve_paper": True,
            "approve_live": True,
            "send_orders": True,
            "call_broker": True,
            "write_redis": True,
        },
    }


def write_report(report: dict[str, Any], out_dir: pathlib.Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "capture_validator_report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "family_admission_matrix.json").write_text(json.dumps(report["family_admission_matrix"], indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "identity_continuity_report.json").write_text(json.dumps(report["details"]["identity"], indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "lifecycle_presence_report.json").write_text(json.dumps(report["details"]["lifecycle"], indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "safety_validation_report.json").write_text(json.dumps(report["details"]["safety"], indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / "lane_e_handoff_precheck.json").write_text(json.dumps({
        "lane_e_handoff_allowed": report["lane_e_handoff_allowed"],
        "blockers": report["blockers"],
        "family_admission_matrix": report["family_admission_matrix"],
        "validated_at_utc": report["validated_at_utc"],
    }, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-only validator for recorded observe-only lifecycle capture bundles.")
    parser.add_argument("--bundle", required=True, help="Path to a captured artifact bundle directory.")
    parser.add_argument("--out", required=True, help="Output directory for validator reports.")
    parser.add_argument("--dry-only", action="store_true", required=True, help="Required safety flag. Validator never runs replay or live.")
    args = parser.parse_args()

    report = validate_capture_bundle(pathlib.Path(args.bundle))
    write_report(report, pathlib.Path(args.out))

    print(json.dumps({
        "bundle_shape_pass": report["bundle_shape_pass"],
        "safety_pass": report["safety_pass"],
        "identity_continuity_pass": report["identity_continuity_pass"],
        "lifecycle_presence_pass": report["lifecycle_presence_pass"],
        "lane_e_handoff_allowed": report["lane_e_handoff_allowed"],
        "blockers": report["blockers"],
    }, indent=2, sort_keys=True))

    # Contract rule:
    # return 2 only for malformed/missing bundle shape.
    # shape-valid but lifecycle-invalid bundles are normal validation failures and return 0.
    return 0 if report["bundle_shape_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
