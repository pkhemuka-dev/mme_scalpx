# LANE-B-R3B_FILL_MODEL_ABI_AND_R4_COMMAND_CORRECTION_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141930
2026-06-07T14:19:30+05:30

LAW=ABI_AUDIT_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## R3A proof
R3A=run/proofs/LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805.json
{
  "tag": "LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805",
  "classification": "PASS_R3A_EXACT_R4_SHADOW_REPLAY_PLAN_READY",
  "patch_applied": false,
  "replay_executed": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "dataset_root": "run/replay/staging/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337",
  "planned_run_root": "run/replay/lane_b_r4/LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805",
  "report": "run/audits/LANE-B-R3A_EXACT_RISK_EXECUTION_SHADOW_REPLAY_PLAN_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141805_report.md"
}

## replay_run.py fill imports and resolver
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mme_scalpx.replay.artifacts import ReplayArtifactsWriter
from app.mme_scalpx.replay.clock import ReplayClock, ReplayClockConfig
from app.mme_scalpx.replay.contracts import ProfilesSection
from app.mme_scalpx.replay.dataset import DatasetDiscoveryConfig, ReplayDatasetRepository
from app.mme_scalpx.replay.engine import ReplayEngine
from app.mme_scalpx.replay.fill_model import (
    ReplayFillModelConfig,
    ReplayFillModelFactory,
    ReplayFillRequest,
)
from app.mme_scalpx.replay.injector import (
    ReplayInjectionEvent,
    ReplayInjector,
)
from app.mme_scalpx.replay.integrity import (
    ReplayIntegrityEvaluator,
    placeholder_pass_check,
    integrity_bundle_to_dict,
    INTEGRITY_CHECK_HASH_FRESHNESS,
    INTEGRITY_CHECK_HEARTBEAT,
    INTEGRITY_CHECK_REPRODUCIBILITY,
    INTEGRITY_CHECK_RESET_CLEANLINESS,
    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    INTEGRITY_CHECK_STALE_LEG,
    ReplayIntegrityCheckResult,
    IntegrityVerdict,
)


    return outputs



def _resolve_fill_model_name(fill_model_name: str | None) -> str:
    if fill_model_name:
        return fill_model_name
    return ReplayFillModelFactory.IMMEDIATE_MARKET


def _risk_action_to_fill_side(risk_action: str) -> str | None:
    if risk_action in ("ENTER_CALL", "ENTER_PUT"):
        return "BUY"
    return None


def build_execution_shadow_results_from_risk_outputs(
    *,
    run_id: str,
    risk_outputs: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    fill_model_name: str | None,
    doctrine_mode: DoctrineMode,
) -> list[dict[str, Any]]:
    ordered_outputs = sorted(
        risk_outputs,
        key=lambda output: (
            str(output.get("event_time") or ""),
            str(output.get("risk_channel") or ""),
            str(output.get("risk_id") or ""),
        ),
    )

    model = ReplayFillModelFactory.create(
        ReplayFillModelConfig(
            model_name=_resolve_fill_model_name(fill_model_name),
            doctrine_mode=doctrine_mode,
        )
    )

    results: list[dict[str, Any]] = []
    for index, risk_output in enumerate(ordered_outputs, start=1):
        risk_action = str(risk_output.get("risk_action") or "HOLD")
        veto_entry = bool(risk_output.get("veto_entry"))
        side = _risk_action_to_fill_side(risk_action)

        if veto_entry or side is None:
            results.append(
                {
                    "execution_id": f"execution_shadow_{index:06d}",
                    "event_time": risk_output.get("event_time"),
                    "execution_channel": "replay:execution_shadow",
                    "source_risk_id": risk_output.get("risk_id"),
                    "risk_action": risk_action,
                    "filled": False,
                    "fill_qty": 0,
                    "fill_price": None,
                    "slippage": None,
                    "reason": "risk_block_or_non_entry",
                    "symbol": risk_output.get("symbol"),
                    "metadata": dict(risk_output.get("metadata") or {}),

## replay_run.py execution-shadow bridge
                "run_id": context.run_id,
                "mode": "replay_risk_bridge",
                "source_strategy_decisions": len(strategy_decisions),
                "risk_outputs_published": published_count,
                "risk_channel": "replay:risk",
                "risk_action_breakdown": risk_action_breakdown,
                "vetoed_entries": vetoed_entries,
            }

        if stage.stage_name == "execution_shadow":
            risk_outputs = transport.risk_outputs
            execution_results = build_execution_shadow_results_from_risk_outputs(
                run_id=context.run_id,
                risk_outputs=risk_outputs,
                fill_model_name=fill_model_name,
                doctrine_mode=doctrine_mode,
            )

            published_count = 0
            filled_count = 0
            for execution_result in execution_results:
                transport.publish_execution_shadow_result(execution_result)
                published_count += 1
                if bool(execution_result.get("filled")):
                    filled_count += 1

            return {
                "stage_name": stage.stage_name,
                "status": "ok",
                "mode": "replay_execution_shadow_bridge",
                "run_id": context.run_id,
                "source_risk_outputs": len(risk_outputs),
                "execution_results_published": published_count,
                "filled_count": filled_count,
                "execution_channel": "replay:execution_shadow",
                "fill_model_name": _resolve_fill_model_name(fill_model_name),
            }

        return {
            "stage_name": stage.stage_name,
            "status": "ok",

## fill_model.py public defs/classes
2:app/mme_scalpx/replay/fill_model.py
39:class ReplayFillModelError(RuntimeError):
43:class ReplayFillModelValidationError(ReplayFillModelError):
48:class ReplayFillRequest:
68:class ReplayFillResult:
74:    model_name: str
84:class ReplayFillModelConfig:
89:    model_name: str
95:class ReplayFillModel(Protocol):
100:class ImmediateMarketFillModel:
123:                model_name=self._config.model_name,
139:            model_name=self._config.model_name,
149:class LimitTouchFillModel:
176:                model_name=self._config.model_name,
192:            model_name=self._config.model_name,
202:class ReplayFillModelFactory:
217:        if config.model_name == cls.IMMEDIATE_MARKET:
218:            return ImmediateMarketFillModel(config)
219:        if config.model_name == cls.LIMIT_TOUCH:
220:            return LimitTouchFillModel(config)
223:            f"unsupported fill model name: {config.model_name!r}"
227:def fill_request_to_dict(request: ReplayFillRequest) -> dict[str, Any]:
242:def fill_result_to_dict(result: ReplayFillResult) -> dict[str, Any]:
245:        "model_name": result.model_name,
255:def _validate_config(config: ReplayFillModelConfig) -> None:
256:    if not isinstance(config.model_name, str) or not config.model_name.strip():
258:            f"model_name must be non-empty string, got {config.model_name!r}"
271:def _validate_request(request: ReplayFillRequest) -> None:
294:def _resolve_immediate_market_fill_price(request: ReplayFillRequest) -> float | None:
304:def _resolve_limit_touch_fill_price(request: ReplayFillRequest) -> float | None:
319:__all__ = [
326:    "ImmediateMarketFillModel",
327:    "LimitTouchFillModel",
333:# BEGIN BATCH27I_REPLAY_FILL_MODEL_SHADOW_HELPERS
335:def replay_fill_model_shadow_assumption_profiles():
340:        "schema_version": "replay_fill_model_shadow_assumption_profiles_v1",
350:    __all__
352:    __all__ = tuple()
354:__all__ = tuple(dict.fromkeys(tuple(__all__) + (
355:    "replay_fill_model_shadow_assumption_profiles",
358:# END BATCH27I_REPLAY_FILL_MODEL_SHADOW_HELPERS

## fill_model.py factory area
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReplayFillModelConfig:
    """
    Canonical fill model config.
    """

    model_name: str
    doctrine_mode: DoctrineMode
    allow_partial_fills: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


class ReplayFillModel(Protocol):
    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
        ...


class ImmediateMarketFillModel:
    """
    Replay-only model:
    - BUY fills at best_ask if present, else market_price
    - SELL fills at best_bid if present, else market_price
    - full fill only
    """

    def __init__(self, config: ReplayFillModelConfig) -> None:
        _validate_config(config)
        self._config = config

    @property
    def config(self) -> ReplayFillModelConfig:
        return self._config

    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
        _validate_request(request)

        fill_price = _resolve_immediate_market_fill_price(request)
        if fill_price is None:
            return ReplayFillResult(
                order_id=request.order_id,
                model_name=self._config.model_name,
                filled=False,
                fill_qty=0,
                fill_price=None,
                slippage=None,
                reason="no_fill_price_available",
                metadata={},
            )

        reference = request.market_price
        slippage = None
        if reference is not None:
            slippage = fill_price - reference

        return ReplayFillResult(
            order_id=request.order_id,
            model_name=self._config.model_name,
            filled=True,
            fill_qty=request.qty,
            fill_price=fill_price,
            slippage=slippage,
            reason="immediate_market_fill",
            metadata={},
        )


class LimitTouchFillModel:
    """
    Replay-only model:
    - BUY fills if market/ask <= order_price
    - SELL fills if market/bid >= order_price
    - full fill only
    """

    def __init__(self, config: ReplayFillModelConfig) -> None:
        _validate_config(config)
        self._config = config

    @property
    def config(self) -> ReplayFillModelConfig:
        return self._config

    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
        _validate_request(request)
        if request.order_price is None:
            raise ReplayFillModelValidationError(
                "limit-touch fill model requires order_price"
            )

        fill_price = _resolve_limit_touch_fill_price(request)
        if fill_price is None:
            return ReplayFillResult(
                order_id=request.order_id,
                model_name=self._config.model_name,
                filled=False,
                fill_qty=0,
                fill_price=None,
                slippage=None,
                reason="limit_not_touched",
                metadata={},
            )

        reference = request.market_price
        slippage = None
        if reference is not None:
            slippage = fill_price - reference

        return ReplayFillResult(
            order_id=request.order_id,
            model_name=self._config.model_name,
            filled=True,
            fill_qty=request.qty,
            fill_price=fill_price,
            slippage=slippage,
            reason="limit_touch_fill",
            metadata={},
        )


class ReplayFillModelFactory:
    """
    Freeze-grade replay fill model factory.
    """

    IMMEDIATE_MARKET = "immediate_market"
    LIMIT_TOUCH = "limit_touch"

    @classmethod
    def create(
        cls,
        config: ReplayFillModelConfig,
    ) -> ReplayFillModel:
        _validate_config(config)

        if config.model_name == cls.IMMEDIATE_MARKET:
            return ImmediateMarketFillModel(config)
        if config.model_name == cls.LIMIT_TOUCH:
            return LimitTouchFillModel(config)

        raise ReplayFillModelValidationError(
            f"unsupported fill model name: {config.model_name!r}"
        )


def fill_request_to_dict(request: ReplayFillRequest) -> dict[str, Any]:
    return {
        "run_id": request.run_id,
        "order_id": request.order_id,

## Import actual exported names
ImmediateMarketFillModel
LimitTouchFillModel
ReplayFillModel
ReplayFillModelConfig
ReplayFillModelError
ReplayFillModelFactory
ReplayFillModelValidationError
ReplayFillRequest
ReplayFillResult
fill_request_to_dict
fill_result_to_dict
replay_fill_model_shadow_assumption_profiles
IMPORT_RC=0

CLASSIFICATION=PASS_R3B_FILL_MODEL_ABI_VISIBLE_READY_TO_REWRITE_R4_COMMAND
