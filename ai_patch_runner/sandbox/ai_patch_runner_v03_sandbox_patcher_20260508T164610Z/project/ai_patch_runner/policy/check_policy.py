#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
POLICY_PATH = ROOT / "ai_patch_runner" / "policy" / "ai_patch_policy.json"


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def normalize(path: str) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.resolve().relative_to(ROOT)).replace("\\", "/")
        except Exception:
            return str(p).replace("\\", "/")
    return str(p).replace("\\", "/")


def path_status(path: str, policy: dict) -> dict:
    rel = normalize(path)

    blocked_exact_or_prefix = []
    for b in policy.get("blocked_auto_touch_paths", []):
        b_norm = b.rstrip("/")
        if rel == b_norm or rel.startswith(b_norm + "/"):
            blocked_exact_or_prefix.append(b)

    blocked_globs = []
    for g in policy.get("blocked_auto_touch_globs", []):
        if fnmatch.fnmatch(rel, g):
            blocked_globs.append(g)

    allowed_prefixes = []
    for a in policy.get("allowed_auto_touch_prefixes", []):
        if rel.startswith(a):
            allowed_prefixes.append(a)

    human_review_prefixes = []
    for h in policy.get("human_review_required_prefixes", []):
        if rel.startswith(h):
            human_review_prefixes.append(h)

    blocked = bool(blocked_exact_or_prefix or blocked_globs)
    allowed_auto = bool(allowed_prefixes) and not blocked and not human_review_prefixes
    human_review_required = bool(human_review_prefixes or blocked)

    return {
        "path": path,
        "relative_path": rel,
        "allowed_auto_touch": allowed_auto,
        "human_review_required": human_review_required,
        "blocked_auto_touch": blocked,
        "matched_allowed_prefixes": allowed_prefixes,
        "matched_human_review_prefixes": human_review_prefixes,
        "matched_blocked_paths": blocked_exact_or_prefix,
        "matched_blocked_globs": blocked_globs,
    }


def command_status(command_text: str, policy: dict) -> dict:
    findings = []

    blocked_cmds = policy.get("blocked_runtime_commands", [])
    for item in blocked_cmds:
        if item in command_text:
            findings.append({"type": "blocked_runtime_command", "match": item})

    blocked_env = policy.get("blocked_env_flags", [])
    for item in blocked_env:
        if item in command_text:
            findings.append({"type": "blocked_env_flag", "match": item})

    line_patterns = [
        ("nohup_command", r"^\s*nohup\b"),
        ("systemctl_command", r"^\s*(sudo\s+)?systemctl\b"),
        ("redis_mutation", r"redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b"),
        ("main_service_start", r"python\s+-m\s+app\.mme_scalpx\.main|\.venv/bin/python\s+-m\s+app\.mme_scalpx\.main"),
    ]

    for lineno, line in enumerate(command_text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for name, pat in line_patterns:
            if re.search(pat, line, flags=re.IGNORECASE):
                findings.append({"type": name, "line": lineno, "text": stripped})

    return {
        "command_allowed": not findings,
        "findings": findings,
    }


def self_test(policy: dict) -> dict:
    cases = {
        "ai_patch_runner/generate_command_package.py": True,
        "run/proofs/proof_x.json": True,
        "docs/milestones/x.md": True,
        "app/mme_scalpx/services/execution.py": False,
        "app/mme_scalpx/services/risk.py": False,
        "app/mme_scalpx/main.py": False,
        "etc/brokers/dhan.yaml": False,
        "common/secrets/brokers/dhan/credentials.env": False,
    }

    results = {}
    ok = True
    for path, expected_allowed in cases.items():
        status = path_status(path, policy)
        actual = status["allowed_auto_touch"]
        results[path] = {
            "expected_allowed_auto_touch": expected_allowed,
            "actual_allowed_auto_touch": actual,
            "status": status,
        }
        if actual != expected_allowed:
            ok = False

    blocked_command = "nohup .venv/bin/python -m app.mme_scalpx.main --service feeds"
    allowed_command = 'echo "proof only" && .venv/bin/python -m py_compile ai_patch_runner/generate_command_package.py'

    blocked_status = command_status(blocked_command, policy)
    allowed_status = command_status(allowed_command, policy)

    if blocked_status["command_allowed"] is not False:
        ok = False
    if allowed_status["command_allowed"] is not True:
        ok = False

    return {
        "self_test_ok": ok,
        "path_cases": results,
        "blocked_command_case": blocked_status,
        "allowed_command_case": allowed_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--command-file")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    policy = load_policy()
    result = {
        "policy_version": policy.get("policy_version"),
        "policy_path": str(POLICY_PATH),
        "paths": [path_status(p, policy) for p in args.path],
        "command": None,
        "self_test": None,
    }

    if args.command_file:
        command_text = Path(args.command_file).read_text(encoding="utf-8", errors="replace")
        result["command"] = command_status(command_text, policy)

    if args.self_test:
        result["self_test"] = self_test(policy)

    ok = True
    for p in result["paths"]:
        if p["blocked_auto_touch"]:
            ok = False
    if result["command"] and not result["command"]["command_allowed"]:
        ok = False
    if result["self_test"] and not result["self_test"]["self_test_ok"]:
        ok = False

    result["ok"] = ok

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
