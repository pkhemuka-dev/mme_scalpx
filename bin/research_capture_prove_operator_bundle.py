from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = PROJECT_ROOT / ".venv" / "bin" / "python"

PROOF_SCRIPTS: tuple[str, ...] = (
    "bin/research_capture_prove_optional_audit_roundtrip.py",
    "bin/research_capture_prove_manifest_report_surfaces.py",
)


@dataclass(frozen=True, slots=True)
class ProofResult:
    script: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _run_proof(script_rel: str) -> ProofResult:
    script_path = (PROJECT_ROOT / script_rel).resolve()
    if not script_path.exists():
        raise FileNotFoundError(f"required proof script missing: {script_path}")

    env = dict(os.environ)
    current_pythonpath = env.get("PYTHONPATH", "")
    project_root_str = str(PROJECT_ROOT)
    if current_pythonpath:
        if project_root_str not in current_pythonpath.split(os.pathsep):
            env["PYTHONPATH"] = project_root_str + os.pathsep + current_pythonpath
    else:
        env["PYTHONPATH"] = project_root_str

    completed = subprocess.run(
        [str(PYTHON_BIN), str(script_path)],
        cwd=str(PROJECT_ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    return ProofResult(
        script=script_rel,
        returncode=int(completed.returncode),
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def main() -> None:
    if not PYTHON_BIN.exists():
        raise FileNotFoundError(f"python interpreter not found: {PYTHON_BIN}")

    results: list[ProofResult] = []
    for script_rel in PROOF_SCRIPTS:
        result = _run_proof(script_rel)
        results.append(result)

        print(f"===== PROOF: {script_rel} =====")
        print(f"returncode={result.returncode}")
        if result.stdout.strip():
            print("--- stdout ---")
            print(result.stdout.rstrip())
        else:
            print("--- stdout ---")
            print("<empty>")
        if result.stderr.strip():
            print("--- stderr ---")
            print(result.stderr.rstrip())
        print()

    failed = [result for result in results if not result.ok]

    print("===== OPERATOR SUMMARY =====")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"{status} :: {result.script}")

    print(f"proof_count={len(results)}")
    print(f"passed_count={sum(1 for result in results if result.ok)}")
    print(f"failed_count={len(failed)}")

    if failed:
        failed_names = ", ".join(result.script for result in failed)
        raise SystemExit(f"operator bundle failed: {failed_names}")

    print("status=GREEN")


if __name__ == "__main__":
    main()
