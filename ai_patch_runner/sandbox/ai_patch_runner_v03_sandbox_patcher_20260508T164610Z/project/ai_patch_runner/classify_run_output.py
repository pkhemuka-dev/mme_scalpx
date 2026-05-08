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
REPORT_DIR = BASE / "reports"
PROMPT_DIR = BASE / "prompts"

for p in (REPORT_DIR, PROMPT_DIR):
    p.mkdir(parents=True, exist_ok=True)

VERSION = "v0.2"

SYSTEM_PROMPT = """
You are an MME-ScalpX manual-run output classifier.

Return ONLY valid JSON. No markdown. No prose.

Classify a manually-run command package output as:
- PASS
- FAIL
- UNCLEAR

JSON schema:
{
  "verdict": "PASS" | "FAIL" | "UNCLEAR",
  "reason": "short reason",
  "evidence": ["short bullet 1", "short bullet 2"],
  "safety_flags": {
    "broker_calls_detected": true/false,
    "service_starts_detected": true/false,
    "live_redis_writes_detected": true/false,
    "paper_or_live_enabled": true/false,
    "orders_detected": true/false
  },
  "artifact_flags": {
    "proof_json_created": true/false,
    "milestone_created": true/false,
    "manual_run_completed": true/false
  },
  "next_action": "STOP" | "REPAIR_PATCH" | "NEXT_BATCH" | "AUDIT_MORE",
  "next_batch_goal": "short safe next goal"
}

Rules:
- If any broker/order/service/live Redis/paper/live action is detected, verdict must be FAIL.
- If traceback, command not found, missing artifacts, syntax error, or partial/incomplete output appears, verdict must be FAIL or UNCLEAR.
- PASS only if the output clearly shows completion and no safety violation.
- For harmless smoke proof output containing SMOKE_PROOF_OK and no safety grep hits, classify PASS.
"""


def safe_slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:80] or "manual_run"


def extract_json(text: str) -> dict:
    s = text.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if lines[0].strip().startswith("```") and lines[-1].strip() == "```":
            s = "\n".join(lines[1:-1]).strip()

    start = s.find("{")
    end = s.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"No JSON object found in model output: {text[:500]}")
    return json.loads(s[start:end + 1])


def local_precheck(log_text: str) -> dict:
    lower = log_text.lower()

    dangerous = {
        "traceback_detected": "traceback" in lower,
        "command_not_found_detected": "command not found" in lower,
        "systemctl_detected": re.search(r"^\s*(sudo\s+)?systemctl\b", log_text, re.I | re.M) is not None,
        "nohup_detected": re.search(r"^\s*nohup\b", log_text, re.I | re.M) is not None,
        "main_service_start_detected": "app.mme_scalpx.main" in log_text,
        "paper_live_env_detected": any(x in log_text for x in [
            "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME=1",
            "SCALPX_REAL_LIVE_ALLOWED=1",
            "SCALPX_ALLOW_REAL_LIVE=1",
        ]),
        "redis_write_detected": re.search(r"redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b", log_text, re.I) is not None,
    }

    positive = {
        "smoke_proof_ok_detected": "SMOKE_PROOF_OK" in log_text,
        "proof_path_detected": "run/proofs/" in log_text,
        "milestone_path_detected": "docs/milestones/" in log_text,
    }

    return {
        "dangerous": dangerous,
        "positive": positive,
        "local_safety_clear": not any(dangerous.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True, help="Manual-run log path")
    parser.add_argument("--batch", default="", help="Optional batch label")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5.5"))
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set")

    log_path = Path(args.log)
    if not log_path.exists():
        raise SystemExit(f"Log file not found: {log_path}")

    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    precheck = local_precheck(log_text)

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")
    slug = safe_slug(args.batch or log_path.stem)

    prompt_path = PROMPT_DIR / f"{ts}_{slug}_classifier_prompt.json"
    report_path = REPORT_DIR / f"{ts}_{slug}_classification.json"

    prompt_record = {
        "created_at": now.isoformat(),
        "version": VERSION,
        "batch": args.batch,
        "log_path": str(log_path),
        "model": args.model,
        "mode": "classify_manual_run_output_only_no_execution",
        "local_precheck": precheck,
    }
    prompt_path.write_text(json.dumps(prompt_record, indent=2), encoding="utf-8")

    user_prompt = f"""
Classify this MME-ScalpX manual-run output.

Batch label: {args.batch}
Log path: {log_path}

Local precheck:
{json.dumps(precheck, indent=2)}

Manual-run log:
{log_text[-24000:]}
"""

    client = OpenAI()
    response = client.responses.create(
        model=args.model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    model_json = extract_json(response.output_text)

    report = {
        "created_at": now.isoformat(),
        "version": VERSION,
        "batch": args.batch,
        "log_path": str(log_path),
        "model": args.model,
        "mode": "classify_manual_run_output_only_no_execution",
        "prompt_path": str(prompt_path),
        "local_precheck": precheck,
        "model_classification": model_json,
        "runner_safety": {
            "executed_commands": False,
            "patched_project": False,
            "called_broker": False,
            "started_services": False,
            "wrote_live_redis": False,
            "enabled_paper_or_live": False
        }
    }

    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"AI PATCH RUNNER {VERSION} CLASSIFICATION COMPLETE")
    print(f"Report: {report_path}")
    print(json.dumps(model_json, indent=2, sort_keys=True))

    verdict = model_json.get("verdict")
    if verdict == "PASS":
        return 0
    if verdict == "UNCLEAR":
        return 3
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
