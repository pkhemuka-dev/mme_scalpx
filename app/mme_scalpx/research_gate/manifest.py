"""Manifest helpers for RAW / Research Gate."""

from __future__ import annotations

from datetime import datetime, timezone

from .contracts import EVIDENCE_TRACKS, VERDICT_RESEARCH_ONLY_FINDING
from .models import RawArtifactRef, RawRunManifest, RawScorecard


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_manifest(
    *,
    run_id: str,
    source_mode: str,
    verdict: str = VERDICT_RESEARCH_ONLY_FINDING,
    evidence_tracks: tuple[str, ...] = EVIDENCE_TRACKS,
    artifacts: tuple[RawArtifactRef, ...] = (),
    scorecard: RawScorecard | None = None,
    notes: tuple[str, ...] = (),
) -> RawRunManifest:
    manifest = RawRunManifest(
        run_id=run_id,
        generated_utc=utc_now_iso(),
        source_mode=source_mode,
        evidence_tracks=evidence_tracks,
        verdict=verdict,
        artifacts=artifacts,
        scorecard=scorecard,
        notes=notes,
    )
    return manifest.validate()
