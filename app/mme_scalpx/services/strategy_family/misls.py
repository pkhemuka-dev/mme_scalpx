from __future__ import annotations

"""
app/mme_scalpx/services/strategy_family/misls.py

MISLS = Market Imbalance Stop/Liquidity Sweep Strategy.

Freeze-grade dormant shadow validator.

Safety law:
- no Redis read/write/delete
- no broker call
- no paper/live order
- no risk/execution mutation
- no candidate promotion
- always HOLD
- shadow candidate only inside metadata
"""

import math
from dataclasses import dataclass, field
from typing import Any, Final, Mapping

from app.mme_scalpx.core import names as N


FAMILY_ID: Final[str] = getattr(N, "STRATEGY_FAMILY_MISLS", "MISLS")
DOCTRINE_ID: Final[str] = getattr(N, "DOCTRINE_MISLS", FAMILY_ID)

BRANCH_CALL: Final[str] = getattr(N, "BRANCH_CALL", "CALL")
BRANCH_PUT: Final[str] = getattr(N, "BRANCH_PUT", "PUT")
SIDE_CALL: Final[str] = getattr(N, "SIDE_CALL", "CALL")
SIDE_PUT: Final[str] = getattr(N, "SIDE_PUT", "PUT")

ACTION_HOLD: Final[str] = getattr(N, "ACTION_HOLD", "HOLD")
ACTION_ENTER_CALL: Final[str] = getattr(N, "ACTION_ENTER_CALL", "ENTER_CALL")
ACTION_ENTER_PUT: Final[str] = getattr(N, "ACTION_ENTER_PUT", "ENTER_PUT")

SUPPORTED_BRANCHES: Final[tuple[str, str]] = (BRANCH_CALL, BRANCH_PUT)
ALLOW_REGISTRY_NOOP_FALLBACK: Final[bool] = False

FULL_CALL: Final[str] = "FULL_MISLS_R3_CALL_CANDIDATE"
FULL_PUT: Final[str] = "FULL_MISLS_R3_PUT_CANDIDATE"

TERMINAL_FULL_BY_BRANCH: Final[Mapping[str, str]] = {
    BRANCH_CALL: FULL_CALL,
    BRANCH_PUT: FULL_PUT,
}

FORBIDDEN_POSITIVE_FIELDS: Final[tuple[str, ...]] = (
    "orders_stream_count",
    "risk_stream_count",
    "execution_stream_count",
    "paper_order_stream_count",
    "broker_order_api_call_count",
    "paper_order_count",
    "live_order_count",
    "position_change_count",
    "redis_delete_count",
    "lock_delete_count",
)

FORBIDDEN_TRUTHY_FIELDS: Final[tuple[str, ...]] = (
    "order_requested",
    "order_sent",
    "paper_order_requested",
    "paper_order_sent",
    "risk_start_requested",
    "execution_start_requested",
    "risk_event_emitted",
    "execution_event_emitted",
    "broker_order_api_called",
)

TRADE_ACTIONS: Final[tuple[str, ...]] = (
    ACTION_ENTER_CALL,
    ACTION_ENTER_PUT,
    "ENTER",
    "BUY",
    "SELL",
)


def safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip() or default
    text = str(value).strip()
    return text if text else default


def safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = safe_str(value).lower()
    if text in {"1", "true", "yes", "y", "on", "ok", "pass", "passed", "available", "armed"}:
        return True
    if text in {"0", "false", "no", "n", "off", "fail", "failed", "none", "null", "disabled"}:
        return False
    return default


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        out = float(str(value).strip())
    except Exception:
        return default
    return out if math.isfinite(out) else default


def as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        try:
            out = value.to_dict()
            if isinstance(out, Mapping):
                return dict(out)
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        return dict(vars(value))
    return {}


def normalize_branch(value: Any) -> str | None:
    text = safe_str(value).upper()
    if text in {"CALL", "CE", "C", BRANCH_CALL}:
        return BRANCH_CALL
    if text in {"PUT", "PE", "P", BRANCH_PUT}:
        return BRANCH_PUT
    return None


def side_for_branch(branch_id: str) -> str:
    return SIDE_CALL if branch_id == BRANCH_CALL else SIDE_PUT


def normalize_score(value: Any) -> float:
    raw = safe_float(value, 0.0)
    if 1.0 < raw <= 100.0:
        return max(0.0, min(1.0, raw / 100.0))
    return max(0.0, min(1.0, raw))


@dataclass(frozen=True, slots=True)
class MislsBlocker:
    code: str
    message: str
    severity: str = "BLOCK"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class MislsEvaluationResult:
    family_id: str
    doctrine_id: str
    branch_id: str | None
    action: str
    is_candidate: bool
    is_blocked: bool
    candidate: None = None
    blocker: MislsBlocker | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def is_no_signal(self) -> bool:
        return not self.is_candidate and not self.is_blocked

    def to_dict(self) -> dict[str, Any]:
        return {
            "family_id": self.family_id,
            "doctrine_id": self.doctrine_id,
            "branch_id": self.branch_id,
            "action": self.action,
            "is_candidate": self.is_candidate,
            "is_blocked": self.is_blocked,
            "is_no_signal": self.is_no_signal,
            "candidate": None,
            "blocker": self.blocker.to_dict() if self.blocker else None,
            "metadata": dict(self.metadata),
        }


def no_signal_result(branch_id: str | None, reason: str, metadata: Mapping[str, Any] | None = None) -> MislsEvaluationResult:
    return MislsEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        action=ACTION_HOLD,
        is_candidate=False,
        is_blocked=False,
        metadata={"reason": reason, **dict(metadata or {})},
    )


def blocked_result(
    branch_id: str | None,
    code: str,
    message: str,
    metadata: Mapping[str, Any] | None = None,
) -> MislsEvaluationResult:
    return MislsEvaluationResult(
        family_id=FAMILY_ID,
        doctrine_id=DOCTRINE_ID,
        branch_id=branch_id,
        action=ACTION_HOLD,
        is_candidate=False,
        is_blocked=True,
        blocker=MislsBlocker(code=code, message=message, metadata=dict(metadata or {})),
        metadata={"reason": code, **dict(metadata or {})},
    )



def _extend_misls_candidates(candidates: list[dict[str, Any]], value: Any) -> None:
    if isinstance(value, (list, tuple)):
        for item in value:
            _extend_misls_candidates(candidates, item)
        return

    item = as_mapping(value)
    if not item:
        return

    for child_key in ("events", "candidates", "shadow_candidates"):
        child = item.get(child_key)
        if isinstance(child, (list, tuple)):
            for row in child:
                row_map = as_mapping(row)
                if row_map:
                    candidates.append(row_map)
        else:
            child_map = as_mapping(child)
            if child_map:
                candidates.append(child_map)

    branch = normalize_branch(
        item.get("branch_id")
        or item.get("side")
        or item.get("option_type")
        or item.get("selected_option_type")
    )
    final_classification = safe_str(item.get("final_classification"))
    event_id = safe_str(item.get("event_id"))
    family = safe_str(item.get("family_id") or item.get("strategy_family")).upper()

    if branch or final_classification or event_id or family == FAMILY_ID:
        candidates.append(item)


def extract_event(view_like: Any, branch_id: str) -> dict[str, Any]:
    view = as_mapping(view_like)

    candidates: list[dict[str, Any]] = []

    _extend_misls_candidates(candidates, view)
    _extend_misls_candidates(candidates, view.get("misls"))

    for root_key in ("research", "metadata"):
        root = as_mapping(view.get(root_key))
        if not root:
            continue
        _extend_misls_candidates(candidates, root.get("misls"))
        _extend_misls_candidates(candidates, root.get("MISLS"))
        _extend_misls_candidates(candidates, root.get(FAMILY_ID))

    for root_key in ("family_surfaces", "family_features", "families"):
        root = as_mapping(view.get(root_key))
        if not root:
            continue
        _extend_misls_candidates(candidates, root.get(FAMILY_ID))
        _extend_misls_candidates(candidates, root.get("MISLS"))
        _extend_misls_candidates(candidates, root.get("misls"))

    clean: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in candidates:
        item = as_mapping(item)
        if not item:
            continue
        identity = (
            safe_str(item.get("event_id")),
            safe_str(item.get("candidate_id")),
            safe_str(item.get("final_classification")),
        )
        if identity in seen and any(identity):
            continue
        seen.add(identity)
        clean.append(item)

    for item in clean:
        item_branch = normalize_branch(
            item.get("branch_id")
            or item.get("side")
            or item.get("option_type")
            or item.get("selected_option_type")
        )
        if item_branch == branch_id:
            return item

    for item in clean:
        final_classification = safe_str(item.get("final_classification"))
        if branch_id == BRANCH_CALL and final_classification == FULL_CALL:
            return item
        if branch_id == BRANCH_PUT and final_classification == FULL_PUT:
            return item

    return {}


def safety_guard(event: Mapping[str, Any]) -> tuple[bool, str | None]:
    for key in FORBIDDEN_POSITIVE_FIELDS:
        if safe_float(event.get(key), 0.0) > 0.0:
            return False, f"FAIL_SAFETY_BREACH:{key}"

    for key in FORBIDDEN_TRUTHY_FIELDS:
        if safe_bool(event.get(key), False) is True:
            return False, f"FAIL_SAFETY_BREACH:{key}"

    action = safe_str(event.get("action") or event.get("action_hint")).upper()
    if action in TRADE_ACTIONS:
        return False, "MISLS_TRADE_ACTION_FORBIDDEN"

    return True, None


def mandatory_fields(event: Mapping[str, Any]) -> tuple[bool, str | None]:
    if not safe_str(event.get("event_id")):
        return False, "FAIL_EVENT_ID_BLANK"

    candidate_id = safe_str(event.get("candidate_id"))
    if not candidate_id or candidate_id.upper() == "NONE":
        return False, "FAIL_CANDIDATE_ID_BLANK"

    for key in ("shadow_entry_price", "shadow_entry_underlying_price"):
        if key not in event or event.get(key) in (None, ""):
            return False, f"MISLS_{key.upper()}_MISSING"

    return True, None


def quote_ok(event: Mapping[str, Any]) -> tuple[bool, str | None]:
    required = (
        "selected_option_bid_post",
        "selected_option_ask_post",
        "selected_option_bid_qty_post",
        "selected_option_ask_qty_post",
        "selected_option_quote_age_ms",
        "paired_option_bid_post",
        "paired_option_ask_post",
        "paired_option_bid_qty_post",
        "paired_option_ask_qty_post",
    )

    for key in required:
        if key not in event or event.get(key) in (None, ""):
            return False, "OPTION_QUOTE_MISSING"

    bid = safe_float(event.get("selected_option_bid_post"))
    ask = safe_float(event.get("selected_option_ask_post"))
    p_bid = safe_float(event.get("paired_option_bid_post"))
    p_ask = safe_float(event.get("paired_option_ask_post"))

    if bid <= 0.0 or ask <= 0.0 or ask <= bid:
        return False, "OPTION_QUOTE_MISSING"
    if p_bid <= 0.0 or p_ask <= 0.0 or p_ask <= p_bid:
        return False, "OPTION_QUOTE_MISSING"

    if safe_float(event.get("selected_option_bid_qty_post")) <= 0.0:
        return False, "OPTION_QUOTE_ZERO_QTY"
    if safe_float(event.get("selected_option_ask_qty_post")) <= 0.0:
        return False, "OPTION_QUOTE_ZERO_QTY"
    if safe_float(event.get("paired_option_bid_qty_post")) <= 0.0:
        return False, "OPTION_QUOTE_ZERO_QTY"
    if safe_float(event.get("paired_option_ask_qty_post")) <= 0.0:
        return False, "OPTION_QUOTE_ZERO_QTY"

    if safe_float(event.get("selected_option_quote_age_ms"), 999999.0) > 250.0:
        return False, "OPTION_QUOTE_STALE"

    return True, None


def evaluate_branch(view_like: Any, branch_id: str) -> MislsEvaluationResult:
    branch_id = normalize_branch(branch_id) or ""
    if branch_id not in SUPPORTED_BRANCHES:
        return no_signal_result(None, "unsupported_branch")

    event = extract_event(view_like, branch_id)
    if not event:
        return no_signal_result(branch_id, "misls_surface_missing")

    safe, reason = safety_guard(event)
    if not safe:
        return blocked_result(branch_id, reason or "MISLS_SAFETY_GUARD_FAILED", "MISLS event contains forbidden trade/risk/execution surface.", {"event_id": safe_str(event.get("event_id"))})

    expected = TERMINAL_FULL_BY_BRANCH[branch_id]
    if safe_str(event.get("final_classification")) != expected:
        return no_signal_result(branch_id, "misls_not_full_shadow_candidate", {"expected": expected, "actual": safe_str(event.get("final_classification"))})

    ok, reason = mandatory_fields(event)
    if not ok:
        return blocked_result(branch_id, reason or "MISLS_FIELD_MISSING", "MISLS full shadow candidate is missing mandatory fields.", {"event_id": safe_str(event.get("event_id"))})

    ok, reason = quote_ok(event)
    if not ok:
        return no_signal_result(branch_id, reason or "misls_quote_integrity_failed", {"event_id": safe_str(event.get("event_id"))})

    score = normalize_score(event.get("score", event.get("score_total", 0.0)))
    shadow_candidate = {
        "family_id": FAMILY_ID,
        "doctrine_id": DOCTRINE_ID,
        "branch_id": branch_id,
        "side": side_for_branch(branch_id),
        "action": ACTION_HOLD,
        "score": score,
        "priority": round(score * 100.0, 6),
        "event_id": safe_str(event.get("event_id")),
        "candidate_id": safe_str(event.get("candidate_id")),
        "candidate_direction": "LONG_CALL_SHADOW_ONLY" if branch_id == BRANCH_CALL else "LONG_PUT_SHADOW_ONLY",
        "research_only": True,
        "shadow_only": True,
        "no_order": True,
        "no_paper": True,
        "no_risk": True,
        "no_execution": True,
    }

    return blocked_result(
        branch_id,
        "MISLS_RESEARCH_ONLY_NO_PROMOTION",
        "MISLS full candidate is research-only and cannot be promoted by this module.",
        {
            "event_id": shadow_candidate["event_id"],
            "candidate_id": shadow_candidate["candidate_id"],
            "score": score,
            "research_only": True,
            "shadow_only": True,
            "is_trade_promotable": False,
            "shadow_candidate": shadow_candidate,
            "misls_shadow_candidate_ready": True,
        },
    )


def evaluate(view_like: Any, branch_id: str | None = None) -> MislsEvaluationResult:
    branch = normalize_branch(branch_id)
    if branch:
        return evaluate_branch(view_like, branch)

    call_result = evaluate_branch(view_like, BRANCH_CALL)
    put_result = evaluate_branch(view_like, BRANCH_PUT)

    if call_result.is_blocked and call_result.metadata.get("misls_shadow_candidate_ready"):
        return call_result
    if put_result.is_blocked and put_result.metadata.get("misls_shadow_candidate_ready"):
        return put_result

    return no_signal_result(None, "misls_no_branch_signal", {"call": call_result.to_dict(), "put": put_result.to_dict()})


def evaluate_family(view_like: Any) -> MislsEvaluationResult:
    return evaluate(view_like)


def evaluate_doctrine(view_like: Any, branch_id: str | None = None) -> MislsEvaluationResult:
    return evaluate(view_like, branch_id=branch_id)


def get_evaluator():
    return evaluate_doctrine


__all__ = [
    "FAMILY_ID",
    "DOCTRINE_ID",
    "SUPPORTED_BRANCHES",
    "MislsBlocker",
    "MislsEvaluationResult",
    "evaluate_branch",
    "evaluate",
    "evaluate_family",
    "evaluate_doctrine",
    "get_evaluator",
]
