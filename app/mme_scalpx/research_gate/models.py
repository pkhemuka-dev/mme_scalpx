"""Schema models for RAW / Research Gate.

Models are lightweight dataclasses. They do not read files, write files, call brokers,
write Redis, or execute strategy/risk/execution logic.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .contracts import (
    EVIDENCE_TRACKS,
    RAW_CONTRACT_VERSION,
    VERDICT_RESEARCH_ONLY_FINDING,
    validate_research_verdict,
)


@dataclass(frozen=True)
class RawArtifactRef:
    path: str
    artifact_type: str
    sha256: str | None = None
    rows: int | None = None
    bytes_size: int | None = None
    remarks: str = ""

    def validate(self) -> "RawArtifactRef":
        if not self.path:
            raise ValueError("RawArtifactRef.path is required")
        if not self.artifact_type:
            raise ValueError("RawArtifactRef.artifact_type is required")
        if self.rows is not None and self.rows < 0:
            raise ValueError("RawArtifactRef.rows cannot be negative")
        if self.bytes_size is not None and self.bytes_size < 0:
            raise ValueError("RawArtifactRef.bytes_size cannot be negative")
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class RawScorecard:
    data_quality_score: float | None = None
    sample_size_score: float | None = None
    pnl_score: float | None = None
    risk_score: float | None = None
    stability_score: float | None = None
    oi_wall_value_score: float | None = None
    overfit_risk_score: float | None = None
    promotion_readiness_score: float | None = None

    def validate(self) -> "RawScorecard":
        for name, value in asdict(self).items():
            if value is None:
                continue
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class RawRunManifest:
    run_id: str
    generated_utc: str
    source_mode: str
    evidence_tracks: tuple[str, ...] = EVIDENCE_TRACKS
    contract_version: str = RAW_CONTRACT_VERSION
    verdict: str = VERDICT_RESEARCH_ONLY_FINDING
    artifacts: tuple[RawArtifactRef, ...] = field(default_factory=tuple)
    scorecard: RawScorecard | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> "RawRunManifest":
        if not self.run_id:
            raise ValueError("RawRunManifest.run_id is required")
        if not self.generated_utc:
            raise ValueError("RawRunManifest.generated_utc is required")
        if not self.source_mode:
            raise ValueError("RawRunManifest.source_mode is required")
        unknown_tracks = sorted(set(self.evidence_tracks) - set(EVIDENCE_TRACKS))
        if unknown_tracks:
            raise ValueError(f"unknown RAW evidence tracks: {unknown_tracks}")
        validate_research_verdict(self.verdict)
        for artifact in self.artifacts:
            artifact.validate()
        if self.scorecard is not None:
            self.scorecard.validate()
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        payload["scorecard"] = self.scorecard.to_dict() if self.scorecard is not None else None
        return payload


@dataclass(frozen=True)
class RawPromotionVerdict:
    verdict: str
    reason: str
    production_mutation_allowed: bool = False
    paper_live_enablement_allowed: bool = False
    recommended_next_step: str = "manual_review"

    def validate(self) -> "RawPromotionVerdict":
        validate_research_verdict(self.verdict)
        if self.production_mutation_allowed:
            raise ValueError("RAW cannot allow direct production mutation")
        if self.paper_live_enablement_allowed:
            raise ValueError("RAW cannot allow direct paper/live enablement")
        if not self.reason:
            raise ValueError("RawPromotionVerdict.reason is required")
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)
