#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.research_capture import contracts as C
from app.mme_scalpx.research_capture import models as M
from app.mme_scalpx.research_capture import normalizer as NORM
from app.mme_scalpx.research_capture import manifest as MF
from app.mme_scalpx.research_capture import archive_writer as AW
from app.mme_scalpx.research_capture import raw_capture_bridge as RCB
from app.mme_scalpx.research_capture import reader as RD
from app.mme_scalpx.research_capture import enricher as EN
from app.mme_scalpx.research_capture import utils as U
from app.mme_scalpx.research_capture.models import (
    CaptureArchiveOutput,
    CaptureDatasetName,
    CaptureSessionManifest,
    IntegritySummary,
    SourceAvailability,
)


def _case(label: str, ok: bool, **extra: Any) -> dict[str, Any]:
    return {"case": label, "status": "PASS" if ok else "FAIL", **extra}


def _expect_reject(label: str, fn, contains: str | None = None) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        if contains is not None and contains not in str(exc):
            return {"case": label, "status": "FAIL", "error": f"wrong error: {type(exc).__name__}: {exc}"}
        return {"case": label, "status": "PASS", "error": f"{type(exc).__name__}: {exc}"}
    return {"case": label, "status": "FAIL", "error": "accepted invalid input"}


def _manifest(session_date: str) -> CaptureSessionManifest:
    source = SourceAvailability(
        sources={"records_present": True, "zerodha": True},
        counts={"zerodha": 1},
        notes=(),
    )
    integrity = IntegritySummary(
        total_records=1,
        dataset_row_counts={"ticks_fut": 1},
        stale_tick_count=0,
        missing_depth_count=0,
        missing_oi_count=0,
        thin_book_count=0,
        integrity_flag_counts={},
        warnings=(),
        errors=(),
    )
    output = CaptureArchiveOutput(
        dataset=CaptureDatasetName.TICKS_FUT,
        row_count=1,
        file_name="ticks_fut.parquet",
        partition_columns=tuple(C.PRIMARY_PARTITIONS + C.SECONDARY_PARTITIONS),
        bytes_written=10,
        notes=(),
    )
    return CaptureSessionManifest(
        session_date=session_date,
        source_availability=source,
        integrity_summary=integrity,
        archive_outputs=(output,),
    )


def main() -> int:
    cases: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Path containment.
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "project"
        root.mkdir()
        inside = root / "run" / "research_capture" / "2026-04-25" / "manifest.json"
        cases.append(
            _case(
                "path_inside_root_accepted",
                U.ensure_path_within_root(inside, root, label="inside") == inside.resolve(),
            )
        )
        cases.append(
            _expect_reject(
                "path_traversal_rejected",
                lambda: U.ensure_path_within_root(root / ".." / "escape.json", root, label="escape"),
                "escapes root",
            )
        )
        cases.append(
            _expect_reject(
                "absolute_unapproved_path_rejected",
                lambda: U.ensure_path_within_root("/tmp/outside_research_capture.json", root, label="absolute"),
                "escapes root",
            )
        )

    # ------------------------------------------------------------------
    # Contract field coverage.
    # ------------------------------------------------------------------
    required_names = set(C.batch17_required_field_names())
    missing = sorted(name for name in required_names if name not in C.FIELD_SPECS_BY_NAME)
    cases.append(_case("batch17_contract_fields_present", not missing, missing=missing))

    for name in (
        "strategy_family_id",
        "doctrine_id",
        "branch_id",
        "provider_ready_miso",
        "dhan_context_status",
        "canonical_instrument_key",
        "zerodha_instrument_token",
        "dhan_security_id",
        "raw_payload_json",
        "ts_event_ns",
        "ts_capture_ns",
        "ts_archive_write_ns",
    ):
        spec = C.FIELD_SPECS_BY_NAME[name]
        cases.append(
            _case(
                f"{name}_not_production_approved",
                spec.usage_class is not C.UsageClass.PRODUCTION_CANDIDATE,
                usage_class=spec.usage_class.value,
            )
        )

    # ------------------------------------------------------------------
    # Unknown field quarantine / raw payload preservation.
    # ------------------------------------------------------------------
    cases.append(
        _expect_reject(
            "unknown_top_level_field_rejected",
            lambda: M.canonicalize_archive_row({"not_a_contract_field": 1}),
            "unknown",
        )
    )
    try:
        row = M.canonicalize_archive_row(
            {
                "session_date": "2026-04-25",
                "instrument_type": "FUT",
                "underlying_symbol": "NIFTY",
                "raw_payload_json": json.dumps({"unknownBrokerField": "preserved"}),
            },
            include_none=False,
        )
        cases.append(
            _case(
                "raw_payload_json_preserves_unknown_broker_fields",
                "unknownBrokerField" in row["raw_payload_json"],
                row=row,
            )
        )
    except Exception as exc:
        cases.append({"case": "raw_payload_json_preserves_unknown_broker_fields", "status": "FAIL", "error": str(exc)})

    # ------------------------------------------------------------------
    # Provider identity preservation.
    # ------------------------------------------------------------------
    zerodha = NORM.batch17_provider_identity_fields(
        {"instrument_token": 111, "tradingsymbol": "NIFTYCE"},
        broker_name="ZERODHA",
        canonical_instrument_key="NIFTY:CE",
    )
    dhan = NORM.batch17_provider_identity_fields(
        {"security_id": "D222", "tradingsymbol": "NIFTYPE"},
        broker_name="DHAN",
        canonical_instrument_key="NIFTY:PE",
    )
    cases.append(
        _case(
            "zerodha_token_preserved_separately",
            zerodha["zerodha_instrument_token"] == 111 and zerodha["dhan_security_id"] is None,
            identity=zerodha,
        )
    )
    cases.append(
        _case(
            "dhan_security_id_preserved_separately",
            dhan["dhan_security_id"] == "D222" and dhan["zerodha_instrument_token"] is None,
            identity=dhan,
        )
    )

    # ------------------------------------------------------------------
    # Production firewall.
    # ------------------------------------------------------------------
    firewall = MF.build_production_firewall_manifest_section()
    cases.append(
        _case(
            "production_firewall_false_for_mutation",
            firewall["production_doctrine_mutated"] is False
            and firewall["production_params_mutated"] is False
            and firewall["live_runtime_mutated"] is False
            and firewall["research_outputs_are_advisory"] is True,
            firewall=firewall,
        )
    )

    manifest = _manifest("2026-04-25")
    payload = manifest.to_dict()
    cases.append(
        _case(
            "manifest_to_dict_contains_production_firewall",
            payload.get("production_firewall", {}).get("production_doctrine_mutated") is False,
            production_firewall=payload.get("production_firewall"),
        )
    )

    # ------------------------------------------------------------------
    # Archive write lock.
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        session_root = Path(tmp) / "run" / "research_capture" / "2026-04-25"
        cases.append(
            _expect_reject(
                "append_requires_session_write_lock",
                lambda: AW.require_session_write_lock(session_root),
                "requires session write lock",
            )
        )
        lock = AW.acquire_session_write_lock(session_root, owner="proof-a")
        cases.append(_case("append_with_lock_accepted", lock.exists(), lock=str(lock)))
        cases.append(
            _expect_reject(
                "second_writer_without_release_rejected",
                lambda: AW.acquire_session_write_lock(session_root, owner="proof-b"),
                "already held",
            )
        )
        AW.release_session_write_lock(session_root, owner="proof-a")
        cases.append(_case("lock_release_removes_lock", not lock.exists()))

    # ------------------------------------------------------------------
    # Destructive purge guard.
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        archive_root = root / "run" / "research_capture"
        session_root = archive_root / "2026-04-25"
        dataset_root = session_root / "runtime_audit"
        dataset_root.mkdir(parents=True)
        (dataset_root / "old.parquet").write_text("x", encoding="utf-8")
        target = RCB._batch17_validate_optional_purge_target(
            dataset_root=dataset_root,
            archive_root=archive_root,
            session_root=session_root,
            dataset_name="runtime_audit",
        )
        cases.append(_case("optional_dataset_purge_known_target_accepted", target == dataset_root.resolve()))
        cases.append(
            _expect_reject(
                "optional_dataset_purge_path_traversal_rejected",
                lambda: RCB._batch17_validate_optional_purge_target(
                    dataset_root=session_root / ".." / "escape",
                    archive_root=archive_root,
                    session_root=session_root,
                    dataset_name="runtime_audit",
                ),
            )
        )
        cases.append(
            _expect_reject(
                "optional_dataset_purge_archive_root_rejected",
                lambda: RCB._batch17_validate_optional_purge_target(
                    dataset_root=archive_root,
                    archive_root=archive_root,
                    session_root=session_root,
                    dataset_name="runtime_audit",
                ),
            )
        )
        cases.append(
            _expect_reject(
                "optional_dataset_purge_unknown_dataset_rejected",
                lambda: RCB._batch17_validate_optional_purge_target(
                    dataset_root=session_root / "ticks_fut",
                    archive_root=archive_root,
                    session_root=session_root,
                    dataset_name="ticks_fut",
                ),
                "not allowed",
            )
        )

    # ------------------------------------------------------------------
    # Manifest-led reader.
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        session_root = Path(tmp) / "run" / "research_capture" / "2026-04-25"
        trusted_dir = session_root / "dataset=ticks_fut"
        trusted_dir.mkdir(parents=True)
        trusted_file = trusted_dir / "ticks_fut.parquet"
        trusted_file.write_text("trusted", encoding="utf-8")
        extra_file = session_root / "extra_old.parquet"
        extra_file.write_text("extra", encoding="utf-8")

        trusted = RD.batch17_manifest_declared_dataset_files(manifest, session_root=session_root)
        extras = RD.batch17_extra_unmanifested_parquet_files(manifest, session_root=session_root)

        cases.append(
            _case(
                "reader_manifest_declared_file_trusted",
                str(trusted_file.resolve()) in trusted["ticks_fut"],
                trusted=trusted,
            )
        )
        cases.append(
            _case(
                "reader_extra_parquet_reported_not_trusted",
                str(extra_file.resolve()) in extras,
                extras=extras,
            )
        )

    # ------------------------------------------------------------------
    # Atomic writer replacement markers.
    # ------------------------------------------------------------------
    import app.mme_scalpx.research_capture.artifact_materializer as AM
    import app.mme_scalpx.research_capture.manifest_materializer as MM
    import app.mme_scalpx.research_capture.session_materializer as SM
    import app.mme_scalpx.research_capture.runtime_bridge as RB

    cases.append(
        _case(
            "critical_json_writes_use_atomic_helper",
            getattr(AM._write_json, "_batch17_atomic", False)
            and getattr(MM._write_json, "_batch17_atomic", False)
            and getattr(SM._write_json, "_batch17_atomic", False)
            and getattr(RB._write_json, "_batch17_atomic", False),
        )
    )

    # ------------------------------------------------------------------
    # Live-derived metrics advisory only.
    # ------------------------------------------------------------------
    marker = EN.batch17_live_derived_non_authoritative_metadata()
    cases.append(
        _case(
            "live_derived_metrics_non_authoritative",
            marker["live_derived_metrics_non_authoritative"] is True
            and marker["derived_not_production_used"] is True,
            marker=marker,
        )
    )

    failed = [case for case in cases if case.get("status") != "PASS"]
    proof = {
        "proof": "research_capture_contracts",
        "status": "FAIL" if failed else "PASS",
        "failed_cases": failed,
        "cases": cases,
    }

    out = PROJECT_ROOT / "run" / "proofs" / "research_capture_contracts.json"
    out.write_text(json.dumps(proof, indent=2, sort_keys=True, default=str))
    print(json.dumps(proof, indent=2, sort_keys=True, default=str))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
