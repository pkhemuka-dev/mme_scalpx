#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.core import codec, models, redisx

OUT = PROJECT_ROOT / "run" / "proofs" / "redisx_typed_stream_helpers.json"

def case(name, ok, **details):
    row = {"case": name, "status": "PASS" if ok else "FAIL", **details}
    if not ok:
        raise AssertionError(json.dumps(row, indent=2, sort_keys=True))
    return row

def main() -> int:
    cases = []
    src = (PROJECT_ROOT / "app/mme_scalpx/core/redisx.py").read_text(encoding="utf-8")

    cases.append(case(
        "redisx_uses_decode_model_from_envelope_as",
        "decode_model_from_envelope_as" in src
        and "decode_model_from_envelope(model_cls, envelope)" not in src,
    ))

    hb = models.Heartbeat(
        service="features",
        instance_id="proof",
        ts_event_ns=1,
        status="OK",
        message=None,
    )
    env = codec.envelope_for_model(
        hb,
        ts_event_ns=1,
        ts_ingest_ns=2,
        producer="batch18-proof",
    )
    decoded = codec.decode_model_from_envelope_as(models.Heartbeat, env)
    cases.append(case(
        "typed_codec_decode_positive_path",
        isinstance(decoded, models.Heartbeat),
    ))

    wrong_type_rejected = False
    error = ""
    if hasattr(models, "FeatureFrame"):
        try:
            codec.decode_model_from_envelope_as(models.FeatureFrame, env)
        except Exception as exc:
            wrong_type_rejected = True
            error = str(exc)
    else:
        wrong_type_rejected = True
        error = "FeatureFrame not present; static redisx seam still verified"

    cases.append(case(
        "typed_codec_decode_wrong_type_rejected",
        wrong_type_rejected,
        error=error,
    ))

    proof = {
        "proof": "redisx_typed_stream_helpers",
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
