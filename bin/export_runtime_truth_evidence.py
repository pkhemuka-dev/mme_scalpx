#!/usr/bin/env python3
from __future__ import annotations

"""
Batch 21 evidence exporter.

Creates a redacted, non-empty config/systemd evidence pack for audit.
Read-only. Does not change runtime behavior.
"""

import json
import os
import re
import shutil
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = ROOT / "run" / "audit_exports" / f"runtime_truth_evidence_{TS}"
TAR_PATH = ROOT / "run" / "audit_exports" / f"runtime_truth_evidence_{TS}.tar.gz"
MANIFEST_PATH = OUT_DIR / "manifest.json"

SECRET_PAT = re.compile(
    r"(?i)(token|secret|password|passwd|api[_-]?key|access[_-]?key|client[_-]?secret|authorization|auth)"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_text(text: str) -> str:
    out_lines = []
    for line in text.splitlines():
        raw = line
        if SECRET_PAT.search(line):
            if "=" in line:
                k, _ = line.split("=", 1)
                raw = f"{k}=<REDACTED>"
            elif ":" in line:
                k, _ = line.split(":", 1)
                raw = f"{k}: <REDACTED>"
            else:
                raw = "<REDACTED_SECRET_LINE>"
        out_lines.append(raw)
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")


def safe_read(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except Exception as exc:
        return f"<READ_ERROR {exc!r}>\n"


def write_redacted(src: Path, dst: Path) -> dict[str, Any]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = safe_read(src)
    redacted = redact_text(text)
    dst.write_text(redacted)
    return {
        "src": str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src),
        "dst": str(dst.relative_to(OUT_DIR)),
        "exists": src.exists(),
        "bytes_redacted": len(redacted.encode()),
    }


def run_cmd(args: list[str], dst: Path, timeout: int = 20) -> dict[str, Any]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        p = subprocess.run(
            args,
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        text = "$ " + " ".join(args) + "\n"
        text += f"returncode={p.returncode}\n\nSTDOUT:\n{p.stdout}\n\nSTDERR:\n{p.stderr}\n"
        dst.write_text(redact_text(text))
        return {"cmd": args, "returncode": p.returncode, "dst": str(dst.relative_to(OUT_DIR))}
    except Exception as exc:
        dst.write_text(f"$ {' '.join(args)}\nERROR: {exc!r}\n")
        return {"cmd": args, "error": repr(exc), "dst": str(dst.relative_to(OUT_DIR))}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "generated_at": now_iso(),
        "project_root": str(ROOT),
        "files": [],
        "commands": [],
        "notes": [
            "Secrets are redacted by key-name heuristic.",
            "This export is read-only.",
            "This pack is intended to fix the prior empty etc_redacted evidence gap.",
        ],
    }

    # Config files/directories that matter for runtime truth.
    include_paths = [
        ROOT / "etc" / "runtime.yaml",
        ROOT / "etc" / "project.env",
        ROOT / "etc" / "proof_registry.yaml",
        ROOT / "etc" / "config_registry.yaml",
    ]

    for pattern in [
        "etc/brokers/**/*.yaml",
        "etc/brokers/**/*.yml",
        "etc/strategy_family/**/*.yaml",
        "etc/strategy_family/**/*.yml",
        "etc/systemd/**/*.service",
        "etc/systemd/**/*.conf",
    ]:
        include_paths.extend(sorted(ROOT.glob(pattern)))

    seen = set()
    for src in include_paths:
        if src in seen:
            continue
        seen.add(src)
        if src.exists() and src.is_file():
            rel = src.relative_to(ROOT)
            dst = OUT_DIR / "etc_redacted" / rel
            manifest["files"].append(write_redacted(src, dst))
        else:
            manifest["files"].append({
                "src": str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src),
                "exists": False,
                "missing": True,
            })

    # Systemd live evidence.
    manifest["commands"].append(run_cmd(
        ["systemctl", "cat", "scalpx-mme.service"],
        OUT_DIR / "systemd_snapshot" / "systemctl_cat_scalpx-mme.service.txt",
    ))
    manifest["commands"].append(run_cmd(
        ["systemctl", "show", "scalpx-mme.service", "--property=Environment", "--property=FragmentPath", "--property=DropInPaths", "--property=ExecStart"],
        OUT_DIR / "systemd_snapshot" / "systemctl_show_scalpx-mme.service.txt",
    ))

    # Git context.
    manifest["commands"].append(run_cmd(["git", "status", "--short"], OUT_DIR / "git" / "status_short.txt"))
    manifest["commands"].append(run_cmd(["git", "diff", "--stat"], OUT_DIR / "git" / "diff_stat.txt"))

    # Existing runtime proof snapshots, if any.
    for proof in [
        ROOT / "run" / "proofs" / "runtime_effective_config.json",
        ROOT / "run" / "proofs" / "proof_config_runtime_truth.json",
        ROOT / "run" / "proofs" / "proof_runtime_truth_authority.json",
    ]:
        if proof.exists():
            dst = OUT_DIR / "run_proofs" / proof.name
            manifest["files"].append(write_redacted(proof, dst))

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True))

    with tarfile.open(TAR_PATH, "w:gz") as tf:
        tf.add(OUT_DIR, arcname=OUT_DIR.name)

    print(json.dumps({
        "status": "PASS",
        "out_dir": str(OUT_DIR.relative_to(ROOT)),
        "tar": str(TAR_PATH.relative_to(ROOT)),
        "manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "file_count": len(manifest["files"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
