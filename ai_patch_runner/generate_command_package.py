#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
BASE = ROOT / "ai_patch_runner"
OUT_DIR = BASE / "outputs"
REPORT_DIR = BASE / "reports"
PROMPT_DIR = BASE / "prompts"
STATE_DIR = BASE / "state"

for p in (OUT_DIR, REPORT_DIR, PROMPT_DIR, STATE_DIR):
    p.mkdir(parents=True, exist_ok=True)


VERSION = "v0.1.3"

SYSTEM_PROMPT = """
You are an MME-ScalpX freeze-final command-package generator.

Return ONLY raw bash. No markdown fences. No explanation. No prose before bash.
The first line must be exactly:
cd /home/Lenovo/scalpx/projects/mme_scalpx

ABSOLUTE SAFETY RULES:
- Do not enable paper_armed.
- Do not enable real live trading.
- Do not set SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1.
- Do not set SCALPX_REAL_LIVE_ALLOWED=1.
- Do not set SCALPX_ALLOW_REAL_LIVE=1.
- Do not call broker login.
- Do not place orders.
- Do not start services.
- Do not use nohup as a command.
- Do not use systemctl as a command.
- Do not write live Redis trading truth.
- Do not execute redis-cli SET/HSET/XADD/DEL on live trading keys.
- Do not patch execution/risk/broker/main live-control files unless the user goal explicitly asks for an audit-only proof.
- If evidence is insufficient, generate audit-only proof, not production patch.

MANDATORY COMMAND PACKAGE STYLE:
- Start with cd /home/Lenovo/scalpx/projects/mme_scalpx
- Use set -euo pipefail
- Resolve PYBIN as .venv/bin/python else python3
- Export PYTHONPATH safely
- Create run/proofs, docs/milestones, run/_code_backups, run/audits as needed
- Inspect before patch
- Back up any inspected/target file before patch
- Generate JSON proof under run/proofs
- Generate milestone markdown under docs/milestones
- Include compile/import proof if Python files are touched
- Include safety flags:
  broker_calls_executed=false
  service_starts_executed=false
  live_redis_writes_executed=false
  paper_or_live_enabled=false
- Prefer audit-only unless patch is clearly safe

CRITICAL HEREDOC LAW:
- Every embedded Python heredoc MUST use a single-quoted delimiter.
- Correct: "$PYBIN" - <<'PY'
- Wrong:   "$PYBIN" - <<PY
- Correct: python3 - <<'PY'
- Wrong:   python3 - <<PY
- If you need shell variables inside Python, export them before the heredoc and read them using os.environ inside Python.

OUTPUT FORMAT:
- Raw bash only.
- No markdown.
- No explanation.
- No code fences.
"""


def safe_slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:80] or "mme_ai_batch"


def normalize_generated_script(script_text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    s = script_text.strip()

    # Strip one or more outer markdown fence wrappers if present.
    changed = True
    while changed:
        changed = False
        lines = s.splitlines()
        if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
            s = "\n".join(lines[1:-1]).strip()
            notes.append("outer_markdown_fence_stripped")
            changed = True

    # If model produced prose before the project cd, keep only from the required cd line.
    required = "cd /home/Lenovo/scalpx/projects/mme_scalpx"
    idx = s.find(required)
    if idx > 0:
        s = s[idx:].strip()
        notes.append("prose_before_required_cd_stripped")

    return s.rstrip() + "\n", notes


def _is_comment_or_data_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    # JSON/Python string/data attestations should not be treated as executable commands.
    if stripped.startswith(('"', "'", "{", "}", ":", ",")):
        return True
    if re.match(r"^[A-Za-z0-9_]+[\"']?\s*:", stripped):
        return True
    return False


def validate_generated_script(script_text: str) -> tuple[bool, list[str]]:
    findings: list[str] = []

    if "```" in script_text:
        findings.append("markdown_fence_detected_after_normalization")

    required = "cd /home/Lenovo/scalpx/projects/mme_scalpx"
    if not script_text.startswith(required):
        findings.append("script_does_not_start_with_required_project_cd")

    if "set -euo pipefail" not in script_text:
        findings.append("missing_set_euo_pipefail")

    # Block unquoted heredocs where bash could expand Python/body content.
    unquoted_patterns = [
        r"<<PY\b",
        r"<<\s*PY\b",
        r"<<EOF\b",
        r"<<\s*EOF\b",
        r"<<JSON\b",
        r"<<\s*JSON\b",
    ]
    for pat in unquoted_patterns:
        for m in re.finditer(pat, script_text):
            start = max(0, m.start() - 80)
            end = min(len(script_text), m.end() + 80)
            snippet = script_text[start:end].replace("\n", "\\n")
            findings.append(f"unquoted_heredoc_detected: {pat}: ...{snippet}...")

    executable_danger_patterns = [
        ("nohup_command", r"^\s*nohup\b"),
        ("systemctl_command", r"^\s*(sudo\s+)?systemctl\b"),
        ("app_main_service_start", r"app\.mme_scalpx\.main"),
        ("controlled_paper_enabled", r"SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME\s*=\s*1"),
        ("real_live_allowed_enabled", r"SCALPX_REAL_LIVE_ALLOWED\s*=\s*1"),
        ("allow_real_live_enabled", r"SCALPX_ALLOW_REAL_LIVE\s*=\s*1"),
        ("redis_live_mutation", r"redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b"),
    ]

    for lineno, line in enumerate(script_text.splitlines(), start=1):
        if _is_comment_or_data_line(line):
            continue
        for name, pat in executable_danger_patterns:
            if re.search(pat, line, flags=re.IGNORECASE):
                findings.append(f"{name}_detected_line_{lineno}: {line.strip()}")

    return (len(findings) == 0), findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True, help="Batch name, e.g. AI-V013-SMOKE")
    parser.add_argument("--goal", required=True, help="Goal for command package")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5.5"))
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set. Add it to ~/.bashrc and source ~/.bashrc")

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")
    slug = safe_slug(args.batch)

    user_prompt = f"""
Batch: {args.batch}

Goal:
{args.goal}

Important:
This is AI Patch Runner {VERSION}. Generate command package only.
The generated package itself must remain safe and proof-oriented.
Do not include commands that start services, call brokers, enable paper/live, or mutate live Redis trading truth.
All embedded Python heredocs must use single-quoted delimiters exactly like <<'PY'.
Return raw bash only. No markdown fences.
"""

    prompt_record = {
        "created_at": now.isoformat(),
        "batch": args.batch,
        "goal": args.goal,
        "model": args.model,
        "mode": f"{VERSION}_generate_only_no_run_with_static_validation",
        "safety": {
            "runs_generated_script": False,
            "patches_project": False,
            "starts_services": False,
            "calls_broker": False,
            "writes_live_redis": False,
            "enables_paper_or_live": False,
        },
    }

    prompt_path = PROMPT_DIR / f"{ts}_{slug}_prompt.json"
    prompt_path.write_text(json.dumps(prompt_record, indent=2), encoding="utf-8")

    client = OpenAI()

    response = client.responses.create(
        model=args.model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_script_text = response.output_text.strip() + "\n"
    script_text, normalization_notes = normalize_generated_script(raw_script_text)
    validation_ok, findings = validate_generated_script(script_text)
    display_findings = [f"normalization_note: {x}" for x in normalization_notes] + findings

    script_path = OUT_DIR / f"{ts}_{slug}.sh"
    meta_path = REPORT_DIR / f"{ts}_{slug}_meta.json"

    script_path.write_text(script_text, encoding="utf-8")
    script_path.chmod(0o600)

    meta = {
        "created_at": now.isoformat(),
        "batch": args.batch,
        "goal": args.goal,
        "model": args.model,
        "mode": f"{VERSION}_generate_only_no_run_with_static_validation",
        "script_path": str(script_path),
        "prompt_path": str(prompt_path),
        "validation": {
            "static_validation_ok": validation_ok,
            "findings": display_findings,
            "normalization_supported": True,
            "outer_markdown_fence_cleanup": True,
            "line_aware_danger_validation": True,
        },
        "safety": {
            "script_generated": True,
            "script_executed": False,
            "project_patched_by_runner": False,
            "broker_calls_executed": False,
            "service_starts_executed": False,
            "live_redis_writes_executed": False,
            "paper_or_live_enabled": False,
        },
        "next_manual_step": (
            f"Review script manually: less {script_path}"
            if validation_ok
            else f"DO NOT RUN. Static validation failed. See {meta_path}"
        ),
    }

    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"AI PATCH RUNNER {VERSION} COMPLETE")
    print(f"Script generated: {script_path}")
    print(f"Metadata:         {meta_path}")
    print(f"Static validation ok: {validation_ok}")
    if display_findings:
        print("Findings:")
        for f in display_findings:
            print(f"  - {f}")
    print()
    print(f"IMPORTANT: {VERSION} does not run the script.")
    if not validation_ok:
        print("DO NOT RUN generated script. Static validation failed.")
        return 2
    print("Review manually before running anything.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
