#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PYBIN = Path(sys.executable)
PROOF_DIR = PROJECT_ROOT / "run" / "proofs"
OUT_PATH = PROOF_DIR / "proof_5family_integration_master.json"

FINAL_VERDICT_READY = "HOLD_OBSERVE_READY"
FINAL_VERDICT_BLOCKED = "BLOCKED"

SECRET_RE = re.compile(
    r"("
    r"\baccess[_-]?token\b|"
    r"\brefresh[_-]?token\b|"
    r"\bclient[_-]?secret\b|"
    r"\bapi[_-]?secret\b|"
    r"\bapi[_-]?key\b|"
    r"\bauthorization\b|"
    r"\bbearer\s+[A-Za-z0-9._\-]+\b|"
    r"\bpassword\b|"
    r"\bpasswd\b|"
    r"(^|[^A-Za-z0-9_])pin([^A-Za-z0-9_]|$)|"
    r"\btotp\b|"
    r"\bjwt\b|"
    r"\benctoken\b"
    r")",
    re.IGNORECASE,
)

RAW_REDIS_LITERAL_RE = re.compile(
    r"^(?:replay:)?(?:"
    r"ticks|features|decisions|orders|trades|cmd|system|state|params|lock|hb|heartbeat|"
    r"feeds|strategy|risk|exec|execution|monitor|provider|dhan|zerodha"
    r")[:][A-Za-z0-9_:\-\.]+$"
)

LEGACY_LEAK_RE = re.compile(
    r"(nifty_suspended|legacy_root|legacy_single_runtime|old_strategy_runtime|single_strategy_live)",
    re.IGNORECASE,
)

ALLOWED_RAW_REDIS_FILES = {
    "app/mme_scalpx/core/names.py",
}

APPROVED_COMPAT_LITERAL_USE = {
    ("app/mme_scalpx/services/features.py", "features:heartbeat"),
    ("app/mme_scalpx/services/strategy.py", "strategy:heartbeat"),
}

ALLOWED_RAW_REDIS_VALUE_FRAGMENTS = (
    "redis://",
    "rediss://",
)


@dataclass(frozen=True)
class ProofSpec:
    label: str
    canonical_key: str
    proof_path: str
    accepted_keys: tuple[str, ...]
    script_candidates: tuple[str, ...] = ()


PROOF_SPECS: tuple[ProofSpec, ...] = (
    ProofSpec(
        label="contract_field_registry",
        canonical_key="contract_field_registry_ok",
        proof_path="run/proofs/proof_contract_field_registry.json",
        accepted_keys=("contract_field_registry_ok",),
        script_candidates=("bin/proof_contract_field_registry.py",),
    ),
    ProofSpec(
        label="provider_runtime_consumer",
        canonical_key="provider_runtime_consumer_ok",
        proof_path="run/proofs/proof_provider_runtime_contract_seam.json",
        accepted_keys=("provider_runtime_contract_seam_ok", "provider_runtime_consumer_ok"),
        script_candidates=("bin/proof_provider_runtime_contract_seam.py", "bin/proof_provider_runtime_feature_consumer.py"),
    ),
    ProofSpec(
        label="feed_snapshot_adapter",
        canonical_key="feed_snapshot_adapter_ok",
        proof_path="run/proofs/proof_feed_snapshot_feature_adapter.json",
        accepted_keys=("feed_snapshot_feature_adapter_ok", "feed_snapshot_adapter_ok"),
        script_candidates=("bin/proof_feed_snapshot_feature_adapter.py",),
    ),
    ProofSpec(
        label="dhan_oi_ladder_persistence",
        canonical_key="dhan_oi_ladder_persistence_ok",
        proof_path="run/proofs/proof_dhan_oi_ladder_persistence.json",
        accepted_keys=("dhan_oi_ladder_persistence_ok",),
        script_candidates=("bin/proof_dhan_oi_ladder_persistence.py",),
    ),
    ProofSpec(
        label="shared_builder_abi",
        canonical_key="shared_builder_abi_ok",
        proof_path="run/proofs/proof_feature_family_shared_builder_abi.json",
        accepted_keys=("feature_family_shared_builder_abi_ok", "shared_builder_abi_ok"),
        script_candidates=("bin/proof_feature_family_shared_builder_abi.py",),
    ),
    ProofSpec(
        label="family_surface_service_path",
        canonical_key="family_surface_service_path_ok",
        proof_path="run/proofs/proof_family_surface_service_path.json",
        accepted_keys=("family_surface_service_path_ok",),
        script_candidates=("bin/proof_family_surface_service_path.py",),
    ),
    ProofSpec(
        label="canonical_family_features",
        canonical_key="canonical_family_features_ok",
        proof_path="run/proofs/proof_family_features_canonical_support.json",
        accepted_keys=("canonical_family_features_ok", "family_features_canonical_support_ok"),
        script_candidates=("bin/proof_family_features_canonical_support.py",),
    ),
    ProofSpec(
        label="miso_provider_alignment",
        canonical_key="miso_provider_alignment_ok",
        proof_path="run/proofs/proof_miso_provider_doctrine_alignment.json",
        accepted_keys=("miso_provider_doctrine_alignment_ok", "miso_provider_alignment_ok"),
        script_candidates=("bin/proof_miso_provider_doctrine_alignment.py",),
    ),
    ProofSpec(
        label="strategy_family_reverse_coverage",
        canonical_key="strategy_family_reverse_coverage_ok",
        proof_path="run/proofs/proof_strategy_family_reverse_coverage.json",
        accepted_keys=("strategy_family_reverse_coverage_ok", "missing_required_signal_count_zero"),
        script_candidates=("bin/proof_strategy_family_reverse_coverage.py",),
    ),
    ProofSpec(
        label="candidate_metadata_contract",
        canonical_key="candidate_metadata_contract_ok",
        proof_path="run/proofs/proof_strategy_candidate_metadata_contract.json",
        accepted_keys=(
            "strategy_candidate_metadata_contract_ok",
            "candidate_metadata_contract_ok",
            "all_family_candidates_have_identity",
        ),
        script_candidates=("bin/proof_strategy_candidate_metadata_contract.py",),
    ),
    ProofSpec(
        label="order_intent_adapter_disabled",
        canonical_key="order_intent_adapter_disabled_ok",
        proof_path="run/proofs/proof_order_intent_adapter_disabled.json",
        accepted_keys=("order_intent_adapter_disabled_ok",),
        script_candidates=("bin/proof_order_intent_adapter_disabled.py",),
    ),
    ProofSpec(
        label="execution_entry_contract_dryrun",
        canonical_key="execution_entry_contract_dryrun_ok",
        proof_path="run/proofs/proof_execution_entry_contract_dryrun.json",
        accepted_keys=("execution_entry_contract_dryrun_ok",),
        script_candidates=("bin/proof_execution_entry_contract_dryrun.py",),
    ),
    ProofSpec(
        label="risk_execution_seam",
        canonical_key="risk_execution_seam_ok",
        proof_path="run/proofs/proof_risk_gate_execution_integration.json",
        accepted_keys=("risk_gate_execution_integration_ok", "risk_execution_seam_ok"),
        script_candidates=("bin/proof_risk_gate_execution_integration.py",),
    ),
    ProofSpec(
        label="runtime_config_alignment",
        canonical_key="runtime_config_alignment_ok",
        proof_path="run/proofs/proof_runtime_config_alignment.json",
        accepted_keys=("runtime_config_alignment_ok",),
        script_candidates=("bin/proof_runtime_config_alignment.py",),
    ),
    ProofSpec(
        label="systemd_runtime_alignment",
        canonical_key="systemd_runtime_alignment_ok",
        proof_path="run/proofs/proof_systemd_runtime_alignment.json",
        accepted_keys=("systemd_runtime_alignment_ok", "systemd_service_registry_ok"),
        script_candidates=("bin/proof_systemd_runtime_alignment.py",),
    ),
    ProofSpec(
        label="batch25s_ancillary_completeness",
        canonical_key="batch25s_ancillary_complete_ok",
        proof_path="run/proofs/proof_batch25s_ancillary_completeness.json",
        accepted_keys=("batch25s_ancillary_complete_ok",),
        script_candidates=(),
    ),
)


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT_ROOT))


def run_command(args: list[str], *, timeout_sec: int = 180) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    started_ns = time.time_ns()
    proc = subprocess.run(
        args,
        cwd=str(PROJECT_ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
    )

    return {
        "args": args,
        "returncode": proc.returncode,
        "started_ns": started_ns,
        "ended_ns": time.time_ns(),
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
        "ok": proc.returncode == 0,
    }


def run_compileall() -> dict[str, Any]:
    targets = [
        "app/mme_scalpx",
        "bin/proof_contract_field_registry.py",
        "bin/proof_provider_runtime_contract_seam.py",
        "bin/proof_provider_runtime_feature_consumer.py",
        "bin/proof_feed_snapshot_feature_adapter.py",
        "bin/proof_dhan_oi_ladder_persistence.py",
        "bin/proof_feature_family_shared_builder_abi.py",
        "bin/proof_family_surface_service_path.py",
        "bin/proof_family_features_canonical_support.py",
        "bin/proof_miso_provider_doctrine_alignment.py",
        "bin/proof_strategy_family_reverse_coverage.py",
        "bin/proof_strategy_candidate_metadata_contract.py",
        "bin/proof_order_intent_adapter_disabled.py",
        "bin/proof_execution_entry_contract_dryrun.py",
        "bin/proof_risk_gate_execution_integration.py",
        "bin/proof_runtime_config_alignment.py",
        "bin/proof_systemd_runtime_alignment.py",
        "bin/proof_5family_integration_master.py",
    ]

    existing = [target for target in targets if (PROJECT_ROOT / target).exists()]
    missing_optional = [target for target in targets if not (PROJECT_ROOT / target).exists()]

    result = run_command([str(PYBIN), "-m", "compileall", "-q", *existing])
    result["targets_existing"] = existing
    result["targets_missing_optional"] = missing_optional
    result["compileall_ok"] = result["ok"]
    return result


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def truthy_key(data: Mapping[str, Any], key: str) -> bool:
    if data.get(key) is True:
        return True

    checks = data.get("checks")
    if isinstance(checks, Mapping) and checks.get(key) is True:
        return True

    observed = data.get("observed")
    if isinstance(observed, Mapping) and observed.get(key) is True:
        return True

    return False


def truthy_any(data: Mapping[str, Any], keys: Iterable[str]) -> tuple[bool, str | None]:
    for key in keys:
        if truthy_key(data, key):
            if data.get(key) is True:
                return True, key
            if isinstance(data.get("checks"), Mapping) and data["checks"].get(key) is True:
                return True, f"checks.{key}"
            if isinstance(data.get("observed"), Mapping) and data["observed"].get(key) is True:
                return True, f"observed.{key}"

    return False, None


def derived_contract_field_registry_ok(proof: Mapping[str, Any]) -> tuple[bool, str | None]:
    ok, matched = truthy_any(proof, ("contract_field_registry_ok",))
    if ok:
        return True, matched

    required = (
        "provider_runtime_keys_complete",
        "snapshot_keys_complete",
        "dhan_context_keys_complete",
        "family_support_keys_complete",
        "execution_entry_keys_complete",
        "no_duplicate_contract_keys",
    )
    if all(truthy_key(proof, key) for key in required):
        return True, "derived.contract_field_registry_subchecks"

    return False, None


def derived_shared_builder_abi_ok(proof: Mapping[str, Any]) -> tuple[bool, str | None]:
    ok, matched = truthy_any(proof, ("feature_family_shared_builder_abi_ok", "shared_builder_abi_ok"))
    if ok:
        return True, matched

    required = (
        "futures_core_builder_used",
        "option_core_builder_used",
        "strike_ladder_builder_used",
        "classic_strike_builder_used",
        "miso_strike_builder_used",
        "regime_builder_used",
        "tradability_builder_used",
        "fallback_builder_count_zero",
    )
    if all(truthy_key(proof, key) for key in required):
        return True, "derived.shared_builder_abi_subchecks"

    return False, None


def proof_ok_for_spec(spec: ProofSpec, proof: Mapping[str, Any]) -> tuple[bool, str | None]:
    if spec.label == "contract_field_registry":
        return derived_contract_field_registry_ok(proof)

    if spec.label == "shared_builder_abi":
        return derived_shared_builder_abi_ok(proof)

    return truthy_any(proof, spec.accepted_keys)


def validate_proof_artifacts() -> dict[str, Any]:
    out: dict[str, Any] = {}

    for spec in PROOF_SPECS:
        path = PROJECT_ROOT / spec.proof_path
        if not path.exists():
            out[spec.label] = {
                "proof_found": False,
                "proof_path": spec.proof_path,
                "ok": False,
                "error": "missing_proof_artifact",
            }
            continue

        try:
            proof = load_json(path)
        except Exception as exc:
            out[spec.label] = {
                "proof_found": True,
                "proof_path": spec.proof_path,
                "ok": False,
                "error": f"invalid_json:{exc}",
            }
            continue

        ok, matched_key = proof_ok_for_spec(spec, proof)
        out[spec.label] = {
            "proof_found": True,
            "proof_path": spec.proof_path,
            "ok": ok,
            "matched_key": matched_key,
            "accepted_keys": spec.accepted_keys,
        }

    return out


def compile_dependency_scripts_present() -> dict[str, Any]:
    status: dict[str, Any] = {}
    for spec in PROOF_SPECS:
        if not spec.script_candidates:
            continue

        candidates = [PROJECT_ROOT / candidate for candidate in spec.script_candidates]
        found = [path for path in candidates if path.exists()]
        status[spec.label] = {
            "script_found": bool(found),
            "scripts": [rel(path) for path in found],
            "candidate_scripts": spec.script_candidates,
        }

    required_alias_groups_ok = all(item["script_found"] for item in status.values())

    return {
        "dependency_proof_scripts_present_ok": required_alias_groups_ok,
        "status": status,
        "note": (
            "Batch 25T-C validates frozen proof artifacts and compiles proof scripts. "
            "It does not rerun older batch proof scripts because some are destructive or rewrite proof artifacts with legacy schemas."
        ),
    }


def literal_values_from_python(path: Path) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError:
        return []

    values: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append((getattr(node, "lineno", 0), node.value))
    return values


def scan_raw_redis_names() -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    approved: list[dict[str, Any]] = []

    names_text = (PROJECT_ROOT / "app/mme_scalpx/core/names.py").read_text(encoding="utf-8", errors="replace")

    for path in sorted((PROJECT_ROOT / "app/mme_scalpx").rglob("*.py")):
        rel_path = rel(path)

        if rel_path in ALLOWED_RAW_REDIS_FILES:
            continue
        if "__pycache__" in rel_path:
            continue

        for lineno, value in literal_values_from_python(path):
            if any(fragment in value for fragment in ALLOWED_RAW_REDIS_VALUE_FRAGMENTS):
                continue

            if not RAW_REDIS_LITERAL_RE.match(value):
                continue

            if (rel_path, value) in APPROVED_COMPAT_LITERAL_USE and value in names_text:
                approved.append(
                    {
                        "path": rel_path,
                        "line": lineno,
                        "value": value,
                        "reason": "approved_compat_literal_present_in_names_py",
                    }
                )
                continue

            hits.append(
                {
                    "path": rel_path,
                    "line": lineno,
                    "value": value,
                }
            )

    return {
        "raw_redis_name_scan_ok": not hits,
        "hit_count": len(hits),
        "hits": hits[:200],
        "approved_compat_literals": approved,
    }


def scan_legacy_leakage() -> dict[str, Any]:
    hits: list[dict[str, Any]] = []

    scan_roots = [
        PROJECT_ROOT / "app/mme_scalpx/services",
        PROJECT_ROOT / "app/mme_scalpx/integrations",
        PROJECT_ROOT / "app/mme_scalpx/main.py",
    ]

    files: list[Path] = []
    for root in scan_roots:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(root.rglob("*.py"))

    for path in sorted(files):
        rel_path = rel(path)
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if LEGACY_LEAK_RE.search(line):
                hits.append(
                    {
                        "path": rel_path,
                        "line": lineno,
                        "line_preview": line.strip()[:200],
                    }
                )

    return {
        "legacy_leakage_scan_ok": not hits,
        "hit_count": len(hits),
        "hits": hits[:200],
    }


def scan_secrets_in_proofs() -> dict[str, Any]:
    hits: list[dict[str, Any]] = []
    approved: list[dict[str, Any]] = []

    for path in sorted(PROOF_DIR.glob("proof_*.json")):
        text = path.read_text(encoding="utf-8", errors="replace")

        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()

            if not stripped:
                continue

            if "<REDACTED>" in stripped:
                approved.append(
                    {
                        "path": rel(path),
                        "line": lineno,
                        "reason": "redacted_secret_name_only",
                    }
                )
                continue

            if "secret_scan_note" in stripped or "secret-detection regex" in stripped:
                approved.append(
                    {
                        "path": rel(path),
                        "line": lineno,
                        "reason": "secret_scanner_note",
                    }
                )
                continue

            if SECRET_RE.search(stripped):
                hits.append(
                    {
                        "path": rel(path),
                        "line": lineno,
                        "line_preview": stripped[:200],
                    }
                )

    return {
        "proof_secret_scan_ok": not hits,
        "hit_count": len(hits),
        "hits": hits[:200],
        "approved_redacted_or_scanner_note_hits": approved[:200],
    }


def derive_hold_publication_safety() -> dict[str, Any]:
    order_path = PROJECT_ROOT / "run/proofs/proof_order_intent_adapter_disabled.json"

    result = {
        "hold_publication_safety_ok": False,
        "source": "run/proofs/proof_order_intent_adapter_disabled.json",
        "checks": {},
        "error": None,
    }

    if not order_path.exists():
        result["error"] = "missing_order_intent_adapter_disabled_proof"
        return result

    try:
        proof = load_json(order_path)
    except Exception as exc:
        result["error"] = f"invalid_json:{exc}"
        return result

    checks = {
        "order_intent_adapter_disabled_ok": truthy_key(proof, "order_intent_adapter_disabled_ok"),
        "observe_only_still_publishes_hold": truthy_key(proof, "observe_only_still_publishes_hold"),
        "non_hold_publication_guard_still_blocks": truthy_key(proof, "non_hold_publication_guard_still_blocks"),
    }

    result["checks"] = checks
    result["hold_publication_safety_ok"] = all(checks.values())
    return result


def main() -> int:
    generated_at_ns = time.time_ns()
    PROOF_DIR.mkdir(parents=True, exist_ok=True)

    compileall = run_compileall()
    dependency_scripts = compile_dependency_scripts_present()
    artifacts = validate_proof_artifacts()
    raw_redis_scan = scan_raw_redis_names()
    legacy_scan = scan_legacy_leakage()
    proof_secret_scan = scan_secrets_in_proofs()
    hold_safety = derive_hold_publication_safety()

    canonical_results: dict[str, bool] = {
        "compileall_ok": bool(compileall.get("compileall_ok")),
        "contract_field_registry_ok": artifacts.get("contract_field_registry", {}).get("ok") is True,
        "provider_runtime_consumer_ok": artifacts.get("provider_runtime_consumer", {}).get("ok") is True,
        "feed_snapshot_adapter_ok": artifacts.get("feed_snapshot_adapter", {}).get("ok") is True,
        "dhan_oi_ladder_persistence_ok": artifacts.get("dhan_oi_ladder_persistence", {}).get("ok") is True,
        "shared_builder_abi_ok": artifacts.get("shared_builder_abi", {}).get("ok") is True,
        "family_surface_service_path_ok": artifacts.get("family_surface_service_path", {}).get("ok") is True,
        "canonical_family_features_ok": artifacts.get("canonical_family_features", {}).get("ok") is True,
        "miso_provider_alignment_ok": artifacts.get("miso_provider_alignment", {}).get("ok") is True,
        "strategy_family_reverse_coverage_ok": artifacts.get("strategy_family_reverse_coverage", {}).get("ok") is True,
        "candidate_metadata_contract_ok": artifacts.get("candidate_metadata_contract", {}).get("ok") is True,
        "order_intent_adapter_disabled_ok": artifacts.get("order_intent_adapter_disabled", {}).get("ok") is True,
        "execution_entry_contract_dryrun_ok": artifacts.get("execution_entry_contract_dryrun", {}).get("ok") is True,
        "risk_execution_seam_ok": artifacts.get("risk_execution_seam", {}).get("ok") is True,
        "runtime_config_alignment_ok": artifacts.get("runtime_config_alignment", {}).get("ok") is True,
        "systemd_runtime_alignment_ok": artifacts.get("systemd_runtime_alignment", {}).get("ok") is True,
        "batch25s_ancillary_complete_ok": artifacts.get("batch25s_ancillary_completeness", {}).get("ok") is True,
        "hold_publication_safety_ok": hold_safety.get("hold_publication_safety_ok") is True,
        "raw_redis_name_scan_ok": raw_redis_scan.get("raw_redis_name_scan_ok") is True,
        "legacy_leakage_scan_ok": legacy_scan.get("legacy_leakage_scan_ok") is True,
        "proof_secret_scan_ok": proof_secret_scan.get("proof_secret_scan_ok") is True,
        "dependency_proof_scripts_present_ok": dependency_scripts.get("dependency_proof_scripts_present_ok") is True,
    }

    # The user-required final verdict does not require rerunning older proof scripts.
    # It requires the full institutional integration state to be green.
    final_ready = all(canonical_results.values())
    final_verdict = FINAL_VERDICT_READY if final_ready else FINAL_VERDICT_BLOCKED

    proof = {
        "proof_name": "proof_5family_integration_master",
        "batch": "25T-C",
        "generated_at_ns": generated_at_ns,
        "final_verdict": final_verdict,
        "hold_observe_ready": final_ready,
        "canonical_results": canonical_results,
        "compileall": compileall,
        "dependency_scripts": dependency_scripts,
        "proof_artifacts": artifacts,
        "hold_publication_safety": hold_safety,
        "raw_redis_name_scan": raw_redis_scan,
        "legacy_leakage_scan": legacy_scan,
        "proof_secret_scan": proof_secret_scan,
    }

    OUT_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(
        {
            "final_verdict": final_verdict,
            "hold_observe_ready": final_ready,
            **canonical_results,
            "proof_path": str(OUT_PATH.relative_to(PROJECT_ROOT)),
        },
        indent=2,
        sort_keys=True,
    ))

    return 0 if final_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
