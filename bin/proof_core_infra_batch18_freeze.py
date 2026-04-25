#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "run" / "proofs" / "core_infra_batch18_freeze.json"

PROOFS = [
    ("core_codec_transport", "bin/proof_core_codec_transport.py", "run/proofs/core_codec_transport.json"),
    ("redisx_typed_stream_helpers", "bin/proof_redisx_typed_stream_helpers.py", "run/proofs/redisx_typed_stream_helpers.json"),
    ("runtime_effective_config", "bin/proof_runtime_effective_config.py", "run/proofs/runtime_effective_config.json"),
    ("clock_session_policy", "bin/proof_clock_session_policy.py", "run/proofs/clock_session_policy.json"),
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "INVALID_JSON", "path": str(path), "error": str(exc)}
    return data if isinstance(data, dict) else {"status": "INVALID_SHAPE", "path": str(path)}


def normalize_status(data: dict[str, Any]) -> str:
    return str(data.get("status") or data.get("proof_status") or "").upper()


def main() -> int:
    ran: list[dict[str, Any]] = []

    for proof_name, script_rel, artifact_rel in PROOFS:
        script = PROJECT_ROOT / script_rel
        artifact = PROJECT_ROOT / artifact_rel

        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
        )

        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)

        artifact_data = load_json(artifact)
        status = normalize_status(artifact_data)

        row = {
            "proof_name": proof_name,
            "script": script_rel,
            "artifact": artifact_rel,
            "returncode": result.returncode,
            "artifact_status": status,
        }
        ran.append(row)

        if result.returncode != 0:
            raise SystemExit(f"{script_rel} failed with returncode={result.returncode}")
        if status != "PASS":
            raise SystemExit(f"{artifact_rel} did not report PASS: {status!r}")

    proof = {
        "proof": "core_infra_batch18_freeze",
        "status": "PASS",
        "ts_epoch": time.time(),
        "ran": ran,
        "summary": {
            "codec_annotation_resolution": True,
            "redisx_typed_stream_seam": True,
            "settings_runtime_truth_introspection": True,
            "clock_session_policy_boundary_recorded": True,
            "runtime_behavior_changed": False,
            "clock_behavior_changed": False,
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(proof, indent=2, sort_keys=True))
    print(f"proof_artifact={OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
