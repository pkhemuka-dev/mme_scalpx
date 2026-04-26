from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/doctrine_contracts.py

Frozen static doctrine registry and provider-profile contracts for the
strategy-family runtime.

Purpose
-------
This module OWNS:
- doctrine contract records for all five families
- required provider-profile contracts
- setup-kind identities
- frozen branch enablement and param-path mapping
- deterministic static lookup / iteration helpers
- import-time validation of family/doctrine/profile coverage

This module DOES NOT own:
- runtime provider health mutation
- Redis reads or writes
- doctrine signal evaluation
- feature math
- live arbitration
- live publishing
- composition wiring

Design rules
------------
- This file is the static contract registry for the doctrine family layer.
- It must remain provider-aware but runtime-agnostic.
- It must not silently infer family/doctrine/profile coverage.
- Static records must be immutable after import.
- Classic MIS families remain degraded-safe when Dhan context is absent/stale.
- MISO requires Dhan selected-option/context truth and healthy synced futures truth.
"""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping

from app.mme_scalpx.core import names as N

from .common import DOCTRINE_PARAM_PATHS, FAMILY_ORDER

# ============================================================================
# Frozen setup-kind identities
# ============================================================================

SETUP_KIND_PULLBACK_RESUME: Final[str] = "pullback_resume"
SETUP_KIND_BREAKOUT_CONTINUATION: Final[str] = "breakout_continuation"
SETUP_KIND_COMPRESSION_BREAKOUT_RETEST: Final[str] = "compression_breakout_retest"
SETUP_KIND_TRAP_REVERSAL: Final[str] = "trap_reversal"
SETUP_KIND_OPTION_LED_MICROSTRUCTURE_BURST: Final[str] = (
    "option_led_microstructure_burst"
)

ALLOWED_SETUP_KINDS: Final[tuple[str, ...]] = (
    SETUP_KIND_PULLBACK_RESUME,
    SETUP_KIND_BREAKOUT_CONTINUATION,
    SETUP_KIND_COMPRESSION_BREAKOUT_RETEST,
    SETUP_KIND_TRAP_REVERSAL,
    SETUP_KIND_OPTION_LED_MICROSTRUCTURE_BURST,
)

# ============================================================================
# Frozen provider-profile identities
# ============================================================================

PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE: Final[str] = (
    "CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE"
)
PROFILE_MISO_DHAN_MANDATORY_SIGNAL_PATH: Final[str] = (
    "MISO_DHAN_MANDATORY_SIGNAL_PATH"
)

PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE: Final[str] = (
    "MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE"
)

ALLOWED_PROVIDER_PROFILE_IDS: Final[tuple[str, ...]] = (
    PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE,
    PROFILE_MISO_DHAN_MANDATORY_SIGNAL_PATH,
    PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE,
)

# ============================================================================
# Exceptions
# ============================================================================


class DoctrineContractsError(ValueError):
    """Raised when the doctrine contract registry is internally inconsistent."""


# ============================================================================
# Small validation helpers
# ============================================================================


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DoctrineContractsError(message)


def _require_non_empty_str(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise DoctrineContractsError(f"{field_name} must be str, got {type(value).__name__}")
    cleaned = value.strip()
    if not cleaned:
        raise DoctrineContractsError(f"{field_name} must be non-empty")
    return cleaned


def _freeze_mapping(mapping: Mapping[str, str]) -> Mapping[str, str]:
    return MappingProxyType(dict(mapping))


# ============================================================================
# Static contract dataclasses
# ============================================================================


@dataclass(frozen=True, slots=True)
class RequiredProviderProfile:
    profile_id: str
    description: str
    futures_provider_id: str | None = None
    allowed_futures_provider_ids: tuple[str, ...] = ()
    selected_option_provider_id: str | None = None
    option_context_provider_id: str | None = None
    execution_primary_provider_id: str | None = None
    execution_fallback_provider_id: str | None = None
    allow_dhan_degraded: bool = False
    execution_bridge_required: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", _require_non_empty_str(self.profile_id, "profile_id"))
        object.__setattr__(self, "description", _require_non_empty_str(self.description, "description"))

        _require(
            self.profile_id in ALLOWED_PROVIDER_PROFILE_IDS,
            f"unknown provider profile id: {self.profile_id!r}",
        )

        for field_name in (
            "futures_provider_id",
            "selected_option_provider_id",
            "option_context_provider_id",
            "execution_primary_provider_id",
            "execution_fallback_provider_id",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require(
                    value in N.ALLOWED_PROVIDER_IDS,
                    f"{field_name} has unsupported provider id: {value!r}",
                )

        _require(
            isinstance(self.allowed_futures_provider_ids, tuple),
            "allowed_futures_provider_ids must be tuple[str, ...]",
        )
        seen_allowed_futures: set[str] = set()
        for provider_id in self.allowed_futures_provider_ids:
            _require(
                provider_id in N.ALLOWED_PROVIDER_IDS,
                f"allowed_futures_provider_ids has unsupported provider id: {provider_id!r}",
            )
            _require(
                provider_id not in seen_allowed_futures,
                f"duplicate allowed_futures_provider_ids provider id: {provider_id!r}",
            )
            seen_allowed_futures.add(provider_id)

        if self.profile_id == PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE:
            _require(
                self.allow_dhan_degraded is True,
                "classic profile must allow Dhan-degraded mode",
            )
            _require(
                self.execution_bridge_required is False,
                "classic profile must not require execution bridge truth",
            )

        if self.profile_id == PROFILE_MISO_DHAN_MANDATORY_SIGNAL_PATH:
            _require(
                self.allow_dhan_degraded is False,
                "MISO profile must not allow Dhan-degraded signal path",
            )
            _require(
                self.execution_bridge_required is True,
                "MISO profile must require execution bridge truth",
            )
            _require(
                self.futures_provider_id == N.PROVIDER_DHAN,
                "MISO legacy profile requires Dhan futures signal path",
            )
            _require(
                self.selected_option_provider_id == N.PROVIDER_DHAN,
                "MISO legacy profile requires Dhan selected-option signal path",
            )
            _require(
                self.option_context_provider_id == N.PROVIDER_DHAN,
                "MISO legacy profile requires Dhan option-context signal path",
            )

        if self.profile_id == PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE:
            _require(
                self.allow_dhan_degraded is False,
                "MISO healthy-futures baseline profile must not allow Dhan-degraded signal path",
            )
            _require(
                self.execution_bridge_required is True,
                "MISO healthy-futures baseline profile must require execution bridge truth",
            )
            _require(
                self.futures_provider_id is None,
                "MISO healthy-futures baseline profile must not hard-code one futures provider",
            )
            _require(
                self.allowed_futures_provider_ids == (N.PROVIDER_ZERODHA, N.PROVIDER_DHAN),
                "MISO healthy-futures baseline profile allows Zerodha or Dhan futures only",
            )
            _require(
                self.selected_option_provider_id == N.PROVIDER_DHAN,
                "MISO healthy-futures baseline profile requires Dhan selected-option signal path",
            )
            _require(
                self.option_context_provider_id == N.PROVIDER_DHAN,
                "MISO healthy-futures baseline profile requires Dhan option-context signal path",
            )


@dataclass(frozen=True, slots=True)
class DoctrineContractSpec:
    family_id: str
    doctrine_id: str
    branches_enabled: tuple[str, ...]
    setup_kind: str
    live_eligible: bool
    shadow_eligible: bool
    required_provider_profile_id: str
    param_paths_by_branch: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "family_id", _require_non_empty_str(self.family_id, "family_id"))
        object.__setattr__(self, "doctrine_id", _require_non_empty_str(self.doctrine_id, "doctrine_id"))
        object.__setattr__(self, "setup_kind", _require_non_empty_str(self.setup_kind, "setup_kind"))
        object.__setattr__(
            self,
            "required_provider_profile_id",
            _require_non_empty_str(
                self.required_provider_profile_id,
                "required_provider_profile_id",
            ),
        )

        _require(
            self.family_id in N.ALLOWED_STRATEGY_FAMILY_IDS,
            f"unknown family_id: {self.family_id!r}",
        )
        _require(
            self.doctrine_id in N.ALLOWED_DOCTRINE_IDS,
            f"unknown doctrine_id: {self.doctrine_id!r}",
        )
        _require(
            self.setup_kind in ALLOWED_SETUP_KINDS,
            f"unsupported setup_kind: {self.setup_kind!r}",
        )
        _require(
            self.required_provider_profile_id in ALLOWED_PROVIDER_PROFILE_IDS,
            (
                "unsupported required_provider_profile_id: "
                f"{self.required_provider_profile_id!r}"
            ),
        )
        _require(
            isinstance(self.live_eligible, bool),
            "live_eligible must be bool",
        )
        _require(
            isinstance(self.shadow_eligible, bool),
            "shadow_eligible must be bool",
        )
        _require(
            isinstance(self.branches_enabled, tuple),
            "branches_enabled must be tuple[str, ...]",
        )
        _require(
            len(self.branches_enabled) > 0,
            "branches_enabled must not be empty",
        )

        seen: set[str] = set()
        for branch_id in self.branches_enabled:
            _require(
                branch_id in N.ALLOWED_BRANCH_IDS,
                f"unsupported branch in branches_enabled: {branch_id!r}",
            )
            _require(
                branch_id not in seen,
                f"duplicate branch in branches_enabled: {branch_id!r}",
            )
            seen.add(branch_id)

        _require(
            isinstance(self.param_paths_by_branch, Mapping),
            "param_paths_by_branch must be a mapping",
        )
        _require(
            set(self.param_paths_by_branch.keys()) == set(self.branches_enabled),
            "param_paths_by_branch keys must match branches_enabled exactly",
        )

        frozen_paths: dict[str, str] = {}
        for branch_id, param_path in self.param_paths_by_branch.items():
            frozen_paths[branch_id] = _require_non_empty_str(
                param_path,
                f"param_paths_by_branch[{branch_id!r}]",
            )
            _require(
                frozen_paths[branch_id].endswith(".yaml"),
                (
                    "param path must end with .yaml for "
                    f"{self.family_id}/{branch_id}: {frozen_paths[branch_id]!r}"
                ),
            )

        object.__setattr__(self, "param_paths_by_branch", _freeze_mapping(frozen_paths))


# ============================================================================
# Required provider profiles
# ============================================================================

_REQUIRED_PROVIDER_PROFILES_RAW: Final[dict[str, RequiredProviderProfile]] = {
    PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE: RequiredProviderProfile(
        profile_id=PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE,
        description=(
            "Classic MIS families are futures-led / option-confirmed, may use "
            "Dhan enhancement when healthy, and remain degraded-safe when Dhan "
            "context is stale or unavailable."
        ),
        futures_provider_id=None,
        selected_option_provider_id=None,
        option_context_provider_id=None,
        execution_primary_provider_id=N.PROVIDER_ZERODHA,
        execution_fallback_provider_id=N.PROVIDER_DHAN,
        allow_dhan_degraded=True,
        execution_bridge_required=False,
    ),
    PROFILE_MISO_DHAN_MANDATORY_SIGNAL_PATH: RequiredProviderProfile(
        profile_id=PROFILE_MISO_DHAN_MANDATORY_SIGNAL_PATH,
        description=(
            "MISO requires Dhan chain context, Dhan selected-option live signal "
            "path, Dhan futures live signal path, and explicit execution-bridge "
            "truth before order send."
        ),
        futures_provider_id=N.PROVIDER_DHAN,
        selected_option_provider_id=N.PROVIDER_DHAN,
        option_context_provider_id=N.PROVIDER_DHAN,
        execution_primary_provider_id=N.PROVIDER_ZERODHA,
        execution_fallback_provider_id=N.PROVIDER_DHAN,
        allow_dhan_degraded=False,
        execution_bridge_required=True,
    ),
    PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE: RequiredProviderProfile(
        profile_id=PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE,
        description=(
            "MISO current production baseline requires Dhan chain context and "
            "Dhan selected-option live signal path, while allowing Zerodha or "
            "Dhan futures when the futures provider is healthy, fresh, and "
            "cross-provider synchronized. Dhan futures is required only in a "
            "future explicit Dhan-futures rollout mode."
        ),
        futures_provider_id=None,
        allowed_futures_provider_ids=(N.PROVIDER_ZERODHA, N.PROVIDER_DHAN),
        selected_option_provider_id=N.PROVIDER_DHAN,
        option_context_provider_id=N.PROVIDER_DHAN,
        execution_primary_provider_id=N.PROVIDER_ZERODHA,
        execution_fallback_provider_id=N.PROVIDER_DHAN,
        allow_dhan_degraded=False,
        execution_bridge_required=True,
    ),
}

REQUIRED_PROVIDER_PROFILES: Final[Mapping[str, RequiredProviderProfile]] = MappingProxyType(
    dict(_REQUIRED_PROVIDER_PROFILES_RAW)
)

# ============================================================================
# Doctrine contract records
# ============================================================================

_DOCTRINE_CONTRACTS_RAW: Final[dict[str, DoctrineContractSpec]] = {
    N.STRATEGY_FAMILY_MIST: DoctrineContractSpec(
        family_id=N.STRATEGY_FAMILY_MIST,
        doctrine_id=N.DOCTRINE_MIST,
        branches_enabled=(N.BRANCH_CALL, N.BRANCH_PUT),
        setup_kind=SETUP_KIND_PULLBACK_RESUME,
        live_eligible=True,
        shadow_eligible=True,
        required_provider_profile_id=PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE,
        param_paths_by_branch={
            N.BRANCH_CALL: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MIST, N.BRANCH_CALL)],
            N.BRANCH_PUT: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MIST, N.BRANCH_PUT)],
        },
    ),
    N.STRATEGY_FAMILY_MISB: DoctrineContractSpec(
        family_id=N.STRATEGY_FAMILY_MISB,
        doctrine_id=N.DOCTRINE_MISB,
        branches_enabled=(N.BRANCH_CALL, N.BRANCH_PUT),
        setup_kind=SETUP_KIND_BREAKOUT_CONTINUATION,
        live_eligible=True,
        shadow_eligible=True,
        required_provider_profile_id=PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE,
        param_paths_by_branch={
            N.BRANCH_CALL: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISB, N.BRANCH_CALL)],
            N.BRANCH_PUT: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISB, N.BRANCH_PUT)],
        },
    ),
    N.STRATEGY_FAMILY_MISC: DoctrineContractSpec(
        family_id=N.STRATEGY_FAMILY_MISC,
        doctrine_id=N.DOCTRINE_MISC,
        branches_enabled=(N.BRANCH_CALL, N.BRANCH_PUT),
        setup_kind=SETUP_KIND_COMPRESSION_BREAKOUT_RETEST,
        live_eligible=True,
        shadow_eligible=True,
        required_provider_profile_id=PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE,
        param_paths_by_branch={
            N.BRANCH_CALL: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISC, N.BRANCH_CALL)],
            N.BRANCH_PUT: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISC, N.BRANCH_PUT)],
        },
    ),
    N.STRATEGY_FAMILY_MISR: DoctrineContractSpec(
        family_id=N.STRATEGY_FAMILY_MISR,
        doctrine_id=N.DOCTRINE_MISR,
        branches_enabled=(N.BRANCH_CALL, N.BRANCH_PUT),
        setup_kind=SETUP_KIND_TRAP_REVERSAL,
        live_eligible=True,
        shadow_eligible=True,
        required_provider_profile_id=PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE,
        param_paths_by_branch={
            N.BRANCH_CALL: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISR, N.BRANCH_CALL)],
            N.BRANCH_PUT: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISR, N.BRANCH_PUT)],
        },
    ),
    N.STRATEGY_FAMILY_MISO: DoctrineContractSpec(
        family_id=N.STRATEGY_FAMILY_MISO,
        doctrine_id=N.DOCTRINE_MISO,
        branches_enabled=(N.BRANCH_CALL, N.BRANCH_PUT),
        setup_kind=SETUP_KIND_OPTION_LED_MICROSTRUCTURE_BURST,
        live_eligible=True,
        shadow_eligible=True,
        required_provider_profile_id=PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE,
        param_paths_by_branch={
            N.BRANCH_CALL: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISO, N.BRANCH_CALL)],
            N.BRANCH_PUT: DOCTRINE_PARAM_PATHS[(N.STRATEGY_FAMILY_MISO, N.BRANCH_PUT)],
        },
    ),
}

DOCTRINE_CONTRACTS: Final[Mapping[str, DoctrineContractSpec]] = MappingProxyType(
    dict(_DOCTRINE_CONTRACTS_RAW)
)

# ============================================================================
# Validation
# ============================================================================


def _validate_registry() -> None:
    _require(
        tuple(FAMILY_ORDER) == tuple(N.ALLOWED_STRATEGY_FAMILY_IDS),
        "FAMILY_ORDER must match names.ALLOWED_STRATEGY_FAMILY_IDS exactly",
    )

    _require(
        set(REQUIRED_PROVIDER_PROFILES.keys()) == set(ALLOWED_PROVIDER_PROFILE_IDS),
        "required provider profiles must match allowed profile ids exactly",
    )

    _require(
        set(DOCTRINE_CONTRACTS.keys()) == set(FAMILY_ORDER),
        "doctrine contracts must cover FAMILY_ORDER exactly",
    )

    expected_doctrine_by_family = {
        N.STRATEGY_FAMILY_MIST: N.DOCTRINE_MIST,
        N.STRATEGY_FAMILY_MISB: N.DOCTRINE_MISB,
        N.STRATEGY_FAMILY_MISC: N.DOCTRINE_MISC,
        N.STRATEGY_FAMILY_MISR: N.DOCTRINE_MISR,
        N.STRATEGY_FAMILY_MISO: N.DOCTRINE_MISO,
    }

    for family_id in FAMILY_ORDER:
        spec = DOCTRINE_CONTRACTS[family_id]

        _require(
            spec.family_id == family_id,
            f"family key/spec mismatch for {family_id!r}",
        )
        _require(
            spec.doctrine_id == expected_doctrine_by_family[family_id],
            f"doctrine mismatch for {family_id!r}",
        )
        _require(
            spec.required_provider_profile_id in REQUIRED_PROVIDER_PROFILES,
            (
                "unknown required_provider_profile_id for "
                f"{family_id!r}: {spec.required_provider_profile_id!r}"
            ),
        )

        for branch_id in spec.branches_enabled:
            expected_param_path = DOCTRINE_PARAM_PATHS[(family_id, branch_id)]
            actual_param_path = spec.param_paths_by_branch[branch_id]
            _require(
                actual_param_path == expected_param_path,
                (
                    "param path mismatch for "
                    f"{family_id}/{branch_id}: {actual_param_path!r} != "
                    f"{expected_param_path!r}"
                ),
            )

        if family_id == N.STRATEGY_FAMILY_MISO:
            _require(
                spec.required_provider_profile_id
                == PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE,
                "MISO must use the Dhan-option/context plus healthy-synced-futures provider profile",
            )
        else:
            _require(
                spec.required_provider_profile_id
                == PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE,
                f"{family_id} must use the classic degraded-safe provider profile",
            )


_validate_registry()

# ============================================================================
# Public helpers
# ============================================================================


def get_required_provider_profile(profile_id: str) -> RequiredProviderProfile:
    try:
        return REQUIRED_PROVIDER_PROFILES[profile_id]
    except KeyError as exc:
        raise ValueError(f"unknown provider profile: {profile_id!r}") from exc


def get_doctrine_contract(family_id: str) -> DoctrineContractSpec:
    try:
        return DOCTRINE_CONTRACTS[family_id]
    except KeyError as exc:
        raise ValueError(f"unknown doctrine family: {family_id!r}") from exc


def get_param_path_for(family_id: str, branch_id: str) -> str:
    spec = get_doctrine_contract(family_id)
    try:
        return spec.param_paths_by_branch[branch_id]
    except KeyError as exc:
        raise ValueError(
            f"branch {branch_id!r} not enabled for family {family_id!r}"
        ) from exc


def get_setup_kind_for(family_id: str) -> str:
    return get_doctrine_contract(family_id).setup_kind


def iter_doctrine_contracts() -> tuple[DoctrineContractSpec, ...]:
    return tuple(get_doctrine_contract(family_id) for family_id in FAMILY_ORDER)


def iter_required_provider_profiles() -> tuple[RequiredProviderProfile, ...]:
    return tuple(
        REQUIRED_PROVIDER_PROFILES[profile_id]
        for profile_id in ALLOWED_PROVIDER_PROFILE_IDS
    )


__all__ = [
    "ALLOWED_PROVIDER_PROFILE_IDS",
    "ALLOWED_SETUP_KINDS",
    "DOCTRINE_CONTRACTS",
    "DOCTRINE_PARAM_PATHS",
    "DoctrineContractSpec",
    "DoctrineContractsError",
    "PROFILE_CLASSIC_DHAN_ENHANCED_DEGRADED_SAFE",
    "PROFILE_MISO_DHAN_MANDATORY_SIGNAL_PATH",
    "PROFILE_MISO_DHAN_CONTEXT_HEALTHY_FUTURES_BASELINE",
    "REQUIRED_PROVIDER_PROFILES",
    "RequiredProviderProfile",
    "SETUP_KIND_BREAKOUT_CONTINUATION",
    "SETUP_KIND_COMPRESSION_BREAKOUT_RETEST",
    "SETUP_KIND_OPTION_LED_MICROSTRUCTURE_BURST",
    "SETUP_KIND_PULLBACK_RESUME",
    "SETUP_KIND_TRAP_REVERSAL",
    "get_doctrine_contract",
    "get_param_path_for",
    "get_required_provider_profile",
    "get_setup_kind_for",
    "iter_doctrine_contracts",
    "iter_required_provider_profiles",
]
