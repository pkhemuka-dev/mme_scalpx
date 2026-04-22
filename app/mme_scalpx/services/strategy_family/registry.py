from __future__ import annotations

"""
app/mme_scalpx/strategy_family/registry.py

Family evaluator registry for doctrine modules.

Purpose
-------
This module OWNS:
- evaluator module-path registry
- lazy evaluator import/registration
- tolerant fallback when a doctrine module is still a stub
- public family-evaluator lookup surface

This module DOES NOT own:
- doctrine math
- Redis access
- live publication
"""

import importlib
from typing import Callable, Final

from app.mme_scalpx.core import names as N

from .common import FAMILY_ORDER, doctrine_for_family
from .doctrine_runtime import DoctrineEvaluationResult, DoctrineRuntimeInput, no_signal_result

FamilyEvaluator = Callable[[DoctrineRuntimeInput], DoctrineEvaluationResult]

FAMILY_MODULE_PATHS: Final[dict[str, str]] = {
    N.STRATEGY_FAMILY_MIST: "app.mme_scalpx.services.strategy_family.mist",
    N.STRATEGY_FAMILY_MISB: "app.mme_scalpx.services.strategy_family.misb",
    N.STRATEGY_FAMILY_MISC: "app.mme_scalpx.services.strategy_family.misc",
    N.STRATEGY_FAMILY_MISR: "app.mme_scalpx.services.strategy_family.misr",
    N.STRATEGY_FAMILY_MISO: "app.mme_scalpx.services.strategy_family.miso",
}

_EVALUATOR_CACHE: dict[str, FamilyEvaluator] = {}


def _build_noop_evaluator(family_id: str) -> FamilyEvaluator:
    doctrine_id = doctrine_for_family(family_id)

    def _noop(runtime: DoctrineRuntimeInput) -> DoctrineEvaluationResult:
        return no_signal_result(
            family_id=family_id,
            doctrine_id=doctrine_id,
            branch_id=runtime.branch_id,
            metadata={"noop_evaluator": True},
        )

    return _noop


def _extract_callable(module, family_id: str) -> FamilyEvaluator:
    for name in ("evaluate_doctrine", "evaluate_family", "evaluate"):
        fn = getattr(module, name, None)
        if callable(fn):
            return fn

    factory = getattr(module, "get_evaluator", None)
    if callable(factory):
        built = factory()
        if callable(built):
            return built

    return _build_noop_evaluator(family_id)


def _load_evaluator(family_id: str) -> FamilyEvaluator:
    module_path = FAMILY_MODULE_PATHS.get(family_id)
    if module_path is None:
        raise ValueError(f"unknown family_id: {family_id!r}")
    module = importlib.import_module(module_path)
    return _extract_callable(module, family_id)


def register_family_evaluator(family_id: str, evaluator: FamilyEvaluator) -> None:
    if not callable(evaluator):
        raise TypeError("evaluator must be callable")
    _EVALUATOR_CACHE[family_id] = evaluator


def get_family_evaluator(family_id: str) -> FamilyEvaluator:
    evaluator = _EVALUATOR_CACHE.get(family_id)
    if evaluator is None:
        evaluator = _load_evaluator(family_id)
        _EVALUATOR_CACHE[family_id] = evaluator
    return evaluator


def list_registered_families() -> tuple[str, ...]:
    return tuple(FAMILY_ORDER)


__all__ = [
    "FAMILY_ORDER",
    "FamilyEvaluator",
    "get_family_evaluator",
    "list_registered_families",
    "register_family_evaluator",
]
