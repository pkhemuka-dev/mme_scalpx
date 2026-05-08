from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path.cwd().resolve()
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
NOW = datetime.now(timezone.utc).isoformat()

BATCH = "RAW-AA13B-R3"
TAG = f"raw_aa13b_r3_true_row_artifact_resolver_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "research_gate" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / f"batch_raw_aa13b_r3_{TS}"
DOC_DIR = ROOT / "docs" / "research_gate"
MILESTONE_DIR = ROOT / "docs" / "milestones"

AUTHORITY_MAP = ROOT / "etc" / "research_gate" / "raw_doctrine_economics_authority_map.json"
AA13B_TOOL = ROOT / "bin" / "raw_aa13b_economics_derivation.py"
TARGET_TOOL = ROOT / "bin" / "raw_aa13b_r3_true_row_artifact_resolver.py"

PREV_R2 = PROOF_DIR / "proof_raw_aa13b_r2_input_artifact_resolver.json"

PROOF_PATH = PROOF_DIR / "proof_raw_aa13b_r3_true_row_artifact_resolver.json"
FREEZE_PATH = PROOF_DIR / "proof_raw_aa13b_r3_freeze_final.json"
DOC_PATH = DOC_DIR / "RAW_AA13B_R3_TRUE_ROW_ARTIFACT_RESOLVER.md"
MILESTONE_PATH = MILESTONE_DIR / f"batch_raw_aa13b_r3_true_row_artifact_resolver_{TS}.md"

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

REJECT_NAME_TOKENS = [
    "ranked_existing_evidence_datasets",
    "source_artifact_breakdown",
    "family_side_matrix",
    "blocker_matrix",
    "oi_wall_context_matrix",
    "oi_wall_source_breakdown",
    "unknown_trade_source_gap_map",
    "unknown_trade_lineage_map",
    "candidate_profiles",
    "resolver_hits",
]

PREFERRED_NAME_TOKENS = [
    "aa10", "aa11", "aa12",
    "enriched", "backfilled", "family_backfill",
    "execution", "trade", "trades", "replay",
]

CSV_PATH_RE = re.compile(r"[\w./-]+\.csv")


def rel(p: pathlib.Path | None) -> str | None:
    if p is None:
        return None
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(p)


def abs_path(s: str) -> pathlib.Path:
    p = pathlib.Path(s)
    return p if p.is_absolute() else ROOT / p


def sha_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ensure_dirs() -> None:
    for d in [PROOF_DIR, RUN_DIR, BACKUP_DIR, DOC_DIR, MILESTONE_DIR, ROOT / "bin"]:
        d.mkdir(parents=True, exist_ok=True)


def backup_existing() -> list[dict[str, Any]]:
    copied = []
    for p in [TARGET_TOOL, PROOF_PATH, FREEZE_PATH, DOC_PATH]:
        if p.exists():
            dst = BACKUP_DIR / rel(p)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            copied.append({"from": rel(p), "to": rel(dst), "sha256": sha_file(p)})
    (BACKUP_DIR / "NO_PRODUCTION_FILES_MODIFIED.txt").write_text(
        "RAW-AA13B-R3 only adds RAW resolver/proof artifacts. No replay, broker IO, Redis live write, order sending, or paper/live enablement.\n",
        encoding="utf-8",
    )
    return copied


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


def load_json(path: pathlib.Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def walk_strings(obj: Any):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_strings(v)
    elif isinstance(obj, str):
        yield obj


def collect_csv_references_from_proofs() -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}

    proof_patterns = [
        "run/proofs/proof_raw_aa10*.json",
        "run/proofs/proof_raw_aa11*.json",
        "run/proofs/proof_raw_aa12*.json",
        "run/proofs/proof_raw_q*.json",
        "run/proofs/proof_raw_*family*.json",
        "run/proofs/proof_raw_*backfill*.json",
        "run/proofs/proof_raw_*execution*.json",
        "run/proofs/proof_raw_*replay*.json",
    ]

    for pat in proof_patterns:
        for proof in ROOT.glob(pat):
            obj = load_json(proof)
            if obj is None:
                continue
            for s in walk_strings(obj):
                for m in CSV_PATH_RE.finditer(s):
                    raw = m.group(0)
                    p = abs_path(raw)
                    if p.exists() and p.is_file():
                        refs.setdefault(rel(p), []).append(rel(proof))

    return refs


def csv_profile(path: pathlib.Path, proof_refs: list[str] | None = None) -> dict[str, Any]:
    proof_refs = proof_refs or []
    r = rel(path)
    name = path.name.lower()
    path_lower = r.lower()

    profile: dict[str, Any] = {
        "path": r,
        "size": path.stat().st_size,
        "sha256": sha_file(path),
        "proof_refs": sorted(set(proof_refs)),
        "header": [],
        "rows": 0,
        "family_counts": {},
        "recognized_family_rows": 0,
        "recognized_family_set": [],
        "has_trade_like_columns": False,
        "has_execution_like_columns": False,
        "has_economics_like_columns": False,
        "is_rejected_artifact_class": False,
        "reject_reasons": [],
        "score": 0,
    }

    if any(tok in name or tok in path_lower for tok in REJECT_NAME_TOKENS):
        profile["is_rejected_artifact_class"] = True
        profile["reject_reasons"].append("diagnostic_manifest_matrix_or_unknown_gap_artifact")

    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            header = list(reader.fieldnames or [])
            profile["header"] = header
            low = {h.lower() for h in header}

            trade_cols = {
                "trade_family", "family", "strategy_family", "strategy_id",
                "side", "selected_leg", "entry_mode",
            }
            execution_cols = {
                "entry_price", "exit_price", "qty", "gross_pnl", "costs",
                "net_pnl_after_costs", "exit_reason", "entry_ts", "exit_ts",
            }
            economics_cols = {
                "target_ticks", "stop_ticks", "reward_ticks", "reward_cost_ratio",
                "target_points", "hard_stop_points", "tick_size",
            }

            profile["has_trade_like_columns"] = bool(low & trade_cols)
            profile["has_execution_like_columns"] = bool(low & execution_cols)
            profile["has_economics_like_columns"] = bool(low & economics_cols)

            for row in reader:
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

    recognized_set = sorted(set(profile["family_counts"]) & FAMILIES)
    profile["recognized_family_set"] = recognized_set

    score = 0
    if proof_refs:
        score += 40
    if any(tok in path_lower for tok in PREFERRED_NAME_TOKENS):
        score += 25
    if not profile["is_rejected_artifact_class"]:
        score += 20
    if profile["has_trade_like_columns"]:
        score += 25
    if profile["has_execution_like_columns"]:
        score += 20
    if profile["rows"] >= 2400:
        score += 35
    if profile["rows"] >= 40000:
        score += 45
    if profile["recognized_family_rows"] >= 500:
        score += 50
    elif profile["recognized_family_rows"] > 0:
        score += 10
    if len(recognized_set) >= 3:
        score += 20
    if len(recognized_set) == 5:
        score += 30

    profile["score"] = score
    return profile


def discover_candidates() -> list[dict[str, Any]]:
    refs = collect_csv_references_from_proofs()
    paths: dict[str, pathlib.Path] = {}

    for ref_path in refs:
        p = abs_path(ref_path)
        if p.exists() and p.is_file():
            paths[rel(p)] = p

    for p in ROOT.glob("run/research_gate/**/*.csv"):
        if not p.is_file():
            continue
        if "aa13b_r3" in rel(p).lower():
            continue
        paths[rel(p)] = p

    profiles = [csv_profile(p, refs.get(rel(p), [])) for p in paths.values()]
    profiles.sort(
        key=lambda x: (
            x["score"],
            x["rows"],
            x["recognized_family_rows"],
            len(x["proof_refs"]),
        ),
        reverse=True,
    )
    return profiles


def eligible_profiles(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for c in profiles:
        if c["is_rejected_artifact_class"]:
            continue
        if c["rows"] < 2400:
            continue
        if c["recognized_family_rows"] < 500:
            continue
        if len(c["recognized_family_set"]) < 3:
            continue
        out.append(c)
    return out


def run_derivation(input_csv: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, dict[str, Any]]:
    output_csv = RUN_DIR / f"{input_csv.stem}_aa13b_r3_economics_derived.csv"
    summary_json = RUN_DIR / "aa13b_r3_derivation_summary.json"

    pybin = ROOT / ".venv" / "bin" / "python"
    if not pybin.exists():
        pybin = pathlib.Path("/usr/bin/python3")

    subprocess.run(
        [
            str(pybin),
            str(AA13B_TOOL),
            "--input-csv", str(input_csv),
            "--output-csv", str(output_csv),
            "--authority-map", str(AUTHORITY_MAP),
            "--summary-json", str(summary_json),
        ],
        check=True,
        timeout=120,
    )

    return output_csv, summary_json, json.loads(summary_json.read_text(encoding="utf-8"))


def validate_derivation(output_csv: pathlib.Path | None, summary: dict[str, Any] | None) -> list[str]:
    blockers = []
    if output_csv is None or summary is None:
        return ["NO_DERIVATION_OUTPUT_CREATED"]

    rows = int(summary.get("rows_written", 0) or 0)
    family_counts = summary.get("family_counts") or {}
    ready_counts = summary.get("ready_counts") or {}

    recognized = sum(v for k, v in family_counts.items() if k in FAMILIES)
    ready_true = int(ready_counts.get("true", 0) or 0)
    ready_partial = int(ready_counts.get("partial", 0) or 0)

    if rows < 2400:
        blockers.append("DERIVED_ROWS_BELOW_MINIMUM_ROW_LEVEL_THRESHOLD")
    if recognized < 500:
        blockers.append("RECOGNIZED_FAMILY_ROWS_BELOW_MINIMUM_THRESHOLD")
    if len(set(family_counts) & FAMILIES) < 3:
        blockers.append("INSUFFICIENT_FAMILY_DIVERSITY")
    if ready_true + ready_partial <= 0:
        blockers.append("NO_TRUE_OR_PARTIAL_READY_ROWS")

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


def previous_r2_eval() -> dict[str, Any]:
    obj = load_json(PREV_R2)
    if not obj:
        return {"present": False, "invalid_for_aa14": True, "reasons": ["missing_or_unreadable"]}

    summary = obj.get("derivation_summary") or {}
    rows = int(summary.get("rows_written", 0) or 0)
    family_counts = summary.get("family_counts") or {}
    ready_counts = summary.get("ready_counts") or {}

    reasons = []
    if rows < 2400:
        reasons.append("previous_selected_tiny_matrix_not_row_level_dataset")
    if sum(v for k, v in family_counts.items() if k in FAMILIES) < 500:
        reasons.append("previous_recognized_family_rows_too_small")
    if int(ready_counts.get("true", 0) or 0) <= 0:
        reasons.append("previous_zero_true_ready_rows")

    return {
        "present": True,
        "path": rel(PREV_R2),
        "verdict": obj.get("verdict"),
        "selected_input_csv": obj.get("selected_input_csv"),
        "derived_output_csv": obj.get("derived_output_csv"),
        "rows_written": rows,
        "family_counts": family_counts,
        "ready_counts": ready_counts,
        "invalid_for_aa14": bool(reasons),
        "reasons": reasons,
    }


def main() -> int:
    ensure_dirs()
    backups = backup_existing()
    TARGET_TOOL.write_text(pathlib.Path(__file__).read_text(encoding="utf-8"), encoding="utf-8")

    blockers = []
    if not AUTHORITY_MAP.exists():
        blockers.append("AUTHORITY_MAP_MISSING")
    if not AA13B_TOOL.exists():
        blockers.append("AA13B_TOOL_MISSING")

    prev_eval = previous_r2_eval()
    profiles = discover_candidates()
    eligible = eligible_profiles(profiles)

    selected_profile = eligible[0] if eligible else None
    selected_path = abs_path(selected_profile["path"]) if selected_profile else None

    output_csv = None
    summary_json = None
    summary = None
    source_sha_before = None
    source_sha_after = None

    if not blockers and selected_path is None:
        blockers.append("NO_TRUE_ROW_LEVEL_FAMILY_DATASET_FOUND")
    elif not blockers and selected_path is not None:
        source_sha_before = sha_file(selected_path)
        output_csv, summary_json, summary = run_derivation(selected_path)
        source_sha_after = sha_file(selected_path)
        if source_sha_before != source_sha_after:
            blockers.append("SOURCE_INPUT_MUTATED_UNEXPECTEDLY")
        blockers.extend(validate_derivation(output_csv, summary))

    verdict = "RAW_AA13B_R3_TRUE_ROW_ARTIFACT_RESOLVER_READY" if not blockers else "RAW_AA13B_R3_TRUE_ROW_ARTIFACT_RESOLVER_DEFERRED"
    next_rec = "RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER" if not blockers else "RAW_AA13B_R4_EXPLICIT_AA11_AA12_OUTPUT_EXPORT_REQUIRED"

    proof = {
        "batch": BATCH,
        "created_at_utc": NOW,
        "verdict": verdict,
        "blockers": blockers,
        "safety_flags": SAFETY,
        "backups": backups,
        "previous_r2_evaluation": prev_eval,
        "authority_map": rel(AUTHORITY_MAP),
        "aa13b_tool": rel(AA13B_TOOL),
        "resolver_tool": rel(TARGET_TOOL),
        "candidate_count": len(profiles),
        "eligible_candidate_count": len(eligible),
        "candidate_profiles_top_50": profiles[:50],
        "selected_profile": selected_profile,
        "selected_input_csv": rel(selected_path),
        "selected_input_sha_before": source_sha_before,
        "selected_input_sha_after": source_sha_after,
        "derived_output_csv": rel(output_csv),
        "derivation_summary_json": rel(summary_json),
        "derivation_summary": summary,
        "field_resolution": {
            "target_ticks": "derived_from_authority_map_on_true_row_level_dataset_only",
            "stop_ticks": "derived_from_authority_map_on_true_row_level_dataset_only",
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

    (RUN_DIR / "candidate_profiles.json").write_text(json.dumps(profiles, indent=2, sort_keys=True), encoding="utf-8")
    (RUN_DIR / "eligible_candidates.json").write_text(json.dumps(eligible, indent=2, sort_keys=True), encoding="utf-8")
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
        "previous_r2_invalid_for_aa14": prev_eval.get("invalid_for_aa14"),
        "selected_input_csv": rel(selected_path),
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
        "# RAW-AA13B-R3 True Row Artifact Resolver",
        "",
        f"created_at_utc: {NOW}",
        f"verdict: `{verdict}`",
        f"blockers: `{blockers}`",
        f"next_recommendation: `{next_rec}`",
        "",
        "## Previous R2 correction",
        "",
        f"- previous_r2_invalid_for_aa14: `{prev_eval.get('invalid_for_aa14')}`",
        f"- reasons: `{prev_eval.get('reasons')}`",
        "",
        "## Selected input",
        "",
        f"- selected_input_csv: `{rel(selected_path)}`",
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
        "# Batch RAW-AA13B-R3 — True Row Artifact Resolver",
        "",
        f"created_at_utc: {NOW}",
        f"verdict: `{verdict}`",
        f"blockers: `{blockers}`",
        f"next: `{next_rec}`",
        "",
        "Rejects tiny diagnostic matrices and requires true row-level family evidence dataset.",
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
        "previous_r2_invalid_for_aa14": prev_eval.get("invalid_for_aa14"),
        "previous_r2_reasons": prev_eval.get("reasons"),
        "candidate_count": len(profiles),
        "eligible_candidate_count": len(eligible),
        "selected_input_csv": rel(selected_path),
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
