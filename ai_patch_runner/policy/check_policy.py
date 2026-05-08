#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
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


def _strip_diff_prefix(line: str) -> str:
    # For unified diffs, inspect the actual changed line content, not diff syntax.
    if line.startswith("+") and not line.startswith("+++"):
        return line[1:]
    if line.startswith("-") and not line.startswith("---"):
        return line[1:]
    return line


def _is_non_executable_line(line: str) -> bool:
    stripped = _strip_diff_prefix(line).strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if stripped.startswith(("\"", "'", "{", "}", "[", "]", ":", ",")):
        return True
    if re.match(r"^[A-Za-z0-9_\"']+\s*:", stripped):
        return True
    # markdown/prose bullets are not shell commands
    if stripped.startswith(("- ", "* ", "##", "#")):
        return True
    return False


def command_status(command_text: str, policy: dict) -> dict:
    findings = []

    # Exact dangerous env flags are blocked anywhere.
    for item in policy.get("blocked_env_flags", []):
        if item in command_text:
            findings.append({"type": "blocked_env_flag", "match": item})

    # Command detection must be line-aware. Do not block harmless prose like
    # "external services"; block executable command forms only.
    line_patterns = [
        ("nohup_command", r"^\s*nohup\b"),
        ("systemctl_command", r"^\s*(sudo\s+)?systemctl\b"),
        ("service_command", r"^\s*(sudo\s+)?service\s+[A-Za-z0-9_.@-]+(?:\s+|$)"),
        ("redis_mutation", r"^\s*redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b"),
        ("main_service_start", r"^\s*(python|python3|\.venv/bin/python)\s+-m\s+app\.mme_scalpx\.main\b"),
        ("controlled_paper_enabled", r"SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME\s*=\s*1"),
        ("real_live_allowed_enabled", r"SCALPX_REAL_LIVE_ALLOWED\s*=\s*1"),
        ("allow_real_live_enabled", r"SCALPX_ALLOW_REAL_LIVE\s*=\s*1"),
    ]

    for lineno, raw_line in enumerate(command_text.splitlines(), start=1):
        line = _strip_diff_prefix(raw_line)
        if _is_non_executable_line(line):
            continue
        stripped = line.strip()
        for name, pat in line_patterns:
            if re.search(pat, stripped, flags=re.IGNORECASE):
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
    blocked_service_command = "sudo service redis-server restart"
    allowed_command = 'echo "proof only" && .venv/bin/python -m py_compile ai_patch_runner/generate_command_package.py'
    harmless_text = "This note does not affect external services, broker connections, or live data."
    harmless_diff = """--- real/ai_patch_runner/SANDBOX_AI_PATCH_NOTE.md
+++ sandbox/ai_patch_runner/SANDBOX_AI_PATCH_NOTE.md
@@ -0,0 +1,3 @@
+# Sandbox AI Patch Note
+This note does not affect external services, broker connections, or live data.
+No live Redis trading truth is written.
"""

    blocked_status = command_status(blocked_command, policy)
    blocked_service_status = command_status(blocked_service_command, policy)
    allowed_status = command_status(allowed_command, policy)
    harmless_status = command_status(harmless_text, policy)
    harmless_diff_status = command_status(harmless_diff, policy)

    if blocked_status["command_allowed"] is not False:
        ok = False
    if blocked_service_status["command_allowed"] is not False:
        ok = False
    if allowed_status["command_allowed"] is not True:
        ok = False
    if harmless_status["command_allowed"] is not True:
        ok = False
    if harmless_diff_status["command_allowed"] is not True:
        ok = False

    return {
        "self_test_ok": ok,
        "path_cases": results,
        "blocked_command_case": blocked_status,
        "blocked_service_command_case": blocked_service_status,
        "allowed_command_case": allowed_status,
        "harmless_text_case": harmless_status,
        "harmless_diff_case": harmless_diff_status,
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

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
