#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]

TARGETS = {
    "MIST": "app/mme_scalpx/services/strategy_family/mist.py",
    "MISB": "app/mme_scalpx/services/strategy_family/misb.py",
    "MISC": "app/mme_scalpx/services/strategy_family/misc.py",
    "MISR": "app/mme_scalpx/services/strategy_family/misr.py",
    "MISO": "app/mme_scalpx/services/strategy_family/miso.py",
}

RELATED = {
    "strategy": "app/mme_scalpx/services/strategy.py",
    "features": "app/mme_scalpx/services/features.py",
    "execution": "app/mme_scalpx/services/execution.py",
    "risk": "app/mme_scalpx/services/risk.py",
    "names": "app/mme_scalpx/core/names.py",
    "models": "app/mme_scalpx/core/models.py",
}

PATCH_STEP = ROOT / "run/proofs/proof_batch26d_strategy_leaf_required_surface_failclosed_patch_step.json"

HELPER_BEGIN = "# BEGIN BATCH26D_STRATEGY_LEAF_REQUIRED_COMMON_SURFACE"
HELPER_END = "# END BATCH26D_STRATEGY_LEAF_REQUIRED_COMMON_SURFACE"

UNSAFE_PROVIDER = 'return as_mapping(view.get("provider_runtime"))'
SAFE_PROVIDER = 'return as_mapping(_batch26d_required_common_surface(view, "provider_runtime", family="{family}", source="view"))'

UNSAFE_SELECTED = 'selected = as_mapping(common.get("selected_option"))'
SAFE_SELECTED = 'selected = as_mapping(_batch26d_required_common_surface(common, "selected_option", family="{family}", source="common"))'


def helper_block(family: str) -> str:
    return f'''
{HELPER_BEGIN}
def _batch26d_required_common_surface(container, key, *, family="{family}", source="unknown"):
    """
    Batch 26D fail-closed common-surface accessor.

    Required surfaces must not silently collapse to empty mappings:
    - view.provider_runtime
    - common.selected_option

    Missing/None/empty required surfaces become explicit blockers by raising
    RuntimeError before family eligibility can interpret absent data as safe.
    """
    sentinel = object()
    value = sentinel

    if container is None:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{{family}}:{{source}}.{{key}}:container_none")

    if isinstance(container, dict):
        value = container.get(key, sentinel)
    else:
        getter = getattr(container, "get", None)
        if callable(getter):
            try:
                value = getter(key, sentinel)
            except TypeError:
                try:
                    value = getter(key)
                except Exception:
                    value = sentinel
            except Exception:
                value = sentinel

        if value is sentinel:
            try:
                value = getattr(container, key)
            except Exception:
                value = sentinel

    if value is sentinel:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{{family}}:{{source}}.{{key}}:absent")

    if value is None:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{{family}}:{{source}}.{{key}}:none")

    if isinstance(value, dict) and not value:
        raise RuntimeError(f"BATCH26D_REQUIRED_SURFACE_MISSING:{{family}}:{{source}}.{{key}}:empty")

    return value
{HELPER_END}

'''


def sha(path: pathlib.Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def inspect_file(path: pathlib.Path) -> dict[str, Any]:
    text = read(path) if path.exists() else ""
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": path.exists(),
        "is_file": path.is_file() if path.exists() else False,
        "line_count": len(text.splitlines()) if text else 0,
        "sha256": sha(path),
        "has_helper": HELPER_BEGIN in text and HELPER_END in text,
        "unsafe_provider_get_present": UNSAFE_PROVIDER in text,
        "unsafe_selected_get_present": UNSAFE_SELECTED in text,
        "safe_provider_present": "_batch26d_required_common_surface(view, \"provider_runtime\"" in text,
        "safe_selected_present": "_batch26d_required_common_surface(common, \"selected_option\"" in text,
    }


def grep(path: pathlib.Path, pattern: str, max_hits: int = 80) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rx = re.compile(pattern, re.IGNORECASE)
    out = []
    for lineno, line in enumerate(read(path).splitlines(), 1):
        if rx.search(line):
            out.append({"line": lineno, "text": line.rstrip()[:260]})
            if len(out) >= max_hits:
                break
    return out


def insert_helper(text: str, family: str) -> tuple[str, bool]:
    if HELPER_BEGIN in text:
        if HELPER_END not in text:
            raise SystemExit(f"{family}: partial Batch 26D helper marker found")
        return text, False

    # Insert before the first private/provider helper if possible; otherwise
    # before first class/dataclass; otherwise after imports by appending above logic.
    candidates = []
    for needle in [
        "\ndef _provider_runtime",
        "\ndef provider_runtime",
        "\ndef _selected_option",
        "\n@dataclass",
        "\nclass ",
    ]:
        idx = text.find(needle)
        if idx != -1:
            candidates.append(idx)

    if candidates:
        idx = min(candidates)
        return text[: idx + 1] + helper_block(family) + text[idx + 1 :], True

    return text.rstrip() + "\n\n" + helper_block(family), True


def patch_leaf(family: str, rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        raise SystemExit(f"{family}: missing target file {rel}")

    before = read(path)
    if "as_mapping" not in before:
        raise SystemExit(f"{family}: as_mapping not found; refusing blind patch")

    pre = inspect_file(path)
    patched, helper_inserted = insert_helper(before, family)

    replacements = {
        "provider_runtime": 0,
        "selected_option": 0,
    }

    if UNSAFE_PROVIDER in patched:
        patched = patched.replace(UNSAFE_PROVIDER, SAFE_PROVIDER.format(family=family))
        replacements["provider_runtime"] += 1

    if UNSAFE_SELECTED in patched:
        patched = patched.replace(UNSAFE_SELECTED, SAFE_SELECTED.format(family=family))
        replacements["selected_option"] += 1

    write(path, patched)
    after = read(path)
    post = inspect_file(path)

    required_ok = (
        post["has_helper"]
        and not post["unsafe_provider_get_present"]
        and not post["unsafe_selected_get_present"]
        and post["safe_provider_present"]
        and post["safe_selected_present"]
    )

    return {
        "family": family,
        "path": rel,
        "helper_inserted": helper_inserted,
        "replacements": replacements,
        "pre": pre,
        "post": post,
        "required_ok": required_ok,
        "relevant_lines": grep(path, r"provider_runtime|selected_option|BATCH26D_REQUIRED_SURFACE", 120),
    }


def main() -> int:
    results = {}
    for family, rel in TARGETS.items():
        results[family] = patch_leaf(family, rel)

    related_inspection = {
        name: inspect_file(ROOT / rel)
        for name, rel in RELATED.items()
        if (ROOT / rel).exists()
    }

    blockers = []
    for family, result in results.items():
        if not result["required_ok"]:
            blockers.append(f"{family}_REQUIRED_SURFACE_PATCH_NOT_PROVEN")
        if result["replacements"]["provider_runtime"] > 1:
            blockers.append(f"{family}_MULTIPLE_PROVIDER_REPLACEMENTS_REVIEW")
        if result["replacements"]["selected_option"] > 1:
            blockers.append(f"{family}_MULTIPLE_SELECTED_OPTION_REPLACEMENTS_REVIEW")

    report = {
        "batch": "26D_strategy_leaf_required_surface_failclosed_patch_step",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "patched_files": TARGETS,
        "related_inspection": related_inspection,
        "results": results,
        "safety_posture": {
            "paper_armed_enabled": False,
            "real_live_enabled": False,
            "services_started": False,
            "redis_writes": False,
            "execution_patched": False,
            "risk_patched": False,
            "strategy_bridge_patched": False,
        },
        "verdict": {
            "patch_step_ok": len(blockers) == 0,
            "blockers": blockers,
            "all_five_leaves_patched": all(r["required_ok"] for r in results.values()),
            "paper_armed_approved": False,
            "real_live_approved": False,
            "runtime_promotion_allowed": False,
        },
    }

    PATCH_STEP.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["verdict"], indent=2, sort_keys=True))
    return 0 if len(blockers) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
