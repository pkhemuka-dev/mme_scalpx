#!/usr/bin/env python3
"""Offline/manual micro-real readiness checker. Never transmits orders."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.mme_scalpx.services.micro_real_readiness_gate import (
    MicroRealReadinessInputs,
    evaluate_micro_real_readiness,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-json")
    args = parser.parse_args()

    payload = json.loads(Path(args.input_json).read_text())
    result = evaluate_micro_real_readiness(MicroRealReadinessInputs(**payload))
    record = result.to_record()

    text = json.dumps(record, indent=2, sort_keys=True)
    print(text)

    if args.output_json:
        Path(args.output_json).write_text(text + "\n")

    return 0 if record["decision"] == "READY_FOR_MANUAL_AUTHORIZATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
