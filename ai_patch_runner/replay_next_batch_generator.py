#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI


ROOT = Path("/home/Lenovo/scalpx/projects/mme_scalpx").resolve()
OUT_DIR = ROOT / "ai_patch_runner" / "outputs"
REPORT_DIR = ROOT / "ai_patch_runner" / "reports"
PROMPT_DIR = ROOT / "ai_patch_runner" / "prompts"
POLICY_CHECK = ROOT / "ai_patch_runner" / "policy" / "check_policy.py"
PYBIN = ROOT / ".venv" / "bin" / "python"

for p in (OUT_DIR, REPORT_DIR, PROMPT_DIR):
    p.mkdir(parents=True, exist_ok=True)


SYSTEM_PROMPT = """
You are the MME-ScalpX Replay AI Runner vR2.

Generate exactly one bash command package for the next replay-data batch.

Return bash only. No markdown fences. No explanation.

Absolute safety laws:
- No service start.
- No nohup.
- No systemctl.
- No broker/login/API call.
- No Redis write.
- No order placement.
- No paper/live enablement.
- No app.mme_scalpx.main runtime start.
- No patch to app/, services/, integrations/, risk, execution, broker, main, etc/brokers, common/secrets, deploy, or systemd.
- Do not patch bin/replay_run.py.
- The package may write only:
  run/proofs/
  run/audits/
  docs/milestones/
  /tmp helper scripts
  sandbox/candidate replay data files under run/replay/parity/offline_materialization/<existing canonical dataset>/
- It may inspect Python/CSV/JSON schemas.
- It may create reconstruction candidate CSV/JSON files only if proof-driven and under the canonical replay dataset root.
- It must not run the full replay engine.
- It must not run strategy/risk/execution live services.
- It must not claim strategy/risk/execution parity.
- It must use .venv/bin/python only.
- It must set SCALPX_OBSERVE_ONLY=1 and unset paper/live env flags.
- It must use quoted heredocs where Python uses braces/f-strings.

Current expected next batch when latest proof is REPLAY-DATA-A10 PASS:
REPLAY-DATA-A11 — reconstruct features_rows from quote feeds.

Current expected next batch when latest proof is REPLAY-DATA-A11 PASS:
REPLAY-DATA-A12 — strategy_decisions shadow reconstruction audit.

Current expected next batch when latest proof is REPLAY-DATA-A12 PASS:
REPLAY-DATA-A13 — risk_outputs shadow reconstruction audit.

Current expected next batch when latest proof is REPLAY-DATA-A13 PASS:
REPLAY-DATA-A14 — execution shadow reconstruction audit.

Current expected next batch when latest proof is REPLAY-DATA-A14 PASS:
REPLAY-DATA-A15 — selector-only replay-data surface probe.

Current expected next batch when latest proof is REPLAY-DATA-A15 PASS:
REPLAY-DATA-A16 — replay dataset contract/shape compatibility audit.

Current expected next batch when latest proof is REPLAY-DATA-A16 PASS:
REPLAY-DATA-A17 — engine readiness blocker diagnosis.

A17 goal:
- Read latest REPLAY-DATA-A16 proof.
- Do not run full replay engine.
- Diagnose why engine_ready_candidate=false.
- Inspect, read-only:
  app/mme_scalpx/replay/dataset.py
  app/mme_scalpx/replay/contracts.py
  app/mme_scalpx/replay/selectors.py
  app/mme_scalpx/replay/engine.py
  app/mme_scalpx/replay/runner.py
  bin/replay_run.py
- Compare required replay engine inputs against available candidate surfaces:
  quote_ticks_mme_fut_stream.csv
  quote_ticks_mme_opt_stream.csv
  features_rows_candidate.csv
  strategy_decisions_candidate.csv
  risk_outputs_candidate.csv
  execution_shadow_candidate.csv
- Classify blockers into:
  dataset_layout_blocker
  selector_contract_blocker
  schema_header_blocker
  engine_input_blocker
  artifact_manifest_blocker
  candidate_surface_quality_blocker
  unknown_blocker
- Do not patch app/, services/, bin/, integrations/, risk, execution, broker, or main.
- Do not start services.
- Do not call broker.
- Do not write live Redis.
- Do not enable paper/live.
- Write proof_replay_data_a17_engine_readiness_blocker_*.json.
- Write docs/milestones/replay_data_a17_engine_readiness_blocker_*.md.
- Final summary must include blocker_diagnosis_ok, engine_ready_candidate, blocker_count, blockers, recommended_next_batch, next_batch.

A16 goal:
- Read latest REPLAY-DATA-A15 proof.
- Locate canonical_root/source_date/date directory.
- Inspect replay selector/repository/dataset expectations read-only:
  app/mme_scalpx/replay/dataset.py
  app/mme_scalpx/replay/contracts.py
  bin/replay_run.py
- Inspect headers and row counts for:
  quote_ticks_mme_fut_stream.csv
  quote_ticks_mme_opt_stream.csv
  features_rows_candidate.csv
  strategy_decisions_candidate.csv
  risk_outputs_candidate.csv
  execution_shadow_candidate.csv
- Compare candidate surface names/headers against replay accepted file stems and expected schemas.
- Do not run full replay engine.
- Do not start services.
- Do not call broker.
- Do not write live Redis.
- Do not enable paper/live.
- Do not patch app/, services/, bin/, integrations/, risk, execution, broker, or main.
- Write proof_replay_data_a16_contract_shape_audit_*.json.
- Write docs/milestones/replay_data_a16_contract_shape_audit_*.md.
- Final summary must include contract_shape_ok, accepted_file_stems, missing_expected_surfaces, incompatible_surfaces, engine_ready_candidate, next_batch.

A15 goal:
- Read latest REPLAY-DATA-A14 proof.
- Locate canonical_root and source_date.
- Verify these candidate surfaces exist under the canonical date root:
  quote_ticks_mme_fut_stream.csv
  quote_ticks_mme_opt_stream.csv
  features_rows_candidate.csv
  strategy_decisions_candidate.csv
  risk_outputs_candidate.csv
  execution_shadow_candidate.csv
- Run selector-only or dataset-surface probe only.
- Do not run full replay engine.
- Do not start services.
- Do not call broker.
- Do not write live Redis.
- Do not enable paper/live.
- Do not patch app/, services/, bin/, integrations/, risk, execution, broker, or main.
- Write proof_replay_data_a15_selector_surface_probe_*.json.
- Write docs/milestones/replay_data_a15_selector_surface_probe_*.md.
- Final summary must include surface_probe_ok, all_required_surfaces_present, engine_ready, next_batch.

A14 goal:
- Read latest REPLAY-DATA-A13 proof.
- Locate canonical_root, source_date, and risk_outputs_candidate.csv.
- Inspect risk_outputs_candidate schema and sample rows.
- Inspect execution shadow expectations read-only from replay contracts/reports and services/execution.py.
- Create execution_shadow_candidate.csv only if schema-safe and sandbox/candidate-only.
- Use conservative no_order / not_sent / qty=0 rows unless proven otherwise.
- Do not call broker.
- Do not send orders.
- Do not run full replay engine.
- Do not patch app/, services/, bin/, integrations/, risk, execution, broker, or main.
- Write proof_replay_data_a14_execution_shadow_*.json.
- Write docs/milestones/replay_data_a14_execution_shadow_*.md.
- Final summary must say execution_shadow_candidate_written, row_count, engine_ready=false, next_batch.

A13 goal:
- Read latest REPLAY-DATA-A12 proof.
- Locate canonical_root, source_date, and strategy_decisions_candidate.csv.
- Inspect strategy_decisions_candidate schema and sample rows.
- Inspect risk output expectations read-only from replay contracts/reports and services/risk.py.
- Create risk_outputs_candidate.csv only if schema-safe and sandbox/candidate-only.
- Use conservative allow=false / no_order / risk_blocked shadow rows unless proven otherwise.
- Do not create execution_shadow yet.
- Do not run full replay engine.
- Do not patch app/, services/, bin/, integrations/, risk, execution, broker, or main.
- Write proof_replay_data_a13_risk_outputs_shadow_*.json.
- Write docs/milestones/replay_data_a13_risk_outputs_shadow_*.md.
- Final summary must say risk_outputs_candidate_written, row_count, engine_ready=false, next_batch.

A12 goal:
- Read latest REPLAY-DATA-A11 proof.
- Locate canonical_root, source_date, and features_rows_candidate.csv.
- Inspect features_rows_candidate schema and sample rows.
- Inspect strategy output expectations read-only from replay contracts/reports and services/strategy.py.
- Create strategy_decisions_candidate.csv only if schema-safe and sandbox/candidate-only.
- Use conservative HOLD/NO_TRADE shadow rows unless proven strategy signals can be reconstructed.
- Do not create risk_outputs or execution_shadow.
- Do not run full replay engine.
- Do not patch app/, services/, bin/, integrations/, risk, execution, broker, or main.
- Write proof_replay_data_a12_strategy_decisions_shadow_*.json.
- Write docs/milestones/replay_data_a12_strategy_decisions_shadow_*.md.
- Final summary must say strategy_decisions_candidate_written, row_count, engine_ready=false, next_batch.

A11 goal:
- Read latest REPLAY-DATA-A10 proof.
- Locate canonical_root and source_date.
- Inspect quote_ticks_mme_fut_stream.csv and quote_ticks_mme_opt_stream.csv.
- Inspect replay dataset.py / contracts.py / reports.py for features_rows expectations.
- Inspect app/mme_scalpx/services/features.py only read-only to learn likely feature output names.
- Create a conservative features_rows reconstruction candidate only if it is schema-safe.
- Prefer a candidate named features_rows_candidate.csv or features_rows.csv only if clearly accepted by replay discovery.
- Include source fields and simple derived fields:
  ts_event, symbol, side/source_stream, bid, ask, ltp, mid, spread, provider, instrument_token.
- Do not create strategy_decisions, risk_outputs, or execution_shadow yet.
- Run selector-only probe only; do not run replay engine.
- Write proof_replay_data_a11_features_rows_reconstruction_*.json.
- Write docs/milestones/replay_data_a11_features_rows_reconstruction_*.md.
- Final summary must say:
  features_rows_candidate_written
  row_count
  selector_plan_ok
  engine_ready=false
  next_batch=REPLAY-DATA-A12 strategy_decisions shadow reconstruction audit
"""


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def latest_replay_proof() -> Path:
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
        "run/proofs/proof_replay_data_a14_execution_shadow_*.json",
        "run/proofs/proof_replay_data_a13_risk_outputs_shadow_*.json",
        "run/proofs/proof_replay_data_a12_strategy_decisions_shadow_*.json",
        "run/proofs/proof_replay_data_a11_features_rows_reconstruction_*.json",
        "run/proofs/proof_replay_data_a10_selector_only_cli_dry_probe_*.json",
        "run/proofs/proof_replay_data_a9_quote_schema_transform_*.json",
        "run/proofs/proof_replay_data_a8b_deep_csv_payload_schema_*.json",
        "run/proofs/proof_replay_data_a7_sandbox_canonical_day_dataset_*.json",
    ]
    candidates: list[Path] = []
    for pat in patterns:
        candidates.extend(ROOT.glob(pat))
    if not candidates:
        raise SystemExit("No replay proof found.")
    return max(candidates, key=lambda p: p.stat().st_mtime)



def load_context_memory() -> dict[str, Any]:
    ctx = ROOT / "ai_patch_runner" / "context"
    files = [
        "project_constitution.md",
        "latest_chain_summary.md",
        "known_contracts.md",
        "replay_current_state.json",
        "safety_boundary.json",
        "allowed_paths.json",
        "blocked_paths.json",
    ]
    out: dict[str, Any] = {}
    for name in files:
        p = ctx / name
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            # Hard cap to keep prompts small.
            out[name] = text[:12000]
        except Exception as exc:
            out[name] = f"__READ_ERROR__ {type(exc).__name__}: {exc}"
    return out


def summarize_proof(proof: dict[str, Any]) -> dict[str, Any]:
    summary = proof.get("summary", {})
    selector_probe = proof.get("selector_probe", {})
    findings = proof.get("findings", [])

    return {
        "batch": proof.get("batch"),
        "title": proof.get("title"),
        "summary": summary,
        "selector_probe": selector_probe,
        "findings": [
            {
                "severity": f.get("severity"),
                "area": f.get("area"),
                "message": f.get("message"),
            }
            for f in findings
        ],
        "canonical_root": proof.get("canonical_root") or summary.get("canonical_root"),
        "source_date": proof.get("source_date") or summary.get("source_date"),
        "dataset_id": summary.get("dataset_id") or selector_probe.get("dataset_id"),
        "safety": proof.get("safety", {}),
    }


def local_replay_classification(proof_summary: dict[str, Any]) -> dict[str, Any]:
    batch = proof_summary.get("batch")
    summary = proof_summary.get("summary") or {}
    findings = proof_summary.get("findings") or []

    if batch == "REPLAY-DATA-A16" and (
        summary.get("contract_shape_ok") is True
        or str(summary.get("next_batch", "")).startswith("REPLAY-DATA-A17")
        or str(proof_summary.get("next_batch", "")).startswith("REPLAY-DATA-A17")
    ):
        return {
            "verdict": "PASS_NEXT_ENGINE_READINESS_BLOCKER_DIAGNOSIS",
            "next_batch": "REPLAY-DATA-A17",
            "next_goal": "Diagnose why engine_ready_candidate is false after contract/shape audit; no full engine execution.",
            "reason": "A16 passed contract/shape audit but engine_ready_candidate is false. Next step is blocker diagnosis before any engine dry run.",
        }

    if batch == "REPLAY-DATA-A15" and (
        summary.get("surface_probe_ok") is True
        or summary.get("all_required_surfaces_present") is True
        or str(summary.get("next_batch", "")).startswith("REPLAY-DATA-A16")
        or str(proof_summary.get("next_batch", "")).startswith("REPLAY-DATA-A16")
    ):
        return {
            "verdict": "PASS_NEXT_REPLAY_CONTRACT_SHAPE_AUDIT",
            "next_batch": "REPLAY-DATA-A16",
            "next_goal": "Audit replay dataset contract/shape compatibility across candidate surfaces; no full engine execution.",
            "reason": "A15 proved candidate surfaces exist. Next step is contract/shape compatibility audit before any full replay engine dry-run.",
        }

    if batch == "REPLAY-DATA-A14" and (
        summary.get("execution_shadow_candidate_written") is True
        or str(summary.get("next_batch", "")).startswith("REPLAY-DATA-A15")
        or str(proof_summary.get("next_batch", "")).startswith("REPLAY-DATA-A15")
    ):
        return {
            "verdict": "PASS_NEXT_SELECTOR_ONLY_SURFACE_PROBE",
            "next_batch": "REPLAY-DATA-A15",
            "next_goal": "Run selector-only replay-data surface probe over quote/features/strategy/risk/execution candidate surfaces; no full engine.",
            "reason": "A14 wrote execution_shadow_candidate or declared A15 as next; next layer is selector-only replay-data surface probe.",
        }

    if batch == "REPLAY-DATA-A13" and summary.get("risk_outputs_candidate_written") is True:
        return {
            "verdict": "PASS_NEXT_EXECUTION_SHADOW_AUDIT",
            "next_batch": "REPLAY-DATA-A14",
            "next_goal": "Audit and create execution_shadow candidate from risk_outputs_candidate; no broker/orders/full engine.",
            "reason": "A13 wrote risk_outputs_candidate; next layer is execution_shadow reconstruction audit.",
        }

    if batch == "REPLAY-DATA-A12" and summary.get("strategy_decisions_candidate_written") is True:
        return {
            "verdict": "PASS_NEXT_RISK_OUTPUTS_SHADOW_AUDIT",
            "next_batch": "REPLAY-DATA-A13",
            "next_goal": "Audit and create risk_outputs shadow reconstruction candidate from strategy_decisions_candidate; no execution/full engine.",
            "reason": "A12 wrote strategy_decisions_candidate; next layer is risk_outputs shadow reconstruction audit.",
        }

    if batch == "REPLAY-DATA-A11" and summary.get("features_rows_candidate_written") is True and summary.get("selector_plan_ok") is True:
        return {
            "verdict": "PASS_NEXT_STRATEGY_DECISIONS_SHADOW_AUDIT",
            "next_batch": "REPLAY-DATA-A12",
            "next_goal": "Audit and create strategy_decisions shadow reconstruction candidate from features_rows_candidate; no risk/execution/full engine.",
            "reason": "A11 wrote features_rows_candidate and selector plan is still OK; next layer is strategy_decisions shadow reconstruction audit.",
        }

    if batch == "REPLAY-DATA-A10" and summary.get("overall_verdict") == "PASS" and summary.get("selector_plan_ok") is True:
        return {
            "verdict": "PASS_NEXT_FEATURES_ROWS_RECONSTRUCTION",
            "next_batch": "REPLAY-DATA-A11",
            "next_goal": "Reconstruct features_rows candidate from quote feeds; selector-only validation; no engine execution.",
            "reason": "A10 proved replay_run selector is ready for 2026-04-17 quote dataset, but engine remains blocked by missing features/strategy/risk/execution surfaces.",
        }

    if batch == "REPLAY-DATA-A9" and summary.get("overall_verdict") == "PASS":
        return {
            "verdict": "PASS_NEXT_SELECTOR_CLI_PROBE",
            "next_batch": "REPLAY-DATA-A10",
            "next_goal": "Run selector-only replay_run CLI dry probe.",
            "reason": "A9 transformed quote files and selector probe passed.",
        }

    if summary.get("overall_verdict") == "FAIL":
        return {
            "verdict": "FAIL_REPAIR_REQUIRED",
            "next_batch": f"{batch or 'REPLAY'}-REPAIR",
            "next_goal": "Generate a targeted audit/repair package for the latest failed replay proof.",
            "reason": "Latest proof overall_verdict is FAIL.",
        }

    return {
        "verdict": "UNCLEAR_AUDIT_REQUIRED",
        "next_batch": "REPLAY-DATA-NEXT-AUDIT",
        "next_goal": "Inspect latest replay proof and generate conservative audit-only next step.",
        "reason": "No specialized classifier matched latest proof.",
    }


def normalize_script(text: str) -> str:
    s = text.strip()
    if "```" in s:
        m = re.search(r"```(?:bash|sh)?\s*(.*?)```", s, flags=re.S | re.I)
        if m:
            s = m.group(1).strip()
        else:
            s = s.replace("```bash", "").replace("```sh", "").replace("```", "").strip()
    if s.startswith("bash\n"):
        s = s[5:].strip()
    return s.rstrip() + "\n"


def validate_script(script: str, expected_batch: str) -> tuple[bool, list[str]]:
    findings: list[str] = []
    lower = script.lower()

    if expected_batch == "REPLAY-DATA-A17":
        required_terms = [
            expected_batch,
            "engine_readiness_blocker",
            "blocker_diagnosis_ok",
            "engine_ready_candidate",
            "blocker_count",
            "recommended_next_batch",
            "proof_replay_data_a17_engine_readiness_blocker",
            "SCALPX_OBSERVE_ONLY=1",
            "engine_execution_performed",
            "broker_calls_executed",
            "live_redis_writes_executed",
            "paper_or_live_enabled",
            "orders_sent",
        ]
    elif expected_batch == "REPLAY-DATA-A16":
        required_terms = [
            expected_batch,
            "contract_shape",
            "accepted_file_stems",
            "missing_expected_surfaces",
            "incompatible_surfaces",
            "engine_ready_candidate",
            "proof_replay_data_a16_contract_shape_audit",
            "SCALPX_OBSERVE_ONLY=1",
            "engine_execution_performed",
            "broker_calls_executed",
            "live_redis_writes_executed",
            "paper_or_live_enabled",
            "orders_sent",
        ]
    elif expected_batch == "REPLAY-DATA-A15":
        required_terms = [
            expected_batch,
            "selector",
            "surface_probe",
            "execution_shadow_candidate",
            "risk_outputs_candidate",
            "strategy_decisions_candidate",
            "features_rows_candidate",
            "proof_replay_data_a15_selector_surface_probe",
            "SCALPX_OBSERVE_ONLY=1",
            "engine_execution_performed",
            "broker_calls_executed",
            "live_redis_writes_executed",
            "paper_or_live_enabled",
            "orders_sent",
        ]
    elif expected_batch == "REPLAY-DATA-A14":
        required_terms = [
            expected_batch,
            "execution_shadow",
            "risk_outputs_candidate",
            "proof_replay_data_a14_execution_shadow",
            "SCALPX_OBSERVE_ONLY=1",
            "engine_execution_performed",
            "broker_calls_executed",
            "live_redis_writes_executed",
            "paper_or_live_enabled",
            "orders_sent",
        ]
    elif expected_batch == "REPLAY-DATA-A13":
        required_terms = [
            expected_batch,
            "risk_outputs",
            "strategy_decisions_candidate",
            "proof_replay_data_a13_risk_outputs_shadow",
            "SCALPX_OBSERVE_ONLY=1",
            "engine_execution_performed",
            "broker_calls_executed",
            "live_redis_writes_executed",
            "paper_or_live_enabled",
        ]
    elif expected_batch == "REPLAY-DATA-A12":
        required_terms = [
            expected_batch,
            "strategy_decisions",
            "features_rows_candidate",
            "proof_replay_data_a12_strategy_decisions_shadow",
            "SCALPX_OBSERVE_ONLY=1",
            "engine_execution_performed",
            "broker_calls_executed",
            "live_redis_writes_executed",
            "paper_or_live_enabled",
        ]
    else:
        required_terms = [
            expected_batch,
            "features_rows",
            "quote_ticks_mme_fut_stream",
            "quote_ticks_mme_opt_stream",
            "proof_replay_data_a11_features_rows_reconstruction",
            "SCALPX_OBSERVE_ONLY=1",
            "engine_execution_performed",
            "broker_calls_executed",
            "live_redis_writes_executed",
            "paper_or_live_enabled",
        ]
    for term in required_terms:
        if term.lower() not in lower:
            findings.append(f"missing_required_term:{term}")

    if "```" in script:
        findings.append("markdown_fence_detected")

    blocked_line_patterns = [
        ("nohup_command", r"^\s*nohup\b"),
        ("systemctl_command", r"^\s*(sudo\s+)?systemctl\b"),
        ("service_command", r"^\s*(sudo\s+)?service\s+[A-Za-z0-9_.@-]+(?:\s+|$)"),
        ("main_runtime_start", r"^\s*(python|python3|\.venv/bin/python)\s+-m\s+app\.mme_scalpx\.main\b"),
        ("redis_mutation", r"^\s*redis-cli\s+.*\b(SET|HSET|XADD|DEL)\b"),
        ("paper_enabled", r"SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME\s*=\s*1"),
        ("real_live_enabled", r"SCALPX_REAL_LIVE_ALLOWED\s*=\s*1|SCALPX_ALLOW_REAL_LIVE\s*=\s*1"),
        ("patch_app", r"cat\s*>\s*app/|sed\s+-i\s+.*app/|cp\s+.*\sapp/"),
        ("patch_bin_replay_run", r"cat\s*>\s*bin/replay_run.py|sed\s+-i\s+.*bin/replay_run.py"),
        ("patch_services", r"cat\s*>\s*app/mme_scalpx/services/|sed\s+-i\s+.*app/mme_scalpx/services/"),
    ]

    for lineno, line in enumerate(script.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for name, pat in blocked_line_patterns:
            if re.search(pat, stripped, flags=re.I):
                findings.append(f"{name}:line_{lineno}:{stripped[:180]}")

    if "features_rows.csv" in lower and "refusing to overwrite" not in lower:
        findings.append("features_rows_csv_write_without_overwrite_guard")
    if expected_batch != "REPLAY-DATA-A12" and "strategy_decisions" in lower and "do not create strategy_decisions" not in lower:
        findings.append("mentions_strategy_decisions_may_be_ok_but_review")
    if expected_batch != "REPLAY-DATA-A13" and "risk_outputs" in lower and "do not create" not in lower:
        findings.append("mentions_risk_outputs_may_be_ok_but_review")

    return (not [f for f in findings if not f.startswith("mentions_")]), findings


def policy_check_script(script_path: Path) -> dict[str, Any]:
    if not POLICY_CHECK.exists():
        return {"ok": False, "error": "policy checker missing"}
    p = subprocess.run(
        [str(PYBIN), str(POLICY_CHECK), "--command-file", str(script_path), "--json"],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
    )
    payload = None
    try:
        payload = json.loads(p.stdout)
    except Exception:
        payload = None
    return {
        "returncode": p.returncode,
        "stdout": p.stdout[-8000:],
        "stderr": p.stderr[-8000:],
        "payload": payload,
        "ok": p.returncode == 0 and bool(payload and payload.get("ok") is True),
    }


def safe_slug(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:90] or "replay_next_batch"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proof", default="")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-5.5"))
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set")

    proof_path = Path(args.proof) if args.proof else latest_replay_proof()
    if not proof_path.is_absolute():
        proof_path = ROOT / proof_path

    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    proof_summary = summarize_proof(proof)
    context_memory = load_context_memory()
    local_classification = local_replay_classification(proof_summary)
    expected_batch = local_classification["next_batch"]

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y%m%d_%H%M%S")
    slug = safe_slug(expected_batch + "_" + local_classification["verdict"])

    prompt_record_path = PROMPT_DIR / f"{ts}_{slug}_prompt.json"
    out_script = OUT_DIR / f"{ts}_{slug}.sh"
    meta_path = REPORT_DIR / f"{ts}_{slug}_meta.json"

    prompt_record = {
        "created_at_utc": now.isoformat(),
        "mode": "ai_replay_r2_generate_only_no_execute",
        "model": args.model,
        "latest_proof": str(proof_path),
        "proof_summary": proof_summary,
        "context_memory": context_memory,
        "local_classification": local_classification,
        "safety": {
            "executes_generated_script": False,
            "patches_real_project": False,
            "starts_services": False,
            "calls_broker": False,
            "writes_live_redis": False,
            "enables_paper_or_live": False,
        },
    }
    prompt_record_path.write_text(json.dumps(prompt_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    user_prompt = f"""
Generate the next safe bash command package.

Latest replay proof path:
{proof_path}

Local classification:
{json.dumps(local_classification, indent=2)}

Proof summary:
{json.dumps(proof_summary, indent=2)}

Local context memory:
{json.dumps(context_memory, indent=2)}

Expected batch:
{expected_batch}

Generate only this expected batch. Do not generate any other batch.
"""

    client = OpenAI()
    response = client.responses.create(
        model=args.model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw = response.output_text
    script = normalize_script(raw)
    out_script.write_text(script, encoding="utf-8")
    out_script.chmod(0o755)

    static_ok, static_findings = validate_script(script, expected_batch)
    policy_result = policy_check_script(out_script)

    meta = {
        "created_at_utc": now.isoformat(),
        "version": "AI-REPLAY-R2",
        "mode": "generate_next_replay_batch_only_no_execution",
        "model": args.model,
        "latest_proof": str(proof_path),
        "prompt_record": str(prompt_record_path),
        "output_script": str(out_script),
        "local_classification": local_classification,
        "expected_batch": expected_batch,
        "static_validation_ok": static_ok,
        "static_findings": static_findings,
        "policy_validation": policy_result,
        "runner_safety": {
            "executed_generated_script": False,
            "patched_real_project": False,
            "started_services": False,
            "called_broker": False,
            "wrote_live_redis": False,
            "enabled_paper_or_live": False,
        },
        "sha256": {
            "output_script": sha256_file(out_script),
            "prompt_record": sha256_file(prompt_record_path),
        },
    }
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("AI-REPLAY-R2 COMPLETE")
    print(f"Latest proof:      {proof_path}")
    print(f"Classification:    {local_classification['verdict']}")
    print(f"Expected batch:    {expected_batch}")
    print(f"Generated script:  {out_script}")
    print(f"Metadata:          {meta_path}")
    print(f"Static validation: {static_ok}")
    print(f"Policy validation: {policy_result.get('ok')}")
    if static_findings:
        print("Static findings:")
        for f in static_findings:
            print(f"  - {f}")
    if not policy_result.get("ok"):
        print("Policy findings/output:")
        print(policy_result.get("stdout", "")[-3000:])
    print()
    print("IMPORTANT: AI-REPLAY-R2 does not run the generated script.")
    if not static_ok or not policy_result.get("ok"):
        print("DO NOT RUN generated script. Validation failed.")
        return 2

    print("Review the generated script manually before running.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
