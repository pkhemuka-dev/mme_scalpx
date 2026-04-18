"""
app.mme_scalpx.research_capture.config_loader

Frozen config-bundle loader and resolver for the research-capture chapter.

Ownership
---------
This module OWNS:
- loading the canonical config registry
- validating the registry surface and referenced files
- resolving entrypoint bundles from the registry
- resolving profile-group bundles from the registry
- building an effective registry snapshot for auditability

This module DOES NOT own:
- runtime business logic
- archive writing
- report generation
- broker/source behavior
- mutation of production doctrine or canonical archive

Design laws
-----------
- registry is the single authoritative config-bundle index
- all entrypoints resolve configs through the registry
- validation fails closed on missing or unknown surfaces
- this module stays thin: names, validation, resolution, snapshot building
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

DEFAULT_CONFIG_REGISTRY_PATH = Path("etc/research_capture/config_registry.json")

_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "schema_name",
    "policy_version",
    "governance",
    "registry_roots",
    "core_contracts",
    "policy_contracts",
    "entrypoint_contracts",
    "profile_groups",
    "load_order",
    "output_contract",
)

_DEFAULT_PROFILE_GROUP_BY_ENTRYPOINT: dict[str, str] = {
    "verify": "base",
    "run": "live_capture",
    "backfill": "historical_backfill",
    "research": "offline_research",
}


class ConfigRegistryError(RuntimeError):
    """Base error for config-registry loading and resolution."""


class RegistryValidationError(ConfigRegistryError):
    """Raised when the registry surface is invalid."""


class UnknownEntrypointError(ConfigRegistryError):
    """Raised when an unknown entrypoint is requested."""


class UnknownProfileGroupError(ConfigRegistryError):
    """Raised when an unknown profile group is requested."""


class UnknownContractKeyError(ConfigRegistryError):
    """Raised when an unknown registered contract key is requested."""


class MissingRegisteredFileError(ConfigRegistryError):
    """Raised when a registered file or script does not exist."""


@dataclass(frozen=True, slots=True)
class EntrypointBundle:
    """Resolved contract bundle for one registered entrypoint."""

    entrypoint: str
    script: str
    default_lane: str
    default_source: str
    required_contract_keys: tuple[str, ...]
    resolved_contract_paths: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "entrypoint": self.entrypoint,
            "script": self.script,
            "default_lane": self.default_lane,
            "default_source": self.default_source,
            "required_contract_keys": list(self.required_contract_keys),
            "resolved_contract_paths": dict(self.resolved_contract_paths),
        }


@dataclass(frozen=True, slots=True)
class ProfileGroupBundle:
    """Resolved contract bundle for one registered profile group."""

    profile_group: str
    contract_keys: tuple[str, ...]
    resolved_contract_paths: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_group": self.profile_group,
            "contract_keys": list(self.contract_keys),
            "resolved_contract_paths": dict(self.resolved_contract_paths),
        }


@dataclass(frozen=True, slots=True)
class EffectiveRegistrySnapshot:
    """Audit snapshot of the resolved registry surface used for one action."""

    registry_version: str
    resolved_profile_group: str
    resolved_entrypoint: str
    resolved_configs: dict[str, str]
    ts_utc: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_version": self.registry_version,
            "resolved_profile_group": self.resolved_profile_group,
            "resolved_entrypoint": self.resolved_entrypoint,
            "resolved_configs": dict(self.resolved_configs),
            "ts_utc": self.ts_utc,
        }


@dataclass(frozen=True, slots=True)
class ConfigRegistry:
    """Typed view over the canonical research-capture config registry."""

    schema_name: str
    policy_version: str
    governance: dict[str, Any]
    registry_roots: dict[str, str]
    core_contracts: dict[str, str]
    policy_contracts: dict[str, str]
    entrypoint_contracts: dict[str, dict[str, Any]]
    profile_groups: dict[str, list[str]]
    load_order: list[str]
    output_contract: dict[str, Any]
    source_path: str

    def all_contracts(self) -> dict[str, str]:
        contracts: dict[str, str] = {}
        contracts.update(self.core_contracts)
        contracts.update(self.policy_contracts)
        return contracts

    def contract_keys(self) -> tuple[str, ...]:
        return tuple(self.load_order)

    def required_effective_registry_fields(self) -> tuple[str, ...]:
        fields = self.output_contract.get("required_effective_registry_fields", [])
        return tuple(fields)


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _ensure_mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RegistryValidationError(f"{name} must be a mapping")
    return dict(value)


def _ensure_nonempty_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryValidationError(f"{name} must be a non-empty string")
    return value


def _ensure_string_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list):
        raise RegistryValidationError(f"{name} must be a list[str]")
    output: list[str] = []
    for idx, item in enumerate(value):
        output.append(_ensure_nonempty_str(item, f"{name}[{idx}]"))
    return output


def _ensure_unique_strings(items: list[str], name: str) -> list[str]:
    if len(items) != len(set(items)):
        raise RegistryValidationError(f"{name} contains duplicate values")
    return items


def _resolve_project_root(project_root: Path | None = None) -> Path:
    root = project_root if project_root is not None else Path.cwd()
    return root.resolve()


def _resolve_path(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def _validate_registered_file_exists(root: Path, label: str, raw_path: str) -> None:
    resolved = _resolve_path(root, raw_path)
    if not resolved.exists():
        raise MissingRegisteredFileError(f"{label} missing: {raw_path}")
    if not resolved.is_file():
        raise MissingRegisteredFileError(f"{label} is not a file: {raw_path}")


def _validate_entrypoint_contracts(
    entrypoint_contracts: dict[str, Any],
    all_contract_keys: set[str],
    root: Path,
) -> dict[str, dict[str, Any]]:
    validated: dict[str, dict[str, Any]] = {}
    for entrypoint, raw_cfg in entrypoint_contracts.items():
        entrypoint_name = _ensure_nonempty_str(entrypoint, "entrypoint_contracts key")
        cfg = _ensure_mapping(raw_cfg, f"entrypoint_contracts.{entrypoint_name}")

        script = _ensure_nonempty_str(cfg.get("script"), f"{entrypoint_name}.script")
        required_configs = _ensure_unique_strings(
            _ensure_string_list(cfg.get("required_configs"), f"{entrypoint_name}.required_configs"),
            f"{entrypoint_name}.required_configs",
        )
        default_lane = _ensure_nonempty_str(cfg.get("default_lane"), f"{entrypoint_name}.default_lane")
        default_source = _ensure_nonempty_str(cfg.get("default_source"), f"{entrypoint_name}.default_source")

        if not set(required_configs).issubset(all_contract_keys):
            unknown = sorted(set(required_configs).difference(all_contract_keys))
            raise RegistryValidationError(
                f"{entrypoint_name}.required_configs contain unknown contract keys: {unknown}"
            )

        _validate_registered_file_exists(root, f"{entrypoint_name}.script", script)

        validated[entrypoint_name] = {
            "script": script,
            "required_configs": required_configs,
            "default_lane": default_lane,
            "default_source": default_source,
        }
    return validated


def _validate_profile_groups(
    profile_groups: dict[str, Any],
    all_contract_keys: set[str],
) -> dict[str, list[str]]:
    validated: dict[str, list[str]] = {}
    for group_name, raw_members in profile_groups.items():
        name = _ensure_nonempty_str(group_name, "profile_groups key")
        members = _ensure_unique_strings(
            _ensure_string_list(raw_members, f"profile_groups.{name}"),
            f"profile_groups.{name}",
        )
        if not set(members).issubset(all_contract_keys):
            unknown = sorted(set(members).difference(all_contract_keys))
            raise RegistryValidationError(f"profile_groups.{name} contains unknown contract keys: {unknown}")
        validated[name] = members
    return validated


def load_config_registry(
    path: Path | str = DEFAULT_CONFIG_REGISTRY_PATH,
    *,
    project_root: Path | None = None,
) -> ConfigRegistry:
    """
    Load and validate the canonical config registry.

    Validation includes:
    - top-level surface checks
    - duplicate/unknown key checks
    - existence checks for registered files and scripts
    """
    root = _resolve_project_root(project_root)
    raw_registry_path = Path(path)
    registry_path = _resolve_path(root, str(raw_registry_path))

    if not registry_path.exists():
        raise MissingRegisteredFileError(f"config registry missing: {registry_path}")

    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RegistryValidationError(f"config registry is not valid JSON: {registry_path}") from exc

    data = _ensure_mapping(payload, "config_registry")

    missing_top_level = [key for key in _REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing_top_level:
        raise RegistryValidationError(f"config registry missing top-level keys: {missing_top_level}")

    schema_name = _ensure_nonempty_str(data["schema_name"], "schema_name")
    policy_version = _ensure_nonempty_str(data["policy_version"], "policy_version")
    governance = _ensure_mapping(data["governance"], "governance")
    registry_roots = _ensure_mapping(data["registry_roots"], "registry_roots")
    core_contracts = _ensure_mapping(data["core_contracts"], "core_contracts")
    policy_contracts = _ensure_mapping(data["policy_contracts"], "policy_contracts")

    all_contract_keys = set(core_contracts) | set(policy_contracts)
    if len(all_contract_keys) != len(core_contracts) + len(policy_contracts):
        raise RegistryValidationError("duplicate contract key exists across core_contracts and policy_contracts")

    validated_core: dict[str, str] = {}
    for key, raw_path in core_contracts.items():
        name = _ensure_nonempty_str(key, "core_contracts key")
        path_value = _ensure_nonempty_str(raw_path, f"core_contracts.{name}")
        _validate_registered_file_exists(root, f"core_contracts.{name}", path_value)
        validated_core[name] = path_value

    validated_policy: dict[str, str] = {}
    for key, raw_path in policy_contracts.items():
        name = _ensure_nonempty_str(key, "policy_contracts key")
        path_value = _ensure_nonempty_str(raw_path, f"policy_contracts.{name}")
        _validate_registered_file_exists(root, f"policy_contracts.{name}", path_value)
        validated_policy[name] = path_value

    entrypoint_contracts = _validate_entrypoint_contracts(
        _ensure_mapping(data["entrypoint_contracts"], "entrypoint_contracts"),
        set(validated_core) | set(validated_policy),
        root,
    )
    profile_groups = _validate_profile_groups(
        _ensure_mapping(data["profile_groups"], "profile_groups"),
        set(validated_core) | set(validated_policy),
    )

    load_order = _ensure_unique_strings(_ensure_string_list(data["load_order"], "load_order"), "load_order")
    if set(load_order) != (set(validated_core) | set(validated_policy)):
        missing = sorted((set(validated_core) | set(validated_policy)).difference(load_order))
        extra = sorted(set(load_order).difference(set(validated_core) | set(validated_policy)))
        raise RegistryValidationError(
            f"load_order mismatch; missing={missing} extra={extra}"
        )

    output_contract = _ensure_mapping(data["output_contract"], "output_contract")
    required_effective_registry_fields = _ensure_unique_strings(
        _ensure_string_list(
            output_contract.get("required_effective_registry_fields"),
            "output_contract.required_effective_registry_fields",
        ),
        "output_contract.required_effective_registry_fields",
    )
    filename = _ensure_nonempty_str(
        output_contract.get("effective_registry_snapshot_filename"),
        "output_contract.effective_registry_snapshot_filename",
    )
    emit_snapshot = output_contract.get("emit_effective_registry_snapshot")
    if emit_snapshot is not True:
        raise RegistryValidationError("output_contract.emit_effective_registry_snapshot must be true")

    normalized_output_contract = {
        "required_effective_registry_fields": required_effective_registry_fields,
        "emit_effective_registry_snapshot": True,
        "effective_registry_snapshot_filename": filename,
    }

    for root_key, root_value in registry_roots.items():
        _ensure_nonempty_str(root_key, "registry_roots key")
        _ensure_nonempty_str(root_value, f"registry_roots.{root_key}")

    return ConfigRegistry(
        schema_name=schema_name,
        policy_version=policy_version,
        governance=dict(governance),
        registry_roots={k: str(v) for k, v in registry_roots.items()},
        core_contracts=validated_core,
        policy_contracts=validated_policy,
        entrypoint_contracts=entrypoint_contracts,
        profile_groups=profile_groups,
        load_order=load_order,
        output_contract=normalized_output_contract,
        source_path=str(registry_path),
    )


def resolve_entrypoint_bundle(
    entrypoint: str,
    *,
    registry: ConfigRegistry | None = None,
    project_root: Path | None = None,
) -> EntrypointBundle:
    """Resolve one entrypoint into its required registered-contract bundle."""
    reg = registry if registry is not None else load_config_registry(project_root=project_root)
    name = _ensure_nonempty_str(entrypoint, "entrypoint")
    if name not in reg.entrypoint_contracts:
        raise UnknownEntrypointError(f"unknown entrypoint: {name}")

    cfg = reg.entrypoint_contracts[name]
    contracts = reg.all_contracts()
    resolved_contract_paths = {key: contracts[key] for key in cfg["required_configs"]}

    return EntrypointBundle(
        entrypoint=name,
        script=cfg["script"],
        default_lane=cfg["default_lane"],
        default_source=cfg["default_source"],
        required_contract_keys=tuple(cfg["required_configs"]),
        resolved_contract_paths=resolved_contract_paths,
    )


def resolve_profile_group_bundle(
    profile_group: str,
    *,
    registry: ConfigRegistry | None = None,
    project_root: Path | None = None,
) -> ProfileGroupBundle:
    """Resolve one profile group into its registered-contract bundle."""
    reg = registry if registry is not None else load_config_registry(project_root=project_root)
    name = _ensure_nonempty_str(profile_group, "profile_group")
    if name not in reg.profile_groups:
        raise UnknownProfileGroupError(f"unknown profile group: {name}")

    members = reg.profile_groups[name]
    contracts = reg.all_contracts()
    resolved_contract_paths = {key: contracts[key] for key in members}

    return ProfileGroupBundle(
        profile_group=name,
        contract_keys=tuple(members),
        resolved_contract_paths=resolved_contract_paths,
    )


def load_registered_json_contract(
    contract_key: str,
    *,
    registry: ConfigRegistry | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    """
    Load a registered JSON contract by key.

    Use this only for JSON-backed contracts. CSV-backed entries such as field_dictionary
    must be consumed by the caller using their own parser.
    """
    reg = registry if registry is not None else load_config_registry(project_root=project_root)
    key = _ensure_nonempty_str(contract_key, "contract_key")
    contracts = reg.all_contracts()
    if key not in contracts:
        raise UnknownContractKeyError(f"unknown contract key: {key}")

    rel_path = contracts[key]
    if not rel_path.endswith(".json"):
        raise RegistryValidationError(f"registered contract is not JSON-backed: {key} -> {rel_path}")

    root = _resolve_project_root(project_root)
    path = _resolve_path(root, rel_path)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RegistryValidationError(f"registered JSON contract invalid: {key} -> {rel_path}") from exc

    return _ensure_mapping(payload, f"registered_json_contract.{key}")


def build_effective_registry_snapshot(
    *,
    entrypoint: str,
    profile_group: str | None = None,
    registry: ConfigRegistry | None = None,
    project_root: Path | None = None,
    ts_utc: str | None = None,
) -> EffectiveRegistrySnapshot:
    """
    Build an auditable effective-registry snapshot for one resolved action.

    If profile_group is omitted, a canonical default is inferred from the entrypoint.
    """
    reg = registry if registry is not None else load_config_registry(project_root=project_root)
    entry_bundle = resolve_entrypoint_bundle(entrypoint, registry=reg, project_root=project_root)

    resolved_profile_group = (
        profile_group
        if profile_group is not None
        else _DEFAULT_PROFILE_GROUP_BY_ENTRYPOINT.get(entry_bundle.entrypoint)
    )
    if resolved_profile_group is None:
        raise UnknownProfileGroupError(
            f"no default profile group mapping for entrypoint: {entry_bundle.entrypoint}"
        )

    profile_bundle = resolve_profile_group_bundle(
        resolved_profile_group,
        registry=reg,
        project_root=project_root,
    )

    resolved_configs: dict[str, str] = {}
    for contract_key in reg.load_order:
        if contract_key in entry_bundle.resolved_contract_paths:
            resolved_configs[contract_key] = entry_bundle.resolved_contract_paths[contract_key]
        elif contract_key in profile_bundle.resolved_contract_paths:
            resolved_configs[contract_key] = profile_bundle.resolved_contract_paths[contract_key]

    snapshot = EffectiveRegistrySnapshot(
        registry_version=reg.policy_version,
        resolved_profile_group=profile_bundle.profile_group,
        resolved_entrypoint=entry_bundle.entrypoint,
        resolved_configs=resolved_configs,
        ts_utc=ts_utc or _utc_now_z(),
    )

    required_fields = set(reg.required_effective_registry_fields())
    produced_fields = set(snapshot.to_dict())
    if required_fields != produced_fields:
        missing = sorted(required_fields.difference(produced_fields))
        extra = sorted(produced_fields.difference(required_fields))
        raise RegistryValidationError(
            f"effective registry snapshot field mismatch; missing={missing} extra={extra}"
        )

    return snapshot


__all__ = [
    "DEFAULT_CONFIG_REGISTRY_PATH",
    "ConfigRegistry",
    "ConfigRegistryError",
    "RegistryValidationError",
    "UnknownEntrypointError",
    "UnknownProfileGroupError",
    "UnknownContractKeyError",
    "MissingRegisteredFileError",
    "EntrypointBundle",
    "ProfileGroupBundle",
    "EffectiveRegistrySnapshot",
    "load_config_registry",
    "resolve_entrypoint_bundle",
    "resolve_profile_group_bundle",
    "load_registered_json_contract",
    "build_effective_registry_snapshot",
]
