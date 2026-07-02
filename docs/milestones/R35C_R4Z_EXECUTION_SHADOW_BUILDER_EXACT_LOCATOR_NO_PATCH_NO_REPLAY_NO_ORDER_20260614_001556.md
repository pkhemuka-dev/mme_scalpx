# R35C_R4Z_EXECUTION_SHADOW_BUILDER_EXACT_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260614_001556

classification: PASS_R35C_R4Z_EXECUTION_SHADOW_BUILDER_EXACT_LOCATOR_DONE_NO_PATCH_NO_REPLAY_NO_ORDER
proof: `run/proofs/R35C_R4Z_EXECUTION_SHADOW_BUILDER_EXACT_LOCATOR_NO_PATCH_NO_REPLAY_NO_ORDER_20260614_001556.json`

safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=0

## Source locator
## Exact function locator
bin/replay_run.py:2283:def build_execution_shadow_results_from_risk_outputs(
bin/replay_run.py:3202:            execution_results = build_execution_shadow_results_from_risk_outputs(

## All execution shadow builder-like functions
app/mme_scalpx/main.py:120:def _b1_allow_execution_shadow_no_broker() -> bool:
app/mme_scalpx/main.py:135:class _B1ExecutionShadowNoBrokerBroker:
app/mme_scalpx/main.py:167:def _b1_resolve_execution_shadow_broker(service_name: str, broker: Any | None) -> Any | None:
app/mme_scalpx/replay/execution_shadow.py:77:def simulate_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:199:def validate_replay_execution_shadow(payload: Mapping[str, Any]) -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:226:def publish_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:244:def replay_execution_shadow_contract_summary() -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:272:    "simulate_replay_execution_shadow",
app/mme_scalpx/replay/engine.py:585:def replay_engine_risk_execution_shadow_plan(*, run_id):
app/mme_scalpx/replay/batch_runner.py:10:    simulate_replay_execution_shadow,
app/mme_scalpx/replay/batch_runner.py:391:    execution_shadow = simulate_replay_execution_shadow(
app/mme_scalpx/replay/contracts.py:2617:def replay_risk_execution_shadow_contract_summary():
app/mme_scalpx/replay/report_exporter.py:191:def build_pnl_execution_shadow_summary(simulation_result: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
app/mme_scalpx/replay/fill_model.py:48:class ReplayFillRequest:
app/mme_scalpx/replay/fill_model.py:96:    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
app/mme_scalpx/replay/fill_model.py:116:    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
app/mme_scalpx/replay/fill_model.py:165:    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
app/mme_scalpx/replay/fill_model.py:227:def fill_request_to_dict(request: ReplayFillRequest) -> dict[str, Any]:
app/mme_scalpx/replay/fill_model.py:271:def _validate_request(request: ReplayFillRequest) -> None:
app/mme_scalpx/replay/fill_model.py:294:def _resolve_immediate_market_fill_price(request: ReplayFillRequest) -> float | None:
app/mme_scalpx/replay/fill_model.py:304:def _resolve_limit_touch_fill_price(request: ReplayFillRequest) -> float | None:
app/mme_scalpx/replay/fill_model.py:322:    "ReplayFillRequest",
app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py:196:def build_execution_sim_shadow(
bin/proof_replay_shadow_fill_pnl.py:20:    simulate_replay_execution_shadow,
bin/proof_replay_shadow_fill_pnl.py:87:        results[policy] = simulate_replay_execution_shadow(
bin/proof_replay_scenario_application.py:23:from app.mme_scalpx.replay.execution_shadow import simulate_replay_execution_shadow, validate_replay_execution_shadow  # noqa: E402
bin/proof_replay_scenario_application.py:107:        execution_shadow = simulate_replay_execution_shadow(
bin/replay_run.py:53:    ReplayFillRequest,
bin/replay_run.py:141:    def execution_shadow_results(self) -> tuple[dict[str, Any], ...]:
bin/replay_run.py:193:    def publish_execution_shadow_result(
bin/replay_run.py:2283:def build_execution_shadow_results_from_risk_outputs(
bin/replay_run.py:2331:        fill_request = ReplayFillRequest(
bin/replay_run.py:3212:                transport.publish_execution_shadow_result(execution_result)
bin/proof_replay_risk_execution_shadow.py:27:    simulate_replay_execution_shadow,
bin/proof_replay_risk_execution_shadow.py:117:        policy: simulate_replay_execution_shadow(
bin/proof_replay_risk_execution_shadow.py:126:    veto_execution = simulate_replay_execution_shadow(

## Source files likely involved
app/mme_scalpx/core/models.py
app/mme_scalpx/replay/fill_model.py
app/mme_scalpx/replay/miv_research_evaluator.py
app/mme_scalpx/research_gate/forensics.py
app/mme_scalpx/services/execution.py
app/mme_scalpx/services/report.py
app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py
bin/post_market_session_forensics.py
bin/proof_execution_family_entry_safety.py
bin/proof_risk_gate_execution_integration.py
bin/replay_run.py

## Context around exact function in likely files

===== bin/replay_run.py =====
     1	#!/usr/bin/env python3
     2	"""
     3	bin/replay_run.py
     4	
     5	Freeze-grade operational CLI entrypoint for one replay run of the
     6	MME-ScalpX Permanent Replay & Validation Framework.
     7	
     8	This version upgrades the feeds stage from placeholder output to a real
     9	dataset->clock->injector replay bridge, while keeping downstream stages
    10	explicitly thin until their replay wiring is frozen.
    11	"""
    12	
    13	from __future__ import annotations
    14	# BEGIN BATCH27C_REPLAY_SAFETY_FIREWALL
    15	try:
    16	    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety
    17	except ModuleNotFoundError:
    18	    import pathlib as _batch27c_pathlib
    19	    import sys as _batch27c_sys
    20	
    21	    _batch27c_here = _batch27c_pathlib.Path(__file__).resolve()
    22	    for _batch27c_parent in [_batch27c_here.parent, *_batch27c_here.parents]:
    23	        if (_batch27c_parent / "app" / "mme_scalpx").exists():
    24	            if str(_batch27c_parent) not in _batch27c_sys.path:
    25	                _batch27c_sys.path.insert(0, str(_batch27c_parent))
    26	            break
    27	    from app.mme_scalpx.replay.safety import assert_replay_module_static_safety
    28	
    29	assert_replay_module_static_safety(__file__)
    30	# END BATCH27C_REPLAY_SAFETY_FIREWALL
    31	
    32	from datetime import datetime, timezone
    33	from collections.abc import MutableMapping
    34	
    35	import argparse
    36	import json
    37	import sys
    38	from pathlib import Path
    39	from typing import Any, Mapping
    40	
    41	PROJECT_ROOT = Path(__file__).resolve().parents[1]
    42	if str(PROJECT_ROOT) not in sys.path:
    43	    sys.path.insert(0, str(PROJECT_ROOT))
    44	
    45	from app.mme_scalpx.replay.artifacts import ReplayArtifactsWriter
    46	from app.mme_scalpx.replay.clock import ReplayClock, ReplayClockConfig
    47	from app.mme_scalpx.replay.contracts import ProfilesSection
    48	from app.mme_scalpx.replay.dataset import DatasetDiscoveryConfig, ReplayDatasetRepository
    49	from app.mme_scalpx.replay.engine import ReplayEngine
    50	from app.mme_scalpx.replay.fill_model import (
    51	    ReplayFillModelConfig,
    52	    ReplayFillModelFactory,
    53	    ReplayFillRequest,
    54	)
    55	from app.mme_scalpx.replay.injector import (
    56	    ReplayInjectionEvent,
    57	    ReplayInjector,
    58	)
    59	from app.mme_scalpx.replay.integrity import (
    60	    ReplayIntegrityEvaluator,
    61	    placeholder_pass_check,
    62	    integrity_bundle_to_dict,
    63	    INTEGRITY_CHECK_HASH_FRESHNESS,
    64	    INTEGRITY_CHECK_HEARTBEAT,
    65	    INTEGRITY_CHECK_REPRODUCIBILITY,
    66	    INTEGRITY_CHECK_RESET_CLEANLINESS,
    67	    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    68	    INTEGRITY_CHECK_STALE_LEG,
    69	    ReplayIntegrityCheckResult,
    70	    IntegrityVerdict,
    71	)
    72	from app.mme_scalpx.replay.modes import (
    73	    DoctrineMode,
    74	    ReplayScope,
    75	    ReplaySideMode,
    76	    ReplaySelectionMode,
    77	    ReplaySpeedMode,
    78	)
    79	from app.mme_scalpx.replay.reports import build_report_bundle, report_bundle_to_dict
    80	from app.mme_scalpx.replay.runner import ReplayRunConfig, ReplayRunner
    81	from app.mme_scalpx.replay.selectors import (
    82	    ReplaySelectionRequest,
    83	    ReplaySelector,
    84	    ReplayTimeWindow,
    85	    selection_plan_to_dict,
    86	)
    87	from app.mme_scalpx.replay.topology import ReplayTopologyBuilder, topology_plan_to_dict
    88	
    89	
    90	REQUIRED_CHECKS = (
    91	    INTEGRITY_CHECK_HEARTBEAT,
    92	    INTEGRITY_CHECK_HASH_FRESHNESS,
    93	    INTEGRITY_CHECK_SNAPSHOT_SYNC,
    94	    INTEGRITY_CHECK_STALE_LEG,
    95	    INTEGRITY_CHECK_RESET_CLEANLINESS,
    96	    INTEGRITY_CHECK_REPRODUCIBILITY,
    97	)
    98	
    99	
   100	class ReplayRunCliError(RuntimeError):
   101	    """CLI-layer replay run error."""
   102	
   103	
   104	
   105	
   106	
   107	
   108	class LocalReplayTransport:
   109	    """
   110	    Replay-safe local transport used by this CLI phase.
   111	
   112	    It does not publish to live/runtime infrastructure. It stores replay-safe
   113	    publications locally so later stages can consume deterministic upstream
   114	    outputs without contaminating live namespaces.
   115	    """
   116	
   117	    def __init__(self) -> None:
   118	        self._published_requests: list[Any] = []
   119	        self._feature_frames: list[dict[str, Any]] = []
   120	        self._strategy_decisions: list[dict[str, Any]] = []
   121	        self._risk_outputs: list[dict[str, Any]] = []
   122	        self._execution_shadow_results: list[dict[str, Any]] = []
   123	
   124	    @property
   125	    def published_requests(self) -> tuple[Any, ...]:
   126	        return tuple(self._published_requests)
   127	
   128	    @property
   129	    def feature_frames(self) -> tuple[dict[str, Any], ...]:
   130	        return tuple(self._feature_frames)
   131	
   132	    @property
   133	    def strategy_decisions(self) -> tuple[dict[str, Any], ...]:
   134	        return tuple(self._strategy_decisions)
   135	
   136	    @property
   137	    def risk_outputs(self) -> tuple[dict[str, Any], ...]:
   138	        return tuple(self._risk_outputs)
   139	
   140	    @property
   141	    def execution_shadow_results(self) -> tuple[dict[str, Any], ...]:
   142	        return tuple(self._execution_shadow_results)
   143	
   144	    def publish(self, request) -> Mapping[str, Any] | None:
   145	        self._published_requests.append(request)
   146	        return {
   147	            "published": True,
   148	            "channel": request.event.channel,
   149	            "sequence_id": request.event.sequence_id,
   150	            "event_time": request.event.event_time,
   151	        }
   152	
   153	    def feed_requests(self, *, channel_prefix: str) -> tuple[Any, ...]:
   154	        return tuple(
   155	            request
   156	            for request in self._published_requests
   157	            if request.event.channel.startswith(channel_prefix)
   158	        )
   159	
   160	    def publish_feature_frame(self, frame: Mapping[str, Any]) -> Mapping[str, Any]:
   161	        stored = dict(frame)
   162	        self._feature_frames.append(stored)
   163	        return {
   164	            "published": True,
   165	            "channel": stored.get("feature_channel"),
   166	            "frame_id": stored.get("frame_id"),
   167	            "event_time": stored.get("event_time"),
   168	        }
   169	
   170	    def publish_strategy_decision(self, decision: Mapping[str, Any]) -> Mapping[str, Any]:
   171	        stored = dict(decision)
   172	        self._strategy_decisions.append(stored)
   173	        return {
   174	            "published": True,
   175	            "channel": stored.get("decision_channel"),
   176	            "decision_id": stored.get("decision_id"),
   177	            "event_time": stored.get("event_time"),
   178	            "action": stored.get("action"),
   179	        }
   180	
   181	    def publish_risk_output(self, risk_output: Mapping[str, Any]) -> Mapping[str, Any]:
   182	        stored = dict(risk_output)
   183	        self._risk_outputs.append(stored)
   184	        return {
   185	            "published": True,
   186	            "channel": stored.get("risk_channel"),
   187	            "risk_id": stored.get("risk_id"),
   188	            "event_time": stored.get("event_time"),
   189	            "risk_action": stored.get("risk_action"),
   190	            "veto_entry": stored.get("veto_entry"),
   191	        }
   192	
   193	    def publish_execution_shadow_result(
   194	        self,
   195	        execution_result: Mapping[str, Any],
   196	    ) -> Mapping[str, Any]:
   197	        stored = dict(execution_result)
   198	        self._execution_shadow_results.append(stored)
   199	        return {
   200	            "published": True,
   201	            "channel": stored.get("execution_channel"),
   202	            "execution_id": stored.get("execution_id"),
   203	            "event_time": stored.get("event_time"),
   204	            "filled": stored.get("filled"),
   205	        }
   206	
   207	
   208	def build_parser() -> argparse.ArgumentParser:
   209	    parser = argparse.ArgumentParser(
   210	        prog="replay_run.py",
   211	        description="Run one frozen replay backbone execution.",
   212	    )
   213	
   214	    parser.add_argument("--dataset-root", required=True, help="Replay dataset root directory")
   215	    parser.add_argument(
   216	        "--selection-mode",
   217	        required=True,
   218	        choices=[mode.value for mode in ReplaySelectionMode],
   219	        help="Canonical replay selection mode",
   220	    )
   221	    parser.add_argument("--single-day", help="YYYY-MM-DD for single_day / intraday_window / session_segment")
   222	    parser.add_argument("--start-date", help="YYYY-MM-DD for date_range")
   223	    parser.add_argument("--end-date", help="YYYY-MM-DD for date_range")
   224	    parser.add_argument("--custom-dates", help="Comma-separated YYYY-MM-DD list for custom_date_list")
   225	    parser.add_argument("--weekdays", help="Comma-separated weekday integers 0..6 for weekday_batch")
   226	    parser.add_argument("--months", help="Comma-separated month integers 1..12 for monthly_batch")
   227	    parser.add_argument("--window-start", help="HH:MM[:SS] intraday window start")
   228	    parser.add_argument("--window-end", help="HH:MM[:SS] intraday window end")
   229	    parser.add_argument("--session-segment", help="Named session segment for session_segment mode")
   230	    parser.add_argument(
   231	        "--doctrine-mode",
   232	        required=True,
   233	        choices=[mode.value for mode in DoctrineMode],
   234	        help="locked or shadow",
   235	    )
   236	    parser.add_argument(
   237	        "--scope",
   238	        required=True,
   239	        choices=[scope.value for scope in ReplayScope],
   240	        help="Replay topology scope",
   241	    )
   242	    parser.add_argument(
   243	        "--speed-mode",
   244	        default=ReplaySpeedMode.ACCELERATED.value,
   245	        choices=[mode.value for mode in ReplaySpeedMode],
   246	        help="Replay clock speed mode",
   247	    )
   248	    parser.add_argument("--run-label", default=None)
   249	    parser.add_argument("--experiment-profile", default=None)
   250	    parser.add_argument("--override-pack-id", default=None)
   251	    parser.add_argument("--dataset-id", default=None)
   252	    parser.add_argument("--fill-model", default=None)
   253	    parser.add_argument("--run-root", default=None)
   254	    parser.add_argument("--required-file-stems", default="")
   255	    parser.add_argument("--optional-file-stems", default="")
   256	    parser.add_argument("--supported-suffixes", default=".jsonl,.json,.csv")
   257	    parser.add_argument("--recurse", action="store_true")
   258	    parser.add_argument(
   259	        "--clock-start-time",
   260	        default="2026-04-17T03:45:00Z",

## Fill model context
     1	"""
     2	app/mme_scalpx/replay/fill_model.py
     3	
     4	Freeze-grade replay-only fill model layer for the MME-ScalpX Permanent Replay &
     5	Validation Framework.
     6	
     7	Fill-model responsibilities
     8	---------------------------
     9	This module owns:
    10	- canonical replay-only fill request/result contracts
    11	- deterministic fill model taxonomy
    12	- replay-only fill decision logic
    13	- machine-readable serialization helpers
    14	
    15	This module does not own:
    16	- live broker execution
    17	- production execution truth
    18	- replay orchestration
    19	- dataset discovery/loading
    20	- doctrine mutation
    21	- artifact persistence
    22	
    23	Design rules
    24	------------
    25	- fill behavior here is replay-only and must never be treated as broker truth
    26	- all fill assumptions must be explicit and auditable
    27	- identical inputs + identical model must yield identical output
    28	- no hidden live-side effects
    29	"""
    30	
    31	from __future__ import annotations
    32	
    33	from dataclasses import dataclass, field
    34	from typing import Any, Mapping, Protocol, Sequence
    35	
    36	from .modes import DoctrineMode
    37	
    38	
    39	class ReplayFillModelError(RuntimeError):
    40	    """Base exception for replay fill-model failures."""
    41	
    42	
    43	class ReplayFillModelValidationError(ReplayFillModelError):
    44	    """Raised when fill-model inputs are invalid."""
    45	
    46	
    47	@dataclass(frozen=True, slots=True)
    48	class ReplayFillRequest:
    49	    """
    50	    Canonical replay-only fill request.
    51	
    52	    Fields are intentionally generic and broker-agnostic.
    53	    """
    54	
    55	    run_id: str
    56	    order_id: str
    57	    side: str
    58	    qty: int
    59	    order_price: float | None = None
    60	    market_price: float | None = None
    61	    best_bid: float | None = None
    62	    best_ask: float | None = None
    63	    timestamp: str | None = None
    64	    metadata: Mapping[str, Any] = field(default_factory=dict)
    65	
    66	
    67	@dataclass(frozen=True, slots=True)
    68	class ReplayFillResult:
    69	    """
    70	    Canonical replay-only fill result.
    71	    """
    72	
    73	    order_id: str
    74	    model_name: str
    75	    filled: bool
    76	    fill_qty: int
    77	    fill_price: float | None
    78	    slippage: float | None
    79	    reason: str
    80	    metadata: Mapping[str, Any] = field(default_factory=dict)
    81	
    82	
    83	@dataclass(frozen=True, slots=True)
    84	class ReplayFillModelConfig:
    85	    """
    86	    Canonical fill model config.
    87	    """
    88	
    89	    model_name: str
    90	    doctrine_mode: DoctrineMode
    91	    allow_partial_fills: bool = False
    92	    notes: tuple[str, ...] = field(default_factory=tuple)
    93	
    94	
    95	class ReplayFillModel(Protocol):
    96	    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
    97	        ...
    98	
    99	
   100	class ImmediateMarketFillModel:
   101	    """
   102	    Replay-only model:
   103	    - BUY fills at best_ask if present, else market_price
   104	    - SELL fills at best_bid if present, else market_price
   105	    - full fill only
   106	    """
   107	
   108	    def __init__(self, config: ReplayFillModelConfig) -> None:
   109	        _validate_config(config)
   110	        self._config = config
   111	
   112	    @property
   113	    def config(self) -> ReplayFillModelConfig:
   114	        return self._config
   115	
   116	    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
   117	        _validate_request(request)
   118	
   119	        fill_price = _resolve_immediate_market_fill_price(request)
   120	        if fill_price is None:
   121	            return ReplayFillResult(
   122	                order_id=request.order_id,
   123	                model_name=self._config.model_name,
   124	                filled=False,
   125	                fill_qty=0,
   126	                fill_price=None,
   127	                slippage=None,
   128	                reason="no_fill_price_available",
   129	                metadata={},
   130	            )
   131	
   132	        reference = request.market_price
   133	        slippage = None
   134	        if reference is not None:
   135	            slippage = fill_price - reference
   136	
   137	        return ReplayFillResult(
   138	            order_id=request.order_id,
   139	            model_name=self._config.model_name,
   140	            filled=True,
   141	            fill_qty=request.qty,
   142	            fill_price=fill_price,
   143	            slippage=slippage,
   144	            reason="immediate_market_fill",
   145	            metadata={},
   146	        )
   147	
   148	
   149	class LimitTouchFillModel:
   150	    """
   151	    Replay-only model:
   152	    - BUY fills if market/ask <= order_price
   153	    - SELL fills if market/bid >= order_price
   154	    - full fill only
   155	    """
   156	
   157	    def __init__(self, config: ReplayFillModelConfig) -> None:
   158	        _validate_config(config)
   159	        self._config = config
   160	
   161	    @property
   162	    def config(self) -> ReplayFillModelConfig:
   163	        return self._config
   164	
   165	    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
   166	        _validate_request(request)
   167	        if request.order_price is None:
   168	            raise ReplayFillModelValidationError(
   169	                "limit-touch fill model requires order_price"
   170	            )
   171	
   172	        fill_price = _resolve_limit_touch_fill_price(request)
   173	        if fill_price is None:
   174	            return ReplayFillResult(
   175	                order_id=request.order_id,
   176	                model_name=self._config.model_name,
   177	                filled=False,
   178	                fill_qty=0,
   179	                fill_price=None,
   180	                slippage=None,
   181	                reason="limit_not_touched",
   182	                metadata={},
   183	            )
   184	
   185	        reference = request.market_price
   186	        slippage = None
   187	        if reference is not None:
   188	            slippage = fill_price - reference
   189	
   190	        return ReplayFillResult(
   191	            order_id=request.order_id,
   192	            model_name=self._config.model_name,
   193	            filled=True,
   194	            fill_qty=request.qty,
   195	            fill_price=fill_price,
   196	            slippage=slippage,
   197	            reason="limit_touch_fill",
   198	            metadata={},
   199	        )
   200	
   201	
   202	class ReplayFillModelFactory:
   203	    """
   204	    Freeze-grade replay fill model factory.
   205	    """
   206	
   207	    IMMEDIATE_MARKET = "immediate_market"
   208	    LIMIT_TOUCH = "limit_touch"
   209	
   210	    @classmethod
   211	    def create(
   212	        cls,
   213	        config: ReplayFillModelConfig,
   214	    ) -> ReplayFillModel:
   215	        _validate_config(config)
   216	
   217	        if config.model_name == cls.IMMEDIATE_MARKET:
   218	            return ImmediateMarketFillModel(config)
   219	        if config.model_name == cls.LIMIT_TOUCH:
   220	            return LimitTouchFillModel(config)
   221	
   222	        raise ReplayFillModelValidationError(
   223	            f"unsupported fill model name: {config.model_name!r}"
   224	        )
   225	
   226	
   227	def fill_request_to_dict(request: ReplayFillRequest) -> dict[str, Any]:
   228	    return {
   229	        "run_id": request.run_id,
   230	        "order_id": request.order_id,
   231	        "side": request.side,
   232	        "qty": request.qty,
   233	        "order_price": request.order_price,
   234	        "market_price": request.market_price,
   235	        "best_bid": request.best_bid,
   236	        "best_ask": request.best_ask,
   237	        "timestamp": request.timestamp,
   238	        "metadata": dict(request.metadata),
   239	    }
   240	
   241	
   242	def fill_result_to_dict(result: ReplayFillResult) -> dict[str, Any]:
   243	    return {
   244	        "order_id": result.order_id,
   245	        "model_name": result.model_name,
   246	        "filled": result.filled,
   247	        "fill_qty": result.fill_qty,
   248	        "fill_price": result.fill_price,
   249	        "slippage": result.slippage,
   250	        "reason": result.reason,
   251	        "metadata": dict(result.metadata),
   252	    }
   253	
   254	
   255	def _validate_config(config: ReplayFillModelConfig) -> None:
   256	    if not isinstance(config.model_name, str) or not config.model_name.strip():
   257	        raise ReplayFillModelValidationError(
   258	            f"model_name must be non-empty string, got {config.model_name!r}"
   259	        )
   260	    if config.allow_partial_fills:
   261	        raise ReplayFillModelValidationError(
   262	            "partial fills are not yet supported in frozen fill model"
   263	        )
   264	    for note in config.notes:
   265	        if not isinstance(note, str):
   266	            raise ReplayFillModelValidationError(
   267	                f"config note must be string, got {note!r}"
   268	            )
   269	
   270	
   271	def _validate_request(request: ReplayFillRequest) -> None:
   272	    if not isinstance(request.run_id, str) or not request.run_id.strip():
   273	        raise ReplayFillModelValidationError(
   274	            f"run_id must be non-empty string, got {request.run_id!r}"
   275	        )
   276	    if not isinstance(request.order_id, str) or not request.order_id.strip():
   277	        raise ReplayFillModelValidationError(
   278	            f"order_id must be non-empty string, got {request.order_id!r}"
   279	        )
   280	    if request.side not in ("BUY", "SELL"):
   281	        raise ReplayFillModelValidationError(
   282	            f"side must be 'BUY' or 'SELL', got {request.side!r}"
   283	        )
   284	    if not isinstance(request.qty, int) or request.qty <= 0:
   285	        raise ReplayFillModelValidationError(
   286	            f"qty must be positive int, got {request.qty!r}"
   287	        )
   288	    if not isinstance(request.metadata, Mapping):
   289	        raise ReplayFillModelValidationError(
   290	            f"metadata must be mapping, got {type(request.metadata)!r}"
   291	        )
   292	
   293	
   294	def _resolve_immediate_market_fill_price(request: ReplayFillRequest) -> float | None:
   295	    if request.side == "BUY":
   296	        if request.best_ask is not None:
   297	            return request.best_ask
   298	        return request.market_price
   299	    if request.best_bid is not None:
   300	        return request.best_bid
   301	    return request.market_price
   302	
   303	
   304	def _resolve_limit_touch_fill_price(request: ReplayFillRequest) -> float | None:
   305	    assert request.order_price is not None
   306	
   307	    if request.side == "BUY":
   308	        touch_price = request.best_ask if request.best_ask is not None else request.market_price
   309	        if touch_price is not None and touch_price <= request.order_price:
   310	            return touch_price
   311	        return None
   312	
   313	    touch_price = request.best_bid if request.best_bid is not None else request.market_price
   314	    if touch_price is not None and touch_price >= request.order_price:
   315	        return touch_price
   316	    return None
   317	
   318	
   319	__all__ = [
   320	    "ReplayFillModelError",
   321	    "ReplayFillModelValidationError",
   322	    "ReplayFillRequest",
   323	    "ReplayFillResult",
   324	    "ReplayFillModelConfig",
   325	    "ReplayFillModel",
   326	    "ImmediateMarketFillModel",
   327	    "LimitTouchFillModel",
   328	    "ReplayFillModelFactory",
   329	    "fill_request_to_dict",
   330	    "fill_result_to_dict",
   331	]
   332	
   333	# BEGIN BATCH27I_REPLAY_FILL_MODEL_SHADOW_HELPERS
   334	
   335	def replay_fill_model_shadow_assumption_profiles():
   336	    """Return replay-only fill policies supported by execution_shadow."""
   337	    from app.mme_scalpx.replay.execution_shadow import REPLAY_SHADOW_FILL_POLICIES
   338	
   339	    return {
   340	        "schema_version": "replay_fill_model_shadow_assumption_profiles_v1",
   341	        "fill_policies": tuple(REPLAY_SHADOW_FILL_POLICIES),
   342	        "real_order_sent": False,
   343	        "broker_calls_executed": False,
   344	        "paper_armed_approved": False,
   345	        "live_trading_approved": False,
   346	        "production_doctrine_changed": False,
   347	    }
   348	
   349	try:
   350	    __all__
   351	except NameError:
   352	    __all__ = tuple()
   353	
   354	__all__ = tuple(dict.fromkeys(tuple(__all__) + (
   355	    "replay_fill_model_shadow_assumption_profiles",
   356	)))
   357	
   358	# END BATCH27I_REPLAY_FILL_MODEL_SHADOW_HELPERS

## Rich shadow contract context
     1	from __future__ import annotations
     2	
     3	from dataclasses import dataclass
     4	from typing import Any, Mapping
     5	
     6	from app.mme_scalpx.replay.live_adapter import write_replay_live_state
     7	from app.mme_scalpx.replay.transport import LocalReplayTransport
     8	
     9	
    10	REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_execution_shadow_v1"
    11	
    12	REPLAY_SHADOW_FILL_POLICIES = (
    13	    "FULL_FILL",
    14	    "PARTIAL_FILL",
    15	    "NO_FILL",
    16	    "REJECTED",
    17	)
    18	
    19	REPLAY_EXECUTION_SHADOW_REQUIRED_FIELDS = (
    20	    "schema_version",
