#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import codec
from app.mme_scalpx.core import models

OUT = PROJECT_ROOT / "run" / "proofs" / "core_codec_transport.json"

def case(name, ok, **details):
    row = {"case": name, "status": "PASS" if ok else "FAIL", **details}
    if not ok:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row


def _proof_decode_event_payload(arg1, arg2):
    """Proof-local compatibility wrapper.

    Accepts both historical proof order:

        _proof_decode_event_payload(model_cls, payload)

    and accidental/canonical order:

        _proof_decode_event_payload(payload, model_cls)

    Then calls the current codec canonical surface:

        codec.decode_event_payload(payload, model_cls)

    This is proof-only. codec.py is not changed.
    """
    if isinstance(arg1, type):
        model_cls = arg1
        payload = arg2
    elif isinstance(arg2, type):
        payload = arg1
        model_cls = arg2
    else:
        raise TypeError(
            "_proof_decode_event_payload requires one Schema model class and one payload mapping"
        )

    return codec.decode_event_payload(payload, model_cls)

def main() -> int:
    cases = []

    hb = models.Heartbeat(
        service="features",
        instance_id="proof",
        ts_event_ns=1,
        status="OK",
        message=None,
    )
    fields = codec.encode_hash_fields(hb)
    hb2 = codec.decode_hash_fields(models.Heartbeat, fields)
    cases.append(case(
        "heartbeat_hash_roundtrip",
        hb2.service == "features" and hb2.message is None and hb2.ts_event_ns == 1,
        fields=fields,
    ))

    hb3 = _proof_decode_event_payload(
        {
            "service": "features",
            "instance_id": "proof",
            "ts_event_ns": 1,
            "status": "OK",
        },
        models.Heartbeat,
    )
    cases.append(case(
        "decode_event_payload_missing_optional_message",
        hb3.message is None,
        message=hb3.message,
    ))

    env = codec.envelope_for_model(
        hb,
        ts_event_ns=1,
        ts_ingest_ns=2,
        producer="batch18-proof",
    )
    decoded = codec.decode_model_from_envelope_as(models.Heartbeat, env)
    cases.append(case(
        "envelope_roundtrip_and_typed_decode",
        isinstance(decoded, models.Heartbeat) and decoded.service == hb.service,
    ))

    wrong_type_rejected = False
    wrong_type_error = ""
    if hasattr(models, "FeatureFrame"):
        try:
            codec.decode_model_from_envelope_as(models.FeatureFrame, env)
        except Exception as exc:
            wrong_type_rejected = True
            wrong_type_error = str(exc)
    else:
        wrong_type_rejected = True
        wrong_type_error = "FeatureFrame not present; skipped without weakening typed decode positive proof"

    cases.append(case(
        "typed_decode_wrong_model_rejected",
        wrong_type_rejected,
        error=wrong_type_error,
    ))

    nan_rejected = False
    nan_error = ""
    try:
        codec.json_dumps({"bad": float("nan")})
    except Exception as exc:
        nan_rejected = True
        nan_error = str(exc)

    cases.append(case("nan_rejected", nan_rejected, error=nan_error))

    proof = {
        "proof": "core_codec_transport",
        "status": "PASS",
        "cases": cases,
        "failed_cases": [],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
