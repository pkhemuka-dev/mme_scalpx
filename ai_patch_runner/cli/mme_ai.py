#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
PYBIN = ROOT / ".venv" / "bin" / "python"
GENERATOR = ROOT / "ai_patch_runner" / "replay_next_batch_generator.py"
OUT_DIR = ROOT / "ai_patch_runner" / "outputs"
REPORT_DIR = ROOT / "ai_patch_runner" / "reports"
LOG_DIR = ROOT / "ai_patch_runner" / "logs"


def run(cmd: list[str], *, check: bool = False, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=check,
    )


def latest(pattern: str) -> Path | None:
    files = sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def latest_meta() -> Path | None:
    metas = sorted(REPORT_DIR.glob("*_meta.json"), key=lambda p: p.stat().st_mtime)
    return metas[-1] if metas else None


def latest_valid_meta() -> Path | None:
    metas = sorted(REPORT_DIR.glob("*_meta.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    for m in metas:
        try:
            data = load_json(m)
        except Exception:
            continue
        if data.get("static_validation_ok") is True and (data.get("policy_validation") or {}).get("ok") is True:
            out = data.get("output_script")
            if out and Path(out).exists():
                return m
    return None


def latest_proof() -> Path | None:
    patterns = [
        "run/proofs/proof_replay_data_a26_guarded_selector_execution_decision_*.json",
        "run/proofs/proof_replay_data_a25_guarded_selector_command_gate_*.json",
        "run/proofs/proof_replay_data_a24_guarded_selector_cli_command_construction_*.json",
        "run/proofs/proof_replay_data_a23_selector_cli_scope_blocker_classifier_*.json",
        "run/proofs/proof_replay_data_a21_guarded_selector_only_dry_run_*.json",
        "run/proofs/proof_replay_data_a20_guarded_selector_only_plan_run_*.json",
        "run/proofs/proof_replay_data_a19_selector_engine_consumption_probe_*.json",
        "run/proofs/proof_replay_data_a18_execution_shadow_semantic_normalization_*.json",
        "run/proofs/proof_replay_data_a17_engine_readiness_blocker_*.json",
        "run/proofs/proof_replay_data_a16_contract_shape_audit_*.json",
        "run/proofs/proof_replay_data_a15_selector_surface_probe_*.json",
        "run/proofs/proof_replay_data_a15_*.json",
        "run/proofs/proof_replay_data_a14_execution_shadow_*.json",
        "run/proofs/proof_replay_data_a13_risk_outputs_shadow_*.json",
        "run/proofs/proof_replay_data_a12_strategy_decisions_shadow_*.json",
        "run/proofs/proof_replay_data_a11_features_rows_reconstruction_*.json",
        "run/proofs/proof_replay_data_a10_selector_only_cli_dry_probe_*.json",
        "run/proofs/proof_ai_replay_r22_mme_ai_shortcuts_*.json",
        "run/proofs/proof_ai_replay_r21_a11_to_a12_classifier_repair_*.json",
    ]
    found = []
    for pat in patterns:
        found.extend(ROOT.glob(pat))
    return max(found, key=lambda p: p.stat().st_mtime) if found else None


def meta_summary(meta_path: Path) -> dict[str, Any]:
    meta = load_json(meta_path)
    return {
        "meta": str(meta_path.relative_to(ROOT)),
        "output_script": meta.get("output_script"),
        "expected_batch": meta.get("expected_batch"),
        "static_validation_ok": meta.get("static_validation_ok"),
        "policy_validation_ok": (meta.get("policy_validation") or {}).get("ok"),
        "classification": (meta.get("local_classification") or {}).get("verdict"),
    }


def cmd_ok(_: argparse.Namespace) -> int:
    os.environ["SCALPX_OBSERVE_ONLY"] = "1"
    for k in [
        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
        "SCALPX_REAL_LIVE_ALLOWED",
        "SCALPX_ALLOW_REAL_LIVE",
    ]:
        os.environ.pop(k, None)

    print("===== MOK: GENERATE NEXT VALIDATED PACKAGE ONLY =====")
    p = subprocess.run([str(PYBIN), str(GENERATOR)], cwd=str(ROOT), text=True)
    return p.returncode


def cmd_show(args: argparse.Namespace) -> int:
    meta_path = latest_valid_meta() or latest_meta()
    if not meta_path:
        print("No meta file found.")
        return 1
    summary = meta_summary(meta_path)
    script = Path(summary["output_script"]) if summary.get("output_script") else None

    print("===== MSHOW: LATEST VALID GENERATED PACKAGE =====")
    print(json.dumps(summary, indent=2, sort_keys=True))

    if script and script.exists():
        print("===== SCRIPT HEAD =====")
        lines = script.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines[: args.lines]:
            print(line)
    else:
        print("No script found from latest meta.")
        return 1
    return 0


def guard_script(script: Path, meta: dict[str, Any]) -> None:
    assert meta.get("static_validation_ok") is True, "static_validation_ok is not true"
    assert (meta.get("policy_validation") or {}).get("ok") is True, "policy_validation_ok is not true"
    assert script.exists(), f"script missing: {script}"
    assert "ai_patch_runner/outputs" in str(script), f"unexpected script path: {script}"
    assert "replay_data_" in script.name, f"not a replay_data script: {script.name}"

    text = script.read_text(encoding="utf-8", errors="replace")

    blocked_line_patterns = [
        ("nohup", r"^\s*nohup\b"),
        ("systemctl", r"^\s*(sudo\s+)?systemctl\b"),
        ("service", r"^\s*(sudo\s+)?service\s+[A-Za-z0-9_.@-]+"),
        ("main_runtime", r"^\s*(python|python3|\.venv/bin/python)\s+-m\s+app\.mme_scalpx\.main\b"),
        ("redis_write", r"^\s*redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b"),
        ("paper_live_env", r"SCALPX_(ALLOW_CONTROLLED_PAPER_RUNTIME|REAL_LIVE_ALLOWED|ALLOW_REAL_LIVE)\s*=\s*1"),
    ]

    hits = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for name, pat in blocked_line_patterns:
            if re.search(pat, stripped, flags=re.I):
                hits.append({"line": lineno, "kind": name, "text": stripped[:180]})
    assert not hits, f"blocked patterns found: {hits}"


def cmd_run(_: argparse.Namespace) -> int:
    meta_path = latest_valid_meta()
    if not meta_path:
        print("No validated meta found.")
        return 1

    meta = load_json(meta_path)
    script = Path(meta["output_script"])

    print("===== MRUN: GUARDED RUN OF LATEST VALIDATED PACKAGE =====")
    print(json.dumps(meta_summary(meta_path), indent=2, sort_keys=True))

    guard_script(script, meta)
    print("RUN_GUARD_OK=true")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f"mrun_{script.stem}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
    print(f"LOG={log.relative_to(ROOT)}")

    with log.open("w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            ["bash", str(script)],
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            print(line, end="")
            f.write(line)
        rc = proc.wait()

    print(f"MRUN_RC={rc}")
    return rc



def cmd_remember(_: argparse.Namespace) -> int:
    builder = Path("/tmp/build_ai_replay_memory.py")
    project_builder = ROOT / "ai_patch_runner" / "cli" / "build_ai_replay_memory.py"
    if project_builder.exists():
        cmd = [str(PYBIN), str(project_builder)]
    elif builder.exists():
        cmd = [str(PYBIN), str(builder)]
    else:
        print("Memory builder missing.")
        return 1
    p = subprocess.run(cmd, cwd=str(ROOT), text=True)
    return p.returncode


def cmd_status(_: argparse.Namespace) -> int:
    print("===== MSTAT: STATUS =====")
    proof = latest_proof()
    meta = latest_meta()
    valid_meta = latest_valid_meta()

    out = {
        "latest_proof": str(proof.relative_to(ROOT)) if proof else None,
        "latest_meta": str(meta.relative_to(ROOT)) if meta else None,
        "latest_valid_meta": str(valid_meta.relative_to(ROOT)) if valid_meta else None,
    }

    if proof:
        try:
            data = load_json(proof)
            out["latest_proof_batch"] = data.get("batch")
            out["latest_proof_summary"] = data.get("summary")
            out["latest_proof_verdict"] = data.get("verdict") or (data.get("summary") or {}).get("overall_verdict")
        except Exception as exc:
            out["latest_proof_error"] = repr(exc)

    if meta:
        try:
            out["latest_meta_summary"] = meta_summary(meta)
        except Exception as exc:
            out["latest_meta_error"] = repr(exc)

    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="mme-ai")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ok")
    show = sub.add_parser("show")
    show.add_argument("--lines", type=int, default=180)
    sub.add_parser("run")
    sub.add_parser("status")
    sub.add_parser("remember")

    args = parser.parse_args()

    if args.cmd == "ok":
        return cmd_ok(args)
    if args.cmd == "show":
        return cmd_show(args)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "status":
        return cmd_status(args)
    if args.cmd == "remember":
        return cmd_remember(args)

    raise SystemExit(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
