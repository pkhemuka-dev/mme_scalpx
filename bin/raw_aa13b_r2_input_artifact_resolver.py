from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path.cwd().resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
NOW = datetime.now(timezone.utc).isoformat()

BATCH = "RAW-AA13B-R2"
TAG = f"raw_aa13b_r2_input_artifact_resolver_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "research_gate" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / f"batch_raw_aa13b_r2_{TS}"
DOC_DIR = ROOT / "docs" / "research_gate"
MILESTONE_DIR = ROOT / "docs" / "milestones"

AUTHORITY_MAP = ROOT / "etc" / "research_gate" / "raw_doctrine_economics_authority_map.json"
AA13B_TOOL = ROOT / "bin" / "raw_aa13b_economics_derivation.py"
TARGET_TOOL = ROOT / "bin" / "raw_aa13b_r2_input_artifact_resolver.py"

PREV_AA13B_PROOF = PROOF_DIR / "proof_raw_aa13b_economics_derivation_implementation.json"

PROOF_PATH = PROOF_DIR / "proof_raw_aa13b_r2_input_artifact_resolver.json"
FREEZE_PATH = PROOF_DIR / "proof_raw_aa13b_r2_freeze_final.json"
DOC_PATH = DOC_DIR / "RAW_AA13B_R2_INPUT_ARTIFACT_RESOLVER.md"
MILESTONE_PATH = MILESTONE_DIR / f"batch_raw_aa13b_r2_input_artifact_resolver_{TS}.md"

FAMILIES = {"MIST", "MISB", "MISC", "MISR", "MISO"}
FAMILY_KEYS = ["trade_family", "family", "strategy_family", "strategy_id"]
REQUIRED_OUTPUT_FIELDS = ["target_ticks", "stop_ticks", "reward_ticks", "raw_economics_ready"]

SAFETY = {
    "batch": BATCH,
    "raw_only": True,
    "non_live": True,
    "production_strategy_code_patched": False,
    "replay_execution_performed": False,
    "enrichment_or_backfill_performed": False,
    "broker_io_performed": False,
    "order_sending_performed": False,
    "redis_live_write_performed": False,
    "paper_live_enablement_performed": False,
}


def rel(p: pathlib.Path | None) -> str | None:
    if p is None:
        return None
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(p)


def sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ensure_dirs() -> None:
    for d in [PROOF_DIR, RUN_DIR, BACKUP_DIR, DOC_DIR, MILESTONE_DIR, ROOT / "bin"]:
        d.mkdir(parents=True, exist_ok=True)


def backup_existing() -> list[dict]:
    copied = []
    for p in [TARGET_TOOL, PROOF_PATH, FREEZE_PATH, DOC_PATH]:
        if p.exists():
            dst = BACKUP_DIR / rel(p)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            copied.append({"from": rel(p), "to": rel(dst), "sha256": sha_file(p)})
    (BACKUP_DIR / "NO_PRODUCTION_FILES_MODIFIED.txt").write_text(
        "RAW-AA13B-R2 only adds RAW resolver/proof artifacts. No production strategy code, replay, broker IO, Redis live write, or paper/live enablement.\n",
        encoding="utf-8",
    )
    return copied


def load_json(path: pathlib.Path) -> dict:
    if not path.exists():
        return {"present": False}
    try:
        return {"present": True, "path": rel(path), "json": json.loads(path.read_text(encoding="utf-8"))}
    except Exception as exc:
        return {"present": True, "path": rel(path), "error": repr(exc)}


def normalize_family(value: str) -> str:
    s = (value or "").strip().upper().replace("_", "-")
    aliases = {
        "MIS-T": "MIST",
        "MIS-B": "MISB",
        "MIS-C": "MISC",
        "MIS-R": "MISR",
        "MIST": "MIST",
        "MISB": "MISB",
        "MISC": "MISC",
        "MISR": "MISR",
        "MISO": "MISO",
    }
    return aliases.get(s, s.replace("-", ""))


def read_csv_profile(path: pathlib.Path, max_scan: int | None = None) -> dict:
    profile = {
        "path": rel(path),
        "size": path.stat().st_size,
        "sha256": sha_file(path),
        "header": [],
        "rows": 0,
        "family_counts": {},
        "recognized_family_rows": 0,
        "has_trade_like_columns": False,
        "has_economics_like_columns": False,
        "is_rejected_discovery_artifact": False,
        "score": 0,
        "reject_reasons": [],
    }

    name = path.name.lower()
    if "ranked_existing_evidence_datasets" in name or "discovery" in rel(path).lower():
        profile["is_rejected_discovery_artifact"] = True
        profile["reject_reasons"].append("discovery_or_ranked_dataset_manifest")

    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            header = list(reader.fieldnames or [])
            profile["header"] = header
            low_header = {h.lower() for h in header}

            trade_like = {
                "trade_family", "family", "strategy_family", "strategy_id",
                "side", "selected_leg", "entry_mode", "entry_price", "exit_price",
                "net_pnl_after_costs", "exit_reason", "entry_ts", "exit_ts",
            }
            economics_like = {
                "target_ticks", "stop_ticks", "reward_ticks", "reward_cost_ratio",
                "target_points", "hard_stop_points", "tick_size",
            }

            profile["has_trade_like_columns"] = bool(low_header & trade_like)
            profile["has_economics_like_columns"] = bool(low_header & economics_like)

            for idx, row in enumerate(reader):
                if max_scan is not None and idx >= max_scan:
                    break
                profile["rows"] += 1
                fam = ""
                for k in FAMILY_KEYS:
                    if k in row and str(row.get(k, "")).strip():
                        fam = normalize_family(str(row.get(k, "")))
                        break
                profile["family_counts"][fam] = profile["family_counts"].get(fam, 0) + 1
                if fam in FAMILIES:
                    profile["recognized_family_rows"] += 1

    except Exception as exc:
        profile["reject_reasons"].append(f"read_failed:{exc!r}")

    score = 0
    if not profile["is_rejected_discovery_artifact"]:
        score += 20
    if profile["has_trade_like_columns"]:
        score += 30
    if profile["recognized_family_rows"] > 0:
        score += 50
    if profile["rows"] >= 1000:
        score += 20
    if len(set(profile["family_counts"]) & FAMILIES) >= 3:
        score += 20
    if len(set(profile["family_counts"]) & FAMILIES) == 5:
        score += 30
    if profile["has_economics_like_columns"]:
        score += 10

    profile["score"] = score
    return profile


def discover_candidates() -> list[dict]:
    candidates = []
    for p in ROOT.glob("run/research_gate/**/*.csv"):
        if not p.is_file():
            continue
        if "aa13b_r2" in rel(p).lower():
            continue
        candidates.append(read_csv_profile(p))
    candidates.sort(key=lambda x: (x["score"], x["rows"], x["recognized_family_rows"]), reverse=True)
    return candidates


def validate_previous_aa13b(prev: dict) -> dict:
    result = {
        "previous_present": prev.get("present", False),
        "previous_verdict": None,
        "previous_selected_input_csv": None,
        "previous_ready_counts": None,
        "previous_family_counts": None,
        "previous_is_invalid_for_promotion": True,
        "reasons": [],
    }
    obj = prev.get("json") or {}
    if not obj:
        result["reasons"].append("previous_proof_missing_or_unreadable")
        return result

    result["previous_verdict"] = obj.get("verdict")
    result["previous_selected_input_csv"] = obj.get("selected_input_csv")
    summary = obj.get("derivation_summary") or {}
    family_counts = summary.get("family_counts") or {}
    ready_counts = summary.get("ready_counts") or {}

    result["previous_family_counts"] = family_counts
    result["previous_ready_counts"] = ready_counts

    recognized = sum(v for k, v in family_counts.items() if k in FAMILIES)
    ready_true = int(ready_counts.get("true", 0) or 0)
    ready_partial = int(ready_counts.get("partial", 0) or 0)

    if "ranked_existing_evidence_datasets" in str(result["previous_selected_input_csv"]):
        result["reasons"].append("previous_selected_discovery_manifest_not_row_level_trade_dataset")
    if recognized <= 0:
        result["reasons"].append("previous_no_recognized_family_rows")
    if ready_true + ready_partial <= 0:
        result["reasons"].append("previous_all_rows_false_ready")

    result["previous_is_invalid_for_promotion"] = bool(result["reasons"])
    return result


def run_derivation(input_csv: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, dict]:
    output_csv = RUN_DIR / f"{input_csv.stem}_aa13b_r2_economics_derived.csv"
    summary_json = RUN_DIR / "aa13b_r2_derivation_summary.json"

    subprocess.run(
        [
            str(ROOT / ".venv" / "bin" / "python" if (ROOT / ".venv" / "bin" / "python").exists() else pathlib.Path("/usr/bin/python3")),
            str(AA13B_TOOL),
            "--input-csv", str(input_csv),
            "--output-csv", str(output_csv),
            "--authority-map", str(AUTHORITY_MAP),
            "--summary-json", str(summary_json),
        ],
        check=True,
        timeout=90,
    )

    summary = json.loads(summary_json.read_text(encoding="utf-8"))
    return output_csv, summary_json, summary


def validate_output(output_csv: pathlib.Path | None, derivation_summary: dict | None) -> list[str]:
    blockers = []
    if output_csv is None or derivation_summary is None:
        return ["NO_DERIVATION_OUTPUT_CREATED"]

    rows = int(derivation_summary.get("rows_written", 0) or 0)
    family_counts = derivation_summary.get("family_counts") or {}
    ready_counts = derivation_summary.get("ready_counts") or {}

    recognized = sum(v for k, v in family_counts.items() if k in FAMILIES)
    ready_true = int(ready_counts.get("true", 0) or 0)
    ready_partial = int(ready_counts.get("partial", 0) or 0)

    if rows <= 0:
        blockers.append("NO_ROWS_WRITTEN")
    if recognized <= 0:
        blockers.append("NO_RECOGNIZED_FAMILY_ROWS_AFTER_DERIVATION")
    if ready_true + ready_partial <= 0:
        blockers.append("NO_TRUE_OR_PARTIAL_READY_ROWS_AFTER_DERIVATION")

    try:
        with output_csv.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            header = set(reader.fieldnames or [])
            for field in REQUIRED_OUTPUT_FIELDS:
                if field not in header:
                    blockers.append(f"MISSING_OUTPUT_FIELD:{field}")
    except Exception as exc:
        blockers.append(f"OUTPUT_READ_FAILED:{exc!r}")

    return blockers


def main() -> int:
    ensure_dirs()
    backups = backup_existing()

    TARGET_TOOL.write_text(pathlib.Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

    blockers = []
    if not AUTHORITY_MAP.exists():
        blockers.append("AUTHORITY_MAP_MISSING")
    if not AA13B_TOOL.exists():
        blockers.append("AA13B_TOOL_MISSING")

    prev = load_json(PREV_AA13B_PROOF)
    prev_eval = validate_previous_aa13b(prev)

    candidates = discover_candidates()
    eligible = [
        c for c in candidates
        if c["score"] >= 100
        and not c["is_rejected_discovery_artifact"]
        and c["recognized_family_rows"] > 0
    ]

    selected = pathlib.Path(eligible[0]["path"]) if eligible else None
    selected_abs = ROOT / selected if selected and not selected.is_absolute() else selected

    output_csv = None
    summary_json = None
    derivation_summary = None
    source_sha_before = None
    source_sha_after = None

    if blockers:
        pass
    elif selected_abs is None:
        blockers.append("NO_ELIGIBLE_ROW_LEVEL_FAMILY_CSV_FOUND")
    else:
        source_sha_before = sha_file(selected_abs)
        output_csv, summary_json, derivation_summary = run_derivation(selected_abs)
        source_sha_after = sha_file(selected_abs)
        if source_sha_before != source_sha_after:
            blockers.append("SOURCE_INPUT_MUTATED_UNEXPECTEDLY")
        blockers.extend(validate_output(output_csv, derivation_summary))

    verdict = "RAW_AA13B_R2_INPUT_ARTIFACT_RESOLVER_READY" if not blockers else "RAW_AA13B_R2_INPUT_ARTIFACT_RESOLVER_DEFERRED"
    next_rec = "RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER" if not blockers else "RAW_AA13B_R3_EXPLICIT_INPUT_PATH_OR_ARTIFACT_EXPORT"

    proof = {
        "batch": BATCH,
        "created_at_utc": NOW,
        "verdict": verdict,
        "blockers": blockers,
        "safety_flags": SAFETY,
        "backups": backups,
        "previous_aa13b_evaluation": prev_eval,
        "authority_map": rel(AUTHORITY_MAP),
        "aa13b_tool": rel(AA13B_TOOL),
        "resolver_tool": rel(TARGET_TOOL),
        "candidate_count": len(candidates),
        "candidate_profiles_top_30": candidates[:30],
        "eligible_candidate_count": len(eligible),
        "selected_input_csv": rel(selected_abs),
        "selected_input_sha_before": source_sha_before,
        "selected_input_sha_after": source_sha_after,
        "derived_output_csv": rel(output_csv),
        "derivation_summary_json": rel(summary_json),
        "derivation_summary": derivation_summary,
        "field_resolution": {
            "target_ticks": "must_be_derived_from_authority_map_on_row_level_family_dataset",
            "stop_ticks": "must_be_derived_from_authority_map_on_row_level_family_dataset",
            "reward_ticks": "first_target_raw_economics_only",
            "reward_cost_ratio": "left_unavailable_until_cost_model",
            "entry_mode": "preserve_from_source_or_mark_partial",
            "selected_leg": "preserve_from_source_or_mark_partial",
            "side": "preserve_from_source_or_mark_partial",
            "oi_wall_strength": "not_derived",
            "oi_wall_distance_points": "not_derived",
        },
        "outputs": {
            "proof": rel(PROOF_PATH),
            "freeze": rel(FREEZE_PATH),
            "doc": rel(DOC_PATH),
            "milestone": rel(MILESTONE_PATH),
            "run_dir": rel(RUN_DIR),
            "resolver_tool": rel(TARGET_TOOL),
            "derived_output_csv": rel(output_csv),
        },
        "next_recommendation": next_rec,
    }

    (RUN_DIR / "candidate_profiles.json").write_text(json.dumps(candidates, indent=2, sort_keys=True), encoding="utf-8")
    (RUN_DIR / "resolver_summary.json").write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    PROOF_PATH.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")

    freeze = {
        "batch": BATCH,
        "created_at_utc": NOW,
        "freeze_final": True,
        "verdict": verdict,
        "blockers": blockers,
        "proof": rel(PROOF_PATH),
        "safety_flags": SAFETY,
        "previous_aa13b_invalid_for_promotion": prev_eval.get("previous_is_invalid_for_promotion"),
        "selected_input_csv": rel(selected_abs),
        "derived_output_csv": rel(output_csv),
        "source_input_mutated": bool(source_sha_before and source_sha_after and source_sha_before != source_sha_after),
        "no_replay": True,
        "no_broker_io": True,
        "no_live_redis_write": True,
        "no_order_sending": True,
        "no_paper_live_enablement": True,
        "next_recommendation": next_rec,
    }
    FREEZE_PATH.write_text(json.dumps(freeze, indent=2, sort_keys=True), encoding="utf-8")

    md = [
        "# RAW-AA13B-R2 Input Artifact Resolver",
        "",
        f"created_at_utc: {NOW}",
        f"verdict: `{verdict}`",
        f"blockers: `{blockers}`",
        f"next_recommendation: `{next_rec}`",
        "",
        "## Previous AA13B correction",
        "",
        f"- previous_invalid_for_promotion: `{prev_eval.get('previous_is_invalid_for_promotion')}`",
        f"- reasons: `{prev_eval.get('reasons')}`",
        "",
        "## Selected input",
        "",
        f"- selected_input_csv: `{rel(selected_abs)}`",
        f"- derived_output_csv: `{rel(output_csv)}`",
        "",
        "## Safety",
        "",
        "- no replay execution",
        "- no broker IO",
        "- no live Redis writes",
        "- no order sending",
        "- no paper/live enablement",
        "",
        "## Outputs",
        "",
    ]
    for k, v in proof["outputs"].items():
        md.append(f"- {k}: `{v}`")
    DOC_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")

    milestone = [
        "# Batch RAW-AA13B-R2 — Input Artifact Resolver",
        "",
        f"created_at_utc: {NOW}",
        f"verdict: `{verdict}`",
        f"blockers: `{blockers}`",
        f"next: `{next_rec}`",
        "",
        "Corrects AA13B by rejecting discovery/ranking CSVs and requiring a row-level family dataset.",
        "No replay. No broker IO. No Redis live write. No order sending. No paper/live enablement.",
        "",
        f"proof: `{rel(PROOF_PATH)}`",
        f"freeze: `{rel(FREEZE_PATH)}`",
        f"doc: `{rel(DOC_PATH)}`",
        f"run_dir: `{rel(RUN_DIR)}`",
    ]
    MILESTONE_PATH.write_text("\n".join(milestone) + "\n", encoding="utf-8")

    print(json.dumps({
        "batch": BATCH,
        "verdict": verdict,
        "blockers": blockers,
        "previous_aa13b_invalid_for_promotion": prev_eval.get("previous_is_invalid_for_promotion"),
        "previous_aa13b_reasons": prev_eval.get("reasons"),
        "candidate_count": len(candidates),
        "eligible_candidate_count": len(eligible),
        "selected_input_csv": rel(selected_abs),
        "derived_output_csv": rel(output_csv),
        "proof": rel(PROOF_PATH),
        "freeze": rel(FREEZE_PATH),
        "doc": rel(DOC_PATH),
        "milestone": rel(MILESTONE_PATH),
        "run_dir": rel(RUN_DIR),
        "next_recommendation": next_rec,
    }, indent=2, sort_keys=True))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
