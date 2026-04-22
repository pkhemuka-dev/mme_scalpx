from __future__ import annotations

from .doctrine_runtime import DoctrineCandidate, DoctrineCandidateContext


def evaluate_entry(ctx: DoctrineCandidateContext) -> DoctrineCandidate | None:
    return None


def evaluate_exit(*args, **kwargs) -> str | None:
    return None
