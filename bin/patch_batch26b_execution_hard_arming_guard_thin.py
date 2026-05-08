#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import re
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXECUTION = ROOT / "app/mme_scalpx/services/execution.py"
CPR = ROOT / "app/mme_scalpx/services/controlled_paper_runtime.py"
PATCH_STEP = ROOT / "run/proofs/batch26b_execution_hard_arming_guard_thin_patch_step.json"

RUNTIME_BEGIN = "# BEGIN BATCH26B_CONTROLLED_EXECUTION_ENTRY_ARMING_CONTRACT"
RUNTIME_END = "# END BATCH26B_CONTROLLED_EXECUTION_ENTRY_ARMING_CONTRACT"
HELPER_BEGIN = "# BEGIN BATCH26B_EXECUTION_ENTRY_HARD_ARMING_HELPER"
HELPER_END = "# END BATCH26B_EXECUTION_ENTRY_HARD_ARMING_HELPER"
GUARD_MARKER = "# BATCH26B_EXECUTION_ENTRY_HARD_ARMING_GUARD"

RUNTIME_CONTRACT = f'''
{RUNTIME_BEGIN}
def controlled_execution_entry_allowed() -> bool:
    """
    Fail-closed execution-entry arming contract.

    Current safety state:
    - observe_only / HOLD-report-only remains default
    - paper_armed is blocked
    - real live trading is blocked

    This function intentionally returns False in Batch 26B.
    Any future change to True requires a separate explicit proof batch.
    """
    return False
{RUNTIME_END}
'''

HELPER = f'''
{HELPER_BEGIN}
def _batch26b_execution_entry_hard_arming_verdict():
    """
    Execution-owned hard gate for ENTRY broker calls.

    This is deliberately independent of strategy and risk:
    - strategy may emit only HOLD/report-only today
    - risk may veto entries but never exits
    - execution must still fail closed before ENTRY broker calls

    EXIT broker calls are not blocked by this helper.
    """
    try:
        from app.mme_scalpx.services.controlled_paper_runtime import (
            controlled_execution_entry_allowed,
        )
    except Exception as exc:
        return False, f"execution_entry_arming_contract_unavailable:{{type(exc).__name__}}:{{exc}}"

    try:
        allowed = bool(controlled_execution_entry_allowed())
    except Exception as exc:
        return False, f"execution_entry_arming_contract_error:{{type(exc).__name__}}:{{exc}}"

    if not allowed:
        return False, "execution_entry_not_armed"

    return True, "execution_entry_armed"
{HELPER_END}

'''


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def find_actual_entry_calls(text: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if "self.broker.place_entry_order(" in line and not line.strip().startswith("#"):
            out.append({"line": lineno, "text": line.rstrip()})
    return out


def find_actual_exit_calls(text: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if "self.broker.place_exit_order(" in line and not line.strip().startswith("#"):
            out.append({"line": lineno, "text": line.rstrip()})
    return out


def guarded_entry_calls(text: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    lines = text.splitlines()
    guarded: list[dict[str, object]] = []
    unguarded: list[dict[str, object]] = []
    for call in find_actual_entry_calls(text):
        idx = int(call["line"]) - 1
        window = "\n".join(lines[max(0, idx - 12):idx])
        if GUARD_MARKER in window and "_batch26b_execution_entry_hard_arming_verdict()" in window and "self._fail_decision(decision, entry_arm_reason)" in window:
            guarded.append(call)
        else:
            unguarded.append(call)
    return guarded, unguarded


def install_runtime_contract(text: str) -> tuple[str, bool]:
    if "def controlled_execution_entry_allowed(" in text:
        return text, False
    return text.rstrip() + "\n\n" + RUNTIME_CONTRACT.lstrip() + "\n", True


def install_helper(text: str) -> tuple[str, bool]:
    if "_batch26b_execution_entry_hard_arming_verdict" in text:
        return text, False

    # Insert after imports/constant surfaces but before first class/dataclass.
    insert_points = [x for x in [text.find("\n@dataclass"), text.find("\nclass ")] if x != -1]
    if not insert_points:
        raise SystemExit("No safe helper insertion point found in execution.py")

    idx = min(insert_points)
    return text[:idx + 1] + HELPER + text[idx + 1:], True


def install_entry_guard(text: str) -> tuple[str, int]:
    calls = find_actual_entry_calls(text)
    if not calls:
        raise SystemExit("No self.broker.place_entry_order(...) call found; refusing blind patch")

    lines = text.splitlines()
    out: list[str] = []
    inserted = 0

    for lineno, line in enumerate(lines, 1):
        if "self.broker.place_entry_order(" in line and not line.strip().startswith("#"):
            prior = "\n".join(out[-12:])
            if GUARD_MARKER not in prior:
                indent = re.match(r"^(\s*)", line).group(1)
                out.append(f"{indent}{GUARD_MARKER}")
                out.append(f"{indent}entry_armed, entry_arm_reason = _batch26b_execution_entry_hard_arming_verdict()")
                out.append(f"{indent}if not entry_armed:")
                out.append(f"{indent}    self._fail_decision(decision, entry_arm_reason)")
                out.append(f"{indent}    return")
                out.append("")
                inserted += 1
        out.append(line)

    return "\n".join(out) + "\n", inserted


def main() -> int:
    if not EXECUTION.exists():
        raise SystemExit("execution.py missing")
    if not CPR.exists():
        raise SystemExit("controlled_paper_runtime.py missing")

    before_execution = read(EXECUTION)
    before_cpr = read(CPR)

    entry_calls_before = find_actual_entry_calls(before_execution)
    exit_calls_before = find_actual_exit_calls(before_execution)

    if not entry_calls_before:
        raise SystemExit("No actual self.broker.place_entry_order(...) call found")
    if not exit_calls_before:
        raise SystemExit("No actual self.broker.place_exit_order(...) call found")

    cpr_after, runtime_inserted = install_runtime_contract(before_cpr)
    write(CPR, cpr_after)

    execution_after, helper_inserted = install_helper(before_execution)
    execution_after, guards_inserted = install_entry_guard(execution_after)

    guarded_after, unguarded_after = guarded_entry_calls(execution_after)
    if unguarded_after:
        raise SystemExit(
            "Unguarded self.broker.place_entry_order(...) call remains: "
            + json.dumps(unguarded_after, indent=2)
        )

    write(EXECUTION, execution_after)

    final_execution = read(EXECUTION)
    final_cpr = read(CPR)

    guarded_final, unguarded_final = guarded_entry_calls(final_execution)

    report = {
        "batch": "26B_execution_hard_arming_guard_thin_patch_step",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "patched_files": [
            "app/mme_scalpx/services/controlled_paper_runtime.py",
            "app/mme_scalpx/services/execution.py",
        ],
        "paper_armed_enabled": False,
        "real_live_enabled": False,
        "services_started": False,
        "redis_writes": False,
        "runtime_contract_inserted": runtime_inserted,
        "execution_helper_inserted": helper_inserted,
        "entry_guards_inserted": guards_inserted,
        "entry_calls_before": entry_calls_before,
        "exit_calls_before": exit_calls_before,
        "entry_calls_after": find_actual_entry_calls(final_execution),
        "exit_calls_after": find_actual_exit_calls(final_execution),
        "guarded_entry_calls_after": guarded_final,
        "unguarded_entry_calls_after": unguarded_final,
        "runtime_contract_present": "def controlled_execution_entry_allowed(" in final_cpr,
        "runtime_contract_fail_closed_text_present": "return False" in final_cpr,
        "execution_helper_present": "_batch26b_execution_entry_hard_arming_verdict" in final_execution,
        "guard_marker_count": final_execution.count(GUARD_MARKER),
        "verdict": {
            "patch_step_ok": (
                "def controlled_execution_entry_allowed(" in final_cpr
                and "return False" in final_cpr
                and "_batch26b_execution_entry_hard_arming_verdict" in final_execution
                and len(guarded_final) >= 1
                and len(unguarded_final) == 0
                and len(find_actual_exit_calls(final_execution)) == len(exit_calls_before)
            ),
            "entry_guarded": len(guarded_final) >= 1 and len(unguarded_final) == 0,
            "exit_call_count_preserved": len(find_actual_exit_calls(final_execution)) == len(exit_calls_before),
            "paper_armed_approved": False,
            "real_live_approved": False,
        },
    }

    PATCH_STEP.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["verdict"], indent=2, sort_keys=True))
    return 0 if report["verdict"]["patch_step_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
