from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any, Iterable


class ReplaySafetyViolation(RuntimeError):
    """Raised when replay code attempts to cross a forbidden live boundary."""


REPLAY_KEY_PREFIX = "replay:"
REPLAY_KEY_PREFIXES = ("replay:", "replay::", "replay|")

BANNED_BROKER_IMPORT_PREFIXES = (
    "kiteconnect",
    "dhanhq",
    "app.mme_scalpx.integrations.broker_api",
    "app.mme_scalpx.integrations.broker_auth",
    "app.mme_scalpx.integrations.dhan_execution",
    "app.mme_scalpx.integrations.zerodha_execution",
    "app.mme_scalpx.integrations.dhan_broker",
    "app.mme_scalpx.integrations.zerodha_broker",
    "app.mme_scalpx.services.execution",
)

BANNED_BROKER_CALL_NAMES = (
    "place_order",
    "modify_order",
    "cancel_order",
    "cancel_all_orders",
    "exit_order",
    "flatten_position",
    "broker_flatten",
    "send_order",
    "submit_order",
    "squareoff",
    "square_off",
)

BANNED_REDIS_IMPORT_PREFIXES = (
    "redis",
    "redis.asyncio",
    "app.mme_scalpx.core.redisx",
)

BANNED_REDIS_WRITE_ATTR_CALLS = (
    "xadd",
    "hset",
    "hmset",
    "set",
    "setex",
    "mset",
    "publish",
    "delete",
    "unlink",
    "rpush",
    "lpush",
    "zadd",
)

# Direct function calls are much rarer and more suspicious than attribute calls.
# Keep this stricter subset to avoid false positives on ordinary .set().
BANNED_REDIS_DIRECT_CALLS = (
    "xadd",
    "hset",
    "hmset",
    "setex",
    "mset",
    "publish",
    "rpush",
    "lpush",
    "zadd",
)

REDIS_RECEIVER_EXACT_NAMES = (
    "r",
    "rds",
    "redis",
    "redisx",
    "redis_client",
    "redis_conn",
    "redis_connection",
    "live_redis",
    "live_redis_client",
)

REDIS_RECEIVER_SUBSTRINGS = (
    "redis",
    "redisx",
)

BANNED_RUNTIME_VALUES = (
    "live",
    "real_live",
    "paper",
    "paper_armed",
    "armed",
    "execution_armed",
)


def project_root() -> Path:
    start = Path(__file__).resolve()
    for parent in [start.parent, *start.parents]:
        if (parent / "app" / "mme_scalpx").exists():
            return parent
    return Path.cwd().resolve()


PROJECT_ROOT = project_root()
REPLAY_ARTIFACT_ROOT = PROJECT_ROOT / "run" / "replay"
REPLAY_CONFIG_ROOT = PROJECT_ROOT / "etc" / "replay"


def _as_path(path: str | os.PathLike[str] | Path) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p.resolve()


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root.resolve())
        return True
    except ValueError:
        return False


def assert_under_root(
    path: str | os.PathLike[str] | Path,
    root: str | os.PathLike[str] | Path,
    *,
    label: str,
) -> Path:
    resolved = _as_path(path)
    root_path = _as_path(root)
    if not _is_under(resolved, root_path):
        raise ReplaySafetyViolation(
            f"{label} must stay under {root_path}; got {resolved}"
        )
    return resolved


def assert_replay_artifact_path(path: str | os.PathLike[str] | Path) -> Path:
    return assert_under_root(path, REPLAY_ARTIFACT_ROOT, label="replay artifact path")


def assert_replay_config_path(path: str | os.PathLike[str] | Path) -> Path:
    return assert_under_root(path, REPLAY_CONFIG_ROOT, label="replay config path")


def assert_replay_key(key: str) -> str:
    if not isinstance(key, str):
        raise ReplaySafetyViolation(f"replay key must be str; got {type(key).__name__}")
    if not key.startswith(REPLAY_KEY_PREFIXES):
        raise ReplaySafetyViolation(
            f"replay key must be replay-namespaced with {REPLAY_KEY_PREFIXES}; got {key!r}"
        )
    return key


def assert_runtime_mode_not_promoted(runtime_mode: Any) -> Any:
    if runtime_mode is None:
        return runtime_mode
    value = str(runtime_mode).strip().lower()
    if value in BANNED_RUNTIME_VALUES:
        raise ReplaySafetyViolation(
            f"replay cannot promote runtime mode to {runtime_mode!r}"
        )
    return runtime_mode


def assert_replay_runtime_safety(
    *,
    runtime_mode: Any | None = None,
    artifact_path: str | os.PathLike[str] | Path | None = None,
    config_path: str | os.PathLike[str] | Path | None = None,
    redis_key: str | None = None,
) -> bool:
    if runtime_mode is not None:
        assert_runtime_mode_not_promoted(runtime_mode)
    if artifact_path is not None:
        assert_replay_artifact_path(artifact_path)
    if config_path is not None:
        assert_replay_config_path(config_path)
    if redis_key is not None:
        assert_replay_key(redis_key)
    return True


def replay_python_paths(*, include_bins: bool = True, include_proofs: bool = False) -> list[Path]:
    paths: list[Path] = []

    replay_dir = PROJECT_ROOT / "app" / "mme_scalpx" / "replay"
    if replay_dir.exists():
        paths.extend(sorted(replay_dir.rglob("*.py")))

    if include_bins:
        bin_dir = PROJECT_ROOT / "bin"
        if bin_dir.exists():
            for p in sorted(bin_dir.glob("*replay*.py")):
                if not include_proofs and p.name.startswith("proof_"):
                    continue
                paths.append(p)

    return sorted(set(paths))


def _import_name_matches(name: str, prefixes: Iterable[str]) -> bool:
    return any(name == prefix or name.startswith(prefix + ".") for prefix in prefixes)


def _target_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _constant_text(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _receiver_text(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _receiver_text(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return _receiver_text(node.func)
    if isinstance(node, ast.Subscript):
        return _receiver_text(node.value)
    return ""


def _receiver_looks_like_redis(receiver: str) -> bool:
    if not receiver:
        return False
    lowered = receiver.lower()
    parts = [p for p in lowered.replace("[", ".").replace("]", ".").split(".") if p]
    if any(part in REDIS_RECEIVER_EXACT_NAMES for part in parts):
        return True
    return any(substr in lowered for substr in REDIS_RECEIVER_SUBSTRINGS)


def scan_python_static_violations(
    paths: Iterable[str | os.PathLike[str] | Path],
    *,
    categories: set[str] | None = None,
) -> list[dict[str, Any]]:
    active_categories = categories or {"broker", "redis_write", "runtime_promotion"}
    violations: list[dict[str, Any]] = []

    for raw_path in paths:
        path = _as_path(raw_path)
        if not path.exists() or not path.is_file() or path.suffix != ".py":
            continue

        # safety.py carries policy constants such as banned method names.
        # Do not classify policy strings as executable violations.
        if path.name == "safety.py":
            continue

        # Proof files are allowed to mention forbidden tokens while proving they
        # are absent elsewhere. Runtime replay paths are scanned separately.
        if path.name.startswith("proof_"):
            continue

        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            violations.append(
                {
                    "category": "syntax",
                    "file": str(path.relative_to(PROJECT_ROOT)),
                    "line": getattr(exc, "lineno", None),
                    "detail": str(exc),
                }
            )
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    if "broker" in active_categories and _import_name_matches(
                        name,
                        BANNED_BROKER_IMPORT_PREFIXES,
                    ):
                        violations.append(
                            {
                                "category": "broker_import",
                                "file": str(path.relative_to(PROJECT_ROOT)),
                                "line": getattr(node, "lineno", None),
                                "detail": name,
                            }
                        )
                    if "redis_write" in active_categories and _import_name_matches(
                        name,
                        BANNED_REDIS_IMPORT_PREFIXES,
                    ):
                        violations.append(
                            {
                                "category": "redis_import",
                                "file": str(path.relative_to(PROJECT_ROOT)),
                                "line": getattr(node, "lineno", None),
                                "detail": name,
                            }
                        )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if "broker" in active_categories and _import_name_matches(
                    module,
                    BANNED_BROKER_IMPORT_PREFIXES,
                ):
                    violations.append(
                        {
                            "category": "broker_import",
                            "file": str(path.relative_to(PROJECT_ROOT)),
                            "line": getattr(node, "lineno", None),
                            "detail": module,
                        }
                    )
                if "redis_write" in active_categories and _import_name_matches(
                    module,
                    BANNED_REDIS_IMPORT_PREFIXES,
                ):
                    violations.append(
                        {
                            "category": "redis_import",
                            "file": str(path.relative_to(PROJECT_ROOT)),
                            "line": getattr(node, "lineno", None),
                            "detail": module,
                        }
                    )

            if isinstance(node, ast.Call):
                call_name = _target_name(node.func)

                if "broker" in active_categories and call_name in BANNED_BROKER_CALL_NAMES:
                    violations.append(
                        {
                            "category": "broker_call",
                            "file": str(path.relative_to(PROJECT_ROOT)),
                            "line": getattr(node, "lineno", None),
                            "detail": call_name,
                        }
                    )

                if "redis_write" in active_categories:
                    if isinstance(node.func, ast.Attribute):
                        receiver = _receiver_text(node.func.value)
                        if (
                            call_name in BANNED_REDIS_WRITE_ATTR_CALLS
                            and _receiver_looks_like_redis(receiver)
                        ):
                            violations.append(
                                {
                                    "category": "redis_write_call",
                                    "file": str(path.relative_to(PROJECT_ROOT)),
                                    "line": getattr(node, "lineno", None),
                                    "detail": f"{receiver}.{call_name}",
                                }
                            )
                    elif isinstance(node.func, ast.Name):
                        if call_name in BANNED_REDIS_DIRECT_CALLS:
                            violations.append(
                                {
                                    "category": "redis_write_call",
                                    "file": str(path.relative_to(PROJECT_ROOT)),
                                    "line": getattr(node, "lineno", None),
                                    "detail": call_name,
                                }
                            )

            if "runtime_promotion" in active_categories:
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    if isinstance(node, ast.Assign):
                        targets = list(node.targets)
                        value = node.value
                    else:
                        targets = [node.target]
                        value = node.value

                    value_text = _constant_text(value) if value is not None else None
                    if value_text and value_text.strip().lower() in BANNED_RUNTIME_VALUES:
                        for target in targets:
                            target_name = _target_name(target)
                            if target_name in {
                                "runtime_mode",
                                "mode",
                                "paper_armed",
                                "live_trading",
                                "execution_armed",
                            }:
                                violations.append(
                                    {
                                        "category": "runtime_promotion",
                                        "file": str(path.relative_to(PROJECT_ROOT)),
                                        "line": getattr(node, "lineno", None),
                                        "detail": f"{target_name}={value_text!r}",
                                    }
                                )

                    if isinstance(value, ast.Constant) and value.value is True:
                        for target in targets:
                            target_name = _target_name(target)
                            if target_name in {"paper_armed", "live_trading", "execution_armed"}:
                                violations.append(
                                    {
                                        "category": "runtime_promotion",
                                        "file": str(path.relative_to(PROJECT_ROOT)),
                                        "line": getattr(node, "lineno", None),
                                        "detail": f"{target_name}=True",
                                    }
                                )

    return violations


def assert_no_static_violations(
    paths: Iterable[str | os.PathLike[str] | Path],
    *,
    categories: set[str] | None = None,
) -> bool:
    violations = scan_python_static_violations(paths, categories=categories)
    if violations:
        raise ReplaySafetyViolation(f"replay safety static violations: {violations}")
    return True


def assert_replay_module_static_safety(path: str | os.PathLike[str] | Path) -> bool:
    p = _as_path(path)
    if p.name.startswith("proof_"):
        return True
    return assert_no_static_violations(
        [p],
        categories={"broker", "redis_write", "runtime_promotion"},
    )
