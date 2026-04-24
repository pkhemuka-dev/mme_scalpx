from __future__ import annotations

"""
app/mme_scalpx/services/feature_family/__init__.py

Canonical package export surface for ScalpX MME feature-family helpers.

Purpose
-------
This package module OWNS:
- the stable import surface for feature-family helper modules
- explicit re-export of the public ``common`` and ``contracts`` surfaces
- compatibility import stability for callers such as services/features.py

This package module DOES NOT own:
- feature computation
- runtime orchestration
- provider selection
- doctrine-specific trading logic
- side effects at import time

Frozen design rules
-------------------
- Keep this file thin and deterministic.
- Do not add runtime/business logic here.
- Re-export only the public surfaces declared by sibling modules.
- Preserve direct module access:
    from app.mme_scalpx.services.feature_family import common
    from app.mme_scalpx.services.feature_family import contracts
- Preserve convenient symbol access:
    from app.mme_scalpx.services.feature_family import <public symbol>
- Avoid wildcard namespace drift by deriving package ``__all__`` from the
  sibling module ``__all__`` declarations when present.
- Fail fast on sibling export collisions rather than silently shadowing names.
"""

from types import ModuleType
from typing import Final

from . import common
from . import contracts


def _public_names(module: ModuleType) -> tuple[str, ...]:
    """
    Return the declared public names for one sibling module.

    Contract:
    - if the module defines ``__all__``, use it exactly
    - otherwise export nothing implicitly from that module
    """
    names = getattr(module, "__all__", ())
    if not isinstance(names, (tuple, list)):
        raise TypeError(
            f"{module.__name__}.__all__ must be a tuple/list of strings"
        )

    normalized: list[str] = []
    seen: set[str] = set()
    for item in names:
        if not isinstance(item, str) or not item.strip():
            raise TypeError(
                f"{module.__name__}.__all__ must contain only non-empty strings"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return tuple(normalized)


_COMMON_EXPORTS: Final[tuple[str, ...]] = _public_names(common)
_CONTRACT_EXPORTS: Final[tuple[str, ...]] = _public_names(contracts)

_DUPLICATE_EXPORTS: Final[tuple[str, ...]] = tuple(
    sorted(set(_COMMON_EXPORTS).intersection(_CONTRACT_EXPORTS))
)
if _DUPLICATE_EXPORTS:
    raise RuntimeError(
        "feature_family package export collision between common and contracts: "
        + ", ".join(_DUPLICATE_EXPORTS)
    )

# Re-export declared public symbols only after collision validation.
from .common import *  # noqa: F401,F403,E402
from .contracts import *  # noqa: F401,F403,E402

__all__: tuple[str, ...] = (
    "common",
    "contracts",
    *_COMMON_EXPORTS,
    *_CONTRACT_EXPORTS,
)
