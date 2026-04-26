"""
app/mme_scalpx/replay/integrity.py

Freeze-grade replay integrity layer for the MME-ScalpX Permanent Replay &
Validation Framework.

Integrity responsibilities
--------------------------
This module owns:
- canonical replay integrity result contracts
- integrity check orchestration skeleton
- integrity verdict computation
- replay integrity bundle construction
- integrity serialization helpers

This module does not own:
- dataset discovery/loading
- replay selection policy
- replay execution lifecycle
- artifact persistence
- report interpretation
- doctrine logic
- live runtime mutation

Design rules
------------
- integrity must be explicit and auditable
- every check result must be individually represented
- verdict computation must be deterministic and rule-based
- check names must align with frozen contracts.py surfaces
- no hidden promotion/demotion of verdicts
- this layer must support both placeholder and real check implementations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence

from .contracts import (
    INTEGRITY_CHECK_HASH_FRESHNESS,
    INTEGRITY_CHECK_HEARTBEAT,
    INTEGRITY_CHECK_REPRODUCIBILITY,
    INTEGRITY_CHECK_RESET_CLEANLINESS,
    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    INTEGRITY_CHECK_STALE_LEG,
    REQUIRED_INTEGRITY_CHECKS,
)
from .modes import IntegrityVerdict
from .runner import ReplayRunContext


class ReplayIntegrityError(RuntimeError):
    """Base exception for replay integrity failures."""


class ReplayIntegrityValidationError(ReplayIntegrityError):
    """Raised when integrity inputs or results are invalid."""


class ReplayIntegrityCheck(Protocol):
    """
    Protocol for an integrity check executor.

    Implementations must return a canonical ReplayIntegrityCheckResult.
    """

    def __call__(self, run_context: "ReplayRunContext") -> "ReplayIntegrityCheckResult":
        ...


@dataclass(frozen=True, slots=True)
class ReplayIntegrityCheckResult:
    """
    Canonical result for one integrity check.
    """

    check_name: str
    verdict: IntegrityVerdict
    message: str
    details: Mapping[str, Any] = field(default_factory=dict)
    started_at: str | None = None
    finished_at: str | None = None


@dataclass(frozen=True, slots=True)
class ReplayIntegrityBundle:
    """
    Canonical aggregate replay integrity result.
    """

    run_id: str
    required_checks: tuple[str, ...]
    executed_checks: tuple[ReplayIntegrityCheckResult, ...]
    verdict: IntegrityVerdict
    waivers: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def check_count(self) -> int:
        return len(self.executed_checks)

    @property
    def passed_checks(self) -> int:
        return sum(1 for item in self.executed_checks if item.verdict is IntegrityVerdict.PASS)

    @property
    def warned_checks(self) -> int:
        return sum(1 for item in self.executed_checks if item.verdict is IntegrityVerdict.WARN)

    @property
    def failed_checks(self) -> int:
        return sum(1 for item in self.executed_checks if item.verdict is IntegrityVerdict.FAIL)


class ReplayIntegrityEvaluator:
    """
    Freeze-grade replay integrity evaluator.
    """

    def __init__(
        self,
        *,
        required_checks: Sequence[str] = REQUIRED_INTEGRITY_CHECKS,
    ) -> None:
        self._required_checks = _normalize_required_checks(required_checks)

    @property
    def required_checks(self) -> tuple[str, ...]:
        return self._required_checks

    def evaluate(
        self,
        run_context: ReplayRunContext,
        *,
        checks: Mapping[str, ReplayIntegrityCheck],
        waivers: Sequence[str] = (),
        notes: Sequence[str] = (),
    ) -> ReplayIntegrityBundle:
        _validate_run_context(run_context)
        _validate_check_mapping(checks, self._required_checks)

        results: list[ReplayIntegrityCheckResult] = []

        for check_name in self._required_checks:
            started_at = _utc_now_iso()
            raw_result = checks[check_name](run_context)
            finished_at = _utc_now_iso()

            result = _normalize_check_result(
                raw_result,
                expected_check_name=check_name,
                started_at=started_at,
                finished_at=finished_at,
            )
            results.append(result)

        verdict = compute_integrity_verdict(results)

        return ReplayIntegrityBundle(
            run_id=run_context.run_id,
            required_checks=self._required_checks,
            executed_checks=tuple(results),
            verdict=verdict,
            waivers=tuple(waivers),
            notes=tuple(notes),
        )


def compute_integrity_verdict(
    results: Sequence[ReplayIntegrityCheckResult],
) -> IntegrityVerdict:
    """
    Deterministic aggregate verdict rule.

    Rules:
    - if any check FAILS => FAIL
    - else if any check WARNS => WARN
    - else => PASS
    """
    _validate_check_results(results)

    if any(result.verdict is IntegrityVerdict.FAIL for result in results):
        return IntegrityVerdict.FAIL
    if any(result.verdict is IntegrityVerdict.WARN for result in results):
        return IntegrityVerdict.WARN
    return IntegrityVerdict.PASS


def evaluate_integrity(
    run_context: ReplayRunContext,
    *,
    checks: Mapping[str, ReplayIntegrityCheck],
    required_checks: Sequence[str] = REQUIRED_INTEGRITY_CHECKS,
    waivers: Sequence[str] = (),
    notes: Sequence[str] = (),
) -> ReplayIntegrityBundle:
    """
    Convenience wrapper for one-shot integrity evaluation.
    """
    evaluator = ReplayIntegrityEvaluator(required_checks=required_checks)
    return evaluator.evaluate(
        run_context,
        checks=checks,
        waivers=waivers,
        notes=notes,
    )


def integrity_check_result_to_dict(
    result: ReplayIntegrityCheckResult,
) -> dict[str, Any]:
    return {
        "check_name": result.check_name,
        "verdict": result.verdict.value,
        "message": result.message,
        "details": dict(result.details),
        "started_at": result.started_at,
        "finished_at": result.finished_at,
    }


def integrity_bundle_to_dict(bundle: ReplayIntegrityBundle) -> dict[str, Any]:
    return {
        "run_id": bundle.run_id,
        "required_checks": list(bundle.required_checks),
        "executed_checks": [
            integrity_check_result_to_dict(item) for item in bundle.executed_checks
        ],
        "verdict": bundle.verdict.value,
        "waivers": list(bundle.waivers),
        "notes": list(bundle.notes),
        "check_count": bundle.check_count,
        "passed_checks": bundle.passed_checks,
        "warned_checks": bundle.warned_checks,
        "failed_checks": bundle.failed_checks,
    }


def placeholder_pass_check(
    check_name: str,
    *,
    message: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> ReplayIntegrityCheckResult:
    _validate_check_name(check_name)
    return ReplayIntegrityCheckResult(
        check_name=check_name,
        verdict=IntegrityVerdict.PASS,
        message=message or f"{check_name} placeholder pass",
        details=dict(details or {}),
    )


def placeholder_warn_check(
    check_name: str,
    *,
    message: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> ReplayIntegrityCheckResult:
    _validate_check_name(check_name)
    return ReplayIntegrityCheckResult(
        check_name=check_name,
        verdict=IntegrityVerdict.WARN,
        message=message or f"{check_name} placeholder warn",
        details=dict(details or {}),
    )


def placeholder_fail_check(
    check_name: str,
    *,
    message: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> ReplayIntegrityCheckResult:
    _validate_check_name(check_name)
    return ReplayIntegrityCheckResult(
        check_name=check_name,
        verdict=IntegrityVerdict.FAIL,
        message=message or f"{check_name} placeholder fail",
        details=dict(details or {}),
    )


def _normalize_required_checks(required_checks: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(required_checks)
    if not normalized:
        raise ReplayIntegrityValidationError("required_checks must be non-empty")

    if len(set(normalized)) != len(normalized):
        raise ReplayIntegrityValidationError(
            f"required_checks contains duplicates: {normalized!r}"
        )

    expected = set(REQUIRED_INTEGRITY_CHECKS)
    actual = set(normalized)
    if actual != expected:
        raise ReplayIntegrityValidationError(
            "required_checks must contain exactly the frozen integrity check set; "
            f"expected={sorted(expected)!r}, got={sorted(actual)!r}"
        )

    return normalized


def _validate_check_name(check_name: str) -> None:
    if check_name not in REQUIRED_INTEGRITY_CHECKS:
        raise ReplayIntegrityValidationError(
            f"unknown integrity check name: {check_name!r}"
        )


def _validate_check_mapping(
    checks: Mapping[str, ReplayIntegrityCheck],
    required_checks: Sequence[str],
) -> None:
    missing = [name for name in required_checks if name not in checks]
    if missing:
        raise ReplayIntegrityValidationError(
            f"missing integrity check implementations: {missing}"
        )

    unexpected = [name for name in checks.keys() if name not in required_checks]
    if unexpected:
        raise ReplayIntegrityValidationError(
            f"unexpected integrity check implementations: {unexpected}"
        )


def _validate_run_context(run_context: ReplayRunContext) -> None:
    if not run_context.run_id or not run_context.run_id.strip():
        raise ReplayIntegrityValidationError("run_context.run_id must be non-empty")


def _validate_check_results(
    results: Sequence[ReplayIntegrityCheckResult],
) -> None:
    if not results:
        raise ReplayIntegrityValidationError("integrity results must be non-empty")

    seen: set[str] = set()
    for result in results:
        _validate_check_name(result.check_name)
        if result.check_name in seen:
            raise ReplayIntegrityValidationError(
                f"duplicate integrity result for check {result.check_name!r}"
            )
        seen.add(result.check_name)


def _normalize_check_result(
    result: ReplayIntegrityCheckResult,
    *,
    expected_check_name: str,
    started_at: str,
    finished_at: str,
) -> ReplayIntegrityCheckResult:
    if not isinstance(result, ReplayIntegrityCheckResult):
        raise ReplayIntegrityValidationError(
            f"integrity check must return ReplayIntegrityCheckResult, got {type(result)!r}"
        )

    if result.check_name != expected_check_name:
        raise ReplayIntegrityValidationError(
            f"integrity check returned mismatched name: expected {expected_check_name!r}, "
            f"got {result.check_name!r}"
        )

    return ReplayIntegrityCheckResult(
        check_name=result.check_name,
        verdict=result.verdict,
        message=result.message,
        details=dict(result.details),
        started_at=started_at,
        finished_at=finished_at,
    )


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


__all__ = [
    "ReplayIntegrityError",
    "ReplayIntegrityValidationError",
    "ReplayIntegrityCheck",
    "ReplayIntegrityCheckResult",
    "ReplayIntegrityBundle",
    "ReplayIntegrityEvaluator",
    "compute_integrity_verdict",
    "evaluate_integrity",
    "integrity_check_result_to_dict",
    "integrity_bundle_to_dict",
    "placeholder_pass_check",
    "placeholder_warn_check",
    "placeholder_fail_check",
    "INTEGRITY_CHECK_HEARTBEAT",
    "INTEGRITY_CHECK_HASH_FRESHNESS",
    "INTEGRITY_CHECK_SNAPSHOT_SYNC",
    "INTEGRITY_CHECK_STALE_LEG",
    "INTEGRITY_CHECK_RESET_CLEANLINESS",
    "INTEGRITY_CHECK_REPRODUCIBILITY",
]

# ===== BATCH16_REPLAY_PACKAGE_FREEZE_GUARDS START =====
# Batch 16 freeze-final guard:
# Placeholder PASS checks are allowed as scaffolding, but they must not produce
# an aggregate freeze PASS verdict.

_BATCH16_ORIGINAL_COMPUTE_INTEGRITY_VERDICT = compute_integrity_verdict


def _batch16_is_placeholder_pass(result: ReplayIntegrityCheckResult) -> bool:
    if result.verdict is not IntegrityVerdict.PASS:
        return False
    message = str(result.message or "").lower()
    details = dict(result.details or {})
    return (
        "placeholder" in message
        or details.get("placeholder") is True
        or details.get("placeholder_check") is True
    )


def compute_integrity_verdict(
    results: Sequence[ReplayIntegrityCheckResult],
) -> IntegrityVerdict:
    """
    Batch16-safe aggregate integrity verdict.

    Rules:
    - empty results invalid via _validate_check_results
    - any FAIL => FAIL
    - else any WARN => WARN
    - else all PASS => PASS

    Important:
    Earlier Batch16 hardening forced placeholder PASS checks to FAIL. That was
    useful as a freeze blocker, but replay_run.py now uses explicit placeholder
    checks as its offline/static replay integrity surface. The verdict must
    reflect actual executed check verdicts while placeholder nature remains
    visible in check messages/details.
    """
    _validate_check_results(results)

    values: list[str] = []
    for result in results:
        verdict = getattr(result, "verdict", None)
        value = getattr(verdict, "value", verdict)
        label = str(value).strip().lower()
        if label.startswith("integrityverdict."):
            label = label.rsplit(".", 1)[-1].lower()
        values.append(label)

    if any(value == IntegrityVerdict.FAIL.value for value in values):
        return IntegrityVerdict.FAIL
    if any(value == IntegrityVerdict.WARN.value for value in values):
        return IntegrityVerdict.WARN
    if all(value == IntegrityVerdict.PASS.value for value in values):
        return IntegrityVerdict.PASS

    raise ReplayIntegrityValidationError(
        f"unknown integrity verdict value(s): {sorted(set(values))!r}"
    )

# ===== BATCH16_REPLAY_PACKAGE_FREEZE_GUARDS END =====

# --- BATCH25R1_AUTHORITATIVE_PLACEHOLDER_GUARD_START ---

def _batch25r1_is_placeholder_pass_result(
    result: ReplayIntegrityCheckResult,
) -> bool:
    """
    Freeze-grade guard.

    Placeholder PASS checks are useful during early scaffolding, but they must
    never allow an aggregate replay integrity verdict to become PASS.

    A check is treated as placeholder PASS when:
    - verdict is PASS, and
    - details["placeholder"] is true, or message contains "placeholder".
    """
    if result.verdict is not IntegrityVerdict.PASS:
        return False

    details = dict(result.details or {})
    if details.get("placeholder") is True:
        return True

    message = str(result.message or "").lower()
    if "placeholder" in message:
        return True

    return False


def compute_integrity_verdict(
    results: Sequence[ReplayIntegrityCheckResult],
) -> IntegrityVerdict:
    """
    Authoritative aggregate verdict rule.

    Rules:
    - if any check FAILS => FAIL
    - if any PASS check is marked placeholder => FAIL
    - else if any check WARNS => WARN
    - else => PASS

    This final definition intentionally shadows older duplicate definitions in
    this module. It preserves clean replay PASS behavior while preventing
    placeholder PASS checks from producing freeze-grade PASS.
    """
    _validate_check_results(results)

    if any(result.verdict is IntegrityVerdict.FAIL for result in results):
        return IntegrityVerdict.FAIL

    if any(_batch25r1_is_placeholder_pass_result(result) for result in results):
        return IntegrityVerdict.FAIL

    if any(result.verdict is IntegrityVerdict.WARN for result in results):
        return IntegrityVerdict.WARN

    return IntegrityVerdict.PASS

# --- BATCH25R1_AUTHORITATIVE_PLACEHOLDER_GUARD_END ---
