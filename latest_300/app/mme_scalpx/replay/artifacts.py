"""
app/mme_scalpx/replay/artifacts.py

Freeze-grade artifact persistence layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Artifact responsibilities
-------------------------
This module owns:
- canonical replay run directory creation
- stable JSON artifact writing
- stable CSV artifact writing
- manifest persistence
- persistence of dataset / selection / topology / engine summaries
- replay artifact existence helpers

This module does not own:
- replay execution
- dataset discovery/loading logic
- selection policy
- topology truth
- metric computation
- report interpretation
- doctrine logic
- live runtime mutation

Design rules
------------
- artifact persistence must be deterministic and auditable
- file writes must be explicit and path-safe
- JSON output must be stable and machine-readable first
- CSV output must have stable column ordering
- this layer must consume canonical contracts from runner/engine/selectors/topology
- no hidden directory creation outside the planned artifact root
"""

from __future__ import annotations

# RAW-S producer family emission hook — replay-only, non-live.
try:
    from app.mme_scalpx.replay.raw_producer_family_emission import emit_family_context as _raw_s_emit_family_context
except Exception:  # defensive replay-only fallback
    def _raw_s_emit_family_context(value, *, source_artifact=""):
        return value


def _raw_s_emit(value):
    source_artifact = __file__
    if isinstance(value, dict):
        source_artifact = str(
            value.get("source_artifact")
            or value.get("raw_source_artifact")
            or value.get("source_path")
            or value.get("artifact_path")
            or value.get("input_file")
            or value.get("input_path")
            or __file__
        )
    return _raw_s_emit_family_context(value, source_artifact=source_artifact)
# END RAW-S producer family emission hook.

# BEGIN BATCH27C_REPLAY_SAFETY_FIREWALL
try:
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety
except ModuleNotFoundError:
    import pathlib as _batch27c_pathlib
    import sys as _batch27c_sys

    _batch27c_here = _batch27c_pathlib.Path(__file__).resolve()
    for _batch27c_parent in [_batch27c_here.parent, *_batch27c_here.parents]:
        if (_batch27c_parent / "app" / "mme_scalpx").exists():
            if str(_batch27c_parent) not in _batch27c_sys.path:
                _batch27c_sys.path.insert(0, str(_batch27c_parent))
            break
    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety

assert_replay_module_static_safety(__file__)
# END BATCH27C_REPLAY_SAFETY_FIREWALL

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .contracts import manifest_to_dict
from .dataset import dataset_summary_to_dict
from .engine import engine_result_to_dict
from .runner import (
    ReplayArtifactPlan,
    ReplayRunContext,
    build_effective_inputs_snapshot,
    build_flattened_override_payload,
    effective_inputs_snapshot_to_dict,
    flattened_override_payload_to_dict,
)
from .selectors import ReplaySelectionPlan, selection_plan_to_dict
from .topology import ReplayTopologyPlan, topology_plan_to_dict


class ReplayArtifactsError(RuntimeError):
    """Base exception for replay artifact persistence failures."""


class ReplayArtifactsValidationError(ReplayArtifactsError):
    """Raised when artifact inputs or paths are invalid."""


@dataclass(frozen=True, slots=True)
class ReplayArtifactWriteResult:
    """
    Canonical result for one artifact write.
    """

    path: str
    bytes_written: int


@dataclass(frozen=True, slots=True)
class ReplayArtifactBundleResult:
    """
    Canonical result summary for a bundle write.
    """

    root_dir: str
    written_paths: tuple[str, ...]

    @property
    def artifact_count(self) -> int:
        return len(self.written_paths)


class ReplayArtifactsWriter:
    """
    Freeze-grade replay artifact writer.
    """

    def ensure_directories(self, artifact_plan: ReplayArtifactPlan) -> None:
        _validate_artifact_plan(artifact_plan)
        Path(artifact_plan.root_dir).mkdir(parents=True, exist_ok=True)
        Path(artifact_plan.log_dir).mkdir(parents=True, exist_ok=True)
        Path(artifact_plan.artifacts_dir).mkdir(parents=True, exist_ok=True)

    def write_json_artifact(
        self,
        path: str | Path,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        file_path = _normalize_file_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        text = _stable_json_dumps(payload) + "\n"
        file_path.write_text(text, encoding="utf-8")

        return ReplayArtifactWriteResult(
            path=str(file_path),
            bytes_written=len(text.encode("utf-8")),
        )

    def write_csv_artifact(
        self,
        path: str | Path,
        rows: Sequence[Mapping[str, Any]],
        *,
        fieldnames: Sequence[str] | None = None,
    ) -> ReplayArtifactWriteResult:
        file_path = _normalize_file_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        normalized_rows = [dict(row) for row in rows]
        resolved_fieldnames = tuple(
            fieldnames if fieldnames is not None else _derive_csv_fieldnames(normalized_rows)
        )

        with file_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=resolved_fieldnames,
                extrasaction="ignore",
            )
            writer.writeheader()
            for row in normalized_rows:
                writer.writerow(
                    {name: _csv_safe_value(row.get(name)) for name in resolved_fieldnames}
                )

        return ReplayArtifactWriteResult(
            path=str(file_path),
            bytes_written=file_path.stat().st_size,
        )

    def write_manifest(
        self,
        run_context: ReplayRunContext,
    ) -> ReplayArtifactWriteResult:
        payload = manifest_to_dict(run_context.manifest)
        return self.write_json_artifact(run_context.artifact_plan.manifest_path, payload)

    def write_dataset_summary(
        self,
        selection_plan: ReplaySelectionPlan,
        artifact_plan: ReplayArtifactPlan,
    ) -> ReplayArtifactWriteResult:
        payload = dataset_summary_to_dict(selection_plan.dataset_summary)
        return self.write_json_artifact(artifact_plan.dataset_summary_path, payload)

    def write_scope_profile(
        self,
        selection_plan: ReplaySelectionPlan,
        topology_plan: ReplayTopologyPlan,
        artifact_plan: ReplayArtifactPlan,
    ) -> ReplayArtifactWriteResult:
        payload = {
            "selection_plan": selection_plan_to_dict(selection_plan),
            "topology_plan": topology_plan_to_dict(topology_plan),
        }
        return self.write_json_artifact(artifact_plan.scope_profile_path, payload)

    def write_integrity_report_placeholder(
        self,
        artifact_plan: ReplayArtifactPlan,
        *,
        verdict: str | None = None,
        checks: Sequence[Mapping[str, Any]] = (),
        notes: Sequence[str] = (),
    ) -> ReplayArtifactWriteResult:
        payload = {
            "verdict": verdict,
            "checks": [dict(item) for item in checks],
            "notes": list(notes),
        }
        return self.write_json_artifact(artifact_plan.integrity_report_path, payload)

    def write_metrics_summary_placeholder(
        self,
        artifact_plan: ReplayArtifactPlan,
        *,
        metrics: Mapping[str, Any] = {},
        notes: Sequence[str] = (),
    ) -> ReplayArtifactWriteResult:
        payload = {
            "metrics": dict(metrics),
            "notes": list(notes),
        }
        return self.write_json_artifact(artifact_plan.metrics_summary_path, payload)

    def write_effective_inputs(
        self,
        run_context: ReplayRunContext,
    ) -> ReplayArtifactWriteResult:
        snapshot = build_effective_inputs_snapshot(run_context)
        payload = effective_inputs_snapshot_to_dict(snapshot)
        return self.write_json_artifact(
            run_context.artifact_plan.effective_inputs_path,
            payload,
        )

    def write_effective_overrides_flat(
        self,
        run_context: ReplayRunContext,
    ) -> ReplayArtifactWriteResult:
        payload = build_flattened_override_payload(run_context)
        return self.write_json_artifact(
            run_context.artifact_plan.effective_overrides_flat_path,
            flattened_override_payload_to_dict(payload),
        )

    def write_engine_result(
        self,
        engine_result,
        artifact_plan: ReplayArtifactPlan,
    ) -> ReplayArtifactWriteResult:
        payload = engine_result_to_dict(engine_result)
        engine_result_path = Path(artifact_plan.artifacts_dir) / "engine_result.json"
        return self.write_json_artifact(engine_result_path, payload)

    def write_trade_log_csv(
        self,
        artifact_plan: ReplayArtifactPlan,
        rows: Sequence[Mapping[str, Any]],
        *,
        fieldnames: Sequence[str] | None = None,
    ) -> ReplayArtifactWriteResult:
        return self.write_csv_artifact(
            artifact_plan.trade_log_path,
            rows,
            fieldnames=fieldnames,
        )

    def write_candidate_audit_csv(
        self,
        artifact_plan: ReplayArtifactPlan,
        rows: Sequence[Mapping[str, Any]],
        *,
        fieldnames: Sequence[str] | None = None,
    ) -> ReplayArtifactWriteResult:
        return self.write_csv_artifact(
            artifact_plan.candidate_audit_path,
            rows,
            fieldnames=fieldnames,
        )

    def write_blocker_breakdown(
        self,
        artifact_plan: ReplayArtifactPlan,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        return self.write_json_artifact(artifact_plan.blocker_breakdown_path, payload)

    def write_exit_breakdown(
        self,
        artifact_plan: ReplayArtifactPlan,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        return self.write_json_artifact(artifact_plan.exit_breakdown_path, payload)

    def write_differential_report(
        self,
        artifact_plan: ReplayArtifactPlan,
        payload: Mapping[str, Any],
    ) -> ReplayArtifactWriteResult:
        return self.write_json_artifact(artifact_plan.differential_report_path, payload)


    # --- B3_R32_REPLAY_ANALYSIS_EXPORTS_HELPERS_BEGIN ---
    def _b3_r32_parse_jsonish(self, value):
        if isinstance(value, str):
            text = value.strip()
            if text[:1] in ("{", "["):
                try:
                    import json
                    return json.loads(text)
                except Exception:
                    return value
        return value

    def _b3_r32_load_json_artifact(self, path):
        from pathlib import Path
        import json

        p = Path(path)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return None

    def _b3_r32_extract_largest_row_list(self, payload):
        if isinstance(payload, list):
            return payload
        best = []

        def walk(obj):
            nonlocal best
            if isinstance(obj, list):
                if len(obj) > len(best) and (not obj or isinstance(obj[0], dict)):
                    best = obj
                for item in obj[:20]:
                    walk(item)
            elif isinstance(obj, dict):
                for value in obj.values():
                    walk(value)

        walk(payload)
        return best

    def _b3_r32_flatten_row(self, row, prefix="", out=None, depth=0, max_depth=6, max_keys=800):
        if out is None:
            out = {}
        if depth > max_depth or len(out) >= max_keys:
            return out
        if isinstance(row, dict):
            for key, value in row.items():
                if len(out) >= max_keys:
                    break
                flat_key = f"{prefix}.{key}" if prefix else str(key)
                parsed = self._b3_r32_parse_jsonish(value)
                out[flat_key] = parsed
                if isinstance(parsed, dict):
                    self._b3_r32_flatten_row(parsed, flat_key, out, depth + 1, max_depth, max_keys)
                elif isinstance(parsed, list):
                    for index, item in enumerate(parsed[:5]):
                        self._b3_r32_flatten_row(item, f"{flat_key}[{index}]", out, depth + 1, max_depth, max_keys)
        return out

    def _b3_r32_first_present(self, flat, names):
        for name in names:
            if name in flat and flat[name] not in (None, ""):
                return flat[name]
            suffix = "." + name
            for key, value in flat.items():
                if key.endswith(suffix) and value not in (None, ""):
                    return value
        return None

    def _b3_r32_boolish(self, value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        return str(value).strip().lower() in {
            "1", "true", "yes", "y", "ok", "pass", "candidate", "entry", "buy", "sell"
        }

    def _b3_r32_str(self, value, default=""):
        if value is None:
            return default
        text = str(value)
        return text if text else default

    def _b3_r32_find_artifact_path(self, artifact_plan, filename):
        from pathlib import Path

        artifacts_dir = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", ".")))
        direct = artifacts_dir / filename
        if direct.exists():
            return direct

        root_dir = Path(getattr(artifact_plan, "root_dir", artifacts_dir))
        try:
            matches = sorted(root_dir.rglob(filename), key=lambda p: (p.stat().st_size, p.stat().st_mtime), reverse=True)
            if matches:
                return matches[0]
        except Exception:
            pass
        return direct

    def _b3_r32_write_candidate_audit_export(self, artifact_plan, strategy_rows):
        fieldnames = [
            "row_index",
            "event_time",
            "source_frame_id",
            "action",
            "candidate",
            "candidate_fallback",
            "selected_leg",
            "side",
            "linked_feature_side",
            "metadata_side",
            "blocker_name",
            "blocker_reason",
            "blocker_reason_fallback",
            "economics_reason",
            "reason",
        ]
        rows = []
        for index, row in enumerate(strategy_rows):
            flat = self._b3_r32_flatten_row(row)
            candidate = self._b3_r32_first_present(flat, ["candidate"])
            candidate_fallback = self._b3_r32_first_present(flat, ["candidate_fallback"])
            rows.append({
                "row_index": index,
                "event_time": self._b3_r32_str(self._b3_r32_first_present(flat, ["event_time", "timestamp", "ts"])),
                "source_frame_id": self._b3_r32_str(self._b3_r32_first_present(flat, ["source_frame_id", "metadata.source_frame_id"])),
                "action": self._b3_r32_str(self._b3_r32_first_present(flat, ["action", "activation_action", "decision_action", "strategy_action", "verdict", "status"])),
                "candidate": self._b3_r32_str(candidate, "False"),
                "candidate_fallback": self._b3_r32_str(candidate_fallback, "False"),
                "selected_leg": self._b3_r32_str(self._b3_r32_first_present(flat, ["selected_leg", "selected_leg_fallback"])),
                "side": self._b3_r32_str(self._b3_r32_first_present(flat, ["side", "side_fallback"])),
                "linked_feature_side": self._b3_r32_str(self._b3_r32_first_present(flat, ["linked_feature_side"])),
                "metadata_side": self._b3_r32_str(self._b3_r32_first_present(flat, ["metadata.side"])),
                "blocker_name": self._b3_r32_str(self._b3_r32_first_present(flat, ["blocker_name", "blocker"])),
                "blocker_reason": self._b3_r32_str(self._b3_r32_first_present(flat, ["blocker_reason"])),
                "blocker_reason_fallback": self._b3_r32_str(self._b3_r32_first_present(flat, ["blocker_reason_fallback"])),
                "economics_reason": self._b3_r32_str(self._b3_r32_first_present(flat, ["economics_reason"])),
                "reason": self._b3_r32_str(self._b3_r32_first_present(flat, ["reason", "decision_reason", "activation_reason"])),
            })
        candidate_path = getattr(artifact_plan, "candidate_audit_path", None)
        if candidate_path is None:
            from pathlib import Path
            candidate_path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "candidate_audit.csv"
        self.write_csv_artifact(candidate_path, rows, fieldnames=fieldnames)
        return rows

    def _b3_r32_write_blocker_distribution_export(self, artifact_plan, candidate_rows):
        from collections import Counter
        from pathlib import Path

        fieldnames = [
            "blocker_key",
            "blocker_name",
            "blocker_reason",
            "blocker_reason_fallback",
            "economics_reason",
            "reason",
            "side",
            "selected_leg",
            "count",
        ]

        counts = Counter()
        for row in candidate_rows:
            blocker_name = row.get("blocker_name", "")
            blocker_reason = row.get("blocker_reason", "")
            blocker_reason_fallback = row.get("blocker_reason_fallback", "")
            economics_reason = row.get("economics_reason", "")
            reason = row.get("reason", "")
            side = row.get("side") or row.get("linked_feature_side") or row.get("metadata_side") or ""
            selected_leg = row.get("selected_leg", "")
            blocker_key = "|".join([
                blocker_name,
                blocker_reason,
                blocker_reason_fallback,
                economics_reason,
                reason,
                side,
                selected_leg,
            ])
            counts[(blocker_key, blocker_name, blocker_reason, blocker_reason_fallback, economics_reason, reason, side, selected_leg)] += 1

        rows = [
            {
                "blocker_key": key[0],
                "blocker_name": key[1],
                "blocker_reason": key[2],
                "blocker_reason_fallback": key[3],
                "economics_reason": key[4],
                "reason": key[5],
                "side": key[6],
                "selected_leg": key[7],
                "count": count,
            }
            for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

        path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "blocker_distribution.csv"
        self.write_csv_artifact(path, rows, fieldnames=fieldnames)
        return rows


    # --- B3_R43_ECONOMICS_SUMMARY_ENRICHMENT_HELPERS_BEGIN ---
    def _b3_r43_extract_numeric_param_authority(self):
        """Best-effort source-labelled parameter scan for export metadata only.

        This is offline/export enrichment only. It must not change strategy,
        replay decisions, broker/order behavior, paper/live behavior, risk,
        or execution.
        """
        from pathlib import Path
        import re

        root = Path.cwd()
        search_roots = [
            root / "app" / "mme_scalpx",
            root / "etc",
            root / "docs" / "contracts",
        ]
        term_map = {
            "tick_size": ["tick_size", "TICK_SIZE"],
            "target_points": ["TARGET_POINTS", "target_points", "profit_target"],
            "stop_points": ["HARD_STOP_POINTS", "STOP_POINTS", "hard_stop_points", "stop_points", "hard_stop"],
        }

        found = {key: [] for key in term_map}
        assignment_re = re.compile(r"(?P<name>[A-Za-z_][A-Za-z0-9_\.]*)\s*(?::[^=]+)?=\s*(?P<value>-?\d+(?:\.\d+)?)")

        for base in search_roots:
            if not base.exists():
                continue
            for path in list(base.rglob("*.py")) + list(base.rglob("*.json")) + list(base.rglob("*.yaml")) + list(base.rglob("*.yml")) + list(base.rglob("*.md")):
                parts = set(path.parts)
                if "__pycache__" in parts or ".venv" in parts or ".git" in parts:
                    continue
                try:
                    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
                except Exception:
                    continue
                for line_no, line in enumerate(lines, 1):
                    low = line.lower()
                    for field, terms in term_map.items():
                        if not any(term.lower() in low for term in terms):
                            continue
                        m = assignment_re.search(line)
                        if not m:
                            continue
                        try:
                            value = float(m.group("value"))
                        except Exception:
                            continue
                        try:
                            rel_path = str(path.relative_to(root))
                        except Exception:
                            rel_path = str(path)
                        found[field].append({
                            "value": value,
                            "path": rel_path,
                            "line": line_no,
                            "text": line.strip()[:240],
                        })

        # B3_R46_ECONOMICS_AUTHORITY_FILTER_BEGIN
        # Pick the best non-zero economics authority candidate while preserving
        # candidates for auditability. Reject model/schema defaults and validators.
        bad_path_parts = (
            "app/mme_scalpx/core/models.py",
        )
        bad_text_parts = (
            "_require_float",
            "min_value=0.0",
            "float = 0.0",
            "default=0.0",
        )
        preferred_path_parts = (
            "app/mme_scalpx/services/strategy_family/",
            "etc/research_gate/raw_doctrine_economics_authority_map.json",
            "docs/contracts/",
        )

        def is_bad_candidate(candidate):
            if not candidate:
                return True
            path_text = str(candidate.get("path", ""))
            line_text = str(candidate.get("text", ""))
            value = candidate.get("value")
            try:
                numeric_value = float(value)
            except Exception:
                return True
            if numeric_value == 0.0:
                return True
            if any(part in path_text for part in bad_path_parts):
                return True
            if any(part in line_text for part in bad_text_parts):
                return True
            return False

        def candidate_score(field, candidate):
            if is_bad_candidate(candidate):
                return -1000000
            path_text = str(candidate.get("path", ""))
            line_text = str(candidate.get("text", ""))
            score = 100

            if any(part in path_text for part in preferred_path_parts):
                score += 50
            if "strategy_family" in path_text:
                score += 30
            if field == "tick_size" and "DEFAULT_TICK_SIZE" in line_text:
                score += 25
            if field == "target_points" and "TARGET_POINTS" in line_text:
                score += 25
            if field == "stop_points" and "HARD_STOP_POINTS" in line_text:
                score += 25
            if "miso_surface.py" in path_text:
                score -= 5
            if "features.py" in path_text:
                score -= 10
            return score

        selected = {}
        rejected = {}
        for field, candidates in found.items():
            ranked = sorted(candidates, key=lambda item: candidate_score(field, item), reverse=True)
            selected[field] = ranked[0] if ranked and not is_bad_candidate(ranked[0]) else None
            rejected[field] = [
                item for item in candidates
                if is_bad_candidate(item)
            ][:20]

        return {
            "selected": selected,
            "candidates": {key: value[:20] for key, value in found.items()},
            "rejected_candidates": rejected,
            "authority_filter_schema_version": "b3_r46_authority_filter_v1",
            "authority_filter_rules": [
                "reject numeric zero for tick_size/target_points/stop_points",
                "reject app/mme_scalpx/core/models.py schema defaults and validators",
                "reject _require_float/min_value=0.0/default=0.0 lines",
                "prefer explicit non-zero strategy_family constants/config doctrine authority",
            ],
        }
        # B3_R46_ECONOMICS_AUTHORITY_FILTER_END

    def _b3_r43_build_economics_enrichment_payload(self, strategy_rows, features_rows, presence, values, missing):
        from collections import Counter

        all_rows = list(strategy_rows) + list(features_rows)
        action_counts = Counter()
        candidate_true_count = 0

        for row in strategy_rows:
            flat = self._b3_r32_flatten_row(row)
            action = self._b3_r32_first_present(flat, ["action", "activation_action", "decision_action", "strategy_action", "verdict", "status"])
            action_counts[str(action or "UNKNOWN")] += 1
            candidate = self._b3_r32_first_present(flat, ["candidate", "candidate_fallback", "candidate_found", "candidate_ok", "entry_candidate"])
            if self._b3_r32_boolish(candidate):
                candidate_true_count += 1

        authority = self._b3_r43_extract_numeric_param_authority()
        selected = authority.get("selected", {})

        target_points = (selected.get("target_points") or {}).get("value")
        stop_points = (selected.get("stop_points") or {}).get("value")
        tick_size = (selected.get("tick_size") or {}).get("value")

        enriched_values = {}
        enrichment_sources = {}

        hold_only = bool(strategy_rows) and set(action_counts.keys()) <= {"HOLD"} and candidate_true_count == 0
        if hold_only:
            enriched_values["entry_mode"] = "NO_ENTRY_HOLD_ONLY"
            enrichment_sources["entry_mode"] = {
                "source_type": "replay_export_derived",
                "basis": "all strategy actions HOLD and candidate_true_count == 0",
                "not_trade_entry_proof": True,
            }

        if tick_size is not None:
            enriched_values["tick_size"] = tick_size
            enrichment_sources["tick_size"] = {
                "source_type": "source_assignment_candidate",
                **(selected.get("tick_size") or {}),
            }

        if target_points is not None:
            enriched_values["target_points"] = target_points
            enriched_values["reward_points"] = target_points
            enrichment_sources["target_points"] = {
                "source_type": "source_assignment_candidate",
                **(selected.get("target_points") or {}),
            }
            enrichment_sources["reward_points"] = {
                "source_type": "derived_same_as_target_points",
                "basis": "reward for first target equals target_points in export summary",
            }

        if stop_points is not None:
            enriched_values["stop_points"] = stop_points
            enrichment_sources["stop_points"] = {
                "source_type": "source_assignment_candidate",
                **(selected.get("stop_points") or {}),
            }

        if target_points is not None and stop_points not in (None, 0):
            enriched_values["reward_cost_ratio"] = round(float(target_points) / float(stop_points), 6)
            enrichment_sources["reward_cost_ratio"] = {
                "source_type": "derived_from_same_unit_basis",
                "formula": "target_points / stop_points",
                "target_points": target_points,
                "stop_points": stop_points,
            }

        if tick_size not in (None, 0) and target_points is not None:
            enriched_values["target_ticks"] = round(float(target_points) / float(tick_size), 6)
            enriched_values["reward_ticks"] = enriched_values["target_ticks"]
            enrichment_sources["target_ticks"] = {
                "source_type": "derived_from_points_and_tick_size",
                "formula": "target_points / tick_size",
                "target_points": target_points,
                "tick_size": tick_size,
            }
            enrichment_sources["reward_ticks"] = {
                "source_type": "derived_same_as_target_ticks",
                "basis": "reward for first target equals target_ticks in export summary",
            }

        if tick_size not in (None, 0) and stop_points is not None:
            enriched_values["stop_ticks"] = round(float(stop_points) / float(tick_size), 6)
            enrichment_sources["stop_ticks"] = {
                "source_type": "derived_from_points_and_tick_size",
                "formula": "stop_points / tick_size",
                "stop_points": stop_points,
                "tick_size": tick_size,
            }

        fields_left_missing = [field for field in missing if field not in enriched_values]

        return {
            "enrichment_schema_version": "b3_r43_economics_export_enrichment_v1",
            "enrichment_status": "enriched_source_labelled" if enriched_values else "no_enrichment_values_available",
            "enriched_field_values": enriched_values,
            "enrichment_sources": enrichment_sources,
            "unit_basis": {
                "target_points": "points",
                "stop_points": "points",
                "reward_points": "points",
                "target_ticks": "derived_ticks_if_tick_size_available",
                "stop_ticks": "derived_ticks_if_tick_size_available",
                "reward_ticks": "derived_ticks_if_tick_size_available",
            },
            "fields_left_missing": fields_left_missing,
            "authority_candidates": authority.get("candidates", {}),
            "governance_notes": [
                "Export-only enrichment; does not change strategy decisions.",
                "Values are source-labelled and must not be treated as trade/PnL proof.",
                "entry_mode=NO_ENTRY_HOLD_ONLY is only an export label when all rows are HOLD and candidate_true_count is zero.",
                "Do not claim paper/live, broker/order, risk/execution, or profitability readiness from this enrichment.",
            ],
        }
    # --- B3_R43_ECONOMICS_SUMMARY_ENRICHMENT_HELPERS_END ---

    def _b3_r32_write_economics_summary_export(self, artifact_plan, strategy_rows, features_rows):
        from collections import Counter
        from pathlib import Path

        fields = [
            "source_frame_id",
            "selected_leg",
            "entry_mode",
            "tick_size",
            "target_ticks",
            "stop_ticks",
            "reward_ticks",
            "reward_cost_ratio",
            "economics_reason",
        ]

        presence = Counter()
        values = {field: Counter() for field in fields}

        for row in list(strategy_rows) + list(features_rows):
            flat = self._b3_r32_flatten_row(row)
            for field in fields:
                value = self._b3_r32_first_present(flat, [field, f"metadata.{field}"])
                if value not in (None, ""):
                    presence[field] += 1
                    values[field][str(value)[:180]] += 1

        missing = [field for field in fields if presence.get(field, 0) == 0]

        # B3_R43_ECONOMICS_SUMMARY_ENRICHMENT_PAYLOAD_VAR_BEGIN
        enrichment = self._b3_r43_build_economics_enrichment_payload(strategy_rows, features_rows, presence, values, missing)
        # B3_R43_ECONOMICS_SUMMARY_ENRICHMENT_PAYLOAD_VAR_END
        payload = {
            "schema_version": "b3_r32_economics_summary_v1",
            # B3_R43_ECONOMICS_SUMMARY_ENRICHMENT_PAYLOAD_FIELDS_BEGIN
            "enrichment_schema_version": enrichment.get("enrichment_schema_version"),
            "enrichment_status": enrichment.get("enrichment_status"),
            "enriched_field_values": enrichment.get("enriched_field_values", {}),
            "enrichment_sources": enrichment.get("enrichment_sources", {}),
            "unit_basis": enrichment.get("unit_basis", {}),
            "fields_left_missing": enrichment.get("fields_left_missing", []),
            "authority_candidates": enrichment.get("authority_candidates", {}),
            "governance_notes": enrichment.get("governance_notes", []),
            # B3_R43_ECONOMICS_SUMMARY_ENRICHMENT_PAYLOAD_FIELDS_END
            "row_count": {
                "strategy_decisions": len(strategy_rows),
                "features_rows": len(features_rows),
            },
            "field_presence": dict(presence),
            "economics_reason_counts": dict(values["economics_reason"].most_common(100)),
            "selected_leg_counts": dict(values["selected_leg"].most_common(100)),
            "value_counts": {
                field: dict(counter.most_common(100))
                for field, counter in values.items()
                if counter
            },
            "missing_economics_fields": missing,
            "note": "This is economics field completeness only; it is not PnL or trade profitability.",
        }

        path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "economics_summary.json"
        self.write_json_artifact(path, payload)
        return payload

    def _b3_r32_write_family_side_summary_export(self, artifact_plan, strategy_rows):
        from collections import Counter
        from pathlib import Path

        fieldnames = [
            "family",
            "side",
            "linked_feature_side",
            "metadata_side",
            "selected_leg",
            "count",
            "decode_quality",
        ]
        counts = Counter()

        for row in strategy_rows:
            flat = self._b3_r32_flatten_row(row)
            family = self._b3_r32_first_present(flat, ["family", "strategy_family", "strategy_family_id", "strategy_id", "strategy", "strategy_name"])
            side = self._b3_r32_first_present(flat, ["side", "side_fallback", "branch", "option_side"])
            linked_feature_side = self._b3_r32_first_present(flat, ["linked_feature_side"])
            metadata_side = self._b3_r32_first_present(flat, ["metadata.side"])
            selected_leg = self._b3_r32_first_present(flat, ["selected_leg", "selected_leg_fallback"])

            family_text = self._b3_r32_str(family, "UNKNOWN")
            side_text = self._b3_r32_str(side, "UNKNOWN")
            linked_text = self._b3_r32_str(linked_feature_side, "")
            metadata_text = self._b3_r32_str(metadata_side, "")
            leg_text = self._b3_r32_str(selected_leg, "")
            decode_quality = "weak" if family_text == "UNKNOWN" else "ok"

            counts[(family_text, side_text, linked_text, metadata_text, leg_text, decode_quality)] += 1

        rows = [
            {
                "family": key[0],
                "side": key[1],
                "linked_feature_side": key[2],
                "metadata_side": key[3],
                "selected_leg": key[4],
                "count": count,
                "decode_quality": key[5],
            }
            for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

        path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "family_side_summary.csv"
        self.write_csv_artifact(path, rows, fieldnames=fieldnames)
        return rows


    # --- B3_R53_DATE_RANGE_AGGREGATE_EXPORT_HELPER_BEGIN ---
    def write_b3_r52_date_range_aggregate_exports(self, *, run_dirs, output_dir, dataset_root=None, selection_dates=None, label=None):
        """Write date-range aggregate exports from already-completed replay run dirs.

        Export-only helper. It reads existing per-run artifacts and writes combined
        reports. It does not run replay, mutate strategy decisions, use Redis, call
        broker/order paths, or touch paper/live/risk/execution.
        """
        import csv
        import json
        from collections import Counter
        from datetime import datetime, timezone
        from pathlib import Path

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        def _as_path(value):
            return Path(value).resolve()

        def _find_artifacts_dir(run_dir):
            root = _as_path(run_dir)
            candidates = []
            if (root / "artifacts").is_dir():
                candidates.append(root / "artifacts")
            if root.is_dir():
                for p in root.rglob("economics_summary.json"):
                    if p.parent.is_dir():
                        candidates.append(p.parent)
            unique = []
            seen = set()
            for c in candidates:
                key = str(c)
                if key not in seen:
                    seen.add(key)
                    unique.append(c)
            return unique[0] if unique else root

        def _load_json(path):
            try:
                return json.loads(Path(path).read_text(encoding="utf-8", errors="replace"))
            except Exception as exc:
                return {"_load_error": repr(exc), "_path": str(path)}

        def _read_csv(path):
            p = Path(path)
            if not p.exists():
                return []
            with p.open("r", encoding="utf-8", errors="replace", newline="") as f:
                return [dict(row) for row in csv.DictReader(f)]

        # B3_R56_AGGREGATE_HELPER_FILE_DISCOVERY_FIX_HELPERS_BEGIN
        def _csv_row_count(path):
            p = Path(path)
            if not p.exists() or p.suffix.lower() != ".csv":
                return 0
            try:
                with p.open("r", encoding="utf-8", errors="replace", newline="") as f:
                    return max(sum(1 for _ in f) - 1, 0)
            except Exception:
                return 0

        def _first_existing(paths):
            for item in paths:
                p = Path(item)
                if p.exists():
                    return p
            return Path(paths[0]) if paths else Path("")

        def _best_csv_by_rows(paths):
            candidates = []
            for item in paths:
                p = Path(item)
                if p.exists():
                    candidates.append((_csv_row_count(p), p.stat().st_size, p))
            if not candidates:
                return Path(paths[0]) if paths else Path("")
            candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
            return candidates[0][2]

        def _find_candidate_audit_file(run_dir, artifacts_dir):
            root = Path(run_dir)
            artifacts = Path(artifacts_dir)
            paths = [
                root / "06_candidate_audit.csv",
                root / "candidate_audit.csv",
                artifacts / "06_candidate_audit.csv",
                artifacts / "candidate_audit.csv",
            ]
            paths.extend(sorted(root.rglob("*candidate*audit*.csv")))
            paths.extend(sorted(root.rglob("*candidate*.csv")))
            return _best_csv_by_rows(paths)

        def _find_named_file(run_dir, artifacts_dir, filename):
            root = Path(run_dir)
            artifacts = Path(artifacts_dir)
            paths = [
                artifacts / filename,
                root / filename,
            ]
            paths.extend(sorted(root.rglob(filename)))
            return _first_existing(paths)
        # B3_R56_AGGREGATE_HELPER_FILE_DISCOVERY_FIX_HELPERS_END

        def _write_csv(path, rows, preferred_fields=None):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            rows = list(rows)
            fields = []
            if preferred_fields:
                for f in preferred_fields:
                    if f not in fields:
                        fields.append(f)
            for row in rows:
                for key in row.keys():
                    if key not in fields:
                        fields.append(key)
            with p.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for row in rows:
                    writer.writerow({field: row.get(field, "") for field in fields})
            return {"path": str(p), "rows": len(rows), "columns": fields}

        def _write_json(path, payload):
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
            return {"path": str(p)}

        def _source_date_from_run(run_dir, manifest_payload):
            if isinstance(manifest_payload, dict):
                selection = manifest_payload.get("selection") or {}
                dates = selection.get("trading_dates") or selection.get("selected_days") or selection.get("dates") or []
                if isinstance(dates, list) and dates:
                    return str(dates[0])
                if isinstance(dates, tuple) and dates:
                    return str(dates[0])
                for key in ("single_day", "session_date", "trading_day"):
                    if selection.get(key):
                        return str(selection.get(key))
            text = str(run_dir)
            import re
            m = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
            return m.group(1) if m else "UNKNOWN"

        run_dirs = [Path(p) for p in run_dirs]
        per_day_rows = []
        combined_candidate_rows = []
        combined_blocker_rows = []
        combined_family_side_rows = []
        economics_per_day = []

        econ_reason_counts = Counter()
        selected_leg_counts = Counter()
        enrichment_versions = Counter()
        fields_left_missing_by_day = {}

        for run_dir in run_dirs:
            artifacts_dir = _find_artifacts_dir(run_dir)
            manifest = _load_json(Path(run_dir) / "00_manifest.json")
            integrity = _load_json(Path(run_dir) / "03_integrity_report.json")
            source_date = _source_date_from_run(run_dir, manifest)

            # B3_R56_AGGREGATE_HELPER_FILE_DISCOVERY_FIX_FILE_SELECTION_BEGIN
            candidate_path = _find_candidate_audit_file(run_dir, artifacts_dir)
            blocker_path = _find_named_file(run_dir, artifacts_dir, "blocker_distribution.csv")
            family_side_path = _find_named_file(run_dir, artifacts_dir, "family_side_summary.csv")
            economics_path = _find_named_file(run_dir, artifacts_dir, "economics_summary.json")
            # B3_R56_AGGREGATE_HELPER_FILE_DISCOVERY_FIX_FILE_SELECTION_END

            candidate_rows = _read_csv(candidate_path)
            blocker_rows = _read_csv(blocker_path)
            family_side_rows = _read_csv(family_side_path)
            economics = _load_json(economics_path) if economics_path.exists() else {}

            for row in candidate_rows:
                enriched = {"source_date": source_date, "source_run_dir": str(run_dir), **row}
                combined_candidate_rows.append(enriched)

            for row in blocker_rows:
                enriched = {"source_date": source_date, "source_run_dir": str(run_dir), **row}
                combined_blocker_rows.append(enriched)

            for row in family_side_rows:
                enriched = {"source_date": source_date, "source_run_dir": str(run_dir), **row}
                combined_family_side_rows.append(enriched)

            if isinstance(economics, dict):
                for key, value in (economics.get("economics_reason_counts") or {}).items():
                    try:
                        econ_reason_counts[str(key)] += int(value)
                    except Exception:
                        pass
                for key, value in (economics.get("selected_leg_counts") or {}).items():
                    try:
                        selected_leg_counts[str(key)] += int(value)
                    except Exception:
                        pass
                if economics.get("enrichment_schema_version"):
                    enrichment_versions[str(economics.get("enrichment_schema_version"))] += 1
                fields_left_missing_by_day[source_date] = economics.get("fields_left_missing", economics.get("missing_economics_fields", []))

            integrity_verdict = ""
            if isinstance(integrity, dict):
                integrity_verdict = integrity.get("verdict") or integrity.get("integrity_verdict") or integrity.get("overall_verdict") or ""

            per_day_rows.append({
                "source_date": source_date,
                "source_run_dir": str(run_dir),
                "artifacts_dir": str(artifacts_dir),
                "integrity_verdict": integrity_verdict,
                "candidate_rows": len(candidate_rows),
                "blocker_rows": len(blocker_rows),
                "family_side_rows": len(family_side_rows),
                "economics_summary_present": bool(isinstance(economics, dict) and economics),
            })

            economics_per_day.append({
                "source_date": source_date,
                "source_run_dir": str(run_dir),
                "economics_summary_path": str(economics_path),
                "economics_summary": economics,
            })

        manifest_payload = {
            "schema_version": "b3_r53_date_range_aggregate_manifest_v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "label": label or "",
            "dataset_root": str(dataset_root or ""),
            "selection_dates": list(selection_dates or []),
            "run_dirs": [str(p) for p in run_dirs],
            "output_dir": str(out_dir),
            "per_day_count": len(per_day_rows),
            "combined_candidate_rows": len(combined_candidate_rows),
            "combined_blocker_rows": len(combined_blocker_rows),
            "combined_family_side_rows": len(combined_family_side_rows),
            "governance": [
                "Aggregate export helper only.",
                "Reads completed replay artifacts; does not run replay.",
                "No Redis, broker/order, paper/live, risk/execution side effects.",
                "Does not mutate strategy decisions or feature rows.",
            ],
        }

        combined_economics = {
            "schema_version": "b3_r53_combined_economics_summary_v1",
            "per_day": economics_per_day,
            "combined_row_count": sum(int(r.get("candidate_rows") or 0) for r in per_day_rows),
            "combined_economics_reason_counts": dict(econ_reason_counts),
            "combined_selected_leg_counts": dict(selected_leg_counts),
            "enrichment_schema_versions": dict(enrichment_versions),
            "fields_left_missing_by_day": fields_left_missing_by_day,
        }

        outputs = {
            "date_range_manifest": _write_json(out_dir / "date_range_manifest.json", manifest_payload),
            "per_day_summary": _write_csv(
                out_dir / "per_day_summary.csv",
                per_day_rows,
                ["source_date", "source_run_dir", "artifacts_dir", "integrity_verdict", "candidate_rows", "blocker_rows", "family_side_rows", "economics_summary_present"],
            ),
            "combined_candidate_audit": _write_csv(
                out_dir / "combined_candidate_audit.csv",
                combined_candidate_rows,
                ["source_date", "source_run_dir"],
            ),
            "combined_blocker_distribution": _write_csv(
                out_dir / "combined_blocker_distribution.csv",
                combined_blocker_rows,
                ["source_date", "source_run_dir", "blocker_key", "blocker_name", "blocker_reason", "side", "selected_leg", "count"],
            ),
            "combined_family_side_summary": _write_csv(
                out_dir / "combined_family_side_summary.csv",
                combined_family_side_rows,
                ["source_date", "source_run_dir", "family", "side", "linked_feature_side", "metadata_side", "selected_leg", "decode_quality", "count"],
            ),
            "combined_economics_summary": _write_json(out_dir / "combined_economics_summary.json", combined_economics),
        }

        return {
            "schema_version": "b3_r53_date_range_aggregate_exports_status_v1",
            "status": "ok",
            "output_dir": str(out_dir),
            "outputs": outputs,
            "per_day_rows": len(per_day_rows),
            "combined_candidate_rows": len(combined_candidate_rows),
            "combined_blocker_rows": len(combined_blocker_rows),
            "combined_family_side_rows": len(combined_family_side_rows),
            "combined_economics_row_count": combined_economics["combined_row_count"],
        }
    # --- B3_R53_DATE_RANGE_AGGREGATE_EXPORT_HELPER_END ---

    def write_b3_r32_analysis_exports(self, run_context_or_artifact_plan):
        """B3_R32_REPLAY_ANALYSIS_EXPORTS_HELPERS: write replay analysis exports.

        Offline artifact-export only. This does not change strategy decisions,
        broker/order behavior, paper/live behavior, risk, or execution.
        """
        from pathlib import Path

        artifact_plan = getattr(run_context_or_artifact_plan, "artifact_plan", run_context_or_artifact_plan)
        artifacts_dir = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", ".")))
        error_path = artifacts_dir / "b3_r32_analysis_export_error.json"

        try:
            strategy_path = self._b3_r32_find_artifact_path(artifact_plan, "strategy_decisions.json")
            features_path = self._b3_r32_find_artifact_path(artifact_plan, "features_rows.json")

            strategy_payload = self._b3_r32_load_json_artifact(strategy_path)
            features_payload = self._b3_r32_load_json_artifact(features_path)

            strategy_rows = self._b3_r32_extract_largest_row_list(strategy_payload)
            features_rows = self._b3_r32_extract_largest_row_list(features_payload)

            candidate_rows = self._b3_r32_write_candidate_audit_export(artifact_plan, strategy_rows)
            blocker_rows = self._b3_r32_write_blocker_distribution_export(artifact_plan, candidate_rows)
            economics_payload = self._b3_r32_write_economics_summary_export(artifact_plan, strategy_rows, features_rows)
            family_side_rows = self._b3_r32_write_family_side_summary_export(artifact_plan, strategy_rows)

            status_path = artifacts_dir / "b3_r32_analysis_exports_status.json"
            self.write_json_artifact(status_path, {
                "schema_version": "b3_r32_analysis_exports_status_v1",
                "status": "ok",
                "strategy_decisions_path": str(strategy_path),
                "features_rows_path": str(features_path),
                "strategy_rows": len(strategy_rows),
                "features_rows": len(features_rows),
                "candidate_audit_rows": len(candidate_rows),
                "blocker_distribution_rows": len(blocker_rows),
                "family_side_summary_rows": len(family_side_rows),
                "economics_missing_fields": economics_payload.get("missing_economics_fields", []),
            })
        except Exception as exc:
            try:
                self.write_json_artifact(error_path, {
                    "schema_version": "b3_r32_analysis_exports_error_v1",
                    "status": "error",
                    "error": repr(exc),
                    "note": "Optional B3_R32 analysis export failed; core replay artifacts are unchanged.",
                })
            except Exception:
                pass
    # --- B3_R32_REPLAY_ANALYSIS_EXPORTS_HELPERS_END ---

    def write_core_artifact_bundle(
        self,
        run_context: ReplayRunContext,
        topology_plan: ReplayTopologyPlan,
        *,
        integrity_verdict: str | None = None,
        integrity_checks: Sequence[Mapping[str, Any]] = (),
        integrity_notes: Sequence[str] = (),
        metrics: Mapping[str, Any] = {},
        metrics_notes: Sequence[str] = (),
    ) -> ReplayArtifactBundleResult:
        artifact_plan = run_context.artifact_plan
        self.ensure_directories(artifact_plan)

        written: list[str] = []

        written.append(self.write_manifest(run_context).path)
        written.append(
            self.write_dataset_summary(run_context.selection_plan, artifact_plan).path
        )
        written.append(
            self.write_scope_profile(
                run_context.selection_plan,
                topology_plan,
                artifact_plan,
            ).path
        )
        written.append(
            self.write_integrity_report_placeholder(
                artifact_plan,
                verdict=integrity_verdict,
                checks=integrity_checks,
                notes=integrity_notes,
            ).path
        )
        written.append(
            self.write_metrics_summary_placeholder(
                artifact_plan,
                metrics=metrics,
                notes=metrics_notes,
            ).path
        )
        written.append(self.write_effective_inputs(run_context).path)
        written.append(self.write_effective_overrides_flat(run_context).path)

        # B3_R32_REPLAY_ANALYSIS_EXPORTS_CALL_BEGIN
        self.write_b3_r32_analysis_exports(run_context)
        # B3_R32_REPLAY_ANALYSIS_EXPORTS_CALL_END
        return ReplayArtifactBundleResult(
            root_dir=artifact_plan.root_dir,
            written_paths=tuple(written),
        )


def ensure_artifact_directories(artifact_plan: ReplayArtifactPlan) -> None:
    writer = ReplayArtifactsWriter()
    writer.ensure_directories(artifact_plan)


def artifact_exists(path: str | Path) -> bool:
    return _normalize_file_path(path).exists()


def read_json_artifact(path: str | Path) -> dict[str, Any]:
    file_path = _normalize_file_path(path)
    if not file_path.exists():
        raise ReplayArtifactsValidationError(f"artifact not found: {file_path}")
    if not file_path.is_file():
        raise ReplayArtifactsValidationError(f"artifact path is not a file: {file_path}")

    try:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReplayArtifactsValidationError(
            f"artifact is not valid JSON: {file_path}"
        ) from exc

    if not isinstance(payload, dict):
        raise ReplayArtifactsValidationError(
            f"JSON artifact must decode to object: {file_path}"
        )

    return _raw_s_emit(payload)
def _validate_artifact_plan(artifact_plan: ReplayArtifactPlan) -> None:
    required = (
        artifact_plan.root_dir,
        artifact_plan.manifest_path,
        artifact_plan.log_dir,
        artifact_plan.artifacts_dir,
        artifact_plan.dataset_summary_path,
        artifact_plan.scope_profile_path,
        artifact_plan.integrity_report_path,
        artifact_plan.metrics_summary_path,
        artifact_plan.effective_inputs_path,
        artifact_plan.effective_overrides_flat_path,
    )
    for value in required:
        if not isinstance(value, str) or not value.strip():
            raise ReplayArtifactsValidationError(
                f"artifact plan contains invalid path value: {value!r}"
            )


def _normalize_file_path(path: str | Path) -> Path:
    file_path = Path(path).expanduser()
    if not file_path.name:
        raise ReplayArtifactsValidationError(f"invalid file path: {path!r}")
    return file_path


def _stable_json_dumps(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    )


def _derive_csv_fieldnames(rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    if not rows:
        return tuple()
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row.keys():
            key_str = str(key)
            if key_str not in seen:
                seen.add(key_str)
                keys.append(key_str)
    return tuple(keys)


def _csv_safe_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


__all__ = [
    "ReplayArtifactsError",
    "ReplayArtifactsValidationError",
    "ReplayArtifactWriteResult",
    "ReplayArtifactBundleResult",
    "ReplayArtifactsWriter",
    "ensure_artifact_directories",
    "artifact_exists",
    "read_json_artifact",
]

# ===== BATCH16_REPLAY_PACKAGE_FREEZE_GUARDS START =====
# Batch 16 freeze-final guard:
# Artifact writes must remain under the planned replay run root.

def _batch16_path_inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False


def validate_artifact_plan_path_containment(artifact_plan: ReplayArtifactPlan) -> dict[str, Any]:
    root = Path(artifact_plan.root_dir).expanduser().resolve()
    path_attrs = (
        "manifest_path",
        "log_dir",
        "artifacts_dir",
        "dataset_summary_path",
        "scope_profile_path",
        "integrity_report_path",
        "metrics_summary_path",
        "trade_log_path",
        "candidate_audit_path",
        "blocker_breakdown_path",
        "exit_breakdown_path",
        "differential_report_path",
        "effective_inputs_path",
        "effective_overrides_flat_path",
    )

    checked: list[str] = []
    for attr in path_attrs:
        value = getattr(artifact_plan, attr)
        candidate = Path(value).expanduser()
        if not _batch16_path_inside(root, candidate):
            raise ReplayArtifactsValidationError(
                f"artifact path {attr} escapes root_dir: {value!r} not under {str(root)!r}"
            )
        checked.append(attr)

    return {
        "ok": True,
        "root_dir": str(root),
        "checked_path_fields": checked,
    }


if "_validate_artifact_plan" in globals():
    _BATCH16_ORIGINAL_VALIDATE_ARTIFACT_PLAN = _validate_artifact_plan

    def _validate_artifact_plan(artifact_plan: ReplayArtifactPlan) -> None:
        _BATCH16_ORIGINAL_VALIDATE_ARTIFACT_PLAN(artifact_plan)
        validate_artifact_plan_path_containment(artifact_plan)
# ===== BATCH16_REPLAY_PACKAGE_FREEZE_GUARDS END =====

# BEGIN BATCH27E_REPLAY_ARTIFACT_INTEGRITY_HELPERS

def replay_artifact_reset_manifest(*, run_id, artifact_root):
    """Return replay-only artifact reset manifest.

    The safety layer enforces that artifact_root is under run/replay.
    """
    from app.mme_scalpx.replay.safety import assert_replay_artifact_path

    root = assert_replay_artifact_path(artifact_root)
    return {
        "schema_version": "replay_artifact_reset_manifest_v1",
        "run_id": str(run_id),
        "artifact_root": str(root),
        "artifact_state_reset": True,
        "paper_armed_approved": False,
        "live_trading_approved": False,
        "production_doctrine_changed": False,
    }

try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "replay_artifact_reset_manifest",
)))

# END BATCH27E_REPLAY_ARTIFACT_INTEGRITY_HELPERS

# BEGIN BATCH27K_REPLAY_ARTIFACT_MATERIALIZATION_HELPERS

def replay_batch_required_artifact_names():
    """Return frozen replay batch artifact names."""
    from app.mme_scalpx.replay.artifact_materializer import REPLAY_BATCH_REQUIRED_ARTIFACTS

    return tuple(REPLAY_BATCH_REQUIRED_ARTIFACTS)

try:
    __all__
except NameError:
    __all__ = tuple()

__all__ = tuple(dict.fromkeys(tuple(__all__) + (
    "replay_batch_required_artifact_names",
)))

# END BATCH27K_REPLAY_ARTIFACT_MATERIALIZATION_HELPERS
