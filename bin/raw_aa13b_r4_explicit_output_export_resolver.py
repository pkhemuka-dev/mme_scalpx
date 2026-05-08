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

BATCH = "RAW-AA13B-R4"
TAG = f"raw_aa13b_r4_explicit_output_export_resolver_{TS}"

PROOF_DIR = ROOT / "run" / "proofs"
RUN_DIR = ROOT / "run" / "research_gate" / TAG
BACKUP_DIR = ROOT / "run" / "_code_backups" / f"batch_raw_aa13b_r4_{TS}"
DOC_DIR = ROOT / "docs" / "research_gate"
MILESTONE_DIR = ROOT / "docs" / "milestones"

AUTHORITY_MAP = ROOT / "etc" / "research_gate" / "raw_doctrine_economics_authority_map.json"
AA13B_TOOL = ROOT / "bin" / "raw_aa13b_economics_derivation.py"
TARGET_TOOL = ROOT / "bin" / "raw_aa13b_r4_explicit_output_export_resolver.py"

PREV_R3 = PROOF_DIR / "proof_raw_aa13b_r3_true_row_artifact_resolver.json"

PROOF_PATH = PROOF_DIR / "proof_raw_aa13b_r4_explicit_output_export_resolver.json"
FREEZE_PATH = PROOF_DIR / "proof_raw_aa13b_r4_freeze_final.json"
DOC_PATH = DOC_DIR / "RAW_AA13B_R4_EXPLICIT_OUTPUT_EXPORT_RESOLVER.md"
MILESTONE_PATH = MILESTONE_DIR / f"batch_raw_aa13b_r4_explicit_output_export_resolver_{TS}.md"

FAMILIES = {"MIST", "MISB", "MISC", "MISR", "MISO"}

FAMILY_KEYS = [
    "trade_family",
    "trade_family_after",
    "family",
    "family_after",
    "strategy_family",
    "strategy_id",
    "candidate_family",
    "rank_candidate_family",
]

SIDE_KEYS = ["side", "trade_side", "branch", "option_side", "signal_side"]
SELECTED_LEG_KEYS = ["selected_leg", "selected_option", "instrument", "symbol", "tradingsymbol", "selected_symbol"]
ENTRY_MODE_KEYS = ["entry_mode", "entry_kind", "entry_type"]

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
    "scorecard",
    "summary",
]

PREFERRED_NAME_TOKENS = [
    "aa10", "aa11", "aa12",
    "enriched", "backfilled", "family_backfill",
    "trade_family", "execution", "trade", "trades",
    "replay", "rows", "dataset",
]

ARTIFACT_RE = re.compile(r"[\w./-]+\.(?:csv|jsonl|ndjson|json|parquet)")


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
        "RAW-AA13B-R4 writes RAW resolver/export/proof artifacts only. "
        "No replay, broker IO, Redis live write, order sending, or paper/live enablement.\n",
        encoding="utf-8",
    )
    return copied


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


def first(row: dict[str, Any], keys: list[str]) -> str:
    for k in keys:
        if k in row and str(row.get(k, "")).strip():
            return str(row.get(k, "")).strip()
    return ""


def collect_refs_from_proofs() -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    patterns = [
        "run/proofs/proof_raw_aa10*.json",
        "run/proofs/proof_raw_aa11*.json",
        "run/proofs/proof_raw_aa12*.json",
        "run/proofs/proof_raw_aa13*.json",
        "run/proofs/proof_raw_*backfill*.json",
        "run/proofs/proof_raw_*enrich*.json",
        "run/proofs/proof_raw_*execution*.json",
        "run/proofs/proof_raw_*family*.json",
        "run/proofs/proof_raw_*replay*.json",
    ]

    for pat in patterns:
        for proof in ROOT.glob(pat):
            obj = load_json(proof)
            if obj is None:
                continue
            for s in walk_strings(obj):
                for m in ARTIFACT_RE.finditer(s):
                    raw = m.group(0).strip().rstrip("),]}'\"")
                    p = abs_path(raw)
                    if p.exists() and p.is_file():
                        refs.setdefault(rel(p), []).append(rel(proof))
    return refs


def count_rows_csv(path: pathlib.Path) -> tuple[list[str], int, dict[str, int], int]:
    family_counts: dict[str, int] = {}
    rows = 0
    recognized = 0
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = list(reader.fieldnames or [])
        for row in reader:
            rows += 1
            fam = normalize_family(first(row, FAMILY_KEYS))
            family_counts[fam] = family_counts.get(fam, 0) + 1
            if fam in FAMILIES:
                recognized += 1
    return header, rows, family_counts, recognized


def count_rows_jsonl(path: pathlib.Path) -> tuple[list[str], int, dict[str, int], int]:
    family_counts: dict[str, int] = {}
    header_set: set[str] = set()
    rows = 0
    recognized = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if not isinstance(row, dict):
                continue
            rows += 1
            header_set.update(str(k) for k in row.keys())
            fam = normalize_family(first(row, FAMILY_KEYS))
            family_counts[fam] = family_counts.get(fam, 0) + 1
            if fam in FAMILIES:
                recognized += 1
    return sorted(header_set), rows, family_counts, recognized


def profile_file(path: pathlib.Path, proof_refs: list[str]) -> dict[str, Any]:
    r = rel(path)
    name = path.name.lower()
    lower = r.lower()
    suffix = path.suffix.lower()

    profile: dict[str, Any] = {
        "path": r,
        "suffix": suffix,
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
        "exportable": suffix in [".csv", ".jsonl", ".ndjson", ".parquet"],
        "is_rejected_artifact_class": False,
        "reject_reasons": [],
        "score": 0,
    }

    if any(tok in name or tok in lower for tok in REJECT_NAME_TOKENS):
        profile["is_rejected_artifact_class"] = True
        profile["reject_reasons"].append("diagnostic_manifest_matrix_summary_or_unknown_gap_artifact")

    try:
        if suffix == ".csv":
            header, rows, fam_counts, recognized = count_rows_csv(path)
        elif suffix in [".jsonl", ".ndjson"]:
            header, rows, fam_counts, recognized = count_rows_jsonl(path)
        elif suffix == ".parquet":
            try:
                import pandas as pd  # type: ignore
                df = pd.read_parquet(path)
                header = [str(c) for c in df.columns]
                rows = int(len(df))
                fam_counts = {}
                recognized = 0
                for _, row in df.iterrows():
                    fam = normalize_family(first({str(k): v for k, v in row.items()}, FAMILY_KEYS))
                    fam_counts[fam] = fam_counts.get(fam, 0) + 1
                    if fam in FAMILIES:
                        recognized += 1
            except Exception as exc:
                header, rows, fam_counts, recognized = [], 0, {}, 0
                profile["reject_reasons"].append(f"parquet_profile_failed:{exc!r}")
        else:
            header, rows, fam_counts, recognized = [], 0, {}, 0
            profile["exportable"] = False
            profile["reject_reasons"].append("unsupported_artifact_extension")
    except Exception as exc:
        header, rows, fam_counts, recognized = [], 0, {}, 0
        profile["reject_reasons"].append(f"profile_failed:{exc!r}")

    profile["header"] = header
    profile["rows"] = rows
    profile["family_counts"] = fam_counts
    profile["recognized_family_rows"] = recognized
    profile["recognized_family_set"] = sorted(set(fam_counts) & FAMILIES)

    low = {h.lower() for h in header}
    profile["has_trade_like_columns"] = bool(low & {k.lower() for k in FAMILY_KEYS + SIDE_KEYS + SELECTED_LEG_KEYS + ENTRY_MODE_KEYS})
    profile["has_execution_like_columns"] = bool(low & {
        "entry_price", "exit_price", "qty", "gross_pnl", "costs",
        "net_pnl_after_costs", "exit_reason", "entry_ts", "exit_ts",
    })
    profile["has_economics_like_columns"] = bool(low & {
        "target_ticks", "stop_ticks", "reward_ticks", "reward_cost_ratio",
        "target_points", "hard_stop_points", "tick_size",
    })

    score = 0
    if proof_refs:
        score += 40
    if any(tok in lower for tok in PREFERRED_NAME_TOKENS):
        score += 30
    if not profile["is_rejected_artifact_class"]:
        score += 25
    if profile["exportable"]:
        score += 10
    if profile["has_trade_like_columns"]:
        score += 25
    if profile["has_execution_like_columns"]:
        score += 25
    if rows >= 2400:
        score += 40
    if rows >= 40000:
        score += 50
    if recognized >= 500:
        score += 60
    elif recognized > 0:
        score += 10
    if len(profile["recognized_family_set"]) >= 3:
        score += 25
    if len(profile["recognized_family_set"]) == 5:
        score += 35

    profile["score"] = score
    return profile


def discover_profiles() -> list[dict[str, Any]]:
    refs = collect_refs_from_proofs()
    paths: dict[str, pathlib.Path] = {}

    for r in refs:
        p = abs_path(r)
        if p.exists() and p.is_file():
            paths[rel(p)] = p

    for ext in ["*.csv", "*.jsonl", "*.ndjson", "*.parquet"]:
        for p in ROOT.glob(f"run/research_gate/**/{ext}"):
            if p.is_file() and "aa13b_r4" not in rel(p).lower():
                paths[rel(p)] = p
        for p in ROOT.glob(f"run/replay/**/{ext}"):
            if p.is_file() and "aa13b_r4" not in rel(p).lower():
                paths[rel(p)] = p

    profiles = [profile_file(p, refs.get(rel(p), [])) for p in paths.values()]
    profiles.sort(
        key=lambda x: (x["score"], x["rows"], x["recognized_family_rows"], len(x["proof_refs"])),
        reverse=True,
    )
    return profiles


def eligible_profiles(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for p in profiles:
        if p["is_rejected_artifact_class"]:
            continue
        if not p["exportable"]:
            continue
        if p["rows"] < 2400:
            continue
        if p["recognized_family_rows"] < 500:
            continue
        if len(p["recognized_family_set"]) < 3:
            continue
        out.append(p)
    return out


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = {str(k): ("" if v is None else str(v)) for k, v in row.items()}

    fam = normalize_family(first(out, FAMILY_KEYS))
    if fam:
        out["trade_family"] = fam

    side = first(out, SIDE_KEYS)
    if side and not out.get("side"):
        out["side"] = side

    selected_leg = first(out, SELECTED_LEG_KEYS)
    if selected_leg and not out.get("selected_leg"):
        out["selected_leg"] = selected_leg

    entry_mode = first(out, ENTRY_MODE_KEYS)
    if entry_mode and not out.get("entry_mode"):
        out["entry_mode"] = entry_mode

    return out


def export_normalized_csv(source: pathlib.Path) -> pathlib.Path:
    out_path = RUN_DIR / f"{source.stem}_aa13b_r4_input_normalized.csv"
    suffix = source.suffix.lower()
    rows: list[dict[str, Any]] = []
    field_order: list[str] = []

    def add_row(row: dict[str, Any]) -> None:
        nonlocal field_order
        n = normalize_row(row)
        for k in n:
            if k not in field_order:
                field_order.append(k)
        rows.append(n)

    if suffix == ".csv":
        with source.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                add_row(dict(row))

    elif suffix in [".jsonl", ".ndjson"]:
        with source.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if isinstance(obj, dict):
                    add_row(obj)

    elif suffix == ".parquet":
        import pandas as pd  # type: ignore
        df = pd.read_parquet(source)
        for _, row in df.iterrows():
            add_row({str(k): v for k, v in row.items()})
    else:
        raise RuntimeError(f"unsupported source suffix: {suffix}")

    for required in ["trade_family", "side", "selected_leg", "entry_mode"]:
        if required not in field_order:
            field_order.append(required)

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=field_order, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return out_path


def run_aa13b_derivation(input_csv: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, dict[str, Any]]:
    output_csv = RUN_DIR / f"{input_csv.stem}_economics_derived.csv"
    summary_json = RUN_DIR / "aa13b_r4_derivation_summary.json"

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
        timeout=180,
    )

    return output_csv, summary_json, json.loads(summary_json.read_text(encoding="utf-8"))


def validate_derived(output_csv: pathlib.Path | None, summary: dict[str, Any] | None) -> list[str]:
    blockers = []
    if output_csv is None or summary is None:
        return ["NO_DERIVATION_OUTPUT_CREATED"]

    rows = int(summary.get("rows_written", 0) or 0)
    fam_counts = summary.get("family_counts") or {}
    ready_counts = summary.get("ready_counts") or {}

    recognized = sum(v for k, v in fam_counts.items() if k in FAMILIES)
    ready_true = int(ready_counts.get("true", 0) or 0)
    ready_partial = int(ready_counts.get("partial", 0) or 0)

    if rows < 2400:
        blockers.append("DERIVED_ROWS_BELOW_TRUE_ROW_THRESHOLD")
    if recognized < 500:
        blockers.append("RECOGNIZED_FAMILY_ROWS_BELOW_TRUE_ROW_THRESHOLD")
    if len(set(fam_counts) & FAMILIES) < 3:
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
        blockers.append(f"DERIVED_OUTPUT_READ_FAILED:{exc!r}")

    return blockers


def previous_r3_eval() -> dict[str, Any]:
    obj = load_json(PREV_R3)
    if not obj:
        return {"present": False, "invalid_for_aa14": True, "reasons": ["missing_or_unreadable"]}

    reasons = []
    if obj.get("verdict") != "RAW_AA13B_R3_TRUE_ROW_ARTIFACT_RESOLVER_READY":
        reasons.append("previous_r3_not_ready")
    if obj.get("eligible_candidate_count", 0) <= 0:
        reasons.append("previous_r3_no_eligible_true_row_dataset")
    if not obj.get("derived_output_csv"):
        reasons.append("previous_r3_no_derived_output_csv")

    return {
        "present": True,
        "path": rel(PREV_R3),
        "verdict": obj.get("verdict"),
        "blockers": obj.get("blockers"),
        "selected_input_csv": obj.get("selected_input_csv"),
        "derived_output_csv": obj.get("derived_output_csv"),
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

    prev_eval = previous_r3_eval()
    profiles = discover_profiles()
    eligible = eligible_profiles(profiles)

    selected_profile = eligible[0] if eligible else None
    selected_path = abs_path(selected_profile["path"]) if selected_profile else None

    normalized_input = None
    derived_output = None
    summary_json = None
    summary = None
    source_sha_before = None
    source_sha_after = None

    if not blockers and selected_path is None:
        blockers.append("NO_EXISTING_TRUE_ROW_LEVEL_AA11_AA12_EXPORT_FOUND")
    elif not blockers and selected_path is not None:
        source_sha_before = sha_file(selected_path)
        normalized_input = export_normalized_csv(selected_path)
        source_sha_after = sha_file(selected_path)

        if source_sha_before != source_sha_after:
            blockers.append("SOURCE_ARTIFACT_MUTATED_UNEXPECTEDLY")

        derived_output, summary_json, summary = run_aa13b_derivation(normalized_input)
        blockers.extend(validate_derived(derived_output, summary))

    verdict = "RAW_AA13B_R4_EXPLICIT_OUTPUT_EXPORT_READY" if not blockers else "RAW_AA13B_R4_EXPLICIT_OUTPUT_EXPORT_DEFERRED"
    next_rec = "RAW_AA14_PNL_COST_MODEL_SOURCE_RESOLVER" if not blockers else "RAW_AA13B_R5_GENERATE_OR_UPLOAD_TRUE_ROW_LEVEL_AA11_AA12_EXPORT"

    missing_export_requirements = {
        "required_min_rows": 2400,
        "preferred_rows": "47919 enriched/backfilled rows or 2420 trade rows",
        "required_family_rows_min": 500,
        "required_family_diversity_min": 3,
        "required_family_column_or_aliases": FAMILY_KEYS,
        "required_fields_for_full_ready_rows": ["side", "selected_leg", "entry_mode"],
        "acceptable_extensions": [".csv", ".jsonl", ".ndjson", ".parquet"],
        "must_not_be": REJECT_NAME_TOKENS,
    }

    proof = {
        "batch": BATCH,
        "created_at_utc": NOW,
        "verdict": verdict,
        "blockers": blockers,
        "safety_flags": SAFETY,
        "backups": backups,
        "previous_r3_evaluation": prev_eval,
        "authority_map": rel(AUTHORITY_MAP),
        "aa13b_tool": rel(AA13B_TOOL),
        "resolver_tool": rel(TARGET_TOOL),
        "candidate_count": len(profiles),
        "eligible_candidate_count": len(eligible),
        "candidate_profiles_top_80": profiles[:80],
        "selected_profile": selected_profile,
        "selected_source_artifact": rel(selected_path),
        "selected_source_sha_before": source_sha_before,
        "selected_source_sha_after": source_sha_after,
        "normalized_input_csv": rel(normalized_input),
        "derived_output_csv": rel(derived_output),
        "derivation_summary_json": rel(summary_json),
        "derivation_summary": summary,
        "missing_export_requirements": missing_export_requirements,
        "field_resolution": {
            "target_ticks": "derived_from_authority_map_only_if_true_row_export_found",
            "stop_ticks": "derived_from_authority_map_only_if_true_row_export_found",
            "reward_ticks": "first_target_raw_economics_only",
            "reward_cost_ratio": "left_unavailable_until_cost_model",
            "entry_mode": "normalized_from_source_alias_or_mark_partial",
            "selected_leg": "normalized_from_source_alias_or_mark_partial",
            "side": "normalized_from_source_alias_or_mark_partial",
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
            "normalized_input_csv": rel(normalized_input),
            "derived_output_csv": rel(derived_output),
        },
        "next_recommendation": next_rec,
    }

    (RUN_DIR / "candidate_profiles.json").write_text(json.dumps(profiles, indent=2, sort_keys=True), encoding="utf-8")
    (RUN_DIR / "eligible_candidates.json").write_text(json.dumps(eligible, indent=2, sort_keys=True), encoding="utf-8")
    (RUN_DIR / "missing_export_requirements.json").write_text(json.dumps(missing_export_requirements, indent=2, sort_keys=True), encoding="utf-8")
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
        "previous_r3_invalid_for_aa14": prev_eval.get("invalid_for_aa14"),
        "selected_source_artifact": rel(selected_path),
        "normalized_input_csv": rel(normalized_input),
        "derived_output_csv": rel(derived_output),
        "source_artifact_mutated": bool(source_sha_before and source_sha_after and source_sha_before != source_sha_after),
        "no_replay": True,
        "no_broker_io": True,
        "no_live_redis_write": True,
        "no_order_sending": True,
        "no_paper_live_enablement": True,
        "next_recommendation": next_rec,
    }
    FREEZE_PATH.write_text(json.dumps(freeze, indent=2, sort_keys=True), encoding="utf-8")

    md = [
        "# RAW-AA13B-R4 Explicit Output Export Resolver",
        "",
        f"created_at_utc: {NOW}",
        f"verdict: `{verdict}`",
        f"blockers: `{blockers}`",
        f"next_recommendation: `{next_rec}`",
        "",
        "## Previous R3 correction",
        "",
        f"- previous_r3_invalid_for_aa14: `{prev_eval.get('invalid_for_aa14')}`",
        f"- reasons: `{prev_eval.get('reasons')}`",
        "",
        "## Selected artifact",
        "",
        f"- selected_source_artifact: `{rel(selected_path)}`",
        f"- normalized_input_csv: `{rel(normalized_input)}`",
        f"- derived_output_csv: `{rel(derived_output)}`",
        "",
        "## Missing export requirements if deferred",
        "",
        "```json",
        json.dumps(missing_export_requirements, indent=2, sort_keys=True),
        "```",
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
        "# Batch RAW-AA13B-R4 — Explicit Output Export Resolver",
        "",
        f"created_at_utc: {NOW}",
        f"verdict: `{verdict}`",
        f"blockers: `{blockers}`",
        f"next: `{next_rec}`",
        "",
        "Searches proof metadata and existing row-level artifacts; exports a RAW-normalized input only if true row-level AA11/AA12 evidence exists.",
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
        "previous_r3_invalid_for_aa14": prev_eval.get("invalid_for_aa14"),
        "candidate_count": len(profiles),
        "eligible_candidate_count": len(eligible),
        "selected_source_artifact": rel(selected_path),
        "normalized_input_csv": rel(normalized_input),
        "derived_output_csv": rel(derived_output),
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
