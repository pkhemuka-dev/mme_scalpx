from __future__ import annotations

import inspect
import sys
from dataclasses import is_dataclass, replace as dataclass_replace
from datetime import datetime
from pathlib import Path
from typing import Any, get_args, get_origin, get_type_hints

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture import models as rc_models
from app.mme_scalpx.research_capture import raw_capture_bridge as bridge
from app.mme_scalpx.research_capture.reader import (
    read_capture_report_dir,
    read_capture_session,
)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_ID = f"research_capture_optional_audit_roundtrip_proof_{TS}"

EXPECTED_COUNTS = {
    "ticks_fut": 1,
    "ticks_opt": 2,
    "runtime_audit": 3,
    "signals_audit": 1,
}


def _unwrap_optional(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is None:
        return annotation
    args = [arg for arg in get_args(annotation) if arg is not type(None)]
    if len(args) == 1:
        return _unwrap_optional(args[0])
    return annotation


def _resolve_strategy_audit_cls():
    hints = get_type_hints(
        rc_models.CaptureRecord,
        globalns=vars(rc_models),
        localns=vars(rc_models),
    )
    annotation = hints.get("strategy_audit")
    if annotation is None:
        raise RuntimeError("unable to resolve CaptureRecord.strategy_audit type hint")
    strategy_audit_cls = _unwrap_optional(annotation)
    if isinstance(strategy_audit_cls, str):
        raise RuntimeError(
            f"strategy_audit type hint still unresolved after get_type_hints: {strategy_audit_cls!r}"
        )
    return strategy_audit_cls


def _field_names(model_cls: type) -> tuple[str, ...]:
    if hasattr(model_cls, "model_fields"):
        return tuple(model_cls.model_fields.keys())
    if is_dataclass(model_cls):
        return tuple(model_cls.__dataclass_fields__.keys())
    annotations = getattr(model_cls, "__annotations__", {})
    if annotations:
        return tuple(annotations.keys())
    try:
        sig = inspect.signature(model_cls)
        return tuple(
            name
            for name, param in sig.parameters.items()
            if name != "self"
            and param.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            )
        )
    except Exception:
        return ()


def _guess_value(field_name: str) -> Any:
    name = field_name.lower()

    if name in {"candidate_found", "candidate", "is_candidate"}:
        return True
    if name in {"blocker_found", "has_blocker"}:
        return False
    if name in {"regime_ok", "regime_pass", "is_regime_ok"}:
        return True
    if name in {"side", "decision_side"}:
        return "CALL"
    if name == "entry_mode":
        return "ATM"
    if name in {"decision_action", "action"}:
        return "ENTER_CALL"

    if name.endswith("_id"):
        return "signals-audit-seed-1"
    if "candidate" in name:
        return True
    if "blocker" in name:
        return False
    if "regime" in name:
        return True
    if "side" in name:
        return "CALL"
    if "action" in name:
        return "ENTER_CALL"
    if "entry" in name and "mode" in name:
        return "ATM"
    if "reason" in name or "note" in name or "message" in name or "remark" in name:
        return "seeded_signals_audit_round_trip"
    if name.endswith("_ts") or name.endswith("_ts_ns") or name == "ts_ns":
        return 1776555786000000000
    if name.startswith("is_") or name.startswith("has_"):
        return True

    return "seeded_signals_audit_round_trip"


def _build_strategy_audit_instance() -> Any:
    strategy_audit_cls = _resolve_strategy_audit_cls()
    field_names = _field_names(strategy_audit_cls)
    if not field_names:
        raise RuntimeError(
            f"unable to resolve strategy_audit field names for {strategy_audit_cls!r}"
        )

    payload = {
        field_names[0]: _guess_value(field_names[0]),
    }

    preferred_names = (
        "candidate_found",
        "candidate",
        "decision_action",
        "action",
        "side",
        "entry_mode",
        "regime_ok",
        "message",
        "note",
        "reason",
    )
    for name in preferred_names:
        if name in field_names:
            payload[name] = _guess_value(name)

    if hasattr(strategy_audit_cls, "model_construct"):
        return strategy_audit_cls.model_construct(**payload)

    if is_dataclass(strategy_audit_cls):
        accepted = {
            key: value
            for key, value in payload.items()
            if key in strategy_audit_cls.__dataclass_fields__
        }
        return strategy_audit_cls(**accepted)

    try:
        sig = inspect.signature(strategy_audit_cls)
        accepted = {
            key: value
            for key, value in payload.items()
            if key in sig.parameters
        }
        return strategy_audit_cls(**accepted)
    except Exception as exc:
        raise RuntimeError(
            f"unable to instantiate strategy_audit payload for {strategy_audit_cls!r}"
        ) from exc


def _clone_record_with_strategy_audit(record, strategy_audit):
    if hasattr(record, "model_copy") and callable(record.model_copy):
        return record.model_copy(update={"strategy_audit": strategy_audit})

    if hasattr(record, "copy") and callable(record.copy):
        try:
            return record.copy(update={"strategy_audit": strategy_audit})
        except TypeError:
            pass

    if is_dataclass(record):
        return dataclass_replace(record, strategy_audit=strategy_audit)

    if hasattr(record, "__dict__"):
        payload = dict(record.__dict__)
        payload["strategy_audit"] = strategy_audit
        return type(record)(**payload)

    raise TypeError(f"unsupported CaptureRecord clone surface: {type(record)!r}")


original_build_capture_records = bridge._build_capture_records


def patched_build_capture_records(rows):
    records = list(original_build_capture_records(rows))
    if not records:
        raise RuntimeError("patched_build_capture_records received empty record batch")

    target_index = 0
    for idx, record in enumerate(records):
        dataset_value = getattr(getattr(record, "dataset", None), "value", None)
        if dataset_value == "ticks_opt":
            target_index = idx
            break

    strategy_audit = _build_strategy_audit_instance()
    records[target_index] = _clone_record_with_strategy_audit(
        records[target_index],
        strategy_audit,
    )
    return tuple(records)


def main() -> None:
    bridge._build_capture_records = patched_build_capture_records
    try:
        result = bridge.run_first_real_raw_capture(
            "run",
            run_id=RUN_ID,
            session_date="2026-04-18",
            notes="canonical_optional_audit_roundtrip_proof",
            project_root=PROJECT_ROOT,
        )
    finally:
        bridge._build_capture_records = original_build_capture_records

    report_dir = Path(
        result.manifest_materialization_result.manifest_seed.metadata["report_root"]
    ).resolve()

    report_bundle = read_capture_report_dir(report_dir)
    session_bundle = read_capture_session(report_bundle["session_root"])

    report_counts = dict(report_bundle["dataset_row_counts"])
    session_counts = dict(session_bundle["dataset_row_counts"])
    integrity_counts = dict(report_bundle["integrity_summary_dataset_row_counts"])

    if report_counts != session_counts:
        raise AssertionError(
            f"report_counts != session_counts :: {report_counts} != {session_counts}"
        )

    if report_counts != integrity_counts:
        raise AssertionError(
            f"report_counts != integrity_counts :: {report_counts} != {integrity_counts}"
        )

    for dataset_name, expected_count in EXPECTED_COUNTS.items():
        actual_count = int(report_counts.get(dataset_name, 0))
        if actual_count != expected_count:
            raise AssertionError(
                f"unexpected row count for {dataset_name}: "
                f"actual={actual_count} expected={expected_count}"
            )

    print("===== CANONICAL_OPTIONAL_AUDIT_ROUNDTRIP_PROOF =====")
    print(f"run_id={result.run_id}")
    print(f"entrypoint={result.entrypoint}")
    print(f"session_root={report_bundle['session_root']}")
    print(f"report_dir={report_bundle['report_dir']}")
    print(f"report_counts={report_counts}")
    print(f"session_counts={session_counts}")
    print(f"integrity_counts={integrity_counts}")
    print("status=GREEN")


if __name__ == "__main__":
    main()
